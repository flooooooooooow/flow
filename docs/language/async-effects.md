# Async via Effects

Flow models asynchronous / concurrent work with **algebraic effects**, not with
`async` / `await` keywords. Call sites perform effect operations; a capability
(handler) supplies the backend (`SimulatedAsync`, `ThreadedAsync`, `FiberAsync`,
`BlockingAsyncIO`, or `NetpollAsyncIO`).

This matches the comparison table in [docs/comparison.md](../comparison.md):
async is “modeled via effects (no `async` keyword).”

Umbrella + measured Go comparison:
[concurrency-vs-go.md](concurrency-vs-go.md) ·
[replace-go.md](replace-go.md).

## Intent

```flow
import "stdlib/async.flow"

function fetch_user(user_id: i32) -> i32 {
    Async.delay(100)          # or async_delay(100)
    return user_id * 10
}

function main() -> i32 {
    let mut result: i32 = 0
    handle Async with SimulatedAsync {
        result = fetch_user(1)
    }
    return result
}
```

Business logic depends only on the effect — swap `SimulatedAsync`,
`ThreadedAsync`, or `FiberAsync` without changing call sites. Swap
`BlockingAsyncIO` vs `NetpollAsyncIO` the same way for `AsyncIO`.

## Implemented

| Piece | Status |
|-------|--------|
| `lib/stdlib/async.flow` — `Async` effect (`delay`, `spawn`, `join`) | ✅ |
| Helpers `async_delay` / `async_spawn` / `async_join` / `async_sleep_ms` / `async_poll_read` | ✅ |
| `async_set_maxprocs` / `async_maxprocs` (`FLOW_MAXPROCS` env) | ✅ |
| `SimulatedAsync` — deterministic sync stand-in | ✅ |
| `ThreadedAsync` — real pthreads via `runtime/flow_concurrency.c` | ✅ |
| `FiberAsync` — **M:N** cooperative fibers via `runtime/flow_fiber.c` | ✅ |
| Asm context switch (`flow_fctx_arm64.S` / `x86_64.S`) | ✅ |
| `AsyncIO` + `BlockingAsyncIO` (`sleep_ms` → `usleep`; poll stubs return ready) | ✅ |
| `NetpollAsyncIO` — real kqueue (Darwin) / epoll (Linux) | ✅ |
| Fiber channel ping-pong + fan-out benches (beat Go) | ✅ |
| `TcpEffect` + `BlockingTcp` (loopback connect/send/recv) | ✅ `runtime/flow_tcp.c` |
| Demos: `examples/effects/async_primitives.flow`, `examples/concurrency/*` | ✅ |
| Runtime tests: `tests/runtime/test_{fiber_async,threaded_async,netpoll,…}.flow` | ✅ |
| Preferred install style: `handle … with …` | ✅ |

### Semantics today (honest)

- **FiberAsync runs `main` on a fiber** so `Async.delay` / netpoll park
  suspend real Flow frames mid-function (see `examples/concurrency/fiber_suspend.flow`).
  Delimited `shift`/`reset` that capture and restore an arbitrary Flow frame
  are still a C scaffold (`flow_cont_*`) — not a full compiler rewrite yet.
  `ThreadedAsync` runs registered C tasks on OS threads.
- **`FiberAsync` is M:N.** Workers = `FLOW_MAXPROCS` / CPU count by default
  (`async_set_maxprocs(n)` before first spawn; values `< 1` clamp to **1**,
  not “auto”). Ready work uses **per-worker deques + work-stealing**; effect
  handlers are **fiber-local** so fibers can migrate OS threads safely.
  The ping-pong microbench forces `maxprocs=1` for a fair switch measurement.
- **`SimulatedAsync` is stateless.** `spawn` is a no-op marker; `join(task_id)`
  returns `task_id * 10` as a deterministic stand-in.
- **`BlockingAsyncIO.sleep_ms`** blocks via POSIX `usleep` when `ms > 0`.
  `poll_read` / `poll_write` ignore the timeout and return `1` (ready).
- **`NetpollAsyncIO`** uses real kqueue/epoll. On a fiber, `poll_read` /
  `poll_write` **park the fiber** (`flow_netpoll_fiber_*`); off-fiber they
  block the OS thread. `sleep_ms` still uses the blocking timer path.
- **Unhandled ops** still default to zero / no-op unless `--strict-effects` /
  `FLOW_STRICT_EFFECTS=1` is set ([effects-showcase.md](../effects-showcase.md)).

## Deferred

| Item | Why deferred |
|------|----------------|
| Full compiler `shift`/`reset` rewrite | Fiber park + C reset/`resume_multi` ship; stack-copy multi-shot restore still open |
| Delimited continuations / Flow-stack suspend | ✅ main-on-fiber park; C `flow_reset`/`flow_shift` scaffold (`cont_reset.flow`) |
| M:N work-stealing | ✅ per-worker deques (`work_steal.flow`) |
| Fiber-aware netpoll | ✅ `flow_netpoll_fiber_*` via `NetpollAsyncIO` |
| Fiber-aware nonblocking TCP | `BlockingTcp` is sync sockets; park-on-poll still via `NetpollAsyncIO` |
| `Cont` + `FiberCont` (Flow-frame resume) | ✅ `Cont.shift` parks fiber (M:N-safe); `cont_arm_resume` — `cont_flow_resume.flow` |
| Fiber-per-conn HTTP + auth mw | ✅ `http_fiber.flow` (`Bearer flow` on `/api`) |
| HTTPS accept-loop (OpenSSL) | ✅ PEM cert/key + ALPN `http/1.1` (`http_tls.flow`) |
| Cont multi-shot scaffold | ✅ `flow_cont_resume_multi` / `cont_multishot.flow` |
| N-way `select` / `default` | ✅ `select2` + `select4` (+ `_try`) |
| `async` / `await` syntax sugar | Only after the runtime model is solid — do **not** add keywords first |
| Stateful handlers (`capability` with mutable task tables) | Capabilities are currently stateless; use struct+`impl` workarounds elsewhere |

Effect-row typing (`function f() -> T with E1, E2`) and `--strict-effects` already
ship — see [LANGUAGE_SPEC §6.3.1](../LANGUAGE_SPEC.md#631-signature-effect-rows)
and [effects-showcase.md](../effects-showcase.md).

## Older demos

`examples/effects/async_effects.flow` sketches Timeout/Retry as policy
effects (`handle ... with ...`, stateless capabilities, state threaded
through `let mut` locals — see [#119](https://github.com/flooooooooooow/flow/issues/119),
it previously used the broken `capability Async` **parameter** style).
Prefer `examples/effects/async_primitives.flow` for the stdlib `Async` /
`AsyncIO` handle/with path; `async_effects.flow` is still the place to look
for Timeout/Retry, which the stdlib doesn't cover yet.

## Next steps

1. Keep new async demos on `handle`/`with` + `lib/stdlib/async.flow`.
2. Decide whether async needs **delimited continuations** (or an explicit
   fiber/runtime API). Without that, Flow-level “suspend here” stays unavailable.
3. Grow `NetpollAsyncIO` toward fiber-parked IO; keep call sites on `AsyncIO.*`.
4. Optional later: surface sugar that desugars to effects — only if the runtime
   model is solid.

## Related

- [concurrency-vs-go.md](concurrency-vs-go.md) — tracks + Go comparison
- [replace-go.md](replace-go.md) — scorecard for replacing Go
- [Effects Showcase](../effects-showcase.md) — runnable effect demo + limitations
- [LANGUAGE_SPEC §6](../LANGUAGE_SPEC.md#6-effect-system) — effect grammar
- `lib/stdlib/async.flow` — effect declarations + capabilities
- `examples/effects/async_primitives.flow` — runnable stdlib demo
- `examples/concurrency/` — fibers, channels, netpoll, `parallel for`
