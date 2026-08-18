"""Heading-id generation and the anchor half of the link checker."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from check_doc_links import heading_slug  # noqa: E402


# --------------------------------------------------------------------------
# heading_slug follows GitHub, including where that looks odd
# --------------------------------------------------------------------------

@pytest.mark.parametrize(
    "heading,slug",
    [
        ("Overview", "overview"),
        ("1. Lexical Structure", "1-lexical-structure"),
        ("3.6 Attributes", "36-attributes"),
        ("`flow` blocks", "flow-blocks"),
        ("Types & Values", "types--values"),
    ],
)
def test_heading_slug_matches_github(heading, slug):
    assert heading_slug(heading) == slug


@pytest.mark.parametrize(
    "heading,slug",
    [
        # A removed punctuation mark leaves the spaces either side, and GitHub
        # turns each into its own dash. Collapsing them is what made 11 anchors
        # resolve on GitHub and die on the published wiki.
        ("10. Domain / DSL Surfaces", "10-domain--dsl-surfaces"),
        ("4.4 Lambdas / Closures", "44-lambdas--closures"),
        ("5.6 Concurrency (language + stdlib)", "56-concurrency-language--stdlib"),
    ],
)
def test_runs_of_dashes_are_preserved(heading, slug):
    assert heading_slug(heading) == slug


def test_the_published_wiki_slugger_agrees_with_this_one():
    """site/wiki.js must not collapse dash runs either.

    The two implementations are in different languages, so the only thing
    holding them together is that neither collapses. Pin the JS source.
    """
    js = (ROOT / "site" / "wiki.js").read_text()
    body = js[js.index("function headingSlug"):]
    body = body[: body.index("\n}")]
    assert "/-+/g" not in body, (
        "site/wiki.js collapses runs of dashes again; that breaks every anchor "
        "into a heading containing punctuation"
    )
    assert "replace(/\\s/g, '-')" in body or 'replace(/\\s/g, "-")' in body


# --------------------------------------------------------------------------
# anchors_in
# --------------------------------------------------------------------------

def test_anchors_come_from_headings(tmp_path, monkeypatch):
    import check_doc_links

    page = tmp_path / "p.md"
    page.write_text("# Title\n\n## A Section\n\ntext\n\n### Deep One\n")
    monkeypatch.setattr(check_doc_links, "ROOT", tmp_path)
    check_doc_links._ANCHOR_CACHE.clear()
    found = check_doc_links.anchors_in("p.md")
    assert {"title", "a-section", "deep-one"} <= found


def test_repeated_headings_are_numbered(tmp_path, monkeypatch):
    import check_doc_links

    page = tmp_path / "p.md"
    page.write_text("## Notes\n\n## Notes\n\n## Notes\n")
    monkeypatch.setattr(check_doc_links, "ROOT", tmp_path)
    check_doc_links._ANCHOR_CACHE.clear()
    found = check_doc_links.anchors_in("p.md")
    assert {"notes", "notes-1", "notes-2"} <= found


def test_explicit_html_ids_count_as_anchors(tmp_path, monkeypatch):
    import check_doc_links

    page = tmp_path / "p.md"
    page.write_text('# T\n\n<a id="hand-written"></a>\n')
    monkeypatch.setattr(check_doc_links, "ROOT", tmp_path)
    check_doc_links._ANCHOR_CACHE.clear()
    assert "hand-written" in check_doc_links.anchors_in("p.md")


# --------------------------------------------------------------------------
# The repository as it stands
# --------------------------------------------------------------------------

def test_every_documented_anchor_resolves():
    """The whole point: no link points at a heading that is not there."""
    result = subprocess.run(
        [sys.executable, "scripts/check_doc_links.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "all relative links and fragments resolve" in result.stdout


def test_same_page_anchors_are_actually_checked():
    """`#` used to sit in the external-skip list, so 55 anchors went unchecked."""
    result = subprocess.run(
        [sys.executable, "scripts/check_doc_links.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    match = re.search(r"checked (\d+) link fragment", result.stdout)
    assert match and int(match.group(1)) > 100, result.stdout
