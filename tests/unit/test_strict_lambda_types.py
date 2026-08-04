"""
Strict-mode typing for lambdas and closure variables (flow-strict-closure-types).

Lambda parameters bind in the lambda's own scope, lambda expressions have
function type, and variables holding lambdas are callable with argument
checking. Before this landed, strict mode reported "Undefined variable"
for lambda parameters and "not a function" for closure variables.
"""

from flow.parser import parse_flow_code
from flow.type_checker import TypeChecker


def check_strict(code: str):
    ast = parse_flow_code(code)
    checker = TypeChecker()
    checker.strict = True
    result = checker.check(ast)
    return result.errors


def test_lambda_parameter_binds_in_scope():
    errors = check_strict(
        """
function main() -> i32 {
    let f = |x: i32| -> i32 { return x + 1 }
    return 0
}
"""
    )
    assert not any("Undefined variable 'x'" in e for e in errors), errors


def test_closure_variable_is_callable():
    errors = check_strict(
        """
function main() -> i32 {
    let a: i32 = 10
    let f = |x: i32| -> i32 { return x + a }
    let r: i32 = f(5)
    return r
}
"""
    )
    assert not any("is not a function" in e for e in errors), errors
    assert not any("No matching overload" in e for e in errors), errors


def test_closure_call_result_type_flows():
    errors = check_strict(
        """
function want_i32(v: i32) -> i32 { return v }
function main() -> i32 {
    let f = |x: i32| -> i32 { return x * 2 }
    let r: i32 = want_i32(f(3))
    return r
}
"""
    )
    assert errors == [], errors


def test_closure_wrong_argument_count_rejected():
    errors = check_strict(
        """
function main() -> i32 {
    let f = |x: i32| -> i32 { return x }
    let r: i32 = f(1, 2)
    return r
}
"""
    )
    assert any("overload" in e.lower() or "argument" in e.lower() for e in errors), errors


def test_strict_closure_runtime_corpus_file_passes():
    with open("tests/core/test_closure_capture.flow") as fh:
        code = fh.read()
    errors = check_strict(code)
    assert errors == [], errors
