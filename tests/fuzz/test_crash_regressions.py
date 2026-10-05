"""Replay minimized fuzz repros from tests/fuzz/crashes/.

Each entry in crashes/known_crashes.json is a compiler crash found by
fuzzing (tracked as a backlog item on the Helm board).

- Open entries (no "status" key) are xfail-marked: they PASS (xfail) while
  the bug still reproduces and report XPASS once fixed -- at that point set
  "status": "fixed" on the manifest entry (keep the repro file: the input
  shape stays in the corpus and the class stops being suppressed by
  run_fuzz.py's known-crash bookkeeping).
- Fixed entries ("status": "fixed") are positive regression tests: the input
  must now be handled cleanly (parsed OK or rejected with a proper
  SyntaxError/FlowSyntaxError carrying a location), never a crash.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests.fuzz.harness import (
    CRASH_DIR,
    full_pipeline,
    parse_only,
    run_guarded,
)


def _load_cases(status: str):
    manifest = CRASH_DIR / "known_crashes.json"
    if not manifest.exists():
        return []
    data = json.loads(manifest.read_text(encoding="utf-8"))
    cases = []
    for fname, meta in sorted(data.items()):
        path = CRASH_DIR / fname
        if not path.exists():
            continue
        if meta.get("status", "open") != status:
            continue
        marks = ()
        if status == "open":
            marks = pytest.mark.xfail(
                reason=(
                    f"known fuzz crash: {meta['exception']} at "
                    f"{meta['location']}"
                ),
                strict=False,
            )
        cases.append(pytest.param(path, meta, id=fname, marks=marks))
    return cases


def _replay(path: Path, meta: dict):
    text = path.read_text(encoding="utf-8")
    runner = parse_only if meta["stage"] == "parse" else full_pipeline
    return run_guarded(lambda: runner(text))


@pytest.mark.parametrize("path,meta", _load_cases("open"))
def test_known_crash(path: Path, meta: dict):
    outcome, exc = _replay(path, meta)
    assert outcome in ("ok", "clean"), (
        f"still crashes: {type(exc).__name__ if exc else 'hang'}: "
        f"{str(exc)[:120] if exc else ''}"
    )


@pytest.mark.parametrize("path,meta", _load_cases("fixed"))
def test_fixed_crash_stays_fixed(path: Path, meta: dict):
    outcome, exc = _replay(path, meta)
    assert outcome in ("ok", "clean"), (
        f"regressed: {type(exc).__name__ if exc else 'hang'}: "
        f"{str(exc)[:120] if exc else ''}"
    )
    if outcome == "clean":
        # Clean rejection must be a real SyntaxError with a location.
        assert isinstance(exc, SyntaxError)
        line = getattr(exc, "line", None) or getattr(exc, "lineno", None)
        assert line is not None, "clean error must carry a line number"
