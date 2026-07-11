# flow-verify

> **Third-party library — not core Flow.** You do not need flow-verify to compile or run ordinary programs. It is an optional formal-math package that shares Flow syntax.

> **Package:** `flow-verify`  
> **Paths:** `lib/verify/` (core modules), `examples/verify/` (extended corpus)  
> **Status:** Active development — verification checker is spec'd; proof documents and book export work today.

Formal mathematics for Flow: a proof is a program, a theorem is a function, and every fact lives at a stable **Claim Path**.

---

## What it is

`flow-verify` is not a separate language. It uses the same Flow syntax with four planned verification keywords (`theorem`, `assume`, `therefore`, `has property`). Today the corpus is written as Flow modules plus generated `.proof.md` step writeups.

Each proof file carries:

| Artifact | Role |
|----------|------|
| `*.flow` | Executable theorem / definition |
| `*.proof.md` | Numbered step narrative with LaTeX goals |
| `*.proof.tex` | Optional LaTeX export slice |

---

## Core modules (`lib/verify/`)

Foundational domains — Peano arithmetic, logic, data structures, and algebra stubs:

| Module | Domain | Proofs |
|--------|--------|--------|
| `Eq` | Leibniz identity, substitution | reflexivity, symmetry |
| `Bool` | Boolean algebra | OR/AND commute, De Morgan |
| `Nat`, `Nat-core`, `Nat-mul`, `Nat-order`, `Nat-sq` | Peano naturals | addition, order, squaring |
| `Int`, `Rat`, `Ratio`, `Real` | Number towers | scaffolding |
| `Pair`, `List`, `Comb`, `Finset` | Discrete structures | cons, append, length |
| `Order` | Order theory | basic lemmas |
| `Group`, `Monoid`, `Ring`, `Ideal`, `Subgroup`, `GroupHom`, `RingHom` | Abstract algebra | definitions + early lemmas |

Open any module proof: e.g. [lib/verify/Nat.proof.md](../../third-party/flow-verify/proofs/lib/Nat.proof.md)

---

## Extended corpus (`examples/verify/`)

| Area | Contents | Scale |
|------|----------|-------|
| **math/derived** | Derived arithmetic & list lemmas | ~80 proofs |
| **euclid/** | Elements Books I–VI (stepped) | ~350 proofs |
| **geometry/** | Taylor series, inscribed angles | 2 proofs |
| **analysis/** | Sine derivatives at zero | 1 proof |
| **circuits/** | Full adder correctness | 1 proof |
| **systems/** | Ring buffer FIFO | 1 proof |
| **transforms/** | Matrix-vectorize semantics | 1 proof |

Euclid Book I is complete (48/48 stepped). Books II–VI are scaffolded with full proposition coverage.

---

## Claim Paths

Facts are named by **what they claim**, not by author-chosen identifiers:

```
Nat/+.zero-right       not  nat_add_zero
Bool/||.commutes       not  bool_or_commutes
Matmul/vectorize.semantics-equal
```

See [epistemology](../language/epistemology.md) for the full grammar and [verification](../language/verification.md) for the language design.

---

## Proof book

The unified proof book merges algebra, geometry, and analysis into continuous theorem numbering.

| Resource | Description |
|----------|-------------|
| [math-proof-book.md](../language/math-proof-book.md) | Book contract + Phase 1 chapters |
| [mathlib-equivalence-toc.md](../language/mathlib-equivalence-toc.md) | Mathlib parity roadmap (~150k target) |
| [flow-verify-catalog.md](flow-verify-catalog.md) | Auto-generated index of all `.proof.md` files |

**Export PDF:**

```bash
./flow doc bundle
# → build/proofs/flow-proof-book.pdf
```

**Single module:**

```bash
./flow doc proof lib/verify/Nat.flow
```

---

## Literature tiers

Every theorem declares a **tier**:

| Tier | Meaning |
|------|---------|
| `definition` | Stipulated (Peano successor, group axioms) |
| `axiom` | Ontological commitment without proof |
| `derived` | Proved from earlier Claim Paths |

Provenance uses `@from` tags (peano, euclid, boole, church, brook taylor, …) with Wikipedia or primary-source URLs.

---

## Browse proofs

Use the wiki sidebar under **Third-Party → Proof Catalog**, or jump directly to a section:

- [Core library proofs](../../third-party/flow-verify/proofs/lib/)
- [Math derived](../../third-party/flow-verify/proofs/examples/math/derived/)
- [Euclid Book I](../../third-party/flow-verify/proofs/examples/euclid/book-i/)
- [Geometry & analysis](../../third-party/flow-verify/proofs/examples/geometry/)

---

## Contributing

1. Pick a Claim Path from [math-proof-book.md](../language/math-proof-book.md) marked ⬜
2. Write `theorem` in a `.flow` file under `lib/verify/` or `examples/verify/`
3. Run `./flow doc proof <file.flow>` to regenerate `.proof.md`
4. `./scripts/build_wiki.py` refreshes the catalog for the wiki

CI will eventually run `flow know --lint-duplicates` to block synonym creep.