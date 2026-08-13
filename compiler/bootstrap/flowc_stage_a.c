#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
#include <complex.h>
typedef float complex c64;
typedef double complex c128;

static inline const char* __flowc_str_concat(const char* a, const char* b) {
  size_t la; size_t lb; char* r;
  if (a == 0) { a = ""; }
  if (b == 0) { b = ""; }
  la = strlen(a); lb = strlen(b);
  r = (char*)malloc(la + lb + 1);
  if (r == 0) { return ""; }
  memcpy(r, a, la); memcpy(r + la, b, lb); r[la + lb] = 0;
  return r;
}

static const int32_t FLOWC_IO_SEEK_SET = 0;
static const int32_t FLOWC_IO_SEEK_END = 2;
void* flowc_io_fopen(const char* path, const char* mode) {
  return fopen(path, mode);
}

int32_t flowc_io_fclose(void* fp) {
  return fclose(fp);
}

int32_t flowc_io_fread(uint8_t* buf, int32_t size, int32_t n, void* fp) {
  return fread(buf, size, n, fp);
}

int32_t flowc_io_fwrite(uint8_t* buf, int32_t size, int32_t n, void* fp) {
  return fwrite(buf, size, n, fp);
}

int32_t flowc_io_fseek(void* fp, int64_t offset, int32_t whence) {
  return fseek(fp, offset, whence);
}

int64_t flowc_io_ftell(void* fp) {
  return ftell(fp);
}

int32_t flowc_read_file(const char* path, uint8_t* buf, int32_t cap) {
  void* fp = (void*)(flowc_io_fopen(path, "rb"));
  if (fp == NULL) {
  return (-1);
}
  if (cap <= 0) {
  int32_t _c0 = flowc_io_fclose(fp);
  return 0;
}
  int32_t n = flowc_io_fread(buf, 1, cap, fp);
  int32_t _c = flowc_io_fclose(fp);
  if (n < 0) {
  return (-1);
}
  return n;
}

int32_t flowc_write_file(const char* path, uint8_t* buf, int32_t n) {
  void* fp = (void*)(flowc_io_fopen(path, "wb"));
  if (fp == NULL) {
  return (-1);
}
  if (n <= 0) {
  int32_t _c0 = flowc_io_fclose(fp);
  return 0;
}
  int32_t wrote = flowc_io_fwrite(buf, 1, n, fp);
  int32_t _c = flowc_io_fclose(fp);
  if (wrote != n) {
  return (-1);
}
  return 0;
}


typedef struct Token {
  int32_t kind;
  int32_t kw;
  int32_t start;
  int32_t end;
  int32_t line;
  int32_t col;
} Token;

typedef struct Lexer {
  uint8_t* input;
  int32_t len;
  int32_t pos;
  int32_t line;
  int32_t col;
} Lexer;

const int32_t TOK_EOF = 0;
const int32_t TOK_IDENT = 1;
const int32_t TOK_KEYWORD = 2;
const int32_t TOK_INT = 3;
const int32_t TOK_FLOAT = 4;
const int32_t TOK_STRING = 5;
const int32_t TOK_LPAREN = 6;
const int32_t TOK_RPAREN = 7;
const int32_t TOK_LBRACE = 8;
const int32_t TOK_RBRACE = 9;
const int32_t TOK_LBRACK = 10;
const int32_t TOK_RBRACK = 11;
const int32_t TOK_COLON = 12;
const int32_t TOK_COMMA = 13;
const int32_t TOK_SEMI = 14;
const int32_t TOK_DOT = 15;
const int32_t TOK_ARROW = 16;
const int32_t TOK_EQ = 17;
const int32_t TOK_EQEQ = 18;
const int32_t TOK_NE = 19;
const int32_t TOK_LT = 20;
const int32_t TOK_LE = 21;
const int32_t TOK_GT = 22;
const int32_t TOK_GE = 23;
const int32_t TOK_PLUS = 24;
const int32_t TOK_MINUS = 25;
const int32_t TOK_STAR = 26;
const int32_t TOK_SLASH = 27;
const int32_t TOK_AMPAMP = 28;
const int32_t TOK_BARBAR = 29;
const int32_t TOK_BANG = 30;
const int32_t TOK_ERROR = 31;
const int32_t TOK_AMP = 32;
const int32_t TOK_PERCENT = 33;
const int32_t TOK_DOTDOT = 34;
const int32_t TOK_FATARROW = 35;
const int32_t TOK_TILDE = 36;
const int32_t TOK_AT = 37;
const int32_t TOK_BAR = 38;
const int32_t TOK_CARET = 39;
const int32_t TOK_SHL = 40;
const int32_t TOK_SHR = 41;
const int32_t TOK_PLUS_EQ = 42;
const int32_t TOK_MINUS_EQ = 43;
const int32_t TOK_STAR_EQ = 44;
const int32_t TOK_SLASH_EQ = 45;
const int32_t TOK_PERCENT_EQ = 46;
const int32_t KW_LET = 1;
const int32_t KW_FUNCTION = 2;
const int32_t KW_RETURN = 3;
const int32_t KW_IF = 4;
const int32_t KW_ELSE = 5;
const int32_t KW_WHILE = 6;
const int32_t KW_FOR = 7;
const int32_t KW_IN = 8;
const int32_t KW_TO = 9;
const int32_t KW_STRUCT = 10;
const int32_t KW_MUT = 11;
const int32_t KW_EXTERN = 12;
const int32_t KW_TRUE = 13;
const int32_t KW_FALSE = 14;
const int32_t KW_NULL = 15;
const int32_t KW_IMPORT = 16;
const int32_t KW_EXPORT = 17;
const int32_t KW_BREAK = 18;
const int32_t KW_CONTINUE = 19;
const int32_t KW_CONST = 20;
const int32_t KW_AS = 21;
const int32_t KW_AND = 22;
const int32_t KW_OR = 23;
const int32_t KW_MATCH = 24;
const int32_t KW_ELIF = 25;
const int32_t KW_TYPE = 26;
const int32_t KW_UNIT = 27;
const int32_t KW_EFFECT = 28;
const int32_t KW_CAPABILITY = 29;
const int32_t KW_NOT = 30;
Token flowc_make_tok(int32_t kind, int32_t kw, int32_t start, int32_t end, int32_t line, int32_t col) {
  return (Token){ .kind = kind, .kw = kw, .start = start, .end = end, .line = line, .col = col };
}


int32_t flowc_lex_is_alpha(int32_t c) {
  if (c >= 65 && c <= 90 || c >= 97 && c <= 122 || c == 95) {
  return 1;
}
  return 0;
}

int32_t flowc_lex_is_digit(int32_t c) {
  if (c >= 48 && c <= 57) {
  return 1;
}
  return 0;
}

int32_t flowc_lex_is_alnum(int32_t c) {
  if (flowc_lex_is_alpha(c) == 1 || flowc_lex_is_digit(c) == 1) {
  return 1;
}
  return 0;
}

int32_t flowc_lex_is_space(int32_t c) {
  if (c == 32 || c == 9 || c == 13) {
  return 1;
}
  return 0;
}

Lexer flowc_lexer_new(uint8_t* input, int32_t len) {
  return (Lexer){ .input = input, .len = len, .pos = 0, .line = 1, .col = 1 };
}

void flowc_lexer_bump(Lexer* lex) {
  int32_t c = (lex[0]).input[(lex[0]).pos];
  (lex[0]).pos = ((lex[0]).pos + 1);
  if (c == 10) {
  (lex[0]).line = ((lex[0]).line + 1);
  (lex[0]).col = 1;
} else {
  (lex[0]).col = ((lex[0]).col + 1);
}
}

void flowc_lexer_skip_trivia(Lexer* lex) {
  while ((lex[0]).pos < (lex[0]).len) {
  int32_t c = (lex[0]).input[(lex[0]).pos];
  if (flowc_lex_is_space(c) == 1) {
  flowc_lexer_bump(lex);
} else {
  if (c == 10) {
  flowc_lexer_bump(lex);
} else {
  if (c == 35) {
  while ((lex[0]).pos < (lex[0]).len && (lex[0]).input[(lex[0]).pos] != 10) {
  flowc_lexer_bump(lex);
}
} else {
  return;
}
}
}
}
}

int32_t flowc_lex_ident_eq(uint8_t* src, int32_t start, int32_t end, uint8_t* lit, int32_t lit_len) {
  if ((end - start) != lit_len) {
  return 0;
}
  int32_t i = 0;
  while (i < lit_len) {
  if (src[(start + i)] != lit[i]) {
  return 0;
}
  i = (i + 1);
}
  return 1;
}

int32_t flowc_lex_classify_keyword(uint8_t* src, int32_t start, int32_t end) {
  uint8_t let_kw[3] = { 108, 101, 116 };
  uint8_t fn_kw[8] = { 102, 117, 110, 99, 116, 105, 111, 110 };
  uint8_t ret_kw[6] = { 114, 101, 116, 117, 114, 110 };
  uint8_t if_kw[2] = { 105, 102 };
  uint8_t else_kw[4] = { 101, 108, 115, 101 };
  uint8_t elif_kw[4] = { 101, 108, 105, 102 };
  uint8_t while_kw[5] = { 119, 104, 105, 108, 101 };
  uint8_t for_kw[3] = { 102, 111, 114 };
  uint8_t in_kw[2] = { 105, 110 };
  uint8_t to_kw[2] = { 116, 111 };
  uint8_t struct_kw[6] = { 115, 116, 114, 117, 99, 116 };
  uint8_t mut_kw[3] = { 109, 117, 116 };
  uint8_t extern_kw[6] = { 101, 120, 116, 101, 114, 110 };
  uint8_t true_kw[4] = { 116, 114, 117, 101 };
  uint8_t false_kw[5] = { 102, 97, 108, 115, 101 };
  uint8_t null_kw[4] = { 110, 117, 108, 108 };
  uint8_t import_kw[6] = { 105, 109, 112, 111, 114, 116 };
  uint8_t export_kw[6] = { 101, 120, 112, 111, 114, 116 };
  uint8_t break_kw[5] = { 98, 114, 101, 97, 107 };
  uint8_t continue_kw[8] = { 99, 111, 110, 116, 105, 110, 117, 101 };
  uint8_t const_kw[5] = { 99, 111, 110, 115, 116 };
  uint8_t as_kw[2] = { 97, 115 };
  uint8_t and_kw[3] = { 97, 110, 100 };
  uint8_t or_kw[2] = { 111, 114 };
  uint8_t match_kw[5] = { 109, 97, 116, 99, 104 };
  uint8_t type_kw[4] = { 116, 121, 112, 101 };
  uint8_t unit_kw[4] = { 117, 110, 105, 116 };
  uint8_t effect_kw[6] = { 101, 102, 102, 101, 99, 116 };
  uint8_t cap_kw[10] = { 99, 97, 112, 97, 98, 105, 108, 105, 116, 121 };
  uint8_t not_kw[3] = { 110, 111, 116 };
  uint8_t* p = (uint8_t*)(let_kw);
  if (flowc_lex_ident_eq(src, start, end, p, 3) == 1) {
  return KW_LET;
}
  p = fn_kw;
  if (flowc_lex_ident_eq(src, start, end, p, 8) == 1) {
  return KW_FUNCTION;
}
  p = ret_kw;
  if (flowc_lex_ident_eq(src, start, end, p, 6) == 1) {
  return KW_RETURN;
}
  p = if_kw;
  if (flowc_lex_ident_eq(src, start, end, p, 2) == 1) {
  return KW_IF;
}
  p = else_kw;
  if (flowc_lex_ident_eq(src, start, end, p, 4) == 1) {
  return KW_ELSE;
}
  p = elif_kw;
  if (flowc_lex_ident_eq(src, start, end, p, 4) == 1) {
  return KW_ELIF;
}
  p = while_kw;
  if (flowc_lex_ident_eq(src, start, end, p, 5) == 1) {
  return KW_WHILE;
}
  p = for_kw;
  if (flowc_lex_ident_eq(src, start, end, p, 3) == 1) {
  return KW_FOR;
}
  p = in_kw;
  if (flowc_lex_ident_eq(src, start, end, p, 2) == 1) {
  return KW_IN;
}
  p = to_kw;
  if (flowc_lex_ident_eq(src, start, end, p, 2) == 1) {
  return KW_TO;
}
  p = struct_kw;
  if (flowc_lex_ident_eq(src, start, end, p, 6) == 1) {
  return KW_STRUCT;
}
  p = mut_kw;
  if (flowc_lex_ident_eq(src, start, end, p, 3) == 1) {
  return KW_MUT;
}
  p = extern_kw;
  if (flowc_lex_ident_eq(src, start, end, p, 6) == 1) {
  return KW_EXTERN;
}
  p = true_kw;
  if (flowc_lex_ident_eq(src, start, end, p, 4) == 1) {
  return KW_TRUE;
}
  p = false_kw;
  if (flowc_lex_ident_eq(src, start, end, p, 5) == 1) {
  return KW_FALSE;
}
  p = null_kw;
  if (flowc_lex_ident_eq(src, start, end, p, 4) == 1) {
  return KW_NULL;
}
  p = import_kw;
  if (flowc_lex_ident_eq(src, start, end, p, 6) == 1) {
  return KW_IMPORT;
}
  p = export_kw;
  if (flowc_lex_ident_eq(src, start, end, p, 6) == 1) {
  return KW_EXPORT;
}
  p = break_kw;
  if (flowc_lex_ident_eq(src, start, end, p, 5) == 1) {
  return KW_BREAK;
}
  p = continue_kw;
  if (flowc_lex_ident_eq(src, start, end, p, 8) == 1) {
  return KW_CONTINUE;
}
  p = const_kw;
  if (flowc_lex_ident_eq(src, start, end, p, 5) == 1) {
  return KW_CONST;
}
  p = as_kw;
  if (flowc_lex_ident_eq(src, start, end, p, 2) == 1) {
  return KW_AS;
}
  p = and_kw;
  if (flowc_lex_ident_eq(src, start, end, p, 3) == 1) {
  return KW_AND;
}
  p = or_kw;
  if (flowc_lex_ident_eq(src, start, end, p, 2) == 1) {
  return KW_OR;
}
  p = match_kw;
  if (flowc_lex_ident_eq(src, start, end, p, 5) == 1) {
  return KW_MATCH;
}
  p = type_kw;
  if (flowc_lex_ident_eq(src, start, end, p, 4) == 1) {
  return KW_TYPE;
}
  p = unit_kw;
  if (flowc_lex_ident_eq(src, start, end, p, 4) == 1) {
  return KW_UNIT;
}
  p = effect_kw;
  if (flowc_lex_ident_eq(src, start, end, p, 6) == 1) {
  return KW_EFFECT;
}
  p = cap_kw;
  if (flowc_lex_ident_eq(src, start, end, p, 10) == 1) {
  return KW_CAPABILITY;
}
  p = not_kw;
  if (flowc_lex_ident_eq(src, start, end, p, 3) == 1) {
  return KW_NOT;
}
  return 0;
}

Token flowc_lexer_next(Lexer* lex) {
  flowc_lexer_skip_trivia(lex);
  int32_t start = (lex[0]).pos;
  int32_t line = (lex[0]).line;
  int32_t col = (lex[0]).col;
  if ((lex[0]).pos >= (lex[0]).len) {
  return flowc_make_tok(TOK_EOF, 0, start, start, line, col);
}
  int32_t c = (lex[0]).input[(lex[0]).pos];
  if (flowc_lex_is_alpha(c) == 1) {
  flowc_lexer_bump(lex);
  while ((lex[0]).pos < (lex[0]).len && flowc_lex_is_alnum((lex[0]).input[(lex[0]).pos]) == 1) {
  flowc_lexer_bump(lex);
}
  int32_t end = (lex[0]).pos;
  int32_t kw = flowc_lex_classify_keyword((lex[0]).input, start, end);
  if (kw != 0) {
  return flowc_make_tok(TOK_KEYWORD, kw, start, end, line, col);
}
  return flowc_make_tok(TOK_IDENT, 0, start, end, line, col);
}
  if (flowc_lex_is_digit(c) == 1) {
  flowc_lexer_bump(lex);
  if (c == 48 && (lex[0]).pos < (lex[0]).len && (lex[0]).input[(lex[0]).pos] == 120 || (lex[0]).input[(lex[0]).pos] == 88) {
  flowc_lexer_bump(lex);
  while ((lex[0]).pos < (lex[0]).len && flowc_lex_is_alnum((lex[0]).input[(lex[0]).pos]) == 1) {
  flowc_lexer_bump(lex);
}
  int32_t end = (lex[0]).pos;
  return flowc_make_tok(TOK_INT, 0, start, end, line, col);
}
  while ((lex[0]).pos < (lex[0]).len && flowc_lex_is_digit((lex[0]).input[(lex[0]).pos]) == 1) {
  flowc_lexer_bump(lex);
}
  int32_t is_float = 0;
  if ((lex[0]).pos < (lex[0]).len && (lex[0]).input[(lex[0]).pos] == 46) {
  if (((lex[0]).pos + 1) < (lex[0]).len && flowc_lex_is_digit((lex[0]).input[((lex[0]).pos + 1)]) == 1) {
  is_float = 1;
  flowc_lexer_bump(lex);
  while ((lex[0]).pos < (lex[0]).len && flowc_lex_is_digit((lex[0]).input[(lex[0]).pos]) == 1) {
  flowc_lexer_bump(lex);
}
}
}
  if ((lex[0]).pos < (lex[0]).len && (lex[0]).input[(lex[0]).pos] == 101 || (lex[0]).input[(lex[0]).pos] == 69) {
  int32_t save_pos = (lex[0]).pos;
  flowc_lexer_bump(lex);
  if ((lex[0]).pos < (lex[0]).len && (lex[0]).input[(lex[0]).pos] == 43 || (lex[0]).input[(lex[0]).pos] == 45) {
  flowc_lexer_bump(lex);
}
  if ((lex[0]).pos < (lex[0]).len && flowc_lex_is_digit((lex[0]).input[(lex[0]).pos]) == 1) {
  is_float = 1;
  while ((lex[0]).pos < (lex[0]).len && flowc_lex_is_digit((lex[0]).input[(lex[0]).pos]) == 1) {
  flowc_lexer_bump(lex);
}
} else {
  (lex[0]).pos = save_pos;
}
}
  int32_t end = (lex[0]).pos;
  if (is_float == 1) {
  return flowc_make_tok(TOK_FLOAT, 0, start, end, line, col);
}
  return flowc_make_tok(TOK_INT, 0, start, end, line, col);
}
  if (c == 34) {
  flowc_lexer_bump(lex);
  while ((lex[0]).pos < (lex[0]).len && (lex[0]).input[(lex[0]).pos] != 34) {
  if ((lex[0]).input[(lex[0]).pos] == 92 && ((lex[0]).pos + 1) < (lex[0]).len) {
  flowc_lexer_bump(lex);
}
  flowc_lexer_bump(lex);
}
  if ((lex[0]).pos < (lex[0]).len) {
  flowc_lexer_bump(lex);
  return flowc_make_tok(TOK_STRING, 0, start, (lex[0]).pos, line, col);
}
  return flowc_make_tok(TOK_ERROR, 0, start, (lex[0]).pos, line, col);
}
  int32_t n1 = 0;
  if (((lex[0]).pos + 1) < (lex[0]).len) {
  n1 = (lex[0]).input[((lex[0]).pos + 1)];
}
  if (c == 45 && n1 == 62) {
  flowc_lexer_bump(lex);
  flowc_lexer_bump(lex);
  return flowc_make_tok(TOK_ARROW, 0, start, (start + 2), line, col);
}
  if (c == 60 && n1 == 60) {
  flowc_lexer_bump(lex);
  flowc_lexer_bump(lex);
  return flowc_make_tok(TOK_SHL, 0, start, (start + 2), line, col);
}
  if (c == 62 && n1 == 62) {
  flowc_lexer_bump(lex);
  flowc_lexer_bump(lex);
  return flowc_make_tok(TOK_SHR, 0, start, (start + 2), line, col);
}
  if (c == 43 && n1 == 61) {
  flowc_lexer_bump(lex);
  flowc_lexer_bump(lex);
  return flowc_make_tok(TOK_PLUS_EQ, 0, start, (start + 2), line, col);
}
  if (c == 45 && n1 == 61) {
  flowc_lexer_bump(lex);
  flowc_lexer_bump(lex);
  return flowc_make_tok(TOK_MINUS_EQ, 0, start, (start + 2), line, col);
}
  if (c == 42 && n1 == 61) {
  flowc_lexer_bump(lex);
  flowc_lexer_bump(lex);
  return flowc_make_tok(TOK_STAR_EQ, 0, start, (start + 2), line, col);
}
  if (c == 47 && n1 == 61) {
  flowc_lexer_bump(lex);
  flowc_lexer_bump(lex);
  return flowc_make_tok(TOK_SLASH_EQ, 0, start, (start + 2), line, col);
}
  if (c == 37 && n1 == 61) {
  flowc_lexer_bump(lex);
  flowc_lexer_bump(lex);
  return flowc_make_tok(TOK_PERCENT_EQ, 0, start, (start + 2), line, col);
}
  if (c == 61 && n1 == 61) {
  flowc_lexer_bump(lex);
  flowc_lexer_bump(lex);
  return flowc_make_tok(TOK_EQEQ, 0, start, (start + 2), line, col);
}
  if (c == 61 && n1 == 62) {
  flowc_lexer_bump(lex);
  flowc_lexer_bump(lex);
  return flowc_make_tok(TOK_FATARROW, 0, start, (start + 2), line, col);
}
  if (c == 33 && n1 == 61) {
  flowc_lexer_bump(lex);
  flowc_lexer_bump(lex);
  return flowc_make_tok(TOK_NE, 0, start, (start + 2), line, col);
}
  if (c == 60 && n1 == 61) {
  flowc_lexer_bump(lex);
  flowc_lexer_bump(lex);
  return flowc_make_tok(TOK_LE, 0, start, (start + 2), line, col);
}
  if (c == 62 && n1 == 61) {
  flowc_lexer_bump(lex);
  flowc_lexer_bump(lex);
  return flowc_make_tok(TOK_GE, 0, start, (start + 2), line, col);
}
  if (c == 38 && n1 == 38) {
  flowc_lexer_bump(lex);
  flowc_lexer_bump(lex);
  return flowc_make_tok(TOK_AMPAMP, 0, start, (start + 2), line, col);
}
  if (c == 124 && n1 == 124) {
  flowc_lexer_bump(lex);
  flowc_lexer_bump(lex);
  return flowc_make_tok(TOK_BARBAR, 0, start, (start + 2), line, col);
}
  flowc_lexer_bump(lex);
  if (c == 40) {
  return flowc_make_tok(TOK_LPAREN, 0, start, (start + 1), line, col);
}
  if (c == 41) {
  return flowc_make_tok(TOK_RPAREN, 0, start, (start + 1), line, col);
}
  if (c == 123) {
  return flowc_make_tok(TOK_LBRACE, 0, start, (start + 1), line, col);
}
  if (c == 125) {
  return flowc_make_tok(TOK_RBRACE, 0, start, (start + 1), line, col);
}
  if (c == 91) {
  return flowc_make_tok(TOK_LBRACK, 0, start, (start + 1), line, col);
}
  if (c == 93) {
  return flowc_make_tok(TOK_RBRACK, 0, start, (start + 1), line, col);
}
  if (c == 58) {
  return flowc_make_tok(TOK_COLON, 0, start, (start + 1), line, col);
}
  if (c == 44) {
  return flowc_make_tok(TOK_COMMA, 0, start, (start + 1), line, col);
}
  if (c == 59) {
  return flowc_make_tok(TOK_SEMI, 0, start, (start + 1), line, col);
}
  if (c == 46 && n1 == 46) {
  flowc_lexer_bump(lex);
  return flowc_make_tok(TOK_DOTDOT, 0, start, (start + 2), line, col);
}
  if (c == 46) {
  return flowc_make_tok(TOK_DOT, 0, start, (start + 1), line, col);
}
  if (c == 61) {
  return flowc_make_tok(TOK_EQ, 0, start, (start + 1), line, col);
}
  if (c == 60) {
  return flowc_make_tok(TOK_LT, 0, start, (start + 1), line, col);
}
  if (c == 62) {
  return flowc_make_tok(TOK_GT, 0, start, (start + 1), line, col);
}
  if (c == 43) {
  return flowc_make_tok(TOK_PLUS, 0, start, (start + 1), line, col);
}
  if (c == 45) {
  return flowc_make_tok(TOK_MINUS, 0, start, (start + 1), line, col);
}
  if (c == 42) {
  return flowc_make_tok(TOK_STAR, 0, start, (start + 1), line, col);
}
  if (c == 47) {
  return flowc_make_tok(TOK_SLASH, 0, start, (start + 1), line, col);
}
  if (c == 37) {
  return flowc_make_tok(TOK_PERCENT, 0, start, (start + 1), line, col);
}
  if (c == 33) {
  return flowc_make_tok(TOK_BANG, 0, start, (start + 1), line, col);
}
  if (c == 38) {
  return flowc_make_tok(TOK_AMP, 0, start, (start + 1), line, col);
}
  if (c == 126) {
  return flowc_make_tok(TOK_TILDE, 0, start, (start + 1), line, col);
}
  if (c == 64) {
  return flowc_make_tok(TOK_AT, 0, start, (start + 1), line, col);
}
  if (c == 124) {
  return flowc_make_tok(TOK_BAR, 0, start, (start + 1), line, col);
}
  if (c == 94) {
  return flowc_make_tok(TOK_CARET, 0, start, (start + 1), line, col);
}
  return flowc_make_tok(TOK_ERROR, 0, start, (start + 1), line, col);
}

int32_t flowc_token_is_kw(Token tok, int32_t kw) {
  if ((tok).kind == TOK_KEYWORD && (tok).kw == kw) {
  return 1;
}
  return 0;
}


typedef struct AstNode {
  int32_t kind;
  int32_t start;
  int32_t end;
  int32_t a;
  int32_t b;
  int32_t c;
  int32_t next;
  int32_t ival;
  int32_t name_start;
  int32_t name_end;
} AstNode;

typedef struct AstArena {
  AstNode* nodes;
  int32_t len;
  int32_t cap;
} AstArena;

const int32_t AST_NONE = (-1);
const int32_t AST_PROGRAM = 1;
const int32_t AST_FN = 2;
const int32_t AST_PARAM = 3;
const int32_t AST_BLOCK = 4;
const int32_t AST_LET = 5;
const int32_t AST_RETURN = 6;
const int32_t AST_IF = 7;
const int32_t AST_WHILE = 8;
const int32_t AST_BINOP = 9;
const int32_t AST_UNARY = 10;
const int32_t AST_CALL = 11;
const int32_t AST_IDENT = 12;
const int32_t AST_INT = 13;
const int32_t AST_TYPE = 14;
const int32_t AST_ASSIGN = 15;
const int32_t AST_EXPR_STMT = 16;
const int32_t AST_BOOL = 17;
const int32_t AST_ERROR = 18;
const int32_t AST_FOR = 19;
const int32_t AST_STRUCT = 20;
const int32_t AST_FIELD = 21;
const int32_t AST_EXTERN = 22;
const int32_t AST_IMPORT = 23;
const int32_t AST_EXPORT = 24;
const int32_t AST_FIELD_ACCESS = 25;
const int32_t AST_INDEX = 26;
const int32_t AST_STRUCT_LIT = 27;
const int32_t AST_BREAK = 28;
const int32_t AST_CONTINUE = 29;
const int32_t AST_STRING = 30;
const int32_t AST_CONST = 31;
const int32_t AST_CAST = 32;
const int32_t AST_ARRAY_LIT = 33;
const int32_t AST_FLOAT = 34;
const int32_t AST_MATCH = 35;
const int32_t AST_MATCH_ARM = 36;
const int32_t AST_TYPE_ALIAS = 37;
const int32_t AST_EXTERN_TYPE = 38;
const int32_t AST_C_INCLUDE = 39;
const int32_t AST_C_EMBED = 40;
const int32_t AST_C_IMPORT = 41;
AstArena flowc_ast_new(int32_t cap) {
  int64_t size = ((int64_t)(cap) * 40);
  uint8_t* raw = (uint8_t*)(malloc(size));
  AstNode* nodes = (AstNode*)(raw);
  int32_t i = 0;
  while (i < cap) {
  (nodes[i]).kind = 0;
  (nodes[i]).start = 0;
  (nodes[i]).end = 0;
  (nodes[i]).a = AST_NONE;
  (nodes[i]).b = AST_NONE;
  (nodes[i]).c = AST_NONE;
  (nodes[i]).next = AST_NONE;
  (nodes[i]).ival = 0;
  (nodes[i]).name_start = 0;
  (nodes[i]).name_end = 0;
  i = (i + 1);
}
  return (AstArena){ .nodes = nodes, .len = 0, .cap = cap };
}

void flowc_ast_free(AstArena arena) {
  uint8_t* raw = (uint8_t*)((arena).nodes);
  free(raw);
}

int32_t flowc_ast_alloc(AstArena* arena, int32_t kind, int32_t start, int32_t end) {
  if ((arena[0]).len >= (arena[0]).cap) {
  return AST_NONE;
}
  int32_t id = (arena[0]).len;
  (arena[0]).len = (id + 1);
  ((arena[0]).nodes[id]).kind = kind;
  ((arena[0]).nodes[id]).start = start;
  ((arena[0]).nodes[id]).end = end;
  ((arena[0]).nodes[id]).a = AST_NONE;
  ((arena[0]).nodes[id]).b = AST_NONE;
  ((arena[0]).nodes[id]).c = AST_NONE;
  ((arena[0]).nodes[id]).next = AST_NONE;
  ((arena[0]).nodes[id]).ival = 0;
  ((arena[0]).nodes[id]).name_start = 0;
  ((arena[0]).nodes[id]).name_end = 0;
  return id;
}

int32_t flowc_ast_count_kind(AstArena arena, int32_t kind) {
  int32_t n = 0;
  int32_t i = 0;
  while (i < (arena).len) {
  if (((arena).nodes[i]).kind == kind) {
  n = (n + 1);
}
  i = (i + 1);
}
  return n;
}

int32_t flowc_ast_chain_push(AstArena* arena, int32_t head, int32_t node) {
  if (head == AST_NONE) {
  return node;
}
  int32_t cur = head;
  while (((arena[0]).nodes[cur]).next != AST_NONE) {
  cur = ((arena[0]).nodes[cur]).next;
}
  ((arena[0]).nodes[cur]).next = node;
  return head;
}

int32_t flowc_ast_chain_len(AstArena arena, int32_t head) {
  int32_t n = 0;
  int32_t cur = head;
  while (cur != AST_NONE) {
  n = (n + 1);
  cur = ((arena).nodes[cur]).next;
}
  return n;
}


typedef struct Parser {
  Lexer lex;
  Token cur;
  AstArena arena;
  int32_t err;
} Parser;

Parser flowc_parser_new(uint8_t* input, int32_t len, int32_t ast_cap) {
  Lexer lex = flowc_lexer_new(input, len);
  Token cur = flowc_lexer_next((&lex));
  AstArena arena = flowc_ast_new(ast_cap);
  return (Parser){ .lex = lex, .cur = cur, .arena = arena, .err = 0 };
}

void flowc_parser_free(Parser p) {
  flowc_ast_free((p).arena);
}

void flowc_parser_advance(Parser* p) {
  (p[0]).cur = flowc_lexer_next((&(p[0]).lex));
}

int32_t flowc_parser_check(Parser p, int32_t kind) {
  if (((p).cur).kind == kind) {
  return 1;
}
  return 0;
}

int32_t flowc_parser_check_kw(Parser p, int32_t kw) {
  return flowc_token_is_kw((p).cur, kw);
}

int32_t flowc_cgen_span_is(uint8_t* src, int32_t start, int32_t end, const char* lit);
int32_t flowc_parser_span_is(Parser p, int32_t start, int32_t end, const char* lit) {
  return flowc_cgen_span_is((p).lex.input, start, end, lit);
}

int32_t flowc_parser_eat(Parser* p, int32_t kind) {
  if (((p[0]).cur).kind == kind) {
  flowc_parser_advance(p);
  return 1;
}
  (p[0]).err = 1;
  return 0;
}

int32_t flowc_parser_eat_kw(Parser* p, int32_t kw) {
  if (flowc_token_is_kw((p[0]).cur, kw) == 1) {
  flowc_parser_advance(p);
  return 1;
}
  (p[0]).err = 1;
  return 0;
}

int32_t flowc_parse_int_span(uint8_t* src, int32_t start, int32_t end) {
  if ((end - start) >= 2 && src[start] == 48 && src[(start + 1)] == 120 || src[(start + 1)] == 88) {
  int32_t v = 0;
  int32_t i = (start + 2);
  while (i < end) {
  int32_t c = src[i];
  if (c >= 48 && c <= 57) {
  v = ((v * 16) + (c - 48));
} else {
  if (c >= 97 && c <= 102) {
  v = ((v * 16) + (c - 87));
} else {
  if (c >= 65 && c <= 70) {
  v = ((v * 16) + (c - 55));
}
}
}
  i = (i + 1);
}
  return v;
}
  int32_t v = 0;
  int32_t i = start;
  while (i < end) {
  int32_t c = src[i];
  if (c < 48 || c > 57) {
  return v;
}
  v = ((v * 10) + (c - 48));
  i = (i + 1);
}
  return v;
}

int32_t flowc_parser_eat_gt(Parser* p) {
  if (flowc_parser_check(p[0], TOK_GT) == 1) {
  flowc_parser_advance(p);
  return 1;
}
  if (flowc_parser_check(p[0], TOK_SHR) == 1) {
  Token t = (p[0]).cur;
  ((p[0]).cur).kind = TOK_GT;
  ((p[0]).cur).start = ((t).start + 1);
  ((p[0]).cur).end = (t).end;
  return 1;
}
  (p[0]).err = 1;
  return 0;
}

int32_t flowc_parse_type(Parser* p) {
  if (flowc_parser_check(p[0], TOK_AMP) == 1) {
  flowc_parser_advance(p);
  return flowc_parse_type(p);
}
  if (flowc_parser_check(p[0], TOK_LBRACK) == 1) {
  int32_t start = ((p[0]).cur).start;
  flowc_parser_advance(p);
  int32_t inner = flowc_parse_type(p);
  if (inner == AST_NONE) {
  return AST_NONE;
}
  if (flowc_parser_eat(p, TOK_RBRACK) == 0) {
  return AST_NONE;
}
  int32_t id = flowc_ast_alloc((&(p[0]).arena), AST_TYPE, start, ((p[0]).cur).start);
  if (id == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[id]).a = inner;
  return id;
}
  if (flowc_parser_check(p[0], TOK_LPAREN) == 1) {
  int32_t start = ((p[0]).cur).start;
  flowc_parser_advance(p);
  int32_t params = AST_NONE;
  if (flowc_parser_check(p[0], TOK_RPAREN) == 0) {
  int32_t loop = 1;
  while (loop == 1) {
  int32_t pt = flowc_parse_type(p);
  if (pt == AST_NONE) {
  return AST_NONE;
}
  params = flowc_ast_chain_push((&(p[0]).arena), params, pt);
  if (flowc_parser_check(p[0], TOK_COMMA) == 1) {
  flowc_parser_advance(p);
} else {
  loop = 0;
}
}
}
  if (flowc_parser_eat(p, TOK_RPAREN) == 0) {
  return AST_NONE;
}
  if (flowc_parser_eat(p, TOK_ARROW) == 0) {
  return AST_NONE;
}
  int32_t ret = flowc_parse_type(p);
  if (ret == AST_NONE) {
  return AST_NONE;
}
  int32_t id = flowc_ast_alloc((&(p[0]).arena), AST_TYPE, start, ((p[0]).cur).start);
  if (id == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[id]).ival = (0 - 1);
  (((p[0]).arena).nodes[id]).a = params;
  (((p[0]).arena).nodes[id]).b = ret;
  return id;
}
  if (flowc_parser_check(p[0], TOK_IDENT) == 0) {
  (p[0]).err = 1;
  return AST_NONE;
}
  int32_t start = ((p[0]).cur).start;
  int32_t end = ((p[0]).cur).end;
  int32_t id = flowc_ast_alloc((&(p[0]).arena), AST_TYPE, start, end);
  if (id == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[id]).name_start = start;
  (((p[0]).arena).nodes[id]).name_end = end;
  flowc_parser_advance(p);
  if (flowc_parser_span_is(p[0], start, end, "cfn") == 1 && flowc_parser_check(p[0], TOK_LPAREN) == 1) {
  flowc_parser_advance(p);
  int32_t params2 = AST_NONE;
  if (flowc_parser_check(p[0], TOK_RPAREN) == 0) {
  int32_t loop2 = 1;
  while (loop2 == 1) {
  int32_t pt2 = flowc_parse_type(p);
  if (pt2 == AST_NONE) { return AST_NONE; }
  params2 = flowc_ast_chain_push((&(p[0]).arena), params2, pt2);
  if (flowc_parser_check(p[0], TOK_COMMA) == 1) {
  flowc_parser_advance(p);
} else { loop2 = 0; }
}
}
  if (flowc_parser_eat(p, TOK_RPAREN) == 0) { return AST_NONE; }
  if (flowc_parser_eat(p, TOK_ARROW) == 0) { return AST_NONE; }
  int32_t ret2 = flowc_parse_type(p);
  if (ret2 == AST_NONE) { return AST_NONE; }
  (((p[0]).arena).nodes[id]).ival = (0 - 2);
  (((p[0]).arena).nodes[id]).a = params2;
  (((p[0]).arena).nodes[id]).b = ret2;
  return id;
}
  if (flowc_parser_check(p[0], TOK_LT) == 1) {
  flowc_parser_advance(p);
  int32_t inner = flowc_parse_type(p);
  if (inner == AST_NONE) {
  return AST_NONE;
}
  (((p[0]).arena).nodes[id]).a = inner;
  if (flowc_parser_check(p[0], TOK_COMMA) == 1) {
  flowc_parser_advance(p);
  if (flowc_parser_check(p[0], TOK_INT) == 0) {
  (p[0]).err = 1;
  return AST_NONE;
}
  int32_t n = flowc_parse_int_span(((p[0]).lex).input, ((p[0]).cur).start, ((p[0]).cur).end);
  (((p[0]).arena).nodes[id]).ival = n;
  flowc_parser_advance(p);
}
  if (flowc_parser_eat_gt(p) == 0) {
  return AST_NONE;
}
  (((p[0]).arena).nodes[id]).end = ((p[0]).cur).start;
}
  return id;
}

int32_t flowc_parse_expr(Parser* p);
int32_t flowc_parse_atom(Parser* p) {
  Token tok = (p[0]).cur;
  if ((tok).kind == TOK_INT) {
  int32_t id = flowc_ast_alloc((&(p[0]).arena), AST_INT, (tok).start, (tok).end);
  if (id == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[id]).ival = flowc_parse_int_span(((p[0]).lex).input, (tok).start, (tok).end);
  flowc_parser_advance(p);
  return id;
}
  if ((tok).kind == TOK_FLOAT) {
  int32_t id = flowc_ast_alloc((&(p[0]).arena), AST_FLOAT, (tok).start, (tok).end);
  if (id == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[id]).name_start = (tok).start;
  (((p[0]).arena).nodes[id]).name_end = (tok).end;
  flowc_parser_advance(p);
  return id;
}
  if ((tok).kind == TOK_STRING) {
  int32_t id = flowc_ast_alloc((&(p[0]).arena), AST_STRING, (tok).start, (tok).end);
  if (id == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[id]).name_start = (tok).start;
  (((p[0]).arena).nodes[id]).name_end = (tok).end;
  flowc_parser_advance(p);
  return id;
}
  if (flowc_token_is_kw(tok, KW_TRUE) == 1 || flowc_token_is_kw(tok, KW_FALSE) == 1) {
  int32_t id = flowc_ast_alloc((&(p[0]).arena), AST_BOOL, (tok).start, (tok).end);
  if (id == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  if (flowc_token_is_kw(tok, KW_TRUE) == 1) {
  (((p[0]).arena).nodes[id]).ival = 1;
} else {
  (((p[0]).arena).nodes[id]).ival = 0;
}
  flowc_parser_advance(p);
  return id;
}
  if (flowc_token_is_kw(tok, KW_NULL) == 1) {
  int32_t id = flowc_ast_alloc((&(p[0]).arena), AST_IDENT, (tok).start, (tok).end);
  if (id == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[id]).name_start = (tok).start;
  (((p[0]).arena).nodes[id]).name_end = (tok).end;
  flowc_parser_advance(p);
  return id;
}
  if ((tok).kind == TOK_IDENT) {
  int32_t name_s = (tok).start;
  int32_t name_e = (tok).end;
  flowc_parser_advance(p);
  if (flowc_parser_check(p[0], TOK_LPAREN) == 1) {
  flowc_parser_advance(p);
  int32_t args = AST_NONE;
  if (flowc_parser_check(p[0], TOK_RPAREN) == 0) {
  int32_t first = flowc_parse_expr(p);
  args = flowc_ast_chain_push((&(p[0]).arena), args, first);
  while (flowc_parser_check(p[0], TOK_COMMA) == 1) {
  flowc_parser_advance(p);
  int32_t arg = flowc_parse_expr(p);
  args = flowc_ast_chain_push((&(p[0]).arena), args, arg);
}
}
  if (flowc_parser_eat(p, TOK_RPAREN) == 0) {
  return AST_NONE;
}
  int32_t call = flowc_ast_alloc((&(p[0]).arena), AST_CALL, name_s, ((p[0]).cur).start);
  if (call == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[call]).name_start = name_s;
  (((p[0]).arena).nodes[call]).name_end = name_e;
  (((p[0]).arena).nodes[call]).a = args;
  return call;
}
  if (flowc_parser_check(p[0], TOK_LT) == 1) {
  Lexer saved_lex = (p[0]).lex;
  Token saved_cur = (p[0]).cur;
  flowc_parser_advance(p);
  int32_t depth = 1;
  int32_t ok = 1;
  while (depth > 0 && ok == 1 && flowc_parser_check(p[0], TOK_EOF) == 0) {
  if (flowc_parser_check(p[0], TOK_LT) == 1) {
  depth = (depth + 1);
  flowc_parser_advance(p);
} else {
  if (flowc_parser_check(p[0], TOK_GT) == 1) {
  depth = (depth - 1);
  flowc_parser_advance(p);
} else {
  if (flowc_parser_check(p[0], TOK_SHR) == 1) {
  depth = (depth - 2);
  flowc_parser_advance(p);
} else {
  if (flowc_parser_check(p[0], TOK_COMMA) == 1 || flowc_parser_check(p[0], TOK_IDENT) == 1 || flowc_parser_check(p[0], TOK_DOT) == 1) {
  flowc_parser_advance(p);
} else {
  ok = 0;
}
}
}
}
}
  if (ok == 1 && depth == 0) {
} else {
  (p[0]).lex = saved_lex;
  (p[0]).cur = saved_cur;
}
}
  if (flowc_parser_check(p[0], TOK_LBRACE) == 1) {
  Lexer saved_lex = (p[0]).lex;
  Token saved_cur = (p[0]).cur;
  flowc_parser_advance(p);
  int32_t is_lit = 0;
  if (flowc_parser_check(p[0], TOK_RBRACE) == 1) {
  is_lit = 1;
} else {
  if (flowc_parser_check(p[0], TOK_IDENT) == 1 || flowc_parser_check(p[0], TOK_KEYWORD) == 1) {
  flowc_parser_advance(p);
  if (flowc_parser_check(p[0], TOK_COLON) == 1) {
  is_lit = 1;
}
}
}
  if (is_lit == 0) {
  (p[0]).lex = saved_lex;
  (p[0]).cur = saved_cur;
} else {
  (p[0]).lex = saved_lex;
  (p[0]).cur = saved_cur;
  flowc_parser_advance(p);
  int32_t fields = AST_NONE;
  while (flowc_parser_check(p[0], TOK_RBRACE) == 0 && flowc_parser_check(p[0], TOK_EOF) == 0) {
  if (flowc_parser_check(p[0], TOK_IDENT) == 0 && flowc_parser_check(p[0], TOK_KEYWORD) == 0) {
  (p[0]).err = 1;
  return AST_NONE;
}
  int32_t fs = ((p[0]).cur).start;
  int32_t fe = ((p[0]).cur).end;
  flowc_parser_advance(p);
  if (flowc_parser_eat(p, TOK_COLON) == 0) {
  return AST_NONE;
}
  int32_t val = flowc_parse_expr(p);
  int32_t field = flowc_ast_alloc((&(p[0]).arena), AST_FIELD, fs, ((p[0]).cur).start);
  if (field == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[field]).name_start = fs;
  (((p[0]).arena).nodes[field]).name_end = fe;
  (((p[0]).arena).nodes[field]).a = val;
  fields = flowc_ast_chain_push((&(p[0]).arena), fields, field);
  if (flowc_parser_check(p[0], TOK_COMMA) == 1) {
  flowc_parser_advance(p);
} else {
  if (flowc_parser_check(p[0], TOK_RBRACE) == 0) {
  (p[0]).err = 1;
  return AST_NONE;
}
}
}
  if (flowc_parser_eat(p, TOK_RBRACE) == 0) {
  return AST_NONE;
}
  int32_t lit = flowc_ast_alloc((&(p[0]).arena), AST_STRUCT_LIT, name_s, ((p[0]).cur).start);
  if (lit == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[lit]).name_start = name_s;
  (((p[0]).arena).nodes[lit]).name_end = name_e;
  (((p[0]).arena).nodes[lit]).a = fields;
  return lit;
}
}
  int32_t id = flowc_ast_alloc((&(p[0]).arena), AST_IDENT, name_s, name_e);
  if (id == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[id]).name_start = name_s;
  (((p[0]).arena).nodes[id]).name_end = name_e;
  return id;
}
  if ((tok).kind == TOK_LPAREN) {
  flowc_parser_advance(p);
  int32_t inner = flowc_parse_expr(p);
  if (flowc_parser_eat(p, TOK_RPAREN) == 0) {
  return AST_NONE;
}
  return inner;
}
  if ((tok).kind == TOK_LBRACK) {
  int32_t start = (tok).start;
  flowc_parser_advance(p);
  int32_t elems = AST_NONE;
  if (flowc_parser_check(p[0], TOK_RBRACK) == 0) {
  int32_t first = flowc_parse_expr(p);
  elems = flowc_ast_chain_push((&(p[0]).arena), elems, first);
  while (flowc_parser_check(p[0], TOK_COMMA) == 1) {
  flowc_parser_advance(p);
  if (flowc_parser_check(p[0], TOK_RBRACK) == 1) {
  break;
}
  int32_t el = flowc_parse_expr(p);
  elems = flowc_ast_chain_push((&(p[0]).arena), elems, el);
}
}
  if (flowc_parser_eat(p, TOK_RBRACK) == 0) {
  return AST_NONE;
}
  int32_t id = flowc_ast_alloc((&(p[0]).arena), AST_ARRAY_LIT, start, ((p[0]).cur).start);
  if (id == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[id]).a = elems;
  return id;
}
  (p[0]).err = 1;
  return AST_NONE;
}

int32_t flowc_parse_postfix(Parser* p) {
  int32_t base = flowc_parse_atom(p);
  if (base == AST_NONE) {
  return AST_NONE;
}
  while (1 == 1) {
  if (flowc_parser_check(p[0], TOK_DOT) == 1) {
  flowc_parser_advance(p);
  if (flowc_parser_check(p[0], TOK_IDENT) == 0) {
  (p[0]).err = 1;
  return AST_NONE;
}
  int32_t fs = ((p[0]).cur).start;
  int32_t fe = ((p[0]).cur).end;
  flowc_parser_advance(p);
  int32_t id = flowc_ast_alloc((&(p[0]).arena), AST_FIELD_ACCESS, 0, 0);
  if (id == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[id]).a = base;
  (((p[0]).arena).nodes[id]).name_start = fs;
  (((p[0]).arena).nodes[id]).name_end = fe;
  base = id;
} else {
  if (flowc_parser_check(p[0], TOK_LBRACK) == 1) {
  flowc_parser_advance(p);
  int32_t idx = flowc_parse_expr(p);
  if (flowc_parser_eat(p, TOK_RBRACK) == 0) {
  return AST_NONE;
}
  int32_t id = flowc_ast_alloc((&(p[0]).arena), AST_INDEX, 0, 0);
  if (id == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[id]).a = base;
  (((p[0]).arena).nodes[id]).b = idx;
  base = id;
} else {
  if (flowc_parser_check(p[0], TOK_LPAREN) == 1) {
  int32_t call_start = ((p[0]).cur).start;
  flowc_parser_advance(p);
  int32_t args = AST_NONE;
  if (flowc_parser_check(p[0], TOK_RPAREN) == 0) {
  int32_t loop = 1;
  while (loop == 1) {
  int32_t arg = flowc_parse_expr(p);
  if (arg == AST_NONE) {
  return AST_NONE;
}
  args = flowc_ast_chain_push((&(p[0]).arena), args, arg);
  if (flowc_parser_check(p[0], TOK_COMMA) == 1) {
  flowc_parser_advance(p);
} else {
  loop = 0;
}
}
}
  if (flowc_parser_eat(p, TOK_RPAREN) == 0) {
  return AST_NONE;
}
  int32_t id = flowc_ast_alloc((&(p[0]).arena), AST_CALL, call_start, ((p[0]).cur).start);
  if (id == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[id]).a = args;
  (((p[0]).arena).nodes[id]).name_start = (((p[0]).arena).nodes[base]).name_start;
  (((p[0]).arena).nodes[id]).name_end = (((p[0]).arena).nodes[base]).name_end;
  base = id;
} else {
  return base;
}
}
}
}
  return base;
}

int32_t flowc_parse_primary(Parser* p) {
  Token tok = (p[0]).cur;
  if ((tok).kind == TOK_BANG || (tok).kind == TOK_MINUS || (tok).kind == TOK_AMP || (tok).kind == TOK_TILDE) {
  int32_t op = (tok).kind;
  int32_t start = (tok).start;
  flowc_parser_advance(p);
  int32_t operand = flowc_parse_primary(p);
  int32_t id = flowc_ast_alloc((&(p[0]).arena), AST_UNARY, start, ((p[0]).cur).start);
  if (id == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[id]).ival = op;
  (((p[0]).arena).nodes[id]).a = operand;
  return id;
}
  if ((tok).kind == TOK_KEYWORD && (tok).kw == KW_NOT) {
  int32_t start = (tok).start;
  flowc_parser_advance(p);
  int32_t operand = flowc_parse_primary(p);
  int32_t id = flowc_ast_alloc((&(p[0]).arena), AST_UNARY, start, ((p[0]).cur).start);
  if (id == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[id]).ival = TOK_BANG;
  (((p[0]).arena).nodes[id]).a = operand;
  return id;
}
  return flowc_parse_postfix(p);
}

int32_t flowc_parse_cast(Parser* p) {
  int32_t base = flowc_parse_primary(p);
  if (base == AST_NONE) {
  return AST_NONE;
}
  while (flowc_parser_check_kw(p[0], KW_AS) == 1) {
  flowc_parser_advance(p);
  int32_t ty = flowc_parse_type(p);
  if (ty == AST_NONE) {
  return AST_NONE;
}
  int32_t id = flowc_ast_alloc((&(p[0]).arena), AST_CAST, 0, 0);
  if (id == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[id]).a = base;
  (((p[0]).arena).nodes[id]).b = ty;
  base = id;
}
  return base;
}

int32_t flowc_parse_binop_kind(Parser p) {
  int32_t op = ((p).cur).kind;
  if (op == TOK_BARBAR) {
  return TOK_BARBAR;
}
  if (op == TOK_AMPAMP) {
  return TOK_AMPAMP;
}
  if (op == TOK_AMP) {
  return TOK_AMP;
}
  if (op == TOK_BAR) {
  return TOK_BAR;
}
  if (op == TOK_CARET) {
  return TOK_CARET;
}
  if (op == TOK_SHL) {
  return TOK_SHL;
}
  if (op == TOK_SHR) {
  return TOK_SHR;
}
  if (op == TOK_EQEQ) {
  return TOK_EQEQ;
}
  if (op == TOK_NE) {
  return TOK_NE;
}
  if (op == TOK_LT) {
  return TOK_LT;
}
  if (op == TOK_LE) {
  return TOK_LE;
}
  if (op == TOK_GT) {
  return TOK_GT;
}
  if (op == TOK_GE) {
  return TOK_GE;
}
  if (op == TOK_PLUS) {
  return TOK_PLUS;
}
  if (op == TOK_MINUS) {
  return TOK_MINUS;
}
  if (op == TOK_STAR) {
  return TOK_STAR;
}
  if (op == TOK_SLASH) {
  return TOK_SLASH;
}
  if (op == TOK_PERCENT) {
  return TOK_PERCENT;
}
  if (op == TOK_KEYWORD) {
  if (((p).cur).kw == KW_OR) {
  return TOK_BARBAR;
}
  if (((p).cur).kw == KW_AND) {
  return TOK_AMPAMP;
}
}
  return (0 - 1);
}

int32_t flowc_parse_binop_prec(int32_t op) {
  if (op == TOK_BARBAR) {
  return 1;
}
  if (op == TOK_AMPAMP) {
  return 2;
}
  if (op == TOK_AMP) {
  return 3;
}
  if (op == TOK_BAR) {
  return 3;
}
  if (op == TOK_CARET) {
  return 3;
}
  if (op == TOK_SHL) {
  return 3;
}
  if (op == TOK_SHR) {
  return 3;
}
  if (op == TOK_EQEQ || op == TOK_NE) {
  return 4;
}
  if (op == TOK_LT || op == TOK_LE || op == TOK_GT || op == TOK_GE) {
  return 5;
}
  if (op == TOK_PLUS || op == TOK_MINUS) {
  return 6;
}
  if (op == TOK_STAR || op == TOK_SLASH || op == TOK_PERCENT) {
  return 7;
}
  return (0 - 1);
}

int32_t flowc_parse_binop_rhs(Parser* p, int32_t min_prec, int32_t lhs) {
  int32_t left = lhs;
  while (1 == 1) {
  int32_t op = flowc_parse_binop_kind(p[0]);
  int32_t prec = flowc_parse_binop_prec(op);
  if (prec < min_prec) {
  return left;
}
  flowc_parser_advance(p);
  int32_t right = flowc_parse_cast(p);
  while (1 == 1) {
  int32_t next = flowc_parse_binop_kind(p[0]);
  int32_t next_prec = flowc_parse_binop_prec(next);
  if (next_prec <= prec) {
  break;
}
  right = flowc_parse_binop_rhs(p, (prec + 1), right);
}
  int32_t node = flowc_ast_alloc((&(p[0]).arena), AST_BINOP, 0, 0);
  if (node == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[node]).ival = op;
  (((p[0]).arena).nodes[node]).a = left;
  (((p[0]).arena).nodes[node]).b = right;
  left = node;
}
  return left;
}

int32_t flowc_parse_expr(Parser* p) {
  int32_t lhs = flowc_parse_cast(p);
  if (lhs == AST_NONE) {
  return AST_NONE;
}
  return flowc_parse_binop_rhs(p, 1, lhs);
}

int32_t flowc_parse_block(Parser* p);
void flowc_parser_skip_brace_block(Parser* p);
void flowc_parser_skip_paren_block(Parser* p);
int32_t flowc_parse_if_chain(Parser* p, int32_t start) {
  flowc_parser_advance(p);
  int32_t elif_cond = flowc_parse_expr(p);
  int32_t elif_then = flowc_parse_block(p);
  int32_t elif_else = AST_NONE;
  if (flowc_parser_check_kw(p[0], KW_ELIF) == 1) {
  int32_t nested = flowc_parse_if_chain(p, start);
  if (nested == AST_NONE) {
  return AST_NONE;
}
  int32_t eb2 = flowc_ast_alloc((&(p[0]).arena), AST_BLOCK, start, ((p[0]).cur).start);
  if (eb2 == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[eb2]).a = flowc_ast_chain_push((&(p[0]).arena), AST_NONE, nested);
  elif_else = eb2;
} else {
  if (flowc_parser_check_kw(p[0], KW_ELSE) == 1) {
  flowc_parser_advance(p);
  elif_else = flowc_parse_block(p);
}
}
  int32_t elif_id = flowc_ast_alloc((&(p[0]).arena), AST_IF, start, ((p[0]).cur).start);
  if (elif_id == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[elif_id]).a = elif_cond;
  (((p[0]).arena).nodes[elif_id]).b = elif_then;
  (((p[0]).arena).nodes[elif_id]).c = elif_else;
  return elif_id;
}

int32_t flowc_parse_stmt(Parser* p) {
  while (flowc_parser_check(p[0], TOK_AT) == 1) {
  flowc_parser_advance(p);
  if (flowc_parser_check(p[0], TOK_IDENT) == 1) {
  flowc_parser_advance(p);
}
  if (flowc_parser_check(p[0], TOK_LPAREN) == 1) {
  flowc_parser_skip_paren_block(p);
}
}
  if (flowc_parser_check_kw(p[0], KW_LET) == 1) {
  int32_t start = ((p[0]).cur).start;
  flowc_parser_advance(p);
  int32_t is_mut = 0;
  if (flowc_parser_check_kw(p[0], KW_MUT) == 1) {
  is_mut = 1;
  flowc_parser_advance(p);
}
  if (flowc_parser_check(p[0], TOK_IDENT) == 0 && flowc_parser_check(p[0], TOK_KEYWORD) == 0) {
  (p[0]).err = 1;
  return AST_NONE;
}
  int32_t ns = ((p[0]).cur).start;
  int32_t ne = ((p[0]).cur).end;
  flowc_parser_advance(p);
  int32_t ty = AST_NONE;
  if (flowc_parser_check(p[0], TOK_COLON) == 1) {
  flowc_parser_advance(p);
  ty = flowc_parse_type(p);
}
  if (flowc_parser_eat(p, TOK_EQ) == 0) {
  return AST_NONE;
}
  int32_t init = flowc_parse_expr(p);
  int32_t id = flowc_ast_alloc((&(p[0]).arena), AST_LET, start, ((p[0]).cur).start);
  if (id == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[id]).name_start = ns;
  (((p[0]).arena).nodes[id]).name_end = ne;
  (((p[0]).arena).nodes[id]).ival = is_mut;
  (((p[0]).arena).nodes[id]).a = ty;
  (((p[0]).arena).nodes[id]).b = init;
  return id;
}
  if (flowc_parser_check_kw(p[0], KW_RETURN) == 1) {
  int32_t start = ((p[0]).cur).start;
  flowc_parser_advance(p);
  int32_t val = AST_NONE;
  int32_t k = ((p[0]).cur).kind;
  int32_t is_expr = 0;
  if (k == TOK_INT || k == TOK_FLOAT || k == TOK_STRING || k == TOK_IDENT || k == TOK_LPAREN || k == TOK_LBRACK) {
  is_expr = 1;
}
  if (k == TOK_BANG || k == TOK_MINUS || k == TOK_AMP || k == TOK_TILDE) {
  is_expr = 1;
}
  if (flowc_token_is_kw((p[0]).cur, KW_TRUE) == 1 || flowc_token_is_kw((p[0]).cur, KW_FALSE) == 1) {
  is_expr = 1;
}
  if (flowc_token_is_kw((p[0]).cur, KW_NULL) == 1) {
  is_expr = 1;
}
  if (is_expr == 1) {
  val = flowc_parse_expr(p);
}
  int32_t id = flowc_ast_alloc((&(p[0]).arena), AST_RETURN, start, ((p[0]).cur).start);
  if (id == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[id]).a = val;
  return id;
}
  if (flowc_parser_check_kw(p[0], KW_IF) == 1) {
  int32_t start = ((p[0]).cur).start;
  flowc_parser_advance(p);
  int32_t cond = flowc_parse_expr(p);
  int32_t then_b = flowc_parse_block(p);
  int32_t else_b = AST_NONE;
  if (flowc_parser_check_kw(p[0], KW_ELIF) == 1) {
  flowc_parser_advance(p);
  int32_t elif_cond = flowc_parse_expr(p);
  int32_t elif_then = flowc_parse_block(p);
  int32_t elif_else = AST_NONE;
  if (flowc_parser_check_kw(p[0], KW_ELIF) == 1) {
  int32_t nested = flowc_parse_if_chain(p, start);
  if (nested == AST_NONE) {
  return AST_NONE;
}
  int32_t eb2 = flowc_ast_alloc((&(p[0]).arena), AST_BLOCK, start, ((p[0]).cur).start);
  if (eb2 == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[eb2]).a = flowc_ast_chain_push((&(p[0]).arena), AST_NONE, nested);
  elif_else = eb2;
} else {
  if (flowc_parser_check_kw(p[0], KW_ELSE) == 1) {
  flowc_parser_advance(p);
  elif_else = flowc_parse_block(p);
}
}
  int32_t elif_id = flowc_ast_alloc((&(p[0]).arena), AST_IF, start, ((p[0]).cur).start);
  if (elif_id == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[elif_id]).a = elif_cond;
  (((p[0]).arena).nodes[elif_id]).b = elif_then;
  (((p[0]).arena).nodes[elif_id]).c = elif_else;
  int32_t eb = flowc_ast_alloc((&(p[0]).arena), AST_BLOCK, start, ((p[0]).cur).start);
  if (eb == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[eb]).a = flowc_ast_chain_push((&(p[0]).arena), AST_NONE, elif_id);
  else_b = eb;
} else {
  if (flowc_parser_check_kw(p[0], KW_ELSE) == 1) {
  flowc_parser_advance(p);
  else_b = flowc_parse_block(p);
}
}
  int32_t id = flowc_ast_alloc((&(p[0]).arena), AST_IF, start, ((p[0]).cur).start);
  if (id == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[id]).a = cond;
  (((p[0]).arena).nodes[id]).b = then_b;
  (((p[0]).arena).nodes[id]).c = else_b;
  return id;
}
  if (flowc_parser_check_kw(p[0], KW_WHILE) == 1) {
  int32_t start = ((p[0]).cur).start;
  flowc_parser_advance(p);
  int32_t cond = flowc_parse_expr(p);
  int32_t body = flowc_parse_block(p);
  int32_t id = flowc_ast_alloc((&(p[0]).arena), AST_WHILE, start, ((p[0]).cur).start);
  if (id == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[id]).a = cond;
  (((p[0]).arena).nodes[id]).b = body;
  return id;
}
  if (flowc_parser_check_kw(p[0], KW_FOR) == 1) {
  int32_t start = ((p[0]).cur).start;
  flowc_parser_advance(p);
  if (flowc_parser_check(p[0], TOK_IDENT) == 0) {
  (p[0]).err = 1;
  return AST_NONE;
}
  int32_t ns = ((p[0]).cur).start;
  int32_t ne = ((p[0]).cur).end;
  flowc_parser_advance(p);
  if (flowc_parser_eat_kw(p, KW_IN) == 0) {
  return AST_NONE;
}
  int32_t lo = flowc_parse_expr(p);
  int32_t got_range = 0;
  if (flowc_parser_check_kw(p[0], KW_TO) == 1) {
  flowc_parser_advance(p);
  got_range = 1;
} else {
  if (flowc_parser_check(p[0], TOK_DOTDOT) == 1) {
  flowc_parser_advance(p);
  got_range = 1;
}
}
  if (got_range == 0) {
  return AST_NONE;
}
  int32_t hi = flowc_parse_expr(p);
  int32_t body = flowc_parse_block(p);
  int32_t id = flowc_ast_alloc((&(p[0]).arena), AST_FOR, start, ((p[0]).cur).start);
  if (id == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[id]).name_start = ns;
  (((p[0]).arena).nodes[id]).name_end = ne;
  (((p[0]).arena).nodes[id]).a = lo;
  (((p[0]).arena).nodes[id]).b = hi;
  (((p[0]).arena).nodes[id]).c = body;
  return id;
}
  if (flowc_parser_check_kw(p[0], KW_MATCH) == 1) {
  int32_t start = ((p[0]).cur).start;
  flowc_parser_advance(p);
  int32_t scrut = flowc_parse_expr(p);
  if (scrut == AST_NONE) {
  return AST_NONE;
}
  if (flowc_parser_eat(p, TOK_LBRACE) == 0) {
  return AST_NONE;
}
  int32_t arms = AST_NONE;
  while (flowc_parser_check(p[0], TOK_RBRACE) == 0 && flowc_parser_check(p[0], TOK_EOF) == 0) {
  int32_t arm_start = ((p[0]).cur).start;
  int32_t pat_kind = 0;
  int32_t pat = AST_NONE;
  int32_t bind_s = 0;
  int32_t bind_e = 0;
  int32_t neg = 0;
  if (flowc_parser_check(p[0], TOK_MINUS) == 1) {
  neg = 1;
  flowc_parser_advance(p);
}
  if (flowc_parser_check(p[0], TOK_INT) == 1) {
  Token tok = (p[0]).cur;
  pat = flowc_ast_alloc((&(p[0]).arena), AST_INT, (tok).start, (tok).end);
  if (pat == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  int32_t v = flowc_parse_int_span(((p[0]).lex).input, (tok).start, (tok).end);
  if (neg == 1) {
  v = (0 - v);
}
  (((p[0]).arena).nodes[pat]).ival = v;
  flowc_parser_advance(p);
  pat_kind = 0;
} else {
  if (neg == 1 || flowc_parser_check(p[0], TOK_IDENT) == 0) {
  if (flowc_parser_check(p[0], TOK_LBRACK) == 1) {
  puts("flowc parse: list patterns not supported in Stage-A match");
} else {
  puts("flowc parse: unsupported match pattern (Stage-A: int literal, `_`, or binding ident)");
}
  (p[0]).err = 1;
  return AST_NONE;
}
  bind_s = ((p[0]).cur).start;
  bind_e = ((p[0]).cur).end;
  flowc_parser_advance(p);
  if (flowc_parser_check(p[0], TOK_LPAREN) == 1) {
  puts("flowc parse: struct patterns not supported in Stage-A match");
  (p[0]).err = 1;
  return AST_NONE;
}
  if ((bind_e - bind_s) == 1 && ((p[0]).lex).input[bind_s] == 95) {
  pat_kind = 1;
} else {
  pat_kind = 2;
}
}
  if (flowc_parser_check_kw(p[0], KW_IF) == 1) {
  puts("flowc parse: match guards not supported in Stage-A");
  (p[0]).err = 1;
  return AST_NONE;
}
  if (flowc_parser_check(p[0], TOK_FATARROW) == 0) {
  puts("flowc parse: expected => after match pattern (or/struct/list patterns unsupported in Stage-A)");
  (p[0]).err = 1;
  return AST_NONE;
}
  flowc_parser_advance(p);
  int32_t body = flowc_parse_block(p);
  if (body == AST_NONE) {
  return AST_NONE;
}
  int32_t arm = flowc_ast_alloc((&(p[0]).arena), AST_MATCH_ARM, arm_start, ((p[0]).cur).start);
  if (arm == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[arm]).ival = pat_kind;
  (((p[0]).arena).nodes[arm]).a = pat;
  (((p[0]).arena).nodes[arm]).b = body;
  (((p[0]).arena).nodes[arm]).name_start = bind_s;
  (((p[0]).arena).nodes[arm]).name_end = bind_e;
  arms = flowc_ast_chain_push((&(p[0]).arena), arms, arm);
  if (flowc_parser_check(p[0], TOK_COMMA) == 1) {
  flowc_parser_advance(p);
}
}
  if (flowc_parser_eat(p, TOK_RBRACE) == 0) {
  return AST_NONE;
}
  int32_t id = flowc_ast_alloc((&(p[0]).arena), AST_MATCH, start, ((p[0]).cur).start);
  if (id == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[id]).a = scrut;
  (((p[0]).arena).nodes[id]).b = arms;
  return id;
}
  if (flowc_parser_check_kw(p[0], KW_BREAK) == 1) {
  int32_t start = ((p[0]).cur).start;
  int32_t end = ((p[0]).cur).end;
  flowc_parser_advance(p);
  int32_t id = flowc_ast_alloc((&(p[0]).arena), AST_BREAK, start, end);
  if (id == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  return id;
}
  if (flowc_parser_check_kw(p[0], KW_CONTINUE) == 1) {
  int32_t start = ((p[0]).cur).start;
  int32_t end = ((p[0]).cur).end;
  flowc_parser_advance(p);
  int32_t id = flowc_ast_alloc((&(p[0]).arena), AST_CONTINUE, start, end);
  if (id == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  return id;
}
  if (flowc_parser_check(p[0], TOK_IDENT) == 1) {
  int32_t saved_start = ((p[0]).cur).start;
  int32_t expr = flowc_parse_expr(p);
  int32_t lk = (((p[0]).arena).nodes[expr]).kind;
  if (flowc_parser_check(p[0], TOK_EQ) == 1 && lk == AST_IDENT || lk == AST_FIELD_ACCESS || lk == AST_INDEX) {
  flowc_parser_advance(p);
  int32_t rhs = flowc_parse_expr(p);
  int32_t id = flowc_ast_alloc((&(p[0]).arena), AST_ASSIGN, saved_start, ((p[0]).cur).start);
  if (id == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[id]).a = expr;
  (((p[0]).arena).nodes[id]).b = rhs;
  return id;
}
  int32_t compound_op = 0;
  if (flowc_parser_check(p[0], TOK_PLUS_EQ) == 1) {
  compound_op = TOK_PLUS;
}
  if (flowc_parser_check(p[0], TOK_MINUS_EQ) == 1) {
  compound_op = TOK_MINUS;
}
  if (flowc_parser_check(p[0], TOK_STAR_EQ) == 1) {
  compound_op = TOK_STAR;
}
  if (flowc_parser_check(p[0], TOK_SLASH_EQ) == 1) {
  compound_op = TOK_SLASH;
}
  if (flowc_parser_check(p[0], TOK_PERCENT_EQ) == 1) {
  compound_op = TOK_PERCENT;
}
  if (compound_op != 0 && lk == AST_IDENT || lk == AST_FIELD_ACCESS || lk == AST_INDEX) {
  flowc_parser_advance(p);
  int32_t rhs = flowc_parse_expr(p);
  int32_t binop = flowc_ast_alloc((&(p[0]).arena), AST_BINOP, saved_start, ((p[0]).cur).start);
  if (binop == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[binop]).ival = compound_op;
  (((p[0]).arena).nodes[binop]).a = expr;
  (((p[0]).arena).nodes[binop]).b = rhs;
  int32_t id = flowc_ast_alloc((&(p[0]).arena), AST_ASSIGN, saved_start, ((p[0]).cur).start);
  if (id == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[id]).a = expr;
  (((p[0]).arena).nodes[id]).b = binop;
  return id;
}
  int32_t id = flowc_ast_alloc((&(p[0]).arena), AST_EXPR_STMT, saved_start, ((p[0]).cur).start);
  if (id == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[id]).a = expr;
  return id;
}
  (p[0]).err = 1;
  return AST_NONE;
}

int32_t flowc_parse_block(Parser* p) {
  int32_t start = ((p[0]).cur).start;
  if (flowc_parser_eat(p, TOK_LBRACE) == 0) {
  return AST_NONE;
}
  int32_t stmts = AST_NONE;
  while (flowc_parser_check(p[0], TOK_RBRACE) == 0 && flowc_parser_check(p[0], TOK_EOF) == 0) {
  if (flowc_parser_check(p[0], TOK_SEMI) == 1) {
  flowc_parser_advance(p);
} else {
  int32_t st = flowc_parse_stmt(p);
  if (st == AST_NONE) {
  return AST_NONE;
}
  stmts = flowc_ast_chain_push((&(p[0]).arena), stmts, st);
}
}
  if (flowc_parser_eat(p, TOK_RBRACE) == 0) {
  return AST_NONE;
}
  int32_t id = flowc_ast_alloc((&(p[0]).arena), AST_BLOCK, start, ((p[0]).cur).start);
  if (id == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[id]).a = stmts;
  return id;
}

int32_t flowc_parse_param(Parser* p) {
  if (flowc_parser_check(p[0], TOK_IDENT) == 0) {
  (p[0]).err = 1;
  return AST_NONE;
}
  int32_t ns = ((p[0]).cur).start;
  int32_t ne = ((p[0]).cur).end;
  flowc_parser_advance(p);
  if (flowc_parser_eat(p, TOK_COLON) == 0) {
  return AST_NONE;
}
  int32_t ty = flowc_parse_type(p);
  int32_t id = flowc_ast_alloc((&(p[0]).arena), AST_PARAM, ns, ((p[0]).cur).start);
  if (id == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[id]).name_start = ns;
  (((p[0]).arena).nodes[id]).name_end = ne;
  (((p[0]).arena).nodes[id]).a = ty;
  return id;
}

int32_t flowc_parse_function(Parser* p) {
  int32_t start = ((p[0]).cur).start;
  if (flowc_parser_eat_kw(p, KW_FUNCTION) == 0) {
  return AST_NONE;
}
  if (flowc_parser_check(p[0], TOK_IDENT) == 0) {
  (p[0]).err = 1;
  return AST_NONE;
}
  int32_t ns = ((p[0]).cur).start;
  int32_t ne = ((p[0]).cur).end;
  flowc_parser_advance(p);
  int32_t is_generic = 0;
  if (flowc_parser_check(p[0], TOK_LT) == 1) {
  is_generic = 1;
  flowc_parser_advance(p);
  int32_t depth = 1;
  while (depth > 0 && flowc_parser_check(p[0], TOK_EOF) == 0) {
  if (flowc_parser_check(p[0], TOK_LT) == 1) {
  depth = (depth + 1);
} else {
  if (flowc_parser_check(p[0], TOK_GT) == 1) {
  depth = (depth - 1);
} else {
  if (flowc_parser_check(p[0], TOK_SHR) == 1) {
  depth = (depth - 2);
}
}
}
  if (depth > 0) {
  flowc_parser_advance(p);
}
}
  if (flowc_parser_check(p[0], TOK_GT) == 1) {
  flowc_parser_advance(p);
} else {
  if (flowc_parser_check(p[0], TOK_SHR) == 1) {
  flowc_parser_advance(p);
}
}
}
  if (flowc_parser_eat(p, TOK_LPAREN) == 0) {
  return AST_NONE;
}
  int32_t params = AST_NONE;
  if (flowc_parser_check(p[0], TOK_RPAREN) == 0) {
  int32_t first = flowc_parse_param(p);
  params = flowc_ast_chain_push((&(p[0]).arena), params, first);
  while (flowc_parser_check(p[0], TOK_COMMA) == 1) {
  flowc_parser_advance(p);
  int32_t pr = flowc_parse_param(p);
  params = flowc_ast_chain_push((&(p[0]).arena), params, pr);
}
}
  if (flowc_parser_eat(p, TOK_RPAREN) == 0) {
  return AST_NONE;
}
  int32_t ret_ty = AST_NONE;
  if (flowc_parser_check(p[0], TOK_ARROW) == 1) {
  flowc_parser_advance(p);
  ret_ty = flowc_parse_type(p);
  if (ret_ty == AST_NONE) {
  return AST_NONE;
}
}
  int32_t body = AST_NONE;
  if (flowc_parser_check(p[0], TOK_LBRACE) == 1) {
  body = flowc_parse_block(p);
}
  int32_t id = flowc_ast_alloc((&(p[0]).arena), AST_FN, start, ((p[0]).cur).start);
  if (id == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[id]).name_start = ns;
  (((p[0]).arena).nodes[id]).name_end = ne;
  (((p[0]).arena).nodes[id]).a = params;
  (((p[0]).arena).nodes[id]).b = ret_ty;
  (((p[0]).arena).nodes[id]).c = body;
  (((p[0]).arena).nodes[id]).ival = is_generic;
  return id;
}

int32_t flowc_parse_struct(Parser* p) {
  int32_t start = ((p[0]).cur).start;
  if (flowc_parser_eat_kw(p, KW_STRUCT) == 0) {
  return AST_NONE;
}
  if (flowc_parser_check(p[0], TOK_IDENT) == 0) {
  (p[0]).err = 1;
  return AST_NONE;
}
  int32_t ns = ((p[0]).cur).start;
  int32_t ne = ((p[0]).cur).end;
  flowc_parser_advance(p);
  if (flowc_parser_check(p[0], TOK_LT) == 1) {
  flowc_parser_advance(p);
  int32_t depth = 1;
  while (depth > 0 && flowc_parser_check(p[0], TOK_EOF) == 0) {
  if (flowc_parser_check(p[0], TOK_LT) == 1) {
  depth = (depth + 1);
} else {
  if (flowc_parser_check(p[0], TOK_GT) == 1) {
  depth = (depth - 1);
} else {
  if (flowc_parser_check(p[0], TOK_SHR) == 1) {
  depth = (depth - 2);
}
}
}
  if (depth > 0) {
  flowc_parser_advance(p);
}
}
  if (flowc_parser_check(p[0], TOK_GT) == 1) {
  flowc_parser_advance(p);
} else {
  if (flowc_parser_check(p[0], TOK_SHR) == 1) {
  flowc_parser_advance(p);
}
}
}
  if (flowc_parser_eat(p, TOK_LBRACE) == 0) {
  return AST_NONE;
}
  int32_t fields = AST_NONE;
  while (flowc_parser_check(p[0], TOK_RBRACE) == 0 && flowc_parser_check(p[0], TOK_EOF) == 0) {
  if (flowc_parser_check(p[0], TOK_IDENT) == 0 && flowc_parser_check(p[0], TOK_KEYWORD) == 0) {
  (p[0]).err = 1;
  return AST_NONE;
}
  int32_t fs = ((p[0]).cur).start;
  int32_t fe = ((p[0]).cur).end;
  flowc_parser_advance(p);
  if (flowc_parser_eat(p, TOK_COLON) == 0) {
  return AST_NONE;
}
  int32_t ty = flowc_parse_type(p);
  int32_t field = flowc_ast_alloc((&(p[0]).arena), AST_FIELD, fs, ((p[0]).cur).start);
  if (field == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[field]).name_start = fs;
  (((p[0]).arena).nodes[field]).name_end = fe;
  (((p[0]).arena).nodes[field]).a = ty;
  fields = flowc_ast_chain_push((&(p[0]).arena), fields, field);
  if (flowc_parser_check(p[0], TOK_COMMA) == 1) {
  flowc_parser_advance(p);
} else {
  if (flowc_parser_check(p[0], TOK_RBRACE) == 0) {
  if (flowc_parser_check(p[0], TOK_IDENT) == 0) {
  (p[0]).err = 1;
  return AST_NONE;
}
}
}
}
  if (flowc_parser_eat(p, TOK_RBRACE) == 0) {
  return AST_NONE;
}
  int32_t id = flowc_ast_alloc((&(p[0]).arena), AST_STRUCT, start, ((p[0]).cur).start);
  if (id == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[id]).name_start = ns;
  (((p[0]).arena).nodes[id]).name_end = ne;
  (((p[0]).arena).nodes[id]).a = fields;
  return id;
}

int32_t flowc_parse_extern(Parser* p) {
  int32_t start = ((p[0]).cur).start;
  if (flowc_parser_eat_kw(p, KW_EXTERN) == 0) {
  return AST_NONE;
}
  if (flowc_parser_check(p[0], TOK_STRING) == 1) {
  flowc_parser_advance(p);
}
  if (flowc_parser_check_kw(p[0], KW_TYPE) == 1) {
  flowc_parser_advance(p);
  if (flowc_parser_check(p[0], TOK_IDENT) == 0) {
  (p[0]).err = 1;
  return AST_NONE;
}
  int32_t tns = ((p[0]).cur).start;
  int32_t tne = ((p[0]).cur).end;
  flowc_parser_advance(p);
  if (flowc_parser_check(p[0], TOK_SEMI) == 1) {
  flowc_parser_advance(p);
}
  int32_t tid = flowc_ast_alloc((&(p[0]).arena), AST_EXTERN_TYPE, tns, tne);
  if (tid == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  ((p[0]).arena).nodes[tid].name_start = tns;
  ((p[0]).arena).nodes[tid].name_end = tne;
  return tid;
}
  if (flowc_parser_check_kw(p[0], KW_FUNCTION) == 1) {
  flowc_parser_advance(p);
  if (flowc_parser_check(p[0], TOK_IDENT) == 1) {
  flowc_parser_advance(p);
}
  if (flowc_parser_check(p[0], TOK_LPAREN) == 1) {
  flowc_parser_skip_paren_block(p);
}
  if (flowc_parser_check(p[0], TOK_ARROW) == 1) {
  flowc_parser_advance(p);
  int32_t _skip_ty = flowc_parse_type(p);
}
  if (flowc_parser_check(p[0], TOK_SEMI) == 1) {
  flowc_parser_advance(p);
}
  int32_t id = flowc_ast_alloc((&(p[0]).arena), AST_EXTERN, start, ((p[0]).cur).start);
  if (id == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  return id;
}
  if (flowc_parser_eat(p, TOK_LBRACE) == 0) {
  return AST_NONE;
}
  int32_t fns = AST_NONE;
  while (flowc_parser_check(p[0], TOK_RBRACE) == 0 && flowc_parser_check(p[0], TOK_EOF) == 0) {
  if (flowc_parser_check_kw(p[0], KW_TYPE) == 1) {
  flowc_parser_advance(p);
  if (flowc_parser_check(p[0], TOK_IDENT) == 0) {
  (p[0]).err = 1;
  return AST_NONE;
}
  int32_t tns2 = ((p[0]).cur).start;
  int32_t tne2 = ((p[0]).cur).end;
  flowc_parser_advance(p);
  if (flowc_parser_check(p[0], TOK_SEMI) == 1) {
  flowc_parser_advance(p);
}
  int32_t tid2 = flowc_ast_alloc((&(p[0]).arena), AST_EXTERN_TYPE, tns2, tne2);
  if (tid2 == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  ((p[0]).arena).nodes[tid2].name_start = tns2;
  ((p[0]).arena).nodes[tid2].name_end = tne2;
  fns = flowc_ast_chain_push((&(p[0]).arena), fns, tid2);
  if (flowc_parser_check(p[0], TOK_COMMA) == 1) {
  flowc_parser_advance(p);
}
  continue;
}
  if (flowc_parser_check_kw(p[0], KW_FUNCTION) == 0) {
  (p[0]).err = 1;
  return AST_NONE;
}
  flowc_parser_advance(p);
  if (flowc_parser_check(p[0], TOK_IDENT) == 0) {
  (p[0]).err = 1;
  return AST_NONE;
}
  int32_t fn_start = start;
  int32_t fn_ns = ((p[0]).cur).start;
  int32_t fn_ne = ((p[0]).cur).end;
  flowc_parser_advance(p);
  int32_t params = AST_NONE;
  if (flowc_parser_check(p[0], TOK_LPAREN) == 1) {
  flowc_parser_advance(p);
  if (flowc_parser_check(p[0], TOK_RPAREN) == 0) {
  int32_t loop = 1;
  while (loop == 1) {
  if (flowc_parser_check(p[0], TOK_IDENT) == 0) {
  (p[0]).err = 1;
  return AST_NONE;
}
  int32_t pns = ((p[0]).cur).start;
  int32_t pne = ((p[0]).cur).end;
  flowc_parser_advance(p);
  if (flowc_parser_eat(p, TOK_COLON) == 0) {
  return AST_NONE;
}
  int32_t pty = flowc_parse_type(p);
  int32_t param = flowc_ast_alloc((&(p[0]).arena), AST_PARAM, pns, ((p[0]).cur).start);
  if (param == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[param]).name_start = pns;
  (((p[0]).arena).nodes[param]).name_end = pne;
  (((p[0]).arena).nodes[param]).a = pty;
  params = flowc_ast_chain_push((&(p[0]).arena), params, param);
  if (flowc_parser_check(p[0], TOK_COMMA) == 1) {
  flowc_parser_advance(p);
  if (flowc_parser_check(p[0], TOK_DOTDOT) == 1 || flowc_parser_check(p[0], TOK_DOT) == 1) {
  while (flowc_parser_check(p[0], TOK_DOTDOT) == 1 || flowc_parser_check(p[0], TOK_DOT) == 1) {
  flowc_parser_advance(p);
}
  loop = 0;
}
} else {
  loop = 0;
}
}
}
  if (flowc_parser_eat(p, TOK_RPAREN) == 0) {
  return AST_NONE;
}
}
  int32_t ret_ty = AST_NONE;
  if (flowc_parser_check(p[0], TOK_ARROW) == 1) {
  flowc_parser_advance(p);
  ret_ty = flowc_parse_type(p);
}
  int32_t fn = flowc_ast_alloc((&(p[0]).arena), AST_FN, fn_start, ((p[0]).cur).start);
  if (fn == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[fn]).name_start = fn_ns;
  (((p[0]).arena).nodes[fn]).name_end = fn_ne;
  (((p[0]).arena).nodes[fn]).a = params;
  (((p[0]).arena).nodes[fn]).b = ret_ty;
  (((p[0]).arena).nodes[fn]).c = AST_NONE;
  fns = flowc_ast_chain_push((&(p[0]).arena), fns, fn);
  if (flowc_parser_check(p[0], TOK_COMMA) == 1) {
  flowc_parser_advance(p);
}
}
  if (flowc_parser_eat(p, TOK_RBRACE) == 0) {
  return AST_NONE;
}
  int32_t id = flowc_ast_alloc((&(p[0]).arena), AST_EXTERN, start, ((p[0]).cur).start);
  if (id == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[id]).a = fns;
  return id;
}

int32_t flowc_parse_brace_idents(Parser* p) {
  if (flowc_parser_check(p[0], TOK_LBRACE) == 0) {
  return AST_NONE;
}
  flowc_parser_advance(p);
  int32_t names = AST_NONE;
  if (flowc_parser_check(p[0], TOK_RBRACE) == 0) {
  if (flowc_parser_check(p[0], TOK_IDENT) == 0) {
  (p[0]).err = 1;
  return AST_NONE;
}
  int32_t ns = ((p[0]).cur).start;
  int32_t ne = ((p[0]).cur).end;
  flowc_parser_advance(p);
  int32_t first = flowc_ast_alloc((&(p[0]).arena), AST_IDENT, ns, ne);
  if (first == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[first]).name_start = ns;
  (((p[0]).arena).nodes[first]).name_end = ne;
  names = flowc_ast_chain_push((&(p[0]).arena), names, first);
  while (flowc_parser_check(p[0], TOK_COMMA) == 1) {
  flowc_parser_advance(p);
  if (flowc_parser_check(p[0], TOK_IDENT) == 0) {
  (p[0]).err = 1;
  return AST_NONE;
}
  int32_t is = ((p[0]).cur).start;
  int32_t ie = ((p[0]).cur).end;
  flowc_parser_advance(p);
  int32_t ident = flowc_ast_alloc((&(p[0]).arena), AST_IDENT, is, ie);
  if (ident == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[ident]).name_start = is;
  (((p[0]).arena).nodes[ident]).name_end = ie;
  names = flowc_ast_chain_push((&(p[0]).arena), names, ident);
}
}
  if (flowc_parser_eat(p, TOK_RBRACE) == 0) {
  return AST_NONE;
}
  return names;
}

int32_t flowc_parse_import(Parser* p) {
  int32_t start = ((p[0]).cur).start;
  if (flowc_parser_eat_kw(p, KW_IMPORT) == 0) {
  return AST_NONE;
}
  if (flowc_parser_check(p[0], TOK_STRING) == 1) {
  int32_t ns = ((p[0]).cur).start;
  int32_t ne = ((p[0]).cur).end;
  flowc_parser_advance(p);
  int32_t id = flowc_ast_alloc((&(p[0]).arena), AST_IMPORT, start, ((p[0]).cur).start);
  if (id == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[id]).name_start = ns;
  (((p[0]).arena).nodes[id]).name_end = ne;
  (((p[0]).arena).nodes[id]).ival = 2;
  return id;
}
  int32_t path_s = 0;
  int32_t path_e = 0;
  int32_t form = 0;
  if (flowc_parser_check(p[0], TOK_DOT) == 1) {
  path_s = ((p[0]).cur).start;
  flowc_parser_advance(p);
  if (flowc_parser_check(p[0], TOK_IDENT) == 0) {
  (p[0]).err = 1;
  return AST_NONE;
}
  path_e = ((p[0]).cur).end;
  flowc_parser_advance(p);
  form = 1;
} else {
  if (flowc_parser_check(p[0], TOK_IDENT) == 0) {
  (p[0]).err = 1;
  return AST_NONE;
}
  path_s = ((p[0]).cur).start;
  path_e = ((p[0]).cur).end;
  flowc_parser_advance(p);
  while (flowc_parser_check(p[0], TOK_DOT) == 1) {
  flowc_parser_advance(p);
  if (flowc_parser_check(p[0], TOK_IDENT) == 0) {
  (p[0]).err = 1;
  return AST_NONE;
}
  path_e = ((p[0]).cur).end;
  flowc_parser_advance(p);
}
  form = 0;
}
  int32_t names = flowc_parse_brace_idents(p);
  if ((p[0]).err != 0) {
  return AST_NONE;
}
  int32_t id = flowc_ast_alloc((&(p[0]).arena), AST_IMPORT, start, ((p[0]).cur).start);
  if (id == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[id]).name_start = path_s;
  (((p[0]).arena).nodes[id]).name_end = path_e;
  (((p[0]).arena).nodes[id]).ival = form;
  (((p[0]).arena).nodes[id]).a = names;
  return id;
}

int32_t flowc_parse_let(Parser* p) {
  int32_t start = ((p[0]).cur).start;
  flowc_parser_advance(p);
  int32_t is_mut = 0;
  if (flowc_parser_check_kw(p[0], KW_MUT) == 1) {
  is_mut = 1;
  flowc_parser_advance(p);
}
  if (flowc_parser_check(p[0], TOK_IDENT) == 0 && flowc_parser_check(p[0], TOK_KEYWORD) == 0) {
  (p[0]).err = 1;
  return AST_NONE;
}
  int32_t ns = ((p[0]).cur).start;
  int32_t ne = ((p[0]).cur).end;
  flowc_parser_advance(p);
  int32_t ty = AST_NONE;
  if (flowc_parser_check(p[0], TOK_COLON) == 1) {
  flowc_parser_advance(p);
  ty = flowc_parse_type(p);
}
  if (flowc_parser_eat(p, TOK_EQ) == 0) {
  return AST_NONE;
}
  int32_t init = flowc_parse_expr(p);
  int32_t id = flowc_ast_alloc((&(p[0]).arena), AST_LET, start, ((p[0]).cur).start);
  if (id == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[id]).name_start = ns;
  (((p[0]).arena).nodes[id]).name_end = ne;
  (((p[0]).arena).nodes[id]).ival = is_mut;
  (((p[0]).arena).nodes[id]).a = ty;
  (((p[0]).arena).nodes[id]).b = init;
  return id;
}

void flowc_parser_skip_brace_block(Parser* p) {
  if (flowc_parser_check(p[0], TOK_LBRACE) == 1) {
  flowc_parser_advance(p);
  int32_t depth = 1;
  while (depth > 0 && flowc_parser_check(p[0], TOK_EOF) == 0) {
  if (flowc_parser_check(p[0], TOK_LBRACE) == 1) {
  depth = (depth + 1);
} else {
  if (flowc_parser_check(p[0], TOK_RBRACE) == 1) {
  depth = (depth - 1);
}
}
  if (depth > 0) {
  flowc_parser_advance(p);
}
}
  if (flowc_parser_check(p[0], TOK_RBRACE) == 1) {
  flowc_parser_advance(p);
}
}
}

void flowc_parser_skip_paren_block(Parser* p) {
  if (flowc_parser_check(p[0], TOK_LPAREN) == 1) {
  flowc_parser_advance(p);
  int32_t depth = 1;
  while (depth > 0 && flowc_parser_check(p[0], TOK_EOF) == 0) {
  if (flowc_parser_check(p[0], TOK_LPAREN) == 1) {
  depth = (depth + 1);
} else {
  if (flowc_parser_check(p[0], TOK_RPAREN) == 1) {
  depth = (depth - 1);
}
}
  if (depth > 0) {
  flowc_parser_advance(p);
}
}
  if (flowc_parser_check(p[0], TOK_RPAREN) == 1) {
  flowc_parser_advance(p);
}
}
}

int32_t flowc_parse_type_alias(Parser* p) {
  int32_t start = ((p[0]).cur).start;
  if (flowc_parser_eat_kw(p, KW_TYPE) == 0) {
  return AST_NONE;
}
  if (flowc_parser_check(p[0], TOK_IDENT) == 0) {
  (p[0]).err = 1;
  return AST_NONE;
}
  int32_t ns = ((p[0]).cur).start;
  int32_t ne = ((p[0]).cur).end;
  flowc_parser_advance(p);
  if (flowc_parser_eat(p, TOK_EQ) == 0) {
  return AST_NONE;
}
  int32_t base_ty = flowc_parse_type(p);
  if (flowc_parser_check(p[0], TOK_SEMI) == 1) {
  flowc_parser_advance(p);
}
  int32_t id = flowc_ast_alloc((&(p[0]).arena), AST_TYPE_ALIAS, start, ((p[0]).cur).start);
  if (id == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[id]).name_start = ns;
  (((p[0]).arena).nodes[id]).name_end = ne;
  (((p[0]).arena).nodes[id]).a = base_ty;
  return id;
}

int32_t flowc_parse_const(Parser* p, int32_t is_export) {
  int32_t start = ((p[0]).cur).start;
  if (flowc_parser_eat_kw(p, KW_CONST) == 0) {
  return AST_NONE;
}
  if (flowc_parser_check(p[0], TOK_IDENT) == 0) {
  (p[0]).err = 1;
  return AST_NONE;
}
  int32_t ns = ((p[0]).cur).start;
  int32_t ne = ((p[0]).cur).end;
  flowc_parser_advance(p);
  if (flowc_parser_eat(p, TOK_COLON) == 0) {
  return AST_NONE;
}
  int32_t ty = flowc_parse_type(p);
  if (flowc_parser_eat(p, TOK_EQ) == 0) {
  return AST_NONE;
}
  int32_t init = flowc_parse_expr(p);
  int32_t id = flowc_ast_alloc((&(p[0]).arena), AST_CONST, start, ((p[0]).cur).start);
  if (id == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[id]).name_start = ns;
  (((p[0]).arena).nodes[id]).name_end = ne;
  (((p[0]).arena).nodes[id]).a = ty;
  (((p[0]).arena).nodes[id]).b = init;
  (((p[0]).arena).nodes[id]).ival = is_export;
  return id;
}

int32_t flowc_parse_export(Parser* p) {
  int32_t start = ((p[0]).cur).start;
  if (flowc_parser_eat_kw(p, KW_EXPORT) == 0) {
  return AST_NONE;
}
  if (flowc_parser_check_kw(p[0], KW_FUNCTION) == 1) {
  int32_t fn = flowc_parse_function(p);
  if (fn == AST_NONE) {
  return AST_NONE;
}
  int32_t id = flowc_ast_alloc((&(p[0]).arena), AST_EXPORT, start, ((p[0]).cur).start);
  if (id == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[id]).a = fn;
  return id;
}
  if (flowc_parser_check_kw(p[0], KW_STRUCT) == 1) {
  int32_t st = flowc_parse_struct(p);
  if (st == AST_NONE) {
  return AST_NONE;
}
  int32_t id = flowc_ast_alloc((&(p[0]).arena), AST_EXPORT, start, ((p[0]).cur).start);
  if (id == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[id]).a = st;
  return id;
}
  if (flowc_parser_check_kw(p[0], KW_CONST) == 1) {
  return flowc_parse_const(p, 1);
}
  if (flowc_parser_check_kw(p[0], KW_EFFECT) == 1 || flowc_parser_check_kw(p[0], KW_CAPABILITY) == 1) {
  flowc_parser_advance(p);
  if (flowc_parser_check(p[0], TOK_IDENT) == 1) {
  flowc_parser_advance(p);
}
  flowc_parser_skip_brace_block(p);
  return flowc_ast_alloc((&(p[0]).arena), AST_EXPR_STMT, start, ((p[0]).cur).start);
}
  if (flowc_parser_check_kw(p[0], KW_TYPE) == 1) {
  return flowc_parse_type_alias(p);
}
  if (flowc_parser_check(p[0], TOK_IDENT) == 1) {
  int32_t ns = ((p[0]).cur).start;
  int32_t ne = ((p[0]).cur).end;
  if ((ne - ns) == 8 && ((p[0]).lex).input[ns] == 100 && ((p[0]).lex).input[(ns + 1)] == 105 && ((p[0]).lex).input[(ns + 2)] == 115 && ((p[0]).lex).input[(ns + 3)] == 116 && ((p[0]).lex).input[(ns + 4)] == 105 && ((p[0]).lex).input[(ns + 5)] == 110 && ((p[0]).lex).input[(ns + 6)] == 99 && ((p[0]).lex).input[(ns + 7)] == 116) {
  flowc_parser_advance(p);
  if (flowc_parser_check_kw(p[0], KW_TYPE) == 1) {
  return flowc_parse_type_alias(p);
}
}
}
  if (flowc_parser_check(p[0], TOK_IDENT) == 0) {
  (p[0]).err = 1;
  return AST_NONE;
}
  int32_t names = AST_NONE;
  int32_t ns = ((p[0]).cur).start;
  int32_t ne = ((p[0]).cur).end;
  flowc_parser_advance(p);
  int32_t first = flowc_ast_alloc((&(p[0]).arena), AST_IDENT, ns, ne);
  if (first == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[first]).name_start = ns;
  (((p[0]).arena).nodes[first]).name_end = ne;
  names = flowc_ast_chain_push((&(p[0]).arena), names, first);
  while (flowc_parser_check(p[0], TOK_COMMA) == 1) {
  flowc_parser_advance(p);
  if (flowc_parser_check(p[0], TOK_IDENT) == 0) {
  (p[0]).err = 1;
  return AST_NONE;
}
  int32_t is = ((p[0]).cur).start;
  int32_t ie = ((p[0]).cur).end;
  flowc_parser_advance(p);
  int32_t ident = flowc_ast_alloc((&(p[0]).arena), AST_IDENT, is, ie);
  if (ident == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[ident]).name_start = is;
  (((p[0]).arena).nodes[ident]).name_end = ie;
  names = flowc_ast_chain_push((&(p[0]).arena), names, ident);
}
  int32_t id = flowc_ast_alloc((&(p[0]).arena), AST_EXPORT, start, ((p[0]).cur).start);
  if (id == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[id]).a = names;
  (((p[0]).arena).nodes[id]).ival = 1;
  return id;
}

int32_t flowc_parse_program(Parser* p) {
  int32_t start = 0;
  int32_t items = AST_NONE;
  while (flowc_parser_check(p[0], TOK_EOF) == 0) {
  int32_t item = AST_NONE;
  while (flowc_parser_check(p[0], TOK_AT) == 1) {
  flowc_parser_advance(p);
  int32_t attr_name = -1;
  int32_t attr_name_end = -1;
  if (flowc_parser_check(p[0], TOK_IDENT) == 1) {
  attr_name = ((p[0]).cur).start;
  attr_name_end = ((p[0]).cur).end;
  flowc_parser_advance(p);
}
  if (flowc_parser_check(p[0], TOK_LPAREN) == 1) {
  if (attr_name >= 0 && flowc_parser_span_is(p[0], attr_name, attr_name_end, "cInclude") == 1) {
  flowc_parser_advance(p);
  if (flowc_parser_check(p[0], TOK_STRING) == 1) {
  int32_t hdr_start = ((p[0]).cur).start;
  int32_t hdr_end = ((p[0]).cur).end;
  flowc_parser_advance(p);
  if (flowc_parser_check(p[0], TOK_RPAREN) == 1) {
  flowc_parser_advance(p);
}
  int32_t cid = flowc_ast_alloc((&(p[0]).arena), AST_C_INCLUDE, hdr_start, hdr_end);
  if (cid != AST_NONE) {
  ((p[0]).arena).nodes[cid].name_start = hdr_start;
  ((p[0]).arena).nodes[cid].name_end = hdr_end;
  items = flowc_ast_chain_push((&(p[0]).arena), items, cid);
}
}
  continue;
}
  if (attr_name >= 0 && flowc_parser_span_is(p[0], attr_name, attr_name_end, "cEmbed") == 1) {
  flowc_parser_advance(p);
  if (flowc_parser_check(p[0], TOK_STRING) == 1) {
  int32_t code_start = ((p[0]).cur).start;
  int32_t code_end = ((p[0]).cur).end;
  flowc_parser_advance(p);
  if (flowc_parser_check(p[0], TOK_RPAREN) == 1) {
  flowc_parser_advance(p);
}
  int32_t cid2 = flowc_ast_alloc((&(p[0]).arena), AST_C_EMBED, code_start, code_end);
  if (cid2 != AST_NONE) {
  ((p[0]).arena).nodes[cid2].name_start = code_start;
  ((p[0]).arena).nodes[cid2].name_end = code_end;
  items = flowc_ast_chain_push((&(p[0]).arena), items, cid2);
}
}
  continue;
}
  if (attr_name >= 0 && flowc_parser_span_is(p[0], attr_name, attr_name_end, "cImport") == 1) {
  flowc_parser_advance(p);
  if (flowc_parser_check(p[0], TOK_STRING) == 1) {
  int32_t hdr_start2 = ((p[0]).cur).start;
  int32_t hdr_end2 = ((p[0]).cur).end;
  flowc_parser_advance(p);
  if (flowc_parser_check(p[0], TOK_RPAREN) == 1) {
  flowc_parser_advance(p);
}
  int32_t cid3 = flowc_ast_alloc((&(p[0]).arena), AST_C_IMPORT, hdr_start2, hdr_end2);
  if (cid3 != AST_NONE) {
  ((p[0]).arena).nodes[cid3].name_start = hdr_start2;
  ((p[0]).arena).nodes[cid3].name_end = hdr_end2;
  items = flowc_ast_chain_push((&(p[0]).arena), items, cid3);
}
}
  continue;
}
  flowc_parser_advance(p);
  int32_t depth = 1;
  while (depth > 0 && flowc_parser_check(p[0], TOK_EOF) == 0) {
  if (flowc_parser_check(p[0], TOK_LPAREN) == 1) {
  depth = (depth + 1);
} else {
  if (flowc_parser_check(p[0], TOK_RPAREN) == 1) {
  depth = (depth - 1);
}
}
  if (depth > 0) {
  flowc_parser_advance(p);
}
}
  if (flowc_parser_check(p[0], TOK_RPAREN) == 1) {
  flowc_parser_advance(p);
}
}
}
  if (flowc_parser_check_kw(p[0], KW_LET) == 1) {
  item = flowc_parse_let(p);
} else {
  if (flowc_parser_check_kw(p[0], KW_IMPORT) == 1) {
  item = flowc_parse_import(p);
} else {
  if (flowc_parser_check_kw(p[0], KW_EXPORT) == 1) {
  item = flowc_parse_export(p);
} else {
  if (flowc_parser_check_kw(p[0], KW_FUNCTION) == 1) {
  item = flowc_parse_function(p);
} else {
  if (flowc_parser_check_kw(p[0], KW_STRUCT) == 1) {
  item = flowc_parse_struct(p);
} else {
  if (flowc_parser_check_kw(p[0], KW_EXTERN) == 1) {
  item = flowc_parse_extern(p);
} else {
  if (flowc_parser_check_kw(p[0], KW_CONST) == 1) {
  item = flowc_parse_const(p, 0);
} else {
  if (flowc_parser_check_kw(p[0], KW_TYPE) == 1) {
  item = flowc_parse_type_alias(p);
} else {
  if (flowc_parser_check_kw(p[0], KW_UNIT) == 1) {
  flowc_parser_advance(p);
  if (flowc_parser_check(p[0], TOK_IDENT) == 1) {
  flowc_parser_advance(p);
}
  if (flowc_parser_check(p[0], TOK_EQ) == 1) {
  flowc_parser_advance(p);
  int32_t _skip = flowc_parse_expr(p);
}
  item = flowc_ast_alloc((&(p[0]).arena), AST_EXPR_STMT, ((p[0]).cur).start, ((p[0]).cur).start);
} else {
  if (flowc_parser_check_kw(p[0], KW_EFFECT) == 1 || flowc_parser_check_kw(p[0], KW_CAPABILITY) == 1) {
  int32_t eff_start = ((p[0]).cur).start;
  flowc_parser_advance(p);
  if (flowc_parser_check(p[0], TOK_IDENT) == 1) {
  flowc_parser_advance(p);
}
  flowc_parser_skip_brace_block(p);
  item = flowc_ast_alloc((&(p[0]).arena), AST_EXPR_STMT, eff_start, ((p[0]).cur).start);
} else {
  (p[0]).err = 1;
  return AST_NONE;
}
}
}
}
}
}
}
}
}
}
  if (item == AST_NONE) {
  return AST_NONE;
}
  items = flowc_ast_chain_push((&(p[0]).arena), items, item);
}
  int32_t id = flowc_ast_alloc((&(p[0]).arena), AST_PROGRAM, start, ((p[0]).cur).start);
  if (id == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[id]).a = items;
  return id;
}


typedef struct CgenBuf {
  uint8_t* out;
  int32_t cap;
  int32_t len;
  int32_t err;
  uint8_t* sigs;
  int32_t sigs_len;
} CgenBuf;

CgenBuf flowc_cgen_buf_init(uint8_t* out, int32_t cap) {
  return (CgenBuf){ .out = out, .cap = cap, .len = 0, .err = 0, .sigs = NULL, .sigs_len = 0 };
}

void flowc_cgen_putc(CgenBuf* w, int32_t c) {
  if ((w[0]).err != 0) {
  return;
}
  if ((w[0]).len >= (w[0]).cap) {
  (w[0]).err = 1;
  return;
}
  (w[0]).out[(w[0]).len] = c;
  (w[0]).len = ((w[0]).len + 1);
}

void flowc_cgen_puts(CgenBuf* w, const char* s) {
  uint8_t* p = (uint8_t*)(s);
  int32_t n = (int32_t)(strlen(s));
  int32_t i = 0;
  while (i < n) {
  flowc_cgen_putc(w, p[i]);
  i = (i + 1);
}
}

void flowc_cgen_put_span(CgenBuf* w, uint8_t* src, int32_t start, int32_t end) {
  int32_t i = start;
  while (i < end) {
  flowc_cgen_putc(w, src[i]);
  i = (i + 1);
}
}

void flowc_cgen_put_i32(CgenBuf* w, int32_t val) {
  int32_t v = val;
  if (v < 0) {
  flowc_cgen_putc(w, 45);
  v = (0 - v);
}
  if (v == 0) {
  flowc_cgen_putc(w, 48);
  return;
}
  uint8_t digits[16] = { 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
  int32_t n = 0;
  while (v > 0) {
  digits[n] = ((v % 10) + 48);
  v = (v / 10);
  n = (n + 1);
}
  int32_t i = n;
  while (i > 0) {
  i = (i - 1);
  flowc_cgen_putc(w, digits[i]);
}
}

void flowc_cgen_emit_expr(CgenBuf* w, AstArena arena, uint8_t* src, int32_t id);
void flowc_cgen_emit_stmt(CgenBuf* w, AstArena arena, uint8_t* src, int32_t id);
void flowc_cgen_emit_block(CgenBuf* w, AstArena arena, uint8_t* src, int32_t id);
int32_t flowc_cgen_expr_is_string(CgenBuf* w, AstArena arena, uint8_t* src, int32_t id);
int32_t flowc_cgen_ident_is_string(AstArena arena, uint8_t* src, int32_t id);
int32_t flowc_cgen_span_eq(uint8_t* src, int32_t a0, int32_t a1, int32_t b0, int32_t b1) {
  if ((a1 - a0) != (b1 - b0)) {
  return 0;
}
  int32_t i = 0;
  int32_t n = (a1 - a0);
  while (i < n) {
  if (src[(a0 + i)] != src[(b0 + i)]) {
  return 0;
}
  i = (i + 1);
}
  return 1;
}

int32_t flowc_cgen_span_is(uint8_t* src, int32_t start, int32_t end, const char* lit) {
  uint8_t* p = (uint8_t*)(lit);
  int32_t n = (int32_t)(strlen(lit));
  if ((end - start) != n) {
  return 0;
}
  int32_t i = 0;
  while (i < n) {
  if (src[(start + i)] != p[i]) {
  return 0;
}
  i = (i + 1);
}
  return 1;
}

int32_t flowc_cgen_is_struct_type(AstArena arena, uint8_t* src, int32_t ty) {
  if (ty == AST_NONE) {
  return 0;
}
  if (((arena).nodes[ty]).kind != AST_TYPE) {
  return 0;
}
  int32_t ts = ((arena).nodes[ty]).name_start;
  int32_t te = ((arena).nodes[ty]).name_end;
  int32_t i = 0;
  while (i < (arena).len) {
  if (((arena).nodes[i]).kind == AST_STRUCT || ((arena).nodes[i]).kind == AST_TYPE_ALIAS) {
  if (flowc_cgen_span_eq(src, ts, te, ((arena).nodes[i]).name_start, ((arena).nodes[i]).name_end) == 1) {
  return 1;
}
}
  i = (i + 1);
}
  return 0;
}

void flowc_cgen_emit_type(CgenBuf* w, AstArena arena, uint8_t* src, int32_t ty) {
  if (ty == AST_NONE || ((arena).nodes[ty]).kind != AST_TYPE) {
  flowc_cgen_puts(w, "int32_t");
  return;
}
  if (((arena).nodes[ty]).ival == (0 - 1) || ((arena).nodes[ty]).ival == (0 - 2)) {
  flowc_cgen_emit_type(w, arena, src, ((arena).nodes[ty]).b);
  flowc_cgen_puts(w, " (*");
  flowc_cgen_puts(w, ")(");
  int32_t param = ((arena).nodes[ty]).a;
  int32_t first = 1;
  while (param != AST_NONE) {
  if (first == 0) {
  flowc_cgen_puts(w, ", ");
}
  flowc_cgen_emit_type(w, arena, src, param);
  first = 0;
  param = ((arena).nodes[param]).next;
}
  flowc_cgen_putc(w, 41);
  return;
}
  int32_t ns = ((arena).nodes[ty]).name_start;
  int32_t ne = ((arena).nodes[ty]).name_end;
  int32_t inner = ((arena).nodes[ty]).a;
  if (inner != AST_NONE && flowc_cgen_span_is(src, ns, ne, "ptr") == 1) {
  flowc_cgen_emit_type(w, arena, src, inner);
  flowc_cgen_putc(w, 42);
  return;
}
  if (inner != AST_NONE && flowc_cgen_span_is(src, ns, ne, "array") == 1 && ((arena).nodes[ty]).ival == 0) {
  flowc_cgen_emit_type(w, arena, src, inner);
  flowc_cgen_putc(w, 42);
  return;
}
  if (inner != AST_NONE && flowc_cgen_span_is(src, ns, ne, "array") == 1 && ((arena).nodes[ty]).ival > 0) {
  flowc_cgen_emit_type(w, arena, src, inner);
  flowc_cgen_putc(w, 42);
  return;
}
  if (flowc_cgen_is_struct_type(arena, src, ty) == 1) {
  flowc_cgen_put_span(w, src, ns, ne);
  return;
}
  if (flowc_cgen_span_is(src, ns, ne, "void") == 1) {
  flowc_cgen_puts(w, "void");
  return;
}
  if (flowc_cgen_span_is(src, ns, ne, "u8") == 1) {
  flowc_cgen_puts(w, "uint8_t");
  return;
}
  if (flowc_cgen_span_is(src, ns, ne, "i8") == 1) {
  flowc_cgen_puts(w, "int8_t");
  return;
}
  if (flowc_cgen_span_is(src, ns, ne, "u16") == 1) {
  flowc_cgen_puts(w, "uint16_t");
  return;
}
  if (flowc_cgen_span_is(src, ns, ne, "i16") == 1) {
  flowc_cgen_puts(w, "int16_t");
  return;
}
  if (flowc_cgen_span_is(src, ns, ne, "u32") == 1) {
  flowc_cgen_puts(w, "uint32_t");
  return;
}
  if (flowc_cgen_span_is(src, ns, ne, "i32") == 1) {
  flowc_cgen_puts(w, "int32_t");
  return;
}
  if (flowc_cgen_span_is(src, ns, ne, "u64") == 1) {
  flowc_cgen_puts(w, "uint64_t");
  return;
}
  if (flowc_cgen_span_is(src, ns, ne, "i64") == 1) {
  flowc_cgen_puts(w, "int64_t");
  return;
}
  if (flowc_cgen_span_is(src, ns, ne, "f32") == 1) {
  flowc_cgen_puts(w, "float");
  return;
}
  if (flowc_cgen_span_is(src, ns, ne, "f64") == 1) {
  flowc_cgen_puts(w, "double");
  return;
}
  if (flowc_cgen_span_is(src, ns, ne, "bool") == 1) {
  flowc_cgen_puts(w, "bool");
  return;
}
  if (flowc_cgen_span_is(src, ns, ne, "string") == 1) {
  flowc_cgen_puts(w, "const char*");
  return;
}
  if (ne > ns) {
  flowc_cgen_put_span(w, src, ns, ne);
  return;
}
  flowc_cgen_puts(w, "int32_t");
}

int32_t flowc_cgen_find_fn(AstArena arena, uint8_t* src, int32_t start, int32_t end) {
  if (end <= start) {
  return AST_NONE;
}
  int32_t i = 0;
  while (i < (arena).len) {
  if (((arena).nodes[i]).kind == AST_FN) {
  if (flowc_cgen_span_eq(src, start, end, ((arena).nodes[i]).name_start, ((arena).nodes[i]).name_end) == 1) {
  return i;
}
}
  i = (i + 1);
}
  return AST_NONE;
}

int32_t flowc_cgen_infer_type_node(AstArena arena, uint8_t* src, int32_t init) {
  if (init == AST_NONE) {
  return AST_NONE;
}
  int32_t kind = ((arena).nodes[init]).kind;
  if (kind == AST_CAST) {
  return ((arena).nodes[init]).b;
}
  if (kind == AST_CALL) {
  int32_t fn = flowc_cgen_find_fn(arena, src, ((arena).nodes[init]).name_start, ((arena).nodes[init]).name_end);
  if (fn != AST_NONE) {
  return ((arena).nodes[fn]).b;
}
}
  return AST_NONE;
}

int32_t flowc_cgen_sig_find(uint8_t* buf, int32_t blen, uint8_t* src, int32_t start, int32_t end) {
  if (buf == NULL) {
  return (0 - 1);
}
  int32_t nlen = (end - start);
  if (nlen <= 0 || blen <= 0) {
  return (0 - 1);
}
  int32_t p = 0;
  while (p < blen) {
  int32_t i = 0;
  while ((p + i) < blen && buf[(p + i)] != 0) {
  i = (i + 1);
}
  int32_t hit = 0;
  if (i == nlen) {
  hit = 1;
  int32_t j = 0;
  while (j < nlen) {
  if (buf[(p + j)] != src[(start + j)]) {
  hit = 0;
}
  j = (j + 1);
}
}
  int32_t vpos = ((p + i) + 1);
  if (vpos >= blen) {
  return (0 - 1);
}
  if (hit == 1) {
  return vpos;
}
  int32_t k = 0;
  while ((vpos + k) < blen && buf[(vpos + k)] != 0) {
  k = (k + 1);
}
  p = ((vpos + k) + 1);
}
  return (0 - 1);
}

int32_t flowc_cgen_write_sig_type(CgenBuf* w, AstArena arena, uint8_t* src, int32_t call) {
  int32_t off = flowc_cgen_sig_find((w[0]).sigs, (w[0]).sigs_len, src, ((arena).nodes[call]).name_start, ((arena).nodes[call]).name_end);
  if (off < 0) {
  return 0;
}
  int32_t i = off;
  while (i < (w[0]).sigs_len) {
  if ((w[0]).sigs[i] == 0) {
  return 1;
}
  flowc_cgen_putc(w, (w[0]).sigs[i]);
  i = (i + 1);
}
  return 1;
}

int32_t flowc_cgen_write_lit_type(CgenBuf* w, AstArena arena, uint8_t* src, int32_t init) {
  if (init == AST_NONE) {
  return 0;
}
  int32_t kind = ((arena).nodes[init]).kind;
  if (kind == AST_STRING) {
  flowc_cgen_puts(w, "const char*");
  return 1;
}
  if (kind == AST_FLOAT) {
  flowc_cgen_puts(w, "double");
  return 1;
}
  if (kind == AST_STRUCT_LIT) {
  flowc_cgen_put_span(w, src, ((arena).nodes[init]).name_start, ((arena).nodes[init]).name_end);
  return 1;
}
  if (kind == AST_BINOP) {
  if (flowc_cgen_expr_is_string(w, arena, src, init) == 1) {
  flowc_cgen_puts(w, "const char*");
  return 1;
}
  return 0;
}
  if (kind == AST_CALL) {
  return flowc_cgen_write_sig_type(w, arena, src, init);
}
  return 0;
}

int32_t flowc_cgen_type_is_string(AstArena arena, uint8_t* src, int32_t ty) {
  if (ty == AST_NONE) {
  return 0;
}
  if (((arena).nodes[ty]).kind != AST_TYPE) {
  return 0;
}
  if (((arena).nodes[ty]).a != AST_NONE) {
  return 0;
}
  return flowc_cgen_span_is(src, ((arena).nodes[ty]).name_start, ((arena).nodes[ty]).name_end, "string");
}

int32_t flowc_cgen_sig_is_string(CgenBuf* w, AstArena arena, uint8_t* src, int32_t call) {
  int32_t off = flowc_cgen_sig_find((w[0]).sigs, (w[0]).sigs_len, src, ((arena).nodes[call]).name_start, ((arena).nodes[call]).name_end);
  if (off < 0) {
  return 0;
}
  const char* want = "const char*";
  uint8_t* wp = (uint8_t*)(want);
  int32_t wn = (int32_t)(strlen(want));
  int32_t i = 0;
  while (i < wn) {
  if ((off + i) >= (w[0]).sigs_len) {
  return 0;
}
  if ((w[0]).sigs[(off + i)] != wp[i]) {
  return 0;
}
  i = (i + 1);
}
  if ((off + wn) >= (w[0]).sigs_len) {
  return 0;
}
  if ((w[0]).sigs[(off + wn)] != 0) {
  return 0;
}
  return 1;
}

int32_t flowc_cgen_expr_is_string(CgenBuf* w, AstArena arena, uint8_t* src, int32_t id) {
  if (id == AST_NONE) {
  return 0;
}
  int32_t kind = ((arena).nodes[id]).kind;
  if (kind == AST_STRING) {
  return 1;
}
  if (kind == AST_CAST) {
  return flowc_cgen_type_is_string(arena, src, ((arena).nodes[id]).b);
}
  if (kind == AST_BINOP) {
  if (((arena).nodes[id]).ival != TOK_PLUS) {
  return 0;
}
  if (flowc_cgen_expr_is_string(w, arena, src, ((arena).nodes[id]).a) == 1) {
  return 1;
}
  return flowc_cgen_expr_is_string(w, arena, src, ((arena).nodes[id]).b);
}
  if (kind == AST_CALL) {
  int32_t fn = flowc_cgen_find_fn(arena, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  if (fn != AST_NONE) {
  return flowc_cgen_type_is_string(arena, src, ((arena).nodes[fn]).b);
}
  return flowc_cgen_sig_is_string(w, arena, src, id);
}
  if (kind == AST_IDENT) {
  return flowc_cgen_ident_is_string(arena, src, id);
}
  return 0;
}

int32_t flowc_cgen_ident_is_string(AstArena arena, uint8_t* src, int32_t id) {
  int32_t ns = ((arena).nodes[id]).name_start;
  int32_t ne = ((arena).nodes[id]).name_end;
  int32_t found = 0;
  int32_t all_str = 1;
  int32_t i = 0;
  while (i < (arena).len) {
  if (((arena).nodes[i]).kind == AST_PARAM || ((arena).nodes[i]).kind == AST_LET) {
  if (flowc_cgen_span_eq(src, ns, ne, ((arena).nodes[i]).name_start, ((arena).nodes[i]).name_end) == 1) {
  found = (found + 1);
  int32_t ty = ((arena).nodes[i]).a;
  if (ty == AST_NONE) {
  all_str = 0;
} else {
  if (flowc_cgen_type_is_string(arena, src, ty) == 0) {
  all_str = 0;
}
}
}
}
  i = (i + 1);
}
  if (found > 0 && all_str == 1) {
  return 1;
}
  return 0;
}

int32_t flowc_cgen_is_str_concat(CgenBuf* w, AstArena arena, uint8_t* src, int32_t id) {
  if (flowc_cgen_expr_is_string(w, arena, src, ((arena).nodes[id]).a) == 1) {
  return 1;
}
  return flowc_cgen_expr_is_string(w, arena, src, ((arena).nodes[id]).b);
}

int32_t flowc_cgen_sig_put(AstArena arena, uint8_t* src, uint8_t* buf, int32_t cap, int32_t len, int32_t fn, int32_t rt) {
  int32_t ns = ((arena).nodes[fn]).name_start;
  int32_t ne = ((arena).nodes[fn]).name_end;
  int32_t nlen = (ne - ns);
  if (nlen <= 0) {
  return len;
}
  if (((len + nlen) + 4) > cap) {
  return len;
}
  int32_t i = 0;
  while (i < nlen) {
  buf[(len + i)] = src[(ns + i)];
  i = (i + 1);
}
  int32_t n = (len + nlen);
  buf[n] = 0;
  n = (n + 1);
  uint8_t* dest = (uint8_t*)((buf + n));
  CgenBuf tw = flowc_cgen_buf_init(dest, ((cap - n) - 1));
  flowc_cgen_emit_type((&tw), arena, src, rt);
  if ((tw).err != 0) {
  return len;
}
  if ((tw).len <= 0) {
  return len;
}
  n = (n + (tw).len);
  buf[n] = 0;
  n = (n + 1);
  return n;
}

int32_t flowc_cgen_binop_needs_parens(int32_t op) {
  if (op == TOK_EQEQ || op == TOK_NE) {
  return 0;
}
  if (op == TOK_LT || op == TOK_GT || op == TOK_LE || op == TOK_GE) {
  return 0;
}
  if (op == TOK_AMPAMP || op == TOK_BARBAR) {
  return 0;
}
  return 1;
}

void flowc_cgen_emit_binop_op(CgenBuf* w, int32_t op) {
  if (op == TOK_PLUS) {
  flowc_cgen_puts(w, " + ");
  return;
}
  if (op == TOK_MINUS) {
  flowc_cgen_puts(w, " - ");
  return;
}
  if (op == TOK_STAR) {
  flowc_cgen_puts(w, " * ");
  return;
}
  if (op == TOK_SLASH) {
  flowc_cgen_puts(w, " / ");
  return;
}
  if (op == TOK_PERCENT) {
  flowc_cgen_puts(w, " % ");
  return;
}
  if (op == TOK_EQEQ) {
  flowc_cgen_puts(w, " == ");
  return;
}
  if (op == TOK_NE) {
  flowc_cgen_puts(w, " != ");
  return;
}
  if (op == TOK_LT) {
  flowc_cgen_puts(w, " < ");
  return;
}
  if (op == TOK_GT) {
  flowc_cgen_puts(w, " > ");
  return;
}
  if (op == TOK_LE) {
  flowc_cgen_puts(w, " <= ");
  return;
}
  if (op == TOK_GE) {
  flowc_cgen_puts(w, " >= ");
  return;
}
  if (op == TOK_AMPAMP) {
  flowc_cgen_puts(w, " && ");
  return;
}
  if (op == TOK_BARBAR) {
  flowc_cgen_puts(w, " || ");
  return;
}
  if (op == TOK_AMP) {
  flowc_cgen_puts(w, " & ");
  return;
}
  if (op == TOK_BAR) {
  flowc_cgen_puts(w, " | ");
  return;
}
  if (op == TOK_CARET) {
  flowc_cgen_puts(w, " ^ ");
  return;
}
  if (op == TOK_SHL) {
  flowc_cgen_puts(w, " << ");
  return;
}
  if (op == TOK_SHR) {
  flowc_cgen_puts(w, " >> ");
  return;
}
  flowc_cgen_puts(w, " /*op*/ ");
}

void flowc_cgen_emit_print_intrinsic(CgenBuf* w, AstArena arena, uint8_t* src, int32_t id, int32_t newline) {
  int32_t arg = ((arena).nodes[id]).a;
  if (arg == AST_NONE) {
  if (newline == 1) {
  flowc_cgen_puts(w, "printf(\"\\n\")");
}
  return;
}
  const char* fmt = "%d";
  int32_t arg_kind = ((arena).nodes[arg]).kind;
  if (arg_kind == AST_STRING) {
  fmt = "%s";
}
  if (arg_kind == AST_FLOAT) {
  fmt = "%f";
}
  if (arg_kind == AST_BOOL) {
  fmt = "%d";
}
  flowc_cgen_puts(w, "printf(\"");
  flowc_cgen_puts(w, fmt);
  if (newline == 1) {
  flowc_cgen_puts(w, "\\n");
}
  flowc_cgen_puts(w, "\", ");
  flowc_cgen_emit_expr(w, arena, src, arg);
  arg = ((arena).nodes[arg]).next;
  while (arg != AST_NONE) {
  flowc_cgen_puts(w, ", ");
  flowc_cgen_emit_expr(w, arena, src, arg);
  arg = ((arena).nodes[arg]).next;
}
  flowc_cgen_putc(w, 41);
}

void flowc_cgen_emit_expr(CgenBuf* w, AstArena arena, uint8_t* src, int32_t id) {
  if (id == AST_NONE || (w[0]).err != 0) {
  return;
}
  int32_t kind = ((arena).nodes[id]).kind;
  if (kind == AST_INT) {
  flowc_cgen_put_i32(w, ((arena).nodes[id]).ival);
  return;
}
  if (kind == AST_FLOAT) {
  flowc_cgen_put_span(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  return;
}
  if (kind == AST_BOOL) {
  flowc_cgen_put_i32(w, ((arena).nodes[id]).ival);
  return;
}
  if (kind == AST_IDENT) {
  if (flowc_cgen_span_is(src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end, "null") == 1) {
  flowc_cgen_puts(w, "NULL");
  return;
}
  flowc_cgen_put_span(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  return;
}
  if (kind == AST_STRING) {
  flowc_cgen_put_span(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  return;
}
  if (kind == AST_BINOP) {
  int32_t op = ((arena).nodes[id]).ival;
  if (op == TOK_PLUS) {
  if (flowc_cgen_is_str_concat(w, arena, src, id) == 1) {
  flowc_cgen_puts(w, "__flowc_str_concat(");
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_cgen_puts(w, ", ");
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).b);
  flowc_cgen_putc(w, 41);
  return;
}
}
  int32_t wrap = flowc_cgen_binop_needs_parens(op);
  if (wrap == 1) {
  flowc_cgen_putc(w, 40);
}
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_cgen_emit_binop_op(w, op);
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).b);
  if (wrap == 1) {
  flowc_cgen_putc(w, 41);
}
  return;
}
  if (kind == AST_UNARY) {
  flowc_cgen_putc(w, 40);
  if (((arena).nodes[id]).ival == TOK_MINUS) {
  flowc_cgen_putc(w, 45);
} else {
  if (((arena).nodes[id]).ival == TOK_BANG) {
  flowc_cgen_putc(w, 33);
} else {
  if (((arena).nodes[id]).ival == TOK_AMP) {
  flowc_cgen_putc(w, 38);
} else {
  if (((arena).nodes[id]).ival == TOK_TILDE) {
  flowc_cgen_putc(w, 126);
}
}
}
}
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_cgen_putc(w, 41);
  return;
}
  if (kind == AST_CAST) {
  flowc_cgen_putc(w, 40);
  flowc_cgen_emit_type(w, arena, src, ((arena).nodes[id]).b);
  flowc_cgen_puts(w, ")(");
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_cgen_putc(w, 41);
  return;
}
  if (kind == AST_INDEX) {
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_cgen_putc(w, 91);
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).b);
  flowc_cgen_putc(w, 93);
  return;
}
  if (kind == AST_CALL) {
  if (flowc_cgen_span_is(src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end, "println") == 1) {
  flowc_cgen_emit_print_intrinsic(w, arena, src, id, 1);
  return;
}
  if (flowc_cgen_span_is(src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end, "print") == 1) {
  flowc_cgen_emit_print_intrinsic(w, arena, src, id, 0);
  return;
}
  int32_t n_args = flowc_ast_chain_len(arena, ((arena).nodes[id]).a);
  if (flowc_cgen_span_is(src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end, "c64") == 1) {
  if (n_args == 2) {
  flowc_cgen_puts(w, "((float)(");
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_cgen_puts(w, ") + (float)(");
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[((arena).nodes[id]).a]).next);
  flowc_cgen_puts(w, ") * I)");
  return;
}
  if (n_args == 1) {
  flowc_cgen_puts(w, "((float)(");
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_cgen_puts(w, ") + 0.0f * I)");
  return;
}
}
  if (flowc_cgen_span_is(src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end, "c128") == 1) {
  if (n_args == 2) {
  flowc_cgen_puts(w, "((double)(");
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_cgen_puts(w, ") + (double)(");
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[((arena).nodes[id]).a]).next);
  flowc_cgen_puts(w, ") * I)");
  return;
}
  if (n_args == 1) {
  flowc_cgen_puts(w, "((double)(");
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_cgen_puts(w, ") + 0.0 * I)");
  return;
}
}
  flowc_cgen_put_span(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  flowc_cgen_putc(w, 40);
  int32_t arg = ((arena).nodes[id]).a;
  int32_t first = 1;
  while (arg != AST_NONE) {
  if (first == 0) {
  flowc_cgen_puts(w, ", ");
}
  first = 0;
  flowc_cgen_emit_expr(w, arena, src, arg);
  arg = ((arena).nodes[arg]).next;
}
  flowc_cgen_putc(w, 41);
  return;
}
  if (kind == AST_FIELD_ACCESS) {
  flowc_cgen_putc(w, 40);
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_cgen_putc(w, 41);
  flowc_cgen_putc(w, 46);
  flowc_cgen_put_span(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  return;
}
  if (kind == AST_STRUCT_LIT) {
  flowc_cgen_putc(w, 40);
  flowc_cgen_put_span(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  flowc_cgen_puts(w, "){ ");
  int32_t field = ((arena).nodes[id]).a;
  int32_t first = 1;
  while (field != AST_NONE) {
  if (first == 0) {
  flowc_cgen_puts(w, ", ");
}
  first = 0;
  flowc_cgen_putc(w, 46);
  flowc_cgen_put_span(w, src, ((arena).nodes[field]).name_start, ((arena).nodes[field]).name_end);
  flowc_cgen_puts(w, " = ");
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[field]).a);
  field = ((arena).nodes[field]).next;
}
  flowc_cgen_puts(w, " }");
  return;
}
  if (kind == AST_ARRAY_LIT) {
  flowc_cgen_puts(w, "{ ");
  int32_t el = ((arena).nodes[id]).a;
  int32_t first = 1;
  while (el != AST_NONE) {
  if (first == 0) {
  flowc_cgen_puts(w, ", ");
}
  first = 0;
  flowc_cgen_emit_expr(w, arena, src, el);
  el = ((arena).nodes[el]).next;
}
  flowc_cgen_puts(w, " }");
  return;
}
  flowc_cgen_puts(w, "0");
}

void flowc_cgen_emit_block(CgenBuf* w, AstArena arena, uint8_t* src, int32_t id) {
  if (id == AST_NONE || (w[0]).err != 0) {
  return;
}
  flowc_cgen_puts(w, "{\n");
  int32_t st = ((arena).nodes[id]).a;
  while (st != AST_NONE) {
  flowc_cgen_emit_stmt(w, arena, src, st);
  st = ((arena).nodes[st]).next;
}
  flowc_cgen_puts(w, "}\n");
}

void flowc_cgen_emit_stmt(CgenBuf* w, AstArena arena, uint8_t* src, int32_t id) {
  if (id == AST_NONE || (w[0]).err != 0) {
  return;
}
  int32_t kind = ((arena).nodes[id]).kind;
  if (kind == AST_LET) {
  int32_t ann = ((arena).nodes[id]).a;
  int32_t init = ((arena).nodes[id]).b;
  int32_t ty = ann;
  if (ann == AST_NONE) {
  ty = flowc_cgen_infer_type_node(arena, src, init);
}
  int32_t arr_n = 0;
  int32_t arr_inner = AST_NONE;
  if (ty != AST_NONE && ((arena).nodes[ty]).kind == AST_TYPE) {
  if (((arena).nodes[ty]).a != AST_NONE && ((arena).nodes[ty]).ival > 0) {
  if (flowc_cgen_span_is(src, ((arena).nodes[ty]).name_start, ((arena).nodes[ty]).name_end, "array") == 1) {
  arr_n = ((arena).nodes[ty]).ival;
  arr_inner = ((arena).nodes[ty]).a;
}
}
}
  flowc_cgen_puts(w, "  ");
  if (ty != AST_NONE && ((arena).nodes[ty]).kind == AST_TYPE && (((arena).nodes[ty]).ival == (0 - 1) || ((arena).nodes[ty]).ival == (0 - 2))) {
  flowc_cgen_emit_type(w, arena, src, ((arena).nodes[ty]).b);
  flowc_cgen_puts(w, " (*");
  flowc_cgen_put_span(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  flowc_cgen_puts(w, ")(");
  int32_t fparam = ((arena).nodes[ty]).a;
  int32_t ffirst = 1;
  while (fparam != AST_NONE) {
  if (ffirst == 0) {
  flowc_cgen_puts(w, ", ");
}
  flowc_cgen_emit_type(w, arena, src, fparam);
  ffirst = 0;
  fparam = ((arena).nodes[fparam]).next;
}
  flowc_cgen_putc(w, 41);
} else if (arr_n > 0) {
  flowc_cgen_emit_type(w, arena, src, arr_inner);
} else {
  int32_t wrote = 0;
  if (ty == AST_NONE) {
  wrote = flowc_cgen_write_lit_type(w, arena, src, init);
}
  if (wrote == 0) {
  flowc_cgen_emit_type(w, arena, src, ty);
}
}
  if (!(ty != AST_NONE && ((arena).nodes[ty]).kind == AST_TYPE && (((arena).nodes[ty]).ival == (0 - 1) || ((arena).nodes[ty]).ival == (0 - 2)))) {
  flowc_cgen_putc(w, 32);
  flowc_cgen_put_span(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
}
  if (arr_n > 0) {
  flowc_cgen_putc(w, 91);
  flowc_cgen_put_i32(w, arr_n);
  flowc_cgen_putc(w, 93);
}
  flowc_cgen_puts(w, " = ");
  int32_t cast_ptr = 0;
  if (ty != AST_NONE && ((arena).nodes[ty]).kind == AST_TYPE) {
  if (((arena).nodes[ty]).a != AST_NONE) {
  if (flowc_cgen_span_is(src, ((arena).nodes[ty]).name_start, ((arena).nodes[ty]).name_end, "ptr") == 1) {
  cast_ptr = 1;
}
}
}
  if (cast_ptr == 1) {
  flowc_cgen_putc(w, 40);
  flowc_cgen_emit_type(w, arena, src, ty);
  flowc_cgen_puts(w, ")(");
  flowc_cgen_emit_expr(w, arena, src, init);
  flowc_cgen_putc(w, 41);
} else {
  flowc_cgen_emit_expr(w, arena, src, init);
  if (init != AST_NONE && ((arena).nodes[init]).kind == AST_FLOAT) {
  if (ty != AST_NONE && ((arena).nodes[ty]).kind == AST_TYPE) {
  if (flowc_cgen_span_is(src, ((arena).nodes[ty]).name_start, ((arena).nodes[ty]).name_end, "f32") == 1) {
  flowc_cgen_putc(w, 102);
}
}
}
}
  flowc_cgen_puts(w, ";\n");
  return;
}
  if (kind == AST_RETURN) {
  if (((arena).nodes[id]).a == AST_NONE) {
  flowc_cgen_puts(w, "  return;\n");
  return;
}
  int32_t ret_expr = ((arena).nodes[id]).a;
  if (((arena).nodes[ret_expr]).kind == AST_IDENT) {
  if (flowc_cgen_span_is(src, ((arena).nodes[ret_expr]).name_start, ((arena).nodes[ret_expr]).name_end, "void") == 1) {
  flowc_cgen_puts(w, "  return;\n");
  return;
}
}
  flowc_cgen_puts(w, "  return ");
  flowc_cgen_emit_expr(w, arena, src, ret_expr);
  flowc_cgen_puts(w, ";\n");
  return;
}
  if (kind == AST_IF) {
  flowc_cgen_puts(w, "  if (");
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_cgen_puts(w, ") {\n");
  int32_t then_b = ((arena).nodes[id]).b;
  if (then_b != AST_NONE) {
  int32_t st = ((arena).nodes[then_b]).a;
  while (st != AST_NONE) {
  flowc_cgen_emit_stmt(w, arena, src, st);
  st = ((arena).nodes[st]).next;
}
}
  if (((arena).nodes[id]).c != AST_NONE) {
  flowc_cgen_puts(w, "} else {\n");
  int32_t else_b = ((arena).nodes[id]).c;
  int32_t est = ((arena).nodes[else_b]).a;
  while (est != AST_NONE) {
  flowc_cgen_emit_stmt(w, arena, src, est);
  est = ((arena).nodes[est]).next;
}
  flowc_cgen_puts(w, "}\n");
} else {
  flowc_cgen_puts(w, "}\n");
}
  return;
}
  if (kind == AST_WHILE) {
  flowc_cgen_puts(w, "  while (");
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_cgen_puts(w, ") ");
  flowc_cgen_emit_block(w, arena, src, ((arena).nodes[id]).b);
  return;
}
  if (kind == AST_FOR) {
  flowc_cgen_puts(w, "  for (int32_t ");
  flowc_cgen_put_span(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  flowc_cgen_puts(w, " = ");
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_cgen_puts(w, "; ");
  flowc_cgen_put_span(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  flowc_cgen_puts(w, " < ");
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).b);
  flowc_cgen_puts(w, "; ");
  flowc_cgen_put_span(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  flowc_cgen_puts(w, " = ");
  flowc_cgen_put_span(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  flowc_cgen_puts(w, " + 1) ");
  flowc_cgen_emit_block(w, arena, src, ((arena).nodes[id]).c);
  return;
}
  if (kind == AST_MATCH) {
  flowc_cgen_puts(w, "  { int32_t __flowc_match = ");
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_cgen_puts(w, ";\n");
  int32_t arm = ((arena).nodes[id]).b;
  int32_t n_lit = 0;
  int32_t chain_open = 0;
  while (arm != AST_NONE) {
  if (((arena).nodes[arm]).ival == 0) {
  if (n_lit == 0) {
  flowc_cgen_puts(w, "  if (__flowc_match == ");
} else {
  flowc_cgen_puts(w, "} else if (__flowc_match == ");
}
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[arm]).a);
  flowc_cgen_puts(w, ") {\n");
  n_lit = (n_lit + 1);
  chain_open = 1;
} else {
  if (n_lit > 0) {
  flowc_cgen_puts(w, "} else {\n");
}
  if (((arena).nodes[arm]).ival == 2) {
  flowc_cgen_puts(w, "  int32_t ");
  flowc_cgen_put_span(w, src, ((arena).nodes[arm]).name_start, ((arena).nodes[arm]).name_end);
  flowc_cgen_puts(w, " = __flowc_match;\n");
}
}
  int32_t body = ((arena).nodes[arm]).b;
  if (body != AST_NONE) {
  int32_t st = ((arena).nodes[body]).a;
  while (st != AST_NONE) {
  flowc_cgen_emit_stmt(w, arena, src, st);
  st = ((arena).nodes[st]).next;
}
}
  arm = ((arena).nodes[arm]).next;
}
  if (chain_open == 1) {
  flowc_cgen_puts(w, "}\n");
}
  flowc_cgen_puts(w, "  }\n");
  return;
}
  if (kind == AST_BREAK) {
  flowc_cgen_puts(w, "  break;\n");
  return;
}
  if (kind == AST_CONTINUE) {
  flowc_cgen_puts(w, "  continue;\n");
  return;
}
  if (kind == AST_ASSIGN) {
  flowc_cgen_puts(w, "  ");
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_cgen_puts(w, " = ");
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).b);
  flowc_cgen_puts(w, ";\n");
  return;
}
  if (kind == AST_EXPR_STMT) {
  flowc_cgen_puts(w, "  ");
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_cgen_puts(w, ";\n");
  return;
}
  if (kind == AST_BLOCK) {
  flowc_cgen_emit_block(w, arena, src, id);
  return;
}
}

void flowc_cgen_emit_param(CgenBuf* w, AstArena arena, uint8_t* src, int32_t id) {
  int32_t ty = ((arena).nodes[id]).a;
  if (ty != AST_NONE && ((arena).nodes[ty]).kind == AST_TYPE && (((arena).nodes[ty]).ival == (0 - 1) || ((arena).nodes[ty]).ival == (0 - 2))) {
  flowc_cgen_emit_type(w, arena, src, ((arena).nodes[ty]).b);
  flowc_cgen_puts(w, " (*");
  flowc_cgen_put_span(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  flowc_cgen_puts(w, ")(");
  int32_t param = ((arena).nodes[ty]).a;
  int32_t first = 1;
  while (param != AST_NONE) {
  if (first == 0) {
  flowc_cgen_puts(w, ", ");
}
  flowc_cgen_emit_type(w, arena, src, param);
  first = 0;
  param = ((arena).nodes[param]).next;
}
  flowc_cgen_putc(w, 41);
  return;
}
  flowc_cgen_emit_type(w, arena, src, ty);
  flowc_cgen_putc(w, 32);
  flowc_cgen_put_span(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
}

int32_t flowc_cgen_is_cli_main(AstArena arena, uint8_t* src, int32_t id) {
  if (flowc_cgen_span_is(src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end, "main") == 0) {
  return 0;
}
  int32_t n = 0;
  int32_t param = ((arena).nodes[id]).a;
  while (param != AST_NONE) {
  n = (n + 1);
  param = ((arena).nodes[param]).next;
}
  if (n == 2) {
  return 1;
}
  return 0;
}

int32_t flowc_cgen_is_cembed_fn(AstArena arena, uint8_t* src, int32_t root, int32_t fn_id) {
  int32_t ns = ((arena).nodes[fn_id]).name_start;
  int32_t ne = ((arena).nodes[fn_id]).name_end;
  if (ns < 0 || ne <= ns) { return 0; }
  int32_t item = ((arena).nodes[root]).a;
  while (item != AST_NONE) {
  if (((arena).nodes[item]).kind == AST_C_EMBED) {
  int32_t cs = ((arena).nodes[item]).name_start + 1;
  int32_t ce = ((arena).nodes[item]).name_end - 1;
  if (cs >= 0 && ce > cs) {
  int32_t len = (ne - ns);
  int32_t i = cs;
  while (i + len <= ce) {
  int32_t match = 1;
  int32_t j = 0;
  while (j < len) {
  if (src[i + j] != src[ns + j]) { match = 0; break; }
  j = (j + 1);
}
  if (match == 1) {
  if (i + len < ce) {
  uint8_t next_ch = src[i + len];
  if (next_ch == 40 || next_ch == 32) { return 1; }
  }
}
  i = (i + 1);
}
}
}
  item = ((arena).nodes[item]).next;
}
  return 0;
}

int32_t flowc_cgen_is_libc_fn(AstArena arena, uint8_t* src, int32_t id) {
  int32_t ns = ((arena).nodes[id]).name_start;
  int32_t ne = ((arena).nodes[id]).name_end;
  if (flowc_cgen_span_is(src, ns, ne, "fopen") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "fclose") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "fread") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "fwrite") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "fgets") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "fputs") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "fputc") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "fgetc") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "putc") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "getc") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "ungetc") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "fflush") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "feof") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "ferror") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "clearerr") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "rename") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "remove") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "tmpfile") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "fseek") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "ftell") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "printf") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "fprintf") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "sprintf") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "snprintf") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "vprintf") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "vfprintf") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "vsprintf") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "vsnprintf") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "puts") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "putchar") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "malloc") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "calloc") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "realloc") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "free") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "aligned_alloc") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "memmove") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "strlen") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "strcmp") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "strncmp") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "strcpy") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "strncpy") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "strcat") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "strchr") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "strrchr") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "strstr") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "memcpy") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "memset") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "memcmp") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "sin") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "cos") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "sqrt") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "fabs") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "pow") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "exp") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "log") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "log2") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "log10") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "floor") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "ceil") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "atan2") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "fmod") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "tanh") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "tan") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "asin") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "acos") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "atan") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "sinh") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "cosh") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "exit") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "abort") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "clock") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "time") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "qsort") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "rand") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "srand") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "getenv") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "system") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "abs") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "atoi") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "atof") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "strtol") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "strtod") == 1) {
  return 1;
}
  return 0;
}

void flowc_cgen_emit_fn(CgenBuf* w, AstArena arena, uint8_t* src, int32_t id) {
  int32_t cli_main = flowc_cgen_is_cli_main(arena, src, id);
  if (cli_main == 1) {
  int32_t p0 = ((arena).nodes[id]).a;
  int32_t p1 = ((arena).nodes[p0]).next;
  flowc_cgen_puts(w, "int main(int ");
  flowc_cgen_put_span(w, src, ((arena).nodes[p0]).name_start, ((arena).nodes[p0]).name_end);
  flowc_cgen_puts(w, ", char **");
  flowc_cgen_put_span(w, src, ((arena).nodes[p1]).name_start, ((arena).nodes[p1]).name_end);
  if (((arena).nodes[id]).c == AST_NONE) {
  flowc_cgen_puts(w, ");\n");
  return;
}
  flowc_cgen_puts(w, ") ");
  flowc_cgen_emit_block(w, arena, src, ((arena).nodes[id]).c);
  flowc_cgen_putc(w, 10);
  return;
}
  int32_t ret_ty = ((arena).nodes[id]).b;
  if (ret_ty == AST_NONE) {
  flowc_cgen_puts(w, "void");
} else {
  flowc_cgen_emit_type(w, arena, src, ret_ty);
}
  flowc_cgen_putc(w, 32);
  flowc_cgen_put_span(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  flowc_cgen_putc(w, 40);
  int32_t param = ((arena).nodes[id]).a;
  int32_t first = 1;
  while (param != AST_NONE) {
  if (first == 0) {
  flowc_cgen_puts(w, ", ");
}
  first = 0;
  flowc_cgen_emit_param(w, arena, src, param);
  param = ((arena).nodes[param]).next;
}
  if (((arena).nodes[id]).c == AST_NONE) {
  flowc_cgen_puts(w, ");\n");
  return;
}
  flowc_cgen_puts(w, ") ");
  flowc_cgen_emit_block(w, arena, src, ((arena).nodes[id]).c);
  flowc_cgen_putc(w, 10);
}

void flowc_cgen_emit_fn_proto(CgenBuf* w, AstArena arena, uint8_t* src, int32_t id) {
  int32_t cli_main = flowc_cgen_is_cli_main(arena, src, id);
  if (cli_main == 1) {
  int32_t p0 = ((arena).nodes[id]).a;
  int32_t p1 = ((arena).nodes[p0]).next;
  flowc_cgen_puts(w, "int main(int ");
  flowc_cgen_put_span(w, src, ((arena).nodes[p0]).name_start, ((arena).nodes[p0]).name_end);
  flowc_cgen_puts(w, ", char **");
  flowc_cgen_put_span(w, src, ((arena).nodes[p1]).name_start, ((arena).nodes[p1]).name_end);
  flowc_cgen_puts(w, ");\n");
  return;
}
  int32_t ret_ty = ((arena).nodes[id]).b;
  if (ret_ty == AST_NONE) {
  flowc_cgen_puts(w, "void");
} else {
  flowc_cgen_emit_type(w, arena, src, ret_ty);
}
  flowc_cgen_putc(w, 32);
  flowc_cgen_put_span(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  flowc_cgen_putc(w, 40);
  int32_t param = ((arena).nodes[id]).a;
  int32_t first = 1;
  while (param != AST_NONE) {
  if (first == 0) {
  flowc_cgen_puts(w, ", ");
}
  first = 0;
  flowc_cgen_emit_param(w, arena, src, param);
  param = ((arena).nodes[param]).next;
}
  flowc_cgen_puts(w, ");\n");
}

void flowc_cgen_emit_const(CgenBuf* w, AstArena arena, uint8_t* src, int32_t id) {
  if (((arena).nodes[id]).ival == 1) {
  flowc_cgen_puts(w, "const int32_t ");
} else {
  flowc_cgen_puts(w, "static const int32_t ");
}
  flowc_cgen_put_span(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  flowc_cgen_puts(w, " = ");
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).b);
  flowc_cgen_puts(w, ";\n");
}

void flowc_cgen_emit_struct(CgenBuf* w, AstArena arena, uint8_t* src, int32_t id) {
  flowc_cgen_puts(w, "typedef struct ");
  flowc_cgen_put_span(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  flowc_cgen_puts(w, " {\n");
  int32_t sns = ((arena).nodes[id]).name_start;
  int32_t sne = ((arena).nodes[id]).name_end;
  int32_t field = ((arena).nodes[id]).a;
  while (field != AST_NONE) {
  flowc_cgen_puts(w, "  ");
  int32_t fty = ((arena).nodes[field]).a;
  int32_t arr_n = 0;
  int32_t arr_inner = AST_NONE;
  if (fty != AST_NONE && ((arena).nodes[fty]).kind == AST_TYPE) {
  if (((arena).nodes[fty]).a != AST_NONE && ((arena).nodes[fty]).ival > 0) {
  if (flowc_cgen_span_is(src, ((arena).nodes[fty]).name_start, ((arena).nodes[fty]).name_end, "array") == 1) {
  arr_n = ((arena).nodes[fty]).ival;
  arr_inner = ((arena).nodes[fty]).a;
}
}
}
  int32_t emitted_self = 0;
  if (arr_n == 0 && fty != AST_NONE && ((arena).nodes[fty]).kind == AST_TYPE) {
  if (flowc_cgen_span_is(src, ((arena).nodes[fty]).name_start, ((arena).nodes[fty]).name_end, "ptr") == 1) {
  int32_t inner = ((arena).nodes[fty]).a;
  if (inner != AST_NONE && ((arena).nodes[inner]).kind == AST_TYPE) {
  if (flowc_cgen_span_eq(src, ((arena).nodes[inner]).name_start, ((arena).nodes[inner]).name_end, sns, sne) == 1) {
  flowc_cgen_puts(w, "struct ");
  flowc_cgen_put_span(w, src, sns, sne);
  flowc_cgen_putc(w, 42);
  emitted_self = 1;
}
}
}
}
  if (arr_n > 0) {
  if (arr_inner != AST_NONE && ((arena).nodes[arr_inner]).kind == AST_TYPE) {
  if (flowc_cgen_span_is(src, ((arena).nodes[arr_inner]).name_start, ((arena).nodes[arr_inner]).name_end, "ptr") == 1) {
  int32_t pinner = ((arena).nodes[arr_inner]).a;
  if (pinner != AST_NONE && ((arena).nodes[pinner]).kind == AST_TYPE) {
  if (flowc_cgen_span_eq(src, ((arena).nodes[pinner]).name_start, ((arena).nodes[pinner]).name_end, sns, sne) == 1) {
  flowc_cgen_puts(w, "struct ");
  flowc_cgen_put_span(w, src, sns, sne);
  flowc_cgen_putc(w, 42);
  flowc_cgen_putc(w, 32);
  flowc_cgen_put_span(w, src, ((arena).nodes[field]).name_start, ((arena).nodes[field]).name_end);
  flowc_cgen_putc(w, 91);
  flowc_cgen_put_i32(w, arr_n);
  flowc_cgen_putc(w, 93);
  flowc_cgen_puts(w, ";\n");
  field = ((arena).nodes[field]).next;
  continue;
}
}
}
}
  flowc_cgen_emit_type(w, arena, src, arr_inner);
} else {
  if (emitted_self == 0) {
  flowc_cgen_emit_type(w, arena, src, fty);
}
}
  flowc_cgen_putc(w, 32);
  flowc_cgen_put_span(w, src, ((arena).nodes[field]).name_start, ((arena).nodes[field]).name_end);
  if (arr_n > 0) {
  flowc_cgen_putc(w, 91);
  flowc_cgen_put_i32(w, arr_n);
  flowc_cgen_putc(w, 93);
}
  flowc_cgen_puts(w, ";\n");
  field = ((arena).nodes[field]).next;
}
  flowc_cgen_puts(w, "} ");
  flowc_cgen_put_span(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  flowc_cgen_puts(w, ";\n\n");
}

int32_t flowc_cgen_unwrap(AstArena arena, int32_t item, int32_t want) {
  if (item == AST_NONE) {
  return AST_NONE;
}
  if (((arena).nodes[item]).kind == want) {
  return item;
}
  if (((arena).nodes[item]).kind == AST_EXPORT) {
  int32_t inner = ((arena).nodes[item]).a;
  if (inner != AST_NONE && ((arena).nodes[inner]).kind == want) {
  return inner;
}
}
  return AST_NONE;
}

// Preprocess a C header and emit function prototypes into the CgenBuf.
// This runs cpp via popen, scans for function-like declarations, and
// emits them as C prototypes. Filters out keywords, uppercase names,
// and preprocessor artifacts.
int32_t flowc_cgen_pp_is_keyword(uint8_t* text, int32_t start, int32_t end);
int32_t flowc_cgen_pp_contains(uint8_t* text, int32_t start, int32_t end, const char* lit);
int32_t flowc_cgen_pp_is_macro_fn(uint8_t* text, int32_t start, int32_t end);
void flowc_cgen_emit_cimport(CgenBuf* w, uint8_t* src, int32_t name_start, int32_t name_end) {
  // Build command: echo '#include <header>' | cpp -P -
  uint8_t cmd[1024];
  int32_t cpos = 0;
  const char* prefix = "echo '#include <";
  int32_t plen = 0;
  while (prefix[plen] != 0 && cpos < 1023) { cmd[cpos] = prefix[plen]; cpos++; plen++; }
  int32_t hi = name_start + 1;
  while (hi < name_end - 1 && cpos < 1023) { cmd[cpos] = src[hi]; cpos++; hi++; }
  const char* suffix = ">' | cpp -P -";
  int32_t slen = 0;
  while (suffix[slen] != 0 && cpos < 1023) { cmd[cpos] = suffix[slen]; cpos++; slen++; }
  cmd[cpos] = 0;

  FILE* fp = popen((char*)cmd, "r");
  if (fp == 0) { return; }

  // Read preprocessed output
  uint8_t* pp_buf = (uint8_t*)(malloc(1048576));
  if (pp_buf == 0) { pclose(fp); return; }
  int32_t pp_len = 0;
  int32_t got = fread(pp_buf + pp_len, 1, 4096, fp);
  while (got > 0 && pp_len < 1048576 - 4096) {
  pp_len = pp_len + got;
  got = fread(pp_buf + pp_len, 1, 4096, fp);
}
  pclose(fp);

  // Also emit the #include so the prototypes match the system types
  flowc_cgen_puts(w, "#include <");
  flowc_cgen_put_span(w, src, name_start + 1, name_end - 1);
  flowc_cgen_puts(w, ">\n");

  // Scan for function declarations: type name(params);
  // Statements are semicolon-delimited (not line-delimited, since
  // cpp -P can split declarations across lines).
  int32_t pos = 0;
  while (pos < pp_len) {
  // Skip whitespace
  while (pos < pp_len && (pp_buf[pos] == 32 || pp_buf[pos] == 10 || pp_buf[pos] == 9 || pp_buf[pos] == 13)) {
  pos = pos + 1;
}
  if (pos >= pp_len) { break; }

  // Find end of statement (semicolon)
  int32_t line_start = pos;
  while (pos < pp_len && pp_buf[pos] != 59) {
  pos = pos + 1;
}
  int32_t line_end = pos;
  if (pos < pp_len && pp_buf[pos] == 59) { pos = pos + 1; }

  // Trim trailing whitespace/newlines from the statement
  while (line_end > line_start && (pp_buf[line_end - 1] == 10 || pp_buf[line_end - 1] == 13 || pp_buf[line_end - 1] == 32 || pp_buf[line_end - 1] == 9)) {
  line_end = line_end - 1;
}

  // Skip statements that contain braces (function bodies, not prototypes)
  int32_t has_brace = 0;
  int32_t scan_br = line_start;
  while (scan_br < line_end) {
  if (pp_buf[scan_br] == 123 || pp_buf[scan_br] == 125) { has_brace = 1; break; }
  scan_br = scan_br + 1;
}
  if (has_brace == 1) { continue; }

  // Check if this line has parens (function-like)
  int32_t paren_pos = 0 - 1;
  int32_t j = line_start;
  while (j < line_end) {
  if (pp_buf[j] == 40) { paren_pos = j; break; }
  j = j + 1;
}
  if (paren_pos < 0) { continue; }

  // Find matching close paren
  int32_t depth = 1;
  int32_t close_pos = paren_pos + 1;
  while (close_pos < line_end && depth > 0) {
  if (pp_buf[close_pos] == 40) { depth = depth + 1; }
  else { if (pp_buf[close_pos] == 41) { depth = depth - 1; } }
  close_pos = close_pos + 1;
}
  if (depth != 0) { continue; }
  close_pos = close_pos - 1;

  // Extract function name (last identifier before paren)
  int32_t fn_end = paren_pos;
  while (fn_end > line_start && (pp_buf[fn_end - 1] == 32 || pp_buf[fn_end - 1] == 9 || pp_buf[fn_end - 1] == 10 || pp_buf[fn_end - 1] == 13)) {
  fn_end = fn_end - 1;
}
  int32_t fn_start = fn_end;
  while (fn_start > line_start && ((pp_buf[fn_start - 1] >= 65 && pp_buf[fn_start - 1] <= 90) || (pp_buf[fn_start - 1] >= 97 && pp_buf[fn_start - 1] <= 122) || (pp_buf[fn_start - 1] >= 48 && pp_buf[fn_start - 1] <= 57) || pp_buf[fn_start - 1] == 95)) {
  fn_start = fn_start - 1;
}
  int32_t fn_len = fn_end - fn_start;
  if (fn_len <= 0) { continue; }

  // Skip double-underscore names
  if (fn_len >= 2 && pp_buf[fn_start] == 95 && pp_buf[fn_start + 1] == 95) { continue; }

  // Skip uppercase names (macro expansions)
  if (pp_buf[fn_start] >= 65 && pp_buf[fn_start] <= 90) { continue; }

  // Skip C keywords as function names
  if (flowc_cgen_pp_is_keyword(pp_buf, fn_start, fn_end) == 1) { continue; }

  // Skip functions that are macros in macOS secure headers
  if (flowc_cgen_pp_is_macro_fn(pp_buf, fn_start, fn_end) == 1) { continue; }

  // Return type is everything before the function name
  int32_t ret_end = fn_start;
  while (ret_end > line_start && (pp_buf[ret_end - 1] == 32 || pp_buf[ret_end - 1] == 9 || pp_buf[ret_end - 1] == 10 || pp_buf[ret_end - 1] == 13)) {
  ret_end = ret_end - 1;
}
  if (ret_end <= line_start) { continue; }

  // Skip if return type contains "defined"
  if (flowc_cgen_pp_contains(pp_buf, line_start, ret_end, "defined") == 1) { continue; }

  // Emit the prototype
  flowc_cgen_put_span(w, pp_buf, line_start, ret_end);
  flowc_cgen_putc(w, 32);
  flowc_cgen_put_span(w, pp_buf, fn_start, fn_end);
  flowc_cgen_putc(w, 40);
  flowc_cgen_put_span(w, pp_buf, paren_pos + 1, close_pos);
  flowc_cgen_puts(w, ");\n");
}

  free(pp_buf);
}

// Check if a span is a C keyword.
int32_t flowc_cgen_pp_is_keyword(uint8_t* text, int32_t start, int32_t end) {
  if (flowc_cgen_span_is(text, start, end, "void")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "int")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "char")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "long")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "short")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "float")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "double")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "unsigned")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "signed")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "const")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "struct")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "union")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "enum")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "typedef")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "static")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "extern")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "inline")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "return")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "if")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "else")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "while")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "for")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "do")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "switch")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "case")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "break")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "continue")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "default")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "sizeof")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "defined")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "goto")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "restrict")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "auto")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "register")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "volatile")) { return 1; }
  return 0;
}

// Check if a span contains a substring.
int32_t flowc_cgen_pp_contains(uint8_t* text, int32_t start, int32_t end, const char* lit) {
  int32_t lit_len = 0;
  while (lit[lit_len] != 0) { lit_len++; }
  if (lit_len <= 0 || end - start < lit_len) { return 0; }
  int32_t i = start;
  while (i + lit_len <= end) {
  int32_t is_match = 1;
  int32_t j = 0;
  while (j < lit_len) {
  if (text[i + j] != (uint8_t)(lit[j])) { is_match = 0; break; }
  j = j + 1;
}
  if (is_match == 1) { return 1; }
  i = i + 1;
}
  return 0;
}

// Check if a function name is a macro in macOS secure headers.
// These functions have inline macro wrappers that conflict with
// regular prototypes.
int32_t flowc_cgen_pp_is_macro_fn(uint8_t* text, int32_t start, int32_t end) {
  if (flowc_cgen_span_is(text, start, end, "memcpy")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "memmove")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "memset")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "memccpy")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "strcpy")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "strncpy")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "strcat")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "strncat")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "strlcpy")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "strlcat")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "stpcpy")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "stpncpy")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "sprintf")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "snprintf")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "vsprintf")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "vsnprintf")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "fprintf")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "vfprintf")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "printf")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "vprintf")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "asprintf")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "vasprintf")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "gets")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "fgets")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "fread")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "fwrite")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "strdup")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "bcopy")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "bzero")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "getc_unlocked")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "putc_unlocked")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "getchar_unlocked")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "putchar_unlocked")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "fputc")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "fputs")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "putc")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "getchar")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "putchar")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "fgetc")) { return 1; }
  if (flowc_cgen_span_is(text, start, end, "getc")) { return 1; }
  return 0;
}

int32_t flowc_cgen_emit_sigs(AstArena arena, int32_t root, uint8_t* src, uint8_t* out, int32_t out_cap, int32_t flags, uint8_t* sigs, int32_t sigs_len) {
  if (root == AST_NONE || root < 0) {
  return (0 - 1);
}
  if (((arena).nodes[root]).kind != AST_PROGRAM) {
  return (0 - 1);
}
  CgenBuf w = flowc_cgen_buf_init(out, out_cap);
  (w).sigs = sigs;
  (w).sigs_len = sigs_len;
  if ((flags % 2) == 0) {
  flowc_cgen_puts((&w), "#include <stdint.h>\n");
  flowc_cgen_puts((&w), "#include <stdbool.h>\n");
  flowc_cgen_puts((&w), "#include <stdlib.h>\n");
  flowc_cgen_puts((&w), "#include <stdio.h>\n");
  flowc_cgen_puts((&w), "#include <string.h>\n");
  flowc_cgen_puts((&w), "#include <math.h>\n");
  flowc_cgen_puts((&w), "#include <complex.h>\n");
  flowc_cgen_puts((&w), "typedef float complex c64;\n");
  flowc_cgen_puts((&w), "typedef double complex c128;\n");
  flowc_cgen_putc((&w), 10);
  flowc_cgen_puts((&w), "static inline const char* __flowc_str_concat(const char* a, const char* b) {\n");
  flowc_cgen_puts((&w), "  size_t la; size_t lb; char* r;\n");
  flowc_cgen_puts((&w), "  if (a == 0) { a = \"\"; }\n");
  flowc_cgen_puts((&w), "  if (b == 0) { b = \"\"; }\n");
  flowc_cgen_puts((&w), "  la = strlen(a); lb = strlen(b);\n");
  flowc_cgen_puts((&w), "  r = (char*)malloc(la + lb + 1);\n");
  flowc_cgen_puts((&w), "  if (r == 0) { return \"\"; }\n");
  flowc_cgen_puts((&w), "  memcpy(r, a, la); memcpy(r + la, b, lb); r[la + lb] = 0;\n");
  flowc_cgen_puts((&w), "  return r;\n");
  flowc_cgen_puts((&w), "}\n");
  flowc_cgen_putc((&w), 10);
}
  int32_t item = ((arena).nodes[root]).a;
  while (item != AST_NONE) {
  if (((arena).nodes[item]).kind == AST_C_INCLUDE) {
  flowc_cgen_puts((&w), "#include \"");
  flowc_cgen_put_span((&w), src, ((arena).nodes[item]).name_start + 1, ((arena).nodes[item]).name_end - 1);
  flowc_cgen_puts((&w), "\"\n");
}
  if (((arena).nodes[item]).kind == AST_C_IMPORT) {
  flowc_cgen_emit_cimport((&w), src, ((arena).nodes[item]).name_start, ((arena).nodes[item]).name_end);
}
  item = ((arena).nodes[item]).next;
}
  item = ((arena).nodes[root]).a;
  while (item != AST_NONE) {
  if (((arena).nodes[item]).kind == AST_C_EMBED) {
  flowc_cgen_put_span((&w), src, ((arena).nodes[item]).name_start + 1, ((arena).nodes[item]).name_end - 1);
  flowc_cgen_putc((&w), 10);
}
  item = ((arena).nodes[item]).next;
}
  item = ((arena).nodes[root]).a;
  while (item != AST_NONE) {
  if (((arena).nodes[item]).kind == AST_EXTERN_TYPE) {
  flowc_cgen_puts((&w), "typedef struct ");
  flowc_cgen_put_span((&w), src, ((arena).nodes[item]).name_start, ((arena).nodes[item]).name_end);
  flowc_cgen_putc((&w), 32);
  flowc_cgen_put_span((&w), src, ((arena).nodes[item]).name_start, ((arena).nodes[item]).name_end);
  flowc_cgen_puts((&w), ";\n");
}
  item = ((arena).nodes[item]).next;
}
  item = ((arena).nodes[root]).a;
  while (item != AST_NONE) {
  int32_t st = flowc_cgen_unwrap(arena, item, AST_STRUCT);
  if (st != AST_NONE) {
  flowc_cgen_emit_struct((&w), arena, src, st);
}
  item = ((arena).nodes[item]).next;
}
  item = ((arena).nodes[root]).a;
  while (item != AST_NONE) {
  if (((arena).nodes[item]).kind == AST_TYPE_ALIAS) {
  flowc_cgen_puts((&w), "typedef ");
  flowc_cgen_emit_type((&w), arena, src, ((arena).nodes[item]).a);
  flowc_cgen_putc((&w), 32);
  flowc_cgen_put_span((&w), src, ((arena).nodes[item]).name_start, ((arena).nodes[item]).name_end);
  flowc_cgen_puts((&w), ";\n");
}
  item = ((arena).nodes[item]).next;
}
  item = ((arena).nodes[root]).a;
  while (item != AST_NONE) {
  if (((arena).nodes[item]).kind == AST_CONST) {
  flowc_cgen_emit_const((&w), arena, src, item);
}
  item = ((arena).nodes[item]).next;
}
  item = ((arena).nodes[root]).a;
  while (item != AST_NONE) {
  if (((arena).nodes[item]).kind == AST_LET) {
  int32_t ann = ((arena).nodes[item]).a;
  int32_t init = ((arena).nodes[item]).b;
  int32_t ty = ann;
  if (ann == AST_NONE) {
  ty = flowc_cgen_infer_type_node(arena, src, init);
}
  int32_t arr_n = 0;
  int32_t arr_inner = AST_NONE;
  if (ty != AST_NONE && ((arena).nodes[ty]).kind == AST_TYPE) {
  if (((arena).nodes[ty]).a != AST_NONE && ((arena).nodes[ty]).ival > 0) {
  if (flowc_cgen_span_is(src, ((arena).nodes[ty]).name_start, ((arena).nodes[ty]).name_end, "array") == 1) {
  arr_n = ((arena).nodes[ty]).ival;
  arr_inner = ((arena).nodes[ty]).a;
}
}
}
  flowc_cgen_puts((&w), "static ");
  if (arr_n > 0) {
  flowc_cgen_emit_type((&w), arena, src, arr_inner);
} else {
  flowc_cgen_emit_type((&w), arena, src, ty);
}
  flowc_cgen_putc((&w), 32);
  flowc_cgen_put_span((&w), src, ((arena).nodes[item]).name_start, ((arena).nodes[item]).name_end);
  if (arr_n > 0) {
  flowc_cgen_putc((&w), 91);
  flowc_cgen_put_i32((&w), arr_n);
  flowc_cgen_putc((&w), 93);
}
  if (init != AST_NONE) {
  flowc_cgen_puts((&w), " = ");
  flowc_cgen_emit_expr((&w), arena, src, init);
}
  flowc_cgen_puts((&w), ";\n");
}
  item = ((arena).nodes[item]).next;
}
  item = ((arena).nodes[root]).a;
  while (item != AST_NONE) {
  if (((arena).nodes[item]).kind == AST_EXTERN) {
  int32_t ef = ((arena).nodes[item]).a;
  while (ef != AST_NONE) {
  if (((arena).nodes[ef]).kind == AST_EXTERN_TYPE) {
  flowc_cgen_puts((&w), "typedef struct ");
  flowc_cgen_put_span((&w), src, ((arena).nodes[ef]).name_start, ((arena).nodes[ef]).name_end);
  flowc_cgen_putc((&w), 32);
  flowc_cgen_put_span((&w), src, ((arena).nodes[ef]).name_start, ((arena).nodes[ef]).name_end);
  flowc_cgen_puts((&w), ";\n");
}
  if (((arena).nodes[ef]).kind == AST_FN) {
  if (flowc_cgen_is_libc_fn(arena, src, ef) == 0 && flowc_cgen_is_cembed_fn(arena, src, root, ef) == 0) {
  flowc_cgen_emit_fn((&w), arena, src, ef);
}
}
  ef = ((arena).nodes[ef]).next;
}
}
  if (((arena).nodes[item]).kind == AST_EXTERN_TYPE) {
  flowc_cgen_puts((&w), "typedef struct ");
  flowc_cgen_put_span((&w), src, ((arena).nodes[item]).name_start, ((arena).nodes[item]).name_end);
  flowc_cgen_putc((&w), 32);
  flowc_cgen_put_span((&w), src, ((arena).nodes[item]).name_start, ((arena).nodes[item]).name_end);
  flowc_cgen_puts((&w), ";\n");
}
  item = ((arena).nodes[item]).next;
}
  item = ((arena).nodes[root]).a;
  while (item != AST_NONE) {
  int32_t fn = flowc_cgen_unwrap(arena, item, AST_FN);
  if (fn != AST_NONE) {
  if (((arena).nodes[fn]).ival == 0 && ((arena).nodes[fn]).c != AST_NONE) {
  if (flowc_cgen_is_libc_fn(arena, src, fn) == 0) {
  flowc_cgen_emit_fn_proto((&w), arena, src, fn);
}
}
}
  item = ((arena).nodes[item]).next;
}
  item = ((arena).nodes[root]).a;
  while (item != AST_NONE) {
  int32_t fn = flowc_cgen_unwrap(arena, item, AST_FN);
  if (fn != AST_NONE) {
  if (((arena).nodes[fn]).ival == 0) {
  if (flowc_cgen_is_libc_fn(arena, src, fn) == 0) {
  flowc_cgen_emit_fn((&w), arena, src, fn);
}
}
}
  item = ((arena).nodes[item]).next;
}
  if ((w).err != 0) {
  return (0 - 1);
}
  return (w).len;
}

int32_t flowc_cgen_emit_ex(AstArena arena, int32_t root, uint8_t* src, uint8_t* out, int32_t out_cap, int32_t flags) {
  return flowc_cgen_emit_sigs(arena, root, src, out, out_cap, flags, NULL, 0);
}

int32_t flowc_cgen_emit(AstArena arena, int32_t root, uint8_t* src, uint8_t* out, int32_t out_cap) {
  return flowc_cgen_emit_sigs(arena, root, src, out, out_cap, 0, NULL, 0);
}

int32_t flowc_cgen_collect_sigs(AstArena arena, int32_t root, uint8_t* src, uint8_t* buf, int32_t cap, int32_t len) {
  if (buf == NULL || root == AST_NONE || root < 0) {
  return len;
}
  if (((arena).nodes[root]).kind != AST_PROGRAM) {
  return len;
}
  int32_t n = len;
  int32_t item = ((arena).nodes[root]).a;
  while (item != AST_NONE) {
  int32_t fn = flowc_cgen_unwrap(arena, item, AST_FN);
  if (fn != AST_NONE) {
  int32_t rt = ((arena).nodes[fn]).b;
  if (rt != AST_NONE) {
  n = flowc_cgen_sig_put(arena, src, buf, cap, n, fn, rt);
}
}
  item = ((arena).nodes[item]).next;
}
  return n;
}


typedef struct TcCtx {
  uint8_t* src;
  int32_t* ns;
  int32_t* ne;
  int32_t* nk;
  int32_t* na;
  int32_t nlen;
  int32_t ncap;
  int32_t* marks;
  int32_t mlen;
  int32_t mcap;
  int32_t err;
  int32_t cur_ret;
  int32_t loop_depth;
  int32_t has_extern;
  int32_t lenient;
  uint8_t* seed_buf;
  int32_t seed_cap;
  int32_t seed_len;
  int32_t seed_nlen;
  const char* path;
} TcCtx;

int32_t flowc_tc_span_eq(uint8_t* src, int32_t a0, int32_t a1, int32_t b0, int32_t b1) {
  if ((a1 - a0) != (b1 - b0)) {
  return 0;
}
  int32_t i = 0;
  int32_t n = (a1 - a0);
  while (i < n) {
  if (src[(a0 + i)] != src[(b0 + i)]) {
  return 0;
}
  i = (i + 1);
}
  return 1;
}

int32_t flowc_tc_span_eq2(uint8_t* src_a, int32_t a0, int32_t a1, uint8_t* src_b, int32_t b0, int32_t b1) {
  if ((a1 - a0) != (b1 - b0)) {
  return 0;
}
  int32_t i = 0;
  int32_t n = (a1 - a0);
  while (i < n) {
  if (src_a[(a0 + i)] != src_b[(b0 + i)]) {
  return 0;
}
  i = (i + 1);
}
  return 1;
}

uint8_t* flowc_tc_bind_src(TcCtx ctx, int32_t i) {
  if (i < (ctx).seed_nlen) {
  return (ctx).seed_buf;
}
  return (ctx).src;
}

int32_t flowc_tc_name_eq(TcCtx ctx, int32_t start, int32_t end, int32_t i) {
  return flowc_tc_span_eq2((ctx).src, start, end, flowc_tc_bind_src(ctx, i), (ctx).ns[i], (ctx).ne[i]);
}

int32_t flowc_tc_span_is(uint8_t* src, int32_t start, int32_t end, const char* lit) {
  uint8_t* p = (uint8_t*)(lit);
  int32_t n = (int32_t)(strlen(lit));
  if ((end - start) != n) {
  return 0;
}
  int32_t i = 0;
  while (i < n) {
  if (src[(start + i)] != p[i]) {
  return 0;
}
  i = (i + 1);
}
  return 1;
}

void flowc_tc_err(TcCtx* ctx) {
  (ctx[0]).err = ((ctx[0]).err + 1);
}

void flowc_tc_note(TcCtx* ctx, const char* label, int32_t start, int32_t end) {
  puts(label);
  const char* path = (ctx[0]).path;
  if (path != NULL) {
  int64_t plen = strlen(path);
  if (plen > 0) {
  puts("flowc tc: file");
  puts(path);
}
}
  uint8_t* src = (uint8_t*)((ctx[0]).src);
  if (src == NULL) {
  return;
}
  int32_t line = 1;
  int32_t col = 1;
  int32_t i = 0;
  while (i < start) {
  if (src[i] == 10) {
  line = (line + 1);
  col = 1;
} else {
  col = (col + 1);
}
  i = (i + 1);
}
  printf("flowc tc: at %d", line);
  printf(":%d\n", col);
  if (end <= start) {
  return;
}
  int32_t n = (end - start);
  if (n > 120) {
  n = 120;
}
  uint8_t* buf = (uint8_t*)(malloc((int64_t)((n + 1))));
  if (buf == NULL) {
  return;
}
  i = 0;
  while (i < n) {
  buf[i] = src[(start + i)];
  i = (i + 1);
}
  buf[n] = 0;
  const char* s = buf;
  puts(s);
  free(buf);
}

void flowc_tc_push_mark(TcCtx* ctx) {
  if ((ctx[0]).mlen < (ctx[0]).mcap) {
  (ctx[0]).marks[(ctx[0]).mlen] = (ctx[0]).nlen;
  (ctx[0]).mlen = ((ctx[0]).mlen + 1);
}
}

void flowc_tc_pop_mark(TcCtx* ctx) {
  if ((ctx[0]).mlen > 0) {
  (ctx[0]).mlen = ((ctx[0]).mlen - 1);
  (ctx[0]).nlen = (ctx[0]).marks[(ctx[0]).mlen];
}
}

void flowc_tc_bind(TcCtx* ctx, int32_t start, int32_t end, int32_t kind, int32_t arity) {
  if ((ctx[0]).nlen >= (ctx[0]).ncap) {
  puts("flowc tc: name table full (raise ncap)");
  flowc_tc_err(ctx);
  return;
}
  int32_t i = (ctx[0]).nlen;
  (ctx[0]).ns[i] = start;
  (ctx[0]).ne[i] = end;
  (ctx[0]).nk[i] = kind;
  (ctx[0]).na[i] = arity;
  (ctx[0]).nlen = (i + 1);
}

int32_t flowc_tc_lookup(TcCtx ctx, int32_t start, int32_t end) {
  if (flowc_tc_span_is((ctx).src, start, end, "null") == 1) {
  return 1;
}
  int32_t i = (ctx).nlen;
  while (i > 0) {
  i = (i - 1);
  if (flowc_tc_name_eq(ctx, start, end, i) == 1) {
  return 1;
}
}
  return 0;
}

int32_t flowc_tc_lookup_local(TcCtx ctx, int32_t start, int32_t end) {
  int32_t base = 0;
  if ((ctx).mlen > 0) {
  base = (ctx).marks[((ctx).mlen - 1)];
}
  int32_t i = (ctx).nlen;
  while (i > base) {
  i = (i - 1);
  if ((ctx).nk[i] == 0) {
  if (flowc_tc_name_eq(ctx, start, end, i) == 1) {
  return 1;
}
}
}
  return 0;
}

int32_t flowc_tc_lookup_val_type(TcCtx ctx, int32_t start, int32_t end) {
  int32_t i = (ctx).nlen;
  while (i > 0) {
  i = (i - 1);
  if ((ctx).nk[i] == 0) {
  if (flowc_tc_name_eq(ctx, start, end, i) == 1) {
  return (ctx).na[i];
}
}
}
  return AST_NONE;
}

void flowc_tc_bind_value(TcCtx* ctx, int32_t start, int32_t end, int32_t ty) {
  if (flowc_tc_lookup_local(ctx[0], start, end) == 1) {
  flowc_tc_err(ctx);
}
  flowc_tc_bind(ctx, start, end, 0, ty);
}

int32_t flowc_tc_find_struct(AstArena arena, uint8_t* src, int32_t ty) {
  if (ty == AST_NONE) {
  return AST_NONE;
}
  if (((arena).nodes[ty]).kind != AST_TYPE) {
  return AST_NONE;
}
  int32_t ts = ((arena).nodes[ty]).name_start;
  int32_t te = ((arena).nodes[ty]).name_end;
  int32_t i = 0;
  while (i < (arena).len) {
  if (((arena).nodes[i]).kind == AST_STRUCT) {
  if (flowc_tc_span_eq(src, ts, te, ((arena).nodes[i]).name_start, ((arena).nodes[i]).name_end) == 1) {
  return i;
}
}
  i = (i + 1);
}
  return AST_NONE;
}

int32_t flowc_tc_find_struct_by_name(AstArena arena, uint8_t* src, int32_t ns, int32_t ne) {
  int32_t i = 0;
  while (i < (arena).len) {
  if (((arena).nodes[i]).kind == AST_STRUCT) {
  if (flowc_tc_span_eq(src, ns, ne, ((arena).nodes[i]).name_start, ((arena).nodes[i]).name_end) == 1) {
  return i;
}
}
  i = (i + 1);
}
  return AST_NONE;
}

int32_t flowc_tc_struct_has_field(AstArena arena, uint8_t* src, int32_t st, int32_t fs, int32_t fe) {
  if (st == AST_NONE) {
  return 0;
}
  int32_t field = ((arena).nodes[st]).a;
  while (field != AST_NONE) {
  if (flowc_tc_span_eq(src, fs, fe, ((arena).nodes[field]).name_start, ((arena).nodes[field]).name_end) == 1) {
  return 1;
}
  field = ((arena).nodes[field]).next;
}
  return 0;
}

int32_t flowc_tc_lookup_fn(TcCtx ctx, int32_t start, int32_t end) {
  if (flowc_tc_span_is((ctx).src, start, end, "println") == 1) {
  return 1;
}
  if (flowc_tc_span_is((ctx).src, start, end, "print") == 1) {
  return 1;
}
  if (flowc_tc_span_is((ctx).src, start, end, "puts") == 1) {
  return 1;
}
  int32_t i = (ctx).nlen;
  while (i > 0) {
  i = (i - 1);
  if ((ctx).nk[i] == 1) {
  if (flowc_tc_name_eq(ctx, start, end, i) == 1) {
  return 1;
}
}
}
  return 0;
}

int32_t flowc_tc_lookup_fn_arity(TcCtx ctx, int32_t start, int32_t end) {
  int32_t i = (ctx).nlen;
  while (i > 0) {
  i = (i - 1);
  if ((ctx).nk[i] == 1) {
  if (flowc_tc_name_eq(ctx, start, end, i) == 1) {
  return (ctx).na[i];
}
}
}
  return (-1);
}

int32_t flowc_tc_unwrap_fn(AstArena arena, int32_t item) {
  if (item == AST_NONE) {
  return AST_NONE;
}
  if (((arena).nodes[item]).kind == AST_FN) {
  return item;
}
  if (((arena).nodes[item]).kind == AST_EXPORT) {
  int32_t inner = ((arena).nodes[item]).a;
  if (inner != AST_NONE && ((arena).nodes[inner]).kind == AST_FN) {
  return inner;
}
}
  return AST_NONE;
}

int32_t flowc_tc_is_i32_type(AstArena arena, uint8_t* src, int32_t ty) {
  if (ty == AST_NONE) {
  return 0;
}
  if (((arena).nodes[ty]).kind != AST_TYPE) {
  return 0;
}
  return flowc_tc_span_is(src, ((arena).nodes[ty]).name_start, ((arena).nodes[ty]).name_end, "i32");
}

int32_t flowc_tc_is_void_ret(AstArena arena, uint8_t* src, int32_t ty) {
  if (ty == AST_NONE) {
  return 1;
}
  if (((arena).nodes[ty]).kind != AST_TYPE) {
  return 0;
}
  return flowc_tc_span_is(src, ((arena).nodes[ty]).name_start, ((arena).nodes[ty]).name_end, "void");
}

int32_t flowc_tc_obvious_non_i32(AstArena arena, int32_t id) {
  if (id == AST_NONE) {
  return 0;
}
  if (((arena).nodes[id]).kind == AST_STRING) {
  return 1;
}
  return 0;
}

void flowc_tc_check_expr(TcCtx* ctx, AstArena arena, int32_t id);
void flowc_tc_check_stmt(TcCtx* ctx, AstArena arena, int32_t id);
void flowc_tc_check_block(TcCtx* ctx, AstArena arena, int32_t id);
void flowc_tc_check_expr(TcCtx* ctx, AstArena arena, int32_t id) {
  if (id == AST_NONE) {
  return;
}
  int32_t kind = ((arena).nodes[id]).kind;
  if (kind == AST_INT || kind == AST_BOOL || kind == AST_STRING || kind == AST_FLOAT) {
  return;
}
  if (kind == AST_IDENT) {
  int32_t ns = ((arena).nodes[id]).name_start;
  int32_t ne = ((arena).nodes[id]).name_end;
  if (flowc_tc_lookup(ctx[0], ns, ne) == 0) {
  if (flowc_tc_lookup_fn(ctx[0], ns, ne) == 0 && (ctx[0]).has_extern == 0) {
  flowc_tc_note(ctx, "flowc tc: unbound ident", ns, ne);
  flowc_tc_err(ctx);
}
}
  return;
}
  if (kind == AST_CALL) {
  int32_t ns = ((arena).nodes[id]).name_start;
  int32_t ne = ((arena).nodes[id]).name_end;
  if (flowc_tc_lookup_fn(ctx[0], ns, ne) == 0) {
  if ((ctx[0]).has_extern == 0) {
  flowc_tc_note(ctx, "flowc tc: unbound call", ns, ne);
  flowc_tc_err(ctx);
}
} else {
  int32_t arity = flowc_tc_lookup_fn_arity(ctx[0], ns, ne);
  if (arity >= 0) {
  int32_t nargs = flowc_ast_chain_len(arena, ((arena).nodes[id]).a);
  if (nargs != arity) {
  flowc_tc_note(ctx, "flowc tc: arity mismatch", ns, ne);
  flowc_tc_err(ctx);
}
}
}
  int32_t arg = ((arena).nodes[id]).a;
  while (arg != AST_NONE) {
  flowc_tc_check_expr(ctx, arena, arg);
  arg = ((arena).nodes[arg]).next;
}
  return;
}
  if (kind == AST_BINOP) {
  flowc_tc_check_expr(ctx, arena, ((arena).nodes[id]).a);
  flowc_tc_check_expr(ctx, arena, ((arena).nodes[id]).b);
  return;
}
  if (kind == AST_UNARY) {
  flowc_tc_check_expr(ctx, arena, ((arena).nodes[id]).a);
  return;
}
  if (kind == AST_FIELD_ACCESS) {
  int32_t base = ((arena).nodes[id]).a;
  flowc_tc_check_expr(ctx, arena, base);
  if (base != AST_NONE && ((arena).nodes[base]).kind == AST_IDENT) {
  int32_t ty = flowc_tc_lookup_val_type(ctx[0], ((arena).nodes[base]).name_start, ((arena).nodes[base]).name_end);
  int32_t st = flowc_tc_find_struct(arena, (ctx[0]).src, ty);
  if (st != AST_NONE) {
  int32_t fs = ((arena).nodes[id]).name_start;
  int32_t fe = ((arena).nodes[id]).name_end;
  if (flowc_tc_struct_has_field(arena, (ctx[0]).src, st, fs, fe) == 0) {
  flowc_tc_err(ctx);
}
}
}
  return;
}
  if (kind == AST_INDEX) {
  flowc_tc_check_expr(ctx, arena, ((arena).nodes[id]).a);
  flowc_tc_check_expr(ctx, arena, ((arena).nodes[id]).b);
  return;
}
  if (kind == AST_CAST) {
  flowc_tc_check_expr(ctx, arena, ((arena).nodes[id]).a);
  return;
}
  if (kind == AST_STRUCT_LIT) {
  int32_t st = flowc_tc_find_struct_by_name(arena, (ctx[0]).src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  int32_t field = ((arena).nodes[id]).a;
  while (field != AST_NONE) {
  if (st != AST_NONE) {
  int32_t fs = ((arena).nodes[field]).name_start;
  int32_t fe = ((arena).nodes[field]).name_end;
  if (flowc_tc_struct_has_field(arena, (ctx[0]).src, st, fs, fe) == 0) {
  flowc_tc_err(ctx);
}
}
  flowc_tc_check_expr(ctx, arena, ((arena).nodes[field]).a);
  field = ((arena).nodes[field]).next;
}
  return;
}
  if (kind == AST_ARRAY_LIT) {
  int32_t el = ((arena).nodes[id]).a;
  while (el != AST_NONE) {
  flowc_tc_check_expr(ctx, arena, el);
  el = ((arena).nodes[el]).next;
}
  return;
}
}

void flowc_tc_check_block(TcCtx* ctx, AstArena arena, int32_t id) {
  if (id == AST_NONE) {
  return;
}
  if (((arena).nodes[id]).kind != AST_BLOCK) {
  return;
}
  flowc_tc_push_mark(ctx);
  int32_t st = ((arena).nodes[id]).a;
  while (st != AST_NONE) {
  flowc_tc_check_stmt(ctx, arena, st);
  st = ((arena).nodes[st]).next;
}
  flowc_tc_pop_mark(ctx);
}

void flowc_tc_check_stmt(TcCtx* ctx, AstArena arena, int32_t id) {
  if (id == AST_NONE) {
  return;
}
  int32_t kind = ((arena).nodes[id]).kind;
  if (kind == AST_LET) {
  flowc_tc_check_expr(ctx, arena, ((arena).nodes[id]).b);
  int32_t ty = ((arena).nodes[id]).a;
  flowc_tc_bind_value(ctx, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end, ty);
  return;
}
  if (kind == AST_RETURN) {
  int32_t val = ((arena).nodes[id]).a;
  int32_t is_void = flowc_tc_is_void_ret(arena, (ctx[0]).src, (ctx[0]).cur_ret);
  if (val == AST_NONE) {
  if (is_void == 0) {
  flowc_tc_err(ctx);
}
} else {
  if (is_void == 1) {
  flowc_tc_err(ctx);
}
  flowc_tc_check_expr(ctx, arena, val);
  if (flowc_tc_is_i32_type(arena, (ctx[0]).src, (ctx[0]).cur_ret) == 1) {
  if (flowc_tc_obvious_non_i32(arena, val) == 1) {
  flowc_tc_err(ctx);
}
}
}
  return;
}
  if (kind == AST_IF) {
  flowc_tc_check_expr(ctx, arena, ((arena).nodes[id]).a);
  flowc_tc_check_block(ctx, arena, ((arena).nodes[id]).b);
  flowc_tc_check_block(ctx, arena, ((arena).nodes[id]).c);
  return;
}
  if (kind == AST_WHILE) {
  flowc_tc_check_expr(ctx, arena, ((arena).nodes[id]).a);
  (ctx[0]).loop_depth = ((ctx[0]).loop_depth + 1);
  flowc_tc_check_block(ctx, arena, ((arena).nodes[id]).b);
  (ctx[0]).loop_depth = ((ctx[0]).loop_depth - 1);
  return;
}
  if (kind == AST_FOR) {
  flowc_tc_check_expr(ctx, arena, ((arena).nodes[id]).a);
  flowc_tc_check_expr(ctx, arena, ((arena).nodes[id]).b);
  flowc_tc_push_mark(ctx);
  flowc_tc_bind(ctx, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end, 0, (-1));
  (ctx[0]).loop_depth = ((ctx[0]).loop_depth + 1);
  flowc_tc_check_block(ctx, arena, ((arena).nodes[id]).c);
  (ctx[0]).loop_depth = ((ctx[0]).loop_depth - 1);
  flowc_tc_pop_mark(ctx);
  return;
}
  if (kind == AST_MATCH) {
  int32_t scrut = ((arena).nodes[id]).a;
  flowc_tc_check_expr(ctx, arena, scrut);
  if (scrut != AST_NONE) {
  int32_t sk = ((arena).nodes[scrut]).kind;
  if (sk == AST_STRING || sk == AST_FLOAT) {
  flowc_tc_note(ctx, "flowc tc: match scrutinee must be integer-typed", ((arena).nodes[scrut]).start, ((arena).nodes[scrut]).end);
  flowc_tc_err(ctx);
}
  if (sk == AST_IDENT) {
  int32_t sty = flowc_tc_lookup_val_type(ctx[0], ((arena).nodes[scrut]).name_start, ((arena).nodes[scrut]).name_end);
  if (sty != AST_NONE && ((arena).nodes[sty]).kind == AST_TYPE) {
  int32_t tns = ((arena).nodes[sty]).name_start;
  int32_t tne = ((arena).nodes[sty]).name_end;
  int32_t bad = 0;
  if (flowc_tc_span_is((ctx[0]).src, tns, tne, "string") == 1) {
  bad = 1;
}
  if (flowc_tc_span_is((ctx[0]).src, tns, tne, "f32") == 1) {
  bad = 1;
}
  if (flowc_tc_span_is((ctx[0]).src, tns, tne, "f64") == 1) {
  bad = 1;
}
  if (bad == 1) {
  flowc_tc_note(ctx, "flowc tc: match scrutinee must be integer-typed", ((arena).nodes[scrut]).name_start, ((arena).nodes[scrut]).name_end);
  flowc_tc_err(ctx);
}
}
}
}
  int32_t arm = ((arena).nodes[id]).b;
  while (arm != AST_NONE) {
  if (((arena).nodes[arm]).ival != 0 && ((arena).nodes[arm]).next != AST_NONE) {
  flowc_tc_note(ctx, "flowc tc: catch-all match arm must be last", ((arena).nodes[arm]).start, ((arena).nodes[arm]).end);
  flowc_tc_err(ctx);
}
  flowc_tc_push_mark(ctx);
  if (((arena).nodes[arm]).ival == 2) {
  flowc_tc_bind(ctx, ((arena).nodes[arm]).name_start, ((arena).nodes[arm]).name_end, 0, (-1));
}
  flowc_tc_check_block(ctx, arena, ((arena).nodes[arm]).b);
  flowc_tc_pop_mark(ctx);
  arm = ((arena).nodes[arm]).next;
}
  return;
}
  if (kind == AST_ASSIGN) {
  int32_t lhs = ((arena).nodes[id]).a;
  if (lhs != AST_NONE && ((arena).nodes[lhs]).kind == AST_IDENT) {
  int32_t ns = ((arena).nodes[lhs]).name_start;
  int32_t ne = ((arena).nodes[lhs]).name_end;
  if (flowc_tc_lookup(ctx[0], ns, ne) == 0) {
  flowc_tc_err(ctx);
}
} else {
  flowc_tc_check_expr(ctx, arena, lhs);
}
  flowc_tc_check_expr(ctx, arena, ((arena).nodes[id]).b);
  return;
}
  if (kind == AST_BREAK || kind == AST_CONTINUE) {
  if ((ctx[0]).loop_depth <= 0) {
  flowc_tc_err(ctx);
}
  return;
}
  if (kind == AST_EXPR_STMT) {
  flowc_tc_check_expr(ctx, arena, ((arena).nodes[id]).a);
  return;
}
  if (kind == AST_BLOCK) {
  flowc_tc_check_block(ctx, arena, id);
  return;
}
}

void flowc_tc_collect_globals(TcCtx* ctx, AstArena arena, int32_t root) {
  int32_t item = ((arena).nodes[root]).a;
  while (item != AST_NONE) {
  int32_t kind = ((arena).nodes[item]).kind;
  if (kind == AST_EXTERN) {
  (ctx[0]).has_extern = 1;
}
  if (kind == AST_CONST) {
  int32_t ty = ((arena).nodes[item]).a;
  flowc_tc_bind_value(ctx, ((arena).nodes[item]).name_start, ((arena).nodes[item]).name_end, ty);
}
  if (kind == AST_LET) {
  int32_t ty = ((arena).nodes[item]).a;
  flowc_tc_bind_value(ctx, ((arena).nodes[item]).name_start, ((arena).nodes[item]).name_end, ty);
}
  if (kind == AST_IMPORT) {
  int32_t nm = ((arena).nodes[item]).a;
  while (nm != AST_NONE) {
  flowc_tc_bind(ctx, ((arena).nodes[nm]).name_start, ((arena).nodes[nm]).name_end, 1, (-1));
  flowc_tc_bind(ctx, ((arena).nodes[nm]).name_start, ((arena).nodes[nm]).name_end, 0, (-1));
  nm = ((arena).nodes[nm]).next;
}
}
  int32_t fn = flowc_tc_unwrap_fn(arena, item);
  if (fn != AST_NONE && ((arena).nodes[fn]).ival == 0) {
  int32_t ns = ((arena).nodes[fn]).name_start;
  int32_t ne = ((arena).nodes[fn]).name_end;
  int32_t body = ((arena).nodes[fn]).c;
  int32_t arity = flowc_ast_chain_len(arena, ((arena).nodes[fn]).a);
  if (body != AST_NONE) {
  int32_t prev = ((arena).nodes[root]).a;
  while (prev != item) {
  int32_t pfn = flowc_tc_unwrap_fn(arena, prev);
  if (pfn != AST_NONE && ((arena).nodes[pfn]).c != AST_NONE) {
  if (flowc_tc_span_eq((ctx[0]).src, ns, ne, ((arena).nodes[pfn]).name_start, ((arena).nodes[pfn]).name_end) == 1) {
  flowc_tc_err(ctx);
}
}
  prev = ((arena).nodes[prev]).next;
}
}
  flowc_tc_bind(ctx, ns, ne, 1, arity);
}
  item = ((arena).nodes[item]).next;
}
}

void flowc_tc_check_fns(TcCtx* ctx, AstArena arena, int32_t root) {
  int32_t item = ((arena).nodes[root]).a;
  while (item != AST_NONE) {
  int32_t fn = flowc_tc_unwrap_fn(arena, item);
  if (fn != AST_NONE && ((arena).nodes[fn]).ival == 0) {
  int32_t body = ((arena).nodes[fn]).c;
  if (body != AST_NONE) {
  flowc_tc_push_mark(ctx);
  int32_t param = ((arena).nodes[fn]).a;
  while (param != AST_NONE) {
  int32_t pty = ((arena).nodes[param]).a;
  flowc_tc_bind_value(ctx, ((arena).nodes[param]).name_start, ((arena).nodes[param]).name_end, pty);
  param = ((arena).nodes[param]).next;
}
  (ctx[0]).cur_ret = ((arena).nodes[fn]).b;
  flowc_tc_check_block(ctx, arena, body);
  (ctx[0]).cur_ret = AST_NONE;
  flowc_tc_pop_mark(ctx);
}
}
  if (((arena).nodes[item]).kind == AST_CONST) {
  flowc_tc_check_expr(ctx, arena, ((arena).nodes[item]).b);
}
  item = ((arena).nodes[item]).next;
}
}

void flowc_tc_seed_bind(TcCtx* ctx, uint8_t* dep_src, int32_t start, int32_t end, int32_t kind, int32_t arity) {
  int32_t n = (end - start);
  if (n <= 0) {
  return;
}
  if ((ctx[0]).seed_buf == NULL) {
  flowc_tc_err(ctx);
  return;
}
  if (((ctx[0]).seed_len + n) > (ctx[0]).seed_cap) {
  puts("flowc tc: seed buffer full (raise seed_cap)");
  flowc_tc_err(ctx);
  return;
}
  if ((ctx[0]).nlen >= (ctx[0]).ncap) {
  puts("flowc tc: name table full while seeding (raise ncap)");
  flowc_tc_err(ctx);
  return;
}
  (ctx[0]).nlen = (ctx[0]).seed_nlen;
  int32_t off = (ctx[0]).seed_len;
  int32_t i = 0;
  while (i < n) {
  (ctx[0]).seed_buf[(off + i)] = dep_src[(start + i)];
  i = (i + 1);
}
  (ctx[0]).seed_len = (off + n);
  int32_t bi = (ctx[0]).nlen;
  (ctx[0]).ns[bi] = off;
  (ctx[0]).ne[bi] = (off + n);
  (ctx[0]).nk[bi] = kind;
  (ctx[0]).na[bi] = arity;
  (ctx[0]).nlen = (bi + 1);
  (ctx[0]).seed_nlen = (ctx[0]).nlen;
}

void flowc_tc_seed_export(TcCtx* ctx, AstArena dep_arena, int32_t dep_root, uint8_t* dep_src) {
  if (dep_root == AST_NONE || dep_root < 0) {
  return;
}
  if (((dep_arena).nodes[dep_root]).kind != AST_PROGRAM) {
  return;
}
  int32_t item = ((dep_arena).nodes[dep_root]).a;
  while (item != AST_NONE) {
  int32_t kind = ((dep_arena).nodes[item]).kind;
  if (kind == AST_CONST) {
  if (((dep_arena).nodes[item]).ival == 1) {
  flowc_tc_seed_bind(ctx, dep_src, ((dep_arena).nodes[item]).name_start, ((dep_arena).nodes[item]).name_end, 0, (-1));
}
}
  if (kind == AST_LET) {
  flowc_tc_seed_bind(ctx, dep_src, ((dep_arena).nodes[item]).name_start, ((dep_arena).nodes[item]).name_end, 0, (-1));
}
  if (kind == AST_EXPORT) {
  int32_t inner = ((dep_arena).nodes[item]).a;
  if (inner != AST_NONE && ((dep_arena).nodes[inner]).kind == AST_FN) {
  int32_t ns = ((dep_arena).nodes[inner]).name_start;
  int32_t ne = ((dep_arena).nodes[inner]).name_end;
  int32_t arity = flowc_ast_chain_len(dep_arena, ((dep_arena).nodes[inner]).a);
  flowc_tc_seed_bind(ctx, dep_src, ns, ne, 1, arity);
}
}
  item = ((dep_arena).nodes[item]).next;
}
}

TcCtx flowc_tc_init(uint8_t* src) {
  int32_t ncap = 4096;
  int32_t mcap = 128;
  int32_t seed_cap = 32768;
  uint8_t* raw_ns = (uint8_t*)(malloc(((int64_t)(ncap) * 4)));
  uint8_t* raw_ne = (uint8_t*)(malloc(((int64_t)(ncap) * 4)));
  uint8_t* raw_nk = (uint8_t*)(malloc(((int64_t)(ncap) * 4)));
  uint8_t* raw_na = (uint8_t*)(malloc(((int64_t)(ncap) * 4)));
  uint8_t* raw_mk = (uint8_t*)(malloc(((int64_t)(mcap) * 4)));
  uint8_t* raw_seed = (uint8_t*)(malloc((int64_t)(seed_cap)));
  if (raw_ns == NULL || raw_ne == NULL || raw_nk == NULL || raw_na == NULL || raw_mk == NULL || raw_seed == NULL) {
  if (raw_ns != NULL) {
  free(raw_ns);
}
  if (raw_ne != NULL) {
  free(raw_ne);
}
  if (raw_nk != NULL) {
  free(raw_nk);
}
  if (raw_na != NULL) {
  free(raw_na);
}
  if (raw_mk != NULL) {
  free(raw_mk);
}
  if (raw_seed != NULL) {
  free(raw_seed);
}
  return (TcCtx){ .src = src, .ns = NULL, .ne = NULL, .nk = NULL, .na = NULL, .nlen = 0, .ncap = 0, .marks = NULL, .mlen = 0, .mcap = 0, .err = 1, .cur_ret = AST_NONE, .loop_depth = 0, .has_extern = 0, .lenient = 0, .seed_buf = NULL, .seed_cap = 0, .seed_len = 0, .seed_nlen = 0, .path = "" };
}
  int32_t zi = 0;
  while (zi < seed_cap) {
  raw_seed[zi] = 0;
  zi = (zi + 1);
}
  int32_t* ns = (int32_t*)(raw_ns);
  int32_t* ne = (int32_t*)(raw_ne);
  int32_t* nk = (int32_t*)(raw_nk);
  int32_t* na = (int32_t*)(raw_na);
  int32_t* marks = (int32_t*)(raw_mk);
  return (TcCtx){ .src = src, .ns = ns, .ne = ne, .nk = nk, .na = na, .nlen = 0, .ncap = ncap, .marks = marks, .mlen = 0, .mcap = mcap, .err = 0, .cur_ret = AST_NONE, .loop_depth = 0, .has_extern = 0, .lenient = 0, .seed_buf = raw_seed, .seed_cap = seed_cap, .seed_len = 0, .seed_nlen = 0, .path = "" };
}

void flowc_tc_free(TcCtx* ctx) {
  if ((ctx[0]).ns != NULL) {
  free((ctx[0]).ns);
  (ctx[0]).ns = NULL;
}
  if ((ctx[0]).ne != NULL) {
  free((ctx[0]).ne);
  (ctx[0]).ne = NULL;
}
  if ((ctx[0]).nk != NULL) {
  free((ctx[0]).nk);
  (ctx[0]).nk = NULL;
}
  if ((ctx[0]).na != NULL) {
  free((ctx[0]).na);
  (ctx[0]).na = NULL;
}
  if ((ctx[0]).marks != NULL) {
  free((ctx[0]).marks);
  (ctx[0]).marks = NULL;
}
  if ((ctx[0]).seed_buf != NULL) {
  free((ctx[0]).seed_buf);
  (ctx[0]).seed_buf = NULL;
}
}

void flowc_tc_reset_module(TcCtx* ctx, uint8_t* src) {
  (ctx[0]).src = src;
  (ctx[0]).nlen = (ctx[0]).seed_nlen;
  (ctx[0]).mlen = 0;
  (ctx[0]).err = 0;
  (ctx[0]).cur_ret = AST_NONE;
  (ctx[0]).loop_depth = 0;
  (ctx[0]).has_extern = 0;
}

void flowc_tc_set_path(TcCtx* ctx, const char* path) {
  (ctx[0]).path = path;
}

int32_t flowc_tc_check_program(TcCtx* ctx, AstArena arena, int32_t root) {
  if (root == AST_NONE || root < 0) {
  flowc_tc_err(ctx);
  return (ctx[0]).err;
}
  if (((arena).nodes[root]).kind != AST_PROGRAM) {
  flowc_tc_err(ctx);
  return (ctx[0]).err;
}
  flowc_tc_collect_globals(ctx, arena, root);
  flowc_tc_check_fns(ctx, arena, root);
  return (ctx[0]).err;
}

int32_t flowc_typecheck_ex(AstArena arena, int32_t root, uint8_t* src, const char* path) {
  if (root == AST_NONE || root < 0) {
  return 1;
}
  if (((arena).nodes[root]).kind != AST_PROGRAM) {
  return 1;
}
  TcCtx ctx = flowc_tc_init(src);
  if ((ctx).ns == NULL) {
  return 1;
}
  if (path != NULL) {
  (ctx).path = path;
}
  flowc_tc_check_program((&ctx), arena, root);
  int32_t errs = (ctx).err;
  flowc_tc_free((&ctx));
  return errs;
}

int32_t flowc_typecheck(AstArena arena, int32_t root, uint8_t* src) {
  return flowc_typecheck_ex(arena, root, src, getenv("FLOWC_IN"));
}


static const int32_t FLOWC_RESOLVE_MAX_MODS = 32;
static const int32_t FLOWC_RESOLVE_PATH_CAP = 256;
static const int32_t FLOWC_RESOLVE_SRC_CAP = 262144;
static const int32_t FLOWC_RESOLVE_AST_CAP = 262144;
static const int32_t FLOWC_RESOLVE_SIG_CAP = 65536;
int32_t flowc_resolve_copy_cstr(const char* s, uint8_t* dst, int32_t cap) {
  uint8_t* p = (uint8_t*)(s);
  int32_t n = (int32_t)(strlen(s));
  if ((n + 1) > cap) {
  return (0 - 1);
}
  int32_t i = 0;
  while (i < n) {
  dst[i] = p[i];
  i = (i + 1);
}
  dst[n] = 0;
  return n;
}

int32_t flowc_resolve_cstr_eq(uint8_t* a, uint8_t* b) {
  int32_t i = 0;
  while (i < 4096) {
  int32_t ca = a[i];
  int32_t cb = b[i];
  if (ca != cb) {
  return 0;
}
  if (ca == 0) {
  return 1;
}
  i = (i + 1);
}
  return 0;
}

int32_t flowc_resolve_find_path(uint8_t* store, int32_t n, int32_t row_cap, uint8_t* path) {
  int32_t i = 0;
  while (i < n) {
  uint8_t* slot = (uint8_t*)((store + (i * row_cap)));
  if (flowc_resolve_cstr_eq(slot, path) == 1) {
  return i;
}
  i = (i + 1);
}
  return (0 - 1);
}

int32_t flowc_resolve_sibling_path(uint8_t* import_span_src, int32_t name_start, int32_t name_end, const char* search_dir, uint8_t* out_path, int32_t out_path_cap) {
  if (name_end <= name_start || out_path_cap <= 1) {
  return (0 - 1);
}
  int32_t s = name_start;
  int32_t e = name_end;
  if (import_span_src[s] == 46) {
  s = (s + 1);
}
  if (s < e && import_span_src[s] == 34) {
  s = (s + 1);
}
  if (e > s && import_span_src[(e - 1)] == 34) {
  e = (e - 1);
}
  if (e <= s) {
  return (0 - 1);
}
  if ((e - s) > 7 && import_span_src[s] == 115 && import_span_src[(s + 1)] == 116 && import_span_src[(s + 2)] == 100 && import_span_src[(s + 3)] == 108 && import_span_src[(s + 4)] == 105 && import_span_src[(s + 5)] == 98 && import_span_src[(s + 6)] == 47) {
  s = (s + 7);
} else {
  if ((e - s) > 11 && import_span_src[s] == 108 && import_span_src[(s + 1)] == 105 && import_span_src[(s + 2)] == 98 && import_span_src[(s + 3)] == 47 && import_span_src[(s + 4)] == 115 && import_span_src[(s + 5)] == 116 && import_span_src[(s + 6)] == 100 && import_span_src[(s + 7)] == 108 && import_span_src[(s + 8)] == 105 && import_span_src[(s + 9)] == 98 && import_span_src[(s + 10)] == 47) {
  s = (s + 11);
}
}
  if (import_span_src[s] == 47) {
  int32_t nabs = (e - s);
  if ((nabs + 1) > out_path_cap) {
  return (0 - 1);
}
  int32_t ai = 0;
  while (ai < nabs) {
  out_path[ai] = import_span_src[(s + ai)];
  ai = (ai + 1);
}
  out_path[nabs] = 0;
  return nabs;
}
  uint8_t* dirp = (uint8_t*)(search_dir);
  int32_t dlen = (int32_t)(strlen(search_dir));
  int32_t has_slash = 0;
  int32_t si = s;
  while (si < e) {
  if (import_span_src[si] == 47) {
  has_slash = 1;
}
  si = (si + 1);
}
  int32_t need_flow = 0;
  if (has_slash == 0) {
  if (import_span_src[name_start] == 46) {
  need_flow = 1;
} else {
  if ((e - s) < 5) {
  need_flow = 1;
} else {
  if (import_span_src[(e - 5)] != 46 || import_span_src[(e - 4)] != 102 || import_span_src[(e - 3)] != 108 || import_span_src[(e - 2)] != 111 || import_span_src[(e - 1)] != 119) {
  need_flow = 1;
}
}
}
}
  int32_t namelen = (e - s);
  int32_t total = ((dlen + 1) + namelen);
  if (need_flow == 1) {
  total = (total + 5);
}
  if ((total + 1) > out_path_cap) {
  return (0 - 1);
}
  int32_t o = 0;
  int32_t di = 0;
  while (di < dlen) {
  out_path[o] = dirp[di];
  o = (o + 1);
  di = (di + 1);
}
  out_path[o] = 47;
  o = (o + 1);
  int32_t ni = 0;
  while (ni < namelen) {
  out_path[o] = import_span_src[(s + ni)];
  o = (o + 1);
  ni = (ni + 1);
}
  if (need_flow == 1) {
  out_path[o] = 46;
  o = (o + 1);
  out_path[o] = 102;
  o = (o + 1);
  out_path[o] = 108;
  o = (o + 1);
  out_path[o] = 111;
  o = (o + 1);
  out_path[o] = 119;
  o = (o + 1);
}
  out_path[o] = 0;
  return o;
}

int32_t flowc_resolve_dirname(const char* path, uint8_t* out, int32_t out_cap) {
  uint8_t* p = (uint8_t*)(path);
  int32_t n = (int32_t)(strlen(path));
  if (n <= 0 || out_cap <= 1) {
  return (0 - 1);
}
  int32_t last_slash = (0 - 1);
  int32_t i = 0;
  while (i < n) {
  if (p[i] == 47) {
  last_slash = i;
}
  i = (i + 1);
}
  if (last_slash < 0) {
  if (out_cap < 2) {
  return (0 - 1);
}
  out[0] = 46;
  out[1] = 0;
  return 1;
}
  if (last_slash == 0) {
  if (out_cap < 2) {
  return (0 - 1);
}
  out[0] = 47;
  out[1] = 0;
  return 1;
}
  if ((last_slash + 1) > out_cap) {
  return (0 - 1);
}
  int32_t j = 0;
  while (j < last_slash) {
  out[j] = p[j];
  j = (j + 1);
}
  out[last_slash] = 0;
  return last_slash;
}

int32_t flowc_resolve_append_path(uint8_t* store, int32_t n, const char* path) {
  uint8_t* path_p = (uint8_t*)(path);
  if (flowc_resolve_find_path(store, n, FLOWC_RESOLVE_PATH_CAP, path_p) >= 0) {
  return n;
}
  if (n >= FLOWC_RESOLVE_MAX_MODS) {
  puts("flowc gather: MAX_MODS exceeded");
  return (0 - 1);
}
  uint8_t* slot = (uint8_t*)((store + (n * FLOWC_RESOLVE_PATH_CAP)));
  if (flowc_resolve_copy_cstr(path, slot, FLOWC_RESOLVE_PATH_CAP) < 0) {
  return (0 - 1);
}
  return (n + 1);
}

int32_t flowc_resolve_gather(const char* entry_path, const char* search_dir, uint8_t* path_store) {
  int32_t n = flowc_resolve_append_path(path_store, 0, entry_path);
  if (n < 0) {
  return (0 - 1);
}
  uint8_t* src = (uint8_t*)(malloc((int64_t)(FLOWC_RESOLVE_SRC_CAP)));
  uint8_t* imp_path = (uint8_t*)(malloc((int64_t)(FLOWC_RESOLVE_PATH_CAP)));
  if (src == NULL || imp_path == NULL) {
  if (src != NULL) {
  free(src);
}
  if (imp_path != NULL) {
  free(imp_path);
}
  return (0 - 1);
}
  int32_t qi = 0;
  while (qi < n) {
  uint8_t* slot = (uint8_t*)((path_store + (qi * FLOWC_RESOLVE_PATH_CAP)));
  const char* mpath = slot;
  int32_t zi = 0;
  while (zi < FLOWC_RESOLVE_SRC_CAP) {
  src[zi] = 0;
  zi = (zi + 1);
}
  int32_t nsrc = flowc_read_file(mpath, src, (FLOWC_RESOLVE_SRC_CAP - 1));
  if (nsrc <= 0) {
  puts("flowc gather: read failed");
  free(imp_path);
  free(src);
  return (0 - 1);
}
  src[nsrc] = 0;
  Parser p = flowc_parser_new(src, nsrc, FLOWC_RESOLVE_AST_CAP);
  int32_t root = flowc_parse_program((&p));
  if (root < 0 || (p).err != 0) {
  puts("flowc gather: parse failed");
  printf("flowc gather: nsrc=%d\n", nsrc);
  flowc_parser_free(p);
  free(imp_path);
  free(src);
  return (0 - 1);
}
  int32_t ii = 0;
  while (ii < ((p).arena).len) {
  if ((((p).arena).nodes[ii]).kind == AST_IMPORT) {
  int32_t form = (((p).arena).nodes[ii]).ival;
  if (form == 1 || form == 2) {
  int32_t plen = flowc_resolve_sibling_path(src, (((p).arena).nodes[ii]).name_start, (((p).arena).nodes[ii]).name_end, search_dir, imp_path, FLOWC_RESOLVE_PATH_CAP);
  if (plen < 0) {
  flowc_parser_free(p);
  free(imp_path);
  free(src);
  return (0 - 1);
}
  const char* dep = imp_path;
  int32_t n2 = flowc_resolve_append_path(path_store, n, dep);
  if (n2 < 0) {
  flowc_parser_free(p);
  free(imp_path);
  free(src);
  return (0 - 1);
}
  n = n2;
}
}
  ii = (ii + 1);
}
  flowc_parser_free(p);
  qi = (qi + 1);
}
  free(imp_path);
  free(src);
  return n;
}

int32_t flowc_resolve_deps_ready(const char* path, const char* search_dir, uint8_t* all_store, int32_t all_n, uint8_t* out_store, int32_t out_n, uint8_t* src, uint8_t* imp_path) {
  int32_t zi = 0;
  while (zi < FLOWC_RESOLVE_SRC_CAP) {
  src[zi] = 0;
  zi = (zi + 1);
}
  int32_t nsrc = flowc_read_file(path, src, (FLOWC_RESOLVE_SRC_CAP - 1));
  if (nsrc <= 0) {
  return 0;
}
  src[nsrc] = 0;
  Parser p = flowc_parser_new(src, nsrc, FLOWC_RESOLVE_AST_CAP);
  int32_t root = flowc_parse_program((&p));
  if (root < 0 || (p).err != 0) {
  flowc_parser_free(p);
  return 0;
}
  int32_t ii = 0;
  while (ii < ((p).arena).len) {
  if ((((p).arena).nodes[ii]).kind == AST_IMPORT) {
  int32_t form = (((p).arena).nodes[ii]).ival;
  if (form == 1 || form == 2) {
  int32_t plen = flowc_resolve_sibling_path(src, (((p).arena).nodes[ii]).name_start, (((p).arena).nodes[ii]).name_end, search_dir, imp_path, FLOWC_RESOLVE_PATH_CAP);
  if (plen < 0) {
  flowc_parser_free(p);
  return 0;
}
  if (flowc_resolve_find_path(all_store, all_n, FLOWC_RESOLVE_PATH_CAP, imp_path) >= 0) {
  if (flowc_resolve_find_path(out_store, out_n, FLOWC_RESOLVE_PATH_CAP, imp_path) < 0) {
  flowc_parser_free(p);
  return 0;
}
}
}
}
  ii = (ii + 1);
}
  flowc_parser_free(p);
  return 1;
}

int32_t flowc_resolve_topo(uint8_t* all_store, int32_t all_n, const char* search_dir, uint8_t* out_store) {
  uint8_t* src = (uint8_t*)(malloc((int64_t)(FLOWC_RESOLVE_SRC_CAP)));
  uint8_t* imp_path = (uint8_t*)(malloc((int64_t)(FLOWC_RESOLVE_PATH_CAP)));
  uint8_t* placed = (uint8_t*)(malloc((int64_t)(FLOWC_RESOLVE_MAX_MODS)));
  if (src == NULL || imp_path == NULL || placed == NULL) {
  if (src != NULL) {
  free(src);
}
  if (imp_path != NULL) {
  free(imp_path);
}
  if (placed != NULL) {
  free(placed);
}
  return (0 - 1);
}
  int32_t pi = 0;
  while (pi < FLOWC_RESOLVE_MAX_MODS) {
  placed[pi] = 0;
  pi = (pi + 1);
}
  int32_t out_n = 0;
  while (out_n < all_n) {
  int32_t progress = 0;
  int32_t i = 0;
  while (i < all_n) {
  if (placed[i] == 0) {
  uint8_t* slot = (uint8_t*)((all_store + (i * FLOWC_RESOLVE_PATH_CAP)));
  const char* mpath = slot;
  if (flowc_resolve_deps_ready(mpath, search_dir, all_store, all_n, out_store, out_n, src, imp_path) == 1) {
  int32_t n2 = flowc_resolve_append_path(out_store, out_n, mpath);
  if (n2 < 0) {
  free(placed);
  free(imp_path);
  free(src);
  return (0 - 1);
}
  out_n = n2;
  placed[i] = 1;
  progress = 1;
}
}
  i = (i + 1);
}
  if (progress == 0) {
  free(placed);
  free(imp_path);
  free(src);
  return (0 - 1);
}
}
  free(placed);
  free(imp_path);
  free(src);
  return out_n;
}

int32_t flowc_resolve_emit_one(const char* path, uint8_t* out, int32_t out_cap, int32_t flags, uint8_t* sigs, int32_t sigcap, int32_t* siglen) {
  uint8_t* src = (uint8_t*)(malloc((int64_t)(FLOWC_RESOLVE_SRC_CAP)));
  if (src == NULL) {
  return (0 - 1);
}
  int32_t zi = 0;
  while (zi < FLOWC_RESOLVE_SRC_CAP) {
  src[zi] = 0;
  zi = (zi + 1);
}
  int32_t nsrc = flowc_read_file(path, src, (FLOWC_RESOLVE_SRC_CAP - 1));
  if (nsrc <= 0) {
  free(src);
  return (0 - 1);
}
  src[nsrc] = 0;
  Parser p = flowc_parser_new(src, nsrc, FLOWC_RESOLVE_AST_CAP);
  int32_t root = flowc_parse_program((&p));
  if (root < 0 || (p).err != 0) {
  flowc_parser_free(p);
  free(src);
  return (0 - 1);
}
  int32_t n = flowc_cgen_emit_sigs((p).arena, root, src, out, out_cap, flags, sigs, siglen[0]);
  if (sigs != NULL) {
  siglen[0] = flowc_cgen_collect_sigs((p).arena, root, src, sigs, sigcap, siglen[0]);
}
  flowc_parser_free(p);
  free(src);
  return n;
}

int32_t flowc_bundle_typecheck(const char* entry_path, const char* search_dir) {
  uint8_t* path_store = (uint8_t*)(malloc((int64_t)((FLOWC_RESOLVE_MAX_MODS * FLOWC_RESOLVE_PATH_CAP))));
  if (path_store == NULL) {
  return 1;
}
  int32_t zi = 0;
  int32_t psz = (FLOWC_RESOLVE_MAX_MODS * FLOWC_RESOLVE_PATH_CAP);
  while (zi < psz) {
  path_store[zi] = 0;
  zi = (zi + 1);
}
  int32_t nmods = flowc_resolve_gather(entry_path, search_dir, path_store);
  if (nmods <= 0) {
  puts("flowc bundle tc: gather failed");
  free(path_store);
  return 1;
}
  uint8_t* order_store = (uint8_t*)(malloc((int64_t)((FLOWC_RESOLVE_MAX_MODS * FLOWC_RESOLVE_PATH_CAP))));
  if (order_store == NULL) {
  free(path_store);
  return 1;
}
  zi = 0;
  while (zi < psz) {
  order_store[zi] = 0;
  zi = (zi + 1);
}
  int32_t norder = flowc_resolve_topo(path_store, nmods, search_dir, order_store);
  if (norder <= 0) {
  puts("flowc bundle tc: topo failed");
  free(order_store);
  free(path_store);
  return 1;
}
  uint8_t* no_src = (uint8_t*)(NULL);
  TcCtx ctx = flowc_tc_init(no_src);
  (ctx).lenient = 1;
  if ((ctx).ns == NULL) {
  free(order_store);
  free(path_store);
  return 1;
}
  uint8_t* src = (uint8_t*)(malloc((int64_t)(FLOWC_RESOLVE_SRC_CAP)));
  if (src == NULL) {
  flowc_tc_free((&ctx));
  free(order_store);
  free(path_store);
  return 1;
}
  int32_t total_err = 0;
  int32_t mi = 0;
  while (mi < norder) {
  uint8_t* slot = (uint8_t*)((order_store + (mi * FLOWC_RESOLVE_PATH_CAP)));
  const char* mpath = slot;
  zi = 0;
  while (zi < FLOWC_RESOLVE_SRC_CAP) {
  src[zi] = 0;
  zi = (zi + 1);
}
  int32_t nsrc = flowc_read_file(mpath, src, (FLOWC_RESOLVE_SRC_CAP - 1));
  if (nsrc <= 0) {
  puts("flowc bundle tc: read failed");
  free(src);
  flowc_tc_free((&ctx));
  free(order_store);
  free(path_store);
  return 1;
}
  src[nsrc] = 0;
  Parser p = flowc_parser_new(src, nsrc, FLOWC_RESOLVE_AST_CAP);
  int32_t root = flowc_parse_program((&p));
  if (root < 0 || (p).err != 0) {
  puts("flowc bundle tc: parse failed");
  printf("flowc bundle tc: nsrc=%d\n", nsrc);
  flowc_parser_free(p);
  free(src);
  flowc_tc_free((&ctx));
  free(order_store);
  free(path_store);
  return 1;
}
  flowc_tc_reset_module((&ctx), src);
  flowc_tc_set_path((&ctx), mpath);
  int32_t errs = flowc_tc_check_program((&ctx), (p).arena, root);
  if (errs > 0) {
  puts("flowc bundle tc: module check failed");
  printf("flowc bundle tc: module_errs=%d\n", errs);
}
  total_err = (total_err + errs);
  (ctx).nlen = (ctx).seed_nlen;
  flowc_tc_seed_export((&ctx), (p).arena, root, src);
  flowc_parser_free(p);
  mi = (mi + 1);
}
  free(src);
  flowc_tc_free((&ctx));
  free(order_store);
  free(path_store);
  return total_err;
}

int32_t flowc_bundle_emit(const char* entry_path, const char* search_dir, uint8_t* out, int32_t out_cap) {
  uint8_t* path_store = (uint8_t*)(malloc((int64_t)((FLOWC_RESOLVE_MAX_MODS * FLOWC_RESOLVE_PATH_CAP))));
  if (path_store == NULL) {
  return (0 - 1);
}
  int32_t zi = 0;
  int32_t psz = (FLOWC_RESOLVE_MAX_MODS * FLOWC_RESOLVE_PATH_CAP);
  while (zi < psz) {
  path_store[zi] = 0;
  zi = (zi + 1);
}
  int32_t nmods = flowc_resolve_gather(entry_path, search_dir, path_store);
  if (nmods <= 0) {
  free(path_store);
  return (0 - 1);
}
  uint8_t* order_store = (uint8_t*)(malloc((int64_t)((FLOWC_RESOLVE_MAX_MODS * FLOWC_RESOLVE_PATH_CAP))));
  if (order_store == NULL) {
  free(path_store);
  return (0 - 1);
}
  zi = 0;
  while (zi < psz) {
  order_store[zi] = 0;
  zi = (zi + 1);
}
  int32_t norder = flowc_resolve_topo(path_store, nmods, search_dir, order_store);
  if (norder <= 0) {
  free(order_store);
  free(path_store);
  return (0 - 1);
}
  uint8_t* sigs = (uint8_t*)(malloc((int64_t)(FLOWC_RESOLVE_SIG_CAP)));
  if (sigs == NULL) {
  free(order_store);
  free(path_store);
  return (0 - 1);
}
  zi = 0;
  while (zi < FLOWC_RESOLVE_SIG_CAP) {
  sigs[zi] = 0;
  zi = (zi + 1);
}
  int32_t siglen = 0;
  int32_t written = 0;
  int32_t mi = 0;
  int32_t first = 1;
  while (mi < norder) {
  uint8_t* slot = (uint8_t*)((order_store + (mi * FLOWC_RESOLVE_PATH_CAP)));
  const char* mpath = slot;
  int32_t flags = 0;
  if (first == 0) {
  flags = 1;
}
  first = 0;
  uint8_t* dest = (uint8_t*)((out + written));
  int32_t rem = (out_cap - written);
  if (rem <= 0) {
  free(sigs);
  free(order_store);
  free(path_store);
  return (0 - 1);
}
  int32_t n = flowc_resolve_emit_one(mpath, dest, rem, flags, sigs, FLOWC_RESOLVE_SIG_CAP, (&siglen));
  if (n <= 0) {
  free(sigs);
  free(order_store);
  free(path_store);
  return (0 - 1);
}
  written = (written + n);
  if (written < out_cap) {
  out[written] = 10;
  written = (written + 1);
}
  mi = (mi + 1);
}
  free(sigs);
  free(order_store);
  free(path_store);
  return written;
}


int32_t flowc_driver_env_set(const char* name) {
  const char* v = getenv(name);
  uint8_t* p = (uint8_t*)(v);
  if (p == NULL) {
  return 0;
}
  if (strlen(v) == 0) {
  return 0;
}
  return 1;
}

int32_t flowc_driver_env_is_zero(const char* name) {
  const char* v = getenv(name);
  uint8_t* p = (uint8_t*)(v);
  if (p == NULL) {
  return 0;
}
  if (strlen(v) != 1) {
  return 0;
}
  if (p[0] == 48) {
  return 1;
}
  return 0;
}

int32_t flowc_driver_want_typecheck() {
  if (flowc_driver_env_set("FLOWC_NO_TYPECHECK") == 1) {
  return 0;
}
  if (flowc_driver_env_is_zero("FLOWC_TYPECHECK") == 1) {
  return 0;
}
  return 1;
}

int32_t flowc_driver_run(const char* in_path, const char* out_path) {
  int32_t out_cap = 1048576;
  uint8_t* out = (uint8_t*)(malloc((int64_t)(out_cap)));
  if (out == NULL) {
  puts("stage_a_driver_flow: malloc out failed");
  return 1;
}
  int32_t zi = 0;
  while (zi < out_cap) {
  out[zi] = 0;
  zi = (zi + 1);
}
  if (flowc_driver_env_set("FLOWC_BUNDLE") == 1) {
  const char* search_dir = "compiler/src";
  uint8_t* dir_buf = (uint8_t*)(malloc(256));
  if (dir_buf == NULL) {
  puts("stage_a_driver_flow: malloc dir failed");
  free(out);
  return 1;
}
  zi = 0;
  while (zi < 256) {
  dir_buf[zi] = 0;
  zi = (zi + 1);
}
  if (flowc_driver_env_set("FLOWC_DIR") == 1) {
  search_dir = getenv("FLOWC_DIR");
} else {
  int32_t dlen = flowc_resolve_dirname(in_path, dir_buf, 256);
  if (dlen > 0) {
  search_dir = dir_buf;
}
}
  if (flowc_driver_want_typecheck() == 1) {
  int32_t tc_errs = flowc_bundle_typecheck(in_path, search_dir);
  if (tc_errs > 0) {
  puts("stage_a_driver_flow: bundle typecheck failed");
  printf("stage_a_driver_flow: tc_errs=%d\n", tc_errs);
  free(dir_buf);
  free(out);
  return 1;
}
}
  int32_t nout = flowc_bundle_emit(in_path, search_dir, out, out_cap);
  free(dir_buf);
  if (nout <= 0) {
  puts("stage_a_driver_flow: bundle emit failed");
  free(out);
  return 1;
}
  if (flowc_write_file(out_path, out, nout) != 0) {
  puts("stage_a_driver_flow: write output failed");
  free(out);
  return 1;
}
  free(out);
  return 0;
}
  int32_t src_cap = 262144;
  uint8_t* src = (uint8_t*)(malloc((int64_t)(src_cap)));
  if (src == NULL) {
  puts("stage_a_driver_flow: malloc src failed");
  free(out);
  return 1;
}
  zi = 0;
  while (zi < src_cap) {
  src[zi] = 0;
  zi = (zi + 1);
}
  int32_t nsrc = flowc_read_file(in_path, src, (src_cap - 1));
  if (nsrc <= 0) {
  puts("stage_a_driver_flow: read input failed");
  free(src);
  free(out);
  return 1;
}
  src[nsrc] = 0;
  Parser p = flowc_parser_new(src, nsrc, 262144);
  int32_t root = flowc_parse_program((&p));
  if (root < 0 || (p).err != 0) {
  puts("stage_a_driver_flow: parse failed");
  printf("stage_a_driver_flow: at %d\n", ((p).cur).start);
  printf("stage_a_driver_flow: arena_len=%d\n", ((p).arena).len);
  flowc_parser_free(p);
  free(src);
  free(out);
  return 1;
}
  if (flowc_driver_want_typecheck() == 1) {
  int32_t tc_errs = flowc_typecheck_ex((p).arena, root, src, in_path);
  if (tc_errs > 0) {
  puts("stage_a_driver_flow: typecheck failed");
  printf("stage_a_driver_flow: tc_errs=%d\n", tc_errs);
  flowc_parser_free(p);
  free(src);
  free(out);
  return 1;
}
}
  int32_t nout = flowc_cgen_emit((p).arena, root, src, out, out_cap);
  if (nout <= 0) {
  puts("stage_a_driver_flow: cgen failed");
  free(out);
  flowc_parser_free(p);
  free(src);
  return 1;
}
  if (flowc_write_file(out_path, out, nout) != 0) {
  puts("stage_a_driver_flow: write output failed");
  free(out);
  flowc_parser_free(p);
  free(src);
  return 1;
}
  free(out);
  flowc_parser_free(p);
  free(src);
  return 0;
}

int main(int argc, char **argv) {
  if (argc == 3) {
  return flowc_driver_run((const char*)(argv[1]), (const char*)(argv[2]));
}
  if (flowc_driver_env_set("FLOWC_IN") == 0) {
  puts("usage: stage_a_driver_flow <in.flow> <out.c>");
  return 2;
}
  if (flowc_driver_env_set("FLOWC_OUT") == 0) {
  puts("usage: stage_a_driver_flow <in.flow> <out.c>");
  return 2;
}
  return flowc_driver_run(getenv("FLOWC_IN"), getenv("FLOWC_OUT"));
}


