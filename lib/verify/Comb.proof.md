# verify.Comb

*Basic combinatorial identities on binomial coefficients.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Definition 1 — Choosing zero items always gives one way

**Coordinate.** Comb · choose · choosing none gives one · **Definition**

*Source: graham-knuth-patashnik*

> **Goal.** Choosing zero items always gives one way
>
> $$\forall n \in \mathbb{N}\quad choose(n, 0) = 1$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We stipulate choosing none gives one for choose on Comb — this is a definition, not a derived fact. |  |  |
| ② | This follows directly from the definition: choose(n, 0) equals 1. Hence proven. | ② | $choose(n, 0) = 1$ |

`Comb · choose · choosing none gives one`

## Definition 2 — Pascal recurrence for binomial coefficients

**Coordinate.** Comb · choose · Pascal recurrence holds · **Definition**

*Source: graham-knuth-patashnik*

> **Goal.** Pascal recurrence for binomial coefficients
>
> $$\forall n \in \mathbb{N} \forall k \in \mathbb{N}\quad choose(n, k) = choose(pred(n), j) + choose(pred(n), k)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We stipulate pascal recurrence holds for choose on Comb — this is a definition, not a derived fact. |  |  |
| ② | We split into exhaustive cases — the claim must hold in each one. |  |  |
| ③ | Case 1 (see step 2): suppose k is zero. |  |  |
| ④ | From step 3, this implies choose(n, k) equals 1 in this case. | ④ | $choose(n, k) = 1$ |
| ⑤ | Case 2 (see step 2): neither disjunct holds. |  |  |
| ⑥ | Let j denote the predecessor of k. |  |  |
| ⑦ | From step 5 and step 6, this implies choose(n, k) equals choose(pred(n), j) plus choose(pred(n), k). Together with the other cases (step 3 and step 5), the goal is discharged. Hence proven. | ⑦ | $choose(n, k) = choose(pred(n), j) + choose(pred(n), k)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |
| ④ | step 3 |
| ⑤ | step 2 |
| ⑦ | step 5 and step 6 |

`Comb · choose · Pascal recurrence holds`
