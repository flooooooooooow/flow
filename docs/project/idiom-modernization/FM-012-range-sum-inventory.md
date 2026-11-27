# FM-012 slice 5: arithmetic progression sums

Evidence for #1787, pinned to main revision `f5ea0f9a917efefbde71a3d9acbefefda6b5fcba`. Companion to [evolution](FM-012-flow-evolution-inventory.md), [dynamics and fields](FM-012-dynamics-field-inventory.md), [algebraic equations](FM-012-algebraic-dae-mna-inventory.md) and [derivatives](FM-012-symbolic-derivative-inventory.md). This is a discovery slice, not a language change.

## Native syntax and lowering

| Construct | Parser anchor in compiler/src/parser.flow | Lowering evidence | Positive fixture |
|---|---|---|---|
| `sum(a..b)` | 763–771; `flowc_parse_range_tail:1637–1666` synthesizes AST_INT 1 when step omitted | C `__flowc_range_sum`; MLIR literal folding or helper | `tests/lang/test_range_sum_step.flow:7–9,52–54` |
| `sum(a..b step s)` | 763–771, 1647–1655 | C generator 9163–9195 and 16320–16330 | Same test, 11–29 and 55–85 |
| `sum(a..b step s &#124; c..d step t)` | 772–791, AST_CALL ival=3 | C `__flowc_range_sum_union` (16356–16358); inclusion-exclusion | `tests/lang/test_range_algebra.flow:67–69,79–88` |
| `sum(a..b step s & c..d step t)` | 772–791, AST_CALL ival=4 | C `__flowc_range_sum_isect` (16336–16355); CRT and LCM | Same test, 70–72 |

The parser stores three or six arguments in AST_CALL and an ival discriminator of 2, 3 or 4 (802–813), not a first-class range value. Bounds after the initial start parse at equality precedence via `flowc_parse_range_bound:1628–1634`; the initial start is parsed by `flowc_parse_expr` (761). The typecheck built-in name recognition in `compiler/src/typecheck.flow:460–463` recognizes sum; detailed argument-type acceptance and result-type diagnostics were not audited.

For nonempty progressions with n terms, first term a and signed stride s, the sum is n*a + s*n*(n-1)/2. The C emitter passes arguments cast to int64_t and casts the result to the type derived from the initial bound expression (9166–9195). This is not an arbitrary-precision guarantee: intermediate overflow and extreme integer bounds are unverified. The C helper treats zero stride or an empty direction as count zero (16321–16326). The end is exclusive for both signs of stride.

For two ranges, the common progression is found using extended Euclid/CRT, bounded by the intersection of their extent, and stepped by LCM. Union subtracts the intersection once. No enumeration of each element is emitted.

## Backend distinction

`compiler/src/mlirgen.flow:6411–6413` dispatches to `mrs_emit`. `mrs_fold:20774–20820` folds literal arguments, and `mrs_emit:20834–20872` emits an i32 constant or redirects the call to __flow_sum_range, __flow_sum_range_union or __flow_sum_range_isect. This differs from the C source emitter, which emits helpers even for literal arguments (downstream optimization may fold them).

The tracked `compiler/mlir_vs_c/failures.txt:797–798` records both language tests as mlir-lower failures involving an unknown custom op. This is an existing snapshot, not a new run, and it does not establish the current underlying cause of failure. Do not infer runtime parity merely from the emitter implementation.

## Behavioral and negative evidence

The single-range test checks default, non-unit, positive offset and descending strides, wrong direction, runtime zero stride, a 1,500,013,378 result fitting i32 despite a larger intermediate, and one evaluation per argument (51–94). The two-range test compares both operations against brute force over 500 deterministic parameter combinations (skipping zero strides) and tests exactly six bound calls for a union (56–89).

The parser accepts at most one set operator and then requires TOK_RPAREN (772–801). Chained unions/intersections are therefore not established even for literals; precedence for chained range operators is not implemented by this branch. A dedicated rejection fixture was not located in this slice. The negative evidence is the parser's required closing parenthesis. The existing docs are corrected to remove the historical eight-range, parse-time folding and unconditional zero-stride-diagnostic claims.

Plain function declarations are not an equation syntax: `flowc_parse_function:2999–3026` parses an optional return type and effect row, followed by a brace body or a forward declaration; no equals-expression body is parsed there. Other shorthand forms elsewhere in the frontend remain unverified.

## Verification

Source and fixtures inspected at the pinned revision. Existing test files establish intended behavior but were not re-executed in this workspace. Commands for follow-up verification:

```sh
./flow run tests/lang/test_range_sum_step.flow
./flow run tests/lang/test_range_algebra.flow
./flow tool doc_links
./flow tool script_refs
./flow tool wiki_nav
```

No compiler, generated artifacts, fixtures or tests changed. Documentation gates pending PR CI.
