# FLOW Language Specification

> **Version**: 0.2.0
> **Last Updated**: 2026-01-09

## Overview

FLOW is a statically-typed, systems programming language with first-class support for:
- **Algebraic effects** for modular side-effect handling
- **GPU computing** via Metal and CUDA backends
- **Automatic differentiation** for machine learning
- **WebAssembly** compilation for browser deployment

## Quick Reference

### Commands
```bash
flow run <file.flow>      # Compile and run
flow compile <file.flow>  # Compile to executable
flow fmt <file.flow>      # Format source code
flow test                 # Run all tests
```

--- v0.1.0

> **AUTHORITATIVE REFERENCE** — This document is the single source of truth for the FLOW language.
> All other documentation references this spec. Features marked ✅ are implemented, ⚠️ are partial, ❌ are planned.

---

## Table of Contents

1. [Lexical Structure](#1-lexical-structure)
2. [Types](#2-types)
3. [Declarations](#3-declarations)
4. [Expressions](#4-expressions)
5. [Statements](#5-statements)
6. [Effect System](#6-effect-system)
7. [Module System](#7-module-system)
8. [Memory Model](#8-memory-model)
9. [Compilation Targets](#9-compilation-targets)

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
| `parallel` | ⚠️ | Control Flow (parsed, not optimized) |
| `step` | ✅ | Control Flow |
| `match` | ⚠️ | Pattern Matching (literals, structs, guards, `\|` alternation, nested literal fields; real exhaustiveness checking for `bool` and enum/ADT variants via path/const patterns, minimal stub for integers) |
| `default` | ✅ | Pattern Matching |
| `inline` | ⚠️ | Optimization Hint (parsed, ignored) |
| `noinline` | ⚠️ | Optimization Hint (parsed, ignored) |
| `always_inline` | ⚠️ | Optimization Hint (parsed, ignored) |
| `target` | ⚠️ | Platform Target (parsed, ignored) |
| `module` | ❌ | Namespace (not implemented) |

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
| `&&` | Logical | ✅ |
| `\|\|` | Logical | ✅ |
| `!` | Logical | ✅ |
| `=` | Assignment | ✅ |
| `..` | Range | ✅ |
| `->` | Type Arrow | ✅ |
| `=>` | Match Arrow | ✅ |
| `::` | Scope Resolution | ✅ (effects only) |
| `.` | Field Access | ✅ |

### 1.3 Literals

| Literal Type | Syntax | Status |
|--------------|--------|--------|
| Integer | `42`, `-17`, `0x1F`, `0b1010` | ✅ (decimal), ⚠️ (hex/bin parsed) |
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
| `i128` | 16 bytes | Signed 128-bit integer | ⚠️ (parsed, C backend uses __int128) |
| `u8` | 1 byte | Unsigned 8-bit integer | ✅ |
| `u16` | 2 bytes | Unsigned 16-bit integer | ✅ |
| `u32` | 4 bytes | Unsigned 32-bit integer | ✅ |
| `u64` | 8 bytes | Unsigned 64-bit integer | ✅ |
| `u128` | 16 bytes | Unsigned 128-bit integer | ⚠️ (parsed, C backend uses __uint128) |
| `f32` | 4 bytes | IEEE 754 single precision | ✅ |
| `f64` | 8 bytes | IEEE 754 double precision | ✅ |
| `bool` | 1 byte | Boolean true/false | ✅ |
| `void` | 0 bytes | No value | ✅ |
| `string` | ptr | String literal (const char*) | ✅ |

### 2.2 Composite Types

| Type | Syntax | Status |
|------|--------|--------|
| Array (dynamic) | `array<T>` | ✅ |
| Array (fixed) | `array<T, N>` | ✅ |
| Pointer | `ptr<T>` | ✅ |
| Struct | `struct Name { ... }` | ✅ |
| Vector (SIMD) | `vec<T, N>` | ⚠️ (parsed, limited codegen) |

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
var_decl := 'let' IDENTIFIER (':' type)? '=' expression
```

**Status:** ✅ Fully implemented (type annotation optional with inference)

**Example:**
```flow
let x: i32 = 42
let y = 3.14          # Inferred as f32
let name = "Alice"    # Inferred as string
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

---

## 5. Statements

### 5.1 Statement Types

| Statement | Status |
|-----------|--------|
| Variable Declaration | ✅ |
| Assignment | ✅ |
| Return | ✅ |
| If/Elif/Else | ✅ |
| While Loop | ✅ |
| For Loop | ✅ |
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
for_stmt := 'for' IDENTIFIER 'in' expression '..' expression ('step' expression)? 'parallel'? block
```

**Status:** ✅ Basic for loop, ⚠️ `parallel` keyword parsed but not optimized

**Example:**
```flow
# Basic for loop
for i in 0..10 {
    printf("%d\n", i)
}

# With step
for i in 0..100 step 5 {
    printf("%d\n", i)
}

# Parallel hint (not yet optimized)
for i in 0..1000 parallel {
    data[i] = i * 2
}
```

### 5.5 Return Statement

**Grammar:**
```
return_stmt := 'return' expression?
```

**Status:** ✅ Fully implemented

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
handle_stmt := 'handle' IDENTIFIER 'with' IDENTIFIER block
```

**Status:** ✅ Fully implemented with runtime dispatch

**Example:**
```flow
function main() -> i32 {
    handle Log with ConsoleLogger {
        Log.emit("Hello from effects!")
        Log.level(3)
    }
    return 0
}
```

### 6.4 Effect Implementation Details

Effects are implemented via vtable-based runtime dispatch:

1. Each effect generates a C struct for the handler vtable
2. A global pointer tracks the current handler for each effect
3. `handle` blocks save/restore the handler pointer
4. Effect calls dispatch through the current handler's vtable

---

## 7. Module System

### 7.1 Import Declaration

**Grammar:**
```
import_decl := 'import' STRING
```

**Status:** ✅ Fully implemented

**Example:**
```flow
import "lib/stdlib/math.flow"
import "utils/helpers.flow"
```

### 7.2 Export Declaration

**Grammar:**
```
export_decl := 'export' (function_decl | struct_decl | const_decl)
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
```

### 7.3 Module Resolution

Import paths are resolved relative to:
1. Current file's directory
2. Project root
3. `lib/stdlib/` directory

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
let p: ptr<i32> = &x    # Address-of (not yet implemented)
let val: i32 = *p       # Dereference (not yet implemented)
```

**Status:** ⚠️ Pointer types parsed, limited operations

---

## 9. Compilation Targets

### 9.1 C Backend

**Status:** ✅ Primary backend, fully functional

- Generates portable C99 code
- Full effect system support via vtables
- All control flow constructs
- Struct and array support

### 9.2 MLIR Backend

**Status:** ⚠️ Functional but incomplete

- Basic function/control flow generation
- LLVM dialect lowering
- Limited effect support

### 9.3 WebAssembly

**Status:** ⚠️ Via Emscripten (C → WASM)

- Requires Emscripten toolchain
- Most features work
- No direct WASM emission

### 9.4 JIT Execution

**Status:** ✅ MLIR JIT via `flow jit` (requires LLVM/MLIR toolchain)

- Pipeline: Flow → MLIR → `mlir-opt` → `mlir-translate` → LLVM IR → `clang -shared` → in-memory execution via `ctypes`
- Commands: `flow jit <file>`, `transpiler --jit`, `transpiler --hot-reload`
- Hot reload watches `.flow` files and re-JITs on save (`FlowJITRunner` + `MLIRJIT`)
- Fallback: `flow run` uses the portable C backend (not JIT)

**Requirements:** `mlir-opt`, `mlir-translate`, and `clang` on `PATH` (e.g. `brew install llvm` on macOS)

**Related (AOT, not in-memory JIT):** `flow mlir-run` lowers MLIR → LLVM object file → links and runs

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
| `_gen_array_access` | Array indexing |
| `_gen_array_literal` | Array literals |
| `_gen_effect_runtime_types` | Effect vtable structs |
| `_gen_capability_method` | Capability method implementations |
| `_gen_effect_vtables` | Vtable initialization |

---

## Appendix C: Feature Implementation Matrix

| Feature | Parser | C Gen | MLIR Gen | Docs |
|---------|--------|-------|----------|------|
| Functions | ✅ | ✅ | ✅ | ✅ |
| Variables | ✅ | ✅ | ✅ | ✅ |
| Constants | ✅ | ✅ | ✅ | ✅ |
| Structs | ✅ | ✅ | ✅ | ✅ |
| Arrays | ✅ | ✅ | ⚠️ | ✅ |
| If/Else | ✅ | ✅ | ✅ | ✅ |
| While | ✅ | ✅ | ✅ | ✅ |
| For | ✅ | ✅ | ⚠️ | ✅ |
| Effects | ✅ | ✅ | ⚠️ | ✅ |
| Capabilities | ✅ | ✅ | ⚠️ | ✅ |
| Handle | ✅ | ✅ | ⚠️ | ✅ |
| Import | ✅ | ✅ | ✅ | ✅ |
| Export | ✅ | ✅ | ✅ | ✅ |
| Extern | ✅ | ✅ | ✅ | ⚠️ |
| Match | ✅ | ⚠️ | ⚠️ | ✅ |
| Parallel | ✅ | ❌ | ❌ | ⚠️ |
| SIMD Vec | ✅ | ⚠️ | ⚠️ | ⚠️ |
| Pointers | ✅ | ⚠️ | ⚠️ | ⚠️ |

---

*Last updated: 2026-01-08*
*Version: 0.1.0*
