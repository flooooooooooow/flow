"""Tests for hybrid events: `when x reaches L { x becomes expr }`.

Card: hybrid-events (docs/vision/north-star.md section 5).
Covers: parse shapes, contextual-keyword non-regression, and validation with
located messages. The generated C is tests/cgen/hybrid_events_ball and the
runtime behaviour is tests/lang/test_hybrid_events.flow.
"""

import pytest

from flow.parser import (
    BinaryOperation,
    FlowDecl,
    FlowSyntaxError,
    FunctionDecl,
    Lexer,
    Literal,
    Parser,
    StructDecl,
    UnaryOperation,
    Variable,
)
from flow.type_checker import TypeChecker


BALL = """
flow Ball {
    state height      : f64 = 2.0
    state velocity    : f64 = 0.0
    param gravity     : f64 = 9.81
    param restitution : f64 = 0.8

    height evolves as velocity
    velocity evolves as -gravity

    when height reaches 0.0 {
        velocity becomes -restitution * velocity
        height becomes 0.0
    }
}
"""


def parse_raw(code: str):
    """Parse without flow lowering, to inspect FlowDecl AST shapes."""
    return Parser(Lexer(code), source=code).parse(expand_flows=False)


def parse_lowered(code: str):
    """Parse with the default flow lowering applied."""
    return Parser(Lexer(code), source=code).parse()


class TestParseShapes:
    def test_when_decl_ast(self):
        decls = parse_raw(BALL)
        flow = next(d for d in decls if isinstance(d, FlowDecl))
        assert len(flow.whens) == 1
        when = flow.whens[0]
        assert when.guard_target == "height"
        assert isinstance(when.threshold, Literal)
        assert [b.target for b in when.body] == ["velocity", "height"]
        # `velocity becomes -restitution * velocity` is a real expression tree.
        assert isinstance(when.body[0].expr, BinaryOperation)
        assert isinstance(when.body[1].expr, Literal)

    def test_param_threshold_and_multiple_events(self):
        code = """
flow F {
    state x : f64 = 0.0
    param ceiling : f64 = 4.0
    x evolves as 1.0
    when x reaches ceiling {
        x becomes 0.0
    }
    when x reaches ceiling / 2.0 {
        x becomes x * 0.5
    }
}
"""
        flow = next(d for d in parse_raw(code) if isinstance(d, FlowDecl))
        assert len(flow.whens) == 2  # declaration order preserved
        assert isinstance(flow.whens[0].threshold, Variable)
        assert flow.whens[0].threshold.name == "ceiling"
        assert isinstance(flow.whens[1].threshold, BinaryOperation)

    def test_negative_literal_threshold(self):
        code = """
flow F {
    state x : f64 = 0.0
    x evolves as -1.0
    when x reaches -2.0 {
        x becomes 0.0
    }
}
"""
        flow = next(d for d in parse_raw(code) if isinstance(d, FlowDecl))
        assert isinstance(flow.whens[0].threshold, UnaryOperation)


class TestContextualKeywords:
    """Programs using the new words as ordinary identifiers must not regress."""

    def test_identifiers_still_work(self):
        code = """
function reaches(when: i32, becomes: i32) -> i32 {
    return when + becomes
}

function main() -> i32 {
    let when: i32 = 1
    let becomes: i32 = 2
    let total: i32 = reaches(when, becomes)
    return total - 3
}
"""
        decls = parse_lowered(code)
        assert not any(isinstance(d, FlowDecl) for d in decls)
        assert {d.name for d in decls if isinstance(d, FunctionDecl)} == {
            "reaches",
            "main",
        }
        result = TypeChecker().check(decls)
        assert result.errors == []

    def test_state_named_when_inside_flow(self):
        # `when` used as a state name still parses; the event form needs
        # `when IDENT reaches`, so `when evolves as ...` stays a dynamics
        # declaration for a state named `when`.
        code = """
flow F {
    state when : f64 = 0.0
    when evolves as 1.0
}
"""
        flow = next(d for d in parse_raw(code) if isinstance(d, FlowDecl))
        assert [s.name for s in flow.states] == ["when"]
        assert [ev.target for ev in flow.evolves] == ["when"]
        assert flow.whens == []

    def test_becomes_and_reaches_as_flow_members(self):
        code = """
flow F {
    state becomes : f64 = 0.0
    param reaches : f64 = 1.0
    becomes evolves as reaches
}
"""
        flow = next(d for d in parse_raw(code) if isinstance(d, FlowDecl))
        assert [s.name for s in flow.states] == ["becomes"]
        assert [p.name for p in flow.params] == ["reaches"]

    def test_when_outside_flow_body_is_rejected(self):
        # In a function body `when` is an ordinary identifier, so the event
        # form does not parse there. FlowSyntaxError subclasses SyntaxError.
        code = """
function main() -> i32 {
    when x reaches 0.0 {
        x becomes 1.0
    }
    return 0
}
"""
        with pytest.raises(SyntaxError):
            parse_lowered(code)


class TestValidation:
    def check_error(self, code: str, fragment: str):
        with pytest.raises(FlowSyntaxError) as excinfo:
            parse_lowered(code)
        assert fragment in str(excinfo.value)
        assert excinfo.value.line, "validation error must carry a line"

    def test_guard_must_be_a_state(self):
        self.check_error(
            """
flow F {
    state x : f64 = 0.0
    x evolves as 1.0
    when ground reaches 0.0 {
        x becomes 0.0
    }
}
""",
            "requires 'ground' to be a declared state",
        )

    def test_guard_must_be_continuous(self):
        self.check_error(
            """
flow F {
    state x : f64 = 0.0
    state mode : f64 = 0.0
    x evolves as 1.0
    when mode reaches 1.0 {
        x becomes 0.0
    }
}
""",
            "requires 'mode' to be a continuous state",
        )

    def test_becomes_target_must_be_a_state(self):
        self.check_error(
            """
flow F {
    state x : f64 = 0.0
    param k : f64 = 2.0
    x evolves as 1.0
    when x reaches 1.0 {
        k becomes 3.0
    }
}
""",
            "requires 'k' to be a declared state",
        )

    def test_duplicate_becomes_rejected(self):
        self.check_error(
            """
flow F {
    state x : f64 = 0.0
    x evolves as 1.0
    when x reaches 1.0 {
        x becomes 0.0
        x becomes 2.0
    }
}
""",
            "two 'becomes' resets",
        )

    def test_threshold_may_not_reference_state(self):
        self.check_error(
            """
flow F {
    state x : f64 = 0.0
    state y : f64 = 1.0
    x evolves as 1.0
    y evolves as 0.5
    when x reaches y {
        x becomes 0.0
    }
}
""",
            "params and literals",
        )

    def test_impure_reset_rejected(self):
        self.check_error(
            """
extern { function printf(fmt: string, val: f64) -> i32 }
flow F {
    state x : f64 = 0.0
    x evolves as 1.0
    when x reaches 1.0 {
        x becomes printf("%f", x) * 1.0
    }
}
""",
            "cannot be proven pure",
        )

    def test_non_becomes_statement_in_when_body_rejected(self):
        self.check_error(
            """
flow F {
    state x : f64 = 0.0
    x evolves as 1.0
    when x reaches 1.0 {
        let y : f64 = 2.0
    }
}
""",
            "Unexpected statement in 'when' body",
        )


# TestCodegenStructure checked the generated C for guard memory, the guard
# check, staged resets and outputs ordering. That is now
# tests/cgen/hybrid_events_ball.

# TestEndToEnd compiled and ran the simultaneous-reset swap and the bouncing
# ball. Both are now tests/lang/test_hybrid_events.flow, which checks the
# same numbers from inside the program.
