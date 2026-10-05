from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

import pytest

from tests.unit.compiler_helpers import compile_and_run, errors, needs_clang


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
POSITIVE = sorted(ROOT.glob("[0-9][0-9]_*.flow"))
# Negative fixtures intentionally do not end in `.flow`; `./flow test --tier2`
# recursively treats every tracked `.flow` file as a positive compile fixture.
NEGATIVE = sorted((ROOT / "negative").glob("[0-9][0-9]_*.flow.txt"))


def _source(path: Path) -> str:
    text = path.read_text()
    first = next((line.strip() for line in text.splitlines() if line.strip()), "")
    assert first.startswith("# spec:"), f"{path.name} has no specification marker"
    return text


def _flowc_driver() -> Path:
    proc = subprocess.run(
        ["bash", "compiler/scripts/ensure_flowc.sh"],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=True,
    )
    driver = (REPO / proc.stdout.strip()).resolve()
    assert driver.is_file(), f"ensure_flowc returned no driver: {proc.stdout!r}"
    return driver


@needs_clang
@pytest.mark.parametrize("fixture", POSITIVE, ids=lambda p: p.stem)
def test_stable_positive_fixture(fixture: Path) -> None:
    assert compile_and_run(_source(fixture)) == 42


@needs_clang
@pytest.mark.parametrize("fixture", POSITIVE, ids=lambda p: p.stem)
def test_stable_positive_fixture_matches_flowc(fixture: Path) -> None:
    driver = _flowc_driver()
    with tempfile.TemporaryDirectory() as td:
        c_path = Path(td) / "fixture.c"
        bin_path = Path(td) / "fixture"
        lower = subprocess.run(
            [str(driver), str(fixture), str(c_path)],
            cwd=REPO,
            capture_output=True,
            text=True,
        )
        assert lower.returncode == 0, (
            f"flowc failed for {fixture.name}:\n{lower.stderr}\n{lower.stdout}"
        )
        build = subprocess.run(
            [os.environ.get("CC", "cc"), "-O0", "-o", str(bin_path), str(c_path), "-lm"],
            cwd=REPO,
            capture_output=True,
            text=True,
        )
        assert build.returncode == 0, (
            f"C emitted by flowc did not compile for {fixture.name}:\n{build.stderr}"
        )
        run = subprocess.run([str(bin_path)], capture_output=True)
        assert run.returncode == 42, (
            f"flowc semantic divergence for {fixture.name}: expected exit 42, "
            f"got {run.returncode}"
        )


@pytest.mark.parametrize("fixture", NEGATIVE, ids=lambda p: p.name.removesuffix(".flow.txt"))
def test_stable_negative_fixture_is_rejected(fixture: Path) -> None:
    assert errors(_source(fixture)), f"{fixture.name} unexpectedly type-checks"


def test_conformance_corpus_is_not_empty() -> None:
    assert POSITIVE
    assert NEGATIVE
