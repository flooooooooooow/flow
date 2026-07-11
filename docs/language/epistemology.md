# Flow Epistemology: Claim Paths

> **Third-party library (flow-verify)** — not core Flow syntax. See [flow-verify](../third-party/flow-verify.md).

> **Status:** Design spec  
> **Replaces:** `nat_add_zero`, `bool_or_commutes`, and all snake_case theorem names.

Snake_case forces you to **invent** a name and **explain** it in a comment. The name and the meaning drift apart. Mathlib has a hundred names for the same idea. We won't.

**A fact is not a function. A fact is a claim. Its address is derived from what it says.**

---

## The Core Idea

Every verified fact gets a **Claim Path** — a stable address built from:

```
Domain / Morphism . Facet
```

| Segment | What it is | Example |
|---------|------------|---------|
| **Domain** | What kind of thing | `Nat`, `Bool`, `FullAdder`, `RingBuffer`, `Matmul` |
| **Morphism** | What operation or transform | `+`, `||`, `push`, `vectorize`, `fuse` |
| **Facet** | What property, in plain English | `zero-left`, `commutes`, `correct`, `order-kept` |

Full address with package:

```
verify.Nat/+.zero-left
verify.Nat/+.commutes
verify.Bool/||.commutes
verify.FullAdder/out.correct
verify.Matmul/vectorize.semantics-equal
verify.RingBuffer/fifo.order-kept
```

**Literature is provenance, not naming.** You don't call it `peano_add_zero`. You call it `Nat/+.zero-left` and attach `@from peano` with a URL.

---

## Why This Hits Every Hoop

| Hoop | How Claim Paths solve it |
|------|--------------------------|
| Readable | `Nat/+.zero-left` reads as "naturals, addition, zero on the left" |
| No function creep | Same claim → same path → compiler rejects duplicates |
| Learn in the moment | `flow know Nat/+.zero-left` shows claim + proof + literature |
| Literature links | `@from` metadata, not baked into identifier |
| All domains | Same grammar for math, circuits, compilers, systems |
| Imports | `import verify.Nat/+ { zero-left, commutes }` |
| Modules | Package = `verify`, file = `Nat/+.flow` or `Nat.flow` |
| LLM-friendly | Regular structure, no invented abbreviations |

---

## Syntax in Flow

Claim Paths appear where names used to go. Same keywords — `theorem`, `assume`, `therefore`, `export`.

### Definitions (from literature)

```flow
# @means  Adding zero on the left gives the other number.
# @from   peano — https://en.wikipedia.org/wiki/Peano_axioms
# @tier   definition

theorem Nat/+.zero-left(m: Nat) {
    therefore 0 + m == m
}
```

### Derived facts

```flow
# @means  Adding zero on the right gives the same number.
# @from   peano/induction — Gries & Schneider, Ch. 3
# @tier   derived
# @needs  Nat/+.zero-left, Nat/+.succ-right

theorem Nat/+.zero-right(n: Nat) {
    if n == 0 {
        assume Nat/+.zero-left(0)
        therefore 0 + 0 == 0
    } else {
        let k = pred(n)
        assume Nat/+.zero-right(k)
        assume Nat/+.succ-left(k, 0)
        therefore n + 0 == n
    }
}
```

### Assume by address

```flow
assume Nat/+.zero-right(n)
assume Nat/+.commutes(n, b)
```

Not `assume add_commutes(n, b)`. The path *is* the reference.

### Export by facet

```flow
export Nat/+.zero-left, Nat/+.succ-right
```

### Import by morphism

```flow
import verify.Nat/+ { zero-left, succ-right }
import verify.Nat/+.zero-right
import .Nat/+.zero-right
```

Import the **morphism** (`Nat/+`) or a **specific facet** (`Nat/+.commutes`).

---

## Facet Naming Rules

Facets are short English phrases, kebab-case. They describe the property, not the proof technique.

| therefore clause | Facet | Not |
|------------------|-------|-----|
| `0 + m == m` | `zero-left` | `nat_zero_add`, `add_left_zero` |
| `n + 0 == n` | `zero-right` | `nat_add_zero`, `add_right_zero` |
| `a + b == b + a` | `commutes` | `add_commutes`, `comm_add` |
| `n + succ(m) == succ(n + m)` | `succ-right` | `add_succ` |
| `a or b == b or a` | `commutes` | `bool_or_commutes` |
| `n * n >= 0` | `square-nonneg` | `square_positive` |
| `C_naive == C_fast` | `semantics-equal` | `matmul_vectorized_correct` |
| `rb ~ Q after push` | `order-kept` | `push_preserves_fifo` |

**One facet per distinct claim.** If two proofs establish the same `therefore`, they share one path — you don't add a second name.

---

## Three Epistemic Tiers

Tier lives in `@tier` metadata. Never in the path.

```
definition   — how an operation is defined (Peano clauses, gate wiring)
axiom        — logical identity (reflexivity, excluded middle where accepted)
derived      — proved from definitions + other derived facts
```

Path says **what**. Tier says **how we know it**. `@from` says **where we learned it**.

```flow
# @tier   axiom
# @from   leibniz — https://en.wikipedia.org/wiki/Law_of_identity

theorem Eq/=.reflexive(x: Nat) {
    therefore x == x
}
```

---

## Domain Examples

### Math

```flow
theorem Nat/+.zero-left(m: Nat)   { therefore 0 + m == m }
theorem Nat/+.succ-right(n, m)   { therefore n + succ(m) == succ(n + m) }
theorem Nat/+.zero-right(n)      { ... }
theorem Nat/+.commutes(a, b)     { ... }
```

### Circuits

```flow
function FullAdder(...) -> ... { ... }

theorem FullAdder/out.correct(A, B, Cin) {
    let result = FullAdder(A, B, Cin)
    therefore result == binary_add_1bit(A, B, Cin) by exhaustive
}

theorem Ripple4/out.correct(A, B, Cin) {
    assume FullAdder/out.correct(...)
    ...
}
```

### Compiler transforms

```flow
theorem Matmul/vectorize.semantics-equal(m, n, k) {
    ...
    therefore matrices_equal(C_naive, C_fast, m, n)
}

theorem Loop/fuse.semantics-equal(n) {
    ...
    therefore memory_equal(separate, fused)
}
```

### Systems

```flow
theorem RingBuffer/fifo.order-kept(rb, q, x) {
    assume RingBuffer/fifo.matches-queue(rb, q)
    ...
    therefore rb_matches_queue(rb2, q2)
}
```

---

## Claim Fingerprints (duplicate prevention)

The compiler canonicalizes each `therefore` into a **fingerprint**.
Two theorems with the same domain, morphism, and fingerprint → **error**.

```flow
theorem Nat/+.zero-right(n: Nat) { therefore n + 0 == n }
theorem Nat/+.identity-right(n: Nat) { therefore n + 0 == n }  # ERROR: same claim
```

You cannot accidentally create `add_zero`, `zero_add`, `add_right_zero` for one fact.
The epistemology rejects synonyms at compile time.

---

## Proof Artifacts — English + LaTeX, auto-generated

Every verification file emits two companions alongside the source:

| File | Contents |
|------|----------|
| `Theorem.proof.md` | Plain-English proof with numbered theorems |
| `Theorem.proof.tex` | LaTeX with `\begin{theorem}`, numbered `\begin{equation}`, `\begin{proof}` |

```bash
flow doc proof examples/verify/math/derived/Nat-plus-zero-right.flow
flow doc proof examples/verify -r    # all theorem files
```

**English output** — Theorem 1 (Adding zero on the right…). Claim in plain language. Proof steps: base case, inductive step, therefore lines.

**LaTeX output** — Numbered theorem environments, equation labels (`\label{eq:Nat-plus-zero-right:1}`), cross-refs to dependencies (`\ref{thm:Nat-plus-zero-left}`), source citation in italics.

Regenerate on `flow verify` (planned) or manually via `flow doc proof`.

---

## `flow know` — learn in the moment

```bash
flow know verify.Nat/+.zero-right
```

```
verify.Nat/+.zero-right

  means:   Adding zero on the right gives the same number.
           Example: 12 + 0 = 12

  claim:   ∀n. n + 0 = n

  tier:    derived
  from:    peano/induction
           https://en.wikipedia.org/wiki/Mathematical_induction
           Gries & Schneider, Ch. 3

  needs:   Nat/+.zero-left, Nat/+.succ-right
  used-by: Nat/+.commutes

  proof:   [show structured proof]
```

No searching Mathlib. No guessing what `nat_add_zero` meant.

---

## How Claim Paths Meet Modules

| Layer | Syntax | Example |
|-------|--------|---------|
| Package | `flow.toml [paths]` | `verify = "lib/verify"` |
| Module file | one domain per file | `lib/verify/Nat.flow` |
| Morphism group | `export` or `import` | `import verify.Nat/+` |
| Single fact | full path | `assume Nat/+.commutes(a, b)` |

File layout:

```
lib/verify/
  Nat.flow          → verify.Nat/*     (all + facts)
  Bool.flow         → verify.Bool/*    (all || facts)
  FullAdder.flow    → verify.FullAdder/*
  RingBuffer.flow   → verify.RingBuffer/*
```

---

## Migration from Snake Case

| Old | Claim Path |
|-----|------------|
| `nat_zero_add` | `Nat/+.zero-left` |
| `nat_add_zero` | `Nat/+.zero-right` |
| `nat_add_succ` | `Nat/+.succ-right` |
| `nat_add_commutes` | `Nat/+.commutes` |
| `eq_reflexive` | `Eq/=.reflexive` |
| `bool_or_commutes` | `Bool/||.commutes` |
| `int_square_nonneg` | `Int/*.square-nonneg` |
| `full_adder_correct` | `FullAdder/out.correct` |
| `matmul_vectorized_correct` | `Matmul/vectorize.semantics-equal` |
| `push_preserves_fifo` | `RingBuffer/fifo.order-kept` |

---

## One Sentence

**Facts are addressed by what they claim (`Nat/+.zero-right`), grounded in literature (`@from peano`), and imported by morphism — never invented as snake_case and explained after the fact.**