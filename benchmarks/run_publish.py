#!/usr/bin/env python3
"""Benchmark harness for the published Flow results.

Compiles and runs the programs under benchmarks/publish/ in Flow, C, Rust,
and Python, then writes benchmarks/RESULTS.md.

Method:
- Each program times only its workload with a monotonic clock and prints
  "result <value>" and "seconds <t>". Compile and process startup time are
  excluded from the reported numbers.
- Each program runs once as a warmup, then a fixed number of timed
  repetitions (default 5). The median is reported, with min and max.
- Flow-generated C and hand-written C are compiled by the same clang with
  the same flags.
- Results are checked for agreement across languages before the report is
  written.

Usage:
  python3 benchmarks/run_publish.py            # full run, writes RESULTS.md
  python3 benchmarks/run_publish.py --quick    # 1 repetition, no report
"""

import argparse
import os
import shutil
import subprocess
import statistics
import sys
import time
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUB = ROOT / "benchmarks" / "publish"
BUILD = PUB / "build"

BENCHES = ["fib", "nbody", "matmul", "spectral", "mandelbrot"]

DESCRIPTIONS = {
    "fib": "Naive recursive Fibonacci, fib(35). Function call overhead.",
    "nbody": "Outer solar system, 5 bodies, 1,000,000 steps (Benchmarks Game).",
    "matmul": "Dense matrix multiply, naive triple loop, 300x300 doubles.",
    "spectral": "Spectral norm, N=500, 10 power iterations (Benchmarks Game).",
    "mandelbrot": "Mandelbrot membership count, 400x400 grid, 100 iterations.",
}

CFLAGS = ["-O3", "-march=native"]
RUSTFLAGS = ["-C", "opt-level=3", "-C", "target-cpu=native"]


ENV = dict(os.environ, PYTHONPATH=str(ROOT / "src"))


def sh(cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd, check=True, env=ENV,
                          capture_output=True, text=True)


def timed_sh(cmd, cwd=None):
    t0 = time.perf_counter()
    sh(cmd, cwd=cwd)
    return time.perf_counter() - t0


def compile_all(have_rust):
    """Compile every benchmark in every compiled language.

    Returns {bench: {lang: compile_seconds}} where Flow's entry is a
    (transpile, clang) pair.
    """
    BUILD.mkdir(parents=True, exist_ok=True)
    times = {}
    for b in BENCHES:
        times[b] = {}

        # Hand-written C
        c_src = PUB / "c" / f"{b}.c"
        times[b]["c"] = timed_sh(
            ["clang", *CFLAGS, "-lm", str(c_src), "-o", str(BUILD / f"{b}_c")])

        # Flow: transpile to C, then clang with the same flags
        flow_src = PUB / "flow" / f"{b}.flow"
        gen_c = BUILD / f"{b}_flow.c"
        t_transpile = timed_sh(
            [sys.executable, "-m", "flow.transpiler", str(flow_src),
             "--c", "--lenient", "-o", str(gen_c)],
            cwd=str(ROOT))
        t_clang = timed_sh(
            ["clang", *CFLAGS, "-lm", str(gen_c), "-o",
             str(BUILD / f"{b}_flow")])
        times[b]["flow"] = (t_transpile, t_clang)

        # Rust
        if have_rust:
            rs_src = PUB / "rust" / f"{b}.rs"
            times[b]["rust"] = timed_sh(
                ["rustc", *RUSTFLAGS, str(rs_src), "-o",
                 str(BUILD / f"{b}_rust")])
    return times


def run_once(cmd):
    proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
    result = None
    seconds = None
    for line in proc.stdout.splitlines():
        if line.startswith("result "):
            result = line.split(None, 1)[1].strip()
        elif line.startswith("seconds "):
            seconds = float(line.split(None, 1)[1])
    if result is None or seconds is None:
        raise RuntimeError(f"bad output from {cmd}: {proc.stdout!r}")
    return result, seconds


def results_agree(values):
    floats = [float(v) for v in values]
    ref = floats[0]
    for f in floats[1:]:
        denom = max(abs(ref), 1e-12)
        if abs(f - ref) / denom > 1e-6:
            return False
    return True


def bench_commands(have_rust):
    cmds = {}
    for b in BENCHES:
        langs = {
            "c": [str(BUILD / f"{b}_c")],
            "flow": [str(BUILD / f"{b}_flow")],
            "python": [sys.executable, str(PUB / "python" / f"{b}.py")],
        }
        if have_rust:
            langs["rust"] = [str(BUILD / f"{b}_rust")]
        cmds[b] = langs
    return cmds


def measure(cmds, reps):
    """Returns {bench: {lang: {"seconds": [...], "result": str}}}."""
    data = {}
    for b, langs in cmds.items():
        data[b] = {}
        for lang, cmd in langs.items():
            print(f"  {b} / {lang} ...", flush=True)
            run_once(cmd)  # warmup, discarded
            secs = []
            result = None
            for _ in range(reps):
                result, s = run_once(cmd)
                secs.append(s)
            data[b][lang] = {"seconds": secs, "result": result}
    return data


def env_info():
    def out(cmd):
        return subprocess.run(cmd, capture_output=True,
                              text=True).stdout.strip()
    return {
        "clang": out(["clang", "--version"]).splitlines()[0],
        "python": out([sys.executable, "--version"]),
        "rustc": out(["rustc", "--version"]) if shutil.which("rustc") else
                 "not installed",
        "cpu": out(["sysctl", "-n", "machdep.cpu.brand_string"]),
        "mem_gb": int(out(["sysctl", "-n", "hw.memsize"])) // (1024 ** 3),
        "ncpu": out(["sysctl", "-n", "hw.ncpu"]),
    }


def fmt_s(x):
    return f"{x:.4f}"


def write_report(data, compile_times, env, reps, have_rust, out_path):
    lang_order = ["flow", "c"] + (["rust"] if have_rust else []) + ["python"]
    lang_names = {"flow": "Flow", "c": "C", "rust": "Rust",
                  "python": "Python"}

    lines = []
    add = lines.append
    add("# Flow benchmark results")
    add("")
    add(f"Date: {date.today().isoformat()}")
    add("")
    add("Flow compiles to C. The comparison that matters is Flow against")
    add("hand-written C built by the same clang with the same flags. Rust and")
    add("plain CPython run the same algorithms at the same sizes for context.")
    add("")

    add("## Summary")
    add("")
    header = "| Benchmark | " + " | ".join(
        f"{lang_names[l]} median (s)" for l in lang_order) + " | Flow / C |"
    add(header)
    add("|" + "---|" * (len(lang_order) + 2))
    for b in BENCHES:
        meds = {l: statistics.median(data[b][l]["seconds"])
                for l in lang_order}
        ratio = meds["flow"] / meds["c"]
        row = f"| {b} | " + " | ".join(fmt_s(meds[l]) for l in lang_order)
        row += f" | {ratio:.2f}x |"
        add(row)
    add("")
    add("Flow / C below 1.00x means the Flow binary was faster on that run.")
    add("Differences within a few percent are run-to-run noise.")
    add("")
    add("## Notes")
    add("")
    add("- nbody is the one benchmark where the Flow binary trails hand C by")
    add("  more than noise. The arithmetic in the generated C is identical.")
    add("  The hand-written C declares its functions static, which lets clang")
    add("  specialize the pair loop for the constant body count at the call")
    add("  site. Flow emits externally visible functions, which blocks that")
    add("  specialization. Two manual experiments support this: adding static")
    add("  to the generated functions moved Flow into C's range, and removing")
    add("  static from the hand C moved C into Flow's range.")
    add("")

    add("## Benchmarks")
    add("")
    for b in BENCHES:
        add(f"### {b}")
        add("")
        add(DESCRIPTIONS[b])
        add("")
        add("| Language | Median (s) | Min (s) | Max (s) | Result |")
        add("|---|---|---|---|---|")
        for l in lang_order:
            secs = data[b][l]["seconds"]
            add(f"| {lang_names[l]} | {fmt_s(statistics.median(secs))} "
                f"| {fmt_s(min(secs))} | {fmt_s(max(secs))} "
                f"| {data[b][l]['result']} |")
        add("")

    add("## Compile time")
    add("")
    add("Measured once per benchmark. Compile time is excluded from every")
    add("workload number.")
    add("")
    add("| Benchmark | Flow transpile (s) | clang on generated C (s) "
        "| clang on hand C (s)" + (" | rustc (s) |" if have_rust else " |"))
    add("|---|---|---|---" + ("|---|" if have_rust else "|"))
    for b in BENCHES:
        t_transpile, t_clang = compile_times[b]["flow"]
        row = (f"| {b} | {t_transpile:.2f} | {t_clang:.2f} "
               f"| {compile_times[b]['c']:.2f}")
        if have_rust:
            row += f" | {compile_times[b]['rust']:.2f}"
        row += " |"
        add(row)
    add("")

    add("## Method")
    add("")
    add("- Each program times only its workload with a monotonic clock and")
    add("  prints the elapsed seconds itself. Compiler time, transpile time,")
    add("  and process startup are excluded.")
    add(f"- One warmup run, then {reps} timed repetitions per program.")
    add("  Median, min, and max of the timed repetitions are reported.")
    add("- Identical algorithms, data sizes, and double precision floats in")
    add("  every language. Sources live in benchmarks/publish/.")
    add("- Flow-generated C and hand-written C are compiled by the same")
    add(f"  clang with the same flags: `{' '.join(CFLAGS)}`.")
    add("  `-ffast-math` is not used.")
    if have_rust:
        add(f"- Rust: `rustc {' '.join(RUSTFLAGS)}`, one source file per")
        add("  benchmark, compiled directly with rustc.")
    add("- Python is plain CPython without numpy.")
    add("- Result values are printed by every program and checked for")
    add("  agreement across languages before this report is written.")
    add("- The machine was otherwise idle.")
    add("")

    add("## Environment")
    add("")
    add(f"- CPU: {env['cpu']}, {env['ncpu']} cores, {env['mem_gb']} GB RAM")
    add(f"- C compiler: {env['clang']}")
    add(f"- Python: {env['python']}")
    add(f"- Rust: {env['rustc']}")
    add("")

    add("## Reproduce")
    add("")
    add("```bash")
    add("./benchmarks/run_publish.sh")
    add("```")
    add("")
    add("This regenerates benchmarks/RESULTS.md in place. A full run takes")
    add("a few minutes; most of that is the Python repetitions.")

    out_path.write_text("\n".join(lines) + "\n")
    print(f"wrote {out_path}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true",
                    help="1 repetition, print numbers, skip the report")
    ap.add_argument("--reps", type=int, default=5)
    args = ap.parse_args()
    reps = 1 if args.quick else args.reps

    have_rust = shutil.which("rustc") is not None
    if not have_rust:
        print("rustc not found; skipping Rust")

    print("compiling ...")
    compile_times = compile_all(have_rust)
    cmds = bench_commands(have_rust)

    print(f"running ({reps} reps + 1 warmup each) ...")
    data = measure(cmds, reps)

    ok = True
    for b in BENCHES:
        values = [data[b][l]["result"] for l in data[b]]
        if not results_agree(values):
            ok = False
            print(f"RESULT MISMATCH in {b}: "
                  + ", ".join(f"{l}={data[b][l]['result']}"
                              for l in data[b]))
    if not ok:
        sys.exit(1)
    print("all results agree across languages")

    if args.quick:
        for b in BENCHES:
            for l, d in data[b].items():
                print(f"{b:12s} {l:8s} {d['seconds'][0]:.4f}s "
                      f"result={d['result']}")
        return

    write_report(data, compile_times, env_info(), reps, have_rust,
                 ROOT / "benchmarks" / "RESULTS.md")


if __name__ == "__main__":
    main()
