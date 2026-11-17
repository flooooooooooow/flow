# Wiki Strategy

> **Status:** Active · **Owner:** Flow project · **Live URL:** [flooooooooooow.github.io/flow](https://flooooooooooow.github.io/flow/)  
> VPS `/flow/` + `/transpile/` deploy is **disabled** (GitHub Pages only).

This document defines how Flow documentation should be built, organized, and maintained long term.

---

## Vision

Flow deserves documentation on par with Rust and Zig: a single canonical site where a newcomer can install, learn, reference, and explore proofs without hunting through a GitHub repo.

The wiki is **not** a dump of markdown files. It is a product with:

1. **Clear information architecture**: every page has one job
2. **Consistent rendering**: grammar, proofs, and tutorials look intentional
3. **Automated freshness**: proof catalogs and nav generated from source
4. **Deployable artifacts**: push to `main` → GitHub Pages

---

## Principles

| Principle | What it means |
|-----------|---------------|
| **Source lives in `docs/`** | Markdown in-repo; wiki shell in `site/`; output in `build/wiki/` |
| **Generated ≠ hand-written** | Edit the source map in `docs/nav.json`; the published `wiki-nav.json`, proof catalogs and search index are generated |
| **Two speeds** | Tutorials change slowly; grammar/spec track the compiler |
| **Proofs are first-class** | `flow-verify` is a third-party library section, not an appendix |
| **No orphan pages** | Every documentation page is listed in `docs/nav.json`, explicitly unlisted with a reason, or linked from its parent |
| **Deploy is boring** | `.github/workflows/wiki.yml` → GitHub Pages |

---

## Information architecture

```
Home (wiki-home.md) — brand, docs index, showcases, demos, install
├── Start       → install, vision, book/tutorials shortcuts, popular galleries
├── Gallery     → recorded demos + live WASM
├── Book        → guided chapters + appendices
├── Tutorials   → interactive tracks (core · systems · vision · applied)
├── Language    → spec, grammar, types, effects, graphics, wasm, spans
├── Library     → stdlib reference (core, autodiff, audio, memory)
├── Tooling     → CLI, compiler toolchain, targets and interop
├── Project     → changelog, contributing, roadmaps, research
└── Proofs      → optional flow-verify (third-party; not required)
```

### Page types & rendering

| Type | Example | Renderer |
|------|---------|----------|
| **Guide** | `getting-started.md` | Markdown + TOC + pager |
| **Reference** | `language/types.md` | Markdown + code highlight |
| **Grammar** | `language/grammar.md` | Markdown + EBNF blocks |
| **Formal spec** | `grammar.ebnf` | EBNF viewer (sections, rule search) |
| **Proof** | `*.proof.md` | Markdown + KaTeX + proof badge |
| **Catalog** | `flow-verify-catalog.md` | Generated tables |
| **Meta** | `wiki-strategy.md` | Standard markdown |

---

## Build pipeline

The public site uses the custom shell in `site/`. The Flow-native builder
validates the source navigation map and assembles the pages and generated data.

```text
docs/**/*.md ───┐
docs/nav.json ───┤
lib/verify/ ─────┼──> ./flow tool build_wiki ──> build/wiki/
examples/ ──────┤                                  │
site/ ──────────┘                                  ├── wiki-nav.json
                                                   ├── search-index.json
                                                   ├── proof catalogs
                                                   ├── releases.md / versions.json
                                                   └── optional Pagefind index

build/wiki/ ──> .github/workflows/wiki.yml ──> GitHub Pages
```

**Rule:** Never edit files in `build/wiki/` by hand. Always change source and rebuild.

VPS deploy is off. Local build: `./flow tool deploy_wiki` (builds only). Emergency VPS: `FLOW_WIKI_VPS=1`.

---

## Content ownership

| Area | Source of truth | Update trigger |
|------|-----------------|----------------|
| Language semantics | `docs/LANGUAGE_SPEC.md`, `compiler/src/`, regression tests | Syntax/compiler change |
| Grammar | `docs/grammar.ebnf`, `compiler/src/` | Parser change |
| Stdlib | `lib/stdlib/*.flow` + `docs/library/` | New module or API change |
| Proofs | `lib/verify/`, `examples/verify/` | `./flow doc proof` |
| Wiki IA | `docs/nav.json` (source), `scripts/tools/build_wiki/` (builder) | New section or package |
| Changelog / releases | `docs/project/CHANGELOG.md` | New version section → rebuild (auto-syncs `releases.md` + `versions.json`) |
| Language roadmap | `ROADMAP.md` (repo root) | Quarterly planning |
| Wiki roadmap | `docs/wiki-roadmap.md` | This strategy doc |

---

## Comparison to other language docs

| Project | What we borrow |
|---------|----------------|
| **Rust Book** | Learning path + reference split; version badge |
| **Zig** | Grammar page clarity; stdlib as reference |
| **Lean/Mathlib** | Proof catalog organization |
| **MkDocs Material** | Tab nav, search, admonitions (future) |

We deliberately **do not** use MkDocs for the live site today. The custom shell gives us proof browsing, EBNF viewing, and tab filtering without fighting a theme. MkDocs config (`mkdocs.yml`) remains for optional static export.

---

## Long-term targets

1. **Custom domain**: `flow-lang.org` (referenced in verification docs; DNS TBD)
2. **Versioned docs**: published, version-scoped language references with a stable `latest` route
3. **API autogen**: stdlib signatures from `flow doc` or LSP
4. **Pagefind**: optional post-build index (`./flow tool build_wiki --pagefind`); search falls back to `search-index.json`
5. **Playground embed**: runnable snippets from tutorial pages
6. **CI deploy**: GitHub Pages via `.github/workflows/wiki.yml` on eligible changes to `main`

See [Wiki Roadmap](wiki-roadmap.md) for phased delivery.

---

## Quality bar

A page is "done" when it:

- Appears in sidebar nav or is linked from a parent index
- Renders correctly (math, code, tables) in the wiki shell
- Has a clear H1 and at least one cross-link
- For grammar/spec: matches the compiler at HEAD

The grammar page must never be a raw `.ebnf` dump without context. Always route through `language/grammar.md` first.

Every executable documentation claim also needs an appropriate verification surface. Run `./flow tool build_wiki` and `./flow tool wiki_links` for content changes; check the generated playground/tutorial/WASM routes with the browser jobs in `.github/workflows/live-demos.yml`. CI on a generated artifact is not a substitute for checking the deployed public site after a release.