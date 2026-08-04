# Async via Effects

Flow models asynchronous / concurrent work with **algebraic effects**, not with
`async` / `await` keywords. Call sites perform effect operations; a capability
(handler) supplies the backend (sync simulator, blocking sleep, or — later —
a real event loop).

This matches the comparison table in [docs/comparison.md](../comparison.md):
async is “modeled via effects (no `async` keyword).”

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

Business logic depends only on the effect — swap `SimulatedAsync` vs a future
epoll/kqueue capability without changing call sites.

## Implemented (this slice)

| Piece | Status |
|-------|--------|
| `lib/stdlib/async.flow` — `Async` effect (`delay`, `spawn`, `join`) | ✅ |
| Helpers `async_delay` / `async_spawn` / `async_join` / `async_sleep_ms` / `async_poll_read` | ✅ |
| `SimulatedAsync` capability — deterministic sync stand-in | ✅ |
| `AsyncIO` effect + `BlockingAsyncIO` (`sleep_ms` → `usleep`; poll stubs return ready) | ✅ |
| `TcpEffect` declaration (ops only; no capability yet) | ✅ stub |
| Runnable demo: `examples/effects/async_primitives.flow` (`./flow run`) | ✅ |
| Runtime test: `tests/runtime/test_async_primitives.flow` | ✅ |
| Preferred install style: `handle … with …` (same as effects showcase) | ✅ |

### Semantics today (honest)

- **Tail-resumptive only.** Every op returns straight to the call site. There is
  no “suspend here / resume later,” no fiber table, no work-stealing scheduler.
- **`SimulatedAsync` is stateless.** Capabilities have no `self` / task map, so
  `spawn` is a no-op marker and `join(task_id)` returns `task_id * 10` as a
  deterministic stand-in for a completed task result.
- **`BlockingAsyncIO.sleep_ms`** blocks the calling thread via POSIX `usleep`
  when `ms > 0`. `poll_read` / `poll_write` ignore the timeout and return `1`
  (ready) — not a real poller.
- **Unhandled ops** still default to zero / no-op (same as the rest of the
  effect system).

## Deferred

| Item | Why deferred |
|------|----------------|
| Resumable / one-shot continuations | Needed for a real scheduler, generators, cancel; not in the C backend yet |
| Fiber / task runtime | Would invent a runtime not patterned elsewhere in the repo |
| epoll / kqueue / IOCP backends behind `AsyncIO` | OS event loops; keep the effect surface stable until then |
| `TcpEffect` capability | Needs real sockets + the poll backend above |
| Effect-row typing / `--strict` for performed effects | Broader effect-system work ([effects showcase limitations](../effects-showcase.md)) |
| `async` / `await` syntax sugar | Only after the runtime model is solid — do **not** add keywords first |
| Stateful handlers (`capability` with mutable task tables) | Capabilities are currently stateless; use struct+`impl` workarounds elsewhere |

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
   fiber/runtime API). Without that, “async effects” stay pedagogical +
   blocking-sleep helpers.
3. Grow `BlockingAsyncIO` (or a sibling) into a real poll backend; keep call
   sites on `AsyncIO.*` unchanged.
4. Optional later: surface sugar that desugars to effects — only if the runtime
   model is solid ([ROADMAP](../../ROADMAP.md) marks async primitives partial).

## Related

- [Effects Showcase](../effects-showcase.md) — runnable effect demo + limitations
- [LANGUAGE_SPEC §6](../LANGUAGE_SPEC.md#6-effect-system) — effect grammar
- `lib/stdlib/async.flow` — effect declarations + capabilities
- `examples/effects/async_primitives.flow` — runnable stdlib demo
- `examples/effects/async_effects.flow` — Timeout/Retry as policy effects
