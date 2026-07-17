# Flow Examples

Comprehensive examples demonstrating Flow's capabilities across multiple domains.

## Directory Structure

```
examples/
├── basics/           # Fundamental algorithms and syntax
├── audio/            # Real-time audio DSP
├── compilers/        # Language implementation demos
├── crypto/           # Cryptographic algorithms
├── data/             # Data processing
├── effects/          # Flow's unique effect system
├── games/            # Interactive games with graphics
├── generics_traits/  # Generic programming and traits
├── gpu/              # GPU/Metal computation
├── graphics/         # Rendering and shaders
├── linalg/           # Linear algebra
├── ml/               # Machine learning framework
├── neural_networks/  # Autodiff and neural networks
├── numerical/        # Scientific computing
└── systems/          # Systems programming primitives
```

## Quick Start

```bash
# Run any example
./flow run examples/basics/hello_world.flow

# Run with graphics (macOS)
./flow compile examples/games/tetris_gfx.flow
clang -O2 build/tetris_gfx.c runtime/gfx_macos.m \
    -framework Cocoa -framework CoreGraphics -framework QuartzCore \
    -o build/tetris_gfx
./build/tetris_gfx
```

## Categories

### Basics (`basics/`)
Fundamental algorithms demonstrating Flow syntax:
- `hello_world.flow` - First program
- `fibonacci.flow` - Recursive functions
- `bubble_sort.flow` - Array manipulation
- `prime_numbers.flow` - Loops and conditionals

### Games (`games/`)
Interactive demonstrations with graphics:
- `tetris_gfx.flow` - Complete Tetris with native graphics
- `2048_gfx.flow` - 2048 puzzle game
- `2048.flow` - Terminal-based 2048

### Machine Learning (`ml/`)
Neural network framework:
- `tensor.flow` - N-dimensional tensor type
- `nn_layers.flow` - Dense layers, activations
- `optimizers.flow` - SGD, Adam, RMSprop
- `models/mlp_xor.flow` - XOR learning demo (trains successfully!)

### Effects (`effects/`)
Flow's unique algebraic effects (not available in Mojo/Julia):
- `dependency_injection.flow` - DI without frameworks
- `state_effects.flow` - Implicit state threading
- `async_effects.flow` - Async as effects

### Audio (`audio/`)
Real-time DSP:
- `loopback_effects.flow` - Input -> effect chain -> output (requires audio backend)
- `offline_graph_demo.flow` - Offline graph processing demo
- `bus_graph_demo.flow` - Parallel bus routing demo
- `gpu_gain_demo.flow` - GPU gain demo (CPU fallback)
- `live_graph_demo.flow` - Live graph single-standard demo

### Neural Networks (`neural_networks/`)
Autodiff and backpropagation:
- `autodiff_benchmark.flow` - Automatic differentiation
- `nn_xor.flow` - XOR neural network
- `neural_network_backprop.flow` - Backpropagation demo

### Linear Algebra (`linalg/`)
Matrix operations (Julia territory):
- `matrix_ops.flow` - Basic matrix operations
- `lu_decomposition.flow` - LU factorization

### Numerical (`numerical/`)
Scientific computing:
- `ode_solver.flow` - Euler, RK4 ODE solvers
- `optimization.flow` - Gradient descent, Newton's method

### Systems (`systems/`)
Low-level systems programming:
- `memory_pool.flow` - O(1) pool allocator
- `ring_buffer.flow` - Lock-free SPSC queue
- `hash_table.flow` - Open addressing hash table

### GPU (`gpu/`)
Metal GPU computation:
- `gpu_fft.flow` - GPU FFT
- `simd_saxpy.flow` - SIMD operations
- `vector_add_gpu.flow` - GPU vector addition

### Generics & Traits (`generics_traits/`)
Generic programming:
- `generics_demo.flow` - Generic type examples
- `traits_demo.flow` - Trait-based polymorphism
- `option_result_demo.flow` - Option/Result types

## Verified Compile Status

See [STATUS.md](STATUS.md) for a machine-generated compile status table covering
every `.flow` file under `examples/`, `apps/`, and `benchmarks/` (pass/fail plus
failure category). Regenerate it with:

```bash
python3 scripts/verify_examples.py
```

A few examples known to compile *and run* successfully:

| Example | Command |
|---------|---------|
| XOR Neural Network | `./flow run examples/ml/models/mlp_xor.flow` |
| Sort Benchmark | `./flow run benchmarks/micro/sort_benchmark.flow` |
| Benchmark Runner | `./flow run benchmarks/runner.flow` |
| Generics Demo | `./flow run examples/generics_traits/generics_demo.flow` |
| Neural Network | `./flow run examples/neural_networks/nn_xor.flow` |

## Adding New Examples

1. Create a `.flow` file in the appropriate directory
2. Include a `main() -> i32` function
3. Test with `./flow run path/to/example.flow`
4. Update this README
