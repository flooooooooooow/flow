# verify.Pair

*Product type projections and pairing laws.*

**Source.** church — https://en.wikipedia.org/wiki/Product_type

## Definition 1 — The first projection returns the first component of a pair

**Coordinate.** Pair · first projection · first component is retrieved · **Definition**

*Source: church*

> **Goal.** The first projection returns the first component of a pair
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N}\quad fst(pair(a, b)) = a$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We stipulate first component is retrieved for first projection on Pair — this is a definition, not a derived fact. |  |  |
| ② | This follows directly from the definition: fst(pair(a, b)) equals a. Hence proven. | ② | $fst(pair(a, b)) = a$ |

`Pair · first projection · first component is retrieved`

## Definition 2 — The second projection returns the second component of a pair

**Coordinate.** Pair · second projection · second component is retrieved · **Definition**

*Source: church*

> **Goal.** The second projection returns the second component of a pair
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N}\quad snd(pair(a, b)) = b$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We stipulate second component is retrieved for second projection on Pair — this is a definition, not a derived fact. |  |  |
| ② | This follows directly from the definition: snd(pair(a, b)) equals b. Hence proven. | ② | $snd(pair(a, b)) = b$ |

`Pair · second projection · second component is retrieved`

## Derived fact 3 — Pairing and projecting round-trip to the same pair

**Coordinate.** Pair · pairing · components determine the pair · **Derived fact**

*Source: church*

*Built on: first component is retrieved, for first projection on Pair, second component is retrieved, for second projection on Pair*

> **Goal.** Pairing and projecting round-trip to the same pair
>
> $$\forall a \in \mathbb{N} \forall b \in \mathbb{N}\quad pair(a, b) = pair(fst(pair(a, b)), snd(pair(a, b)))$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that components determine the pair for pairing on Pair. |  |  |
| ② | We invoke the definitional clause governing first projection on Pair: first component is retrieved, for first projection on Pair (instantiated for a, b). |  |  |
| ③ | We invoke the definitional clause governing second projection on Pair: second component is retrieved, for second projection on Pair (instantiated for a, b). |  |  |
| ④ | From step 2 and step 3, this implies pair(a, b) equals pair(fst(pair(a, b)), snd(pair(a, b))). Hence proven. | ④ | $pair(a, b) = pair(fst(pair(a, b)), snd(pair(a, b)))$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ④ | step 2 and step 3 |

`Pair · pairing · components determine the pair`
