# Request and persistent lifetime domains

> **Status:** implemented in the C-backend type checker as part of epic
> [#679](https://github.com/flooooooooooow/flow/issues/679). These are the two
> Axiom §7 names that v0 of [lifetime domains](lifetime-domains.md) left out.
> The four rules (LD1–LD4) apply unchanged.

The full lattice is

```text
callback  <  frame  <  request  <  session  <  application  <  persistent
```

`request` and `persistent` are ordinary `@lifetime(...)` names. They need no
new syntax. A value still takes its domain from its allocation site.

## `request`

One inbound HTTP, RPC, or event. Longer than a render `frame`, shorter than
the `session` (connection, document, or stream) that produced it.

A request handler may allocate. That is the difference from `frame` and
`callback`:

```flow-pseudocode
@lifetime(request)
function handle(id: i32) -> i32 {
    let raw: ptr<void> = malloc(64)
    # ... use raw, then free it before return ...
    return id
}
```

A `session` function may call `handle`. A `callback` function may not.
Parking a request-local pointer in a session or application static is LD1.

## `persistent`

Storage that is intended to outlive this process run: a file-backed map, a
database handle, a durable counter. It is the longest domain, so:

- a persistent static may not hold an `application` (or shorter) reference
- an `@lifetime(application)` function may not call a persistent function
- unannotated `main` may call persistent setup, same as it may call
  application setup

```flow-pseudocode
@lifetime(persistent)
let mut hits: i32 = 0

@lifetime(persistent)
function remember(n: i32) -> i32 {
    hits = hits + n
    return hits
}
```

Same-rank calls and stores are allowed. `remember` writing `hits` is fine.

## Allocation

| Domain | Heap create/destroy | Locks |
|---|---|---|
| `callback` | forbidden (`@rt_safe`) | forbidden |
| `frame` | forbidden | allowed |
| `request` | allowed | allowed |
| `session` | allowed | allowed |
| `application` | allowed | allowed |
| `persistent` | allowed | allowed |

## Tests

Accepted program: `tests/lang/test_lifetime_request_persistent.flow`.

Rejected programs: `compiler/fixtures/typecheck_rules/domain_request_*.flow`
and `domain_application_call_persistent.flow` /
`domain_application_escape_persistent.flow`.
