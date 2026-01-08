# GPU Computing Examples

This directory contains examples of GPU programming in FLOW, demonstrating parallel computing, CUDA integration, and GPU-accelerated algorithms.

## Files

- **gpu_fft.flow** - Fast Fourier Transform on GPU
- **simple_gpu_fft.flow** - Simplified GPU FFT implementation
- **gpu_fft_jit.flow** - GPU FFT with JIT compilation

## Running Examples

```bash
# GPU FFT computation
flow run gpu_fft.flow

# Simple GPU FFT
flow run simple_gpu_fft.flow

# GPU FFT with JIT
flow run gpu_fft_jit.flow
```

## What You'll Learn

1. **GPU Programming**: How to write GPU-accelerated code in FLOW
2. **Parallel Algorithms**: Designing algorithms for parallel execution
3. **Memory Management**: GPU memory allocation and transfer
4. **Kernel Launch**: Executing code on GPU
5. **Performance Optimization**: GPU-specific optimization techniques

## GPU Computing Overview

FLOW's GPU capabilities provide:
- **CUDA Integration**: Direct CUDA kernel support
- **Parallel Execution**: Massively parallel computation
- **Memory Management**: Efficient GPU memory handling
- **JIT Compilation**: Runtime kernel compilation

## Key Concepts

### GPU Kernel Definition
```flow
kernel gpu_add(a: [f32; n], b: [f32; n], result: [f32; n]) {
    let idx = get_global_id();
    if idx < n {
        result[idx] = a[idx] + b[idx];
    }
}
```

### Kernel Launch
```flow
let grid_size = (n + 255) / 256;
let block_size = 256;
launch_kernel(gpu_add, grid_size, block_size, a, b, result);
```

### Memory Management
```flow
# Allocate GPU memory
let gpu_a = gpu_malloc(f32, n);
let gpu_b = gpu_malloc(f32, n);
let gpu_result = gpu_malloc(f32, n);

# Copy data to GPU
gpu_copy_to_device(a, gpu_a);
gpu_copy_to_device(b, gpu_b);

# Launch kernel
launch_kernel(gpu_add, grid_size, block_size, gpu_a, gpu_b, gpu_result);

# Copy result back
gpu_copy_to_host(gpu_result, result);

# Free GPU memory
gpu_free(gpu_a);
gpu_free(gpu_b);
gpu_free(gpu_result);
```

## GPU Architecture

### Thread Hierarchy
```
Grid -> Block -> Thread
```

### Memory Hierarchy
```
Register -> Shared Memory -> Global Memory
```

### Execution Model
- **SIMT**: Single Instruction, Multiple Threads
- **Warps**: Groups of 32 threads executing together
- **Occupancy**: Number of active warps per SM

## Common GPU Patterns

### 1. Map Pattern
Apply operation to each element:
```flow
kernel gpu_map<T, U>(input: [T; n], output: [U; n], op: fn(T) -> U) {
    let idx = get_global_id();
    if idx < n {
        output[idx] = op(input[idx]);
    }
}
```

### 2. Reduce Pattern
Parallel reduction for aggregation:
```flow
kernel gpu_reduce<T>(data: [T; n], result: T, op: fn(T, T) -> T) {
    let tid = get_local_id();
    let bid = get_block_id();
    
    # Shared memory for block reduction
    let shared: [T; 256];
    shared[tid] = data[bid * 256 + tid];
    
    # Synchronize threads
    barrier();
    
    # Reduce within block
    let stride = 128;
    while stride > 0 {
        if tid < stride {
            shared[tid] = op(shared[tid], shared[tid + stride]);
        }
        barrier();
        stride = stride / 2;
    }
    
    # Write block result
    if tid == 0 {
        result[bid] = shared[0];
    }
}
```

### 3. Stencil Pattern
Neighborhood operations:
```flow
kernel gpu_stencil<T>(input: [T; n], output: [T; n], radius: i32) {
    let idx = get_global_id();
    if idx >= radius && idx < n - radius {
        let mut sum = input[idx];
        for i in range(1, radius + 1) {
            sum = sum + input[idx - i] + input[idx + i];
        }
        output[idx] = sum;
    }
}
```

## FFT Implementation

### Cooley-Tukey Algorithm
```flow
kernel gpu_fft_radix2(data: [f32; n], twiddle: [f32; n/2]) {
    let idx = get_global_id();
    let stage = get_stage_id();
    let distance = 1 << stage;
    let pair = idx & (distance - 1);
    let base = (idx & ~(distance - 1)) << 1;
    
    let a = base + pair;
    let b = base + distance + pair;
    
    let angle = 2.0 * 3.14159 * pair / (2.0 * distance);
    let w_real = cos(angle);
    let w_imag = sin(angle);
    
    # Complex multiplication
    let temp_real = data[2*b] * w_real - data[2*b+1] * w_imag;
    let temp_imag = data[2*b] * w_imag + data[2*b+1] * w_real;
    
    # Butterfly operation
    data[2*b] = data[2*a] - temp_real;
    data[2*b+1] = data[2*a+1] - temp_imag;
    data[2*a] = data[2*a] + temp_real;
    data[2*a+1] = data[2*a+1] + temp_imag;
}
```

## Performance Optimization

### 1. Memory Coalescing
Ensure contiguous memory access:
```flow
# Good: Coalesced access
result[idx] = input[idx];

# Bad: Strided access
result[idx * stride] = input[idx];
```

### 2. Shared Memory Usage
Use shared memory for frequently accessed data:
```flow
kernel gpu_matrix_multiply(A: [f32; N][N], B: [f32; N][N], C: [f32; N][N]) {
    let tile_size = 16;
    let shared_A: [f32; tile_size][tile_size];
    let shared_B: [f32; tile_size][tile_size];
    
    # Load tiles into shared memory
    let row = get_local_id();
    let col = get_local_id();
    shared_A[row][col] = A[block_row * tile_size + row][block_col * tile_size + col];
    shared_B[row][col] = B[block_row * tile_size + row][block_col * tile_size + col];
    
    barrier();
    
    # Compute using shared memory
    let mut sum = 0.0;
    for k in range(0, tile_size) {
        sum = sum + shared_A[row][k] * shared_B[k][col];
    }
    
    C[row][col] = sum;
}
```

### 3. Occupancy Optimization
Maximize active warps:
```flow
# Use appropriate block size
let block_size = 256;  # Good balance of occupancy and resource usage

# Minimize register usage
kernel optimized_kernel(...) {
    # Use fewer registers
    # Use shared memory instead of registers when possible
}
```

## Debugging GPU Code

### 1. Host-Side Validation
```flow
# Verify GPU results with CPU implementation
let cpu_result = cpu_fft(input);
let gpu_result = gpu_fft(input);

if !approx_equal(cpu_result, gpu_result) {
    printf("GPU computation error!\n");
}
```

### 2. Memory Checking
```flow
# Check for memory errors
gpu_check_errors();

# Validate memory bounds
if idx >= n {
    return;  # Bounds check
}
```

### 3. Profiling
```flow
# Time GPU operations
let start = gpu_timer_start();
launch_kernel(kernel, grid, block, args);
let elapsed = gpu_timer_end(start);

printf("Kernel time: %.3f ms\n", elapsed);
```

## Best Practices

### 1. Algorithm Design
- **Parallelize**: Find data parallelism
- **Minimize Divergence**: Avoid thread divergence
- **Balance Workload**: Distribute work evenly
- **Optimize Memory**: Minimize memory transfers

### 2. Memory Management
- **Batch Transfers**: Minimize host-device transfers
- **Use Pinned Memory**: Faster transfers with pinned memory
- **Overlap Transfers**: Overlap computation and transfers
- **Reuse Memory**: Reuse GPU buffers when possible

### 3. Performance Tuning
- **Profile First**: Measure before optimizing
- **Experiment**: Try different block sizes
- **Check Occupancy**: Monitor GPU utilization
- **Benchmark**: Compare with CPU implementation

## Prerequisites

- Strong FLOW programming skills
- Understanding of parallel computing
- Familiarity with CUDA/GPU concepts
- [Performance Examples](../performance/) completed

## Related Topics

- [Performance Examples](../performance/) - CPU performance optimization
- [SIMD Examples](../performance/) - Vector programming
- [Language Reference - GPU](../../language/gpu.md) - GPU language features
- [Standard Library - GPU](../../library/gpu.md) - GPU standard library

## Hardware Considerations

### GPU Architecture
- **Compute Capability**: CUDA architecture version
- **Memory Size**: Global memory capacity
- **SM Count**: Number of streaming multiprocessors
- **Clock Speed**: GPU clock frequency

### Memory Bandwidth
- **Peak Bandwidth**: Theoretical maximum transfer rate
- **Effective Bandwidth**: Actual achieved bandwidth
- **Bandwidth Optimization**: Techniques to maximize bandwidth

## Further Reading

- **CUDA Programming Guide**: Official CUDA documentation
- **GPU Computing**: General GPU programming concepts
- **Parallel Algorithms**: Design patterns for parallel algorithms
- **Computer Architecture**: Understanding GPU architecture
