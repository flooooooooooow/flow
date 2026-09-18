# Editor and syntax integrations

Flow keeps first-party integration sources here so external ecosystem submissions have a canonical implementation to copy from.

| Integration | Source | Status |
| --- | --- | --- |
| VS Code / Cursor | `vscode/flow-language` | Shipping |
| Vim / Neovim syntax | `vim-flow` | First-party source |
| Tree-sitter | `tree-sitter-flow` | First-party grammar source; upstream/consumer packaging pending |
| Pygments | `pygments-flow` | First-party lexer source; upstream submission pending |

The language specification in `docs/LANGUAGE_SPEC.md` is authoritative. Integrations should not introduce syntax that the compiler/spec does not support.

When an integration is accepted upstream, keep the in-repo source as the reference copy and document the upstream project/version here.
