; Tree-sitter syntax highlight queries for Flow in Helix
; Copy to ~/.config/helix/queries/flow/highlights.scm

; Keywords
[
  "function"
  "let"
  "mut"
  "const"
  "if"
  "else"
  "for"
  "while"
  "in"
  "return"
  "break"
  "continue"
  "struct"
  "enum"
  "trait"
  "impl"
  "type"
  "export"
  "import"
  "extern"
  "match"
  "effect"
  "handle"
  "perform"
  "shader"
  "fill"
] @keyword

; Decorators & Attributes (@gpu, @rt_safe, @lifetime, etc.)
(attribute) @attribute
"%" @attribute

; Literals
(string_literal) @string
(number_literal) @number
(boolean_literal) @boolean

; Comments
(comment) @comment

; Functions
(function_declaration name: (identifier) @function)
(call_expression function: (identifier) @function.call)

; Types
(type_identifier) @type
(primitive_type) @type.builtin

; Operators
[
  "+" "-" "*" "/" "%" "=" "==" "!=" "<" ">" "<=" ">=" "->" "=>" "|>"
] @operator
