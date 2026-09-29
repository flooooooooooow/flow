"""Parser torture: deep nesting and combinatorial surface stress."""

import pytest

from flow.parser import parse_flow_code
from tests.unit.compiler_helpers import errors


def _nested_ifs(depth: int) -> str:
    body = "return 0"
    for i in range(depth):
        body = f"if {i} == {i} {{\n{body}\n}} else {{\nreturn 1\n}}"
    return f"function main() -> i32 {{\n{body}\n}}"


def _nested_whiles(depth: int) -> str:
    body = "let x: i32 = 0"
    for _ in range(depth):
        body = f"while false {{\n{body}\n}}"
    return f"function main() -> i32 {{\n{body}\nreturn 0\n}}"


def _nested_structs(depth: int) -> str:
    """S0 { v }; S1 { inner: S0 }; ... Sd { inner: S(d-1) } with nested literal."""
    lines = ["struct S0 { v: i32 }"]
    for i in range(1, depth + 1):
        lines.append(f"struct S{i} {{ inner: S{i - 1} }}")
    lit = "S0 { v: 7 }"
    for i in range(1, depth + 1):
        lit = f"S{i} {{ inner: {lit} }}"
    access = "x" + (".inner" * depth) + ".v"
    lines.append(
        f"""
function main() -> i32 {{
    let x: S{depth} = {lit}
    if {access} == 7 {{
        return 0
    }}
    return 1
}}
"""
    )
    return "\n".join(lines)


@pytest.mark.parametrize("depth", [8, 16, 32])
def test_nested_if_parses(depth: int):
    decls = parse_flow_code(_nested_ifs(depth))
    assert any(getattr(d, "name", None) == "main" for d in decls)


@pytest.mark.parametrize("depth", [8, 16, 32])
def test_nested_while_parses(depth: int):
    decls = parse_flow_code(_nested_whiles(depth))
    assert any(getattr(d, "name", None) == "main" for d in decls)


@pytest.mark.parametrize("depth", [3, 6, 10])
def test_nested_struct_parses(depth: int):
    src = _nested_structs(depth)
    decls = parse_flow_code(src)
    assert len([d for d in decls if getattr(d, "name", "").startswith("S")]) >= depth


def test_deep_expression_parens_bounded():
    expr = "(" * 40 + "1" + ")" * 40
    src = f"function main() -> i32 {{ return {expr} }}"
    try:
        parse_flow_code(src)
    except SyntaxError:
        pass
    except RecursionError:
        pytest.fail("RecursionError: parser depth limit missing")


def test_match_bool_still_typechecks():
    errs = errors(
        """
function f(b: bool) -> i32 {
    match b {
        true => { return 1 }
        false => { return 0 }
    }
    return -1
}
function main() -> i32 { return f(true) - 1 }
"""
    )
    assert errs == []


# The compile-and-run stress cases live in tests/lang/test_torture.flow
# (struct nest, sixty-four locals, thirty-two functions, sixteen-deep if)
# and tests/cgen/torture_nesting_struct10 (a ten-deep struct nest).
