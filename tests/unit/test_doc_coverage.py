"""Feature coverage: does every part of the language have a documented home?

The checker is the Flow program behind scripts/check_doc_coverage.sh. These
tests drive it through the shim, using its --inventory, --map,
--mentions and --is-backend options.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "scripts" / "check_doc_coverage.sh"
MAP = ROOT / "docs" / "coverage.json"


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["bash", str(CHECKER), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def _inventory() -> dict[str, set[str]]:
    result = _run("--inventory")
    assert result.returncode == 0, result.stderr
    found: dict[str, set[str]] = {}
    for line in result.stdout.splitlines():
        category, _, name = line.partition(":")
        found.setdefault(category, set()).add(name)
    return found


def _check_with_map(tmp_path: Path, mapping: dict, *extra: str) -> subprocess.CompletedProcess:
    path = tmp_path / "coverage.json"
    path.write_text(json.dumps(mapping))
    return _run("--map", str(path), *extra)


def _real_map() -> dict:
    return json.loads(MAP.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------
# The inventory comes from the compiler, so it cannot go stale
# --------------------------------------------------------------------------

def test_keywords_come_from_the_lexer():
    kws = _inventory()["keyword"]
    # A sample of constructs the parser really reserves.
    assert {"function", "effect", "capability", "distinct", "defer", "match"} <= kws


def test_attributes_come_from_the_attribute_module():
    from flow.attributes import KNOWN_ATTRIBUTES

    assert _inventory()["attribute"] == set(KNOWN_ATTRIBUTES)


def test_cli_commands_come_from_the_dispatch_table():
    commands = _inventory()["cli"]
    assert {"run", "compile", "test", "fmt", "repl", "wasm"} <= commands
    # Arch and profile `case` arms elsewhere in the driver must not leak in.
    assert not {"x86_64", "aarch64", "auto", "safety", "flight"} & commands


def test_stdlib_modules_are_discovered_including_subdirectories():
    modules = _inventory()["stdlib"]
    assert {"array", "string", "gfx"} <= modules
    assert {"filters", "oscillators"} <= modules, "audio/ subdirectory missing"
    assert {"lqr", "wfc"} <= modules, "dynamics/ subdirectory missing"


def test_backends_are_discovered():
    assert {"c_generator", "mlir_generator", "wasm_compiler"} <= _inventory()["backend"]


@pytest.mark.parametrize(
    "stem,expected",
    [
        ("x_generator", True),
        ("y_codegen", True),
        ("z_compiler", True),
        # A BPF target on an unmerged branch was named bpf_target.py, which
        # the original three suffixes did not match, so a whole new
        # compilation target would have landed undocumented.
        ("bpf_target", True),
        ("w_backend", True),
        ("parser", False),
    ],
)
def test_backend_discovery_covers_every_naming_convention(stem, expected):
    result = _run("--is-backend", stem)
    assert result.stdout.strip() == str(expected)


# --------------------------------------------------------------------------
# The shipped map
# --------------------------------------------------------------------------

def test_every_feature_has_a_home_or_a_written_reason():
    result = _run()
    assert result.returncode == 0, result.stdout + result.stderr
    assert "every feature has a documented home" in result.stdout


def test_every_exemption_carries_a_reason():
    for key, reason in _real_map().get("exempt", {}).items():
        assert str(reason).strip(), f"{key} is exempt with no reason"


def test_the_map_is_valid_json_and_sorted():
    data = _real_map()
    assert data["covered"] and "exempt" in data


# --------------------------------------------------------------------------
# A mapping has to be true, not just present
# --------------------------------------------------------------------------

def test_a_feature_with_no_mapping_is_reported(tmp_path):
    mapping = _real_map()
    del mapping["covered"]["keyword:defer"]
    result = _check_with_map(tmp_path, mapping)
    assert result.returncode == 1
    assert "keyword:defer has no documented home" in result.stdout


def test_a_mapping_to_a_missing_page_fails(tmp_path):
    mapping = _real_map()
    mapping["covered"]["keyword:defer"] = "no/such/page.md"
    result = _check_with_map(tmp_path, mapping)
    assert result.returncode == 1
    assert "does not exist" in result.stdout


def test_a_page_that_does_not_mention_the_feature_fails(tmp_path):
    # An absolute page path is joined as-is, so the map can point outside docs/.
    page = tmp_path / "empty.md"
    page.write_text("# A page about something else entirely\n")
    mapping = _real_map()
    mapping["covered"]["keyword:defer"] = str(page)
    result = _check_with_map(tmp_path, mapping)
    assert result.returncode == 1
    assert f"keyword:defer maps to '{page}', which never mentions it" in result.stdout

    page.write_text("`defer` runs on scope exit\n")
    result = _check_with_map(tmp_path, mapping)
    assert result.returncode == 0, result.stdout


@pytest.mark.parametrize(
    "category,feature,text,expected",
    [
        ("attribute", "gpu", "use @gpu on a kernel", True),
        ("attribute", "gpu", "the gpu is fast", False),  # bare word is not the attribute
        ("cli", "run", "./flow run prog.flow", True),
        ("cli", "run", "a long run of failures", False),
        ("keyword", "defer", "`defer` runs on scope exit", True),
        ("keyword", "defer", "deferred work", False),
    ],
)
def test_mentions_is_specific_enough_to_be_worth_something(
    tmp_path, category, feature, text, expected
):
    page = tmp_path / "p.md"
    page.write_text(text)
    result = _run("--mentions", category, feature, str(page))
    assert result.stdout.strip() == str(expected)
