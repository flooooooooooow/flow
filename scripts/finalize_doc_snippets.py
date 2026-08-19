#!/usr/bin/env python3
"""One-time deterministic cleanup for documentation snippets.

This repairs known stale fragments that were exposed by check_doc_flow_snippets.
It does not classify arbitrary failures. Only explicitly schematic/future pages
are mass-retagged; current reference examples are replaced with complete units.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FENCE = re.compile(r"^(?P<indent>\s{0,3})(?P<mark>`{3,}|~{3,})(?P<info>.*?)(?P<eol>\r?\n)?$")


def replace(path: str, old: str, new: str) -> None:
    p = ROOT / path
    text = p.read_text(encoding="utf-8")
    if old in text:
        p.write_text(text.replace(old, new, 1), encoding="utf-8")


def retag_generic(path: str, label: str) -> None:
    """Retag generic text/untyped fences in an explicitly non-standalone page."""
    p = ROOT / path
    lines = p.read_text(encoding="utf-8").splitlines(keepends=True)
    out: list[str] = []
    for line in lines:
        m = FENCE.match(line)
        if m and m.group("info").strip() in {"", "text"}:
            # Only retag openings; closing fences have an empty info string too,
            # so track whether we are currently inside a fence.
            pass
        out.append(line)

    # A second pass with fence state keeps closing delimiters untouched.
    inside = False
    result: list[str] = []
    for line in lines:
        m = FENCE.match(line)
        if not m:
            result.append(line)
            continue
        if inside:
            inside = False
            result.append(line)
            continue
        inside = True
        info = m.group("info").strip()
        if info in {"", "text"}:
            eol = m.group("eol") or ""
            line = f"{m.group('indent')}{m.group('mark')}{label}{eol}"
        result.append(line)
    p.write_text("".join(result), encoding="utf-8")


def main() -> int:
    # README syntax cards are notation, not standalone programs.
    replace(
        "README.md",
        "### Types\n\n```\nPrimitives:  i32, i64, f32, f64, bool, string, void\nPointers:    ptr<T>, ptr<void>\nArrays:      array<T, N>\nGenerics:    function identity<T>(x: T) -> T\n```",
        "### Types\n\n```flow-pseudocode\nPrimitives:  i32, i64, f32, f64, bool, string, void\nPointers:    ptr<T>, ptr<void>\nArrays:      array<T, N>\nGenerics:    function identity<T>(x: T) -> T\n```",
    )

    # AI handbook: replace orphan current fragments with complete units.
    replace(
        "docs/AI_FLOW_HANDBOOK.md",
        "```text\nlet mut position: f64 = 0.0\nposition = position + velocity * dt\n```",
        "```flow\nfunction advance(position: f64, velocity: f64, dt: f64) -> f64 {\n    let mut next: f64 = position\n    next = next + velocity * dt\n    return next\n}\n```",
    )
    replace(
        "docs/AI_FLOW_HANDBOOK.md",
        "```text\nlet mut p: Pendulum = Pendulum_new()\nPendulum_step(&p, 0.001)\n```",
        "The generated constructor/step API is exercised by the complete program `examples/evolution/pendulum_evolves.flow`.",
    )
    replace(
        "docs/AI_FLOW_HANDBOOK.md",
        "```text\nwhen height reaches 0.0 {\n    velocity becomes -restitution * velocity\n    height becomes 0.0\n}\n```",
        "```flow\nflow HandbookBall {\n    state height: f64 = 2.0\n    state velocity: f64 = 0.0\n    param gravity: f64 = 9.81\n    param restitution: f64 = 0.8\n    height evolves as velocity\n    velocity evolves as -gravity\n    when height reaches 0.0 {\n        velocity becomes -restitution * velocity\n        height becomes 0.0\n    }\n}\n```",
    )
    replace(
        "docs/AI_FLOW_HANDBOOK.md",
        "```text\nhandle Log with QuietLog {\n    do_work()\n}\n```",
        "```flow\neffect ScopedLog {\n    info(msg: string) -> void,\n}\ncapability ScopedQuietLog {\n    effect ScopedLog,\n    function info(msg: string) -> void { },\n}\nfunction scoped_work() -> void with ScopedLog { ScopedLog.info(\"work\") }\nfunction scoped_handler_demo() -> i32 {\n    handle ScopedLog with ScopedQuietLog { scoped_work() }\n    return 0\n}\n```",
    )
    replace(
        "docs/AI_FLOW_HANDBOOK.md",
        "```text\n@max_iterations(1000)\nwhile condition {\n    step()\n}\n```",
        "```flow\nfunction bounded_iteration(limit: i32) -> i32 {\n    let mut i: i32 = 0\n    @max_iterations(1000)\n    while i < limit { i = i + 1 }\n    return i\n}\n```",
    )

    # Language spec: repair the known disconnected current examples.
    replace(
        "docs/LANGUAGE_SPEC.md",
        "```text\nlet raw: i64 = 42\nlet id: UserId = raw as UserId\nlet back: i64 = id as i64\n```",
        "```flow\ndistinct type SpecUserId = i64\nfunction distinct_roundtrip(raw: i64) -> i64 {\n    let id: SpecUserId = raw as SpecUserId\n    return id as i64\n}\n```",
    )
    replace(
        "docs/LANGUAGE_SPEC.md",
        "```text\nxs |> sort                     # ascending, stable\nxs |> sort(desc)               # descending, stable\nxs |> sortBy([asc .key, desc .tie])\nxs |> sort unique              # sort then compact adjacent equals\nlet i: i32 = xs |> find(target) # binary search; -1 if absent\n```",
        "```flow\nfunction ordering_spec() -> i32 {\n    let mut xs: array<i32, 5> = [3, 1, 4, 1, 5]\n    xs |> sort\n    return xs |> find(4)\n}\n```",
    )
    replace(
        "docs/LANGUAGE_SPEC.md",
        "```text\nlet x: i32 = if n > 0 { n } else { -n }\n```",
        "```flow\nfunction spec_abs(n: i32) -> i32 {\n    let x: i32 = if n > 0 { n } else { -n }\n    return x\n}\n```",
    )
    replace(
        "docs/LANGUAGE_SPEC.md",
        "```text\nif x > 0 {\n    return 1\n} elif x < 0 {\n    return -1\n} else {\n    return 0\n}\n```",
        "```flow\nfunction spec_sign(x: i32) -> i32 {\n    if x > 0 { return 1 }\n    elif x < 0 { return -1 }\n    else { return 0 }\n}\n```",
    )
    replace(
        "docs/LANGUAGE_SPEC.md",
        "```text\nlet mut i = 0\nwhile i < 10 {\n    i = i + 1\n}\n```",
        "```flow\nfunction spec_while() -> i32 {\n    let mut i: i32 = 0\n    while i < 10 { i = i + 1 }\n    return i\n}\n```",
    )
    replace(
        "docs/LANGUAGE_SPEC.md",
        "```text\nhandle Log with ConsoleLogger {\n    Log.emit(\"Hello from effects!\")\n}\n```",
        "```flow\neffect SpecLog { emit(message: string) -> void, }\ncapability SpecLogger {\n    effect SpecLog,\n    function emit(message: string) -> void { println(message) },\n}\nfunction spec_handle() -> i32 {\n    handle SpecLog with SpecLogger { SpecLog.emit(\"hello\") }\n    return 0\n}\n```",
    )
    replace(
        "docs/LANGUAGE_SPEC.md",
        "```text\nfunction greet(name: string) -> void with Log {\n    Log.emit(name)\n}\n```",
        "```flow\neffect RowLog { emit(message: string) -> void, }\nfunction row_greet(name: string) -> void with RowLog { RowLog.emit(name) }\n```",
    )

    # Clearly schematic/future documents: make their non-current nature explicit.
    retag_generic("docs/vision/north-star.md", "flow-future")
    retag_generic("docs/project/archive/PROJECT_STRUCTURE.md", "flow-pseudocode")
    retag_generic("docs/project/pattern-adoption.md", "flow-pseudocode")
    retag_generic("docs/research/FLOW_RESEARCH_PAPER.md", "flow-pseudocode")
    retag_generic("docs/language/graphics.md", "flow-pseudocode")
    retag_generic("docs/language/graphics-3d.md", "flow-pseudocode")
    retag_generic("examples/neuro/README.md", "flow-pseudocode")

    # A solver line is valid only inside a flow declaration; label the isolated
    # notation fragment rather than pretending it is a standalone program.
    replace(
        "docs/tutorials/evolution.md",
        "```text\nsolver { dt 5 ms  method rk4 }\n```",
        "```flow-pseudocode\nsolver { dt 5 ms  method rk4 }\n```",
    )

    # Make the atlas model itself executable instead of leaving a hybrid event
    # with semicolon-separated resets and an undeclared input.
    replace(
        "docs/project/example-atlas.md",
        "```text\nflow Neuron {\n    state v: f64 = -65.0\n    state u: f64 = -13.0\n    param a: f64 = 0.02\n\n    v evolves as 0.04 * v * v + 5.0 * v + 140.0 - u + I\n    u evolves as a * (0.2 * v - u)\n\n    when v reaches 30.0 { v becomes -65.0; u becomes u + 8.0 }\n}\n```",
        "```flow\nflow Neuron {\n    state v: f64 = -65.0\n    state u: f64 = -13.0\n    input I: f64\n    param a: f64 = 0.02\n    v evolves as 0.04 * v * v + 5.0 * v + 140.0 - u + I\n    u evolves as a * (0.2 * v - u)\n    when v reaches 30.0 {\n        v becomes -65.0\n        u becomes u + 8.0\n    }\n}\n```",
    )

    print("documentation snippet finalization applied")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
