# 14. Numerics, automatic differentiation, and machine learning

Flow provides ordinary numeric operators, specialised library modules,
generated derivatives, and optional accelerated backends. Check numerical
results with tolerances and reference calculations. Exact floating-point
equality is rarely the right test.

## 14.1 Numeric building blocks

The core provides integer, floating-point, and complex arithmetic. The math
library supplies trigonometric, exponential, logarithmic, rounding, and related
functions. Additional modules cover:

- vectors and matrices;
- BLAS/LAPACK bindings;
- ODE and state-space operations;
- optimisation and statistics;
- tensors and neural-network layers;
- fast multipole methods;
- DSP, RF, circuit, and audio numerics;
- checked, saturating, wrapping, and big-integer helpers.

The generated [standard-library API](../library/stdlib-api.md) is the function
catalog; the book describes the families and their contracts.

## 14.2 Tolerances

```flow
function near(a: f64, b: f64, tolerance: f64) -> bool {
    return abs(a - b) <= tolerance
}
```

An absolute tolerance is suitable near a known scale. Across many orders of
magnitude, combine absolute and relative criteria:

```text
|a - b| <= absolute + relative * max(|a|, |b|)
```

NaN, infinity, cancellation, overflow, underflow, and conditioning must be
considered independently of syntax.

## 14.3 Worked check: a centred numerical gradient

For a scalar function, a centred finite difference estimates the derivative:

```text
f'(x) ~= (f(x + h) - f(x - h)) / (2h)
```

The following program compares that estimate with an analytic derivative.

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
```

At `x = 3`, the analytic derivative is `29`.

```flow
let estimate: f64 = centred_gradient(3.0, 0.0001)
let reference: f64 = analytic_gradient(3.0)
let error: f64 = estimate - reference

if error < -0.000001 or error > 0.000001 {
    return 1
}
```

Source:
[`examples/book/14_numeric_gradient.flow`](../../examples/book/14_numeric_gradient.flow)

```bash
./flow run examples/book/14_numeric_gradient.flow
```

```text
estimate: 29.000000 reference: 29.000000 error: 0.000000010
```

Making `h` smaller does not improve the estimate forever. Very small steps
lose precision when the two nearby function values are subtracted. A gradient
check should therefore try several step sizes.

## 14.4 SIMD vectors

```flow
let a: vec<f32, 4> = <1.0, 2.0, 3.0, 4.0>
let b: vec<f32, 4> = <4.0, 3.0, 2.0, 1.0>
let c: vec<f32, 4> = a + b
```

Vector syntax parses, but code generation and target coverage are partial.
Portable code can use fixed arrays and a loop; target-specific performance can
use `@target`, generated MLIR vector operations, library SIMD helpers, or GPU
kernels after measuring the chosen platform.

## 14.5 Linear algebra

The pure Flow matrix examples demonstrate construction, indexing,
multiplication, and decomposition:

```bash
./flow run examples/linalg/matrix_ops.flow
./flow run examples/linalg/lu_decomposition.flow
./flow run examples/linalg/blas_demo.flow
```

BLAS bindings require a platform BLAS implementation such as Accelerate or
OpenBLAS. A matrix layout, leading dimension, transpose convention, and
ownership policy belong to the API contract; they cannot be inferred from the
word “matrix”.

## 14.6 Forward automatic differentiation

A dual value carries a primal value and one directional derivative:

```flow
import "stdlib/autodiff.flow"

let x: Dual = dual(3.0, 1.0)
let y: Dual = dual_mul(x, x)

printf("value=%f derivative=%f\n", y.val, y.grad)
```

For `y = x^2` at `x = 3`, the pair is `(9, 6)`. Forward mode is efficient when
the number of independent input directions is small.

Operations include addition, multiplication, division, powers, trigonometric
functions, exponentials, and common activations.

```bash
FLOW_HOST=python ./flow run examples/ml/autodiff/dual_ops.flow
FLOW_HOST=python ./flow run examples/ml/autodiff/autodiff_benchmark.flow
```

## 14.7 Reverse mode

`stdlib/autodiff_reverse.flow` records operations on a tape and propagates
adjoints from outputs back to inputs. Reverse mode is efficient when many
parameters contribute to a small number of scalar objectives.

```bash
FLOW_HOST=python ./flow run examples/ml/tape_mul.flow
```

Tape capacity, supported operations, mutation, and memory reuse limit the
implementation. Check a gradient against finite differences or an independent
expression before trusting it.

## 14.8 Generated gradients

Some examples generate derivative functions instead of using a runtime tape.
The objective remains ordinary Flow, and a generation step writes its gradient
function. Native tools can optimise that function without interpreting a tape
during the calculation.

```bash
./flow run examples/ml/models/mlp_xor.flow
```

Generated code should be treated like generated C: reproducible, inspected at
boundaries, and tested against the primal function.

## 14.9 Tensors

Tensor modules provide shaped numeric storage and elementwise operations.
The C backend implements tensor arithmetic through library operations and
selected overloads. MLIR can lower tensors and matrices, but not every core
language feature has backend parity.

```bash
FLOW_HOST=python ./flow run examples/ml/autodiff/tensor_ops.flow
./flow ml bench examples/ml/mlir_tensor_bench.flow
```

The `flow ml` command family supplies `run`, `jit`, `bench`, and `test` modes
for MLIR-first workloads.

## 14.10 Neural networks and optimisation

The repository contains both pedagogical and reusable layers:

```bash
./flow run examples/ml/models/mlp_xor_from_scratch.flow
./flow run examples/ml/models/mlp_xor_adam.flow
FLOW_HOST=python ./flow run examples/ml/digits_mlp.flow
```

The digits example constructs a ten-class classifier, performs minibatch SGD
with momentum, and enforces an accuracy gate. A parallel variant accumulates
gradient shards with native threads. The Metal variant measures supported GPU
operations and reports crossover rather than assuming acceleration.

## 14.11 Numerical and statistical examples

```bash
./flow run examples/numerical/ode_solver.flow
./flow run examples/numerical/optimization.flow
./flow run examples/numerical/fmm_selftest.flow
./flow run examples/stats/regression_gd.flow
```

Each algorithm requires its own validation quantity: residual, objective,
convergence rate, conditioning estimate, held-out error, or comparison with a
known solution.

## Exercises

1. Compare a dual-number derivative with a centred finite difference.
2. Measure the residual of an LU solve.
3. Demonstrate a case where absolute tolerance alone is inadequate.
4. Train the XOR model and record the objective and final classification.

Next: [Graphics, shaders, GPU, UI, and audio](15-media-gpu-and-audio.md).
