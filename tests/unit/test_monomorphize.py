"""Monomorphization middle-end tests — specialize generics before codegen."""

import pytest

from flow.parser import StructDecl, FunctionDecl
from flow.monomorphize import monomorphize
from tests.unit.compiler_helpers import parse, to_c


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


def test_generic_function_call_site_rewritten_in_c():
    c = to_c(
        """
function identity<T>(x: T) -> T { return x }
function main() -> i32 {
    let a: i32 = identity<i32>(7)
    return a
}
"""
    )
    assert "identity_i32" in c or "identity<" not in c
    assert "identity<i32>" not in c


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


def test_c_emits_specialized_struct_typedef():
    c = to_c(
        """
struct Box<T> { value: T }
function main() -> i32 {
    let b: Box<i32> = Box { value: 9 }
    return b.value
}
"""
    )
    assert "typedef struct Box_" in c or "struct Box_" in c
    assert "i32" in c


# test_e2e_generic_pair_compiles_and_runs is now covered by the Pair<i32, bool>
# section of tests/lang/test_generics.flow, which also proves two
# specializations of one template coexist in the emitted C.


def test_bare_generic_literal_rewritten_to_specialized_name():
    c = to_c(
        """
struct Box<T> { value: T }
function main() -> i32 {
    let b: Box<i32> = Box { value: 9 }
    return b.value - 9
}
"""
    )
    assert "Box_i32" in c or "Box_N3_i32" in c
    # Must not cast the specialized variable from the bare generic type alone
    assert "(Box){" not in c or "Box_i32" in c
