---
name: Language / feature proposal
description: Propose a language or toolchain change
labels: ["enhancement"]
---

### Problem
Currently, the CUDA GPU backend in FLOW (handled in `src/flow/gpu_integration.py`) generates rudimentary, custom string-based CUDA C code for kernels and compiles it via raw `nvcc`. This simple `for`-loop approach is fine for basic element-wise operations but falls severely short for heavy dense linear algebra, specifically General Matrix Multiply (GEMM) workloads.

When training or inferencing machine learning models, modern NVIDIA architectures rely heavily on Tensor Cores to reach peak performance. The current AST code generation strategy lacks the sophisticated loop tiling, memory hierarchy management, and software pipelining needed to properly utilize these hardware features, leading to severely suboptimal performance for neural networks and large-scale simulations in FLOW.

### Proposal
We propose integrating [NVIDIA/cutlass](https://github.com/NVIDIA/cutlass) into the FLOW CUDA toolchain. CUTLASS is a collection of high-performance C++ template abstractions for implementing GEMM and related computations in CUDA, efficiently targeting Tensor Cores.

By integrating CUTLASS, FLOW could automatically route complex matrix-multiplication operations directly to highly optimized CUTLASS templates rather than naive nested loops.

Since the exact implementation strategy needs to be carefully deliberated upon later, a few high-level approaches exist:
1. **AST Pattern Matching**: Detect `gemm`-like patterns in the FLOW AST and automatically lower them to CUTLASS C++ template instantiations during code generation in `_generate_cuda_kernel`.
2. **Standard Library Primitives**: Expose explicit GEMM intrinsics in a module like `stdlib/cuda/cutlass.flow` that allow developers to manually invoke tensor operations, bypassing the naive AST generator entirely.
3. **MLIR Dialect Lowering**: If FLOW relies more heavily on MLIR in the future, lower FLOW ops into an MLIR dialect that inherently maps to CUTLASS.

### Alternatives considered
* **cuBLAS**: A highly optimized standard library by NVIDIA. However, cuBLAS is a pre-compiled binary library whereas CUTLASS is header-only C++, offering much greater flexibility for custom data types, epilogue fusions (like activation functions directly after a GEMM), and easier integration into our existing C/C++ generation pipeline.
* **MLIR GPU/NVVM Dialects**: Waiting for and relying solely on upstream MLIR to handle optimal Tensor Core loop tiling. While possible, directly using CUTLASS might be a faster path to peak hardware utilization for specific known operations.

### Design authority
- [x] I understand language design decisions are human-final (see CONTRIBUTING.md)