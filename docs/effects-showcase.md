# Effect System Showcase: One Service, Many Worlds

Flow's algebraic effect system is its clearest differentiator against Rust, Go,
Mojo, and Julia. This document walks through the runnable demo at
[`examples/effects/showcase.flow`](../examples/effects/showcase.flow) and makes
the argument concrete.

```sh
./flow run examples/effects/showcase.flow
```

The behaviours it demonstrates are pinned by an executed regression test,
`tests/runtime/test_effects_showcase.flow` (run with `./flow test-runtime`),
and the example itself is transpile-checked by `./flow test` like every
tracked file under `examples/`.

## What the demo is

A miniature checkout service. The business logic is one function, written
once, with **no** environment parameters:

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

Every side effect — logging, time, inventory reads/writes, notifications —
is an *effect operation* declared against an interface:

```flow
effect Inventory {
    stock_of(sku: i32) -> i32,
    reserve(sku: i32, qty: i32) -> i32,
}
```

Concrete behaviour is supplied by *capabilities* (handlers), installed for a
dynamic scope with `handle ... with ...`:

```flow
handle Log with SilentLogger {
    handle Inventory, Notify with TestBackend {
        test_accepted = run_batch()   # same compiled code, new world
    }
}
```

The demo runs the same `place_order` under four different worlds:

1. **Production stack** — timestamped ops logging, warehouse stock levels,
   outbound email. Order B is rejected (only 1 unit of sku 2002 in stock)
   and ops gets a restock email.
2. **Test stack** — same calls, zero code changes: fixture inventory (order B
   now *accepted*), silent logs, captured notifications. One capability
   (`TestBackend`) handles two effects at once.
3. **Dynamic scoping** — a nested `handle Log with SilentLogger` silences one
   region only; the outer handler is restored automatically when the block
   exits.
4. **Handler composition** — the production logger *itself* performs the
   `Clock` effect to timestamp lines, so swapping only the clock handler
   re-times every log line without touching the logger.
5. **Safe defaults** — with no handler installed, operations are no-ops that
   return zero; the service degrades instead of crashing.

## Captured output

Real output from `./flow run examples/effects/showcase.flow`
(macOS, C backend, current compiler):

```text
=====================================================
 FLOW EFFECT SYSTEM SHOWCASE: one service, many worlds
=====================================================
business logic: place_order(sku, qty) -- written once,
compiled once, no environment parameters.

--- [1] PRODUCTION stack ---------------------------
handle Log,Clock,Inventory,Notify with production handlers

order A: sku=1001 qty=2
  [1721224800] INFO  order received
  [1721224800] INFO  stock reserved
  --> email to customer@shop.example: order confirmed
  ACCEPTED (order id 501001)
order B: sku=2002 qty=5
  [1721224800] INFO  order received
  [1721224800] WARN  insufficient stock -- rejecting order
  --> email to ops@shop.example: restock needed
  REJECTED

production result: 1 of 2 orders accepted

--- [2] TEST stack: SAME code, zero changes --------
handle Log with SilentLogger; Inventory,Notify with TestBackend

order A: sku=1001 qty=2
  (test captured a notification for customer@shop.example)
  ACCEPTED (order id 42)
order B: sku=2002 qty=5
  (test captured a notification for customer@shop.example)
  ACCEPTED (order id 42)

test result: 2 of 2 orders accepted (fixture stock)
no log noise, no real email -- and place_order was not edited

--- [3] DYNAMIC SCOPE: silence one region ----------
outer scope logs loudly:
  [1721224800] INFO  before quiet region
inner quiet region (order still processed):
  --> email to customer@shop.example: order confirmed
  order id 501001, but not a single log line
outer handler restored automatically:
  [1721224800] INFO  after quiet region

--- [4] COMPOSED HANDLERS: swap ONLY the clock -----
OpsLogger asks the Clock effect for timestamps, so replacing
just the Clock handler re-times every log line:

  [1721224800] INFO  with WallClock
  [0] INFO  with FrozenClock

--- [5] NO HANDLER: safe defaults ------------------
calling place_order with NO handlers installed:
  returned -1 -- unhandled stock_of() defaulted to 0,
  logs and notifications were silent no-ops

=====================================================
 same compiled function. four different worlds.
=====================================================
```

## Why other languages can't express this as cleanly

The load-bearing property: **the callee names the *interface*, the caller
names the *implementation*, and the binding is dynamically scoped** —
`place_order` mentions `Inventory.stock_of` with no handler parameter, and
whichever `handle` block encloses the *call* (however deep the call stack)
decides what that means.

- **Rust / Go** — no dynamic scoping. To swap an implementation you must
  thread it: a trait object / interface parameter, a generic parameter, or a
  context struct passed through *every* function between `main` and the leaf
  call. Adding a `Notify` dependency to a leaf function forces a signature
  change up the whole call chain (or a global/thread-local you manage by
  hand, with none of the automatic save/restore that `handle` blocks give
  you). In the showcase, `run_batch` sits between `main` and `place_order`
  and mentions no dependencies at all.
- **Go specifically** — the idiomatic workaround is `context.Context`
  smuggling values by string key: untyped, invisible in signatures, and
  checked at runtime. Flow's effect operations are typed declarations.
- **Mojo / Julia** — no algebraic effects. Julia can approximate handler
  swapping with dynamic multiple dispatch plus global state, Mojo with
  trait parameters, but both reduce to the same choice: thread parameters
  everywhere or mutate globals manually. Neither has scoped
  install/override/restore semantics as a language construct.
- **Haskell** — can express this (mtl, `polysemy`, effect libraries) but at
  the cost of monad transformer stacks or effect-row type gymnastics.
  Flow's version is first-class syntax in a systems language that compiles
  to plain C: a `handle` block is a save/restore of a vtable pointer.

Section [4] shows the property compounding: handlers themselves perform
effects, so a *stack* of handlers is reconfigurable one layer at a time.
Mock the clock; keep the real logger; the logger doesn't know.

## How it works (current implementation)

The C backend implements effects with vtable-based dynamic dispatch
(`src/flow/c_generator.py`):

- each `effect` generates a handler struct of function pointers plus one
  global current-handler pointer;
- each `capability` generates plain C functions and a static vtable
  instance per handled effect;
- `handle E with H { ... }` saves the current pointer, installs `H`'s
  vtable, runs the block, and restores the pointer on exit;
- `E.op(args)` compiles to a dispatch function that calls through the
  current handler, or returns a zeroed default when none is installed;
- **zero-cost substitution**: written directly inside a `handle E with H`
  block, `E.op(args)` skips the dispatch function entirely and compiles to
  a direct call to `H`'s implementation, which the C compiler can inline.
  Swapping one handler for another is resolved at compile time and costs
  nothing at runtime. Dynamic dispatch remains wherever the handler is
  unknowable at the call site: functions called from inside the block,
  lambda bodies (a closure can outlive the block), and operations the
  installed capability does not implement.

Cost: zero for effect calls written inside a `handle` block; one indirect
call where dispatch stays dynamic. No allocation, no continuations, no
runtime library.

## Honest limitations (found while building this)

- **No effect typing / strict mode support.** Function signatures do not
  declare which effects they perform, so the compiler cannot reject a
  program that performs an unhandled effect — you get the runtime default
  instead. Relatedly, `--strict` type-checking does not yet model effect
  operations (`Inventory.stock_of` is reported as an undefined function);
  the standard harness compiles effect programs in the default `--lenient`
  mode.
- **Handlers are stateless.** Capability methods are plain functions: no
  `self`, and Flow has no mutable globals (only `const`), so a handler
  cannot accumulate state (e.g. a real collecting test-spy or a metrics
  counter). State-machine-style handlers need the struct + `impl` pattern
  instead — but see the next point.
- **The `capability EffectName` parameter style does not link.** The older
  examples in `examples/effects/` (`dependency_injection.flow`,
  `state_effects.flow`, `async_effects.flow`) pass handlers as
  `db: capability Database` parameters backed by struct `impl`s. Today the
  C backend emits calls to such functions but not their definitions, so
  those examples transpile (and thus pass the tier-1 harness) but fail C
  compilation under `./flow run`. This showcase uses only the
  `handle`/`with` + `capability` declaration form, which compiles, links,
  and runs end to end.
- **Resumable/one-shot continuation semantics are absent.** These are
  tail-resumptive handlers only (every operation returns straight to the
  call site). You cannot abort a computation from a handler, retry it, or
  run it twice — the classic exception/generator/scheduler encodings of
  full algebraic effects are out of scope today.
- **Type-inference gap inside capability methods.** `print`/`println` do
  not see parameter types inside capability method bodies (a string
  parameter prints as a float). Workaround used in the showcase: copy the
  parameter to a typed local (`let m: string = msg`) or use `printf`.
- **No handler-stack polymorphism in returns.** Effect operations returning
  `void`/`i32`/`string` work; unhandled operations default to zero, which
  is convenient (section [5]) but silent — combined with the missing effect
  typing, forgetting a `handle` block is easy to do and invisible until
  runtime.

## Files

- `examples/effects/showcase.flow` — the demo (this document's subject)
- `tests/runtime/test_effects_showcase.flow` — executed assertions pinning
  handler swap, nested override/restore, multi-effect capabilities,
  handler composition, and unhandled defaults
- `tests/unit/test_zero_cost_effects.py` — pins direct-call emission inside
  `handle` blocks and dynamic dispatch everywhere the handler is unknowable
- `docs/LANGUAGE_SPEC.md` section 6 — effect grammar and implementation notes
