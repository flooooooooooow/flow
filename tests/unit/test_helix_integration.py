"""Unit tests for Helix editor integration files."""

import os
from pathlib import Path
import tomllib


REPO_ROOT = Path(__file__).resolve().parents[2]
HELIX_DIR = REPO_ROOT / "third_party" / "integrations" / "helix"


def test_helix_integration_files_exist():
    """Verify that all required Helix integration files exist."""
    languages_toml = HELIX_DIR / "languages.toml"
    highlights_scm = HELIX_DIR / "queries" / "highlights.scm"
    readme_md = HELIX_DIR / "README.md"
    doc_helix = REPO_ROOT / "docs" / "project" / "helix.md"

    assert languages_toml.is_file(), f"Missing {languages_toml}"
    assert highlights_scm.is_file(), f"Missing {highlights_scm}"
    assert readme_md.is_file(), f"Missing {readme_md}"
    assert doc_helix.is_file(), f"Missing {doc_helix}"


def test_helix_languages_toml_validity():
    """Verify that languages.toml is valid TOML and configures Flow properly."""
    languages_toml = HELIX_DIR / "languages.toml"
    content = languages_toml.read_text(encoding="utf-8")
    parsed = tomllib.loads(content)

    assert "language" in parsed, "languages.toml missing [[language]]"
    flow_lang = None
    for lang in parsed["language"]:
        if lang.get("name") == "flow":
            flow_lang = lang
            break

    assert flow_lang is not None, "Flow language entry not found in languages.toml"
    assert flow_lang.get("scope") == "source.flow"
    assert "flow" in flow_lang.get("file-types", [])
    assert "flow-lsp" in flow_lang.get("language-servers", [])


def test_helix_highlights_scm_queries():
    """Verify key Flow syntax tokens are captured in highlights.scm."""
    highlights_scm = HELIX_DIR / "queries" / "highlights.scm"
    content = highlights_scm.read_text(encoding="utf-8")

    expected_captures = [
        "@keyword.control",
        "@keyword.storage",
        "@keyword.operator",
        "@type.builtin",
        "@constant.builtin",
        "@comment",
        "@string",
        "@function",
        "@operator",
    ]

    for capture in expected_captures:
        assert capture in content, f"Missing capture '{capture}' in highlights.scm"

    expected_keywords = [
        "function",
        "let",
        "mut",
        "struct",
        "enum",
        "effect",
        "capability",
        "if",
        "else",
        "while",
        "for",
        "return",
    ]

    for kw in expected_keywords:
        assert f'"{kw}"' in content, f"Missing keyword '{kw}' in highlights.scm"
