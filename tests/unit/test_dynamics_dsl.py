"""Tests for the dsys dynamical-systems surface syntax.

The expander is flowc's (compiler/src/dynamics_dsl.flow); these go through
the Python bridge. compiler/scripts/parity_dynamics_dsl.sh holds the full
expansion byte for byte against the retired Python expander.
"""

import re

import pytest

from flow.dynamics_dsl import expand_dynamics_dsl, has_dynamics_dsl


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


class TestDynamicsDSLExpansion:
    def test_expand_strips_dsl_blocks(self):
        out = expand_dynamics_dsl(SAMPLE)
        assert "dsys plant {" not in out
        assert "ga evolve" not in out
        assert "function main" in out
        assert "dsys_discrete(2, 1, 1, 0.10000000000000001," in out
        assert "horizon_finite(50)" in out
        assert "population: 8, generations: 20, horizon: 50, mutation: 0.25" in out

    def test_invalid_dsys_raises(self):
        with pytest.raises(SyntaxError):
            expand_dynamics_dsl("dsys bad\n")

    def test_expand_emits_discrete_system(self):
        out = expand_dynamics_dsl(SAMPLE)
        assert "__dsys_plant" in out
        assert "let plant: DynamicalSystem = __dsys_plant" in out

    def test_expand_emits_ga_evolve(self):
        out = expand_dynamics_dsl(SAMPLE)
        assert "ga_evolve_traced" in out
        assert "array<f64, 8>" in out
        assert "__ga_e0_k1" in out

    def test_expand_sense_controllable_is_i32(self):
        out = expand_dynamics_dsl(SAMPLE)
        assert "let mut plant_ok: i32" in out
        assert "is_controllable" in out


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
    def test_dynamics_block_expands(self):
        assert has_dynamics_dsl(NAMESPACED_BLOCK)
        out = expand_dynamics_dsl(NAMESPACED_BLOCK)
        assert "dynamics {" not in out
        assert "dsys plant" not in out
        assert "__dsys_plant" in out
        assert "horizon_finite(50)" in out
        assert out.count("is_controllable(") == 1

    def test_dyn_dot_prefix_expands(self):
        out = expand_dynamics_dsl(NAMESPACED_PREFIX)
        assert "dyn.dsys" not in out
        assert "dynamics.horizon" not in out
        assert "dsys_discrete(2, 1, 1," in out
        assert "horizon_finite(40)" in out
        assert out.startswith(
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
        out = expand_dynamics_dsl(REPRESENT_IN_FLOW)
        assert "represent linear" not in out
        assert "flow Pendulum" in out
        assert "angle evolves as velocity" in out
        assert "[0.0, 1.0, -9.8100000000000005, 0.0]" in out
        assert "dsys_continuous(2, 1, 1," in out

    def test_top_level_represent_linear_name(self):
        out = expand_dynamics_dsl(REPRESENT_TOP_LEVEL)
        assert "represent linear" not in out
        assert "let __dsys_Plant_lin: DynamicalSystem = dsys_discrete(" in out

    def test_at_without_A_errors(self):
        with pytest.raises(SyntaxError, match="linearization coefficients required"):
            expand_dynamics_dsl(REPRESENT_AT_ONLY)

    def test_reserved_represent_kind_errors(self):
        src = "represent koopman {\n  observables 4\n}\nfunction main() -> i32 { return 0 }\n"
        with pytest.raises(SyntaxError, match="not yet implemented"):
            expand_dynamics_dsl(src)

    def test_nonlinear_represent_is_noop(self):
        src = (
            "flow Ball {\n"
            "    state h : f64 = 1.0\n"
            "    h evolves as 0.0\n"
            "    represent nonlinear { }\n"
            "}\n"
            "function main() -> i32 { return 0 }\n"
        )
        out = expand_dynamics_dsl(src)
        assert "represent nonlinear" not in out
        assert "dsys" not in out

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
    def test_strips_and_lowers_portrait(self):
        out = expand_dynamics_dsl(REPRESENT_PHASE_PORTRAIT)
        assert "    represent phase_portrait(" not in out
        assert "const Lorenz_portrait_trail: i32 = 320" in out
        assert "const Lorenz_portrait_win_w: i32 = 900" in out
        assert "project_axis(xs[idx], -25.0, 25.0, 900, 10)" in out

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
            expand_dynamics_dsl(src)

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
            expand_dynamics_dsl(src)


class TestDynamicsDSLWFC:
    def test_expand_wfc_and_couple(self):
        out = expand_dynamics_dsl(WFC_SAMPLE)
        assert "wfc field" not in out
        assert "couple plant" not in out
        assert "let __wfc_layout_cells: array<i32, 16>" in out
        assert "wfc_run_guided" in out
        assert "couple_ga_wfc_guidance" in out
        assert "guide_state_evolution" in out

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
    def test_expand_vision_analyze_lqr(self):
        out = expand_dynamics_dsl(ANALYZE_LQR)
        assert "analyze plant" not in out
        assert "let __lqr_0_q: array<f64, 2> = [1.0, 1.0]" in out
        assert "__lqr_0_q, 1.0, 2, __lqr_0_k, 200)" in out
        assert "let k2: f64 = __lqr_0_k[1]" in out

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
        out = expand_dynamics_dsl(src)
        assert out.count("ga_analyze_control_search(") == 1
        assert "dlqr_diag_q_scalar_u" not in out
