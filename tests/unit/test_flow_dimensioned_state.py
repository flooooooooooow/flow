"""A flow member may be elided and may carry a dimension.

VISION.md has written this since the beginning:

    flow Pendulum {
        angle : Angle
        velocity : AngularVelocity

        angle evolves as velocity
    }

Three things stopped it compiling. A bare `name : T` member was read as flow
composition, so a type that was not a flow was an error. A member had to be
f64 or f32. And a state without an initializer was an error, though an elided
member has nowhere to put one.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from flow.flow_blocks import expand_flow_decls  # noqa: E402
from flow.parser import FlowSyntaxError, parse_flow_code  # noqa: E402


def lower(source: str):
    return expand_flow_decls(parse_flow_code(source), source=source)


def test_a_bare_unit_member_is_state():
    """`angle : Angle` was read as composition and rejected."""
    assert lower(
        """
unit Angle

flow Pendulum {
    angle : Angle
    angle evolves as 1.0
}
"""
    )


def test_a_bare_scalar_member_is_state():
    assert lower(
        """
flow Ramp {
    x : f64
    x evolves as 1.0
}
"""
    )


def test_a_bare_flow_member_is_still_composition():
    """The form that already worked keeps its meaning."""
    assert lower(
        """
flow Inner {
    state x : f64 = 0.0
    x evolves as 1.0
}

flow Outer {
    plant : Inner
}
"""
    )


def test_a_member_naming_neither_is_still_an_error():
    with pytest.raises(FlowSyntaxError, match="not a flow in this file"):
        lower(
            """
flow Outer {
    plant : NoSuchThing
}
"""
        )


def test_state_without_an_initializer_starts_at_zero():
    assert lower(
        """
flow F {
    state x : f64
    x evolves as 1.0
}
"""
    )


def test_an_integer_member_is_still_rejected():
    with pytest.raises(FlowSyntaxError, match="f64, f32, or a declared unit"):
        lower(
            """
flow F {
    state x : i32 = 0
    x evolves as x
}
"""
        )


def test_a_dimensioned_flow_integrates():
    """End to end: units on state, a real step, correct arithmetic."""
    import os
    import subprocess
    import tempfile

    source = """
unit Angle
unit AngularVelocity

flow Pendulum {
    angle : Angle
    velocity : AngularVelocity
    solver { dt 100 ms  method euler }

    angle evolves as 2.0
    velocity evolves as 0.0 - 9.81
}

function main() -> i32 {
    let mut p: Pendulum = Pendulum_new()
    let mut i: i32 = 0
    while i < 10 {
        Pendulum_step(&p, Pendulum_default_dt())
        i = i + 1
    }
    printf("%.3f %.3f\\n", p.angle, p.velocity)
    return 0
}
"""
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    with tempfile.TemporaryDirectory() as td:
        src, c, exe = Path(td) / "p.flow", Path(td) / "p.c", Path(td) / "p"
        src.write_text(source)
        assert subprocess.run(
            [sys.executable, "-m", "flow.transpiler", str(src), "--c", "-o", str(c)],
            cwd=ROOT, env=env, capture_output=True, text=True,
        ).returncode == 0
        assert subprocess.run(
            ["clang", "-w", "-O0", "-o", str(exe), str(c), "-lm"],
            capture_output=True, text=True,
        ).returncode == 0
        out = subprocess.run([str(exe)], capture_output=True, text=True).stdout
    # 2.0 rad/s and -9.81 rad/s^2 over ten 100ms steps.
    assert out.strip() == "2.000 -9.810", out


def test_an_alias_of_radian_satisfies_sin():
    """`type Angle = Radian` is transparent, so sin(angle) is fine."""
    assert lower(
        """
unit Radian
type Angle = Radian

flow Pendulum {
    angle : Angle
    angle evolves as sin(angle)
}
"""
    )
