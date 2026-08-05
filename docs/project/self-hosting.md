# Self-Hosting Plan — Rewrite the Compiler in Flow

> **Status:** Active · Phases A–B on `main` · Phase C soft cutover (`FLOW_HOST`) · **Tracker:** GitHub issues labeled `self-hosting` · **Bootstrap tree:** [`compiler/`](../../compiler/)
>
> Goal: retire `src/flow/*.py` as the production compiler and make **`flowc`** (Flow→C, written in Flow) the sole host.

---

## Why

1. **Dogfood** — the language’s best stress test is compiling itself.
2. **Ship shape** — one toolchain story for users (no Python runtime required to build Flow programs long-term).
3. **Closer to the metal** — Stage-A already emits C; self-hosting forces the subset that systems code actually needs.

Python remains acceptable for **tooling** (wiki build, LSP glue, benches) until those are ported; it must not remain on the compile critical path.

---

## Non-goals (for the rewrite)

| Non-goal | Reason |
|----------|--------|
| Bit-identical AST with Python | Behavioral parity on the supported subset is enough |
| Porting MLIR/JIT in phase 1 | C backend first; MLIR stays Python/host optional |
| Porting every DSL day one | Dynamics / shaders / verify can stay host expanders until Stage-B |
| Deleting Python overnight | Dual-run until `./flow` defaults to `flowc` and CI is green |

---

## Current baseline (honest)

| Piece | Today |
|-------|--------|
| Production compiler | Python under `src/flow/` (`./flow` → transpile → `cc`) |
| Flow-written bootstrap | `compiler/` — lexer, parser, AST arena, Stage-A cgen/jsgen/fmt, light typecheck, multi-file bundle, self-emit fixed-point scripts |
| Can `flowc` compile `flowc` end-to-end? | **No** — Stage-A is a subset; roundtrip is fixture + frontend `.o` dogfood |
| Entry | `./flow run compiler/src/main.flow` (Python host runs Flow source) |

Detail: [`compiler/README.md`](../../compiler/README.md).

---

## Architecture target

```text
.flow source
    │
    ▼
 flowc (Flow) ──► C (or later MLIR)
    │
    ▼
   cc / clang
    │
    ▼
 native binary
```

Bootstrap ladder (classic):

1. **Gen0** — Python compiles `compiler/src/*.flow` → C → `flowc` objects/driver  
2. **Gen1** — Gen0 `flowc` re-emits frontend → `flowc_frontend_self.o`  
3. **Gen2** — Gen1 re-emits; `cmp` fixed-point with Gen1  
4. **Cutover** — `./flow` invokes GenN `flowc` by default; Python behind `FLOW_HOST=python`

---

## Phased plan

### Phase A — Land & CI the bootstrap  *(near-term)*

- Merge `compiler/` + Stage-A scripts onto `main`.
- CI job: `./compiler/scripts/roundtrip.sh` (and self-emit when stable).
- Document supported subset vs Python gaps in `compiler/README.md` (keep honest).

**Exit:** green CI roundtrip on every PR that touches `compiler/` or C codegen.

### Phase B — Close the Stage-A language gap

Expand `flowc` until it parses/emits everything the **compiler sources themselves** need:

- Full `import` / packages (no skip-at-emit)
- Generics enough for stdlib used by `flowc` (or keep `flowc` monomorphic)
- `match`, richer structs, string ops used in diagnostics
- Errors with locations (file:line)

**Exit:** `FLOWC_BUNDLE=1` builds all of `compiler/src` without `FLOWC_TYPECHECK=0` hacks except documented externs.

### Phase C — `flowc` replaces Python for `./flow run|build`  *(in progress)*

- Thin `./flow` shim: `FLOW_HOST=flowc` (default) | `python` | `auto`.
- Resolve driver via `compiler/scripts/ensure_flowc.sh` (prefers
  `stage_a_driver_flow_self`, bootstraps Gen0 with Phase-A roundtrip if needed).
- CI: after `roundtrip.sh`, smoke `FLOW_HOST=flowc ./flow run examples/basics/hello_world.flow`.
- Example/benchmark jobs keep `FLOW_HOST=python` until Stage-A covers the full
  language surface (Phase D).

**Exit:** default `./flow run examples/basics/hello_world.flow` does not import `src/flow/parser.py`.

### Phase D — Retire Python from the compile path

- Move remaining Python-only features (or reimplement):
  - dynamics / shader / verify preprocessors → Flow or keep as optional Python plugins
  - LSP: keep Python server talking to `flowc` JSON diagnostics, or rewrite later
- Archive or quarantine unused Python modules.
- README / getting-started: “requires `cc` + Flow binary,” not Python, for compile.

**Exit:** CI compile jobs have no `pip install` for the compiler itself.

### Phase E — Optional backends & polish

- MLIR/GPU paths as separate Flow modules or retained host tools.
- `flowc` packaging (Homebrew / releases) from self-hosted artifacts.
- Proof: three consecutive gen fixed-points in release CI.

---

## Suggested ownership split

| Area | Primary |
|------|---------|
| Lexer / parser / AST | `compiler/src/{token,lexer,parser,ast}.flow` |
| Typecheck / resolve | `compiler/src/{typecheck,resolve}.flow` |
| C emit | `compiler/src/cgen.flow` |
| Driver / CLI | `compiler/src/{main,driver}.flow` + tiny C host until argv is pure Flow |
| Host escape / FFI | `compiler/host/` shrink over time |
| Python parity tests | `tests/` + `compiler/scripts/roundtrip.sh` |

---

## Risk register

| Risk | Mitigation |
|------|------------|
| Subset forever | Track “blocks self-host” gaps as issues; refuse feature creep in Python without Flow twin |
| Bootstrap loops | Always keep a known-good Gen0 artifact in CI cache |
| Perf of Flow-hosted compiler | Profile after cutover; Stage-A is already C |
| DSLs block cutover | Allow Python pre-pass plugins with explicit `flow.toml` opt-in |

---

## Success metrics

1. `compiler/scripts/stage_a_self_emit_g2.sh` green on `main`.
2. Default `./flow` host is `flowc` for ≥90% of `examples/STATUS.md` pass set.
3. No Python import on the hot path of `flow build`.
4. Contributors edit `compiler/src/*.flow` for language bugs, not only `src/flow/*.py`.

---

## Related

- Roadmap §5.1 — [ROADMAP.md](../../ROADMAP.md)
- Bootstrap README — [compiler/README.md](../../compiler/README.md)
- Issues — label `self-hosting` on GitHub
