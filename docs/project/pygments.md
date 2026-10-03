# Upstream Pygments Lexer Registration

This document outlines the Pygments lexer implementation for **Flow** and the procedure for upstreaming it to [pygments/pygments](https://github.com/pygments/pygments).

## Status

| Check | Result |
|-------|--------|
| Lexer implementation | `src/flow/pygments_lexer.py` (`FlowLexer`) |
| Entry point registered | `pyproject.toml` under `[project.entry-points."pygments.lexers"]` |
| Aliases | `flow`, `flow-lang` |
| File extensions | `*.flow` |
| MIME types | `text/x-flow` |
| Upstream Pygments status | Prepared locally for submission |

## Local Usage

When `flow-lang` is installed in Python (`pip install -e .`), Pygments automatically discovers `FlowLexer` via entry points:

```python
from pygments.lexers import get_lexer_by_name
from pygments import highlight
from pygments.formatters import HtmlFormatter

lexer = get_lexer_by_name("flow")
code = 'function main() -> i32 { return 0 }'
html = highlight(code, lexer, HtmlFormatter())
```

You can also import the lexer directly:

```python
from flow.pygments_lexer import FlowLexer

lexer = FlowLexer()
```

## Upstreaming Procedure

To submit Flow's lexer directly to upstream Pygments:

1. **Fork `pygments/pygments`**
   Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/pygments.git
   cd pygments
   ```

2. **Add `FlowLexer` to Pygments**
   Create `pygments/lexers/flow.py` with the contents from `src/flow/pygments_lexer.py`.

3. **Register `FlowLexer` in Pygments Lexer Registry**
   Add `FlowLexer` to `pygments/lexers/_mapping.py` or export it in `pygments/lexers/__init__.py`.

4. **Add Lexer Tests**
   Add test samples in `tests/examplefiles/flow/` and regex/token unit tests in `tests/test_flow.py`.

5. **Submit Pull Request**
   Open a pull request against `pygments/pygments:master`.
