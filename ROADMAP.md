# FLOW Roadmap

> Last updated: 2026-10-13  
> Current version: 2.0.0  
> Source: ~391,000 physical lines tracked (see README project statistics)

This document tracks what we're building next and why.

> **Vision:** the destination this roadmap points at is laid out in
> [VISION.md](VISION.md): a language where the primary abstraction is the
> evolution of systems through time.
>
> **Product thesis / beachhead:** Flow describes **physical computational
> systems** (RF, embedded, SDR, FPGA-adjacent, satellite). Architecture and
> 30-pillar sequencing: the phase table below.
> Dynamics grammar cards: [docs/vision/north-star.md](docs/vision/north-star.md).

> **Live tracker:** day-to-day backlog and task status now live on the Helm board
> (local kanban at `http://127.0.0.1:9470/app?project=flow`). This document stays
> the strategic overview; the board is the source of truth for in-flight work.
> Open items here mirror to GitHub issues as `[roadmap]` labels via
> `./flow tool roadmap_sync` (creates missing issues, closes + checks ones marked
> done); `./flow tool issues_sync` then rounds trip state with `issues-checklist.md`.

---

## Physical systems beachhead (RF → satellite)

Strategic cut: do **not** pitch "safer embedded." Pitch a compiler that understands
units + rates + timing + memory topology + hardware + precision. Phase map below;
grammar cards in [north-star.md](docs/vision/north-star.md).

| Phase | Focus | Status |
|-------|--------|--------|
| **W0** | RF units + quantity literals + complex/IQ + phantom rate `Signal` + memory/RT attrs + docs/examples | 🔨 near-complete: `c64`/`c128` complex types (C99 `_Complex`), `c64()`/`c128()` constructors, `creal`/`cimag`/`cabs`/`carg`/`conj`/`cexp`/`clog`/`csqrt`/`cpow` builtins, complex arithmetic with auto-promotion, `lib/stdlib/rf.flow` (`IQ` alias, `IQSample` distinct type, `Signal<R>` generic struct with phantom rate type parameter, rate markers Hz1000/Hz8000/Hz44100/Hz48000/Hz1M/etc., `signal_new`/`signal_mix`/`signal_scale`/`signal_magnitude_spectrum` with compile-time rate checking), `lib/stdlib/units_si.flow` (SI base + derived units), quantity literals (`3.14 Hertz` desugars to `3.14 as Hertz`), `examples/rf/dft.flow` + `examples/rf/iq_mixer.flow` + `examples/rf/sdr_receiver.flow`, `tests/unit/test_complex_types.py` (15) + `test_rf_types.py` (11) + `test_quantity_literals.py` (10). |
| **W1** | Fuseable DSP `\|>` + rate analysis; harden `guarantee` | ✅ complete: `lib/stdlib/dsp.flow` (`map_f32`/`map_f64`, `filter_f32`, `reduce_f32`/`reduce_f64`, `scan_f32`/`scan_f64`, `zip_with_f32`/`zip_with_f64`, `scale_f32`/`scale_f64`, `offset_f32`, `clip_f32`, `sum_f32`/`sum_f64`, `dot_f32`/`dot_f64`), `|>` pipeline chaining with lambdas and named functions, function-type parameter compatibility fix, lambda-as-argument fat-pointer wrapping in C generator, `examples/dsp/pipeline.flow`, `tests/unit/test_dsp_pipeline.py` (11 tests). Compile-time fusion of adjacent `map`/`scale`/`offset` stages shipped in 0.11.0. Next: rate analysis. |
| **W2** | MMIO, bitfields, fixed-point + saturating | ✅ complete: `lib/stdlib/mmio.flow`, `lib/stdlib/bitfield.flow`, `lib/stdlib/fixed_point.flow` (`Q16_16`, `Q8_24`), `saturating_*` helpers in `checked_arith.flow` |
| **W3** | Bare-metal/RTOS, interrupts, state machines | ✅ complete: `lib/stdlib/interrupt.flow`, `lib/stdlib/rtos.flow`, `lib/stdlib/fsm.flow`, `examples/embedded/fsm_controller.flow`, `tests/lang/test_interrupt.flow`, `tests/lang/test_rtos.flow`, `tests/lang/test_fsm.flow` |
| **W4** | Sim ↔ deploy identical code; digital twin | 🔲 |
| **W5** | `@hardware` → RTL; CDC; deploy partitions | ✅ complete: `lib/stdlib/hardware.flow` (`ClockDomain`, `Register`, `cdc_sync`), `@hardware` compiler attribute validation, `examples/hardware/blink.flow`, and `tests/lang/test_hardware_cdc.flow`. |
| **W6** | Fault/radiation; `Flow Safety` / `--profile flight` | 🔨 partial: Phase 0+overflow+arena+control: flags/sanitizers, checked +/−/*, strcat/closure temp arena (#267/#268), recursion reject (#271), `@max_iterations` (#272), [safety-profiles.md](docs/language/safety-profiles.md). Null dereference macro and fault handler (#288). |

Audio `@rt_safe` / lifetime domains remain the proving ground for the same contracts.

### Guiding Principles

1. **Working > Perfect** - Ship incrementally, iterate based on use
2. **Explicit > Implicit** - Clear syntax, obvious behavior
3. **Unique > Clone** - Physical-system compile-time model (plus effects/autodiff) rather than a Rust clone
4. **Portable > Fast** - C backend means runs anywhere; zero-cost escape hatches required

### Decision Authority

| What | Who Decides |
|------|-------------|
| Language design, syntax, features | Human (final authority) |
| Implementation, code structure | AI (proposes, human approves) |
| Bug fixes, refactoring | AI (within scope) |
| Roadmap priorities | Human |

---

## Examples & domains roadmap

Tourist-facing demos and domain coverage. Canonical "one entrypoint per domain"
lives in [examples/README.md](examples/README.md). The `examples/verify/` tree is
a proof corpus rather than the showcase.

### Further structure

- [x] Merge `examples/neural_networks/` → `examples/ml/autodiff/`
- [x] Fold `examples/system/` → `examples/systems/` (`system_info.flow`)
- [x] Remove misleading `examples/graphics/shader_showcase.flow` catalog stub (keep `shader_demo.flow`)
- [x] Add Tier-0 stubs: `stats/`, `net/`, `basics/result_pipeline`, `basics/match_enums`
- [x] Canonical entrypoints table in `examples/README.md`
- [x] UI layout tourist example under `examples/` (`examples/ui/layout_hello.flow`)
- [x] Packages / WASM showcase entrypoints (`examples/packages/`, `examples/wasm/hello_wasm.flow`)
- [x] Regenerate `examples/STATUS.md` after layout settles
- [x] Concurrency pipeline example once channel send/recv is exposed
- [x] RF beachhead examples under `examples/rf/` (W0: `dft.flow`, `iq_mixer.flow`)

### Tier 0: Minimum domains

| Domain | Entrypoint / note | Status |
|--------|-------------------|--------|
| Networking | `examples/net/tcp_echo.flow` (API shape; full echo loop planned) | ✅ |
| HTTP slice | `apps/flow-http/http.flow` | ✅ |
| Stats | `examples/stats/regression_gd.flow` | ✅ |
| FFI / C | Zero-bridge C interop in 0.11.0: `@cImport`/`@cInclude`/`@cEmbed`, `extern type`, `cfn(A) -> R`; BLAS bindings + `benchmarks/blas_vs_naive.flow`; `examples/interop/python_embed.flow` for Python | ✅ |
| WASM | `examples/wasm/hello_wasm.flow` | ✅ |
| Packages | `examples/packages/use_hello_lib/` | ✅ |
| Errors / Result | `examples/basics/result_pipeline.flow` | ✅ |
| Match | `examples/basics/match_enums.flow` | ✅ |
| RT audio `@rt_safe` | `examples/audio/lattice_allpass_phase_engine.flow` | ✅ |
| Verify repair | `examples/verify/circuits/full_adder.flow` (+ `.proof.md`); corpus ahead of checker | done |
| UI layout | `examples/ui/layout_hello.flow` | ✅ |
| Concurrency pipeline | `examples/concurrency/pipeline.flow` | ✅ |

### Tier 1: Vision domains

| Domain | Intent | Status |
|--------|--------|--------|
| Hybrid guarantees | Continuous + discrete with checkable invariants (`evolution/bouncing_ball`) | ✅ |
| Control + plant `dsys` flagship | `evolution/spring_mass_control.flow` / dynamics suite | ✅ |
| Units | Typed units / dimensional analysis showcase | ✅ (`units_kinematics`; RF in W0) |
| Digital twin lite | Small plant + observer narrative | ✅ |
| Embedded RT | Constrained / no-alloc RT path beyond audio policy | ✅ |
| RF / SDR beachhead | Quantity literals, IQ, rate-typed signals | 🔨 W0: `c64`/`c128` shipped, DFT + IQ mixer examples |
| Shader × sim | Couple shader fill with a sim loop (not catalog stubs) | ✅ |

### Tier 2: Competitive completeness

| Domain | Intent | Status |
|--------|--------|--------|
| Crypto beyond SHA | More than `examples/crypto/` SHA-256 | ✅ |
| JSON / TSV | Data interchange demos (`examples/data/json_parser.flow`, `tsv_parser.flow`) | ✅ |
| Compiler dogfood | Grow `examples/compilers/` into a real lexer/parser story | ✅ |
| Physics DSL honesty | Document what `physics/` can/can't do | ✅ |
| Linalg QR / eigen | Beyond LU / matrix_ops | ✅ |
| Games twin | Second polished interactive beyond Tetris/2048 | ✅ |

### Syntax & features to showcase

**Must-demo:**

| Feature | Where today / target |
|---------|----------------------|
| `\|>` pipe | docs + add a basics demo when surface is stable |
| `parallel for` | concurrency / GPU examples when API lands |
| `handle` / `with` | `examples/effects/showcase.flow` |
| Shader fill | real shader path; keep `shader_demo.flow` honest |
| `dsys` | `examples/dynamics/ga_dsys_syntax.flow` |
| Postfix chaining | recovered systems examples (`ring_buffer`, …) |
| Closures | `examples/generics_traits/closures_demo.flow` |
| `match` | `examples/basics/match_enums.flow` |
| `@gpu` | `examples/gpu/` |
| Theorems / verify | `examples/verify/` corpus |

**Avoid showcasing:**

- Ignored / no-op attributes
- Broken capability demos
- Duplicate XOR nets as the only ML story (keep one canonical: `ml/models/mlp_xor.flow`)

### Sequencing

| Sprint | Focus |
|--------|--------|
| **A** | Structure cleanup + Tier-0 stubs: merge autodiff, fold system/, stats/net/result/match |
| **B** | Wire real TCP echo + concurrency pipeline; UI layout tourist example |
| **C** | Shader×sim + units / digital-twin lite; regenerate STATUS |
| **D** | Tier-2 competitive gaps (QR/eigen, JSON, crypto breadth, WASM/packages entrypoints) |

---

## Tooling & Platform Priorities

The core language and self-hosted compiler are complete. Current platform and tooling priorities:

1. ✅ **Polish & Docs** - Wiki live at GitHub Pages, interactive tutorials app, language reference
2. ✅ **Async primitives** - Effects-based concurrency in stdlib `Async`/`AsyncIO` (`lib/stdlib/async.flow`), runnable `examples/effects/async_primitives.flow`
3. 🔲 **Debugger** - LLDB/GDB integration with source line mappings, step debugging (deferred; needs wasm compiler build)
4. ✅ **Web Playground** - `docs/playground/index.html` syntax explorer with compile-verified samples
5. 🔲 **Real-world projects** - Large production deployments proving out the physical systems beachhead
6. ✅ **Parser fix** - `ptr[0].field` unified postfix chaining shipped end-to-end
7. ✅ **Fuzz crashes** - array-size and nesting depth now clean `SyntaxError` regressions
8. ✅ **Codegen parity** - cgen failures cleared; verified in `examples/STATUS.md`

---

## What's Next? (Flow 2.0 Memory Safety)

✅ **[Flow 2.0 Epic] Ergonomic Memory Safety Architecture**
ROADMAP-SYNC: flow-2-0-epic-ergonomic-memory-safety-architecture

Shipped in Flow 2.0.0. Compile-time lifetime domain propagation, borrow inference, and effect-bounded lifetimes.
Reference: [docs/project/roadmap-2.0.md](docs/project/roadmap-2.0.md)

---

## Flow 3.0 Roadmap

1. 🔲 **Orchestration syntax** (#723, #724). `std.orchestrate` ships the combinators (`seq`, `fanout`, Result joins; see [docs/library/orchestrate.md](docs/library/orchestrate.md)). Syntax decisions will emerge from real library use, using a dedicated keyword or operator.
2. 🔲 **Hardware synthesis and partitioning**. Lower `@hardware` declarations to RTL, enforce clock domain crossings, and deploy across hardware-software boundaries.
3. 🔲 **Certified safety profiles**. Expand `--profile flight` with fault mitigation, static loop iteration bounds, and formal proofs of domain lattice rules.
4. 🔲 **Distributed digital twins**. Deploy identical code paths across simulation, RTOS environments, and bare metal targets.

---

## Milestone History & Archives

Flow follows semantic versioning. The 2.x line represents the current stable generation of the language.

| Version | Status | Milestone Focus | Archive Reference |
|---|---|---|---|
| **0.1 - 0.11** | Shipped | Core language, effects, autodiff, MLIR/C backends, initial self-hosting | [`docs/project/archive/ROADMAP-0.x.md`](docs/project/archive/ROADMAP-0.x.md) |
| **1.0.0** | Shipped | Release qualification, specification conformance, platform tiering | [`docs/project/archive/ROADMAP-1.0.md`](docs/project/archive/ROADMAP-1.0.md) |
| **2.0.0** | Current | Compile-time memory safety, borrow inference, full self-hosting `flowc` | [`docs/project/roadmap-2.0.md`](docs/project/roadmap-2.0.md) |
| **3.0.0** | Planned | Orchestration, hardware synthesis to RTL, certified safety profiles | Active roadmap above |

Detailed release notes and changelogs are maintained in [`CHANGELOG.md`](CHANGELOG.md).
