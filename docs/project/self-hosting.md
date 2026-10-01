# Self-Hosting Plan: Rewrite the Compiler in Flow

> **Status:** Active · Phases A-D done · Phase E landing (packaging + release CI) · **Tracker:** GitHub issues labeled `self-hosting` · **Bootstrap tree:** [`compiler/`](../../compiler/)
>
> Goal: retire `src/flow/*.py` as the production compiler and make **`flowc`** (Flow→C, written in Flow) the sole host.

---

## Why

1. **Dogfood**: the language's best stress test is compiling itself.
2. **Ship shape**: one toolchain story for users (no Python runtime required to build Flow programs long-term).
3. **Closer to the metal**: Stage-A already emits C; self-hosting forces the subset that systems code actually needs.

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
| Production compiler | `flowc`, the only C compiler. The Python C backend is retired; `FLOW_HOST=python` stops with an error. On the corpus flowc matches the retired backend on 1037 of 1053 programs with `main()` ([`report.txt`](../../compiler/corpus_parity/report.txt)) |
| Flow-written bootstrap | `compiler/`: lexer, parser, AST arena, Stage-A cgen/jsgen/fmt, typecheck, multi-file bundle, self-emit fixed-point scripts |
| Can `flowc` compile `flowc` end-to-end? | **Yes, for the Stage-A subset the compiler is written in.** All 17 modules of `compiler/src` bundle-emit C that `cc` accepts with zero diagnostics; the resulting binary passes flowc's own self-tests and reproduces itself for three generations ([`self_host_full.sh`](../../compiler/scripts/self_host_full.sh)) |
| Getting a compiler with no Python | `./compiler/scripts/bootstrap_from_c.sh`: `cc` on the checked-in [`compiler/bootstrap/flowc_stage_a.c`](../../compiler/bootstrap/flowc_stage_a.c) |
| Entry | `./flow run examples/...` (flowc host) · `./flow run compiler/src/main.flow` for the Flow source directly |

Detail: [`compiler/README.md`](../../compiler/README.md).

### Backends

Every backend is a module of `compiler/src`:

| Module | Output |
|--------|--------|
| `cgen` | C, the default path |
| `jsgen` | JavaScript |
| `mlirgen` | MLIR (`FLOWC_EMIT=mlir`), lowered by `compiler/scripts/mlir_lower.sh` |
| `metal_codegen` | Metal shaders for `@gpu` functions |
| `wgsl_codegen` | WGSL shaders for `@gpu` functions |
| `bpf_target` | eBPF subset checks |
| `bpf_gen` | eBPF bytecode |
| `wasm_gen` | WebAssembly |

### Language suite

The `.flow` files in `tests/lang/` are the language regression target. Run
them with `./flow test-lang`. The C output goldens are `tests/cgen/run.sh`.
The bare bootstrap loop over `tests/lang/` (no runtime libraries linked) is
in [`AGENTS.md`](../../AGENTS.md#bootstrap-suite), with its current count and
the remaining failures.

Features landed in the self-hosted compiler that closed earlier gaps:

- Enum tagged unions: `typedef enum { Name_V0 } Name_Tag; typedef struct { Name_Tag tag; } Name;`
- Enum variant references: bare `Red` emits as `Color_Red`
- Span indexing: `values[i]` on a `span<T>` variable emits as `values.data[i]`
- Span slicing: `xs[a..b]` on a span uses `.data` as the pointer base
- Array-to-span conversion: passing an `array<T, N>` to a `span<T>` parameter wraps it in `((flowc_span_T){ arr, N })`
- Lambda parsing and capturing lambdas via static globals
- Generic call syntax: `name<Type>(args)`
- Stable struct sort by first field with descending support
- `span<mut T>`, `&mut [T]`, `&[T]`, and slice syntax `a..b`

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

1. **Gen0**: `cc` builds `flowc` from the checked-in `compiler/bootstrap/flowc_stage_a.c`. (Before that C existed, Gen0 came from the Python compiler.)  
2. **Gen1**: Gen0 `flowc` compiles `compiler/src` → C → binary  
3. **Gen2**: Gen1 re-emits; `cmp` fixed-point with Gen1  
4. **Cutover**: `./flow` invokes GenN `flowc` for every C command. The Python C backend is retired

---

## Phased plan

### Phase A: Land & CI the bootstrap  *(near-term)*

- Merge `compiler/` + Stage-A scripts onto `main`.
- CI job: `./compiler/scripts/roundtrip.sh` (and self-emit when stable).
- Document supported subset vs Python gaps in `compiler/README.md` (keep honest).

**Exit:** green CI roundtrip on every PR that touches `compiler/` or C codegen.

### Phase B: Close the Stage-A language gap  *(done)*

**Exit:** `FLOWC_BUNDLE=1` builds all of `compiler/src` without `FLOWC_TYPECHECK=0`
hacks except documented externs. ✅

Gated by [`selfcompile_audit.sh`](../../compiler/scripts/selfcompile_audit.sh),
a roundtrip step: every module under `compiler/src` bundle-emits C that the C
compiler accepts with **zero** diagnostics. All 17 pass.

Landed along the way: real multi-file `import` with Kahn topo-sort, bundle
typecheck with a growing seed of dependency exports, diagnostics carrying
`file` + `line:col`, inferred `let`, `match` on integers, and string `+`.

**Progress (2026-08-05):** inferred `let` (no `: Type`), larger resolve/emit
src+AST caps, and `FLOWC_BUNDLE=1` typecheck of `compiler/src/main.flow` green.
Dogfood `compile_module` / self-emit / frontend bundles no longer force
`FLOWC_TYPECHECK=0` (imports seed names). Typecheck diagnostics print
`flowc tc: file` + path and `flowc tc: at line:col`.

**Progress (2026-08-05, match subset):** Stage-A `match` statement landed end
to end (lexer `match` keyword + `=>` token, parser, AST_MATCH/AST_MATCH_ARM,
typecheck, cgen). Subset: int-literal arms (incl. negative), `_` wildcard, and
a binding-ident catch-all. Guards, or-patterns, struct patterns, and list
patterns are rejected with clear diagnostics. C backend only: `jsgen` / `fmt`
do not lower AST_MATCH yet.

**Progress (2026-08-06, the two gaps that actually blocked self-compile):**

An audit of the emitted C (`FLOWC_BUNDLE=1` on each module, then `cc`) found
exactly two causes behind every failure.

1. *Inferred `let` had no type inference.* `let x = expr` with no annotation
   emitted `int32_t` for every initialiser, so a struct-returning call became
   `int32_t t = flowc_lexer_new(...)` and the next line did member access on an
   int. 28 errors in `main.flow` alone, and it is what makes a fixture like
   `stage_a_infer_call` silently wrong rather than merely unsupported.
   cgen now infers from the initialiser: casts and calls to functions in the
   same module use the declared type node; string / float / struct literals
   write the type directly; calls into other bundle modules read a
   `name\0ctype\0` table that `flowc_bundle_emit` fills deps-first.
2. *String `+` was pointer arithmetic.* `addr.carrier + "." + addr.structure`
   emitted C `+` on `const char*` and `char[2]`. Five modules
   (`claim_address`, `claim_path`, `know`, `math_prose`, `proof_sub`), four
   errors each. cgen now lowers it to a `__flowc_str_concat` helper emitted in
   the preamble (malloc + `memcpy`, never freed, same lifetime discipline as
   the compiler's other arenas). Detection is syntactic and conservative: a
   literal, a `+` chain containing one, a cast to `string`, or a call declared
   `-> string`. Two string values with neither a literal nor a call between
   them still emit `+` and are rejected by `cc`. The failure is loud and never wrong.

Fixtures that run and check their exit code: `stage_a_infer_struct` (42),
`bundle_infer_main` (42, cross-module), `stage_a_strcat` (42, reads every
result back through `strcmp`/`strlen`).

Since then flowc has gained generics, effects, the Field and dynamics DSLs,
flow blocks and the shader DSL, and it is now the only C compiler.

### Phase C: `flowc` replaces Python for `./flow run|build`  *(done: hard cutover)*

- Thin `./flow` shim. `FLOW_HOST=flowc` is the only value; `auto` is treated
  as flowc, and `python` stops with an error pointing to flowc.
  `FLOWC_BIN=<path>` picks a flowc binary.
- Resolve driver via `compiler/scripts/ensure_flowc.sh`, which builds flowc
  from the checked-in bootstrap C. `compiler/scripts/flowc_host.sh` prints a
  flowc built from the current `compiler/src`.
- CI: after `roundtrip.sh`, smoke `FLOW_HOST=flowc` on Stage-A basics.
- Example and benchmark jobs run on flowc.

**Exit:** default `./flow run examples/basics/hello_world.flow` does not import `src/flow/parser.py`. ✅

### Phase D: Retire Python from the compile path  *(done)*

**Exit:** CI user-compile jobs have no `pip install` for the compiler itself. ✅

- **Slice 1 (#197):** `flowc-compile` CI job compiles Stage-A programs from a
  downloaded driver artifact with no `pip install`.
- **Slice 2 (2026-08-06):** [`compiler/bootstrap/flowc_stage_a.c`](../../compiler/bootstrap/flowc_stage_a.c)
  is `driver.flow` plus every module it imports, emitted by flowc as one
  translation unit and checked in. `cc` on that file is a complete compiler, so
  a clean checkout needs **no Python at all**:

  ```bash
  ./compiler/scripts/bootstrap_from_c.sh
  ./flow run examples/basics/fibonacci.flow    # exit 55
  ```

  Verified with `python` and `python3` replaced by shims that exit 127 and log
  any call: no invocation, and the three-generation self-host chain runs clean
  under the same shims. CI job `flowc self-host (no Python)` has no
  `setup-python` step and repeats both checks.

  `ensure_flowc.sh` builds this. It once fell back to a Python Gen0
  roundtrip; that fallback is gone, and `flowc_host.sh` builds a flowc from
  the current `compiler/src` with the bootstrap binary.

  The checked-in C cannot drift: `bootstrap_from_c.sh --verify` runs in
  roundtrip and requires it to be byte-for-byte what flowc emits from
  `compiler/src` today. Regenerate with `--regen`.

**What still uses Python** (none of it on the compile path):

| Thing | Why |
|-------|-----|
| `flow python` wheel build | the Flow tool writes the extension source, `setup.py` and `pyproject.toml`; `pip wheel` with setuptools builds the Python artifact |
| `benchmarks/baselines/python/` | benchmark subjects that measure CPython and NumPy; Flow and bash harnesses run them and skip them when there is no python3 |
| `examples/interop/python/` | the Python modules Flow programs call through `lib/stdlib/python_embed.flow` |

No other tracked `.py` file exists. `./flow tool python_ratchet` excludes only
those two directories (and vendored trees) and fails on any other `.py`.

`flow check`, `flow analyze`, `flow fir-g`, `flow gpu`, `flow dap`, `flow bpf`,
`flow wasm32`, project-mode `flow test`, `flow run --json`, the package
commands (`init`, `publish`, `build`, `build-native`, `run-native`, `clean`)
and the doc example checkers are Flow tools. Each has a parity gate recorded
from the Python version it replaced.

### Phase E: Packaging & polish  *(in progress)*

- **Done:** three consecutive generation fixed-points in
  [`self_host_full.sh`](../../compiler/scripts/self_host_full.sh), run by
  roundtrip and by CI. gen1 = the bootstrap driver compiling all of
  `compiler/src`; gen2 = gen1 compiling it; gen3 = gen2 compiling it. Each
  generation must pass flowc's self-tests and compile an ordinary program, and
  `gen1.c == gen2.c == gen3.c` with `gen2.o == gen3.o`.
- **Done:** [`package_flowc.sh`](../../compiler/scripts/package_flowc.sh) →
  `dist/flowc-<version>-<os>-<arch>.tar.gz` with the binary, the bootstrap C,
  a `build.sh` that rebuilds it with `cc` alone, a LICENSE, and examples.
- **Done:** [`flowc-release.yml`](../../.github/workflows/flowc-release.yml) on
  `flowc-v*` tags: linux + macos, self-compile audit, fixed point, package,
  unpack and use the archive as a user would, publish with checksums.
- **Done (#695):** the `flow` command is a Flow program,
  [`tools/flow_cli`](../../tools/flow_cli/main.flow). `./flow` is a POSIX sh
  stub that builds it from the bootstrap C with `cc` on first use and execs
  it. The 4,311-line bash `flow-driver` is deleted; `tests/cli/run.sh` holds
  the CLI to goldens recorded from it.
- **Remaining:** Homebrew formula; a published release to point people at;
  optional MLIR/GPU as separate tracks.

---

## Suggested ownership split

| Area | Primary |
|------|---------|
| Lexer / parser / AST | `compiler/src/{token,lexer,parser,ast}.flow` |
| Typecheck / resolve | `compiler/src/{typecheck,resolve}.flow` |
| C emit | `compiler/src/cgen.flow` |
| Driver / CLI | `compiler/src/{main,driver}.flow` (flowc) and `tools/flow_cli` (the `flow` command) |
| Host escape / FFI | `compiler/host/` shrink over time |
| Python parity tests | `tests/` + `compiler/scripts/roundtrip.sh` |

---

## Risk register

| Risk | Mitigation |
|------|------------|
| Subset forever | Track "blocks self-host" gaps as issues; refuse feature creep in Python without Flow twin |
| Bootstrap loops | The checked-in bootstrap C is the known-good Gen0; `bootstrap_from_c.sh --verify` keeps it at a fixed point |
| Perf of Flow-hosted compiler | Profile after cutover; Stage-A is already C |
| DSLs block cutover | Allow Python pre-pass plugins with explicit `flow.toml` opt-in |

---

## Success metrics

1. Three consecutive generation fixed-points: ✅ `self_host_full.sh`, in roundtrip and CI.
2. Default `./flow` host is `flowc` for ≥90% of `examples/STATUS.md` pass set: ✅ flowc is the only C host, and on the corpus it matches the retired Python backend on 98.5% of programs with `main()`.
3. No Python import on the hot path of `flow build`: ✅ proven with `python`/`python3` shimmed to exit 127.
4. Contributors edit `compiler/src/*.flow` for language bugs as well as `src/flow/*.py`: ongoing.

---

## Related

- Roadmap §5.1: [ROADMAP.md](../../ROADMAP.md)
- Bootstrap README: [compiler/README.md](../../compiler/README.md)
- Issues: label `self-hosting` on GitHub
