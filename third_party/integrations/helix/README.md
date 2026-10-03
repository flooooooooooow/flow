# Helix support

Merge the contents of `languages.toml` into `~/.config/helix/languages.toml`.

This enables Flow filetype recognition and the existing `flow lsp` language server.

Tree-sitter highlighting is intentionally not declared here yet. Helix grammar sources are best pointed at a dedicated, versioned `tree-sitter-flow` repository; the grammar source currently lives at `third_party/integrations/tree-sitter-flow` in the main Flow repository and should be split out after validation.
