#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
#include <complex.h>
#pragma clang diagnostic ignored "-Wint-conversion"
#pragma clang diagnostic ignored "-Wincompatible-pointer-types"
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

#define __flow_in_arr(arr, val) __extension__ ({ \
    int _found = 0; \
    size_t _n = sizeof(arr)/sizeof((arr)[0]); \
    for (size_t _i = 0; _i < _n; _i++) { \
        if ((arr)[_i] == (val)) { _found = 1; break; } \
    } _found; })

#define __flow_dbg(x) (__extension__ ({ int32_t __flow_dbg_v = (x); fprintf(stderr, "dbg: %s = %d\n", #x, __flow_dbg_v); __flow_dbg_v; }))

#include <sys/stat.h>
#ifndef FLOWC_IO_FOPEN
#define FLOWC_IO_FOPEN
static inline void* flowc_io_fopen(const char* path, const char* mode) { return fopen(path, mode); }
#endif
#ifndef FLOWC_IO_FCLOSE
#define FLOWC_IO_FCLOSE
static inline int32_t flowc_io_fclose(void* fp) { return fclose(fp); }
#endif
#ifndef FLOWC_IO_FREAD
#define FLOWC_IO_FREAD
static inline int32_t flowc_io_fread(uint8_t* buf, int32_t size, int32_t n, void* fp) { return fread(buf, size, n, fp); }
#endif
#ifndef FLOWC_IO_FWRITE
#define FLOWC_IO_FWRITE
static inline int32_t flowc_io_fwrite(uint8_t* buf, int32_t size, int32_t n, void* fp) { return fwrite(buf, size, n, fp); }
#endif
#ifndef FLOWC_IO_FSEEK
#define FLOWC_IO_FSEEK
static inline int32_t flowc_io_fseek(void* fp, int64_t offset, int32_t whence) { return fseek(fp, offset, whence); }
#endif
#ifndef FLOWC_IO_FTELL
#define FLOWC_IO_FTELL
static inline int64_t flowc_io_ftell(void* fp) { return ftell(fp); }
#endif
#ifndef FLOWC_READ_FILE
#define FLOWC_READ_FILE
static inline int32_t flowc_read_file(const char* path, uint8_t* buf, int32_t cap) { void* fp = fopen(path, "rb"); if (fp == 0) { return -1; } if (cap <= 0) { fclose(fp); return 0; } int32_t n = fread(buf, 1, cap, fp); fclose(fp); return n < 0 ? -1 : n; }
#endif
#ifndef FLOWC_WRITE_FILE
#define FLOWC_WRITE_FILE
static inline int32_t flowc_write_file(const char* path, uint8_t* buf, int32_t n) { void* fp = fopen(path, "wb"); if (fp == 0) { return -1; } if (n <= 0) { fclose(fp); return 0; } int32_t w = fwrite(buf, 1, n, fp); fclose(fp); return w != n ? -1 : 0; }
#endif
#ifndef FLOWC_IO_REMOVE
#define FLOWC_IO_REMOVE
static inline int32_t flowc_io_remove(const char* path) { return remove(path); }
#endif
#ifndef FLOWC_IO_MKDIR
#define FLOWC_IO_MKDIR
static inline int32_t flowc_io_mkdir(const char* path) { return mkdir(path, 493); }
#endif
#ifndef FLOWC_IO_EXISTS
#define FLOWC_IO_EXISTS
static inline int32_t flowc_io_exists(const char* path) { struct stat st; return stat(path, &st) == 0 ? 1 : 0; }
#endif
#ifndef FLOWC_IO_FILE_SIZE
#define FLOWC_IO_FILE_SIZE
static inline int64_t flowc_io_file_size(const char* path) { void* fp = fopen(path, "rb"); if (fp == 0) { return -1; } fseek(fp, 0, 2); int64_t sz = ftell(fp); fclose(fp); return sz; }
#endif
#ifndef FLOWC_IO_POPEN_READ
#define FLOWC_IO_POPEN_READ
static inline int32_t flowc_io_popen_read(const char* cmd, uint8_t* buf, int32_t cap) { void* fp = popen(cmd, "r"); if (fp == 0) { return -1; } if (cap <= 0) { pclose(fp); return 0; } int32_t n = fread(buf, 1, cap, fp); pclose(fp); return n < 0 ? -1 : n; }
#endif
#ifndef FLOWC_IO_SYSTEM
#define FLOWC_IO_SYSTEM
static inline int32_t flowc_io_system(const char* cmd) { return system(cmd); }
#endif
#ifndef FLOWC_SORT
#define FLOWC_SORT
#include <stdlib.h>
static int flowc_cmp_i32(const void* a, const void* b) { int32_t x = *(const int32_t*)a; int32_t y = *(const int32_t*)b; return (x > y) - (x < y); }
static int flowc_cmp_u8(const void* a, const void* b) { uint8_t x = *(const uint8_t*)a; uint8_t y = *(const uint8_t*)b; return (x > y) - (x < y); }
static int flowc_cmp_f64(const void* a, const void* b) { double x = *(const double*)a; double y = *(const double*)b; int xu = (x != x), yu = (y != y); if (xu && yu) { union { double d; uint64_t u; } ux, uy; ux.d = x; uy.d = y; return (ux.u < uy.u) - (ux.u > uy.u); } if (xu) { union { double d; uint64_t u; } ux; ux.d = x; return (ux.u >> 63) ? -1 : 1; } if (yu) { union { double d; uint64_t u; } uy; uy.d = y; return (uy.u >> 63) ? 1 : -1; } if (x == y) { union { double d; uint64_t u; } ux, uy; ux.d = x; uy.d = y; return (ux.u < uy.u) - (ux.u > uy.u); } return (x > y) - (x < y); }
static int flowc_cmp_f32(const void* a, const void* b) { float x = *(const float*)a; float y = *(const float*)b; if (x != x) return 1; if (y != y) return -1; return (x > y) - (x < y); }
static int32_t flowc_sort_dispatch(void* a, int32_t n, int32_t sz, int32_t desc) { if (sz == 1) qsort(a, n, 1, flowc_cmp_u8); else if (sz == 4) qsort(a, n, 4, flowc_cmp_i32); else if (sz == 8) qsort(a, n, 8, flowc_cmp_f64); else qsort(a, n, sz, flowc_cmp_i32); if (desc) { int32_t i = 0, j = n - 1; while (i < j) { char tmp[8]; memcpy(tmp, (char*)a + i * sz, sz); memcpy((char*)a + i * sz, (char*)a + j * sz, sz); memcpy((char*)a + j * sz, tmp, sz); i++; j--; } } return 0; }
static int32_t flowc_find_i32(int32_t* a, int32_t n, int32_t target) { for (int32_t i = 0; i < n; i++) { if (a[i] == target) return i; } return -1; }
static int32_t flowc_sort_struct(void* a, int32_t n, int32_t sz, int32_t desc) { char* base = (char*)a; char* tmp = (char*)malloc(sz); for (int32_t i = 1; i < n; i++) { memcpy(tmp, base + i * sz, sz); int32_t j = i; while (j > 0) { int32_t cmp = *(int32_t*)(base + (j-1) * sz) - *(int32_t*)tmp; if (desc ? (cmp <= 0) : (cmp > 0)) { memcpy(base + j * sz, base + (j-1) * sz, sz); j--; } else break; } memcpy(base + j * sz, tmp, sz); } free(tmp); return 0; }
#endif

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
const int32_t TOK_IN = 47;
const int32_t TOK_PIPELINE = 48;
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
const int32_t KW_DEFER = 31;
const int32_t KW_ENUM = 32;
const int32_t KW_TRAIT = 33;
const int32_t KW_IMPL = 34;
const int32_t KW_TEST = 35;
const int32_t KW_PARALLEL = 36;
const int32_t KW_DBG = 37;
const int32_t KW_EXPECT = 38;
const int32_t KW_DEFAULT = 39;
Token flowc_make_tok(int32_t kind, int32_t kw, int32_t start, int32_t end, int32_t line, int32_t col);
Token flowc_make_tok(int32_t kind, int32_t kw, int32_t start, int32_t end, int32_t line, int32_t col) {
  return (Token){ .kind = kind, .kw = kw, .start = start, .end = end, .line = line, .col = col };
}


int32_t flowc_lex_is_alpha(int32_t c);
int32_t flowc_lex_is_digit(int32_t c);
int32_t flowc_lex_is_alnum(int32_t c);
int32_t flowc_lex_is_space(int32_t c);
Lexer flowc_lexer_new(uint8_t* input, int32_t len);
void flowc_lexer_bump(Lexer* lex);
void flowc_lexer_skip_trivia(Lexer* lex);
int32_t flowc_lex_ident_eq(uint8_t* src, int32_t start, int32_t end, uint8_t* lit, int32_t lit_len);
int32_t flowc_lex_classify_keyword(uint8_t* src, int32_t start, int32_t end);
Token flowc_lexer_next(Lexer* lex);
int32_t flowc_token_is_kw(Token tok, int32_t kw);
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
  uint8_t defer_kw[5] = { 100, 101, 102, 101, 114 };
  uint8_t enum_kw[4] = { 101, 110, 117, 109 };
  uint8_t trait_kw[5] = { 116, 114, 97, 105, 116 };
  uint8_t impl_kw[4] = { 105, 109, 112, 108 };
  uint8_t test_kw[4] = { 116, 101, 115, 116 };
  uint8_t parallel_kw[8] = { 112, 97, 114, 97, 108, 108, 101, 108 };
  uint8_t dbg_kw[3] = { 100, 98, 103 };
  uint8_t expect_kw[6] = { 101, 120, 112, 101, 99, 116 };
  uint8_t default_kw[7] = { 100, 101, 102, 97, 117, 108, 116 };
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
  p = defer_kw;
  if (flowc_lex_ident_eq(src, start, end, p, 5) == 1) {
  return KW_DEFER;
}
  p = enum_kw;
  if (flowc_lex_ident_eq(src, start, end, p, 4) == 1) {
  return KW_ENUM;
}
  p = trait_kw;
  if (flowc_lex_ident_eq(src, start, end, p, 5) == 1) {
  return KW_TRAIT;
}
  p = impl_kw;
  if (flowc_lex_ident_eq(src, start, end, p, 4) == 1) {
  return KW_IMPL;
}
  p = test_kw;
  if (flowc_lex_ident_eq(src, start, end, p, 4) == 1) {
  return KW_TEST;
}
  p = parallel_kw;
  if (flowc_lex_ident_eq(src, start, end, p, 8) == 1) {
  return KW_PARALLEL;
}
  p = dbg_kw;
  if (flowc_lex_ident_eq(src, start, end, p, 3) == 1) {
  return KW_DBG;
}
  p = expect_kw;
  if (flowc_lex_ident_eq(src, start, end, p, 6) == 1) {
  return KW_EXPECT;
}
  p = default_kw;
  if (flowc_lex_ident_eq(src, start, end, p, 7) == 1) {
  return KW_DEFAULT;
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
  if (c == 48 && (lex[0]).pos < (lex[0]).len && ((lex[0]).input[(lex[0]).pos] == 120 || (lex[0]).input[(lex[0]).pos] == 88)) {
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
  if ((lex[0]).pos < (lex[0]).len && ((lex[0]).input[(lex[0]).pos] == 101 || (lex[0]).input[(lex[0]).pos] == 69)) {
  int32_t save_pos = (lex[0]).pos;
  flowc_lexer_bump(lex);
  if ((lex[0]).pos < (lex[0]).len && ((lex[0]).input[(lex[0]).pos] == 43 || (lex[0]).input[(lex[0]).pos] == 45)) {
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
  if (c == 124 && n1 == 62) {
  flowc_lexer_bump(lex);
  flowc_lexer_bump(lex);
  return flowc_make_tok(TOK_PIPELINE, 0, start, (start + 2), line, col);
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
const int32_t AST_DEFER = 42;
const int32_t AST_ENUM = 43;
const int32_t AST_ENUM_VARIANT = 44;
const int32_t AST_IF_EXPR = 45;
const int32_t AST_TYPE_SPAN_MUTABLE = 1;
AstArena flowc_ast_new(int32_t cap);
void flowc_ast_free(AstArena arena);
int32_t flowc_ast_alloc(AstArena* arena, int32_t kind, int32_t start, int32_t end);
int32_t flowc_ast_type_set_span_mutable(AstArena* arena, int32_t id, int32_t is_mutable);
int32_t flowc_ast_type_span_mutable(AstArena arena, int32_t id);
int32_t flowc_ast_count_kind(AstArena arena, int32_t kind);
int32_t flowc_ast_chain_push(AstArena* arena, int32_t head, int32_t node);
int32_t flowc_ast_chain_len(AstArena arena, int32_t head);
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

int32_t flowc_ast_type_set_span_mutable(AstArena* arena, int32_t id, int32_t is_mutable) {
  if (id == AST_NONE || id < 0 || id >= (arena[0]).len) {
  return (0 - 1);
}
  if (((arena[0]).nodes[id]).kind != AST_TYPE) {
  return (0 - 1);
}
  if (is_mutable == 0) {
  ((arena[0]).nodes[id]).c = AST_NONE;
} else {
  ((arena[0]).nodes[id]).c = AST_TYPE_SPAN_MUTABLE;
}
  return 0;
}

int32_t flowc_ast_type_span_mutable(AstArena arena, int32_t id) {
  if (id == AST_NONE || id < 0 || id >= (arena).len) {
  return 0;
}
  if (((arena).nodes[id]).kind != AST_TYPE) {
  return 0;
}
  if (((arena).nodes[id]).c == AST_TYPE_SPAN_MUTABLE) {
  return 1;
}
  return 0;
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

Parser flowc_parser_new(uint8_t* input, int32_t len, int32_t ast_cap);
void flowc_parser_free(Parser p);
void flowc_parser_advance(Parser* p);
int32_t flowc_parser_check(Parser p, int32_t kind);
int32_t flowc_parser_check_kw(Parser p, int32_t kw);
int32_t flowc_parser_span_is(Parser p, int32_t start, int32_t end, const char* lit);
int32_t flowc_parser_eat(Parser* p, int32_t kind);
int32_t flowc_parser_eat_kw(Parser* p, int32_t kw);
int32_t flowc_parse_int_span(uint8_t* src, int32_t start, int32_t end);
int32_t flowc_parser_eat_gt(Parser* p);
int32_t flowc_parse_type(Parser* p);
int32_t flowc_parse_atom(Parser* p);
int32_t flowc_parse_postfix(Parser* p);
int32_t flowc_parse_primary(Parser* p);
int32_t flowc_parse_cast(Parser* p);
int32_t flowc_parse_binop_kind(Parser p);
int32_t flowc_parse_binop_prec(int32_t op);
int32_t flowc_parse_binop_rhs(Parser* p, int32_t min_prec, int32_t lhs);
int32_t flowc_parse_expr(Parser* p);
int32_t flowc_parse_apply_pipe(Parser* p, int32_t left, int32_t right);
int32_t flowc_parse_if_chain(Parser* p, int32_t start);
int32_t flowc_parse_stmt(Parser* p);
int32_t flowc_parse_block(Parser* p);
int32_t flowc_parse_param(Parser* p);
int32_t flowc_parse_function(Parser* p);
int32_t flowc_parse_struct(Parser* p);
int32_t flowc_parse_extern(Parser* p);
int32_t flowc_parse_brace_idents(Parser* p);
int32_t flowc_parse_import(Parser* p);
int32_t flowc_parse_let(Parser* p);
void flowc_parser_skip_brace_block(Parser* p);
void flowc_parser_skip_paren_block(Parser* p);
int32_t flowc_parse_enum(Parser* p);
int32_t flowc_parse_type_alias(Parser* p);
int32_t flowc_parse_const(Parser* p, int32_t is_export);
int32_t flowc_parse_export(Parser* p);
int32_t flowc_parse_program(Parser* p);
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

int32_t flowc_parser_span_is(Parser p, int32_t start, int32_t end, const char* lit) {
  uint8_t* lp = (uint8_t*)(lit);
  int32_t n = (int32_t)(strlen(lit));
  if ((end - start) != n) {
  return 0;
}
  int32_t i = 0;
  while (i < n) {
  if (((p).lex).input[(start + i)] != lp[i]) {
  return 0;
}
  i = (i + 1);
}
  return 1;
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
  if ((end - start) >= 2 && src[start] == 48 && (src[(start + 1)] == 120 || src[(start + 1)] == 88)) {
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
  int32_t start = ((p[0]).cur).start;
  flowc_parser_advance(p);
  int32_t is_mut = 0;
  if (flowc_parser_check_kw(p[0], KW_MUT) == 1) {
  is_mut = 1;
  flowc_parser_advance(p);
}
  if (flowc_parser_check(p[0], TOK_LBRACK) == 1) {
  flowc_parser_advance(p);
  int32_t inner = flowc_parse_type(p);
  if (inner == AST_NONE) {
  return AST_NONE;
}
  int32_t extent = 0;
  if (flowc_parser_check(p[0], TOK_SEMI) == 1) {
  flowc_parser_advance(p);
  if (flowc_parser_check(p[0], TOK_INT) == 1) {
  extent = flowc_parse_int_span(((p[0]).lex).input, ((p[0]).cur).start, ((p[0]).cur).end);
  flowc_parser_advance(p);
} else {
  (p[0]).err = 1;
  return AST_NONE;
}
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
  (((p[0]).arena).nodes[id]).ival = extent;
  if (is_mut == 1) {
  flowc_ast_type_set_span_mutable((&(p[0]).arena), id, 1);
}
  return id;
} else {
  return flowc_parse_type(p);
}
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
  if (flowc_parser_span_is(p[0], start, end, "cfn") == 1) {
  if (flowc_parser_check(p[0], TOK_LPAREN) == 1) {
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
  (((p[0]).arena).nodes[id]).ival = (0 - 2);
  (((p[0]).arena).nodes[id]).a = params;
  (((p[0]).arena).nodes[id]).b = ret;
  (((p[0]).arena).nodes[id]).end = ((p[0]).cur).start;
  return id;
}
}
  if (flowc_parser_check(p[0], TOK_LT) == 1) {
  flowc_parser_advance(p);
  if (flowc_parser_check_kw(p[0], KW_MUT) == 1) {
  flowc_parser_advance(p);
}
  int32_t inner = flowc_parse_type(p);
  if (inner == AST_NONE) {
  return AST_NONE;
}
  (((p[0]).arena).nodes[id]).a = inner;
  if (flowc_parser_check(p[0], TOK_COMMA) == 1) {
  flowc_parser_advance(p);
  if (flowc_parser_check(p[0], TOK_INT) == 1) {
  int32_t n = flowc_parse_int_span(((p[0]).lex).input, ((p[0]).cur).start, ((p[0]).cur).end);
  (((p[0]).arena).nodes[id]).ival = n;
  flowc_parser_advance(p);
} else {
  int32_t last = inner;
  int32_t next_ty = flowc_parse_type(p);
  if (next_ty == AST_NONE) {
  return AST_NONE;
}
  (((p[0]).arena).nodes[last]).next = next_ty;
  last = next_ty;
  while (flowc_parser_check(p[0], TOK_COMMA) == 1) {
  flowc_parser_advance(p);
  int32_t nt = flowc_parse_type(p);
  if (nt == AST_NONE) {
  return AST_NONE;
}
  (((p[0]).arena).nodes[last]).next = nt;
  last = nt;
}
}
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
  (((p[0]).arena).nodes[id]).name_start = (tok).start;
  (((p[0]).arena).nodes[id]).name_end = (tok).end;
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
  int32_t pending_type_args = AST_NONE;
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
  if (flowc_parser_check(p[0], TOK_COMMA) == 1) {
  flowc_parser_advance(p);
} else {
  if (flowc_parser_check(p[0], TOK_IDENT) == 1) {
  int32_t ty = flowc_parse_type(p);
  if (ty != AST_NONE) {
  pending_type_args = flowc_ast_chain_push((&(p[0]).arena), pending_type_args, ty);
}
} else {
  if (flowc_parser_check(p[0], TOK_DOT) == 1) {
  flowc_parser_advance(p);
} else {
  ok = 0;
}
}
}
}
}
}
}
  if (ok == 1 && depth == 0) {
  if (pending_type_args != AST_NONE && flowc_parser_check(p[0], TOK_LPAREN) == 1) {
  flowc_parser_advance(p);
  int32_t args = AST_NONE;
  if (flowc_parser_check(p[0], TOK_RPAREN) == 0) {
  int32_t first = flowc_parse_expr(p);
  args = flowc_ast_chain_push((&(p[0]).arena), args, first);
  while (flowc_parser_check(p[0], TOK_COMMA) == 1) {
  flowc_parser_advance(p);
  int32_t a = flowc_parse_expr(p);
  args = flowc_ast_chain_push((&(p[0]).arena), args, a);
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
  (((p[0]).arena).nodes[call]).b = pending_type_args;
  return call;
}
} else {
  (p[0]).lex = saved_lex;
  (p[0]).cur = saved_cur;
  pending_type_args = AST_NONE;
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
  (((p[0]).arena).nodes[lit]).b = pending_type_args;
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
  if ((tok).kind == TOK_BAR) {
  int32_t lam_start = (tok).start;
  flowc_parser_advance(p);
  int32_t params = AST_NONE;
  if (flowc_parser_check(p[0], TOK_BAR) == 0) {
  int32_t loop = 1;
  while (loop == 1) {
  if (flowc_parser_check(p[0], TOK_IDENT) == 0) {
  puts("flowc parse: expected param name in lambda");
  (p[0]).err = 1;
  return AST_NONE;
}
  int32_t pname_s = ((p[0]).cur).start;
  int32_t pname_e = ((p[0]).cur).end;
  flowc_parser_advance(p);
  if (flowc_parser_eat(p, TOK_COLON) == 0) {
  return AST_NONE;
}
  int32_t pty = flowc_parse_type(p);
  if (pty == AST_NONE) {
  return AST_NONE;
}
  int32_t param = flowc_ast_alloc((&(p[0]).arena), AST_PARAM, pname_s, pname_e);
  if (param == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[param]).name_start = pname_s;
  (((p[0]).arena).nodes[param]).name_end = pname_e;
  (((p[0]).arena).nodes[param]).b = pty;
  params = flowc_ast_chain_push((&(p[0]).arena), params, param);
  if (flowc_parser_check(p[0], TOK_COMMA) == 1) {
  flowc_parser_advance(p);
} else {
  loop = 0;
}
}
}
  if (flowc_parser_eat(p, TOK_BAR) == 0) {
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
  if (flowc_parser_check(p[0], TOK_LBRACE) == 0) {
  puts("flowc parse: expected lambda body { ... }");
  (p[0]).err = 1;
  return AST_NONE;
}
  int32_t body = flowc_parse_block(p);
  if (body == AST_NONE) {
  return AST_NONE;
}
  int32_t lam_fn = flowc_ast_alloc((&(p[0]).arena), AST_FN, lam_start, ((p[0]).cur).start);
  if (lam_fn == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[lam_fn]).a = params;
  (((p[0]).arena).nodes[lam_fn]).b = ret_ty;
  (((p[0]).arena).nodes[lam_fn]).c = body;
  (((p[0]).arena).nodes[lam_fn]).ival = 0;
  int32_t lam_name = ((p[0]).arena).len;
  (((p[0]).arena).nodes[lam_fn]).name_start = (0 - lam_name);
  (((p[0]).arena).nodes[lam_fn]).name_end = (0 - lam_name);
  return lam_fn;
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
  if (flowc_parser_check(p[0], TOK_LT) == 1 && base != AST_NONE && (((p[0]).arena).nodes[base]).kind == AST_IDENT) {
  int32_t save_pos = ((p[0]).lex).pos;
  int32_t save_line = ((p[0]).lex).line;
  int32_t save_col = ((p[0]).lex).col;
  int32_t save_kind = ((p[0]).cur).kind;
  int32_t save_kw = ((p[0]).cur).kw;
  int32_t save_start = ((p[0]).cur).start;
  int32_t save_end = ((p[0]).cur).end;
  int32_t save_cur_line = ((p[0]).cur).line;
  int32_t save_cur_col = ((p[0]).cur).col;
  flowc_parser_advance(p);
  int32_t parse_ok = 1;
  int32_t depth = 1;
  int32_t type_args = AST_NONE;
  while (depth > 0 && parse_ok == 1) {
  if (flowc_parser_check(p[0], TOK_EOF) == 1) {
  parse_ok = 0;
} else {
  if (flowc_parser_check(p[0], TOK_GT) == 1) {
  depth = (depth - 1);
  if (depth > 0) {
  flowc_parser_advance(p);
}
} else {
  if (flowc_parser_check(p[0], TOK_SHR) == 1) {
  depth = (depth - 2);
  if (depth > 0) {
  flowc_parser_advance(p);
}
} else {
  if (flowc_parser_check(p[0], TOK_LT) == 1) {
  depth = (depth + 1);
  flowc_parser_advance(p);
} else {
  if (flowc_parser_check(p[0], TOK_COMMA) == 1) {
  flowc_parser_advance(p);
} else {
  if (flowc_parser_check(p[0], TOK_IDENT) == 1) {
  int32_t ty = flowc_parse_type(p);
  if (ty != AST_NONE) {
  type_args = flowc_ast_chain_push((&(p[0]).arena), type_args, ty);
}
} else {
  if (flowc_parser_check(p[0], TOK_DOT) == 1) {
  flowc_parser_advance(p);
} else {
  parse_ok = 0;
}
}
}
}
}
}
}
}
  if (parse_ok == 1 && depth == 0) {
  flowc_parser_advance(p);
  if (flowc_parser_check(p[0], TOK_LPAREN) == 1) {
  flowc_parser_advance(p);
  int32_t args = AST_NONE;
  if (flowc_parser_check(p[0], TOK_RPAREN) == 0) {
  int32_t first = flowc_parse_expr(p);
  args = flowc_ast_chain_push((&(p[0]).arena), args, first);
  while (flowc_parser_check(p[0], TOK_COMMA) == 1) {
  flowc_parser_advance(p);
  int32_t a = flowc_parse_expr(p);
  args = flowc_ast_chain_push((&(p[0]).arena), args, a);
}
}
  if (flowc_parser_eat(p, TOK_RPAREN) == 0) {
  return AST_NONE;
}
  int32_t id = flowc_ast_alloc((&(p[0]).arena), AST_CALL, 0, 0);
  if (id == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[id]).name_start = (((p[0]).arena).nodes[base]).name_start;
  (((p[0]).arena).nodes[id]).name_end = (((p[0]).arena).nodes[base]).name_end;
  (((p[0]).arena).nodes[id]).a = args;
  (((p[0]).arena).nodes[id]).b = type_args;
  base = id;
} else {
  ((p[0]).lex).pos = save_pos;
  ((p[0]).lex).line = save_line;
  ((p[0]).lex).col = save_col;
  ((p[0]).cur).kind = save_kind;
  ((p[0]).cur).kw = save_kw;
  ((p[0]).cur).start = save_start;
  ((p[0]).cur).end = save_end;
  ((p[0]).cur).line = save_cur_line;
  ((p[0]).cur).col = save_cur_col;
  break;
}
} else {
  ((p[0]).lex).pos = save_pos;
  ((p[0]).lex).line = save_line;
  ((p[0]).lex).col = save_col;
  ((p[0]).cur).kind = save_kind;
  ((p[0]).cur).kw = save_kw;
  ((p[0]).cur).start = save_start;
  ((p[0]).cur).end = save_end;
  ((p[0]).cur).line = save_cur_line;
  ((p[0]).cur).col = save_cur_col;
  break;
}
} else {
  if (flowc_parser_check(p[0], TOK_LBRACK) == 1) {
  if (base != AST_NONE && (((p[0]).arena).nodes[base]).kind == AST_IDENT) {
  int32_t bns = (((p[0]).arena).nodes[base]).name_start;
  int32_t bne = (((p[0]).arena).nodes[base]).name_end;
  if (flowc_parser_span_is(p[0], bns, bne, "sortBy") == 1) {
  flowc_parser_advance(p);
  int32_t depth = 1;
  int32_t has_desc = 0;
  while (depth > 0 && (p[0]).err == 0) {
  if (flowc_parser_check(p[0], TOK_LBRACK) == 1) {
  depth = (depth + 1);
}
  if (flowc_parser_check(p[0], TOK_RBRACK) == 1) {
  depth = (depth - 1);
}
  if (depth > 0) {
  if (flowc_parser_check(p[0], TOK_IDENT) == 1) {
  int32_t ts = ((p[0]).cur).start;
  int32_t te = ((p[0]).cur).end;
  if (flowc_parser_span_is(p[0], ts, te, "desc") == 1) {
  has_desc = 1;
}
  if (flowc_parser_span_is(p[0], ts, te, "descending") == 1) {
  has_desc = 1;
}
}
  flowc_parser_advance(p);
}
}
  if (depth == 0) {
  flowc_parser_advance(p);
}
  (((p[0]).arena).nodes[base]).ival = has_desc;
} else {
  flowc_parser_advance(p);
  int32_t idx = flowc_parse_expr(p);
  if (flowc_parser_check(p[0], TOK_DOTDOT) == 1) {
  flowc_parser_advance(p);
  int32_t end_idx = AST_NONE;
  if (flowc_parser_check(p[0], TOK_RBRACK) == 0) {
  end_idx = flowc_parse_expr(p);
}
  if (flowc_parser_eat(p, TOK_RBRACK) == 0) {
  return AST_NONE;
}
  int32_t sid = flowc_ast_alloc((&(p[0]).arena), AST_INDEX, 0, 0);
  if (sid == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[sid]).a = base;
  (((p[0]).arena).nodes[sid]).b = idx;
  (((p[0]).arena).nodes[sid]).c = end_idx;
  (((p[0]).arena).nodes[sid]).ival = 1;
  base = sid;
} else {
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
}
}
} else {
  flowc_parser_advance(p);
  int32_t idx = flowc_parse_expr(p);
  if (flowc_parser_check(p[0], TOK_DOTDOT) == 1) {
  flowc_parser_advance(p);
  int32_t end_idx = AST_NONE;
  if (flowc_parser_check(p[0], TOK_RBRACK) == 0) {
  end_idx = flowc_parse_expr(p);
}
  if (flowc_parser_eat(p, TOK_RBRACK) == 0) {
  return AST_NONE;
}
  int32_t sid = flowc_ast_alloc((&(p[0]).arena), AST_INDEX, 0, 0);
  if (sid == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[sid]).a = base;
  (((p[0]).arena).nodes[sid]).b = idx;
  (((p[0]).arena).nodes[sid]).c = end_idx;
  (((p[0]).arena).nodes[sid]).ival = 1;
  base = sid;
} else {
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
}
}
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
  if ((((p[0]).arena).nodes[base]).kind == AST_FIELD_ACCESS) {
  int32_t recv = (((p[0]).arena).nodes[base]).a;
  if (recv != AST_NONE) {
  (((p[0]).arena).nodes[recv]).next = args;
  args = recv;
}
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
  if ((tok).kind == TOK_KEYWORD && (tok).kw == KW_IF) {
  int32_t start = (tok).start;
  flowc_parser_advance(p);
  int32_t cond = flowc_parse_expr(p);
  if (cond == AST_NONE) {
  return AST_NONE;
}
  if (flowc_parser_check(p[0], TOK_LBRACE) == 0) {
  (p[0]).err = 1;
  return AST_NONE;
}
  flowc_parser_advance(p);
  int32_t then_e = flowc_parse_expr(p);
  if (flowc_parser_check(p[0], TOK_RBRACE) == 0) {
  (p[0]).err = 1;
  return AST_NONE;
}
  flowc_parser_advance(p);
  int32_t else_e = AST_NONE;
  if (flowc_parser_check_kw(p[0], KW_ELSE) == 1) {
  flowc_parser_advance(p);
  if (flowc_parser_check(p[0], TOK_LBRACE) == 0) {
  (p[0]).err = 1;
  return AST_NONE;
}
  flowc_parser_advance(p);
  else_e = flowc_parse_expr(p);
  if (flowc_parser_check(p[0], TOK_RBRACE) == 0) {
  (p[0]).err = 1;
  return AST_NONE;
}
  flowc_parser_advance(p);
}
  int32_t id = flowc_ast_alloc((&(p[0]).arena), AST_IF_EXPR, start, ((p[0]).cur).start);
  if (id == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[id]).a = cond;
  (((p[0]).arena).nodes[id]).b = then_e;
  (((p[0]).arena).nodes[id]).c = else_e;
  return id;
}
  if ((tok).kind == TOK_KEYWORD && (tok).kw == KW_DBG) {
  int32_t start = (tok).start;
  flowc_parser_advance(p);
  int32_t operand = flowc_parse_primary(p);
  int32_t id = flowc_ast_alloc((&(p[0]).arena), AST_UNARY, start, ((p[0]).cur).start);
  if (id == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[id]).ival = KW_DBG;
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
  if (((p).cur).kw == KW_IN) {
  return TOK_IN;
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
  if (op == TOK_LT || op == TOK_LE || op == TOK_GT || op == TOK_GE || op == TOK_IN) {
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
  int32_t result = flowc_parse_binop_rhs(p, 1, lhs);
  while (flowc_parser_check(p[0], TOK_PIPELINE) == 1) {
  flowc_parser_advance(p);
  int32_t rhs = flowc_parse_cast(p);
  if (rhs == AST_NONE) {
  return AST_NONE;
}
  if ((((p[0]).arena).nodes[rhs]).kind == AST_IDENT) {
  int32_t ns = (((p[0]).arena).nodes[rhs]).name_start;
  int32_t ne = (((p[0]).arena).nodes[rhs]).name_end;
  if (flowc_parser_span_is(p[0], ns, ne, "sort") == 1 || flowc_parser_span_is(p[0], ns, ne, "sortBy") == 1) {
  int32_t mods = AST_NONE;
  while (flowc_parser_check(p[0], TOK_IDENT) == 1) {
  int32_t ms = ((p[0]).cur).start;
  int32_t me = ((p[0]).cur).end;
  int32_t mnode = flowc_ast_alloc((&(p[0]).arena), AST_IDENT, ms, me);
  if (mnode == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[mnode]).name_start = ms;
  (((p[0]).arena).nodes[mnode]).name_end = me;
  mods = flowc_ast_chain_push((&(p[0]).arena), mods, mnode);
  flowc_parser_advance(p);
}
  if (mods != AST_NONE) {
  int32_t call = flowc_ast_alloc((&(p[0]).arena), AST_CALL, ns, ne);
  if (call == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[call]).name_start = ns;
  (((p[0]).arena).nodes[call]).name_end = ne;
  (((p[0]).arena).nodes[call]).a = mods;
  rhs = call;
}
}
}
  result = flowc_parse_apply_pipe(p, result, rhs);
  if (result == AST_NONE) {
  return AST_NONE;
}
}
  return result;
}

int32_t flowc_parse_apply_pipe(Parser* p, int32_t left, int32_t right) {
  if ((((p[0]).arena).nodes[right]).kind == AST_CALL) {
  (((p[0]).arena).nodes[right]).a = flowc_ast_chain_push((&(p[0]).arena), left, (((p[0]).arena).nodes[right]).a);
  return right;
}
  int32_t name_src = right;
  if ((((p[0]).arena).nodes[right]).kind == AST_INDEX) {
  name_src = (((p[0]).arena).nodes[right]).a;
}
  int32_t id = flowc_ast_alloc((&(p[0]).arena), AST_CALL, 0, 0);
  if (id == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[id]).a = flowc_ast_chain_push((&(p[0]).arena), AST_NONE, left);
  (((p[0]).arena).nodes[id]).name_start = (((p[0]).arena).nodes[name_src]).name_start;
  (((p[0]).arena).nodes[id]).name_end = (((p[0]).arena).nodes[name_src]).name_end;
  (((p[0]).arena).nodes[id]).ival = (((p[0]).arena).nodes[name_src]).ival;
  return id;
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
  if (k == TOK_INT || k == TOK_FLOAT || k == TOK_STRING || k == TOK_IDENT || k == TOK_LPAREN || k == TOK_LBRACK || k == TOK_BAR) {
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
  if (flowc_parser_check_kw(p[0], KW_PARALLEL) == 1) {
  flowc_parser_advance(p);
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
  int32_t step = AST_NONE;
  if (flowc_parser_check(p[0], TOK_IDENT) == 1) {
  if (flowc_parser_span_is(p[0], ((p[0]).cur).start, ((p[0]).cur).end, "step") == 1) {
  flowc_parser_advance(p);
  step = flowc_parse_expr(p);
}
}
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
  if (step != AST_NONE) {
  (((p[0]).arena).nodes[id]).ival = step;
}
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
  if (flowc_parser_check_kw(p[0], KW_DEFAULT) == 1) {
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
  (((p[0]).arena).nodes[arm]).ival = 1;
  (((p[0]).arena).nodes[arm]).a = AST_NONE;
  (((p[0]).arena).nodes[arm]).b = body;
  arms = flowc_ast_chain_push((&(p[0]).arena), arms, arm);
  if (flowc_parser_check(p[0], TOK_COMMA) == 1) {
  flowc_parser_advance(p);
}
  continue;
}
  if (flowc_parser_check(p[0], TOK_MINUS) == 1) {
  neg = 1;
  flowc_parser_advance(p);
}
  if (flowc_parser_check_kw(p[0], KW_TRUE) == 1) {
  pat = flowc_ast_alloc((&(p[0]).arena), AST_BOOL, ((p[0]).cur).start, ((p[0]).cur).end);
  if (pat == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[pat]).ival = 1;
  flowc_parser_advance(p);
  pat_kind = 0;
} else {
  if (flowc_parser_check_kw(p[0], KW_FALSE) == 1) {
  pat = flowc_ast_alloc((&(p[0]).arena), AST_BOOL, ((p[0]).cur).start, ((p[0]).cur).end);
  if (pat == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[pat]).ival = 0;
  flowc_parser_advance(p);
  pat_kind = 0;
} else {
  if (flowc_parser_check(p[0], TOK_INT) == 1) {
  Token tok = (p[0]).cur;
  pat = flowc_ast_alloc((&(p[0]).arena), AST_INT, (tok).start, (tok).end);
  if (pat == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[pat]).name_start = (tok).start;
  (((p[0]).arena).nodes[pat]).name_end = (tok).end;
  int32_t v = flowc_parse_int_span(((p[0]).lex).input, (tok).start, (tok).end);
  if (neg == 1) {
  v = (0 - v);
}
  (((p[0]).arena).nodes[pat]).ival = v;
  flowc_parser_advance(p);
  pat_kind = 0;
} else {
  if (flowc_parser_check(p[0], TOK_FLOAT) == 1) {
  Token tok = (p[0]).cur;
  pat = flowc_ast_alloc((&(p[0]).arena), AST_FLOAT, (tok).start, (tok).end);
  if (pat == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[pat]).name_start = (tok).start;
  (((p[0]).arena).nodes[pat]).name_end = (tok).end;
  flowc_parser_advance(p);
  pat_kind = 3;
} else {
  if (flowc_parser_check(p[0], TOK_STRING) == 1) {
  Token tok = (p[0]).cur;
  pat = flowc_ast_alloc((&(p[0]).arena), AST_STRING, (tok).start, (tok).end);
  if (pat == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[pat]).name_start = (tok).start;
  (((p[0]).arena).nodes[pat]).name_end = (tok).end;
  flowc_parser_advance(p);
  pat_kind = 4;
} else {
  if (neg == 1 || flowc_parser_check(p[0], TOK_IDENT) == 0) {
  if (flowc_parser_check(p[0], TOK_LBRACK) == 1) {
  flowc_parser_advance(p);
  int32_t elems = AST_NONE;
  while (flowc_parser_check(p[0], TOK_RBRACK) == 0) {
  int32_t sub = AST_NONE;
  if (flowc_parser_check(p[0], TOK_INT) == 1) {
  Token tok = (p[0]).cur;
  sub = flowc_ast_alloc((&(p[0]).arena), AST_INT, (tok).start, (tok).end);
  if (sub == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[sub]).name_start = (tok).start;
  (((p[0]).arena).nodes[sub]).name_end = (tok).end;
  (((p[0]).arena).nodes[sub]).ival = flowc_parse_int_span(((p[0]).lex).input, (tok).start, (tok).end);
  flowc_parser_advance(p);
} else {
  if (flowc_parser_check(p[0], TOK_IDENT) == 1) {
  int32_t bs = ((p[0]).cur).start;
  int32_t be = ((p[0]).cur).end;
  sub = flowc_ast_alloc((&(p[0]).arena), AST_IDENT, bs, be);
  if (sub == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[sub]).name_start = bs;
  (((p[0]).arena).nodes[sub]).name_end = be;
  flowc_parser_advance(p);
} else {
  puts("flowc parse: unsupported list pattern element");
  (p[0]).err = 1;
  return AST_NONE;
}
}
  elems = flowc_ast_chain_push((&(p[0]).arena), elems, sub);
  if (flowc_parser_check(p[0], TOK_COMMA) == 1) {
  flowc_parser_advance(p);
}
}
  flowc_parser_advance(p);
  pat = elems;
  pat_kind = 6;
} else {
  puts("flowc parse: unsupported match pattern (Stage-A: int literal, `_`, or binding ident)");
  (p[0]).err = 1;
  return AST_NONE;
}
} else {
  bind_s = ((p[0]).cur).start;
  bind_e = ((p[0]).cur).end;
  flowc_parser_advance(p);
  if (flowc_parser_check(p[0], TOK_LPAREN) == 1) {
  flowc_parser_advance(p);
  int32_t binds = AST_NONE;
  while (flowc_parser_check(p[0], TOK_RPAREN) == 0) {
  if (flowc_parser_check(p[0], TOK_IDENT) == 0) {
  puts("flowc parse: expected binding in struct pattern");
  (p[0]).err = 1;
  return AST_NONE;
}
  int32_t bs = ((p[0]).cur).start;
  int32_t be = ((p[0]).cur).end;
  int32_t bnode = flowc_ast_alloc((&(p[0]).arena), AST_IDENT, bs, be);
  if (bnode == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[bnode]).name_start = bs;
  (((p[0]).arena).nodes[bnode]).name_end = be;
  binds = flowc_ast_chain_push((&(p[0]).arena), binds, bnode);
  flowc_parser_advance(p);
  if (flowc_parser_check(p[0], TOK_COMMA) == 1) {
  flowc_parser_advance(p);
}
}
  flowc_parser_advance(p);
  pat = binds;
  pat_kind = 5;
} else {
  if ((bind_e - bind_s) == 1 && ((p[0]).lex).input[bind_s] == 95) {
  pat_kind = 1;
} else {
  pat_kind = 2;
}
}
}
}
}
}
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
  if (flowc_parser_check_kw(p[0], KW_DEFER) == 1) {
  int32_t start = ((p[0]).cur).start;
  flowc_parser_advance(p);
  int32_t expr = flowc_parse_expr(p);
  if (expr == AST_NONE) {
  return AST_NONE;
}
  int32_t id = flowc_ast_alloc((&(p[0]).arena), AST_DEFER, start, ((p[0]).cur).start);
  if (id == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[id]).a = expr;
  return id;
}
  if (flowc_parser_check_kw(p[0], KW_EXPECT) == 1) {
  int32_t start = ((p[0]).cur).start;
  flowc_parser_advance(p);
  int32_t cond = flowc_parse_expr(p);
  if (cond == AST_NONE) {
  return AST_NONE;
}
  int32_t id = flowc_ast_alloc((&(p[0]).arena), AST_UNARY, start, ((p[0]).cur).start);
  if (id == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[id]).ival = KW_EXPECT;
  (((p[0]).arena).nodes[id]).a = cond;
  return id;
}
  if (flowc_parser_check(p[0], TOK_IDENT) == 1) {
  int32_t saved_start = ((p[0]).cur).start;
  int32_t expr = flowc_parse_expr(p);
  if (expr == AST_NONE) {
  return AST_NONE;
}
  int32_t lk = (((p[0]).arena).nodes[expr]).kind;
  if (flowc_parser_check(p[0], TOK_EQ) == 1 && (lk == AST_IDENT || lk == AST_FIELD_ACCESS || lk == AST_INDEX)) {
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
  if (compound_op != 0 && (lk == AST_IDENT || lk == AST_FIELD_ACCESS || lk == AST_INDEX)) {
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
  int32_t fn_type_params = AST_NONE;
  if (flowc_parser_check(p[0], TOK_LT) == 1) {
  is_generic = 1;
  flowc_parser_advance(p);
  int32_t depth = 1;
  while (depth > 0 && flowc_parser_check(p[0], TOK_EOF) == 0) {
  if (flowc_parser_check(p[0], TOK_LT) == 1) {
  depth = (depth + 1);
  flowc_parser_advance(p);
} else {
  if (flowc_parser_check(p[0], TOK_GT) == 1) {
  depth = (depth - 1);
  if (depth > 0) {
  flowc_parser_advance(p);
}
} else {
  if (flowc_parser_check(p[0], TOK_SHR) == 1) {
  depth = (depth - 2);
  if (depth > 0) {
  flowc_parser_advance(p);
}
} else {
  if (flowc_parser_check(p[0], TOK_IDENT) == 1) {
  int32_t tp_s = ((p[0]).cur).start;
  int32_t tp_e = ((p[0]).cur).end;
  flowc_parser_advance(p);
  if (flowc_parser_check(p[0], TOK_COLON) == 1) {
  flowc_parser_advance(p);
  if (flowc_parser_check(p[0], TOK_IDENT) == 1) {
  flowc_parser_advance(p);
}
}
  int32_t tp_node = flowc_ast_alloc((&(p[0]).arena), AST_TYPE, tp_s, tp_e);
  if (tp_node != AST_NONE) {
  (((p[0]).arena).nodes[tp_node]).name_start = tp_s;
  (((p[0]).arena).nodes[tp_node]).name_end = tp_e;
  fn_type_params = flowc_ast_chain_push((&(p[0]).arena), fn_type_params, tp_node);
}
} else {
  if (flowc_parser_check(p[0], TOK_COMMA) == 1) {
  flowc_parser_advance(p);
} else {
  flowc_parser_advance(p);
}
}
}
}
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
  int32_t ntp = 0;
  int32_t tp = fn_type_params;
  while (tp != AST_NONE) {
  ntp = (ntp + 1);
  tp = (((p[0]).arena).nodes[tp]).next;
}
  (((p[0]).arena).nodes[id]).ival = ntp;
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
  int32_t type_params = AST_NONE;
  if (flowc_parser_check(p[0], TOK_LT) == 1) {
  flowc_parser_advance(p);
  int32_t depth = 1;
  while (depth > 0 && flowc_parser_check(p[0], TOK_EOF) == 0) {
  if (flowc_parser_check(p[0], TOK_LT) == 1) {
  depth = (depth + 1);
  flowc_parser_advance(p);
} else {
  if (flowc_parser_check(p[0], TOK_GT) == 1) {
  depth = (depth - 1);
  if (depth > 0) {
  flowc_parser_advance(p);
}
} else {
  if (flowc_parser_check(p[0], TOK_SHR) == 1) {
  depth = (depth - 2);
  if (depth > 0) {
  flowc_parser_advance(p);
}
} else {
  if (flowc_parser_check(p[0], TOK_IDENT) == 1) {
  int32_t tp_s = ((p[0]).cur).start;
  int32_t tp_e = ((p[0]).cur).end;
  flowc_parser_advance(p);
  if (flowc_parser_check(p[0], TOK_COLON) == 1) {
  flowc_parser_advance(p);
  if (flowc_parser_check(p[0], TOK_IDENT) == 1) {
  flowc_parser_advance(p);
}
}
  int32_t tp_node = flowc_ast_alloc((&(p[0]).arena), AST_TYPE, tp_s, tp_e);
  if (tp_node != AST_NONE) {
  (((p[0]).arena).nodes[tp_node]).name_start = tp_s;
  (((p[0]).arena).nodes[tp_node]).name_end = tp_e;
  type_params = flowc_ast_chain_push((&(p[0]).arena), type_params, tp_node);
}
} else {
  if (flowc_parser_check(p[0], TOK_COMMA) == 1) {
  flowc_parser_advance(p);
} else {
  flowc_parser_advance(p);
}
}
}
}
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
  (((p[0]).arena).nodes[id]).b = type_params;
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
  (((p[0]).arena).nodes[tid]).name_start = tns;
  (((p[0]).arena).nodes[tid]).name_end = tne;
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
  (((p[0]).arena).nodes[tid]).name_start = tns;
  (((p[0]).arena).nodes[tid]).name_end = tne;
  fns = flowc_ast_chain_push((&(p[0]).arena), fns, tid);
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

int32_t flowc_parse_enum(Parser* p) {
  int32_t start = ((p[0]).cur).start;
  if (flowc_parser_eat_kw(p, KW_ENUM) == 0) {
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
}
}
  if (depth > 0) {
  flowc_parser_advance(p);
}
}
  if (flowc_parser_check(p[0], TOK_GT) == 1) {
  flowc_parser_advance(p);
}
}
  if (flowc_parser_eat(p, TOK_LBRACE) == 0) {
  return AST_NONE;
}
  int32_t variants = AST_NONE;
  int32_t idx = 0;
  while (flowc_parser_check(p[0], TOK_RBRACE) == 0 && flowc_parser_check(p[0], TOK_EOF) == 0) {
  if (flowc_parser_check(p[0], TOK_IDENT) == 0) {
  (p[0]).err = 1;
  return AST_NONE;
}
  int32_t vns = ((p[0]).cur).start;
  int32_t vne = ((p[0]).cur).end;
  flowc_parser_advance(p);
  int32_t vid = flowc_ast_alloc((&(p[0]).arena), AST_ENUM_VARIANT, vns, vne);
  if (vid == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[vid]).name_start = vns;
  (((p[0]).arena).nodes[vid]).name_end = vne;
  (((p[0]).arena).nodes[vid]).ival = idx;
  idx = (idx + 1);
  if (flowc_parser_check(p[0], TOK_LPAREN) == 1) {
  flowc_parser_advance(p);
  int32_t pdepth = 1;
  while (pdepth > 0 && flowc_parser_check(p[0], TOK_EOF) == 0) {
  if (flowc_parser_check(p[0], TOK_LPAREN) == 1) {
  pdepth = (pdepth + 1);
} else {
  if (flowc_parser_check(p[0], TOK_RPAREN) == 1) {
  pdepth = (pdepth - 1);
}
}
  if (pdepth > 0) {
  flowc_parser_advance(p);
}
}
  if (flowc_parser_check(p[0], TOK_RPAREN) == 1) {
  flowc_parser_advance(p);
}
}
  variants = flowc_ast_chain_push((&(p[0]).arena), variants, vid);
  if (flowc_parser_check(p[0], TOK_COMMA) == 1) {
  flowc_parser_advance(p);
}
}
  if (flowc_parser_eat(p, TOK_RBRACE) == 0) {
  return AST_NONE;
}
  int32_t id = flowc_ast_alloc((&(p[0]).arena), AST_ENUM, start, ((p[0]).cur).start);
  if (id == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  (((p[0]).arena).nodes[id]).name_start = ns;
  (((p[0]).arena).nodes[id]).name_end = ne;
  (((p[0]).arena).nodes[id]).a = variants;
  return id;
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
  if (flowc_parser_check_kw(p[0], KW_IMPORT) == 1) {
  return flowc_parse_import(p);
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
  int32_t attr_name = (-1);
  int32_t attr_name_end = (-1);
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
  (((p[0]).arena).nodes[cid]).name_start = hdr_start;
  (((p[0]).arena).nodes[cid]).name_end = hdr_end;
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
  int32_t cid = flowc_ast_alloc((&(p[0]).arena), AST_C_EMBED, code_start, code_end);
  if (cid != AST_NONE) {
  (((p[0]).arena).nodes[cid]).name_start = code_start;
  (((p[0]).arena).nodes[cid]).name_end = code_end;
  items = flowc_ast_chain_push((&(p[0]).arena), items, cid);
}
}
  continue;
}
  if (attr_name >= 0 && flowc_parser_span_is(p[0], attr_name, attr_name_end, "cImport") == 1) {
  flowc_parser_advance(p);
  if (flowc_parser_check(p[0], TOK_STRING) == 1) {
  int32_t hdr_start = ((p[0]).cur).start;
  int32_t hdr_end = ((p[0]).cur).end;
  flowc_parser_advance(p);
  if (flowc_parser_check(p[0], TOK_RPAREN) == 1) {
  flowc_parser_advance(p);
}
  if (flowc_parser_check_kw(p[0], KW_AS) == 1) {
  flowc_parser_advance(p);
  if (flowc_parser_check(p[0], TOK_IDENT) == 1) {
  flowc_parser_advance(p);
}
}
  int32_t cid = flowc_ast_alloc((&(p[0]).arena), AST_C_IMPORT, hdr_start, hdr_end);
  if (cid != AST_NONE) {
  (((p[0]).arena).nodes[cid]).name_start = hdr_start;
  (((p[0]).arena).nodes[cid]).name_end = hdr_end;
  items = flowc_ast_chain_push((&(p[0]).arena), items, cid);
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
  if (flowc_parser_check_kw(p[0], KW_ENUM) == 1) {
  item = flowc_parse_enum(p);
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
  if (flowc_parser_check_kw(p[0], KW_TRAIT) == 1 || flowc_parser_check_kw(p[0], KW_IMPL) == 1 || flowc_parser_check_kw(p[0], KW_TEST) == 1) {
  int32_t ti_start = ((p[0]).cur).start;
  flowc_parser_advance(p);
  if (flowc_parser_check(p[0], TOK_IDENT) == 1) {
  flowc_parser_advance(p);
}
  while (flowc_parser_check(p[0], TOK_LBRACE) == 0 && flowc_parser_check(p[0], TOK_EOF) == 0) {
  flowc_parser_advance(p);
}
  flowc_parser_skip_brace_block(p);
  item = flowc_ast_alloc((&(p[0]).arena), AST_EXPR_STMT, ti_start, ((p[0]).cur).start);
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


static const int32_t FLOWC_IO_SEEK_SET = 0;
static const int32_t FLOWC_IO_SEEK_END = 2;

typedef struct CgenBuf {
  uint8_t* out;
  int32_t cap;
  int32_t len;
  int32_t err;
  uint8_t* sigs;
  int32_t sigs_len;
  uint8_t* cembed_names;
  int32_t* cembed_offs;
  int32_t* cembed_lens;
  int32_t cembed_count;
  int32_t* cap_starts;
  int32_t* cap_ends;
  int32_t cap_count;
  int32_t in_lambda;
  int32_t* lambda_cap_lambda;
  int32_t* lambda_cap_start;
  int32_t* lambda_cap_end;
  int32_t lambda_cap_count;
  int32_t* mono_tp_starts;
  int32_t* mono_tp_ends;
  int32_t* mono_tp_concrete;
  int32_t mono_ntp;
  int32_t cur_fn;
} CgenBuf;

static const int32_t FLOWC_CGEN_MAX_TP = 8;
CgenBuf flowc_cgen_buf_init(uint8_t* out, int32_t cap);
void flowc_cgen_putc(CgenBuf* w, int32_t c);
void flowc_cgen_puts(CgenBuf* w, const char* s);
void flowc_cgen_put_span(CgenBuf* w, uint8_t* src, int32_t start, int32_t end);
void flowc_cgen_put_i32(CgenBuf* w, int32_t val);
void flowc_cgen_put_u64_hex(CgenBuf* w, uint64_t val);
void flowc_cgen_emit_int_literal(CgenBuf* w, uint8_t* src, int32_t start, int32_t end);
int32_t flowc_cgen_span_eq(uint8_t* src, int32_t a0, int32_t a1, int32_t b0, int32_t b1);
int32_t flowc_cgen_span_is(uint8_t* src, int32_t start, int32_t end, const char* lit);
void flowc_cgen_put_ident(CgenBuf* w, uint8_t* src, int32_t start, int32_t end);
int32_t flowc_cgen_is_struct_type(AstArena arena, uint8_t* src, int32_t ty);
void flowc_cgen_emit_type(CgenBuf* w, AstArena arena, uint8_t* src, int32_t ty);
int32_t flowc_cgen_find_fn(AstArena arena, uint8_t* src, int32_t start, int32_t end);
int32_t flowc_cgen_count_overloads(AstArena arena, uint8_t* src, int32_t start, int32_t end);
void flowc_cgen_put_mangled_fn(CgenBuf* w, AstArena arena, uint8_t* src, int32_t fn_id);
int32_t flowc_cgen_resolve_overload(AstArena arena, uint8_t* src, int32_t start, int32_t end, int32_t call_id);
int32_t flowc_cgen_infer_arg_type(AstArena arena, uint8_t* src, int32_t arg_id);
int32_t flowc_cgen_find_type_by_name(AstArena arena, uint8_t* src, uint8_t* name);
int32_t flowc_cgen_infer_type_node(AstArena arena, uint8_t* src, int32_t init);
int32_t flowc_cgen_sig_find(uint8_t* buf, int32_t blen, uint8_t* src, int32_t start, int32_t end);
int32_t flowc_cgen_write_sig_type(CgenBuf* w, AstArena arena, uint8_t* src, int32_t call);
int32_t flowc_cgen_write_lit_type(CgenBuf* w, AstArena arena, uint8_t* src, int32_t init);
int32_t flowc_cgen_type_is_string(AstArena arena, uint8_t* src, int32_t ty);
int32_t flowc_cgen_sig_is_string(CgenBuf* w, AstArena arena, uint8_t* src, int32_t call);
int32_t flowc_cgen_expr_is_string(CgenBuf* w, AstArena arena, uint8_t* src, int32_t id);
int32_t flowc_cgen_ident_is_string(AstArena arena, uint8_t* src, int32_t id);
int32_t flowc_cgen_is_str_concat(CgenBuf* w, AstArena arena, uint8_t* src, int32_t id);
int32_t flowc_cgen_sig_put(AstArena arena, uint8_t* src, uint8_t* buf, int32_t cap, int32_t len, int32_t fn, int32_t rt);
int32_t flowc_cgen_binop_needs_parens(int32_t op);
void flowc_cgen_emit_binop_child(CgenBuf* w, AstArena arena, uint8_t* src, int32_t child, int32_t parent_op);
void flowc_cgen_emit_binop_op(CgenBuf* w, int32_t op);
void flowc_cgen_emit_print_intrinsic(CgenBuf* w, AstArena arena, uint8_t* src, int32_t id, int32_t newline);
void flowc_cgen_scan_captures(CgenBuf* w, AstArena arena, uint8_t* src, int32_t id, int32_t* param_spans, int32_t nparams);
int32_t flowc_cgen_scan_lambda_caps(AstArena arena, uint8_t* src, int32_t id, int32_t* buf, int32_t count, int32_t* param_spans, int32_t nparams);
int32_t flowc_cgen_is_captured(CgenBuf* w, uint8_t* src, int32_t ns, int32_t ne);
int32_t flowc_cgen_is_span_var(AstArena arena, uint8_t* src, int32_t id);
int32_t flowc_cgen_var_elem_type(AstArena arena, uint8_t* src, int32_t id);
int32_t flowc_cgen_fn_param_is_span(AstArena arena, uint8_t* src, int32_t fn_id, int32_t param_idx);
int32_t flowc_cgen_is_array_var(AstArena arena, uint8_t* src, int32_t id);
int32_t flowc_cgen_array_var_size(AstArena arena, uint8_t* src, int32_t id);
int32_t flowc_cgen_find_enum_variant(AstArena arena, uint8_t* src, int32_t ns, int32_t ne);
void flowc_cgen_emit_expr(CgenBuf* w, AstArena arena, uint8_t* src, int32_t id);
void flowc_cgen_emit_block(CgenBuf* w, AstArena arena, uint8_t* src, int32_t id);
void flowc_cgen_emit_stmt(CgenBuf* w, AstArena arena, uint8_t* src, int32_t id);
void flowc_cgen_emit_param(CgenBuf* w, AstArena arena, uint8_t* src, int32_t id);
int32_t flowc_cgen_is_cli_main(AstArena arena, uint8_t* src, int32_t id);
int32_t flowc_cgen_is_libc_fn(AstArena arena, uint8_t* src, int32_t id);
void flowc_cgen_emit_fn(CgenBuf* w, AstArena arena, uint8_t* src, int32_t id);
void flowc_cgen_emit_fn_proto(CgenBuf* w, AstArena arena, uint8_t* src, int32_t id);
void flowc_cgen_emit_const(CgenBuf* w, AstArena arena, uint8_t* src, int32_t id);
int32_t flowc_cgen_find_tp(uint8_t* src, int32_t ns, int32_t ne, int32_t* tp_starts, int32_t* tp_ends, int32_t ntp);
void flowc_cgen_emit_type_subst(CgenBuf* w, AstArena arena, uint8_t* src, int32_t ty, int32_t* tp_starts, int32_t* tp_ends, int32_t* tp_concrete, int32_t ntp);
void flowc_cgen_emit_struct_mono(CgenBuf* w, AstArena arena, uint8_t* src, int32_t id, int32_t* tp_starts, int32_t* tp_ends, int32_t* tp_concrete, int32_t ntp);
void flowc_cgen_emit_struct(CgenBuf* w, AstArena arena, uint8_t* src, int32_t id);
int32_t flowc_cgen_unwrap(AstArena arena, int32_t item, int32_t want);
int32_t flowc_cgen_pp_is_keyword(uint8_t* text, int32_t start, int32_t end);
int32_t flowc_cgen_pp_is_macro_fn(uint8_t* text, int32_t start, int32_t end);
int32_t flowc_cgen_pp_contains(uint8_t* text, int32_t start, int32_t end, const char* lit);
void flowc_cgen_emit_cimport(CgenBuf* w, uint8_t* src, int32_t name_start, int32_t name_end);
void flowc_cgen_scan_cembed_names(CgenBuf* w, uint8_t* src, int32_t start, int32_t end);
int32_t flowc_cgen_is_cembed_fn(CgenBuf* w, uint8_t* src, int32_t ns, int32_t ne);
int32_t flowc_cgen_emit_sigs(AstArena arena, int32_t root, uint8_t* src, uint8_t* out, int32_t out_cap, int32_t flags, uint8_t* sigs, int32_t sigs_len);
int32_t flowc_cgen_emit_ex(AstArena arena, int32_t root, uint8_t* src, uint8_t* out, int32_t out_cap, int32_t flags);
int32_t flowc_cgen_is_type_param_name(AstArena arena, uint8_t* src, int32_t ns, int32_t ne);
int32_t flowc_cgen_mono_hash(uint8_t* src, int32_t ns, int32_t ne, int32_t type_args, AstArena arena);
void flowc_cgen_emit_mono(CgenBuf* w, AstArena arena, uint8_t* src, int32_t root);
int32_t flowc_cgen_emit(AstArena arena, int32_t root, uint8_t* src, uint8_t* out, int32_t out_cap);
int32_t flowc_cgen_collect_sigs(AstArena arena, int32_t root, uint8_t* src, uint8_t* buf, int32_t cap, int32_t len);
CgenBuf flowc_cgen_buf_init(uint8_t* out, int32_t cap) {
  return (CgenBuf){ .out = out, .cap = cap, .len = 0, .err = 0, .sigs = NULL, .sigs_len = 0, .cembed_names = NULL, .cembed_offs = NULL, .cembed_lens = NULL, .cembed_count = 0, .cap_starts = NULL, .cap_ends = NULL, .cap_count = 0, .in_lambda = 0, .lambda_cap_lambda = NULL, .lambda_cap_start = NULL, .lambda_cap_end = NULL, .lambda_cap_count = 0, .mono_tp_starts = NULL, .mono_tp_ends = NULL, .mono_tp_concrete = NULL, .mono_ntp = 0, .cur_fn = AST_NONE };
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

void flowc_cgen_put_u64_hex(CgenBuf* w, uint64_t val) {
  uint8_t hex[16] = { 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 97, 98, 99, 100, 101, 102 };
  uint8_t digits[16] = { 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
  uint64_t v = val;
  int32_t n = 0;
  if (v == 0) {
  flowc_cgen_putc(w, 48);
  return;
}
  while (v > 0) {
  digits[n] = hex[(int32_t)((v & 15))];
  v = (v >> 4);
  n = (n + 1);
}
  int32_t i = n;
  while (i > 0) {
  i = (i - 1);
  flowc_cgen_putc(w, digits[i]);
}
}

void flowc_cgen_emit_int_literal(CgenBuf* w, uint8_t* src, int32_t start, int32_t end) {
  uint64_t hi = 0;
  uint64_t lo = 0;
  int32_t i = start;
  while (i < end) {
  uint8_t c = src[i];
  if (c < 48 || c > 57) {
  flowc_cgen_put_span(w, src, start, end);
  return;
}
  uint64_t d = (uint64_t)((c - 48));
  uint64_t new_lo = ((lo * 10) + d);
  uint64_t carry = 0;
  if (new_lo < lo) {
  carry = 1;
}
  lo = new_lo;
  hi = ((hi * 10) + carry);
  i = (i + 1);
}
  if (hi == 0) {
  flowc_cgen_put_span(w, src, start, end);
  return;
}
  flowc_cgen_puts(w, "((__int128)0x");
  flowc_cgen_put_u64_hex(w, hi);
  flowc_cgen_puts(w, "ULL << 64 | (__int128)0x");
  flowc_cgen_put_u64_hex(w, lo);
  flowc_cgen_puts(w, "ULL)");
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

void flowc_cgen_put_ident(CgenBuf* w, uint8_t* src, int32_t start, int32_t end) {
  if (flowc_cgen_span_is(src, start, end, "double") == 1) {
  flowc_cgen_puts(w, "_flow_double");
  return;
}
  if (flowc_cgen_span_is(src, start, end, "float") == 1) {
  flowc_cgen_puts(w, "_flow_float");
  return;
}
  if (flowc_cgen_span_is(src, start, end, "int") == 1) {
  flowc_cgen_puts(w, "_flow_int");
  return;
}
  if (flowc_cgen_span_is(src, start, end, "char") == 1) {
  flowc_cgen_puts(w, "_flow_char");
  return;
}
  if (flowc_cgen_span_is(src, start, end, "long") == 1) {
  flowc_cgen_puts(w, "_flow_long");
  return;
}
  if (flowc_cgen_span_is(src, start, end, "short") == 1) {
  flowc_cgen_puts(w, "_flow_short");
  return;
}
  if (flowc_cgen_span_is(src, start, end, "switch") == 1) {
  flowc_cgen_puts(w, "_flow_switch");
  return;
}
  if (flowc_cgen_span_is(src, start, end, "case") == 1) {
  flowc_cgen_puts(w, "_flow_case");
  return;
}
  if (flowc_cgen_span_is(src, start, end, "default") == 1) {
  flowc_cgen_puts(w, "_flow_default");
  return;
}
  if (flowc_cgen_span_is(src, start, end, "do") == 1) {
  flowc_cgen_puts(w, "_flow_do");
  return;
}
  if (flowc_cgen_span_is(src, start, end, "for") == 1) {
  flowc_cgen_puts(w, "_flow_for");
  return;
}
  if (flowc_cgen_span_is(src, start, end, "while") == 1) {
  flowc_cgen_puts(w, "_flow_while");
  return;
}
  if (flowc_cgen_span_is(src, start, end, "goto") == 1) {
  flowc_cgen_puts(w, "_flow_goto");
  return;
}
  if (flowc_cgen_span_is(src, start, end, "register") == 1) {
  flowc_cgen_puts(w, "_flow_register");
  return;
}
  if (flowc_cgen_span_is(src, start, end, "auto") == 1) {
  flowc_cgen_puts(w, "_flow_auto");
  return;
}
  if (flowc_cgen_span_is(src, start, end, "extern") == 1) {
  flowc_cgen_puts(w, "_flow_extern");
  return;
}
  if (flowc_cgen_span_is(src, start, end, "static") == 1) {
  flowc_cgen_puts(w, "_flow_static");
  return;
}
  if (flowc_cgen_span_is(src, start, end, "inline") == 1) {
  flowc_cgen_puts(w, "_flow_inline");
  return;
}
  if (flowc_cgen_span_is(src, start, end, "struct") == 1) {
  flowc_cgen_puts(w, "_flow_struct");
  return;
}
  if (flowc_cgen_span_is(src, start, end, "union") == 1) {
  flowc_cgen_puts(w, "_flow_union");
  return;
}
  if (flowc_cgen_span_is(src, start, end, "enum") == 1) {
  flowc_cgen_puts(w, "_flow_enum");
  return;
}
  if (flowc_cgen_span_is(src, start, end, "typedef") == 1) {
  flowc_cgen_puts(w, "_flow_typedef");
  return;
}
  if (flowc_cgen_span_is(src, start, end, "sizeof") == 1) {
  flowc_cgen_puts(w, "_flow_sizeof");
  return;
}
  if (flowc_cgen_span_is(src, start, end, "return") == 1) {
  flowc_cgen_puts(w, "_flow_return");
  return;
}
  if (flowc_cgen_span_is(src, start, end, "void") == 1) {
  flowc_cgen_puts(w, "_flow_void");
  return;
}
  if (flowc_cgen_span_is(src, start, end, "volatile") == 1) {
  flowc_cgen_puts(w, "_flow_volatile");
  return;
}
  if (flowc_cgen_span_is(src, start, end, "const") == 1) {
  flowc_cgen_puts(w, "_flow_const");
  return;
}
  if (flowc_cgen_span_is(src, start, end, "signed") == 1) {
  flowc_cgen_puts(w, "_flow_signed");
  return;
}
  if (flowc_cgen_span_is(src, start, end, "unsigned") == 1) {
  flowc_cgen_puts(w, "_flow_unsigned");
  return;
}
  if (flowc_cgen_span_is(src, start, end, "continue") == 1) {
  flowc_cgen_puts(w, "_flow_continue");
  return;
}
  if (flowc_cgen_span_is(src, start, end, "break") == 1) {
  flowc_cgen_puts(w, "_flow_break");
  return;
}
  if (flowc_cgen_span_is(src, start, end, "if") == 1) {
  flowc_cgen_puts(w, "_flow_if");
  return;
}
  if (flowc_cgen_span_is(src, start, end, "else") == 1) {
  flowc_cgen_puts(w, "_flow_else");
  return;
}
  flowc_cgen_put_span(w, src, start, end);
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
  if ((w[0]).mono_ntp > 0) {
  int32_t ns = ((arena).nodes[ty]).name_start;
  int32_t ne = ((arena).nodes[ty]).name_end;
  int32_t inner = ((arena).nodes[ty]).a;
  if (inner == AST_NONE && ns > 0) {
  int32_t idx = flowc_cgen_find_tp(src, ns, ne, (w[0]).mono_tp_starts, (w[0]).mono_tp_ends, (w[0]).mono_ntp);
  if (idx >= 0) {
  flowc_cgen_emit_type(w, arena, src, (w[0]).mono_tp_concrete[idx]);
  return;
}
}
  if (inner != AST_NONE && flowc_cgen_span_is(src, ns, ne, "ptr") == 1) {
  int32_t inner_idx = flowc_cgen_find_tp(src, ((arena).nodes[inner]).name_start, ((arena).nodes[inner]).name_end, (w[0]).mono_tp_starts, (w[0]).mono_tp_ends, (w[0]).mono_ntp);
  if (inner_idx >= 0) {
  flowc_cgen_emit_type(w, arena, src, (w[0]).mono_tp_concrete[inner_idx]);
  flowc_cgen_putc(w, 42);
  return;
}
}
  if (inner != AST_NONE && flowc_cgen_is_struct_type(arena, src, ty) == 1) {
  flowc_cgen_put_span(w, src, ns, ne);
  int32_t ta = inner;
  while (ta != AST_NONE) {
  if (((arena).nodes[ta]).kind == AST_TYPE) {
  int32_t ta_idx = flowc_cgen_find_tp(src, ((arena).nodes[ta]).name_start, ((arena).nodes[ta]).name_end, (w[0]).mono_tp_starts, (w[0]).mono_tp_ends, (w[0]).mono_ntp);
  flowc_cgen_putc(w, 95);
  if (ta_idx >= 0) {
  flowc_cgen_put_span(w, src, ((arena).nodes[(w[0]).mono_tp_concrete[ta_idx]]).name_start, ((arena).nodes[(w[0]).mono_tp_concrete[ta_idx]]).name_end);
} else {
  flowc_cgen_put_span(w, src, ((arena).nodes[ta]).name_start, ((arena).nodes[ta]).name_end);
}
}
  ta = ((arena).nodes[ta]).next;
}
  return;
}
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
  if (inner != AST_NONE && ns == 0 && ne == 0 && ((arena).nodes[ty]).ival == 0) {
  if (((arena).nodes[inner]).kind == AST_TYPE) {
  if (((arena).nodes[inner]).name_start > 0) {
  flowc_cgen_puts(w, "flowc_span_");
  flowc_cgen_emit_type(w, arena, src, inner);
  return;
}
}
}
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
  if (inner != AST_NONE && flowc_cgen_span_is(src, ns, ne, "span") == 1) {
  flowc_cgen_puts(w, "flowc_span_");
  flowc_cgen_emit_type(w, arena, src, inner);
  return;
}
  if (flowc_cgen_is_struct_type(arena, src, ty) == 1) {
  flowc_cgen_put_span(w, src, ns, ne);
  int32_t ta = inner;
  while (ta != AST_NONE) {
  if (((arena).nodes[ta]).kind == AST_TYPE) {
  flowc_cgen_putc(w, 95);
  flowc_cgen_put_span(w, src, ((arena).nodes[ta]).name_start, ((arena).nodes[ta]).name_end);
}
  ta = ((arena).nodes[ta]).next;
}
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
  if (flowc_cgen_span_is(src, ns, ne, "i128") == 1) {
  flowc_cgen_puts(w, "__int128");
  return;
}
  if (flowc_cgen_span_is(src, ns, ne, "u128") == 1) {
  flowc_cgen_puts(w, "unsigned __int128");
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

int32_t flowc_cgen_count_overloads(AstArena arena, uint8_t* src, int32_t start, int32_t end) {
  int32_t count = 0;
  int32_t i = 0;
  while (i < (arena).len) {
  if (((arena).nodes[i]).kind == AST_FN) {
  if (((arena).nodes[i]).c != AST_NONE) {
  if (flowc_cgen_span_eq(src, start, end, ((arena).nodes[i]).name_start, ((arena).nodes[i]).name_end) == 1) {
  count = (count + 1);
}
}
}
  i = (i + 1);
}
  return count;
}

void flowc_cgen_put_mangled_fn(CgenBuf* w, AstArena arena, uint8_t* src, int32_t fn_id) {
  flowc_cgen_put_span(w, src, ((arena).nodes[fn_id]).name_start, ((arena).nodes[fn_id]).name_end);
  int32_t param = ((arena).nodes[fn_id]).a;
  while (param != AST_NONE) {
  int32_t ty = ((arena).nodes[param]).a;
  if (ty != AST_NONE) {
  flowc_cgen_putc(w, 95);
  flowc_cgen_put_span(w, src, ((arena).nodes[ty]).name_start, ((arena).nodes[ty]).name_end);
}
  param = ((arena).nodes[param]).next;
}
}

int32_t flowc_cgen_resolve_overload(AstArena arena, uint8_t* src, int32_t start, int32_t end, int32_t call_id) {
  int32_t best = AST_NONE;
  int32_t best_score = (0 - 1);
  int32_t i = 0;
  while (i < (arena).len) {
  if (((arena).nodes[i]).kind == AST_FN) {
  if (((arena).nodes[i]).c != AST_NONE) {
  if (flowc_cgen_span_eq(src, start, end, ((arena).nodes[i]).name_start, ((arena).nodes[i]).name_end) == 1) {
  int32_t score = 0;
  int32_t arg = ((arena).nodes[call_id]).a;
  int32_t param = ((arena).nodes[i]).a;
  int32_t exact = 1;
  while (arg != AST_NONE && param != AST_NONE) {
  int32_t arg_ty = flowc_cgen_infer_arg_type(arena, src, arg);
  int32_t param_ty = ((arena).nodes[param]).a;
  if (arg_ty != AST_NONE && param_ty != AST_NONE) {
  if (flowc_cgen_span_eq(src, ((arena).nodes[arg_ty]).name_start, ((arena).nodes[arg_ty]).name_end, ((arena).nodes[param_ty]).name_start, ((arena).nodes[param_ty]).name_end) == 1) {
  score = (score + 10);
} else {
  score = (score + 1);
  exact = 0;
}
} else {
  score = (score + 1);
}
  arg = ((arena).nodes[arg]).next;
  param = ((arena).nodes[param]).next;
}
  if (exact == 1 && score > best_score) {
  best = i;
  best_score = score;
} else {
  if (best == AST_NONE) {
  best = i;
  best_score = score;
}
}
}
}
}
  i = (i + 1);
}
  return best;
}

int32_t flowc_cgen_infer_arg_type(AstArena arena, uint8_t* src, int32_t arg_id) {
  if (arg_id == AST_NONE) {
  return AST_NONE;
}
  int32_t kind = ((arena).nodes[arg_id]).kind;
  if (kind == AST_INT) {
  uint8_t i32_name[4] = { 105, 51, 50, 0 };
  return flowc_cgen_find_type_by_name(arena, src, (&i32_name[0]));
}
  if (kind == AST_CAST) {
  return ((arena).nodes[arg_id]).b;
}
  if (kind == AST_IDENT) {
  int32_t i = 0;
  while (i < (arena).len) {
  if (((arena).nodes[i]).kind == AST_LET || ((arena).nodes[i]).kind == AST_PARAM) {
  if (flowc_cgen_span_eq(src, ((arena).nodes[arg_id]).name_start, ((arena).nodes[arg_id]).name_end, ((arena).nodes[i]).name_start, ((arena).nodes[i]).name_end) == 1) {
  int32_t ty = ((arena).nodes[i]).a;
  if (ty != AST_NONE && ((arena).nodes[ty]).kind == AST_TYPE) {
  return ty;
}
}
}
  i = (i + 1);
}
}
  return AST_NONE;
}

int32_t flowc_cgen_find_type_by_name(AstArena arena, uint8_t* src, uint8_t* name) {
  int32_t i = 0;
  while (i < (arena).len) {
  if (((arena).nodes[i]).kind == AST_TYPE) {
  if (flowc_cgen_span_is(src, ((arena).nodes[i]).name_start, ((arena).nodes[i]).name_end, name) == 1) {
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

void flowc_cgen_emit_binop_child(CgenBuf* w, AstArena arena, uint8_t* src, int32_t child, int32_t parent_op) {
  int32_t needs_wrap = 0;
  if (parent_op == TOK_AMPAMP) {
  if (((arena).nodes[child]).kind == AST_BINOP && ((arena).nodes[child]).ival == TOK_BARBAR) {
  needs_wrap = 1;
}
}
  if (needs_wrap == 1) {
  flowc_cgen_putc(w, 40);
}
  flowc_cgen_emit_expr(w, arena, src, child);
  if (needs_wrap == 1) {
  flowc_cgen_putc(w, 41);
}
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

void flowc_cgen_scan_captures(CgenBuf* w, AstArena arena, uint8_t* src, int32_t id, int32_t* param_spans, int32_t nparams) {
  if (id == AST_NONE) {
  return;
}
  int32_t kind = ((arena).nodes[id]).kind;
  if (kind == AST_FN) {
  int32_t nparams2 = nparams;
  int32_t param = ((arena).nodes[id]).a;
  while (param != AST_NONE && nparams2 < 16) {
  param_spans[(nparams2 * 2)] = ((arena).nodes[param]).name_start;
  param_spans[((nparams2 * 2) + 1)] = ((arena).nodes[param]).name_end;
  nparams2 = (nparams2 + 1);
  param = ((arena).nodes[param]).next;
}
  flowc_cgen_scan_captures(w, arena, src, ((arena).nodes[id]).c, param_spans, nparams2);
  return;
}
  if (kind == AST_IDENT) {
  int32_t ns = ((arena).nodes[id]).name_start;
  int32_t ne = ((arena).nodes[id]).name_end;
  int32_t is_param = 0;
  int32_t i = 0;
  while (i < (nparams * 2)) {
  if (flowc_cgen_span_eq(src, ns, ne, param_spans[i], param_spans[(i + 1)]) == 1) {
  is_param = 1;
}
  i = (i + 2);
}
  if (is_param == 0) {
  int32_t found = 0;
  int32_t j = 0;
  while (j < (w[0]).cap_count) {
  if (flowc_cgen_span_eq(src, ns, ne, (w[0]).cap_starts[j], (w[0]).cap_ends[j]) == 1) {
  found = 1;
}
  j = (j + 1);
}
  if (found == 0 && (w[0]).cap_count < 64) {
  (w[0]).cap_starts[(w[0]).cap_count] = ns;
  (w[0]).cap_ends[(w[0]).cap_count] = ne;
  (w[0]).cap_count = ((w[0]).cap_count + 1);
}
}
  return;
}
  flowc_cgen_scan_captures(w, arena, src, ((arena).nodes[id]).a, param_spans, nparams);
  flowc_cgen_scan_captures(w, arena, src, ((arena).nodes[id]).b, param_spans, nparams);
  flowc_cgen_scan_captures(w, arena, src, ((arena).nodes[id]).c, param_spans, nparams);
  flowc_cgen_scan_captures(w, arena, src, ((arena).nodes[id]).next, param_spans, nparams);
}

int32_t flowc_cgen_scan_lambda_caps(AstArena arena, uint8_t* src, int32_t id, int32_t* buf, int32_t count, int32_t* param_spans, int32_t nparams) {
  if (id == AST_NONE) {
  return count;
}
  int32_t kind = ((arena).nodes[id]).kind;
  if (kind == AST_FN) {
  int32_t nparams2 = nparams;
  int32_t param = ((arena).nodes[id]).a;
  while (param != AST_NONE && nparams2 < 16) {
  param_spans[(nparams2 * 2)] = ((arena).nodes[param]).name_start;
  param_spans[((nparams2 * 2) + 1)] = ((arena).nodes[param]).name_end;
  nparams2 = (nparams2 + 1);
  param = ((arena).nodes[param]).next;
}
  return flowc_cgen_scan_lambda_caps(arena, src, ((arena).nodes[id]).c, buf, count, param_spans, nparams2);
}
  if (kind == AST_IDENT) {
  int32_t ns = ((arena).nodes[id]).name_start;
  int32_t ne = ((arena).nodes[id]).name_end;
  int32_t is_param = 0;
  int32_t i = 0;
  while (i < (nparams * 2)) {
  if (flowc_cgen_span_eq(src, ns, ne, param_spans[i], param_spans[(i + 1)]) == 1) {
  is_param = 1;
}
  i = (i + 2);
}
  if (is_param == 0) {
  int32_t found = 0;
  int32_t j = 0;
  while (j < count) {
  if (flowc_cgen_span_eq(src, ns, ne, buf[(j * 2)], buf[((j * 2) + 1)]) == 1) {
  found = 1;
}
  j = (j + 1);
}
  if (found == 0 && count < 16) {
  buf[(count * 2)] = ns;
  buf[((count * 2) + 1)] = ne;
  return (count + 1);
}
}
  return count;
}
  count = flowc_cgen_scan_lambda_caps(arena, src, ((arena).nodes[id]).a, buf, count, param_spans, nparams);
  count = flowc_cgen_scan_lambda_caps(arena, src, ((arena).nodes[id]).b, buf, count, param_spans, nparams);
  count = flowc_cgen_scan_lambda_caps(arena, src, ((arena).nodes[id]).c, buf, count, param_spans, nparams);
  return flowc_cgen_scan_lambda_caps(arena, src, ((arena).nodes[id]).next, buf, count, param_spans, nparams);
}

int32_t flowc_cgen_is_captured(CgenBuf* w, uint8_t* src, int32_t ns, int32_t ne) {
  int32_t i = 0;
  while (i < (w[0]).cap_count) {
  if (flowc_cgen_span_eq(src, ns, ne, (w[0]).cap_starts[i], (w[0]).cap_ends[i]) == 1) {
  return 1;
}
  i = (i + 1);
}
  return 0;
}

int32_t flowc_cgen_is_span_var(AstArena arena, uint8_t* src, int32_t id) {
  int32_t ns = ((arena).nodes[id]).name_start;
  int32_t ne = ((arena).nodes[id]).name_end;
  int32_t i = 0;
  while (i < (arena).len) {
  if (((arena).nodes[i]).kind == AST_PARAM || ((arena).nodes[i]).kind == AST_LET) {
  if (flowc_cgen_span_eq(src, ns, ne, ((arena).nodes[i]).name_start, ((arena).nodes[i]).name_end) == 1) {
  int32_t ty = ((arena).nodes[i]).a;
  if (((arena).nodes[i]).kind == AST_PARAM && ((arena).nodes[i]).a == AST_NONE) {
  ty = ((arena).nodes[i]).b;
}
  if (ty != AST_NONE) {
  int32_t tns = ((arena).nodes[ty]).name_start;
  int32_t tne = ((arena).nodes[ty]).name_end;
  if (flowc_cgen_span_is(src, tns, tne, "span") == 1) {
  return 1;
}
  int32_t inner = ((arena).nodes[ty]).a;
  if (inner != AST_NONE && tns == 0 && tne == 0) {
  return 1;
}
}
}
}
  i = (i + 1);
}
  return 0;
}

int32_t flowc_cgen_var_elem_type(AstArena arena, uint8_t* src, int32_t id) {
  int32_t ns = ((arena).nodes[id]).name_start;
  int32_t ne = ((arena).nodes[id]).name_end;
  int32_t i = 0;
  while (i < (arena).len) {
  if (((arena).nodes[i]).kind == AST_PARAM || ((arena).nodes[i]).kind == AST_LET) {
  if (flowc_cgen_span_eq(src, ns, ne, ((arena).nodes[i]).name_start, ((arena).nodes[i]).name_end) == 1) {
  int32_t ty = ((arena).nodes[i]).a;
  if (((arena).nodes[i]).kind == AST_PARAM && ((arena).nodes[i]).a == AST_NONE) {
  ty = ((arena).nodes[i]).b;
}
  if (ty != AST_NONE) {
  int32_t tns = ((arena).nodes[ty]).name_start;
  int32_t tne = ((arena).nodes[ty]).name_end;
  int32_t inner = ((arena).nodes[ty]).a;
  if (inner != AST_NONE) {
  if (flowc_cgen_span_is(src, tns, tne, "ptr") == 1) {
  return inner;
}
  if (flowc_cgen_span_is(src, tns, tne, "span") == 1) {
  return inner;
}
  if (flowc_cgen_span_is(src, tns, tne, "array") == 1) {
  return inner;
}
  if (tns == 0 && tne == 0) {
  return inner;
}
}
}
}
}
  i = (i + 1);
}
  return AST_NONE;
}

int32_t flowc_cgen_fn_param_is_span(AstArena arena, uint8_t* src, int32_t fn_id, int32_t param_idx) {
  if (fn_id == AST_NONE) {
  return 0;
}
  int32_t param = ((arena).nodes[fn_id]).a;
  int32_t idx = 0;
  while (param != AST_NONE) {
  if (idx == param_idx) {
  int32_t ty = ((arena).nodes[param]).a;
  if (ty != AST_NONE) {
  int32_t tns = ((arena).nodes[ty]).name_start;
  int32_t tne = ((arena).nodes[ty]).name_end;
  if (flowc_cgen_span_is(src, tns, tne, "span") == 1) {
  return 1;
}
  int32_t inner = ((arena).nodes[ty]).a;
  if (inner != AST_NONE && tns == 0 && tne == 0) {
  return 1;
}
}
  return 0;
}
  idx = (idx + 1);
  param = ((arena).nodes[param]).next;
}
  return 0;
}

int32_t flowc_cgen_is_array_var(AstArena arena, uint8_t* src, int32_t id) {
  int32_t ns = ((arena).nodes[id]).name_start;
  int32_t ne = ((arena).nodes[id]).name_end;
  int32_t i = 0;
  while (i < (arena).len) {
  if (((arena).nodes[i]).kind == AST_LET) {
  if (flowc_cgen_span_eq(src, ns, ne, ((arena).nodes[i]).name_start, ((arena).nodes[i]).name_end) == 1) {
  int32_t ty = ((arena).nodes[i]).a;
  if (ty != AST_NONE) {
  if (((arena).nodes[ty]).ival > 0) {
  return 1;
}
}
}
}
  i = (i + 1);
}
  return 0;
}

int32_t flowc_cgen_array_var_size(AstArena arena, uint8_t* src, int32_t id) {
  int32_t ns = ((arena).nodes[id]).name_start;
  int32_t ne = ((arena).nodes[id]).name_end;
  int32_t i = 0;
  while (i < (arena).len) {
  if (((arena).nodes[i]).kind == AST_LET) {
  if (flowc_cgen_span_eq(src, ns, ne, ((arena).nodes[i]).name_start, ((arena).nodes[i]).name_end) == 1) {
  int32_t ty = ((arena).nodes[i]).a;
  if (ty != AST_NONE) {
  if (((arena).nodes[ty]).ival > 0) {
  return ((arena).nodes[ty]).ival;
}
}
}
}
  i = (i + 1);
}
  return 0;
}

int32_t flowc_cgen_find_enum_variant(AstArena arena, uint8_t* src, int32_t ns, int32_t ne) {
  int32_t i = 0;
  while (i < (arena).len) {
  if (((arena).nodes[i]).kind == AST_ENUM) {
  int32_t var = ((arena).nodes[i]).a;
  while (var != AST_NONE) {
  if (flowc_cgen_span_eq(src, ns, ne, ((arena).nodes[var]).name_start, ((arena).nodes[var]).name_end) == 1) {
  return i;
}
  var = ((arena).nodes[var]).next;
}
}
  i = (i + 1);
}
  return AST_NONE;
}

void flowc_cgen_emit_expr(CgenBuf* w, AstArena arena, uint8_t* src, int32_t id) {
  if (id == AST_NONE || (w[0]).err != 0) {
  return;
}
  int32_t kind = ((arena).nodes[id]).kind;
  if (kind == AST_INT) {
  flowc_cgen_emit_int_literal(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
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
  if ((w[0]).in_lambda != 0) {
  if (flowc_cgen_is_captured(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end) == 1) {
  flowc_cgen_puts(w, "__flowc_cap_");
  flowc_cgen_put_span(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  return;
}
}
  int32_t en_id = flowc_cgen_find_enum_variant(arena, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  if (en_id != AST_NONE) {
  flowc_cgen_put_span(w, src, ((arena).nodes[en_id]).name_start, ((arena).nodes[en_id]).name_end);
  flowc_cgen_putc(w, 95);
  flowc_cgen_put_span(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  return;
}
  if (flowc_cgen_span_is(src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end, "general") == 1) {
  flowc_cgen_puts(w, "0");
  return;
}
  if (flowc_cgen_span_is(src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end, "adaptive") == 1) {
  flowc_cgen_puts(w, "0");
  return;
}
  if (flowc_cgen_span_is(src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end, "descending") == 1) {
  flowc_cgen_puts(w, "0");
  return;
}
  if (flowc_cgen_span_is(src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end, "ascending") == 1) {
  flowc_cgen_puts(w, "0");
  return;
}
  if (flowc_cgen_span_is(src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end, "unique") == 1) {
  flowc_cgen_puts(w, "0");
  return;
}
  if (flowc_cgen_span_is(src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end, "asc") == 1) {
  flowc_cgen_puts(w, "0");
  return;
}
  if (flowc_cgen_span_is(src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end, "desc") == 1) {
  flowc_cgen_puts(w, "0");
  return;
}
  flowc_cgen_put_ident(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  return;
}
  if (kind == AST_FN) {
  int32_t lam_id = (0 - ((arena).nodes[id]).name_start);
  int32_t ci = 0;
  int32_t has_snap = 0;
  while (ci < (w[0]).lambda_cap_count) {
  if ((w[0]).lambda_cap_lambda[ci] == lam_id) {
  if (has_snap == 0) {
  flowc_cgen_putc(w, 40);
  has_snap = 1;
} else {
  flowc_cgen_puts(w, ", ");
}
  flowc_cgen_puts(w, "__flowc_cap_");
  flowc_cgen_put_span(w, src, (w[0]).lambda_cap_start[ci], (w[0]).lambda_cap_end[ci]);
  flowc_cgen_puts(w, " = ");
  if ((w[0]).in_lambda != 0) {
  flowc_cgen_puts(w, "__flowc_cap_");
}
  flowc_cgen_put_span(w, src, (w[0]).lambda_cap_start[ci], (w[0]).lambda_cap_end[ci]);
}
  ci = (ci + 1);
}
  if (has_snap == 1) {
  flowc_cgen_puts(w, ", ");
}
  flowc_cgen_puts(w, "__flowc_lambda_");
  flowc_cgen_put_i32(w, lam_id);
  if (has_snap == 1) {
  flowc_cgen_putc(w, 41);
}
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
  if (op == TOK_IN) {
  if (flowc_cgen_expr_is_string(w, arena, src, ((arena).nodes[id]).b) == 1) {
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_cgen_puts(w, " != NULL && strchr(");
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).b);
  flowc_cgen_puts(w, ", (int)(");
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_cgen_puts(w, ")[0]) != NULL");
} else {
  flowc_cgen_puts(w, "__flow_in_arr(");
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).b);
  flowc_cgen_puts(w, ", ");
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_cgen_putc(w, 41);
}
  return;
}
  int32_t wrap = flowc_cgen_binop_needs_parens(op);
  if (wrap == 1) {
  flowc_cgen_putc(w, 40);
}
  flowc_cgen_emit_binop_child(w, arena, src, ((arena).nodes[id]).a, op);
  flowc_cgen_emit_binop_op(w, op);
  flowc_cgen_emit_binop_child(w, arena, src, ((arena).nodes[id]).b, op);
  if (wrap == 1) {
  flowc_cgen_putc(w, 41);
}
  return;
}
  if (kind == AST_UNARY) {
  if (((arena).nodes[id]).ival == KW_DBG) {
  flowc_cgen_puts(w, "__flow_dbg(");
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_cgen_putc(w, 41);
  return;
}
  if (((arena).nodes[id]).ival == KW_EXPECT) {
  flowc_cgen_puts(w, "do { if (!(");
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_cgen_puts(w, ")) { fprintf(stderr, \"expectation failed\\n\"); abort(); } } while(0)");
  return;
}
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
  if (kind == AST_IF_EXPR) {
  flowc_cgen_puts(w, "((");
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_cgen_puts(w, ") ? (");
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).b);
  flowc_cgen_puts(w, ") : (");
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).c);
  flowc_cgen_puts(w, "))");
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
  if (((arena).nodes[id]).ival == 1) {
  int32_t elem = AST_NONE;
  if (((arena).nodes[((arena).nodes[id]).a]).kind == AST_IDENT) {
  elem = flowc_cgen_var_elem_type(arena, src, ((arena).nodes[id]).a);
}
  flowc_cgen_puts(w, "((flowc_span_");
  if (elem != AST_NONE) {
  flowc_cgen_emit_type(w, arena, src, elem);
} else {
  flowc_cgen_puts(w, "int32_t");
}
  flowc_cgen_puts(w, "){ (");
  if (elem != AST_NONE) {
  flowc_cgen_emit_type(w, arena, src, elem);
} else {
  flowc_cgen_puts(w, "int32_t");
}
  flowc_cgen_puts(w, "*)");
  if (((arena).nodes[((arena).nodes[id]).a]).kind == AST_IDENT) {
  if (flowc_cgen_is_span_var(arena, src, ((arena).nodes[id]).a) == 1) {
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_cgen_puts(w, ".data");
} else {
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).a);
}
} else {
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).a);
}
  flowc_cgen_puts(w, " + ");
  if (((arena).nodes[id]).b != AST_NONE) {
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).b);
} else {
  flowc_cgen_puts(w, "0");
}
  flowc_cgen_puts(w, ", ");
  if (((arena).nodes[id]).c != AST_NONE) {
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).c);
  flowc_cgen_puts(w, " - ");
  if (((arena).nodes[id]).b != AST_NONE) {
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).b);
} else {
  flowc_cgen_puts(w, "0");
}
} else {
  if (((arena).nodes[((arena).nodes[id]).a]).kind == AST_IDENT) {
  if (flowc_cgen_is_span_var(arena, src, ((arena).nodes[id]).a) == 1) {
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_cgen_puts(w, ".len - ");
} else {
  flowc_cgen_puts(w, "(int32_t)(sizeof(");
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_cgen_puts(w, ")/sizeof((");
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_cgen_puts(w, ")[0])) - ");
}
} else {
  flowc_cgen_puts(w, "(int32_t)(sizeof(");
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_cgen_puts(w, ")/sizeof((");
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_cgen_puts(w, ")[0])) - ");
}
  if (((arena).nodes[id]).b != AST_NONE) {
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).b);
} else {
  flowc_cgen_puts(w, "0");
}
}
  flowc_cgen_puts(w, "})");
  return;
}
  if (((arena).nodes[((arena).nodes[id]).a]).kind == AST_IDENT) {
  if (flowc_cgen_is_span_var(arena, src, ((arena).nodes[id]).a) == 1) {
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_cgen_puts(w, ".data[");
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).b);
  flowc_cgen_putc(w, 93);
  return;
}
}
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
  if (flowc_cgen_span_is(src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end, "len") == 1) {
  flowc_cgen_putc(w, 40);
  int32_t arg = ((arena).nodes[id]).a;
  if (arg != AST_NONE) {
  flowc_cgen_emit_expr(w, arena, src, arg);
}
  flowc_cgen_puts(w, ").len");
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
  if (flowc_cgen_span_is(src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end, "sort") == 1) {
  int32_t desc_flag = 0;
  int32_t arg = ((arena).nodes[id]).a;
  while (arg != AST_NONE) {
  if (((arena).nodes[arg]).kind == AST_IDENT) {
  if (flowc_cgen_span_is(src, ((arena).nodes[arg]).name_start, ((arena).nodes[arg]).name_end, "descending") == 1) {
  desc_flag = 1;
}
}
  arg = ((arena).nodes[arg]).next;
}
  flowc_cgen_puts(w, "(flowc_sort_dispatch((void*)");
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_cgen_puts(w, ", (int32_t)(sizeof(");
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_cgen_puts(w, ")/sizeof((");
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_cgen_puts(w, ")[0])), (int32_t)sizeof((");
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_cgen_puts(w, ")[0]), ");
  flowc_cgen_put_i32(w, desc_flag);
  flowc_cgen_puts(w, "), 0)");
  return;
}
  if (flowc_cgen_span_is(src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end, "sortBy") == 1) {
  int32_t desc_flag = ((arena).nodes[id]).ival;
  int32_t arg = ((arena).nodes[id]).a;
  while (arg != AST_NONE) {
  if (((arena).nodes[arg]).kind == AST_IDENT) {
  if (flowc_cgen_span_is(src, ((arena).nodes[arg]).name_start, ((arena).nodes[arg]).name_end, "descending") == 1) {
  desc_flag = 1;
}
}
  arg = ((arena).nodes[arg]).next;
}
  flowc_cgen_puts(w, "(flowc_sort_struct((void*)");
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_cgen_puts(w, ", (int32_t)(sizeof(");
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_cgen_puts(w, ")/sizeof((");
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_cgen_puts(w, ")[0])), (int32_t)sizeof((");
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_cgen_puts(w, ")[0]), ");
  flowc_cgen_put_i32(w, desc_flag);
  flowc_cgen_puts(w, "), 0)");
  return;
}
  if (flowc_cgen_span_is(src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end, "find") == 1) {
  flowc_cgen_puts(w, "flowc_find_i32(");
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_cgen_puts(w, ", (int32_t)(sizeof(");
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_cgen_puts(w, ")/sizeof(int32_t))");
  if (n_args >= 2) {
  flowc_cgen_puts(w, ", ");
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[((arena).nodes[id]).a]).next);
}
  flowc_cgen_puts(w, ")");
  return;
}
  if (((arena).nodes[id]).b != AST_NONE) {
  flowc_cgen_put_ident(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  int32_t ta = ((arena).nodes[id]).b;
  while (ta != AST_NONE) {
  flowc_cgen_putc(w, 95);
  flowc_cgen_put_span(w, src, ((arena).nodes[ta]).name_start, ((arena).nodes[ta]).name_end);
  ta = ((arena).nodes[ta]).next;
}
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
  flowc_cgen_puts(w, ")");
  return;
}
  int32_t n_overloads = flowc_cgen_count_overloads(arena, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  int32_t fn_id = 0;
  if (n_overloads > 1) {
  fn_id = flowc_cgen_resolve_overload(arena, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end, id);
  if (fn_id != AST_NONE) {
  flowc_cgen_put_mangled_fn(w, arena, src, fn_id);
} else {
  flowc_cgen_put_ident(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
}
} else {
  flowc_cgen_put_ident(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  fn_id = flowc_cgen_find_fn(arena, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
}
  flowc_cgen_putc(w, 40);
  int32_t arg = ((arena).nodes[id]).a;
  int32_t first = 1;
  int32_t param_idx = 0;
  while (arg != AST_NONE) {
  if (first == 0) {
  flowc_cgen_puts(w, ", ");
}
  first = 0;
  if (fn_id != AST_NONE && flowc_cgen_fn_param_is_span(arena, src, fn_id, param_idx) == 1) {
  if (((arena).nodes[arg]).kind == AST_IDENT && flowc_cgen_is_array_var(arena, src, arg) == 1) {
  int32_t arr_size = flowc_cgen_array_var_size(arena, src, arg);
  flowc_cgen_puts(w, "((flowc_span_int32_t){ ");
  flowc_cgen_emit_expr(w, arena, src, arg);
  flowc_cgen_puts(w, ", ");
  flowc_cgen_put_i32(w, arr_size);
  flowc_cgen_puts(w, " })");
  arg = ((arena).nodes[arg]).next;
  param_idx = (param_idx + 1);
  continue;
}
}
  flowc_cgen_emit_expr(w, arena, src, arg);
  arg = ((arena).nodes[arg]).next;
  param_idx = (param_idx + 1);
}
  flowc_cgen_putc(w, 41);
  return;
}
  if (kind == AST_FIELD_ACCESS) {
  int32_t base = ((arena).nodes[id]).a;
  int32_t is_ptr = 0;
  if (base != AST_NONE && ((arena).nodes[base]).kind == AST_IDENT && (w[0]).cur_fn != AST_NONE) {
  int32_t param = ((arena).nodes[(w[0]).cur_fn]).a;
  while (param != AST_NONE) {
  if (((arena).nodes[param]).kind == AST_PARAM) {
  if (flowc_cgen_span_eq(src, ((arena).nodes[base]).name_start, ((arena).nodes[base]).name_end, ((arena).nodes[param]).name_start, ((arena).nodes[param]).name_end) == 1) {
  int32_t ty = ((arena).nodes[param]).a;
  if (ty != AST_NONE && ((arena).nodes[ty]).kind == AST_TYPE) {
  if (flowc_cgen_span_is(src, ((arena).nodes[ty]).name_start, ((arena).nodes[ty]).name_end, "ptr") == 1) {
  is_ptr = 1;
}
}
}
}
  param = ((arena).nodes[param]).next;
}
}
  if (is_ptr == 1) {
  flowc_cgen_emit_expr(w, arena, src, base);
  flowc_cgen_puts(w, "->");
  flowc_cgen_put_span(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
} else {
  flowc_cgen_putc(w, 40);
  flowc_cgen_emit_expr(w, arena, src, base);
  flowc_cgen_putc(w, 41);
  flowc_cgen_putc(w, 46);
  flowc_cgen_put_span(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
}
  return;
}
  if (kind == AST_STRUCT_LIT) {
  flowc_cgen_putc(w, 40);
  flowc_cgen_put_span(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  int32_t ta = ((arena).nodes[id]).b;
  while (ta != AST_NONE) {
  if (((arena).nodes[ta]).kind == AST_TYPE) {
  flowc_cgen_putc(w, 95);
  if ((w[0]).mono_ntp > 0) {
  int32_t idx = flowc_cgen_find_tp(src, ((arena).nodes[ta]).name_start, ((arena).nodes[ta]).name_end, (w[0]).mono_tp_starts, (w[0]).mono_tp_ends, (w[0]).mono_ntp);
  if (idx >= 0) {
  flowc_cgen_put_span(w, src, ((arena).nodes[(w[0]).mono_tp_concrete[idx]]).name_start, ((arena).nodes[(w[0]).mono_tp_concrete[idx]]).name_end);
} else {
  flowc_cgen_put_span(w, src, ((arena).nodes[ta]).name_start, ((arena).nodes[ta]).name_end);
}
} else {
  flowc_cgen_put_span(w, src, ((arena).nodes[ta]).name_start, ((arena).nodes[ta]).name_end);
}
}
  ta = ((arena).nodes[ta]).next;
}
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
  int32_t defers[64] = { 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
  int32_t n_defers = 0;
  int32_t st = ((arena).nodes[id]).a;
  while (st != AST_NONE) {
  if (((arena).nodes[st]).kind == AST_DEFER) {
  if (n_defers < 64) {
  defers[n_defers] = st;
  n_defers = (n_defers + 1);
}
} else {
  if (((arena).nodes[st]).kind == AST_RETURN) {
  int32_t d = (n_defers - 1);
  while (d >= 0) {
  flowc_cgen_puts(w, "  ");
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[defers[d]]).a);
  flowc_cgen_puts(w, ";\n");
  d = (d - 1);
}
}
  flowc_cgen_emit_stmt(w, arena, src, st);
}
  st = ((arena).nodes[st]).next;
}
  int32_t i = (n_defers - 1);
  while (i >= 0) {
  flowc_cgen_puts(w, "  ");
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[defers[i]]).a);
  flowc_cgen_puts(w, ";\n");
  i = (i - 1);
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
  int32_t is_captured = flowc_cgen_is_captured(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  if (is_captured == 1) {
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
  if (arr_n > 0) {
  flowc_cgen_emit_type(w, arena, src, arr_inner);
} else {
  int32_t wrote = 0;
  if (ty == AST_NONE) {
  wrote = flowc_cgen_write_lit_type(w, arena, src, init);
}
  if (wrote == 0) {
  if (ty == AST_NONE && init != AST_NONE && ((arena).nodes[init]).kind == AST_FN) {
  int32_t lam_ret = ((arena).nodes[init]).b;
  if (lam_ret == AST_NONE) {
  flowc_cgen_puts(w, "void");
} else {
  flowc_cgen_emit_type(w, arena, src, lam_ret);
}
  flowc_cgen_puts(w, " (*");
  flowc_cgen_put_ident(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  flowc_cgen_puts(w, ")(");
  int32_t lam_param = ((arena).nodes[init]).a;
  int32_t lam_first = 1;
  while (lam_param != AST_NONE) {
  if (lam_first == 0) {
  flowc_cgen_puts(w, ", ");
}
  flowc_cgen_emit_type(w, arena, src, ((arena).nodes[lam_param]).b);
  lam_first = 0;
  lam_param = ((arena).nodes[lam_param]).next;
}
  flowc_cgen_putc(w, 41);
  flowc_cgen_puts(w, " = ");
  flowc_cgen_emit_expr(w, arena, src, init);
  flowc_cgen_puts(w, ";\n");
  return;
}
  if (ty != AST_NONE && ((arena).nodes[ty]).kind == AST_TYPE && (((arena).nodes[ty]).ival == (-1) || ((arena).nodes[ty]).ival == (-2))) {
  flowc_cgen_emit_type(w, arena, src, ((arena).nodes[ty]).b);
  flowc_cgen_puts(w, " (*");
  flowc_cgen_put_ident(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  flowc_cgen_puts(w, ")(");
  int32_t cfn_param = ((arena).nodes[ty]).a;
  int32_t cfn_first = 1;
  while (cfn_param != AST_NONE) {
  if (cfn_first == 0) {
  flowc_cgen_puts(w, ", ");
}
  flowc_cgen_emit_type(w, arena, src, cfn_param);
  cfn_first = 0;
  cfn_param = ((arena).nodes[cfn_param]).next;
}
  flowc_cgen_putc(w, 41);
  flowc_cgen_puts(w, " = ");
  flowc_cgen_emit_expr(w, arena, src, init);
  flowc_cgen_puts(w, ";\n");
  return;
}
  flowc_cgen_emit_type(w, arena, src, ty);
}
}
  flowc_cgen_putc(w, 32);
  flowc_cgen_put_ident(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
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
  const char* cmp = " < ";
  if (((arena).nodes[id]).ival != AST_NONE && ((arena).nodes[id]).ival != 0) {
  int32_t step_id = ((arena).nodes[id]).ival;
  if (((arena).nodes[step_id]).kind == AST_UNARY && ((arena).nodes[step_id]).ival == TOK_MINUS) {
  cmp = " >= ";
}
}
  flowc_cgen_puts(w, "  for (int32_t ");
  flowc_cgen_put_span(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  flowc_cgen_puts(w, " = ");
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_cgen_puts(w, "; ");
  flowc_cgen_put_span(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  flowc_cgen_puts(w, cmp);
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).b);
  flowc_cgen_puts(w, "; ");
  flowc_cgen_put_span(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  flowc_cgen_puts(w, " = ");
  flowc_cgen_put_span(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  flowc_cgen_puts(w, " + ");
  if (((arena).nodes[id]).ival != AST_NONE && ((arena).nodes[id]).ival != 0) {
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).ival);
} else {
  flowc_cgen_puts(w, "1");
}
  flowc_cgen_puts(w, ") ");
  flowc_cgen_emit_block(w, arena, src, ((arena).nodes[id]).c);
  return;
}
  if (kind == AST_MATCH) {
  int32_t match_expr = ((arena).nodes[id]).a;
  int32_t arm0 = ((arena).nodes[id]).b;
  int32_t first_kind = 0;
  if (arm0 != AST_NONE) {
  first_kind = ((arena).nodes[arm0]).ival;
}
  if (first_kind == 4) {
  flowc_cgen_puts(w, "  { const char* __flowc_match = ");
  flowc_cgen_emit_expr(w, arena, src, match_expr);
  flowc_cgen_puts(w, ";\n");
  int32_t arm = arm0;
  int32_t n_lit = 0;
  int32_t chain_open = 0;
  while (arm != AST_NONE) {
  if (((arena).nodes[arm]).ival == 0 || ((arena).nodes[arm]).ival == 4) {
  if (n_lit == 0) {
  flowc_cgen_puts(w, "  if (strcmp(__flowc_match, ");
} else {
  flowc_cgen_puts(w, "} else if (strcmp(__flowc_match, ");
}
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[arm]).a);
  flowc_cgen_puts(w, ") == 0) {\n");
  n_lit = (n_lit + 1);
  chain_open = 1;
} else {
  if (n_lit > 0) {
  flowc_cgen_puts(w, "} else {\n");
}
  if (((arena).nodes[arm]).ival == 2) {
  flowc_cgen_puts(w, "  const char* ");
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
  if (first_kind == 3) {
  flowc_cgen_puts(w, "  { double __flowc_match = ");
  flowc_cgen_emit_expr(w, arena, src, match_expr);
  flowc_cgen_puts(w, ";\n");
  int32_t arm = arm0;
  int32_t n_lit = 0;
  int32_t chain_open = 0;
  while (arm != AST_NONE) {
  if (((arena).nodes[arm]).ival == 0 || ((arena).nodes[arm]).ival == 3) {
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
  flowc_cgen_puts(w, "  double ");
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
  if (first_kind == 5) {
  int32_t sname_s = ((arena).nodes[arm0]).name_start;
  int32_t sname_e = ((arena).nodes[arm0]).name_end;
  flowc_cgen_puts(w, "  { ");
  flowc_cgen_put_span(w, src, sname_s, sname_e);
  flowc_cgen_puts(w, " __flowc_match = ");
  flowc_cgen_emit_expr(w, arena, src, match_expr);
  flowc_cgen_puts(w, ";\n");
  int32_t arm = arm0;
  int32_t chain_open = 0;
  while (arm != AST_NONE) {
  if (((arena).nodes[arm]).ival == 5) {
  if (chain_open == 1) {
  flowc_cgen_puts(w, "} else {\n");
}
  int32_t struct_def = AST_NONE;
  int32_t si = 0;
  while (si < (arena).len) {
  if (((arena).nodes[si]).kind == AST_STRUCT) {
  if (flowc_cgen_span_eq(src, ((arena).nodes[si]).name_start, ((arena).nodes[si]).name_end, sname_s, sname_e) == 1) {
  struct_def = si;
  break;
}
}
  si = (si + 1);
}
  int32_t bind = ((arena).nodes[arm]).a;
  int32_t field = AST_NONE;
  if (struct_def != AST_NONE) {
  field = ((arena).nodes[struct_def]).a;
}
  while (bind != AST_NONE) {
  flowc_cgen_puts(w, "  int32_t ");
  flowc_cgen_put_span(w, src, ((arena).nodes[bind]).name_start, ((arena).nodes[bind]).name_end);
  flowc_cgen_puts(w, " = __flowc_match.");
  if (field != AST_NONE) {
  flowc_cgen_put_span(w, src, ((arena).nodes[field]).name_start, ((arena).nodes[field]).name_end);
  field = ((arena).nodes[field]).next;
}
  flowc_cgen_puts(w, ";\n");
  bind = ((arena).nodes[bind]).next;
}
  chain_open = 0;
} else {
  if (chain_open == 1) {
  flowc_cgen_puts(w, "} else {\n");
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
  flowc_cgen_puts(w, "  }\n");
  return;
}
  if (first_kind == 6) {
  flowc_cgen_puts(w, "  { int32_t* __flowc_match = ");
  flowc_cgen_emit_expr(w, arena, src, match_expr);
  flowc_cgen_puts(w, ";\n");
  int32_t arm = arm0;
  int32_t n_lit = 0;
  int32_t chain_open = 0;
  while (arm != AST_NONE) {
  if (((arena).nodes[arm]).ival == 6) {
  if (n_lit == 0) {
  flowc_cgen_puts(w, "  if (");
} else {
  flowc_cgen_puts(w, "} else if (");
}
  int32_t elem = ((arena).nodes[arm]).a;
  int32_t idx = 0;
  int32_t first_cond = 1;
  while (elem != AST_NONE) {
  if (((arena).nodes[elem]).kind == AST_INT) {
  if (first_cond == 0) {
  flowc_cgen_puts(w, " && ");
}
  flowc_cgen_puts(w, "__flowc_match[");
  flowc_cgen_put_i32(w, idx);
  flowc_cgen_puts(w, "] == ");
  flowc_cgen_put_i32(w, ((arena).nodes[elem]).ival);
  first_cond = 0;
}
  idx = (idx + 1);
  elem = ((arena).nodes[elem]).next;
}
  if (first_cond == 1) {
  flowc_cgen_puts(w, "1");
}
  flowc_cgen_puts(w, ") {\n");
  elem = ((arena).nodes[arm]).a;
  idx = 0;
  while (elem != AST_NONE) {
  if (((arena).nodes[elem]).kind == AST_IDENT) {
  flowc_cgen_puts(w, "  int32_t ");
  flowc_cgen_put_span(w, src, ((arena).nodes[elem]).name_start, ((arena).nodes[elem]).name_end);
  flowc_cgen_puts(w, " = __flowc_match[");
  flowc_cgen_put_i32(w, idx);
  flowc_cgen_puts(w, "];\n");
}
  idx = (idx + 1);
  elem = ((arena).nodes[elem]).next;
}
  n_lit = (n_lit + 1);
  chain_open = 1;
} else {
  if (n_lit > 0) {
  flowc_cgen_puts(w, "} else {\n");
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
  flowc_cgen_puts(w, "  { int32_t __flowc_match = ");
  flowc_cgen_emit_expr(w, arena, src, match_expr);
  flowc_cgen_puts(w, ";\n");
  int32_t arm = arm0;
  int32_t n_lit = 0;
  int32_t chain_open = 0;
  while (arm != AST_NONE) {
  if (((arena).nodes[arm]).ival == 0) {
  if (n_lit == 0) {
  flowc_cgen_puts(w, "  if (__flowc_match == ");
} else {
  flowc_cgen_puts(w, "} else if (__flowc_match == ");
}
  if (((arena).nodes[((arena).nodes[arm]).a]).kind == AST_INT) {
  flowc_cgen_put_i32(w, ((arena).nodes[((arena).nodes[arm]).a]).ival);
} else {
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[arm]).a);
}
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
  if (kind == AST_DEFER) {
  flowc_cgen_puts(w, "  ");
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_cgen_puts(w, ";\n");
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
  if (flowc_cgen_span_is(src, ns, ne, "popen") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "pclose") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "fscanf") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "sscanf") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "scanf") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "pthread_create") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "pthread_join") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "pthread_exit") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "pthread_mutex_init") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "pthread_mutex_destroy") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "pthread_mutex_lock") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "pthread_mutex_unlock") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "pthread_cond_init") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "pthread_cond_destroy") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "pthread_cond_wait") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "pthread_cond_signal") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "pthread_cond_broadcast") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "pthread_self") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "stat") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "fstat") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "lstat") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "mkdir") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "flowc_io_fopen") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "flowc_io_fclose") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "flowc_io_fread") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "flowc_io_fwrite") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "flowc_io_fseek") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "flowc_io_ftell") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "flowc_read_file") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "flowc_write_file") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "flowc_io_remove") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "flowc_io_mkdir") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "flowc_io_exists") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "flowc_io_file_size") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "flowc_io_popen_read") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "flowc_io_system") == 1) {
  return 1;
}
  return 0;
}

void flowc_cgen_emit_fn(CgenBuf* w, AstArena arena, uint8_t* src, int32_t id) {
  int32_t cli_main = flowc_cgen_is_cli_main(arena, src, id);
  (w[0]).cur_fn = id;
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
  if (((arena).nodes[ret_ty]).kind == AST_TYPE && (((arena).nodes[ret_ty]).ival == (-1) || ((arena).nodes[ret_ty]).ival == (-2))) {
  flowc_cgen_puts(w, "void*");
} else {
  flowc_cgen_emit_type(w, arena, src, ret_ty);
}
}
  flowc_cgen_putc(w, 32);
  if ((w[0]).mono_ntp > 0 && cli_main == 0) {
  flowc_cgen_put_ident(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  int32_t mi = 0;
  while (mi < (w[0]).mono_ntp) {
  flowc_cgen_putc(w, 95);
  flowc_cgen_put_span(w, src, ((arena).nodes[(w[0]).mono_tp_concrete[mi]]).name_start, ((arena).nodes[(w[0]).mono_tp_concrete[mi]]).name_end);
  mi = (mi + 1);
}
} else {
  if (flowc_cgen_count_overloads(arena, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end) > 1 && cli_main == 0) {
  flowc_cgen_put_mangled_fn(w, arena, src, id);
} else {
  flowc_cgen_put_ident(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
}
}
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
  if (((arena).nodes[ret_ty]).kind == AST_TYPE && (((arena).nodes[ret_ty]).ival == (-1) || ((arena).nodes[ret_ty]).ival == (-2))) {
  flowc_cgen_puts(w, "void*");
} else {
  flowc_cgen_emit_type(w, arena, src, ret_ty);
}
}
  flowc_cgen_putc(w, 32);
  if ((w[0]).mono_ntp > 0 && cli_main == 0) {
  flowc_cgen_put_ident(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  int32_t mi = 0;
  while (mi < (w[0]).mono_ntp) {
  flowc_cgen_putc(w, 95);
  flowc_cgen_put_span(w, src, ((arena).nodes[(w[0]).mono_tp_concrete[mi]]).name_start, ((arena).nodes[(w[0]).mono_tp_concrete[mi]]).name_end);
  mi = (mi + 1);
}
} else {
  if (flowc_cgen_count_overloads(arena, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end) > 1 && cli_main == 0) {
  flowc_cgen_put_mangled_fn(w, arena, src, id);
} else {
  flowc_cgen_put_ident(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
}
}
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
  flowc_cgen_puts(w, "const ");
} else {
  flowc_cgen_puts(w, "static const ");
}
  int32_t ty = ((arena).nodes[id]).a;
  if (ty != AST_NONE) {
  flowc_cgen_emit_type(w, arena, src, ty);
} else {
  flowc_cgen_puts(w, "int32_t");
}
  flowc_cgen_putc(w, 32);
  flowc_cgen_put_ident(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  flowc_cgen_puts(w, " = ");
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).b);
  flowc_cgen_puts(w, ";\n");
}

int32_t flowc_cgen_find_tp(uint8_t* src, int32_t ns, int32_t ne, int32_t* tp_starts, int32_t* tp_ends, int32_t ntp) {
  int32_t i = 0;
  while (i < ntp) {
  if (flowc_cgen_span_eq(src, ns, ne, tp_starts[i], tp_ends[i]) == 1) {
  return i;
}
  i = (i + 1);
}
  return (0 - 1);
}

void flowc_cgen_emit_type_subst(CgenBuf* w, AstArena arena, uint8_t* src, int32_t ty, int32_t* tp_starts, int32_t* tp_ends, int32_t* tp_concrete, int32_t ntp) {
  if (ty == AST_NONE || ((arena).nodes[ty]).kind != AST_TYPE) {
  flowc_cgen_puts(w, "int32_t");
  return;
}
  if (((arena).nodes[ty]).ival == (0 - 1) || ((arena).nodes[ty]).ival == (0 - 2)) {
  flowc_cgen_emit_type(w, arena, src, ty);
  return;
}
  int32_t ns = ((arena).nodes[ty]).name_start;
  int32_t ne = ((arena).nodes[ty]).name_end;
  int32_t inner = ((arena).nodes[ty]).a;
  if (inner == AST_NONE) {
  int32_t idx = flowc_cgen_find_tp(src, ns, ne, tp_starts, tp_ends, ntp);
  if (idx >= 0) {
  flowc_cgen_emit_type(w, arena, src, tp_concrete[idx]);
  return;
}
}
  if (inner != AST_NONE && flowc_cgen_span_is(src, ns, ne, "ptr") == 1) {
  int32_t inner_idx = flowc_cgen_find_tp(src, ((arena).nodes[inner]).name_start, ((arena).nodes[inner]).name_end, tp_starts, tp_ends, ntp);
  if (inner_idx >= 0) {
  flowc_cgen_emit_type(w, arena, src, tp_concrete[inner_idx]);
  flowc_cgen_putc(w, 42);
  return;
}
}
  if (inner != AST_NONE && flowc_cgen_span_is(src, ns, ne, "span") == 1) {
  int32_t inner_idx = flowc_cgen_find_tp(src, ((arena).nodes[inner]).name_start, ((arena).nodes[inner]).name_end, tp_starts, tp_ends, ntp);
  if (inner_idx >= 0) {
  flowc_cgen_puts(w, "flowc_span_");
  flowc_cgen_emit_type(w, arena, src, tp_concrete[inner_idx]);
  return;
}
}
  if (inner != AST_NONE && flowc_cgen_is_struct_type(arena, src, ty) == 1) {
  flowc_cgen_put_span(w, src, ns, ne);
  int32_t ta = inner;
  while (ta != AST_NONE) {
  if (((arena).nodes[ta]).kind == AST_TYPE) {
  int32_t ta_idx = flowc_cgen_find_tp(src, ((arena).nodes[ta]).name_start, ((arena).nodes[ta]).name_end, tp_starts, tp_ends, ntp);
  flowc_cgen_putc(w, 95);
  if (ta_idx >= 0) {
  flowc_cgen_put_span(w, src, ((arena).nodes[tp_concrete[ta_idx]]).name_start, ((arena).nodes[tp_concrete[ta_idx]]).name_end);
} else {
  flowc_cgen_put_span(w, src, ((arena).nodes[ta]).name_start, ((arena).nodes[ta]).name_end);
}
}
  ta = ((arena).nodes[ta]).next;
}
  return;
}
  flowc_cgen_emit_type(w, arena, src, ty);
}

void flowc_cgen_emit_struct_mono(CgenBuf* w, AstArena arena, uint8_t* src, int32_t id, int32_t* tp_starts, int32_t* tp_ends, int32_t* tp_concrete, int32_t ntp) {
  flowc_cgen_puts(w, "typedef struct ");
  flowc_cgen_put_span(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  int32_t i = 0;
  while (i < ntp) {
  flowc_cgen_putc(w, 95);
  flowc_cgen_put_span(w, src, ((arena).nodes[tp_concrete[i]]).name_start, ((arena).nodes[tp_concrete[i]]).name_end);
  i = (i + 1);
}
  flowc_cgen_puts(w, " {\n");
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
  if (arr_n > 0) {
  flowc_cgen_emit_type_subst(w, arena, src, arr_inner, tp_starts, tp_ends, tp_concrete, ntp);
} else {
  flowc_cgen_emit_type_subst(w, arena, src, fty, tp_starts, tp_ends, tp_concrete, ntp);
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
  i = 0;
  while (i < ntp) {
  flowc_cgen_putc(w, 95);
  flowc_cgen_put_span(w, src, ((arena).nodes[tp_concrete[i]]).name_start, ((arena).nodes[tp_concrete[i]]).name_end);
  i = (i + 1);
}
  flowc_cgen_puts(w, ";\n\n");
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

int32_t flowc_cgen_pp_is_keyword(uint8_t* text, int32_t start, int32_t end) {
  if (flowc_cgen_span_is(text, start, end, "void")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "int")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "char")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "long")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "short")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "float")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "double")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "unsigned")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "signed")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "const")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "struct")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "union")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "enum")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "typedef")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "static")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "extern")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "inline")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "return")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "if")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "else")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "while")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "for")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "do")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "switch")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "case")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "break")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "continue")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "default")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "sizeof")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "defined")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "goto")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "restrict")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "auto")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "register")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "volatile")) {
  return 1;
}
  return 0;
}

int32_t flowc_cgen_pp_is_macro_fn(uint8_t* text, int32_t start, int32_t end) {
  if (flowc_cgen_span_is(text, start, end, "memcpy")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "memmove")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "memset")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "memccpy")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "strcpy")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "strncpy")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "strcat")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "strncat")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "strlcpy")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "strlcat")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "stpcpy")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "stpncpy")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "sprintf")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "snprintf")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "vsprintf")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "vsnprintf")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "fprintf")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "vfprintf")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "printf")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "vprintf")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "asprintf")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "vasprintf")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "gets")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "fgets")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "fread")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "fwrite")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "strdup")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "bcopy")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "bzero")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "getc_unlocked")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "putc_unlocked")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "getchar_unlocked")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "putchar_unlocked")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "fputc")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "fputs")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "putc")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "getchar")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "putchar")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "fgetc")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "getc")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "atoi")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "atof")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "atol")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "strtol")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "strtod")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "strtoul")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "exit")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "abort")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "malloc")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "free")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "calloc")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "realloc")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "sqrt")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "fabs")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "pow")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "abs")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "labs")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "sin")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "cos")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "tan")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "log")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "log2")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "log10")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "exp")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "floor")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "ceil")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "round")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "fmod")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "strcmp")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "strncmp")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "strlen")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "strchr")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "strrchr")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "strstr")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "popen")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "pclose")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "fscanf")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "sscanf")) {
  return 1;
}
  if (flowc_cgen_span_is(text, start, end, "scanf")) {
  return 1;
}
  return 0;
}

int32_t flowc_cgen_pp_contains(uint8_t* text, int32_t start, int32_t end, const char* lit) {
  uint8_t* lit_ptr = (uint8_t*)((uint8_t*)(lit));
  int32_t lit_len = (int32_t)(strlen(lit_ptr));
  if (lit_len <= 0 || (end - start) < lit_len) {
  return 0;
}
  int32_t i = start;
  while ((i + lit_len) <= end) {
  int32_t is_match = 1;
  int32_t j = 0;
  while (j < lit_len) {
  if (text[(i + j)] != lit_ptr[j]) {
  is_match = 0;
  break;
}
  j = (j + 1);
}
  if (is_match == 1) {
  return 1;
}
  i = (i + 1);
}
  return 0;
}

void flowc_cgen_emit_cimport(CgenBuf* w, uint8_t* src, int32_t name_start, int32_t name_end) {
  uint8_t* cmd_buf = (uint8_t*)(malloc(1024));
  if (cmd_buf == NULL) {
  return;
}
  int32_t pos = 0;
  const char* prefix = "echo '#include <";
  uint8_t* prefix_ptr = (uint8_t*)((uint8_t*)(prefix));
  int32_t prefix_len = (int32_t)(strlen(prefix_ptr));
  int32_t i = 0;
  while (i < prefix_len && pos < 1023) {
  cmd_buf[pos] = prefix_ptr[i];
  pos = (pos + 1);
  i = (i + 1);
}
  i = (name_start + 1);
  while (i < (name_end - 1) && pos < 1023) {
  cmd_buf[pos] = src[i];
  pos = (pos + 1);
  i = (i + 1);
}
  const char* suffix = ">' | cpp -P -";
  uint8_t* suffix_ptr = (uint8_t*)((uint8_t*)(suffix));
  int32_t suffix_len = (int32_t)(strlen(suffix_ptr));
  i = 0;
  while (i < suffix_len && pos < 1023) {
  cmd_buf[pos] = suffix_ptr[i];
  pos = (pos + 1);
  i = (i + 1);
}
  cmd_buf[pos] = 0;
  void* fp = (void*)(popen((const char*)(cmd_buf), (const char*)("r")));
  free(cmd_buf);
  if (fp == NULL) {
  return;
}
  uint8_t* pp_buf = (uint8_t*)(malloc(1048576));
  if (pp_buf == NULL) {
  pclose(fp);
  return;
}
  int32_t pp_len = 0;
  int32_t got = fread((pp_buf + pp_len), 1, 4096, fp);
  while (got > 0 && pp_len < (1048576 - 4096)) {
  pp_len = (pp_len + got);
  got = fread((pp_buf + pp_len), 1, 4096, fp);
}
  pclose(fp);
  flowc_cgen_puts(w, "#include <");
  flowc_cgen_put_span(w, src, (name_start + 1), (name_end - 1));
  flowc_cgen_puts(w, ">\n");
  int32_t pos2 = 0;
  while (pos2 < pp_len) {
  while (pos2 < pp_len && (pp_buf[pos2] == 32 || pp_buf[pos2] == 10 || pp_buf[pos2] == 9 || pp_buf[pos2] == 13)) {
  pos2 = (pos2 + 1);
}
  if (pos2 >= pp_len) {
  break;
}
  int32_t line_start = pos2;
  while (pos2 < pp_len && pp_buf[pos2] != 59) {
  pos2 = (pos2 + 1);
}
  int32_t line_end = pos2;
  if (pos2 < pp_len && pp_buf[pos2] == 59) {
  pos2 = (pos2 + 1);
}
  while (line_end > line_start && (pp_buf[(line_end - 1)] == 10 || pp_buf[(line_end - 1)] == 13 || pp_buf[(line_end - 1)] == 32 || pp_buf[(line_end - 1)] == 9)) {
  line_end = (line_end - 1);
}
  int32_t has_brace = 0;
  int32_t scan_br = line_start;
  while (scan_br < line_end) {
  if (pp_buf[scan_br] == 123 || pp_buf[scan_br] == 125) {
  has_brace = 1;
  break;
}
  scan_br = (scan_br + 1);
}
  if (has_brace == 1) {
  continue;
}
  int32_t paren_pos = (0 - 1);
  int32_t j = line_start;
  while (j < line_end) {
  if (pp_buf[j] == 40) {
  paren_pos = j;
  break;
}
  j = (j + 1);
}
  if (paren_pos < 0) {
  continue;
}
  int32_t depth = 1;
  int32_t close_pos = (paren_pos + 1);
  while (close_pos < line_end && depth > 0) {
  if (pp_buf[close_pos] == 40) {
  depth = (depth + 1);
} else {
  if (pp_buf[close_pos] == 41) {
  depth = (depth - 1);
}
}
  close_pos = (close_pos + 1);
}
  if (depth != 0) {
  continue;
}
  close_pos = (close_pos - 1);
  int32_t fn_end = paren_pos;
  while (fn_end > line_start && (pp_buf[(fn_end - 1)] == 32 || pp_buf[(fn_end - 1)] == 9 || pp_buf[(fn_end - 1)] == 10 || pp_buf[(fn_end - 1)] == 13)) {
  fn_end = (fn_end - 1);
}
  int32_t fn_start = fn_end;
  while (fn_start > line_start && (pp_buf[(fn_start - 1)] >= 65 && pp_buf[(fn_start - 1)] <= 90 || pp_buf[(fn_start - 1)] >= 97 && pp_buf[(fn_start - 1)] <= 122 || pp_buf[(fn_start - 1)] >= 48 && pp_buf[(fn_start - 1)] <= 57 || pp_buf[(fn_start - 1)] == 95)) {
  fn_start = (fn_start - 1);
}
  int32_t fn_len = (fn_end - fn_start);
  if (fn_len <= 0) {
  continue;
}
  if (fn_len >= 2 && pp_buf[fn_start] == 95 && pp_buf[(fn_start + 1)] == 95) {
  continue;
}
  if (pp_buf[fn_start] >= 65 && pp_buf[fn_start] <= 90) {
  continue;
}
  if (flowc_cgen_pp_is_keyword(pp_buf, fn_start, fn_end) == 1) {
  continue;
}
  if (flowc_cgen_pp_is_macro_fn(pp_buf, fn_start, fn_end) == 1) {
  continue;
}
  int32_t ret_end = fn_start;
  while (ret_end > line_start && (pp_buf[(ret_end - 1)] == 32 || pp_buf[(ret_end - 1)] == 9 || pp_buf[(ret_end - 1)] == 10 || pp_buf[(ret_end - 1)] == 13)) {
  ret_end = (ret_end - 1);
}
  if (ret_end <= line_start) {
  continue;
}
  if (flowc_cgen_pp_contains(pp_buf, line_start, ret_end, "defined") == 1) {
  continue;
}
  flowc_cgen_put_span(w, pp_buf, line_start, ret_end);
  flowc_cgen_putc(w, 32);
  flowc_cgen_put_span(w, pp_buf, fn_start, fn_end);
  flowc_cgen_putc(w, 40);
  flowc_cgen_put_span(w, pp_buf, (paren_pos + 1), close_pos);
  flowc_cgen_puts(w, ");\n");
}
  free(pp_buf);
}

void flowc_cgen_scan_cembed_names(CgenBuf* w, uint8_t* src, int32_t start, int32_t end) {
  int32_t i = start;
  while (i < end) {
  int32_t kw_len = 0;
  if (flowc_cgen_span_is(src, i, (i + 3), "int") == 1) {
  kw_len = 3;
}
  if (kw_len == 0 && flowc_cgen_span_is(src, i, (i + 4), "void") == 1) {
  kw_len = 4;
}
  if (kw_len == 0 && flowc_cgen_span_is(src, i, (i + 4), "char") == 1) {
  kw_len = 4;
}
  if (kw_len == 0 && flowc_cgen_span_is(src, i, (i + 5), "float") == 1) {
  kw_len = 5;
}
  if (kw_len == 0 && flowc_cgen_span_is(src, i, (i + 5), "short") == 1) {
  kw_len = 5;
}
  if (kw_len == 0 && flowc_cgen_span_is(src, i, (i + 4), "long") == 1) {
  kw_len = 4;
}
  if (kw_len == 0 && flowc_cgen_span_is(src, i, (i + 5), "double") == 1) {
  kw_len = 5;
}
  if (kw_len == 0 && flowc_cgen_span_is(src, i, (i + 4), "bool") == 1) {
  kw_len = 4;
}
  if (kw_len == 0 && flowc_cgen_span_is(src, i, (i + 7), "int32_t") == 1) {
  kw_len = 7;
}
  if (kw_len == 0 && flowc_cgen_span_is(src, i, (i + 7), "int64_t") == 1) {
  kw_len = 7;
}
  if (kw_len == 0 && flowc_cgen_span_is(src, i, (i + 8), "uint32_t") == 1) {
  kw_len = 8;
}
  if (kw_len == 0 && flowc_cgen_span_is(src, i, (i + 8), "uint64_t") == 1) {
  kw_len = 8;
}
  if (kw_len == 0 && flowc_cgen_span_is(src, i, (i + 7), "size_t") == 1) {
  kw_len = 6;
}
  if (kw_len > 0) {
  if (i > start) {
  int32_t prev = src[(i - 1)];
  if (prev >= 65 && prev <= 90 || prev >= 97 && prev <= 122 || prev == 95 || prev >= 48 && prev <= 57) {
  i = (i + 1);
  continue;
}
}
  int32_t j = (i + kw_len);
  while (j < end && (src[j] == 32 || src[j] == 9 || src[j] == 10)) {
  j = (j + 1);
}
  while (j < end && src[j] == 42) {
  j = (j + 1);
  while (j < end && (src[j] == 32 || src[j] == 9)) {
  j = (j + 1);
}
}
  int32_t name_start = j;
  while (j < end && (src[j] >= 65 && src[j] <= 90 || src[j] >= 97 && src[j] <= 122 || src[j] == 95 || src[j] >= 48 && src[j] <= 57)) {
  j = (j + 1);
}
  int32_t name_end = j;
  while (j < end && (src[j] == 32 || src[j] == 9)) {
  j = (j + 1);
}
  if (name_end > name_start && j < end && src[j] == 40) {
  if ((w[0]).cembed_count < 32) {
  int32_t nlen = (name_end - name_start);
  if ((((w[0]).cembed_count * 128) + nlen) <= 4096) {
  int32_t off = ((w[0]).cembed_count * 128);
  int32_t k = 0;
  while (k < nlen) {
  (w[0]).cembed_names[(off + k)] = src[(name_start + k)];
  k = (k + 1);
}
  (w[0]).cembed_offs[(w[0]).cembed_count] = off;
  (w[0]).cembed_lens[(w[0]).cembed_count] = nlen;
  (w[0]).cembed_count = ((w[0]).cembed_count + 1);
}
}
}
  i = j;
  continue;
}
  i = (i + 1);
}
}

int32_t flowc_cgen_is_cembed_fn(CgenBuf* w, uint8_t* src, int32_t ns, int32_t ne) {
  int32_t n = (ne - ns);
  int32_t idx = 0;
  while (idx < (w[0]).cembed_count) {
  if ((w[0]).cembed_lens[idx] == n) {
  int32_t off = (w[0]).cembed_offs[idx];
  int32_t k = 0;
  int32_t is_match = 1;
  while (k < n) {
  if ((w[0]).cembed_names[(off + k)] != src[(ns + k)]) {
  is_match = 0;
  k = n;
}
  k = (k + 1);
}
  if (is_match == 1) {
  return 1;
}
}
  idx = (idx + 1);
}
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
  uint8_t cembed_name_buf[4096] = {  };
  int32_t cembed_off_arr[32] = {  };
  int32_t cembed_len_arr[32] = {  };
  (w).cembed_names = (&cembed_name_buf[0]);
  (w).cembed_offs = (&cembed_off_arr[0]);
  (w).cembed_lens = (&cembed_len_arr[0]);
  int32_t cap_start_arr[64] = {  };
  int32_t cap_end_arr[64] = {  };
  (w).cap_starts = (&cap_start_arr[0]);
  (w).cap_ends = (&cap_end_arr[0]);
  (w).cap_count = 0;
  int32_t lam_cap_lambda_arr[256] = {  };
  int32_t lam_cap_start_arr[256] = {  };
  int32_t lam_cap_end_arr[256] = {  };
  (w).lambda_cap_lambda = (&lam_cap_lambda_arr[0]);
  (w).lambda_cap_start = (&lam_cap_start_arr[0]);
  (w).lambda_cap_end = (&lam_cap_end_arr[0]);
  (w).lambda_cap_count = 0;
  (w).cembed_count = 0;
  if ((flags % 2) == 0) {
  flowc_cgen_puts((&w), "#include <stdint.h>\n");
  flowc_cgen_puts((&w), "#include <stdbool.h>\n");
  flowc_cgen_puts((&w), "#include <stdlib.h>\n");
  flowc_cgen_puts((&w), "#include <stdio.h>\n");
  flowc_cgen_puts((&w), "#include <string.h>\n");
  flowc_cgen_puts((&w), "#include <math.h>\n");
  flowc_cgen_puts((&w), "#include <complex.h>\n");
  flowc_cgen_puts((&w), "#pragma clang diagnostic ignored \"-Wint-conversion\"\n");
  flowc_cgen_puts((&w), "#pragma clang diagnostic ignored \"-Wincompatible-pointer-types\"\n");
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
  flowc_cgen_puts((&w), "#define __flow_in_arr(arr, val) __extension__ ({ \\\n");
  flowc_cgen_puts((&w), "    int _found = 0; \\\n");
  flowc_cgen_puts((&w), "    size_t _n = sizeof(arr)/sizeof((arr)[0]); \\\n");
  flowc_cgen_puts((&w), "    for (size_t _i = 0; _i < _n; _i++) { \\\n");
  flowc_cgen_puts((&w), "        if ((arr)[_i] == (val)) { _found = 1; break; } \\\n");
  flowc_cgen_puts((&w), "    } _found; })\n");
  flowc_cgen_putc((&w), 10);
  flowc_cgen_puts((&w), "#define __flow_dbg(x) (__extension__ ({ int32_t __flow_dbg_v = (x); fprintf(stderr, \"dbg: %s = %d\\n\", #x, __flow_dbg_v); __flow_dbg_v; }))\n");
  flowc_cgen_putc((&w), 10);
  flowc_cgen_puts((&w), "#include <sys/stat.h>\n");
  flowc_cgen_puts((&w), "#ifndef FLOWC_IO_FOPEN\n#define FLOWC_IO_FOPEN\n");
  flowc_cgen_puts((&w), "static inline void* flowc_io_fopen(const char* path, const char* mode) { return fopen(path, mode); }\n");
  flowc_cgen_puts((&w), "#endif\n");
  flowc_cgen_puts((&w), "#ifndef FLOWC_IO_FCLOSE\n#define FLOWC_IO_FCLOSE\n");
  flowc_cgen_puts((&w), "static inline int32_t flowc_io_fclose(void* fp) { return fclose(fp); }\n");
  flowc_cgen_puts((&w), "#endif\n");
  flowc_cgen_puts((&w), "#ifndef FLOWC_IO_FREAD\n#define FLOWC_IO_FREAD\n");
  flowc_cgen_puts((&w), "static inline int32_t flowc_io_fread(uint8_t* buf, int32_t size, int32_t n, void* fp) { return fread(buf, size, n, fp); }\n");
  flowc_cgen_puts((&w), "#endif\n");
  flowc_cgen_puts((&w), "#ifndef FLOWC_IO_FWRITE\n#define FLOWC_IO_FWRITE\n");
  flowc_cgen_puts((&w), "static inline int32_t flowc_io_fwrite(uint8_t* buf, int32_t size, int32_t n, void* fp) { return fwrite(buf, size, n, fp); }\n");
  flowc_cgen_puts((&w), "#endif\n");
  flowc_cgen_puts((&w), "#ifndef FLOWC_IO_FSEEK\n#define FLOWC_IO_FSEEK\n");
  flowc_cgen_puts((&w), "static inline int32_t flowc_io_fseek(void* fp, int64_t offset, int32_t whence) { return fseek(fp, offset, whence); }\n");
  flowc_cgen_puts((&w), "#endif\n");
  flowc_cgen_puts((&w), "#ifndef FLOWC_IO_FTELL\n#define FLOWC_IO_FTELL\n");
  flowc_cgen_puts((&w), "static inline int64_t flowc_io_ftell(void* fp) { return ftell(fp); }\n");
  flowc_cgen_puts((&w), "#endif\n");
  flowc_cgen_puts((&w), "#ifndef FLOWC_READ_FILE\n#define FLOWC_READ_FILE\n");
  flowc_cgen_puts((&w), "static inline int32_t flowc_read_file(const char* path, uint8_t* buf, int32_t cap) { void* fp = fopen(path, \"rb\"); if (fp == 0) { return -1; } if (cap <= 0) { fclose(fp); return 0; } int32_t n = fread(buf, 1, cap, fp); fclose(fp); return n < 0 ? -1 : n; }\n");
  flowc_cgen_puts((&w), "#endif\n");
  flowc_cgen_puts((&w), "#ifndef FLOWC_WRITE_FILE\n#define FLOWC_WRITE_FILE\n");
  flowc_cgen_puts((&w), "static inline int32_t flowc_write_file(const char* path, uint8_t* buf, int32_t n) { void* fp = fopen(path, \"wb\"); if (fp == 0) { return -1; } if (n <= 0) { fclose(fp); return 0; } int32_t w = fwrite(buf, 1, n, fp); fclose(fp); return w != n ? -1 : 0; }\n");
  flowc_cgen_puts((&w), "#endif\n");
  flowc_cgen_puts((&w), "#ifndef FLOWC_IO_REMOVE\n#define FLOWC_IO_REMOVE\n");
  flowc_cgen_puts((&w), "static inline int32_t flowc_io_remove(const char* path) { return remove(path); }\n");
  flowc_cgen_puts((&w), "#endif\n");
  flowc_cgen_puts((&w), "#ifndef FLOWC_IO_MKDIR\n#define FLOWC_IO_MKDIR\n");
  flowc_cgen_puts((&w), "static inline int32_t flowc_io_mkdir(const char* path) { return mkdir(path, 493); }\n");
  flowc_cgen_puts((&w), "#endif\n");
  flowc_cgen_puts((&w), "#ifndef FLOWC_IO_EXISTS\n#define FLOWC_IO_EXISTS\n");
  flowc_cgen_puts((&w), "static inline int32_t flowc_io_exists(const char* path) { struct stat st; return stat(path, &st) == 0 ? 1 : 0; }\n");
  flowc_cgen_puts((&w), "#endif\n");
  flowc_cgen_puts((&w), "#ifndef FLOWC_IO_FILE_SIZE\n#define FLOWC_IO_FILE_SIZE\n");
  flowc_cgen_puts((&w), "static inline int64_t flowc_io_file_size(const char* path) { void* fp = fopen(path, \"rb\"); if (fp == 0) { return -1; } fseek(fp, 0, 2); int64_t sz = ftell(fp); fclose(fp); return sz; }\n");
  flowc_cgen_puts((&w), "#endif\n");
  flowc_cgen_puts((&w), "#ifndef FLOWC_IO_POPEN_READ\n#define FLOWC_IO_POPEN_READ\n");
  flowc_cgen_puts((&w), "static inline int32_t flowc_io_popen_read(const char* cmd, uint8_t* buf, int32_t cap) { void* fp = popen(cmd, \"r\"); if (fp == 0) { return -1; } if (cap <= 0) { pclose(fp); return 0; } int32_t n = fread(buf, 1, cap, fp); pclose(fp); return n < 0 ? -1 : n; }\n");
  flowc_cgen_puts((&w), "#endif\n");
  flowc_cgen_puts((&w), "#ifndef FLOWC_IO_SYSTEM\n#define FLOWC_IO_SYSTEM\n");
  flowc_cgen_puts((&w), "static inline int32_t flowc_io_system(const char* cmd) { return system(cmd); }\n");
  flowc_cgen_puts((&w), "#endif\n");
  flowc_cgen_puts((&w), "#ifndef FLOWC_SORT\n#define FLOWC_SORT\n");
  flowc_cgen_puts((&w), "#include <stdlib.h>\n");
  flowc_cgen_puts((&w), "static int flowc_cmp_i32(const void* a, const void* b) { int32_t x = *(const int32_t*)a; int32_t y = *(const int32_t*)b; return (x > y) - (x < y); }\n");
  flowc_cgen_puts((&w), "static int flowc_cmp_u8(const void* a, const void* b) { uint8_t x = *(const uint8_t*)a; uint8_t y = *(const uint8_t*)b; return (x > y) - (x < y); }\n");
  flowc_cgen_puts((&w), "static int flowc_cmp_f64(const void* a, const void* b) { double x = *(const double*)a; double y = *(const double*)b; int xu = (x != x), yu = (y != y); if (xu && yu) { union { double d; uint64_t u; } ux, uy; ux.d = x; uy.d = y; return (ux.u < uy.u) - (ux.u > uy.u); } if (xu) { union { double d; uint64_t u; } ux; ux.d = x; return (ux.u >> 63) ? -1 : 1; } if (yu) { union { double d; uint64_t u; } uy; uy.d = y; return (uy.u >> 63) ? 1 : -1; } if (x == y) { union { double d; uint64_t u; } ux, uy; ux.d = x; uy.d = y; return (ux.u < uy.u) - (ux.u > uy.u); } return (x > y) - (x < y); }\n");
  flowc_cgen_puts((&w), "static int flowc_cmp_f32(const void* a, const void* b) { float x = *(const float*)a; float y = *(const float*)b; if (x != x) return 1; if (y != y) return -1; return (x > y) - (x < y); }\n");
  flowc_cgen_puts((&w), "static int32_t flowc_sort_dispatch(void* a, int32_t n, int32_t sz, int32_t desc) { if (sz == 1) qsort(a, n, 1, flowc_cmp_u8); else if (sz == 4) qsort(a, n, 4, flowc_cmp_i32); else if (sz == 8) qsort(a, n, 8, flowc_cmp_f64); else qsort(a, n, sz, flowc_cmp_i32); if (desc) { int32_t i = 0, j = n - 1; while (i < j) { char tmp[8]; memcpy(tmp, (char*)a + i * sz, sz); memcpy((char*)a + i * sz, (char*)a + j * sz, sz); memcpy((char*)a + j * sz, tmp, sz); i++; j--; } } return 0; }\n");
  flowc_cgen_puts((&w), "static int32_t flowc_find_i32(int32_t* a, int32_t n, int32_t target) { for (int32_t i = 0; i < n; i++) { if (a[i] == target) return i; } return -1; }\n");
  flowc_cgen_puts((&w), "static int32_t flowc_sort_struct(void* a, int32_t n, int32_t sz, int32_t desc) { char* base = (char*)a; char* tmp = (char*)malloc(sz); for (int32_t i = 1; i < n; i++) { memcpy(tmp, base + i * sz, sz); int32_t j = i; while (j > 0) { int32_t cmp = *(int32_t*)(base + (j-1) * sz) - *(int32_t*)tmp; if (desc ? (cmp <= 0) : (cmp > 0)) { memcpy(base + j * sz, base + (j-1) * sz, sz); j--; } else break; } memcpy(base + j * sz, tmp, sz); } free(tmp); return 0; }\n");
  flowc_cgen_puts((&w), "#endif\n");
  flowc_cgen_putc((&w), 10);
}
  int32_t param_span_buf[32] = {  };
  int32_t per_lam_buf[32] = {  };
  int32_t li = 0;
  while (li < (arena).len) {
  if (((arena).nodes[li]).kind == AST_FN) {
  if (((arena).nodes[li]).name_start < 0) {
  int32_t lam_id = (0 - ((arena).nodes[li]).name_start);
  int32_t nparams = 0;
  int32_t param = ((arena).nodes[li]).a;
  while (param != AST_NONE && nparams < 16) {
  param_span_buf[(nparams * 2)] = ((arena).nodes[param]).name_start;
  param_span_buf[((nparams * 2) + 1)] = ((arena).nodes[param]).name_end;
  nparams = (nparams + 1);
  param = ((arena).nodes[param]).next;
}
  flowc_cgen_scan_captures((&w), arena, src, ((arena).nodes[li]).c, (&param_span_buf[0]), nparams);
  int32_t per_lam_count = flowc_cgen_scan_lambda_caps(arena, src, ((arena).nodes[li]).c, (&per_lam_buf[0]), 0, (&param_span_buf[0]), nparams);
  int32_t pi = 0;
  while (pi < per_lam_count && (w).lambda_cap_count < 256) {
  (w).lambda_cap_lambda[(w).lambda_cap_count] = lam_id;
  (w).lambda_cap_start[(w).lambda_cap_count] = per_lam_buf[(pi * 2)];
  (w).lambda_cap_end[(w).lambda_cap_count] = per_lam_buf[((pi * 2) + 1)];
  (w).lambda_cap_count = ((w).lambda_cap_count + 1);
  pi = (pi + 1);
}
}
}
  li = (li + 1);
}
  int32_t ci = 0;
  while (ci < (w).cap_count) {
  flowc_cgen_puts((&w), "static int32_t __flowc_cap_");
  flowc_cgen_put_span((&w), src, (w).cap_starts[ci], (w).cap_ends[ci]);
  flowc_cgen_puts((&w), " = 0;\n");
  ci = (ci + 1);
}
  int32_t item = ((arena).nodes[root]).a;
  while (item != AST_NONE) {
  if (((arena).nodes[item]).kind == AST_C_INCLUDE) {
  flowc_cgen_puts((&w), "#include \"");
  flowc_cgen_put_span((&w), src, (((arena).nodes[item]).name_start + 1), (((arena).nodes[item]).name_end - 1));
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
  flowc_cgen_put_span((&w), src, (((arena).nodes[item]).name_start + 1), (((arena).nodes[item]).name_end - 1));
  flowc_cgen_putc((&w), 10);
  flowc_cgen_scan_cembed_names((&w), src, (((arena).nodes[item]).name_start + 1), (((arena).nodes[item]).name_end - 1));
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
  if (st != AST_NONE && ((arena).nodes[st]).b == AST_NONE) {
  flowc_cgen_emit_struct((&w), arena, src, st);
}
  item = ((arena).nodes[item]).next;
}
  item = ((arena).nodes[root]).a;
  while (item != AST_NONE) {
  int32_t en = flowc_cgen_unwrap(arena, item, AST_ENUM);
  if (en != AST_NONE) {
  flowc_cgen_puts((&w), "typedef enum {");
  int32_t var = ((arena).nodes[en]).a;
  int32_t first = 1;
  while (var != AST_NONE) {
  if (first == 0) {
  flowc_cgen_puts((&w), ", ");
} else {
  flowc_cgen_putc((&w), 32);
}
  first = 0;
  flowc_cgen_put_span((&w), src, ((arena).nodes[en]).name_start, ((arena).nodes[en]).name_end);
  flowc_cgen_putc((&w), 95);
  flowc_cgen_put_span((&w), src, ((arena).nodes[var]).name_start, ((arena).nodes[var]).name_end);
  var = ((arena).nodes[var]).next;
}
  flowc_cgen_puts((&w), " } ");
  flowc_cgen_put_span((&w), src, ((arena).nodes[en]).name_start, ((arena).nodes[en]).name_end);
  flowc_cgen_puts((&w), "_Tag;\n");
  flowc_cgen_puts((&w), "typedef struct { ");
  flowc_cgen_put_span((&w), src, ((arena).nodes[en]).name_start, ((arena).nodes[en]).name_end);
  flowc_cgen_puts((&w), "_Tag tag; } ");
  flowc_cgen_put_span((&w), src, ((arena).nodes[en]).name_start, ((arena).nodes[en]).name_end);
  flowc_cgen_puts((&w), ";\n");
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
  int32_t ti = 0;
  while (ti < (arena).len) {
  if (((arena).nodes[ti]).kind == AST_TYPE) {
  int32_t tns = ((arena).nodes[ti]).name_start;
  int32_t tne = ((arena).nodes[ti]).name_end;
  if (flowc_cgen_span_is(src, tns, tne, "span") == 1) {
  int32_t inner = ((arena).nodes[ti]).a;
  if (inner != AST_NONE) {
  flowc_cgen_puts((&w), "#ifndef FLOWC_SPAN_");
  flowc_cgen_emit_type((&w), arena, src, inner);
  flowc_cgen_puts((&w), "\n#define FLOWC_SPAN_");
  flowc_cgen_emit_type((&w), arena, src, inner);
  flowc_cgen_puts((&w), "\ntypedef struct { ");
  flowc_cgen_emit_type((&w), arena, src, inner);
  flowc_cgen_puts((&w), "* data; int32_t len; } flowc_span_");
  flowc_cgen_emit_type((&w), arena, src, inner);
  flowc_cgen_puts((&w), ";\n#endif\n");
}
}
}
  ti = (ti + 1);
}
  flowc_cgen_emit_mono((&w), arena, src, root);
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
  if (flowc_cgen_is_libc_fn(arena, src, ef) == 0) {
  if (flowc_cgen_is_cembed_fn((&w), src, ((arena).nodes[ef]).name_start, ((arena).nodes[ef]).name_end) == 0) {
  flowc_cgen_emit_fn((&w), arena, src, ef);
}
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
  int32_t i = 0;
  while (i < (arena).len) {
  if (((arena).nodes[i]).kind == AST_FN) {
  if (((arena).nodes[i]).name_start < 0) {
  int32_t lam_id = (0 - ((arena).nodes[i]).name_start);
  int32_t ret_ty = ((arena).nodes[i]).b;
  if (ret_ty == AST_NONE) {
  flowc_cgen_puts((&w), "void");
} else {
  flowc_cgen_emit_type((&w), arena, src, ret_ty);
}
  flowc_cgen_puts((&w), " __flowc_lambda_");
  flowc_cgen_put_i32((&w), lam_id);
  flowc_cgen_putc((&w), 40);
  int32_t param = ((arena).nodes[i]).a;
  int32_t first = 1;
  while (param != AST_NONE) {
  if (first == 0) {
  flowc_cgen_puts((&w), ", ");
}
  first = 0;
  flowc_cgen_emit_param((&w), arena, src, param);
  param = ((arena).nodes[param]).next;
}
  flowc_cgen_puts((&w), ");\n");
}
}
  i = (i + 1);
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
  i = 0;
  while (i < (arena).len) {
  if (((arena).nodes[i]).kind == AST_FN) {
  if (((arena).nodes[i]).name_start < 0) {
  int32_t lam_id = (0 - ((arena).nodes[i]).name_start);
  int32_t ret_ty = ((arena).nodes[i]).b;
  if (ret_ty == AST_NONE) {
  flowc_cgen_puts((&w), "void");
} else {
  flowc_cgen_emit_type((&w), arena, src, ret_ty);
}
  flowc_cgen_puts((&w), " __flowc_lambda_");
  flowc_cgen_put_i32((&w), lam_id);
  flowc_cgen_putc((&w), 40);
  int32_t param = ((arena).nodes[i]).a;
  int32_t first = 1;
  while (param != AST_NONE) {
  if (first == 0) {
  flowc_cgen_puts((&w), ", ");
}
  first = 0;
  flowc_cgen_emit_param((&w), arena, src, param);
  param = ((arena).nodes[param]).next;
}
  flowc_cgen_puts((&w), ") ");
  (w).in_lambda = 1;
  flowc_cgen_emit_block((&w), arena, src, ((arena).nodes[i]).c);
  (w).in_lambda = 0;
  flowc_cgen_putc((&w), 10);
}
}
  i = (i + 1);
}
  if ((w).err != 0) {
  return (0 - 1);
}
  return (w).len;
}

int32_t flowc_cgen_emit_ex(AstArena arena, int32_t root, uint8_t* src, uint8_t* out, int32_t out_cap, int32_t flags) {
  return flowc_cgen_emit_sigs(arena, root, src, out, out_cap, flags, NULL, 0);
}

int32_t flowc_cgen_is_type_param_name(AstArena arena, uint8_t* src, int32_t ns, int32_t ne) {
  int32_t i = 0;
  while (i < (arena).len) {
  if (((arena).nodes[i]).kind == AST_STRUCT && ((arena).nodes[i]).b != AST_NONE) {
  int32_t tp = ((arena).nodes[i]).b;
  while (tp != AST_NONE) {
  if (flowc_cgen_span_eq(src, ns, ne, ((arena).nodes[tp]).name_start, ((arena).nodes[tp]).name_end) == 1) {
  return 1;
}
  tp = ((arena).nodes[tp]).next;
}
}
  i = (i + 1);
}
  return 0;
}

int32_t flowc_cgen_mono_hash(uint8_t* src, int32_t ns, int32_t ne, int32_t type_args, AstArena arena) {
  int32_t h = 5381;
  int32_t i = ns;
  while (i < ne) {
  h = ((h * 31) + src[i]);
  i = (i + 1);
}
  int32_t ta = type_args;
  while (ta != AST_NONE) {
  int32_t tas = ((arena).nodes[ta]).name_start;
  int32_t tae = ((arena).nodes[ta]).name_end;
  int32_t j = tas;
  while (j < tae) {
  h = ((h * 31) + src[j]);
  j = (j + 1);
}
  ta = ((arena).nodes[ta]).next;
}
  return h;
}

void flowc_cgen_emit_mono(CgenBuf* w, AstArena arena, uint8_t* src, int32_t root) {
  int32_t emitted_hashes[256] = { 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
  int32_t emitted_count = 0;
  int32_t tp_starts[8] = { 0, 0, 0, 0, 0, 0, 0, 0 };
  int32_t tp_ends[8] = { 0, 0, 0, 0, 0, 0, 0, 0 };
  int32_t tp_concrete[8] = { 0, 0, 0, 0, 0, 0, 0, 0 };
  int32_t i = 0;
  while (i < (arena).len) {
  int32_t kind = ((arena).nodes[i]).kind;
  if (kind == AST_CALL && ((arena).nodes[i]).b != AST_NONE) {
  int32_t ns = ((arena).nodes[i]).name_start;
  int32_t ne = ((arena).nodes[i]).name_end;
  int32_t ntp = 0;
  int32_t ta = ((arena).nodes[i]).b;
  int32_t is_param = 0;
  while (ta != AST_NONE && ntp < 8) {
  tp_concrete[ntp] = ta;
  if (flowc_cgen_is_type_param_name(arena, src, ((arena).nodes[ta]).name_start, ((arena).nodes[ta]).name_end) == 1) {
  is_param = 1;
}
  ntp = (ntp + 1);
  ta = ((arena).nodes[ta]).next;
}
  if (ntp > 0 && is_param == 0) {
  int32_t cur_hash = flowc_cgen_mono_hash(src, ns, ne, ((arena).nodes[i]).b, arena);
  int32_t already = 0;
  int32_t ei = 0;
  while (ei < emitted_count) {
  if (emitted_hashes[ei] == cur_hash) {
  already = 1;
}
  ei = (ei + 1);
}
  if (already == 0) {
  int32_t fn_id = AST_NONE;
  int32_t j = 0;
  while (j < (arena).len) {
  if (((arena).nodes[j]).kind == AST_FN && ((arena).nodes[j]).ival > 0) {
  if (flowc_cgen_span_eq(src, ns, ne, ((arena).nodes[j]).name_start, ((arena).nodes[j]).name_end) == 1) {
  fn_id = j;
}
}
  j = (j + 1);
}
  if (fn_id != AST_NONE) {
  int32_t ntp_names = 0;
  int32_t pos = ((arena).nodes[fn_id]).name_end;
  while (pos < 200000 && src[pos] != 60 && src[pos] != 40) {
  pos = (pos + 1);
}
  if (src[pos] == 60) {
  pos = (pos + 1);
  while (pos < 200000 && src[pos] != 62) {
  while (pos < 200000 && (src[pos] == 32 || src[pos] == 10 || src[pos] == 9)) {
  pos = (pos + 1);
}
  if (src[pos] == 62) {
  break;
}
  if (src[pos] == 44) {
  pos = (pos + 1);
} else {
  int32_t id_start = pos;
  while (pos < 200000 && (src[pos] >= 65 && src[pos] <= 90 || src[pos] >= 97 && src[pos] <= 122 || src[pos] >= 48 && src[pos] <= 57 || src[pos] == 95)) {
  pos = (pos + 1);
}
  if (ntp_names < 8) {
  tp_starts[ntp_names] = id_start;
  tp_ends[ntp_names] = pos;
  ntp_names = (ntp_names + 1);
}
  while (pos < 200000 && src[pos] != 44 && src[pos] != 62) {
  pos = (pos + 1);
}
}
}
}
  if (ntp_names == ntp) {
  (w[0]).mono_tp_starts = (&tp_starts[0]);
  (w[0]).mono_tp_ends = (&tp_ends[0]);
  (w[0]).mono_tp_concrete = (&tp_concrete[0]);
  (w[0]).mono_ntp = ntp;
  flowc_cgen_emit_fn_proto(w, arena, src, fn_id);
  flowc_cgen_emit_fn(w, arena, src, fn_id);
  (w[0]).mono_ntp = 0;
  if (emitted_count < 256) {
  emitted_hashes[emitted_count] = cur_hash;
  emitted_count = (emitted_count + 1);
}
}
}
}
}
}
  if (kind == AST_STRUCT_LIT && ((arena).nodes[i]).b != AST_NONE) {
  int32_t ns = ((arena).nodes[i]).name_start;
  int32_t ne = ((arena).nodes[i]).name_end;
  int32_t ntp = 0;
  int32_t ta = ((arena).nodes[i]).b;
  int32_t is_param = 0;
  while (ta != AST_NONE && ntp < 8) {
  tp_concrete[ntp] = ta;
  if (flowc_cgen_is_type_param_name(arena, src, ((arena).nodes[ta]).name_start, ((arena).nodes[ta]).name_end) == 1) {
  is_param = 1;
}
  ntp = (ntp + 1);
  ta = ((arena).nodes[ta]).next;
}
  if (ntp > 0 && is_param == 0) {
  int32_t cur_hash = flowc_cgen_mono_hash(src, ns, ne, ((arena).nodes[i]).b, arena);
  int32_t already = 0;
  int32_t ei = 0;
  while (ei < emitted_count) {
  if (emitted_hashes[ei] == cur_hash) {
  already = 1;
}
  ei = (ei + 1);
}
  if (already == 0) {
  int32_t st_id = AST_NONE;
  int32_t j = 0;
  while (j < (arena).len) {
  if (((arena).nodes[j]).kind == AST_STRUCT && ((arena).nodes[j]).b != AST_NONE) {
  if (flowc_cgen_span_eq(src, ns, ne, ((arena).nodes[j]).name_start, ((arena).nodes[j]).name_end) == 1) {
  st_id = j;
}
}
  j = (j + 1);
}
  if (st_id != AST_NONE) {
  int32_t ntp_names = 0;
  int32_t tp = ((arena).nodes[st_id]).b;
  while (tp != AST_NONE && ntp_names < 8) {
  tp_starts[ntp_names] = ((arena).nodes[tp]).name_start;
  tp_ends[ntp_names] = ((arena).nodes[tp]).name_end;
  ntp_names = (ntp_names + 1);
  tp = ((arena).nodes[tp]).next;
}
  if (ntp_names == ntp) {
  flowc_cgen_emit_struct_mono(w, arena, src, st_id, (&tp_starts[0]), (&tp_ends[0]), (&tp_concrete[0]), ntp);
  if (emitted_count < 256) {
  emitted_hashes[emitted_count] = cur_hash;
  emitted_count = (emitted_count + 1);
}
}
}
}
}
}
  if (kind == AST_TYPE && ((arena).nodes[i]).a != AST_NONE && ((arena).nodes[i]).ival == 0) {
  int32_t ns = ((arena).nodes[i]).name_start;
  int32_t ne = ((arena).nodes[i]).name_end;
  if (flowc_cgen_is_struct_type(arena, src, i) == 1) {
  int32_t ntp = 0;
  int32_t ta = ((arena).nodes[i]).a;
  int32_t is_param = 0;
  while (ta != AST_NONE && ntp < 8) {
  tp_concrete[ntp] = ta;
  if (flowc_cgen_is_type_param_name(arena, src, ((arena).nodes[ta]).name_start, ((arena).nodes[ta]).name_end) == 1) {
  is_param = 1;
}
  ntp = (ntp + 1);
  ta = ((arena).nodes[ta]).next;
}
  if (ntp > 0 && is_param == 0) {
  int32_t cur_hash = flowc_cgen_mono_hash(src, ns, ne, ((arena).nodes[i]).a, arena);
  int32_t already = 0;
  int32_t ei = 0;
  while (ei < emitted_count) {
  if (emitted_hashes[ei] == cur_hash) {
  already = 1;
}
  ei = (ei + 1);
}
  if (already == 0) {
  int32_t st_id = AST_NONE;
  int32_t j = 0;
  while (j < (arena).len) {
  if (((arena).nodes[j]).kind == AST_STRUCT && ((arena).nodes[j]).b != AST_NONE) {
  if (flowc_cgen_span_eq(src, ns, ne, ((arena).nodes[j]).name_start, ((arena).nodes[j]).name_end) == 1) {
  st_id = j;
}
}
  j = (j + 1);
}
  if (st_id != AST_NONE) {
  int32_t ntp_names = 0;
  int32_t tp = ((arena).nodes[st_id]).b;
  while (tp != AST_NONE && ntp_names < 8) {
  tp_starts[ntp_names] = ((arena).nodes[tp]).name_start;
  tp_ends[ntp_names] = ((arena).nodes[tp]).name_end;
  ntp_names = (ntp_names + 1);
  tp = ((arena).nodes[tp]).next;
}
  if (ntp_names == ntp) {
  flowc_cgen_emit_struct_mono(w, arena, src, st_id, (&tp_starts[0]), (&tp_ends[0]), (&tp_concrete[0]), ntp);
  if (emitted_count < 256) {
  emitted_hashes[emitted_count] = cur_hash;
  emitted_count = (emitted_count + 1);
}
}
}
}
}
}
}
  i = (i + 1);
}
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


typedef struct JsgenBuf {
  uint8_t* out;
  int32_t cap;
  int32_t len;
  int32_t err;
} JsgenBuf;

JsgenBuf flowc_jsgen_buf_init(uint8_t* out, int32_t cap);
void flowc_jsgen_putc(JsgenBuf* w, int32_t c);
void flowc_jsgen_puts(JsgenBuf* w, const char* s);
void flowc_jsgen_put_span(JsgenBuf* w, uint8_t* src, int32_t start, int32_t end);
void flowc_jsgen_put_i32(JsgenBuf* w, int32_t val);
void flowc_jsgen_emit_binop_op(JsgenBuf* w, int32_t op);
void flowc_jsgen_emit_expr(JsgenBuf* w, AstArena arena, uint8_t* src, int32_t id);
void flowc_jsgen_emit_block(JsgenBuf* w, AstArena arena, uint8_t* src, int32_t id);
void flowc_jsgen_emit_stmt(JsgenBuf* w, AstArena arena, uint8_t* src, int32_t id);
void flowc_jsgen_emit_fn(JsgenBuf* w, AstArena arena, uint8_t* src, int32_t id);
int32_t flowc_jsgen_unwrap_fn(AstArena arena, int32_t item);
int32_t flowc_jsgen_emit(AstArena arena, int32_t root, uint8_t* src, uint8_t* out, int32_t out_cap);
JsgenBuf flowc_jsgen_buf_init(uint8_t* out, int32_t cap) {
  return (JsgenBuf){ .out = out, .cap = cap, .len = 0, .err = 0 };
}

void flowc_jsgen_putc(JsgenBuf* w, int32_t c) {
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

void flowc_jsgen_puts(JsgenBuf* w, const char* s) {
  uint8_t* p = (uint8_t*)(s);
  int32_t n = (int32_t)(strlen(s));
  int32_t i = 0;
  while (i < n) {
  flowc_jsgen_putc(w, p[i]);
  i = (i + 1);
}
}

void flowc_jsgen_put_span(JsgenBuf* w, uint8_t* src, int32_t start, int32_t end) {
  int32_t i = start;
  while (i < end) {
  flowc_jsgen_putc(w, src[i]);
  i = (i + 1);
}
}

void flowc_jsgen_put_i32(JsgenBuf* w, int32_t val) {
  int32_t v = val;
  if (v < 0) {
  flowc_jsgen_putc(w, 45);
  v = (0 - v);
}
  if (v == 0) {
  flowc_jsgen_putc(w, 48);
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
  flowc_jsgen_putc(w, digits[i]);
}
}

void flowc_jsgen_emit_expr(JsgenBuf* w, AstArena arena, uint8_t* src, int32_t id);
void flowc_jsgen_emit_stmt(JsgenBuf* w, AstArena arena, uint8_t* src, int32_t id);
void flowc_jsgen_emit_block(JsgenBuf* w, AstArena arena, uint8_t* src, int32_t id);
void flowc_jsgen_emit_binop_op(JsgenBuf* w, int32_t op) {
  if (op == TOK_PLUS) {
  flowc_jsgen_puts(w, " + ");
  return;
}
  if (op == TOK_MINUS) {
  flowc_jsgen_puts(w, " - ");
  return;
}
  if (op == TOK_STAR) {
  flowc_jsgen_puts(w, " * ");
  return;
}
  if (op == TOK_SLASH) {
  flowc_jsgen_puts(w, " / ");
  return;
}
  if (op == TOK_PERCENT) {
  flowc_jsgen_puts(w, " % ");
  return;
}
  if (op == TOK_EQEQ) {
  flowc_jsgen_puts(w, " == ");
  return;
}
  if (op == TOK_NE) {
  flowc_jsgen_puts(w, " != ");
  return;
}
  if (op == TOK_LT) {
  flowc_jsgen_puts(w, " < ");
  return;
}
  if (op == TOK_GT) {
  flowc_jsgen_puts(w, " > ");
  return;
}
  if (op == TOK_LE) {
  flowc_jsgen_puts(w, " <= ");
  return;
}
  if (op == TOK_GE) {
  flowc_jsgen_puts(w, " >= ");
  return;
}
  if (op == TOK_AMPAMP) {
  flowc_jsgen_puts(w, " && ");
  return;
}
  if (op == TOK_BARBAR) {
  flowc_jsgen_puts(w, " || ");
  return;
}
  flowc_jsgen_puts(w, " /*op*/ ");
}

void flowc_jsgen_emit_expr(JsgenBuf* w, AstArena arena, uint8_t* src, int32_t id) {
  if (id == AST_NONE || (w[0]).err != 0) {
  return;
}
  int32_t kind = ((arena).nodes[id]).kind;
  if (kind == AST_INT) {
  flowc_jsgen_put_i32(w, ((arena).nodes[id]).ival);
  return;
}
  if (kind == AST_BOOL) {
  if (((arena).nodes[id]).ival != 0) {
  flowc_jsgen_puts(w, "true");
} else {
  flowc_jsgen_puts(w, "false");
}
  return;
}
  if (kind == AST_IDENT) {
  flowc_jsgen_put_span(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  return;
}
  if (kind == AST_BINOP) {
  flowc_jsgen_putc(w, 40);
  flowc_jsgen_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_jsgen_emit_binop_op(w, ((arena).nodes[id]).ival);
  flowc_jsgen_emit_expr(w, arena, src, ((arena).nodes[id]).b);
  flowc_jsgen_putc(w, 41);
  return;
}
  if (kind == AST_UNARY) {
  flowc_jsgen_putc(w, 40);
  if (((arena).nodes[id]).ival == TOK_MINUS) {
  flowc_jsgen_putc(w, 45);
} else {
  if (((arena).nodes[id]).ival == TOK_BANG) {
  flowc_jsgen_putc(w, 33);
}
}
  flowc_jsgen_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_jsgen_putc(w, 41);
  return;
}
  if (kind == AST_CALL) {
  flowc_jsgen_put_span(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  flowc_jsgen_putc(w, 40);
  int32_t arg = ((arena).nodes[id]).a;
  int32_t first = 1;
  while (arg != AST_NONE) {
  if (first == 0) {
  flowc_jsgen_puts(w, ", ");
}
  first = 0;
  flowc_jsgen_emit_expr(w, arena, src, arg);
  arg = ((arena).nodes[arg]).next;
}
  flowc_jsgen_putc(w, 41);
  return;
}
  flowc_jsgen_puts(w, "0");
}

void flowc_jsgen_emit_block(JsgenBuf* w, AstArena arena, uint8_t* src, int32_t id) {
  if (id == AST_NONE || (w[0]).err != 0) {
  return;
}
  flowc_jsgen_puts(w, "{\n");
  int32_t st = ((arena).nodes[id]).a;
  while (st != AST_NONE) {
  flowc_jsgen_emit_stmt(w, arena, src, st);
  st = ((arena).nodes[st]).next;
}
  flowc_jsgen_puts(w, "}\n");
}

void flowc_jsgen_emit_stmt(JsgenBuf* w, AstArena arena, uint8_t* src, int32_t id) {
  if (id == AST_NONE || (w[0]).err != 0) {
  return;
}
  int32_t kind = ((arena).nodes[id]).kind;
  if (kind == AST_LET) {
  flowc_jsgen_puts(w, "  let ");
  flowc_jsgen_put_span(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  flowc_jsgen_puts(w, " = ");
  flowc_jsgen_emit_expr(w, arena, src, ((arena).nodes[id]).b);
  flowc_jsgen_puts(w, ";\n");
  return;
}
  if (kind == AST_RETURN) {
  if (((arena).nodes[id]).a == AST_NONE) {
  flowc_jsgen_puts(w, "  return;\n");
  return;
}
  flowc_jsgen_puts(w, "  return ");
  flowc_jsgen_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_jsgen_puts(w, ";\n");
  return;
}
  if (kind == AST_IF) {
  flowc_jsgen_puts(w, "  if (");
  flowc_jsgen_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_jsgen_puts(w, ") {\n");
  int32_t then_b = ((arena).nodes[id]).b;
  if (then_b != AST_NONE) {
  int32_t st = ((arena).nodes[then_b]).a;
  while (st != AST_NONE) {
  flowc_jsgen_emit_stmt(w, arena, src, st);
  st = ((arena).nodes[st]).next;
}
}
  if (((arena).nodes[id]).c != AST_NONE) {
  flowc_jsgen_puts(w, "} else {\n");
  int32_t else_b = ((arena).nodes[id]).c;
  int32_t est = ((arena).nodes[else_b]).a;
  while (est != AST_NONE) {
  flowc_jsgen_emit_stmt(w, arena, src, est);
  est = ((arena).nodes[est]).next;
}
  flowc_jsgen_puts(w, "}\n");
} else {
  flowc_jsgen_puts(w, "}\n");
}
  return;
}
  if (kind == AST_WHILE) {
  flowc_jsgen_puts(w, "  while (");
  flowc_jsgen_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_jsgen_puts(w, ") ");
  flowc_jsgen_emit_block(w, arena, src, ((arena).nodes[id]).b);
  return;
}
  if (kind == AST_FOR) {
  flowc_jsgen_puts(w, "  for (let ");
  flowc_jsgen_put_span(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  flowc_jsgen_puts(w, " = ");
  flowc_jsgen_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_jsgen_puts(w, "; ");
  flowc_jsgen_put_span(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  flowc_jsgen_puts(w, " < ");
  flowc_jsgen_emit_expr(w, arena, src, ((arena).nodes[id]).b);
  flowc_jsgen_puts(w, "; ");
  flowc_jsgen_put_span(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  flowc_jsgen_puts(w, "++) ");
  flowc_jsgen_emit_block(w, arena, src, ((arena).nodes[id]).c);
  return;
}
  if (kind == AST_BREAK) {
  flowc_jsgen_puts(w, "  break;\n");
  return;
}
  if (kind == AST_CONTINUE) {
  flowc_jsgen_puts(w, "  continue;\n");
  return;
}
  if (kind == AST_ASSIGN) {
  flowc_jsgen_puts(w, "  ");
  flowc_jsgen_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_jsgen_puts(w, " = ");
  flowc_jsgen_emit_expr(w, arena, src, ((arena).nodes[id]).b);
  flowc_jsgen_puts(w, ";\n");
  return;
}
  if (kind == AST_EXPR_STMT) {
  flowc_jsgen_puts(w, "  ");
  flowc_jsgen_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_jsgen_puts(w, ";\n");
  return;
}
  if (kind == AST_BLOCK) {
  flowc_jsgen_emit_block(w, arena, src, id);
  return;
}
}

void flowc_jsgen_emit_fn(JsgenBuf* w, AstArena arena, uint8_t* src, int32_t id) {
  if (((arena).nodes[id]).c == AST_NONE) {
  return;
}
  flowc_jsgen_puts(w, "function ");
  flowc_jsgen_put_span(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  flowc_jsgen_putc(w, 40);
  int32_t param = ((arena).nodes[id]).a;
  int32_t first = 1;
  while (param != AST_NONE) {
  if (first == 0) {
  flowc_jsgen_puts(w, ", ");
}
  first = 0;
  flowc_jsgen_put_span(w, src, ((arena).nodes[param]).name_start, ((arena).nodes[param]).name_end);
  param = ((arena).nodes[param]).next;
}
  flowc_jsgen_puts(w, ") ");
  flowc_jsgen_emit_block(w, arena, src, ((arena).nodes[id]).c);
  flowc_jsgen_putc(w, 10);
}

int32_t flowc_jsgen_unwrap_fn(AstArena arena, int32_t item) {
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

int32_t flowc_jsgen_emit(AstArena arena, int32_t root, uint8_t* src, uint8_t* out, int32_t out_cap) {
  if (root == AST_NONE || root < 0) {
  return (0 - 1);
}
  if (((arena).nodes[root]).kind != AST_PROGRAM) {
  return (0 - 1);
}
  JsgenBuf w = flowc_jsgen_buf_init(out, out_cap);
  flowc_jsgen_puts((&w), "// Generated by flowc Stage-A\n\n");
  int32_t item = ((arena).nodes[root]).a;
  while (item != AST_NONE) {
  int32_t fn = flowc_jsgen_unwrap_fn(arena, item);
  if (fn != AST_NONE) {
  flowc_jsgen_emit_fn((&w), arena, src, fn);
}
  item = ((arena).nodes[item]).next;
}
  if ((w).err != 0) {
  return (0 - 1);
}
  return (w).len;
}


typedef struct FmtBuf {
  uint8_t* out;
  int32_t cap;
  int32_t len;
  int32_t err;
} FmtBuf;

FmtBuf flowc_fmt_buf_init(uint8_t* out, int32_t cap);
void flowc_fmt_putc(FmtBuf* w, int32_t c);
void flowc_fmt_puts(FmtBuf* w, const char* s);
void flowc_fmt_put_span(FmtBuf* w, uint8_t* src, int32_t start, int32_t end);
void flowc_fmt_put_i32(FmtBuf* w, int32_t val);
void flowc_fmt_indent(FmtBuf* w, int32_t indent);
void flowc_fmt_emit_binop_op(FmtBuf* w, int32_t op);
void flowc_fmt_emit_type(FmtBuf* w, AstArena arena, uint8_t* src, int32_t ty);
void flowc_fmt_emit_expr(FmtBuf* w, AstArena arena, uint8_t* src, int32_t id);
void flowc_fmt_emit_block_body(FmtBuf* w, AstArena arena, uint8_t* src, int32_t block, int32_t indent);
void flowc_fmt_emit_stmt(FmtBuf* w, AstArena arena, uint8_t* src, int32_t id, int32_t indent);
void flowc_fmt_emit_param(FmtBuf* w, AstArena arena, uint8_t* src, int32_t id);
void flowc_fmt_emit_fn(FmtBuf* w, AstArena arena, uint8_t* src, int32_t id, int32_t is_export);
void flowc_fmt_emit_struct(FmtBuf* w, AstArena arena, uint8_t* src, int32_t id, int32_t is_export);
void flowc_fmt_emit_const(FmtBuf* w, AstArena arena, uint8_t* src, int32_t id);
void flowc_fmt_emit_enum(FmtBuf* w, AstArena arena, uint8_t* src, int32_t id, int32_t is_export);
void flowc_fmt_emit_type_alias(FmtBuf* w, AstArena arena, uint8_t* src, int32_t id);
int32_t flowc_fmt_emit(AstArena arena, int32_t root, uint8_t* src, uint8_t* out, int32_t out_cap);
FmtBuf flowc_fmt_buf_init(uint8_t* out, int32_t cap) {
  return (FmtBuf){ .out = out, .cap = cap, .len = 0, .err = 0 };
}

void flowc_fmt_putc(FmtBuf* w, int32_t c) {
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

void flowc_fmt_puts(FmtBuf* w, const char* s) {
  uint8_t* p = (uint8_t*)(s);
  int32_t n = (int32_t)(strlen(s));
  int32_t i = 0;
  while (i < n) {
  flowc_fmt_putc(w, p[i]);
  i = (i + 1);
}
}

void flowc_fmt_put_span(FmtBuf* w, uint8_t* src, int32_t start, int32_t end) {
  int32_t i = start;
  while (i < end) {
  flowc_fmt_putc(w, src[i]);
  i = (i + 1);
}
}

void flowc_fmt_put_i32(FmtBuf* w, int32_t val) {
  int32_t v = val;
  if (v < 0) {
  flowc_fmt_putc(w, 45);
  v = (0 - v);
}
  if (v == 0) {
  flowc_fmt_putc(w, 48);
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
  flowc_fmt_putc(w, digits[i]);
}
}

void flowc_fmt_indent(FmtBuf* w, int32_t indent) {
  int32_t i = 0;
  while (i < indent) {
  flowc_fmt_puts(w, "    ");
  i = (i + 1);
}
}

void flowc_fmt_emit_expr(FmtBuf* w, AstArena arena, uint8_t* src, int32_t id);
void flowc_fmt_emit_stmt(FmtBuf* w, AstArena arena, uint8_t* src, int32_t id, int32_t indent);
void flowc_fmt_emit_type(FmtBuf* w, AstArena arena, uint8_t* src, int32_t ty);
void flowc_fmt_emit_binop_op(FmtBuf* w, int32_t op) {
  if (op == TOK_PLUS) {
  flowc_fmt_puts(w, " + ");
  return;
}
  if (op == TOK_MINUS) {
  flowc_fmt_puts(w, " - ");
  return;
}
  if (op == TOK_STAR) {
  flowc_fmt_puts(w, " * ");
  return;
}
  if (op == TOK_SLASH) {
  flowc_fmt_puts(w, " / ");
  return;
}
  if (op == TOK_PERCENT) {
  flowc_fmt_puts(w, " % ");
  return;
}
  if (op == TOK_EQEQ) {
  flowc_fmt_puts(w, " == ");
  return;
}
  if (op == TOK_NE) {
  flowc_fmt_puts(w, " != ");
  return;
}
  if (op == TOK_LT) {
  flowc_fmt_puts(w, " < ");
  return;
}
  if (op == TOK_GT) {
  flowc_fmt_puts(w, " > ");
  return;
}
  if (op == TOK_LE) {
  flowc_fmt_puts(w, " <= ");
  return;
}
  if (op == TOK_GE) {
  flowc_fmt_puts(w, " >= ");
  return;
}
  if (op == TOK_AMPAMP) {
  flowc_fmt_puts(w, " && ");
  return;
}
  if (op == TOK_BARBAR) {
  flowc_fmt_puts(w, " || ");
  return;
}
  if (op == TOK_IN) {
  flowc_fmt_puts(w, " in ");
  return;
}
  flowc_fmt_puts(w, " ");
}

void flowc_fmt_emit_type(FmtBuf* w, AstArena arena, uint8_t* src, int32_t ty) {
  if (ty == AST_NONE || ((arena).nodes[ty]).kind != AST_TYPE) {
  flowc_fmt_puts(w, "void");
  return;
}
  int32_t ns = ((arena).nodes[ty]).name_start;
  int32_t ne = ((arena).nodes[ty]).name_end;
  int32_t inner = ((arena).nodes[ty]).a;
  if (inner != AST_NONE) {
  flowc_fmt_put_span(w, src, ns, ne);
  flowc_fmt_putc(w, 60);
  flowc_fmt_emit_type(w, arena, src, inner);
  if (((arena).nodes[ty]).ival > 0) {
  flowc_fmt_puts(w, ", ");
  flowc_fmt_put_i32(w, ((arena).nodes[ty]).ival);
}
  flowc_fmt_putc(w, 62);
  return;
}
  flowc_fmt_put_span(w, src, ns, ne);
}

void flowc_fmt_emit_expr(FmtBuf* w, AstArena arena, uint8_t* src, int32_t id) {
  if (id == AST_NONE || (w[0]).err != 0) {
  return;
}
  int32_t kind = ((arena).nodes[id]).kind;
  if (kind == AST_INT) {
  flowc_fmt_put_i32(w, ((arena).nodes[id]).ival);
  return;
}
  if (kind == AST_FLOAT) {
  flowc_fmt_put_span(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  return;
}
  if (kind == AST_BOOL) {
  if (((arena).nodes[id]).ival == 0) {
  flowc_fmt_puts(w, "false");
} else {
  flowc_fmt_puts(w, "true");
}
  return;
}
  if (kind == AST_IDENT) {
  flowc_fmt_put_span(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  return;
}
  if (kind == AST_STRING) {
  flowc_fmt_put_span(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  return;
}
  if (kind == AST_BINOP) {
  flowc_fmt_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_fmt_emit_binop_op(w, ((arena).nodes[id]).ival);
  flowc_fmt_emit_expr(w, arena, src, ((arena).nodes[id]).b);
  return;
}
  if (kind == AST_UNARY) {
  if (((arena).nodes[id]).ival == KW_DBG) {
  flowc_fmt_puts(w, "dbg ");
  flowc_fmt_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  return;
}
  if (((arena).nodes[id]).ival == KW_EXPECT) {
  flowc_fmt_puts(w, "expect ");
  flowc_fmt_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_fmt_putc(w, 10);
  return;
}
  if (((arena).nodes[id]).ival == TOK_MINUS) {
  flowc_fmt_putc(w, 45);
} else {
  if (((arena).nodes[id]).ival == TOK_BANG) {
  flowc_fmt_putc(w, 33);
} else {
  if (((arena).nodes[id]).ival == TOK_AMP) {
  flowc_fmt_putc(w, 38);
}
}
}
  flowc_fmt_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  return;
}
  if (kind == AST_CAST) {
  flowc_fmt_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_fmt_puts(w, " as ");
  flowc_fmt_emit_type(w, arena, src, ((arena).nodes[id]).b);
  return;
}
  if (kind == AST_IF_EXPR) {
  flowc_fmt_puts(w, "if ");
  flowc_fmt_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_fmt_puts(w, " { ");
  flowc_fmt_emit_expr(w, arena, src, ((arena).nodes[id]).b);
  flowc_fmt_puts(w, " } else { ");
  flowc_fmt_emit_expr(w, arena, src, ((arena).nodes[id]).c);
  flowc_fmt_puts(w, " }");
  return;
}
  if (kind == AST_INDEX) {
  flowc_fmt_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_fmt_putc(w, 91);
  flowc_fmt_emit_expr(w, arena, src, ((arena).nodes[id]).b);
  flowc_fmt_putc(w, 93);
  return;
}
  if (kind == AST_CALL) {
  flowc_fmt_put_span(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  flowc_fmt_putc(w, 40);
  int32_t arg = ((arena).nodes[id]).a;
  int32_t first = 1;
  while (arg != AST_NONE) {
  if (first == 0) {
  flowc_fmt_puts(w, ", ");
}
  first = 0;
  flowc_fmt_emit_expr(w, arena, src, arg);
  arg = ((arena).nodes[arg]).next;
}
  flowc_fmt_putc(w, 41);
  return;
}
  if (kind == AST_FIELD_ACCESS) {
  flowc_fmt_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_fmt_putc(w, 46);
  flowc_fmt_put_span(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  return;
}
  if (kind == AST_STRUCT_LIT) {
  flowc_fmt_put_span(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  flowc_fmt_puts(w, " { ");
  int32_t field = ((arena).nodes[id]).a;
  int32_t first = 1;
  while (field != AST_NONE) {
  if (first == 0) {
  flowc_fmt_puts(w, ", ");
}
  first = 0;
  flowc_fmt_put_span(w, src, ((arena).nodes[field]).name_start, ((arena).nodes[field]).name_end);
  flowc_fmt_puts(w, ": ");
  flowc_fmt_emit_expr(w, arena, src, ((arena).nodes[field]).a);
  field = ((arena).nodes[field]).next;
}
  flowc_fmt_puts(w, " }");
  return;
}
  if (kind == AST_ARRAY_LIT) {
  flowc_fmt_putc(w, 91);
  int32_t el = ((arena).nodes[id]).a;
  int32_t first = 1;
  while (el != AST_NONE) {
  if (first == 0) {
  flowc_fmt_puts(w, ", ");
}
  first = 0;
  flowc_fmt_emit_expr(w, arena, src, el);
  el = ((arena).nodes[el]).next;
}
  flowc_fmt_putc(w, 93);
  return;
}
  flowc_fmt_puts(w, "<expr>");
}

void flowc_fmt_emit_block_body(FmtBuf* w, AstArena arena, uint8_t* src, int32_t block, int32_t indent) {
  if (block == AST_NONE) {
  return;
}
  int32_t st = ((arena).nodes[block]).a;
  while (st != AST_NONE) {
  flowc_fmt_emit_stmt(w, arena, src, st, indent);
  st = ((arena).nodes[st]).next;
}
}

void flowc_fmt_emit_stmt(FmtBuf* w, AstArena arena, uint8_t* src, int32_t id, int32_t indent) {
  if (id == AST_NONE || (w[0]).err != 0) {
  return;
}
  int32_t kind = ((arena).nodes[id]).kind;
  if (kind == AST_LET) {
  flowc_fmt_indent(w, indent);
  flowc_fmt_puts(w, "let ");
  if (((arena).nodes[id]).ival == 1) {
  flowc_fmt_puts(w, "mut ");
}
  flowc_fmt_put_span(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  flowc_fmt_puts(w, ": ");
  flowc_fmt_emit_type(w, arena, src, ((arena).nodes[id]).a);
  if (((arena).nodes[id]).b != AST_NONE) {
  flowc_fmt_puts(w, " = ");
  flowc_fmt_emit_expr(w, arena, src, ((arena).nodes[id]).b);
}
  flowc_fmt_putc(w, 10);
  return;
}
  if (kind == AST_RETURN) {
  flowc_fmt_indent(w, indent);
  flowc_fmt_puts(w, "return");
  if (((arena).nodes[id]).a != AST_NONE) {
  flowc_fmt_putc(w, 32);
  flowc_fmt_emit_expr(w, arena, src, ((arena).nodes[id]).a);
}
  flowc_fmt_putc(w, 10);
  return;
}
  if (kind == AST_IF) {
  flowc_fmt_indent(w, indent);
  flowc_fmt_puts(w, "if ");
  flowc_fmt_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_fmt_puts(w, " {\n");
  flowc_fmt_emit_block_body(w, arena, src, ((arena).nodes[id]).b, (indent + 1));
  if (((arena).nodes[id]).c != AST_NONE) {
  flowc_fmt_indent(w, indent);
  flowc_fmt_puts(w, "} else {\n");
  flowc_fmt_emit_block_body(w, arena, src, ((arena).nodes[id]).c, (indent + 1));
}
  flowc_fmt_indent(w, indent);
  flowc_fmt_puts(w, "}\n");
  return;
}
  if (kind == AST_WHILE) {
  flowc_fmt_indent(w, indent);
  flowc_fmt_puts(w, "while ");
  flowc_fmt_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_fmt_puts(w, " {\n");
  flowc_fmt_emit_block_body(w, arena, src, ((arena).nodes[id]).b, (indent + 1));
  flowc_fmt_indent(w, indent);
  flowc_fmt_puts(w, "}\n");
  return;
}
  if (kind == AST_FOR) {
  flowc_fmt_indent(w, indent);
  flowc_fmt_puts(w, "for ");
  flowc_fmt_put_span(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  flowc_fmt_puts(w, " in ");
  flowc_fmt_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_fmt_puts(w, " to ");
  flowc_fmt_emit_expr(w, arena, src, ((arena).nodes[id]).b);
  if (((arena).nodes[id]).ival != AST_NONE && ((arena).nodes[id]).ival != 0) {
  flowc_fmt_puts(w, " step ");
  flowc_fmt_emit_expr(w, arena, src, ((arena).nodes[id]).ival);
}
  flowc_fmt_puts(w, " {\n");
  flowc_fmt_emit_block_body(w, arena, src, ((arena).nodes[id]).c, (indent + 1));
  flowc_fmt_indent(w, indent);
  flowc_fmt_puts(w, "}\n");
  return;
}
  if (kind == AST_BREAK) {
  flowc_fmt_indent(w, indent);
  flowc_fmt_puts(w, "break\n");
  return;
}
  if (kind == AST_CONTINUE) {
  flowc_fmt_indent(w, indent);
  flowc_fmt_puts(w, "continue\n");
  return;
}
  if (kind == AST_DEFER) {
  flowc_fmt_indent(w, indent);
  flowc_fmt_puts(w, "defer ");
  flowc_fmt_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_fmt_putc(w, 10);
  return;
}
  if (kind == AST_ASSIGN) {
  flowc_fmt_indent(w, indent);
  flowc_fmt_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_fmt_puts(w, " = ");
  flowc_fmt_emit_expr(w, arena, src, ((arena).nodes[id]).b);
  flowc_fmt_putc(w, 10);
  return;
}
  if (kind == AST_EXPR_STMT) {
  flowc_fmt_indent(w, indent);
  flowc_fmt_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_fmt_putc(w, 10);
  return;
}
  if (kind == AST_BLOCK) {
  flowc_fmt_indent(w, indent);
  flowc_fmt_puts(w, "{\n");
  flowc_fmt_emit_block_body(w, arena, src, id, (indent + 1));
  flowc_fmt_indent(w, indent);
  flowc_fmt_puts(w, "}\n");
  return;
}
}

void flowc_fmt_emit_param(FmtBuf* w, AstArena arena, uint8_t* src, int32_t id) {
  flowc_fmt_put_span(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  flowc_fmt_puts(w, ": ");
  flowc_fmt_emit_type(w, arena, src, ((arena).nodes[id]).a);
}

void flowc_fmt_emit_fn(FmtBuf* w, AstArena arena, uint8_t* src, int32_t id, int32_t is_export) {
  if (is_export == 1) {
  flowc_fmt_puts(w, "export ");
}
  flowc_fmt_puts(w, "function ");
  flowc_fmt_put_span(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  flowc_fmt_putc(w, 40);
  int32_t param = ((arena).nodes[id]).a;
  int32_t first = 1;
  while (param != AST_NONE) {
  if (first == 0) {
  flowc_fmt_puts(w, ", ");
}
  first = 0;
  flowc_fmt_emit_param(w, arena, src, param);
  param = ((arena).nodes[param]).next;
}
  flowc_fmt_putc(w, 41);
  int32_t ret_ty = ((arena).nodes[id]).b;
  if (ret_ty != AST_NONE) {
  flowc_fmt_puts(w, " -> ");
  flowc_fmt_emit_type(w, arena, src, ret_ty);
}
  if (((arena).nodes[id]).c == AST_NONE) {
  flowc_fmt_putc(w, 10);
  return;
}
  flowc_fmt_puts(w, " {\n");
  flowc_fmt_emit_block_body(w, arena, src, ((arena).nodes[id]).c, 1);
  flowc_fmt_puts(w, "}\n");
}

void flowc_fmt_emit_struct(FmtBuf* w, AstArena arena, uint8_t* src, int32_t id, int32_t is_export) {
  if (is_export == 1) {
  flowc_fmt_puts(w, "export ");
}
  flowc_fmt_puts(w, "struct ");
  flowc_fmt_put_span(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  flowc_fmt_puts(w, " {\n");
  int32_t field = ((arena).nodes[id]).a;
  while (field != AST_NONE) {
  flowc_fmt_indent(w, 1);
  flowc_fmt_put_span(w, src, ((arena).nodes[field]).name_start, ((arena).nodes[field]).name_end);
  flowc_fmt_puts(w, ": ");
  flowc_fmt_emit_type(w, arena, src, ((arena).nodes[field]).a);
  flowc_fmt_putc(w, 10);
  field = ((arena).nodes[field]).next;
}
  flowc_fmt_puts(w, "}\n");
}

void flowc_fmt_emit_const(FmtBuf* w, AstArena arena, uint8_t* src, int32_t id) {
  if (((arena).nodes[id]).ival == 1) {
  flowc_fmt_puts(w, "export ");
}
  flowc_fmt_puts(w, "const ");
  flowc_fmt_put_span(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  flowc_fmt_puts(w, ": ");
  flowc_fmt_emit_type(w, arena, src, ((arena).nodes[id]).a);
  flowc_fmt_puts(w, " = ");
  flowc_fmt_emit_expr(w, arena, src, ((arena).nodes[id]).b);
  flowc_fmt_putc(w, 10);
}

void flowc_fmt_emit_enum(FmtBuf* w, AstArena arena, uint8_t* src, int32_t id, int32_t is_export) {
  if (is_export == 1) {
  flowc_fmt_puts(w, "export ");
}
  flowc_fmt_puts(w, "enum ");
  flowc_fmt_put_span(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  flowc_fmt_puts(w, " {\n");
  int32_t var = ((arena).nodes[id]).a;
  while (var != AST_NONE) {
  flowc_fmt_indent(w, 1);
  flowc_fmt_put_span(w, src, ((arena).nodes[var]).name_start, ((arena).nodes[var]).name_end);
  flowc_fmt_putc(w, 10);
  var = ((arena).nodes[var]).next;
}
  flowc_fmt_puts(w, "}\n");
}

void flowc_fmt_emit_type_alias(FmtBuf* w, AstArena arena, uint8_t* src, int32_t id) {
  flowc_fmt_puts(w, "type ");
  flowc_fmt_put_span(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  flowc_fmt_puts(w, " = ");
  flowc_fmt_emit_type(w, arena, src, ((arena).nodes[id]).a);
  flowc_fmt_putc(w, 10);
}

int32_t flowc_fmt_emit(AstArena arena, int32_t root, uint8_t* src, uint8_t* out, int32_t out_cap) {
  if (root == AST_NONE || root < 0) {
  return (0 - 1);
}
  if (((arena).nodes[root]).kind != AST_PROGRAM) {
  return (0 - 1);
}
  FmtBuf w = flowc_fmt_buf_init(out, out_cap);
  int32_t item = ((arena).nodes[root]).a;
  int32_t first_item = 1;
  while (item != AST_NONE) {
  int32_t kind = ((arena).nodes[item]).kind;
  int32_t wrote = 0;
  if (kind == AST_STRUCT) {
  if (first_item == 0) {
  flowc_fmt_putc((&w), 10);
}
  flowc_fmt_emit_struct((&w), arena, src, item, 0);
  wrote = 1;
}
  if (kind == AST_FN) {
  if (first_item == 0) {
  flowc_fmt_putc((&w), 10);
}
  flowc_fmt_emit_fn((&w), arena, src, item, 0);
  wrote = 1;
}
  if (kind == AST_CONST) {
  if (first_item == 0) {
  flowc_fmt_putc((&w), 10);
}
  flowc_fmt_emit_const((&w), arena, src, item);
  wrote = 1;
}
  if (kind == AST_ENUM) {
  if (first_item == 0) {
  flowc_fmt_putc((&w), 10);
}
  flowc_fmt_emit_enum((&w), arena, src, item, 0);
  wrote = 1;
}
  if (kind == AST_TYPE_ALIAS) {
  if (first_item == 0) {
  flowc_fmt_putc((&w), 10);
}
  flowc_fmt_emit_type_alias((&w), arena, src, item);
  wrote = 1;
}
  if (kind == AST_EXPORT) {
  int32_t inner = ((arena).nodes[item]).a;
  if (inner != AST_NONE) {
  int32_t ik = ((arena).nodes[inner]).kind;
  if (ik == AST_STRUCT) {
  if (first_item == 0) {
  flowc_fmt_putc((&w), 10);
}
  flowc_fmt_emit_struct((&w), arena, src, inner, 1);
  wrote = 1;
}
  if (ik == AST_FN) {
  if (first_item == 0) {
  flowc_fmt_putc((&w), 10);
}
  flowc_fmt_emit_fn((&w), arena, src, inner, 1);
  wrote = 1;
}
  if (ik == AST_ENUM) {
  if (first_item == 0) {
  flowc_fmt_putc((&w), 10);
}
  flowc_fmt_emit_enum((&w), arena, src, inner, 1);
  wrote = 1;
}
}
}
  if (wrote == 1) {
  first_item = 0;
}
  item = ((arena).nodes[item]).next;
}
  if ((w).err != 0) {
  return (0 - 1);
}
  return (w).len;
}


int32_t flowc_wasm_gen_compile(const char* in_path, const char* out_path, const char* optimize);
int32_t flowc_wasm_gen_compile(const char* in_path, const char* out_path, const char* optimize) {
  uint8_t* cmd = (uint8_t*)(malloc(4096));
  if (cmd == NULL) {
  return 1;
}
  int32_t _s1 = sprintf(cmd, (uint8_t*)("PYTHONPATH=src python3 -m flow.transpiler %s --wasm32 --llvm -o build/flow_wasm_tmp.ll"), (uint8_t*)(in_path), (uint8_t*)(""), (uint8_t*)(""));
  int32_t rc1 = flowc_io_system((const char*)(cmd));
  if (rc1 != 0) {
  puts("error: Flow -> LLVM IR lowering failed");
  free(cmd);
  return 1;
}
  int32_t _s2 = sprintf(cmd, (uint8_t*)("clang --target=wasm32-unknown-unknown -x ir -O%s -nostdlib build/flow_wasm_tmp.ll -Wl,--no-entry -Wl,--export-all -Wl,--allow-undefined -Wl,--export-memory -o %s"), (uint8_t*)(optimize), (uint8_t*)(out_path), (uint8_t*)(""));
  int32_t rc2 = flowc_io_system((const char*)(cmd));
  if (rc2 != 0) {
  puts("error: LLVM IR -> WebAssembly compilation failed");
  free(cmd);
  return 1;
}
  free(cmd);
  return 0;
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

int32_t flowc_tc_span_eq(uint8_t* src, int32_t a0, int32_t a1, int32_t b0, int32_t b1);
int32_t flowc_tc_span_eq2(uint8_t* src_a, int32_t a0, int32_t a1, uint8_t* src_b, int32_t b0, int32_t b1);
uint8_t* flowc_tc_bind_src(TcCtx ctx, int32_t i);
int32_t flowc_tc_name_eq(TcCtx ctx, int32_t start, int32_t end, int32_t i);
int32_t flowc_tc_span_is(uint8_t* src, int32_t start, int32_t end, const char* lit);
void flowc_tc_err(TcCtx* ctx);
void flowc_tc_note(TcCtx* ctx, const char* label, int32_t start, int32_t end);
void flowc_tc_push_mark(TcCtx* ctx);
void flowc_tc_pop_mark(TcCtx* ctx);
void flowc_tc_bind(TcCtx* ctx, int32_t start, int32_t end, int32_t kind, int32_t arity);
int32_t flowc_tc_lookup(TcCtx ctx, int32_t start, int32_t end);
int32_t flowc_tc_lookup_local(TcCtx ctx, int32_t start, int32_t end);
int32_t flowc_tc_lookup_val_type(TcCtx ctx, int32_t start, int32_t end);
void flowc_tc_bind_value(TcCtx* ctx, int32_t start, int32_t end, int32_t ty);
int32_t flowc_tc_find_struct(AstArena arena, uint8_t* src, int32_t ty);
int32_t flowc_tc_find_struct_by_name(AstArena arena, uint8_t* src, int32_t ns, int32_t ne);
int32_t flowc_tc_struct_has_field(AstArena arena, uint8_t* src, int32_t st, int32_t fs, int32_t fe);
int32_t flowc_tc_lookup_fn(TcCtx ctx, int32_t start, int32_t end);
int32_t flowc_tc_lookup_fn_arity(TcCtx ctx, int32_t start, int32_t end);
int32_t flowc_tc_unwrap_fn(AstArena arena, int32_t item);
int32_t flowc_tc_params_eq(AstArena arena, uint8_t* src, int32_t fn_a, int32_t fn_b);
int32_t flowc_tc_is_i32_type(AstArena arena, uint8_t* src, int32_t ty);
int32_t flowc_tc_is_void_ret(AstArena arena, uint8_t* src, int32_t ty);
int32_t flowc_tc_obvious_non_i32(AstArena arena, int32_t id);
void flowc_tc_check_expr(TcCtx* ctx, AstArena arena, int32_t id);
void flowc_tc_check_block(TcCtx* ctx, AstArena arena, int32_t id);
void flowc_tc_check_stmt(TcCtx* ctx, AstArena arena, int32_t id);
void flowc_tc_collect_globals(TcCtx* ctx, AstArena arena, int32_t root);
void flowc_tc_check_fns(TcCtx* ctx, AstArena arena, int32_t root);
void flowc_tc_seed_bind(TcCtx* ctx, uint8_t* dep_src, int32_t start, int32_t end, int32_t kind, int32_t arity);
void flowc_tc_seed_bind_enum_variant(TcCtx* ctx, uint8_t* src, int32_t ens, int32_t ene, int32_t vns, int32_t vne);
void flowc_tc_seed_export(TcCtx* ctx, AstArena dep_arena, int32_t dep_root, uint8_t* dep_src);
TcCtx flowc_tc_init(uint8_t* src);
void flowc_tc_free(TcCtx* ctx);
void flowc_tc_reset_module(TcCtx* ctx, uint8_t* src);
void flowc_tc_set_path(TcCtx* ctx, const char* path);
int32_t flowc_tc_check_program(TcCtx* ctx, AstArena arena, int32_t root);
int32_t flowc_typecheck_ex(AstArena arena, int32_t root, uint8_t* src, const char* path);
int32_t flowc_typecheck(AstArena arena, int32_t root, uint8_t* src);
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
  if (flowc_tc_span_is((ctx).src, start, end, "sort") == 1) {
  return 1;
}
  if (flowc_tc_span_is((ctx).src, start, end, "sortBy") == 1) {
  return 1;
}
  if (flowc_tc_span_is((ctx).src, start, end, "len") == 1) {
  return 1;
}
  if (flowc_tc_span_is((ctx).src, start, end, "push") == 1) {
  return 1;
}
  if (flowc_tc_span_is((ctx).src, start, end, "pop") == 1) {
  return 1;
}
  if (flowc_tc_span_is((ctx).src, start, end, "map") == 1) {
  return 1;
}
  if (flowc_tc_span_is((ctx).src, start, end, "filter") == 1) {
  return 1;
}
  if (flowc_tc_span_is((ctx).src, start, end, "reduce") == 1) {
  return 1;
}
  if (flowc_tc_span_is((ctx).src, start, end, "fold") == 1) {
  return 1;
}
  if (flowc_tc_span_is((ctx).src, start, end, "reverse") == 1) {
  return 1;
}
  if (flowc_tc_span_is((ctx).src, start, end, "keys") == 1) {
  return 1;
}
  if (flowc_tc_span_is((ctx).src, start, end, "values") == 1) {
  return 1;
}
  if (flowc_tc_span_is((ctx).src, start, end, "assert") == 1) {
  return 1;
}
  if (flowc_tc_span_is((ctx).src, start, end, "dbg") == 1) {
  return 1;
}
  if (flowc_tc_span_is((ctx).src, start, end, "find") == 1) {
  return 1;
}
  if (flowc_tc_span_is((ctx).src, start, end, "channel_new") == 1) {
  return 1;
}
  if (flowc_tc_span_is((ctx).src, start, end, "channel_send") == 1) {
  return 1;
}
  if (flowc_tc_span_is((ctx).src, start, end, "channel_recv") == 1) {
  return 1;
}
  if (flowc_tc_span_is((ctx).src, start, end, "channel_try_send") == 1) {
  return 1;
}
  if (flowc_tc_span_is((ctx).src, start, end, "channel_try_recv") == 1) {
  return 1;
}
  if (flowc_tc_span_is((ctx).src, start, end, "channel_close") == 1) {
  return 1;
}
  if (flowc_tc_span_is((ctx).src, start, end, "channel_destroy") == 1) {
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
  if (flowc_tc_span_is((ctx).src, start, end, "printf") == 1) {
  return (-1);
}
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

int32_t flowc_tc_params_eq(AstArena arena, uint8_t* src, int32_t fn_a, int32_t fn_b) {
  int32_t pa = ((arena).nodes[fn_a]).a;
  int32_t pb = ((arena).nodes[fn_b]).a;
  while (pa != AST_NONE && pb != AST_NONE) {
  int32_t ta = ((arena).nodes[pa]).a;
  int32_t tb = ((arena).nodes[pb]).a;
  if (ta == AST_NONE && tb == AST_NONE) {
  int32_t unused = 0;
} else {
  if (ta == AST_NONE || tb == AST_NONE) {
  return 0;
} else {
  if (flowc_tc_span_eq(src, ((arena).nodes[ta]).name_start, ((arena).nodes[ta]).name_end, ((arena).nodes[tb]).name_start, ((arena).nodes[tb]).name_end) == 0) {
  return 0;
}
}
}
  pa = ((arena).nodes[pa]).next;
  pb = ((arena).nodes[pb]).next;
}
  if (pa != AST_NONE || pb != AST_NONE) {
  return 0;
}
  return 1;
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
  if (kind == AST_FN) {
  flowc_tc_push_mark(ctx);
  int32_t param = ((arena).nodes[id]).a;
  while (param != AST_NONE) {
  flowc_tc_bind(ctx, ((arena).nodes[param]).name_start, ((arena).nodes[param]).name_end, 0, (-1));
  param = ((arena).nodes[param]).next;
}
  flowc_tc_check_block(ctx, arena, ((arena).nodes[id]).c);
  flowc_tc_pop_mark(ctx);
  return;
}
  if (kind == AST_IDENT) {
  int32_t ns = ((arena).nodes[id]).name_start;
  int32_t ne = ((arena).nodes[id]).name_end;
  if (flowc_tc_span_is((ctx[0]).src, ns, ne, "descending") == 1) {
  return;
}
  if (flowc_tc_span_is((ctx[0]).src, ns, ne, "ascending") == 1) {
  return;
}
  if (flowc_tc_span_is((ctx[0]).src, ns, ne, "unique") == 1) {
  return;
}
  if (flowc_tc_span_is((ctx[0]).src, ns, ne, "adaptive") == 1) {
  return;
}
  if (flowc_tc_span_is((ctx[0]).src, ns, ne, "general") == 1) {
  return;
}
  if (flowc_tc_span_is((ctx[0]).src, ns, ne, "asc") == 1) {
  return;
}
  if (flowc_tc_span_is((ctx[0]).src, ns, ne, "desc") == 1) {
  return;
}
  if (flowc_tc_lookup(ctx[0], ns, ne) == 0) {
  if ((ctx[0]).has_extern == 0) {
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
  int32_t is_gpu_builtin = 0;
  if (flowc_tc_span_is((ctx[0]).src, ns, ne, "gpu_thread_id") == 1) {
  is_gpu_builtin = 1;
} else {
  if (flowc_tc_span_is((ctx[0]).src, ns, ne, "gpu_thread_id_x") == 1) {
  is_gpu_builtin = 1;
} else {
  if (flowc_tc_span_is((ctx[0]).src, ns, ne, "gpu_thread_id_y") == 1) {
  is_gpu_builtin = 1;
} else {
  if (flowc_tc_span_is((ctx[0]).src, ns, ne, "gpu_thread_id_z") == 1) {
  is_gpu_builtin = 1;
} else {
  if (flowc_tc_span_is((ctx[0]).src, ns, ne, "gpu_block_id") == 1) {
  is_gpu_builtin = 1;
} else {
  if (flowc_tc_span_is((ctx[0]).src, ns, ne, "gpu_block_id_x") == 1) {
  is_gpu_builtin = 1;
} else {
  if (flowc_tc_span_is((ctx[0]).src, ns, ne, "gpu_block_id_y") == 1) {
  is_gpu_builtin = 1;
} else {
  if (flowc_tc_span_is((ctx[0]).src, ns, ne, "gpu_block_id_z") == 1) {
  is_gpu_builtin = 1;
} else {
  if (flowc_tc_span_is((ctx[0]).src, ns, ne, "gpu_local_id") == 1) {
  is_gpu_builtin = 1;
} else {
  if (flowc_tc_span_is((ctx[0]).src, ns, ne, "gpu_local_id_x") == 1) {
  is_gpu_builtin = 1;
} else {
  if (flowc_tc_span_is((ctx[0]).src, ns, ne, "gpu_block_size") == 1) {
  is_gpu_builtin = 1;
} else {
  if (flowc_tc_span_is((ctx[0]).src, ns, ne, "gpu_sync") == 1) {
  is_gpu_builtin = 1;
} else {
  if (flowc_tc_span_is((ctx[0]).src, ns, ne, "gpu_barrier") == 1) {
  is_gpu_builtin = 1;
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
}
}
}
  if (flowc_tc_lookup(ctx[0], ns, ne) == 0 && is_gpu_builtin == 0) {
  if ((ctx[0]).has_extern == 0) {
  flowc_tc_note(ctx, "flowc tc: unbound call", ns, ne);
  flowc_tc_err(ctx);
}
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
  int32_t arm = ((arena).nodes[id]).b;
  while (arm != AST_NONE) {
  if ((((arena).nodes[arm]).ival == 1 || ((arena).nodes[arm]).ival == 2) && ((arena).nodes[arm]).next != AST_NONE) {
  flowc_tc_note(ctx, "flowc tc: catch-all match arm must be last", ((arena).nodes[arm]).start, ((arena).nodes[arm]).end);
  flowc_tc_err(ctx);
}
  flowc_tc_push_mark(ctx);
  if (((arena).nodes[arm]).ival == 2) {
  flowc_tc_bind(ctx, ((arena).nodes[arm]).name_start, ((arena).nodes[arm]).name_end, 0, (-1));
}
  if (((arena).nodes[arm]).ival == 5) {
  int32_t bind = ((arena).nodes[arm]).a;
  while (bind != AST_NONE) {
  flowc_tc_bind(ctx, ((arena).nodes[bind]).name_start, ((arena).nodes[bind]).name_end, 0, (-1));
  bind = ((arena).nodes[bind]).next;
}
}
  if (((arena).nodes[arm]).ival == 6) {
  int32_t elem = ((arena).nodes[arm]).a;
  while (elem != AST_NONE) {
  if (((arena).nodes[elem]).kind == AST_IDENT) {
  flowc_tc_bind(ctx, ((arena).nodes[elem]).name_start, ((arena).nodes[elem]).name_end, 0, (-1));
}
  elem = ((arena).nodes[elem]).next;
}
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
  if (kind == AST_DEFER) {
  flowc_tc_check_expr(ctx, arena, ((arena).nodes[id]).a);
  return;
}
  if (kind == AST_IF_EXPR) {
  flowc_tc_check_expr(ctx, arena, ((arena).nodes[id]).a);
  flowc_tc_check_expr(ctx, arena, ((arena).nodes[id]).b);
  flowc_tc_check_expr(ctx, arena, ((arena).nodes[id]).c);
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
  if (kind == AST_ENUM) {
  int32_t ens = ((arena).nodes[item]).name_start;
  int32_t ene = ((arena).nodes[item]).name_end;
  int32_t var = ((arena).nodes[item]).a;
  while (var != AST_NONE) {
  flowc_tc_seed_bind_enum_variant(ctx, (ctx[0]).src, ens, ene, ((arena).nodes[var]).name_start, ((arena).nodes[var]).name_end);
  var = ((arena).nodes[var]).next;
}
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
  if (fn != AST_NONE) {
  int32_t ns = ((arena).nodes[fn]).name_start;
  int32_t ne = ((arena).nodes[fn]).name_end;
  int32_t body = ((arena).nodes[fn]).c;
  int32_t arity = flowc_ast_chain_len(arena, ((arena).nodes[fn]).a);
  if (body != AST_NONE && ((arena).nodes[fn]).ival == 0) {
  int32_t prev = ((arena).nodes[root]).a;
  while (prev != item) {
  int32_t pfn = flowc_tc_unwrap_fn(arena, prev);
  if (pfn != AST_NONE && ((arena).nodes[pfn]).c != AST_NONE) {
  if (flowc_tc_span_eq((ctx[0]).src, ns, ne, ((arena).nodes[pfn]).name_start, ((arena).nodes[pfn]).name_end) == 1) {
  int32_t params_same = flowc_tc_params_eq(arena, (ctx[0]).src, fn, pfn);
  if (params_same == 1) {
  flowc_tc_note(ctx, "flowc tc: duplicate function with same signature", ns, ne);
  flowc_tc_err(ctx);
}
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

void flowc_tc_seed_bind_enum_variant(TcCtx* ctx, uint8_t* src, int32_t ens, int32_t ene, int32_t vns, int32_t vne) {
  if ((ctx[0]).seed_buf == NULL) {
  flowc_tc_err(ctx);
  return;
}
  int32_t en_len = (ene - ens);
  int32_t vn_len = (vne - vns);
  int32_t total = ((en_len + 1) + vn_len);
  if (((ctx[0]).seed_len + total) > (ctx[0]).seed_cap) {
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
  while (i < en_len) {
  (ctx[0]).seed_buf[(off + i)] = src[(ens + i)];
  i = (i + 1);
}
  (ctx[0]).seed_buf[(off + en_len)] = 95;
  i = 0;
  while (i < vn_len) {
  (ctx[0]).seed_buf[(((off + en_len) + 1) + i)] = src[(vns + i)];
  i = (i + 1);
}
  (ctx[0]).seed_len = (off + total);
  int32_t bi = (ctx[0]).nlen;
  (ctx[0]).ns[bi] = off;
  (ctx[0]).ne[bi] = (off + total);
  (ctx[0]).nk[bi] = 0;
  (ctx[0]).na[bi] = (-1);
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
int32_t flowc_resolve_copy_cstr(const char* s, uint8_t* dst, int32_t cap);
int32_t flowc_resolve_cstr_eq(uint8_t* a, uint8_t* b);
int32_t flowc_resolve_find_path(uint8_t* store, int32_t n, int32_t row_cap, uint8_t* path);
int32_t flowc_resolve_sibling_path(uint8_t* import_span_src, int32_t name_start, int32_t name_end, const char* search_dir, uint8_t* out_path, int32_t out_path_cap);
int32_t flowc_resolve_dotted_path(uint8_t* import_span_src, int32_t name_start, int32_t name_end, const char* search_dir, uint8_t* out_path, int32_t out_path_cap);
int32_t flowc_resolve_dirname(const char* path, uint8_t* out, int32_t out_cap);
int32_t flowc_resolve_append_path(uint8_t* store, int32_t n, const char* path);
int32_t flowc_resolve_gather(const char* entry_path, const char* search_dir, uint8_t* path_store);
int32_t flowc_resolve_deps_ready(const char* path, const char* search_dir, uint8_t* all_store, int32_t all_n, uint8_t* out_store, int32_t out_n, uint8_t* src, uint8_t* imp_path);
int32_t flowc_resolve_topo(uint8_t* all_store, int32_t all_n, const char* search_dir, uint8_t* out_store);
int32_t flowc_resolve_emit_one(const char* path, uint8_t* out, int32_t out_cap, int32_t flags, uint8_t* sigs, int32_t sigcap, int32_t* siglen);
int32_t flowc_bundle_typecheck(const char* entry_path, const char* search_dir);
int32_t flowc_bundle_emit(const char* entry_path, const char* search_dir, uint8_t* out, int32_t out_cap);
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
  int32_t namelen = (e - s);
  int32_t total = (11 + namelen);
  if ((total + 1) > out_path_cap) {
  return (0 - 1);
}
  out_path[0] = 108;
  out_path[1] = 105;
  out_path[2] = 98;
  out_path[3] = 47;
  out_path[4] = 115;
  out_path[5] = 116;
  out_path[6] = 100;
  out_path[7] = 108;
  out_path[8] = 105;
  out_path[9] = 98;
  out_path[10] = 47;
  int32_t ni = 0;
  while (ni < namelen) {
  out_path[(11 + ni)] = import_span_src[(s + ni)];
  ni = (ni + 1);
}
  out_path[total] = 0;
  if (flowc_io_exists((const char*)(out_path)) == 1) {
  return total;
}
  return (0 - 1);
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
  if (flowc_io_exists((const char*)(out_path)) == 1) {
  return nabs;
}
  return (0 - 1);
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
  if (flowc_io_exists((const char*)(out_path)) == 1) {
  return o;
}
  return (0 - 1);
}

int32_t flowc_resolve_dotted_path(uint8_t* import_span_src, int32_t name_start, int32_t name_end, const char* search_dir, uint8_t* out_path, int32_t out_path_cap) {
  int32_t s = name_start;
  int32_t e = name_end;
  if (e <= s || out_path_cap <= 1) {
  return (0 - 1);
}
  int32_t dlen = (int32_t)(strlen(search_dir));
  int32_t namelen = (e - s);
  int32_t total = (((dlen + 1) + namelen) + 5);
  if ((total + 1) > out_path_cap) {
  return (0 - 1);
}
  int32_t o = 0;
  int32_t di = 0;
  while (di < dlen) {
  out_path[o] = (uint8_t*)(search_dir)[di];
  o = (o + 1);
  di = (di + 1);
}
  out_path[o] = 47;
  o = (o + 1);
  int32_t ni = 0;
  while (ni < namelen) {
  uint8_t c = import_span_src[(s + ni)];
  if (c == 46) {
  out_path[o] = 47;
} else {
  out_path[o] = c;
}
  o = (o + 1);
  ni = (ni + 1);
}
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
  out_path[o] = 0;
  if (flowc_io_exists((const char*)(out_path)) == 1) {
  return o;
}
  int32_t lib_total = ((4 + namelen) + 5);
  if ((lib_total + 1) > out_path_cap) {
  return (0 - 1);
}
  o = 0;
  out_path[o] = 108;
  o = (o + 1);
  out_path[o] = 105;
  o = (o + 1);
  out_path[o] = 98;
  o = (o + 1);
  out_path[o] = 47;
  o = (o + 1);
  ni = 0;
  while (ni < namelen) {
  uint8_t c = import_span_src[(s + ni)];
  if (c == 46) {
  out_path[o] = 47;
} else {
  out_path[o] = c;
}
  o = (o + 1);
  ni = (ni + 1);
}
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
  out_path[o] = 0;
  if (flowc_io_exists((const char*)(out_path)) == 1) {
  return o;
}
  return (0 - 1);
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
  uint8_t* mod_dir = (uint8_t*)(malloc((int64_t)(FLOWC_RESOLVE_PATH_CAP)));
  if (src == NULL || imp_path == NULL || mod_dir == NULL) {
  if (src != NULL) {
  free(src);
}
  if (imp_path != NULL) {
  free(imp_path);
}
  if (mod_dir != NULL) {
  free(mod_dir);
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
  free(mod_dir);
  free(imp_path);
  free(src);
  return (0 - 1);
}
  src[nsrc] = 0;
  int32_t mod_dlen = flowc_resolve_dirname(mpath, mod_dir, FLOWC_RESOLVE_PATH_CAP);
  const char* mod_search = search_dir;
  if (mod_dlen > 0) {
  mod_search = (const char*)(mod_dir);
}
  Parser p = flowc_parser_new(src, nsrc, FLOWC_RESOLVE_AST_CAP);
  int32_t root = flowc_parse_program((&p));
  if (root < 0 || (p).err != 0) {
  puts("flowc gather: parse failed");
  printf("flowc gather: nsrc=%d\n", nsrc);
  flowc_parser_free(p);
  free(mod_dir);
  free(imp_path);
  free(src);
  return (0 - 1);
}
  int32_t ii = 0;
  while (ii < ((p).arena).len) {
  if ((((p).arena).nodes[ii]).kind == AST_IMPORT) {
  int32_t form = (((p).arena).nodes[ii]).ival;
  if (form == 1 || form == 2) {
  int32_t plen = flowc_resolve_sibling_path(src, (((p).arena).nodes[ii]).name_start, (((p).arena).nodes[ii]).name_end, mod_search, imp_path, FLOWC_RESOLVE_PATH_CAP);
  if (plen < 0 && mod_search != search_dir) {
  plen = flowc_resolve_sibling_path(src, (((p).arena).nodes[ii]).name_start, (((p).arena).nodes[ii]).name_end, search_dir, imp_path, FLOWC_RESOLVE_PATH_CAP);
}
  if (plen < 0) {
  flowc_parser_free(p);
  free(mod_dir);
  free(imp_path);
  free(src);
  return (0 - 1);
}
  const char* dep = imp_path;
  int32_t n2 = flowc_resolve_append_path(path_store, n, dep);
  if (n2 < 0) {
  flowc_parser_free(p);
  free(mod_dir);
  free(imp_path);
  free(src);
  return (0 - 1);
}
  n = n2;
}
  if (form == 0) {
  int32_t plen = flowc_resolve_dotted_path(src, (((p).arena).nodes[ii]).name_start, (((p).arena).nodes[ii]).name_end, search_dir, imp_path, FLOWC_RESOLVE_PATH_CAP);
  if (plen < 0) {
  flowc_parser_free(p);
  free(mod_dir);
  free(imp_path);
  free(src);
  return (0 - 1);
}
  const char* dep = imp_path;
  int32_t n2 = flowc_resolve_append_path(path_store, n, dep);
  if (n2 < 0) {
  flowc_parser_free(p);
  free(mod_dir);
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
  free(mod_dir);
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
  uint8_t mod_dir_buf[1024] = { 0 };
  int32_t mod_dlen = flowc_resolve_dirname(path, (uint8_t*)((&mod_dir_buf[0])), 1024);
  const char* mod_search = search_dir;
  if (mod_dlen > 0) {
  mod_search = (const char*)((&mod_dir_buf[0]));
}
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
  int32_t plen = flowc_resolve_sibling_path(src, (((p).arena).nodes[ii]).name_start, (((p).arena).nodes[ii]).name_end, mod_search, imp_path, FLOWC_RESOLVE_PATH_CAP);
  if (plen < 0 && mod_search != search_dir) {
  plen = flowc_resolve_sibling_path(src, (((p).arena).nodes[ii]).name_start, (((p).arena).nodes[ii]).name_end, search_dir, imp_path, FLOWC_RESOLVE_PATH_CAP);
}
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
  if (form == 0) {
  int32_t plen = flowc_resolve_dotted_path(src, (((p).arena).nodes[ii]).name_start, (((p).arena).nodes[ii]).name_end, search_dir, imp_path, FLOWC_RESOLVE_PATH_CAP);
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


int32_t flowc_streq_span(uint8_t* text, int32_t start, int32_t end, uint8_t* lit);
int32_t flowc_streq(const char* s, uint8_t* lit);
int32_t flowc_strlen(const char* s);
int32_t flowc_strncpy_span(uint8_t* dst, uint8_t* src, int32_t start, int32_t end);
const char* flowc_strdup(const char* s);
int32_t flowc_span_starts_with(uint8_t* text, int32_t start, int32_t end, uint8_t* lit);
int32_t flowc_span_find_last(uint8_t* text, int32_t start, int32_t end, int32_t ch);
int32_t flowc_span_find_first(uint8_t* text, int32_t start, int32_t end, int32_t ch);
int32_t flowc_path_basename_start(uint8_t* text, int32_t start, int32_t end);
int32_t flowc_span_ends_with(uint8_t* text, int32_t start, int32_t end, uint8_t* lit);
int32_t flowc_streq_span(uint8_t* text, int32_t start, int32_t end, uint8_t* lit) {
  int32_t lit_len = (int32_t)(strlen(lit));
  if ((end - start) != lit_len) {
  return 0;
}
  int32_t i = 0;
  while (i < lit_len) {
  if (text[(start + i)] != lit[i]) {
  return 0;
}
  i = (i + 1);
}
  return 1;
}

int32_t flowc_streq(const char* s, uint8_t* lit) {
  uint8_t* sp = (uint8_t*)((uint8_t*)(s));
  if (strcmp(sp, lit) == 0) {
  return 1;
}
  return 0;
}

int32_t flowc_strlen(const char* s) {
  uint8_t* sp = (uint8_t*)((uint8_t*)(s));
  return (int32_t)(strlen(sp));
}

int32_t flowc_strncpy_span(uint8_t* dst, uint8_t* src, int32_t start, int32_t end) {
  int32_t n = (end - start);
  if (n <= 0) {
  return 0;
}
  int32_t i = 0;
  while (i < n) {
  dst[i] = src[(start + i)];
  i = (i + 1);
}
  return n;
}

const char* flowc_strdup(const char* s) {
  uint8_t* sp = (uint8_t*)((uint8_t*)(s));
  int32_t len = (int32_t)(strlen(sp));
  uint8_t* buf = (uint8_t*)(malloc((len + 1)));
  if (buf == NULL) {
  return (const char*)("");
}
  if (len > 0) {
  uint8_t* _m = (uint8_t*)(memcpy(buf, sp, (int64_t)(len)));
}
  buf[len] = 0;
  return (const char*)(buf);
}

int32_t flowc_span_starts_with(uint8_t* text, int32_t start, int32_t end, uint8_t* lit) {
  int32_t lit_len = (int32_t)(strlen(lit));
  if ((end - start) < lit_len) {
  return 0;
}
  int32_t i = 0;
  while (i < lit_len) {
  if (text[(start + i)] != lit[i]) {
  return 0;
}
  i = (i + 1);
}
  return 1;
}

int32_t flowc_span_find_last(uint8_t* text, int32_t start, int32_t end, int32_t ch) {
  int32_t i = (end - 1);
  while (i >= start) {
  if (text[i] == ch) {
  return i;
}
  i = (i - 1);
}
  return (0 - 1);
}

int32_t flowc_span_find_first(uint8_t* text, int32_t start, int32_t end, int32_t ch) {
  int32_t i = start;
  while (i < end) {
  if (text[i] == ch) {
  return i;
}
  i = (i + 1);
}
  return (0 - 1);
}

int32_t flowc_path_basename_start(uint8_t* text, int32_t start, int32_t end) {
  int32_t slash = flowc_span_find_last(text, start, end, 47);
  if (slash < 0) {
  return start;
}
  return (slash + 1);
}

int32_t flowc_span_ends_with(uint8_t* text, int32_t start, int32_t end, uint8_t* lit) {
  int32_t lit_len = (int32_t)(strlen(lit));
  if ((end - start) < lit_len) {
  return 0;
}
  int32_t off = (end - lit_len);
  int32_t i = 0;
  while (i < lit_len) {
  if (text[(off + i)] != lit[i]) {
  return 0;
}
  i = (i + 1);
}
  return 1;
}


int32_t flowc_bpf_gen_compile(const char* in_path, const char* out_path, const char* optimize);
int32_t flowc_bpf_gen_compile(const char* in_path, const char* out_path, const char* optimize) {
  uint8_t* cmd = (uint8_t*)(malloc(4096));
  if (cmd == NULL) {
  return 1;
}
  int32_t _s1 = sprintf(cmd, (uint8_t*)("PYTHONPATH=src python3 -m flow.transpiler %s --llvm --optimize --opt-level O%s -o build/flow_bpf_tmp.ll"), (uint8_t*)(in_path), (uint8_t*)(optimize), (uint8_t*)(""));
  int32_t rc1 = flowc_io_system((const char*)(cmd));
  if (rc1 != 0) {
  puts("error: Flow -> LLVM IR lowering failed");
  free(cmd);
  return 1;
}
  const char* tmp_path = "build/flow_bpf_tmp.ll";
  int64_t sz = flowc_io_file_size(tmp_path);
  if (sz <= 0) {
  free(cmd);
  return 1;
}
  uint8_t* ir_buf = (uint8_t*)(malloc((sz + 1)));
  int32_t nread = flowc_read_file(tmp_path, ir_buf, (int32_t)(sz));
  if (nread < 0) {
  free(ir_buf);
  free(cmd);
  return 1;
}
  ir_buf[nread] = 0;
  uint8_t* out_buf = (uint8_t*)(malloc((sz + 1024)));
  int32_t out_len = 0;
  int32_t _s_out = sprintf(out_buf, (uint8_t*)("target datalayout = \"e-m:e-p:64:64-i64:64-i128:128-n32:64-S128\"\ntarget triple = \"bpfel\"\n"), (uint8_t*)(""), (uint8_t*)(""), (uint8_t*)(""));
  out_len = flowc_strlen((const char*)(out_buf));
  int32_t i = 0;
  while (i < nread) {
  int32_t nl = flowc_span_find_first(ir_buf, i, nread, 10);
  int32_t end = nread;
  if (nl >= 0) {
  end = (nl + 1);
}
  int32_t is_dl = flowc_span_starts_with(ir_buf, i, end, (uint8_t*)("target datalayout ="));
  int32_t is_tt = flowc_span_starts_with(ir_buf, i, end, (uint8_t*)("target triple ="));
  if (is_dl == 0 && is_tt == 0) {
  uint8_t* _m = (uint8_t*)(memcpy((out_buf + out_len), (ir_buf + i), (int64_t)((end - i))));
  out_len = (out_len + (end - i));
}
  i = end;
}
  int32_t _w = flowc_write_file(tmp_path, out_buf, out_len);
  free(ir_buf);
  free(out_buf);
  int32_t _s2 = sprintf(cmd, (uint8_t*)("clang -target bpfel -O%s -x ir -c -o %s build/flow_bpf_tmp.ll"), (uint8_t*)(optimize), (uint8_t*)(out_path), (uint8_t*)(""));
  int32_t rc2 = flowc_io_system((const char*)(cmd));
  if (rc2 != 0) {
  puts("error: LLVM IR -> eBPF compilation failed");
  free(cmd);
  return 1;
}
  free(cmd);
  return 0;
}


int32_t flowc_env_set(const char* name);
int32_t flowc_env_eq(const char* name, const char* want);
int32_t flowc_env_is_zero(const char* name);
int32_t flowc_want_typecheck();
int32_t flowc_emit_mode();
int32_t flowc_bytes_contains(uint8_t* hay, int32_t hay_len, const char* needle);
int32_t expect_kind(int32_t kind, int32_t want);
int32_t test_lexer_smoke();
int32_t test_parse_core();
int32_t test_parse_for();
int32_t test_parse_struct();
int32_t test_parse_extern();
int32_t test_parse_import_export();
int32_t test_parse_export_bare();
int32_t test_cgen_for();
int32_t test_cgen_logic();
int32_t test_cgen_string();
int32_t test_cgen_emit();
int32_t test_parse_fixture_file();
int32_t test_parse_ptr_array_types();
int32_t test_parse_field_index();
int32_t test_parse_struct_lit();
int32_t test_parse_break_continue();
int32_t test_parse_string_lit();
int32_t test_parse_const();
int32_t test_cgen_const();
int32_t test_cgen_struct();
int32_t test_cgen_ptr();
int32_t test_parse_cast();
int32_t test_parse_index_assign();
int32_t test_cgen_cast();
int32_t test_cgen_void();
int32_t test_jsgen_emit();
int32_t test_typecheck_ok();
int32_t test_typecheck_bad();
int32_t test_typecheck_arity_void();
int32_t test_typecheck_dup_let();
int32_t test_typecheck_dup_const();
int32_t test_typecheck_assign_unknown();
int32_t test_typecheck_break_outside();
int32_t test_typecheck_bad_field();
int32_t test_resolve_sibling();
int32_t test_bundle_typecheck();
int32_t test_bundle_emit();
int32_t test_fmt_emit();
int32_t test_parse_match();
int32_t test_cgen_match();
int32_t test_parse_elif();
int32_t test_typecheck_match_catchall();
int32_t main();
int32_t flowc_env_set(const char* name) {
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

int32_t flowc_env_eq(const char* name, const char* want) {
  const char* v = getenv(name);
  uint8_t* p = (uint8_t*)(v);
  if (p == NULL) {
  return 0;
}
  if (strcmp(v, want) == 0) {
  return 1;
}
  return 0;
}

int32_t flowc_env_is_zero(const char* name) {
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

int32_t flowc_want_typecheck() {
  if (flowc_env_set("FLOWC_NO_TYPECHECK") == 1) {
  return 0;
}
  if (flowc_env_is_zero("FLOWC_TYPECHECK") == 1) {
  return 0;
}
  return 1;
}

int32_t flowc_emit_mode() {
  const char* in_path = getenv("FLOWC_IN");
  const char* out_path = getenv("FLOWC_OUT");
  if (flowc_env_eq("FLOWC_BACKEND", "wasm") == 1) {
  if (out_path == NULL) {
  puts("flowc emit: wasm requires FLOWC_OUT");
  return 1;
}
  return flowc_wasm_gen_compile(in_path, out_path, "2");
}
  if (flowc_env_eq("FLOWC_BACKEND", "bpf") == 1) {
  if (out_path == NULL) {
  puts("flowc emit: bpf requires FLOWC_OUT");
  return 1;
}
  return flowc_bpf_gen_compile(in_path, out_path, "2");
}
  int32_t out_cap = 1048576;
  uint8_t* out = (uint8_t*)(malloc((int64_t)(out_cap)));
  if (out == NULL) {
  puts("flowc emit: malloc out failed");
  return 1;
}
  int32_t zi = 0;
  while (zi < out_cap) {
  out[zi] = 0;
  zi = (zi + 1);
}
  int32_t nout = 0;
  if (flowc_env_set("FLOWC_BUNDLE") == 1) {
  const char* search_dir = "compiler/src";
  uint8_t* dir_buf = (uint8_t*)(malloc(256));
  if (dir_buf == NULL) {
  puts("flowc emit: malloc dir failed");
  free(out);
  return 1;
}
  zi = 0;
  while (zi < 256) {
  dir_buf[zi] = 0;
  zi = (zi + 1);
}
  if (flowc_env_set("FLOWC_DIR") == 1) {
  search_dir = getenv("FLOWC_DIR");
} else {
  int32_t dlen = flowc_resolve_dirname(in_path, dir_buf, 256);
  if (dlen > 0) {
  search_dir = dir_buf;
}
}
  if (flowc_want_typecheck() == 1) {
  int32_t tc_errs = flowc_bundle_typecheck(in_path, search_dir);
  if (tc_errs > 0) {
  puts("flowc emit: bundle typecheck failed");
  printf("flowc emit: tc_errs=%d\n", tc_errs);
  free(dir_buf);
  free(out);
  return 1;
}
}
  nout = flowc_bundle_emit(in_path, search_dir, out, out_cap);
  free(dir_buf);
  if (nout <= 0) {
  puts("flowc emit: bundle emit failed");
  free(out);
  return 1;
}
} else {
  int32_t src_cap = 262144;
  uint8_t* src = (uint8_t*)(malloc((int64_t)(src_cap)));
  if (src == NULL) {
  puts("flowc emit: malloc src failed");
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
  puts("flowc emit: read FLOWC_IN failed");
  free(src);
  free(out);
  return 1;
}
  src[nsrc] = 0;
  Parser p = flowc_parser_new(src, nsrc, 262144);
  int32_t root = flowc_parse_program((&p));
  if (root < 0 || (p).err != 0) {
  puts("flowc emit: parse failed");
  printf("flowc emit: at %d\n", ((p).cur).start);
  printf("flowc emit: arena_len=%d\n", ((p).arena).len);
  flowc_parser_free(p);
  free(src);
  free(out);
  return 1;
}
  if (flowc_want_typecheck() == 1) {
  int32_t tc_errs = flowc_typecheck((p).arena, root, src);
  if (tc_errs > 0) {
  puts("flowc emit: typecheck failed");
  printf("flowc emit: tc_errs=%d\n", tc_errs);
  flowc_parser_free(p);
  free(src);
  free(out);
  return 1;
}
}
  if (flowc_env_eq("FLOWC_BACKEND", "js") == 1) {
  nout = flowc_jsgen_emit((p).arena, root, src, out, out_cap);
  if (nout <= 0) {
  puts("flowc emit: jsgen failed");
  free(out);
  flowc_parser_free(p);
  free(src);
  return 1;
}
} else {
  if (flowc_env_eq("FLOWC_BACKEND", "fmt") == 1) {
  nout = flowc_fmt_emit((p).arena, root, src, out, out_cap);
  if (nout <= 0) {
  puts("flowc emit: fmt failed");
  free(out);
  flowc_parser_free(p);
  free(src);
  return 1;
}
} else {
  nout = flowc_cgen_emit((p).arena, root, src, out, out_cap);
  if (nout <= 0) {
  puts("flowc emit: cgen failed");
  free(out);
  flowc_parser_free(p);
  free(src);
  return 1;
}
}
}
  flowc_parser_free(p);
  free(src);
}
  int32_t rc = 0;
  if (flowc_env_set("FLOWC_OUT") == 1) {
  const char* out_path = getenv("FLOWC_OUT");
  if (flowc_write_file(out_path, out, nout) != 0) {
  puts("flowc emit: write FLOWC_OUT failed");
  rc = 1;
}
} else {
  if (nout < out_cap) {
  out[nout] = 0;
}
  puts(out);
}
  free(out);
  return rc;
}

int32_t flowc_bytes_contains(uint8_t* hay, int32_t hay_len, const char* needle) {
  uint8_t* np = (uint8_t*)(needle);
  int32_t nlen = (int32_t)(strlen(needle));
  if (nlen == 0) {
  return 1;
}
  if (nlen > hay_len) {
  return 0;
}
  int32_t i = 0;
  while (i <= (hay_len - nlen)) {
  int32_t j = 0;
  int32_t ok = 1;
  while (j < nlen) {
  if (hay[(i + j)] != np[j]) {
  ok = 0;
  break;
}
  j = (j + 1);
}
  if (ok == 1) {
  return 1;
}
  i = (i + 1);
}
  return 0;
}

int32_t expect_kind(int32_t kind, int32_t want) {
  if (kind == want) {
  return 1;
}
  return 0;
}

int32_t test_lexer_smoke() {
  uint8_t a[15] = { 108, 101, 116, 32, 120, 58, 32, 105, 51, 50, 32, 61, 32, 52, 50 };
  uint8_t* ap = (uint8_t*)(a);
  Lexer la = flowc_lexer_new(ap, 15);
  Token t0 = flowc_lexer_next((&la));
  Token t1 = flowc_lexer_next((&la));
  Token t2 = flowc_lexer_next((&la));
  Token t3 = flowc_lexer_next((&la));
  Token t4 = flowc_lexer_next((&la));
  Token t5 = flowc_lexer_next((&la));
  Token t6 = flowc_lexer_next((&la));
  int32_t ok = 1;
  if (expect_kind((t0).kind, TOK_KEYWORD) == 0) {
  ok = 0;
}
  if ((t0).kw != KW_LET) {
  ok = 0;
}
  if (expect_kind((t1).kind, TOK_IDENT) == 0) {
  ok = 0;
}
  if (expect_kind((t5).kind, TOK_INT) == 0) {
  ok = 0;
}
  if (expect_kind((t6).kind, TOK_EOF) == 0) {
  ok = 0;
}
  return ok;
}

int32_t test_parse_core() {
  uint8_t src[220] = { 102, 117, 110, 99, 116, 105, 111, 110, 32, 97, 100, 100, 40, 97, 58, 32, 105, 51, 50, 44, 32, 98, 58, 32, 105, 51, 50, 41, 32, 45, 62, 32, 105, 51, 50, 32, 123, 10, 32, 32, 108, 101, 116, 32, 109, 117, 116, 32, 115, 58, 32, 105, 51, 50, 32, 61, 32, 97, 32, 43, 32, 98, 10, 32, 32, 114, 101, 116, 117, 114, 110, 32, 115, 10, 125, 10, 102, 117, 110, 99, 116, 105, 111, 110, 32, 109, 97, 105, 110, 40, 41, 32, 45, 62, 32, 105, 51, 50, 32, 123, 10, 32, 32, 108, 101, 116, 32, 120, 58, 32, 105, 51, 50, 32, 61, 32, 97, 100, 100, 40, 50, 48, 44, 32, 50, 50, 41, 10, 32, 32, 105, 102, 32, 120, 32, 61, 61, 32, 52, 50, 32, 123, 10, 32, 32, 32, 32, 114, 101, 116, 117, 114, 110, 32, 120, 10, 32, 32, 125, 32, 101, 108, 115, 101, 32, 123, 10, 32, 32, 32, 32, 114, 101, 116, 117, 114, 110, 32, 48, 10, 32, 32, 125, 10, 125, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
  uint8_t* sp = (uint8_t*)(src);
  int32_t len = 0;
  while (len < 220 && sp[len] != 0) {
  len = (len + 1);
}
  Parser p = flowc_parser_new(sp, len, 512);
  int32_t root = flowc_parse_program((&p));
  int32_t ok = 1;
  if (root < 0) {
  ok = 0;
}
  if ((p).err != 0) {
  ok = 0;
}
  int32_t n_fn = flowc_ast_count_kind((p).arena, AST_FN);
  int32_t n_let = flowc_ast_count_kind((p).arena, AST_LET);
  int32_t n_ret = flowc_ast_count_kind((p).arena, AST_RETURN);
  int32_t n_if = flowc_ast_count_kind((p).arena, AST_IF);
  int32_t n_call = flowc_ast_count_kind((p).arena, AST_CALL);
  int32_t n_binop = flowc_ast_count_kind((p).arena, AST_BINOP);
  int32_t n_int = flowc_ast_count_kind((p).arena, AST_INT);
  printf("fns=%d\n", n_fn);
  printf("lets=%d\n", n_let);
  printf("returns=%d\n", n_ret);
  printf("ifs=%d\n", n_if);
  printf("calls=%d\n", n_call);
  printf("binops=%d\n", n_binop);
  printf("ints=%d\n", n_int);
  printf("nodes=%d\n", ((p).arena).len);
  printf("err=%d\n", (p).err);
  if (n_fn != 2) {
  ok = 0;
}
  if (n_let != 2) {
  ok = 0;
}
  if (n_ret != 3) {
  ok = 0;
}
  if (n_if != 1) {
  ok = 0;
}
  if (n_call != 1) {
  ok = 0;
}
  if (n_binop < 2) {
  ok = 0;
}
  flowc_parser_free(p);
  return ok;
}

int32_t test_parse_for() {
  uint8_t src[80] = { 102, 117, 110, 99, 116, 105, 111, 110, 32, 102, 40, 41, 32, 45, 62, 32, 105, 51, 50, 32, 123, 10, 32, 32, 102, 111, 114, 32, 105, 32, 105, 110, 32, 48, 32, 116, 111, 32, 49, 48, 32, 123, 10, 32, 32, 32, 32, 108, 101, 116, 32, 120, 58, 32, 105, 51, 50, 32, 61, 32, 105, 10, 32, 32, 125, 10, 32, 32, 114, 101, 116, 117, 114, 110, 32, 48, 10, 125, 10, 0 };
  uint8_t* sp = (uint8_t*)(src);
  int32_t len = 0;
  while (len < 80 && sp[len] != 0) {
  len = (len + 1);
}
  Parser p = flowc_parser_new(sp, len, 256);
  int32_t root = flowc_parse_program((&p));
  int32_t ok = 1;
  if (root < 0) {
  ok = 0;
}
  if ((p).err != 0) {
  ok = 0;
}
  int32_t n_for = flowc_ast_count_kind((p).arena, AST_FOR);
  int32_t n_let = flowc_ast_count_kind((p).arena, AST_LET);
  printf("fors=%d\n", n_for);
  printf("for_lets=%d\n", n_let);
  if (n_for != 1) {
  ok = 0;
}
  if (n_let != 1) {
  ok = 0;
}
  flowc_parser_free(p);
  return ok;
}

int32_t test_parse_struct() {
  uint8_t src[80] = { 115, 116, 114, 117, 99, 116, 32, 80, 111, 105, 110, 116, 32, 123, 10, 32, 32, 120, 58, 32, 105, 51, 50, 44, 10, 32, 32, 121, 58, 32, 105, 51, 50, 10, 125, 10, 102, 117, 110, 99, 116, 105, 111, 110, 32, 111, 114, 105, 103, 105, 110, 40, 41, 32, 45, 62, 32, 105, 51, 50, 32, 123, 10, 32, 32, 114, 101, 116, 117, 114, 110, 32, 48, 10, 125, 10, 0, 0, 0, 0 };
  uint8_t* sp = (uint8_t*)(src);
  int32_t len = 0;
  while (len < 80 && sp[len] != 0) {
  len = (len + 1);
}
  Parser p = flowc_parser_new(sp, len, 256);
  int32_t root = flowc_parse_program((&p));
  int32_t ok = 1;
  if (root < 0) {
  ok = 0;
}
  if ((p).err != 0) {
  ok = 0;
}
  int32_t n_st = flowc_ast_count_kind((p).arena, AST_STRUCT);
  int32_t n_field = flowc_ast_count_kind((p).arena, AST_FIELD);
  int32_t n_fn = flowc_ast_count_kind((p).arena, AST_FN);
  printf("structs=%d\n", n_st);
  printf("fields=%d\n", n_field);
  printf("struct_fns=%d\n", n_fn);
  if (n_st != 1) {
  ok = 0;
}
  if (n_field != 2) {
  ok = 0;
}
  if (n_fn != 1) {
  ok = 0;
}
  flowc_parser_free(p);
  return ok;
}

int32_t test_parse_extern() {
  uint8_t src[88] = { 101, 120, 116, 101, 114, 110, 32, 123, 10, 32, 32, 102, 117, 110, 99, 116, 105, 111, 110, 32, 112, 117, 116, 115, 40, 115, 58, 32, 115, 116, 114, 105, 110, 103, 41, 32, 45, 62, 32, 105, 51, 50, 10, 125, 10, 102, 117, 110, 99, 116, 105, 111, 110, 32, 109, 97, 105, 110, 40, 41, 32, 45, 62, 32, 105, 51, 50, 32, 123, 10, 32, 32, 114, 101, 116, 117, 114, 110, 32, 48, 10, 125, 10, 0, 0, 0, 0, 0 };
  uint8_t* sp = (uint8_t*)(src);
  int32_t len = 0;
  while (len < 88 && sp[len] != 0) {
  len = (len + 1);
}
  Parser p = flowc_parser_new(sp, len, 256);
  int32_t root = flowc_parse_program((&p));
  int32_t ok = 1;
  if (root < 0) {
  ok = 0;
}
  if ((p).err != 0) {
  ok = 0;
}
  int32_t n_ex = flowc_ast_count_kind((p).arena, AST_EXTERN);
  int32_t n_fn = flowc_ast_count_kind((p).arena, AST_FN);
  printf("externs=%d\n", n_ex);
  printf("extern_fns=%d\n", n_fn);
  if (n_ex != 1) {
  ok = 0;
}
  if (n_fn != 2) {
  ok = 0;
}
  flowc_parser_free(p);
  return ok;
}

int32_t test_parse_import_export() {
  uint8_t src[200] = { 105, 109, 112, 111, 114, 116, 32, 46, 116, 111, 107, 101, 110, 32, 123, 32, 84, 79, 75, 95, 69, 79, 70, 32, 125, 10, 105, 109, 112, 111, 114, 116, 32, 112, 107, 103, 46, 109, 111, 100, 32, 123, 32, 97, 44, 32, 98, 32, 125, 10, 105, 109, 112, 111, 114, 116, 32, 34, 112, 97, 116, 104, 46, 102, 108, 111, 119, 34, 10, 101, 120, 112, 111, 114, 116, 32, 102, 117, 110, 99, 116, 105, 111, 110, 32, 97, 100, 100, 40, 97, 58, 32, 105, 51, 50, 44, 32, 98, 58, 32, 105, 51, 50, 41, 32, 45, 62, 32, 105, 51, 50, 32, 123, 32, 114, 101, 116, 117, 114, 110, 32, 97, 32, 125, 10, 101, 120, 112, 111, 114, 116, 32, 115, 116, 114, 117, 99, 116, 32, 80, 111, 105, 110, 116, 32, 123, 32, 120, 58, 32, 105, 51, 50, 32, 125, 10, 102, 117, 110, 99, 116, 105, 111, 110, 32, 109, 97, 105, 110, 40, 41, 32, 45, 62, 32, 105, 51, 50, 32, 123, 32, 114, 101, 116, 117, 114, 110, 32, 48, 32, 125, 10, 0, 0, 0, 0, 0, 0, 0, 0 };
  uint8_t* sp = (uint8_t*)(src);
  int32_t len = 0;
  while (len < 200 && sp[len] != 0) {
  len = (len + 1);
}
  Parser p = flowc_parser_new(sp, len, 512);
  int32_t root = flowc_parse_program((&p));
  int32_t ok = 1;
  if (root < 0) {
  ok = 0;
}
  if ((p).err != 0) {
  ok = 0;
}
  int32_t n_imp = flowc_ast_count_kind((p).arena, AST_IMPORT);
  int32_t n_exp = flowc_ast_count_kind((p).arena, AST_EXPORT);
  int32_t n_fn = flowc_ast_count_kind((p).arena, AST_FN);
  int32_t n_st = flowc_ast_count_kind((p).arena, AST_STRUCT);
  printf("imports=%d\n", n_imp);
  printf("exports=%d\n", n_exp);
  printf("ie_fns=%d\n", n_fn);
  printf("ie_structs=%d\n", n_st);
  if (n_imp != 3) {
  ok = 0;
}
  if (n_exp != 2) {
  ok = 0;
}
  if (n_fn != 2) {
  ok = 0;
}
  if (n_st != 1) {
  ok = 0;
}
  int32_t rel = 0;
  int32_t str_form = 0;
  int32_t i = 0;
  while (i < ((p).arena).len) {
  if ((((p).arena).nodes[i]).kind == AST_IMPORT) {
  if ((((p).arena).nodes[i]).ival == 1) {
  rel = (rel + 1);
}
  if ((((p).arena).nodes[i]).ival == 2) {
  str_form = (str_form + 1);
}
}
  i = (i + 1);
}
  printf("import_rel=%d\n", rel);
  printf("import_str=%d\n", str_form);
  if (rel != 1) {
  ok = 0;
}
  if (str_form != 1) {
  ok = 0;
}
  flowc_parser_free(p);
  return ok;
}

int32_t test_parse_export_bare() {
  uint8_t src[48] = { 101, 120, 112, 111, 114, 116, 32, 97, 44, 32, 98, 10, 102, 117, 110, 99, 116, 105, 111, 110, 32, 109, 97, 105, 110, 40, 41, 32, 45, 62, 32, 105, 51, 50, 32, 123, 32, 114, 101, 116, 117, 114, 110, 32, 48, 32, 125, 10 };
  uint8_t* sp = (uint8_t*)(src);
  Parser p = flowc_parser_new(sp, 48, 128);
  int32_t root = flowc_parse_program((&p));
  int32_t ok = 1;
  if (root < 0) {
  ok = 0;
}
  if ((p).err != 0) {
  ok = 0;
}
  int32_t n_exp = flowc_ast_count_kind((p).arena, AST_EXPORT);
  int32_t n_fn = flowc_ast_count_kind((p).arena, AST_FN);
  printf("bare_exports=%d\n", n_exp);
  printf("bare_fns=%d\n", n_fn);
  if (n_exp != 1) {
  ok = 0;
}
  if (n_fn != 1) {
  ok = 0;
}
  int32_t bare = 0;
  int32_t i = 0;
  while (i < ((p).arena).len) {
  if ((((p).arena).nodes[i]).kind == AST_EXPORT && (((p).arena).nodes[i]).ival == 1) {
  bare = (bare + 1);
  int32_t n_names = flowc_ast_chain_len((p).arena, (((p).arena).nodes[i]).a);
  printf("bare_names=%d\n", n_names);
  if (n_names != 2) {
  ok = 0;
}
}
  i = (i + 1);
}
  if (bare != 1) {
  ok = 0;
}
  flowc_parser_free(p);
  return ok;
}

int32_t test_cgen_for() {
  uint8_t src[80] = { 102, 117, 110, 99, 116, 105, 111, 110, 32, 102, 40, 41, 32, 45, 62, 32, 105, 51, 50, 32, 123, 10, 32, 32, 102, 111, 114, 32, 105, 32, 105, 110, 32, 48, 32, 116, 111, 32, 49, 48, 32, 123, 10, 32, 32, 32, 32, 108, 101, 116, 32, 120, 58, 32, 105, 51, 50, 32, 61, 32, 105, 10, 32, 32, 125, 10, 32, 32, 114, 101, 116, 117, 114, 110, 32, 48, 10, 125, 10, 0 };
  uint8_t* sp = (uint8_t*)(src);
  int32_t len = 0;
  while (len < 80 && sp[len] != 0) {
  len = (len + 1);
}
  Parser p = flowc_parser_new(sp, len, 256);
  int32_t root = flowc_parse_program((&p));
  int32_t ok = 1;
  if (root < 0) {
  ok = 0;
}
  if ((p).err != 0) {
  ok = 0;
}
  int32_t cap = 8192;
  uint8_t* bp = (uint8_t*)(malloc((int64_t)(cap)));
  if (bp == NULL) {
  puts("cgen_for: malloc failed");
  flowc_parser_free(p);
  return 0;
}
  int32_t zi = 0;
  while (zi < cap) {
  bp[zi] = 0;
  zi = (zi + 1);
}
  int32_t n = flowc_cgen_emit((p).arena, root, sp, bp, cap);
  printf("cgen_for_bytes=%d\n", n);
  if (n <= 0) {
  ok = 0;
}
  if (flowc_bytes_contains(bp, n, "for (") == 0) {
  ok = 0;
}
  if (flowc_bytes_contains(bp, n, "int32_t i") == 0) {
  ok = 0;
}
  if (flowc_bytes_contains(bp, n, "i = i + 1") == 0) {
  ok = 0;
}
  if (flowc_bytes_contains(bp, n, "i < ") == 0) {
  ok = 0;
}
  free(bp);
  flowc_parser_free(p);
  return ok;
}

int32_t test_cgen_logic() {
  uint8_t src[128] = { 102, 117, 110, 99, 116, 105, 111, 110, 32, 102, 40, 97, 58, 32, 105, 51, 50, 44, 32, 98, 58, 32, 105, 51, 50, 41, 32, 45, 62, 32, 105, 51, 50, 32, 123, 10, 32, 32, 114, 101, 116, 117, 114, 110, 32, 97, 32, 38, 38, 32, 98, 10, 125, 10, 102, 117, 110, 99, 116, 105, 111, 110, 32, 103, 40, 120, 58, 32, 105, 51, 50, 44, 32, 121, 58, 32, 105, 51, 50, 41, 32, 45, 62, 32, 105, 51, 50, 32, 123, 10, 32, 32, 114, 101, 116, 117, 114, 110, 32, 120, 32, 61, 61, 32, 49, 32, 124, 124, 32, 121, 32, 61, 61, 32, 50, 10, 125, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
  uint8_t* sp = (uint8_t*)(src);
  int32_t len = 0;
  while (len < 128 && sp[len] != 0) {
  len = (len + 1);
}
  Parser p = flowc_parser_new(sp, len, 256);
  int32_t root = flowc_parse_program((&p));
  int32_t ok = 1;
  if (root < 0) {
  ok = 0;
}
  if ((p).err != 0) {
  ok = 0;
}
  int32_t cap = 8192;
  uint8_t* bp = (uint8_t*)(malloc((int64_t)(cap)));
  if (bp == NULL) {
  puts("cgen_logic: malloc failed");
  flowc_parser_free(p);
  return 0;
}
  int32_t zi = 0;
  while (zi < cap) {
  bp[zi] = 0;
  zi = (zi + 1);
}
  int32_t n = flowc_cgen_emit((p).arena, root, sp, bp, cap);
  printf("cgen_logic_bytes=%d\n", n);
  if (n <= 0) {
  ok = 0;
}
  if (flowc_bytes_contains(bp, n, "&&") == 0) {
  ok = 0;
}
  if (flowc_bytes_contains(bp, n, "||") == 0) {
  ok = 0;
}
  free(bp);
  flowc_parser_free(p);
  return ok;
}

int32_t test_cgen_string() {
  uint8_t src[64] = { 102, 117, 110, 99, 116, 105, 111, 110, 32, 109, 97, 105, 110, 40, 41, 32, 45, 62, 32, 105, 51, 50, 32, 123, 10, 32, 32, 108, 101, 116, 32, 115, 58, 32, 115, 116, 114, 105, 110, 103, 32, 61, 32, 34, 104, 105, 34, 10, 32, 32, 114, 101, 116, 117, 114, 110, 32, 48, 10, 125, 10, 0, 0, 0 };
  uint8_t* sp = (uint8_t*)(src);
  int32_t len = 0;
  while (len < 64 && sp[len] != 0) {
  len = (len + 1);
}
  Parser p = flowc_parser_new(sp, len, 256);
  int32_t root = flowc_parse_program((&p));
  int32_t ok = 1;
  if (root < 0) {
  ok = 0;
}
  if ((p).err != 0) {
  ok = 0;
}
  int32_t cap = 8192;
  uint8_t* bp = (uint8_t*)(malloc((int64_t)(cap)));
  if (bp == NULL) {
  puts("cgen_string: malloc failed");
  flowc_parser_free(p);
  return 0;
}
  int32_t zi = 0;
  while (zi < cap) {
  bp[zi] = 0;
  zi = (zi + 1);
}
  int32_t n = flowc_cgen_emit((p).arena, root, sp, bp, cap);
  printf("cgen_string_bytes=%d\n", n);
  if (n <= 0) {
  ok = 0;
}
  if (flowc_bytes_contains(bp, n, "\"hi\"") == 0) {
  ok = 0;
}
  free(bp);
  flowc_parser_free(p);
  return ok;
}

int32_t test_cgen_emit() {
  uint8_t src[220] = { 102, 117, 110, 99, 116, 105, 111, 110, 32, 97, 100, 100, 40, 97, 58, 32, 105, 51, 50, 44, 32, 98, 58, 32, 105, 51, 50, 41, 32, 45, 62, 32, 105, 51, 50, 32, 123, 10, 32, 32, 108, 101, 116, 32, 109, 117, 116, 32, 115, 58, 32, 105, 51, 50, 32, 61, 32, 97, 32, 43, 32, 98, 10, 32, 32, 114, 101, 116, 117, 114, 110, 32, 115, 10, 125, 10, 102, 117, 110, 99, 116, 105, 111, 110, 32, 109, 97, 105, 110, 40, 41, 32, 45, 62, 32, 105, 51, 50, 32, 123, 10, 32, 32, 108, 101, 116, 32, 120, 58, 32, 105, 51, 50, 32, 61, 32, 97, 100, 100, 40, 50, 48, 44, 32, 50, 50, 41, 10, 32, 32, 105, 102, 32, 120, 32, 61, 61, 32, 52, 50, 32, 123, 10, 32, 32, 32, 32, 114, 101, 116, 117, 114, 110, 32, 120, 10, 32, 32, 125, 32, 101, 108, 115, 101, 32, 123, 10, 32, 32, 32, 32, 114, 101, 116, 117, 114, 110, 32, 48, 10, 32, 32, 125, 10, 125, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
  uint8_t* sp = (uint8_t*)(src);
  int32_t len = 0;
  while (len < 220 && sp[len] != 0) {
  len = (len + 1);
}
  Parser p = flowc_parser_new(sp, len, 512);
  int32_t root = flowc_parse_program((&p));
  int32_t ok = 1;
  if (root < 0) {
  ok = 0;
}
  if ((p).err != 0) {
  ok = 0;
}
  int32_t cap = 8192;
  uint8_t* bp = (uint8_t*)(malloc((int64_t)(cap)));
  if (bp == NULL) {
  puts("cgen: malloc failed");
  flowc_parser_free(p);
  return 0;
}
  int32_t zi = 0;
  while (zi < cap) {
  bp[zi] = 0;
  zi = (zi + 1);
}
  int32_t n = flowc_cgen_emit((p).arena, root, sp, bp, cap);
  printf("cgen_bytes=%d\n", n);
  if (n <= 0) {
  ok = 0;
}
  if (flowc_bytes_contains(bp, n, "int32_t") == 0) {
  ok = 0;
}
  if (flowc_bytes_contains(bp, n, "add") == 0) {
  ok = 0;
}
  if (flowc_bytes_contains(bp, n, "return") == 0) {
  ok = 0;
}
  if (flowc_bytes_contains(bp, n, "#include <stdint.h>") == 0) {
  ok = 0;
}
  if (flowc_bytes_contains(bp, n, "if (") == 0) {
  ok = 0;
}
  if (n > 0 && n < cap) {
  bp[n] = 0;
  puts("--- cgen output ---");
  puts(bp);
  puts("--- end cgen ---");
}
  free(bp);
  flowc_parser_free(p);
  return ok;
}

int32_t test_parse_fixture_file() {
  const char* path = "compiler/fixtures/hello_subset.flow";
  int32_t cap = 4096;
  uint8_t* bp = (uint8_t*)(malloc((int64_t)(cap)));
  if (bp == NULL) {
  puts("fixture: malloc failed");
  return 0;
}
  int32_t zi = 0;
  while (zi < cap) {
  bp[zi] = 0;
  zi = (zi + 1);
}
  int32_t n = flowc_read_file(path, bp, (cap - 1));
  printf("fixture_bytes=%d\n", n);
  if (n <= 0) {
  puts("fixture: open/read failed (cwd must be repo root)");
  free(bp);
  return 0;
}
  bp[n] = 0;
  Parser p = flowc_parser_new(bp, n, 512);
  int32_t root = flowc_parse_program((&p));
  int32_t ok = 1;
  if (root < 0) {
  ok = 0;
}
  if ((p).err != 0) {
  ok = 0;
}
  int32_t n_fn = flowc_ast_count_kind((p).arena, AST_FN);
  int32_t n_let = flowc_ast_count_kind((p).arena, AST_LET);
  int32_t n_ret = flowc_ast_count_kind((p).arena, AST_RETURN);
  int32_t n_if = flowc_ast_count_kind((p).arena, AST_IF);
  int32_t n_for = flowc_ast_count_kind((p).arena, AST_FOR);
  int32_t n_st = flowc_ast_count_kind((p).arena, AST_STRUCT);
  int32_t n_field = flowc_ast_count_kind((p).arena, AST_FIELD);
  int32_t n_ex = flowc_ast_count_kind((p).arena, AST_EXTERN);
  int32_t n_call = flowc_ast_count_kind((p).arena, AST_CALL);
  printf("fixture_fns=%d\n", n_fn);
  printf("fixture_lets=%d\n", n_let);
  printf("fixture_returns=%d\n", n_ret);
  printf("fixture_ifs=%d\n", n_if);
  printf("fixture_fors=%d\n", n_for);
  printf("fixture_structs=%d\n", n_st);
  printf("fixture_fields=%d\n", n_field);
  printf("fixture_externs=%d\n", n_ex);
  printf("fixture_calls=%d\n", n_call);
  printf("fixture_nodes=%d\n", ((p).arena).len);
  printf("fixture_err=%d\n", (p).err);
  if (n_fn != 3) {
  ok = 0;
}
  if (n_st != 1) {
  ok = 0;
}
  if (n_field != 2) {
  ok = 0;
}
  if (n_ex != 1) {
  ok = 0;
}
  if (n_if != 1) {
  ok = 0;
}
  if (n_for != 1) {
  ok = 0;
}
  if (n_call != 1) {
  ok = 0;
}
  if (n_let < 2) {
  ok = 0;
}
  if (n_ret < 2) {
  ok = 0;
}
  flowc_parser_free(p);
  free(bp);
  return ok;
}

int32_t test_parse_ptr_array_types() {
  uint8_t src[64] = { 102, 117, 110, 99, 116, 105, 111, 110, 32, 102, 40, 112, 58, 32, 112, 116, 114, 60, 105, 51, 50, 62, 44, 32, 97, 58, 32, 97, 114, 114, 97, 121, 60, 105, 51, 50, 44, 32, 52, 62, 41, 32, 45, 62, 32, 105, 51, 50, 32, 123, 10, 32, 32, 114, 101, 116, 117, 114, 110, 32, 48, 10, 125, 10 };
  uint8_t* sp = (uint8_t*)(src);
  Parser p = flowc_parser_new(sp, 64, 256);
  int32_t root = flowc_parse_program((&p));
  int32_t ok = 1;
  if (root < 0) {
  ok = 0;
}
  if ((p).err != 0) {
  ok = 0;
}
  int32_t n_generic = 0;
  int32_t array_n = 0;
  int32_t i = 0;
  while (i < ((p).arena).len) {
  if ((((p).arena).nodes[i]).kind == AST_TYPE && (((p).arena).nodes[i]).a != AST_NONE) {
  n_generic = (n_generic + 1);
  if ((((p).arena).nodes[i]).ival == 4) {
  array_n = (array_n + 1);
}
}
  i = (i + 1);
}
  printf("generic_types=%d\n", n_generic);
  printf("array_size4=%d\n", array_n);
  if (n_generic != 2) {
  ok = 0;
}
  if (array_n != 1) {
  ok = 0;
}
  flowc_parser_free(p);
  return ok;
}

int32_t test_parse_field_index() {
  uint8_t src[74] = { 102, 117, 110, 99, 116, 105, 111, 110, 32, 102, 40, 41, 32, 45, 62, 32, 105, 51, 50, 32, 123, 10, 32, 32, 108, 101, 116, 32, 120, 58, 32, 105, 51, 50, 32, 61, 32, 112, 46, 120, 10, 32, 32, 108, 101, 116, 32, 121, 58, 32, 105, 51, 50, 32, 61, 32, 97, 91, 48, 93, 10, 32, 32, 114, 101, 116, 117, 114, 110, 32, 121, 10, 125, 10 };
  uint8_t* sp = (uint8_t*)(src);
  Parser p = flowc_parser_new(sp, 74, 256);
  int32_t root = flowc_parse_program((&p));
  int32_t ok = 1;
  if (root < 0) {
  ok = 0;
}
  if ((p).err != 0) {
  ok = 0;
}
  int32_t n_fa = flowc_ast_count_kind((p).arena, AST_FIELD_ACCESS);
  int32_t n_ix = flowc_ast_count_kind((p).arena, AST_INDEX);
  printf("field_access=%d\n", n_fa);
  printf("index=%d\n", n_ix);
  if (n_fa != 1) {
  ok = 0;
}
  if (n_ix != 1) {
  ok = 0;
}
  flowc_parser_free(p);
  return ok;
}

int32_t test_parse_struct_lit() {
  uint8_t src[73] = { 102, 117, 110, 99, 116, 105, 111, 110, 32, 102, 40, 41, 32, 45, 62, 32, 105, 51, 50, 32, 123, 10, 32, 32, 108, 101, 116, 32, 112, 58, 32, 80, 111, 105, 110, 116, 32, 61, 32, 80, 111, 105, 110, 116, 32, 123, 32, 120, 58, 32, 49, 44, 32, 121, 58, 32, 50, 32, 125, 10, 32, 32, 114, 101, 116, 117, 114, 110, 32, 48, 10, 125, 10 };
  uint8_t* sp = (uint8_t*)(src);
  Parser p = flowc_parser_new(sp, 73, 256);
  int32_t root = flowc_parse_program((&p));
  int32_t ok = 1;
  if (root < 0) {
  ok = 0;
}
  if ((p).err != 0) {
  ok = 0;
}
  int32_t n_lit = flowc_ast_count_kind((p).arena, AST_STRUCT_LIT);
  printf("struct_lits=%d\n", n_lit);
  if (n_lit != 1) {
  ok = 0;
}
  flowc_parser_free(p);
  return ok;
}

int32_t test_parse_break_continue() {
  uint8_t kw[14] = { 98, 114, 101, 97, 107, 32, 99, 111, 110, 116, 105, 110, 117, 101 };
  uint8_t* kp = (uint8_t*)(kw);
  Lexer la = flowc_lexer_new(kp, 14);
  Token t0 = flowc_lexer_next((&la));
  Token t1 = flowc_lexer_next((&la));
  int32_t ok = 1;
  if (expect_kind((t0).kind, TOK_KEYWORD) == 0) {
  ok = 0;
}
  if ((t0).kw != KW_BREAK) {
  ok = 0;
}
  if (expect_kind((t1).kind, TOK_KEYWORD) == 0) {
  ok = 0;
}
  if ((t1).kw != KW_CONTINUE) {
  ok = 0;
}
  uint8_t src[74] = { 102, 117, 110, 99, 116, 105, 111, 110, 32, 102, 40, 41, 32, 45, 62, 32, 105, 51, 50, 32, 123, 10, 32, 32, 119, 104, 105, 108, 101, 32, 49, 32, 123, 10, 32, 32, 32, 32, 98, 114, 101, 97, 107, 10, 32, 32, 32, 32, 99, 111, 110, 116, 105, 110, 117, 101, 10, 32, 32, 125, 10, 32, 32, 114, 101, 116, 117, 114, 110, 32, 48, 10, 125, 10 };
  uint8_t* sp = (uint8_t*)(src);
  Parser p = flowc_parser_new(sp, 74, 256);
  int32_t root = flowc_parse_program((&p));
  if (root < 0) {
  ok = 0;
}
  if ((p).err != 0) {
  ok = 0;
}
  int32_t n_br = flowc_ast_count_kind((p).arena, AST_BREAK);
  int32_t n_co = flowc_ast_count_kind((p).arena, AST_CONTINUE);
  printf("breaks=%d\n", n_br);
  printf("continues=%d\n", n_co);
  if (n_br != 1) {
  ok = 0;
}
  if (n_co != 1) {
  ok = 0;
}
  flowc_parser_free(p);
  return ok;
}

int32_t test_parse_string_lit() {
  uint8_t src[58] = { 102, 117, 110, 99, 116, 105, 111, 110, 32, 102, 40, 41, 32, 45, 62, 32, 105, 51, 50, 32, 123, 10, 32, 32, 108, 101, 116, 32, 115, 58, 32, 115, 116, 114, 105, 110, 103, 32, 61, 32, 34, 104, 105, 34, 10, 32, 32, 114, 101, 116, 117, 114, 110, 32, 48, 10, 125, 10 };
  uint8_t* sp = (uint8_t*)(src);
  Parser p = flowc_parser_new(sp, 58, 256);
  int32_t root = flowc_parse_program((&p));
  int32_t ok = 1;
  if (root < 0) {
  ok = 0;
}
  if ((p).err != 0) {
  ok = 0;
}
  int32_t n_str = flowc_ast_count_kind((p).arena, AST_STRING);
  printf("strings=%d\n", n_str);
  if (n_str != 1) {
  ok = 0;
}
  flowc_parser_free(p);
  return ok;
}

int32_t test_parse_const() {
  uint8_t kw[5] = { 99, 111, 110, 115, 116 };
  uint8_t* kp = (uint8_t*)(kw);
  Lexer la = flowc_lexer_new(kp, 5);
  Token t0 = flowc_lexer_next((&la));
  int32_t ok = 1;
  if (expect_kind((t0).kind, TOK_KEYWORD) == 0) {
  ok = 0;
}
  if ((t0).kw != KW_CONST) {
  ok = 0;
}
  uint8_t src[78] = { 99, 111, 110, 115, 116, 32, 88, 58, 32, 105, 51, 50, 32, 61, 32, 52, 50, 10, 101, 120, 112, 111, 114, 116, 32, 99, 111, 110, 115, 116, 32, 89, 58, 32, 105, 51, 50, 32, 61, 32, 55, 10, 102, 117, 110, 99, 116, 105, 111, 110, 32, 109, 97, 105, 110, 40, 41, 32, 45, 62, 32, 105, 51, 50, 32, 123, 32, 114, 101, 116, 117, 114, 110, 32, 48, 32, 125, 10 };
  uint8_t* sp = (uint8_t*)(src);
  Parser p = flowc_parser_new(sp, 78, 256);
  int32_t root = flowc_parse_program((&p));
  if (root < 0) {
  ok = 0;
}
  if ((p).err != 0) {
  ok = 0;
}
  int32_t n_c = flowc_ast_count_kind((p).arena, AST_CONST);
  printf("consts=%d\n", n_c);
  if (n_c != 2) {
  ok = 0;
}
  int32_t exported = 0;
  int32_t i = 0;
  while (i < ((p).arena).len) {
  if ((((p).arena).nodes[i]).kind == AST_CONST && (((p).arena).nodes[i]).ival == 1) {
  exported = (exported + 1);
}
  i = (i + 1);
}
  printf("export_consts=%d\n", exported);
  if (exported != 1) {
  ok = 0;
}
  flowc_parser_free(p);
  return ok;
}

int32_t test_cgen_const() {
  uint8_t src[85] = { 101, 120, 112, 111, 114, 116, 32, 99, 111, 110, 115, 116, 32, 78, 58, 32, 105, 51, 50, 32, 61, 32, 55, 10, 99, 111, 110, 115, 116, 32, 77, 58, 32, 105, 51, 50, 32, 61, 32, 53, 10, 102, 117, 110, 99, 116, 105, 111, 110, 32, 109, 97, 105, 110, 40, 41, 32, 45, 62, 32, 105, 51, 50, 32, 123, 10, 32, 32, 32, 32, 114, 101, 116, 117, 114, 110, 32, 78, 32, 43, 32, 77, 10, 125, 10 };
  uint8_t* sp = (uint8_t*)(src);
  Parser p = flowc_parser_new(sp, 85, 256);
  int32_t root = flowc_parse_program((&p));
  int32_t ok = 1;
  if (root < 0) {
  ok = 0;
}
  if ((p).err != 0) {
  ok = 0;
}
  int32_t cap = 8192;
  uint8_t* bp = (uint8_t*)(malloc((int64_t)(cap)));
  if (bp == NULL) {
  puts("cgen_const: malloc failed");
  flowc_parser_free(p);
  return 0;
}
  int32_t zi = 0;
  while (zi < cap) {
  bp[zi] = 0;
  zi = (zi + 1);
}
  int32_t n = flowc_cgen_emit((p).arena, root, sp, bp, cap);
  printf("cgen_const_bytes=%d\n", n);
  if (n <= 0) {
  ok = 0;
}
  if (flowc_bytes_contains(bp, n, "static const int32_t") == 0) {
  ok = 0;
}
  if (flowc_bytes_contains(bp, n, "N") == 0) {
  ok = 0;
}
  if (flowc_bytes_contains(bp, n, "7") == 0) {
  ok = 0;
}
  if (flowc_bytes_contains(bp, n, "M") == 0) {
  ok = 0;
}
  if (flowc_bytes_contains(bp, n, "5") == 0) {
  ok = 0;
}
  free(bp);
  flowc_parser_free(p);
  return ok;
}

int32_t test_cgen_struct() {
  uint8_t src[136] = { 115, 116, 114, 117, 99, 116, 32, 80, 111, 105, 110, 116, 32, 123, 10, 32, 32, 32, 32, 120, 58, 32, 105, 51, 50, 44, 10, 32, 32, 32, 32, 121, 58, 32, 105, 51, 50, 10, 125, 10, 10, 102, 117, 110, 99, 116, 105, 111, 110, 32, 109, 97, 105, 110, 40, 41, 32, 45, 62, 32, 105, 51, 50, 32, 123, 10, 32, 32, 32, 32, 108, 101, 116, 32, 112, 58, 32, 80, 111, 105, 110, 116, 32, 61, 32, 80, 111, 105, 110, 116, 32, 123, 32, 120, 58, 32, 50, 48, 44, 32, 121, 58, 32, 50, 50, 32, 125, 10, 32, 32, 32, 32, 114, 101, 116, 117, 114, 110, 32, 112, 46, 120, 32, 43, 32, 112, 46, 121, 10, 125, 10, 0, 0, 0, 0 };
  uint8_t* sp = (uint8_t*)(src);
  int32_t len = 0;
  while (len < 136 && sp[len] != 0) {
  len = (len + 1);
}
  Parser p = flowc_parser_new(sp, len, 256);
  int32_t root = flowc_parse_program((&p));
  int32_t ok = 1;
  if (root < 0) {
  ok = 0;
}
  if ((p).err != 0) {
  ok = 0;
}
  int32_t cap = 8192;
  uint8_t* bp = (uint8_t*)(malloc((int64_t)(cap)));
  if (bp == NULL) {
  puts("cgen_struct: malloc failed");
  flowc_parser_free(p);
  return 0;
}
  int32_t zi = 0;
  while (zi < cap) {
  bp[zi] = 0;
  zi = (zi + 1);
}
  int32_t n = flowc_cgen_emit((p).arena, root, sp, bp, cap);
  printf("cgen_struct_bytes=%d\n", n);
  if (n <= 0) {
  ok = 0;
}
  if (flowc_bytes_contains(bp, n, "typedef struct") == 0) {
  ok = 0;
}
  if (flowc_bytes_contains(bp, n, "Point") == 0) {
  ok = 0;
}
  if (flowc_bytes_contains(bp, n, "int32_t x") == 0) {
  ok = 0;
}
  if (flowc_bytes_contains(bp, n, "int32_t y") == 0) {
  ok = 0;
}
  if (flowc_bytes_contains(bp, n, ".x = ") == 0) {
  ok = 0;
}
  if (flowc_bytes_contains(bp, n, ".y = ") == 0) {
  ok = 0;
}
  free(bp);
  flowc_parser_free(p);
  return ok;
}

int32_t test_cgen_ptr() {
  uint8_t src[51] = { 102, 117, 110, 99, 116, 105, 111, 110, 32, 102, 40, 112, 58, 32, 112, 116, 114, 60, 105, 51, 50, 62, 41, 32, 45, 62, 32, 105, 51, 50, 32, 123, 10, 32, 32, 32, 32, 114, 101, 116, 117, 114, 110, 32, 112, 91, 48, 93, 10, 125, 10 };
  uint8_t* sp = (uint8_t*)(src);
  Parser p = flowc_parser_new(sp, 51, 256);
  int32_t root = flowc_parse_program((&p));
  int32_t ok = 1;
  if (root < 0) {
  ok = 0;
}
  if ((p).err != 0) {
  ok = 0;
}
  int32_t cap = 8192;
  uint8_t* bp = (uint8_t*)(malloc((int64_t)(cap)));
  if (bp == NULL) {
  puts("cgen_ptr: malloc failed");
  flowc_parser_free(p);
  return 0;
}
  int32_t zi = 0;
  while (zi < cap) {
  bp[zi] = 0;
  zi = (zi + 1);
}
  int32_t n = flowc_cgen_emit((p).arena, root, sp, bp, cap);
  printf("cgen_ptr_bytes=%d\n", n);
  if (n <= 0) {
  ok = 0;
}
  if (flowc_bytes_contains(bp, n, "int32_t*") == 0) {
  ok = 0;
}
  if (flowc_bytes_contains(bp, n, "p[0]") == 0) {
  ok = 0;
}
  free(bp);
  flowc_parser_free(p);
  return ok;
}

int32_t test_parse_cast() {
  uint8_t kw[2] = { 97, 115 };
  uint8_t* kp = (uint8_t*)(kw);
  Lexer la = flowc_lexer_new(kp, 2);
  Token t0 = flowc_lexer_next((&la));
  int32_t ok = 1;
  if (expect_kind((t0).kind, TOK_KEYWORD) == 0) {
  ok = 0;
}
  if ((t0).kw != KW_AS) {
  ok = 0;
}
  uint8_t src[72] = { 102, 117, 110, 99, 116, 105, 111, 110, 32, 102, 40, 41, 32, 45, 62, 32, 105, 51, 50, 32, 123, 10, 32, 32, 32, 32, 108, 101, 116, 32, 120, 58, 32, 105, 51, 50, 32, 61, 32, 49, 10, 32, 32, 32, 32, 114, 101, 116, 117, 114, 110, 32, 40, 120, 32, 97, 115, 32, 105, 54, 52, 41, 32, 97, 115, 32, 105, 51, 50, 10, 125, 10 };
  uint8_t* sp = (uint8_t*)(src);
  Parser p = flowc_parser_new(sp, 72, 256);
  int32_t root = flowc_parse_program((&p));
  if (root < 0) {
  ok = 0;
}
  if ((p).err != 0) {
  ok = 0;
}
  int32_t n_cast = flowc_ast_count_kind((p).arena, AST_CAST);
  printf("casts=%d\n", n_cast);
  if (n_cast != 2) {
  ok = 0;
}
  flowc_parser_free(p);
  return ok;
}

int32_t test_parse_index_assign() {
  uint8_t src[173] = { 102, 117, 110, 99, 116, 105, 111, 110, 32, 109, 97, 105, 110, 40, 41, 32, 45, 62, 32, 105, 51, 50, 32, 123, 10, 32, 32, 32, 32, 108, 101, 116, 32, 109, 117, 116, 32, 120, 58, 32, 105, 51, 50, 32, 61, 32, 48, 10, 32, 32, 32, 32, 108, 101, 116, 32, 109, 117, 116, 32, 121, 58, 32, 105, 51, 50, 32, 61, 32, 48, 10, 32, 32, 32, 32, 108, 101, 116, 32, 112, 58, 32, 112, 116, 114, 60, 105, 51, 50, 62, 32, 61, 32, 38, 120, 10, 32, 32, 32, 32, 108, 101, 116, 32, 113, 58, 32, 112, 116, 114, 60, 105, 51, 50, 62, 32, 61, 32, 38, 121, 10, 32, 32, 32, 32, 112, 91, 48, 93, 32, 61, 32, 52, 48, 10, 32, 32, 32, 32, 113, 91, 48, 93, 32, 61, 32, 50, 10, 32, 32, 32, 32, 114, 101, 116, 117, 114, 110, 32, 112, 91, 48, 93, 32, 43, 32, 113, 91, 48, 93, 10, 125, 10 };
  uint8_t* sp = (uint8_t*)(src);
  Parser p = flowc_parser_new(sp, 173, 256);
  int32_t root = flowc_parse_program((&p));
  int32_t ok = 1;
  if (root < 0) {
  ok = 0;
}
  if ((p).err != 0) {
  ok = 0;
}
  int32_t n_as = flowc_ast_count_kind((p).arena, AST_ASSIGN);
  int32_t n_ix = flowc_ast_count_kind((p).arena, AST_INDEX);
  printf("assigns=%d\n", n_as);
  printf("indexes=%d\n", n_ix);
  if (n_as != 2) {
  ok = 0;
}
  if (n_ix < 2) {
  ok = 0;
}
  flowc_parser_free(p);
  return ok;
}

int32_t test_cgen_cast() {
  uint8_t src[101] = { 102, 117, 110, 99, 116, 105, 111, 110, 32, 109, 97, 105, 110, 40, 41, 32, 45, 62, 32, 105, 51, 50, 32, 123, 10, 32, 32, 32, 32, 108, 101, 116, 32, 120, 58, 32, 105, 51, 50, 32, 61, 32, 52, 48, 10, 32, 32, 32, 32, 108, 101, 116, 32, 121, 58, 32, 105, 54, 52, 32, 61, 32, 40, 120, 32, 97, 115, 32, 105, 54, 52, 41, 32, 43, 32, 50, 10, 32, 32, 32, 32, 114, 101, 116, 117, 114, 110, 32, 40, 121, 32, 97, 115, 32, 105, 51, 50, 41, 10, 125, 10 };
  uint8_t* sp = (uint8_t*)(src);
  Parser p = flowc_parser_new(sp, 101, 256);
  int32_t root = flowc_parse_program((&p));
  int32_t ok = 1;
  if (root < 0) {
  ok = 0;
}
  if ((p).err != 0) {
  ok = 0;
}
  int32_t cap = 8192;
  uint8_t* bp = (uint8_t*)(malloc((int64_t)(cap)));
  if (bp == NULL) {
  puts("cgen_cast: malloc failed");
  flowc_parser_free(p);
  return 0;
}
  int32_t zi = 0;
  while (zi < cap) {
  bp[zi] = 0;
  zi = (zi + 1);
}
  int32_t n = flowc_cgen_emit((p).arena, root, sp, bp, cap);
  printf("cgen_cast_bytes=%d\n", n);
  if (n <= 0) {
  ok = 0;
}
  if (flowc_bytes_contains(bp, n, "int64_t") == 0) {
  ok = 0;
}
  if (flowc_bytes_contains(bp, n, ")(") == 0) {
  ok = 0;
}
  free(bp);
  flowc_parser_free(p);
  return ok;
}

int32_t test_cgen_void() {
  uint8_t src[66] = { 102, 117, 110, 99, 116, 105, 111, 110, 32, 103, 40, 41, 32, 45, 62, 32, 118, 111, 105, 100, 32, 123, 10, 125, 10, 10, 102, 117, 110, 99, 116, 105, 111, 110, 32, 109, 97, 105, 110, 40, 41, 32, 45, 62, 32, 105, 51, 50, 32, 123, 10, 32, 32, 32, 32, 114, 101, 116, 117, 114, 110, 32, 48, 10, 125, 10 };
  uint8_t* sp = (uint8_t*)(src);
  Parser p = flowc_parser_new(sp, 66, 256);
  int32_t root = flowc_parse_program((&p));
  int32_t ok = 1;
  if (root < 0) {
  ok = 0;
}
  if ((p).err != 0) {
  ok = 0;
}
  int32_t cap = 8192;
  uint8_t* bp = (uint8_t*)(malloc((int64_t)(cap)));
  if (bp == NULL) {
  puts("cgen_void: malloc failed");
  flowc_parser_free(p);
  return 0;
}
  int32_t zi = 0;
  while (zi < cap) {
  bp[zi] = 0;
  zi = (zi + 1);
}
  int32_t n = flowc_cgen_emit((p).arena, root, sp, bp, cap);
  printf("cgen_void_bytes=%d\n", n);
  if (n <= 0) {
  ok = 0;
}
  if (flowc_bytes_contains(bp, n, "void g") == 0) {
  ok = 0;
}
  free(bp);
  flowc_parser_free(p);
  return ok;
}

int32_t test_jsgen_emit() {
  uint8_t src[220] = { 102, 117, 110, 99, 116, 105, 111, 110, 32, 97, 100, 100, 40, 97, 58, 32, 105, 51, 50, 44, 32, 98, 58, 32, 105, 51, 50, 41, 32, 45, 62, 32, 105, 51, 50, 32, 123, 10, 32, 32, 108, 101, 116, 32, 109, 117, 116, 32, 115, 58, 32, 105, 51, 50, 32, 61, 32, 97, 32, 43, 32, 98, 10, 32, 32, 114, 101, 116, 117, 114, 110, 32, 115, 10, 125, 10, 102, 117, 110, 99, 116, 105, 111, 110, 32, 109, 97, 105, 110, 40, 41, 32, 45, 62, 32, 105, 51, 50, 32, 123, 10, 32, 32, 108, 101, 116, 32, 120, 58, 32, 105, 51, 50, 32, 61, 32, 97, 100, 100, 40, 50, 48, 44, 32, 50, 50, 41, 10, 32, 32, 105, 102, 32, 120, 32, 61, 61, 32, 52, 50, 32, 123, 10, 32, 32, 32, 32, 114, 101, 116, 117, 114, 110, 32, 120, 10, 32, 32, 125, 32, 101, 108, 115, 101, 32, 123, 10, 32, 32, 32, 32, 114, 101, 116, 117, 114, 110, 32, 48, 10, 32, 32, 125, 10, 125, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
  uint8_t* sp = (uint8_t*)(src);
  int32_t len = 0;
  while (len < 220 && sp[len] != 0) {
  len = (len + 1);
}
  Parser p = flowc_parser_new(sp, len, 512);
  int32_t root = flowc_parse_program((&p));
  int32_t ok = 1;
  if (root < 0) {
  ok = 0;
}
  if ((p).err != 0) {
  ok = 0;
}
  int32_t cap = 2048;
  uint8_t* bp = (uint8_t*)(malloc((int64_t)(cap)));
  if (bp == NULL) {
  puts("jsgen: malloc failed");
  flowc_parser_free(p);
  return 0;
}
  int32_t zi = 0;
  while (zi < cap) {
  bp[zi] = 0;
  zi = (zi + 1);
}
  int32_t n = flowc_jsgen_emit((p).arena, root, sp, bp, cap);
  printf("jsgen_bytes=%d\n", n);
  if (n <= 0) {
  ok = 0;
}
  if (flowc_bytes_contains(bp, n, "function") == 0) {
  ok = 0;
}
  if (flowc_bytes_contains(bp, n, "return") == 0) {
  ok = 0;
}
  if (flowc_bytes_contains(bp, n, "add") == 0) {
  ok = 0;
}
  if (flowc_bytes_contains(bp, n, "// Generated by flowc Stage-A") == 0) {
  ok = 0;
}
  if (flowc_bytes_contains(bp, n, "if (") == 0) {
  ok = 0;
}
  if (n > 0 && n < cap) {
  bp[n] = 0;
  puts("--- jsgen output ---");
  puts(bp);
  puts("--- end jsgen ---");
}
  free(bp);
  flowc_parser_free(p);
  return ok;
}

int32_t test_typecheck_ok() {
  uint8_t src[144] = { 102, 117, 110, 99, 116, 105, 111, 110, 32, 97, 100, 100, 40, 97, 58, 32, 105, 51, 50, 44, 32, 98, 58, 32, 105, 51, 50, 41, 32, 45, 62, 32, 105, 51, 50, 32, 123, 10, 32, 32, 108, 101, 116, 32, 109, 117, 116, 32, 115, 58, 32, 105, 51, 50, 32, 61, 32, 97, 32, 43, 32, 98, 10, 32, 32, 114, 101, 116, 117, 114, 110, 32, 115, 10, 125, 10, 102, 117, 110, 99, 116, 105, 111, 110, 32, 109, 97, 105, 110, 40, 41, 32, 45, 62, 32, 105, 51, 50, 32, 123, 10, 32, 32, 108, 101, 116, 32, 120, 58, 32, 105, 51, 50, 32, 61, 32, 97, 100, 100, 40, 50, 48, 44, 32, 50, 50, 41, 10, 32, 32, 114, 101, 116, 117, 114, 110, 32, 120, 10, 125, 10, 0, 0, 0 };
  uint8_t* sp = (uint8_t*)(src);
  int32_t len = 0;
  while (len < 144 && sp[len] != 0) {
  len = (len + 1);
}
  Parser p = flowc_parser_new(sp, len, 256);
  int32_t root = flowc_parse_program((&p));
  int32_t ok = 1;
  if (root < 0) {
  ok = 0;
}
  if ((p).err != 0) {
  ok = 0;
}
  int32_t errs = flowc_typecheck((p).arena, root, sp);
  printf("tc_ok_errs=%d\n", errs);
  if (errs != 0) {
  ok = 0;
}
  flowc_parser_free(p);
  return ok;
}

int32_t test_typecheck_bad() {
  uint8_t src[176] = { 102, 117, 110, 99, 116, 105, 111, 110, 32, 102, 40, 41, 32, 45, 62, 32, 105, 51, 50, 32, 123, 32, 114, 101, 116, 117, 114, 110, 32, 48, 32, 125, 10, 102, 117, 110, 99, 116, 105, 111, 110, 32, 102, 40, 41, 32, 45, 62, 32, 105, 51, 50, 32, 123, 32, 114, 101, 116, 117, 114, 110, 32, 49, 32, 125, 10, 102, 117, 110, 99, 116, 105, 111, 110, 32, 109, 97, 105, 110, 40, 41, 32, 45, 62, 32, 105, 51, 50, 32, 123, 10, 32, 32, 108, 101, 116, 32, 120, 58, 32, 105, 51, 50, 32, 61, 32, 110, 111, 112, 101, 40, 41, 10, 32, 32, 114, 101, 116, 117, 114, 110, 32, 121, 10, 125, 10, 102, 117, 110, 99, 116, 105, 111, 110, 32, 103, 40, 41, 32, 45, 62, 32, 105, 51, 50, 32, 123, 32, 114, 101, 116, 117, 114, 110, 32, 34, 104, 105, 34, 32, 125, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
  uint8_t* sp = (uint8_t*)(src);
  int32_t len = 0;
  while (len < 176 && sp[len] != 0) {
  len = (len + 1);
}
  Parser p = flowc_parser_new(sp, len, 256);
  int32_t root = flowc_parse_program((&p));
  int32_t ok = 1;
  if (root < 0) {
  ok = 0;
}
  if ((p).err != 0) {
  ok = 0;
}
  int32_t errs = flowc_typecheck((p).arena, root, sp);
  printf("tc_bad_errs=%d\n", errs);
  if (errs <= 0) {
  ok = 0;
}
  flowc_parser_free(p);
  return ok;
}

int32_t test_typecheck_arity_void() {
  uint8_t src[176] = { 102, 117, 110, 99, 116, 105, 111, 110, 32, 104, 40, 97, 58, 32, 105, 51, 50, 41, 32, 45, 62, 32, 105, 51, 50, 32, 123, 32, 114, 101, 116, 117, 114, 110, 32, 97, 32, 125, 10, 102, 117, 110, 99, 116, 105, 111, 110, 32, 118, 40, 41, 32, 45, 62, 32, 118, 111, 105, 100, 32, 123, 32, 114, 101, 116, 117, 114, 110, 32, 49, 32, 125, 10, 102, 117, 110, 99, 116, 105, 111, 110, 32, 119, 40, 41, 32, 45, 62, 32, 105, 51, 50, 32, 123, 32, 114, 101, 116, 117, 114, 110, 32, 125, 10, 102, 117, 110, 99, 116, 105, 111, 110, 32, 109, 97, 105, 110, 40, 41, 32, 45, 62, 32, 105, 51, 50, 32, 123, 10, 32, 32, 108, 101, 116, 32, 122, 58, 32, 105, 51, 50, 32, 61, 32, 104, 40, 41, 10, 32, 32, 114, 101, 116, 117, 114, 110, 32, 122, 10, 125, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
  uint8_t* sp = (uint8_t*)(src);
  int32_t len = 0;
  while (len < 176 && sp[len] != 0) {
  len = (len + 1);
}
  Parser p = flowc_parser_new(sp, len, 256);
  int32_t root = flowc_parse_program((&p));
  int32_t ok = 1;
  if (root < 0) {
  ok = 0;
}
  if ((p).err != 0) {
  ok = 0;
}
  int32_t errs = flowc_typecheck((p).arena, root, sp);
  printf("tc_arity_void_errs=%d\n", errs);
  if (errs < 3) {
  ok = 0;
}
  flowc_parser_free(p);
  return ok;
}

int32_t test_typecheck_dup_let() {
  uint8_t src[80] = { 102, 117, 110, 99, 116, 105, 111, 110, 32, 109, 97, 105, 110, 40, 41, 32, 45, 62, 32, 105, 51, 50, 32, 123, 10, 32, 32, 108, 101, 116, 32, 120, 58, 32, 105, 51, 50, 32, 61, 32, 49, 10, 32, 32, 108, 101, 116, 32, 120, 58, 32, 105, 51, 50, 32, 61, 32, 50, 10, 32, 32, 114, 101, 116, 117, 114, 110, 32, 120, 10, 125, 10, 0, 0, 0, 0, 0, 0, 0, 0 };
  uint8_t* sp = (uint8_t*)(src);
  int32_t len = 0;
  while (len < 80 && sp[len] != 0) {
  len = (len + 1);
}
  Parser p = flowc_parser_new(sp, len, 256);
  int32_t root = flowc_parse_program((&p));
  int32_t ok = 1;
  if (root < 0) {
  ok = 0;
}
  if ((p).err != 0) {
  ok = 0;
}
  int32_t errs = flowc_typecheck((p).arena, root, sp);
  printf("tc_dup_let_errs=%d\n", errs);
  if (errs <= 0) {
  ok = 0;
}
  flowc_parser_free(p);
  return ok;
}

int32_t test_typecheck_dup_const() {
  uint8_t src[80] = { 99, 111, 110, 115, 116, 32, 65, 58, 32, 105, 51, 50, 32, 61, 32, 49, 10, 99, 111, 110, 115, 116, 32, 65, 58, 32, 105, 51, 50, 32, 61, 32, 50, 10, 102, 117, 110, 99, 116, 105, 111, 110, 32, 109, 97, 105, 110, 40, 41, 32, 45, 62, 32, 105, 51, 50, 32, 123, 32, 114, 101, 116, 117, 114, 110, 32, 65, 32, 125, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
  uint8_t* sp = (uint8_t*)(src);
  int32_t len = 0;
  while (len < 80 && sp[len] != 0) {
  len = (len + 1);
}
  Parser p = flowc_parser_new(sp, len, 256);
  int32_t root = flowc_parse_program((&p));
  int32_t ok = 1;
  if (root < 0) {
  ok = 0;
}
  if ((p).err != 0) {
  ok = 0;
}
  int32_t errs = flowc_typecheck((p).arena, root, sp);
  printf("tc_dup_const_errs=%d\n", errs);
  if (errs <= 0) {
  ok = 0;
}
  flowc_parser_free(p);
  return ok;
}

int32_t test_typecheck_assign_unknown() {
  uint8_t src[48] = { 102, 117, 110, 99, 116, 105, 111, 110, 32, 109, 97, 105, 110, 40, 41, 32, 45, 62, 32, 105, 51, 50, 32, 123, 10, 32, 32, 121, 32, 61, 32, 49, 10, 32, 32, 114, 101, 116, 117, 114, 110, 32, 48, 10, 125, 10, 0, 0 };
  uint8_t* sp = (uint8_t*)(src);
  int32_t len = 0;
  while (len < 48 && sp[len] != 0) {
  len = (len + 1);
}
  Parser p = flowc_parser_new(sp, len, 256);
  int32_t root = flowc_parse_program((&p));
  int32_t ok = 1;
  if (root < 0) {
  ok = 0;
}
  if ((p).err != 0) {
  ok = 0;
}
  int32_t errs = flowc_typecheck((p).arena, root, sp);
  printf("tc_assign_unknown_errs=%d\n", errs);
  if (errs <= 0) {
  ok = 0;
}
  flowc_parser_free(p);
  return ok;
}

int32_t test_typecheck_break_outside() {
  uint8_t src[48] = { 102, 117, 110, 99, 116, 105, 111, 110, 32, 109, 97, 105, 110, 40, 41, 32, 45, 62, 32, 105, 51, 50, 32, 123, 10, 32, 32, 98, 114, 101, 97, 107, 10, 32, 32, 114, 101, 116, 117, 114, 110, 32, 48, 10, 125, 10, 0, 0 };
  uint8_t* sp = (uint8_t*)(src);
  int32_t len = 0;
  while (len < 48 && sp[len] != 0) {
  len = (len + 1);
}
  Parser p = flowc_parser_new(sp, len, 256);
  int32_t root = flowc_parse_program((&p));
  int32_t ok = 1;
  if (root < 0) {
  ok = 0;
}
  if ((p).err != 0) {
  ok = 0;
}
  int32_t errs = flowc_typecheck((p).arena, root, sp);
  printf("tc_break_outside_errs=%d\n", errs);
  if (errs <= 0) {
  ok = 0;
}
  flowc_parser_free(p);
  return ok;
}

int32_t test_typecheck_bad_field() {
  uint8_t src[112] = { 115, 116, 114, 117, 99, 116, 32, 80, 111, 105, 110, 116, 32, 123, 32, 120, 58, 32, 105, 51, 50, 44, 32, 121, 58, 32, 105, 51, 50, 32, 125, 10, 102, 117, 110, 99, 116, 105, 111, 110, 32, 109, 97, 105, 110, 40, 41, 32, 45, 62, 32, 105, 51, 50, 32, 123, 10, 32, 32, 108, 101, 116, 32, 112, 58, 32, 80, 111, 105, 110, 116, 32, 61, 32, 80, 111, 105, 110, 116, 32, 123, 32, 120, 58, 32, 49, 44, 32, 121, 58, 32, 50, 32, 125, 10, 32, 32, 114, 101, 116, 117, 114, 110, 32, 112, 46, 122, 10, 125, 10, 0, 0 };
  uint8_t* sp = (uint8_t*)(src);
  int32_t len = 0;
  while (len < 112 && sp[len] != 0) {
  len = (len + 1);
}
  Parser p = flowc_parser_new(sp, len, 256);
  int32_t root = flowc_parse_program((&p));
  int32_t ok = 1;
  if (root < 0) {
  ok = 0;
}
  if ((p).err != 0) {
  ok = 0;
}
  int32_t errs = flowc_typecheck((p).arena, root, sp);
  printf("tc_bad_field_errs=%d\n", errs);
  if (errs <= 0) {
  ok = 0;
}
  flowc_parser_free(p);
  return ok;
}

int32_t test_resolve_sibling() {
  uint8_t span[6] = { 46, 116, 111, 107, 101, 110 };
  uint8_t* sp = (uint8_t*)(span);
  uint8_t* out = (uint8_t*)(malloc(256));
  if (out == NULL) {
  puts("resolve_sibling: malloc failed");
  return 0;
}
  int32_t zi = 0;
  while (zi < 256) {
  out[zi] = 0;
  zi = (zi + 1);
}
  int32_t n = flowc_resolve_sibling_path(sp, 0, 6, "compiler/src", out, 256);
  printf("resolve_sib_len=%d\n", n);
  int32_t ok = 1;
  if (n <= 0) {
  ok = 0;
}
  if (flowc_bytes_contains(out, n, "compiler/src/token.flow") == 0) {
  ok = 0;
}
  free(out);
  return ok;
}

int32_t test_bundle_typecheck() {
  int32_t ok_errs = flowc_bundle_typecheck("compiler/fixtures/bundle_tc_ok.flow", "compiler/fixtures");
  printf("bundle_tc_ok_errs=%d\n", ok_errs);
  int32_t ok = 1;
  if (ok_errs != 0) {
  ok = 0;
}
  return ok;
}

int32_t test_bundle_emit() {
  int32_t out_cap = 65536;
  uint8_t* out = (uint8_t*)(malloc((int64_t)(out_cap)));
  if (out == NULL) {
  puts("bundle_emit: malloc failed");
  return 0;
}
  int32_t zi = 0;
  while (zi < out_cap) {
  out[zi] = 0;
  zi = (zi + 1);
}
  int32_t n = flowc_bundle_emit("compiler/fixtures/bundle_main.flow", "compiler/fixtures", out, out_cap);
  printf("bundle_bytes=%d\n", n);
  int32_t ok = 1;
  if (n <= 0) {
  ok = 0;
}
  if (flowc_bytes_contains(out, n, "twice") == 0) {
  ok = 0;
}
  if (flowc_bytes_contains(out, n, "int32_t N") == 0) {
  ok = 0;
}
  if (flowc_bytes_contains(out, n, "main") == 0) {
  ok = 0;
}
  if (flowc_bytes_contains(out, n, "#include <stdint.h>") == 0) {
  ok = 0;
}
  const char* needle = "#include <stdint.h>";
  uint8_t* np = (uint8_t*)(needle);
  int32_t nlen = (int32_t)(strlen(needle));
  int32_t count = 0;
  int32_t i = 0;
  while (i <= (n - nlen)) {
  int32_t j = 0;
  int32_t hit = 1;
  while (j < nlen) {
  if (out[(i + j)] != np[j]) {
  hit = 0;
  break;
}
  j = (j + 1);
}
  if (hit == 1) {
  count = (count + 1);
}
  i = (i + 1);
}
  printf("bundle_stdint_includes=%d\n", count);
  if (count != 1) {
  ok = 0;
}
  free(out);
  return ok;
}

int32_t test_fmt_emit() {
  uint8_t src[64] = { 102, 117, 110, 99, 116, 105, 111, 110, 32, 97, 100, 100, 40, 97, 58, 105, 51, 50, 44, 98, 58, 105, 51, 50, 41, 45, 62, 105, 51, 50, 123, 10, 108, 101, 116, 32, 120, 58, 105, 51, 50, 61, 97, 43, 98, 10, 114, 101, 116, 117, 114, 110, 32, 120, 10, 125, 10, 0, 0, 0, 0, 0, 0, 0 };
  uint8_t* sp = (uint8_t*)(src);
  int32_t len = 0;
  while (len < 64 && sp[len] != 0) {
  len = (len + 1);
}
  Parser p = flowc_parser_new(sp, len, 256);
  int32_t root = flowc_parse_program((&p));
  int32_t ok = 1;
  if (root < 0) {
  ok = 0;
}
  if ((p).err != 0) {
  ok = 0;
}
  int32_t cap = 1024;
  uint8_t* bp = (uint8_t*)(malloc((int64_t)(cap)));
  if (bp == NULL) {
  puts("fmt_emit: malloc failed");
  flowc_parser_free(p);
  return 0;
}
  int32_t zi = 0;
  while (zi < cap) {
  bp[zi] = 0;
  zi = (zi + 1);
}
  int32_t n = flowc_fmt_emit((p).arena, root, sp, bp, cap);
  printf("fmt_bytes=%d\n", n);
  if (n <= 0) {
  ok = 0;
}
  if (flowc_bytes_contains(bp, n, "function") == 0) {
  ok = 0;
}
  if (flowc_bytes_contains(bp, n, "return") == 0) {
  ok = 0;
}
  if (flowc_bytes_contains(bp, n, "let") == 0) {
  ok = 0;
}
  if (flowc_bytes_contains(bp, n, " -> ") == 0) {
  ok = 0;
}
  if (flowc_bytes_contains(bp, n, "a + b") == 0) {
  ok = 0;
}
  if (flowc_bytes_contains(bp, n, "{") == 0) {
  ok = 0;
}
  if (flowc_bytes_contains(bp, n, "}") == 0) {
  ok = 0;
}
  free(bp);
  flowc_parser_free(p);
  return ok;
}

int32_t test_parse_match() {
  uint8_t src[144] = { 102, 117, 110, 99, 116, 105, 111, 110, 32, 102, 40, 118, 58, 32, 105, 51, 50, 41, 32, 45, 62, 32, 105, 51, 50, 32, 123, 10, 32, 32, 108, 101, 116, 32, 109, 117, 116, 32, 114, 58, 32, 105, 51, 50, 32, 61, 32, 48, 10, 32, 32, 109, 97, 116, 99, 104, 32, 118, 32, 123, 10, 32, 32, 32, 32, 49, 32, 61, 62, 32, 123, 10, 32, 32, 32, 32, 32, 32, 114, 32, 61, 32, 49, 48, 10, 32, 32, 32, 32, 125, 10, 32, 32, 32, 32, 110, 32, 61, 62, 32, 123, 10, 32, 32, 32, 32, 32, 32, 114, 32, 61, 32, 110, 32, 43, 32, 49, 10, 32, 32, 32, 32, 125, 10, 32, 32, 125, 10, 32, 32, 114, 101, 116, 117, 114, 110, 32, 114, 10, 125, 10, 0, 0, 0 };
  uint8_t* sp = (uint8_t*)(src);
  int32_t len = 0;
  while (len < 144 && sp[len] != 0) {
  len = (len + 1);
}
  Parser p = flowc_parser_new(sp, len, 256);
  int32_t root = flowc_parse_program((&p));
  int32_t ok = 1;
  if (root < 0) {
  ok = 0;
}
  if ((p).err != 0) {
  ok = 0;
}
  int32_t n_match = flowc_ast_count_kind((p).arena, AST_MATCH);
  int32_t n_arm = flowc_ast_count_kind((p).arena, AST_MATCH_ARM);
  printf("matches=%d\n", n_match);
  printf("match_arms=%d\n", n_arm);
  if (n_match != 1) {
  ok = 0;
}
  if (n_arm != 2) {
  ok = 0;
}
  int32_t errs = flowc_typecheck((p).arena, root, sp);
  printf("match_tc_errs=%d\n", errs);
  if (errs != 0) {
  ok = 0;
}
  flowc_parser_free(p);
  return ok;
}

int32_t test_cgen_match() {
  uint8_t src[144] = { 102, 117, 110, 99, 116, 105, 111, 110, 32, 102, 40, 118, 58, 32, 105, 51, 50, 41, 32, 45, 62, 32, 105, 51, 50, 32, 123, 10, 32, 32, 108, 101, 116, 32, 109, 117, 116, 32, 114, 58, 32, 105, 51, 50, 32, 61, 32, 48, 10, 32, 32, 109, 97, 116, 99, 104, 32, 118, 32, 123, 10, 32, 32, 32, 32, 49, 32, 61, 62, 32, 123, 10, 32, 32, 32, 32, 32, 32, 114, 32, 61, 32, 49, 48, 10, 32, 32, 32, 32, 125, 10, 32, 32, 32, 32, 110, 32, 61, 62, 32, 123, 10, 32, 32, 32, 32, 32, 32, 114, 32, 61, 32, 110, 32, 43, 32, 49, 10, 32, 32, 32, 32, 125, 10, 32, 32, 125, 10, 32, 32, 114, 101, 116, 117, 114, 110, 32, 114, 10, 125, 10, 0, 0, 0 };
  uint8_t* sp = (uint8_t*)(src);
  int32_t len = 0;
  while (len < 144 && sp[len] != 0) {
  len = (len + 1);
}
  Parser p = flowc_parser_new(sp, len, 256);
  int32_t root = flowc_parse_program((&p));
  int32_t ok = 1;
  if (root < 0) {
  ok = 0;
}
  if ((p).err != 0) {
  ok = 0;
}
  int32_t cap = 8192;
  uint8_t* bp = (uint8_t*)(malloc((int64_t)(cap)));
  if (bp == NULL) {
  puts("cgen_match: malloc failed");
  flowc_parser_free(p);
  return 0;
}
  int32_t zi = 0;
  while (zi < cap) {
  bp[zi] = 0;
  zi = (zi + 1);
}
  int32_t n = flowc_cgen_emit((p).arena, root, sp, bp, cap);
  printf("cgen_match_bytes=%d\n", n);
  if (n <= 0) {
  ok = 0;
}
  if (flowc_bytes_contains(bp, n, "int32_t __flowc_match = v;") == 0) {
  ok = 0;
}
  if (flowc_bytes_contains(bp, n, "if (__flowc_match == 1) {") == 0) {
  ok = 0;
}
  if (flowc_bytes_contains(bp, n, "} else {") == 0) {
  ok = 0;
}
  if (flowc_bytes_contains(bp, n, "int32_t n = __flowc_match;") == 0) {
  ok = 0;
}
  free(bp);
  flowc_parser_free(p);
  return ok;
}

int32_t test_parse_elif() {
  uint8_t src[128] = { 102, 117, 110, 99, 116, 105, 111, 110, 32, 102, 40, 118, 58, 32, 105, 51, 50, 41, 32, 45, 62, 32, 105, 51, 50, 32, 123, 10, 32, 32, 105, 102, 32, 118, 32, 60, 32, 48, 32, 123, 10, 32, 32, 32, 32, 114, 101, 116, 117, 114, 110, 32, 49, 10, 32, 32, 125, 32, 101, 108, 105, 102, 32, 118, 32, 61, 61, 32, 48, 32, 123, 10, 32, 32, 32, 32, 114, 101, 116, 117, 114, 110, 32, 50, 10, 32, 32, 125, 32, 101, 108, 115, 101, 32, 123, 10, 32, 32, 32, 32, 114, 101, 116, 117, 114, 110, 32, 51, 10, 32, 32, 125, 10, 32, 32, 114, 101, 116, 117, 114, 110, 32, 48, 10, 125, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
  uint8_t* sp = (uint8_t*)(src);
  int32_t len = 0;
  while (len < 128 && sp[len] != 0) {
  len = (len + 1);
}
  Parser p = flowc_parser_new(sp, len, 256);
  int32_t root = flowc_parse_program((&p));
  int32_t ok = 1;
  if (root < 0) {
  ok = 0;
}
  if ((p).err != 0) {
  ok = 0;
}
  int32_t n_if = flowc_ast_count_kind((p).arena, AST_IF);
  int32_t n_ret = flowc_ast_count_kind((p).arena, AST_RETURN);
  printf("elif_ifs=%d\n", n_if);
  printf("elif_returns=%d\n", n_ret);
  if (n_if != 2) {
  ok = 0;
}
  if (n_ret != 4) {
  ok = 0;
}
  int32_t errs = flowc_typecheck((p).arena, root, sp);
  printf("elif_tc_errs=%d\n", errs);
  if (errs != 0) {
  ok = 0;
}
  flowc_parser_free(p);
  return ok;
}

int32_t test_typecheck_match_catchall() {
  uint8_t src[128] = { 102, 117, 110, 99, 116, 105, 111, 110, 32, 102, 40, 118, 58, 32, 105, 51, 50, 41, 32, 45, 62, 32, 105, 51, 50, 32, 123, 10, 32, 32, 109, 97, 116, 99, 104, 32, 118, 32, 123, 10, 32, 32, 32, 32, 95, 32, 61, 62, 32, 123, 10, 32, 32, 32, 32, 32, 32, 114, 101, 116, 117, 114, 110, 32, 49, 10, 32, 32, 32, 32, 125, 10, 32, 32, 32, 32, 50, 32, 61, 62, 32, 123, 10, 32, 32, 32, 32, 32, 32, 114, 101, 116, 117, 114, 110, 32, 50, 10, 32, 32, 32, 32, 125, 10, 32, 32, 125, 10, 32, 32, 114, 101, 116, 117, 114, 110, 32, 48, 10, 125, 10, 0, 0, 0, 0, 0, 0, 0 };
  uint8_t* sp = (uint8_t*)(src);
  int32_t len = 0;
  while (len < 128 && sp[len] != 0) {
  len = (len + 1);
}
  Parser p = flowc_parser_new(sp, len, 256);
  int32_t root = flowc_parse_program((&p));
  int32_t ok = 1;
  if (root < 0) {
  ok = 0;
}
  if ((p).err != 0) {
  ok = 0;
}
  int32_t errs = flowc_typecheck((p).arena, root, sp);
  printf("tc_match_catchall_errs=%d\n", errs);
  if (errs <= 0) {
  ok = 0;
}
  flowc_parser_free(p);
  return ok;
}

int32_t main() {
  if (flowc_env_set("FLOWC_IN") == 1) {
  return flowc_emit_mode();
}
  puts("flowc: self-hosting bootstrap");
  int32_t lex_ok = test_lexer_smoke();
  printf("lexer_ok=%d\n", lex_ok);
  int32_t parse_ok = test_parse_core();
  printf("parse_ok=%d\n", parse_ok);
  int32_t for_ok = test_parse_for();
  printf("for_ok=%d\n", for_ok);
  int32_t struct_ok = test_parse_struct();
  printf("struct_ok=%d\n", struct_ok);
  int32_t extern_ok = test_parse_extern();
  printf("extern_ok=%d\n", extern_ok);
  int32_t ie_ok = test_parse_import_export();
  printf("import_export_ok=%d\n", ie_ok);
  int32_t bare_ok = test_parse_export_bare();
  printf("export_bare_ok=%d\n", bare_ok);
  int32_t fixture_ok = test_parse_fixture_file();
  printf("fixture_ok=%d\n", fixture_ok);
  int32_t ty_ok = test_parse_ptr_array_types();
  printf("ptr_array_ok=%d\n", ty_ok);
  int32_t fi_ok = test_parse_field_index();
  printf("field_index_ok=%d\n", fi_ok);
  int32_t lit_ok = test_parse_struct_lit();
  printf("struct_lit_ok=%d\n", lit_ok);
  int32_t bc_ok = test_parse_break_continue();
  printf("break_continue_ok=%d\n", bc_ok);
  int32_t str_ok = test_parse_string_lit();
  printf("string_ok=%d\n", str_ok);
  int32_t const_ok = test_parse_const();
  printf("const_ok=%d\n", const_ok);
  int32_t cgen_ok = test_cgen_emit();
  printf("cgen_ok=%d\n", cgen_ok);
  int32_t for_cgen_ok = test_cgen_for();
  printf("cgen_for_ok=%d\n", for_cgen_ok);
  int32_t logic_ok = test_cgen_logic();
  printf("cgen_logic_ok=%d\n", logic_ok);
  int32_t string_cgen_ok = test_cgen_string();
  printf("cgen_string_ok=%d\n", string_cgen_ok);
  int32_t cgen_const_ok = test_cgen_const();
  printf("cgen_const_ok=%d\n", cgen_const_ok);
  int32_t cgen_struct_ok = test_cgen_struct();
  printf("cgen_struct_ok=%d\n", cgen_struct_ok);
  int32_t cgen_ptr_ok = test_cgen_ptr();
  printf("cgen_ptr_ok=%d\n", cgen_ptr_ok);
  int32_t cast_ok = test_parse_cast();
  printf("cast_ok=%d\n", cast_ok);
  int32_t idx_as_ok = test_parse_index_assign();
  printf("index_assign_ok=%d\n", idx_as_ok);
  int32_t cgen_cast_ok = test_cgen_cast();
  printf("cgen_cast_ok=%d\n", cgen_cast_ok);
  int32_t cgen_void_ok = test_cgen_void();
  printf("cgen_void_ok=%d\n", cgen_void_ok);
  int32_t jsgen_ok = test_jsgen_emit();
  printf("jsgen_ok=%d\n", jsgen_ok);
  int32_t tc_ok = test_typecheck_ok();
  printf("typecheck_ok=%d\n", tc_ok);
  int32_t tc_bad = test_typecheck_bad();
  printf("typecheck_bad=%d\n", tc_bad);
  int32_t tc_av = test_typecheck_arity_void();
  printf("typecheck_arity_void=%d\n", tc_av);
  int32_t tc_dl = test_typecheck_dup_let();
  printf("typecheck_dup_let=%d\n", tc_dl);
  int32_t tc_dc = test_typecheck_dup_const();
  printf("typecheck_dup_const=%d\n", tc_dc);
  int32_t tc_au = test_typecheck_assign_unknown();
  printf("typecheck_assign_unknown=%d\n", tc_au);
  int32_t tc_bo = test_typecheck_break_outside();
  printf("typecheck_break_outside=%d\n", tc_bo);
  int32_t tc_bf = test_typecheck_bad_field();
  printf("typecheck_bad_field=%d\n", tc_bf);
  int32_t match_ok = test_parse_match();
  printf("match_ok=%d\n", match_ok);
  int32_t cgen_match_ok = test_cgen_match();
  printf("cgen_match_ok=%d\n", cgen_match_ok);
  int32_t tc_mc = test_typecheck_match_catchall();
  printf("typecheck_match_catchall=%d\n", tc_mc);
  int32_t elif_ok = test_parse_elif();
  printf("elif_ok=%d\n", elif_ok);
  int32_t fmt_ok = test_fmt_emit();
  printf("fmt_ok=%d\n", fmt_ok);
  int32_t resolve_ok = test_resolve_sibling();
  printf("resolve_ok=%d\n", resolve_ok);
  int32_t bundle_tc_ok = test_bundle_typecheck();
  printf("bundle_tc_ok=%d\n", bundle_tc_ok);
  int32_t bundle_ok = test_bundle_emit();
  printf("bundle_ok=%d\n", bundle_ok);
  if (lex_ok == 1 && parse_ok == 1 && for_ok == 1 && struct_ok == 1 && extern_ok == 1 && ie_ok == 1 && bare_ok == 1 && fixture_ok == 1 && ty_ok == 1 && fi_ok == 1 && lit_ok == 1 && bc_ok == 1 && str_ok == 1 && const_ok == 1 && cgen_ok == 1 && for_cgen_ok == 1 && logic_ok == 1 && string_cgen_ok == 1 && cgen_const_ok == 1 && cgen_struct_ok == 1 && cgen_ptr_ok == 1 && cast_ok == 1 && idx_as_ok == 1 && cgen_cast_ok == 1 && cgen_void_ok == 1 && jsgen_ok == 1 && tc_ok == 1 && tc_bad == 1 && tc_av == 1 && tc_dl == 1 && tc_dc == 1 && tc_au == 1 && tc_bo == 1 && tc_bf == 1 && match_ok == 1 && cgen_match_ok == 1 && tc_mc == 1 && elif_ok == 1 && fmt_ok == 1 && resolve_ok == 1 && bundle_tc_ok == 1 && bundle_ok == 1) {
  puts("flowc: PASS");
  return 0;
}
  puts("flowc: FAIL");
  return 1;
}


