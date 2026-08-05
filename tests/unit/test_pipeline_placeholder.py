"""Unit tests for the `|>` pipeline placeholder `_`.

Default piping prepends the piped value (`x |> f(y)` -> `f(x, y)`). A single
`_` in the piped call overrides that, routing the piped value to the marked
slot instead (`x |> clamp(0.0, _, 1.0)` -> `clamp(0.0, x, 1.0)`).
"""

import pytest

from flow.parser import (
    Lexer,
    Parser,
    FunctionCall,
    MethodCall,
    Variable,
    Literal,
    FunctionDecl,
)


def _lower(expr_src: str):
    """Parse `let r = <expr_src>` in main and return the lowered initializer."""
    src = "function main() -> i32 { let r = " + expr_src + "\nreturn 0 }"
    decls = Parser(Lexer(src)).parse()
    fn = next(d for d in decls if isinstance(d, FunctionDecl) and d.name == "main")
    return fn.body.statements[0].initializer


def _render(node) -> str:
    if isinstance(node, FunctionCall):
        return node.name + "(" + ", ".join(_render(a) for a in node.arguments) + ")"
    if isinstance(node, MethodCall):
        inner = ", ".join(_render(a) for a in node.arguments)
        return _render(node.object) + "." + node.method + "(" + inner + ")"
    if isinstance(node, Variable):
        return node.name
    if isinstance(node, Literal):
        return str(node.value)
    return type(node).__name__


def test_default_prepend_unchanged():
    assert _render(_lower("x |> f")) == "f(x)"
    assert _render(_lower("x |> f(y)")) == "f(x, y)"


def test_placeholder_middle_slot():
    assert _render(_lower("x |> clamp(0.0, _, 1.0)")) == "clamp(0.0, x, 1.0)"


def test_placeholder_leading_slot():
    # Explicit leading `_` is equivalent to the default prepend.
    assert _render(_lower("x |> mix(_, side, 0.5)")) == "mix(x, side, 0.5)"


def test_placeholder_in_chain():
    assert _render(_lower("a |> f() |> g(_, 2)")) == "g(f(a), 2)"


def test_placeholder_in_method_call():
    assert _render(_lower("x |> obj.m(_, y)")) == "obj.m(x, y)"


def test_multiple_placeholders_rejected():
    with pytest.raises(Exception) as exc:
        _lower("x |> mix(_, _, 0.5)")
    assert "_" in str(exc.value)
