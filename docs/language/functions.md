# Functions

Functions are the primary building blocks of FLOW programs, enabling code organization, reuse, and abstraction.

## 🎯 Function Definition

### Basic Function

```
function add(a: i32, b: i32) -> i32 {
    return a + b
}
```

### Function Without Return Value

```
function greet(name: string) -> void {
    print("Hello, " + name + "!")
}
```

### Function Without Parameters

```
function get_app_name() -> string {
    return "FLOW Application"
}
```

### Minimal Function

```
function do_nothing() -> void {
    # Empty function body
}
```

## 📝 Parameters

### Typed Parameters

```
function calculate_area(width: f32, height: f32) -> f32 {
    return width * height
}
```

### Multiple Parameters

```
function create_person(name: string, age: i32, city: string) -> Person {
    return Person {
        name: name,
        age: age,
        address: Address { city: city, street: "" }
    }
}
```

### Array Parameters

```
function sum_array(numbers: [i32]) -> i32 {
    let sum = 0
    let i = 0
    while i < length(numbers) {
        sum = sum + numbers[i]
        i = i + 1
    }
    return sum
}
```

### Struct Parameters

```
function distance(p1: Point, p2: Point) -> f32 {
    let dx = p2.x - p1.x
    let dy = p2.y - p1.y
    return sqrt(dx * dx + dy * dy)
}
```

## 🔄 Return Values

### Single Return Value

```
function multiply(a: i32, b: i32) -> i32 {
    return a * b
}
```

### Multiple Return Values (Future)

```
function divide_and_remainder(a: i32, b: i32) -> (i32, i32) {
    return (a / b, a % b)
}
```

### Early Return

```
function absolute_value(x: i32) -> i32 {
    if x < 0 {
        return -x
    }
    return x
}
```

### Void Return

```
function print_message(msg: string) -> void {
    print("Message: " + msg)
    return  # Optional explicit return
}
```

## 🚀 Function Calls

### Basic Call

```
let result = add(5, 3)
greet("Alice")
```

### Call with Expressions

```
let area = calculate_area(width + 2, height * 1.5)
let total = sum_array([1, 2, 3, 4, 5])
```

### Nested Calls

```
let result = add(multiply(2, 3), 4)  # add(6, 4) = 10
```

### Call as Argument

```
print(string(add(5, 3)))  # Prints "8"
```

## 🏗️ Function Types

### Function Type Notation

```
# Type: (i32, i32) -> i32
let operation: (i32, i32) -> i32 = add

# Type: (string) -> void
let logger: (string) -> void = greet
```

### Higher-Order Functions (Future)

```
function apply_twice(f: (i32) -> i32, value: i32) -> i32 {
    return f(f(value))
}

let result = apply_twice(func(x) { return x * 2 }, 5)  # 5 * 2 * 2 = 20
```

## 📦 Function Organization

### Related Functions

```
# Math functions
function square(x: f32) -> f32 {
    return x * x
}

function cube(x: f32) -> f32 {
    return x * x * x
}

function power(base: f32, exp: i32) -> f32 {
    if exp == 0 {
        return 1.0
    }
    return base * power(base, exp - 1)
}
```

### Utility Functions

```
function is_even(n: i32) -> bool {
    return n % 2 == 0
}

function is_positive(n: i32) -> bool {
    return n > 0
}

function clamp(value: f32, min: f32, max: f32) -> f32 {
    if value < min {
        return min
    }
    if value > max {
        return max
    }
    return value
}
```

## 🎮 Recursive Functions

### Simple Recursion

```
function factorial(n: i32) -> i32 {
    if n <= 1 {
        return 1
    }
    return n * factorial(n - 1)
}
```

### Tail Recursion

```
function factorial_tail(n: i32, acc: i32) -> i32 {
    if n <= 1 {
        return acc
    }
    return factorial_tail(n - 1, acc * n)
}

function factorial(n: i32) -> i32 {
    return factorial_tail(n, 1)
}
```

### Mutual Recursion

```
function is_even(n: i32) -> bool {
    if n == 0 {
        return true
    }
    return is_odd(n - 1)
}

function is_odd(n: i32) -> bool {
    if n == 0 {
        return false
    }
    return is_even(n - 1)
}
```

## 🔧 Function Parameters

### Pass by Value

```
function modify_value(x: i32) -> i32 {
    x = x + 1  # Modifies local copy only
    return x
}

let original = 10
let result = modify_value(original)  # result = 11, original = 10
```

### Struct Parameters

```
function move_point(p: Point, dx: f32, dy: f32) -> Point {
    return Point {
        x: p.x + dx,
        y: p.y + dy
    }
}

let original = Point { x: 10.0, y: 20.0 }
let moved = move_point(original, 5.0, 3.0)  # Creates new point
```

## 🎯 Function Overloading (Future)

```
function add(a: i32, b: i32) -> i32 {
    return a + b
}

function add(a: f32, b: f32) -> f32 {
    return a + b
}

function add(a: string, b: string) -> string {
    return a + b
}
```

## 📚 Standard Library Functions

### String Functions

```
function length(s: string) -> i32
function substring(s: string, start: i32, length: i32) -> string
function to_upper(s: string) -> string
function to_lower(s: string) -> string
```

### Math Functions

```
function sqrt(x: f32) -> f32
function sin(x: f32) -> f32
function cos(x: f32) -> f32
function abs(x: i32) -> i32
function min(a: i32, b: i32) -> i32
function max(a: i32, b: i32) -> i32
```

### Array Functions

```
function length(arr: [T]) -> i32
function append(arr: [T], element: T) -> [T]
function remove(arr: [T], index: i32) -> [T]
```

## 🚀 Performance Considerations

### Inline Functions

```
# Small functions may be inlined by compiler
function small_add(a: i32, b: i32) -> i32 {
    return a + b
}
```

### Function Call Overhead

```
# Prefer loops over recursion for performance
function iterative_sum(n: i32) -> i32 {
    let sum = 0
    let i = 0
    while i < n {
        sum = sum + i
        i = i + 1
    }
    return sum
}
```

### Memory Usage

```
# Functions create stack frames for local variables
function memory_intensive() -> i32 {
    let large_array = [i32; 1000]  # Allocated on stack
    # ... use array ...
    return 0
}  # Array automatically freed when function returns
```

## 🎯 Best Practices

1. **Keep functions small and focused**
2. **Use descriptive function names**
3. **Limit the number of parameters (ideally ≤ 5)**
4. **Use structs to group related parameters**
5. **Prefer iteration over recursion for performance**
6. **Document function behavior with comments**
7. **Handle edge cases in functions**
8. **Use type annotations for clarity**

## 🔧 Common Patterns

### Factory Functions

```
function create_point(x: f32, y: f32) -> Point {
    return Point { x: x, y: y }
}

function create_unit_circle() -> [Point] {
    let points = [Point; 360]
    let i = 0
    while i < 360 {
        let angle = i * 3.14159 / 180.0
        points[i] = Point {
            x: cos(angle),
            y: sin(angle)
        }
        i = i + 1
    }
    return points
}
```

### Validation Functions

```
function validate_email(email: string) -> bool {
    # Simple email validation
    let has_at = contains(email, "@")
    let has_dot = contains(email, ".")
    return has_at and has_dot
}

function validate_age(age: i32) -> bool {
    return age >= 0 and age <= 150
}
```

### Conversion Functions

```
function celsius_to_fahrenheit(c: f32) -> f32 {
    return (c * 9.0 / 5.0) + 32.0
}

function fahrenheit_to_celsius(f: f32) -> f32 {
    return (f - 32.0) * 5.0 / 9.0
}
```

Functions in FLOW provide powerful abstraction capabilities while maintaining type safety and performance.
