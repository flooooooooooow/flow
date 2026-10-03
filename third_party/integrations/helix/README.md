# Helix Editor Integration for Flow

This directory contains Helix editor configuration and queries for the [Flow programming language](https://flow-lang.org).

## Features

- **Language Server Protocol (LSP)**: Automatic diagnostic hints, completion, and typed hover via `flow lsp`.
- **Tree-sitter Syntax Highlighting**: Highlighting for keywords, types, functions, attributes (`@gpu`, `@rt_safe`), strings, and comments.

## Local Setup

To configure Flow in Helix locally:

1. Add the content of `languages.toml` to your Helix configuration at `~/.config/helix/languages.toml`:

   ```toml
   [[language]]
   name = "flow"
   scope = "source.flow"
   injection-regex = "flow"
   file-types = ["flow"]
   roots = ["flow.toml", ".git"]
   comment-token = "#"
   indent = { tab-width = 4, unit = "    " }
   language-servers = ["flow-lsp"]
   grammar = "flow"

   [language-server.flow-lsp]
   command = "flow"
   args = ["lsp"]

   [[grammar]]
   name = "flow"
   source = { git = "https://github.com/flooooooooooow/tree-sitter-flow", rev = "3dbbac87134e00d750e8c736c313d22a4b2c2343" }
   ```

2. Copy the syntax queries to your Helix queries directory:

   ```bash
   mkdir -p ~/.config/helix/queries/flow
   cp third_party/integrations/helix/queries/highlights.scm ~/.config/helix/queries/flow/
   ```

3. Fetch and build the tree-sitter grammar:

   ```bash
   hx --grammar fetch
   hx --grammar build
   ```

4. Verify setup health:

   ```bash
   hx --health flow
   ```

## Upstream Integration

Upstream PR handoff instructions and tracking for `helix-editor/helix` are documented in [`docs/project/helix.md`](../../../docs/project/helix.md).
