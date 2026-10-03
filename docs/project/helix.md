# Helix Editor Integration for Flow

Flow provides first-class support for the [Helix editor](https://helix-editor.com/).

## Overview

Helix support includes:
- Syntax highlighting for Flow language constructs, types, and keywords.
- `flow-lsp` integration for hover information, diagnostics, and code intelligence.
- Auto-indentation and tab settings.

## Configuration

To enable Flow support in Helix:

1. Copy or append the language configuration from `third_party/integrations/helix/languages.toml` to your Helix configuration file (`~/.config/helix/languages.toml`):

```toml
[[language]]
name = "flow"
scope = "source.flow"
injection-regex = "flow"
file-types = ["flow"]
roots = ["flow.toml"]
comment-token = "#"
indent = { tab-width = 4, unit = "    " }
language-servers = ["flow-lsp"]

[language-server.flow-lsp]
command = "flow-lsp"
```

2. Copy the tree-sitter highlight queries into your Helix runtime folder:

```bash
mkdir -p ~/.config/helix/runtime/queries/flow
cp third_party/integrations/helix/queries/highlights.scm ~/.config/helix/runtime/queries/flow/
```

3. Ensure `flow-lsp` is available on your system `PATH`.
