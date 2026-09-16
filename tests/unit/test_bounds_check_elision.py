"""Bounds-check elision for `for i in 0 to span.len { span[i] }` (issue #615).

A loop whose bound is the span's own length keeps the index in range for the
whole body, so the per-access bounds check is dead and gets dropped. The check
stays wherever the range fact does not hold: a different span, a non-zero
start, a rebound span, or an arbitrary index.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from flow.parser import parse_flow_code
from flow.c_generator import flow_to_c


def _accesses(source: str):
    c = flow_to_c(parse_flow_code(source))
    return [line.strip() for line in c.splitlines() if ".data[" in line]


def _is_elided(line: str) -> bool:
    return "out of bounds" not in line


def test_loop_bound_span_access_is_elided():
    lines = _accesses(
        """
        function sum(a: span<f64>) -> f64 {
            let mut acc: f64 = 0.0
            for i in 0 to a.len as i32 {
                acc = acc + a[i]
            }
            return acc
        }
        """
    )
    assert lines and all(_is_elided(l) for l in lines), lines


def test_loop_bound_without_cast_is_elided():
    lines = _accesses(
        """
        function sum(a: span<f64>) -> f64 {
            let mut acc: f64 = 0.0
            for i in 0 to a.len {
                acc = acc + a[i]
            }
            return acc
        }
        """
    )
    assert lines and all(_is_elided(l) for l in lines), lines


def test_element_write_is_elided():
    lines = _accesses(
        """
        function fill(a: span<f64>) {
            for i in 0 to a.len as i32 {
                a[i] = 1.0
            }
        }
        """
    )
    assert lines and all(_is_elided(l) for l in lines), lines


def test_different_span_keeps_check():
    # `a` bounds the loop and is elided; `b` is a separate span the compiler
    # cannot prove long enough, so its check stays. Keep the two accesses on
    # separate statements so each line carries exactly one.
    lines = _accesses(
        """
        function dot(a: span<f64>, b: span<f64>) -> f64 {
            let mut acc: f64 = 0.0
            for i in 0 to a.len as i32 {
                let x: f64 = a[i]
                let y: f64 = b[i]
                acc = acc + x * y
            }
            return acc
        }
        """
    )
    a_access = [l for l in lines if "(a).data[i]" in l]
    b_access = [l for l in lines if "(b).data[i]" in l]
    assert a_access and all(_is_elided(l) for l in a_access), a_access
    assert b_access and all(not _is_elided(l) for l in b_access), b_access


def test_nonzero_start_keeps_check():
    lines = _accesses(
        """
        function sum(a: span<f64>) -> f64 {
            let mut acc: f64 = 0.0
            for i in 1 to a.len as i32 {
                acc = acc + a[i]
            }
            return acc
        }
        """
    )
    assert lines and all(not _is_elided(l) for l in lines), lines


def test_rebound_span_keeps_check():
    lines = _accesses(
        """
        function sum(a: span<f64>, other: span<f64>) -> f64 {
            let mut acc: f64 = 0.0
            let mut v: span<f64> = a
            for i in 0 to v.len as i32 {
                v = other
                acc = acc + v[i]
            }
            return acc
        }
        """
    )
    assert lines and all(not _is_elided(l) for l in lines), lines


def test_rebound_span_inside_branch_keeps_check():
    lines = _accesses(
        """
        function sum(a: span<f64>, other: span<f64>, flag: bool) -> f64 {
            let mut acc: f64 = 0.0
            let mut v: span<f64> = a
            for i in 0 to v.len as i32 {
                if flag { v = other }
                acc = acc + v[i]
            }
            return acc
        }
        """
    )
    assert lines and all(not _is_elided(l) for l in lines), lines


def test_arbitrary_index_keeps_check():
    lines = _accesses(
        """
        function at(a: span<f64>, j: i32) -> f64 {
            return a[j]
        }
        """
    )
    assert lines and all(not _is_elided(l) for l in lines), lines


def test_nested_loop_reusing_index_keeps_outer_check():
    # The inner loop rebinds `i` to `b.len`, so `a[i]` inside it can exceed
    # `a.len` and must stay checked.
    lines = _accesses(
        """
        function f(a: span<f64>, b: span<f64>) -> f64 {
            let mut acc: f64 = 0.0
            for i in 0 to a.len as i32 {
                for i in 0 to b.len as i32 {
                    acc = acc + a[i]
                }
            }
            return acc
        }
        """
    )
    assert lines and all(not _is_elided(l) for l in lines), lines
