"""Tests for field / boundary PDE surface (#163)."""

import pytest

from flow.field_dsl import (
    expand_field_dsl,
    has_field_dsl,
    parse_field_dsl,
)


SAMPLE = """
import "stdlib/dynamics/pde.flow"

const AMBIENT: f64 = 20.0

field T : f64[32] on Line
T evolves as laplacian(T)
boundary T { left = AMBIENT  right = AMBIENT }

function main() -> i32 {
    return 0
}
"""


class TestFieldDSL:
    def test_detects_field(self):
        assert has_field_dsl(SAMPLE)
        assert not has_field_dsl("function main() -> i32 { return 0 }\n")

    def test_parse_strips_and_records(self):
        fields, stripped = parse_field_dsl(SAMPLE)
        assert "field T" not in stripped
        assert "boundary T" not in stripped
        assert "T evolves as" not in stripped
        assert "T" in fields
        assert fields["T"].n == 32
        assert fields["T"].left_bc == "AMBIENT"
        assert fields["T"].right_bc == "AMBIENT"
        assert fields["T"].evolve_seen

    def test_expand_emits_step(self):
        out = expand_field_dsl(SAMPLE)
        assert "T_field_step" in out
        assert "T_field_n" in out
        assert "heat_euler_step_1d(u, next, 32, r, AMBIENT, AMBIENT)" in out
        assert "    field T" not in out

    def test_boundary_before_field_errors(self):
        src = (
            "boundary T { left = 0.0  right = 1.0 }\n"
            "field T : f64[8] on Line\n"
            "T evolves as laplacian(T)\n"
            "function main() -> i32 { return 0 }\n"
        )
        with pytest.raises(SyntaxError, match="declare"):
            parse_field_dsl(src)

    def test_missing_evolve_errors(self):
        src = (
            "field T : f64[8] on Line\n"
            "boundary T { left = 0.0  right = 1.0 }\n"
            "function main() -> i32 { return 0 }\n"
        )
        with pytest.raises(SyntaxError, match="missing"):
            parse_field_dsl(src)

    def test_flow_evolves_untouched(self):
        src = (
            "flow Ball {\n"
            "    state h : f64 = 1.0\n"
            "    h evolves as 0.0\n"
            "}\n"
            "function main() -> i32 { return 0 }\n"
        )
        assert not has_field_dsl(src)
        assert expand_field_dsl(src) == src
