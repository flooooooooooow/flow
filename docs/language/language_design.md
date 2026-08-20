# Flow Language Design

This page describes the design that the current compiler implements. Older sketches of pointer syntax such as `[*i32]`, `[T; N]` arrays, `0..n` loops, `generic fn`, CLOS-style `method` declarations, inline LLVM blocks, and `vec4f32` types predated the present language and are not current Flow syntax.

For proposed future syntax, use the [north-star design](../vision/north-star.md) and [roadmap](../../ROADMAP.md). Proposed code there is explicitly labelled `flow-future` rather than being presented as runnable Flow.

## Design goals

Flow is built around a small statically typed systems core plus high-level constructs that lower predictably. The main goals are readable source, aggressive ahead-of-time compilation, explicit effects, direct C/MLIR backends, deterministic low-level behavior where required, and first-class descriptions of evolving systems.

## Current core syntax

```flow
struct Point {
    x: f32,
    y: f32
}

function squared_length(point: Point) -> f32 {
    return point.x * point.x + point.y * point.y
}

function main() -> i32 {
    let point: Point = Point { x: 3.0, y: 4.0 }
    if squared_length(point) == 25.0 {
        return 0
    }
    return 1
}
```

The current spellings include `ptr<T>` for pointers, `array<T, N>` for fixed arrays, `span<T>` for borrowed views, `for i in a to b` for ranges, and `@attribute` for compiler attributes.

## Effects and capabilities

Effects are part of function types rather than hidden runtime behavior.

```flow
effect Log {
    write(value: i32) -> void
}

function record(value: i32) -> void with Log {
    Log.write(value)
}
```

Capabilities provide implementations for effects. See [Effects and capabilities](../effects-showcase.md) for the complete executable examples.

## Evolution as a language construct

The current compiler supports `flow` declarations with state and differential evolution:

```flow
flow Decay {
    state value : f64 = 1.0
    param rate  : f64 = 0.5

    value evolves as -rate * value
}
```

The compiler lowers the model to explicit state plus generated stepping functions. The language is growing from this shipped core toward the broader temporal-system design in [north-star.md](../vision/north-star.md).

## Backends

Flow has C and MLIR compilation paths. Backend-specific facilities are documented separately rather than embedded as invented surface syntax:

[C backend and ABI](export-abi.md), [MLIR](modules-namespacing.md), [GPU and shaders](graphics.md), [Wasm](wasm.md), and [BPF](bpf.md).

## Memory model

Ownership-sensitive APIs use explicit pointers, spans, arenas, and lifetime domains. Flow does not use the early design's `[*T]`, `[&T]`, `allocate_stack()`, or `memory_region` pseudo-types as language syntax. See [Spans](spans.md), [Lifetime domains](lifetime-domains.md), and [Memory](../library/memory.md).

## Parallelism and optimization

Parallelism, SIMD, target attributes, and backend optimization are exposed only where the compiler has a concrete implementation. The authoritative surface is the [language specification](../LANGUAGE_SPEC.md) and compiler-tested examples; speculative syntax belongs in `flow-future` fences.

## Extensible dispatch

An old design section proposed CLOS-style `generic fn`, `method`, `before`, `after`, and runtime multiple dispatch. Those forms are not part of current Flow. Existing polymorphism uses generics, traits, modules, effects, and capability dispatch. If multiple dispatch is revisited, it will be specified in the roadmap before appearing in language-reference code.

## Source of truth

The order of authority is the compiler and tests first, the [language specification](../LANGUAGE_SPEC.md) second, and focused reference pages under `docs/language/` third. CI compiles every block labelled `flow`; future and schematic syntax must identify itself explicitly.