"""Escaping HOF ABI: (T)->R fat-pointer closures."""

from flow.parser import parse_flow_code
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


# The typedef and ABI shape check is tests/cgen/escaping_closures_fn_type.
# The three end-to-end runs (an annotated local fn-typed closure, a closure
# returned from a function, and one passed as a higher-order parameter) are
# now tests/lang/test_closures.flow.


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
