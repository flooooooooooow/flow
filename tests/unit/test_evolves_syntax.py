"""Tests for `flow Name { ... }` blocks and `x evolves as expr` dynamics.

Card: evolves-syntax (docs/vision/north-star.md sections 1 and 2).
Covers: parse shapes, contextual-keyword non-regression, lowering and
validation, strict type checking of lowered output, generated-C structure,
and an end-to-end compile-and-run trajectory check against a Python
reference Euler integration.
"""

import math
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

from flow.c_generator import flow_to_c
from flow.flow_blocks import expand_flow_decls
from flow.parser import (
    BinaryOperation,
    FlowDecl,
    FlowSyntaxError,
    FunctionDecl,
    Lexer,
    Parser,
    StructDecl,
    Variable,
)
from flow.type_checker import TypeChecker


PENDULUM = """
extern {
    function sin(x: f64) -> f64
}

flow Pendulum {
    state angle    : f64 = 2.0
    state velocity : f64 = 0.0
    param gravity  : f64 = 9.81
    param length   : f64 = 1.0
    param damping  : f64 = 0.5

    angle evolves as velocity
    velocity evolves as -(gravity / length) * sin(angle) - damping * velocity
}
"""


def parse_raw(code: str):
    """Parse without flow lowering, to inspect FlowDecl AST shapes."""
    return Parser(Lexer(code), source=code).parse(expand_flows=False)


def parse_lowered(code: str):
    """Parse with the default flow lowering applied."""
    return Parser(Lexer(code), source=code).parse()


class TestParseShapes:
    def test_flow_decl_ast(self):
        decls = parse_raw(PENDULUM)
        flows = [d for d in decls if isinstance(d, FlowDecl)]
        assert len(flows) == 1
        flow = flows[0]
        assert flow.name == "Pendulum"
        assert [s.name for s in flow.states] == ["angle", "velocity"]
        assert [p.name for p in flow.params] == ["gravity", "length", "damping"]
        assert flow.inputs == []
        assert flow.outputs == []
        assert all(s.type.name == "f64" for s in flow.states)
        assert flow.states[0].initializer is not None

    def test_evolves_ast(self):
        decls = parse_raw(PENDULUM)
        flow = next(d for d in decls if isinstance(d, FlowDecl))
        assert [ev.target for ev in flow.evolves] == ["angle", "velocity"]
        # `angle evolves as velocity` has a bare variable RHS.
        assert isinstance(flow.evolves[0].expr, Variable)
        assert flow.evolves[0].expr.name == "velocity"
        # The second RHS is a real expression tree.
        assert isinstance(flow.evolves[1].expr, BinaryOperation)

    def test_input_output_sections(self):
        code = """
flow Motor {
    state speed : f64 = 0.0
    input voltage : f64
    output torque : f64 = 0.6 * speed
    param damping : f64 = 0.1

    speed evolves as voltage - damping * speed
}
"""
        flow = next(d for d in parse_raw(code) if isinstance(d, FlowDecl))
        assert [i.name for i in flow.inputs] == ["voltage"]
        assert [o.name for o in flow.outputs] == ["torque"]
        assert flow.outputs[0].expr is not None

    def test_multiline_evolves_rhs(self):
        code = """
extern { function sin(x: f64) -> f64 }
flow F {
    state x : f64 = 0.0
    state v : f64 = 0.0
    x evolves as v
    v evolves as
        -(9.81 / 1.0) * sin(x)
            - 0.5 * v
}
"""
        flow = next(d for d in parse_raw(code) if isinstance(d, FlowDecl))
        assert len(flow.evolves) == 2


class TestContextualKeywords:
    """Programs using the new words as ordinary identifiers must not regress."""

    def test_identifiers_still_work(self):
        code = """
function flow(state: i32, evolves: i32) -> i32 {
    let param: i32 = state + evolves
    return param
}

function main() -> i32 {
    let flow: i32 = 1
    let state: i32 = 2
    let evolves: i32 = 3
    let output: i32 = flow + state + evolves
    return output
}
"""
        decls = parse_lowered(code)
        assert not any(isinstance(d, FlowDecl) for d in decls)
        assert {d.name for d in decls if isinstance(d, FunctionDecl)} == {
            "flow",
            "main",
        }

    def test_flow_call_is_not_a_flow_decl(self):
        # `flow(...)` and `flow.x` in expressions stay ordinary code.
        code = """
function flow(x: i32) -> i32 { return x }
function main() -> i32 {
    let y: i32 = flow(4)
    return y
}
"""
        decls = parse_lowered(code)
        assert not any(isinstance(d, FlowDecl) for d in decls)

    def test_strict_check_unchanged_program(self):
        code = """
function main() -> i32 {
    let state: f64 = 1.0
    let evolves: f64 = state * 2.0
    if evolves > 1.0 {
        return 0
    }
    return 1
}
"""
        result = TypeChecker().check(parse_lowered(code))
        assert result.errors == []


class TestLowering:
    def test_flow_lowers_to_struct_and_functions(self):
        decls = parse_lowered(PENDULUM)
        structs = [d for d in decls if isinstance(d, StructDecl)]
        assert [s.name for s in structs] == ["Pendulum"]
        # Field order: state, input, output, param (spec 1.2).
        assert [f.name for f in structs[0].fields] == [
            "angle", "velocity", "gravity", "length", "damping",
        ]
        names = {d.name for d in decls if isinstance(d, FunctionDecl)}
        for expected in (
            "Pendulum_new", "Pendulum_init", "Pendulum_derivs", "Pendulum_step",
        ):
            assert expected in names
        # No outputs declared, so no outputs function.
        assert "Pendulum_outputs" not in names

    def test_generated_functions_carry_flow_api_attribute(self):
        decls = parse_lowered(PENDULUM)
        for d in decls:
            if isinstance(d, FunctionDecl) and d.name.startswith("Pendulum_"):
                assert "flow_api" in d.attributes

    def test_struct_keeps_dynamics_metadata(self):
        decls = parse_lowered(PENDULUM)
        struct = next(d for d in decls if isinstance(d, StructDecl))
        assert isinstance(struct.flow_decl, FlowDecl)
        assert [ev.target for ev in struct.flow_decl.evolves] == [
            "angle", "velocity",
        ]

    def test_lowered_output_is_strict_clean(self):
        decls = parse_lowered(PENDULUM)
        result = TypeChecker().check(decls)
        assert result.errors == []

    def test_derivs_order_follows_state_declaration_order(self):
        # Evolves written in reverse order; signature must follow state order.
        code = """
flow F {
    state a : f64 = 0.0
    state b : f64 = 1.0
    b evolves as a
    a evolves as b
}
"""
        decls = parse_lowered(code)
        derivs = next(
            d for d in decls
            if isinstance(d, FunctionDecl) and d.name == "F_derivs"
        )
        assert [p.name for p in derivs.parameters] == ["self", "d_a", "d_b"]


class TestValidation:
    def check_error(self, code: str, fragment: str):
        with pytest.raises(FlowSyntaxError) as excinfo:
            parse_lowered(code)
        assert fragment in str(excinfo.value)

    def test_evolves_target_must_be_state(self):
        self.check_error(
            """
flow F {
    state x : f64 = 0.0
    y evolves as x
}
""",
            "requires 'y' to be a declared state",
        )

    def test_duplicate_evolves_rejected(self):
        self.check_error(
            """
flow F {
    state x : f64 = 0.0
    x evolves as x
    x evolves as x * 2.0
}
""",
            "two 'evolves' declarations",
        )

    def test_state_needs_initializer(self):
        self.check_error(
            """
flow F {
    state x : f64
    x evolves as x
}
""",
            "needs an initial value",
        )

    def test_member_type_must_be_float(self):
        self.check_error(
            """
flow F {
    state x : i32 = 0
    x evolves as x
}
""",
            "must be f64 or f32",
        )

    def test_output_needs_inline_map(self):
        self.check_error(
            """
flow F {
    state x : f64 = 0.0
    output y : f64
    x evolves as x
}
""",
            "needs an inline map",
        )

    def test_impure_call_rejected(self):
        self.check_error(
            """
extern { function printf(fmt: string, val: f64) -> i32 }
flow F {
    state x : f64 = 0.0
    x evolves as printf("%f", x) * 1.0
}
""",
            "cannot be proven pure",
        )

    def test_duplicate_member_rejected(self):
        self.check_error(
            """
flow F {
    state x : f64 = 0.0
    param x : f64 = 1.0
    x evolves as x
}
""",
            "declares 'x' twice",
        )


class TestCodegenStructure:
    def generate(self, code: str = PENDULUM) -> str:
        return flow_to_c(parse_lowered(code))

    def test_unmangled_c_api(self):
        c_code = self.generate()
        assert "Pendulum Pendulum_new(void)" in c_code
        assert "void Pendulum_init(Pendulum* self)" in c_code
        assert (
            "void Pendulum_derivs(Pendulum* self, double* d_angle, "
            "double* d_velocity)" in c_code
        )
        assert "void Pendulum_step(Pendulum* self, double dt)" in c_code
        # No mangled variants of the flow API.
        assert "Pendulum_step_ptr_Pendulum" not in c_code
        assert "Pendulum_derivs_ptr_Pendulum" not in c_code

    def test_struct_fields(self):
        c_code = self.generate()
        struct_body = c_code.split("struct Pendulum {", 1)[1].split("};", 1)[0]
        for field in ("angle", "velocity", "gravity", "length", "damping"):
            assert f"double {field};" in struct_body

    def test_step_calls_derivs_before_integrating(self):
        c_code = self.generate()
        step_body = c_code.split(
            "void Pendulum_step(Pendulum* self, double dt) {", 1
        )[1]
        step_body = step_body.split("\n}", 1)[0]
        derivs_at = step_body.index("Pendulum_derivs(self")
        angle_write = step_body.index("self->angle =")
        velocity_write = step_body.index("self->velocity =")
        assert derivs_at < angle_write
        assert derivs_at < velocity_write
        # Euler update reads the derivative locals, scaled by dt.
        assert "self->angle + (d_angle * dt)" in step_body
        assert "self->velocity + (d_velocity * dt)" in step_body

    def test_derivs_reads_pre_step_state_only(self):
        c_code = self.generate()
        derivs_body = c_code.split(
            "void Pendulum_derivs(Pendulum* self, double* d_angle, "
            "double* d_velocity) {", 1
        )[1].split("\n}", 1)[0]
        assert "d_angle[0] = self->velocity;" in derivs_body
        # No writes to self inside derivs.
        assert "self->angle =" not in derivs_body
        assert "self->velocity =" not in derivs_body

    def test_outputs_generated_and_called_after_integration(self):
        code = """
flow Motor {
    state speed : f64 = 0.0
    input voltage : f64
    output torque : f64 = 0.6 * speed
    param damping : f64 = 0.1

    speed evolves as voltage - damping * speed
}
"""
        c_code = flow_to_c(parse_lowered(code))
        assert "void Motor_outputs(Motor* self)" in c_code
        step_body = c_code.split("void Motor_step(Motor* self, double dt)", 1)[1]
        step_body = step_body.split("Motor_outputs(self);", 1)
        assert len(step_body) == 2  # outputs called inside step
        assert "self->speed =" in step_body[0]  # integration first


class TestEndToEnd:
    @pytest.mark.skipif(shutil.which("clang") is None, reason="clang not found")
    def test_compile_and_run_matches_reference_euler(self, tmp_path):
        program = PENDULUM + """
extern {
    function printf(fmt: string, val: f64) -> i32
}

function main() -> i32 {
    let mut p: Pendulum = Pendulum_new()
    for k in 0 to 2400 {
        Pendulum_step(&p, 0.01)
    }
    printf("%.15f\\n", p.angle)
    printf("%.15f\\n", p.velocity)
    return 0
}
"""
        src = tmp_path / "pendulum_e2e.flow"
        src.write_text(program)
        c_file = tmp_path / "pendulum_e2e.c"
        exe = tmp_path / "pendulum_e2e"
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
        run = subprocess.run(
            [str(exe)], capture_output=True, text=True, timeout=60
        )
        assert run.returncode == 0
        angle, velocity = (float(line) for line in run.stdout.split())

        # Reference: same Euler integration in Python.
        ref_angle, ref_velocity = 2.0, 0.0
        for _ in range(2400):
            d_angle = ref_velocity
            d_velocity = -(9.81 / 1.0) * math.sin(ref_angle) - 0.5 * ref_velocity
            ref_angle += d_angle * 0.01
            ref_velocity += d_velocity * 0.01

        assert abs(angle - ref_angle) < 1e-9
        assert abs(velocity - ref_velocity) < 1e-9
        # Damped pendulum settles near the stable equilibrium.
        assert abs(angle) < 0.05
        assert abs(velocity) < 0.05
