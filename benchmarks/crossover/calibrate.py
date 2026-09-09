import sys
import subprocess
import time
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]

def run_backend(flow_file, backend):
    cmd = [
        sys.executable, "-m", "flow.run", str(flow_file),
        f"--backend={backend}", "--json"
    ]
    env = dict(import_os=True)
    import os
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "src") + os.pathsep + env.get("PYTHONPATH", "")
    
    t0 = time.monotonic()
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    t_total = time.monotonic() - t0
    
    if result.returncode != 0:
        return float('inf')
        
    try:
        data = json.loads(result.stdout)
        # return the total time measured by flow.run to be precise, or just the outer subprocess time.
        # Outer subprocess time includes python startup, so let's use the inner timing which is what we care about for the compiler.
        return data["timing"]["total_s"]
    except:
        return t_total

def main():
    corpus = list(Path(__file__).parent.glob("*.flow"))
    corpus.sort()
    
    print(f"{'Program':<30} | {'C Time (s)':<12} | {'MLIR Time (s)':<15} | {'Winner'}")
    print("-" * 75)
    
    for f in corpus:
        c_time = run_backend(f, "c")
        mlir_time = run_backend(f, "mlir")
        
        winner = "C" if c_time < mlir_time else "MLIR"
        if c_time == float('inf'): c_time_str = "Error"
        else: c_time_str = f"{c_time:.4f}"
        
        if mlir_time == float('inf'): mlir_time_str = "Error"
        else: mlir_time_str = f"{mlir_time:.4f}"
        
        print(f"{f.name:<30} | {c_time_str:<12} | {mlir_time_str:<15} | {winner}")

if __name__ == "__main__":
    main()
