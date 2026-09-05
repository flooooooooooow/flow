#!/usr/bin/env python3
import os
import sys
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
        sh(["clang", "-O3", "-march=native", "-lm", str(gen_c), "-o", str(exe)], cwd=str(ROOT))

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
    
    print(f"Arch: {arch}, OS: {system}, Cores: {cores}")
    
    lines = []
    lines.append(f"# Flow Performance Baselines")
    lines.append(f"")
    lines.append(f"Date: {date.today().isoformat()}")
    lines.append(f"OS: {system}")
    lines.append(f"Arch: {arch}")
    lines.append(f"Cores: {cores}")
    lines.append(f"")
    lines.append(f"| Benchmark | Median (s) | Min (s) | Max (s) | Result |")
    lines.append(f"|---|---|---|---|---|")
    
    for b in BENCHES:
        secs = data[b]["seconds"]
        med = statistics.median(secs)
        min_s = min(secs)
        max_s = max(secs)
        res = data[b]["result"]
        lines.append(f"| {b} | {med:.6f} | {min_s:.6f} | {max_s:.6f} | {res} |")
        
    OUT_MD.write_text("\n".join(lines) + "\n")
    print(f"Wrote {OUT_MD}")

if __name__ == "__main__":
    main()
