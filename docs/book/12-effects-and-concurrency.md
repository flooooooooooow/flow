# 12. Effects and concurrency

An effect names an operation; a capability provides its implementation. Flow combines this with data-parallel loops and concurrency libraries rather than adding `async`/`await` keywords. Every `flow` block in this chapter is compiler-checked in CI.

## 12.1 Effect, capability, handler

```flow
effect Log {
    info(message: string) -> void,
    metric(name: string, value: i32) -> i32,
}

capability Console {
    effect Log,

    function info(message: string) -> void {
        printf("%s\n", message)
    },

    function metric(name: string, value: i32) -> i32 {
        printf("%s\n", name)
        return value
    },
}

function work() -> void with Log {
    Log.info("started")
    let count: i32 = Log.metric("items", 12)
}

function main() -> i32 {
    handle Log with Console {
        work()
    }
    return 0
}
```

The effect is the interface, the capability is one implementation, and `handle` installs it for a dynamic scope.

## 12.2 Effect rows

The `with` clause records effects a function may perform:

```flow
effect BookLog {
    info(message: string) -> void,
}

function process(name: string) -> void with BookLog {
    BookLog.info(name)
}
```

With strict effects enabled, callers must either install the effect or include it in their own row.

```bash
FLOW_STRICT_EFFECTS=1 FLOW_HOST=python ./flow run examples/effects/effect_rows.flow
```

## 12.3 Swappable policy

The same effect can have multiple capabilities. Business logic continues to call the effect interface while the caller selects console, test, remote, simulated, threaded, or fiber-backed behavior. The complete patterns live in [Effects & capabilities](../effects-showcase.md).

## 12.4 Parallel loops

```flow
function square_all(input: ptr<i32>, output: ptr<i32>, n: i32) -> void {
    parallel for i in 0 to n {
        output[i] = input[i] * input[i]
    }
}
```

The C backend uses OpenMP when available and otherwise preserves a correct serial loop. Parallel bodies must avoid racing shared writes.

## 12.5 Channels and synchronization

`lib/stdlib/concurrent.flow` supplies pthread-backed channels, mutexes, condition variables, semaphores, one-time initialization, thread spawn/join, `WaitGroup`, and small `select` helpers. Because these examples depend on the imported library and native runtime, use the checked-in complete programs:

```bash
FLOW_HOST=python ./flow run examples/concurrency/channels.flow
FLOW_HOST=python ./flow run examples/concurrency/select.flow
```

## 12.6 Asynchronous effects

The async standard library exposes an `Async` effect with several handler implementations. A complete self-contained example is kept in the repository:

```bash
FLOW_HOST=python ./flow run examples/effects/async_effects.flow
```

Available policies include deterministic simulated execution, OS-thread execution, fibers, blocking I/O, and netpoll-backed I/O. The active handler changes policy without changing the operation that requests the effect.

## 12.7 Fiber and I/O semantics

`FiberAsync` can park work and keeps effect handlers fiber-local. Worker count is controlled through the runtime configuration. General arbitrary-stack delimited continuations are not claimed as complete; the runtime has continuation infrastructure but the supported async surface is the one exercised by repository tests and examples.

## 12.8 Races and determinism

Effects and channels do not make unrelated shared mutation safe. A `parallel for` should write disjoint storage or use explicit synchronization. ThreadSanitizer can be enabled where the platform toolchain supports it.

## Exercises

Implement two capabilities for one effect, run the same async operation under different handlers, design a producer/consumer close protocol, and replace a racy parallel reduction with disjoint partial results.

Next: [Evolution, hybrid systems, dynamics, and fields](13-evolution-and-dynamics.md).
