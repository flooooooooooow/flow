from __future__ import annotations

from pathlib import Path

import pytest

from tests.unit.compiler_helpers import compile_and_run, errors, needs_clang


ROOT = Path(__file__).resolve().parent
POSITIVE = sorted(ROOT.glob("[0-9][0-9]_*.flow"))
NEGATIVE = sorted((ROOT / "negative").glob("[0-9][0-9]_*.flow"))


def _source(path: Path) -> str:
    text = path.read_text()
    first = next((line.strip() for line in text.splitlines() if line.strip()), "")
    assert first.startswith("# spec:"), f"{path.name} has no specification marker"
    return text


@needs_clang
@pytest.mark.parametrize("fixture", POSITIVE, ids=lambda p: p.stem)
def test_stable_positive_fixture(fixture: Path) -> None:
    assert compile_and_run(_source(fixture)) == 42


@pytest.mark.parametrize("fixture", NEGATIVE, ids=lambda p: p.stem)
def test_stable_negative_fixture_is_rejected(fixture: Path) -> None:
    assert errors(_source(fixture)), f"{fixture.name} unexpectedly type-checks"


def test_conformance_corpus_is_not_empty() -> None:
    assert POSITIVE
    assert NEGATIVE
