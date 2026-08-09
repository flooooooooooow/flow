# Spans

Borrowed views over contiguous storage: `{pointer, length}` as one value.
Callers never write `span(...)`. Arrays and slices borrow automatically.

> The browser interpreter does **not** run real `span<T>`. Lessons below use
> fixed arrays + an explicit length to teach the shape. Native:
>
> ```bash
> ./flow run examples/basics/spans.flow
> ```
>
> Spec: [spans.md](../language/spans.md).

## Part 1: Why spans exist

### 1.1 Pointer + length can lie

```flow
function sum_lying(data: ptr<i32>, n: i32) -> i32 {
    let mut s: i32 = 0
    for i in 0 to n {
        s = s + data[i]
    }
    return s
}

function main() -> i32 {
    let xs: [i32; 3] = [10, 20, 30]
    # Honest call
    printf("ok=%d\n", sum_lying(&xs[0], 3))
    # Wrong n would be undefined natively — we just show the API smell
    printf("api=ptr+len (easy to get wrong)\n")
    return 0
}
```

### 1.2 Fixed array only fits one extent

```flow
function sum4(xs: [i32; 4]) -> i32 {
    return xs[0] + xs[1] + xs[2] + xs[3]
}

function main() -> i32 {
    let a: [i32; 4] = [1, 2, 3, 4]
    printf("%d\n", sum4(a))
    printf("need sum8? write another function\n")
    return 0
}
```

## Part 2: View-shaped APIs (browser)

### 2.1 Total over a length

```flow
function total(xs: [i32; 8], n: i32) -> i32 {
    let mut s: i32 = 0
    let mut i: i32 = 0
    while i < n {
        s = s + xs[i]
        i = i + 1
    }
    return s
}

function main() -> i32 {
    let xs: [i32; 8] = [1, 2, 3, 4, 5, 6, 7, 8]
    printf("all=%d\n", total(xs, 8))
    printf("first4=%d\n", total(xs, 4))
    return 0
}
```

### 2.2 Window (slice caricature)

```flow
function window_sum(xs: [i32; 8], start: i32, len: i32) -> i32 {
    let mut s: i32 = 0
    let mut i: i32 = 0
    while i < len {
        s = s + xs[start + i]
        i = i + 1
    }
    return s
}

function main() -> i32 {
    let xs: [i32; 8] = [1, 2, 3, 4, 5, 6, 7, 8]
    printf("%d\n", window_sum(xs, 1, 3))
    return 0
}
```

### 2.3 Scale in place (mutable view)

```flow
function scale(xs: ptr<i32>, n: i32, factor: i32) -> void {
    let mut i: i32 = 0
    while i < n {
        xs[i] = xs[i] * factor
        i = i + 1
    }
}

function main() -> i32 {
    let mut xs: [i32; 4] = [1, 2, 3, 4]
    scale(&xs[0], 4, 2)
    printf("%d %d %d %d\n", xs[0], xs[1], xs[2], xs[3])
    return 0
}
```

### 2.4 Static extent habit

```flow
function corners(box: [i32; 4]) -> i32 {
    return box[0] + box[3]
}

function main() -> i32 {
    let b: [i32; 4] = [1, 0, 0, 9]
    printf("%d\n", corners(b))
    return 0
}
```

## Part 3: Nested views

### 3.1 First half then sum

```flow
function half_len(n: i32) -> i32 {
    return n / 2
}

function total(xs: [i32; 8], n: i32) -> i32 {
    let mut s: i32 = 0
    for i in 0 to n {
        s = s + xs[i]
    }
    return s
}

function main() -> i32 {
    let xs: [i32; 8] = [2, 4, 6, 8, 10, 12, 14, 16]
    let n: i32 = half_len(8)
    printf("front=%d\n", total(xs, n))
    return 0
}
```

### 3.2 Read-only vs write intent

```flow
function peek(xs: [i32; 4], i: i32) -> i32 {
    return xs[i]
}

function poke(xs: ptr<i32>, i: i32, v: i32) -> void {
    xs[i] = v
}

function main() -> i32 {
    let mut xs: [i32; 4] = [0, 0, 0, 0]
    poke(&xs[0], 2, 42)
    printf("%d\n", peek(xs, 2))
    return 0
}
```

## Part 4: Native spans

Real surface (native only, do not paste into the browser runner):

```flow
function total(samples: span<f32>) -> f32 {
    let mut acc: f32 = 0.0
    let mut i: i32 = 0
    while i < samples.len {
        acc = acc + samples[i]
        i = i + 1
    }
    return acc
}

function scale(samples: span<mut f32>, factor: f32) {
    let mut i: i32 = 0
    while i < samples.len {
        samples[i] = samples[i] * factor
        i = i + 1
    }
}
```

```bash
./flow run examples/basics/spans.flow
```

`span<T>`, `span<mut T>`, `span<T, N>`, and `&[T]` sugar are in the C backend.
Inference (`bare span`, dependent extents) is not, name the element type.
