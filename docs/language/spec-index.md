# Language Spec Index

Navigable table of contents for the full [LANGUAGE_SPEC.md](../LANGUAGE_SPEC.md) (authoritative reference), plus links to focused Language Reference pages.

> Prefer the focused pages for learning; use the full spec for status matrices and edge cases.
> Spec version **0.3.4** (2026-08-05).

## Full specification

| Spec section | Anchors | Focused page |
|--------------|---------|--------------|
| [Overview](../LANGUAGE_SPEC.md#overview) | — | [Overview](overview.md) |
| [Quick Reference](../LANGUAGE_SPEC.md#quick-reference) | Commands | [Getting Started](../getting-started.md) |
| [1. Lexical Structure](../LANGUAGE_SPEC.md#1-lexical-structure) | [Keywords](../LANGUAGE_SPEC.md#11-keywords) · [Operators](../LANGUAGE_SPEC.md#12-operators) · [Literals](../LANGUAGE_SPEC.md#13-literals) · [Comments](../LANGUAGE_SPEC.md#14-comments) | [Syntax](syntax.md) · [Grammar](grammar.md) |
| [2. Types](../LANGUAGE_SPEC.md#2-types) | [Primitives](../LANGUAGE_SPEC.md#21-primitive-types) · [Composite](../LANGUAGE_SPEC.md#22-composite-types) · [Aliases](../LANGUAGE_SPEC.md#24-type-aliases-and-distinct-types) · [Casts](../LANGUAGE_SPEC.md#25-explicit-casts) · [Units](../LANGUAGE_SPEC.md#26-units-of-measure) | [Types](types.md) |
| [3. Declarations](../LANGUAGE_SPEC.md#3-declarations) | [Functions](../LANGUAGE_SPEC.md#31-function-declaration) · [Variables](../LANGUAGE_SPEC.md#32-variable-declaration) · [Structs](../LANGUAGE_SPEC.md#34-struct-declaration) · [Extern](../LANGUAGE_SPEC.md#35-extern-declaration) · [Attributes](../LANGUAGE_SPEC.md#36-attributes) | [Functions](functions.md) · [Variables](variables.md) |
| [4. Expressions](../LANGUAGE_SPEC.md#4-expressions) | [Expression types](../LANGUAGE_SPEC.md#41-expression-types) · [Built-ins](../LANGUAGE_SPEC.md#43-built-in-functions) · [Lambdas](../LANGUAGE_SPEC.md#44-lambdas--closures) · [Pipe / ordering](../LANGUAGE_SPEC.md#45-pipe--declarative-ordering-and-search) | [Syntax](syntax.md) · [Ordering](ordering.md) · [Ranges](ranges.md) |
| [5. Statements](../LANGUAGE_SPEC.md#5-statements) | [If](../LANGUAGE_SPEC.md#52-if-statement) · [While](../LANGUAGE_SPEC.md#53-while-loop) · [For](../LANGUAGE_SPEC.md#54-for-loop) · [Concurrency](../LANGUAGE_SPEC.md#56-concurrency-language--stdlib) | [Syntax](syntax.md) · [Ranges](ranges.md) · [Concurrency vs Go](concurrency-vs-go.md) |
| [6. Effect System](../LANGUAGE_SPEC.md#6-effect-system) | [Effect](../LANGUAGE_SPEC.md#61-effect-declaration) · [Capability](../LANGUAGE_SPEC.md#62-capability-declaration) · [Handle](../LANGUAGE_SPEC.md#63-handle-statement) | [Effects Showcase](../effects-showcase.md) · [Async via Effects](async-effects.md) |
| [7. Module System](../LANGUAGE_SPEC.md#7-module-system) | [Import](../LANGUAGE_SPEC.md#71-import-declaration) · [Export](../LANGUAGE_SPEC.md#72-export-declaration) · [Re-export](../LANGUAGE_SPEC.md#73-re-export-declaration) · [Resolution](../LANGUAGE_SPEC.md#74-module-resolution) · [`module` blocks](../LANGUAGE_SPEC.md#75-module-blocks) | [Modules](modules.md) · [Namespacing](modules-namespacing.md) |
| [8. Memory Model](../LANGUAGE_SPEC.md#8-memory-model) | [Value semantics](../LANGUAGE_SPEC.md#81-value-semantics) · [Pointers](../LANGUAGE_SPEC.md#83-pointer-operations) | [Memory (stdlib)](../library/memory.md) |
| [9. Compilation Targets](../LANGUAGE_SPEC.md#9-compilation-targets) | [C](../LANGUAGE_SPEC.md#91-c-backend) · [MLIR](../LANGUAGE_SPEC.md#92-mlir-backend) · [Wasm](../LANGUAGE_SPEC.md#93-webassembly) · [JIT](../LANGUAGE_SPEC.md#94-jit-execution) | [MLIR opt flags](mlir-opt-flags.md) · [Wasm](wasm.md) |
| [10. Domain / DSL Surfaces](../LANGUAGE_SPEC.md#10-domain--dsl-surfaces) | [flow / evolves](../LANGUAGE_SPEC.md#101-flow--evolves-as--representation) · [Dynamics / LQR](../LANGUAGE_SPEC.md#102-dynamics--analyze--lqr) · [Field PDE](../LANGUAGE_SPEC.md#103-field--boundary--laplacian-pde) · [Shaders](../LANGUAGE_SPEC.md#104-fill-shaders) · [Graphics](../LANGUAGE_SPEC.md#105-native-graphics) · [GPU memory](../LANGUAGE_SPEC.md#106-gpu-memory-stdlib) | [Dynamics DSL](dynamics-dsl.md) · [North-star](../vision/north-star.md) · [Pattern adoption](../project/pattern-adoption.md) |

## Appendices (spec only)

- [Appendix A: AST Node Reference](../LANGUAGE_SPEC.md#appendix-a-ast-node-reference)
- [Appendix B: C Generator Capabilities](../LANGUAGE_SPEC.md#appendix-b-c-generator-capabilities)
- [Appendix C: Feature Implementation Matrix](../LANGUAGE_SPEC.md#appendix-c-feature-implementation-matrix)

## Related reference pages

| Page | Topic |
|------|-------|
| [Formal EBNF](../grammar.ebnf) | Machine-readable grammar |
| [Dynamics DSL](dynamics-dsl.md) | `dsys` / `analyze` / LQR expanders |
| [Declarative ordering](ordering.md) | `\|> sort` / `sortBy` |
| [Ranges and range algebra](ranges.md) | `a..b step c`, `sum`, `\|` / `&` on ranges |
| [North-star / evolves](../vision/north-star.md) | Evolution cards + units design |
| [Pattern adoption](../project/pattern-adoption.md) | Shipped DSL checklist |
| [Graphics](graphics.md) | Native 2D graphics + platform matrix |
| [Shaders](shaders.md) | Fill-shader surface language |
| [GPU memory](../library/gpu-memory.md) | Unified GPU buffers (Metal) |
| [RT-safety](../library/rt-safety.md) | `@rt_safe` |
| [Async via Effects](async-effects.md) | FiberAsync / ThreadedAsync / NetpollAsyncIO |
| [Concurrency vs Go](concurrency-vs-go.md) | Channels, fibers, OpenMP, benches |
| [Replacing Go](replace-go.md) | Scorecard for Go-shaped workloads |
| [Debugging](debugging.md) | `./flow debug` + `#line` / LLDB |
| [Verification](verification.md) | Proof / claim system |
| [Design Notes](language_design.md) | Rationale |
| [Language README](README.md) | Short learning TOC |

## Open the full document

→ **[LANGUAGE_SPEC.md](../LANGUAGE_SPEC.md)**
