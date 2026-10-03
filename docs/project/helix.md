# Helix Editor Integration Handoff

This document details the Helix editor integration for Flow and the upstream PR submission procedure to `helix-editor/helix`.

## Status

In-repo editor support for Helix is maintained under `third_party/integrations/helix/`:

* `third_party/integrations/helix/languages.toml` — Helix language definition and LSP configuration (`flow lsp`).
* `third_party/integrations/helix/queries/highlights.scm` — Tree-sitter highlight queries.
* `third_party/integrations/helix/README.md` — Setup and testing instructions for local Helix installations.

## Upstream PR Procedure (`helix-editor/helix`)

Upstream acceptance in Helix requires adding `languages.toml` and query files to Helix's official repository:

1. **Prerequisite**: Standalone `tree-sitter-flow` grammar repository published with a tagged/pinned git revision (tracked in issue #899).
2. **Pin Grammar Revision**: Update `[[grammar]]` in `languages.toml` with the exact pinned commit hash:
   ```toml
   [[grammar]]
   name = "flow"
   source = { git = "https://github.com/flooooooooooow/tree-sitter-flow", rev = "<pinned_commit_sha>" }
   ```
3. **Helix PR Checklist**:
   - Add language entry to `languages.toml` in `helix-editor/helix`.
   - Add highlight queries to `runtime/queries/flow/highlights.scm`.
   - Run `cargo test` and `hx --health flow` in the Helix tree.
   - Submit PR to `helix-editor/helix` referencing Flow language specification.
