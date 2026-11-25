"""
ELA Paper VI (Version 1.0) — Deuteron Radial Schrödinger Boundary-Value Solver
Reproduces Analytic Derivation 3.1 & Table I benchmarks (Section III.B).
"""
import numpy as np
from scipy.linalg import eigh_tridiagonal

# Physical constants & ELA Paper VI two-phase potential parameters (Sec. III.A-B)
mu = 469.46          # Proton-neutron reduced mass (MeV/c^2)
hbar_c = 197.327     # MeV * fm
V0 = 180.0           # Attractive gauge-well depth (MeV)
rc = 0.705           # Short-range smoothing scale (fm)
mu_pi = 1.0 / 1.41   # Sleeve screening inverse range (fm^-1)
V_core = 165.0       # Steric repulsive core amplitude (MeV)
r_hard = 0.45        # Hard-core Dirichlet inner boundary (fm)
R_box = 21.2         # Outer Dirichlet box boundary (fm)
N_grid = 4000        # Radial grid points

# Radial grid with Dirichlet boundary conditions: u(r_hard) = 0, u(R_box) = 0
r_all = np.linspace(r_hard, R_box, N_grid)
dr = r_all[1] - r_all[0]
r = r_all[1:-1]      # Interior grid points
N_in = len(r)

# Two-phase strong nuclear potential V_strong(r) = V_att(r) + V_rep(r) [Eqs. 8-9]
V_att = -V0 * (np.exp(-mu_pi * r) / (mu_pi * r)) * (1.0 - np.exp(-(r / rc) ** 2))
x_core = (r_hard / r) ** 2
V_rep = V_core * (x_core / (1.0 - x_core))
V_strong = V_att + V_rep

# Tridiagonal finite-difference Hamiltonian: -(hbar^2 / 2mu) u'' + V_strong(r) u = E u
kin = (hbar_c ** 2) / (2.0 * mu * (dr ** 2))
diag = 2.0 * kin + V_strong
off_diag = -kin * np.ones(N_in - 1)

# Solve for lowest eigenvalues and ground-state eigenvector
evals, evecs = eigh_tridiagonal(diag, off_diag, select="i", select_range=(0, 2))
E0, E1 = evals[0], evals[1]

u0 = evecs[:, 0]
if u0[0] < 0:
    u0 = -u0
u0 /= np.sqrt(np.sum(u0 ** 2) * dr)

# Expectation values <V>, <T>, and RMS matter radius r_cm = 0.5 * sqrt(<r^2>)
V_exp = np.sum((u0 ** 2) * V_strong) * dr
T_exp = E0 - V_exp
r_cm = 0.5 * np.sqrt(np.sum((u0 ** 2) * (r ** 2)) * dr)

print(f"Ground-State Binding Energy E0 : {E0:.3f} MeV  (Paper VI: -2.225 MeV)")
print(f"Kinetic Expectation <T>        : {T_exp:+.2f} MeV  (Paper VI: +10.17 MeV)")
print(f"Potential Expectation <V>      : {V_exp:+.2f} MeV  (Paper VI: -12.40 MeV)")
print(f"First Continuum State E1       : {E1:+.2f} MeV  (Paper VI: +1.80 MeV)")
print(f"RMS Matter Radius r_cm         : {r_cm:.3f} fm   (Paper VI: 2.103 fm)")