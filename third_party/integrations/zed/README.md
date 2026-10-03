# Flow Language Extension for Zed

This directory contains the official [Zed](https://zed.dev/) extension for the Flow programming language (`.flow` files).

## Features

- **Syntax Highlighting**: Tree-sitter query rules for core keywords, types, control flow, dynamics DSLs, ordering operators, comments, and literals.
- **Language Server Protocol (LSP)**: Integrated with `flow-lsp` for diagnostics, autocompletion, hovers, and jump-to-definition.
- **Bracket Matching**: Rainbow brackets and auto-closing bracket definitions.
- **Indentation Rules**: Automatic indentation on braces, brackets, and parentheses.
- **Symbol Outline**: Document symbol indexing for functions, structs, enums, traits, and effects.
- **Semantic Token Rules**: Default mapping of LSP semantic tokens to editor syntax themes.

## Installation

### Method 1: Local Dev Extension (Recommended for Development)

1. Open Zed.
2. Open the Command Palette (`cmd-shift-p` on macOS or `ctrl-shift-p` on Linux/Windows) and run:
   ```
   zed: install dev extension
   ```
3. Select the `third_party/integrations/zed` directory from your Flow repository checkout.

### Method 2: Manual Link to Extensions Directory

You can also install the extension locally by linking or copying this folder into your Zed extension directory:

**macOS:**
```bash
mkdir -p ~/.config/zed/extensions/installed
ln -s "$(pwd)/third_party/integrations/zed" ~/.config/zed/extensions/installed/flow
```

**Linux:**
```bash
mkdir -p ~/.local/share/zed/extensions/installed
ln -s "$(pwd)/third_party/integrations/zed" ~/.local/share/zed/extensions/installed/flow
```

## Language Server Setup

The Zed extension automatically configures the `flow-lsp` language server for `.flow` files.

Ensure `flow-lsp` (or `flow`) is available in your PATH:

```bash
# Ensure flow is built or linked in PATH
export PATH="$PATH:/path/to/flow"
```

Or configure custom language server settings in your Zed `settings.json`:

```json
{
  "lsp": {
    "flow-lsp": {
      "binary": {
        "path": "python3",
        "arguments": ["-m", "flow.lsp_server"]
      }
    }
  }
}
```

## Repository Structure

```
third_party/integrations/zed/
├── extension.toml                     # Zed extension manifest
├── README.md                          # Installation and usage instructions
└── languages/
    └── flow/
        ├── config.toml                # Language configuration (suffixes, comment chars)
        ├── highlights.scm             # Tree-sitter syntax highlighting query
        ├── brackets.scm               # Tree-sitter bracket matching query
        ├── indents.scm                # Tree-sitter indentation query
        ├── outline.scm                # Tree-sitter outline query
        └── semantic_token_rules.json  # Semantic token mapping rules for LSP
```
