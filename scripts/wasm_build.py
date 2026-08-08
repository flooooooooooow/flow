#!/usr/bin/env python3
"""Compile one Flow program to a runnable WebAssembly page.

Pipeline (CPU backend selectable):
  - ``c`` (default): Flow → C (flow.transpiler --c) → emcc → HTML
  - ``mlir``: Flow → MLIR → LLVM IR → emcc → HTML

Two shapes come out the other end.

Graphics programs (anything that reaches ``lib/stdlib/gfx.flow``) are linked
against ``runtime/gfx_wasm.c``, the browser backend of the gfx API. The page
gets a canvas, keyboard wiring that speaks the same macOS keycodes the games
use, and a click-to-start overlay because browsers want a gesture first.

Everything else is a console program. The page runs ``main`` on click and
streams stdout into a ``<pre>``.

Native Metal / Python-embed / Darwin frameworks are never linked here.
Browser GPU stays WGSL/WebGPU (see docs/language/wasm-crossings.md);
MLIR→SPIR-V remains a separate native emit path.

Usage:
    python3 scripts/wasm_build.py examples/games/snake_gfx.flow --out site/wasm/snake
    python3 scripts/wasm_build.py examples/wasm/hello_wasm.flow --backend=mlir
    python3 scripts/wasm_build.py examples/wasm/hello_wasm.flow --backend=mlir \\
        --preload /tmp/data@/data --link runtime/flow_rt_support.c
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TRANSPILER = "flow.transpiler"

# Homebrew's emscripten ships a config pointing LLVM_ROOT at Xcode clang (no
# wasm backend) and a launcher that picks a python too old to parse its own
# sources. Point both at emscripten's own copies unless the caller already has.
HOMEBREW_ENV = {
    "EMSDK_PYTHON": "/opt/homebrew/bin/python3.14",
    "EM_LLVM_ROOT": "/opt/homebrew/opt/emscripten/libexec/llvm/bin",
    "EM_BINARYEN_ROOT": "/opt/homebrew/opt/emscripten/libexec/binaryen",
}


class BuildError(RuntimeError):
    """A stage of the pipeline failed; the message is the reason to report."""


def emcc_env() -> dict:
    env = dict(os.environ)
    for key, value in HOMEBREW_ENV.items():
        if env.get(key):
            continue
        target = Path(value)
        if target.exists():
            env[key] = value
    return env


def have_emcc() -> bool:
    if shutil.which("emcc") is None:
        return False
    try:
        proc = subprocess.run(
            ["emcc", "-v"],
            capture_output=True,
            text=True,
            env=emcc_env(),
            timeout=30,
        )
        return proc.returncode == 0
    except Exception:
        return False


def resolve_backend(explicit: Optional[str] = None) -> str:
    mode = (explicit or os.environ.get("FLOW_CPU_BACKEND") or "c").strip().lower()
    if mode not in ("c", "mlir"):
        raise BuildError(f"unknown backend {mode!r} (expected c|mlir)")
    return mode


def flow_to_c(program: Path, c_out: Path, library: bool = False) -> str:
    """Transpile a Flow program (or, with library=True, a runtime library) to
    C. Returns the generated C source."""
    c_out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, "-m", TRANSPILER, str(program), "--c"]
    if library:
        cmd.append("--library")
    cmd += ["--lenient", "-o", str(c_out)]
    proc = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True, text=True)
    if proc.returncode != 0 or not c_out.exists():
        detail = (proc.stderr or proc.stdout or "").strip().splitlines()
        raise BuildError("flow->c: " + (detail[-1] if detail else "transpiler failed"))
    return c_out.read_text()


def flow_to_llvm_ir(program: Path, ll_out: Path) -> str:
    """Transpile Flow → MLIR → LLVM IR for emcc. Returns the IR text."""
    ll_out.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            TRANSPILER,
            str(program),
            "--mlir",
            "--llvm",
            "--lenient",
            "-o",
            str(ll_out),
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": str(PROJECT_ROOT / "src")
             + ((":" + os.environ["PYTHONPATH"]) if os.environ.get("PYTHONPATH") else "")},
    )
    if proc.returncode != 0 or not ll_out.exists() or ll_out.stat().st_size == 0:
        detail = (proc.stderr or proc.stdout or "").strip().splitlines()
        raise BuildError(
            "flow->mlir->llvm: " + (detail[-1] if detail else "transpiler failed")
        )
    return ll_out.read_text()


def uses_gfx(source: str) -> bool:
    """True when the lowered TU references the Flow gfx ABI (C or LLVM IR)."""
    return "flow_gfx_init" in source


def uses_gfx_flow_source(flow_source: str) -> bool:
    """Heuristic for gfx before lowering (imports / API names)."""
    markers = (
        'import "stdlib/gfx.flow"',
        "import \"stdlib/gfx",
        "flow_gfx_",
        "gfx_init",
        "gfx_present",
    )
    return any(m in flow_source for m in markers)


def filter_browser_link_inputs(paths: list[Path]) -> list[Path]:
    """Drop native-only sources (Cocoa .m, Metal) that cannot link under emcc."""
    out: list[Path] = []
    for path in paths:
        suffix = path.suffix.lower()
        if suffix in (".m", ".mm", ".metal"):
            continue
        out.append(path)
    return out


def emcc_command(
    input_file: Path,
    out_js: Path,
    gfx: bool,
    opt: str,
    preload: Optional[list[str]] = None,
    extra_link: Optional[list[Path]] = None,
    initial_memory: str = "32MB",
    asyncify_stack_size: int = 32768,
    emcc_flags: Optional[list[str]] = None,
    threads: bool = False,
    workers: int = 8,
) -> list:
    sources: list[str] = [str(input_file)]
    if gfx:
        sources.append(str(PROJECT_ROOT / "runtime" / "gfx_wasm.c"))
    for path in filter_browser_link_inputs(list(extra_link or [])):
        sources.append(str(path.resolve()))

    cmd: list[str] = ["emcc", *sources, opt]
    if gfx:
        # ASYNCIFY lets flow_gfx_present hand the event loop back to the
        # browser from inside the Flow program's own while-loop.
        cmd += [
            "-sASYNCIFY=1",
            f"-sASYNCIFY_STACK_SIZE={asyncify_stack_size}",
        ]
    cmd += [
        "-o", str(out_js),
        f"-sINITIAL_MEMORY={initial_memory}",
        "-sMODULARIZE=1",
    ]
    if threads:
        # Real pthreads over SharedArrayBuffer: one pre-spawned worker per
        # shard, plus one for the proxied main thread. main() runs on a worker
        # (the browser main thread must never block), and the module factory
        # resolves once the program exits, so the page never calls callMain.
        # No -sSTACK_SIZE here: with -pthread the stack setting is applied per
        # pthread and carved out of the fixed SAB heap, so a 16MB stack per
        # worker would exhaust it (Aborted(OOM) on first spawn).
        cmd += [
            "-sENVIRONMENT=web,worker",
            "-sEXPORT_NAME=createFlowThreaded",
            "-pthread",
            f"-sPTHREAD_POOL_SIZE={workers + 1}",
            "-sPROXY_TO_PTHREAD",
            f"-DFLOW_PAR_WORKERS={workers}",
            "-sEXIT_RUNTIME=1",
        ]
    else:
        cmd += [
            "-sENVIRONMENT=web",
            "-sALLOW_MEMORY_GROWTH=1",
            # Flow puts fixed-size arrays on the stack, and a field simulation
            # holds several 128x128 grids of doubles at once. wasm32 defaults
            # to a 64 KB stack, which those overrun instantly.
            "-sSTACK_SIZE=16MB",
            "-sEXPORT_NAME=createFlowModule",
            "-sINVOKE_RUN=0",
            "-sEXIT_RUNTIME=0",
            "-sEXPORTED_RUNTIME_METHODS=callMain,ccall",
            "-sEXPORTED_FUNCTIONS=_main,_malloc,_free",
        ]
    cmd += [
        "-Wno-implicit-function-declaration",
        "-lm",
    ]
    if preload:
        # Without FORCE_FILESYSTEM, emcc may strip MEMFS when it cannot see
        # fopen uses through the .ll path (#225).
        cmd.append("-sFORCE_FILESYSTEM=1")
        for spec in preload:
            cmd.extend(["--preload-file", spec])
    if emcc_flags:
        cmd.extend(emcc_flags)
    return cmd


def compile_wasm(
    input_file: Path,
    out_js: Path,
    gfx: bool,
    opt: str,
    timeout: int,
    preload: Optional[list[str]] = None,
    extra_link: Optional[list[Path]] = None,
    initial_memory: str = "32MB",
    asyncify_stack_size: int = 32768,
    emcc_flags: Optional[list[str]] = None,
    threads: bool = False,
    workers: int = 8,
) -> None:
    out_js.parent.mkdir(parents=True, exist_ok=True)
    cmd = emcc_command(
        input_file,
        out_js,
        gfx,
        opt,
        preload=preload,
        extra_link=extra_link,
        initial_memory=initial_memory,
        asyncify_stack_size=asyncify_stack_size,
        emcc_flags=emcc_flags,
        threads=threads,
        workers=workers,
    )
    try:
        proc = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True,
                              text=True, env=emcc_env(), timeout=timeout)
    except subprocess.TimeoutExpired:
        raise BuildError(f"emcc: timed out after {timeout}s")
    if proc.returncode != 0:
        raise BuildError("emcc: " + first_error(proc.stderr or proc.stdout))
    if not out_js.with_suffix(".wasm").exists():
        raise BuildError("emcc: no .wasm emitted")
    if preload and not out_js.with_suffix(".data").exists():
        raise BuildError("emcc: --preload requested but no .data package emitted")


# ---------------------------------------------------------------------------
# Browser stubs for host-only externs
# ---------------------------------------------------------------------------

# Host-only C symbols the wasm build cannot link natively (no host OS, CPU
# feature probes, GPU, tape runtime, ...). Each entry maps the missing symbol
# to a browser-facing definition appended to the generated C before emcc runs.
# EM_ASM reads real host facts (OS, core count) from the browser tab itself;
# anything genuinely unprobeable from wasm degrades to an honest default.
EXTERN_STUBS = {
    "num_cores": "int32_t num_cores(void) { return EM_ASM_INT(return (navigator.hardwareConcurrency || 1) | 0); }",
    "os_is_linux": "bool os_is_linux(void) { return EM_ASM_INT(return /linux/i.test(navigator.platform || '') ? 1 : 0); }",
    "os_is_windows": "bool os_is_windows(void) { return EM_ASM_INT(return /win/i.test(navigator.platform || '') ? 1 : 0); }",
    "os_is_macos": "bool os_is_macos(void) { return EM_ASM_INT(return /mac/i.test(navigator.platform || '') ? 1 : 0); }",
    "has_sse4": "bool has_sse4(void) { return 0; }",
    "has_avx": "bool has_avx(void) { return 0; }",
    "has_avx2": "bool has_avx2(void) { return 0; }",
    "has_avx512f": "bool has_avx512f(void) { return 0; }",
    "has_avx512_vnni": "bool has_avx512_vnni(void) { return 0; }",
    "has_neon": "bool has_neon(void) { return 0; }",
    "is_apple_m1": "bool is_apple_m1(void) { return 0; }",
    "has_intel_amx": "bool has_intel_amx(void) { return 0; }",
    "current_cpu": "char* current_cpu(void) { return \"web browser\"; }",
    "current_arch": "char* current_arch(void) { return \"wasm32\"; }",
    "_cpu_features_string": "char* _cpu_features_string(void) { return \"n/a (browser)\"; }",
    "print_kv_str": "void print_kv_str(char* label, char* val) { printf(\"%s %s\\n\", label, val); }",
    "print_kv_i32": "void print_kv_i32(char* label, int32_t val) { printf(\"%s %d\\n\", label, val); }",
    # flow_parallel_for_i32 / flow_rt_par_workers are NOT stubbed: examples that
    # use them build in threads mode, where the parallel-for orchestration
    # (lib/runtime/concurrency_parallel.flow) compiles as a library and lands on
    # real pthread_create over SharedArrayBuffer (see build() threads=True).
}


def _append_extern_stubs(c_source: str) -> str:
    """Append browser-facing definitions for host-only externs the generated
    C references but does not define (os_is_linux, num_cores, ...).

    Only symbols that are *called* and *missing* from the generated C get a
    stub. Caveat: the check inspects the generated C only, not the `extra_link`
    translation units — keep EXTERN_STUBS free of symbols that linked runtime
    files provide (e.g. flow_rt_monotonic_ns comes from flow_rt_support.c),
    or a later entry would double-define them at link time.
    """
    missing = []
    for sym, stub in EXTERN_STUBS.items():
        referenced = re.search(rf"\b{re.escape(sym)}\s*\(", c_source)
        # A definition is `TYPE sym(...) {`; a call like `if (sym()) {` must
        # not count as one, so require the name to be preceded by a type token
        # (not an open paren / word char) and the `)` to be followed by `{`.
        defined = re.search(
            rf"(?<![\w(])\b{re.escape(sym)}\s*\([^;]*\)\s*{{",
            c_source,
        )
        if referenced and not defined:
            missing.append(stub)
    if not missing:
        return c_source
    block = ["", "/* Browser stubs for host-only externs (see EXTERN_STUBS). */",
             "#include <emscripten/emscripten.h>"]
    block.extend(missing)
    return c_source + "\n" + "\n".join(block) + "\n"


def tidy(line: str) -> str:
    """Drop scratch paths so the reason reads the same on any machine."""
    import re
    line = re.sub(r"\S*emscripten_temp_\S+?[:\s]", "", line)
    line = line.replace(str(PROJECT_ROOT) + "/", "")
    line = re.sub(r"^(emcc|wasm-ld|clang):\s*", "", line)
    line = re.sub(r"\s*\[-W[a-z-]+\]", "", line)
    return line.strip()


def first_error(text: str) -> str:
    """Pull the most useful single line out of an emcc failure."""
    lines = [ln.strip() for ln in (text or "").splitlines() if ln.strip()]
    import re
    for line in lines:
        hit = re.search(r"undefined (?:exported )?symbol:?\s*\"?([\w.$]+)", line)
        if hit:
            return f"undefined symbol {hit.group(1).lstrip('_')}"
    for line in lines:
        if "error:" in line.lower():
            return tidy(line)[:200]
    return tidy(lines[-1] if lines else "unknown error")[:200]


# ---------------------------------------------------------------------------
# HTML host page
# ---------------------------------------------------------------------------

PAGE_CSS = """
:root { color-scheme: dark; }
* { box-sizing: border-box; }
body {
  margin: 0; padding: 0;
  background: #0c0d11; color: #d8dae4;
  font: 14px/1.55 ui-sans-serif, -apple-system, "Segoe UI", sans-serif;
  display: flex; flex-direction: column; min-height: 100vh;
}
header {
  padding: 10px 16px; border-bottom: 1px solid #1e2029;
  display: flex; gap: 12px; align-items: baseline; flex-wrap: wrap;
}
header h1 { font-size: 15px; margin: 0; font-weight: 600; letter-spacing: .01em; }
header .meta { color: #6d7183; font-size: 12px; }
header a { color: #7aa2f7; text-decoration: none; }
header a:hover { text-decoration: underline; }
main { flex: 1; display: flex; flex-direction: column; align-items: center;
       justify-content: center; padding: 16px; gap: 12px; }
.stage { position: relative; line-height: 0; max-width: 100%; }
canvas { display: block; background: #000; border: 1px solid #22252f;
         border-radius: 4px; image-rendering: pixelated;
         width: auto; height: auto;
         max-width: 100%; max-height: calc(100vh - 190px); }
.overlay {
  position: absolute; inset: 0; display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 10px; cursor: pointer;
  background: rgba(9,10,14,.86); border-radius: 4px; line-height: 1.5;
}
.overlay strong { font-size: 16px; font-weight: 600; }
.overlay span { color: #8a8fa3; font-size: 12px; max-width: 30ch;
                text-align: center; }
.overlay.hidden { display: none; }
button {
  font: inherit; background: #7aa2f7; color: #0c0d11; border: 0;
  border-radius: 5px; padding: 7px 18px; cursor: pointer; font-weight: 600;
}
button:hover { background: #93b5ff; }
button:disabled { background: #2a2d38; color: #6d7183; cursor: default; }
.bar { display: flex; gap: 8px; align-items: center; flex-wrap: wrap;
       color: #6d7183; font-size: 12px; }
pre#out {
  width: min(880px, 100%); margin: 0; padding: 10px 12px; min-height: 3em;
  max-height: 40vh; overflow: auto; background: #08090c;
  border: 1px solid #1e2029; border-radius: 4px; color: #9ece6a;
  font: 12px/1.5 ui-monospace, SFMono-Regular, Menlo, monospace;
  white-space: pre-wrap; word-break: break-word;
}
pre#out:empty { display: none; }
.keys { color: #6d7183; font-size: 12px; text-align: center;
        max-width: 60ch; }
.err { color: #f7768e; }
/* Per-example note card (e.g. the tiny-pointers abstract-claim coverage map). */
details.coverage {
  width: min(880px, 100%); margin: 12px auto 0; padding: 10px 14px;
  background: #101219; border: 1px solid #1e2029; border-radius: 4px;
}
details.coverage summary {
  cursor: pointer; font-weight: 600; color: #d8dae4;
  font-size: 13px; user-select: none;
}
details.coverage summary:hover { color: #7aa2f7; }
details.coverage .note { color: #6d7183; font-size: 12px; margin: 8px 0 4px; }
details.coverage table { border-collapse: collapse; width: 100%; margin: 6px 0;
                         font-size: 12.5px; }
details.coverage th, details.coverage td { text-align: left; padding: 4px 8px;
  border-bottom: 1px solid #1a1c24; vertical-align: top; }
details.coverage th { color: #8a8fa3; font-weight: 600; white-space: nowrap; }
details.coverage a { color: #7aa2f7; text-decoration: none; }
details.coverage a:hover { text-decoration: underline; }
"""

GFX_BODY = """
<main>
  <div class="stage">
    <canvas id="canvas" width="__W__" height="__H__"></canvas>
    <div class="overlay" id="overlay">
      <strong>Click to run</strong>
      <span>__TITLE__ compiled to WebAssembly. Keyboard goes straight to the
      program once it starts.</span>
      <button id="start">Start</button>
    </div>
  </div>
  <div class="bar">
    <button id="stop" disabled>Stop</button>
    <span id="status">idle</span>
  </div>
  <div class="keys">__KEYS__</div>
  <pre id="out"></pre>
</main>
"""

CONSOLE_BODY = """
<main>
  <div class="bar">
    <button id="start">Run</button>
    <button id="clear">Clear</button>
    <span id="status">idle</span>
  </div>
  <pre id="out"></pre>
</main>
"""

GFX_SCRIPT = """
<script src="__NAME__.js"></script>
<script>
(function () {
  var overlay = document.getElementById('overlay');
  var startBtn = document.getElementById('start');
  var stopBtn = document.getElementById('stop');
  var status = document.getElementById('status');
  var out = document.getElementById('out');
  var started = false;

  function log(text, isErr) {
    var line = document.createElement('span');
    if (isErr) { line.className = 'err'; }
    line.textContent = text + '\\n';
    out.appendChild(line);
    out.scrollTop = out.scrollHeight;
  }

  window.flowGfxOnStart = function (title, w, h) { status.textContent = 'running ' + w + 'x' + h; };
  window.flowGfxOnExit = function (frames) {
    status.textContent = 'finished after ' + frames + ' frames';
    stopBtn.disabled = true;
  };

  function boot() {
    if (started) { return; }
    started = true;
    overlay.classList.add('hidden');
    status.textContent = 'loading module...';
    window.focus();
    createFlowModule({
      print: function (t) { log(t, false); },
      printErr: function (t) { log(t, true); },
      canvas: document.getElementById('canvas')
    }).then(function (mod) {
      stopBtn.disabled = false;
      status.textContent = 'running';
      try { mod.callMain([]); } catch (e) {
        if (!(e && e.name === 'ExitStatus')) { log('' + e, true); }
      }
    }).catch(function (e) {
      status.textContent = 'failed to load';
      log('' + e, true);
    });
  }

  overlay.addEventListener('click', boot);
  startBtn.addEventListener('click', function (e) { e.stopPropagation(); boot(); });
  stopBtn.addEventListener('click', function () {
    if (window.flowGfxStop) { window.flowGfxStop(); }
    status.textContent = 'stopping...';
  });
  // The gallery loads these pages in an iframe; autostart on request.
  if (location.search.indexOf('autostart=1') >= 0) { boot(); }
  document.addEventListener('click', function () { window.focus(); });
})();
</script>
"""

CONSOLE_SCRIPT = """
<script src="__NAME__.js"></script>
<script>
(function () {
  var startBtn = document.getElementById('start');
  var clearBtn = document.getElementById('clear');
  var status = document.getElementById('status');
  var out = document.getElementById('out');

  function log(text, isErr) {
    var line = document.createElement('span');
    if (isErr) { line.className = 'err'; }
    line.textContent = text + '\\n';
    out.appendChild(line);
    out.scrollTop = out.scrollHeight;
  }

  function run() {
    startBtn.disabled = true;
    status.textContent = 'running...';
    createFlowModule({
      print: function (t) { log(t, false); },
      printErr: function (t) { log(t, true); }
    }).then(function (mod) {
      var code = 0;
      try { code = mod.callMain([]); } catch (e) {
        if (e && e.name === 'ExitStatus') { code = e.status; }
        else { log('' + e, true); code = -1; }
      }
      if (code === undefined) { code = 0; }
      // Plenty of Flow examples answer with a return value rather than
      // printing, so always show it.
      log((out.textContent ? '\\n' : '') + 'main returned ' + code, false);
      status.textContent = 'exit ' + code;
      startBtn.disabled = false;
    }).catch(function (e) {
      log('' + e, true);
      status.textContent = 'failed to load';
      startBtn.disabled = false;
    });
  }

  startBtn.addEventListener('click', run);
  clearBtn.addEventListener('click', function () { out.textContent = ''; });
  if (location.search.indexOf('autostart=1') >= 0) { run(); }
})();
</script>
"""

THREADS_BODY = """
<main>
  <div class="bar">
    <button id="start">Run (pthreads)</button>
    <button id="clear">Clear</button>
    <span id="status">idle</span>
  </div>
  <pre id="out"></pre>
  <div class="keys">This build runs on real pthreads over SharedArrayBuffer and
  Web Workers. The browser only allows SharedArrayBuffer on cross-origin-isolated
  pages: open this page in a tab and let its service worker reload once.</div>
</main>
"""

THREADS_SCRIPT = """
<script src="__NAME__.js"></script>
<script>
(function () {
  var startBtn = document.getElementById('start');
  var clearBtn = document.getElementById('clear');
  var status = document.getElementById('status');
  var out = document.getElementById('out');

  function log(text, isErr) {
    var line = document.createElement('span');
    if (isErr) { line.className = 'err'; }
    line.textContent = text + '\\n';
    out.appendChild(line);
    out.scrollTop = out.scrollHeight;
  }

  var isolated = self.crossOriginIsolated && typeof SharedArrayBuffer === 'function';

  function showIsolation() {
    status.textContent = 'needs cross-origin isolation';
    startBtn.disabled = true;
    log('The browser blocks SharedArrayBuffer unless the page is cross-origin isolated,');
    log('and an iframe cannot become isolated on its own. Open this page in a tab:');
    log('the service worker adds the isolation headers and reloads once.');
  }

  function run() {
    startBtn.disabled = true;
    status.textContent = 'spawning workers...';
    var done = false;
    function finish(code) {
      if (done) { return; }
      done = true;
      log((out.textContent ? '\\n' : '') + 'main returned ' + code);
      status.textContent = 'exit ' + code;
      startBtn.disabled = false;
    }
    // With PROXY_TO_PTHREAD the module factory resolves as soon as the
    // runtime is initialised, before main() has run on its worker thread.
    // Only onExit fires when main() really returns, so it alone finishes.
    createFlowThreaded({
      print: function (t) { log(t, false); },
      printErr: function (t) { log(t, true); },
      onExit: function (code) { finish(code === undefined ? 0 : code); }
    }).then(function () {
      if (!done) { status.textContent = 'running (pthreads)...'; }
    }).catch(function (e) {
      if (done) { return; }
      done = true;
      log('' + e, true);
      status.textContent = 'failed to load';
      startBtn.disabled = false;
    });
  }

  if (!isolated) { showIsolation(); }
  startBtn.addEventListener('click', run);
  clearBtn.addEventListener('click', function () { out.textContent = ''; });
  if (location.search.indexOf('autostart=1') >= 0 && isolated) { run(); }
})();
</script>
"""


def html_escape(text: str) -> str:
    return (text.replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;").replace('"', "&quot;"))


def canvas_size(flow_source: str) -> tuple:
    """Best-effort read of the gfx_open(w, h, ...) call in a Flow program."""
    import re
    match = re.search(r"gfx_open\s*\(\s*(\d+)\s*,\s*(\d+)", flow_source)
    if match:
        return int(match.group(1)), int(match.group(2))
    # Some programs pass named constants; fall back to resolving them.
    match = re.search(r"gfx_open\s*\(\s*([A-Za-z_][\w]*)\s*,\s*([A-Za-z_][\w]*)",
                      flow_source)
    if match:
        dims = []
        for name in (match.group(1), match.group(2)):
            const = re.search(r"const\s+%s\s*:\s*i32\s*=\s*(\d+)" % re.escape(name),
                              flow_source)
            dims.append(int(const.group(1)) if const else 0)
        if all(dims):
            return dims[0], dims[1]
    return 800, 600


def key_hints(flow_source: str) -> str:
    """Pull the Controls / KEYS block out of the program's header comment."""
    lines = flow_source.splitlines()
    picked = []
    grabbing = False
    for line in lines[:60]:
        if not line.startswith("#"):
            if grabbing:
                break
            continue
        body = line.lstrip("#").strip()
        low = body.lower()
        if low.startswith("controls") or low.startswith("keys") or \
                low.startswith("parameters / keys"):
            grabbing = True
            continue
        if grabbing:
            if not body:
                break
            picked.append(body)
    if not picked:
        return "Arrows or WASD move, Space acts, P pauses, R restarts, Esc quits."
    return html_escape(" &middot; ".join(picked[:8])).replace("&amp;middot;", "&middot;")


def write_page(out_dir: Path, name: str, title: str, gfx: bool,
               flow_source: str, source_url: str, backend: str = "c",
               extra_html: str = "", threads: bool = False) -> Path:
    if gfx:
        width, height = canvas_size(flow_source)
        body = (GFX_BODY.replace("__W__", str(width))
                        .replace("__H__", str(height))
                        .replace("__TITLE__", html_escape(title))
                        .replace("__KEYS__", key_hints(flow_source)))
        script = GFX_SCRIPT.replace("__NAME__", name)
    elif threads:
        body = THREADS_BODY
        script = THREADS_SCRIPT.replace("__NAME__", name)
    else:
        body = CONSOLE_BODY
        script = CONSOLE_SCRIPT.replace("__NAME__", name)

    pipe = "MLIR &rarr; LLVM &rarr; WebAssembly" if backend == "mlir" else "C &rarr; WebAssembly"
    # The COI service worker must load before anything touches
    # SharedArrayBuffer: it reloads once to put the isolation headers in place.
    coi = '<script src="coi-serviceworker.js"></script>\n' if threads else ""
    kind = "gfx canvas backend" if gfx else ("console &middot; pthreads over SharedArrayBuffer" if threads else "console")
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html_escape(title)} — Flow on WebAssembly</title>
{coi}<style>{PAGE_CSS}</style>
</head>
<body>
<header>
  <h1>{html_escape(title)}</h1>
  <span class="meta">Flow &rarr; {pipe} &middot; {kind}</span>
  <span class="meta"><a href="{html_escape(source_url)}">source</a></span>
</header>
{extra_html}
{body}
{script}
</body>
</html>
"""
    page_path = out_dir / "index.html"
    page_path.write_text(page)
    return page_path


# ---------------------------------------------------------------------------


def build(program: Path, out_dir: Path, name: str = "", title: str = "",
          opt: str = "-O2", timeout: int = 600, keep_c: bool = False,
          backend: str = "c",
          preload: Optional[list[str]] = None,
          extra_link: Optional[list[Path]] = None,
          initial_memory: str = "32MB",
          asyncify_stack_size: int = 32768,
          emcc_flags: Optional[list[str]] = None,
          extra_html: str = "",
          threads: bool = False,
          workers: int = 8) -> dict:
    """Build one program. Returns a result dict; raises BuildError on failure.

    threads=True compiles the program on real pthreads: Flow's parallel-for
    orchestration (lib/runtime/concurrency_parallel.flow) is compiled in as a
    library TU and lands on pthread_create over SharedArrayBuffer, backed by
    the pthread kernel runtime/flow_rt_parallel.c. The page ships a COI service
    worker because the browser only allows SharedArrayBuffer on
    cross-origin-isolated pages.
    """
    program = program.resolve()
    if not program.exists():
        raise BuildError(f"no such file: {program}")
    backend = resolve_backend(backend)
    if threads and backend == "mlir":
        raise BuildError("threads mode requires the C backend")
    name = name or program.stem
    title = title or name.replace("_gfx", "").replace("_", " ")
    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    flow_source = program.read_text()

    if not have_emcc():
        raise BuildError("emcc not on PATH (see docs/language/wasm.md)")

    artifacts: list[Path] = []
    if backend == "mlir":
        ir_file = out_dir / f"{name}.ll"
        ir_text = flow_to_llvm_ir(program, ir_file)
        gfx = uses_gfx(ir_text) or uses_gfx_flow_source(flow_source)
        compile_input = ir_file
        artifacts.append(ir_file)
    else:
        c_file = out_dir / f"{name}.c"
        c_source = flow_to_c(program, c_file)
        c_source = _append_extern_stubs(c_source)
        c_file.write_text(c_source)
        gfx = uses_gfx(c_source)
        compile_input = c_file
        artifacts.append(c_file)
        if threads:
            # Flow's parallel-for chunk orchestration, compiled as a library
            # (it defines flow_parallel_for_i32; the program declares it
            # extern), plus the pthread create/join kernel and the monotonic
            # clock.
            lib_c = out_dir / f"{name}_parallel_lib.c"
            flow_to_c(PROJECT_ROOT / "lib" / "runtime" / "concurrency_parallel.flow",
                      lib_c, library=True)
            artifacts.append(lib_c)
            merged = list(extra_link or [])
            for path in (lib_c,
                         PROJECT_ROOT / "runtime" / "flow_rt_parallel.c",
                         PROJECT_ROOT / "runtime" / "flow_rt_support.c"):
                if path.resolve() not in [p.resolve() for p in merged]:
                    merged.append(path)
            extra_link = merged

    started = time.time()
    out_js = out_dir / f"{name}.js"
    compile_wasm(
        compile_input,
        out_js,
        gfx,
        opt,
        timeout,
        preload=preload,
        extra_link=extra_link,
        initial_memory=initial_memory,
        asyncify_stack_size=asyncify_stack_size,
        emcc_flags=emcc_flags,
        threads=threads,
        workers=workers,
    )
    elapsed = time.time() - started

    if threads:
        # Client-side cross-origin isolation: the service worker injects
        # COOP/COEP and reloads once, so the SAB heap works on static hosts.
        sw = PROJECT_ROOT / "wasm" / "crossing_assets" / "coi-serviceworker.js"
        shutil.copyfile(sw, out_dir / "coi-serviceworker.js")

    try:
        rel = program.relative_to(PROJECT_ROOT)
        source_url = f"https://github.com/flooooooooooow/flow/blob/main/{rel}"
    except ValueError:
        rel = program.name
        source_url = str(program)

    write_page(out_dir, name, title, gfx, flow_source, source_url,
               backend=backend, extra_html=extra_html, threads=threads)
    if not keep_c:
        for artifact in artifacts:
            artifact.unlink(missing_ok=True)

    wasm = out_js.with_suffix(".wasm")
    data = out_js.with_suffix(".data")
    result = {
        "name": name,
        "title": title,
        "source": str(rel),
        "backend": backend,
        "gfx": gfx,
        "wasm_bytes": wasm.stat().st_size,
        "js_bytes": out_js.stat().st_size,
        "seconds": round(elapsed, 1),
        "out": str(out_dir),
        "preload": list(preload or []),
        "link": [str(p) for p in (extra_link or [])],
    }
    if data.exists():
        result["data_bytes"] = data.stat().st_size
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("program", help="path to a .flow program")
    parser.add_argument("--out", default="", help="output directory")
    parser.add_argument("--name", default="", help="module basename")
    parser.add_argument("--title", default="", help="page title")
    parser.add_argument(
        "--backend",
        default=None,
        choices=["c", "mlir"],
        help="CPU codegen: c (default) or mlir (Flow→MLIR→LLVM→emcc). "
             "Also accepts FLOW_CPU_BACKEND.",
    )
    parser.add_argument(
        "--preload",
        action="append",
        default=[],
        metavar="HOST@VFS",
        help="emcc --preload-file mapping (repeatable). Enables FORCE_FILESYSTEM. "
             "Works for both --backend=c and --backend=mlir (#225).",
    )
    parser.add_argument(
        "--link",
        action="append",
        default=[],
        metavar="PATH",
        help="extra C/runtime file to pass to emcc (repeatable). "
             "Cocoa .m/.mm are skipped. Example: runtime/flow_rt_support.c",
    )
    parser.add_argument(
        "--initial-memory",
        default="32MB",
        help="emcc -sINITIAL_MEMORY (default 32MB; doom-scale often 64MB)",
    )
    parser.add_argument(
        "--asyncify-stack-size",
        type=int,
        default=32768,
        help="emcc -sASYNCIFY_STACK_SIZE when gfx is linked (default 32768)",
    )
    parser.add_argument(
        "-O",
        dest="opt",
        default="-O2",
        metavar="LEVEL",
        type=lambda s: s if str(s).startswith("-O") else f"-O{s}",
        help="emcc optimisation level: -O2 (default), or -O -O1 / -O2",
    )
    parser.add_argument(
        "--emcc-flag",
        action="append",
        default=[],
        metavar="FLAG",
        help="extra flag passed through to emcc (repeatable). "
             "Example: --emcc-flag=-DNORMALUNIX",
    )
    parser.add_argument(
        "--threads",
        action="store_true",
        help="build on real pthreads (-pthread over SharedArrayBuffer, "
             "PROXY_TO_PTHREAD). The page ships a COI service worker because "
             "the browser only allows SAB on cross-origin-isolated pages.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=8,
        help="pthread pool size / shard count for --threads (default 8)",
    )
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--keep-c", action="store_true",
                        help="keep the generated C / LLVM IR next to the output")
    parser.add_argument("--json", action="store_true",
                        help="print the result as JSON")
    args = parser.parse_args(argv)

    program = Path(args.program)
    out_dir = Path(args.out) if args.out else \
        PROJECT_ROOT / "build" / "wasm" / program.stem
    extra_link = [Path(p) for p in args.link]

    try:
        backend = resolve_backend(args.backend)
        result = build(
            program,
            out_dir,
            args.name,
            args.title,
            args.opt,
            args.timeout,
            args.keep_c,
            backend=backend,
            preload=args.preload or None,
            extra_link=extra_link or None,
            initial_memory=args.initial_memory,
            asyncify_stack_size=args.asyncify_stack_size,
            emcc_flags=args.emcc_flag or None,
            threads=args.threads,
            workers=args.workers,
        )
    except BuildError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        kind = "gfx canvas" if result["gfx"] else "console"
        print(f"built {result['name']} ({kind}, backend={result['backend']}) "
              f"in {result['seconds']}s")
        print(f"  wasm {result['wasm_bytes'] / 1024:.0f} KB  "
              f"js {result['js_bytes'] / 1024:.0f} KB")
        if result.get("data_bytes"):
            print(f"  data {result['data_bytes'] / 1024:.0f} KB  "
                  f"(preload {', '.join(result['preload'])})")
        if result.get("link"):
            print(f"  link {' '.join(result['link'])}")
        print(f"  page {out_dir / 'index.html'}")
        print(f"  serve: python3 -m http.server -d {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
