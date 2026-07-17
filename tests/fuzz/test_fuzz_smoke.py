"""Fast fuzzing smoke tests for CI.

Each target runs a short, seeded, deterministic budget (default 5s, override
with FLOW_FUZZ_SMOKE_SECONDS). A crash class already recorded in
crashes/known_crashes.json is tolerated (it is tracked as a backlog item and
replayed by test_crash_regressions.py); any NEW crash class fails the test.

For longer local/CI campaigns use:  python3 tests/fuzz/run_fuzz.py --seconds 300
"""

from __future__ import annotations

import json
import os

import pytest

from tests.fuzz.harness import CRASH_DIR, TARGETS

SMOKE_SECONDS = float(os.environ.get("FLOW_FUZZ_SMOKE_SECONDS", "5"))
SMOKE_SEED = 99


def _known_crash_classes() -> set:
    manifest = CRASH_DIR / "known_crashes.json"
    if not manifest.exists():
        return set()
    data = json.loads(manifest.read_text(encoding="utf-8"))
    # match on (stage, exception): the exact frame can drift across refactors
    return {(entry["stage"], entry["exception"]) for entry in data.values()}


@pytest.mark.parametrize("target", sorted(TARGETS))
def test_fuzz_smoke(target):
    stats = TARGETS[target](SMOKE_SECONDS, SMOKE_SEED)
    assert stats.iterations > 0
    known = _known_crash_classes()
    new = [
        finding
        for finding in stats.findings.values()
        if (finding.stage, finding.exc_type) not in known
    ]
    details = "\n".join(
        f"  {finding.exc_type} at {finding.location} (stage {finding.stage}): "
        f"{finding.message[:100]}\n    repro: "
        f"{(finding.minimized or finding.input_text)[:160]!r}"
        for finding in new
    )
    assert not new, (
        f"fuzz target '{target}' found {len(new)} NEW crash class(es):\n{details}\n"
        "Minimize+record via: python3 tests/fuzz/run_fuzz.py --save"
    )
