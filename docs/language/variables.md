# Variables and Constants

This section covers variable declarations, constants, and variable management in FLOW.

## 🔤 Variable Declarations

### Basic Declaration

```
let x = 42
let name = "Alice"
let pi = 3.14159
```

### Typed Declaration

```
let x: i32 = 42
let name: string = "Bob"
let pi: f64 = 3.14159265359
```

### Multiple Declaration

```
let x = 1, y = 2, z = 3
let a: i32 = 10, b: f32 = 3.14
```

## 📦 Constants

### Constant Declaration

```
const PI = 3.14159
const MAX_USERS = 1000
const APP_NAME = "FLOW App"
```

### Typed Constants

```
const PI: f64 = 3.141592653589793
const BUFFER_SIZE: i32 = 1024
const VERSION: string = "1.0.0"
```

### Global vs Local Constants

```
# Global constant (file level)
const GLOBAL_CONFIG = "production"

function main() -> i32 {
    # Local constant
    const LOCAL_TIMEOUT = 5000
    print(GLOBAL_CONFIG)
    return 0
}
```

## 🔄 Variable Assignment

### Initial Assignment

```
let x = 10        # Declaration with initialization
x = 20           # Reassignment
```

### Type-Safe Assignment

```
let x: i32 = 10   # Must assign i32 value
x = 15           # OK: still i32
# x = 3.14       # Error: cannot assign f32 to i32 variable
```

### Complex Assignment

```
let point = Point { x: 10.0, y: 20.0 }
point.x = 15.0   # Field assignment
point.y = 25.0

let arr = [1, 2, 3, 4, 5]
arr[0] = 10       # Array element assignment
arr[2] = 30
```

## 🎯 Variable Scope

### Function Scope

```
function demo() -> i32 {
    let x = 10        # Function-scoped variable
    
    if x > 5 {
        let y = 20    # Block-scoped variable
        return x + y  # OK: both x and y accessible
    }
    
    # return y        # Error: y not accessible outside if block
    return x
}
```

### Shadowing

```
let x = 10          # Outer variable

function test() -> i32 {
    let x = 20      # Shadows outer x
    return x        # Returns 20
}

function main() -> i32 {
    let result = test()
    print(string(result))  # Prints 20
    print(string(x))        # Prints 10 (original x unchanged)
    return 0
}
```

## 🔍 Type Inference

### Automatic Type Detection

```
let x = 42           # Inferred as i32
let y = 3.14         # Inferred as f32
let name = "Alice"   # Inferred as string
let flag = true      # Inferred as bool
```

### Context-Based Inference

```
function add(a: i32, b: i32) -> i32 {
    return a + b
}

let result = add(5, 3)  # result inferred as i32 (function return type)
```

### Inference with Arrays

```
let numbers = [1, 2, 3, 4, 5]     # Inferred as [i32]
let floats = [1.0, 2.0, 3.0]       # Inferred as [f32]
let mixed = [1, 2.0, 3]            # Error: mixed types not allowed
```

## 🏗️ Struct Variables

### Struct Declaration

```
struct Point {
    x: f32,
    y: f32
}

let p = Point { x: 10.0, y: 20.0 }
```

### Field Access and Assignment

```
let p = Point { x: 10.0, y: 20.0 }
p.x = 15.0           # Field assignment
p.y = p.x + 5.0      # Assignment with expression

let x_coord = p.x    # Field access
```

### Nested Structs

```
struct Address {
    street: string,
    city: string
}

struct Person {
    name: string,
    address: Address
}

let person = Person {
    name: "Alice",
    address: Address {
        street: "123 Main St",
        city: "NYC"
    }
}

person.address.city = "Boston"  # Nested field assignment
```

## 📊 Array Variables

### Array Declaration

```
let numbers = [1, 2, 3, 4, 5]           # Dynamic array
let fixed = [i32; 10]                    # Fixed-size array (uninitialized)
let initialized = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # [i32; 10]
```

### Array Element Assignment

```
let arr = [1, 2, 3, 4, 5]
arr[0] = 10        # First element
arr[2] = 30        # Third element
arr[4] = 50        # Last element
```

### Array Operations

```
let arr = [1, 2, 3, 4, 5]
let length = length(arr)     # Get array length
let first = arr[0]           # Access first element
let last = arr[length - 1]   # Access last element
```

## 🔧 Variable Patterns

### Counter Pattern

```
function count_to_n(n: i32) -> void {
    let i = 0
    while i < n {
        print("Count: " + string(i))
        i = i + 1
    }
}
```

### Accumulator Pattern

```
function sum_array(arr: [i32]) -> i32 {
    let sum = 0
    let i = 0
    while i < length(arr) {
        sum = sum + arr[i]
        i = i + 1
    }
    return sum
}
```

### Swap Pattern

```
function swap(a: i32, b: i32) -> (i32, i32) {
    let temp = a
    a = b
    b = temp
    return (a, b)
}
```

## 🎮 Mutable vs Immutable

### Immutable Variables (Default)

```
let x = 10
# x = 20        # Error: let variables are immutable by default
```

### Mutable Variables (Future)

```
# Future syntax for mutable variables
mut x = 10
x = 20          # OK: mutable variable
```

### Constants vs Variables

```
const PI = 3.14159    # Compile-time constant
let x = 10           # Runtime variable (immutable)
# PI = 3.14          # Error: cannot change constant
# x = 20             # Error: cannot change let variable
```

## 🔍 Variable Inspection

### Type Checking

```
# Future: type inspection
typeof(x)              # Get type of variable
is_type<i32>(x)        # Check if variable is i32
```

### Variable Information

```
# Future: debug information
debug_info(x)          # Show variable type and value
sizeof(x)              # Get memory size
```

## 🚀 Performance Considerations

### Stack vs Heap

```
# Stack allocation (fast)
let x = 42
let point = Point { x: 10.0, y: 20.0 }

# Heap allocation (slower, for large data)
let large_array = [i32; 1000000]
```

### Variable Lifetime

```
function demo() -> i32 {
    let x = 10        # Created when function enters
    # ... use x ...
    return x          # x destroyed when function exits
}
```

### Memory Layout

```
struct Example {
    a: i8,    # 1 byte
    b: i32,   # 4 bytes (aligned to 4)
    c: f32,   # 4 bytes
    d: i64    # 8 bytes (aligned to 8)
}
# Total: 16 bytes with padding
```

## 🎯 Best Practices

1. **Use `const` for values that never change**
2. **Prefer `let` over mutable variables when possible**
3. **Initialize variables at declaration**
4. **Use descriptive variable names**
5. **Keep variable scope as small as possible**
6. **Avoid variable shadowing when it creates confusion**
7. **Use type annotations for clarity in complex code**

## 🔧 Common Patterns

### Configuration Constants

```
const CONFIG_FILE = "config.json"
const MAX_CONNECTIONS = 100
const TIMEOUT_SECONDS = 30
```

### State Variables

```
function process_data() -> i32 {
    let processed_count = 0
    let error_count = 0
    
    # ... processing logic ...
    
    return processed_count
}
```

### Temporary Variables

```
function calculate_distance(x1: f32, y1: f32, x2: f32, y2: f32) -> f32 {
    let dx = x2 - x1
    let dy = y2 - y1
    return sqrt(dx * dx + dy * dy)
}
```

Variables and constants in FLOW provide a solid foundation for building reliable and maintainable programs with strong type safety and clear semantics.
