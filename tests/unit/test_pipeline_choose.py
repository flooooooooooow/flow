"""Unit tests for the `choose` pipeline stage.

`src |> choose selector { A => f, B => g }` selects which stage runs based on
`selector`, lowering to a hoisted `let mut __choose_N` plus a `match` that
assigns the chosen arm — so no value-form `match` is needed.
"""

import pytest

from flow.parser import (
    Lexer,
    Parser,
    FunctionCall,
    Variable,
    VarDecl,
    MatchStatement,
    FunctionDecl,
)
from flow.c_generator import flow_to_c
from flow.type_checker import TypeChecker


PRELUDE = """
enum Mode { Slow, Fast }
function f(x: i32) -> i32 { return x * 2 }
function g(x: i32) -> i32 { return x * 3 }
function norm(x: i32) -> i32 { return x + 1 }
function choose(x: i32) -> i32 { return x }
"""


def _main(body: str):
    src = PRELUDE + "function main() -> i32 {\n    let m: Mode = Mode { tag: Mode_Slow }\n" + body + "\n    return 0\n}"
    decls = Parser(Lexer(src)).parse()
    return decls, next(
        d for d in decls if isinstance(d, FunctionDecl) and d.name == "main"
    )


def test_choose_lowers_to_temp_and_match():
    _, main = _main("    let r = 5 |> choose m.tag { Mode_Slow => f, Mode_Fast => g }")
    kinds = [type(s).__name__ for s in main.body.statements]
    # let m ; let mut __choose_0 ; match ; let r = __choose_0 ; return
    assert "VarDecl" in kinds and "MatchStatement" in kinds
    temp = next(s for s in main.body.statements
                if isinstance(s, VarDecl) and s.name.startswith("__choose"))
    assert temp.is_mutable and temp.type.name == "i32"  # inferred from f/g
    match = next(s for s in main.body.statements if isinstance(s, MatchStatement))
    # each arm assigns the temp from the chosen function applied to the source
    assert len(match.cases) == 2
    r = next(s for s in main.body.statements if getattr(s, "name", None) == "r")
    assert isinstance(r.initializer, Variable) and r.initializer.name == temp.name


def test_choose_arm_applies_source():
    _, main = _main("    let r = 5 |> choose m.tag { Mode_Slow => f, Mode_Fast => g }")
    match = next(s for s in main.body.statements if isinstance(s, MatchStatement))
    body0 = match.cases[0].body.statements[0]  # __choose_0 = f(5)
    assert isinstance(body0.value, FunctionCall) and body0.value.name == "f"
    assert body0.value.arguments[0].value == "5"


def test_choose_result_continues_pipeline():
    _, main = _main("    let r = 5 |> choose m.tag { Mode_Slow => f, Mode_Fast => g } |> norm")
    r = next(s for s in main.body.statements if getattr(s, "name", None) == "r")
    # r = norm(__choose_0)
    assert isinstance(r.initializer, FunctionCall) and r.initializer.name == "norm"
    assert r.initializer.arguments[0].name.startswith("__choose")


def test_nontrivial_source_hoisted_once():
    _, main = _main("    let r = f(9) |> choose m.tag { Mode_Slow => f, Mode_Fast => g }")
    srcs = [s for s in main.body.statements
            if isinstance(s, VarDecl) and s.name.startswith("__fork_src")]
    assert len(srcs) == 1  # f(9) evaluated once


def test_bare_choose_stays_a_call():
    _, main = _main("    let r = 5 |> choose")
    r = next(s for s in main.body.statements if getattr(s, "name", None) == "r")
    assert isinstance(r.initializer, FunctionCall) and r.initializer.name == "choose"


def test_choose_with_parens_stays_a_call():
    _, main = _main("    let r = 5 |> choose(7)")
    r = next(s for s in main.body.statements if getattr(s, "name", None) == "r")
    assert isinstance(r.initializer, FunctionCall) and r.initializer.name == "choose"
    assert len(r.initializer.arguments) == 2  # choose(5, 7)


def test_choose_compiles_and_is_strict_clean():
    decls, _ = _main("    let r = 5 |> choose m.tag { Mode_Slow => f, Mode_Fast => g }")
    assert TypeChecker().check(decls).errors == []
    c = flow_to_c(decls)
    assert "__choose_0" in c
