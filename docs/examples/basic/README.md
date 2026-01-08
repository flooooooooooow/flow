# Basic FLOW Examples

Welcome to the basic FLOW examples! These examples demonstrate fundamental concepts and are perfect for beginners learning the language.

## 📋 Table of Contents

- [Hello World](#hello-world)
- [Variables and Types](#variables-and-types)
- [Basic Arithmetic](#basic-arithmetic)
- [Functions](#functions)
- [Control Flow](#control-flow)
- [Loops](#loops)
- [Arrays](#arrays)
- [Structs](#structs)
- [Input and Output](#input-and-output)

## Hello World

The classic first program in any language.

```flow
// hello_world.flow
extern "C" fn printf(s: string, ...);

fn main() {
    printf("Hello, World!\n");
}
```

**Run it:**
```bash
flow run hello_world.flow
```

**Output:**
```
Hello, World!
```

## Variables and Types

Demonstrates FLOW's type system and variable declarations.

```flow
// variables.flow
extern "C" fn printf(s: string, ...);

fn main() {
    // Type inference
    let integer = 42;           // i32
    let floating = 3.14159;      // f64
    let boolean = true;          // bool
    let text = "FLOW";           // string
    
    // Explicit types
    let age: i32 = 25;
    let pi: f64 = 3.14159265359;
    let is_student: bool = true;
    let name: string = "Alice";
    
    // Print them
    printf("Integer: %d\n", integer);
    printf("Float: %f\n", floating);
    printf("Boolean: %s\n", boolean ? "true" : "false");
    printf("String: %s\n", text);
    printf("Age: %d\n", age);
    printf("Pi: %.10f\n", pi);
    printf("Is student: %s\n", is_student ? "true" : "false");
    printf("Name: %s\n", name);
}
```

## Basic Arithmetic

Shows mathematical operations in FLOW.

```flow
// arithmetic.flow
extern "C" fn printf(s: string, ...);

fn main() {
    let a = 10;
    let b = 3;
    
    // Basic operations
    let sum = a + b;
    let difference = a - b;
    let product = a * b;
    let quotient = a / b;
    let remainder = a % b;
    
    printf("Arithmetic with %d and %d:\n", a, b);
    printf("Sum: %d\n", sum);
    printf("Difference: %d\n", difference);
    printf("Product: %d\n", product);
    printf("Quotient: %d\n", quotient);
    printf("Remainder: %d\n", remainder);
    
    // Floating point arithmetic
    let x = 3.5;
    let y = 2.0;
    let fp_sum = x + y;
    let fp_product = x * y;
    
    printf("\nFloating point arithmetic:\n");
    printf("%.2f + %.2f = %.2f\n", x, y, fp_sum);
    printf("%.2f * %.2f = %.2f\n", x, y, fp_product);
}
```

## Functions

Demonstrates function definition and usage.

```flow
// functions.flow
extern "C" fn printf(s: string, ...);

// Simple function
fn add(a: i32, b: i32) -> i32 {
    return a + b;
}

// Function with multiple return paths
fn absolute_value(n: i32) -> i32 {
    if n < 0 {
        return -n;
    }
    return n;
}

// Function that returns a string
fn greet(name: string) -> string {
    return "Hello, " + name + "!";
}

// Function with no return value
fn print_separator() {
    printf("-------------------\n");
}

fn main() {
    // Test the functions
    let sum = add(15, 27);
    printf("15 + 27 = %d\n", sum);
    
    print_separator();
    
    let abs1 = absolute_value(-10);
    let abs2 = absolute_value(42);
    printf("|-10| = %d\n", abs1);
    printf("|42| = %d\n", abs2);
    
    print_separator();
    
    let greeting = greet("World");
    printf("%s\n", greeting);
}
```

## Control Flow

Shows conditional statements and logic.

```flow
// control_flow.flow
extern "C" fn printf(s: string, ...);

fn check_number(n: i32) {
    printf("Checking number %d:\n", n);
    
    if n > 0 {
        printf("  Positive\n");
    } else if n < 0 {
        printf("  Negative\n");
    } else {
        printf("  Zero\n");
    }
    
    // Check if it's even or odd
    if n % 2 == 0 {
        printf("  Even\n");
    } else {
        printf("  Odd\n");
    }
    
    // Check range
    if n >= 1 && n <= 10 {
        printf("  In range 1-10\n");
    } else if n >= 11 && n <= 100 {
        printf("  In range 11-100\n");
    } else {
        printf("  Outside range 1-100\n");
    }
}

fn main() {
    let numbers = [0, 5, -3, 12, 150];
    
    for i in range(0, 5) {
        check_number(numbers[i]);
        printf("\n");
    }
}
```

## Loops

Demonstrates different types of loops.

```flow
// loops.flow
extern "C" fn printf(s: string, ...);

fn main() {
    printf("=== For Loop ===\n");
    // Basic for loop
    for i in range(0, 5) {
        printf("Iteration %d\n", i);
    }
    
    printf("\n=== For Loop with Step ===\n");
    // For loop with step
    for i in range(0, 10, 2) {
        printf("Even number: %d\n", i);
    }
    
    printf("\n=== While Loop ===\n");
    // While loop
    let mut count = 0;
    while count < 3 {
        printf("Count: %d\n", count);
        count = count + 1;
    }
    
    printf("\n=== Nested Loops ===\n");
    // Nested loops
    for i in range(0, 3) {
        for j in range(0, 3) {
            printf("i=%d, j=%d\n", i, j);
        }
    }
    
    printf("\n=== Loop Control ===\n");
    // Loop with break and continue (simplified)
    for i in range(0, 10) {
        if i == 7 {
            printf("Breaking at %d\n", i);
            break;
        }
        if i % 2 == 0 {
            continue;  // Skip even numbers
        }
        printf("Odd number: %d\n", i);
    }
}
```

## Arrays

Shows array operations and manipulation.

```flow
// arrays.flow
extern "C" fn printf(s: string, ...);

fn main() {
    printf("=== Array Creation ===\n");
    // Different ways to create arrays
    let numbers = [1, 2, 3, 4, 5];
    let zeros = [0; 5];
    let floats: [f64; 3] = [1.1, 2.2, 3.3];
    
    printf("Numbers: ");
    for i in range(0, 5) {
        printf("%d ", numbers[i]);
    }
    printf("\n");
    
    printf("Zeros: ");
    for i in range(0, 5) {
        printf("%d ", zeros[i]);
    }
    printf("\n");
    
    printf("Floats: ");
    for i in range(0, 3) {
        printf("%.1f ", floats[i]);
    }
    printf("\n\n");
    
    printf("=== Array Operations ===\n");
    // Access and modify elements
    printf("First element: %d\n", numbers[0]);
    printf("Last element: %d\n", numbers[4]);
    
    numbers[0] = 10;
    printf("Modified first element: %d\n", numbers[0]);
    
    // Sum all elements
    let mut sum = 0;
    for i in range(0, 5) {
        sum = sum + numbers[i];
    }
    printf("Sum: %d\n", sum);
    
    // Find maximum
    let mut max = numbers[0];
    for i in range(1, 5) {
        if numbers[i] > max {
            max = numbers[i];
        }
    }
    printf("Maximum: %d\n", max);
    
    // Reverse array
    let mut reversed: [i32; 5];
    for i in range(0, 5) {
        reversed[i] = numbers[4 - i];
    }
    
    printf("Reversed: ");
    for i in range(0, 5) {
        printf("%d ", reversed[i]);
    }
    printf("\n");
}
```

## Structs

Demonstrates custom data structures.

```flow
// structs.flow
extern "C" fn printf(s: string, ...);

// Define a struct
struct Point {
    x: f64,
    y: f64
}

struct Person {
    name: string,
    age: i32,
    height: f64
}

// Function that works with structs
fn distance(p1: Point, p2: Point) -> f64 {
    let dx = p2.x - p1.x;
    let dy = p2.y - p1.y;
    return sqrt(dx * dx + dy * dy);
}

fn print_person(person: Person) {
    printf("Name: %s\n", person.name);
    printf("Age: %d\n", person.age);
    printf("Height: %.1f\n", person.height);
}

fn main() {
    printf("=== Point Struct ===\n");
    // Create points
    let p1 = Point { x: 0.0, y: 0.0 };
    let p2 = Point { x: 3.0, y: 4.0 };
    
    printf("Point 1: (%.1f, %.1f)\n", p1.x, p1.y);
    printf("Point 2: (%.1f, %.1f)\n", p2.x, p2.y);
    
    let dist = distance(p1, p2);
    printf("Distance: %.2f\n", dist);
    
    printf("\n=== Person Struct ===\n");
    // Create a person
    let person = Person {
        name: "Alice Johnson",
        age: 30,
        height: 5.6
    };
    
    print_person(person);
    
    // Modify struct fields
    person.age = 31;
    printf("\nAfter birthday:\n");
    print_person(person);
}
```

## Input and Output

Basic file I/O operations.

```flow
// io.flow
extern "C" fn printf(s: string, ...);
extern "C" fn fopen(filename: string, mode: string) -> i32;
extern "C" fn fclose(file: i32) -> i32;
extern "C" fn fprintf(file: i32, format: string, ...) -> i32;

fn write_numbers_to_file(filename: string) -> bool {
    let file = fopen(filename, "w");
    if file == 0 {
        printf("Failed to open file for writing\n");
        return false;
    }
    
    // Write numbers 1 to 10
    for i in range(1, 11) {
        fprintf(file, "%d\n", i);
    }
    
    fclose(file);
    printf("Successfully wrote numbers to %s\n", filename);
    return true;
}

fn main() {
    printf("=== File I/O Example ===\n");
    
    // Write to file
    let success = write_numbers_to_file("numbers.txt");
    
    if success {
        printf("File operation completed successfully\n");
    } else {
        printf("File operation failed\n");
    }
    
    printf("\n=== Console Output ===\n");
    printf("This demonstrates basic console output\n");
    printf("You can format numbers: %d, strings: %s, floats: %.2f\n", 
           42, "FLOW", 3.14159);
}
```

## 🚀 Running the Examples

Each example can be run individually:

```bash
# Run the hello world example
flow run hello_world.flow

# Run the arithmetic example
flow run arithmetic.flow

# Run the structs example
flow run structs.flow
```

Or compile them first:

```bash
# Compile
flow build hello_world.flow

# Run the executable
./hello_world
```

## 📚 What's Next?

After mastering these basic examples, you can explore:

1. **[Data Structures](../data-structures/)** - More complex data structures
2. **[Algorithms](../algorithms/)** - Common algorithms and patterns
3. **[Intermediate Tutorial](../../tutorials/intermediate.md)** - Learn advanced features
4. **[Language Reference](../../language/overview.md)** - Complete language documentation

## 💡 Tips for Learning

1. **Run Each Example** - Type them out and run them yourself
2. **Modify Them** - Change values and see what happens
3. **Combine Concepts** - Try mixing different examples together
4. **Experiment** - Create your own variations
5. **Ask Questions** - Join the community if you get stuck

---

*Ready to move on to more complex examples? Let's continue your FLOW journey! 🚀*
