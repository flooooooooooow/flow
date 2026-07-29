# Async via Effects (Design Note)

Flow models asynchronous / concurrent I/O with **algebraic effects**, not with
`async` / `await` keywords. Call sites perform effect operations; a capability
(handler) supplies the scheduler or OS backend.

This matches the comparison table in [docs/comparison.md](../comparison.md):
async is “modeled via effects (no `async` keyword).”

## Intent

```flow
effect Async {
    delay(ms: i32) -> void,
    spawn(task_id: i32) -> void,
    await_task(task_id: i32) -> i32,
}

# Business logic depends only on the effect — swap Sync vs real I/O handlers
function fetch_user(user_id: i32) -> i32 {
    Async.delay(100)
    return user_id * 10
}
```

Stdlib sketch: `lib/stdlib/async.flow` declares `AsyncIO` / `TcpEffect` with a
blocking stub capability — swap for epoll/kqueue/IOCP later without changing
call sites.

Runnable-but-limited demo: `examples/effects/async_effects.flow` (uses the older
`capability Async` **parameter** style).

## Current limitations

From [docs/effects-showcase.md](../effects-showcase.md) (honest limitations) and
the async examples:

| Limitation | Impact on async |
|------------|-----------------|
| **No resumable / one-shot continuations** | Handlers are tail-resumptive only — cannot encode a real scheduler, generators, or “suspend here / resume later” without a different runtime |
| **`capability Effect` parameter style does not link** | `async_effects.flow` (and older DI/state examples) transpile under the harness but fail C link under `./flow run` |
| **No effect typing / `--strict` for effects** | Signatures do not declare performed effects; unhandled ops become silent zeros |
| **Handlers are largely stateless** | Hard to build a collecting task table or metrics spy without workarounds |
| **Stdlib `async.flow` is a stub** | `BlockingAsyncIO` no-ops; no epoll/kqueue/IOCP backend yet |

Working pattern today: `handle … with …` + `capability` declarations as in the
effects showcase — compiles and runs end to end for sync effect demos, not for
true async scheduling.

## Next steps

1. Prefer `handle`/`with` for any new async demos; fix or retire the parameter-style
   examples once the C backend emits definitions for `capability` parameters.
2. Decide whether async needs **delimited continuations** (or an explicit
   fiber/runtime API). Without that, “async effects” stay pedagogical.
3. Grow `lib/stdlib/async.flow`: real poll/sleep backends behind the same
   `AsyncIO` effect; keep call sites backend-agnostic.
4. Optional later: surface sugar that desugars to effects — only if the runtime
   model is solid; do **not** add bare `async`/`await` keywords first
   ([ROADMAP](../../ROADMAP.md) still lists effects-based async primitives as open).

## Related

- [Effects Showcase](../effects-showcase.md) — runnable effect demo + limitations
- [LANGUAGE_SPEC §6](../LANGUAGE_SPEC.md#6-effect-system) — effect grammar
- `lib/stdlib/async.flow` — effect declarations
- `examples/effects/async_effects.flow` — historical async-as-effects sketch
