# Python compiler → Flow

> Status: hybrid, see [self-hosting plan](self-hosting.md).
> Default `./flow run|compile` is Stage-A **flowc** (`FLOW_HOST=flowc`).
> Full language / DSLs / tests still use `FLOW_HOST=python` (`src/flow/`).

Production Python compiler lives in [`src/flow/`](../../src/flow/).
Stage-A self-host lives in [`compiler/`](../../compiler/) (`flowc`).

## Stage-A status (honest)

| Claim | Reality |
|---|---|
| Default `./flow compile` / `./flow run` | **flowc** (Stage-A subset); escape hatch `FLOW_HOST=python` |
| Stage-A lexer / parser / cgen / typecheck / resolve | Landed in `compiler/src/*.flow`; fixtures + module dogfood |
| Emit → cc → run for subset fixtures | Works (sum/fib/structs/ptr/bundle/…) |
| Self-emit fixed-point (`stage_a_self_emit*.sh`) | Works for the Stage-A frontend object graph |
| Full language without Python host | **No**, effects, generics, match, gfx, MLIR, DSLs stay host |
| CI user-compile without `pip install` | **Yes**, `flowc-compile` job (Phase D slice 1) |
| Flow-in-WASM compiler | **No**, see [wasm.md](../language/wasm.md) |

Minimal proof that flowc round-trips one fixture (exits non-zero on failure):

```bash
./compiler/scripts/stage_a_smoke.sh
```

Full Stage-A suite (fixtures + frontend modules + driver + self-emit):

```bash
./compiler/scripts/roundtrip.sh
```

## Host plugins (stay on `FLOW_HOST=python`)

These are intentional Python host plugins until Flow ports exist. Do not delete
them as part of Phase D; call them via the escape hatch:

| Plugin / module | Role |
|---|---|
| `dynamics_dsl.py` / `flow_blocks.py` | Dynamics DSL expand-before-parse |
| `shader_dsl.py` / `shader_codegen.py` | Shader DSL |
| Verify / proof modules | `proof_*.py`, math prose host path |
| `lsp_server.py` | LSP (may shell out to flowc later) |
| `mlir_*.py`, GPU runtimes | MLIR / Metal / numpy |
| `test_runner.py`, `package.py`, `repl.py` | Tests, packaging, TTY |

## Boundary

| Stay Python / host | Why |
|---|---|
| `./flow` bash + Gen0 bootstrap | orchestrates flowc; Gen0 still emits via `src/flow` once |
| `mlir_jit.py`, `mlir_optimizer.py`, GPU/Metal **runtimes** | subprocess, ctypes, numpy |
| `lsp_server.py`, `package.py`, `repl.py`, `test_runner.py` | JSON-RPC, git/network, TTY, pytest |
| `python_generator.py` (wheel) | setuptools/pip |
| Full `proof_document.py` / PDF / matplotlib kernels | host tools |

| Landed in Flow | Where |
|---|---|
| Repo stats counter | [`scripts/tools/repo_stats/main.flow`](../../scripts/tools/repo_stats/main.flow) via [`scripts/update_repo_stats.sh`](../../scripts/update_repo_stats.sh) (git dump stays in shell) |
| Claim Coordinates | [`compiler/src/claim_address.flow`](../../compiler/src/claim_address.flow) |
| Claim path + fingerprint | [`compiler/src/claim_path.flow`](../../compiler/src/claim_path.flow) |
| Math prose (core) | [`compiler/src/math_prose.flow`](../../compiler/src/math_prose.flow) — incl. `flowc_mathematical_case_condition` (exact port: word-boundary `== true/false/0` + `==`→` equals ` fallback; Stage-A string char-indexing) |
| Premise instantiate | [`compiler/src/proof_sub.flow`](../../compiler/src/proof_sub.flow) |
| `flow know` helpers | [`compiler/src/know.flow`](../../compiler/src/know.flow), normalize/qualify/match/print + theorem-header scan |
| Stage-A JS / fmt | [`jsgen.flow`](../../compiler/src/jsgen.flow) / [`fmt.flow`](../../compiler/src/fmt.flow) |
| LSP ordering gloss | [`examples/compilers/lsp_ordering_port.flow`](../../examples/compilers/lsp_ordering_port.flow) |
| Lexer / parser / cgen / typecheck / resolve | [`compiler/src/`](../../compiler/src/) — floats, `pkg_add`, `for ..` / `to`, bundles, runtime string concat (`+` → `flow_strcat`) |

Where a Flow port replaces a Python script that still exists, the Python
stays as the reference and the shim diffs the two on every run. The repo
stats counter works this way: `update_repo_stats.sh` runs Flow, then fails
loudly if `update_repo_stats.py` disagrees with what Flow wrote.

| Still rewrite priority | Target |
|---|---|
| Grow parser/cgen | more of production C path |
| Full proof parse / `flow doc proof` | remaining `proof_document.py` |
| Expr→English / LaTeX | remaining `math_prose.py` — `mathematical_case_condition` landed; the regex-rewrite prose (`_normalize_geometry_tokens`, `_replace_word`) still needs general word replacement on strings |
| Recursive claim index over disk | wrap `know` + `fileio` + directory walk |

## Phases

1. **Satellites**, pure string/AST walkers ← largely landed
2. **Stage-A basics C path**, ten Stage-A-clean `examples/basics/*` via `emit_basics.sh`
3. **Language surface**, effects/generics/match after Stage-A can express them
4. **Optional**, full proof PDF / shader emitters (host-run)

## Dogfood

```bash
./compiler/scripts/stage_a_smoke.sh
FLOW_HOST=python ./flow run compiler/src/main.flow
./compiler/scripts/roundtrip.sh
FLOWC_EMIT_ONLY=1 ./compiler/scripts/emit_basics.sh
./compiler/scripts/smoke_math_prose.sh
./compiler/scripts/smoke_know.sh
FLOW_HOST=python ./flow run examples/compilers/claim_address_demo.flow
FLOW_HOST=python ./flow run examples/compilers/math_prose_demo.flow
FLOW_HOST=python ./flow run examples/compilers/know_demo.flow
```

Python remains the Gen0 bootstrap and the full-language host until Stage-A covers
those surfaces; default Stage-A user compile is already flowc.
