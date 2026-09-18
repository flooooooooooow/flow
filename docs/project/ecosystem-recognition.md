# Ecosystem recognition

This page tracks whether Flow is merely supported by its own repository or recognized by external developer ecosystems.

The rule is deliberately strict: a local integration is not marked upstream until the external project has accepted it.

## Current state

| Surface | Repository support | External state | Exit criterion |
|---|---|---|---|
| GitHub Linguist | TextMate grammar, samples, PR template, issue #172 | Blocked on independent public usage evidence | Upstream Linguist release identifies `.flow` as Flow |
| Tree-sitter | Grammar + highlight queries in `third_party/integrations/tree-sitter-flow` | Local integration | Dedicated grammar repository, generated parser, tagged release, external consumers |
| Pygments | Installable lexer plugin in `third_party/integrations/pygments-flow` | Local integration | Lexer merged into Pygments and released |
| VS Code / Cursor | Extension and TextMate grammar | Published project integration | Keep extension compatible with current syntax |
| Vim | Filetype + syntax files in `third_party/integrations/vim-flow` | Local integration | Upstream runtime files or a standalone community plugin with users |
| Neovim | Vim syntax + `flow lsp` bootstrap | Local integration | Community plugin / upstream ecosystem listing using Flow LSP |
| Helix | `languages.toml` LSP configuration | Local integration | Tree-sitter grammar published and Flow accepted into Helix languages |
| Zed | Integration handoff in `third_party/integrations/zed` + existing `flow lsp` | Local handoff | Dedicated Tree-sitter repository, then a published Zed language extension |
| Rosetta Code | Submission pack in `docs/community/rosetta-code.md` | Ready to publish | Flow category exists with multiple tasks |
| Independent tutorials | Author kit and reproducibility contract | Waiting on outside authors | At least three technically substantive tutorials by non-core authors |
| Homebrew | Tap + formula | Available | Maintain release compatibility |
| Open VSX | VS Code-family extension path documented | Available/project-controlled | External installs and continued publication |
| Benchmarks | Internal + standardized benchmark layouts | Partial external visibility | Accepted entries in independent benchmark suites |

## Tree-sitter

The grammar source is at:

```text
third_party/integrations/tree-sitter-flow/
```

Validation:

```bash
cd third_party/integrations/tree-sitter-flow
npm install
npm test
```

Before calling Tree-sitter support externally available, generate the parser, run it over representative files from `examples/`, split the grammar into a dedicated repository, tag a release, and point editors at immutable revisions.

## Pygments

The local plugin is installable directly:

```bash
cd third_party/integrations/pygments-flow
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
python test_lexer.py
```

The upstream contribution should preserve the `*.flow` filename mapping, `flow` / `flowlang` aliases, and regression examples covering ordinary code plus Flow's evolution syntax.

## Editor integrations

Flow should not implement a different semantic engine for every editor. The preferred architecture is:

```text
editor filetype / Tree-sitter
          +
       flow lsp
          |
      Flow compiler
```

VS Code already follows this direction. Vim/Neovim and Helix integration assets are checked in under `third_party/integrations/`; Zed has a handoff package ready for the standalone Tree-sitter revision.

Zed should wait until `tree-sitter-flow` has a stable repository and revision, because Zed language extensions normally need a versioned grammar source rather than an unversioned subdirectory of the compiler repository.

## GitHub Linguist

The upstream pack lives under `docs/project/linguist/`. Do not submit it merely to make the Flow repository's language bar look better. Linguist's popularity requirements exist to distinguish languages with independent usage from project-local file extensions.

The practical dependency chain is:

```text
independent repositories using Flow
        -> Linguist popularity evidence
        -> upstream PR
        -> Linguist release
        -> GitHub recognizes .flow natively
```

Issue #172 remains the source of truth.

## Rosetta Code

The copy-ready submission material is at `docs/community/rosetta-code.md`. It includes enough conventional tasks to establish Flow before adding more distinctive numerical and dynamical examples.

## Independent tutorials

The project must not relabel its own writing as independent coverage. `docs/community/tutorial-author-kit.md` is a reproducibility kit for outside authors. Third-party tutorials should be listed whether they are positive, mixed, or critical, provided they are technically substantive.

## Next external actions

The highest-leverage external actions are to publish the Rosetta Code category, split and release `tree-sitter-flow`, upstream the Pygments lexer, then use the Tree-sitter release for Helix and Zed submissions. Linguist follows when independent usage evidence clears its threshold.
