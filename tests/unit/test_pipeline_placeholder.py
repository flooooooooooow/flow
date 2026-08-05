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
    StructLiteral,
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
    if isinstance(node, StructLiteral):
        inner = ", ".join(f + ": " + _render(v) for f, v in node.fields)
        return node.struct_name + "{" + inner + "}"
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


# --- Fork blocks: `source |> Record { field = pipeline, ... }` -----------------


def test_fork_block_applies_source_to_each_branch():
    r = _lower("mic |> Analysis { spectrum = fft |> magnitude, loudness = rms }")
    assert isinstance(r, StructLiteral)
    assert r.struct_name == "Analysis"
    assert _render(r) == "Analysis{spectrum: magnitude(fft(mic)), loudness: rms(mic)}"


def test_fork_branches_support_args_and_placeholder():
    r = _lower("src |> R { a = f, b = g(2), c = h(_, k) }")
    assert _render(r) == "R{a: f(src), b: g(src, 2), c: h(src, k)}"


def test_fork_result_can_continue_pipeline():
    r = _lower("src |> R { only = f } |> normalize")
    assert _render(r) == "normalize(R{only: f(src)})"


def test_fork_source_may_be_a_pipeline_stage():
    r = _lower("x |> frames(1024) |> Out { lo = lowpass, hi = highpass }")
    assert _render(r) == (
        "Out{lo: lowpass(frames(x, 1024)), hi: highpass(frames(x, 1024))}"
    )


def test_fork_colon_field_rejected():
    with pytest.raises(Exception) as exc:
        _lower("src |> R { a: f }")
    assert "'='" in str(exc.value)


def test_fork_empty_block_rejected():
    with pytest.raises(Exception):
        _lower("src |> R { }")


def test_fork_duplicate_field_rejected():
    with pytest.raises(Exception) as exc:
        _lower("src |> R { a = f, a = g }")
    assert "Duplicate" in str(exc.value)


# --- Anonymous fork records: `source |> { a = f, b = g }` ---------------------

from flow.parser import StructDecl  # noqa: E402


def _parse_program(src: str):
    return Parser(Lexer(src)).parse()


_ANON_SRC = """
function twice(x: i32) -> i32 {{ return x * 2 }}
function square(x: i32) -> i32 {{ return x * x }}
function main() -> i32 {{
    let n: i32 = 6
    let s = n |> {{ {branches} }}
    return 0
}}
"""


def _anon(branches: str):
    decls = _parse_program(_ANON_SRC.format(branches=branches))
    structs = [d for d in decls if isinstance(d, StructDecl)]
    main = next(d for d in decls if isinstance(d, FunctionDecl) and d.name == "main")
    lit = main.body.statements[1].initializer
    return structs, lit


def test_anon_fork_synthesizes_struct_and_literal():
    structs, lit = _anon("doubled = twice, squared = square")
    assert len(structs) == 1
    s = structs[0]
    assert [(p.name, p.type.name) for p in s.fields] == [
        ("doubled", "i32"),
        ("squared", "i32"),
    ]
    # The fork lowers to a struct literal of the synthesized record.
    assert isinstance(lit, StructLiteral)
    assert lit.struct_name == s.name
    assert _render(lit) == s.name + "{doubled: twice(n), squared: square(n)}"


def test_anon_fork_dedups_identical_records():
    src = """
    function f(x: i32) -> i32 { return x }
    function g(x: i32) -> i32 { return x }
    function main() -> i32 {
        let a = 1 |> { p = f, q = g }
        let b = 2 |> { p = f, q = g }
        return 0
    }
    """
    structs = [d for d in _parse_program(src) if isinstance(d, StructDecl)]
    assert len(structs) == 1


def test_anon_fork_uninferrable_field_errors():
    src = """
    function main() -> i32 {
        let obj = 5
        let s = obj |> { bad = obj.method() }
        return 0
    }
    """
    with pytest.raises(Exception) as exc:
        _parse_program(src)
    assert "infer" in str(exc.value)
