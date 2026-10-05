# verify.Monoid

*Monoid axioms for an associative operation with identity.*

**Source.** dummit-foote — *Abstract Algebra*, §1.1

## Definition 1 — Monoid multiplication associates

**Coordinate.** Monoid · multiplication · parentheses do not matter · **Definition**

*Source: dummit-foote*

> **Goal.** Monoid multiplication associates
>
> $$\forall a \in Monoid \forall b \in Monoid \forall c \in Monoid\quad (a \cdot b) * c = a * (b \cdot c)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We stipulate parentheses do not matter for multiplication on Monoid — this is a definition, not a derived fact. |  |  |
| ② | This follows directly from the definition: (a times b) times c equals a times (b times c). Hence proven. | ② | $(a \cdot b) * c = a * (b \cdot c)$ |

`Monoid · multiplication · parentheses do not matter`

## Definition 2 — The identity is a left unit

**Coordinate.** Monoid · identity · one is the left identity · **Definition**

*Source: dummit-foote*

> **Goal.** The identity is a left unit
>
> $$\forall m \in Monoid\quad 1 \cdot m = m$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We stipulate one is the left identity for identity on Monoid — this is a definition, not a derived fact. |  |  |
| ② | This follows directly from the definition: 1 times m equals m. Hence proven. | ② | $1 \cdot m = m$ |

`Monoid · identity · one is the left identity`

## Definition 3 — The identity is a right unit

**Coordinate.** Monoid · identity · one is the right identity · **Definition**

*Source: dummit-foote*

> **Goal.** The identity is a right unit
>
> $$\forall m \in Monoid\quad m \cdot 1 = m$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We stipulate one is the right identity for identity on Monoid — this is a definition, not a derived fact. |  |  |
| ② | This follows directly from the definition: m times 1 equals m. Hence proven. | ② | $m \cdot 1 = m$ |

`Monoid · identity · one is the right identity`
