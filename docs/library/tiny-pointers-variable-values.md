# Variable-Size Value Dictionaries (arXiv:2111.12800 §6.5) in Flow

A working, self-verifying Flow implementation of the paper's fourth
application — **space-efficient dictionaries with variable-size values** — lives
in [`examples/systems/tiny_pointers.flow`](../../examples/systems/tiny_pointers.flow)
as **Phase 11**.

> [!important] The guarantee
> Any key-value dictionary designed for uniform-size values can store
> **arbitrary-length values** (up to O(1) machine words) with constant-time
> overhead, replacing the value array with a structure that consumes
>
> `O(m log⁽ʳ⁾ m) + Σᵢ (vᵢ + O(log vᵢ))`
>
> bits for m values of lengths v₁…vₘ — instead of a uniform W-bit slot per
> value. A dictionary that mostly holds small values no longer pays W bits for
> every one of them.

## Theorem 9 and the size-class construction

**Paper (Theorem 9, Section 6.5).** The transformation is black-box: the base
dictionary T (hash table, BST, whatever) keeps its keys and pointers, only its
*value array* is replaced. Values are grouped into **size classes** — a value
of v bits lives in class `⌈log₂ v⌉`, whose slots are exactly `2^⌈log v⌉` bits —
and each class owns its own dereference-table storage keyed on the key, exactly
like every other tiny-pointer table in the paper. The key hashes to a bucket
inside the class; the tiny pointer packs (class, choice, slot) in
`⌈log₂ classes⌉ + 1 + ⌈log₂ b⌉ = O(log v)` bits. The paper's r-levels-of-
indirection chain (pointers of size O(log k), O(log log k), … up to log⁽ʳ⁾ n)
is implemented as **Phase 15**: values up to 256 bits live behind a 5-bit
second-level tiny pointer p₁ = O(log k), while the base pointer stays
O(log⁽ʳ⁾ n) — constant in value size ([details
below](#the-r-levels-chain--phase-15-65)). Its **deamortized dynamic resizing
(§6.1) is implemented as Phase 14**: the class storage grows and shrinks
incrementally, so no single insert copies O(m) values ([details
below](#deamortized-dynamic-resizing--phase-14-61)).

**Parameter math** (concrete instance in Phase 11):

```text
classes   = 7          slots of 1, 2, 4, 8, 16, 32, 64 bits
buckets   = 4096 / class · b = 8 slots · power-of-two-choices
pointer   = 3 class bits + 1 choice bit + 3 slot bits = 7 bits = O(log 64)
value space per key = 2^⌈log v⌉ (rounded payload) + 7 (pointer bits)
paper bound (Eq. 4) = O(m log⁽ʳ⁾ m) + Σᵢ (vᵢ + O(log vᵢ))
```

Values are drawn from a skewed distribution — 70% ≤ 8 bits, 20% ≤ 16 bits,
10% up to 64 bits — the regime where size-classed storage wins hardest.

**Empirical results (Phase 11, n = 2^16, all runs exit 0):**

| Measurement | Result |
|---|---|
| Load (49,152 keys, skewed sizes) | 0 verify errors · 0 per-class invariant violations |
| Size-class histogram (1,2,4,8,16,32,64-bit slots) | 4263 · 4271 · 8672 · 17172 · 9882 · 1638 · 3254 |
| Value space (payload + 7-bit pointers) | **947,717 bits = 19.28 bits/value** vs uniform 64-bit 3,145,728 bits → **69.9% saved** |
| 30,000-op churn (deletes + fresh skewed values) | 0 errors |
| Uniform 64-bit control (+8,192 max-size values) | verify 0 · invariants 0 — final mean 26.64 bits/value |

The control is a **fixed-size** check: the same +8,192 max-size values at
every scale (it does not grow with n), so at the smallest benchmark size it
becomes the dominant contributor to the 64-bit class's bucket load. It exists
to prove the bound is tight when values are uniform-max, not to model a
scaled workload — keep it fixed if you re-run the geometry at other n.
| Wall-clock (native `-O2` binary, n = 2^16) | ≈ 4.3 ms for the whole phase (~88 ns/value) |

What the numbers show:

- **Skew wins.** 70% of values are ≤ 8 bits and cost ≤ 8 + 7 = 15 bits instead
  of 64. The mean drops to **19.3 bits/value — ≈ 3.3× less than a uniform
  64-bit dictionary** (the paper's abstract promises `log⁽ʳ⁾ n + O(log j)` bits
  per j-bit value; the demo measures that bound directly).
- **The bound is tight when values are uniform-max.** Adding 8,192 64-bit
  values drags the mean up to 26.6 bits/value: each large value pays its full
  64 bits plus its O(log v) pointer, exactly as `Σ(vᵢ + O(log vᵢ))` predicts —
  the construction saves nothing for uniform large values and never loses.
- **Bit-exact round-trips.** Every stored i64 is read back and compared against
  the recorded value for *all* live keys after every sub-phase (the registry
  model, same as Phases 1–10), so the size-classed storage is proven lossless
  for every key, every value size, every seed.
- **Constant time.** Two-choice hashing keeps per-op cost flat; the phase
  scales linearly in n (0.86 → 1.77 → 4.33 ms across n = 2^14..2^16 — see the
  benchmark table in the main reference).

## The keys analogue — Phase 12

The paper states Theorem 9 for "a key-value dictionary … designed to store
fixed-length keys", and remarks that the construction is symmetric: "the same
techniques work … without modification." **Phase 12** applies the size-class
trick to the *key array* — a k-bit key lives in class `⌈log₂ k⌉` with
`2^⌈log k⌉`-bit slots, so the key space is also `Σ(2^⌈log kᵢ⌉ + O(log kᵢ))`
instead of a uniform 64-bit slot per key — and stores **both** sides of each
pair size-classed: a key table and a value table keyed on the same logical
key, one registry entry per pair, everything verified bit-exactly.

**The key chain.** Phase 12 lifts the KEY cap exactly as Phase 15 lifts the
VALUE cap: the key side runs the same r-levels-of-indirection chain, so keys
of 65–256 bits live in a compact key arena (an RLTable, 2 classes of
128/256-bit slots keyed on the key) behind a 5-bit p₁ = O(log 256) held in an
8-bit base class-3 holder slot, with flag bit 7 marking chained keys. Keys
≤ 64 bits store directly in the base key VDTable. The base pointer stays
**8 bits for every key size** — the key analogue of Phase 15's base-pointer
independence — and the chain costs **13 bits per big key** (8-bit holder +
5-bit p₁), never per pair.

**Empirical results (Phase 12, n = 2^16, all runs exit 0):**

| Measurement | Result |
|---|---|
| Load (49,152 pairs, skewed key and value sizes) | 0 verify errors · 0 key-table / 0 key-arena / 0 value-table invariant violations |
| Key-size histogram (1,2,4,8,16,32,64-bit slots + 128/256-bit arena) | 3636 · 3751 · 7320 · 14776 · 8855 · 1933 · 4020 · **3412 · 1449** |
| Chained keys (65–256 bits through the arena) | **4,861 of 49,152** (9.9%) — verify 0 through base → p₁ → arena |
| Value-size histogram (same pairs) | 4126 · 4319 · 8751 · 17306 · 9749 · 1660 · 3241 |
| **Combined key+value space** (payloads + 7-bit key/value pointers; chained keys +13) | **2,747,160 bits = 55.89 bits/pair** vs uniform 64+64 = 6,291,456 bits → **56.3% saved** vs uniform 256+64 = 15,728,640 bits → **82.5% saved** |
| 30,000-op churn (deletes + fresh skewed pairs, big keys through the chain) | 0 errors · 0 invariant violations |
| Uniform 64+64 control (+8,192 max-size pairs) + uniform 256+64 control (+1,024 max-size chained keys) | verify 0 · invariants 0 — final mean 73.06 bits/pair |

Combining Phase 11's value classes with the new key classes saves on **both**
sides: skewed keys cost ≈ 19.3 bits (like skewed values did) and the 9.9% of
keys that exceed 64 bits cost only ≈ 128/256 + 13 instead of a uniform 256-bit
slot. The pair mean lands at **55.89 bits** — 56.3% off the old 64+64 uniform
baseline and **82.5% off the 256+64 baseline sized to the new caps** — the
largest saving yet because the uniform comparison now pays for the biggest key
any pair can hold. The +8,192/+1,024 controls are **fixed-size** (they do not
scale with n), so at the smallest benchmark size they dominate their classes'
bucket load — keep them fixed if you re-run the geometry at other n.

## The r-levels chain — Phase 15 (§6.5)

The size-class table caps values at O(1) machine words because its slots are
sized to the value: a 200-bit value would need a 256-bit **base** slot, and
the base class tag would have to grow with the max value size. Theorem 9's
proof stores every value "at the end of a linked list of length O(1)" — value
k bits ← p₁ of O(log k) bits ← … ← base pointer of O(log⁽ʳ⁾ n) bits — with a
different dereference table per size class at each level.

Phase 15 implements the chain with r = 2 levels, lifting the v ≤ 64 cap to
256 bits:

```text
base pointer = 1 flag + 3 class + 1 choice + 3 slot = 8 bits (for v = 1..256)
p₁           = 1 arena-class + 1 choice + 3 slot     = 5 bits = O(log 256)
holder slot  = 8-bit base slot (class 3) holding p₁
value        = 128 or 256 bits, in the level-1 arena (compact, keyed on the key)
```

Values ≤ 64 bits store directly (Phase-11 classes); values of 65–256 bits go
through the chain. The flag bit (the paper's "points at a pointer vs a value"
metadata) marks chained pointers, and the 5-bit p₁ (O(log k)) lives in an
8-bit base slot — so the **base pointer stays 8 bits for every value size**,
the paper's "base pointer … is O(log⁽ʳ⁾ n) bits".

### The r = 3 extension — the O(log log k) middle pointer p₂

The demo now goes one level deeper (Phase 15's r=3 extension): the
O(log log k)-bit **p₂** is inserted between the base and p₁, and the value
store becomes a word pool that an arena slot points at — so a value can be
**any width**:

```text
base pointer = 8 bits, UNCHANGED (flag + class + choice + slot) — holds p₂
p₂           = 6 bits = class(1) + choice(1) + slot(4) — into the level-2 table
p₁           = 5 bits = class(1) + choice(1) + slot(3) — into the level-1 arena
value        = up to 2^32 bits in the design (demo stores up to 2^18) — words
               in a shared pool behind the 5-bit p₁
```

Measured pointer hierarchy: **8 → 6 → 5 bits** (base → p₂ → p₁), all
CONSTANT as v grows — the base never changes even for a 2^32-bit value, and
only the word count grows. (These widths are table-geometry constants, not
the paper's exponentially-sized hierarchy — the demo captures the
base-pointer independence, not the asymptotic sizing; see the divergence
notes below.) The per-big-value chain cost is 19 bits (8-bit holder + 6-bit
p₂ + 5-bit p₁) vs r=2's 13: the extra 6 bits lift the value cap from 256
bits to 2^32 bits. Measured at n = 2^16: 12,288 keys with ≈1,230 chained
values (63 of them > 2^16 bits, up to 32 KB) verify 0 errors and 0 invariant
violations through base → p₂ → p₁ → pool, churn 0, and the chain saves
99.34% vs a uniform store sized to the largest value.

**Empirical results (Phase 15, n = 2^16, all runs exit 0):**

| Measurement | Result |
|---|---|
| Load 12,288 keys + 4,000-op churn → 12,352 live (11,116 ≤ 64-bit, 860 × 128-bit, 376 × 256-bit) | 0 verify errors · 0 arena / 0 base invariant violations |
| Churn (4,000 ops incl. big-value inserts/deletes) | verify 0 — p₁ holder + arena slot freed/reallocated atomically per key |
| r-levels space | **475,366 bits = 38.5 bits/value** vs uniform 256-bit 3,162,112 bits → **84.97% saved** |
| Single-level size-classed (same data) | 459,298 bits → 85.47% saved — the chain costs **13 bits/value on big values only** (8-bit holder + 5-bit p₁ = the paper's O(log v) overhead in Eq. 4) |
| Base pointer size | 8 bits for v = 1 and v = 256 alike — value-size-independent |

The second level costs 13 bits per *big* value (the O(log v) term in Eq. 4),
never per key: small values pay exactly what Phase 11 charges. In exchange
the base table's geometry (class tags, bucket counts) is completely
independent of value size — a future 2⁶⁴-bit value class would only grow the
compact arena, never the base table or the base pointer.

### Where the demo diverges from §6.5

The chain faithfully realizes the linked-list part of Theorem 9's proof —
base → p₂ → p₁ → value (length O(1)),
per-size-class buckets (packed into one shared table per level via class
tags — the demo's compact analogue of the paper's separate per-size-class
tables), the per-pointer flag (the paper's "points at a pointer vs a value"
bit, with class tags approximating the rest of its O(j) metadata), and the
chain's overhead charged per *value* (the O(log vᵢ) term of Eq. 4), never
per key. Four deliberate divergences from the paper's construction:

- **Pointer widths are geometry constants, and the hierarchy direction is
  inverted.** The paper sizes pointers by the *value*: p₁ = O(log k) is the
  LARGEST (it grows with the value's bit-length k), each subsequent pointer
  toward the base is exponentially smaller, and the base O(log⁽ʳ⁾ n) is the
  smallest ("each subsequent pointer is exponentially larger than the
  previous one"). The demo's measured 8 → 6 → 5 bits (base → p₂ → p₁) shrink
  in the *opposite* direction and never move with v — they are the
  class+choice+slot widths of three differently-sized tables. The demo
  captures the *base-pointer independence* property (the base never grows
  with the value), not the exponential sizing. The k-dependent part — the
  word-pool offset, which plays the role of the paper's per-size-class value
  addressing — is stored *inside* the arena slot; the slot itself is the
  demo's analogue of the paper's "chunked-storage technique" for
  variable-sized objects.
- **The base does not shrink with r.** In the paper, adding levels shrinks
  the base itself: O(log⁽ʳ⁾ n), with log⁽³⁾ n < log² n. The demo's base stays
  8 bits at r = 2 and r = 3 — constant in both the value size and r. The
  Phase 8b retriever sweep demonstrates the log⁽ʳ⁾ n shrinkage on the
  Theorem-6 side instead (w₀ = 15 → 4 → 2 → 1 bits/key).
- **Values past the paper's O(1)-word convenience cap.** Theorem 9 states
  values "up to O(1) machine words" (so each value is read/written in
  constant time) and notes the techniques "work for even larger values
  without modification"; the demo's 2^32-bit design (2^18 stored) leans on
  that remark.
- **Fixed-capacity chain tables.** §6.5's proof is mostly the
  dynamic-resizing machinery — zone-aggregated resizing of every
  per-size-class table under the dynamic-sizing invariant. The demo's chain
  tables are fixed-capacity (and its word pool is bump-only: freed words are
  not reclaimed); Phase 14 demonstrates zone-aggregated resizing on the
  single-level size-class table, not on the chain.

## Deamortized dynamic resizing — Phase 14 (§6.1)

The r-levels construction also hides a *one-shot resize*: when a class's
storage doubles or halves, the textbook implementation pays the full Θ(m) copy
inside the operation that triggers it. Section 6.1's **zone-aggregated
resizing** deamortizes this — the rebuild is spread over the following
operations at a fixed per-op budget, so even the triggering op stays O(1).

Phase 14 runs the **same** resize-heavy workload twice — load 30,000 → churn
20,000 → drain 26,000 → reload 25,000, 12 grow/shrink transitions, same seed:

- **Naive one-shot** — each resize finishes inside the triggering op (the
  textbook Θ(live) copy of the whole class storage).
- **Deamortized** — the transition runs in the background at a fixed budget
  (`RV_BUDGET = 16` values migrated + `RV_SCAN = 64` registry entries examined
  per op), with an epoch cursor and a second, destination generation:
  inserts/deletes keep hitting the source generation and are migrated by the
  sweep. Grow triggers early (at 7·B) and shrink has hysteresis (at 3.5·B,
  past the post-shrink grow point), so a mid-transition load burst can never
  push a size class's busiest bucket past its 8-slot ceiling; and the
  transition check only inspects the zeroed prefix of the in-flight
  destination generation, never its uninitialized tail.

**Empirical results (n = 2^16, both runs exit 0):**

| Measurement | Naive one-shot | Deamortized |
|---|---|---|
| Worst single op | **143,363 work units · 1,905,000 ns** | **81 work units · 23,000 ns** |
| Resize cost placement | full Θ(live) copy inside the trigger op | spread within RV_BUDGET + RV_SCAN + 2 = 82 per op (measured worst 81) |
| Verifies (12 transitions + final flush) | 0 errors | 0 errors |

The worst-case per-op cost drops **143,363 → 81 work units (≈ 1770×)** and
**1.9 ms → 23 µs (≈ 83×)** — the deamortized op sits inside the fixed-budget
allowance (81 ≤ RV_BUDGET + RV_SCAN + 2 = 82), so the resize is *worst-case*
O(1) per operation, not merely amortized. Both runs re-verify every live
value bit-exactly through the dereference table even mid-transition (each
value is atomic per generation: it lives in the source or the destination,
never half-written).

## Relationship to the rest of the demo

| Section | Phase | Result |
|---|---|---|
| Thm 1 — fixed-size tiny pointers (§3) | 1–4 | 6-bit pointers |
| Thm 2 — variable-size tiny pointers (§4) | 5–6 | ~3-bit pointers, doubly-exponential tail |
| Thm 6 — relaxed retrieval (§6.2) | 7–8, 8b | O(1)-expected hints beat Ω(log log n); Phase 8b sweeps the r = 1..4 tradeoff: O(r) insert/delete vs `O(n log⁽ʳ⁾ n)` space (retriever term 15 → 4 → 2 → 1 bits/key) |
| Thm 7 — succinct rotation-based BSTs (§6.3) | 9–10 | ~3 bits/child pointer, O(1) rotations |
| Thm 8 — stable dictionaries (§6.4) | 3–4 | values never move across rehash |
| **Thm 9 — variable-size value dictionaries** | **11** | **19.3 bits/value vs 64 uniform** |
| **Thm 9 keys analogue — variable-size key+value dicts** | **12** | **55.9 bits/pair: 56.3% vs 64+64, 82.5% vs 256+64 — keys to 256 bits through the same chain as Phase 15** |
| **Thm 3–5 — the lower bounds** | **13** | **floor holds at every budget s; < 6 bits collides** |
| **§6.1 — deamortized resize** | **14** | **worst op 81 units vs 143,363 naive — Θ(live) → O(1)** |
| **§6.5 — r-levels of indirection** | **15** | **values to 256 bits behind a 5-bit p₁; base pointer stays 8 bits (r=2); r=3 inserts a 6-bit p₂ and lifts the cap to 2^32 bits — pointers 8 → 6 → 5, all constant in v** |
| **Thm 10 — optimal internal-memory stash** | **16** | **O(m log ε⁻¹) = O(m) internal bits; 7.76 bits/key vs 15 naive; one external read per query** |

### Abstract-claim coverage

Where the table above maps each *phase* to its result, this maps each
**abstract promise** — the two pointer results and five applications the
paper's abstract advertises — to the row that fulfils it (full theorem table
in [tiny-pointers.md](tiny-pointers.md)). This deep-dive is the **application
④** entry — *arbitrary-size values* (Theorem 9):

| Abstract claim | Row |
|---|---|
| Fixed-size pointers of `Θ(log log log n + log k)` bits | Theorem 1 (Phases 1–4) |
| Variable-size pointers of `Θ(log k)` expected bits | Theorem 2 (Phases 5–6) |
| `nv + O(n log⁽ʳ⁾ n)`-bit store with an O(1)-expected pointer per key, O(r) insert/delete | Theorem 6 (Phases 7–8, 8b) |
| Succinct BSTs, rotations included | Theorem 7 (Phases 9–10) |
| Stable fixed-capacity dictionaries, `1 + o(1)` overhead | Theorem 8 (Phases 3–4) |
| **Arbitrary-size values at `log⁽ʳ⁾ n + O(log j)` bits per j-bit value** | **Theorem 9 (Phases 11/12/14/15) — this doc (§6.5)** |
| `O(n log ε⁻¹)`-bit internal-memory stash, no IOs | Theorem 10 (Phase 16) |

(Theorems 3–5 are *lower bounds* / intermediate steps, not constructions —
e.g. Theorem 3 proves `Ω(log log log n + log k)` is optimal for fixed-size
tiny pointers. The demo implements the matching constructions.)

## Run it

```bash
FLOW_HOST=python ./flow run examples/systems/tiny_pointers.flow
```

Exit code 0 = PASS. Every phase — including the variable-value dictionary, its
Phase 12 keys analogue (now with 128/256-bit keys through the same r-levels
chain as Phase 15, verified word-by-word), the Phase 14 deamortized resize
(naive vs deamortized runs of the same workload, both self-verified), the
Phase 15 r-levels chain (128/256-bit values through a second-level tiny
pointer, verified bit-exactly, plus its r=3 extension: values up to 2^18 bits
through base(8) → p₂(6) → p₁(5) → pool, verified word-by-word), and the
Phase 16 optimal internal-memory stash (Theorem 10,
§6.6: 4-bit tiny pointers in a prefix-free adaptive filter, one external read
per query) — passes across all tested seeds (the size draws are deterministic
per seed; the savings stay 69.7–70.0% for the value-only accounting, 55.9–56.4%
vs 64+64 / 82.3–82.8% vs 256+64 for the combined key+value accounting,
84.8–85.0% vs a uniform 256-bit baseline for the r-levels chain, and ≈48% vs
a naive full-address stash for Phase 16).

## See also

- Main reference: [tiny-pointers.md](tiny-pointers.md) — all seven
  constructions, the Section-5 lower bounds (Thm 3–5, Phase 13), the
  deamortized resize (Phase 14), the r-levels-of-indirection chain (Phase 15,
  incl. the r=3 extension to 2^32-bit values), the optimal internal-memory
  stash (Phase 16, Theorem 10), the parameter
  math, and the per-phase benchmark table.
- Source: [`examples/systems/tiny_pointers.flow`](../../examples/systems/tiny_pointers.flow)
- Paper: [Tiny Pointers, arXiv:2111.12800](https://arxiv.org/abs/2111.12800)
