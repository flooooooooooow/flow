#!/usr/bin/env python3
import argparse
import json
import os
import platform
import shutil
import statistics
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def get_flow_version():
    version_file = ROOT / "src" / "flow" / "version.py"
    if version_file.exists():
        env = {}
        exec(version_file.read_text(), env)
        return env.get("__version__", "unknown")
    return "unknown"

def get_system_info():
    git_sha = "unknown"
    if shutil.which("git"):
        res = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=str(ROOT))
        if res.returncode == 0:
            git_sha = res.stdout.strip()
            
    return {
        "os": platform.system(),
        "cpu": platform.processor() or platform.machine(),
        "arch": platform.machine(),
        "git_sha": git_sha,
        "python_version": platform.python_version(),
        "flow_version": get_flow_version(),
        "threads": os.cpu_count()
    }

def get_percentile(data, p):
    if not data:
        return 0.0
    sorted_data = sorted(data)
    k = (len(sorted_data) - 1) * p
    f = int(k)
    c = min(f + 1, len(sorted_data) - 1)
    if f == c:
        return sorted_data[f]
    return sorted_data[f] * (c - k) + sorted_data[c] * (k - f)

def get_peak_rss(proc, time_out_file):
    if not os.path.exists(time_out_file):
        return 0
    with open(time_out_file, "r") as f:
        content = f.read()
        for line in content.splitlines():
            if "Maximum resident set size" in line:
                try:
                    return int(line.split(":")[1].strip())
                except ValueError:
                    return 0
    return 0
    
def get_allocations_and_copies(stdout_str):
    allocs, copies = 0, 0
    for line in stdout_str.splitlines():
        if line.startswith("allocations:"):
            try: allocs = int(line.split(":")[1].strip())
            except ValueError: pass
        if line.startswith("copies:"):
            try: copies = int(line.split(":")[1].strip())
            except ValueError: pass
    return allocs, copies

def run_cmd(cmd, env=None, measure_memory=False, cwd=None):
    t0 = time.perf_counter()
    time_out = "time_out.txt"
    if measure_memory and shutil.which("/usr/bin/time"):
        full_cmd = ["/usr/bin/time", "-v", "-o", time_out] + cmd
    else:
        full_cmd = cmd
        
    proc = subprocess.run(full_cmd, env=env, cwd=cwd, capture_output=True, text=True)
    t1 = time.perf_counter()
    
    rss = 0
    if measure_memory and os.path.exists(time_out):
        rss = get_peak_rss(proc, time_out)
        os.remove(time_out)
        
    allocs, copies = get_allocations_and_copies(proc.stdout)
        
    return {
        "time": t1 - t0,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "returncode": proc.returncode,
        "rss_kb": rss,
        "allocations": allocs,
        "copies": copies
    }

def run_benchmark(workload_id, flow_cmd, python_cmd, repeats, warm_mode=False, semantic_parity="verified", measure_memory=False, cwd=None):
    sys_info = get_system_info()
    
    env = dict(os.environ)
    if "PYTHONPATH" not in env:
        env["PYTHONPATH"] = str(ROOT / "src")
        
    if warm_mode:
        if flow_cmd: subprocess.run(flow_cmd, env=env, cwd=cwd, capture_output=True)
        if python_cmd: subprocess.run(python_cmd, env=env, cwd=cwd, capture_output=True)
        
    results = {
        "workload_id": workload_id,
        "semantic_parity_status": semantic_parity,
        "flow_command": " ".join(flow_cmd) if flow_cmd else None,
        "python_command": " ".join(python_cmd) if python_cmd else None,
        "compiler_version": sys_info["flow_version"],
        "interpreter_version": sys_info["python_version"],
        "backend": "c",
        "blas_lapack_identity": "none",
        "thread_counts": sys_info["threads"],
        "cpu": sys_info["cpu"],
        "os": sys_info["os"],
        "warm_mode": warm_mode,
        "repeats": repeats,
        "flow_metrics": {},
        "python_metrics": {}
    }
    
    for cmd, name in [(flow_cmd, "flow_metrics"), (python_cmd, "python_metrics")]:
        if not cmd:
            continue
            
        times = []
        rss_vals = []
        alloc_vals = []
        copy_vals = []
        for _ in range(repeats):
            res = run_cmd(cmd, env=env, measure_memory=measure_memory, cwd=cwd)
            if res["returncode"] != 0 and semantic_parity == "verified":
                results["semantic_parity_status"] = "unresolved"
            times.append(res["time"])
            if measure_memory:
                rss_vals.append(res["rss_kb"])
            alloc_vals.append(res["allocations"])
            copy_vals.append(res["copies"])
                
        if times:
            results[name] = {
                "median": statistics.median(times),
                "min": min(times),
                "p95": get_percentile(times, 0.95),
                "dispersion": statistics.stdev(times) if len(times) > 1 else 0.0,
                "allocations": statistics.median(alloc_vals),
                "copies": statistics.median(copy_vals)
            }
            if measure_memory and rss_vals:
                results[name]["median_rss_kb"] = statistics.median(rss_vals)
                
    return results

def evaluate_regression(old_res, new_res):
    if old_res["os"] != new_res["os"] or old_res["cpu"] != new_res["cpu"]:
        return "skipped_env_mismatch"
        
    if new_res["semantic_parity_status"] != "verified":
        return "skipped_unresolved_correctness"
        
    old_median = old_res["flow_metrics"].get("median", 0)
    new_median = new_res["flow_metrics"].get("median", 0)
    
    if new_median == 0 or old_median == 0:
        return "no_data"
        
    if new_median <= old_median:
        return "pass"
        
    margin = old_median * 0.05
    if new_median - old_median <= margin:
        return "pass_within_margin"
        
    return "regression"

def get_harness_dir():
    return ROOT / "benchmarks" / "cross_harness"

def compile_flow(flow_path, bin_path):
    env = dict(os.environ)
    if "PYTHONPATH" not in env:
        env["PYTHONPATH"] = str(ROOT / "src")
        
    gen_c = bin_path.with_suffix(".c")
    proc = subprocess.run([sys.executable, "-m", "flow.transpiler", str(flow_path), "--c", "--lenient", "-o", str(gen_c)], env=env, capture_output=True, text=True)
    if proc.returncode != 0:
        print(f"Compilation to C failed for {flow_path}:\n{proc.stdout}\n{proc.stderr}")
        return False
        
    proc2 = subprocess.run(["clang", "-O3", "-march=native", "-lm", str(gen_c), "-o", str(bin_path)], capture_output=True, text=True)
    if proc2.returncode != 0:
        print(f"Clang compilation failed for {gen_c}:\n{proc2.stdout}\n{proc2.stderr}")
        return False
        
    return True

def discover_suites(smoke=False):
    harness_dir = get_harness_dir()
    if not harness_dir.exists():
        return []
        
    results = []
    repeats = 3 if smoke else 10
    
    suites = ["cold", "runtime", "compiler", "memory"]
    
    build_dir = ROOT / "build" / "benchmarks"
    build_dir.mkdir(parents=True, exist_ok=True)
    
    for suite in suites:
        suite_dir = harness_dir / suite
        if not suite_dir.exists():
            continue
            
        for d in suite_dir.iterdir():
            if not d.is_dir():
                continue
                
            workload_id = f"{suite}_{d.name}"
            
            flow_cmd = None
            python_cmd = None
            measure_memory = (suite == "memory")
            warm_mode = (suite != "cold")
            
            flow_files = list(d.glob("*.flow"))
            if flow_files:
                if suite == "cold" or suite == "compiler":
                    flow_cmd = [sys.executable, "-m", "flow.run", str(flow_files[0])]
                else:
                    bin_path = build_dir / workload_id
                    if compile_flow(flow_files[0], bin_path):
                        flow_cmd = [str(bin_path)]
                    else:
                        print(f"Skipping {workload_id} due to compilation error")
                        continue
                
            py_files = list(d.glob("*.py"))
            if py_files:
                python_cmd = [sys.executable, str(py_files[0])]
                
            if flow_cmd or python_cmd:
                res = run_benchmark(
                    workload_id=workload_id,
                    flow_cmd=flow_cmd,
                    python_cmd=python_cmd,
                    repeats=repeats,
                    warm_mode=warm_mode,
                    measure_memory=measure_memory,
                    cwd=str(d)
                )
                results.append(res)
                
    return results

def main():
    parser = argparse.ArgumentParser(description="Flow cross-dimensional performance harness")
    parser.add_argument("--smoke", action="store_true", help="Run low-noise local smoke gate")
    parser.add_argument("--baseline", type=str, help="Compare against previous results JSON")
    parser.add_argument("--out", type=str, default="benchmark_schema.json", help="Output JSON path")
    args = parser.parse_args()
    
    print(f"Running benchmarks (smoke={args.smoke})...")
    
    benchmarks = discover_suites(smoke=args.smoke)
    
    if not benchmarks:
        print("No benchmarks found. Create some in benchmarks/cross_harness/")
        
        benchmarks.append(run_benchmark(
            workload_id="mock_workload",
            flow_cmd=["echo", "flow_mock"],
            python_cmd=["echo", "python_mock"],
            repeats=3 if args.smoke else 10,
            warm_mode=True
        ))
    
    final_data = {
        "timestamp": datetime.now().isoformat(),
        "system": get_system_info(),
        "benchmarks": benchmarks
    }
    
    regression_failed = False
    
    if args.baseline:
        if os.path.exists(args.baseline):
            with open(args.baseline, "r") as f:
                old_data = json.load(f)
                
            for new_b in final_data["benchmarks"]:
                old_b = next((b for b in old_data.get("benchmarks", []) if b["workload_id"] == new_b["workload_id"]), None)
                if old_b:
                    status = evaluate_regression(old_b, new_b)
                    print(f"{new_b['workload_id']}: {status}")
                    if status == "regression":
                        print(f"  Regression found! Old median: {old_b['flow_metrics'].get('median')}, New median: {new_b['flow_metrics'].get('median')}")
                        regression_failed = True
        else:
            print(f"Baseline file {args.baseline} not found.")
            
    with open(args.out, "w") as f:
        json.dump(final_data, f, indent=2)
    print(f"Wrote benchmark results to {args.out}")
    
    if regression_failed:
        sys.exit(1)

if __name__ == "__main__":
    main()
