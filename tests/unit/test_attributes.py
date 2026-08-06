"""Function attributes: parse, lower to C, compile with clang, run.

Covers the four code-generation attributes documented in
docs/LANGUAGE_SPEC.md §3.6 -- `@inline`, `@noinline`, `@always_inline`,
`@target(...)` -- plus the validation the type checker performs on the
attribute vocabulary as a whole.

The last section pins the observed behaviour of the `dbg` / `expect` / `test`
helpers, whose coverage differs per backend. Those tests exist so the spec's
description of them stays true; they assert what is, including the gaps.

Every "it works" claim here is backed by a clang compile and a process run,
not by string matching alone.
"""

import os
import re
import shutil
import subprocess
import tempfile

import pytest

from flow.attributes import (
    ATTRIBUTES_WITH_ARGS,
    KNOWN_ATTRIBUTES,
    attribute_errors,
    parse_attribute,
    validate_target_spec,
)
from flow.c_generator import CGenerator
from flow.parser import Block, FunctionDecl, Type, parse_flow_code
from flow.type_checker import TypeChecker

from .compiler_helpers import compile_and_run, needs_clang, to_c


needs_nm = pytest.mark.skipif(shutil.which("nm") is None, reason="nm not available")


def check_strict(code: str):
    checker = TypeChecker()
    checker.strict = True
    return checker.check(parse_flow_code(code)).errors


def attrs_of(code: str, fn_name: str):
    for decl in parse_flow_code(code):
        if getattr(decl, "name", None) == fn_name:
            return getattr(decl, "attributes", None) or []
    raise AssertionError(f"no declaration named {fn_name!r}")


def decl_lines(c_code: str, c_name: str):
    """The generated C lines that declare or define `c_name`.

    File-scope only: call sites live inside a function body and are indented,
    so anything starting with whitespace is skipped.
    """
    pattern = re.compile(rf"\b{re.escape(c_name)}\s*\(")
    return [
        line
        for line in c_code.splitlines()
        if line[:1].strip() and pattern.search(line)
    ]


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


def test_inline_emits_static_inline():
    c = to_c(INLINE_SRC)
    lines = decl_lines(c, "add_i32_i32")
    assert lines, c
    # Both the forward declaration and the definition carry the specifier.
    assert len(lines) == 2, lines
    for line in lines:
        assert line.startswith("static inline int32_t add_i32_i32("), line


def test_inline_on_exported_function_keeps_external_linkage():
    """`static` would hide a symbol another object file may name, so an
    exported `@inline` function uses C99 `extern inline` instead."""
    src = """
@inline
export function add(a: i32, b: i32) -> i32 {
    return a + b
}

function main() -> i32 {
    return add(1, 2) - 3
}
"""
    c = to_c(src)
    lines = decl_lines(c, "add_i32_i32")
    assert len(lines) == 2, lines
    for line in lines:
        assert line.startswith("extern inline int32_t add_i32_i32("), line
    assert "static inline int32_t add_i32_i32(" not in c


def test_main_is_never_made_static_inline():
    src = """
@inline
function main() -> i32 {
    return 0
}
"""
    c = to_c(src)
    assert "static inline int32_t main(" not in c
    assert "extern inline int32_t main(void)" in c


# test_inline_compiles_and_runs -> tests/lang/test_attributes.flow


# test_exported_inline_compiles_and_runs -> tests/lang/test_attributes.flow


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


def test_noinline_emits_gnu_attribute():
    c = to_c(NOINLINE_SRC)
    lines = decl_lines(c, "sub_i32_i32")
    assert len(lines) == 2, lines
    for line in lines:
        assert line.startswith("__attribute__((noinline)) int32_t sub_i32_i32("), line
    # Linkage is untouched: noinline says nothing about visibility.
    assert "static" not in " ".join(lines)


# test_noinline_compiles_and_runs -> tests/lang/test_attributes.flow.
# test_noinline_survives_optimization stays: test-lang compiles every
# program with one fixed clang invocation, so it cannot ask for -O2.


@needs_clang
def test_noinline_survives_optimization():
    """At -O2 the call would normally be inlined away; `noinline` keeps the
    out-of-line body, and the program still returns the right answer."""
    assert compile_and_run(NOINLINE_SRC, extra_cflags=["-O2"]) == 0


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


def test_always_inline_emits_attribute_and_inline_specifier():
    c = to_c(ALWAYS_INLINE_SRC)
    lines = decl_lines(c, "mul_i32_i32")
    assert len(lines) == 2, lines
    for line in lines:
        assert line.startswith(
            "__attribute__((always_inline)) static inline int32_t mul_i32_i32("
        ), line


# test_always_inline_compiles_and_runs -> tests/lang/test_attributes.flow.
# test_always_inline_is_accepted_at_O0 stays for the same reason as the
# -O2 case above: it needs its own clang flags.


@needs_clang
def test_always_inline_is_accepted_at_O0():
    """clang honours always_inline even without optimization; a mismatch here
    would surface as an "always_inline function could not be inlined" error."""
    assert compile_and_run(ALWAYS_INLINE_SRC, extra_cflags=["-O0", "-Werror"]) == 0


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


def test_target_emits_gnu_target_attribute():
    c = to_c(TARGET_SRC)
    lines = decl_lines(c, "bump_i32")
    assert len(lines) == 2, lines
    for line in lines:
        assert line.startswith(
            '__attribute__((target("crypto"))) int32_t bump_i32('
        ), line


def test_target_keeps_multiple_features_in_one_attribute():
    src = """
@target("avx2,fma")
function bump(a: i32) -> i32 {
    return a + 1
}

function main() -> i32 {
    return bump(-1)
}
"""
    c = to_c(src)
    assert '__attribute__((target("avx2,fma"))) int32_t bump_i32(int32_t a);' in c


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
    with pytest.raises(ValueError):
        to_c(src)


@needs_clang
def test_target_compiles_and_runs():
    """`crypto` is a real feature on arm64 and an unknown one elsewhere;
    clang warns on unknown features rather than failing, so this compiles
    and runs on every host. Whether the feature exists is the C compiler's
    call, not Flow's."""
    assert compile_and_run(TARGET_SRC) == 0


# --------------------------------------------------------------------------
# Combinations
# --------------------------------------------------------------------------

COMBINED_SRC = """
@noinline
@target("crypto")
function scale(a: i32) -> i32 {
    return a * 2
}

@always_inline
function offset(a: i32) -> i32 {
    return a + 2
}

function main() -> i32 {
    if scale(offset(19)) != 42 {
        return 6
    }
    return 0
}
"""


def test_combined_attributes_emit_both_specifiers():
    c = to_c(COMBINED_SRC)
    line = next(line for line in decl_lines(c, "scale_i32") if line.endswith(";"))
    assert line == (
        '__attribute__((noinline)) __attribute__((target("crypto"))) '
        "int32_t scale_i32(int32_t a);"
    ), line


@needs_clang
def test_combined_attributes_compile_and_run():
    assert compile_and_run(COMBINED_SRC) == 0


def test_always_inline_with_target_emits_both_but_is_a_c_level_conflict():
    """The lowering is faithful, and the combination is still a bad idea:
    clang refuses to inline a function whose target features the caller
    lacks. Flow emits what was asked for and lets the C compiler say so."""
    src = """
@always_inline
@target("crypto")
function scale(a: i32) -> i32 {
    return a * 2
}

function main() -> i32 {
    return scale(0)
}
"""
    c = to_c(src)
    assert (
        '__attribute__((always_inline)) __attribute__((target("crypto"))) '
        "static inline int32_t scale_i32(int32_t a);"
    ) in c


# --------------------------------------------------------------------------
# The hints actually reach the optimizer
# --------------------------------------------------------------------------

OPT_SRC = """
@inline
function hinted(a: i32) -> i32 {
    return a + 1
}

@noinline
function pinned(a: i32) -> i32 {
    return a + 2
}

function main() -> i32 {
    if hinted(pinned(39)) != 42 {
        return 1
    }
    return 0
}
"""


@needs_clang
@needs_nm
def test_noinline_keeps_a_symbol_that_inline_loses_at_O2():
    """The strongest available evidence that these are more than comments: at
    -O2 the `@noinline` body survives in the linked binary while the `@inline`
    one is folded into its caller and disappears."""
    c_code = to_c(OPT_SRC)
    with tempfile.TemporaryDirectory() as td:
        c_path = os.path.join(td, "prog.c")
        bin_path = os.path.join(td, "prog")
        with open(c_path, "w") as f:
            f.write(c_code)
        build = subprocess.run(
            ["clang", "-O2", "-o", bin_path, c_path],
            capture_output=True,
            text=True,
        )
        assert build.returncode == 0, build.stderr
        assert subprocess.run([bin_path]).returncode == 0
        symbols = subprocess.run(
            ["nm", bin_path], capture_output=True, text=True
        ).stdout

    assert "pinned_i32" in symbols, symbols
    assert "hinted_i32" not in symbols, symbols


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


def test_unknown_attribute_is_not_silently_accepted_by_codegen():
    """Regression guard: an unknown attribute must not reach C untouched."""
    src = """
@fastcall
function f() -> i32 {
    return 0
}
"""
    assert "fastcall" not in to_c(src)


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
# Attributes that are parsed but deliberately not lowered
# --------------------------------------------------------------------------

def test_bodyless_declarations_get_no_specifier():
    """`extern` and forward declarations have no body in this translation
    unit; an inline specifier there would promise a definition the backend
    never emits."""
    gen = CGenerator()
    fn = FunctionDecl(
        "f", [], Type("i32"), Block([]), ["inline", "noinline", "target(crypto)"]
    )

    fn.is_extern = True
    assert gen._c_attribute_prefix(fn) == ""

    fn.is_extern = False
    fn.is_forward_decl = True
    assert gen._c_attribute_prefix(fn) == ""

    fn.is_forward_decl = False
    assert gen._c_attribute_prefix(fn) != ""


# --------------------------------------------------------------------------
# dbg / expect / test -- what each one really does, per backend
# --------------------------------------------------------------------------

def build_and_run(source: str):
    """Compile with clang and run; return (exit code, stderr)."""
    c_code = to_c(source)
    with tempfile.TemporaryDirectory() as td:
        c_path = os.path.join(td, "prog.c")
        bin_path = os.path.join(td, "prog")
        with open(c_path, "w") as f:
            f.write(c_code)
        build = subprocess.run(
            ["clang", "-O0", "-o", bin_path, c_path, "-lm"],
            capture_output=True,
            text=True,
        )
        assert build.returncode == 0, f"{build.stderr}\n---\n{c_code}"
        run = subprocess.run([bin_path], capture_output=True, text=True)
        return run.returncode, run.stderr


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
    runtime abort is C-backend behaviour, not a language-wide guarantee."""
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


@needs_clang
def test_test_block_is_emitted_but_never_invoked():
    """Honest gap: `test "..." { }` compiles to an ordinary `bool` function.
    No backend and no harness calls it, so a failing body is never reached
    unless the program calls the function itself. If a harness is ever wired
    up, this test should fail and the spec row should be upgraded."""
    c = to_c(TEST_BLOCK_SRC)
    assert "bool test_one_plus_one(void) {" in c
    # The only mentions are the forward declaration and the definition.
    assert c.count("test_one_plus_one") == 2, c

    # A test body that would fail still exits 0, because nothing runs it.
    failing = """
test "always fails" {
    expect 1 + 1 == 3
    return false
}

function main() -> i32 {
    return 0
}
"""
    code, _ = build_and_run(failing)
    assert code == 0
