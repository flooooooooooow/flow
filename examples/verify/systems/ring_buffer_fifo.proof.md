# ring_buffer_fifo

## Derived fact 1: Rb_matches_queue

> **Goal.** We're showing that queue order(rb) equals q.items.
>
> $$\forall rb \in RingBuffer \forall q \in Queue<i32>\quad \text{queue order}(rb) = q.items$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We can deduce that ring size(rb) equals q.len. | ① | $\text{ring size}(rb) = q.len$ |
| ② | We can deduce that queue order(rb) equals q.items. Hence proven. | ② | $\text{queue order}(rb) = q.items$ |

`rb_matches_queue`

## Derived fact 2: Push_preserves_fifo

> **Goal.** We're showing that rb matches queue(rb2, q2).
>
> $$\forall rb \in RingBuffer \forall q \in Queue<i32> \forall x \in \mathbb{Z}\quad \text{rb matches queue}(rb2, q2)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We invoke the derived fact: rb_matches_queue (instantiated for rb, q). |  |  |
| ② | We invoke the derived fact: not ring_is_full (instantiated for rb). |  |  |
| ③ | Let rb2 = ring_push(rb, x). |  |  |
| ④ | Let q2 = queue_push(q, x). |  |  |
| ⑤ | From step 1, step 2, step 3, and step 4, this implies rb matches queue(rb2, q2). Hence proven. | ⑤ | $\text{rb matches queue}(rb2, q2)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑤ | step 1, step 2, step 3, and step 4 |

`push_preserves_fifo`
