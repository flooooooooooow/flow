# verify.Nat-core

*Peano predecessor and successor structural laws.*

**Source.** peano — https://en.wikipedia.org/wiki/Peano_axioms

## Definition 1 — Taking predecessor after successor returns the same number

**Coordinate.** the natural numbers · predecessor · predecessor undoes successor · **Definition**

*Source: peano*

> **Goal.** Taking predecessor after successor returns the same number.  pred(succ(n)) = n
>
> $$\forall n \in \mathbb{N}\quad pred(\mathrm{succ}(n)) = n$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We stipulate predecessor undoes successor for predecessor on the natural numbers — this is a definition, not a derived fact. |  |  |
| ② | This follows directly from the definition: pred(the successor of n) equals n. Hence proven. | ② | $pred(\mathrm{succ}(n)) = n$ |

`the natural numbers · predecessor · predecessor undoes successor`

## Definition 2 — For a nonzero natural, successor after predecessor recovers the number

**Coordinate.** the natural numbers · successor · successor undoes predecessor away from zero · **Definition**

*Source: peano*

> **Goal.** For a nonzero natural, successor after predecessor recovers the number
>
> $$\forall n \in \mathbb{N}\quad \mathrm{succ}(pred(n)) = n$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We stipulate successor undoes predecessor away from zero for successor on the natural numbers — this is a definition, not a derived fact. |  |  |
| ② | We split into exhaustive cases — the claim must hold in each one. |  |  |
| ③ | Case 1 (see step 2): suppose n is zero. |  |  |
| ④ | From step 3, this implies the successor of pred(n) equals n in this case. | ④ | $\mathrm{succ}(pred(n)) = n$ |
| ⑤ | Case 2 (see step 2): neither disjunct holds. |  |  |
| ⑥ | Let k denote the predecessor of n. |  |  |
| ⑦ | We invoke the definitional clause governing predecessor on the natural numbers: predecessor undoes successor, for predecessor on the natural numbers (instantiated for k). |  |  |
| ⑧ | From step 5, step 6, and step 7, this implies the successor of pred(n) equals n. Together with the other cases (step 3 and step 5), the goal is discharged. Hence proven. | ⑧ | $\mathrm{succ}(pred(n)) = n$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |
| ④ | step 3 |
| ⑤ | step 2 |
| ⑧ | step 5, step 6, and step 7 |

`the natural numbers · successor · successor undoes predecessor away from zero`

## Derived fact 3 — If two successors match, the originals match

**Coordinate.** the natural numbers · successor · successor is injective · **Derived fact**

*Source: peano — https://en.wikipedia.org/wiki/Injective_function*

*Built on: predecessor undoes successor, for predecessor on the natural numbers*

> **Goal.** If two successors match, the originals match.  succ(m) = succ(n) → m = n
>
> $$\forall m \in \mathbb{N} \forall n \in \mathbb{N}\quad m = n$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that successor is injective for successor on the natural numbers. |  |  |
| ② | We split into exhaustive cases — the claim must hold in each one. |  |  |
| ③ | Case 1 (see step 2): suppose succ(m)  equals  succ(n). |  |  |
| ④ | We invoke the definitional clause governing predecessor on the natural numbers: predecessor undoes successor, for predecessor on the natural numbers (instantiated for m). |  |  |
| ⑤ | We invoke the definitional clause governing predecessor on the natural numbers: predecessor undoes successor, for predecessor on the natural numbers (instantiated for n). |  |  |
| ⑥ | From step 3, step 4, and step 5, this implies m equals n. Together with the other cases (step 3), the goal is discharged. Hence proven. | ⑥ | $m = n$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |
| ⑥ | step 3, step 4, and step 5 |

`the natural numbers · successor · successor is injective`

## Derived fact 4 — Zero is never the successor of any natural number

**Coordinate.** the natural numbers · zero · zero is not a successor · **Derived fact**

*Source: peano*

*Built on: predecessor undoes successor, for predecessor on the natural numbers*

> **Goal.** Zero is never the successor of any natural number
>
> $$\forall n \in \mathbb{N}\quad pred(0) = n$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that zero is not a successor for zero on the natural numbers. |  |  |
| ② | We split into exhaustive cases — the claim must hold in each one. |  |  |
| ③ | Case 1 (see step 2): suppose 0  equals  succ(n). |  |  |
| ④ | We invoke the definitional clause governing predecessor on the natural numbers: predecessor undoes successor, for predecessor on the natural numbers (instantiated for n). |  |  |
| ⑤ | From step 3 and step 4, this implies pred(0) equals n. Together with the other cases (step 3), the goal is discharged. Hence proven. | ⑤ | $pred(0) = n$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |
| ⑤ | step 3 and step 4 |

`the natural numbers · zero · zero is not a successor`

## Derived fact 5 — Successor never produces zero

**Coordinate.** the natural numbers · successor · successor never yields zero · **Derived fact**

*Source: peano*

*Built on: zero is not a successor, for zero on the natural numbers*

> **Goal.** Successor never produces zero
>
> $$\forall n \in \mathbb{N}\quad \mathrm{succ}(n) != 0$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that successor never yields zero for successor on the natural numbers. |  |  |
| ② | We split into exhaustive cases — the claim must hold in each one. |  |  |
| ③ | Case 1 (see step 2): suppose succ(n)  equals  0. |  |  |
| ④ | We invoke the derived fact governing zero on the natural numbers: zero is not a successor, for zero on the natural numbers (instantiated for n). |  |  |
| ⑤ | From step 3 and step 4, this implies the successor of n ! equals 0 in this case. | ⑤ | $\mathrm{succ}(n) != 0$ |
| ⑥ | Case 2 (see step 2): neither disjunct holds. |  |  |
| ⑦ | From step 6, this implies the successor of n ! equals 0. Together with the other cases (step 3 and step 6), the goal is discharged. Hence proven. | ⑦ | $\mathrm{succ}(n) != 0$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |
| ⑤ | step 3 and step 4 |
| ⑥ | step 2 |
| ⑦ | step 6 |

`the natural numbers · successor · successor never yields zero`

## Derived fact 6 — Every natural is either zero or the successor of some natural

**Coordinate.** the natural numbers · cases · every number is zero or a successor · **Derived fact**

*Source: peano*

*Built on: predecessor undoes successor, for predecessor on the natural numbers*

> **Goal.** Every natural is either zero or the successor of some natural
>
> $$\forall n \in \mathbb{N}\quad n = \mathrm{succ}(k)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that every number is zero or a successor for cases on the natural numbers. |  |  |
| ② | We split into exhaustive cases — the claim must hold in each one. |  |  |
| ③ | Case 1 (see step 2): suppose n is zero. |  |  |
| ④ | From step 3, this implies n equals 0 in this case. | ④ | $n = 0$ |
| ⑤ | Case 2 (see step 2): neither disjunct holds. |  |  |
| ⑥ | Let k denote the predecessor of n. |  |  |
| ⑦ | We invoke the definitional clause governing predecessor on the natural numbers: predecessor undoes successor, for predecessor on the natural numbers (instantiated for k). |  |  |
| ⑧ | From step 5, step 6, and step 7, this implies n equals the successor of k. Together with the other cases (step 3 and step 5), the goal is discharged. Hence proven. | ⑧ | $n = \mathrm{succ}(k)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |
| ④ | step 3 |
| ⑤ | step 2 |
| ⑧ | step 5, step 6, and step 7 |

`the natural numbers · cases · every number is zero or a successor`
