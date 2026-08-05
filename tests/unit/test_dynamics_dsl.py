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
        assert "let plant: DynamicalSystem = __dsys_plant" in code
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


WFC_SAMPLE = SAMPLE + """
wfc field layout {
    size 4 4
    tiles 3
    seed 7
    pin 0 1
    collapse 20
}

couple plant field layout using report k1 k2 {
    guidance -> guide
    collapsed -> wfc_ok
}

guide plant with k1 k2 through layout using guide over rollout {
    energy -> E_guide
    spectral -> rho_guide
}
"""


NAMESPACED_BLOCK = """
dynamics {
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
}

function main() -> i32 {
    return plant_ok
}
"""

NAMESPACED_PREFIX = """
dyn.dsys plant {
    discrete
    n 2 m 1 p 1
    A 1.0 0.1 0.0 1.0
    B 0.0 0.1
    C 1.0 0.0
}
dynamics.horizon rollout finite 40
dyn.sense on plant {
    controllable -> ok
}

function main() -> i32 { return ok }
"""


class TestDynamicsNamespaces:
    def test_dynamics_block_parses(self):
        assert has_dynamics_dsl(NAMESPACED_BLOCK)
        program, stripped = parse_dynamics_dsl(NAMESPACED_BLOCK)
        assert "dynamics {" not in stripped
        assert "dsys plant" not in stripped
        assert "plant" in program.systems
        assert program.horizons["rollout"].steps == 50
        assert len(program.senses) == 1

    def test_dyn_dot_prefix_parses(self):
        program, stripped = parse_dynamics_dsl(NAMESPACED_PREFIX)
        assert "dyn.dsys" not in stripped
        assert "dynamics.horizon" not in stripped
        assert program.systems["plant"].n == 2
        assert program.horizons["rollout"].steps == 40
        assert expand_dynamics_dsl(NAMESPACED_PREFIX).startswith(
            'import "stdlib/dynamics/ga_analysis.flow"'
        )


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


REPRESENT_IN_FLOW = """
flow Pendulum {
    state angle : f64 = 0.0
    state velocity : f64 = 0.0
    angle evolves as velocity
    velocity evolves as -9.81 * angle

    represent linear {
        at (angle: 0.0, velocity: 0.0)
        outputs (angle)
        continuous
        dt 0.01
        A 0.0 1.0 -9.81 0.0
        B 0.0 1.0
        C 1.0 0.0
    }
}

sense on Pendulum_lin {
    controllable -> lin_ok
    spectral -> lin_rho
}

function main() -> i32 {
    return lin_ok
}
"""

REPRESENT_TOP_LEVEL = """
represent linear Plant {
    discrete
    dt 0.1
    n 2 m 1 p 1
    A 1.0 0.1 0.0 1.0
    B 0.0 0.1
    C 1.0 0.0
}

sense on Plant_lin {
    spectral -> rho
}

function main() -> i32 { return 0 }
"""

REPRESENT_AT_ONLY = """
represent linear Plant {
    at (x: 0.0, v: 0.0)
    outputs (x)
}

function main() -> i32 { return 0 }
"""


class TestRepresentLinear:
    def test_has_dynamics_dsl_detects_represent(self):
        assert has_dynamics_dsl(REPRESENT_IN_FLOW)
        assert has_dynamics_dsl("represent linear Foo { A 0.0 1.0 0.0 0.0 }\n")

    def test_strips_represent_from_flow_body(self):
        program, stripped = parse_dynamics_dsl(REPRESENT_IN_FLOW)
        assert "represent linear" not in stripped
        assert "flow Pendulum" in stripped
        assert "angle evolves as velocity" in stripped
        assert "Pendulum_lin" in program.systems
        sys = program.systems["Pendulum_lin"]
        assert sys.mode == "continuous"
        assert sys.n == 2
        assert sys.m == 1
        assert sys.A == [0.0, 1.0, -9.81, 0.0]
        assert len(program.represents) == 1
        assert program.represents[0].at_point == {"angle": 0.0, "velocity": 0.0}

    def test_top_level_represent_linear_name(self):
        program, stripped = parse_dynamics_dsl(REPRESENT_TOP_LEVEL)
        assert "represent linear" not in stripped
        assert "Plant_lin" in program.systems
        assert program.systems["Plant_lin"].mode == "discrete"

    def test_at_without_A_errors(self):
        with pytest.raises(SyntaxError, match="linearization coefficients required"):
            parse_dynamics_dsl(REPRESENT_AT_ONLY)

    def test_reserved_represent_kind_errors(self):
        src = "represent koopman {\n  observables 4\n}\nfunction main() -> i32 { return 0 }\n"
        with pytest.raises(SyntaxError, match="not yet implemented"):
            parse_dynamics_dsl(src)

    def test_nonlinear_represent_is_noop(self):
        src = (
            "flow Ball {\n"
            "    state h : f64 = 1.0\n"
            "    h evolves as 0.0\n"
            "    represent nonlinear { }\n"
            "}\n"
            "function main() -> i32 { return 0 }\n"
        )
        program, stripped = parse_dynamics_dsl(src)
        assert "represent nonlinear" not in stripped
        assert program.systems == {}
        assert program.represents == []

    def test_expand_emits_continuous_dsys(self):
        out = expand_dynamics_dsl(REPRESENT_IN_FLOW)
        assert "dsys_continuous" in out
        assert "__dsys_Pendulum_lin" in out
        assert "is_controllable" in out
        assert "represent linear" not in out


REPRESENT_PHASE_PORTRAIT = """
import "stdlib/gfx.flow"
import "stdlib/dynamics/portrait.flow"

flow Lorenz {
    state x : f64 = 1.0
    state z : f64 = 1.0
    x evolves as 0.0
    z evolves as 0.0

    represent phase_portrait(x, z) {
        trail 320
        window 900, 700
        map x in [-25, 25] -> col
        map z in [0, 55] -> row
    }
}

function main() -> i32 {
    return 0
}
"""


class TestRepresentPhasePortrait:
    def test_strips_and_parses_portrait(self):
        program, stripped = parse_dynamics_dsl(REPRESENT_PHASE_PORTRAIT)
        assert "represent phase_portrait" not in stripped
        assert len(program.portraits) == 1
        p = program.portraits[0]
        assert p.flow_name == "Lorenz"
        assert p.axis0 == "x"
        assert p.axis1 == "z"
        assert p.trail == 320
        assert p.win_w == 900
        assert p.maps["x"] == (-25.0, 25.0, "col")
        assert p.maps["z"] == (0.0, 55.0, "row")

    def test_expand_emits_portrait_frame(self):
        out = expand_dynamics_dsl(REPRESENT_PHASE_PORTRAIT)
        assert "Lorenz_portrait_frame" in out
        assert "Lorenz_portrait_trail" in out
        assert "trail_push_2d" in out
        assert "project_axis" in out
        assert "    represent phase_portrait" not in out
        # row axis inverts for screen y
        assert "project_axis(zs[idx], 55.0, 0.0" in out

    def test_portrait_outside_flow_errors(self):
        src = (
            "represent phase_portrait(x, z) {\n"
            "    trail 10\n"
            "    window 100, 100\n"
            "    map x in [0, 1] -> col\n"
            "    map z in [0, 1] -> row\n"
            "}\n"
            "function main() -> i32 { return 0 }\n"
        )
        with pytest.raises(SyntaxError, match="inside"):
            parse_dynamics_dsl(src)

    def test_portrait_missing_map_errors(self):
        src = (
            "flow F {\n"
            "    state x : f64 = 0.0\n"
            "    state z : f64 = 0.0\n"
            "    x evolves as 0.0\n"
            "    represent phase_portrait(x, z) {\n"
            "        trail 10\n"
            "        window 100, 100\n"
            "        map x in [0, 1] -> col\n"
            "    }\n"
            "}\n"
            "function main() -> i32 { return 0 }\n"
        )
        with pytest.raises(SyntaxError, match="need map for both"):
            parse_dynamics_dsl(src)


class TestDynamicsDSLWFC:
    def test_parse_wfc_and_couple(self):
        program, stripped = parse_dynamics_dsl(WFC_SAMPLE)
        assert "wfc field" not in stripped
        assert "couple plant" not in stripped
        assert "layout" in program.wfc_fields
        assert program.wfc_fields["layout"].width == 4
        assert len(program.couples) == 1
        assert len(program.guides) == 1

    def test_compile_wfc_coupling(self):
        program, _ = parse_dynamics_dsl(WFC_SAMPLE)
        code = compile_dynamics_program(program)
        assert "wfc_run_guided" in code
        assert "couple_ga_wfc_guidance" in code
        assert "guide_state_evolution" in code
        assert "__wfc_layout" in code

    def test_expand_imports_coupling_module(self):
        out = expand_dynamics_dsl(WFC_SAMPLE)
        assert 'import "stdlib/dynamics/wfc_ga_coupling.flow"' in out

ANALYZE_LQR = """
dsys plant {
    discrete
    dt 0.1
    n 2 m 1 p 1
    A 1.0 0.1 0.0 1.0
    B 0.0 0.1
    C 1.0 0.0
}

analyze plant {
    lqr {
        Q 1.0 1.0
        R 1.0
        -> k1 k2
    }
}

function main() -> i32 {
    return 0
}
"""


class TestAnalyzeLqr:
    def test_parse_vision_analyze_lqr(self):
        program, stripped = parse_dynamics_dsl(ANALYZE_LQR)
        assert "analyze plant" not in stripped
        assert len(program.analyze_lqrs) == 1
        lqr = program.analyze_lqrs[0]
        assert lqr.system == "plant"
        assert lqr.q_diag == [1.0, 1.0]
        assert lqr.r == 1.0
        assert lqr.gain_vars == ["k1", "k2"]

    def test_expand_emits_dlqr(self):
        out = expand_dynamics_dsl(ANALYZE_LQR)
        assert "dlqr_diag_q_scalar_u" in out
        assert 'import "stdlib/dynamics/lqr.flow"' in out
        assert "let k1: f64" in out
        assert "1.0" in out  # R must stay f64 literal

    def test_ga_form_still_works(self):
        src = (
            "dsys plant {\n discrete\n dt 0.1\n n 2 m 1 p 1\n"
            " A 1.0 0.1 0.0 1.0\n B 0.0 0.1\n C 1.0 0.0\n}\n"
            "horizon h finite 10\n"
            "analyze plant ga k1 k2 over h -> report { full }\n"
            "function main() -> i32 { return 0 }\n"
        )
        program, _ = parse_dynamics_dsl(src)
        assert len(program.analyzes) == 1
        assert program.analyze_lqrs == []
