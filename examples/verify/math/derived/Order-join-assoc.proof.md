# examples.verify.math.derived

*Join associates on the lattice order.*

**Source.** davey-priestley — *Introduction to Lattices and Order*

## Derived fact 1 — (a ∨ b) ∨ c = a ∨ (b ∨ c)

**Coordinate.** Order · join · parentheses do not matter · **Derived fact**

*Source: davey-priestley*

*Built on: order does not matter, for join on Order, parentheses do not matter, for meet on Order*

> **Goal.** (a ∨ b) ∨ c = a ∨ (b ∨ c)
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N} \forall c \in \mathbb{N}\quad join(join(a, b), c) = join(a, join(b, c))$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that parentheses do not matter for join on Order. |  |  |
| ② | We invoke the derived fact governing join on Order: order does not matter, for join on Order (instantiated for a, b). |  |  |
| ③ | We invoke the derived fact governing join on Order: order does not matter, for join on Order (instantiated for b, c). |  |  |
| ④ | We invoke the derived fact governing meet on Order: parentheses do not matter, for meet on Order (instantiated for a, b, c). |  |  |
| ⑤ | From step 2, step 3, and step 4, this implies join(join(a, b), c) equals join(a, join(b, c)). Hence proven. | ⑤ | $join(join(a, b), c) = join(a, join(b, c))$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑤ | step 2, step 3, and step 4 |

`Order · join · parentheses do not matter`
