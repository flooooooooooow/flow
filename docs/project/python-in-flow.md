# Python compiler → Flow

> Status: hybrid forever — see the broader
> [self-hosting plan](self-hosting.md). Python is still the **production**
> compiler; Stage-A `flowc` is a dogfood subset, not a replacement.

Production compiler lives in [`src/flow/`](../../src/flow/) (~32k LOC Python).
Stage-A self-host lives in [`compiler/`](../../compiler/) (`flowc`).

## Stage-A status (honest)

| Claim | Reality |
|---|---|
| Production `./flow compile` / `./flow run` | Still Python (`src/flow/`) |
| Stage-A lexer / parser / cgen / typecheck / resolve | Landed in `compiler/src/*.flow`; fixtures + module dogfood |
| Emit → cc → run for subset fixtures | Works (sum/fib/structs/ptr/bundle/…) |
| Self-emit fixed-point (`stage_a_self_emit*.sh`) | Works for the Stage-A frontend object graph |
| Replaces Python host for real programs | **No** — effects, generics, match, gfx, MLIR, packaging stay host |
| Flow-in-WASM compiler | **No** — see [wasm.md](../language/wasm.md) |

Minimal proof that flowc round-trips one fixture (exits non-zero on failure):

```bash
./compiler/scripts/stage_a_smoke.sh
```

Full Stage-A suite (fixtures + frontend modules + driver + self-emit):

```bash
./compiler/scripts/roundtrip.sh
```

## Boundary

| Stay Python / host | Why |
|---|---|
| `./flow` bash, `transpiler.py` CLI | packaging, cc/Metal/MLIR orchestration |
| `mlir_jit.py`, `mlir_optimizer.py`, GPU/Metal **runtimes** | subprocess, ctypes, numpy |
| `lsp_server.py`, `package.py`, `repl.py`, `test_runner.py` | JSON-RPC, git/network, TTY, pytest |
| `python_generator.py` (wheel) | setuptools/pip |
| Full `proof_document.py` / PDF / matplotlib kernels | host tools |

| Landed in Flow | Where |
|---|---|
| Repo stats counter | [`scripts/tools/repo_stats/main.flow`](../../scripts/tools/repo_stats/main.flow) via [`scripts/update_repo_stats.sh`](../../scripts/update_repo_stats.sh) (git dump stays in shell) |
| Claim Coordinates | [`compiler/src/claim_address.flow`](../../compiler/src/claim_address.flow) |
| Claim path + fingerprint | [`compiler/src/claim_path.flow`](../../compiler/src/claim_path.flow) |
| Math prose (core) | [`compiler/src/math_prose.flow`](../../compiler/src/math_prose.flow) |
| Premise instantiate | [`compiler/src/proof_sub.flow`](../../compiler/src/proof_sub.flow) |
| `flow know` helpers | [`compiler/src/know.flow`](../../compiler/src/know.flow) — normalize/qualify/match/print + theorem-header scan |
| Stage-A JS / fmt | [`jsgen.flow`](../../compiler/src/jsgen.flow) / [`fmt.flow`](../../compiler/src/fmt.flow) |
| LSP ordering gloss | [`examples/compilers/lsp_ordering_port.flow`](../../examples/compilers/lsp_ordering_port.flow) |
| Lexer / parser / cgen / typecheck / resolve | [`compiler/src/`](../../compiler/src/) — floats, `pkg_add`, `for ..` / `to`, bundles |

| Still rewrite priority | Target |
|---|---|
| Grow parser/cgen | more of production C path |
| Full proof parse / `flow doc proof` | remaining `proof_document.py` |
| Expr→English / LaTeX | remaining `math_prose.py` |
| Recursive claim index over disk | wrap `know` + `fileio` + directory walk |

## Phases

1. **Satellites** — pure string/AST walkers ← largely landed
2. **Stage-A basics C path** — ten Stage-A-clean `examples/basics/*` via `emit_basics.sh`
3. **Language surface** — effects/generics/match after Stage-A can express them
4. **Optional** — full proof PDF / shader emitters (host-run)

## Dogfood

```bash
./compiler/scripts/stage_a_smoke.sh
./flow run compiler/src/main.flow
./compiler/scripts/roundtrip.sh
FLOWC_EMIT_ONLY=1 ./compiler/scripts/emit_basics.sh
./compiler/scripts/smoke_math_prose.sh
./compiler/scripts/smoke_know.sh
./flow run examples/compilers/claim_address_demo.flow
./flow run examples/compilers/math_prose_demo.flow
./flow run examples/compilers/know_demo.flow
```

Python remains the production driver until Stage-A covers the C path without host emit.
