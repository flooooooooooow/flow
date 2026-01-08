# Reference Index

Welcome to the FLOW reference section! This area provides quick reference materials for all language features, APIs, and compiler information.

## 📋 Reference Materials

### 🔤 [Keywords and Operators](keywords.md)
- Language reserved words
- Operator precedence and associativity
- Symbol reference
- Syntax quick reference

### 🏗️ [Language Grammar](grammar.md)
- Formal grammar specification
- BNF notation
- Syntax rules
- Parsing information

### 🔧 [Compiler Directives](directives.md)
- Pragmas and annotations
- Compiler flags
- Build configuration
- Optimization settings

### 📚 [Built-in Functions](builtins.md)
- Core language functions
- Type operations
- Memory functions
- System calls

### 📖 [API Reference](api.md)
- Complete API documentation
- Function signatures
- Type specifications
- Usage examples

### 🚨 [Error Codes](errors.md)
- Compiler error messages
- Runtime error codes
- Debugging information
- Troubleshooting guide

### 📚 [Standard Library Index](stdlib-index.md)
- Quick function lookup
- Module organization
- Function signatures
- Usage patterns

## 🎯 Quick Reference

### Language Keywords
```flow
// Declaration keywords
fn struct let mut import export
// Control flow keywords
if else for while do match return
// Type keywords
i32 i64 f32 f64 bool string
// Effect keywords
effect handle resume
```

### Basic Types
```flow
// Integers
i8  i16  i32  i64
u8  u16  u32  u64

// Floats
f32  f64

// Other
bool  string  void
```

### Operators (by precedence)
```flow
// Highest
.  []  ()          // Field access, indexing, grouping
!  -  +            // Logical not, unary minus/plus
*  /  %            // Multiplication, division, remainder
+  -               // Addition, subtraction
<  <=  >  >=       // Comparisons
==  !=             // Equality
&&                 // Logical and
||                 // Logical or
=  +=  -=  *=  /=  // Assignment
// Lowest
```

### Standard Library Functions
```flow
// Math
abs(x)        sqrt(x)       pow(x, y)
sin(x)        cos(x)        tan(x)
min(x, y)     max(x, y)      random()

// Arrays
len(arr)      sort(arr)      reverse(arr)
find(arr, x)  filter(arr, f) map(arr, f)

// I/O
print(s)      printf(fmt, ...) read_file(path)
write_file(path, content)     open_file(path, mode)
```

## 🔍 Quick Lookup

### Common Patterns

#### Function Definition
```flow
fn function_name(param1: Type1, param2: Type2) -> ReturnType {
    // function body
    return value;
}
```

#### Struct Definition
```flow
struct StructName {
    field1: Type1,
    field2: Type2
}
```

#### Pattern Matching
```flow
match value {
    pattern1 => result1,
    pattern2 => result2,
    _ => default_result
}
```

#### Effect Definition
```flow
effect EffectName {
    fn operation(param: Type) -> ReturnType;
}
```

#### Module Import
```flow
import module_name;
import module_name { function1, function2 };
import module_name as alias;
```

### Type Conversions
```flow
// Explicit casting
let int_value = some_float as i32;
let float_value = some_int as f64;

// Type inference
let value = 42;        // i32
let value = 3.14;      // f64
let value = "hello";   // string
```

### Memory Operations
```flow
// Allocation
let ptr = allocate<Type>(size);

// Deallocation
deallocate(ptr);

// Pointer operations
let value = *ptr;      // Dereference
*ptr = new_value;      // Assign
```

## 📊 Performance Characteristics

### Time Complexity
| Operation | Complexity | Notes |
|-----------|------------|-------|
| Array access | O(1) | Direct indexing |
| Array push | O(1) | Amortized |
| Array insert | O(n) | Requires shifting |
| String concat | O(n) | Creates new string |
| Hash lookup | O(1) | Average case |

### Space Complexity
| Type | Size | Notes |
|------|------|-------|
| i32 | 4 bytes | 32-bit integer |
| i64 | 8 bytes | 64-bit integer |
| f32 | 4 bytes | 32-bit float |
| f64 | 8 bytes | 64-bit float |
| bool | 1 byte | Boolean value |
| string | variable | Length + data |

### Optimization Levels
| Level | Description | Use Case |
|-------|-------------|----------|
| -O0 | No optimization | Debugging |
| -O1 | Basic optimization | Development |
| -O2 | Standard optimization | Production |
| -O3 | Aggressive optimization | Performance critical |
| -Os | Size optimization | Embedded systems |

## 🛠️ Compiler Options

### Basic Options
```bash
flow run program.flow          # Run directly
flow build program.flow        # Build executable
flow test                      # Run tests
flow docs                      # Generate docs
```

### Optimization Flags
```bash
flow build -O3 program.flow   # Maximum optimization
flow build -Os program.flow   # Size optimization
flow build -g program.flow     # Include debug info
```

### Warning Levels
```bash
flow build -Wall program.flow  # All warnings
flow build -Werror program.flow # Warnings as errors
flow build -Wextra program.flow # Extra warnings
```

## 🚨 Common Errors

### Syntax Errors
```
Error: Expected ';' at line 5
Fix: Add semicolon after statement
```

### Type Errors
```
Error: Type mismatch: expected i32, found f64
Fix: Use explicit cast or change variable type
```

### Runtime Errors
```
Error: Index out of bounds
Fix: Check array bounds before access
```

### Link Errors
```
Error: Undefined symbol 'printf'
Fix: Add extern declaration or link library
```

## 🔧 Development Tools

### IDE Support
- **VS Code**: FLOW extension with syntax highlighting
- **Vim**: flow.vim plugin for syntax highlighting
- **Emacs**: flow-mode for editing support

### Build Tools
- **Make**: Traditional build system
- **CMake**: Cross-platform build system
- **Flow Build**: Native FLOW build system

### Debugging
- **GDB**: GNU Debugger integration
- **LLDB**: LLVM Debugger
- **Flow Debug**: Native FLOW debugger

### Profiling
- **perf**: Linux performance profiler
- **Instruments**: macOS profiling tools
- **Flow Profile**: Native FLOW profiler

## 📚 Standards and Specifications

### Language Version
- **Current**: 1.0.0
- **Status**: Stable
- **Compatibility**: Backward compatible within major version

### Standard Library Version
- **Version**: 1.0.0
- **API Stability**: Stable
- **Deprecation**: 6-month notice period

### Compiler Version
- **LLVM**: 15.0+
- **MLIR**: 15.0+
- **Target**: x86_64, ARM64

## 🔗 External Resources

### Documentation
- **[FLOW Website](https://flow-lang.org)** - Official documentation
- **[GitHub Repository](https://github.com/flow-lang/flow)** - Source code
- **[API Docs](api.md)** - Complete API reference

### Community
- **[Discord](https://discord.gg/flow-lang)** - Real-time chat
- **[Reddit](https://reddit.com/r/flow-lang)** - Community discussions
- **[Stack Overflow](https://stackoverflow.com/questions/tagged/flow-lang)** - Q&A

### Tools and Ecosystem
- **[Package Manager](https://packages.flow-lang.org)** - Package repository
- **[Plugin Registry](https://plugins.flow-lang.org)** - IDE plugins
- **[Template Gallery](https://templates.flow-lang.org)** - Project templates

## 📋 Cheat Sheets

### Function Signature Template
```flow
fn name(param1: Type1, param2: Type2) -> ReturnType {
    // Implementation
    return value;
}
```

### Struct Template
```flow
struct Name {
    field1: Type1,
    field2: Type2
}
```

### Effect Template
```flow
effect Name {
    fn operation(param: Type) -> ReturnType;
}
```

### Module Template
```flow
// module_name.flow
export fn function1() -> Type1 {
    // Implementation
}

export fn function2(param: Type) -> Type2 {
    // Implementation
}
```

## 🚀 Quick Start Commands

```bash
# Install FLOW
curl https://flow-lang.org/install | sh

# Create new project
flow new my_project
cd my_project

# Run program
flow run src/main.flow

# Build for production
flow build -O3 src/main.flow

# Run tests
flow test

# Generate documentation
flow docs

# Check code style
flow lint src/

# Format code
flow format src/
```

---

*Need detailed information? Check the specific reference documents or visit the [Language Reference](../language/) section! 🚀*
