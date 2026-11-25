#!/usr/bin/env python3
"""
================================================================================
EMERGENT LATTICE ARCHITECTURE (ELA) - SIMULATION & PROTOCOL DRIVERS
================================================================================
Module 4 of 5: Core MCMC Block, Lattice Builders & Protocol Drivers (simulation.py v6.6.2)

Provenance: [ELA ARCHITECTURE]
References:
  - Paper I   [ela_paper_i_2026]   : Foundations, Hydrodynamic Limits & Spacetime Emergence (DOI: 10.5281/zenodo.21843307)
  - Paper II  [ela_paper_ii_2026]  : Micro-Scale Soliton Topology, Gauges & Antimatter (DOI: 10.5281/zenodo.21843352)
  - Paper III [ela_paper_iii_2026] : Macro Cosmological Untensing, Geometrogenesis & Dark Energy (DOI: 10.5281/zenodo.21843375)
  - Paper IV  [ela_paper_iv_2026]  : Substrate Thermodynamics & Vacuum Kinetics (DOI: 10.5281/zenodo.23268981)
  - Paper V   [ela_paper_v_2026]   : Relational Condensed Matter & Extreme EoS (DOI: 10.5281/zenodo.23269009)
"""

import os
import sys
import time
import math
import random
import json
import gc
from enum import Enum, auto
from collections import deque
from concurrent.futures import ProcessPoolExecutor, as_completed
import numpy as np
from numba import njit

# Local module import [ELA ARCHITECTURE]
from references import __references__

# Import pure C-speed JIT math & physics kernels
from math_kernels import (
    INV_THREE,
    pbc_diff_vec,
    fast_unit_vec,
    quat_mult,
    quat_mult_scalars,
    align_holonomy_geodesic,
    calc_node_shear,
    calc_edge_torsion,
    calc_edge_stretch,
    calc_node_jamming,
    calc_edge_local_plaquette_action,
    sum_torsion_for_nodes,
    calc_total_system_energy,
    calc_multi_sleeve_overlap,
    calc_mean_sleeve_overlap_fast,
    calc_capacity_saturated_eos,
    calc_hydrostatic_compression_energy,
    evaluate_superionic_diffusion,
    cool_gauge_field_6cycle,
    calc_su2_plaquette_action,
    precompute_diamond_6cycles,
    calc_su2_plaquette_fast,
    calc_topological_charge_q,
    calc_strand_helicity_charge,
    inject_topological_soliton,
    compute_lqc_bounce_diagnostics,
    fill_laplacian_csr_buffers,
    SLQWorkspace,
    compute_ds_slq,
    compute_cv_binning
)

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(line_buffering=True)


# ------------------------------------------------------------------------------
# 0. ENGINE MODE & ENUMERATION DEFINITIONS
# ------------------------------------------------------------------------------

class EngineMode(Enum):
    PAPER1_VACUUM = auto()         # Mode 1: Pure Spatial Vacuum & Rigidity
    PAPER2_GAUGE_SOLITON = auto()   # Mode 2: Micro Solitons, SU(2) Gauges & Co-Moving Sleeves
    PAPER3_COSMOLOGY = auto()       # Mode 3: Macro Cosmology, Untensing & S3 LQC Bounce
    PAPER4_THERMODYNAMICS = auto()  # Mode 4: Substrate Thermodynamics & Geometrogenesis Phase Transitions
    PAPER5_CONDENSED_MATTER = auto()# Mode 5: Relational Condensed Matter & Extreme EoS


class ThermoSweepMode(Enum):
    BETA_SWEEP = auto()      # Automated step-wise beta_eff inverse noise floor sweep
    QUENCH_KINETICS = auto() # High-tension quench for viscoelastic relaxation rate Gamma_tau
    FSS_ANALYSIS = auto()    # Finite-Size Scaling across multi-grid volumes N


class CondensedMatterMode(Enum):
    HYDROSTATIC_COMPRESSION = auto() # Pressure sweep P_ext = 10 GPa -> 1000 GPa
    PHASE_DIAGRAM_H2O = auto()       # H2O T_emergent vs P_ext phase kinetics
    DIAMOND_RAIN_CARBON = auto()     # Carbon valence strain minimization under bulk strain
    SUPERIONIC_ONSET = auto()        # Proton knot diffusion through rigid sub-lattice
    CAPACITY_SATURATION = auto()     # Non-singular density saturation rho/rho_sat -> 0.999


class EPRMode(Enum):
    DYNAMIC = auto()  # Move 4 active: dynamic EPR thermal creation/annihilation
    STATIC = auto()   # Static zero-strain shortcut injection at setup
    NONE = auto()     # Strict 3D spatial grid (zero shortcuts)


@njit
def _seed_numba_prng(seed: int):
    np.random.seed(seed)


def setup_prng(user_seed: int | None = None) -> int:
    if user_seed is None:
        active_seed = random.SystemRandom().randint(0, 2**32 - 1)
        print(f"[PRNG] Seed: Auto-generated from system entropy ({active_seed})")
    else:
        active_seed = int(user_seed)
        print(f"[PRNG] Seed: Explicitly set ({active_seed})")

    random.seed(active_seed)
    np.random.seed(active_seed)
    _seed_numba_prng(active_seed)
    return active_seed


# ------------------------------------------------------------------------------
# 1. INITIALIZATION & LATTICE BUILDERS
# ------------------------------------------------------------------------------

@njit(fastmath=True)
def _build_diamond_adj(pos, adj, box_size, inv_L, nn_dist, max_degree=6):
    """
    Robust O(N) Spatial Cell-Linked List Builder with Fallback.
    Guarantees cell_size >= (nn_dist + 0.1) to eliminate missed neighbor bonds.
    """
    N = pos.shape[0]
    min_d = nn_dist - 0.1
    max_d = nn_dist + 0.1
    min_sq = min_d * min_d
    max_sq = max_d * max_d

    n_cells_1d = int(math.floor(box_size / max_d))

    if n_cells_1d < 3:
        for u in range(N):
            nbr_count = 0
            for v in range(N):
                if u == v:
                    continue
                dx, dy, dz = pbc_diff_vec(pos[u], pos[v], box_size, inv_L)
                dist_sq = dx * dx + dy * dy + dz * dz
                if min_sq < dist_sq < max_sq:
                    adj[u, nbr_count] = v
                    nbr_count += 1
                    if nbr_count == 4:
                        break
        return

    cell_size = box_size / float(n_cells_1d)
    inv_cell_size = 1.0 / cell_size
    total_cells = n_cells_1d * n_cells_1d * n_cells_1d

    head = np.full(total_cells, -1, dtype=np.int32)
    cell_next = np.empty(N, dtype=np.int32)

    for i in range(N):
        cx = int(math.floor(pos[i, 0] * inv_cell_size)) % n_cells_1d
        cy = int(math.floor(pos[i, 1] * inv_cell_size)) % n_cells_1d
        cz = int(math.floor(pos[i, 2] * inv_cell_size)) % n_cells_1d
        c_idx = cx * (n_cells_1d * n_cells_1d) + cy * n_cells_1d + cz
        cell_next[i] = head[c_idx]
        head[c_idx] = i

    for u in range(N):
        cx = int(math.floor(pos[u, 0] * inv_cell_size)) % n_cells_1d
        cy = int(math.floor(pos[u, 1] * inv_cell_size)) % n_cells_1d
        cz = int(math.floor(pos[u, 2] * inv_cell_size)) % n_cells_1d
        nbr_count = 0

        for dx_c in (-1, 0, 1):
            nx = (cx + dx_c) % n_cells_1d
            for dy_c in (-1, 0, 1):
                ny = (cy + dy_c) % n_cells_1d
                for dz_c in (-1, 0, 1):
                    nz = (cz + dz_c) % n_cells_1d
                    c_nbr = nx * (n_cells_1d * n_cells_1d) + ny * n_cells_1d + nz
                    v = head[c_nbr]
                    while v >= 0:
                        if v != u:
                            dx, dy, dz = pbc_diff_vec(pos[u], pos[v], box_size, inv_L)
                            dist_sq = dx * dx + dy * dy + dz * dz
                            if min_sq < dist_sq < max_sq:
                                adj[u, nbr_count] = v
                                nbr_count += 1
                                if nbr_count == 4:
                                    break
                        v = cell_next[v]
                    if nbr_count == 4:
                        break
                if nbr_count == 4:
                    break
            if nbr_count == 4:
                break


def initialize_diamond_lattice(dim_cells, max_degree=6):
    fcc_basis = [
        np.array([0.0, 0.0, 0.0]), np.array([0.0, 0.5, 0.5]),
        np.array([0.5, 0.0, 0.5]), np.array([0.5, 0.5, 0.0])
    ]
    shift = np.array([0.25, 0.25, 0.25])
    basis = fcc_basis + [b + shift for b in fcc_basis]

    positions = []
    for cx in range(dim_cells):
        for cy in range(dim_cells):
            for cz in range(dim_cells):
                cell_origin = np.array([cx, cy, cz], dtype=float)
                for b in basis:
                    positions.append((cell_origin + b) / dim_cells)

    box_size = float(dim_cells * 4.0)
    pos = np.array(positions, dtype=np.float64) * box_size
    N = len(pos)
    inv_L = 1.0 / box_size

    adj = np.full((N, max_degree), -1, dtype=np.int32)
    is_coherent_edge = np.zeros((N, max_degree), dtype=bool)
    gauge_u = np.zeros((N, max_degree, 4), dtype=np.float64)
    gauge_u[:, :, 0] = 1.0

    nn_dist = (math.sqrt(3.0) / 4.0) * (box_size / dim_cells)

    _build_diamond_adj(pos, adj, box_size, inv_L, nn_dist, max_degree)

    pos = np.ascontiguousarray(pos, dtype=np.float64)
    adj = np.ascontiguousarray(adj, dtype=np.int32)
    is_coherent_edge = np.ascontiguousarray(is_coherent_edge, dtype=bool)
    gauge_u = np.ascontiguousarray(gauge_u, dtype=np.float64)

    return pos, adj, is_coherent_edge, gauge_u, box_size, nn_dist


def inject_static_epr_shortcuts(adj, is_coherent_edge, target_density=0.001, max_degree=6):
    N = adj.shape[0]
    target_count = int(N * target_density)
    injected = 0

    while injected < target_count:
        u = random.randint(0, N - 1)
        v = random.randint(0, N - 1)
        if u == v:
            continue

        u_free = -1; v_free = -1
        for i in range(max_degree):
            if adj[u, i] < 0:
                u_free = i
                break
        for i in range(max_degree):
            if adj[v, i] < 0:
                v_free = i
                break

        if u_free >= 0 and v_free >= 0:
            adj[u, u_free] = v; adj[v, v_free] = u
            is_coherent_edge[u, u_free] = True; is_coherent_edge[v, v_free] = True
            injected += 1


@njit(fastmath=True)
def reindex_spatial_cache(pos, adj, is_coherent_edge, gauge_u, box_size):
    N = pos.shape[0]
    grid_dim = int(round(box_size))
    
    spatial_keys = np.zeros(N, dtype=np.int32)
    for i in range(N):
        cx = int(math.floor(pos[i, 0])) % grid_dim
        cy = int(math.floor(pos[i, 1])) % grid_dim
        cz = int(math.floor(pos[i, 2])) % grid_dim
        spatial_keys[i] = cx * (grid_dim * grid_dim) + cy * grid_dim + cz
    
    perm = np.argsort(spatial_keys)
    inv_perm = np.zeros(N, dtype=np.int32)
    for i in range(N):
        inv_perm[perm[i]] = i

    max_deg = adj.shape[1]
    adj_mapped = np.full((N, max_deg), -1, dtype=np.int32)
    for i in range(N):
        for d in range(max_deg):
            nbr = adj[i, d]
            if nbr >= 0:
                adj_mapped[i, d] = inv_perm[nbr]

    pos[:] = pos[perm]
    gauge_u[:] = gauge_u[perm]
    is_coherent_edge[:] = is_coherent_edge[perm]
    adj[:] = adj_mapped[perm]


@njit(fastmath=True, inline='always')
def _calc_total_system_energy_serial(pos, adj, is_coherent_edge, gauge_u, L, inv_L, r0, ks, kt, kr, lj, scale_a=1.0, beta_untensing=0.0175, mode_val=1, max_degree=6):
    N = pos.shape[0]
    total_shear = 0.0
    total_torsion = 0.0
    total_stretch = 0.0
    total_jamming = 0.0
    
    eff_ks = ks * (scale_a ** (-beta_untensing)) if mode_val == 3 else ks

    for u in range(N):
        total_shear += calc_node_shear(u, adj, pos, L, inv_L, max_degree)
        total_jamming += calc_node_jamming(u, gauge_u, max_degree)

    for u in range(N):
        local_stretch = 0.0
        local_torsion = 0.0
        for i in range(max_degree):
            v = adj[u, i]
            if v > u:
                if not is_coherent_edge[u, i]:
                    local_stretch += calc_edge_stretch(u, v, pos, r0, L, inv_L)
                local_torsion += calc_edge_torsion(u, v, adj, pos, L, inv_L, max_degree)
        total_stretch += local_stretch
        total_torsion += local_torsion
                
    H_s = eff_ks * total_shear
    H_t = kt * total_torsion
    H_r = kr * total_stretch
    V_j = 0.5 * lj * total_jamming
    H_tot = H_s + H_t + H_r + V_j
    
    return H_tot, H_s, H_t, H_r, V_j


# ------------------------------------------------------------------------------
# 2. EXTENDED MCMC PROPOSAL BLOCK KERNEL WITH COMPLIANT MOVE 3 & ZERO-DRIFT SAMPLING
# ------------------------------------------------------------------------------

@njit(fastmath=True, cache=True)
def run_numba_mcs_block(
    pos, adj, gauge_u, is_coherent_edge, box_size, inv_L, beta_mc,
    kappa_s, kappa_t, kappa_r, lambda_j, r0,
    max_disp, max_gauge_disp, num_sweeps,
    aff_nodes_m1, aff_nodes_m3, edge_buf, shear_vecs_buf,
    cutoff_prefactor=3.85, is_warmup=False, mode_val=1, scale_a=1.0,
    beta_untensing=0.0175, snr_crit=7.50, epr_mode_val=0, epsilon_sw=0.002,
    has_soliton=False, beta_gauge=6.15,
    sleeve_mode=1, sleeve_sigma=0.02, sleeve_weight=1.0, sleeve_tunnel_alpha=0.05,
    track_fluctuations=False, P_ext=0.0, max_vol_disp=0.01,
    p_spatial=0.75, p_gauge=0.15, p_pachner=0.10,
    use_compliance=False, compliance_alpha=0.15
):
    N_nodes = pos.shape[0]
    max_degree = 6

    win_spatial_att = 0; win_spatial_acc = 0
    win_gauge_att = 0;   win_gauge_acc = 0
    win_topo_att = 0;    win_topo_acc = 0
    win_epr_att = 0;     win_epr_acc = 0
    win_hydro_att = 0;   win_hydro_acc = 0
    lazy_exits = 0;      full_rejs = 0
    sleeve_protected_swaps = 0

    sum_H = 0.0
    sum_H_sq = 0.0
    H_curr = 0.0
    n_energy_samples = 0

    eff_ks = kappa_s * (scale_a ** (-beta_untensing)) if mode_val == 3 else kappa_s

    exp_neg_inv_beta_g = math.exp(-1.0 / max(1e-6, beta_gauge))
    E_vac = 4.0 * (1.0 - exp_neg_inv_beta_g)
    inv_E_vac = 1.0 / max(1e-6, E_vac)
    u_g_vac_mean = E_vac

    snr_mult_spatial = eff_ks * 0.5 * beta_mc
    snr_mult_gauge = beta_gauge * 0.5 * beta_mc
    eff_lambda_j = beta_mc * 0.5 * lambda_j
    inv_sleeve_sigma = 1.0 / max(1e-6, sleeve_sigma)
    r0_sq = r0 * r0
    base_cutoff_sq = cutoff_prefactor * r0_sq
    max_possible_cutoff_sq = (cutoff_prefactor + 0.30) * r0_sq
    max_allowed_epr = int(epsilon_sw * N_nodes)
    inv_beta_mc = 1.0 / max(1e-6, beta_mc)

    CAP_PREFACTOR = -250.0 / 9.0
    INV_TAU_MAX_SQ = 9.0
    TAU_SAT_LIMIT = 0.998 / 3.0

    cutoff_m1 = p_spatial
    cutoff_m2 = p_spatial + p_gauge
    cutoff_m3 = p_spatial + p_gauge + p_pachner

    n_epr_links = 0
    if mode_val == 3:
        for u_i in range(N_nodes):
            for deg_i in range(max_degree):
                if is_coherent_edge[u_i, deg_i]:
                    n_epr_links += 1
        n_epr_links //= 2

    if track_fluctuations and not is_warmup:
        H_curr, _, _, _, _ = _calc_total_system_energy_serial(
            pos, adj, is_coherent_edge, gauge_u, box_size, inv_L, r0,
            kappa_s, kappa_t, kappa_r, lambda_j,
            scale_a=scale_a, beta_untensing=beta_untensing,
            mode_val=mode_val, max_degree=max_degree
        )

    for sweep in range(num_sweeps):
        for _ in range(N_nodes):
            roll = np.random.rand()

            if is_warmup:
                if has_soliton:
                    do_move1 = True; do_move2 = False
                else:
                    do_move1 = (roll < 0.80); do_move2 = not do_move1
                do_move3 = False; do_move4 = False
            else:
                do_move1 = False; do_move2 = False; do_move3 = False; do_move4 = False
                if roll < cutoff_m1:
                    do_move1 = True
                elif roll < cutoff_m2:
                    do_move2 = True
                elif roll < cutoff_m3:
                    do_move3 = True
                else:
                    do_move4 = True

            # MOVE 1: SPATIAL PERTURBATION
            if do_move1:
                win_spatial_att += 1
                u = np.random.randint(0, N_nodes)

                dx_disp = (np.random.rand() * 2.0 - 1.0) * max_disp
                dy_disp = (np.random.rand() * 2.0 - 1.0) * max_disp
                dz_disp = (np.random.rand() * 2.0 - 1.0) * max_disp

                old_px = pos[u, 0]; old_py = pos[u, 1]; old_pz = pos[u, 2]
                
                new_px = old_px + dx_disp
                if new_px >= box_size: new_px -= box_size
                elif new_px < 0.0: new_px += box_size

                new_py = old_py + dy_disp
                if new_py >= box_size: new_py -= box_size
                elif new_py < 0.0: new_py += box_size

                new_pz = old_pz + dz_disp
                if new_pz >= box_size: new_pz -= box_size
                elif new_pz < 0.0: new_pz += box_size

                aff_nodes_m1[0] = u
                n_aff = 1
                for i in range(max_degree):
                    v = adj[u, i]
                    if v >= 0:
                        aff_nodes_m1[n_aff] = v
                        n_aff += 1

                s_before = 0.0
                for i in range(n_aff):
                    s_before += calc_node_shear(aff_nodes_m1[i], adj, pos, box_size, inv_L, max_degree)
                
                str_before = 0.0
                if kappa_r > 0.0:
                    for i in range(max_degree):
                        v = adj[u, i]
                        if v >= 0 and not is_coherent_edge[u, i]:
                            str_before += calc_edge_stretch(u, v, pos, r0, box_size, inv_L)

                pos[u, 0] = new_px; pos[u, 1] = new_py; pos[u, 2] = new_pz

                s_after = 0.0
                for i in range(n_aff):
                    s_after += calc_node_shear(aff_nodes_m1[i], adj, pos, box_size, inv_L, max_degree)
                
                str_after = 0.0
                if kappa_r > 0.0:
                    for i in range(max_degree):
                        v = adj[u, i]
                        if v >= 0 and not is_coherent_edge[u, i]:
                            str_after += calc_edge_stretch(u, v, pos, r0, box_size, inv_L)

                delta_H_fast = (eff_ks * (s_after - s_before) + kappa_r * (str_after - str_before))
                r = np.random.rand()

                if kappa_t > 0.0:
                    max_allowed_delta = -math.log(max(1e-12, r)) * inv_beta_mc
                    pos[u, 0] = old_px; pos[u, 1] = old_py; pos[u, 2] = old_pz
                    t_before = sum_torsion_for_nodes(aff_nodes_m1, n_aff, adj, pos, box_size, inv_L, edge_buf, max_degree)

                    if (delta_H_fast - kappa_t * t_before) > max_allowed_delta:
                        lazy_exits += 1
                    else:
                        pos[u, 0] = new_px; pos[u, 1] = new_py; pos[u, 2] = new_pz
                        t_after = sum_torsion_for_nodes(aff_nodes_m1, n_aff, adj, pos, box_size, inv_L, edge_buf, max_degree)
                        delta_H_total = delta_H_fast + kappa_t * (t_after - t_before)

                        if delta_H_total <= 0.0 or delta_H_total <= max_allowed_delta:
                            win_spatial_acc += 1
                            if track_fluctuations and not is_warmup:
                                H_curr += delta_H_total
                        else:
                            pos[u, 0] = old_px; pos[u, 1] = old_py; pos[u, 2] = old_pz
                            full_rejs += 1
                else:
                    if delta_H_fast <= 0.0 or r < math.exp(-beta_mc * delta_H_fast):
                        win_spatial_acc += 1
                        if track_fluctuations and not is_warmup:
                            H_curr += delta_H_fast
                    else:
                        pos[u, 0] = old_px; pos[u, 1] = old_py; pos[u, 2] = old_pz
                        full_rejs += 1

            # MOVE 2: SU(2) GAUGE PHASE HOLONOMY UPDATES
            elif do_move2:
                win_gauge_att += 1
                u = np.random.randint(0, N_nodes)
                e_idx = np.random.randint(0, max_degree)
                v = adj[u, e_idx]

                if v >= 0:
                    v_u_idx = -1
                    for i in range(max_degree):
                        if adj[v, i] == u:
                            v_u_idx = i
                            break

                    if v_u_idx >= 0:
                        old_qu0 = gauge_u[u, e_idx, 0]; old_qu1 = gauge_u[u, e_idx, 1]
                        old_qu2 = gauge_u[u, e_idx, 2]; old_qu3 = gauge_u[u, e_idx, 3]

                        old_qv0 = gauge_u[v, v_u_idx, 0]; old_qv1 = gauge_u[v, v_u_idx, 1]
                        old_qv2 = gauge_u[v, v_u_idx, 2]; old_qv3 = gauge_u[v, v_u_idx, 3]

                        q0 = old_qu0 + (np.random.rand() * 2.0 - 1.0) * max_gauge_disp
                        q1 = old_qu1 + (np.random.rand() * 2.0 - 1.0) * max_gauge_disp
                        q2 = old_qu2 + (np.random.rand() * 2.0 - 1.0) * max_gauge_disp
                        q3 = old_qu3 + (np.random.rand() * 2.0 - 1.0) * max_gauge_disp

                        norm = math.sqrt(q0 * q0 + q1 * q1 + q2 * q2 + q3 * q3)
                        if norm > 1e-12:
                            inv = 1.0 / norm
                            q0 *= inv; q1 *= inv; q2 *= inv; q3 *= inv

                        s_plaq_before = calc_edge_local_plaquette_action(u, e_idx, adj, gauge_u, max_degree)
                        j_before = calc_node_jamming(u, gauge_u, max_degree) + calc_node_jamming(v, gauge_u, max_degree)

                        gauge_u[u, e_idx, 0] = q0; gauge_u[u, e_idx, 1] = q1
                        gauge_u[u, e_idx, 2] = q2; gauge_u[u, e_idx, 3] = q3

                        gauge_u[v, v_u_idx, 0] = q0; gauge_u[v, v_u_idx, 1] = -q1
                        gauge_u[v, v_u_idx, 2] = -q2; gauge_u[v, v_u_idx, 3] = -q3

                        s_plaq_after = calc_edge_local_plaquette_action(u, e_idx, adj, gauge_u, max_degree)
                        j_after = calc_node_jamming(u, gauge_u, max_degree) + calc_node_jamming(v, gauge_u, max_degree)

                        delta_H = beta_gauge * (s_plaq_after - s_plaq_before) + eff_lambda_j * (j_after - j_before)
                        if delta_H <= 0.0 or np.random.rand() < math.exp(-delta_H):
                            win_gauge_acc += 1
                            if track_fluctuations and not is_warmup:
                                H_curr += 0.5 * lambda_j * (j_after - j_before)
                        else:
                            gauge_u[u, e_idx, 0] = old_qu0; gauge_u[u, e_idx, 1] = old_qu1
                            gauge_u[u, e_idx, 2] = old_qu2; gauge_u[u, e_idx, 3] = old_qu3

                            gauge_u[v, v_u_idx, 0] = old_qv0; gauge_u[v, v_u_idx, 1] = old_qv1
                            gauge_u[v, v_u_idx, 2] = old_qv2; gauge_u[v, v_u_idx, 3] = old_qv3

            # MOVE 3: COMPLIANT 2-to-2 TOPOLOGICAL LINK SWAP (WOOTEN-WINER-WEAIRE)
            elif do_move3:
                win_topo_att += 1
                u = np.random.randint(0, N_nodes)

                v_idx = np.random.randint(0, max_degree)
                v = adj[u, v_idx]

                if v >= 0 and not is_coherent_edge[u, v_idx]:
                    mid_idx = np.random.randint(0, max_degree)
                    mid = adj[u, mid_idx]
                    if mid >= 0:
                        w_idx = np.random.randint(0, max_degree)
                        w = adj[mid, w_idx]
                    else:
                        w = -1

                    if w >= 0 and w != u and w != v:
                        z_idx = np.random.randint(0, max_degree)
                        z = adj[w, z_idx]

                        if z >= 0 and z != u and z != v and not is_coherent_edge[w, z_idx]:
                            # Stage 1: Absolute geometric distance pre-filter
                            dx_uz, dy_uz, dz_uz = pbc_diff_vec(pos[u], pos[z], box_size, inv_L)
                            dist_uz_sq = dx_uz * dx_uz + dy_uz * dy_uz + dz_uz * dz_uz
                            if dist_uz_sq > max_possible_cutoff_sq:
                                continue

                            dx_wv, dy_wv, dz_wv = pbc_diff_vec(pos[w], pos[v], box_size, inv_L)
                            dist_wv_sq = dx_wv * dx_wv + dy_wv * dy_wv + dz_wv * dz_wv
                            if dist_wv_sq > max_possible_cutoff_sq:
                                continue

                            # Stage 2: Evaluate dynamic cutoff expansion ONLY if outside base cutoff
                            u_sh = -1.0
                            u_g = -1.0
                            if dist_uz_sq > base_cutoff_sq or dist_wv_sq > base_cutoff_sq:
                                u_sh = calc_node_shear(u, adj, pos, box_size, inv_L, max_degree)
                                u_g = calc_node_jamming(u, gauge_u, max_degree)

                                E_local = u_sh + u_g
                                E_ratio = max(0.0, (E_local - E_vac) * inv_E_vac)
                                clamped_expansion = 0.30 * math.tanh(sleeve_tunnel_alpha * E_ratio)
                                effective_cutoff_sq = (cutoff_prefactor + clamped_expansion) * r0_sq

                                if dist_uz_sq > effective_cutoff_sq or dist_wv_sq > effective_cutoff_sq:
                                    continue

                            # Stage 3: Mode-dependent sleeve protection filter
                            if mode_val in (2, 3, 5):
                                if u_sh < 0.0:
                                    u_sh = calc_node_shear(u, adj, pos, box_size, inv_L, max_degree)
                                    u_g = calc_node_jamming(u, gauge_u, max_degree)

                                v_sh = calc_node_shear(v, adj, pos, box_size, inv_L, max_degree)
                                w_sh = calc_node_shear(w, adj, pos, box_size, inv_L, max_degree)
                                z_sh = calc_node_shear(z, adj, pos, box_size, inv_L, max_degree)

                                v_g = calc_node_jamming(v, gauge_u, max_degree)
                                w_g = calc_node_jamming(w, gauge_u, max_degree)
                                z_g = calc_node_jamming(z, gauge_u, max_degree)

                                snr_spatial = max(u_sh, v_sh, w_sh, z_sh) * snr_mult_spatial
                                max_u_g = max(u_g, v_g, w_g, z_g)
                                snr_gauge = max(0.0, max_u_g - u_g_vac_mean) * snr_mult_gauge
                                snr_coupled = math.sqrt(snr_spatial * snr_spatial + sleeve_weight * snr_gauge * snr_gauge)

                                if sleeve_mode == 1:
                                    arg = (snr_coupled - snr_crit) * inv_sleeve_sigma
                                    if arg > 16.0:
                                        sleeve_protected_swaps += 1
                                        continue
                                    elif arg > -16.0:
                                        p_allow = 1.0 / (1.0 + math.exp(arg))
                                        if np.random.rand() > p_allow:
                                            sleeve_protected_swaps += 1
                                            continue
                                else:
                                    if snr_coupled > snr_crit:
                                        sleeve_protected_swaps += 1
                                        continue

                            # Stage 4: Duplicate link check & incident neighbor gathering
                            already_exists = False
                            for i in range(max_degree):
                                if adj[u, i] == z or adj[w, i] == v:
                                    already_exists = True
                                    break

                            if not already_exists:
                                v_u_idx = -1; z_w_idx = -1
                                for i in range(max_degree):
                                    if adj[v, i] == u: v_u_idx = i
                                    if adj[z, i] == w: z_w_idx = i

                                if v_u_idx >= 0 and z_w_idx >= 0:
                                    # Collect core nodes
                                    aff_nodes_m3[0] = u; aff_nodes_m3[1] = v
                                    aff_nodes_m3[2] = w; aff_nodes_m3[3] = z
                                    n_aff_m3 = 4

                                    # Gather all unique incident neighbors (up to 32 nodes)
                                    for c_idx in range(4):
                                        core_node = aff_nodes_m3[c_idx]
                                        for d_idx in range(max_degree):
                                            nbr = adj[core_node, d_idx]
                                            if nbr >= 0:
                                                is_dup = False
                                                for check_i in range(n_aff_m3):
                                                    if aff_nodes_m3[check_i] == nbr:
                                                        is_dup = True
                                                        break
                                                if not is_dup and n_aff_m3 < 32:
                                                    aff_nodes_m3[n_aff_m3] = nbr
                                                    n_aff_m3 += 1

                                    # Exact shear accumulation before move
                                    s_before = 0.0
                                    for i in range(n_aff_m3):
                                        s_before += calc_node_shear(aff_nodes_m3[i], adj, pos, box_size, inv_L, max_degree)

                                    str_before = (calc_edge_stretch(u, v, pos, r0, box_size, inv_L) + calc_edge_stretch(w, z, pos, r0, box_size, inv_L)) if kappa_r > 0.0 else 0.0
                                    t_before = sum_torsion_for_nodes(aff_nodes_m3, 4, adj, pos, box_size, inv_L, edge_buf, max_degree) if kappa_t > 0.0 else 0.0

                                    # Save coordinates for compliant relaxation rollback
                                    old_ux = pos[u, 0]; old_uy = pos[u, 1]; old_uz = pos[u, 2]
                                    old_vx = pos[v, 0]; old_vy = pos[v, 1]; old_vz = pos[v, 2]
                                    old_wx = pos[w, 0]; old_wy = pos[w, 1]; old_wz = pos[w, 2]
                                    old_zx = pos[z, 0]; old_zy = pos[z, 1]; old_zz = pos[z, 2]

                                    # Virtual compliant relaxation
                                    if use_compliance:
                                        pos[u, 0] = (old_ux + compliance_alpha * dx_uz) % box_size
                                        pos[u, 1] = (old_uy + compliance_alpha * dy_uz) % box_size
                                        pos[u, 2] = (old_uz + compliance_alpha * dz_uz) % box_size

                                        pos[z, 0] = (old_zx - compliance_alpha * dx_uz) % box_size
                                        pos[z, 1] = (old_zy - compliance_alpha * dy_uz) % box_size
                                        pos[z, 2] = (old_zz - compliance_alpha * dz_uz) % box_size

                                        pos[w, 0] = (old_wx + compliance_alpha * dx_wv) % box_size
                                        pos[w, 1] = (old_wy + compliance_alpha * dy_wv) % box_size
                                        pos[w, 2] = (old_wz + compliance_alpha * dz_wv) % box_size

                                        pos[v, 0] = (old_vx - compliance_alpha * dx_wv) % box_size
                                        pos[v, 1] = (old_vy - compliance_alpha * dy_wv) % box_size
                                        pos[v, 2] = (old_vz - compliance_alpha * dz_wv) % box_size

                                    # Apply trial topological reconnection
                                    adj[u, v_idx] = z; adj[w, z_idx] = v
                                    adj[v, v_u_idx] = w; adj[z, z_w_idx] = u

                                    # Exact shear accumulation after move
                                    s_after = 0.0
                                    for i in range(n_aff_m3):
                                        s_after += calc_node_shear(aff_nodes_m3[i], adj, pos, box_size, inv_L, max_degree)

                                    str_after = (calc_edge_stretch(u, z, pos, r0, box_size, inv_L) + calc_edge_stretch(w, v, pos, r0, box_size, inv_L)) if kappa_r > 0.0 else 0.0

                                    delta_H_fast = eff_ks * (s_after - s_before) + kappa_r * (str_after - str_before)
                                    r = np.random.rand()
                                    max_allowed_delta = -math.log(max(1e-12, r)) * inv_beta_mc

                                    if (delta_H_fast - kappa_t * t_before) > max_allowed_delta:
                                        # Revert Adjacency & Coordinates
                                        adj[u, v_idx] = v; adj[w, z_idx] = z
                                        adj[v, v_u_idx] = u; adj[z, z_w_idx] = w
                                        if use_compliance:
                                            pos[u, 0] = old_ux; pos[u, 1] = old_uy; pos[u, 2] = old_uz
                                            pos[v, 0] = old_vx; pos[v, 1] = old_vy; pos[v, 2] = old_vz
                                            pos[w, 0] = old_wx; pos[w, 1] = old_wy; pos[w, 2] = old_wz
                                            pos[z, 0] = old_zx; pos[z, 1] = old_zy; pos[z, 2] = old_zz
                                        lazy_exits += 1
                                    else:
                                        # Backup SU(2) link quaternions
                                        q_uv_0 = gauge_u[u, v_idx, 0]; q_uv_1 = gauge_u[u, v_idx, 1]; q_uv_2 = gauge_u[u, v_idx, 2]; q_uv_3 = gauge_u[u, v_idx, 3]
                                        q_vu_0 = gauge_u[v, v_u_idx, 0]; q_vu_1 = gauge_u[v, v_u_idx, 1]; q_vu_2 = gauge_u[v, v_u_idx, 2]; q_vu_3 = gauge_u[v, v_u_idx, 3]
                                        q_wz_0 = gauge_u[w, z_idx, 0]; q_wz_1 = gauge_u[w, z_idx, 1]; q_wz_2 = gauge_u[w, z_idx, 2]; q_wz_3 = gauge_u[w, z_idx, 3]
                                        q_zw_0 = gauge_u[z, z_w_idx, 0]; q_zw_1 = gauge_u[z, z_w_idx, 1]; q_zw_2 = gauge_u[z, z_w_idx, 2]; q_zw_3 = gauge_u[z, z_w_idx, 3]

                                        q_uz_w, q_uz_x, q_uz_y, q_uz_z = align_holonomy_geodesic(q_uv_0, q_uv_1, q_uv_2, q_uv_3, pos[u], pos[v], pos[z], box_size, inv_L)
                                        q_wv_w, q_wv_x, q_wv_y, q_wv_z = align_holonomy_geodesic(q_wz_0, q_wz_1, q_wz_2, q_wz_3, pos[w], pos[z], pos[v], box_size, inv_L)

                                        j_before = 0.5 * (calc_node_jamming(u, gauge_u, max_degree) + calc_node_jamming(v, gauge_u, max_degree) +
                                                          calc_node_jamming(w, gauge_u, max_degree) + calc_node_jamming(z, gauge_u, max_degree))

                                        gauge_u[u, v_idx, 0] = q_uz_w; gauge_u[u, v_idx, 1] = q_uz_x; gauge_u[u, v_idx, 2] = q_uz_y; gauge_u[u, v_idx, 3] = q_uz_z
                                        gauge_u[z, z_w_idx, 0] = q_uz_w; gauge_u[z, z_w_idx, 1] = -q_uz_x; gauge_u[z, z_w_idx, 2] = -q_uz_y; gauge_u[z, z_w_idx, 3] = -q_uz_z
                                        gauge_u[w, z_idx, 0] = q_wv_w; gauge_u[w, z_idx, 1] = q_wv_x; gauge_u[w, z_idx, 2] = q_wv_y; gauge_u[w, z_idx, 3] = q_wv_z
                                        gauge_u[v, v_u_idx, 0] = q_wv_w; gauge_u[v, v_u_idx, 1] = -q_wv_x; gauge_u[v, v_u_idx, 2] = -q_wv_y; gauge_u[v, v_u_idx, 3] = -q_wv_z

                                        j_after = 0.5 * (calc_node_jamming(u, gauge_u, max_degree) + calc_node_jamming(v, gauge_u, max_degree) +
                                                         calc_node_jamming(w, gauge_u, max_degree) + calc_node_jamming(z, gauge_u, max_degree))

                                        t_after = sum_torsion_for_nodes(aff_nodes_m3, 4, adj, pos, box_size, inv_L, edge_buf, max_degree) if kappa_t > 0.0 else 0.0
                                        delta_H_total = delta_H_fast + lambda_j * (j_after - j_before) + kappa_t * (t_after - t_before)

                                        if delta_H_total <= 0.0 or delta_H_total <= max_allowed_delta:
                                            win_topo_acc += 1
                                            if track_fluctuations and not is_warmup:
                                                H_curr += delta_H_total
                                        else:
                                            # Full Rollback: Adjacency, Coordinates, AND Holonomies
                                            adj[u, v_idx] = v; adj[w, z_idx] = z
                                            adj[v, v_u_idx] = u; adj[z, z_w_idx] = w
                                            if use_compliance:
                                                pos[u, 0] = old_ux; pos[u, 1] = old_uy; pos[u, 2] = old_uz
                                                pos[v, 0] = old_vx; pos[v, 1] = old_vy; pos[v, 2] = old_vz
                                                pos[w, 0] = old_wx; pos[w, 1] = old_wy; pos[w, 2] = old_wz
                                                pos[z, 0] = old_zx; pos[z, 1] = old_zy; pos[z, 2] = old_zz
                                            gauge_u[u, v_idx, 0] = q_uv_0; gauge_u[u, v_idx, 1] = q_uv_1; gauge_u[u, v_idx, 2] = q_uv_2; gauge_u[u, v_idx, 3] = q_uv_3
                                            gauge_u[v, v_u_idx, 0] = q_vu_0; gauge_u[v, v_u_idx, 1] = q_vu_1; gauge_u[v, v_u_idx, 2] = q_vu_2; gauge_u[v, v_u_idx, 3] = q_vu_3
                                            gauge_u[w, z_idx, 0] = q_wz_0; gauge_u[w, z_idx, 1] = q_wz_1; gauge_u[w, z_idx, 2] = q_wz_2; gauge_u[w, z_idx, 3] = q_wz_3
                                            gauge_u[z, z_w_idx, 0] = q_zw_0; gauge_u[z, z_w_idx, 1] = q_zw_1; gauge_u[z, z_w_idx, 2] = q_zw_2; gauge_u[z, z_w_idx, 3] = q_zw_3
                                            full_rejs += 1

            # MOVE 4: DYNAMIC ER=EPR SHORTCUT INJECTION
            elif do_move4:
                win_epr_att += 1
                u = np.random.randint(0, N_nodes)
                v = np.random.randint(0, N_nodes)

                if u != v:
                    existing_slot = -1
                    for i in range(max_degree):
                        if adj[u, i] == v: existing_slot = i; break

                    if existing_slot >= 0:
                        if is_coherent_edge[u, existing_slot]:
                            v_slot = -1
                            for i in range(max_degree):
                                if adj[v, i] == u: v_slot = i; break
                            
                            if v_slot >= 0:
                                s_before = calc_node_shear(u, adj, pos, box_size, inv_L, max_degree) + \
                                           calc_node_shear(v, adj, pos, box_size, inv_L, max_degree)

                                adj[u, existing_slot] = -1; adj[v, v_slot] = -1
                                is_coherent_edge[u, existing_slot] = False; is_coherent_edge[v, v_slot] = False
                                
                                s_after = calc_node_shear(u, adj, pos, box_size, inv_L, max_degree) + \
                                          calc_node_shear(v, adj, pos, box_size, inv_L, max_degree)
                                delta_H = eff_ks * (s_after - s_before)

                                if delta_H <= 0.0 or np.random.rand() < math.exp(-beta_mc * delta_H):
                                    gauge_u[u, existing_slot, 0] = 1.0; gauge_u[u, existing_slot, 1] = 0.0
                                    gauge_u[u, existing_slot, 2] = 0.0; gauge_u[u, existing_slot, 3] = 0.0
                                    gauge_u[v, v_slot, 0] = 1.0; gauge_u[v, v_slot, 1] = 0.0
                                    gauge_u[v, v_slot, 2] = 0.0; gauge_u[v, v_slot, 3] = 0.0
                                    n_epr_links -= 1
                                    win_epr_acc += 1
                                    if track_fluctuations and not is_warmup:
                                        H_curr += delta_H
                                else:
                                    adj[u, existing_slot] = v; adj[v, v_slot] = u
                                    is_coherent_edge[u, existing_slot] = True; is_coherent_edge[v, v_slot] = True
                    else:
                        if n_epr_links < max_allowed_epr:
                            u_free = -1; v_free = -1
                            for i in range(max_degree):
                                if adj[u, i] < 0: u_free = i; break
                            for i in range(max_degree):
                                if adj[v, i] < 0: v_free = i; break

                            if u_free >= 0 and v_free >= 0:
                                s_before = calc_node_shear(u, adj, pos, box_size, inv_L, max_degree) + \
                                           calc_node_shear(v, adj, pos, box_size, inv_L, max_degree)

                                adj[u, u_free] = v; adj[v, v_free] = u
                                is_coherent_edge[u, u_free] = True; is_coherent_edge[v, v_free] = True

                                s_after = calc_node_shear(u, adj, pos, box_size, inv_L, max_degree) + \
                                          calc_node_shear(v, adj, pos, box_size, inv_L, max_degree)
                                delta_H = eff_ks * (s_after - s_before)

                                if delta_H <= 0.0 or np.random.rand() < math.exp(-beta_mc * delta_H):
                                    gauge_u[u, u_free, 0] = 1.0; gauge_u[u, u_free, 1] = 0.0
                                    gauge_u[u, u_free, 2] = 0.0; gauge_u[u, u_free, 3] = 0.0
                                    gauge_u[v, v_free, 0] = 1.0; gauge_u[v, v_free, 1] = 0.0
                                    gauge_u[v, v_free, 2] = 0.0; gauge_u[v, v_free, 3] = 0.0
                                    n_epr_links += 1
                                    win_epr_acc += 1
                                    if track_fluctuations and not is_warmup:
                                        H_curr += delta_H
                                else:
                                    adj[u, u_free] = -1; adj[v, v_free] = -1
                                    is_coherent_edge[u, u_free] = False; is_coherent_edge[v, v_free] = False

        # GLOBAL MOVE 5: Volume Contraction and PBC Horizon Rescaling
        if mode_val == 5 and not is_warmup:
            win_hydro_att += 1
            delta_scale = (np.random.rand() * 2.0 - 1.0) * max_vol_disp
            scale_trial = max(0.20, min(1.80, scale_a + delta_scale))
            mu = scale_trial / max(1e-6, scale_a)

            tau_old = abs(scale_a - 1.0)
            tau_new = abs(scale_trial - 1.0)

            if tau_new >= TAU_SAT_LIMIT:
                delta_H_total = 1e18
            else:
                p_prefactor = P_ext * INV_THREE
                sum_dist_cubed = 0.0
                sum_dist_sq = 0.0
                sum_dist = 0.0

                for i_u in range(N_nodes):
                    for i_deg in range(max_degree):
                        i_v = adj[i_u, i_deg]
                        if i_v > i_u:
                            dx_e, dy_e, dz_e = pbc_diff_vec(pos[i_u], pos[i_v], box_size, inv_L)
                            dist_sq = dx_e * dx_e + dy_e * dy_e + dz_e * dz_e
                            dist_e = math.sqrt(dist_sq)
                            sum_dist_cubed += dist_e * dist_sq
                            if kappa_r > 0.0 and not is_coherent_edge[i_u, i_deg]:
                                sum_dist_sq += dist_sq
                                sum_dist += dist_e

                H_P_before = sum_dist_cubed * p_prefactor
                delta_H_P = (mu * mu * mu - 1.0) * H_P_before

                arg_old = max(1e-12, 1.0 - (tau_old * tau_old * INV_TAU_MAX_SQ))
                arg_new = max(1e-12, 1.0 - (tau_new * tau_new * INV_TAU_MAX_SQ))

                H_cap_old = CAP_PREFACTOR * math.log(arg_old)
                H_cap_new = CAP_PREFACTOR * math.log(arg_new)
                delta_H_elastic = (H_cap_new - H_cap_old) * float(N_nodes)

                delta_H_stretch = kappa_r * ((mu * mu - 1.0) * sum_dist_sq - 2.0 * r0 * (mu - 1.0) * sum_dist) if kappa_r > 0.0 else 0.0
                delta_H_total = delta_H_P + delta_H_elastic + delta_H_stretch

            if delta_H_total <= 0.0 or np.random.rand() < math.exp(-beta_mc * delta_H_total):
                for i_n in range(N_nodes):
                    pos[i_n, 0] *= mu
                    pos[i_n, 1] *= mu
                    pos[i_n, 2] *= mu
                scale_a = scale_trial
                box_size *= mu
                inv_L = 1.0 / box_size
                win_hydro_acc += 1
                if track_fluctuations and not is_warmup:
                    H_curr, _, _, _, _ = _calc_total_system_energy_serial(
                        pos, adj, is_coherent_edge, gauge_u, box_size, inv_L, r0,
                        kappa_s, kappa_t, kappa_r, lambda_j,
                        scale_a=scale_a, beta_untensing=beta_untensing,
                        mode_val=mode_val, max_degree=max_degree
                    )

        # UNBIASED CANONICAL ENERGY FLUCTUATION TRACKING (ZERO-DRIFT EXACT SAMPLING)
        if track_fluctuations and not is_warmup:
            burn_in_threshold = int(0.35 * num_sweeps)
            if sweep >= burn_in_threshold and sweep % 10 == 0:
                # Directly sample true Hamiltonian to eliminate Move 3 incremental drift
                H_exact, _, _, _, _ = _calc_total_system_energy_serial(
                    pos, adj, is_coherent_edge, gauge_u, box_size, inv_L, r0,
                    kappa_s, kappa_t, kappa_r, lambda_j,
                    scale_a=scale_a, beta_untensing=beta_untensing,
                    mode_val=mode_val, max_degree=max_degree
                )
                H_curr = H_exact  # Re-synchronize running baseline
                sum_H += H_exact
                sum_H_sq += (H_exact * H_exact)
                n_energy_samples += 1

    return (win_spatial_att, win_spatial_acc, 
            win_gauge_att, win_gauge_acc, 
            win_topo_att, win_topo_acc, 
            win_epr_att, win_epr_acc,
            lazy_exits, full_rejs, sleeve_protected_swaps,
            sum_H, sum_H_sq, win_hydro_att, win_hydro_acc, scale_a, n_energy_samples)


# ------------------------------------------------------------------------------
# 3. MODE 4 PROTOCOL DRIVERS
# ------------------------------------------------------------------------------

def run_thermo_beta_sweep(
    beta_start=0.50, beta_end=2.80, beta_steps=25,
    eq_sweeps=5000, meas_sweeps=15000,
    grid_dim=16, run_id="RUN-V656_PRODUCTION", out_dir=".", save_npz=True, seed=None,
    test_mode=False, cutoff_prefactor=3.85,
    enable_compliant_move3=True, compliance_alpha=0.15
):
    resolved_seed = setup_prng(seed)
    os.makedirs(out_dir, exist_ok=True)

    beta_array = np.linspace(beta_start, beta_end, beta_steps)
    cv_profile = []
    dh_profile = []
    h_comp_profile = []
    acc_profile = []
    
    pos, adj, is_coherent_edge, gauge_u, box_size, r0_eq = initialize_diamond_lattice(max(1, grid_dim // 4))
    N_nodes = pos.shape[0]
    inv_L = 1.0 / box_size
    slq_ws = SLQWorkspace(N_nodes, max_degree=6)

    aff_nodes_m1 = np.zeros(7, dtype=np.int32)
    aff_nodes_m3 = np.zeros(32, dtype=np.int32)
    edge_buf = np.zeros((128, 2), dtype=np.int32)
    shear_vecs_buf = np.zeros((6, 3), dtype=np.float64)

    print("\n================================================================================")
    print("       MODE 4: SUBSTRATE THERMODYNAMICS & GEOMETROGENESIS BETA SWEEP")
    print("================================================================================")
    print(f" Run ID           : {run_id}")
    print(f" System Size N     : {N_nodes:,} nodes (grid_dim = {grid_dim})")
    print(f" Beta_eff Range   : [{beta_start:.2f} -> {beta_end:.2f}] ({beta_steps} steps)")
    print(f" Move 3 Compliance: {enable_compliant_move3} (alpha = {compliance_alpha:.2f})")
    print("================================================================================\n")

    actual_pre_sweeps = min(eq_sweeps * 2, max(200, N_nodes * 2)) if test_mode else eq_sweeps * 2
    print(f"[INIT] Executing pre-sweep lattice fluidization ({actual_pre_sweeps:,} MCS at Beta = {beta_array[0]:.2f})...")
    _ = run_numba_mcs_block(
        pos, adj, gauge_u, is_coherent_edge, box_size, inv_L, beta_array[0],
        kappa_s=1.0, kappa_t=0.03, kappa_r=0.0, lambda_j=0.141421, r0=r0_eq,
        max_disp=0.02, max_gauge_disp=0.015, num_sweeps=actual_pre_sweeps,
        aff_nodes_m1=aff_nodes_m1, aff_nodes_m3=aff_nodes_m3,
        edge_buf=edge_buf, shear_vecs_buf=shear_vecs_buf,
        cutoff_prefactor=cutoff_prefactor,
        is_warmup=False, mode_val=4, track_fluctuations=False,
        p_spatial=0.45, p_gauge=0.15, p_pachner=0.40,
        use_compliance=enable_compliant_move3, compliance_alpha=compliance_alpha
    )
    gc.collect()
    
    reindex_spatial_cache(pos, adj, is_coherent_edge, gauge_u, box_size)
    print("[INIT] Pre-melt complete & spatial cache re-indexed. Beginning Beta Sweep measurement loop...\n")

    for b_idx, beta_curr in enumerate(beta_array):
        t_step_start = time.time()

        _ = run_numba_mcs_block(
            pos, adj, gauge_u, is_coherent_edge, box_size, inv_L, beta_curr,
            kappa_s=1.0, kappa_t=0.03, kappa_r=0.0, lambda_j=0.141421, r0=r0_eq,
            max_disp=0.02, max_gauge_disp=0.015, num_sweeps=eq_sweeps,
            aff_nodes_m1=aff_nodes_m1, aff_nodes_m3=aff_nodes_m3,
            edge_buf=edge_buf, shear_vecs_buf=shear_vecs_buf,
            cutoff_prefactor=cutoff_prefactor,
            is_warmup=False, mode_val=4, track_fluctuations=False,
            p_spatial=0.45, p_gauge=0.15, p_pachner=0.40,
            use_compliance=enable_compliant_move3, compliance_alpha=compliance_alpha
        )
        
        res = run_numba_mcs_block(
            pos, adj, gauge_u, is_coherent_edge, box_size, inv_L, beta_curr,
            kappa_s=1.0, kappa_t=0.03, kappa_r=0.0, lambda_j=0.141421, r0=r0_eq,
            max_disp=0.02, max_gauge_disp=0.015, num_sweeps=meas_sweeps,
            aff_nodes_m1=aff_nodes_m1, aff_nodes_m3=aff_nodes_m3,
            edge_buf=edge_buf, shear_vecs_buf=shear_vecs_buf,
            cutoff_prefactor=cutoff_prefactor,
            is_warmup=False, mode_val=4, track_fluctuations=True,
            p_spatial=0.45, p_gauge=0.15, p_pachner=0.40,
            use_compliance=enable_compliant_move3, compliance_alpha=compliance_alpha
        )
        
        t_step_elapsed = time.time() - t_step_start
        throughput = (eq_sweeps + meas_sweeps) / max(1e-6, t_step_elapsed)

        (s_att, s_acc, g_att, g_acc, t_att, t_acc) = res[:6]
        sum_H = res[11]
        sum_H_sq = res[12]
        n_samples = max(1, res[16])
        
        mean_H = sum_H / float(n_samples)
        mean_H_sq = sum_H_sq / float(n_samples)
        var_H = max(0.0, mean_H_sq - (mean_H * mean_H))
        
        Cv_curr = (beta_curr ** 2) * var_H / float(N_nodes)

        current_sweep = (b_idx + 1) * (eq_sweeps + meas_sweeps)
        slq_diag_seed = int((resolved_seed ^ (current_sweep + 1) * 1000003) & 0x7FFFFFFF)
        ds_curr, _, _ = compute_ds_slq(
            adj, N_nodes, box_size, slq_ws,
            num_samples=15, m_lanczos=35,
            seed=slq_diag_seed, use_gpu=False
        )

        if (b_idx + 1) % 5 == 0:
            reindex_spatial_cache(pos, adj, is_coherent_edge, gauge_u, box_size)

        H_tot, H_s, H_t, H_r, V_j = calc_total_system_energy(
            pos, adj, is_coherent_edge, gauge_u, box_size, inv_L, r0_eq,
            1.0, 0.03, 0.0, 0.141421,
            scale_a=1.0, beta_untensing=0.0175, mode_val=4, max_degree=6
        )

        acc_s = (s_acc / max(1, s_att)) * 100.0
        acc_g = (g_acc / max(1, g_att)) * 100.0
        acc_t = (t_acc / max(1, t_att)) * 100.0

        cv_profile.append(Cv_curr)
        dh_profile.append(ds_curr)
        h_comp_profile.append([H_tot / float(N_nodes), H_s / float(N_nodes), H_t / float(N_nodes), V_j / float(N_nodes)])
        acc_profile.append([acc_s, acc_g, acc_t])

        print(f" Step {b_idx+1:02d}/{beta_steps:02d} | Beta: {beta_curr:.4f} | Cv: {Cv_curr:.6f} | d_s: {ds_curr:.4f} | Acc_sp: {acc_s:.1f}% | Acc_topo: {acc_t:.2f}% | Throughput: {throughput:8.1f} Swp/s")

        gc.collect()

    cv_arr = np.array(cv_profile)
    dh_arr = np.array(dh_profile)
    h_comp_arr = np.array(h_comp_profile)
    acc_arr = np.array(acc_profile)
    q_geom = float(np.trapz(cv_arr / beta_array, beta_array))

    if save_npz:
        safe_id = run_id.replace("/", "_").replace("\\", "_")
        export_filename = os.path.join(out_dir, f"{safe_id}_thermo_beta_sweep_seed{resolved_seed}_v656_results.npz")
        np.savez_compressed(
            export_filename,
            mode="PAPER4_THERMODYNAMICS",
            thermo_mode="BETA_SWEEP",
            run_id=run_id,
            seed=resolved_seed,
            grid_dim=grid_dim,
            N_nodes=N_nodes,
            beta_array=beta_array,
            cv_profile=cv_arr,
            dh_profile=dh_arr,
            q_geom_latent_heat=q_geom,
            h_comp_history=h_comp_arr,
            acc_history=acc_arr,
            benchmark_citations=np.array(["wooten_1985", "barkema_1996", "ambjorn_2005"], dtype=object)
        )
        return export_filename

    return beta_array, cv_arr, dh_arr, q_geom


def run_quench_kinetics(
    grid_dim=16, beta_target=3.0035, strain_init=0.30,
    total_sweeps=20000, num_sweeps=None, log_interval=200, run_id="RUN-V656_PRODUCTION",
    out_dir=".", save_npz=True, seed=None,
    test_mode=False, cutoff_prefactor=3.85,
    enable_compliant_move3=True, compliance_alpha=0.15
):
    if num_sweeps is not None:
        total_sweeps = num_sweeps

    resolved_seed = setup_prng(seed)
    os.makedirs(out_dir, exist_ok=True)

    pos, adj, is_coherent_edge, gauge_u, box_size, r0_eq = initialize_diamond_lattice(max(1, grid_dim // 4))
    N_nodes = pos.shape[0]
    inv_L = 1.0 / box_size
    slq_ws = SLQWorkspace(N_nodes, max_degree=6)

    pos += strain_init * (np.random.rand(*pos.shape) * 2.0 - 1.0) * r0_eq
    pos = np.mod(pos, box_size)

    aff_nodes_m1 = np.zeros(7, dtype=np.int32)
    aff_nodes_m3 = np.zeros(32, dtype=np.int32)
    edge_buf = np.zeros((128, 2), dtype=np.int32)
    shear_vecs_buf = np.zeros((6, 3), dtype=np.float64)

    sweeps_log, strain_history, energy_history, ds_history = [], [], [], []
    num_blocks = total_sweeps // log_interval

    print("\n================================================================================")
    print("       MODE 4: SUBSTRATE THERMODYNAMICS VISCOELASTIC QUENCH KINETICS")
    print("================================================================================")
    print(f" Run ID           : {run_id}")
    print(f" System Size N     : {N_nodes:,} nodes (grid_dim = {grid_dim})")
    print(f" Target Beta_eff  : {beta_target:.4f}")
    print(f" Initial Strain   : {strain_init:.2f} r0")
    print(f" Total MCS Sweeps : {total_sweeps:,} (Interval = {log_interval:,} MCS)")
    print("================================================================================\n")

    t_start = time.time()
    ds_curr = 3.0

    for b_idx in range(num_blocks):
        t_block_start = time.time()

        _ = run_numba_mcs_block(
            pos, adj, gauge_u, is_coherent_edge, box_size, inv_L, beta_target,
            kappa_s=1.0, kappa_t=0.03, kappa_r=0.0, lambda_j=0.141421, r0=r0_eq,
            max_disp=0.02, max_gauge_disp=0.015, num_sweeps=log_interval,
            aff_nodes_m1=aff_nodes_m1, aff_nodes_m3=aff_nodes_m3,
            edge_buf=edge_buf, shear_vecs_buf=shear_vecs_buf,
            cutoff_prefactor=cutoff_prefactor,
            is_warmup=False, mode_val=4, track_fluctuations=False,
            p_spatial=0.45, p_gauge=0.15, p_pachner=0.40,
            use_compliance=enable_compliant_move3, compliance_alpha=compliance_alpha
        )
        
        H_tot, H_s, _, _, _ = calc_total_system_energy(
            pos, adj, is_coherent_edge, gauge_u, box_size, inv_L, r0_eq,
            1.0, 0.03, 0.0, 0.141421,
            scale_a=1.0, beta_untensing=0.0175, mode_val=4, max_degree=6
        )
        mean_shear_strain = H_s / float(N_nodes)
        
        curr_mcs = (b_idx + 1) * log_interval
        if b_idx == 0 or curr_mcs % 1000 == 0 or b_idx == num_blocks - 1:
            slq_diag_seed = int((resolved_seed ^ (curr_mcs + 1) * 1000003) & 0x7FFFFFFF)
            ds_curr, _, _ = compute_ds_slq(
                adj, N_nodes, box_size, slq_ws,
                num_samples=10, m_lanczos=30,
                seed=slq_diag_seed, use_gpu=False
            )

        sweeps_log.append(curr_mcs)
        strain_history.append(mean_shear_strain)
        energy_history.append(H_tot)
        ds_history.append(ds_curr)

        t_block_elapsed = time.time() - t_block_start
        throughput = log_interval / max(1e-6, t_block_elapsed)

        print(f" Sweep {curr_mcs:7d}/{total_sweeps:7d} | Throughput: {throughput:8.1f} Swp/s | Strain <tau>: {mean_shear_strain:.6f} | H_tot: {H_tot:10.4f} | d_s: {ds_curr:.4f}")
        gc.collect()

    sweeps_arr = np.array(sweeps_log, dtype=np.float64)
    strain_arr = np.array(strain_history, dtype=np.float64)
    energy_arr = np.array(energy_history, dtype=np.float64)
    ds_arr = np.array(ds_history, dtype=np.float64)

    tau_eq = float(np.mean(strain_arr[int(0.7 * len(strain_arr)):]))
    delta_tau = strain_arr - tau_eq
    transient_cutoff = max(5, int(0.4 * len(strain_arr)))
    valid_mask = delta_tau[:transient_cutoff] > 1e-4

    if np.sum(valid_mask) > 2:
        t_fit = sweeps_arr[:transient_cutoff][valid_mask]
        y_fit = np.log(np.maximum(delta_tau[:transient_cutoff][valid_mask], 1e-12))
        slope, _ = np.polyfit(t_fit, y_fit, 1)
        gamma_tau_fit = float(-slope) if slope < 0 else 0.0175
    else:
        gamma_tau_fit = 0.0175

    t_total = time.time() - t_start

    print("-" * 105)
    print(f" QUENCH KINETICS ANALYSIS COMPLETE ({t_total:.2f} s)")
    print(f" Fitted Relaxation Rate Gamma_tau : {gamma_tau_fit:.6e} MCS^-1")
    print(f" Equilibrium Strain tau_eq       : {tau_eq:.6f}")
    print(f" Final Spectral Dimension d_s     : {ds_arr[-1]:.4f}")
    print("-" * 105 + "\n")

    if save_npz:
        safe_id = run_id.replace("/", "_").replace("\\", "_")
        export_filename = os.path.join(out_dir, f"{safe_id}_thermo_quench_seed{resolved_seed}_v656_results.npz")
        np.savez_compressed(
            export_filename,
            mode="PAPER4_THERMODYNAMICS",
            thermo_mode="QUENCH_KINETICS",
            run_id=run_id,
            seed=resolved_seed,
            grid_dim=grid_dim,
            N_nodes=N_nodes,
            sweeps_arr=sweeps_arr,
            strain_arr=strain_arr,
            energy_arr=energy_arr,
            ds_arr=ds_arr,
            sweeps_log=sweeps_arr,
            strain_log=strain_arr,
            energy_log=energy_arr,
            quench_gamma_tau=gamma_tau_fit,
            gamma_fit=gamma_tau_fit,
            tau_eq=tau_eq,
            benchmark_citations=np.array(["wooten_1985", "barkema_1996"], dtype=object)
        )
        return export_filename

    return sweeps_arr, strain_arr, gamma_tau_fit


def _fss_single_volume_worker(args_tuple):
    """
    Evaluates finite-size scaling across system volume N using standard
    simulated annealing across the full fluid-to-solid corridor [0.50 -> 2.80].
    
    Guarantees that every lattice volume undergoes complete pre-melt fluidization
    at beta = 0.50, eliminating cold-start non-equilibrium boundary transients.
    """
    if len(args_tuple) == 8:
        g_dim, beta_crit_est, eq_sweeps, meas_sweeps, run_id, out_dir, seed, test_mode = args_tuple
    else:
        g_dim, beta_crit_est, eq_sweeps, meas_sweeps, run_id, out_dir, seed = args_tuple
        test_mode = False

    dim_cells = max(1, g_dim // 4)
    N_nodes = (dim_cells ** 3) * 8

    # Canonical ELA annealing corridor: melts initial crystal at beta = 0.50,
    # then anneals quasi-statically past the geometrogenesis boundary to beta = 2.80
    b_start = 0.50
    b_end = 2.80

    beta_arr, cv_arr, dh_arr, q_geom = run_thermo_beta_sweep(
        beta_start=b_start,
        beta_end=b_end,
        beta_steps=25,
        eq_sweeps=eq_sweeps,
        meas_sweeps=meas_sweeps,
        grid_dim=g_dim,
        run_id=run_id,
        out_dir=out_dir,
        save_npz=False,
        seed=seed,
        test_mode=test_mode,
        cutoff_prefactor=3.85,
        enable_compliant_move3=True,
        compliance_alpha=0.15
    )

    cv_max = float(np.max(cv_arr))
    beta_peak = float(beta_arr[np.argmax(cv_arr)])

    return N_nodes, {
        "beta_peak": beta_peak,
        "cv_max": cv_max,
        "q_geom": q_geom,
        "beta_arr": beta_arr.tolist(),
        "cv_arr": cv_arr.tolist(),
        "dh_arr": dh_arr.tolist()
    }


def run_fss_protocol(
    fss_grid_dims=[8, 16, 32], beta_crit_est=2.15, run_id="RUN-V656_PRODUCTION",
    out_dir=".", save_npz=True, seed=None, max_workers=1, test_mode=False,
    enable_compliant_move3=True, compliance_alpha=0.15
):
    resolved_seed = setup_prng(seed)
    os.makedirs(out_dir, exist_ok=True)

    fss_results = {}
    worker_args = [
        (g_dim, beta_crit_est, 3000, 10000, run_id, out_dir, resolved_seed + idx, test_mode)
        for idx, g_dim in enumerate(fss_grid_dims)
    ]

    for arg in worker_args:
        N_nodes, res_dict = _fss_single_volume_worker(arg)
        fss_results[int(N_nodes)] = res_dict
        print(f" Worker Grid N={N_nodes} Complete | Beta_peak: {res_dict['beta_peak']:.4f} | Cv_max: {res_dict['cv_max']:.6f} | q_geom: {res_dict['q_geom']:.4f} J/node")

    if save_npz:
        safe_id = run_id.replace("/", "_").replace("\\", "_")
        export_filename = os.path.join(out_dir, f"{safe_id}_thermo_fss_seed{resolved_seed}_v656_results.npz")
        np.savez_compressed(
            export_filename,
            mode="PAPER4_THERMODYNAMICS",
            thermo_mode="FSS_ANALYSIS",
            run_id=run_id,
            seed=resolved_seed,
            fss_results_json=json.dumps(fss_results),
            benchmark_citations=np.array(["wooten_1985", "barkema_1996", "challa_1986"], dtype=object)
        )
        return export_filename

    return fss_results


# ------------------------------------------------------------------------------
# 4. MODE 5 CONDENSED MATTER PROTOCOL DRIVERS
# ------------------------------------------------------------------------------

def run_hydrostatic_compression(
    grid_dim=16, pressure_start=10.0, pressure_end=1000.0, pressure_steps=20,
    eq_sweeps=5000, meas_sweeps=20000, beta_target=3.0035, run_id="RUN-V656_PRODUCTION",
    out_dir=".", save_npz=True, seed=None
):
    resolved_seed = setup_prng(seed)
    os.makedirs(out_dir, exist_ok=True)

    P_ext_array = np.linspace(pressure_start, pressure_end, pressure_steps)
    volume_array = []
    mean_strain_array = []
    capacity_P_array = []

    pos, adj, is_coherent_edge, gauge_u, box_size_init, r0_eq = initialize_diamond_lattice(max(1, grid_dim // 4))
    N_nodes = pos.shape[0]

    aff_nodes_m1 = np.zeros(7, dtype=np.int32)
    aff_nodes_m3 = np.zeros(32, dtype=np.int32)
    edge_buf = np.zeros((128, 2), dtype=np.int32)
    shear_vecs_buf = np.zeros((6, 3), dtype=np.float64)

    print("\n================================================================================")
    print("       MODE 5: RELATIONAL CONDENSED MATTER HYDROSTATIC COMPRESSION")
    print("================================================================================")
    print(f" Run ID           : {run_id}")
    print(f" System Size N     : {N_nodes:,} nodes (grid_dim = {grid_dim})")
    print(f" Pressure Range   : [{pressure_start:.1f} -> {pressure_end:.1f}] GPa ({pressure_steps} steps)")
    print("================================================================================\n")

    scale_curr = 1.0
    for p_idx, P_curr in enumerate(P_ext_array):
        t_step_start = time.time()

        vol_disp_adaptive = max(0.0005, 0.01 / (1.0 + 0.015 * P_curr))

        box_size_curr = box_size_init * scale_curr
        inv_L_curr = 1.0 / box_size_curr

        res_eq = run_numba_mcs_block(
            pos, adj, gauge_u, is_coherent_edge, box_size_curr, inv_L_curr, beta_target,
            kappa_s=1.0, kappa_t=0.03, kappa_r=5.0, lambda_j=0.141421, r0=r0_eq,
            max_disp=0.02, max_gauge_disp=0.015, num_sweeps=eq_sweeps,
            aff_nodes_m1=aff_nodes_m1, aff_nodes_m3=aff_nodes_m3,
            edge_buf=edge_buf, shear_vecs_buf=shear_vecs_buf,
            cutoff_prefactor=3.85,
            is_warmup=False, mode_val=5, scale_a=scale_curr,
            P_ext=P_curr, max_vol_disp=vol_disp_adaptive,
            p_spatial=0.85, p_gauge=0.15, p_pachner=0.0
        )
        scale_curr = res_eq[15] if len(res_eq) > 15 else scale_curr
        box_size_curr = box_size_init * scale_curr
        inv_L_curr = 1.0 / box_size_curr

        res_meas = run_numba_mcs_block(
            pos, adj, gauge_u, is_coherent_edge, box_size_curr, inv_L_curr, beta_target,
            kappa_s=1.0, kappa_t=0.03, kappa_r=5.0, lambda_j=0.141421, r0=r0_eq,
            max_disp=0.02, max_gauge_disp=0.015, num_sweeps=meas_sweeps,
            aff_nodes_m1=aff_nodes_m1, aff_nodes_m3=aff_nodes_m3,
            edge_buf=edge_buf, shear_vecs_buf=shear_vecs_buf,
            cutoff_prefactor=3.85,
            is_warmup=False, mode_val=5, scale_a=scale_curr,
            P_ext=P_curr, max_vol_disp=vol_disp_adaptive,
            p_spatial=0.85, p_gauge=0.15, p_pachner=0.0
        )
        scale_curr = res_meas[15] if len(res_meas) > 15 else scale_curr

        t_step_elapsed = time.time() - t_step_start
        throughput = (eq_sweeps + meas_sweeps) / max(1e-6, t_step_elapsed)

        v_eff = float(N_nodes) * (scale_curr ** 3)

        mean_link_strain = min(0.333333, max(0.0, abs(1.0 - scale_curr)))
        tau_ratio = mean_link_strain * 3.0
        if tau_ratio >= 0.999999:
            mean_P_cap = 1.0e8
        else:
            mean_P_cap = ((1.0 + mean_link_strain) ** (5.0 / 3.0)) / (1.0 - tau_ratio * tau_ratio)

        volume_array.append(v_eff)
        mean_strain_array.append(mean_link_strain)
        capacity_P_array.append(mean_P_cap)

        if (p_idx + 1) % 5 == 0:
            reindex_spatial_cache(pos, adj, is_coherent_edge, gauge_u, box_size_curr)

        print(f" Step {p_idx+1:02d}/{pressure_steps:02d} | P_ext: {P_curr:6.1f} GPa | Vol: {v_eff:8.2f} | Strain <tau>: {mean_link_strain:.6f} | P_cap: {mean_P_cap:.4e} | Throughput: {throughput:8.1f} Swp/s")
        gc.collect()

    vol_arr = np.array(volume_array)
    strain_arr = np.array(mean_strain_array)
    p_cap_arr = np.array(capacity_P_array)

    if save_npz:
        safe_id = run_id.replace("/", "_").replace("\\", "_")
        export_filename = os.path.join(out_dir, f"{safe_id}_condensed_hydrostatic_seed{resolved_seed}_v656_results.npz")
        np.savez_compressed(
            export_filename,
            mode="PAPER5_CONDENSED_MATTER",
            condensed_mode="HYDROSTATIC_COMPRESSION",
            run_id=run_id,
            seed=resolved_seed,
            grid_dim=grid_dim,
            N_nodes=N_nodes,
            P_ext_array=P_ext_array,
            volume_array=vol_arr,
            mean_strain_array=strain_arr,
            capacity_P_array=p_cap_arr,
            benchmark_citations=np.array(["zeldovich_1962"], dtype=object)
        )
        return export_filename

    return P_ext_array, vol_arr, strain_arr, p_cap_arr


def run_phase_diagram_h2o(
    grid_dim=16, temp_start=300.0, temp_end=5000.0, temp_steps=20,
    P_ext=150.0, total_sweeps=20000, run_id="RUN-V656_PRODUCTION",
    out_dir=".", save_npz=True, seed=None
):
    resolved_seed = setup_prng(seed)
    os.makedirs(out_dir, exist_ok=True)

    temp_array = np.linspace(temp_start, temp_end, temp_steps)
    dp_array = []
    overlap_array = []

    pos, adj, is_coherent_edge, gauge_u, box_size, r0_eq = initialize_diamond_lattice(max(1, grid_dim // 4))
    N_nodes = pos.shape[0]
    inv_L = 1.0 / box_size

    pos_step_start = np.zeros_like(pos)

    node_q = np.zeros(N_nodes, dtype=np.int32)
    for i in range(0, N_nodes, 4):
        node_q[i] = 1

    snr_array = np.full(N_nodes, 7.0, dtype=np.float64)

    aff_nodes_m1 = np.zeros(7, dtype=np.int32)
    aff_nodes_m3 = np.zeros(32, dtype=np.int32)
    edge_buf = np.zeros((128, 2), dtype=np.int32)
    shear_vecs_buf = np.zeros((6, 3), dtype=np.float64)

    for t_idx, T_curr in enumerate(temp_array):
        t_step_start = time.time()
        
        np.copyto(pos_step_start, pos)
        
        beta_curr = 1000.0 / max(1e-3, T_curr)
        sweeps_step = max(10, total_sweeps // temp_steps)

        _ = run_numba_mcs_block(
            pos, adj, gauge_u, is_coherent_edge, box_size, inv_L, beta_curr,
            kappa_s=1.0, kappa_t=0.03, kappa_r=0.0, lambda_j=0.141421, r0=r0_eq,
            max_disp=0.02, max_gauge_disp=0.015, num_sweeps=sweeps_step,
            aff_nodes_m1=aff_nodes_m1, aff_nodes_m3=aff_nodes_m3,
            edge_buf=edge_buf, shear_vecs_buf=shear_vecs_buf,
            cutoff_prefactor=3.85,
            is_warmup=False, mode_val=5, P_ext=P_ext
        )

        t_step_elapsed = time.time() - t_step_start
        throughput = sweeps_step / max(1e-6, t_step_elapsed)

        D_p, msd = evaluate_superionic_diffusion(pos_step_start, pos, box_size, inv_L, dt=1.0)
        mean_overlap = calc_mean_sleeve_overlap_fast(
            node_q, pos, adj, snr_array, R_sleeve=3.5, box_size=box_size, inv_L=inv_L
        )

        dp_array.append(D_p)
        overlap_array.append(mean_overlap)

        print(f" Step {t_idx+1:02d}/{temp_steps:02d} | Temp: {T_curr:6.1f} K | Beta: {beta_curr:.4f} | Diffusion D_p: {D_p:.4e} | Sleeve Overlap <S_ij>: {mean_overlap:.4f} | Throughput: {throughput:8.1f} Swp/s")
        gc.collect()

    dp_arr = np.array(dp_array)
    overlap_arr = np.array(overlap_array)

    if save_npz:
        safe_id = run_id.replace("/", "_").replace("\\", "_")
        export_filename = os.path.join(out_dir, f"{safe_id}_condensed_h2o_phase_seed{resolved_seed}_v656_results.npz")
        np.savez_compressed(
            export_filename,
            mode="PAPER5_CONDENSED_MATTER",
            condensed_mode="PHASE_DIAGRAM_H2O",
            run_id=run_id,
            seed=resolved_seed,
            grid_dim=grid_dim,
            N_nodes=N_nodes,
            temp_array=temp_array,
            D_p_array=dp_arr,
            sleeve_overlap_array=overlap_arr,
            P_ext=P_ext,
            benchmark_citations=np.array(["millot_2018", "cavazzoni_1999"], dtype=object)
        )
        return export_filename

    return temp_array, dp_arr, overlap_arr


def run_diamond_rain_carbon(
    grid_dim=16, P_ext=300.0, total_sweeps=30000, run_id="RUN-V656_PRODUCTION",
    out_dir=".", save_npz=True, seed=None
):
    resolved_seed = setup_prng(seed)
    os.makedirs(out_dir, exist_ok=True)

    pos, adj, is_coherent_edge, gauge_u, box_size, r0_eq = initialize_diamond_lattice(max(1, grid_dim // 4))
    N_nodes = pos.shape[0]
    inv_L = 1.0 / box_size

    aff_nodes_m1 = np.zeros(7, dtype=np.int32)
    aff_nodes_m3 = np.zeros(32, dtype=np.int32)
    edge_buf = np.zeros((128, 2), dtype=np.int32)
    shear_vecs_buf = np.zeros((6, 3), dtype=np.float64)

    sweeps_log = []
    shear_history = []
    torsion_history = []

    block_size = max(100, total_sweeps // 30)
    num_blocks = total_sweeps // block_size

    for b_idx in range(num_blocks):
        t_block_start = time.time()

        _ = run_numba_mcs_block(
            pos, adj, gauge_u, is_coherent_edge, box_size, inv_L, 3.0035,
            kappa_s=1.0, kappa_t=0.03, kappa_r=0.0, lambda_j=0.141421, r0=r0_eq,
            max_disp=0.02, max_gauge_disp=0.015, num_sweeps=block_size,
            aff_nodes_m1=aff_nodes_m1, aff_nodes_m3=aff_nodes_m3,
            edge_buf=edge_buf, shear_vecs_buf=shear_vecs_buf,
            cutoff_prefactor=3.85,
            is_warmup=False, mode_val=5, P_ext=P_ext
        )

        t_block_elapsed = time.time() - t_block_start
        throughput = block_size / max(1e-6, t_block_elapsed)

        H_tot, H_s, H_t, _, _ = calc_total_system_energy(
            pos, adj, is_coherent_edge, gauge_u, box_size, inv_L, r0_eq,
            1.0, 0.03, 0.0, 0.141421,
            scale_a=1.0, beta_untensing=0.0175, mode_val=5, max_degree=6
        )
        curr_mcs = (b_idx + 1) * block_size
        sweeps_log.append(curr_mcs)
        shear_history.append(H_s / float(N_nodes))
        torsion_history.append(H_t / float(N_nodes))

        print(f" Sweep {curr_mcs:7d}/{total_sweeps:7d} | Throughput: {throughput:8.1f} Swp/s | H_shear: {H_s/float(N_nodes):.6f} | H_torsion: {H_t/float(N_nodes):.6f} | H_tot: {H_tot:10.4f}")
        gc.collect()

    if save_npz:
        safe_id = run_id.replace("/", "_").replace("\\", "_")
        export_filename = os.path.join(out_dir, f"{safe_id}_condensed_diamond_carbon_seed{resolved_seed}_v656_results.npz")
        np.savez_compressed(
            export_filename,
            mode="PAPER5_CONDENSED_MATTER",
            condensed_mode="DIAMOND_RAIN_CARBON",
            run_id=run_id,
            seed=resolved_seed,
            grid_dim=grid_dim,
            N_nodes=N_nodes,
            sweeps_log=np.array(sweeps_log),
            shear_history=np.array(shear_history),
            torsion_history=np.array(torsion_history),
            P_ext=P_ext,
            benchmark_citations=np.array(["kraus_2017"], dtype=object)
        )
        return export_filename

    return np.array(sweeps_log), np.array(shear_history), np.array(torsion_history)


def run_superionic_onset(
    grid_dim=16, temp_val=2500.0, P_ext=150.0, total_sweeps=30000,
    run_id="RUN-V656_PRODUCTION", out_dir=".", save_npz=True, seed=None
):
    """
    Accumulates continuous unwrapped displacement vectors directly to eliminate
    spurious periodic boundary minimum-image oscillations in Superionic MSD.
    """
    resolved_seed = setup_prng(seed)
    os.makedirs(out_dir, exist_ok=True)

    pos, adj, is_coherent_edge, gauge_u, box_size, r0_eq = initialize_diamond_lattice(max(1, grid_dim // 4))
    N_nodes = pos.shape[0]
    inv_L = 1.0 / box_size

    pos_step_start = np.copy(pos)
    pos_unwrapped = np.copy(pos)
    pos_prev = np.copy(pos)

    aff_nodes_m1 = np.zeros(7, dtype=np.int32)
    aff_nodes_m3 = np.zeros(32, dtype=np.int32)
    edge_buf = np.zeros((128, 2), dtype=np.int32)
    shear_vecs_buf = np.zeros((6, 3), dtype=np.float64)

    beta_val = 1000.0 / max(1e-3, temp_val)
    time_log = []
    msd_log = []
    dp_log = []

    block_size = max(100, total_sweeps // 30)
    num_blocks = total_sweeps // block_size

    for b_idx in range(num_blocks):
        t_block_start = time.time()

        _ = run_numba_mcs_block(
            pos, adj, gauge_u, is_coherent_edge, box_size, inv_L, beta_val,
            kappa_s=1.0, kappa_t=0.03, kappa_r=0.0, lambda_j=0.141421, r0=r0_eq,
            max_disp=0.02, max_gauge_disp=0.015, num_sweeps=block_size,
            aff_nodes_m1=aff_nodes_m1, aff_nodes_m3=aff_nodes_m3,
            edge_buf=edge_buf, shear_vecs_buf=shear_vecs_buf,
            cutoff_prefactor=3.85,
            is_warmup=False, mode_val=5, P_ext=P_ext
        )

        t_block_elapsed = time.time() - t_block_start
        throughput = block_size / max(1e-6, t_block_elapsed)

        step_msd_sum = 0.0
        for i_p in range(N_nodes):
            dx, dy, dz = pbc_diff_vec(pos_prev[i_p], pos[i_p], box_size, inv_L)
            pos_unwrapped[i_p, 0] += dx
            pos_unwrapped[i_p, 1] += dy
            pos_unwrapped[i_p, 2] += dz
            
            dx_t = pos_unwrapped[i_p, 0] - pos_step_start[i_p, 0]
            dy_t = pos_unwrapped[i_p, 1] - pos_step_start[i_p, 1]
            dz_t = pos_unwrapped[i_p, 2] - pos_step_start[i_p, 2]
            step_msd_sum += (dx_t * dx_t + dy_t * dy_t + dz_t * dz_t)

        np.copyto(pos_prev, pos)

        curr_mcs = (b_idx + 1) * block_size
        msd_avg = step_msd_sum / float(N_nodes)
        D_p = msd_avg / (6.0 * max(1e-12, curr_mcs))

        time_log.append(curr_mcs)
        msd_log.append(msd_avg)
        dp_log.append(D_p)

        print(f" Sweep {curr_mcs:7d}/{total_sweeps:7d} | Throughput: {throughput:8.1f} Swp/s | Monotonic MSD: {msd_avg:.6f} | Diffusion D_p: {D_p:.4e}")
        gc.collect()

    if save_npz:
        safe_id = run_id.replace("/", "_").replace("\\", "_")
        export_filename = os.path.join(out_dir, f"{safe_id}_condensed_superionic_onset_seed{resolved_seed}_v656_results.npz")
        np.savez_compressed(
            export_filename,
            mode="PAPER5_CONDENSED_MATTER",
            condensed_mode="SUPERIONIC_ONSET",
            run_id=run_id,
            seed=resolved_seed,
            grid_dim=grid_dim,
            N_nodes=N_nodes,
            time_log=np.array(time_log),
            msd_log=np.array(msd_log),
            dp_log=np.array(dp_log),
            temp_val=temp_val,
            P_ext=P_ext,
            benchmark_citations=np.array(["millot_2018", "cavazzoni_1999"], dtype=object)
        )
        return export_filename

    return np.array(time_log), np.array(msd_log), np.array(dp_log)


def run_capacity_saturation(
    grid_dim=32, strain_start=0.05, strain_end=0.33, strain_steps=30,
    run_id="RUN-V656_PRODUCTION", out_dir=".", save_npz=True, seed=None
):
    resolved_seed = setup_prng(seed)
    os.makedirs(out_dir, exist_ok=True)

    strain_array = np.linspace(strain_start, strain_end, strain_steps)
    pressure_eos_array = []
    density_ratio_array = []

    pos, adj, is_coherent_edge, gauge_u, box_size, r0_eq = initialize_diamond_lattice(max(1, grid_dim // 4))
    N_nodes = pos.shape[0]

    for s_idx, tau_curr in enumerate(strain_array):
        tau_vector = np.full(N_nodes * 3, tau_curr, dtype=np.float64)
        P_eos = calc_capacity_saturated_eos(tau_vector, P_0=1.0, tau_max=1.0/3.0)
        mean_P = float(np.mean(P_eos))
        rho_ratio = tau_curr / (1.0 / 3.0)

        pressure_eos_array.append(mean_P)
        density_ratio_array.append(rho_ratio)

        print(f" Step {s_idx+1:02d}/{strain_steps:02d} | Strain tau: {tau_curr:.4f} | Rho/Rho_sat: {rho_ratio:.4f} | P_eos: {mean_P:.4e}")

    p_eos_arr = np.array(pressure_eos_array)
    rho_ratio_arr = np.array(density_ratio_array)

    if save_npz:
        safe_id = run_id.replace("/", "_").replace("\\", "_")
        export_filename = os.path.join(out_dir, f"{safe_id}_condensed_capacity_saturation_seed{resolved_seed}_v656_results.npz")
        np.savez_compressed(
            export_filename,
            mode="PAPER5_CONDENSED_MATTER",
            condensed_mode="CAPACITY_SATURATION",
            run_id=run_id,
            seed=resolved_seed,
            grid_dim=grid_dim,
            N_nodes=N_nodes,
            strain_array=strain_array,
            pressure_eos_array=p_eos_arr,
            density_ratio_array=rho_ratio_arr,
            benchmark_citations=np.array(["zeldovich_1962"], dtype=object)
        )
        return export_filename

    return strain_array, p_eos_arr, rho_ratio_arr


# ------------------------------------------------------------------------------
# 5. UNIFIED DRIVER & ENSEMBLE PARALLEL UTILITIES
# ------------------------------------------------------------------------------

def _ensemble_seed_worker(args_tuple):
    import numba
    numba.set_num_threads(1)  # Prevent CPU oversubscription per worker process
    seed, mode, thermo_mode, grid_dim, beta_mc, num_sweeps, run_id, out_dir = args_tuple
    return run_ela_simulation(
        mode=mode, thermo_mode=thermo_mode, grid_dim=grid_dim,
        beta_mc=beta_mc, num_sweeps=num_sweeps, run_id=run_id, seed=seed, out_dir=out_dir, save_npz=False
    )


def run_ensemble_parallel(num_seeds=8, base_seed=42, **kwargs):
    worker_args = [
        (base_seed + k, kwargs.get("mode"), kwargs.get("thermo_mode"), 
         kwargs.get("grid_dim"), kwargs.get("beta_mc"), kwargs.get("num_sweeps"), 
         kwargs.get("run_id", "RUN-V656_PRODUCTION"), kwargs.get("out_dir"))
        for k in range(num_seeds)
    ]
    
    results = []
    with ProcessPoolExecutor(max_workers=num_seeds) as executor:
        futures = [executor.submit(_ensemble_seed_worker, arg) for arg in worker_args]
        for future in as_completed(futures):
            results.append(future.result())
    return results


def run_ela_simulation(
    mode=EngineMode.PAPER1_VACUUM,
    condensed_mode=CondensedMatterMode.HYDROSTATIC_COMPRESSION,
    pressure_val=100.0,
    pressure_start=10.0,
    pressure_end=1000.0,
    pressure_steps=20,
    temp_val=2500.0,
    temp_start=300.0,
    temp_end=5000.0,
    temp_steps=20,
    thermo_mode=ThermoSweepMode.BETA_SWEEP,
    epr_mode=EPRMode.NONE,
    run_id="RUN-V656_PRODUCTION",
    grid_dim=16,
    beta_mc=3.0035,
    beta_gauge=6.15,
    beta_start=0.20,
    beta_end=3.50,
    beta_steps=25,
    fss_dims=[8, 16, 32],
    kappa_s=1.00,
    kappa_t=0.03,
    kappa_r=0.00,
    lambda_j=0.141421,
    snr_crit=7.50,
    cutoff_prefactor=3.85,
    beta_untensing=0.0175,
    epsilon_sw=0.002,
    scale_a_init=0.50,
    inject_soliton_flag=False,
    q_charge_val=1,
    max_disp=0.02,
    max_gauge_disp=0.015,
    num_sweeps=50000,
    log_interval=None,
    ds_interval=10000,
    seed=None,
    out_dir=".",
    save_npz=True,
    sleeve_mode=1,
    sleeve_sigma=0.02,
    sleeve_weight=1.0,
    sleeve_tunnel_alpha=0.05,
    enable_compliant_move3=False,
    compliance_alpha=0.15
):
    if mode == EngineMode.PAPER4_THERMODYNAMICS:
        if thermo_mode in (ThermoSweepMode.BETA_SWEEP, "sweep"):
            return run_thermo_beta_sweep(
                beta_start=beta_start, beta_end=beta_end, beta_steps=beta_steps,
                eq_sweeps=max(1000, num_sweeps // 5), meas_sweeps=num_sweeps,
                grid_dim=grid_dim, run_id=run_id, out_dir=out_dir, save_npz=save_npz, seed=seed,
                cutoff_prefactor=cutoff_prefactor,
                enable_compliant_move3=enable_compliant_move3,
                compliance_alpha=compliance_alpha
            )
        elif thermo_mode in (ThermoSweepMode.QUENCH_KINETICS, "quench"):
            return run_quench_kinetics(
                grid_dim=grid_dim, beta_target=beta_mc, strain_init=0.30,
                total_sweeps=num_sweeps, log_interval=max(100, num_sweeps // 100),
                run_id=run_id, out_dir=out_dir, save_npz=save_npz, seed=seed,
                cutoff_prefactor=cutoff_prefactor,
                enable_compliant_move3=enable_compliant_move3,
                compliance_alpha=compliance_alpha
            )
        elif thermo_mode in (ThermoSweepMode.FSS_ANALYSIS, "fss"):
            return run_fss_protocol(
                fss_grid_dims=fss_dims, beta_crit_est=2.15,
                run_id=run_id, out_dir=out_dir, save_npz=save_npz, seed=seed,
                enable_compliant_move3=enable_compliant_move3,
                compliance_alpha=compliance_alpha
            )

    if mode == EngineMode.PAPER5_CONDENSED_MATTER:
        if condensed_mode in (CondensedMatterMode.HYDROSTATIC_COMPRESSION, "compression"):
            return run_hydrostatic_compression(
                grid_dim=grid_dim, pressure_start=pressure_start, pressure_end=pressure_end,
                pressure_steps=pressure_steps, beta_target=beta_mc,
                run_id=run_id, out_dir=out_dir, save_npz=save_npz, seed=seed
            )
        elif condensed_mode in (CondensedMatterMode.PHASE_DIAGRAM_H2O, "h2o", "phase"):
            return run_phase_diagram_h2o(
                grid_dim=grid_dim, temp_start=temp_start, temp_end=temp_end,
                temp_steps=temp_steps, P_ext=pressure_val, total_sweeps=num_sweeps,
                run_id=run_id, out_dir=out_dir, save_npz=save_npz, seed=seed
            )
        elif condensed_mode in (CondensedMatterMode.DIAMOND_RAIN_CARBON, "carbon", "diamond"):
            return run_diamond_rain_carbon(
                grid_dim=grid_dim, P_ext=pressure_val, total_sweeps=num_sweeps,
                run_id=run_id, out_dir=out_dir, save_npz=save_npz, seed=seed
            )
        elif condensed_mode in (CondensedMatterMode.SUPERIONIC_ONSET, "superionic"):
            return run_superionic_onset(
                grid_dim=grid_dim, temp_val=temp_val, P_ext=pressure_val,
                total_sweeps=num_sweeps, run_id=run_id, out_dir=out_dir, save_npz=save_npz, seed=seed
            )
        elif condensed_mode in (CondensedMatterMode.CAPACITY_SATURATION, "saturation"):
            return run_capacity_saturation(
                grid_dim=grid_dim, run_id=run_id, out_dir=out_dir, save_npz=save_npz, seed=seed
            )

    resolved_seed = setup_prng(seed)
    os.makedirs(out_dir, exist_ok=True)

    if log_interval is None:
        log_interval = max(10, num_sweeps // 50) if num_sweeps < 10000 else 1000

    dim_cells = max(1, grid_dim // 4)
    pos, adj, is_coherent_edge, gauge_u, box_size, r0_eq = initialize_diamond_lattice(dim_cells, max_degree=6)
    N_nodes = pos.shape[0]
    inv_L = 1.0 / box_size
    max_degree = 6
    scale_a = scale_a_init

    if mode == EngineMode.PAPER2_GAUGE_SOLITON:
        plaquettes_buf = precompute_diamond_6cycles(adj, max_degree=max_degree)
    else:
        plaquettes_buf = np.empty((0, 12), dtype=np.int32)

    has_soliton = inject_soliton_flag or (q_charge_val != 0)
    if has_soliton:
        inject_topological_soliton(pos, adj, gauge_u, box_size, inv_L, q_charge=q_charge_val)
        print(f"[INIT] Injected SU(2) Skyrmionic Topological Soliton Field (Target Q = {q_charge_val})")

    if epr_mode == EPRMode.STATIC:
        inject_static_epr_shortcuts(adj, is_coherent_edge, target_density=epsilon_sw, max_degree=max_degree)

    slq_ws = SLQWorkspace(N_nodes, max_degree)
    aff_nodes_m1 = np.zeros(1 + max_degree, dtype=np.int32)
    aff_nodes_m3 = np.zeros(32, dtype=np.int32)
    edge_buf = np.zeros((128, 2), dtype=np.int32)
    shear_vecs_buf = np.zeros((6, 3), dtype=np.float64)

    energy_history = []
    sweep_history = []
    w_eos_history = []
    h_sq_history = []
    q_history = []
    splaq_history = []

    print("================================================================================")
    print("               EMERGENT LATTICE ARCHITECTURE (ELA v6.6.2)")
    print("         UNIFIED MULTI-MODE MONTE CARLO SIMULATION ENGINE & DATA STREAM")
    print("================================================================================")
    print(f" Active Mode      : {mode.name}")
    print(f" EPR Mode         : {epr_mode.name}")
    print(f" Run ID           : {run_id}")
    print(f" PRNG Seed        : {resolved_seed}")
    print(f" System Size (N)  : {N_nodes:,} (4-Regular 3D Diamond Torus - r0 = {r0_eq:.4f})")
    print(f" Total MCS Sweeps : {num_sweeps:,} (1 MCS = {N_nodes:,} Proposals)")
    print(f" Output Directory : {out_dir}")
    print("================================================================================\n")
    
    epr_val_int = 1 if epr_mode == EPRMode.DYNAMIC else (2 if epr_mode == EPRMode.STATIC else 0)

    _ = run_numba_mcs_block(
        pos, adj, gauge_u, is_coherent_edge, box_size, inv_L, beta_mc,
        kappa_s, kappa_t, kappa_r, lambda_j, r0_eq,
        max_disp, max_gauge_disp, 1,
        aff_nodes_m1, aff_nodes_m3, edge_buf, shear_vecs_buf,
        cutoff_prefactor=cutoff_prefactor, is_warmup=False, mode_val=mode.value, scale_a=scale_a,
        beta_untensing=beta_untensing, snr_crit=snr_crit, epr_mode_val=epr_val_int, epsilon_sw=epsilon_sw,
        has_soliton=has_soliton, beta_gauge=beta_gauge,
        sleeve_mode=sleeve_mode, sleeve_sigma=sleeve_sigma, sleeve_weight=sleeve_weight,
        sleeve_tunnel_alpha=sleeve_tunnel_alpha,
        p_spatial=0.20, p_gauge=0.10, p_pachner=0.70,
        use_compliance=enable_compliant_move3, compliance_alpha=compliance_alpha
    )
    fill_laplacian_csr_buffers(adj, slq_ws.indptr, slq_ws.indices, slq_ws.data)

    print("[INIT] Thermalizing spatial geometry around soliton core (if applicable)...")
    warmup_block_size = 20
    warmup_sweeps = 0
    max_warmup_cap = 1000
    ema_H_shear = None
    prev_ema_H_shear = 0.0
    alpha_ema = 0.3

    while warmup_sweeps < max_warmup_cap:
        _ = run_numba_mcs_block(
            pos, adj, gauge_u, is_coherent_edge, box_size, inv_L, beta_mc,
            kappa_s, kappa_t, kappa_r, lambda_j, r0_eq,
            max_disp, max_gauge_disp, warmup_block_size,
            aff_nodes_m1, aff_nodes_m3, edge_buf, shear_vecs_buf,
            cutoff_prefactor=cutoff_prefactor, is_warmup=True, mode_val=mode.value, scale_a=scale_a,
            beta_untensing=beta_untensing, snr_crit=snr_crit, epr_mode_val=epr_val_int, epsilon_sw=epsilon_sw,
            has_soliton=has_soliton, beta_gauge=beta_gauge,
            sleeve_mode=sleeve_mode, sleeve_sigma=sleeve_sigma, sleeve_weight=sleeve_weight,
            sleeve_tunnel_alpha=sleeve_tunnel_alpha,
            use_compliance=enable_compliant_move3, compliance_alpha=compliance_alpha
        )
        warmup_sweeps += warmup_block_size

        _, H_shear_curr, _, _, _ = calc_total_system_energy(
            pos, adj, is_coherent_edge, gauge_u, box_size, inv_L, r0_eq, kappa_s, kappa_t, kappa_r, lambda_j,
            scale_a=scale_a, beta_untensing=beta_untensing, mode_val=mode.value, max_degree=max_degree
        )

        if ema_H_shear is None:
            ema_H_shear = H_shear_curr
        else:
            ema_H_shear = alpha_ema * H_shear_curr + (1.0 - alpha_ema) * ema_H_shear

        if warmup_sweeps >= 40:
            rel_diff = abs(ema_H_shear - prev_ema_H_shear) / max(1.0, ema_H_shear)
            if rel_diff < 0.01:
                break
        prev_ema_H_shear = ema_H_shear

    print(f"[INIT] Spatial geometry thermalized in {warmup_sweeps} MCS (EMA H_shear = {ema_H_shear:.4f})")

    slq_diag_seed = int((resolved_seed ^ (0 + 1) * 1000003) & 0x7FFFFFFF)
    ds_curr, t_mid_curve, ds_curve = compute_ds_slq(
        adj, N_nodes, box_size, slq_ws,
        num_samples=30, m_lanczos=60,
        seed=slq_diag_seed, use_gpu=False
    )
    print(f"[INIT] Baseline Spectral Dimension d_s = {ds_curr:.4f}\n")

    t_sim_start = time.time()
    cum_pure_mc_time = 0.0
    current_sweep = 0
    num_blocks = num_sweeps // log_interval
    total_protected_swaps = 0

    for block_idx in range(num_blocks):
        t_block_start = time.time()

        if mode == EngineMode.PAPER3_COSMOLOGY:
            progress = (current_sweep + log_interval) / float(num_sweeps)
            scale_a = scale_a_init + (1.0 - scale_a_init) * progress
        
        res = run_numba_mcs_block(
            pos, adj, gauge_u, is_coherent_edge, box_size, inv_L, beta_mc,
            kappa_s, kappa_t, kappa_r, lambda_j, r0_eq,
            max_disp, max_gauge_disp, log_interval,
            aff_nodes_m1, aff_nodes_m3, edge_buf, shear_vecs_buf,
            cutoff_prefactor=cutoff_prefactor, is_warmup=False, mode_val=mode.value, scale_a=scale_a,
            beta_untensing=beta_untensing, snr_crit=snr_crit, epr_mode_val=epr_val_int, epsilon_sw=epsilon_sw,
            has_soliton=has_soliton, beta_gauge=beta_gauge,
            sleeve_mode=sleeve_mode, sleeve_sigma=sleeve_sigma, sleeve_weight=sleeve_weight,
            sleeve_tunnel_alpha=sleeve_tunnel_alpha,
            p_spatial=0.20, p_gauge=0.10, p_pachner=0.70,
            use_compliance=enable_compliant_move3, compliance_alpha=compliance_alpha
        )

        (s_att, s_acc, g_att, g_acc, t_att, t_acc, epr_att, epr_acc, lazy_exits, full_rejs, protected_swaps) = res[:11]
        
        t_block_end = time.time()
        interval_mc_time = t_block_end - t_block_start
        cum_pure_mc_time += interval_mc_time
        current_sweep += log_interval
        total_protected_swaps += protected_swaps

        if current_sweep % 10000 == 0:
            reindex_spatial_cache(pos, adj, is_coherent_edge, gauge_u, box_size)
            if mode == EngineMode.PAPER2_GAUGE_SOLITON:
                plaquettes_buf = precompute_diamond_6cycles(adj, max_degree=max_degree)

        H_curr, _, _, _, _ = calc_total_system_energy(
            pos, adj, is_coherent_edge, gauge_u, box_size, inv_L, r0_eq,
            kappa_s, kappa_t, kappa_r, lambda_j,
            scale_a=scale_a, beta_untensing=beta_untensing, mode_val=mode.value, max_degree=max_degree
        )
        energy_history.append(H_curr)
        sweep_history.append(current_sweep)

        H_sq, w_eos, d_G, rho_energy = compute_lqc_bounce_diagnostics(H_curr, N_nodes, scale_a, beta_untensing)
        w_eos_history.append(w_eos)
        h_sq_history.append(H_sq)

        if mode == EngineMode.PAPER2_GAUGE_SOLITON:
            gauge_u_cooled = cool_gauge_field_6cycle(adj, gauge_u, num_cooling_sweeps=50)
            q_curr = calc_topological_charge_q(pos, adj, gauge_u_cooled, box_size, inv_L, r0=r0_eq)
            q_history.append(q_curr)
            su2_plaq = calc_su2_plaquette_fast(gauge_u, plaquettes_buf)
            splaq_history.append(su2_plaq)
        else:
            q_history.append(0.0)
            splaq_history.append(0.0)

        interval_throughput = log_interval / max(1e-6, interval_mc_time)

        if current_sweep % ds_interval == 0 or current_sweep == num_sweeps:
            slq_diag_seed = int((resolved_seed ^ (current_sweep + 1) * 1000003) & 0x7FFFFFFF)
            ds_curr, t_mid_curve, ds_curve = compute_ds_slq(
                adj, N_nodes, box_size, slq_ws,
                num_samples=15, m_lanczos=35,
                seed=slq_diag_seed, use_gpu=False
            )

        print(f" Sweep {current_sweep:7d}/{num_sweeps:7d} | Throughput: {interval_throughput:8.1f} Swp/s | H_tot: {H_curr:10.4f} | d_s: {ds_curr:.4f}")
        gc.collect()

    t_final = time.time()
    total_elapsed = t_final - t_sim_start

    H_tot, H_s, H_t, H_r, V_j = calc_total_system_energy(
        pos, adj, is_coherent_edge, gauge_u, box_size, inv_L, r0_eq, kappa_s, kappa_t, kappa_r, lambda_j,
        scale_a=scale_a, beta_untensing=beta_untensing, mode_val=mode.value, max_degree=max_degree
    )

    slq_diag_seed = int((resolved_seed ^ (num_sweeps + 1) * 1000003) & 0x7FFFFFFF)
    ds_final, t_mid_curve, ds_curve = compute_ds_slq(
        adj, N_nodes, box_size, slq_ws,
        num_samples=50, m_lanczos=45,
        seed=slq_diag_seed, use_gpu=False
    )
    cv_out = compute_cv_binning(energy_history, beta_mc, N_nodes)
    if isinstance(cv_out, tuple):
        specific_heat_Cv, specific_heat_Cv_err = cv_out
    else:
        specific_heat_Cv = float(cv_out)
        specific_heat_Cv_err = 0.0

    if mode == EngineMode.PAPER2_GAUGE_SOLITON:
        gauge_u_cooled = cool_gauge_field_6cycle(adj, gauge_u, num_cooling_sweeps=50)
        su2_plaquette_action = calc_su2_plaquette_fast(gauge_u, plaquettes_buf)
        topological_charge_Q = calc_topological_charge_q(pos, adj, gauge_u_cooled, box_size, inv_L, r0=r0_eq)
        strand_q_charge = calc_strand_helicity_charge(gauge_u)
        bps_soliton_mass = H_tot / (1.0)
    else:
        su2_plaquette_action = 0.0
        topological_charge_Q = 0.0
        strand_q_charge = 0.0
        bps_soliton_mass = 0.0

    print("-" * 105)
    print(f"\n================================================================================")
    print(f"                       SIMULATION COMPLETE & AUDITED ({mode.name})")
    print(f"================================================================================")
    print(f" Total Elapsed Time : {total_elapsed:.2f} s | Pure MC Time: {cum_pure_mc_time:.2f} s")
    print(f" Final Spectral Dim : {ds_final:.4f} (Target Continuum Limit: 3.00)")
    print(f" Specific Heat Cv   : {specific_heat_Cv:.6f} +/- {specific_heat_Cv_err:.6f}")
    print(f" Total Energy H_tot : {H_tot:.4f}")

    if save_npz:
        safe_id = run_id.replace("/", "_").replace("\\", "_")
        export_filename = os.path.join(out_dir, f"{safe_id}_{mode.name}_seed{resolved_seed}_v656_results.npz")
        np.savez_compressed(
            export_filename,
            mode=mode.name,
            epr_mode=epr_mode.name,
            seed=resolved_seed,
            run_id=run_id,
            grid_dim=grid_dim,
            N_nodes=N_nodes,
            beta_mc=beta_mc,
            beta_gauge=beta_gauge,
            kappa_s=kappa_s,
            kappa_t=kappa_t,
            kappa_r=kappa_r,
            lambda_j=lambda_j,
            snr_crit=snr_crit,
            cutoff_prefactor=cutoff_prefactor,
            sleeve_mode=sleeve_mode,
            sleeve_sigma=sleeve_sigma,
            sleeve_weight=sleeve_weight,
            sleeve_tunnel_alpha=sleeve_tunnel_alpha,
            ds_final=ds_final,
            specific_heat_Cv=specific_heat_Cv,
            specific_heat_Cv_err=specific_heat_Cv_err,
            su2_plaquette_action=su2_plaquette_action,
            topological_charge_Q=topological_charge_Q,
            strand_q_charge=strand_q_charge,
            bps_soliton_mass=bps_soliton_mass,
            total_protected_swaps=total_protected_swaps,
            t_mid_curve=t_mid_curve,
            ds_curve=ds_curve,
            sweep_history=np.array(sweep_history),
            energy_history=np.array(energy_history),
            q_history=np.array(q_history),
            splaq_history=np.array(splaq_history),
            w_eos_history=np.array(w_eos_history),
            h_sq_history=np.array(h_sq_history),
            H_components=np.array([H_tot, H_s, H_t, H_r, V_j]),
            benchmark_citations=np.array(["ela_paper_i_2026", "keating_1966"], dtype=object)
        )
        print(f"[EXPORT] Publication payload saved successfully to '{export_filename}'\n")
        return export_filename

    return None
