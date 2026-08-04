# Autodiff

FLOW currently supports **automatic differentiation as library code**, not as a compiler pass.

## What exists today

- **Forward mode (dual numbers)**: `lib/stdlib/autodiff.flow`
  - Best when you have **few parameters**
  - Dual is `{ val: f32, grad: f32 }` — constructors `dual_var` / `dual_const`, accessors `dual_val` / `dual_grad`
  - Demos: `examples/neural_networks/autodiff_clean_syntax.flow`, `autodiff_benchmark.flow`
  - NN training (slow but simple): `examples/neural_networks/neural_network.flow`

- **Reverse-mode helpers (local gradients)**: `lib/stdlib/autodiff_reverse.flow`
  - Best when you have **many parameters**
  - Primitives like `op_sigmoid` returning value + local derivative.
  - Demo: `examples/neural_networks/neural_network_backprop.flow`

- **Live reverse tape (`Tape` + `ArrayTape`)**: `lib/stdlib/autodiff.flow` + `lib/runtime/tape.flow`
  - Fixed-size mul/add tape with `track` / `mul` / `add` / `backward` / `get_grad`
  - Demo: `examples/ml/tape_mul.flow` (`handle Tape with ArrayTape { … }`)
  - Still not a compiler AD pass — you record ops explicitly

## Gradient Codegen Tools

Two prototype tools can **auto-generate gradient code** from a scalar loss function:

### 1. C code generator (`tools/grad/flow_grad_c.py`)

Generates C code that computes value + gradients using a reverse-mode tape:

```bash
# Point at a Flow file that defines a scalar loss `f`
PYTHONPATH=src python3 tools/grad/flow_grad_c.py path/to/loss.flow f > build/grad_demo.c
clang -O2 build/grad_demo.c -lm -o build/grad_demo
./build/grad_demo 1.0 2.0
```

Supports: `sin`, `cos`, `exp`, `log`, `sqrt`, `sigmoid`, `let` bindings.
Tools live under `tools/grad/`.

### 2. FLOW code generator (`tools/grad/flow_grad_flow.py`)

Generates **FLOW code** with a gradient struct and function:

```bash
PYTHONPATH=src python3 tools/grad/flow_grad_flow.py lib/stdlib/nn_xor_loss_clean.flow xor_loss_clean > lib/stdlib/nn_xor_loss_clean_grad.flow
```

Supports:
- All the above primitives
- **Multi-arg function calls** (inlined automatically)

Related stdlib pieces (when present):
- Input loss: `lib/stdlib/nn_xor_loss_clean.flow`
- Generated grads: `lib/stdlib/nn_xor_loss_clean_grad.flow`
- Wrapper: `lib/stdlib/nn_autogen.flow`
- End-to-end MLP demo: `examples/ml/models/mlp_xor.flow`

## NN stdlib (`lib/stdlib/nn.flow`)

Provides fixed-shape MLP structs with manual backprop:

- **Net2x2x1**: 2 inputs → 2 hidden → 1 output
- **Net2x4x1**: 2 inputs → 4 hidden → 1 output
- **Net2x8x1**: 2 inputs → 8 hidden → 1 output

Each includes: `_predict`, `_loss_xor`, `_grads_xor`, `_step`, and gradient checking (`net2x2x1_gradcheck_xor`).

Examples:
- `examples/neural_networks/nn_xor.flow` (2x2x1)
- `examples/neural_networks/nn_gradcheck.flow` (numerical gradient verification)
- `examples/ml/models/mlp_xor.flow` (MLP training)

## GPU gradient kernels (manual, not compiler AD)

Elementwise backward kernels for device training live in
`lib/stdlib/gpu_gradients.flow`:

| Kernel | Forward meaning | Gradient |
|--------|-----------------|----------|
| `gpu_mse_grad` | mean squared error | `2*(pred-target)/n` |
| `gpu_relu_grad` | ReLU | `dout` if `x>0` else `0` |
| `gpu_sigmoid_grad` | sigmoid (given `y`) | `dout * y * (1-y)` |
| `gpu_scale_grad` | `alpha * x` | `alpha * dout` |

```bash
./flow gpu lib/stdlib/gpu_gradients.flow   # emit Metal
./flow run lib/stdlib/gpu_gradients.flow   # CPU ref self-check
```

This is **not** automatic differentiation on the GPU — it is a set of hand-written
gradient primitives that pair with `@gpu` forward kernels in `gpu_kernels.flow`.
Full GPU autodiff (tape / dual numbers on device) remains future work.

## Why reverse-mode isn't a full tape yet

A true tape-based reverse-mode needs:
- ergonomic array/struct mutation for tape storage
- a real semantic/type pass (so we can transform code safely)

See `docs/STRUCTURAL_GAPS.md` for the "IR + typechecker" path that unlocks this.
