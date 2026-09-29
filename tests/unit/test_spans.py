"""Spans: borrowed views over contiguous storage (docs/language/spans.md).

Layer 1: concrete element types. Covers both spellings desugaring to one
type, the two-word lowering, auto-borrow at call sites, slice expressions,
and every diagnostic the design doc specifies.
"""

from __future__ import annotations

import pytest

from flow.parser import parse_flow_code
from flow.type_checker import TypeKind

from .compiler_helpers import errors


def _param_type(source: str, function: str = "f", index: int = 0):
    for decl in parse_flow_code(source):
        if getattr(decl, "name", None) == function:
            return decl.parameters[index].type
    raise AssertionError(f"function {function!r} not found")


# --- Both spellings parse to exactly one internal type -----------------------


@pytest.mark.parametrize(
    "span_form,sugar_form",
    [
        ("span<f32>", "&[f32]"),
        ("span<const f32>", "&[f32]"),
        ("span<mut i32>", "&mut [i32]"),
        ("span<f64, 16>", "&[f64; 16]"),
        ("span<mut u8, 32>", "&mut [u8; 32]"),
    ],
)
def test_sugar_desugars_to_the_same_type(span_form, sugar_form):
    a = _param_type(f"function f(v: {span_form}) {{ }}")
    b = _param_type(f"function f(v: {sugar_form}) {{ }}")
    assert a == b


def test_span_type_names_encode_element_and_mutability():
    assert _param_type("function f(v: span<f32>) { }").name == "span_const_f32"
    assert _param_type("function f(v: span<mut f32>) { }").name == "span_mut_f32"


def test_static_extent_is_carried_on_the_type_not_the_name():
    plain = _param_type("function f(v: span<f32>) { }")
    fixed = _param_type("function f(v: span<f32, 512>) { }")
    assert plain.name == fixed.name  # one body serves both
    assert plain.size is None
    assert fixed.size == 512


def test_span_is_its_own_semantic_kind():
    from flow.type_checker import TypeChecker

    checker = TypeChecker()
    semantic = checker._parse_type(_param_type("function f(v: span<mut f32>) { }"))
    assert semantic.kind == TypeKind.SPAN
    assert str(semantic) == "span<mut f32>"


# --- Lowering ----------------------------------------------------------------

# The view typedef, parameter lowering, auto-borrow and slice lowering are
# pinned against flowc by tests/cgen/spans_lowering.

# The six compile-and-run cases (summing a borrowed array, filling through a
# mutable span, a slice passed onward, a span forwarded unchanged, a
# fixed-extent parameter, and the &[T] sugar) are now
# tests/lang/test_spans.flow. The lowering shape and the rejection
# diagnostics stay here.


# --- Diagnostics -------------------------------------------------------------


def test_mutable_borrow_of_an_immutable_binding_is_rejected():
    found = errors(
        """
        function fill(values: span<mut i32>) { values[0] = 1 }
        function main() -> i32 {
            let samples: array<i32, 4> = [0, 0, 0, 0]
            fill(samples)
            return 0
        }
        """
    )
    assert "cannot borrow `samples` mutably; it is declared with `let`" in found


def test_mutable_borrow_of_a_let_mut_binding_is_accepted():
    assert (
        errors(
            """
            function fill(values: span<mut i32>) { values[0] = 1 }
            function main() -> i32 {
                let mut samples: array<i32, 4> = [0, 0, 0, 0]
                fill(samples)
                return 0
            }
            """
        )
        == []
    )


def test_pointer_argument_is_rejected_with_a_slice_suggestion():
    found = errors(
        """
        function total(values: span<f32>) -> f32 { return values[0] }
        function main() -> i32 {
            let p: ptr<f32> = null
            let t: f32 = total(p)
            return 0
        }
        """
    )
    assert len(found) == 1
    assert "a pointer has no length" in found[0]
    assert "`p[0..n]`" in found[0]


def test_slicing_a_pointer_gives_it_a_length():
    assert (
        errors(
            """
            function total(values: span<f32>) -> f32 { return values[0] }
            function main() -> i32 {
                let p: ptr<f32> = null
                let t: f32 = total(p[0..4])
                return 0
            }
            """
        )
        == []
    )


def test_static_extent_mismatch_names_both_lengths():
    found = errors(
        """
        function matrix4(values: span<f32, 16>) { }
        function main() -> i32 {
            let xs: array<f32, 4> = [1.0, 2.0, 3.0, 4.0]
            matrix4(xs)
            return 0
        }
        """
    )
    assert len(found) == 1
    assert "16" in found[0] and "4" in found[0]
    assert "static extent mismatch" in found[0]


def test_static_extent_from_a_dynamic_length_is_rejected():
    found = errors(
        """
        function matrix4(values: span<f32, 16>) { }
        function forward(values: span<f32>) { matrix4(values) }
        function main() -> i32 { return 0 }
        """
    )
    assert len(found) == 1
    assert "not known at compile time" in found[0]


def test_matching_static_extent_is_accepted():
    assert (
        errors(
            """
            function matrix4(values: span<f32, 4>) { }
            function main() -> i32 {
                let xs: array<f32, 4> = [1.0, 2.0, 3.0, 4.0]
                matrix4(xs)
                matrix4(xs[0..4])
                return 0
            }
            """
        )
        == []
    )


def test_returning_a_view_of_a_local_is_rejected():
    found = errors(
        """
        function invalid() -> span<i32> {
            let local: array<i32, 3> = [1, 2, 3]
            return local[0..3]
        }
        function main() -> i32 { return 0 }
        """
    )
    assert len(found) == 1
    assert found[0].startswith("span outlives borrowed storage `local`")
    assert "line 4" in found[0]


def test_returning_a_span_local_that_borrows_a_local_is_rejected():
    found = errors(
        """
        function invalid() -> span<i32> {
            let local: array<i32, 3> = [1, 2, 3]
            let view: span<i32> = local[0..3]
            return view
        }
        function main() -> i32 { return 0 }
        """
    )
    assert any(
        e.startswith("span outlives borrowed storage `local`") for e in found
    ), found


def test_returning_a_view_of_a_parameter_is_accepted():
    assert (
        errors(
            """
            function head(values: span<i32>) -> span<i32> { return values[0..2] }
            function main() -> i32 { return 0 }
            """
        )
        == []
    )


def test_storing_a_local_view_in_a_module_static_is_rejected():
    found = errors(
        """
        let mut cached: span<i32> = null
        function stash() {
            let local: array<i32, 3> = [1, 2, 3]
            cached = local[0..3]
        }
        function main() -> i32 { return 0 }
        """
    )
    assert any(
        e.startswith("span outlives borrowed storage `local`") for e in found
    ), found


def test_writing_through_an_immutable_view_is_rejected():
    found = errors(
        """
        function bad(values: span<i32>) { values[0] = 1 }
        function main() -> i32 { return 0 }
        """
    )
    assert len(found) == 1
    assert "immutable view" in found[0]


def test_element_type_must_match_exactly():
    found = errors(
        """
        function total(values: span<f64>) -> f64 { return values[0] }
        function main() -> i32 {
            let xs: array<f32, 2> = [1.0, 2.0]
            let t: f64 = total(xs)
            return 0
        }
        """
    )
    assert found  # a span may not reinterpret the storage it views


# --- Layer 2 forms report their absence clearly ------------------------------


@pytest.mark.parametrize(
    "form",
    [
        "span",
        "span<mut>",
        "span<const>",
        "span[16]",
        "span<number>",
        "span<mut, source.extent>",
    ],
)
def test_layer_two_forms_say_they_are_not_implemented(form):
    with pytest.raises(SyntaxError) as excinfo:
        parse_flow_code(f"function f(v: {form}) {{ }}")
    assert "not yet implemented in this compiler version" in str(excinfo.value)
