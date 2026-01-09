# FLOW Tutorial: Intermediate

Build on the basics with generics, traits, error handling, and more.

## Part 1: Generics

### 1.1 Generic Functions

```flow
# A function that works with any type
function identity<T>(x: T) -> T {
    return x
}

function swap<T>(a: T, b: T) -> T {
    # Returns b (just demonstrating generic usage)
    return b
}

function main() -> i32 {
    let x = identity<i32>(42)
    let y = identity<f64>(3.14)
    let z = identity<string>("hello")
    
    printf("x = %d, y = %f\n", x, y)
    return 0
}
```

### 1.2 Generic Structs

```flow
struct Box<T> {
    value: T
}

struct Pair<A, B> {
    first: A,
    second: B
}

function main() -> i32 {
    let int_box = Box<i32> { value: 42 }
    let float_box = Box<f64> { value: 3.14 }
    
    let pair = Pair<string, i32> {
        first: "Alice",
        second: 30
    }
    
    printf("Box: %d\n", int_box.value)
    printf("Pair: %s is %d\n", pair.first, pair.second)
    
    return 0
}
```

### 1.3 How Generics Work: Monomorphization

FLOW uses **monomorphization** - it generates specialized versions of generic code for each concrete type used.

```flow
# You write:
function identity<T>(x: T) -> T { return x }

let a = identity<i32>(1)
let b = identity<f64>(2.0)

# FLOW generates:
# function identity_i32(x: i32) -> i32 { return x }
# function identity_f64(x: f64) -> f64 { return x }
```

---

## Part 2: Traits

### 2.1 Defining Traits

```flow
trait Display {
    function show(self: Self) -> void
}

trait Comparable {
    function compare(self: Self, other: Self) -> i32
}
```

### 2.2 Implementing Traits

```flow
struct Point {
    x: f32,
    y: f32
}

impl Display for Point {
    function show(self: Point) -> void {
        printf("Point(%f, %f)", self.x, self.y)
    }
}

struct Person {
    name: string,
    age: i32
}

impl Display for Person {
    function show(self: Person) -> void {
        printf("%s (age %d)", self.name, self.age)
    }
}

function main() -> i32 {
    let p = Point { x: 3.0, y: 4.0 }
    Point_Display_show(p)
    printf("\n")
    
    let person = Person { name: "Alice", age: 30 }
    Person_Display_show(person)
    printf("\n")
    
    return 0
}
```

### 2.3 Trait Bounds

```flow
# Require that T implements Display
function print_value<T: Display>(value: T) -> void {
    value.show()
    printf("\n")
}
```

---

## Part 3: Enums (Algebraic Data Types)

### 3.1 Simple Enums

```flow
enum Color {
    Red,
    Green,
    Blue
}

function color_name(c: Color) -> string {
    match c {
        Color::Red => return "red"
        Color::Green => return "green"
        Color::Blue => return "blue"
    }
}

function main() -> i32 {
    let c = Color::Green
    printf("Color: %s\n", color_name(c))
    return 0
}
```

### 3.2 Enums with Data

```flow
enum Shape {
    Circle(radius: f32),
    Rectangle(width: f32, height: f32),
    Triangle(base: f32, height: f32)
}

function area(s: Shape) -> f32 {
    match s {
        Shape::Circle(r) => return 3.14159 * r * r
        Shape::Rectangle(w, h) => return w * h
        Shape::Triangle(b, h) => return 0.5 * b * h
    }
}
```

### 3.3 Option Type

```flow
import "stdlib/option.flow"

function find_index(arr: array<i32, 5>, target: i32) -> Option_i32 {
    for i in 0..5 {
        if arr[i] == target {
            return some_i32(i)
        }
    }
    return none_i32()
}

function main() -> i32 {
    let arr = [10, 20, 30, 40, 50]
    
    let result = find_index(arr, 30)
    if is_some_i32(result) {
        printf("Found at index %d\n", unwrap_i32(result))
    } else {
        printf("Not found\n")
    }
    
    return 0
}
```

### 3.4 Result Type

```flow
import "stdlib/result.flow"

function parse_positive(s: string) -> Result_i32_string {
    let n = atoi(s)
    if n <= 0 {
        return err_i32_string("Not a positive number")
    }
    return ok_i32_string(n)
}

function main() -> i32 {
    let r1 = parse_positive("42")
    if is_ok_i32_string(r1) {
        printf("Parsed: %d\n", unwrap_i32_string(r1))
    }
    
    let r2 = parse_positive("-5")
    if is_err_i32_string(r2) {
        printf("Error: %s\n", unwrap_err_i32_string(r2))
    }
    
    return 0
}
```

---

## Part 4: Lambda Expressions

### 4.1 Basic Lambdas

```flow
function main() -> i32 {
    # Lambda that adds two numbers
    let add = |a: i32, b: i32| -> i32 { return a + b }
    
    printf("3 + 4 = %d\n", add(3, 4))
    
    return 0
}
```

### 4.2 Higher-Order Functions

```flow
# Function that takes a function as parameter
function apply_twice(f: fn(i32) -> i32, x: i32) -> i32 {
    return f(f(x))
}

function double(n: i32) -> i32 {
    return n * 2
}

function main() -> i32 {
    let result = apply_twice(double, 5)
    printf("double(double(5)) = %d\n", result)  # 20
    return 0
}
```

---

## Part 5: Collections

### 5.1 Vector

```flow
import "stdlib/collections.flow"

function main() -> i32 {
    let v = vector_i32_new()
    
    # Vectors would typically have push/pop operations
    # For now, showing the struct
    printf("Vector len: %d\n", vector_i32_len(v))
    printf("Is empty: %d\n", vector_i32_is_empty(v))
    
    return 0
}
```

### 5.2 HashMap

```flow
import "stdlib/collections.flow"

function main() -> i32 {
    let map = hashmap_string_i32_new(16)
    
    printf("HashMap size: %d\n", hashmap_string_i32_len(map))
    printf("Is empty: %d\n", hashmap_string_i32_is_empty(map))
    
    return 0
}
```

### 5.3 Stack and Queue

```flow
import "stdlib/collections.flow"

function main() -> i32 {
    # Stack (LIFO)
    let stack = stack_i32_new(10)
    printf("Stack empty: %d\n", stack_i32_is_empty(stack))
    
    # Queue (FIFO)
    let queue = queue_i32_new(10)
    printf("Queue empty: %d\n", queue_i32_is_empty(queue))
    
    return 0
}
```

---

## Part 6: Concurrency

### 6.1 Threads

```flow
import "stdlib/concurrent.flow"

function main() -> i32 {
    let t = thread_new()
    printf("Thread created\n")
    
    return 0
}
```

### 6.2 Mutex

```flow
import "stdlib/concurrent.flow"

struct Counter {
    value: i32,
    lock: Mutex
}

function counter_new() -> Counter {
    return Counter { value: 0, lock: mutex_new() }
}
```

### 6.3 Channels

```flow
import "stdlib/concurrent.flow"

function main() -> i32 {
    # Create a buffered channel
    let ch = channel_i32_new(10)
    
    printf("Channel capacity: %d\n", ch.capacity)
    printf("Channel empty: %d\n", channel_i32_is_empty(ch))
    
    return 0
}
```

### 6.4 Atomics

```flow
import "stdlib/concurrent.flow"

function main() -> i32 {
    let counter = atomic_i32_new(0)
    
    # Atomic operations for thread-safe access
    printf("Initial: %d\n", counter.value)
    
    return 0
}
```

---

## Part 7: Networking

### 7.1 TCP Server

```flow
import "stdlib/net.flow"

function main() -> i32 {
    let listener = tcp_listener_new(8080)
    printf("TCP listener on port %d\n", listener.port)
    
    return 0
}
```

### 7.2 TCP Client

```flow
import "stdlib/net.flow"

function main() -> i32 {
    let stream = tcp_stream_new()
    printf("TCP stream created\n")
    printf("Connected: %d\n", tcp_stream_is_connected(stream))
    
    return 0
}
```

### 7.3 HTTP Client

```flow
import "stdlib/net.flow"

function main() -> i32 {
    let response = http_get("http://example.com")
    printf("Status: %d\n", response.status_code)
    
    return 0
}
```

---

## Exercises

### Exercise 1: Generic Stack

Implement a generic stack with `push`, `pop`, and `peek` operations.

### Exercise 2: Result Chaining

Write a function that parses a string to int, validates it's positive, and doubles it—using Result at each step.

### Exercise 3: Thread-Safe Counter

Create a counter that can be safely incremented from multiple threads.

---

## Next Steps

Continue to [Advanced Tutorial](advanced.md) to learn:
- Effect system
- Automatic differentiation
- GPU programming
- MLIR/LLVM backend
