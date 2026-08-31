# Flow 2.0 Memory Safety Roadmap

> Status: Internal design draft. Unlinked.

This document outlines the long-term exploration for Flow 2.0. The goal is full compile-time spatial and temporal memory safety without verbose lifetime annotations or restrictive ownership constraints.

---

## 1. Principles

1. **Zero Annotation Tax:** Code remains clean. The compiler infers lifetimes and aliasing rather than requiring explicit lifetime parameters on functions and types.
2. **Structural Freedom:** Common systems patterns like cyclic graphs, observers, self-referential structures, and arenas remain direct to express.
3. **Domain-Driven Lifetimes:** Memory validity ties to execution domains and scopes rather than individual variable bindings.
4. **Deterministic Teardown:** Resources clean up through structured domains, effects, and lexical scopes. No garbage collector.
5. **Escape Hatches with Boundaries:** Unchecked pointer operations remain available for low-level systems and hardware boundaries behind explicit markers.

---

## 2. Strategic Phases

### Phase 1: Sound Lifetime Domain Propagation

Expand the existing `@lifetime` domain hierarchy (`callback < frame < session < application`) into a sound, whole-program model.

- **Deep Struct and Field Tracking:** Propagate lifetime domains through struct fields, slices, and collections.
- **Interprocedural Escape Analysis:** Track reference passing across function boundaries without requiring user-written domain annotations on every parameter.
- **Arena-Bound Types:** Tie heap and arena allocations to their originating domain scope so references cannot outlive their backing storage.

---

### Phase 2: Automated Aliasing and Borrow Inference

Provide temporal safety without manual borrow annotations.

- **Local Region Inference:** Use compiler analysis to synthesize region boundaries and prove non-aliasing automatically.
- **Value Semantics with Move Defaults:** Treat data as independent values by default. Use destructive moves or shared references when safety can be proven.
- **Spans as Safe Views:** Make `span<T>` the standard borrow primitive across all APIs, backed by compile-time bounds and lifetime proofs.

---

### Phase 3: Effect-Bounded Lifetimes and Capabilities

Connect resource management to Flow's algebraic effect system.

- **Capability-Gated Allocation:** Model memory pools, device memory, and custom allocators as capabilities.
- **Scoped Teardown Handlers:** Handlers clean up all resources created within their scope upon exit.
- **Linear Tokens for Hardware and FFI:** Use single-use tokens for peripheral registers, file descriptors, and foreign resource lifecycles.

---

### Phase 4: Tiered Safety Profiles and Formal Proofs

Provide configurable verification depth based on target environment.

- **Compiler Proving Engine:** Automatically prove spatial bounds and absence of use-after-free for safe subsets.
- **Checked Debug Lowering:** Insert lightweight assertions in debug builds when static proof cannot be fully completed.
- **Strict Verification Profile:** Reject unprovable patterns in mission-critical profiles such as flight and medical targets.
