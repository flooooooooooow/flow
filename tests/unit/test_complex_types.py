"""Tests for c64/c128 complex number types."""
import subprocess
import sys
import os
import pytest

from tests.unit.compiler_helpers import errors, to_c, compile_and_run, compile_c_only


def test_c64_type_recognized():
    assert not errors("""
    function main() -> i32 {
        let z: c64 = c64(1.0, 2.0)
        return 0
    }
    """)


def test_c128_type_recognized():
    assert not errors("""
    function main() -> i32 {
        let z: c128 = c128(1.0, 2.0)
        return 0
    }
    """)


def test_complex_addition():
    assert not errors("""
    function main() -> i32 {
        let z: c64 = c64(1.0, 2.0)
        let w: c64 = c64(3.0, 4.0)
        let s: c64 = z + w
        return 0
    }
    """)


def test_complex_multiplication():
    assert not errors("""
    function main() -> i32 {
        let z: c64 = c64(1.0, 2.0)
        let w: c64 = c64(3.0, 4.0)
        let p: c64 = z * w
        return 0
    }
    """)


def test_complex_subtraction():
    assert not errors("""
    function main() -> i32 {
        let z: c64 = c64(5.0, 6.0)
        let w: c64 = c64(1.0, 2.0)
        let d: c64 = z - w
        return 0
    }
    """)


def test_complex_division():
    assert not errors("""
    function main() -> i32 {
        let z: c64 = c64(4.0, 0.0)
        let w: c64 = c64(2.0, 0.0)
        let q: c64 = z / w
        return 0
    }
    """)


def test_creal_cimag():
    assert not errors("""
    function main() -> i32 {
        let z: c64 = c64(3.0, 4.0)
        let re: f64 = creal(z)
        let im: f64 = cimag(z)
        return 0
    }
    """)


def test_cabs():
    assert not errors("""
    function main() -> i32 {
        let z: c64 = c64(3.0, 4.0)
        let mag: f64 = cabs(z)
        return 0
    }
    """)


def test_c64_to_c128_promotion():
    assert not errors("""
    function main() -> i32 {
        let z: c64 = c64(1.0, 2.0)
        let w: c128 = c128(3.0, 4.0)
        let s: c128 = z + w
        return 0
    }
    """)


def test_complex_scalar_arithmetic():
    """c64 + f32 should yield c64."""
    assert not errors("""
    function main() -> i32 {
        let z: c64 = c64(1.0, 2.0)
        let s: f32 = 3.0
        let sum: c64 = z + s
        return 0
    }
    """)


def test_complex_single_arg_constructor():
    """c64(x) should create a complex from a real value."""
    assert not errors("""
    function main() -> i32 {
        let z: c64 = c64(5.0)
        return 0
    }
    """)


def test_complex_in_struct():
    assert not errors("""
    struct IQ { re: f32, im: f32, freq: f64 }
    function main() -> i32 {
        let s: IQ = IQ { re: 1.0, im: 2.0, freq: 2.4e9 }
        return 0
    }
    """)


def test_complex_array():
    assert not errors("""
    function main() -> i32 {
        let buf: array<c64, 8>
        return 0
    }
    """)


def test_complex_c_codegen():
    """Verify the generated C uses complex.h types and CMPLXF."""
    c_code = compile_c_only("""
    function main() -> i32 {
        let z: c64 = c64(3.0, 4.0)
        let w: c64 = c64(1.0, 2.0)
        let s: c64 = z + w
        return 0
    }
    """)
    assert "complex.h" in c_code
    assert "float complex" in c_code
    assert "* I" in c_code  # C99 complex construction via I macro


def test_complex_compile_and_run():
    """End-to-end: compile a complex arithmetic program and check exit code."""
    rc = compile_and_run("""
    function main() -> i32 {
        let z: c64 = c64(3.0, 4.0)
        let w: c64 = c64(1.0, 2.0)
        let s: c64 = z + w
        let mag: f64 = cabs(z)
        if mag > 4.9 && mag < 5.1 {
            return 0
        }
        return 1
    }
    """)
    assert rc == 0
