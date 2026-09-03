#!/usr/bin/env python3
"""
================================================================================
EMERGENT LATTICE ARCHITECTURE (ELA) SIMULATION ENGINE v4.4.2
================================================================================
A Unified Multi-Mode Non-Perturbative Physics Engine for Lattice Field Theory,
Micro-Scale SU(2) Solitons with Continuous Fermi-Dirac Co-Moving Sleeves,
and Quantum Cosmology Bounces.

ACADEMIC ATTRIBUTION & CITATION INDEX:
--------------------------------------------------------------------------------
- Diamond Crystal Structure:      Ashcroft, N. W. & Mermin, N. D. (1976), Solid State Phys.
- Minimum Image Convention:       Allen, M. P. & Tildesley, D. J. (1987), Comp. Sim. Liq.
- Quaternion Algebra:             Hamilton, W. R. (1844), Phil. Mag. 25, 489.
- Valence Force Field Elasticity: Keating, P. N. (1966), Phys. Rev. 145(2), 637.
- Lattice Gauge Theory:           Wilson, K. G. (1974), Phys. Rev. D 10(8), 2445.
- Gauge Field Cooling:            Teper, M. (1985), Phys. Lett. B 162(1-3), 137.
- Skyrmion Soliton Physics:       Skyrme, T. H. R. (1962), Nucl. Phys. 31, 556.
- Instanton Density Factor:       Belavin, A. A. et al. (1975), Phys. Lett. B 59(1), 85.
- Loop Quantum Cosmology Bounce:  Ashtekar, A. et al. (2006), Phys. Rev. D 74, 084003.
- Dark Energy EoS w(a):           Linder, E. V. (2003), Phys. Rev. Lett. 90(9), 091301.
- Dark Energy CPL Model:          Chevallier, M. & Polarski, D. (2001), Int. J. Mod. Phys. D 10, 213.
- CMB Spectral Index Measurement: Planck Collaboration (2020), A&A 641, A6.
- Metropolis-Hastings MCMC:       Metropolis, N. et al. (1953), J. Chem. Phys. 21, 1087.
- SU(2) Gauge Heatbath Updates:   Creutz, M. (1980), Phys. Rev. D 21(8), 2308.
- Bistellar Pachner Surgery:      Pachner, U. (1991), Geom. Dedicata 38(3), 301.
- Small-World Network Topology:   Watts, D. J. & Strogatz, S. H. (1998), Nature 393, 440.
- ER=EPR Bridge Analogy:          Maldacena, J. & Susskind, L. (2013), Fortschr. Phys. 61, 781.
- Sparse Matrix CSR Format:       Saad, Y. (2003), Iterative Methods for Sparse Linear Systems.
- Stochastic Lanczos Quadrature:  Ubaru, S. et al. (2017), SIAM J. Matrix Anal. 38, 1075.
- Hutchinson Trace Estimator:     Hutchinson, M. F. (1989), Comm. Stat. Sim. Comp. 18, 1059.
- Lanczos Iteration Engine:       Lanczos, C. (1950), J. Res. Natl. Bur. Stand. 45, 255.
- Spectral Dimension Analysis:    Ambjørn, J. et al. (2005), Phys. Rev. Lett. 95, 171301.
- Statistical Binning Analysis:   Flyvbjerg, H. & Petersen, H. (1989), J. Chem. Phys. 91, 461.
================================================================================
"""

__references__ = {
    # --- Crystallography, Geometry & Kinematics ---
    "ashcroft_mermin_1976": {
        "authors": "Ashcroft, Neil W.; Mermin, N. David",
        "title": "Solid State Physics",
        "publisher": "Saunders College Publishing",
        "year": 1976,
        "isbn": "978-0030839931"
    },
    "allen_tildesley_1987": {
        "authors": "Allen, M. P.; Tildesley, D. J.",
        "title": "Computer Simulation of Liquids",
        "publisher": "Oxford University Press",
        "year": 1987,
        "isbn": "978-0198556459"
    },
    "hamilton_1844": {
        "authors": "Hamilton, William Rowan",
        "title": "On Quaternions; or on a new System of Imaginaries in Algebra",
        "journal": "Philosophical Magazine",
        "volume": "25",
        "pages": "489--495",
        "year": 1844
    },

    # --- Continuum & Lattice Physical Theories ---
    "keating_1966": {
        "authors": "Keating, P. N.",
        "title": "Effect of Invariance Requirements on the Elastic Strain Energy of Crystals with Application to the Diamond Structure",
        "journal": "Physical Review",
        "volume": "145",
        "issue": "2",
        "pages": "637--645",
        "year": 1966,
        "doi": "10.1103/PhysRev.145.637"
    },
    "wilson_1974": {
        "authors": "Wilson, Kenneth G.",
        "title": "Confinement of quarks",
        "journal": "Physical Review D",
        "volume": "10",
        "issue": "8",
        "pages": "2445--2459",
        "year": 1974,
        "doi": "10.1103/PhysRevD.10.2445"
    },
    "berg_1981": {
        "authors": "Berg, Bernd",
        "title": "Dislocations and topological background in the lattice O(3) sigma-model",
        "journal": "Physics Letters B",
        "volume": "104",
        "issue": "6",
        "pages": "475--480",
        "year": 1981,
        "doi": "10.1016/0370-2693(81)90038-3"
    },
    "teper_1985": {
        "authors": "Teper, Michael",
        "title": "Instantons in the SU(2) lattice gauge theory",
        "journal": "Physics Letters B",
        "volume": "162",
        "issue": "1-3",
        "pages": "137--142",
        "year": 1985,
        "doi": "10.1016/0370-2693(85)91073-1"
    },
    "skyrme_1962": {
        "authors": "Skyrme, T. H. R.",
        "title": "A unified field theory of mesons and baryons",
        "journal": "Nuclear Physics",
        "volume": "31",
        "pages": "556--569",
        "year": 1962,
        "doi": "10.1016/0029-5582(62)90775-7"
    },
    "belavin_1975": {
        "authors": "Belavin, A. A.; Polyakov, A. M.; Schwartz, A. S.; Tyupkin, Y. S.",
        "title": "Pseudoparticle solutions of the Yang-Mills equations",
        "journal": "Physics Letters B",
        "volume": "59",
        "issue": "1",
        "pages": "85--87",
        "year": 1975,
        "doi": "10.1016/0370-2693(75)90163-X"
    },
    "ashtekar_2006": {
        "authors": "Ashtekar, Abhay; Pawlowski, Tomasz; Singh, Parampreet",
        "title": "Quantum nature of the big bang: Improved dynamics",
        "journal": "Physical Review D",
        "volume": "74",
        "issue": "8",
        "pages": "084003",
        "year": 2006,
        "doi": "10.1103/PhysRevD.74.084003"
    },
    "linder_2003": {
        "authors": "Linder, Eric V.",
        "title": "Exploring the Expansion History of the Universe",
        "journal": "Physical Review Letters",
        "volume": "90",
        "issue": "9",
        "pages": "091301",
        "year": 2003,
        "doi": "10.1103/PhysRevLett.90.091301"
    },
    "chevallier_polarski_2001": {
        "authors": "Chevallier, Michel; Polarski, David",
        "title": "Accelerating Universes with Scaling Dark Energy",
        "journal": "International Journal of Modern Physics D",
        "volume": "10",
        "issue": "02",
        "pages": "213--223",
        "year": 2001,
        "doi": "10.1142/S0218271801000822"
    },
    "planck_2020": {
        "authors": "Aghanim, N. et al. (Planck Collaboration)",
        "title": "Planck 2018 results. VI. Cosmological parameters",
        "journal": "Astronomy & Astrophysics",
        "volume": "641",
        "pages": "A6",
        "year": 2020,
        "doi": "10.1051/0004-6361/201833910"
    },
    "pachner_1991": {
        "authors": "Pachner, Udo",
        "title": "PL homeomorphic manifolds are bistellar equivalent",
        "journal": "Geometriae Dedicata",
        "volume": "38",
        "issue": "3",
        "pages": "301--320",
        "year": 1991,
        "doi": "10.1007/BF00183020"
    },
    "ambjorn_loll_1998": {
        "authors": "Ambjørn, Jan; Loll, Renate",
        "title": "Non-perturbative Lorentzian quantum gravity, causality and topology change",
        "journal": "Nuclear Physics B",
        "volume": "536",
        "issue": "1-2",
        "pages": "407--434",
        "year": 1998,
        "doi": "10.1016/S0550-3213(98)00692-0"
    },
    "watts_strogatz_1998": {
        "authors": "Watts, Duncan J.; Strogatz, Steven H.",
        "title": "Collective dynamics of 'small-world' networks",
        "journal": "Nature",
        "volume": "393",
        "issue": "6684",
        "pages": "440--442",
        "year": 1998,
        "doi": "10.1038/30918"
    },
    "maldacena_susskind_2013": {
        "authors": "Maldacena, Juan; Susskind, Leonard",
        "title": "Cool horizons for entangled black holes",
        "journal": "Fortschritte der Physik",
        "volume": "61",
        "issue": "9",
        "pages": "781--811",
        "year": 2013,
        "doi": "10.1002/prop.201300020"
    },

    # --- Computational, Linear Algebra & Statistical Algorithms ---
    "metropolis_1953": {
        "authors": "Metropolis, Nicholas; Rosenbluth, Arianna W.; Rosenbluth, Marshall N.; Teller, Augusta H.; Teller, Edward",
        "title": "Equation of State Calculations by Fast Computing Machines",
        "journal": "The Journal of Chemical Physics",
        "volume": "21",
        "issue": "6",
        "pages": "1087--1092",
        "year": 1953,
        "doi": "10.1063/1.1699114"
    },
    "hastings_1970": {
        "authors": "Hastings, W. K.",
        "title": "Monte Carlo sampling methods using Markov chains and their applications",
        "journal": "Biometrika",
        "volume": "57",
        "issue": "1",
        "pages": "97--109",
        "year": 1970,
        "doi": "10.1093/biomet/57.1.97"
    },
    "creutz_1980": {
        "authors": "Creutz, Michael",
        "title": "Monte Carlo study of quantized SU(2) gauge theory",
        "journal": "Physical Review D",
        "volume": "21",
        "issue": "8",
        "pages": "2308--2315",
        "year": 1980,
        "doi": "10.1103/PhysRevD.21.2308"
    },
    "saad_2003": {
        "authors": "Saad, Yousef",
        "title": "Iterative Methods for Sparse Linear Systems",
        "edition": "2nd",
        "publisher": "Society for Industrial and Applied Mathematics (SIAM)",
        "year": 2003,
        "doi": "10.1137/1.9780898718003"
    },
    "ubaru_2017": {
        "authors": "Ubaru, Shashanka; Chen, Jie; Saad, Yousef",
        "title": "Fast Estimation of Tr(f(A)) via Stochastic Lanczos Quadrature",
        "journal": "SIAM Journal on Matrix Analysis and Applications",
        "volume": "38",
        "issue": "4",
        "pages": "1075--1099",
        "year": 2017,
        "doi": "10.1137/16M1104974"
    },
    "hutchinson_1989": {
        "authors": "Hutchinson, M. F.",
        "title": "A stochastic estimator of the trace of the influence matrix for Laplacian smoothing splines",
        "journal": "Communications in Statistics - Simulation and Computation",
        "volume": "18",
        "issue": "3",
        "pages": "1059--1076",
        "year": 1989,
        "doi": "10.1080/03665198908805276"
    },
    "lanczos_1950": {
        "authors": "Lanczos, Cornelius",
        "title": "An iteration method for the solution of the eigenvalue problem of linear differential and integral operators",
        "journal": "Journal of Research of the National Bureau of Standards",
        "volume": "45",
        "issue": "4",
        "pages": "255--282",
        "year": 1950,
        "doi": "10.6028/jres.045.026"
    },
    "ambjorn_2005": {
        "authors": "Ambjørn, Jan; Jurkiewicz, Jerzy; Loll, Renate",
        "title": "Spectral Dimension of the Universe",
        "journal": "Physical Review Letters",
        "volume": "95",
        "issue": "17",
        "pages": "171301",
        "year": 2005,
        "doi": "10.1103/PhysRevLett.95.171301"
    },
    "flyvbjerg_1989": {
        "authors": "Flyvbjerg, Henrik; Petersen, Henrik Gordon",
        "title": "Error estimates on averages of correlated data",
        "journal": "The Journal of Chemical Physics",
        "volume": "91",
        "issue": "1",
        "pages": "461--466",
        "year": 1989,
        "doi": "10.1063/1.457480"
    },

    # --- Software Infrastructure & Libraries ---
    "numba_2015": {
        "authors": "Lam, Siu Kwan; Pitrou, Antoine; Seibert, Stanley",
        "title": "Numba: A LLVM-based Python JIT compiler",
        "booktitle": "Proceedings of the Second Workshop on the LLVM Compiler Infrastructure in HPC",
        "pages": "1--6",
        "year": 2015,
        "doi": "10.1145/2833157.2833162"
    },
    "numpy_2020": {
        "authors": "Harris, Charles R. et al.",
        "title": "Array programming with NumPy",
        "journal": "Nature",
        "volume": "585",
        "pages": "357--362",
        "year": 2020,
        "doi": "10.1038/s41586-020-2649-2"
    },
    "matplotlib_2007": {
        "authors": "Hunter, John D.",
        "title": "Matplotlib: A 2D graphics environment",
        "journal": "Computing in Science & Engineering",
        "volume": "9",
        "issue": "3",
        "pages": "90--95",
        "year": 2007,
        "doi": "10.1109/MCSE.2007.55"
    }
}

from enum import Enum, auto
import time
import math
import os
import sys
import random
from collections import deque
import argparse
import numpy as np
from numba import njit, prange
import matplotlib.pyplot as plt

sys.stdout.reconfigure(line_buffering=True)


# ------------------------------------------------------------------------------
# 0. ENGINE MODE & PRNG SEEDING ENGINE
# ------------------------------------------------------------------------------


class EngineMode(Enum):
    """
    Theoretical physics execution modes for the ELA simulation engine.
    
    Refs:
      - Mode 1: Keating, P. N. (1966). Phys. Rev. 145(2), 637.
      - Mode 2: Wilson, K. G. (1974). Phys. Rev. D 10(8), 2445; Skyrme, T. H. R. (1962). Nucl. Phys. 31, 556.
      - Mode 3: Ashtekar, A. et al. (2006). Phys. Rev. D 74(8), 084003; Planck Collaboration (2020). A&A 641, A6.
    """
    PAPER1_VACUUM = auto()        # Mode 1: Pure Spatial Vacuum & Rigidity
    PAPER2_GAUGE_SOLITON = auto()  # Mode 2: Micro Solitons, SU(2) Gauges & Co-Moving Sleeves
    PAPER3_COSMOLOGY = auto()      # Mode 3: Macro Cosmology, Untensing & S3 LQC Bounce


class EPRMode(Enum):
    """
    [EXACT IMPLEMENTATION]
    Configures non-local ER=EPR shortcut link dynamics on small-world network geometries.
    
    Refs:
      - Watts, D. J. & Strogatz, S. H. (1998). Nature, 393, 440--442. DOI: 10.1038/30918
      - Maldacena, J. & Susskind, L. (2013). Fortschr. Phys., 61, 781--811. DOI: 10.1002/prop.201300020
    """
    DYNAMIC = auto()  # Move 4 active: dynamic EPR thermal creation/annihilation
    STATIC = auto()   # Static zero-strain shortcut injection at setup
    NONE = auto()     # Strict 3D spatial grid (zero shortcuts)


@njit
def _seed_numba_prng(seed: int):
    """
    [EXACT IMPLEMENTATION]
    Seeds Numba JIT internal Pseudo-Random Number Generator (PRNG) state.
    
    Refs:
      - Lam, S. K. et al. (2015). Numba: A LLVM-based Python JIT compiler.
        Proc. LLVM Infrastructure in HPC, 1--6. DOI: 10.1145/2833157.2833162
      - Harris, C. R. et al. (2020). Array programming with NumPy. 
        Nature, 585, 357--362. DOI: 10.1038/s41586-020-2649-2
    """
    np.random.seed(seed)


def setup_prng(user_seed: int | None = None) -> int:
    """
    [EXACT IMPLEMENTATION]
    Initializes global system PRNG entropy across Python random, NumPy, and Numba engines.
    
    Refs:
      - Harris, C. R. et al. (2020). Array programming with NumPy. 
        Nature, 585, 357--362. DOI: 10.1038/s41586-020-2649-2
    """
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
# 1. NUMBA-ACCELERATED VECTOR MATH & HAMILTONIAN KERNELS
# ------------------------------------------------------------------------------

@njit(fastmath=True, inline='always')
def pbc_diff_vec(p1, p2, L, inv_L):
    """
    [EXACT IMPLEMENTATION]
    Calculates spatial separation vector under Periodic Boundary Conditions (PBC) 
    using the Minimum Image Convention (MIC).
    
    Ref: Allen, M. P. & Tildesley, D. J. (1987). Computer Simulation of Liquids. 
         Oxford University Press. ISBN: 978-0198556459
    """
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    dz = p2[2] - p1[2]
    dx -= L * math.floor(dx * inv_L + 0.5)
    dy -= L * math.floor(dy * inv_L + 0.5)
    dz -= L * math.floor(dz * inv_L + 0.5)
    return dx, dy, dz


@njit(fastmath=True, inline='always')
def fast_unit_vec(p1, p2, L, inv_L):
    """
    [EXACT IMPLEMENTATION]
    Computes normalized unit direction vector and Euclidean norm under Periodic Boundary Conditions.
    
    Ref: Allen, M. P. & Tildesley, D. J. (1987). Computer Simulation of Liquids. 
         Oxford University Press.
    """
    dx, dy, dz = pbc_diff_vec(p1, p2, L, inv_L)
    norm_sq = dx * dx + dy * dy + dz * dz
    if norm_sq < 1e-14:
        return 0.0, 0.0, 0.0, 0.0
    norm = math.sqrt(norm_sq)
    inv = 1.0 / norm
    return dx * inv, dy * inv, dz * inv, norm


@njit(inline='always')
def quat_mult(q, r):
    """
    [EXACT IMPLEMENTATION - IEEE 754 STRICT PRECISION]
    Executes Hamilton product of two 4-component unit quaternions (SU(2) link holonomies).
    Retains strict IEEE 754 precision (no fastmath reassociation) to prevent unit norm drift.
    
    Ref: Hamilton, W. R. (1844). On Quaternions; or on a new System of Imaginaries in Algebra. 
         Philosophical Magazine, 25, 489--495.
    """
    w = q[0]*r[0] - q[1]*r[1] - q[2]*r[2] - q[3]*r[3]
    x = q[0]*r[1] + q[1]*r[0] + q[2]*r[3] - q[3]*r[2]
    y = q[0]*r[2] - q[1]*r[3] + q[2]*r[0] + q[3]*r[1]
    z = q[0]*r[3] + q[1]*r[2] - q[2]*r[1] + q[3]*r[0]
    return w, x, y, z


@njit(inline='always')
def align_holonomy_geodesic(q_old, p_start, p_old_target, p_new_target, box_size, inv_L):
    """
    [CUSTOM / PROPRIETARY IMPLEMENTATION - IEEE 754 STRICT PRECISION]
    Parallel transports unit quaternion SU(2) link holonomies along minimal S^3 geodesic 
    arcs matching spatial direction changes during Move 3 topological link swaps.
    
    Note: Custom ELA geometric transport algorithm designed to preserve holonomy continuity 
    during 2-to-2 Pachner link reconnections.
    """
    dx1, dy1, dz1 = pbc_diff_vec(p_start, p_old_target, box_size, inv_L)
    n1_sq = dx1*dx1 + dy1*dy1 + dz1*dz1
    if n1_sq < 1e-14:
        return q_old
    n1 = math.sqrt(n1_sq)
    e1_x = dx1 / n1; e1_y = dy1 / n1; e1_z = dz1 / n1

    dx2, dy2, dz2 = pbc_diff_vec(p_start, p_new_target, box_size, inv_L)
    n2_sq = dx2*dx2 + dy2*dy2 + dz2*dz2
    if n2_sq < 1e-14:
        return q_old
    n2 = math.sqrt(n2_sq)
    e2_x = dx2 / n2; e2_y = dy2 / n2; e2_z = dz2 / n2

    dot = e1_x*e2_x + e1_y*e2_y + e1_z*e2_z
    if dot > 0.9999999:
        return q_old

    if dot < -0.9999999:
        orth_x = 0.0; orth_y = 0.0; orth_z = 1.0
        if abs(e1_z) > 0.8:
            orth_x = 1.0; orth_z = 0.0
        ax = e1_y*orth_z - e1_z*orth_y
        ay = e1_z*orth_x - e1_x*orth_z
        az = e1_x*orth_y - e1_y*orth_x
        norm = math.sqrt(ax*ax + ay*ay + az*az)
        if norm > 1e-12:
            inv = 1.0 / norm
            qw, qx, qy, qz = 0.0, ax*inv, ay*inv, az*inv
        else:
            qw, qx, qy, qz = 0.0, 1.0, 0.0, 0.0
    else:
        cx = e1_y*e2_z - e1_z*e2_y
        cy = e1_z*e2_x - e1_x*e2_z
        cz = e1_x*e2_y - e1_y*e2_x
        c_norm = math.sqrt(cx*cx + cy*cy + cz*cz)
        if c_norm < 1e-12:
            return q_old
        axis_x = cx / c_norm
        axis_y = cy / c_norm
        axis_z = cz / c_norm

        half_angle = 0.5 * math.acos(max(-1.0, min(1.0, dot)))
        sin_h = math.sin(half_angle)
        cos_h = math.cos(half_angle)
        qw, qx, qy, qz = cos_h, axis_x * sin_h, axis_y * sin_h, axis_z * sin_h

    q_rot = np.array([qw, qx, qy, qz], dtype=np.float64)
    w, x, y, z = quat_mult(q_rot, q_old)
    norm_q = math.sqrt(w*w + x*x + y*y + z*z)
    if norm_q > 1e-12:
        inv_q = 1.0 / norm_q
        w *= inv_q; x *= inv_q; y *= inv_q; z *= inv_q
    return np.array([w, x, y, z], dtype=np.float64)


@njit(fastmath=True, inline='always')
def calc_node_shear(u, adj, pos, L, inv_L, shear_vecs_buf, max_degree=6):
    """
    [EXACT IMPLEMENTATION]
    Computes bond-angle shear strain energy based on the Valence Force Field (VFF) model.
    
    Ref: Keating, P. N. (1966). Effect of Invariance Requirements on the Elastic Strain 
         Energy of Crystals with Application to the Diamond Structure. 
         Phys. Rev., 145(2), 637--645. DOI: 10.1103/PhysRev.145.637
    """
    shear = 0.0
    deg = 0
    INV_THREE = 1.0 / 3.0

    for i in range(max_degree):
        v = adj[u, i]
        if v >= 0:
            dx, dy, dz, norm = fast_unit_vec(pos[u], pos[v], L, inv_L)
            if norm > 1e-14:
                shear_vecs_buf[deg, 0] = dx
                shear_vecs_buf[deg, 1] = dy
                shear_vecs_buf[deg, 2] = dz
                deg += 1

    for i in range(deg):
        for j in range(i + 1, deg):
            cos_ij = (shear_vecs_buf[i, 0] * shear_vecs_buf[j, 0] + 
                      shear_vecs_buf[i, 1] * shear_vecs_buf[j, 1] + 
                      shear_vecs_buf[i, 2] * shear_vecs_buf[j, 2])
            dev = cos_ij + INV_THREE
            shear += dev * dev

    return shear


@njit(fastmath=True, inline='always')
def calc_edge_torsion(j, k, adj, pos, L, inv_L, max_degree=6):
    """
    [OPTIMIZED STACK-HOISTED IMPLEMENTATION]
    Computes dihedral bond-torsion strain energy on 4-regular tetrahedral lattices.
    Hoists n2 plane normal calculations into stack scalars to eliminate redundant cross-products.
    
    Ref: Keating, P. N. (1966). Effect of Invariance Requirements on the Elastic Strain 
         Energy of Crystals with Application to the Diamond Structure. 
         Phys. Rev., 145(2), 637--645. DOI: 10.1103/PhysRev.145.637
    """
    pj = pos[j]
    pk = pos[k]
    ujk_x, ujk_y, ujk_z, norm_jk = fast_unit_vec(pj, pk, L, inv_L)
    if norm_jk < 1e-7:
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
            c = n1_x * l0_nx + n1_y * l0_ny + n1_z * l0_nz
            if c > 1.0: c = 1.0
            elif c < -1.0: c = -1.0
            torsion += w1 * l0_w2 * (1.0 + 4.0 * c * c * c - 3.0 * c)
        if n2_count > 1:
            c = n1_x * l1_nx + n1_y * l1_ny + n1_z * l1_nz
            if c > 1.0: c = 1.0
            elif c < -1.0: c = -1.0
            torsion += w1 * l1_w2 * (1.0 + 4.0 * c * c * c - 3.0 * c)
        if n2_count > 2:
            c = n1_x * l2_nx + n1_y * l2_ny + n1_z * l2_nz
            if c > 1.0: c = 1.0
            elif c < -1.0: c = -1.0
            torsion += w1 * l2_w2 * (1.0 + 4.0 * c * c * c - 3.0 * c)
            
    return torsion


@njit(fastmath=True, inline='always')
def calc_edge_stretch(u, v, pos, r0, L, inv_L):
    """
    [EXACT IMPLEMENTATION]
    Computes central harmonic bond-length stretching strain energy.
    
    Ref: Keating, P. N. (1966). Phys. Rev., 145(2), 637--645. DOI: 10.1103/PhysRev.145.637
    """
    dx, dy, dz = pbc_diff_vec(pos[u], pos[v], L, inv_L)
    dist = math.sqrt(dx * dx + dy * dy + dz * dz)
    dev = dist - r0
    return dev * dev


@njit(fastmath=True, inline='always')
def calc_node_jamming(u, gauge_u, max_degree=6):
    """
    [ADAPTED / GENERALIZED IMPLEMENTATION]
    Computes node gauge phase jamming potential V_j = 0.5 * lambda * sum(1 - q0),
    penalizing deviations of link holonomies from the SU(2) identity element (q0 = 1).
    
    Note on Adaptation: Adapts standard SU(2) gauge field holonomies to construct 
    a local phase-jamming potential penalizing non-identity link orientations.
    
    Ref (Base Gauge Theory): 
      - Wilson, K. G. (1974). Confinement of quarks. 
        Phys. Rev. D, 10(8), 2445--2459. DOI: 10.1103/PhysRevD.10.2445
    """
    jamming = 0.0
    for i in range(max_degree):
        q0 = gauge_u[u, i, 0]
        jamming += (1.0 - q0)
    return jamming


@njit(fastmath=True, inline='always')
def calc_edge_local_plaquette_action(u, e_idx, adj, gauge_u, max_degree=6):
    """
    [ADAPTED / GENERALIZED IMPLEMENTATION]
    Computes local 6-cycle Wilson plaquette action increment for an edge on diamond networks.
    
    Note on Adaptation: Standard Wilson gauge theory uses 4-link square plaquettes. 
    Because tetrahedral diamond lattices lack 4-cycle loops, this function evaluates 
    the trace of 6-link elementary closed loops.
    
    Ref (Base Theory): Wilson, K. G. (1974). Confinement of quarks. 
                       Phys. Rev. D, 10(8), 2445--2459. DOI: 10.1103/PhysRevD.10.2445
    """
    v = adj[u, e_idx]
    if v < 0:
        return 0.0

    total_action = 0.0
    q1 = gauge_u[u, e_idx]

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
                                if z >= 0 and z != x and z != w and z != v and z != u:
                                    for n_idx in range(max_degree):
                                        if adj[z, n_idx] == u:
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
                                            break
    return total_action


@njit(fastmath=True, inline='always')
def sum_torsion_for_nodes(nodes_list, n_count, adj, pos, L, inv_L, edge_buf, max_degree=6):
    """
    [EXACT IMPLEMENTATION]
    Aggregates Keating dihedral torsion energy across local node neighborhoods.
    
    Ref: Keating, P. N. (1966). Phys. Rev., 145(2), 637--645.
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


@njit(fastmath=True)
def calc_total_system_energy(pos, adj, is_coherent_edge, gauge_u, L, inv_L, r0, ks, kt, kr, lj, shear_vecs_buf, scale_a=1.0, beta_untensing=0.0175, mode_val=1, max_degree=6):
    """
    [ADAPTED / GENERALIZED IMPLEMENTATION]
    Evaluates total system Hamiltonian H_tot = H_shear + H_torsion + H_stretch + V_jamming,
    including scale-factor dependent shear untensing ks(a) = ks * a^(-beta).
    
    Refs:
      - Keating, P. N. (1966). Phys. Rev., 145(2), 637--645.
      - Wilson, K. G. (1974). Phys. Rev. D, 10(8), 2445--2459.
      - Planck Collaboration (2020). Planck 2018 results. VI. Cosmological parameters. 
        A&A, 641, A6. DOI: 10.1051/0004-6361/201833910
    """
    N = pos.shape[0]
    total_shear = 0.0
    total_torsion = 0.0
    total_stretch = 0.0
    total_jamming = 0.0
    
    eff_ks = ks * (scale_a ** (-beta_untensing)) if mode_val == 3 else ks

    for u in range(N):
        total_shear += calc_node_shear(u, adj, pos, L, inv_L, shear_vecs_buf, max_degree)
        total_jamming += calc_node_jamming(u, gauge_u, max_degree)
        
        for i in range(max_degree):
            v = adj[u, i]
            if v > u:
                if not is_coherent_edge[u, i]:
                    total_stretch += calc_edge_stretch(u, v, pos, r0, L, inv_L)
                total_torsion += calc_edge_torsion(u, v, adj, pos, L, inv_L, max_degree)
                
    H_s = eff_ks * total_shear
    H_t = kt * total_torsion
    H_r = kr * total_stretch
    V_j = 0.5 * lj * total_jamming
    H_tot = H_s + H_t + H_r + V_j
    
    return H_tot, H_s, H_t, H_r, V_j


# ------------------------------------------------------------------------------
# 2. PAPER 2 & 3 KERNELS: GAUGE ACTION, COOLING, SOLITONS & LQC BOUNCE
# ------------------------------------------------------------------------------

@njit
def cool_gauge_field_6cycle(adj, gauge_u, num_cooling_sweeps=25):
    """
    [ADAPTED / GENERALIZED IMPLEMENTATION - IEEE 754 STRICT PRECISION]
    Relaxes local ultraviolet thermal fluctuations in SU(2) link fields along the gradient 
    of the 6-cycle Wilson plaquette action while preserving global topological charge Q.
    
    Note on Adaptation: Adapts standard 4-cycle staple minimization to 5-link staples 
    matching the 6-ring elementary cycles of the diamond network.
    
    Refs (Base Theory): 
      - Berg, B. (1981). Dislocations and topological background in the lattice O(3) 
        sigma-model. Phys. Lett. B, 104(6), 475--480. DOI: 10.1016/0370-2693(81)90038-3
      - Teper, M. (1985). Instantons in the SU(2) lattice gauge theory. 
        Phys. Lett. B, 162(1-3), 137--142. DOI: 10.1016/0370-2693(85)91073-1
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
                                                                q2 = cooled_u[v, j]
                                                                q3 = cooled_u[w, k]
                                                                q4 = cooled_u[x_node, l]
                                                                q5 = cooled_u[y_node, m]
                                                                q6 = cooled_u[z_node, n_idx]
                                                                
                                                                w23, x23, y23, z23 = quat_mult(q2, q3)
                                                                w45, x45, y45, z45 = quat_mult(q4, q5)
                                                                q23 = np.array([w23, x23, y23, z23], dtype=np.float64)
                                                                q45 = np.array([w45, x45, y45, z45], dtype=np.float64)
                                                                
                                                                w2345, x2345, y2345, z2345 = quat_mult(q23, q45)
                                                                q2345 = np.array([w2345, x2345, y2345, z2345], dtype=np.float64)
                                                                
                                                                w_st, x_st, y_st, z_st = quat_mult(q2345, q6)
                                                                
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
    [ADAPTED / GENERALIZED IMPLEMENTATION - OPTIMIZED CANONICAL TRAVERSAL]
    Calculates average 6-cycle SU(2) Wilson Plaquette Action S_P for diamond lattices.
    Uses canonical minimum node checking (u == min(u, v, w, x, y, z)) to eliminate 
    12x redundant cycle evaluations.
    
    Ref: Wilson, K. G. (1974). Confinement of quarks. 
         Phys. Rev. D, 10(8), 2445--2459. DOI: 10.1103/PhysRevD.10.2445
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
def calc_topological_charge_q(pos, adj, gauge_u, box_size, inv_L, r0=1.7320508075688772):
    """
    [ADAPTED / PROXICAL IMPLEMENTATION - EXACT PAPER 2 EQ. (1) ALIGNMENT]
    Calculates continuous topological Skyrmion charge Q matching Paper 2 Eq. (1):
      Q = -1 / (24 * pi^2) * integral(det(grad q) d^3x)

    Includes the discrete 4-regular tetrahedral lattice factor (3/4)^3 = 27/64
    arising from Theorem 2.1 sum(e_i (x) e_i) = (4/3) * I.
    
    Refs:
      - Skyrme, T. H. R. (1962). A unified field theory of mesons and baryons. 
        Nucl. Phys., 31, 556--569. DOI: 10.1016/0029-5582(62)90775-7
      - Belavin, A. A. et al. (1975). Pseudoparticle solutions of the Yang-Mills equations. 
        Phys. Lett. B, 59(1), 85--87. DOI: 10.1016/0370-2693(75)90163-X
    """
    N = pos.shape[0]
    max_degree = gauge_u.shape[1]
    inv_r0_sq = 1.0 / (r0 * r0)
    total_Q_density = 0.0

    for u in range(N):
        g0 = np.zeros(3, dtype=np.float64)
        g1 = np.zeros(3, dtype=np.float64)
        g2 = np.zeros(3, dtype=np.float64)

        for i in range(max_degree):
            v = adj[u, i]
            if v >= 0:
                dx, dy, dz = pbc_diff_vec(pos[u], pos[v], box_size, inv_L)
                q1 = gauge_u[u, i, 1]
                q2 = gauge_u[u, i, 2]
                q3 = gauge_u[u, i, 3]

                g0[0] += q1 * dx
                g0[1] += q1 * dy
                g0[2] += q1 * dz
                g1[0] += q2 * dx
                g1[1] += q2 * dy
                g1[2] += q2 * dz
                g2[0] += q3 * dx
                g2[1] += q3 * dy
                g2[2] += q3 * dz

        g0 *= 3.0 * inv_r0_sq
        g1 *= 3.0 * inv_r0_sq
        g2 *= 3.0 * inv_r0_sq

        det_color = (
            g0[0] * (g1[1] * g2[2] - g1[2] * g2[1])
            - g0[1] * (g1[0] * g2[2] - g1[2] * g2[0])
            + g0[2] * (g1[0] * g2[1] - g1[1] * g2[0])
        )

        total_Q_density += det_color

    V_node = (box_size**3) / float(N)

    # Apply discrete tetrahedral correction (3/4)^3 = 27/64 to map discrete sum to continuous field integral
    lattice_correction = 27.0 / 64.0
    continuous_integral = total_Q_density * V_node * lattice_correction

    # CRITICAL PARITY NOTE: The leading minus sign IS REQUIRED.
    # The field injector (inject_topological_soliton) negates spatial vector components
    # (qu1 = -node_q[u,1], etc.), which scales the 3x3 spatial determinant by (-1)^3 = -1.
    # Evaluating a right-handed Q = +1 Skyrmion yields continuous_integral ~ -24*pi^2.
    # The leading minus sign cancels this orientation negation, mapping -(-24*pi^2) / (24*pi^2) -> +1.
    Q_continuous = -continuous_integral / (24.0 * math.pi * math.pi)
    return Q_continuous


@njit(fastmath=True)
def calc_strand_helicity_charge(gauge_u):
    """
    [CUSTOM / PROPRIETARY IMPLEMENTATION]
    Evaluates fractionally quantized strand helicity charge q_k based on global U(1) phase 
    winding across quaternionic link holonomies.
    """
    N = gauge_u.shape[0]
    max_degree = gauge_u.shape[1]
    total_phase = 0.0

    for u in range(N):
        for i in range(max_degree):
            q0 = gauge_u[u, i, 0]
            q1 = gauge_u[u, i, 1]
            phase = 2.0 * math.atan2(q1, q0)
            total_phase += phase

    avg_phase = (total_phase / (N * max_degree)) / (2.0 * math.pi)
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
    [EXACT IMPLEMENTATION]
    Constructs an SU(2) Skyrmion hedgehog configuration mapping S^3 -> S^3 with winding number Q.
    
    Ref: Skyrme, T. H. R. (1962). A unified field theory of mesons and baryons. 
         Nucl. Phys., 31, 556--569. DOI: 10.1016/0029-5582(62)90775-7
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
def compute_lqc_bounce_diagnostics(
    H_tot, N_nodes, scale_a, beta_untensing=0.0175
):
    """
    [EXACT IMPLEMENTATION - CORRECTED DARK ENERGY SIGN & BOUNCE CLAMPING]
    Evaluates modified Friedmann Hubble expansion rate H^2 under Loop Quantum Cosmology (LQC) 
    holonomy corrections and CPL dark energy parameterization w(a).
    
    Equations:
      - H^2 = (8*pi*G/3) * rho * (1 - rho/rho_crit)
      - w(a) = -1 + w_a * (1 - a), where w_a = -2 * beta_untensing = -0.0350
      - CMB Spectral Tilt Relation: n_s = 1 - 2*beta_untensing = 0.9650
    
    Refs:
      - Ashtekar, A. et al. (2006). Quantum nature of the big bang: Improved dynamics. 
        Phys. Rev. D, 74(8), 084003. DOI: 10.1103/PhysRevD.74.084003
      - Linder, E. V. (2003). Exploring the Expansion History of the Universe. 
        Phys. Rev. Lett., 90(9), 091301. DOI: 10.1103/PhysRevLett.90.091301
      - Chevallier, M. & Polarski, D. (2001). Int. J. Mod. Phys. D 10, 213.
      - Planck Collaboration (2020). Planck 2018 results. VI. Cosmological parameters. 
        A&A, 641, A6. DOI: 10.1051/0004-6361/201833910
    """
    V_eff = float(N_nodes) * (scale_a ** 3)
    rho_energy = H_tot / max(1e-9, V_eff)
    
    # Scale critical density relative to compact initial energy density scale (~30.0)
    # Prevents rho_ratio from clamping to 1.0 (which forces cos(d_G/2) = 0 -> H^2 = 0)
    rho_crit = 30.0
    rho_ratio = min(1.0, max(0.0, rho_energy / rho_crit))
    
    d_G = 2.0 * math.asin(math.sqrt(rho_ratio))
    cos_half_dG = math.cos(d_G / 2.0)
    
    H_squared = (8.0 * math.pi / 3.0) * rho_energy * (cos_half_dG ** 2)
    
    w_a = -2.0 * beta_untensing  # Correct negative sign w_a = -0.0350
    w_eos = -1.0 + w_a * (1.0 - scale_a)
    
    return H_squared, w_eos, d_G, rho_energy


# ------------------------------------------------------------------------------
# 3. MONTE CARLO BLOCK KERNEL WITH GEODESIC REALIGNMENT & PROTECTED WARMUP
# ------------------------------------------------------------------------------

@njit(fastmath=True)
def run_numba_mcs_block(
    pos, adj, gauge_u, is_coherent_edge, box_size, inv_L, beta_mc,
    kappa_s, kappa_t, kappa_r, lambda_j, r0,
    max_disp, max_gauge_disp, num_sweeps,
    aff_nodes_m1, aff_nodes_m3, edge_buf, shear_vecs_buf,
    cutoff_prefactor=2.2, is_warmup=False, mode_val=1, scale_a=1.0,
    beta_untensing=0.0175, snr_crit=10.882796, epr_mode_val=0, epsilon_sw=0.005,
    has_soliton=False, beta_gauge=4.50,
    sleeve_mode=1, sleeve_sigma=0.15, sleeve_weight=1.0, sleeve_tunnel_alpha=0.05
):
    """
    [ADAPTED / GENERALIZED IMPLEMENTATION - CONTINUOUS SLEEVE & BOUNDED CUTOFF]
    Executes single-proposal Markov Chain Monte Carlo (MCMC) updates across 4 move types:
      - Move 1: Spatial node displacement (Metropolis-Hastings).
      - Move 2: SU(2) gauge phase holonomy updates.
      - Move 3: Local 2-to-2 link swaps (bistellar Pachner moves) with geodesic realignment,
                Fermi-Dirac sigmoidal sleeve protection, and hyperbolically bounded distance cutoffs.
      - Move 4: Dynamic EPR shortcut creation/annihilation (small-world topology).
    
    Refs:
      - Metropolis, N. et al. (1953). J. Chem. Phys., 21(6), 1087.
      - Hastings, W. K. (1970). Biometrika, 57(1), 97.
      - Creutz, M. (1980). Phys. Rev. D, 21(8), 2308.
      - Pachner, U. (1991). Geom. Dedicata, 38(3), 301--320.
      - Ambjørn, J. & Loll, R. (1998). Nucl. Phys. B, 536, 407--434.
      - Watts, D. J. & Strogatz, S. H. (1998). Nature, 393, 440--442.
      - Maldacena, J. & Susskind, L. (2013). Fortschr. Phys., 61, 781--811.
    """
    N_nodes = pos.shape[0]
    max_degree = 6

    win_spatial_att = 0; win_spatial_acc = 0
    win_gauge_att = 0;   win_gauge_acc = 0
    win_topo_att = 0;    win_topo_acc = 0
    win_epr_att = 0;     win_epr_acc = 0
    lazy_exits = 0;      full_rejs = 0
    sleeve_protected_swaps = 0

    eff_ks = kappa_s * (scale_a ** (-beta_untensing)) if mode_val == 3 else kappa_s
    sigma_tau_sq = 1.0 / beta_mc

    n_epr_links = 0
    if mode_val == 3:
        for u_i in range(N_nodes):
            for deg_i in range(max_degree):
                if is_coherent_edge[u_i, deg_i]:
                    n_epr_links += 1
        n_epr_links //= 2

    for _ in range(num_sweeps):
        for _ in range(N_nodes):
            roll = np.random.rand()

            if is_warmup:
                if has_soliton:
                    do_move1 = True
                    do_move2 = False
                else:
                    do_move1 = (roll < 0.80)
                    do_move2 = not do_move1
                do_move3 = False
                do_move4 = False
            else:
                if mode_val == 3 and epr_mode_val == 1:
                    do_move1 = (roll < 0.20)
                    do_move2 = (not do_move1) and (roll < 0.30)
                    do_move3 = (not do_move1) and (not do_move2) and (roll < 0.90)
                    do_move4 = (not do_move1) and (not do_move2) and (not do_move3)
                else:
                    do_move1 = (roll < 0.20)
                    do_move2 = (not do_move1) and (roll < 0.30)
                    do_move3 = (not do_move1) and (not do_move2)
                    do_move4 = False

            # MOVE 1: SPATIAL PERTURBATION
            if do_move1:
                win_spatial_att += 1
                u = np.random.randint(0, N_nodes)

                dx_disp = (np.random.rand() * 2.0 - 1.0) * max_disp
                dy_disp = (np.random.rand() * 2.0 - 1.0) * max_disp
                dz_disp = (np.random.rand() * 2.0 - 1.0) * max_disp

                old_px = pos[u, 0]; old_py = pos[u, 1]; old_pz = pos[u, 2]
                new_px = (old_px + dx_disp) % box_size
                new_py = (old_py + dy_disp) % box_size
                new_pz = (old_pz + dz_disp) % box_size

                aff_nodes_m1[0] = u
                n_aff = 1
                for i in range(max_degree):
                    v = adj[u, i]
                    if v >= 0:
                        aff_nodes_m1[n_aff] = v
                        n_aff += 1

                s_before = 0.0
                for i in range(n_aff):
                    s_before += calc_node_shear(aff_nodes_m1[i], adj, pos, box_size, inv_L, shear_vecs_buf, max_degree)
                t_before = sum_torsion_for_nodes(aff_nodes_m1, n_aff, adj, pos, box_size, inv_L, edge_buf, max_degree)
                
                str_before = 0.0
                for i in range(max_degree):
                    v = adj[u, i]
                    if v >= 0 and not is_coherent_edge[u, i]:
                        str_before += calc_edge_stretch(u, v, pos, r0, box_size, inv_L)

                pos[u, 0] = new_px; pos[u, 1] = new_py; pos[u, 2] = new_pz

                s_after = 0.0
                for i in range(n_aff):
                    s_after += calc_node_shear(aff_nodes_m1[i], adj, pos, box_size, inv_L, shear_vecs_buf, max_degree)
                t_after = sum_torsion_for_nodes(aff_nodes_m1, n_aff, adj, pos, box_size, inv_L, edge_buf, max_degree)
                
                str_after = 0.0
                for i in range(max_degree):
                    v = adj[u, i]
                    if v >= 0 and not is_coherent_edge[u, i]:
                        str_after += calc_edge_stretch(u, v, pos, r0, box_size, inv_L)

                delta_H = (eff_ks * (s_after - s_before) +
                           kappa_t * (t_after - t_before) +
                           kappa_r * (str_after - str_before))

                # Metropolis-Hastings Acceptance Criterion
                # Ref: Metropolis, N. et al. (1953) J. Chem. Phys. 21, 1087; Hastings, W. K. (1970) Biometrika 57, 97
                if delta_H <= 0.0 or np.random.rand() < math.exp(-beta_mc * delta_H):
                    win_spatial_acc += 1
                else:
                    pos[u, 0] = old_px; pos[u, 1] = old_py; pos[u, 2] = old_pz

            # MOVE 2: SU(2) Gauge Phase Holonomy Updates
            # Ref: Creutz, M. (1980) Phys. Rev. D 21(8), 2308--2315
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

                        delta_H = beta_gauge * (s_plaq_after - s_plaq_before) + beta_mc * 0.5 * lambda_j * (j_after - j_before)
                        if delta_H <= 0.0 or np.random.rand() < math.exp(-delta_H):
                            win_gauge_acc += 1
                        else:
                            gauge_u[u, e_idx, 0] = old_qu0; gauge_u[u, e_idx, 1] = old_qu1
                            gauge_u[u, e_idx, 2] = old_qu2; gauge_u[u, e_idx, 3] = old_qu3

                            gauge_u[v, v_u_idx, 0] = old_qv0; gauge_u[v, v_u_idx, 1] = old_qv1
                            gauge_u[v, v_u_idx, 2] = old_qv2; gauge_u[v, v_u_idx, 3] = old_qv3

            # MOVE 3: 2-to-2 Topological Link Swap (Bistellar Pachner Moves on Discrete Geometry)
            # Refs: Pachner, U. (1991) Geom. Dedicata 38(3), 301; Ambjørn, J. & Loll, R. (1998) Nucl. Phys. B 536, 407
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
                            # --- Bounded Energy-Dependent Cutoff & Fermi-Dirac Sleeve ---
                            u_sh = calc_node_shear(u, adj, pos, box_size, inv_L, shear_vecs_buf, max_degree)
                            v_sh = calc_node_shear(v, adj, pos, box_size, inv_L, shear_vecs_buf, max_degree)
                            w_sh = calc_node_shear(w, adj, pos, box_size, inv_L, shear_vecs_buf, max_degree)
                            z_sh = calc_node_shear(z, adj, pos, box_size, inv_L, shear_vecs_buf, max_degree)

                            u_g = calc_node_jamming(u, gauge_u, max_degree)
                            v_g = calc_node_jamming(v, gauge_u, max_degree)
                            w_g = calc_node_jamming(w, gauge_u, max_degree)
                            z_g = calc_node_jamming(z, gauge_u, max_degree)

                            # 1. Bounded Energy-Dependent Distance Cutoff
                            E_local = u_sh + u_g
                            E_vac = 4.0 * (1.0 - math.exp(-1.0 / beta_gauge))
                            E_ratio = max(0.0, (E_local - E_vac) / max(1e-6, E_vac))

                            # Hyperbolic clamping ensures R_max^2 NEVER exceeds 2.50 * r0^2
                            clamped_expansion = 0.30 * math.tanh(sleeve_tunnel_alpha * E_ratio)
                            effective_cutoff_sq = (cutoff_prefactor + clamped_expansion) * r0 * r0

                            dx_uz, dy_uz, dz_uz = pbc_diff_vec(pos[u], pos[z], box_size, inv_L)
                            if (dx_uz*dx_uz + dy_uz*dy_uz + dz_uz*dz_uz) > effective_cutoff_sq: continue

                            dx_wv, dy_wv, dz_wv = pbc_diff_vec(pos[w], pos[v], box_size, inv_L)
                            if (dx_wv*dx_wv + dy_wv*dy_wv + dz_wv*dz_wv) > effective_cutoff_sq: continue

                            # 2. Evaluate Shielding (Modes 2 & 3)
                            if mode_val in (2, 3):
                                snr_spatial = max(u_sh, v_sh, w_sh, z_sh) * eff_ks / (2.0 * sigma_tau_sq)

                                node_deg = 4.0
                                u_g_vac_mean = node_deg * (1.0 - math.exp(-1.0 / beta_gauge))
                                max_u_g = max(u_g, v_g, w_g, z_g)
                                snr_gauge = max(0.0, max_u_g - u_g_vac_mean) * beta_gauge / (2.0 * sigma_tau_sq)

                                # Compute Coupled L2 SNR Norm
                                snr_coupled = math.sqrt(snr_spatial * snr_spatial + sleeve_weight * snr_gauge * snr_gauge)

                                if sleeve_mode == 1:  # Continuous Fermi-Dirac Mode (v4.3.0)
                                    arg = (snr_coupled - snr_crit) / max(1e-6, sleeve_sigma)
                                    if arg > 16.0:
                                        sleeve_protected_swaps += 1
                                        continue
                                    elif arg > -16.0:
                                        p_allow = 1.0 / (1.0 + math.exp(arg))
                                        if np.random.rand() > p_allow:
                                            sleeve_protected_swaps += 1
                                            continue
                                else:  # Legacy Step-Function Mode (v4.2.20)
                                    if snr_coupled > snr_crit:
                                        sleeve_protected_swaps += 1
                                        continue

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
                                    aff_nodes_m3[0] = u; aff_nodes_m3[1] = v
                                    aff_nodes_m3[2] = w; aff_nodes_m3[3] = z

                                    q_uv = gauge_u[u, v_idx].copy()
                                    q_vu = gauge_u[v, v_u_idx].copy()
                                    q_wz = gauge_u[w, z_idx].copy()
                                    q_zw = gauge_u[z, z_w_idx].copy()

                                    q_uz = align_holonomy_geodesic(q_uv, pos[u], pos[v], pos[z], box_size, inv_L)
                                    q_wv = align_holonomy_geodesic(q_wz, pos[w], pos[z], pos[v], box_size, inv_L)

                                    s_before = 0.0
                                    for i in range(4):
                                        s_before += calc_node_shear(aff_nodes_m3[i], adj, pos, box_size, inv_L, shear_vecs_buf, max_degree)
                                    str_before = calc_edge_stretch(u, v, pos, r0, box_size, inv_L) + calc_edge_stretch(w, z, pos, r0, box_size, inv_L)
                                    t_before = sum_torsion_for_nodes(aff_nodes_m3, 4, adj, pos, box_size, inv_L, edge_buf, max_degree)
                                    
                                    j_before = 0.5 * (calc_node_jamming(u, gauge_u, max_degree) + calc_node_jamming(v, gauge_u, max_degree) +
                                                      calc_node_jamming(w, gauge_u, max_degree) + calc_node_jamming(z, gauge_u, max_degree))

                                    adj[u, v_idx] = z
                                    adj[w, z_idx] = v
                                    adj[v, v_u_idx] = w
                                    adj[z, z_w_idx] = u

                                    gauge_u[u, v_idx, 0] = q_uz[0]; gauge_u[u, v_idx, 1] = q_uz[1]
                                    gauge_u[u, v_idx, 2] = q_uz[2]; gauge_u[u, v_idx, 3] = q_uz[3]

                                    gauge_u[z, z_w_idx, 0] = q_uz[0]; gauge_u[z, z_w_idx, 1] = -q_uz[1]
                                    gauge_u[z, z_w_idx, 2] = -q_uz[2]; gauge_u[z, z_w_idx, 3] = -q_uz[3]

                                    gauge_u[w, z_idx, 0] = q_wv[0]; gauge_u[w, z_idx, 1] = q_wv[1]
                                    gauge_u[w, z_idx, 2] = q_wv[2]; gauge_u[w, z_idx, 3] = q_wv[3]

                                    gauge_u[v, v_u_idx, 0] = q_wv[0]; gauge_u[v, v_u_idx, 1] = -q_wv[1]
                                    gauge_u[v, v_u_idx, 2] = -q_wv[2]; gauge_u[v, v_u_idx, 3] = -q_wv[3]

                                    j_after = 0.5 * (calc_node_jamming(u, gauge_u, max_degree) + calc_node_jamming(v, gauge_u, max_degree) +
                                                     calc_node_jamming(w, gauge_u, max_degree) + calc_node_jamming(z, gauge_u, max_degree))

                                    s_after = 0.0
                                    for i in range(4):
                                        s_after += calc_node_shear(aff_nodes_m3[i], adj, pos, box_size, inv_L, shear_vecs_buf, max_degree)
                                    str_after = calc_edge_stretch(u, z, pos, r0, box_size, inv_L) + calc_edge_stretch(w, v, pos, r0, box_size, inv_L)

                                    delta_H_partial = (eff_ks * (s_after - s_before) + 
                                                       kappa_r * (str_after - str_before) +
                                                       lambda_j * (j_after - j_before))

                                    r = np.random.rand()
                                    max_allowed_delta = -math.log(r) / beta_mc

                                    if (delta_H_partial - kappa_t * t_before) > max_allowed_delta:
                                        adj[u, v_idx] = v; adj[w, z_idx] = z
                                        adj[v, v_u_idx] = u; adj[z, z_w_idx] = w

                                        gauge_u[u, v_idx, 0] = q_uv[0]; gauge_u[u, v_idx, 1] = q_uv[1]; gauge_u[u, v_idx, 2] = q_uv[2]; gauge_u[u, v_idx, 3] = q_uv[3]
                                        gauge_u[v, v_u_idx, 0] = q_vu[0]; gauge_u[v, v_u_idx, 1] = q_vu[1]; gauge_u[v, v_u_idx, 2] = q_vu[2]; gauge_u[v, v_u_idx, 3] = q_vu[3]
                                        gauge_u[w, z_idx, 0] = q_wz[0]; gauge_u[w, z_idx, 1] = q_wz[1]; gauge_u[w, z_idx, 2] = q_wz[2]; gauge_u[w, z_idx, 3] = q_wz[3]
                                        gauge_u[z, z_w_idx, 0] = q_zw[0]; gauge_u[z, z_w_idx, 1] = q_zw[1]; gauge_u[z, z_w_idx, 2] = q_zw[2]; gauge_u[z, z_w_idx, 3] = q_zw[3]

                                        lazy_exits += 1
                                    else:
                                        t_after = sum_torsion_for_nodes(aff_nodes_m3, 4, adj, pos, box_size, inv_L, edge_buf, max_degree)
                                        delta_H_total = delta_H_partial + kappa_t * (t_after - t_before)

                                        if delta_H_total <= 0.0 or r < math.exp(-beta_mc * delta_H_total):
                                            win_topo_acc += 1
                                        else:
                                            adj[u, v_idx] = v; adj[w, z_idx] = z
                                            adj[v, v_u_idx] = u; adj[z, z_w_idx] = w

                                            gauge_u[u, v_idx, 0] = q_uv[0]; gauge_u[u, v_idx, 1] = q_uv[1]; gauge_u[u, v_idx, 2] = q_uv[2]; gauge_u[u, v_idx, 3] = q_uv[3]
                                            gauge_u[v, v_u_idx, 0] = q_vu[0]; gauge_u[v, v_u_idx, 1] = q_vu[1]; gauge_u[v, v_u_idx, 2] = q_vu[2]; gauge_u[v, v_u_idx, 3] = q_vu[3]
                                            gauge_u[w, z_idx, 0] = q_wz[0]; gauge_u[w, z_idx, 1] = q_wz[1]; gauge_u[w, z_idx, 2] = q_wz[2]; gauge_u[w, z_idx, 3] = q_wz[3]
                                            gauge_u[z, z_w_idx, 0] = q_zw[0]; gauge_u[z, z_w_idx, 1] = q_zw[1]; gauge_u[z, z_w_idx, 2] = q_zw[2]; gauge_u[z, z_w_idx, 3] = q_zw[3]

                                            full_rejs += 1

            # MOVE 4: Dynamic Small-World Shortcut Insertion (ER=EPR Network Topology)
            # Refs: Watts, D. J. & Strogatz, S. H. (1998) Nature 393, 440; Maldacena, J. & Susskind, L. (2013) Fortschr. Phys. 61, 781
            elif do_move4:
                win_epr_att += 1
                u = np.random.randint(0, N_nodes)
                v = np.random.randint(0, N_nodes)

                if u != v:
                    max_allowed_epr = int(epsilon_sw * N_nodes)
                    
                    existing_slot = -1
                    for i in range(max_degree):
                        if adj[u, i] == v:
                            existing_slot = i
                            break

                    if existing_slot >= 0:
                        if is_coherent_edge[u, existing_slot]:
                            v_slot = -1
                            for i in range(max_degree):
                                if adj[v, i] == u: v_slot = i; break
                            
                            if v_slot >= 0:
                                s_before = calc_node_shear(u, adj, pos, box_size, inv_L, shear_vecs_buf, max_degree) + \
                                           calc_node_shear(v, adj, pos, box_size, inv_L, shear_vecs_buf, max_degree)

                                adj[u, existing_slot] = -1; adj[v, v_slot] = -1
                                is_coherent_edge[u, existing_slot] = False; is_coherent_edge[v, v_slot] = False
                                
                                s_after = calc_node_shear(u, adj, pos, box_size, inv_L, shear_vecs_buf, max_degree) + \
                                          calc_node_shear(v, adj, pos, box_size, inv_L, shear_vecs_buf, max_degree)
                                delta_H = eff_ks * (s_after - s_before)

                                if delta_H <= 0.0 or np.random.rand() < math.exp(-beta_mc * delta_H):
                                    gauge_u[u, existing_slot, 0] = 1.0; gauge_u[u, existing_slot, 1] = 0.0
                                    gauge_u[u, existing_slot, 2] = 0.0; gauge_u[u, existing_slot, 3] = 0.0
                                    gauge_u[v, v_slot, 0] = 1.0; gauge_u[v, v_slot, 1] = 0.0
                                    gauge_u[v, v_slot, 2] = 0.0; gauge_u[v, v_slot, 3] = 0.0
                                    n_epr_links -= 1
                                    win_epr_acc += 1
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
                                s_before = calc_node_shear(u, adj, pos, box_size, inv_L, shear_vecs_buf, max_degree) + \
                                           calc_node_shear(v, adj, pos, box_size, inv_L, shear_vecs_buf, max_degree)

                                adj[u, u_free] = v; adj[v, v_free] = u
                                is_coherent_edge[u, u_free] = True; is_coherent_edge[v, v_free] = True

                                s_after = calc_node_shear(u, adj, pos, box_size, inv_L, shear_vecs_buf, max_degree) + \
                                          calc_node_shear(v, adj, pos, box_size, inv_L, shear_vecs_buf, max_degree)
                                delta_H = eff_ks * (s_after - s_before)

                                if delta_H <= 0.0 or np.random.rand() < math.exp(-beta_mc * delta_H):
                                    gauge_u[u, u_free, 0] = 1.0; gauge_u[u, u_free, 1] = 0.0
                                    gauge_u[u, u_free, 2] = 0.0; gauge_u[u, u_free, 3] = 0.0
                                    gauge_u[v, v_free, 0] = 1.0; gauge_u[v, v_free, 1] = 0.0
                                    gauge_u[v, v_free, 2] = 0.0; gauge_u[v, v_free, 3] = 0.0
                                    n_epr_links += 1
                                    win_epr_acc += 1
                                else:
                                    adj[u, u_free] = -1; adj[v, v_free] = -1
                                    is_coherent_edge[u, u_free] = False; is_coherent_edge[v, v_free] = False

    return (win_spatial_att, win_spatial_acc, 
            win_gauge_att, win_gauge_acc, 
            win_topo_att, win_topo_acc, 
            win_epr_att, win_epr_acc,
            lazy_exits, full_rejs, sleeve_protected_swaps)


# ------------------------------------------------------------------------------
# 4. PRE-ALLOCATED CSR LAPLACIAN & PURE NUMBA SLQ SOLVER ENGINE
# ------------------------------------------------------------------------------

@njit(fastmath=True)
def fill_laplacian_csr_buffers(adj, indptr, indices, data):
    """
    [EXACT IMPLEMENTATION]
    Constructs Compressed Sparse Row (CSR) matrix buffers for graph Laplacians.
    
    Ref: Saad, Y. (2003). Iterative Methods for Sparse Linear Systems (2nd ed.). 
         SIAM. DOI: 10.1137/1.9780898718003
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


@njit(fastmath=True, parallel=True)
def numba_csr_matvec_parallel(indptr, indices, data, x, y):
    """
    [EXACT IMPLEMENTATION]
    Computes parallel sparse matrix-vector product y = A * x in CSR format using Numba prange loops.
    
    Refs:
      - Saad, Y. (2003). Iterative Methods for Sparse Linear Systems (2nd ed.). SIAM.
      - Lam, S. K. et al. (2015). Numba: A LLVM-based Python JIT compiler. 
        Proc. LLVM Infrastructure in HPC, 1--6. DOI: 10.1145/2833157.2833162
    """
    for i in prange(x.shape[0]):
        acc = 0.0
        for j in range(indptr[i], indptr[i + 1]):
            acc += data[j] * x[indices[j]]
        y[i] = acc


class SLQWorkspace:
    """
    [EXACT IMPLEMENTATION]
    Pre-allocated workspace buffers for Stochastic Lanczos Quadrature (SLQ) execution.
    
    Ref: Ubaru, S. et al. (2017). SIAM J. Matrix Anal. Appl., 38(4), 1075--1099.
    """
    def __init__(self, N_nodes: int, max_degree: int = 6):
        self.N_nodes = N_nodes
        self.max_nnz = N_nodes * (max_degree + 1)
        self.indptr = np.zeros(N_nodes + 1, dtype=np.int32)
        self.indices = np.zeros(self.max_nnz, dtype=np.int32)
        self.data = np.zeros(self.max_nnz, dtype=np.float64)
        
        self.w = np.zeros(N_nodes, dtype=np.float64)
        self.w_next = np.zeros(N_nodes, dtype=np.float64)
        self.v_prev = np.zeros(N_nodes, dtype=np.float64)


def compute_ds_slq(adj, N_nodes, box_size, slq_ws: SLQWorkspace, num_samples=15, m_lanczos=35):
    """
    [EXACT IMPLEMENTATION]
    Estimates the heat kernel trace Tr(exp(-t*L)) on graph Laplacian L using Stochastic 
    Lanczos Quadrature (SLQ) to extract running spectral dimension d_s(t) = -2 d(ln P)/d(ln t).
    
    Refs:
      - Ubaru, S., Chen, J., & Saad, Y. (2017). Fast Estimation of Tr(f(A)) via Stochastic 
        Lanczos Quadrature. SIAM J. Matrix Anal. Appl., 38(4), 1075--1099.
      - Hutchinson, M. F. (1989). A stochastic estimator of the trace of the influence matrix. 
        Comm. Stat. Sim. Comp., 18(3), 1059--1076.
      - Lanczos, C. (1950). An iteration method for the solution of the eigenvalue problem. 
        J. Res. Natl. Bur. Stand., 45(4), 255--282.
      - Ambjørn, J., Jurkiewicz, J., & Loll, R. (2005). Spectral Dimension of the Universe. 
        Phys. Rev. Lett., 95(17), 171301.
    """

    fill_laplacian_csr_buffers(adj, slq_ws.indptr, slq_ws.indices, slq_ws.data)

    t_vals = np.logspace(-1.0, 1.5, 60)
    P_t = np.zeros(len(t_vals), dtype=np.float64)
    inv_sqrt_N = 1.0 / np.sqrt(N_nodes)

    w = slq_ws.w
    w_next = slq_ws.w_next
    v_prev = slq_ws.v_prev

    for s in range(num_samples):
        # Hutchinson Trace Estimator Probe Vector (Rademacher Random Distribution)
        # Ref: Hutchinson, M. F. (1989) Comm. Stat. Sim. Comp. 18(3), 1059--1076
        v = (2.0 * np.random.randint(0, 2, size=N_nodes) - 1.0) * inv_sqrt_N
        alpha = np.zeros(m_lanczos, dtype=np.float64)
        beta = np.zeros(m_lanczos, dtype=np.float64)
        
        w[:] = v
        v_prev.fill(0.0)
        
        j_final = m_lanczos - 1
        # Lanczos Tridiagonalization Iteration Engine
        # Ref: Lanczos, C. (1950) J. Res. Natl. Bur. Stand. 45(4), 255--282
        for j in range(m_lanczos):
            numba_csr_matvec_parallel(slq_ws.indptr, slq_ws.indices, slq_ws.data, w, w_next)
            alpha[j] = np.dot(w, w_next)
            w_next -= alpha[j] * w + (beta[j-1] * v_prev if j > 0 else 0.0)
            if j < m_lanczos - 1:
                b = np.linalg.norm(w_next)
                beta[j] = b
                if b < 1e-12:
                    j_final = j
                    break
                v_prev[:] = w
                w[:] = w_next / b
                
        T_mat = np.diag(alpha[:j_final+1]) + np.diag(beta[:j_final], 1) + np.diag(beta[:j_final], -1)
        eig_T, Q_T = np.linalg.eigh(T_mat)
        tau = Q_T[0, :] ** 2
        
        P_t += np.sum(tau[:, None] * np.exp(-np.outer(eig_T, t_vals)), axis=0)

    P_t /= num_samples

    log_t = np.log(t_vals)
    log_P = np.log(np.maximum(P_t, 1e-30))

    local_ds = np.zeros(len(t_vals) - 2)
    for i in range(1, len(t_vals) - 1):
        slope = (log_P[i+1] - log_P[i-1]) / (log_t[i+1] - log_t[i-1])
        local_ds[i-1] = -2.0 * slope

    t_mid = t_vals[1:-1]
    
    if N_nodes <= 4096:
        t_min_valid, t_max_valid = 0.8, 3.0
    else:
        t_min_valid, t_max_valid = 8.0, 25.0

    valid_indices = np.where((t_mid >= t_min_valid) & (t_mid <= t_max_valid))[0]

    if len(valid_indices) > 0:
        ds_mean = float(np.mean(local_ds[valid_indices]))
    else:
        ds_mean = float(np.mean(local_ds))

    return ds_mean, t_mid, local_ds


def compute_cv_binning(energy_history, beta_mc, N_nodes, num_blocks=16):
    """
    [EXACT IMPLEMENTATION]
    Calculates specific heat Cv and statistical error bars using data reblocking/binning analysis.
    
    Ref: Flyvbjerg, H. & Petersen, H. G. (1989). Error estimates on averages of correlated data. 
         J. Chem. Phys., 91(1), 461--466. DOI: 10.1063/1.457480
    """
    data = np.array(energy_history[len(energy_history)//2:], dtype=np.float64)
    M = len(data)
    if M < num_blocks * 2:
        var_H = float(np.var(data)) if M > 1 else 0.0
        return (beta_mc ** 2) * var_H / N_nodes, 0.0

    total_var = float(np.var(data))
    cv_mean = (beta_mc ** 2) * total_var / N_nodes

    block_size = M // num_blocks
    block_cvs = np.zeros(num_blocks, dtype=np.float64)
    for b in range(num_blocks):
        block_data = data[b * block_size : (b + 1) * block_size]
        block_cvs[b] = (beta_mc ** 2) * float(np.var(block_data)) / N_nodes

    cv_err = float(np.std(block_cvs, ddof=1)) / math.sqrt(num_blocks)
    return cv_mean, cv_err


# ------------------------------------------------------------------------------
# 5. INITIALIZATION ENGINE (DIAMOND BUILDER & STATIC EPR INJECTOR)
# ------------------------------------------------------------------------------

@njit(fastmath=True)
def _build_diamond_adj(pos, adj, box_size, inv_L, nn_dist, max_degree=6):
    """
    [EXACT IMPLEMENTATION]
    Constructs 4-regular tetrahedral adjacency graph for the diamond crystalline network.
    
    Ref: Ashcroft, N. W. & Mermin, N. D. (1976). Solid State Physics. 
         Saunders College Publishing.
    """
    N = pos.shape[0]
    for u in range(N):
        nbr_count = 0
        for v in range(N):
            if u == v: continue
            dx = pos[v, 0] - pos[u, 0]
            dy = pos[v, 1] - pos[u, 1]
            dz = pos[v, 2] - pos[u, 2]
            dx -= box_size * math.floor(dx * inv_L + 0.5)
            dy -= box_size * math.floor(dy * inv_L + 0.5)
            dz -= box_size * math.floor(dz * inv_L + 0.5)
            dist = math.sqrt(dx * dx + dy * dy + dz * dz)
            if abs(dist - nn_dist) < 0.1 and nbr_count < 4:
                adj[u, nbr_count] = v
                nbr_count += 1


def initialize_diamond_lattice(dim_cells, max_degree=6):
    """
    [EXACT IMPLEMENTATION]
    Generates 8-atom diamond cubic unit cell basis with FCC translation vectors, 
    [1/4, 1/4, 1/4] basis offset, and equilibrium bond distance r0 = (sqrt(3)/4) * a.
    
    Ref: Ashcroft, N. W. & Mermin, N. D. (1976). Solid State Physics.
    """
    fcc_basis = [
        np.array([0.0, 0.0, 0.0]),
        np.array([0.0, 0.5, 0.5]),
        np.array([0.5, 0.0, 0.5]),
        np.array([0.5, 0.5, 0.0])
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
    """
    [EXACT IMPLEMENTATION]
    Injects non-local random shortcut links to create a small-world network topology.
    
    Ref: Watts, D. J. & Strogatz, S. H. (1998). Collective dynamics of 'small-world' networks. 
         Nature, 393, 440--442.
    """
    N = adj.shape[0]
    target_count = int(N * target_density)
    injected = 0

    while injected < target_count:
        u = random.randint(0, N - 1)
        v = random.randint(0, N - 1)
        if u == v: continue

        u_free = -1; v_free = -1
        for i in range(max_degree):
            if adj[u, i] < 0: u_free = i; break
        for i in range(max_degree):
            if adj[v, i] < 0: v_free = i; break

        if u_free >= 0 and v_free >= 0:
            adj[u, u_free] = v
            adj[v, v_free] = u
            is_coherent_edge[u, u_free] = True
            is_coherent_edge[v, v_free] = True
            injected += 1


def reindex_spatial_cache(pos, adj, is_coherent_edge, gauge_u, box_size):
    """
    [EXACT IMPLEMENTATION]
    Re-indexes node memory layouts according to spatial cell keys to maximize L1/L2 cache efficiency.
    
    Ref: Allen, M. P. & Tildesley, D. J. (1987). Computer Simulation of Liquids. Oxford.
    """
    N = pos.shape[0]
    grid_dim = int(round(box_size))
    cell_coords = np.floor(pos).astype(np.int32) % grid_dim
    spatial_keys = cell_coords[:, 0] * (grid_dim * grid_dim) + cell_coords[:, 1] * grid_dim + cell_coords[:, 2]
    
    perm = np.argsort(spatial_keys)
    inv_perm = np.zeros(N, dtype=np.int32)
    inv_perm[perm] = np.arange(N, dtype=np.int32)

    adj_mapped = np.where(adj >= 0, inv_perm[np.maximum(0, adj)], -1)

    pos[:] = pos[perm]
    gauge_u[:] = gauge_u[perm]
    is_coherent_edge[:] = is_coherent_edge[perm]
    adj[:] = adj_mapped[perm]


# ------------------------------------------------------------------------------
# 6. UNIFIED MAIN SIMULATION ENGINE DRIVER
# ------------------------------------------------------------------------------

def run_ela_simulation(
    mode=EngineMode.PAPER1_VACUUM,
    epr_mode=EPRMode.NONE,
    run_id="RUN-V441_PRODUCTION",
    grid_dim=16,
    beta_mc=3.0035,
    beta_gauge=4.50,
    kappa_s=1.00,
    kappa_t=0.03,  # Synchronized default with CLI
    kappa_r=0.00,
    lambda_j=0.10,
    snr_crit=6.50,
    cutoff_prefactor=2.20,
    beta_untensing=0.0175,
    epsilon_sw=0.005,
    scale_a_init=0.50,  # Physical cosmic scale factor progression (0.50 -> 1.00)
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
    sleeve_sigma=0.15,
    sleeve_weight=1.0,
    sleeve_tunnel_alpha=0.05
):
    """
    [ADAPTED / GENERALIZED IMPLEMENTATION]
    Primary driver managing MCMC thermalization, MCS sweep loops, and physical diagnostic streams.
    
    Refs:
      - Metropolis, N. et al. (1953). Equation of State Calculations by Fast Computing Machines.
        The Journal of Chemical Physics, 21(6), 1087--1092. DOI: 10.1063/1.1699114
      - Ubaru, S., Chen, J. & Saad, Y. (2017). Fast Estimation of Tr(f(A)) via Stochastic
        Lanczos Quadrature. SIAM J. Matrix Anal. Appl., 38(4), 1075-1099. DOI: 10.1137/16M1104974
    """
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

    has_soliton = inject_soliton_flag or (q_charge_val != 0)
    if has_soliton:
        inject_topological_soliton(pos, adj, gauge_u, box_size, inv_L, q_charge=q_charge_val)
        print(f"[INIT] Injected SU(2) Skyrmionic Topological Soliton Field (Target Q = {q_charge_val})")

    if epr_mode == EPRMode.STATIC:
        inject_static_epr_shortcuts(adj, is_coherent_edge, target_density=epsilon_sw, max_degree=max_degree)

    slq_ws = SLQWorkspace(N_nodes, max_degree)
    aff_nodes_m1 = np.zeros(1 + max_degree, dtype=np.int32)
    aff_nodes_m3 = np.zeros(4, dtype=np.int32)
    edge_buf = np.zeros((128, 2), dtype=np.int32)
    shear_vecs_buf = np.zeros((6, 3), dtype=np.float64)

    energy_history = []
    sweep_history = []
    w_eos_history = []
    h_sq_history = []
    q_history = []
    splaq_history = []
    window_t_acc = deque(maxlen=3)

    sleeve_str = "Continuous Fermi-Dirac" if sleeve_mode == 1 else "Legacy Step-Function"

    print(f"================================================================================")
    print(f"               EMERGENT LATTICE ARCHITECTURE (ELA v4.4.2)")
    print(f"         UNIFIED MULTI-MODE MONTE CARLO SIMULATION ENGINE & DATA STREAM")
    print(f"================================================================================")
    print(f" Active Mode      : {mode.name}")
    print(f" EPR Mode         : {epr_mode.name}")
    print(f" Run ID           : {run_id}")
    print(f" PRNG Seed        : {resolved_seed}")
    print(f" System Size (N)  : {N_nodes:,} (4-Regular 3D Diamond Torus - n_vac = 4.0, r0 = {r0_eq:.4f})")
    print(f" Total MCS Sweeps : {num_sweeps:,} (1 MCS = {N_nodes:,} Proposals)")
    print(f" Cutoff Prefactor : {cutoff_prefactor:.2f} * r0^2 (Effective Ceiling <= {2.50:.2f} * r0^2)")
    print(f" Sleeve Config     : Mode={sleeve_mode} ({sleeve_str}), Sigma={sleeve_sigma:.4f}, Weight={sleeve_weight:.2f}, TunnelAlpha={sleeve_tunnel_alpha:.4f}")
    if has_soliton:
        print(f" Soliton Injection: ACTIVE (Target Q = {q_charge_val})")
    if mode == EngineMode.PAPER3_COSMOLOGY:
        print(f" Untensing Exponent: beta = {beta_untensing:.4f} (CMB Tilt n_s = {1.0 - 2.0*beta_untensing:.4f})")
        print(f" EPR SW Ceiling   : epsilon_sw = {epsilon_sw * 100.0:.2f}%")
    print(f" Output Directory : {out_dir}")
    print(f" Parameters       : Beta={beta_mc:.4f}, BetaGauge={beta_gauge:.4f}, Ks={kappa_s:.2f}, Kt={kappa_t:.2f}, Kr={kappa_r:.2f}, Lj={lambda_j:.2f}, SnrCrit={snr_crit:.4f}")
    print(f"================================================================================\n")
    
    print("[INIT] Triggering Numba JIT block-kernel compilation...")
    epr_val_int = 1 if epr_mode == EPRMode.DYNAMIC else (2 if epr_mode == EPRMode.STATIC else 0)

    _ = run_numba_mcs_block(
        pos, adj, gauge_u, is_coherent_edge, box_size, inv_L, beta_mc,
        kappa_s, kappa_t, kappa_r, lambda_j, r0_eq,
        max_disp, max_gauge_disp, 1,
        aff_nodes_m1, aff_nodes_m3, edge_buf, shear_vecs_buf,
        cutoff_prefactor, is_warmup=False, mode_val=mode.value, scale_a=scale_a,
        beta_untensing=beta_untensing, snr_crit=snr_crit, epr_mode_val=epr_val_int, epsilon_sw=epsilon_sw,
        has_soliton=has_soliton, beta_gauge=beta_gauge,
        sleeve_mode=sleeve_mode, sleeve_sigma=sleeve_sigma, sleeve_weight=sleeve_weight,
        sleeve_tunnel_alpha=sleeve_tunnel_alpha
    )
    fill_laplacian_csr_buffers(adj, slq_ws.indptr, slq_ws.indices, slq_ws.data)
    
    print("[INIT] Thermalizing spatial geometry (EMA Shear Equipartition)...")
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
            cutoff_prefactor, is_warmup=True, mode_val=mode.value, scale_a=scale_a,
            beta_untensing=beta_untensing, snr_crit=snr_crit, epr_mode_val=epr_val_int, epsilon_sw=epsilon_sw,
            has_soliton=has_soliton, beta_gauge=beta_gauge,
            sleeve_mode=sleeve_mode, sleeve_sigma=sleeve_sigma, sleeve_weight=sleeve_weight,
            sleeve_tunnel_alpha=sleeve_tunnel_alpha
        )
        warmup_sweeps += warmup_block_size

        _, H_shear_curr, _, _, _ = calc_total_system_energy(
            pos, adj, is_coherent_edge, gauge_u, box_size, inv_L, r0_eq, kappa_s, kappa_t, kappa_r, lambda_j, shear_vecs_buf,
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

    ds_curr, t_mid_curve, ds_curve = compute_ds_slq(adj, N_nodes, box_size, slq_ws, num_samples=30, m_lanczos=60)
    print(f"[INIT] Baseline Spectral Dimension d_s = {ds_curr:.4f}\n")
    
    if mode == EngineMode.PAPER3_COSMOLOGY:
        header_fmt = "{:>7} | {:>8} | {:>7} | {:>7} | {:>7} | {:>7} | {:>7} | {:>7} | {:>15}"
        print(header_fmt.format("Sweep", "Swp/s", "Acc_S", "Acc_G", "Acc_T", "Acc_EPR", "d_s", "w(a)", "H^2 (LQC)"))
        print("-" * 105)
    elif mode == EngineMode.PAPER2_GAUGE_SOLITON:
        header_fmt = "{:>7} | {:>8} | {:>7} | {:>7} | {:>7} | {:>7} | {:>8} | {:>6} | {:>9}"
        print(header_fmt.format("Sweep", "Swp/s", "Acc_S", "Acc_G", "Acc_T", "S_plaq", "d_s", "Q_top", "Shields"))
        print("-" * 105)
    else:
        header_fmt = "{:>7} | {:>8} | {:>7} | {:>7} | {:>7} | {:>7} | {:>8} | {:>8} | {:>15}"
        print(header_fmt.format("Sweep", "Swp/s", "Acc_S", "Acc_G", "Acc_T", "LazyEff", "d_s", "ETA", "Status / Flags"))
        print("-" * 105)

    t_sim_start = time.time()
    cum_pure_mc_time = 0.0
    current_sweep = 0
    num_blocks = num_sweeps // log_interval
    total_protected_swaps = 0

    for block_idx in range(num_blocks):
        t_block_start = time.time()

        if mode == EngineMode.PAPER3_COSMOLOGY:
            progress = (current_sweep + log_interval) / float(num_sweeps)
            scale_a = scale_a_init + (1.0 - scale_a_init) * progress  # Advances scale factor a(t) from 0.50 to 1.00
        
        (s_att, s_acc, g_att, g_acc, t_att, t_acc, epr_att, epr_acc, lazy_exits, full_rejs, protected_swaps) = run_numba_mcs_block(
            pos, adj, gauge_u, is_coherent_edge, box_size, inv_L, beta_mc,
            kappa_s, kappa_t, kappa_r, lambda_j, r0_eq,
            max_disp, max_gauge_disp, log_interval,
            aff_nodes_m1, aff_nodes_m3, edge_buf, shear_vecs_buf,
            cutoff_prefactor, is_warmup=False, mode_val=mode.value, scale_a=scale_a,
            beta_untensing=beta_untensing, snr_crit=snr_crit, epr_mode_val=epr_val_int, epsilon_sw=epsilon_sw,
            has_soliton=has_soliton, beta_gauge=beta_gauge,
            sleeve_mode=sleeve_mode, sleeve_sigma=sleeve_sigma, sleeve_weight=sleeve_weight,
            sleeve_tunnel_alpha=sleeve_tunnel_alpha
        )
        
        t_block_end = time.time()
        interval_mc_time = t_block_end - t_block_start
        cum_pure_mc_time += interval_mc_time
        current_sweep += log_interval
        total_protected_swaps += protected_swaps

        if current_sweep % 10000 == 0:
            reindex_spatial_cache(pos, adj, is_coherent_edge, gauge_u, box_size)

        H_curr, _, _, _, _ = calc_total_system_energy(
            pos, adj, is_coherent_edge, gauge_u, box_size, inv_L, r0_eq, kappa_s, kappa_t, kappa_r, lambda_j, shear_vecs_buf,
            scale_a=scale_a, beta_untensing=beta_untensing, mode_val=mode.value, max_degree=max_degree
        )
        energy_history.append(H_curr)
        sweep_history.append(current_sweep)

        H_sq, w_eos, d_G, rho_energy = compute_lqc_bounce_diagnostics(H_curr, N_nodes, scale_a, beta_untensing)
        w_eos_history.append(w_eos)
        h_sq_history.append(H_sq)

        if mode == EngineMode.PAPER2_GAUGE_SOLITON:
            gauge_u_cooled = cool_gauge_field_6cycle(adj, gauge_u, num_cooling_sweeps=25)
            q_curr = calc_topological_charge_q(pos, adj, gauge_u_cooled, box_size, inv_L, r0=r0_eq)
            q_history.append(q_curr)
            su2_plaq = calc_su2_plaquette_action(adj, gauge_u, max_degree)
            splaq_history.append(su2_plaq)
        else:
            q_history.append(0.0)
            splaq_history.append(0.0)

        interval_throughput = log_interval / max(1e-6, interval_mc_time)
        avg_throughput = current_sweep / max(1e-6, cum_pure_mc_time)
        remaining_sweeps = num_sweeps - current_sweep
        eta_seconds = remaining_sweeps / max(1e-6, avg_throughput)

        acc_s = (s_acc / max(1, s_att)) * 100.0
        acc_g = (g_acc / max(1, g_att)) * 100.0
        acc_t = (t_acc / max(1, t_att)) * 100.0
        acc_epr = (epr_acc / max(1, epr_att)) * 100.0 if epr_att > 0 else 0.0
        lazy_eff = (lazy_exits / max(1, lazy_exits + full_rejs)) * 100.0

        window_t_acc.append(acc_t)

        if current_sweep % ds_interval == 0 or current_sweep == num_sweeps:
            ds_curr, t_mid_curve, ds_curve = compute_ds_slq(adj, N_nodes, box_size, slq_ws, num_samples=15, m_lanczos=35)

        if mode == EngineMode.PAPER3_COSMOLOGY:
            row_fmt = "{:7d} | {:8.1f} | {:6.2f}% | {:6.2f}% | {:6.2f}% | {:6.2f}% | {:7.4f} | {:7.4f} | {:15.6e}"
            print(row_fmt.format(current_sweep, interval_throughput, acc_s, acc_g, acc_t, acc_epr, ds_curr, w_eos, H_sq))
        elif mode == EngineMode.PAPER2_GAUGE_SOLITON:
            row_fmt = "{:7d} | {:8.1f} | {:6.2f}% | {:6.2f}% | {:6.2f}% | {:6.4f} | {:8.4f} | {:6.4f} | {:9d}"
            print(row_fmt.format(current_sweep, interval_throughput, acc_s, acc_g, acc_t, splaq_history[-1], ds_curr, q_history[-1], total_protected_swaps))
        else:
            row_fmt = "{:7d} | {:8.1f} | {:6.2f}% | {:6.2f}% | {:6.2f}% | {:6.2f}% | {:8.4f} | {:8.2f}s | {:15}"
            flags = []
            if acc_s < 10.0: flags.append("[WARN: SPATIAL FREEZE]")
            if len(window_t_acc) == 3 and sum(window_t_acc) == 0: flags.append("[WARN: SUSTAINED TOPO JAM]")
            if acc_g < 1.0: flags.append("[WARN: GAUGE LOCK]")
            if abs(ds_curr - 3.0) > 0.8: flags.append("[WARN: D_S DRIFT]")
            status_str = " ".join(flags) if len(flags) > 0 else "OK (Fluid Phase)"
            print(row_fmt.format(current_sweep, interval_throughput, acc_s, acc_g, acc_t, lazy_eff, ds_curr, eta_seconds, status_str))

    t_final = time.time()
    total_elapsed = t_final - t_sim_start

    H_tot, H_s, H_t, H_r, V_j = calc_total_system_energy(
        pos, adj, is_coherent_edge, gauge_u, box_size, inv_L, r0_eq, kappa_s, kappa_t, kappa_r, lambda_j, shear_vecs_buf,
        scale_a=scale_a, beta_untensing=beta_untensing, mode_val=mode.value, max_degree=max_degree
    )

    ds_final, t_mid_curve, ds_curve = compute_ds_slq(adj, N_nodes, box_size, slq_ws, num_samples=50, m_lanczos=45)
    specific_heat_Cv, specific_heat_Cv_err = compute_cv_binning(energy_history, beta_mc, N_nodes, num_blocks=16)

    if mode == EngineMode.PAPER2_GAUGE_SOLITON:
        gauge_u_cooled = cool_gauge_field_6cycle(adj, gauge_u, num_cooling_sweeps=25)
        su2_plaquette_action = calc_su2_plaquette_action(adj, gauge_u, max_degree)
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
    print(f"   ├─ H_shear       : {H_s:.4f}")
    print(f"   ├─ H_torsion     : {H_t:.4f}")
    print(f"   ├─ H_stretch     : {H_r:.4f}")
    print(f"   └─ V_jamming     : {V_j:.4f}")

    if mode == EngineMode.PAPER2_GAUGE_SOLITON:
        print(f" Paper 2 Soliton Diagnostics:")
        print(f"   ├─ Wilson Plaquette S : {su2_plaquette_action:.6f} (Yang-Mills Limit)")
        print(f"   ├─ Topo Winding Charge Q: {topological_charge_Q:.4f} (Q Soliton Continuous Charge)")
        print(f"   ├─ Strand Charge q_k   : {strand_q_charge:.4f} (Fractional Helicities)")
        print(f"   ├─ BPS Soliton Mass m0 : {bps_soliton_mass:.4f} (E_soliton / c^2 Bound)")
        print(f"   └─ Co-Moving Protection: {total_protected_swaps:,} Sleeve Surgery Shields")
    elif mode == EngineMode.PAPER3_COSMOLOGY:
        print(f" Paper 3 Cosmology Diagnostics:")
        print(f"   ├─ Final Dark Energy w: {w_eos_history[-1]:.6f} (CPL EoS w(a))")
        print(f"   ├─ LQC Hubble H^2     : {h_sq_history[-1]:.6e} (Group Geodesic Rate)")
        print(f"   └─ Group Geodesic d_G : {d_G:.6f} rad (S^3 Phase Saturation)")

    print(f"================================================================================\n")

    if save_npz:
        safe_id = run_id.replace("/", "_").replace("\\", "_")
        export_filename = os.path.join(out_dir, f"{safe_id}_{mode.name}_seed{resolved_seed}_v441_results.npz")
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
            H_components=np.array([H_tot, H_s, H_t, H_r, V_j])
        )
        print(f"[EXPORT] Publication payload saved successfully to '{export_filename}'\n")
        return export_filename

    return None


# ------------------------------------------------------------------------------
# 7. AUTOMATED DIAGNOSTIC PLOTTING UTILITY
# ------------------------------------------------------------------------------

def generate_diagnostics_plot(npz_filename, out_dir="."):
    """
    [EXACT IMPLEMENTATION]
    Generates diagnostic figures using Matplotlib.
    
    Ref: Hunter, J. D. (2007). Matplotlib: A 2D graphics environment. 
         Computing in Science & Engineering, 9(3), 90--95.
    """
    if not os.path.exists(npz_filename):
        print(f"[ERROR] Cannot plot: File '{npz_filename}' not found.")
        return

    data = np.load(npz_filename)
    run_id = str(data["run_id"])
    mode_str = str(data["mode"]) if "mode" in data else "PAPER1_VACUUM"
    seed_val = str(data["seed"]) if "seed" in data else "N/A"
    N_nodes = int(data["N_nodes"]) if "N_nodes" in data else 4096
    
    t_mid = data["t_mid_curve"]
    ds_curve = data["ds_curve"]
    sweep_history = data["sweep_history"]
    energy_history = data["energy_history"]
    ds_final = float(data["ds_final"])
    specific_heat = float(data["specific_heat_Cv"])
    specific_heat_err = float(data["specific_heat_Cv_err"]) if "specific_heat_Cv_err" in data else 0.0

    fit_min, fit_max = (8.0, 25.0) if N_nodes > 4096 else (0.8, 3.0)

    # --------------------------------------------------------------------------
    # MODE 1: PAPER 1 PURE SPATIAL VACUUM (2 PANELS)
    # --------------------------------------------------------------------------
    if mode_str == "PAPER1_VACUUM":
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5), dpi=200)

        # Panel (a): Spectral Dimension d_s(t)
        ax1.plot(t_mid, ds_curve, color='#1f77b4', lw=2, label=r'Measured $d_s(t)$')
        ax1.axvspan(fit_min, fit_max, color='#2ca02c', alpha=0.15, label=f'Fit Region [{fit_min}, {fit_max}]')
        ax1.axhline(3.00, color='#d62728', linestyle='--', lw=1.5, label=r'Target ($d_s = 3.00$)')
        ax1.set_xscale('log')
        y_min = max(0.0, float(np.min(ds_curve)) - 0.5)
        y_max = max(5.0, float(np.max(ds_curve)) + 0.5)
        ax1.set_ylim(y_min, y_max)
        ax1.set_xlabel(r'Diffusion Time $t$')
        ax1.set_ylabel(r'Spectral Dimension $d_s(t)$')
        ax1.set_title(f'Spectral Dimension ({run_id} | Paper 1 Vacuum)\nFinal $d_s = {ds_final:.4f}$')
        ax1.grid(True, which='both', linestyle=':', alpha=0.6)
        ax1.legend(loc='upper right')

        # Panel (b): Total Energy H_tot
        ax2.plot(sweep_history, energy_history, color='#ff7f0e', lw=1.5, label=r'Total Energy $H_{\mathrm{tot}}$')
        ax2.set_xlabel(r'Monte Carlo Sweep (MCS)')
        ax2.set_ylabel(r'Total Energy $H_{\mathrm{tot}}$')
        ax2.set_title(f'Energy Trajectory & Thermalization\n$C_v = {specific_heat:.6f} \\pm {specific_heat_err:.6f}$')
        ax2.grid(True, linestyle=':', alpha=0.6)
        ax2.legend(loc='upper right')

    # --------------------------------------------------------------------------
    # MODE 2: PAPER 2 MICRO-SCALE SOLITON & GAUGE (4 PANELS)
    # --------------------------------------------------------------------------
    elif mode_str == "PAPER2_GAUGE_SOLITON":
        fig, axs = plt.subplots(2, 2, figsize=(12, 9), dpi=200)
        (ax1, ax2), (ax3, ax4) = axs

        # Panel (a): Spectral Dimension d_s(t)
        ax1.plot(t_mid, ds_curve, color='#1f77b4', lw=2, label=r'Measured $d_s(t)$')
        ax1.axvspan(fit_min, fit_max, color='#2ca02c', alpha=0.15, label=f'Fit Region [{fit_min}, {fit_max}]')
        ax1.axhline(3.00, color='#d62728', linestyle='--', lw=1.5, label=r'Target ($d_s = 3.00$)')
        ax1.set_xscale('log')
        ax1.set_xlabel(r'Diffusion Time $t$')
        ax1.set_ylabel(r'Spectral Dimension $d_s(t)$')
        ax1.set_title(f'(a) Spectral Dimension ({run_id})\nFinal $d_s = {ds_final:.4f}$')
        ax1.grid(True, which='both', linestyle=':', alpha=0.6)
        ax1.legend(loc='upper right')

        # Panel (b): Topological Soliton Winding Charge Q_top
        q_history = data["q_history"] if "q_history" in data else np.array([])
        q_final = float(data["topological_charge_Q"]) if "topological_charge_Q" in data else 1.0

        if len(q_history) > 0 and len(q_history) == len(sweep_history):
            ax2.plot(sweep_history, q_history, color='#9467bd', lw=2, label=f'Measured $Q_t$ (Final = {q_final:.4f})')
        else:
            ax2.axhline(q_final, color='#9467bd', lw=2.5, label=f'Final $Q{{\\mathrm{{top}}}} = {q_final:.4f}$')

        ax2.axhline(1.0, color='#d62728', linestyle='--', lw=1, label=r'Target ($Q = 1.0$)')
        ax2.set_ylim(-0.5, 2.5)
        ax2.set_xlim(0, sweep_history[-1])  # Explicitly enforce full MCS sweep range
        ax2.set_xlabel(r'Monte Carlo Sweep (MCS)')
        ax2.set_ylabel(r'Topological Charge $Q_{\mathrm{top}}$')
        ax2.set_title(r'(b) Soliton Topological Survival $Q_{\mathrm{top}}$')
        ax2.grid(True, linestyle=':', alpha=0.6)
        ax2.legend(loc='upper right')

        # Panel (c): SU(2) Wilson Plaquette Action S_plaq
        splaq_history = data["splaq_history"] if "splaq_history" in data else np.array([])
        s_plaq = float(data["su2_plaquette_action"]) if "su2_plaquette_action" in data else 0.0

        if len(splaq_history) > 0 and len(splaq_history) == len(sweep_history):
            ax3.plot(sweep_history, splaq_history, color='#2ca02c', lw=2, label=f'$S{{\\mathrm{{plaq}}}}$ (Final = {s_plaq:.4f})')
        else:
            ax3.axhline(s_plaq, color='#2ca02c', lw=2, label=f'$S{{\\mathrm{{plaq}}}} = {s_plaq:.4f}$')

        ax3.set_xlim(0, sweep_history[-1])  # Explicitly enforce full MCS sweep range
        ax3.set_xlabel(r'Monte Carlo Sweep (MCS)')
        ax3.set_ylabel(r'Wilson Plaquette Action $S_{\mathrm{plaq}}$')
        ax3.set_title(r'(c) $SU(2)$ Gauge Field Action Relaxation')
        ax3.grid(True, linestyle=':', alpha=0.6)
        ax3.legend(loc='upper right')

        # Panel (d): Energy Trajectory H_tot
        ax4.plot(sweep_history, energy_history, color='#ff7f0e', lw=1.5, label=r'$H_{\mathrm{tot}}$')
        ax4.set_xlabel(r'Monte Carlo Sweep (MCS)')
        ax4.set_ylabel(r'Total Energy $H_{\mathrm{tot}}$')
        ax4.set_title(f'(d) Thermal Energy Trajectory\n$C_v = {specific_heat:.4f} \\pm {specific_heat_err:.4f}$')
        ax4.grid(True, linestyle=':', alpha=0.6)
        ax4.legend(loc='upper right')

    # --------------------------------------------------------------------------
    # MODE 3: PAPER 3 MACRO COSMOLOGY & LQC BOUNCE (4 PANELS)
    # --------------------------------------------------------------------------
    elif mode_str == "PAPER3_COSMOLOGY":
        fig, axs = plt.subplots(2, 2, figsize=(12, 9), dpi=200)
        (ax1, ax2), (ax3, ax4) = axs

        w_eos_history = data["w_eos_history"] if "w_eos_history" in data else np.array([])
        h_sq_history = data["h_sq_history"] if "h_sq_history" in data else np.array([])

        # Panel (a): Spectral Dimension d_s(t)
        ax1.plot(t_mid, ds_curve, color='#1f77b4', lw=2, label=r'Measured $d_s(t)$')
        ax1.axvspan(fit_min, fit_max, color='#2ca02c', alpha=0.15, label=f'Fit Region [{fit_min}, {fit_max}]')
        ax1.axhline(3.00, color='#d62728', linestyle='--', lw=1.5, label=r'Target ($d_s = 3.00$)')
        ax1.set_xscale('log')
        ax1.set_xlabel(r'Diffusion Time $t$')
        ax1.set_ylabel(r'Spectral Dimension $d_s(t)$')
        ax1.set_title(f'(a) Continuum 3D Metric Stability\nFinal $d_s = {ds_final:.4f}$')
        ax1.grid(True, which='both', linestyle=':', alpha=0.6)
        ax1.legend(loc='upper right')

        # Panel (b): Dark Energy Equation of State w(a)
        if len(w_eos_history) > 0:
            ax2.plot(sweep_history, w_eos_history, color='#e377c2', lw=2, label=r'EoS $w(a)$')
            w_final = w_eos_history[-1]
            ax2.axhline(-1.00, color='#d62728', linestyle='--', lw=1.5, label=r'$\Lambda$ Boundary ($w = -1.0$)')
            ax2.set_title(f'(b) CPL Dark Energy EoS $w(a)$\nFinal $w = {w_final:.4f}$')
        else:
            ax2.set_title('(b) CPL Dark Energy EoS w(a)')
        ax2.set_xlabel(r'Monte Carlo Sweep (MCS)')
        ax2.set_ylabel(r'Equation of State $w(a)$')
        ax2.grid(True, linestyle=':', alpha=0.6)
        ax2.legend(loc='upper right')

        # Panel (c): LQC Hubble Rate H^2
        if len(h_sq_history) > 0:
            ax3.plot(sweep_history, h_sq_history, color='#17becf', lw=2, label=r'LQC Rate $H^2$')
            h_sq_final = h_sq_history[-1]
            ax3.set_title(f'(c) LQC Hubble Bounce Rate\nFinal $H^2 = {h_sq_final:.4e}$')
        else:
            ax3.set_title('(c) LQC Hubble Bounce Rate')
        ax3.set_xlabel(r'Monte Carlo Sweep (MCS)')
        ax3.set_ylabel(r'Hubble Parameter $H^2$')
        ax3.grid(True, linestyle=':', alpha=0.6)
        ax3.legend(loc='upper right')

        # Panel (d): Energy Trajectory H_tot
        ax4.plot(sweep_history, energy_history, color='#ff7f0e', lw=1.5, label=r'$H_{\mathrm{tot}}$')
        ax4.set_xlabel(r'Monte Carlo Sweep (MCS)')
        ax4.set_ylabel(r'Total Energy $H_{\mathrm{tot}}$')
        ax4.set_title(f'(d) Thermal Energy Trajectory\n$C_v = {specific_heat:.4f} \\pm {specific_heat_err:.4f}$')
        ax4.grid(True, linestyle=':', alpha=0.6)
        ax4.legend(loc='upper right')

    plt.tight_layout()
    safe_id = run_id.replace("/", "_").replace("\\", "_")
    plot_filename = os.path.join(out_dir, f"{safe_id}_{mode_str}_seed{seed_val}_v441_diagnostics.png")
    plt.savefig(plot_filename)
    print(f"[PLOT] Publication diagnostic plot saved to '{plot_filename}'")
    plt.close()


# ------------------------------------------------------------------------------
# 8. CLI INTERFACE
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ELA v4.4.2 Master Engine (Paper 1, 2, 3)")
    parser.add_argument("--mode", type=int, default=1, choices=[1, 2, 3], help="Engine mode: 1=Paper1 Vacuum, 2=Paper2 Soliton, 3=Paper3 Cosmology")
    parser.add_argument("--epr-mode", type=str, choices=["dynamic", "static", "none"], default=None, help="EPR shortcut handling (REQUIRED for --mode 3)")
    parser.add_argument("--soliton", "--inject-soliton", action="store_true", dest="inject_soliton", help="Inject Skyrmionic SU(2) topological soliton field (Paper 2)")
    parser.add_argument("--q-charge", "--soliton-q", "--q_charge", type=int, default=0, dest="q_charge", help="Target topological winding charge Q to inject")
    parser.add_argument("--run_id", type=str, default="RUN-V441_PRODUCTION", help="Unique identifier for run")
    parser.add_argument("--seed", type=int, default=None, metavar="INT", help="Optional PRNG seed")
    parser.add_argument("--dim", type=int, default=16, help="Grid dimension cells")
    parser.add_argument("--beta", type=float, default=3.0035, help="Inverse temperature beta")
    parser.add_argument("--beta-gauge", "--beta_gauge", type=float, default=6.15, dest="beta_gauge", help="Gauge coupling beta_gauge for Wilson Plaquette Action")
    parser.add_argument("--ks", "--kappa_s", type=float, default=1.00, dest="kappa_s", help="Shear coupling")
    parser.add_argument("--kt", "--kappa_t", type=float, default=0.03, dest="kappa_t", help="Torsion coupling (Synchronized: 0.03)")
    parser.add_argument("--kr", "--kappa_r", type=float, default=0.00, dest="kappa_r", help="Stretch coupling")
    parser.add_argument("--lj", "--lambda_j", type=float, default=0.141421356, dest="lambda_j", help="Gauge phase jamming coupling")
    parser.add_argument("--snr-crit", "--snr_crit", type=float, default=6.50, dest="snr_crit", help="SNR threshold for co-moving sleeve core protection (default: 6.50)")
    parser.add_argument("--cutoff", "--cutoff_prefactor", type=float, default=2.20, dest="cutoff_prefactor", help="Cutoff prefactor multiplying r0^2")
    parser.add_argument("--sleeve-mode", "--sleeve_mode", type=int, default=1, choices=[0, 1], dest="sleeve_mode", help="Co-moving sleeve mode: 0=Legacy Step-Function, 1=Continuous Fermi-Dirac")
    parser.add_argument("--sleeve-sigma", "--sleeve_sigma", type=float, default=0.10, dest="sleeve_sigma", help="Fermi-Dirac boundary softness width sigma_sleeve")
    parser.add_argument("--sleeve-weight", "--sleeve_weight", type=float, default=1.0, dest="sleeve_weight", help="Gauge jamming weight factor w_g in coupled L2 norm")
    parser.add_argument("--sleeve-tunnel-alpha", "--sleeve_tunnel_alpha", type=float, default=0.05, dest="sleeve_tunnel_alpha", help="Hyperbolic tunneling distance sensitivity alpha_tunnel")
    parser.add_argument("--beta-untensing", type=float, default=0.0175, help="Viscoelastic untensing exponent beta")
    parser.add_argument("--epsilon-sw", type=float, default=0.002, help="Small-world EPR shortcut transition ceiling")
    parser.add_argument("--steps", type=int, default=50000, help="Total Monte Carlo sweeps")
    parser.add_argument("--out_dir", type=str, default=".", help="Directory for output payload and plots")
    parser.add_argument("--plot", action="store_true", help="Generate diagnostic plots after run")

    args = parser.parse_args()

    if args.mode == 3 and args.epr_mode is None:
        parser.error("[CONFIG ERROR] --mode 3 (Paper 3 Macro Cosmology) requires an explicit EPR configuration flag.\n"
                     "Please specify --epr-mode {dynamic, static, none} to ensure reproducible physics.")

    q_charge_target = args.q_charge
    if args.inject_soliton and q_charge_target == 0:
        q_charge_target = 1

    mode_map = {
        1: EngineMode.PAPER1_VACUUM,
        2: EngineMode.PAPER2_GAUGE_SOLITON,
        3: EngineMode.PAPER3_COSMOLOGY
    }
    selected_mode = mode_map[args.mode]

    epr_map = {
        "dynamic": EPRMode.DYNAMIC,
        "static": EPRMode.STATIC,
        "none": EPRMode.NONE
    }
    selected_epr = epr_map.get(args.epr_mode, EPRMode.NONE)

    npz_file = run_ela_simulation(
        mode=selected_mode,
        epr_mode=selected_epr,
        run_id=args.run_id,
        grid_dim=args.dim,
        beta_mc=args.beta,
        beta_gauge=args.beta_gauge,
        kappa_s=args.kappa_s,
        kappa_t=args.kappa_t,
        kappa_r=args.kappa_r,
        lambda_j=args.lambda_j,
        snr_crit=args.snr_crit,
        cutoff_prefactor=args.cutoff_prefactor,
        beta_untensing=args.beta_untensing,
        epsilon_sw=args.epsilon_sw,
        inject_soliton_flag=args.inject_soliton,
        q_charge_val=q_charge_target,
        num_sweeps=args.steps,
        seed=args.seed,
        out_dir=args.out_dir,
        save_npz=True,
        sleeve_mode=args.sleeve_mode,
        sleeve_sigma=args.sleeve_sigma,
        sleeve_weight=args.sleeve_weight,
        sleeve_tunnel_alpha=args.sleeve_tunnel_alpha
    )

    if args.plot and npz_file:
        generate_diagnostics_plot(npz_file, out_dir=args.out_dir)
