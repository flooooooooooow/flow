#!/usr/bin/env python3
"""Shared plumbing for the Flow WASM crossing builds.

A "crossing" is one thing people assume cannot reach WebAssembly: OS threads,
the GPU, sockets, an embedded CPython. Each crossing has its own build script
(wasm/flow_wasm_threads.py and friends); this module holds the parts they all
need: locating the tree, driving the Flow compiler, and setting up Homebrew's
Emscripten so emcc actually finds a wasm backend.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
RUNTIME_DIR = PROJECT_ROOT / "runtime"
BUILD_DIR = PROJECT_ROOT / "build" / "wasm-crossings"
SITE_DIR = PROJECT_ROOT / "site" / "wasm-crossings"

# Homebrew's emscripten ships a config pointing LLVM_ROOT at /usr/bin (Xcode
# clang, which has no wasm backend) and a launcher that picks the system
# python3. Point both at emscripten's own copies unless the caller already has.
_EM_DEFAULTS = {
    "EMSDK_PYTHON": "/opt/homebrew/bin/python3.14",
    "EM_LLVM_ROOT": "/opt/homebrew/opt/emscripten/libexec/llvm/bin",
    "EM_BINARYEN_ROOT": "/opt/homebrew/opt/emscripten/libexec/binaryen",
}


def emscripten_env() -> dict:
    """Environment for emcc, with the Homebrew paths filled in if unset."""
    env = dict(os.environ)
    for key, value in _EM_DEFAULTS.items():
        if not env.get(key) and Path(value).exists():
            env[key] = value
    return env


def require_emcc() -> str:
    emcc = shutil.which("emcc")
    if not emcc:
        sys.exit("emcc not on PATH. Install emscripten (brew install emscripten).")
    return emcc


def run(cmd, env=None, cwd=None, quiet=False) -> subprocess.CompletedProcess:
    """Run a command, echoing it, and abort the build if it fails."""
    if not quiet:
        print("  $ " + " ".join(str(c) for c in cmd))
    proc = subprocess.run(
        [str(c) for c in cmd],
        env=env,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        sys.stdout.write(proc.stdout)
        sys.stderr.write(proc.stderr)
        sys.exit(f"command failed ({proc.returncode}): {cmd[0]}")
    return proc


def flow_to_c_available() -> bool:
    """True when the Python-hosted Flow compiler can be imported from src/."""
    return (SRC_DIR / "flow" / "transpiler.py").exists()


def flow_to_c(flow_file: Path, out_c: Path, library: bool = False) -> Path:
    """Compile a .flow source to C with the Python-hosted Flow compiler."""
    out_c.parent.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env["PYTHONPATH"] = str(SRC_DIR) + os.pathsep + env.get("PYTHONPATH", "")
    cmd = [sys.executable, "-m", "flow.transpiler", str(flow_file), "--c"]
    cmd += ["--library", "--lenient"] if library else ["--strict"]
    cmd += ["-o", str(out_c)]
    run(cmd, env=env, quiet=True)
    if not out_c.exists():
        sys.exit(f"Flow compiler produced no C for {flow_file}")
    return out_c


def read_asset(name: str) -> str:
    """Read a page asset that ships next to the crossing scripts."""
    return (Path(__file__).resolve().parent / "crossing_assets" / name).read_text()


def write_out(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    print(f"  wrote {path.relative_to(PROJECT_ROOT)}")
    return path
