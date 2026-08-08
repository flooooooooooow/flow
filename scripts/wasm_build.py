#!/usr/bin/env python3
"""Compile one Flow program to a runnable WebAssembly page.

Pipeline: Flow -> C (flow.transpiler) -> WebAssembly (emcc) -> an HTML host.

Two shapes come out the other end.

Graphics programs (anything that reaches ``lib/stdlib/gfx.flow``) are linked
against ``runtime/gfx_wasm.c``, the browser backend of the gfx API. The page
gets a canvas, keyboard wiring that speaks the same macOS keycodes the games
use, and a click-to-start overlay because browsers want a gesture first.

Everything else is a console program. The page runs ``main`` on click and
streams stdout into a ``<pre>``.

Usage:
    python3 scripts/wasm_build.py examples/games/snake_gfx.flow --out site/wasm/snake
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

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
    return shutil.which("emcc") is not None


def flow_to_c(program: Path, c_out: Path) -> str:
    """Transpile a Flow program to C. Returns the generated C source."""
    c_out.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        [sys.executable, "-m", TRANSPILER, str(program), "--c", "--lenient",
         "-o", str(c_out)],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0 or not c_out.exists():
        detail = (proc.stderr or proc.stdout or "").strip().splitlines()
        raise BuildError("flow->c: " + (detail[-1] if detail else "transpiler failed"))
    return c_out.read_text()


def uses_gfx(c_source: str) -> bool:
    return "flow_gfx_init" in c_source


def emcc_command(c_file: Path, out_js: Path, gfx: bool, opt: str,
                  extra_c: tuple = ()) -> list:
    cmd = [
        "emcc", str(c_file),
        *[str(c) for c in extra_c],
        opt,
        "-o", str(out_js),
        "-sENVIRONMENT=web",
        "-sALLOW_MEMORY_GROWTH=1",
        # Flow puts fixed-size arrays on the stack, and a field simulation
        # holds several 128x128 grids of doubles at once. wasm32 defaults to a
        # 64 KB stack, which those overrun instantly.
        "-sSTACK_SIZE=16MB",
        "-sINITIAL_MEMORY=32MB",
        "-sMODULARIZE=1",
        "-sEXPORT_NAME=createFlowModule",
        "-sINVOKE_RUN=0",
        "-sEXIT_RUNTIME=0",
        "-sEXPORTED_RUNTIME_METHODS=callMain,ccall",
        "-sEXPORTED_FUNCTIONS=_main,_malloc,_free",
        "-Wno-implicit-function-declaration",
        "-lm",
    ]
    if gfx:
        # ASYNCIFY lets flow_gfx_present hand the event loop back to the
        # browser from inside the Flow program's own while-loop.
        cmd.insert(3, "-sASYNCIFY=1")
        cmd.insert(4, "-sASYNCIFY_STACK_SIZE=32768")
        cmd.insert(2, str(PROJECT_ROOT / "runtime" / "gfx_wasm.c"))
    return cmd


def compile_wasm(c_file: Path, out_js: Path, gfx: bool, opt: str,
                 timeout: int, extra_c: tuple = ()) -> None:
    out_js.parent.mkdir(parents=True, exist_ok=True)
    cmd = emcc_command(c_file, out_js, gfx, opt, extra_c=extra_c)
    try:
        proc = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True,
                              text=True, env=emcc_env(), timeout=timeout)
    except subprocess.TimeoutExpired:
        raise BuildError(f"emcc: timed out after {timeout}s")
    if proc.returncode != 0:
        raise BuildError("emcc: " + first_error(proc.stderr or proc.stdout))
    if not out_js.with_suffix(".wasm").exists():
        raise BuildError("emcc: no .wasm emitted")


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
               flow_source: str, source_url: str, extra_html: str = "") -> Path:
    if gfx:
        width, height = canvas_size(flow_source)
        body = (GFX_BODY.replace("__W__", str(width))
                        .replace("__H__", str(height))
                        .replace("__TITLE__", html_escape(title))
                        .replace("__KEYS__", key_hints(flow_source)))
        script = GFX_SCRIPT.replace("__NAME__", name)
    else:
        body = CONSOLE_BODY
        script = CONSOLE_SCRIPT.replace("__NAME__", name)

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html_escape(title)} — Flow on WebAssembly</title>
<style>{PAGE_CSS}</style>
</head>
<body>
<header>
  <h1>{html_escape(title)}</h1>
  <span class="meta">Flow &rarr; C &rarr; WebAssembly{' &middot; gfx canvas backend' if gfx else ' &middot; console'}</span>
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
          extra_c: tuple = (), extra_html: str = "") -> dict:
    """Build one program. Returns a result dict; raises BuildError on failure.

    ``extra_c`` is a tuple of extra C files to link (e.g. the runtime support
    file that provides ``flow_rt_monotonic_ns``); ``extra_html`` is an HTML
    fragment injected into the host page between the header and the body
    (used for per-example notes like the tiny-pointers coverage card).
    """
    program = program.resolve()
    if not program.exists():
        raise BuildError(f"no such file: {program}")
    name = name or program.stem
    title = title or name.replace("_gfx", "").replace("_", " ")
    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    flow_source = program.read_text()
    c_file = out_dir / f"{name}.c"
    c_source = flow_to_c(program, c_file)
    gfx = uses_gfx(c_source)

    if not have_emcc():
        raise BuildError("emcc not on PATH (see docs/language/wasm.md)")

    # Resolve relative extra C files against the repo root, matching how the
    # gfx backend is passed as an absolute path.
    resolved_extra = tuple(
        c if Path(c).is_absolute() else PROJECT_ROOT / c for c in extra_c
    )

    started = time.time()
    out_js = out_dir / f"{name}.js"
    compile_wasm(c_file, out_js, gfx, opt, timeout, extra_c=resolved_extra)
    elapsed = time.time() - started

    try:
        rel = program.relative_to(PROJECT_ROOT)
        source_url = f"https://github.com/flooooooooooow/flow/blob/main/{rel}"
    except ValueError:
        rel = program.name
        source_url = str(program)

    write_page(out_dir, name, title, gfx, flow_source, source_url,
               extra_html=extra_html)
    if not keep_c:
        c_file.unlink(missing_ok=True)

    wasm = out_js.with_suffix(".wasm")
    return {
        "name": name,
        "title": title,
        "source": str(rel),
        "gfx": gfx,
        "wasm_bytes": wasm.stat().st_size,
        "js_bytes": out_js.stat().st_size,
        "seconds": round(elapsed, 1),
        "out": str(out_dir),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("program", help="path to a .flow program")
    parser.add_argument("--out", default="", help="output directory")
    parser.add_argument("--name", default="", help="module basename")
    parser.add_argument("--title", default="", help="page title")
    parser.add_argument("-O", dest="opt", default="-O2",
                        help="emcc optimisation flag (default -O2)")
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--keep-c", action="store_true",
                        help="keep the generated C next to the output")
    parser.add_argument("--json", action="store_true",
                        help="print the result as JSON")
    args = parser.parse_args(argv)

    program = Path(args.program)
    out_dir = Path(args.out) if args.out else \
        PROJECT_ROOT / "build" / "wasm" / program.stem

    try:
        result = build(program, out_dir, args.name, args.title, args.opt,
                       args.timeout, args.keep_c)
    except BuildError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        kind = "gfx canvas" if result["gfx"] else "console"
        print(f"built {result['name']} ({kind}) in {result['seconds']}s")
        print(f"  wasm {result['wasm_bytes'] / 1024:.0f} KB  "
              f"js {result['js_bytes'] / 1024:.0f} KB")
        print(f"  page {out_dir / 'index.html'}")
        print(f"  serve: python3 -m http.server -d {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
