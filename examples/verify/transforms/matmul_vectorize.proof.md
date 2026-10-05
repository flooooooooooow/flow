# matmul_vectorize

## Derived fact 10 — Matmul_vectorized_correct

> **Goal.** We're showing that matrices_equal(C_naive, C_fast, m, n).
>
> $$\forall m \in \mathbb{Z},\; matrices_equal(C_naive, C_fast, m, n)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | Let A = arbitrary_f32_matrix(m, k). |  |  |
| ② | Let B = arbitrary_f32_matrix(k, n). |  |  |
| ③ | Let C_naive = f32_matrix_zeros(m, n). |  |  |
| ④ | Let C_fast = f32_matrix_zeros(m, n). |  |  |
| ⑤ | From ①, ②, ③, and ④, this implies matrices_equal(C_naive, C_fast, m, n). Hence proven. | ⑤ | $matrices_equal(C_naive, C_fast, m, n)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑤ | ①, ②, ③, and ④ |

`matmul_vectorized_correct`

## Derived fact 11 — Loop_fusion_correct

> **Goal.** We're showing that memory_equal(σ_separate, σ_fused).
>
> $$\forall n \in \mathbb{Z},\; memory_equal(σ_separate, σ_fused)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | Let σ = arbitrary_memory(). |  |  |
| ② | Let a = fresh_array(n). |  |  |
| ③ | Let b = fresh_array(n). |  |  |
| ④ | Let σ_separate = run_separate_loops(σ, a, b, n). |  |  |
| ⑤ | Let σ_fused = run_fused_loop(σ, a, b, n). |  |  |
| ⑥ | From ①, ②, ③, ④, and ⑤, this implies memory_equal(σ_separate, σ_fused). Hence proven. | ⑥ | $memory_equal(σ_separate, σ_fused)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑥ | ①, ②, ③, ④, and ⑤ |

`loop_fusion_correct`
