"""Replay minimized fuzz repros from tests/fuzz/crashes/.

Each entry in crashes/known_crashes.json is a known compiler crash found by
fuzzing (tracked as a backlog item on the Helm board). The test is
xfail-marked: it PASSES (xfail) while the bug still reproduces, and reports
XPASS once the compiler handles the input cleanly -- at that point delete the
repro + manifest entry and close the backlog task.
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


def _load_cases():
    manifest = CRASH_DIR / "known_crashes.json"
    if not manifest.exists():
        return []
    data = json.loads(manifest.read_text(encoding="utf-8"))
    cases = []
    for fname, meta in sorted(data.items()):
        path = CRASH_DIR / fname
        if path.exists():
            cases.append(
                pytest.param(
                    path,
                    meta,
                    id=fname,
                    marks=pytest.mark.xfail(
                        reason=(
                            f"known fuzz crash: {meta['exception']} at "
                            f"{meta['location']}"
                        ),
                        strict=False,
                    ),
                )
            )
    return cases


@pytest.mark.parametrize("path,meta", _load_cases())
def test_known_crash(path: Path, meta: dict):
    text = path.read_text(encoding="utf-8")
    runner = parse_only if meta["stage"] == "parse" else full_pipeline
    outcome, exc = run_guarded(lambda: runner(text))
    assert outcome in ("ok", "clean"), (
        f"still crashes: {type(exc).__name__ if exc else 'hang'}: "
        f"{str(exc)[:120] if exc else ''}"
    )
