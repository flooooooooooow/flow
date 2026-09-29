"""Flow Shader Language (FSL) fill shaders, built by flowc.

The language is written in Flow (compiler/src/shader_dsl.flow) and flowc
builds it to Metal or WGSL with FLOWC_SHADER=metal|wgsl. This module is the
bridge for the Python host's module resolver and wasm/flow_webgpu_shader.py.
Parity with the retired Python backends is held by
compiler/scripts/parity_shader_dsl.sh. See docs/language/shaders.md.
"""

from __future__ import annotations

import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional

_ROOT = Path(__file__).resolve().parents[2]
_HEAD_RE = re.compile(r"^[ \t]*shader\s+fill\s+[A-Za-z_]\w*\s*\{", re.MULTILINE)
_DIAG = "flowc shader: "


def has_fill_shader_dsl(source: str) -> bool:
    """True when a line starts a `shader fill` block (an FSL module)."""
    return bool(_HEAD_RE.search(source))


def _flowc() -> str:
    """FLOWC_BIN, else flowc built with cc from the checked-in bootstrap C."""
    env_bin = os.environ.get("FLOWC_BIN")
    if env_bin and os.access(env_bin, os.X_OK):
        return env_bin
    boot_c = _ROOT / "compiler" / "bootstrap" / "flowc_stage_a.c"
    binary = _ROOT / "compiler" / "build" / "flowc_bootstrap"
    if not binary.exists() or binary.stat().st_mtime < boot_c.stat().st_mtime:
        binary.parent.mkdir(parents=True, exist_ok=True)
        tmp = binary.with_name(f"flowc_bootstrap.{os.getpid()}")
        cc = os.environ.get("CC", "cc")
        subprocess.run([cc, "-O2", "-o", str(tmp), str(boot_c), "-lm"], check=True, capture_output=True)
        os.replace(tmp, binary)
    return str(binary)


def _run(mode: str, source: str, out: Optional[str] = None, name: Optional[str] = None) -> str:
    env = dict(os.environ, FLOWC_SHADER=mode, FLOWC_IN=str(source))
    for key in ("FLOWC_BUNDLE", "FLOWC_OUT", "FLOWC_SHADER_NAME"):
        env.pop(key, None)
    if out is not None:
        env["FLOWC_OUT"] = str(out)
    if name:
        env["FLOWC_SHADER_NAME"] = name
    proc = subprocess.run([_flowc()], env=env, capture_output=True, text=True)
    if proc.returncode != 0:
        at = proc.stdout.find(_DIAG)
        if at >= 0:
            raise SyntaxError(proc.stdout[at + len(_DIAG):].rstrip("\n"))
        raise SyntaxError("flowc shader failed: " + (proc.stdout + proc.stderr).strip())
    return proc.stdout


def fill_names(source_path: str) -> List[str]:
    """Names of the `shader fill` blocks in a file, in source order."""
    return _run("list", source_path).splitlines()


def expand_fill_shader(source: str) -> str:
    """Host Flow for a source: a stub main for an FSL module, else unchanged."""
    if not has_fill_shader_dsl(source):
        return source
    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, "in.flow")
        out = os.path.join(tmp, "out.flow")
        with open(src, "w", encoding="utf-8", newline="") as f:
            f.write(source)
        _run("expand", src, out)
        with open(out, encoding="utf-8", newline="") as f:
            return f.read()


def compile_shader_file(
    source_path: str,
    out_dir: str,
    shader_name: Optional[str] = None,
    target: str = "metal",
) -> Path:
    """Build the fills of a `.flow` file to `target` (metal or wgsl) files.

    Metal writes `<stem>_gallery.metal`, `<stem>_gallery.entries` and a
    `<name>_fill.metal` / `.entry` pair per fill. WGSL writes
    `<stem>_gallery.wgsl` (or `<name>_fill.wgsl` when named) and
    `<stem>_gallery.wgsl.entries`. Returns the gallery (or named) path.
    """
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    return Path(_run(target, source_path, out_dir, shader_name).splitlines()[-1])
