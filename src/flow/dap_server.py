#!/usr/bin/env python3
"""Debug Adapter Protocol server for Flow (wraps lldb-dap).

IDE mode (stdio, non-TTY): speaks DAP, builds with `./flow debug --no-launch`,
rewrites `launch` to point at the `.debug` binary, then proxies to `lldb-dap`.

CLI:
  ./flow dap examples/basics/hello_world.flow   # → ./flow debug …
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import threading
from pathlib import Path
from typing import Any, Dict, Optional

REPO = Path(__file__).resolve().parents[2]


def _find_lldb_dap() -> Optional[str]:
    for cand in (
        shutil.which("lldb-dap"),
        "/Applications/Xcode.app/Contents/Developer/usr/bin/lldb-dap",
        "/Library/Developer/CommandLineTools/usr/bin/lldb-dap",
    ):
        if cand and Path(cand).is_file():
            return cand
    try:
        out = subprocess.run(
            ["xcrun", "-f", "lldb-dap"],
            capture_output=True,
            text=True,
            check=False,
        )
        p = (out.stdout or "").strip()
        if p and Path(p).is_file():
            return p
    except Exception:
        pass
    return None


def _build_debug(flow_file: Path) -> Path:
    flow_cli = REPO / "flow"
    r = subprocess.run(
        [str(flow_cli), "debug", str(flow_file), "--no-launch"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        raise RuntimeError(
            f"flow debug --no-launch failed:\n{r.stdout}\n{r.stderr}"
        )
    exe = REPO / "build" / f"{flow_file.stem}.debug"
    if not exe.exists():
        raise RuntimeError(f"expected debug binary missing: {exe}")
    return exe


def _read_message(stream) -> Optional[Dict[str, Any]]:
    headers: Dict[str, str] = {}
    while True:
        line = stream.readline()
        if not line:
            return None
        if isinstance(line, bytes):
            line = line.decode("utf-8")
        line = line.strip("\r\n")
        if line == "":
            break
        if ":" in line:
            k, v = line.split(":", 1)
            headers[k.strip().lower()] = v.strip()
    length = int(headers.get("content-length", "0"))
    if length <= 0:
        return None
    body = stream.read(length)
    if isinstance(body, bytes):
        body = body.decode("utf-8")
    return json.loads(body)


def _write_message(stream, msg: Dict[str, Any]) -> None:
    data = json.dumps(msg).encode("utf-8")
    header = f"Content-Length: {len(data)}\r\n\r\n".encode("utf-8")
    stream.write(header + data)
    stream.flush()


def _send_error(seq: int, command: str, message: str) -> None:
    _write_message(
        sys.stdout.buffer,
        {
            "type": "response",
            "request_seq": seq,
            "success": False,
            "command": command,
            "message": message,
        },
    )


def run_ide_adapter() -> int:
    lldb_dap = _find_lldb_dap()
    if not lldb_dap:
        # Still answer initialize so the IDE shows a clear error on launch.
        while True:
            msg = _read_message(sys.stdin.buffer)
            if msg is None:
                return 2
            if msg.get("command") == "initialize":
                _write_message(
                    sys.stdout.buffer,
                    {
                        "type": "response",
                        "request_seq": msg.get("seq", 0),
                        "success": True,
                        "command": "initialize",
                        "body": {
                            "supportsConfigurationDoneRequest": True,
                        },
                    },
                )
                _write_message(
                    sys.stdout.buffer,
                    {
                        "type": "event",
                        "event": "initialized",
                        "body": {},
                    },
                )
            elif msg.get("command") == "launch":
                _send_error(
                    msg.get("seq", 0),
                    "launch",
                    "lldb-dap not found; install Xcode CLT or use ./flow debug",
                )
                return 2
            else:
                _write_message(
                    sys.stdout.buffer,
                    {
                        "type": "response",
                        "request_seq": msg.get("seq", 0),
                        "success": True,
                        "command": msg.get("command", ""),
                        "body": {},
                    },
                )

    child = subprocess.Popen(
        [lldb_dap],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=sys.stderr,
    )
    assert child.stdin and child.stdout

    def pump_lldb_to_client() -> None:
        try:
            while True:
                msg = _read_message(child.stdout)
                if msg is None:
                    break
                _write_message(sys.stdout.buffer, msg)
        except Exception:
            pass

    threading.Thread(target=pump_lldb_to_client, daemon=True).start()

    while True:
        msg = _read_message(sys.stdin.buffer)
        if msg is None:
            break
        if msg.get("type") == "request" and msg.get("command") == "launch":
            args = dict(msg.get("arguments") or {})
            flow_src = (
                args.get("flowFile")
                or args.get("program")
                or args.get("source")
            )
            if not flow_src:
                _send_error(msg.get("seq", 0), "launch", "missing flowFile/program")
                continue
            src = Path(str(flow_src)).expanduser()
            if not src.is_absolute():
                cwd = Path(str(args.get("cwd") or REPO))
                src = (cwd / src).resolve()
            try:
                exe = _build_debug(src)
            except RuntimeError as exc:
                _send_error(msg.get("seq", 0), "launch", str(exc)[:500])
                continue
            args["program"] = str(exe)
            args.setdefault("cwd", str(REPO))
            msg = {**msg, "arguments": args}
        _write_message(child.stdin, msg)

    try:
        child.terminate()
    except Exception:
        pass
    return 0


def main(argv: Optional[list] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0

    # CLI convenience → interactive LLDB
    if argv and sys.stdin.isatty():
        src = Path(argv[0])
        return subprocess.call([str(REPO / "flow"), "debug", str(src)])

    # IDE / stdio DAP
    return run_ide_adapter()


if __name__ == "__main__":
    raise SystemExit(main())
