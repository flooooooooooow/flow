# 14. Numerics, automatic differentiation, and machine learning

Flow provides ordinary numeric operators, specialised library modules, generated derivatives, and optional accelerated backends. Every `flow` block in this chapter is compiler-checked in CI.

## 14.1 Numeric building blocks

The core supports integer, floating-point, and complex arithmetic. Library modules cover linear algebra, ODEs, optimization, statistics, tensors, neural-network layers, DSP, RF, circuit analysis, audio, checked arithmetic, and big integers. The generated [stdlib API](../library/stdlib-api.md) is the catalog.

## 14.2 Tolerances

A portable scalar tolerance helper can be written without relying on an overloaded absolute-value builtin:

```flow
function absolute(x: f64) -> f64 {
    if x < 0.0 { return -x }
    return x
}

function near(a: f64, b: f64, tolerance: f64) -> bool {
    return absolute(a - b) <= tolerance
}
```

Across many magnitudes, combine absolute and relative criteria. NaN, infinity, cancellation, overflow, underflow, and conditioning need separate consideration.

## 14.3 Centred numerical gradient

```flow
function objective(x: f64) -> f64 {
    return x * x * x + 2.0 * x
}

function analytic_gradient(x: f64) -> f64 {
    return 3.0 * x * x + 2.0
}

function centred_gradient(x: f64, h: f64) -> f64 {
    return (objective(x + h) - objective(x - h)) / (2.0 * h)
}

function gradient_check() -> i32 {
    let estimate: f64 = centred_gradient(3.0, 0.0001)
    let reference: f64 = analytic_gradient(3.0)
    let error: f64 = estimate - reference
    if error < -0.000001 or error > 0.000001 {
        return 1
    }
    return 0
}
```

The checked-in complete program is [`examples/book/14_numeric_gradient.flow`](../../examples/book/14_numeric_gradient.flow). Very small finite-difference steps eventually lose accuracy to floating-point cancellation.

## 14.4 SIMD vectors

`vec<T, N>` and vector literals are still a partial surface across backends. They are not presented here as portable runnable Flow. Use fixed arrays/loops for the portable baseline, then target SIMD or MLIR vector operations after measuring the platform.

## 14.5 Linear algebra

Complete executable examples cover matrix construction, indexing, multiplication, decomposition, and BLAS integration:

```bash
FLOW_HOST=python ./flow run examples/linalg/matrix_ops.flow
FLOW_HOST=python ./flow run examples/linalg/lu_decomposition.flow
FLOW_HOST=python ./flow run examples/linalg/blas_demo.flow
```

BLAS bindings additionally depend on a platform BLAS implementation.

## 14.6 Forward automatic differentiation

Forward AD is provided by `stdlib/autodiff.flow`. Because the `Dual` type and operations come from that module, use the complete imported examples rather than copying calls without their declaration context:

```bash
FLOW_HOST=python ./flow run examples/ml/autodiff/dual_ops.flow
FLOW_HOST=python ./flow run examples/ml/autodiff/autodiff_benchmark.flow
```

A dual value carries a primal value plus a directional derivative. Forward mode is efficient when the number of input directions is small.

## 14.7 Reverse mode

`stdlib/autodiff_reverse.flow` records operations on a tape and propagates adjoints from outputs to inputs:

```bash
FLOW_HOST=python ./flow run examples/ml/tape_mul.flow
```

Gradient implementations should be checked against finite differences or an independent analytic result.

## 14.8 Generated gradients

Some workloads generate derivative functions ahead of time rather than interpreting a runtime tape. Treat generated derivatives like generated C: reproducible, inspectable at boundaries, and tested against the primal calculation.

```bash
FLOW_HOST=python ./flow run examples/ml/models/mlp_xor.flow
```

## 14.9 Tensors and MLIR

Tensor modules provide shaped numeric storage and elementwise operations. MLIR can lower selected tensor and matrix workloads, but backend parity is not claimed for every language feature.

```bash
FLOW_HOST=python ./flow run examples/ml/autodiff/tensor_ops.flow
./flow ml bench examples/ml/mlir_tensor_bench.flow
```

## 14.10 Neural networks and optimization

```bash
FLOW_HOST=python ./flow run examples/ml/models/mlp_xor_from_scratch.flow
FLOW_HOST=python ./flow run examples/ml/models/mlp_xor_adam.flow
FLOW_HOST=python ./flow run examples/ml/digits_mlp.flow
```

Validation belongs in the example: objective reduction, held-out accuracy, gradient checks, residuals, or comparison with a known solution.

## 14.11 Numerical and statistical examples

```bash
FLOW_HOST=python ./flow run examples/numerical/ode_solver.flow
FLOW_HOST=python ./flow run examples/numerical/optimization.flow
FLOW_HOST=python ./flow run examples/numerical/fmm_selftest.flow
FLOW_HOST=python ./flow run examples/stats/regression_gd.flow
```

## Exercises

Compare a dual derivative with a centred finite difference, measure an LU residual, construct a case where relative tolerance matters, and train the XOR model while recording its objective and classification result.

Next: [Graphics, shaders, GPU, UI, and audio](15-media-gpu-and-audio.md).
