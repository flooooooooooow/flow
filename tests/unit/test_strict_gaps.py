"""Regression tests for type-checker gaps that used to force `flow:lenient`.

Each class pins one gap that previously made a corpus file uncheckable under
`--strict`. The pragma removal is part of the fix, so the tests also assert
that the files stay strict-clean.
"""

from __future__ import annotations

import os
import sys
import warnings

import pytest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if os.path.join(REPO_ROOT, "src") not in sys.path:
    sys.path.insert(0, os.path.join(REPO_ROOT, "src"))

from flow.parser import parse_flow_code  # noqa: E402
from flow.transpiler import resolve_modules  # noqa: E402
from flow.type_checker import TypeChecker  # noqa: E402


def strict_errors(source: str) -> list:
    """Type check a source string in strict mode and return the errors."""
    checker = TypeChecker()
    checker.strict = True
    return checker.check(parse_flow_code(source)).errors


def strict_errors_for_file(rel_path: str) -> list:
    """Resolve imports for a corpus file, then strict-check it."""
    path = os.path.join(REPO_ROOT, rel_path)
    cwd = os.getcwd()
    os.chdir(REPO_ROOT)
    try:
        with warnings.catch_warnings():
            # Corpus files still use legacy string imports; that is a separate
            # migration and not what these tests are pinning.
            warnings.simplefilter("ignore", DeprecationWarning)
            declarations = resolve_modules(path)
    finally:
        os.chdir(cwd)
    checker = TypeChecker()
    checker.strict = True
    return checker.check(declarations).errors


def assert_no_lenient_pragma(rel_path: str) -> None:
    with open(os.path.join(REPO_ROOT, rel_path)) as handle:
        assert "flow:lenient" not in handle.read(), (
            f"{rel_path} regressed to flow:lenient"
        )


# ---------------------------------------------------------------------------
# Gap 1: generic channel intrinsics (flow-strict-concurrency-intrinsics)
# ---------------------------------------------------------------------------

GENERIC_CALL = """
struct Box<T> {
    value: T
}

function box_make<T>(v: T) -> Box<T> {
    return Box<T> { value: v }
}

function box_get<T>(b: ptr<Box<T> >) -> T {
    return b.value
}

function main() -> i32 {
    let mut b: Box<i32> = box_make<i32>(7)
    let v: i32 = box_get<i32>(&b)
    return v - 7
}
"""

GENERIC_WRONG_ARG = """
struct Box<T> {
    value: T
}

function box_make<T>(v: T) -> Box<T> {
    return Box<T> { value: v }
}

function main() -> i32 {
    let b: Box<i32> = box_make<i32>("not an int", 3)
    return 0
}
"""


class TestGenericInstantiationIsChecked:
    """`box_make<i32>(7)` parses as a call to `box_make_i32`, a function the
    monomorphizer only creates after type checking. The checker synthesizes
    the same signature so the call site resolves and is really checked."""

    def test_generic_call_sites_type_check(self):
        assert strict_errors(GENERIC_CALL) == []

    def test_synthesized_signature_still_catches_arity(self):
        errors = strict_errors(GENERIC_WRONG_ARG)
        assert any("box_make_i32" in e for e in errors), errors

    @pytest.mark.parametrize(
        "rel_path",
        [
            "examples/concurrency/generic_channel.flow",
            "examples/concurrency/channels.flow",
            "examples/concurrency/channels_i64.flow",
            "examples/concurrency/select.flow",
            "examples/concurrency/pipeline.flow",
            "tests/runtime/test_concurrent_channels.flow",
            "tests/lang/test_generic_channels.flow",
        ],
    )
    def test_concurrency_corpus_is_strict_clean(self, rel_path):
        assert_no_lenient_pragma(rel_path)
        assert strict_errors_for_file(rel_path) == []
