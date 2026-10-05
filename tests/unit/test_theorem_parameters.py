"""Theorem parameters may be written without a type (#587).

`docs/language/epistemology.md` has always written

    theorem Nat/+.commutes(a, b) { therefore a + b == b + a }

The parameters name what the claim quantifies over, and their types come from
the claim being referred to, so requiring an annotation would make the
statement of the theorem carry information the theorem does not need. The
parser required one, so every such block failed with
`Expected TokenType.COLON, got TokenType.COMMA`.
"""

import pytest

from flow.c_generator import flow_to_c
from flow.parser import FlowSyntaxError, parse_flow_code


def theorem(source: str):
    return parse_flow_code(source)[0]


def test_untyped_parameters_parse():
    decl = theorem("theorem Nat/+.commutes(a, b) { therefore a + b == b + a }")
    assert [p.name for p in decl.parameters] == ["a", "b"]
    assert [p.type.name for p in decl.parameters] == ["unconstrained"] * 2


def test_typed_parameters_still_carry_their_type():
    decl = theorem("theorem Nat/+.zero-left(m: Nat) { therefore 0 + m == m }")
    assert [(p.name, p.type.name) for p in decl.parameters] == [("m", "Nat")]


def test_the_two_forms_mix():
    decl = theorem("theorem P/q.mixed(a, b: Nat, c) { therefore a == c }")
    assert [(p.name, p.type.name) for p in decl.parameters] == [
        ("a", "unconstrained"), ("b", "Nat"), ("c", "unconstrained")
    ]


def test_a_function_parameter_still_needs_its_type():
    """Only theorems relax this; an ordinary signature is unchanged."""
    with pytest.raises(FlowSyntaxError):
        parse_flow_code("function f(a, b) -> i32 { return 0 }")


def test_proof_statements_do_not_stop_codegen():
    """`assume` and `therefore` are for the proof layer and emit nothing.

    The C backend raised NotImplementedError on AssumeStmt, so a file
    containing one could not be compiled at all.
    """
    c = flow_to_c(parse_flow_code("""
theorem Nat/+.commutes(a, b) {
    assume Nat/+.zero-right(a)
    therefore a + b == b + a
}

function main() -> i32 { return 0 }
"""))
    assert "int32_t main" in c
