# Effects Basics

> Effect-**shaped** control flow that runs in the browser.
>
> These lessons use plain functions as stand-ins. Real algebraic effects
> (`effect` / `capability` / `handle` / `with`) compile natively; see Part 4.

## Part 1: Motivation

### 1.1 Pure vs effectful

```flow
function pure_add(a: i32, b: i32) -> i32 {
    return a + b
}

function main() -> i32 {
    printf("pure=%d\n", pure_add(2, 3))
    printf("printf is an effect\n")
    return 0
}
```
### 1.2 Injected logger

```flow
function do_work(log_enabled: bool) -> i32 {
    let x: i32 = 10
    if log_enabled {
        printf("x=%d\n", x)
    }
    return x * 2
}

function main() -> i32 {
    printf("%d\n", do_work(true))
    printf("%d\n", do_work(false))
    return 0
}
```

## Part 2: Handler-shaped

### 2.1 Choose backend

```flow
function emit(backend: i32, msg: string) -> void {
    if backend == 0 {
        printf("[stdout] %s\n", msg)
    } else {
        printf("[null] (dropped)\n")
    }
}

function main() -> i32 {
    emit(0, "hello")
    emit(1, "hello")
    return 0
}
```
### 2.2 State thread

```flow
function step(state: ptr<i32>) -> void {
    state[0] = state[0] + 1
}

function main() -> i32 {
    let mut s: i32 = 0
    step(&s)
    step(&s)
    printf("%d\n", s)
    return 0
}
```

### 2.3 Resume-shaped continuation

Handlers resume the caller with a value. Model that as a callback result:

```flow
function ask(prompt: string) -> i32 {
    printf("ask: %s\n", prompt)
    return 42
}

function work() -> i32 {
    let n: i32 = ask("n?")
    return n * 2
}

function main() -> i32 {
    printf("%d\n", work())
    return 0
}
```

### 2.4 Multi-operation handler table

```flow
function on_op(op: i32, arg: i32) -> i32 {
    if op == 0 {
        printf("log %d\n", arg)
        return 0
    }
    if op == 1 {
        return arg + 1
    }
    return -1
}

function main() -> i32 {
    on_op(0, 7)
    printf("inc=%d\n", on_op(1, 10))
    printf("unknown=%d\n", on_op(9, 0))
    return 0
}
```

### 2.5 Capability-shaped gate

```flow
function write_file(allowed: bool, name: string) -> i32 {
    if !allowed {
        printf("denied: %s\n", name)
        return 1
    }
    printf("wrote: %s\n", name)
    return 0
}

function main() -> i32 {
    printf("rc=%d\n", write_file(false, "a.txt"))
    printf("rc=%d\n", write_file(true, "a.txt"))
    return 0
}
```

## Part 3: Limits

### 3.1 Document the boundary

```flow
function main() -> i32 {
    printf("Full effect handlers: see effects-showcase.md\n")
    printf("This lesson uses plain functions as stand-ins\n")
    return 0
}
```

## Part 4: Native effects (run with `./flow`)

The browser interpreter rejects `effect` / `handle` / `capability`. On the
real compiler:

```bash
./flow run examples/effects/showcase.flow
```

Read the walkthrough: [effects-showcase.md](../effects-showcase.md).

Typical surface (native):

```flow
effect Logger {
    log(msg: string) -> void
}

function work() -> void with Logger {
    perform Logger.log("hello")
}

handle Logger with {
    log(msg) => { printf("%s\n", msg); resume() }
} in {
    work()
}
```

Swap handlers (stdout vs null vs file) without rewriting `work`.
