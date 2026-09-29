# Where the Flow checker differs from the Python one

The goldens in `cases/` were recorded from the Python checker
(`scripts/check_doc_examples.py`, `check_doc_examples_strict.py`,
`check_doc_flow_snippets.py`, `docs_blocks.py`) and then replaced by the
Flow checker's output only where the two differ for one of the reasons
below. Every exit status is the same as Python's.

## Front end

The Python checker parsed and type-checked each block with the Python front
end, then compiled it with flowc. The Flow checker parses with the flowc
parser and leaves the type check to flowc (`compiler/scripts/flowc_emit.sh`,
the defaults of `flow compile`).

1. Parse error text. A block that does not parse reports flowc's message,
   `block.flow:1:13: parse error: unexpected token '->' (byte 12)`, where the
   Python checker reported the Python parser's. The verdict and the stage
   (`parse`) are the same. Cases: harness.1 to .5 (docs.md:100, docs.md:141),
   ledger_new.1, ledger_edited.1.

2. Names the Python type checker rejected and flowc leaves to clang. An
   undefined variable and an undeclared return type were `unverified` at
   stage `types`; they are still `unverified`, now at stage `clang` with
   clang's message. Cases: harness.1 to .6 (docs.md:64, docs.md:211). With
   `--no-clang` (harness.6) the two blocks verify, since nothing after flowc
   looks at them.

3. Module statics. The Python parser required a top-level `let` to be
   `let mut` with a type. flowc accepts both forms and writes C that does not
   compile, so the Flow checker applies the rule itself, in token order up to
   where flowc stopped parsing, with the Python message. No golden changed.

## Command line

4. `snippets` on a bad info string printed a Python traceback and exited 1.
   It now prints `error: <message>` and still exits 1. Cases: badinfo_*.2.

5. The hint after paid-off debt names `./scripts/check_doc_examples.sh
   --write-ledger` in place of `python3 scripts/check_doc_examples.py
   --write-ledger`. Case: ledger_paid.1.

## The repository's own documentation

Over the whole tree (635 blocks on 2026-09-29), 622 ledger rows are
byte-identical. The other 13 differ for the reasons above:

- Eight blocks tagged `expect-error` are rejected only by checks the
  Python type checker had and flowc does not: a string initialising an
  `i32` (ROADMAP.md), assignment to an immutable `let`
  (docs/book/02-values-and-types.md), lifetime domain escapes and
  violations and the RT-safety rule (four in
  docs/language/lifetime-domains.md), a span outliving its storage
  (docs/language/spans.md) and a call to an undefined function, which
  flowc reports as a warning (docs/language/modules-namespacing.md).
  They are now `unverified` ("tagged expect-error but compiles") and sit
  in the ledger until flowc gains those checks.
- Two blocks the Python parser accepted and flowc's parser does not
  (docs/LANGUAGE_SPEC.md, docs/book/10-memory-and-lifetimes.md): still
  `unverified`, now at stage `parse`.
- Three blocks that define a capability twice once split into
  declarations and statements (two in docs/effects-showcase.md, one in
  docs/tutorials/effects-basics.md): the Python type checker rejected the
  duplicate, flowc accepts it and clang reports the redefinition. Still
  `unverified`, now at stage `clang`.
