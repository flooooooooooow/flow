# flow-verify: parser status vs. the `examples/verify/` corpus

> **TL;DR:** Most remaining failures under `examples/verify/` in
> [`examples/STATUS.md`](../../examples/STATUS.md) are not a core-Flow
> regression. They come from a proof corpus written *ahead of* the
> `flow-verify` checker, exploring notation (set-builder operators, Euclidean
> ratios, ghost/ownership contracts) that
> [`verification.md`](../language/verification.md) describes as future design.
> Regenerate this analysis with `python3 scripts/triage_verify_failures.py`.

---

## Context (2026-08-04)

- Full sweep (`examples/` + `apps/` + `benchmarks/`): **985/1192 (82.6%)** pass
  (`examples/STATUS.md`).
- Within `examples/verify/` specifically: **848/1054 (80.5%)** pass.
- Already shipped for this corpus:
  - `theorem` / `assume` / `therefore`, 3-group claim coordinates
  - Hyphenated import paths/symbols (`import .Group-inv-unique { inv-unique }`)
  - Operator-suffixed morphism imports (`import verify.Nat/+ { zero-left }`)
    resolving to `lib/verify/Nat.flow`
  - Citation-only brace lists on verify modules (facet names need not match
    declaration symbols)

## Failure categories (206 files)

A file can land in more than one bucket, so counts need not sum to 206.

| # files | Category | What it looks like | Verdict |
|---:|---|---|---|
| 71 | Unicode set operators `\`, `∩`, `∪` | `card(s \ empty)`, `card(s ∩ t)` | **New binary operators + non-ASCII lexing.** Needs a language-design decision before touching the parser. |
| 49 | `in` as a membership expression | `if a in I { ... }`, `therefore 0 in I` | `in` is only valid inside `for x in a to b`. Membership over Ideal/Subgroup/Finset is checker work. |
| 33 | Unbalanced parentheses | e.g. `List-len-cons-oct-nil.flow` | **Corpus bug**, not a parser gap. |
| 32 | List append operator `++` | `(xs ++ ys) ++ zs` | New binary operator, needs a design decision. |
| 9 | `assume` of a bare fact | `assume segment_AB == segment_DE` | `assume` only accepts claim-path forms today. |
| 8 | Non-triple guillemet claim coordinate | `x : «Ring» «Nat»` | Lexer only recognizes exactly **3** `«...»` groups. |
| 2 | Residual hyphenated-import tags | (heuristic overlap) | Hyphen imports parse; these files still fail for another bucket. |
| 1 each | `and`/`or`, `by <tactic>`, `:` ratio, `has property`, `ghost type`, `mod`, non-ASCII id | various | Specced as future / design examples. |

Raw parser error strings (from latest triage):

| Raw error | Count | Maps to |
|---|---:|---|
| `Unexpected character` | 80 | unicode set ops + non-triple guillemet |
| `Expected TokenType.LBRACE, got TokenType.IN` | 47 | `in` as membership |
| `Unexpected token in expression: TokenType.PLUS` | 32 | `++` append |
| `Expected TokenType.RPAREN, got TokenType.RBRACE` | 17 | unbalanced parens |
| `Unexpected token in expression: TokenType.RPAREN` | 11 | unbalanced parens |
| `Unexpected token in expression: TokenType.COLON` | 5 | freeform `assume` / ratios |
| `Unexpected token in expression: TokenType.EQUALS` | 5 | freeform `assume` |
| other | ≤3 each | see triage output |

**Gone since earlier triage:** `Unexpected declaration: TokenType.MINUS`
(hyphenated imports) and `Unexpected declaration: TokenType.SLASH`
(operator-suffixed `Nat/+` imports).

## Recommendation

Do **not** batch-add parser stubs for set operators, `++`, membership `in`,
or freeform `assume` without a design decision (see `.cursorrules`).

Narrow, already-shipped fixes worth keeping:

1. Hyphenated import path/symbol segments
2. Operator-suffixed module-path segments + resolve `Domain/op` → `Domain.flow`
3. Citation-only symbol lists for `lib/verify` / `examples/verify` modules

**What to do instead for the rest:**

1. Re-run `scripts/triage_verify_failures.py` after parser changes
2. Keep this document linked from `examples/STATUS.md`
3. Open design questions for set ops / `++` / membership before implementing

## Related reading

- [`docs/language/verification.md`](../language/verification.md)
- [`docs/language/epistemology.md`](../language/epistemology.md), `verify.Nat/+` addresses
- [`docs/language/modules.md`](../language/modules.md)
- [`docs/third-party/flow-verify.md`](flow-verify.md)
