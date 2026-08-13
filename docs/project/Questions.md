# Flow Development Questions

This file tracks questions that need human resolution before the AI can proceed.

Format:
- Questions are added by AI when uncertain
- Answers are added by human
- Resolved questions move to the archive at the bottom

---

## Open Questions

### 2026-08-07: Heterogeneous FIR-G compiler architecture

**Context:** Design for FIR-S → FIR-G → FIR-M with GPU/MLX analysis and learned
optimisation (MLGO-style profitability only). See [fir-g.md](fir-g.md).

**Options:**
1. Bolt ML onto existing AST walkers
2. Introduce dense-ID FIR-G as first-class IR; CPU analyses first; MLX later
3. Jump straight to MLX-in-core / C++ rewrite

**Recommendation:** (2) — Phase order locked in fir-g.md. Correctness stays
deterministic; ML only for profitability. Dual C/MLIR/WASM backends remain.

**Status:** ✅ Resolved (2026-08-07) — Phases 1–4 landed in Python alongside
existing emitters (`./flow fir-g`, measured routing, opt candidates).

---

### 2026-08-04: Self-hosting bootstrap strategy

**Context:** Started `compiler/` (`flowc`) — Flow lexer + subset parser that
runs under today’s Python→C host. Next phases: more syntax, then a backend.

**Progress:** Stage-A path well underway. Host runs tests; Stage-A emits+links
real `token`/`ast`/`lexer`/`fileio`/`parser`/`cgen` → `flowc_frontend.o`; C
driver emits fixtures; **self-emit** rebuilds frontend → `flowc_frontend_self.o`.
See [compiler/README.md](../../compiler/README.md), `roundtrip.sh`.

**Options:**
1. **Heterogeneous forever** — Flow front-end (lex/parse/typecheck), keep C/MLIR
   codegen in Python until Flow can emit C well enough to compile itself
2. **Stage-A C emitter in Flow** — tiny subset→C in Flow; use host to compile
   `flowc`, then `flowc` compiles a larger `flowc`
3. **Interpreter first** — Flow AST interpreter for dogfooding before codegen

**Recommendation:** (1) until parser covers ~80% of `src/flow` syntax surface,
then (2) for a minimal `function`/`let`/`if`/`return`→C path. Avoid (3) as the
main line — Flow’s product is compiled.

**Status:** 🔲 Pending

---

### 2026-08-04: Ecosystem packages — registry vs stdlib

**Context:** Seeded `json`, `toml`, `http`, `sqlite` under `registry/packages/` (not
`lib/stdlib/`) so apps pull them with `flow add` / `flow.toml`. Stdlib still
owns POSIX, collections, audio, gfx, concurrency.

**Options:**
1. Keep app-facing libs in the registry; stdlib stays language/runtime primitives
2. Graduate mature packages into `lib/stdlib/` / `std.*` once stable
3. Dual-publish (stdlib re-exports registry) — more moving parts

**Recommendation:** (1) now; (2) only for ubiquitous primitives (e.g. JSON) after
API freeze. Wrap packages that need system libs (`http`, `sqlite`) stay registry
+ `[native]` forever.

**Status:** 🔲 Pending

---

### 2026-08-04: Concurrency vs Go — Phase 2 priorities

**Context:** Phase 1 shipped ([docs/language/concurrency-vs-go.md](../language/concurrency-vs-go.md)):
real channels, WaitGroup wait, TLS effect handlers, `parallel for`→OpenMP,
`ThreadedAsync` over pthreads. (Later the same day: `select2`, FiberAsync M:N,
asm fctx, `NetpollAsyncIO`. Still no delimited continuations / N-way `select`.)

**Options:**
1. Continuations + fiber scheduler next (true effects-native async)
2. `select` + generic channels next (Go API parity)
3. Go-comparison benchmarks next (credibility before more runtime)
4. Real `AsyncIO` (kqueue/epoll) next (server path)

**Recommendation:** (3) then (1) — measure channel/ping-pong and parallel-for
vs Go before inventing fibers; keep effect surface stable.

**Status:** ✅ Resolved (2026-08-04) — through M:N + netpoll ([replace-go.md](../language/replace-go.md)).
Flow wins ping-pong + fan-out vs Go. Follow-ups shipped: `select4`, fiber-park
IO, HTTP microbench, `FLOW_RACE=1` hooks, `flow_cont` scaffold. Remaining:
true Flow-frame suspend, generic channels, TSAN-class races. GitHub CI disabled.

---

### 2026-08-04: Effect-row typing vs soft defaults

**Context:** Unhandled effect ops currently return zero / no-op (documented
“safe defaults”). Interim opt-in abort shipped: `FLOW_STRICT_EFFECTS=1` and
`--strict-effects` (see `docs/effects-showcase.md`).

**Options:**
1. Keep soft defaults as language default; rows later; strict via env/flag
2. Flip default to fail-loud; soft defaults only with an explicit pragma
3. Effect-row typing on signatures (Koka/Unison style) — reject unhandled at compile time

**Recommendation:** Stay on (1) until rows exist; then prefer (3) and retire
soft defaults for typed code. Do not flip default to abort without a migration
note — showcase and tests rely on zeros.

**Update (2026-08-04):** Phase 1 shipped — `--strict-effects` enables
**compile-time** unhandled-effect errors via a lexical handler stack in the
type checker (plus runtime abort).

**Update (2026-08-04, later):** Phase 2 shipped — `function f() -> T with E1, E2`
declares a signature effect row; under `--strict-effects` the body may perform
those effects, and callers must cover them via `handle` or their own `with`.

**Update (2026-08-04, final):** First-class rows shipped — `(T) -> R with E` on
types; calls through such values require `E` under `--strict-effects`. Soft
defaults remain the language default (option 1). Still open: whether to retire
soft defaults for typed code later.

**Status:** ✅ Resolved for typing surface (soft-default policy remains option 1)

---

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

### 2026-08-06: Declarative ordering — Phase 2 selector and new surface

**Context:** Phase 2 shipped (#144, #145, #146, #147). A cost-based selector
(`src/flow/plan_selector.py`) picks among six sort lowerings and two search
lowerings; ordering provenance (`src/flow/ordering_hints.py`) carries
sortedness and integer-range facts through straight-line code; `--explain`
prints every decision. Measured payoff in `benchmarks/ordering/RESULTS.md`.

**Decided:**
1. **Float ordering** — IEEE 754-2008 totalOrder for sort / unique / find;
   arithmetic comparison stays IEEE. Rationale in `docs/language/ordering.md`.
   Supersedes the NaN-before / NaN-after question in #144.
2. **New surface** — two additions, both pipeline-position only:
   `xs |> find(t)` (index of the first match under the same total order, or
   `-1`) and the `general` sort policy (pin the general plan, ignore hints).
   `find` is claimed only after `|>` and only when followed by `(`, so an
   ordinary `find(...)` call is untouched.
3. **Cost vocabulary** — one dimension, estimated element operations, plus a
   single hard resource budget (256 KiB of compiler scratch). `require` /
   `prefer` and a `supports cpu / simd / gpu` axis wait for a cost IR with
   real units.

**Still open:** items (1) `unique` length, (2) entropy, (3) `order { }` and
(4) copy vs mutate from the 2026-08-04 entry above are all untouched.

**Status:** ✅ Resolved for the selector and the new surface; the four Phase 1
semantics questions above remain pending.

---

### 2026-08-11: Multi-implementation selection beyond sort (#147)

**Context:** The cost-based selector in `plan_selector.py` is already
construct-agnostic. `ordering_plans.py` registers sort and search. The
issue asks for the same mechanism to cover non-sorting transforms (DSP,
ML, numerics) with a constraint vocabulary (`require` / `prefer`).

**Decided:**
1. **Implementation declaration** stays a stdlib registry, not a new
   syntax block. Each construct registers `Implementation` objects via
   `register()`. New file: `src/flow/general_plans.py` registers `matmul`
   (naive vs blocked) and `reduce` (sequential vs parallel_tree).
2. **Constraint vocabulary** lives in `src/flow/constraints.py`.
   `require(memory < N)` becomes `require_memory_bytes = N` in the Facts
   data dict. `prefer(parallel)` becomes `prefer = "parallel"`.
   Implementations check these in their applicability predicates and
   cost models. The selector itself does not know about constraints.
3. **Surface syntax** for `require` / `prefer` is attribute-based:
   `@require(memory < 4096)`, `@prefer(parallel)`. The parser is in
   `constraints.py` but not yet wired into the compiler. The compiler
   builds Facts programmatically today. Wiring the attribute form is a
   follow-up once the cost IR has real units.
4. **Two constructs, two implementations each, constraint flips choice:**
   - matmul: naive (small n) vs blocked (large n). `require(memory < 4096)`
     flips large n back to naive.
   - reduce: sequential (small n) vs parallel_tree (large n).
     `prefer(parallel)` flips small n to parallel_tree.
5. **`--explain`** already works for any construct. The report includes
   matmul and reduce selections with the same format as sort.

**What stays parsed-only:** `prefer` for objectives other than `parallel`
(latency, energy, memory) is parsed but does not bias the cost model yet.
The cost IR has one dimension (estimated element operations). Real units
need a target model.

**Status:** Resolved. Implemented in `general_plans.py`, `constraints.py`,
20 tests in `test_general_plans.py`.

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

**Answer:** Defer + design doc — no central registry until 3+ real third-party packages; git/path deps are the supported path. See [docs/project/package-registry.md](package-registry.md).

**Resolved:** 2026-07-28

### 2026-01-09: Parser `ptr[0].field` Syntax

**Answer:** Fix the parser — unified postfix chaining shipped (parser + C codegen). Ring buffer, memory pool, hash table, 2048, tetris, csv_parser, flowdb recovered.

**Resolved:** 2026-07

### 2026-01-08: Should we use `let mut` or `var` for mutable variables?

**Answer:** Use `let mut` - matches Rust, explicit about mutation.

**Resolved:** 2026-01-08
