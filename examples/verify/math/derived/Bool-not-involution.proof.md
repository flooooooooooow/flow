# examples.verify.math.derived

*Negating twice returns the original boolean.*

**Source.** boole — https://en.wikipedia.org/wiki/Involution_(mathematics)

## Derived fact 1 — Double negation is the identity: ¬¬a = a

**Coordinate.** boolean truth values · negation · double negation returns the value · **Derived fact**

*Source: boole — https://en.wikipedia.org/wiki/Negation*

> **Goal.** Double negation is the identity: ¬¬a = a
>
> $$\forall a \in \{\mathsf{true}, \mathsf{false}\}\quad !(!a) = a$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that double negation returns the value for negation on boolean truth values. |  |  |
| ② | We split into exhaustive cases — the claim must hold in each one. |  |  |
| ③ | Case 1 (see step 2): suppose a holds. |  |  |
| ④ | From step 3, this implies !(!a) equals a in this case. | ④ | $!(!a) = a$ |
| ⑤ | Case 2 (see step 2): neither disjunct holds. |  |  |
| ⑥ | From step 5, this implies !(!a) equals a. Together with the other cases (step 3 and step 5), the goal is discharged. Hence proven. | ⑥ | $!(!a) = a$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |
| ④ | step 3 |
| ⑤ | step 2 |
| ⑥ | step 5 |

`boolean truth values · negation · double negation returns the value`
