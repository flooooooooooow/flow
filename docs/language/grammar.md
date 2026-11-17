# Formal Grammar

Flow's active source parser is written in Flow in [`compiler/src/parser.flow`](../../compiler/src/parser.flow), alongside the lexer in [`compiler/src/lexer.flow`](../../compiler/src/lexer.flow) and dedicated language expanders such as [`compiler/src/flow_blocks.flow`](../../compiler/src/flow_blocks.flow). This page and [`grammar.ebnf`](../grammar.ebnf) are **illustrative guides**, not an exhaustive or mechanically generated parser specification. For an accepted construct, the compiler and its versioned fixtures/tests are authoritative.

> **Machine-readable source:** [grammar.ebnf](../grammar.ebnf) · **Human guide:** [Syntax](syntax.md)

---

## EBNF notation

| Symbol | Meaning | Example |
|--------|---------|---------|
| `::=` | Definition | `program ::= declaration* EOF` |
| `\|` | Alternative | `"if" \| "while"` |
| `( )` | Grouping | `("," parameter)*` |
| `[ ]` | Optional (0 or 1) | `["else" block]` |
| `{ }` | Repeat (0 or more) | `{ statement* }` |
| `*` | Zero or more (suffix) | `declaration*` |
| `ε` | Empty / absent | `parameter_list ::= ε` |
| `"..."` | Terminal token | `"function"` |
| `IDENTIFIER` | Lexical nonterminal | `[a-zA-Z_][a-zA-Z0-9_]*` |

Comments (`# ...`) and section banners are documentation only. The lexer rule that ignores `#` line comments applies to `.flow` source rather than to this file.

---

## Program structure

The following is a **selected core subset** for reading the EBNF notation. It is not a complete list of Flow top-level forms: units, evolutions, equations, test/proof constructs, traits, modules and specialized DSL extensions are implemented and tested through additional parser/expander paths. Do not use this abbreviated production to reject code without checking the active compiler.

```
program        ::= declaration* EOF
declaration    ::= export_marker? ( function_decl | struct_decl | effect_decl
                                   | capability_decl | const_decl
                                   | import_decl | extern_decl )
export_marker  ::= "export"
```

**Top-level forms:** functions, structs, algebraic effects, capabilities, constants, imports, and `extern` blocks for C FFI.

`export` in front of an `import_decl` is a re-export: the imported module's
exports become exports of this file. See [modules.md](modules.md#re-export).

---

## Functions & types

```
function_decl  ::= "function" IDENTIFIER "(" parameter_list ")" ("->" type)? block
parameter_list ::= parameter ("," parameter)* | ε
parameter      ::= IDENTIFIER ":" type

type           ::= primitive_type | array_type | pointer_type
                 | struct_type | function_type

primitive_type ::= "i8"…"i128" | "u8"…"u128" | "f32" | "f64" | "bool" | "string" | "void"
array_type     ::= "array" "<" type ("," NUMBER)? ">"
pointer_type   ::= "ptr" "<" type ">"
```

Generics use monomorphization at compile time; the surface grammar may extend with type parameters as the language evolves.

---

## Statements

```
block          ::= "{" statement* "}"
statement      ::= var_decl | assignment | return_stmt | if_stmt | while_stmt
                 | for_stmt | handle_stmt | match_stmt | expression_stmt
                 | effect_decl | capability_decl

var_decl       ::= "let" IDENTIFIER (":" type)? "=" expression
if_stmt        ::= "if" expression block ("elif" expression block)* ("else" block)?
while_stmt     ::= "while" expression block
for_stmt       ::= ("parallel")? "for" IDENTIFIER "in" range_expr block
range_expr     ::= expression "to" expression ("step" expression)?
handle_stmt    ::= "handle" expression "with" "{" handler_case* "}"
match_stmt     ::= "match" expression "{" (match_case | default_case)* "}"
match_case     ::= match_pattern ("if" expression)? "=>" block ","?
default_case   ::= "default" block
match_pattern  ::= pattern_atom ("|" pattern_atom)*
pattern_atom   ::= literal | IDENTIFIER | IDENTIFIER "(" pattern_arg ("," pattern_arg)* ")"
pattern_arg    ::= literal | IDENTIFIER
```

`match_pattern` is parsed one precedence level below bitwise-OR, so a bare
`|` between patterns means alternation (`1 | 2 | 3 => ...`), not the
bitwise-OR operator. Alternatives must all be literals. `IDENTIFIER "(" ... ")"`
is the struct-pattern form (`Point(a, b)`); a `literal` argument in that form
becomes a nested value check on that field instead of a binding
(`Point(0, y)`).

`let mut` and additional statement forms are documented in [Variables](variables.md) and [Language Spec](../LANGUAGE_SPEC.md).

---

## Expressions (precedence)

Expression parsing follows a fixed precedence chain (lowest to highest binding):

| Level | Operators / forms |
|-------|-------------------|
| 1 | `\|\|` (logical or) |
| 2 | `&&` (logical and) |
| 3 | `==` `!=` |
| 4 | `<` `>` `<=` `>=` |
| 5 | `+` `-` |
| 6 | `*` `/` `%` |
| 7 | Unary `-` `!` |
| 8 | Primary: literals, calls, struct/array literals, indexing, member access |

```
expression     ::= logical_or_expr
logical_or_expr::= logical_and_expr ("||" logical_and_expr)*
…
primary_expr   ::= literal | variable | function_call | struct_literal
                 | array_literal | paren_expr | array_access | member_access
```

---

## Effects & capabilities

```
effect_decl       ::= "effect" IDENTIFIER "{" effect_operation* "}"
effect_operation  ::= IDENTIFIER "(" parameter_list ")" ("->" type)?
capability_decl   ::= "capability" IDENTIFIER "{" capability_method* "}"
capability_method ::= IDENTIFIER ":" effect_operation
```

See [Verification](../language/verification.md) for the proof-oriented extensions (`theorem`, `assume`, `therefore`) planned on the same grammar foundation.

---

## Full specification

For an **illustrative EBNF inventory** of lexical tokens, keywords and common statements, see [grammar.ebnf](../grammar.ebnf). It is not currently a complete, automatically verified grammar for the entire implemented language. The parser source, language fixtures and [`./flow tool compiler/scripts/parse_coverage.flow --check`](../../compiler/scripts/parse_coverage.flow) provide executable evidence about actual accepted syntax. Parse coverage is not proof that every construct typechecks, lowers, executes or works across backends; use the relevant language, C and MLIR parity tests for those claims.