# Lifetime domains through struct fields and collections

> **Status:** implemented in the C-backend type checker (issue #684).
> The v0 domain checker tracked direct locals and module statics. This
> page is the composite-storage extension: a reference stored in a field
> or collection element keeps its lifetime-domain constraint.

A longer-lived domain may not hold a reference to a shorter-lived one.
That axiom already rejected `tail = scratch` when `tail` was a static.
It now also rejects the same store when it goes through a field path, an
array element, or a struct/array literal, and it rejects a store into a
field that declares its own longer-lived `@lifetime(D)`.

The full domain order, allocation rules (LD3) and call-order rule (LD4)
stay on [lifetime-domains.md](lifetime-domains.md). This page is only
the storage-propagation rules.

## How a field gets a domain

| Storage | Domain |
|---|---|
| any field or element of a module static | the static's domain (default `application`) |
| a field declared `@lifetime(D)` | `D`, wherever the instance lives |
| an unannotated field of a local struct | none: unchecked, because the struct dies with the frame |

Both halves are opt-in. A store fires only when the writing function
declares a domain, the target's domain outlives it, and the value is
rooted in the writing frame.

## Static-rooted composites (LD1)

A reference stored anywhere inside a module static is an escape, at any
field depth or through an array element:

```flow expect-error
struct Holder { view: ptr<i32> }

let mut holder: ptr<Holder> = null

@lifetime(callback)
function process() -> void {
    let scratch: array<i32, 4> = [1, 2, 3, 4]
    holder[0].view = &scratch
}
```

```text
error: lifetime domain escape: `scratch` lives in the `callback` domain but is
       stored in `holder`, which lives in the `application` domain (a
       longer-lived domain may not hold a reference to a shorter-lived one)
```

The same diagnostic names the static for `holder[0].inner.view = &scratch`,
`table[0][0] = &scratch`, `holder[0].items[0] = &scratch`, and
`holder[0] = Holder { view: &scratch }`. Module statics that hold a
composite are a `ptr<T>` (the language does not allow a struct-typed
module static).

A local unannotated struct is not an escape: it lives exactly as long as
the reference it receives.

## Field-declared domains (LD5)

`@lifetime(D)` on a struct field is a contract that the field holds a
`D`-domain reference. A shorter-lived store breaks it wherever the
instance lives:

```flow expect-error
struct Holder {
    @lifetime(application)
    view: ptr<i32>
}

@lifetime(callback)
function process() -> void {
    let mut h: Holder = Holder { view: null }
    let scratch: array<i32, 4> = [1, 2, 3, 4]
    h.view = &scratch
}
```

```text
error: lifetime domain escape: `scratch` lives in the `callback` domain but is
       stored in field `view`, which is declared to live in the `application`
       domain (a longer-lived domain may not hold a reference to a
       shorter-lived one)
```

The check follows one pointer indirection (`h[0].view` where
`h: ptr<Holder>`), a span local that already borrowed the array, a
struct-literal field (`Holder { view: &scratch }`), and a record update.

A field whose domain does not outlive the writer, a same-domain field, a
plain `i32` field, a store of a longer-lived reference (`&g` into an
application field), and any store inside an unannotated function stay
legal.

The annotation is erased before codegen. A field `@lifetime` leaves no
trace in the C.

## Returning a composite

Returning a struct or array literal that contains a reference into the
function's own frame is the same escape as returning the reference
directly (LD2):

```flow expect-error
struct Holder { view: ptr<i32> }

@lifetime(callback)
function build() -> Holder {
    let scratch: array<i32, 4> = [1, 2, 3, 4]
    return Holder { view: &scratch }
}
```

## Pointer-parameter targets fail closed

A pointer/span parameter is caller-owned storage whose pointee lifetime is
not bounded by the callee. A domain-local reference therefore cannot be
stored through an **unannotated** parameter target:

```flow expect-error
struct Holder { view: ptr<i32> }

@lifetime(callback)
function fill(out: ptr<Holder>) -> void {
    let scratch: array<i32, 4> = [1, 2, 3, 4]
    out[0].view = &scratch
}

function main() -> i32 { return 0 }
```

The same rule covers a whole-composite assignment such as
`out[0] = Holder { view: &scratch }`. An explicit field contract at the
same or shorter domain remains legal: for example an
`@lifetime(callback) view: ptr<i32>` field can receive a callback-local
reference through `ptr<BoundHolder>`.

## What is still not checked

- Copying a local struct that was previously filled with a short-lived
  reference (`holder = local`) without a literal on the right-hand side.
- Escape through a closure, a function pointer, the heap, or pointer
  laundering. Same gaps as [lifetime-domains.md](lifetime-domains.md).

## Related

[Lifetime domains](lifetime-domains.md) ·
[Spans](spans.md) ·
[LANGUAGE_SPEC §8.4](../LANGUAGE_SPEC.md#84-lifetime-domains)

Tests: `compiler/fixtures/typecheck_rules/domain_field_*.flow`,
`domain_array_*.flow`, `domain_ld5_*.flow`, `domain_return_struct.flow`,
`tests/lang/test_domain_fields.flow`
