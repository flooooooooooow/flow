module.exports = grammar({
  name: "flow",

  extras: $ => [
    /\s/,
    $.comment,
  ],

  word: $ => $.identifier,

  supertypes: $ => [
    $.expression,
    $.statement,
    $.declaration,
  ],

  rules: {
    source_file: $ => repeat($.declaration),

    comment: _ => token(seq("#", /.*/)),

    identifier: _ => /[A-Za-z_][A-Za-z0-9_]*/,
    number: _ => token(choice(
      /0x[0-9A-Fa-f]+/,
      /[0-9]+\.[0-9]+([eE][+-]?[0-9]+)?/,
      /[0-9]+([eE][+-]?[0-9]+)?/
    )),
    string: _ => seq(
      '"',
      repeat(choice(
        token.immediate(/[^"\\\n]+/),
        token.immediate(/\\./)
      )),
      '"'
    ),

    type: $ => choice(
      "i8", "i16", "i32", "i64", "i128",
      "u8", "u16", "u32", "u64", "u128",
      "f32", "f64", "bool", "string", "void",
      $.identifier,
      $.generic_type
    ),

    generic_type: $ => seq(
      field("name", choice("array", "ptr", "vec", "span", $.identifier)),
      "<",
      commaSep1(choice($.type, $.number, "mut")),
      ">"
    ),

    declaration: $ => choice(
      $.function_declaration,
      $.struct_declaration,
      $.enum_declaration,
      $.effect_declaration,
      $.capability_declaration,
      $.type_declaration,
      $.const_declaration,
      $.import_declaration,
      $.extern_declaration,
      $.flow_declaration,
      $.statement
    ),

    function_declaration: $ => seq(
      optional("export"),
      optional(choice("inline", "noinline", "always_inline")),
      "function",
      field("name", $.identifier),
      optional($.type_parameters),
      $.parameters,
      optional(seq("->", field("return_type", $.type))),
      $.block
    ),

    type_parameters: $ => seq("<", commaSep1($.identifier), ">"),

    parameters: $ => seq(
      "(",
      commaSep(seq(field("name", $.identifier), ":", field("type", $.type))),
      ")"
    ),

    struct_declaration: $ => seq(
      optional("export"),
      "struct",
      field("name", $.identifier),
      optional($.type_parameters),
      "{",
      commaSep(seq(field("name", $.identifier), ":", field("type", $.type))),
      optional(","),
      "}"
    ),

    enum_declaration: $ => seq(
      optional("export"),
      "enum",
      field("name", $.identifier),
      "{",
      commaSep1($.identifier),
      optional(","),
      "}"
    ),

    effect_declaration: $ => seq(
      "effect",
      field("name", $.identifier),
      "{",
      repeat(seq(
        field("operation", $.identifier),
        $.parameters,
        optional(seq("->", $.type))
      )),
      "}"
    ),

    capability_declaration: $ => seq(
      "capability",
      field("name", $.identifier),
      "{",
      repeat(choice(
        seq("effect", $.identifier),
        $.function_declaration,
        seq($.identifier, ":", $.identifier, $.parameters, optional(seq("->", $.type)))
      )),
      "}"
    ),

    type_declaration: $ => seq(
      optional("distinct"),
      "type",
      field("name", $.identifier),
      "=",
      $.type
    ),

    const_declaration: $ => seq(
      "const",
      field("name", $.identifier),
      optional(seq(":", $.type)),
      "=",
      $.expression
    ),

    import_declaration: $ => seq(
      optional("export"),
      "import",
      choice($.string, $.identifier),
      optional(seq("{", commaSep1($.identifier), "}"))
    ),

    extern_declaration: $ => seq(
      "extern",
      "{",
      repeat($.function_declaration),
      "}"
    ),

    flow_declaration: $ => seq(
      "flow",
      field("name", $.identifier),
      "{",
      repeat(choice(
        seq(choice("state", "param"), $.identifier, ":", $.type, "=", $.expression),
        seq($.identifier, "evolves", "as", $.expression),
        $.statement
      )),
      "}"
    ),

    block: $ => seq("{", repeat($.statement), "}"),

    statement: $ => choice(
      $.variable_declaration,
      $.assignment,
      $.return_statement,
      $.if_statement,
      $.while_statement,
      $.for_statement,
      $.break_statement,
      $.continue_statement,
      $.defer_statement,
      $.expression_statement
    ),

    variable_declaration: $ => seq(
      "let",
      optional("mut"),
      field("name", $.identifier),
      optional(seq(":", $.type)),
      "=",
      $.expression
    ),

    assignment: $ => seq($.expression, "=", $.expression),
    return_statement: $ => seq("return", optional($.expression)),
    break_statement: _ => "break",
    continue_statement: _ => "continue",
    defer_statement: $ => seq("defer", choice($.block, $.expression_statement)),

    if_statement: $ => seq(
      "if",
      $.expression,
      $.block,
      repeat(seq("elif", $.expression, $.block)),
      optional(seq("else", $.block))
    ),

    while_statement: $ => seq("while", $.expression, $.block),

    for_statement: $ => seq(
      optional("parallel"),
      "for",
      field("iterator", $.identifier),
      "in",
      $.expression,
      choice("to", ".."),
      $.expression,
      optional(seq("step", $.expression)),
      $.block
    ),

    expression_statement: $ => $.expression,

    expression: $ => choice(
      $.identifier,
      $.number,
      $.string,
      "true",
      "false",
      "null",
      $.array_literal,
      $.struct_literal,
      $.call_expression,
      $.field_expression,
      $.index_expression,
      $.unary_expression,
      $.binary_expression,
      $.parenthesized_expression
    ),

    array_literal: $ => seq("[", commaSep($.expression), "]"),

    struct_literal: $ => seq(
      field("type", $.identifier),
      "{",
      commaSep(seq($.identifier, ":", $.expression)),
      optional(","),
      "}"
    ),

    call_expression: $ => prec(9, seq(
      field("function", choice($.identifier, $.field_expression)),
      "(",
      commaSep($.expression),
      ")"
    )),

    field_expression: $ => prec.left(10, seq($.expression, ".", $.identifier)),
    index_expression: $ => prec.left(10, seq($.expression, "[", $.expression, "]")),
    parenthesized_expression: $ => seq("(", $.expression, ")"),

    unary_expression: $ => prec(8, seq(choice("-", "!", "not", "~", "&", "*"), $.expression)),

    binary_expression: $ => choice(
      prec.left(7, seq($.expression, choice("*", "/", "%"), $.expression)),
      prec.left(6, seq($.expression, choice("+", "-"), $.expression)),
      prec.left(5, seq($.expression, choice("<<", ">>"), $.expression)),
      prec.left(4, seq($.expression, choice("<", "<=", ">", ">="), $.expression)),
      prec.left(3, seq($.expression, choice("==", "!="), $.expression)),
      prec.left(2, seq($.expression, choice("&&", "and", "&", "^", "|"), $.expression)),
      prec.left(1, seq($.expression, choice("||", "or", "|>"), $.expression))
    )
  }
});

function commaSep(rule) {
  return optional(commaSep1(rule));
}

function commaSep1(rule) {
  return seq(rule, repeat(seq(",", rule)));
}
