# Flow Verification: Same Language, Same Syntax

> **Third-party library — not core Flow.** Formal math verification lives in the **`flow-verify`** package ([overview](../third-party/flow-verify.md)). Core Flow is a general-purpose compiled language; `theorem` / `therefore` keywords are planned for the library, not required to write everyday programs.

> **Status:** Design spec (not yet implemented)  
> **Core idea:** A proof is a program. A theorem is a function. No second language.

Flow already has `let`, `if`, `for`, `while`, `struct`, `function`. Verification adds exactly four keywords:

```
theorem       — declare something that must be true
assume        — bring a fact into scope
therefore     — state what follows (the checker verifies it)
has property  — attach a claim to code, types, or loops
```

Everything else is ordinary Flow.

---

## Documentation Is Mandatory

Every `theorem` carries a header comment in plain English. No exceptions.
If you cannot write the header, the theorem should not exist.

```flow ignore="illustrative code skeleton"
# ── nat_add_zero ────────────────────────────────────────────────
# means:  Adding zero on the right gives you the same number.
#         Example: 12 + 0 = 12
#
# from:   Derived by induction from the Peano definition of addition.
#         Peano axioms: https://en.wikipedia.org/wiki/Peano_axioms
#         Proof style:  Gries & Schneider, *A Logical Approach to
#         Discrete Math*, Ch. 3 — https://www.springer.com/series/634
#
# tier:   derived
# needs:  nat_add_succ, nat_zero_add
# used_by: nat_add_commutes
# ────────────────────────────────────────────────────────────────

theorem nat_add_zero(n: Nat) {
    ...
}
```

### Header fields

| Field | Required | Purpose |
|-------|----------|---------|
| `means` | always | One or two sentences a beginner understands |
| `from` | always | Where this comes from — textbook, paper, axiom system, with URL |
| `tier` | always | `definition`, `axiom`, or `derived` |
| `needs` | if derived | Which theorems it depends on |
| `used_by` | if known | Which proofs consume it — prevents orphans |

The checker warns on missing headers. CI fails on orphan derived theorems (proved but never referenced).

---

## Claim Paths, Not Snake Case

Facts are addressed by **what they claim**, not invented names.
See [epistemology.md](epistemology.md) for the full system.

```
Domain / Morphism . Facet

Nat/+.zero-right      not  nat_add_zero
Nat/+.commutes        not  add_commutes
Bool/||.commutes      not  bool_or_commutes
Matmul/vectorize.semantics-equal
```

- **Path** = what the fact says
- **`@from`** = literature provenance (peano, landau, boole — with URL)
- **`@tier`** = definition | axiom | derived
- **Same claim → same path** — compiler rejects synonym creep

```flow ignore="illustrative code skeleton"
theorem Nat/+.zero-right(n: Nat) {
    @from peano/induction
    therefore n + 0 == n
}

assume Nat/+.zero-right(n)
import verify.Nat/+ { zero-left, succ-right }
```

No function creep: two theorems with the same `therefore` cannot get different paths.

---

## Theorem = Function

A theorem has parameters and a body, just like `function`.

```flow
# ── nat_add_commutes ────────────────────────────────────────────
# means:  You can swap the order of addition.
#         Example: 3 + 5 = 5 + 3
#
# from:   Standard result in Peano arithmetic; see Landau,
#         *Foundations of Analysis* (1921), Ch. 1
#         https://en.wikipedia.org/wiki/Foundations_of_analysis_(book)
#
# tier:   derived
# needs:  nat_add_zero, nat_zero_add, nat_add_succ
# ────────────────────────────────────────────────────────────────

theorem nat_add_commutes(a: Nat, b: Nat) {
    if a == 0 {
        assume nat_add_zero(b)
        assume nat_zero_add(b)
        therefore a + b == b + a
    } else {
        let n = pred(a)
        assume nat_add_commutes(n, b)
        assume nat_add_succ(n, b)
        therefore a + b == b + a
    }
}
```

### `therefore` with steps

```flow ignore="illustrative code skeleton"
let step = succ(n + b)    by nat_add_succ(n, b)
therefore lhs == rhs
```

### Automation suffixes

```flow ignore="the `therefore ... by` proof form parses but has no lowering yet"
therefore x == y by exhaustive
therefore x == y by smt
therefore x == y by symbolic
```

---

## `has property` = Spec on Real Code

```flow ignore="illustrative code skeleton"
function ring_push(rb: ptr<RingBuffer>, value: i32) -> i32
    has property not ring_is_full(rb) before
    has property ring_size(rb) == old(ring_size(rb)) + 1 after
{
    ...
}
```

Properties get the same header comments as theorems.

---

## Domain Examples

### Math — minimal foundations, derive the rest

`lib/verify/nat.flow` holds **definitions only**:

```flow
# means:  Adding zero on the left gives the other number.  (0 + 5 = 5)
# from:   Peano recursive definition of +
# tier:   definition

theorem nat_zero_add(m: Nat) {
    therefore 0 + m == m
}

# means:  Adding one more on the right steps the result.  (3 + succ(2) = succ(5))
# from:   Peano recursive definition of +
# tier:   definition

theorem nat_add_succ(n: Nat, m: Nat) {
    therefore n + succ(m) == succ(n + m)
}
```

Everything else (`nat_add_zero`, `nat_add_commutes`, …) lives in `derived/` and lists `needs`.

### Circuits — function + theorem, literature link to the architecture

```flow ignore="proof metadata header, not code"
# means:  The full adder output matches binary addition with carry.
# from:   Patterson & Hennessy, *Computer Organization and Design*, §A.5
#         https://en.wikipedia.org/wiki/Adder_(electronics)#Full_adder
# tier:   derived
# needs:  (truth table — exhaustive over 8 inputs)
```

### Compiler opts — run both, therefore equal

```flow ignore="proof metadata header, not code"
# means:  Vectorized matmul writes the same matrix as the naive version.
# from:   BLIS design paper (Van Zee & van de Geijn, 2015) for why we vectorize;
#         this theorem states the optimisation is sound, not why we want it.
# tier:   derived
# needs:  matmul_naive, matmul_vectorized_0
```

---

## Checker & CI Rules

| Rule | Enforcement |
|------|-------------|
| Every theorem has `means` + `from` + `tier` | warning → error |
| `derived` must list `needs` | error |
| No two theorems with the same `means` (synonym lint) | error |
| `derived` with empty `used_by` after 30 days | CI warning |
| Names must match `<domain>_<operation>_<property>` | lint |

---

## Implementation Phases

| Phase | What ships |
|-------|------------|
| **1** | `theorem`, `assume`, `therefore`, `has property` + header lint |
| **2** | `lib/verify/nat.flow` foundations + `derived/` |
| **3** | SMT / exhaustive backends |
| **4** | Orphan-theorem CI, synonym detection |
| **5** | `flow verify --explain <theorem>` prints header + proof trace |

---

## Proof Artifacts (auto-generated)

Every verification `.flow` file generates two companions:

| Output | Contents |
|--------|----------|
| `*.proof.md` | Plain-English proof, numbered theorems, literature |
| `*.proof.tex` | LaTeX with `\begin{theorem}`, numbered equations, `\begin{proof}` |

```bash
flow doc proof examples/verify/math/derived/Nat-plus-zero-right.flow
flow doc proof examples/verify -r
```

See [epistemology.md](epistemology.md) for Claim Paths and artifact details.

---

## One Sentence

**Flow verification is Flow — every fact is named once, explained in English, linked to literature, and added only when something actually needs it.**
