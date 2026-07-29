# flow-verify: parser status vs. the `examples/verify/` corpus

> **TL;DR:** The ~270 parser failures under `examples/verify/` in
> [`examples/STATUS.md`](../../examples/STATUS.md) are not a core-Flow
> regression. They come from a proof corpus that was written *ahead of* the
> `flow-verify` parser/checker implementation, deliberately exploring notation
> (set-builder operators, Euclidean ratios, ghost/ownership contracts) that
> [`verification.md`](../language/verification.md) describes as future design,
> not shipped syntax. This document explains why, categorizes every failure,
> and gives a recommendation per category. No parser changes were made.

---

## Context

- Core Flow (the general-purpose compiled language) is unaffected: **906/1177
  (77.0%)** of the full example/app/benchmark sweep passes, and only **one**
  failure (`benchmarks/micro/nbody_benchmark.flow`, a `step` keyword clash)
  is outside `examples/verify/`.
- Within `examples/verify/` specifically: **784/1054 (74.4%) pass**. The
  `theorem` / `assume` / `therefore` keywords, 3-group claim-path syntax
  (`«Domain» «Morphism» «Facet»`), and relative-file imports already work —
  that's why the majority of the corpus compiles today.
- The **270 failures** are concentrated in files that reach for a *specific*
  extra notation the checker doesn't parse yet. Every single failure was
  traced to one of the buckets below — none require implementing the actual
  proof checker (SMT/exhaustive backends, ghost-state semantics, etc.) just to
  explain *why* parsing fails.

Regenerate this analysis at any time with:

```bash
python3 scripts/triage_verify_failures.py
```

## Failure categories (270 files)

A file can land in more than one bucket (e.g. a Finset lemma may use both
`\` and a hyphenated import), so the counts below don't sum to 270.

| # files | Category | What it looks like | Verdict |
|---:|---|---|---|
| 71 | Unicode set operators `\`, `∩`, `∪` | `card(s \ empty)`, `card(s ∩ t)` | **New binary operators + non-ASCII lexing.** Not in `verification.md`. Needs a language-design decision (ASCII fallback like `diff`/`inter`/`union`, or genuinely add non-ASCII operator glyphs to the lexer) before touching the parser. |
| 65 | Hyphenated import paths/symbols | `import .Group-inv-unique { inv-unique }` | Sibling proof files are named with hyphens (matching the filename) and imported that way, but the imported symbol is a **dependency citation that's never called** — the body always uses the full `«A» «B» «C»` claim path instead. Narrow, plausibly-safe fix (isolated to `_parse_module_path`/import-symbol-list grammar, doesn't touch expressions) — see [Recommendation](#recommendation) below. Not applied without sign-off (syntax changes require human approval per `.cursorrules`). |
| 49 | `in` as a membership expression | `if a in I { ... }`, `therefore 0 in I` | `in` is currently *only* valid inside `for x in a to b`. Turning it into a general infix membership operator needs type-checker semantics for "membership" over `Ideal`/`Subgroup`/`Finset` — this is checker work, explicitly out of scope. |
| 33 | Unbalanced parentheses | e.g. `List-len-cons-oct-nil.flow` has one fewer `)` than `cons(` calls | **Corpus bug, not a parser gap.** These are auto-generated derived-list lemmas with an off-by-one paren count. Fixing the parser wouldn't help; the fix is regenerating/hand-correcting those specific files. |
| 32 | List append operator `++` | `(xs ++ ys) ++ zs` | New binary operator, not in the spec. Same category as `\`/`∩`/`∪` — needs a design decision, not a parser hack. |
| 9 | `assume` of a bare fact (not a claim-path call) | `assume segment_AB == segment_DE`, `assume Common Notion 4: things coinciding …` | The parser's `assume` grammar is `assume <claim-path>` or `assume <claim-path>(args)` only (see `parse_assume` in `src/flow/parser.py`). These Euclid-style files want `assume` to accept an arbitrary boolean expression or a freeform prose citation — a materially different, unspec'd grammar for `assume`. |
| 8 | Operator-suffixed module path (`Nat/+`) | `import verify.Nat/+ { zero-left }` | Embeds an operator glyph inside a module-path segment. Overlaps with the `CLAIM_PATH` token's `Domain/op.facet` grammar, but as an *import path* rather than an inline reference — not handled by `_parse_module_path`. |
| 8 | Non-triple guillemet claim coordinate | `x : «Ring» «Nat»`, `«Ring» «mul»(x, 1)` | The lexer only recognizes exactly **3** consecutive `«...»` groups (`CLAIM_COORDINATE`). These files reuse the notation with 2 groups as a pseudo-type or a 2-arg call; a lone `«` outside a valid triple isn't a token, so lexing fails immediately. Would need a distinct 2-group token + parsing rule + type-system meaning — undefined today. |
| 1 | `and`/`or` keywords in expressions | `result.Sum == expected.sum and result.Cout == ...` | Flow uses `&&`/`||`. Trivial in isolation, but this file (`circuits/full_adder.flow`) also uses `by exhaustive` below, so it wouldn't parse anyway. |
| 1 | `by <tactic>` proof-automation suffix | `therefore x == y by exhaustive` | Explicitly **Phase 3** in `verification.md`'s implementation-phases table ("SMT / exhaustive backends") — deliberately not built yet. |
| 1 | `:` as a ratio/proportion operator | `therefore area(ABC) : area(DEF) == base_BC : base_EF` | Euclid's classical `A : B` ratio notation. `:` today only means type annotation / struct-field separator. |
| 1 | `has property` contract clauses | `has property ring_size(rb) == old(ring_size(rb)) + 1 after` | File header literally says `# Status: design example (syntax not yet implemented)`. `has property` is the 4th keyword named in `verification.md` but has no parser support yet (needs `before`/`after`/`old(...)` too). |
| 1 | `ghost type` declarations | `ghost type Queue<T> { ... }` | Same file as above; model/ghost-state types aren't in the grammar. |
| 1 | `mod` keyword operator | `(write_idx - read_idx) mod capacity` | Same file; Flow spells this `%`. |
| 1 | Non-ASCII identifier | `let σ = arbitrary_memory()` | File header says `# Status: design example (syntax not yet implemented)`. The lexer's `IDENTIFIER` pattern is ASCII-only. |

Raw parser error strings (from `examples/STATUS.md`) mapped onto these
categories, for cross-reference:

| Raw error | Count | Maps to |
|---|---:|---|
| `Unexpected character` | 78 | unicode set ops (71) + non-triple guillemet (8, some overlap) |
| `Unexpected declaration: TokenType.MINUS` | 59 | hyphenated import paths |
| `Expected TokenType.LBRACE, got TokenType.IN` | 47 | `in` as membership (the `if a in I {` shape) |
| `Unexpected token in expression: TokenType.PLUS` | 32 | `++` append |
| `Expected TokenType.RPAREN, got TokenType.RBRACE` | 17 | unbalanced parens (corpus typo) |
| `Unexpected token in expression: TokenType.RPAREN` | 11 | unbalanced parens (corpus typo) |
| `Unexpected declaration: TokenType.SLASH` | 7 | operator-suffixed module path |
| `Unexpected token in expression: TokenType.COLON` | 5 | freeform `assume` (Euclid `Postulate N:` citations) |
| `Unexpected token in expression: TokenType.EQUALS` | 5 | freeform `assume` (bare `==` fact) |
| `Expected TokenType.RPAREN, got TokenType.ASSUME` | 3 | unbalanced parens (corpus typo) |
| `Unexpected token in expression: TokenType.IN` | 2 | `in` as membership (the `therefore 0 in I` shape) |
| `Expected TokenType.RPAREN, got TokenType.THEREFORE` | 2 | unbalanced parens (corpus typo) |
| `Unexpected token in expression: TokenType.AND` | 1 | `and`/`or` keywords |
| `Expected TokenType.COLON, got TokenType.IDENTIFIER` | 1 | `has property` / `ghost type` / `mod` |

(There's also 1 failure outside `examples/verify/`:
`benchmarks/micro/nbody_benchmark.flow` uses `step` as a variable name, which
collides with a reserved word — unrelated to this corpus, tracked separately
in `examples/STATUS.md`.)

## Recommendation

**Do not add parser stubs for these as a batch.** Per the task constraints and
`.cursorrules` ("syntax choices are a human decision"), none of these
categories are "add 3-4 keywords and unblock most of the corpus":

- The two biggest buckets (`\`/`∩`/`∪` set operators, hyphenated imports) are
  each ~25% of the failures on their own, but every bucket needs either (a) a
  genuinely new operator/grammar rule with real type-checker semantics
  (membership, ratios, non-ASCII operators), which is explicitly "the full
  checker" this task says not to build, or (b) isn't a parser gap at all
  (corpus typos).
- The one candidate that *looks* narrow and low-risk — accepting hyphens in
  `import <path> { <symbols> }` — is scoped to a single, non-expression
  grammar production and wouldn't touch general identifier/expression parsing
  elsewhere. It would recover ~65-73 files (~25-27%). It is flagged as an open
  design question in [`Questions.md`](../../Questions.md) rather than
  implemented, since it's still a syntax change and outside this task's
  scope to unilaterally decide.

**What to do instead (this task's output):**

1. `scripts/triage_verify_failures.py` — re-runnable triage tool; rerun it
   after any parser change to see which buckets shrink.
2. This document, cross-linked from `examples/STATUS.md`'s header and
   `ROADMAP.md`'s "what's broken" section, so the 270 number reads as
   "corpus ahead of checker" rather than "270 compiler bugs."
3. An open question in `Questions.md` about whether to special-case hyphens
   in import paths.

## Related reading

- [`docs/language/verification.md`](../language/verification.md) — the
  4-keyword design spec (`theorem`, `assume`, `therefore`, `has property`)
  and its 5-phase implementation plan (we're mid Phase 1/2).
- [`docs/third-party/flow-verify.md`](flow-verify.md) — package overview;
  already states `theorem`/`assume`/`therefore`/`has property` are "four
  **planned** verification keywords."
- [`docs/third-party/README.md`](README.md) — third-party package index.
