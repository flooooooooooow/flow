# flow-pygments

Pygments lexer plugin for Flow.

## Local test

```bash
cd third_party/integrations/pygments-flow
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
python test_lexer.py
pygmentize -L lexers | grep -i flow
```

## Upstream path

This package is intentionally small enough to translate directly into a Pygments upstream contribution. Once the lexer has been exercised on the Flow example corpus, submit `FlowLexer` to Pygments with `*.flow`, aliases `flow` / `flowlang`, and representative tests.

Until that is merged, projects can install this directory as an ordinary Pygments plugin.
