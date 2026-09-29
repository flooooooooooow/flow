"""Tests for `flow Name { ... }` blocks and `x evolves as expr` dynamics.

Card: evolves-syntax (docs/vision/north-star.md sections 1 and 2).
Covers: parse shapes, contextual-keyword non-regression, lowering and
validation, and strict type checking of lowered output. The generated C
and the end-to-end trajectory are tests/cgen/evolves_*.
"""

import pytest

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

    def test_state_without_an_initializer_starts_at_zero(self):
        """Requiring `= 0.0` on every member made the common case noisier
        than the model it describes, and `angle : Angle` has nowhere to put
        one."""
        decls = parse_lowered(
            """
flow F {
    state x : f64
    x evolves as x
}
"""
        )
        assert decls, "flow with an uninitialized state should still lower"

    def test_member_type_must_be_a_float_or_a_unit(self):
        self.check_error(
            """
flow F {
    state x : i32 = 0
    x evolves as x
}
""",
            "a flow member is f64, f32, or a declared unit",
        )

    def test_a_declared_unit_is_a_valid_member_type(self):
        decls = parse_lowered(
            """
unit Angle

flow F {
    state x : Angle
    x evolves as 1.0
}
"""
        )
        assert decls

    def test_a_bare_member_of_unit_type_is_state_not_a_nested_flow(self):
        """`angle : Angle` used to be read as composition and rejected
        because Angle is not a flow."""
        decls = parse_lowered(
            """
unit Angle

flow F {
    angle : Angle
    angle evolves as 1.0
}
"""
        )
        assert decls

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


# The generated-C structure and the end-to-end Euler trajectory checks are
# tests/cgen/evolves_pendulum and tests/cgen/evolves_outputs.
