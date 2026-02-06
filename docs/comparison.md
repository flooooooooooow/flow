# Flow Language Comparison

How Flow compares to other programming languages.

---

## Compiler Build Requirements

| Language | Disk Space | Build Time | Dependencies |
|----------|------------|------------|--------------|
| **Flow** | **< 50 MB** | **< 1s** | Python 3.8+, Clang |
| V | < 20 MB | < 1s | None (self-hosted) |
| Go | 525 MB | 1m 33s | None |
| GCC | 8 GB | 50m | Many |
| Rust | 30 GB | 45m | LLVM |
| Clang | 90 GB | 60m | LLVM |
| Swift | 70 GB | 90m | LLVM |

**Flow's advantage:** No LLVM dependency. The compiler is ~12k lines of Python that generates portable C.

---

## Feature Comparison

| Feature | Flow | Rust | Go | Mojo | Julia | Zig | V |
|---------|------|------|-----|------|-------|-----|---|
| **Algebraic Effects** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Built-in Autodiff** | ✅ | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ |
| **Generics** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Pattern Matching** | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ❌ |
| **C Backend** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| **No LLVM Required** | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ | ✅ |
| **Native Graphics** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **REPL** | ✅ | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ |
| **Hot Reload** | 🔲 | ❌ | ❌ | ✅ | ✅ | ❌ | ✅ |
| **Memory Safety** | Manual | ✅ | GC | ✅ | GC | ✅ | GC |
| **Null Safety** | ✅ | ✅ | ❌ | ✅ | ❌ | ✅ | ✅ |
| **GPU Support** | ✅ | Libs | ❌ | ✅ | ❌ | ❌ | ❌ |

---

## Philosophy Comparison

### Flow vs Rust
- **Rust:** Maximum safety, zero-cost abstractions, steep learning curve
- **Flow:** Practical safety, effects for side effects, gentler learning curve
- **When to use Flow:** Rapid prototyping, AI/ML, when you need algebraic effects
- **When to use Rust:** Production systems, maximum performance, memory-critical

### Flow vs Go
- **Go:** Simplicity, concurrency, garbage collected
- **Flow:** Expressiveness, effects, no GC overhead
- **When to use Flow:** Scientific computing, graphics, when you need generics/effects
- **When to use Go:** Web services, DevOps tools, when you need simplicity

### Flow vs Mojo
- **Mojo:** Python superset, AI-focused, LLVM-based
- **Flow:** New syntax, effects-based, C-backend
- **When to use Flow:** When you want algebraic effects, portable C output
- **When to use Mojo:** When you need Python compatibility, Modular ecosystem

### Flow vs Julia
- **Julia:** Scientific computing, JIT, dynamic typing
- **Flow:** Static typing, compiled, effects system
- **When to use Flow:** When you want static types, effects, native binaries
- **When to use Julia:** Interactive data science, existing Julia ecosystem

### Flow vs Zig
- **Zig:** Low-level control, C interop, comptime
- **Flow:** Higher-level, effects, autodiff
- **When to use Flow:** ML, graphics, when you need effects
- **When to use Zig:** Systems programming, replacing C

### Flow vs V
- **V:** Simplicity, fast compilation, C-backend
- **Flow:** More features (effects, autodiff), similar compilation model
- **When to use Flow:** When you need effects, autodiff, pattern matching
- **When to use V:** When you want extreme simplicity

---

## Performance Comparison

*Note: These are preliminary benchmarks. Run `./flow run benchmarks/runner.flow` for current results.*

| Benchmark | Flow | C (clang -O2) | Ratio |
|-----------|------|---------------|-------|
| Matrix Multiply (512x512) | TBD | TBD | TBD |
| Mandelbrot (1024x1024) | TBD | TBD | TBD |
| N-body (1000 bodies) | TBD | TBD | TBD |
| Quicksort (1M elements) | TBD | TBD | TBD |

**Target:** Within 2x of C for compute-bound workloads.

---

## Unique Flow Features

### 1. Algebraic Effects

No other systems language has this. Effects allow:
- Dependency injection without frameworks
- Testable code without mocking libraries
- Controlled side effects

```flow
effect Logger {
    log(msg: string) -> void
}

# Swap implementations without changing code
capability ConsoleLogger { ... }
capability FileLogger { ... }
capability TestLogger { ... }
```

### 2. Built-in Autodiff

Automatic differentiation in the language, not a library:

```flow
# Forward-mode autodiff for gradients
# Used for neural networks, optimization, physics
```

### 3. Native Graphics

Built-in window creation and rendering:

```flow
gfx_open(800, 600, "My App")
gfx_fill_rect(x, y, w, h, color)
gfx_present()
```

### 4. C Backend

Compiles to readable C, not LLVM IR:
- Debug with printf, GDB, Valgrind
- Port to any platform with a C compiler
- Inspect generated code easily

---

## When to Choose Flow

✅ **Choose Flow if you:**
- Want algebraic effects (unique feature)
- Need autodiff built into the language
- Want to avoid LLVM complexity
- Are building AI/ML applications
- Want native graphics without external libs
- Prefer explicit mutation (`let mut`)

❌ **Don't choose Flow if you:**
- Need maximum runtime performance (use Rust/C++)
- Need a large ecosystem (use Python/JS/Rust)
- Need production-ready stability (Flow is young)
- Need async/await (coming soon via effects)

---

## Migration Guides

*(Coming soon)*

- From Python to Flow
- From Rust to Flow
- From Julia to Flow
