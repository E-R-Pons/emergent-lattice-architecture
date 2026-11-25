#!/usr/bin/env python3
"""
================================================================================
EMERGENT LATTICE ARCHITECTURE (ELA) - MASTER CLI CONTROL ENTRY POINT
================================================================================
Module 5 of 5: Orchestrator, Argument Parser & Entry Point (main.py v6.6.2)

Provenance: [ELA ARCHITECTURE]
References:
  - Paper I   [ela_paper_i_2026]   : Foundations, Hydrodynamic Limits & Spacetime Emergence (DOI: 10.5281/zenodo.21843307)
  - Paper II  [ela_paper_ii_2026]  : Micro-Scale Soliton Topology, Gauges & Antimatter (DOI: 10.5281/zenodo.21843352)
  - Paper III [ela_paper_iii_2026] : Macro Cosmological Untensing, Geometrogenesis & Dark Energy (DOI: 10.5281/zenodo.21843375)
  - Paper IV  [ela_paper_iv_2026]  : Substrate Thermodynamics & Vacuum Kinetics (DOI: 10.5281/zenodo.23268981)
  - Paper V   [ela_paper_v_2026]   : Relational Condensed Matter & Extreme EoS (DOI: 10.5281/zenodo.23269009)
"""

import sys
import argparse

# Local module imports
from references import __references__
from simulation import (
    EngineMode,
    CondensedMatterMode,
    ThermoSweepMode,
    EPRMode,
    run_ela_simulation
)
from plotting import generate_diagnostics_plot


def main():
    """
    Master CLI orchestrator and entry point for ELA physics simulations.
    
    Provenance: [ELA ARCHITECTURE]
    """
    parser = argparse.ArgumentParser(
        description="ELA v6.6.2 Master Physics Engine (Papers I - V)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Bibliographic Reference Query Flag [ELA ARCHITECTURE]
    parser.add_argument("--references", "--citations", action="store_true", 
                        help="Display primary bibliographic reference registry and exit")

    # Primary Execution Mode Selection [PURE LITERATURE]
    parser.add_argument("--mode", type=int, default=1, choices=[1, 2, 3, 4, 5], 
                        help="Engine mode: 1=Paper1 Vac, 2=Paper2 Soliton, 3=Paper3 Cosmo, 4=Paper4 Thermo, 5=Paper5 Condensed Matter")
    
    # Sub-Protocol Selectors [ELA ARCHITECTURE]
    parser.add_argument("--condensed-mode", "--condensed_mode", type=str, 
                        choices=["compression", "h2o", "carbon", "superionic", "saturation"], default="compression",
                        dest="condensed_mode", help="Mode 5 protocol: 'compression', 'h2o', 'carbon', 'superionic', 'saturation'")
    parser.add_argument("--thermo-mode", "--thermo_mode", type=str, choices=["sweep", "quench", "fss"], default="sweep",
                        dest="thermo_mode", help="Mode 4 protocol: 'sweep' (Beta sweep), 'quench' (Kinetics), 'fss' (Scaling)")
    parser.add_argument("--epr-mode", "--epr_mode", type=str, choices=["dynamic", "static", "none"], default=None,
                        help="EPR shortcut handling (REQUIRED for --mode 3)")

    # Mode 5 Pressure & Temperature Parameters (Extended Alias Coverage) [ELA ADAPTED]
    parser.add_argument("--pressure", "--pressure-val", "--pressure_val", "--P-ext", "--p_ext", type=float, default=100.0, dest="pressure_val", help="External hydrostatic pressure P_ext (GPa)")
    parser.add_argument("--pressure-start", "--pressure_start", type=float, default=10.0, dest="pressure_start", help="Starting P_ext for compression sweep")
    parser.add_argument("--pressure-end", "--pressure_end", type=float, default=1000.0, dest="pressure_end", help="Ending P_ext for compression sweep")
    parser.add_argument("--pressure-steps", "--pressure_steps", type=int, default=20, dest="pressure_steps", help="Number of pressure steps")
    parser.add_argument("--temp", "--temp-val", "--temp_val", "--T-emergent", "--temp_emergent", type=float, default=2500.0, dest="temp_val", help="Emergent temperature T_emergent (K)")
    parser.add_argument("--temp-start", "--temp_start", type=float, default=300.0, dest="temp_start", help="Starting T_emergent for phase sweep")
    parser.add_argument("--temp-end", "--temp_end", type=float, default=5000.0, dest="temp_end", help="Ending T_emergent for phase sweep")
    parser.add_argument("--temp-steps", "--temp_steps", type=int, default=20, dest="temp_steps", help="Number of temperature steps")

    # Mode 4 Thermodynamics Parameters [PURE LITERATURE]
    parser.add_argument("--beta-start", "--beta_start", type=float, default=0.20, dest="beta_start", help="Mode 4 starting beta_eff")
    parser.add_argument("--beta-end", "--beta_end", type=float, default=3.50, dest="beta_end", help="Mode 4 ending beta_eff")
    parser.add_argument("--beta-steps", "--beta_steps", type=int, default=25, dest="beta_steps", help="Number of beta steps in Mode 4 sweep")
    parser.add_argument("--fss-dims", "--fss_dims", type=int, nargs="+", default=[8, 16, 32], dest="fss_dims", help="Grid dimensions for FSS protocol")

    # Topological Compliance Controls (Paper IV & Stress Tests)
    parser.add_argument("--compliance", "--enable-compliant-move3", action="store_true",
                        dest="enable_compliant_move3",
                        help="Enable Wooten-Winer-Weaire compliant coordinate relaxation in Move 3")
    parser.add_argument("--compliance-alpha", "--compliance_alpha", type=float, default=0.15,
                        dest="compliance_alpha",
                        help="Virtual coordinate relaxation displacement fraction alpha in [0.05, 0.25]")

    # General Physics & Simulation Control [ELA REPRODUCIBILITY]
    parser.add_argument("--soliton", "--inject-soliton", action="store_true", dest="inject_soliton", help="Inject Skyrmionic SU(2) topological soliton field (Paper 2)")
    parser.add_argument("--q-charge", "--soliton-q", "--q_charge", type=int, default=0, dest="q_charge", help="Target topological winding charge Q to inject")
    parser.add_argument("--run_id", "--run-id", type=str, default="RUN-V656_PRODUCTION", dest="run_id", help="Unique identifier for run")
    parser.add_argument("--seed", type=int, default=None, metavar="INT", help="Optional PRNG seed")
    parser.add_argument("--dim", type=int, default=16, help="Grid dimension cells")
    parser.add_argument("--beta", type=float, default=3.0035, help="Inverse temperature beta")
    parser.add_argument("--beta-gauge", "--beta_gauge", type=float, default=6.15, dest="beta_gauge", help="Gauge coupling beta_gauge for Wilson Plaquette Action")
    parser.add_argument("--ks", "--kappa_s", type=float, default=1.00, dest="kappa_s", help="Shear coupling")
    parser.add_argument("--kt", "--kappa_t", type=float, default=0.03, dest="kappa_t", help="Torsion coupling")
    parser.add_argument("--kr", "--kappa_r", type=float, default=0.00, dest="kappa_r", help="Stretch coupling")
    parser.add_argument("--lj", "--lambda_j", type=float, default=0.141421356, dest="lambda_j", help="Gauge phase jamming coupling")
    parser.add_argument("--snr-crit", "--snr_crit", type=float, default=6.50, dest="snr_crit", help="SNR threshold for co-moving sleeve core protection")
    parser.add_argument("--cutoff", "--cutoff_prefactor", type=float, default=3.85, dest="cutoff_prefactor", help="Cutoff prefactor multiplying r0^2")
    parser.add_argument("--sleeve-mode", "--sleeve_mode", type=int, default=1, choices=[0, 1], dest="sleeve_mode", help="Co-moving sleeve mode: 0=Step-Function, 1=Continuous Fermi-Dirac")
    parser.add_argument("--sleeve-sigma", "--sleeve_sigma", type=float, default=0.10, dest="sleeve_sigma", help="Fermi-Dirac boundary softness width sigma_sleeve")
    parser.add_argument("--sleeve-weight", "--sleeve_weight", type=float, default=1.0, dest="sleeve_weight", help="Gauge jamming weight factor w_g in coupled L2 norm")
    parser.add_argument("--sleeve-tunnel-alpha", "--sleeve_tunnel_alpha", type=float, default=0.05, dest="sleeve_tunnel_alpha", help="Hyperbolic tunneling distance sensitivity alpha_tunnel")
    parser.add_argument("--beta-untensing", type=float, default=0.0175, help="Viscoelastic untensing exponent beta")
    parser.add_argument("--epsilon-sw", type=float, default=0.002, help="Small-world EPR shortcut transition ceiling")
    parser.add_argument("--steps", type=int, default=50000, help="Total Monte Carlo sweeps")
    parser.add_argument("--out_dir", type=str, default=".", help="Directory for output payload and plots")
    parser.add_argument("--plot", action="store_true", help="Generate diagnostic plots after run")

    args = parser.parse_args()

    # Handle Reference Query Flag [ELA ARCHITECTURE]
    if args.references:
        print("\n================================================================================")
        print("         EMERGENT LATTICE ARCHITECTURE (ELA) - BIBLIOGRAPHIC REGISTRY")
        print("================================================================================\n")
        for key, ref in __references__.items():
            print(f" [{key}]")
            print(f"   Title   : {ref.get('title', 'N/A')}")
            print(f"   Authors : {ref.get('authors', 'N/A')}")
            print(f"   Journal : {ref.get('journal', ref.get('publisher', 'N/A'))}")
            print(f"   Year    : {ref.get('year', 'N/A')}\n")
        sys.exit(0)

    # Rule Validation [ELA REPRODUCIBILITY]
    if args.mode == 3 and args.epr_mode is None:
        parser.error("[CONFIG ERROR] --mode 3 (Paper 3 Macro Cosmology) requires an explicit EPR configuration flag.\n"
                     "Please specify --epr-mode {dynamic, static, none} to ensure reproducible physics.")

    q_charge_target = args.q_charge
    if args.inject_soliton and q_charge_target == 0:
        q_charge_target = 1

    # Enum Mapping [ELA ARCHITECTURE]
    mode_map = {
        1: EngineMode.PAPER1_VACUUM,
        2: EngineMode.PAPER2_GAUGE_SOLITON,
        3: EngineMode.PAPER3_COSMOLOGY,
        4: EngineMode.PAPER4_THERMODYNAMICS,
        5: EngineMode.PAPER5_CONDENSED_MATTER
    }
    selected_mode = mode_map[args.mode]

    epr_map = {
        "dynamic": EPRMode.DYNAMIC,
        "static": EPRMode.STATIC,
        "none": EPRMode.NONE
    }
    selected_epr = epr_map.get(args.epr_mode, EPRMode.NONE)

    thermo_map = {
        "sweep": ThermoSweepMode.BETA_SWEEP,
        "quench": ThermoSweepMode.QUENCH_KINETICS,
        "fss": ThermoSweepMode.FSS_ANALYSIS
    }
    selected_thermo = thermo_map.get(args.thermo_mode, ThermoSweepMode.BETA_SWEEP)

    condensed_map = {
        "compression": CondensedMatterMode.HYDROSTATIC_COMPRESSION,
        "h2o": CondensedMatterMode.PHASE_DIAGRAM_H2O,
        "carbon": CondensedMatterMode.DIAMOND_RAIN_CARBON,
        "superionic": CondensedMatterMode.SUPERIONIC_ONSET,
        "saturation": CondensedMatterMode.CAPACITY_SATURATION
    }
    selected_condensed = condensed_map.get(args.condensed_mode, CondensedMatterMode.HYDROSTATIC_COMPRESSION)

    # Automatically activate compliance for Mode 4 unless explicitly disabled
    compliance_active = args.enable_compliant_move3 or (selected_mode == EngineMode.PAPER4_THERMODYNAMICS)

    # Route execution into simulation driver [ELA ARCHITECTURE]
    npz_file = run_ela_simulation(
        mode=selected_mode,
        thermo_mode=selected_thermo,
        condensed_mode=selected_condensed,
        pressure_val=args.pressure_val,
        pressure_start=args.pressure_start,
        pressure_end=args.pressure_end,
        pressure_steps=args.pressure_steps,
        temp_val=args.temp_val,
        temp_start=args.temp_start,
        temp_end=args.temp_end,
        temp_steps=args.temp_steps,
        epr_mode=selected_epr,
        run_id=args.run_id,
        grid_dim=args.dim,
        beta_mc=args.beta,
        beta_gauge=args.beta_gauge,
        beta_start=args.beta_start,
        beta_end=args.beta_end,
        beta_steps=args.beta_steps,
        fss_dims=args.fss_dims,
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
        sleeve_tunnel_alpha=args.sleeve_tunnel_alpha,
        enable_compliant_move3=compliance_active,
        compliance_alpha=args.compliance_alpha
    )

    # Trigger visualization if requested [ELA ARCHITECTURE]
    if args.plot and npz_file:
        generate_diagnostics_plot(npz_file, out_dir=args.out_dir)


if __name__ == "__main__":
    main()