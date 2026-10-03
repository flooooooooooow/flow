# Zed support

This directory is a Zed language extension for Flow.

It registers:

- `.flow` files as Flow
- `#` line comments
- `tree-sitter-flow` at commit `2e0cfb80a52a72d08a00b9ac9afc5889c31fe71c`
- highlight queries from the grammar
- `flow lsp`, found on the worktree's shell `PATH`

## Install for development

In Zed, open Extensions, choose "Install Dev Extension", then select this
directory. The `flow` command must be available on `PATH`.

The grammar source is https://github.com/flooooooooooow/tree-sitter-flow.
Release `v0.1.0` corresponds to the pinned commit above.

## Publishing Status

Upstream publish of the Zed extension is currently blocked on #899 because Zed language extensions require a Tree-sitter grammar repository pinned to a Git revision.
