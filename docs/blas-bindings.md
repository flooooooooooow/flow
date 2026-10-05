# BLAS/LAPACK Bindings for Flow

Flow provides high-performance linear algebra via Apple Accelerate (macOS) or OpenBLAS (Linux).

## Quick Start

```flow
import "stdlib/blas.flow"

function main() -> i32 {
    # MATLAB-style matrix creation
    let A: Mat = eye(3)
    let B: Mat = ones(3, 3)
    
    # Matrix multiply: C = A @ B
    let C: Mat = matmul(A, B)
    
    # Or in-place for zero allocation:
    let D: Mat = mat_new(3, 3)
    gemm(A, B, D)  # D = A @ B
    
    # Linear solve: x = A \ b
    let b: array<f64, 3> = [1.0, 2.0, 3.0]
    let x: array<f64, 3> = [0.0, 0.0, 0.0]
    solve(A, b, x)  # Solves A * x = b
    
    mat_free(A)
    mat_free(B)
    mat_free(C)
    mat_free(D)
    return 0
}
```

## Compilation

```bash
# macOS (uses Accelerate framework)
FLOW_LDFLAGS="-framework Accelerate" ./flow run myfile.flow

# Or compile to C, then link yourself:
./flow build myfile.flow --c -o build/myfile.c
clang -O3 build/myfile.c -framework Accelerate -o myfile

# Linux (uses OpenBLAS)
FLOW_LDFLAGS="-lopenblas" ./flow run myfile.flow
```

## Performance

Benchmarked on Apple Silicon (Accelerate with AMX), `benchmarks/blas_vs_naive.flow`:

| Matrix Size | BLAS | Naive Loops | Speedup |
|-------------|------|-------------|---------|
| 128x128 | 240 GFLOPS | 1.7 GFLOPS | 120x |
| 256x256 | 241 GFLOPS | 1.7 GFLOPS | 144x |
| 512x512 | 271 GFLOPS | 2.2 GFLOPS | 121x |

Run it yourself: `FLOW_LDFLAGS="-framework Accelerate" ./flow run benchmarks/blas_vs_naive.flow`

## API Reference

### Matrix Creation

| Function | Description |
|----------|-------------|
| `mat_new(rows, cols)` | Allocate zero-initialized matrix |
| `eye(n)` | n×n identity matrix |
| `zeros(rows, cols)` | Zero matrix |
| `ones(rows, cols)` | Matrix of ones |
| `mat_clone(A)` | Deep copy |
| `mat_free(A)` | Free memory |

### Element Access

| Function | Description |
|----------|-------------|
| `mat_get(A, i, j)` | Get A[i,j] |
| `mat_set(A, i, j, val)` | Set A[i,j] = val |

### BLAS Level 1 (Vector)

| Function | Description |
|----------|-------------|
| `dot(x, y, n)` | Dot product |
| `norm2(x, n)` | Euclidean norm |
| `axpy(alpha, x, y, n)` | y = alpha*x + y |
| `scal(alpha, x, n)` | x = alpha*x |

### BLAS Level 3 (Matrix)

| Function | Description |
|----------|-------------|
| `gemm(A, B, C)` | C = A @ B |
| `gemm_alpha_beta(α, A, B, β, C)` | C = α*A@B + β*C |
| `matmul(A, B)` | Returns new C = A @ B |
| `transpose(A)` | Returns new A^T |

### LAPACK

| Function | Description |
|----------|-------------|
| `solve(A, b, x)` | Solve A*x = b (LU) |

## Comparison with MATLAB

| MATLAB | Flow |
|--------|------|
| `A * B` | `matmul(A, B)` or `gemm(A, B, C)` |
| `A \ b` | `solve(A, b, x)` |
| `eye(n)` | `eye(n)` |
| `zeros(m,n)` | `zeros(m, n)` |
| `ones(m,n)` | `ones(m, n)` |
| `A'` | `transpose(A)` |

### Key Differences

1. **Memory management**: Flow requires explicit `mat_free()`. MATLAB has GC.
2. **In-place ops**: Flow's `gemm(A, B, C)` writes to pre-allocated C. MATLAB allocates.
3. **Speed**: Flow is faster (no interpreter overhead, same BLAS backend).
4. **Cost**: Flow is free. MATLAB is $2,150/year.

## Why This Beats MATLAB

1. **Same BLAS backend** — Both call vendor-optimized BLAS (Accelerate/MKL)
2. **No interpreter** — Flow compiles to native code
3. **Zero startup** — No 2-5 second MATLAB launch time
4. **Tiny binaries** — ~100KB vs 2GB MATLAB Runtime
5. **Real-time safe** — Can use in audio/embedded (MATLAB can't)
