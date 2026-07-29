# Autodiff

FLOW currently supports **automatic differentiation as library code**, not as a compiler pass.

## What exists today

- **Forward mode (dual numbers)**: `lib/stdlib/autodiff.flow`
  - Best when you have **few parameters**
  - Demo: `examples/autodiff_demo.flow`
  - NN training (slow but simple): `examples/neural_network.flow`

- **Reverse-mode helpers (local gradients)**: `lib/stdlib/autodiff_reverse.flow`
  - Best when you have **many parameters**
  - This is not a tape engine yet; it provides primitives like `op_sigmoid` returning value + local derivative.
  - Demo: `examples/neural_network_backprop.flow`

## Gradient Codegen Tools

Two prototype tools can **auto-generate gradient code** from a scalar loss function:

### 1. C code generator (`tools/grad/flow_grad_c.py`)

Generates C code that computes value + gradients using a reverse-mode tape:

```bash
PYTHONPATH=src python3 tools/grad/flow_grad_c.py examples/grad_tool_demo.flow f > build/grad_demo.c
clang -O2 build/grad_demo.c -lm -o build/grad_demo
./build/grad_demo 1.0 2.0
```

Supports: `sin`, `cos`, `exp`, `log`, `sqrt`, `sigmoid`, `let` bindings.

### 2. FLOW code generator (`tools/grad/flow_grad_flow.py`)

Generates **FLOW code** with a gradient struct and function:

```bash
PYTHONPATH=src python3 tools/grad/flow_grad_flow.py lib/stdlib/nn_xor_loss_clean.flow xor_loss_clean > lib/stdlib/nn_xor_loss_clean_grad.flow
```

Supports:
- All the above primitives
- **Multi-arg function calls** (inlined automatically)

The generated code can be imported and used for NN training:
- Input loss: `lib/stdlib/nn_xor_loss_clean.flow`
- Generated grads: `lib/stdlib/nn_xor_loss_clean_grad.flow`
- Wrapper: `lib/stdlib/nn_autogen.flow`
- Training demo: `examples/nn_xor_autogen.flow`

## NN stdlib (`lib/stdlib/nn.flow`)

Provides fixed-shape MLP structs with manual backprop:

- **Net2x2x1**: 2 inputs → 2 hidden → 1 output
- **Net2x4x1**: 2 inputs → 4 hidden → 1 output
- **Net2x8x1**: 2 inputs → 8 hidden → 1 output

Each includes: `_predict`, `_loss_xor`, `_grads_xor`, `_step`, and gradient checking (`net2x2x1_gradcheck_xor`).

Examples:
- `examples/nn_xor.flow` (2x2x1)
- `examples/nn_xor_2x4.flow` (2x4x1)
- `examples/nn_xor_2x8.flow` (2x8x1)
- `examples/nn_gradcheck.flow` (numerical gradient verification)

## Why reverse-mode isn't a full tape yet

A true tape-based reverse-mode needs:
- ergonomic array/struct mutation for tape storage
- a real semantic/type pass (so we can transform code safely)

See `docs/STRUCTURAL_GAPS.md` for the "IR + typechecker" path that unlocks this.
