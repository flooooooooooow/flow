# FLOW Tutorial: Beginner

Learn FLOW from scratch with hands-on examples. Every program below with a `main` function **runs in your browser**. Click **Run** to execute it, or open the [interactive tutorials app](index.html).

## Part 1: Your First Program

### 1.1 Hello World

Create `hello.flow`:

```flow
function main() -> i32 {
    printf("Hello, World!\n")
    return 0
}
```

Run it:
```bash
./flow run hello.flow
```

**Key points:**
- Every FLOW program needs a `main` function
- `main` returns `i32` (32-bit integer)
- `printf` is available by default (from C stdlib)
- Strings use double quotes
- `\n` is a newline

### 1.2 Variables

```flow
function main() -> i32 {
    # Integer types
    let age: i32 = 25
    let big_number: i64 = 9999999999
    
    # Floating point
    let pi: f32 = 3.14159
    let precise_pi: f64 = 3.14159265358979
    
    # Boolean
    let is_active: bool = true
    
    # String
    let name: string = "Alice"
    
    printf("Name: %s, Age: %d\n", name, age)
    printf("Pi: %f\n", pi)
    
    return 0
}
```

### 1.3 Basic Operations

```flow
function main() -> i32 {
    let a = 10
    let b = 3
    
    # Arithmetic
    printf("a + b = %d\n", a + b)   # 13
    printf("a - b = %d\n", a - b)   # 7
    printf("a * b = %d\n", a * b)   # 30
    printf("a / b = %d\n", a / b)   # 3 (integer division)
    printf("a %% b = %d\n", a % b)  # 1 (modulo)
    
    # Comparison
    printf("a > b: %d\n", a > b)    # 1 (true)
    printf("a == b: %d\n", a == b)  # 0 (false)
    
    # Logical
    let x = true
    let y = false
    printf("x && y: %d\n", x && y)  # 0
    printf("x || y: %d\n", x || y)  # 1
    printf("!x: %d\n", !x)          # 0
    
    return 0
}
```

---

## Part 2: Control Flow

### 2.1 If Statements

```flow
function check_number(n: i32) -> void {
    if n > 0 {
        printf("%d is positive\n", n)
    } elif n < 0 {
        printf("%d is negative\n", n)
    } else {
        printf("It's zero\n")
    }
}

function main() -> i32 {
    check_number(5)
    check_number(-3)
    check_number(0)
    return 0
}
```

### 2.2 While Loops

```flow
function main() -> i32 {
    # Count from 1 to 5
    let mut i = 1
    while i <= 5 {
        printf("%d\n", i)
        i = i + 1
    }
    
    # Sum 1 to 100
    let mut sum = 0
    let mut n = 1
    while n <= 100 {
        sum = sum + n
        n = n + 1
    }
    printf("Sum 1-100: %d\n", sum)  # 5050
    
    return 0
}
```

### 2.3 For Loops

```flow
function main() -> i32 {
    # Basic for loop
    for i in 0..5 {
        printf("%d ", i)  # 0 1 2 3 4
    }
    printf("\n")
    
    # With step
    for i in 0..10 step 2 {
        printf("%d ", i)  # 0 2 4 6 8
    }
    printf("\n")
    
    return 0
}
```

---

## Part 3: Functions

### 3.1 Basic Functions

```flow
# No return value
function greet(name: string) -> void {
    printf("Hello, %s!\n", name)
}

# Returns a value
function add(a: i32, b: i32) -> i32 {
    return a + b
}

# Multiple parameters
function power(base: i32, exp: i32) -> i32 {
    let mut result = 1
    for i in 0..exp {
        result = result * base
    }
    return result
}

function main() -> i32 {
    greet("Alice")
    printf("2 + 3 = %d\n", add(2, 3))
    printf("2^10 = %d\n", power(2, 10))
    return 0
}
```

### 3.2 Recursion

```flow
function factorial(n: i32) -> i32 {
    if n <= 1 {
        return 1
    }
    return n * factorial(n - 1)
}

function fibonacci(n: i32) -> i32 {
    if n <= 1 {
        return n
    }
    return fibonacci(n - 1) + fibonacci(n - 2)
}

function main() -> i32 {
    printf("5! = %d\n", factorial(5))        # 120
    printf("fib(10) = %d\n", fibonacci(10))  # 55
    return 0
}
```

---

## Part 4: Data Structures

### 4.1 Structs

```flow
struct Point {
    x: f32,
    y: f32
}

struct Rectangle {
    top_left: Point,
    width: f32,
    height: f32
}

function point_new(x: f32, y: f32) -> Point {
    return Point { x: x, y: y }
}

function rect_area(r: Rectangle) -> f32 {
    return r.width * r.height
}

function main() -> i32 {
    let p = point_new(10.0, 20.0)
    printf("Point: (%f, %f)\n", p.x, p.y)
    
    let rect = Rectangle {
        top_left: Point { x: 0.0, y: 0.0 },
        width: 5.0,
        height: 3.0
    }
    printf("Area: %f\n", rect_area(rect))  # 15.0
    
    return 0
}
```

### 4.2 Arrays

```flow
function main() -> i32 {
    # Fixed-size array (stored on stack)
    let arr: array<i32, 5> = [1, 2, 3, 4, 5]
    
    # Access elements
    printf("First: %d\n", arr[0])
    printf("Last: %d\n", arr[4])
    
    # Sum all elements
    let mut sum = 0
    for i in 0..5 {
        sum = sum + arr[i]
    }
    printf("Sum: %d\n", sum)  # 15
    
    return 0
}
```

---

## Part 5: Modules

### 5.1 Importing

```flow
# Import from standard library
import "stdlib/math.flow"
import "stdlib/string.flow"

function main() -> i32 {
    let x = sin(3.14159 / 2.0)  # ~1.0
    printf("sin(pi/2) = %f\n", x)
    return 0
}
```

### 5.2 Creating Modules

Create `mylib.flow`:

```flow
export function double(n: i32) -> i32 {
    return n * 2
}

export function triple(n: i32) -> i32 {
    return n * 3
}
```

Use it in `main.flow`:

```flow-pseudocode
import "mylib.flow"

function main() -> i32 {
    printf("double(5) = %d\n", double(5))  # 10
    printf("triple(5) = %d\n", triple(5))  # 15
    return 0
}
```

---

## Part 6: Pattern Matching

### 6.1 Match Expressions

```flow
function day_name(day: i32) -> string {
    match day {
        1 => { return "Monday" }
        2 => { return "Tuesday" }
        3 => { return "Wednesday" }
        4 => { return "Thursday" }
        5 => { return "Friday" }
        6 => { return "Saturday" }
        7 => { return "Sunday" }
        default { return "Invalid" }
    }
    return "Invalid"
}

function main() -> i32 {
    printf("Day 3 is %s\n", day_name(3))  # Wednesday
    return 0
}
```

### 6.2 Match on tags (browser)

Enums need the native compiler (`enum` is unsupported in the browser
interpreter). Tag-style matching with integers teaches the same shape:

```flow
function wait_seconds(light: i32) -> i32 {
    match light {
        0 => { return 30 }
        1 => { return 5 }
        2 => { return 25 }
        default { return -1 }
    }
    return -1
}

function main() -> i32 {
    printf("red waits %d s\n", wait_seconds(0))
    printf("green waits %d s\n", wait_seconds(2))
    return 0
}
```

Native enums:

```bash
./flow run examples/basics/match_enums.flow
```

---

## Exercises

### Exercise 1: FizzBuzz

Write a program that prints numbers 1 to 100, but:
- For multiples of 3, print "Fizz"
- For multiples of 5, print "Buzz"
- For multiples of both, print "FizzBuzz"

<details>
<summary>Solution</summary>

```flow
function main() -> i32 {
    for i in 1..101 {
        if i % 15 == 0 {
            printf("FizzBuzz\n")
        } elif i % 3 == 0 {
            printf("Fizz\n")
        } elif i % 5 == 0 {
            printf("Buzz\n")
        } else {
            printf("%d\n", i)
        }
    }
    return 0
}
```
</details>

### Exercise 2: Prime Numbers

Write a function `is_prime(n: i32) -> bool` that returns true if n is prime.

<details>
<summary>Solution</summary>

```flow
function is_prime(n: i32) -> bool {
    if n < 2 {
        return false
    }
    let mut i = 2
    while i * i <= n {
        if n % i == 0 {
            return false
        }
        i = i + 1
    }
    return true
}

function main() -> i32 {
    for i in 1..20 {
        if is_prime(i) {
            printf("%d is prime\n", i)
        }
    }
    return 0
}
```
</details>

### Exercise 3: Struct Operations

Create a `Vector2D` struct with `x` and `y` fields. Implement:
- `vector_add(a, b)` - add two vectors
- `vector_dot(a, b)` - dot product
- `vector_magnitude(v)` - length of vector

<details>
<summary>Solution</summary>

```flow
struct Vector2D {
    x: f32,
    y: f32
}

function vector_add(a: Vector2D, b: Vector2D) -> Vector2D {
    return Vector2D { x: a.x + b.x, y: a.y + b.y }
}

function vector_dot(a: Vector2D, b: Vector2D) -> f32 {
    return a.x * b.x + a.y * b.y
}

function vector_magnitude(v: Vector2D) -> f32 {
    return sqrt(v.x * v.x + v.y * v.y)
}

function main() -> i32 {
    let a = Vector2D { x: 3.0, y: 0.0 }
    let b = Vector2D { x: 0.0, y: 4.0 }
    
    let sum = vector_add(a, b)
    printf("Sum: (%f, %f)\n", sum.x, sum.y)
    
    printf("Dot: %f\n", vector_dot(a, b))
    printf("Magnitude of a: %f\n", vector_magnitude(a))
    
    return 0
}
```
</details>

---

## Next Steps

Continue to [Intermediate Tutorial](intermediate.md) to learn:
- Generics
- Traits
- Enums
- Error handling with Option/Result
- Effects system
