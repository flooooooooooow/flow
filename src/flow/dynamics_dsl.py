"""Dynamical-systems DSL (dsys, horizon, sense, ga evolve, closed, analyze,
wfc, couple, guide, represent), expanded by flowc.

The expander is written in Flow (compiler/src/dynamics_dsl.flow) and runs
inside flowc before parse. The Python host calls flowc's FLOWC_EXPAND_ONLY
mode instead of keeping a second implementation. The syntax is described in
docs/language/dynamics-dsl.md; parity with the retired Python expander is
held by compiler/scripts/parity_dynamics_dsl.sh.
"""

from __future__ import annotations

import re

from .field_dsl import run_flowc_expand

_DIAG = "flowc dynamics: "
_NS = r"(?:(?:dyn|dynamics)\.)?"
_HEAD_RE = re.compile(
    rf"^\s*{_NS}(?:dsys\s+\w+|horizon\s+\w+|sense\s+on\s+|ga\s+evolve\s+"
    rf"|closed\s+\w+|analyze\s+\w+|wfc\s+field\s+|couple\s+\w+|guide\s+\w+)"
    r"|^\s*(?:dyn|dynamics)\s*\{|^\s*represent\s+\w+",
    re.MULTILINE,
)


def has_dynamics_dsl(source: str) -> bool:
    return bool(_HEAD_RE.search(source))


def expand_dynamics_dsl(source: str) -> str:
    if not has_dynamics_dsl(source):
        return source
    text, log = run_flowc_expand(source, "dynamics")
    if log is not None:
        lines = log.splitlines()
        for i, line in enumerate(lines):
            if line.startswith(_DIAG):
                raise SyntaxError("\n".join([line[len(_DIAG):]] + lines[i + 1:]))
        raise SyntaxError("flowc dynamics expansion failed: " + log.strip())
    return text
