# Wiki Roadmap
 
> Note: this document tracks phased delivery for the Flow documentation website ([flooooooooooow.github.io/flow](https://flooooooooooow.github.io/flow/)). For the Flow language, compiler, and runtime roadmap, see [ROADMAP.md](../ROADMAP.md).  
> Strategy: [wiki-strategy.md](wiki-strategy.md)

---

## Existing website capabilities

| Item | Status |
|------|--------|
| Custom wiki shell (`site/index.html`, CSS, JS) | ✅ |
| Tab navigation + collapsible sidebar | ✅ |
| ⌘K search over docs + proofs | ✅ |
| KaTeX math in proof pages | ✅ |
| Optional third-party `flow-verify` proof section | ✅ |
| Euclid book index pages (auto-generated) | ✅ |
| Flow-native site builder (`./flow tool build_wiki`) | ✅ |
| Deploy script (`./flow tool deploy_wiki`) | ✅ build-only (VPS behind `FLOW_WIKI_VPS=1`) |
| Version dropdown + changelog | ✅ |
| GitHub Pages deploy (`wiki.yml`) | ✅ |
| VPS live deploy (`/flow/` + `/transpile/`) | ❌ disabled |
| Grammar page + EBNF viewer | ✅ |
| Language roadmap linked in nav | ✅ |
| Admonitions (`note/tip/warning/important/caution`) | ✅ |
| Interactive tutorials application | ✅ |
| 404 / not-found panel in wiki shell | ✅ |
| Proof link resolution + HTML-fallback guard | ✅ |
| Mobile drawer (backdrop / Escape / aria) | ✅ |
| Edit-on-GitHub per page | ✅ |
| Playground syntax explorer | ✅ |

---

## Phase 2: Reference completeness (in progress)

**Goal:** Every language feature has a reference page; nothing lives only in README.

| Task | Status | Notes |
|------|--------|-------|
| Comparison: Rust + Zig columns | ✅ | `comparison.md` |
| Benchmark results in wiki | ✅ | `project/benchmark-results.md` |
| Effects guide in nav | ✅ | `effects-showcase.md` |
| Autodiff guide | ✅ | `library/autodiff-guide.md` |
| Stdlib API autogen | ✅ | `./flow tool gen_stdlib_docs` → `library/stdlib-api.md` |
| Split `LANGUAGE_SPEC.md` into sections | ✅ | Index: `language/spec-index.md` (anchors + focused pages); full spec kept intact |
| RT-safety policy (audio) | ✅ | `library/rt-safety.md` linked from Audio DSP + nav |
| Changelog auto-sync on release | ✅ | `copy_docs()` ships `project/CHANGELOG.md`; `write_releases_index` + `versions.json` regenerate each build |

**Exit criteria:** Newcomers can compare languages, read effects/AD guides, and browse generated stdlib signatures without leaving the wiki.

---

## Phase 3: Interactive & searchable

| Task | Notes |
|------|-------|
| Pagefind wiki search | ✅ | `./flow tool build_wiki --pagefind` after wiki build when node/npx present; ⌘K uses Pagefind with `search-index.json` fallback |
| Playground and browser execution | partial | Browser interpreter, **Run (native local)** via `./flow tool playground_server`, and precompiled WASM demos are distinct targets; an in-browser native-equivalent Flow compiler remains deferred (#121). See [WebAssembly](language/wasm.md) and the [documentation guide](README.md) |
| Proof graph visualization | partial | Module-level import graph at `third-party/proof-graph.md`; per-theorem Claim Path edges remain open |
| Dark/light theme toggle | ✅ Header **Theme** button; `localStorage` key `flow-wiki-theme` |

---

## Phase 4: Platform

| Task | Notes |
|------|-------|
| `flow-lang.org` DNS + SSL | Redirect from `/flow/` + `/transpile/` |
| Versioned doc sets (`/v0.8/`, `/latest/`) | Build matrix in CI |
| Package docs (`flow.toml` dependencies) | Per-package subsites |
| CI auto-deploy on `main` | ✅ GitHub Pages (`wiki.yml`) |

---

## Relationship to language roadmap

The **language** roadmap (`ROADMAP.md`) tracks compiler features. The **wiki** roadmap tracks documentation delivery. They intersect at:

| Language milestone | Wiki deliverable |
|--------------------|------------------|
| Verification checker ships | Update `language/verification.md` status |
| Linux graphics | `language/graphics.md` platform section |
| WASM (C→emscripten) | `language/wasm.md` + playground note (#121 / #132) |
| Package registry | Third-party publishing guide |
| `flow-lang.org` | Phase 4 DNS + migration |

---

## Quality and acceptance gates

The historical page counts and performance targets are not evidence of the
current deployed site. Read the latest build and deployment logs rather than
copying a number from this roadmap. A documentation improvement is complete when
its canonical source and navigation are correct, generated pages have no broken
internal links, and the affected browser workflows pass on the proposed commit.

For interactive changes, distinguish the browser interpreter, precompiled WASM,
and native compilation. Validate keyboard navigation, accessible labels, output,
reset/share behaviour, and target-specific runtime errors in Chromium. Follow up
with a production Pages check after deployment; build-time tests do not prove
the public site is current.

## How to contribute

Edit the canonical Markdown under `docs/` and the navigation source in
`docs/nav.json`. Never edit generated `build/wiki/` files. The maintained
toolchain is Flow-native:

```bash
./flow tool gen_stdlib_docs --check
./flow tool build_wiki
./flow tool wiki_links
./flow tool wiki_browser verify
./flow tool wiki_browser contrast
```

The first command matters when standard-library exports or documentation
change. Browser tooling requires an available browser environment. For the
interactive playground, tutorials, live gallery or generated site routing, run
the corresponding Chromium checks in `.github/workflows/live-demos.yml`.
To preview the site locally, run
`./flow tool wiki_browser serve build/wiki 8777`.

### Releases / changelog

1. Update `docs/project/CHANGELOG.md` with a new `## [X.Y.Z] - YYYY-MM-DD` heading.
2. Rebuild. The wiki serves that file as `project/CHANGELOG.md` and regenerates `releases.md` + `versions.json` from it.
3. Deploy when you want the live site to pick up the new version.
