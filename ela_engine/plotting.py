#!/usr/bin/env python3
"""
================================================================================
EMERGENT LATTICE ARCHITECTURE (ELA) - AUTOMATED DIAGNOSTIC PLOTTING ENGINE
================================================================================
Module 3 of 5: Publication-Ready Figure & Data Visualization Suite (plotting.py v6.6.2)

Provenance: [ELA VISUALIZATION]
References:
  - Paper I   [ela_paper_i_2026]   : Foundations, Hydrodynamic Limits & Spacetime Emergence (DOI: 10.5281/zenodo.21843307)
  - Paper II  [ela_paper_ii_2026]  : Micro-Scale Soliton Topology, Gauges & Antimatter (DOI: 10.5281/zenodo.21843352)
  - Paper III [ela_paper_iii_2026] : Macro Cosmological Untensing, Geometrogenesis & Dark Energy (DOI: 10.5281/zenodo.21843375)
  - Paper IV  [ela_paper_iv_2026]  : Substrate Thermodynamics & Vacuum Kinetics (DOI: 10.5281/zenodo.23268981)
  - Paper V   [ela_paper_v_2026]   : Relational Condensed Matter & Extreme EoS (DOI: 10.5281/zenodo.23269009)
"""

import os
import math
import json
import numpy as np
import matplotlib.pyplot as plt

# Local module import [ELA VISUALIZATION]
from references import __references__


def fmt_sci_tex(val: float) -> str:
    """
    Formats floating-point numbers into clean LaTeX exponential notation for matplotlib labels.
    
    Provenance: [ELA VISUALIZATION]
    Format    : x.xx \times 10^{exponent}
    """
    if val == 0 or not np.isfinite(val):
        return "0.00"
    exponent = int(np.floor(np.log10(abs(val))))
    coeff = val / (10 ** exponent)
    return f"{coeff:.2f} \\times 10^{{{exponent}}}"


def generate_diagnostics_plot(npz_filename: str, out_dir: str = ".") -> None:
    """
    Generates publication-ready multi-panel diagnostic figures across Modes 1-5 using Matplotlib.
    
    Provenance: [ELA VISUALIZATION]
    References:
      - Mode 1 Vacuum [ela_paper_i_2026]: Continuum spectral dimension & thermalization.
      - Mode 2 Soliton [ela_paper_ii_2026]: Topological charge Q_top & Wilson plaquette action.
      - Mode 3 Cosmo [ela_paper_iii_2026]: Dark energy w(a) & LQC Hubble bounce profiles.
      - Mode 4 Thermo [binder_heermann_2010, ela_paper_iv_2026]: Fluctuation-Dissipation C_V & latent heat.
      - Mode 5 Matter [ela_paper_v_2026]: Relational Strain Saturation & Superionic Diffusion.
    """
    if not os.path.exists(npz_filename):
        print(f"[ERROR] Cannot plot: File '{npz_filename}' not found.")
        return

    data = np.load(npz_filename, allow_pickle=True)
    run_id = str(data["run_id"]) if "run_id" in data else "RUN_V620"
    mode_str = str(data["mode"]) if "mode" in data else "PAPER1_VACUUM"
    seed_val = str(data["seed"]) if "seed" in data else "N/A"
    safe_id = run_id.replace("/", "_").replace("\\", "_")

    # --------------------------------------------------------------------------
    # MODE 5: PAPER 5 RELATIONAL CONDENSED MATTER DIAGNOSTICS [ELA ADAPTED]
    # --------------------------------------------------------------------------
    if mode_str == "PAPER5_CONDENSED_MATTER":
        cond_mode_str = str(data["condensed_mode"]) if "condensed_mode" in data else "HYDROSTATIC_COMPRESSION"
        fig, axs = plt.subplots(2, 2, figsize=(12, 9), dpi=200)
        (ax1, ax2), (ax3, ax4) = axs

        if cond_mode_str == "HYDROSTATIC_COMPRESSION":
            P_arr = data["P_ext_array"]
            vol_arr = data["volume_array"] if "volume_array" in data else data["volume_response"]
            strain_arr = data["mean_strain_array"] if "mean_strain_array" in data else np.zeros_like(P_arr)
            P_cap = data["capacity_P_array"] if "capacity_P_array" in data else np.ones_like(P_arr)

            ax1.plot(P_arr, vol_arr, color='#1f77b4', marker='o', lw=2, label=r'Volume $V(P)$')
            ax1.set_xlabel(r'External Pressure $P_{\mathrm{ext}}$ (GPa)')
            ax1.set_ylabel(r'Effective Volume $V$')
            ax1.set_title(r'(a) Hydrostatic Volume Contraction')
            ax1.grid(True, linestyle=':', alpha=0.6)
            ax1.legend(loc='upper right')

            ax2.plot(P_arr, strain_arr, color='#d62728', marker='s', lw=2, label=r'Mean Link Strain $\langle \tau \rangle$')
            ax2.axhline(1.0 / 3.0, color='darkred', linestyle='--', lw=1.5, label=r'Capacity Ceiling $\tau_{\mathrm{max}} = 1/3$')
            ax2.set_xlabel(r'External Pressure $P_{\mathrm{ext}}$ (GPa)')
            ax2.set_ylabel(r'Link Strain $\langle \tau \rangle$')

            # Dynamic Y-axis limit adjustment to prevent clipping
            max_measured_strain = float(np.max(strain_arr)) if len(strain_arr) > 0 else 0.33
            ax2.set_ylim(0.0, max(0.40, max_measured_strain * 1.15))

            ax2.set_title(r'(b) Relational Strain Saturation')
            ax2.grid(True, linestyle=':', alpha=0.6)
            ax2.legend(loc='upper right')

            ax3.plot(P_arr, np.maximum(P_cap, 1e-6), color='#ff7f0e', marker='^', lw=2, label=r'Capacity $P(\tau)$ Response')
            ax3.set_yscale('log')
            ax3.set_xlabel(r'External Pressure $P_{\mathrm{ext}}$ (GPa)')
            ax3.set_ylabel(r'Non-Singular Resistance Factor')
            ax3.set_title(r'(c) Capacity-Bound Divergence Resistance')
            ax3.grid(True, which='both', linestyle=':', alpha=0.6)
            ax3.legend(loc='upper left')

            # Thermodynamic Bulk Modulus K(P) = -V (dP/dV)
            sort_idx = np.argsort(P_arr)
            p_s = np.asarray(P_arr)[sort_idx]
            v_s = np.asarray(vol_arr)[sort_idx]
            dv_dp = np.gradient(v_s, p_s)
            dv_dp_safe = np.where(np.abs(dv_dp) < 1e-12, -1e-12, dv_dp)
            bulk_modulus = -v_s * (1.0 / dv_dp_safe)

            ax4.plot(p_s, np.maximum(bulk_modulus, 1e-3), color='#2ca02c', marker='d', lw=2, label=r'Bulk Modulus $K(P)$')
            ax4.set_yscale('log')
            ax4.set_xlabel(r'External Pressure $P_{\mathrm{ext}}$ (GPa)')
            ax4.set_ylabel(r'Bulk Modulus $K$ (GPa)')
            ax4.set_title(r'(d) Emergent Incompressibility ($K \to \infty$)')
            ax4.grid(True, which='both', linestyle=':', alpha=0.6)
            ax4.legend(loc='lower right')

        elif cond_mode_str == "PHASE_DIAGRAM_H2O":
            T_arr = data["temp_array"]
            Dp_arr = data["D_p_array"]
            S_ij_arr = data["sleeve_overlap_array"]

            ax1.plot(T_arr, np.maximum(Dp_arr, 1e-12), color='#9467bd', marker='o', lw=2, label=r'Proton Diffusion $D_p$')
            ax1.set_yscale('log')
            ax1.set_xlabel(r'Temperature $T_{\mathrm{emergent}}$ (K)')
            ax1.set_ylabel(r'Diffusion Coefficient $D_p$')
            ax1.set_title(r'(a) Superionic Proton Diffusion Onset')
            ax1.grid(True, which='both', linestyle=':', alpha=0.6)
            ax1.legend(loc='lower right')

            ax2.plot(T_arr, S_ij_arr, color='#8c564b', marker='s', lw=2, label=r'Sleeve Overlap $\langle S_{ij} \rangle$')
            ax2.set_xlabel(r'Temperature $T_{\mathrm{emergent}}$ (K)')
            ax2.set_ylabel(r'Overlap Integral $S_{ij}$')
            ax2.set_title(r'(b) Multi-Soliton Sleeve Overlap Integral')
            ax2.grid(True, linestyle=':', alpha=0.6)
            ax2.legend(loc='upper right')

            ax3.plot(T_arr, Dp_arr * S_ij_arr, color='#e377c2', lw=2, label=r'Ionic Flux Product')
            ax3.set_xlabel(r'Temperature $T_{\mathrm{emergent}}$ (K)')
            ax3.set_ylabel(r'$D_p \cdot S_{ij}$')
            ax3.set_title(r'(c) Coupled Superionic Phase Kinetics')
            ax3.grid(True, linestyle=':', alpha=0.6)
            ax3.legend(loc='upper left')

            p_ext_val = float(data['P_ext']) if 'P_ext' in data else 150.0
            ax4.text(0.5, 0.5, f"H2O Phase Kinetics\n$P={p_ext_val:.1f}$ GPa\nRun ID: {run_id}", ha='center', va='center', transform=ax4.transAxes, fontsize=11)
            ax4.set_title(r'(d) System Phase Bounds')

        elif cond_mode_str == "DIAMOND_RAIN_CARBON":
            sweeps = data["sweeps_log"]
            shear_h = data["shear_history"]
            torsion_h = data["torsion_history"]
            p_ext_val = float(data['P_ext']) if 'P_ext' in data else 300.0

            ax1.plot(sweeps, shear_h, color='#1f77b4', lw=2, label=r'$\langle H_{\mathrm{shear}} \rangle / N$')
            ax1.set_xlabel(r'Monte Carlo Sweep (MCS)')
            ax1.set_ylabel(r'Shear Energy Density (J/node)')
            ax1.set_title(r'(a) Valence Shear Strain Minimization')
            ax1.grid(True, linestyle=':', alpha=0.6)
            ax1.legend(loc='upper right')

            ax2.plot(sweeps, torsion_h, color='#ff7f0e', lw=2, label=r'$\langle H_{\mathrm{torsion}} \rangle / N$')
            ax2.set_xlabel(r'Monte Carlo Sweep (MCS)')
            ax2.set_ylabel(r'Torsion Energy Density (J/node)')
            ax2.set_title(r'(b) Dihedral Torsion Strain Relaxation')
            ax2.grid(True, linestyle=':', alpha=0.6)
            ax2.legend(loc='upper right')

            ax3.plot(sweeps, shear_h + torsion_h, color='#2ca02c', lw=2, label=r'Total Valence Energy')
            ax3.set_xlabel(r'Monte Carlo Sweep (MCS)')
            ax3.set_ylabel(r'Valence Strain (J/node)')
            ax3.set_title(r'(c) Total Diamond Valence Energy Relaxation')
            ax3.grid(True, linestyle=':', alpha=0.6)
            ax3.legend(loc='upper right')

            ax4.text(0.5, 0.5, f"Carbon Diamond Rain\n$P={p_ext_val:.1f}$ GPa\nRun ID: {run_id}", ha='center', va='center', transform=ax4.transAxes, fontsize=11)
            ax4.set_title(r'(d) Carbon Valence State Summary')

        elif cond_mode_str == "SUPERIONIC_ONSET":
            time_log = data["time_log"]
            msd_log = data["msd_log"]
            dp_log = data["dp_log"]
            temp_val = float(data['temp_val']) if 'temp_val' in data else 2500.0
            p_ext_val = float(data['P_ext']) if 'P_ext' in data else 150.0

            ax1.plot(time_log, msd_log, color='#d62728', marker='o', lw=2, label=r'Proton Knot MSD')
            ax1.set_xlabel(r'Monte Carlo Sweep (MCS)')
            ax1.set_ylabel(r'Mean Squared Displacement ($r_0^2$)')
            ax1.set_title(r'(a) Proton Knot Mean Squared Displacement')
            ax1.grid(True, linestyle=':', alpha=0.6)
            ax1.legend(loc='upper left')

            ax2.plot(time_log, dp_log, color='#9467bd', marker='s', lw=2, label=r'Diffusion Rate $D_p$')
            ax2.set_xlabel(r'Monte Carlo Sweep (MCS)')
            ax2.set_ylabel(r'Proton Diffusion Coefficient $D_p$')
            ax2.set_title(r'(b) Superionic Proton Diffusion Kinetics')
            ax2.grid(True, linestyle=':', alpha=0.6)
            ax2.legend(loc='upper right')

            ax3.plot(msd_log, dp_log, color='#17becf', lw=2, label=r'Diffusion vs MSD Trajectory')
            ax3.set_xlabel(r'MSD ($r_0^2$)')
            ax3.set_ylabel(r'Diffusion Coefficient $D_p$')
            ax3.set_title(r'(c) Diffusion Phase Trajectory')
            ax3.grid(True, linestyle=':', alpha=0.6)
            ax3.legend(loc='upper right')

            ax4.text(0.5, 0.5, f"Superionic Proton Diffusion Onset\n$T={temp_val:.1f}$ K | $P={p_ext_val:.1f}$ GPa\nRun ID: {run_id}", ha='center', va='center', transform=ax4.transAxes, fontsize=11)
            ax4.set_title(r'(d) Superionic State Boundary')

        elif cond_mode_str == "CAPACITY_SATURATION":
            strain_arr = data["strain_array"]
            p_eos_arr = data["pressure_eos_array"]
            rho_ratio_arr = data["density_ratio_array"]

            ax1.plot(strain_arr, p_eos_arr, color='#1f77b4', marker='o', lw=2, label=r'Pressure Response $P(\tau)$')
            ax1.axvline(1.0 / 3.0, color='darkred', linestyle='--', label=r'Capacity Boundary $\tau_{\mathrm{max}} = 1/3$')
            ax1.set_xlabel(r'Shear Strain $\tau$')
            ax1.set_ylabel(r'Capacity EOS Pressure $P_{\mathrm{eos}}$')
            ax1.set_title(r'(a) Capacity-Saturated Equation of State')
            ax1.grid(True, linestyle=':', alpha=0.6)
            ax1.legend(loc='upper left')

            ax2.plot(strain_arr, rho_ratio_arr, color='#2ca02c', marker='s', lw=2, label=r'Density Ratio $\rho / \rho_{\mathrm{sat}}$')
            ax2.axhline(1.0, color='red', linestyle='--', label=r'Saturation Ceiling $\rho / \rho_{\mathrm{sat}} = 1.0$')
            ax2.set_xlabel(r'Shear Strain $\tau$')
            ax2.set_ylabel(r'Relative Density $\rho / \rho_{\mathrm{sat}}$')
            ax2.set_title(r'(b) Normalized Density Ratio Saturation')
            ax2.grid(True, linestyle=':', alpha=0.6)
            ax2.legend(loc='lower right')

            ax3.plot(rho_ratio_arr, np.maximum(p_eos_arr, 1e-6), color='#d62728', marker='^', lw=2, label=r'$P_{\mathrm{eos}}(\rho/\rho_{\mathrm{sat}})$')
            ax3.set_yscale('log')
            ax3.set_xlabel(r'Density Ratio $\rho / \rho_{\mathrm{sat}}$')
            ax3.set_ylabel(r'Divergent Pressure Factor $P_{\mathrm{eos}}$')
            ax3.set_title(r'(c) Asymptotic Density Barrier Divergence')
            ax3.grid(True, which='both', linestyle=':', alpha=0.6)
            ax3.legend(loc='upper left')

            ax4.text(0.5, 0.5, f"Non-Singular Capacity Saturation\nMax Density Limit: $\\rho \\to \\rho_{{sat}}$\nRun ID: {run_id}", ha='center', va='center', transform=ax4.transAxes, fontsize=11)
            ax4.set_title(r'(d) Substrate Density Horizon')

        else:
            ax1.text(0.5, 0.5, f"Mode 5 Protocol: {cond_mode_str}\nRun ID: {run_id}", ha='center', va='center', transform=ax1.transAxes)

        plt.tight_layout()
        plt.subplots_adjust(top=0.92)
        plt.suptitle(f"Mode 5 Condensed Matter ({run_id}) - {cond_mode_str}", y=0.98)
        plot_filename = os.path.join(out_dir, f"{safe_id}_mode5_{cond_mode_str}_seed{seed_val}_v620_diagnostics.png")
        plt.savefig(plot_filename)
        print(f"[PLOT] Mode 5 diagnostic plot saved to '{plot_filename}'")
        plt.close()
        return

    # --------------------------------------------------------------------------
    # MODE 4: PAPER 4 THERMODYNAMICS DIAGNOSTICS [PURE LITERATURE]
    # --------------------------------------------------------------------------
    if mode_str == "PAPER4_THERMODYNAMICS":
        thermo_mode_str = str(data["thermo_mode"]) if "thermo_mode" in data else "BETA_SWEEP"

        if thermo_mode_str == "BETA_SWEEP":
            fig, axs = plt.subplots(2, 2, figsize=(12, 9), dpi=200)
            (ax1, ax2), (ax3, ax4) = axs

            beta_arr = data["beta_array"]
            cv_arr = data["cv_profile"]
            dh_arr = data["dh_profile"]
            q_geom = float(data["q_geom_latent_heat"])

            ax1.plot(beta_arr, cv_arr, color='#d62728', marker='o', lw=2, label=r'Specific Heat $C_V(\beta_{\mathrm{eff}})$')
            ax1.axvline(2.15, color='gray', linestyle='--', label=r'Critical Boundary $\beta_{\mathrm{crit}} \approx 2.15$')
            ax1.set_xlabel(r'Inverse Noise Floor $\beta_{\mathrm{eff}}$')
            ax1.set_ylabel(r'Specific Heat $C_V$ (FDT)')
            ax1.set_title(f'(a) Geometrogenesis Specific Heat Peak\nLatent Heat $q_{{geom}} = {q_geom:.4f}$ J/node')
            ax1.grid(True, linestyle=':', alpha=0.6)
            ax1.legend(loc='upper right')

            ax2.plot(beta_arr, dh_arr, color='#1f77b4', marker='s', lw=2, label=r'Spectral Dim $\langle d_s \rangle$')
            ax2.axhline(3.00, color='#2ca02c', linestyle='--', label=r'3D Metric Boundary ($d_s = 3.0$)')
            ax2.set_xlabel(r'Inverse Noise Floor $\beta_{\mathrm{eff}}$')
            ax2.set_ylabel(r'Spectral Dimension $d_s$')
            ax2.set_title(r'(b) Spatial Dimension Condensation')
            ax2.grid(True, linestyle=':', alpha=0.6)
            ax2.legend(loc='lower right')

            if "h_comp_history" in data:
                h_comps = data["h_comp_history"]
                ax3.plot(beta_arr, h_comps[:, 1], color='#ff7f0e', lw=2, label=r'$\langle H_{\mathrm{shear}} \rangle$')
                ax3.plot(beta_arr, h_comps[:, 2], color='#9467bd', lw=2, label=r'$\langle H_{\mathrm{torsion}} \rangle$')
                ax3.plot(beta_arr, h_comps[:, 3], color='#2ca02c', lw=2, label=r'$\langle \mathcal{V}_{\mathrm{jam}} \rangle$')
                ax3.set_ylabel(r'Energy / Node (J)')
            else:
                ax3.text(0.5, 0.5, "Component Breakdown\nLogged in v6.0.0+", ha='center', va='center', transform=ax3.transAxes)
            ax3.set_xlabel(r'Inverse Noise Floor $\beta_{\mathrm{eff}}$')
            ax3.set_title(r'(c) Substrate Energy Component Relaxation')
            ax3.grid(True, linestyle=':', alpha=0.6)
            ax3.legend(loc='upper right')

            if "acc_history" in data:
                accs = data["acc_history"]
                ax4.plot(beta_arr, accs[:, 0], color='#1f77b4', lw=2, label=r'Spatial ($\mathrm{Acc}_{\mathrm{sp}}$)')
                ax4.plot(beta_arr, accs[:, 1], color='#ff7f0e', lw=2, label=r'Gauge ($\mathrm{Acc}_{\mathrm{g}}$)')
                ax4.plot(beta_arr, accs[:, 2], color='#d62728', lw=2, label=r'Pachner Swap ($\mathrm{Acc}_{\mathrm{topo}}$)')
            else:
                ax4.text(0.5, 0.5, "Acceptance Stream\nLogged in v6.0.0+", ha='center', va='center', transform=ax4.transAxes)
            ax4.set_xlabel(r'Inverse Noise Floor $\beta_{\mathrm{eff}}$')
            ax4.set_ylabel(r'Acceptance Rate (%)')
            ax4.set_title(r'(d) MCMC Phase Mobility & Transition Rates')
            ax4.grid(True, linestyle=':', alpha=0.6)
            ax4.legend(loc='upper right')

            plt.tight_layout()
            plt.subplots_adjust(top=0.92)
            plt.suptitle(f"Mode 4: Substrate Geometrogenesis Beta Sweep ({run_id})", y=0.98)

        elif thermo_mode_str == "QUENCH_KINETICS":
            fig, axs = plt.subplots(2, 2, figsize=(12, 9), dpi=200)
            (ax1, ax2), (ax3, ax4) = axs

            sweeps_arr = data["sweeps_arr"]
            strain_arr = data["strain_arr"]
            gamma_tau = float(data["quench_gamma_tau"])
            ds_arr = data["ds_arr"] if "ds_arr" in data else np.full_like(sweeps_arr, 3.0)
            energy_arr = data["energy_arr"] if "energy_arr" in data else np.zeros_like(sweeps_arr)
            tau_eq = float(data["tau_eq"]) if "tau_eq" in data else float(np.min(strain_arr))

            ax1.plot(sweeps_arr, ds_arr, color='#1f77b4', lw=2, label=r'Measured $d_s(t)$')
            ax1.axhline(3.00, color='#2ca02c', linestyle='--', label=r'3D Spatial Boundary ($d_s = 3.00$)')
            ax1.set_xlabel(r'Monte Carlo Sweep (MCS)')
            ax1.set_ylabel(r'Spectral Dimension $d_s$')
            ax1.set_title(f'(a) Metric Continuity During Quench\nFinal $d_s = {ds_arr[-1]:.4f}$')
            ax1.grid(True, linestyle=':', alpha=0.6)
            ax1.legend(loc='lower right')

            ax2.plot(sweeps_arr, strain_arr, color='#ff7f0e', lw=2, label=r'Mean Strain $\langle \tau(t) \rangle$')
            ax2.axhline(tau_eq, color='red', linestyle=':', label=f'Equilibrium $\\tau_{{eq}} = {tau_eq:.4f}$')
            ax2.set_xlabel(r'Monte Carlo Sweep (MCS)')
            ax2.set_ylabel(r'Shear Strain Energy $\langle \tau \rangle$')
            ax2.set_title(f'(b) Viscoelastic Strain Relaxation Profile\n$\\Gamma_\\tau = {fmt_sci_tex(gamma_tau)}$')
            ax2.grid(True, linestyle=':', alpha=0.6)
            ax2.legend(loc='upper right')

            fit_mask = (strain_arr - tau_eq) > 1e-5
            if np.sum(fit_mask) > 1:
                log_delta = np.log(strain_arr[fit_mask] - tau_eq)
                ax3.plot(sweeps_arr[fit_mask], log_delta, color='#9467bd', marker='o', ms=3, lw=2, label=r'Log Decay $\ln(\langle \tau \rangle - \tau_{\mathrm{eq}})$')
            ax3.set_xlabel(r'Monte Carlo Sweep (MCS)')
            ax3.set_ylabel(r'$\ln(\langle \tau(t) \rangle - \tau_{\mathrm{eq}})$')
            ax3.set_title(f'(c) Transient Exponential Decay Fit')
            ax3.grid(True, linestyle=':', alpha=0.6)
            ax3.legend(loc='upper right')

            ax4.plot(sweeps_arr, energy_arr, color='#d62728', lw=2, label=r'Total Energy $H_{\mathrm{tot}}$')
            ax4.set_xlabel(r'Monte Carlo Sweep (MCS)')
            ax4.set_ylabel(r'Total Hamiltonian $H_{\mathrm{tot}}$')
            ax4.set_title(f'(d) Strain Energy Dissipation')
            ax4.grid(True, linestyle=':', alpha=0.6)
            ax4.legend(loc='upper right')

            plt.tight_layout()
            plt.subplots_adjust(top=0.92)
            plt.suptitle(f"Mode 4: Substrate Viscoelastic Quench ({run_id})", y=0.98)

        elif thermo_mode_str == "FSS_ANALYSIS":
            fig, axs = plt.subplots(2, 2, figsize=(12, 9), dpi=200)
            (ax1, ax2), (ax3, ax4) = axs

            fss_json_str = str(data["fss_results_json"])
            fss_dict = json.loads(fss_json_str)

            volumes = sorted([int(k) for k in fss_dict.keys()])
            cv_maxs = [fss_dict[str(v)]["cv_max"] for v in volumes]
            beta_peaks = [fss_dict[str(v)]["beta_peak"] for v in volumes]
            q_geoms = [fss_dict[str(v)]["q_geom"] for v in volumes]

            # (a) Peak Specific Heat Scaling
            ax1.plot(volumes, cv_maxs, color='#9467bd', marker='o', lw=2, ms=6, label=r'Measured $C_{V,\mathrm{max}}(N)$')
            ax1.set_xscale('log')
            if len(cv_maxs) > 0 and min(cv_maxs) > 0:
                ax1.set_yscale('log')
            ax1.set_xlabel(r'Lattice Volume $N_{\mathrm{nodes}}$')
            ax1.set_ylabel(r'Peak Specific Heat $C_{V,\mathrm{max}}$')
            ax1.set_title(r'(a) Finite-Size Scaling ($C_{V,\mathrm{max}} \propto N$)')
            ax1.grid(True, which='both', linestyle=':', alpha=0.6)
            ax1.legend(loc='upper left')

            # (b) Critical Noise Floor Shift
            ax2.plot(volumes, beta_peaks, color='#2ca02c', marker='s', lw=2, ms=6, label=r'$\beta_{\mathrm{peak}}(N)$')
            ax2.set_xscale('log')
            ax2.set_xlabel(r'Lattice Volume $N_{\mathrm{nodes}}$')
            ax2.set_ylabel(r'Critical Noise Floor $\beta_{\mathrm{peak}}$')
            ax2.set_title(r'(b) Critical Boundary Position $\beta_{\mathrm{crit}}(N)$')
            ax2.grid(True, linestyle=':', alpha=0.6)
            ax2.legend(loc='upper right')

            # (c) Order Parameter Condensation profiles across N
            colors = ['#1f77b4', '#ff7f0e', '#d62728', '#9467bd', '#8c564b']
            has_dh_data = False
            for idx, v in enumerate(volumes):
                v_data = fss_dict[str(v)]
                if "beta_arr" in v_data and "dh_arr" in v_data:
                    has_dh_data = True
                    b_arr = np.array(v_data["beta_arr"])
                    d_arr = np.array(v_data["dh_arr"])
                    c_col = colors[idx % len(colors)]
                    ax3.plot(b_arr, d_arr, color=c_col, marker='s', ms=4, lw=1.5, label=f'$N = {v:,}$')

            if has_dh_data:
                ax3.axhline(3.00, color='#2ca02c', linestyle='--', label=r'3D Boundary ($d_s = 3.0$)')
                ax3.set_xlabel(r'Inverse Noise Floor $\beta_{\mathrm{eff}}$')
                ax3.set_ylabel(r'Spectral Dimension $\langle d_s \rangle$')
                ax3.set_title(r'(c) Order Parameter Condensation $d_s(\beta_{\mathrm{eff}})$')
                ax3.grid(True, linestyle=':', alpha=0.6)
                ax3.legend(loc='lower right')
            else:
                ax3.text(0.5, 0.5, f"FSS Active Volumes: {volumes}\nRun ID: {run_id}", ha='center', va='center', transform=ax3.transAxes)
                ax3.set_title(r'(c) Order Parameter Condensation $d_s(\beta_{\mathrm{eff}})$')

            # (d) Specific Structural Latent Heat Volume Convergence
            ax4.plot(volumes, q_geoms, color='#e377c2', marker='^', lw=2, ms=6, label=r'$q_{\mathrm{geom}}(N)$')
            ax4.set_xscale('log')
            ax4.set_xlabel(r'Lattice Volume $N_{\mathrm{nodes}}$')
            ax4.set_ylabel(r'Latent Heat $q_{\mathrm{geom}}$ (J/node)')
            ax4.set_title(r'(d) Latent Heat Volume Convergence')
            ax4.grid(True, linestyle=':', alpha=0.6)
            ax4.legend(loc='upper right')

            plt.tight_layout()
            plt.subplots_adjust(top=0.92)
            plt.suptitle(f"Mode 4: Substrate Finite-Size Scaling FSS ({run_id})", y=0.98)

        plot_filename = os.path.join(out_dir, f"{safe_id}_mode4_{thermo_mode_str}_seed{seed_val}_v620_diagnostics.png")
        plt.savefig(plot_filename)
        print(f"[PLOT] Mode 4 diagnostic plot saved to '{plot_filename}'")
        plt.close()
        return

    # --------------------------------------------------------------------------
    # MODES 1-3 PLOTTING [PURE LITERATURE]
    # --------------------------------------------------------------------------
    N_nodes = int(data["N_nodes"]) if "N_nodes" in data else 4096
    t_mid = data["t_mid_curve"]
    ds_curve = data["ds_curve"]
    sweep_history = data["sweep_history"]
    energy_history = data["energy_history"]
    ds_final = float(data["ds_final"])
    specific_heat = float(data["specific_heat_Cv"]) if "specific_heat_Cv" in data else 0.0
    specific_heat_err = float(data["specific_heat_Cv_err"]) if "specific_heat_Cv_err" in data else 0.0

    fit_min, fit_max = (8.0, 25.0) if N_nodes > 4096 else (0.8, 3.0)

    if mode_str == "PAPER1_VACUUM":
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5), dpi=200)

        ax1.plot(t_mid, ds_curve, color='#1f77b4', lw=2, label=r'Measured $d_s(t)$')
        ax1.axvspan(fit_min, fit_max, color='#2ca02c', alpha=0.15, label=f'Fit Region [{fit_min}, {fit_max}]')
        ax1.axhline(3.00, color='#d62728', linestyle='--', lw=1.5, label=r'Target ($d_s = 3.00$)')
        ax1.set_xscale('log')
        ax1.set_xlabel(r'Diffusion Time $t$')
        ax1.set_ylabel(r'Spectral Dimension $d_s(t)$')
        ax1.set_title(f'Spectral Dimension ({run_id} | Paper 1 Vacuum)\nFinal $d_s = {ds_final:.4f}$')
        ax1.grid(True, which='both', linestyle=':', alpha=0.6)
        ax1.legend(loc='upper right')

        ax2.plot(sweep_history, energy_history, color='#ff7f0e', lw=1.5, label=r'Total Energy $H_{\mathrm{tot}}$')
        ax2.set_xlabel(r'Monte Carlo Sweep (MCS)')
        ax2.set_ylabel(r'Total Energy $H_{\mathrm{tot}}$')
        ax2.set_title(f'Energy Trajectory & Thermalization\n$C_v = {specific_heat:.6f} \\pm {specific_heat_err:.6f}$')
        ax2.grid(True, linestyle=':', alpha=0.6)
        ax2.legend(loc='upper right')

    elif mode_str == "PAPER2_GAUGE_SOLITON":
        fig, axs = plt.subplots(2, 2, figsize=(12, 9), dpi=200)
        (ax1, ax2), (ax3, ax4) = axs

        ax1.plot(t_mid, ds_curve, color='#1f77b4', lw=2, label=r'Measured $d_s(t)$')
        ax1.axvspan(fit_min, fit_max, color='#2ca02c', alpha=0.15, label=f'Fit Region [{fit_min}, {fit_max}]')
        ax1.axhline(3.00, color='#d62728', linestyle='--', lw=1.5, label=r'Target ($d_s = 3.00$)')
        ax1.set_xscale('log')
        ax1.set_xlabel(r'Diffusion Time $t$')
        ax1.set_ylabel(r'Spectral Dimension $d_s(t)$')
        ax1.set_title(f'(a) Spectral Dimension ({run_id})\nFinal $d_s = {ds_final:.4f}$')
        ax1.grid(True, which='both', linestyle=':', alpha=0.6)
        ax1.legend(loc='upper right')

        q_history = data["q_history"] if "q_history" in data else np.array([])
        q_final = float(data["topological_charge_Q"]) if "topological_charge_Q" in data else 1.0

        if len(q_history) > 0 and len(q_history) == len(sweep_history):
            ax2.plot(sweep_history, q_history, color='#9467bd', lw=2, label=f'Measured $Q_t$ (Final = {q_final:.4f})')
        else:
            ax2.axhline(q_final, color='#9467bd', lw=2.5, label=f'Final $Q{{\\mathrm{{top}}}} = {q_final:.4f}$')

        ax2.axhline(1.0, color='#d62728', linestyle='--', lw=1, label=r'Target ($Q = 1.0$)')
        ax2.set_ylim(-0.5, 2.5)
        ax2.set_xlim(0, sweep_history[-1])
        ax2.set_xlabel(r'Monte Carlo Sweep (MCS)')
        ax2.set_ylabel(r'Topological Charge $Q_{\mathrm{top}}$')
        ax2.set_title(r'(b) Soliton Topological Survival $Q_{\mathrm{top}}$')
        ax2.grid(True, linestyle=':', alpha=0.6)
        ax2.legend(loc='upper right')

        splaq_history = data["splaq_history"] if "splaq_history" in data else np.array([])
        s_plaq = float(data["su2_plaquette_action"]) if "su2_plaquette_action" in data else 0.0

        if len(splaq_history) > 0 and len(splaq_history) == len(sweep_history):
            ax3.plot(sweep_history, splaq_history, color='#2ca02c', lw=2, label=f'$S{{\\mathrm{{plaq}}}}$ (Final = {s_plaq:.4f})')
        else:
            ax3.axhline(s_plaq, color='#2ca02c', lw=2, label=f'$S{{\\mathrm{{plaq}}}} = {s_plaq:.4f}$')

        ax3.set_xlim(0, sweep_history[-1])
        ax3.set_xlabel(r'Monte Carlo Sweep (MCS)')
        ax3.set_ylabel(r'Wilson Plaquette Action $S_{\mathrm{plaq}}$')
        ax3.set_title(r'(c) $SU(2)$ Gauge Field Action Relaxation')
        ax3.grid(True, linestyle=':', alpha=0.6)
        ax3.legend(loc='upper right')

        ax4.plot(sweep_history, energy_history, color='#ff7f0e', lw=1.5, label=r'$H_{\mathrm{tot}}$')
        ax4.set_xlabel(r'Monte Carlo Sweep (MCS)')
        ax4.set_ylabel(r'Total Energy $H_{\mathrm{tot}}$')
        ax4.set_title(f'(d) Thermal Energy Trajectory\n$C_v = {specific_heat:.4f} \\pm {specific_heat_err:.4f}$')
        ax4.grid(True, linestyle=':', alpha=0.6)
        ax4.legend(loc='upper right')

    elif mode_str == "PAPER3_COSMOLOGY":
        fig, axs = plt.subplots(2, 2, figsize=(12, 9), dpi=200)
        (ax1, ax2), (ax3, ax4) = axs

        w_eos_history = data["w_eos_history"] if "w_eos_history" in data else np.array([])
        h_sq_history = data["h_sq_history"] if "h_sq_history" in data else np.array([])

        ax1.plot(t_mid, ds_curve, color='#1f77b4', lw=2, label=r'Measured $d_s(t)$')
        ax1.axvspan(fit_min, fit_max, color='#2ca02c', alpha=0.15, label=f'Fit Region [{fit_min}, {fit_max}]')
        ax1.axhline(3.00, color='#d62728', linestyle='--', lw=1.5, label=r'Target ($d_s = 3.00$)')
        ax1.set_xscale('log')
        ax1.set_xlabel(r'Diffusion Time $t$')
        ax1.set_ylabel(r'Spectral Dimension $d_s(t)$')
        ax1.set_title(f'(a) Continuum 3D Metric Stability\nFinal $d_s = {ds_final:.4f}$')
        ax1.grid(True, which='both', linestyle=':', alpha=0.6)
        ax1.legend(loc='upper right')

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

        if len(h_sq_history) > 0:
            ax3.plot(sweep_history, h_sq_history, color='#17becf', lw=2, label=r'LQC Rate $H^2$')
            h_sq_final = h_sq_history[-1]
            ax3.set_title(f'(c) LQC Hubble Bounce Rate\nFinal $H^2 = {fmt_sci_tex(h_sq_final)}$')
        else:
            ax3.set_title('(c) LQC Hubble Bounce Rate')
        ax3.set_xlabel(r'Monte Carlo Sweep (MCS)')
        ax3.set_ylabel(r'Hubble Parameter $H^2$')
        ax3.grid(True, linestyle=':', alpha=0.6)
        ax3.legend(loc='upper right')

        ax4.plot(sweep_history, energy_history, color='#ff7f0e', lw=1.5, label=r'$H_{\mathrm{tot}}$')
        ax4.set_xlabel(r'Monte Carlo Sweep (MCS)')
        ax4.set_ylabel(r'Total Energy $H_{\mathrm{tot}}$')
        ax4.set_title(f'(d) Thermal Energy Trajectory\n$C_v = {specific_heat:.4f} \\pm {specific_heat_err:.4f}$')
        ax4.grid(True, linestyle=':', alpha=0.6)
        ax4.legend(loc='upper right')

    plt.tight_layout()
    plt.subplots_adjust(top=0.92)
    plot_filename = os.path.join(out_dir, f"{safe_id}_{mode_str}_seed{seed_val}_v620_diagnostics.png")
    plt.savefig(plot_filename)
    print(f"[PLOT] Publication diagnostic plot saved to '{plot_filename}'")
    plt.close()
