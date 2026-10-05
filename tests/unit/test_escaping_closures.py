"""Escaping HOF ABI: (T)->R fat-pointer closures."""

from flow.parser import parse_flow_code
from flow.c_generator import flow_to_c
from flow.type_checker import TypeChecker


def test_parse_fn_type():
    from flow.parser import parse_flow_code

    decls = parse_flow_code(
        """
function apply(f: (i32) -> i32, x: i32) -> i32 {
    return f(x)
}
function main() -> i32 { return 0 }
"""
    )
    apply = next(d for d in decls if getattr(d, "name", None) == "apply")
    assert apply.parameters[0].type.name == "fn_i32__i32"


def test_fn_type_typedef_emitted():
    c = flow_to_c(
        parse_flow_code(
            """
function main() -> i32 {
    let n: i32 = 5
    let add_n: (i32) -> i32 = |x: i32| -> i32 { return x + n }
    return add_n(10)
}
"""
        )
    )
    assert "typedef struct" in c and "fn_i32__i32" in c
    assert ".env =" in c
    assert "add_n.fn(add_n.env" in c


# The three end-to-end runs (an annotated local fn-typed closure, a closure
# returned from a function, and one passed as a higher-order parameter) are
# now tests/lang/test_closures.flow. The typedef and ABI shape stay here.


def test_strict_types_accept_fn_annotation():
    checker = TypeChecker()
    checker.strict = True
    result = checker.check(
        parse_flow_code(
            """
function main() -> i32 {
    let n: i32 = 1
    let f: (i32) -> i32 = |x: i32| -> i32 { return x + n }
    return f(0)
}
"""
        )
    )
    assert result.errors == [], result.errors
