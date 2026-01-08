# FLOW Tutorial - From Beginner to Advanced

Welcome to the FLOW programming language tutorial! This guide will take you from the basics of FLOW to advanced concepts, with plenty of examples and exercises along the way.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Basic Syntax](#basic-syntax)
3. [Types and Variables](#types-and-variables)
4. [Functions](#functions)
5. [Control Flow](#control-flow)
6. [Arrays and Collections](#arrays-and-collections)
7. [Structs and Data Structures](#structs-and-data-structures)
8. [Pattern Matching](#pattern-matching)
9. [Effects and Capabilities](#effects-and-capabilities)
10. [Modules and Packages](#modules-and-packages)
11. [Graphics and Rendering](#graphics-and-rendering)
12. [Performance Optimization](#performance-optimization)
13. [Advanced Topics](#advanced-topics)
14. [Project Ideas](#project-ideas)

---

## Getting Started

### Installation

First, install FLOW on your system:

```bash
# Clone the repository
git clone https://github.com/flow-lang/flow.git
cd flow

# Install dependencies
pip install -e .

# Verify installation
flow --version
```

### Your First Program

Create a file called `hello.flow`:

```flow
function main() -> i32 {
    printf("Hello, FLOW!\n")
    return 0
}
```

Run it:

```bash
flow run hello.flow
```

Output:
```
Hello, FLOW!
```

### Understanding the Structure

Every FLOW program has a `main` function that returns an `i32` (exit code). The `printf` function prints to standard output, and `\n` represents a newline.

---

## Basic Syntax

### Comments

```flow
# This is a single-line comment

#=
This is a
multi-line comment
=#
```

### Identifiers and Keywords

FLOW identifiers can contain letters, numbers, and underscores, but must start with a letter:

```flow
let my_variable = 42
let anotherVar = "hello"
let _private = 3.14
```

Keywords are reserved words like `function`, `let`, `if`, `for`, etc.

### Whitespace

FLOW is whitespace-insensitive but indentation is recommended for readability:

```flow
function example() -> i32 {
    let x = 1
    let y = 2
    return x + y
}
```

---

## Types and Variables

### Primitive Types

FLOW has several built-in primitive types:

```flow
function demo_types() -> i32 {
    # Integers
    let small: i8 = 127        # 8-bit signed
    let medium: i32 = 1000000 # 32-bit signed
    let large: i64 = 9000000000000000000 # 64-bit signed
    
    # Unsigned integers
    let unsigned: u32 = 4000000000 # 32-bit unsigned
    
    # Floating point
    let single: f32 = 3.14159  # 32-bit float
    let double: f64 = 2.718281828459045 # 64-bit float
    
    # Boolean
    let is_true: bool = true
    let is_false: bool = false
    
    # String
    let greeting: string = "Hello, World!"
    
    return 0
}
```

### Variable Declaration

Use the `let` keyword to declare variables:

```flow
function variables() -> i32 {
    # With explicit type
    let age: i32 = 25
    
    # Type inference (preferred)
    let name = "Alice"
    let height = 5.7
    
    # Mutable variables (reassignment)
    let counter = 0
    counter = counter + 1
    
    return counter
}
```

### Constants

Use `const` for compile-time constants:

```flow
const PI: f32 = 3.14159265359
const MAX_USERS: i32 = 1000

function circle_area(radius: f32) -> f32 {
    return PI * radius * radius
}
```

### Type Conversion

```flow
function conversions() -> i32 {
    let integer: i32 = 42
    let floating: f32 = 3.14
    
    # Implicit conversion (safe)
    let promoted: f64 = integer
    
    # Explicit conversion
    let truncated: i32 = floating as i32
    
    return truncated
}
```

---

## Functions

### Basic Functions

```flow
function add(a: i32, b: i32) -> i32 {
    return a + b
}

function greet(name: string) -> void {
    printf("Hello, %s!\n", name)
}
```

### Function Parameters

```flow
# Pass by value (default)
function increment(x: i32) -> i32 {
    return x + 1
}

# Pass by reference (for large structs)
function transform_in_place(data: array<f32>) -> void {
    for i in 0..len(data) {
        data[i] = data[i] * 2.0
    }
}
```

### Return Values

```flow
# Single return value
function multiply(a: i32, b: i32) -> i32 {
    return a * b
}

# Multiple return values using tuples
function divide_and_remainder(a: i32, b: i32) -> (i32, i32) {
    return (a / b, a % b)
}

# No return value
function print_message(msg: string) -> void {
    printf("%s\n", msg)
}
```

### Function Overloading

```flow
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

### Higher-Order Functions

```flow
function apply_twice(f: fn(i32) -> i32, x: i32) -> i32 {
    return f(f(x))
}

function demo_higher_order() -> i32 {
    let square = fn(x: i32) -> i32 { x * x }
    return apply_twice(square, 3)  # Returns 81 (3^4)
}
```

---

## Control Flow

### If Statements

```flow
function classify_number(n: i32) -> string {
    if n > 0 {
        return "positive"
    } elif n < 0 {
        return "negative"
    } else {
        return "zero"
    }
}
```

### Switch/Match Statements

```flow
function describe_grade(grade: string) -> string {
    match grade {
        "A" => "Excellent",
        "B" => "Good",
        "C" => "Average",
        "D" => "Below Average",
        "F" => "Failing",
        _ => "Invalid grade"
    }
}
```

### Loops

#### While Loop

```flow
function countdown(n: i32) -> i32 {
    while n > 0 {
        printf("%d\n", n)
        n = n - 1
    }
    return 0
}
```

#### For Loop

```flow
function sum_range(start: i32, end: i32) -> i32 {
    let sum: i32 = 0
    for i in start..end {
        sum = sum + i
    }
    return sum
}
```

#### For Each Loop

```flow
function print_array(arr: array<i32>) -> void {
    for value in arr {
        printf("%d ", value)
    }
    printf("\n")
}
```

#### Parallel For Loop

```flow
function parallel_process(data: array<f32>) -> array<f32> {
    let result: array<f32> = array<f32>(len(data))
    
    for i in 0..len(data) parallel {
        result[i] = expensive_computation(data[i])
    }
    
    return result
}
```

### Break and Continue

```flow
function find_first_even(arr: array<i32>) -> i32 {
    for value in arr {
        if value % 2 == 0 {
            return value  # Found it!
        }
        if value > 100 {
            break  # Stop searching
        }
    }
    return -1  # Not found
}
```

---

## Arrays and Collections

### Array Creation

```flow
function array_creation() -> i32 {
    # Array literals
    let numbers = [1, 2, 3, 4, 5]
    let names = ["Alice", "Bob", "Charlie"]
    
    # Dynamic arrays
    let dynamic: array<i32> = array<i32>(10)
    
    # Multi-dimensional arrays
    let matrix: array<array<i32>> = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9]
    ]
    
    return len(numbers)
}
```

### Array Operations

```flow
function array_operations() -> i32 {
    let arr = [10, 20, 30, 40, 50]
    
    # Access elements
    let first = arr[0]      # 10
    let last = arr[4]       # 50
    
    # Modify elements
    arr[2] = 35            # [10, 20, 35, 40, 50]
    
    # Get length
    let length = len(arr)   # 5
    
    # Check if empty
    let is_empty = len(arr) == 0
    
    return length
}
```

### Array Slicing

```flow
function array_slicing() -> i32 {
    let arr = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    
    # Slice from index 2 to 6 (exclusive)
    let slice1 = arr[2:6]   # [3, 4, 5]
    
    # Slice from beginning to index 5
    let slice2 = arr[:5]    # [1, 2, 3, 4, 5]
    
    # Slice from index 3 to end
    let slice3 = arr[3:]    # [4, 5, 6, 7, 8, 9, 10]
    
    # Slice with step
    let slice4 = arr[0:10:2] # [1, 3, 5, 7, 9]
    
    return len(slice1)
}
```

### Common Array Patterns

```flow
function array_patterns() -> i32 {
    let numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    
    # Sum all elements
    let sum: i32 = 0
    for num in numbers {
        sum = sum + num
    }
    
    # Find maximum
    let max = numbers[0]
    for num in numbers {
        if num > max {
            max = num
        }
    }
    
    # Filter even numbers
    let evens: array<i32> = []
    for num in numbers {
        if num % 2 == 0 {
            evens.append(num)
        }
    }
    
    return sum
}
```

---

## Structs and Data Structures

### Basic Structs

```flow
struct Point {
    x: f32,
    y: f32
}

struct Person {
    name: string,
    age: i32,
    location: Point
}
```

### Creating Structs

```flow
function create_structs() -> i32 {
    # Struct literal
    let p1 = Point { x: 1.0, y: 2.0 }
    
    # With type inference
    let p2 = Point { x: 3.0, y: 4.0 }
    
    # Nested struct
    let person = Person {
        name: "Alice",
        age: 30,
        location: Point { x: 10.0, y: 20.0 }
    }
    
    return 0
}
```

### Accessing Fields

```flow
function access_fields() -> f32 {
    let point = Point { x: 3.0, y: 4.0 }
    
    # Access fields
    let x_coord = point.x
    let y_coord = point.y
    
    # Modify fields
    point.x = 5.0
    
    # Nested access
    let person = Person {
        name: "Bob",
        age: 25,
        location: Point { x: 1.0, y: 2.0 }
    }
    
    return person.location.y
}
```

### Struct Methods

```flow
struct Vector2D {
    x: f32,
    y: f32
}

# Associated function (like static method)
function Vector2D.zero() -> Vector2D {
    return Vector2D { x: 0.0, y: 0.0 }
}

# Method on Vector2D
function length(v: Vector2D) -> f32 {
    return sqrt(v.x * v.x + v.y * v.y)
}

function normalize(v: Vector2D) -> Vector2D {
    let len = length(v)
    return Vector2D { x: v.x / len, y: v.y / len }
}
```

### Struct Memory Layout

```flow
struct Example {
    a: i8,   # Offset 0, size 1
    b: i32,  # Offset 4, size 4 (aligned to 4 bytes)
    c: f32,  # Offset 8, size 4
    d: i8    # Offset 12, size 1
}

function memory_layout() -> i32 {
    # Total size is 16 bytes (due to alignment)
    let size = sizeof(Example)
    
    # Field offsets
    let a_offset = offsetof(Example, a)  # 0
    let b_offset = offsetof(Example, b)  # 4
    let c_offset = offsetof(Example, c)  # 8
    let d_offset = offsetof(Example, d)  # 12
    
    return size
}
```

---

## Pattern Matching

### Basic Pattern Matching

```flow
function describe_number(n: i32) -> string {
    match n {
        0 => "zero",
        1 => "one",
        2 => "two",
        3 => "three",
        _ => "many"
    }
}
```

### Pattern Matching with Guards

```flow
function classify_age(age: i32) -> string {
    match age {
        n if n < 0 => "invalid age",
        n if n < 13 => "child",
        n if n < 20 => "teenager",
        n if n < 65 => "adult",
        _ => "senior citizen"
    }
}
```

### Struct Pattern Matching

```flow
struct Point {
    x: i32,
    y: i32
}

function match_point(p: Point) -> string {
    match p {
        Point { x: 0, y: 0 } => "origin",
        Point { x: x, y: 0 } => "on x-axis at {x}",
        Point { x: 0, y: y } => "on y-axis at {y}",
        Point { x: x, y: y } => "at coordinates ({x}, {y})"
    }
}
```

### Nested Pattern Matching

```flow
struct Circle {
    center: Point,
    radius: i32
}

function describe_circle(c: Circle) -> string {
    match c {
        Circle { center: Point { x: 0, y: 0 }, radius: r } => "circle at origin with radius {r}",
        Circle { center: Point { x: x, y: y }, radius: r } => "circle at ({x}, {y}) with radius {r}"
    }
}
```

### Array Pattern Matching

```flow
function analyze_list(arr: array<i32>) -> string {
    match arr {
        [] => "empty list",
        [x] => "single element: {x}",
        [x, y] => "two elements: {x}, {y}",
        [x, y, z, ...] => "at least three elements: {x}, {y}, {z}...",
        _ => "many elements"
    }
}
```

---

## Effects and Capabilities

### Understanding Effects

Effects in FLOW provide a way to manage side effects in a type-safe manner.

```flow
effect FileSystem {
    read(path: string) -> string,
    write(path: string, content: string) -> void,
    delete(path: string) -> void
}

effect Network {
    get(url: string) -> string,
    post(url: string, data: string) -> string
}
```

### Implementing Capabilities

```flow
capability LocalFileSystem implements FileSystem {
    function read(path: string) -> string {
        # Implementation for local file system
        return read_local_file(path)
    }
    
    function write(path: string, content: string) -> void {
        write_local_file(path, content)
    }
    
    function delete(path: string) -> void {
        delete_local_file(path)
    }
}

capability HTTPClient implements Network {
    function get(url: string) -> string {
        # HTTP GET implementation
        return http_get(url)
    }
    
    function post(url: string, data: string) -> string {
        # HTTP POST implementation
        return http_post(url, data)
    }
}
```

### Using Effects

```flow
function process_file(path: string) -> i32 {
    handle FileSystem with LocalFileSystem {
        let content = FileSystem.read(path)
        let processed = transform_content(content)
        FileSystem.write(path + ".processed", processed)
        return 0
    }
}

function fetch_data(url: string) -> string {
    handle Network with HTTPClient {
        return Network.get(url)
    }
}
```

### Effect Polymorphism

```flow
function generic_computation<T: FileSystem>(path: string) -> i32 {
    handle FileSystem with T {
        let data = FileSystem.read(path)
        let result = analyze_data(data)
        FileSystem.write(path + ".analysis", result)
        return 0
    }
}

# Usage with different implementations
let result1 = generic_computation<LocalFileSystem>("data.txt")
let result2 = generic_computation<CloudFileSystem>("cloud://data.txt")
```

---

## Modules and Packages

### Creating Modules

Create a file `math/vector.flow`:

```flow
export struct Vector2D {
    x: f32,
    y: f32
}

export function add(a: Vector2D, b: Vector2D) -> Vector2D {
    return Vector2D { x: a.x + b.x, y: a.y + b.y }
}

export function length(v: Vector2D) -> f32 {
    return sqrt(v.x * v.x + v.y * v.y)
}
```

### Importing Modules

In `main.flow`:

```flow
import "math/vector.flow"

function main() -> i32 {
    let v1 = Vector2D { x: 1.0, y: 2.0 }
    let v2 = Vector2D { x: 3.0, y: 4.0 }
    
    let sum = add(v1, v2)
    let len = length(sum)
    
    printf("Result: (%.2f, %.2f), length: %.2f\n", sum.x, sum.y, len)
    return 0
}
```

### Selective Imports

```flow
# Import specific symbols
import { Vector2D, add } from "math/vector.flow"

# Import with alias
import { Vector2D as Vec2 } from "math/vector.flow"

# Import all symbols (use sparingly)
import * as Math from "math/vector.flow"
```

### Package Management

Create a `package.json`:

```json
{
    "name": "my-project",
    "version": "1.0.0",
    "dependencies": {
        "flow-math": "^1.2.0",
        "flow-graphics": "^2.1.0"
    }
}
```

Install dependencies:

```bash
flow install
```

---

## Graphics and Rendering

### Basic 2D Graphics

```flow
struct Color {
    r: f32,
    g: f32,
    b: f32,
    a: f32
}

struct Rectangle {
    x: f32,
    y: f32,
    width: f32,
    height: f32
}

function draw_rect(rect: Rectangle, color: Color) -> void {
    handle GPU with OpenGLGPU {
        GPU.set_color(color)
        GPU.draw_rectangle(rect)
    }
}
```

### Scene Graph

```flow
struct SceneNode {
    id: string,
    transform: Transform,
    children: array<SceneNode>,
    renderer: Renderer
}

struct Transform {
    position: Vector2D,
    rotation: f32,
    scale: Vector2D
}

function render_scene(scene: SceneNode) -> void {
    handle GPU with OpenGLGPU {
        GPU.clear(Color { r: 0.2, g: 0.2, b: 0.2, a: 1.0 })
        render_node(scene)
        GPU.present()
    }
}

function render_node(node: SceneNode) -> void {
    # Apply transform
    GPU.push_matrix()
    GPU.translate(node.transform.position)
    GPU.rotate(node.transform.rotation)
    GPU.scale(node.transform.scale)
    
    # Render this node
    node.renderer.render(node)
    
    # Render children
    for child in node.children {
        render_node(child)
    }
    
    GPU.pop_matrix()
}
```

### Animation

```flow
struct Animation {
    duration: f32,
    keyframes: array<Keyframe>,
    easing: EasingFunction
}

function animate_value(animation: Animation, time: f32) -> f32 {
    let t = time / animation.duration
    let eased = animation.easing(t)
    return interpolate_keyframes(animation.keyframes, eased)
}

function ease_in_out(t: f32) -> f32 {
    return t * t * (3.0 - 2.0 * t)
}
```

---

## Performance Optimization

### SIMD Vectorization

```flow
function vectorized_add(a: array<f32>, b: array<f32>) -> array<f32> {
    let result: array<f32> = array<f32>(len(a))
    
    # This loop will be auto-vectorized by LLVM
    for i in 0..len(a) {
        result[i] = a[i] + b[i]
    }
    
    return result
}
```

### Memory Layout Optimization

```flow
# Structure of Arrays (better for SIMD)
struct ParticlesSoA {
    positions_x: array<f32>,
    positions_y: array<f32>,
    velocities_x: array<f32>,
    velocities_y: array<f32>
}

# Array of Structures (better for random access)
struct Particle {
    position: Vector2D,
    velocity: Vector2D
}
```

### Parallel Processing

```flow
function parallel_process(data: array<f32>) -> array<f32> {
    let result: array<f32> = array<f32>(len(data))
    
    for i in 0..len(data) parallel {
        result[i] = expensive_computation(data[i])
    }
    
    return result
}
```

### Cache-Friendly Algorithms

```flow
function matrix_multiply(a: array<array<f32>>, b: array<array<f32>>) -> array<array<f32>> {
    let n = len(a)
    let result: array<array<f32>> = array<array<f32>>(n)
    
    for i in 0..n {
        result[i] = array<f32>(n)
        for j in 0..n {
            let sum: f32 = 0.0
            for k in 0..n {
                sum = sum + a[i][k] * b[k][j]
            }
            result[i][j] = sum
        }
    }
    
    return result
}
```

---

## Advanced Topics

### Metaprogramming

```flow
macro generate_struct(name: string, fields: array<string>) -> string {
    let struct_def = "struct " + name + " {\n"
    
    for field in fields {
        struct_def = struct_def + "    " + field + ": i32,\n"
    }
    
    struct_def = struct_def + "}"
    return struct_def
}

# Use at compile time
#generate_struct("Point", ["x", "y"])
```

### Foreign Function Interface

```flow
foreign {
    function malloc(size: i32) -> ptr
    function free(ptr: ptr) -> void
    function printf(format: string, ...) -> i32
}

function demo_ffi() -> i32 {
    let ptr = malloc(1024)
    # Use ptr...
    free(ptr)
    
    printf("Hello from FFI!\n")
    return 0
}
```

### Generic Programming

```flow
function swap<T>(a: T, b: T) -> (T, T) {
    return (b, a)
}

function max<T: Ord>(a: T, b: T) -> T {
    if a > b {
        return a
    } else {
        return b
    }
}
```

### Memory Management

```flow
struct MemoryPool {
    start: ptr,
    current: ptr,
    end: ptr
}

function pool_create(size: i32) -> MemoryPool {
    let start = malloc(size)
    return MemoryPool {
        start: start,
        current: start,
        end: start + size
    }
}

function pool_alloc(pool: MemoryPool, size: i32) -> ptr {
    if pool.current + size > pool.end {
        panic("Out of memory")
    }
    
    let ptr = pool.current
    pool.current = pool.current + size
    return ptr
}
```

---

## Project Ideas

### Beginner Projects

1. **Calculator**: A simple command-line calculator
2. **Guess the Number**: Classic number guessing game
3. **Todo List**: Command-line todo application
4. **File Processor**: Process and transform text files
5. **Simple Game**: Text-based adventure game

### Intermediate Projects

1. **Image Processor**: Apply filters to images
2. **JSON Parser**: Parse and manipulate JSON data
3. **Web Server**: Simple HTTP server
4. **Data Visualizer**: Plot data points in a GUI
5. **Chat Client**: Real-time chat application

### Advanced Projects

1. **Game Engine**: 2D game engine with physics
2. **Compiler**: Compile a simple language to FLOW
3. **Operating System**: Simple OS kernel
4. **Database**: Key-value store with indexing
5. **Machine Learning**: Neural network implementation

### Example: Simple Calculator

```flow
import "std/io.flow"

function evaluate_expression(expr: string) -> f32 {
    # Simple expression evaluation
    # In a real implementation, you'd parse the expression
    return 42.0
}

function main() -> i32 {
    printf("Simple Calculator\n")
    printf("Enter expressions (or 'quit' to exit):\n")
    
    while true {
        printf("> ")
        let input = read_line()
        
        if input == "quit" {
            break
        }
        
        let result = evaluate_expression(input)
        printf("= %.2f\n", result)
    }
    
    return 0
}
```

### Example: Todo List

```flow
struct TodoItem {
    id: i32,
    text: string,
    completed: bool
}

struct TodoList {
    items: array<TodoItem>,
    next_id: i32
}

function todo_list_create() -> TodoList {
    return TodoList {
        items: [],
        next_id: 1
    }
}

function todo_list_add(list: TodoList, text: string) -> TodoList {
    let item = TodoItem {
        id: list.next_id,
        text: text,
        completed: false
    }
    
    list.items.append(item)
    list.next_id = list.next_id + 1
    
    return list
}

function todo_list_complete(list: TodoList, id: i32) -> TodoList {
    for item in list.items {
        if item.id == id {
            item.completed = true
            break
        }
    }
    
    return list
}

function todo_list_print(list: TodoList) -> void {
    printf("Todo List:\n")
    
    for item in list.items {
        let status = if item.completed { "✓" } else { " " }
        printf("[%s] %d: %s\n", status, item.id, item.text)
    }
}

function main() -> i32 {
    let todos = todo_list_create()
    
    todos = todo_list_add(todos, "Learn FLOW")
    todos = todo_list_add(todos, "Build a project")
    todos = todo_list_add(todos, "Master advanced topics")
    
    todos = todo_list_complete(todos, 1)
    
    todo_list_print(todos)
    
    return 0
}
```

---

## Next Steps

Congratulations! You've completed the FLOW tutorial. Here are some suggestions for continuing your journey:

1. **Read the Language Reference**: Dive deep into the language specification
2. **Explore the Standard Library**: Discover built-in functions and modules
3. **Join the Community**: Connect with other FLOW developers
4. **Contribute to Open Source**: Help improve FLOW itself
5. **Build Something**: Apply your knowledge to real projects

### Resources

- [Official Documentation](https://flow-lang.org/docs)
- [Community Forum](https://forum.flow-lang.org)
- [GitHub Repository](https://github.com/flow-lang/flow)
- [Examples Gallery](https://flow-lang.org/examples)

Happy coding with FLOW! 🚀
