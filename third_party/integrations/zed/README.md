# Zed support

Flow's language server can be consumed by Zed, but a distributable Zed language extension should wait until the Tree-sitter grammar is published as a standalone repository with an immutable revision.

When that repository exists, the Zed extension should register:

- language name: Flow
- file extension: `.flow`
- line comment: `#`
- grammar: the standalone `tree-sitter-flow` repository pinned to a commit
- language server command: `flow lsp`

Canonical sources:

- `docs/LANGUAGE_SPEC.md`
- `third_party/integrations/tree-sitter-flow/grammar.js`
- `third_party/integrations/tree-sitter-flow/queries/highlights.scm`
- `third_party/integrations/vscode/flow-language/syntaxes/flow.tmLanguage.json`

Do not publish a Zed extension with an unpinned grammar or a second hand-maintained syntax definition. The Tree-sitter grammar should remain the syntax source and `flow lsp` should remain the semantic source.
