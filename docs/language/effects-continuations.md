# Effect continuations

> **Status:** 1.0 language rule. Handlers are **tail-resumptive**. Abort,
> retry, and multi-shot continuation capture are reserved / future (issue
> [#564](https://github.com/flooooooooooow/flow/issues/564), surface
> `effects-multishot` in `stability/surfaces.json`).

Flow's `effect` / `capability` / `handle` system is a dynamically scoped
capability table. An operation is a function call: the current handler runs
and **returns to the call site**. That is enough for logging, configuration,
dependency injection, clocks, metrics, and test doubles. It is not Koka,
Eff, or OCaml 5.

The design choice and the ABI reason are in
[rfc_effects_continuations.md](../research/rfc_effects_continuations.md).
The cookbook that stays inside this model is
[effects-showcase.md](../effects-showcase.md).

## What tail-resumptive means

```flow
effect Probe {
    mark(x: i32) -> i32,
}

capability PlusOne {
    effect Probe,
    function mark(x: i32) -> i32 {
        return x + 1
    },
}

function main() -> i32 {
    let mut n: i32 = 0
    handle Probe with PlusOne {
        n = Probe.mark(n)
        n = Probe.mark(n)
    }
    return n
}
```

`return x + 1` **is** the resume. Control continues at `n = Probe.mark(n)`.
The second call happens because the first one came back. The handle block
is not a delimited continuation the handler can jump out of or replay.

## What is not expressible

| Encoding | What a full handler would do | Flow 1.0 encoding |
|---|---|---|
| **Abort** | Decline to resume, so the rest of the `handle` block does not run (exceptions) | Return a `Result` or a status code; the caller branches |
| **Retry** | Invoke the continuation again with different state | A loop in the caller plus a policy effect (`should_retry`) |
| **Multi-shot** | Invoke the same continuation more than once (generators, backtracking, schedulers) | Not an effect-handler feature. The runtime `Cont` scaffold is a separate concurrency API |

The type checker rejects the reserved forms `resume` and `resume_multi`
inside a capability method so they cannot be mistaken for continuation
operators.

```flow expect-error
effect Probe {
    mark(x: i32) -> i32,
}

capability Replay {
    effect Probe,
    function mark(x: i32) -> i32 {
        resume(x)
        return x
    },
}

function main() -> i32 {
    return 0
}
```

## Abort: status, not a jump

A handler cannot cancel the rest of the `handle` block. Return a code the
caller inspects.

```flow
effect Gate {
    allow(n: i32) -> i32,
}

capability Closed {
    effect Gate,
    function allow(n: i32) -> i32 {
        return 0 - 1
    },
}

function main() -> i32 {
    let mut code: i32 = 0
    handle Gate with Closed {
        code = Gate.allow(1)
        if code < 0 {
            return 1
        }
        return 0
    }
    return code
}
```

`Closed.allow` still returns to the call site. The `if` is ordinary control
flow, not an abort of the handler.

## Retry: a loop in the caller

The showcase retry pattern is a policy effect, not a handler re-invoking
its continuation. `examples/effects/async_effects.flow` is the complete
program.

```flow
effect Retry {
    should_retry(attempt: i32, max_attempts: i32) -> i32,
}

capability LinearRetry {
    effect Retry,
    function should_retry(attempt: i32, max_attempts: i32) -> i32 {
        if attempt < max_attempts {
            return 1
        }
        return 0
    },
}

function try_once(n: i32) -> i32 {
    return n
}

function main() -> i32 {
    let mut attempt: i32 = 0
    let mut last: i32 = 0
    handle Retry with LinearRetry {
        while attempt < 3 {
            last = try_once(attempt)
            if Retry.should_retry(attempt, 3) == 0 {
                return last
            }
            attempt = attempt + 1
        }
    }
    return last
}
```

## Multi-shot: not on `handle`

A capability method cannot capture the rest of the `handle` block and run
it twice. Scheduler, generator, and backtracking encodings that need that
do not belong on `handle` in 1.0.

The concurrency runtime has a separate `Cont` scaffold
(`examples/concurrency/cont_multishot.flow`). That is not algebraic-effect
handler semantics.

## How the C backend keeps this cheap

Each effect is a vtable and a `_Thread_local` (fiber-keyed) current-handler
pointer. `handle E with H` saves, installs, runs the block, and restores.
`E.op(args)` is a call through that pointer, or a direct call to `H_op`
when the operation is written inside the `handle` block itself.

There is no continuation object, no stack copy, and no CPS transform. That
is why abort / retry / multi-shot are not a small extension: they need a
different compilation strategy.

## See also

- [Effects & Capabilities cookbook](../effects-showcase.md)
- [Book 12: Effects and Concurrency](../book/12-effects-and-concurrency.md)
- [Async via Effects](async-effects.md)
- [RFC: continuation limitation](../research/rfc_effects_continuations.md)
- Language spec §6.5 in [LANGUAGE_SPEC.md](../LANGUAGE_SPEC.md)
