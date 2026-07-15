# verify.Nat-mul

*Peano definitions for multiplication on natural numbers.*

**Source.** peano — https://en.wikipedia.org/wiki/Peano_axioms

## Definition 1 — Zero times anything is zero

**Coordinate.** the natural numbers · multiplication · zero is the left annihilator · **Definition**

*Source: peano*

> **Goal.** Zero times anything is zero.  (0 * 7 = 0)
>
> $$\forall m \in \mathbb{N}\quad 0 \cdot m = 0$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We stipulate zero is the left annihilator for multiplication on the natural numbers — this is a definition, not a derived fact. |  |  |
| ② | This follows directly from the definition: 0 times m equals 0. Hence proven. | ② | $0 \cdot m = 0$ |

`the natural numbers · multiplication · zero is the left annihilator`

## Definition 2 — Multiplying by a successor adds another copy

**Coordinate.** the natural numbers · multiplication · successor on the right distributes · **Definition**

*Source: peano*

> **Goal.** Multiplying by a successor adds another copy.  (3 * succ(2) = 3*2 + 3)
>
> $$\forall n \in \mathbb{N} \forall m \in \mathbb{N}\quad n * \mathrm{succ}(m) = n \cdot m + n$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We stipulate successor on the right distributes for multiplication on the natural numbers — this is a definition, not a derived fact. |  |  |
| ② | This follows directly from the definition: n times the successor of m equals n times m plus n. Hence proven. | ② | $n * \mathrm{succ}(m) = n \cdot m + n$ |

`the natural numbers · multiplication · successor on the right distributes`

## Definition 3 — Multiplying anything by zero on the right gives zero

**Coordinate.** the natural numbers · multiplication · zero is the right annihilator · **Definition**

*Source: peano*

> **Goal.** Multiplying anything by zero on the right gives zero.  (7 * 0 = 0)
>
> $$\forall n \in \mathbb{N}\quad n \cdot 0 = 0$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We stipulate zero is the right annihilator for multiplication on the natural numbers — this is a definition, not a derived fact. |  |  |
| ② | This follows directly from the definition: n times 0 equals 0. Hence proven. | ② | $n \cdot 0 = 0$ |

`the natural numbers · multiplication · zero is the right annihilator`
