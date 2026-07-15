# examples.verify.math.derived

*Reversing a singleton list is that singleton.*

**Source.** List reverse cons

## Derived fact 1 — Reversing a singleton list is that singleton

**Coordinate.** List · reverse · append singleton · **Derived fact**

*Source: List reverse cons*

*Built on: append singleton, for reverse on List*

> **Goal.** Reversing a singleton list is that singleton
>
> $$\forall x \in \guillemotleft{}List\guillemotright{} \guillemotleft{}Nat\guillemotright{}\quad «List» «reverse» «cons»(x, «List» «empty») = «List» «cons»(x, «List» «empty»)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We prove that append singleton for reverse on List. |  |  |
| ② | We invoke the derived fact governing reverse on List: cons, for reverse on List (instantiated for x, «List» «empty») = «List» «cons»(x, «List» «empty»). |  |  |
| ③ | From step 2, this implies «List» «reverse» «cons»(x, «List» «empty») equals «List» «cons»(x, «List» «empty»). Hence proven. | ③ | $«List» «reverse» «cons»(x, «List» «empty») = «List» «cons»(x, «List» «empty»)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ③ | step 2 |

`List · reverse · append singleton`
