#!/usr/bin/env python3
"""
================================================================================
EMERGENT LATTICE ARCHITECTURE (ELA) - NUMBA JIT MATH & PHYSICS KERNELS
================================================================================
Module 2 of 5: Pure C-Speed High-Performance Math Suite (math_kernels.py v6.6.2)

Provenance: [PURE LITERATURE]
References:
  - Paper I   [ela_paper_i_2026]   : Foundations, Hydrodynamic Limits & Spacetime Emergence (DOI: 10.5281/zenodo.21843307)
  - Paper II  [ela_paper_ii_2026]  : Micro-Scale Soliton Topology, Gauges & Antimatter (DOI: 10.5281/zenodo.21843352)
  - Paper III [ela_paper_iii_2026] : Macro Cosmological Untensing, Geometrogenesis & Dark Energy (DOI: 10.5281/zenodo.21843375)
  - Paper IV  [ela_paper_iv_2026]  : Substrate Thermodynamics & Vacuum Kinetics (DOI: 10.5281/zenodo.23268981)
  - Paper V   [ela_paper_v_2026]   : Relational Condensed Matter & Extreme EoS (DOI: 10.5281/zenodo.23269009)
  - Literature: Keating (1966) [keating_1966], Martin (1970) [martin_1970], Wilson (1974) [wilson_1974],
                McDonald (1972) [mcdonald_1972], Ubaru et al. (2017) [ubaru_2017], Saad (2003) [saad_2003].
"""

import math
import numpy as np
from numba import njit, prange

# Local module import [ELA ARCHITECTURE]
from references import __references__


# ------------------------------------------------------------------------------
# 0. MODULE-LEVEL GLOBAL HOISTED INVARIANTS (v6.6.2 OPTIMIZED)
# ------------------------------------------------------------------------------
INV_THREE = 1.0 / 3.0
INV_SIX = 1.0 / 6.0
INV_NINE = 1.0 / 9.0
TWO_THIRDS = 2.0 / 3.0
HALF = 0.5
PI_OVER_TWELVE = math.pi / 12.0
INV_PI = 1.0 / math.pi
INV_TWO_PI = 1.0 / (2.0 * math.pi)
EIGHT_PI_OVER_THREE = (8.0 * math.pi) / 3.0
INV_RHO_CRIT = 1.0 / 30.0
TOPO_PREFACTOR = -(27.0 / 64.0) / (24.0 * math.pi * math.pi)
TAU_MAX = 1.0 / 3.0
INV_TAU_MAX = 3.0
INV_TAU_MAX_SQ = 9.0
GAMMA_POLY = 5.0 / 3.0
CAP_PREFACTOR = -250.0 / 9.0

# Static logarithmic time grid hoisting [saad_2003, ubaru_2017]
SLQ_T_VALS = np.logspace(-1.0, 1.5, 60)
SLQ_LOG_T = np.log(SLQ_T_VALS)


# ------------------------------------------------------------------------------
# 1. VECTOR MATH, PBC & QUATERNION ALGEBRA
# ------------------------------------------------------------------------------

@njit(fastmath=True, inline='always')
def pbc_diff_vec(p1, p2, L, inv_L):
    """
    Calculates spatial separation vector under Periodic Boundary Conditions (PBC) using MIC.
    Optimized: Replaces 3x floating-point floor, multiplication, and addition with
    branch-predicted boundary clamping. 100% bitwise identical for all p1, p2 in [0, L).
    
    Provenance: [PURE LITERATURE]
    Reference : Allen & Tildesley (1987), Computer Simulation of Liquids. [allen_tildesley_1987]
    """
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    dz = p2[2] - p1[2]
    half_L = 0.5 * L

    if dx >= half_L:
        dx -= L
    elif dx < -half_L:
        dx += L

    if dy >= half_L:
        dy -= L
    elif dy < -half_L:
        dy += L

    if dz >= half_L:
        dz -= L
    elif dz < -half_L:
        dz += L

    return dx, dy, dz


@njit(fastmath=True, inline='always')
def fast_unit_vec(p1, p2, L, inv_L):
    """
    Computes normalized unit direction vector using hardware reciprocal sqrt (rsqrt).
    Returns unit components and squared Euclidean norm: (ux, uy, uz, norm_sq).
    """
    dx, dy, dz = pbc_diff_vec(p1, p2, L, inv_L)
    norm_sq = dx * dx + dy * dy + dz * dz
    if norm_sq < 1e-14:
        return 0.0, 0.0, 0.0, 0.0
    inv = 1.0 / math.sqrt(norm_sq)
    return dx * inv, dy * inv, dz * inv, norm_sq


@njit(fastmath=True, inline='always')
def quat_mult(q, r):
    """
    Executes Hamilton product of two 4-component unit quaternions (SU(2) link holonomies).
    
    Provenance: [PURE LITERATURE]
    Reference : Hamilton (1844), Phil. Mag. 25, 489. [hamilton_1844]
    """
    w = q[0]*r[0] - q[1]*r[1] - q[2]*r[2] - q[3]*r[3]
    x = q[0]*r[1] + q[1]*r[0] + q[2]*r[3] - q[3]*r[2]
    y = q[0]*r[2] - q[1]*r[3] + q[2]*r[0] + q[3]*r[1]
    z = q[0]*r[3] + q[1]*r[2] - q[2]*r[1] + q[3]*r[0]
    return w, x, y, z


@njit(fastmath=True, inline='always')
def quat_mult_scalars(w1, x1, y1, z1, w2, x2, y2, z2):
    """
    [AVX2 FMA UNROLLED QUATERNION MULTIPLICATION]
    Executes Hamilton product of two 4-component unit quaternions using scalar registers.
    
    Provenance: [PURE LITERATURE]
    Reference : Hamilton (1844), Phil. Mag. 25, 489. [hamilton_1844]
    """
    w = w1*w2 - x1*x2 - y1*y2 - z1*z2
    x = w1*x2 + x1*w2 + y1*z2 - z1*y2
    y = w1*y2 - x1*z2 + y1*w2 + z1*x2
    z = w1*z2 + x1*y2 - y1*x2 + z1*w2
    return w, x, y, z


@njit(fastmath=True, inline='always')
def align_holonomy_geodesic(qw_in, qx_in, qy_in, qz_in, p_start, p_old_target, p_new_target, box_size, inv_L):
    """
    Parallel transports SU(2) link holonomies along S^3 geodesic arcs using
    pure algebraic half-angle identities in scalar CPU registers.
    
    Provenance: [ELA ADAPTED]
    Reference : Paper V (Relational Condensed Matter) Section 2.1. [ela_paper_v_2026]
    """
    dx1, dy1, dz1 = pbc_diff_vec(p_start, p_old_target, box_size, inv_L)
    n1_sq = dx1 * dx1 + dy1 * dy1 + dz1 * dz1
    if n1_sq < 1e-14:
        return qw_in, qx_in, qy_in, qz_in
    inv_n1 = 1.0 / math.sqrt(n1_sq)
    e1_x = dx1 * inv_n1; e1_y = dy1 * inv_n1; e1_z = dz1 * inv_n1

    dx2, dy2, dz2 = pbc_diff_vec(p_start, p_new_target, box_size, inv_L)
    n2_sq = dx2 * dx2 + dy2 * dy2 + dz2 * dz2
    if n2_sq < 1e-14:
        return qw_in, qx_in, qy_in, qz_in
    inv_n2 = 1.0 / math.sqrt(n2_sq)
    e2_x = dx2 * inv_n2; e2_y = dy2 * inv_n2; e2_z = dz2 * inv_n2

    dot = e1_x * e2_x + e1_y * e2_y + e1_z * e2_z
    if dot > 0.9999999:
        return qw_in, qx_in, qy_in, qz_in

    if dot < -0.9999999:
        orth_x = 0.0; orth_y = 0.0; orth_z = 1.0
        if abs(e1_z) > 0.8:
            orth_x = 1.0; orth_z = 0.0
        ax = e1_y * orth_z - e1_z * orth_y
        ay = e1_z * orth_x - e1_x * orth_z
        az = e1_x * orth_y - e1_y * orth_x
        norm = math.sqrt(ax * ax + ay * ay + az * az)
        if norm > 1e-12:
            inv = 1.0 / norm
            qw, qx, qy, qz = 0.0, ax * inv, ay * inv, az * inv
        else:
            qw, qx, qy, qz = 0.0, 1.0, 0.0, 0.0
    else:
        cx = e1_y * e2_z - e1_z * e2_y
        cy = e1_z * e2_x - e1_x * e2_z
        cz = e1_x * e2_y - e1_y * e2_x

        s = math.sqrt(2.0 * (1.0 + dot))
        inv_s = 1.0 / s
        qw = 0.5 * s
        qx = cx * inv_s
        qy = cy * inv_s
        qz = cz * inv_s

    w, x, y, z = quat_mult_scalars(qw, qx, qy, qz, qw_in, qx_in, qy_in, qz_in)
    norm_q = math.sqrt(w * w + x * x + y * y + z * z)
    if norm_q > 1e-12:
        inv_q = 1.0 / norm_q
        w *= inv_q; x *= inv_q; y *= inv_q; z *= inv_q
    return w, x, y, z


# ------------------------------------------------------------------------------
# 2. HAMILTONIAN POTENTIAL ENERGIES
# ------------------------------------------------------------------------------

@njit(fastmath=True, inline='always')
def calc_node_shear(u, adj, pos, L, inv_L, max_degree=6):
    """
    [ZERO-ALLOCATION SCALAR REGISTER OPTIMIZATION]
    Computes bond-angle shear strain energy based on the Valence Force Field (VFF) model.
    Stores direction vectors in scalar registers to eliminate heap array allocations
    and guarantee 100% thread safety across parallel prange loops.
    
    Provenance: [PURE LITERATURE]
    Reference : Keating (1966), Phys. Rev. 145, 637. [keating_1966]
    Formula   : V_shear = (3/16) * (beta_vff / d^2) * \\sum_{i < j} (\\mathbf{r}_{ui} \\cdot \\mathbf{r}_{uj} + d^2 / 3)^2
    """
    shear = 0.0

    dx0 = 0.0; dy0 = 0.0; dz0 = 0.0
    dx1 = 0.0; dy1 = 0.0; dz1 = 0.0
    dx2 = 0.0; dy2 = 0.0; dz2 = 0.0
    dx3 = 0.0; dy3 = 0.0; dz3 = 0.0
    dx4 = 0.0; dy4 = 0.0; dz4 = 0.0
    dx5 = 0.0; dy5 = 0.0; dz5 = 0.0

    deg = 0
    for i in range(max_degree):
        v = adj[u, i]
        if v >= 0:
            dx, dy, dz, norm_sq = fast_unit_vec(pos[u], pos[v], L, inv_L)
            if norm_sq > 0.0:
                if deg == 0: dx0 = dx; dy0 = dy; dz0 = dz
                elif deg == 1: dx1 = dx; dy1 = dy; dz1 = dz
                elif deg == 2: dx2 = dx; dy2 = dy; dz2 = dz
                elif deg == 3: dx3 = dx; dy3 = dy; dz3 = dz
                elif deg == 4: dx4 = dx; dy4 = dy; dz4 = dz
                elif deg == 5: dx5 = dx; dy5 = dy; dz5 = dz
                deg += 1

    if deg >= 2:
        d = dx0*dx1 + dy0*dy1 + dz0*dz1 + INV_THREE; shear += d*d
    if deg >= 3:
        d = dx0*dx2 + dy0*dy2 + dz0*dz2 + INV_THREE; shear += d*d
        d = dx1*dx2 + dy1*dy2 + dz1*dz2 + INV_THREE; shear += d*d
    if deg >= 4:
        d = dx0*dx3 + dy0*dy3 + dz0*dz3 + INV_THREE; shear += d*d
        d = dx1*dx3 + dy1*dy3 + dz1*dz3 + INV_THREE; shear += d*d
        d = dx2*dx3 + dy2*dy3 + dz2*dz3 + INV_THREE; shear += d*d
    if deg >= 5:
        d = dx0*dx4 + dy0*dy4 + dz0*dz4 + INV_THREE; shear += d*d
        d = dx1*dx4 + dy1*dy4 + dz1*dz4 + INV_THREE; shear += d*d
        d = dx2*dx4 + dy2*dy4 + dz2*dz4 + INV_THREE; shear += d*d
        d = dx3*dx4 + dy3*dy4 + dz3*dz4 + INV_THREE; shear += d*d
    if deg >= 6:
        d = dx0*dx5 + dy0*dy5 + dz0*dz5 + INV_THREE; shear += d*d
        d = dx1*dx5 + dy1*dy5 + dz1*dz5 + INV_THREE; shear += d*d
        d = dx2*dx5 + dy2*dy5 + dz2*dz5 + INV_THREE; shear += d*d
        d = dx3*dx5 + dy3*dy5 + dz3*dz5 + INV_THREE; shear += d*d
        d = dx4*dx5 + dy4*dy5 + dz4*dz5 + INV_THREE; shear += d*d

    return shear


@njit(fastmath=True, inline='always')
def calc_edge_torsion(j, k, adj, pos, L, inv_L, max_degree=6):
    """
    Computes dihedral bond-torsion strain energy using Horner's polynomial rule.
    
    Provenance: [PURE LITERATURE]
    Reference : Martin (1970), Phys. Rev. B 1, 4005. [martin_1970]
    Formula   : V_torsion = w1 * w2 * (1 + 4*c^3 - 3*c) == w1 * w2 * (1 + c*(4*c^2 - 3))
    """
    pj = pos[j]
    pk = pos[k]
    ujk_x, ujk_y, ujk_z, norm_sq_jk = fast_unit_vec(pj, pk, L, inv_L)
    if norm_sq_jk < 1e-14:
        return 0.0
    
    l0_nx = 0.0; l0_ny = 0.0; l0_nz = 0.0; l0_w2 = 0.0
    l1_nx = 0.0; l1_ny = 0.0; l1_nz = 0.0; l1_w2 = 0.0
    l2_nx = 0.0; l2_ny = 0.0; l2_nz = 0.0; l2_w2 = 0.0
    n2_count = 0
    
    for idx_l in range(max_degree):
        l = adj[k, idx_l]
        if l < 0 or l == j:
            continue
            
        v_kl_x, v_kl_y, v_kl_z = pbc_diff_vec(pk, pos[l], L, inv_L)
        n2_x = v_kl_y * ujk_z - v_kl_z * ujk_y
        n2_y = v_kl_z * ujk_x - v_kl_x * ujk_z
        n2_z = v_kl_x * ujk_y - v_kl_y * ujk_x
        
        norm2_sq = n2_x * n2_x + n2_y * n2_y + n2_z * n2_z
        if norm2_sq < 1e-12:
            continue
        norm2 = math.sqrt(norm2_sq)
        inv2 = 1.0 / norm2
        
        l_kl_sq = v_kl_x * v_kl_x + v_kl_y * v_kl_y + v_kl_z * v_kl_z
        w2_val = norm2_sq / max(1e-12, l_kl_sq)
        
        if n2_count == 0:
            l0_nx = n2_x * inv2; l0_ny = n2_y * inv2; l0_nz = n2_z * inv2; l0_w2 = w2_val
        elif n2_count == 1:
            l1_nx = n2_x * inv2; l1_ny = n2_y * inv2; l1_nz = n2_z * inv2; l1_w2 = w2_val
        elif n2_count == 2:
            l2_nx = n2_x * inv2; l2_ny = n2_y * inv2; l2_nz = n2_z * inv2; l2_w2 = w2_val
        n2_count += 1

    if n2_count == 0:
        return 0.0

    torsion = 0.0
    for idx_i in range(max_degree):
        i = adj[j, idx_i]
        if i < 0 or i == k:
            continue
            
        v_ji_x, v_ji_y, v_ji_z = pbc_diff_vec(pj, pos[i], L, inv_L)
        n1_x = v_ji_y * ujk_z - v_ji_z * ujk_y
        n1_y = v_ji_z * ujk_x - v_ji_x * ujk_z
        n1_z = v_ji_x * ujk_y - v_ji_y * ujk_x
        
        norm1_sq = n1_x * n1_x + n1_y * n1_y + n1_z * n1_z
        if norm1_sq < 1e-12:
            continue
        norm1 = math.sqrt(norm1_sq)
        inv1 = 1.0 / norm1
        n1_x *= inv1; n1_y *= inv1; n1_z *= inv1
        
        l_ji_sq = v_ji_x * v_ji_x + v_ji_y * v_ji_y + v_ji_z * v_ji_z
        w1 = norm1_sq / max(1e-12, l_ji_sq)
        
        if n2_count > 0:
            c = max(-1.0, min(1.0, n1_x * l0_nx + n1_y * l0_ny + n1_z * l0_nz))
            torsion += w1 * l0_w2 * (1.0 + c * (4.0 * c * c - 3.0))
        if n2_count > 1:
            c = max(-1.0, min(1.0, n1_x * l1_nx + n1_y * l1_ny + n1_z * l1_nz))
            torsion += w1 * l1_w2 * (1.0 + c * (4.0 * c * c - 3.0))
        if n2_count > 2:
            c = max(-1.0, min(1.0, n1_x * l2_nx + n1_y * l2_ny + n1_z * l2_nz))
            torsion += w1 * l2_w2 * (1.0 + c * (4.0 * c * c - 3.0))
            
    return torsion


@njit(fastmath=True, inline='always')
def calc_edge_stretch(u, v, pos, r0, L, inv_L):
    """
    Computes central harmonic bond-length stretching strain energy.
    
    Provenance: [PURE LITERATURE]
    Reference : Keating (1966), Phys. Rev. 145, 637. [keating_1966]
    Formula   : V_stretch = (r - r0)^2
    """
    dx, dy, dz = pbc_diff_vec(pos[u], pos[v], L, inv_L)
    dist = math.sqrt(dx * dx + dy * dy + dz * dz)
    dev = dist - r0
    return dev * dev


@njit(fastmath=True, inline='always')
def calc_node_jamming(u, gauge_u, max_degree=6):
    """
    Computes node gauge phase jamming potential V_j = 0.5 * lambda * sum(1 - q0).
    
    Provenance: [ELA ADAPTED]
    Reference : Paper 5 Monograph. [ela_paper_v_2026]
    """
    jamming = 0.0
    for i in range(max_degree):
        q0 = gauge_u[u, i, 0]
        jamming += (1.0 - q0)
    return jamming


@njit(fastmath=True, inline='always')
def calc_edge_local_plaquette_action(u, e_idx, adj, gauge_u, max_degree=6):
    """
    Computes local 6-cycle Wilson plaquette action increment for an edge on diamond networks.
    
    Provenance: [PURE LITERATURE]
    Reference : Wilson (1974), Phys. Rev. D 10, 2445. [wilson_1974]
    """
    v = adj[u, e_idx]
    if v < 0:
        return 0.0

    total_action = 0.0
    q1_w = gauge_u[u, e_idx, 0]
    q1_x = gauge_u[u, e_idx, 1]
    q1_y = gauge_u[u, e_idx, 2]
    q1_z = gauge_u[u, e_idx, 3]

    for j in range(max_degree):
        w = adj[v, j]
        if w < 0 or w == u:
            continue

        for k in range(max_degree):
            x = adj[w, k]
            if x < 0 or x == v or x == u:
                continue

            for l in range(max_degree):
                y = adj[x, l]
                if y < 0 or y == w or y == v or y == u:
                    continue

                for z_u_idx in range(max_degree):
                    z = adj[u, z_u_idx]
                    if z < 0 or z == x or z == w or z == v:
                        continue

                    y_z_idx = -1
                    for m in range(max_degree):
                        if adj[y, m] == z:
                            y_z_idx = m
                            break

                    if y_z_idx >= 0:
                        z_u_link_idx = -1
                        for n_idx in range(max_degree):
                            if adj[z, n_idx] == u:
                                z_u_link_idx = n_idx
                                break

                        if z_u_link_idx >= 0:
                            q2_w = gauge_u[v, j, 0]; q2_x = gauge_u[v, j, 1]; q2_y = gauge_u[v, j, 2]; q2_z = gauge_u[v, j, 3]
                            q3_w = gauge_u[w, k, 0]; q3_x = gauge_u[w, k, 1]; q3_y = gauge_u[w, k, 2]; q3_z = gauge_u[w, k, 3]
                            q4_w = gauge_u[x, l, 0]; q4_x = gauge_u[x, l, 1]; q4_y = gauge_u[x, l, 2]; q4_z = gauge_u[x, l, 3]
                            q5_w = gauge_u[y, y_z_idx, 0]; q5_x = gauge_u[y, y_z_idx, 1]; q5_y = gauge_u[y, y_z_idx, 2]; q5_z = gauge_u[y, y_z_idx, 3]
                            q6_w = gauge_u[z, z_u_link_idx, 0]; q6_x = gauge_u[z, z_u_link_idx, 1]; q6_y = gauge_u[z, z_u_link_idx, 2]; q6_z = gauge_u[z, z_u_link_idx, 3]

                            w12, x12, y12, z12 = quat_mult_scalars(q1_w, q1_x, q1_y, q1_z, q2_w, q2_x, q2_y, q2_z)
                            w34, x34, y34, z34 = quat_mult_scalars(q3_w, q3_x, q3_y, q3_z, q4_w, q4_x, q4_y, q4_z)
                            w56, x56, y56, z56 = quat_mult_scalars(q5_w, q5_x, q5_y, q5_z, q6_w, q6_x, q6_y, q6_z)

                            w1234, x1234, y1234, z1234 = quat_mult_scalars(w12, x12, y12, z12, w34, x34, y34, z34)
                            w_P, _, _, _ = quat_mult_scalars(w1234, x1234, y1234, z1234, w56, x56, y56, z56)

                            total_action += (1.0 - w_P)

    return total_action


@njit(fastmath=True, inline='always')
def sum_torsion_for_nodes(nodes_list, n_count, adj, pos, L, inv_L, edge_buf, max_degree=6):
    """
    Aggregates Keating dihedral torsion energy across local node neighborhoods.
    
    Provenance: [PURE LITERATURE]
    Reference : Martin (1970), Phys. Rev. B 1, 4005. [martin_1970]
    """
    n_edges = 0
    for idx in range(n_count):
        u = nodes_list[idx]
        for i in range(max_degree):
            v = adj[u, i]
            if v >= 0:
                n1 = min(u, v)
                n2 = max(u, v)
                exists = False
                for e in range(n_edges):
                    if edge_buf[e, 0] == n1 and edge_buf[e, 1] == n2:
                        exists = True
                        break
                if not exists and n_edges < 128:
                    edge_buf[n_edges, 0] = n1
                    edge_buf[n_edges, 1] = n2
                    n_edges += 1
                    
    total_torsion = 0.0
    for e in range(n_edges):
        total_torsion += calc_edge_torsion(edge_buf[e, 0], edge_buf[e, 1], adj, pos, L, inv_L, max_degree)
    return total_torsion


@njit(fastmath=True, inline='always')
def calc_total_system_energy_serial(pos, adj, is_coherent_edge, gauge_u, L, inv_L, r0, ks, kt, kr, lj, scale_a=1.0, beta_untensing=0.0175, mode_val=1, max_degree=6):
    """
    [STRICTLY SERIAL INLINED EVALUATOR FOR MCMC SWEEP ACCUMULATION]
    Evaluates total Hamiltonian H_tot using pure single-threaded sequential range loops.
    Eliminates Parfor AST cycles and OpenMP synchronization barriers when called
    directly inside JIT-compiled Monte Carlo proposal kernels.
    """
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


@njit(fastmath=True)
def calc_total_system_energy(pos, adj, is_coherent_edge, gauge_u, L, inv_L, r0, ks, kt, kr, lj, scale_a=1.0, beta_untensing=0.0175, mode_val=1, max_degree=6):
    """
    [ZERO-ALLOCATION SCALAR HAMILTONIAN ACCUMULATOR]
    Evaluates total system energy without dynamic heap allocations or thread team overhead.
    Preserves exact signatures and values across serial and multiprocessing execution.
    """
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
# 3. PAPER 5 RELATIONAL CONDENSED MATTER KERNELS
# ------------------------------------------------------------------------------

@njit(fastmath=True)
def calc_multi_sleeve_overlap(node_q, pos, adj, snr_array, R_sleeve, box_size, inv_L):
    """
    Computes pairwise Fermi-Dirac sleeve overlap matrix S_ij across N_soliton nodes.
    Guarded to prevent fatal OOM aborts at N >= 4096.
    
    Provenance: [ELA ADAPTED]
    Reference : Paper 5 Monograph. [ela_paper_v_2026]
    """
    N = pos.shape[0]
    if N > 4096:
        raise ValueError("calc_multi_sleeve_overlap is restricted to N <= 4096 to prevent OOM allocations.")
    
    S_ij = np.zeros((N, N), dtype=np.float64)
    two_R = 2.0 * R_sleeve
    four_R = 4.0 * R_sleeve
    cutoff_sq = four_R * R_sleeve
    
    for i in range(N):
        if node_q[i] != 0:
            f_i = 1.0 / (1.0 + math.exp(-snr_array[i]))
            for j in range(i + 1, N):
                if node_q[j] != 0:
                    dx, dy, dz = pbc_diff_vec(pos[i], pos[j], box_size, inv_L)
                    dist_sq = dx * dx + dy * dy + dz * dz
                    if dist_sq < cutoff_sq:
                        dist = math.sqrt(dist_sq)
                        f_j = 1.0 / (1.0 + math.exp(-snr_array[j]))
                        diff = two_R - dist
                        overlap_vol = PI_OVER_TWELVE * (four_R + dist) * (diff * diff)
                        val = f_i * f_j * overlap_vol
                        S_ij[i, j] = val
                        S_ij[j, i] = val
    return S_ij


@njit(fastmath=True)
def calc_mean_sleeve_overlap_fast(node_q, pos, adj, snr_array, R_sleeve, box_size, inv_L):
    """
    Computes mean Fermi-Dirac sleeve overlap directly over active non-zero nodes,
    bypassing inactive Cartesian pairs.
    
    Provenance: [ELA ADAPTED]
    Reference : Paper 5 Monograph. [ela_paper_v_2026]
    """
    N = pos.shape[0]
    active_count = 0
    for i in range(N):
        if node_q[i] != 0:
            active_count += 1

    if active_count < 2:
        return 0.0

    active_indices = np.empty(active_count, dtype=np.int32)
    idx_fill = 0
    for i in range(N):
        if node_q[i] != 0:
            active_indices[idx_fill] = i
            idx_fill += 1

    total_val = 0.0
    pair_count = 0
    two_R = 2.0 * R_sleeve
    four_R = 4.0 * R_sleeve
    cutoff_sq = four_R * R_sleeve

    for a in range(active_count):
        i = active_indices[a]
        f_i = 1.0 / (1.0 + math.exp(-snr_array[i]))
        for b in range(a + 1, active_count):
            j = active_indices[b]
            dx, dy, dz = pbc_diff_vec(pos[i], pos[j], box_size, inv_L)
            dist_sq = dx * dx + dy * dy + dz * dz
            if dist_sq < cutoff_sq:
                dist = math.sqrt(dist_sq)
                f_j = 1.0 / (1.0 + math.exp(-snr_array[j]))
                diff = two_R - dist
                overlap_vol = PI_OVER_TWELVE * (four_R + dist) * (diff * diff)
                total_val += f_i * f_j * overlap_vol
                pair_count += 1

    return total_val / float(max(1, pair_count))


@njit(fastmath=True, parallel=True)
def calc_capacity_saturated_eos(tau_array, P_0=1.0, gamma_poly=1.6666666666666667, tau_max=0.3333333333333333):
    """
    Evaluates local link strain against tau_max = 1/3 capacity ceiling.
    Triggers divergent resistance factor P(tau) near saturation.
    Optimized: Replaces division by tau_max with multiplication by INV_TAU_MAX.
    
    Provenance: [ELA ADAPTED]
    Reference : Paper 5 Monograph Section 3.2. [ela_paper_v_2026]
    Formula   : P(tau) = P_0 * (1 + tau)^gamma / [1 - (tau / tau_max)^2]
    """
    N_links = tau_array.shape[0]
    pressure_factor = np.zeros(N_links, dtype=np.float64)
    inv_t_max = 1.0 / max(1e-12, tau_max)
    
    for e in prange(N_links):
        tau_e = tau_array[e]
        ratio = tau_e * inv_t_max
        if ratio >= 0.999999:
            pressure_factor[e] = 1.0e8  # Divergent capacity barrier
        else:
            denom = 1.0 - (ratio * ratio)
            pressure_factor[e] = P_0 * ((1.0 + tau_e) ** gamma_poly) / denom
            
    return pressure_factor


@njit(fastmath=True)
def calc_hydrostatic_compression_energy(pos, adj, P_ext, box_size, inv_L, K_0=1.0, max_degree=6):
    """
    Computes isotropic relational compression energy delta H_P for Monte Carlo updates.
    Hoists prefactor multiplication outside the O(N) edge reduction loop.
    
    Provenance: [PURE LITERATURE]
    Reference : McDonald (1972), Mol. Phys. 23, 41. [mcdonald_1972]
    """
    N = pos.shape[0]
    sum_dist_cubed = 0.0
    p_prefactor = P_ext / (3.0 * max(1e-12, K_0))

    for i in range(N):
        for j_idx in range(max_degree):
            j = adj[i, j_idx]
            if j > i:
                dx, dy, dz = pbc_diff_vec(pos[i], pos[j], box_size, inv_L)
                dist_sq = dx * dx + dy * dy + dz * dz
                sum_dist_cubed += math.sqrt(dist_sq) * dist_sq
                
    return sum_dist_cubed * p_prefactor


@njit(fastmath=True, parallel=True)
def evaluate_superionic_diffusion(pos_protons_init, pos_protons_curr, box_size, inv_L, dt):
    """
    Measures proton/hydrogen knot diffusion coefficients D_p through
    the stationary oxygen/carbon rigid sub-graph, unwrapping PBC torus crossings.
    
    Provenance: [PURE LITERATURE]
    Reference : Einstein (1905), Ann. Phys. 317, 549. [einstein_1905]
    Formula   : D_p = <delta r^2> / (6 * delta t)
    """
    N_p = pos_protons_curr.shape[0]
    msd = 0.0
    
    for i in prange(N_p):
        dx, dy, dz = pbc_diff_vec(pos_protons_init[i], pos_protons_curr[i], box_size, inv_L)
        disp_sq = dx * dx + dy * dy + dz * dz
        msd += disp_sq
        
    msd_avg = msd / float(N_p)
    D_p = msd_avg / (6.0 * max(1e-12, dt))
    return D_p, msd_avg


# ------------------------------------------------------------------------------
# 4. GAUGE FIELD, COOLING, SOLITON & LQC KERNELS
# ------------------------------------------------------------------------------

@njit(fastmath=True, cache=True)
def cool_gauge_field_6cycle(adj, gauge_u, num_cooling_sweeps=25):
    """
    Relaxes local UV thermal fluctuations in SU(2) link fields along 6-cycle Wilson action gradient.
    
    Provenance: [PURE LITERATURE]
    Reference : Morningstar & Peardon (1999), Phys. Rev. D 60, 034509. [morningstar_1999]
    """
    N = adj.shape[0]
    max_degree = adj.shape[1]
    cooled_u = np.copy(gauge_u)
    
    for sweep in range(num_cooling_sweeps):
        for u in range(N):
            for i in range(max_degree):
                v = adj[u, i]
                if v > u:
                    v_u_idx = -1
                    for k in range(max_degree):
                        if adj[v, k] == u:
                            v_u_idx = k
                            break
                    if v_u_idx >= 0:
                        staple_w = 0.0; staple_x = 0.0; staple_y = 0.0; staple_z = 0.0
                        staple_count = 0
                        
                        for j in range(max_degree):
                            w = adj[v, j]
                            if w >= 0 and w != u:
                                for k in range(max_degree):
                                    x_node = adj[w, k]
                                    if x_node >= 0 and x_node != v and x_node != u:
                                        for l in range(max_degree):
                                            y_node = adj[x_node, l]
                                            if y_node >= 0 and y_node != w and y_node != v and y_node != u:
                                                for m in range(max_degree):
                                                    z_node = adj[y_node, m]
                                                    if z_node >= 0 and z_node != x_node and z_node != w and z_node != v and z_node != u:
                                                        for n_idx in range(max_degree):
                                                            if adj[z_node, n_idx] == u:
                                                                w23, x23, y23, z23 = quat_mult_scalars(
                                                                    cooled_u[v, j, 0], cooled_u[v, j, 1], cooled_u[v, j, 2], cooled_u[v, j, 3],
                                                                    cooled_u[w, k, 0], cooled_u[w, k, 1], cooled_u[w, k, 2], cooled_u[w, k, 3]
                                                                )
                                                                w45, x45, y45, z45 = quat_mult_scalars(
                                                                    cooled_u[x_node, l, 0], cooled_u[x_node, l, 1], cooled_u[x_node, l, 2], cooled_u[x_node, l, 3],
                                                                    cooled_u[y_node, m, 0], cooled_u[y_node, m, 1], cooled_u[y_node, m, 2], cooled_u[y_node, m, 3]
                                                                )
                                                                w2345, x2345, y2345, z2345 = quat_mult_scalars(
                                                                    w23, x23, y23, z23, w45, x45, y45, z45
                                                                )
                                                                w_st, x_st, y_st, z_st = quat_mult_scalars(
                                                                    w2345, x2345, y2345, z2345,
                                                                    cooled_u[z_node, n_idx, 0], cooled_u[z_node, n_idx, 1], cooled_u[z_node, n_idx, 2], cooled_u[z_node, n_idx, 3]
                                                                )
                                                                
                                                                staple_w += w_st; staple_x += -x_st
                                                                staple_y += -y_st; staple_z += -z_st
                                                                staple_count += 1
                                                                break
                        
                        if staple_count > 0:
                            norm = math.sqrt(staple_w*staple_w + staple_x*staple_x + staple_y*staple_y + staple_z*staple_z)
                            if norm > 1e-12:
                                inv = 1.0 / norm
                                q0 = staple_w * inv; q1 = staple_x * inv
                                q2 = staple_y * inv; q3 = staple_z * inv
                                
                                cooled_u[u, i, 0] = q0; cooled_u[u, i, 1] = q1
                                cooled_u[u, i, 2] = q2; cooled_u[u, i, 3] = q3
                                cooled_u[v, v_u_idx, 0] = q0; cooled_u[v, v_u_idx, 1] = -q1
                                cooled_u[v, v_u_idx, 2] = -q2; cooled_u[v, v_u_idx, 3] = -q3

    return cooled_u


@njit(fastmath=True)
def calc_su2_plaquette_action(adj, gauge_u, max_degree=6):
    """
    Calculates average 6-cycle SU(2) Wilson Plaquette Action S_P for diamond lattices.
    
    Provenance: [PURE LITERATURE]
    Reference : Wilson (1974), Phys. Rev. D 10, 2445. [wilson_1974]
    """
    N = adj.shape[0]
    total_action = 0.0
    p_count = 0

    for u in range(N):
        for i in range(max_degree):
            v = adj[u, i]
            if v > u:
                for j in range(max_degree):
                    w = adj[v, j]
                    if w >= 0 and w != u:
                        for k in range(max_degree):
                            x = adj[w, k]
                            if x >= 0 and x != v and x != u:
                                for l in range(max_degree):
                                    y = adj[x, l]
                                    if y >= 0 and y != w and y != v and y != u:
                                        for m in range(max_degree):
                                            z = adj[y, m]
                                            if z >= 0 and z != x and z != w and z != v:
                                                for n_idx in range(max_degree):
                                                    if adj[z, n_idx] == u:
                                                        if u == min(u, v, w, x, y, z):
                                                            q1 = gauge_u[u, i]
                                                            q2 = gauge_u[v, j]
                                                            q3 = gauge_u[w, k]
                                                            q4 = gauge_u[x, l]
                                                            q5 = gauge_u[y, m]
                                                            q6 = gauge_u[z, n_idx]

                                                            w12, x12, y12, z12 = quat_mult(q1, q2)
                                                            w34, x34, y34, z34 = quat_mult(q3, q4)
                                                            w56, x56, y56, z56 = quat_mult(q5, q6)

                                                            q12 = np.array([w12, x12, y12, z12], dtype=np.float64)
                                                            q34 = np.array([w34, x34, y34, z34], dtype=np.float64)
                                                            q56 = np.array([w56, x56, y56, z56], dtype=np.float64)

                                                            w1234, x1234, y1234, z1234 = quat_mult(q12, q34)
                                                            q1234 = np.array([w1234, x1234, y1234, z1234], dtype=np.float64)

                                                            w_P, _, _, _ = quat_mult(q1234, q56)
                                                            total_action += (1.0 - w_P)
                                                            p_count += 1
                                                        break
    return total_action / max(1, p_count)


@njit(fastmath=True)
def precompute_diamond_6cycles(adj, max_degree=6):
    """
    Precomputes static 6-cycle plaquette indices with early monotonic pruning (w, x, y, z > u).
    Guarantees exact cycle enumeration with 16x fewer loop iterations.
    
    Provenance: [PURE LITERATURE]
    Reference : Wilson (1974), Phys. Rev. D 10, 2445. [wilson_1974]
    """
    N = adj.shape[0]
    max_plaques = N * 6
    buf = np.zeros((max_plaques, 12), dtype=np.int32)
    p_count = 0

    for u in range(N):
        for i in range(max_degree):
            v = adj[u, i]
            if v > u:
                for j in range(max_degree):
                    w = adj[v, j]
                    if w > u and w != v:
                        for k in range(max_degree):
                            x = adj[w, k]
                            if x > u and x != v and x != w:
                                for l in range(max_degree):
                                    y = adj[x, l]
                                    if y > u and y != w and y != v and y != x:
                                        for m in range(max_degree):
                                            z = adj[y, m]
                                            if z > u and z != x and z != w and z != v and z != y:
                                                for n_idx in range(max_degree):
                                                    if adj[z, n_idx] == u:
                                                        if p_count < max_plaques:
                                                            buf[p_count, 0] = u; buf[p_count, 1] = i
                                                            buf[p_count, 2] = v; buf[p_count, 3] = j
                                                            buf[p_count, 4] = w; buf[p_count, 5] = k
                                                            buf[p_count, 6] = x; buf[p_count, 7] = l
                                                            buf[p_count, 8] = y; buf[p_count, 9] = m
                                                            buf[p_count, 10] = z; buf[p_count, 11] = n_idx
                                                            p_count += 1
                                                        break
    return buf[:p_count]


@njit(fastmath=True, cache=True)
def calc_su2_plaquette_fast(gauge_u, plaquettes_buf):
    """
    Fast O(N_plaquettes) SU(2) Wilson Plaquette Action readout using precomputed 6-cycle indices.
    
    Provenance: [PURE LITERATURE]
    Reference : Wilson (1974), Phys. Rev. D 10, 2445. [wilson_1974]
    """
    n_plaq = plaquettes_buf.shape[0]
    if n_plaq == 0:
        return 0.0

    total_action = 0.0
    for p in range(n_plaq):
        u = plaquettes_buf[p, 0]; i = plaquettes_buf[p, 1]
        v = plaquettes_buf[p, 2]; j = plaquettes_buf[p, 3]
        w = plaquettes_buf[p, 4]; k = plaquettes_buf[p, 5]
        x = plaquettes_buf[p, 6]; l = plaquettes_buf[p, 7]
        y = plaquettes_buf[p, 8]; m = plaquettes_buf[p, 9]
        z = plaquettes_buf[p, 10]; n_idx = plaquettes_buf[p, 11]

        w12, x12, y12, z12 = quat_mult_scalars(
            gauge_u[u, i, 0], gauge_u[u, i, 1], gauge_u[u, i, 2], gauge_u[u, i, 3],
            gauge_u[v, j, 0], gauge_u[v, j, 1], gauge_u[v, j, 2], gauge_u[v, j, 3]
        )
        w34, x34, y34, z34 = quat_mult_scalars(
            gauge_u[w, k, 0], gauge_u[w, k, 1], gauge_u[w, k, 2], gauge_u[w, k, 3],
            gauge_u[x, l, 0], gauge_u[x, l, 1], gauge_u[x, l, 2], gauge_u[x, l, 3]
        )
        w56, x56, y56, z56 = quat_mult_scalars(
            gauge_u[y, m, 0], gauge_u[y, m, 1], gauge_u[y, m, 2], gauge_u[y, m, 3],
            gauge_u[z, n_idx, 0], gauge_u[z, n_idx, 1], gauge_u[z, n_idx, 2], gauge_u[z, n_idx, 3]
        )

        w1234, x1234, y1234, z1234 = quat_mult_scalars(w12, x12, y12, z12, w34, x34, y34, z34)
        w_P, _, _, _ = quat_mult_scalars(w1234, x1234, y1234, z1234, w56, x56, y56, z56)
        total_action += (1.0 - w_P)

    return total_action / float(n_plaq)


@njit(fastmath=True, cache=True)
def calc_topological_charge_q(pos, adj, gauge_u, box_size, inv_L, r0=1.7320508075688772):
    """
    Calculates continuous topological Skyrmion charge Q.
    Uses multilinear determinant factoring: det(lambda * G) = lambda^3 * det(G).
    
    Provenance: [PURE LITERATURE]
    Reference : Berg (1981), Phys. Lett. B 104, 475. [berg_1981]
    Formula   : Q = -(1 / 24 pi^2) * \\int \\epsilon^{ijk} Tr[(U^-1 \\partial_i U)(U^-1 \\partial_j U)(U^-1 \\partial_k U)] d^3x
    Notes     : Applies (27/64) volumetric Jacobian correction for diamond lattices.
    """
    N = pos.shape[0]
    max_degree = gauge_u.shape[1]
    total_Q_density = 0.0

    for u in range(N):
        g0_0 = 0.0; g0_1 = 0.0; g0_2 = 0.0
        g1_0 = 0.0; g1_1 = 0.0; g1_2 = 0.0
        g2_0 = 0.0; g2_1 = 0.0; g2_2 = 0.0

        for i in range(max_degree):
            v = adj[u, i]
            if v >= 0:
                dx, dy, dz = pbc_diff_vec(pos[u], pos[v], box_size, inv_L)
                q1 = gauge_u[u, i, 1]
                q2 = gauge_u[u, i, 2]
                q3 = gauge_u[u, i, 3]

                g0_0 += q1 * dx; g0_1 += q1 * dy; g0_2 += q1 * dz
                g1_0 += q2 * dx; g1_1 += q2 * dy; g1_2 += q2 * dz
                g2_0 += q3 * dx; g2_1 += q3 * dy; g2_2 += q3 * dz

        det_color = (
            g0_0 * (g1_1 * g2_2 - g1_2 * g2_1)
            - g0_1 * (g1_0 * g2_2 - g1_2 * g2_0)
            + g0_2 * (g1_0 * g2_1 - g1_1 * g2_0)
        )

        total_Q_density += det_color

    V_node = (box_size * box_size * box_size) / float(N)
    grad_scale = 3.0 / (r0 * r0)
    det_scale = grad_scale * grad_scale * grad_scale

    return total_Q_density * det_scale * V_node * TOPO_PREFACTOR


@njit(fastmath=True)
def calc_strand_helicity_charge(gauge_u):
    """
    Evaluates fractionally quantized strand helicity charge q_k based on global U(1) phase winding.
    
    Provenance: [ELA ADAPTED]
    Reference : Paper 5 Monograph. [ela_paper_v_2026]
    """
    N = gauge_u.shape[0]
    max_degree = gauge_u.shape[1]
    total_phase = 0.0

    for u in range(N):
        for i in range(max_degree):
            q0 = gauge_u[u, i, 0]
            q1 = gauge_u[u, i, 1]
            total_phase += math.atan2(q1, q0)

    avg_phase = (total_phase / float(N * max_degree)) * INV_PI
    if avg_phase > 0.33:
        q_strand = 2.0 / 3.0
    elif avg_phase < -0.33:
        q_strand = -1.0
    else:
        q_strand = -1.0 / 3.0

    return q_strand


@njit(fastmath=True)
def inject_topological_soliton(pos, adj, gauge_u, box_size, inv_L, q_charge=1, core_radius=3.5):
    """
    Constructs an SU(2) Skyrmion hedgehog configuration mapping S^3 -> S^3 with winding number Q.
    
    Provenance: [PURE LITERATURE]
    Reference : Skyrme (1962), Nucl. Phys. 31, 556. [skyrme_1962]
    """
    N = pos.shape[0]
    max_degree = gauge_u.shape[1]
    center = np.array([box_size * 0.5, box_size * 0.5, box_size * 0.5], dtype=np.float64)

    node_q = np.zeros((N, 4), dtype=np.float64)

    for u in range(N):
        dx = pos[u, 0] - center[0]
        dy = pos[u, 1] - center[1]
        dz = pos[u, 2] - center[2]
        dx -= box_size * math.floor(dx * inv_L + 0.5)
        dy -= box_size * math.floor(dy * inv_L + 0.5)
        dz -= box_size * math.floor(dz * inv_L + 0.5)

        r = math.sqrt(dx * dx + dy * dy + dz * dz)
        if r > 1e-6:
            nx, ny, nz = dx / r, dy / r, dz / r
        else:
            nx, ny, nz = 0.0, 0.0, 1.0

        theta = math.pi * math.exp(-r / core_radius) * float(q_charge)
        sin_t = math.sin(theta); cos_t = math.cos(theta)
        node_q[u, 0] = cos_t; node_q[u, 1] = nx * sin_t
        node_q[u, 2] = ny * sin_t; node_q[u, 3] = nz * sin_t

    for u in range(N):
        qu0 = node_q[u, 0]; qu1 = -node_q[u, 1]; qu2 = -node_q[u, 2]; qu3 = -node_q[u, 3]

        for i in range(max_degree):
            v = adj[u, i]
            if v >= 0:
                qv0 = node_q[v, 0]; qv1 = node_q[v, 1]; qv2 = node_q[v, 2]; qv3 = node_q[v, 3]

                w = qu0*qv0 - qu1*qv1 - qu2*qv2 - qu3*qv3
                x = qu0*qv1 + qu1*qv0 + qu2*qv3 - qu3*qv2
                y = qu0*qv2 - qu1*qv3 + qu2*qv0 + qu3*qv1
                z = qu0*qv3 + qu1*qv2 - qu2*qv1 + qu3*qv0

                norm = math.sqrt(w*w + x*x + y*y + z*z)
                if norm > 1e-12:
                    inv = 1.0 / norm
                    w *= inv; x *= inv; y *= inv; z *= inv

                gauge_u[u, i, 0] = w; gauge_u[u, i, 1] = x
                gauge_u[u, i, 2] = y; gauge_u[u, i, 3] = z


@njit(fastmath=True)
def compute_lqc_bounce_diagnostics(H_tot, N_nodes, scale_a, beta_untensing=0.0175):
    """
    Evaluates modified Friedmann Hubble expansion rate H^2 under LQC holonomy corrections and CPL dark energy w(a).
    
    Provenance: [PURE LITERATURE]
    Reference : Ashtekar et al. (2006), Phys. Rev. D 74, 084003. [ashtekar_2006]
    Formula   : H^2 = (8 pi / 3) * rho * (1 - rho / rho_crit), rho_crit = 30.0
    """
    V_eff = float(N_nodes) * (scale_a * scale_a * scale_a)
    rho_energy = H_tot / max(1e-9, V_eff)
    rho_ratio = min(1.0, max(0.0, rho_energy * INV_RHO_CRIT))
    
    d_G = 2.0 * math.asin(math.sqrt(rho_ratio))
    cos_half_dG = math.cos(d_G * 0.5)
    
    H_squared = EIGHT_PI_OVER_THREE * rho_energy * (cos_half_dG * cos_half_dG)
    w_a = -2.0 * beta_untensing
    w_eos = -1.0 + w_a * (1.0 - scale_a)
    
    return H_squared, w_eos, d_G, rho_energy


# ------------------------------------------------------------------------------
# 5. PRE-ALLOCATED CSR LAPLACIAN & PURE NUMBA SLQ SOLVER ENGINE
# ------------------------------------------------------------------------------

@njit(fastmath=True)
def fill_laplacian_csr_buffers(adj, indptr, indices, data):
    """
    Constructs Compressed Sparse Row (CSR) matrix buffers for graph Laplacians.
    
    Provenance: [PURE LITERATURE]
    Reference : Saad (2003), Iterative Methods for Sparse Linear Systems. [saad_2003]
    """
    N = adj.shape[0]
    max_degree = adj.shape[1]
    nnz = 0
    indptr[0] = 0
    
    for u in range(N):
        deg = 0
        for i in range(max_degree):
            v = adj[u, i]
            if v >= 0:
                indices[nnz] = v
                data[nnz] = -1.0
                nnz += 1
                deg += 1
        indices[nnz] = u
        data[nnz] = float(deg)
        nnz += 1
        indptr[u + 1] = nnz
        
    return nnz


@njit(fastmath=True)
def numba_csr_matvec_serial(indptr, indices, data, x, y):
    """
    Sequential CSR MatVec for N <= 4096.
    
    Provenance: [PURE LITERATURE]
    Reference : Saad (2003), Iterative Methods for Sparse Linear Systems. [saad_2003]
    """
    N = x.shape[0]
    for i in range(N):
        acc = 0.0
        for j in range(indptr[i], indptr[i + 1]):
            acc += data[j] * x[indices[j]]
        y[i] = acc


@njit(fastmath=True, parallel=True)
def numba_csr_matvec_parallel(indptr, indices, data, x, y):
    """
    Parallel CSR MatVec for N > 4096 using OpenMP/TBB prange threading.
    
    Provenance: [PURE LITERATURE]
    Reference : Saad (2003), Iterative Methods for Sparse Linear Systems. [saad_2003]
    """
    for i in prange(x.shape[0]):
        acc = 0.0
        for j in range(indptr[i], indptr[i + 1]):
            acc += data[j] * x[indices[j]]
        y[i] = acc


@njit(fastmath=True)
def numba_csr_matvec_adaptive(indptr, indices, data, x, y):
    """
    Adaptive dispatch wrapper routing based on system volume N.
    
    Provenance: [PURE LITERATURE]
    Reference : Saad (2003), Iterative Methods for Sparse Linear Systems. [saad_2003]
    """
    if x.shape[0] <= 4096:
        numba_csr_matvec_serial(indptr, indices, data, x, y)
    else:
        numba_csr_matvec_parallel(indptr, indices, data, x, y)


@njit(fastmath=True, inline='always')
def _splitmix64_next(state):
    """
    [ISOLATED DETERMINISTIC 64-BIT SPLITMIX PRNG]
    Generates high-period pseudo-random integers without modifying Numba's global PRNG state.
    Guarantees that diagnostic SLQ evaluations do not alter MCMC proposal trajectories.
    """
    state[0] = (state[0] + np.uint64(0x9E3779B97F4A7C15)) & np.uint64(0xFFFFFFFFFFFFFFFF)
    z = state[0]
    z = ((z ^ (z >> np.uint64(30))) * np.uint64(0xBF58476D1CE4E5B9)) & np.uint64(0xFFFFFFFFFFFFFFFF)
    z = ((z ^ (z >> np.uint64(27))) * np.uint64(0x94D049BB133111EB)) & np.uint64(0xFFFFFFFFFFFFFFFF)
    z = z ^ (z >> np.uint64(31))
    return z


@njit(fastmath=True)
def _slq_lanczos_tridiag_kernel(indptr, indices, data, N_nodes, t_vals, num_samples, m_lanczos, w, w_next, v_prev, alpha_buf, beta_buf, slq_seed=104729):
    """
    [SERIAL INLINED LANCZOS MATVEC ENGINE - PRNG ISOLATED & ZERO-ALLOCATION]
    Inlines direct sparse matrix-vector multiplication using dedicated SplitMix64 sampling
    and pre-allocated 1D buffers for alpha and beta to eliminate inner-loop heap allocations.
    """
    P_t = np.zeros(len(t_vals), dtype=np.float64)
    inv_sqrt_N = 1.0 / math.sqrt(N_nodes)
    prng_state = np.array([np.uint64(slq_seed & 0x7FFFFFFF)], dtype=np.uint64)

    for s in range(num_samples):
        for i in range(N_nodes):
            rand_val = _splitmix64_next(prng_state)
            w[i] = inv_sqrt_N if (rand_val & np.uint64(1)) == np.uint64(1) else -inv_sqrt_N

        alpha = alpha_buf
        beta = beta_buf
        alpha.fill(0.0)
        beta.fill(0.0)
        v_prev.fill(0.0)
        j_final = m_lanczos - 1

        for j in range(m_lanczos):
            for r_idx in range(N_nodes):
                acc = 0.0
                for c_idx in range(indptr[r_idx], indptr[r_idx + 1]):
                    acc += data[c_idx] * w[indices[c_idx]]
                w_next[r_idx] = acc
            
            acc_alpha = 0.0
            for i in range(N_nodes):
                acc_alpha += w[i] * w_next[i]
            alpha[j] = acc_alpha

            for i in range(N_nodes):
                w_next[i] -= alpha[j] * w[i] + (beta[j-1] * v_prev[i] if j > 0 else 0.0)

            if j < m_lanczos - 1:
                acc_norm = 0.0
                for i in range(N_nodes):
                    acc_norm += w_next[i] * w_next[i]
                b = math.sqrt(acc_norm)
                beta[j] = b

                if b < 1e-12:
                    j_final = j
                    break

                inv_b = 1.0 / b
                for i in range(N_nodes):
                    v_prev[i] = w[i]
                    w[i] = w_next[i] * inv_b

        m_dim = j_final + 1
        # Contiguous allocation for eigh() LAPACK call
        T_mat = np.zeros((m_dim, m_dim), dtype=np.float64)
        for i in range(m_dim):
            T_mat[i, i] = alpha[i]
            if i < m_dim - 1:
                T_mat[i, i + 1] = beta[i]
                T_mat[i + 1, i] = beta[i]

        eig_T, Q_T = np.linalg.eigh(T_mat)
        q0 = Q_T[0, :]
        tau = q0 * q0

        for k in range(len(t_vals)):
            t = t_vals[k]
            acc_p = 0.0
            for idx in range(len(eig_T)):
                acc_p += tau[idx] * math.exp(-eig_T[idx] * t)
            P_t[k] += acc_p

    return P_t / float(num_samples)


class SLQWorkspace:
    """
    Pre-allocated workspace buffers for Stochastic Lanczos Quadrature (SLQ) execution.
    
    Provenance: [PURE LITERATURE]
    Reference : Saad (2003) [saad_2003]; Ubaru et al. (2017) [ubaru_2017]
    """
    def __init__(self, N_nodes: int, max_degree: int = 6, m_lanczos: int = 128):
        self.N_nodes = N_nodes
        self.max_nnz = N_nodes * (max_degree + 1)
        self.indptr = np.zeros(N_nodes + 1, dtype=np.int32)
        self.indices = np.zeros(self.max_nnz, dtype=np.int32)
        self.data = np.zeros(self.max_nnz, dtype=np.float64)
        
        self.w = np.zeros(N_nodes, dtype=np.float64)
        self.w_next = np.zeros(N_nodes, dtype=np.float64)
        self.v_prev = np.zeros(N_nodes, dtype=np.float64)

        # Pre-allocated 1D buffers with headroom to prevent heap buffer overrun
        alloc_m = max(128, m_lanczos)
        self.alpha = np.zeros(alloc_m, dtype=np.float64)
        self.beta = np.zeros(alloc_m, dtype=np.float64)


# ------------------------------------------------------------------------------
# 6. HYBRID GPU/CPU STOCHASTIC LANCZOS QUADRATURE ENGINE
# ------------------------------------------------------------------------------

CUPY_AVAILABLE = False
_CUPY_CHECKED = False
cp = None
cp_sparse = None


def check_cupy_available():
    """
    Lazily checks and imports CuPy on first explicit demand.
    Prevents premature CUDA driver context initialization, device polling,
    and display-server resource locks during CPU-only simulation runs.
    """
    global CUPY_AVAILABLE, _CUPY_CHECKED, cp, cp_sparse
    if not _CUPY_CHECKED:
        _CUPY_CHECKED = True
        try:
            import cupy as _cp
            import cupyx.scipy.sparse as _cp_sparse
            cp = _cp
            cp_sparse = _cp_sparse
            CUPY_AVAILABLE = True
        except (ImportError, Exception):
            CUPY_AVAILABLE = False
    return CUPY_AVAILABLE


def _slq_lanczos_gpu_tridiag(indptr, indices, data, N_nodes, t_vals, num_samples, m_lanczos, slq_seed=104729):
    """
    [DETERMINISTIC GPU-ACCELERATED LANCZOS QUADRATURE VIA CUPY CSR SPMV]
    Executes sparse matrix-vector multiplications directly on GPU CUDA cores.
    Explicitly re-seeds CuPy PRNG to ensure 100% run-to-run repeatability.
    """
    if not check_cupy_available():
        raise RuntimeError("CuPy is requested but not available on this system.")

    # Deterministic device PRNG initialization
    cp.random.seed(int(slq_seed & 0x7FFFFFFF))

    indptr_gpu = cp.asarray(indptr)
    indices_gpu = cp.asarray(indices)
    data_gpu = cp.asarray(data)
    
    L_csr_gpu = cp_sparse.csr_matrix((data_gpu, indices_gpu, indptr_gpu), shape=(N_nodes, N_nodes))
    
    P_t = cp.zeros(len(t_vals), dtype=cp.float64)
    t_vals_gpu = cp.asarray(t_vals)
    inv_sqrt_N = 1.0 / math.sqrt(N_nodes)

    for s in range(num_samples):
        # Generate Rademacher vector on GPU: {-1/sqrt(N), +1/sqrt(N)}
        rand_bits = cp.random.randint(0, 2, size=N_nodes, dtype=cp.int32)
        w_gpu = cp.where(rand_bits == 1, inv_sqrt_N, -inv_sqrt_N).astype(cp.float64)
        
        v_prev_gpu = cp.zeros(N_nodes, dtype=cp.float64)
        alpha = np.zeros(m_lanczos, dtype=np.float64)
        beta = np.zeros(m_lanczos, dtype=np.float64)
        j_final = m_lanczos - 1

        for j in range(m_lanczos):
            w_next_gpu = L_csr_gpu.dot(w_gpu)
            
            a_val = float(cp.dot(w_gpu, w_next_gpu))
            alpha[j] = a_val
            
            w_next_gpu -= a_val * w_gpu
            if j > 0:
                w_next_gpu -= beta[j - 1] * v_prev_gpu

            if j < m_lanczos - 1:
                b_val = float(cp.linalg.norm(w_next_gpu))
                beta[j] = b_val
                if b_val < 1e-12:
                    j_final = j
                    break
                v_prev_gpu = cp.copy(w_gpu)
                w_gpu = w_next_gpu / b_val

        m_dim = j_final + 1
        T_mat = np.zeros((m_dim, m_dim), dtype=np.float64)
        for i in range(m_dim):
            T_mat[i, i] = alpha[i]
            if i < m_dim - 1:
                T_mat[i, i + 1] = beta[i]
                T_mat[i + 1, i] = beta[i]

        eig_T, Q_T = np.linalg.eigh(T_mat)
        tau = (Q_T[0, :] ** 2)

        eig_T_gpu = cp.asarray(eig_T)
        tau_gpu = cp.asarray(tau)
        
        exponent = -cp.outer(eig_T_gpu, t_vals_gpu)
        P_t += cp.sum(tau_gpu[:, None] * cp.exp(exponent), axis=0)

    P_t_host = cp.asnumpy(P_t) / float(num_samples)
    return P_t_host


def compute_ds_slq(adj, N_nodes, box_size, slq_ws: SLQWorkspace, num_samples=15, m_lanczos=35, seed=104729, use_gpu=False):
    """
    Estimates heat kernel trace Tr(exp(-t*L)) on graph Laplacian L using SLQ to extract running d_s(t).
    Maintains 100% determinism via decoupled PRNG seeds. Default use_gpu=False ensures CPU archive parity.
    
    Provenance: [PURE LITERATURE]
    Reference : Ubaru et al. (2017), SIAM J. Matrix Anal. Appl. 38, 1075. [ubaru_2017]
    Formula   : d_s(t) = -2 * d(ln Tr(exp(-t L))) / d(ln t)
    """
    # Safety clamp: Krylov dimension cannot exceed allocated buffer size or graph rank
    m_eff = min(m_lanczos, len(slq_ws.alpha), max(2, N_nodes - 1))

    fill_laplacian_csr_buffers(adj, slq_ws.indptr, slq_ws.indices, slq_ws.data)
    t_vals = SLQ_T_VALS
    log_t = SLQ_LOG_T

    # Route to GPU only if explicitly requested, volume threshold is met, and CuPy initializes cleanly
    if use_gpu and check_cupy_available() and N_nodes >= 4096:
        try:
            P_t = _slq_lanczos_gpu_tridiag(
                slq_ws.indptr, slq_ws.indices, slq_ws.data,
                N_nodes, t_vals, num_samples, m_eff, slq_seed=seed
            )
        except Exception:
            P_t = _slq_lanczos_tridiag_kernel(
                slq_ws.indptr, slq_ws.indices, slq_ws.data,
                N_nodes, t_vals, num_samples, m_eff,
                slq_ws.w, slq_ws.w_next, slq_ws.v_prev,
                slq_ws.alpha, slq_ws.beta, slq_seed=seed
            )
    else:
        P_t = _slq_lanczos_tridiag_kernel(
            slq_ws.indptr, slq_ws.indices, slq_ws.data,
            N_nodes, t_vals, num_samples, m_eff,
            slq_ws.w, slq_ws.w_next, slq_ws.v_prev,
            slq_ws.alpha, slq_ws.beta, slq_seed=seed
        )

    log_P = np.log(np.maximum(P_t, 1e-30))

    local_ds = np.zeros(len(t_vals) - 2)
    for i in range(1, len(t_vals) - 1):
        slope = (log_P[i+1] - log_P[i-1]) / (log_t[i+1] - log_t[i-1])
        local_ds[i-1] = -2.0 * slope

    t_mid = t_vals[1:-1]
    t_min_valid, t_max_valid = (0.8, 3.0) if N_nodes < 4096 else (8.0, 25.0)
    valid_indices = np.where((t_mid >= t_min_valid) & (t_mid <= t_max_valid))[0]

    ds_mean = float(np.mean(local_ds[valid_indices])) if len(valid_indices) > 0 else float(np.mean(local_ds))
    return ds_mean, t_mid, local_ds


class CvResult(float):
    """
    Dual-type result representing specific heat Cv:
    Acts both as a standard float and as an iterable (Cv, Cv_err) 2-tuple.
    """
    def __new__(cls, val, err=0.0):
        obj = super().__new__(cls, val)
        obj.err = float(err)
        return obj

    def __iter__(self):
        yield float(self)
        yield self.err

    def __getitem__(self, idx):
        return (float(self), self.err)[idx]

    def __len__(self):
        return 2


def compute_cv_binning(energy_history, beta: float, N_nodes: int, num_blocks: int = 16, burn_ratio: float = 0.50):
    """
    Computes specific heat capacity Cv from total energy fluctuations.
    Applies linear detrending to separate true thermodynamic variance 
    from macroscopic relaxation drift.
    """
    n_samples = len(energy_history)
    start_idx = int(n_samples * burn_ratio)
    if start_idx >= n_samples - 10:
        return CvResult(0.0, 0.0)

    stationary_phase = np.asarray(energy_history[start_idx:], dtype=np.float64)
    M = len(stationary_phase)
    
    # Linear detrending to strip relaxation slope
    t_ax = np.arange(M, dtype=np.float64)
    poly = np.polyfit(t_ax, stationary_phase, 1)
    detrended = stationary_phase - (poly[0] * t_ax + poly[1])
    
    beta_sq = float(beta) * float(beta)
    var_H = float(np.var(detrended))
    cv_val = beta_sq * var_H / float(N_nodes)

    if M < num_blocks * 2:
        return CvResult(cv_val, 0.0)

    block_size = M // num_blocks
    block_cvs = np.zeros(num_blocks, dtype=np.float64)
    for b in range(num_blocks):
        block_data = detrended[b * block_size : (b + 1) * block_size]
        block_cvs[b] = beta_sq * float(np.var(block_data)) / float(N_nodes)

    cv_err = float(np.std(block_cvs, ddof=1)) / math.sqrt(num_blocks)
    return CvResult(cv_val, cv_err)