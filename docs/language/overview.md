# FLOW Programming Language

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/flow-lang/flow)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.1.0-orange.svg)](https://github.com/flow-lang/flow/releases)

A high-performance, compiled programming language for scene graph rendering, UI development, and high-performance computing. FLOW compiles to MLIR and executes via JIT compilation, providing both developer productivity and runtime performance.

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/flow-lang/flow.git
cd flow
pip install -e .
```

### Your First FLOW Program

Create `hello.flow`:
```flow
function main() -> i32 {
    printf("Hello, World!\n")
    return 0
}
```

Run it:
```bash
flow run hello.flow
```

### Features at a Glance

- **🎯 Scene Graph Rendering**: Built-in support for declarative UI and graphics
- **⚡ JIT Compilation**: MLIR-based optimization with LLVM backend
- **🔒 Type Safety**: Strong static typing with generic arrays and structs
- **🎨 Effects System**: Capability-based side effect management
- **📦 Module System**: Imports, exports, and package management
- **🔥 Hot Reload**: Real-time compilation and execution
- **🧠 Pattern Matching**: Destructuring and pattern-based control flow
- **🏗️ Struct Memory Layout**: Precise control over data representation

---

## 📚 Table of Contents

1. [Language Overview](#language-overview)
2. [Types and Values](#types-and-values)
3. [Functions and Control Flow](#functions-and-control-flow)
4. [Structs and Memory Layout](#structs-and-memory-layout)
5. [Arrays and Generics](#arrays-and-generics)
6. [Pattern Matching](#pattern-matching)
7. [Effects and Capabilities](#effects-and-capabilities)
8. [Modules and Packages](#modules-and-packages)
9. [Scene Graph Rendering](#scene-graph-rendering)
10. [Memory Management](#memory-management)
11. [Performance Considerations](#performance-considerations)
12. [Standard Library](#standard-library)

---

## Language Overview

FLOW is a statically-typed, compiled language designed for high-performance graphics and computing. It combines the expressiveness of high-level languages with the performance of low-level systems programming languages.

### Design Philosophy

- **Declarative First**: Express what you want, not how to compute it
- **Zero-Cost Abstractions**: High-level features compile to efficient machine code
- **Type Safety**: Catch errors at compile time, not runtime
- **Composable**: Build complex systems from simple, reusable components
- **Hot-Reload Friendly**: Designed for rapid iteration and development

### Hello World

```flow
function main() -> i32 {
    # Print to stdout
    printf("Hello, FLOW!\n")
    
    # Return exit code
    return 0
}
```

### A More Complex Example

```flow
struct Point {
    x: f32,
    y: f32
}

struct Rectangle {
    top_left: Point,
    size: Point
}

function area(rect: Rectangle) -> f32 {
    return rect.size.x * rect.size.y
}

function main() -> i32 {
    let rect = Rectangle {
        top_left: Point { x: 0.0, y: 0.0 },
        size: Point { x: 10.0, y: 5.0 }
    }
    
    printf("Area: %.2f\n", area(rect))
    return 0
}
```

---

## Types and Values

FLOW provides a rich type system with primitive types, composite types, and user-defined types.

### Primitive Types

| Type | Description | Size | Example |
|------|-------------|------|---------|
| `i8` | 8-bit signed integer | 1 byte | `-128` to `127` |
| `i16` | 16-bit signed integer | 2 bytes | `-32768` to `32767` |
| `i32` | 32-bit signed integer | 4 bytes | `-2147483648` to `2147483647` |
| `i64` | 64-bit signed integer | 8 bytes | `-9.22×10^18` to `9.22×10^18` |
| `u8` | 8-bit unsigned integer | 1 byte | `0` to `255` |
| `u16` | 16-bit unsigned integer | 2 bytes | `0` to `65535` |
| `u32` | 32-bit unsigned integer | 4 bytes | `0` to `4294967295` |
| `u64` | 64-bit unsigned integer | 8 bytes | `0` to `1.84×10^19` |
| `f32` | 32-bit floating point | 4 bytes | IEEE-754 single precision |
| `f64` | 64-bit floating point | 8 bytes | IEEE-754 double precision |
| `bool` | Boolean value | 1 byte | `true` or `false` |
| `string` | String literal | Variable | `"Hello, World!"` |

### Type Inference

FLOW supports type inference for local variables:

```flow
function demo() -> i32 {
    let integer = 42        # Inferred as i32
    let floating = 3.14     # Inferred as f32
    let truthy = true       # Inferred as bool
    let text = "Hello"      # Inferred as string
    
    # Explicit types are still required for function parameters
    return integer
}
```

### Type Conversions

#### Implicit Conversions

FLOW allows safe implicit conversions:

```flow
function demo() -> f64 {
    let i: i32 = 42
    let f: f64 = i  # Implicitly promoted to f64
    return f
}
```

#### Explicit Conversions

Use built-in functions for explicit conversions:

```flow
function demo() -> i32 {
    let f: f32 = 3.14
    let i: i32 = f as i32  # Truncates decimal part
    return i
}
```

---

## Functions and Control Flow

### Function Definition

```flow
# Basic function
function add(a: i32, b: i32) -> i32 {
    return a + b
}

# Function with no return value
function greet(name: string) -> void {
    printf("Hello, %s!\n", name)
}

# Recursive function
function factorial(n: i32) -> i32 {
    if n <= 1 {
        return 1
    } else {
        return n * factorial(n - 1)
    }
}
```

### Control Flow

#### If-Elif-Else

```flow
function classify_score(score: i32) -> string {
    if score >= 90 {
        return "Excellent"
    } elif score >= 80 {
        return "Good"
    } elif score >= 70 {
        return "Average"
    } else {
        return "Needs Improvement"
    }
}
```

#### Loops

```flow
function demo_loops() -> i32 {
    # While loop
    let i: i32 = 0
    while i < 10 {
        printf("While: %d\n", i)
        i = i + 1
    }
    
    # For loop with range
    for j in 0..10 {
        printf("For: %d\n", j)
    }
    
    # Parallel for loop
    for k in 0..1000 parallel {
        # This loop can be parallelized
        printf("Parallel: %d\n", k)
    }
    
    return 0
}
```

#### Loop-Carried Variables

FLOW automatically detects variables modified in loops and handles them correctly:

```flow
function sum_array(arr: array<i32>) -> i32 {
    let sum: i32 = 0
    for i in 0..len(arr) {
        sum = sum + arr[i]  # sum is loop-carried
    }
    return sum
}
```

---

## Structs and Memory Layout

FLOW provides precise control over struct memory layout, making it ideal for performance-critical applications and interfacing with other languages.

### Struct Definition

```flow
struct Vector2D {
    x: f32,
    y: f32
}

struct Person {
    name: string,
    age: i32,
    position: Vector2D
}
```

### Memory Layout

Structs are laid out in memory with predictable byte offsets:

```flow
struct Example {
    a: i8,   # Offset 0, size 1
    b: i32,  # Offset 4, size 4 (aligned)
    c: f32,  # Offset 8, size 4
    d: i8    # Offset 12, size 1
}
```

### Field Access

```flow
function demo_struct_access() -> f32 {
    let v = Vector2D { x: 1.0, y: 2.0 }
    let x_coord = v.x
    let y_coord = v.y
    
    # Nested access
    let person = Person {
        name: "Alice",
        age: 30,
        position: Vector2D { x: 10.0, y: 20.0 }
    }
    
    return person.position.y  # Returns 20.0
}
```

### Struct Assignment

Structs are copied by value:

```flow
function demo_struct_copy() -> i32 {
    let a = Vector2D { x: 1.0, y: 2.0 }
    let b = a        # b is a copy of a
    b.x = 10.0      # Only b is modified
    
    # a.x is still 1.0
    return 0
}
```

### Memory Layout Introspection

You can inspect struct layouts at compile time:

```flow
function demo_layout() -> i32 {
    # Vector2D has size 8 bytes (2 * 4 bytes for f32)
    let size = sizeof(Vector2D)  # Returns 8
    
    # Field offsets can be queried
    let x_offset = offsetof(Vector2D, x)  # Returns 0
    let y_offset = offsetof(Vector2D, y)  # Returns 4
    
    return size
}
```

---

## Arrays and Generics

FLOW provides powerful generic array support with compile-time type safety.

### Array Types

```flow
# Fixed-size array
let fixed: array<i32, 10> = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# Dynamic array
let dynamic: array<f32> = array<f32>(10)

# Array literals
let numbers = [1, 2, 3, 4, 5]
let floats = [1.0, 2.0, 3.0]
```

### Array Operations

```flow
function demo_arrays() -> i32 {
    # Create an array
    let arr: array<i32> = array<i32>(5)
    
    # Set elements
    arr[0] = 10
    arr[1] = 20
    arr[2] = 30
    arr[3] = 40
    arr[4] = 50
    
    # Get elements
    let first = arr[0]
    let last = arr[4]
    
    # Array length
    let length = len(arr)  # Returns 5
    
    # Iterate over array
    let sum: i32 = 0
    for i in 0..length {
        sum = sum + arr[i]
    }
    
    return sum
}
```

### Multi-dimensional Arrays

```flow
function demo_2d_array() -> i32 {
    # 2D array: 3x4 matrix
    let matrix: array<array<i32>> = array<array<i32>>(3)
    
    # Initialize
    for i in 0..3 {
        matrix[i] = array<i32>(4)
        for j in 0..4 {
            matrix[i][j] = i * 4 + j
        }
    }
    
    # Access element
    return matrix[1][2]  # Returns 6
}
```

### Array Slices

```flow
function demo_slices() -> i32 {
    let arr = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    
    # Slice from index 2 to 6 (exclusive)
    let slice = arr[2:6]  # [3, 4, 5, 6]
    
    # Slice with step
    let every_other = arr[0:10:2]  # [1, 3, 5, 7, 9]
    
    return len(slice)
}
```

---

## Pattern Matching

FLOW provides powerful pattern matching capabilities for expressive control flow.

### Basic Pattern Matching

```flow
function describe_number(n: i32) -> string {
    match n {
        0 => "zero",
        1 => "one",
        2 => "two",
        _ => "many"
    }
}
```

### Pattern Matching with Guards

```flow
function classify_age(age: i32) -> string {
    match age {
        n if n < 0 => "invalid",
        n if n < 13 => "child",
        n if n < 20 => "teenager",
        n if n < 65 => "adult",
        _ => "senior"
    }
}
```

### Struct Pattern Matching

```flow
struct Point {
    x: i32,
    y: i32
}

function match_point(p: Point) -> string {
    match p {
        Point { x: 0, y: 0 } => "origin",
        Point { x: x, y: 0 } => "on x-axis",
        Point { x: 0, y: y } => "on y-axis",
        Point { x: x, y: y } => "at ({x}, {y})"
    }
}
```

### Nested Pattern Matching

```flow
struct Circle {
    center: Point,
    radius: i32
}

function describe_circle(c: Circle) -> string {
    match c {
        Circle { center: Point { x: 0, y: 0 }, radius: r } => "circle at origin with radius {r}",
        Circle { center: Point { x: x, y: y }, radius: r } => "circle at ({x}, {y}) with radius {r}"
    }
}
```

### Pattern Matching with Arrays

```flow
function analyze_list(arr: array<i32>) -> string {
    match arr {
        [] => "empty",
        [x] => "single element: {x}",
        [x, y] => "two elements: {x}, {y}",
        [x, y, z, ...] => "at least three: {x}, {y}, {z}...",
        _ => "many elements"
    }
}
```

---

## Effects and Capabilities

FLOW's effect system provides capability-based side effect management, allowing for safe and composable code.

### Defining Effects

```flow
effect FileSystem {
    read(path: string) -> string,
    write(path: string, content: string) -> void,
    delete(path: string) -> void
}

effect GPU {
    allocate_buffer(size: i32) -> GPUBuffer,
    launch_kernel(kernel: Shader, grid: i32, block: i32) -> void,
    synchronize() -> void
}
```

### Implementing Capabilities

```flow
capability LocalFileSystem implements FileSystem {
    function read(path: string) -> string {
        # Local file system implementation
        return read_local_file(path)
    }
    
    function write(path: string, content: string) -> void {
        write_local_file(path, content)
    }
    
    function delete(path: string) -> void {
        delete_local_file(path)
    }
}

capability CUDAGPU implements GPU {
    function allocate_buffer(size: i32) -> GPUBuffer {
        return cuda_allocate(size)
    }
    
    function launch_kernel(kernel: Shader, grid: i32, block: i32) -> void {
        cuda_launch(kernel, grid, block)
    }
    
    function synchronize() -> void {
        cuda_sync()
    }
}
```

### Using Effects

```flow
function process_file(path: string) -> i32 {
    handle FileSystem with LocalFileSystem {
        let content = FileSystem.read(path)
        let processed = transform_content(content)
        FileSystem.write(path + ".processed", processed)
        return 0
    }
}

function compute_on_gpu(data: array<f32>) -> array<f32> {
    handle GPU with CUDAGPU {
        let buffer = GPU.allocate_buffer(len(data) * 4)
        GPU.launch_kernel(compute_shader, 1024, 64)
        GPU.synchronize()
        return read_results(buffer)
    }
}
```

### Effect Polymorphism

Effects can be polymorphic, allowing different implementations:

```flow
function generic_computation<T: GPU>(data: array<f32>) -> array<f32> {
    handle GPU with T {
        # This works with any GPU implementation
        return gpu_compute(data)
    }
}

# Usage
let result_cuda = generic_computation<CUDAGPU>(data)
let result_opencl = generic_computation<OpenCLGPU>(data)
```

---

## Modules and Packages

FLOW provides a robust module system for code organization and reuse.

### Module Structure

```
my_project/
├── main.flow
├── math/
│   ├── vector.flow
│   └── matrix.flow
├── graphics/
│   ├── renderer.flow
│   └── shader.flow
└── utils/
    └── helpers.flow
```

### Exports and Imports

#### math/vector.flow
```flow
export struct Vector2D {
    x: f32,
    y: f32
}

export function dot(a: Vector2D, b: Vector2D) -> f32 {
    return a.x * b.x + a.y * b.y
}

export function length(v: Vector2D) -> f32 {
    return sqrt(dot(v, v))
}
```

#### main.flow
```flow
import "math/vector.flow"
import "graphics/renderer.flow"

function main() -> i32 {
    let v = Vector2D { x: 3.0, y: 4.0 }
    let l = length(v)  # Using imported function
    
    printf("Vector length: %.2f\n", l)
    return 0
}
```

### Selective Imports

```flow
# Import only specific symbols
import { Vector2D, dot } from "math/vector.flow"

# Import with alias
import { Vector2D as Vec2 } from "math/vector.flow"

# Import all symbols (use sparingly)
import * as Math from "math/vector.flow"
```

### Package Management

FLOW supports package management through a package.json file:

```json
{
    "name": "my-project",
    "version": "1.0.0",
    "dependencies": {
        "flow-math": "^1.2.0",
        "flow-graphics": "^2.1.0"
    },
    "dev-dependencies": {
        "flow-test": "^0.5.0"
    }
}
```

Install dependencies:
```bash
flow install
```

---

## Scene Graph Rendering

FLOW has built-in support for declarative scene graph rendering, making it ideal for UI and graphics applications.

### Scene Graph Structure

```flow
struct SceneNode {
    id: string,
    transform: Transform,
    children: array<SceneNode>,
    renderer: Renderer
}

struct Transform {
    position: Vector2D,
    rotation: f32,
    scale: Vector2D
}
```

### Declarative UI

```flow
function build_ui() -> SceneNode {
    return SceneNode {
        id: "main_panel",
        transform: Transform {
            position: Vector2D { x: 0.0, y: 0.0 },
            rotation: 0.0,
            scale: Vector2D { x: 1.0, y: 1.0 }
        },
        children: [
            create_button("OK", Vector2D { x: 10.0, y: 10.0 }),
            create_button("Cancel", Vector2D { x: 10.0, y: 50.0 }),
            create_text_field("input", Vector2D { x: 10.0, y: 90.0 })
        ],
        renderer: PanelRenderer
    }
}
```

### Rendering Pipeline

```flow
function render_scene(scene: SceneNode, time: f32) -> void {
    handle GPU with OpenGLGPU {
        # Clear screen
        GPU.clear(Color { r: 0.2, g: 0.2, b: 0.2, a: 1.0 })
        
        # Render scene graph
        render_node(scene, time)
        
        # Present
        GPU.present()
    }
}

function render_node(node: SceneNode, time: f32) -> void {
    # Apply transform
    GPU.push_matrix()
    GPU.translate(node.transform.position)
    GPU.rotate(node.transform.rotation)
    GPU.scale(node.transform.scale)
    
    # Render this node
    node.renderer.render(node, time)
    
    # Render children
    for child in node.children {
        render_node(child, time)
    }
    
    # Restore transform
    GPU.pop_matrix()
}
```

### Animation System

```flow
struct Animation {
    duration: f32,
    keyframes: array<Keyframe>,
    easing: EasingFunction
}

function animate_value(animation: Animation, time: f32) -> f32 {
    let t = time / animation.duration
    let eased = animation.easing(t)
    
    # Interpolate between keyframes
    return interpolate_keyframes(animation.keyframes, eased)
}
```

---

## Memory Management

FLOW provides predictable memory management with both automatic and manual control options.

### Stack Allocation

Local variables are allocated on the stack:

```flow
function demo_stack() -> i32 {
    let x: i32 = 42        # Stack allocated
    let arr: array<i32> = [1, 2, 3, 4, 5]  # Stack allocated
    
    return x + arr[0]
}
```

### Heap Allocation

Dynamic allocation uses the heap:

```flow
function demo_heap() -> i32 {
    let size = 1000
    let large_array: array<i32> = array<i32>(size)  # Heap allocated
    
    for i in 0..size {
        large_array[i] = i * 2
    }
    
    return large_array[size - 1]
}
```

### Memory Pools

For performance-critical applications, FLOW supports memory pools:

```flow
effect MemoryPool {
    allocate(size: i32) -> ptr,
    deallocate(ptr: ptr) -> void
}

capability BumpAllocator implements MemoryPool {
    let pool_start: ptr
    let pool_end: ptr
    let current: ptr
    
    function allocate(size: i32) -> ptr {
        if self.current + size > self.pool_end {
            panic("Out of memory")
        }
        
        let ptr = self.current
        self.current = self.current + size
        return ptr
    }
    
    function deallocate(ptr: ptr) -> void {
        # Bump allocator doesn't free individual allocations
        # Entire pool is freed at once
    }
}
```

### Zero-Copy Operations

FLOW optimizes for zero-copy operations:

```flow
function process_large_data(data: array<f32>) -> array<f32> {
    # Instead of copying, pass by reference
    return transform_in_place(data)
}

function transform_in_place(data: array<f32>) -> array<f32> {
    for i in 0..len(data) {
        data[i] = data[i] * 2.0
    }
    return data  # Same array, modified in place
}
```

---

## Performance Considerations

FLOW is designed for high performance, with several optimization features.

### SIMD Vectorization

FLOW automatically vectorizes compatible operations:

```flow
function vectorized_add(a: array<f32>, b: array<f32>) -> array<f32> {
    let result: array<f32> = array<f32>(len(a))
    
    # This loop will be auto-vectorized by LLVM
    for i in 0..len(a) {
        result[i] = a[i] + b[i]
    }
    
    return result
}
```

### Parallel Execution

```flow
function parallel_process(data: array<f32>) -> array<f32> {
    let result: array<f32> = array<f32>(len(data))
    
    # This loop can run in parallel
    for i in 0..len(data) parallel {
        result[i] = expensive_computation(data[i])
    }
    
    return result
}
```

### Inlining

FLOW aggressively inlines small functions:

```flow
inline function small_add(a: i32, b: i32) -> i32 {
    return a + b
}

function demo() -> i32 {
    # small_add will be inlined
    return small_add(1, 2)
}
```

### Profile-Guided Optimization

```flow
# Mark hot functions for optimization
hot function critical_path(data: array<f32>) -> f32 {
    # This function will be heavily optimized
    return compute_result(data)
}
```

### Cache-Friendly Data Structures

```flow
# Struct of Arrays (SoA) for better cache locality
struct ParticlesSoA {
    positions_x: array<f32>,
    positions_y: array<f32>,
    velocities_x: array<f32>,
    velocities_y: array<f32>
}

# Array of Structs (AoS) for convenience
struct Particle {
    position: Vector2D,
    velocity: Vector2D
}
```

---

## Standard Library

FLOW provides a comprehensive standard library.

### Math Library

```flow
import "std/math.flow"

function demo_math() -> f32 {
    let x = 3.14159
    let sin_x = sin(x)
    let cos_x = cos(x)
    let sqrt_x = sqrt(x)
    
    return sin_x * cos_x + sqrt_x
}
```

### String Library

```flow
import "std/string.flow"

function demo_strings() -> string {
    let s1 = "Hello"
    let s2 = "World"
    let combined = s1 + ", " + s2 + "!"
    
    let substring = combined[0:5]  # "Hello"
    let length = len(combined)    # 13
    
    return combined
}
```

### Array Library

```flow
import "std/array.flow"

function demo_array_ops() -> i32 {
    let arr = [1, 2, 3, 4, 5]
    
    let sum = reduce(arr, 0, fn(a, b) { a + b })
    let doubled = map(arr, fn(x) { x * 2 })
    let evens = filter(arr, fn(x) { x % 2 == 0 })
    
    return sum
}
```

### File I/O

```flow
import "std/io.flow"

function demo_io() -> i32 {
    handle FileSystem with LocalFileSystem {
        let content = FileSystem.read("input.txt")
        let lines = split(content, "\n")
        
        for line in lines {
            printf("Line: %s\n", line)
        }
        
        FileSystem.write("output.txt", "Processed content")
        return 0
    }
}
```

---

## Advanced Topics

### Metaprogramming

FLOW supports compile-time metaprogramming:

```flow
macro generate_struct(name: string, fields: array<string>) -> string {
    let struct_def = "struct " + name + " {\n"
    
    for field in fields {
        struct_def = struct_def + "    " + field + ": i32,\n"
    }
    
    struct_def = struct_def + "}"
    return struct_def
}

# Use at compile time
#generate_struct("Point", ["x", "y"])
```

### Foreign Function Interface

```flow
foreign {
    function malloc(size: i32) -> ptr
    function free(ptr: ptr) -> void
    function printf(format: string, ...) -> i32
}

function demo_ffi() -> i32 {
    let ptr = malloc(1024)
    # Use ptr...
    free(ptr)
    
    printf("Hello from FFI!\n")
    return 0
}
```

### Compile-Time Constants

```flow
const PI: f32 = 3.14159265359
const GRAVITY: f32 = 9.81
const MAX_ENTITIES: i32 = 1000

function demo_constants() -> f32 {
    return PI * GRAVITY
}
```

---

## Tooling and Ecosystem

### Compiler Tools

```bash
# Compile to executable
flow build program.flow -o program

# Run with JIT
flow run program.flow

# Check types
flow check program.flow

# Format code
flow format program.flow

# Generate documentation
flow docs program.flow
```

### IDE Integration

FLOW provides LSP (Language Server Protocol) support for:

- Syntax highlighting
- Auto-completion
- Go-to-definition
- Type checking
- Refactoring

### Testing Framework

```flow
import "std/test.flow"

test "addition works" {
    assert(add(2, 3) == 5)
    assert(add(-1, 1) == 0)
}

test "array operations" {
    let arr = [1, 2, 3]
    assert(len(arr) == 3)
    assert(arr[0] == 1)
}

run_tests()
```

---

## Contributing

We welcome contributions to FLOW! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
git clone https://github.com/flow-lang/flow.git
cd flow
pip install -e ".[dev]"
pre-commit install
```

### Running Tests

```bash
# Run all tests
flow test

# Run specific test
flow test tests/test_structs.flow

# Run with coverage
flow test --coverage
```

---

## License

FLOW is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## Community

- [Discord Server](https://discord.gg/flow-lang)
- [Reddit Community](https://reddit.com/r/flow-lang)
- [Twitter](https://twitter.com/flow_lang)

---

## Acknowledgments

FLOW is built on the shoulders of giants:

- [MLIR](https://mlir.llvm.org/) for the multi-level intermediate representation
- [LLVM](https://llvm.org/) for the compiler infrastructure
- [Rust](https://www.rust-lang.org/) for inspiration on type safety and memory management
- [Mojo](https://www.modular.com/mojo) for AI/ML integration ideas
- [C++](https://isocpp.org/) for zero-cost abstractions philosophy
