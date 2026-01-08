# Data Structures Examples

This directory contains examples of data structures in FLOW, including custom structs and their usage.

## Files

- **stack.flow** - Stack implementation with push/pop operations
- **composition_car_engine.flow** - Struct composition example (car with engine)
- **oop_person.flow** - Object-oriented style person struct

## Running Examples

```bash
# Test the stack implementation
flow run stack.flow

# See struct composition
flow run composition_car_engine.flow

# OOP-style programming
flow run oop_person.flow
```

## What You'll Learn

1. **Struct Definition**: How to define custom data structures
2. **Field Access**: Accessing and modifying struct fields
3. **Composition**: Combining structs to create complex types
4. **Methods**: Functions that operate on structs
5. **Memory Layout**: How structs are organized in memory

## Key Concepts

### Struct Definition
```flow
struct Point {
    x: f64,
    y: f64
}
```

### Field Access
```flow
let p = Point { x: 10.0, y: 20.0 };
printf("X: %.2f\n", p.x);
```

### Composition
```flow
struct Engine {
    horsepower: i32
}

struct Car {
    engine: Engine,
    make: string
}
```

## Prerequisites

- Understanding of basic FLOW syntax
- Familiarity with functions and variables
- [Basic Examples](../basic/) completed

## Related Topics

- [Algorithms](../algorithms/) - Algorithms using data structures
- [Graphics Examples](../graphics/) - Graphics data structures
- [Language Reference - Structs](../../language/structs.md) - Complete struct documentation
