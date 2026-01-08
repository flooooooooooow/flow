# Language Reference Index

Welcome to the FLOW language reference! This section provides comprehensive documentation of all language features.

## 📋 Language Topics

### 🎯 [Overview](overview.md)
Language philosophy, design goals, and quick introduction

### 📝 [Syntax and Grammar](syntax.md)
- Lexical structure
- Grammar rules
- Syntax conventions
- Code formatting

### 🔢 [Type System](types.md)
- Primitive types
- Type inference
- Generic types
- Type conversions

### 📦 [Variables and Constants](variables.md)
- Variable declarations
- Constants
- Scope and lifetime
- Mutability

### 🔄 [Functions](functions.md)
- Function definitions
- Parameters and returns
- Closures and lambdas
- Higher-order functions

### 🔀 [Control Flow](control-flow.md)
- Conditional statements
- Loops and iteration
- Pattern matching
- Exception handling

### 🏗️ [Structs and Records](structs.md)
- Struct definitions
- Field access
- Memory layout
- Methods and impl blocks

### 📋 [Arrays and Slices](arrays.md)
- Array types
- Array operations
- Slices and views
- Multi-dimensional arrays

### 🎭 [Pattern Matching](pattern-matching.md)
- Match expressions
- Pattern types
- Destructuring
- Guards and conditions

### ✨ [Effects System](effects.md)
- Algebraic effects
- Effect handlers
- Capability types
- Composable programs

### 📦 [Modules and Packages](modules.md)
- Module system
- Imports and exports
- Package management
- Namespaces

### 🎨 [Graphics Programming](graphics.md)
- Built-in graphics
- Rendering pipeline
- Shaders and GPU
- Scene graphs

### 🧠 [Memory Management](memory.md)
- Memory allocation
- Manual vs automatic
- Pointers and references
- Memory safety

### ⚡ [Performance Optimization](performance.md)
- SIMD operations
- GPU computing
- Parallelism
- Optimization techniques

### 🚨 [Error Handling](error-handling.md)
- Error types
- Result and Option
- Panic and recover
- Error propagation

### 🔧 [Metaprogramming](metaprogramming.md)
- Compile-time computation
- Macros
- Code generation
- Reflection

### 🔌 [Foreign Function Interface](ffi.md)
- C interoperability
- External functions
- Callbacks
- Library linking

## 🎯 Quick Reference

### Basic Syntax
```flow
// Variable declaration
let x = 42;
let y: f64 = 3.14;

// Function definition
fn add(a: i32, b: i32) -> i32 {
    return a + b;
}

// Struct definition
struct Point {
    x: f64,
    y: f64
}

// Pattern matching
match value {
    0 => "zero",
    n => "other"
}
```

### Key Concepts

- **Static Typing**: All types checked at compile time
- **Type Inference**: Compiler can deduce types automatically
- **Pattern Matching**: Powerful conditional expressions
- **Effects System**: Composable side effects
- **Memory Safety**: Manual control with safety guarantees

## 📚 Learning Path

1. **Start with [Overview](overview.md)** - Language introduction
2. **Learn [Syntax and Grammar](syntax.md)** - Basic language rules
3. **Study [Type System](types.md)** - Understanding types
4. **Master [Functions](functions.md)** - Building blocks
5. **Explore [Control Flow](control-flow.md)** - Program logic
6. **Learn [Structs](structs.md)** - Data structures
7. **Discover [Effects](effects.md)** - Advanced features
8. **Study [Performance](performance.md)** - Optimization

## 🔗 Related Resources

- **[Getting Started](../getting-started.md)** - Installation and first program
- **[Tutorials](../tutorials/)** - Step-by-step guides
- **[Standard Library](../library/)** - API documentation
- **[Examples](../examples/)** - Code examples
- **[Reference](../reference/)** - Quick reference materials

---

*Need help? Check the [Getting Started](../getting-started.md) guide or visit the [Examples](../examples/) gallery! 🚀*
