module.exports = grammar({
  name: "flow",

  extras: $ => [
    /\s/,
    $.comment,
  ],

  word: $ => $.identifier,

  rules: {
    source_file: $ => repeat($._item),

    _item: $ => choice(
      $.attribute,
      $.import_declaration,
      $.module_declaration,
      $.function_declaration,
      $.struct_declaration,
      $.enum_declaration,
      $.type_declaration,
      $.trait_declaration,
      $.impl_declaration,
      $.effect_declaration,
      $.capability_declaration,
      $.extern_declaration,
      $.const_declaration,
      $.flow_declaration,
      $.statement,
    ),

    comment: _ => token(seq("#", /.*/)),

    attribute: $ => seq(
      "@",
      $.identifier,
      optional(seq("(", optional(commaSep1($.expression)), ")")),
    ),

    import_declaration: $ => seq(
      "import",
      choice($.string, $.identifier),
      optional(seq("{", optional(commaSep1($.identifier)), "}")),
    ),

    module_declaration: $ => seq("module", $.identifier),

    export_modifier: _ => "export",

    function_declaration: $ => seq(
      optional($.export_modifier),
      "function",
      field("name", $.identifier),
      optional($.type_parameters),
      field("parameters", $.parameter_list),
      optional(seq("->", field("return_type", $.type))),
      field("body", $.block),
    ),

    type_parameters: $ => seq("<", commaSep1($.identifier), ">"),

    parameter_list: $ => seq(
      "(",
      optional(commaSep1($.parameter)),
      ")",
    ),

    parameter: $ => seq(
      field("name", $.identifier),
      ":",
      field("type", $.type),
    ),

    struct_declaration: $ => seq(
      optional($.export_modifier),
      "struct",
      field("name", $.identifier),
      optional($.type_parameters),
      "{",
      repeat(choice($.attribute, $.field_declaration)),
      "}",
    ),

    field_declaration: $ => seq(
      field("name", $.identifier),
      ":",
      field("type", $.type),
      optional(","),
    ),

    enum_declaration: $ => seq(
      optional($.export_modifier),
      "enum",
      field("name", $.identifier),
      "{",
      optional(commaSep1($.enum_variant)),
      optional(","),
      "}",
    ),

    enum_variant: $ => seq(
      $.identifier,
      optional(seq("(", optional(commaSep1($.type)), ")")),
    ),

    type_declaration: $ => seq(
      optional($.export_modifier),
      "type",
      $.identifier,
      "=",
      $.type,
    ),

    trait_declaration: $ => seq(
      optional($.export_modifier),
      "trait",
      $.identifier,
      optional($.type_parameters),
      $.block,
    ),

    impl_declaration: $ => seq(
      "impl",
      $.identifier,
      optional(seq("for", $.type)),
      $.block,
    ),

    effect_declaration: $ => seq(
      optional($.export_modifier),
      "effect",
      $.identifier,
      "{",
      repeat($.effect_operation),
      "}",
    ),

    effect_operation: $ => seq(
      $.identifier,
      $.parameter_list,
      optional(seq("->", $.type)),
    ),

    capability_declaration: $ => seq(
      optional($.export_modifier),
      "capability",
      $.identifier,
      "{",
      repeat(choice($.effect_operation, $.function_declaration)),
      "}",
    ),

    extern_declaration: $ => seq(
      optional($.export_modifier),
      "extern",
      optional($.string),
      "{",
      repeat(choice($.extern_function, $.const_declaration)),
      "}",
    ),

    extern_function: $ => seq(
      "function",
      $.identifier,
      $.parameter_list,
      optional(seq("->", $.type)),
    ),

    const_declaration: $ => seq(
      optional($.export_modifier),
      "const",
      $.identifier,
      optional(seq(":", $.type)),
      "=",
      $.expression,
    ),

    flow_declaration: $ => seq(
      "flow",
      field("name", $.identifier),
      "{",
      repeat(choice(
        $.state_declaration,
        $.param_declaration,
        $.solver_declaration,
        $.evolution_statement,
        $.every_statement,
        $.statement,
      )),
      "}",
    ),

    state_declaration: $ => seq(
      "state",
      $.identifier,
      optional(seq(":", $.type)),
      optional(seq("=", $.expression)),
    ),

    param_declaration: $ => seq(
      "param",
      $.identifier,
      optional(seq(":", $.type)),
      optional(seq("=", $.expression)),
    ),

    solver_declaration: $ => seq(
      "solver",
      choice($.identifier, $.string),
    ),

    evolution_statement: $ => seq(
      $.expression,
      "evolves",
      "as",
      $.expression,
    ),

    every_statement: $ => seq(
      "every",
      $.expression,
      $.block,
    ),

    block: $ => seq("{", repeat($.statement), "}"),

    statement: $ => choice(
      $.variable_declaration,
      $.return_statement,
      $.if_statement,
      $.while_statement,
      $.for_statement,
      $.match_statement,
      $.break_statement,
      $.continue_statement,
      $.assignment_statement,
      $.expression_statement,
      $.block,
    ),

    variable_declaration: $ => seq(
      "let",
      optional("mut"),
      $.identifier,
      optional(seq(":", $.type)),
      "=",
      $.expression,
    ),

    return_statement: $ => seq("return", optional($.expression)),
    break_statement: _ => "break",
    continue_statement: _ => "continue",

    if_statement: $ => seq(
      "if",
      $.expression,
      $.block,
      repeat(seq("elif", $.expression, $.block)),
      optional(seq("else", $.block)),
    ),

    while_statement: $ => seq("while", $.expression, $.block),

    for_statement: $ => seq(
      optional("parallel"),
      "for",
      $.identifier,
      "in",
      $.expression,
      $.block,
    ),

    match_statement: $ => seq(
      "match",
      $.expression,
      "{",
      repeat($.match_arm),
      "}",
    ),

    match_arm: $ => seq(
      $.pattern,
      optional(seq("if", $.expression)),
      "=>",
      choice($.block, $.expression),
      optional(","),
    ),

    pattern: $ => choice(
      "_",
      $.literal,
      $.identifier,
      seq($.identifier, "(", optional(commaSep1($.pattern)), ")"),
      prec.left(1, seq($.pattern, "|", $.pattern)),
    ),

    assignment_statement: $ => seq(
      field("left", $.assignment_target),
      field("operator", choice("=", "+=", "-=", "*=", "/=", "%=")),
      field("right", $.expression),
    ),

    assignment_target: $ => choice(
      $.identifier,
      $.member_expression,
      $.index_expression,
    ),

    expression_statement: $ => $.expression,

    type: $ => choice(
      $.primitive_type,
      $.identifier,
      $.generic_type,
      $.array_type,
      $.function_type,
    ),

    primitive_type: _ => choice(
      "i8", "i16", "i32", "i64", "i128",
      "u8", "u16", "u32", "u64", "u128",
      "f32", "f64", "bool", "string", "void",
    ),

    generic_type: $ => seq(
      choice("array", "ptr", "vec", $.identifier),
      "<",
      commaSep1(choice($.type, $.integer)),
      ">",
    ),

    array_type: $ => seq("[", $.type, ";", $.integer, "]"),

    function_type: $ => seq(
      "(",
      optional(commaSep1($.type)),
      ")",
      "->",
      $.type,
    ),

    expression: $ => choice(
      $.lambda_expression,
      $.binary_expression,
      $.unary_expression,
      $.call_expression,
      $.member_expression,
      $.index_expression,
      $.struct_literal,
      $.array_literal,
      $.parenthesized_expression,
      $.literal,
      $.identifier,
    ),

    lambda_expression: $ => prec.right(seq(
      "|",
      optional(commaSep1($.identifier)),
      "|",
      choice($.expression, $.block),
    )),

    binary_expression: $ => choice(
      prec.left(1, seq($.expression, "|>", $.expression)),
      prec.left(2, seq($.expression, "or", $.expression)),
      prec.left(3, seq($.expression, "and", $.expression)),
      prec.left(4, seq($.expression, choice("==", "!="), $.expression)),
      prec.left(5, seq($.expression, choice("<", "<=", ">", ">="), $.expression)),
      prec.left(6, seq($.expression, choice("|", "^", "&"), $.expression)),
      prec.left(7, seq($.expression, choice("<<", ">>"), $.expression)),
      prec.left(8, seq($.expression, choice("+", "-"), $.expression)),
      prec.left(9, seq($.expression, choice("*", "/", "%"), $.expression)),
      prec.left(10, seq($.expression, "..", $.expression)),
      prec.left(10, seq($.expression, "to", $.expression, optional(seq("step", $.expression)))),
    ),

    unary_expression: $ => prec(11, seq(
      choice("-", "+", "!", "not", "~", "&", "*"),
      $.expression,
    )),

    call_expression: $ => prec(12, seq(
      field("function", $.expression),
      field("arguments", $.argument_list),
    )),

    argument_list: $ => seq(
      "(",
      optional(commaSep1($.expression)),
      ")",
    ),

    member_expression: $ => prec(13, seq(
      field("object", $.expression),
      ".",
      field("property", $.identifier),
    )),

    index_expression: $ => prec(13, seq(
      field("object", $.expression),
      "[",
      field("index", $.expression),
      "]",
    )),

    struct_literal: $ => seq(
      $.identifier,
      "{",
      optional(commaSep1($.field_initializer)),
      optional(","),
      "}",
    ),

    field_initializer: $ => seq($.identifier, ":", $.expression),

    array_literal: $ => seq(
      "[",
      optional(commaSep1($.expression)),
      optional(","),
      "]",
    ),

    parenthesized_expression: $ => seq("(", $.expression, ")"),

    literal: $ => choice(
      $.float,
      $.integer,
      $.string,
      $.boolean,
      $.null,
    ),

    boolean: _ => choice("true", "false"),
    null: _ => "null",

    integer: _ => token(choice(
      /0x[0-9a-fA-F]+/,
      /[0-9][0-9_]*/,
    )),

    float: _ => token(choice(
      /[0-9][0-9_]*\.[0-9][0-9_]*([eE][+-]?[0-9][0-9_]*)?/,
      /[0-9][0-9_]*[eE][+-]?[0-9][0-9_]*/,
    )),

    string: _ => token(seq(
      '"',
      repeat(choice(
        /[^"\\\n]/,
        /\\./,
      )),
      '"',
    )),

    identifier: _ => /[A-Za-z_][A-Za-z0-9_]*/,
  },
});

function commaSep1(rule) {
  return seq(rule, repeat(seq(",", rule)));
}
