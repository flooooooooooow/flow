# tree-sitter-flow

Tree-sitter grammar source for Flow.

This integration is intentionally kept inside the main Flow repository until its grammar has enough external consumers to justify a standalone upstream repository.

## Generate

```bash
cd third_party/integrations/tree-sitter-flow
npm install
npm run generate
npm test
```

The grammar targets Flow 1.x core syntax plus enough evolution syntax for editor navigation and highlighting. The authoritative language contract remains `docs/LANGUAGE_SPEC.md` and `docs/grammar.ebnf`.

## Consumers

The intended consumers are Neovim, Helix, Zed, code search/indexing tools, and future GitHub ecosystem integrations.
