# Python Package Target

Flow can generate Python packages (wheels) as a first-class compilation target.

## Quick Start

```bash
# Generate a Python wheel from a Flow library
./flow python mylib.flow

# Install and use
pip install dist/mylib-0.1.0-*.whl
python -c "import mylib; print(mylib.add(1, 2))"
```

## How It Works

```
Flow Source → Parse → Type Check → C Generator → Python Bindings → Wheel
                                         ↓
                              CPython Extension Module
```

1. Flow compiles to C (via existing C backend)
2. Python bindings are generated automatically
3. A standard CPython extension module is produced
4. Package is built as a pip-installable wheel

## Export Rules

### Automatic Exports

Public symbols with ABI-compatible types are exported automatically:

```flow
# EXPORTED: Public function with compatible types
function add(a: i32, b: i32) -> i32 {
    return a + b
}

# EXPORTED: Public struct with compatible fields
struct Point {
    x: f64,
    y: f64
}

# NOT EXPORTED: Private (starts with underscore)
function _internal_helper() -> void { ... }

# NOT EXPORTED: main() is never exported
function main() -> i32 { return 0 }
```

### ABI-Compatible Types

| Flow Type | Python Type | Notes |
|-----------|-------------|-------|
| `i32`, `i64` | `int` | Full precision |
| `u32`, `u64` | `int` | Unsigned |
| `f32`, `f64` | `float` | IEEE 754 |
| `bool` | `bool` | |
| `string` | `str` | UTF-8 |
| `void` | `None` | Return only |
| `ptr<T>` | `capsule` | Opaque handle |
| Struct types | `dict` | Field access |

### Incompatible Types

Types that cannot cross the Python boundary are excluded with diagnostics:

- Raw pointers without struct context
- Function pointers
- Complex nested generics

## CLI Options

```bash
./flow python <file.flow> [options]

Options:
  --name NAME      Python module name (default: filename)
  --version VER    Package version (default: 0.1.0)
  --source         Generate C extension source only (no wheel)
```

## Output Structure

```
dist/
├── mylib-0.1.0-cp311-cp311-macosx_14_0_arm64.whl
└── mylib_ext.c  (if --source)
```

## Example: Math Library

```flow
# mathlib.flow

function square(x: f64) -> f64 {
    return x * x
}

function factorial(n: i32) -> i32 {
    if n <= 1 {
        return 1
    }
    return n * factorial(n - 1)
}

struct Vec2 {
    x: f64,
    y: f64
}

function vec2_length(v: Vec2) -> f64 {
    return sqrt(v.x * v.x + v.y * v.y)
}
```

Compile and use:

```bash
./flow python mathlib.flow --name mathlib

pip install dist/mathlib-0.1.0-*.whl

python3 << 'EOF'
import mathlib

print(mathlib.square(5.0))      # 25.0
print(mathlib.factorial(5))      # 120
EOF
```

## Export Diagnostics

The compiler shows which symbols are exported/excluded:

```
============================================================
Python Export Analysis: mathlib
============================================================

✅ Exported (3 symbols):
   square: Public function with ABI-compatible signature
   factorial: Public function with ABI-compatible signature
   Vec2: Public struct with ABI-compatible fields

⚠️  Excluded (2 symbols):
   main: Entry point 'main' not exported
   _helper: Private symbol (starts with underscore)
```

## Advanced: Export Overrides

For advanced cases, explicit control is available (future):

```flow
# Rename for Python
@python(name="py_func_name")
function flow_func_name() -> void { ... }

# Add documentation
@python(doc="Computes the square root")
function sqrt(x: f64) -> f64 { ... }

# Force exclude
@python(exclude=true)
function dont_export() -> void { ... }
```

## Design Principles

1. **Python is an output target, not a parent language**
   - No Python semantics leak into Flow
   - All code is compiled, never interpreted

2. **Zero boilerplate for common cases**
   - No explicit export annotations needed
   - Automatic type inference

3. **Deterministic, transparent inference**
   - Same code always produces same exports
   - Clear diagnostics for every decision

4. **Strict semantic separation**
   - Flow owns memory, lifetimes, errors
   - Python sees a clean FFI boundary

## Limitations

- Struct methods not yet supported
- Async effects don't map to Python async
- No NumPy array integration (future)
- macOS/Linux only (Windows future)
