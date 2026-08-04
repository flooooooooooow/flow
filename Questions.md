# Flow Development Questions

This file tracks questions that need human resolution before the AI can proceed.

Format:
- Questions are added by AI when uncertain
- Answers are added by human
- Resolved questions move to the archive at the bottom

---

## Open Questions

### 2026-08-04: Declarative ordering — Phase 2 scope

**Context:** Phase 1 shipped (`docs/language/ordering.md`): `xs |> sort`,
`sort by` / `sortBy [asc .f, desc .g]`, `stable`/`unique`/`descending`,
plus parsed-but-ignored policies (`parallel`, `gpu`, `with entropy`, …).
C backend lowers to in-place stable insertion on `array<T, N>`.

**Open decisions for Phase 2:**
1. **`unique` length** — keep compact-in-place with stale tail (current), or
   return `(array, len)`, or shrink via slices?
2. **Entropy** — first-class effect (`with entropy`) vs optional seed arg only?
3. **`order { }` block** — required sugar, or keep pipeline-only?
4. **Copy vs mutate** — pipeline looks pure; today is in-place. Pure
   `sorted` copy as default?

**Recommendation:** Keep Phase 1 semantics; decide (1) and (4) before
advertising `unique` widely; defer GPU/distributed until adaptive selector
exists.

**Status:** 🔲 Pending (Phase 1 implemented 2026-08-04)

---

### 2026-08-04: Dynamics DSL namespace style

**Context:** Top-level bare keywords `dsys` / `horizon` / `sense` / `ga` /
`analyze` / `closed` collide with ordinary identifiers and the vision-layer
`analyze Name { }` form. Editors need a clear namespace for IntelliSense.

**Options:**
1. Additive `dyn.` / `dynamics.` prefixes + `dynamics { … }` block (bare forms kept)
2. Require namespace only; deprecate bare keywords
3. No syntax change — IntelliSense-only labeling

**Recommendation:** Option 1 (shipped). Bare forms remain; prefer namespaced
forms in new code. See `docs/language/dynamics-dsl.md` § Namespaces and
`examples/dynamics/ga_dsys_namespaced.flow`.

**Status:** ✅ Resolved (Option 1 implemented 2026-08-04)

---

### 2026-01-09: Web Playground Debugging Support

**Context:** The web playground exists (`docs/playground/index.html`) but doesn't have debugging capabilities.

**Options:**
1. Source maps + breakpoints
2. Step-through interpreter in the playground
3. Print-based debugging only

**Recommendation:** Start with clear print output in tutorials (`flow-compile.js`), then option 2.

**Status:** ✅ **Answered: Option 2** — visual step-debugger desired; blocked on real wasm/compile playground (wiki Phase 3)

---

## Resolved Questions (Archive)

### 2026-07-28: Allow hyphens in `import` module paths / symbol lists?

**Answer:** Implemented Option 1, plus one additional low-risk change
discovered while verifying it end-to-end:

1. `_parse_module_path` / `_parse_import_symbol_list` in `src/flow/parser.py`
   now route through a new `_parse_dashed_identifier()` helper that merges
   `IDENTIFIER (- IDENTIFIER)*` runs into one dashed name (`Group-inv-unique`,
   `inv-unique`). Scoped to those two grammar productions only — MINUS has no
   other meaning in an import path/symbol-list position, so ordinary
   subtraction elsewhere is untouched (regression test added:
   `test_subtraction_still_works_outside_imports`).
2. Parsing alone wasn't sufficient to unblock the corpus: `import_symbols`
   are validated for existence in `ModuleResolver._validate_import_symbols`
   (`src/flow/module_resolver.py`), and the cited hyphenated names
   (`inv-unique`) never actually match a real declaration (declarations are
   always named by claim path, e.g. `«Group» «inverse» «is unique»`; no Flow
   declaration name can itself contain a hyphen). Confirmed this list is
   citation-only — it does not gate which declarations get pulled in
   (`all_declarations` already includes every transitively-imported
   declaration regardless of the symbol list) — so skipping the
   exists/exported checks specifically for symbol names containing a hyphen
   is safe: it only affects the newly-legal hyphenated-citation syntax, never
   a real (non-hyphenated) imported binding, so existing typo detection is
   unaffected.

Verified with `scripts/triage_verify_failures.py`: 43 of the 56 files tagged
purely "hyphenated import path/symbols" now transpile cleanly (827 vs. 784
pass out of 1054 under `examples/verify/`), with **zero regressions**
(diffed the full pass/fail set before vs. after). The other 13 still fail,
but for unrelated, already-catalogued reasons (operator-suffixed module
paths like `Nat/+`, or citation imports of a *non-hyphenated* symbol name
that also doesn't exist — same root issue as this one but out of scope since
it wasn't gated on hyphens). Added parser + resolver tests to
`tests/unit/test_module_resolver.py`; full `tests/unit/` suite (239 tests)
passes.

**Resolved:** 2026-07-28

### 2026-07-28: Package registry design

**Answer:** Defer + design doc — no central registry until 3+ real third-party packages; git/path deps are the supported path. See [docs/project/package-registry.md](docs/project/package-registry.md).

**Resolved:** 2026-07-28

### 2026-01-09: Parser `ptr[0].field` Syntax

**Answer:** Fix the parser — unified postfix chaining shipped (parser + C codegen). Ring buffer, memory pool, hash table, 2048, tetris, csv_parser, flowdb recovered.

**Resolved:** 2026-07

### 2026-01-08: Should we use `let mut` or `var` for mutable variables?

**Answer:** Use `let mut` - matches Rust, explicit about mutation.

**Resolved:** 2026-01-08
