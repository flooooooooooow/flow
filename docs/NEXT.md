# What's Next for Flow

> Strategic priorities after the v0.7.0 security audit (Feb 2026)

## Current State Assessment

**What Works Well:**
- Core language compiles and runs (C backend)
- 62 examples, 6 benchmarks, 2 apps
- Native graphics on macOS (Tetris, 2048 playable)
- ML framework (XOR network trains successfully)
- Autodiff working
- Effect system as a unique differentiator
- Documentation cleaned up with mascot
- 98/98 audit issues resolved (100%)
- All testing and CLI issues closed
- Module resolver fully hardened (path traversal, circular imports, symbol collisions)
- MLIR generator stabilized (7 bug fixes)
- Security fixes for CLI injection and runtime command injection
- `ptr[0].field` / unified postfix chaining works end-to-end (parser + C codegen);
  recovered ring_buffer, memory_pool, hash_table, 2048, tetris_gfx, csv_parser, flowdb
- Test corpus is strict-clean: `./flow test --strict --tier2` passes 215/215
- Targeted fuzzing harness (`tests/fuzz/`) runs in CI
- LSP: inline diagnostics, find references, rename (39-test scripted harness)
- Compile status of all examples tracked honestly in `../examples/STATUS.md`
  (891/1170 compile, 76.2%)

**What Needs Work:**
- 2 known parser crashes from fuzzing (xfail regressions): `ValueError` in
  `parse_type` on float array sizes, `RecursionError` on ~70 nested parens
- 8 remaining C-codegen failures listed in `../examples/STATUS.md`
- MLIR backend not yet validated against the new postfix-chain AST shapes
- Older `capability EffectName`-style effects examples transpile but don't link
  (see [effects-showcase.md](effects-showcase.md))
- Benchmark results not yet published
- Graphics is macOS-only

---

## Priority 1: Keep CI Healthy

The audit-driven CI fixes are complete. Keep the pipeline green by:
- Treating new warnings as failures
- Pinning or locking any new dependencies
- Keeping security scans enabled

The Feb 10, 2026 audit also identified new CI hygiene gaps (dependency pinning, lint depth,
and security scanning). Track those in the issue list.

---

## Priority 2: Quality & Regression Prevention

- Expand test coverage for recent fixes
- Done: targeted fuzzing for parser/typecheck/codegen paths (`tests/fuzz/run_fuzz.py`,
  mutation/grammar/pipeline targets, 30s per target in CI)
- Next: fix the two known fuzz crashes tracked as xfail in
  `tests/fuzz/test_crash_regressions.py`

---

## Priority 4: Showcase Strengths

### Effect System Demo
The effect system is Flow's **killer feature** - not in Rust, Go, Mojo, or Julia.

Done: `examples/effects/showcase.flow` plus a walkthrough in
[effects-showcase.md](effects-showcase.md) (including honest limitations of the
current handler model).

### Interactive Playground
Done: `docs/playground/index.html` is a syntax explorer with current-syntax examples
(all verified against `./flow run`), keyword-accurate highlighting, and basic lint
checks. It does not execute code in the browser; it links to server-side compilation
instructions instead.

Follow-up (out of scope for the syntax refresh): a real step-through debugger /
in-browser execution would need a wasm build of the compiler pipeline.

### Performance Comparison
Run benchmarks against C/Rust/Python and publish results.

---

## Priority 5: Broader Adoption

### Cross-Platform Graphics
- Add `runtime/gfx_linux.c` (SDL2 or X11)
- Add `runtime/gfx_windows.c` (Win32 or SDL2)

### Package Registry
- Simple TOML-based package format
- GitHub-based package hosting

### Parser Improvements
Done: the `ptr[0].field` limitation is fixed (unified postfix chaining), unblocking
the systems, games, csv_parser, and flowdb examples. Remaining parser work is the
two fuzz crashes and the `examples/verify/` proof-corpus syntax (271 parser failures
in `../examples/STATUS.md`, mostly that corpus).

### Real-World Project
Build something substantial in Flow to prove the language out end-to-end.

---

## Issue Tracker Hygiene

### Close Rate by Category

| Category | Closed | Open | Rate |
|----------|--------|------|------|
| Testing | 5 | 0 | 100% |
| CLI | 5 | 0 | 100% |
| Stdlib | 13 | 0 | 100% |
| Compiler | 58 | 0 | 100% |
| Runtime | 6 | 0 | 100% |
| CI | 6 | 0 | 100% |

---

## The 80/20 Focus

| Action | Impact | Effort |
|--------|--------|--------|
| Keep CI green + secure | Very High | Ongoing |
| Fix the 2 known fuzz crashes | High | 1 day |
| Publish benchmark results | High | 1-2 days |
| MLIR polish (validate postfix chains, optimization passes) | Medium | 1 week |
| Cross-platform graphics | Medium | 1 week |

---

## Audit Summary

The v0.7.0 audit filed 98 issues across all components. All 98 are now resolved
as of Feb 10, 2026. The next release should focus on regression prevention and
developer experience improvements rather than new security remediation.
