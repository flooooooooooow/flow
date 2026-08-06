#!/usr/bin/env python3
"""Crossing 1: Flow's pthread concurrency runtime, running in a browser.

Builds a Flow program twice from one source:

  threaded     emcc -pthread -sPROXY_TO_PTHREAD -sPTHREAD_POOL_SIZE=N
  single       the same C with no -pthread at all

and drops both, plus a page that runs them back to back, into
site/wasm-crossings/threads/.

The Flow side needs no changes. `parallel for` and flow_parallel_for_i32 land
on pthread_create in runtime/flow_rt_parallel.c, and Emscripten implements
pthread_create with a Web Worker plus a SharedArrayBuffer heap. In the
single-thread build the same pthread_create fails, and Flow's parallel-for
already falls back to running the job inline, so the program stays correct and
simply stops going faster. That is the control.

Two browser facts shape the build:

  * SharedArrayBuffer needs cross-origin isolation, which a static host cannot
    give you. crossing_assets/coi-serviceworker.js adds the headers client-side.
  * The browser main thread must never block. Flow's parallel-for joins its
    workers, so main() is moved onto a worker with -sPROXY_TO_PTHREAD.

Usage:
    python3 wasm/flow_wasm_threads.py [program.flow] [--workers N] [--no-build]
"""

from __future__ import annotations

import argparse
import html
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from crossing_common import (  # noqa: E402
    BUILD_DIR,
    PROJECT_ROOT,
    RUNTIME_DIR,
    SITE_DIR,
    emscripten_env,
    flow_to_c,
    flow_to_c_available,
    read_asset,
    require_emcc,
    run,
    write_out,
)

DEFAULT_PROGRAM = PROJECT_ROOT / "examples" / "wasm" / "parallel_sum.flow"

# Flow-implemented runtime modules the concurrency surface needs.
RUNTIME_FLOW_MODULES = [PROJECT_ROOT / "lib" / "runtime" / "concurrency_parallel.flow"]

# C runtime kernels: the pthread create/join pair and the monotonic clock.
RUNTIME_C_SOURCES = [
    RUNTIME_DIR / "flow_rt_parallel.c",
    RUNTIME_DIR / "flow_rt_support.c",
]


def build(program: Path, workers: int, out_dir: Path, do_build: bool) -> dict:
    stem = program.stem
    work = BUILD_DIR / "threads"
    work.mkdir(parents=True, exist_ok=True)

    print(f"Flow -> C: {program.relative_to(PROJECT_ROOT)}")
    c_sources = [flow_to_c(program, work / f"{stem}.c")]
    for module in RUNTIME_FLOW_MODULES:
        c_sources.append(flow_to_c(module, work / f"{module.stem}.c", library=True))
    c_sources.extend(RUNTIME_C_SOURCES)

    out_dir.mkdir(parents=True, exist_ok=True)

    if do_build:
        emcc = require_emcc()
        env = emscripten_env()
        common = [
            "-O2",
            "-Wno-everything",
            f"-I{RUNTIME_DIR}",
            f"-DFLOW_PAR_WORKERS={workers}",
            *[str(s) for s in c_sources],
            "-sMODULARIZE=1",
            "-sEXIT_RUNTIME=1",
            "-sINITIAL_MEMORY=134217728",
            "-sENVIRONMENT=web,worker",
        ]

        print(f"C -> WASM (threaded, {workers} workers)")
        run(
            [
                emcc,
                *common,
                "-pthread",
                # One worker per shard, plus one for the proxied main().
                f"-sPTHREAD_POOL_SIZE={workers + 1}",
                # The browser main thread may not block, and Flow's
                # parallel-for joins. Move main() onto a worker.
                "-sPROXY_TO_PTHREAD",
                "-sEXPORT_NAME=createFlowThreaded",
                "-o",
                str(out_dir / f"{stem}_threaded.js"),
            ],
            env=env,
        )

        print("C -> WASM (single-thread control)")
        run(
            [
                emcc,
                *common,
                "-sEXPORT_NAME=createFlowSingle",
                "-o",
                str(out_dir / f"{stem}_single.js"),
            ],
            env=env,
        )

    write_out(out_dir / "coi-serviceworker.js", read_asset("coi-serviceworker.js"))
    write_out(out_dir / "crossing.css", read_asset("crossing.css"))
    write_out(out_dir / "index.html", page_html(stem, program, workers))

    return {"stem": stem, "out_dir": out_dir}


def page_html(stem: str, program: Path, workers: int) -> str:
    source = html.escape(program.read_text())
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Flow crossing 1: OS threads in WebAssembly</title>
<!-- Must run before anything touches SharedArrayBuffer: it reloads once to
     put the cross-origin-isolation service worker in control. -->
<script src="coi-serviceworker.js"></script>
<link rel="stylesheet" href="crossing.css">
</head>
<body>
<main>
<h1>Crossing 1 &mdash; OS threads</h1>
<p class="lede">
Flow's concurrency runtime is pthreads. This page runs the same Flow program
twice: once built with <code>-pthread</code>, so
<code>flow_parallel_for_i32</code> lands on real <code>pthread_create</code>
backed by Web Workers over a shared heap, and once built without it, where
<code>pthread_create</code> fails and Flow's parallel-for falls back to running
the job inline.
</p>

<div class="facts">
  <div class="fact"><span class="k">cross-origin isolated</span><span class="v" id="f-coi">&hellip;</span></div>
  <div class="fact"><span class="k">SharedArrayBuffer</span><span class="v" id="f-sab">&hellip;</span></div>
  <div class="fact"><span class="k">hardwareConcurrency</span><span class="v" id="f-hc">&hellip;</span></div>
  <div class="fact"><span class="k">build workers</span><span class="v">{workers}</span></div>
</div>

<h2>Run</h2>
<div class="panel">
  <button id="run-threaded">Run threaded build</button>
  <button id="run-single" class="secondary">Run single-thread build</button>
  <button id="clear" class="secondary">Clear</button>
</div>

<h2>Measured</h2>
<div class="panel">
<table>
  <thead><tr><th>build</th><th>serial pass</th><th>threaded pass</th><th>in-process speedup</th><th>result</th></tr></thead>
  <tbody>
    <tr><td>threaded (-pthread)</td><td id="t-ser">&mdash;</td><td id="t-par">&mdash;</td><td id="t-sp">&mdash;</td><td id="t-res">&mdash;</td></tr>
    <tr><td>single-thread control</td><td id="s-ser">&mdash;</td><td id="s-par">&mdash;</td><td id="s-sp">&mdash;</td><td id="s-res">&mdash;</td></tr>
  </tbody>
</table>
</div>

<h2>Program output</h2>
<pre id="out">click a button</pre>

<h2>Flow source</h2>
<pre class="source">{source}</pre>

<footer>
Built by <code>wasm/flow_wasm_threads.py</code>. Mechanism and constraints:
<code>docs/language/wasm-crossings.md</code>.
</footer>
</main>

<script src="{stem}_threaded.js"></script>
<script src="{stem}_single.js"></script>
<script>
const out = document.getElementById("out");
const log = (line) => {{ out.textContent += line + "\\n"; out.scrollTop = out.scrollHeight; }};

function setFact(id, text, cls) {{
  const el = document.getElementById(id);
  el.textContent = text;
  el.className = "v" + (cls ? " " + cls : "");
}}

setFact("f-coi", self.crossOriginIsolated ? "yes" : "no", self.crossOriginIsolated ? "ok" : "bad");
setFact("f-sab", typeof SharedArrayBuffer === "function" ? "available" : "blocked",
        typeof SharedArrayBuffer === "function" ? "ok" : "bad");
setFact("f-hc", String(navigator.hardwareConcurrency || "?"));

// Pull the numbers the Flow program prints straight out of its stdout.
function parseRun(text) {{
  const num = (re) => {{ const m = text.match(re); return m ? parseFloat(m[1]) : null; }};
  return {{
    serial: num(/serial:\\s+ms\\s+([0-9.]+)/),
    parallel: num(/threaded:\\s+ms\\s+([0-9.]+)/),
    speedup: num(/speedup:\\s+([0-9.]+)x/),
    pass: /\\bPASS\\b/.test(text),
  }};
}}

function fill(prefix, r, wall) {{
  const f = (v, s) => (v === null ? "&mdash;" : v.toFixed(2) + s);
  document.getElementById(prefix + "-ser").innerHTML = f(r.serial, " ms");
  document.getElementById(prefix + "-par").innerHTML = f(r.parallel, " ms");
  document.getElementById(prefix + "-sp").innerHTML = f(r.speedup, "x");
  const res = document.getElementById(prefix + "-res");
  res.textContent = (r.pass ? "PASS" : "FAIL") + " (" + wall.toFixed(0) + " ms wall)";
  res.style.color = r.pass ? "var(--ok)" : "var(--bad)";
}}

async function runModule(factory, label, prefix, buttons) {{
  buttons.forEach((b) => (b.disabled = true));
  log("=== " + label + " ===");
  let text = "";
  const t0 = performance.now();
  await new Promise((resolve) => {{
    factory({{
      print: (s) => {{ text += s + "\\n"; log(s); }},
      printErr: (s) => {{ text += s + "\\n"; log("stderr: " + s); }},
      onExit: () => resolve(),
      quit: () => resolve(),
    }}).catch((e) => {{ log("module failed: " + e); resolve(); }});
  }});
  const wall = performance.now() - t0;
  fill(prefix, parseRun(text), wall);
  log("");
  buttons.forEach((b) => (b.disabled = false));
}}

const btnT = document.getElementById("run-threaded");
const btnS = document.getElementById("run-single");
const btns = [btnT, btnS];

btnT.onclick = () => {{
  if (!self.crossOriginIsolated) {{
    log("not cross-origin isolated: SharedArrayBuffer is blocked, so the");
    log("threaded build cannot start. Reload once to let the service worker");
    log("take control, and serve over https or localhost.");
    return;
  }}
  runModule(createFlowThreaded, "threaded build (-pthread, PROXY_TO_PTHREAD)", "t", btns);
}};
btnS.onclick = () => runModule(createFlowSingle, "single-thread control (no -pthread)", "s", btns);
document.getElementById("clear").onclick = () => {{ out.textContent = ""; }};
</script>
</body>
</html>
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("program", nargs="?", default=str(DEFAULT_PROGRAM))
    ap.add_argument("--workers", type=int, default=8, help="pthread pool size / shard count")
    ap.add_argument("--out", default=str(SITE_DIR / "threads"))
    ap.add_argument("--no-build", action="store_true", help="regenerate the page only")
    args = ap.parse_args()

    program = Path(args.program).resolve()
    if not program.exists():
        sys.exit(f"no such program: {program}")
    if not flow_to_c_available():
        sys.exit("Flow compiler not importable; run from the project root.")

    build(program, args.workers, Path(args.out).resolve(), not args.no_build)
    print("\nServe it:  python3 -m http.server -d site 8000")
    print("Then open: http://127.0.0.1:8000/wasm-crossings/threads/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
