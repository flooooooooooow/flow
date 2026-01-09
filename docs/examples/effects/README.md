# Effects Examples

This directory contains examples of FLOW's algebraic effects system, demonstrating how to use effects for composable and extensible programs.

## Files

- **simple_effects.flow** - Basic effect definition and handling
- **effects_demo.flow** - More complex effect composition
- **complete_effects.flow** - Comprehensive effects demonstration

## Running Examples

```bash
# Basic effects
flow run simple_effects.flow

# Effects demo
flow run effects_demo.flow

# Complete effects showcase
flow run complete_effects.flow
```

## What You'll Learn

1. **Effect Definition**: How to define custom effects
2. **Effect Handlers**: Writing handlers to manage effects
3. **Effect Composition**: Combining multiple effects
4. **Algebraic Properties**: Understanding effect algebra
5. **Practical Applications**: Real-world effect usage

## Effects System Overview

FLOW's effects system provides:
- **Composable Side Effects**: Separating effectful code from pure logic
- **Type Safety**: Compile-time checking of effect usage
- **Extensibility**: Easy to add new effects
- **Performance**: Zero-cost abstractions where possible

## Key Concepts

### Effect Definition
```flow
effect Logger {
    fn log(message: string);
}
```

### Effect Handling
```flow
fn with_logging<T>(body: () -> T) -> T {
    handle body() {
        log(msg) => {
            printf("LOG: %s\n", msg);
            resume();
        }
    }
}
```

### Effect Usage
```flow
fn program() -> i32 {
    log("Starting program");
    # ... program logic ...
    log("Program finished");
    return 0;
}
```

## Effect Patterns

### 1. Logging Effect
Provides structured logging with different levels:
```flow
effect Logger {
    fn debug(message: string);
    fn info(message: string);
    fn warn(message: string);
    fn error(message: string);
}
```

### 2. State Effect
Manages mutable state in a functional way:
```flow
effect State<T> {
    fn get() -> T;
    fn set(value: T);
}
```

### 3. Exception Effect
Handles errors and exceptions:
```flow
effect Exception {
    fn throw(message: string);
}
```

### 4. IO Effect
Manages input/output operations:
```flow
effect IO {
    fn read() -> string;
    fn write(message: string);
}
```

## Effect Composition

Effects can be composed in various ways:

### Sequential Composition
```flow
fn with_logging_and_state<T>(body: () -> T) -> T {
    with_state(0, fn() {
        with_logging(body)
    })
}
```

### Nested Composition
```flow
fn layered_computation<T>(body: () -> T) -> T {
    with_error_handling(fn() {
        with_logging(fn() {
            with_state(0, body)
        })
    })
}
```

## Advanced Features

### Effect Polymorphism
Functions that work with any effect:
```flow
fn with_any_effect<E, T>(effect: E, body: () -> T) -> T {
    handle body() {
        # Generic effect handling
    }
}
```

### Effect Instances
Creating instances of effects with specific behavior:
```flow
let console_logger = Logger {
    log: fn(msg) { printf("%s\n", msg); }
};
```

## Performance Considerations

1. **Effect Elimination**: Compiler can eliminate unused effects
2. **Inlining**: Effect handlers can be inlined
3. **Specialization**: Specialized handlers for common cases
4. **Zero-Cost**: No runtime overhead for unused effects

## Best Practices

1. **Keep Effects Small**: Single responsibility per effect
2. **Compose Effects**: Build complex behavior from simple effects
3. **Handle Effects Early**: Handle effects close to their definition
4. **Document Effects**: Clear documentation of effect behavior
5. **Test Effects**: Unit tests for effect handlers

## Common Patterns

### Resource Management
```flow
effect Resource {
    fn acquire() -> Resource;
    fn release(resource: Resource);
}
```

### Configuration
```flow
effect Config {
    fn get(key: string) -> string;
    fn set(key: string, value: string);
}
```

### Telemetry
```flow
effect Telemetry {
    fn metric(name: string, value: f64);
    fn event(name: string, data: map[string, string]);
}
```

## Prerequisites

- Strong understanding of FLOW functions and types
- Familiarity with functional programming concepts
- [Basic Examples](../basic/) completed
- [Intermediate Tutorial](../../tutorials/intermediate.md) completed

## Related Topics

- [Language Reference - Effects](../../LANGUAGE_SPEC.md) - Complete effects documentation
- [Advanced Tutorial](../../tutorials/advanced.md) - Advanced effects usage
- [Standard Library - Effects](../../LANGUAGE_SPEC.md) - Built-in effects
- [Modules Examples](../modules/) - Effect organization

## Further Reading

- **Algebraic Effects**: Theory and mathematical foundations
- **Effect Handlers**: Implementation techniques and patterns
- **Functional Programming**: Broader functional programming concepts
- **Category Theory**: Mathematical underpinnings of effects
