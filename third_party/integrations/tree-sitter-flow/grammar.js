module.exports = grammar({
  name: "flow",

  extras: $ => [
    /\s/,
    $.comment,
  ],

  word: $ => $._identifier_token,

  conflicts: $ => [
    [$.function_declaration, $.identifier],
    [$.export_modifier, $.export_declaration],
    [$.analyze_statement, $.expression, $.dsl_arrow],
    [$.connect_declaration, $.identifier],
    [$.trait_declaration, $._statement],
    [$.sort_expression, $.identifier],
    [$.choose_expression, $.identifier],
    [$.module_declaration],
    [$._item, $._statement],
    [$.map_statement, $.identifier],
    [$.at_statement, $.identifier],
    [$.field_declaration_stmt, $.identifier],
    [$.vector_literal, $.binary_expression],
    [$.vector_literal, $.generic_type, $.binary_expression],
    [$.sort_expression],
    [$.type, $.sized_type, $.expression, $.list_call],
    [$.expression, $.sort_expression],
    [$.sized_type, $.expression],
    [$.sized_type, $.literal],
    [$.guillemet_type],
    [$.type, $.sized_type],
    [$.sized_type, $.expression, $.list_call],
    [$.proof_line, $.expression],
    [$.export_declaration],
    [$.variable_declaration, $.identifier],
    [$.type, $.struct_literal],
    [$.type, $.expression, $.list_call],
    [$.type, $.generic_type, $.expression],
    [$.type, $.struct_literal, $.pipeline_record],
    [$.analyze_statement, $.expression, $.dsl_arrow, $.dsl_setting],
    [$.generic_type, $.expression, $.dsl_setting],
    [$.proof_line],
    [$.field_declaration],
    [$.proof_atom, $.guillemet_type],
    [$.proof_atom],
    [$.analyze_statement, $.expression],
    [$.expression, $.pipeline_stage],
    [$.struct_literal, $.pipeline_record, $.dsl_block],
    [$.effect_ref],
    [$.expression, $.dsl_arrow],
    [$.expression, $.struct_literal, $.pipeline_record, $.dsl_named_block, $.dsl_setting],
    [$.dsl_arrow],
    [$.dsl_setting],
    [$.binary_expression, $.call_expression],
    [$.type, $.expression],
    [$.generic_type, $.expression],
    [$.expression, $.dsl_arrow, $.dsl_setting],
    [$.expression, $.list_call, $.dsl_setting],
    [$.expression, $.struct_literal, $.pipeline_record, $.dsl_setting],
    [$.expression, $.dsl_setting],
    [$.function_declaration],
    [$.horizon_declaration],
    [$.struct_literal, $.pipeline_record],
    [$.solver_setting],
    [$.dsl_arrow, $.dsl_setting],
    [$.expression, $.type_arguments],
    [$.binary_expression, $.unary_expression, $.call_expression],
    [$.assume_statement],
    [$.member_path],
    [$.assignment_target, $.pipeline_field],
    [$.unary_expression, $.assignment_target],
    [$.expression, $.assignment_target],
    [$.expression, $.assignment_statement],
    [$.binary_expression, $.unary_expression],
    [$.expression, $.unary_expression],
    [$.binary_expression, $.unary_expression, $.assignment_statement],
    [$.binary_expression, $.statement],
    [$.expression, $.statement],
    [$.member_path, $.index_expression],
    [$.member_path, $.expression],
    [$.sort_key, $.expression],
    [$.identifier, $.sort_key],
    [$.member_path, $.member_expression],
    [$.type, $.generic_type],
    [$._item, $.statement],
    [$.expression, $.struct_literal, $.pipeline_record],
    [$.expression, $.list_call],
    [$.block, $.pipeline_record],
  ],

  rules: {
    source_file: $ => repeat(choice(";", $._item)),

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
      $.theorem_declaration,
      $.export_declaration,
      $.extern_type_declaration,
      $.extern_const_declaration,
      $.ghost_declaration,
      $.dynamics_declaration,
      $.dsys_declaration,
      $.horizon_declaration,
      $.sense_declaration,
      $.ga_declaration,
      $.closed_declaration,
      $.couple_declaration,
      $.statement,
    ),

    comment: _ => token(seq("#", /.*/)),

    attribute: $ => prec.right(seq(
      "@",
      $.identifier,
      optional(seq("(", optional(commaSep1(choice($.expression, $.kwarg))), ")")),
    )),

    import_declaration: $ => prec.right(seq(
      optional($.export_modifier),
      "import",
      choice($.string, $.import_path),
      optional(seq("{", optional(commaSep1($.module_segment)), optional(","), "}")),
    )),

    import_path: _ => /[A-Za-z0-9_.+\/-]+/,

    dotted_name: $ => seq(
      repeat("."),
      $.module_segment,
      repeat(seq(".", $.module_segment)),
    ),

    module_segment: _ => /[A-Za-z_][A-Za-z0-9_-]*/,

    module_declaration: $ => seq(
      "module",
      $.identifier,
      optional(seq("{", repeat(choice(";", ",", $._item)), "}")),
    ),

    export_modifier: _ => "export",

    function_declaration: $ => seq(
      optional($.export_modifier),
      choice("function", "fn"),
      field("name", $.identifier),
      optional($.type_parameters),
      field("parameters", $.parameter_list),
      optional(seq("->", field("return_type", $.type))),
      optional(field("body", $.block)),
    ),

    type_parameters: $ => seq("<", commaSep1($.identifier), ">"),

    parameter_list: $ => seq(
      "(",
      optional(commaSep1(choice($.parameter, $.identifier, "..."))),
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
      repeat(choice($.attribute, $.field_declaration, $.has_property_statement, ",")),
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
      seq("{", repeat(choice(",", $.function_declaration, $.statement)), "}"),
    ),

    impl_declaration: $ => seq(
      "impl",
      $.identifier,
      optional(seq("for", $.type)),
      seq("{", repeat(choice(",", $.function_declaration, $.statement)), "}"),
    ),

    effect_declaration: $ => seq(
      optional($.export_modifier),
      "effect",
      $.identifier,
      "{",
      repeat(choice(",", $.effect_operation, $.function_declaration)),
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
      repeat(choice(",", $.effect_operation, $.function_declaration, $.effect_ref)),
      "}",
    ),

    effect_ref: $ => seq("effect", commaSep1($.identifier), optional(",")),

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
      optional(seq("=", $.expression)),
    ),

    flow_declaration: $ => seq(
      "flow",
      field("name", $.identifier),
      "{",
      repeat(choice(
        $.state_declaration,
        $.param_declaration,
        $.port_declaration,
        $.flow_member_declaration,
        $.connect_declaration,
        $.dsl_arrow,
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

    solver_declaration: $ => choice(
      seq("solver", choice($.identifier, $.string)),
      seq("solver", "{", repeat($.solver_setting), "}"),
    ),

    solver_setting: $ => seq(
      $.identifier,
      $.expression,
      optional($.identifier),
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
      optional($.identifier),
      $.block,
    ),

    block: $ => seq("{", repeat(choice(";", ",", $.statement)), "}"),

    statement: $ => seq(
      repeat($.attribute),
      $._statement,
    ),

    _statement: $ => choice(
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
      $.assume_statement,
      $.assume_loose,
      $.therefore_statement,
      $.handle_statement,
      $.guide_statement,
      $.analyze_statement,
      $.has_property_statement,
      $.at_statement,
      $.map_statement,
      $.field_declaration_stmt,
      $.function_declaration,
      $.block,
    ),

    // assume Postulate 3: a circle can be drawn ...
    assume_statement: $ => seq(
      "assume",
      repeat(choice($.guillemet_label, $.identifier, /\d+/, /[A-Za-z_][\w.+\/-]*/)),
      optional($.argument_list),
      optional(seq(choice(":", "="), choice($.proof_line, /[^\n]+/))),
    ),
    assume_loose: $ => seq("assume", /[^\n]+/),

    proof_atom: $ => seq(
      repeat1($.guillemet_label),
      optional($.argument_list),
    ),

    proof_line: $ => seq(
      choice($.proof_atom, $.expression),
      repeat(seq(choice("=", "==", "<=", "<", ">=", ">", ":"), choice($.proof_atom, $.expression))),
    ),

    therefore_statement: $ => choice(
      seq("therefore", $.proof_line),
      seq("therefore", /[^\n]+/),
    ),

    has_property_statement: $ => seq("has", "property", $.expression),

    guide_statement: $ => seq(
      "guide",
      repeat(choice($.identifier, $.literal, "with", "through", "using", "over", "->")),
      $.dsl_block,
    ),

    analyze_statement: $ => seq(
      repeat(seq(choice("dynamics", $.identifier), ".")),
      "analyze",
      $.identifier,
      repeat(choice($.identifier, $.literal)),
      optional(seq("over", $.identifier)),
      optional(seq("->", repeat1($.identifier))),
      $.dsl_block,
    ),

    handle_statement: $ => seq(
      "handle",
      commaSep1($.identifier),
      "with",
      commaSep1($.identifier),
      $.block,
    ),

    field_declaration_stmt: $ => seq(
      "field",
      $.identifier,
      optional(seq(":", $.type)),
      optional(seq("on", $.identifier)),
      optional(seq("=", $.expression)),
    ),

    at_statement: $ => seq(
      "at",
      "(",
      optional(commaSep1(seq($.identifier, ":", $.expression))),
      ")",
    ),

    map_statement: $ => seq(
      "map",
      $.identifier,
      "in",
      $.expression,
      "->",
      $.expression,
    ),

    port_declaration: $ => seq(
      choice("input", "output"),
      $.identifier,
      optional(seq(":", $.type)),
      optional(seq("=", $.expression)),
    ),

    flow_member_declaration: $ => seq(
      $.identifier,
      ":",
      $.type,
      optional(seq("=", $.expression)),
    ),

    connect_declaration: $ => seq(
      "connect",
      "{",
      repeat($.dsl_arrow),
      "}",
    ),

    variable_declaration: $ => seq(
      choice("let", "var"),
      optional("mut"),
      $.identifier,
      optional(seq(":", $.type)),
      optional(seq("=", $.expression)),
    ),

    return_statement: $ => prec.right(seq("return", optional($.expression))),
    break_statement: _ => "break",
    continue_statement: _ => "continue",

    if_statement: $ => seq(
      "if",
      $.expression,
      $.block,
      repeat(seq("elif", $.expression, $.block)),
      repeat(seq("else", "if", $.expression, $.block)),
      optional(seq("else", $.block)),
    ),

    while_statement: $ => seq("while", $.expression, $.block),

    for_statement: $ => seq(
      optional("parallel"),
      "for",
      $.identifier,
      "in",
      $.expression,
      optional(seq("step", $.expression)),
      $.block,
    ),

    match_statement: $ => seq(
      "match",
      $.expression,
      "{",
      repeat($.match_arm),
      "}",
    ),

    match_arm: $ => choice(
      seq("default", $.block, optional(",")),
      seq(
        $.pattern,
        optional(seq("if", $.expression)),
        "=>",
        choice($.block, $.expression),
        optional(","),
      ),
    ),

    pattern: $ => choice(
      "_",
      "default",
      seq("[", optional(commaSep1($.pattern)), "]"),
      $.literal,
      $.identifier,
      seq($.identifier, "(", optional(commaSep1($.pattern)), ")"),
      prec.left(1, seq($.pattern, "|", $.pattern)),
    ),

    assignment_statement: $ => prec.right(seq(
      field("left", $.assignment_target),
      field("operator", choice("=", "+=", "-=", "*=", "/=", "%=")),
      field("right", choice($.expression, $.assignment_statement)),
    )),

    assignment_target: $ => choice(
      $.identifier,
      $.member_expression,
      $.index_expression,
      $.unary_expression,
      $.parenthesized_expression,
    ),

    expression_statement: $ => $.expression,

    type: $ => choice(
      $.primitive_type,
      $.identifier,
      $.generic_type,
      $.array_type,
      $.function_type,
      $.reference_type,
      $.slice_type,
      $.sized_type,
      $.guillemet_type,
      $.capability_type,
    ),

    capability_type: $ => seq("capability", $.identifier),

    guillemet_type: $ => repeat1($.guillemet_label),

    reference_type: $ => seq("&", optional("mut"), $.type),

    slice_type: $ => seq("[", $.type, "]"),

    sized_type: $ => seq(
      choice($.primitive_type, $.identifier, $.generic_type),
      "[",
      choice($.integer, $.identifier),
      "]",
    ),

    primitive_type: _ => choice(
      "i8", "i16", "i32", "i64", "i128",
      "u8", "u16", "u32", "u64", "u128",
      "f32", "f64", "bool", "string", "void",
    ),

    generic_type: $ => seq(
      $.identifier,
      "<",
      commaSep1(choice($.type, seq("mut", $.type), $.integer)),
      ">",
    ),

    array_type: $ => seq("[", $.type, ";", $.expression, "]"),

    function_type: $ => seq(
      optional("cfn"),
      "(",
      optional(commaSep1($.type)),
      ")",
      "->",
      $.type,
    ),

    expression: $ => choice(
      $.lambda_expression,
      $.pipeline_record,
      $.list_call,
      $.binary_expression,
      $.unary_expression,
      $.call_expression,
      $.member_expression,
      $.index_expression,
      $.struct_literal,
      $.array_literal,
      $.parenthesized_expression,
      $.vector_literal,
      $.member_path,
      $.sort_key,
      $.try_expression,
      $.proof_atom,
      $.literal,
      $.identifier,
    ),

    vector_literal: $ => seq("<", commaSep1($.expression), token.immediate(">")),

    try_expression: $ => prec(14, seq($.expression, choice("?", "!"))),

    kwarg: $ => seq($.identifier, choice("=", ":"), $.expression),

    lambda_expression: $ => prec.right(seq(
      "|",
      optional(commaSep1(choice($.identifier, $.parameter))),
      "|",
      optional(seq("->", $.type)),
      choice($.expression, $.block),
    )),

    binary_expression: $ => choice(
      prec.left(1, seq($.expression, "|>", $.pipeline_stage)),
      prec.left(2, seq($.expression, choice("or", "||"), $.expression)),
      prec.left(3, seq($.expression, choice("and", "&&"), $.expression)),
      prec.left(4, seq($.expression, choice("==", "!=", "in", "not in", "∈", "∉"), $.expression)),
      prec.left(4, seq($.expression, choice("∪", "∩", "\\", "⊆", "⊂"), $.expression)),
      prec.left(5, seq($.expression, choice("<", "<=", ">", ">="), $.expression)),
      prec.left(6, seq($.expression, choice("|", "^", "&"), $.expression)),
      prec.left(7, seq($.expression, choice("<<", ">>"), $.expression)),
      prec.left(8, seq($.expression, choice("+", "-"), $.expression)),
      prec.left(9, seq($.expression, choice("*", "/", "%", "mod", "div"), $.expression)),
      prec.left(10, seq($.expression, choice("..", "to"), $.expression, optional(seq("step", $.expression)))),
      prec.left(10, seq($.expression, "as", $.type)),
    ),

    unary_expression: $ => prec(11, seq(
      choice("-", "+", "!", "not", "~", "&", "*"),
      $.expression,
    )),

    call_expression: $ => prec(12, seq(
      field("function", $.expression),
      optional($.type_arguments),
      field("arguments", $.argument_list),
    )),

    type_arguments: $ => seq("<", commaSep1($.type), ">"),

    argument_list: $ => seq(
      "(",
      optional(commaSep1(choice($.expression, $.kwarg))),
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
      choice($.identifier, $.generic_type),
      "{",
      optional(commaSep1(choice($.field_initializer, $.spread_field))),
      optional(","),
      "}",
    ),

    extern_type_declaration: $ => seq("extern", "type", $.identifier),

    extern_const_declaration: $ => seq("extern", $.const_declaration),

    ghost_declaration: $ => seq(
      "ghost",
      "type",
      $.identifier,
      optional($.type_parameters),
      "{",
      repeat(choice(",", $.field_declaration)),
      "}",
    ),

    export_declaration: $ => seq(
      "export",
      repeat1(choice($.guillemet_label, $.identifier)),
    ),

    // theorem «Domain» «Source» «Title» () { ... }
    theorem_declaration: $ => seq(
      "theorem",
      repeat(choice($.guillemet_label, /[A-Za-z_][A-Za-z0-9_.\/+\-]*/)),
      $.parameter_list,
      $.block,
    ),

    guillemet_label: _ => /«[^»]*»/,

    field_initializer: $ => seq($.identifier, ":", $.expression),

    spread_field: $ => seq("..", $.expression),

    array_literal: $ => seq(
      "[",
      optional(choice(
        seq($.expression, ";", $.expression),
        commaSep1($.expression),
      )),
      optional(","),
      "]",
    ),

    parenthesized_expression: $ => seq("(", $.expression, ")"),

    // x |> Stats { doubled = twice } and x |> { doubled = twice }
    pipeline_record: $ => seq(
      optional($.identifier),
      "{",
      optional(commaSep1($.pipeline_field)),
      optional(","),
      "}",
    ),

    pipeline_field: $ => seq($.identifier, "=", $.expression),

    pipeline_stage: $ => choice(
      $.choose_expression,
      $.sort_expression,
      $.list_call,
      $.expression,
    ),

    // x |> choose m.tag { Mode_A => f, Mode_B => g }
    choose_expression: $ => seq(
      "choose",
      $.expression,
      "{",
      optional(commaSep1($.choose_arm)),
      optional(","),
      "}",
    ),

    choose_arm: $ => seq($.expression, "=>", $.expression),

    // x |> sortBy [desc .score, asc .name]
    list_call: $ => seq(
      $.identifier,
      $.array_literal,
    ),

    sort_key: $ => seq(
      choice("asc", "desc"),
      $.member_path,
    ),

    member_path: $ => prec(13, seq(".", $.identifier, repeat(seq(".", $.identifier)))),

    // dynamics DSL: dynamics { dsys ... } or bare dsys/horizon/sense/ga/closed
    dynamics_declaration: $ => seq("dynamics", $.dsl_block),

    dsl_block: $ => seq(
      "{",
      repeat(choice(";", $.dsl_item)),
      "}",
    ),

    dsl_item: $ => choice(
      $.flow_member_declaration,
      $.port_declaration,
      $.state_declaration,
      $.param_declaration,
      $.dsl_arrow,
      $.dsl_named_block,
      $.dsl_setting,
      $.dsys_declaration,
      $.horizon_declaration,
      $.sense_declaration,
      $.ga_declaration,
      $.closed_declaration,
      $.couple_declaration,
      $.statement,
    ),

    dsys_declaration: $ => seq("dsys", $.identifier, $.dsl_block),

    horizon_declaration: $ => seq(
      "horizon",
      $.identifier,
      repeat(choice($.identifier, $.literal)),
    ),

    sense_declaration: $ => seq(
      "sense",
      "on",
      $.identifier,
      $.dsl_block,
    ),

    ga_declaration: $ => seq(
      "ga",
      "evolve",
      "on",
      $.identifier,
      "over",
      $.identifier,
      "->",
      repeat1($.identifier),
      $.dsl_block,
    ),

    couple_declaration: $ => seq(
      "couple",
      repeat(choice($.identifier, $.literal)),
      "using",
      repeat1(choice($.identifier, $.literal)),
      $.dsl_block,
    ),

    closed_declaration: $ => seq(
      "closed",
      $.identifier,
      "with",
      repeat1($.identifier),
      $.dsl_block,
    ),

    dsl_arrow: $ => seq(
      repeat(choice($.identifier, $.literal, ".")),
      "->",
      repeat1(choice($.identifier, ".", $.literal)),
    ),

    dsl_named_block: $ => seq($.identifier, $.dsl_block),

    dsl_setting: $ => seq(
      $.identifier,
      repeat(choice($.identifier, $.literal)),
    ),

    // x |> sort by [.name] stable
    sort_expression: $ => seq(
      "sort",
      repeat(choice(
        "ascending", "descending", "unique", "stable", "gpu", "cpu",
        seq("by", choice($.array_literal, $.member_path, $.expression)),
        seq("with", $.expression),
      )),
    ),

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
        /[^"\\]/,
        /\\./,
      )),
      '"',
    )),

    identifier: $ => choice(
      $._identifier_token,
      "var", "has", "map", "sort", "choose", "asc", "desc",
      "field", "connect", "at", "fn",
    ),

    _identifier_token: _ => /[\p{L}_][\p{L}\p{N}_]*/,
  },
});

function commaSep1(rule) {
  return seq(rule, repeat(seq(",", rule)));
}
