# FLOW Documentation

Welcome to the FLOW programming language documentation.

## Quick Start

| Goal | Document |
|------|----------|
| **Install & Run** | [Getting Started](getting-started.md) |
| **Compare with Rust/Zig/Go** | [Language Comparison](comparison.md) |
| **Learn FLOW** | [Tutorials](tutorials/beginner.md) |
| **Language Reference** | [Language Spec](LANGUAGE_SPEC.md) |
| **Standard Library** | [API Reference](library/stdlib-reference.md) |
| **See Examples** | [Examples](examples/README.md) |

## Documentation Structure

```
docs/
├── getting-started.md      # Installation, first program, commands
├── tutorials/              # Learning paths (beginner → advanced)
│   ├── beginner.md
│   ├── intermediate.md
│   └── advanced.md
├── language/               # Language features explained
│   ├── overview.md
│   ├── syntax.md
│   ├── types.md
│   └── ...
├── library/                # Standard library reference
│   └── stdlib-reference.md # Complete API documentation
├── examples/               # Working code examples
│   ├── basic/
│   ├── algorithms/
│   ├── effects/
│   └── gpu/
├── LANGUAGE_SPEC.md        # Authoritative language specification
└── DEVELOPMENT.md          # Compiler internals & contributing
```

## Build Documentation

```bash
# Install MkDocs
pip3 install mkdocs mkdocs-material pymdown-extensions

# Serve locally (auto-reload)
python3 -m mkdocs serve
# Open http://127.0.0.1:8000

# Build static HTML
python3 -m mkdocs build
# Output in site/

# Deploy to GitHub Pages
python3 -m mkdocs gh-deploy
```

## Status

| Component | Status |
|-----------|--------|
| Lexer/Parser | ✅ Complete |
| C Backend | ✅ Complete |
| MLIR Backend | ✅ Working |
| Effect System | ✅ Complete |
| Type System | ✅ Generics, Traits |
| LSP | ✅ Go-to-def, Hover |
| REPL | ✅ Interactive |
| Package Manager | ✅ Basic |
| GPU Codegen | ✅ Metal |
| Standard Library | ✅ Expanded |

---

*FLOW v0.3.0 — AI-Generated Language Infrastructure*
