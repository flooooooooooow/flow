"""Counted-loop rotation (#473) and trivial accessor inlining (#474)."""

from flow.mlir_canonicalize import canonicalize_counted_loops, find_trivial_accessors
from flow.mlir_generator import MLIRGenerator
from flow.parser import Assignment, BinaryOperation, WhileStatement
from tests.unit.compiler_helpers import parse


def _main_body(source: str):
    decls = parse(source)
    main = next(d for d in decls if getattr(d, "name", None) == "main")
    return canonicalize_counted_loops(main.body).statements


COUNTED = """
function main() -> i32 {
    let mut count: i32 = 5
    let mut acc: i32 = 0
    while true {
        acc = acc + 1
        if count == 0 {
            break
        }
        count = count - 1
    }
    return acc
}
"""


def test_counted_loop_is_rotated_into_a_latch_compare():
    statements = _main_body(COUNTED)
    # The prefix is peeled ahead of the loop, and the loop now tests the counter.
    peeled = statements[2]
    assert isinstance(peeled, Assignment) and peeled.target == "acc"
    loop = statements[3]
    assert isinstance(loop, WhileStatement)
    assert isinstance(loop.condition, BinaryOperation)
    assert loop.condition.operator == "!="
    assert loop.condition.left.name == "count"


def test_rotated_body_keeps_the_decrement_before_the_peeled_prefix():
    loop = _main_body(COUNTED)[3]
    body = loop.body.statements
    # Suffix first (the decrement), then the duplicated prefix.
    assert [getattr(s, "target", None) for s in body] == ["count", "acc"]
    # The mid-body break is gone; the exit test is the loop condition.
    assert not any(hasattr(s, "then_block") for s in body)


def test_rotated_loop_emits_no_mid_body_exit_branch():
    mlir = MLIRGenerator().generate_module(parse(COUNTED))
    # One conditional branch (the latch test), not a header br plus a body test.
    assert mlir.count("cf.cond_br") == 1, mlir
    assert "arith.cmpi ne" in mlir, mlir


def test_loop_without_a_decrement_is_left_alone():
    statements = _main_body(
        """
function main() -> i32 {
    let mut count: i32 = 5
    while true {
        if count == 0 {
            break
        }
        count = count + 1
    }
    return count
}
"""
    )
    loop = statements[1]
    assert isinstance(loop, WhileStatement)
    assert loop.condition.value == "true"


def test_loop_with_a_second_break_is_left_alone():
    statements = _main_body(
        """
function main() -> i32 {
    let mut count: i32 = 5
    let mut acc: i32 = 0
    while true {
        acc = acc + 1
        if acc > 100 {
            break
        }
        if count == 0 {
            break
        }
        count = count - 1
    }
    return acc
}
"""
    )
    loop = statements[2]
    assert isinstance(loop, WhileStatement)
    assert loop.condition.value == "true"


def test_prefix_declaration_blocks_rotation():
    # `let` in the peeled prefix would land in two different scopes.
    statements = _main_body(
        """
function main() -> i32 {
    let mut count: i32 = 5
    let mut acc: i32 = 0
    while true {
        let bump: i32 = count + 1
        acc = acc + bump
        if count == 0 {
            break
        }
        count = count - 1
    }
    return acc
}
"""
    )
    loop = statements[2]
    assert isinstance(loop, WhileStatement)
    assert loop.condition.value == "true"


def test_break_first_loop_rotates_without_duplicating_anything():
    statements = _main_body(
        """
function main() -> i32 {
    let mut count: i32 = 5
    let mut acc: i32 = 0
    while true {
        if count == 0 {
            break
        }
        acc = acc + 1
        count = count - 1
    }
    return acc
}
"""
    )
    loop = statements[2]
    assert isinstance(loop, WhileStatement)
    assert loop.condition.operator == "!="
    assert [s.target for s in loop.body.statements] == ["acc", "count"]


ACCESSORS = """
let mut dc_yh: i32 = 0
let mut dc_x: i32 = 0

function dc_yh_addr() -> ptr<i32> {
    return &dc_yh
}

function dc_x_value() -> i32 {
    return dc_x
}

function main() -> i32 {
    let p: ptr<i32> = dc_yh_addr()
    return dc_x_value()
}
"""


def test_trivial_accessors_are_detected():
    decls = parse(ACCESSORS)
    globals_ = {"dc_yh", "dc_x"}
    found = find_trivial_accessors(decls, globals_.__contains__)
    assert set(found) == {"dc_yh_addr", "dc_x_value"}


def test_accessor_calls_are_replaced_by_the_global():
    mlir = MLIRGenerator().generate_module(parse(ACCESSORS))
    body = mlir.split("func.func @main")[1]
    assert "func.call @dc_yh_addr" not in body, body
    assert "func.call @dc_x_value" not in body, body
    assert "llvm.mlir.addressof @dc_yh" in body, body
    # The definitions stay for external linkage.
    assert "func.func @dc_yh_addr" in mlir, mlir


def test_functions_with_parameters_are_not_accessors():
    decls = parse(
        """
let mut dc_yh: i32 = 0

function pick(flag: i32) -> i32 {
    return dc_yh
}
"""
    )
    assert find_trivial_accessors(decls, {"dc_yh"}.__contains__) == {}


def test_non_global_returns_are_not_accessors():
    decls = parse(
        """
function loose() -> i32 {
    return 7
}
"""
    )
    assert find_trivial_accessors(decls, {"dc_yh"}.__contains__) == {}
