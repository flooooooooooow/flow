# 12. Effects and concurrency

An effect names an operation. A capability provides its implementation.
Concurrency comes from data-parallel loops, pthread-based primitives, and
asynchronous runtimes selected by effect handlers. Flow has no `async`,
`await`, `go`, or language-level `select` keyword.

## 12.1 Declaring an effect

```flow
effect Log {
    info(message: string) -> void,
    metric(name: string, value: i32) -> i32,
}
```

The declaration names operations and their types. It does not choose where the
message goes.

## 12.2 Capabilities

```flow
capability Console {
    effect Log,

    function info(message: string) -> void {
        printf("[info] %s\n", message)
    },

    function metric(name: string, value: i32) -> i32 {
        printf("[metric] %s\n", name)
        return value
    },
}
```

A capability supplies implementations for one effect. Capabilities are
currently stateless; mutable handler state must be threaded through ordinary
program values or a lower-level runtime object.

## 12.3 Installing handlers

```text
handle Log with Console {
    Log.info("started")
    let count: i32 = Log.metric("items", 12)
}
```

The handler is dynamically scoped. A nested `handle` temporarily overrides an
outer handler and the outer handler is restored at block exit. A function
called from inside the block observes the installed handler too.

Multiple effects and handlers can be installed together:

```text
handle Log, Notify with Console, DesktopNotifications {
    place_order()
}
```

The C backend uses a thread-local handler pointer and a vtable. When the handler
is statically known, the compiler may replace dispatch with a direct call.

## 12.4 Effect rows

```text
function process(name: string) -> void with Log {
    Log.info(name)
}

let operation: (string) -> void with Log = process
```

The `with` clause records permitted effects in a function or function type.
With `--strict-effects` or `FLOW_STRICT_EFFECTS=1`, a caller must install the
effect or declare it in its own row. Without strict effects, an unhandled
operation retains the compatibility behaviour of returning a zero value or
doing nothing.

```bash
FLOW_HOST=python ./flow run tests/lang/test_effects.flow
FLOW_STRICT_EFFECTS=1 FLOW_HOST=python ./flow run examples/effects/effect_rows.flow
FLOW_STRICT_EFFECTS=1 FLOW_HOST=python ./flow run examples/book/10_effect_handler.flow
```

## 12.5 Why handlers matter

The call site remains stable while policy changes:

```text
Log operation -> console capability
              -> quiet capability
              -> test recorder
              -> remote collector
```

Asynchronous schedulers and I/O handlers use the same arrangement.

## 12.6 Three concurrency models

| Form | Model | Use |
|---|---|---|
| `parallel for` | OpenMP or serial fallback | independent indexed work |
| `stdlib/concurrent.flow` | pthread threads, mutexes, condition variables | shared-memory and channel programs |
| `stdlib/async.flow` | effects selecting simulated, threaded, fiber, or netpoll handlers | swappable scheduling and I/O policy |

## 12.7 Worked parallel loop: disjoint writes

Each parallel iteration below writes to a different array element. The final
sum runs after the parallel loop has finished.

```flow
extern {
    function printf(fmt: string, ...) -> i32
}

function main() -> i32 {
    let input: array<i32, 8> = [1, 2, 3, 4, 5, 6, 7, 8]
    let mut output: array<i32, 8> = [0, 0, 0, 0, 0, 0, 0, 0]

    parallel for i in 0 to 8 {
        output[i] = input[i] * input[i]
    }

    let mut total: i32 = 0
    for i in 0 to 8 {
        total = total + output[i]
    }

    printf("sum of squares: %d\n", total)
    if total != 204 { return 1 }
    return 0
}
```

Source:
[`examples/book/12_parallel_transform.flow`](../../examples/book/12_parallel_transform.flow)

```bash
./flow run examples/book/12_parallel_transform.flow
```

```text
sum of squares: 204
```

Writing `total = total + ...` inside the parallel loop would create a race.
Separate output elements avoid shared writes, and the serial reduction makes
the order clear.

## 12.8 Channels and synchronisation

```text
import "stdlib/concurrent.flow"

let mut channel: Channel_i32 = channel_i32_new(16)
let cp: ptr<Channel_i32> = &channel

channel_i32_send(cp, 42)
let mut value: i32 = 0
channel_i32_recv(cp, &value)
channel_i32_close(cp)
channel_i32_destroy(cp)
```

The library supplies blocking and nonblocking send/receive, close, `select2`,
`select4`, mutexes, condition variables, semaphores, once initialisation,
thread spawn/join, and `WaitGroup`. Each object owns native resources and must
be destroyed according to its API.

```bash
./flow run examples/concurrency/channels.flow
./flow run examples/concurrency/select.flow
```

## 12.9 Asynchronous effects

```flow
import "stdlib/async.flow"

function work(id: i32) -> i32 with Async {
    Async.delay(10)
    return id * 10
}

function main() -> i32 {
    let mut result: i32 = 0
    handle Async with SimulatedAsync {
        result = work(4)
    }
    return result - 40
}
```

Available handlers include:

- `SimulatedAsync`, a deterministic synchronous implementation;
- `ThreadedAsync`, using OS threads;
- `FiberAsync`, an M:N cooperative fiber runtime with work stealing;
- `BlockingAsyncIO`, using blocking system calls;
- `NetpollAsyncIO`, using kqueue on Darwin and epoll on Linux.

The active handler selects the implementation without changing `work`.

## 12.10 Fiber and I/O semantics

`FiberAsync` runs Flow's main work on fibers so delay and netpoll operations can
park a fiber. Effect handlers are fiber-local, allowing migration between OS
threads. Worker count comes from `FLOW_MAXPROCS` or the detected CPU count and
can be set before the scheduler starts.

The runtime contains continuation scaffolding and multi-shot experiments, but
arbitrary Flow stack frames are not yet captured and restored by general
delimited continuations. `BlockingTcp` uses synchronous sockets; netpoll can
park around readiness, but a fully integrated nonblocking TCP effect remains a
separate concern.

## 12.11 Races and determinism

Neither effects nor channels make arbitrary shared mutation safe. A
`parallel for` body must assign disjoint elements or use explicit
synchronisation. A channel orders values through its own protocol but does not
protect unrelated state. Use `FLOW_TSAN=1` or `--sanitize=tsan` when the
platform toolchain supports it.

## Exercises

1. Implement console and quiet capabilities for one effect.
2. Run the same asynchronous operation under simulated and fiber handlers.
3. Design a channel close protocol with one producer and one consumer.
4. Identify the data race in a parallel sum and replace it with disjoint partial
   sums.

Next: [Evolution, hybrid systems, dynamics, and fields](13-evolution-and-dynamics.md).
