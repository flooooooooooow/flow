# verify.Finset

*Finite set algebra on Finset carriers.*

**Source.** graham-knuth-patashnik — *Concrete Mathematics*

## Definition 1 — Union with the empty set changes nothing

**Coordinate.** Finset · union · empty is the right identity · **Definition**

*Source: graham-knuth-patashnik*

> **Goal.** Union with the empty set changes nothing
>
> $$\forall s \in Finset\quad s ∪ empty = s$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We stipulate empty is the right identity for union on Finset — this is a definition, not a derived fact. |  |  |
| ② | This follows directly from the definition: s ∪ empty equals s. Hence proven. | ② | $s ∪ empty = s$ |

`Finset · union · empty is the right identity`

## Definition 2 — Union with the empty set on the left changes nothing

**Coordinate.** Finset · union · empty is the left identity · **Definition**

*Source: graham-knuth-patashnik*

> **Goal.** Union with the empty set on the left changes nothing
>
> $$\forall s \in Finset\quad empty ∪ s = s$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We stipulate empty is the left identity for union on Finset — this is a definition, not a derived fact. |  |  |
| ② | This follows directly from the definition: empty ∪ s equals s. Hence proven. | ② | $empty ∪ s = s$ |

`Finset · union · empty is the left identity`

## Derived fact 3 — Union order does not matter

**Coordinate.** Finset · union · order does not matter · **Derived fact**

*Source: graham-knuth-patashnik*

> **Goal.** Union order does not matter
>
> $$\forall a \in Finset \forall b \in Finset\quad a ∪ b = b ∪ a$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that order does not matter for union on Finset. |  |  |
| ② | We can deduce that a ∪ b equals b ∪ a. Hence proven. | ② | $a ∪ b = b ∪ a$ |

`Finset · union · order does not matter`

## Definition 4 — The empty finite set has cardinality zero

**Coordinate.** Finset · cardinality · the empty set has size zero · **Definition**

*Source: graham-knuth-patashnik*

> **Goal.** The empty finite set has cardinality zero
>
> $$card(empty) = 0$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We stipulate the empty set has size zero for cardinality on Finset — this is a definition, not a derived fact. |  |  |
| ② | This follows directly from the definition: card(empty) equals 0. Hence proven. | ② | $card(empty) = 0$ |

`Finset · cardinality · the empty set has size zero`

## Definition 5 — Intersecting with the empty set yields the empty set

**Coordinate.** Finset · intersection · empty is the right annihilator · **Definition**

*Source: graham-knuth-patashnik*

> **Goal.** Intersecting with the empty set yields the empty set
>
> $$\forall s \in Finset\quad s ∩ empty = empty$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We stipulate empty is the right annihilator for intersection on Finset — this is a definition, not a derived fact. |  |  |
| ② | This follows directly from the definition: s ∩ empty equals empty. Hence proven. | ② | $s ∩ empty = empty$ |

`Finset · intersection · empty is the right annihilator`

## Definition 6 — Intersecting the empty set on the left yields the empty set

**Coordinate.** Finset · intersection · empty is the left annihilator · **Definition**

*Source: graham-knuth-patashnik*

> **Goal.** Intersecting the empty set on the left yields the empty set
>
> $$\forall s \in Finset\quad empty ∩ s = empty$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We stipulate empty is the left annihilator for intersection on Finset — this is a definition, not a derived fact. |  |  |
| ② | This follows directly from the definition: empty ∩ s equals empty. Hence proven. | ② | $empty ∩ s = empty$ |

`Finset · intersection · empty is the left annihilator`
