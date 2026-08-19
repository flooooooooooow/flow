# 8. Types and declarations beyond the core

The first five chapters used a small set of stable types. Flow also has wide
integers, complex values, nominal types, units, generics, enums, traits,
constants, module state, and code-generation attributes.

## 8.1 Complete scalar set

| Family | Types | Important qualification |
|---|---|---|
| Signed integers | `i8`, `i16`, `i32`, `i64`, `i128` | `i128` uses the C backend; MLIR does not support it fully |
| Unsigned integers | `u8`, `u16`, `u32`, `u64`, `u128` | unsigned arithmetic and bit operations |
| Floating point | `f32`, `f64` | IEEE 754 arithmetic and comparison |
| Complex | `c64`, `c128` | two-component C99 complex values |
| Logical | `bool` | `true` or `false` |
| Text | `string` | a pointer to immutable character data at the C boundary |
| Empty result | `void` | used when a function returns no value |

Wide integer literals and complex values are explicit:

```flow
let mask: u64 = 0xFFFF
let large: i128 = 9000000000000000000 as i128
let z: c128 = c128(3.0, 4.0)
let magnitude: f64 = cabs(z)  # 5.0
```

Complex operations include `creal`, `cimag`, `cabs`, `carg`, `conj`, `cexp`,
`clog`, `csqrt`, and `cpow`. Arithmetic promotes `c64` to `c128` when a
`c128` or `f64` operand requires the wider representation.

## 8.2 Floating-point order

Ordinary comparisons use IEEE rules. In particular, a NaN is unordered and
`nan == nan` is false. Sorting requires a total relation, so declarative
`sort`, `sortBy`, `sort unique`, and `find` use IEEE total order:

```text
-NaN < -infinity < ... < -0.0 < +0.0 < ... < +infinity < +NaN
```

The total order gives sorting a deterministic result. Ordinary arithmetic
still follows IEEE rules.
See [`tests/lang/test_sort_nan.flow`](../../tests/lang/test_sort_nan.flow).

## 8.3 Composite type forms

```text
array<T>             # dynamic array
array<T, N>          # fixed array
ptr<T>               # pointer
span<T>              # immutable borrowed view
span<mut T>          # mutable borrowed view
span<T, N>           # borrowed view with static extent
vec<T, N>            # SIMD vector; parsing and code generation are partial
(A, B) -> R          # function or closure type
```

`&[T]`, `&mut [T]`, and `&[T; N]` are span spellings. Bare inferred spans,
such as `span` without an element type, are not implemented.

## 8.4 Aliases and distinct types

A transparent alias supplies another name for one type:

```flow
type Bytes = array<u8>
```

A distinct type creates a nominal boundary:

```flow
distinct type UserId = i64

let raw: i64 = 42
let user: UserId = raw as UserId
let stored: i64 = user as i64
```

`Bytes` and `array<u8>` are interchangeable. `UserId` and `i64` are not;
crossing that boundary requires `as`.

## 8.5 Units of measure

```flow
unit Meter
unit Second
unit Velocity = Meter / Second
unit Acceleration = Meter / Second^2

let distance: Meter = 100.0 as Meter
let duration: Second = 8.0 as Second
let speed: Velocity = distance / duration
```

The checker composes dimensions through multiplication and division and
requires equal dimensions for addition, subtraction, and ordered comparison.
Units erase to ordinary floating-point storage at runtime.

Run the complete kinematics example:

```bash
FLOW_HOST=python ./flow run examples/evolution/units_kinematics.flow
```

## 8.6 Constants and module statics

```text
const BLOCK_SIZE: i32 = 256

let mut calls: i32 = 0
let mut table: array<i32, 4> = [0, 0, 0, 0]
let mut head: ptr<Node> = null
```

`const` declares an immutable compile-time value. A top-level `let mut`
declares private, file-scope state in the C backend. Module statics require an
explicit type and constant initializer. The MLIR backend currently rejects
module statics.

## 8.7 Enums and matching

```flow
enum Direction {
    North,
    South,
    East,
    West
}

let north: i32 = Direction_North as i32
```

Enum tags begin at zero. Enum values also support the tagged form used by
`match` and `choose`; see
[`examples/generics_traits/enum_match_exhaustive.flow`](../../examples/generics_traits/enum_match_exhaustive.flow).

## 8.8 Generics

```flow
struct Box<T> {
    value: T
}

function identity<T>(x: T) -> T {
    return x
}

let box: Box<i32> = Box<i32> { value: 42 }
let answer: i32 = identity<i32>(box.value)
```

The compiler monomorphises each used type combination into a concrete
specialisation. Explicit type arguments are the dependable form. Inferred
generic struct literals such as `Box { value: 42 }` remain incomplete.

```bash
FLOW_HOST=python ./flow run tests/lang/test_generics.flow
FLOW_HOST=python ./flow run examples/book/08_types_patterns.flow
```

## 8.9 Function overloading

Several functions may share a source name when their parameter types differ:

```flow
function pick(value: i32) -> i32 { return 1 }
function pick(value: u32) -> i32 { return 2 }
```

Resolution uses argument types and the C backend mangles the chosen signature.
An unsuffixed literal must still lead to an unambiguous type. Stable external
consumers use export aliases or `@flow_api`, not mangled names.

## 8.10 Traits and implementations

```flow
struct Point {
    x: i32,
    y: i32
}

trait Comparable {
    function compare(self: Point, other: Point) -> i32
}

impl Comparable for Point {
    function compare(self: Point, other: Point) -> i32 {
        if self.x < other.x { return -1 }
        if self.x > other.x { return 1 }
        return 0
    }
}
```

Trait and `impl` syntax is accepted by the Python host, but trait-driven
dispatch remains partial. The self-hosted parser skips these blocks rather
than implementing their semantics. Use ordinary named functions where a
portable call across both hosts is required.

## 8.11 Function attributes

Attributes precede a function declaration:

```flow
@always_inline
@target("avx2")
function dot4(a: ptr<f32>, b: ptr<f32>) -> f32 {
    # ...
}
```

| Attribute | Purpose |
|---|---|
| `@only(mode)`, `@guard(modes...)`, `@compile` | include a function for selected build modes |
| `@inline`, `@always_inline`, `@noinline` | steer C inlining |
| `@target("features")` | request target-specific C code generation |
| `@flow_api` | preserve a stable, unmangled C-facing name |
| `@gpu` | mark device code |
| `@rt_safe` | require every reachable call to be real-time safe |
| `@lifetime(domain)` | attach a lifetime domain |
| `@safe`, `@unsafe` | mark checked and escaped certification boundaries |

Inlining attributes do not change program semantics. `@target` is interpreted
by the platform C compiler and is necessarily platform-dependent.

## 8.12 Debug and test declarations

```text
let measured: i32 = dbg compute()
expect measured >= 0

test "nonnegative result" {
    return measured >= 0
}
```

On the C backend, `dbg` writes to standard error and yields its operand;
`expect` aborts when its Boolean condition is false. MLIR evaluates their
operands but does not yet reproduce those diagnostics. A `test` block becomes
a Boolean function, but the test harness does not discover or invoke it.
Executable Flow tests therefore use `main` plus distinct nonzero return codes.

## Exercises

1. Define distinct `InputIndex` and `OutputIndex` types and make an accidental
   interchange fail type checking.
2. Add `Mass` and `Force` to the unit system and derive the missing dimension.
3. Instantiate one generic pair with `i32, bool` and another with `f64, i32`.
4. Run the generic and enum examples through both compiler hosts and record
   which features each one accepts.

Next: [Expressions, matching, and declarative operations](09-expressions-and-matching.md).
