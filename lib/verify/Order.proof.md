# verify.Order

*Lattice laws for meet and join on a partial order.*

**Source.** davey-priestley — *Introduction to Lattices and Order*

## Derived fact 1 — Meet is commutative: a ∧ b = b ∧ a

**Coordinate.** Order · meet · order does not matter · **Derived fact**

*Source: davey-priestley*

> **Goal.** Meet is commutative: a ∧ b = b ∧ a
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N}\quad meet(a, b) = meet(b, a)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that order does not matter for meet on Order. |  |  |
| ② | We can deduce that meet(a, b) equals meet(b, a). Hence proven. | ② | $meet(a, b) = meet(b, a)$ |

`Order · meet · order does not matter`

## Derived fact 2 — Join is commutative: a ∨ b = b ∨ a

**Coordinate.** Order · join · order does not matter · **Derived fact**

*Source: davey-priestley*

> **Goal.** Join is commutative: a ∨ b = b ∨ a
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N}\quad join(a, b) = join(b, a)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that order does not matter for join on Order. |  |  |
| ② | We can deduce that join(a, b) equals join(b, a). Hence proven. | ② | $join(a, b) = join(b, a)$ |

`Order · join · order does not matter`

## Derived fact 3 — Meet associates: (a ∧ b) ∧ c = a ∧ (b ∧ c)

**Coordinate.** Order · meet · parentheses do not matter · **Derived fact**

*Source: davey-priestley*

*Built on: order does not matter, for meet on Order*

> **Goal.** Meet associates: (a ∧ b) ∧ c = a ∧ (b ∧ c)
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N} \forall c \in \mathbb{N}\quad meet(meet(a, b), c) = meet(a, meet(b, c))$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that parentheses do not matter for meet on Order. |  |  |
| ② | We invoke the derived fact governing meet on Order: order does not matter, for meet on Order (instantiated for a, b). |  |  |
| ③ | We invoke the derived fact governing meet on Order: order does not matter, for meet on Order (instantiated for b, c). |  |  |
| ④ | From step 2 and step 3, this implies meet(meet(a, b), c) equals meet(a, meet(b, c)). Hence proven. | ④ | $meet(meet(a, b), c) = meet(a, meet(b, c))$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Order · meet · parentheses do not matter`
