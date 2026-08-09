# Third-Party Libraries

Flow ships a focused standard library in `lib/stdlib/`. The packages below are **not part of core Flow**, they live outside the language/compiler tree as optional libraries you can import, study, or extend.

| Package | Location | Proofs | Description |
|---------|----------|--------|-------------|
| **[flow-verify](flow-verify.md)** | `lib/verify/` + `examples/verify/` | ~1056 `.proof.md` under `examples/verify/` | Formal math with Claim Paths and stepped `.proof.md` writeups |

---

## flow-verify

A formal mathematics library (**flow-verify**), separate from everyday Flow programming. Proofs are ordinary Flow programs; each theorem has a human-readable `.proof.md` companion with numbered steps and trace tables.

**Highlights:**

- **Claim Paths**, facts addressed by what they claim (`Nat/+.zero-right`), not invented snake_case names
- **Stepped proofs**, every deductive move numbered and cited
- **Book export**, `./flow doc bundle` → unified PDF proof book
- **Mathlib roadmap**, phased plan toward Mathlib-scale coverage ([mathlib-equivalence-toc](../language/mathlib-equivalence-toc.md))

Browse the full [proof catalog](flow-verify-catalog.md) or read the [package overview](flow-verify.md).

The corpus is written ahead of the parser/checker in places (set-builder
operators, Euclidean ratios, ghost/ownership contracts). See
[flow-verify-parser-status.md](flow-verify-parser-status.md) for a categorized
breakdown of every `examples/verify/` parse failure and why it isn't a
core-Flow regression.

---

## Adding a third-party package

1. Place sources under `lib/<name>/`, `registry/packages/<name>/`, or an external git repo
2. Add a `flow.toml` and run `./flow publish` (or `./flow publish --git … --tag …`)
3. Add a page under `docs/third-party/<name>.md` and link it here
4. Run `./scripts/build_wiki.py` before deploy

Install for consumers: `./flow add <name>`, see [package-registry.md](../project/package-registry.md).