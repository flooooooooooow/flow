# ring_buffer_fifo

## Derived fact 8 — Rb_matches_queue

> **Goal.** We're showing that queue_order(rb) equals q.items.
>
> $$\forall rb \in Queue<i32>,\; queue_order(rb) = q.items$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We can deduce that ring_size(rb) equals q.len. | ① | $ring_size(rb) = q.len$ |
| ② | We can deduce that queue_order(rb) equals q.items. Hence proven. | ② | $queue_order(rb) = q.items$ |

`rb_matches_queue`

## Derived fact 9 — Push_preserves_fifo

> **Goal.** We're showing that rb_matches_queue(rb2, q2).
>
> $$\forall rb \in \mathbb{Z},\; rb_matches_queue(rb2, q2)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | We invoke the derived fact: rb_matches_queue (instantiated for rb, q). |  |  |
| ② | We invoke the derived fact: not ring_is_full (instantiated for rb). |  |  |
| ③ | Let rb2 = ring_push(rb, x). |  |  |
| ④ | Let q2 = queue_push(q, x). |  |  |
| ⑤ | From ①, ②, ③, and ④, this implies rb_matches_queue(rb2, q2). Hence proven. | ⑤ | $rb_matches_queue(rb2, q2)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑤ | ①, ②, ③, and ④ |

`push_preserves_fifo`
