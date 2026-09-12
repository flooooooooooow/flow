#!/usr/bin/env python3
import os
import sys
import json
import subprocess
import time
import shutil
import platform
import statistics
from pathlib import Path
from datetime import date

ROOT = Path(__file__).resolve().parent.parent.parent
BASELINES = ROOT / "benchmarks" / "baselines"
BUILD = BASELINES / "build"
OUT_MD = BASELINES / "baseline_results.md"

BENCHES = ["numeric", "string_io", "startup"]
CLANG_FLAGS = ["-O3", "-march=native", "-lm"]



def get_git_sha():
    try:
        proc = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True)
        return proc.stdout.strip()
    except subprocess.CalledProcessError:
        return "unknown"

def get_compiler_version():
    try:
        sys.path.insert(0, str(ROOT / "src"))
        import flow.version
        return flow.version.__version__
    except ImportError:
        return "unknown"

def sh(cmd, cwd=None, env=None):
    proc = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True)
    if proc.returncode != 0:
        print(f"Command failed: {' '.join(cmd)}")
        print(proc.stdout)
        print(proc.stderr)
        proc.check_returncode()
    return proc

def compile_all():
    BUILD.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    if "PYTHONPATH" not in env:
        env["PYTHONPATH"] = str(ROOT / "src")
    
    for b in BENCHES:
        flow_src = BASELINES / f"{b}.flow"
        gen_c = BUILD / f"{b}.c"
        exe = BUILD / b
        
        sh([sys.executable, "-m", "flow.transpiler", str(flow_src), "--c", "--lenient", "-o", str(gen_c)], cwd=str(ROOT), env=env)
        sh(["clang"] + CLANG_FLAGS + [str(gen_c), "-o", str(exe)], cwd=str(ROOT))

def run_once(cmd):
    t0 = time.perf_counter()
    proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
    t1 = time.perf_counter()
    
    result = None
    seconds = t1 - t0
    
    for line in proc.stdout.splitlines():
        if line.startswith("result "):
            result = line.split(None, 1)[1].strip()
            
    if result is None:
        raise RuntimeError(f"bad output from {cmd}: {proc.stdout!r}")
    return result, seconds

def measure():
    data = {}
    for b in BENCHES:
        cmd = [str(BUILD / b)]
        print(f"Running {b}...", flush=True)
        
        run_once(cmd) # warmup
        reps = 5
        if b == "startup":
            reps = 20
            
        secs = []
        result = None
        for _ in range(reps):
            r, s = run_once(cmd)
            secs.append(s)
            result = r
        data[b] = {"seconds": secs, "result": result}
    return data

def main():
    print("Compiling...")
    compile_all()
    
    print("Measuring...")
    data = measure()
    
    arch = platform.machine()
    system = platform.system()
    cores = os.cpu_count()
    version = get_compiler_version()
    git_sha = get_git_sha()
    host_py = f"Python {platform.python_version()}"
    flags_str = " ".join(["clang"] + CLANG_FLAGS)
    
    print(f"Arch: {arch}, OS: {system}, Cores: {cores}, Flow: {version} ({git_sha})")
    
    lines = []
    lines.append(f"# Flow Performance Baselines")
    lines.append(f"")
    lines.append(f"Date: {date.today().isoformat()}")
    lines.append(f"OS: {system}")
    lines.append(f"Arch: {arch}")
    lines.append(f"Cores: {cores}")
    lines.append(f"Flow Version: {version}")
    lines.append(f"Git SHA: {git_sha}")
    lines.append(f"Host: {host_py}")
    lines.append(f"Flags: `{flags_str}`")
    lines.append(f"")
    lines.append(f"| Benchmark | Median (s) | Min (s) | Max (s) | Result |")
    lines.append(f"|---|---|---|---|---|")
    
    # Load contracts
    contracts_file = BASELINES / "contracts.json"
    contracts = {}
    if contracts_file.exists():
        with open(contracts_file, "r") as f:
            contracts = json.load(f)

    contract_failed = False
    
    # Store machine-readable results
    machine_results = {
        "metadata": {
            "date": date.today().isoformat(),
            "os": system,
            "arch": arch,
            "cores": cores,
            "flow_version": version,
            "git_sha": git_sha,
            "host": host_py,
            "flags": flags_str
        },
        "benchmarks": {}
    }
    
    for b in BENCHES:
        secs = data[b]["seconds"]
        med = statistics.median(secs)
        min_s = min(secs)
        max_s = max(secs)
        res = data[b]["result"]
        lines.append(f"| {b} | {med:.6f} | {min_s:.6f} | {max_s:.6f} | {res} |")
        
        machine_results["benchmarks"][b] = {
            "median_s": med,
            "min_s": min_s,
            "max_s": max_s,
            "result": res
        }
        
        if b in contracts and "max_median_s" in contracts[b]:
            max_med = contracts[b]["max_median_s"]
            if med > max_med:
                print(f"ERROR: {b} median {med:.6f}s exceeds contract {max_med}s")
                contract_failed = True
        
    OUT_MD.write_text("\n".join(lines) + "\n")
    print(f"Wrote {OUT_MD}")
    
    out_json = BASELINES / "baseline_results.json"
    with open(out_json, "w") as f:
        json.dump(machine_results, f, indent=2)
    print(f"Wrote {out_json}")
    
    if contract_failed:
        sys.exit(1)

if __name__ == "__main__":
    main()
