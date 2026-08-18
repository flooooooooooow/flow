# Effects Basics

> The browser lessons below use ordinary functions to teach the shape of dependency selection.
> The native compiler supports the real `effect` / `capability` / `handle` / `with` system.
>
> For the full native cookbook, see [Effects & Capabilities](../effects-showcase.md).

## Part 1: Motivation

### 1.1 Pure vs effectful

```flow
function pure_add(a: i32, b: i32) -> i32 {
    return a + b
}

function main() -> i32 {
    printf("pure=%d\n", pure_add(2, 3))
    printf("printf performs observable I/O\n")
    return 0
}
```

### 1.2 Why passing flags everywhere gets noisy

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

This is manageable for one flag. It becomes plumbing when every function needs logger, clock,
configuration, storage, notification, or scheduling parameters just so a deeper function can use
them.

## Part 2: Handler-shaped ideas in the browser

The interactive browser runner does not currently parse native effect declarations, so these
examples use plain functions to introduce the idea before moving to the real syntax.

### 2.1 Choose a backend

```flow
function emit(backend: i32, msg: string) -> void {
    if backend == 0 {
        printf("[stdout] %s\n", msg)
    } else {
        printf("[null] dropped\n")
    }
}

function main() -> i32 {
    emit(0, "hello")
    emit(1, "hello")
    return 0
}
```

### 2.2 Keep mutable state explicit

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

This remains useful with native effects: capabilities are stateless today, so mutable application
state normally stays in ordinary values and pointers.

## Part 3: Native Flow effects

Run native examples with `./flow`:

```bash
./flow run examples/effects/showcase.flow
./flow run examples/effects/dependency_injection.flow
./flow run examples/effects/state_effects.flow
./flow run examples/effects/async_effects.flow
```

### 3.1 Declare an effect

```flow
effect Logger {
    log_info(msg: string) -> void,
    log_error(msg: string) -> void,
}
```

### 3.2 Implement it with a capability

```flow
capability ConsoleLogger {
    effect Logger,

    function log_info(msg: string) -> void {
        let m: string = msg
        printf("[INFO] %s\n", m)
    },

    function log_error(msg: string) -> void {
        let m: string = msg
        printf("[ERROR] %s\n", m)
    },
}
```

### 3.3 Call the effect from business logic

```flow preamble=tests/fixtures/doc_preambles/effects-basics-effects.flow
function work() -> void with Logger {
    Logger.log_info("hello")
}
```

There is no handler parameter on `work`.

### 3.4 Install the capability for one dynamic scope

```flow preamble=tests/fixtures/doc_preambles/effects-basics-all.flow
function main() -> i32 {
    handle Logger with ConsoleLogger {
        work()
    }
    return 0
}
```

### 3.5 Swap the handler

```flow preamble=tests/fixtures/doc_preambles/effects-basics-all.flow
capability NullLogger {
    effect Logger,

    function log_info(msg: string) -> void {
    },

    function log_error(msg: string) -> void {
    },
}

handle Logger with NullLogger {
    work()
}
```

The body of `work` does not change.

### 3.6 Override one nested region

```flow preamble=tests/fixtures/doc_preambles/effects-basics.flow
handle Logger with ConsoleLogger {
    Logger.log_info("visible")

    handle Logger with NullLogger {
        Logger.log_info("hidden")
    }

    Logger.log_info("visible again")
}
```

The outer handler is restored when the nested block ends.

### 3.7 Handle several effects with one capability

```flow
effect Inventory {
    stock_of(sku: i32) -> i32,
}

effect Notify {
    send(recipient: string, msg: string) -> void,
}

capability TestBackend {
    effect Inventory, Notify,

    function stock_of(sku: i32) -> i32 {
        return 99
    },

    function send(recipient: string, msg: string) -> void {
        let r: string = recipient
        printf("captured for %s\n", r)
    },
}

handle Inventory, Notify with TestBackend {
    let stock: i32 = Inventory.stock_of(1001)
    Notify.send("test@example.com", "done")
}
```

### 3.8 Strict effect rows

```flow preamble=tests/fixtures/doc_preambles/effects-basics-effects.flow
function greet(name: string) -> void with Logger {
    Logger.log_info(name)
}
```

Compile with effect coverage checking:

```bash
./flow transpile program.flow --c --strict-effects -o build/program.c
```

A caller must then handle `Logger` or declare the requirement on its own signature.

## Part 4: What native handlers do not mean

Current Flow handlers are not general resumable continuations. The supported syntax is named
`capability` declarations installed by `handle ... with ...`; there is no current inline
`resume()` handler syntax.

For retry, timeout, counters, accumulators, and similar stateful patterns, keep state explicit and
use the effect as a swappable policy. The runnable examples demonstrate that exact shape.

## Next

Read the main [Effects & Capabilities cookbook](../effects-showcase.md) for more than twenty concrete
patterns, then inspect the runnable sources under [`examples/effects/`](../../examples/effects/).
