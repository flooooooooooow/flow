"""Coverage tests for hybrid events (flow-test-coverage).

Extends tests/unit/test_hybrid_events.py with cases it does not touch:
several when-blocks firing in declaration order within one step, an
event whose reset targets a different state than the guard, and guard
behavior near the threshold with tiny dt (fire exactly once on an exact
hit, never fire on an asymptotic approach).
"""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from flow.c_generator import flow_to_c
from flow.parser import Lexer, Parser


def parse_lowered(code: str):
    return Parser(Lexer(code), source=code).parse()


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


TWO_WHENS = """
flow F {
    state t : f64 = 0.0
    state a : f64 = 1.0
    state b : f64 = 0.0
    t evolves as 1.0
    when t reaches 1.0 {
        a becomes a * 2.0
    }
    when t reaches 1.0 {
        b becomes a
    }
}
"""


class TestMultipleWhenBlockOrdering:
    def test_each_when_gets_its_own_guard_memory(self):
        c = flow_to_c(parse_lowered(TWO_WHENS + "function main() -> i32 { return 0 }"))
        struct_body = c.split("struct F {", 1)[1].split("};", 1)[0]
        assert "double __guard_0_prev;" in struct_body
        assert "double __guard_1_prev;" in struct_body

    def test_guards_are_checked_in_declaration_order(self):
        c = flow_to_c(parse_lowered(TWO_WHENS + "function main() -> i32 { return 0 }"))
        step = c.split("void F_step(F* self, double dt) {", 1)[1].split("\n}", 1)[0]
        first = step.index("double __g_0 =")
        second = step.index("double __g_1 =")
        assert first < second
        # The first event's reset is fully applied before the second
        # event's reset is staged, so event 1 observes event 0's writes.
        write_a = step.index("self->a = __reset_0_a;")
        stage_b = step.index("double __reset_1_b = self->a;")
        assert write_a < stage_b

    @pytest.mark.skipif(shutil.which("clang") is None, reason="clang not found")
    def test_second_event_observes_first_events_reset(self, tmp_path):
        # Both events fire in the same step (t hits 1.0 exactly with
        # dt = 0.25). Event 0 doubles a to 2.0; event 1 copies a into b.
        # Declaration-order firing means b must see the doubled value.
        program = TWO_WHENS + """
extern { function printf(fmt: string, val: f64) -> i32 }

function main() -> i32 {
    let mut f: F = F_new()
    for k in 0 to 4 {
        F_step(&f, 0.25)
    }
    printf("%.1f\\n", f.a)
    printf("%.1f\\n", f.b)
    return 0
}
"""
        out = run_flow_program(program, tmp_path, "two_whens_e2e")
        a, b = (float(line) for line in out.split())
        assert a == 2.0
        assert b == 2.0


class TestCrossStateReset:
    COUNTER = """
flow Counter {
    state t : f64 = 0.0
    state hits : f64 = 0.0
    t evolves as 1.0
    when t reaches 1.0 {
        hits becomes hits + 1.0
    }
}
"""

    def test_guard_state_differs_from_reset_target(self):
        c = flow_to_c(parse_lowered(self.COUNTER + "function main() -> i32 { return 0 }"))
        step = c.split("void Counter_step(Counter* self, double dt) {", 1)[1]
        step = step.split("\n}", 1)[0]
        # Guard watches t; the reset writes hits and never writes t.
        assert "double __g_0 = (self->t - 1.0);" in step
        assert "self->hits = __reset_0_hits;" in step
        reset_block = step.split("if ((__g_0", 1)[1].split("}", 1)[0]
        assert "self->t =" not in reset_block

    @pytest.mark.skipif(shutil.which("clang") is None, reason="clang not found")
    def test_event_fires_once_when_guard_state_keeps_growing(self, tmp_path):
        # t grows monotonically through 1.0 and is never reset, so the
        # sign-change guard must fire exactly once over the whole run.
        program = self.COUNTER + """
extern { function printf(fmt: string, val: f64) -> i32 }

function main() -> i32 {
    let mut c: Counter = Counter_new()
    for k in 0 to 32 {
        Counter_step(&c, 0.125)
    }
    printf("%.1f\\n", c.hits)
    printf("%.3f\\n", c.t)
    return 0
}
"""
        out = run_flow_program(program, tmp_path, "counter_e2e")
        hits, t = (float(line) for line in out.split())
        assert hits == 1.0
        assert t == 4.0


class TestGuardNearThresholdTinyDt:
    @pytest.mark.skipif(shutil.which("clang") is None, reason="clang not found")
    def test_exact_hit_with_tiny_dt_fires_exactly_once(self, tmp_path):
        # dt = 2^-10 and threshold 0.25 make the hit exact in binary:
        # after 256 steps t == 0.25 with no rounding, triggering the
        # `__g == 0.0` arm of the guard. The remaining steps move away
        # from the threshold and must not re-fire.
        program = """
flow Tiny {
    state t : f64 = 0.0
    state hits : f64 = 0.0
    t evolves as 1.0
    when t reaches 0.25 {
        hits becomes hits + 1.0
    }
}

extern { function printf(fmt: string, val: f64) -> i32 }

function main() -> i32 {
    let mut f: Tiny = Tiny_new()
    for k in 0 to 512 {
        Tiny_step(&f, 0.0009765625)
    }
    printf("%.1f\\n", f.hits)
    return 0
}
"""
        out = run_flow_program(program, tmp_path, "tiny_exact_e2e")
        assert float(out.strip()) == 1.0

    @pytest.mark.skipif(shutil.which("clang") is None, reason="clang not found")
    def test_crossing_between_steps_fires_exactly_once(self, tmp_path):
        # Threshold 0.3 is not representable, so t never equals it; the
        # event must fire on the sign change between two tiny steps, and
        # only once.
        program = """
flow Cross {
    state t : f64 = 0.0
    state hits : f64 = 0.0
    t evolves as 1.0
    when t reaches 0.3 {
        hits becomes hits + 1.0
    }
}

extern { function printf(fmt: string, val: f64) -> i32 }

function main() -> i32 {
    let mut f: Cross = Cross_new()
    for k in 0 to 1024 {
        Cross_step(&f, 0.0009765625)
    }
    printf("%.1f\\n", f.hits)
    return 0
}
"""
        out = run_flow_program(program, tmp_path, "tiny_cross_e2e")
        assert float(out.strip()) == 1.0

    @pytest.mark.skipif(shutil.which("clang") is None, reason="clang not found")
    def test_asymptotic_approach_never_fires(self, tmp_path):
        # x evolves as (1 - x) from 0: Euler with dt < 1 approaches 1.0
        # from below and never reaches it, so the guard at 1.0 must
        # never fire no matter how close x gets.
        program = """
flow Approach {
    state x : f64 = 0.0
    state hits : f64 = 0.0
    x evolves as 1.0 - x
    when x reaches 1.0 {
        hits becomes hits + 1.0
    }
}

extern { function printf(fmt: string, val: f64) -> i32 }

function main() -> i32 {
    let mut f: Approach = Approach_new()
    for k in 0 to 4096 {
        Approach_step(&f, 0.03125)
    }
    printf("%.1f\\n", f.hits)
    printf("%.9f\\n", f.x)
    return 0
}
"""
        out = run_flow_program(program, tmp_path, "approach_e2e")
        hits, x = (float(line) for line in out.split())
        assert hits == 0.0
        assert 0.999 < x <= 1.0
