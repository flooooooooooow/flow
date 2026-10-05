import pytest
from tests.unit.compiler_helpers import to_c

def test_vectorization_saxpy():
    """Verify that a standard SAXPY kernel triggers loop vectorization."""
    code = """
    function saxpy(a: f32, x: memref_f32, y: memref_f32, out: memref_f32, n: i32) -> i32 {
        for i in 0 to n step 1 {
            out[i] = a * x[i] + y[i]
        }
        return 0
    }
    """
    c_code = to_c(code)
    assert "#pragma clang loop vectorize(enable) interleave(enable)" in c_code
    assert "#pragma GCC ivdep" in c_code

def test_vectorization_dot_product():
    """Verify that a dot product kernel triggers loop vectorization."""
    code = """
    function dot(x: memref_f32, y: memref_f32, n: i32) -> f32 {
        let mut sum: f32 = 0.0
        for i in 0 to n step 1 {
            sum = sum + x[i] * y[i]
        }
        return sum
    }
    """
    c_code = to_c(code)
    assert "#pragma clang loop vectorize(enable) interleave(enable)" in c_code
    assert "#pragma GCC ivdep" in c_code

def test_vectorization_elementwise_add():
    """Verify that an elementwise addition kernel triggers loop vectorization."""
    code = """
    function add(x: memref_f32, y: memref_f32, out: memref_f32, n: i32) -> i32 {
        for i in 0 to n step 1 {
            out[i] = x[i] + y[i]
        }
        return 0
    }
    """
    c_code = to_c(code)
    assert "#pragma clang loop vectorize(enable) interleave(enable)" in c_code
    assert "#pragma GCC ivdep" in c_code

def test_vectorization_regression_scalar():
    """Verify that a non-trivially vectorizable loop does not emit vectorization hints."""
    code = """
    function scalar_loop(x: memref_f32, n: i32) -> i32 {
        for i in 0 to n step 1 {
            if x[i] > 0.0 {
                x[i] = 0.0
            }
        }
        return 0
    }
    """
    c_code = to_c(code)
    assert "#pragma clang loop vectorize(enable)" not in c_code

def test_vectorization_no_step_is_scalar():
    """Verify that a loop without an explicit step does not emit vectorization hints."""
    code = """
    function no_step_loop(a: f32, x: memref_f32, y: memref_f32, out: memref_f32, n: i32) -> i32 {
        for i in 0 to n {
            out[i] = a * x[i] + y[i]
        }
        return 0
    }
    """
    c_code = to_c(code)
    assert "#pragma clang loop vectorize(enable)" not in c_code

def test_vectorization_regression_function_call():
    """Verify that a loop with a function call does not emit vectorization hints."""
    code = """
    function compute(val: f32) -> f32 { return val * 2.0 }
    function map_func(x: memref_f32, n: i32) -> i32 {
        for i in 0 to n step 1 {
            x[i] = compute(x[i])
        }
        return 0
    }
    """
    c_code = to_c(code)
    assert "#pragma clang loop vectorize(enable)" not in c_code

def test_vectorization_regression_complex_control_flow():
    """Verify that a loop with break/continue does not emit vectorization hints."""
    code = """
    function check_values(x: memref_f32, n: i32) -> i32 {
        for i in 0 to n step 1 {
            if x[i] < 0.0 {
                break
            }
        }
        return 0
    }
    """
    c_code = to_c(code)
    assert "#pragma clang loop vectorize(enable)" not in c_code
