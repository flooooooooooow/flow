# FLOW Roadmap

> Last updated: 2026-01-09
> Current version: 0.2.0

This document tracks what we're building next and why.

---

## Current State (v0.3.0)

**What works:**
- ✅ Core language (types, functions, control flow, structs, arrays)
- ✅ Effect system (effects, capabilities, handlers)
- ✅ Module system (imports, exports, cycle detection)
- ✅ Autodiff (forward mode, reverse mode, neural nets)
- ✅ Type checker (strict mode with --lenient fallback)
- ✅ C backend (stable)
- ✅ Formatter (`flow fmt`)
- ✅ Test framework (156 tests passing - 100%)
- ✅ Documentation (spec, grammar, implementation map)
- ✅ Generics (monomorphization)
- ✅ Option<T> / Result<T, E> types
- ✅ Pattern matching (integer + struct patterns)
- ✅ SIMD vectors (vec4<f32>)
- ✅ Traits/interfaces
- ✅ Lambda expressions (basic)
- ✅ Enhanced error messages with source context

**What's broken/missing:**
- ❌ GPU codegen — Runtime exists, no shader generation
- ❌ Package manager — No dependency management

**Recently completed:**
- ✅ Enums / ADTs — Tagged unions in C
- ✅ Trait bounds — `<T: Display>` stored in AST
- ✅ MLIR backend — Full pipeline: FLOW → MLIR → LLVM → native
- ✅ LSP — go-to-definition, hover, autocomplete
- ✅ Closures — Manual pattern with `self: Type`
- ✅ REPL — `flow repl` for interactive development
- ✅ JIT — `flow jit` for fast execution via MLIR

---

## Phase 1: Type System Completion (2 weeks)

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
- [ ] Change `type_checker.py` to collect errors, not just warnings
- [ ] Update `transpiler.py` to exit with code 1 on type errors
- [ ] Add `--strict` flag (default on) and `--lenient` flag
- [ ] Fix all 152 tests to pass strict checking
- [ ] Document error messages in `docs/language/types.md`

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
- [ ] Add `TypeParameter` to AST in `parser.py`
- [ ] Parse `<T>` syntax after function/struct names
- [ ] Implement type substitution in `type_checker.py`
- [ ] Monomorphize generics in `c_generator.py` (generate specialized versions)
- [ ] Add generic stdlib functions: `map`, `filter`, `fold`
- [ ] Test with `Option<T>`, `Result<T, E>` types

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

## Phase 2: Language Completeness (2-4 weeks)

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
- [ ] Add `StructPattern` with field destructuring
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
- [ ] Add `EnumDecl` to AST
- [ ] Parse `enum Name { Variant1, Variant2(T) }`
- [ ] Generate tagged unions in C
- [ ] Integrate with pattern matching
- [ ] Add `Option` and `Result` to stdlib

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
- [ ] Add `TraitDecl` and `ImplBlock` to AST
- [ ] Parse trait and impl syntax
- [ ] Implement trait bounds on generics
- [ ] Generate vtables or monomorphize
- [ ] Decide: traits vs effects — when to use which?

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
- [ ] Implement closure environment capture
- [ ] Decide: move vs copy semantics for captures
- [ ] Generate closure structs in C
- [ ] Test with higher-order functions

---

## Phase 3: Tooling (1-2 months)

**Goal:** Make FLOW pleasant to use.

### 3.1 Full LSP
**Priority:** High  
**Effort:** 2-3 weeks

Make `flow-lsp` actually useful.

**Features:**
- [ ] Go to definition
- [ ] Find references
- [ ] Hover for type info
- [ ] Autocomplete
- [ ] Inline error diagnostics
- [ ] Rename symbol

### 3.2 REPL
**Priority:** Medium  
**Effort:** 1 week

Interactive FLOW session.

```bash
$ flow repl
FLOW v0.3.0
>>> let x: i32 = 42
>>> x * 2
84
>>> function double(n: i32) -> i32 { return n * 2 }
>>> double(x)
84
```

### 3.3 Package Manager
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

**Defer until:** Community exists and needs it.

### 3.4 Debugger Integration
**Priority:** Low  
**Effort:** 2+ weeks

DWARF debug info, breakpoints, step-through.

**Defer until:** People are writing non-trivial programs.

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

### 5.2 Standard Library Expansion
- Data structures (HashMap, Set, Queue)
- I/O (files, network)
- Concurrency (channels, async)
- Serialization (JSON, protobuf)

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
| **Async/await** | Effects can model this better |

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
| **0.3.0** | 2 weeks | Strict types, generics basics |
| **0.4.0** | 1 month | Pattern matching, enums |
| **0.5.0** | 2 months | Traits, full closures |
| **0.6.0** | 3 months | Full LSP, REPL |
| **1.0.0** | 6 months | Production-ready core |

---

## Immediate Next Steps

**Completed (2026-01-09):**
1. [x] Strict type enforcement (turn warnings → errors)
   - `--strict` is default, `--lenient` for backwards compatibility
   - 62/153 tests pass strict mode
2. [x] Parse generic syntax (`<T>`) — parsed, not yet monomorphized
   - `function foo<T>(...)` and `struct Bar<T> { ... }` work
   - Type bounds `<T: Trait>` parsed (ignored for now)
3. [x] Add `Option<T>` and `Result<T, E>` types to stdlib
   - Concrete types: Option_i32, Result_f32_string, etc.
   - Full API with constructors, predicates, unwrapping
4. [x] **Generics with monomorphization** ✨
   - Full monomorphization pass (`src/flow/monomorphize.py`)
   - Box<T>, Pair<A, B>, identity<T> all work
   - Generic struct literals: `Box<i32> { value: 42 }`
   - 145/154 tests passing (9 pre-existing failures)

**This week:**
1. [x] Add MatchStatement to C generator ✅
   - Integer patterns → switch statement
   - Struct patterns → if-else with destructuring
   - Variable binding with __auto_type
2. [x] Add VectorLiteral to C generator ✅
   - GCC/Clang vector extensions
   - Compound literal syntax for inline vectors
3. [x] Parser fix: vector literals in return statements ✅

**Test Results:** 156/156 passing (100%) 🎉

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

*This roadmap will be updated as priorities shift.*
