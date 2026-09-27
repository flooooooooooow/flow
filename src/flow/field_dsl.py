"""Field / boundary PDE surface (#163), expanded by flowc.

The expander is written in Flow (compiler/src/field_dsl.flow) and runs inside
flowc before parse. The Python host calls flowc's FLOWC_EXPAND_ONLY mode
instead of keeping a second implementation:

    field T : f64[32] on Line
    T evolves as laplacian(T)
    boundary T { left = AMBIENT  right = AMBIENT }

becomes `T_field_step(u, next, r)` calling `heat_euler_step_1d`. Parity with
the retired Python expander is held by compiler/scripts/parity_field_dsl.sh.

`run_flowc_expand` is shared with dynamics_dsl.py and flow_blocks.py, which
bridge to the other two flowc source expansions the same way.
"""

from __future__ import annotations

import os
import re
import subprocess
import tempfile
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_HEAD_RE = re.compile(r"^\s*field\s+\w+\s*:|^\s*boundary\s+\w+\s*\{", re.MULTILINE)
_DIAG = "flowc field: "


def has_field_dsl(source: str) -> bool:
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
        subprocess.run([cc, "-O2", "-o", str(tmp), str(boot_c)], check=True, capture_output=True)
        os.replace(tmp, binary)
    return str(binary)


def run_flowc_expand(source: str, stage: str):
    """Run one flowc expansion stage (field, dynamics or flow) on source.

    Returns (expanded, None) or (None, flowc stdout) when flowc reports a
    diagnostic.
    """
    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, "in.flow")
        out = os.path.join(tmp, "out.flow")
        with open(src, "w", encoding="utf-8", newline="") as f:
            f.write(source)
        env = dict(os.environ, FLOWC_EXPAND_ONLY=stage, FLOWC_IN=src, FLOWC_OUT=out)
        env.pop("FLOWC_BUNDLE", None)
        proc = subprocess.run([_flowc()], env=env, capture_output=True, text=True)
        if proc.returncode != 0:
            return None, proc.stdout + proc.stderr
        with open(out, encoding="utf-8", newline="") as f:
            return f.read(), None


def expand_field_dsl(source: str) -> str:
    if not has_field_dsl(source):
        return source
    text, log = run_flowc_expand(source, "field")
    if log is not None:
        for line in log.splitlines():
            if line.startswith(_DIAG):
                raise SyntaxError(line[len(_DIAG):])
        raise SyntaxError("flowc field expansion failed: " + log.strip())
    return text
