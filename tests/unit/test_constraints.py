"""Tests for `always { }` / `never { }` runtime invariants.

Card: constraints (docs/vision/north-star.md §5.4).
Covers: parse shapes, contextual-keyword non-regression, validation,
generated-C structure (Name_check + post-output call from Name_step),
and end-to-end hold / panic behavior.
"""

import pytest

from flow.c_generator import flow_to_c
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


class TestCodegenStructure:
    def generate(self, code: str = BOUNDED) -> str:
        return flow_to_c(parse_lowered(code))

    def test_check_function_emitted(self):
        c = self.generate()
        assert "int32_t Bound_check(Bound* self)" in c
        assert "Bound_check(self)" in c
        assert "invariant violated" in c
        assert "exit(1)" in c
        # Negation must parenthesize the comparison (C precedence).
        assert "(!(self->x < 10.0))" in c

    def test_check_called_after_outputs_when_present(self):
        code = """
flow F {
    state x : f64 = 0.0
    output y : f64 = x
    x evolves as 1.0
    always { x < 100.0 }
}
"""
        c = flow_to_c(parse_lowered(code))
        step = c.split("void F_step(F* self, double dt) {", 1)[1].split("\n}", 1)[0]
        out_at = step.index("F_outputs(self)")
        check_at = step.index("F_check(self)")
        assert out_at < check_at

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


class TestCheckLowering:
    """Runtime behavior is encoded in generated C; assert the shape here.

    Full compile-and-run checks live with the other evolves e2e tests when
    the host can execute clang binaries; this card's unit suite stays
    parse/check/codegen so it runs in restricted environments.
    """

    def test_check_returns_clause_indices(self):
        c = flow_to_c(parse_lowered(BOUNDED))
        check = c.split("int32_t Bound_check(Bound* self) {", 1)[1]
        check = check.split("\n}", 1)[0]
        # always clauses first (indices 1, 2), then never (index 3).
        assert "(!(self->x < 10.0))" in check
        assert "return 1;" in check
        assert "(!(self->x > (-1.0)))" in check
        assert "return 2;" in check
        assert "self->x < (-0.5)" in check
        assert "return 3;" in check
        assert "return 0;" in check

    def test_step_embeds_panic_on_violation(self):
        c = flow_to_c(parse_lowered("""
flow Bound {
    state x : f64 = 0.0
    x evolves as 1.0
    always { x < 1.5 }
}
"""))
        step = c.split("void Bound_step(Bound* self, double dt) {", 1)[1]
        step = step.split("\n}", 1)[0]
        assert "Bound_check(self)" in step
        assert "invariant violated: x < 1.5" in step
        assert "exit(1)" in step

    def test_never_clause_is_positive_test(self):
        c = flow_to_c(parse_lowered("""
flow F {
    state x : f64 = 0.0
    x evolves as 1.0
    never { x < -0.5 }
}
"""))
        check = c.split("int32_t F_check(F* self) {", 1)[1]
        check = check.split("\n}", 1)[0]
        # never: fire when the expression is true (no negation).
        assert "if (self->x < (-0.5))" in check
        assert "!(self->x < (-0.5))" not in check
