"""Tests for the dsys dynamical-systems surface syntax preprocessor."""

import re

import pytest

from flow.dynamics_dsl import (
    compile_dynamics_program,
    expand_dynamics_dsl,
    has_dynamics_dsl,
    parse_dynamics_dsl,
)


SAMPLE = """
dsys plant {
    discrete
    dt 0.1
    n 2 m 1 p 1
    A 1.0 0.1 0.0 1.0
    B 0.0 0.1
    C 1.0 0.0
}

horizon rollout finite 50

sense on plant {
    controllable -> plant_ok
    spectral -> rho_open
}

ga evolve on plant over rollout -> k1 k2 {
    population 8
    generations 20
    mutation 0.25
}

function main() -> i32 {
    return 0
}
"""


class TestDynamicsDSLDetection:
    def test_has_dynamics_dsl_positive(self):
        assert has_dynamics_dsl(SAMPLE)

    def test_has_dynamics_dsl_negative(self):
        assert not has_dynamics_dsl('println("hello")')


class TestDynamicsDSLParser:
    def test_parse_strips_dsl_blocks(self):
        program, stripped = parse_dynamics_dsl(SAMPLE)
        assert "dsys plant" not in stripped
        assert "ga evolve" not in stripped
        assert "function main" in stripped
        assert "plant" in program.systems
        assert program.systems["plant"].n == 2
        assert program.horizons["rollout"].steps == 50
        assert len(program.ga_evolutions) == 1
        assert program.ga_evolutions[0].population == 8

    def test_invalid_dsys_raises(self):
        with pytest.raises(SyntaxError):
            parse_dynamics_dsl("dsys bad\n")


class TestDynamicsDSLCompiler:
    def test_compile_emits_discrete_system(self):
        program, _ = parse_dynamics_dsl(SAMPLE)
        code = compile_dynamics_program(program)
        assert "dsys_discrete" in code
        assert "__dsys_plant" in code
        assert "horizon_finite(50)" in code

    def test_compile_emits_ga_evolve(self):
        program, _ = parse_dynamics_dsl(SAMPLE)
        code = compile_dynamics_program(program)
        assert "ga_evolve_traced" in code
        assert "array<f64, 8>" in code
        assert "__ga_e0_k1" in code

    def test_compile_sense_controllable_is_i32(self):
        program, _ = parse_dynamics_dsl(SAMPLE)
        code = compile_dynamics_program(program)
        assert "let mut plant_ok: i32" in code
        assert "is_controllable" in code


class TestDynamicsDSLExpand:
    def test_expand_injects_import_at_top(self):
        out = expand_dynamics_dsl(SAMPLE)
        assert out.startswith('import "stdlib/dynamics/ga_analysis.flow"')

    def test_expand_injects_setup_into_main(self):
        out = expand_dynamics_dsl(SAMPLE)
        assert "dsys DSL expansion" in out
        m = re.search(r"function\s+main\s*\([^)]*\)\s*->\s*\w+\s*\{", out)
        assert m is not None
        body_start = m.end()
        assert "dsys_discrete" in out[body_start:body_start + 800]

    def test_expand_noop_without_dsl(self):
        plain = 'function main() -> i32 { return 0 }'
        assert expand_dynamics_dsl(plain) == plain