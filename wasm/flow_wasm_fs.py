#!/usr/bin/env python3
"""Crossing 5: Flow programs doing file I/O inside a browser tab.

`fopen`, `fread`, `fwrite`, `fclose`, `mkdir`. Emscripten answers all of them
out of a virtual filesystem, so a Flow program that writes a file writes a
file. Three backends matter here:

  MEMFS    the default. A filesystem in the module's heap. Fast, scratch-only,
           gone when the page unloads.
  IDBFS    a MEMFS image backed by IndexedDB. Survives a reload, but only
           where the host calls FS.syncfs in both directions.
  preload  emcc --preload-file packs a host directory into a .data blob that
           the loader unpacks into MEMFS before main() runs.

Builds three demos into site/wasm-crossings/fs/:

  gif      examples/graphics/gif_writer.flow, unmodified, writing a real
           animated GIF89a byte by byte in Flow. The page reads the bytes back
           out of MEMFS and puts them in an <img>.
  counter  examples/wasm/fs_counter.flow on an IDBFS mount, incrementing a
           number that survives reloads.
  preload  examples/wasm/fs_preload.flow reading a file that was never
           fetched by the program.

Usage:
    python3 wasm/flow_wasm_fs.py [program.flow] [--fs memfs|idbfs]
                                 [--preload DIR@/mount] [--read PATH]
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

# Mount point used for the IDBFS build. The Flow side just writes to
# "persist/...", so this has to match.
IDBFS_MOUNT = "/persist"

# sha256 of build/gif_demo.gif from a native clang build of
# examples/graphics/gif_writer.flow. The page compares the file the WASM build
# writes against it, so any drift in the encoder shows up as a mismatch.
NATIVE_GIF_SHA256 = "9bbb1327b8f74b69dd87e50f65adafe7da7d2eaca963c646604ab2596844f59b"


def build_module(
    program: Path,
    out_dir: Path,
    export_name: str,
    fs: str = "memfs",
    preload: list | None = None,
    extra_flow_sources: list | None = None,
) -> str:
    """Compile one Flow program to a filesystem-enabled WASM module."""
    stem = program.stem
    work = BUILD_DIR / "fs"
    work.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    c_sources = [flow_to_c(program, work / f"{stem}.c")]
    for extra in extra_flow_sources or []:
        c_sources.append(flow_to_c(extra, work / f"{extra.stem}.c", library=True))

    # IDBFS lives inside the module closure, so the page can only mount it if
    # it is exported alongside FS.
    runtime_methods = ["FS", "callMain", "addRunDependency", "removeRunDependency"]
    if fs == "idbfs":
        runtime_methods.append("IDBFS")

    cmd = [
        require_emcc(),
        "-O2",
        "-Wno-everything",
        *[str(s) for s in c_sources],
        "-sMODULARIZE=1",
        f"-sEXPORT_NAME={export_name}",
        "-sALLOW_MEMORY_GROWTH=1",
        # Keep the filesystem even when the linker cannot see a use for it,
        # and hand the page the pieces it needs to mount and sync.
        "-sFORCE_FILESYSTEM=1",
        "-sEXPORTED_RUNTIME_METHODS=" + json.dumps(runtime_methods),
        # The page drives main() itself so it can sync IDBFS in before the run
        # and out after it, and read files afterwards.
        "-sINVOKE_RUN=0",
        "-sEXIT_RUNTIME=0",
        "-sENVIRONMENT=web",
    ]
    if fs == "idbfs":
        cmd.append("-lidbfs.js")
    for spec in preload or []:
        cmd += ["--preload-file", spec]
    cmd += ["-o", str(out_dir / f"{stem}.js")]

    run(cmd, env=emscripten_env())
    return stem


def page_html(demos: dict) -> str:
    def src(path: Path, limit: int = 100000) -> str:
        return html.escape(path.read_text()[:limit])

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Flow crossing 5: files in WebAssembly</title>
<link rel="stylesheet" href="crossing.css">
</head>
<body>
<main>
<h1>Crossing 5 &mdash; the filesystem</h1>
<p class="lede">
Three Flow programs calling <code>fopen</code>, <code>fread</code>,
<code>fwrite</code> and <code>mkdir</code>. Emscripten answers all of it out of
a virtual filesystem, so the first one below writes a real animated GIF byte by
byte in Flow, and the page reads those bytes back out and shows them.
</p>

<div class="facts">
  <div class="fact"><span class="k">MEMFS</span><span class="v" id="f-memfs">&hellip;</span></div>
  <div class="fact"><span class="k">IDBFS</span><span class="v" id="f-idbfs">&hellip;</span></div>
  <div class="fact"><span class="k">preloaded data</span><span class="v" id="f-preload">&hellip;</span></div>
  <div class="fact"><span class="k">runs recorded</span><span class="v" id="f-runs">&mdash;</span></div>
</div>

<h2>1. Flow writes a GIF into MEMFS, the browser renders it</h2>
<div class="panel">
  <button id="run-gif">Write build/gif_demo.gif</button>
  <span id="gif-note"></span>
  <div style="margin-top:1rem;display:flex;gap:1.5rem;align-items:flex-start;flex-wrap:wrap">
    <img id="gif-img" alt="GIF written by Flow inside WASM"
         style="image-rendering:pixelated;width:256px;height:256px;border:1px solid var(--line);border-radius:8px;background:#06080d">
    <div>
      <table>
        <tbody>
          <tr><th>path in MEMFS</th><td id="g-path">&mdash;</td></tr>
          <tr><th>bytes written</th><td id="g-size">&mdash;</td></tr>
          <tr><th>header</th><td id="g-magic">&mdash;</td></tr>
          <tr><th>frames encoded</th><td id="g-frames">&mdash;</td></tr>
          <tr><th>sha256</th><td id="g-sha" style="font:11px ui-monospace,monospace;word-break:break-all">&mdash;</td></tr>
          <tr><th>matches native build</th><td id="g-same">&mdash;</td></tr>
          <tr><th>result</th><td id="g-res">&mdash;</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</div>

<h2>2. IDBFS: a counter that survives a reload</h2>
<div class="panel">
  <button id="run-counter">Run once</button>
  <button id="reload" class="secondary">Reload the page</button>
  <button id="wipe" class="secondary">Wipe stored state</button>
  <table style="margin-top:0.8rem">
    <tbody>
      <tr><th>mount</th><td>{IDBFS_MOUNT} (IDBFS over IndexedDB)</td></tr>
      <tr><th>count before</th><td id="c-before">&mdash;</td></tr>
      <tr><th>count after</th><td id="c-after">&mdash;</td></tr>
      <tr><th>syncfs in / out</th><td id="c-sync">&mdash;</td></tr>
      <tr><th>result</th><td id="c-res">&mdash;</td></tr>
    </tbody>
  </table>
</div>

<h2>3. --preload-file: an input file the program never fetched</h2>
<div class="panel">
  <button id="run-preload">Read data/fs_input.txt</button>
  <table style="margin-top:0.8rem">
    <tbody>
      <tr><th>bytes</th><td id="p-bytes">&mdash;</td></tr>
      <tr><th>lines</th><td id="p-lines">&mdash;</td></tr>
      <tr><th>checksum</th><td id="p-sum">&mdash;</td></tr>
      <tr><th>native run</th><td>bytes 291, lines 5</td></tr>
      <tr><th>result</th><td id="p-res">&mdash;</td></tr>
    </tbody>
  </table>
</div>

<h2>Log</h2>
<pre id="out">click a button</pre>

<h2>Flow source: the GIF writer</h2>
<pre class="source">{src(PROJECT_ROOT / "examples" / "graphics" / "gif_writer.flow")}</pre>

<h2>Flow source: the IDBFS counter</h2>
<pre class="source">{src(PROJECT_ROOT / "examples" / "wasm" / "fs_counter.flow")}</pre>

<footer>
Built by <code>wasm/flow_wasm_fs.py</code>. Mechanism:
<code>docs/language/wasm-crossings.md</code>.
</footer>
</main>

<script src="{demos['gif']}.js"></script>
<script src="{demos['counter']}.js"></script>
<script src="{demos['preload']}.js"></script>
<script>
const out = document.getElementById("out");
const log = (s) => {{ out.textContent += s + "\\n"; out.scrollTop = out.scrollHeight; }};
const setFact = (id, text, cls) => {{
  const el = document.getElementById(id);
  el.textContent = text;
  el.className = "v" + (cls ? " " + cls : "");
}};
const setRes = (id, ok, text) => {{
  const el = document.getElementById(id);
  el.textContent = text;
  el.style.color = ok ? "var(--ok)" : "var(--bad)";
}};

// Instantiate a module without running main, so the page can mount, sync and
// read around the program.
function load(factory, opts) {{
  return factory(Object.assign({{
    print: (s) => log(s),
    printErr: (s) => log("stderr: " + s),
    noInitialRun: true,
  }}, opts || {{}}));
}}

// Walk the GIF89a block structure so the frame count is the real one rather
// than a count of 0x2C bytes, which also occur inside compressed data.
function parseGif(b) {{
  const width = b[6] | (b[7] << 8);
  const height = b[8] | (b[9] << 8);
  let p = 13;
  if (b[10] & 0x80) p += 3 * (1 << ((b[10] & 0x07) + 1));   // global colour table
  const skipSubBlocks = () => {{
    while (p < b.length && b[p] !== 0) p += b[p] + 1;
    p++;
  }};
  let frames = 0;
  let trailer = false;
  while (p < b.length) {{
    const tag = b[p++];
    if (tag === 0x3b) {{ trailer = true; break; }}          // end of file
    if (tag === 0x21) {{ p++; skipSubBlocks(); continue; }}  // extension
    if (tag === 0x2c) {{                                     // image descriptor
      const packed = b[p + 8];
      p += 9;
      if (packed & 0x80) p += 3 * (1 << ((packed & 0x07) + 1)); // local table
      p++;                                                   // LZW min code size
      skipSubBlocks();
      frames++;
      continue;
    }}
    break;                                                   // unexpected byte
  }}
  return {{ width, height, frames, trailer }};
}}

// ---- 1. MEMFS + the GIF -------------------------------------------------
async function runGif() {{
  document.getElementById("run-gif").disabled = true;
  log("=== gif_writer (MEMFS) ===");
  const m = await load(createFlowGif);
  setFact("f-memfs", "mounted", "ok");

  const rc = m.callMain([]);
  const path = "/build/gif_demo.gif";
  let bytes = null;
  try {{
    bytes = m.FS.readFile(path);
  }} catch (e) {{
    log("could not read " + path + ": " + e);
  }}

  if (!bytes) {{
    setRes("g-res", false, "FAIL (no file in MEMFS)");
    document.getElementById("run-gif").disabled = false;
    return false;
  }}

  const magic = String.fromCharCode(...bytes.slice(0, 6));
  const gif = parseGif(bytes);

  document.getElementById("g-path").textContent = path;
  document.getElementById("g-size").textContent = bytes.length.toLocaleString() + " bytes";
  document.getElementById("g-magic").textContent =
    magic + " " + gif.width + "x" + gif.height;
  document.getElementById("g-frames").textContent =
    gif.frames + (gif.trailer ? "" : " (truncated)");

  // Same program built with clang and run on macOS produces this file. If the
  // WASM run hashes the same, the encoder crossed without drifting a byte.
  const NATIVE_SHA256 =
    "{NATIVE_GIF_SHA256}";
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  const sha = [...new Uint8Array(digest)].map((v) => v.toString(16).padStart(2, "0")).join("");
  const sameAsNative = sha === NATIVE_SHA256;
  document.getElementById("g-sha").textContent = sha;
  const sameCell = document.getElementById("g-same");
  sameCell.textContent = sameAsNative ? "yes, byte for byte" : "no";
  sameCell.style.color = sameAsNative ? "var(--ok)" : "var(--warn)";

  const url = URL.createObjectURL(new Blob([bytes], {{ type: "image/gif" }}));
  const img = document.getElementById("gif-img");
  const shown = await new Promise((resolve) => {{
    img.onload = () => resolve(true);
    img.onerror = () => resolve(false);
    img.src = url;
  }});

  const ok = rc === 0 && magic.startsWith("GIF89a") && gif.trailer && gif.frames === 24 && shown;
  log(`  exit ${{rc}}, ${{bytes.length}} bytes, header ${{magic}} ${{gif.width}}x${{gif.height}}, ${{gif.frames}} frames, trailer ${{gif.trailer}}`);
  log(`  browser decoded it: ${{shown}} (${{img.naturalWidth}}x${{img.naturalHeight}})`);
  setRes("g-res", ok, ok ? `PASS: decoded ${{img.naturalWidth}}x${{img.naturalHeight}}` : "FAIL");
  document.getElementById("run-gif").disabled = false;
  return ok;
}}

// ---- 2. IDBFS -----------------------------------------------------------
// IDBFS is a MEMFS image plus an IndexedDB store, and they only meet when
// FS.syncfs is called. Inbound before the program runs, outbound after.
async function runCounter() {{
  document.getElementById("run-counter").disabled = true;
  log("=== fs_counter (IDBFS) ===");
  let syncIn = false;

  const m = await load(createFlowCounter, {{
    preRun: [function (mod) {{
      const FS = mod.FS;
      try {{ FS.mkdir("{IDBFS_MOUNT}"); }} catch (e) {{ /* already there */ }}
      FS.mount(mod.IDBFS, {{}}, "{IDBFS_MOUNT}");
      // Block startup until the IndexedDB contents are in memory.
      mod.addRunDependency("idbfs-in");
      FS.syncfs(true, (err) => {{
        if (err) log("  syncfs(in) error: " + err);
        else syncIn = true;
        mod.removeRunDependency("idbfs-in");
      }});
    }}],
  }});
  setFact("f-idbfs", "mounted at {IDBFS_MOUNT}", "ok");
  log("  syncfs(true) done: " + syncIn);

  let before = 0;
  try {{
    const prev = m.FS.readFile("{IDBFS_MOUNT}/run_counter.bin");
    before = new DataView(prev.buffer, prev.byteOffset, 4).getInt32(0, true);
  }} catch (e) {{
    before = 0;
  }}

  const rc = m.callMain([]);

  const after = new DataView(
    m.FS.readFile("{IDBFS_MOUNT}/run_counter.bin").buffer
  ).getInt32(0, true);

  const syncOut = await new Promise((resolve) => {{
    m.FS.syncfs(false, (err) => {{
      if (err) log("  syncfs(out) error: " + err);
      resolve(!err);
    }});
  }});
  log("  syncfs(false) done: " + syncOut);

  document.getElementById("c-before").textContent = String(before);
  document.getElementById("c-after").textContent = String(after);
  document.getElementById("c-sync").textContent = `${{syncIn}} / ${{syncOut}}`;
  setFact("f-runs", String(after), "ok");
  const ok = rc === 0 && after === before + 1 && syncOut;
  setRes("c-res", ok, ok ? `PASS: ${{before}} -> ${{after}}, persisted` : "FAIL");
  log(`  exit ${{rc}}, counter ${{before}} -> ${{after}}`);
  document.getElementById("run-counter").disabled = false;
  return ok;
}}

async function wipe() {{
  const m = await load(createFlowCounter, {{
    preRun: [function (mod) {{
      const FS = mod.FS;
      try {{ FS.mkdir("{IDBFS_MOUNT}"); }} catch (e) {{ /* already there */ }}
      FS.mount(mod.IDBFS, {{}}, "{IDBFS_MOUNT}");
      mod.addRunDependency("idbfs-in");
      FS.syncfs(true, () => mod.removeRunDependency("idbfs-in"));
    }}],
  }});
  try {{ m.FS.unlink("{IDBFS_MOUNT}/run_counter.bin"); }} catch (e) {{ /* nothing there */ }}
  await new Promise((r) => m.FS.syncfs(false, r));
  log("stored state wiped");
  setFact("f-runs", "0");
}}

// ---- 3. --preload-file ---------------------------------------------------
async function runPreload() {{
  document.getElementById("run-preload").disabled = true;
  log("=== fs_preload (--preload-file) ===");
  const m = await load(createFlowPreload);
  let listed = [];
  try {{ listed = m.FS.readdir("/data"); }} catch (e) {{ /* not mounted */ }}
  setFact("f-preload", listed.filter((f) => f[0] !== ".").join(", ") || "missing",
          listed.length > 2 ? "ok" : "bad");

  let text = "";
  const rc = m.callMain([]);
  text = out.textContent;
  const num = (re) => {{ const mm = text.match(re); return mm ? mm[1] : null; }};
  document.getElementById("p-bytes").textContent = num(/bytes: (\\d+)/) || "\\u2014";
  document.getElementById("p-lines").textContent = num(/lines: (\\d+)/) || "\\u2014";
  document.getElementById("p-sum").textContent = num(/checksum: (-?\\d+)/) || "\\u2014";
  const ok = rc === 0;
  setRes("p-res", ok, ok ? "PASS" : "FAIL");
  document.getElementById("run-preload").disabled = false;
  return ok;
}}

document.getElementById("run-gif").onclick = runGif;
document.getElementById("run-counter").onclick = runCounter;
document.getElementById("run-preload").onclick = runPreload;
document.getElementById("reload").onclick = () => location.reload();
document.getElementById("wipe").onclick = wipe;
window.runGif = runGif;
window.runCounter = runCounter;
window.runPreload = runPreload;
window.wipeState = wipe;
</script>
</body>
</html>
"""


def build_all(out_dir: Path, do_build: bool) -> None:
    gif_program = PROJECT_ROOT / "examples" / "graphics" / "gif_writer.flow"
    counter_program = PROJECT_ROOT / "examples" / "wasm" / "fs_counter.flow"
    preload_program = PROJECT_ROOT / "examples" / "wasm" / "fs_preload.flow"
    data_dir = PROJECT_ROOT / "examples" / "wasm" / "data"

    demos = {
        "gif": gif_program.stem,
        "counter": counter_program.stem,
        "preload": preload_program.stem,
    }

    if do_build:
        print("gif_writer -> MEMFS build")
        build_module(gif_program, out_dir, "createFlowGif", fs="memfs")
        print("fs_counter -> IDBFS build")
        build_module(counter_program, out_dir, "createFlowCounter", fs="idbfs")
        print("fs_preload -> MEMFS build with --preload-file")
        build_module(
            preload_program,
            out_dir,
            "createFlowPreload",
            fs="memfs",
            preload=[f"{data_dir}@/data"],
        )

    write_out(out_dir / "crossing.css", read_asset("crossing.css"))
    write_out(out_dir / "index.html", page_html(demos))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("program", nargs="?", help="single program; omit to build the demo page")
    ap.add_argument("--fs", choices=["memfs", "idbfs"], default="memfs")
    ap.add_argument("--preload", action="append", default=[], metavar="DIR@/MOUNT")
    ap.add_argument("--export-name", default="createFlowFs")
    # Single-program builds go somewhere of their own so they cannot clobber
    # the demo page's modules, which have fixed export names.
    ap.add_argument("--out", default=None)
    ap.add_argument("--no-build", action="store_true")
    args = ap.parse_args()

    default_out = BUILD_DIR / "fs-out" if args.program else SITE_DIR / "fs"
    out_dir = Path(args.out).resolve() if args.out else default_out

    if args.program:
        program = Path(args.program).resolve()
        if not program.exists():
            sys.exit(f"no such program: {program}")
        print(f"Flow -> C -> WASM ({args.fs}): {program.name}")
        build_module(
            program, out_dir, args.export_name, fs=args.fs, preload=args.preload
        )
        print(f"\nWrote {out_dir}/{program.stem}.js")
        return 0

    build_all(out_dir, not args.no_build)
    print("\nServe it:  python3 -m http.server -d site 8000")
    print("Then open: http://127.0.0.1:8000/wasm-crossings/fs/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
