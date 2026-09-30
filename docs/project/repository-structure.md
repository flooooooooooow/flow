# Repository Structure Contract

This page defines where new Flow repository content belongs. It is intentionally
stable. Current feature status belongs in `ROADMAP.md`, issues, pull requests
and CI.

## Canonical ownership

| Path | Responsibility |
|---|---|
| `compiler/` | flowc, the self-hosted compiler and the only compiler: sources in `compiler/src/`, the bootstrap C, and self-host verification |
| `lib/` | Flow libraries and standard library |
| `runtime/` | Native runtime implementation used by generated programs |
| `tests/` | Regression, integration, conformance, fuzz and language tests |
| `examples/` | User-facing and verification examples |
| `benchmarks/` | Reproducible performance workloads and comparison harnesses |
| `apps/` | Substantial applications built with Flow |
| `tools/` | Developer tools with their own implementation, such as the LSP, DAP, REPL and the Python ratchet |
| `scripts/tools/` | Flow programs behind repository checks and automation, one per `scripts/tools/<name>/main.flow`, built by `scripts/tools/build_tool.sh` |
| `scripts/` | Thin shell entry points, release and CI glue |
| `docs/` | User, language, research and project documentation |
| `docs/generated/` | Reproducibly generated documentation data |
| `build/` | Disposable local build output, never a source of truth |
| `.github/` | GitHub CI, templates, ownership and repository automation |
| `third_party/` | Vendored or externally maintained integrations |
| `packaging/` | Distribution and package-manager metadata |

## Structural invariants

New code is Flow. `scripts/python_ratchet.sh` fails on any new `.py` file
outside the exempt trees it names.

A source implementation has one canonical home. A tool lives under `tools/`
or under `scripts/tools/`, never both. `scripts/check_tool_layout.sh` fails
when the same tool name appears in both trees.

A shell script may call a tool but should not contain a second copy of it.
When Flow needs an external command such as git, the shell entry point runs
the command and leaves its output in `build/` for the Flow program to read.

Generated reports should live under `docs/generated/`, a build artifact, or a
workflow artifact unless they are intentionally reviewed historical records.
Do not keep multiple generated backlog reports beside executable source.

Root files are reserved for repository entry points and durable project
contracts. Release-specific snapshots and superseded roadmaps move under an
archive location in `docs/project/` rather than accumulating at the root.

A document that contains changing project state must either be generated or
point to the live source. Hand-maintained copies of test counts, current
failures, active agents, compiler coverage and open issue totals are
prohibited.

The public command contract is `./flow`. Makefiles, shell scripts, docs, CI
and examples delegate to it. A second compilation pipeline is allowed only in
a file that exists to test a backend.

## Migration rule

Structural cleanup should preserve history and avoid colliding with active
feature branches. When duplicate trees exist, choose the canonical owner,
redirect callers, prove parity, then delete the duplicate in one focused pull
request.

Do not perform broad moves while an open pull request is actively changing the
same tree. Record the cleanup as a dependency and land it after the overlapping
work.
