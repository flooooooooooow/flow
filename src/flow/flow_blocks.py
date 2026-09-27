"""Lowering for `flow Name { ... }` blocks, done by flowc.

Spec: docs/vision/north-star.md sections 1 to 8. The lowering is written in
Flow (compiler/src/flow_blocks.flow) and runs inside flowc before parse: each
flow block becomes a struct and the functions Name_new, Name_init,
Name_derivs, Name_step, Name_default_dt, and Name_outputs / Name_check when
the flow has outputs / invariants, all tagged `@flow_api`. The Python host
asks flowc's FLOWC_EXPAND_ONLY=flow mode for that source and parses it
(Parser.parse), instead of keeping a second implementation. Parity with the
retired Python lowering is held by compiler/scripts/parity_flow_blocks.sh.
"""

from __future__ import annotations

import re

from .field_dsl import run_flowc_expand

_HEAD_RE = re.compile(r"\bflow\s+\w+\s*\{")
_DIAG = "flowc flow: "
_HINT = "flowc flow hint: "
_AT_RE = re.compile(r"^Error: (.*) at line (\d+)(?:, column (\d+))?$", re.DOTALL)


def has_flow_blocks(source: str) -> bool:
    return bool(_HEAD_RE.search(source))


def expand_flow_blocks(source: str) -> str:
    """Source with every flow block lowered. Raises FlowSyntaxError with the
    line, column and hint flowc reports."""
    from .parser import FlowSyntaxError

    if not has_flow_blocks(source):
        return source
    text, log = run_flowc_expand(source, "flow")
    if log is None:
        return text
    lines = log.splitlines()
    msg = next((ln[len(_DIAG):] for ln in lines if ln.startswith(_DIAG)), None)
    hint = next((ln[len(_HINT):] for ln in lines if ln.startswith(_HINT)), None)
    if msg is None:
        raise SyntaxError("flowc flow expansion failed: " + log.strip())
    m = _AT_RE.match(msg)
    if m is None:
        if msg.startswith("Error: "):
            raise FlowSyntaxError(msg[len("Error: "):], suggestion=hint)
        raise SyntaxError(msg)
    column = int(m.group(3)) if m.group(3) else None
    raise FlowSyntaxError(
        m.group(1), line=int(m.group(2)), column=column, source=source,
        suggestion=hint,
    )
