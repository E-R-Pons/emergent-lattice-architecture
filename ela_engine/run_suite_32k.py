#!/usr/bin/env python3
"""
================================================================================
           EMERGENT LATTICE ARCHITECTURE (ELA) ENGINE v6.6.2
               PRODUCTION 32K BENCHMARK SUITE ORCHESTRATOR
================================================================================
Standardized 32k-node (grid_dim = 64) benchmark protocols across Papers I-V[cite: 34].
Inherits all v6.6.2 defaults (cutoff_prefactor=3.85, snr_crit=7.5,
sleeve_sigma=0.02, sleeve_weight=1.0) directly from simulation.py[cite: 34].

Usage:
    python run_suite_32k.py --all
    python run_suite_32k.py --paper 1 2 3
    python run_suite_32k.py --paper 4 --p4_mode sweep
    python run_suite_32k.py --paper 5 --p5_mode hydrostatic
================================================================================
"""

import argparse
import datetime
import os
import sys
import time
import traceback
import numpy as np

import simulation
from simulation import (
    EngineMode,
    EPRMode,
    ThermoSweepMode,
    CondensedMatterMode,
    run_ela_simulation
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run 32k ELA Engine v6.6.2 Production Benchmark Suite"
    )
    parser.add_argument(
        "--all", action="store_true", help="Run full benchmark suite for all Papers (I-V)"
    )
    parser.add_argument(
        "--paper", type=int, nargs="+", choices=[1, 2, 3, 4, 5],
        help="Select specific Paper(s) to execute (1, 2, 3, 4, or 5)"
    )
    parser.add_argument(
        "--grid_dim", type=int, default=64,
        help="Grid dimension for diamond torus (default: 64 -> 32,768 nodes)"
    )
    parser.add_argument(
        "--seed", type=int, default=104729,
        help="Production PRNG seed (default: 104729)"
    )
    parser.add_argument(
        "--sweeps_p123", type=int, default=50000,
        help="Monte Carlo sweeps for Papers 1, 2, and 3 (default: 50,000)"
    )
    parser.add_argument(
        "--out_dir", type=str, default="./results_v662_32k",
        help="Destination directory for output NPZ archives"
    )
    parser.add_argument(
        "--run_id_prefix", type=str, default="PROD_V662_32K",
        help="Prefix string for run identifiers"
    )
    parser.add_argument(
        "--p4_mode", type=str, default="all",
        choices=["all", "quench", "sweep", "fss"],
        help="Sub-protocol selection for Paper IV (default: all)"
    )
    parser.add_argument(
        "--p5_mode", type=str, default="all",
        choices=["all", "hydrostatic", "carbon", "h2o", "saturation", "superionic"],
        help="Sub-protocol selection for Paper V (default: all)"
    )
    return parser.parse_args()


def extract_npz_metrics(npz_path):
    """Safely extracts key physical metrics from the exported NPZ archive."""
    if not (isinstance(npz_path, str) and os.path.exists(npz_path)):
        return "NPZ saved"
    try:
        with np.load(npz_path) as data:
            metrics = []
            if "ds_final" in data:
                metrics.append(f"ds={float(data['ds_final']):.4f}")
            if "topological_charge_Q" in data:
                metrics.append(f"Q={float(data['topological_charge_Q']):.4f}")
            if "strand_q_charge" in data:
                metrics.append(f"q_strand={float(data['strand_q_charge']):.4f}")
            if "total_protected_swaps" in data:
                metrics.append(f"shielded={int(data['total_protected_swaps']):,}")
            if "specific_heat_Cv" in data:
                metrics.append(f"Cv={float(data['specific_heat_Cv']):.2f}")
            return " | ".join(metrics) if metrics else "Done"
    except Exception:
        return "Archive generated"


# ------------------------------------------------------------------------------
# BENCHMARK RUNNERS FOR PAPERS I–V
# ------------------------------------------------------------------------------

def execute_paper_1(args):
    """Paper I: Spatial Vacuum Rigidity, Metric Continuity, and 3D Continuum Limit."""
    run_id = f"{args.run_id_prefix}_P1_VACUUM_SEED_{args.seed}"
    print(f"\n{'='*80}\n[PAPER I] EXECUTING VACUUM RIGIDITY BENCHMARK (32K NODES)\n{'='*80}")
    t0 = time.time()
    npz_file = run_ela_simulation(
        mode=EngineMode.PAPER1_VACUUM,
        grid_dim=args.grid_dim,
        num_sweeps=args.sweeps_p123,
        run_id=run_id,
        out_dir=args.out_dir,
        seed=args.seed,
        save_npz=True
    )
    elapsed = time.time() - t0
    print(f"[PAPER I COMPLETE] Elapsed: {elapsed:.2f}s | {extract_npz_metrics(npz_file)}")
    return elapsed


def execute_paper_2(args):
    """Paper II: Gauge Soliton Confinement, Sleeve Protection, and Helicity Invariance."""
    run_id = f"{args.run_id_prefix}_P2_SOLITON_Q1_SEED_{args.seed}"
    print(f"\n{'='*80}\n[PAPER II] EXECUTING GAUGE SOLITON BENCHMARK (32K NODES)\n{'='*80}")
    t0 = time.time()
    npz_file = run_ela_simulation(
        mode=EngineMode.PAPER2_GAUGE_SOLITON,
        grid_dim=args.grid_dim,
        num_sweeps=args.sweeps_p123,
        inject_soliton_flag=True,
        q_charge_val=1,
        run_id=run_id,
        out_dir=args.out_dir,
        seed=args.seed,
        save_npz=True
    )
    elapsed = time.time() - t0
    print(f"[PAPER II COMPLETE] Elapsed: {elapsed:.2f}s | {extract_npz_metrics(npz_file)}")
    return elapsed


def execute_paper_3(args):
    """Paper III: Untensing Cosmology, LQC Bounce, and Dark Energy Equation of State."""
    run_id = f"{args.run_id_prefix}_P3_COSMOLOGY_SEED_{args.seed}"
    print(f"\n{'='*80}\n[PAPER III] EXECUTING COSMOLOGICAL BOUNCE BENCHMARK (32K NODES)\n{'='*80}")
    t0 = time.time()
    npz_file = run_ela_simulation(
        mode=EngineMode.PAPER3_COSMOLOGY,
        epr_mode=EPRMode.DYNAMIC,
        grid_dim=args.grid_dim,
        num_sweeps=args.sweeps_p123,
        run_id=run_id,
        out_dir=args.out_dir,
        seed=args.seed,
        save_npz=True
    )
    elapsed = time.time() - t0
    print(f"[PAPER III COMPLETE] Elapsed: {elapsed:.2f}s | {extract_npz_metrics(npz_file)}")
    return elapsed


def execute_paper_4(args):
    """Paper IV: Substrate Thermodynamics, Viscoelastic Quench, and Geometrogenesis."""
    print(f"\n{'='*80}\n[PAPER IV] EXECUTING SUBSTRATE THERMODYNAMICS SUITE (32K NODES)\n{'='*80}")
    t0 = time.time()

    # 1. Viscoelastic Quench Kinetics
    if args.p4_mode in ("all", "quench"):
        print("\n--- Sub-protocol: Viscoelastic Quench Kinetics ---")
        run_id_quench = f"{args.run_id_prefix}_P4_QUENCH_SEED_{args.seed}"
        run_ela_simulation(
            mode=EngineMode.PAPER4_THERMODYNAMICS,
            thermo_mode=ThermoSweepMode.QUENCH_KINETICS,
            grid_dim=args.grid_dim,
            num_sweeps=10000,
            run_id=run_id_quench,
            out_dir=args.out_dir,
            seed=args.seed,
            save_npz=True,
            enable_compliant_move3=True,
            compliance_alpha=0.15,
            cutoff_prefactor=3.85
        )

    # 2. Thermodynamic Beta Sweep (Annealing: [0.50 -> 2.80])
    if args.p4_mode in ("all", "sweep"):
        print("\n--- Sub-protocol: Thermodynamic Beta Sweep (Annealing: [0.50 -> 2.80]) ---")
        run_id_sweep = f"{args.run_id_prefix}_P4_SWEEP_SEED_{args.seed}"
        run_ela_simulation(
            mode=EngineMode.PAPER4_THERMODYNAMICS,
            thermo_mode=ThermoSweepMode.BETA_SWEEP,
            grid_dim=args.grid_dim,
            beta_start=0.50,
            beta_end=2.80,
            beta_steps=25,
            num_sweeps=10000,
            run_id=run_id_sweep,
            out_dir=args.out_dir,
            seed=args.seed,
            save_npz=True,
            enable_compliant_move3=True,
            compliance_alpha=0.15,
            cutoff_prefactor=3.85
        )

    # 3. Finite-Size Scaling (FSS Multi-Volume Hierarchy)
    if args.p4_mode in ("all", "fss"):
        print("\n--- Sub-protocol: Finite-Size Scaling (FSS Hierarchy) ---")
        run_id_fss = f"{args.run_id_prefix}_P4_FSS_SEED_{args.seed}"
        run_ela_simulation(
            mode=EngineMode.PAPER4_THERMODYNAMICS,
            thermo_mode=ThermoSweepMode.FSS_ANALYSIS,
            fss_dims=[8, 16, 32, 64],
            run_id=run_id_fss,
            out_dir=args.out_dir,
            seed=args.seed,
            save_npz=True,
            enable_compliant_move3=True,
            compliance_alpha=0.15,
            cutoff_prefactor=3.85
        )

    elapsed = time.time() - t0
    print(f"[PAPER IV COMPLETE] Elapsed: {elapsed:.2f}s")
    return elapsed


def execute_paper_5(args):
    """Paper V: Relational Condensed Matter, Capacity Saturation, and Extreme EoS."""
    print(f"\n{'='*80}\n[PAPER V] EXECUTING CONDENSED MATTER & EXTREME EOS SUITE (32K NODES)\n{'='*80}")
    t0 = time.time()

    # 1. Hydrostatic Compression (10 -> 1000 GPa)
    if args.p5_mode in ("all", "hydrostatic"):
        print("\n--- Sub-protocol: Hydrostatic Compression (10 -> 1000 GPa) ---")
        run_id_hydro = f"{args.run_id_prefix}_P5_HYDROSTATIC_SEED_{args.seed}"
        run_ela_simulation(
            mode=EngineMode.PAPER5_CONDENSED_MATTER,
            condensed_mode=CondensedMatterMode.HYDROSTATIC_COMPRESSION,
            grid_dim=args.grid_dim,
            pressure_start=10.0,
            pressure_end=1000.0,
            pressure_steps=20,
            run_id=run_id_hydro,
            out_dir=args.out_dir,
            seed=args.seed,
            save_npz=True
        )

    # 2. Diamond Rain Carbon Relaxation (100 GPa)
    if args.p5_mode in ("all", "carbon"):
        print("\n--- Sub-protocol: Diamond Rain Carbon (100 GPa) ---")
        run_id_carbon = f"{args.run_id_prefix}_P5_CARBON_SEED_{args.seed}"
        run_ela_simulation(
            mode=EngineMode.PAPER5_CONDENSED_MATTER,
            condensed_mode=CondensedMatterMode.DIAMOND_RAIN_CARBON,
            grid_dim=args.grid_dim,
            pressure_val=100.0,
            num_sweeps=10000,
            run_id=run_id_carbon,
            out_dir=args.out_dir,
            seed=args.seed,
            save_npz=True
        )

    # 3. High-Pressure H2O Phase Diagram (300 -> 5000 K)
    if args.p5_mode in ("all", "h2o"):
        print("\n--- Sub-protocol: H2O Superionic Phase Diagram ---")
        run_id_h2o = f"{args.run_id_prefix}_P5_H2O_SEED_{args.seed}"
        run_ela_simulation(
            mode=EngineMode.PAPER5_CONDENSED_MATTER,
            condensed_mode=CondensedMatterMode.PHASE_DIAGRAM_H2O,
            grid_dim=args.grid_dim,
            temp_start=300.0,
            temp_end=5000.0,
            temp_steps=20,
            pressure_val=100.0,
            run_id=run_id_h2o,
            out_dir=args.out_dir,
            seed=args.seed,
            save_npz=True
        )

    # 4. Asymptotic Capacity Saturation
    if args.p5_mode in ("all", "saturation"):
        print("\n--- Sub-protocol: Capacity Saturation EoS ---")
        run_id_sat = f"{args.run_id_prefix}_P5_SATURATION_SEED_{args.seed}"
        run_ela_simulation(
            mode=EngineMode.PAPER5_CONDENSED_MATTER,
            condensed_mode=CondensedMatterMode.CAPACITY_SATURATION,
            grid_dim=args.grid_dim,
            run_id=run_id_sat,
            out_dir=args.out_dir,
            seed=args.seed,
            save_npz=True
        )

    # 5. Superionic Proton Knot Diffusion Onset (2500 K, 100 GPa)
    if args.p5_mode in ("all", "superionic"):
        print("\n--- Sub-protocol: Superionic Diffusion Onset (2500 K, 100 GPa) ---")
        run_id_super = f"{args.run_id_prefix}_P5_SUPERIONIC_SEED_{args.seed}"
        run_ela_simulation(
            mode=EngineMode.PAPER5_CONDENSED_MATTER,
            condensed_mode=CondensedMatterMode.SUPERIONIC_ONSET,
            grid_dim=args.grid_dim,
            temp_val=2500.0,
            pressure_val=100.0,
            num_sweeps=10000,
            run_id=run_id_super,
            out_dir=args.out_dir,
            seed=args.seed,
            save_npz=True
        )

    elapsed = time.time() - t0
    print(f"[PAPER V COMPLETE] Elapsed: {elapsed:.2f}s")
    return elapsed


# ------------------------------------------------------------------------------
# MAIN SUITE ORCHESTRATOR
# ------------------------------------------------------------------------------

def main():
    args = parse_args()

    papers_to_run = []
    if args.all:
        papers_to_run = [1, 2, 3, 4, 5]
    elif args.paper:
        papers_to_run = sorted(list(set(args.paper)))
    else:
        print("[ERROR] Please specify either --all or --paper 1 [2 3 4 5]")
        sys.exit(1)

    os.makedirs(args.out_dir, exist_ok=True)

    start_wall_time = datetime.datetime.now()
    suite_t0 = time.time()

    print(f"\n{'#'*80}")
    print("       EMERGENT LATTICE ARCHITECTURE (ELA) v6.6.2 PRODUCTION RUNNER")
    print(f"{'#'*80}")
    print(f" Start Time       : {start_wall_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f" Target Papers    : {papers_to_run}")
    print(f" Grid Dimension   : {args.grid_dim} (N = 32,768 nodes)")
    print(f" Global Seed      : {args.seed}")
    print(f" Output Directory : {os.path.abspath(args.out_dir)}")
    print(f"{'#'*80}\n")

    execution_log = {}

    runner_dispatch = {
        1: ("Paper I (Vacuum Rigidity)", execute_paper_1),
        2: ("Paper II (Gauge Soliton)", execute_paper_2),
        3: ("Paper III (Cosmology & LQC)", execute_paper_3),
        4: ("Paper IV (Substrate Thermo)", execute_paper_4),
        5: ("Paper V (Condensed Matter)", execute_paper_5),
    }

    for paper_num in papers_to_run:
        label, func = runner_dispatch[paper_num]
        print(f"\n>>> Starting {label} at {datetime.datetime.now().strftime('%H:%M:%S')}...")
        try:
            runtime = func(args)
            execution_log[label] = {"status": "SUCCESS", "runtime": runtime}
        except Exception as e:
            print(f"\n[CRITICAL FAILURE] Execution failed for {label}: {e}")
            traceback.print_exc()
            execution_log[label] = {"status": f"FAILED ({str(e)})", "runtime": 0.0}

    total_suite_elapsed = time.time() - suite_t0
    print(f"\n{'='*80}")
    print("                       PRODUCTION RUN EXECUTION SUMMARY")
    print(f"{'='*80}")
    print(f" Total Elapsed Time: {datetime.timedelta(seconds=int(total_suite_elapsed))}")
    print(f"{'-'*80}")
    print(f"{'Benchmark Target':<35} | {'Status':<15} | {'Runtime (s)':<12}")
    print(f"{'-'*80}")
    for label, info in execution_log.items():
        print(f"{label:<35} | {info['status']:<15} | {info['runtime']:>10.2f}s")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()