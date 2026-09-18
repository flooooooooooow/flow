# Vim / Neovim support

Minimal first-party Flow filetype support.

## Vim

Copy or symlink `ftdetect/flow.vim`, `syntax/flow.vim`, and `ftplugin/flow.vim` into the matching directories under `~/.vim`.

## Neovim

The same files work under `~/.config/nvim`. For semantic features, run Flow's LSP with `./flow lsp`; the repository's LSP remains the source of completion/diagnostics rather than this syntax package.

The syntax file intentionally tracks the Flow 1.x lexical surface and does not try to replace the parser.
