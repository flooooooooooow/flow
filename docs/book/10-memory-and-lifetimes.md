# 10. Memory, spans, and lifetime domains

Flow has no garbage collector. Local values normally use stack storage;
long-lived or variable-sized storage is allocated explicitly. Pointers expose
native memory directly, spans describe borrowed regions, arenas amortise
allocation, and lifetime domains check selected escape and call rules.

## 10.1 Value semantics

Primitive values and structs are passed and assigned by value unless a pointer
or span is used:

```text
let p: Point = Point { x: 3, y: 4 }
let q: Point = p
```

Changing a mutable field of `q` does not identify `p` as the same object. A
pointer makes shared identity explicit.

## 10.2 Addresses, pointers, and null

```flow
let mut count: i32 = 0
let address: ptr<i32> = &count

address[0] = 42
let observed: i32 = *address

let absent: ptr<i32> = null
if absent == null {
    println("no value")
}
```

`&x` obtains an address and `*p` dereferences a pointer. Index notation is
convenient for contiguous storage. Postfix chains such as `bodies[i].position.x`
and `ptr[0].field` are supported by the C backend.

Pointer arithmetic is native and unsafe. The compiler cannot prove that an
address is in bounds, aligned, initialised, or still alive.

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

The allocation owner must arrange exactly one `free` after the last use.
`realloc` may move storage; retain the old pointer until the call succeeds.
Clear a mutable pointer to `null` after freeing when later code might inspect
it.

Run the complete memory example:

```bash
./flow run examples/systems/manual_memory.flow
FLOW_HOST=python ./flow run examples/book/09_memory_cleanup.flow
```

## 10.4 Spans

A span packages a pointer and a length without taking ownership:

```flow
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

Arrays and slices borrow into spans at a call site:

```text
let mut signal: array<f32, 256> = [0.0; 256]
let window: span<f32> = signal[64..128]
let value: f32 = total(window)
clear(signal)
```

`span<T, N>` carries a static extent checked at the call site. A span must not
outlive its source storage. It never frees the source.

```bash
FLOW_HOST=python ./flow run examples/basics/spans.flow
```

## 10.5 Arenas

An arena allocates one large region and advances an offset for each request:

```text
let mut arena: Arena = arena_create(1024 * 1024)
defer arena_destroy(&arena)

let points: ptr<Point> = arena_alloc(&arena, 100 * 16)
# construct points
arena_reset(&arena)
```

Individual arena objects are not freed. Resetting invalidates them together.
An arena works well for per-frame scratch data and request-local graphs. The
programmer must still choose its capacity and alignment, decide when to reset
it, and track the lifetime of every returned pointer.

## 10.6 Lifetime domains

Flow defines an ordered set of implemented domains:

```text
callback < frame < session < application
```

`A < B` means that `A` lives no longer than `B`.

```flow
@lifetime(callback)
@rt_safe
function process_block(input: span<f32>) -> void {
    # bounded, nonblocking work
}

@lifetime(application)
let mut cache: ptr<f32> = null
```

The opt-in checker enforces four rules:

1. shorter-lived local storage cannot be assigned into a longer-lived static;
2. a function cannot return a pointer or span into its own domain frame;
3. callback and frame domains impose allocation discipline;
4. a shorter-lived annotated function cannot call a longer-lived annotated
   function.

`callback` also activates the transitive real-time safety restrictions. A
`frame` function may use a frame arena and blocking locks but may not create,
destroy, or grow heap storage.

## 10.7 Boundaries of the lifetime checker

The first implementation does not follow references through arbitrary calls,
struct fields, closure environments, heap cells, pointer/integer casts, or
external functions. It also does not infer the domain of arena allocations or
consult imported annotations across modules. Code that uses these operations
needs manual review.

The precise rules and known gaps are part of the language contract:
[lifetime domains](../language/lifetime-domains.md).

## 10.8 Real-time safety

`@rt_safe` rejects a reachable call that may allocate, perform file or device
I/O, submit GPU work, or take a blocking lock. The intended structure is:

```text
setup: allocate and initialise
  -> callback: bounded work over preallocated memory
  -> teardown: release resources
```

The check only examines the static call graph. It does not prove a worst-case
execution time. Function pointers, some extern calls, and data-dependent work
still require analysis.

## Exercises

1. Allocate and free a typed buffer while making every failure path leak-free.
2. Replace a pointer-plus-length function with `span<T>`.
3. Design an arena reset point for a frame renderer.
4. Give one example for each lifetime-domain error.

Next: [Modules, projects, packages, and interoperation](11-modules-packages-and-interop.md).
