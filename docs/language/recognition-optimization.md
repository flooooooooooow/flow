# Recognition-safe learned optimisation

Flow separates semantic admissibility from optimization policy.

A candidate may come from a deterministic heuristic, an ML cost model, reinforcement learning, autotuning, beam search, or speculative branch exploration. None of those mechanisms defines correctness.

For source P, candidate C, and protected recognition domains Q, C is admissible only when every protected projection is preserved. The policy ranks only the admissible set.

This permits many lowering families to coexist: C, MLIR CPU, Metal, WGSL/WebGPU, MLIR GPU/SPIR-V, Python, JS, WASM, and future targets.

## Optimization branch prediction

A modern optimizer may fork several futures: inline then vectorize, fuse then CPU, tile then GPU, tensor-core lowering, or other sequences. Every frontier state carries recognition signatures. A branch that violates a protected domain is pruned immediately. Surviving branches may be ranked by latency, code size, energy, memory, compile time, profile data, or a learned value function.

## Recognition refinement

The recognition lattice adds a refinement relation. A fine observer refines a coarse observer when equality under the fine observer implies equality under the coarse observer. Finite compiler corpora can falsify this relation now; proof artifacts can establish stronger results later.

A residual witness exists when the coarse observer considers two programs equal while the fine observer distinguishes them. This makes information erased by a semantic regime explicit.

## Neural policies

Neural models are adapters, not trusted dependencies. CallablePolicy accepts any inference function returning a score. That function can later be backed by TFLite, ONNX Runtime, MLX, native Flow inference, or an external training process. The semantic gate is unchanged.

This follows the useful separation used by LLVM MLGO: learned models replace selected optimization heuristics while compiler logic retains correctness constraints. Flow extends that separation across multiple simultaneous semantic observers and lowering families.
