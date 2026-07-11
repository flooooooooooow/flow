# Third-Party Libraries

Flow ships a focused standard library in `lib/stdlib/`. The packages below are **not part of core Flow** — they live outside the language/compiler tree as optional libraries you can import, study, or extend.

| Package | Location | Proofs | Description |
|---------|----------|--------|-------------|
| **[flow-verify](flow-verify.md)** | `lib/verify/` + `examples/verify/` | 519 | Formal math with Claim Paths and stepped `.proof.md` writeups |

---

## flow-verify

A formal mathematics library (**flow-verify**), separate from everyday Flow programming. Proofs are ordinary Flow programs; each theorem has a human-readable `.proof.md` companion with numbered steps and trace tables.

**Highlights:**

- **Claim Paths** — facts addressed by what they claim (`Nat/+.zero-right`), not invented snake_case names
- **Stepped proofs** — every deductive move numbered and cited
- **Book export** — `./flow doc bundle` → unified PDF proof book
- **Mathlib roadmap** — phased plan toward Mathlib-scale coverage ([mathlib-equivalence-toc](../language/mathlib-equivalence-toc.md))

Browse the full [proof catalog](flow-verify-catalog.md) or read the [package overview](flow-verify.md).

---

## Adding a third-party package

1. Place sources under `lib/<name>/` or `examples/<name>/`
2. Add a page under `docs/third-party/<name>.md`
3. Register it in this index and in `site/wiki-nav.json`
4. Run `./scripts/build_wiki.py` before deploy

Packages should declare their own `flow.toml` when they become independently installable.