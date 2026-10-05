# examples.verify.math.derived

*Multiplying on the left preserves less-or-equal order.*

**Source.** peano — https://en.wikipedia.org/wiki/Monotonic_function

## Derived fact 1 — If a ≤ b then c * a ≤ c * b

**Coordinate.** the natural numbers · multiplication · multiplying on the left preserves order · **Derived fact**

*Source: peano/induction — Gries & Schneider, Ch. 3*

*Built on: zero is the left annihilator, for multiplication on the natural numbers, successor on the right distributes, for multiplication on the natural numbers, adding on the right preserves order, for addition on the natural numbers*

> **Goal.** If a ≤ b then c * a ≤ c * b
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N} \forall c \in \mathbb{N}\quad c \cdot a \le c \cdot b$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that multiplying on the left preserves order for multiplication on the natural numbers. |  |  |
| ② | We proceed by induction on a: first the base case, then the inductive step. |  |  |
| ③ | Consider the base case in which a <= b. |  |  |
| ④ | Consider the base case in which c is zero. |  |  |
| ⑤ | We invoke the definitional clause governing multiplication on the natural numbers: zero is the left annihilator, for multiplication on the natural numbers (instantiated for a). |  |  |
| ⑥ | We invoke the definitional clause governing multiplication on the natural numbers: zero is the left annihilator, for multiplication on the natural numbers (instantiated for b). |  |  |
| ⑦ | From step 4, step 5, and step 6, we can deduce that c times a is at most c times b. This establishes the base case (see step 4, step 5, and step 6). Hence proven. | ⑦ | $c \cdot a \le c \cdot b$ |
| ⑧ | For the inductive step, suppose the claim holds for all smaller values. |  |  |
| ⑨ | Under the supposition in step 8, let k denote the predecessor of c. |  |  |
| ⑩ | Under the supposition in step 8, we cross the inductive boundary: assume the claim holds for a (the induction hypothesis). | ⑩ | $k \cdot a \le k \cdot b$ |
| ⑪ | We invoke the definitional clause governing multiplication on the natural numbers: successor on the right distributes, for multiplication on the natural numbers (instantiated for k, a). |  |  |
| ⑫ | We invoke the definitional clause governing multiplication on the natural numbers: successor on the right distributes, for multiplication on the natural numbers (instantiated for k, b). |  |  |
| ⑬ | We invoke the derived fact governing addition on the natural numbers: adding on the right preserves order, for addition on the natural numbers (instantiated for k * a, a, b). |  |  |
| ⑭ | From step 8, step 9, step 10, step 11, step 12, and step 13, this implies c times a is at most c times b. Hence proven. | ⑭ | $c \cdot a \le c \cdot b$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑤ | step 4 |
| ⑥ | step 4 |
| ⑦ | step 4, step 5, and step 6 |
| ⑨ | step 8 |
| ⑩ | step 8 |
| ⑭ | step 8, step 9, step 10, step 11, step 12, and step 13 |

`the natural numbers · multiplication · multiplying on the left preserves order`
