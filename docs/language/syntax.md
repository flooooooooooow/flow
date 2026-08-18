# Flow Syntax

## Keywords

```
function, struct, if, elif, else, while, for, in, to, return,
let, mut, true, false, effect, capability, extern, and, or, not
```

## Literals

```flow ignore="catalogue of literal forms, not an expression"
# Integers (decimal and hex)
42, -17, 0xFF
# Binary 0b… is not lexed yet — use decimal/hex

# Floats
3.14, -0.001, 1.5e10

# Strings
"Hello, World!"

# Booleans
true, false

# Null pointer
null
```

## Comments

```flow ignore="comment syntax only"
# Single line comment
```

## Operators

### Arithmetic
```
+  -  *  /  %
```

### Comparison
```
==  !=  <  <=  >  >=
```

### Logical
```
and  or  not
```

### Bitwise
```
|  &  ^  ~  <<  >>
```

## Statements

### Variable Declaration
```flow
let x: i32 = 42
let mut counter: i32 = 0
```

### Assignment
```flow ignore="assignment forms over placeholder names"
counter = counter + 1
point.x = 10.0
arr[0] = 42
```

### Function Definition
```flow ignore="declaration template; Type and ReturnType are metasyntactic"
function name(param: Type) -> ReturnType {
    return value
}
```

### Control Flow
```flow ignore="control-flow shapes with elided bodies"
if condition {
    # ...
} elif other {
    # ...
} else {
    # ...
}

while condition {
    # ...
}

for i in 0 to n {
    # ...
}
```

### Match

```flow ignore="match arm forms over an undeclared subject"
match n {
    0 => { return "zero" }
    1 | 2 | 3 => { return "small" }        # `|` alternation (literal patterns only)
    x if x > 100 => { return "big" }       # guard clause: binds x, checked with `if`
    x if x < 0 => { return "negative" }
    _ => { return "other" }
}

match point {
    Point(0, 0) => { return "origin" }     # nested literal pattern on field 0
    Point(0, y) => { return "y-axis" }     # literal + binding mixed
    Point(x, y) if x == y => { return "diagonal" }
    _ => { return "elsewhere" }
}
```

- Arms are checked top-to-bottom; the first arm whose pattern matches **and**
  whose guard (if any) is true wins. A failing guard falls through to the
  next arm, it does not exit the match.
- `_` is a wildcard that matches anything and binds nothing.
- A bare identifier (e.g. `x`) matches anything and binds the matched value
  to that name for the rest of the arm (guard + body).
- `|` combines several literal patterns into one arm (`1 | 2 | 3 => ...`).
  Only literals can be combined this way — bindings and struct patterns
  cannot appear on either side of `|`.
- Struct patterns (`Point(a, b)`) destructure positionally. A literal in a
  field position (`Point(0, y)`) requires that field to equal the literal
  instead of binding it; the remaining positions bind as usual.
- `default { ... }` provides a fallback when no arm (and no guard) matches.

### Struct Definition
```flow
struct Name {
    field1: Type1,
    field2: Type2
}
```

### Extern Block
```flow
extern {
    function malloc(size: i64) -> ptr<void>
    function free(p: ptr<void>) -> void
}
```

## Expressions

### Function Call
```flow ignore="call syntax with placeholder names"
function_name(arg1, arg2)
```

### Struct Literal
```flow
Point { x: 1.0, y: 2.0 }
```

### Array Literal
```flow
[1, 2, 3, 4, 5]
```

### Field Access
```flow ignore="field-access notation"
point.x
person.address.city
```

### Index Access
```flow ignore="index notation"
arr[0]
matrix[i * width + j]
```

### Pipeline

`|>` is forward composition: the value on the left becomes an argument to the
call on the right. It is left-associative, so a chain reads top-to-bottom in
the order the data flows.

```flow ignore="pipe desugaring shown as equivalences"
x |> f            # f(x)
x |> f(y)         # f(x, y)      — piped value is prepended
x |> obj.m(y)     # obj.m(x, y)  — works for method calls too
a |> f() |> g()   # g(f(a))      — left-associative chain
```

By default the piped value is inserted as the **first** argument. A single `_`
placeholder overrides that, routing the piped value to whichever slot you mark
instead:

```flow ignore="pipe placeholder forms shown as equivalences"
signal |> lowpass(cutoff)      # lowpass(signal, cutoff)
value  |> clamp(0.0, _, 1.0)   # clamp(0.0, value, 1.0)
x      |> mix(_, sidechain, k) # mix(x, sidechain, k)  — explicit leading slot
```

At most one `_` may appear per stage — the piped value fills exactly one slot,
so two placeholders would duplicate it and are rejected at parse time.

#### Fork blocks

A **fork block** applies several pipelines to the *same* value and collects the
results into a record:

```flow ignore="fork-block notation over undeclared helpers"
let s: Stats = n |> Stats {
    doubled  = twice,
    squared  = square,
    plus_ten = add(_, 10),
}
# == Stats { doubled: twice(n), squared: square(n), plus_ten: add(n, 10) }
```

Each `field = stage…` branch is the pipeline `source |> stage…`, so branch
stages compose (and take placeholders) exactly like any other pipeline. Branches
use `=` — not the struct-literal `:` — so the fork and the record it builds read
distinctly. The block lowers to a struct literal of the named record, which is
type-checked against that struct's declared fields like any other literal. The
result is itself a value, so a fork can sit mid-pipeline: `x |> R { … } |> f`.

Dropping the record name makes it **anonymous** — the record type is inferred
rather than declared:

```flow ignore="inferred-record notation over undeclared helpers"
let s = n |> {
    doubled  = twice,
    squared  = square,
    plus_ten = add(_, 10),
}
# s : { doubled: i32, squared: i32, plus_ten: i32 }, inferred from the
# return types of twice / square / add — no struct declared anywhere.
```

Each field takes the return type of the function its branch pipeline ends in, so
branches must bottom out in a call whose return type is known; a branch that
can't be typed structurally (e.g. a method call on an inferred receiver) has to
name the record instead. Anonymous records with the same field signature share
one synthesized type.

Whether named or anonymous, the piped value is evaluated **once** and shared
across every branch: a non-trivial `source` (a call rather than a variable) is
hoisted to a temporary binding just above the statement, so `frames(1024)` in
`x |> frames(1024) |> { … }` runs a single time no matter how many branches read
it.

#### `choose` — a state-driven stage

A `choose` stage selects which pipeline runs based on a value, so the shape of
the computation can depend on state:

```flow ignore="fragment of a piped return expression"
return x
    |> choose mode.tag {
        Mode_Double => double,
        Mode_Triple => triple,
    }
    |> normalize
```

Each `pattern => stage` arm is a pipeline over the piped value; `choose` applies
the arm the selector matches. It lowers to a hoisted `let mut __choose : T` plus
a `match` that assigns the chosen arm (`T` is the arms' common return type), so
the result is an ordinary value that flows on to later stages. The source is
evaluated once, like a fork. `choose` is contextual: `x |> choose(a, b)` and a
bare `x |> choose` stay ordinary calls — only `choose selector { … }` is the
stage form.

## Grammar (Simplified EBNF)

```ebnf
program     = { declaration }
declaration = function_decl | struct_decl | extern_decl

function_decl = "function" IDENT "(" params ")" "->" type block
struct_decl   = "struct" IDENT "{" { field "," } "}"
extern_decl   = "extern" "{" { extern_fn } "}"

type = "i32" | "i64" | "f32" | "f64" | "bool" | "string" | "void"
     | "ptr" "<" type ">"
     | "array" "<" type "," INT ">"
     | IDENT

statement = let_stmt | assign_stmt | if_stmt | while_stmt | for_stmt
          | return_stmt | expr_stmt

expr = literal | IDENT | unary_expr | binary_expr | call_expr
     | field_expr | index_expr | struct_literal | "(" expr ")"
```

See [grammar.ebnf](../grammar.ebnf) for the complete formal grammar.
