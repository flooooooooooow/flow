# FLOW Tutorial: Intermediate

Build on the basics with generics, traits, error handling, and more. Programs with `main` **run in the browser** — use **Run** on each example or the [interactive app](index.html).

## Part 1: Generics

### 1.1 Generic Functions

```flow
# A function that works with any type
function identity<T>(x: T) -> T {
    return x
}

function swap<T>(a: T, b: T) -> T {
    # Returns b (just demonstrating generic usage)
    return b
}

function main() -> i32 {
    let x = identity<i32>(42)
    let y = identity<f64>(3.14)
    let z = identity<string>("hello")
    
    printf("x = %d, y = %f\n", x, y)
    return 0
}
```

### 1.2 Generic Structs

```flow
struct Box<T> {
    value: T
}

struct Pair<A, B> {
    first: A,
    second: B
}

function main() -> i32 {
    let int_box = Box<i32> { value: 42 }
    let float_box = Box<f64> { value: 3.14 }
    
    let pair = Pair<string, i32> {
        first: "Alice",
        second: 30
    }
    
    printf("Box: %d\n", int_box.value)
    printf("Pair: %s is %d\n", pair.first, pair.second)
    
    return 0
}
```

### 1.3 How Generics Work: Monomorphization

FLOW uses **monomorphization** — it generates specialized versions of generic code for each concrete type used.

```flow
function identity_i32(x: i32) -> i32 { return x }
function identity_f64(x: f64) -> f64 { return x }

function main() -> i32 {
    # Same idea as identity<T>, specialized per type:
    let a: i32 = identity_i32(1)
    let b: f64 = identity_f64(2.0)
    printf("mono i32=%d f64=%f\n", a, b)
    return 0
}
```

### 1.4 Pair map helper

```flow
struct Pair {
    a: i32,
    b: i32
}

function pair_sum(p: Pair) -> i32 {
    return p.a + p.b
}

function main() -> i32 {
    let p: Pair = Pair { a: 7, b: 5 }
    printf("sum=%d\n", pair_sum(p))
    return 0
}
```

---

## Part 2: Traits (method-shaped)

### 2.1 Display-shaped show

Browser-friendly stand-in for trait methods: a naming convention plus a call.

```flow
struct Point {
    x: i32,
    y: i32
}

function Point_show(p: Point) -> void {
    printf("Point(%d, %d)", p.x, p.y)
}

function main() -> i32 {
    let p: Point = Point { x: 3, y: 4 }
    Point_show(p)
    printf("\n")
    return 0
}
```

### 2.2 Comparable-shaped order

```flow
struct Point {
    x: i32,
    y: i32
}

function Point_compare(a: Point, b: Point) -> i32 {
    if a.x < b.x {
        return -1
    }
    if a.x > b.x {
        return 1
    }
    if a.y < b.y {
        return -1
    }
    if a.y > b.y {
        return 1
    }
    return 0
}

function main() -> i32 {
    let a: Point = Point { x: 1, y: 2 }
    let b: Point = Point { x: 1, y: 9 }
    printf("cmp=%d\n", Point_compare(a, b))
    return 0
}
```

### 2.3 Print any Display-shaped value

```flow
struct Person {
    age: i32
}

function Person_show(p: Person) -> void {
    printf("age=%d", p.age)
}

function print_person(p: Person) -> void {
    Person_show(p)
    printf("\n")
}

function main() -> i32 {
    print_person(Person { age: 30 })
    return 0
}
```

---

## Part 3: Enums (tag + payload)

### 3.1 Color tags

```flow
# 0=Red 1=Green 2=Blue
function color_name(c: i32) -> void {
    if c == 0 {
        printf("red\n")
    } elif c == 1 {
        printf("green\n")
    } else {
        printf("blue\n")
    }
}

function main() -> i32 {
    color_name(1)
    return 0
}
```

### 3.2 Shape area by tag

```flow
# tag: 0=circle(r) 1=rect(w,h) 2=tri(b,h) — payloads in a/b
function area(tag: i32, a: f32, b: f32) -> f32 {
    if tag == 0 {
        return 3.14159 * a * a
    } elif tag == 1 {
        return a * b
    }
    return 0.5 * a * b
}

function main() -> i32 {
    printf("circle=%f\n", area(0, 2.0, 0.0))
    printf("rect=%f\n", area(1, 3.0, 4.0))
    printf("tri=%f\n", area(2, 6.0, 4.0))
    return 0
}
```

### 3.3 Option-shaped find

```flow
function find_index(arr: ptr<i32>, n: i32, target: i32) -> i32 {
    for i in 0 to n {
        if arr[i] == target {
            return i
        }
    }
    return -1
}

function main() -> i32 {
    let arr: [i32; 5] = [10, 20, 30, 40, 50]
    let result: i32 = find_index(arr, 5, 30)
    if result >= 0 {
        printf("Found at index %d\n", result)
    } else {
        printf("Not found\n")
    }
    return 0
}
```

### 3.4 Result-shaped parse

```flow
function parse_positive(n: i32) -> i32 {
    if n <= 0 {
        return -1
    }
    return n
}

function main() -> i32 {
    let r1: i32 = parse_positive(42)
    if r1 >= 0 {
        printf("Parsed: %d\n", r1)
    }
    let r2: i32 = parse_positive(-5)
    if r2 < 0 {
        printf("Error: not positive\n")
    }
    return 0
}
```

---

## Part 4: Higher-order style

### 4.1 Apply a named function twice

```flow
function apply_twice(x: i32) -> i32 {
    let once: i32 = x * 2
    return once * 2
}

function main() -> i32 {
    printf("double(double(5)) = %d\n", apply_twice(5))
    return 0
}
```

### 4.2 Map over a fixed array

```flow
function main() -> i32 {
    let mut xs: [i32; 4] = [1, 2, 3, 4]
    for i in 0 to 4 {
        xs[i] = xs[i] * xs[i]
    }
    for i in 0 to 4 {
        printf("%d ", xs[i])
    }
    printf("\n")
    return 0
}
```

### 4.3 Fold / reduce sum

```flow
function fold_sum(xs: ptr<i32>, n: i32) -> i32 {
    let mut t: i32 = 0
    for i in 0 to n {
        t = t + xs[i]
    }
    return t
}

function main() -> i32 {
    let xs: [i32; 5] = [1, 2, 3, 4, 5]
    printf("sum=%d\n", fold_sum(xs, 5))
    return 0
}
```

---

## Part 5: Collection shapes (arrays)

### 5.1 Stack push/pop

```flow
struct Stack {
    data: [i32; 8],
    top: i32
}

function stack_push(s: ptr<Stack>, v: i32) -> void {
    s[0].data[s[0].top] = v
    s[0].top = s[0].top + 1
}

function stack_pop(s: ptr<Stack>) -> i32 {
    s[0].top = s[0].top - 1
    return s[0].data[s[0].top]
}

function main() -> i32 {
    let mut s: Stack = Stack {
        data: [0, 0, 0, 0, 0, 0, 0, 0],
        top: 0
    }
    stack_push(&s, 1)
    stack_push(&s, 2)
    stack_push(&s, 3)
    printf("%d %d\n", stack_pop(&s), stack_pop(&s))
    return 0
}
```

### 5.2 Queue enqueue/dequeue

```flow
struct Queue {
    data: [i32; 8],
    head: i32,
    tail: i32,
    count: i32
}

function q_push(q: ptr<Queue>, v: i32) -> void {
    q[0].data[q[0].tail] = v
    q[0].tail = (q[0].tail + 1) % 8
    q[0].count = q[0].count + 1
}

function q_pop(q: ptr<Queue>) -> i32 {
    let v: i32 = q[0].data[q[0].head]
    q[0].head = (q[0].head + 1) % 8
    q[0].count = q[0].count - 1
    return v
}

function main() -> i32 {
    let mut q: Queue = Queue {
        data: [0, 0, 0, 0, 0, 0, 0, 0],
        head: 0,
        tail: 0,
        count: 0
    }
    q_push(&q, 10)
    q_push(&q, 20)
    printf("%d %d count=%d\n", q_pop(&q), q_pop(&q), q.count)
    return 0
}
```

### 5.3 Mini map: key lookup

```flow
function lookup(keys: ptr<i32>, vals: ptr<i32>, n: i32, key: i32) -> i32 {
    for i in 0 to n {
        if keys[i] == key {
            return vals[i]
        }
    }
    return -1
}

function main() -> i32 {
    let keys: [i32; 3] = [1, 2, 3]
    let vals: [i32; 3] = [100, 200, 300]
    printf("2 -> %d\n", lookup(keys, vals, 3, 2))
    printf("9 -> %d\n", lookup(keys, vals, 3, 9))
    return 0
}
```

---

## Part 6: Concurrency shapes

For fuller browser lessons, see [concurrency.md](concurrency.md).

### 6.1 Shared counter (single-threaded sketch)

```flow
function main() -> i32 {
    let mut counter: i32 = 0
    for i in 0 to 5 {
        counter = counter + 1
    }
    printf("counter=%d\n", counter)
    return 0
}
```

### 6.2 Mutex-shaped lock flag

```flow
struct Counter {
    value: i32,
    locked: i32
}

function main() -> i32 {
    let mut c: Counter = Counter { value: 0, locked: 0 }
    c.locked = 1
    c.value = c.value + 1
    c.locked = 0
    printf("value=%d locked=%d\n", c.value, c.locked)
    return 0
}
```

### 6.3 Channel-shaped buffer

```flow
function main() -> i32 {
    let mut buf: [i32; 4] = [0, 0, 0, 0]
    let mut count: i32 = 0
    buf[count] = 42
    count = count + 1
    printf("channel-ish count=%d first=%d\n", count, buf[0])
    return 0
}
```

### 6.4 Atomic-shaped read-modify-write

```flow
function main() -> i32 {
    let mut counter: i32 = 0
    # Single-threaded stand-in for atomic add
    counter = counter + 1
    counter = counter + 1
    printf("atomic-ish=%d\n", counter)
    return 0
}
```

---

## Part 7: Protocol sketches

### 7.1 Port bind sketch

```flow
function main() -> i32 {
    let port: i32 = 8080
    printf("TCP listener on port %d\n", port)
    return 0
}
```

### 7.2 Connection flag

```flow
function main() -> i32 {
    let connected: i32 = 0
    printf("TCP stream created\n")
    printf("Connected: %d\n", connected)
    return 0
}
```

### 7.3 Status code sketch

```flow
function main() -> i32 {
    let status_code: i32 = 200
    printf("Status: %d\n", status_code)
    return 0
}
```

---

## Exercises

### Exercise 1: Generic Stack

Implement a generic stack with `push`, `pop`, and `peek` operations.

### Exercise 2: Result Chaining

Write a function that parses a string to int, validates it's positive, and doubles it—using Result at each step.

### Exercise 3: Thread-Safe Counter

Create a counter that can be safely incremented from multiple threads.

---

## Next Steps

Continue to [Advanced Tutorial](advanced.md) to learn:
- Effect system
- Automatic differentiation
- GPU programming
- MLIR/LLVM backend
