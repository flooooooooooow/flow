# Flow Development Questions

This file tracks questions that need human resolution before the AI can proceed.

Format:
- Questions are added by AI when uncertain
- Answers are added by human
- Resolved questions move to the archive at the bottom

---

## Open Questions

### 2026-10-05: Algebraic effects: abort, retry, and multi-shot continuations?

**Context:** Issue #564 records that shipped handlers are tail-resumptive
only: an operation returns to its call site, and a capability method cannot
decline to resume (abort / exception encoding), replay the continuation
(retry), or invoke it more than once (multi-shot / generators / schedulers).
The C backend implements this as a `_Thread_local` handler pointer plus a
direct call. Full continuations need CPS, heap stacks, or a state machine,
which conflicts with the zero-overhead C ABI path. See
[rfc_effects_continuations.md](../research/rfc_effects_continuations.md)
and [effects-continuations.md](../language/effects-continuations.md).

**Options:**
1. Keep tail-resumptive handlers as the 1.0 language rule. Reject reserved
   `resume` / `resume_multi` forms in capability methods. Encode abort as
   `Result` / status, retry as a caller loop plus a policy effect.
2. Add abort (0-shot) only, via longjmp or an extra handle-block status,
   still without retry or multi-shot.
3. Add general one-shot and multi-shot continuation capture (Koka / Eff /
   OCaml 5 style).

**Recommendation:** Option 1. It is the conservative 1.0 choice already
accepted by the RFC. Options 2 and 3 change control-flow and ABI
predictability and need an explicit human design decision before anyone
plans a scheduler or exception encoding on top of `handle`.

**Status:** Conservative option implemented (2026-10-05): spec + compiler
rejection of `resume` / `resume_multi` in capability methods + tests.
Options 2 and 3 remain open for a later 1.x or post-1.0 decision.

---

### 2026-08-06: Lifetime domains: annotation-only or `domain` blocks in v0?

**Context:** Issue #148 asks for `callback` / `frame` / `session` /
`application` as a first-class memory model, and leaves the v0 surface open:
annotations on declarations, or a `domain frame { … }` block that implies an
arena reset at the block's end.
([lifetime-domains.md](../language/lifetime-domains.md))

**Options:**
1. Annotation-only: `@lifetime(D)` on a function and on a module static.
   Reuses the existing decorator grammar, no parser work beyond a new
   attribute name, and a value takes its domain from its allocation site.
2. `domain frame { … }` blocks: nicer at the frame boundary because the
   reset is implicit, but it needs new grammar, a new scope kind, and a
   decision about what a domain block means when nested or when it contains
   a `return`.
3. Both.

**Recommendation:** Option 1 for v0, shipped. `@lifetime(...)` parses on
functions, statics and struct fields; the five rules (LD1 escape to a
longer-lived static, including through composite storage, LD2 escape by
return, LD3 allocation discipline, LD4 call ordering, LD5 field-declared
domains) are enforced by the type checker. Block sugar is listed under
Future work with `frame_begin` / `frame_end` as the explicit form it would
expand to. Field annotations are issue #684.

**Status:** ✅ Resolved for v0 (annotation-only, 2026-08-06; fields 2026-10-05)

---

### 2026-08-05: `gfx_run`: callback vs block sugar?

**Context:** Pattern adoption ([pattern-adoption.md](pattern-adoption.md)) wants
to kill the repeated poll/esc/clear/present loop in every gfx demo. Two sketches:

**Options:**
1. Stdlib/runtime callback: `flow_gfx_run` + user `flow_gfx_frame(g, frame) -> i32`
   (works today; slightly awkward naming).
2. Block sugar: `gfx_run(g, max_frames: N) { … }` (nicer; needs parser/lowering).
3. Both: A now, B later when frame blocks exist.

**Recommendation:** Option 3 (shipped MVP): `gfx_frame_pump` for inline loops;
`flow_gfx_run` / `gfx_run` calling weak-overridable `flow_gfx_frame`. Block sugar deferred.

**Status:** ✅ Resolved (Option 3 MVP 2026-08-05)

---

### 2026-08-05: `represent phase_portrait`: language form or stdlib trail helper?

**Context:** Lorenz north-star wants `represent phase_portrait(x, z) { trail … }`
inside a `flow`. We already have `represent linear`.

**Options:**
1. Full `represent phase_portrait` lowering (ring buffer + window + maps).
2. Stdlib-only `portrait_trail_*` helpers; keep `represent` for linear/analysis.
3. Hybrid: stdlib trail now; grammar sugar later that expands to helpers.

**Recommendation:** Option 3. Lorenz now uses `flow` + trail in `main`; grammar sugar later.

**Status:** ✅ Resolved for MVP (stdlib trail helpers / grammar still open as follow-on)

---

### 2026-08-05: LQR n>2: stdlib first or extend `dsys`?

**Context:** Cartpole control reimplements 4×4 Riccati because dynamics DSL is n=2.

**Options:**
1. Stdlib `lqr`/`dare` over LAPACK/Accelerate; DSL stays n=2 until matrix literals mature.
2. Extend `dsys`/`analyze`/`lqr` to arbitrary n in the DSL immediately.
3. Codegen-only for fixed n=4 cartpole (one-off).

**Recommendation:** Option 1: general, dogfoods BLAS, unblocks cartpole without
rushing DSL matrix codegen.

**Status:** 🔲 Pending

---

### 2026-08-05: Field / laplacian: stdlib MVP or grammar card?

**Context:** `heat_diffusion.flow` is nested Euler; vision wants
`T evolves as alpha * laplacian(T)`.

**Options:**
1. Stdlib `laplacian_1d` + ordinary `flow` over array-backed state (no new keywords).
2. Full `field` / `boundary` grammar from north-star.
3. Defer until after Lorenz/`gfx_run` land.

**Recommendation:** Option 1 for P2 MVP; grammar as follow-on card.

**Status:** 🔲 Pending

---


### 2026-08-05: Self-hosting cutover: when does `./flow` drop Python?

**Context:** Plan in `docs/project/self-hosting.md`. Stage-A `flowc` exists
as a bootstrap; production is still `src/flow/*.py`.

**Options:**
1. Hard cutover after Phase C parity suite green (recommended).
2. Soft forever dual-host (`FLOW_HOST=python|flowc`) with no deadline.
3. Freeze Python features and only grow `flowc` (slow user-facing velocity).

**Recommendation:** (1) with a published parity checklist; keep (2) as escape
hatch for one release after cutover.

**Resolution (2026-08-05):** Soft dual-host now: `./flow run|compile`
defaults to `FLOW_HOST=flowc` (Stage-A); escape hatch `FLOW_HOST=python`.
Hard drop of Python from the compile path is Phase D (#153).

**Status:** ✅ Resolved (soft cutover; Phase D retires Python)

### 2026-08-07: Heterogeneous FIR-G compiler architecture

**Context:** Design for FIR-S → FIR-G → FIR-M with GPU/MLX analysis and learned
optimisation (MLGO-style profitability only). See [fir-g.md](fir-g.md).

**Options:**
1. Bolt ML onto existing AST walkers
2. Introduce dense-ID FIR-G as first-class IR; CPU analyses first; MLX later
3. Jump straight to MLX-in-core / C++ rewrite

**Recommendation:** (2). Phase order locked in fir-g.md. Correctness stays
deterministic; ML only for profitability. Dual C/MLIR/WASM backends remain.

**Status:** ✅ Resolved (2026-08-07). Phases 1-4 landed in Python alongside
existing emitters (`./flow fir-g`, measured routing, opt candidates).

---

### 2026-08-04: Self-hosting bootstrap strategy

**Context:** Started `compiler/` (`flowc`): Flow lexer + subset parser that
runs under today's Python→C host. Next phases: more syntax, then a backend.

**Progress:** Stage-A path well underway. Host runs tests; Stage-A emits+links
real `token`/`ast`/`lexer`/`fileio`/`parser`/`cgen` → `flowc_frontend.o`; C
driver emits fixtures; **self-emit** rebuilds frontend → `flowc_frontend_self.o`.
See [compiler/README.md](../../compiler/README.md), `roundtrip.flow`.

**Options:**
1. **Heterogeneous forever**: Flow front-end (lex/parse/typecheck), keep C/MLIR
   codegen in Python until Flow can emit C well enough to compile itself
2. **Stage-A C emitter in Flow**: tiny subset→C in Flow; use host to compile
   `flowc`, then `flowc` compiles a larger `flowc`
3. **Interpreter first**: Flow AST interpreter for dogfooding before codegen

**Recommendation:** (1) until parser covers ~80% of `src/flow` syntax surface,
then (2) for a minimal `function`/`let`/`if`/`return`→C path. Avoid (3) as the
main line. Flow's product is compiled.

**Status:** 🔲 Pending

---

### 2026-08-04: Ecosystem packages: registry vs stdlib

**Context:** Seeded `json`, `toml`, `http`, `sqlite` under `registry/packages/` (not
`lib/stdlib/`) so apps pull them with `flow add` / `flow.toml`. Stdlib still
owns POSIX, collections, audio, gfx, concurrency.

**Options:**
1. Keep app-facing libs in the registry; stdlib stays language/runtime primitives
2. Graduate mature packages into `lib/stdlib/` / `std.*` once stable
3. Dual-publish (stdlib re-exports registry): more moving parts

**Recommendation:** (1) now; (2) only for ubiquitous primitives (e.g. JSON) after
API freeze. Wrap packages that need system libs (`http`, `sqlite`) stay registry
+ `[native]` forever.

**Status:** 🔲 Pending

---

### 2026-08-04: Concurrency vs Go: Phase 2 priorities

**Context:** Phase 1 shipped ([docs/language/concurrency-vs-go.md](../language/concurrency-vs-go.md)):
real channels, WaitGroup wait, TLS effect handlers, `parallel for`→OpenMP,
`ThreadedAsync` over pthreads. (Later the same day: `select2`, FiberAsync M:N,
asm fctx, `NetpollAsyncIO`. Still no delimited continuations / N-way `select`.)

**Options:**
1. Continuations + fiber scheduler next (true effects-native async)
2. `select` + generic channels next (Go API parity)
3. Go-comparison benchmarks next (credibility before more runtime)
4. Real `AsyncIO` (kqueue/epoll) next (server path)

**Recommendation:** (3) then (1). Measure channel/ping-pong and parallel-for
vs Go before inventing fibers; keep effect surface stable.

**Status:** ✅ Resolved (2026-08-04) through M:N + netpoll ([replace-go.md](../language/replace-go.md)).
Flow wins ping-pong + fan-out vs Go. Follow-ups shipped: `select4`, fiber-park
IO, HTTP microbench, `FLOW_RACE=1` hooks, `flow_cont` scaffold. Remaining:
true Flow-frame suspend, generic channels, TSAN-class races. GitHub CI disabled.

---

### 2026-08-04: Effect-row typing vs soft defaults

**Context:** Unhandled effect ops currently return zero / no-op (documented
"safe defaults"). Interim opt-in abort shipped: `FLOW_STRICT_EFFECTS=1` and
`--strict-effects` (see `docs/effects-showcase.md`).

**Options:**
1. Keep soft defaults as language default; rows later; strict via env/flag
2. Flip default to fail-loud; soft defaults only with an explicit pragma
3. Effect-row typing on signatures (Koka/Unison style): reject unhandled at compile time

**Recommendation:** Stay on (1) until rows exist; then prefer (3) and retire
soft defaults for typed code. Do not flip default to abort without a migration
note. Showcase and tests rely on zeros.

**Update (2026-08-04):** Phase 1 shipped: `--strict-effects` enables
**compile-time** unhandled-effect errors via a lexical handler stack in the
type checker (plus runtime abort).

**Update (2026-08-04, later):** Phase 2 shipped: `function f() -> T with E1, E2`
declares a signature effect row; in Stable mode the body may perform
those effects, and callers must cover them via `handle` or their own `with`.

**Update (2026-08-04, final):** First-class rows shipped: `(T) -> R with E` on
types; calls through such values require `E` in Stable mode. The legacy
zero/no-op behavior remains available through the explicit permissive environment
variables described above.

**Status:** ✅ Resolved. Stable compilation and runtime fail loudly by default. Set
`FLOWC_PERMISSIVE_EFFECTS=1` while compiling and `FLOW_PERMISSIVE_EFFECTS=1`
while running to retain the legacy zero/no-op behavior.

---

### 2026-08-04: Declarative ordering: Phase 2 scope

**Context:** Phase 1 shipped (`docs/language/ordering.md`): `xs |> sort`,
`sort by` / `sortBy [asc .f, desc .g]`, `stable`/`unique`/`descending`,
plus parsed-but-ignored policies (`parallel`, `gpu`, `with entropy`, …).
C backend lowers to in-place stable insertion on `array<T, N>`.

**Open decisions for Phase 2:**
1. **`unique` length**: keep compact-in-place with stale tail (current), or
   return `(array, len)`, or shrink via slices?
2. **Entropy**: first-class effect (`with entropy`) vs optional seed arg only?
3. **`order { }` block**: required sugar, or keep pipeline-only?
4. **Copy vs mutate**: pipeline looks pure; today is in-place. Pure
   `sorted` copy as default?

**Recommendation:** Keep Phase 1 semantics; decide (1) and (4) before
advertising `unique` widely; defer GPU/distributed until adaptive selector
exists.

**Status:** 🔲 Pending (Phase 1 implemented 2026-08-04)

---

### 2026-08-06: Declarative ordering: Phase 2 selector and new surface

**Context:** Phase 2 shipped (#144, #145, #146, #147). A cost-based selector
(`src/flow/plan_selector.py`) picks among six sort lowerings and two search
lowerings; ordering provenance (`src/flow/ordering_hints.py`) carries
sortedness and integer-range facts through straight-line code; `--explain`
prints every decision. Measured payoff in `benchmarks/ordering/RESULTS.md`.

**Decided:**
1. **Float ordering**: IEEE 754-2008 totalOrder for sort / unique / find;
   arithmetic comparison stays IEEE. Rationale in `docs/language/ordering.md`.
   Supersedes the NaN-before / NaN-after question in #144.
2. **New surface**: two additions, both pipeline-position only:
   `xs |> find(t)` (index of the first match under the same total order, or
   `-1`) and the `general` sort policy (pin the general plan, ignore hints).
   `find` is claimed only after `|>` and only when followed by `(`, so an
   ordinary `find(...)` call is untouched.
3. **Cost vocabulary**: one dimension, estimated element operations, plus a
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
3. No syntax change: IntelliSense-only labeling

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

**Status:** ✅ **Answered: Option 2**. Visual step-debugger desired; blocked on real wasm/compile playground (wiki Phase 3)

---

## Resolved Questions (Archive)

### 2026-10-08: AST parse cache: how far should flowc distrust its own cache directory? (#736)
The user cache directory stays trusted as #1345 set it. Records carry a
payload checksum and a size cap, so a torn or corrupt record is a miss and
is re-parsed. No ownership or mode checks on the directory and no
`O_CREAT|O_EXCL` writes. #1402 implements this (record schema 2).

**Resolved:** 2026-10-08, decided by the coordinator with the owner's
delegation.

### 2026-10-08: Is Flow 1.0.2 still released?

**Context:** Issue #760 tracked a 1.0.2 patch release over Stable 1.x.
`VERSION` on main is `2.0.0`, the newest release is `v1.0.1`, and no
frozen 1.x maintenance commit exists to qualify. The Python compiler and
the Python host that the 1.0.2 qualification notes relied on are deleted
from main, so a release cut from main is not a 1.x patch. Issue #652
listed 1.0.2 publication as its last acceptance box.

**Answer:** 1.0.2 is superseded by 2.0. No 1.0.2 tag or release is
made. #760 is closed, with each of its items mapped to the 2.0 work or
to the pull request that delivered it. #652 is retargeted to the 2.0
release: qualification, RC promotion and Homebrew apply to `v2.0.0`.

**Resolved:** 2026-10-08, decided by the coordinator on the project
owner's behalf.

### 2026-10-07: Flow 3.0 Structural Orchestration Algebra: syntax or library?

**Context:** Issue #723 proposes syntax-native orchestration. PR #1393
overloads `>>` by operand type: integer shift for integers, orchestration
sequencing for other operands, and `>> { ... }` for fan-out. Its type
check falls back to unknown, and its description claims parser and C
lowering changes that the diff does not contain.

**Answer:** Not accepted in this form. Overloading `>>` by operand type
gives one symbol two meanings decided by inference, so a mistyped shift
silently becomes orchestration. Orchestration starts as a library:
`std.orchestrate` combinators (`seq`, `fanout`) with no new syntax.
Syntax is decided later from real use. If syntax is added, it uses a
dedicated operator or keyword, never `>>`. #1393 is closed; #723 stays
open. See the
[Flow 3.0 tracker](flow-3-0-feature-request-tracker.md#orchestration-library-first).

**Resolved:** 2026-10-07, decided by the project owner.

### 2026-10-07: Lifetime domains: `request` and `persistent` (Axiom §7)

**Context:** [lifetime-domains.md](../language/lifetime-domains.md)
listed `request` and `persistent` as unimplemented with no position in
the domain order. PR #1369 (issue #679) adds them.

**Answer:** Accepted. The lattice is
`callback < frame < request < session < application < persistent`.
`request` may allocate and is not `@rt_safe`. `persistent` is the
outermost domain and outlives the process. Follow-up #1421, decided by
the project owner on 2026-10-07: yes, a value stored in `persistent` must
be TransportSafe (the trait from #1340), and the checker names the field
or element that carries the reference.

**Resolved:** 2026-10-07, decided by the project owner.

### 2026-10-07: `@lifetime(D)` on struct fields and rule LD5

**Context:** The 2026-08-06 entry covers `@lifetime(D)` on functions and
module statics only. PR #1358 (issue #684) propagates domains through
struct fields and collections, adds `@lifetime(D)` on a struct field as a
contract, and adds rule LD5.

**Answer:** Accepted. `@lifetime(D)` is allowed on struct fields as a
contract, together with rule LD5. #1358 merges after #1369.

**Resolved:** 2026-10-07, decided by the project owner.

### 2026-10-07: Last-use moves without a `move` keyword or COW

**Context:** Issue #696 asks for value semantics with compiler-inferred
move defaults. PR #1354 recorded three options: conservative last-use
lowering, a `move` expression with use-after-move errors, or inferred
copy-on-write and implicit sharing.

**Answer:** Option 1. There is no `move` keyword and no copy-on-write or
implicit sharing. A move is inferred only at a proven last use of a
uniquely owned function-scoped local or by-value parameter. Observable
value semantics are unchanged: the move is a pure optimisation. #1354
merges after #1367.

**Resolved:** 2026-10-07, decided by the project owner.

### 2026-10-07: Public type reflection API and its stability tier

**Context:** Issue #775 asks for stable type identity and reflection for
cross-target runtime schemas. PR #1365 adds the `@schema_revision(N)`
attribute, `type_member_count<T>()`, `type_member_table<T>()` and the
per-target `type_sizeof_*`, `type_alignof_*` and `type_layout_*` names for
native64 and wasm32.

**Answer:** Accepted. These names become public API at Experimental
stability. They are registered as `experimental` in
`stability/surfaces.json` so they can change before a 1.x review.

**Resolved:** 2026-10-07, decided by the project owner.

### 2026-10-07: Linux release qualification policy

**Context:** Issue #652 needs a rule for what qualifies a Linux release
and which run is the authority. PR #1399 adds source archive
qualification and Debian packaging.

**Answer:** Policy accepted. Qualification is local and checksum-gated.
The `.deb` is reproducible, source-built from a pinned commit with
`SOURCE_DATE_EPOCH` and root ownership. Hosted CI is not qualification
authority. Linux arm64 is explicitly unqualified. Conditions before
merge: the PR's three shell scripts become Flow tools that use
`std.process`, with callers and docs pointing at `./flow tool ...`, and
one real qualification run on Linux with the real flowc (on the CI VPS,
runner `vps-linux`) is recorded in the PR.

**Resolved:** 2026-10-07, decided by the project owner.

### 2026-07-28: Allow hyphens in `import` module paths / symbol lists?

**Answer:** Implemented Option 1, plus one additional low-risk change
discovered while verifying it end-to-end:

1. `_parse_module_path` / `_parse_import_symbol_list` in `src/flow/parser.py`
   now route through a new `_parse_dashed_identifier()` helper that merges
   `IDENTIFIER (- IDENTIFIER)*` runs into one dashed name (`Group-inv-unique`,
   `inv-unique`). Scoped to those two grammar productions only. MINUS has no
   other meaning in an import path/symbol-list position, so ordinary
   subtraction elsewhere is untouched (regression test added:
   `test_subtraction_still_works_outside_imports`).
2. Parsing alone wasn't sufficient to unblock the corpus: `import_symbols`
   are validated for existence in `ModuleResolver._validate_import_symbols`
   (`src/flow/module_resolver.py`), and the cited hyphenated names
   (`inv-unique`) never actually match a real declaration (declarations are
   always named by claim path, e.g. `«Group» «inverse» «is unique»`; no Flow
   declaration name can itself contain a hyphen). Confirmed this list is
   citation-only. It does not gate which declarations get pulled in
   (`all_declarations` already includes every transitively-imported
   declaration regardless of the symbol list), so skipping the
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
that also doesn't exist: same root issue as this one but out of scope since
it wasn't gated on hyphens). Added parser + resolver tests to
`tests/unit/test_module_resolver.py`; full `tests/unit/` suite (239 tests)
passes.

**Resolved:** 2026-07-28

### 2026-07-28: Package registry design

**Answer:** Defer + design doc. No central registry until 3+ real third-party packages; git/path deps are the supported path. See [docs/project/package-registry.md](package-registry.md).

**Resolved:** 2026-07-28

### 2026-01-09: Parser `ptr[0].field` Syntax

**Answer:** Fix the parser. Unified postfix chaining shipped (parser + C codegen). Ring buffer, memory pool, hash table, 2048, tetris, csv_parser, flowdb recovered.

**Resolved:** 2026-07

### 2026-01-08: Should we use `let mut` or `var` for mutable variables?

**Answer:** Use `let mut` - matches Rust, explicit about mutation.

**Resolved:** 2026-01-08
