# FLOW Roadmap

> Last updated: 2026-01-09  
> Current version: 0.3.3  
> Lines of Code: ~38,000

This document tracks what we're building next and why.

---

## Development Philosophy

Flow is built through **agentic pair programming** - human vision interpreted through AI implementation.

See [CONTRIBUTING.md](CONTRIBUTING.md) for collaboration guidelines.

### Guiding Principles

1. **Working > Perfect** - Ship incrementally, iterate based on use
2. **Explicit > Implicit** - Clear syntax, obvious behavior
3. **Unique > Clone** - Effects and autodiff are our differentiators
4. **Portable > Fast** - C backend means runs anywhere

### Decision Authority

| What | Who Decides |
|------|-------------|
| Language design, syntax, features | Human (final authority) |
| Implementation, code structure | AI (proposes, human approves) |
| Bug fixes, refactoring | AI (within scope) |
| Roadmap priorities | Human |

---

## Now: v0.4.0 Focus

### 🎯 Immediate Priorities (This Week)

| Task | Status | Impact |
|------|--------|--------|
| Fix `ptr[0].field` parser issue | ✅ | Unblocks 20+ examples |
| Add GitHub Actions CI | 🔲 | Prevents regressions |
| Update examples with verified status | 🔲 | Honest documentation |
| Record Tetris demo GIF | 🔲 | Visual proof it works |

### 📅 Short Term (This Month)

| Task | Status | Impact |
|------|--------|--------|
| Python package target | ✅ | Python interop |
| Cross-platform graphics (Linux) | 🔲 | Broader audience |
| Package registry design | 🔲 | Ecosystem growth |
| Effect system showcase | 🔲 | Unique selling point |
| Benchmark vs C comparison | 🔲 | Performance credibility |
| Documentation enhancements (comparisons with C and MOJO) | ✅ | Clear positioning |
| Live DSP standard (single graph + buffer layout) | ✅ | Audio consistency |
| Live plugin ABI registry | ✅ | Extensible DSP |
| Live graph hot-swap handle | ✅ | Live coding |
| RT-safety policy (no-alloc audio thread) | 🔲 | Dropout prevention |

### 🧹 Repository Cleanup

The repo has accumulated stray files, empty stubs, and misplaced artifacts. This section tracks the cleanup plan.

#### High Priority — Delete or Move

| File | Problem | Action | Status |
|------|---------|--------|--------|
| `/bench.sh` | Empty (0 bytes), superseded by `scripts/bench.sh` | Delete | 🔲 |
| `/run_bench.py` | Empty (0 bytes), superseded by `scripts/run_bench.py` | Delete | 🔲 |
| `/flow_wasm.py` | Duplicate of `wasm/flow_to_wasm.py` | Delete from root | 🔲 |
| `/test_ci_locally.sh` | Dev utility loose at repo root | Moved to `scripts/test_ci_locally.sh` | ✅ |

#### Medium Priority — Remove Empty Stubs

| File | Problem | Action | Status |
|------|---------|--------|--------|
| `examples/gpu_integration_demo.flow` | Empty (0 bytes) | Deleted | ✅ |
| `examples/gpu_integration_simple.flow` | Empty (0 bytes) | Deleted | ✅ |
| `tests/test_graphics.flow` | Empty (0 bytes) | Deleted | ✅ |
| `tests/test_const_comprehensive.flow` | Empty (0 bytes) | Deleted | ✅ |

#### Medium Priority — Misplaced Files

| File | Problem | Action | Status |
|------|---------|--------|--------|
| `examples/effects_demo.mlir` | MLIR file loose in examples root | Move to `examples/effects/` | 🔲 |
| `tools/srir_demo.mlir` | Demo data in tools dir | Move to `examples/` or `tests/` | 🔲 |
| 21 `.flow` test files in `tests/` root | `tests/core/` subdir already exists | Organize into subdirectories | 🔲 |

#### Low Priority — Empty Directories & Structure

| Item | Problem | Action | Status |
|------|---------|--------|--------|
| `challenges/` | Empty directory | Remove if not planned | 🔲 |
| `editors/` | Empty directory | Remove if not planned | 🔲 |
| `tools/` flat structure | Mixed-purpose files (debug, grad, JIT, SIMD, test) | Consider subdirs by purpose | 🔲 |
| `lib/` → `lib/stdlib/` | Single nested child | Consider flattening | 🔲 |

### 🔮 Medium Term (This Quarter)

| Task | Status | Impact |
|------|--------|--------|
| Windows graphics support | 🔲 | Full platform coverage |
| Self-hosting components | 🔲 | Dogfooding |
| WASM target | 🔲 | Web deployment |
| GPU autodiff | 🔲 | ML performance |

---

## Current State (v0.3.3)

**What works:**
- ✅ Core language (types, functions, control flow, structs, arrays)
- ✅ Effect system (effects, capabilities, handlers)
- ✅ Module system (imports, exports, cycle detection)
- ✅ Autodiff (forward mode, reverse mode, neural nets)
- ✅ Type checker (strict mode with --lenient fallback)
- ✅ C backend (stable)
- ✅ Formatter (`flow fmt`)
- ✅ Test framework (`./flow test`)
- ✅ Documentation (spec, grammar, implementation map)
- ✅ Generics (monomorphization)
- ✅ Option<T> / Result<T, E> types
- ✅ Pattern matching (integer + struct patterns)
- ✅ SIMD vectors (vec4<f32>)
- ✅ Traits/interfaces
- ✅ Lambda expressions (basic)
- ✅ Enhanced error messages with source context
- ✅ **NEW:** FFI improvements (extern blocks preserve all decls, `null` literal)
- ✅ **NEW:** Explicit mutation (`let mut`, field assignment)
- ✅ **NEW:** Bitwise operators (`|`, `&`, `^`, `~`, `<<`, `>>`) and hex literals
- ✅ **NEW:** `len(arr)` builtin, `println(...)` builtin
- ✅ **NEW:** Native runtime linking (`flow run-native`, `[native]` in flow.toml)

**What's broken/missing:**
- (Nothing critical! All major features complete)

**Recently completed:**
- ✅ Enums / ADTs — Tagged unions in C
- ✅ Trait bounds — `<T: Display>` stored in AST
- ✅ MLIR backend — Full pipeline: FLOW → MLIR → LLVM → native
- ✅ LSP — go-to-definition, hover, autocomplete
- ✅ Closures — Manual pattern with `self: Type`
- ✅ REPL — `flow repl` for interactive development
- ✅ JIT — `flow jit` for fast execution via MLIR
- ✅ Package manager — `flow init`, `flow add`, `flow build`
- ✅ GPU codegen — `@gpu` decorator, Metal shader generation
- ✅ Stdlib expansion — POSIX, collections, networking, concurrency, strings
- ✅ Documentation — Tutorials, getting started, stdlib reference

---

## Recently Completed (v0.3.3): Demo Roadmap - Competing with Mojo/Julia

**Goal:** Create comprehensive demos across 8 categories to position Flow competitively.

### Performance Benchmarks (Complete ✅)
- [x] `benchmarks/micro/matmul_benchmark.flow` - Matrix multiplication
- [x] `benchmarks/micro/mandelbrot_benchmark.flow` - Fractal computation  
- [x] `benchmarks/micro/nbody_benchmark.flow` - N-body simulation
- [x] `benchmarks/micro/fft_benchmark.flow` - Fast Fourier Transform
- [x] `benchmarks/micro/sort_benchmark.flow` - Sorting algorithms
- [x] `benchmarks/runner.flow` - Benchmark suite with statistics

### ML Framework (Complete ✅)
- [x] `examples/ml/tensor.flow` - N-dimensional tensor type
- [x] `examples/ml/nn_layers.flow` - Dense layers, activations, loss functions
- [x] `examples/ml/optimizers.flow` - SGD, Adam, RMSprop
- [x] `examples/ml/models/mlp_xor.flow` - Working XOR training demo

### Effect System Demos (Complete ✅)
- [x] `examples/effects/dependency_injection.flow` - DI without frameworks
- [x] `examples/effects/state_effects.flow` - Implicit state threading
- [x] `examples/effects/async_effects.flow` - Async/await as effects

### Scientific Computing (Complete ✅)
- [x] `examples/linalg/matrix_ops.flow` - Matrix operations
- [x] `examples/linalg/lu_decomposition.flow` - LU factorization
- [x] `examples/numerical/ode_solver.flow` - Euler, Midpoint, RK4
- [x] `examples/numerical/optimization.flow` - Gradient descent, Newton's method

### Systems Programming (Complete ✅)
- [x] `examples/systems/memory_pool.flow` - O(1) pool allocator
- [x] `examples/systems/ring_buffer.flow` - Lock-free SPSC queue
- [x] `examples/systems/hash_table.flow` - Open addressing hash table

### Real Applications (Complete ✅)
- [x] `apps/flowdb/flowdb.flow` - Key-value database
- [x] `apps/flow-http/http.flow` - HTTP framework

### Domain-Specific (Complete ✅)
- [x] `examples/data/csv_parser.flow` - CSV parsing
- [x] `examples/crypto/sha256.flow` - SHA-256 implementation
- [x] `examples/compilers/calculator.flow` - Expression parser

---

## Previously Completed (v0.3.2): Library & Native Module Ergonomics

**Goal:** Make Flow suitable for writing real libraries and native modules.

### FFI Improvements (Complete ✅)
- [x] `extern { ... }` blocks now preserve ALL function declarations (not just the first)
- [x] Extern functions never mangle their names (for correct C ABI linking)
- [x] Added `null` literal as a proper keyword (`ptr<void>` type)
- [x] Extern functions are declaration-only (no empty body generated)

### Explicit Mutation (Complete ✅)
- [x] Added `let mut` syntax for mutable variables: `let mut x: i32 = 0`
- [x] Field assignment works: `obj.field = value`
- [x] Type checker tracks mutability and warns on immutable assignment

### Bitwise Operators (Complete ✅)
- [x] Added `|` (OR), `&` (AND), `^` (XOR), `~` (NOT), `<<` (left shift), `>>` (right shift)
- [x] Hex literals work: `0xFF`, `0x1234`
- [x] Correct C precedence rules

### Arrays & Slices (Complete ✅)
- [x] Added `len(arr)` builtin for sized arrays
- [x] Created `lib/stdlib/slice.flow` with `Slice_i32`, `Slice_f32` types
- [x] Improved sized array handling (memcpy for non-literal initializers)

### Formatting (Complete ✅)
- [x] Added `println(...)` builtin (print with newline)
- [x] Improved `print()` type detection for integers, floats, strings

### Native Runtime Linking (Complete ✅)
- [x] Extended `flow.toml` with `[native]` section for native sources, frameworks, and libs
- [x] Added `flow build-native` and `flow run-native` commands

---

## Phase 1: Type System Completion (Complete ✅)

**Goal:** Make the type system trustworthy.

### 1.1 Strict Type Enforcement
**Priority:** Critical  
**Effort:** 3-5 days

Turn type checker warnings into errors. A program with type errors should not compile.

```flow
# This should ERROR, not warn
let x: i32 = "hello"  # Type mismatch: expected i32, got string
```

**Tasks:**
- [x] Change `type_checker.py` to collect errors, not just warnings
- [x] Update `transpiler.py` to exit with code 1 on type errors
- [x] Add `--strict` flag (default on) and `--lenient` flag
- [ ] Make the test corpus strict-clean (or explicitly run tests in `--lenient` where intended)
- [x] Document error messages in `docs/language/types.md`

### 1.2 Generics (Parametric Polymorphism)
**Priority:** High  
**Effort:** 1-2 weeks

Add type parameters to functions and structs.

```flow
# Generic function
function identity<T>(x: T) -> T {
    return x
}

# Generic struct
struct Pair<A, B> {
    first: A
    second: B
}

# Generic array operations
function map<T, U>(arr: array<T>, f: (T) -> U) -> array<U> {
    # ...
}
```

**Tasks:**
- [x] Add `TypeParameter` to AST in `parser.py`
- [x] Parse `<T>` syntax after function/struct names
- [x] Implement type substitution in `type_checker.py`
- [x] Monomorphize generics in `c_generator.py` (generate specialized versions)
- [x] Add generic stdlib functions: `map`, `filter`, `fold`
- [x] Test with `Option<T>`, `Result<T, E>` types

### 1.3 Type Inference (Optional)
**Priority:** Medium  
**Effort:** 3-5 days

Allow omitting obvious type annotations.

```flow
# Current (verbose)
let x: i32 = 42
let y: f32 = 3.14

# With inference (optional)
let x = 42      # Inferred as i32
let y = 3.14    # Inferred as f32
```

**Decision needed:** Do we want inference? It trades explicitness for convenience. The epistemic contract says "what you see is what you get" — inference hides information.

**Current leaning:** No inference for v1.0. Explicit types align with project philosophy.

---

## Phase 2: Language Completeness (Complete ✅)

**Goal:** Fill in missing language features.

### 2.1 Full Pattern Matching
**Priority:** High  
**Effort:** 1 week

Expand `match` to support destructuring, guards, and nested patterns.

```flow
# Current (limited)
match value {
    0 => handle_zero()
    1 => handle_one()
    _ => handle_other()
}

# Target (full)
match point {
    Point { x: 0, y: 0 } => "origin"
    Point { x: 0, y } => "on y-axis at " + y
    Point { x, y } if x == y => "on diagonal"
    _ => "elsewhere"
}
```

**Tasks:**
- [x] Add `StructPattern` with field destructuring
- [ ] Add guard clauses (`if condition`)
- [ ] Add nested patterns
- [ ] Add `|` for multiple patterns
- [ ] Exhaustiveness checking (warn on non-exhaustive matches)

### 2.2 Enums / Algebraic Data Types
**Priority:** High  
**Effort:** 1 week

Add sum types.

```flow
enum Option<T> {
    Some(T)
    None
}

enum Result<T, E> {
    Ok(T)
    Err(E)
}

function divide(a: f32, b: f32) -> Result<f32, string> {
    if b == 0.0 {
        return Err("division by zero")
    }
    return Ok(a / b)
}
```

**Tasks:**
- [x] Add `EnumDecl` to AST
- [x] Parse `enum Name { Variant1, Variant2(T) }`
- [x] Generate tagged unions in C
- [x] Integrate with pattern matching
- [x] Add `Option` and `Result` to stdlib

### 2.3 Traits / Interfaces
**Priority:** Medium  
**Effort:** 1-2 weeks

Add interface abstraction (separate from effects).

```flow
trait Printable {
    function to_string(self) -> string
}

impl Printable for Point {
    function to_string(self) -> string {
        return "(" + self.x + ", " + self.y + ")"
    }
}

function print<T: Printable>(x: T) -> void {
    printf("%s\n", x.to_string())
}
```

**Tasks:**
- [x] Add `TraitDecl` and `ImplBlock` to AST
- [x] Parse trait and impl syntax
- [x] Implement trait bounds on generics
- [x] Generate vtables or monomorphize
- [x] Decide: traits vs effects — when to use which?

### 2.4 Closures (Full)
**Priority:** Medium  
**Effort:** 1 week

Make closures capture variables properly.

```flow
function make_adder(n: i32) -> (i32) -> i32 {
    return fn(x: i32) -> i32 {
        return x + n  # Captures n
    }
}

let add5: (i32) -> i32 = make_adder(5)
let result: i32 = add5(10)  # 15
```

**Tasks:**
- [ ] Implement closure environment capture (automatic captures, not just explicit `self`)
- [x] Decide: move vs copy semantics for captures
- [x] Generate closure structs in C
- [x] Test with higher-order functions

---

## Phase 3: Tooling (Mostly complete ✅)

**Goal:** Make FLOW pleasant to use.

### 3.1 Full LSP
**Priority:** High  
**Effort:** 2-3 weeks

Make `flow-lsp` actually useful.

**Features:**
- [x] Go to definition
- [ ] Find references
- [x] Hover for type info
- [x] Autocomplete
- [ ] Inline error diagnostics
- [ ] Rename symbol

### 3.2 REPL (Complete ✅)
**Priority:** Medium  
**Effort:** 1 week

Interactive FLOW session.

```bash
$ flow repl
FLOW v0.3.x
>>> let x: i32 = 42
>>> x * 2
84
>>> function double(n: i32) -> i32 { return n * 2 }
>>> double(x)
84
```

### 3.3 Package Manager (Complete ✅)
**Priority:** Low  
**Effort:** 2-3 weeks

Dependency management.

```toml
# flow.toml
[package]
name = "my-project"
version = "0.1.0"

[dependencies]
math = "1.0"
json = { git = "https://github.com/..." }
```

**Future:** Registry/lockfiles/semantic version resolution once there’s real third-party package demand.

### 3.4 Debugger Integration
**Priority:** Low  
**Effort:** 2+ weeks

DWARF debug info, breakpoints, step-through.

**Status:** Basic setup landed (C backend): `flow debug <program.flow>` builds with `-g -O0` and emits coarse `#line` mappings back to `.flow`.

**Next:** Improve fidelity (statement-level mappings), and add an MLIR/LLVM debug story.

---

## Phase 4: Performance (2-3 months)

**Goal:** Make FLOW fast.

### 4.1 MLIR Optimization
**Priority:** Medium  
**Effort:** 2-4 weeks

Make the MLIR backend actually optimize.

- [ ] Loop vectorization
- [ ] Function inlining
- [ ] Dead code elimination
- [ ] Constant propagation

### 4.2 GPU Codegen
**Priority:** Medium  
**Effort:** 1-2 months

Generate Metal/CUDA shaders from FLOW.

**Status:** Experimental path exists (see `@gpu` + Metal codegen); treat this phase as polish/perf work, not “first implementation”.

```flow
@gpu
function vector_add(a: array<f32>, b: array<f32>, c: array<f32>, n: i32) -> void {
    let idx: i32 = gpu_thread_id()
    if idx < n {
        c[idx] = a[idx] + b[idx]
    }
}
```

### 4.3 SIMD Intrinsics
**Priority:** Low  
**Effort:** 1-2 weeks

Expose vector operations.

```flow
import "stdlib/simd.flow"

let a: f32x4 = f32x4(1.0, 2.0, 3.0, 4.0)
let b: f32x4 = f32x4(5.0, 6.0, 7.0, 8.0)
let c: f32x4 = simd_add(a, b)  # (6.0, 8.0, 10.0, 12.0)
```

---

## Phase 5: Ecosystem (Long-term)

### 5.1 Self-Hosting
Rewrite the compiler in FLOW itself.

### 5.2 Standard Library Expansion (Complete ✅)
See **Standard Library Expansion (Complete ✅)** below for the module list.

### 5.3 Documentation Generator
Generate docs from code comments.

---

## What We're NOT Doing

These are explicitly out of scope:

| Feature | Reason |
|---------|--------|
| **Garbage collection** | FLOW is for systems programming |
| **Exceptions** | Use effects and `Result<T, E>` instead |
| **Inheritance** | Composition via traits/effects |
| **Operator overloading** | Keeps code readable |
| **Macros** | Complexity not worth it yet |
| **Async/await syntax sugar** | Effects can model async without new syntax |

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-09 | No type inference for v1.0 | Explicit types align with epistemic contract |
| 2026-01-09 | Generics before traits | Generics are more fundamental |
| 2026-01-09 | Monomorphization over runtime generics | Simpler, no runtime overhead |

---

## Version Targets

| Version | Target | Key Features |
|---------|--------|--------------|
| **0.3.0** | shipped | Feature-complete core |
| **0.3.1** | next | Stabilization, docs polish, version unification |
| **0.4.0** | later | Tooling upgrades (LSP refs/rename/diagnostics), perf/MLIR polish |
| **0.5.0** | later | Ecosystem experiments (playground, debugger, packages) |
| **1.0.0** | when earned | “Boring” stability + real-world validation |

---

## Immediate Next Steps

**Completed (2026-01-09):**
1. [x] Strict type enforcement (turn warnings → errors)
   - `--strict` is default, `--lenient` for backwards compatibility
   - Run `./flow test --strict` to validate strict mode
2. [x] Parse generic syntax (`<T>`) — parsed + monomorphized
   - `function foo<T>(...)` and `struct Bar<T> { ... }` work
   - Type bounds `<T: Trait>` parsed (ignored for now)
3. [x] Add `Option<T>` and `Result<T, E>` types to stdlib
   - Concrete types: Option_i32, Result_f32_string, etc.
   - Full API with constructors, predicates, unwrapping
4. [x] **Generics with monomorphization** ✨
   - Full monomorphization pass (`src/flow/monomorphize.py`)
   - Box<T>, Pair<A, B>, identity<T> all work
   - Generic struct literals: `Box<i32> { value: 42 }`
   - Covered by the test suite (see `./flow test`)

**This week:**
1. [x] Add MatchStatement to C generator ✅
   - Integer patterns → switch statement
   - Struct patterns → if-else with destructuring
   - Variable binding with __auto_type
2. [x] Add VectorLiteral to C generator ✅
   - GCC/Clang vector extensions
   - Compound literal syntax for inline vectors
3. [x] Parser fix: vector literals in return statements ✅

**Test Results:** see `./flow test`

**Phase 2 Completed (2026-01-09):**
1. [x] Traits/interfaces ✅
   - `trait Display { function show(self) }` works
   - `impl Display for Point { ... }` works
   - Self parameter injected as first param in C
   - Method name mangling: Type_Trait_method
2. [x] Closures/lambdas (partial) ✅
   - Lambda parsing: `|x: i32| -> i32 { return x * x }`
   - Lambda C codegen: generates static functions
   - IIFE pattern needs work (tracked for future)
3. [x] Better error messages ✅
   - FlowSyntaxError with source context
   - Shows line number, column, source line
   - Caret (^) points to error location
   - Helpful suggestions for common errors

**Next priorities:**
1. [x] Full closure captures ✅ (manual closure pattern with explicit `self: Type`)
2. [x] Trait bounds stored in AST ✅ (`<T: Display>` -> TypeParameter)
3. [x] Enums / algebraic data types ✅ (tagged unions in C)
4. [x] WASM build improvements ✅ (`flow wasm` command)
5. [x] LSP improvements ✅ (go-to-definition, hover, autocomplete)
6. [x] MLIR backend ✅ (full pipeline: FLOW → MLIR → LLVM IR → native)

---

## Standard Library Expansion (Complete ✅)

New stdlib modules added:

1. **posix.flow** ✅ - POSIX system calls
   - File I/O (open, read, write, close, lseek)
   - Process management (fork, exec, wait, exit)
   - Signals (kill, signal constants)
   - Environment variables (getenv, setenv)
   - Directory operations (mkdir, chdir, getcwd)

2. **collections.flow** ✅ - Data structures
   - Vector (dynamic array)
   - Stack (LIFO)
   - Queue (FIFO)
   - HashMap (key-value store)
   - Set (unique elements)
   - LinkedList
   - PriorityQueue (min-heap)
   - Pair, Triple

3. **net.flow** ✅ - Networking
   - TCP sockets (TcpListener, TcpStream)
   - UDP sockets (UdpSocket)
   - HTTP client (HttpRequest, HttpResponse)
   - Socket address structures
   - DNS resolution stubs

4. **concurrent.flow** ✅ - Concurrency
   - Threads (pthread wrappers)
   - Mutex (mutual exclusion)
   - Condition variables
   - Read-write locks
   - Semaphores
   - Channels (Go-style)
   - Atomics (AtomicI32, AtomicI64, AtomicBool)
   - SpinLock, Once, WaitGroup

5. **string.flow** ✅ - String utilities
   - C string functions (strlen, strcmp, etc.)
   - Character classification (is_digit, is_alpha)
   - Number parsing (parse_int, parse_float)
   - StringBuilder

---

## What's Next?

The language is feature-complete! Future work:

1. ✅ **Polish & Docs** - Documentation reorganized, examples cleaned, mascot added
2. 🔲 **Async primitives** - Effects-based async/concurrency story
3. 🔲 **Debugger** - LLDB/GDB integration + web playground step-debugger
4. ✅ **Web Playground** - Browser-based IDE exists, needs step-through debugger
5. 🔲 **Real-world projects** - Build something substantial to prove it out
6. 🔲 **Parser fix** - Support `ptr[0].field` syntax (unblocks 20+ examples)

---

*This roadmap will be updated as priorities shift.*
