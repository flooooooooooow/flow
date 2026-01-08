# FLOW API Reference

Complete API reference for the FLOW programming language, including all built-in functions, types, and standard library modules.

## Table of Contents

- [Language Reference](#language-reference)
- [Built-in Types](#built-in-types)
- [Built-in Functions](#built-in-functions)
- [Standard Library](#standard-library)
- [Compiler Directives](#compiler-directives)
- [Foreign Function Interface](#foreign-function-interface)

---

## Language Reference

### Keywords

```flow
# Control flow
if, elif, else, match, case, for, while, break, continue, return

# Declarations
function, struct, effect, capability, handle, import, export, const, let

# Types
i8, i16, i32, i64, u8, u16, u32, u64, f32, f64, bool, string, void, ptr

# Modifiers
inline, hot, export, private, public

# Pattern matching
match, case, with, when, otherwise

# Effects and capabilities
effect, capability, implements, handle, with

# Modules
import, export, as, from

# Other
true, false, null, self, super, sizeof, offsetof, typeof, alignof
```

### Operators

#### Arithmetic Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `+` | Addition | `a + b` |
| `-` | Subtraction | `a - b` |
| `*` | Multiplication | `a * b` |
| `/` | Division | `a / b` |
| `%` | Modulo | `a % b` |
| `**` | Exponentiation | `a ** b` |

#### Comparison Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `==` | Equal | `a == b` |
| `!=` | Not equal | `a != b` |
| `<` | Less than | `a < b` |
| `<=` | Less than or equal | `a <= b` |
| `>` | Greater than | `a > b` |
| `>=` | Greater than or equal | `a >= b` |

#### Logical Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `&&` | Logical AND | `a && b` |
| `||` | Logical OR | `a || b` |
| `!` | Logical NOT | `!a` |

#### Bitwise Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `&` | Bitwise AND | `a & b` |
| `|` | Bitwise OR | `a | b` |
| `^` | Bitwise XOR | `a ^ b` |
| `<<` | Left shift | `a << b` |
| `>>` | Right shift | `a >> b` |
| `~` | Bitwise NOT | `~a` |

#### Assignment Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `=` | Assignment | `a = b` |
| `+=` | Add and assign | `a += b` |
| `-=` | Subtract and assign | `a -= b` |
| `*=` | Multiply and assign | `a *= b` |
| `/=` | Divide and assign | `a /= b` |
| `%=` | Modulo and assign | `a %= b` |

#### Other Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `.` | Member access | `obj.field` |
| `->` | Pointer dereference | `ptr->field` |
| `[]` | Array indexing | `arr[index]` |
| `()` | Function call | `func(args)` |
| `:` | Type annotation | `x: i32` |
| `=>` | Lambda/arrow | `x => x + 1` |
| `..` | Range | `0..10` |
| `...` | Spread | `func(...args)` |

---

## Built-in Types

### Primitive Types

#### Integer Types

```flow
# Signed integers
i8   # 8-bit signed integer (-128 to 127)
i16  # 16-bit signed integer (-32768 to 32767)
i32  # 32-bit signed integer (-2147483648 to 2147483647)
i64  # 64-bit signed integer (-9223372036854775808 to 9223372036854775807)

# Unsigned integers
u8   # 8-bit unsigned integer (0 to 255)
u16  # 16-bit unsigned integer (0 to 65535)
u32  # 32-bit unsigned integer (0 to 4294967295)
u64  # 64-bit unsigned integer (0 to 18446744073709551615)
```

#### Floating Point Types

```flow
f32  # 32-bit IEEE-754 floating point
f64  # 64-bit IEEE-754 floating point
```

#### Other Primitive Types

```flow
bool   # Boolean (true or false)
string # String literal
void   # No value (for functions)
ptr    # Raw pointer type
```

### Composite Types

#### Array Types

```flow
# Fixed-size array
array<T, N>     # Array of type T with N elements

# Dynamic array
array<T>        # Array of type T with dynamic size

# Multi-dimensional array
array<array<T>> # 2D array
```

#### Function Types

```flow
# Function type
fn(T1, T2, ...) -> R  # Function taking T1, T2, ... returning R

# Generic function type
fn<T>(T) -> T         # Generic function
```

#### Option and Result Types

```flow
# Optional value
Option<T>  # Either Some(T) or None

# Result type
Result<T, E>  # Either Ok(T) or Err(E)
```

---

## Built-in Functions

### Type Information

```flow
# Get size of type in bytes
function sizeof<T>(type: Type<T>) -> i32

# Get alignment of type in bytes
function alignof<T>(type: Type<T>) -> i32

# Get offset of field in struct
function offsetof<T>(struct: Type<T>, field: string) -> i32

# Get type name
function type_name<T>(value: T) -> string

# Type checking
function is_same_type<T, U>(a: T, b: U) -> bool
```

### Array Operations

```flow
# Array information
function len<T>(arr: array<T>) -> i32
function capacity<T>(arr: array<T>) -> i32
function is_empty<T>(arr: array<T>) -> bool

# Element access
function first<T>(arr: array<T>) -> T
function last<T>(arr: array<T>) -> T
function get<T>(arr: array<T>, index: i32) -> T
function set<T>(arr: array<T>, index: i32, value: T) -> void

# Array creation
function array<T>(size: i32) -> array<T>
function array<T>(values: T...) -> array<T>

# Array manipulation
function append<T>(arr: array<T>, value: T) -> void
function pop<T>(arr: array<T>) -> T
function insert<T>(arr: array<T>, index: i32, value: T) -> void
function remove<T>(arr: array<T>, index: i32) -> T
```

### String Operations

```flow
# String information
function len(s: string) -> i32
function is_empty(s: string) -> bool

# String manipulation
function concat(a: string, b: string) -> string
function substring(s: string, start: i32, length: i32) -> string
function slice(s: string, start: i32, end: i32) -> string

# String searching
function find(s: string, pattern: string) -> i32
function contains(s: string, pattern: string) -> bool
function starts_with(s: string, prefix: string) -> bool
function ends_with(s: string, suffix: string) -> bool

# String transformation
function to_upper(s: string) -> string
function to_lower(s: string) -> string
function trim(s: string) -> string
```

### Mathematical Functions

```flow
# Basic arithmetic
function abs(x: i32) -> i32
function abs(x: f32) -> f32
function min(a: i32, b: i32) -> i32
function max(a: i32, b: i32) -> i32
function clamp(x: f32, min: f32, max: f32) -> f32

# Trigonometric
function sin(x: f32) -> f32
function cos(x: f32) -> f32
function tan(x: f32) -> f32
function asin(x: f32) -> f32
function acos(x: f32) -> f32
function atan(x: f32) -> f32
function atan2(y: f32, x: f32) -> f32

# Exponential and logarithmic
function exp(x: f32) -> f32
function log(x: f32) -> f32
function log2(x: f32) -> f32
function log10(x: f32) -> f32
function pow(x: f32, y: f32) -> f32
function sqrt(x: f32) -> f32

# Rounding
function floor(x: f32) -> f32
function ceil(x: f32) -> f32
function round(x: f32) -> f32
function trunc(x: f32) -> f32
```

### Memory Operations

```flow
# Memory allocation
function malloc(size: i32) -> ptr
function free(ptr: ptr) -> void
function realloc(ptr: ptr, size: i32) -> ptr

# Memory manipulation
function memcpy(dest: ptr, src: ptr, size: i32) -> ptr
function memset(dest: ptr, value: i8, size: i32) -> ptr
function memcmp(a: ptr, b: ptr, size: i32) -> i32
function memmove(dest: ptr, src: ptr, size: i32) -> ptr
```

### I/O Operations

```flow
# Standard I/O
function printf(format: string, ...) -> i32
function scanf(format: string, ...) -> i32
function putchar(c: i32) -> i32
function getchar() -> i32
function puts(s: string) -> i32
function gets(buffer: string, size: i32) -> string

# File I/O
function fopen(path: string, mode: string) -> ptr
function fclose(file: ptr) -> i32
function fread(buffer: ptr, size: i32, count: i32, file: ptr) -> i32
function fwrite(buffer: ptr, size: i32, count: i32, file: ptr) -> i32
function fseek(file: ptr, offset: i32, origin: i32) -> i32
function ftell(file: ptr) -> i32
```

### Conversion Functions

```flow
# Type conversions
function as<T>(value: any) -> T
function cast<T>(value: any) -> T

# String conversions
function to_string(value: i32) -> string
function to_string(value: f32) -> string
function to_string(value: bool) -> string
function parse_int(s: string) -> i32
function parse_float(s: string) -> f32
function parse_bool(s: string) -> bool
```

### Assertion and Debug

```flow
# Assertions
function assert(condition: bool) -> void
function assert(condition: bool, message: string) -> void

# Debug
function debug_print(value: any) -> void
function debug_println(value: any) -> void
function panic(message: string) -> void
function unreachable() -> void
```

---

## Standard Library

### `std/core`

Core types and utilities.

#### Constants

```flow
const INT_MIN: i32 = -2147483648
const INT_MAX: i32 = 2147483647
const FLOAT_PI: f32 = 3.14159265359
const FLOAT_E: f32 = 2.71828182846
const BOOL_TRUE: bool = true
const BOOL_FALSE: bool = false
```

#### Types

```flow
# Optional type
enum Option<T> {
    Some(T),
    None
}

# Result type
enum Result<T, E> {
    Ok(T),
    Err(E)
}

# Pair type
struct Pair<T, U> {
    first: T,
    second: U
}

# Triple type
struct Triple<T, U, V> {
    first: T,
    second: U,
    third: V
}
```

### `std/math`

Mathematical functions and constants.

#### Constants

```flow
const PI: f32 = 3.14159265358979323846
const E: f32 = 2.71828182845904523536
const SQRT_2: f32 = 1.41421356237309504880
const SQRT_PI: f32 = 1.77245385090551602729
const LN_2: f32 = 0.69314718055994530942
const LN_10: f32 = 2.30258509299404568402
```

#### Vector Types

```flow
struct Vec2 { x: f32, y: f32 }
struct Vec3 { x: f32, y: f32, z: f32 }
struct Vec4 { x: f32, y: f32, z: f32, w: f32 }

# Vector operations
function vec2(x: f32, y: f32) -> Vec2
function vec3(x: f32, y: f32, z: f32) -> Vec3
function vec4(x: f32, y: f32, z: f32, w: f32) -> Vec4

function add(a: Vec2, b: Vec2) -> Vec2
function sub(a: Vec2, b: Vec2) -> Vec2
function mul(a: Vec2, s: f32) -> Vec2
function div(a: Vec2, s: f32) -> Vec2

function dot(a: Vec2, b: Vec2) -> f32
function cross(a: Vec3, b: Vec3) -> Vec3
function length(v: Vec2) -> f32
function normalize(v: Vec2) -> Vec2
function distance(a: Vec2, b: Vec2) -> f32
```

#### Matrix Types

```flow
struct Mat2 {
    m00: f32, m01: f32,
    m10: f32, m11: f32
}

struct Mat3 {
    m00: f32, m01: f32, m02: f32,
    m10: f32, m11: f32, m12: f32,
    m20: f32, m21: f32, m22: f32
}

struct Mat4 {
    m00: f32, m01: f32, m02: f32, m03: f32,
    m10: f32, m11: f32, m12: f32, m13: f32,
    m20: f32, m21: f32, m22: f32, m23: f32,
    m30: f32, m31: f32, m32: f32, m33: f32
}

# Matrix operations
function mat2_identity() -> Mat2
function mat2_rotation(angle: f32) -> Mat2
function mat2_scale(sx: f32, sy: f32) -> Mat2
function mat2_translation(tx: f32, ty: f32) -> Mat3

function mul(a: Mat2, b: Mat2) -> Mat2
function mul(m: Mat2, v: Vec2) -> Vec2
function transpose(m: Mat2) -> Mat2
function determinant(m: Mat2) -> f32
function inverse(m: Mat2) -> Mat2
```

### `std/string`

String manipulation functions.

```flow
# String operations
function split(s: string, delimiter: string) -> array<string>
function join(parts: array<string>, delimiter: string) -> string
function replace(s: string, old: string, new: string) -> string
function replace_all(s: string, old: string, new: string) -> string

# Case operations
function capitalize(s: string) -> string
function title_case(s: string) -> string
function snake_case(s: string) -> string
function camel_case(s: string) -> string

# Padding and alignment
function pad_left(s: string, width: i32, char: string) -> string
function pad_right(s: string, width: i32, char: string) -> string
function center(s: string, width: i32, char: string) -> string

# Character operations
function is_digit(c: string) -> bool
function is_alpha(c: string) -> bool
function is_alnum(c: string) -> bool
function is_space(c: string) -> bool
function is_lower(c: string) -> bool
function is_upper(c: string) -> bool
function is_printable(c: string) -> bool
```

### `std/array`

Array manipulation functions.

```flow
# Searching and sorting
function find<T>(arr: array<T>, value: T) -> i32
function contains<T>(arr: array<T>, value: T) -> bool
function binary_search<T>(arr: array<T>, value: T) -> i32
function sort<T>(arr: array<T>) -> void
function sort_by<T>(arr: array<T>, comparator: fn(T, T) -> i32) -> void
function reverse<T>(arr: array<T>) -> void

# Functional operations
function map<T, U>(arr: array<T>, mapper: fn(T) -> U) -> array<U>
function filter<T>(arr: array<T>, predicate: fn(T) -> bool) -> array<T>
function reduce<T>(arr: array<T>, initial: T, accumulator: fn(T, T) -> T) -> T

# Set operations
function unique<T>(arr: array<T>) -> array<T>
function union<T>(a: array<T>, b: array<T>) -> array<T>
function intersection<T>(a: array<T>, b: array<T>) -> array<T>
function difference<T>(a: array<T>, b: array<T>) -> array<T>

# Chunking and windowing
function chunk<T>(arr: array<T>, size: i32) -> array<array<T>>
function window<T>(arr: array<T>, size: i32) -> array<array<T>>
function slide<T>(arr: array<T>, size: i32, step: i32) -> array<array<T>>
```

### `std/io`

File I/O and stream operations.

```flow
# File operations
function exists(path: string) -> bool
function is_file(path: string) -> bool
function is_directory(path: string) -> bool
function file_size(path: string) -> i64
function file_modified(path: string) -> f64
function file_created(path: string) -> f64

function read_file(path: string) -> string
function write_file(path: string, content: string) -> void
function append_file(path: string, content: string) -> void
function read_bytes(path: string) -> array<u8>
function write_bytes(path: string, data: array<u8>) -> void

# Directory operations
function create_directory(path: string) -> void
function create_directories(path: string) -> void
function remove_directory(path: string) -> void
function list_directory(path: string) -> array<string>
function list_files(path: string) -> array<string>
function list_directories(path: string) -> array<string>

# Path operations
function basename(path: string) -> string
function dirname(path: string) -> string
function extension(path: string) -> string
function filename(path: string) -> string
function is_absolute(path: string) -> bool
function normalize_path(path: string) -> string
function join_path(parts: array<string>) -> string
function relative_path(from: string, to: string) -> string
```

### `std/graphics`

Graphics and rendering utilities.

```flow
# Colors
struct Color {
    r: f32, g: f32, b: f32, a: f32
}

# Color constants
const COLOR_BLACK: Color = Color { r: 0.0, g: 0.0, b: 0.0, a: 1.0 }
const COLOR_WHITE: Color = Color { r: 1.0, g: 1.0, b: 1.0, a: 1.0 }
const COLOR_RED: Color = Color { r: 1.0, g: 0.0, b: 0.0, a: 1.0 }
const COLOR_GREEN: Color = Color { r: 0.0, g: 1.0, b: 0.0, a: 1.0 }
const COLOR_BLUE: Color = Color { r: 0.0, g: 0.0, b: 1.0, a: 1.0 }

# Color operations
function rgb(r: u8, g: u8, b: u8) -> Color
function rgba(r: u8, g: u8, b: u8, a: u8) -> Color
function rgb_f(r: f32, g: f32, b: f32) -> Color
function rgba_f(r: f32, g: f32, b: f32, a: f32) -> Color

function rgb_to_hsv(color: Color) -> Vec3
function hsv_to_rgb(hsv: Vec3) -> Color
function lerp_color(a: Color, b: Color, t: f32) -> Color
function brightness(color: Color) -> f32
function contrast(color: Color, factor: f32) -> Color

# 2D primitives
struct Rectangle {
    x: f32, y: f32, width: f32, height: f32
}

struct Circle {
    center: Vec2, radius: f32
}

struct Line {
    start: Vec2, end: Vec2
}

# Geometry operations
function rect(x: f32, y: f32, width: f32, height: f32) -> Rectangle
function circle(center: Vec2, radius: f32) -> Circle
function line(start: Vec2, end: Vec2) -> Line

function contains_point(rect: Rectangle, point: Vec2) -> bool
function intersects(a: Rectangle, b: Rectangle) -> bool
function distance_point_to_line(point: Vec2, line: Line) -> f32
function point_in_circle(point: Vec2, circle: Circle) -> bool
```

### `std/memory`

Memory management utilities.

```flow
# Memory pools
struct MemoryPool {
    start: ptr, current: ptr, end: ptr, page_size: i32
}

function create_pool(initial_size: i32) -> MemoryPool
function destroy_pool(pool: MemoryPool) -> void
function pool_alloc(pool: MemoryPool, size: i32) -> ptr
function pool_reset(pool: MemoryPool) -> void

# Arena allocator
struct Arena {
    current_block: ptr, blocks: array<ptr>, total_allocated: i32
}

function arena_create() -> Arena
function arena_destroy(arena: Arena) -> void
function arena_alloc(arena: Arena, size: i32) -> ptr
function arena_reset(arena: Arena) -> void

# Reference counting
struct RefCounted<T> {
    value: T, count: i32
}

function ref_create<T>(value: T) -> RefCounted<T>
function ref_acquire<T>(ref: RefCounted<T>) -> RefCounted<T>
function ref_release<T>(ref: RefCounted<T>) -> void
function ref_count<T>(ref: RefCounted<T>) -> i32
```

### `std/concurrency`

Concurrency and parallelism utilities.

```flow
# Threads
struct Thread { id: i32, handle: ptr }

function thread_create(func: fn() -> void) -> Thread
function thread_join(thread: Thread) -> void
function thread_sleep(milliseconds: i32) -> void
function thread_yield() -> void

# Mutex and locks
struct Mutex { handle: ptr }

function mutex_create() -> Mutex
function mutex_destroy(mutex: Mutex) -> void
function mutex_lock(mutex: Mutex) -> void
function mutex_unlock(mutex: Mutex) -> void
function mutex_try_lock(mutex: Mutex) -> bool

# Atomic operations
struct Atomic<T> { value: T }

function atomic_load<T>(atomic: Atomic<T>) -> T
function atomic_store<T>(atomic: Atomic<T>, value: T) -> void
function atomic_exchange<T>(atomic: Atomic<T>, value: T) -> T
function atomic_compare_exchange<T>(atomic: Atomic<T>, expected: T, desired: T) -> bool
function atomic_fetch_add<T>(atomic: Atomic<T>, value: T) -> T
function atomic_fetch_sub<T>(atomic: Atomic<T>, value: T) -> T

# Channels
struct Channel<T> {
    buffer: array<T>, read_index: i32, write_index: i32,
    mutex: Mutex, condition: Condition
}

function channel_create<T>(capacity: i32) -> Channel<T>
function channel_send<T>(channel: Channel<T>, value: T) -> void
function channel_receive<T>(channel: Channel<T>) -> T
function channel_try_send<T>(channel: Channel<T>, value: T) -> bool
function channel_try_receive<T>(channel: Channel<T>) -> Option<T>

# Parallel algorithms
function parallel_for<T>(range: Range, body: fn(i32) -> T) -> array<T>
function parallel_map<T, U>(arr: array<T>, mapper: fn(T) -> U) -> array<U>
function parallel_filter<T>(arr: array<T>, predicate: fn(T) -> bool) -> array<T>
function parallel_reduce<T>(arr: array<T>, initial: T, accumulator: fn(T, T) -> T) -> T
```

### `std/crypto`

Cryptographic functions.

```flow
# Hashing
function sha256(data: array<u8>) -> array<u8>
function sha512(data: array<u8>) -> array<u8>
function md5(data: array<u8>) -> array<u8>
function crc32(data: array<u8>) -> u32

# Encryption
function aes_encrypt(key: array<u8>, data: array<u8>) -> array<u8>
function aes_decrypt(key: array<u8>, data: array<u8>) -> array<u8>
function rsa_encrypt(public_key: array<u8>, data: array<u8>) -> array<u8>
function rsa_decrypt(private_key: array<u8>, data: array<u8>) -> array<u8>

# Random numbers
function random_bytes(size: i32) -> array<u8>
function random_u32() -> u32
function random_u64() -> u64
function random_f32() -> f32
function random_f64() -> f64
function random_range(min: i32, max: i32) -> i32
```

---

## Compiler Directives

### Optimization Directives

```flow
# Force inlining
inline function fast_add(a: i32, b: i32) -> i32 {
    return a + b
}

# Mark as hot path
hot function critical_section() -> void {
    # This function will be heavily optimized
}

# Export symbol
export function public_api() -> i32 {
    return 42
}

# Private symbol (default)
private function internal_helper() -> void {
    # Not visible outside module
}
```

### Memory Directives

```flow
# Align struct to specific boundary
align(16) struct AlignedStruct {
    data: array<f32, 4>
}

# Pack struct (no padding)
packed struct PackedStruct {
    a: i8, b: i32, c: i8
}
```

### Target Directives

```flow
# Target-specific code
target("x86_64") {
    function optimized_for_x86() -> void {
        # x86_64 specific optimizations
    }
}

target("arm64") {
    function optimized_for_arm() -> void {
        # ARM64 specific optimizations
    }
}
```

---

## Foreign Function Interface

### Foreign Declarations

```flow
foreign {
    # C standard library
    function malloc(size: i32) -> ptr
    function free(ptr: ptr) -> void
    function printf(format: string, ...) -> i32
    function scanf(format: string, ...) -> i32
    
    # POSIX
    function open(path: string, flags: i32) -> i32
    function close(fd: i32) -> i32
    function read(fd: i32, buf: ptr, count: i32) -> i32
    function write(fd: i32, buf: ptr, count: i32) -> i32
    
    # OpenGL
    function glClear(mask: u32) -> void
    function glBegin(mode: u32) -> void
    function glEnd() -> void
    function glVertex3f(x: f32, y: f32, z: f32) -> void
}
```

### Callback Functions

```flow
# Define callback type
type Callback = fn(i32) -> void

# Foreign function that takes callback
foreign {
    function register_callback(callback: Callback) -> void
    function call_registered_callback(value: i32) -> void
}

# FLOW callback function
function my_callback(value: i32) -> void {
    printf("Callback called with: %d\n", value)
}

function main() -> i32 {
    register_callback(my_callback)
    call_registered_callback(42)
    return 0
}
```

### Struct Interop

```flow
# C-compatible struct
packed struct CStruct {
    field1: i32,
    field2: f32,
    field3: array<u8, 16>
}

foreign {
    function process_c_struct(data: ptr) -> i32
}

function demo_c_interop() -> i32 {
    let c_data = CStruct {
        field1: 42,
        field2: 3.14,
        field3: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    }
    
    return process_c_struct(&c_data)
}
```

---

## Error Codes

### Standard Error Codes

```flow
const ERROR_NONE: i32 = 0
const ERROR_INVALID_ARGUMENT: i32 = 1
const ERROR_OUT_OF_MEMORY: i32 = 2
const ERROR_FILE_NOT_FOUND: i32 = 3
const ERROR_PERMISSION_DENIED: i32 = 4
const ERROR_ALREADY_EXISTS: i32 = 5
const ERROR_NOT_FOUND: i32 = 6
const ERROR_NOT_IMPLEMENTED: i32 = 7
const ERROR_TIMEOUT: i32 = 8
const ERROR_NETWORK_ERROR: i32 = 9
const ERROR_PARSE_ERROR: i32 = 10
```

### Error Handling Utilities

```flow
function get_error_message(code: i32) -> string
function is_error(code: i32) -> bool
function is_success(code: i32) -> bool
```

---

## Version Information

### Runtime Version

```flow
function flow_version() -> string
function flow_version_major() -> i32
function flow_version_minor() -> i32
function flow_version_patch() -> i32
function flow_build_info() -> string
```

### Target Information

```flow
function target_architecture() -> string
function target_os() -> string
function target_vendor() -> string
function target_environment() -> string
```

---

This API reference provides comprehensive documentation for all FLOW language features, built-in functions, and standard library modules. Use this as your primary reference when developing FLOW applications.
