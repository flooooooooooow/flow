# Wiki Roadmap

> Phased plan for [abhishek-shivakumar.com/transpile](https://abhishek-shivakumar.com/transpile/)  
> Strategy: [wiki-strategy.md](wiki-strategy.md)

---

## Current state (Phase 0 — shipped locally)

| Item | Status |
|------|--------|
| Custom wiki shell (`site/index.html`, CSS, JS) | ✅ |
| Tab navigation + collapsible sidebar | ✅ |
| ⌘K search over docs + proofs | ✅ |
| KaTeX math in proof pages | ✅ |
| Third-party `flow-verify` section (676 proofs) | ✅ |
| Euclid book index pages (auto-generated) | ✅ |
| Build script (`scripts/build_wiki.py`) | ✅ |
| Deploy script (`scripts/deploy_wiki.py`) | ✅ (blocked when VPS unreachable) |
| Version dropdown + changelog | ✅ |
| VPS live deploy | 🔲 pending |

---

## Phase 1 — Polish & deploy (now → 2 weeks)

**Goal:** Live site looks pristine; grammar and reference pages are professional.

| Task | Priority | Owner |
|------|----------|-------|
| Deploy `build/wiki/` to VPS | P0 | `./scripts/deploy_wiki.py` |
| Grammar page + EBNF viewer | P0 | `language/grammar.md` + JS viewer |
| Wiki strategy & roadmap (this doc) | P0 | docs |
| Link language roadmap from wiki | P1 | Copy/symlink `ROADMAP.md` into docs |
| Fix `grammar.ebnf` copy path in build | P1 | `docs/grammar.ebnf` |
| Admonition blocks (`> [!note]`) in CSS | P2 | wiki.js renderer |
| Playground link works from production | P1 | verify `playground/index.html` (page refreshed 2026-07 as a non-executing syntax explorer with 9 compile-verified samples) |
| 404 / error page in wiki shell | P2 | wiki.js |

**Exit criteria:** `https://abhishek-shivakumar.com/transpile/` shows new shell; grammar page is navigable and readable; strategy doc is in sidebar.

---

## Phase 2 — Reference completeness (1–2 months)

**Goal:** Every language feature has a reference page; nothing lives only in README.

| Task | Notes |
|------|-------|
| Split `LANGUAGE_SPEC.md` into navigable sections | Or generate sidebar from headings |
| Stdlib autogen from `.flow` sources | Signatures + doc comments |
| Effects & autodiff dedicated guides | Beyond stdlib API list |
| Comparison page: add Zig + Rust columns | Update `comparison.md` |
| Benchmark results embedded | Link `benchmarks/suite/RESULTS.md` |
| Changelog synced from `project/CHANGELOG.md` | Auto on release |

---

## Phase 3 — Interactive & searchable (2–4 months)

| Task | Notes |
|------|-------|
| Pagefind or Algolia index | Replace hand-rolled JSON at 1000+ pages |
| Playground: compile via WASM or API | Tutorial embed buttons |
| Proof graph visualization | Claim Path dependency edges |
| Dark/light theme toggle | CSS variables already structured |
| Mobile nav polish | Test on phone |

---

## Phase 4 — Platform (6+ months)

| Task | Notes |
|------|-------|
| `flow-lang.org` DNS + SSL | Redirect from `/transpile/` |
| Versioned doc sets (`/v0.8/`, `/latest/`) | Build matrix in CI |
| Community edit links | "Edit on GitHub" per page |
| Package docs (`flow.toml` dependencies) | Per-package subsites |
| CI auto-deploy on `main` | Webhook to VPS |

---

## Relationship to language roadmap

The **language** roadmap (`ROADMAP.md`) tracks compiler features (day-to-day task
status lives on the local Helm board, `http://127.0.0.1:9470/app?project=flow`).
The **wiki** roadmap tracks documentation delivery. They intersect at:

| Language milestone | Wiki deliverable |
|--------------------|------------------|
| Verification checker ships | Update `language/verification.md` status; proof lint docs |
| Linux graphics | `language/graphics.md` platform section |
| Package registry | Third-party publishing guide |
| `flow-lang.org` | Phase 4 DNS + migration |

Language roadmap does not block wiki Phase 1 deploy — documentation can lead implementation for verification and grammar.

---

## Metrics

| Metric | Target (Phase 1) | Target (Phase 4) |
|--------|------------------|------------------|
| Pages in nav | 50+ | 200+ |
| Proof pages hosted | 676 | 2,000+ |
| Deploy time | < 2 min | < 30 s (CI) |
| Search latency | < 100 ms | < 50 ms (Pagefind) |
| Lighthouse accessibility | 90+ | 95+ |

---

## How to contribute

1. Edit markdown under `docs/`
2. Run `./scripts/build_wiki.py`
3. Preview: `cd build/wiki && python3 -m http.server 8777`
4. Open PR; after merge, run `./scripts/deploy_wiki.py`

For new third-party packages, follow [third-party/README.md](third-party/README.md) and update `write_nav()` in `build_wiki.py`.