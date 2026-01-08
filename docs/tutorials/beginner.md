# Beginner Tutorial - Getting Started with FLOW

Welcome to the FLOW beginner tutorial! This guide will teach you the fundamentals of the FLOW programming language, from basic syntax to your first complete program.

## 🎯 Learning Objectives

By the end of this tutorial, you will be able to:
- Write basic FLOW programs
- Understand FLOW's syntax and structure
- Work with variables, types, and functions
- Use control flow statements
- Create and manipulate data structures
- Handle input and output

## 📝 Your First Program

Let's start with the classic "Hello, World!" program:

```flow
// hello.flow
extern "C" fn printf(s: string, ...);

fn main() {
    printf("Hello, FLOW!\n");
}
```

### Breaking It Down

- `// hello.flow` - A comment (ignored by the compiler)
- `extern "C" fn printf(s: string, ...);` - Declaration of an external C function
- `fn main() { ... }` - The main function where execution begins
- `printf("Hello, FLOW!\n");` - Function call to print text

### Running Your Program

Save the code as `hello.flow` and run:

```bash
flow run hello.flow
```

Output:
```
Hello, FLOW!
```

## 🔤 Variables and Types

FLOW is a statically typed language with type inference. This means the compiler can figure out types automatically, but you can also specify them explicitly.

### Basic Types

```flow
extern "C" fn printf(s: string, ...);

fn main() {
    // Integers
    let age = 25;           // i32 (32-bit integer)
    let big_number: i64 = 1000000;  // i64 (64-bit integer)
    
    // Floating point numbers
    let pi = 3.14159;       // f64 (64-bit float)
    let temperature: f32 = 98.6;     // f32 (32-bit float)
    
    // Boolean
    let is_student = true;
    let graduated = false;
    
    // Strings
    let name = "Alice";
    let greeting: string = "Hello, World!";
    
    // Print them out
    printf("Age: %d\n", age);
    printf("Pi: %f\n", pi);
    printf("Is student: %s\n", is_student ? "true" : "false");
    printf("Name: %s\n", name);
}
```

### Type Inference vs Explicit Types

```flow
// Type inference - compiler figures out the type
let x = 42;        // Compiler knows this is i32
let y = 3.14;      // Compiler knows this is f64

// Explicit types - you tell the compiler the type
let a: i32 = 100;
let b: f64 = 2.71828;
```

## 🧮 Basic Operations

### Arithmetic Operations

```flow
extern "C" fn printf(s: string, ...);

fn main() {
    let a = 10;
    let b = 3;
    
    // Basic arithmetic
    let sum = a + b;        // 13
    let difference = a - b; // 7
    let product = a * b;    // 30
    let quotient = a / b;   // 3 (integer division)
    let remainder = a % b;   // 1
    
    printf("Sum: %d\n", sum);
    printf("Difference: %d\n", difference);
    printf("Product: %d\n", product);
    printf("Quotient: %d\n", quotient);
    printf("Remainder: %d\n", remainder);
}
```

### Comparison Operations

```flow
extern "C" fn printf(s: string, ...);

fn main() {
    let a = 10;
    let b = 5;
    
    // Comparisons return boolean values
    let is_equal = a == b;        // false
    let is_not_equal = a != b;    // true
    let is_greater = a > b;       // true
    let is_less = a < b;          // false
    let is_greater_equal = a >= b; // true
    let is_less_equal = a <= b;   // false
    
    printf("a == b: %s\n", is_equal ? "true" : "false");
    printf("a != b: %s\n", is_not_equal ? "true" : "false");
    printf("a > b: %s\n", is_greater ? "true" : "false");
}
```

### Logical Operations

```flow
extern "C" fn printf(s: string, ...);

fn main() {
    let is_sunny = true;
    let is_warm = false;
    
    // Logical AND
    let good_weather = is_sunny && is_warm;  // false
    
    // Logical OR
    let can_go_out = is_sunny || is_warm;    // true
    
    // Logical NOT
    let is_cloudy = !is_sunny;               // false
    
    printf("Good weather: %s\n", good_weather ? "true" : "false");
    printf("Can go out: %s\n", can_go_out ? "true" : "false");
    printf("Is cloudy: %s\n", is_cloudy ? "true" : "false");
}
```

## 🔄 Control Flow

### If Statements

```flow
extern "C" fn printf(s: string, ...);

fn main() {
    let age = 18;
    
    if age < 13 {
        printf("You are a child\n");
    } else if age < 18 {
        printf("You are a teenager\n");
    } else if age < 65 {
        printf("You are an adult\n");
    } else {
        printf("You are a senior\n");
    }
}
```

### Ternary Operator

For simple conditions, use the ternary operator:

```flow
extern "C" fn printf(s: string, ...);

fn main() {
    let age = 20;
    let message = age >= 18 ? "You can vote" : "You cannot vote";
    
    printf("%s\n", message);
}
```

### Loops

#### For Loops

```flow
extern "C" fn printf(s: string, ...);

fn main() {
    // Count from 0 to 4
    for i in range(0, 5) {
        printf("Count: %d\n", i);
    }
    
    // Count by 2s
    for i in range(0, 10, 2) {
        printf("Even: %d\n", i);
    }
}
```

#### While Loops

```flow
extern "C" fn printf(s: string, ...);

fn main() {
    let mut count = 0;
    
    while count < 5 {
        printf("While count: %d\n", count);
        count = count + 1;
    }
    
    // Do-while style (check at the end)
    let mut i = 0;
    do {
        printf("Do-while: %d\n", i);
        i = i + 1;
    } while i < 3;
}
```

## 📦 Functions

Functions are reusable blocks of code that perform specific tasks.

### Basic Functions

```flow
extern "C" fn printf(s: string, ...);

// Function that takes two integers and returns their sum
fn add(a: i32, b: i32) -> i32 {
    return a + b;
}

// Function that returns a greeting
fn greet(name: string) -> string {
    return "Hello, " + name + "!";
}

// Function with no return value (void function)
fn print_message(message: string) {
    printf("Message: %s\n", message);
}

fn main() {
    let sum = add(10, 20);
    let greeting = greet("Alice");
    
    printf("Sum: %d\n", sum);
    printf("%s\n", greeting);
    print_message("This is a message");
}
```

### Function Overloading

FLOW supports function overloading (multiple functions with the same name but different parameters):

```flow
extern "C" fn printf(s: string, ...);

// Integer version
fn print(value: i32) {
    printf("Integer: %d\n", value);
}

// Float version
fn print(value: f64) {
    printf("Float: %f\n", value);
}

// String version
fn print(value: string) {
    printf("String: %s\n", value);
}

fn main() {
    print(42);           // Calls integer version
    print(3.14);         // Calls float version
    print("Hello");      // Calls string version
}
```

## 🗂️ Arrays

Arrays are fixed-size collections of elements of the same type.

### Creating and Using Arrays

```flow
extern "C" fn printf(s: string, ...);

fn main() {
    // Array with explicit initialization
    let numbers = [1, 2, 3, 4, 5];
    
    // Array with all elements the same
    let zeros = [0; 10];  // 10 zeros
    
    // Array with specified type and size
    let floats: [f64; 5] = [1.1, 2.2, 3.3, 4.4, 5.5];
    
    // Access elements (0-based indexing)
    printf("First element: %d\n", numbers[0]);
    printf("Last element: %d\n", numbers[4]);
    
    // Modify elements
    numbers[0] = 10;
    printf("Modified first element: %d\n", numbers[0]);
    
    // Get array length
    let length = 5;  // In FLOW, array length is known at compile time
    printf("Array length: %d\n", length);
}
```

### Array Operations

```flow
extern "C" fn printf(s: string, ...);

fn main() {
    let numbers = [1, 2, 3, 4, 5];
    
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

## 🏗️ Structs

Structs are custom data types that group related data together.

### Defining and Using Structs

```flow
extern "C" fn printf(s: string, ...);

// Define a struct
struct Person {
    name: string,
    age: i32,
    height: f64
}

fn main() {
    // Create a struct instance
    let person = Person {
        name: "Alice",
        age: 30,
        height: 5.6
    };
    
    // Access struct fields
    printf("Name: %s\n", person.name);
    printf("Age: %d\n", person.age);
    printf("Height: %.1f\n", person.height);
    
    // Modify struct fields
    person.age = 31;
    printf("Updated age: %d\n", person.age);
}
```

### Structs with Functions

```flow
extern "C" fn printf(s: string, ...);

struct Point {
    x: f64,
    y: f64
}

// Function that works with structs
fn distance(p1: Point, p2: Point) -> f64 {
    let dx = p2.x - p1.x;
    let dy = p2.y - p1.y;
    return sqrt(dx * dx + dy * dy);
}

fn main() {
    let p1 = Point { x: 0.0, y: 0.0 };
    let p2 = Point { x: 3.0, y: 4.0 };
    
    let dist = distance(p1, p2);
    printf("Distance: %.2f\n", dist);  // Should be 5.00
}
```

## 🎯 Putting It All Together

Let's create a complete program that uses everything we've learned:

```flow
extern "C" fn printf(s: string, ...);

struct Student {
    name: string,
    age: i32,
    grades: [i32; 3]
}

fn calculate_average(grades: [i32; 3]) -> f64 {
    let mut sum = 0;
    for i in range(0, 3) {
        sum = sum + grades[i];
    }
    return (sum as f64) / 3.0;
}

fn print_student_info(student: Student) {
    printf("Student: %s\n", student.name);
    printf("Age: %d\n", student.age);
    printf("Grades: ");
    
    for i in range(0, 3) {
        printf("%d ", student.grades[i]);
    }
    printf("\n");
    
    let average = calculate_average(student.grades);
    printf("Average: %.2f\n", average);
    
    if average >= 90.0 {
        printf("Grade: A\n");
    } else if average >= 80.0 {
        printf("Grade: B\n");
    } else if average >= 70.0 {
        printf("Grade: C\n");
    } else if average >= 60.0 {
        printf("Grade: D\n");
    } else {
        printf("Grade: F\n");
    }
}

fn main() {
    let student1 = Student {
        name: "Alice",
        age: 20,
        grades: [95, 87, 92]
    };
    
    let student2 = Student {
        name: "Bob",
        age: 19,
        grades: [78, 82, 85]
    };
    
    printf("=== Student 1 ===\n");
    print_student_info(student1);
    
    printf("\n=== Student 2 ===\n");
    print_student_info(student2);
}
```

## 🧪 Practice Exercises

Try these exercises to practice what you've learned:

### Exercise 1: Temperature Converter
Write a function that converts Celsius to Fahrenheit:
- Formula: `F = (C * 9/5) + 32`
- Test with 0°C, 25°C, and 100°C

### Exercise 2: Even/Odd Checker
Write a program that:
- Takes an array of numbers
- Prints whether each number is even or odd
- Counts how many even and odd numbers there are

### Exercise 3: Simple Calculator
Create a calculator that:
- Takes two numbers and an operation (+, -, *, /)
- Performs the operation and prints the result
- Handles division by zero

### Exercise 4: Book Library
Create a simple library system with:
- A `Book` struct (title, author, pages)
- Functions to add books and display library info
- Search for books by author

## 🚀 Next Steps

Congratulations! You've learned the basics of FLOW programming. Here's what to explore next:

1. **[Intermediate Tutorial](intermediate.md)** - Learn about modules, error handling, and more advanced features
2. **[Language Reference](../language/overview.md)** - Detailed documentation of all language features
3. **[Standard Library](../library/overview.md)** - Explore available functions and modules
4. **[Examples Gallery](../examples/README.md)** - See more complex examples

## 💡 Tips for Learning

1. **Practice Every Day** - Write small programs regularly
2. **Experiment** - Try variations of the examples
3. **Read Error Messages** - They often tell you exactly what's wrong
4. **Break Problems Down** - Solve small pieces first
5. **Ask for Help** - Join the FLOW community Discord or forums

---

*Happy coding with FLOW! 🚀*
