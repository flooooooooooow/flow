# examples.verify.math.derived

*Cardinality is monotone under union on the right.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Derived fact 1 — card(b) <= card(a ∪ b)

**Coordinate.** Finset · cardinality · size is monotone under union on the right · **Derived fact**

*Source: graham-knuth-patashnik*

*Built on: order does not matter, for union on Finset, size is monotone under union on the left, for cardinality on Finset*

> **Goal.** card(b) <= card(a ∪ b)
>
> $$\forall a \in Finset \forall b \in Finset\quad card(b) \le card(a ∪ b)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that size is monotone under union on the right for cardinality on Finset. |  |  |
| ② | We invoke the derived fact governing union on Finset: order does not matter, for union on Finset (instantiated for a, b). |  |  |
| ③ | We invoke the derived fact governing cardinality on Finset: size is monotone under union on the left, for cardinality on Finset (instantiated for b, a). |  |  |
| ④ | From step 2 and step 3, this implies card(b) is at most card(a ∪ b). Hence proven. | ④ | $card(b) \le card(a ∪ b)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Finset · cardinality · size is monotone under union on the right`
