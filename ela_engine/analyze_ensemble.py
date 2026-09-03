#!/usr/bin/env python3
"""
================================================================================
ELA V4.4.2 PRODUCTION ENSEMBLE ANALYSIS & PUBLICATION PLOTTER
================================================================================
Aggregates multi-seed NPZ outputs from production runs across Paper 1, Paper 2,
and Paper 3. Calculates ensemble means and standard errors (SEM = sigma / sqrt(K)),
outputs LaTeX-ready summary tables, and saves multi-panel publication-quality 
figures with shaded 1-sigma SEM confidence envelopes.
================================================================================
"""

import glob
import os
import numpy as np
import matplotlib.pyplot as plt

# Publication-grade Matplotlib configuration
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
    }
}


def compute_ensemble_stats(arrays):
    """Calculates mean, std, and SEM across axis 0 of stacked run arrays."""
    stacked = np.array(arrays)
    mean = np.mean(stacked, axis=0)
    std = np.std(stacked, axis=0, ddof=1) if len(arrays) > 1 else np.zeros_like(mean)
    sem = std / np.sqrt(len(arrays))
    return mean, std, sem


def process_ensemble_group(paper_key, meta):
    files = sorted(glob.glob(meta["pattern"]))
    print(f"\n================================================================================")
    print(f" ANALYZING {meta['title'].upper()}")
    print(f" Found {len(files)} seed payload(s) matching pattern: {meta['pattern']}")
    print(f"================================================================================")

    if not files:
        print(f" [WARN] No production outputs found for {paper_key}. Skipping.")
        return

    ds_finals = []
    energy_histories = []
    ds_t_histories = []
    t_mid_histories = []
    sweep_histories = []
    
    # Scalar metrics & time series for Paper 2
    topo_charges_final = []
    topo_histories = []
    plaquette_actions_final = []
    splaq_histories = []
    
    # Paper 3 histories
    w_eos_histories = []
    w_eos_finals = []
    h_sq_histories = []
    h_sq_finals = []
    
    n_nodes_val = 4096

    for fpath in files:
        try:
            data = np.load(fpath)
            ds_finals.append(float(data["ds_final"]))
            
            if "energy_history" in data:
                energy_histories.append(data["energy_history"])

            if "N_nodes" in data:
                n_nodes_val = int(data["N_nodes"])

            if "ds_curve" in data:
                ds_t_histories.append(data["ds_curve"])
            elif "ds_t_history" in data:
                ds_t_histories.append(data["ds_t_history"])

            if "t_mid_curve" in data:
                t_mid_histories.append(data["t_mid_curve"])

            if "sweep_history" in data:
                sweep_histories.append(data["sweep_history"])

            # Paper 2 Soliton / Gauge Data
            if "topological_charge_Q" in data:
                topo_charges_final.append(int(data["topological_charge_Q"]))
            if "q_history" in data:
                topo_histories.append(data["q_history"])

            if "su2_plaquette_action" in data:
                plaquette_actions_final.append(float(data["su2_plaquette_action"]))
            if "splaq_history" in data:
                splaq_histories.append(data["splaq_history"])

            # Paper 3 Cosmology Data
            if "w_eos_history" in data:
                w_hist = data["w_eos_history"]
                w_eos_histories.append(w_hist)
                w_eos_finals.append(float(w_hist[-1]))

            if "h_sq_history" in data:
                h_hist = data["h_sq_history"]
                h_sq_histories.append(h_hist)
                h_sq_finals.append(float(h_hist[-1]))

        except Exception as e:
            print(f" [ERROR] Failed to load {fpath}: {str(e)}")

    if not ds_finals:
        print(f" [WARN] Failed to parse valid numerical payloads for {paper_key}. Skipping.")
        return

    k_count = len(ds_finals)
    ds_mean, ds_std, ds_sem = compute_ensemble_stats(ds_finals)
    print(f" Multi-Seed Ensemble Count (K) : {k_count}")
    print(f" Spectral Dimension <d_s>     : {ds_mean:.4f} +/- {ds_sem:.4f} (std = {ds_std:.4f})")

    if topo_charges_final:
        q_mean, _, q_sem = compute_ensemble_stats(topo_charges_final)
        print(f" Topological Charge <Q_top>   : {q_mean:.2f} +/- {q_sem:.2f} (Invariance Check: {set(topo_charges_final)})")

    if plaquette_actions_final:
        p_mean, _, p_sem = compute_ensemble_stats(plaquette_actions_final)
        print(f" Wilson Plaquette <S_plaq>   : {p_mean:.5f} +/- {p_sem:.5f}")

    if w_eos_finals:
        w_mean, _, w_sem = compute_ensemble_stats(w_eos_finals)
        print(f" Dark Energy EoS <w(a)>       : {w_mean:.4f} +/- {w_sem:.4f}")

    if h_sq_finals:
        h_mean, _, h_sem = compute_ensemble_stats(h_sq_finals)
        print(f" LQC Bounce Rate <H^2>        : {h_mean:.6e} +/- {h_sem:.6e}")

    # Determine X-axis for MCS sweep trajectories cleanly
    min_mcs_len = min(len(h) for h in energy_histories) if energy_histories else 0
    if sweep_histories and min_mcs_len > 0:
        mcs_x = sweep_histories[0][:min_mcs_len]
    elif min_mcs_len > 0:
        mcs_x = np.arange(1, min_mcs_len + 1)
    else:
        mcs_x = np.array([])

    fit_min, fit_max = (8.0, 25.0) if n_nodes_val > 4096 else (0.8, 3.0)

    # ==========================================================================
    # FIGURE GENERATION PER PAPER MODE
    # ==========================================================================
    
    # --------------------------------------------------------------------------
    # PAPER 1: VACUUM SPACETIME CONTINUUM (1 x 2 PANELS)
    # --------------------------------------------------------------------------
    if paper_key == "Paper 1":
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))

        # Panel (a): Energy Thermalization Trajectories
        if energy_histories:
            truncated_energies = [h[:min_mcs_len] for h in energy_histories]
            e_mean, _, e_sem = compute_ensemble_stats(truncated_energies)

            for idx, h in enumerate(truncated_energies):
                ax1.plot(mcs_x, h, color="gray", alpha=0.25, lw=0.8, label="Single Seed Trajectory" if idx == 0 else "")

            ax1.plot(mcs_x, e_mean, color="#1f77b4", label=r"Ensemble Mean $\langle H_{\mathrm{tot}} \rangle$")
            ax1.fill_between(mcs_x, e_mean - e_sem, e_mean + e_sem, color="#1f77b4", alpha=0.3, label=r"$\pm 1\text{ SEM Envelope}$")
            ax1.set_xlabel("Monte Carlo Sweeps (MCS)")
            ax1.set_ylabel("Total Hamiltonian $H_{\mathrm{tot}}$")
            ax1.set_title("Thermalization & Stationarity Profile")
            ax1.grid(True, linestyle="--", alpha=0.5)
            ax1.legend(loc="lower right")

        # Panel (b): Spectral Dimension Probe / Profile
        if ds_t_histories and t_mid_histories:
            min_t_len = min(len(h) for h in ds_t_histories)
            truncated_ds_t = [h[:min_t_len] for h in ds_t_histories]
            t_x = t_mid_histories[0][:min_t_len]
            dst_mean, _, dst_sem = compute_ensemble_stats(truncated_ds_t)

            for idx, h in enumerate(truncated_ds_t):
                ax2.plot(t_x, h, color="gray", alpha=0.25, lw=0.8)

            ax2.plot(t_x, dst_mean, color="#d62728", label=r"Ensemble $\langle d_s(t) \rangle$")
            ax2.fill_between(t_x, dst_mean - dst_sem, dst_mean + dst_sem, color="#d62728", alpha=0.3, label=r"$\pm 1\text{ SEM Envelope}$")
            ax2.axvspan(fit_min, fit_max, color="#2ca02c", alpha=0.15, label=f"Fit Region [{fit_min}, {fit_max}]")
            ax2.axhline(3.00, color="black", linestyle=":", label="Continuum Limit ($d_s=3.00$)")
            ax2.set_xscale("log")
            ax2.set_xlabel("Diffusion Time $t$")
            ax2.set_ylabel("Spectral Dimension $d_s(t)$")
            ax2.set_title("Spectral Dimension Convergence")
            ax2.grid(True, linestyle="--", alpha=0.5, which="both")
            ax2.legend(loc="lower right")
        else:
            ax2.hist(ds_finals, bins=max(3, k_count), color="#2ca02c", edgecolor="black", alpha=0.7)
            ax2.axvline(np.mean(ds_finals), color="red", linestyle="--", label=f"Mean = {np.mean(ds_finals):.4f}")
            ax2.set_xlabel("Final Spectral Dimension $d_s$")
            ax2.set_ylabel("Seed Frequency")
            ax2.set_title("Ensemble Distribution $d_s$")
            ax2.legend()

    # --------------------------------------------------------------------------
    # PAPER 2: SU(2) SKYRMIONIC SOLITON (2 x 2 PANELS)
    # --------------------------------------------------------------------------
    elif paper_key == "Paper 2":
        fig, axs = plt.subplots(2, 2, figsize=(12, 9))
        (ax1, ax2), (ax3, ax4) = axs

        # Subplot (a): Spectral Dimension Convergence
        if ds_t_histories and t_mid_histories:
            min_t_len = min(len(h) for h in ds_t_histories)
            truncated_ds_t = [h[:min_t_len] for h in ds_t_histories]
            t_x = t_mid_histories[0][:min_t_len]
            dst_mean, _, dst_sem = compute_ensemble_stats(truncated_ds_t)

            for idx, h in enumerate(truncated_ds_t):
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

        # Subplot (b): Soliton Topological Charge Survival
        if topo_histories:
            min_q_len = min(len(h) for h in topo_histories)
            truncated_q = [h[:min_q_len] for h in topo_histories]
            q_m_seq, _, q_s_seq = compute_ensemble_stats(truncated_q)
            q_x = mcs_x[:min_q_len] if len(mcs_x) >= min_q_len else np.arange(1, min_q_len + 1)

            for idx, h in enumerate(truncated_q):
                ax2.plot(q_x, h, color="gray", alpha=0.25, lw=0.8, label="Single Seed" if idx == 0 else "")

            ax2.plot(q_x, q_m_seq, color="#9467bd", lw=2.0, label=r"Ensemble $\langle Q_{\mathrm{top}} \rangle$")
            ax2.fill_between(q_x, q_m_seq - q_s_seq, q_m_seq + q_s_seq, color="#9467bd", alpha=0.3, label=r"$\pm 1\text{ SEM Envelope}$")
            ax2.axhline(1.0, color="#d62728", linestyle="--", lw=1.5, label=r"Target ($Q = +1$)")
            ax2.set_ylim(-0.2, 2.2)
            ax2.set_xlabel("Monte Carlo Sweeps (MCS)")
            ax2.set_ylabel(r"Topological Charge $Q_{\mathrm{top}}$")
            ax2.set_title(f"(b) Soliton Topological Charge Survival\nFinal $\\langle Q \\rangle = {q_m_seq[-1]:.2f} \\pm {q_s_seq[-1]:.2f}$")
            ax2.grid(True, linestyle=":", alpha=0.6)
            ax2.legend(loc="upper right")
        elif topo_charges_final:
            q_m, _, q_s = compute_ensemble_stats(topo_charges_final)
            for idx, q in enumerate(topo_charges_final):
                ax2.plot(mcs_x, np.full_like(mcs_x, q), color="gray", alpha=0.3, lw=1.0, label="Single Seed" if idx == 0 else "")
            ax2.axhline(q_m, color="#9467bd", lw=2.5, label=f"Ensemble $\\langle Q_{{\\mathrm{{top}}}} \\rangle = {q_m:.2f} \\pm {q_s:.2f}$")
            ax2.axhline(1.0, color="#d62728", linestyle="--", lw=1.5, label=r"Target ($Q = +1$)")
            ax2.set_ylim(-0.2, 2.2)
            ax2.set_xlabel("Monte Carlo Sweeps (MCS)")
            ax2.set_ylabel(r"Topological Charge $Q_{\mathrm{top}}$")
            ax2.set_title(r"(b) Soliton Topological Charge Survival")
            ax2.grid(True, linestyle=":", alpha=0.6)
            ax2.legend(loc="upper right")

        # Subplot (c): SU(2) Wilson Plaquette Action
        if splaq_histories:
            min_p_len = min(len(h) for h in splaq_histories)
            truncated_p = [h[:min_p_len] for h in splaq_histories]
            p_m_seq, _, p_s_seq = compute_ensemble_stats(truncated_p)
            p_x = mcs_x[:min_p_len] if len(mcs_x) >= min_p_len else np.arange(1, min_p_len + 1)

            for idx, h in enumerate(truncated_p):
                ax3.plot(p_x, h, color="gray", alpha=0.25, lw=0.8, label="Single Seed" if idx == 0 else "")

            ax3.plot(p_x, p_m_seq, color="#2ca02c", lw=2.0, label=r"Ensemble $\langle S_{\mathrm{plaq}} \rangle$")
            ax3.fill_between(p_x, p_m_seq - p_s_seq, p_m_seq + p_s_seq, color="#2ca02c", alpha=0.3, label=r"$\pm 1\text{ SEM Envelope}$")
            ax3.set_xlabel("Monte Carlo Sweeps (MCS)")
            ax3.set_ylabel(r"Wilson Plaquette Action $S_{\mathrm{plaq}}$")
            ax3.set_title(f"(c) $SU(2)$ Plaquette Action Stationarity\nFinal $\\langle S \\rangle = {p_m_seq[-1]:.4f} \\pm {p_s_seq[-1]:.4f}$")
            ax3.grid(True, linestyle=":", alpha=0.6)
            ax3.legend(loc="lower right")
        elif plaquette_actions_final:
            p_m, _, p_s = compute_ensemble_stats(plaquette_actions_final)
            for idx, p in enumerate(plaquette_actions_final):
                ax3.plot(mcs_x, np.full_like(mcs_x, p), color="gray", alpha=0.3, lw=1.0, label="Single Seed" if idx == 0 else "")
            ax3.axhline(p_m, color="#2ca02c", lw=2.5, label=f"Ensemble $\\langle S_{{\\mathrm{{plaq}}}} \\rangle = {p_m:.4f} \\pm {p_s:.4f}$")
            ax3.set_xlabel("Monte Carlo Sweeps (MCS)")
            ax3.set_ylabel(r"Wilson Plaquette Action $S_{\mathrm{plaq}}$")
            ax3.set_title(r"(c) $SU(2)$ Plaquette Action Stationarity")
            ax3.grid(True, linestyle=":", alpha=0.6)
            ax3.legend(loc="lower right")

        # Subplot (d): Total Energy Trajectory
        if energy_histories:
            truncated_energies = [h[:min_mcs_len] for h in energy_histories]
            e_mean, _, e_sem = compute_ensemble_stats(truncated_energies)

            for idx, h in enumerate(truncated_energies):
                ax4.plot(mcs_x, h, color="gray", alpha=0.25, lw=0.8, label="Single Seed" if idx == 0 else "")

            ax4.plot(mcs_x, e_mean, color="#ff7f0e", lw=2.0, label=r"Ensemble Mean $\langle H_{\mathrm{tot}} \rangle$")
            ax4.fill_between(mcs_x, e_mean - e_sem, e_mean + e_sem, color="#ff7f0e", alpha=0.3, label=r"$\pm 1\text{ SEM Envelope}$")
            ax4.set_xlabel("Monte Carlo Sweeps (MCS)")
            ax4.set_ylabel(r"Total Hamiltonian $H_{\mathrm{tot}}$")
            ax4.set_title(r"(d) Total Energy Stationarity Plateau")
            ax4.grid(True, linestyle=":", alpha=0.6)
            ax4.legend(loc="lower right")

    # --------------------------------------------------------------------------
    # PAPER 3: MACRO COSMOLOGY & LQC BOUNCE (2 x 2 PANELS)
    # --------------------------------------------------------------------------
    elif paper_key == "Paper 3":
        fig, axs = plt.subplots(2, 2, figsize=(12, 9))
        (ax1, ax2), (ax3, ax4) = axs

        # Subplot (a): Spectral Dimension Stability
        if ds_t_histories and t_mid_histories:
            min_t_len = min(len(h) for h in ds_t_histories)
            truncated_ds_t = [h[:min_t_len] for h in ds_t_histories]
            t_x = t_mid_histories[0][:min_t_len]
            dst_mean, _, dst_sem = compute_ensemble_stats(truncated_ds_t)

            for idx, h in enumerate(truncated_ds_t):
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

        # Subplot (b): Dark Energy Equation of State w(a)
        if w_eos_histories:
            min_w_len = min(len(h) for h in w_eos_histories)
            truncated_w = [h[:min_w_len] for h in w_eos_histories]
            w_m_seq, _, w_s_seq = compute_ensemble_stats(truncated_w)
            w_x = mcs_x[:min_w_len] if len(mcs_x) >= min_w_len else np.arange(1, min_w_len + 1)

            for idx, h in enumerate(truncated_w):
                ax2.plot(w_x, h, color="gray", alpha=0.25, lw=0.8, label="Single Seed" if idx == 0 else "")

            ax2.plot(w_x, w_m_seq, color="#e377c2", lw=2, label=r"Ensemble Mean $\langle w(a) \rangle$")
            ax2.fill_between(w_x, w_m_seq - w_s_seq, w_m_seq + w_s_seq, color="#e377c2", alpha=0.3, label=r"$\pm 1\text{ SEM Envelope}$")
            ax2.axhline(-1.00, color="#d62728", linestyle="--", lw=1.5, label=r"$\Lambda$ Boundary ($w = -1.0$)")
            w_final_val = w_m_seq[-1]
            ax2.set_title(f"(b) CPL Dark Energy EoS $w(a)$\nFinal $\\langle w \\rangle = {w_final_val:.4f} \\pm {w_s_seq[-1]:.4f}$")
            ax2.set_xlabel("Monte Carlo Sweeps (MCS)")
            ax2.set_ylabel(r"Equation of State $w(a)$")
            ax2.grid(True, linestyle=":", alpha=0.6)
            ax2.legend(loc="lower right")

        # Subplot (c): Loop Quantum Cosmology (LQC) Hubble Bounce Rate H^2
        if h_sq_histories:
            min_h_len = min(len(h) for h in h_sq_histories)
            truncated_h = [h[:min_h_len] for h in h_sq_histories]
            h_m_seq, _, h_s_seq = compute_ensemble_stats(truncated_h)
            h_x = mcs_x[:min_h_len] if len(mcs_x) >= min_h_len else np.arange(1, min_h_len + 1)

            for idx, h in enumerate(truncated_h):
                ax3.plot(h_x, h, color="gray", alpha=0.25, lw=0.8, label="Single Seed" if idx == 0 else "")

            ax3.plot(h_x, h_m_seq, color="#17becf", lw=2, label=r"Ensemble Mean $\langle H^2 \rangle$")
            ax3.fill_between(h_x, h_m_seq - h_s_seq, h_m_seq + h_s_seq, color="#17becf", alpha=0.3, label=r"$\pm 1\text{ SEM Envelope}$")
            h_final_val = h_m_seq[-1]
            ax3.set_title(f"(c) LQC Hubble Bounce Rate Stationarity\nFinal $\\langle H^2 \\rangle = {h_final_val:.4e} \\pm {h_s_seq[-1]:.4e}$")
            ax3.set_xlabel("Monte Carlo Sweeps (MCS)")
            ax3.set_ylabel(r"Hubble Parameter $H^2$")
            ax3.grid(True, linestyle=":", alpha=0.6)
            ax3.legend(loc="upper right")

        # Subplot (d): Total Energy Trajectory
        if energy_histories:
            truncated_energies = [h[:min_mcs_len] for h in energy_histories]
            e_mean, _, e_sem = compute_ensemble_stats(truncated_energies)

            for idx, h in enumerate(truncated_energies):
                ax4.plot(mcs_x, h, color="gray", alpha=0.25, lw=0.8, label="Single Seed" if idx == 0 else "")

            ax4.plot(mcs_x, e_mean, color="#ff7f0e", lw=2.0, label=r"Ensemble Mean $\langle H_{\mathrm{tot}} \rangle$")
            ax4.fill_between(mcs_x, e_mean - e_sem, e_mean + e_sem, color="#ff7f0e", alpha=0.3, label=r"$\pm 1\text{ SEM Envelope}$")
            ax4.set_xlabel("Monte Carlo Sweeps (MCS)")
            ax4.set_ylabel(r"Total Hamiltonian $H_{\mathrm{tot}}$")
            ax4.set_title(r"(d) Thermal Energy Trajectory Plateau")
            ax4.grid(True, linestyle=":", alpha=0.6)
            ax4.legend(loc="lower right")

    plt.suptitle(meta["title"], y=1.02)
    plt.tight_layout()
    plt.savefig(meta["out_fig"])
    plt.close()

    print(f" Output figure saved -> {meta['out_fig']}")

    # Print LaTeX Table Snippet
    print(f"\n--- LaTeX Table Row ({paper_key}) ---")
    latex_row = f"{paper_key} & ${k_count}$ & ${ds_mean:.4f} \\pm {ds_sem:.4f}$"
    if topo_charges_final:
        q_m, _, q_s = compute_ensemble_stats(topo_charges_final)
        latex_row += f" & ${q_m:.2f} \\pm {q_s:.2f}$"
    if plaquette_actions_final:
        p_m, _, p_s = compute_ensemble_stats(plaquette_actions_final)
        latex_row += f" & ${p_m:.4f} \\pm {p_s:.4f}$"
    if w_eos_finals:
        w_m, _, w_s = compute_ensemble_stats(w_eos_finals)
        latex_row += f" & ${w_m:.4f} \\pm {w_s:.4f}$"
    if h_sq_finals:
        h_m, _, h_s = compute_ensemble_stats(h_sq_finals)
        latex_row += f" & ${h_m:.4e} \\pm {h_s:.4e}$"
    latex_row += r" \\"
    print(latex_row)


def main():
    print("================================================================================")
    print("      ELA v4.4.2 MULTI-SEED ENSEMBLE STATISTICAL POST-PROCESSING")
    print("================================================================================")

    for paper_key, meta in GROUPS.items():
        process_ensemble_group(paper_key, meta)

    print("\n================================================================================")
    print("      ALL PRODUCTION ENSEMBLE ANALYSES COMPLETED SUCCESSFULLY")
    print("================================================================================")


if __name__ == "__main__":
    main()
