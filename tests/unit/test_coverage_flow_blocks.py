"""Coverage tests for flow blocks and evolves (flow-test-coverage).

Extends tests/unit/test_evolves_syntax.py with cases it does not touch:
several flow blocks in one file, a flow with no states (rejected),
evolves expressions that reference params and inputs together, and an
end-to-end check that two instances of the same flow step independently.
"""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from flow.c_generator import flow_to_c
from flow.parser import (
    FlowSyntaxError,
    FunctionDecl,
    Lexer,
    Parser,
    StructDecl,
)
from flow.type_checker import TypeChecker


TWO_FLOWS = """
flow Decay {
    state x : f64 = 1.0
    param k : f64 = 0.5
    x evolves as -k * x
}

flow Ramp {
    state y : f64 = 0.0
    input drive : f64
    param gain : f64 = 2.0
    y evolves as gain * drive - y
}
"""


def parse_lowered(code: str):
    return Parser(Lexer(code), source=code).parse()


class TestMultipleFlowsInOneFile:
    def test_both_flows_lower_to_structs(self):
        decls = parse_lowered(TWO_FLOWS)
        structs = [d for d in decls if isinstance(d, StructDecl)]
        assert [s.name for s in structs] == ["Decay", "Ramp"]

    def test_both_flows_get_full_api(self):
        decls = parse_lowered(TWO_FLOWS)
        names = {d.name for d in decls if isinstance(d, FunctionDecl)}
        for flow_name in ("Decay", "Ramp"):
            for suffix in ("_new", "_init", "_derivs", "_step"):
                assert flow_name + suffix in names

    def test_lowered_two_flow_file_is_strict_clean(self):
        result = TypeChecker().check(parse_lowered(TWO_FLOWS))
        assert result.errors == []

    def test_generated_c_keeps_apis_separate(self):
        c = flow_to_c(parse_lowered(TWO_FLOWS))
        assert "void Decay_step(Decay* self, double dt)" in c
        assert "void Ramp_step(Ramp* self, double dt)" in c
        # Each derivs signature mentions only its own states.
        assert "void Decay_derivs(Decay* self, double* d_x)" in c
        assert "void Ramp_derivs(Ramp* self, double* d_y)" in c


class TestStatelessFlowRejected:
    def test_flow_with_only_params_and_outputs_is_rejected(self):
        code = """
flow K {
    param gain : f64 = 2.0
    output doubled : f64 = gain * 2.0
}
"""
        with pytest.raises(FlowSyntaxError) as excinfo:
            parse_lowered(code)
        assert "declares no state" in str(excinfo.value)
        # The error points at the fix.
        assert "state name : f64 = value" in str(excinfo.value)


class TestEvolvesReferencingParamsAndInputs:
    MOTOR = """
flow Motor {
    state speed : f64 = 0.0
    input voltage : f64
    param damping : f64 = 0.25
    param gain : f64 = 2.0
    speed evolves as gain * voltage - damping * speed
}
"""

    def test_lowering_is_strict_clean(self):
        result = TypeChecker().check(parse_lowered(self.MOTOR))
        assert result.errors == []

    def test_derivs_reads_inputs_and_params_via_self(self):
        c = flow_to_c(parse_lowered(self.MOTOR))
        derivs = c.split(
            "void Motor_derivs(Motor* self, double* d_speed) {", 1
        )[1].split("\n}", 1)[0]
        assert "self->gain" in derivs
        assert "self->voltage" in derivs
        assert "self->damping" in derivs
        assert "self->speed" in derivs
        # derivs never writes state.
        assert "self->speed =" not in derivs
        assert "self->voltage =" not in derivs


class TestRk4SolverMethod:
    RK4 = """
flow Spring {
    state x : f64 = 1.0
    state v : f64 = 0.0
    solver { dt 1 ms  method rk4 }
    x evolves as v
    v evolves as 0.0 - x
}
"""

    def test_rk4_lowering_is_strict_clean(self):
        result = TypeChecker().check(parse_lowered(self.RK4))
        assert result.errors == []

    def test_rk4_step_emits_four_derivs_stages(self):
        c = flow_to_c(parse_lowered(self.RK4))
        step = c.split("void Spring_step(Spring* self, double dt) {", 1)[1]
        step = step.split("\n}", 1)[0]
        assert step.count("Spring_derivs(self,") == 4
        assert "y0_x" in step and "k4_v" in step


class TestIndependentInstances:
    @pytest.mark.skipif(shutil.which("clang") is None, reason="clang not found")
    def test_two_instances_of_one_flow_step_independently(self, tmp_path):
        # Constant derivative makes Euler exact: after n steps of dt,
        # x = x0 + n * dt * rate, with every quantity a power of two so
        # the doubles are exact. The two instances use different params
        # and step counts; neither may disturb the other.
        program = """
flow Linear {
    state x : f64 = 0.0
    param rate : f64 = 1.0
    x evolves as rate
}

extern {
    function printf(fmt: string, val: f64) -> i32
}

function main() -> i32 {
    let mut a: Linear = Linear_new()
    let mut b: Linear = Linear_new()
    b.rate = 4.0

    for k in 0 to 8 {
        Linear_step(&a, 0.25)
    }
    for k in 0 to 4 {
        Linear_step(&b, 0.25)
    }

    printf("%.6f\\n", a.x)
    printf("%.6f\\n", b.x)
    return 0
}
"""
        src = tmp_path / "instances.flow"
        src.write_text(program)
        c_file = tmp_path / "instances.c"
        exe = tmp_path / "instances"
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
        run = subprocess.run([str(exe)], capture_output=True, text=True,
                             timeout=60)
        assert run.returncode == 0
        a_x, b_x = (float(line) for line in run.stdout.split())
        assert a_x == 2.0  # 8 steps * 0.25 * rate 1.0
        assert b_x == 4.0  # 4 steps * 0.25 * rate 4.0
