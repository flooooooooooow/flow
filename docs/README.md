# Flow Documentation

<img src="assets/flow-mascot.png" alt="Flowy the Hedgehog" width="200" align="right">

Welcome to the Flow programming language documentation!

## Quick Links

| Document | Description |
|----------|-------------|
| **[Getting Started](getting-started.md)** | Installation and first program |
| **[Language Spec](LANGUAGE_SPEC.md)** | Complete language reference |
| **[Grammar](grammar.ebnf)** | Formal EBNF grammar |

## Language Reference

- [Overview](language/overview.md) - Language philosophy and features
- [Syntax](language/syntax.md) - Lexical structure and grammar
- [Types](language/types.md) - Type system
- [Functions](language/functions.md) - Function definitions
- [Variables](language/variables.md) - Variables and mutability
- [Graphics](language/graphics.md) - Native graphics API

## Standard Library

- [Core](library/core.md) - Built-in functions
- [Autodiff](library/autodiff.md) - Automatic differentiation
- [Audio DSP](library/audio.md) - Real-time audio DSP utilities
- [Memory](library/memory.md) - Memory management

## Third-Party Libraries

- [Overview](third-party/README.md) - Packages outside the core stdlib
- [flow-verify](third-party/flow-verify.md) - Formal math proofs and Claim Paths
- [Proof Catalog](third-party/flow-verify-catalog.md) - Auto-generated proof index

## Documentation Project

- [Wiki Strategy](wiki-strategy.md) - Long-term documentation architecture
- [Wiki Roadmap](wiki-roadmap.md) - Phased wiki delivery plan

## Verification

- [Verification Design](language/verification.md) - `theorem` / `therefore` language spec
- [Epistemology](language/epistemology.md) - Claim Path grammar
- [Proof Book](language/math-proof-book.md) - Numbered proof book plan
- [Mathlib Roadmap](language/mathlib-equivalence-toc.md) - Mathlib parity TOC

## Tutorials

- [Beginner](tutorials/beginner.md) - Learn the basics
- [Intermediate](tutorials/intermediate.md) - Deeper concepts
- [Advanced](tutorials/advanced.md) - Expert techniques

## Project

- [Contributing](project/CONTRIBUTING.md) - How to contribute, security policy
- [Changelog](project/CHANGELOG.md) - Version history and audit fixes
- [What's Next](NEXT.md) - Prioritized roadmap after v0.7.0 audit
- [Audit Report (2026-02-10)](project/AUDIT_2026-02-10.md) - Latest full audit findings
- [Development](DEVELOPMENT.md) - Building Flow

## Examples

All examples are in the [`examples/`](../examples/) directory:

```
examples/
├── basics/           # Hello world, fibonacci, etc.
├── games/            # Tetris, 2048 with graphics
├── ml/               # Machine learning framework
├── effects/          # Algebraic effects demos
├── neural_networks/  # Autodiff and backprop
└── ...
```

Run any example:

```bash
./flow run examples/basics/hello_world.flow
```
