# FLOW Language Specification

> **Version**: 0.11.1
> **Last Updated**: 2026-08-14

## Overview

FLOW is a statically-typed, systems programming language with first-class support for:
- **Algebraic effects** for modular side-effect handling
- **Evolution / dynamics DSLs** (`flow` / `evolves as`, units of measure, `field` PDE, `analyze` LQR) — see [§10](#10-domain--dsl-surfaces)
- **Native graphics** (macOS Metal/Cocoa; Linux/Windows SDL2) and **fill shaders** (`shader fill`) — see [graphics.md](language/graphics.md) / [shaders.md](language/shaders.md)
- **GPU memory helpers** via Metal on macOS (stdlib); CUDA/OpenCL are **not** shipping
- **Automatic differentiation** as library dual/reverse helpers (see [autodiff.md](library/autodiff.md))
- **WebAssembly** via Flow→C→Emscripten (see [wasm.md](language/wasm.md))

## Quick Reference

### Commands
```bash
flow run <file.flow>      # Compile and run (default host: flowc; escape: FLOW_HOST=python)
flow compile <file.flow>  # Compile to executable
flow fmt <file.flow>      # Format source code
flow test                 # Run all tests
flow jit <file.flow>      # MLIR JIT (requires LLVM/MLIR toolchain)
flow gfx <file.flow>      # Native graphics programs
flow shader <file.flow>   # Fill-shader surface → Metal / C
flow debug <file.flow>    # Launch with debugger (#line maps)
```

---

> **AUTHORITATIVE REFERENCE** — This document is the single source of truth for the FLOW language.
> All other documentation references this spec. Features marked ✅ are implemented, ⚠️ are partial, ❌ are planned.
> Focused pages under [docs/language/](language/) are preferred for learning; this file owns status matrices and edge cases.

---

## Table of Contents

1. [Lexical Structure](#1-lexical-structure)
2. [Types](#2-types) (incl. [§2.6 Units](#26-units-of-measure))
3. [Declarations](#3-declarations)
4. [Expressions](#4-expressions)
5. [Statements](#5-statements)
6. [Effect System](#6-effect-system)
7. [Module System](#7-module-system)
8. [Memory Model](#8-memory-model)
9. [Compilation Targets](#9-compilation-targets)
10. [Domain / DSL Surfaces](#10-domain--dsl-surfaces)

---

## 1. Lexical Structure

### 1.1 Keywords

| Keyword | Status | Category |
|---------|--------|----------|
| `function` | ✅ | Declaration |
| `let` | ✅ | Declaration |
| `const` | ✅ | Declaration |
| `struct` | ✅ | Declaration |
| `effect` | ✅ | Effect System |
| `capability` | ✅ | Effect System |
| `handle` | ✅ | Effect System |
| `with` | ✅ | Effect System |
| `import` | ✅ | Module |
| `export` | ✅ | Module |
| `extern` | ✅ | FFI |
| `return` | ✅ | Control Flow |
| `if` | ✅ | Control Flow |
| `else` | ✅ | Control Flow |
| `elif` | ✅ | Control Flow |
| `while` | ✅ | Control Flow |
| `for` | ✅ | Control Flow |
| `in` | ✅ | Control Flow |
| `parallel` | ✅ | Control Flow (`parallel for` → OpenMP when available; serial fallback) |
| `step` | ✅ | Control Flow |
| `match` | ⚠️ | Pattern Matching (literals, structs, guards, `\|` alternation, nested literal fields; real exhaustiveness checking for `bool` and enum/ADT variants via path/const patterns, minimal stub for integers) |
| `default` | ✅ | Pattern Matching |
| `mut` | ✅ | Mutability (`let mut`) |
| `to` | ✅ | Range (`for i in 0 to n`) — preferred over `..` |
| `break` | ✅ | Control Flow |
| `continue` | ✅ | Control Flow |
| `defer` | ✅ | Control Flow (run on scope exit) |
| `enum` | ✅ | Declaration |
| `trait` | ✅ | Declaration |
| `impl` | ✅ | Declaration |
| `type` | ✅ | Type alias |
| `distinct` | ✅ | Nominal / distinct type |
| `as` | ✅ | Explicit cast |
| `and` / `or` / `not` | ✅ | Logical (alongside `&&` / `\|\|` / `!`) |
| `null` | ✅ | Null pointer literal |
| `dbg` | ⚠️ | Prints to stderr and yields its operand in the C backend; evaluation-only in MLIR (§3.6.1) |
| `expect` | ⚠️ | Aborts with a diagnostic in the C backend; evaluation-only in MLIR (§3.6.1) |
| `test` | ⚠️ | Parses to a `bool` function; no backend or harness calls it (§3.6.1) |
| `inline` | ✅ | Optimization hint; emits `static inline` (§3.6) |
| `noinline` | ✅ | Emits `__attribute__((noinline))` (§3.6) |
| `always_inline` | ✅ | Emits `__attribute__((always_inline))` plus the inline specifier (§3.6) |
| `target` | ✅ | Emits `__attribute__((target("…")))`; the string's shape is checked, its meaning is the C compiler's (§3.6) |
| `module` | ⚠️ | `module X { ... }` is parsed, then flattened: the block name is discarded and the inner declarations become globals. Two blocks declaring the same name emit duplicate C. Accepts 7 declaration forms; `import` inside a block is never resolved. See [modules-namespacing.md](language/modules-namespacing.md) |
| `theorem` / `assume` / `therefore` | ⚠️ | Verification surface (`flow-verify` / design — see [verification.md](language/verification.md)) |
| `unit` | ✅ | Units of measure (§2.6) |
| `flow` | ✅ | Evolution block (§10.1) — contextual keyword |
| `ui_layout` / `ui_row` / `ui_column` / `ui_stack` / `ui_grid` | ⚠️ | UI layout sugar (parsed; host-dependent) |

### 1.2 Operators

| Operator | Type | Status |
|----------|------|--------|
| `+` | Arithmetic | ✅ |
| `-` | Arithmetic | ✅ |
| `*` | Arithmetic | ✅ |
| `/` | Arithmetic | ✅ |
| `%` | Arithmetic | ✅ |
| `==` | Comparison | ✅ |
| `!=` | Comparison | ✅ |
| `<` | Comparison | ✅ |
| `>` | Comparison | ✅ |
| `<=` | Comparison | ✅ |
| `>=` | Comparison | ✅ |
| `&&` / `and` | Logical | ✅ |
| `\|\|` / `or` | Logical | ✅ |
| `!` / `not` | Logical | ✅ |
| `&` `|` `^` `~` `<<` `>>` | Bitwise | ✅ |
| `=` | Assignment | ✅ |
| `to` | Range keyword | ✅ (canonical `for` range) |
| `..` | Range | ✅ (accepted alias of `to`) |
| `\|>` | Pipe | ✅ (declarative ordering — §4.5) |
| `&` / `*` | Address-of / deref | ✅ (unary; see §8.3) |
| `->` | Type Arrow | ✅ |
| `=>` | Match Arrow | ✅ |
| `::` | Scope Resolution | ✅ (effects only) |
| `.` | Field Access | ✅ |

### 1.3 Literals

| Literal Type | Syntax | Status |
|--------------|--------|--------|
| Integer | `42`, `-17`, `0x1F` | ✅ decimal and hex |
| Integer (binary) | `0b1010` | ❌ not lexed (use decimal/hex) |
| Float | `3.14`, `-0.5`, `1e-6` | ✅ |
| Boolean | `true`, `false` | ✅ |
| String | `"hello"`, `"line\n"` | ✅ |
| Array | `[1, 2, 3]` | ✅ |
| Struct | `Point { x: 1.0, y: 2.0 }` | ✅ |

### 1.4 Comments

```flow
# Single-line comment (hash style)
// Single-line comment (C style) - NOT SUPPORTED
/* Block comment */ - NOT SUPPORTED
```

Status: ✅ Hash comments only

---

## 2. Types

### 2.1 Primitive Types

| Type | Size | Description | Status |
|------|------|-------------|--------|
| `i8` | 1 byte | Signed 8-bit integer | ✅ |
| `i16` | 2 bytes | Signed 16-bit integer | ✅ |
| `i32` | 4 bytes | Signed 32-bit integer | ✅ |
| `i64` | 8 bytes | Signed 64-bit integer | ✅ |
| `i128` | 16 bytes | Signed 128-bit integer | ✅ (C backend emits `__int128`; literals wider than 64 bits are composed from halves) |
| `u8` | 1 byte | Unsigned 8-bit integer | ✅ |
| `u16` | 2 bytes | Unsigned 16-bit integer | ✅ |
| `u32` | 4 bytes | Unsigned 32-bit integer | ✅ |
| `u64` | 8 bytes | Unsigned 64-bit integer | ✅ |
| `u128` | 16 bytes | Unsigned 128-bit integer | ✅ (C backend emits `unsigned __int128`; MLIR backend unsupported) |
| `f32` | 4 bytes | IEEE 754 single precision | ✅ |
| `f64` | 8 bytes | IEEE 754 double precision | ✅ |
| `bool` | 1 byte | Boolean true/false | ✅ |
| `void` | 0 bytes | No value | ✅ |
| `string` | ptr | String literal (const char*) | ✅ |

#### Float comparison: two relations

`f32` and `f64` have two distinct comparison relations, and which one applies
depends on the operation.

| Operation | Relation | NaN | `-0.0` vs `+0.0` | Status |
|-----------|----------|-----|------------------|--------|
| `<` `>` `<=` `>=` `==` `!=` | IEEE 754 | Every comparison is false, `x == x` is false | Equal | ✅ |
| `\|> sort`, `sortBy`, `sort unique`, `\|> find` | IEEE 754-2008 totalOrder (clause 5.10) | Ordered by sign then payload: `-NaN` first, `+NaN` last | `-0.0` sorts strictly before `+0.0` | ✅ |

Arithmetic keeps IEEE semantics unchanged. Ordering needs a relation that is
reflexive, antisymmetric and transitive, which IEEE comparison is not, so
declarative ordering uses totalOrder:

```
-NaN < -inf < ... < -0.0 < +0.0 < ... < +inf < +NaN
```

`sort unique` compacts elements the *ordering* calls equal, so for floats that
is bitwise equality: two NaNs with the same payload collapse to one, and
`-0.0` and `+0.0` both survive.

Rationale, alternatives considered, and the implementation are in
[ordering.md](language/ordering.md). Tests: `tests/lang/test_sort_nan.flow`.

### 2.2 Composite Types

| Type | Syntax | Status |
|------|--------|--------|
| Array (dynamic) | `array<T>` | ✅ |
| Array (fixed) | `array<T, N>` | ✅ |
| Pointer | `ptr<T>` | ✅ |
| Struct | `struct Name { ... }` | ✅ |
| Vector (SIMD) | `vec<T, N>` | ⚠️ (parsed, limited codegen) |
| Span (immutable view) | `span<T>`, `&[T]` | ✅ concrete element types — [spans.md](language/spans.md) |
| Span (mutable view) | `span<mut T>`, `&mut [T]` | ✅ concrete element types |
| Span (static extent) | `span<T, N>`, `&[T; N]` | ✅ length checked at the call site |
| Span (inferred) | `span`, `span<mut>`, `span<number>` | ❌ layer 2 — parser reports "not yet implemented" |

### 2.3 Type Syntax

```flow
# Basic type annotation
let x: i32 = 42

# Array types
let arr: array<i32> = [1, 2, 3]
let fixed: array<f32, 4> = [1.0, 2.0, 3.0, 4.0]

# Pointer types
let p: ptr<i32> = &x

# Nested types
let matrix: array<array<f32>> = ...

# Borrowed views (spans). Both spellings are the same type.
function analyse(samples: span<f32>) -> f32
function analyse(samples: &[f32]) -> f32
function clear(samples: span<mut f32>)
function fft(frame: &[f32; 1024])

# Contiguous sources borrow implicitly; a slice expression produces a span.
let window: span<f32> = signal[128..256]
analyse(signal)
analyse(signal[0..64])
```

### 2.4 Type Aliases and Distinct Types

Flow supports two modern type declaration forms:

```flow
# Transparent alias (structural)
type Bytes = array<u8>

# Distinct (nominal) type
distinct type UserId = i64
```

- **Type aliases** are transparent and interchangeable with their base type.
- **Distinct types** are nominal and incompatible with their base type unless explicitly cast.

### 2.5 Explicit Casts

Use `as` to convert between compatible types (including to/from distinct types):

```flow
let raw: i64 = 42
let id: UserId = raw as UserId
let back: i64 = id as i64
```

### 2.6 Units of Measure

**Status:** ✅ Shipped (dimensional analysis at check time; erase to `f64` / `typedef double` at runtime)

A `unit` declaration creates a numeric type that carries a physical dimension:

```flow
unit Meter
unit Second
unit Velocity = Meter / Second
unit Accel    = Meter / Second^2
unit Hertz    = 1 / Second

let d: Meter  = 100.0 as Meter
let t: Second = 8.0 as Second
let v: Velocity = d / t
```

- Bare `unit Name` declares a base dimension; `unit Name = expr` derives via `*`, `/`, and integer `^`.
- Literals take a unit with `as`. Addition/subtraction require matching dimensions; `*`/`/` compose them.
- `Radian` may pass through trig builtins as dimensionless.
- Focused write-up: [types.md — Units](language/types.md); example: `examples/evolution/units_kinematics.flow`; design: [north-star.md](vision/north-star.md).

---

## 3. Declarations

### 3.1 Function Declaration

**Grammar:**
```
function_decl := 'function' IDENTIFIER '(' parameters? ')' ('->' type)? block
parameters := parameter (',' parameter)*
parameter := IDENTIFIER ':' type
```

**Status:** ✅ Fully implemented

**Example:**
```flow
function add(a: i32, b: i32) -> i32 {
    return a + b
}

function greet(name: string) -> void {
    printf("Hello, %s!\n", name)
}
```

### 3.1.1 Function Guards (Build Modes)

Flow supports lightweight build guards to include/exclude functions per mode:

```flow
@only(hot)
function dev_overlay() -> void { ... }

@guard(jit, compile)
function shared_path() -> void { ... }

@compile
function release_only() -> void { ... }
```

Modes are resolved by the transpiler:
- `compile` (default)
- `jit`
- `hot`
- `mlir`, `c`

Use `--mode` in the CLI to override mode detection when needed.

### 3.2 Variable Declaration

**Grammar:**
```
var_decl := 'let' 'mut'? IDENTIFIER (':' type)? '=' expression
```

**Status:** ✅ Fully implemented (type annotation optional with inference; `mut` for mutation)

**Example:**
```flow
let x: i32 = 42          # Immutable
let mut counter: i32 = 0 # Mutable
let y = 3.14             # Inferred as f32
let name = "Alice"       # Inferred as string
```

### 3.3 Constant Declaration

**Grammar:**
```
const_decl := 'const' IDENTIFIER ':' type '=' expression
```

**Status:** ✅ Fully implemented

**Example:**
```flow
const PI: f32 = 3.14159
const MAX_SIZE: i32 = 1024
```

### 3.3.1 Module Statics

**Grammar:**
```
static_decl := 'let' 'mut' IDENTIFIER ':' type '=' expression
```

A top-level `let mut` declares module-level mutable state. Functions in the
same module read and write it like a normal variable. The type annotation is
required and the initializer must be a compile-time constant.

Allowed types: primitives (`i32`/`i64`/`u8`/`u32`/`f32`/`f64`/`bool`), fixed
arrays of primitives (`array<T, N>` with a full literal initializer), and
`ptr<T>` initialized to `null`. Anything else is a type error.

**Status:** ✅ C backend. The MLIR backend reports "module statics not yet
supported in MLIR backend" instead of compiling them.

**Example:**
```flow
let mut counter: i32 = 0
let mut table: array<i32, 4> = [0, 0, 0, 0]
let mut head: ptr<Node> = null

function bump() -> i32 {
    counter = counter + 1
    return counter
}
```

**C lowering:** always a file-scope `static`, so each translation unit keeps
its statics private. Arrays lower to C static arrays with brace initializers;
an all-zero array literal lowers to `{0}`. A top-level `let` without `mut` is
a syntax error; use `const` for immutable module-level values.

### 3.4 Struct Declaration

**Grammar:**
```
struct_decl := 'struct' IDENTIFIER '{' (field (',' field)*)? '}'
field := IDENTIFIER ':' type
```

**Status:** ✅ Fully implemented

**Example:**
```flow
struct Point {
    x: f32,
    y: f32
}

struct Rectangle {
    origin: Point,
    width: f32,
    height: f32
}
```

### 3.5 Extern Declaration

**Grammar:**
```
extern_decl := 'extern' STRING? '{' function_signature* '}'
function_signature := 'function' IDENTIFIER '(' parameters? ')' ('->' type)?
```

**Status:** ✅ Fully implemented

**Example:**
```flow
extern "C" {
    function malloc(size: i32) -> ptr<void>
    function free(ptr: ptr<void>) -> void
}
```

### 3.6 Attributes

An attribute is written `@name` or `@name(arg, …)` immediately before a
`function` declaration. Several may be stacked. The full vocabulary lives in
`src/flow/attributes.py`. A name outside it is a type error, so a misspelled
attribute gets reported.

```flow
@always_inline
@target("avx2")
function dot4(a: ptr<f32>, b: ptr<f32>) -> f32 { ... }
```

| Attribute | Status | Notes |
|-----------|--------|-------|
| `@only` / `@guard` | ✅ | Build-mode guards (§3.1.1) |
| `@rt_safe` | ✅ | Real-time safety annotation — see [rt-safety.md](library/rt-safety.md) |
| `@flow_api` | ✅ | Keep the plain, unmangled name for a stable C ABI |
| `@gpu` | ✅ | Device code generation |
| `@inline` | ✅ | Inline hint (below) |
| `@noinline` | ✅ | Inline barrier (below) |
| `@always_inline` | ✅ | Forced inline (below) |
| `@target("…")` | ✅ | Per-function C target features (below) |

#### Code-generation attributes

These four change the C the backend emits. The specifier appears on both the
forward declaration and the definition, so the two always agree.

| Flow | Emitted C |
|------|-----------|
| `@inline` | `static inline int32_t add_i32_i32(int32_t a, int32_t b)` |
| `@noinline` | `__attribute__((noinline)) int32_t sub_i32_i32(int32_t a, int32_t b)` |
| `@always_inline` | `__attribute__((always_inline)) static inline int32_t mul_i32_i32(int32_t a, int32_t b)` |
| `@target("crypto")` | `__attribute__((target("crypto"))) int32_t bump_i32(int32_t a)` |

Caveats worth knowing before you reach for them:

- **`@inline` is a hint.** The C compiler decides. At `-O0` nothing is inlined;
  at `-O2` a small function is usually inlined with or without the attribute.
- **`@inline` and `@always_inline` add `static`.** That is what makes the
  inline definition self-contained. Some symbols have to stay visible to
  another object file: `main`, an `export function`, a `@flow_api` function,
  and anything in a `--library` build. For those the backend emits C99
  `extern inline`, which keeps the external definition and the hint.
- **`@always_inline` is honored at every optimization level,** including
  `-O0`. If the compiler cannot inline the call, it reports an error.
- **`@always_inline` combined with `@target(…)` usually fails to build.** A
  caller without the named features cannot absorb a body that requires them,
  and clang says so. Flow emits both attributes as written and lets the C
  compiler make the call.
- **`@noinline` cannot be combined with `@inline` or `@always_inline`;** the
  type checker rejects the pair.
- **`@target` is platform-specific and unverified at compile time.** Flow
  checks only the string's shape: comma-separated items, each a bare feature
  (`avx2`, `crypto`), a signed feature (`+avx2`, `-sse`, `no-sse`) or a
  `key=value` pair (`arch=haswell`, `tune=native`,
  `branch-protection=standard`). Whether those features exist is decided by the
  host C compiler for the machine it is targeting. Clang warns on an
  unrecognized feature and ignores it, so an x86 target string still compiles
  on arm64 and does nothing there.
- **Attributes on `extern` and forward declarations are dropped.** There is no
  body in that translation unit, so an inline specifier would promise a
  definition the backend never emits.
- None of these change what a program computes. They only steer the C
  compiler.

#### 3.6.1 Debug and test helpers

`dbg`, `expect` and `test` are keywords, and their support genuinely differs
by backend. What each one does today:

| Form | C backend | MLIR backend | JS backend |
|------|-----------|--------------|------------|
| `dbg <expr>` | Evaluates `<expr>` once, writes `dbg: <value>` to stderr, yields the value | Lowers to `<expr>`; no printing | Not supported |
| `expect <cond>` | `if (!cond) { fprintf(stderr, "expect failed (line N)"); exit(1); }` | Emits the condition for its side effects; no abort | Not supported |
| `test "name" { … }` | Becomes `bool test_name(void)` in the output | Same function, same non-use | Not supported |

The Python packaging target goes through the C backend, so it inherits the C
behaviour. `expect` requires a `bool` condition in every backend; that check is
in the type checker.

`test` blocks are the honest gap. A block parses into an ordinary
`bool`-returning function carrying the `test` attribute, and nothing calls it:
no backend emits a driver and no harness collects it. A failing body is never
reached. Flow's own test suites are `tests/lang/*.flow` programs run by
`./flow test-lang`, where `main` returns 0 on success and a distinct nonzero
code per failing check.

Enums (`enum`), traits (`trait` / `impl`), and `flow` / `unit` declarations are covered in §1.1 and §10; full field grammars live in the focused pages and EBNF.

---

## 4. Expressions

### 4.1 Expression Types

| Expression | Syntax | Status |
|------------|--------|--------|
| Literal | `42`, `3.14`, `"str"`, `true` | ✅ |
| Variable | `x`, `name` | ✅ |
| Binary Op | `a + b`, `x && y` | ✅ |
| Unary Op | `-x`, `!flag` | ✅ |
| Function Call | `foo(a, b)` | ✅ |
| Effect Call | `Effect.method(args)` | ✅ |
| Field Access | `point.x` | ✅ |
| Array Access | `arr[i]` | ✅ |
| Array Literal | `[1, 2, 3]` | ✅ |
| Struct Literal | `Point { x: 1.0, y: 2.0 }` | ✅ |
| Vector Literal | `<1.0, 2.0, 3.0, 4.0>` | ⚠️ |
| Lambda | `\|x: i32\| -> i32 { x + n }` | ✅ |
| If-expression | `if cond { a } else { b }` | ✅ |

### 4.2 Operator Precedence (highest to lowest)

1. `()` Parentheses
2. `.` `[]` Field/Array access
3. `!` `-` (unary) Unary operators
4. `*` `/` `%` Multiplicative
5. `+` `-` Additive
6. `<` `>` `<=` `>=` Relational
7. `==` `!=` Equality
8. `&&` Logical AND
9. `||` Logical OR

### 4.3 Built-in Functions

| Function | Signature | Status |
|----------|-----------|--------|
| `printf` | `(format: string, ...) -> i32` | ✅ |
| `print` | `(msg: string) -> void` | ✅ |
| `length` | `(arr: array<T>) -> i32` | ✅ |
| `sqrt` | `(x: f32) -> f32` | ✅ |
| `sin` | `(x: f32) -> f32` | ✅ |
| `cos` | `(x: f32) -> f32` | ✅ |
| `abs` | `(x: i32) -> i32` | ✅ |
| `min` | `(a: T, b: T) -> T` | ✅ |
| `max` | `(a: T, b: T) -> T` | ✅ |
| `sum` | `(range) -> i32` | ✅ |

`sum` takes a range rather than a value: `sum(0..1000 step 3)`. It applies the
closed form for an arithmetic progression, so it does not iterate. Inside
`sum(...)`, `|` and `&` between two ranges mean union and intersection instead
of the bitwise operators. See [Ranges and range algebra](language/ranges.md).

### 4.4 Lambdas / Closures

Pipe-lambda syntax captures free local variables **by value** at creation
time (snapshot semantics). The C backend lowers capturing lambdas to a
`{ fn, env }` closure struct; non-capturing lambdas remain C function
pointers.

```flow
let n: i32 = 5
let add_n: (i32) -> i32 = |x: i32| -> i32 { return x + n }
let result: i32 = add_n(10)  # 15
```

**Status notes:**
- Automatic free-variable capture is implemented (C backend).
- Escaping HOF ABI: declare `(T) -> R` (fat pointer `{fn, env}`); capturing
  lambdas heap-copy their env so they can be returned or passed to HOFs.
- Prefer `|params| -> Ret { … }` over the older manual
  `struct + self` closure idiom.

### 4.5 Pipe / Declarative Ordering and Search

**Status:** ✅

```flow
let ys = xs |> sort
let zs = xs |> sortBy [asc .key, desc .tie]
let i  = xs |> find(target)     # index of the first match, or -1
```

These name an intent. The compiler picks the implementation from a registry
of lowerings with cost models and applicability predicates.

| Surface | Meaning | Status |
|---------|---------|--------|
| `\|> sort`, `sort by`, `sortBy`, `descending`, `unique` | Order, in place, on `array<T, N>` | ✅ |
| `\|> find(t)` | First index equal to `t` under the same total order, else `-1` | ✅ |
| Plan selection (6 sort plans, 2 search plans) | Cheapest applicable, with a scratch budget | ✅ |
| Ordering hints (sortedness, integer range) through straight-line code | Skip-sort, reverse-only, counting sort, binary search | ✅ |
| `adaptive`, `general` | Shift the run estimate; pin the general plan | ✅ |
| `stable` / `unstable` | Parsed; every plan is stable today, so `unstable` buys nothing | ⚠️ |
| `with entropy`, `parallel`, `gpu`, `simd`, `compact`, … | Parsed, no specialization | ⚠️ |
| `--explain` / `flow explain` | Print the plan, the costs, and every failed constraint | ✅ |

### 4.6 If-expressions

Value-producing conditionals (issue #252):

```flow
let x: i32 = if n > 0 { n } else { -n }
```

- Arms are **expressions** (not statement blocks).
- `else` is **required**.
- Lowers to a C ternary / MLIR `scf.if` with a value.

See [ordering.md](language/ordering.md),
[explainable-compilation.md](language/explainable-compilation.md), and
`examples/basics/declarative_sort.flow`.

**Related (library, not core syntax):** Dual / Tensor arithmetic overloads (`+ - * /`, scale, add_scalar) are implemented in the C generator + stdlib — see pattern-adoption notes and `examples/ml/autodiff/tensor_ops.flow`.

---

## 5. Statements

### 5.1 Statement Types

| Statement | Status |
|-----------|--------|
| Variable Declaration | ✅ (`let` / `let mut`) |
| Assignment | ✅ |
| Return | ✅ |
| If/Elif/Else | ✅ |
| While Loop | ✅ |
| For Loop | ✅ (`to` preferred; `..` alias) |
| `break` / `continue` | ✅ |
| `defer` | ✅ |
| Handle Statement | ✅ |
| Match Statement | ⚠️ (literals/structs/guards/`\|`/nested-literal fields/struct-in-struct patterns work; exhaustiveness is real for `bool` and enum/ADT variants via path/const patterns, minimal stub for plain integers) |
| Expression Statement | ✅ |

### 5.2 If Statement

**Grammar:**
```
if_stmt := 'if' expression block ('elif' expression block)* ('else' block)?
block := '{' statement* '}'
```

**Status:** ✅ Fully implemented

**Example:**
```flow
if x > 0 {
    printf("Positive\n")
} elif x < 0 {
    printf("Negative\n")
} else {
    printf("Zero\n")
}
```

### 5.3 While Loop

**Grammar:**
```
while_stmt := 'while' expression block
```

**Status:** ✅ Fully implemented

**Example:**
```flow
let i: i32 = 0
while i < 10 {
    printf("%d\n", i)
    i = i + 1
}
```

### 5.4 For Loop

**Grammar:**
```
for_stmt := 'parallel'? 'for' IDENTIFIER 'in' expression ('..' | 'to') expression
            ('step' expression)? block
```

**Status:** ✅ Fully implemented. Prefix `parallel for` emits
`#pragma omp parallel for` under `#ifdef _OPENMP` in the C backend;
`./flow` passes `-fopenmp` when the toolchain supports it, otherwise the
loop is correct and serial. See [concurrency-vs-go.md](language/concurrency-vs-go.md).

**Example:**
```flow
# Basic for loop (both `to` and `..` are accepted)
for i in 0 to 10 {
    printf("%d\n", i)
}

# With step
for i in 0 to 100 step 5 {
    printf("%d\n", i)
}

# Data-parallel (OpenMP when available)
parallel for i in 0 to 1000 {
    data[i] = i * 2
}
```

### 5.5 Return Statement

**Grammar:**
```
return_stmt := 'return' expression?
```

**Status:** ✅ Fully implemented

### 5.6 Concurrency (language + stdlib)

There is **no** language-level `go` / `select` / `async` keyword. Concurrency
surfaces as:

| Surface | Where | Notes |
|---------|-------|-------|
| `parallel for` | Language (§5.4) | OpenMP when available |
| Channels, WaitGroup, mutex, threads | `lib/stdlib/concurrent.flow` | `channel_i32_select2` and `channel_i32_select4` |
| `Async` / `AsyncIO` effects | `lib/stdlib/async.flow` | `FiberAsync` (M:N), `ThreadedAsync`, `NetpollAsyncIO` |

Design + measured Go comparison: [language/concurrency-vs-go.md](language/concurrency-vs-go.md).
Async honesty: [language/async-effects.md](language/async-effects.md).

---

## 6. Effect System

The effect system provides capability-based side effect management through algebraic effects.

### 6.1 Effect Declaration

**Grammar:**
```
effect_decl := 'effect' IDENTIFIER '{' effect_operation* '}'
effect_operation := IDENTIFIER '(' parameters? ')' '->' type ','
```

**Status:** ✅ Fully implemented

**Example:**
```flow
effect Log {
    emit(message: string) -> void,
    level(lvl: i32) -> void,
}

effect FileSystem {
    read(path: string) -> string,
    write(path: string, content: string) -> void,
}
```

### 6.2 Capability Declaration

**Grammar:**
```
capability_decl := 'capability' IDENTIFIER '{' 'effect' IDENTIFIER ',' method* '}'
method := 'function' IDENTIFIER '(' parameters? ')' '->' type block
```

**Status:** ✅ Fully implemented

**Example:**
```flow
capability ConsoleLogger {
    effect Log,
    
    function emit(message: string) -> void {
        printf("%s\n", message)
    },
    
    function level(lvl: i32) -> void {
        printf("Log level: %d\n", lvl)
    },
}
```

### 6.3 Handle Statement

**Grammar:**
```
handle_stmt := 'handle' IDENTIFIER (',' IDENTIFIER)* 'with' IDENTIFIER (',' IDENTIFIER)* block
```

**Status:** ✅ Fully implemented with runtime dispatch (multi-effect /
multi-handler forms supported)

**Example:**
```flow
function main() -> i32 {
    handle Log with ConsoleLogger {
        Log.emit("Hello from effects!")
        Log.level(3)
    }
    # Multi-effect install (one capability may cover several effects)
    handle Log, Notify with ConsoleLogger, ConsoleNotifier {
        place_order()
    }
    return 0
}
```

### 6.3.1 Signature Effect Rows

**Grammar (function declaration):**
```
function_decl := 'function' IDENTIFIER '(' parameters? ')' '->' type
                 ('with' IDENTIFIER (',' IDENTIFIER)*)? block
```

**Status:** ✅ Implemented (enforced under `--strict-effects` or
`FLOW_STRICT_EFFECTS=1`)

A `with E1, E2` clause declares effects the function may perform. The body may
use those effects without a local `handle`. Callers must cover the row via an
enclosing `handle` or their own `with` clause. Soft zero defaults remain when
`--strict-effects` is omitted. First-class types carry the same clause:
`(string) -> void with Log`. See `examples/effects/effect_rows.flow` and
[effects-showcase.md](effects-showcase.md).

**Example:**
```flow
function greet(name: string) -> void with Log {
    Log.emit(name)
}

let f: (string) -> void with Log = greet
```

### 6.4 Effect Implementation Details

Effects are implemented via vtable-based runtime dispatch:

1. Each effect generates a C struct for the handler vtable
2. A `_Thread_local` pointer tracks the current handler for each effect
   (safe across OS threads / `parallel for`)
3. `handle` blocks save/restore the handler pointer
4. Effect calls dispatch through the current handler's vtable

---

## 7. Module System

### 7.1 Import Declaration

**Grammar:**
```
import_decl := 'import' STRING
             | 'import' module_path ('{' symbols '}')?
             | 'import' module_path 'as' IDENTIFIER
```

**Status:** ✅ Dot-path imports + legacy string imports both work.
Prefer named modules; see [language/modules.md](language/modules.md).

**Example:**
```flow ignore="catalogue of import forms over illustrative module names"
import "lib/stdlib/math.flow"          # legacy string path
import std.math { sin, cos }           # named module + symbols
import verify.nat as nat               # aliased module
```

### 7.2 Export Declaration

**Grammar:**
```
export_decl := 'export' (function_decl | struct_decl | enum_decl | const_decl
                        | type_decl | distinct_decl | effect_decl
                        | capability_decl | theorem_decl)
             | 'export' IDENTIFIER (',' IDENTIFIER)*
```

**Status:** ✅ Fully implemented

**Example:**
```flow
export function add(a: i32, b: i32) -> i32 {
    return a + b
}

export struct Point {
    x: f32,
    y: f32
}

# File-level list form
function greet() -> i32 { return 1 }
export greet
```

### 7.3 Re-export Declaration

**Grammar:**
```
reexport_decl := 'export' 'import' module_path ('{' symbols '}')?
```

**Status:** ✅ Implemented (Python host)

`export import M` makes every symbol `M` exports an export of the current file
as well. `export import M { a, b }` forwards only the named symbols, which must
be exported by `M`. A package's `lib.flow` can therefore aggregate its
submodules under one name.

```flow ignore="relative-import form; the sibling module is illustrative"
# registry/packages/flowlm/src/lib.flow
export import .util
export import .model
export import .train { flm_train_step, flm_sample }
```

```flow ignore="flowlm is a registry package, not vendored here"
# consumer
import flowlm.lib { flm_model_init, flm_forward, flm_train_step }
```

Rules:

- Forwarding binds the declaring module's symbol. The declaration is emitted
  once no matter how many modules forward it.
- Re-exports chain: forwarding a module also forwards what that module
  forwarded.
- `export import M as name` is rejected. Re-export forwards symbols; use a
  plain `import ... as` for an alias.
- A forwarded name that collides with another exported declaration, or with a
  declaration in the forwarding file, is an error naming both source modules.

The self-hosted `flowc` parser does not accept `export import` yet.

### 7.4 Module Resolution

Import paths are resolved relative to:
1. Current file's directory
2. Project root
3. `lib/stdlib/` directory

### 7.5 `module` Blocks

`module X { ... }` is parsed and then flattened. The block name is discarded
and its declarations become globals, so `module` groups source text without
creating a namespace. See
[language/modules-namespacing.md](language/modules-namespacing.md) for the
current behavior, the collisions it allows, and what a real namespace would
cost.

---

## 8. Memory Model

### 8.1 Value Semantics

- Primitives: Pass by value (copied)
- Structs: Pass by value (deep copy)
- Arrays: Pass by reference (pointer semantics)
- Strings: Immutable, pass by pointer

### 8.2 Stack vs Heap

| Type | Allocation |
|------|------------|
| Primitives | Stack |
| Small structs | Stack |
| Fixed arrays | Stack |
| Dynamic arrays | Heap (via malloc) |
| Strings | Static data section |

### 8.3 Pointer Operations

```flow
let x: i32 = 42
let p: ptr<i32> = &x       # Address-of
let val: i32 = *p          # Dereference
# Postfix chaining (field through index) is supported on the C backend:
#   cells[i].field   /   ptr[0].field
```

**Status:** ✅ Address-of, dereference, and `ptr[i].field` / postfix chaining on the C backend.
Example: `tests/runtime/test_pointers.flow`.

### 8.4 Lifetime Domains

Where a value lives is a second question from where the allocator put it. A
lifetime domain names how long it lives. Full description:
[lifetime-domains.md](language/lifetime-domains.md).

```text
callback  <  frame  <  session  <  application
```

`@lifetime(D)` goes on a function, where it declares the domain the frame runs
in, and on a module static, where it declares the domain of that storage
(default `application`). It is the only attribute allowed on a static. A value
takes its domain from its allocation site: a local belongs to the enclosing
function's domain, a static to its own.

```flow
@lifetime(application)
let mut tail: span<f32> = null

@lifetime(session)
function setup() -> FrameArena { return frame_arena_create(1 << 16) }

@lifetime(frame)
function build(f: ptr<FrameArena>, n: i64) -> ptr<f32> {
    frame_begin(f)
    return frame_alloc_f32(f, n)
}

@lifetime(callback)
function process(input: span<f32>) -> f32 { return input[0] }
```

Four rules are checked, each an error in `--strict` and a warning in
`--lenient`:

| Rule | What it rejects |
|---|---|
| LD1 | storing a reference rooted in local storage into a static of a longer-lived domain |
| LD2 | returning a reference into the annotated function's own frame |
| LD3 | allocation: `callback` is `@rt_safe`; `frame` forbids heap create/destroy but allows bumping an arena |
| LD4 | calling a function whose declared domain outlives the caller's |

Domains are opt-in. An unannotated function has no domain and no rule fires
inside it. The annotation is erased after checking: every domain lowers to the
same C.

**Not checked** (documented rather than half-enforced): escape through a call,
a struct field, a closure, or heap storage; the domain of arena-allocated
memory; domains on parameters or in types.

**Status:** ✅ C-backend type checker. Tests: `tests/unit/test_lifetime_domains.py`,
`tests/lang/test_lifetime_domains.flow`. Example:
`examples/audio/lifetime_domains.flow`.

---

## 9. Compilation Targets

### 9.1 C Backend

**Status:** ✅ Primary backend, fully functional

- Generates portable C99 code
- Full effect system support via vtables
- All control flow constructs
- Struct and array support

### 9.2 MLIR Backend

**Status:** ⚠️ Functional; control flow and arrays match the C backend, effects do not

- Functions, structs, arrays, if/else, while, for (`to` / `..` / `step`),
  `match`, `break` / `continue` / `defer` all lower and execute with the same
  exit code as the C backend. `tests/unit/test_backend_parity.py` runs the
  same programs through both and compares.
- Loops and matches with their own control flow lower to the `cf` dialect
  with block arguments carrying the merged locals; simple counted loops stay
  on `scf.for` so the elementwise vectorizer can rewrite them to
  `vector.transfer_read` / `vector.transfer_write` at VF=4.
- Effects, capabilities and `handle` are partial; module statics are
  unsupported and raise.
- Full CLI pass toggles + `--print-pass-pipeline`: see [mlir-opt-flags.md](language/mlir-opt-flags.md)

### 9.3 WebAssembly

**Status:** ✅ Via Emscripten — C or MLIR CPU backends — see [language/wasm.md](language/wasm.md)

- Paths: Flow → C → `emcc`, or Flow → MLIR → LLVM IR → `emcc`
  (`./flow wasm --backend=c|mlir`, default `c`)
- Gfx canvas games link `runtime/gfx_wasm.c` + `-sASYNCIFY` on both backends
  (smoke: `examples/games/snake_gfx.flow --backend=mlir`)
- `--preload HOST@/vfs` → `emcc --preload-file` + `FORCE_FILESYSTEM` (both backends)
- `--link PATH` for extra runtime C (e.g. `runtime/flow_rt_support.c`); Cocoa `.m` skipped
- Doom-scale knobs: `--initial-memory`, `--asyncify-stack-size`, `--emcc-flag`
- `--fs` / `--threads` crossings remain C-only today
- Requires Emscripten locally; not required for all CI jobs
- No direct WASM emission; native Flow-in-WASM compiler deferred

### 9.4 JIT Execution

**Status:** ✅ MLIR JIT via `flow jit` (requires LLVM/MLIR toolchain)

- Pipeline: Flow → MLIR → `mlir-opt` → `mlir-translate` → LLVM IR → `clang -shared` → in-memory execution via `ctypes`
- Commands: `flow jit <file>`, `transpiler --jit`, `transpiler --hot-reload`
- Hot reload watches `.flow` files and re-JITs on save (`FlowJITRunner` + `MLIRJIT`)
- Fallback: `flow run` uses the portable C backend (not JIT)

**Requirements:** `mlir-opt`, `mlir-translate`, and `clang` on `PATH` (e.g. `brew install llvm` on macOS)

**Related (AOT, not in-memory JIT):** `flow mlir-run` lowers MLIR → LLVM object file → links and runs

---

## 10. Domain / DSL Surfaces

These are first-class language / pre-parse surfaces shipped alongside the core grammar. Status is relative to the Python host (`FLOW_HOST=python`) unless noted. Stage-A `flowc` covers a subset (see [self-hosting.md](project/self-hosting.md)).

### 10.1 `flow` / `evolves as` / representation

**Status:** ✅

Plant-style evolution blocks: `state` / `param` / `solver` (`rk4` and friends), `every`, `when` / `reaches` / `becomes`, and `represent phase_portrait {…}` (emits `{Name}_portrait_frame`).

- Design cards: [north-star.md](vision/north-star.md)
- Checklist: [pattern-adoption.md](project/pattern-adoption.md)
- Examples under `examples/evolution/` and `examples/compilers/`

### 10.2 Dynamics / `analyze` / LQR

**Status:** ✅ (pre-parse expander)

Legacy `dsys` / `dynamics { }` and vision-form `analyze plant { lqr { Q… R… → k… } }` (diagonal Q, scalar R, `n ≤ 8`) expand to Flow + helpers such as `dlqr_diag_q_scalar_u`.

- [dynamics-dsl.md](language/dynamics-dsl.md)
- Examples: `examples/control/spring_mass_lqr.flow`, `chain4_lqr.flow`

### 10.3 `field` / `boundary` / Laplacian PDE

**Status:** ✅ (Stage-1 expander in `field_dsl.py`)

`field` / `boundary` / `evolves as laplacian` → `T_field_step` helpers. Heat demo and pattern-adoption #163.

### 10.4 Fill shaders

**Status:** ✅ Metal on macOS (`shader fill` + `./flow shader`)

- [shaders.md](language/shaders.md)

### 10.5 Native graphics

**Status:** ✅ macOS Cocoa; Linux/Windows SDL2 (+ stub without headers)

- [graphics.md](language/graphics.md)
- `./flow gfx`

### 10.6 GPU memory (stdlib)

**Status:** ✅ Metal path; stub elsewhere — [gpu-memory.md](library/gpu-memory.md)

CUDA/OpenCL backends are **not** shipping.

### 10.7 Recording and GIF output

**Status:** ✅ (headless recorder + pure-Flow stdlib encoder)

Two shipped surfaces for turning Flow programs into images and animations.

**Headless recorder.** `./flow record <program.flow>` builds a gfx program
against the recording backend and runs it without a window, writing numbered
P6 PPM frames. The recorder logic itself is Flow (`lib/runtime/gfx_record.flow`);
`runtime/gfx_record.c` keeps only the `flow_gfx_*` ABI table and framebuffer.
Environment contract:

| Variable | Meaning | Default |
|----------|---------|---------|
| `FLOW_GFX_RECORD_DIR` | output directory for frames | `./frames` |
| `FLOW_GFX_RECORD_FRAMES` | stop after N presented frames | `240` |
| `FLOW_GFX_RECORD_SKIP` | keep every Nth frame | `1` |
| `FLOW_GFX_RECORD_KEYS` | scripted input windows, `first-last:keycode` CSV | none |

**Stdlib GIF encoder.** `lib/stdlib/gif.flow` is a GIF89a animated encoder in
pure Flow: fixed 256-entry palette (6x7x6 RGB cube plus 4 grays), correct
GIF-variant LZW (9 to 12 bit codes, clear/EOI, 4096-entry dictionary,
255-byte sub-blocks), and a NETSCAPE2.0 infinite-loop extension. Only libc
`fopen`/`fwrite`/`fputc`/`fclose` and `malloc`/`free` cross the FFI line.
Open-file state is held in module statics (section 3.3.1).

```flow
import stdlib.gif { gif_begin, gif_add_frame_rgb, gif_end }

function main() -> i32 {
    gif_begin("out.gif", 128, 128, 5)   # 5 cs/frame, loops forever
    gif_add_frame_rgb(pixels, 128, 128) # RGB24, row-major
    gif_end()
    return 0
}
```

- Example: `examples/graphics/gif_writer.flow` (24-frame animation)
- Tests: `tests/lang/test_gif_encoder.flow`, `tests/unit/test_gif_flow_encoder.py`
  (Pillow decodes the output as ground truth)

---

## Appendix A: AST Node Reference

Complete list of AST nodes defined in `src/flow/parser.py`:

| Node | Purpose | Fields |
|------|---------|--------|
| `Token` | Lexer token | type, value, line, column |
| `Type` | Type annotation | name, is_pointer, is_reference, size, element_type |
| `Parameter` | Function parameter | name, type |
| `FunctionDecl` | Function definition | name, parameters, return_type, body, effects |
| `VarDecl` | Variable declaration | name, type, initializer |
| `Block` | Statement block | statements |
| `IfStatement` | Conditional | condition, then_block, elif_blocks, else_block |
| `WhileStatement` | While loop | condition, body |
| `ForStatement` | For loop | variable, range_start, range_end, step, is_parallel, body |
| `ReturnStatement` | Return | value |
| `Assignment` | Assignment | target, target_expr, value |
| `FunctionCall` | Function call | name, arguments |
| `BinaryOperation` | Binary op | operator, left, right |
| `UnaryOperation` | Unary op | operator, operand |
| `Literal` | Literal value | value, type |
| `Variable` | Variable reference | name |
| `StructLiteral` | Struct instantiation | struct_name, fields |
| `FieldAccess` | Field access | object, field |
| `ArrayLiteral` | Array literal | elements |
| `VectorLiteral` | SIMD vector | elements |
| `ArrayAccess` | Array index | array, index |
| `SliceExpr` | Slice / borrow `a[i..j]` | base, start, end |
| `StructDecl` | Struct definition | name, fields |
| `EffectDecl` | Effect definition | name, operations |
| `EffectOperation` | Effect method signature | name, parameters, return_type |
| `CapabilityDecl` | Capability definition | name, effect, methods |
| `CapabilityMethod` | Capability method | name, parameters, return_type, body |
| `EffectCall` | Effect method call | effect, operation, arguments |
| `HandleStatement` | Handle block | effect, handler, body |
| `MatchStatement` | Match expression | value, cases |
| `MatchCase` | Match case | pattern, body, guard |
| `StructPattern` | Struct pattern | struct_name, bindings, field_literals |
| `OrPattern` | `\|`-alternation of literal patterns | patterns |
| `ImportDecl` | Import statement | path |
| `ConstDecl` | Constant declaration | name, type, value |
| `Lambda` | Lambda / closure | parameters, return_type, body, captures |

---

## Appendix B: C Generator Capabilities

Methods in `src/flow/c_generator.py` and their coverage:

| Generator Method | Handles |
|------------------|---------|
| `_gen_function` | Function declarations |
| `_gen_block` | Statement blocks |
| `_gen_statement` | Statement dispatch |
| `_gen_if` | If/elif/else |
| `_gen_while` | While loops |
| `_gen_for` | For loops |
| `_gen_handle` | Effect handle blocks |
| `_gen_expr` | Expression dispatch |
| `_gen_effect_call` | Effect method calls |
| `_gen_array_access` | Array indexing (arrays, pointers, spans) |
| `_gen_span_borrow` | Auto-borrow at call sites; slice lowering |
| `_ensure_span_typedef` | Two-word span view typedefs |
| `_gen_array_literal` | Array literals |
| `_gen_effect_runtime_types` | Effect vtable structs |
| `_gen_capability_method` | Capability method implementations |
| `_gen_effect_vtables` | Vtable initialization |

---

## Appendix C: Feature Implementation Matrix

| Feature | Parser | C Gen | MLIR Gen | Docs |
|---------|--------|-------|----------|------|
| Functions | ✅ | ✅ | ✅ | ✅ |
| Variables (`let` / `mut`) | ✅ | ✅ | ✅ | ✅ |
| Constants | ✅ | ✅ | ✅ | ✅ |
| Structs | ✅ | ✅ | ✅ | ✅ |
| Enums / traits / impl | ✅ | ⚠️ | ⚠️ | ⚠️ |
| Units of measure | ✅ | ✅ | ❌ | ✅ |
| Arrays | ✅ | ✅ | ✅ | ✅ |
| Spans (`span<T>` / `&[T]`, concrete elements) | ✅ | ✅ | ❌ | ✅ |
| Spans (bare `span`, trait-shaped, dependent extents) | ❌ | ❌ | ❌ | ✅ (documented gap) |
| Lifetime domains (`@lifetime(...)`, 4 rules) | ✅ | ✅ (erased) | ✅ (erased) | ✅ |
| If/Else | ✅ | ✅ | ✅ | ✅ |
| While | ✅ | ✅ | ✅ | ✅ |
| For (`to` / `..` / `step`) | ✅ | ✅ | ✅ | ✅ |
| `break` / `continue` / `defer` | ✅ | ✅ | ✅ | ⚠️ |
| Effects | ✅ | ✅ | ⚠️ | ✅ |
| Capabilities | ✅ | ✅ | ⚠️ | ✅ |
| Handle | ✅ | ✅ | ⚠️ | ✅ |
| Import | ✅ | ✅ | ✅ | ✅ |
| Export | ✅ | ✅ | ✅ | ✅ |
| Extern | ✅ | ✅ | ✅ | ⚠️ |
| Match | ✅ | ⚠️ | ✅ | ✅ |
| Parallel | ✅ | ✅ | ⚠️ (scf.parallel, runs serially) | ✅ (OpenMP / serial) |
| SIMD Vec | ✅ | ⚠️ | ⚠️ | ⚠️ |
| Pointers (`&` / `*` / `ptr[i].field`) | ✅ | ✅ | ⚠️ | ✅ |
| Lambdas / captures | ✅ | ✅ | ❌ | ✅ |
| Postfix chaining | ✅ | ✅ | ✅ | ✅ |
| Pipe / `sort` / `sortBy` | ✅ | ✅ | ❌ | ✅ |
| `flow` / evolves / phase_portrait | ✅ | ✅ | ❌ | ✅ |
| Dynamics / LQR / `field` PDE | ✅ (expander) | ✅ | ❌ | ✅ |
| Fill shaders / gfx | ✅ | ✅ | ❌ | ✅ |
| `module` (flatten only) | ✅ | ✅ | ✅ | ⚠️ |
| Binary `0b…` literals | ❌ | ❌ | ❌ | ✅ (documented gap) |
| Dual / Tensor ops | ✅ | ✅ | ⚠️ | ⚠️ |

The MLIR Gen column is measured by execution, not by inspecting the emitted
IR. `tests/unit/test_backend_parity.py` compiles the same program through
both backends and requires the same exit code, and for `defer` and `break`
the same stdout. A row is ✅ only when a parity case covers it.

Known MLIR gaps behind the remaining ⚠️ marks:

- `break` / `continue` inside a `parallel for` body have no legal cf edge out
  of the `scf.parallel` region; the generator raises instead of emitting
  wrong code.
- `parallel for` lowers to `scf.parallel`, which the current pass pipeline
  serializes. Results are correct; there is no parallel execution.

Match stays ⚠️ for C Gen because `break` inside a match arm lowers to a C
`switch`, where `break` leaves the switch rather than the enclosing loop. The
MLIR lowering branches to the loop's exit block and gets this right, so the
two backends disagree on that one shape.

---

*Last updated: 2026-08-06*
*Version: 0.11.1*
