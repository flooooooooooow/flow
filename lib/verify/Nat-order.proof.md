# verify.Nat-order

*Order axioms and basic lemmas on natural numbers.*

**Source.** peano — https://en.wikipedia.org/wiki/Total_order

## Derived fact 1 — Every natural is less than or equal to itself

**Coordinate.** the natural numbers · order · less-or-equal is reflexive · **Derived fact**

*Source: peano*

> **Goal.** Every natural is less than or equal to itself.  n ≤ n
>
> $$\forall n \in \mathbb{N}\quad n \le n$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that less-or-equal is reflexive for order on the natural numbers. |  |  |
| ② | We can deduce that n is at most n. Hence proven. | ② | $n \le n$ |

`the natural numbers · order · less-or-equal is reflexive`

## Derived fact 2 — If a ≤ b and b ≤ a, then a = b

**Coordinate.** the natural numbers · order · less-or-equal is antisymmetric · **Derived fact**

*Source: peano*

*Built on: left cancellation holds, for addition on the natural numbers*

> **Goal.** If a ≤ b and b ≤ a, then a = b
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N}\quad a = b$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that less-or-equal is antisymmetric for order on the natural numbers. |  |  |
| ② | We split into exhaustive cases — the claim must hold in each one. |  |  |
| ③ | Case 1 (see step 2): suppose a <= b. |  |  |
| ④ | Case 2 (see step 2): suppose b <= a. |  |  |
| ⑤ | We invoke the derived fact governing addition on the natural numbers: left cancellation holds, for addition on the natural numbers (instantiated for a, 0, 0). |  |  |
| ⑥ | From step 4 and step 5, this implies a equals b. Together with the other cases (step 3 and step 4), the goal is discharged. Hence proven. | ⑥ | $a = b$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |
| ④ | step 2 |
| ⑥ | step 4 and step 5 |

`the natural numbers · order · less-or-equal is antisymmetric`

## Derived fact 3 — If a ≤ b and b ≤ c, then a ≤ c

**Coordinate.** the natural numbers · order · less-or-equal is transitive · **Derived fact**

*Source: peano*

> **Goal.** If a ≤ b and b ≤ c, then a ≤ c
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N} \forall c \in \mathbb{N}\quad a \le c$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that less-or-equal is transitive for order on the natural numbers. |  |  |
| ② | We split into exhaustive cases — the claim must hold in each one. |  |  |
| ③ | Case 1 (see step 2): suppose a <= b. |  |  |
| ④ | Case 2 (see step 2): suppose b <= c. |  |  |
| ⑤ | From step 4, this implies a is at most c. Together with the other cases (step 3 and step 4), the goal is discharged. Hence proven. | ⑤ | $a \le c$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |
| ④ | step 2 |
| ⑤ | step 4 |

`the natural numbers · order · less-or-equal is transitive`

## Derived fact 4 — Every natural is strictly less than its successor

**Coordinate.** the natural numbers · order · every number is below its successor · **Derived fact**

*Source: peano*

*Built on: adding zero on the left does not change the number*

> **Goal.** Every natural is strictly less than its successor.  n < succ(n)
>
> $$\forall n \in \mathbb{N}\quad n < \mathrm{succ}(n)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that every number is below its successor for order on the natural numbers. |  |  |
| ② | We invoke the definitional clause governing addition on the natural numbers: adding zero on the left does not change the number (instantiated for n). | ② | $0 + n = n$ |
| ③ | From step 2, this implies n < the successor of n. Hence proven. | ③ | $n < \mathrm{succ}(n)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |

`the natural numbers · order · every number is below its successor`
