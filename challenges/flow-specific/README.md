# Flow-specific coding challenges

The full series is printed as Chapter 19 of
[Introduction to Flow](../../docs/book/19-coding-challenge-series.md).

List the challenges:

```bash
challenges/flow-specific/check.sh list
```

Check a submission:

```bash
challenges/flow-specific/check.sh check F01 path/to/answer.flow
```

The checker removes line comments before checking syntax. A required token in a
comment therefore does not count. If the syntax check passes, the checker runs
the submission with the compiler host and environment listed in
[`catalog.json`](catalog.json). A successful program returns zero.

Use `--syntax-only` for a target that is unavailable on the current machine:

```bash
challenges/flow-specific/check.sh check F31 kernel.flow --syntax-only
```

The checker is written in Flow (`scripts/tools/challenge_check`). `check.sh`
builds it with the Stage-A compiler on first use, so it needs only `cc`.
`check.sh self-test` runs its unit checks, and `check.sh scan file.flow...`
prints the syntax verdict of every challenge for each file.

Syntax checks prevent ordinary shortcut solutions, but they do not prove that
the required construct performs the main work. Course runners should add hidden
input and output tests for assessed submissions.
