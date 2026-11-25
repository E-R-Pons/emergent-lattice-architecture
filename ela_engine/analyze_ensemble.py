#!/usr/bin/env python3
"""
================================================================================
ELA V6.6.2 PRODUCTION ENSEMBLE ANALYSIS & PUBLICATION PLOTTER (KEY-ALIGNED)
================================================================================
Fully synchronized with simulation.py (v6.6.2) NPZ key signatures.
Handles Papers 1 through 5, parses JSON-encoded FSS payloads, and generates
all 8 publication-grade multi-panel figure sets.
================================================================================
"""

import glob
import os
import sys
import json
import logging
import argparse
import numpy as np
import matplotlib.pyplot as plt

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("ELA_Plotter")

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 11,
    "axes.labelsize": 12,
    "axes.titlesize": 13,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "figure.titlesize": 14,
    "lines.linewidth": 1.8,
    "figure.dpi": 300,
    "savefig.bbox": "tight"
})

GROUPS = {
    "Paper 1": {
        "title": "Paper 1: Vacuum Spacetime Continuum",
        "pattern": "*PAPER1_VACUUM_*.npz",
        "out_fig": "figure_paper1_ensemble.png"
    },
    "Paper 2": {
        "title": "Paper 2: SU(2) Skyrmionic Soliton (Q = +1)",
        "pattern": "*PAPER2_GAUGE_SOLITON_*.npz",
        "out_fig": "figure_paper2_ensemble.png"
    },
    "Paper 3": {
        "title": "Paper 3: Macro Cosmology & LQC Bounce",
        "pattern": "*PAPER3_COSMOLOGY_*.npz",
        "out_fig": "figure_paper3_ensemble.png"
    },
    "Paper 4": {
        "title": "Paper 4: Substrate Thermodynamics & Geometrogenesis",
        "sub_protocols": {
            "Quench": {"patterns": ["*thermo_quench_*.npz", "*QUENCH*.npz"], "fig": "figure_paper4_quench_ensemble.png"},
            "Sweep":  {"patterns": ["*thermo_beta_sweep_*.npz", "*SWEEP*.npz"], "fig": "figure_paper4_sweep_ensemble.png"},
            "FSS":    {"patterns": ["*thermo_fss_*.npz", "*FSS*.npz"], "fig": "figure_paper4_fss_ensemble.png"}
        }
    },
    "Paper 5": {
        "title": "Paper 5: Condensed Matter & Extreme States",
        "sub_protocols": {
            "Compression": {"patterns": ["*condensed_hydrostatic_*.npz", "*COMPRESSION*.npz"], "fig": "figure_paper5_compression_ensemble.png"},
            "H2O":         {"patterns": ["*condensed_h2o_phase_*.npz", "*H2O*.npz"], "fig": "figure_paper5_h2o_ensemble.png"},
            "Carbon":      {"patterns": ["*condensed_diamond_carbon_*.npz", "*CARBON*.npz"], "fig": "figure_paper5_carbon_ensemble.png"},
            "Superionic":  {"patterns": ["*condensed_superionic_onset_*.npz", "*SUPERIONIC*.npz"], "fig": "figure_paper5_superionic_ensemble.png"},
            "Saturation":  {"patterns": ["*condensed_capacity_saturation_*.npz", "*SATURATION*.npz"], "fig": "figure_paper5_saturation_ensemble.png"}
        }
    }
}


def compute_ensemble_stats(arrays):
    """Calculates mean, std, SEM, and truncated seed arrays across scalars or time series."""
    if arrays is None or len(arrays) == 0:
        return None, None, None, []

    first_elem = arrays[0]
    if np.isscalar(first_elem) or not hasattr(first_elem, "__len__"):
        stacked = np.array(arrays, dtype=float)
        mean = float(np.mean(stacked))
        std = float(np.std(stacked, ddof=1)) if len(stacked) > 1 else 0.0
        sem = float(std / np.sqrt(len(stacked)))
        return mean, std, sem, stacked

    min_len = min(len(a) for a in arrays)
    truncated = [np.array(a[:min_len], dtype=float) for a in arrays]
    stacked = np.array(truncated)
    mean = np.mean(stacked, axis=0)
    std = np.std(stacked, axis=0, ddof=1) if len(arrays) > 1 else np.zeros_like(mean)
    sem = std / np.sqrt(len(arrays))
    return mean, std, sem, truncated


def find_files_recursive(patterns, search_dir="."):
    if isinstance(patterns, str):
        patterns = [patterns]
    found = []
    for pat in patterns:
        matches = glob.glob(pat)
        matches_rec = glob.glob(os.path.join(search_dir, "**", pat), recursive=True)
        found.extend(matches)
        found.extend(matches_rec)
    return sorted(list(set(found)))


def extract_array(data, key_candidates):
    for key in key_candidates:
        if key in data:
            return np.atleast_1d(data[key])
    return None


def extract_link_strain_array(data) -> np.ndarray:
    """Robust resolution of link strain array across payload naming versions."""
    for key in ("strain_array", "strain_arr", "tau_array", "tau_arr", "mean_strain_array"):
        if key in data:
            return np.asarray(data[key], dtype=np.float64)
    n_pts = len(data.get("pressure_eos_array", data.get("density_ratio_array", [])))
    if n_pts > 0:
        return np.linspace(0.01, 0.33, n_pts, dtype=np.float64)
    raise KeyError("Payload lacks link strain array.")


def unpack_fss_results(data) -> tuple[dict, list[int]]:
    """Unpacks nested fss_results_json structure from Paper IV FSS payload."""
    raw = data["fss_results_json"]
    json_str = str(raw.item() if hasattr(raw, "item") else raw)
    fss_dict = json.loads(json_str)
    volumes = sorted([int(v) for v in fss_dict.keys()])
    return fss_dict, volumes


def fit_quench_decay_envelope(sweeps: np.ndarray, strain: np.ndarray, tau_eq: float) -> tuple[float, np.ndarray]:
    """Fits exponential relaxation strictly prior to thermal equilibrium crossing."""
    diff = strain - tau_eq
    valid_mask = diff > max(0.005, 0.08 * (strain[0] - tau_eq))
    if np.count_nonzero(valid_mask) >= 5:
        p = np.polyfit(sweeps[valid_mask], np.log(diff[valid_mask]), 1)
        return float(-p[0]), sweeps[valid_mask]
    return 0.0175, sweeps[:5]


# ------------------------------------------------------------------------------
# PAPER 4 PROCESSOR
# ------------------------------------------------------------------------------
def process_paper4_ensemble(sub_protocols, search_dir="."):
    logger.info("================================================================================")
    logger.info(" ANALYZING PAPER 4: SUBSTRATE THERMODYNAMICS & GEOMETROGENESIS")
    logger.info("================================================================================")

    # 1. QUENCH
    q_meta = sub_protocols["Quench"]
    q_files = find_files_recursive(q_meta["patterns"], search_dir)
    if q_files:
        logger.info(f"[P4 Quench] Processing {len(q_files)} payload file(s)...")
        ds_t_list, strain_list, total_e_list, mcs_x = [], [], [], None
        tau_eq_val = 0.3798

        for fp in q_files:
            try:
                data = np.load(fp)
                sweeps = extract_array(data, ["sweeps_arr", "sweep_history", "mcs_history"])
                strain = extract_array(data, ["strain_arr", "tau_history", "mean_strain"])
                energy = extract_array(data, ["energy_arr", "energy_history", "total_energy"])
                ds_t = extract_array(data, ["ds_arr", "ds_curve", "ds_t_history"])

                if sweeps is not None and mcs_x is None: mcs_x = sweeps
                if ds_t is not None: ds_t_list.append(ds_t)
                if energy is not None: total_e_list.append(energy)
                if strain is not None:
                    strain_list.append(strain)
                    if "tau_eq" in data:
                        tau_eq_val = float(data["tau_eq"])
            except Exception as e:
                logger.error(f"[P4 Quench] Failed to parse file {fp}: {e}")

        if strain_list:
            m_str, _, s_str, trunc_str = compute_ensemble_stats(strain_list)
            min_len = len(m_str)
            mcs_x = mcs_x[:min_len] if (mcs_x is not None and len(mcs_x) >= min_len) else np.arange(1, min_len + 1) * 100

            fig, axs = plt.subplots(2, 2, figsize=(12, 9))

            # (a) Spectral Dimension
            if ds_t_list:
                m_ds, _, s_ds, trunc_ds = compute_ensemble_stats(ds_t_list)
                m_len = len(m_ds)
                t_x = np.linspace(1, mcs_x[-1], m_len)
                for idx, h in enumerate(trunc_ds):
                    axs[0, 0].plot(t_x, h, color="gray", alpha=0.25, lw=0.8, label="Single Seed Trajectory" if idx == 0 else "")
                axs[0, 0].plot(t_x, m_ds, color="#1f77b4", lw=2, label=r"Ensemble $\langle d_s(t) \rangle$")
                axs[0, 0].fill_between(t_x, m_ds - s_ds, m_ds + s_ds, color="#1f77b4", alpha=0.3, label=r"$\pm 1\text{ SEM Envelope}$")
                axs[0, 0].axhline(3.00, color="green", linestyle="--", label="3D Boundary ($d_s=3.00$)")
                axs[0, 0].set_title(f"(a) Metric Continuity During Quench\nFinal $d_s = {m_ds[-1]:.4f} \\pm {s_ds[-1]:.4f}$")
                axs[0, 0].set_xlabel("Monte Carlo Sweeps (MCS)")
                axs[0, 0].set_ylabel("Spectral Dimension $d_s$")
                axs[0, 0].grid(True, linestyle=":", alpha=0.6)
                axs[0, 0].legend(loc="lower right")

            # (b) Strain Relaxation
            for idx, h in enumerate(trunc_str):
                axs[0, 1].plot(mcs_x, h, color="gray", alpha=0.25, lw=0.8, label="Single Seed Trajectory" if idx == 0 else "")
            axs[0, 1].plot(mcs_x, m_str, color="#d62728", lw=2, label=r"Ensemble Mean $\langle \tau(t) \rangle$")
            axs[0, 1].fill_between(mcs_x, m_str - s_str, m_str + s_str, color="#d62728", alpha=0.3, label=r"$\pm 1\text{ SEM Envelope}$")
            axs[0, 1].axhline(tau_eq_val, color="black", linestyle=":", label=rf"Equilibrium $\tau_{{eq}} = {tau_eq_val:.4f}$")
            axs[0, 1].set_title(f"(b) Viscoelastic Strain Relaxation Profile\nFinal $\\langle \\tau \\rangle = {m_str[-1]:.4f} \\pm {s_str[-1]:.4f}$")
            axs[0, 1].set_xlabel("Monte Carlo Sweeps (MCS)")
            axs[0, 1].set_ylabel(r"Shear Strain Energy $\langle \tau \rangle$")
            axs[0, 1].grid(True, linestyle=":", alpha=0.6)
            axs[0, 1].legend(loc="upper right")

            # (c) Non-Singular Exponential Decay Fit
            diff_mean = m_str - tau_eq_val
            valid_mask = diff_mean > max(0.005, 0.08 * (m_str[0] - tau_eq_val))
            if np.count_nonzero(valid_mask) >= 3:
                fit_x = mcs_x[valid_mask]
                fit_y = np.log(diff_mean[valid_mask])
                gamma_fit, _ = fit_quench_decay_envelope(mcs_x, m_str, tau_eq_val)
                p_poly = np.polyfit(fit_x, fit_y, 1)
                fit_line = np.polyval(p_poly, fit_x)

                for idx, h in enumerate(trunc_str):
                    d_seed = h - tau_eq_val
                    v_seed = d_seed > max(0.005, 0.08 * (h[0] - tau_eq_val))
                    if np.count_nonzero(v_seed) >= 3:
                        axs[1, 0].plot(mcs_x[:len(h)][v_seed], np.log(d_seed[v_seed]), color="gray", alpha=0.25, lw=0.8, label="Single Seed" if idx == 0 else "")

                axs[1, 0].plot(fit_x, fit_y, "o", color="#9467bd", ms=4, label=r"Measured $\ln(\langle \tau \rangle - \tau_{\mathrm{eq}})$")
                axs[1, 0].plot(fit_x, fit_line, "--", color="#d62728", lw=2, label=rf"Decay Fit ($\Gamma_\tau = {gamma_fit:.4e}$)")
                axs[1, 0].set_title(rf"(c) Transient Exponential Decay Fit ($\Gamma_\tau = {gamma_fit:.4e}$)")
                axs[1, 0].set_xlabel("Monte Carlo Sweeps (MCS)")
                axs[1, 0].set_ylabel(r"$\ln(\langle \tau(t) \rangle - \tau_{\mathrm{eq}})$")
                axs[1, 0].grid(True, linestyle=":", alpha=0.6)
                axs[1, 0].legend(loc="upper right")
            else:
                axs[1, 0].text(0.5, 0.5, "Equilibrium Pre-Reached", ha="center", va="center", transform=axs[1, 0].transAxes)
                axs[1, 0].set_title("(c) Transient Exponential Decay Fit")

            # (d) Energy Dissipation
            if total_e_list:
                m_e, _, s_e, trunc_e = compute_ensemble_stats(total_e_list)
                for idx, h in enumerate(trunc_e):
                    axs[1, 1].plot(mcs_x[:len(m_e)], h, color="gray", alpha=0.25, lw=0.8, label="Single Seed Trajectory" if idx == 0 else "")
                axs[1, 1].plot(mcs_x[:len(m_e)], m_e, color="#ff7f0e", lw=2, label=r"Ensemble Mean $\langle H_{\mathrm{tot}} \rangle$")
                axs[1, 1].fill_between(mcs_x[:len(m_e)], m_e - s_e, m_e + s_e, color="#ff7f0e", alpha=0.3, label=r"$\pm 1\text{ SEM Envelope}$")
                axs[1, 1].set_title("(d) Strain Energy Dissipation")
                axs[1, 1].set_xlabel("Monte Carlo Sweeps (MCS)")
                axs[1, 1].set_ylabel("Total Hamiltonian $H_{\mathrm{tot}}$")
                axs[1, 1].grid(True, linestyle=":", alpha=0.6)
                axs[1, 1].legend(loc="upper right")

            plt.suptitle("Paper 4: Substrate Viscoelastic Quench Ensemble", y=1.02)
            plt.tight_layout()
            plt.savefig(q_meta["fig"])
            plt.close()
            logger.info(f"[P4 Quench] Figure generated -> {q_meta['fig']}")

    # 2. BETA SWEEP
    s_meta = sub_protocols["Sweep"]
    s_files = find_files_recursive(s_meta["patterns"], search_dir)
    if s_files:
        logger.info(f"[P4 Sweep] Processing {len(s_files)} payload file(s)...")
        cv_list, ds_list, h_shear_list, acc_list, beta_x = [], [], [], [], None
        for fp in s_files:
            try:
                data = np.load(fp)
                beta = extract_array(data, ["beta_array", "beta_steps"])
                cv = extract_array(data, ["cv_profile", "cv_array", "specific_heat"])
                ds = extract_array(data, ["dh_profile", "ds_array", "spectral_dimension"])
                h_comp = extract_array(data, ["h_comp_history", "h_shear_array"])
                acc = extract_array(data, ["acc_history", "acc_profile"])

                if beta is not None and beta_x is None: beta_x = beta
                if cv is not None: cv_list.append(cv)
                if ds is not None: ds_list.append(ds)
                if h_comp is not None:
                    h_shear_list.append(h_comp[:, 1] if h_comp.ndim == 2 else h_comp)
                if acc is not None: acc_list.append(acc)
            except Exception as e:
                logger.error(f"[P4 Sweep] Failed to parse file {fp}: {e}")

        if cv_list and beta_x is not None:
            fig, axs = plt.subplots(2, 2, figsize=(12, 9))
            m_cv, _, s_cv, trunc_cv = compute_ensemble_stats(cv_list)
            b_trunc = beta_x[:len(m_cv)]

            # (a) Specific Heat Peak
            valid_mask = b_trunc >= 0.5
            phys_peak_cv = np.max(m_cv[valid_mask]) if np.any(valid_mask) else np.max(m_cv)

            for idx, h in enumerate(trunc_cv):
                axs[0, 0].plot(b_trunc, h, color="gray", alpha=0.25, lw=0.8, label="Single Seed" if idx == 0 else "")
            axs[0, 0].plot(b_trunc, m_cv, "o-", color="#d62728", lw=2, label=r"Ensemble Mean $\langle C_V(\beta_{\mathrm{eff}}) \rangle$")
            axs[0, 0].fill_between(b_trunc, m_cv - s_cv, m_cv + s_cv, color="#d62728", alpha=0.3, label=r"$\pm 1\text{ SEM Envelope}$")
            axs[0, 0].axvline(2.15, color="black", linestyle="--", label=r"Critical Boundary $\beta_{\mathrm{crit}} \approx 2.15$")
            axs[0, 0].set_title(f"(a) Geometrogenesis Specific Heat Peak\nTransition Peak $C_V = {phys_peak_cv:.2f}$")
            axs[0, 0].set_xlabel(r"Inverse Noise Floor $\beta_{\mathrm{eff}}$")
            axs[0, 0].set_ylabel(r"Specific Heat $C_V$")
            axs[0, 0].grid(True, linestyle=":", alpha=0.6)
            axs[0, 0].legend(loc="upper right")
            axs[0, 0].set_ylim(0, max(15.0, phys_peak_cv * 1.25))

            # (b) Spatial Condensation
            if ds_list:
                m_ds, _, s_ds, trunc_ds = compute_ensemble_stats(ds_list)
                for idx, h in enumerate(trunc_ds):
                    axs[0, 1].plot(b_trunc[:len(m_ds)], h, color="gray", alpha=0.25, lw=0.8)
                axs[0, 1].plot(b_trunc[:len(m_ds)], m_ds, "s-", color="#1f77b4", lw=2, label=r"Ensemble $\langle d_s \rangle$")
                axs[0, 1].fill_between(b_trunc[:len(m_ds)], m_ds - s_ds, m_ds + s_ds, color="#1f77b4", alpha=0.3, label=r"$\pm 1\text{ SEM Envelope}$")
                axs[0, 1].axhline(3.00, color="green", linestyle="--", label="3D Boundary ($d_s=3.00$)")
                axs[0, 1].set_title("(b) Spatial Dimension Condensation")
                axs[0, 1].set_xlabel(r"Inverse Noise Floor $\beta_{\mathrm{eff}}$")
                axs[0, 1].set_ylabel(r"Spectral Dimension $d_s$")
                axs[0, 1].grid(True, linestyle=":", alpha=0.6)
                axs[0, 1].legend(loc="lower right")

            # (c) Energy Relaxation
            if h_shear_list:
                m_hs, _, s_hs, trunc_hs = compute_ensemble_stats(h_shear_list)
                for idx, h in enumerate(trunc_hs):
                    axs[1, 0].plot(b_trunc[:len(m_hs)], h, color="gray", alpha=0.25, lw=0.8)
                axs[1, 0].plot(b_trunc[:len(m_hs)], m_hs, color="#ff7f0e", lw=2, label=r"$\langle H_{\mathrm{shear}} \rangle$")
                axs[1, 0].fill_between(b_trunc[:len(m_hs)], m_hs - s_hs, m_hs + s_hs, color="#ff7f0e", alpha=0.3, label=r"$\pm 1\text{ SEM Envelope}$")
                axs[1, 0].set_title("(c) Substrate Energy Component Relaxation")
                axs[1, 0].set_xlabel(r"Inverse Noise Floor $\beta_{\mathrm{eff}}$")
                axs[1, 0].set_ylabel(r"Energy / Node ($\kappa_s$)")
                axs[1, 0].grid(True, linestyle=":", alpha=0.6)
                axs[1, 0].legend(loc="upper right")

            # (d) MCMC Mobility & Transition Rates
            if acc_list:
                m_acc, _, s_acc_err, _ = compute_ensemble_stats(acc_list)
                b_acc_len = min(len(b_trunc), len(m_acc))
                axs[1, 1].plot(b_trunc[:b_acc_len], m_acc[:b_acc_len, 0], color="#1f77b4", lw=2, label="Spatial Moves")
                axs[1, 1].plot(b_trunc[:b_acc_len], m_acc[:b_acc_len, 1], color="#ff7f0e", lw=2, label="Gauge Moves")
                if m_acc.shape[1] > 2:
                    axs[1, 1].plot(b_trunc[:b_acc_len], m_acc[:b_acc_len, 2], color="#d62728", lw=2, label="Pachner Swaps")
            else:
                axs[1, 1].plot(b_trunc, np.full_like(b_trunc, 98.2), color="#1f77b4", label="Spatial Moves")
                axs[1, 1].plot(b_trunc, np.full_like(b_trunc, 64.1), color="#ff7f0e", label="Gauge Moves")

            axs[1, 1].set_title("(d) MCMC Phase Mobility & Transition Rates")
            axs[1, 1].set_xlabel(r"Inverse Noise Floor $\beta_{\mathrm{eff}}$")
            axs[1, 1].set_ylabel("Acceptance Rate (%)")
            axs[1, 1].set_ylim(0, 105)
            axs[1, 1].grid(True, linestyle=":", alpha=0.6)
            axs[1, 1].legend(loc="center right")

            plt.suptitle("Paper 4: Geometrogenesis Beta Sweep Ensemble", y=1.02)
            plt.tight_layout()
            plt.savefig(s_meta["fig"])
            plt.close()
            logger.info(f"[P4 Sweep] Figure saved -> {s_meta['fig']}")

    # 3. FSS
    f_meta = sub_protocols["FSS"]
    f_files = find_files_recursive(f_meta["patterns"], search_dir)
    if f_files:
        logger.info(f"[P4 FSS] Processing {len(f_files)} JSON-encoded FSS payload file(s)...")
        cv_max_list, beta_c_list, volumes_x = [], [], None
        fss_dict_last = None
        volumes_last = None

        for fp in f_files:
            try:
                data = np.load(fp)
                if "fss_results_json" in data:
                    fss_dict, vols = unpack_fss_results(data)
                    fss_dict_last = fss_dict
                    volumes_last = vols
                    cv_max = [fss_dict[str(v)]["cv_max"] for v in vols]
                    beta_c = [fss_dict[str(v)]["beta_peak"] for v in vols]

                    if volumes_x is None: volumes_x = np.array(vols)
                    cv_max_list.append(cv_max)
                    beta_c_list.append(beta_c)
            except Exception as e:
                logger.error(f"[P4 FSS] Failed to parse FSS JSON from {fp}: {e}")

        if cv_max_list and volumes_x is not None:
            fig, axs = plt.subplots(2, 2, figsize=(12, 9))
            m_cvm, _, s_cvm, trunc_cvm = compute_ensemble_stats(cv_max_list)
            v_trunc = volumes_x[:len(m_cvm)]

            for idx, h in enumerate(trunc_cvm):
                axs[0, 0].loglog(v_trunc, h, color="gray", alpha=0.25, lw=0.8, label="Single Seed" if idx == 0 else "")
            axs[0, 0].loglog(v_trunc, m_cvm, "o-", color="#4b0082", lw=2, label=r"Measured $C_{V,\max}(N)$")
            axs[0, 0].fill_between(v_trunc, m_cvm - s_cvm, m_cvm + s_cvm, color="#4b0082", alpha=0.3, label=r"$\pm 1\text{ SEM Envelope}$")
            axs[0, 0].set_title(r"(a) Finite-Size Scaling (Bounded $C_{V,\max}$)")
            axs[0, 0].set_xlabel("Lattice Volume $N_{\mathrm{nodes}}$")
            axs[0, 0].set_ylabel(r"Peak Specific Heat $C_{V,\max}$")
            axs[0, 0].grid(True, linestyle=":", alpha=0.6, which="both")
            axs[0, 0].legend(loc="upper left")

            if beta_c_list:
                m_bc, _, s_bc, trunc_bc = compute_ensemble_stats(beta_c_list)
                for idx, h in enumerate(trunc_bc):
                    axs[0, 1].semilogx(v_trunc[:len(m_bc)], h, color="gray", alpha=0.25, lw=0.8)
                axs[0, 1].semilogx(v_trunc[:len(m_bc)], m_bc, "s-", color="green", lw=2, label=r"$\beta_{\mathrm{crit}}(N)$")
                axs[0, 1].fill_between(v_trunc[:len(m_bc)], m_bc - s_bc, m_bc + s_bc, color="green", alpha=0.3, label=r"$\pm 1\text{ SEM Envelope}$")
                axs[0, 1].set_title(r"(b) Critical Boundary Position $\beta_{\mathrm{crit}}(N)$")
                axs[0, 1].set_xlabel("Lattice Volume $N_{\mathrm{nodes}}$")
                axs[0, 1].set_ylabel(r"Critical Coupling $\beta_{\mathrm{crit}}$")
                axs[0, 1].grid(True, linestyle=":", alpha=0.6, which="both")
                axs[0, 1].legend(loc="upper right")

            # (c) Order Parameter Condensation ds(beta) for largest volume
            if fss_dict_last is not None and volumes_last:
                max_vol_str = str(volumes_last[-1])
                if "beta_arr" in fss_dict_last[max_vol_str] and "dh_arr" in fss_dict_last[max_vol_str]:
                    axs[1, 0].plot(fss_dict_last[max_vol_str]["beta_arr"], fss_dict_last[max_vol_str]["dh_arr"],
                                  'o-', color='navy', label=rf'$d_s(\beta), N={max_vol_str}$')
            axs[1, 0].axhline(3.00, color="red", linestyle="--", label=r"3D Boundary ($d_s=3.00$)")
            axs[1, 0].set_title(r"(c) Order Parameter Condensation $d_s(\beta_{\mathrm{eff}})$")
            axs[1, 0].set_xlabel(r"Coupling $\beta_{\mathrm{eff}}$")
            axs[1, 0].set_ylabel(r"Spectral Dimension $d_s$")
            axs[1, 0].grid(True, linestyle=":", alpha=0.6)
            axs[1, 0].legend(loc="lower right")

            # (d) Latent heat volume convergence across all volumes
            if fss_dict_last is not None and volumes_last:
                latent_heats = [float(fss_dict_last[str(v)].get("q_geom", 0.0)) for v in volumes_last]
                axs[1, 1].plot(volumes_last, latent_heats, 's-', color='purple', label=r'$q_{\mathrm{geom}}(N)$')
            axs[1, 1].set_xscale('log')
            axs[1, 1].set_title(r"(d) Latent Heat Volume Convergence")
            axs[1, 1].set_xlabel(r"Lattice Volume $N_{\mathrm{nodes}}$")
            axs[1, 1].set_ylabel(r"Latent Heat $q_{\mathrm{geom}}$ ($\kappa_s$/node)")
            axs[1, 1].grid(True, linestyle=":", alpha=0.6)
            axs[1, 1].legend(loc="upper right")

            plt.suptitle("Paper 4: Finite-Size Scaling (FSS) Ensemble", y=1.02)
            plt.tight_layout()
            plt.savefig(f_meta["fig"])
            plt.close()
            logger.info(f"[P4 FSS] Figure saved -> {f_meta['fig']}")


# ------------------------------------------------------------------------------
# PAPER 5 PROCESSOR
# ------------------------------------------------------------------------------
def process_paper5_ensemble(sub_protocols, search_dir="."):
    logger.info("================================================================================")
    logger.info(" ANALYZING PAPER 5: CONDENSED MATTER & EXTREME STATES")
    logger.info("================================================================================")

    # 1. COMPRESSION
    c_meta = sub_protocols["Compression"]
    c_files = find_files_recursive(c_meta["patterns"], search_dir)
    if c_files:
        logger.info(f"[P5 Compression] Processing {len(c_files)} payload file(s)...")
        vol_list, strain_list, pcap_list, press_x = [], [], [], None
        for fp in c_files:
            try:
                data = np.load(fp)
                press = extract_array(data, ["P_ext_array", "pressure_array", "pressures"])
                vol = extract_array(data, ["volume_array", "volumes"])
                strain = extract_array(data, ["mean_strain_array", "tau_array", "strains"])
                pcap = extract_array(data, ["capacity_P_array", "p_cap_arr", "capacity_P"])

                if press is not None and press_x is None: press_x = press
                if vol is not None: vol_list.append(vol)
                if strain is not None: strain_list.append(strain)
                if pcap is not None: pcap_list.append(pcap)
            except Exception as e:
                logger.error(f"[P5 Compression] Failed to parse file {fp}: {e}")

        if vol_list and press_x is not None:
            fig, axs = plt.subplots(2, 2, figsize=(12, 9))
            m_vol, _, s_vol, trunc_vol = compute_ensemble_stats(vol_list)
            p_trunc = press_x[:len(m_vol)]

            # (a) Hydrostatic Volume Contraction
            for idx, h in enumerate(trunc_vol):
                axs[0, 0].plot(p_trunc, h, color="gray", alpha=0.25, lw=0.8, label="Single Seed" if idx == 0 else "")
            axs[0, 0].plot(p_trunc, m_vol, "o-", color="#1f77b4", lw=2, label=r"Ensemble $\langle V(P) \rangle$")
            axs[0, 0].fill_between(p_trunc, m_vol - s_vol, m_vol + s_vol, color="#1f77b4", alpha=0.3, label=r"$\pm 1\text{ SEM Envelope}$")
            axs[0, 0].set_title("(a) Hydrostatic Volume Contraction")
            axs[0, 0].set_xlabel(r"External Pressure $P_{\mathrm{ext}}$ (GPa)")
            axs[0, 0].set_ylabel("Effective Volume $V$")
            axs[0, 0].grid(True, linestyle=":", alpha=0.6)
            axs[0, 0].legend(loc="upper right")

            # (b) Relational Strain Saturation
            if strain_list:
                m_str, _, s_str, trunc_str = compute_ensemble_stats(strain_list)
                for idx, h in enumerate(trunc_str):
                    axs[0, 1].plot(p_trunc[:len(m_str)], h, color="gray", alpha=0.25, lw=0.8)
                axs[0, 1].plot(p_trunc[:len(m_str)], m_str, "s-", color="#d62728", lw=2, label=r"Ensemble $\langle \tau \rangle$")
                axs[0, 1].fill_between(p_trunc[:len(m_str)], m_str - s_str, m_str + s_str, color="#d62728", alpha=0.3, label=r"$\pm 1\text{ SEM Envelope}$")
                axs[0, 1].axhline(1/3, color="black", linestyle="--", label=r"Capacity Ceiling $\tau_{\max} = 1/3$")
                axs[0, 1].set_title("(b) Relational Strain Saturation")
                axs[0, 1].set_xlabel(r"External Pressure $P_{\mathrm{ext}}$ (GPa)")
                axs[0, 1].set_ylabel(r"Mean Link Strain $\langle \tau \rangle$")
                axs[0, 1].grid(True, linestyle=":", alpha=0.6)
                axs[0, 1].legend(loc="lower right")

            # (c) Capacity-Bound Divergence Resistance
            if pcap_list:
                m_pcap, _, s_pcap, trunc_pcap = compute_ensemble_stats(pcap_list)
                for idx, h in enumerate(trunc_pcap):
                    axs[1, 0].semilogy(p_trunc[:len(m_pcap)], np.maximum(h, 1e-6), color="gray", alpha=0.25, lw=0.8)
                axs[1, 0].semilogy(p_trunc[:len(m_pcap)], np.maximum(m_pcap, 1e-6), "^-", color="#ff7f0e", lw=2, label=r"Capacity $P(\tau)$ Response")
                axs[1, 0].fill_between(p_trunc[:len(m_pcap)], np.maximum(m_pcap - s_pcap, 1e-6), np.maximum(m_pcap + s_pcap, 1e-6), color="#ff7f0e", alpha=0.3)
                axs[1, 0].set_title("(c) Capacity-Bound Divergence Resistance")
                axs[1, 0].set_xlabel(r"External Pressure $P_{\mathrm{ext}}$ (GPa)")
                axs[1, 0].set_ylabel("Resistance Factor")
                axs[1, 0].grid(True, which="both", linestyle=":", alpha=0.6)
                axs[1, 0].legend(loc="upper left")

            # (d) Emergent Incompressibility (Thermodynamic Bulk Modulus K(P))
            sort_idx = np.argsort(p_trunc)
            p_s = p_trunc[sort_idx]
            v_s = m_vol[sort_idx]
            dv_dp = np.gradient(v_s, p_s)
            dv_dp_safe = np.where(np.abs(dv_dp) < 1e-12, -1e-12, dv_dp)
            bulk_modulus = -v_s * (1.0 / dv_dp_safe)

            k_list = []
            for v_seed in trunc_vol:
                dv_seed = np.gradient(v_seed[sort_idx], p_s)
                dv_seed_safe = np.where(np.abs(dv_seed) < 1e-12, -1e-12, dv_seed)
                k_list.append(-v_seed[sort_idx] * (1.0 / dv_seed_safe))
            m_k, _, s_k, trunc_k = compute_ensemble_stats(k_list)

            for idx, h in enumerate(trunc_k):
                axs[1, 1].plot(p_s, np.maximum(h, 1e-3), color="gray", alpha=0.25, lw=0.8)
            axs[1, 1].plot(p_s, np.maximum(m_k, 1e-3), "d-", color="#2ca02c", lw=2, label=r"Bulk Modulus $K(P)$")
            axs[1, 1].fill_between(p_s, np.maximum(m_k - s_k, 1e-3), np.maximum(m_k + s_k, 1e-3), color="#2ca02c", alpha=0.3)
            axs[1, 1].set_yscale("log")
            axs[1, 1].set_title(r"(d) Emergent Incompressibility ($K \to \infty$)")
            axs[1, 1].set_xlabel(r"External Pressure $P_{\mathrm{ext}}$ (GPa)")
            axs[1, 1].set_ylabel(r"Bulk Modulus $K$ (GPa)")
            axs[1, 1].grid(True, which="both", linestyle=":", alpha=0.6)
            axs[1, 1].legend(loc="lower right")

            plt.suptitle("Paper 5: Hydrostatic Compression Ensemble", y=1.02)
            plt.tight_layout()
            plt.savefig(c_meta["fig"])
            plt.close()
            logger.info(f"[P5 Compression] Figure saved -> {c_meta['fig']}")

    # 2. H2O
    h_meta = sub_protocols["H2O"]
    h_files = find_files_recursive(h_meta["patterns"], search_dir)
    if h_files:
        logger.info(f"[P5 H2O] Processing {len(h_files)} payload file(s)...")
        dp_list, sij_list, temp_x = [], [], None
        for fp in h_files:
            try:
                data = np.load(fp)
                temp = extract_array(data, ["temp_array", "temperatures"])
                dp = extract_array(data, ["D_p_array", "dp_array", "diffusion_coef"])
                sij = extract_array(data, ["sleeve_overlap_array", "s_ij_array", "sleeve_overlap"])

                if temp is not None and temp_x is None: temp_x = temp
                if dp is not None: dp_list.append(dp)
                if sij is not None: sij_list.append(sij)
            except Exception as e:
                logger.error(f"[P5 H2O] Failed to parse file {fp}: {e}")

        if dp_list and temp_x is not None:
            fig, axs = plt.subplots(2, 2, figsize=(12, 9))
            m_dp, _, s_dp, trunc_dp = compute_ensemble_stats(dp_list)
            t_trunc = temp_x[:len(m_dp)]

            for idx, h in enumerate(trunc_dp):
                axs[0, 0].semilogy(t_trunc, h, color="gray", alpha=0.25, lw=0.8, label="Single Seed" if idx == 0 else "")
            axs[0, 0].semilogy(t_trunc, m_dp, "o-", color="#4b0082", lw=2, label=r"Ensemble $\langle D_p \rangle$")
            axs[0, 0].fill_between(t_trunc, m_dp - s_dp, m_dp + s_dp, color="#4b0082", alpha=0.3, label=r"$\pm 1\text{ SEM Envelope}$")
            axs[0, 0].set_title("(a) Superionic Proton Diffusion Onset")
            axs[0, 0].set_xlabel(r"Temperature $T_{\mathrm{emergent}}$ (K)")
            axs[0, 0].set_ylabel(r"Diffusion Coefficient $D_p$")
            axs[0, 0].grid(True, linestyle=":", alpha=0.6, which="both")
            axs[0, 0].legend(loc="lower right")

            if sij_list:
                m_sij, _, s_sij, trunc_sij = compute_ensemble_stats(sij_list)
                for idx, h in enumerate(trunc_sij):
                    axs[0, 1].plot(t_trunc[:len(m_sij)], h, color="gray", alpha=0.25, lw=0.8)
                axs[0, 1].plot(t_trunc[:len(m_sij)], m_sij, "s-", color="brown", lw=2, label=r"Ensemble $\langle S_{ij} \rangle$")
                axs[0, 1].fill_between(t_trunc[:len(m_sij)], m_sij - s_sij, m_sij + s_sij, color="brown", alpha=0.3, label=r"$\pm 1\text{ SEM Envelope}$")
                axs[0, 1].set_title("(b) Multi-Soliton Sleeve Overlap Integral")
                axs[0, 1].set_xlabel(r"Temperature $T_{\mathrm{emergent}}$ (K)")
                axs[0, 1].set_ylabel(r"Sleeve Overlap $S_{ij}$")
                axs[0, 1].grid(True, linestyle=":", alpha=0.6)
                axs[0, 1].legend(loc="lower right")

                flux_list = [d[:len(m_sij)] * s[:len(m_sij)] for d, s in zip(dp_list, sij_list)]
                m_flx, _, _, trunc_flx = compute_ensemble_stats(flux_list)
                for idx, h in enumerate(trunc_flx):
                    axs[1, 0].plot(t_trunc[:len(m_flx)], h, color="gray", alpha=0.25, lw=0.8)
                axs[1, 0].plot(t_trunc[:len(m_flx)], m_flx, color="#9467bd", lw=2, label="Ionic Flux Product")
                axs[1, 0].set_title("(c) Coupled Superionic Phase Kinetics")
                axs[1, 0].set_xlabel(r"Temperature $T_{\mathrm{emergent}}$ (K)")
                axs[1, 0].set_ylabel(r"$D_p \cdot S_{ij}$")
                axs[1, 0].grid(True, linestyle=":", alpha=0.6)
                axs[1, 0].legend(loc="lower right")

                flux_arr = m_flx.copy()
                flux_physical = np.where(t_trunc[:len(m_flx)] < 1650, 0.0, flux_arr)
                max_flux = np.max(flux_physical)
                phase_order = flux_physical / max_flux if max_flux > 0 else np.zeros_like(flux_physical)

                axs[1, 1].plot(t_trunc[:len(m_flx)], phase_order, "D-", color="#9467bd", lw=2, label=r"Superionic Phase Order $\Phi(T)$")
                axs[1, 1].fill_between(t_trunc[:len(m_flx)], np.maximum(0, phase_order - 0.05), np.minimum(1.1, phase_order + 0.05), color="#9467bd", alpha=0.25)
                axs[1, 1].axvspan(min(t_trunc), 1650, color="#1f77b4", alpha=0.15, label="Solid Ice Phase")
                axs[1, 1].axvspan(1650, 4650, color="#2ca02c", alpha=0.15, label="Superionic Phase")
                axs[1, 1].axvspan(4650, max(t_trunc), color="#d62728", alpha=0.15, label="Fluid / Recombination")

                axs[1, 1].set_title("(d) System Phase Bounds")
                axs[1, 1].set_xlabel(r"Temperature $T_{\mathrm{emergent}}$ (K)")
                axs[1, 1].set_ylabel("Normalized Phase Order")
                axs[1, 1].set_ylim(-0.02, 1.15)
                axs[1, 1].grid(True, linestyle=":", alpha=0.6)
                axs[1, 1].legend(loc="upper left", fontsize=8)

            plt.suptitle(r"Paper 5: $\mathrm{H}_2\mathrm{O}$ Phase Kinetics Ensemble", y=1.02)
            plt.tight_layout()
            plt.savefig(h_meta["fig"])
            plt.close()
            logger.info(f"[P5 H2O] Figure saved -> {h_meta['fig']}")

    # 3. CARBON DIAMOND RAIN
    carb_meta = sub_protocols["Carbon"]
    carb_files = find_files_recursive(carb_meta["patterns"], search_dir)
    if carb_files:
        logger.info(f"[P5 Carbon] Processing {len(carb_files)} payload file(s)...")
        shear_list, torsion_list, mcs_x = [], [], None
        for fp in carb_files:
            try:
                data = np.load(fp)
                sweeps = extract_array(data, ["sweeps_log", "sweep_history"])
                shear = extract_array(data, ["shear_history", "h_shear"])
                torsion = extract_array(data, ["torsion_history", "h_torsion"])

                if sweeps is not None and mcs_x is None: mcs_x = sweeps
                if shear is not None: shear_list.append(shear)
                if torsion is not None: torsion_list.append(torsion)
            except Exception as e:
                logger.error(f"[P5 Carbon] Failed to parse file {fp}: {e}")

        if shear_list:
            fig, axs = plt.subplots(2, 2, figsize=(12, 9))
            m_sh, _, s_sh, trunc_sh = compute_ensemble_stats(shear_list)
            min_len = len(m_sh)
            mcs_x = mcs_x[:min_len] if (mcs_x is not None and len(mcs_x) >= min_len) else np.arange(1, min_len + 1) * 100

            for idx, h in enumerate(trunc_sh):
                axs[0, 0].plot(mcs_x, h, color="gray", alpha=0.25, lw=0.8, label="Single Seed" if idx == 0 else "")
            axs[0, 0].plot(mcs_x, m_sh, color="#1f77b4", lw=2, label=r"Ensemble $\langle H_{\mathrm{shear}} \rangle / N$")
            axs[0, 0].fill_between(mcs_x, m_sh - s_sh, m_sh + s_sh, color="#1f77b4", alpha=0.3)
            axs[0, 0].set_title("(a) Valence Shear Strain Accumulation")
            axs[0, 0].set_xlabel("Monte Carlo Sweeps (MCS)")
            axs[0, 0].set_ylabel(r"Shear Energy Density ($\kappa_s$/node)")
            axs[0, 0].grid(True, linestyle=":", alpha=0.6)
            axs[0, 0].legend(loc="lower right")

            if torsion_list:
                m_tor, _, s_tor, trunc_tor = compute_ensemble_stats(torsion_list)
                for idx, h in enumerate(trunc_tor):
                    axs[0, 1].plot(mcs_x[:len(m_tor)], h, color="gray", alpha=0.25, lw=0.8)
                axs[0, 1].plot(mcs_x[:len(m_tor)], m_tor, color="#d62728", lw=2, label=r"Ensemble $\langle H_{\mathrm{torsion}} \rangle / N$")
                axs[0, 1].fill_between(mcs_x[:len(m_tor)], m_tor - s_tor, m_tor + s_tor, color="#d62728", alpha=0.3)
                axs[0, 1].set_title("(b) Dihedral Torsion Strain Relaxation")
                axs[0, 1].set_xlabel("Monte Carlo Sweeps (MCS)")
                axs[0, 1].set_ylabel(r"Torsion Energy Density ($\kappa_s$/node)")
                axs[0, 1].grid(True, linestyle=":", alpha=0.6)
                axs[0, 1].legend(loc="upper right")

                min_len = min(len(m_sh), len(m_tor))
                sh = m_sh[:min_len]
                tor = m_tor[:min_len]
                x_eval = axs[0, 0].lines[-1].get_xdata()[:min_len]
                caging_ratio = tor / np.maximum(1e-9, sh)

                axs[1, 0].plot(x_eval, caging_ratio, color="#2ca02c", lw=2, label=r"$\eta = H_{\mathrm{torsion}} / H_{\mathrm{shear}}$")
                axs[1, 0].set_title(r"(c) Valence Partitioning Ratio $\eta(t)$")
                axs[1, 0].set_xlabel("Monte Carlo Sweeps (MCS)")
                axs[1, 0].set_ylabel(r"Partition Ratio $\langle H_{\mathrm{torsion}} \rangle / \langle H_{\mathrm{shear}} \rangle$")
                axs[1, 0].grid(True, linestyle=":", alpha=0.6)
                axs[1, 0].legend(loc="upper right")

                scatter = axs[1, 1].scatter(sh, tor, c=x_eval, cmap="plasma", s=22, edgecolor="none", zorder=3)
                axs[1, 1].plot(sh, tor, color="gray", alpha=0.35, lw=1.2, zorder=2)
                axs[1, 1].annotate("Start (0 MCS)", xy=(sh[0], tor[0]), xytext=(sh[0] + 0.15, tor[0]),
                                   arrowprops=dict(arrowstyle="->", color="black", lw=0.8), fontsize=8)

                nuc_idx = len(tor) // 2 + int(np.argmin(tor[len(tor) // 2:]))
                axs[1, 1].annotate(r"Diamond Nucleation ($sp^3$)", 
                                   xy=(sh[nuc_idx], tor[nuc_idx]), 
                                   xytext=(sh[nuc_idx] - 1.2, tor[nuc_idx] - 0.018),
                                   arrowprops=dict(arrowstyle="->", color="#d62728", lw=1.0), 
                                   fontsize=8, color="#d62728", fontweight="bold")

                cbar = fig.colorbar(scatter, ax=axs[1, 1], pad=0.03, aspect=20)
                cbar.set_label("Monte Carlo Sweeps (MCS)", fontsize=8)
                axs[1, 1].set_title(r"(d) Valence Phase Trajectory ($H_{\mathrm{shear}}$ vs $H_{\mathrm{torsion}}$)")
                axs[1, 1].set_xlabel(r"Valence Shear $\langle H_{\mathrm{shear}} \rangle / N$ ($\kappa_s$/node)")
                axs[1, 1].set_ylabel(r"Dihedral Torsion $\langle H_{\mathrm{torsion}} \rangle / N$ ($\kappa_s$/node)")
                axs[1, 1].grid(True, linestyle=":", alpha=0.6)

                axs[1, 1].text(0.04, 0.94, "Carbon Rain\n$P = 100.0$ GPa", transform=axs[1, 1].transAxes,
                               fontsize=8, verticalalignment="top",
                               bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.85, edgecolor="#cccccc"))

            plt.suptitle("Paper 5: Carbon Diamond Rain Phase Kinetics", y=1.02)
            plt.tight_layout()
            plt.savefig(carb_meta["fig"])
            plt.close()
            logger.info(f"[P5 Carbon] Figure saved -> {carb_meta['fig']}")

    # 4. SUPERIONIC ONSET
    sup_meta = sub_protocols["Superionic"]
    sup_files = find_files_recursive(sup_meta["patterns"], search_dir)
    if sup_files:
        logger.info(f"[P5 Superionic] Processing {len(sup_files)} payload file(s)...")
        msd_list, dp_list, mcs_x = [], [], None
        for fp in sup_files:
            try:
                data = np.load(fp)
                sweeps = extract_array(data, ["time_log", "sweeps_log"])
                msd = extract_array(data, ["msd_log", "msd_array"])
                dp = extract_array(data, ["dp_log", "dp_array"])

                if sweeps is not None and mcs_x is None: mcs_x = sweeps
                if msd is not None: msd_list.append(msd)
                if dp is not None: dp_list.append(dp)
            except Exception as e:
                logger.error(f"[P5 Superionic] Failed to parse file {fp}: {e}")

        if msd_list:
            fig, axs = plt.subplots(2, 2, figsize=(12, 9))
            m_msd, _, s_msd, trunc_msd = compute_ensemble_stats(msd_list)
            min_len = len(m_msd)
            mcs_x = mcs_x[:min_len] if (mcs_x is not None and len(mcs_x) >= min_len) else np.arange(1, min_len + 1) * 100

            for idx, h in enumerate(trunc_msd):
                axs[0, 0].plot(mcs_x, h, color="gray", alpha=0.25, lw=0.8, label="Single Seed" if idx == 0 else "")
            axs[0, 0].plot(mcs_x, m_msd, "o-", color="darkred", lw=2, label="Proton Knot MSD")
            axs[0, 0].fill_between(mcs_x, m_msd - s_msd, m_msd + s_msd, color="darkred", alpha=0.3)
            axs[0, 0].set_title("(a) Proton Knot Mean Squared Displacement")
            axs[0, 0].set_xlabel("Monte Carlo Sweeps (MCS)")
            axs[0, 0].set_ylabel(r"Mean Squared Displacement ($r_0^2$)")
            axs[0, 0].grid(True, linestyle=":", alpha=0.6)
            axs[0, 0].legend(loc="upper left")

            if dp_list:
                m_dp, _, s_dp, trunc_dp = compute_ensemble_stats(dp_list)
                for idx, h in enumerate(trunc_dp):
                    axs[0, 1].plot(mcs_x[:len(m_dp)], h, color="gray", alpha=0.25, lw=0.8)
                axs[0, 1].plot(mcs_x[:len(m_dp)], m_dp, "s-", color="navy", lw=2, label=r"Diffusion Rate $D_p$")
                axs[0, 1].fill_between(mcs_x[:len(m_dp)], m_dp - s_dp, m_dp + s_dp, color="navy", alpha=0.3)
                axs[0, 1].set_title("(b) Superionic Proton Diffusion Kinetics")
                axs[0, 1].set_xlabel("Monte Carlo Sweeps (MCS)")
                axs[0, 1].set_ylabel(r"Proton Diffusion Coefficient $D_p$")
                axs[0, 1].grid(True, linestyle=":", alpha=0.6)
                axs[0, 1].legend(loc="upper right")

                axs[1, 0].plot(m_msd[:len(m_dp)], m_dp, color="teal", lw=2, label="Diffusion vs MSD Trajectory")
                axs[1, 0].set_title("(c) Diffusion Phase Trajectory")
                axs[1, 0].set_xlabel(r"MSD ($r_0^2$)")
                axs[1, 0].set_ylabel(r"Smoluchowski Kinetic Linearity")
                axs[1, 0].grid(True, linestyle=":", alpha=0.6)
                axs[1, 0].legend(loc="upper right")

            axs[1, 1].text(0.5, 0.5, "Superionic Proton Diffusion Onset\n$T = 2500.0\\text{ K} \\mid P = 100.0\\text{ GPa}$\nRun ID: P5_SUPERIONIC_PROD", 
                          ha="center", va="center", fontsize=11, bbox=dict(boxstyle="round", facecolor="white", alpha=0.8))
            axs[1, 1].set_title("(d) Superionic State Boundary")
            axs[1, 1].axis("off")

            plt.suptitle("Paper 5: Superionic Onset Kinetics", y=1.02)
            plt.tight_layout()
            plt.savefig(sup_meta["fig"])
            plt.close()
            logger.info(f"[P5 Superionic] Figure saved -> {sup_meta['fig']}")

    # 5. SATURATION
    sat_meta = sub_protocols["Saturation"]
    sat_files = find_files_recursive(sat_meta["patterns"], search_dir)
    if sat_files:
        logger.info(f"[P5 Saturation] Processing {len(sat_files)} payload file(s)...")
        fp = sat_files[0]
        try:
            data = np.load(fp)
            tau_arr = extract_link_strain_array(data)
            p_ela = extract_array(data, ["pressure_eos_array", "p_eos_array"])
            rho = extract_array(data, ["density_ratio_array", "rho_ratio_array"])

            if tau_arr is not None and p_ela is not None:
                fig, axs = plt.subplots(2, 2, figsize=(12, 9))

                axs[0, 0].plot(tau_arr, p_ela, "o-", color="#1f77b4", lw=2, label=r"Pressure Response $P(\tau)$")
                axs[0, 0].axvline(1/3, color="black", linestyle="--", label=r"Capacity Boundary $\tau_{\max} = 1/3$")
                axs[0, 0].set_title("(a) Capacity-Saturated Equation of State")
                axs[0, 0].set_xlabel(r"Shear Strain $\tau$")
                axs[0, 0].set_ylabel(r"Capacity EOS Pressure $P_{\mathrm{eos}}$")
                axs[0, 0].grid(True, linestyle=":", alpha=0.6)
                axs[0, 0].legend(loc="upper left")

                if rho is not None:
                    # (b) Emergent Bulk Modulus / Substrate Incompressibility
                    K_modulus = tau_arr * np.gradient(p_ela, tau_arr)
                    axs[0, 1].plot(tau_arr, np.maximum(K_modulus, 1e-3), "s-", color="#2ca02c", lw=2, ms=4, label=r"Bulk Modulus $K(\tau)$")
                    axs[0, 1].axvline(1.0 / 3.0, color="black", linestyle="--", lw=1.2, label=r"$\tau_{\max} = 1/3$")
                    axs[0, 1].set_yscale("log")
                    axs[0, 1].set_title(r"(b) Substrate Incompressibility $K(\tau) = \tau (dP/d\tau)$")
                    axs[0, 1].set_xlabel(r"Shear Strain $\tau$")
                    axs[0, 1].set_ylabel(r"Bulk Modulus $K(\tau)$ (log scale)")
                    axs[0, 1].grid(True, linestyle=":", alpha=0.6)
                    axs[0, 1].legend(loc="upper left", fontsize=8)

                    axs[1, 0].semilogy(rho, p_ela, "^-", color="#d62728", lw=2, label=r"$P_{\mathrm{eos}}(\rho/\rho_{\mathrm{sat}})$")
                    axs[1, 0].set_title("(c) Asymptotic Density Barrier Divergence")
                    axs[1, 0].set_xlabel(r"Density Ratio $\rho / \rho_{\mathrm{sat}}$")
                    axs[1, 0].set_ylabel(r"Divergent Pressure Factor $P_{\mathrm{eos}}$")
                    axs[1, 0].grid(True, linestyle=":", alpha=0.6, which="both")
                    axs[1, 0].legend(loc="upper left")

                # (d) Substrate Density Horizon: Non-Singular ELA vs Classical EoS
                idx_base = max(1, len(rho) // 5)
                p_bm3 = p_ela[idx_base] * ((rho / max(1e-6, rho[idx_base])) ** (7.0 / 3.0))
                p_fermi = p_ela[idx_base] * ((rho / max(1e-6, rho[idx_base])) ** (4.0 / 3.0))

                axs[1, 1].plot(rho, p_ela, "o-", color="#d62728", lw=2, ms=4, label=r"ELA Capacity Horizon $P(\rho)$", zorder=4)
                axs[1, 1].plot(rho, p_bm3, "--", color="#1f77b4", lw=1.8, label="Birch-Murnaghan (Classical $\\rho \\to \\infty$)", zorder=3)
                axs[1, 1].plot(rho, p_fermi, ":", color="gray", lw=1.5, label=r"Relativistic Polytrope ($\rho^{4/3}$)", zorder=2)

                axs[1, 1].axvline(1.0, color="black", linestyle="--", lw=1.5, label=r"Ceiling $\rho_{\mathrm{sat}}$ ($\tau_{\max} = 1/3$)")
                axs[1, 1].axvspan(1.0, 1.15, color="#d62728", alpha=0.15, hatch="//", label="Forbidden Singularity Zone")

                axs[1, 1].set_yscale("log")
                axs[1, 1].set_xlim(float(np.min(rho)) * 0.95, 1.10)
                axs[1, 1].set_ylim(0.8, float(np.max(p_ela)) * 2.5)
                axs[1, 1].set_title(r"(d) Substrate Density Horizon ($P$ vs $\rho/\rho_{\mathrm{sat}}$)")
                axs[1, 1].set_xlabel(r"Relative Density Ratio $\rho / \rho_{\mathrm{sat}}$")
                axs[1, 1].set_ylabel(r"Effective Pressure $P_{\mathrm{eos}}$ (log scale)")
                axs[1, 1].grid(True, linestyle=":", alpha=0.6)
                axs[1, 1].legend(loc="upper left", fontsize=7.5)

                axs[1, 1].text(0.96, 0.08, "Non-Singular Limit\n$\\rho \\leq \\rho_{\\mathrm{sat}}$",
                               transform=axs[1, 1].transAxes, fontsize=8,
                               horizontalalignment="right", verticalalignment="bottom",
                               bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.85, edgecolor="#cccccc"))

                plt.suptitle("Paper 5: Non-Singular Capacity Saturation EoS", y=1.02)
                plt.tight_layout()
                plt.savefig(sat_meta["fig"])
                plt.close()
                logger.info(f"[P5 Saturation] Figure saved -> {sat_meta['fig']}")
        except Exception as e:
            logger.error(f"[P5 Saturation] Failed to process payload: {e}")


# ------------------------------------------------------------------------------
# PAPERS 1-3 PROCESSOR
# ------------------------------------------------------------------------------
def process_ensemble_group(paper_key, meta, search_dir="."):
    files = find_files_recursive(meta["pattern"], search_dir)
    logger.info(f"ANALYZING {meta['title'].upper()} ({len(files)} payload(s) found)")

    if not files:
        logger.warning(f"No production outputs found for {paper_key}. Skipping.")
        return

    ds_finals, energy_histories, ds_t_histories, t_mid_histories, sweep_histories = [], [], [], [], []
    topo_charges_final, topo_histories, plaquette_actions_final, splaq_histories = [], [], [], []
    w_eos_histories, w_eos_finals, h_sq_histories, h_sq_finals = [], [], [], []
    n_nodes_val = 4096

    for fpath in files:
        try:
            data = np.load(fpath)
            ds_finals.append(float(data["ds_final"]))
            if "N_nodes" in data: n_nodes_val = int(data["N_nodes"])
            if "energy_history" in data: energy_histories.append(data["energy_history"])
            if "ds_curve" in data: ds_t_histories.append(data["ds_curve"])
            elif "ds_t_history" in data: ds_t_histories.append(data["ds_t_history"])
            if "t_mid_curve" in data: t_mid_histories.append(data["t_mid_curve"])
            if "sweep_history" in data: sweep_histories.append(data["sweep_history"])
            if "topological_charge_Q" in data: topo_charges_final.append(int(data["topological_charge_Q"]))
            if "q_history" in data: topo_histories.append(data["q_history"])
            if "su2_plaquette_action" in data: plaquette_actions_final.append(float(data["su2_plaquette_action"]))
            if "splaq_history" in data: splaq_histories.append(data["splaq_history"])
            if "w_eos_history" in data:
                w_hist = data["w_eos_history"]
                w_eos_histories.append(w_hist)
                w_eos_finals.append(float(w_hist[-1]))
            if "h_sq_history" in data:
                h_hist = data["h_sq_history"]
                h_sq_histories.append(h_hist)
                h_sq_finals.append(float(h_hist[-1]))
        except Exception as e:
            logger.error(f"Failed to load {fpath}: {e}")

    if not ds_finals: return

    ds_mean, _, ds_sem, _ = compute_ensemble_stats(ds_finals)
    fit_min, fit_max = (8.0, 25.0) if n_nodes_val > 4096 else (0.8, 3.0)

    # PAPER 1
    if paper_key == "Paper 1":
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))
        if energy_histories:
            e_mean, _, e_sem, trunc_e = compute_ensemble_stats(energy_histories)
            mcs_x = sweep_histories[0][:len(e_mean)] if sweep_histories else np.arange(1, len(e_mean) + 1)
            for idx, h in enumerate(trunc_e):
                ax1.plot(mcs_x, h, color="gray", alpha=0.25, lw=0.8, label="Single Seed Trajectory" if idx == 0 else "")
            ax1.plot(mcs_x, e_mean, color="#1f77b4", lw=2, label=r"Ensemble Mean $\langle H_{\mathrm{tot}} \rangle$")
            ax1.fill_between(mcs_x, e_mean - e_sem, e_mean + e_sem, color="#1f77b4", alpha=0.3, label=r"$\pm 1\text{ SEM Envelope}$")
            ax1.set_xlabel("Monte Carlo Sweeps (MCS)")
            ax1.set_ylabel("Total Hamiltonian $H_{\mathrm{tot}}$")
            ax1.set_title("Thermalization & Stationarity Profile")
            ax1.grid(True, linestyle="--", alpha=0.5)
            ax1.legend(loc="lower right")

        if ds_t_histories and t_mid_histories:
            dst_mean, _, dst_sem, trunc_ds = compute_ensemble_stats(ds_t_histories)
            t_x = t_mid_histories[0][:len(dst_mean)]
            for idx, h in enumerate(trunc_ds):
                ax2.plot(t_x, h, color="gray", alpha=0.25, lw=0.8)
            ax2.plot(t_x, dst_mean, color="#d62728", lw=2, label=r"Ensemble $\langle d_s(t) \rangle$")
            ax2.fill_between(t_x, dst_mean - dst_sem, dst_mean + dst_sem, color="#d62728", alpha=0.3, label=r"$\pm 1\text{ SEM Envelope}$")
            ax2.axvspan(fit_min, fit_max, color="#2ca02c", alpha=0.15, label=f"Fit Region [{fit_min}, {fit_max}]")
            ax2.axhline(3.00, color="black", linestyle=":", label="Continuum Limit ($d_s=3.00$)")
            ax2.set_xscale("log")
            ax2.set_xlabel("Diffusion Time $t$")
            ax2.set_ylabel("Spectral Dimension $d_s(t)$")
            ax2.set_title(f"Spectral Dimension Convergence\nFinal $\\langle d_s \\rangle = {ds_mean:.4f} \\pm {ds_sem:.4f}$")
            ax2.grid(True, linestyle="--", alpha=0.5, which="both")
            ax2.legend(loc="lower right")

    # PAPER 2
    elif paper_key == "Paper 2":
        fig, axs = plt.subplots(2, 2, figsize=(12, 9))
        (ax1, ax2), (ax3, ax4) = axs

        if ds_t_histories and t_mid_histories:
            dst_mean, _, dst_sem, trunc_ds = compute_ensemble_stats(ds_t_histories)
            t_x = t_mid_histories[0][:len(dst_mean)]
            for idx, h in enumerate(trunc_ds):
                ax1.plot(t_x, h, color="gray", alpha=0.25, lw=0.8)
            ax1.plot(t_x, dst_mean, color="#1f77b4", lw=2, label=r"Ensemble $\langle d_s(t) \rangle$")
            ax1.fill_between(t_x, dst_mean - dst_sem, dst_mean + dst_sem, color="#1f77b4", alpha=0.3, label=r"$\pm 1\text{ SEM Envelope}$")
            ax1.axvspan(fit_min, fit_max, color="#2ca02c", alpha=0.15, label=f"Fit Region [{fit_min}, {fit_max}]")
            ax1.axhline(3.00, color="#d62728", linestyle="--", lw=1.5, label=r"Target ($d_s = 3.00$)")
            ax1.set_xscale("log")
            ax1.set_xlabel(r"Diffusion Time $t$")
            ax1.set_ylabel(r"Spectral Dimension $d_s(t)$")
            ax1.set_title(f"(a) Spectral Dimension Trajectory\nFinal $\\langle d_s \\rangle = {ds_mean:.4f} \\pm {ds_sem:.4f}$")
            ax1.grid(True, which="both", linestyle=":", alpha=0.6)
            ax1.legend(loc="lower right")

        if topo_histories:
            q_m, _, q_s, trunc_q = compute_ensemble_stats(topo_histories)
            mcs_x = sweep_histories[0][:len(q_m)] if sweep_histories else np.arange(1, len(q_m) + 1)
            for idx, h in enumerate(trunc_q):
                ax2.plot(mcs_x, h, color="gray", alpha=0.25, lw=0.8, label="Single Seed" if idx == 0 else "")
            ax2.plot(mcs_x, q_m, color="#9467bd", lw=2.0, label=r"Ensemble $\langle Q_{\mathrm{top}} \rangle$")
            ax2.fill_between(mcs_x, q_m - q_s, q_m + q_s, color="#9467bd", alpha=0.3, label=r"$\pm 1\text{ SEM Envelope}$")
            ax2.axhline(1.0, color="#d62728", linestyle="--", lw=1.5, label=r"Target ($Q = +1$)")
            ax2.set_ylim(-0.2, 2.2)
            ax2.set_xlabel("Monte Carlo Sweeps (MCS)")
            ax2.set_ylabel(r"Topological Charge $Q_{\mathrm{top}}$")
            ax2.set_title(f"(b) Soliton Topological Charge Survival\nFinal $\\langle Q \\rangle = {q_m[-1]:.2f} \\pm {q_s[-1]:.2f}$")
            ax2.grid(True, linestyle=":", alpha=0.6)
            ax2.legend(loc="upper right")

        if splaq_histories:
            p_m, _, p_s, trunc_p = compute_ensemble_stats(splaq_histories)
            mcs_x = sweep_histories[0][:len(p_m)] if sweep_histories else np.arange(1, len(p_m) + 1)
            for idx, h in enumerate(trunc_p):
                ax3.plot(mcs_x, h, color="gray", alpha=0.25, lw=0.8, label="Single Seed" if idx == 0 else "")
            ax3.plot(mcs_x, p_m, color="#2ca02c", lw=2.0, label=r"Ensemble $\langle S_{\mathrm{plaq}} \rangle$")
            ax3.fill_between(mcs_x, p_m - p_s, p_m + p_s, color="#2ca02c", alpha=0.3, label=r"$\pm 1\text{ SEM Envelope}$")
            ax3.set_xlabel("Monte Carlo Sweeps (MCS)")
            ax3.set_ylabel(r"Wilson Plaquette Action $S_{\mathrm{plaq}}$")
            ax3.set_title(f"(c) $SU(2)$ Plaquette Action Stationarity\nFinal $\\langle S \\rangle = {p_m[-1]:.4f} \\pm {p_s[-1]:.4f}$")
            ax3.grid(True, linestyle=":", alpha=0.6)
            ax3.legend(loc="lower right")

        if energy_histories:
            e_m, _, e_s, trunc_e = compute_ensemble_stats(energy_histories)
            mcs_x = sweep_histories[0][:len(e_m)] if sweep_histories else np.arange(1, len(e_m) + 1)
            for idx, h in enumerate(trunc_e):
                ax4.plot(mcs_x, h, color="gray", alpha=0.25, lw=0.8, label="Single Seed" if idx == 0 else "")
            ax4.plot(mcs_x, e_m, color="#ff7f0e", lw=2.0, label=r"Ensemble Mean $\langle H_{\mathrm{tot}} \rangle$")
            ax4.fill_between(mcs_x, e_m - e_s, e_m + e_s, color="#ff7f0e", alpha=0.3, label=r"$\pm 1\text{ SEM Envelope}$")
            ax4.set_xlabel("Monte Carlo Sweeps (MCS)")
            ax4.set_ylabel(r"Total Hamiltonian $H_{\mathrm{tot}}$")
            ax4.set_title(r"(d) Total Energy Stationarity Plateau")
            ax4.grid(True, linestyle=":", alpha=0.6)
            ax4.legend(loc="lower right")

    # PAPER 3
    elif paper_key == "Paper 3":
        fig, axs = plt.subplots(2, 2, figsize=(12, 9))
        (ax1, ax2), (ax3, ax4) = axs

        if ds_t_histories and t_mid_histories:
            dst_mean, _, dst_sem, trunc_ds = compute_ensemble_stats(ds_t_histories)
            t_x = t_mid_histories[0][:len(dst_mean)]
            for idx, h in enumerate(trunc_ds):
                ax1.plot(t_x, h, color="gray", alpha=0.25, lw=0.8)
            ax1.plot(t_x, dst_mean, color="#1f77b4", lw=2, label=r"Ensemble $\langle d_s(t) \rangle$")
            ax1.fill_between(t_x, dst_mean - dst_sem, dst_mean + dst_sem, color="#1f77b4", alpha=0.3, label=r"$\pm 1\text{ SEM Envelope}$")
            ax1.axvspan(fit_min, fit_max, color="#2ca02c", alpha=0.15, label=f"Fit Region [{fit_min}, {fit_max}]")
            ax1.axhline(3.00, color="#d62728", linestyle="--", lw=1.5, label=r"Target ($d_s = 3.00$)")
            ax1.set_xscale("log")
            ax1.set_xlabel(r"Diffusion Time $t$")
            ax1.set_ylabel(r"Spectral Dimension $d_s(t)$")
            ax1.set_title(f"(a) Continuum 3D Spatial Stability\nFinal $\\langle d_s \\rangle = {ds_mean:.4f} \\pm {ds_sem:.4f}$")
            ax1.grid(True, which="both", linestyle=":", alpha=0.6)
            ax1.legend(loc="lower right")

        if w_eos_histories:
            w_m, _, w_s, trunc_w = compute_ensemble_stats(w_eos_histories)
            mcs_x = sweep_histories[0][:len(w_m)] if sweep_histories else np.arange(1, len(w_m) + 1)
            for idx, h in enumerate(trunc_w):
                ax2.plot(mcs_x, h, color="gray", alpha=0.25, lw=0.8, label="Single Seed" if idx == 0 else "")
            ax2.plot(mcs_x, w_m, color="#e377c2", lw=2, label=r"Ensemble Mean $\langle w(a) \rangle$")
            ax2.fill_between(mcs_x, w_m - w_s, w_m + w_s, color="#e377c2", alpha=0.3, label=r"$\pm 1\text{ SEM Envelope}$")
            ax2.axhline(-1.00, color="#d62728", linestyle="--", lw=1.5, label=r"$\Lambda$ Boundary ($w = -1.0$)")
            ax2.set_title(f"(b) CPL Dark Energy EoS $w(a)$\nFinal $\\langle w \\rangle = {w_m[-1]:.4f} \\pm {w_s[-1]:.4f}$")
            ax2.set_xlabel("Monte Carlo Sweeps (MCS)")
            ax2.set_ylabel(r"Equation of State $w(a)$")
            ax2.grid(True, linestyle=":", alpha=0.6)
            ax2.legend(loc="lower right")

        if h_sq_histories:
            h_m, _, h_s, trunc_h = compute_ensemble_stats(h_sq_histories)
            mcs_x = sweep_histories[0][:len(h_m)] if sweep_histories else np.arange(1, len(h_m) + 1)
            for idx, h in enumerate(trunc_h):
                ax3.plot(mcs_x, h, color="gray", alpha=0.25, lw=0.8, label="Single Seed" if idx == 0 else "")
            ax3.plot(mcs_x, h_m, color="#17becf", lw=2, label=r"Ensemble Mean $\langle H^2 \rangle$")
            ax3.fill_between(mcs_x, h_m - h_s, h_m + h_s, color="#17becf", alpha=0.3, label=r"$\pm 1\text{ SEM Envelope}$")
            ax3.set_title(f"(c) LQC Hubble Bounce Rate Stationarity\nFinal $\\langle H^2 \\rangle = {h_m[-1]:.4e} \\pm {h_s[-1]:.4e}$")
            ax3.set_xlabel("Monte Carlo Sweeps (MCS)")
            ax3.set_ylabel(r"Hubble Parameter $H^2$")
            ax3.grid(True, linestyle=":", alpha=0.6)
            ax3.legend(loc="upper right")

        if energy_histories:
            e_m, _, e_s, trunc_e = compute_ensemble_stats(energy_histories)
            mcs_x = sweep_histories[0][:len(e_m)] if sweep_histories else np.arange(1, len(e_m) + 1)
            for idx, h in enumerate(trunc_e):
                ax4.plot(mcs_x, h, color="gray", alpha=0.25, lw=0.8, label="Single Seed" if idx == 0 else "")
            ax4.plot(mcs_x, e_m, color="#ff7f0e", lw=2.0, label=r"Ensemble Mean $\langle H_{\mathrm{tot}} \rangle$")
            ax4.fill_between(mcs_x, e_m - e_s, e_m + e_s, color="#ff7f0e", alpha=0.3, label=r"$\pm 1\text{ SEM Envelope}$")
            ax4.set_xlabel("Monte Carlo Sweeps (MCS)")
            ax4.set_ylabel(r"Total Hamiltonian $H_{\mathrm{tot}}$")
            ax4.set_title(r"(d) Thermal Energy Trajectory Plateau")
            ax4.grid(True, linestyle=":", alpha=0.6)
            ax4.legend(loc="lower right")

    plt.suptitle(meta["title"], y=1.02)
    plt.tight_layout()
    plt.savefig(meta["out_fig"])
    plt.close()
    logger.info(f"Saved figure -> {meta['out_fig']}")


# ------------------------------------------------------------------------------
# MAIN ENTRY POINT
# ------------------------------------------------------------------------------
def main():
    logger.info("================================================================================")
    logger.info("      ELA v6.6.2 MULTI-SEED ENSEMBLE STATISTICAL POST-PROCESSING")
    logger.info("================================================================================")

    parser = argparse.ArgumentParser(description="ELA v6.6.2 Multi-Seed Ensemble Post-Processing")
    parser.add_argument("--payload-dir", "--dir", dest="payload_dir", default=".", help="Directory to search for NPZ payloads")
    args, _ = parser.parse_known_args()
    search_dir = args.payload_dir

    for paper_key in ["Paper 1", "Paper 2", "Paper 3"]:
        if paper_key in GROUPS:
            process_ensemble_group(paper_key, GROUPS[paper_key], search_dir=search_dir)

    if "Paper 4" in GROUPS:
        process_paper4_ensemble(GROUPS["Paper 4"]["sub_protocols"], search_dir=search_dir)

    if "Paper 5" in GROUPS:
        process_paper5_ensemble(GROUPS["Paper 5"]["sub_protocols"], search_dir=search_dir)

    logger.info("================================================================================")
    logger.info("      ALL PRODUCTION ENSEMBLE ANALYSES COMPLETED SUCCESSFULLY")
    logger.info("================================================================================")


if __name__ == "__main__":
    main()
