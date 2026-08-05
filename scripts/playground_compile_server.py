#!/usr/bin/env python3
"""Local native compile API for the FLOW playground (GitHub #132, Option B).

Binds to 127.0.0.1 only. The playground's "Run (native local)" button POSTs
source here; we transpile with the real Flow toolchain, optionally compile +
run with clang, and return stdout/stderr.

Security (keep this localhost-only):
  - bind address is loopback (override only via --host for advanced use)
  - request body capped (default 64 KiB)
  - subprocess timeouts (default 15s transpile / 10s run)
  - no shell=True; temp dir wiped per request
  - CORS restricted to common local origins

Usage (from repo root):
  python3 scripts/playground_compile_server.py
  # then open the wiki playground and click Run (native local)

  python3 scripts/playground_compile_server.py --port 8765 --no-run  # transpile only
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PORT = 8765
MAX_SOURCE_BYTES = 64 * 1024
ALLOWED_ORIGINS = {
    "http://127.0.0.1:8777",
    "http://localhost:8777",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "http://127.0.0.1:8765",
    "http://localhost:8765",
    "null",  # file:// pages send Origin: null
}


def _cors_origin(handler: BaseHTTPRequestHandler) -> str:
    origin = handler.headers.get("Origin", "")
    if origin in ALLOWED_ORIGINS:
        return origin
    # Allow any localhost / 127.0.0.1 port for local wiki servers.
    try:
        u = urlparse(origin)
        if u.hostname in ("127.0.0.1", "localhost"):
            return origin
    except Exception:
        pass
    return "http://127.0.0.1:8777"


def compile_and_maybe_run(
    source: str,
    *,
    do_run: bool,
    transpile_timeout: float,
    run_timeout: float,
    target: str = "native",
) -> dict:
    if len(source.encode("utf-8", errors="replace")) > MAX_SOURCE_BYTES:
        return {
            "ok": False,
            "mode": "native-local",
            "error": f"source exceeds {MAX_SOURCE_BYTES} byte limit",
        }

    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO_ROOT / "src") + (
        os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else ""
    )

    tmp = tempfile.mkdtemp(prefix="flow-playground-")
    try:
        flow_path = Path(tmp) / "main.flow"
        c_path = Path(tmp) / "main.c"
        bin_path = Path(tmp) / "main"
        flow_path.write_text(source, encoding="utf-8")

        try:
            tp = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "flow.transpiler",
                    str(flow_path),
                    "--c",
                    "--lenient",
                    "-o",
                    str(c_path),
                ],
                capture_output=True,
                text=True,
                timeout=transpile_timeout,
                env=env,
                cwd=REPO_ROOT,
            )
        except subprocess.TimeoutExpired:
            return {
                "ok": False,
                "mode": "native-local",
                "error": f"transpile exceeded {transpile_timeout}s",
            }

        if tp.returncode != 0 or not c_path.exists():
            return {
                "ok": False,
                "mode": "native-local",
                "error": "transpile failed",
                "stderr": (tp.stderr or "")[-4000:],
                "stdout": (tp.stdout or "")[-2000:],
            }

        c_preview = c_path.read_text(encoding="utf-8", errors="replace")[:6000]

        if target == "c" or (not do_run and target != "wasm"):
            return {
                "ok": True,
                "mode": "transpile-c",
                "stdout": "Transpile OK (C only).\n",
                "c_preview": c_preview,
            }

        if target == "wasm":
            emcc = shutil.which("emcc")
            if not emcc:
                return {
                    "ok": False,
                    "mode": "wasm-local",
                    "error": "emcc not on PATH (install emsdk)",
                    "c_preview": c_preview,
                }
            js_out = Path(tmp) / "main.js"
            try:
                cp = subprocess.run(
                    [
                        emcc,
                        str(c_path),
                        "-O1",
                        "-s",
                        "WASM=1",
                        "-s",
                        "EXPORTED_FUNCTIONS=['_main']",
                        "-o",
                        str(js_out),
                    ],
                    capture_output=True,
                    text=True,
                    timeout=transpile_timeout + 30,
                    cwd=tmp,
                )
            except subprocess.TimeoutExpired:
                return {
                    "ok": False,
                    "mode": "wasm-local",
                    "error": "emcc exceeded timeout",
                    "c_preview": c_preview,
                }
            if cp.returncode != 0 or not js_out.exists():
                return {
                    "ok": False,
                    "mode": "wasm-local",
                    "error": "emcc failed",
                    "stderr": (cp.stderr or "")[-4000:],
                    "c_preview": c_preview,
                }
            # Node can execute the modularized/non-modularized emcc output.
            node = shutil.which("node")
            if not node or not do_run:
                return {
                    "ok": True,
                    "mode": "wasm-local",
                    "stdout": "WASM build OK (run skipped or node missing).\n",
                    "c_preview": c_preview,
                }
            try:
                rp = subprocess.run(
                    [node, str(js_out)],
                    capture_output=True,
                    text=True,
                    timeout=run_timeout,
                    cwd=tmp,
                )
            except subprocess.TimeoutExpired:
                return {
                    "ok": False,
                    "mode": "wasm-local",
                    "error": f"wasm run exceeded {run_timeout}s",
                    "c_preview": c_preview,
                }
            return {
                "ok": rp.returncode == 0,
                "mode": "wasm-local",
                "exit_code": rp.returncode,
                "stdout": (rp.stdout or "")[-8000:],
                "stderr": (rp.stderr or "")[-4000:],
                "c_preview": c_preview,
            }

        clang = shutil.which("clang") or shutil.which("cc")
        if not clang:
            return {
                "ok": False,
                "mode": "native-local",
                "error": "clang/cc not found on PATH",
                "c_preview": c_preview,
            }

        try:
            cp = subprocess.run(
                [clang, "-O0", "-o", str(bin_path), str(c_path)],
                capture_output=True,
                text=True,
                timeout=transpile_timeout,
                cwd=tmp,
            )
        except subprocess.TimeoutExpired:
            return {
                "ok": False,
                "mode": "native-local",
                "error": "clang exceeded timeout",
                "c_preview": c_preview,
            }

        if cp.returncode != 0 or not bin_path.exists():
            return {
                "ok": False,
                "mode": "native-local",
                "error": "C compile failed",
                "stderr": (cp.stderr or "")[-4000:],
                "c_preview": c_preview,
            }

        try:
            rp = subprocess.run(
                [str(bin_path)],
                capture_output=True,
                text=True,
                timeout=run_timeout,
                cwd=tmp,
            )
        except subprocess.TimeoutExpired:
            return {
                "ok": False,
                "mode": "native-local",
                "error": f"program exceeded {run_timeout}s runtime limit",
                "c_preview": c_preview,
            }

        return {
            "ok": rp.returncode == 0,
            "mode": "native-local",
            "exit_code": rp.returncode,
            "stdout": (rp.stdout or "")[-8000:],
            "stderr": (rp.stderr or "")[-4000:],
            "c_preview": c_preview,
        }
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def make_handler(do_run: bool, transpile_timeout: float, run_timeout: float):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt: str, *args) -> None:
            sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

        def _send(self, code: int, payload: dict) -> None:
            body = json.dumps(payload).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Access-Control-Allow-Origin", _cors_origin(self))
            self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS, GET")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()
            self.wfile.write(body)

        def do_OPTIONS(self) -> None:  # noqa: N802
            self._send(204, {})

        def do_GET(self) -> None:  # noqa: N802
            path = urlparse(self.path).path
            if path in ("/", "/health"):
                self._send(
                    200,
                    {
                        "ok": True,
                        "service": "flow-playground-compile",
                        "run": do_run,
                        "targets": ["native", "c", "wasm"],
                        "max_source_bytes": MAX_SOURCE_BYTES,
                        "pyodide": "/pyodide",
                    },
                )
                return
            # Serve Flow Python sources for in-browser Pyodide transpile.
            if path.startswith("/flow-src/"):
                rel = path[len("/flow-src/") :]
                if ".." in rel or rel.startswith("/"):
                    self._send(400, {"ok": False, "error": "bad path"})
                    return
                root = (REPO_ROOT / "src" / "flow").resolve()
                target = (root / rel).resolve()
                if not str(target).startswith(str(root)) or not target.is_file():
                    self._send(404, {"ok": False, "error": "not found"})
                    return
                data = target.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
                self.send_header("Access-Control-Allow-Origin", _cors_origin(self))
                self.end_headers()
                self.wfile.write(data)
                return
            if path == "/pyodide":
                page = (REPO_ROOT / "docs" / "playground" / "pyodide.html")
                if not page.is_file():
                    self._send(404, {"ok": False, "error": "pyodide.html missing"})
                    return
                data = page.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
                self.send_header("Access-Control-Allow-Origin", _cors_origin(self))
                self.end_headers()
                self.wfile.write(data)
                return
            self._send(404, {"ok": False, "error": "not found"})

        def do_POST(self) -> None:  # noqa: N802
            if self.path.rstrip("/") != "/compile":
                self._send(404, {"ok": False, "error": "not found"})
                return
            length = int(self.headers.get("Content-Length") or "0")
            if length <= 0 or length > MAX_SOURCE_BYTES + 2048:
                self._send(413, {"ok": False, "error": "body too large or empty"})
                return
            raw = self.rfile.read(length)
            try:
                data = json.loads(raw.decode("utf-8"))
            except Exception:
                self._send(400, {"ok": False, "error": "invalid JSON"})
                return
            source = data.get("source")
            if not isinstance(source, str) or not source.strip():
                self._send(400, {"ok": False, "error": "missing source string"})
                return
            target = str(data.get("target") or "native")
            if target not in ("native", "c", "wasm"):
                target = "native"
            result = compile_and_maybe_run(
                source,
                do_run=do_run if target != "c" else False,
                transpile_timeout=transpile_timeout,
                run_timeout=run_timeout,
                target=target,
            )
            self._send(200 if result.get("ok") else 422, result)

    return Handler


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--host", default="127.0.0.1", help="bind address (default loopback)")
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)
    ap.add_argument(
        "--no-run",
        action="store_true",
        help="transpile only (do not clang + execute)",
    )
    ap.add_argument("--transpile-timeout", type=float, default=15.0)
    ap.add_argument("--run-timeout", type=float, default=10.0)
    args = ap.parse_args()

    if args.host not in ("127.0.0.1", "localhost", "::1") and args.host != "0.0.0.0":
        print(
            "WARNING: binding outside loopback exposes a compile endpoint. "
            "Prefer 127.0.0.1.",
            file=sys.stderr,
        )

    handler = make_handler(
        do_run=not args.no_run,
        transpile_timeout=args.transpile_timeout,
        run_timeout=args.run_timeout,
    )
    server = ThreadingHTTPServer((args.host, args.port), handler)
    print(
        f"FLOW playground compile API on http://{args.host}:{args.port}/compile\n"
        f"  health: http://{args.host}:{args.port}/health\n"
        f"  run={'off' if args.no_run else 'on'}  "
        f"max_source={MAX_SOURCE_BYTES}B\n"
        f"Open the wiki playground and use Run (native local).",
        flush=True,
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nbye", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
