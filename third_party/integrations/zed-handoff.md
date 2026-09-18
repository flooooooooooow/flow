# Zed integration handoff

Zed support depends on a published Tree-sitter grammar repository. Once `tree-sitter-flow` is standalone, create a small Zed extension that registers:

- language name: Flow
- extension: `.flow`
- grammar: `tree-sitter-flow`
- language server command: `flow lsp`
- line comment: `#`

Use the current Zed extension schema at submission time and pin the grammar to an immutable commit.

The canonical syntax sources are:

- `docs/LANGUAGE_SPEC.md`
- `third_party/integrations/tree-sitter-flow/grammar.js`
- `third_party/integrations/tree-sitter-flow/queries/highlights.scm`
- `third_party/integrations/vscode/flow-language/syntaxes/flow.tmLanguage.json`

Do not create a second, drifting keyword list inside the Zed integration unless Zed's format requires it.
