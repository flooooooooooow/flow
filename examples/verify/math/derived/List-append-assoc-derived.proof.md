# examples.verify.math.derived

*List append associativity as a derived law.*

**Source.** church — https://en.wikipedia.org/wiki/Associative_property

## Derived fact 1 — (xs ++ ys) ++ zs = xs ++ (ys ++ zs)

**Coordinate.** List · append · append associativity derived · **Derived fact**

*Source: church*

*Built on: parentheses do not matter, for append on List*

> **Goal.** (xs ++ ys) ++ zs = xs ++ (ys ++ zs)
>
> $$\forall xs \in List \forall ys \in List \forall zs \in List\quad (xs ++ ys) ++ zs = xs ++ (ys ++ zs)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that append associativity derived for append on List. |  |  |
| ② | We invoke the derived fact governing append on List: parentheses do not matter, for append on List (instantiated for xs, ys, zs). |  |  |
| ③ | From step 2, this implies (xs plus plus ys) plus plus zs equals xs plus plus (ys plus plus zs). Hence proven. | ③ | $(xs ++ ys) ++ zs = xs ++ (ys ++ zs)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |

`List · append · append associativity derived`
