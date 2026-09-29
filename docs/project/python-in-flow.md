# Python compiler → Flow

> Status: hybrid. See [self-hosting plan](self-hosting.md).
> **flowc** is the only C compiler. `./flow run`, `compile`, `test`,
> `test-lang` and the other C commands all use it, and since #960 they run
> with no Python on `PATH`. The Python C backend (`c_generator.py`) is
> retired and `FLOW_HOST=python` stops with an error. Python still runs the
> MLIR backend (generator fallback, JIT, GPU lowering), the setuptools wheel
> build of `flow python`, and the scripts listed in
> [self-hosting.md](self-hosting.md).
> New code is written in Flow. `scripts/python_ratchet.sh` fails CI when a new
> `.py` file appears or tracked Python grows (#981).

The compiler is [`compiler/`](../../compiler/) (`flowc`). The Python modules
that remain live in [`src/flow/`](../../src/flow/).

This page describes what is merged on `main`. Open pull requests are listed as
in progress and are not counted as landed.

## Stage-A status

| Claim | Reality |
|---|---|
| Default `./flow compile` / `./flow run` | **flowc**, the only C compiler. `FLOW_HOST=python` is retired and stops with an error |
| `./flow run` with no Python installed | **Yes** on the flowc host (#960). The package sync decision is `scripts/tools/pkg_sync/main.flow`; a project that must fetch a dependency runs the Flow package manager (`compiler/src/pkg_main.flow`). `scripts/check_run_without_python.sh` checks it |
| Stage-A lexer / parser / cgen / typecheck / resolve | Landed in `compiler/src/*.flow`; fixtures + module dogfood |
| Emit → cc → run for subset fixtures | Works (sum/fib/structs/ptr/bundle/…) |
| Self-emit fixed-point (`stage_a_self_emit*.sh`) | Works for the Stage-A frontend object graph |
| Full language on the C path without Python | **Yes**. On the corpus flowc matches the retired Python backend on 1037 of 1053 programs with `main()` and builds 6 it could not ([`report.txt`](../../compiler/corpus_parity/report.txt)). The MLIR backend still falls back to the Python generator |
| CI user-compile without `pip install` | **Yes**: `flowc-compile` job (Phase D slice 1) |
| Flow-in-WASM compiler | **No**. See [wasm.md](../language/wasm.md) |

Minimal proof that flowc round-trips one fixture (exits non-zero on failure):

```bash
./compiler/scripts/stage_a_smoke.sh
```

Full Stage-A suite (fixtures + frontend modules + driver + self-emit):

```bash
./compiler/scripts/roundtrip.sh
```

## Python modules and their Flow ports

These Python modules were the Python host's plugins. The C path now runs
the Flow port of each one. The table records where each port stands.

| Plugin / module | Role | Flow port |
|---|---|---|
| `field_dsl.py` | Thin bridge for the remaining Python tools: calls flowc with `FLOWC_EXPAND_ONLY=1` | Complete in [`field_dsl.flow`](../../compiler/src/field_dsl.flow) (#956) |
| `dynamics_dsl.py` / `flow_blocks.py` | Dynamics DSL and `flow` block lowering | Line helpers in [`dynamics_dsl.flow`](../../compiler/src/dynamics_dsl.flow). Full expansion in flowc: open PR #999 |
| `shader_dsl.py` / `shader_codegen.py` / `shader_codegen_wgsl.py` | Shader DSL (FSL) and its Metal and WGSL backends | Parsing and validation in [`shader_dsl.flow`](../../compiler/src/shader_dsl.flow). Both backends in flowc: open PR #998 |
| Verify / proof modules | `proof_*.py`, math prose host path | Helpers landed (see below); document assembly and PDF stay Python |
| `repl.py` | `flow repl` | A REPL written in Flow (`tools/repl/main.flow`): open PR #987 |
| `test_runner.py` | No callers | Deleted in open PR #987 |
| `package.py`, `registry.py` | Every package command | Ported to `compiler/src/pkg.flow` and `pkg_main.flow`; both Python files are deleted |
| `mlir_*.py`, GPU runtimes | MLIR / Metal / numpy | Core-language MLIR text in flowc ([`mlirgen.flow`](../../compiler/src/mlirgen.flow), `FLOWC_EMIT=mlir`); lowering in [`mlir_lower.sh`](../../compiler/scripts/mlir_lower.sh). Plan and slice order: [MLIR in Flow](../design/mlir-in-flow.md) |

## Boundary

| Stay Python / host | Why |
|---|---|
| `./flow` bash | orchestrates flowc. The bootstrap needs no Python: flowc is built from `compiler/bootstrap/flowc_stage_a.c` with `cc` |
| `mlir_generator.py` | fallback when the Flow MLIR emitter cannot handle a program (`--backend=mlir`) |
| `mlir_jit.py` loading half, GPU/Metal **runtimes** | ctypes, numpy; planned to move to C (see [MLIR in Flow](../design/mlir-in-flow.md)) |
| `pip wheel` in `flow python` | building the wheel needs setuptools. The generator is the Flow tool `tools/pywheel` |
| `wasm/flow_to_wasm.py` | takes its C from `compiler/scripts/flowc_emit.sh`. The GPU crossing and the WebGPU shader page moved to `wasm/crossings.sh gpu` and `wasm/crossings.sh shader` |
| `benchmarks/**/python/*` baselines | the Python side of a Python-versus-Flow comparison |

## Scripts and tools ported to Flow

Each port is a Flow program under `scripts/tools/<name>/main.flow` behind a
bash shim. `scripts/tools/build_tool.sh` builds the Stage-A compiler from
`compiler/bootstrap/flowc_stage_a.c` with `cc` and compiles the tool, so these
need no Python. The Python original was deleted in the same pull request.

| Was (deleted) | Now | PR |
|---|---|---|
| `scripts/check_doc_links.py` | [`scripts/check_doc_links.sh`](../../scripts/check_doc_links.sh) → `scripts/tools/doc_links` | #959 |
| `scripts/check_doc_coverage.py` | [`scripts/check_doc_coverage.sh`](../../scripts/check_doc_coverage.sh) → `scripts/tools/doc_coverage` | #959 |
| `scripts/check_wiki_links.py` | [`scripts/check_wiki_links.sh`](../../scripts/check_wiki_links.sh) → `scripts/tools/wiki_links` | #959 |
| `scripts/check_stability_manifest.py` | [`scripts/check_stability_manifest.sh`](../../scripts/check_stability_manifest.sh) → `scripts/tools/stability_manifest` | #959 |
| `scripts/sync_version.py` | [`scripts/sync_version.sh`](../../scripts/sync_version.sh) → `scripts/tools/sync_version` | #959 |
| `scripts/sync_roadmap.py` | [`scripts/sync_roadmap.sh`](../../scripts/sync_roadmap.sh) → `scripts/tools/roadmap_sync` | #959 |
| `challenges/flow-specific/check.py` | [`challenges/flow-specific/check.sh`](../../challenges/flow-specific/check.sh) → `scripts/tools/challenge_check` | #965 |
| `tools/grad/flow_grad_c.py`, `flow_grad_flow.py` | [`scripts/tools/grad/grad.sh`](../../scripts/tools/grad/grad.sh) | #965 |
| `tools/size/measure_size.py` | [`scripts/tools/measure_size/measure_size.sh`](../../scripts/tools/measure_size/measure_size.sh) | #965 |
| `wasm/flow_wasm_{threads,sockets,python,fs,crossings}.py` | [`wasm/crossings.sh`](../../wasm/crossings.sh) → `scripts/tools/wasm_crossings` | #965 |
| `benchmarks/baselines/run_baselines.py` | [`benchmarks/baselines/run_baselines.sh`](../../benchmarks/baselines/run_baselines.sh) → `scripts/tools/bench_baselines` | #965 |
| `benchmarks/run_publish.py` | [`benchmarks/run_publish.sh`](../../benchmarks/run_publish.sh) → `scripts/tools/bench_publish` | #965 |
| None (new) | [`scripts/python_ratchet.sh`](../../scripts/python_ratchet.sh) → `tools/python_ratchet/main.flow` | #981 |

#965 also deleted Python with no port: the Euclid book generators, the backlog
sorters, `flow_debug.py`, `flow_jit_opt.py`, `simd_check.py` and other
superseded scripts. Its description lists each one with the reason.

Tests move the same way. #966 fixed the Stage-A bugs that kept run tests in
Python and ported those tests to `tests/lang/`. See
[tests-in-flow.md](tests-in-flow.md).

### In progress (open pull requests)

| PR | Scope |
|---|---|
| #971 | The remaining `scripts/*.py`: changelog check, release prep, repo stats, stdlib docs, wiki build, wasm and shader galleries, and others |
| #955 | Python run tests to `tests/lang`, batch 2 |
| #998 | Shader DSL and both backends in flowc; `shader_codegen*.py` deleted |
| #999 | Dynamics DSL and `flow` block lowering in flowc |
| #987 | REPL in Flow; `repl.py` and `test_runner.py` deleted; LSP stays Python |
| #693 | Language server in Flow (`tools/lsp/main.flow`); `lsp_server.py`, `lsp_intel.py`, `lsp_syntax.py`, `lsp_dynamics.py` and `lsp_ordering.py` deleted |
| #989 | Package manager in Flow |
| #1001 | flowc parses every `.flow` file the Python parser accepts |

## Compiler modules ported to Flow

| Landed in Flow | Where |
|---|---|
| Repo stats counter | [`scripts/tools/repo_stats/main.flow`](../../scripts/tools/repo_stats/main.flow) via [`scripts/update_repo_stats.sh`](../../scripts/update_repo_stats.sh) (git dump stays in shell) |
| Claim Coordinates | [`compiler/src/claim_address.flow`](../../compiler/src/claim_address.flow) |
| Claim path + fingerprint | [`compiler/src/claim_path.flow`](../../compiler/src/claim_path.flow) |
| Math prose (**complete**) | [`compiler/src/math_prose.flow`](../../compiler/src/math_prose.flow): the whole of `math_prose.py`: coordinates and tier openings, plus `flowc_flow_expr_to_mathematical_english` / `flowc_flow_expr_to_latex` / `flowc_geometry_expr_to_latex` / `flowc_analysis_expr_to_latex` / `flowc_invoke_premise_mathematical`. Regex replaced by hand-written single-pass scans. Gated with the rest of the proof layer by [`parity_proofs.sh`](../../compiler/scripts/parity_proofs.sh) |
| Premise instantiate | [`compiler/src/proof_sub.flow`](../../compiler/src/proof_sub.flow) |
| Require/prefer constraints | [`compiler/src/constraints.flow`](../../compiler/src/constraints.flow): `flowc_parse_require` / `flowc_parse_prefer` / tighter-value picker |
| Convention avoid-pattern matcher | [`compiler/src/conventions.flow`](../../compiler/src/conventions.flow): `flowc_contains_ci` / `flowc_check_source` (TOML loading stays Python) |
| MISRA/CERT C scanner (**complete**) | [`compiler/src/misra_scan.flow`](../../compiler/src/misra_scan.flow): `flowc_scan_c_source` flags heap/stdio/abort calls; `flowc_misra_report` is the whole `misra_scan.py` report. `flow analyze` runs it from [`tools/analyze/main.flow`](../../tools/analyze/main.flow) |
| WCET and stack depth (**complete**) | [`tools/analyze/main.flow`](../../tools/analyze/main.flow) over the flowc parser, with the tables in [`compiler/src/wcet.flow`](../../compiler/src/wcet.flow). Replaces `wcet_analysis.py`; gated by [`tests/tools/analyze/run.sh`](../../tests/tools/analyze/run.sh) |
| Function attribute vocabulary | [`compiler/src/attributes.flow`](../../compiler/src/attributes.flow): `flowc_parse_attribute` / `flowc_validate_target_spec` / `flowc_domain_rank` |
| Matmul/reduce cost models | [`compiler/src/general_plans.flow`](../../compiler/src/general_plans.flow): `flowc_select_matmul` / `flowc_select_reduce` (pure cost/applicability, registry stays Python) |
| FIR-G effect propagation | [`compiler/src/fir_analysis.flow`](../../compiler/src/fir_analysis.flow): `flowc_propagate_effects` / `flowc_reachable_functions` / `flowc_is_pure` (CSR graph, fixpoint OR) |
| FIR-G opt candidate scoring | [`compiler/src/fir_opts.flow`](../../compiler/src/fir_opts.flow): `flowc_score_inline` / `flowc_score_dead_elim` / `flowc_compare_candidates` |
| FIR-G routing decision | [`compiler/src/fir_route.flow`](../../compiler/src/fir_route.flow): `flowc_choose_analysis_backend` |
| FIR-G tool (**complete**) | [`tools/fir/main.flow`](../../tools/fir/main.flow): `flow fir-g`, graphify on the flowc front end, monomorphization, analyses, candidates, routing and calibration. Gated by [`tests/fir/run.sh`](../../tests/fir/run.sh) against goldens from the retired Python tool |
| Language server (**complete**) | [`tools/lsp/main.flow`](../../tools/lsp/main.flow): JSON-RPC over stdio, diagnostics from the flowc parser and Stage-A checker in process, hover, completion, definition, references, highlight, rename, document symbols, formatting through [`fmt.flow`](../../compiler/src/fmt.flow) and idiom code actions. `./flow lsp` and `./flow-lsp` run it. Gated by [`tests/tools/lsp/run.sh`](../../tests/tools/lsp/run.sh): recorded sessions diffed against the retired Python server, with the accepted differences listed in [`ACCEPTED.md`](../../tests/tools/lsp/ACCEPTED.md) |
| LSP syntax token detection | [`compiler/src/lsp_syntax.flow`](../../compiler/src/lsp_syntax.flow): `flowc_syntax_token_at_position` / `flowc_is_multi_char_op` |
| LSP receiver/field detection | [`compiler/src/lsp_intel.flow`](../../compiler/src/lsp_intel.flow): `flowc_receiver_before_dot` / `flowc_field_access_at` |
| Proof tools (**complete**) | [`compiler/src/proof_doc.flow`](../../compiler/src/proof_doc.flow), [`geometry_diagram.flow`](../../compiler/src/geometry_diagram.flow) and [`geometry_script.flow`](../../compiler/src/geometry_script.flow): the whole of the former `proof_document.py`, `geometry_diagram.py`, `geometry_script.py`, `proof_kernel.py`, `know.py`, `claim_address.py`, `claim_path.py`, `math_prose.py` and `proof_substitution.py`. `flow doc proof`, `flow doc bundle`, `flow doc kernel` and `flow know` run on flowc, and the driver keeps only the LaTeX engine call. In programs, `theorem`, `assume`, `therefore` and claim references are erased by [`proof_lower.flow`](../../compiler/src/proof_lower.flow). Gated by [`parity_proofs.sh`](../../compiler/scripts/parity_proofs.sh): every examples/verify file against the Python at any revision, byte for byte |
| Dynamics DSL line helpers | [`compiler/src/dynamics_dsl.flow`](../../compiler/src/dynamics_dsl.flow): `flowc_strip_comments` / `flowc_strip_dynamics_namespace` (full DSL parsing and expansion stay Python) |
| LSP utility helpers | [`compiler/src/lsp_utils.flow`](../../compiler/src/lsp_utils.flow): `flowc_is_valid_identifier` / `flowc_word_range` / `flowc_completion_prefix` |
| Field DSL expansion (**complete**) | [`compiler/src/field_dsl.flow`](../../compiler/src/field_dsl.flow): the whole of the former `field_dsl.py`, covering detection, `field` / `boundary` / `evolves as laplacian` parsing, diagnostics, and `T_field_step` generation. flowc runs it on every source it reads (`main.flow`, `driver.flow`, all bundle passes in `resolve.flow`), so `./flow compile examples/evolution/heat_diffusion.flow` needs no Python. `src/flow/field_dsl.py` is now a bridge that shells out to flowc. Gated by [`parity_field_dsl.sh`](../../compiler/scripts/parity_field_dsl.sh): 21 fixtures against goldens recorded from the Python expander, 1995-file passthrough, an optional live diff against the Python at any revision, and heat_diffusion compiled and run on flowc |
| DSL detection | [`compiler/src/dsl_detect.flow`](../../compiler/src/dsl_detect.flow): `flowc_has_field_dsl` / `flowc_has_dynamics_dsl` / `flowc_has_fill_shader_dsl` (dynamics and shader expansion stay Python) |
| LSP ordering hover | [`compiler/src/lsp_ordering.flow`](../../compiler/src/lsp_ordering.flow): `flowc_ordering_hover` |
| LSP dynamics hover | [`compiler/src/lsp_dynamics.flow`](../../compiler/src/lsp_dynamics.flow): `flowc_dynamics_hover` |
| WCET analysis helpers | [`compiler/src/wcet.flow`](../../compiler/src/wcet.flow): `flowc_type_size` / `flowc_stmt_cost` / `FLOWC_DEFAULT_LOOP_BOUND` (AST traversal and report formatting stay Python) |
| Stage-A JS / fmt | [`jsgen.flow`](../../compiler/src/jsgen.flow) / [`fmt.flow`](../../compiler/src/fmt.flow) |
| LSP ordering gloss | [`examples/compilers/lsp_ordering_port.flow`](../../examples/compilers/lsp_ordering_port.flow) |
| Lexer / parser / cgen / typecheck / resolve | [`compiler/src/`](../../compiler/src/): floats, `pkg_add`, `for ..` / `to`, bundles |

Where a Flow port replaces a Python script that still exists, the Python
stays as the reference and the shim diffs the two on every run. The repo
stats counter works this way: `update_repo_stats.sh` runs Flow, then fails
loudly if `update_repo_stats.py` disagrees with what Flow wrote. Open PR #971
drops that cross-check and deletes the Python.

| Still rewrite priority | Target |
|---|---|
| Grow parser/cgen | more of production C path |

## Porting notes

**Module-private helpers share one namespace inside a bundle.** Stage-A emits a
non-exported `function` under its plain name, so two modules that each define
their own `str_append` collide the moment an `import` puts them in the same
bundle. Nine modules under `compiler/src` defined one. The audit catches it as
`redefinition of 'str_append'` in the emitted C.

Prefix private helpers with the module (`mp_`, `pd_`, `kn_`) before adding an
import. `math_prose.flow`, `proof_document.flow`, and `know.flow` are already
prefixed. `attributes`, `conventions`, `geometry_diagram`, `misra_scan`,
`proof_sub`, `proof_kernel`, and `claim_path` still define a bare
`str_append`, so importing any two of those into one bundle will fail until
they are renamed or a shared `flowc_str_append` moves into `strutil.flow`.

**Regex has no Stage-A equivalent.** Every `re.sub` becomes a hand-written
left-to-right scan that advances past what it consumed, which is the same
non-overlapping rule `re.sub` uses. Where Python relies on iteration order of a
dict or a set, say so in a comment: `_latex_escape` depends on its dict order,
and the claim index keys do not depend on set order.

**Reserved words bite.** `from` and `to` are Flow keywords, so a helper ported
from `replace(s, from, to)` needs different parameter names.

## Phases

1. **Satellites**: pure string/AST walkers ← largely landed
2. **Stage-A basics C path**: ten Stage-A-clean `examples/basics/*` via `emit_basics.sh`
3. **Language surface**: effects/generics/match after Stage-A can express them
4. **Optional**: full proof PDF / shader emitters (host-run)

## Dogfood

```bash
./compiler/scripts/stage_a_smoke.sh
./flow run compiler/src/main.flow
./compiler/scripts/roundtrip.sh
FLOWC_EMIT_ONLY=1 ./compiler/scripts/emit_basics.sh
./compiler/scripts/smoke_math_prose.sh
./compiler/scripts/parity_proofs.sh
./compiler/scripts/smoke_know.sh
./compiler/scripts/parity_field_dsl.sh
./flow run examples/compilers/claim_address_demo.flow
./flow run examples/compilers/math_prose_demo.flow
./flow run examples/compilers/math_prose_expr_demo.flow
./flow run examples/compilers/proof_parse_demo.flow
./flow run examples/compilers/know_index_demo.flow
./flow run examples/compilers/know_demo.flow
```

flowc compiles the whole C path and rebuilds itself from the checked-in C
with `./compiler/scripts/bootstrap_from_c.sh --regen`. Python remains for the
tools listed under Boundary.
