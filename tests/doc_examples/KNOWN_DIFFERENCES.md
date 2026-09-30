# Where the Flow checker differs from the Python one

The goldens in `cases/` were recorded from the Python checker
(`scripts/check_doc_examples.py`, `check_doc_examples_strict.py`,
`check_doc_flow_snippets.py`, `docs_blocks.py`) and then replaced by the
Flow checker's output only where the two differ for one of the reasons
below. Every exit status is the same as Python's.

## Front end

The Python checker parsed and type-checked each block with the Python front
end, then compiled it with flowc. The Flow checker parses with the flowc
parser and compiles with `compiler/scripts/flowc_emit.sh --strict`, whose
type check is the port of the Python one (compiler/src/sem_check.flow). A
type error stops the block at stage `types` with the checker's first
message, as it did in Python.

1. Parse error text. A block that does not parse reports flowc's message,
   `block.flow:1:13: parse error: unexpected token '->' (byte 12)`, where the
   Python checker reported the Python parser's. The verdict and the stage
   (`parse`) are the same. Cases: harness.1 to .5 (docs.md:100, docs.md:141),
   ledger_new.1, ledger_edited.1.

2. Module statics. The Python parser required a top-level `let` to be
   `let mut` with a type. flowc accepts both forms and writes C that does not
   compile, so the Flow checker applies the rule itself, in token order up to
   where flowc stopped parsing, with the Python message. No golden changed.

## Command line

3. `snippets` on a bad info string printed a Python traceback and exited 1.
   It now prints `error: <message>` and still exits 1. Cases: badinfo_*.2.

4. The hint after paid-off debt names `./scripts/check_doc_examples.sh
   --write-ledger` in place of `python3 scripts/check_doc_examples.py
   --write-ledger`. Case: ledger_paid.1.

## The repository's own documentation

Over the whole tree (635 blocks on 2026-09-29) every status and stage in
docs/generated/example-status.json is the Python checker's. One detail
differs. The `expect-error` block in docs/language/modules-namespacing.md
has two modules that both define `gain`. The Python host kept both
definitions as overloads, and its checker failed a later harness rung
with "Undefined function 'gain'". flowc stops at the first rung with
"function 'gain' is defined twice with the same parameter types", the
error the block is about.
