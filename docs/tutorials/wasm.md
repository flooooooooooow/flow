# WASM

Flow’s C backend targets WebAssembly via emcc. Same source runs native and in
the browser — threads, WebGPU, sockets, files, and even CPython crossings are
documented with measured demos.

> Interactive lessons below are ordinary `main` programs (they also run under
> `./flow run`). Building `.wasm` needs emscripten:
>
> ```bash
> ./flow wasm examples/wasm/hello_wasm.flow
> ./scripts/build_wasm_hello.sh
> ```
>
> Deep dive: [wasm-crossings.md](../language/wasm-crossings.md) ·
> [examples/wasm/](../../examples/wasm/).

## Part 1: Same program, two targets

### 1.1 Hello fib

```flow
function fib(n: i32) -> i32 {
    if n <= 1 {
        return n
    }
    return fib(n - 1) + fib(n - 2)
}

function main() -> i32 {
    let v: i32 = fib(10)
    printf("hello_wasm fib(10) = %d\n", v)
    if v != 55 {
        return 1
    }
    return 0
}
```

### 1.2 Deterministic check

```flow
function main() -> i32 {
    let mut s: i32 = 0
    for i in 1 to 11 {
        s = s + i
    }
    printf("sum1..10=%d\n", s)
    if s != 55 {
        return 1
    }
    return 0
}
```

## Part 2: What crosses the boundary

### 2.1 Pure compute ships cleanly

```flow
function dot(a: [i32; 4], b: [i32; 4]) -> i32 {
    let mut s: i32 = 0
    for i in 0 to 4 {
        s = s + a[i] * b[i]
    }
    return s
}

function main() -> i32 {
    let a: [i32; 4] = [1, 2, 3, 4]
    let b: [i32; 4] = [4, 3, 2, 1]
    printf("%d\n", dot(a, b))
    return 0
}
```

### 2.2 Fixed buffers, no hidden alloc

```flow
function fill(xs: ptr<i32>, n: i32, v: i32) -> void {
    for i in 0 to n {
        xs[i] = v
    }
}

function main() -> i32 {
    let mut buf: [i32; 8] = [0, 0, 0, 0, 0, 0, 0, 0]
    fill(&buf[0], 8, 7)
    printf("%d %d\n", buf[0], buf[7])
    return 0
}
```

## Part 3: Parallel-shaped workload

### 3.1 Chunk sum (stand-in for workers)

```flow
function chunk_sum(xs: [i32; 8], lo: i32, hi: i32) -> i32 {
    let mut s: i32 = 0
    let mut i: i32 = lo
    while i < hi {
        s = s + xs[i]
        i = i + 1
    }
    return s
}

function main() -> i32 {
    let xs: [i32; 8] = [1, 1, 1, 1, 1, 1, 1, 1]
    let a: i32 = chunk_sum(xs, 0, 4)
    let b: i32 = chunk_sum(xs, 4, 8)
    printf("parts=%d %d total=%d\n", a, b, a + b)
    return 0
}
```

### 3.2 Reduce after map

```flow
function main() -> i32 {
    let mut xs: [i32; 5] = [1, 2, 3, 4, 5]
    for i in 0 to 5 {
        xs[i] = xs[i] * xs[i]
    }
    let mut s: i32 = 0
    for i in 0 to 5 {
        s = s + xs[i]
    }
    printf("%d\n", s)
    return 0
}
```

## Part 4: Native WASM path

```bash
# Native smoke (no emcc)
./flow run examples/wasm/hello_wasm.flow

# Emit C (+ .wasm / HTML when emcc is installed)
./flow wasm examples/wasm/hello_wasm.flow

# Parallel sum with pthreads → Web Workers
./flow wasm examples/wasm/parallel_sum.flow --threads --workers 8
```

Serve the measured crossing demos:

```bash
python3 -m http.server -d site 8000
# open http://127.0.0.1:8000/wasm-crossings/threads/
```

Crossings covered in docs: OS threads, WebGPU, sockets, filesystem, embedded
CPython — see [wasm-crossings.md](../language/wasm-crossings.md).
