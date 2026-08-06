"""
Tests for automatic closure environment capture (flow-closure-capture).

A capturing lambda lowers to a lifted static C function plus a per-lambda
closure struct `lambda_N_closure { fn, env }`. The env snapshots each
captured variable by value at the point of creation, and call sites pass
`&var.env` as a hidden first argument. Non-capturing lambdas keep their
bare-function-pointer form: the expression stays `&lambda_N` and the
lifted function's signature contains only the declared parameters.
"""

from flow.parser import parse_flow_code
from flow.c_generator import flow_to_c


def gen(main_body: str, prelude: str = "") -> str:
    code = prelude + "function main() -> i32 {\n%s\n    return 0\n}\n" % main_body
    return flow_to_c(parse_flow_code(code))


def test_env_struct_emitted_and_populated():
    c = gen(
        """
    let a: i32 = 1
    let b: i32 = 2
    let f = |x: i32| -> i32 { return a + b + x }
    let r: i32 = f(3)
"""
    )
    assert "typedef struct { int32_t a; int32_t b; } lambda_1_env;" in c
    assert (
        "typedef struct { int32_t (*fn)(lambda_1_env*, int32_t); "
        "lambda_1_env env; } lambda_1_closure;" in c
    )
    # Env is populated by value at the creation site.
    assert ".fn = &lambda_1" in c
    assert ".env = { .a = a, .b = b }" in c
    # The body reads captures through the env pointer.
    assert "_env->a" in c and "_env->b" in c


def test_call_site_passes_env():
    c = gen(
        """
    let a: i32 = 1
    let f = |x: i32| -> i32 { return a + x }
    let r: i32 = f(3)
"""
    )
    assert "f.fn(&f.env, 3)" in c
    # No stale comment-based env emission remains.
    assert "/* closure env:" not in c


def test_capture_substitution_is_token_safe():
    # Old line.replace rewriting corrupted identifiers containing a capture
    # name as a substring (capture `x` mangled `x_total`).
    c = gen(
        """
    let x: i32 = 5
    let f = |x_total: i32| -> i32 { return x_total + x }
    let r: i32 = f(1)
"""
    )
    assert "_env->x_total" not in c
    assert "(x_total + _env->x)" in c


def test_noncapturing_lambda_stays_bare_pointer():
    c = gen(
        """
    let f = |x: i32| -> i32 { return x * 2 }
    let r: i32 = f(21)
"""
    )
    # Expression form and ABI unchanged: plain pointer, no env anywhere.
    assert "&lambda_1" in c
    assert "lambda_1_env" not in c
    assert "static int32_t lambda_1(int32_t x)" in c
    assert "f(21)" in c


def test_local_declaration_inside_body_is_not_a_capture():
    c = gen(
        """
    let f = |x: i32| -> i32 {
        let y: i32 = 2
        return x + y
    }
    let r: i32 = f(1)
"""
    )
    # y is a body local; the lambda captures nothing.
    assert "lambda_1_env" not in c
    assert "&lambda_1" in c


def test_constants_are_not_captured():
    c = gen(
        """
    let f = |x: i32| -> i32 { return x + LIMIT }
    let r: i32 = f(1)
""",
        prelude="const LIMIT: i32 = 10\n",
    )
    # File-scope constants stay reachable from the lifted function.
    assert "lambda_1_env" not in c
    assert "LIMIT" in c


def test_env_snapshot_uses_creation_scope_types():
    c = gen(
        """
    let scale: f64 = 1.5
    let f = |x: f64| -> f64 { return x * scale }
    let r: f64 = f(2.0)
"""
    )
    assert "typedef struct { double scale; } lambda_1_env;" in c


def test_capture_through_struct_literal_field():
    # Free names inside struct-literal fields must be captured; previously
    # StructLiteral was skipped by free-variable collection, so `n` stayed
    # a bare identifier in the lifted function and failed to compile.
    c = gen(
        """
    let n: i32 = 5
    let f = |z: i32| -> i32 {
        let q: Point = Point { x: n, y: z }
        return q.x + q.y
    }
    let r: i32 = f(3)
""",
        prelude="struct Point { x: i32, y: i32 }\n",
    )
    assert "typedef struct { int32_t n; } lambda_1_env;" in c
    assert "_env->n" in c
    assert ".env = { .n = n }" in c


def test_capture_through_array_literal_element():
    c = gen(
        """
    let n: i32 = 7
    let f = |z: i32| -> i32 {
        let xs: [i32; 2] = [n, z]
        return xs[0] + xs[1]
    }
    let r: i32 = f(3)
"""
    )
    assert "typedef struct { int32_t n; } lambda_1_env;" in c
    assert "_env->n" in c


def test_capture_struct_value_via_field_access():
    c = gen(
        """
    let p: Point = Point { x: 1, y: 2 }
    let f = |z: i32| -> i32 { return p.x + z }
    let r: i32 = f(3)
""",
        prelude="struct Point { x: i32, y: i32 }\n",
    )
    assert "typedef struct { Point p; } lambda_1_env;" in c
    assert "_env->p.x" in c


# The end-to-end compile-and-run cases (capture of one and two variables,
# snapshot semantics, a lambda in a loop, nested lambdas, a mutating capture
# staying local, and a non-capturing lambda) are now tests/lang/test_closures.flow.
# What stays here is the generated-C shape: the env struct, the call-site
# argument, and the substitution rules.
