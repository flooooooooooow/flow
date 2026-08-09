# C function-pointer call-through

> **Status**: ⚠️ runtime escape hatch (implemented). First-class language
> support is ❌ planned.
>
> **Requested by**: doom-flow (Doom port), thinkers, map traversers, draw
> column/span callbacks, and atexit handlers all store raw C `void*`
> function pointers that must be invoked from Flow.

## Problem

Flow today:

| Can | Cannot |
|-----|--------|
| Pass a named `@flow_api` / function value **to** C as `ptr<void>` | Cast `ptr<void>` **to** a C function type |
| Call Flow fat-pointer closures `(T) -> R` (`.fn` / `.env`) | Call through an opaque C ABI function pointer |

Strict typecheck rejects `ptr<void> as (ptr<void>) -> void` and there is no
expression-call form for an arbitrary callee.

Re-emitting `extern` prototypes for libc names like `remove` / `rename` /
`mkdir` also clashes with system headers (approximate Flow types vs real
`const char *` / `mode_t` decls).

## Current solution (this release)

Always-linked `runtime/flow_rt_support.c` trampolines, imported from
`lib/runtime/c_call.flow`:

```flow
extern {
    function flow_rt_call_void(fn: ptr<void>) -> void
    function flow_rt_call_p1(fn: ptr<void>, arg: ptr<void>) -> void
    function flow_rt_call_p2(fn: ptr<void>, a: ptr<void>, b: ptr<void>) -> void
    function flow_rt_call_p1_bool(fn: ptr<void>, arg: ptr<void>) -> i32
    function flow_rt_call_p3_bool(fn: ptr<void>, a: ptr<void>, x: i32, y: i32) -> i32
    function flow_rt_errno() -> i32
    function flow_rt_errno_is_isdir() -> i32
    function flow_rt_error_popup(msg: string) -> void
}
```

Plus extern hygiene: the C backend skips re-declaring common POSIX names
already covered by system headers (`mkdir`, `rename`, `unlink`, `remove`, …).

## Requested language feature

1. A **raw C function-pointer type**, distinct from fat-pointer `(T)->R`
   (e.g. `cfn<(ptr<void>) -> void>` or allowing `ptr<void> as …` to a
   non-capturing function type).
2. **Call-through** for values of that type.
3. Lowering to a bare C cast-call: `((R(*)(T…))p)(args)`.
4. Keep extern hygiene (do not re-emit prototypes that conflict with libc).

Until then, `flow_rt_call_*` is the supported API.
