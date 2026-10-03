; Keywords and control flow
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

; Declarations
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
] @keyword

; Operators
"evolves as" @operator

; Built-in types
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
] @boolean

"null" @constant.builtin

; Comments
(comment) @comment

; Literals
(string_literal) @string
(number_literal) @number

; Dynamics and DSL primitives
[
  "dsys"
  "horizon"
  "sense"
  "closed"
  "analyze"
  "couple"
  "guide"
  "controllable"
  "spectral"
  "gramian"
  "stable"
  "population"
  "generations"
  "mutation"
  "discrete"
  "continuous"
] @keyword.other.dynamics

; Ordering operators and keywords
[
  "sortBy"
  "sort"
  "order"
  "asc"
  "desc"
  "ascending"
  "descending"
  "unique"
  "adaptive"
  "compact"
  "entropy"
] @keyword.other.ordering

; Functions and calls
(function_declaration name: (identifier) @function)
(call_expression function: (identifier) @function)

; Variables and parameters
(parameter name: (identifier) @variable.parameter)
(identifier) @variable
