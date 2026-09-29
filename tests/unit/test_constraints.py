"""Tests for `always { }` / `never { }` runtime invariants.

Card: constraints (docs/vision/north-star.md §5.4).
Covers: parse shapes, contextual-keyword non-regression, validation,
and the lowered Name_check function. The generated C and the runtime
panic are covered by tests/cgen/constraints_*.
"""

import pytest

from flow.parser import (
    BinaryOperation,
    FlowDecl,
    FlowSyntaxError,
    FunctionDecl,
    Lexer,
    Parser,
)
from flow.type_checker import TypeChecker


BOUNDED = """
flow Bound {
    state x : f64 = 0.0
    x evolves as 1.0
    always {
        x < 10.0
        x > -1.0
    }
    never {
        x < -0.5
    }
}
"""


def parse_raw(code: str):
    return Parser(Lexer(code), source=code).parse(expand_flows=False)


def parse_lowered(code: str):
    return Parser(Lexer(code), source=code).parse()


class TestParseShapes:
    def test_always_and_never_ast(self):
        flow = next(d for d in parse_raw(BOUNDED) if isinstance(d, FlowDecl))
        assert len(flow.alwayses) == 1
        assert len(flow.alwayses[0].clauses) == 2
        assert all(
            isinstance(c.expr, BinaryOperation)
            for c in flow.alwayses[0].clauses
        )
        assert "x < 10.0" in flow.alwayses[0].clauses[0].text
        assert len(flow.nevers) == 1
        assert len(flow.nevers[0].clauses) == 1
        assert "x < -0.5" in flow.nevers[0].clauses[0].text

    def test_never_conjunction_is_one_boolean_expr(self):
        code = """
flow F {
    state a : f64 = 0.0
    state b : f64 = 0.0
    a evolves as 0.0
    never {
        a > 1.0 && b > 1.0
    }
}
"""
        flow = next(d for d in parse_raw(code) if isinstance(d, FlowDecl))
        clause = flow.nevers[0].clauses[0]
        assert isinstance(clause.expr, BinaryOperation)
        assert clause.expr.operator == "&&"


class TestContextualKeywords:
    def test_always_never_as_identifiers(self):
        code = """
function always_fn(never: i32) -> i32 {
    return never + 1
}

function main() -> i32 {
    let always: i32 = 1
    let never: i32 = 2
    return always_fn(always + never) - 4
}
"""
        decls = parse_lowered(code)
        assert not any(isinstance(d, FlowDecl) for d in decls)
        result = TypeChecker().check(decls)
        assert result.errors == []

    def test_state_named_always_still_parses(self):
        code = """
flow F {
    state always : f64 = 0.0
    always evolves as 1.0
}
"""
        flow = next(d for d in parse_raw(code) if isinstance(d, FlowDecl))
        assert [s.name for s in flow.states] == ["always"]
        assert flow.alwayses == []


class TestValidation:
    def check_error(self, code: str, fragment: str):
        with pytest.raises(FlowSyntaxError) as excinfo:
            parse_lowered(code)
        assert fragment in str(excinfo.value)

    def test_empty_always_rejected(self):
        self.check_error(
            """
flow F {
    state x : f64 = 0.0
    x evolves as 1.0
    always { }
}
""",
            "needs at least one boolean expression",
        )

    def test_non_boolean_clause_rejected(self):
        self.check_error(
            """
flow F {
    state x : f64 = 0.0
    x evolves as 1.0
    always {
        x + 1.0
    }
}
""",
            "must be a boolean expression",
        )

    def test_impure_clause_rejected(self):
        self.check_error(
            """
extern { function printf(fmt: string, val: f64) -> i32 }
flow F {
    state x : f64 = 0.0
    x evolves as 1.0
    always {
        printf("%f", x) == 0
    }
}
""",
            "cannot be proven pure",
        )


class TestLowering:
    def test_lowered_is_strict_clean(self):
        result = TypeChecker().check(parse_lowered(BOUNDED))
        assert result.errors == []

    def test_no_check_without_invariants(self):
        code = """
flow F {
    state x : f64 = 0.0
    x evolves as 1.0
}
"""
        names = {
            d.name for d in parse_lowered(code) if isinstance(d, FunctionDecl)
        }
        assert "F_check" not in names
