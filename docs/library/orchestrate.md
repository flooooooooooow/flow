# std.orchestrate

Composition combinators for the Structural Orchestration Algebra (#723).
Per the 2026-10-07 decision in [Questions](../project/Questions.md),
orchestration starts as a library with no new syntax. Syntax is decided
later from real use, and if it comes it uses a dedicated operator or
keyword.

```flow
import std.orchestrate { seq_i32, fanout2_i32, Fanout2_i32 }
```

The file form `import "stdlib/orchestrate.flow"` also works.

Branches run one after another on the calling thread, in source order.
Function-typed generic parameters do not lower to C yet, so the
combinators are concrete: `i32` and `f32` values, and `Result_i32_string`
from `stdlib/result.flow` for failure.

## Sequencing

`seq_i32(f, g, a)` is `g(f(a))`. `seq_f32` is the same for `f32`.

```flow
import std.orchestrate { seq_i32 }

function add_one(x: i32) -> i32 { return x + 1 }
function times_two(x: i32) -> i32 { return x * 2 }

let r: i32 = seq_i32(add_one, times_two, 10)   # 22
```

## Fan-out

`fanout2_i32(f, g, a)` runs both functions on `a` and returns a record
with one field per branch. `fanout3_i32`, `fanout2_f32` and `fanout3_f32`
follow the same pattern.

```flow
import std.orchestrate { fanout2_i32, Fanout2_i32 }

function add_one(x: i32) -> i32 { return x + 1 }
function times_two(x: i32) -> i32 { return x * 2 }

let f2: Fanout2_i32 = fanout2_i32(add_one, times_two, 10)
# f2.v0 == 11, f2.v1 == 20
```

## Failure

`seq_result_i32(f, g, a)` calls `g` only when `f` succeeds and otherwise
returns `f`'s error.

`fanout2_result_i32(f, g, a)` runs both branches and keeps both results.
Two joins combine them:

| Join | Result |
|---|---|
| `join2_result_i32` | `Joined2_i32` with `ok`, both values and `error`. Every branch must succeed; otherwise the error is the first failed branch in source order. |
| `join2_first_ok_i32` | The first successful branch in source order, for an optional branch with a fallback. The last branch's error when none succeeds. |

The error choice depends only on branch order, never on timing.

```flow
import "stdlib/orchestrate.flow"
import "stdlib/result.flow"

function must_be_positive(x: i32) -> Result_i32_string {
    if x <= 0 { return err_i32("not positive") }
    return ok_i32(x)
}
function div_by_two(x: i32) -> Result_i32_string {
    if x % 2 != 0 { return err_i32("not even") }
    return ok_i32(x / 2)
}

let j: Joined2_i32 = join2_result_i32(fanout2_result_i32(must_be_positive, div_by_two, 8))
# j.ok, j.v0 == 8, j.v1 == 4
```

## Not yet covered

Concurrent branches, deadlines, retry, quorum, race, cancellation,
transactions and compensation from the #723 design are future work. The
syntax question is tracked in ROADMAP.md.

Tests: `tests/lang/test_orchestrate.flow`.
