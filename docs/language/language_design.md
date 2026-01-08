# FLOW: Fast Language for Optimizable Operations

## Design Philosophy

FLOW is a systems programming language designed specifically for:
1. **Fast transpilation** to MLIR/LLVMIR with minimal overhead
2. **LLM-friendly** syntax that's easy to generate and parse
3. **Human-readable** structure for debugging and maintenance
4. **Zero-cost abstractions** - no runtime penalty for high-level constructs

## Core Principles

### 1. Predictable Mapping to MLIR/LLVMIR
- Every language construct has a direct, obvious mapping to MLIR/LLVMIR
- No hidden runtime or complex semantics
- Explicit memory management and layout

### 2. LLM-Optimized Syntax
- Consistent, regular grammar with minimal exceptions
- Verbose but clear keywords (no cryptic symbols)
- Strong typing with explicit type annotations
- Minimal syntactic sugar

### 3. Performance-First Design
- Static compilation only (no JIT in language spec)
- Explicit parallelism and vectorization
- Direct hardware control when needed
- Escape hatches for inline MLIR/LLVMIR

## Language Specification

### Basic Syntax

```
# Comments are line-based with #
# No block comments - keeps parsing simple

function main() -> i32 {
    let result: i32 = add_numbers(10, 20)
    return result
}

function add_numbers(a: i32, b: i32) -> i32 {
    return a + b
}
```

### Type System

```
# Primitive types
i8, i16, i32, i64, i128    # Signed integers
u8, u16, u32, u64, u128    # Unsigned integers
f32, f64                   # Floating point
bool                       # Boolean
void                       # No return value

# Vector types (SIMD)
vec4f32                    # 4-element f32 vector
vec8i32                    # 8-element i32 vector

# Array types
[i32; 10]                  # Fixed-size array
[*i32]                     # Pointer to i32
[&i32]                     # Reference to i32

# Function types
fn(i32, i32) -> i32        # Function pointer type
```

### Control Flow

```
function factorial(n: i32) -> i32 {
    if n <= 1 {
        return 1
    } else {
        return n * factorial(n - 1)
    }
}

function sum_array(arr: [*i32], length: i32) -> i32 {
    let sum: i32 = 0
    let i: i32 = 0
    
    while i < length {
        sum = sum + arr[i]
        i = i + 1
    }
    
    return sum
}

# For loops with explicit bounds
function process_data() {
    for i in 0..100 {
        # Process element i
    }
}

# Parallel loops
function parallel_process(data: [*f32], n: i32) {
    parallel for i in 0..n {
        data[i] = data[i] * 2.0
    }
}
```

### Memory Management

```
function memory_example() {
    # Stack allocation
    let stack_array: [i32; 100] = allocate_stack()
    
    # Heap allocation
    let heap_ptr: [*i32] = allocate_heap(i32, 1000)
    
    # Manual deallocation
    deallocate(heap_ptr)
    
    # Memory regions (for MLIR memory ops)
    let region: memory_region = create_region(1024)
    let ptr: [*i32] = region_alloc(region, i32, 100)
    destroy_region(region)
}
```

### Structs and Layouts

```
struct Vector3 {
    x: f32
    y: f32
    z: f32
}

# Explicit layout control
struct packed Point {
    x: i16
    y: i16
} layout(packed)

struct aligned Matrix4 {
    data: [f32; 16]
} layout(align(16))
```

### Function Attributes and Optimization Hints

```
# Inline hint
inline function fast_add(a: i32, b: i32) -> i32 {
    return a + b
}

# Always inline
always_inline function critical_function() {
    # Critical path code
}

# No inline
noinline function large_function() {
    # Large function that shouldn't be inlined
}

# Target-specific attributes
target(cpu: "x86_64", features: "avx2") 
function vectorized_add(a: vec4f32, b: vec4f32) -> vec4f32 {
    return a + b
}
```

### SIMD and Vector Operations

```
function vector_operations() {
    let a: vec4f32 = load_vector(ptr_a)
    let b: vec4f32 = load_vector(ptr_b)
    let result: vec4f32 = a + b  # Vector addition
    
    # Shuffle operations
    let shuffled: vec4f32 = shuffle(a, [1, 0, 3, 2])
    
    # Horizontal operations
    let sum: f32 = horizontal_add(a)
    
    store_vector(result, ptr_c)
}
```

### MLIR Integration

```
# Direct MLIR dialect embedding
mlir_dialect "affine" {
    # Direct MLIR code here
    affine.for %i = 0 to 100 {
        %val = affine.load %A[%i] : memref<100xf32>
        %res = affine.addf %val, %cst : f32
        affine.store %res, %B[%i] : memref<100xf32>
    }
}

# LLVM IR embedding
llvm_ir {
    %1 = add i32 %a, %b
    ret i32 %1
}
```

### Modules and Imports

```
module math_utils {
    export function add(a: f64, b: f64) -> f64 {
        return a + b
    }
    
    export function multiply(a: f64, b: f64) -> f64 {
        return a * b
    }
}

# Import and use
import math_utils

function calculate() -> f64 {
    return math_utils.add(1.0, 2.0) * math_utils.multiply(3.0, 4.0)
}
```

## Grammar Rules (Simplified EBNF)

```
program = { function_decl | struct_decl | import_stmt | module_decl }

function_decl = "function" identifier "(" [param_list] ")" ["->" type] block

param_list = param { "," param }
param = identifier ":" type

type = primitive_type | vector_type | array_type | function_type
primitive_type = "i8" | "i16" | "i32" | "i64" | "i128" 
               | "u8" | "u16" | "u32" | "u64" | "u128"
               | "f32" | "f64" | "bool" | "void"

vector_type = "vec" number type
array_type = "[" type ";" number "]"
function_type = "fn" "(" [type_list] ")" "->" type

block = "{" { statement } "}"
statement = var_decl | assignment | if_stmt | while_stmt | for_stmt 
          | return_stmt | expr_stmt

var_decl = "let" identifier ":" type ["=" expression]
assignment = identifier "=" expression

if_stmt = "if" expression block ["else" block]
while_stmt = "while" expression block
for_stmt = "for" identifier "in" range block
range = expression ".." expression

expression = identifier | literal | binary_op | unary_op | function_call
binary_op = expression operator expression
unary_op = operator expression
function_call = identifier "(" [arg_list] ")"
```

## Transpilation Strategy

### Phase 1: Parsing to AST
- Simple recursive descent parser
- No ambiguity in grammar
- Explicit tokenization

### Phase 2: AST to MLIR
- Direct mapping of constructs
- Type checking and validation
- Optimization hints preservation

### Phase 3: MLIR to LLVMIR
- Use existing MLIR infrastructure
- Preserve performance characteristics
- Generate optimized machine code

## Example: Matrix Multiplication

```
function matrix_multiply(A: [*f32], B: [*f32], C: [*f32], n: i32) {
    # Cache-friendly blocking
    let block_size: i32 = 64
    
    parallel for i in 0..n {
        parallel for j in 0..n {
            let sum: f32 = 0.0
            
            for k in 0..n {
                let a_val: f32 = A[i * n + k]
                let b_val: f32 = B[k * n + j]
                sum = sum + a_val * b_val
            }
            
            C[i * n + j] = sum
        }
    }
}

# Vectorized version
function matrix_multiply_simd(A: [*f32], B: [*f32], C: [*f32], n: i32) {
    parallel for i in 0..n {
        parallel for j in 0..n {
            let sum_vec: vec4f32 = [0.0, 0.0, 0.0, 0.0]
            
            for k in 0..n step 4 {
                let a_vec: vec4f32 = load_vector(&A[i * n + k])
                let b_vec: vec4f32 = load_vector(&B[k * n + j])
                sum_vec = sum_vec + a_vec * b_vec
            }
            
            C[i * n + j] = horizontal_add(sum_vec)
        }
    }
}
```

## Benefits for LLM Generation

1. **Predictable Structure**: Every function follows the same pattern
2. **Explicit Types**: No type inference ambiguity
3. **Clear Keywords**: No cryptic symbols or operators
4. **Regular Grammar**: Easy to generate valid code
5. **Minimal Context**: Local scoping reduces complexity

## Benefits for Performance

1. **Zero-Cost Abstractions**: High-level constructs compile to optimal MLIR
2. **Explicit Parallelism**: Direct mapping to parallel MLIR dialects
3. **SIMD Support**: First-class vector operations
4. **Memory Control**: Explicit allocation and layout
5. **Target Optimization**: Attribute-based target tuning

## Implementation Roadmap

1. **Parser**: Simple recursive descent parser
2. **AST**: Minimal, performance-focused AST
3. **MLIR Generator**: Direct AST to MLIR translation
4. **Optimizer**: MLIR-based optimization pipeline
5. **LLVMIR Backend**: Standard MLIR to LLVMIR conversion

## Lisp-Style Polysemy Extension

### Overview
Add extensible generic functions with multiple dispatch to FLOW, inspired by Common Lisp's CLOS (Common Lisp Object System). This enables polymorphic behavior based on multiple argument types rather than single-recipient message passing.

### Core Features

#### 1. Generic Function Declaration
```flow
# Define a generic function (abstract interface)
generic fn draw(shape: Shape, context: Context) -> void
    documentation: "Render a shape to the given context"
```

#### 2. Method Implementations
```flow
# Single dispatch
method draw(shape: Circle, context: Context) -> void {
    circle_renderer.draw(shape, context)
}

# Multiple dispatch (multimethods)
method beat(drum: SnareDrum, stick: WoodenDrumstick) -> Sound {
    return acoustic_model.hit_snare(drum, stick)
}
```

#### 3. Method Combination
```flow
# Before/after methods
method before withdraw(account: BankAccount, amount: f64) -> void {
    log_transaction("withdrawal_started", account.id, amount)
}

method after withdraw(account: BankAccount, amount: f64) -> void {
    update_balance_display(account)
}

# Primary method with call-next-method
method withdraw(account: BankAccount, amount: f64) -> void {
    if account.balance < amount {
        error("Insufficient funds")
    }
    call_next_method(account, amount)  # Calls more specific method
}
```

#### 4. Type Specialization Patterns
```flow
# EQL specialization (specific values)
method process(value: 42) -> i32 {
    return "the answer"
}

# Range specialization  
method process(value: 0..100) -> i32 {
    return "small number"
}

# Pattern matching integration
method process(shape: Rectangle { width: w, height: h }) -> i32 {
    return w * h
}
```

### Implementation Phases

#### Phase 1: Parser Extensions
- Add `GenericDecl` AST node for generic function declarations
- Add `MethodDecl` AST node for method implementations  
- Add `Specializer` AST node for type/value specializers
- Add `CallNextMethod` AST node for method combination
- Extend keyword map with `generic`, `method`, `before`, `after`, `call_next_method`

#### Phase 2: Type System Extensions
- **Method tables**: Per-generic-function dispatch tables
- **Specializer matching**: Algorithm for determining applicable methods
- **Method precedence**: Rules for method specificity and ordering
- **Multiple dispatch**: Runtime resolution based on argument types
- **Type checking**: Compile-time validation of method signatures

#### Phase 3: MLIR Generation
- **Dispatch tables**: Generate lookup structures for each generic function
- **Type-based dispatch**: Runtime dispatch mechanism
- **Inline optimization**: Devirtualization for monomorphic calls
- **Method combination**: Infrastructure for before/after/around methods
- **Performance optimization**: Cache dispatch results, inline when possible

#### Phase 4: Advanced Features
- **Generic function introspection**: Runtime inspection of methods
- **Method addition/removal**: Dynamic method registration
- **Custom method combinations**: User-defined combination strategies
- **Performance profiling**: Dispatch optimization based on usage patterns

### Benefits

1. **Extensibility**: New types can add methods without modifying existing code
2. **Multiple Dispatch**: Behavior based on multiple argument types
3. **Open/Closed Principle**: Open for extension, closed for modification
4. **Type Safety**: Compile-time checking of method signatures
5. **Performance**: Monomorphic calls can be devirtualized
6. **Separation of Concerns**: Operations decoupled from data types

### Example Use Cases

#### Graphics Rendering System
```flow
generic fn render(obj: Renderable, target: RenderTarget) -> void

method render(obj: 3DModel, target: OpenGLContext) -> void {
    opengl_renderer.draw_model(obj, target)
}

method render(obj: 3DModel, target: VulkanContext) -> void {
    vulkan_renderer.draw_model(obj, target)
}

# Usage - automatic dispatch based on both argument types
fn render_scene(scene: Scene, target: RenderTarget) {
    for obj in scene.objects {
        render(obj, target)  # Dispatches to correct method
    }
}
```

#### Mathematical Operations
```flow
generic fn add(a: Numeric, b: Numeric) -> Numeric

method add(a: Vector2D, b: Vector2D) -> Vector2D {
    return Vector2D { x: a.x + b.x, y: a.y + b.y }
}

method add(a: Matrix, b: Matrix) -> Matrix {
    return matrix_add(a, b)  # Optimized matrix addition
}

method add(a: Scalar, b: Vector2D) -> Vector2D {
    return Vector2D { x: a.value + b.x, y: a.value + b.y }
}
```

### Integration with Existing Features

- **Structs**: Natural fit with existing struct system
- **Pattern Matching**: Can be used in method specializers
- **Effects System**: Methods can participate in effect handling
- **Modules**: Generic functions can be exported/imported
- **Performance**: Zero-cost abstractions for monomorphic calls

This design balances the needs of fast compilation, LLM generation, and human readability while maintaining direct paths to high-performance MLIR/LLVMIR code and adding powerful extensible polymorphism capabilities.
