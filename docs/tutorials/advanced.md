# FLOW Tutorial: Advanced

Master effects, autodiff, GPU programming, and compiler backends.

## Part 1: Effect System

FLOW's effect system lets you declare and handle side effects explicitly.

### 1.1 Declaring Effects

```flow
effect Console {
    function print(message: string) -> void
    function read_line() -> string
}

effect FileSystem {
    function read_file(path: string) -> string
    function write_file(path: string, content: string) -> void
}
```

### 1.2 Using Effects

```flow
function greet() -> void with Console {
    Console.print("What's your name? ")
    let name = Console.read_line()
    Console.print("Hello, ")
    Console.print(name)
    Console.print("!\n")
}
```

### 1.3 Capability-Based Effects

```flow
capability StdioConsole for Console {
    function print(message: string) -> void {
        printf("%s", message)
    }
    
    function read_line() -> string {
        return "User"  # Simplified
    }
}

function main() -> i32 {
    handle greet() with StdioConsole
    return 0
}
```

### 1.4 Why Effects?

| Benefit | Description |
|---------|-------------|
| **Testability** | Mock effects in tests |
| **Composition** | Combine effects safely |
| **Documentation** | Effects are visible in types |
| **Purity** | Pure functions have no effects |

---

## Part 2: Automatic Differentiation

FLOW has built-in support for computing gradients.

### 2.1 Forward Mode (Dual Numbers)

```flow
import "stdlib/autodiff.flow"

function main() -> i32 {
    # Create dual numbers: value + derivative
    let x = dual(3.0, 1.0)  # x = 3, dx/dx = 1
    
    # f(x) = x²
    let y = dual_mul(x, x)
    
    printf("f(3) = %f\n", y.val)   # 9
    printf("f'(3) = %f\n", y.grad) # 6 (derivative of x² is 2x)
    
    return 0
}
```

### 2.2 Common Operations

```flow
import "stdlib/autodiff.flow"

function main() -> i32 {
    let x = dual(1.0, 1.0)
    
    # All return Dual with (value, gradient)
    let a = dual_add(x, x)      # 2x
    let b = dual_mul(x, x)      # x²
    let c = dual_sin(x)         # sin(x)
    let d = dual_exp(x)         # e^x
    let e = dual_sigmoid(x)     # 1/(1+e^(-x))
    
    printf("sin(1) = %f, d/dx = %f\n", c.val, c.grad)
    
    return 0
}
```

### 2.3 Neural Network Example

```flow
import "stdlib/nn.flow"

function main() -> i32 {
    # Create a 2-input, 2-hidden, 1-output network
    let net = net2x2x1_new()
    
    # XOR training data
    let inputs = [[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]]
    let targets = [0.0, 1.0, 1.0, 0.0]
    
    # Training loop would go here
    printf("Neural network created\n")
    
    return 0
}
```

---

## Part 3: GPU Programming

### 3.1 The @gpu Decorator

Mark functions for GPU execution:

```flow
@gpu
function vector_add(a: array<f32>, b: array<f32>, out: array<f32>, n: i32) {
    let i = gpu_thread_id()
    if i < n {
        out[i] = a[i] + b[i]
    }
}
```

### 3.2 GPU Built-ins

| Function | Description |
|----------|-------------|
| `gpu_thread_id()` | Current thread index |
| `gpu_block_id` | Current block index |
| `gpu_local_id` | Thread index within block |
| `gpu_barrier()` | Synchronize threads |
| `gpu_block_size` | Threads per block |

### 3.3 Generate Metal Shaders

```bash
./flow gpu my_kernels.flow
```

This generates Metal Shading Language code:

```metal
#include <metal_stdlib>
using namespace metal;

kernel void vector_add(
    device float* a [[buffer(0)]],
    device float* b [[buffer(1)]],
    device float* out [[buffer(2)]],
    constant int& n [[buffer(3)]],
    uint tid [[thread_position_in_grid]]
) {
    auto i = tid;
    if ((i < n)) {
        out[i] = (a[i] + b[i]);
    }
}
```

### 3.4 Matrix Multiplication

```flow
@gpu
function matmul(A: array<f32>, B: array<f32>, C: array<f32>, M: i32, N: i32, K: i32) {
    let row = gpu_thread_id() / N
    let col = gpu_thread_id() % N
    
    if row < M && col < N {
        let sum = 0.0
        for k in 0..K {
            sum = sum + A[row * K + k] * B[k * N + col]
        }
        C[row * N + col] = sum
    }
}
```

### 3.5 Parallel Reduction

```flow
@gpu
function parallel_sum(input: array<f32>, output: array<f32>, n: i32) {
    let i = gpu_thread_id()
    
    # Each thread handles one element
    if i < n {
        # Simplified - real reduction uses shared memory
        output[0] = output[0] + input[i]
    }
    
    gpu_barrier()
}
```

---

## Part 4: Multiple Backends

### 4.1 C Backend (Default)

```bash
./flow run program.flow      # Compile to C, run
./flow compile program.flow  # Compile to executable
```

Generates portable C99 code.

### 4.2 MLIR Backend

```bash
./flow mlir program.flow      # Generate MLIR
./flow mlir-run program.flow  # Compile via MLIR and run
```

Pipeline: FLOW → MLIR → LLVM IR → Native

### 4.3 JIT Compilation

```bash
./flow jit program.flow
```

Fastest for development - compiles in memory.

### 4.4 WebAssembly

```bash
./flow wasm program.flow
```

Generates browser-runnable code.

---

## Part 5: POSIX System Programming

### 5.1 File I/O

```flow
import "stdlib/posix.flow"

function main() -> i32 {
    # Open a file for writing
    let fd = open("test.txt", O_WRONLY | O_CREAT | O_TRUNC, DEFAULT_MODE)
    
    if fd < 0 {
        printf("Failed to open file\n")
        return 1
    }
    
    # Write to file (simplified)
    let msg = "Hello, file!\n"
    # write(fd, msg, strlen(msg))
    
    close(fd)
    return 0
}
```

### 5.2 Process Management

```flow
import "stdlib/posix.flow"

function main() -> i32 {
    printf("PID: %d\n", getpid())
    printf("Parent PID: %d\n", getppid())
    printf("UID: %d\n", getuid())
    
    return 0
}
```

### 5.3 Environment Variables

```flow
import "stdlib/posix.flow"

function main() -> i32 {
    let home = getenv("HOME")
    let path = getenv("PATH")
    
    printf("HOME: %s\n", home)
    
    return 0
}
```

---

## Part 6: SIMD Vectors

### 6.1 Vector Types

```flow
function main() -> i32 {
    # 4-element float vector
    let a: vec4<f32> = [1.0, 2.0, 3.0, 4.0]
    let b: vec4<f32> = [5.0, 6.0, 7.0, 8.0]
    
    # Vector operations
    let sum = a + b        # Element-wise addition
    let product = a * b    # Element-wise multiplication
    
    return 0
}
```

### 6.2 SIMD in Practice

```flow
@gpu
function simd_saxpy(x: array<f32>, y: array<f32>, a: f32, n: i32) {
    let i = gpu_thread_id() * 4  # Process 4 elements at a time
    
    if i + 3 < n {
        # Load 4 elements
        let vx: vec4<f32> = [x[i], x[i+1], x[i+2], x[i+3]]
        let vy: vec4<f32> = [y[i], y[i+1], y[i+2], y[i+3]]
        let va: vec4<f32> = [a, a, a, a]
        
        # y = a*x + y
        let result = va * vx + vy
        
        # Store back
        y[i] = result[0]
        y[i+1] = result[1]
        y[i+2] = result[2]
        y[i+3] = result[3]
    }
}
```

---

## Part 7: Language Server Protocol

### 7.1 IDE Features

FLOW includes an LSP server for IDE integration:

```bash
./flow lsp
```

Or use the wrapper:

```bash
./flow-lsp
```

### 7.2 Supported Features

| Feature | Status |
|---------|--------|
| Syntax highlighting | ✅ |
| Go to definition | ✅ |
| Hover information | ✅ |
| Autocomplete | ✅ |
| Document symbols | ✅ |
| Error diagnostics | ✅ |

### 7.3 VS Code Extension

The `editors/vscode/` directory contains a VS Code extension with:
- Syntax highlighting for `.flow` files
- LSP client integration

---

## Part 8: Testing

### 8.1 Test Declarations

```flow
test "addition works" {
    let result = 2 + 2
    if result != 4 {
        return 1  # Test failed
    }
    return 0  # Test passed
}

test "fibonacci is correct" {
    if fibonacci(10) != 55 {
        return 1
    }
    return 0
}
```

### 8.2 Running Tests

```bash
./flow test                    # Run all tests
./flow test tests/my_test.flow # Run specific test
./flow test-strict             # Strict type checking
```

---

## Exercises

### Exercise 1: Custom Effect

Create a `Logger` effect with `log`, `warn`, and `error` operations.

### Exercise 2: GPU Dot Product

Write a `@gpu` function that computes the dot product of two vectors.

### Exercise 3: Autodiff Chain Rule

Compute the gradient of `f(x) = sin(x²)` using the autodiff library.

---

## Reference

- [Language Specification](../LANGUAGE_SPEC.md)
- [Grammar (EBNF)](../grammar.ebnf)
- [Standard Library API](../library/stdlib-reference.md)
- [Development Guide](../DEVELOPMENT.md)
