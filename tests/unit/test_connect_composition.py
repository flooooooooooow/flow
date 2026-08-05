"""Tests for Stage-1 `connect { a.out -> b.in }` composition.

Card: connect (docs/vision/north-star.md §8).
Covers: parse shapes, nested flow members, port checks, algebraic-loop
rejection, lowering (topo-ordered child stepping + port copies), and
strict type checking of the lowered AST. End-to-end native runs live in
examples/evolution/robot_connect.flow (sandbox may block subprocess
binaries here).
"""

from flow.c_generator import flow_to_c
from flow.parser import (
    FlowConnection,
    FlowDecl,
    FlowSyntaxError,
    FunctionDecl,
    Lexer,
    Parser,
    StructDecl,
)
from flow.type_checker import TypeChecker


CHAIN = """
flow Ramp {
    state x : f64 = 0.0
    output out : f64 = x
    x evolves as 1.0
}

flow Integrator {
    state y : f64 = 0.0
    input u : f64
    output total : f64 = y
    y evolves as u
}

flow Chain {
    a : Ramp
    b : Integrator

    connect {
        a.out -> b.u
    }
}
"""

ROBOT = """
flow Motor {
    state speed : f64 = 0.0
    input voltage : f64
    output speed_out : f64 = speed
    param damping : f64 = 0.5
    speed evolves as voltage - damping * speed
}

flow Controller {
    state cmd : f64 = 0.0
    input setpoint : f64
    input feedback : f64
    output command : f64 = cmd
    param kp : f64 = 2.0
    every 1 ms {
        cmd becomes kp * (setpoint - feedback)
    }
}

flow Robot {
    plant : Motor
    controller : Controller
    connect {
        controller.command -> plant.voltage
        plant.speed_out -> controller.feedback
    }
}
"""


def parse_raw(code: str):
    return Parser(Lexer(code), source=code).parse(expand_flows=False)


def parse_lowered(code: str):
    return Parser(Lexer(code), source=code).parse()


class TestParseShapes:
    def test_child_and_connect_ast(self):
        flows = {d.name: d for d in parse_raw(CHAIN) if isinstance(d, FlowDecl)}
        chain = flows["Chain"]
        assert [(c.name, c.type.name) for c in chain.children] == [
            ("a", "Ramp"), ("b", "Integrator"),
        ]
        assert len(chain.connections) == 1
        conn = chain.connections[0]
        assert isinstance(conn, FlowConnection)
        assert (conn.src_member, conn.src_port, conn.dst_member, conn.dst_port) == (
            "a", "out", "b", "u",
        )

    def test_connect_stays_contextual(self):
        code = """
function main() -> i32 {
    let connect: i32 = 1
    return connect
}
"""
        decls = parse_lowered(code)
        assert not any(isinstance(d, FlowDecl) for d in decls)


class TestValidation:
    def check_error(self, code: str, fragment: str):
        try:
            parse_lowered(code)
            raise AssertionError(f"expected FlowSyntaxError containing {fragment!r}")
        except FlowSyntaxError as exc:
            assert fragment in str(exc), str(exc)

    def test_unknown_child_type(self):
        self.check_error(
            """
flow Parent {
    plant : Missing
}
""",
            "not a flow in this file",
        )

    def test_source_must_be_output_or_state(self):
        self.check_error(
            """
flow A {
    state x : f64 = 0.0
    input u : f64
    output y : f64 = x
    x evolves as u
}
flow B {
    state z : f64 = 0.0
    input v : f64
    z evolves as v
}
flow C {
    a : A
    b : B
    connect {
        a.u -> b.v
    }
}
""",
            "connection sources must be an output or state",
        )

    def test_dest_must_be_input(self):
        self.check_error(
            """
flow A {
    state x : f64 = 0.0
    output y : f64 = x
    x evolves as 1.0
}
flow B {
    state z : f64 = 0.0
    input v : f64
    z evolves as v
}
flow C {
    a : A
    b : B
    connect {
        a.y -> b.z
    }
}
""",
            "connection destinations must be an input",
        )

    def test_duplicate_incoming_rejected(self):
        self.check_error(
            """
flow A {
    state x : f64 = 0.0
    output y : f64 = x
    x evolves as 1.0
}
flow B {
    state z : f64 = 0.0
    input v : f64
    z evolves as v
}
flow C {
    a1 : A
    a2 : A
    b : B
    connect {
        a1.y -> b.v
        a2.y -> b.v
    }
}
""",
            "two incoming connections",
        )

    def test_algebraic_loop_rejected(self):
        # Combinational output maps through inputs form a cycle.
        self.check_error(
            """
flow A {
    state s : f64 = 0.0
    input u : f64
    output y : f64 = u
    s evolves as 0.0
}
flow B {
    state s : f64 = 0.0
    input u : f64
    output y : f64 = u
    s evolves as 0.0
}
flow Loop {
    a : A
    b : B
    connect {
        a.y -> b.u
        b.y -> a.u
    }
}
""",
            "algebraic loop",
        )

    def test_state_broken_feedback_ok(self):
        # Robot feedback reads a state-mapped output; not combinational.
        decls = parse_lowered(ROBOT)
        assert any(isinstance(d, StructDecl) and d.name == "Robot" for d in decls)


class TestLowering:
    def test_composite_struct_embeds_children(self):
        decls = parse_lowered(CHAIN)
        chain = next(d for d in decls if isinstance(d, StructDecl) and d.name == "Chain")
        assert [f.name for f in chain.fields] == ["a", "b"]
        assert [f.type.name for f in chain.fields] == ["Ramp", "Integrator"]

    def test_step_copies_then_calls_children(self):
        decls = parse_lowered(CHAIN)
        step = next(
            d for d in decls
            if isinstance(d, FunctionDecl) and d.name == "Chain_step"
        )
        c = flow_to_c(decls)
        # Port copy before child step; Ramp before Integrator (decl order /
        # state-broken edge does not constrain).
        assert "self->b.u = self->a.out" in c
        assert "Ramp_step((&(self->a)), dt)" in c
        assert "Integrator_step((&(self->b)), dt)" in c
        a_pos = c.index("Ramp_step((&(self->a)), dt)")
        b_copy = c.index("self->b.u = self->a.out")
        b_step = c.index("Integrator_step((&(self->b)), dt)")
        assert b_copy < b_step
        assert a_pos < b_step

    def test_robot_feedback_order(self):
        c = flow_to_c(parse_lowered(ROBOT))
        assert "self->plant.voltage = self->controller.command" in c
        assert "self->controller.feedback = self->plant.speed_out" in c
        assert "Motor_step((&(self->plant)), dt)" in c
        assert "Controller_step((&(self->controller)), dt)" in c

    def test_lowered_chain_is_strict_clean(self):
        result = TypeChecker().check(parse_lowered(CHAIN))
        assert result.errors == []

    def test_lowered_robot_is_strict_clean(self):
        result = TypeChecker().check(parse_lowered(ROBOT))
        assert result.errors == []

    def test_composite_may_have_no_own_state(self):
        decls = parse_lowered(CHAIN)
        names = {d.name for d in decls if isinstance(d, FunctionDecl)}
        assert "Chain_step" in names
        assert "Chain_new" in names


# A parent flow port (input/state) driving a child input: `signal -> g.x`.
PARENT_SOURCE = """
flow Gain {
    state y : f64 = 0.0
    input x : f64
    output out : f64 = y
    param k : f64 = 2.0
    y evolves as k * x - y
}

flow Chain {
    input signal : f64
    g : Gain

    connect {
        signal -> g.x
    }
}
"""


class TestParentSource:
    def test_bare_source_parses_as_parent_port(self):
        flows = {d.name: d for d in parse_raw(PARENT_SOURCE) if isinstance(d, FlowDecl)}
        conn = flows["Chain"].connections[0]
        # Empty src_member marks a parent-port source.
        assert (conn.src_member, conn.src_port, conn.dst_member, conn.dst_port) == (
            "", "signal", "g", "x",
        )

    def test_parent_source_copies_from_self_field(self):
        c = flow_to_c(parse_lowered(PARENT_SOURCE))
        # Parent input is a field on self directly, copied into the child input
        # before the child steps.
        assert "self->g.x = self->signal" in c
        copy = c.index("self->g.x = self->signal")
        step = c.index("Gain_step((&(self->g)), dt)")
        assert copy < step

    def test_parent_source_is_strict_clean(self):
        assert TypeChecker().check(parse_lowered(PARENT_SOURCE)).errors == []

    def test_bare_source_must_be_a_real_parent_port(self):
        code = PARENT_SOURCE.replace("signal -> g.x", "nope -> g.x")
        try:
            parse_lowered(code)
            raise AssertionError("expected FlowSyntaxError")
        except FlowSyntaxError as exc:
            assert "not a port of this flow" in str(exc)

    def test_parent_output_source_rejected(self):
        # A parent *output* is not a valid source (only input/state).
        code = """
flow Gain {
    state y : f64 = 0.0
    input x : f64
    output out : f64 = y
    y evolves as x - y
}

flow Chain {
    input signal : f64
    output echo : f64 = signal
    g : Gain

    connect {
        echo -> g.x
    }
}
"""
        try:
            parse_lowered(code)
            raise AssertionError("expected FlowSyntaxError")
        except FlowSyntaxError as exc:
            assert "must be an input or state" in str(exc)


# `output y = signal |> FlowA |> FlowB` — flows composed as pipeline stages.
STAGES = """
flow Gain {
    state y : f64 = 0.0
    input x : f64
    output out : f64 = y
    param k : f64 = 2.0
    y evolves as k * x - y
}

flow Limiter {
    state z : f64 = 0.0
    input w : f64
    output out : f64 = z
    z evolves as w - z
}

flow Chain {
    input signal : f64
    output result : f64 = signal |> Gain |> Limiter
}
"""


class TestFlowPipelineStages:
    def _chain(self, decls):
        # After lowering, Chain is a struct; inspect its lowered step in C.
        return flow_to_c(decls)

    def test_stages_become_children_and_wires(self):
        raw = {d.name: d for d in parse_raw(STAGES) if isinstance(d, FlowDecl)}
        # parse_raw skips flow expansion, so the sugar is still a call chain.
        chain = raw["Chain"]
        assert chain.children == []
        # The output expr is the |>-lowered nested call Limiter(Gain(signal)).
        assert chain.outputs[0].expr.name == "Limiter"

    def test_lowered_pipeline_wiring_and_order(self):
        c = flow_to_c(parse_lowered(STAGES))
        # Two synthesized stage children.
        assert "Gain __result_stage0;" in c
        assert "Limiter __result_stage1;" in c
        # Source -> stage0 -> stage1, output reads the last stage.
        assert "self->__result_stage0.x = self->signal" in c
        assert "self->__result_stage1.w = self->__result_stage0.out" in c
        assert "self->result = self->__result_stage1.out" in c
        # Copy precedes the corresponding child step.
        assert c.index("self->__result_stage0.x = self->signal") < c.index(
            "Gain_step((&(self->__result_stage0)), dt)"
        )

    def test_lowered_pipeline_is_strict_clean(self):
        assert TypeChecker().check(parse_lowered(STAGES)).errors == []

    def test_multi_input_stage_rejected(self):
        code = """
flow Two {
    state s : f64 = 0.0
    input a : f64
    input b : f64
    output o : f64 = s
    s evolves as a
}
flow Ch {
    input sig : f64
    output r : f64 = sig |> Two
}
"""
        try:
            parse_lowered(code)
            raise AssertionError("expected FlowSyntaxError")
        except FlowSyntaxError as exc:
            assert "exactly one input" in str(exc)

    def test_plain_function_output_is_not_desugared(self):
        # A non-flow callee in output position stays an ordinary call.
        code = """
function double(v: f64) -> f64 { return v * 2.0 }
flow F {
    state s : f64 = 1.0
    output o : f64 = double(s)
    s evolves as 0.0
}
"""
        decls = parse_lowered(code)
        f = next(d for d in decls if isinstance(d, StructDecl) and d.name == "F")
        # No synthesized stage fields were added.
        assert not any(field.name.startswith("__") for field in f.fields)


# A stage with a parameter override: `Gain { k: 3.0 }` (colon = value form).
STAGE_PARAMS = """
flow Gain {
    state y : f64 = 0.0
    input x : f64
    output out : f64 = y
    param k : f64 = 2.0
    y evolves as k * x - y
}

flow Chain {
    input signal : f64
    output result : f64 = signal |> Gain { k: 3.0 }
}
"""


class TestStageParams:
    def test_override_applied_in_init(self):
        c = flow_to_c(parse_lowered(STAGE_PARAMS))
        # The override lands in Chain_init, after the stage's own init.
        assert "self->__result_stage0.k = 3.0" in c
        assert c.index("Gain_init") < c.index("self->__result_stage0.k = 3.0")

    def test_stage_params_are_strict_clean(self):
        assert TypeChecker().check(parse_lowered(STAGE_PARAMS)).errors == []

    def test_unknown_param_rejected(self):
        code = STAGE_PARAMS.replace("k: 3.0", "bogus: 3.0")
        try:
            parse_lowered(code)
            raise AssertionError("expected FlowSyntaxError")
        except FlowSyntaxError as exc:
            assert "has no param 'bogus'" in str(exc)

    def test_stage_params_outside_flow_rejected(self):
        # `Name { p: v }` in a function body has no flow-stage meaning.
        code = """
flow Gain {
    state y : f64 = 0.0
    input x : f64
    output out : f64 = y
    param k : f64 = 2.0
    y evolves as k * x - y
}
function main() -> i32 {
    let z = 5 |> Gain { k: 3.0 }
    return 0
}
"""
        try:
            parse_lowered(code)
            raise AssertionError("expected an error")
        except Exception as exc:
            assert "stage" in str(exc)
