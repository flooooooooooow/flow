# Systems Patterns

> Buffers, pools, and systems-style code.


## Part 1: Buffers

### 1.1 Ring buffer push/pop

```flow
struct Ring {
    data: [i32; 8],
    head: i32,
    tail: i32,
    count: i32
}

function ring_push(r: ptr<Ring>, v: i32) -> bool {
    if r[0].count >= 8 {
        return false
    }
    r[0].data[r[0].tail] = v
    r[0].tail = (r[0].tail + 1) % 8
    r[0].count = r[0].count + 1
    return true
}

function ring_pop(r: ptr<Ring>) -> i32 {
    if r[0].count == 0 {
        return -1
    }
    let v: i32 = r[0].data[r[0].head]
    r[0].head = (r[0].head + 1) % 8
    r[0].count = r[0].count - 1
    return v
}

function main() -> i32 {
    let mut r: Ring = Ring { data: [0, 0, 0, 0, 0, 0, 0, 0], head: 0, tail: 0, count: 0 }
    ring_push(&r, 10)
    ring_push(&r, 20)
    printf("%d %d\n", ring_pop(&r), ring_pop(&r))
    return 0
}
```
### 1.2 Slot allocator

```flow
function main() -> i32 {
    let mut used: [i32; 4] = [0, 0, 0, 0]
    let mut i: i32 = 0
    while i < 4 {
        if used[i] == 0 {
            used[i] = 1
            printf("alloc slot %d\n", i)
            break
        }
        i = i + 1
    }
    used[2] = 0
    printf("freed slot 2\n")
    return 0
}
```

## Part 2: Pools

### 2.1 Object pool acquire

```flow
struct Obj { alive: i32, value: i32 }

function acquire(pool: ptr<Obj>, n: i32, v: i32) -> i32 {
    for i in 0 to n {
        if pool[i].alive == 0 {
            pool[i].alive = 1
            pool[i].value = v
            return i
        }
    }
    return -1
}

function main() -> i32 {
    let mut pool: [Obj; 3] = [
        Obj { alive: 0, value: 0 },
        Obj { alive: 0, value: 0 },
        Obj { alive: 0, value: 0 }
    ]
    printf("%d\n", acquire(pool, 3, 42))
    printf("%d\n", acquire(pool, 3, 7))
    return 0
}
```
### 2.2 Release and reuse

```flow
struct Obj { alive: i32, value: i32 }

function main() -> i32 {
    let mut pool: [Obj; 2] = [
        Obj { alive: 1, value: 1 },
        Obj { alive: 1, value: 2 }
    ]
    pool[0].alive = 0
    let mut idx: i32 = -1
    for i in 0 to 2 {
        if pool[i].alive == 0 {
            pool[i].alive = 1
            pool[i].value = 99
            idx = i
            break
        }
    }
    printf("reused %d value=%d\n", idx, pool[idx].value)
    return 0
}
```

## Part 3: Bits

### 3.1 Flags pack

```flow
function main() -> i32 {
    let READ: i32 = 1
    let WRITE: i32 = 2
    let EXEC: i32 = 4
    let mut flags: i32 = READ | WRITE
    printf("write? %d\n", (flags & WRITE) != 0)
    flags = flags | EXEC
    printf("flags=%d\n", flags)
    return 0
}
```
### 3.2 Power-of-two align

```flow
function align_up(x: i32, a: i32) -> i32 {
    return (x + a - 1) & ~(a - 1)
}

function main() -> i32 {
    printf("%d %d\n", align_up(13, 8), align_up(16, 8))
    return 0
}
```

## Part 4: More systems shapes

### 4.1 Popcount (bit count)

```flow
function popcount(x: i32) -> i32 {
    let mut n: i32 = x
    let mut c: i32 = 0
    while n != 0 {
        c = c + (n & 1)
        n = n >> 1
    }
    return c
}

function main() -> i32 {
    printf("%d %d\n", popcount(7), popcount(16))
    return 0
}
```

### 4.2 Freelist head

```flow
function main() -> i32 {
    let mut next: [i32; 4] = [1, 2, 3, -1]
    let mut free_head: i32 = 0
    let taken: i32 = free_head
    free_head = next[taken]
    next[taken] = -2
    printf("took=%d free_head=%d\n", taken, free_head)
    return 0
}
```

### 4.3 Rolling checksum

```flow
function checksum(xs: [i32; 5]) -> i32 {
    let mut s: i32 = 0
    for i in 0 to 5 {
        s = (s * 31 + xs[i]) % 1000
    }
    return s
}

function main() -> i32 {
    let xs: [i32; 5] = [1, 2, 3, 4, 5]
    printf("%d\n", checksum(xs))
    return 0
}
```
