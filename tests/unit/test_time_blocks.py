"""Tests for explicit time in flow blocks: duration literals,
`every <duration> { ... }`, and the `solver` block.

Card: time-blocks (docs/vision/north-star.md sections 2.3 and 4).
Covers: duration literal parsing (every suffix, i64 nanosecond values),
contextual-keyword non-regression (suffix words stay identifiers),
every-block and solver-block parse shapes, validation with located
messages, generated-C structure (accumulator fields, firing condition,
ordering relative to integration, events, and outputs), and end-to-end
compile-and-run checks.
"""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from flow.c_generator import flow_to_c
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


def run_flow_program(program: str, tmp_path, name: str) -> str:
    """Transpile --strict, compile with clang, run, return stdout."""
    src = tmp_path / f"{name}.flow"
    src.write_text(program)
    c_file = tmp_path / f"{name}.c"
    exe = tmp_path / name
    repo_root = Path(__file__).resolve().parents[2]

    transpile = subprocess.run(
        [sys.executable, "-m", "flow.transpiler", str(src), "--c",
         "--strict", "-o", str(c_file)],
        capture_output=True, text=True, timeout=120,
        cwd=repo_root, env={"PYTHONPATH": str(repo_root / "src"),
                            "PATH": "/usr/bin:/bin"},
    )
    assert transpile.returncode == 0, transpile.stderr
    compile_run = subprocess.run(
        ["clang", str(c_file), "-o", str(exe), "-lm"],
        capture_output=True, text=True, timeout=120,
    )
    assert compile_run.returncode == 0, compile_run.stderr
    run = subprocess.run([str(exe)], capture_output=True, text=True, timeout=60)
    assert run.returncode == 0, run.stdout + run.stderr
    return run.stdout


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

    def test_solver_rk4_not_yet(self):
        self.check_error(
            """
flow F {
    state x : f64 = 0.0
    solver { dt 1 ms  method rk4 }
    x evolves as 1.0
}
""",
            "not yet implemented",
        )

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


class TestCodegenStructure:
    def generate(self, code: str = COUNTER) -> str:
        return flow_to_c(parse_lowered(code))

    def step_body(self, c_code: str, name: str = "Counter") -> str:
        body = c_code.split(f"void {name}_step({name}* self, double dt) {{", 1)[1]
        return body.split("\n}", 1)[0]

    def test_struct_has_accumulator_field(self):
        c_code = self.generate()
        struct_body = c_code.split("struct Counter {", 1)[1].split("};", 1)[0]
        assert "int64_t __every_0_acc;" in struct_body

    def test_init_zeroes_accumulator(self):
        c_code = self.generate()
        init_body = c_code.split("void Counter_init(Counter* self) {", 1)[1]
        init_body = init_body.split("\n}", 1)[0]
        assert "self->__every_0_acc = 0;" in init_body

    def test_dt_converts_to_ns_once(self):
        step = self.step_body(self.generate())
        assert step.count("int64_t __dt_ns") == 1
        assert "(int64_t)((dt * 1000000000.0))" in step

    def test_firing_condition_and_catchup_cap(self):
        step = self.step_body(self.generate())
        assert "self->__every_0_acc = (self->__every_0_acc + __dt_ns);" in step
        assert ("while ((self->__every_0_acc >= 10000000 "
                "&& __every_0_n < 1024))") in step
        assert "self->__every_0_acc = (self->__every_0_acc - 10000000);" in step

    def test_every_runs_after_integration(self):
        step = self.step_body(self.generate())
        integrate_at = step.index("self->t = (self->t +")
        acc_at = step.index("self->__every_0_acc = (self->__every_0_acc +")
        assert integrate_at < acc_at

    def test_every_runs_before_events(self):
        code = """
flow Mixed {
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
        step = self.step_body(flow_to_c(parse_lowered(code)), "Mixed")
        every_at = step.index("self->__every_0_acc")
        guard_at = step.index("double __g_0")
        assert every_at < guard_at

    def test_every_runs_before_outputs(self):
        code = """
flow Gauge {
    state level : f64 = 0.0
    output display : f64 = level * 100.0
    every 10 ms {
        level becomes level + 1.0
    }
}
"""
        step = self.step_body(flow_to_c(parse_lowered(code)), "Gauge")
        assert step.index("__every_0_acc") < step.index("Gauge_outputs(self);")

    def test_updates_are_staged_then_assigned(self):
        code = """
flow Swap {
    state a : f64 = 1.0
    state b : f64 = 2.0
    every 10 ms {
        a becomes b
        b becomes a
    }
}
"""
        step = self.step_body(flow_to_c(parse_lowered(code)), "Swap")
        stage_a = step.index("double __tick_0_a = self->b;")
        stage_b = step.index("double __tick_0_b = self->a;")
        write_a = step.index("self->a = __tick_0_a;")
        write_b = step.index("self->b = __tick_0_b;")
        assert stage_a < write_a
        assert stage_b < write_a
        assert stage_a < write_b

    def test_default_dt_from_solver_block(self):
        c_code = self.generate()
        assert "double Counter_default_dt(void) {" in c_code
        body = c_code.split("double Counter_default_dt(void) {", 1)[1]
        body = body.split("\n}", 1)[0]
        assert "return 0.001;" in body

    def test_default_dt_fallback_is_one_ms(self):
        code = """
flow Plain {
    state x : f64 = 0.0
    x evolves as 1.0
}
"""
        c_code = flow_to_c(parse_lowered(code))
        body = c_code.split("double Plain_default_dt(void) {", 1)[1]
        body = body.split("\n}", 1)[0]
        assert "return 0.001;" in body

    def test_step_signature_unchanged_by_solver(self):
        # The solver block pins a default; dt stays caller-supplied.
        c_code = self.generate()
        assert "void Counter_step(Counter* self, double dt)" in c_code


class TestEndToEnd:
    @pytest.mark.skipif(shutil.which("clang") is None, reason="clang not found")
    def test_firing_count_and_catchup(self, tmp_path):
        # 1000 steps of 1 ms cover 1 s: an `every 10 ms` block fires 100
        # times (first firing at t >= P, spec 4.3). A single 95 ms step
        # catches up with 9 firings instead of dropping ticks.
        program = COUNTER + """
extern { function printf(fmt: string, val: f64) -> i32 }

function main() -> i32 {
    let mut c: Counter = Counter_new()
    for k in 0 to 1000 {
        Counter_step(&c, 0.001)
    }
    printf("%.1f\\n", c.ticks)

    let mut burst: Counter = Counter_new()
    Counter_step(&burst, 0.095)
    printf("%.1f\\n", burst.ticks)

    printf("%.6f\\n", Counter_default_dt())
    return 0
}
"""
        out = run_flow_program(program, tmp_path, "every_e2e")
        steady, burst, default_dt = out.split()
        assert float(steady) == 100.0
        assert float(burst) == 9.0
        assert float(default_dt) == pytest.approx(0.001)

    @pytest.mark.skipif(shutil.which("clang") is None, reason="clang not found")
    def test_every_updates_are_simultaneous(self, tmp_path):
        # `a becomes b; b becomes a` inside one every-body must swap.
        program = """
extern { function printf(fmt: string, val: f64) -> i32 }

flow Swap {
    state a : f64 = 1.0
    state b : f64 = 2.0
    every 10 ms {
        a becomes b
        b becomes a
    }
}

function main() -> i32 {
    let mut s: Swap = Swap_new()
    Swap_step(&s, 0.01)
    printf("%.1f\\n", s.a)
    printf("%.1f\\n", s.b)
    return 0
}
"""
        out = run_flow_program(program, tmp_path, "swap_every_e2e")
        a, b = (float(line) for line in out.split())
        assert a == 2.0
        assert b == 1.0
