# Wiki Roadmap

> Phased plan for [flooooooooooow.github.io/flow](https://flooooooooooow.github.io/flow/)  
> Strategy: [wiki-strategy.md](wiki-strategy.md)

---

## Current state (Phase 0-1, shipped)

| Item | Status |
|------|--------|
| Custom wiki shell (`site/index.html`, CSS, JS) | ✅ |
| Tab navigation + collapsible sidebar | ✅ |
| ⌘K search over docs + proofs | ✅ |
| KaTeX math in proof pages | ✅ |
| Third-party `flow-verify` section (1000+ proofs) | ✅ |
| Euclid book index pages (auto-generated) | ✅ |
| Build script (`scripts/build_wiki.py`) | ✅ |
| Deploy script (`scripts/deploy_wiki.py`) | ✅ build-only (VPS behind `FLOW_WIKI_VPS=1`) |
| Version dropdown + changelog | ✅ |
| GitHub Pages deploy (`wiki.yml`) | ✅ |
| VPS live deploy (`/flow/` + `/transpile/`) | ❌ disabled |
| Grammar page + EBNF viewer | ✅ |
| Language roadmap linked in nav | ✅ |
| Admonitions (`note/tip/warning/important/caution`) | ✅ |
| Interactive tutorials app (40+ lessons) | ✅ |
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
| Stdlib API autogen | ✅ | `scripts/gen_stdlib_docs.py` → `library/stdlib-api.md` |
| Split `LANGUAGE_SPEC.md` into sections | ✅ | Index: `language/spec-index.md` (anchors + focused pages); full spec kept intact |
| RT-safety policy (audio) | ✅ | `library/rt-safety.md` linked from Audio DSP + nav |
| Changelog auto-sync on release | ✅ | `copy_docs()` ships `project/CHANGELOG.md`; `write_releases_index` + `versions.json` regenerate each build |

**Exit criteria:** Newcomers can compare languages, read effects/AD guides, and browse generated stdlib signatures without leaving the wiki.

---

## Phase 3: Interactive & searchable (2-4 months)

| Task | Notes |
|------|-------|
| Pagefind wiki search | ✅ | `scripts/build_pagefind.sh` after wiki build when node/npx present; ⌘K uses Pagefind with `search-index.json` fallback |
| Playground: compile via WASM or API | partial ✅ | browser interpreter + **Run (native local)** via `scripts/playground_compile_server.py` (#132); next: emscripten hello artifact (`scripts/build_wasm_hello.sh`, [language/wasm.md](language/wasm.md)); in-browser Flow compiler still deferred (#121) |
| Proof graph visualization | ✅ partial: module-level `import` graph (`third-party/proof-graph.md`, `scripts/build_wiki.py::build_proof_graph`); per-theorem Claim Path edges still open |
| Dark/light theme toggle | ✅ Header **Theme** button; `localStorage` key `flow-wiki-theme` |

---

## Phase 4: Platform (6+ months)

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

## Metrics

| Metric | Target (now) | Target (Phase 4) |
|--------|--------------|------------------|
| Pages in nav | 50+ | 200+ |
| Proof pages hosted | 1000+ | 2,000+ |
| Deploy time | < 2 min | < 30 s (CI) |
| Search latency | < 100 ms | < 50 ms (Pagefind) |

---

## How to contribute

1. Edit markdown under `docs/`
2. Run `python3 scripts/gen_stdlib_docs.py` (if touching stdlib)
3. Run `python3 scripts/build_wiki.py` (also runs Pagefind if `node`/`npx` are available)
4. Optional re-index only: `./scripts/build_pagefind.sh`
5. Preview: `cd build/wiki && python3 -m http.server 8777`
6. Preview: `cd build/wiki && python3 -m http.server 8777`. Production deploys from `main` via GitHub Pages.

### Releases / changelog

1. Update `docs/project/CHANGELOG.md` with a new `## [X.Y.Z] - YYYY-MM-DD` heading.
2. Rebuild. The wiki serves that file as `project/CHANGELOG.md` and regenerates `releases.md` + `versions.json` from it.
3. Deploy when you want the live site to pick up the new version.
