"""MLIR elementwise loop vectorization (#113)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from flow.parser import parse_flow_code
from flow.mlir_generator import MLIRGenerator


SAXPY = """
function saxpy(a: f32, x: memref_f32, y: memref_f32, out: memref_f32, n: i32) -> i32 {
    for i in 0 to n {
        out[i] = a * x[i] + y[i]
    }
    return 0
}

function main() -> i32 {
    return 0
}
"""

SCALAR_ACC = """
function sum(x: memref_f32, n: i32) -> f32 {
    let mut acc: f32 = 0.0
    for i in 0 to n {
        acc = acc + x[i]
    }
    return acc
}

function main() -> i32 {
    return 0
}
"""


def _gen(src: str) -> str:
    return MLIRGenerator().generate_module(parse_flow_code(src))


def test_saxpy_emits_vector_transfer():
    mlir = _gen(SAXPY)
    assert "vector.transfer_read" in mlir
    assert "vector.transfer_write" in mlir
    assert "vector<4xf32>" in mlir
    assert "flow: vectorized elementwise f32 loop" in mlir


def test_reduction_not_vectorized():
    """Loop-carried accumulators must stay scalar."""
    mlir = _gen(SCALAR_ACC)
    assert "vector.transfer_write" not in mlir


IAXPY = """
function iaxpy(a: i32, x: memref_i32, y: memref_i32, out: memref_i32, n: i32) -> i32 {
    for i in 0 to n {
        out[i] = a * x[i] + y[i]
    }
    return 0
}

function main() -> i32 {
    return 0
}
"""


def test_iaxpy_emits_i32_vector_transfer():
    mlir = _gen(IAXPY)
    assert "vector.transfer_read" in mlir
    assert "vector<4xi32>" in mlir
    assert "arith.muli" in mlir or "arith.addi" in mlir


RBF_GAUSSIAN = """
function rbf_gaussian(gamma: f32, x: memref_f32, y: memref_f32, out: memref_f32, n: i32) -> i32 {
    for i in 0 to n {
        out[i] = exp(-gamma * (x[i] - y[i]) * (x[i] - y[i]))
    }
    return 0
}

function main() -> i32 {
    return 0
}
"""


def test_rbf_gaussian_emits_vector_math_exp():
    """Verify Gaussian RBF kernel lowers to vectorized math.exp in MLIR."""
    mlir = _gen(RBF_GAUSSIAN)
    assert "vector.transfer_read" in mlir
    assert "vector.transfer_write" in mlir
    assert "vector<4xf32>" in mlir
    assert "math.exp" in mlir


TRANSCENDENTAL = """
function trans_kernel(x: memref_f32, y: memref_f32, out: memref_f32, n: i32) -> i32 {
    for i in 0 to n {
        out[i] = sin(x[i]) + sqrt(abs(y[i]))
    }
    return 0
}

function main() -> i32 {
    return 0
}
"""


def test_transcendental_math_vectorized():
    """Verify elementwise loops with sin/sqrt/abs lower to MLIR vector math ops."""
    mlir = _gen(TRANSCENDENTAL)
    assert "vector.transfer_read" in mlir
    assert "vector.transfer_write" in mlir
    assert "vector<4xf32>" in mlir
    assert "math.sin" in mlir
    assert "math.sqrt" in mlir
    assert "math.absf" in mlir
