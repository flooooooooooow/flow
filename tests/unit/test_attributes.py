"""Function attributes: parsing and validation.

Covers the four code-generation attributes documented in
docs/LANGUAGE_SPEC.md §3.6 (`@inline`, `@noinline`, `@always_inline`,
`@target(...)`) and the validation the type checker performs on the
attribute vocabulary as a whole.

The last section pins the front-end and MLIR behaviour of the `dbg`,
`expect` and `test` helpers.

The C side is flowc. tests/lang/test_function_attributes.flow runs programs
that carry each attribute, and tests/cgen/attributes_not_spliced.flow checks
that attribute text never reaches the C verbatim.
"""

import pytest

from flow.attributes import (
    ATTRIBUTES_WITH_ARGS,
    KNOWN_ATTRIBUTES,
    attribute_errors,
    parse_attribute,
    validate_target_spec,
)
from flow.parser import parse_flow_code
from flow.type_checker import TypeChecker


def check_strict(code: str):
    checker = TypeChecker()
    checker.strict = True
    return checker.check(parse_flow_code(code)).errors


def attrs_of(code: str, fn_name: str):
    for decl in parse_flow_code(code):
        if getattr(decl, "name", None) == fn_name:
            return getattr(decl, "attributes", None) or []
    raise AssertionError(f"no declaration named {fn_name!r}")


# --------------------------------------------------------------------------
# @inline
# --------------------------------------------------------------------------

INLINE_SRC = """
@inline
function add(a: i32, b: i32) -> i32 {
    return a + b
}

function main() -> i32 {
    if add(20, 22) != 42 {
        return 1
    }
    return 0
}
"""


def test_inline_parses_onto_the_declaration():
    assert attrs_of(INLINE_SRC, "add") == ["inline"]


# test_inline_compiles_and_runs -> tests/lang/test_function_attributes.flow


# test_exported_inline_compiles_and_runs -> tests/lang/test_function_attributes.flow


# --------------------------------------------------------------------------
# @noinline
# --------------------------------------------------------------------------

NOINLINE_SRC = """
@noinline
function sub(a: i32, b: i32) -> i32 {
    return a - b
}

function main() -> i32 {
    if sub(44, 2) != 42 {
        return 3
    }
    return 0
}
"""


def test_noinline_parses_onto_the_declaration():
    assert attrs_of(NOINLINE_SRC, "sub") == ["noinline"]


# test_noinline_compiles_and_runs -> tests/lang/test_function_attributes.flow.


# --------------------------------------------------------------------------
# @always_inline
# --------------------------------------------------------------------------

ALWAYS_INLINE_SRC = """
@always_inline
function mul(a: i32, b: i32) -> i32 {
    return a * b
}

function main() -> i32 {
    if mul(6, 7) != 42 {
        return 4
    }
    return 0
}
"""


def test_always_inline_parses_onto_the_declaration():
    assert attrs_of(ALWAYS_INLINE_SRC, "mul") == ["always_inline"]


# test_always_inline_compiles_and_runs -> tests/lang/test_function_attributes.flow.


# --------------------------------------------------------------------------
# @target
# --------------------------------------------------------------------------

TARGET_SRC = """
@target("crypto")
function bump(a: i32) -> i32 {
    return a + 1
}

function main() -> i32 {
    if bump(41) != 42 {
        return 5
    }
    return 0
}
"""


def test_target_parses_with_its_string_argument():
    assert attrs_of(TARGET_SRC, "bump") == ["target(crypto)"]


@pytest.mark.parametrize(
    "spec",
    ["avx2", "+avx2", "-sse", "no-sse", "sse4.2,popcnt", "arch=haswell",
     "tune=native", "branch-protection=standard", "crypto"],
)
def test_target_accepts_documented_forms(spec):
    assert validate_target_spec(spec) is None


@pytest.mark.parametrize(
    "spec",
    ["", "avx2,", ",avx2", 'avx2")) __attribute__((constructor', "a b", "a;b",
     "$(whoami)", "a\\nb"],
)
def test_target_rejects_implausible_specs(spec):
    assert validate_target_spec(spec) is not None


def test_target_string_cannot_escape_the_c_attribute():
    """A crafted target string must be rejected, never spliced into the C."""
    src = """
@target("x\\")) __attribute__((constructor")
function evil() -> i32 {
    return 0
}

function main() -> i32 {
    return evil()
}
"""
    errors = check_strict(src)
    assert any("@target" in e for e in errors), errors


# The target and combined-attribute run tests ->
# tests/lang/test_function_attributes.flow.


# --------------------------------------------------------------------------
# Validation / negative cases
# --------------------------------------------------------------------------

def test_unknown_attribute_is_an_error():
    errors = check_strict(
        """
@fastcall
function f() -> i32 {
    return 0
}
"""
    )
    assert len(errors) == 1, errors
    assert "Unknown attribute '@fastcall'" in errors[0]
    assert "function 'f'" in errors[0]
    # The message lists what the user could have meant.
    assert "@inline" in errors[0]


def test_known_attributes_produce_no_error():
    for name in sorted(KNOWN_ATTRIBUTES):
        if name in ATTRIBUTES_WITH_ARGS:
            continue
        assert attribute_errors("f", [name]) == [], name


def test_attribute_that_takes_no_arguments_rejects_them():
    errors = attribute_errors("f", ["inline(x)"])
    assert errors and "takes no arguments" in errors[0], errors


def test_target_without_a_string_is_an_error():
    errors = attribute_errors("f", ["target"])
    assert errors and "requires a target string" in errors[0], errors

    errors = attribute_errors("f", ["target()"])
    assert errors and "requires a target string" in errors[0], errors


def test_noinline_conflicts_with_inline():
    errors = attribute_errors("f", ["inline", "noinline"])
    assert errors and "cannot be both" in errors[0], errors

    errors = attribute_errors("f", ["always_inline", "noinline"])
    assert errors and "cannot be both" in errors[0], errors


def test_parse_attribute_splits_name_and_args():
    assert parse_attribute("inline") == ("inline", [])
    assert parse_attribute("target(avx2)") == ("target", ["avx2"])
    assert parse_attribute("target(avx2,fma)") == ("target", ["avx2", "fma"])
    assert parse_attribute("only(hot,jit)") == ("only", ["hot", "jit"])


def test_existing_attributes_still_validate():
    """The pre-existing vocabulary must keep working unchanged."""
    for attr in ("gpu", "rt_safe", "flow_api", "only(hot)", "guard(jit,compile)",
                 "compile", "monomorphized", "test"):
        assert attribute_errors("f", [attr]) == [], attr


# --------------------------------------------------------------------------
# dbg / expect / test -- what each one really does, per backend
# --------------------------------------------------------------------------

DBG_SRC = """
function main() -> i32 {
    let x: i32 = dbg 41
    if x != 41 {
        return 1
    }
    return 0
}
"""


# test_dbg_prints_to_stderr_and_is_value_transparent ->
# tests/lang/test_dbg_expect.flow, judged against its .expected-stderr.


def test_dbg_in_mlir_is_evaluation_only():
    """MLIR backend: `dbg e` lowers to `e`. There is no printing. Pinning this
    keeps the spec honest about the difference from the C backend."""
    from flow.mlir_generator import MLIRGenerator

    mlir = MLIRGenerator("t.flow").generate_module(parse_flow_code(DBG_SRC))
    assert "__flow_dbg" not in mlir
    assert "dbg: " not in mlir


EXPECT_FAIL_SRC = """
function main() -> i32 {
    expect 1 + 1 == 3
    return 0
}
"""


# test_expect_aborts_with_a_diagnostic_when_false ->
# tests/lang/test_expect_fails.flow, whose .exitcode is 1.


# test_expect_is_a_no_op_when_true -> tests/lang/test_dbg_expect.flow.


def test_expect_requires_a_bool():
    errors = check_strict(
        """
function main() -> i32 {
    expect 1 + 1
    return 0
}
"""
    )
    assert any("expect condition must be a bool" in e for e in errors), errors


def test_expect_in_mlir_evaluates_but_does_not_abort():
    """MLIR backend: the condition is emitted for its side effects only. The
    runtime abort is C-backend behaviour. The language does not guarantee it."""
    from flow.mlir_generator import MLIRGenerator

    mlir = MLIRGenerator("t.flow").generate_module(parse_flow_code(EXPECT_FAIL_SRC))
    assert "abort" not in mlir
    assert "exit" not in mlir


TEST_BLOCK_SRC = """
test "one plus one" {
    expect 1 + 1 == 2
    return true
}

function main() -> i32 {
    return 0
}
"""


def test_test_block_becomes_a_bool_function_with_a_test_attribute():
    decls = parse_flow_code(TEST_BLOCK_SRC)
    names = [getattr(d, "name", None) for d in decls]
    assert "test_one_plus_one" in names, names
    fn = next(d for d in decls if getattr(d, "name", None) == "test_one_plus_one")
    assert fn.attributes == ["test"]
    assert fn.return_type.name == "bool"


# test_test_block_is_emitted_but_never_invoked: the run part (a failing test
# body does not fail the program) -> tests/cgen/attributes_not_spliced.flow.
