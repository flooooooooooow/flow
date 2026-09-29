"""Tests for explicit time in flow blocks: duration literals,
`every <duration> { ... }`, and the `solver` block.

Card: time-blocks (docs/vision/north-star.md sections 2.3 and 4).
Covers: duration literal parsing (every suffix, i64 nanosecond values),
contextual-keyword non-regression (suffix words stay identifiers),
every-block and solver-block parse shapes, validation with located
messages.

The generated C and the runtime behaviour are checked under flowc by
tests/cgen/time_blocks_every_shape, tests/lang/test_time_blocks.flow and
tests/lang/test_time_blocks_rk4.flow.
"""

import pytest

from flow.parser import (
    DURATION_UNIT_NS,
    BinaryOperation,
    FlowDecl,
    FlowSyntaxError,
    FunctionDecl,
    Lexer,
    Parser,
)
from flow.type_checker import TypeChecker


COUNTER = """
flow Counter {
    state t     : f64 = 0.0
    state ticks : f64 = 0.0

    solver { dt 1 ms  method euler }

    t evolves as 1.0

    every 10 ms {
        ticks becomes ticks + 1.0
    }
}
"""


def parse_raw(code: str):
    """Parse without flow lowering, to inspect FlowDecl AST shapes."""
    return Parser(Lexer(code), source=code).parse(expand_flows=False)


def parse_lowered(code: str):
    """Parse with the default flow lowering applied."""
    return Parser(Lexer(code), source=code).parse()


def flow_of(decls) -> FlowDecl:
    return next(d for d in decls if isinstance(d, FlowDecl))


def every_flow(period: str) -> FlowDecl:
    code = f"""
flow F {{
    state x : f64 = 0.0
    every {period} {{
        x becomes x + 1.0
    }}
}}
"""
    return flow_of(parse_raw(code))


class TestDurationLiterals:
    """Spec 4.1: NUMBER + suffix canonicalizes to i64 nanoseconds at
    parse time; fractional values must land on whole nanoseconds."""

    @pytest.mark.parametrize("period,expected_ns", [
        ("5 ns", 5),
        ("5 us", 5_000),
        ("5 ms", 5_000_000),
        ("5 s", 5_000_000_000),
        ("5 min", 300_000_000_000),
    ])
    def test_every_suffix(self, period, expected_ns):
        flow = every_flow(period)
        assert flow.everys[0].period_ns == expected_ns
        assert flow.everys[0].period_text == period

    def test_suffix_table_is_the_spec_set(self):
        assert set(DURATION_UNIT_NS) == {"ns", "us", "ms", "s", "min"}

    def test_no_space_form(self):
        # `10ms` lexes as NUMBER(10) IDENT(ms); the parser composes them.
        assert every_flow("10ms").everys[0].period_ns == 10_000_000

    def test_fractional_exact(self):
        assert every_flow("0.5 ms").everys[0].period_ns == 500_000
        assert every_flow("2.5 s").everys[0].period_ns == 2_500_000_000

    def test_exponent_form(self):
        assert every_flow("1e3 us").everys[0].period_ns == 1_000_000

    def test_fractional_nanoseconds_rejected(self):
        with pytest.raises(FlowSyntaxError) as excinfo:
            every_flow("0.5 ns")
        assert "whole number of nanoseconds" in str(excinfo.value)

    def test_i64_overflow_rejected(self):
        # 2^63 ns is one past the i64 range.
        with pytest.raises(FlowSyntaxError) as excinfo:
            every_flow("9223372036854775808 ns")
        assert "i64" in str(excinfo.value)

    def test_max_i64_accepted(self):
        assert (every_flow("9223372036854775807 ns").everys[0].period_ns
                == 2**63 - 1)

    def test_missing_suffix_rejected(self):
        with pytest.raises(FlowSyntaxError) as excinfo:
            every_flow("10")
        assert "time unit" in str(excinfo.value)

    def test_unknown_suffix_rejected(self):
        with pytest.raises(FlowSyntaxError) as excinfo:
            every_flow("10 kg")
        assert "time unit" in str(excinfo.value)
        assert "kg" in str(excinfo.value)


class TestContextualSuffixes:
    """Suffix words and block words stay ordinary identifiers everywhere
    a duration is not grammatically expected (spec 0.2, 4.1)."""

    def test_suffixes_as_variables(self):
        code = """
function main() -> i32 {
    let ns: i32 = 1
    let us: i32 = 2
    let ms: i32 = 3
    let s: i32 = 4
    let min: i32 = 5
    let every: i32 = 6
    let solver: i32 = 7
    return ns + us + ms + s + min + every + solver - 28
}
"""
        decls = parse_lowered(code)
        assert not any(isinstance(d, FlowDecl) for d in decls)
        result = TypeChecker().check(decls)
        assert result.errors == []

    def test_suffixes_as_function_names(self):
        code = """
function ms(min: i32, s: i32) -> i32 {
    return min * 60 + s
}

function main() -> i32 {
    return ms(0, 0)
}
"""
        decls = parse_lowered(code)
        assert {d.name for d in decls if isinstance(d, FunctionDecl)} == {
            "ms",
            "main",
        }

    def test_every_and_solver_as_flow_members(self):
        # `every` before a number opens a block; `every` anywhere else is
        # an identifier, so a state may carry the name. Same for `solver`
        # before '{'.
        code = """
flow F {
    state every : f64 = 0.0
    state solver : f64 = 1.0
    every evolves as solver
}
"""
        flow = flow_of(parse_raw(code))
        assert [st.name for st in flow.states] == ["every", "solver"]
        assert [ev.target for ev in flow.evolves] == ["every"]
        assert flow.everys == []
        assert flow.solver is None

    def test_every_outside_flow_body_is_rejected(self):
        code = """
function main() -> i32 {
    every 10 ms {
        return 1
    }
    return 0
}
"""
        with pytest.raises(SyntaxError):
            parse_lowered(code)


class TestParseShapes:
    def test_every_decl_ast(self):
        flow = flow_of(parse_raw(COUNTER))
        assert len(flow.everys) == 1
        every = flow.everys[0]
        assert every.period_ns == 10_000_000
        assert every.period_text == "10 ms"
        assert [b.target for b in every.body] == ["ticks"]
        assert isinstance(every.body[0].expr, BinaryOperation)

    def test_multiple_every_blocks_keep_declaration_order(self):
        code = """
flow F {
    state a : f64 = 0.0
    state b : f64 = 0.0
    every 20 ms {
        a becomes a + 1.0
    }
    every 5 ms {
        b becomes b + 1.0
    }
}
"""
        flow = flow_of(parse_raw(code))
        assert [e.period_ns for e in flow.everys] == [20_000_000, 5_000_000]

    def test_solver_decl_ast(self):
        flow = flow_of(parse_raw(COUNTER))
        assert flow.solver is not None
        assert flow.solver.dt_ns == 1_000_000
        assert flow.solver.dt_text == "1 ms"
        assert flow.solver.method == "euler"

    def test_solver_method_defaults_to_euler(self):
        code = """
flow F {
    state x : f64 = 0.0
    solver { dt 500 us }
    x evolves as 1.0
}
"""
        flow = flow_of(parse_raw(code))
        assert flow.solver.dt_ns == 500_000
        assert flow.solver.method == "euler"

    def test_solver_settings_in_either_order(self):
        code = """
flow F {
    state x : f64 = 0.0
    solver { method euler  dt 2 ms }
    x evolves as 1.0
}
"""
        flow = flow_of(parse_raw(code))
        assert flow.solver.dt_ns == 2_000_000
        assert flow.solver.method == "euler"

    def test_every_coexists_with_when(self):
        code = """
flow F {
    state x : f64 = 0.0
    state n : f64 = 0.0
    x evolves as 1.0
    every 10 ms {
        n becomes n + 1.0
    }
    when x reaches 1.0 {
        x becomes 0.0
    }
}
"""
        flow = flow_of(parse_raw(code))
        assert len(flow.everys) == 1
        assert len(flow.whens) == 1


class TestValidation:
    def check_error(self, code: str, fragment: str):
        with pytest.raises(FlowSyntaxError) as excinfo:
            parse_lowered(code)
        assert fragment in str(excinfo.value)
        assert excinfo.value.line, "validation error must carry a line"

    def test_zero_period_rejected(self):
        self.check_error(
            """
flow F {
    state x : f64 = 0.0
    every 0 ms {
        x becomes x + 1.0
    }
}
""",
            "period must be positive",
        )

    def test_becomes_target_must_be_a_state(self):
        self.check_error(
            """
flow F {
    state x : f64 = 0.0
    param k : f64 = 2.0
    every 10 ms {
        k becomes 3.0
    }
}
""",
            "requires 'k' to be a declared state",
        )

    def test_continuous_state_may_not_be_discrete(self):
        self.check_error(
            """
flow F {
    state x : f64 = 0.0
    x evolves as 1.0
    every 10 ms {
        x becomes 0.0
    }
}
""",
            "continuous or discrete",
        )

    def test_duplicate_becomes_in_one_every_rejected(self):
        self.check_error(
            """
flow F {
    state x : f64 = 0.0
    every 10 ms {
        x becomes 0.0
        x becomes 1.0
    }
}
""",
            "two 'becomes' updates",
        )

    def test_impure_every_body_rejected(self):
        self.check_error(
            """
extern { function printf(fmt: string, val: f64) -> i32 }
flow F {
    state x : f64 = 0.0
    every 10 ms {
        x becomes printf("%f", x) * 1.0
    }
}
""",
            "cannot be proven pure",
        )

    def test_non_becomes_statement_in_every_body_rejected(self):
        self.check_error(
            """
flow F {
    state x : f64 = 0.0
    every 10 ms {
        let y : f64 = 2.0
    }
}
""",
            "Unexpected statement in 'every' body",
        )

    def test_solver_without_dt_rejected(self):
        self.check_error(
            """
flow F {
    state x : f64 = 0.0
    solver { method euler }
    x evolves as 1.0
}
""",
            "needs a 'dt' setting",
        )

    def test_solver_rk4_accepted(self):
        code = """
flow F {
    state x : f64 = 0.0
    solver { dt 1 ms  method rk4 }
    x evolves as 1.0
}
"""
        flow = flow_of(parse_raw(code))
        assert flow.solver is not None
        assert flow.solver.method == "rk4"
        result = TypeChecker().check(parse_lowered(code))
        assert result.errors == []

    def test_solver_unknown_method_rejected(self):
        self.check_error(
            """
flow F {
    state x : f64 = 0.0
    solver { dt 1 ms  method leapfrog }
    x evolves as 1.0
}
""",
            "unknown solver method 'leapfrog'",
        )

    def test_two_solver_blocks_rejected(self):
        self.check_error(
            """
flow F {
    state x : f64 = 0.0
    solver { dt 1 ms }
    solver { dt 2 ms }
    x evolves as 1.0
}
""",
            "two 'solver' blocks",
        )

    def test_solver_dt_twice_rejected(self):
        self.check_error(
            """
flow F {
    state x : f64 = 0.0
    solver { dt 1 ms  dt 2 ms }
    x evolves as 1.0
}
""",
            "sets 'dt' twice",
        )
