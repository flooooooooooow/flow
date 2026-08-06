#!/usr/bin/env python3
"""Crossing 2: a Flow @gpu kernel dispatched on the browser's GPU.

Flow owns its shader codegen. src/flow/metal_codegen.py turns an @gpu function
into Metal Shading Language straight from the AST; src/flow/wgsl_codegen.py is
its sibling and emits WGSL from the same AST. So the same kernel reaches a Mac
GPU through Metal and any GPU through WebGPU, with no vendor compiler and no
SPIR-V detour in between.

This script builds both halves of the proof from one Flow file:

  WGSL      one .wgsl per @gpu function, plus the binding reflection the host
            needs (binding indices, storage access modes, uniform layout)
  WASM      the same file through the C generator, where the kernel bodies
            become ordinary C driven one element at a time, giving a CPU
            reference computed from the identical AST

The page runs both and compares the results element by element.

Usage:
    python3 wasm/flow_wasm_gpu.py [program.flow] [-n 1048576]
"""

from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

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

DEFAULT_PROGRAM = PROJECT_ROOT / "examples" / "wasm" / "gpu_vector_add.flow"
SHIM_C = Path(__file__).resolve().parent / "crossing_assets" / "gpu_thread_id_shim.c"


def generate_wgsl(program: Path, out_dir: Path) -> list:
    from flow.module_resolver import ModuleResolver
    from flow.wgsl_codegen import WgslCodegen, extract_gpu_functions

    declarations = ModuleResolver(str(program)).resolve()
    gpu_funcs = extract_gpu_functions(declarations)
    if not gpu_funcs:
        sys.exit(f"no @gpu functions in {program}")

    kernels = []
    for func in gpu_funcs:
        codegen = WgslCodegen()
        source = codegen.generate_kernel(func)
        write_out(out_dir / f"{func.name}.wgsl", source)
        layout = codegen.binding_layout(func)
        # The CPU reference for gpu_foo is cpu_foo, exported @flow_api.
        layout["cpuEntry"] = "cpu_" + func.name[4:] if func.name.startswith("gpu_") else None
        layout["file"] = f"{func.name}.wgsl"
        kernels.append(layout)
    return kernels


def build_wasm(program: Path, kernels: list, out_dir: Path) -> None:
    work = BUILD_DIR / "gpu"
    work.mkdir(parents=True, exist_ok=True)
    c_file = flow_to_c(program, work / f"{program.stem}.c")

    exported = ["_malloc", "_free", "_fill_pattern"]
    exported += [f"_{k['cpuEntry']}" for k in kernels if k.get("cpuEntry")]

    emcc = require_emcc()
    run(
        [
            emcc,
            "-O2",
            "-Wno-everything",
            str(c_file),
            str(SHIM_C),
            "-sMODULARIZE=1",
            "-sEXPORT_ES6=0",
            "-sEXPORT_NAME=createFlowCpu",
            "-sALLOW_MEMORY_GROWTH=1",
            "-sEXPORTED_FUNCTIONS=" + json.dumps(exported),
            "-sEXPORTED_RUNTIME_METHODS=" + json.dumps(["HEAPF32", "HEAP32", "cwrap"]),
            "-sENVIRONMENT=web",
            "-o",
            str(out_dir / f"{program.stem}_cpu.js"),
        ],
        env=emscripten_env(),
    )


def page_html(program: Path, kernels: list, count: int, out_dir: Path) -> str:
    source = html.escape(program.read_text())
    first_wgsl = out_dir / kernels[0]["file"]
    wgsl_preview = html.escape(first_wgsl.read_text() if first_wgsl.exists() else "")
    manifest = json.dumps(kernels, indent=2)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Flow crossing 2: an @gpu kernel on WebGPU</title>
<link rel="stylesheet" href="crossing.css">
</head>
<body>
<main>
<h1>Crossing 2 &mdash; the GPU</h1>
<p class="lede">
Flow compiles an <code>@gpu</code> function to Metal today. The same AST goes
through <code>src/flow/wgsl_codegen.py</code> to WGSL, and the browser
dispatches it on the real GPU through WebGPU. The reference on the right comes
from the <em>same</em> kernel body compiled to C and run one element at a time
inside WASM, so the two columns are the same arithmetic on two machines.
</p>

<div class="facts">
  <div class="fact"><span class="k">WebGPU</span><span class="v" id="f-gpu">&hellip;</span></div>
  <div class="fact"><span class="k">adapter</span><span class="v" id="f-adapter">&hellip;</span></div>
  <div class="fact"><span class="k">elements</span><span class="v">{count:,}</span></div>
  <div class="fact"><span class="k">kernels</span><span class="v">{len(kernels)}</span></div>
</div>

<h2>Run</h2>
<div class="panel">
  <button id="run">Run every kernel on GPU and CPU</button>
  <button id="clear" class="secondary">Clear</button>
</div>

<h2>GPU vs CPU</h2>
<div class="panel">
<table>
  <thead><tr>
    <th>kernel</th><th>GPU (WGSL)</th><th>CPU (WASM)</th>
    <th>exact matches</th><th>max abs diff</th><th>verdict</th>
  </tr></thead>
  <tbody id="rows"></tbody>
</table>
</div>

<h2>Log</h2>
<pre id="out">click run</pre>

<h2>Generated WGSL (first kernel)</h2>
<pre class="source">{wgsl_preview}</pre>

<h2>Flow source</h2>
<pre class="source">{source}</pre>

<footer>
Built by <code>wasm/flow_wasm_gpu.py</code>; WGSL from
<code>src/flow/wgsl_codegen.py</code>. Mechanism:
<code>docs/language/wasm-crossings.md</code>.
</footer>
</main>

<script src="{program.stem}_cpu.js"></script>
<script type="module">
import {{ getDevice, runKernel, compare }} from "./webgpu-host.js";

const KERNELS = {manifest};
const N = {count};

const out = document.getElementById("out");
const log = (s) => {{ out.textContent += s + "\\n"; out.scrollTop = out.scrollHeight; }};
const setFact = (id, text, cls) => {{
  const el = document.getElementById(id);
  el.textContent = text;
  el.className = "v" + (cls ? " " + cls : "");
}};

setFact("f-gpu", navigator.gpu ? "present" : "missing", navigator.gpu ? "ok" : "bad");

let wasm = null;
const cpuReady = createFlowCpu({{ print: log, printErr: log }}).then((m) => {{ wasm = m; }});

// Scalars every kernel might ask for. The host picks the ones its uniform
// block declares.
const SCALARS = {{ n: N, alpha: 2.5 }};

async function runAll() {{
  document.getElementById("run").disabled = true;
  document.getElementById("rows").innerHTML = "";
  await cpuReady;

  let device;
  try {{
    const got = await getDevice();
    device = got.device;
    const info = got.adapter.info || {{}};
    setFact("f-adapter", [info.vendor, info.architecture].filter(Boolean).join(" ") || "ok", "ok");
  }} catch (e) {{
    setFact("f-adapter", "unavailable", "bad");
    log("WebGPU unavailable: " + e.message);
    document.getElementById("run").disabled = false;
    return;
  }}

  // Inputs live in the WASM heap so the CPU reference reads exactly the bytes
  // the GPU was handed.
  const bytes = N * 4;
  const pa = wasm._malloc(bytes), pb = wasm._malloc(bytes), pout = wasm._malloc(bytes);
  wasm._fill_pattern(pa, N, 12345);
  wasm._fill_pattern(pb, N, 98765);
  const a = wasm.HEAPF32.subarray(pa >> 2, (pa >> 2) + N).slice();
  const b = wasm.HEAPF32.subarray(pb >> 2, (pb >> 2) + N).slice();
  log(`inputs: a[0]=${{a[0]}} b[0]=${{b[0]}} a[${{N - 1}}]=${{a[N - 1]}}`);

  for (const kernel of KERNELS) {{
    log("--- " + kernel.kernel + " ---");
    const code = await (await fetch(kernel.file)).text();

    const inputs = {{}};
    for (const buf of kernel.buffers) {{
      if (buf.access !== "read") continue;
      inputs[buf.name] = buf.name === "b" ? b : a;
    }}

    const args = [pa, pb, pout, N];
    if (kernel.params.some((p) => p.name === "alpha")) args.push(SCALARS.alpha);

    // First call on either side pays for shader compilation and pipeline
    // creation on the GPU, and for V8's baseline WASM tier on the CPU. Run
    // each twice and report the second.
    let gpuRes;
    try {{
      const warm = await runKernel(device, kernel, code, inputs, SCALARS, N);
      log(`  first GPU dispatch (compile + pipeline): ${{warm.ms.toFixed(2)}} ms`);
      gpuRes = await runKernel(device, kernel, code, inputs, SCALARS, N);
    }} catch (e) {{
      log("GPU dispatch failed: " + e.message);
      addRow(kernel.kernel, "&mdash;", "&mdash;", "&mdash;", "&mdash;", "FAIL", false);
      continue;
    }}

    wasm["_" + kernel.cpuEntry](...args);
    const t0 = performance.now();
    wasm["_" + kernel.cpuEntry](...args);
    const cpuMs = performance.now() - t0;
    const cpu = wasm.HEAPF32.subarray(pout >> 2, (pout >> 2) + N).slice();

    const gpu = gpuRes.outputs.out;
    const cmp = compare(gpu, cpu);
    // Exact agreement is the bar for +, * and fma-free arithmetic. WGSL only
    // promises sqrt to 1 ulp, so a chain of them is checked to a tolerance.
    const exactBar = cmp.maxAbs === 0;
    const ok = exactBar || cmp.maxRel < 1e-4;
    const verdict = exactBar
      ? "bit-identical"
      : ok
      ? "agrees to " + cmp.maxRel.toExponential(1) + " rel"
      : "MISMATCH";
    log(`  gpu ${{gpuRes.ms.toFixed(2)}} ms, cpu ${{cpuMs.toFixed(2)}} ms  (${{(cpuMs / gpuRes.ms).toFixed(2)}}x)`);
    log(`  exact ${{cmp.exact}}/${{cmp.n}}, max abs diff ${{cmp.maxAbs}}, max rel ${{cmp.maxRel}}`);
    log(`  gpu[0]=${{gpu[0]}} cpu[0]=${{cpu[0]}}  gpu[${{N - 1}}]=${{gpu[N - 1]}} cpu[${{N - 1}}]=${{cpu[N - 1]}}`);
    addRow(
      kernel.kernel,
      gpuRes.ms.toFixed(2) + " ms",
      cpuMs.toFixed(2) + " ms (" + (cpuMs / gpuRes.ms).toFixed(2) + "x)",
      cmp.exact + " / " + cmp.n,
      String(cmp.maxAbs),
      verdict,
      ok
    );
  }}

  wasm._free(pa); wasm._free(pb); wasm._free(pout);
  document.getElementById("run").disabled = false;
}}

function addRow(...cells) {{
  const ok = cells.pop();
  const tr = document.createElement("tr");
  tr.innerHTML = cells.map((c) => `<td>${{c}}</td>`).join("");
  tr.lastChild.style.color = ok ? "var(--ok)" : "var(--bad)";
  document.getElementById("rows").appendChild(tr);
}}

document.getElementById("run").onclick = runAll;
document.getElementById("clear").onclick = () => {{ out.textContent = ""; }};
window.runAll = runAll;
</script>
</body>
</html>
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("program", nargs="?", default=str(DEFAULT_PROGRAM))
    ap.add_argument("-n", "--count", type=int, default=1 << 20)
    ap.add_argument("--out", default=str(SITE_DIR / "gpu"))
    ap.add_argument("--no-build", action="store_true")
    args = ap.parse_args()

    program = Path(args.program).resolve()
    if not program.exists():
        sys.exit(f"no such program: {program}")

    out_dir = Path(args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Flow @gpu -> WGSL: {program.relative_to(PROJECT_ROOT)}")
    kernels = generate_wgsl(program, out_dir)

    if not args.no_build:
        print("Flow -> C -> WASM (CPU reference)")
        build_wasm(program, kernels, out_dir)

    write_out(out_dir / "webgpu-host.js", read_asset("webgpu-host.js"))
    write_out(out_dir / "crossing.css", read_asset("crossing.css"))
    write_out(out_dir / "index.html", page_html(program, kernels, args.count, out_dir))

    print("\nServe it:  python3 -m http.server -d site 8000")
    print("Then open: http://127.0.0.1:8000/wasm-crossings/gpu/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
