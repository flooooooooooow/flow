# tree-sitter-flow

Tree-sitter grammar source for the Flow programming language.

This integration is kept in the main Flow repository until it is useful to split it into a dedicated `tree-sitter-flow` repository. The grammar targets the stable language core and the commonly used experimental evolution surface.

## Validate

```bash
cd third_party/integrations/tree-sitter-flow
npm install
npm test
```

## Use

The grammar identifies `*.flow` files with scope `source.flow`. Highlight queries live in `queries/highlights.scm`.

The language specification remains authoritative. If this grammar and the compiler disagree, fix the grammar rather than changing compiler behavior to satisfy editor tooling.

## Upstream path

Once this grammar has generated cleanly against representative Flow sources, publish it as a dedicated repository and use that repository for Helix, Zed, Neovim and other Tree-sitter consumers. The dedicated repository should check in generated parser sources and tag releases.
