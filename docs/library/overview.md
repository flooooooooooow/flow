# FLOW Standard Library Reference

The FLOW standard library provides a comprehensive set of modules for common programming tasks.

## Table of Contents

- [Core Types](#core-types)
- [Math Operations](#math-operations)
- [String Manipulation](#string-manipulation)
- [Array Operations](#array-operations)
- [File I/O](#file-io)
- [Memory Management](#memory-management)
- [Graphics and Rendering](#graphics-and-rendering)
- [Testing Framework](#testing-framework)
- [Concurrency](#concurrency)

---

## Core Types

### `std/core.flow`

Provides fundamental types and operations.

#### Constants

```flow
const INT_MIN: i32 = -2147483648
const INT_MAX: i32 = 2147483647
const FLOAT_PI: f32 = 3.14159265359
const FLOAT_E: f32 = 2.71828182846
const BOOL_TRUE: bool = true
const BOOL_FALSE: bool = false
```

#### Type Utilities

```flow
# Get the size of a type in bytes
function sizeof<T>(type: Type<T>) -> i32

# Get the alignment of a type in bytes
function alignof<T>(type: Type<T>) -> i32

# Get the offset of a field in a struct
function offsetof<T>(struct: Type<T>, field: string) -> i32

# Type introspection
function type_name<T>(value: T) -> string
function is_same_type<T, U>(a: T, b: U) -> bool
```

#### Memory Operations

```flow
# Copy memory
function memcpy(dest: ptr, src: ptr, size: i32) -> ptr

# Fill memory with a value
function memset(dest: ptr, value: i8, size: i32) -> ptr

# Compare memory
function memcmp(a: ptr, b: ptr, size: i32) -> i32

# Move memory (handles overlapping regions)
function memmove(dest: ptr, src: ptr, size: i32) -> ptr
```

---

## Math Operations

### `std/math.flow`

Comprehensive mathematical functions and constants.

#### Constants

```flow
const PI: f32 = 3.14159265358979323846
const E: f32 = 2.71828182845904523536
const SQRT_2: f32 = 1.41421356237309504880
const SQRT_PI: f32 = 1.77245385090551602729
const LN_2: f32 = 0.69314718055994530942
const LN_10: f32 = 2.30258509299404568402
```

#### Basic Operations

```flow
# Absolute value
function abs(x: i32) -> i32
function abs(x: f32) -> f32
function abs(x: f64) -> f64

# Minimum and maximum
function min(a: i32, b: i32) -> i32
function max(a: i32, b: i32) -> i32
function min(a: f32, b: f32) -> f32
function max(a: f32, b: f32) -> f32

# Clamping
function clamp(x: f32, min: f32, max: f32) -> f32
function clamp(x: i32, min: i32, max: i32) -> i32

# Linear interpolation
function lerp(a: f32, b: f32, t: f32) -> f32
function lerp(a: f64, b: f64, t: f64) -> f64
```

#### Trigonometric Functions

```flow
# Basic trigonometry
function sin(x: f32) -> f32
function cos(x: f32) -> f32
function tan(x: f32) -> f32

# Inverse trigonometry
function asin(x: f32) -> f32
function acos(x: f32) -> f32
function atan(x: f32) -> f32
function atan2(y: f32, x: f32) -> f32

# Hyperbolic functions
function sinh(x: f32) -> f32
function cosh(x: f32) -> f32
function tanh(x: f32) -> f32
```

#### Exponential and Logarithmic

```flow
# Exponential
function exp(x: f32) -> f32
function exp2(x: f32) -> f32
function pow(x: f32, y: f32) -> f32

# Logarithmic
function log(x: f32) -> f32
function log2(x: f32) -> f32
function log10(x: f32) -> f32

# Roots
function sqrt(x: f32) -> f32
function cbrt(x: f32) -> f32
```

#### Rounding

```flow
function floor(x: f32) -> f32
function ceil(x: f32) -> f32
function round(x: f32) -> f32
function trunc(x: f32) -> f32
```

#### Vector Operations

```flow
struct Vec2 {
    x: f32,
    y: f32
}

struct Vec3 {
    x: f32,
    y: f32,
    z: f32
}

struct Vec4 {
    x: f32,
    y: f32,
    z: f32,
    w: f32
}

# Vector arithmetic
function add(a: Vec2, b: Vec2) -> Vec2
function sub(a: Vec2, b: Vec2) -> Vec2
function mul(a: Vec2, s: f32) -> Vec2
function div(a: Vec2, s: f32) -> Vec2

# Vector operations
function dot(a: Vec2, b: Vec2) -> f32
function cross(a: Vec3, b: Vec3) -> Vec3
function length(v: Vec2) -> f32
function normalize(v: Vec2) -> Vec2
function distance(a: Vec2, b: Vec2) -> f32
```

#### Matrix Operations

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

# Matrix arithmetic
function mul(a: Mat2, b: Mat2) -> Mat2
function mul(m: Mat2, v: Vec2) -> Vec2
function transpose(m: Mat2) -> Mat2
function determinant(m: Mat2) -> f32
function inverse(m: Mat2) -> Mat2

# Matrix creation
function mat2_identity() -> Mat2
function mat2_rotation(angle: f32) -> Mat2
function mat2_scale(sx: f32, sy: f32) -> Mat2
function mat2_translation(tx: f32, ty: f32) -> Mat3
```

---

## String Manipulation

### `std/string.flow`

Comprehensive string operations.

#### Basic Operations

```flow
# String length
function len(s: string) -> i32

# String concatenation
function concat(a: string, b: string) -> string

# String comparison
function equal(a: string, b: string) -> bool
function compare(a: string, b: string) -> i32

# Substring
function substring(s: string, start: i32, length: i32) -> string
function slice(s: string, start: i32, end: i32) -> string
```

#### Searching and Splitting

```flow
# Find substring
function find(s: string, pattern: string) -> i32
function find_from(s: string, pattern: string, start: i32) -> i32
function rfind(s: string, pattern: string) -> i32

# Check if contains
function contains(s: string, pattern: string) -> bool
function starts_with(s: string, prefix: string) -> bool
function ends_with(s: string, suffix: string) -> bool

# Split and join
function split(s: string, delimiter: string) -> array<string>
function join(parts: array<string>, delimiter: string) -> string
```

#### Case Operations

```flow
function to_upper(s: string) -> string
function to_lower(s: string) -> string
function capitalize(s: string) -> string
function title_case(s: string) -> string
```

#### Trimming and Padding

```flow
function trim(s: string) -> string
function trim_left(s: string) -> string
function trim_right(s: string) -> string
function pad_left(s: string, width: i32, char: string) -> string
function pad_right(s: string, width: i32, char: string) -> string
```

#### Character Operations

```flow
function is_digit(c: string) -> bool
function is_alpha(c: string) -> bool
function is_alnum(c: string) -> bool
function is_space(c: string) -> bool
function is_lower(c: string) -> bool
function is_upper(c: string) -> bool
```

#### String Formatting

```flow
# Format strings with placeholders
function format(fmt: string, args: array<any>) -> string

# Common formatting functions
function format_int(value: i32, base: i32) -> string
function format_float(value: f32, precision: i32) -> string
function format_bool(value: bool) -> string
```

---

## Array Operations

### `std/array.flow`

Powerful array manipulation functions.

#### Basic Operations

```flow
# Array information
function len<T>(arr: array<T>) -> i32
function is_empty<T>(arr: array<T>) -> bool
function capacity<T>(arr: array<T>) -> i32

# Element access
function get<T>(arr: array<T>, index: i32) -> T
function set<T>(arr: array<T>, index: i32, value: T) -> void
function first<T>(arr: array<T>) -> T
function last<T>(arr: array<T>) -> T
```

#### Searching

```flow
# Linear search
function find<T>(arr: array<T>, value: T) -> i32
function contains<T>(arr: array<T>, value: T) -> bool
function index_of<T>(arr: array<T>, value: T) -> i32
function last_index_of<T>(arr: array<T>, value: T) -> i32

# Binary search (requires sorted array)
function binary_search<T>(arr: array<T>, value: T) -> i32
function lower_bound<T>(arr: array<T>, value: T) -> i32
function upper_bound<T>(arr: array<T>, value: T) -> i32
```

#### Sorting

```flow
# Basic sorting
function sort<T>(arr: array<T>) -> void
function sort_by<T>(arr: array<T>, comparator: fn(T, T) -> i32) -> void
function reverse<T>(arr: array<T>) -> void

# Check if sorted
function is_sorted<T>(arr: array<T>) -> bool
function is_sorted_by<T>(arr: array<T>, comparator: fn(T, T) -> i32) -> bool
```

#### Filtering and Mapping

```flow
# Filter elements
function filter<T>(arr: array<T>, predicate: fn(T) -> bool) -> array<T>
function filter_map<T, U>(arr: array<T>, mapper: fn(T) -> Option<U>) -> array<U>

# Map elements
function map<T, U>(arr: array<T>, mapper: fn(T) -> U) -> array<U>
function map_enumerate<T, U>(arr: array<T>, mapper: fn(i32, T) -> U) -> array<U>

# Flat map
function flat_map<T, U>(arr: array<T>, mapper: fn(T) -> array<U>) -> array<U>
```

#### Reductions

```flow
# Reduce operations
function reduce<T>(arr: array<T>, initial: T, accumulator: fn(T, T) -> T) -> T
function reduce_enumerate<T>(arr: array<T>, initial: T, accumulator: fn(T, i32, T) -> T) -> T

# Common reductions
function sum<T: Number>(arr: array<T>) -> T
function product<T: Number>(arr: array<T>) -> T
function min<T: Ord>(arr: array<T>) -> T
function max<T: Ord>(arr: array<T>) -> T
function average<T: Number>(arr: array<T>) -> f32
```

#### Array Manipulation

```flow
# Adding and removing elements
function push<T>(arr: array<T>, value: T) -> void
function pop<T>(arr: array<T>) -> T
function insert<T>(arr: array<T>, index: i32, value: T) -> void
function remove<T>(arr: array<T>, index: i32) -> T
function remove_at<T>(arr: array<T>, index: i32) -> void

# Slicing and chunking
function slice<T>(arr: array<T>, start: i32, end: i32) -> array<T>
function chunk<T>(arr: array<T>, size: i32) -> array<array<T>>
function window<T>(arr: array<T>, size: i32) -> array<array<T>>

# Combining arrays
function concat<T>(a: array<T>, b: array<T>) -> array<T>
function repeat<T>(arr: array<T>, count: i32) -> array<T>
function interleave<T>(a: array<T>, b: array<T>) -> array<T>
```

#### Set Operations

```flow
function unique<T>(arr: array<T>) -> array<T>
function union<T>(a: array<T>, b: array<T>) -> array<T>
function intersection<T>(a: array<T>, b: array<T>) -> array<T>
function difference<T>(a: array<T>, b: array<T>) -> array<T>
function symmetric_difference<T>(a: array<T>, b: array<T>) -> array<T>
```

---

## File I/O

### `std/io.flow`

File system operations and I/O handling.

#### File Operations

```flow
# File existence and properties
function exists(path: string) -> bool
function is_file(path: string) -> bool
function is_directory(path: string) -> bool
function file_size(path: string) -> i64
function file_modified(path: string) -> f64

# File reading and writing
function read_file(path: string) -> string
function write_file(path: string, content: string) -> void
function append_file(path: string, content: string) -> void
function read_bytes(path: string) -> array<u8>
function write_bytes(path: string, data: array<u8>) -> void
```

#### Directory Operations

```flow
# Directory creation and removal
function create_directory(path: string) -> void
function create_directories(path: string) -> void
function remove_directory(path: string) -> void
function remove_directories(path: string) -> void

# Directory listing
function list_directory(path: string) -> array<string>
function list_files(path: string) -> array<string>
function list_directories(path: string) -> array<string>

# Directory operations
function current_directory() -> string
function set_current_directory(path: string) -> void
function parent_directory(path: string) -> string
function join_path(parts: array<string>) -> string
```

#### Path Operations

```flow
function basename(path: string) -> string
function dirname(path: string) -> string
function extension(path: string) -> string
function filename(path: string) -> string
function is_absolute(path: string) -> bool
function normalize_path(path: string) -> string
function relative_path(from: string, to: string) -> string
```

#### Stream I/O

```flow
struct FileStream {
    handle: i32,
    mode: FileMode
}

enum FileMode {
    Read,
    Write,
    Append,
    ReadWrite
}

function open_file(path: string, mode: FileMode) -> FileStream
function close_file(stream: FileStream) -> void
function read_line(stream: FileStream) -> string
function write_line(stream: FileStream, line: string) -> void
function flush(stream: FileStream) -> void
```

---

## Memory Management

### `std/memory.flow`

Advanced memory management utilities.

#### Memory Pools

```flow
struct MemoryPool {
    start: ptr,
    current: ptr,
    end: ptr,
    page_size: i32
}

function create_pool(initial_size: i32) -> MemoryPool
function destroy_pool(pool: MemoryPool) -> void
function pool_alloc(pool: MemoryPool, size: i32) -> ptr
function pool_reset(pool: MemoryPool) -> void
```

#### Arena Allocator

```flow
struct Arena {
    current_block: ptr,
    blocks: array<ptr>,
    total_allocated: i32
}

function arena_create() -> Arena
function arena_destroy(arena: Arena) -> void
function arena_alloc(arena: Arena, size: i32) -> ptr
function arena_reset(arena: Arena) -> void
```

#### Reference Counting

```flow
struct RefCounted<T> {
    value: T,
    count: i32
}

function ref_create<T>(value: T) -> RefCounted<T>
function ref_acquire<T>(ref: RefCounted<T>) -> RefCounted<T>
function ref_release<T>(ref: RefCounted<T>) -> void
function ref_count<T>(ref: RefCounted<T>) -> i32
```

---

## Graphics and Rendering

### `std/graphics.flow`

2D and 3D graphics utilities.

#### Colors

```flow
struct Color {
    r: f32,
    g: f32,
    b: f32,
    a: f32
}

# Color constants
const COLOR_BLACK: Color = Color { r: 0.0, g: 0.0, b: 0.0, a: 1.0 }
const COLOR_WHITE: Color = Color { r: 1.0, g: 1.0, b: 1.0, a: 1.0 }
const COLOR_RED: Color = Color { r: 1.0, g: 0.0, b: 0.0, a: 1.0 }
const COLOR_GREEN: Color = Color { r: 0.0, g: 1.0, b: 0.0, a: 1.0 }
const COLOR_BLUE: Color = Color { r: 0.0, g: 0.0, b: 1.0, a: 1.0 }

# Color operations
function rgb_to_hsv(color: Color) -> Vec3
function hsv_to_rgb(hsv: Vec3) -> Color
function lerp_color(a: Color, b: Color, t: f32) -> Color
function brightness(color: Color) -> f32
function contrast(color: Color, factor: f32) -> Color
```

#### 2D Primitives

```flow
struct Rectangle {
    x: f32,
    y: f32,
    width: f32,
    height: f32
}

struct Circle {
    center: Vec2,
    radius: f32
}

struct Line {
    start: Vec2,
    end: Vec2
}

# Geometry operations
function contains_point(rect: Rectangle, point: Vec2) -> bool
function intersects(a: Rectangle, b: Rectangle) -> bool
function distance_point_to_line(point: Vec2, line: Line) -> f32
function point_in_circle(point: Vec2, circle: Circle) -> bool
```

#### 3D Primitives

```flow
struct Plane {
    normal: Vec3,
    distance: f32
}

struct Sphere {
    center: Vec3,
    radius: f32
}

struct AABB {
    min: Vec3,
    max: Vec3
}

# 3D operations
function ray_plane_intersection(ray: Ray, plane: Plane) -> Option<f32>
function ray_sphere_intersection(ray: Ray, sphere: Sphere) -> Option<f32>
function aabb_contains_point(aabb: AABB, point: Vec3) -> bool
function aabb_intersects(a: AABB, b: AABB) -> bool
```

---

## Testing Framework

### `std/test.flow`

Comprehensive testing framework.

#### Test Definition

```flow
# Basic test
test "test_name" {
    # Test code here
    assert(condition)
}

# Test with setup and teardown
test "test_name" {
    setup {
        # Setup code
    }
    teardown {
        # Teardown code
    }
    # Test code here
}

# Parameterized test
test "test_name" with parameters {
    (input: i32, expected: i32) -> {
        assert(add(input, 1) == expected)
    }
    (1, 2),
    (2, 3),
    (3, 4)
}
```

#### Assertions

```flow
# Basic assertions
function assert(condition: bool) -> void
function assert_true(condition: bool) -> void
function assert_false(condition: bool) -> void

# Value assertions
function assert_equal<T>(actual: T, expected: T) -> void
function assert_not_equal<T>(actual: T, expected: T) -> void
function assert_less<T: Ord>(a: T, b: T) -> void
function assert_less_equal<T: Ord>(a: T, b: T) -> void
function assert_greater<T: Ord>(a: T, b: T) -> void
function assert_greater_equal<T: Ord>(a: T, b: T) -> void

# String assertions
function assert_contains(actual: string, expected: string) -> void
function assert_starts_with(actual: string, expected: string) -> void
function assert_ends_with(actual: string, expected: string) -> void

# Array assertions
function assert_array_equal<T>(actual: array<T>, expected: array<T>) -> void
function assert_array_contains<T>(arr: array<T>, value: T) -> void

# Floating point assertions
function assert_approx_equal(actual: f32, expected: f32, epsilon: f32) -> void
```

#### Test Suites

```flow
suite "Math Operations" {
    test "addition" {
        assert_equal(add(2, 3), 5)
    }
    
    test "subtraction" {
        assert_equal(sub(5, 3), 2)
    }
    
    test "multiplication" {
        assert_equal(mul(4, 3), 12)
    }
}
```

#### Mocking and Fakes

```flow
# Mock interface
mock FileSystem {
    function read(path: string) -> string
    function write(path: string, content: string) -> void
}

# Use mock in test
test "file operations" {
    let mock = FileSystem.mock()
    mock.read.returns("mock content")
    
    let result = process_file(mock, "test.txt")
    
    assert_equal(result, "processed: mock content")
    mock.write.assert_called_with("test.txt", "processed: mock content")
}
```

---

## Concurrency

### `std/concurrency.flow`

Concurrency and parallelism utilities.

#### Threads

```flow
struct Thread {
    id: i32,
    handle: ptr
}

function thread_create(func: fn() -> void) -> Thread
function thread_join(thread: Thread) -> void
function thread_sleep(milliseconds: i32) -> void
function thread_yield() -> void
```

#### Mutex and Locks

```flow
struct Mutex {
    handle: ptr
}

function mutex_create() -> Mutex
function mutex_destroy(mutex: Mutex) -> void
function mutex_lock(mutex: Mutex) -> void
function mutex_unlock(mutex: Mutex) -> void
function mutex_try_lock(mutex: Mutex) -> bool
```

#### Atomic Operations

```flow
struct Atomic<T> {
    value: T
}

function atomic_load<T>(atomic: Atomic<T>) -> T
function atomic_store<T>(atomic: Atomic<T>, value: T) -> void
function atomic_exchange<T>(atomic: Atomic<T>, value: T) -> T
function atomic_compare_exchange<T>(atomic: Atomic<T>, expected: T, desired: T) -> bool
function atomic_fetch_add<T>(atomic: Atomic<T>, value: T) -> T
function atomic_fetch_sub<T>(atomic: Atomic<T>, value: T) -> T
```

#### Channels

```flow
struct Channel<T> {
    buffer: array<T>,
    read_index: i32,
    write_index: i32,
    mutex: Mutex,
    condition: Condition
}

function channel_create<T>(capacity: i32) -> Channel<T>
function channel_send<T>(channel: Channel<T>, value: T) -> void
function channel_receive<T>(channel: Channel<T>) -> T
function channel_try_send<T>(channel: Channel<T>, value: T) -> bool
function channel_try_receive<T>(channel: Channel<T>) -> Option<T>
```

#### Parallel Algorithms

```flow
function parallel_for<T>(range: Range, body: fn(i32) -> T) -> array<T>
function parallel_map<T, U>(arr: array<T>, mapper: fn(T) -> U) -> array<U>
function parallel_filter<T>(arr: array<T>, predicate: fn(T) -> bool) -> array<T>
function parallel_reduce<T>(arr: array<T>, initial: T, accumulator: fn(T, T) -> T) -> T
```

---

## Error Handling

### `std/error.flow`

Comprehensive error handling utilities.

#### Error Types

```flow
struct Error {
    code: i32,
    message: string,
    source: string
}

enum Result<T, E> {
    Ok(T),
    Err(E)
}

enum Option<T> {
    Some(T),
    None
}
```

#### Error Operations

```flow
function create_error(code: i32, message: string) -> Error
function wrap_error(error: Error, context: string) -> Error
function error_to_string(error: Error) -> string

# Result operations
function is_ok<T, E>(result: Result<T, E>) -> bool
function is_err<T, E>(result: Result<T, E>) -> bool
function unwrap<T, E>(result: Result<T, E>) -> T
function unwrap_or<T, E>(result: Result<T, E>, default: T) -> T
function map<T, U, E>(result: Result<T, E>, mapper: fn(T) -> U) -> Result<U, E>

# Option operations
function is_some<T>(option: Option<T>) -> bool
function is_none<T>(option: Option<T>) -> bool
function unwrap<T>(option: Option<T>) -> T
function unwrap_or<T>(option: Option<T>, default: T) -> T
function map<T, U>(option: Option<T>, mapper: fn(T) -> U) -> Option<U>
```

#### Panic and Recovery

```flow
function panic(message: string) -> void
function assert(condition: bool, message: string) -> void
function unreachable(message: string) -> void

# Error handling with try-catch
function try_catch<T>(body: fn() -> T, handler: fn(Error) -> T) -> T
```

---

## Performance and Profiling

### `std/profiling.flow`

Performance measurement and optimization tools.

#### Timing

```flow
struct Timer {
    start_time: f64
}

function timer_start() -> Timer
function timer_elapsed(timer: Timer) -> f64
function timer_stop(timer: Timer) -> f64
```

#### Profiling

```flow
struct Profile {
    samples: array<f64>,
    total_time: f64,
    call_count: i32
}

function profile_start(name: string) -> void
function profile_end(name: string) -> void
function profile_get(name: string) -> Profile
function profile_reset(name: string) -> void
function profile_print_all() -> void
```

#### Benchmarks

```flow
benchmark "addition performance" {
    iterations: 1000000,
    setup: {
        let a = 42
        let b = 24
    },
    run: {
        let result = a + b
    }
}
```

---

## Cryptography

### `std/crypto.flow`

Cryptographic functions and utilities.

#### Hashing

```flow
function sha256(data: array<u8>) -> array<u8>
function sha512(data: array<u8>) -> array<u8>
function md5(data: array<u8>) -> array<u8>
function crc32(data: array<u8>) -> u32
```

#### Encryption

```flow
function aes_encrypt(key: array<u8>, data: array<u8>) -> array<u8>
function aes_decrypt(key: array<u8>, data: array<u8>) -> array<u8>
function rsa_encrypt(public_key: array<u8>, data: array<u8>) -> array<u8>
function rsa_decrypt(private_key: array<u8>, data: array<u8>) -> array<u8>
```

#### Random Numbers

```flow
function random_bytes(size: i32) -> array<u8>
function random_u32() -> u32
function random_u64() -> u64
function random_f32() -> f32
function random_f64() -> f64
function random_range(min: i32, max: i32) -> i32
```

---

This standard library reference provides a comprehensive overview of all available modules and functions in FLOW. Each module is designed to be efficient, type-safe, and easy to use while maintaining the performance characteristics that FLOW is known for.
