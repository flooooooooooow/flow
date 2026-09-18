"""Opt-in per-phase compile profiling for the Python host compiler (#735).

The transpiler can time each identifiable compile phase and emit a
machine-readable report, without affecting a normal compile. These tests cover
the CompileProfiler component directly and an end-to-end transpile of a tiny
`function main() -> i32` program with the mode on and off.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"

sys.path.insert(0, str(SRC))

from flow.compile_profiling import (  # noqa: E402
    CompileProfiler,
    REPORT_MARKER,
    count_ast_nodes,
    count_source_loc,
    profiling_enabled,
    profiling_mode,
)

# Phases that the in-process Python host records. external_compile and
# process_launch run in the driver, out of this process.
HOST_PHASES = [
    "startup",
    "source_read",
    "parse_resolve",
    "typecheck",
    "monomorphize",
    "codegen",
]

PROGRAM = """
function main() -> i32 {
    let x: i32 = 41
    return x + 1
}
"""


# -- component tests --------------------------------------------------------

def test_mode_off_by_default(monkeypatch):
    monkeypatch.delenv("FLOW_PROFILE", raising=False)
    assert profiling_mode() == "off"
    assert profiling_enabled() is False


@pytest.mark.parametrize("val", ["", "0", "false", "no", "off"])
def test_falsey_values_stay_off(monkeypatch, val):
    monkeypatch.setenv("FLOW_PROFILE", val)
    assert profiling_enabled() is False


@pytest.mark.parametrize("val,expected", [("1", "text"), ("on", "text"), ("json", "json")])
def test_truthy_values_enable(monkeypatch, val, expected):
    monkeypatch.setenv("FLOW_PROFILE", val)
    assert profiling_enabled() is True
    assert profiling_mode() == expected


def test_profiler_records_and_orders():
    prof = CompileProfiler()
    # Record out of canonical order on purpose.
    prof.record("codegen", 0.003)
    prof.record("startup", 0.010)
    prof.record("typecheck", 0.002)
    prof.set_source_loc(5)
    prof.set_ast_nodes(12)

    data = prof.report_dict()
    order = data["phase_order"]
    # Canonical order, regardless of insertion order.
    assert order == ["startup", "typecheck", "codegen"]

    seconds = [p["seconds"] for p in data["phases"]]
    assert all(s >= 0 for s in seconds)
    assert data["total_seconds"] == pytest.approx(0.015)
    assert data["startup_seconds"] == pytest.approx(0.010)
    assert data["source_loc"] == 5
    assert data["ast_nodes"] == 12
    assert data["loc_per_second"] == pytest.approx(5 / 0.015)
    assert data["ast_nodes_per_second"] == pytest.approx(12 / 0.015)


def test_negative_durations_clamped():
    prof = CompileProfiler()
    prof.record("codegen", -1.0)
    assert prof.phases["codegen"] == 0.0


def test_rates_zero_when_no_time():
    prof = CompileProfiler()
    prof.set_source_loc(10)
    data = prof.report_dict()
    assert data["total_seconds"] == 0.0
    assert data["loc_per_second"] == 0.0
    assert data["ast_nodes_per_second"] == 0.0


def test_phase_context_manager_measures_nonnegative():
    prof = CompileProfiler()
    with prof.phase("typecheck"):
        pass
    assert prof.phases["typecheck"] >= 0.0


def test_count_source_loc_ignores_blank_lines():
    assert count_source_loc("a\n\n  \nb\n") == 2


def test_count_ast_nodes_walks_parser_objects():
    from flow.parser import Lexer, Parser

    parser = Parser(Lexer(textwrap.dedent(PROGRAM)))
    declarations = parser.parse()
    assert count_ast_nodes(declarations) > 0


# -- end-to-end transpile ---------------------------------------------------

def _transpile(tmp_path, profile_value):
    src = tmp_path / "tiny.flow"
    src.write_text(textwrap.dedent(PROGRAM))
    out = tmp_path / "tiny.c"
    env = {**os.environ, "PYTHONPATH": str(SRC)}
    if profile_value is None:
        env.pop("FLOW_PROFILE", None)
    else:
        env["FLOW_PROFILE"] = profile_value
    run = subprocess.run(
        [sys.executable, "-m", "flow.transpiler", str(src), "--c", "--lenient", "-o", str(out)],
        cwd=ROOT, capture_output=True, text=True, env=env,
    )
    return run, out


def _parse_report(stderr):
    lines = [ln for ln in stderr.splitlines() if ln.startswith(REPORT_MARKER)]
    assert lines, f"no profile report line in stderr:\n{stderr}"
    return json.loads(lines[-1][len(REPORT_MARKER):].strip())


def test_end_to_end_report_has_host_phases(tmp_path):
    run, out = _transpile(tmp_path, "1")
    assert run.returncode == 0, run.stderr
    assert out.exists()

    data = _parse_report(run.stderr)
    names = [p["name"] for p in data["phases"]]
    # Every in-process phase is present.
    for phase in HOST_PHASES:
        assert phase in names, (phase, names)
    # Reported in canonical order.
    assert names == [p for p in HOST_PHASES if p in names]


def test_end_to_end_numbers_are_sane(tmp_path):
    run, _ = _transpile(tmp_path, "json")
    assert run.returncode == 0, run.stderr
    data = _parse_report(run.stderr)

    seconds = [p["seconds"] for p in data["phases"]]
    assert all(s >= 0 for s in seconds)
    assert data["total_seconds"] == pytest.approx(sum(seconds))
    assert data["total_seconds"] > 0
    assert data["startup_seconds"] >= 0
    assert data["source_loc"] > 0
    assert data["ast_nodes"] > 0
    assert data["loc_per_second"] > 0
    assert data["ast_nodes_per_second"] > 0


def test_json_mode_is_a_single_line(tmp_path):
    run, _ = _transpile(tmp_path, "json")
    report_lines = [ln for ln in run.stderr.splitlines() if ln.startswith(REPORT_MARKER)]
    assert len(report_lines) == 1


def test_mode_off_emits_no_report(tmp_path):
    run, out = _transpile(tmp_path, None)
    assert run.returncode == 0, run.stderr
    assert out.exists()
    assert REPORT_MARKER not in run.stderr
