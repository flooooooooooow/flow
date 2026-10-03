# tree-sitter-flow

Tree-sitter grammar source for the Flow programming language.

This integration is kept in the main Flow repository until it is useful to split it into a dedicated `tree-sitter-flow` repository. The grammar targets the stable language core and the commonly used experimental evolution surface.

## Validate

```bash
cd third_party/integrations/tree-sitter-flow
npm install
npm test
```

`npm test` runs `tree-sitter generate` and the corpus suite in
`test/corpus/`. For a broader check, parse the repository's own Flow
sources and look for `ERROR` nodes:

```bash
find /path/to/flow -name '*.flow' > /tmp/flow-files.txt
npx tree-sitter parse --paths /tmp/flow-files.txt -q
```

As of this revision the grammar parses the full in-tree corpus cleanly.
The only remaining `ERROR` results are intentional parse-failure fixtures
(`tests/*/fixtures/*bad*`, `parse_error.flow`, `syntaxerr.flow`) and
`tests/lang/test_prefix_deref.flow`, whose `*p = 7` statement after an
expression line relies on Flow's indentation-aware disambiguation between
a binary `*` continuation and a dereference statement.

## Use

The grammar identifies `*.flow` files with scope `source.flow`. Highlight queries live in `queries/highlights.scm`.

The language specification remains authoritative. If this grammar and the compiler disagree, fix the grammar rather than changing compiler behavior to satisfy editor tooling.

## Upstream path

Once this grammar has generated cleanly against representative Flow sources, publish it as a dedicated repository and use that repository for Helix, Zed, Neovim and other Tree-sitter consumers. The dedicated repository should check in generated parser sources and tag releases.
