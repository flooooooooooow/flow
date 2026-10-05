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

1. `flow python` runs the Flow tool `tools/pywheel`. It parses the program and
   its imports with the flowc front end and decides what to export.
2. flowc compiles the program to C (`./flow tool compiler/scripts/flowc_emit.flow --strict`).
   A type error stops here.
3. The tool writes a CPython extension source around that C, plus
   `setup.py` and `pyproject.toml`.
4. `python3 -m pip wheel` builds the wheel into `dist/`. This is the only
   step that runs Python, because building a wheel needs setuptools. Set
   `FLOW_PYTHON` to use another interpreter. `--source` skips it and runs no
   Python at all.

## Export Rules

### Automatic Exports

Public symbols with ABI-compatible types are exported automatically:

```flow-pseudocode
# EXPORTED: Public function with compatible types
function add(a: i32, b: i32) -> i32 {
    return a + b
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

Type aliases resolve to their base type for this check.

### Incompatible Types

Types that cannot cross the Python boundary are excluded with diagnostics:

- Pointers, arrays, spans and function types
- Enums and generic types
- Structs. A public struct with fields stops generation with exit status 1,
  naming the struct. Private structs (leading underscore) and empty structs
  do not.

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

✅ Exported (2 symbols):
   square: Public function with ABI-compatible signature
   factorial: Public function with ABI-compatible signature

⚠️  Excluded (2 symbols):
   main: Entry point 'main' not exported
   _helper: Private symbol (starts with underscore)
```

## Advanced: Export Overrides

For advanced cases, explicit control is available:

```flow
# Rename for Python
@python(name="py_func_name")
function flow_func_name() -> void { }

# Add documentation
@python(doc="Computes the square root")
function sqrt(x: f64) -> f64 { return x }

# Force exclude
@python(exclude=true)
function dont_export() -> void { }
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

- Structs, pointers and arrays do not cross the boundary yet
- Async effects don't map to Python async
- No NumPy array integration in `flow python`. Zero-copy arrays use the
  [C buffer ABI](language/ffi-buffer.md) through ctypes / PEP 3118; see
  the [boundary audit](language/ffi-boundary-audit.md)
- macOS/Linux only (Windows future)
