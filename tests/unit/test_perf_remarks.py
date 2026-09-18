"""Compiler performance remarks (#744).

Opt-in performance-report mode surfaces optimization facts the C generator
already computes. It is off by default and emits nothing then. When on, each
remark names the source construct and marks the decision as a proven fact or a
heuristic.

Three remark types are wired to real codegen decision points:

- span-bounds-check-retained: an index into a span keeps its runtime bounds
  check because the index is not proven in range (_gen_array_access).
- loop-not-vectorized: a for loop with an explicit step stays scalar because
  its body has a function call or control flow (_gen_for / _loop_body_is_simple).
- f32-math-widened-to-f64: a libm call on an f32 argument lowers to the bare
  double-precision name, so the argument widens (call-site lowering).
"""

from __future__ import annotations

from flow.parser import parse_flow_code
from flow.c_generator import flow_to_c


def _remarks(source: str) -> list[str]:
    flow_to_c(parse_flow_code(source), perf_report=True)
    return list(flow_to_c.last_perf_remarks)


# --- span bounds check -------------------------------------------------------

SPAN_INDEX = "function reads(v: span<i32>) -> i32 { return v[0] }"


def test_span_index_keeps_a_bounds_check_remark():
    remarks = _remarks(SPAN_INDEX)
    assert any(r.startswith("perf[span-bounds-check-retained]") for r in remarks)
    hit = next(r for r in remarks if "span-bounds-check-retained" in r)
    assert "`v`" in hit
    assert "not proven in range" in hit
    assert "(fact)" in hit


def test_bounds_check_remark_is_absent_without_an_index():
    # No indexing, so nothing to report.
    remarks = _remarks("function main() -> i32 { return 0 }")
    assert not any("span-bounds-check-retained" in r for r in remarks)


# --- scalarized loop ---------------------------------------------------------

SCALAR_LOOP = """
function work(x: i32) -> i32 { return x }
function main() -> i32 {
  let acc: i32 = 0
  for i in 0..10 step 1 {
    acc = work(i)
  }
  return acc
}
"""


def test_loop_with_a_call_reports_not_vectorized():
    remarks = _remarks(SCALAR_LOOP)
    hit = next(
        (r for r in remarks if "loop-not-vectorized" in r), None
    )
    assert hit is not None
    assert "`i`" in hit
    assert "scalar" in hit


# --- f32 math widening -------------------------------------------------------

F32_SQRT = """
function main() -> f32 {
  let x: f32 = 2.0
  return sqrt(x)
}
"""


def test_f32_libm_call_reports_widening():
    remarks = _remarks(F32_SQRT)
    hit = next(
        (r for r in remarks if "f32-math-widened-to-f64" in r), None
    )
    assert hit is not None
    assert "`sqrt`" in hit
    assert "widened to f64" in hit


def test_f64_libm_call_does_not_report_widening():
    # f64 argument: no widening, no remark.
    source = """
function main() -> f64 {
  let x: f64 = 2.0
  return sqrt(x)
}
"""
    remarks = _remarks(source)
    assert not any("f32-math-widened-to-f64" in r for r in remarks)


# --- off by default ----------------------------------------------------------

def test_mode_is_off_by_default():
    out = flow_to_c(parse_flow_code(SPAN_INDEX))
    assert flow_to_c.last_perf_remarks == []
    assert "performance remarks" not in out


def test_remarks_become_c_comments_when_enabled():
    out = flow_to_c(parse_flow_code(SPAN_INDEX), perf_report=True)
    assert "Flow performance remarks (#744)" in out
    assert "span-bounds-check-retained" in out
