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


# ---------------------------------------------------------------------------
# Gap 2: string vs byte buffer (flow-strict-string-buffer-coercions)
# ---------------------------------------------------------------------------

BYTE_BUFFER_CASTS = """
extern {
    function malloc(n: i64) -> ptr<u8>
}

function main() -> i32 {
    let buf: ptr<u8> = malloc(8)
    buf[0] = 104
    buf[1] = 0
    let from_ptr: string = buf as string

    let mut arr: array<u8, 8> = []
    arr[0] = 111
    arr[1] = 0
    let from_array: string = arr as string

    let back_to_ptr: ptr<u8> = from_ptr
    return 0
}
"""

IMPLICIT_PTR_TO_STRING = """
extern {
    function malloc(n: i64) -> ptr<u8>
}

function main() -> i32 {
    let buf: ptr<u8> = malloc(8)
    let s: string = buf
    return 0
}
"""

IMPLICIT_ARRAY_TO_STRING = """
function main() -> i32 {
    let arr: array<u8, 8> = []
    let s: string = arr
    return 0
}
"""


class TestByteBufferToString:
    """A `ptr<u8>` or `array<u8, N>` becomes a `string` only through an
    explicit cast. Implicit coercion would silently assert NUL termination
    the checker cannot see, so it stays an error."""

    def test_explicit_casts_are_accepted(self):
        assert strict_errors(BYTE_BUFFER_CASTS) == []

    def test_implicit_pointer_to_string_is_still_rejected(self):
        errors = strict_errors(IMPLICIT_PTR_TO_STRING)
        assert any("ptr<u8>" in e and "string" in e for e in errors), errors

    def test_implicit_array_to_string_is_still_rejected(self):
        errors = strict_errors(IMPLICIT_ARRAY_TO_STRING)
        assert any("array<u8" in e and "string" in e for e in errors), errors

    @pytest.mark.parametrize(
        "rel_path",
        [
            "examples/compilers/know_demo.flow",
            "examples/compilers/claim_address_demo.flow",
            "examples/compilers/math_prose_demo.flow",
        ],
    )
    def test_flowc_corpus_is_strict_clean(self, rel_path):
        assert_no_lenient_pragma(rel_path)
        assert strict_errors_for_file(rel_path) == []


# ---------------------------------------------------------------------------
# Gap 3: capability parameters in handle blocks (flow-strict-effect-ops)
# ---------------------------------------------------------------------------

IMPLICIT_CAPABILITY_ARGS = """
effect Store {
    put(v: i32) -> void,
}

capability MemStore {
    effect Store,

    function put(v: i32) -> void {
        return
    }
}

function stash(v: i32, store: Store) -> i32 {
    Store.put(v)
    return v
}

function main() -> i32 {
    handle Store with MemStore {
        let kept: i32 = stash(7)
        return kept - 7
    }
    return 1
}
"""

CAPABILITY_ARGS_OUTSIDE_HANDLE = """
effect Store {
    put(v: i32) -> void,
}

function stash(v: i32, store: Store) -> i32 {
    return v
}

function main() -> i32 {
    let kept: i32 = stash(7)
    return kept
}
"""


class TestImplicitCapabilityArguments:
    """Inside `handle E with Cap { … }` a call may omit trailing parameters
    typed by a handled effect; the C backend passes zero-initialized
    capability structs for them. Strict checking now uses the same rule."""

    def test_call_inside_handle_may_omit_capability_params(self):
        assert strict_errors(IMPLICIT_CAPABILITY_ARGS) == []

    def test_omission_outside_a_handle_is_still_an_error(self):
        errors = strict_errors(CAPABILITY_ARGS_OUTSIDE_HANDLE)
        assert any("stash" in e for e in errors), errors

    @pytest.mark.parametrize(
        "rel_path",
        [
            "examples/gpu/gpu_fft.flow",
            "examples/gpu/gpu_mul_backward.flow",
        ],
    )
    def test_gpu_corpus_is_strict_clean(self, rel_path):
        assert_no_lenient_pragma(rel_path)
        assert strict_errors_for_file(rel_path) == []

    def test_gpu_mul_kernels_have_flow_bindings(self):
        """gpu_mul_backward.flow called gpu_mul_f32 and friends with no
        declaration anywhere, so the generated C had implicit declarations
        that passed a GpuBuffer struct where the runtime wants a void*."""
        with open(os.path.join(REPO_ROOT, "lib", "stdlib", "gpu_memory.flow")) as f:
            stdlib = f.read()
        with open(os.path.join(REPO_ROOT, "lib", "runtime", "gpu_memory_stub.flow")) as f:
            stub = f.read()
        for name in (
            "gpu_mul_f32",
            "gpu_mul_backward_a_f32",
            "gpu_mul_backward_b_f32",
        ):
            assert f"export function {name}(" in stdlib, name
            assert f"export function flow_{name}(" in stub, name
