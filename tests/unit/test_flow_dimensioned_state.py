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

from flow.parser import FlowSyntaxError, Lexer, Parser  # noqa: E402


def lower(source: str):
    return Parser(Lexer(source), source=source).parse()


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


# The end-to-end integration run is tests/cgen/flow_dimensioned_state_pendulum.


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
