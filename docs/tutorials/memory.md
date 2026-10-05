# Manual Memory
> Flow has **no GC**. Allocate with `malloc`/`alloc_*`, free what you own, or use an arena.
> Run native demos with `./flow run` — browser lessons simulate output.

## Part 1: Heap basics
### 1.1 Hello heap

```flow
extern {
    function malloc(size: i64) -> ptr<void>
    function free(p: ptr<void>) -> void
}

function main() -> i32 {
    let p: ptr<void> = malloc(64)
    if p == null {
        printf("out of memory\n")
        return 1
    }
    printf("allocated 64 bytes\n")
    free(p)
    printf("freed\n")
    return 0
}
```
### 1.2 Typed i32 buffer

```flow
extern {
    function calloc(n: i64, size: i64) -> ptr<void>
    function free(p: ptr<void>) -> void
}

function main() -> i32 {
    let nums: ptr<i32> = calloc(4, 4)
    if nums == null {
        printf("fail\n")
        return 1
    }
    nums[0] = 10
    nums[1] = 20
    nums[2] = 30
    nums[3] = 40
    printf("%d %d %d %d\n", nums[0], nums[1], nums[2], nums[3])
    free(nums)
    return 0
}
```
### 1.3 Grow with realloc

```flow
extern {
    function malloc(size: i64) -> ptr<void>
    function realloc(p: ptr<void>, size: i64) -> ptr<void>
    function free(p: ptr<void>) -> void
}

function main() -> i32 {
    let mut p: ptr<i32> = malloc(2 * 4)
    p[0] = 1
    p[1] = 2
    let grown: ptr<void> = realloc(p, 4 * 4)
    if grown == null {
        free(p)
        printf("realloc failed\n")
        return 1
    }
    p = grown
    p[2] = 3
    p[3] = 4
    printf("%d %d %d %d\n", p[0], p[1], p[2], p[3])
    free(p)
    return 0
}
```
### 1.4 Null check discipline

```flow
extern {
    function malloc(size: i64) -> ptr<void>
    function free(p: ptr<void>) -> void
}

function main() -> i32 {
    let p: ptr<void> = malloc(0)
    if p == null {
        printf("null (or implementation-defined empty alloc)\n")
    } else {
        printf("non-null empty-ish alloc\n")
        free(p)
    }
    printf("always check before use\n")
    return 0
}
```

## Part 2: Patterns
### 2.1 Fill and sum

```flow
extern {
    function calloc(n: i64, size: i64) -> ptr<void>
    function free(p: ptr<void>) -> void
}

function sum(p: ptr<i32>, n: i32) -> i32 {
    let mut t: i32 = 0
    for i in 0 to n {
        t = t + p[i]
    }
    return t
}

function main() -> i32 {
    let n: i32 = 8
    let p: ptr<i32> = calloc(n, 4)
    for i in 0 to n {
        p[i] = i + 1
    }
    printf("sum 1..8 = %d\n", sum(p, n))
    free(p)
    return 0
}
```
### 2.2 Copy buffer

```flow
extern {
    function calloc(n: i64, size: i64) -> ptr<void>
    function free(p: ptr<void>) -> void
}

function copy_i32(dst: ptr<i32>, src: ptr<i32>, n: i32) -> void {
    for i in 0 to n {
        dst[i] = src[i]
    }
}

function main() -> i32 {
    let a: ptr<i32> = calloc(3, 4)
    let b: ptr<i32> = calloc(3, 4)
    a[0] = 7
    a[1] = 8
    a[2] = 9
    copy_i32(b, a, 3)
    printf("b = %d %d %d\n", b[0], b[1], b[2])
    free(a)
    free(b)
    return 0
}
```
### 2.3 Struct on the heap

```flow
extern {
    function malloc(size: i64) -> ptr<void>
    function free(p: ptr<void>) -> void
}

struct Point {
    x: i32,
    y: i32
}

function main() -> i32 {
    let raw: ptr<void> = malloc(8)
    let p: ptr<Point> = raw
    p[0].x = 3
    p[0].y = 4
    printf("Point(%d, %d)\n", p[0].x, p[0].y)
    free(raw)
    return 0
}
```

## Part 3: Arenas
### 3.1 Arena create / destroy

```flow
extern {
    function malloc(size: i64) -> ptr<void>
    function free(p: ptr<void>) -> void
}

struct Arena {
    buffer: ptr<i8>,
    capacity: i64,
    offset: i64
}

function main() -> i32 {
    let raw: ptr<void> = malloc(256)
    let mut a: Arena = Arena { buffer: raw, capacity: 256, offset: 0 }
    printf("arena capacity=%d used=%d\n", a.capacity, a.offset)
    free(a.buffer)
    printf("destroyed\n")
    return 0
}
```
### 3.2 Bump allocate ints

```flow
extern {
    function malloc(size: i64) -> ptr<void>
    function free(p: ptr<void>) -> void
}

struct Arena {
    buffer: ptr<i8>,
    capacity: i64,
    offset: i64
}

function arena_alloc_i32(arena: ptr<Arena>, count: i64) -> ptr<i32> {
    let need: i64 = count * 4
    let a: Arena = arena[0]
    if a.offset + need > a.capacity {
        return null
    }
    let out: ptr<i32> = a.buffer + a.offset
    arena[0].offset = a.offset + need
    return out
}

function main() -> i32 {
    let raw: ptr<void> = malloc(128)
    let mut a: Arena = Arena { buffer: raw, capacity: 128, offset: 0 }
    let xs: ptr<i32> = arena_alloc_i32(&a, 4)
    xs[0] = 1
    xs[1] = 2
    xs[2] = 3
    xs[3] = 4
    printf("%d %d %d %d used=%d\n", xs[0], xs[1], xs[2], xs[3], a.offset)
    free(a.buffer)
    return 0
}
```
### 3.3 Reset and reuse

```flow
extern {
    function malloc(size: i64) -> ptr<void>
    function free(p: ptr<void>) -> void
}

struct Arena {
    buffer: ptr<i8>,
    capacity: i64,
    offset: i64
}

function main() -> i32 {
    let raw: ptr<void> = malloc(64)
    let mut a: Arena = Arena { buffer: raw, capacity: 64, offset: 24 }
    printf("before reset used=%d\n", a.offset)
    a.offset = 0
    printf("after reset used=%d\n", a.offset)
    free(a.buffer)
    return 0
}
```

## Part 4: Safety drills
### 4.1 Never double-free

```flow
extern {
    function malloc(size: i64) -> ptr<void>
    function free(p: ptr<void>) -> void
}

function main() -> i32 {
    let p: ptr<void> = malloc(32)
    free(p)
    # free(p) again would be undefined — don't
    printf("freed once\n")
    return 0
}
```
### 4.2 Set pointer null after free

```flow
extern {
    function malloc(size: i64) -> ptr<void>
    function free(p: ptr<void>) -> void
}

function main() -> i32 {
    let mut p: ptr<void> = malloc(16)
    free(p)
    p = null
    if p == null {
        printf("safe: pointer cleared\n")
    }
    return 0
}
```
### 4.3 Ownership transfer

```flow
extern {
    function calloc(n: i64, size: i64) -> ptr<void>
    function free(p: ptr<void>) -> void
}

function take_and_free(p: ptr<i32>) -> void {
    printf("took ownership of %d\n", p[0])
    free(p)
}

function main() -> i32 {
    let p: ptr<i32> = calloc(1, 4)
    p[0] = 99
    take_and_free(p)
    # p is dangling — do not use
    printf("caller must not free again\n")
    return 0
}
```

## Part 5: Advanced patterns

### 5.1 Dangling pointer awareness

After `free`, the pointer still holds an address — but that memory is no longer yours.
This lesson never *uses* a dangling pointer; it only teaches the discipline of clearing it.

```flow
extern {
    function malloc(size: i64) -> ptr<void>
    function free(p: ptr<void>) -> void
}

function main() -> i32 {
    let mut p: ptr<i32> = malloc(4)
    if p == null {
        printf("alloc failed\n")
        return 1
    }
    p[0] = 42
    printf("live value=%d\n", p[0])

    free(p)
    # At this point p is dangling — reading p[0] would be undefined.
    # Educational rule: null it out so later checks fail safely.
    p = null

    if p == null {
        printf("dangling avoided: pointer cleared after free\n")
    }
    printf("never use a pointer after free\n")
    return 0
}
```

### 5.2 Growable buffer pattern

Track `len` and `cap`, grow with `realloc` when full — the classic dynamic array shape.

```flow
extern {
    function malloc(size: i64) -> ptr<void>
    function realloc(p: ptr<void>, size: i64) -> ptr<void>
    function free(p: ptr<void>) -> void
}

struct GrowBuf {
    data: ptr<i32>,
    len: i32,
    cap: i32
}

function growbuf_push(b: ptr<GrowBuf>, v: i32) -> i32 {
    if b[0].len >= b[0].cap {
        let new_cap: i32 = b[0].cap * 2
        let grown: ptr<void> = realloc(b[0].data, new_cap * 4)
        if grown == null {
            return 0
        }
        b[0].data = grown
        b[0].cap = new_cap
        printf("grew to cap=%d\n", new_cap)
    }
    b[0].data[b[0].len] = v
    b[0].len = b[0].len + 1
    return 1
}

function main() -> i32 {
    let mut b: GrowBuf = GrowBuf {
        data: malloc(2 * 4),
        len: 0,
        cap: 2
    }
    if b.data == null {
        printf("alloc failed\n")
        return 1
    }

    growbuf_push(&b, 10)
    growbuf_push(&b, 20)
    growbuf_push(&b, 30)
    growbuf_push(&b, 40)

    printf("len=%d values=", b.len)
    for i in 0 to b.len {
        printf("%d ", b.data[i])
    }
    printf("\n")
    free(b.data)
    return 0
}
```

### 5.3 Arena frame pattern

Bump-allocate during a "frame", then reset the offset so the slab is reused.
Pointers from a previous frame must not be used after reset.

```flow
extern {
    function malloc(size: i64) -> ptr<void>
    function free(p: ptr<void>) -> void
}

struct Arena {
    buffer: ptr<i8>,
    capacity: i64,
    offset: i64
}

function arena_alloc_i32(arena: ptr<Arena>, count: i64) -> ptr<i32> {
    let need: i64 = count * 4
    let a: Arena = arena[0]
    if a.offset + need > a.capacity {
        return null
    }
    let out: ptr<i32> = a.buffer + a.offset
    arena[0].offset = a.offset + need
    return out
}

function arena_reset(arena: ptr<Arena>) -> void {
    arena[0].offset = 0
}

function main() -> i32 {
    let raw: ptr<void> = malloc(256)
    let mut arena: Arena = Arena { buffer: raw, capacity: 256, offset: 0 }

    for frame in 0 to 3 {
        let xs: ptr<i32> = arena_alloc_i32(&arena, 4)
        if xs == null {
            printf("frame %d: OOM\n", frame)
            free(arena.buffer)
            return 1
        }
        xs[0] = frame
        xs[1] = frame + 10
        xs[2] = frame + 20
        xs[3] = frame + 30
        printf("frame %d: %d %d %d %d used=%d\n",
            frame, xs[0], xs[1], xs[2], xs[3], arena.offset)

        # End of frame: reclaim the whole slab for the next frame.
        # Do not keep or use `xs` after this reset.
        arena_reset(&arena)
        printf("frame %d: reset used=%d\n", frame, arena.offset)
    }

    free(arena.buffer)
    printf("arena frame pattern ok\n")
    return 0
}
```

### 5.4 Temp scratch then keep result

Allocate scratch in an arena, copy the final answer out, then reset — keep only what you own.

```flow
extern {
    function malloc(size: i64) -> ptr<void>
    function free(p: ptr<void>) -> void
}

struct Arena {
    buffer: ptr<i8>,
    capacity: i64,
    offset: i64
}

function arena_alloc_i32(arena: ptr<Arena>, count: i64) -> ptr<i32> {
    let need: i64 = count * 4
    let a: Arena = arena[0]
    if a.offset + need > a.capacity {
        return null
    }
    let out: ptr<i32> = a.buffer + a.offset
    arena[0].offset = a.offset + need
    return out
}

function main() -> i32 {
    let raw: ptr<void> = malloc(128)
    let mut arena: Arena = Arena { buffer: raw, capacity: 128, offset: 0 }

    let scratch: ptr<i32> = arena_alloc_i32(&arena, 5)
    for i in 0 to 5 {
        scratch[i] = (i + 1) * (i + 1)
    }
    let mut sum: i32 = 0
    for i in 0 to 5 {
        sum = sum + scratch[i]
    }

    # Keep only the result on the stack / heap you own; drop scratch via reset.
    arena.offset = 0
    printf("scratch sum=%d arena reused used=%d\n", sum, arena.offset)
    free(arena.buffer)
    return 0
}
```
