# Intermediate Tutorial - Expanding Your FLOW Skills

Welcome to the intermediate FLOW tutorial! Building on the basics, this guide will introduce you to more powerful features like modules, error handling, pattern matching, and advanced data structures.

## 🎯 Learning Objectives

By the end of this tutorial, you will be able to:
- Organize code with modules and packages
- Handle errors gracefully
- Use pattern matching for complex logic
- Work with advanced data structures
- Write more efficient and maintainable code
- Use generic programming concepts

## 📦 Modules and Packages

Modules help you organize large programs and create reusable code libraries.

### Creating a Module

Create a file called `math_utils.flow`:

```flow
// math_utils.flow
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

// Private function (not exported)
fn internal_helper(x: i32) -> i32 {
    return x * 2;
}

export fn double(x: i32) -> i32 {
    return internal_helper(x);
}
```

### Using a Module

```flow
// main.flow
import math_utils;

extern "C" fn printf(s: string, ...);

fn main() {
    let sum = math_utils.add(10, 20);
    let product = math_utils.multiply(5, 6);
    let fact = math_utils.factorial(5);
    let doubled = math_utils.double(10);
    
    printf("Sum: %d\n", sum);
    printf("Product: %d\n", product);
    printf("Factorial: %d\n", fact);
    printf("Doubled: %d\n", doubled);
}
```

### Module Aliases

```flow
import math_utils as math;

fn main() {
    let result = math.add(5, 3);  // Use alias
}
```

### Selective Imports

```flow
import math_utils { add, multiply };

fn main() {
    let sum = add(10, 20);        // No prefix needed
    let product = multiply(5, 6);
    // let fact = factorial(5);   // Error: factorial not imported
}
```

## 🎭 Pattern Matching

Pattern matching is a powerful feature for handling complex conditional logic.

### Basic Pattern Matching

```flow
extern "C" fn printf(s: string, ...);

fn describe_number(n: i32) -> string {
    match n {
        0 => "zero",
        1 => "one",
        2 => "two",
        _ => "many"  // Wildcard pattern
    }
}

fn main() {
    for i in range(0, 5) {
        let description = describe_number(i);
        printf("%d is %s\n", i, description);
    }
}
```

### Pattern Matching with Conditions

```flow
extern "C" fn printf(s: string, ...);

fn classify_age(age: i32) -> string {
    match age {
        n if n < 0 => "invalid",
        n if n < 13 => "child",
        n if n < 18 => "teenager",
        n if n < 65 => "adult",
        n if n < 120 => "senior",
        _ => "impossible"
    }
}

fn main() {
    let ages = [-1, 5, 15, 25, 70, 150];
    for i in range(0, 6) {
        let age = ages[i];
        let classification = classify_age(age);
        printf("Age %d: %s\n", age, classification);
    }
}
```

### Struct Pattern Matching

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

## 🚨 Error Handling

FLOW provides several ways to handle errors gracefully.

### Result Type

```flow
// Result type definition (built-in in FLOW)
enum Result<T, E> {
    Ok(T),
    Err(E)
}

extern "C" fn printf(s: string, ...);

fn divide(a: f64, b: f64) -> Result<f64, string> {
    if b == 0.0 {
        return Result::Err("Division by zero");
    }
    return Result::Ok(a / b);
}

fn main() {
    let result1 = divide(10.0, 2.0);
    let result2 = divide(10.0, 0.0);
    
    match result1 {
        Result::Ok(value) => printf("10 / 2 = %.2f\n", value),
        Result::Err(error) => printf("Error: %s\n", error)
    }
    
    match result2 {
        Result::Ok(value) => printf("10 / 0 = %.2f\n", value),
        Result::Err(error) => printf("Error: %s\n", error)
    }
}
```

### Option Type

```flow
// Option type for nullable values
enum Option<T> {
    Some(T),
    None
}

extern "C" fn printf(s: string, ...);

fn find_element(arr: [i32; 5], target: i32) -> Option<i32> {
    for i in range(0, 5) {
        if arr[i] == target {
            return Option::Some(i);
        }
    }
    return Option::None;
}

fn main() {
    let numbers = [1, 3, 5, 7, 9];
    
    let result1 = find_element(numbers, 5);
    let result2 = find_element(numbers, 2);
    
    match result1 {
        Option::Some(index) => printf("Found 5 at index %d\n", index),
        Option::None => printf("5 not found\n")
    }
    
    match result2 {
        Option::Some(index) => printf("Found 2 at index %d\n", index),
        Option::None => printf("2 not found\n")
    }
}
```

### Panic and Recover

```flow
extern "C" fn printf(s: string, ...);

fn risky_operation(should_fail: bool) -> i32 {
    if should_fail {
        panic("Something went wrong!");
    }
    return 42;
}

fn safe_operation() -> i32 {
    // In a real implementation, you might use try-catch here
    return risky_operation(false);
}

fn main() {
    let result = safe_operation();
    printf("Result: %d\n", result);
    
    // This would panic:
    // let bad_result = risky_operation(true);
}
```

## 🧬 Advanced Data Structures

### Linked Lists

```flow
extern "C" fn printf(s: string, ...);

struct Node {
    value: i32,
    next: Option<Box<Node>>
}

struct LinkedList {
    head: Option<Box<Node>>
}

fn create_linked_list() -> LinkedList {
    return LinkedList { head: Option::None };
}

fn append(list: LinkedList, value: i32) -> LinkedList {
    let new_node = Node {
        value: value,
        next: Option::None
    };
    
    match list.head {
        Option::None => {
            return LinkedList { 
                head: Option::Some(Box::new(new_node)) 
            };
        }
        Option::Some(head) => {
            // In a real implementation, you'd traverse to the end
            // For simplicity, we'll just prepend
            let new_head = Node {
                value: value,
                next: Option::Some(head)
            };
            return LinkedList { 
                head: Option::Some(Box::new(new_head)) 
            };
        }
    }
}

fn print_list(list: LinkedList) {
    printf("List: ");
    match list.head {
        Option::None => printf("empty"),
        Option::Some(head) => {
            printf("%d", head.value);
            // In a real implementation, you'd traverse the whole list
        }
    }
    printf("\n");
}

fn main() {
    let list = create_linked_list();
    let list = append(list, 10);
    let list = append(list, 20);
    let list = append(list, 30);
    
    print_list(list);
}
```

### Binary Trees

```flow
extern "C" fn printf(s: string, ...);

struct TreeNode {
    value: i32,
    left: Option<Box<TreeNode>>,
    right: Option<Box<TreeNode>>
}

struct BinaryTree {
    root: Option<Box<TreeNode>>
}

fn create_tree() -> BinaryTree {
    return BinaryTree { root: Option::None };
}

fn insert(tree: BinaryTree, value: i32) -> BinaryTree {
    let new_node = TreeNode {
        value: value,
        left: Option::None,
        right: Option::None
    };
    
    match tree.root {
        Option::None => {
            return BinaryTree { 
                root: Option::Some(Box::new(new_node)) 
            };
        }
        Option::Some(root) => {
            // Simplified insertion logic
            if value < root.value {
                // Insert left (simplified)
                return tree;
            } else {
                // Insert right (simplified)
                return tree;
            }
        }
    }
}

fn inorder_traversal(tree: BinaryTree) {
    match tree.root {
        Option::None => return,
        Option::Some(root) => {
            // Simplified traversal
            printf("%d ", root.value);
        }
    }
}

fn main() {
    let tree = create_tree();
    let tree = insert(tree, 50);
    let tree = insert(tree, 30);
    let tree = insert(tree, 70);
    
    printf("In-order traversal: ");
    inorder_traversal(tree);
    printf("\n");
}
```

## 🔧 Generic Programming

Generics allow you to write code that works with multiple types.

### Generic Functions

```flow
extern "C" fn printf(s: string, ...);

// Generic function that works with any type
fn swap<T>(a: T, b: T) -> (T, T) {
    return (b, a);
}

// Generic function with constraints
fn max<T>(a: T, b: T) -> T {
    if a > b {
        return a;
    }
    return b;
}

fn main() {
    // Swap integers
    let (x, y) = swap(10, 20);
    printf("Swapped: %d, %d\n", x, y);
    
    // Swap strings
    let (s1, s2) = swap("hello", "world");
    printf("Swapped: %s, %s\n", s1, s2);
    
    // Find maximum
    let max_int = max(10, 20);
    let max_float = max(3.14, 2.71);
    
    printf("Max int: %d\n", max_int);
    printf("Max float: %f\n", max_float);
}
```

### Generic Structs

```flow
extern "C" fn printf(s: string, ...);

// Generic struct
struct Container<T> {
    value: T,
    count: i32
}

// Generic implementation
impl<T> Container<T> {
    fn new(value: T) -> Container<T> {
        return Container { value: value, count: 1 };
    }
    
    fn get_value(&self) -> T {
        return self.value;
    }
    
    fn increment_count(&mut self) {
        self.count = self.count + 1;
    }
}

fn main() {
    let int_container = Container::new(42);
    let string_container = Container::new("Hello");
    
    printf("Int container value: %d\n", int_container.get_value());
    printf("String container value: %s\n", string_container.get_value());
}
```

## 🎯 Advanced Functions

### Higher-Order Functions

```flow
extern "C" fn printf(s: string, ...);

// Function that takes another function as parameter
fn apply_twice<T>(f: fn(T) -> T, value: T) -> T {
    return f(f(value));
}

// Function that returns a function
fn create_adder(n: i32) -> fn(i32) -> i32 {
    return fn(x: i32) -> i32 {
        return x + n;
    };
}

fn main() {
    // Higher-order function
    let double = fn(x: i32) -> i32 { return x * 2; };
    let result = apply_twice(double, 5);  // (5 * 2) * 2 = 20
    printf("Result: %d\n", result);
    
    // Function factory
    let add_five = create_adder(5);
    let sum = add_five(10);  // 10 + 5 = 15
    printf("Sum: %d\n", sum);
}
```

### Closures and Lambdas

```flow
extern "C" fn printf(s: string, ...);

fn filter<T>(arr: [T; 5], predicate: fn(T) -> bool) -> [T; 5] {
    let mut result: [T; 5];
    let mut count = 0;
    
    for i in range(0, 5) {
        if predicate(arr[i]) {
            result[count] = arr[i];
            count = count + 1;
        }
    }
    
    return result;
}

fn main() {
    let numbers = [1, 2, 3, 4, 5];
    
    // Using a lambda
    let even_numbers = filter(numbers, fn(x: i32) -> bool {
        return x % 2 == 0;
    });
    
    printf("Even numbers: ");
    for i in range(0, 5) {
        printf("%d ", even_numbers[i]);
    }
    printf("\n");
}
```

## 📊 Working with Files

### File I/O Operations

```flow
extern "C" fn printf(s: string, ...);
extern "C" fn fopen(filename: string, mode: string) -> i32;
extern "C" fn fclose(file: i32) -> i32;
extern "C" fn fprintf(file: i32, format: string, ...) -> i32;
extern "C" fn fgets(buffer: string, size: i32, file: i32) -> string;

fn write_to_file(filename: string, content: string) -> bool {
    let file = fopen(filename, "w");
    if file == 0 {
        return false;
    }
    
    fprintf(file, "%s", content);
    fclose(file);
    return true;
}

fn read_from_file(filename: string) -> string {
    let file = fopen(filename, "r");
    if file == 0 {
        return "";
    }
    
    let buffer: [char; 1024];
    let content = fgets(buffer, 1024, file);
    fclose(file);
    return content;
}

fn main() {
    let success = write_to_file("test.txt", "Hello, FLOW!");
    if success {
        printf("File written successfully\n");
    } else {
        printf("Failed to write file\n");
    }
    
    let content = read_from_file("test.txt");
    printf("File content: %s\n", content);
}
```

## 🧪 Practice Project: Student Management System

Let's create a complete student management system using everything we've learned:

```flow
// student_management.flow
extern "C" fn printf(s: string, ...);
extern "C" fn fopen(filename: string, mode: string) -> i32;
extern "C" fn fclose(file: i32) -> i32;
extern "C" fn fprintf(file: i32, format: string, ...) -> i32;

struct Student {
    id: i32,
    name: string,
    age: i32,
    grades: [f64; 3]
}

struct StudentDatabase {
    students: [Student; 100],
    count: i32
}

fn create_database() -> StudentDatabase {
    let students: [Student; 100];
    return StudentDatabase { students: students, count: 0 };
}

fn add_student(db: StudentDatabase, student: Student) -> StudentDatabase {
    if db.count < 100 {
        db.students[db.count] = student;
        db.count = db.count + 1;
    }
    return db;
}

fn find_student(db: StudentDatabase, id: i32) -> Option<Student> {
    for i in range(0, db.count) {
        if db.students[i].id == id {
            return Option::Some(db.students[i]);
        }
    }
    return Option::None;
}

fn calculate_average(grades: [f64; 3]) -> f64 {
    let mut sum = 0.0;
    for i in range(0, 3) {
        sum = sum + grades[i];
    }
    return sum / 3.0;
}

fn print_student(student: Student) {
    printf("ID: %d\n", student.id);
    printf("Name: %s\n", student.name);
    printf("Age: %d\n", student.age);
    printf("Grades: %.1f, %.1f, %.1f\n", 
           student.grades[0], student.grades[1], student.grades[2]);
    
    let avg = calculate_average(student.grades);
    printf("Average: %.2f\n", avg);
    
    match avg {
        score if score >= 90.0 => printf("Grade: A\n"),
        score if score >= 80.0 => printf("Grade: B\n"),
        score if score >= 70.0 => printf("Grade: C\n"),
        score if score >= 60.0 => printf("Grade: D\n"),
        _ => printf("Grade: F\n")
    }
}

fn save_database(db: StudentDatabase, filename: string) -> bool {
    let file = fopen(filename, "w");
    if file == 0 {
        return false;
    }
    
    fprintf(file, "%d\n", db.count);
    for i in range(0, db.count) {
        let student = db.students[i];
        fprintf(file, "%d,%s,%d,%.1f,%.1f,%.1f\n", 
                student.id, student.name, student.age,
                student.grades[0], student.grades[1], student.grades[2]);
    }
    
    fclose(file);
    return true;
}

fn main() {
    let db = create_database();
    
    // Add some students
    let student1 = Student {
        id: 1,
        name: "Alice Johnson",
        age: 20,
        grades: [95.0, 87.5, 92.0]
    };
    
    let student2 = Student {
        id: 2,
        name: "Bob Smith",
        age: 19,
        grades: [78.0, 82.5, 85.0]
    };
    
    let db = add_student(db, student1);
    let db = add_student(db, student2);
    
    // Find and display a student
    let result = find_student(db, 1);
    match result {
        Option::Some(student) => {
            printf("Found student:\n");
            print_student(student);
        }
        Option::None => printf("Student not found\n")
    }
    
    // Save to file
    let success = save_database(db, "students.txt");
    if success {
        printf("Database saved successfully\n");
    } else {
        printf("Failed to save database\n");
    }
}
```

## 🚀 Next Steps

Congratulations! You've mastered intermediate FLOW concepts. Here's what to explore next:

1. **[Advanced Tutorial](advanced.md)** - Learn about effects, graphics programming, and performance optimization
2. **[Effects System](../language/effects.md)** - Discover FLOW's powerful effect system
3. **[Graphics Programming](../language/graphics.md)** - Create visual applications
4. **[Performance Optimization](../language/performance.md)** - Write high-performance code

## 💡 Best Practices

1. **Use Modules** - Organize large programs into logical modules
2. **Handle Errors** - Always handle potential errors gracefully
3. **Use Pattern Matching** - Prefer pattern matching over complex if-else chains
4. **Write Generic Code** - Use generics to write reusable components
5. **Test Your Code** - Write tests for your functions and modules

---

*Ready for advanced FLOW programming? Let's continue! 🚀*
