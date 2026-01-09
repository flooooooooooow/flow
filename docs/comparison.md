# FLOW vs Other Languages

A detailed comparison of FLOW with established systems programming languages.

## Quick Comparison Matrix

| Feature | FLOW | Rust | Zig | Go | C |
|---------|------|------|-----|-----|---|
| **Memory Safety** | Manual + Effects | Ownership | Manual | GC | Manual |
| **Generics** | ✅ Monomorphized | ✅ Monomorphized | ✅ Comptime | ❌ | ❌ |
| **Traits/Interfaces** | ✅ | ✅ | ❌ | ✅ | ❌ |
| **Algebraic Effects** | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Pattern Matching** | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Enums (ADTs)** | ✅ | ✅ | ✅ | ❌ | Weak |
| **REPL** | ✅ | ❌ | ❌ | ❌ | ❌ |
| **JIT Compilation** | ✅ | ❌ | ❌ | ❌ | ❌ |
| **GPU Codegen** | ✅ Metal | Via libs | Via libs | Via libs | Via libs |
| **Autodiff** | ✅ Built-in | Via libs | ❌ | ❌ | ❌ |
| **WebAssembly** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Self-Hosting** | ❌ Python | ✅ | ✅ | ✅ | ✅ |
| **Maturity** | < 1 year | 14 years | 8 years | 15 years | 50+ years |

---

## FLOW vs Rust

### Similarities
- Static typing with type inference
- Generics with monomorphization
- Pattern matching and enums
- Traits for polymorphism
- Zero-cost abstractions goal

### Key Differences

| Aspect | FLOW | Rust |
|--------|------|------|
| **Memory** | Manual (like C) | Ownership + Borrow Checker |
| **Learning Curve** | Lower | Steeper |
| **Side Effects** | Explicit via Effects | Implicit |
| **Compile Time** | Fast (C backend) | Slower |
| **Ecosystem** | Minimal | Massive (crates.io) |

### When to Choose FLOW over Rust

✅ **Choose FLOW if you:**
- Want explicit effect tracking
- Need built-in autodiff for ML
- Prefer simpler memory model
- Want REPL for prototyping
- Are experimenting with language design

✅ **Choose Rust if you:**
- Need memory safety guarantees
- Want mature ecosystem
- Building production systems
- Need async/await
- Want compiler-enforced safety

### Code Comparison

**FLOW:**
```flow
effect Logger {
    function log(msg: string) -> void
}

function process(data: array<i32>) -> i32 with Logger {
    Logger.log("Processing...")
    let sum = 0
    for i in 0..len(data) {
        sum = sum + data[i]
    }
    return sum
}
```

**Rust:**
```rust
// Side effects are implicit
fn process(data: &[i32]) -> i32 {
    println!("Processing...");  // Hidden side effect
    data.iter().sum()
}
```

---

## FLOW vs Zig

### Similarities
- Systems programming focus
- Manual memory management
- C interop priority
- Compile-time evaluation
- No hidden control flow

### Key Differences

| Aspect | FLOW | Zig |
|--------|------|-----|
| **Generics** | Type parameters | Comptime |
| **Effects** | First-class | None |
| **Build System** | Shell/Make | Built-in |
| **Error Handling** | Result types | Error unions |
| **Compiler** | Python → C | Self-hosted |

### When to Choose FLOW over Zig

✅ **Choose FLOW if you:**
- Want algebraic effects
- Need autodiff/ML features
- Prefer traditional generics syntax
- Want REPL development
- Are exploring effect systems

✅ **Choose Zig if you:**
- Need production-ready systems code
- Want comptime metaprogramming
- Building OS/embedded systems
- Need mature tooling
- Want self-hosted compiler

### Code Comparison

**FLOW:**
```flow
function generic_max<T>(a: T, b: T) -> T {
    if a > b {
        return a
    }
    return b
}
```

**Zig:**
```zig
fn generic_max(comptime T: type, a: T, b: T) T {
    return if (a > b) a else b;
}
```

---

## FLOW vs Go

### Similarities
- Simple, readable syntax
- Fast compilation
- Built-in tooling (fmt, test)
- Interfaces for polymorphism

### Key Differences

| Aspect | FLOW | Go |
|--------|------|-----|
| **Generics** | ✅ Full | Limited (1.18+) |
| **Memory** | Manual | Garbage Collected |
| **Effects** | First-class | None |
| **Enums** | ✅ ADTs | ❌ Constants only |
| **Concurrency** | Effects-based | Goroutines |

### When to Choose FLOW over Go

✅ **Choose FLOW if you:**
- Need full generics
- Want effect tracking
- Need pattern matching
- Want manual memory control
- Building ML/scientific code

✅ **Choose Go if you:**
- Building web services
- Need goroutines/channels
- Want large ecosystem
- Prefer GC simplicity
- Need production stability

### Code Comparison

**FLOW:**
```flow
enum Result<T, E> {
    Ok(T),
    Err(E)
}

function divide(a: f64, b: f64) -> Result<f64, string> {
    if b == 0.0 {
        return Err("division by zero")
    }
    return Ok(a / b)
}
```

**Go:**
```go
func divide(a, b float64) (float64, error) {
    if b == 0 {
        return 0, errors.New("division by zero")
    }
    return a / b, nil
}
```

---

## FLOW vs C

### Similarities
- Manual memory management
- Direct hardware access
- Minimal runtime
- Transpiles to C

### Key Differences

| Aspect | FLOW | C |
|--------|------|---|
| **Type Safety** | Stronger | Weak |
| **Generics** | ✅ | ❌ (macros) |
| **Effects** | ✅ | ❌ |
| **Enums** | ADTs | Integer constants |
| **Modules** | ✅ | Header files |

### When to Choose FLOW over C

✅ **Choose FLOW if you:**
- Want type-safe generics
- Need effect tracking
- Want pattern matching
- Building ML/autodiff code
- Want cleaner syntax

✅ **Choose C if you:**
- Need maximum portability
- Working with existing C codebases
- Need embedded/kernel development
- Want widest tool support
- Need ABI stability

### Code Comparison

**FLOW:**
```flow
struct Point<T> {
    x: T,
    y: T
}

function distance<T>(p1: Point<T>, p2: Point<T>) -> T {
    let dx = p2.x - p1.x
    let dy = p2.y - p1.y
    return sqrt(dx * dx + dy * dy)
}
```

**C:**
```c
// No generics - need separate functions or macros
typedef struct { float x, y; } PointF;
typedef struct { double x, y; } PointD;

float distance_f(PointF p1, PointF p2) {
    float dx = p2.x - p1.x;
    float dy = p2.y - p1.y;
    return sqrtf(dx * dx + dy * dy);
}
```

---

## FLOW's Unique Features

### 1. Algebraic Effects

No other mainstream systems language has this:

```flow
effect State<T> {
    function get() -> T
    function set(val: T) -> void
}

function counter() -> i32 with State<i32> {
    let current = State.get()
    State.set(current + 1)
    return current
}

capability MemoryState<T> for State<T> {
    let storage: T = 0
    
    function get() -> T { return storage }
    function set(val: T) -> void { storage = val }
}

function main() -> i32 {
    handle counter() with MemoryState<i32>
    return 0
}
```

### 2. Built-in Autodiff

```flow
import "stdlib/autodiff.flow"

function gradient_descent() -> f64 {
    let x = dual(2.0, 1.0)  # x = 2, dx/dx = 1
    
    # f(x) = x² - 4x + 4 = (x-2)²
    let f = dual_sub(dual_mul(x, x), dual_add(dual_mul(dual(4.0, 0.0), x), dual(-4.0, 0.0)))
    
    # f.grad is the derivative at x=2
    return f.grad  # Should be 0 (minimum)
}
```

### 3. GPU Codegen from High-Level Code

```flow
@gpu
function neural_layer(input: array<f32>, weights: array<f32>, output: array<f32>, in_size: i32, out_size: i32) {
    let i = gpu_thread_id()
    if i < out_size {
        let sum = 0.0
        for j in 0..in_size {
            sum = sum + input[j] * weights[i * in_size + j]
        }
        output[i] = 1.0 / (1.0 + exp(-sum))  # sigmoid
    }
}
```

Generates actual Metal shaders—not just bindings.

### 4. Interactive REPL

```
$ flow repl
flow> let x = 42
flow> x * 2
84
flow> function fib(n: i32) -> i32 { if n <= 1 { return n } return fib(n-1) + fib(n-2) }
flow> fib(10)
55
```

No other systems language has this level of interactivity.

---

## Feature Deep Dives

### Effect System Comparison

| Language | Side Effect Tracking |
|----------|---------------------|
| **FLOW** | First-class effects with handlers |
| **Rust** | None (implicit) |
| **Haskell** | Monads (different approach) |
| **Koka** | Similar effect system |
| **OCaml 5** | Algebraic effects (recent) |

FLOW is one of the few *systems* languages with algebraic effects.

### Generics Comparison

| Language | Approach | Polymorphism |
|----------|----------|--------------|
| **FLOW** | Monomorphization | Compile-time |
| **Rust** | Monomorphization | Compile-time |
| **Go** | Type erasure + dict | Runtime |
| **C++** | Templates | Compile-time |
| **Java** | Type erasure | Runtime |

### Autodiff Comparison

| Language | Autodiff Support |
|----------|-----------------|
| **FLOW** | Built-in (forward + reverse) |
| **Julia** | Via packages (Zygote, ForwardDiff) |
| **Python** | Via libraries (JAX, PyTorch) |
| **Swift** | Experimental (differentiable programming) |
| **Rust** | Via crates |

FLOW has autodiff as a *first-class* stdlib feature.

---

## Ecosystem Comparison

| Metric | FLOW | Rust | Zig | Go |
|--------|------|------|-----|-----|
| **Package Manager** | Basic | Cargo | Zigmod | Go modules |
| **Packages** | ~10 | 100k+ | ~1k | 300k+ |
| **IDE Support** | LSP | Excellent | Good | Excellent |
| **Documentation** | Growing | Excellent | Good | Excellent |
| **Community** | Small | Large | Medium | Large |

---

## Migration Guides

### From C to FLOW

```c
// C
typedef struct { int x, y; } Point;
int add(Point p) { return p.x + p.y; }
```

```flow
// FLOW
struct Point { x: i32, y: i32 }
function add(p: Point) -> i32 { return p.x + p.y }
```

### From Rust to FLOW

```rust
// Rust
fn process<T: Display>(items: Vec<T>) -> Result<(), Error> {
    for item in items {
        println!("{}", item);
    }
    Ok(())
}
```

```flow
// FLOW
effect IO {
    function print(msg: string) -> void
}

function process<T>(items: array<T>) -> void with IO {
    for i in 0..len(items) {
        IO.print(to_string(items[i]))
    }
}
```

### From Go to FLOW

```go
// Go
type Result struct {
    Value int
    Err   error
}

func divide(a, b int) Result {
    if b == 0 {
        return Result{Err: errors.New("div by zero")}
    }
    return Result{Value: a / b}
}
```

```flow
// FLOW
enum Result<T, E> {
    Ok(T),
    Err(E)
}

function divide(a: i32, b: i32) -> Result<i32, string> {
    if b == 0 {
        return Err("div by zero")
    }
    return Ok(a / b)
}
```

---

## When to Use FLOW

### ✅ Great For

- **ML/Scientific Computing** — Built-in autodiff, GPU codegen
- **Language Research** — Effect system experimentation
- **Prototyping** — REPL, fast iteration
- **Learning** — Clean syntax, explicit semantics
- **Side-Effect Tracking** — Effects make I/O visible

### ⚠️ Not Yet Ready For

- **Production Systems** — Too young, small ecosystem
- **Large Teams** — Limited tooling
- **Embedded/Kernel** — C/Rust more appropriate
- **Web Services** — Go/Rust have better ecosystems

---

## Summary

| If You Value... | Consider |
|-----------------|----------|
| Memory safety guarantees | Rust |
| Maximum performance + simplicity | Zig |
| Fast development + GC | Go |
| Maximum portability | C |
| **Effect tracking + Autodiff + Experimentation** | **FLOW** |

FLOW occupies a unique niche: a systems language with algebraic effects, built-in autodiff, and GPU codegen. It's not trying to replace Rust or Go—it's exploring what a modern systems language *could* look like with different tradeoffs.

---

*FLOW v0.3.0 — Exploring the design space of systems programming*
