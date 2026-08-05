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
