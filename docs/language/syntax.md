# Flow Syntax

## Keywords

```
function, struct, if, elif, else, while, for, in, to, return,
let, mut, true, false, effect, capability, extern, and, or, not
```

## Literals

```flow
# Integers
42, -17, 0xFF, 0b1010

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

```flow
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
```flow
counter = counter + 1
point.x = 10.0
arr[0] = 42
```

### Function Definition
```flow
function name(param: Type) -> ReturnType {
    return value
}
```

### Control Flow
```flow
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
```flow
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
```flow
point.x
person.address.city
```

### Index Access
```flow
arr[0]
matrix[i * width + j]
```

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
