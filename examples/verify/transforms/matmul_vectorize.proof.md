# matmul_vectorize

## Derived fact 1: Matmul_vectorized_correct

> **Goal.** We're showing that matrices equal(C naive, C fast, m, n).
>
> $$\forall m \in \mathbb{Z} \forall n \in \mathbb{Z} \forall k \in \mathbb{Z}\quad \text{matrices equal}(\text{C naive}, \text{C fast}, m, n)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | Let A = arbitrary_f32_matrix(m, k). |  |  |
| ② | Let B = arbitrary_f32_matrix(k, n). |  |  |
| ③ | Let C_naive = f32_matrix_zeros(m, n). |  |  |
| ④ | Let C_fast = f32_matrix_zeros(m, n). |  |  |
| ⑤ | From step 1, step 2, step 3, and step 4, this implies matrices equal(C naive, C fast, m, n). Hence proven. | ⑤ | $\text{matrices equal}(\text{C naive}, \text{C fast}, m, n)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑤ | step 1, step 2, step 3, and step 4 |

`matmul_vectorized_correct`

## Derived fact 2: Loop_fusion_correct

> **Goal.** We're showing that memory equal(σ_separate, σ_fused).
>
> $$\forall n \in \mathbb{Z}\quad \text{memory equal}(σ_separate, σ_fused)$$

| | **Proof** | | **Math** |
|:---:|:---|:---:|:---|
| ① | Let σ = arbitrary_memory(). |  |  |
| ② | Let a = fresh_array(n). |  |  |
| ③ | Let b = fresh_array(n). |  |  |
| ④ | Let σ_separate = run_separate_loops(σ, a, b, n). |  |  |
| ⑤ | Let σ_fused = run_fused_loop(σ, a, b, n). |  |  |
| ⑥ | From step 1, step 2, step 3, step 4, and step 5, this implies memory equal(σ_separate, σ_fused). Hence proven. | ⑥ | $\text{memory equal}(σ_separate, σ_fused)$ |

**Trace.** Each step lists the earlier steps it depends on.

| Step | Uses |
|:---:|:---|
| ⑥ | step 1, step 2, step 3, step 4, and step 5 |

`loop_fusion_correct`
