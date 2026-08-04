"""English `and`/`or` as logical ops and as callables (verify corpus)."""

from __future__ import annotations

import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_SRC = os.path.join(_REPO, "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from flow.parser import Lexer, Parser, BinaryOperation, FunctionCall  # noqa: E402


def _parse(src: str):
    return Parser(Lexer(src), source=src).parse()


def test_english_and_or_in_expression():
    decls = _parse(
        """
        function main() -> bool {
            return a == 1 and b == 2 or c == 3
        }
        """
    )
    body = decls[0].body.statements[0].value
    assert isinstance(body, BinaryOperation)
    assert body.operator == "||"


def test_and_or_as_function_calls():
    decls = _parse(
        """
        function main() -> i32 {
            return and(xor(1, 0), or(0, 1))
        }
        """
    )
    call = decls[0].body.statements[0].value
    assert isinstance(call, FunctionCall)
    assert call.name == "and"


def test_and_as_function_name():
    decls = _parse(
        """
        function and(a: i32, b: i32) -> i32 {
            return a * b
        }
        """
    )
    assert decls[0].name == "and"


def test_full_adder_example_parses():
    path = os.path.join(_REPO, "examples/verify/circuits/full_adder.flow")
    with open(path, encoding="utf-8") as f:
        src = f.read()
    decls = _parse(src)
    names = {getattr(d, "name", None) or getattr(d, "claim_path", None) for d in decls}
    assert "FullAdder" in names
    assert "and" in names
    assert "FullAdder/out.correct" in names
