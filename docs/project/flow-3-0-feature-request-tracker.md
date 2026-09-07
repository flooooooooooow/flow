# Flow 3.0 feature request tracker

This issue is the top-level intake and design tracker for language and compiler ideas targeted at Flow 3.0. Inclusion here means the idea is worth carrying as a 3.0 design candidate; it does not by itself mean syntax or semantics are frozen.

| Feature request | Scope | Status |
|---|---|---|
| #723 Structural Orchestration Algebra | Syntax-native composition graphs, structural concurrency, typed failure/fallback, deadlines, retry, quorum/race, cancellation, transactional regions, compensation, constraints, resource contracts and graph-aware lowering | PRD drafted; design review required |

## Version 3.0 design rule

Flow 3.0 proposals should aim to increase compiler-visible semantic structure while reducing user-visible plumbing. New syntax should earn its place by making complex systems easier to read, verify, optimize or deploy, rather than merely shortening existing library calls.

## Tracker maintenance

New 3.0 feature requests should use a `[Flow 3.0 Feature Request]` title, carry a stable `ROADMAP-SYNC` key, state whether they change syntax/semantics/IR/backends, and link back to this tracker. Once a proposal is accepted, its row here should move from design candidate to an implementation phase or dedicated epic.
