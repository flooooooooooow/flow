"""The wiki nav manifest and the checks that keep it honest.

The checks live in the Flow program scripts/tools/wiki_nav, run through
scripts/wiki_nav.sh. The wiki build (scripts/build_wiki.sh) runs the same
validation before it writes the sidebar.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SHIM = ROOT / "scripts" / "wiki_nav.sh"


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["bash", str(SHIM), *args], cwd=ROOT, capture_output=True, text=True
    )


def lines(*args: str) -> list[str]:
    result = run(*args)
    return [line for line in result.stdout.splitlines() if line]


@pytest.fixture
def nav():
    return json.loads((ROOT / "docs" / "nav.json").read_text(encoding="utf-8"))


# --------------------------------------------------------------------------
# The real manifest
# --------------------------------------------------------------------------

def test_the_shipped_manifest_is_consistent_with_docs():
    # This is the check that would have caught project/PROJECT_STRUCTURE.md,
    # a sidebar entry pointing at a file that only exists under archive/.
    result = run("--problems")
    assert result.returncode == 0, result.stdout
    assert result.stdout == ""


def test_the_summary_reports_a_consistent_manifest():
    result = run()
    assert result.returncode == 0, result.stdout
    assert result.stdout.endswith("\nnav is consistent with docs/\n")


def _reachable(nav, prefix: str) -> set[str]:
    listed = set(lines("--listed"))
    unlisted = set(nav.get("unlisted", {}))
    pages = {p for p in lines("--pages") if p.startswith(prefix)}
    assert pages, f"no pages under {prefix}"
    return pages - listed - unlisted


def test_every_language_page_is_reachable_from_the_sidebar(nav):
    # A reference manual whose reference pages are not in the sidebar is a
    # reference manual you cannot use.
    assert _reachable(nav, "language/") == set()


def test_every_library_page_is_reachable_from_the_sidebar(nav):
    assert _reachable(nav, "library/") == set()


def test_unlisted_pages_all_carry_a_reason(nav):
    for path, reason in nav.get("unlisted", {}).items():
        assert str(reason).strip(), f"{path} is unlisted with no reason"


def test_sections_reference_declared_tabs(nav):
    tabs = {tab["id"] for tab in nav["tabs"]}
    assert all(section["tab"] in tabs for section in nav["sections"])


# --------------------------------------------------------------------------
# Validation catches the failures it exists for
# --------------------------------------------------------------------------

def _problems(tmp_path: Path, sections, unlisted=None, pages=()) -> list[str]:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "home.md").write_text("# home")
    for page in pages:
        (docs / page).write_text("# page")
    manifest = {
        "default": "home.md",
        "tabs": [{"id": "start", "label": "Start"}],
        "sections": sections,
        "unlisted": unlisted or {},
    }
    path = tmp_path / "nav.json"
    path.write_text(json.dumps(manifest))
    return lines("--manifest", str(path), "--docs", str(docs), "--problems")


def _home_only():
    return [{"id": "s", "tab": "start", "title": "S",
             "items": [{"label": "Home", "path": "home.md"}]}]


def test_a_nav_entry_pointing_at_nothing_is_a_failure(tmp_path):
    problems = _problems(
        tmp_path,
        [{"id": "s", "tab": "start", "title": "S", "items": [
            {"label": "Home", "path": "home.md"},
            {"label": "Ghost", "path": "does-not-exist.md"},
        ]}],
    )
    assert any("does-not-exist.md" in p for p in problems)


def test_a_page_in_no_section_is_a_failure(tmp_path):
    problems = _problems(tmp_path, _home_only(), pages=["stranded.md"])
    assert any("stranded.md" in p for p in problems)


def test_an_unlisted_page_with_a_reason_is_accepted(tmp_path):
    problems = _problems(
        tmp_path,
        _home_only(),
        unlisted={"internal.md": "internal runbook, not reader documentation"},
        pages=["internal.md"],
    )
    assert problems == []


def test_an_unlisted_page_with_a_blank_reason_is_a_failure(tmp_path):
    problems = _problems(
        tmp_path, _home_only(), unlisted={"internal.md": "   "}, pages=["internal.md"]
    )
    assert any("written reason" in p for p in problems)


def test_a_page_cannot_be_both_listed_and_unlisted(tmp_path):
    problems = _problems(tmp_path, _home_only(), unlisted={"home.md": "some reason"})
    assert any("both in the nav" in p for p in problems)


def test_a_section_naming_an_unknown_tab_is_a_failure(tmp_path):
    problems = _problems(
        tmp_path,
        [{"id": "s", "tab": "nope", "title": "S",
          "items": [{"label": "Home", "path": "home.md"}]}],
    )
    assert any("does not exist" in p for p in problems)


def test_build_generated_pages_do_not_have_to_exist_on_disk(tmp_path):
    # releases.md and friends are written into build/wiki from sources outside
    # docs/, so requiring them here would fail every build.
    problems = _problems(
        tmp_path,
        [{"id": "s", "tab": "start", "title": "S", "items": [
            {"label": "Home", "path": "home.md"},
            {"label": "Releases", "path": "releases.md"},
        ]}],
    )
    assert problems == []


# --------------------------------------------------------------------------
# Derived views
# --------------------------------------------------------------------------

def test_generated_sections_are_filled_in_at_build_time():
    result = run("--sections", "--fill", "euclid", "Book I", "x.md")
    built = json.loads(result.stdout)
    euclid = next(s for s in built if s["id"] == "proofs-euclid")
    assert euclid["items"] == [{"label": "Book I", "path": "x.md"}]
    assert "generated" not in euclid


def test_search_category_follows_the_tab_a_page_sits_under():
    def category(path: str) -> str:
        return run("--category", path).stdout.strip()

    assert category("language/types.md") == "reference"
    assert category("library/memory.md") == "reference"
    assert category("tutorials/beginner.md") == "tutorial"
    assert category("DEVELOPMENT.md") == "tooling"


def test_an_unknown_page_falls_back_to_guide():
    assert run("--category", "no/such/page.md").stdout.strip() == "guide"


def test_the_shipped_manifest_is_valid_json():
    raw = (ROOT / "docs" / "nav.json").read_text()
    data = json.loads(raw)
    assert data["sections"] and data["tabs"]
