# FLOW Standard Library

Location: `lib/stdlib/`

## Available Modules

| Module | Import | Status |
|--------|--------|--------|
| [math.flow](../../lib/stdlib/math.flow) | `import "lib/stdlib/math.flow"` | ✅ |
| [io.flow](../../lib/stdlib/io.flow) | `import "lib/stdlib/io.flow"` | ⚠️ |
| [array.flow](../../lib/stdlib/array.flow) | `import "lib/stdlib/array.flow"` | ⚠️ |
| [memory.flow](../../lib/stdlib/memory.flow) | `import "lib/stdlib/memory.flow"` | ⚠️ |
| [time.flow](../../lib/stdlib/time.flow) | `import "lib/stdlib/time.flow"` | ⚠️ |
| [srir.flow](../../lib/stdlib/srir.flow) | `import "lib/stdlib/srir.flow"` | ⚠️ |
| [autodiff.flow](../../lib/stdlib/autodiff.flow) | `import "lib/stdlib/autodiff.flow"` | ✅ |
| [autodiff_reverse.flow](../../lib/stdlib/autodiff_reverse.flow) | `import "lib/stdlib/autodiff_reverse.flow"` | ✅ |
| [nn.flow](../../lib/stdlib/nn.flow) | `import "lib/stdlib/nn.flow"` | ✅ |

## Usage

```flow
import "lib/stdlib/math.flow"

function main() -> i32 {
    let x: f32 = sqrt(2.0)
    printf("sqrt(2) = %f\n", x)
    return 0
}
```

## Built-in Functions

These are available without imports (via C backend):

| Function | Signature | Notes |
|----------|-----------|-------|
| `printf` | `(fmt: string, ...) -> i32` | C printf |
| `sqrt` | `(x: f32) -> f32` | math.h |
| `sin` | `(x: f32) -> f32` | math.h |
| `cos` | `(x: f32) -> f32` | math.h |
| `abs` | `(x: i32) -> i32` | stdlib.h |

See [LANGUAGE_SPEC.md](../LANGUAGE_SPEC.md) §4.3 for complete built-in list.

## Autodiff and Neural Nets

- **Autodiff overview**: [autodiff.md](autodiff.md)
- **XOR training example using stdlib NN**: `examples/nn_xor.flow`
