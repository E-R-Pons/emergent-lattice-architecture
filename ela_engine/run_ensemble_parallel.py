#!/usr/bin/env python3
"""
================================================================================
ELA PARALLEL MULTI-SEED PRODUCTION ORCHESTRATOR
================================================================================
Executes multi-seed production ensembles across Paper 1, Paper 2, and Paper 3
concurrently using a worker pool. Logs each run independently to prevent terminal interleaving.
================================================================================
"""

import os
import sys
import subprocess
import multiprocessing
import time
from pathlib import Path

ENGINE_SCRIPT = "./ela_engine_v442.py"
LOG_DIR = Path("logs_production")
LOG_DIR.mkdir(exist_ok=True)

# Set based on available system CPU cores & RAM
MAX_PARALLEL_WORKERS = min(6, os.cpu_count() or 1)

SEEDS = [104729, 224737, 349781, 499796, 629143, 748921, 869102, 991207]

PRODUCTION_RUNS = [
    {
        "paper": "Paper 1",
        "prefix": "PROD_P1_VACUUM",
        "extra": ["--mode", "1", "--dim", "64", "--steps", "50000"]
    },
    {
        "paper": "Paper 2",
        "prefix": "PROD_P2_SOLITON_Q1",
        "extra": ["--mode", "2", "--dim", "64", "--steps", "50000", "--soliton", "--q-charge", "1"]
    },
    {
        "paper": "Paper 3",
        "prefix": "PROD_P3_COSMOLOGY",
        "extra": ["--mode", "3", "--dim", "64", "--steps", "50000", "--epr-mode", "dynamic"]
    }
]


def execute_seed_task(task):
    paper = task["paper"]
    prefix = task["prefix"]
    seed = task["seed"]
    extra_args = task["extra"]

    run_id = f"{prefix}_SEED_{seed}"
    log_file = LOG_DIR / f"{run_id}.log"

    cmd = [
        sys.executable, ENGINE_SCRIPT,
        "--run_id", run_id,
        "--seed", str(seed),
        "--plot"
    ] + extra_args

    t0 = time.time()
    with open(log_file, "w", buffering=1) as f_log:
        process = subprocess.Popen(
            cmd,
            stdout=f_log,
            stderr=subprocess.STDOUT,
            text=True
        )
        process.wait()

    elapsed = time.time() - t0
    success = (process.returncode == 0)
    
    return run_id, paper, seed, success, elapsed


def main():
    if not os.path.exists(ENGINE_SCRIPT):
        print(f"[ERROR] Engine script '{ENGINE_SCRIPT}' not found.")
        sys.exit(1)

    # Build flat task queue (3 papers x 5 seeds = 15 parallel tasks)
    tasks = []
    for run in PRODUCTION_RUNS:
        for seed in SEEDS:
            tasks.append({
                "paper": run["paper"],
                "prefix": run["prefix"],
                "seed": seed,
                "extra": run["extra"]
            })

    total_tasks = len(tasks)
    print("================================================================================")
    print("      ELA v4.4.2 PARALLEL PRODUCTION ENSEMBLE ORCHESTRATOR")
    print("================================================================================")
    print(f" Engine Script      : {ENGINE_SCRIPT}")
    print(f" Total Queue Tasks  : {total_tasks} (3 Papers x {len(SEEDS)} Seeds)")
    print(f" Parallel Workers   : {MAX_PARALLEL_WORKERS} Processes")
    print(f" Logs Directory     : {LOG_DIR.resolve()}")
    print("================================================================================")

    completed = 0
    failed = 0

    with multiprocessing.Pool(processes=MAX_PARALLEL_WORKERS) as pool:
        for run_id, paper, seed, success, elapsed in pool.imap_unordered(execute_seed_task, tasks):
            completed += 1
            status = "[PASSED]" if success else "[FAILED]"
            if not success:
                failed += 1
            
            print(f" [{completed:02d}/{total_tasks:02d}] {status} {paper:<8} | Seed {seed} | RunID: {run_id:<30} ({elapsed:.1f}s)")

    print("\n================================================================================")
    if failed == 0:
        print("      ALL MULTI-SEED PRODUCTION RUNS COMPLETED SUCCESSFULLY [ALL PASSED]")
    else:
        print(f"      PRODUCTION FINISHED WITH {failed} FAILURE(S) — Check logs in {LOG_DIR}")
    print("================================================================================")


if __name__ == "__main__":
    main()
