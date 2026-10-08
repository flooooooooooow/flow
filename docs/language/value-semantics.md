# Value semantics and inferred moves

> **Status:** Implemented on the C backend. Structs and other by-value
> types copy on assignment and at function boundaries. The compiler may
> treat a **last use** of a uniquely owned binding as a move and elide the
> intermediate copy. There is no `move` keyword. Copy-on-write and implicit
> sharing are not inferred; see
> [Questions.md](../project/Questions.md#2026-10-07-last-use-moves-without-a-move-keyword-or-cow).

Flow's observable model is **value semantics**. `let q = p` and `foo(p)`
give `q` and the callee their own values. Mutating one copy never changes
the other:

```flow
struct Point {
    x: i32,
    y: i32
}

function copied_point() -> i32 {
    let p: Point = Point { x: 3, y: 4 }
    let mut q: Point = p
    q.x = 10
    return p.x
}
```

`copied_point` returns `3`. Sharing identity is explicit: `ptr<T>` or
`span<T>`.

## Last-use moves

A full copy of a large struct is the safe default. When the compiler can
prove that a function-scoped `let` or by-value parameter is **uniquely
owned** and that a particular mention is its **last use**, it may lower
that mention as a move.

The case that pays off today is a record update of such a binding:

```flow
struct Point {
    x: i32,
    y: i32
}

function bump(p: Point) -> Point {
    return Point { ..p, x: 5 }
}

function consume(p: Point) -> i32 {
    return p.x + p.y
}

function last_use_arg(p: Point) -> i32 {
    return consume(Point { ..p, x: 9 })
}
```

Neither function needs a source-level `move`. In `last_use_arg`, `p` is
dead after the update, so the C backend writes the new field onto `p` and
passes `p` itself. `bump` returns through the caller's destination
([copy elision](copy-elision.md), #732): `p` is copied once into that
slot and the field is written there. The caller still owns its own `p`,
so a later read of the caller's `p` sees the original fields.

A last-use move is withheld unless every check below succeeds. Any doubt
keeps the copy.

| Required | Refused when |
|---|---|
| Function-scoped `let` or by-value parameter | Module static, `const`, or unresolved name |
| Not captured by a lambda | The name is in the current capture set |
| Address not taken | `&p` or `&p.field` appears in the function |
| No pending `defer` | A defer is still in scope at the use |
| Last use on this path | A later statement on the same continuation mentions `p` |
| Not a repeating loop use | The use is inside `while` / `for` and does not return |
| Update values do not read the base | `Point { ..p, x: p.y }` (would clobber `p.y`) |
| No other mention in the same statement | `foo(Point { ..p, x: 1 }, p)` |

Path-sensitive last-use: a use in the `then` branch of `if` does not see
the `else` branch as a later mention. A `return` ends the path, so a
returned last use is always last on that path (including `return` from
inside a loop).

```flow
struct Point {
    x: i32,
    y: i32
}

function consume(p: Point) -> i32 {
    return p.x + p.y
}

function branched(p: Point, c: i32) -> i32 {
    if c == 1 {
        return consume(Point { ..p, x: 7 })
    }
    return p.x
}

function still_live(p: Point) -> i32 {
    let n: i32 = consume(Point { ..p, x: 8 })
    return n + p.x
}
```

`branched` may move on the `c == 1` path. `still_live` must copy: `p.x`
is read after the update.

## What this is not

- **Not a `move` keyword.** Source still writes ordinary uses. The
  rewrite is a lowering default, not a new ownership transfer in the
  language.
- **Not use-after-move.** Because a move is only applied when the binding
  is dead, later mentions are not errors; they simply keep the copy.
- **Not copy-on-write or implicit sharing.** Two live bindings stay
  independent values. Sharing is `ptr` / `span`.
- **Not destination-passing for every aggregate.** Constructing a record
  update into a `let`, an assignment target, or a returned local is
  [copy elision](../LANGUAGE_SPEC.md#81-value-semantics) on the C
  backend (`#732`). Last-use analysis is the `#696` input to that
  lowering. By-value ABI copies at function boundaries remain.

## Tests

- Runtime: `tests/lang/test_move_inference.flow`
- Generated C: `tests/cgen/move_inference.flow`
