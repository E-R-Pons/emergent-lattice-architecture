# Emergent Lattice Architecture (ELA) Physics Engine & Simulation Payloads

**Author:** E. R. Pons (`er.pons.research@proton.me`)  
**PGP Fingerprint:** `EF67 9AE4 71F9 0157 0525  C228 DF85 35ED 268C 67B5`  
**Repository:** [https://github.com/E-R-Pons/emergent-lattice-architecture](https://github.com/E-R-Pons/emergent-lattice-architecture)  
**Zenodo DOI:** [10.5281/zenodo.24512307](https://doi.org/10.5281/zenodo.24512307)  

---

## Overview

This archive contains the official **ELA Physics Engine (`v6.6.2`)** source code (alongside legacy `v4.4.2` archival code), analysis scripts, and multi-seed Monte Carlo datasets supporting the six-part preprint series:

1. **Paper I:** *Emergent Lattice Architecture I: Foundations and Spacetime Emergence* (`10.5281/zenodo.24512071`)
2. **Paper II:** *Emergent Lattice Architecture II: Micro-Scale Physics, Gauges, and Interactions* (`10.5281/zenodo.24512165`)
3. **Paper III:** *Emergent Lattice Architecture III: Macro-Scale Cosmology, Dark Energy, and Cyclic Bounce* (`10.5281/zenodo.24512244`)
4. **Paper IV:** *Emergent Lattice Architecture IV: Substrate Thermodynamics, Geometrogenesis, and Non-Equilibrium Vacuum Kinetics* (`10.5281/zenodo.23268981`)
5. **Paper V:** *Emergent Lattice Architecture V: Relational Condensed Matter, Extreme Planetary Equations of State, and Topological Phase Kinetics* (`10.5281/zenodo.23269009`)
6. **Paper VI:** *Emergent Lattice Architecture VI: Relational Nuclear Topology, Multi-Baryon Bound States, and Topological Transmutation* (`10.5281/zenodo.24205610`)

The ELA engine simulates a background-independent dynamic graph $G(t)=(V,E(t))$ with vertex valence bound $n(v) \le 6$, link-tension capacity ceiling $\tau_{\max} \equiv 1/3$, and vacuum average expectation $\langle n\rangle_{\mathrm{vac}} = 4$. The production datasets record Metropolis–Hastings ensemble sampling across $N=32,768$ nodes over 50,000 sweeps per seed ($K=5$ seeds per mode), complemented by the deterministic deuteron radial boundary-value solver for Paper VI.

---

## File Structure

```text
.
├── LICENSE-CODE                            # MIT License for source code
├── LICENSE-DATA                            # CC-BY-4.0 License for datasets & manuscripts
├── README.md                               # Repository documentation
├── CHECKSUMS.sha256                        # Cryptographic SHA-256 file hashes
│
├── ela_engine/                             # ELA v6.6.2 simulation codebase
│   ├── analyze_ensemble.py                 # Diagnostic & plotting script
│   ├── main.py                             # Orchestrator, Argument Parser & Entry Point
│   ├── math_kernels.py                     # Pure C-Speed High-Performance Math Suite
│   ├── plotting.py                         # Publication-Ready Figure & Data Visualization Suite
│   ├── references.py                       # Master Citation Bibliography Data Payload
│   ├── simulation.py                       # Core MCMC Block, Lattice Builders & Protocol Drivers
│   ├── run_suite_32k.py                    # Production 32K benchmark suite orchestrator
│   ├── paper6_deuteron_radial_solver.py    # Deuteron Radial Schrödinger Boundary-Value Solver
│   └── README.py                           # Instructions to reproduce v6.6.2 payloads
│
└── payloads/                               # Compressed array datasets for v6.6.2
    ├── PROD_P1_VACUUM_SEED_*.npz           # Paper I: Vacuum spacetime runs
    ├── PROD_P2_SOLITON_Q1_SEED_*.npz       # Paper II: Skyrmion soliton runs
    ├── PROD_P3_COSMOLOGY_SEED_*.npz        # Paper III: Cosmological bounce runs
    ├── PROD_P4_FSS_SEED_*.npz              # Paper IV: Finite-size scaling (FSS) thermodynamic runs
    ├── PROD_P4_QUENCH_SEED_*.npz           # Paper IV: Non-equilibrium rapid quench geometrogenesis runs
    ├── PROD_P4_SWEEP_SEED_*.npz            # Paper IV: Temperature & coupling parameter sweep runs
    ├── PROD_P5_CARBON_SEED_*.npz           # Paper V: Diamond/graphene covalent sleeve & band runs
    ├── PROD_P5_H20_SEED_*.npz              # Paper V: Hydrogen-bonded water/ice network kinetics
    ├── PROD_P5_HYDROSTATIC_SEED_*.npz      # Paper V: High-pressure hydrostatic compression EOS runs
    ├── PROD_P5_SATURATION_SEED_*.npz       # Paper V: Link-tension capacity ceiling (tau -> 1/3) runs
    └── PROD_P5_SUPERIONIC_SEED_*.npz       # Paper V: Extreme planetary superionic transition runs

```

---

## Dataset Registry

| File Pattern | Paper | Target Physics | Logged Observables |
| :--- | :--- | :--- | :--- |
| `PROD_P1_VACUUM_SEED_*.npz` | Paper I | Unperturbed Vacuum Spacetime | `ds_curve` ($d_s$), `energy_history` ($H_{\text{tot}}$), `ds_final`, `topological_charge_Q`, `su2_plaquette_action` |
| `PROD_P2_SOLITON_Q1_SEED_*.npz` | Paper II | $SU(2)$ Skyrmion ($Q=+1$) | `ds_curve` ($d_s$), `q_history` ($Q_{\text{top}}$), `splaq_history` ($S_{\text{plaq}}$), `energy_history` ($H_{\text{tot}}$), `bps_soliton_mass` |
| `PROD_P3_COSMOLOGY_SEED_*.npz` | Paper III | Cosmological Bounce & Expansion | `ds_curve` ($d_s$), `w_eos_history` ($w(a)$), `h_sq_history` ($H^2$), `energy_history` ($H_{\text{tot}}$), `su2_plaquette_action` |
| `PROD_P4_FSS_SEED_*.npz` | Paper IV | Finite-Size Scaling & Criticality | `ds_curve` ($d_s$), `energy_history` ($H_{\text{tot}}$), specific heat $C_V$, susceptibility $\chi_G$, valence distribution $P(n)$ |
| `PROD_P4_QUENCH_SEED_*.npz` | Paper IV | Non-Equilibrium Quench Geometrogenesis | `ds_curve` ($d_s(t)$), `energy_history` ($H_{\text{tot}}(t)$), WWW swap acceptance rate, defect relaxation time |
| `PROD_P4_SWEEP_SEED_*.npz` | Paper IV | Substrate Thermal & Coupling Sweeps | `ds_final`, `energy_history` ($H_{\text{tot}}$), `su2_plaquette_action`, order-parameter phase curves |
| `PROD_P5_CARBON_SEED_*.npz` | Paper V | Covalent Diamond/Graphene Sleeves | `energy_history` ($H_{\text{tot}}$), sleeve overlap $S_{ij}$, holonomy jamming $\mathcal{V}_{\text{jam}}$, shear stiffness |
| `PROD_P5_H20_SEED_*.npz` | Paper V | Hydrogen-Bonded Network Kinetics | `energy_history` ($H_{\text{tot}}$), directional bond-angle torsion $H_{\text{torsion}}$, H-bond rewiring rate |
| `PROD_P5_HYDROSTATIC_SEED_*.npz` | Paper V | High-Pressure Hydrostatic EOS | Pressure–volume $P(V)$, bulk modulus $K_0$, `energy_history` ($H_{\text{tot}}$), mean link tension $\langle \tau_e \rangle$ |
| `PROD_P5_SATURATION_SEED_*.npz` | Paper V | Link-Tension Ceiling ($\tau_{\max} \equiv 1/3$) | Max link tension $\max(\tau_e)$, steric repulsion wall onset, valence saturation $n(v) \to 6$ |
| `PROD_P5_SUPERIONIC_SEED_*.npz` | Paper V | Planetary Superionic Ice Transition | Sublattice proton diffusivity $D_{\text{H}^+}$, host oxygen rigidity, $\mathcal{V}_{\text{jam}}$, `energy_history` |

---

## Citation

```bibtex
@dataset{pons_2026_ela_engine,
  author       = {Pons, E. R.},
  title        = {{Emergent Lattice Architecture (ELA) Physics Engine 
                   v6.6.2 Simulation Data and Analysis Scripts}},
  month        = nov,
  year         = 2026,
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.24512307},
  url          = {[https://doi.org/10.5281/zenodo.24512307](https://doi.org/10.5281/zenodo.24512307)}
}
```

---

## License

* **Source Code (`ela_engine/`):** [MIT License](LICENSE-CODE)
* **Datasets & Data Payloads (`payloads/`):** [Creative Commons Attribution 4.0 International (CC BY 4.0)](LICENSE-DATA)
