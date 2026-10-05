# examples.verify.math.derived

*Adding a successor on the right steps the sum by one.*

**Source.** peano — https://en.wikipedia.org/wiki/Peano_axioms

## Derived fact 1 — a + succ(b) = succ(a + b)

**Coordinate.** the natural numbers · addition · successor on the right via commutativity · **Derived fact**

*Source: peano*

*Built on: adding one more on the right bumps the sum by one, you can swap the order when you add, successor on the left steps the sum, for addition on the natural numbers*

> **Goal.** a + succ(b) = succ(a + b)
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N}\quad a + \mathrm{succ}(b) = \mathrm{succ}(a + b)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that successor on the right via commutativity for addition on the natural numbers. |  |  |
| ② | We invoke the definitional clause governing addition on the natural numbers: adding one more on the right bumps the sum by one (instantiated for a, b). | ② | $a + \mathrm{succ}(b) = \mathrm{succ}(a + b)$ |
| ③ | We invoke the derived fact governing addition on the natural numbers: you can swap the order when you add (instantiated for a, b). | ③ | $a + b = b + a$ |
| ④ | We invoke the derived fact governing addition on the natural numbers: successor on the left steps the sum, for addition on the natural numbers (instantiated for b, a). |  |  |
| ⑤ | From step 2, step 3, and step 4, this implies a plus the successor of b equals the successor of a plus b. Hence proven. | ⑤ | $a + \mathrm{succ}(b) = \mathrm{succ}(a + b)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑤ | step 2, step 3, and step 4 |

`the natural numbers · addition · successor on the right via commutativity`
