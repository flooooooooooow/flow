# FLOW Syntax and Grammar

This section describes the formal syntax and grammar of the FLOW programming language.

## 📝 Lexical Structure

### Keywords

FLOW reserves the following keywords:

```
function, struct, if, else, while, return, let, const, true, false, 
capability, effect, handler, import, export, extern, and, or, not, 
in, for, break, continue, match, case, when
```

### Identifiers

Identifiers start with a letter or underscore, followed by letters, digits, or underscores:

```
valid_name, _private, value123, camelCase, snake_case
```

### Literals

#### Integer Literals
```
42, -17, 0, 1_000_000, 0xFF, 0b1010, 0o52
```

#### Floating Point Literals
```
3.14, -0.001, 1.5e10, 2.5f, 1.0e-5
```

#### String Literals
```
"Hello, World!", "Line 1\nLine 2", "Unicode: \u{1F600}"
```

#### Boolean Literals
```
true, false
```

### Comments

```
# Single line comment

# 
# Multi-line comment
# spanning multiple lines
#
```

## 🔤 Types

### Primitive Types

```
i8, i16, i32, i64      # Signed integers
u8, u16, u32, u64      # Unsigned integers  
f32, f64               # Floating point numbers
bool                   # Boolean
string                 # String
void                   # No return value
```

### Array Types

```
[i32]           # Array of integers
[f32; 10]       # Fixed-size array of 10 floats
[string]        # Array of strings
```

### Struct Types

```
struct Point {
    x: f32,
    y: f32
}

struct Rectangle {
    top_left: Point,
    width: f32,
    height: f32
}
```

## 🎯 Expressions

### Literals

```
42                    # Integer
3.14                  # Float
"hello"               # String
true                  # Boolean
```

### Variables and Constants

```
let x = 42
const PI = 3.14159
name                  # Variable reference
```

### Binary Operations

```
x + y                 # Addition
x - y                 # Subtraction
x * y                 # Multiplication
x / y                 # Division
x % y                 # Modulo
x and y               # Logical AND
x or y                # Logical OR
x == y                # Equality
x != y                # Inequality
x < y                 # Less than
x <= y                # Less than or equal
x > y                 # Greater than
x >= y                # Greater than or equal
```

### Unary Operations

```
-x                    # Negation
not x                 # Logical NOT
```

### Function Calls

```
func(arg1, arg2)
print("Hello")
math.sqrt(16.0)
```

### Field Access

```
point.x
rect.top_left.x
array[0]
```

## 🔄 Statements

### Variable Declarations

```
let x: i32 = 42
const name: string = "FLOW"
let mutable_var = calculate_value()
```

### Assignments

```
x = 10
point.x = 3.14
array[0] = 42
```

### Function Definitions

```
function add(a: i32, b: i32) -> i32 {
    return a + b
}

function greet(name: string) -> void {
    print("Hello, " + name + "!")
}
```

### Control Flow

#### If Statements

```
if x > 0 {
    print("Positive")
} else if x < 0 {
    print("Negative") 
} else {
    print("Zero")
}
```

#### While Loops

```
while i < 10 {
    print(i)
    i = i + 1
}
```

#### For Loops (Range)

```
for i in 0..10 {
    print(i)
}

for i in 0..length(array) {
    process(array[i])
}
```

### Return Statements

```
return 42
return result
return  # Early return from void function
```

## 🏗️ Struct Definitions

```
struct Point {
    x: f32,
    y: f32
}

struct Person {
    name: string,
    age: i32,
    address: Address
}
```

### Struct Literals

```
let p = Point { x: 3.14, y: 2.71 }
let person = Person {
    name: "Alice",
    age: 30,
    address: Address { city: "NYC", zip: "10001" }
}
```

## 🎮 Capability Declarations

```
capability gpu
capability graphics
capability simd

function gpu_function() -> void {
    # GPU-accelerated code
}
```

## 🌊 Effect Declarations

```
effect State {
    get(key: string) -> any
    set(key: string, value: any) -> void
}

effect IO {
    read_file(path: string) -> string
    write_file(path: string, content: string) -> void
}
```

## 📦 Module System

### Imports

```
import "math"
import "graphics"
import "my_module"

# Import specific items
import math.{sqrt, sin, cos}
```

### Exports

```
export function public_api() -> void {
    # Public function
}

export const PUBLIC_CONSTANT = 42
```

### External Declarations

```
extern {
    function printf(format: string, ...) -> i32
    function malloc(size: i64) -> i64
    function free(ptr: i64) -> void
}
```

## 🎯 Pattern Matching

```
match value {
    0 => print("Zero"),
    1 => print("One"),
    n => print("Other: " + string(n))
}

match point {
    Point { x: 0.0, y: 0.0 } => print("Origin"),
    Point { x, y } => print("Point: " + string(x) + ", " + string(y))
}
```

## 🔧 Grammar (EBNF)

```
program = { declaration }

declaration = 
    | function_decl
    | struct_decl
    | const_decl
    | capability_decl
    | effect_decl
    | import_decl
    | export_decl
    | extern_decl

function_decl = "function" identifier "(" [parameter_list] ")" "->" type block_stmt

struct_decl = "struct" identifier "{" { field_decl "}" } "}"

field_decl = identifier ":" type

const_decl = "const" identifier ":" type "=" expression

capability_decl = "capability" identifier

effect_decl = "effect" identifier "{" { effect_operation "}" } "}"

effect_operation = identifier "(" [parameter_list] ")" "->" type

import_decl = "import" string_literal

export_decl = "export" declaration

extern_decl = "extern" "{" { extern_function "}" }"

extern_function = "function" identifier "(" [parameter_list] ")" "->" type

type = 
    | primitive_type
    | array_type
    | struct_type
    | function_type

primitive_type = "i8" | "i16" | "i32" | "i64" | "u8" | "u16" | "u32" | "u64" | "f32" | "f64" | "bool" | "string" | "void"

array_type = "[" type [ ";" integer_literal ] "]"

struct_type = identifier

function_type = "(" [type_list] ")" "->" type

expression = 
    | literal
    | identifier
    | unary_op expression
    | expression binary_op expression
    | function_call
    | field_access
    | array_access
    | struct_literal
    | "(" expression ")"

statement = 
    | var_decl
    | assignment
    | function_call
    | if_stmt
    | while_stmt
    | for_stmt
    | return_stmt
    | block_stmt
    | expression_stmt

var_decl = "let" identifier [ ":" type ] "=" expression

assignment = expression "=" expression

if_stmt = "if" expression block_stmt [ "else" ( if_stmt | block_stmt ) ]

while_stmt = "while" expression block_stmt

for_stmt = "for" identifier "in" range_expr block_stmt

range_expr = expression ".." expression

return_stmt = "return" [ expression ]

block_stmt = "{" { statement } "}"
```

## 🚀 Syntax Examples

### Complete Program

```
# Example: Simple calculator
import "math"

struct Calculator {
    memory: f32
}

function Calculator.new() -> Calculator {
    return Calculator { memory: 0.0 }
}

function Calculator.add(self: Calculator, value: f32) -> f32 {
    self.memory = self.memory + value
    return self.memory
}

function Calculator.sqrt(self: Calculator, value: f32) -> f32 {
    return math.sqrt(value)
}

function main() -> i32 {
    let calc = Calculator.new()
    let result = calc.add(10.0)
    let sqrt_result = calc.sqrt(result)
    
    print("Result: " + string(sqrt_result))
    return 0
}
```

### GPU Function

```
capability gpu

function vector_add(a: [f32], b: [f32], result: [f32], n: i32) -> void {
    for i in 0..n {
        result[i] = a[i] + b[i]
    }
}
```

### Effect Handler

```
effect Logger {
    log(message: string) -> void
}

handler with_logger() {
    log("Starting operation")
    # ... code that uses log effect
    log("Operation complete")
}

function main() -> void {
    with_logger()
}
```

This syntax reference provides the complete formal specification of the FLOW language.
