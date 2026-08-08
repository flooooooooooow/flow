# Tiny Pointers (arXiv:2111.12800) in Flow

A working, self-verifying Flow implementation of **Tiny Pointers** — Bender,
Conway, Farach-Colton, Kuszmaul & Tagliavini — lives in
[`examples/systems/tiny_pointers.flow`](../../examples/systems/tiny_pointers.flow).

> [!important] The whole point
> A dereference table lets n keys each own one slot in a shared value array. A
> naive implementation hands each user a `log n`-bit pointer. Because the key
> *and* the pointer are both known at dereference time, the pointer only needs
> to encode the slot within a hash-derived bucket — **`o(log n)` bits total**.

The example rebuilds every construction in the paper's Sections 3–6 from
scratch in Flow and verifies each one empirically:

| Theorem | Paper result (exact section) | Flow phase | Status |
|---------|------------------------------|------------|--------|
| **1** | Fixed-size tiny pointers: `Θ(log log log n + log k)` bits at load `1 − 1/k` (§3: *Upper Bound for Fixed-Size Pointers*) | Phases 1–4 | ✅ 6 bits vs 16 |
| **2** | Variable-size tiny pointers: `Θ(log k)` expected bits (`O(1 + log δ⁻¹)`), doubly-exponential tail (§4: *Upper Bounds for Variable-Sized Pointers*) | Phases 5–6 | ✅ ~3 bits, tail confirmed |
| **3–5** | Lower bounds: `Ω(log log log n + log k)` fixed / `Ω(log k)` variable, via the fullest-bin floor `Ω((log log m)/2^s)` (§5: *Lower Bounds*) | Phase 13 | ✅ floor holds at every budget; < 6 bits collides |
| **6** | Relaxed retrieval: tiny retrievers of expected size O(1) — `nv + O(n log⁽ʳ⁾ n)` bits total for n v-bit values, beating the `Ω(log log n)` lower bound; the tradeoff: **O(r) insert/delete vs `O(n log⁽ʳ⁾ n)` space** (§6.2: *Overcoming the Ω(log log n)-Bit Lower Bound for Data Retrieval*) | Phases 7–8, 8b | ✅ mean 3.04 bits; `H` = `nv + O(n)`; retriever term shrinks 15 → 4 → 2 → 1 bits/key for r = 1..4 |
| **7** | Succinct rotation-based BSTs: `nk + O(n log⁽ʳ⁾ n)` bits, rotations stay constant-time (§6.3: *Succinct Binary Search Trees*) | Phases 9–10 | ✅ ~3 bits/child pointer |
| **8** | Stable dictionaries: values never move, `O(log v)` extra bits/value, `1 + o(1)` space overhead (§6.4: *Space-Efficient Stable Dictionaries*) | Phases 3–4 | ✅ rehash-proof |
| **9** | Variable-size value dictionaries: `O(m log⁽ʳ⁾ m) + Σᵢ(vᵢ + O(log vᵢ))` bits (Eq. 4) for arbitrary-length values (§6.5: *Space-Efficient Dictionaries with Variable-Size Values*) | Phase 11 | ✅ 19.3 bits/value vs 64 |
| **9** (deamortized) | Theorem-9's zone-aggregated resizing: class storage grows/shrinks incrementally — no single op copies O(m) values (§6.1: *Some General-Purpose Techniques*) | Phase 14 | ✅ worst op 143,363 → 81 work units |
| **9** (r-levels) | Theorem-9's r-levels-of-indirection chain: values to 256 bits behind a 5-bit p₁ = O(log k); the base pointer stays 8 bits — constant in value size and in r (§6.5; caveats in the body) | Phase 15 | ✅ 84.97% saved (r=2); r=3 lifts the cap to 2^32 bits, pointers 8 → 6 → 5 |
| **9** (keys chain) | Theorem-9's remark applied to the KEY array with the same chain: 128/256-bit keys behind a 5-bit p₁ in an 8-bit base slot — the base pointer stays 8 bits for every key size (§6.5) | Phase 12 | ✅ 82.5% saved vs uniform 256+64 (56.3% vs 64+64) |
| **10** | Optimal internal-memory stash: `O(m log ε⁻¹)` internal bits locate every key/value of an external array; constant-time RAM ops with no IOs, stable (page-table-like) (§6.6: *An Optimal Internal-Memory Stash*) | Phase 16 | ✅ 7.76 bits/key vs 15 |

**Abstract-claim coverage.** The paper's abstract promises two pointer
results and five applications; each has a measured row above:

| Abstract claim | Row |
|---|---|
| Fixed-size pointers of `Θ(log log log n + log k)` bits | Theorem 1 (Phases 1–4) |
| Variable-size pointers of `Θ(log k)` expected bits | Theorem 2 (Phases 5–6) |
| `nv + O(n log⁽ʳ⁾ n)`-bit store with an O(1)-expected pointer per key, O(r) insert/delete | Theorem 6 (Phases 7–8, 8b) |
| Succinct BSTs, rotations included | Theorem 7 (Phases 9–10) |
| Stable fixed-capacity dictionaries, `1 + o(1)` overhead | Theorem 8 (Phases 3–4) |
| Arbitrary-size values at `log⁽ʳ⁾ n + O(log j)` bits per j-bit value | Theorem 9 (Phases 11/12/14/15) |
| `O(n log ε⁻¹)`-bit internal-memory stash, no IOs | Theorem 10 (Phase 16) |

(Theorems 3–5 are *lower bounds* / intermediate steps, not constructions —
e.g. Theorem 3 proves `Ω(log log log n + log k)` is optimal for fixed-size
tiny pointers. The demo implements the matching constructions.)

**Run it** (full language host; every allocation, dereference and stability
check is self-verified, exit code 0 = PASS, 1 = FAIL):

```bash
FLOW_HOST=python ./flow run examples/systems/tiny_pointers.flow
```

The adversarial keys, churn phases and rotation storm are deterministic per
PRNG seed; the file passes across all tested seeds. Each run also reports its
own per-phase wall-clock timings — see [Benchmarks](#benchmarks-wall-clock).

---

## The core abstraction

A **dereference table** supports `Allocate(k) → p`, `Dereference(k, p) → s`
and `Free(k, p)`, where `s ∈ [0, m)` is a slot **unique** to `k`. The pointer
`p` is tiny because it only encodes *which slot inside the bucket that `k`
hashes to* — the key supplies the bucket, the pointer supplies the position.

- `tp_allocate` / `tp_dereference` / `tp_free` — fixed-size table (§3)
- `vtp_allocate` / `vtp_dereference` / `vtp_free` — variable-size table (§4)
- `hash_u32(x, salt)` — Murmur-style finalizer, salted for independence

---

## Theorem 1 — fixed-size tiny pointers (§3, Phases 1–4)

**Paper.** With load factor `1 − δ`, there is a two-level construction with
pointers of size `O(log log log n + log δ⁻¹)` bits: a *primary* load-balancing
table (hash → bucket of `b` slots, pointer = slot index) that overflows on a
~`δ²` fraction of allocations, plus a sparse *secondary* power-of-two-choices
table (hash to **two** buckets, pointer = 1 choice bit + slot) that absorbs the
overflow w.h.p.

**Parameter math** (concrete instance in the demo):

```
n      = 65536              log₂ n = 16 (raw pointer bits)
δ      = 1/4                load factor 1 − δ = 0.75
primary   = (1 − δ/2)·n = 57344 slots = 1792 buckets × b=32
secondary = δ·n/2       =  8192 slots = 1024 buckets × b=8
pointer   = 1 table bit + 5 slot bits = 6 bits
theory    = Θ(log log log 65536 + log 4) = Θ(2 + 2) = 4 bits → achieved 6
```

**Empirical results (Phase 1–4):**

| Measurement | Result | Theory |
|-------------|--------|--------|
| Overflow to secondary (49,152 inserts) | **1103** | ≤ δ²n = 4096 w.h.p. ✓ |
| Max primary bucket load | 32 (full) | — |
| Max secondary bucket load | 3 / 8 | O(log log n) ✓ |
| Verification (bulk + 30 000-op churn) | 0 errors | — |
| Pinned values after 30 000 more ops | positions unchanged | Theorem 8 ✓ |

---

## Theorem 2 — variable-size tiny pointers (§4, Phases 5–6)

**Paper (Prop. 1).** Dropping the fixed-size requirement removes the
`log log log n` term entirely: pointers have **`O(1 + log δ⁻¹)` expected bits**
with a *doubly-exponential* tail, `Pr[size ≥ ℓ] ≤ 2^(−2^Ω(ℓ))`.

**Construction.** `n/log n` containers, each a mini-table of capacity `s` with
`log₂ s` levels; level `i` is a load-balancing table of `sᵢ = s/2ⁱ` buckets
(`b` slots each) plus an overflow array of `sᵢ` slots. The deterministic
invariant `Lᵢ ≤ sᵢ` (values in levels ≥ i) makes overflow-fill provably
unreachable. Allocate descends levels: on bucket-full, recurse to `i+1` only
while `Lᵢ₊₁ < sᵢ₊₁`, else place in level `i`'s overflow array.

**Parameter math:**

```
containers = n/log n = 4096      s = 32 = 2·log₂ n      b = 2
levels     = log₂ s = 5          sᵢ = 32, 16, 8, 4, 2   (186 slots / container)
size(table slot @i)   = Elias-γ(i+1) + 1 + ⌈log₂b⌉     = O(log i) bits
size(overflow slot @i)= Elias-γ(5−i) + 1 + ⌈log₂sᵢ⌉    = O(log sᵢ) bits
```

**Empirical results (Phases 5–6):**

- **Natural load** (49,152 uniform keys): `L0:48177  L1:975` → **~98% get a
  3-bit pointer**; the tail is invisible at this scale (that is the point).
- **Doubly-exponential tail** (measured over 49,163 live pointers, checked
  against the theory bound at every threshold):

  | ℓ | empirical Pr[size ≥ ℓ] | theory bound | |
  |---|------------------------|--------------|---|
  | 5 | 0.020198 | 1.753906 | ✓ |
  | 7 | 0.000244 | 0.503906 | ✓ |
  | 9 | 0.000122 | 0.066406 | ✓ |
  | 11| 0.000041 | 0.003906 | ✓ |

- **Adversarial cascade** (20 keys that hash to the *same* container and, nested,
  the same level-0/1/2/3 buckets, found by offline bit-exact search): drills to
  levels `L0:4 L1:8 L2:4 L3:4`, engages overflow arrays `O0:2 O1:4 O2:2` — and
  **still never exceeds an 11-bit pointer** (raw pointer: 16).

---

## Theorem 6 — relaxed retrieval, tiny retrievers (§6.2, Phases 7–8)

**Paper.** Classic dynamic retrieval provably costs `Ω(log log n)` metadata
bits per value (even for `v = 1`). Relax the contract: `Insert(x, y)` returns
an **O(1)-expected hint r** the user keeps, and `Query(x, r)` / `Delete(x, r)`
present both. The hint is just a Theorem-2 tiny pointer; `Dereference(x, r)`
names a slot unique to `x`, and the value lives in hash table `H` keyed on
that slot. Because `H`'s keys come from the tiny universe `[2n]`,
`log C(2n,n) = O(n)` bits (Stirling) — **`H` costs `nv + O(n)` total**.

Key demo detail: the dereference table's **store is never read** ("we need not
even allocate space for it") — only the uniqueness of the slot matters.

**Empirical results (Phases 7–8):**

| Measurement | Result |
|-------------|--------|
| Hint sizes (49,152 keys) | **98.02% at 3 bits · mean 3.04 bits · worst 5** |
| Classic lower bound at n = 2^16 | Ω(log log n) = **4 bits/value → beaten** |
| 20 000-op churn with tombstoned deletes | 0 errors, 0 slot dups |
| Full `H` rebuild (new seed, compacts tombstones) | 49,183 entries, verify 0 — **all hints survived** |

`H` is pure auxiliary metadata: it may rehash or move freely, because hints
name **slots in the dereference table**, not cells in `H`.

### Phase 8b — the O(r)-time / `nv + O(n log⁽ʳ⁾ n)`-space tradeoff

The abstract promises the curve: with **r levels of indirection**,
insertions/deletions take **O(r) time** while total space is
`nv + O(n log⁽ʳ⁾ n)` bits (constant-time ops give, e.g., `nv + O(n log⁵ n)`;
O(logⁱ n)-time ops give `nv + O(n)`). Phase 8b sweeps `r = 1..4` on a
relaxed-retrieval store whose dereference table is an **r-level chain of
keyed buckets**, and measures both sides of the curve.

The retriever is the **level-0 slot code** — the base pointer of the chain —
and the level-0 bucket capacity is `2^⌈log⁽ʳ⁾ n⌉`, so the retriever costs
`w₀ = ⌈log⁽ʳ⁾ n⌉` bits (the `O(n log⁽ʳ⁾ n)` term). At `n = 2^14` (universe
`2n = 2^15`) the measured widths are **15 → 4 → 2 → 1 bits/key** for
`r = 1..4`: `r = 1` is the paper's `(1 + log n)`-bit slot number (the
spendthrift end), `r = 4` is `log⁴ n`. Deeper levels hold exponentially
larger buckets (`2^w₀, 2^2w₀, …`), so the chain telescopes to the full
`2^(1+log n)` value universe. `Insert`/`Delete` descend level by level until
a bucket has room: the **worst case walks all r levels** (measured depth
1, 2, 3, 4), while the expected case stays O(1) — natural churn shows mean
descent `0.00 / 0.00 / 0.05 / 0.14` and flat per-op time.

| r | `w₀ = ⌈log⁽ʳ⁾ n⌉` | retriever metadata `n·w₀` | `nv + n·w₀` total | worst-case descent |
|---|---|---|---|---|
| 1 | 15 bits | 245,760 bits | 507,904 bits | 1 level |
| 2 | 4 bits | 65,536 bits | 327,680 bits | 2 levels |
| 3 | 2 bits | 32,768 bits | 294,912 bits | 3 levels |
| 4 | 1 bit | 16,384 bits | 278,528 bits | 4 levels |

All four runs verify 0 errors; the adversarial single-bucket cascade (64
keys that collide at every level) descends all r levels with verify 0, and
its total insert time rises with r (the r = 4 cascade ≈ 1.8× the r = 1
cascade in the host run; the descent depth 1 → 4 levels is the direct O(r)
evidence). The `O(n log⁽ʳ⁾ n)` term shrinks `15n → 4n → 2n → 1n` bits as r
grows, the `nv` payload untouched — exactly the abstract's curve. (The
measured widths are the bucket-capacity constants of the geometry, like
Phase 15's; the descent counts and wall-clock are measured.)

---

## Theorem 7 — succinct rotation-based BSTs (§6.3, Phases 9–10)

**Paper.** There are at most `4ⁿ` ordered binary trees on `n` nodes, so a
tree's pointer structure fits in `O(n)` bits — but classic succinct trees
cannot do **rotations**, which AVL / red-black / splay trees live on.
Theorem 7: store each child pointer as a tiny retriever — `r₁` for the left
child keyed on `x◦0`, `r₂` for the right child keyed on `x◦1` — with the
dereference table's store as the node array. Navigating parent → child is one
O(1) query; a **rotation rewrites only 2–3 edge slots**, so nodes never move
and retrievers never change. The child-pointer structure is `na + nb + O(n)`
bits (distinct keys give `na = Ω(n log n)`, so the tree is succinct); the
paper's full theorem carries an auxiliary term `O(n log^(r) n)` where `r` is
the modification-time parameter — the demo measures the O(n) pointer part
(2n retrievers, ~3 bits each) directly.

**Empirical results (Phases 9–10):**

| Measurement | Result |
|-------------|--------|
| 16,384 **sorted** inserts (worst case) | height **15** (AVL bound ≈ 29), 16,369 rotations |
| In-order traversal | 16,384 nodes, 0 out-of-order pairs |
| Child-pointer size | **3.018 bits/node avg → 98,906 bits vs 524,288** (2n log n) for a raw BST |
| Avg search depth (2,048 random keys) | **11.998** (log₂ n = 14), 0 value mismatches |
| Rotation storm (20,000 attempts) | 10,073 real rotations; in-order preserved; pointer integrity **0** |

---

## Theorem 8 — stable dictionaries (§6.4, Phases 3–4)

**Paper.** Replace a dictionary's value array with an array of tiny pointers
into a dereference table holding the values. Values **never move** after
insert — even across a full map rehash/reallocation — at `O(log v)` extra
bits per value.

**Empirical results (Phase 4):** 8 dictionary entries keyed by tiny pointer;
lookups all correct **before and after** a full rebuild that reallocated the
map with a new hash seed and repositioned every entry — the tiny pointers
were copied verbatim and every value stayed put.

---

## The r-levels-of-indirection chain — Phase 15 (§6.5)

The size-class table caps values at O(1) machine words because its slots are
sized to the value: a 200-bit value would need a 256-bit **base** slot, and
the base class tag would have to grow with the max value size. The paper's
fix (Theorem 9's proof) stores every value "at the end of a linked list of
length O(1)":

```
value k bits ← p₁ of O(log k) bits ← p₂ of O(log log k) bits ← … ← base
pointer of O(log⁽ʳ⁾ n) bits
```

where each pointer is exponentially larger than the one it points at. Phase 15
implements the chain with r = 2 levels, lifting the v ≤ 64 cap to 256 bits:

```
base pointer = 1 flag + 3 class + 1 choice + 3 slot = 8 bits (for v = 1..256)
p₁           = 1 arena-class + 1 choice + 3 slot     = 5 bits = O(log 256)
holder slot  = 8-bit base slot (class 3) holding p₁
value        = 128 or 256 bits, in the level-1 arena (compact, keyed on the key)
```

Values ≤ 64 bits store directly (Phase-11 classes); values of 65–256 bits go
through the chain. The flag bit (the paper's "points at a pointer vs a value"
metadata) marks the chained pointers, and the 5-bit p₁ (O(log k)) lives in an
8-bit base slot — so the **base pointer stays 8 bits for every value size**, the
paper's "base pointer … is O(log⁽ʳ⁾ n) bits" with the O(log k) cost paid only in
the exponentially-larger next level.

**Empirical results (Phase 15, n = 2^16, all runs exit 0):**

| Measurement | Result |
|---|---|
| Load 12,288 keys + 4,000-op churn → 12,352 live (11,116 ≤ 64-bit, 860 × 128-bit, 376 × 256-bit) | 0 verify errors · 0 arena / 0 base invariant violations |
| Churn (4,000 ops incl. big-value inserts/deletes) | verify 0 — p₁ holder + arena slot freed/reallocated atomically per key |
| r-levels space | **475,366 bits = 38.5 bits/value** vs uniform 256-bit 3,162,112 bits → **84.97% saved** |
| Single-level size-classed (same data) | 459,298 bits → 85.47% saved — the chain costs **13 bits/value on big values only** (8-bit holder + 5-bit p₁ = the paper's O(log v) overhead in Eq. 4) |
| Base pointer size | 8 bits for v = 1 and v = 256 alike — value-size-independent |

### r = 3 — the O(log log k) middle pointer p₂ (values up to 2^32 bits)

The r=2 chain caps values at 256 bits because its arena slots are four words.
The paper's next level inserts the **O(log log k)-bit p₂** between the base and
p₁ — "value k bits ← p₁ of O(log k) bits ← p₂ of O(log log k) bits ← base of
O(log⁽³⁾ n) bits" — and the value store becomes a *word pool* that an arena
slot points at, so a value can be **any width**:

```text
base pointer = 8 bits, UNCHANGED (flag + class + choice + slot) — the class-3
               slot now holds p₂ instead of p₁
p₂           = 6 bits = class(1) + choice(1) + slot(4) — into the level-2 table
p₁           = 5 bits = class(1) + choice(1) + slot(3) — into the level-1 arena
value        = up to 2^32 bits in the design (the demo stores up to 2^18), the
               words live in a shared pool behind the 5-bit p₁
```

Measured pointer hierarchy: **8 → 6 → 5 bits** (base → p₂ → p₁) — every
pointer width is CONSTANT as v grows: the base never changes even for a 2^32-bit
value (the paper's base-pointer independence), and only the value's word count
grows. The chain's per-big-value cost is 19 bits (8-bit holder + 6-bit p₂ +
5-bit p₁) vs r=2's 13 — the extra 6 bits buy the 256 → 2^32 cap lift.

One honest caveat: the measured widths are **geometry constants** (class +
choice + slot bits of each table), not the paper's exponentially-sized
hierarchy — the demo captures the *base-pointer independence* property, not
the asymptotic sizing. Three consequences worth stating: (1) the paper's p₁ =
O(log k) is the LARGEST pointer (it grows with the value's bit-length k) and
the base O(log⁽ʳ⁾ n) the smallest — "each subsequent pointer is exponentially
larger" — while the demo's 8 → 6 → 5 shrinks in the *opposite* direction and
never moves with v; (2) the paper's base itself shrinks with r (log⁽³⁾ n <
log² n), while the demo's stays 8 bits at r = 2 and r = 3 — the Phase 8b
retriever sweep shows that log⁽ʳ⁾ n shrinkage on the Theorem-6 side instead;
and (3) the demo stores values past the paper's O(1)-word convenience cap
(2^32-bit design, leaning on the paper's "works for even larger values
without modification" remark) and its chain tables are fixed-capacity (the
§6.5 proof is mostly the zone-aggregated resizing machinery). In the paper's
construction p₁ = O(log k) would grow with the value size; here p₁ stays 5
bits because the level-1 arena is keyed like every other tiny-pointer table,
so v never appears in any pointer.

**Empirical results (r=3 extension, n = 2^16, all runs exit 0):**

| Measurement | Result |
|---|---|
| Load 12,288 keys (≈1,230 chained values of 65..2^18 bits) | 0 verify errors · 0 invariant violations |
| Biggest stored values | 63 values > 2^16 bits, up to 2^18 bits (32 KB), verified word-by-word through base → p₂ → p₁ → pool |
| 3,000-op churn (deletes + fresh big values) | verify 0 — all three levels freed/reallocated atomically per key |
| r=3 chain space (12,650 live) | 21,600,985 bits (payload-dominated) — base pointer 8 bits/key constant, chain overhead 19 bits per big value vs 13 for r=2 |
| vs uniform-sized-to-max | 3,260,322,450 bits → **99.34% saved** |

The honest trade: the r=3 chain costs 6 bits more per big value than r=2 — but
the value cap lifts from 256 bits to 2^32 bits and the base pointer stays 8
bits for every value size (a uniform store sized to a 32 KB value would pay
262,144 bits for every key).

---

## Theorem 10 — the optimal internal-memory stash (§6.6, Phase 16)

The paper's final application revisits the oldest problem in external-memory
data structures: a small *internal* stash X that tells you where each
key/value pair of a large *external* structure resides, so queries cost a
single access to external memory. The classic result (Gonnet–Larson) is a
**stable** stash of `O(n log ε⁻¹)` bits with *expected-time* `Θ(ε⁻¹)` ops and
guarantees only for *random* insertion/deletion sequences. Theorem 10: tiny
pointers + the adaptive filter of Bender et al. give a stable stash of
`O(m log ε⁻¹)` bits with **constant-time** RAM ops for **arbitrary**
insert/delete/query sequences — and page-table stability, because positions
are permanent once an element is placed.

**Construction (Phase 16).** External memory is a dereference table with load
factor `1 − ε` (ε = 3/4): `4096` buckets × `8` slots = `32768 = 4m` slots.
Each key's bucket is **implicit** — a pure two-choice hash of the key — so
the stash entry only stores the intra-bucket address:

```text
external    = 4096 buckets × 8 slots = 4m slots    load 1/4 (1 − ε, ε = 3/4)
tiny pointer = 1 choice bit + 3 slot bits = 4 bits = Θ(log ε⁻¹)
naive stash  = m · log₂(4m) = 15 bits/key (a full address per key)
stash bins   = 2048 quotient bins (avg 4 keys/bin); the bin index IS the
               quotient — stored nowhere, the filter's implicit-quotient trick
fingerprint  = prefix-free, grows only to separate bin-mates — the paper's
               adaptivity bits, O(m) total (Bender et al.'s adaptive filter)
paper bound  = O(m log ε⁻¹) = O(m) bits — never grows with the external size
theory       = Θ(log ε⁻¹) ≈ 2 bits (b = 1/(1−ε) = 4) → achieved 4 with b = 8
               two-choice slack (1 choice + 3 slot)
```

`Query(k)`: recompute the quotient bin, scan the bin for the *unique* entry
whose fingerprint is a prefix of `h(k)` (the prefix-free invariant allows at
most one match), then read external memory **exactly once**. Inserts/deletes
are O(1) expected RAM; deleting only frees a slot, so no element ever moves
(stability — the page-table criterion).

**Empirical results (Phase 16, n = 2^16, all runs exit 0):**

| Measurement | Result |
|---|---|
| Load 8,192 keys into the external array | 0 verify errors · 0 insert failures · 0 invariant violations |
| Query storm (16,384 random queries) | **16,384 external reads — exactly one per query**, 0 errors |
| 6,000-op churn (55/45 insert/delete, periodic re-verify) | verify 0 · 0 insert failures · 0 invariant violations |
| Stash space (8,828 live) | **68,477 bits = 7.76 bits/key** (4-bit pointer + ≈3.8 adaptivity) vs naive 132,420 bits = 15 bits/key → **48.3% saved** |
| Pointer size vs external size | 4 bits by construction — the pointer encodes only choice+slot, never the bucket index (the bench runs the same 4-bit pointer at external sizes 2^13..2^15 slots while the naive pointer width grows 13 → 15) |

The 4 bits/key pointer is the paper's `m · Θ(log ε⁻¹)` baseline; the ≈3.8
bits/key of prefix-free adaptivity is the filter's O(m)-total adaptivity
bits. Both are constant as the external array grows — the stash is `O(m)`
bits where a naive full-address stash is `O(m log m)`.

---

## Benchmarks (wall-clock)

The demo is parameterized by n — every table geometry, load and op count is a
constant proportional to n — so the same source builds at any size. The table
below re-derives the constants at `n = 2^14, 2^15, 2^16`, compiles each
variant to a **native binary** (`FLOW_HOST=python FLOW_CFLAGS=-O2 ./flow
compile`), and runs that binary directly: the timings are the program's own
`CLOCK_MONOTONIC` report, best of 3 runs, every run exit 0 (PASS). Reproduce
with `scripts/bench_tiny_pointers.sh`.

| Phase | n = 2^14 | n = 2^15 | n = 2^16 | scaling |
|---|---|---|---|---|
| 1 bulk load (0.75·n keys, two-level table) | 0.23 ms | 0.45 ms | 0.93 ms | linear — ≈ 18 ns/key |
| 2 dynamic churn (churn ops ∝ n) | 0.17 ms | 0.53 ms | 1.77 ms | super-linear — 20 → 60 ns/op (periodic 2n-registry verify) |
| 3 stability churn (churn ops ∝ n, 8 pinned) | 0.12 ms | 0.24 ms | 0.48 ms | linear — no periodic verify |
| 4 stable dict (8 entries + full rehash) | 0.14 ms | 0.16 ms | 0.15 ms | **flat — constant work** |
| 5 natural load (0.75·n keys, container table) | 0.33 ms | 0.50 ms | 0.86 ms | linear — ≈ 17 ns/key at 2^16 |
| 6 adversarial cascade + tail check | 0.09 ms | 0.16 ms | 0.28 ms | ≈ linear (tail check scans the registry) |
| 7 retrieval load (0.75·n hints) | 0.48 ms | 0.86 ms | 1.56 ms | linear — ≈ 32 ns/hint at 2^16 |
| 8 churn + H rebuild (churn ops ∝ n) | 0.56 ms | 1.43 ms | 3.82 ms | super-linear (verify + full H rebuild scale with n) |
| 8b r-tradeoff (r = 1..4 sweep: 4 loads + 4 churns + 4 cascades, §6.2) | 1.02 ms | 2.53 ms | 5.32 ms | near-linear — ≈ 0.05 µs/op at 2^16; per-op flat across r (O(1) expected) |
| 9 AVL build (n/4 sorted keys) | 1.65 ms | 3.27 ms | 6.20 ms | linear — ≈ 0.38 µs/insert, rotations included |
| 10 rotation storm (attempts ∝ n) | 1.20 ms | 2.74 ms | 6.83 ms | linear — ≈ 0.34 µs/attempt |
| 11 variable-value dict (0.75·n keys, skewed sizes) | 0.90 ms | 1.91 ms | 4.63 ms | linear — ≈ 94 ns/value |
| 12 variable-key+value dict (0.75·n pairs, skewed both; keys to 256 bits via the Phase-15 chain) | 2.32 ms | 4.27 ms | 9.37 ms | linear — ≈ 191 ns/pair (two tables, key arena, two verifies) |
| 13 lower bounds (Thm 3–5: m·2^s probes + collision masks) | 2.30 ms | 4.63 ms | 10.28 ms | linear — the s-sweep probes scale as m·Σ2^s |
| 14 deamortized resize (naive + deamortized workloads, §6.1) | 3.88 ms | 8.97 ms | 19.86 ms | linear — two full workloads; worst-op 143,363 → 81 units |
| 15 r-levels chain + r=3 extension (values to 2^18 bits through base → p₂ → p₁, §6.5) | 0.82 ms | 1.58 ms | 3.74 ms | linear — the word pool + three-level deref dominate; ≈ 0.3 µs/key |
| 16 optimal stash (external deref table + prefix-free filter, §6.6) | 0.79 ms | 1.61 ms | 4.01 ms | ≈ linear — ≈ 0.49 µs/key; full verify + table check at each phase boundary |
| **total** | **23.69 ms** | **55.04 ms** | **112.20 ms** | linear |

(The total is the script's own measured sum for that run, not the arithmetic
sum of the rounded rows above; the 2^14 column carries ±30% run-to-run
variance.)

What the numbers show:

- **O(1) operations stay O(1) as n grows.** Bulk load, retrieval and the
  rotation phases double their total cost when n doubles, with flat per-key /
  per-op cost (Phase 1 ≈ 16–18 ns/key across the 4× range; Phase 9 ≈ 0.37–0.41
  µs per AVL insert including rebalancing; Phase 10 ≈ 0.3 µs per rotation
  attempt; Phase 11 ≈ 88 ns/value; Phase 12 ≈ 191 ns/pair). Phase 12 does two
  table allocations + two verifies per pair, and its ~10% chained keys add an
  arena allocation + holder slot each, so it tracks at ≈ 2× Phase 11's per-op
  cost — still flat, still constant-time. Phase 13's Theorem-5 sweep
  runs the least-loaded placement at every budget s = 0..6, whose probes sum
  to m·(2^7 − 1) ≈ 8.3M at n = 2^16 — 10.24 ms ≈ 1.2 ns/probe, cleanly linear
  (2.37 → 4.68 → 10.24 ms across the 4× range). Phase 14 runs the same
  resize-heavy workload (load 30k → churn 20k → drain 26k → reload 25k, 12
  grow/shrink transitions) *twice* — naive one-shot vs deamortized — and
  reports the worst single op: **143,363 work units (1.9 ms)** for the naive
  trigger op vs **81 units (23 µs)** deamortized, a ≈ 1770× ratio. The naive op
  pays Θ(live) in one shot; the deamortized op is capped at the fixed
  RV_BUDGET + RV_SCAN + 2 allowance (81 ≤ 82), exactly as §6.1 requires. Churn is the diagnostic
  exception: Phase 2 and 8 re-run a full `reg_verify` over the whole registry
  (REG_SIZE = 2n) every 5 000 ops, so their per-op cost grows with n
  (Phase 2: 20 → 35 → 62 ns/op) — while Phase 3, which churns *without* the
  periodic verify, stays cleanly linear (0.12 → 0.23 → 0.48 ms), isolating the
  verify's O(n) scan as the cause.
- **Phase 4 is the control**: its workload is a fixed 8-entry dictionary, and its
  time is flat (0.14–0.15 ms) — a constant amount of work costs a constant amount
  of time, as it must.
- **Phase 6 grows with the registry, not the attack**: the 20-key cascade itself
  is constant work, but the tail check re-scans every live key, so the phase
  scales with n — the table's own report makes the fixed vs. scanning split
  visible.
- **The chain costs O(1) pointers per big value, not per key.** Phase 15's
  r-levels chain (r=2: 13 bits/value — 8-bit holder + 5-bit p₁; r=3: 19
  bits/value — 8-bit holder + 6-bit p₂ + 5-bit p₁) adds one dereference per
  level only for values > 64 bits, so its time tracks Phase 11's per-key cost
  (0.82 → 1.58 → 3.74 ms — cleanly linear; the r=3 word pool + three-level
  deref dominate the phase). The constant-length linked list keeps every op
  O(1), the base pointer never grows with value size — 8 bits for v = 1..2^32
  — and the r=3 pointer widths (8 → 6 → 5) are all CONSTANT in v, so the base
  table's geometry is value-size-independent.
- **The stash is O(m) regardless of the external array.** Phase 16 keeps its
  4-bit pointer fixed (the bucket is implicit — it is never stored) and its
  adaptivity bits at ≈3.8/key (the prefix-free filter, O(m) total), so the
  stash scales linearly with m, not with log(4m): ≈0.5 µs/key at n = 2^16
  (0.79 → 1.61 → 4.01 ms — the super-linear tail is the full registry verify
  and the 4n-slot table check at each phase boundary, which scale with n).
  Query still costs exactly one external read — measured 16,384 reads for
  16,384 queries.
- **Why the sizes stop at 2^16**: the variable-size table is the paper's
  δn/2-slot *secondary* — 4096 containers × 32 slots — so its standalone load is
  deliberately low. At n = 2^17 the fixed geometry saturates and the demo fails
  its own capacity check, exactly as the paper's reduction predicts: this
  construction is meant to sit *under* a primary table, not to hold a full
  (1 − δ)·n load by itself.

Machine caveat: single machine (Apple M-series, clang 17, `-O2`, best of 3).
The 2^14 columns are sub-millisecond and carry ±30% run-to-run variance
(consecutive runs: Phase 1 0.20 vs 0.29 ms) — treat them as order-of-magnitude;
the 2^16 column is stable to a few percent. The numbers demonstrate the scaling
and constant-time claims, not peak throughput.

---

## Verification methodology

Every phase re-checks its own work before reporting:

- **Registry model** — each key's expected slot and value are recorded; every
  phase ends by re-running `Dereference(key, pointer)` on *all* live keys and
  comparing (functions `reg_verify`, `vreg_verify`, `rreg_verify`).
- **Deterministic invariants** — `Lᵢ ≤ sᵢ`, bucket/overflow occupancies
  (`vtable_check`), `H entries == live count`, AVL balance
  (`bst_balance_check`), retriever→slot→store integrity and node positions
  (`bst_ptr_check`).
- **Exit code** — 0 on PASS, 1 on any FAIL, so the example is CI-friendly.

One implementation subtlety worth knowing: the demo's null-edge sentinel is
`BST_NULL = -2`, *not* `-1`, because the dereference table treats `-1` as its
free marker — a null child stored as `-1` would look like a free slot and get
reallocated to another key.

## See also

- Source: [`examples/systems/tiny_pointers.flow`](../../examples/systems/tiny_pointers.flow)
- Application deep dive: [variable-size value dictionaries](tiny-pointers-variable-values.md)
- Paper: [Tiny Pointers, arXiv:2111.12800](https://arxiv.org/abs/2111.12800)
- Related stdlib: [memory.md](memory.md), [core.md](core.md)
