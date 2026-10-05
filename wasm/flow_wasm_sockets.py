#!/usr/bin/env python3
"""Crossing 3: Flow's BSD sockets, dialling out from a browser tab.

runtime/flow_tcp.c is `socket()`, `connect()`, `send()`, `recv()`, `close()`
and nothing else. Emscripten bridges those calls onto WebSockets, so
`connect(fd, 127.0.0.1:9505)` inside the module opens `ws://127.0.0.1:9505/`
and each send becomes a binary frame. The C file is compiled for wasm
unmodified.

A browser cannot open a raw TCP socket to an arbitrary host and port. That is
a browser security rule, not a Flow limitation, and no amount of compiler work
removes it. Something on the far end has to speak WebSocket, which is what
scripts/ws_echo_relay.py is.

The build turns on -sASYNCIFY because Emscripten's socket bridge cannot block:
the handshake and every inbound frame arrive on the event loop, so the program
has to yield while it polls. flow_net_yield is emscripten_sleep here and
usleep natively.

Usage:
    python3 wasm/flow_wasm_sockets.py [program.flow] [--port 9505]
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
    read_asset,
    require_emcc,
    run,
    write_out,
)

DEFAULT_PROGRAM = PROJECT_ROOT / "examples" / "wasm" / "tcp_echo.flow"
ASSETS = Path(__file__).resolve().parent / "crossing_assets"

RUNTIME_C_SOURCES = [
    RUNTIME_DIR / "flow_tcp.c",       # BSD sockets, unmodified
    RUNTIME_DIR / "flow_rt_support.c",  # monotonic clock
    ASSETS / "net_yield_shim.c",
]


def build(program: Path, port: int, out_dir: Path, do_build: bool) -> None:
    stem = program.stem
    work = BUILD_DIR / "sockets"
    work.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Flow -> C: {program.relative_to(PROJECT_ROOT)}")
    c_file = flow_to_c(program, work / f"{stem}.c")

    if do_build:
        run(
            [
                require_emcc(),
                "-O2",
                "-Wno-everything",
                f"-I{RUNTIME_DIR}",
                f"-DFLOW_DEMO_PORT={port}",
                str(c_file),
                *[str(s) for s in RUNTIME_C_SOURCES],
                # Emscripten's socket bridge is event-loop driven, so the
                # program must be able to yield mid-call.
                "-sASYNCIFY",
                "-sASYNCIFY_STACK_SIZE=16384",
                "-sMODULARIZE=1",
                "-sEXIT_RUNTIME=1",
                "-sALLOW_MEMORY_GROWTH=1",
                "-sEXPORT_NAME=createFlowSockets",
                "-sENVIRONMENT=web",
                "-o",
                str(out_dir / f"{stem}.js"),
            ],
            env=emscripten_env(),
        )

    write_out(out_dir / "crossing.css", read_asset("crossing.css"))
    write_out(out_dir / "index.html", page_html(stem, program, port))


def page_html(stem: str, program: Path, port: int) -> str:
    source = html.escape(program.read_text())
    relay = html.escape((PROJECT_ROOT / "scripts" / "ws_echo_relay.py").read_text()[:1400])
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Flow crossing 3: BSD sockets from a browser</title>
<link rel="stylesheet" href="crossing.css">
</head>
<body>
<main>
<h1>Crossing 3 &mdash; sockets</h1>
<p class="lede">
<code>runtime/flow_tcp.c</code> is BSD sockets and nothing else, compiled for
wasm unmodified. Emscripten maps <code>connect()</code>,
<code>send()</code> and <code>recv()</code> onto a WebSocket, so a Flow program
calling the ordinary socket API round-trips bytes from inside this tab.
</p>
<p class="lede">
The far end has to speak WebSocket, because a browser cannot open a raw TCP
socket to an arbitrary host and port. That is a browser security rule.
Start the relay first:
<code>python3 scripts/ws_echo_relay.py --port {port}</code>
</p>

<div class="facts">
  <div class="fact"><span class="k">relay</span><span class="v" id="f-relay">&hellip;</span></div>
  <div class="fact"><span class="k">port</span><span class="v">{port}</span></div>
  <div class="fact"><span class="k">transport</span><span class="v">ws://127.0.0.1:{port}/</span></div>
  <div class="fact"><span class="k">round trips ok</span><span class="v" id="f-ok">&mdash;</span></div>
</div>

<h2>Run</h2>
<div class="panel">
  <button id="run">Connect and echo</button>
  <button id="probe" class="secondary">Probe relay</button>
  <button id="clear" class="secondary">Clear</button>
</div>

<h2>Measured</h2>
<div class="panel">
<table>
  <thead><tr><th>connect</th><th>round trips</th><th>best rtt</th><th>mean rtt</th><th>result</th></tr></thead>
  <tbody><tr>
    <td id="m-conn">&mdash;</td><td id="m-trips">&mdash;</td>
    <td id="m-best">&mdash;</td><td id="m-mean">&mdash;</td><td id="m-res">&mdash;</td>
  </tr></tbody>
</table>
</div>

<h2>Program output</h2>
<pre id="out">click run</pre>

<h2>Flow source</h2>
<pre class="source">{source}</pre>

<h2>The relay (head of scripts/ws_echo_relay.py)</h2>
<pre class="source">{relay}</pre>

<footer>
Built by <code>wasm/flow_wasm_sockets.py</code>. Mechanism:
<code>docs/language/wasm-crossings.md</code>.
</footer>
</main>

<script src="{stem}.js"></script>
<script>
const out = document.getElementById("out");
const log = (s) => {{ out.textContent += s + "\\n"; out.scrollTop = out.scrollHeight; }};
const setFact = (id, text, cls) => {{
  const el = document.getElementById(id);
  el.textContent = text;
  el.className = "v" + (cls ? " " + cls : "");
}};

// Open a WebSocket by hand first, so a missing relay is reported as a missing
// relay instead of as a socket bug inside the module.
function probe() {{
  return new Promise((resolve) => {{
    let ws;
    try {{
      ws = new WebSocket("ws://127.0.0.1:{port}/", "binary");
    }} catch (e) {{
      setFact("f-relay", "unreachable", "bad");
      resolve(false);
      return;
    }}
    let settled = false;
    const done = (ok) => {{
      if (settled) return;   // onopen and the timeout can both fire
      settled = true;
      setFact("f-relay", ok ? "reachable" : "not running", ok ? "ok" : "bad");
      if (!ok) log("relay not reachable: start it with  python3 scripts/ws_echo_relay.py --port {port}");
      try {{ ws.close(); }} catch (e) {{ /* already closed */ }}
      resolve(ok);
    }};
    ws.onopen = () => done(true);
    ws.onerror = () => done(false);
    setTimeout(() => done(false), 2000);
  }});
}}

async function runProgram() {{
  document.getElementById("run").disabled = true;
  if (!(await probe())) {{
    document.getElementById("run").disabled = false;
    return;
  }}
  log("=== tcp_echo ===");
  let text = "";
  await new Promise((resolve) => {{
    createFlowSockets({{
      print: (s) => {{ text += s + "\\n"; log(s); }},
      printErr: (s) => {{ text += s + "\\n"; log("stderr: " + s); }},
      onExit: () => resolve(),
      quit: () => resolve(),
    }}).catch((e) => {{ log("module failed: " + e); resolve(); }});
  }});

  const num = (re) => {{ const m = text.match(re); return m ? m[1] : null; }};
  const trips = num(/round trips ok:\\s+(\\d+ \\/ \\d+)/);
  document.getElementById("m-conn").textContent = /connected, fd/.test(text) ? "ok" : "failed";
  document.getElementById("m-trips").textContent = trips || "\\u2014";
  document.getElementById("m-best").textContent = (num(/best rtt ms ([0-9.]+)/) || "\\u2014") + " ms";
  document.getElementById("m-mean").textContent = (num(/mean rtt ms ([0-9.]+)/) || "\\u2014") + " ms";
  const pass = /\\bPASS\\b/.test(text);
  const res = document.getElementById("m-res");
  res.textContent = pass ? "PASS" : "FAIL";
  res.style.color = pass ? "var(--ok)" : "var(--bad)";
  setFact("f-ok", trips || "\\u2014", pass ? "ok" : "bad");
  document.getElementById("run").disabled = false;
  return pass;
}}

document.getElementById("run").onclick = runProgram;
document.getElementById("probe").onclick = probe;
document.getElementById("clear").onclick = () => {{ out.textContent = ""; }};
window.runProgram = runProgram;
probe();
</script>
</body>
</html>
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("program", nargs="?", default=str(DEFAULT_PROGRAM))
    ap.add_argument("--port", type=int, default=9505)
    ap.add_argument("--out", default=str(SITE_DIR / "sockets"))
    ap.add_argument("--no-build", action="store_true")
    args = ap.parse_args()

    program = Path(args.program).resolve()
    if not program.exists():
        sys.exit(f"no such program: {program}")

    build(program, args.port, Path(args.out).resolve(), not args.no_build)
    print(f"\nStart the relay: python3 scripts/ws_echo_relay.py --port {args.port}")
    print("Serve it:        python3 -m http.server -d site 8000")
    print("Then open:       http://127.0.0.1:8000/wasm-crossings/sockets/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
