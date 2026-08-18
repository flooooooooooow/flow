"""The wiki nav manifest and the checks that keep it honest."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import wiki_nav  # noqa: E402


@pytest.fixture
def nav():
    return wiki_nav.load()


# --------------------------------------------------------------------------
# The real manifest
# --------------------------------------------------------------------------

def test_the_shipped_manifest_is_consistent_with_docs(nav):
    # This is the check that would have caught project/PROJECT_STRUCTURE.md,
    # a sidebar entry pointing at a file that only exists under archive/.
    assert wiki_nav.validate(nav) == []


def test_every_language_page_is_reachable_from_the_sidebar(nav):
    # The point of the exercise: a reference manual whose reference pages are
    # not in the sidebar is a reference manual you cannot use.
    listed = wiki_nav.nav_paths(nav)
    unlisted = set(nav.get("unlisted", {}))
    language_pages = {
        p for p in wiki_nav.doc_pages() if p.startswith("language/")
    }
    assert language_pages - listed - unlisted == set()


def test_every_library_page_is_reachable_from_the_sidebar(nav):
    listed = wiki_nav.nav_paths(nav)
    unlisted = set(nav.get("unlisted", {}))
    pages = {p for p in wiki_nav.doc_pages() if p.startswith("library/")}
    assert pages - listed - unlisted == set()


def test_unlisted_pages_all_carry_a_reason(nav):
    for path, reason in nav.get("unlisted", {}).items():
        assert str(reason).strip(), f"{path} is unlisted with no reason"


def test_sections_reference_declared_tabs(nav):
    tabs = {tab["id"] for tab in nav["tabs"]}
    assert all(section["tab"] in tabs for section in nav["sections"])


# --------------------------------------------------------------------------
# Validation catches the failures it exists for
# --------------------------------------------------------------------------

def _minimal(tmp_path: Path, sections, unlisted=None) -> tuple[dict, Path]:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "home.md").write_text("# home")
    manifest = {
        "default": "home.md",
        "tabs": [{"id": "start", "label": "Start"}],
        "sections": sections,
        "unlisted": unlisted or {},
    }
    return manifest, docs


def test_a_nav_entry_pointing_at_nothing_is_a_failure(tmp_path):
    manifest, docs = _minimal(
        tmp_path,
        [{"id": "s", "tab": "start", "title": "S", "items": [
            {"label": "Home", "path": "home.md"},
            {"label": "Ghost", "path": "does-not-exist.md"},
        ]}],
    )
    problems = wiki_nav.validate(manifest, docs)
    assert any("does-not-exist.md" in p for p in problems)


def test_a_page_in_no_section_is_a_failure(tmp_path):
    manifest, docs = _minimal(
        tmp_path,
        [{"id": "s", "tab": "start", "title": "S",
          "items": [{"label": "Home", "path": "home.md"}]}],
    )
    (docs / "stranded.md").write_text("# nobody links here")
    problems = wiki_nav.validate(manifest, docs)
    assert any("stranded.md" in p for p in problems)


def test_an_unlisted_page_with_a_reason_is_accepted(tmp_path):
    manifest, docs = _minimal(
        tmp_path,
        [{"id": "s", "tab": "start", "title": "S",
          "items": [{"label": "Home", "path": "home.md"}]}],
        unlisted={"internal.md": "internal runbook, not reader documentation"},
    )
    (docs / "internal.md").write_text("# internal")
    assert wiki_nav.validate(manifest, docs) == []


def test_an_unlisted_page_with_a_blank_reason_is_a_failure(tmp_path):
    manifest, docs = _minimal(
        tmp_path,
        [{"id": "s", "tab": "start", "title": "S",
          "items": [{"label": "Home", "path": "home.md"}]}],
        unlisted={"internal.md": "   "},
    )
    (docs / "internal.md").write_text("# internal")
    assert any("written reason" in p for p in wiki_nav.validate(manifest, docs))


def test_a_page_cannot_be_both_listed_and_unlisted(tmp_path):
    manifest, docs = _minimal(
        tmp_path,
        [{"id": "s", "tab": "start", "title": "S",
          "items": [{"label": "Home", "path": "home.md"}]}],
        unlisted={"home.md": "some reason"},
    )
    assert any("both in the nav" in p for p in wiki_nav.validate(manifest, docs))


def test_a_section_naming_an_unknown_tab_is_a_failure(tmp_path):
    manifest, docs = _minimal(
        tmp_path,
        [{"id": "s", "tab": "nope", "title": "S",
          "items": [{"label": "Home", "path": "home.md"}]}],
    )
    assert any("does not exist" in p for p in wiki_nav.validate(manifest, docs))


def test_build_generated_pages_do_not_have_to_exist_on_disk(tmp_path):
    # releases.md and friends are written into build/wiki from sources outside
    # docs/, so requiring them here would fail every build.
    manifest, docs = _minimal(
        tmp_path,
        [{"id": "s", "tab": "start", "title": "S", "items": [
            {"label": "Home", "path": "home.md"},
            {"label": "Releases", "path": "releases.md"},
        ]}],
    )
    assert wiki_nav.validate(manifest, docs) == []


# --------------------------------------------------------------------------
# Derived views
# --------------------------------------------------------------------------

def test_generated_sections_are_filled_in_at_build_time(nav):
    built = wiki_nav.sections_for_build(
        nav, {"euclid": [{"label": "Book I", "path": "x.md"}], "proofs": []}
    )
    euclid = next(s for s in built if s["id"] == "proofs-euclid")
    assert euclid["items"] == [{"label": "Book I", "path": "x.md"}]
    assert "generated" not in euclid


def test_search_category_follows_the_tab_a_page_sits_under(nav):
    assert wiki_nav.category_for("language/types.md", nav) == "reference"
    assert wiki_nav.category_for("library/core.md", nav) == "reference"
    assert wiki_nav.category_for("tutorials/beginner.md", nav) == "tutorial"
    assert wiki_nav.category_for("DEVELOPMENT.md", nav) == "tooling"


def test_an_unknown_page_falls_back_to_guide(nav):
    assert wiki_nav.category_for("no/such/page.md", nav) == "guide"


def test_the_shipped_manifest_is_valid_json():
    raw = (ROOT / "docs" / "nav.json").read_text()
    data = json.loads(raw)
    assert data["sections"] and data["tabs"]
