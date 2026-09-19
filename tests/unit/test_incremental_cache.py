"""Soundness tests for the frontend declaration cache in module_resolver.

These cover the staleness holes closed for issue #736. The original cache
keyed only on raw source text, so it could serve declarations produced by a
different compiler frontend, and it never noticed when an imported module
changed. Each test counts real parses by spying on the Parser the resolver
uses, so a cache hit is observable without timing.
"""

import os

import pytest

import flow.module_resolver as mr
from flow.module_resolver import resolve_modules


@pytest.fixture
def parse_counter(monkeypatch):
    """Count Parser instantiations inside module_resolver.

    The resolver builds `Parser(lexer)` only on a cache miss, so the count is
    the number of files actually reparsed.
    """
    real_parser = mr.Parser
    state = {"count": 0}

    class CountingParser(real_parser):
        def __init__(self, *args, **kwargs):
            state["count"] += 1
            super().__init__(*args, **kwargs)

    monkeypatch.setattr(mr, "Parser", CountingParser)
    return state


def _write(path, text):
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def test_unchanged_rebuild_hits_cache(tmp_path, parse_counter):
    root = tmp_path / "leaf.flow"
    _write(root, "function main() -> i32 { return 42; }\n")

    resolve_modules(str(root))
    assert parse_counter["count"] == 1  # cold build parses once

    resolve_modules(str(root))
    assert parse_counter["count"] == 1  # warm rebuild is a pure cache hit


def test_source_edit_invalidates(tmp_path, parse_counter):
    root = tmp_path / "leaf.flow"
    _write(root, "function main() -> i32 { return 1; }\n")
    decls_1 = resolve_modules(str(root))
    assert parse_counter["count"] == 1

    _write(root, "function main() -> i32 { return 2; }\n")
    decls_2 = resolve_modules(str(root))
    assert parse_counter["count"] == 2  # edited text is reparsed

    # The updated body reaches the caller (no stale entry served).
    assert decls_1[0].body.statements[0].value.value == "1"
    assert decls_2[0].body.statements[0].value.value == "2"


def test_compiler_salt_change_invalidates(tmp_path, parse_counter, monkeypatch):
    root = tmp_path / "leaf.flow"
    _write(root, "function main() -> i32 { return 42; }\n")

    monkeypatch.setenv("FLOW_CACHE_SALT", "frontend-v1")
    resolve_modules(str(root))
    assert parse_counter["count"] == 1

    # Same source, unchanged rebuild under the same salt: cache hit.
    resolve_modules(str(root))
    assert parse_counter["count"] == 1

    # A different compiler/schema salt must never reuse the old entry, even
    # though the source text is byte-for-byte identical.
    monkeypatch.setenv("FLOW_CACHE_SALT", "frontend-v2")
    resolve_modules(str(root))
    assert parse_counter["count"] == 2


def test_imported_module_change_invalidates(tmp_path, parse_counter):
    """Editing a dependency invalidates the importer, whose own text is fixed."""
    leaf = tmp_path / "leaf.flow"
    root = tmp_path / "app.flow"
    _write(leaf, "function helper() -> i32 { return 1; }\n")
    _write(
        root,
        "import .leaf\nfunction main() -> i32 { return 0; }\n",
    )

    resolve_modules(str(root))
    assert parse_counter["count"] == 2  # app + leaf parsed cold

    # Unchanged rebuild: both entries hit, nothing reparsed.
    resolve_modules(str(root))
    assert parse_counter["count"] == 2

    # Change only the imported leaf. The leaf reparses because its own text
    # changed, and the importer reparses because its recorded dependency hash
    # no longer matches. If import invalidation were missing, only the leaf
    # would reparse and this count would be 3.
    _write(leaf, "function helper() -> i32 { return 999; }\n")
    resolve_modules(str(root))
    assert parse_counter["count"] == 4


def test_imported_change_reaches_output(tmp_path):
    """A rebuild after an import edit produces the updated declarations."""
    leaf = tmp_path / "leaf.flow"
    root = tmp_path / "app.flow"
    _write(leaf, "function helper() -> i32 { return 1; }\n")
    _write(root, "import .leaf\nfunction main() -> i32 { return 0; }\n")

    first = resolve_modules(str(root))
    helper_first = [d for d in first if getattr(d, "name", None) == "helper"][0]
    assert helper_first.body.statements[0].value.value == "1"

    _write(leaf, "function helper() -> i32 { return 999; }\n")
    second = resolve_modules(str(root))
    helper_second = [d for d in second if getattr(d, "name", None) == "helper"][0]
    assert helper_second.body.statements[0].value.value == "999"


def test_corrupt_cache_entry_falls_back_to_parse(tmp_path, parse_counter):
    """A garbage cache file is ignored; the resolver reparses instead."""
    root = tmp_path / "leaf.flow"
    _write(root, "function main() -> i32 { return 42; }\n")
    resolve_modules(str(root))
    assert parse_counter["count"] == 1

    cache_dir = tmp_path / ".flow_cache"
    for entry in cache_dir.iterdir():
        with open(entry, "wb") as handle:
            handle.write(b"not a pickle")

    # A corrupt entry must miss (never crash or serve stale), so we reparse.
    resolve_modules(str(root))
    assert parse_counter["count"] == 2
