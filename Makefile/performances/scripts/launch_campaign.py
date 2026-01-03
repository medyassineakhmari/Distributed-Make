#!/usr/bin/env python3
import subprocess
import os
import sys
from datetime import datetime

# === CONFIGURATION ===
# Cluster target (nova, dahu, etc.)
TARGET_CLUSTER = "nova"
# Node configurations to test
NODE_COUNTS = [2, 3, 4, 6, 8, 10, 12, 15, 18]
# Max duration per job
WALLTIME = "01:00:00"
# Repetitions per config
ITERATIONS = 3

# Paths
PROJECT_DIR = os.path.expanduser("~/Distributed-Make/Makefile")
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BENCHMARK_SCRIPT = os.path.join(SCRIPT_DIR, "benchmark_model.sh")
DATA_DIR = os.path.join(PROJECT_DIR, "performances", "data")

def check_prerequisites():
    """Verifies environment consistency."""
    errors = []

    # Check benchmark script existence
    if not os.path.exists(BENCHMARK_SCRIPT):
        errors.append(f"Script not found: {BENCHMARK_SCRIPT}")

    # Check Grid5000 environment
    try:
        hostname = subprocess.getoutput("hostname")
        if "grid5000" not in hostname and "g5k" not in hostname:
            print(f"[WARN] Hostname '{hostname}' does not look like Grid5000.")
    except Exception:
        pass

    # Check oarsub availability
    try:
        subprocess.run(["which", "oarsub"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        errors.append("Command 'oarsub' not found. Are you on a frontend?")

    return errors

def submit_job(node_count):
    """Submits an OAR job for a specific node count."""
    job_name = f"bench_{node_count}nodes"
    
    # OAR Command construction
    cmd = [
        "oarsub",
        "-l", f"nodes={node_count},walltime={WALLTIME}",
        "-p", f"cluster='{TARGET_CLUSTER}'",
        "-n", job_name,
        f"bash {BENCHMARK_SCRIPT} {ITERATIONS}"
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            # Parse Job ID
            for line in result.stdout.split('\n'):
                if "OAR_JOB_ID" in line:
                    return line.split('=')[1].strip()
            return "submitted (ID unknown)"
        else:
            return f"ERROR: {result.stderr.strip()}"
            
    except subprocess.TimeoutExpired:
        return "TIMEOUT"
    except Exception as e:
        return f"EXCEPTION: {str(e)}"

def main():
    print("==================================================")
    print("   PERFORMANCE MODEL VALIDATION CAMPAIGN")
    print("==================================================")
    print(f"Cluster      : {TARGET_CLUSTER}")
    print(f"Configs      : {NODE_COUNTS}")
    print(f"Iterations   : {ITERATIONS}")
    print(f"Script       : {BENCHMARK_SCRIPT}")
    print("--------------------------------------------------")

    # 1. Check prerequisites
    errors = check_prerequisites()
    if errors:
        for err in errors:
            print(f"[ERROR] {err}")
        sys.exit(1)

    # 2. Prepare environment
    if os.path.exists(BENCHMARK_SCRIPT):
        os.chmod(BENCHMARK_SCRIPT, 0o755)
    
    os.makedirs(DATA_DIR, exist_ok=True)

    # 3. Submit jobs
    print("\n[INFO] Submitting jobs...")
    submitted_jobs = []

    for n in NODE_COUNTS:
        print(f"Nodes: {n:2d} ... ", end="", flush=True)
        result = submit_job(n)

        if "ERROR" in result or "EXCEPTION" in result or "TIMEOUT" in result:
            print(f"[FAIL] {result}")
        else:
            print(f"[OK] Job ID {result}")
            submitted_jobs.append((n, result))

    # 4. Summary
    print("--------------------------------------------------")
    print(f"Total submitted : {len(submitted_jobs)}/{len(NODE_COUNTS)}")
    print(f"Est. Duration   : ~{len(NODE_COUNTS) * 30} minutes")
    print("\n[INFO] To monitor jobs:")
    print("       oarstat -u $USER")
    print("\n[INFO] Results will be in:")
    print(f"       {DATA_DIR}/raw_measurements.csv")

    # 5. Log campaign
    log_file = os.path.join(DATA_DIR, f"campaign_{datetime.now():%Y%m%d_%H%M%S}.log")
    with open(log_file, 'w') as f:
        f.write(f"Date: {datetime.now()}\n")
        f.write(f"Cluster: {TARGET_CLUSTER}\n")
        f.write("Jobs:\n")
        for n, jid in submitted_jobs:
            f.write(f"{n} nodes: {jid}\n")

    print(f"\n[INFO] Campaign log saved to: {log_file}")

if __name__ == "__main__":
    main()
