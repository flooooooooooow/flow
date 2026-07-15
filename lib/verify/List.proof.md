# verify.List

*List append definitions on finite sequences.*

**Source.** church — https://en.wikipedia.org/wiki/List_(abstract_data_type)

## Definition 1 — Appending the empty list on the left changes nothing

**Coordinate.** List · append · empty is the left identity · **Definition**

*Source: church*

> **Goal.** Appending the empty list on the left changes nothing
>
> $$\forall xs \in List\quad nil ++ xs = xs$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We stipulate empty is the left identity for append on List — this is a definition, not a derived fact. |  |  |
| ② | This follows directly from the definition: nil plus plus xs equals xs. Hence proven. | ② | $nil ++ xs = xs$ |

`List · append · empty is the left identity`

## Definition 2 — Appending a singleton prepends the head

**Coordinate.** List · append · singleton prepends the head · **Definition**

*Source: church*

> **Goal.** Appending a singleton prepends the head
>
> $$\forall x \in \mathbb{N} \forall xs \in List\quad cons(x, nil) ++ xs = cons(x, xs)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We stipulate singleton prepends the head for append on List — this is a definition, not a derived fact. |  |  |
| ② | This follows directly from the definition: cons(x, nil) plus plus xs equals cons(x, xs). Hence proven. | ② | $cons(x, nil) ++ xs = cons(x, xs)$ |

`List · append · singleton prepends the head`
