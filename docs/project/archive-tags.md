# Archive tags

These tags keep branches that were deleted in a branch review on 2026-10-01.
Most hold reference implementations of roadmap features written against the
retired Python compiler (`src/flow/`). None of the code builds on main today.
Use them as a design starting point when the feature is written in Flow.

Fetch one with `git fetch origin tag archive/<name>`, then read it with
`git log -p archive/<name>`. Several branches were stacked on each other, so a
tag can hold more than the one feature in its name; the line says so.

| Tag | Issue | What it holds |
|---|---|---|
| `archive/feat/563-effects-default` (6f693d24) | #563 | Strict effect coverage as the Stable default. |
| `archive/feat/684-domain-fields` (4bd8fb8d) | #684 | Lifetime domains propagated through struct fields and collections, stacked on the perf batch below. |
| `archive/feat/690-arena-domains` (c4fb09cc) | #690 | Arena memory bound to the arena instance's declared domain, on top of #684, #694 and #696. |
| `archive/feat/694-region-inference` (685ad519) | #694 | Conservative local non-aliasing proofs, stacked on the perf batch. |
| `archive/feat/721-text-blocks` (2be0a18a) | #721 | Indentation-based text blocks and `print:` syntax. |
| `archive/feat/731-local-restrict` (5f5b8a0b) | #731 | `restrict` on proven-disjoint local pointers, on top of #684, #690, #694 and #696. |
| `archive/feat/735-compile-profiling` (0d25a222) | #735 | Opt-in wall-time profiling of compile phases. |
| `archive/feat/740-mem-profiling` (bca40a57) | #740 | Opt-in runtime memory profiler. |
| `archive/feat/744-perf-remarks` (0c733e0e) | #744 | Opt-in compiler performance remarks. |
| `archive/feat/775-type-identity` (4523d6ca) | #775 | Stable type keys for user structs. |
| `archive/feat/900-pygments-lexer` (1bd8ef55) | #900 | A Pygments lexer for Flow, on top of the #736 cache work and its stack. |
| `archive/fix/615-bounds-elision` (b91fd372) | #615 | Span bounds check elided when the loop bound is the span's length. |
| `archive/fix/729-hoist-length-loads` (05c6669b) | #729 | Invariant span `.len` loop bound hoisted into a temporary. |
| `archive/fix/732-copy-elision` (3f7e1573) | #732 | Let-bound record updates built in place. |
| `archive/fix/734-f32-math-intrinsics` (1411cfae) | #734 | f32 math lowered to the precision-correct `*f` intrinsics. |
| `archive/perf/696-move-inference` (4626927b) | #696 | Move of a returned record update of a local base, stacked on the perf batch. |
| `archive/perf/736-incremental-cache` (1560378f) | #736 | A sound frontend declaration cache, on top of #684, #690, #694 and #696. |
| `archive/perf/745-runtime-primitive` (ff447cd3) | #745 | No #745-specific commit. The tip is the #694 fix that pointer arithmetic inherits its base region, on top of #684, #690 and #696. |
| `archive/perf/746-cold-start` (fc8e1a26) | #746 | Unused runtime frameworks trimmed from tiny-program startup, stacked on #615, #729, #732, #734, #740, #744 and #775. |
| `archive/perf/747-string-io` (b8fbbf25) | #747 | Pure-string concat chains joined in one pass, on the same stack as #746. |
| `archive/integrate/perf-batch` (6d91795a) | none | Integration of every perf and domain branch above, plus the Pygments lexer (#900) and Rosetta Code task solutions (#896, which later landed on main as #1144). |
| `archive/clinalg` (d50ec072) | none | Complex linear algebra and matrix functions for the standard library (`lib/stdlib/clinalg.flow`, `lib/stdlib/blas.flow`) with checks under `examples/linalg/`. Based on an old main. |
| `archive/feat/denotational-mlir` (ded16e28) | #664 | The Python prototype of the denotational MLIR emitter for flow blocks. See [Denotational MLIR](../design/denotational-mlir.md). |
