# Standard Library Index

Welcome to the FLOW standard library documentation! This section provides comprehensive reference for all modules, functions, and types available in FLOW's standard library.

## 📚 Library Overview

The FLOW standard library is organized into logical modules, each providing specific functionality:

### 🔧 [Core Types](core.md)
- Primitive types and operations
- Basic type utilities
- Type conversions
- Memory operations

### 🧠 [Memory Management](memory.md)
- Memory allocation and deallocation
- Memory manipulation functions
- Alignment and layout utilities
- Memory safety and debugging
- Stack allocation and memory pools

### 🔢 [Math Library](math.md)
- Mathematical functions
- Trigonometry and geometry
- Random number generation
- Statistical functions

### 📝 [String Operations](strings.md)
- String manipulation
- Text processing
- Regular expressions
- Encoding and decoding

### 📋 [Array Operations](arrays.md)
- Array utilities
- Sorting and searching
- Data structures
- Collection operations

### 📁 [File I/O](io.md)
- File system operations
- Stream handling
- Path manipulation
- Directory operations

### 🧠 [Memory Management](memory.md)
- Memory allocation
- Smart pointers
- Memory pools
- Garbage collection

### 🎨 [Graphics Library](graphics.md)
- 2D/3D rendering
- Image processing
- Window management
- Shader programming

### 🧪 [Testing Framework](testing.md)
- Unit testing
- Benchmarks
- Test utilities
- Assertion helpers

### ⚡ [Concurrency](concurrency.md)
- Threads and async
- Synchronization
- Message passing
- Parallel computing

### 🚨 [Error Handling](errors.md)
- Error types
- Exception utilities
- Error propagation
- Debugging tools

### 📊 [Profiling Tools](profiling.md)
- Performance analysis
- Memory profiling
- Timing utilities
- Optimization helpers

### 🗄️ [Collections](collections.md)
- Advanced data structures
- Maps and sets
- Trees and graphs
- Custom containers

### 🌐 [Networking](networking.md)
- Socket programming
- HTTP client/server
- Protocol support
- Network utilities

## 🎯 Quick Reference

### Importing Modules

```flow
// Import entire module
import math;

// Import specific functions
import math { sin, cos, sqrt };

// Import with alias
import graphics as gfx;
```

### Common Patterns

```flow
// Using math functions
let result = math.sqrt(16.0);
let angle = math.sin(math.pi / 2.0);

// Working with arrays
let numbers = [1, 2, 3, 4, 5];
let sorted = arrays::sort(numbers);
let found = arrays::binary_search(sorted, 3);

// File operations
let content = io::read_file("data.txt");
io::write_file("output.txt", content);

// Graphics programming
let window = graphics::create_window(800, 600);
graphics::draw_circle(window, center, radius, color);
```

## 📦 Module Categories

### Core Modules
Essential modules that are always available:
- **core**: Basic types and operations
- **math**: Mathematical functions
- **arrays**: Array utilities

### System Modules
Modules for system-level programming:
- **io**: File and stream I/O
- **memory**: Memory management
- **networking**: Network programming

### Application Modules
Modules for application development:
- **graphics**: Graphics and rendering
- **testing**: Testing framework
- **profiling**: Performance tools

### Advanced Modules
Specialized modules for advanced use cases:
- **concurrency**: Parallel programming
- **collections**: Advanced data structures
- **errors**: Error handling utilities

## 🔍 Module Details

### Core Types Module

```flow
import core;

// Type utilities
let max_value = core::max_int32();
let min_value = core::min_int32();

// Memory operations
let size = core::size_of<i32>();
let aligned = core::align_of<f64>();
```

### Math Module

```flow
import math;

// Basic operations
let result = math::pow(2.0, 8.0);  // 256.0
let absolute = math::abs(-5.5);    // 5.5

// Trigonometry
let sine = math::sin(math::pi / 2.0);
let cosine = math::cos(0.0);

// Random numbers
let random = math::random_int(1, 100);
```

### Arrays Module

```flow
import arrays;

let data = [3, 1, 4, 1, 5, 9];

// Sorting
let sorted = arrays::sort(data);

// Searching
let index = arrays::binary_search(sorted, 4);

// Transformations
let doubled = arrays::map(data, fn(x) { return x * 2; });
let sum = arrays::reduce(data, 0, fn(acc, x) { return acc + x; });
```

### Graphics Module

```flow
import graphics;

// Window management
let window = graphics::create_window(800, 600, "My App");

// Drawing
graphics::clear(window, graphics::color_rgb(255, 255, 255));
graphics::draw_rectangle(window, {x: 10, y: 10}, {width: 100, height: 50}, 
                        graphics::color_rgb(255, 0, 0));

// Display
graphics::present(window);
```

## 📚 Learning Resources

### For Beginners
1. **[Core Types](core.md)** - Start with basic types
2. **[Math Library](math.md)** - Essential mathematical functions
3. **[Array Operations](arrays.md)** - Working with collections

### For Intermediate Users
1. **[File I/O](io.md)** - File system programming
2. **[String Operations](strings.md)** - Text processing
3. **[Testing Framework](testing.md)** - Writing tests

### For Advanced Users
1. **[Graphics Library](graphics.md)** - Graphics programming
2. **[Concurrency](concurrency.md)** - Parallel programming
3. **[Profiling Tools](profiling.md)** - Performance optimization

## 🔧 Development Guidelines

### Module Design Principles

1. **Consistency**: All modules follow consistent naming conventions
2. **Safety**: Functions are designed to be safe and predictable
3. **Performance**: Critical operations are optimized
4. **Documentation**: All public APIs are fully documented

### Best Practices

1. **Import Specific Functions**: Only import what you need
2. **Use Type Annotations**: Be explicit about types when helpful
3. **Handle Errors**: Always handle potential errors
4. **Test Your Code**: Use the testing framework for validation

## 🚀 Examples

### Scientific Computing
```flow
import math;
import arrays;

fn analyze_data(data: [f64; 1000]) -> f64 {
    let mean = arrays::reduce(data, 0.0, fn(acc, x) { return acc + x; }) / 1000.0;
    let variance = arrays::reduce(data, 0.0, fn(acc, x) { 
        return acc + math::pow(x - mean, 2.0); 
    }) / 1000.0;
    return math::sqrt(variance);
}
```

### Graphics Application
```flow
import graphics;
import math;

fn draw_pattern(window) {
    for i in range(0, 10) {
        let angle = (i as f64) * 2.0 * math::pi / 10.0;
        let x = 400.0 + 100.0 * math::cos(angle);
        let y = 300.0 + 100.0 * math::sin(angle);
        graphics::draw_circle(window, {x: x, y: y}, 10.0, 
                            graphics::color_hsv(i * 36, 1.0, 1.0));
    }
}
```

### File Processing
```flow
import io;
import arrays;
import strings;

fn process_file(filename: string) -> i32 {
    let content = io::read_file(filename);
    let lines = strings::split(content, '\n');
    let non_empty = arrays::filter(lines, fn(line) { 
        return strings::length(strings::trim(line)) > 0; 
    });
    return arrays::length(non_empty);
}
```

## 🔗 Related Resources

- **[Language Reference](../language/)** - Core language features
- **[Tutorials](../tutorials/)** - Learning guides
- **[Examples](../examples/)** - Code examples
- **[API Reference](../reference/api.md)** - Complete API documentation

---

*Need help with a specific module? Check the module documentation or visit the [Examples](../examples/) gallery! 🚀*
