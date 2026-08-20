# 10. Memory, spans, and lifetime domains

Flow has no garbage collector. Local values normally use stack storage; long-lived or variable-sized storage is explicit. Every `flow` block in this chapter is compiler-checked in CI.

## 10.1 Value semantics

Struct assignment copies the value unless a pointer or span is used:

```flow
struct MemoryPoint {
    x: i32,
    y: i32
}

function copied_point() -> i32 {
    let p: MemoryPoint = MemoryPoint { x: 3, y: 4 }
    let mut q: MemoryPoint = p
    q.x = 10
    return p.x
}
```

`p` and `q` are independent values. A pointer makes shared identity explicit.

## 10.2 Addresses and pointers

```flow
function pointer_write() -> i32 {
    let mut count: i32 = 0
    let address: ptr<i32> = &count
    address[0] = 42
    return *address
}
```

`&x` obtains an address, `*p` dereferences it, and indexing is available for contiguous storage. Pointer arithmetic is native and unsafe: the compiler cannot generally prove bounds, alignment, initialization, or liveness.

## 10.3 Heap allocation

```flow
extern {
    function calloc(count: i64, size: i64) -> ptr<void>
    function free(p: ptr<void>) -> void
}

function main() -> i32 {
    let data: ptr<i32> = calloc(4, 4)
    if data == null { return 1 }
    defer free(data)

    for i in 0 to 4 {
        data[i] = (i + 1) * 10
    }
    return data[3] - 40
}
```

The allocation owner arranges exactly one release after the final use. A `defer` is useful for structured cleanup.

```bash
FLOW_HOST=python ./flow run examples/systems/manual_memory.flow
```

## 10.4 Spans

A span packages a pointer and length without taking ownership:

```flow id=span-ops
function total(samples: span<f32>) -> f32 {
    let mut sum: f32 = 0.0
    for i in 0 to samples.len {
        sum = sum + samples[i]
    }
    return sum
}

function clear(samples: span<mut f32>) -> void {
    for i in 0 to samples.len {
        samples[i] = 0.0
    }
}
```

Arrays and slices borrow into spans:

```flow uses=span-ops
function span_window_total() -> f32 {
    let mut signal: array<f32, 8> = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]
    let window: span<f32> = signal[2..6]
    let value: f32 = total(window)
    clear(signal)
    return value
}
```

`span<T, N>` adds a compile-time extent. A span never frees its source and may not outlive it.

## 10.5 Arenas

Flow's memory standard library includes `Arena` and frame-arena helpers. Because the API depends on imported declarations, the canonical runnable sources are [`lib/stdlib/memory.flow`](../../lib/stdlib/memory.flow) and [`examples/audio/lifetime_domains.flow`](../../examples/audio/lifetime_domains.flow), rather than isolated pseudo-calls copied without their import context.

An arena owns one region and advances an offset for each allocation; resetting invalidates its contained transient objects together.

## 10.6 Lifetime domains

The implemented order is `callback < frame < session < application`.

```flow
@lifetime(callback)
function process_value(value: i32) -> i32 {
    return value + 1
}

@lifetime(application)
let mut cache: ptr<i32> = null
```

The checker rejects direct shorter-lived escapes into longer-lived statics, returns of references into a function's own frame, forbidden allocation in short domains, and calls from a shorter-lived annotated domain into a longer-lived one.

Intentional violations are compiler-tested on the focused [lifetime domains](../language/lifetime-domains.md) page.

## 10.7 Real-time safety

`@rt_safe` constrains the reachable static call graph. It rejects known heap allocation, blocking locks, file/device I/O, and GPU submission on the RT path.

```flow
@rt_safe
function process_sample(sample: f32, gain: f32) -> f32 {
    return sample * gain
}
```

The analysis does not prove a worst-case execution time and cannot fully reason about arbitrary function pointers or external implementations.

## 10.8 Known limits

The current lifetime analysis does not soundly follow references through arbitrary calls, struct fields, closure environments, heap cells, pointer/integer laundering, or imported domain metadata. Those limits are explicit parts of the contract rather than implied guarantees.

## Exercises

Allocate and release a typed buffer without leaks; replace pointer-plus-length APIs with spans; choose an arena reset point for a renderer; and construct one checked negative example for each lifetime-domain rule.

Next: [Modules, projects, packages, and interoperation](11-modules-packages-and-interop.md).
