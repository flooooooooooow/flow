(comment) @comment
(string) @string
(number) @number

[
  "true"
  "false"
  "null"
] @constant.builtin

[
  "function"
  "let"
  "mut"
  "const"
  "struct"
  "enum"
  "effect"
  "capability"
  "import"
  "export"
  "module"
  "extern"
  "type"
  "distinct"
  "trait"
  "impl"
  "flow"
  "state"
  "param"
] @keyword

[
  "if"
  "elif"
  "else"
  "while"
  "for"
  "parallel"
  "in"
  "to"
  "step"
  "return"
  "break"
  "continue"
  "defer"
  "evolves"
  "as"
] @keyword.control

(type) @type
(function_declaration name: (identifier) @function)
(call_expression function: (identifier) @function.call)
(struct_declaration name: (identifier) @type.definition)
(enum_declaration name: (identifier) @type.definition)
(effect_declaration name: (identifier) @type.definition)
(capability_declaration name: (identifier) @type.definition)
