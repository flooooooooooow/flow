# Flow Tutorial: Advanced

This tutorial covers effects, autodiff, GPU kernels, backends, native interop, and testing using the current compiler surface. Every `flow` block is compiler-checked in CI.

## Algebraic effects

An effect declares operations; a capability implements them; a handler installs the capability for a dynamic scope.

```flow
effect TutorialLog {
    write(message: string) -> void,
}

capability TutorialConsole {
    effect TutorialLog,
    function write(message: string) -> void {
        println(message)
    },
}

function greet(name: string) -> void with TutorialLog {
    TutorialLog.write(name)
}

function effect_demo() -> i32 {
    handle TutorialLog with TutorialConsole {
        greet("Flow")
    }
    return 0
}
```

For nested replacement, multiple handlers, and strict effect rows, use [`examples/effects/showcase.flow`](../../examples/effects/showcase.flow) and [Effects & capabilities](../effects-showcase.md).

## Automatic differentiation

Autodiff types and functions live in imported modules, so the complete executable examples are the best reference:

```bash
FLOW_HOST=python ./flow run examples/ml/autodiff/dual_ops.flow
FLOW_HOST=python ./flow run examples/ml/autodiff/autodiff_benchmark.flow
FLOW_HOST=python ./flow run examples/ml/tape_mul.flow
```

Forward mode carries primal and tangent values. Reverse mode records a tape and propagates adjoints. Check gradients against finite differences or an analytic derivative before relying on them.

## GPU kernels

The current Metal-oriented kernel surface uses explicit pointers and `gpu_thread_id()`:

```flow
@gpu
function vector_add(a: ptr<f32>, b: ptr<f32>, out: ptr<f32>, n: i32) -> void {
    let i: i32 = gpu_thread_id()
    if i < n {
        out[i] = a[i] + b[i]
    }
}
```

Generate device code with:

```bash
./flow gpu my_kernels.flow
```

For allocation/transfer/synchronization use [GPU memory](../library/gpu-memory.md). The portable host language does not use the old `vec4<f32>` / `<...>` tutorial syntax; backend vectorization is documented separately from the source-level baseline.

## Compilation backends

```bash
./flow run program.flow
./flow compile program.flow
./flow mlir program.flow
./flow mlir-run program.flow
./flow jit program.flow
./flow wasm program.flow
```

C is the primary portable native path. MLIR supports a substantial but not identical subset. Wasm is produced through the documented C/MLIR-to-Emscripten paths. `flow explain` is useful when a high-level operation has multiple lowering plans.

## POSIX and native APIs

Native modules must be imported in complete programs so types, constants, and link requirements are visible. The repository's POSIX examples are the executable reference:

```bash
FLOW_HOST=python ./flow run examples/systems/posix_file_io.flow
FLOW_HOST=python ./flow run examples/systems/process_info.flow
```

When wrapping C directly, keep the extern surface small and verify ABI types, ownership, lifetime, and link flags.

## Memory and spans

Use `ptr<T>` for explicit pointer APIs, `array<T, N>` for fixed owned arrays, and `span<T>` / `span<mut T>` for borrowed contiguous views. See [Spans](../language/spans.md), [Memory](../library/memory.md), and [Lifetime domains](../language/lifetime-domains.md).

## Tests

A language test may use a `test` declaration:

```flow
function fibonacci(n: i32) -> i32 {
    if n < 2 {
        return n
    }
    return fibonacci(n - 1) + fibonacci(n - 2)
}

test "addition works" {
    let result: i32 = 2 + 2
    if result != 4 {
        return false
    }
    return true
}

test "fibonacci is correct" {
    if fibonacci(10) != 55 {
        return false
    }
    return true
}
```

Run tests with:

```bash
./flow test
./flow test tests/my_test.flow
./flow test-strict
```

For deployment-oriented checks, add sanitizers, safety profiles, generated-C inspection, and target-specific measurements rather than treating a successful compile as sufficient evidence.

## Next references

See the [Language specification](../LANGUAGE_SPEC.md), [Effects showcase](../effects-showcase.md), [ML tutorial](ml-on-macbook.md), [GPU memory](../library/gpu-memory.md), and [Engineering & verification](../book/17-engineering-and-verification.md).
