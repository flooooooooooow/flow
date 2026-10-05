# Flow 2.0 Ergonomic Memory Safety Architecture

## Overview
Flow 2.0 aims to achieve compile-time spatial and temporal memory safety without verbose lifetime annotations or restrictive ownership constraints.

Tracker: GitHub epic [#679](https://github.com/flooooooooooow/flow/issues/679).
Design: [lifetime-domains.md](../language/lifetime-domains.md).

## Core Workstreams
1. Sound Lifetime Domain Propagation
2. Automated Aliasing and Borrow Inference
ROADMAP-SYNC: local-region-inference-and-automated-non-aliasing-proofs
3. Effect-Bounded Lifetimes and Capabilities
4. Tiered Safety Profiles and Formal Proofs

## Checklist

### Sound lifetime domain propagation

- [x] `@lifetime(...)` on functions and module statics
- [x] LD1 escape into a longer-lived static
- [x] LD2 escape by return
- [x] LD3 `callback` = `@rt_safe`; `frame` forbids heap create/destroy
- [x] LD4 call ordering between declared domains
- [x] `FrameArena` bump API
- [x] Interprocedural escape analysis without parameter annotations (#687)
- [x] Axiom §7 `request` and `persistent` domains
- [ ] Sound propagation through struct fields and collections (#684)
- [ ] Domain-bound allocation tracking for arenas and heap regions (#690)
- [ ] Escape through a call, closure, or heap cell (remaining gaps)
- [ ] Domains on parameters / in types
- [ ] `domain frame { ... }` blocks

### Automated aliasing and borrow inference

- [ ] Local region inference and automated non-aliasing proofs (#694)
- [ ] Value semantics with compiler-inferred move defaults (#696)

### Effect-bounded lifetimes and capabilities

- [x] Cross-module summaries for public functions (first slice, #765)
- [ ] Remaining `@rt_safe` / `@lifetime` summary gaps (#765)
- [ ] Reject `unknown` externs from `@rt_safe` / `callback`
- [ ] First-class RT-safe callable contracts for closures (#766)

### Tiered safety profiles and formal proofs

- [x] `safety` / `flight` profiles (loop bounds, recursion reject)
- [ ] `flight` no-heap / no-float subset
- [ ] Default lowering from domain to stack / arena / heap
- [ ] Formal proofs of the domain lattice rules
