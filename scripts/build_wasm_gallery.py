#!/usr/bin/env python3
"""Compile a list of Flow examples to WebAssembly and build the gallery.

Every target becomes ``site/wasm/<name>/`` holding a .wasm, its .js loader and
a standalone HTML page. Alongside them the script writes ``manifest.json``
(what built, how big, what failed and why) and ``index.html``, the gallery that
runs any of them in place.

    python3 scripts/build_wasm_gallery.py                 # everything
    python3 scripts/build_wasm_gallery.py --only snake_gfx gray_scott
    python3 scripts/build_wasm_gallery.py --category games
    python3 scripts/build_wasm_gallery.py --list

Examples that fail are kept in the manifest with their error. The failure list
is part of the output, not a reason to stop.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import re
import shutil
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from wasm_build import PROJECT_ROOT, BuildError, build, have_emcc  # noqa: E402

SITE_WASM = PROJECT_ROOT / "site" / "wasm"

CATEGORIES = [
    {
        "id": "games",
        "title": "Games",
        "blurb": "The same sources docs/demos/games.md records as GIFs, "
                 "running live on the gfx canvas backend.",
        "globs": [("examples/games", "*_gfx.flow")],
    },
    {
        "id": "morphogenesis",
        "title": "Morphogenesis",
        "blurb": "Reaction-diffusion, growth and cellular automata fields. "
                 "Number keys switch presets, R reseeds, P pauses.",
        "globs": [("examples/morphogenesis", "*.flow")],
    },
    {
        "id": "basics",
        "title": "Basics",
        "blurb": "Pure computation. No graphics, no host services: the "
                 "program runs and prints into the page.",
        "globs": [("examples/basics", "*.flow")],
        "files": ["examples/wasm/hello_wasm.flow",
                  "examples/wasm/parallel_scaling.flow",
                  "examples/wasm/parallel_sum.flow"],
    },
    {
        "id": "language",
        "title": "Language and compilers",
        "blurb": "Generics, traits, enums, effect rows, and Flow tools "
                 "written in Flow. Output goes to the page.",
        "globs": [
            ("examples/generics_traits", "*.flow"),
            ("examples/compilers", "*.flow"),
            ("examples/effects", "*.flow"),
        ],
    },
    {
        "id": "numerics",
        "title": "Numerics and dynamics",
        "blurb": "Solvers, optimisers, linear algebra and control theory. "
                 "The ones that reach a native BLAS do not link here.",
        "globs": [
            ("examples/numerical", "*.flow"),
            ("examples/dynamics", "*.flow"),
            ("examples/linalg", "*.flow"),
            ("examples/stats", "*.flow"),
            ("examples/physics", "*.flow"),
        ],
    },
    {
        "id": "learning",
        "title": "Learning",
        "blurb": "Small models and agents. The Metal and tape-runtime "
                 "variants need host services that are not linked here.",
        "globs": [
            ("examples/ml", "*.flow"),
            ("examples/ai", "*.flow"),
        ],
    },
    {
        "id": "systems",
        "title": "Systems and data",
        "blurb": "Allocators, hash tables, hashing, parsers, file formats. "
                 "Anything asking the OS about itself stops at the link step.",
        "globs": [
            ("examples/systems", "*.flow"),
            ("examples/crypto", "*.flow"),
            ("examples/data", "*.flow"),
            ("examples/graphics", "*.flow"),
        ],
    },
]

TINY_POINTERS_COVERAGE_CARD = """
<details class="coverage">
  <summary>Abstract-claim coverage — every promise in the paper's abstract, mapped to the phase that measures it</summary>
  <p class="note">The same map prints at the top of this program's run output.
  Each row links to its section in the docs
  (<a href="../../library/tiny-pointers.md">tiny-pointers.md</a> ·
  <a href="../../library/tiny-pointers-variable-values.md">variable-size values</a>).</p>
  <table>
    <tr><th>Abstract claim</th><th>Row</th></tr>
    <tr><td>Fixed-size pointers of Θ(log log log n + log k) bits</td>
        <td><a href="../../library/tiny-pointers.md#theorem-1-fixed-size-tiny-pointers-3-phases-14">Theorem 1 (Phases 1–4) · §3</a></td></tr>
    <tr><td>Variable-size pointers of Θ(log k) expected bits</td>
        <td><a href="../../library/tiny-pointers.md#theorem-2-variable-size-tiny-pointers-4-phases-56">Theorem 2 (Phases 5–6) · §4</a></td></tr>
    <tr><td>① relaxed retrieval: nv + O(n log⁽ʳ⁾ n), O(1)-expected hints, O(r) insert/delete</td>
        <td><a href="../../library/tiny-pointers.md#theorem-6-relaxed-retrieval-tiny-retrievers-62-phases-78">Theorem 6 (Phases 7–8, 8b) · §6.2</a></td></tr>
    <tr><td>② succinct rotation-based BSTs, rotations included</td>
        <td><a href="../../library/tiny-pointers.md#theorem-7-succinct-rotation-based-bsts-63-phases-910">Theorem 7 (Phases 9–10) · §6.3</a></td></tr>
    <tr><td>③ stable fixed-capacity dicts, 1 + o(1) overhead</td>
        <td><a href="../../library/tiny-pointers.md#theorem-8-stable-dictionaries-64-phases-34">Theorem 8 (Phases 3–4) · §6.4</a></td></tr>
    <tr><td>④ arbitrary-size values at log⁽ʳ⁾ n + O(log j) bits per j-bit value</td>
        <td><a href="../../library/tiny-pointers-variable-values.md#theorem-9-and-the-size-class-construction">Theorem 9 (Phases 11/12/14/15) · §6.5</a></td></tr>
    <tr><td>⑤ optimal internal-memory stash, O(n log ε⁻¹) bits, no IOs</td>
        <td><a href="../../library/tiny-pointers.md#theorem-10-the-optimal-internal-memory-stash-66-phase-16">Theorem 10 (Phase 16) · §6.6</a></td></tr>
  </table>
  <p class="note">Theorems 3–5 are lower bounds / intermediate steps, not constructions.
  Full theorem table: <a href="../../library/tiny-pointers.md">tiny-pointers.md</a>.</p>
</details>
"""

# Per-example extras for the build pipeline. `extra_link` adds C/runtime
# files to the emcc link step (tiny_pointers needs the monotonic clock in
# runtime/flow_rt_support.c, which the plain console build does not link);
# `html` injects an HTML fragment between the page header and the run body.
PAGE_EXTRAS = {
    # Examples that call flow_rt_monotonic_ns link the real runtime file
    # (host monotonic clock) instead of a stub.
    "tiny_pointers": {
        "extra_link": ["runtime/flow_rt_support.c"],
        "html": TINY_POINTERS_COVERAGE_CARD,
    },
    "digits_mlp": {"extra_link": ["runtime/flow_rt_support.c"]},
    # Real pthreads: wasm_build compiles the parallel-for library TU and links
    # runtime/flow_rt_parallel.c + flow_rt_support.c itself (threads mode).
    # The browser blocks SharedArrayBuffer without cross-origin isolation, so
    # the page ships a COI service worker and needs to be opened in a tab.
    "digits_mlp_parallel": {"threads": True, "workers": 8, "initial_memory": "128MB"},
    "parallel_sum": {"threads": True, "workers": 8},
    "parallel_scaling": {"threads": True, "workers": 8},
    # The reverse-mode AD tape lives in lib/runtime/tape.flow (pure Flow,
    # replaces the deleted runtime/flow_tape.c). The native launcher links all
    # lib/runtime modules; the wasm build opts in per example.
    "tape_mul": {"extra_flow_runtime": ["lib/runtime/tape.flow"]},
    # stdlib/blas.flow externs are Accelerate/OpenBLAS-backed natively; the
    # wasm pages get runtime/blas_wasm.c, a plain correct shim for the exact
    # routines these examples call (daxpy/dcopy/ddot/dnrm2/dscal/dgemv/dgemm
    # + dgesv_).
    "blas_demo": {"extra_c": ["runtime/blas_wasm.c"]},
    "lu_decomposition": {"extra_c": ["runtime/blas_wasm.c"]},
}


def pretty_title(stem: str) -> str:
    name = stem.replace("_gfx", "").replace("_", " ").strip()
    special = {
        "2048": "2048", "lightsout": "Lights Out", "connect4": "Connect Four",
        "maze chase": "Maze Chase", "lane racer": "Lane Racer",
        "missile": "Missile Command", "invaders": "Space Invaders",
        "hanoi": "Tower of Hanoi", "match3": "Match-3", "dla": "DLA",
        "wfc growth": "WFC Growth", "lsystem plant": "L-System Plant",
        "lsystem tree": "L-System Tree", "cyclic ca": "Cyclic CA",
        "hexagonal ca": "Hexagonal CA", "gcd": "GCD",
        "hello wasm": "Hello WASM", "blas demo": "BLAS Demo",
        "lu decomposition": "LU Decomposition",
        "lu decomposition pedagogical": "LU Decomposition (pedagogical)",
        "digits mlp": "Digits MLP", "digits mlp metal": "Digits MLP (Metal)",
        "digits mlp parallel": "Digits MLP (parallel)",
        "ga flappy": "GA Flappy", "ga control": "GA Control",
        "ga dsys namespaced": "GA Dsys (namespaced)",
        "ga dsys syntax": "GA Dsys Syntax",
        "ga full analysis": "GA Full Analysis",
        "ga wfc coupled": "GA + WFC Coupled",
        "q snake": "Q-Snake", "wfc demo": "WFC Demo",
        "nn layers": "NN Layers", "mlir tensor bench": "MLIR Tensor Bench",
        "sha256": "SHA-256", "runtime sha256": "Runtime SHA-256",
        "csv parser": "CSV Parser", "gif writer": "GIF Writer",
        "lsp ordering port": "LSP Ordering Port",
        "oop counter": "OOP Counter", "oop person": "OOP Person",
        "flowlm charlm": "FlowLM Char-LM",
        "ode solver": "ODE Solver", "regression gd": "Regression (GD)",
    }
    if name in special:
        return special[name]
    return " ".join(word.capitalize() for word in name.split())


def one_line_summary(source: str) -> str:
    """First substantive line of the program's header comment."""
    for line in source.splitlines()[:40]:
        if not line.startswith("#"):
            break
        body = line.lstrip("#").strip()
        if not body:
            continue
        if body.lower().startswith(("run:", "controls", "build", "usage")):
            continue
        body = re.sub(r"^[A-Z0-9 \-]+:\s*", "", body, count=1)
        if len(body) > 12:
            return body.rstrip(".")
    return ""


def collect(categories) -> list:
    targets = []
    for cat in categories:
        paths = []
        for folder, pattern in cat.get("globs", []):
            paths += sorted((PROJECT_ROOT / folder).glob(pattern))
        for name in cat.get("files", []):
            path = PROJECT_ROOT / name
            if path.exists():
                paths.append(path)
        for path in paths:
            targets.append({
                "path": path,
                "name": path.stem,
                "category": cat["id"],
                "title": pretty_title(path.stem),
            })
    return targets


def build_one(target: dict, out_root: Path, opt: str, timeout: int) -> dict:
    extras = PAGE_EXTRAS.get(target["name"], {})
    record = {
        "name": target["name"],
        "title": target["title"],
        "category": target["category"],
        "source": str(target["path"].relative_to(PROJECT_ROOT)),
        "summary": one_line_summary(target["path"].read_text()),
    }
    if extras.get("threads"):
        record["threads"] = True
    out_dir = out_root / target["name"]
    try:
        result = build(target["path"], out_dir, name=target["name"],
                       title=target["title"], opt=opt, timeout=timeout,
                       extra_link=[PROJECT_ROOT / p for p in extras.get("extra_link", [])]
                       or None,
                       extra_html=extras.get("html", ""),
                       extra_c=extras.get("extra_c", ()),
                       extra_flow_runtime=extras.get("extra_flow_runtime", ()),
                       threads=extras.get("threads", False),
                       workers=extras.get("workers", 8),
                       initial_memory=extras.get("initial_memory", "32MB"))
    except BuildError as exc:
        shutil.rmtree(out_dir, ignore_errors=True)
        record.update(status="failed", error=str(exc))
        return record
    # Build times deliberately stay out of the manifest so a rebuild produces
    # a byte-identical file.
    record.update(
        status="ok",
        gfx=result["gfx"],
        wasm_bytes=result["wasm_bytes"],
        js_bytes=result["js_bytes"],
        total_bytes=result["wasm_bytes"] + result["js_bytes"],
        page=f"{target['name']}/index.html",
    )
    return record


# ---------------------------------------------------------------------------
# Gallery page
# ---------------------------------------------------------------------------

GALLERY_CSS = """
:root { color-scheme: dark; }
* { box-sizing: border-box; }
body {
  margin: 0; background: #0c0d11; color: #d8dae4;
  font: 15px/1.6 ui-sans-serif, -apple-system, "Segoe UI", sans-serif;
}
.wrap { max-width: 1080px; margin: 0 auto; padding: 40px 20px 80px; }
h1 { font-size: 26px; margin: 0 0 6px; font-weight: 650; letter-spacing: -.01em; }
.lede { color: #8a8fa3; max-width: 62ch; margin: 0 0 6px; }
.lede a { color: #7aa2f7; }
h2 { font-size: 17px; margin: 44px 0 4px; font-weight: 620; }
h2 .count { color: #575c6e; font-weight: 400; font-size: 13px; }
.blurb { color: #8a8fa3; font-size: 13.5px; margin: 0 0 16px; max-width: 66ch; }
.grid {
  display: grid; gap: 12px;
  grid-template-columns: repeat(auto-fill, minmax(232px, 1fr));
}
.card {
  border: 1px solid #1e2029; border-radius: 8px; background: #101219;
  padding: 13px 14px; display: flex; flex-direction: column; gap: 7px;
}
.card h3 { margin: 0; font-size: 14.5px; font-weight: 600; }
.card p { margin: 0; font-size: 12.5px; color: #7e8397; line-height: 1.5;
          flex: 1; }
.card .row { display: flex; align-items: center; gap: 9px; font-size: 12px;
             color: #575c6e; }
.card button {
  font: inherit; font-size: 13px; font-weight: 600; border: 0;
  border-radius: 5px; padding: 5px 14px; cursor: pointer;
  background: #7aa2f7; color: #0c0d11;
}
.card button:hover { background: #93b5ff; }
.card a { color: #6b7ca8; text-decoration: none; font-size: 12px; }
.card a:hover { color: #7aa2f7; text-decoration: underline; }
.card.failed { opacity: .72; border-style: dashed; }
.card.failed .why { color: #d08770; font-size: 11.5px;
  font-family: ui-monospace, Menlo, monospace; word-break: break-word; }
.tag { font-size: 10.5px; letter-spacing: .04em; text-transform: uppercase;
       color: #575c6e; border: 1px solid #232631; border-radius: 3px;
       padding: 1px 5px; }
table.status { border-collapse: collapse; width: 100%; margin-top: 12px;
               font-size: 13.5px; }
table.status th, table.status td {
  text-align: left; padding: 7px 10px; border-bottom: 1px solid #1a1c24;
  vertical-align: top;
}
table.status th { color: #8a8fa3; font-weight: 600; }
.state { font-weight: 600; white-space: nowrap; }
.state.runs { color: #9ece6a; }
.state.wip { color: #e0af68; }
.state.none { color: #6d7183; }
#modal {
  position: fixed; inset: 0; background: rgba(6,7,10,.9); display: none;
  align-items: center; justify-content: center; flex-direction: column;
  gap: 10px; padding: 20px; z-index: 50;
}
#modal.open { display: flex; }
#modal iframe {
  width: min(1000px, 96vw); height: min(720px, 82vh); border: 1px solid #232631;
  border-radius: 8px; background: #0c0d11;
}
#modal .bar { display: flex; gap: 12px; align-items: center; color: #8a8fa3;
              font-size: 13px; }
#modal button { font: inherit; background: #232631; color: #d8dae4; border: 0;
                border-radius: 5px; padding: 5px 14px; cursor: pointer; }
#modal button:hover { background: #2e3240; }
footer { margin-top: 56px; color: #575c6e; font-size: 13px;
         border-top: 1px solid #1a1c24; padding-top: 16px; }
footer a { color: #6b7ca8; }
"""

GALLERY_JS = """
(function () {
  var modal = document.getElementById('modal');
  var frame = document.getElementById('frame');
  var label = document.getElementById('label');
  var link = document.getElementById('open');

  function run(page, title) {
    label.textContent = title;
    link.href = page;
    frame.src = page + '?autostart=1';
    modal.classList.add('open');
    setTimeout(function () { frame.focus(); }, 60);
  }
  function close() {
    modal.classList.remove('open');
    frame.src = 'about:blank';
  }
  document.addEventListener('click', function (ev) {
    var btn = ev.target.closest('[data-run]');
    if (btn) { run(btn.getAttribute('data-run'), btn.getAttribute('data-title')); }
    if (ev.target.id === 'close' || ev.target === modal) { close(); }
  });
  document.addEventListener('keydown', function (ev) {
    if (ev.key === 'Escape' && modal.classList.contains('open')) { close(); }
  });
})();
"""

STATUS_ROWS = [
    ("Pure computation", "runs", "Runs today",
     "Arithmetic, arrays, structs, strings, printf. Straight Flow to C to "
     "wasm32 with nothing else linked in."),
    ("gfx graphics and keyboard", "runs", "Runs today",
     "runtime/gfx_wasm.c paints the framebuffer onto a canvas and maps DOM "
     "key events to the macOS keycodes the programs already use."),
    ("Threads and channels", "runs", "Runs today",
     "digits_mlp_parallel and parallel_sum run on real Emscripten pthreads over "
     "SharedArrayBuffer and Web Workers. SharedArrayBuffer needs a "
     "cross-origin-isolated page, so open those cards in a tab and let their "
     "service worker reload once."),
    ("Sockets and HTTP", "wip", "In progress",
     "Emscripten's WebSocket-backed POSIX socket bridge "
     "(-lwebsocket.js / PROXY_POSIX_SOCKETS). Not built here."),
    ("GPU kernels", "wip", "In progress",
     "WebGPU, with WGSL generated from the same @gpu AST that already emits "
     "Metal. Not built here."),
    ("Embedded CPython", "wip", "In progress",
     "Pyodide, which is CPython itself compiled to WebAssembly. "
     "Not built here."),
    ("File I/O", "wip", "In progress",
     "Emscripten's MEMFS and IDBFS filesystems. Not wired into these pages."),
    ("Audio", "none", "Not attempted",
     "The miniaudio and Metal audio backends have no browser counterpart "
     "here yet; WebAudio would be the route."),
]


def esc(text: str) -> str:
    return (str(text).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def kb(n: int) -> str:
    return f"{n / 1024:.0f} KB" if n < 1024 * 1024 else f"{n / 1048576:.1f} MB"


def render_gallery(records: list, out: Path) -> None:
    by_cat = {}
    for rec in records:
        by_cat.setdefault(rec["category"], []).append(rec)

    sections = []
    for cat in CATEGORIES:
        rows = by_cat.get(cat["id"], [])
        if not rows:
            continue
        ok = [r for r in rows if r["status"] == "ok"]
        cards = []
        for rec in sorted(rows, key=lambda r: (r["status"] != "ok", r["title"])):
            src = ("https://github.com/flooooooooooow/flow/blob/main/"
                   + rec["source"])
            if rec["status"] == "ok":
                kind = "canvas" if rec.get("gfx") else "console"
                tags = f'<span class="tag">{kind}</span>'
                if rec.get("threads"):
                    tags += ' <span class="tag">threads</span>'
                cards.append(f"""      <div class="card">
        <h3>{esc(rec['title'])}</h3>
        <p>{esc(rec['summary'])}</p>
        <div class="row">
          <button data-run="{esc(rec['page'])}" data-title="{esc(rec['title'])}">Run</button>
          {tags}
          <span>{kb(rec['total_bytes'])}</span>
          <a href="{esc(src)}">source</a>
        </div>
      </div>""")
            else:
                cards.append(f"""      <div class="card failed">
        <h3>{esc(rec['title'])}</h3>
        <p>{esc(rec['summary'])}</p>
        <div class="why">does not build: {esc(rec['error'])}</div>
        <div class="row"><a href="{esc(src)}">source</a></div>
      </div>""")
        sections.append(f"""    <h2>{esc(cat['title'])}
      <span class="count">{len(ok)} of {len(rows)} running</span></h2>
    <p class="blurb">{esc(cat['blurb'])}</p>
    <div class="grid">
{chr(10).join(cards)}
    </div>""")

    status = "\n".join(
        f"""      <tr><td>{esc(name)}</td>
        <td class="state {cls}">{esc(state)}</td>
        <td>{esc(note)}</td></tr>"""
        for name, cls, state, note in STATUS_ROWS)

    total_ok = sum(1 for r in records if r["status"] == "ok")
    total_bytes = sum(r.get("total_bytes", 0) for r in records
                      if r["status"] == "ok")

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Flow in the browser — WebAssembly gallery</title>
<style>{GALLERY_CSS}</style>
</head>
<body>
<div class="wrap">
  <h1>Flow in the browser</h1>
  <p class="lede">{total_ok} Flow examples compiled to WebAssembly and running
  live on this page. Each one is the unedited source from the repository, put
  through Flow &rarr; C &rarr; <code>emcc</code>. Graphics programs link
  <code>runtime/gfx_wasm.c</code>, a canvas backend for the same gfx API that
  drives the native window and the headless GIF recorder, so nothing in the
  games or the field simulations had to change.</p>
  <p class="lede">Click Run, then click inside the frame so it takes the
  keyboard. Esc closes the frame.</p>

{chr(10).join(sections)}

  <h2>What runs, and what is still being crossed</h2>
  <p class="blurb">Rows marked “runs” are verified in a browser. The
  threads row needs the card opened in a tab (an iframe cannot become
  cross-origin isolated on its own). The rest name the mechanism and say
  plainly that it is not built here yet.</p>
  <table class="status">
    <tr><th>Capability</th><th>State</th><th>Route</th></tr>
{status}
  </table>

  <footer>
    Built by <code>python3 scripts/build_wasm_gallery.py</code>.
    Total payload {kb(total_bytes)} across {total_ok} examples.
    Machine-readable index: <a href="manifest.json">manifest.json</a>.
  </footer>
</div>

<div id="modal">
  <div class="bar">
    <strong id="label"></strong>
    <a id="open" href="#" target="_blank" style="color:#6b7ca8">open in a tab</a>
    <button id="close">Close</button>
  </div>
  <iframe id="frame" src="about:blank" title="Flow example"></iframe>
</div>

<script>{GALLERY_JS}</script>
</body>
</html>
"""
    out.write_text(page)


# ---------------------------------------------------------------------------


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", default=str(SITE_WASM),
                        help="output root (default site/wasm)")
    parser.add_argument("--category", action="append", default=[],
                        help="restrict to a category id")
    parser.add_argument("--only", nargs="*", default=[],
                        help="restrict to these example names")
    parser.add_argument("--list", action="store_true",
                        help="print the target list and exit")
    parser.add_argument("-j", "--jobs", type=int, default=4)
    parser.add_argument("-O", dest="opt", default="-O2")
    parser.add_argument("--timeout", type=int, default=600)
    args = parser.parse_args(argv)

    categories = [c for c in CATEGORIES
                  if not args.category or c["id"] in args.category]
    targets = collect(categories)
    if args.only:
        wanted = set(args.only)
        targets = [t for t in targets if t["name"] in wanted]

    if args.list:
        for target in targets:
            print(f"{target['category']:>14}  {target['name']}")
        print(f"{len(targets)} targets")
        return 0

    if not targets:
        print("no targets matched", file=sys.stderr)
        return 1
    if not have_emcc():
        print("error: emcc not on PATH (see docs/language/wasm.md)",
              file=sys.stderr)
        return 1

    out_root = Path(args.out).resolve()
    out_root.mkdir(parents=True, exist_ok=True)

    print(f"building {len(targets)} examples into {out_root}")
    started = time.time()
    records = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = {pool.submit(build_one, t, out_root, args.opt, args.timeout): t
                   for t in targets}
        for future in concurrent.futures.as_completed(futures):
            rec = future.result()
            records.append(rec)
            if rec["status"] == "ok":
                print(f"  ok    {rec['name']:<24} {kb(rec['total_bytes']):>8}")
            else:
                print(f"  FAIL  {rec['name']:<24} {rec['error']}")

    order = {c["id"]: i for i, c in enumerate(CATEGORIES)}
    records.sort(key=lambda r: (order.get(r["category"], 99), r["name"]))

    # Drop stale directories from earlier runs so the gallery matches the
    # manifest exactly.
    live = {r["name"] for r in records if r["status"] == "ok"}
    if not args.only and not args.category:
        for child in out_root.iterdir():
            if child.is_dir() and child.name not in live:
                shutil.rmtree(child, ignore_errors=True)

    ok = [r for r in records if r["status"] == "ok"]
    manifest = {
        "generated_by": "scripts/build_wasm_gallery.py",
        "examples": len(records),
        "built": len(ok),
        "failed": len(records) - len(ok),
        "total_bytes": sum(r["total_bytes"] for r in ok),
        "categories": [{"id": c["id"], "title": c["title"],
                        "blurb": c["blurb"]} for c in CATEGORIES],
        "entries": records,
    }
    (out_root / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    render_gallery(records, out_root / "index.html")

    print(f"\n{len(ok)} built, {len(records) - len(ok)} failed "
          f"in {time.time() - started:.0f}s")
    print(f"  gallery  {out_root / 'index.html'}")
    print(f"  manifest {out_root / 'manifest.json'}")
    print(f"  serve    python3 -m http.server -d {out_root.parent}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
