#!/usr/bin/env python3
"""Opt-in per-phase compile profiling for the Python host compiler (#735).

The profiler measures wall time for the compilation phases that are cleanly
identifiable in ``flow.transpiler``:

  startup         fixed cost: interpreter + compiler-module import + argparse,
                  measured from process/module load to the first real work
  source_read     reading the root source file off disk
  parse_resolve   lexing, parsing and import resolution (see note below)
  typecheck       the TypeChecker pass
  monomorphize    generic expansion
  codegen         IR/lowering and C or MLIR generation
  external_compile   the C toolchain (clang) invocation, timed by the driver
  process_launch     running the produced executable, timed by the driver

Note on parse vs import resolution: the current pipeline lexes and parses each
module inside ``resolve_modules``. Parsing is not a separate call in the host
pipeline, so parse time is folded into the ``parse_resolve`` phase rather than
forcing a fragile hook to split it out.

The last two phases run in separate processes (clang and the executable) that
the transpiler launches through the bash driver, so they are timed by the
driver and are absent from a single ``python -m flow.transpiler`` report.

Everything here is OFF unless ``FLOW_PROFILE`` is set to a truthy value, so a
normal compile is unaffected.
"""

from __future__ import annotations

import json
import os
import sys
import time
from contextlib import contextmanager

# Canonical phase order. Reports print in this order regardless of the order in
# which phases were recorded.
PHASE_ORDER = [
    "startup",
    "source_read",
    "parse_resolve",
    "typecheck",
    "monomorphize",
    "codegen",
    "external_compile",
    "process_launch",
]

# Single-line marker so the machine-readable report is easy to grep out of an
# interleaved stderr stream.
REPORT_MARKER = "[flow-profile]"

_TRUTHY_OFF = {"", "0", "false", "no", "off"}


def profiling_mode() -> str:
    """Return "off", "text" or "json" from the FLOW_PROFILE env var."""
    val = os.environ.get("FLOW_PROFILE", "").strip().lower()
    if val in _TRUTHY_OFF:
        return "off"
    if val == "json":
        return "json"
    return "text"


def profiling_enabled() -> bool:
    return profiling_mode() != "off"


def count_ast_nodes(declarations) -> int:
    """Count AST nodes reachable from ``declarations``.

    Walks the object graph and counts each distinct instance whose class lives
    in ``flow.parser`` (the AST/token module). Cycles and shared subtrees are
    counted once via an identity set.
    """
    seen: set[int] = set()
    count = 0
    stack = list(declarations)
    while stack:
        obj = stack.pop()
        oid = id(obj)
        if oid in seen:
            continue
        seen.add(oid)
        if isinstance(obj, (list, tuple, set, frozenset)):
            stack.extend(obj)
            continue
        if isinstance(obj, dict):
            stack.extend(obj.keys())
            stack.extend(obj.values())
            continue
        if type(obj).__module__ == "flow.parser":
            count += 1
            fields = getattr(obj, "__dict__", None)
            if fields:
                stack.extend(fields.values())
    return count


def count_source_loc(text: str) -> int:
    """Non-blank source lines."""
    return sum(1 for line in text.splitlines() if line.strip())


class CompileProfiler:
    """Accumulates per-phase wall time and source/AST size metrics."""

    def __init__(self) -> None:
        self.phases: dict[str, float] = {}
        self._order: list[str] = []
        self.source_loc = 0
        self.ast_nodes = 0

    # -- recording ---------------------------------------------------------
    def record(self, name: str, seconds: float) -> None:
        if seconds < 0:
            seconds = 0.0
        self.phases[name] = self.phases.get(name, 0.0) + seconds
        if name not in self._order:
            self._order.append(name)

    def mark_startup(self, process_start: float) -> None:
        """Record fixed startup cost from ``process_start`` (a monotonic ref)."""
        self.record("startup", time.monotonic() - process_start)

    @contextmanager
    def phase(self, name: str):
        start = time.monotonic()
        try:
            yield
        finally:
            self.record(name, time.monotonic() - start)

    def set_source_loc(self, loc: int) -> None:
        self.source_loc = max(0, int(loc))

    def set_ast_nodes(self, nodes: int) -> None:
        self.ast_nodes = max(0, int(nodes))

    # -- reporting ---------------------------------------------------------
    def ordered_phases(self) -> list[tuple[str, float]]:
        """Phases in canonical order, then any extras in insertion order."""
        result: list[tuple[str, float]] = []
        for name in PHASE_ORDER:
            if name in self.phases:
                result.append((name, self.phases[name]))
        for name in self._order:
            if name not in PHASE_ORDER:
                result.append((name, self.phases[name]))
        return result

    def total_seconds(self) -> float:
        return sum(self.phases.values())

    def report_dict(self) -> dict:
        ordered = self.ordered_phases()
        total = self.total_seconds()
        startup = self.phases.get("startup", 0.0)
        return {
            "schema": "flow-compile-profile/1",
            "phases": [
                {"name": name, "seconds": seconds}
                for name, seconds in ordered
            ],
            "phase_order": [name for name, _ in ordered],
            "source_loc": self.source_loc,
            "ast_nodes": self.ast_nodes,
            "total_seconds": total,
            "startup_seconds": startup,
            "loc_per_second": (self.source_loc / total) if total > 0 else 0.0,
            "ast_nodes_per_second": (self.ast_nodes / total) if total > 0 else 0.0,
        }

    def format_text(self) -> str:
        data = self.report_dict()
        lines = ["Compile profile (per-phase wall time):"]
        total = data["total_seconds"]
        for entry in data["phases"]:
            name = entry["name"]
            secs = entry["seconds"]
            pct = (secs / total * 100.0) if total > 0 else 0.0
            lines.append(f"  {name:<16} {secs * 1000:9.3f} ms  {pct:5.1f}%")
        lines.append(f"  {'total':<16} {total * 1000:9.3f} ms")
        lines.append(
            f"  startup (fixed)  {data['startup_seconds'] * 1000:9.3f} ms"
        )
        lines.append(
            f"  source LOC {data['source_loc']} "
            f"({data['loc_per_second']:.0f} LOC/s); "
            f"AST nodes {data['ast_nodes']} "
            f"({data['ast_nodes_per_second']:.0f} nodes/s)"
        )
        return "\n".join(lines)

    def emit(self, stream=None, mode: str | None = None) -> None:
        if stream is None:
            stream = sys.stderr
        if mode is None:
            mode = profiling_mode()
        if mode == "off":
            return
        if mode == "text":
            print(self.format_text(), file=stream)
        print(
            f"{REPORT_MARKER} " + json.dumps(self.report_dict()),
            file=stream,
        )
        stream.flush()


def _time_subprocess(phase: str, cmd: list[str]) -> int:
    """Run ``cmd``, timing only the subprocess, and emit a profile line.

    Used by the bash driver to time the two out-of-process phases
    (``external_compile``, ``process_launch``) around clang and the produced
    executable. Python interpreter startup is outside the measured window, so
    the reported time is the subprocess wall time. stdout/stderr are inherited
    so the wrapped command behaves normally.
    """
    import subprocess

    prof = CompileProfiler()
    start = time.monotonic()
    proc = subprocess.run(cmd)
    prof.record(phase, time.monotonic() - start)
    if profiling_enabled():
        # Always a single JSON line here; the transpiler already prints the
        # human-readable table for its own phases.
        prof.emit(mode="json")
    return proc.returncode


def main(argv: list[str] | None = None) -> int:
    """CLI: ``python -m flow.compile_profiling <phase> <cmd> [args...]``."""
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) < 2:
        print(
            "usage: python -m flow.compile_profiling <phase> <cmd> [args...]",
            file=sys.stderr,
        )
        return 2
    phase = args[0]
    cmd = args[1:]
    return _time_subprocess(phase, cmd)


if __name__ == "__main__":
    sys.exit(main())
