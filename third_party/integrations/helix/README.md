# Helix support

Merge the contents of `languages.toml` into
`~/.config/helix/languages.toml`, then fetch and build the grammar:

```bash
hx --grammar fetch
hx --grammar build
```

This enables Flow file recognition, Tree-sitter highlighting, and the
`flow lsp` language server. The grammar is pinned to commit
`2e0cfb80a52a72d08a00b9ac9afc5889c31fe71c` from the standalone
`tree-sitter-flow` repository.
