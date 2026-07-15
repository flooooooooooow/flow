# verify.Nat

*Peano definitions for addition on natural numbers.*

**Source.** peano — https://en.wikipedia.org/wiki/Peano_axioms

## Definition 1 — Adding zero on the left gives the other number

**Coordinate.** the natural numbers · addition · zero is the left identity · **Definition**

*Source: peano*

> **Goal.** Adding zero on the left gives the other number.  (0 + 7 = 7)
>
> $$\forall m \in \mathbb{N}\quad 0 + m = m$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We stipulate zero is the left identity for addition on the natural numbers — this is a definition, not a derived fact. |  |  |
| ② | This follows directly from the definition: 0 plus m equals m. Hence proven. | ② | $0 + m = m$ |

`the natural numbers · addition · zero is the left identity`

## Definition 2 — Adding one more on the right steps the sum by one

**Coordinate.** the natural numbers · addition · successor on the right steps the sum · **Definition**

*Source: peano*

> **Goal.** Adding one more on the right steps the sum by one
>
> $$\forall n \in \mathbb{N} \forall m \in \mathbb{N}\quad n + \mathrm{succ}(m) = \mathrm{succ}(n + m)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We stipulate successor on the right steps the sum for addition on the natural numbers — this is a definition, not a derived fact. |  |  |
| ② | This follows directly from the definition: n plus the successor of m equals the successor of n plus m. Hence proven. | ② | $n + \mathrm{succ}(m) = \mathrm{succ}(n + m)$ |

`the natural numbers · addition · successor on the right steps the sum`
