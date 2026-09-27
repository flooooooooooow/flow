# Repository Structure Contract

This page defines where new Flow repository content belongs. It is intentionally
stable; current feature status belongs in `ROADMAP.md`, issues, pull requests,
and CI.

## Canonical ownership

| Path | Responsibility |
|---|---|
| `src/flow/` | Full/reference Python-host compiler and tooling that still requires it |
| `compiler/` | Self-hosted Flow compiler, bootstrap artifacts, and self-host verification |
| `lib/` | Flow libraries and standard library |
| `runtime/` | Native runtime implementation used by generated programs |
| `tests/` | Regression, integration, conformance, fuzz, and language tests |
| `examples/` | User-facing and verification examples |
| `benchmarks/` | Reproducible performance workloads and comparison harnesses |
| `apps/` | Substantial applications built with Flow |
| `tools/` | Canonical long-lived developer tools with their own implementation |
| `scripts/` | Thin repository automation, entry shims, release/CI glue, and orchestration |
| `docs/` | User, language, research, and project documentation |
| `docs/generated/` | Reproducibly generated documentation data |
| `build/` | Disposable local build output; never a source-of-truth |
| `.github/` | GitHub CI, templates, ownership, and repository automation |
| `third_party/` | Vendored or externally maintained integrations |
| `packaging/` | Distribution/package-manager metadata |

## Structural invariants

A source implementation has one canonical home. Do not mirror the same Python,
Flow, C, or generated source tree under both `tools/` and `scripts/`.

A script may call a tool, but it should not contain a second copy of that tool.
If a tool needs a shell entry point, keep the implementation in `tools/` and a
thin shim in `scripts/`.

Generated reports should live under `docs/generated/`, a build artifact, or a
workflow artifact unless they are intentionally reviewed historical records.
Do not keep multiple generated backlog reports beside executable source.

Root files are reserved for repository entry points and durable project
contracts. Release-specific snapshots and superseded roadmaps should move under
an archive/project-documentation location rather than accumulating at the
root.

A document that contains changing project state must either be generated or
point to the live source. Hand-maintained copies of test counts, current
failures, active agents, compiler coverage, and open issue totals are
prohibited.

The public command contract is `./flow`. Makefiles, shell scripts, docs, CI,
and examples should delegate to that contract rather than maintaining a second
compilation pipeline unless the file is explicitly testing a backend.

## Migration rule

Structural cleanup should preserve history and avoid colliding with active
feature branches. When duplicate trees exist, choose the canonical owner,
redirect callers, prove parity, then delete the duplicate in one focused pull
request.

Do not perform broad moves while an open pull request is actively changing the
same tree. Record the cleanup as a dependency and land it after the overlapping
work.
