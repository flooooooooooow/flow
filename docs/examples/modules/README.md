# Modules Examples

This directory contains examples of FLOW's module system, demonstrating code organization, imports, exports, and package management.

## Files

- **main.flow** - Main module demonstrating imports
- **math.flow** - Math module with exported functions
- **a.flow** - Module A (part of module system demo)
- **b.flow** - Module B (part of module system demo)

## Running Examples

```bash
# Run the main module
flow run main.flow

# Test individual modules
flow run math.flow
flow run a.flow
flow run b.flow
```

## What You'll Learn

1. **Module Creation**: How to create and organize modules
2. **Exports**: Making functions and types available to other modules
3. **Imports**: Using code from other modules
4. **Module Aliases**: Creating aliases for imported modules
5. **Package Structure**: Organizing related modules into packages

## Module System Overview

FLOW's module system provides:
- **Encapsulation**: Hide implementation details
- **Reusability**: Share code across projects
- **Namespacing**: Avoid naming conflicts
- **Dependency Management**: Clear module dependencies

## Key Concepts

### Module Definition
```flow
# math.flow
export fn add(a: i32, b: i32) -> i32 {
    return a + b;
}

export fn multiply(a: i32, b: i32) -> i32 {
    return a * b;
}

# Private function (not exported)
fn internal_helper(x: i32) -> i32 {
    return x * 2;
}
```

### Module Import
```flow
# main.flow
import math;

fn main() -> i32 {
    let sum = math.add(10, 20);
    let product = math.multiply(5, 6);
    return sum + product;
}
```

### Selective Import
```flow
import math { add, multiply };

fn main() -> i32 {
    return add(10, 20) + multiply(5, 6);
}
```

### Module Alias
```flow
import math as m;

fn main() -> i32 {
    return m.add(10, 20);
}
```

## Module Organization

### Single File Modules
Simple modules contained in a single `.flow` file:
```flow
# utils.flow
export fn max(a: i32, b: i32) -> i32 {
    return a > b ? a : b;
}

export fn min(a: i32, b: i32) -> i32 {
    return a < b ? a : b;
}
```

### Multi-File Packages
Related modules organized in directories:
```
mypackage/
├── mod1.flow
├── mod2.flow
├── subpackage/
│   ├── mod3.flow
│   └── mod4.flow
└── package.json
```

## Export Patterns

### Functions
```flow
export fn public_function() -> i32 {
    return 42;
}

fn private_function() -> i32 {
    return 24;
}
```

### Types
```flow
export struct Point {
    x: f64,
    y: f64
}

struct InternalType {
    data: i32
}
```

### Constants
```flow
export const PI: f64 = 3.14159;
export const MAX_SIZE: i32 = 1024;
```

### Re-exports
```flow
import base_module;

export { base_module.public_function };
export { base_module.PublicType as Type };
```

## Import Strategies

### Full Import
```flow
import graphics;
import math;
import io;
```

### Selective Import
```flow
import graphics { draw_circle, fill_rectangle };
import math { sin, cos, sqrt };
```

### Aliased Import
```flow
import graphics as gfx;
import mathematics as math;
```

### Qualified Import
```flow
import std.collections as collections;
import std.algorithms as algorithms;
```

## Module Dependencies

### Circular Dependencies
FLOW detects and prevents circular dependencies:
```flow
# A imports B
# B imports A  # ❌ Error: Circular dependency
```

### Dependency Graph
Modules form a directed acyclic graph (DAG):
```
main.flow
├── math.flow
│   └── utils.flow
└── graphics.flow
    ├── math.flow
    └── io.flow
```

## Package Management

### Package Definition
```json
{
    "name": "my_package",
    "version": "1.0.0",
    "description": "A sample FLOW package",
    "modules": ["math", "graphics", "utils"],
    "dependencies": {
        "stdlib": "^1.0.0"
    },
    "author": "Your Name",
    "license": "MIT"
}
```

### Package Installation
```bash
# Install from registry
flow-pkg install some_package

# Install from local path
flow-pkg install ./local_package

# Install from Git
flow-pkg install https://github.com/user/repo.git
```

## Best Practices

### 1. Module Design
- **Single Responsibility**: Each module should have one clear purpose
- **Minimal Exports**: Export only what's necessary
- **Clear Names**: Use descriptive module and function names
- **Documentation**: Document public APIs

### 2. Dependency Management
- **Minimal Dependencies**: Keep dependencies to a minimum
- **Stable APIs**: Maintain backward compatibility
- **Version Carefully**: Use semantic versioning
- **Test Dependencies**: Test with different dependency versions

### 3. Code Organization
- **Logical Grouping**: Group related functionality
- **Hierarchical Structure**: Use subpackages for large projects
- **Consistent Naming**: Follow naming conventions
- **Module Size**: Keep modules focused and manageable

## Common Patterns

### Utility Modules
```flow
# utils.flow
export fn clamp(value: f32, min: f32, max: f32) -> f32 {
    return value < min ? min : (value > max ? max : value);
}

export fn lerp(a: f32, b: f32, t: f32) -> f32 {
    return a + t * (b - a);
}
```

### Configuration Modules
```flow
# config.flow
export const WINDOW_WIDTH: i32 = 800;
export const WINDOW_HEIGHT: i32 = 600;
export const MAX_FPS: i32 = 60;
```

### Platform Abstraction
```flow
# platform.flow
export fn get_time() -> f64;
export fn sleep(seconds: f64) -> void;
export fn open_file(path: string) -> File;
```

## Prerequisites

- Understanding of FLOW functions and types
- Familiarity with basic program structure
- [Basic Examples](../basic/) completed

## Related Topics

- [Language Reference - Modules](../../language/modules.md) - Complete module documentation
- [Standard Library Overview](../../library/overview.md) - Standard library modules
- [Package Management](../../reference/packages.md) - Package system reference
- [Project Structure](../../getting-started.md#project-structure) - Project organization

## Advanced Topics

- **Module Parameters**: Parameterized modules
- **Conditional Compilation**: Platform-specific modules
- **Module Reflection**: Runtime module introspection
- **Dynamic Loading**: Loading modules at runtime
