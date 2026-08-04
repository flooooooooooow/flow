# Language Spec Index

Navigable table of contents for the full [LANGUAGE_SPEC.md](../LANGUAGE_SPEC.md) (authoritative reference), plus links to focused Language Reference pages.

> Prefer the focused pages for learning; use the full spec for status matrices and edge cases.

## Full specification

| Spec section | Anchors | Focused page |
|--------------|---------|--------------|
| [Overview](../LANGUAGE_SPEC.md#overview) | — | [Overview](overview.md) |
| [Quick Reference](../LANGUAGE_SPEC.md#quick-reference) | Commands | [Getting Started](../getting-started.md) |
| [1. Lexical Structure](../LANGUAGE_SPEC.md#1-lexical-structure) | [Keywords](../LANGUAGE_SPEC.md#11-keywords) · [Operators](../LANGUAGE_SPEC.md#12-operators) · [Literals](../LANGUAGE_SPEC.md#13-literals) · [Comments](../LANGUAGE_SPEC.md#14-comments) | [Syntax](syntax.md) · [Grammar](grammar.md) |
| [2. Types](../LANGUAGE_SPEC.md#2-types) | [Primitives](../LANGUAGE_SPEC.md#21-primitive-types) · [Composite](../LANGUAGE_SPEC.md#22-composite-types) · [Syntax](../LANGUAGE_SPEC.md#23-type-syntax) · [Aliases](../LANGUAGE_SPEC.md#24-type-aliases-and-distinct-types) · [Casts](../LANGUAGE_SPEC.md#25-explicit-casts) | [Types](types.md) |
| [3. Declarations](../LANGUAGE_SPEC.md#3-declarations) | [Functions](../LANGUAGE_SPEC.md#31-function-declaration) · [Variables](../LANGUAGE_SPEC.md#32-variable-declaration) · [Constants](../LANGUAGE_SPEC.md#33-constant-declaration) · [Structs](../LANGUAGE_SPEC.md#34-struct-declaration) · [Extern](../LANGUAGE_SPEC.md#35-extern-declaration) | [Functions](functions.md) · [Variables](variables.md) |
| [4. Expressions](../LANGUAGE_SPEC.md#4-expressions) | [Expression types](../LANGUAGE_SPEC.md#41-expression-types) · [Precedence](../LANGUAGE_SPEC.md#42-operator-precedence-highest-to-lowest) · [Built-ins](../LANGUAGE_SPEC.md#43-built-in-functions) | [Syntax](syntax.md) |
| [5. Statements](../LANGUAGE_SPEC.md#5-statements) | [If](../LANGUAGE_SPEC.md#52-if-statement) · [While](../LANGUAGE_SPEC.md#53-while-loop) · [For](../LANGUAGE_SPEC.md#54-for-loop) · [Concurrency](../LANGUAGE_SPEC.md#56-concurrency-language--stdlib) · [Return](../LANGUAGE_SPEC.md#55-return-statement) | [Syntax](syntax.md) · [Concurrency vs Go](concurrency-vs-go.md) |
| [6. Effect System](../LANGUAGE_SPEC.md#6-effect-system) | [Effect](../LANGUAGE_SPEC.md#61-effect-declaration) · [Capability](../LANGUAGE_SPEC.md#62-capability-declaration) · [Handle](../LANGUAGE_SPEC.md#63-handle-statement) · [Effect rows](../LANGUAGE_SPEC.md#631-signature-effect-rows) · [Details](../LANGUAGE_SPEC.md#64-effect-implementation-details) | [Effects Showcase](../effects-showcase.md) · [Async via Effects](async-effects.md) |
| [7. Module System](../LANGUAGE_SPEC.md#7-module-system) | [Import](../LANGUAGE_SPEC.md#71-import-declaration) · [Export](../LANGUAGE_SPEC.md#72-export-declaration) · [Resolution](../LANGUAGE_SPEC.md#73-module-resolution) | [Modules](modules.md) |
| [8. Memory Model](../LANGUAGE_SPEC.md#8-memory-model) | [Value semantics](../LANGUAGE_SPEC.md#81-value-semantics) · [Stack vs heap](../LANGUAGE_SPEC.md#82-stack-vs-heap) · [Pointers](../LANGUAGE_SPEC.md#83-pointer-operations) | [Memory (stdlib)](../library/memory.md) |
| [9. Compilation Targets](../LANGUAGE_SPEC.md#9-compilation-targets) | [C](../LANGUAGE_SPEC.md#91-c-backend) · [MLIR](../LANGUAGE_SPEC.md#92-mlir-backend) · [Wasm](../LANGUAGE_SPEC.md#93-webassembly) · [JIT](../LANGUAGE_SPEC.md#94-jit-execution) | — |

## Appendices (spec only)

- [Appendix A: AST Node Reference](../LANGUAGE_SPEC.md#appendix-a-ast-node-reference)
- [Appendix B: C Generator Capabilities](../LANGUAGE_SPEC.md#appendix-b-c-generator-capabilities)
- [Appendix C: Feature Implementation Matrix](../LANGUAGE_SPEC.md#appendix-c-feature-implementation-matrix)

## Related reference pages

| Page | Topic |
|------|-------|
| [Formal EBNF](../grammar.ebnf) | Machine-readable grammar |
| [Graphics](graphics.md) | Native 2D graphics + platform matrix |
| [Shaders](shaders.md) | Fill-shader surface language |
| [Async via Effects](async-effects.md) | FiberAsync / ThreadedAsync / NetpollAsyncIO |
| [Concurrency vs Go](concurrency-vs-go.md) | Channels, fibers, OpenMP, benches |
| [Replacing Go](replace-go.md) | Scorecard for Go-shaped workloads |
| [Debugging](debugging.md) | `./flow debug` + `#line` / LLDB |
| [Verification](verification.md) | Proof / claim system |
| [Design Notes](language_design.md) | Rationale |
| [Language README](README.md) | Short learning TOC |

## Open the full document

→ **[LANGUAGE_SPEC.md](../LANGUAGE_SPEC.md)**
