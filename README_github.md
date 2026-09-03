# Emergent Lattice Architecture (ELA) Physics Engine & Simulation Payloads

**Author:** E. R. Pons
**PGP Fingerprint:** `EF67 9AE4 71F9 0157 0525  C228 DF85 35ED 268C 67B5`
**Repository:** [https://github.com/E-R-Pons/emergent-lattice-architecture](https://github.com/E-R-Pons/emergent-lattice-architecture)
**Zenodo DOI:** [10.5281/zenodo.21843390](https://doi.org/10.5281/zenodo.21843390)  

---

## Overview

This archive contains the official **ELA Physics Engine (`v4.4.2`)** source code, analysis scripts, and multi-seed Monte Carlo datasets supporting the paper trilogy:

1. *Emergent Lattice Architecture I: Foundations and Spacetime Emergence* (https://doi.org/10.5281/zenodo.21843307)
2. *Emergent Lattice Architecture II: Micro-Scale Physics, Gauges, and Interactions* (https://doi.org/10.5281/zenodo.21843352)
3. *Emergent Lattice Architecture III: Macro-Scale Cosmology, Dark Energy, and Cyclic Bounce* (https://doi.org/10.5281/zenodo.21843375)

The ELA engine simulates a background-independent dynamic graph $G(t)=(V,E(t))$ with vertex valence bound $n(v) \le 6$ and vacuum average expectation $\langle n\rangle_{vac} = 4$. The production datasets record Metropolis-Hastings ensemble sampling across $N=32,768$ nodes over 50,000 sweeps per seed ($K=8$ seeds per mode).

---

## File Structure

```text
.
├── LICENSE-CODE                        # MIT License for source code
├── LICENSE-DATA                        # CC-BY-4.0 License for datasets & manuscripts
├── README.md                           # Repository documentation
├── CHECKSUMS.sha256                    # Cryptographic SHA-256 file hashes
│
├── ela_engine/                         # ELA v4.4.2 simulation codebase
│   ├── ela_engine_v442.py              # Simulation Engine
│   ├── run_ensemble_parallel.py        # Parallel multi-seed production orchestrator
│   └── analyze_ensemble.py             # Diagnostic & plotting script
│
└── payloads/                           # Compressed array datasets
    ├── PROD_P1_VACUUM_SEED_*.npz       # Paper I: Vacuum spacetime runs
    ├── PROD_P2_SOLITON_Q1_SEED_*.npz   # Paper II: Skyrmion soliton runs
    └── PROD_P3_COSMOLOGY_SEED_*.npz    # Paper III: Cosmological bounce runs
```

---

## Dataset Registry

| File Pattern | Paper | Target Physics | Logged Observables |
| :--- | :--- | :--- | :--- |
| `PROD_P1_VACUUM_SEED_*.npz` | Paper I | Unperturbed Vacuum Spacetime | `ds_curve` ($d_s$), `energy_history` ($H_{\text{tot}}$), `ds_final`, `topological_charge_Q`, `su2_plaquette_action` |
| `PROD_P2_SOLITON_Q1_SEED_*.npz` | Paper II | $SU(2)$ Skyrmion ($Q=+1$) | `ds_curve` ($d_s$), `q_history` ($Q_{\text{top}}$), `splaq_history` ($S_{\text{plaq}}$), `energy_history` ($H_{\text{tot}}$), `bps_soliton_mass` |
| `PROD_P3_COSMOLOGY_SEED_*.npz` | Paper III | Cosmological Bounce & Expansion | `ds_curve` ($d_s$), `w_eos_history` ($w(a)$), `h_sq_history` ($H^2$), `energy_history` ($H_{\text{tot}}$), `su2_plaquette_action` |

---

## Citation

```bibtex
@dataset{pons_2026_ela_engine,
  author       = {Pons, E. R.},
  title        = {{Emergent Lattice Architecture (ELA) Physics Engine 
                   v4.4.2 Simulation Data and Analysis Scripts}},
  month        = aug,
  year         = 2026,
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.21843390},
  url          = {[https://doi.org/10.5281/zenodo.21843390](https://doi.org/10.5281/zenodo.21843390)}
}
```

---

## License

* **Source Code (`ela_engine/`):** [MIT License](LICENSE-CODE)
* **Datasets & Data Payloads (`payloads/`):** [Creative Commons Attribution 4.0 International (CC BY 4.0)](LICENSE-DATA)
