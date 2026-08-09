# Formal Grammar

Flow's syntax is defined by a single EBNF specification, kept in sync with `src/flow/parser.py`. This page explains the notation and maps the grammar into readable sections.

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

Comments (`# ...`) and section banners are documentation only, the lexer ignores `#` line comments in `.flow` source, not in this file.

---

## Program structure

A compilation unit is a sequence of top-level declarations followed by end-of-input.

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
bitwise-OR operator, alternatives must all be literals. `IDENTIFIER "(" ... ")"`
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

The complete EBNF, including lexical tokens, keywords, and symbol definitions, is in **[grammar.ebnf](../grammar.ebnf)**.

Open it in the wiki for syntax highlighting, section navigation, and rule search.