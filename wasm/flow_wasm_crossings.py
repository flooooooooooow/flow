#!/usr/bin/env python3
"""Build every WASM crossing demo, and the index that ties them together.

    python3 wasm/flow_wasm_crossings.py            # build all five
    python3 wasm/flow_wasm_crossings.py --index    # index page only

Each crossing has its own script and can be run on its own:

    wasm/flow_wasm_threads.py    OS threads over Web Workers
    wasm/flow_wasm_gpu.py        @gpu kernels to WGSL, dispatched by WebGPU
    wasm/flow_wasm_sockets.py    BSD sockets over WebSockets
    wasm/flow_wasm_python.py     Flow's CPython embedding, routed to Pyodide
    wasm/flow_wasm_fs.py         stdio on MEMFS, IDBFS and preloaded data
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from crossing_common import SITE_DIR, read_asset, write_out  # noqa: E402

HERE = Path(__file__).resolve().parent

CROSSINGS = [
    ("threads", "flow_wasm_threads.py"),
    ("gpu", "flow_wasm_gpu.py"),
    ("sockets", "flow_wasm_sockets.py"),
    ("python", "flow_wasm_python.py"),
    ("fs", "flow_wasm_fs.py"),
]


def index_html() -> str:
    body = read_asset("index_template.html")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Flow: WASM crossings</title>
<link rel="stylesheet" href="crossing.css">
</head>
<body>
<main>
{body}
</main>
</body>
</html>
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--index", action="store_true", help="write the index page only")
    ap.add_argument("--out", default=str(SITE_DIR))
    args = ap.parse_args()

    out_dir = Path(args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    if not args.index:
        for name, script in CROSSINGS:
            print(f"=== {name} ===")
            rc = subprocess.run([sys.executable, str(HERE / script)]).returncode
            if rc != 0:
                sys.exit(f"{script} failed ({rc})")

    write_out(out_dir / "crossing.css", read_asset("crossing.css"))
    write_out(out_dir / "index.html", index_html())

    print("\nServe it:  python3 -m http.server -d site 8000")
    print("Then open: http://127.0.0.1:8000/wasm-crossings/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
