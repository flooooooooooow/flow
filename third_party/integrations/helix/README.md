# Flow Support for Helix Editor

This directory contains configuration files and tree-sitter queries for the [Helix editor](https://helix-editor.com/).

## Features

- Syntax highlighting for Flow keywords, primitive types, operators, and comments.
- Integration with `flow-lsp` Language Server Protocol.
- Indentation and tab configuration.

## Installation

### 1. Language Configuration (`languages.toml`)

Append or merge the contents of `languages.toml` into your personal Helix configuration directory (`~/.config/helix/languages.toml` on Linux/macOS or `%RUST_LOG%` / `%AppData%\helix\languages.toml` on Windows):

```toml
[[language]]
name = "flow"
scope = "source.flow"
file-types = ["flow"]
roots = ["flow.toml"]
comment-token = "#"
indent = { tab-width = 4, unit = "    " }
language-servers = ["flow-lsp"]

[language-server.flow-lsp]
command = "flow-lsp"
```

### 2. Highlight Queries (`highlights.scm`)

Copy the `queries` directory to your Helix runtime configuration path:

```bash
mkdir -p ~/.config/helix/runtime/queries/flow
cp third_party/integrations/helix/queries/highlights.scm ~/.config/helix/runtime/queries/flow/
```

### 3. Verification

Open any `.flow` file in Helix (`hx file.flow`) and run:
- `:lsp-workspace-command` or `:health flow` to verify language server status and syntax highlighting.
