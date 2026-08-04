# Package Registry Design

**Status:** Deferred (design only — no implementation)  
**Date:** 2026-07-28  
**Related:** [Questions.md](../../Questions.md) · [Third-party libs](../third-party/README.md) · [Modules](../language/modules.md)

---

## Current state

Flow already has a project/dependency surface:

| Piece | Role today |
|-------|------------|
| `flow.toml` | Package name, entry, `[paths]`, `[dependencies]`, `[native]` |
| Local deps | `path` dependencies install into `flow_packages/<name>` and update `flow.lock` |
| Git deps | `{ git = "...", tag = "..." }` clones into `flow_packages/<name>` and checks out the requested ref |
| Registry | Deferred — bare name/version dependencies fail honestly until a public index exists |

There is **one** documented third-party package in the wiki: [flow-verify](../third-party/flow-verify.md). That is not enough demand to justify a central registry.

---

## Options

### 1. Git-only longer

Keep `flow.toml` deps as path + git URLs. Improve `flow add` / install to clone and pin (tag/commit) into `flow.lock`. No central index.

- **Pros:** Matches Zig/Go early ecosystems; zero hosting; works for private packages.
- **Cons:** Discovery is manual; no “browse packages” UX.

### 2. Minimal static registry

A static JSON (or TOML) index on the docs VPS — name → git URL + versions. CLI resolves names through the index, still fetches via git.

- **Pros:** Name-based `flow add foo`; cheap to host; wiki can generate a package list.
- **Cons:** Needs maintainers, naming policy, and trust story before there are packages to list.

### 3. Defer central registry

Ship no registry until the ecosystem has **3+ real third-party packages** (beyond in-tree / flow-verify). Document git/path deps as the supported path.

- **Pros:** Avoids empty crates.io-shaped infrastructure; design can follow real package shapes.
- **Cons:** No branded package search until that bar is met.

---

## Recommendation

**Option 3: defer**, with **git (+ local path) as the documented dependency path**.

Revisit a minimal static registry only when:

1. At least **three** independently maintained packages appear in [docs/third-party](../third-party/README.md), and  
2. Authors actually need name-based install (not just git URLs).

Until then, do not implement publish/search, and do not advertise a package index on the wiki home.

---

## Supported path (until then)

```toml
# flow.toml
[dependencies]
# Local / in-monorepo
my_lib = { path = "../my_lib" }

# Remote — preferred for third-party
audio_dsp = { git = "https://github.com/example/flow-audio-dsp", tag = "v0.3" }
```

Run:

```bash
./flow install
```

Installed dependencies are placed under `flow_packages/<name>` and pinned in
`flow.lock`. Dot imports resolve through the package name:

```flow
import audio_dsp.reverb { process_reverb }
```

Authors should:

1. Publish a git repo with its own `flow.toml`.
2. Consumers pin by tag or commit.
3. Consumers run `./flow install`.
4. Optionally add a wiki page under `docs/third-party/` for discoverability (see below).

---

## Wiki third-party interaction

The [third-party section](../third-party/README.md) is the **human discovery layer**, not a registry:

| Concern | Owner |
|---------|--------|
| “What packages exist?” | Wiki table in `docs/third-party/README.md` |
| “How do I install?” | This doc + git URL in each package page |
| “How do I resolve imports?” | `flow.toml` + module resolver ([modules](../language/modules.md)) |
| Name → URL index | Deferred (option 2 later) |

When a new package qualifies:

1. Add `docs/third-party/<name>.md` (overview, git URL, license, status).
2. Link it from `docs/third-party/README.md` and wiki nav.
3. Keep install instructions as **git clone / `flow.toml` git dep** — not `flow add` from a registry.

The wiki does **not** become an automatic package host. It catalogs packages the project chooses to highlight; git remains the source of truth for bits.

---

## Out of scope (for now)

- Central publish API or account system  
- Semver solver beyond lock-file pins  
- Mirroring / CDN of package tarballs  
- Replacing path deps for in-repo libs (`lib/verify`, stdlib)

---

## Decision log

| Date | Decision |
|------|----------|
| 2026-07-28 | Defer central registry; document git deps; design captured here |
