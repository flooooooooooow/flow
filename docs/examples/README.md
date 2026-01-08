# FLOW Examples Gallery

Welcome to the FLOW examples gallery! This collection showcases the language's features through practical, real-world examples. Each example demonstrates different aspects of FLOW programming from basic concepts to advanced techniques.

## Table of Contents

- [Basic Examples](#basic-examples)
- [Data Structures](#data-structures)
- [Algorithms](#algorithms)
- [Graphics and Visual Effects](#graphics-and-visual-effects)
- [Performance and SIMD](#performance-and-simd)
- [Effects and Composition](#effects-and-composition)
- [Modules and Packages](#modules-and-packages)
- [GPU Computing](#gpu-computing)
- [Advanced Topics](#advanced-topics)

## Basic Examples

### Hello World
```flow
// The classic Hello World program
extern "C" fn printf(s: string, ...);

fn main() {
    printf("Hello, World!\n");
}
```

### Basic Arithmetic
```flow
extern "C" fn printf(s: string, ...);

fn main() {
    let a: i32 = 10;
    let b: i32 = 20;
    let sum: i32 = a + b;
    
    printf("Sum: %d\n", sum);
}
```

### Simple Loop
```flow
extern "C" fn printf(s: string, ...);

fn main() {
    for i in range(0, 5) {
        printf("Iteration: %d\n", i);
    }
}
```

## Data Structures

### Stack Implementation
```flow
extern "C" fn printf(s: string, ...);

struct Stack {
    data: [i32; 100],
    top: i32
}

fn create_stack() -> Stack {
    return Stack { data: [0; 100], top: -1 };
}

fn push(stack: Stack, value: i32) -> Stack {
    if stack.top < 99 {
        stack.top = stack.top + 1;
        stack.data[stack.top] = value;
    }
    return stack;
}

fn pop(stack: Stack) -> (Stack, i32) {
    if stack.top >= 0 {
        let value = stack.data[stack.top];
        stack.top = stack.top - 1;
        return (stack, value);
    }
    return (stack, 0);
}

fn main() {
    let stack = create_stack();
    stack = push(stack, 10);
    stack = push(stack, 20);
    stack = push(stack, 30);
    
    let (stack, val1) = pop(stack);
    let (stack, val2) = pop(stack);
    
    printf("Popped: %d, %d\n", val1, val2);
}
```

### Person Structure
```flow
extern "C" fn printf(s: string, ...);

struct Address {
    street: string,
    city: string,
    zip: i32
}

struct Person {
    name: string,
    age: i32,
    address: Address
}

fn main() {
    let person = Person {
        name: "John Doe",
        age: 30,
        address: Address {
            street: "123 Main St",
            city: "Anytown",
            zip: 12345
        }
    };
    
    printf("Name: %s\n", person.name);
    printf("City: %s\n", person.address.city);
}
```

## Algorithms

### Fibonacci Sequence
```flow
extern "C" fn printf(s: string, ...);

fn fibonacci(n: i32) -> i32 {
    if n <= 1 {
        return n;
    }
    return fibonacci(n - 1) + fibonacci(n - 2);
}

fn main() {
    for i in range(0, 10) {
        let fib = fibonacci(i);
        printf("fib(%d) = %d\n", i, fib);
    }
}
```

### Bubble Sort
```flow
extern "C" fn printf(s: string, ...);

fn bubble_sort(arr: [i32; 10]) -> [i32; 10] {
    let n = 10;
    for i in range(0, n) {
        for j in range(0, n - i - 1) {
            if arr[j] > arr[j + 1] {
                let temp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = temp;
            }
        }
    }
    return arr;
}

fn main() {
    let numbers = [64, 34, 25, 12, 22, 11, 90, 88, 76, 50];
    numbers = bubble_sort(numbers);
    
    printf("Sorted array:\n");
    for i in range(0, 10) {
        printf("%d ", numbers[i]);
    }
    printf("\n");
}
```

### Prime Numbers
```flow
extern "C" fn printf(s: string, ...);

fn is_prime(n: i32) -> bool {
    if n <= 1 {
        return false;
    }
    if n <= 3 {
        return true;
    }
    if n % 2 == 0 || n % 3 == 0 {
        return false;
    }
    
    let i = 5;
    while i * i <= n {
        if n % i == 0 || n % (i + 2) == 0 {
            return false;
        }
        i = i + 6;
    }
    return true;
}

fn main() {
    printf("Prime numbers up to 100:\n");
    for i in range(2, 101) {
        if is_prime(i) {
            printf("%d ", i);
        }
    }
    printf("\n");
}
```

### Palindrome Checker
```flow
extern "C" fn printf(s: string, ...);

fn is_palindrome(s: string) -> bool {
    let len = 0;
    // Calculate string length (simplified)
    while s[len] != '\0' {
        len = len + 1;
    }
    
    let left = 0;
    let right = len - 1;
    
    while left < right {
        if s[left] != s[right] {
            return false;
        }
        left = left + 1;
        right = right - 1;
    }
    
    return true;
}

fn main() {
    let test1 = "racecar";
    let test2 = "hello";
    
    printf("'%s' is palindrome: %s\n", test1, 
           is_palindrome(test1) ? "true" : "false");
    printf("'%s' is palindrome: %s\n", test2, 
           is_palindrome(test2) ? "true" : "false");
}
```

## Graphics and Visual Effects

### Simple Image Generation
```flow
extern "C" fn printf(s: string, ...);
extern "C" fn fopen(filename: string, mode: string) -> i32;
extern "C" fn fclose(file: i32) -> i32;
extern "C" fn fprintf(file: i32, format: string, ...) -> i32;

fn generate_ppm(width: i32, height: i32) {
    let file = fopen("output.ppm", "w");
    fprintf(file, "P3\n%d %d\n255\n", width, height);
    
    for y in range(0, height) {
        for x in range(0, width) {
            let r = (x * 255) / width;
            let g = (y * 255) / height;
            let b = 128;
            
            fprintf(file, "%d %d %d ", r, g, b);
        }
        fprintf(file, "\n");
    }
    
    fclose(file);
}

fn main() {
    generate_ppm(256, 256);
    printf("Generated image: output.ppm\n");
}
```

### SRIR Demo (Simple Rendering Interface)
```flow
extern "C" fn printf(s: string, ...);

// Simplified SRIR (Simple Rendering Interface) demo
struct Color {
    r: f32,
    g: f32,
    b: f32
}

struct Point {
    x: f32,
    y: f32
}

fn create_color(r: f32, g: f32, b: f32) -> Color {
    return Color { r: r, g: g, b: b };
}

fn create_point(x: f32, y: f32) -> Point {
    return Point { x: x, y: y };
}

fn render_pixel(x: i32, y: i32, color: Color) {
    // Simplified rendering - in real SRIR, this would write to a buffer
    printf("Pixel(%d, %d) = RGB(%f, %f, %f)\n", 
           x, y, color.r, color.g, color.b);
}

fn main() {
    printf("SRIR Demo Phase 0\n");
    
    let red = create_color(1.0, 0.0, 0.0);
    let green = create_color(0.0, 1.0, 0.0);
    let blue = create_color(0.0, 0.0, 1.0);
    
    let center = create_point(128.0, 128.0);
    
    render_pixel(100, 100, red);
    render_pixel(150, 150, green);
    render_pixel(200, 200, blue);
    
    printf("Center point: (%f, %f)\n", center.x, center.y);
}
```

## Performance and SIMD

### SIMD SAXPY (Single-Precision A*X Plus Y)
```flow
extern "C" fn printf(s: string, ...);

// SIMD-optimized SAXPY operation
fn saxpy_simd(n: i32, a: f32, x: [f32; 1024], y: [f32; 1024]) -> [f32; 1024] {
    // This would use SIMD instructions in a real implementation
    for i in range(0, n) {
        y[i] = a * x[i] + y[i];
    }
    return y;
}

fn main() {
    let n = 1024;
    let a: f32 = 2.5;
    let x: [f32; 1024];
    let y: [f32; 1024];
    
    // Initialize arrays
    for i in range(0, n) {
        x[i] = (i as f32) * 0.1;
        y[i] = (i as f32) * 0.05;
    }
    
    y = saxpy_simd(n, a, x, y);
    
    printf("SIMD SAXPY completed\n");
    printf("First result: %f\n", y[0]);
    printf("Last result: %f\n", y[n-1]);
}
```

### Matrix Multiplication
```flow
extern "C" fn printf(s: string, ...);

fn matmul_tile(A: [f32; 64], B: [f32; 64], C: [f32; 64]) -> [f32; 64] {
    let TILE_SIZE = 8;
    
    for i in range(0, 8) {
        for j in range(0, 8) {
            C[i * 8 + j] = 0.0;
            for k in range(0, 8) {
                C[i * 8 + j] = C[i * 8 + j] + A[i * 8 + k] * B[k * 8 + j];
            }
        }
    }
    
    return C;
}

fn main() {
    let A: [f32; 64];
    let B: [f32; 64];
    let C: [f32; 64];
    
    // Initialize matrices
    for i in range(0, 8) {
        for j in range(0, 8) {
            A[i * 8 + j] = (i * 8 + j) as f32;
            B[i * 8 + j] = (j * 8 + i) as f32;
        }
    }
    
    C = matmul_tile(A, B, C);
    
    printf("Matrix multiplication completed\n");
    printf("C[0][0] = %f\n", C[0]);
    printf("C[7][7] = %f\n", C[63]);
}
```

### Dot Product
```flow
extern "C" fn printf(s: string, ...);

fn dot_product(a: [f32; 1024], b: [f32; 1024]) -> f32 {
    let result: f32 = 0.0;
    let n = 1024;
    
    for i in range(0, n) {
        result = result + a[i] * b[i];
    }
    
    return result;
}

fn main() {
    let a: [f32; 1024];
    let b: [f32; 1024];
    let n = 1024;
    
    // Initialize vectors
    for i in range(0, n) {
        a[i] = (i as f32) * 0.1;
        b[i] = (i as f32) * 0.2;
    }
    
    let result = dot_product(a, b);
    
    printf("Dot product: %f\n", result);
}
```

## Effects and Composition

### Simple Effects Demo
```flow
extern "C" fn printf(s: string, ...);

effect Logger {
    fn log(message: string);
}

effect Counter {
    fn increment();
    fn get() -> i32;
}

fn with_logging<T>(body: () -> T) -> T {
    handle body() {
        log(msg) => {
            printf("LOG: %s\n", msg);
            resume();
        }
    }
}

fn with_counter<T>(body: () -> T) -> T {
    let count = 0;
    handle body() {
        increment() => {
            count = count + 1;
            resume();
        }
        get() => {
            resume(count);
        }
    }
}

fn main() {
    let result = with_logging(fn() {
        let counter_result = with_counter(fn() {
            increment();
            increment();
            log("Counter operations completed");
            return get();
        });
        return counter_result;
    });
    
    printf("Final count: %d\n", result);
}
```

### Complete Effects System
```flow
extern "C" fn printf(s: string, ...);

effect State<T> {
    fn get() -> T;
    fn set(value: T);
}

effect IO {
    fn print(s: string);
    fn read() -> string;
}

fn with_state<T, S>(initial: S, body: () -> T) -> T {
    let state = initial;
    handle body() {
        get() => resume(state);
        set(value) => {
            state = value;
            resume();
        }
    }
}

fn with_io<T>(body: () -> T) -> T {
    handle body() {
        print(s) => {
            printf("%s", s);
            resume();
        }
        read() => {
            // Simplified - would read from input
            resume("input");
        }
    }
}

fn main() {
    let result = with_io(fn() {
        let state_result = with_state(0, fn() {
            print("Current state: ");
            let current = get();
            print(current as string);
            print("\n");
            
            set(current + 1);
            
            print("New state: ");
            let new_current = get();
            print(new_current as string);
            print("\n");
            
            return new_current;
        });
        return state_result;
    });
    
    printf("Program completed with final state: %d\n", result);
}
```

### Composition Demo
```flow
extern "C" fn printf(s: string, ...);

struct Engine {
    horsepower: i32,
    torque: i32
}

struct Car {
    make: string,
    model: string,
    engine: Engine
}

struct Team {
    name: string,
    members: [string; 5],
    project: Car
}

fn create_engine(hp: i32, tq: i32) -> Engine {
    return Engine { horsepower: hp, torque: tq };
}

fn create_car(make: string, model: string, engine: Engine) -> Car {
    return Car { make: make, model: model, engine: engine };
}

fn create_team(name: string, members: [string; 5], project: Car) -> Team {
    return Team { name: name, members: members, project: project };
}

fn main() {
    let engine = create_engine(300, 350);
    let car = create_car("Toyota", "Supra", engine);
    let team = create_team("AutoTeam", ["Alice", "Bob", "Charlie", "Diana", "Eve"], car);
    
    printf("Team: %s\n", team.name);
    printf("Project: %s %s\n", team.project.make, team.project.model);
    printf("Engine: %d hp, %d lb-ft torque\n", 
           team.project.engine.horsepower, team.project.engine.torque);
}
```

## Modules and Packages

### Module System Demo
```flow
// File: math.flow
export fn add(a: i32, b: i32) -> i32 {
    return a + b;
}

export fn multiply(a: i32, b: i32) -> i32 {
    return a * b;
}

export fn factorial(n: i32) -> i32 {
    if n <= 1 {
        return 1;
    }
    return n * factorial(n - 1);
}

// File: main.flow
import math;

extern "C" fn printf(s: string, ...);

fn main() {
    let sum = math.add(10, 20);
    let product = math.multiply(5, 6);
    let fact = math.factorial(5);
    
    printf("Sum: %d\n", sum);
    printf("Product: %d\n", product);
    printf("Factorial: %d\n", fact);
}
```

### Package Demo
```flow
// File: package.json
{
    "name": "my_package",
    "version": "1.0.0",
    "modules": ["utils", "math", "graphics"]
}

// File: utils.flow
export fn max(a: i32, b: i32) -> i32 {
    return a > b ? a : b;
}

export fn min(a: i32, b: i32) -> i32 {
    return a < b ? a : b;
}

// File: main.flow
import utils;

extern "C" fn printf(s: string, ...);

fn main() {
    let a = 10;
    let b = 20;
    
    printf("Max of %d and %d: %d\n", a, b, utils.max(a, b));
    printf("Min of %d and %d: %d\n", a, b, utils.min(a, b));
}
```

## GPU Computing

### Simple GPU FFT
```flow
extern "C" fn printf(s: string, ...);

// Simplified GPU FFT demo
fn gpu_fft(input: [f32; 1024]) -> [f32; 1024] {
    let output: [f32; 1024];
    let n = 1024;
    
    // This would run on GPU in real implementation
    for i in range(0, n) {
        let real = input[i];
        let imag = 0.0;
        
        // Simplified FFT calculation
        let angle = -2.0 * 3.14159 * i / n;
        output[i] = real * cos(angle) - imag * sin(angle);
    }
    
    return output;
}

fn main() {
    let input: [f32; 1024];
    let n = 1024;
    
    // Initialize input signal
    for i in range(0, n) {
        input[i] = sin(2.0 * 3.14159 * i / 100.0);
    }
    
    let output = gpu_fft(input);
    
    printf("GPU FFT completed\n");
    printf("First output value: %f\n", output[0]);
    printf("Last output value: %f\n", output[n-1]);
}
```

### GPU Matrix Operations
```flow
extern "C" fn printf(s: string, ...);

fn gpu_matrix_add(A: [f32; 1024], B: [f32; 1024]) -> [f32; 1024] {
    let C: [f32; 1024];
    let n = 1024;
    
    // This would run on GPU in real implementation
    for i in range(0, n) {
        C[i] = A[i] + B[i];
    }
    
    return C;
}

fn main() {
    let A: [f32; 1024];
    let B: [f32; 1024];
    let n = 1024;
    
    // Initialize matrices
    for i in range(0, n) {
        A[i] = (i as f32) * 0.1;
        B[i] = (i as f32) * 0.2;
    }
    
    let C = gpu_matrix_add(A, B);
    
    printf("GPU matrix addition completed\n");
    printf("C[0] = %f\n", C[0]);
    printf("C[1023] = %f\n", C[1023]);
}
```

## Advanced Topics

### Pattern Matching with Structs
```flow
extern "C" fn printf(s: string, ...);

struct Point {
    x: i32,
    y: i32
}

struct Circle {
    center: Point,
    radius: i32
}

struct Rectangle {
    top_left: Point,
    width: i32,
    height: i32
}

fn describe_shape(shape) -> string {
    match shape {
        Point { x, y } => {
            printf("Point at (%d, %d)\n", x, y);
            return "point";
        }
        Circle { center: Point { x, y }, radius } => {
            printf("Circle centered at (%d, %d) with radius %d\n", x, y, radius);
            return "circle";
        }
        Rectangle { top_left: Point { x, y }, width, height } => {
            printf("Rectangle at (%d, %d) size %dx%d\n", x, y, width, height);
            return "rectangle";
        }
    }
}

fn main() {
    let p = Point { x: 10, y: 20 };
    let c = Circle { center: Point { x: 5, y: 5 }, radius: 10 };
    let r = Rectangle { top_left: Point { x: 0, y: 0 }, width: 100, height: 50 };
    
    describe_shape(p);
    describe_shape(c);
    describe_shape(r);
}
```

### Turing Machine Simulation
```flow
extern "C" fn printf(s: string, ...);

struct Tape {
    cells: [i32; 100],
    head: i32
}

struct TuringMachine {
    tape: Tape,
    state: i32
}

fn create_tape() -> Tape {
    let cells: [i32; 100];
    for i in range(0, 100) {
        cells[i] = 0;
    }
    return Tape { cells: cells, head: 50 };
}

fn write_tape(tape: Tape, value: i32) -> Tape {
    tape.cells[tape.head] = value;
    return tape;
}

fn move_right(tape: Tape) -> Tape {
    tape.head = tape.head + 1;
    return tape;
}

fn move_left(tape: Tape) -> Tape {
    tape.head = tape.head - 1;
    return tape;
}

fn main() {
    let tape = create_tape();
    tape = write_tape(tape, 1);
    tape = move_right(tape);
    tape = write_tape(tape, 1);
    tape = move_right(tape);
    tape = write_tape(tape, 1);
    
    printf("Turing Machine simulation\n");
    printf("Head position: %d\n", tape.head);
    printf("Cell at head: %d\n", tape.cells[tape.head]);
}
```

### JIT Compilation Demo
```flow
extern "C" fn printf(s: string, ...);

// This demonstrates FLOW's JIT capabilities
fn compile_and_run(code: string) -> i32 {
    // In a real implementation, this would:
    // 1. Parse the code
    // 2. Generate MLIR
    // 3. Compile to machine code
    // 4. Execute and return result
    
    printf("Compiling: %s\n", code);
    
    // Simplified - just return a constant
    return 42;
}

fn main() {
    let result1 = compile_and_run("fn add(a, b) { return a + b; }");
    let result2 = compile_and_run("fn mul(a, b) { return a * b; }");
    
    printf("JIT compilation results:\n");
    printf("Result 1: %d\n", result1);
    printf("Result 2: %d\n", result2);
}
```

## Running Examples

To run any of these examples:

1. Save the code to a `.flow` file
2. Run using the FLOW compiler:
   ```bash
   flow run example.flow
   ```

3. Or compile and execute:
   ```bash
   flow build example.flow
   ./example
   ```

## Contributing Examples

Have an interesting example you'd like to share? Please contribute!

- Ensure code follows FLOW style guidelines
- Include comments explaining the concept
- Test your example before submitting
- Add it to the appropriate section above

## Next Steps

These examples demonstrate FLOW's capabilities. For more in-depth learning:

1. Read the [Tutorial](tutorial.md)
2. Study the [Language Reference](language.md)
3. Explore the [Standard Library](stdlib.md)
4. Check the [API Documentation](api.md)

Happy coding with FLOW! 🚀
