"""Denotational MLIR emitter for flow evolution blocks (#664/#665/#667 lane).

Pins the dialect shape from docs/design/denotational-mlir.md: a `flow` block
emits a `flow.system` with `flow.state`/`flow.param` members and one
`flow.evolve` region per state, and the derivative expression lowers to
`arith`/`math` so the vector field stays visible to later passes.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

import pytest

from flow.denotational_mlir import (
    raw_flow_decls,
    emit_denotational_mlir,
    emit_ensemble_step,
)

PENDULUM = """\
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


def _emit(source: str) -> str:
    fds = raw_flow_decls(source)
    assert fds, "no flow blocks parsed"
    return emit_denotational_mlir(fds[0])


def test_system_and_members():
    mlir = _emit(PENDULUM)
    assert "flow.system @Pendulum {" in mlir
    assert 'flow.state "angle" : f64 {init = 2.0}' in mlir
    assert 'flow.state "velocity" : f64 {init = 0.0}' in mlir
    assert 'flow.param "gravity" : f64 {init = 9.81}' in mlir
    assert 'flow.param "damping" : f64 {init = 0.5}' in mlir


def test_one_evolve_region_per_state():
    mlir = _emit(PENDULUM)
    assert mlir.count("flow.evolve %") == 2
    assert mlir.count("flow.deriv ") == 2


def test_identity_derivative_references_the_state():
    # `angle evolves as velocity` is dx/dt = velocity, a bare member reference.
    mlir = _emit(PENDULUM)
    assert "flow.evolve %angle {\n    flow.deriv %velocity : f64\n  }" in mlir


def test_arithmetic_derivative_lowers_to_arith_and_math():
    mlir = _emit(PENDULUM)
    # velocity's derivative uses div, neg, sin, two muls and a sub.
    for op in ("arith.divf", "arith.negf", "math.sin", "arith.mulf", "arith.subf"):
        assert op in mlir, op
    # No opaque fallback for this fully-lowerable derivative.
    assert "flow.opaque" not in mlir


def test_pure_continuous_system_has_no_pending_marker():
    # Pendulum has only evolves, so the output is complete.
    assert "flow.pending" not in _emit(PENDULUM)


def test_every_block_emits_flow_every_with_becomes():
    # An `every P { x becomes e }` reset maps to flow.every with a flow.becomes
    # region carrying the update expression.
    src = """\
flow Blinker {
    state level : f64 = 0.0
    param on : f64 = 1.0
    level evolves as 0.0
    every 10 ms {
        level becomes on
    }
}
"""
    mlir = _emit(src)
    assert "flow.system @Blinker {" in mlir
    assert "flow.every 10000000 {" in mlir
    assert "flow.becomes %level {" in mlir
    assert "flow.value %on : f64" in mlir


def test_when_block_emits_flow_when_with_threshold_and_reset():
    # A `when x reaches L { x becomes e }` zero-crossing maps to flow.when with
    # a threshold region and a do-region of flow.becomes resets.
    src = """\
flow Ball {
    state height   : f64 = 2.0
    state velocity : f64 = 0.0
    param gravity  : f64 = 9.81
    param restitution : f64 = 0.8
    height evolves as velocity
    velocity evolves as -gravity
    when height reaches 0.0 {
        velocity becomes -restitution * velocity
        height becomes 0.0
    }
}
"""
    mlir = _emit(src)
    assert "flow.when %height reaches {" in mlir
    assert "flow.threshold %d0 : f64" in mlir
    assert "} do {" in mlir
    assert "flow.becomes %velocity {" in mlir
    assert "flow.becomes %height {" in mlir


def test_unsupported_construct_is_preserved_as_opaque():
    # A modulo in a derivative is outside the lowered subset, so it is kept as
    # a flow.opaque op carrying its source rather than dropped.
    src = """\
flow Osc {
    state x : f64 = 1.0
    param k : f64 = 3.0
    x evolves as k % x
}
"""
    mlir = _emit(src)
    assert "flow.opaque" in mlir
    assert "k % x" in mlir
    assert "flow.evolve %x {" in mlir


# --- ensemble fusion: the payoff of keeping the vector field visible -------

def _ensemble(source: str, n: int) -> str:
    fds = raw_flow_decls(source)
    assert fds, "no flow blocks parsed"
    return emit_ensemble_step(fds[0], n)


def test_ensemble_step_vectorizes_states_and_params():
    mlir = _ensemble(PENDULUM, 1000)
    assert "flow.ensemble @Pendulum x 1000 {" in mlir
    assert 'flow.ensemble_state "angle" : vector<1000xf64>' in mlir
    assert 'flow.ensemble_param "gravity" : vector<1000xf64>' in mlir


def test_ensemble_step_fuses_the_derivative_over_vectors():
    # The whole ensemble's derivative is one vectorized region: the arith/math
    # ops run on vector<1000xf64>, so N systems step in one kernel.
    mlir = _ensemble(PENDULUM, 1000)
    assert "flow.step %dt {" in mlir
    assert "math.sin %angle : vector<1000xf64>" in mlir
    assert "arith.mulf %d1, %d2 : vector<1000xf64>" in mlir
    assert "flow.deriv %d5 : vector<1000xf64>" in mlir
    # No scalar f64 arithmetic leaked into the fused region.
    assert " : f64" not in mlir.split("flow.step")[1]


def test_ensemble_size_must_be_positive():
    fd = raw_flow_decls(PENDULUM)[0]
    with pytest.raises(ValueError):
        emit_ensemble_step(fd, 0)


# --- standalone CLI entry point --------------------------------------------

def _load_cli():
    import importlib.util

    root = os.path.join(os.path.dirname(__file__), "..", "..")
    path = os.path.join(root, "scripts", "emit_denotational_mlir.py")
    spec = importlib.util.spec_from_file_location("emit_denotational_mlir", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_cli_renders_system_and_ensemble():
    cli = _load_cli()
    system = cli.render(PENDULUM, None)
    assert "flow.system @Pendulum {" in system
    ensemble = cli.render(PENDULUM, 64)
    assert "flow.ensemble @Pendulum x 64 {" in ensemble
    assert "vector<64xf64>" in ensemble


def test_cli_reports_when_no_flow_blocks():
    cli = _load_cli()
    assert cli.render("function main() -> i32 { return 0 }", None) == "// no flow blocks found"


# --- wired into the real transpiler CLI ------------------------------------

def _run_transpiler(*extra):
    import subprocess

    root = os.path.join(os.path.dirname(__file__), "..", "..")
    src = os.path.join(root, "src")
    example = os.path.join(root, "examples", "evolution", "pendulum_evolves.flow")
    env = dict(os.environ)
    env["PYTHONPATH"] = src + os.pathsep + env.get("PYTHONPATH", "")
    return subprocess.run(
        [sys.executable, "-m", "flow.transpiler", example, *extra],
        capture_output=True, text=True, env=env,
    )


def test_transpiler_flag_emits_denotational_system():
    result = _run_transpiler("--emit-denotational-mlir")
    assert result.returncode == 0, result.stderr
    assert "flow.system @Pendulum {" in result.stdout
    assert "flow.evolve %velocity {" in result.stdout


def test_transpiler_flag_emits_ensemble_with_size():
    result = _run_transpiler("--emit-denotational-mlir", "512")
    assert result.returncode == 0, result.stderr
    assert "flow.ensemble @Pendulum x 512 {" in result.stdout
    assert "vector<512xf64>" in result.stdout
