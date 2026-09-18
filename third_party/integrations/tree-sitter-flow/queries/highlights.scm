(comment) @comment

(string) @string
(integer) @number
(float) @number.float
(boolean) @boolean
(null) @constant.builtin

[
  "function"
  "struct"
  "enum"
  "type"
  "trait"
  "impl"
  "effect"
  "capability"
  "extern"
  "const"
  "flow"
  "state"
  "param"
  "solver"
  "import"
  "module"
] @keyword

(export_modifier) @keyword

[
  "if"
  "elif"
  "else"
  "while"
  "for"
  "in"
  "parallel"
  "return"
  "match"
  "every"
  "evolves"
  "as"
] @keyword.control

(break_statement) @keyword.control
(continue_statement) @keyword.control

[
  "and"
  "or"
  "not"
] @keyword.operator

(primitive_type) @type.builtin
(type_declaration (identifier) @type.definition)
(struct_declaration name: (identifier) @type.definition)
(enum_declaration name: (identifier) @type.definition)
(trait_declaration (identifier) @type.definition)
(effect_declaration (identifier) @type.definition)
(capability_declaration (identifier) @type.definition)
(flow_declaration name: (identifier) @type.definition)

(function_declaration name: (identifier) @function)
(call_expression function: (identifier) @function.call)

(parameter name: (identifier) @variable.parameter)
(field_declaration name: (identifier) @property)
(field_initializer (identifier) @property)
(member_expression property: (identifier) @property)

(attribute (identifier) @attribute)

[
  "="
  "+="
  "-="
  "*="
  "/="
  "%="
  "=="
  "!="
  "<"
  "<="
  ">"
  ">="
  "+"
  "-"
  "*"
  "/"
  "%"
  "|"
  "&"
  "^"
  "~"
  "<<"
  ">>"
  "|>"
  "->"
  "=>"
] @operator
