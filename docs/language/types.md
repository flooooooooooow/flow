# Type System

FLOW features a static type system with type inference and comprehensive type checking.

## 🔤 Primitive Types

### Integer Types

```
i8   # 8-bit signed integer (-128 to 127)
i16  # 16-bit signed integer (-32,768 to 32,767)
i32  # 32-bit signed integer (-2,147,483,648 to 2,147,483,647)
i64  # 64-bit signed integer (-9,223,372,036,854,775,808 to 9,223,372,036,854,775,807)

u8   # 8-bit unsigned integer (0 to 255)
u16  # 16-bit unsigned integer (0 to 65,535)
u32  # 32-bit unsigned integer (0 to 4,294,967,295)
u64  # 64-bit unsigned integer (0 to 18,446,744,073,709,551,615)
```

### Floating Point Types

```
f32  # 32-bit floating point (IEEE 754 single precision)
f64  # 64-bit floating point (IEEE 754 double precision)
```

### Complex Types

```
c64   # 64-bit complex (two f32s, C99 float complex)
c128  # 128-bit complex (two f64s, C99 double complex)
```

Constructors: `c64(re, im)`, `c128(re, im)`, or `c64(x)` for a real-only value.
Builtins: `creal`, `cimag`, `cabs`, `carg`, `conj`, `cexp`, `clog`, `csqrt`, `cpow`.
Arithmetic operators `+`, `-`, `*`, `/` work on complex types with automatic
promotion (`c64 + c128` yields `c128`, `c64 + f64` yields `c128`).

### Other Primitive Types

```
bool    # Boolean value (true or false)
string  # String of characters
void    # No return value
```

## 📚 Array Types

### Dynamic Arrays

```
[i32]        # Array of integers with dynamic size
[f32]        # Array of floats
[string]     # Array of strings
[Point]      # Array of struct instances
```

### Fixed-Size Arrays

```
[i32; 10]    # Array of exactly 10 integers
[f32; 3]     # Array of exactly 3 floats
[bool; 8]    # Array of exactly 8 booleans
```

### Array Operations

```
let arr = [1, 2, 3, 4, 5]
let length = length(arr)        # Get array length
let element = arr[0]            # Access element
arr[1] = 10                    # Modify element
```

## 🪟 Span Types (borrowed views)

A span is a `{pointer, length}` view over contiguous storage. It never owns
its data and never allocates. Arrays and slices borrow into one automatically
at the call site.

```text
function analyse(samples: span<f32>) -> f32     # immutable view
function clear(samples: span<mut f32>)          # mutable view
function fft(frame: span<f32, 1024>)            # static extent
function analyse(samples: &[f32]) -> f32        # same type, bracket sugar

let window: span<f32> = signal[128..256]        # slice expression
```

Full reference: [spans.md](spans.md).

## 🏗️ Struct Types

### Struct Definition

```
struct Point {
    x: f32,
    y: f32
}

struct Rectangle {
    top_left: Point,
    width: f32,
    height: f32
}
```

### Struct Usage

```
let p = Point { x: 3.14, y: 2.71 }
let rect = Rectangle {
    top_left: Point { x: 0.0, y: 0.0 },
    width: 100.0,
    height: 50.0
}

# Field access
let x_coord = p.x
rect.width = 150.0
```

### Nested Structs

```
struct Address {
    street: string,
    city: string,
    zip: string
}

struct Person {
    name: string,
    age: i32,
    address: Address
}

let person = Person {
    name: "Alice",
    age: 30,
    address: Address {
        street: "123 Main St",
        city: "NYC",
        zip: "10001"
    }
}

# Nested field access
let city = person.address.city
```

## 🔄 Function Types

### Function Signatures

```
# Function type notation
(i32, i32) -> i32           # Takes two integers, returns integer
(string) -> void            # Takes string, returns nothing
() -> f32                   # Takes no parameters, returns float
([i32]) -> i32              # Takes integer array, returns integer
```

### Function Pointers (Future)

```
let func: (i32, i32) -> i32 = add
let result = func(5, 3)      # Calls through function pointer
```

## 🎯 Type Inference

FLOW can infer types from context:

```
# Type inferred from literal
let x = 42           # x is i32
let y = 3.14         # y is f32
let name = "Alice"   # name is string

# Type inferred from function return
let result = add(5, 3)  # result is i32 if add returns i32

# Type inferred from assignment
let arr = [1, 2, 3]      # arr is [i32]
```

### Explicit Type Annotations

You can always specify types explicitly:

```
let x: i32 = 42
let y: f64 = 3.14159
let name: string = "Bob"
let numbers: [i32; 5] = [1, 2, 3, 4, 5]
```

## 🔍 Type Checking

### Static Type Checking

FLOW checks types at compile time:

```
function add(a: i32, b: i32) -> i32 {
    return a + b  # OK: both operands are i32
}

# Usage
add(5, 3)        # OK: both arguments are i32
add(5, 3.14)     # Error: second argument is f32, expected i32
```

### Type Coercion

Limited automatic type conversion:

```
# Integer to float conversion (widening)
let f: f32 = 5           # OK: i32 literal converted to f32
let arr: [f32] = [1, 2, 3]  # OK: i32 literals converted to f32

# No narrowing conversion
let i: i32 = 3.14        # Error: cannot convert f32 to i32
```

## 📏 Units of Measure

A `unit` declaration creates a numeric type that carries a physical
dimension. The checker performs dimensional analysis at compile time.
At runtime a unit value is a plain `f64`.

```
unit Meter
unit Second
unit Velocity = Meter / Second
unit Accel    = Meter / Second^2
unit Hertz    = 1 / Second
```

A bare `unit Name` declares a new base dimension. A declaration with `=`
derives a unit from existing ones using `*`, `/`, and integer `^`
exponents. The literal `1` stands for the dimensionless unit.

```
let d: Meter  = 100.0 as Meter    # literals take a unit with `as`
let t: Second = 8.0 as Second

let v: Velocity = d / t           # division composes dimensions
let d2: Meter   = v * t           # multiplication cancels them
let sum: Meter  = d + d2          # addition needs equal dimensions
let ratio: f64  = d2 / d          # full cancellation gives plain f64
let far: bool   = sum > d         # comparison needs equal dimensions

let bad = d + t                   # compile error:
# line N: dimensional error: Meter + Second
# (operands of '+' must have the same dimension)
```

Dimensionless scalars multiply and divide freely: `d * 2.0` is a
`Meter`. Adding a bare literal to a unit value is an error; give the
literal a unit first with `as`. Casting between units requires equal
dimensions; cross-dimension conversion goes through the numeric base,
as in `d as f64 as Second`.

Two derived units with the same exponent vector are interchangeable.
When a `*` or `/` result matches no declared unit, error messages print
its dimensions directly, for example `Meter/Second^3`.

Trigonometric and exponential builtins take dimensionless arguments.
A unit named `Radian` is the one exception: angles pass into `sin`,
`cos`, and the rest as plain numbers.

Units erase in the generated C. Each unit becomes a `typedef double`,
so the runtime cost is zero.

## 🎭 Generic Types (Future)

```
# Future generic type support
function array_length<T>(arr: [T]) -> i32 {
    return length(arr)
}

function swap<T>(a: T, b: T) -> (T, T) {
    return (b, a)
}
```

## 🚀 Advanced Type Features

### Type Aliases (Future)

```
type Vector3D = [f32; 3]
type Matrix4x4 = [[f32; 4]; 4]

let position: Vector3D = [0.0, 0.0, 0.0]
let transform: Matrix4x4 = identity_matrix()
```

### Union Types (Future)

```
type Number = i32 | f32

function process_number(n: Number) -> void {
    match n {
        i: i32 => print("Integer: " + string(i)),
        f: f32 => print("Float: " + string(f))
    }
}
```

### Optional Types (Future)

```
type Optional<T> = T | null

function safe_divide(a: f32, b: f32) -> Optional<f32> {
    if b == 0.0 {
        return null
    }
    return a / b
}
```

## 🔧 Type System Features

### Memory Layout

Structs have predictable memory layout:

```
struct Example {
    a: i8,    # Offset 0, size 1
    b: i32,   # Offset 4 (aligned), size 4
    c: f32,   # Offset 8, size 4
    d: i64    # Offset 16 (aligned), size 8
}
# Total size: 24 bytes
```

### Type Safety

FLOW provides strong type safety:

- No implicit conversions between incompatible types
- Struct field access is type-checked
- Array bounds checking (runtime)
- Function parameter type checking

### Performance Considerations

- Primitive types map directly to machine types
- Structs are laid out efficiently in memory
- Arrays use contiguous memory
- No runtime type information for primitive types

## 📊 Type Compatibility Matrix

| From \ To | i8 | i16 | i32 | i64 | f32 | f64 |
|-----------|----|-----|-----|-----|-----|-----|
| i8        | ✓  | ✓   | ✓   | ✓   | ✓   | ✓   |
| i16       | ✗  | ✓   | ✓   | ✓   | ✓   | ✓   |
| i32       | ✗  | ✗   | ✓   | ✓   | ✓   | ✓   |
| i64       | ✗  | ✗   | ✗   | ✓   | ✓   | ✓   |
| f32       | ✗  | ✗   | ✗   | ✗   | ✓   | ✓   |
| f64       | ✗  | ✗   | ✗   | ✗   | ✗   | ✓   |

✓ = Allowed conversion (with possible loss of precision)
✗ = Not allowed

## 🎯 Best Practices

1. **Use the most specific type** that fits your needs
2. **Prefer i32 for general integers** unless you need larger ranges
3. **Use f32 for graphics and performance-critical code**
4. **Use f64 for scientific computing** when precision matters
5. **Be explicit with struct field types** for clarity
6. **Use arrays for collections** of the same type
7. **Consider memory layout** for performance-critical structs

## 🔍 Type Debugging

### Type Errors

```
# Common type errors
add(5, 3.14)           # Type mismatch: expected i32, got f32
point.x = "hello"      # Type mismatch: expected f32, got string
arr[1.5]               # Type mismatch: expected i32, got f32
```

### Type Inspection

```
# Future: type inspection functions
typeof(x)              # Get type of expression
is_type<T>(value)      # Check if value is of type T
```

The FLOW type system provides safety and performance while maintaining clarity and expressiveness.

## RF / SDR Types

The `stdlib/rf.flow` module provides types for software-defined radio:

### IQ (transparent alias)

```flow
type IQ = c64   # In-phase / Quadrature sample
```

`IQ` is a transparent alias for `c64`. Use it for readability in RF code;
it interchanges freely with `c64`.

### IQSample (distinct type)

```flow
distinct type IQSample = c64
```

`IQSample` is a distinct (opaque) type. It does **not** interchange with
`c64` without an explicit cast, preventing accidental mixing of RF sample
buffers with generic complex arithmetic:

```text
let z: c64 = c64(1.0, 2.0)
let s: IQSample = z as IQSample   # explicit cast required
```

### Signal (rate-typed buffer)

```flow
struct Signal<R> {
    data: ptr<c64>,
    len: i32,
    sample_rate: u32,
}
```

`Signal<R>` carries a phantom type parameter `R` that tags the sample
rate at compile time. `R` does not appear in the fields. The type
checker enforces that `signal_mix<R>` receives two signals with the same
`R`, so mixing signals at different rates is a compile-time error:

```text
let a: Signal<Hz44100> = signal_new<Hz44100>(64, 44100)
let b: Signal<Hz48000> = signal_new<Hz48000>(64, 48000)
let m: Signal<Hz44100> = signal_mix<Hz44100>(a, b)  # compile error
```

Rate markers are distinct types: `distinct type Hz44100 = u32`. The
stdlib provides common rates (Hz1000, Hz8000, Hz44100, Hz48000, Hz1M,
etc.). To create a new rate marker: `distinct type HzMyRate = u32`.

### Quantity literals

A number followed by a unit name on the same line desugars to a cast:

```text
unit Hertz = Second^-1

let f: Hertz = 3.14e6 Hertz   # same as: 3.14e6 as Hertz
let d: Meter = 100.0 Meter
```

The identifier must start with an uppercase letter. This avoids ambiguity
with contextual keywords like `step` in `for i in 0 to 10 step 2`.

`lib/stdlib/units_si.flow` provides SI base dimensions (Second, Meter,
Kilogram, Ampere, Kelvin, Radian) and derived units (Hertz, Newton, Watt,
Volt, Ohm, Farad, Henry, Coulomb, Tesla, Weber).
