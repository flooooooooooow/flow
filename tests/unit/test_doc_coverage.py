"""Feature coverage: does every part of the language have a documented home?"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import check_doc_coverage as cov  # noqa: E402


# --------------------------------------------------------------------------
# The inventory comes from the compiler, so it cannot go stale
# --------------------------------------------------------------------------

def test_keywords_come_from_the_lexer():
    kws = cov._keywords()
    # A sample of constructs the parser really reserves.
    assert {"function", "effect", "capability", "distinct", "defer", "match"} <= kws


def test_attributes_come_from_the_attribute_module():
    from flow.attributes import KNOWN_ATTRIBUTES

    assert cov._attributes() == set(KNOWN_ATTRIBUTES)


def test_cli_commands_come_from_the_dispatch_table():
    commands = cov._cli_commands()
    assert {"run", "compile", "test", "fmt", "repl", "wasm"} <= commands
    # Arch and profile `case` arms elsewhere in the driver must not leak in.
    assert not {"x86_64", "aarch64", "auto", "safety", "flight"} & commands


def test_stdlib_modules_are_discovered_including_subdirectories():
    modules = cov._stdlib_modules()
    assert {"array", "string", "gfx"} <= modules
    assert {"filters", "oscillators"} <= modules, "audio/ subdirectory missing"
    assert {"lqr", "wfc"} <= modules, "dynamics/ subdirectory missing"


def test_backends_are_discovered():
    assert {"c_generator", "mlir_generator", "wasm_compiler"} <= cov._backends()


# --------------------------------------------------------------------------
# The shipped map
# --------------------------------------------------------------------------

def test_every_feature_has_a_home_or_a_written_reason():
    problems, _ = cov.check()
    assert problems == [], "\n".join(problems)


def test_every_exemption_carries_a_reason():
    mapping = cov.load_map()
    for key, reason in mapping.get("exempt", {}).items():
        assert str(reason).strip(), f"{key} is exempt with no reason"


def test_the_map_is_valid_json_and_sorted():
    raw = (ROOT / "docs" / "coverage.json").read_text()
    data = json.loads(raw)
    assert data["covered"] and "exempt" in data


# --------------------------------------------------------------------------
# A mapping has to be true, not just present
# --------------------------------------------------------------------------

def test_a_mapping_to_a_page_that_never_mentions_the_feature_fails(monkeypatch):
    monkeypatch.setattr(
        cov, "load_map",
        lambda: {"covered": {"keyword": "x"}, "exempt": {}},
    )
    monkeypatch.setattr(cov, "inventory", lambda: {"keyword": {"defer"}})
    problems, _ = cov.check()
    assert any("no documented home" in p for p in problems)


def test_a_mapping_to_a_missing_page_fails(monkeypatch, tmp_path):
    monkeypatch.setattr(
        cov, "load_map",
        lambda: {"covered": {"keyword:defer": "no/such/page.md"}, "exempt": {}},
    )
    monkeypatch.setattr(cov, "inventory", lambda: {"keyword": {"defer"}})
    problems, _ = cov.check()
    assert any("does not exist" in p for p in problems)


def test_a_page_that_does_not_mention_the_feature_fails(monkeypatch, tmp_path):
    page = tmp_path / "empty.md"
    page.write_text("# A page about something else entirely\n")
    monkeypatch.setattr(cov, "DOCS", tmp_path)
    monkeypatch.setattr(
        cov, "load_map",
        lambda: {"covered": {"keyword:defer": "empty.md"}, "exempt": {}},
    )
    monkeypatch.setattr(cov, "inventory", lambda: {"keyword": {"defer"}})
    problems, _ = cov.check()
    assert any("never mentions it" in p for p in problems)


def test_a_mapping_for_a_feature_the_compiler_dropped_is_reported(monkeypatch):
    monkeypatch.setattr(
        cov, "load_map",
        lambda: {"covered": {"keyword:removed_thing": "DEVELOPMENT.md"}, "exempt": {}},
    )
    monkeypatch.setattr(cov, "inventory", lambda: {"keyword": set()})
    problems, _ = cov.check()
    assert any("no longer exists" in p for p in problems)


@pytest.mark.parametrize(
    "category,feature,text,expected",
    [
        ("attribute", "gpu", "use @gpu on a kernel", True),
        ("attribute", "gpu", "the gpu is fast", False),  # bare word is not the attribute
        ("cli", "run", "./flow run prog.flow", True),
        ("cli", "run", "a long run of failures", False),
        ("keyword", "defer", "`defer` runs on scope exit", True),
    ],
)
def test_mentions_is_specific_enough_to_be_worth_something(
    monkeypatch, tmp_path, category, feature, text, expected
):
    page = tmp_path / "p.md"
    page.write_text(text)
    monkeypatch.setattr(cov, "DOCS", tmp_path)
    assert cov.mentions("p.md", category, feature) is expected
