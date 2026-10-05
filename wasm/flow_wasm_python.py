#!/usr/bin/env python3
"""Crossing 4: Flow's CPython embedding, running against Pyodide in a browser.

runtime/flow_python_embed.c reaches CPython through libpython's C API. That
file cannot cross: there is no libpython.so to dlopen inside a browser, and
the CPython C API is not an ABI you can shim from JavaScript.

The Flow-visible surface is much smaller than the C API underneath it. Thirteen
functions, all C-ABI scalars and NUL-terminated strings
(lib/stdlib/python_embed.flow). That surface crosses. This build drops
flow_python_embed.c from the link line and supplies the same thirteen symbols
from wasm/crossing_assets/pyodide_bridge.js, an Emscripten --js-library that
routes them to Pyodide: CPython compiled to wasm, running as its own module in
the same page.

The two wasm modules never share memory. Everything crosses as a string or a
number, which is all the embedding surface ever asked for.

Usage:
    python3 wasm/flow_wasm_python.py [program.flow]
"""

from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from crossing_common import (  # noqa: E402
    BUILD_DIR,
    PROJECT_ROOT,
    SITE_DIR,
    emscripten_env,
    flow_to_c,
    read_asset,
    require_emcc,
    run,
    write_out,
)

DEFAULT_PROGRAM = PROJECT_ROOT / "examples" / "wasm" / "python_embed.flow"
PY_MODULE = PROJECT_ROOT / "examples" / "wasm" / "python" / "flow_demo.py"
BRIDGE = Path(__file__).resolve().parent / "crossing_assets" / "pyodide_bridge.js"

PYODIDE_VERSION = "0.27.2"
PYODIDE_CDN = f"https://cdn.jsdelivr.net/pyodide/v{PYODIDE_VERSION}/full/"


def build(program: Path, out_dir: Path, do_build: bool) -> None:
    stem = program.stem
    work = BUILD_DIR / "python"
    work.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Flow -> C: {program.relative_to(PROJECT_ROOT)}")
    c_file = flow_to_c(program, work / f"{stem}.c")

    if do_build:
        # Symbols the bridge defines in JS. Naming them keeps the linker from
        # dead-stripping the library and makes a typo a link error rather than
        # a silent no-op at runtime.
        bridge_symbols = [
            "_python_init",
            "_python_destroy",
            "_python_add_to_path",
            "_python_import_module",
            "_python_call0",
            "_python_call1_str",
            "_python_call1_i32",
            "_python_call1_f32",
            "_python_call1_bool",
            "_python_call3_i32_f64",
            "_python_last_error",
            "_print_line",
            "_main",
            "_malloc",
            "_free",
        ]
        run(
            [
                require_emcc(),
                "-O2",
                "-Wno-everything",
                str(c_file),
                # flow_python_embed.c is deliberately absent; the JS library
                # below provides the same symbols.
                "--js-library",
                str(BRIDGE),
                "-sMODULARIZE=1",
                "-sEXPORT_NAME=createFlowPython",
                "-sEXIT_RUNTIME=0",
                "-sINVOKE_RUN=0",
                "-sALLOW_MEMORY_GROWTH=1",
                "-sEXPORTED_FUNCTIONS=" + json.dumps(bridge_symbols),
                "-sEXPORTED_RUNTIME_METHODS=" + json.dumps(["callMain"]),
                "-sENVIRONMENT=web",
                "-o",
                str(out_dir / f"{stem}.js"),
            ],
            env=emscripten_env(),
        )

    write_out(out_dir / "flow_demo.py", PY_MODULE.read_text())
    write_out(out_dir / "crossing.css", read_asset("crossing.css"))
    write_out(out_dir / "index.html", page_html(stem, program))


def page_html(stem: str, program: Path) -> str:
    flow_src = html.escape(program.read_text())
    py_src = html.escape(PY_MODULE.read_text())
    bridge_src = html.escape(BRIDGE.read_text()[:2600])
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Flow crossing 4: CPython in the browser, via Pyodide</title>
<link rel="stylesheet" href="crossing.css">
</head>
<body>
<main>
<h1>Crossing 4 &mdash; embedded CPython</h1>
<p class="lede">
<code>runtime/flow_python_embed.c</code> drives libpython through the CPython C
API, and it cannot cross: there is no <code>libpython.so</code> to
<code>dlopen</code> in a browser. What crosses is the surface Flow actually
exposes, thirteen C-ABI functions in
<code>lib/stdlib/python_embed.flow</code>. This build drops the C file and
supplies those thirteen symbols from a JavaScript library that routes them to
Pyodide.
</p>

<div class="facts">
  <div class="fact"><span class="k">Pyodide</span><span class="v" id="f-pyodide">loading&hellip;</span></div>
  <div class="fact"><span class="k">interpreter</span><span class="v" id="f-impl">&hellip;</span></div>
  <div class="fact"><span class="k">bridge symbols</span><span class="v">13</span></div>
  <div class="fact"><span class="k">flow_python_embed.c</span><span class="v">not linked</span></div>
</div>

<h2>Run</h2>
<div class="panel">
  <button id="run" disabled>Run the Flow program</button>
  <button id="clear" class="secondary">Clear</button>
</div>

<h2>Checks</h2>
<div class="panel">
<table>
  <thead><tr><th>call</th><th>route</th><th>observed</th><th>verdict</th></tr></thead>
  <tbody id="rows"></tbody>
</table>
</div>

<h2>Program output</h2>
<pre id="out">waiting for Pyodide</pre>

<h2>Flow source</h2>
<pre class="source">{flow_src}</pre>

<h2>Python module (examples/wasm/python/flow_demo.py)</h2>
<pre class="source">{py_src}</pre>

<h2>The bridge (head of wasm/crossing_assets/pyodide_bridge.js)</h2>
<pre class="source">{bridge_src}</pre>

<footer>
Built by <code>wasm/flow_wasm_python.py</code>. Pyodide {PYODIDE_VERSION} from
jsDelivr, so this page needs network. Mechanism:
<code>docs/language/wasm-crossings.md</code>.
</footer>
</main>

<script src="{PYODIDE_CDN}pyodide.js"></script>
<script src="{stem}.js"></script>
<script>
const out = document.getElementById("out");
const log = (s) => {{ out.textContent += s + "\\n"; out.scrollTop = out.scrollHeight; }};
globalThis.flowPyLog = log;
const setFact = (id, text, cls) => {{
  const el = document.getElementById(id);
  el.textContent = text;
  el.className = "v" + (cls ? " " + cls : "");
}};
function addRow(call, route, observed, ok) {{
  const tr = document.createElement("tr");
  tr.innerHTML = `<td><code>${{call}}</code></td><td>${{route}}</td><td>${{observed}}</td>` +
                 `<td style="color:${{ok ? "var(--ok)" : "var(--bad)"}}">${{ok ? "ok" : "FAIL"}}</td>`;
  document.getElementById("rows").appendChild(tr);
}}

// python_init() is synchronous and loadPyodide() is not, so Pyodide is brought
// up first and parked on a global. The Flow program is unchanged; only the
// order of operations on this side had to move.
(async () => {{
  out.textContent = "";
  log("loading Pyodide " + "{PYODIDE_VERSION}" + " ...");
  const t0 = performance.now();
  const pyodide = await loadPyodide({{ indexURL: "{PYODIDE_CDN}" }});
  globalThis.flowPyodide = pyodide;
  const loadMs = performance.now() - t0;

  // Give the Flow program something to import. It asks for sys.path entry
  // "python", so the module goes there inside Pyodide's own filesystem.
  const source = await (await fetch("flow_demo.py")).text();
  pyodide.FS.mkdir("/home/pyodide/python");
  pyodide.FS.writeFile("/home/pyodide/python/flow_demo.py", source);

  const impl = pyodide.runPython(
    "import platform, sys; platform.python_implementation() + ' ' + sys.version.split()[0]"
  );
  setFact("f-pyodide", "loaded in " + loadMs.toFixed(0) + " ms", "ok");
  setFact("f-impl", impl, "ok");
  log("Pyodide ready: " + impl + " (" + loadMs.toFixed(0) + " ms)");
  log("wrote /home/pyodide/python/flow_demo.py into Pyodide's filesystem");
  log("");
  document.getElementById("run").disabled = false;
}})().catch((e) => {{
  setFact("f-pyodide", "failed", "bad");
  log("Pyodide failed to load: " + e);
}});

async function runProgram() {{
  document.getElementById("run").disabled = true;
  document.getElementById("rows").innerHTML = "";
  log("=== python_embed ===");
  const before = out.textContent.length;

  const m = await createFlowPython({{
    print: (s) => log(s),
    printErr: (s) => log("stderr: " + s),
    noInitialRun: true,
  }});
  // Pyodide writes Python's own stdout through its stdout handler; point it
  // at the same log so interleaving is visible.
  globalThis.flowPyodide.setStdout({{ batched: (s) => log(s) }});

  const t0 = performance.now();
  const rc = m.callMain([]);
  const ms = performance.now() - t0;
  const text = out.textContent.slice(before);

  const has = (re) => re.test(text);
  addRow("python_import_module", "pyodide.pyimport", has(/imported flow_demo/) ? "flow_demo imported" : "not imported", has(/imported flow_demo/));
  addRow("python_call0", "banner()", has(/\\[python\\] CPython/) ? text.match(/\\[python\\] (CPython [0-9.]+)/)[1] : "no output", has(/\\[python\\] CPython/));
  addRow("python_call1_str", "greet(\\"Flow\\")", has(/hello, Flow/) ? "hello, Flow" : "no output", has(/hello, Flow/));
  addRow("python_call1_i32", "square(12)", has(/12 squared is 144/) ? "144" : "no output", has(/12 squared is 144/));
  addRow("python_call1_f32", "scale(1.5)", has(/1\\.5000 \\* 3 = 4\\.5000/) ? "4.5000" : "no output", has(/1\\.5000 \\* 3 = 4\\.5000/));
  addRow("python_call1_bool", "toggle(True)", has(/not True is False/) ? "False" : "no output", has(/not True is False/));
  const hyp = text.match(/hypot3\\(3, 4, 12\\) returned ([0-9.]+)/);
  addRow("python_call3_i32_f64", "math.sqrt in Python", hyp ? hyp[1] : "no value", !!hyp && Math.abs(parseFloat(hyp[1]) - 13) < 1e-6);
  const evc = text.match(/recorded (\\d+) calls/);
  addRow("module state", "list on the Python module", evc ? evc[1] + " calls remembered" : "none", !!evc && parseInt(evc[1]) >= 6);
  const boom = text.match(/boom\\(\\) reported error code (\\d+)/);
  addRow("raised exception", "ValueError -> error code", boom ? "code " + boom[1] + ", message returned" : "not caught", !!boom);
  const miss = text.match(/missing attribute reported error code (\\d+)/);
  addRow("missing attribute", "AttributeError -> error code", miss ? "code " + miss[1] : "not caught", !!miss);

  const pass = rc === 0 && /\\bPASS\\b/.test(text);
  addRow("program exit", "main()", "rc " + rc + ", " + ms.toFixed(1) + " ms", pass);
  log(`  exit ${{rc}} in ${{ms.toFixed(1)}} ms`);
  document.getElementById("run").disabled = false;
  return pass;
}}

document.getElementById("run").onclick = runProgram;
document.getElementById("clear").onclick = () => {{ out.textContent = ""; }};
window.runProgram = runProgram;
</script>
</body>
</html>
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("program", nargs="?", default=str(DEFAULT_PROGRAM))
    ap.add_argument("--out", default=str(SITE_DIR / "python"))
    ap.add_argument("--no-build", action="store_true")
    args = ap.parse_args()

    program = Path(args.program).resolve()
    if not program.exists():
        sys.exit(f"no such program: {program}")

    build(program, Path(args.out).resolve(), not args.no_build)
    print("\nServe it:  python3 -m http.server -d site 8000")
    print("Then open: http://127.0.0.1:8000/wasm-crossings/python/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
