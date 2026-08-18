# Effects & Capabilities: Cookbook and Showcase

Flow's effect system separates **what code needs to do** from **what implementation does it**.
Business code calls typed effect operations. A `capability` implements one or more effects, and
`handle ... with ...` installs that implementation for a dynamic scope.

This page is the main entry point for effects and capabilities in Flow. It starts with tiny
patterns, then points to complete runnable programs and the current implementation limits.

```sh
./flow run examples/effects/showcase.flow
./flow run examples/effects/dependency_injection.flow
./flow run examples/effects/state_effects.flow
./flow run examples/effects/async_effects.flow
```

The complete checkout showcase is pinned by `tests/runtime/test_effects_showcase.flow`, and
tracked examples under `examples/` are transpile-checked by `./flow test`.

## The model in 30 seconds

```flow
effect Log {
    info(msg: string) -> void,
}

capability Console {
    effect Log,
    function info(msg: string) -> void {
        printf("%s\n", msg)
    },
}

function work() -> void with Log {
    Log.info("hello")
}

function main() -> i32 {
    handle Log with Console {
        work()
    }
    return 0
}
```

The callee names the **effect interface**. The caller chooses the **capability implementation**.
Nothing is threaded through every intermediate function just to reach the leaf call.

## Cookbook

### 1. Declare an effect interface

An effect is a typed set of operations.

```flow
effect Clock {
    now() -> i32,
}

effect Notify {
    send(recipient: string, msg: string) -> void,
}
```

### 2. Call an effect operation

Business logic calls the interface directly.

```flow
function announce() -> void {
    let t: i32 = Clock.now()
    printf("time=%d\n", t)
    Notify.send("ops@example.com", "started")
}
```

There is no `clock` or `notifier` parameter.

### 3. Implement an effect with a capability

```flow
capability FrozenClock {
    effect Clock,
    function now() -> i32 {
        return 0
    },
}
```

A capability is the handler implementation installed by `handle`.

### 4. Install a handler for one scope

```flow
handle Clock with FrozenClock {
    let t: i32 = Clock.now()
    printf("%d\n", t)
}
```

The handler is active only inside the block.

### 5. Swap implementations without changing business code

```flow
capability WallClock {
    effect Clock,
    function now() -> i32 {
        return 1721224800
    },
}

capability FrozenClock {
    effect Clock,
    function now() -> i32 {
        return 0
    },
}

function print_time() -> void {
    printf("%d\n", Clock.now())
}

handle Clock with WallClock {
    print_time()
}

handle Clock with FrozenClock {
    print_time()
}
```

`print_time` is identical in both worlds.

### 6. Override a handler in a nested dynamic scope

```flow
handle Log with OpsLogger {
    Log.info("loud")

    handle Log with SilentLogger {
        Log.info("silent")
    }

    Log.info("loud again")
}
```

The outer handler is restored automatically when the inner block exits.

### 7. Handle several effects with one capability

A capability can implement more than one effect.

```flow
capability TestBackend {
    effect Inventory, Notify,

    function stock_of(sku: i32) -> i32 {
        return 99
    },

    function reserve(sku: i32, qty: i32) -> i32 {
        return 42
    },

    function send(recipient: string, msg: string) -> void {
        let r: string = recipient
        printf("captured notification for %s\n", r)
    },
}

handle Inventory, Notify with TestBackend {
    let order_id: i32 = place_order(1001, 2)
}
```

This is useful for test fixtures or adapters that naturally own several related interfaces.

### 8. Let one handler perform another effect

Handlers compose. The logger below asks the `Clock` effect for its timestamp.

```flow
capability OpsLogger {
    effect Log,

    function info(msg: string) -> void {
        let t: i32 = Clock.now()
        let m: string = msg
        printf("[%d] %s\n", t, m)
    },
}
```

Now changing only the clock changes every log timestamp.

```flow
handle Clock with FrozenClock {
    handle Log with OpsLogger {
        Log.info("deterministic test")
    }
}
```

### 9. Mix real and test handlers

You do not need an all-production or all-test stack.

```flow
handle Clock with FrozenClock {
    handle Log with OpsLogger {
        handle Inventory with WarehouseInventory {
            handle Notify with TestNotifier {
                place_order(1001, 1)
            }
        }
    }
}
```

This keeps real inventory behaviour, freezes time, and captures outbound notifications.

### 10. Declare an effect row on a function

Under `--strict-effects`, functions can state which effects they may perform.

```flow
function greet(name: string) -> void with Log {
    Log.info("hello")
    Log.info(name)
}
```

This is the current effect-row syntax used by `examples/effects/effect_rows.flow`.

### 11. Propagate an effect requirement through callers

```flow
function greet(name: string) -> void with Log {
    Log.info(name)
}

function shout() -> void with Log {
    greet("world")
    Log.info("!")
}
```

A caller may either install a handler or declare the same requirement on its own signature.

### 12. Close the effect row at the application boundary

```flow
function main() -> i32 {
    handle Log with Console {
        shout()
    }
    return 0
}
```

With strict effects enabled, the call is valid because the enclosing handler covers the row.

### 13. Turn unhandled effects into compile-time errors

```sh
./flow transpile program.flow --c --strict-effects -o build/program.c
```

`--strict-effects` checks bare performs and function effect rows. The default language mode
remains backwards-compatible with soft defaults.

### 14. Turn unhandled effects into runtime failures

```sh
FLOW_STRICT_EFFECTS=1 ./flow run program.flow
```

This is useful when you want fail-loud behaviour without changing source syntax.

### 15. Use the default soft fallback deliberately

Without strict effects, an unhandled operation returns its zeroed default and `void` operations
become no-ops.

```flow
function main() -> i32 {
    let t: i32 = Clock.now()
    printf("%d\n", t)   # 0 when no Clock handler is installed
    return 0
}
```

The checkout showcase demonstrates this explicitly. Prefer strict effects when a missing handler
would be a correctness bug.

### 16. Use effects for dependency injection

```flow
effect Database {
    query(sql: string) -> string,
    execute(sql: string) -> i32,
}

function get_user_name(user_id: i32) -> string {
    return Database.query("SELECT name FROM users WHERE id = 1")
}
```

Production and test database capabilities can be swapped at the call boundary.

```flow
handle Database with ProductionDB {
    let name: string = get_user_name(1)
}

handle Database with MockDBOk {
    let test_name: string = get_user_name(1)
}
```

See `examples/effects/dependency_injection.flow` for the complete database, logger, and config
example.

### 17. Inject configuration without a framework

```flow
effect Config {
    get_config(key: string) -> string,
}

function get_app_setting(key: string) -> string {
    return Config.get_config(key)
}

handle Config with EnvConfig {
    let value: string = get_app_setting("api_key")
}

handle Config with TestConfig {
    let value: string = get_app_setting("api_key")
}
```

The function stays unaware of environment variables, files, fixtures, or test harnesses.

### 18. Silence or redirect logging for one region

```flow
capability NullLogger {
    effect Logger,

    function log_info(msg: string) -> void {
    },

    function log_error(msg: string) -> void {
    },
}

handle Logger with NullLogger {
    create_user("Alice")
}
```

The business function is unchanged and no global logging mode is mutated.

### 19. Keep mutable state explicit; use the effect as policy

Capabilities are stateless today, so stateful loops should keep their state in ordinary locals
and let the effect decide the policy.

```flow
effect Counter {
    next(current: i32) -> i32,
}

capability UnitCounter {
    effect Counter,
    function next(current: i32) -> i32 {
        return current + 1
    },
}

capability DoubleStepCounter {
    effect Counter,
    function next(current: i32) -> i32 {
        return current + 2
    },
}

function count_up_to(start: i32, target: i32) -> i32 {
    let mut count: i32 = start
    while count < target {
        count = Counter.next(count)
    }
    return count
}
```

The same loop can use either policy.

```flow
handle Counter with UnitCounter {
    let result: i32 = count_up_to(0, 5)
}

handle Counter with DoubleStepCounter {
    let result: i32 = count_up_to(0, 5)
}
```

See `examples/effects/state_effects.flow` for counter and accumulator examples.

### 20. Model timeout policy as an effect

```flow
effect Timeout {
    has_expired(elapsed_ms: i32, deadline_ms: i32) -> i32,
}

capability SimpleTimeout {
    effect Timeout,

    function has_expired(elapsed_ms: i32, deadline_ms: i32) -> i32 {
        if elapsed_ms >= deadline_ms {
            return 1
        }
        return 0
    },
}
```

The elapsed time stays explicit; the handler decides the timeout rule.

### 21. Model retry policy as an effect

Flow's current handlers are tail-resumptive, so retry is modeled as policy rather than as a
continuation that replays the caller.

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
```

`examples/effects/async_effects.flow` contains a complete retry loop using this pattern.

### 22. Express async operations through an effect interface

```flow
effect Async {
    delay(ms: i32) -> void,
    spawn(task_id: i32) -> void,
    join(task_id: i32) -> i32,
}
```

A synchronous deterministic capability can stand in for the runtime implementation.

```flow
capability SyncAsync {
    effect Async,

    function delay(ms: i32) -> void {
        return
    },

    function spawn(task_id: i32) -> void {
        return
    },

    function join(task_id: i32) -> i32 {
        return task_id * 10
    },
}
```

For the stdlib `Async` / `AsyncIO` path, use `examples/effects/async_primitives.flow`. For timeout
and retry policy examples, use `examples/effects/async_effects.flow`.

### 23. Know when *not* to use an effect

Effects are best for behaviour selected by an enclosing environment: logging, time, I/O policy,
configuration, storage adapters, notifications, scheduling, test doubles, and similar concerns.

Owned mutable data is usually just data. The stack in `examples/effects/state_effects.flow` is an
ordinary `struct` plus pointer mutation because there is no useful environmental implementation
to swap.

### 24. Direct operations can become direct calls

Inside a `handle E with H` block, an `E.op(...)` written directly in that block can be emitted as
a direct call to `H`'s implementation. Calls where the handler is not statically knowable keep
dynamic dispatch.

That gives Flow two useful modes from the same source model: compile-time substitution where the
handler is obvious, and scoped dynamic dispatch through deeper call chains.

## Complete showcase: one service, many worlds

The runnable checkout demo at [`examples/effects/showcase.flow`](../examples/effects/showcase.flow)
uses four interfaces:

```flow
effect Log {
    info(msg: string) -> void,
    warn(msg: string) -> void,
}

effect Clock {
    now() -> i32,
}

effect Inventory {
    stock_of(sku: i32) -> i32,
    reserve(sku: i32, qty: i32) -> i32,
}

effect Notify {
    send(recipient: string, msg: string) -> void,
}
```

Its business function is written once:

```flow
function place_order(sku: i32, qty: i32) -> i32 {
    Log.info("order received")
    let available: i32 = Inventory.stock_of(sku)
    if available < qty {
        Log.warn("insufficient stock -- rejecting order")
        Notify.send("ops@shop.example", "restock needed")
        return -1
    }
    let order_id: i32 = Inventory.reserve(sku, qty)
    Log.info("stock reserved")
    Notify.send("customer@shop.example", "order confirmed")
    return order_id
}
```

It is then run under production handlers, test handlers, a nested logging override, and composed
clock/logger handlers. No environment parameter is added to `place_order` or the functions above
it in the call chain.

## Runnable example map

| Example | What it demonstrates | Run |
|---|---|---|
| [`showcase.flow`](../examples/effects/showcase.flow) | production/test swaps, nested scope, multi-effect capability, composition, defaults | `./flow run examples/effects/showcase.flow` |
| [`dependency_injection.flow`](../examples/effects/dependency_injection.flow) | database, logger, config, mocks | `./flow run examples/effects/dependency_injection.flow` |
| [`effect_rows.flow`](../examples/effects/effect_rows.flow) | `with Log` rows and strict-effect coverage | `./flow run examples/effects/effect_rows.flow` |
| [`state_effects.flow`](../examples/effects/state_effects.flow) | explicit state with swappable effect policy | `./flow run examples/effects/state_effects.flow` |
| [`async_effects.flow`](../examples/effects/async_effects.flow) | async stand-in, timeout policy, retry policy | `./flow run examples/effects/async_effects.flow` |
| [`async_primitives.flow`](../examples/effects/async_primitives.flow) | stdlib `Async` / `AsyncIO` handler path | `./flow run examples/effects/async_primitives.flow` |

For the guided chapter, read [Book 12: Effects and Concurrency](book/12-effects-and-concurrency.md).
For async-specific reference, read [Async via Effects](language/async-effects.md).

## How the C backend implements effects

The current C backend uses vtable-based dynamic dispatch:

- each `effect` generates a handler struct of function pointers plus one `_Thread_local`
  current-handler pointer;
- each `capability` generates plain C functions and a static vtable instance for the effects it
  handles;
- `handle E with H { ... }` saves the current pointer, installs `H`, runs the block, and restores
  the previous pointer on exit;
- `E.op(args)` calls through the current handler or uses the soft zero/no-op default when none is
  installed;
- operations written directly inside a statically-known `handle E with H` block can be emitted as
  direct calls, while deeper calls retain dynamic dispatch.

The handler mechanism itself allocates nothing and does not use continuations. Async capabilities
such as `FiberAsync` and `NetpollAsyncIO` pull in their runtime support only when used.

## Current limitations

These are important when designing real programs around the feature.

**Effect rows are opt-in.** `--strict-effects` enables compile-time coverage checking for lexical
handlers and declared function rows. Without it, the language keeps soft defaults for unhandled
operations.

**Capabilities are stateless.** Capability methods have no `self` or stored fields. Keep mutable
state in ordinary values and pointers, or use the explicit-state policy pattern shown above.

**Dynamic capability objects are not wired to dispatch.** The retired `capability EffectName`
parameter style should not be used. Install named capability blocks with `handle ... with ...`.
The older examples were rewritten to this supported form in issue #119.

**Handlers do not expose general resumable continuations.** An operation returns to its call site.
A handler cannot currently abort the whole computation, replay it, or resume it multiple times.
Model retry/timeout as explicit policy effects, as the runnable examples do.

**Capability method type inference has a known printing gap.** Some capability method parameters
need a typed local before `print`/`println`; the runnable examples use `printf` or an explicitly
typed local where necessary.

## The practical rule

Use an effect when the caller should choose **what a dependency means for this scope** without
rewriting or plumbing that choice through the callee. Use ordinary arguments, structs, and pointers
when the value is simply owned application data.

That distinction is what makes the system useful rather than merely another dependency-injection
mechanism: handlers are typed, dynamically scoped, composable, nestable, and can themselves perform
other effects.
