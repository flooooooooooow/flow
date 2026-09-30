# Vim and Neovim support

This directory provides filetype detection and fallback syntax highlighting for Flow. Neovim users can additionally start the existing Flow language server.

## Vim

Add this directory to `runtimepath`, or copy `ftdetect/flow.vim` and `syntax/flow.vim` into the matching directories under `~/.vim`.

## Neovim

Add this directory to `runtimepath`. For LSP support, place `lua/flow.lua` on `runtimepath` and call:

```lua
require("flow").setup()
```

By default it starts:

```text
flow lsp
```

Pass `{ cmd = { "/absolute/path/to/flow", "lsp" } }` if Flow is not on `PATH`.

The LSP is authoritative for diagnostics and language intelligence. Vim syntax is only a fallback highlighter.
