# Python compiler → Flow

> Status: hybrid — see [self-hosting plan](self-hosting.md).
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
| Full language without Python host | **No** — effects, generics, match, gfx, MLIR, DSLs stay host |
| CI user-compile without `pip install` | **Yes** — `flowc-compile` job (Phase D slice 1) |
| Flow-in-WASM compiler | **No** — see [wasm.md](../language/wasm.md) |

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
| Math prose (**complete**) | [`compiler/src/math_prose.flow`](../../compiler/src/math_prose.flow) — the whole of `math_prose.py`: coordinates and tier openings, plus `flowc_flow_expr_to_mathematical_english` / `flowc_flow_expr_to_latex` / `flowc_geometry_expr_to_latex` / `flowc_analysis_expr_to_latex` / `flowc_invoke_premise_mathematical`. Regex replaced by hand-written single-pass scans. Gated by [`parity_math_prose_expr.py`](../../compiler/scripts/parity_math_prose_expr.py) |
| Premise instantiate | [`compiler/src/proof_sub.flow`](../../compiler/src/proof_sub.flow) |
| `flow know` helpers + **index and rendering** | [`compiler/src/know.flow`](../../compiler/src/know.flow) — normalize/qualify/match/print, plus `flowc_default_search_roots` / `flowc_claim_index_keys` / `flowc_lookup_matches` / `flowc_format_know`. The rendered entry runs the claim expression through the Flow English and LaTeX ports. Walking the search roots and reading files stay Python. Gated by [`parity_know_index.py`](../../compiler/scripts/parity_know_index.py) |
| Require/prefer constraints | [`compiler/src/constraints.flow`](../../compiler/src/constraints.flow) — `flowc_parse_require` / `flowc_parse_prefer` / tighter-value picker |
| Convention avoid-pattern matcher | [`compiler/src/conventions.flow`](../../compiler/src/conventions.flow) — `flowc_contains_ci` / `flowc_check_source` (TOML loading stays Python) |
| MISRA/CERT C scanner | [`compiler/src/misra_scan.flow`](../../compiler/src/misra_scan.flow) — `flowc_scan_c_source` flags heap/stdio/abort calls |
| Function attribute vocabulary | [`compiler/src/attributes.flow`](../../compiler/src/attributes.flow) — `flowc_parse_attribute` / `flowc_validate_target_spec` / `flowc_domain_rank` |
| Matmul/reduce cost models | [`compiler/src/general_plans.flow`](../../compiler/src/general_plans.flow) — `flowc_select_matmul` / `flowc_select_reduce` (pure cost/applicability, registry stays Python) |
| FIR-G effect propagation | [`compiler/src/fir_analysis.flow`](../../compiler/src/fir_analysis.flow) — `flowc_propagate_effects` / `flowc_reachable_functions` / `flowc_is_pure` (CSR graph, fixpoint OR) |
| FIR-G opt candidate scoring | [`compiler/src/fir_opts.flow`](../../compiler/src/fir_opts.flow) — `flowc_score_inline` / `flowc_score_dead_elim` / `flowc_compare_candidates` |
| FIR-G routing decision | [`compiler/src/fir_route.flow`](../../compiler/src/fir_route.flow) — `flowc_choose_analysis_backend` (calibration and timing stay Python) |
| LSP syntax token detection | [`compiler/src/lsp_syntax.flow`](../../compiler/src/lsp_syntax.flow) — `flowc_syntax_token_at_position` / `flowc_is_multi_char_op` (markdown hover stays Python) |
| LSP receiver/field detection | [`compiler/src/lsp_intel.flow`](../../compiler/src/lsp_intel.flow) — `flowc_receiver_before_dot` / `flowc_field_access_at` (URI parsing and typecheck stay Python) |
| Geometry diagram helpers | [`compiler/src/geometry_diagram.flow`](../../compiler/src/geometry_diagram.flow) — `flowc_svg_escape` / `flowc_vec2_unit` / `flowc_lerp` (full SVG rendering stays Python) |
| Proof document formatting + **parsing** | [`compiler/src/proof_document.flow`](../../compiler/src/proof_document.flow) — `flowc_circled` / `flowc_step_label_latex` / `flowc_fmt_refs` / `flowc_from_refs` / `flowc_under_refs` / `flowc_slug_label`, plus the text half of `parse_proof_file`: `flowc_proof_meta_key` / `flowc_proof_meta_value` / `flowc_extract_brace_body` / `flowc_extract_brace_end` / `flowc_proof_step_kind` / `flowc_proof_step_text` / `flowc_proof_step_detail` / `flowc_proof_claim_from_therefore` / `flowc_latex_escape` / `flowc_latex_escape_params`, and the per-item renderers `flowc_claim_path_phrase` / `flowc_natural_claim_sentence` / `flowc_facet_title` / `flowc_natural_let` / `flowc_theorem_ref_plain` / `flowc_theorem_ref_latex` / `flowc_render_math_cell_latex` / `flowc_trace_legend_row` / `flowc_diagram_markdown_embed` / `flowc_latex_preamble`. File reading, document assembly, the theorem catalogue, and PDF stay Python. Gated by [`parity_proof_parse.py`](../../compiler/scripts/parity_proof_parse.py) |
| Dynamics DSL line helpers | [`compiler/src/dynamics_dsl.flow`](../../compiler/src/dynamics_dsl.flow) — `flowc_strip_comments` / `flowc_strip_dynamics_namespace` (full DSL parsing and expansion stay Python) |
| LSP utility helpers | [`compiler/src/lsp_utils.flow`](../../compiler/src/lsp_utils.flow) — `flowc_is_valid_identifier` / `flowc_word_range` / `flowc_completion_prefix` (full LSP protocol stays Python) |
| DSL detection | [`compiler/src/dsl_detect.flow`](../../compiler/src/dsl_detect.flow) — `flowc_has_field_dsl` / `flowc_has_dynamics_dsl` / `flowc_has_fill_shader_dsl` (full DSL parsing and expansion stay Python) |
| Claim lookup helpers | [`compiler/src/know.flow`](../../compiler/src/know.flow) — `flowc_normalize_query` / `flowc_package_prefix` / `flowc_qualify` (filesystem scanning and claim indexing stay Python) |
| LSP ordering hover | [`compiler/src/lsp_ordering.flow`](../../compiler/src/lsp_ordering.flow) — `flowc_ordering_hover` (completion items with snippets stay Python) |
| LSP dynamics hover | [`compiler/src/lsp_dynamics.flow`](../../compiler/src/lsp_dynamics.flow) — `flowc_dynamics_hover` (completion items stay Python) |
| WCET analysis helpers | [`compiler/src/wcet.flow`](../../compiler/src/wcet.flow) — `flowc_type_size` / `flowc_stmt_cost` / `FLOWC_DEFAULT_LOOP_BOUND` (AST traversal and report formatting stay Python) |
| Proof kernel helpers | [`compiler/src/proof_kernel.flow`](../../compiler/src/proof_kernel.flow) — `flowc_node_kind` / `flowc_escape_dot` (kernel construction, JSON, and plotting stay Python) |
| Stage-A JS / fmt | [`jsgen.flow`](../../compiler/src/jsgen.flow) / [`fmt.flow`](../../compiler/src/fmt.flow) |
| LSP ordering gloss | [`examples/compilers/lsp_ordering_port.flow`](../../examples/compilers/lsp_ordering_port.flow) |
| Lexer / parser / cgen / typecheck / resolve | [`compiler/src/`](../../compiler/src/) — floats, `pkg_add`, `for ..` / `to`, bundles |

Where a Flow port replaces a Python script that still exists, the Python
stays as the reference and the shim diffs the two on every run. The repo
stats counter works this way: `update_repo_stats.sh` runs Flow, then fails
loudly if `update_repo_stats.py` disagrees with what Flow wrote.

| Still rewrite priority | Target |
|---|---|
| Grow parser/cgen | more of production C path |
| `flow doc proof` rendering | remaining `proof_document.py` — the parse helpers have landed; document assembly, Markdown/LaTeX rendering, and PDF are next |
| Recursive claim index over disk | the key aliases, lookup predicate, and rendering have landed; what remains is the directory walk itself (`fileio` + `popen("find")`, as `update_repo_stats.sh` does for git) |

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

1. **Satellites** — pure string/AST walkers ← largely landed
2. **Stage-A basics C path** — ten Stage-A-clean `examples/basics/*` via `emit_basics.sh`
3. **Language surface** — effects/generics/match after Stage-A can express them
4. **Optional** — full proof PDF / shader emitters (host-run)

## Dogfood

```bash
./compiler/scripts/stage_a_smoke.sh
FLOW_HOST=python ./flow run compiler/src/main.flow
./compiler/scripts/roundtrip.sh
FLOWC_EMIT_ONLY=1 ./compiler/scripts/emit_basics.sh
./compiler/scripts/smoke_math_prose.sh
python3 compiler/scripts/parity_math_prose_expr.py
python3 compiler/scripts/parity_proof_parse.py
python3 compiler/scripts/parity_know_index.py
./compiler/scripts/smoke_know.sh
FLOW_HOST=python ./flow run examples/compilers/claim_address_demo.flow
FLOW_HOST=python ./flow run examples/compilers/math_prose_demo.flow
FLOW_HOST=python ./flow run examples/compilers/math_prose_expr_demo.flow
FLOW_HOST=python ./flow run examples/compilers/proof_parse_demo.flow
FLOW_HOST=python ./flow run examples/compilers/know_index_demo.flow
FLOW_HOST=python ./flow run examples/compilers/know_demo.flow
```

Python remains the Gen0 bootstrap and the full-language host until Stage-A covers
those surfaces; default Stage-A user compile is already flowc.
