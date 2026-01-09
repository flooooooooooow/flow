# Flow Examples

Organized examples demonstrating Flow language features.

## Directory Structure

```
examples/
├── basics/           # Core language: loops, functions, algorithms
├── audio/            # Real-time audio DSP with audio library
├── neural_networks/  # Autodiff, backprop, XOR networks
├── gpu/              # GPU computing, SIMD, Metal integration
├── effects/          # Effect system demos
├── generics_traits/  # Generics, traits, enums, closures
├── graphics/         # PPM output, shaders, web demos
├── modules/          # Import/export, multi-file projects
└── misc/             # Experimental, tests, misc demos
```

## Quick Start

```bash
# Run any example
./flow run examples/basics/hello_world.flow
./flow run examples/audio/audio_synth_demo.flow
./flow run examples/neural_networks/nn_xor.flow

# Run all tests
./flow test
```

## Highlights by Category

### basics/
- `hello_world.flow` - Start here
- `fibonacci.flow` - Recursion
- `bubble_sort.flow` - Arrays and loops

### audio/
- `audio_synth_demo.flow` - Subtractive synth with oscillator, filter, envelope
- `audio_effects_demo.flow` - Audio I/O using Flow's effect system

### neural_networks/
- `autodiff_demo.flow` - Forward-mode automatic differentiation
- `nn_xor.flow` - Train a neural network on XOR
- `neural_network_backprop.flow` - Manual backpropagation

### gpu/
- `simple_gpu_fft.flow` - FFT on GPU
- `simd_saxpy.flow` - SIMD vector operations

### effects/
- `effects_working.flow` - Core effect system demo
- `effect_dispatch_demo.flow` - Runtime effect dispatch

### generics_traits/
- `generics_demo.flow` - Generic functions and structs
- `traits_demo.flow` - Trait-based polymorphism
- `option_result_demo.flow` - Option and Result types
