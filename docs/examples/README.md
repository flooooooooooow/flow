# FLOW Examples

Working code demonstrating implemented features.
See [LANGUAGE_SPEC.md](../LANGUAGE_SPEC.md) for what's supported.

## Categories

| Directory | Features Demonstrated |
|-----------|----------------------|
| [basic/](basic/) | Functions, variables, loops, conditionals |
| [algorithms/](algorithms/) | Recursion, iteration, classic algorithms |
| [data-structures/](data-structures/) | Structs, composition, arrays |
| [effects/](effects/) | Effect system, capabilities, handlers |
| [graphics/](graphics/) | PPM output, scene rendering |
| [modules/](modules/) | Import/export, multi-file projects |
| [performance/](performance/) | SIMD hints, parallel loops |
| [gpu/](gpu/) | GPU effects (experimental) |
| [advanced/](advanced/) | Turing machines, JIT patterns |

## Quick Reference

### Minimal Working Example
```flow
function main() -> i32 {
    printf("Hello!\n")
    return 0
}
```

### Effect Example
```flow
effect Log {
    emit(msg: string) -> void,
}

capability Console {
    effect Log,
    function emit(msg: string) -> void {
        printf("%s\n", msg)
    },
}

function main() -> i32 {
    handle Log with Console {
        Log.emit("Working!")
    }
    return 0
}
```

### Run Any Example
```bash
./flow run docs/examples/basic/hello_world.flow
./flow run docs/examples/effects/effects_demo.flow
```

## Testing Examples

All examples should compile and run without errors:

```bash
# Test all examples
for f in docs/examples/**/*.flow; do
    echo "Testing $f"
    ./flow run "$f" || echo "FAILED: $f"
done
```
