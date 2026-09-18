# Pygments lexer for Flow

This directory carries an upstream-ready lexer implementation for Flow.

It is not vendored into Pygments at runtime. The purpose is to keep the exact lexer and metadata ready for a contribution to `pygments/pygments`, while giving documentation systems a reference implementation today.

Upstream metadata:

```text
Name: Flow
Aliases: flow
Filenames: *.flow
MIME: text/x-flow
Lexer class: FlowLexer
```

Before upstream submission, run the Pygments test suite against the current upstream checkout and add the lexer entry using Pygments' current plugin/registry conventions.
