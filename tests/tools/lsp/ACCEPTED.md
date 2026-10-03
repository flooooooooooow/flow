# Accepted differences from the Python language server

`run.flow` diffs the native server's replies against `<case>.python`, the
replies the retired `src/flow/lsp_server.py` gave to the same session.
Every line of every `<case>.accepted.diff` falls into one of the classes
below. A change to the native server that moves any other line fails the
test.

Before diffing, `run.flow` rewrites U+2014 in the Python recording as a
hyphen. The hover and completion prose in `tools/lsp/catalog.flow` is the
Python text with that one character changed.

## 1. Capabilities (`initialize` in every case)

The native server advertises `codeActionProvider: true` and reports
`serverInfo.version` 0.3.0. The Python server had a code action handler
for idiom quick fixes but never routed `textDocument/codeAction`, so it
answered `null` (`diagnostics` id 2). The native server answers with the
quick fix.

## 2. Diagnostic wording and the checker behind it

Parse errors come from the flowc parser and type findings from the Stage-A
checker (`compiler/src/typecheck.flow`), not from the Python parser and
`TypeChecker`. The messages are flowc's:

| Python | Native |
|---|---|
| `Undefined variable 'x'` | `unbound ident 'x'` |
| `Undefined function 'f'` | `unbound call 'f'` |
| `Unterminated block: expected '}' before end of file` at 0:0 | `parse error: unexpected end of file` at the end |
| `Error: Expected TokenType.LBRACE, got TokenType.FAT_ARROW ...` | `parse error: unexpected token '=>'` |
| `Unexpected declaration: TokenType.IDENTIFIER` | `parse error: unexpected identifier 'xs'` |

Ranges are the same in these cases except the end-of-file error, which
flowc places where the file ends.

The Python checker also reported `Function 'use_norm' returns void but
should return f64` (and the same for `main` in `stdlib_add.flow`) for
functions that do return a value. flowc does not report these.
(`definition`, `references_rename`, `hover`, `completion`,
`diagnostics`, `formatting`.)

`fixtures/attr.flow` declares `let v: vec = 0`. The Python parser rejected
the bare `vec`; flowc accepts it, so the file has no diagnostics.

## 3. Idiom hints

FIDIOM001 in `fixtures/idiom.flow` is on line 1, columns 4 to 11 (the
`let mut`). Python put it at line 0, columns 3 to 10: it read a 1-based
location as 0-based on one axis and not the other.

The Python advisor crashed (`'IfStatement' object has no attribute
'else_if'`) on any function with an `if`, which silenced hints for the
whole file. The native check walks every branch. It also counts a write
through `x[i] = ...`, `x.f = ...`, `x += ...` or `&x`, and writes inside
blocks flowc keeps as text (`handle`), as mutation. The repository files
in these sessions have no hints either way.

## 4. Python framing bug: non-ASCII documents

The Python server read `Content-Length` bytes as characters. A document
with any non-ASCII character (an em dash in a comment, `«»` in a claim
path, box-drawing rules) made it read past the message, drop it, and
misparse the next one. In these sessions that lost:

- `hover`: the didOpen of `examples/packages/use_hello_lib/src/main.flow`
  and hover id 46; ids 47 and 48 answered `null` for a document it never
  opened.
- `definition`: the same didOpen and id 14; id 15 answered `null`.
- `repo_files`: the didOpens of `controllability_demo.flow`,
  `sine-derivatives-at-zero.flow`, `compiler/src/lsp_utils.flow` and
  `use_hello_lib/src/main.flow`, with ids 7, 8 and 10, and an empty id 11.

The native server frames by bytes and answers all of them. The package
imports in `use_hello_lib` resolve through `flow_packages/`, so hover and
definition reach `hello_lib/src/lib.flow`.

## 5. Symbol ranges

For functions and structs the Python range end came from its parser's
`SourceLocation.end_line`, which drifted one to ten lines above the
declaration after `@attr` lines (`lib/stdlib/math.flow` from `sin` on,
`definition` id 8). The native end is the end of the name on the
declaration line.

`documentSymbol` on a file with imports (`imports` id 7) lists only the
file's own declarations. Python listed the imported symbols too, with
their line and column in the file that declares them.

## 6. Type text in signatures

The Python server printed its internal type names. The native server
prints the type from the source:

| Python | Native |
|---|---|
| `ptr<ptr_f64>` | `ptr<f64>` |
| `array_f32`, `array_7_i32` | `array<f32>`, `array<i32>` |
| `fn_f32__bool<f32>` | `(f32) -> bool` |
| `Signal_R<R>` | `Signal<R>` |
| `span_mut_i32` | `span<i32>` |

This moves stdlib completion items in `completion` ids 9, 11 and 13.

## 7. The dynamics DSL

The Python server expanded `dyn.` blocks before indexing but parsed the
raw text for diagnostics, so `fixtures/dsl.flow` got a parse error on
`dyn.dsys` while hover still worked. The native server runs flowc's
expansions (Field DSL, dynamics DSL, flow blocks) before both, as flowc
does when it compiles the file, and reports no error (`hover`,
`completion`).

## 8. Formatting

The Python formatter was lossy: it replaced `for` loops and field access
with `<expr>`, wrote `let p: auto`, dropped comments and dropped
parentheses (`(a + b) * 2` became `a + b * 2`). Its edits in `formatting`
ids 2, 3, 5, 6, 8 and 10 change or delete code.

The native server formats with `compiler/src/fmt.flow`, the formatter
behind `flow fmt`. It changes whitespace only: every token and comment
stays, and line breaks stay where they were
(`compiler/scripts/fmt_check.flow` checks this over every tracked `.flow`
file). `messy.flow` (ids 2 and 3) is re-indented and re-spaced, and keeps
`struct P { x: f64, y: f64 }` and `if s > 2 { return 1 } else { return 0 }`
on one line each, commas included. `messy_comments.flow` (id 10) keeps
its comments and parentheses and only changes indentation and blank
lines. The files that are already laid out (ids 5, 6, 8) get no edit.
