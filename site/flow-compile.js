/**
 * Flow browser interpreter.
 *
 * A real lexer + recursive-descent parser + tree-walking evaluator for the
 * subset of Flow used by the tutorials and the playground. It executes the
 * program starting at main() and captures stdout, with C-compatible integer,
 * float and printf semantics so that browser output matches `./flow run`.
 *
 * It never guesses. Anything outside the supported subset (imports, effects,
 * capabilities, generics, GPU kernels, unknown externs) is reported as an
 * explicit "not supported in the browser interpreter" notice instead of
 * producing invented output.
 *
 * Dependency-free plain browser JS. No build step.
 */
(function (global) {
  'use strict';

  var STEP_LIMIT = 5000000;
  var DEPTH_LIMIT = 2000;
  var OUTPUT_LIMIT = 4 * 1024 * 1024;

  var NATIVE_HINT = 'Run it natively with ./flow run <file>.flow';

  /* ==================================================================== *
   * Errors
   * ==================================================================== */

  function FlowError(message, line) {
    this.name = 'FlowError';
    this.line = line || 0;
    this.rawMessage = message;
    this.message = this.line ? 'line ' + this.line + ': ' + message : message;
  }
  FlowError.prototype = Object.create(Error.prototype);
  FlowError.prototype.constructor = FlowError;

  function Unsupported(construct, line, detail) {
    this.name = 'Unsupported';
    this.construct = construct;
    this.line = line || 0;
    this.detail = detail || '';
    this.message =
      construct +
      (this.line ? ' (line ' + this.line + ')' : '') +
      ' is not supported in the browser interpreter — ' +
      NATIVE_HINT +
      '.' +
      (this.detail ? ' ' + this.detail : '');
  }
  Unsupported.prototype = Object.create(Error.prototype);
  Unsupported.prototype.constructor = Unsupported;

  /* ==================================================================== *
   * Lexer
   * ==================================================================== */

  var KEYWORDS = {
    'function': 'FUNCTION', 'let': 'LET', 'mut': 'MUT', 'return': 'RETURN',
    'if': 'IF', 'else': 'ELSE', 'elif': 'ELIF', 'while': 'WHILE', 'for': 'FOR',
    'break': 'BREAK', 'continue': 'CONTINUE', 'in': 'IN', 'to': 'TO',
    'import': 'IMPORT', 'export': 'EXPORT', 'extern': 'EXTERN',
    'const': 'CONST', 'struct': 'STRUCT', 'enum': 'ENUM', 'match': 'MATCH',
    'default': 'DEFAULT', 'true': 'TRUE', 'false': 'FALSE', 'null': 'NULL',
    'as': 'AS', 'effect': 'EFFECT', 'capability': 'CAPABILITY',
    'handle': 'HANDLE', 'with': 'WITH', 'trait': 'TRAIT', 'impl': 'IMPL',
    'test': 'TEST', 'module': 'MODULE', 'distinct': 'DISTINCT',
    'defer': 'DEFER', 'parallel': 'PARALLEL', 'theorem': 'THEOREM',
    'expect': 'EXPECT', 'dbg': 'DBG', 'type': 'TYPE',
    // Word forms of the logical operators, exactly as the native lexer maps them.
    'and': 'ANDAND', 'or': 'OROR', 'not': 'NOT'
    // `step` is contextual: it is only a keyword directly after a for-range,
    // so it stays an identifier here (matching the native lexer).
  };

  var RULES = [
    ['COMMENT', /#[^\n]*/y],
    ['NEWLINE', /\n/y],
    ['WS', /[ \t\r\f\v]+/y],
    ['ARROW', /->/y],
    ['FAT_ARROW', /=>/y],
    ['QUESTION', /\?/y],
    ['EQ', /==/y],
    ['NE', /!=/y],
    ['SHL', /<</y],
    ['SHR', />>/y],
    ['LE', /<=/y],
    ['GE', />=/y],
    ['ANDAND', /&&/y],
    ['OROR', /\|\|/y],
    ['PIPELINE', /\|>/y],
    ['PIPE', /\|/y],
    ['AMP', /&/y],
    ['CARET', /\^/y],
    ['TILDE', /~/y],
    ['DOTDOT', /\.\./y],
    ['DCOLON', /::/y],
    ['PLUS_ASSIGN', /\+=/y],
    ['MINUS_ASSIGN', /-=/y],
    ['STAR_ASSIGN', /\*=/y],
    ['SLASH_ASSIGN', /\/=/y],
    ['PERCENT_ASSIGN', /%=/y],
    ['PLUS', /\+/y],
    ['MINUS', /-/y],
    ['STAR', /\*/y],
    ['SLASH', /\//y],
    ['PERCENT', /%/y],
    ['LT', /</y],
    ['GT', />/y],
    ['ASSIGN', /=/y],
    ['NOT', /!/y],
    ['LPAREN', /\(/y],
    ['RPAREN', /\)/y],
    ['LBRACE', /\{/y],
    ['RBRACE', /\}/y],
    ['LBRACKET', /\[/y],
    ['RBRACKET', /\]/y],
    ['SEMI', /;/y],
    ['COLON', /:/y],
    ['COMMA', /,/y],
    ['DOT', /\./y],
    ['AT', /@/y],
    ['STRING', /"(?:[^"\\]|\\.)*"/y],
    ['NUMBER', /0x[0-9a-fA-F]+|[0-9]+\.[0-9]+(?:[eE][+-]?[0-9]+)?|[0-9]+[eE][+-]?[0-9]+|[0-9]+/y],
    ['IDENT', /[A-Za-z_][A-Za-z0-9_]*/y]
  ];

  function lex(src) {
    var tokens = [];
    var pos = 0;
    var line = 1;
    var n = src.length;
    while (pos < n) {
      var matched = false;
      for (var i = 0; i < RULES.length; i++) {
        var name = RULES[i][0];
        var re = RULES[i][1];
        re.lastIndex = pos;
        var m = re.exec(src);
        if (!m) continue;
        var text = m[0];
        matched = true;
        if (name === 'NEWLINE') {
          line++;
        } else if (name !== 'WS' && name !== 'COMMENT') {
          var type = name;
          if (name === 'IDENT' && Object.prototype.hasOwnProperty.call(KEYWORDS, text)) {
            type = KEYWORDS[text];
          }
          tokens.push({ type: type, value: text, line: line });
        }
        pos += text.length;
        break;
      }
      if (!matched) {
        throw new FlowError("unexpected character '" + src[pos] + "'", line);
      }
    }
    tokens.push({ type: 'EOF', value: '', line: line });
    return tokens;
  }

  /* ==================================================================== *
   * Types
   * ==================================================================== */

  function intType(name, bits, signed) {
    return { k: 'int', name: name, bits: bits, signed: signed };
  }

  var TY = {
    i8: intType('i8', 8, true),
    i16: intType('i16', 16, true),
    i32: intType('i32', 32, true),
    i64: intType('i64', 64, true),
    u8: intType('u8', 8, false),
    u16: intType('u16', 16, false),
    u32: intType('u32', 32, false),
    u64: intType('u64', 64, false),
    f32: { k: 'float', name: 'f32', bits: 32 },
    f64: { k: 'float', name: 'f64', bits: 64 },
    bool: { k: 'bool', name: 'bool' },
    string: { k: 'string', name: 'string' },
    'void': { k: 'void', name: 'void' }
  };

  function ptrType(elem) {
    return { k: 'ptr', name: 'ptr<' + elem.name + '>', elem: elem };
  }
  function arrayType(elem, len) {
    return { k: 'array', name: '[' + elem.name + '; ' + len + ']', elem: elem, len: len };
  }
  function structType(name) {
    return { k: 'struct', name: name };
  }

  var PTR_VOID = ptrType(TY['void']);

  /* ==================================================================== *
   * Parser
   * ==================================================================== */

  function Parser(tokens, structNames) {
    this.toks = tokens;
    this.i = 0;
    this.structNames = structNames;
  }

  Parser.prototype.peek = function (k) {
    return this.toks[this.i + (k || 0)];
  };
  Parser.prototype.at = function (type) {
    return this.toks[this.i].type === type;
  };
  Parser.prototype.next = function () {
    return this.toks[this.i++];
  };
  Parser.prototype.line = function () {
    return this.toks[this.i].line;
  };
  Parser.prototype.accept = function (type) {
    if (this.toks[this.i].type === type) return this.toks[this.i++];
    return null;
  };
  Parser.prototype.expect = function (type, what) {
    var t = this.toks[this.i];
    if (t.type !== type) {
      throw new FlowError(
        'expected ' + (what || type) + " but found '" + (t.value || 'end of file') + "'",
        t.line
      );
    }
    this.i++;
    return t;
  };

  var PRIMITIVE_TYPES = {
    i8: 1, i16: 1, i32: 1, i64: 1, u8: 1, u16: 1, u32: 1, u64: 1,
    f32: 1, f64: 1, bool: 1, string: 1, 'void': 1
  };

  Parser.prototype.parseType = function () {
    var t = this.peek();
    if (t.type === 'LBRACKET') {
      // [T; N]
      this.next();
      var elem = this.parseType();
      this.expect('SEMI', "';' in array type");
      var lenTok = this.expect('NUMBER', 'array length');
      this.expect('RBRACKET', "']'");
      return arrayType(elem, parseInt(lenTok.value, 10));
    }
    if (t.type !== 'IDENT') {
      throw new FlowError("expected a type but found '" + t.value + "'", t.line);
    }
    this.next();
    var name = t.value;
    if (name === 'ptr') {
      this.expect('LT', "'<' after ptr");
      var pe = this.parseType();
      this.expect('GT', "'>'");
      return ptrType(pe);
    }
    if (name === 'array') {
      this.expect('LT', "'<' after array");
      var ae = this.parseType();
      var alen = -1;
      if (this.accept('COMMA')) {
        alen = parseInt(this.expect('NUMBER', 'array length').value, 10);
      }
      this.expect('GT', "'>'");
      return alen >= 0 ? arrayType(ae, alen) : ptrType(ae);
    }
    if (name === 'vec') {
      throw new Unsupported('the vec<T> type', t.line);
    }
    if (this.at('LT')) {
      throw new Unsupported('generic type ' + name + '<...>', t.line);
    }
    if (PRIMITIVE_TYPES[name]) return TY[name];
    return structType(name);
  };

  /* ---- declarations ---- */

  var ALLOWED_EXTERNS = {
    malloc: 1, calloc: 1, realloc: 1, free: 1,
    memcpy: 1, memmove: 1, memset: 1,
    printf: 1, puts: 1, putchar: 1,
    strlen: 1, abs: 1,
    sqrt: 1, sin: 1, cos: 1, tan: 1, pow: 1, exp: 1, log: 1, fabs: 1,
    floor: 1, ceil: 1, round: 1, fmod: 1
  };

  Parser.prototype.parseProgram = function () {
    var prog = {
      structs: Object.create(null),
      structOrder: [],
      functions: Object.create(null),
      functionOrder: [],
      consts: [],
      externs: Object.create(null)
    };
    while (!this.at('EOF')) {
      var t = this.peek();
      switch (t.type) {
        case 'IMPORT':
          throw new Unsupported(
            'the import statement',
            t.line,
            'Module and stdlib imports are not resolved in the browser.'
          );
        case 'EXPORT':
          this.next();
          continue;
        case 'EXTERN':
          this.parseExtern(prog);
          continue;
        case 'STRUCT':
          this.parseStruct(prog);
          continue;
        case 'FUNCTION':
          this.parseFunction(prog, false);
          continue;
        case 'CONST':
          this.parseConst(prog);
          continue;
        case 'EFFECT':
          throw new Unsupported('effect declarations', t.line);
        case 'CAPABILITY':
          throw new Unsupported('capability declarations', t.line);
        case 'TRAIT':
          throw new Unsupported('trait declarations', t.line);
        case 'IMPL':
          throw new Unsupported('impl blocks', t.line);
        case 'ENUM':
          throw new Unsupported('enum declarations', t.line);
        case 'TEST':
          throw new Unsupported('test blocks', t.line);
        case 'MODULE':
          throw new Unsupported('module declarations', t.line);
        case 'THEOREM':
          throw new Unsupported('theorem declarations', t.line);
        case 'DISTINCT':
          throw new Unsupported('distinct type declarations', t.line);
        case 'TYPE':
          throw new Unsupported('type aliases', t.line);
        case 'AT':
          throw new Unsupported(
            'the @' + (this.peek(1) ? this.peek(1).value : '') + ' attribute',
            t.line
          );
        case 'IDENT':
          throw new FlowError("unexpected '" + t.value + "' at top level", t.line);
        default:
          throw new FlowError("unexpected '" + t.value + "' at top level", t.line);
      }
    }
    return prog;
  };

  Parser.prototype.parseExtern = function (prog) {
    var start = this.expect('EXTERN');
    if (this.at('LBRACE')) {
      this.next();
      while (!this.at('RBRACE')) {
        if (this.at('EOF')) throw new FlowError('unterminated extern block', start.line);
        this.parseExternFn(prog);
      }
      this.expect('RBRACE');
      return;
    }
    this.parseExternFn(prog);
  };

  Parser.prototype.parseExternFn = function (prog) {
    var t = this.expect('FUNCTION', "'function' inside extern");
    var name = this.expect('IDENT', 'function name').value;
    if (!ALLOWED_EXTERNS[name]) {
      throw new Unsupported(
        "the extern function '" + name + "'",
        t.line,
        'Only the C memory/string/math externs used by the tutorials are emulated.'
      );
    }
    this.expect('LPAREN');
    while (!this.at('RPAREN')) {
      if (this.at('EOF')) throw new FlowError('unterminated parameter list', t.line);
      this.next();
    }
    this.expect('RPAREN');
    if (this.accept('ARROW')) this.parseType();
    prog.externs[name] = true;
  };

  Parser.prototype.parseStruct = function (prog) {
    var t = this.expect('STRUCT');
    var name = this.expect('IDENT', 'struct name').value;
    if (this.at('LT')) throw new Unsupported('generic structs', t.line);
    this.expect('LBRACE');
    var fields = [];
    while (!this.at('RBRACE')) {
      if (this.at('EOF')) throw new FlowError('unterminated struct body', t.line);
      var fname = this.expect('IDENT', 'field name').value;
      this.expect('COLON', "':' after field name");
      var ftype = this.parseType();
      fields.push({ name: fname, type: ftype });
      if (!this.accept('COMMA')) {
        if (!this.at('RBRACE')) {
          // newline-separated fields are fine; keep going
          if (this.at('IDENT')) continue;
        }
      }
    }
    this.expect('RBRACE');
    if (prog.structs[name]) {
      throw new FlowError("struct '" + name + "' declared twice", t.line);
    }
    prog.structs[name] = { name: name, fields: fields, line: t.line };
    prog.structOrder.push(name);
  };

  Parser.prototype.parseConst = function (prog) {
    var t = this.expect('CONST');
    var name = this.expect('IDENT', 'constant name').value;
    var type = null;
    if (this.accept('COLON')) type = this.parseType();
    this.expect('ASSIGN', "'=' in const declaration");
    var value = this.parseExpression();
    prog.consts.push({ name: name, type: type, value: value, line: t.line });
  };

  Parser.prototype.parseFunction = function (prog) {
    var t = this.expect('FUNCTION');
    var name = this.expect('IDENT', 'function name').value;
    if (this.at('LT')) {
      throw new Unsupported('generic functions', t.line, 'Monomorphization happens in the native compiler.');
    }
    this.expect('LPAREN');
    var params = [];
    while (!this.at('RPAREN')) {
      this.accept('MUT');
      var pname = this.expect('IDENT', 'parameter name').value;
      this.expect('COLON', "':' after parameter name");
      var ptype = this.parseType();
      params.push({ name: pname, type: ptype });
      if (!this.accept('COMMA')) break;
    }
    this.expect('RPAREN');
    var ret = TY['void'];
    if (this.accept('ARROW')) ret = this.parseType();
    if (this.at('WITH')) {
      throw new Unsupported('effect annotations (with ...)', this.line());
    }
    var body = this.parseBlock();
    if (prog.functions[name]) {
      throw new FlowError("function '" + name + "' declared twice", t.line);
    }
    prog.functions[name] = {
      name: name, params: params, ret: ret, body: body, line: t.line
    };
    prog.functionOrder.push(name);
  };

  /* ---- statements ---- */

  Parser.prototype.parseBlock = function () {
    var open = this.expect('LBRACE', "'{'");
    var stmts = [];
    while (!this.at('RBRACE')) {
      if (this.at('EOF')) throw new FlowError('unterminated block', open.line);
      stmts.push(this.parseStatement());
    }
    this.expect('RBRACE');
    return { kind: 'Block', body: stmts, line: open.line };
  };

  Parser.prototype.parseStatement = function () {
    var t = this.peek();
    switch (t.type) {
      case 'LET': return this.parseLet();
      case 'RETURN': return this.parseReturn();
      case 'IF': return this.parseIf();
      case 'WHILE': return this.parseWhile();
      case 'FOR': return this.parseFor();
      case 'MATCH': return this.parseMatch();
      case 'BREAK': this.next(); return { kind: 'Break', line: t.line };
      case 'CONTINUE': this.next(); return { kind: 'Continue', line: t.line };
      case 'LBRACE': return this.parseBlock();
      case 'SEMI': this.next(); return { kind: 'Empty', line: t.line };
      case 'DEFER': throw new Unsupported('defer statements', t.line);
      case 'HANDLE': throw new Unsupported('handle/with effect blocks', t.line);
      case 'EXPECT': throw new Unsupported('expect assertions', t.line);
      case 'DBG': throw new Unsupported('the dbg operator', t.line);
      case 'PARALLEL': throw new Unsupported('parallel for loops', t.line);
      case 'FUNCTION': throw new Unsupported('nested function declarations', t.line);
      case 'EFFECT': throw new Unsupported('effect declarations', t.line);
      case 'CAPABILITY': throw new Unsupported('capability declarations', t.line);
      case 'AT': throw new Unsupported('statement attributes', t.line);
      default: break;
    }
    var expr = this.parseExpression();
    var op = this.peek();
    var COMPOUND = {
      ASSIGN: '=', PLUS_ASSIGN: '+', MINUS_ASSIGN: '-',
      STAR_ASSIGN: '*', SLASH_ASSIGN: '/', PERCENT_ASSIGN: '%'
    };
    if (Object.prototype.hasOwnProperty.call(COMPOUND, op.type)) {
      this.next();
      var rhs = this.parseExpression();
      return {
        kind: 'Assign', target: expr, op: COMPOUND[op.type], value: rhs, line: op.line
      };
    }
    return { kind: 'ExprStmt', expr: expr, line: t.line };
  };

  Parser.prototype.parseLet = function () {
    var t = this.expect('LET');
    var isMut = !!this.accept('MUT');
    var name = this.expect('IDENT', 'variable name').value;
    var type = null;
    if (this.accept('COLON')) type = this.parseType();
    this.expect('ASSIGN', "'=' in let declaration");
    var value = this.parseExpression();
    return { kind: 'Let', name: name, mut: isMut, type: type, value: value, line: t.line };
  };

  var STMT_START = {
    LET: 1, RETURN: 1, IF: 1, WHILE: 1, FOR: 1, MATCH: 1, BREAK: 1,
    CONTINUE: 1, RBRACE: 1, EOF: 1, FUNCTION: 1, STRUCT: 1
  };

  Parser.prototype.parseReturn = function () {
    var t = this.expect('RETURN');
    if (STMT_START[this.peek().type]) {
      return { kind: 'Return', value: null, line: t.line };
    }
    var v = this.parseExpression();
    return { kind: 'Return', value: v, line: t.line };
  };

  Parser.prototype.parseIf = function () {
    var t = this.next(); // IF or ELIF
    var cond = this.parseExpression();
    var then = this.parseBlock();
    var otherwise = null;
    if (this.at('ELIF')) {
      otherwise = { kind: 'Block', body: [this.parseIf()], line: this.line() };
    } else if (this.accept('ELSE')) {
      if (this.at('IF')) {
        otherwise = { kind: 'Block', body: [this.parseIf()], line: this.line() };
      } else {
        otherwise = this.parseBlock();
      }
    }
    return { kind: 'If', cond: cond, then: then, otherwise: otherwise, line: t.line };
  };

  Parser.prototype.parseWhile = function () {
    var t = this.expect('WHILE');
    var cond = this.parseExpression();
    var body = this.parseBlock();
    return { kind: 'While', cond: cond, body: body, line: t.line };
  };

  Parser.prototype.parseFor = function () {
    var t = this.expect('FOR');
    var name = this.expect('IDENT', 'loop variable').value;
    this.expect('IN', "'in'");
    var start = this.parseExpression();
    var end;
    if (this.accept('TO')) {
      end = this.parseExpression();
    } else if (this.accept('DOTDOT')) {
      end = this.parseExpression();
    } else {
      throw new Unsupported(
        'for-in over a value (only integer ranges are supported)',
        t.line,
        "Use `for i in 0 to n` or `for i in 0..n`."
      );
    }
    var stepExpr = null;
    if (this.at('IDENT') && this.peek().value === 'step') {
      this.next();
      stepExpr = this.parseExpression();
    }
    var body = this.parseBlock();
    return {
      kind: 'For', name: name, start: start, end: end, step: stepExpr,
      body: body, line: t.line
    };
  };

  Parser.prototype.parseMatch = function () {
    var t = this.expect('MATCH');
    var subject = this.parseExpression();
    this.expect('LBRACE');
    var cases = [];
    var fallback = null;
    while (!this.at('RBRACE')) {
      if (this.at('EOF')) throw new FlowError('unterminated match block', t.line);
      if (this.accept('DEFAULT')) {
        this.accept('FAT_ARROW');
        fallback = this.parseBlock();
        this.accept('COMMA');
        continue;
      }
      var patterns = [this.parsePattern()];
      while (this.accept('PIPE')) patterns.push(this.parsePattern());
      var guard = null;
      if (this.accept('IF')) guard = this.parseExpression();
      this.expect('FAT_ARROW', "'=>'");
      var body = this.parseBlock();
      this.accept('COMMA');
      cases.push({ patterns: patterns, guard: guard, body: body });
    }
    this.expect('RBRACE');
    return {
      kind: 'Match', subject: subject, cases: cases, fallback: fallback, line: t.line
    };
  };

  Parser.prototype.parsePattern = function () {
    var t = this.peek();
    if (t.type === 'NUMBER' || t.type === 'STRING' || t.type === 'TRUE' ||
        t.type === 'FALSE' || t.type === 'MINUS') {
      return { kind: 'LiteralPattern', expr: this.parseUnary(), line: t.line };
    }
    if (t.type === 'IDENT') {
      this.next();
      if (this.at('LPAREN')) {
        throw new Unsupported('destructuring match patterns', t.line);
      }
      return { kind: 'BindPattern', name: t.value, line: t.line };
    }
    throw new FlowError("unsupported match pattern '" + t.value + "'", t.line);
  };

  /* ---- expressions ---- */

  Parser.prototype.parseExpression = function () {
    return this.parseLogicalOr();
  };

  function binaryLevel(nextFn, types) {
    return function () {
      var left = nextFn.call(this);
      while (types[this.peek().type]) {
        var op = this.next();
        var right = nextFn.call(this);
        left = {
          kind: 'Binary', op: op.value, left: left, right: right, line: op.line
        };
      }
      return left;
    };
  }

  Parser.prototype.parseUnary = function () {
    var t = this.peek();
    if (t.type === 'MINUS' || t.type === 'NOT' || t.type === 'TILDE' ||
        t.type === 'AMP' || t.type === 'STAR') {
      this.next();
      var operand = this.parseUnary();
      return { kind: 'Unary', op: t.value, operand: operand, line: t.line };
    }
    return this.parsePrimary();
  };

  Parser.prototype.parseCast = function () {
    var expr = this.parseUnary();
    while (this.at('AS')) {
      var t = this.next();
      var type = this.parseType();
      expr = { kind: 'Cast', expr: expr, type: type, line: t.line };
    }
    if (this.at('QUESTION')) {
      throw new Unsupported('the ? error-propagation operator', this.line());
    }
    return expr;
  };

  Parser.prototype.parseFactor = binaryLevel(
    Parser.prototype.parseCast, { STAR: 1, SLASH: 1, PERCENT: 1 });
  Parser.prototype.parseTerm = binaryLevel(
    Parser.prototype.parseFactor, { PLUS: 1, MINUS: 1 });
  Parser.prototype.parseShift = binaryLevel(
    Parser.prototype.parseTerm, { SHL: 1, SHR: 1 });
  Parser.prototype.parseComparison = binaryLevel(
    Parser.prototype.parseShift, { LT: 1, GT: 1, LE: 1, GE: 1 });
  Parser.prototype.parseEquality = binaryLevel(
    Parser.prototype.parseComparison, { EQ: 1, NE: 1 });
  Parser.prototype.parseBitAnd = binaryLevel(
    Parser.prototype.parseEquality, { AMP: 1 });
  Parser.prototype.parseBitXor = binaryLevel(
    Parser.prototype.parseBitAnd, { CARET: 1 });
  Parser.prototype.parseBitOr = binaryLevel(
    Parser.prototype.parseBitXor, { PIPE: 1 });
  Parser.prototype.parseLogicalAnd = binaryLevel(
    Parser.prototype.parseBitOr, { ANDAND: 1 });
  Parser.prototype.parseLogicalOr = binaryLevel(
    Parser.prototype.parseLogicalAnd, { OROR: 1 });

  Parser.prototype.parsePrimary = function () {
    var t = this.peek();
    var expr;
    switch (t.type) {
      case 'NUMBER':
        this.next();
        expr = numberLiteral(t);
        break;
      case 'STRING':
        this.next();
        expr = { kind: 'StringLit', value: unescapeString(t.value, t.line), line: t.line };
        break;
      case 'TRUE':
        this.next();
        expr = { kind: 'BoolLit', value: true, line: t.line };
        break;
      case 'FALSE':
        this.next();
        expr = { kind: 'BoolLit', value: false, line: t.line };
        break;
      case 'NULL':
        this.next();
        expr = { kind: 'NullLit', line: t.line };
        break;
      case 'LPAREN':
        this.next();
        expr = this.parseExpression();
        this.expect('RPAREN', "')'");
        break;
      case 'LBRACKET': {
        this.next();
        var elems = [];
        while (!this.at('RBRACKET')) {
          elems.push(this.parseExpression());
          if (!this.accept('COMMA')) break;
        }
        this.expect('RBRACKET', "']'");
        expr = { kind: 'ArrayLit', elements: elems, line: t.line };
        break;
      }
      case 'PIPE':
        throw new Unsupported('lambda expressions', t.line);
      case 'IDENT': {
        this.next();
        if (this.at('LBRACE') && this.structNames[t.value]) {
          expr = this.parseStructLiteral(t);
        } else if (this.at('DCOLON')) {
          throw new Unsupported('path expressions (A::B)', t.line);
        } else {
          expr = { kind: 'Var', name: t.value, line: t.line };
        }
        break;
      }
      default:
        throw new FlowError("unexpected '" + (t.value || 'end of file') + "' in expression", t.line);
    }
    return this.parsePostfix(expr);
  };

  Parser.prototype.parseStructLiteral = function (nameTok) {
    this.expect('LBRACE');
    var fields = [];
    while (!this.at('RBRACE')) {
      if (this.at('EOF')) throw new FlowError('unterminated struct literal', nameTok.line);
      var fname = this.expect('IDENT', 'field name').value;
      this.expect('COLON', "':' after field name");
      var value = this.parseExpression();
      fields.push({ name: fname, value: value });
      if (!this.accept('COMMA')) break;
    }
    this.expect('RBRACE', "'}'");
    return {
      kind: 'StructLit', name: nameTok.value, fields: fields, line: nameTok.line
    };
  };

  Parser.prototype.parsePostfix = function (expr) {
    for (;;) {
      var t = this.peek();
      if (t.type === 'LPAREN') {
        this.next();
        var args = [];
        while (!this.at('RPAREN')) {
          args.push(this.parseExpression());
          if (!this.accept('COMMA')) break;
        }
        this.expect('RPAREN', "')'");
        if (expr.kind !== 'Var') {
          throw new Unsupported('calling a computed function value', t.line);
        }
        expr = { kind: 'Call', name: expr.name, args: args, line: t.line };
      } else if (t.type === 'LBRACKET') {
        this.next();
        var idx = this.parseExpression();
        this.expect('RBRACKET', "']'");
        expr = { kind: 'Index', base: expr, index: idx, line: t.line };
      } else if (t.type === 'DOT') {
        this.next();
        var f = this.expect('IDENT', 'field name');
        expr = { kind: 'Field', base: expr, field: f.value, line: t.line };
      } else if (t.type === 'PIPELINE') {
        throw new Unsupported('the |> pipeline operator', t.line);
      } else {
        return expr;
      }
    }
  };

  function numberLiteral(t) {
    var text = t.value;
    if (/^0x/i.test(text)) {
      return { kind: 'IntLit', value: BigInt(text), line: t.line };
    }
    if (/[.eE]/.test(text)) {
      return { kind: 'FloatLit', value: parseFloat(text), line: t.line };
    }
    return { kind: 'IntLit', value: BigInt(text), line: t.line };
  }

  function unescapeString(raw, line) {
    var body = raw.slice(1, -1);
    var out = '';
    for (var i = 0; i < body.length; i++) {
      var c = body[i];
      if (c !== '\\') { out += c; continue; }
      i++;
      var e = body[i];
      switch (e) {
        case 'n': out += '\n'; break;
        case 't': out += '\t'; break;
        case 'r': out += '\r'; break;
        case '0': out += '\0'; break;
        case 'a': out += '\x07'; break;
        case 'b': out += '\b'; break;
        case 'f': out += '\f'; break;
        case 'v': out += '\v'; break;
        case '\\': out += '\\'; break;
        case '"': out += '"'; break;
        case "'": out += "'"; break;
        case 'x': {
          var hex = body.substr(i + 1, 2);
          if (!/^[0-9a-fA-F]{1,2}$/.test(hex)) {
            throw new FlowError('bad \\x escape in string literal', line);
          }
          out += String.fromCharCode(parseInt(hex, 16));
          i += hex.length;
          break;
        }
        default:
          throw new FlowError("unknown escape '\\" + e + "' in string literal", line);
      }
    }
    return out;
  }

  function collectStructNames(tokens) {
    var names = Object.create(null);
    for (var i = 0; i + 1 < tokens.length; i++) {
      if (tokens[i].type === 'STRUCT' && tokens[i + 1].type === 'IDENT') {
        names[tokens[i + 1].value] = true;
      }
    }
    return names;
  }

  /* ==================================================================== *
   * C-compatible number formatting
   * ==================================================================== */

  var POW10 = [1n];
  function pow10(k) {
    while (POW10.length <= k) POW10.push(POW10[POW10.length - 1] * 10n);
    return POW10[k];
  }

  var SCRATCH = new DataView(new ArrayBuffer(8));

  /** Exact decomposition: |x| === m * 2^e with m an integer BigInt. */
  function decompose(x) {
    SCRATCH.setFloat64(0, x);
    var hi = SCRATCH.getUint32(0);
    var lo = SCRATCH.getUint32(4);
    var exp = (hi >>> 20) & 0x7ff;
    var m = (BigInt(hi & 0xfffff) << 32n) | BigInt(lo >>> 0);
    var e;
    if (exp === 0) {
      e = -1074;
    } else {
      m |= (1n << 52n);
      e = exp - 1075;
    }
    return { m: m, e: e };
  }

  /** round_half_even(|x| * 10^k) as a BigInt. */
  function exactScaled(x, k) {
    var d = decompose(Math.abs(x));
    var num = d.m;
    var den = 1n;
    if (k >= 0) num *= pow10(k); else den *= pow10(-k);
    if (d.e >= 0) num <<= BigInt(d.e); else den <<= BigInt(-d.e);
    var q = num / den;
    var r = num % den;
    var twice = r * 2n;
    if (twice > den || (twice === den && (q & 1n) === 1n)) q += 1n;
    return q;
  }

  function fixedDigits(x, prec) {
    var n = exactScaled(x, prec).toString();
    if (prec === 0) return n;
    while (n.length <= prec) n = '0' + n;
    return n.slice(0, n.length - prec) + '.' + n.slice(n.length - prec);
  }

  function sciDigits(x, prec) {
    var ax = Math.abs(x);
    if (ax === 0) {
      var z = '0';
      if (prec > 0) z += '.' + new Array(prec + 1).join('0');
      return { mant: z, exp: 0 };
    }
    var e10 = Math.floor(Math.log10(ax));
    for (var tries = 0; tries < 6; tries++) {
      var n = exactScaled(ax, prec - e10);
      if (n < pow10(prec)) { e10--; continue; }
      if (n >= pow10(prec + 1)) { e10++; continue; }
      var s = n.toString();
      var mant = prec > 0 ? s[0] + '.' + s.slice(1) : s;
      return { mant: mant, exp: e10 };
    }
    return { mant: ax.toExponential(prec).split('e')[0], exp: Math.floor(Math.log10(ax)) };
  }

  function expSuffix(exp, upper) {
    var sign = exp < 0 ? '-' : '+';
    var a = Math.abs(exp).toString();
    if (a.length < 2) a = '0' + a;
    return (upper ? 'E' : 'e') + sign + a;
  }

  function formatFloat(x, conv, prec) {
    var upper = conv === conv.toUpperCase() && /[FEG]/.test(conv);
    var lc = conv.toLowerCase();
    if (!isFinite(x)) {
      var word = isNaN(x) ? 'nan' : 'inf';
      if (upper) word = word.toUpperCase();
      return { sign: (!isNaN(x) && x < 0) ? '-' : '', body: word, special: true };
    }
    var neg = x < 0 || (x === 0 && 1 / x < 0);
    var sign = neg ? '-' : '';
    var body;
    if (lc === 'f') {
      body = fixedDigits(x, prec === null ? 6 : prec);
    } else if (lc === 'e') {
      var p = prec === null ? 6 : prec;
      var s = sciDigits(x, p);
      body = s.mant + expSuffix(s.exp, upper);
    } else {
      var P = prec === null ? 6 : (prec === 0 ? 1 : prec);
      var probe = sciDigits(x, P - 1);
      var X = x === 0 ? 0 : probe.exp;
      if (X >= -4 && X < P) {
        body = fixedDigits(x, P - 1 - X);
        if (body.indexOf('.') >= 0) {
          body = body.replace(/0+$/, '').replace(/\.$/, '');
        }
      } else {
        var mant = probe.mant;
        if (mant.indexOf('.') >= 0) {
          mant = mant.replace(/0+$/, '').replace(/\.$/, '');
        }
        body = mant + expSuffix(probe.exp, upper);
      }
    }
    return { sign: sign, body: body, special: false };
  }

  /* ==================================================================== *
   * printf
   * ==================================================================== */

  var SPEC_RE = /^%([-+ #0']*)(\*|\d+)?(?:\.(\*|\d*))?(hh|h|ll|l|z|j|t|L|q)?([diouxXeEfFgGaAcspn%])/;

  function padTo(text, width, leftAlign, padChar) {
    if (!width || text.length >= width) return text;
    var pad = new Array(width - text.length + 1).join(padChar || ' ');
    return leftAlign ? text + pad : pad + text;
  }

  function Printf(interp) {
    this.interp = interp;
  }

  Printf.prototype.format = function (fmt, args, line) {
    var out = '';
    var ai = 0;
    var self = this;
    function nextArg(what) {
      if (ai >= args.length) {
        throw new FlowError(
          'printf format needs more arguments than were supplied (%' + what + ')', line);
      }
      return args[ai++];
    }
    for (var i = 0; i < fmt.length; i++) {
      if (fmt[i] !== '%') { out += fmt[i]; continue; }
      var m = SPEC_RE.exec(fmt.slice(i));
      if (!m) {
        throw new FlowError("unrecognised printf conversion at '" + fmt.slice(i, i + 4) + "'", line);
      }
      i += m[0].length - 1;
      var flags = m[1] || '';
      var conv = m[5];
      if (conv === '%') { out += '%'; continue; }
      if (conv === 'n') {
        throw new Unsupported('the printf %n conversion', line);
      }
      var leftAlign = flags.indexOf('-') >= 0;
      var plus = flags.indexOf('+') >= 0;
      var space = flags.indexOf(' ') >= 0;
      var zero = flags.indexOf('0') >= 0;
      var alt = flags.indexOf('#') >= 0;
      var width = null;
      if (m[2] === '*') width = Number(asInteger(nextArg('*'), line));
      else if (m[2] !== undefined) width = parseInt(m[2], 10);
      if (width !== null && width < 0) { leftAlign = true; width = -width; }
      var prec = null;
      if (m[3] === '*') prec = Number(asInteger(nextArg('*'), line));
      else if (m[3] !== undefined) prec = m[3] === '' ? 0 : parseInt(m[3], 10);
      var len = m[4] || '';
      var piece;

      if (conv === 'd' || conv === 'i' || conv === 'u' || conv === 'o' ||
          conv === 'x' || conv === 'X') {
        var v = asInteger(nextArg(conv), line);
        var bits = (len === 'll' || len === 'l' || len === 'z' || len === 'j' || len === 't') ? 64 : 32;
        if (len === 'hh') bits = 8; else if (len === 'h') bits = 16;
        var signed = (conv === 'd' || conv === 'i');
        v = signed ? BigInt.asIntN(bits, v) : BigInt.asUintN(bits, v);
        var negative = v < 0n;
        var digits;
        if (conv === 'o') digits = (negative ? -v : v).toString(8);
        else if (conv === 'x') digits = (negative ? -v : v).toString(16);
        else if (conv === 'X') digits = (negative ? -v : v).toString(16).toUpperCase();
        else digits = (negative ? -v : v).toString(10);
        if (prec !== null) {
          while (digits.length < prec) digits = '0' + digits;
          if (prec === 0 && v === 0n) digits = '';
        }
        var prefix = negative ? '-' : (signed ? (plus ? '+' : (space ? ' ' : '')) : '');
        if (alt && conv === 'o' && digits[0] !== '0') digits = '0' + digits;
        if (alt && (conv === 'x' || conv === 'X') && v !== 0n) {
          prefix += (conv === 'x' ? '0x' : '0X');
        }
        piece = prefix + digits;
        if (zero && !leftAlign && prec === null && width !== null && piece.length < width) {
          piece = prefix + padTo(digits, width - prefix.length, false, '0');
        }
        piece = padTo(piece, width, leftAlign, ' ');
      } else if (conv === 'f' || conv === 'F' || conv === 'e' || conv === 'E' ||
                 conv === 'g' || conv === 'G' || conv === 'a' || conv === 'A') {
        if (conv === 'a' || conv === 'A') {
          throw new Unsupported('the printf %a conversion', line);
        }
        var fv = asDouble(nextArg(conv), line);
        var f = formatFloat(fv, conv, prec);
        var fsign = f.sign || (plus ? '+' : (space ? ' ' : ''));
        piece = fsign + f.body;
        if (zero && !leftAlign && !f.special && width !== null && piece.length < width) {
          piece = fsign + padTo(f.body, width - fsign.length, false, '0');
        }
        piece = padTo(piece, width, leftAlign, ' ');
      } else if (conv === 'c') {
        var cv = nextArg('c');
        var ch;
        if (cv.t.k === 'string') ch = cv.v.charAt(0);
        else ch = String.fromCharCode(Number(BigInt.asUintN(8, asInteger(cv, line))));
        piece = padTo(ch, width, leftAlign, ' ');
      } else if (conv === 's') {
        var sv = nextArg('s');
        if (sv.t.k !== 'string') {
          if (sv.t.k === 'ptr' && sv.v === null) piece = '(null)';
          else {
            throw new FlowError(
              'printf %s expects a string but got ' + sv.t.name, line);
          }
        } else {
          piece = sv.v;
        }
        if (prec !== null) piece = piece.slice(0, prec);
        piece = padTo(piece, width, leftAlign, ' ');
      } else if (conv === 'p') {
        var pv = nextArg('p');
        piece = self.interp.pointerText(pv, line);
        piece = padTo(piece, width, leftAlign, ' ');
      } else {
        throw new FlowError('unsupported printf conversion %' + conv, line);
      }
      out += piece;
    }
    return out;
  };

  function asInteger(val, line) {
    switch (val.t.k) {
      case 'int': return val.v;
      case 'bool': return val.v ? 1n : 0n;
      case 'float':
        throw new FlowError(
          'printf integer conversion given a ' + val.t.name +
          ' value (use %f, or cast the argument)', line);
      default:
        throw new FlowError(
          'printf integer conversion given a ' + val.t.name + ' value', line);
    }
  }

  function asDouble(val, line) {
    if (val.t.k === 'float') return val.v;
    if (val.t.k === 'int') {
      throw new FlowError(
        'printf float conversion given an ' + val.t.name +
        ' value (use %d, or cast the argument)', line);
    }
    throw new FlowError(
      'printf float conversion given a ' + val.t.name + ' value', line);
  }

  /* ==================================================================== *
   * Values and memory
   * ==================================================================== */

  function wrapInt(v, t) {
    return t.signed ? BigInt.asIntN(t.bits, v) : BigInt.asUintN(t.bits, v);
  }
  function mkInt(v, t) {
    return { t: t, v: wrapInt(v, t) };
  }
  function mkFloat(v, t, cd) {
    return { t: t, v: t.bits === 32 && !cd ? Math.fround(v) : v, cd: !!cd };
  }
  function mkBool(v) { return { t: TY.bool, v: !!v }; }
  function mkString(v) { return { t: TY.string, v: v }; }
  var VOID_VALUE = { t: TY['void'], v: null };

  function isNumeric(val) {
    return val.t.k === 'int' || val.t.k === 'float' || val.t.k === 'bool';
  }
  function numOf(val) {
    if (val.t.k === 'int') return Number(val.v);
    if (val.t.k === 'bool') return val.v ? 1 : 0;
    return val.v;
  }
  function bigOf(val, line) {
    if (val.t.k === 'int') return val.v;
    if (val.t.k === 'bool') return val.v ? 1n : 0n;
    if (val.t.k === 'float') return BigInt(Math.trunc(val.v));
    throw new FlowError('expected an integer but got ' + val.t.name, line);
  }

  function Block(size, tag) {
    this.size = size;
    this.cells = new Map();
    this.freed = false;
    this.tag = tag || 'memory';
    this.id = ++Block.counter;
  }
  Block.counter = 0;

  /* ==================================================================== *
   * Interpreter
   * ==================================================================== */

  function Scope(parent) {
    this.vars = Object.create(null);
    this.parent = parent || null;
  }
  Scope.prototype.lookup = function (name) {
    var s = this;
    while (s) {
      var r = s.vars[name];
      if (r !== undefined) return r;
      s = s.parent;
    }
    return null;
  };

  function Interp(prog) {
    this.prog = prog;
    this.out = [];
    this.outLen = 0;
    this.steps = 0;
    this.depth = 0;
    this.globals = new Scope(null);
    this.printf = new Printf(this);
    this.structSizes = Object.create(null);
    this.truncated = false;
  }

  Interp.prototype.tick = function (line) {
    if (++this.steps > STEP_LIMIT) {
      throw new FlowError(
        'step budget exceeded (' + STEP_LIMIT +
        ' operations) — the program looks like it does not terminate', line);
    }
  };

  Interp.prototype.write = function (text) {
    if (this.outLen >= OUTPUT_LIMIT) {
      if (!this.truncated) {
        this.truncated = true;
        this.out.push('\n[output truncated by the browser interpreter]\n');
      }
      return;
    }
    this.out.push(text);
    this.outLen += text.length;
  };

  Interp.prototype.stdout = function () {
    return this.out.join('');
  };

  /* ---- type helpers ---- */

  Interp.prototype.structDecl = function (name, line) {
    var s = this.prog.structs[name];
    if (!s) throw new FlowError("unknown struct '" + name + "'", line);
    return s;
  };

  Interp.prototype.sizeOf = function (t, line) {
    switch (t.k) {
      case 'int': return t.bits / 8;
      case 'float': return t.bits / 8;
      case 'bool': return 1;
      case 'string': return 8;
      case 'ptr': return 8;
      case 'void': return 1;
      case 'array': return t.len * this.sizeOf(t.elem, line);
      case 'struct': return this.structSize(t.name, line);
      default: return 8;
    }
  };

  Interp.prototype.structSize = function (name, line) {
    if (this.structSizes[name] !== undefined) return this.structSizes[name];
    var decl = this.structDecl(name, line);
    this.structSizes[name] = 8; // guard against recursion
    var offset = 0;
    var maxAlign = 1;
    for (var i = 0; i < decl.fields.length; i++) {
      var ft = decl.fields[i].type;
      var fs = this.sizeOf(ft, line);
      var align = Math.min(fs, 8) || 1;
      if (ft.k === 'array') align = Math.min(this.sizeOf(ft.elem, line), 8) || 1;
      if (ft.k === 'struct') align = 8;
      maxAlign = Math.max(maxAlign, align);
      offset = Math.ceil(offset / align) * align;
      offset += fs;
    }
    offset = Math.ceil(offset / maxAlign) * maxAlign;
    this.structSizes[name] = offset || 1;
    return this.structSizes[name];
  };

  Interp.prototype.zeroValue = function (t, line) {
    switch (t.k) {
      case 'int': return mkInt(0n, t);
      case 'float': return mkFloat(0, t, t.bits === 64);
      case 'bool': return mkBool(false);
      case 'string': return mkString('');
      case 'ptr': return { t: t, v: null };
      case 'struct': {
        var decl = this.structDecl(t.name, line);
        var fields = Object.create(null);
        for (var i = 0; i < decl.fields.length; i++) {
          fields[decl.fields[i].name] = this.zeroValue(decl.fields[i].type, line);
        }
        return { t: t, v: fields };
      }
      case 'array': {
        var blk = new Block(this.sizeOf(t, line), 'array');
        return { t: t, v: { blk: blk, off: 0 } };
      }
      default: return VOID_VALUE;
    }
  };

  Interp.prototype.cloneValue = function (val) {
    if (val.t.k !== 'struct') return val;
    var fields = Object.create(null);
    for (var k in val.v) fields[k] = this.cloneValue(val.v[k]);
    return { t: val.t, v: fields };
  };

  /** Convert a value to the given declared type, applying C conversions. */
  Interp.prototype.coerce = function (val, t, line, what) {
    switch (t.k) {
      case 'int':
        if (val.t.k === 'int') return mkInt(val.v, t);
        if (val.t.k === 'bool') return mkInt(val.v ? 1n : 0n, t);
        if (val.t.k === 'float') return mkInt(BigInt(Math.trunc(val.v)), t);
        break;
      case 'float':
        if (val.t.k === 'float') return mkFloat(val.v, t, t.bits === 64);
        if (val.t.k === 'int') return mkFloat(Number(val.v), t, t.bits === 64);
        if (val.t.k === 'bool') return mkFloat(val.v ? 1 : 0, t, t.bits === 64);
        break;
      case 'bool':
        if (val.t.k === 'bool') return val;
        if (val.t.k === 'int') return mkBool(val.v !== 0n);
        break;
      case 'string':
        if (val.t.k === 'string') return val;
        break;
      case 'ptr':
        if (val.t.k === 'ptr') return { t: t, v: val.v };
        if (val.t.k === 'array') return { t: t, v: val.v };
        break;
      case 'array':
        if (val.t.k === 'array') return { t: t, v: val.v };
        break;
      case 'struct':
        if (val.t.k === 'struct' && val.t.name === t.name) return this.cloneValue(val);
        break;
      case 'void':
        return VOID_VALUE;
      default:
        break;
    }
    throw new FlowError(
      'cannot use a ' + val.t.name + ' value where ' + t.name + ' is expected' +
      (what ? ' (' + what + ')' : ''), line);
  };

  /* ---- memory access ---- */

  Interp.prototype.checkBlock = function (blk, line) {
    if (blk.freed) {
      throw new FlowError('use after free: this memory was already released', line);
    }
  };

  Interp.prototype.readCell = function (blk, off, t, line) {
    this.checkBlock(blk, line);
    var size = this.sizeOf(t, line);
    if (off < 0 || off + size > blk.size) {
      throw new FlowError(
        'out-of-bounds read at byte ' + off + ' of a ' + blk.size + '-byte ' + blk.tag, line);
    }
    var cur = blk.cells.get(off);
    if (cur === undefined) {
      cur = this.zeroValue(t, line);
      blk.cells.set(off, cur);
    }
    return cur;
  };

  Interp.prototype.writeCell = function (blk, off, t, val, line) {
    this.checkBlock(blk, line);
    var size = this.sizeOf(t, line);
    if (off < 0 || off + size > blk.size) {
      throw new FlowError(
        'out-of-bounds write at byte ' + off + ' of a ' + blk.size + '-byte ' + blk.tag, line);
    }
    blk.cells.set(off, this.coerce(val, t, line));
  };

  Interp.prototype.pointerText = function (val, line) {
    if (val.t.k !== 'ptr' && val.t.k !== 'array') {
      throw new FlowError('%p expects a pointer but got ' + val.t.name, line);
    }
    if (!val.v) return '0x0';
    return '0x' + (0x100000000 + val.v.blk.id * 0x1000 + val.v.off).toString(16);
  };

  /* ---- variables ---- */

  Interp.prototype.declare = function (scope, name, type, mut, value, line) {
    scope.vars[name] = {
      name: name, type: type, mut: mut, value: value,
      boxed: false, blk: null, off: 0
    };
  };

  Interp.prototype.readVarRec = function (rec, line) {
    if (rec.boxed) return this.readCell(rec.blk, rec.off, rec.type, line);
    return rec.value;
  };

  Interp.prototype.writeVarRec = function (rec, val, line) {
    var coerced = this.coerce(val, rec.type, line, "assigning to '" + rec.name + "'");
    if (rec.boxed) this.writeCell(rec.blk, rec.off, rec.type, coerced, line);
    else rec.value = coerced;
  };

  Interp.prototype.addressOfVar = function (rec, line) {
    if (!rec.boxed) {
      if (rec.type.k === 'array') {
        return { t: ptrType(rec.type.elem), v: rec.value.v };
      }
      var blk = new Block(this.sizeOf(rec.type, line), 'variable');
      blk.cells.set(0, rec.value);
      rec.boxed = true;
      rec.blk = blk;
      rec.off = 0;
    }
    return { t: ptrType(rec.type), v: { blk: rec.blk, off: rec.off } };
  };

  /* ==================================================================== *
   * Builtins
   * ==================================================================== */

  var MATH1 = {
    sqrt: Math.sqrt, cbrt: Math.cbrt, sin: Math.sin, cos: Math.cos,
    tan: Math.tan, asin: Math.asin, acos: Math.acos, atan: Math.atan,
    sinh: Math.sinh, cosh: Math.cosh, tanh: Math.tanh, asinh: Math.asinh,
    acosh: Math.acosh, atanh: Math.atanh, exp: Math.exp, exp2: function (x) {
      return Math.pow(2, x);
    },
    expm1: Math.expm1, log: Math.log, log2: Math.log2, log10: Math.log10,
    log1p: Math.log1p, floor: Math.floor, ceil: Math.ceil,
    round: function (x) { return Math.sign(x) * Math.round(Math.abs(x)); },
    trunc: Math.trunc, fabs: Math.abs,
    sigmoid: function (x) { return 1 / (1 + Math.exp(-x)); }
  };

  var MATH2 = {
    pow: Math.pow, atan2: Math.atan2, hypot: Math.hypot,
    fmod: function (a, b) { return a % b; },
    fmin: Math.min, fmax: Math.max,
    fdim: function (a, b) { return a > b ? a - b : 0; }
  };

  var BUILTIN_NAMES = {
    printf: 1, print: 1, println: 1, puts: 1, putchar: 1,
    malloc: 1, calloc: 1, realloc: 1, free: 1,
    memcpy: 1, memmove: 1, memset: 1,
    strlen: 1, abs: 1, len: 1, array_length: 1, length: 1
  };
  for (var mk1 in MATH1) BUILTIN_NAMES[mk1] = 1;
  for (var mk2 in MATH2) BUILTIN_NAMES[mk2] = 1;

  Interp.prototype.callBuiltin = function (name, args, node) {
    var line = node.line;
    var i;
    switch (name) {
      case 'printf': {
        if (!args.length || args[0].t.k !== 'string') {
          throw new FlowError('printf needs a string format as its first argument', line);
        }
        var text = this.printf.format(args[0].v, args.slice(1), line);
        this.write(text);
        return mkInt(BigInt(text.length), TY.i32);
      }
      case 'puts': {
        if (!args.length || args[0].t.k !== 'string') {
          throw new FlowError('puts needs a string argument', line);
        }
        this.write(args[0].v + '\n');
        return mkInt(0n, TY.i32);
      }
      case 'putchar': {
        this.write(String.fromCharCode(Number(BigInt.asUintN(8, bigOf(args[0], line)))));
        return mkInt(0n, TY.i32);
      }
      case 'print':
      case 'println': {
        var parts = [];
        for (i = 0; i < args.length; i++) parts.push(this.defaultRender(args[i], line));
        this.write(parts.join(' ') + (name === 'println' ? '\n' : ''));
        return VOID_VALUE;
      }
      case 'malloc': {
        var msize = Number(bigOf(args[0], line));
        if (msize < 0) throw new FlowError('malloc called with a negative size', line);
        return { t: PTR_VOID, v: { blk: new Block(Math.max(msize, 1), 'heap block'), off: 0 } };
      }
      case 'calloc': {
        var cn = Number(bigOf(args[0], line));
        var cs = Number(bigOf(args[1], line));
        return {
          t: PTR_VOID,
          v: { blk: new Block(Math.max(cn * cs, 1), 'heap block'), off: 0 }
        };
      }
      case 'realloc': {
        var oldp = args[0];
        var newSize = Number(bigOf(args[1], line));
        var nb = new Block(Math.max(newSize, 1), 'heap block');
        if (oldp.v) {
          this.checkBlock(oldp.v.blk, line);
          oldp.v.blk.cells.forEach(function (v, off) {
            if (off < newSize) nb.cells.set(off, v);
          });
          oldp.v.blk.freed = true;
        }
        return { t: PTR_VOID, v: { blk: nb, off: 0 } };
      }
      case 'free': {
        var fp = args[0];
        if (!fp || fp.v === null) return VOID_VALUE;
        if (fp.t.k !== 'ptr' && fp.t.k !== 'array') {
          throw new FlowError('free expects a pointer', line);
        }
        if (fp.v.blk.freed) throw new FlowError('double free', line);
        if (fp.v.off !== 0) {
          throw new FlowError('free called on a pointer into the middle of a block', line);
        }
        fp.v.blk.freed = true;
        return VOID_VALUE;
      }
      case 'memset': {
        var sp = args[0];
        var fill = Number(bigOf(args[1], line));
        var count = Number(bigOf(args[2], line));
        if (fill !== 0) {
          throw new Unsupported('memset with a non-zero fill byte', line);
        }
        if (sp.v) {
          this.checkBlock(sp.v.blk, line);
          var base = sp.v.off;
          var keys = [];
          sp.v.blk.cells.forEach(function (v, off) {
            if (off >= base && off < base + count) keys.push(off);
          });
          for (i = 0; i < keys.length; i++) sp.v.blk.cells['delete'](keys[i]);
        }
        return sp;
      }
      case 'memcpy':
      case 'memmove': {
        var dst = args[0];
        var src = args[1];
        var nbytes = Number(bigOf(args[2], line));
        if (!dst.v || !src.v) throw new FlowError(name + ' called with a null pointer', line);
        this.checkBlock(dst.v.blk, line);
        this.checkBlock(src.v.blk, line);
        var sbase = src.v.off;
        var dbase = dst.v.off;
        var copy = [];
        src.v.blk.cells.forEach(function (v, off) {
          if (off >= sbase && off < sbase + nbytes) copy.push([off, v]);
        });
        for (i = 0; i < copy.length; i++) {
          dst.v.blk.cells.set(dbase + (copy[i][0] - sbase), copy[i][1]);
        }
        return dst;
      }
      case 'strlen': {
        if (args[0].t.k !== 'string') {
          throw new Unsupported('strlen on a raw character buffer', line);
        }
        return mkInt(BigInt(args[0].v.length), TY.u64);
      }
      case 'abs': {
        if (args[0].t.k === 'float') {
          return mkFloat(Math.abs(args[0].v), TY.f32, true);
        }
        var av = bigOf(args[0], line);
        return mkInt(av < 0n ? -av : av, TY.i32);
      }
      case 'len':
      case 'length':
      case 'array_length': {
        if (args[0].t.k === 'array') return mkInt(BigInt(args[0].t.len), TY.i64);
        if (args[0].t.k === 'string') return mkInt(BigInt(args[0].v.length), TY.i64);
        throw new FlowError(name + ' expects an array or string', line);
      }
      default: break;
    }
    if (MATH1[name]) {
      if (args.length !== 1) {
        throw new FlowError(name + ' takes exactly one argument', line);
      }
      return mkFloat(MATH1[name](this.toDouble(args[0], line)), TY.f32, true);
    }
    if (MATH2[name]) {
      if (args.length !== 2) {
        throw new FlowError(name + ' takes exactly two arguments', line);
      }
      return mkFloat(
        MATH2[name](this.toDouble(args[0], line), this.toDouble(args[1], line)),
        TY.f32, true);
    }
    throw new Unsupported("the builtin '" + name + "'", line);
  };

  Interp.prototype.toDouble = function (val, line) {
    if (val.t.k === 'float') return val.v;
    if (val.t.k === 'int') return Number(val.v);
    if (val.t.k === 'bool') return val.v ? 1 : 0;
    throw new FlowError('expected a number but got ' + val.t.name, line);
  };

  Interp.prototype.defaultRender = function (val, line) {
    switch (val.t.k) {
      case 'string': return val.v;
      case 'bool': return val.v ? '1' : '0';
      case 'int': return val.v.toString();
      case 'float': return fixedDigits(val.v, 6) === undefined
        ? String(val.v) : (val.v < 0 ? '-' : '') + fixedDigits(val.v, 6);
      case 'ptr': return this.pointerText(val, line);
      default: return '(' + val.t.name + ')';
    }
  };

  /* ==================================================================== *
   * Evaluation
   * ==================================================================== */

  var SIG_RETURN = 'return';
  var SIG_BREAK = 'break';
  var SIG_CONTINUE = 'continue';

  Interp.prototype.execBlock = function (block, scope) {
    var inner = new Scope(scope);
    var body = block.body;
    for (var i = 0; i < body.length; i++) {
      var sig = this.execStatement(body[i], inner);
      if (sig) return sig;
    }
    return null;
  };

  Interp.prototype.execStatement = function (stmt, scope) {
    this.tick(stmt.line);
    switch (stmt.kind) {
      case 'Empty':
        return null;
      case 'Let': {
        var value = this.evaluate(stmt.value, scope);
        var type = stmt.type;
        if (!type) type = this.inferDeclaredType(value, stmt.line);
        if (type.k === 'array' && stmt.value.kind === 'ArrayLit' &&
            type.len !== stmt.value.elements.length) {
          throw new FlowError(
            'array literal has ' + stmt.value.elements.length + ' elements but ' +
            type.name + ' needs ' + type.len, stmt.line);
        }
        if (type.k === 'array') {
          value = this.buildArray(stmt.value, type, scope, stmt.line, value);
        } else {
          value = this.coerce(value, type, stmt.line, "initialising '" + stmt.name + "'");
        }
        if (scope.vars[stmt.name] !== undefined) {
          throw new FlowError("variable '" + stmt.name + "' is already declared in this scope", stmt.line);
        }
        this.declare(scope, stmt.name, type, stmt.mut, value, stmt.line);
        return null;
      }
      case 'Assign': {
        var ref = this.lvalue(stmt.target, scope);
        var rhs = this.evaluate(stmt.value, scope);
        if (stmt.op !== '=') {
          rhs = this.binary(stmt.op, ref.get(), rhs, stmt.line);
        }
        ref.set(rhs);
        return null;
      }
      case 'Return': {
        var rv = stmt.value ? this.evaluate(stmt.value, scope) : VOID_VALUE;
        return { sig: SIG_RETURN, value: rv, line: stmt.line };
      }
      case 'ExprStmt':
        this.evaluate(stmt.expr, scope);
        return null;
      case 'If': {
        if (this.truthy(this.evaluate(stmt.cond, scope), stmt.line)) {
          return this.execBlock(stmt.then, scope);
        }
        if (stmt.otherwise) return this.execBlock(stmt.otherwise, scope);
        return null;
      }
      case 'While': {
        for (;;) {
          this.tick(stmt.line);
          if (!this.truthy(this.evaluate(stmt.cond, scope), stmt.line)) break;
          var s = this.execBlock(stmt.body, scope);
          if (s) {
            if (s.sig === SIG_BREAK) break;
            if (s.sig === SIG_CONTINUE) continue;
            return s;
          }
        }
        return null;
      }
      case 'For':
        return this.execFor(stmt, scope);
      case 'Block':
        return this.execBlock(stmt, scope);
      case 'Break':
        return { sig: SIG_BREAK, line: stmt.line };
      case 'Continue':
        return { sig: SIG_CONTINUE, line: stmt.line };
      case 'Match':
        return this.execMatch(stmt, scope);
      default:
        throw new FlowError('cannot execute ' + stmt.kind, stmt.line);
    }
  };

  Interp.prototype.execFor = function (stmt, scope) {
    var startV = this.evaluate(stmt.start, scope);
    var endV = this.evaluate(stmt.end, scope);
    if (startV.t.k !== 'int' || endV.t.k !== 'int') {
      throw new FlowError('for-in ranges need integer bounds', stmt.line);
    }
    var stepV = 1n;
    if (stmt.step) {
      var sv = this.evaluate(stmt.step, scope);
      stepV = bigOf(sv, stmt.line);
      if (stepV === 0n) throw new FlowError('for-in step cannot be zero', stmt.line);
    }
    var loopType = startV.t.bits >= endV.t.bits ? startV.t : endV.t;
    var i = startV.v;
    var end = endV.v;
    for (;;) {
      this.tick(stmt.line);
      if (stepV > 0n ? !(i < end) : !(i > end)) break;
      var iterScope = new Scope(scope);
      this.declare(iterScope, stmt.name, loopType, false, mkInt(i, loopType), stmt.line);
      var s = this.execBlock(stmt.body, iterScope);
      if (s) {
        if (s.sig === SIG_BREAK) break;
        if (s.sig !== SIG_CONTINUE) return s;
      }
      i += stepV;
    }
    return null;
  };

  Interp.prototype.execMatch = function (stmt, scope) {
    var subject = this.evaluate(stmt.subject, scope);
    for (var i = 0; i < stmt.cases.length; i++) {
      var c = stmt.cases[i];
      for (var p = 0; p < c.patterns.length; p++) {
        var pat = c.patterns[p];
        var caseScope = new Scope(scope);
        var matched = false;
        if (pat.kind === 'LiteralPattern') {
          var pv = this.evaluate(pat.expr, scope);
          matched = this.valuesEqual(subject, pv, stmt.line);
        } else {
          this.declare(caseScope, pat.name, subject.t, false, subject, pat.line);
          matched = true;
        }
        if (!matched) continue;
        if (c.guard && !this.truthy(this.evaluate(c.guard, caseScope), stmt.line)) continue;
        return this.execBlock(c.body, caseScope);
      }
    }
    if (stmt.fallback) return this.execBlock(stmt.fallback, scope);
    return null;
  };

  Interp.prototype.valuesEqual = function (a, b, line) {
    if (a.t.k === 'string' || b.t.k === 'string') {
      if (a.t.k !== b.t.k) return false;
      return a.v === b.v;
    }
    if (a.t.k === 'ptr' || b.t.k === 'ptr' || a.t.k === 'array' || b.t.k === 'array') {
      var pa = a.v, pb = b.v;
      if (pa === null || pb === null) return pa === pb;
      return pa.blk === pb.blk && pa.off === pb.off;
    }
    if (a.t.k === 'bool' && b.t.k === 'bool') return a.v === b.v;
    if (a.t.k === 'float' || b.t.k === 'float') return numOf(a) === numOf(b);
    return bigOf(a, line) === bigOf(b, line);
  };

  Interp.prototype.truthy = function (val, line) {
    if (val.t.k === 'bool') return val.v;
    if (val.t.k === 'int') return val.v !== 0n;
    if (val.t.k === 'ptr') return val.v !== null;
    if (val.t.k === 'float') return val.v !== 0;
    throw new FlowError('condition must be a bool, got ' + val.t.name, line);
  };

  Interp.prototype.inferDeclaredType = function (value, line) {
    // Mirrors the native checker: integer literals are i32, float literals f32.
    if (value.t.k === 'array') return value.t;
    return value.t;
  };

  Interp.prototype.buildArray = function (node, type, scope, line, prebuilt) {
    if (node.kind === 'ArrayLit') {
      var blk = new Block(this.sizeOf(type, line), 'array');
      var esize = this.sizeOf(type.elem, line);
      for (var i = 0; i < node.elements.length; i++) {
        var ev = this.evaluate(node.elements[i], scope);
        this.writeCell(blk, i * esize, type.elem, ev, line);
      }
      return { t: type, v: { blk: blk, off: 0 } };
    }
    return this.coerce(prebuilt, type, line);
  };

  /* ---- lvalues ---- */

  Interp.prototype.lvalue = function (node, scope) {
    var self = this;
    var line = node.line;
    if (node.kind === 'Var') {
      var rec = scope.lookup(node.name);
      if (!rec) throw new FlowError("undefined variable '" + node.name + "'", line);
      if (!rec.mut) {
        throw new FlowError(
          "cannot assign to immutable variable '" + node.name + "' (use 'let mut')", line);
      }
      return {
        get: function () { return self.readVarRec(rec, line); },
        set: function (v) { self.writeVarRec(rec, v, line); },
        type: rec.type
      };
    }
    if (node.kind === 'Index') {
      var target = this.indexTarget(node, scope);
      return {
        get: function () {
          return self.readCell(target.blk, target.off, target.elem, line);
        },
        set: function (v) {
          self.writeCell(target.blk, target.off, target.elem, v, line);
        },
        type: target.elem
      };
    }
    if (node.kind === 'Field') {
      var base = this.evaluate(node.base, scope);
      if (base.t.k !== 'struct') {
        if (base.t.k === 'ptr') {
          throw new FlowError(
            "cannot use '.' on a pointer; index it first (p[0]." + node.field + ')', line);
        }
        throw new FlowError('field access on a ' + base.t.name + ' value', line);
      }
      var decl = this.structDecl(base.t.name, line);
      var ftype = null;
      for (var i = 0; i < decl.fields.length; i++) {
        if (decl.fields[i].name === node.field) ftype = decl.fields[i].type;
      }
      if (!ftype) {
        throw new FlowError(
          "struct " + base.t.name + " has no field '" + node.field + "'", line);
      }
      // Mutability of the containing variable is checked when it is a plain
      // variable; through pointers C allows writes, and so do we.
      if (node.base.kind === 'Var') {
        var brec = scope.lookup(node.base.name);
        if (brec && !brec.mut) {
          throw new FlowError(
            "cannot assign to a field of immutable variable '" + node.base.name +
            "' (use 'let mut')", line);
        }
      }
      return {
        get: function () { return base.v[node.field]; },
        set: function (v) {
          base.v[node.field] = self.coerce(v, ftype, line, 'field ' + node.field);
        },
        type: ftype
      };
    }
    if (node.kind === 'Unary' && node.op === '*') {
      var p = this.evaluate(node.operand, scope);
      if (p.t.k !== 'ptr') throw new FlowError('cannot dereference a ' + p.t.name, line);
      if (!p.v) throw new FlowError('null pointer dereference', line);
      var et = p.t.elem;
      return {
        get: function () { return self.readCell(p.v.blk, p.v.off, et, line); },
        set: function (v) { self.writeCell(p.v.blk, p.v.off, et, v, line); },
        type: et
      };
    }
    throw new FlowError('this expression cannot be assigned to', line);
  };

  Interp.prototype.indexTarget = function (node, scope) {
    var line = node.line;
    var base;
    if (node.base.kind === 'Var') {
      var rec = scope.lookup(node.base.name);
      if (!rec) throw new FlowError("undefined variable '" + node.base.name + "'", line);
      base = this.readVarRec(rec, line);
      if (base.t.k === 'array' && !rec.mut) {
        // reads are fine; writes to immutable arrays are rejected below
        base = { t: base.t, v: base.v, immutable: true, owner: rec.name };
      }
    } else {
      base = this.evaluate(node.base, scope);
    }
    var idxVal = this.evaluate(node.index, scope);
    var idx = Number(bigOf(idxVal, line));
    var elem;
    if (base.t.k === 'array') {
      elem = base.t.elem;
      if (idx < 0 || idx >= base.t.len) {
        throw new FlowError(
          'array index ' + idx + ' is out of bounds for ' + base.t.name, line);
      }
    } else if (base.t.k === 'ptr') {
      elem = base.t.elem;
      if (elem.k === 'void') {
        throw new FlowError('cannot index a ptr<void>; assign it to a typed pointer first', line);
      }
    } else if (base.t.k === 'string') {
      throw new Unsupported('indexing into a string', line);
    } else {
      throw new FlowError('cannot index a ' + base.t.name + ' value', line);
    }
    if (!base.v) throw new FlowError('null pointer dereference', line);
    var esize = this.sizeOf(elem, line);
    return { blk: base.v.blk, off: base.v.off + idx * esize, elem: elem };
  };

  /* ---- expressions ---- */

  Interp.prototype.evaluate = function (node, scope) {
    this.tick(node.line);
    switch (node.kind) {
      case 'IntLit':
        return mkInt(node.value, node.value > 2147483647n || node.value < -2147483648n
          ? TY.i64 : TY.i32);
      case 'FloatLit':
        return { t: TY.f32, v: node.value, cd: true };
      case 'BoolLit':
        return mkBool(node.value);
      case 'StringLit':
        return mkString(node.value);
      case 'NullLit':
        return { t: PTR_VOID, v: null };
      case 'Var': {
        var rec = scope.lookup(node.name);
        if (!rec) throw new FlowError("undefined variable '" + node.name + "'", node.line);
        return this.readVarRec(rec, node.line);
      }
      case 'Binary':
        return this.evalBinary(node, scope);
      case 'Unary':
        return this.evalUnary(node, scope);
      case 'Cast':
        return this.evalCast(node, scope);
      case 'Call':
        return this.evalCall(node, scope);
      case 'Index': {
        var target = this.indexTarget(node, scope);
        return this.readCell(target.blk, target.off, target.elem, node.line);
      }
      case 'Field': {
        var base = this.evaluate(node.base, scope);
        if (base.t.k === 'ptr') {
          throw new FlowError(
            "cannot use '.' on a pointer; index it first (p[0]." + node.field + ')', node.line);
        }
        if (base.t.k !== 'struct') {
          throw new FlowError('field access on a ' + base.t.name + ' value', node.line);
        }
        var fv = base.v[node.field];
        if (fv === undefined) {
          throw new FlowError(
            'struct ' + base.t.name + " has no field '" + node.field + "'", node.line);
        }
        return fv;
      }
      case 'StructLit':
        return this.evalStructLit(node, scope);
      case 'ArrayLit': {
        var elems = [];
        for (var i = 0; i < node.elements.length; i++) {
          elems.push(this.evaluate(node.elements[i], scope));
        }
        if (!elems.length) throw new FlowError('empty array literals need a type annotation', node.line);
        var et = elems[0].t;
        var type = arrayType(et, elems.length);
        var blk = new Block(this.sizeOf(type, node.line), 'array');
        var esize = this.sizeOf(et, node.line);
        for (var j = 0; j < elems.length; j++) {
          this.writeCell(blk, j * esize, et, elems[j], node.line);
        }
        return { t: type, v: { blk: blk, off: 0 } };
      }
      default:
        throw new FlowError('cannot evaluate ' + node.kind, node.line);
    }
  };

  Interp.prototype.evalStructLit = function (node, scope) {
    var decl = this.structDecl(node.name, node.line);
    var fields = Object.create(null);
    var seen = Object.create(null);
    for (var i = 0; i < node.fields.length; i++) {
      var f = node.fields[i];
      var ftype = null;
      for (var d = 0; d < decl.fields.length; d++) {
        if (decl.fields[d].name === f.name) ftype = decl.fields[d].type;
      }
      if (!ftype) {
        throw new FlowError(
          'struct ' + node.name + " has no field '" + f.name + "'", node.line);
      }
      var value = this.evaluate(f.value, scope);
      if (ftype.k === 'array') {
        fields[f.name] = this.buildArray(f.value, ftype, scope, node.line, value);
      } else {
        fields[f.name] = this.coerce(value, ftype, node.line, 'field ' + f.name);
      }
      seen[f.name] = true;
    }
    for (var k = 0; k < decl.fields.length; k++) {
      if (!seen[decl.fields[k].name]) {
        fields[decl.fields[k].name] = this.zeroValue(decl.fields[k].type, node.line);
      }
    }
    return { t: structType(node.name), v: fields };
  };

  Interp.prototype.evalUnary = function (node, scope) {
    var line = node.line;
    if (node.op === '&') {
      if (node.operand.kind === 'Var') {
        var rec = scope.lookup(node.operand.name);
        if (!rec) {
          throw new FlowError("undefined variable '" + node.operand.name + "'", line);
        }
        return this.addressOfVar(rec, line);
      }
      if (node.operand.kind === 'Index') {
        var target = this.indexTarget(node.operand, scope);
        return { t: ptrType(target.elem), v: { blk: target.blk, off: target.off } };
      }
      throw new Unsupported('taking the address of this expression', line);
    }
    if (node.op === '*') {
      var p = this.evaluate(node.operand, scope);
      if (p.t.k !== 'ptr') throw new FlowError('cannot dereference a ' + p.t.name, line);
      if (!p.v) throw new FlowError('null pointer dereference', line);
      return this.readCell(p.v.blk, p.v.off, p.t.elem, line);
    }
    var v = this.evaluate(node.operand, scope);
    switch (node.op) {
      case '-':
        if (v.t.k === 'float') return mkFloat(-v.v, v.t, v.cd);
        if (v.t.k === 'int') return mkInt(-v.v, v.t);
        throw new FlowError('cannot negate a ' + v.t.name, line);
      case '!':
        if (v.t.k === 'bool') return mkBool(!v.v);
        if (v.t.k === 'int') return mkBool(v.v === 0n);
        throw new FlowError('cannot apply ! to a ' + v.t.name, line);
      case '~':
        if (v.t.k === 'int') return mkInt(~v.v, v.t);
        throw new FlowError('cannot apply ~ to a ' + v.t.name, line);
      default:
        throw new FlowError('unknown unary operator ' + node.op, line);
    }
  };

  Interp.prototype.evalCast = function (node, scope) {
    var v = this.evaluate(node.expr, scope);
    var t = node.type;
    if (t.k === 'float') {
      return mkFloat(this.toDouble(v, node.line), t, t.bits === 64);
    }
    if (t.k === 'int') {
      if (v.t.k === 'float') return mkInt(BigInt(Math.trunc(v.v)), t);
      return mkInt(bigOf(v, node.line), t);
    }
    if (t.k === 'bool') return mkBool(this.truthy(v, node.line));
    if (t.k === 'ptr') {
      if (v.t.k === 'ptr' || v.t.k === 'array') return { t: t, v: v.v };
    }
    throw new FlowError('cannot cast a ' + v.t.name + ' to ' + t.name, node.line);
  };

  Interp.prototype.evalBinary = function (node, scope) {
    var op = node.op;
    if (op === '&&' || op === '||') {
      var l = this.evaluate(node.left, scope);
      var lb = this.truthy(l, node.line);
      if (op === '&&' && !lb) return mkBool(false);
      if (op === '||' && lb) return mkBool(true);
      var r = this.evaluate(node.right, scope);
      return mkBool(this.truthy(r, node.line));
    }
    var a = this.evaluate(node.left, scope);
    var b = this.evaluate(node.right, scope);
    return this.binary(op, a, b, node.line);
  };

  Interp.prototype.binary = function (op, a, b, line) {
    switch (op) {
      case '==': return mkBool(this.valuesEqual(a, b, line));
      case '!=': return mkBool(!this.valuesEqual(a, b, line));
      default: break;
    }
    if (op === '<' || op === '>' || op === '<=' || op === '>=') {
      if (a.t.k === 'float' || b.t.k === 'float') {
        var x = this.toDouble(a, line), y = this.toDouble(b, line);
        return mkBool(op === '<' ? x < y : op === '>' ? x > y : op === '<=' ? x <= y : x >= y);
      }
      var i = bigOf(a, line), j = bigOf(b, line);
      return mkBool(op === '<' ? i < j : op === '>' ? i > j : op === '<=' ? i <= j : i >= j);
    }
    if (op === '+' && (a.t.k === 'string' || b.t.k === 'string')) {
      return mkString(this.stringify(a, line) + this.stringify(b, line));
    }
    if (a.t.k === 'float' || b.t.k === 'float') {
      var fa = this.toDouble(a, line);
      var fb = this.toDouble(b, line);
      var bits = 32;
      if ((a.t.k === 'float' && a.t.bits === 64) || (b.t.k === 'float' && b.t.bits === 64)) {
        bits = 64;
      }
      var cd = !!a.cd || !!b.cd;
      var res;
      switch (op) {
        case '+': res = fa + fb; break;
        case '-': res = fa - fb; break;
        case '*': res = fa * fb; break;
        case '/': res = fa / fb; break;
        case '%': res = fa % fb; break;
        default:
          throw new FlowError("operator '" + op + "' is not defined for floats", line);
      }
      var ft = bits === 64 ? TY.f64 : TY.f32;
      return { t: ft, v: (bits === 32 && !cd) ? Math.fround(res) : res, cd: cd };
    }
    if (a.t.k === 'ptr' || b.t.k === 'ptr' || a.t.k === 'array' || b.t.k === 'array') {
      return this.pointerArith(op, a, b, line);
    }
    var ia = bigOf(a, line);
    var ib = bigOf(b, line);
    var rt = TY.i32;
    if (a.t.k === 'int' && b.t.k === 'int') {
      rt = (a.t.bits > b.t.bits) ? a.t : (b.t.bits > a.t.bits ? b.t : a.t);
      if (rt.bits < 32) rt = TY.i32;
    } else if (a.t.k === 'int') {
      rt = a.t.bits < 32 ? TY.i32 : a.t;
    } else if (b.t.k === 'int') {
      rt = b.t.bits < 32 ? TY.i32 : b.t;
    }
    var out;
    switch (op) {
      case '+': out = ia + ib; break;
      case '-': out = ia - ib; break;
      case '*': out = ia * ib; break;
      case '/':
        if (ib === 0n) throw new FlowError('integer division by zero', line);
        out = ia / ib;
        break;
      case '%':
        if (ib === 0n) throw new FlowError('integer remainder by zero', line);
        out = ia % ib;
        break;
      case '&': out = ia & ib; break;
      case '|': out = ia | ib; break;
      case '^': out = ia ^ ib; break;
      case '<<': out = ia << ib; break;
      case '>>': out = ia >> ib; break;
      default:
        throw new FlowError("unknown operator '" + op + "'", line);
    }
    return mkInt(out, rt);
  };

  /** C pointer arithmetic: p + n moves by n * sizeof(*p) bytes. */
  Interp.prototype.pointerArith = function (op, a, b, line) {
    var self = this;
    function asPointer(v) {
      if (v.t.k === 'ptr') return { t: v.t, elem: v.t.elem, v: v.v };
      if (v.t.k === 'array') return { t: ptrType(v.t.elem), elem: v.t.elem, v: v.v };
      return null;
    }
    var pa = asPointer(a);
    var pb = asPointer(b);
    if (pa && pb) {
      if (op !== '-') {
        throw new FlowError("operator '" + op + "' is not defined for two pointers", line);
      }
      if (!pa.v || !pb.v) throw new FlowError('pointer difference with a null pointer', line);
      if (pa.v.blk !== pb.v.blk) {
        throw new FlowError('pointer difference across two different allocations', line);
      }
      var esz = this.sizeOf(pa.elem, line) || 1;
      return mkInt(BigInt(Math.trunc((pa.v.off - pb.v.off) / esz)), TY.i64);
    }
    var ptr = pa || pb;
    var other = pa ? b : a;
    if (other.t.k !== 'int' && other.t.k !== 'bool') {
      throw new FlowError(
        'cannot combine a pointer with a ' + other.t.name + ' value', line);
    }
    if (op !== '+' && op !== '-') {
      throw new FlowError(
        "operator '" + op + "' is not defined for pointers", line);
    }
    if (op === '-' && pb) {
      throw new FlowError('cannot subtract a pointer from an integer', line);
    }
    if (!ptr.v) throw new FlowError('pointer arithmetic on a null pointer', line);
    var size = this.sizeOf(ptr.elem, line) || 1;
    var delta = Number(bigOf(other, line)) * size;
    var off = op === '-' ? ptr.v.off - delta : ptr.v.off + delta;
    if (off < 0 || off > ptr.v.blk.size) {
      throw new FlowError(
        'pointer arithmetic moved outside the ' + ptr.v.blk.size + '-byte ' +
        ptr.v.blk.tag, line);
    }
    self = null;
    return { t: ptr.t, v: { blk: ptr.v.blk, off: off } };
  };

  Interp.prototype.stringify = function (val, line) {
    if (val.t.k === 'string') return val.v;
    return this.defaultRender(val, line);
  };

  Interp.prototype.evalCall = function (node, scope) {
    var fn = this.prog.functions[node.name];
    var args = [];
    for (var i = 0; i < node.args.length; i++) {
      args.push(this.evaluate(node.args[i], scope));
    }
    if (!fn) {
      if (BUILTIN_NAMES[node.name]) return this.callBuiltin(node.name, args, node);
      throw new FlowError("undefined function '" + node.name + "'", node.line);
    }
    return this.callFunction(fn, args, node.line);
  };

  Interp.prototype.callFunction = function (fn, args, line) {
    if (args.length !== fn.params.length) {
      throw new FlowError(
        "function '" + fn.name + "' takes " + fn.params.length +
        ' argument(s) but got ' + args.length, line);
    }
    if (++this.depth > DEPTH_LIMIT) {
      this.depth--;
      throw new FlowError(
        'recursion depth limit (' + DEPTH_LIMIT + ') exceeded in ' + fn.name + '()', line);
    }
    try {
      var scope = new Scope(this.globals);
      for (var i = 0; i < fn.params.length; i++) {
        var p = fn.params[i];
        var v = this.coerce(args[i], p.type, line, "argument '" + p.name + "'");
        this.declare(scope, p.name, p.type, true, v, line);
      }
      var sig = this.execBlock(fn.body, scope);
      if (sig && sig.sig === SIG_RETURN) {
        if (fn.ret.k === 'void') return VOID_VALUE;
        return this.coerce(sig.value, fn.ret, sig.line, 'return value of ' + fn.name);
      }
      if (fn.ret.k !== 'void') {
        throw new FlowError(
          "function '" + fn.name + "' ended without returning a " + fn.ret.name, fn.line);
      }
      return VOID_VALUE;
    } finally {
      this.depth--;
    }
  };

  /* ==================================================================== *
   * Static checks before execution
   * ==================================================================== */

  function walkExpr(node, visit) {
    if (!node || typeof node !== 'object') return;
    visit(node);
    var keys = ['left', 'right', 'operand', 'expr', 'base', 'index', 'value',
      'cond', 'subject', 'start', 'end', 'step'];
    for (var i = 0; i < keys.length; i++) {
      if (node[keys[i]]) walkExpr(node[keys[i]], visit);
    }
    if (node.args) node.args.forEach(function (a) { walkExpr(a, visit); });
    if (node.elements) node.elements.forEach(function (a) { walkExpr(a, visit); });
    if (node.fields) node.fields.forEach(function (f) { walkExpr(f.value, visit); });
    if (node.body && node.body.length !== undefined) {
      node.body.forEach(function (s) { walkExpr(s, visit); });
    } else if (node.body) {
      walkExpr(node.body, visit);
    }
    if (node.then) walkExpr(node.then, visit);
    if (node.otherwise) walkExpr(node.otherwise, visit);
    if (node.target) walkExpr(node.target, visit);
    if (node.cases) {
      node.cases.forEach(function (c) {
        walkExpr(c.body, visit);
        if (c.guard) walkExpr(c.guard, visit);
      });
    }
    if (node.fallback) walkExpr(node.fallback, visit);
  }

  /** Reject unknown calls before running so we never print half a program. */
  function checkCalls(prog) {
    var names = prog.functionOrder;
    for (var i = 0; i < names.length; i++) {
      var fn = prog.functions[names[i]];
      walkExpr(fn.body, function (n) {
        if (n.kind !== 'Call') return;
        if (prog.functions[n.name]) return;
        if (BUILTIN_NAMES[n.name]) return;
        throw new Unsupported(
          "the function '" + n.name + "'",
          n.line,
          'It is not defined in this snippet and is not one of the builtins the ' +
          'browser interpreter emulates.');
      });
    }
  }

  /* ==================================================================== *
   * AST rendering (real, from the parser)
   * ==================================================================== */

  function astText(prog) {
    var lines = ['Module {'];
    function ind(n) { return new Array(n + 1).join('  '); }

    prog.structOrder.forEach(function (name) {
      var s = prog.structs[name];
      lines.push(ind(1) + 'StructDecl ' + name + ' {');
      s.fields.forEach(function (f) {
        lines.push(ind(2) + f.name + ': ' + f.type.name);
      });
      lines.push(ind(1) + '}');
    });

    prog.functionOrder.forEach(function (name) {
      var f = prog.functions[name];
      var params = f.params.map(function (p) { return p.name + ': ' + p.type.name; });
      lines.push(ind(1) + 'FunctionDecl ' + name + '(' + params.join(', ') + ') -> ' + f.ret.name + ' {');
      renderStmts(f.body.body, 2);
      lines.push(ind(1) + '}');
    });

    lines.push('}');
    return lines.join('\n');

    function renderStmts(stmts, depth) {
      stmts.forEach(function (s) { renderStmt(s, depth); });
    }

    function renderStmt(s, depth) {
      switch (s.kind) {
        case 'Let':
          lines.push(ind(depth) + 'Let ' + (s.mut ? 'mut ' : '') + s.name +
            (s.type ? ': ' + s.type.name : '') + ' = ' + expr(s.value));
          break;
        case 'Assign':
          lines.push(ind(depth) + 'Assign ' + expr(s.target) + ' ' + s.op + '= ' + expr(s.value));
          break;
        case 'Return':
          lines.push(ind(depth) + 'Return' + (s.value ? ' ' + expr(s.value) : ''));
          break;
        case 'ExprStmt':
          lines.push(ind(depth) + 'Expr ' + expr(s.expr));
          break;
        case 'If':
          lines.push(ind(depth) + 'If ' + expr(s.cond) + ' {');
          renderStmts(s.then.body, depth + 1);
          if (s.otherwise) {
            lines.push(ind(depth) + '} else {');
            renderStmts(s.otherwise.body, depth + 1);
          }
          lines.push(ind(depth) + '}');
          break;
        case 'While':
          lines.push(ind(depth) + 'While ' + expr(s.cond) + ' {');
          renderStmts(s.body.body, depth + 1);
          lines.push(ind(depth) + '}');
          break;
        case 'For':
          lines.push(ind(depth) + 'For ' + s.name + ' in ' + expr(s.start) + ' to ' +
            expr(s.end) + (s.step ? ' step ' + expr(s.step) : '') + ' {');
          renderStmts(s.body.body, depth + 1);
          lines.push(ind(depth) + '}');
          break;
        case 'Match':
          lines.push(ind(depth) + 'Match ' + expr(s.subject) + ' {');
          s.cases.forEach(function (c) {
            lines.push(ind(depth + 1) + c.patterns.map(patText).join(' | ') + ' => {');
            renderStmts(c.body.body, depth + 2);
            lines.push(ind(depth + 1) + '}');
          });
          if (s.fallback) {
            lines.push(ind(depth + 1) + 'default {');
            renderStmts(s.fallback.body, depth + 2);
            lines.push(ind(depth + 1) + '}');
          }
          lines.push(ind(depth) + '}');
          break;
        case 'Block':
          lines.push(ind(depth) + 'Block {');
          renderStmts(s.body, depth + 1);
          lines.push(ind(depth) + '}');
          break;
        default:
          lines.push(ind(depth) + s.kind);
      }
    }

    function patText(p) {
      return p.kind === 'LiteralPattern' ? expr(p.expr) : p.name;
    }

    function expr(e) {
      if (!e) return '';
      switch (e.kind) {
        case 'IntLit': return e.value.toString();
        case 'FloatLit': return String(e.value);
        case 'BoolLit': return String(e.value);
        case 'StringLit': return JSON.stringify(e.value);
        case 'NullLit': return 'null';
        case 'Var': return e.name;
        case 'Binary': return '(' + expr(e.left) + ' ' + e.op + ' ' + expr(e.right) + ')';
        case 'Unary': return e.op + expr(e.operand);
        case 'Cast': return '(' + expr(e.expr) + ' as ' + e.type.name + ')';
        case 'Call': return e.name + '(' + e.args.map(expr).join(', ') + ')';
        case 'Index': return expr(e.base) + '[' + expr(e.index) + ']';
        case 'Field': return expr(e.base) + '.' + e.field;
        case 'ArrayLit': return '[' + e.elements.map(expr).join(', ') + ']';
        case 'StructLit':
          return e.name + ' { ' + e.fields.map(function (f) {
            return f.name + ': ' + expr(f.value);
          }).join(', ') + ' }';
        default: return e.kind;
      }
    }
  }

  var C_NOTICE =
    '// The browser interpreter executes Flow directly — it does not generate C.\n' +
    '// Nothing is shown here rather than a plausible-looking fake.\n' +
    '//\n' +
    '// For the real C the native backend emits:\n' +
    '//     ./flow transpile yourfile.flow --c -o yourfile.c\n';

  var MLIR_NOTICE =
    '// The browser interpreter executes Flow directly — it does not lower to MLIR.\n' +
    '// Nothing is shown here rather than a plausible-looking fake.\n' +
    '//\n' +
    '// For real MLIR from the native backend:\n' +
    '//     ./flow transpile yourfile.flow --mlir -o yourfile.mlir\n';

  /* ==================================================================== *
   * Public API
   * ==================================================================== */

  function compileProgram(code) {
    var tokens = lex(code);
    var parser = new Parser(tokens, collectStructNames(tokens));
    var prog = parser.parseProgram();
    checkCalls(prog);
    return prog;
  }

  function execute(code) {
    var prog = compileProgram(code);
    if (!prog.functions.main) {
      throw new FlowError('no main() function found — execution starts at main()', 0);
    }
    var interp = new Interp(prog);
    var mainFn = prog.functions.main;
    if (mainFn.params.length) {
      throw new Unsupported('main() with parameters', mainFn.line);
    }
    var exit = 0;
    var runError = null;
    try {
      var rv = interp.callFunction(mainFn, [], mainFn.line);
      if (rv && rv.t.k === 'int') exit = Number(BigInt.asIntN(32, rv.v));
    } catch (err) {
      runError = err;
    }
    return {
      prog: prog,
      output: interp.stdout(),
      exitCode: exit,
      steps: interp.steps,
      error: runError
    };
  }

  function errorResult(err, partialOutput, prog) {
    if (err instanceof Unsupported || err.name === 'Unsupported') {
      return {
        ok: false,
        unsupported: true,
        construct: err.construct,
        line: err.line,
        error: err.message,
        output: '',
        exitCode: null,
        ast: prog ? astText(prog) : '',
        c: '',
        mlir: ''
      };
    }
    var message = err instanceof FlowError || err.name === 'FlowError'
      ? err.message
      : (err && err.message ? err.message : String(err));
    return {
      ok: false,
      unsupported: false,
      line: err.line || 0,
      error: message,
      output: partialOutput || '',
      exitCode: null,
      ast: prog ? astText(prog) : '',
      c: '',
      mlir: ''
    };
  }

  function compileAndRun(code) {
    var run;
    try {
      run = execute(code);
    } catch (err) {
      return errorResult(err, '', null);
    }
    if (run.error) {
      var r = errorResult(run.error, run.output, run.prog);
      return r;
    }
    return {
      ok: true,
      unsupported: false,
      output: run.output,
      exitCode: run.exitCode,
      steps: run.steps,
      ast: astText(run.prog),
      c: C_NOTICE,
      mlir: MLIR_NOTICE,
      error: null
    };
  }

  /** Backwards-compatible shape used by older callers. */
  function simulate(code) {
    var r = compileAndRun(code);
    if (!r.ok) throw new FlowError(r.error, r.line || 0);
    return { output: r.output, ast: r.ast, c: r.c, mlir: r.mlir };
  }

  global.FlowCompile = {
    run: compileAndRun,
    simulate: simulate,
    parse: compileProgram,
    version: '2-interpreter'
  };
})(typeof window !== 'undefined' ? window : globalThis);
