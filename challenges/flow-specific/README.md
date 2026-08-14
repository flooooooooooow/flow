# Flow-specific coding challenges

The full series is printed as Chapter 19 of
[Introduction to Flow](../../docs/book/19-coding-challenge-series.md).

List the challenges:

```bash
python3 challenges/flow-specific/check.py list
```

Check a submission:

```bash
python3 challenges/flow-specific/check.py check F01 path/to/answer.flow
```

The checker removes line comments before checking syntax. A required token in a
comment therefore does not count. If the syntax check passes, the checker runs
the submission with the compiler host and environment listed in
[`catalog.json`](catalog.json). A successful program returns zero.

Use `--syntax-only` for a target that is unavailable on the current machine:

```bash
python3 challenges/flow-specific/check.py check F31 kernel.flow --syntax-only
```

Syntax checks prevent ordinary shortcut solutions, but they do not prove that
the required construct performs the main work. Course runners should add hidden
input and output tests for assessed submissions.
