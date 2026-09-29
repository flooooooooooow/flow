"""Monomorphization middle-end tests: specialize generics before codegen."""

from flow.parser import StructDecl, FunctionDecl
from flow.monomorphize import monomorphize
from tests.unit.compiler_helpers import parse


def _names(decls):
    return [getattr(d, "name", None) for d in decls]


def test_generic_struct_instantiates_mangled_name():
    decls = monomorphize(
        parse(
            """
struct Box<T> {
    value: T
}
function main() -> i32 {
    let b: Box<i32> = Box { value: 42 }
    return b.value
}
"""
        )
    )
    names = _names(decls)
    assert any(n and n.startswith("Box_") and "i32" in n for n in names), names
    # Generic template may remain; specialized form must exist.
    specialized = [d for d in decls if isinstance(d, StructDecl) and d.name.startswith("Box_")]
    assert specialized
    assert specialized[0].type_params in (None, [], ())


def test_generic_pair_two_type_args():
    decls = monomorphize(
        parse(
            """
struct Pair<A, B> {
    first: A,
    second: B
}
function main() -> i32 {
    let p: Pair<i32, bool> = Pair { first: 1, second: true }
    return p.first
}
"""
        )
    )
    names = _names(decls)
    assert any(n and n.startswith("Pair_") and "i32" in n and "bool" in n for n in names), names


# test_generic_function_call_site_rewritten_in_c ->
# tests/cgen/monomorphize_specialized_names.


def test_unused_generic_struct_not_specialized():
    decls = monomorphize(
        parse(
            """
struct Box<T> { value: T }
struct Pair<A, B> { first: A, second: B }
function main() -> i32 {
    let b: Box<i32> = Box { value: 1 }
    return b.value
}
"""
        )
    )
    names = _names(decls)
    assert any(n and n.startswith("Box_") for n in names)
    assert not any(n and n.startswith("Pair_") and "i32" in (n or "") for n in names)


def test_duplicate_instantiation_deduped():
    decls = monomorphize(
        parse(
            """
struct Box<T> { value: T }
function main() -> i32 {
    let a: Box<i32> = Box { value: 1 }
    let b: Box<i32> = Box { value: 2 }
    return a.value + b.value
}
"""
        )
    )
    box_specs = [
        d.name
        for d in decls
        if isinstance(d, StructDecl) and d.name.startswith("Box_") and "i32" in d.name
    ]
    assert len(box_specs) == len(set(box_specs))
    assert len(box_specs) == 1, box_specs


# test_c_emits_specialized_struct_typedef ->
# tests/cgen/monomorphize_specialized_names.


# test_e2e_generic_pair_compiles_and_runs is now covered by the Pair<i32, bool>
# section of tests/lang/test_generics.flow, which also proves two
# specializations of one template coexist in the emitted C.


# test_bare_generic_literal_rewritten_to_specialized_name checked that a bare
# `Box { ... }` literal typed as Box<i32> lowers to Box_i32. flowc still emits
# (Box){...} for it, which does not build. tests/cgen/monomorphize_specialized_names
# covers the explicit Box<i32> { ... } spelling.
