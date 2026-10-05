# Flow Mathlib Equivalence — Master Table of Contents

> **Status:** Living roadmap  
> **Goal:** A single numbered proof book and `lib/verify` corpus that covers the same mathematical ground as [Lean + Mathlib](https://leanprover-community.github.io/mathlib-overview.html), with every fact at a stable Claim Path and traceable proof steps.  
> **Companion:** [math-proof-book.md](math-proof-book.md) (book contract), [epistemology.md](epistemology.md) (Claim Path grammar)

---

## Where we are vs Mathlib

| Metric | Flow today | Mathlib4 (approx.) |
|--------|------------|-------------------|
| Verified declarations in book | **123** | **~150,000** |
| Proof depth | ~73 stepped (arith + data); **Euclid Book I complete (48/48 stepped)** | Full tactic proofs |
| Book parts | Part I (54) + Part II (19) + Euclid I (48) + Appendix (2) | N/A (module tree) |
| Claim registry | `flow know`, per-theorem `.proof.md` | `docs/overview.yaml` + module index |
| Geometry | Euclid Book I scaffolded | Affine, manifold, algebraic geometry |

**Interpretation:** Infrastructure is sound; content is ~0.04% of Mathlib scale. This document is the **build order** to close that gap without Mathlib-style naming bloat.

---

## Build phases (what we build first)

Phases are **dependency-ordered**. Each phase ships a PDF slice via `BOOK_PARTS` and a `lib/verify` subtree.

| Phase | Name | Target theorems | Mathlib mirror | Depends on | ETA (aggressive) |
|-------|------|-----------------|----------------|------------|------------------|
| **0** | Engine & book contract | — | `Tactic`, `Testing` | — | ✅ done |
| **1** | Logic + Peano spine | **~200** | `Init`, `Logic`, `Data.Nat` | 0 | **now → 8 wk** |
| **2** | Discrete structures | **~350** | `Data`, `Order`, `Combinatorics` (basic) | 1 | 8 wk |
| **3** | Euclidean corpus | **~350** | `Geometry` (synthetic) | 1 | 6 wk (I done, II–VI next) |
| **4** | Algebra core | **~800** | `Algebra`, `GroupTheory`, `RingTheory` | 1–2 | 12 wk |
| **5** | Linear algebra | **~600** | `LinearAlgebra` | 4 | 10 wk |
| **6** | Topology & metric analysis | **~1,200** | `Topology`, `Analysis` (metric) | 5 | 16 wk |
| **7** | Measure & probability | **~900** | `MeasureTheory`, `Probability` | 6 | 14 wk |
| **8** | Number theory | **~700** | `NumberTheory` | 4 | 12 wk |
| **9** | Manifolds & advanced geometry | **~1,000** | `Geometry.Manifold`, `AlgebraicGeometry` | 6–7 | 20 wk |
| **10** | Category theory & homological | **~800** | `CategoryTheory`, homological slice | 4–5 | 16 wk |
| **11** | Set theory & foundations | **~400** | `SetTheory`, `ModelTheory` | 1 | 10 wk |
| **12** | Computability & dynamics | **~300** | `Computability`, `Dynamics` | 11 | 8 wk |
| **Σ** | **Full Mathlib parity** | **~7,600** (core) → **~150k** (complete) | all `Mathlib/*` | — | multi-year |

**Phase 1–3 = “undergraduate Mathlib”** (~900 theorems): enough to replace a first proof course + discrete math + Euclid.

---

## Book spine (`BOOK_PARTS` target)

Continuous theorem numbering across parts. Current → target:

```
Part 0   — Meta (not in book)
Part I   — Logic and Arithmetic          [ 54 →  200]   Phase 1
Part II  — Data and Order                [ 19 →  350]   Phase 2
Book I   — Euclid's Elements             [ 48 →   48]   Phase 3a ✅ scaffold
Book II  — Euclid (areas)                [  0 →   14]
Book III — Euclid (circles)                [  0 →   37]
Book IV  — Euclid (polygons)               [  0 →   16]
Book V   — Euclid (proportion)             [  0 →   25]
Book VI  — Euclid (similar figures)        [  0 →   33]
Part III — Algebra                       [  0 →  800]   Phase 4
Part IV  — Linear Algebra                [  0 →  600]   Phase 5
Part V   — Topology                      [  0 →  500]   Phase 6
Part VI  — Analysis                      [  0 →  700]   Phase 6–7
Part VII — Number Theory                 [  0 →  700]   Phase 8
Part VIII— Combinatorics                 [  0 →  400]   Phase 2+
Part IX  — Probability                   [  0 →  500]   Phase 7
Part X   — Category & Algebraic Geometry [  0 →  800]   Phase 9–10
Part XI  — Set Theory & Logic            [  0 →  400]   Phase 11
Part XII — Computability & Dynamics      [  0 →  300]   Phase 12
Appendix — Special topics (Taylor, etc.) [  2 →   50]
```

Command: `./flow doc bundle` → `build/proofs/flow-proof-book.pdf`

---

## Volume I — Foundations (Phase 1)

**Mathlib:** `Init`, `Logic`, `Order` (basic), `Data.Nat`  
**Flow package:** `lib/verify/` + `examples/verify/math/`

### §1 Logic and equality (`Logic`, `Eq`, `Bool`)

| § | Claim Path | Tier | Mathlib anchor | Status |
|---|------------|------|----------------|--------|
| 1.1 | `Eq/=.reflexive` | axiom | `Eq.refl` | ✅ |
| 1.2 | `Eq/=.symmetric` | derived | `Eq.symm` | ⬜ |
| 1.3 | `Eq/=.transitive` | derived | `Eq.trans` | ⬜ |
| 1.4 | `Eq/=.subst` | derived | `Eq.subst` | ⬜ |
| 1.5 | `Eq/=.congr` | derived | `congrArg` | ⬜ |
| 1.6 | `Prop/→.intro` | definition | `Function` | ⬜ |
| 1.7 | `Prop/∧.intro` | definition | `And.intro` | ⬜ |
| 1.8 | `Prop/∨.intro-left` | definition | `Or.inl` | ⬜ |
| 1.9 | `Prop/¬.def` | definition | `Not` | ⬜ |
| 1.10 | `Bool/||.commutes` | derived | `Bool.or_comm` | ✅ |
| 1.11–1.24 | `Bool/*` algebra | derived | `Bool` ring | 1/16 |

**Files:** `lib/verify/Eq.flow`, `lib/verify/Bool.flow`, `lib/verify/Prop.flow`

### §2 Natural numbers — Peano core (`Data.Nat.Basic`)

| § | Claim Path | Tier | Mathlib anchor | Status |
|---|------------|------|----------------|--------|
| 2.1 | `Nat/succ.injective` | derived | `Nat.succ.inj` | ⬜ |
| 2.2 | `Nat/pred.succ-left` | definition | `Nat.pred_succ` | ⬜ |
| 2.3 | `Nat/0.not-succ` | derived | `Nat.zero_ne_succ` | ⬜ |
| 2.4 | `Nat/succ.ne-zero` | derived | `Nat.succ_ne_zero` | ⬜ |
| 2.5 | `Nat/cases.two` | derived | `Nat.casesOn` | ⬜ |
| 2.6 | `Nat/induction.principle` | meta | `Nat.rec` | ⬜ |
| 2.7 | `Nat/eq.decidable` | derived | `Nat.decEq` | ⬜ |

**Files:** `lib/verify/Nat-core.flow`

### §3 Natural numbers — addition (`Algebra.Group.Nat`)

| § | Claim Path | Tier | Status |
|---|------------|------|--------|
| 3.1 | `Nat/+.zero-left` | definition | ✅ |
| 3.2 | `Nat/+.succ-right` | definition | ✅ |
| 3.3 | `Nat/+.zero-right` | derived | ✅ |
| 3.4 | `Nat/+.commutes` | derived | ✅ |
| 3.5 | `Nat/+.assoc` | derived | ⬜ |
| 3.6 | `Nat/+.succ-left` | derived | ⬜ |
| 3.7 | `Nat/+.cancel-left` | derived | ⬜ |
| 3.8 | `Nat/+.cancel-right` | derived | ⬜ |

**Files:** `lib/verify/Nat.flow`, `examples/verify/math/derived/Nat-plus-*.flow`

### §4 Natural numbers — multiplication

| § | Claim Path | Tier | Status |
|---|------------|------|--------|
| 4.1 | `Nat/*.zero-left` | definition | ⬜ |
| 4.2 | `Nat/*.succ-right` | definition | ⬜ |
| 4.3 | `Nat/*.zero-right` | derived | ⬜ |
| 4.4 | `Nat/*.one-left` | derived | ⬜ |
| 4.5 | `Nat/*.commutes` | derived | ⬜ |
| 4.6 | `Nat/*.assoc` | derived | ⬜ |
| 4.7 | `Nat/*.distrib-left` | derived | ⬜ |
| 4.8 | `Nat/*.distrib-right` | derived | ⬜ |
| 4.9 | `Nat/sq.def` | definition | ⬜ |
| 4.10 | `Nat/sq.nonneg` | derived | ⬜ |

**Files:** `lib/verify/Nat-mul.flow`

### §5 Natural numbers — order

| § | Claim Path | claim | Status |
|---|------------|-------|--------|
| 5.1 | `Nat/<=.refl` | `n ≤ n` | ⬜ |
| 5.2 | `Nat/<=.antisym` | antisymmetry | ⬜ |
| 5.3 | `Nat/<=.trans` | transitivity | ⬜ |
| 5.4 | `Nat/<.succ` | `n < succ(n)` | ⬜ |
| 5.5 | `Nat/<=.trichotomy` | trichotomy | ⬜ |
| 5.6 | `Nat/<=.plus-right` | monotonicity | ⬜ |
| 5.7–5.14 | `Nat/<.*` | order ↔ `*`, `/`, `%` | ⬜ |

**Files:** `lib/verify/Nat-order.flow`

### §6 Integers (`Data.Int`)

| § | Claim Path | Status |
|---|------------|--------|
| 6.1 | `Int/+.def` | ⬜ |
| 6.2 | `Int/*.square-nonneg` | ✅ |
| 6.3–6.18 | `Int/+.*`, `Int/*.*`, `Int/<=.*`, `Int/abs.*` | ⬜ |

**Files:** `lib/verify/Int.flow`

### §7 Rationals (`Data.Rat`)

| § | Claim Path | Mathlib anchor | Status |
|---|------------|----------------|--------|
| 7.1 | `Rat/+.def` | pair quotient | ⬜ |
| 7.2 | `Rat/*.def` | field ops | ⬜ |
| 7.3 | `Rat/<=.def` | order | ⬜ |
| 7.4 | `Rat/dense` | between any two, a third | ⬜ |

**Files:** `lib/verify/Rat.flow`

### §8 Reals (`Data.Real`)

| § | Claim Path | Mathlib anchor | Status |
|---|------------|----------------|--------|
| 8.1 | `Real/Cauchy.def` | Cauchy sequences | ⬜ |
| 8.2 | `Real/+.complete` | completeness | ⬜ |
| 8.3 | `Real/sup.exists` | least upper bound | ⬜ |
| 8.4 | `Real/archimedean` | Archimedean property | ⬜ |

**Files:** `lib/verify/Real.flow` (Dedekind or Cauchy — pick one, document in `@from`)

### §9 Complex numbers (`Data.Complex`)

| § | Claim Path | Status |
|---|------------|--------|
| 9.1 | `Complex/+.def` | ⬜ |
| 9.2 | `Complex/*.def` | ⬜ |
| 9.3 | `Complex/i.sq` | `i² = -1` | ⬜ |
| 9.4 | `Complex/isAlgClosed` | fundamental theorem of algebra | ⬜ |

**Files:** `lib/verify/Complex.flow`

**Phase 1 target:** ~200 theorems, fully stepped proofs for §1–§5; §6–§9 definitions + 10 flagship derived facts.

---

## Volume II — Data structures & order (Phase 2)

**Mathlib:** `Data`, `Order`, `Combinatorics` (enumerative basics)  
**Flow package:** `lib/verify/Data/`, `lib/verify/Order/`

### §10 Products and sums

| Block | Claim paths | Target count |
|-------|-------------|--------------|
| `Pair/fst`, `Pair/snd`, `Prod/×.*` | projections, pairing, associativity | 12 |
| `Sum/inl`, `Sum/inr`, `Sum/cases` | coproduct | 10 |

### §11 Lists and sequences

| Block | Claim paths | Target count |
|-------|-------------|--------------|
| `List/append.*` | associativity, identity | 14 |
| `List/len.*` | length homomorphism | 10 |
| `List/rev.rev` | involution | 6 |
| `List/map.*`, `List/filter.*` | functor laws | 16 |

### §12 Finite sets (`Finset`)

| Block | Claim paths | Target count |
|-------|-------------|--------------|
| `Finset/∪.*`, `Finset/∩.*` | lattice laws | 24 |
| `Finset/card.*` | cardinality | 18 |
| `Finset/choose.*` | binomial coefficients | 20 |

### §13 Order theory (`Order`)

| Block | Claim paths | Target count |
|-------|-------------|--------------|
| `PartialOrder/<=.refl|trans|antisym` | axioms + lemmas | 15 |
| `Lattice/∧.comm`, `∨.comm` | lattice algebra | 20 |
| `WellFounded/induction` | well-founded recursion | 8 |

### §14 Basic combinatorics

| Block | Claim paths | Mathlib anchor | Target |
|-------|-------------|----------------|--------|
| `Comb/pigeonhole.finite` | `Fintype.exists_ne_map_eq` | 4 |
| `Comb/choose.sym` | `Nat.choose_symm` | 6 |
| `Comb/catalan.rec` | Catalan recurrence | 8 |
| `Comb/bell.rec` | Bell numbers | 6 |

**Phase 2 target:** ~350 theorems.

**Files:**
```
lib/verify/Pair.flow
lib/verify/List.flow
lib/verify/Finset.flow
lib/verify/Order.flow
lib/verify/Comb.flow
```

---

## Volume III — Euclidean geometry (Phase 3)

**Mathlib:** synthetic geometry via `Geometry.Euclidean` (later volumes); primary source is Euclid.

### Book I — Straight-line geometry ✅ scaffolded

| Prop | Claim coordinate | File | Status |
|------|------------------|------|--------|
| 1–48 | `«Geometry» «Euclid Book I» «Proposition N: …»` | `examples/verify/euclid/book-i/prop-*.flow` | ✅ 48 stubs |

**Next:** replace stubs with stepped proofs citing prior props by theorem number.

### Book II — Geometric algebra (areas)

| Prop | Topic | Target |
|------|-------|--------|
| 1–14 | rectangles, gnomons, `a+b` squares | 14 theorems |

**Files:** `examples/verify/euclid/book-ii/prop-*.flow`  
**Generator:** `tools/generate_euclid_book_ii.py` (mirror Book I)

### Book III — Circles

| Prop | Topic | Target |
|------|-------|--------|
| 1–37 | chords, tangents, power of a point | 37 theorems |

### Book IV — Polygons

| Prop | Topic | Target |
|------|-------|--------|
| 1–16 | inscribed/circumscribed | 16 theorems |

### Book V — Proportion

| Prop | Topic | Target |
|------|-------|--------|
| 1–25 | Eudoxus theory of proportion | 25 theorems |

### Book VI — Similar figures

| Prop | Topic | Target |
|------|-------|--------|
| 1–33 | similarity, area ratios | 33 theorems |

### Analytic geometry bridge (post-Euclid)

| § | Claim Path | Mathlib anchor | Target |
|---|------------|----------------|--------|
| AG.1 | `«Geometry» «affine space» «barycenter»` | `AffineSpace` | 8 |
| AG.2 | `«Geometry» «Euclidean» «angle»` | `InnerProductGeometry.angle` | 12 |
| AG.3 | `«Geometry» «distance» «triangle inequality»` | metric geometry | 6 |

**Phase 3 target:** 173 Euclid props + ~26 analytic bridge = **~199** (Book I done at scaffold level).

---

## Volume IV — Algebra (Phase 4)

**Mathlib:** `Algebra`, `GroupTheory`, `RingTheory`, `FieldTheory`

### §20 Group theory

| Block | Key facets | Target |
|-------|------------|--------|
| `Group/+.assoc`, `Group/1.left`, `Group/inv.left` | group axioms | 12 |
| `GroupHom/kernel.normal` | morphisms | 20 |
| `Subgroup/index` | Lagrange | 15 |
| `QuotientGroup/first-isomorphism` | isomorphism theorems | 18 |
| `GroupAction/orbit-stabilizer` | actions | 12 |
| `Sylow/*` | Sylow theorems | 10 |

**Files:** `lib/verify/Group.flow`, `lib/verify/GroupTheory/`

### §21 Ring theory

| Block | Key facets | Target |
|-------|------------|--------|
| `Ring/+.assoc`, `Ring/*.distrib` | ring axioms | 14 |
| `RingHom/kernel.ideal` | morphisms | 16 |
| `Ideal/prime.def`, `Ideal/maximal.def` | ideals | 20 |
| `Ideal/quotient.ring` | quotient rings | 12 |
| `Ideal/chinese-remainder` | CRT | 4 |

**Files:** `lib/verify/Ring.flow`, `lib/verify/RingTheory/`

### §22 Integral domains & divisibility

| Block | Target |
|-------|--------|
| `GCD/gcd`, `GCD/lcm`, `UFD/*`, `EuclideanDomain/*` | 40 |

### §23 Polynomials

| Block | Target |
|-------|--------|
| `Polynomial/eval`, `Polynomial/roots`, `Polynomial/eisenstein` | 50 |

### §24 Field theory

| Block | Target |
|-------|--------|
| `Field/char`, `Field/splitting`, `Galois/correspondence` | 45 |

### §25 Representation theory

| Block | Target |
|-------|--------|
| `Representation/character`, `Representation/orthogonality` | 20 |

**Phase 4 target:** ~800 theorems.

---

## Volume V — Linear algebra (Phase 5)

**Mathlib:** `LinearAlgebra`

### §30 Modules and vector spaces

| Block | Target |
|-------|--------|
| `Module/linear-map`, `Module/basis`, `Module/quotient` | 40 |

### §31 Matrices

| Block | Target |
|-------|--------|
| `Matrix/det`, `Matrix/inv`, `Matrix/toLin` | 35 |

### §32 Spectral theory

| Block | Target |
|-------|--------|
| `Eigenvalue/exists`, `Charpoly/cayley-hamilton` | 25 |

### §33 Bilinear & quadratic forms

| Block | Target |
|-------|--------|
| `BilinForm/symm`, `QuadraticForm/polar` | 20 |

### §34 Inner product spaces

| Block | Target |
|-------|--------|
| `InnerProduct/cauchy-schwarz`, `InnerProduct/gram-schmidt` | 30 |

**Phase 5 target:** ~600 theorems.  
**Files:** `lib/verify/LinearAlgebra/`

---

## Volume VI — Topology (Phase 6)

**Mathlib:** `Topology`

### §40 General topology

| Block | Mathlib anchor | Target |
|-------|----------------|--------|
| `TopologicalSpace/open.*` | opens, continuity | 40 |
| `Filter/Tendsto` | limits via filters | 30 |
| `Compact/*` | compactness | 35 |
| `Connected/*` | connectedness | 20 |
| `Separation/T2` | Hausdorff | 15 |

### §41 Uniform & metric spaces

| Block | Target |
|-------|--------|
| `UniformSpace/Cauchy`, `MetricSpace/complete` | 35 |
| `Metric/ball`, `Metric/hausdorff` | 25 |
| `Contraction/fixed-point` | Banach fixed point | 4 |

### §42 Topological algebra

| Block | Target |
|-------|--------|
| `TopologicalGroup/*`, `TopologicalRing/*` | 30 |

**Phase 6 (topology slice):** ~500 theorems.  
**Files:** `lib/verify/Topology/`

---

## Volume VII — Analysis (Phase 6–7)

**Mathlib:** `Analysis`, `MeasureTheory` (intro)

### §50 Normed & Banach spaces

| Block | Target |
|-------|--------|
| `NormedSpace/complete`, `Banach/open-mapping` | 40 |
| `HahnBanach/exists-extension` | 4 |

### §51 Hilbert spaces

| Block | Target |
|-------|--------|
| `InnerProductSpace/cauchy-schwarz`, `LaxMilgram/*` | 30 |

### §52 Calculus

| Block | Target | Status |
|-------|--------|--------|
| `Deriv/chain-rule` | 8 | ⬜ |
| `Deriv/mean-value` | 6 | ⬜ |
| `Taylor/remainder` | 8 | partial (Appendix) |
| `ContDiff/Ck` | 15 | ⬜ |
| `InverseFunction/local` | 6 | ⬜ |
| `ImplicitFunction/*` | 6 | ⬜ |

**Appendix today:** `sine-derivatives-at-zero`, `taylor-sin-maclaurin` → expand into §52.

### §53 Special functions

| Block | Target |
|-------|--------|
| `Real/exp`, `Real/log`, `Real/sin`, `Real/cos` | 40 |

### §54 Complex analysis

| Block | Target |
|-------|--------|
| `Complex/cauchy-integral`, `Complex/liouville`, `Complex/schwarz` | 35 |

### §55 Fourier analysis

| Block | Target |
|-------|--------|
| `Fourier/transform`, `Fourier/inversion` | 20 |

**Phase 6–7 (analysis slice):** ~700 theorems.  
**Files:** `lib/verify/Analysis/`, `examples/verify/analysis/`

---

## Volume VIII — Measure theory & probability (Phase 7)

**Mathlib:** `MeasureTheory`, `Probability`

### §60 Measure theory

| Block | Target |
|-------|--------|
| `MeasurableSpace/def`, `Measure/count`, `Measure/lebesgue` | 50 |
| `Bochner/integral`, `DominatedConvergence/*` | 40 |
| `Fubini/*`, `FundThmCalculus/*` | 20 |

### §61 Probability

| Block | Target |
|-------|--------|
| `Probability/independence`, `Probability/conditional` | 35 |
| `Probability/lln`, `Probability/clt` | 12 |
| `Martingale/optional-stopping` | 15 |

**Phase 7 target:** ~900 theorems (measure + probability).  
**Files:** `lib/verify/MeasureTheory/`, `lib/verify/Probability/`

---

## Volume IX — Number theory (Phase 8)

**Mathlib:** `NumberTheory`

### §70 Elementary

| Block | Target |
|-------|--------|
| `Nat/Prime.def`, `Nat/gcd`, `Nat/prime-unique-factorization` | 30 |
| `Legendre/quadratic-reciprocity` | 4 |
| `Nat/sum-two-squares`, `Nat/sum-four-squares` | 8 |

### §71 Algebraic number theory

| Block | Target |
|-------|--------|
| `NumberField/class-number`, `NumberField/dirichlet-units` | 15 |

### §72 p-adic & transcendence

| Block | Target |
|-------|--------|
| `Padic/hensels-lemma`, `Transcendental/liouville` | 12 |

**Phase 8 target:** ~700 theorems.  
**Files:** `lib/verify/NumberTheory/`

---

## Volume X — Combinatorics (Phase 2+)

**Mathlib:** `Combinatorics`

### §80 Enumerative & graph theory

| Block | Target |
|-------|--------|
| `SimpleGraph/degree-sum`, `SimpleGraph/matching` | 30 |
| `Combinatorics/hall-marriage` | 4 |
| `Combinatorics/turan`, `Combinatorics/ramsey` | 20 |

### §81 Additive combinatorics

| Block | Target |
|-------|--------|
| `Additive/roth-3ap`, `Additive/pluennecke-ruzsa` | 25 |

**Extended target:** ~400 theorems beyond §14.  
**Files:** `lib/verify/Combinatorics/`

---

## Volume XI — Geometry advanced (Phase 9)

**Mathlib:** `Geometry.Manifold`, `AlgebraicGeometry`

### §90 Manifolds

| Block | Target |
|-------|--------|
| `Manifold/smooth`, `Manifold/tangent-bundle` | 40 |
| `LieGroup/def`, `IntegralCurve/exists` | 30 |

### §91 Riemannian geometry

| Block | Target |
|-------|--------|
| `Riemannian/metric`, `Geodesic/exists` | 25 |

### §92 Algebraic geometry

| Block | Target |
|-------|--------|
| `PrimeSpectrum/zariski`, `Scheme/def`, `Nullstellensatz` | 35 |

**Phase 9 target:** ~1,000 theorems.  
**Files:** `lib/verify/Geometry/`

---

## Volume XII — Category theory & homological algebra (Phase 10)

**Mathlib:** `CategoryTheory`

### §100 Category theory core

| Block | Target |
|-------|--------|
| `Category/functor`, `Category/natural-transformation` | 30 |
| `Category/adjunction`, `Category/limits` | 40 |
| `Category/abelian`, `Category/yoneda` | 25 |

### §101 Homological algebra

| Block | Target |
|-------|--------|
| `HomologicalComplex/homology` | 15 |

**Phase 10 target:** ~800 theorems.  
**Files:** `lib/verify/CategoryTheory/`

---

## Volume XIII — Set theory, logic, computability (Phase 11–12)

**Mathlib:** `SetTheory`, `ModelTheory`, `Computability`, `Dynamics`

### §110 Set theory

| Block | Target |
|-------|--------|
| `Ordinal/basic`, `Cardinal/aleph`, `ZFC/model` | 50 |

### §111 Model theory

| Block | Target |
|-------|--------|
| `FirstOrder/compactness`, `FirstOrder/lowenheim-skolem` | 20 |

### §112 Computability

| Block | Target |
|-------|--------|
| `Computable/def`, `Halting/undecidable`, `Primrec/*` | 30 |

### §113 Dynamics

| Block | Target |
|-------|--------|
| `Dynamics/fixed-point`, `Dynamics/omega-limit` | 15 |

**Phase 11–12 target:** ~700 theorems.  
**Files:** `lib/verify/SetTheory/`, `lib/verify/Computability/`, `lib/verify/Dynamics/`

---

## Parallel track — Verification engine (not in book)

| Component | Purpose | Mathlib analogue |
|-----------|---------|------------------|
| `flow verify` | SMT + induction checker | `tactic` + `simp` |
| `flow know` | Claim Path registry | `docs` + search |
| Lean bridge | import Mathlib as oracle | `Mathlib` itself |
| `proof_document.py` | Book PDF | N/A |

---

## File tree (target layout)

```
lib/verify/
  Eq.flow  Bool.flow  Prop.flow
  Nat-core.flow  Nat.flow  Nat-mul.flow  Nat-order.flow
  Int.flow  Rat.flow  Real.flow  Complex.flow
  Pair.flow  List.flow  Finset.flow  Order.flow  Comb.flow
  Group/  Ring/  RingTheory/  FieldTheory/
  LinearAlgebra/
  Topology/
  Analysis/
  MeasureTheory/  Probability/
  NumberTheory/
  Combinatorics/
  Geometry/
  CategoryTheory/
  SetTheory/  ModelTheory/
  Computability/  Dynamics/

examples/verify/
  math/derived/          # stepped proofs importing lib/verify
  euclid/book-i/         # ✅ 48 props
  euclid/book-ii/ … vi/  # generators + props
  analysis/              # calculus, special functions
  geometry/              # legacy + analytic bridge

tools/
  generate_euclid_book_i.py   # ✅
  generate_euclid_book_ii.py  # planned
  generate_book_manifest.py   # planned: BOOK_PARTS from YAML

docs/language/
  mathlib-equivalence-toc.md  # this file
  math-proof-book.md          # book contract
```

---

## Mathlib top-level module map

Every `Mathlib/*` root directory maps to a Flow volume:

| Mathlib directory | Flow volume | Phase |
|-------------------|-------------|-------|
| `Algebra` | IV §20–25 | 4 |
| `AlgebraicGeometry` | XI §92 | 9 |
| `AlgebraicTopology` | XII (future) | 10+ |
| `Analysis` | VII §50–55 | 6–7 |
| `CategoryTheory` | XII §100–101 | 10 |
| `Combinatorics` | II §14, X §80–81 | 2+ |
| `Computability` | XIII §112 | 12 |
| `Data` | II §10–12 | 2 |
| `Dynamics` | XIII §113 | 12 |
| `FieldTheory` | IV §24 | 4 |
| `Geometry` | III, XI §90–91 | 3, 9 |
| `GroupTheory` | IV §20 | 4 |
| `InformationTheory` | (future) | — |
| `LinearAlgebra` | V §30–34 | 5 |
| `Logic` | I §1 | 1 |
| `MeasureTheory` | VIII §60 | 7 |
| `ModelTheory` | XIII §111 | 11 |
| `NumberTheory` | IX §70–72 | 8 |
| `Order` | II §13 | 2 |
| `Probability` | VIII §61 | 7 |
| `RepresentationTheory` | IV §25 | 4 |
| `RingTheory` | IV §21–22 | 4 |
| `SetTheory` | XIII §110 | 11 |
| `Topology` | VI §40–42 | 6 |

---

## Immediate next steps (Phase 1 sprint)

1. **Complete §1–§5** — `Eq.flow`, `Bool.flow`, `Nat-mul.flow`, `Nat-order.flow` with stepped proofs.
2. **Deepen Euclid I** — replace assume/therefore stubs in props 1–10 first (construction + SAS chain).
3. **Regenerate book** — `./flow doc bundle` after each § lands; keep continuous numbering.
4. **Add `tools/generate_book_manifest.py`** — drive `BOOK_PARTS` from `docs/language/mathlib-toc.yaml` (machine-readable slice of this TOC).
5. **CI** — `flow know --lint-duplicates` + theorem count regression test per phase.

---

## Success criteria (Mathlib equivalence)

| Criterion | Undergraduate (Phases 1–3) | Graduate core (Phases 4–8) | Full parity |
|-----------|---------------------------|---------------------------|-------------|
| Theorem count | ~900 | ~7,600 | ~150,000 |
| Stepped proof coverage | 80% | 60% | 40% (rest certified via Lean bridge) |
| `assume` cites Claim Path or theorem # | 100% | 100% | 100% |
| Duplicate fingerprints | 0 | 0 | 0 |
| Book PDF | Single continuous volume | Multi-volume | Searchable corpus |
| Mathlib topic coverage | `undergrad.html` | `overview.yaml` core | Full index |

---

## One sentence

**We build Mathlib equivalence bottom-up: finish the Peano spine and stepped Euclid I proofs first (Phase 1), then data/order, then the full Euclid corpus, then algebra → analysis → everything else — one Claim Path, one theorem number, one proof book.**