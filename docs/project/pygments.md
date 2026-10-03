# Pygments — Flow Language Support

Goal: register the **Flow** programming language (`.flow`, `flow`, `flow-lang`) with [pygments/pygments](https://github.com/pygments/pygments) for syntax highlighting across Python-based documentation engines, MkDocs, Sphinx, and code review platforms.

## Current Status

A local Pygments lexer implementation is provided in `src/flow/pygments_lexer.py` (`FlowLexer`). Unit tests in `tests/unit/test_pygments_lexer.py` verify syntax highlighting for keywords, primitive types, function definitions, algebraic effects, numbers, strings, comments, and attributes.

## Upstream Contribution Plan

The upstreaming process for `FlowLexer` into official Pygments consists of:

1. Submitting a Pull Request to [pygments/pygments](https://github.com/pygments/pygments) placing `FlowLexer` in `pygments/lexers/flow.py`.
2. Registering `FlowLexer` in `pygments/lexers/_mapping.py` or entry points.
3. Adding test samples in `tests/examplefiles/flow/` and `tests/snippets/flow/`.

For complete maintainer instructions on opening the Pygments PR, see [docs/project/pygments/UPSTREAM.md](pygments/UPSTREAM.md).
