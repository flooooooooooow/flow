# Flow changelog

The complete version-by-version history of Flow is maintained in [`docs/project/CHANGELOG.md`](docs/project/CHANGELOG.md).

That history covers the project from the initial `0.1.0` implementation through the pre-1.0 language releases and the current `1.x` compatibility line. It is the canonical human-readable release history; Git tags remain the source of truth for the exact repository state of a release.

## Current release

**Flow 1.0.0** is the first release governed by the explicit 1.x compatibility contract in [`STABILITY.md`](STABILITY.md). The Stable core is intentionally narrower than the full set of shipped Experimental features.

[Read the complete changelog →](docs/project/CHANGELOG.md)

## Release history

| Version | Recorded date | Headline |
|---|---|---|
| 1.0.0 | 2026-08-22 | First explicit Stable 1.x compatibility contract; self-hosted `flowc` + portable C Stable core; exact-tag qualification |
| 0.12.0 | 2026-08-19 | Range algebra and correctness fixes found by executable-documentation verification |
| 0.11.1 | 2026-08-14 | Linux `@cImport` correctness patch |
| 0.11.0 | 2026-08-13 | Zero-bridge C interop, BLAS/LAPACK, RF/units and major `flowc` expansion |
| 0.10.0 | 2026-08-08 | MLIR/WASM expansion, three-generation self-hosting and broader runtime/stdlib work |
| 0.9.0 | 2026-08-05 | Concurrency/runtime consolidation, registry and deeper self-hosting |
| 0.8.0 | 2026-08-05 | Official public-language release and repository/release infrastructure |
| 0.7.0 | 2026-02-09 | Security and quality audit/hardening release |
| 0.6.0 | 2026-01-08 | Import/export system and multi-backend GPU integration |
| 0.5.0 | 2026-01-08 | Documentation/project overhaul, type-system and graphics foundations |
| 0.4.0 | 2025-01-05* | MLIR optimisation pipeline |
| 0.3.0 | 2025-01-05* | DWARF, loop-carried SSA and LSP/VS Code support |
| 0.2.0 | 2025-01-05* | Strings/I/O, arrays, pointers, loops and parallel constructs |
| 0.1.0 | 2026-01-05 | Initial Flow language implementation |

`*` The early changelog contains legacy chronology metadata that predates the formal public release process. Those recorded dates are preserved rather than silently rewritten. The detailed changelog also contains an older duplicate `0.2.0` historical section from the project's pre-release documentation era; it is retained as provenance rather than presented here as a second release.

## Changelog policy

Every future release must have a version section in the canonical changelog before publication. Release notes should summarize that section rather than becoming an independent history that can drift from the repository. Breaking changes, deprecations and Stable-surface promotions must be called out explicitly.
