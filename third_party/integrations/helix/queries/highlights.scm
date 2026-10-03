; Tree-sitter highlight queries for Flow
; Place this in ~/.config/helix/runtime/queries/flow/highlights.scm

; Keywords
[
  "if"
  "elif"
  "else"
  "while"
  "for"
  "return"
  "match"
  "default"
  "handle"
  "with"
  "parallel"
  "in"
  "step"
  "to"
  "and"
  "or"
  "not"
  "break"
  "continue"
  "when"
  "always"
] @keyword.control

[
  "function"
  "let"
  "mut"
  "struct"
  "enum"
  "effect"
  "capability"
  "import"
  "export"
  "module"
  "extern"
  "const"
  "theorem"
  "assume"
  "therefore"
  "type"
  "impl"
  "trait"
  "flow"
  "state"
  "shader"
] @keyword.storage

"evolves as" @keyword.operator

; Primitive types
[
  "i8"
  "i16"
  "i32"
  "i64"
  "i128"
  "u8"
  "u16"
  "u32"
  "u64"
  "u128"
  "f32"
  "f64"
  "bool"
  "void"
  "string"
  "array"
  "ptr"
  "vec"
] @type.builtin

; Constants
[
  "true"
  "false"
  "null"
] @constant.builtin

; Comments
(comment) @comment
(line_comment) @comment

; Strings & Escapes
(string_literal) @string
(escape_sequence) @constant.character.escape

; Numbers
(integer_literal) @constant.numeric.integer
(float_literal) @constant.numeric.float

; Functions
(function_declarator name: (identifier) @function)
(call_expression function: (identifier) @function.method)

; Operators & Punctuation
[
  "+"
  "-"
  "*"
  "/"
  "%"
  "=="
  "!="
  "<"
  "<="
  ">"
  ">="
  "&&"
  "||"
  "!"
  "="
  "->"
  "|>"
  ".."
] @operator

[
  "("
  ")"
  "["
  "]"
  "{"
  "}"
] @punctuation.bracket

[
  ","
  ";"
  ":"
  "."
] @punctuation.delimiter
