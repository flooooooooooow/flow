#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
#include <complex.h>
#include <time.h>
#pragma clang diagnostic ignored "-Wint-conversion"
#pragma clang diagnostic ignored "-Wincompatible-pointer-types"
#if defined(__GNUC__) && !defined(__clang__)
#pragma GCC diagnostic ignored "-Wint-conversion"
#pragma GCC diagnostic ignored "-Wincompatible-pointer-types"
#endif
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

static inline int64_t __flowc_range_count(int64_t s, int64_t e, int64_t d) {
  if (d > 0 && e > s) { return (e - s + d - 1) / d; }
  if (d < 0 && e < s) { return (s - e - d - 1) / (0 - d); }
  return 0;
}
static inline int64_t __flowc_range_sum(int64_t s, int64_t e, int64_t d) {
  int64_t n = __flowc_range_count(s, e, d);
  return n * s + d * ((n * (n - 1)) / 2);
}
static inline int64_t __flowc_floordiv(int64_t a, int64_t b) {
  int64_t q = a / b; if ((a % b != 0) && ((a < 0) != (b < 0))) { q = q - 1; } return q;
}
static inline int64_t __flowc_range_sum_isect(int64_t s1, int64_t e1, int64_t d1, int64_t s2, int64_t e2, int64_t d2) {
  int64_t n1 = __flowc_range_count(s1, e1, d1); int64_t n2 = __flowc_range_count(s2, e2, d2);
  if (n1 == 0 || n2 == 0) { return 0; }
  int64_t p1 = d1 < 0 ? 0 - d1 : d1; int64_t p2 = d2 < 0 ? 0 - d2 : d2;
  int64_t lo1 = d1 > 0 ? s1 : s1 + d1 * (n1 - 1); int64_t lo2 = d2 > 0 ? s2 : s2 + d2 * (n2 - 1);
  int64_t hi1 = lo1 + p1 * (n1 - 1); int64_t hi2 = lo2 + p2 * (n2 - 1);
  int64_t a = p1; int64_t b = p2; int64_t x0 = 1; int64_t x1 = 0;
  while (b != 0) { int64_t q = a / b; int64_t t = a - q * b; a = b; b = t; t = x0 - q * x1; x0 = x1; x1 = t; }
  int64_t g = a; int64_t diff = lo2 - lo1;
  if (diff % g != 0) { return 0; }
  int64_t m = p2 / g; int64_t lcm = p1 * m;
  int64_t t = (int64_t)(((__int128)(diff / g) * (__int128)x0) % (__int128)m); if (t < 0) { t = t + m; }
  int64_t x = lo1 + p1 * t;
  int64_t lower = lo1 > lo2 ? lo1 : lo2; int64_t upper = hi1 < hi2 ? hi1 : hi2;
  if (lower > upper) { return 0; }
  int64_t first = x - __flowc_floordiv(x - lower, lcm) * lcm;
  if (first > upper) { return 0; }
  int64_t cnt = (upper - first) / lcm + 1;
  return cnt * first + lcm * ((cnt * (cnt - 1)) / 2);
}
static inline int64_t __flowc_range_sum_union(int64_t s1, int64_t e1, int64_t d1, int64_t s2, int64_t e2, int64_t d2) {
  return __flowc_range_sum(s1, e1, d1) + __flowc_range_sum(s2, e2, d2) - __flowc_range_sum_isect(s1, e1, d1, s2, e2, d2);
}
static inline const char* __flowc_str_of_i64(int64_t v) {
  char* r = (char*)malloc(32); if (r == 0) { return ""; }
  snprintf(r, 32, "%lld", (long long)v); return r;
}
static inline const char* __flowc_str_of_u64(uint64_t v) {
  char* r = (char*)malloc(32); if (r == 0) { return ""; }
  snprintf(r, 32, "%llu", (unsigned long long)v); return r;
}
static inline const char* __flowc_str_of_f64(double v) {
  char* r = (char*)malloc(64); if (r == 0) { return ""; }
  snprintf(r, 64, "%f", v); return r;
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
const int32_t KW_SHADER = 40;
const int32_t KW_HANDLE = 41;
const int32_t KW_WITH = 42;
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
  uint8_t shader_kw[6] = { 115, 104, 97, 100, 101, 114 };
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
  p = shader_kw;
  if (flowc_lex_ident_eq(src, start, end, p, 6) == 1) {
  return KW_SHADER;
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
const int32_t AST_SHADER = 46;
const int32_t AST_EFFECT = 47;
const int32_t AST_CAPABILITY = 48;
const int32_t AST_HANDLE = 49;
const int32_t AST_EFFECT_OP = 50;
const int32_t AST_TYPE_SPAN_MUTABLE = 1;
const int32_t AST_IDENT_SORT_MOD = 1;
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

void flowc_parser_report(Parser p, const char* path);
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
int32_t flowc_parse_range_bound(Parser* p);
int32_t flowc_parse_range_tail(Parser* p, int32_t args);
int32_t flowc_parse_binop_kind(Parser p);
int32_t flowc_parse_binop_prec(int32_t op);
int32_t flowc_parse_binop_rhs(Parser* p, int32_t min_prec, int32_t lhs);
int32_t flowc_parse_expr(Parser* p);
int32_t flowc_parse_apply_pipe(Parser* p, int32_t left, int32_t right);
int32_t flowc_parse_if_chain(Parser* p, int32_t start);
int32_t flowc_parse_stmt(Parser* p);
int32_t flowc_parse_stmt_inner(Parser* p);
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
int32_t flowc_parse_effect(Parser* p, int32_t is_capability);
int32_t flowc_parse_capability(Parser* p, int32_t x);
int32_t flowc_parse_handle(Parser* p);
int32_t flowc_parse_program(Parser* p);
int32_t flowc_parse_is_enum_const(uint8_t* src, int32_t ns, int32_t ne, int32_t es, int32_t ee, int32_t vs, int32_t ve);
void flowc_parse_resolve_enum_arms(Parser* p);
void flowc_parser_report(Parser p, const char* path) {
  int32_t n = (((p).cur).end - ((p).cur).start);
  uint8_t* text = (uint8_t*)((((p).lex).input + ((p).cur).start));
  if (((p).cur).kind == TOK_EOF) {
  printf("%s:%d:%d: parse error at end of file\n", path, ((p).cur).line, ((p).cur).col);
  return;
}
  printf("%s:%d:%d: parse error at '%.*s'\n", path, ((p).cur).line, ((p).cur).col, n, text);
  if (((p).cur).kind == TOK_KEYWORD) {
  printf("%s:%d:%d: note: '%.*s' is a reserved word and cannot be used as a name\n", path, ((p).cur).line, ((p).cur).col, n, text);
}
}

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
  __flowc_tail: ;
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
  {
  __auto_type __flowc_targ0 = p;
  p = __flowc_targ0;
  goto __flowc_tail;
  }
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
  int32_t saw_mut = 0;
  if (flowc_parser_check_kw(p[0], KW_MUT) == 1) {
  saw_mut = 1;
  flowc_parser_advance(p);
}
  int32_t inner = flowc_parse_type(p);
  if (inner == AST_NONE) {
  return AST_NONE;
}
  (((p[0]).arena).nodes[id]).a = inner;
  if (saw_mut == 1 && flowc_parser_span_is(p[0], start, end, "span") == 1) {
  if (flowc_ast_type_set_span_mutable((&(p[0]).arena), id, 1) != 0) {
  (p[0]).err = 1;
  return AST_NONE;
}
}
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
  int32_t range_sum = 0;
  if (flowc_parser_check(p[0], TOK_RPAREN) == 0) {
  int32_t first = flowc_parse_expr(p);
  args = flowc_ast_chain_push((&(p[0]).arena), args, first);
  if (flowc_parser_check(p[0], TOK_DOTDOT) == 1 && flowc_parser_span_is(p[0], name_s, name_e, "sum") == 1) {
  args = flowc_parse_range_tail(p, args);
  if ((p[0]).err != 0) {
  return AST_NONE;
}
  range_sum = 2;
  if (flowc_parser_check(p[0], TOK_BAR) == 1 || flowc_parser_check(p[0], TOK_AMP) == 1) {
  range_sum = 3;
  if (flowc_parser_check(p[0], TOK_AMP) == 1) {
  range_sum = 4;
}
  flowc_parser_advance(p);
  int32_t lo2 = flowc_parse_range_bound(p);
  if (lo2 == AST_NONE) {
  return AST_NONE;
}
  args = flowc_ast_chain_push((&(p[0]).arena), args, lo2);
  if (flowc_parser_check(p[0], TOK_DOTDOT) == 0) {
  (p[0]).err = 1;
  return AST_NONE;
}
  args = flowc_parse_range_tail(p, args);
  if ((p[0]).err != 0) {
  return AST_NONE;
}
}
}
  while (range_sum == 0 && flowc_parser_check(p[0], TOK_COMMA) == 1) {
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
  if (range_sum > 0) {
  (((p[0]).arena).nodes[call]).ival = range_sum;
}
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
  int32_t repeat_n = AST_NONE;
  if (flowc_parser_check(p[0], TOK_RBRACK) == 0) {
  int32_t first = flowc_parse_expr(p);
  elems = flowc_ast_chain_push((&(p[0]).arena), elems, first);
  if (flowc_parser_check(p[0], TOK_SEMI) == 1) {
  flowc_parser_advance(p);
  repeat_n = flowc_parse_expr(p);
  if (repeat_n == AST_NONE) {
  return AST_NONE;
}
}
  while (repeat_n == AST_NONE && flowc_parser_check(p[0], TOK_COMMA) == 1) {
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
  (((p[0]).arena).nodes[id]).b = repeat_n;
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

int32_t flowc_parse_range_bound(Parser* p) {
  int32_t lhs = flowc_parse_cast(p);
  if (lhs == AST_NONE) {
  return AST_NONE;
}
  return flowc_parse_binop_rhs(p, 6, lhs);
}

int32_t flowc_parse_range_tail(Parser* p, int32_t args) {
  int32_t out = args;
  flowc_parser_advance(p);
  int32_t hi = flowc_parse_range_bound(p);
  if (hi == AST_NONE) {
  (p[0]).err = 1;
  return out;
}
  out = flowc_ast_chain_push((&(p[0]).arena), out, hi);
  if (flowc_parser_check(p[0], TOK_IDENT) == 1 && flowc_parser_span_is(p[0], ((p[0]).cur).start, ((p[0]).cur).end, "step") == 1) {
  flowc_parser_advance(p);
  int32_t st = flowc_parse_range_bound(p);
  if (st == AST_NONE) {
  (p[0]).err = 1;
  return out;
}
  out = flowc_ast_chain_push((&(p[0]).arena), out, st);
  return out;
}
  int32_t one = flowc_ast_alloc((&(p[0]).arena), AST_INT, 0, 0);
  if (one == AST_NONE) {
  (p[0]).err = 1;
  return out;
}
  (((p[0]).arena).nodes[one]).name_start = 0;
  (((p[0]).arena).nodes[one]).name_end = 0;
  (((p[0]).arena).nodes[one]).ival = 1;
  out = flowc_ast_chain_push((&(p[0]).arena), out, one);
  return out;
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
  if (op == TOK_BAR) {
  return 3;
}
  if (op == TOK_CARET) {
  return 4;
}
  if (op == TOK_AMP) {
  return 5;
}
  if (op == TOK_EQEQ || op == TOK_NE) {
  return 6;
}
  if (op == TOK_LT || op == TOK_LE || op == TOK_GT || op == TOK_GE || op == TOK_IN) {
  return 7;
}
  if (op == TOK_SHL || op == TOK_SHR) {
  return 8;
}
  if (op == TOK_PLUS || op == TOK_MINUS) {
  return 9;
}
  if (op == TOK_STAR || op == TOK_SLASH || op == TOK_PERCENT) {
  return 10;
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
  (((p[0]).arena).nodes[mnode]).ival = AST_IDENT_SORT_MOD;
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
  int32_t max_iter = 0;
  while (flowc_parser_check(p[0], TOK_AT) == 1) {
  flowc_parser_advance(p);
  int32_t is_bound = 0;
  if (flowc_parser_check(p[0], TOK_IDENT) == 1) {
  if (flowc_parser_span_is(p[0], ((p[0]).cur).start, ((p[0]).cur).end, "max_iterations") == 1) {
  is_bound = 1;
}
  flowc_parser_advance(p);
}
  if (flowc_parser_check(p[0], TOK_LPAREN) == 1) {
  if (is_bound == 1) {
  flowc_parser_advance(p);
  if (flowc_parser_check(p[0], TOK_INT) == 1) {
  max_iter = flowc_parse_int_span(((p[0]).lex).input, ((p[0]).cur).start, ((p[0]).cur).end);
  flowc_parser_advance(p);
}
  if (flowc_parser_eat(p, TOK_RPAREN) == 0) {
  return AST_NONE;
}
} else {
  flowc_parser_skip_paren_block(p);
}
}
}
  int32_t st = flowc_parse_stmt_inner(p);
  if (st != AST_NONE && max_iter > 0) {
  if ((((p[0]).arena).nodes[st]).kind == AST_WHILE) {
  (((p[0]).arena).nodes[st]).ival = max_iter;
}
}
  return st;
}

int32_t flowc_parse_stmt_inner(Parser* p) {
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
  if (flowc_token_is_kw((p[0]).cur, KW_NOT) == 1 || flowc_token_is_kw((p[0]).cur, KW_DBG) == 1) {
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
  if (flowc_parser_check_kw(p[0], KW_HANDLE) == 1) {
  return flowc_parse_handle(p);
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

int32_t flowc_parse_effect(Parser* p, int32_t is_capability) {
  int32_t start = ((p[0]).cur).start;
  flowc_parser_advance(p);
  if (flowc_parser_check(p[0], TOK_IDENT) == 0) {
  (p[0]).err = 1;
  return AST_NONE;
}
  int32_t name_start = ((p[0]).cur).start;
  int32_t name_end = ((p[0]).cur).end;
  flowc_parser_advance(p);
  if (flowc_parser_check(p[0], TOK_LBRACE) == 0) {
  (p[0]).err = 1;
  return AST_NONE;
}
  flowc_parser_advance(p);
  int32_t ops = AST_NONE;
  while (flowc_parser_check(p[0], TOK_RBRACE) == 0 && flowc_parser_check(p[0], TOK_EOF) == 0) {
  if (flowc_parser_check(p[0], TOK_IDENT) == 0) {
  (p[0]).err = 1;
  return AST_NONE;
}
  int32_t op_start = ((p[0]).cur).start;
  int32_t op_end = ((p[0]).cur).end;
  flowc_parser_advance(p);
  if (flowc_parser_check(p[0], TOK_LPAREN) == 0) {
  (p[0]).err = 1;
  return AST_NONE;
}
  flowc_parser_advance(p);
  int32_t params = AST_NONE;
  while (flowc_parser_check(p[0], TOK_RPAREN) == 0 && flowc_parser_check(p[0], TOK_EOF) == 0) {
  int32_t pname_start = (-1);
  int32_t pname_end = (-1);
  if (flowc_parser_check(p[0], TOK_IDENT) == 1) {
  pname_start = ((p[0]).cur).start;
  pname_end = ((p[0]).cur).end;
  flowc_parser_advance(p);
  if (flowc_parser_check(p[0], TOK_COLON) == 1) {
  flowc_parser_advance(p);
} else {
  pname_start = (-1);
  pname_end = (-1);
}
}
  int32_t ty = flowc_parse_type(p);
  if (ty == AST_NONE) {
  (p[0]).err = 1;
  return AST_NONE;
}
  int32_t param_id = flowc_ast_alloc((&(p[0]).arena), AST_PARAM, pname_start, ((p[0]).cur).start);
  if (param_id != AST_NONE) {
  (((p[0]).arena).nodes[param_id]).name_start = pname_start;
  (((p[0]).arena).nodes[param_id]).name_end = pname_end;
  (((p[0]).arena).nodes[param_id]).a = ty;
  params = flowc_ast_chain_push((&(p[0]).arena), params, param_id);
}
  if (flowc_parser_check(p[0], TOK_COMMA) == 1) {
  flowc_parser_advance(p);
} else {
  break;
}
}
  if (flowc_parser_check(p[0], TOK_RPAREN) == 1) {
  flowc_parser_advance(p);
}
  int32_t ret_ty = AST_NONE;
  if (flowc_parser_check(p[0], TOK_ARROW) == 1) {
  flowc_parser_advance(p);
  ret_ty = flowc_parse_type(p);
}
  int32_t op_id = flowc_ast_alloc((&(p[0]).arena), AST_EFFECT_OP, op_start, ((p[0]).cur).start);
  if (op_id != AST_NONE) {
  (((p[0]).arena).nodes[op_id]).name_start = op_start;
  (((p[0]).arena).nodes[op_id]).name_end = op_end;
  (((p[0]).arena).nodes[op_id]).a = params;
  (((p[0]).arena).nodes[op_id]).b = ret_ty;
  ops = flowc_ast_chain_push((&(p[0]).arena), ops, op_id);
}
  if (flowc_parser_check(p[0], TOK_SEMI) == 1 || flowc_parser_check(p[0], TOK_COMMA) == 1) {
  flowc_parser_advance(p);
}
}
  if (flowc_parser_check(p[0], TOK_RBRACE) == 1) {
  flowc_parser_advance(p);
}
  int32_t kind = AST_EFFECT;
  if (is_capability == 1) {
  kind = AST_CAPABILITY;
}
  int32_t id = flowc_ast_alloc((&(p[0]).arena), kind, start, ((p[0]).cur).start);
  if (id != AST_NONE) {
  (((p[0]).arena).nodes[id]).name_start = name_start;
  (((p[0]).arena).nodes[id]).name_end = name_end;
  (((p[0]).arena).nodes[id]).a = ops;
}
  return id;
}

int32_t flowc_parse_capability(Parser* p, int32_t x) {
  return flowc_parse_effect(p, 1);
}

int32_t flowc_parse_handle(Parser* p) {
  int32_t start = ((p[0]).cur).start;
  flowc_parser_advance(p);
  int32_t body = flowc_parse_stmt(p);
  if (flowc_parser_check_kw(p[0], KW_WITH) == 0) {
  (p[0]).err = 1;
  return AST_NONE;
}
  flowc_parser_advance(p);
  int32_t eff = flowc_parse_expr(p);
  int32_t id = flowc_ast_alloc((&(p[0]).arena), AST_HANDLE, start, ((p[0]).cur).start);
  if (id != AST_NONE) {
  (((p[0]).arena).nodes[id]).a = body;
  (((p[0]).arena).nodes[id]).b = eff;
}
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
  if (flowc_parser_check_kw(p[0], KW_SHADER) == 1) {
  int32_t shader_start = ((p[0]).cur).start;
  flowc_parser_advance(p);
  if (flowc_parser_check(p[0], TOK_IDENT) == 1) {
  flowc_parser_advance(p);
}
  if (flowc_parser_check(p[0], TOK_IDENT) == 1) {
  flowc_parser_advance(p);
}
  flowc_parser_skip_brace_block(p);
  item = flowc_ast_alloc((&(p[0]).arena), AST_SHADER, shader_start, ((p[0]).cur).start);
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
  flowc_parse_resolve_enum_arms(p);
  return id;
}

int32_t flowc_parse_is_enum_const(uint8_t* src, int32_t ns, int32_t ne, int32_t es, int32_t ee, int32_t vs, int32_t ve) {
  int32_t el = (ee - es);
  int32_t vl = (ve - vs);
  if ((ne - ns) != ((el + 1) + vl)) {
  return 0;
}
  int32_t i = 0;
  while (i < el) {
  if (src[(ns + i)] != src[(es + i)]) {
  return 0;
}
  i = (i + 1);
}
  if (src[(ns + el)] != 95) {
  return 0;
}
  i = 0;
  while (i < vl) {
  if (src[(((ns + el) + 1) + i)] != src[(vs + i)]) {
  return 0;
}
  i = (i + 1);
}
  return 1;
}

void flowc_parse_resolve_enum_arms(Parser* p) {
  uint8_t* src = (uint8_t*)(((p[0]).lex).input);
  int32_t n = ((p[0]).arena).len;
  int32_t i = 0;
  while (i < n) {
  if ((((p[0]).arena).nodes[i]).kind == AST_MATCH_ARM && (((p[0]).arena).nodes[i]).ival == 2) {
  int32_t ns = (((p[0]).arena).nodes[i]).name_start;
  int32_t ne = (((p[0]).arena).nodes[i]).name_end;
  int32_t hit = 0;
  int32_t j = 0;
  while (j < n && hit == 0) {
  if ((((p[0]).arena).nodes[j]).kind == AST_ENUM) {
  int32_t es = (((p[0]).arena).nodes[j]).name_start;
  int32_t ee = (((p[0]).arena).nodes[j]).name_end;
  int32_t v = (((p[0]).arena).nodes[j]).a;
  while (v != AST_NONE && hit == 0) {
  if (flowc_parse_is_enum_const(src, ns, ne, es, ee, (((p[0]).arena).nodes[v]).name_start, (((p[0]).arena).nodes[v]).name_end) == 1) {
  hit = 1;
}
  v = (((p[0]).arena).nodes[v]).next;
}
}
  j = (j + 1);
}
  if (hit == 1) {
  int32_t pat = flowc_ast_alloc((&(p[0]).arena), AST_IDENT, ns, ne);
  if (pat != AST_NONE) {
  (((p[0]).arena).nodes[pat]).name_start = ns;
  (((p[0]).arena).nodes[pat]).name_end = ne;
  (((p[0]).arena).nodes[i]).a = pat;
  (((p[0]).arena).nodes[i]).ival = 0;
}
}
}
  i = (i + 1);
}
}


static const int32_t FLOWC_IO_SEEK_SET = 0;
static const int32_t FLOWC_IO_SEEK_END = 2;

void flowc_fuse_pipelines(AstArena* arena, uint8_t* src);
void flowc_fuse_pipelines(AstArena* arena, uint8_t* src) {
  int32_t id = 0;
  int32_t len = (arena[0]).len;
  while (id < len) {
  AstNode node = (arena[0]).nodes[id];
  if ((node).kind == AST_CALL) {
  int32_t ns = (node).name_start;
  int32_t ne = (node).name_end;
  int32_t is_scale = 0;
  if ((ne - ns) == 9) {
  is_scale = 1;
}
  if (is_scale == 1) {
  int32_t first_arg = (node).a;
  if (first_arg != AST_NONE) {
  if (((arena[0]).nodes[first_arg]).kind == AST_CALL) {
  int32_t ins = ((arena[0]).nodes[first_arg]).name_start;
  int32_t ine = ((arena[0]).nodes[first_arg]).name_end;
  if ((ine - ins) == 9) {
  int32_t inner_a = ((arena[0]).nodes[first_arg]).a;
  if (inner_a != AST_NONE) {
  int32_t inner_n = ((arena[0]).nodes[inner_a]).next;
  if (inner_n != AST_NONE) {
  int32_t inner_val = ((arena[0]).nodes[inner_n]).next;
  int32_t outer_a = (node).a;
  int32_t outer_n = ((arena[0]).nodes[outer_a]).next;
  if (outer_n != AST_NONE) {
  int32_t outer_val = ((arena[0]).nodes[outer_n]).next;
  if (inner_val != AST_NONE && outer_val != AST_NONE) {
  int32_t binop_id = flowc_ast_alloc(arena, AST_BINOP, 0, 0);
  ((arena[0]).nodes[binop_id]).a = inner_val;
  ((arena[0]).nodes[binop_id]).b = outer_val;
  ((arena[0]).nodes[binop_id]).ival = 26;
  ((arena[0]).nodes[id]).a = inner_a;
  ((arena[0]).nodes[inner_a]).next = inner_n;
  ((arena[0]).nodes[inner_n]).next = binop_id;
  ((arena[0]).nodes[binop_id]).next = AST_NONE;
}
}
}
}
}
}
}
}
}
  id = (id + 1);
}
}


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
  int32_t* defer_ids;
  int32_t defer_len;
  int32_t loop_defer_base;
  int32_t tail_fn;
} CgenBuf;

static const int32_t FLOWC_PRIM_UNKNOWN = 0;
static const int32_t FLOWC_PRIM_STRING = 1;
static const int32_t FLOWC_PRIM_F64 = 2;
static const int32_t FLOWC_PRIM_I64 = 3;
static const int32_t FLOWC_PRIM_U64 = 4;
static const int32_t FLOWC_PRIM_U32 = 5;
static const int32_t FLOWC_PRIM_I32 = 6;
static const int32_t FLOWC_PRIM_BOOL = 7;
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
int32_t flowc_cgen_is_sized_array(AstArena arena, uint8_t* src, int32_t ty);
int32_t flowc_cgen_array_base(AstArena arena, uint8_t* src, int32_t ty);
void flowc_cgen_emit_array_dims(CgenBuf* w, AstArena arena, uint8_t* src, int32_t ty);
void flowc_cgen_put_type_mangle(CgenBuf* w, AstArena arena, uint8_t* src, int32_t ty);
void flowc_cgen_put_array_ret_name(CgenBuf* w, AstArena arena, uint8_t* src, int32_t ty);
void flowc_cgen_emit_array_ret_typedef(CgenBuf* w, AstArena arena, uint8_t* src, int32_t ty);
int32_t flowc_cgen_fn_returns_array(AstArena arena, uint8_t* src, int32_t fn);
int32_t flowc_cgen_sig_returns_array(CgenBuf* w, uint8_t* src, int32_t ns, int32_t ne);
void flowc_cgen_put_array_dest(CgenBuf* w, uint8_t* src, int32_t dest_mode, int32_t ns, int32_t ne);
void flowc_cgen_emit_array_fill(CgenBuf* w, AstArena arena, uint8_t* src, int32_t dest_mode, int32_t ns, int32_t ne, int32_t init);
int32_t flowc_cgen_array_lit_is_init(AstArena arena, uint8_t* src, int32_t ty, int32_t init);
void flowc_cgen_emit_ret_type(CgenBuf* w, AstArena arena, uint8_t* src, int32_t ret_ty);
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
int32_t flowc_cgen_find_let(AstArena arena, uint8_t* src, int32_t node, int32_t use_id, int32_t best, int32_t depth);
int32_t flowc_cgen_scoped_decl(CgenBuf* w, AstArena arena, uint8_t* src, int32_t id);
int32_t flowc_cgen_find_const(AstArena arena, uint8_t* src, int32_t id);
int32_t flowc_cgen_decl_type(AstArena arena, int32_t decl);
int32_t flowc_cgen_find_struct(AstArena arena, uint8_t* src, int32_t start, int32_t end);
int32_t flowc_cgen_expr_type_node(CgenBuf* w, AstArena arena, uint8_t* src, int32_t id);
int32_t flowc_cgen_expr_is_ptr(CgenBuf* w, AstArena arena, uint8_t* src, int32_t id);
int32_t flowc_cgen_expr_is_string(CgenBuf* w, AstArena arena, uint8_t* src, int32_t id);
int32_t flowc_cgen_ident_is_string(CgenBuf* w, AstArena arena, uint8_t* src, int32_t id);
int32_t flowc_cgen_is_str_concat(CgenBuf* w, AstArena arena, uint8_t* src, int32_t id);
int32_t flowc_cgen_prim_of_type(AstArena arena, uint8_t* src, int32_t ty);
int32_t flowc_cgen_sig_ctype_is(CgenBuf* w, int32_t off, const char* lit);
int32_t flowc_cgen_ident_prim(CgenBuf* w, AstArena arena, uint8_t* src, int32_t id);
int32_t flowc_cgen_expr_prim(CgenBuf* w, AstArena arena, uint8_t* src, int32_t id);
const char* flowc_cgen_prim_fmt(int32_t k);
void flowc_cgen_emit_concat_operand(CgenBuf* w, AstArena arena, uint8_t* src, int32_t id);
int32_t flowc_cgen_sig_put(AstArena arena, uint8_t* src, uint8_t* buf, int32_t cap, int32_t len, int32_t fn, int32_t rt);
int32_t flowc_cgen_binop_needs_parens(int32_t op);
int32_t flowc_cgen_c_prec(int32_t op);
void flowc_cgen_emit_binop_child(CgenBuf* w, AstArena arena, uint8_t* src, int32_t child, int32_t parent_op, int32_t is_right);
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
void flowc_cgen_emit_defers_to(CgenBuf* w, AstArena arena, uint8_t* src, int32_t base);
void flowc_cgen_emit_scoped_stmts(CgenBuf* w, AstArena arena, uint8_t* src, int32_t first);
void flowc_cgen_emit_block(CgenBuf* w, AstArena arena, uint8_t* src, int32_t id);
void flowc_cgen_emit_stmt(CgenBuf* w, AstArena arena, uint8_t* src, int32_t id);
void flowc_cgen_emit_param(CgenBuf* w, AstArena arena, uint8_t* src, int32_t id);
int32_t flowc_cgen_is_cli_main(AstArena arena, uint8_t* src, int32_t id);
int32_t flowc_cgen_is_libc_fn(AstArena arena, uint8_t* src, int32_t id);
void flowc_cgen_emit_fn(CgenBuf* w, AstArena arena, uint8_t* src, int32_t id);
int32_t flowc_cgen_is_self_call(AstArena arena, uint8_t* src, int32_t fn, int32_t call);
int32_t flowc_cgen_has_self_tail_call(AstArena arena, uint8_t* src, int32_t fn);
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
  return (CgenBuf){ .out = out, .cap = cap, .len = 0, .err = 0, .sigs = NULL, .sigs_len = 0, .cembed_names = NULL, .cembed_offs = NULL, .cembed_lens = NULL, .cembed_count = 0, .cap_starts = NULL, .cap_ends = NULL, .cap_count = 0, .in_lambda = 0, .lambda_cap_lambda = NULL, .lambda_cap_start = NULL, .lambda_cap_end = NULL, .lambda_cap_count = 0, .mono_tp_starts = NULL, .mono_tp_ends = NULL, .mono_tp_concrete = NULL, .mono_ntp = 0, .cur_fn = AST_NONE, .defer_ids = NULL, .defer_len = 0, .loop_defer_base = 0, .tail_fn = AST_NONE };
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
int32_t flowc_cgen_ident_is_string(CgenBuf* w, AstArena arena, uint8_t* src, int32_t id);
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
  if (flowc_cgen_span_is(src, start, end, "I") == 1) {
  flowc_cgen_puts(w, "_flow_I");
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

int32_t flowc_cgen_is_sized_array(AstArena arena, uint8_t* src, int32_t ty) {
  if (ty == AST_NONE) {
  return 0;
}
  if (((arena).nodes[ty]).kind != AST_TYPE) {
  return 0;
}
  if (((arena).nodes[ty]).a == AST_NONE || ((arena).nodes[ty]).ival <= 0) {
  return 0;
}
  return flowc_cgen_span_is(src, ((arena).nodes[ty]).name_start, ((arena).nodes[ty]).name_end, "array");
}

int32_t flowc_cgen_array_base(AstArena arena, uint8_t* src, int32_t ty) {
  int32_t t = ty;
  while (flowc_cgen_is_sized_array(arena, src, t) == 1) {
  t = ((arena).nodes[t]).a;
}
  return t;
}

void flowc_cgen_emit_array_dims(CgenBuf* w, AstArena arena, uint8_t* src, int32_t ty) {
  int32_t t = ty;
  while (flowc_cgen_is_sized_array(arena, src, t) == 1) {
  flowc_cgen_putc(w, 91);
  flowc_cgen_put_i32(w, ((arena).nodes[t]).ival);
  flowc_cgen_putc(w, 93);
  t = ((arena).nodes[t]).a;
}
}

void flowc_cgen_put_type_mangle(CgenBuf* w, AstArena arena, uint8_t* src, int32_t ty) {
  if (ty == AST_NONE || ((arena).nodes[ty]).kind != AST_TYPE) {
  flowc_cgen_puts(w, "i32");
  return;
}
  if (flowc_cgen_is_sized_array(arena, src, ty) == 1) {
  flowc_cgen_put_type_mangle(w, arena, src, ((arena).nodes[ty]).a);
  flowc_cgen_putc(w, 95);
  flowc_cgen_put_i32(w, ((arena).nodes[ty]).ival);
  return;
}
  flowc_cgen_put_span(w, src, ((arena).nodes[ty]).name_start, ((arena).nodes[ty]).name_end);
  int32_t ta = ((arena).nodes[ty]).a;
  while (ta != AST_NONE) {
  flowc_cgen_putc(w, 95);
  flowc_cgen_put_type_mangle(w, arena, src, ta);
  ta = ((arena).nodes[ta]).next;
}
}

void flowc_cgen_put_array_ret_name(CgenBuf* w, AstArena arena, uint8_t* src, int32_t ty) {
  flowc_cgen_puts(w, "__flowc_arr_");
  flowc_cgen_put_type_mangle(w, arena, src, ty);
}

void flowc_cgen_emit_array_ret_typedef(CgenBuf* w, AstArena arena, uint8_t* src, int32_t ty) {
  flowc_cgen_puts(w, "#ifndef ");
  flowc_cgen_put_array_ret_name(w, arena, src, ty);
  flowc_cgen_puts(w, "_DEFINED\n#define ");
  flowc_cgen_put_array_ret_name(w, arena, src, ty);
  flowc_cgen_puts(w, "_DEFINED\ntypedef struct { ");
  flowc_cgen_emit_type(w, arena, src, flowc_cgen_array_base(arena, src, ty));
  flowc_cgen_puts(w, " v");
  flowc_cgen_emit_array_dims(w, arena, src, ty);
  flowc_cgen_puts(w, "; } ");
  flowc_cgen_put_array_ret_name(w, arena, src, ty);
  flowc_cgen_puts(w, ";\n#endif\n");
}

int32_t flowc_cgen_fn_returns_array(AstArena arena, uint8_t* src, int32_t fn) {
  if (fn == AST_NONE) {
  return 0;
}
  return flowc_cgen_is_sized_array(arena, src, ((arena).nodes[fn]).b);
}

int32_t flowc_cgen_sig_returns_array(CgenBuf* w, uint8_t* src, int32_t ns, int32_t ne) {
  int32_t off = flowc_cgen_sig_find((w[0]).sigs, (w[0]).sigs_len, src, ns, ne);
  if (off < 0) {
  return 0;
}
  const char* want = "__flowc_arr_";
  uint8_t* wp = (uint8_t*)(want);
  int32_t i = 0;
  while (i < 12) {
  if ((off + i) >= (w[0]).sigs_len) {
  return 0;
}
  if ((w[0]).sigs[(off + i)] != wp[i]) {
  return 0;
}
  i = (i + 1);
}
  return 1;
}

void flowc_cgen_put_array_dest(CgenBuf* w, uint8_t* src, int32_t dest_mode, int32_t ns, int32_t ne) {
  if (dest_mode == 1) {
  flowc_cgen_puts(w, "__flowc_ret.v");
  return;
}
  flowc_cgen_put_ident(w, src, ns, ne);
}

void flowc_cgen_emit_array_fill(CgenBuf* w, AstArena arena, uint8_t* src, int32_t dest_mode, int32_t ns, int32_t ne, int32_t init) {
  if (init != AST_NONE && ((arena).nodes[init]).kind == AST_ARRAY_LIT && ((arena).nodes[init]).b == AST_NONE) {
  int32_t el = ((arena).nodes[init]).a;
  int32_t idx = 0;
  while (el != AST_NONE) {
  flowc_cgen_puts(w, "  memcpy(");
  flowc_cgen_put_array_dest(w, src, dest_mode, ns, ne);
  flowc_cgen_putc(w, 91);
  flowc_cgen_put_i32(w, idx);
  flowc_cgen_puts(w, "], ");
  flowc_cgen_emit_expr(w, arena, src, el);
  flowc_cgen_puts(w, ", sizeof(");
  flowc_cgen_put_array_dest(w, src, dest_mode, ns, ne);
  flowc_cgen_putc(w, 91);
  flowc_cgen_put_i32(w, idx);
  flowc_cgen_puts(w, "]));\n");
  idx = (idx + 1);
  el = ((arena).nodes[el]).next;
}
  return;
}
  flowc_cgen_puts(w, "  memcpy(");
  flowc_cgen_put_array_dest(w, src, dest_mode, ns, ne);
  flowc_cgen_puts(w, ", ");
  flowc_cgen_emit_expr(w, arena, src, init);
  flowc_cgen_puts(w, ", sizeof(");
  flowc_cgen_put_array_dest(w, src, dest_mode, ns, ne);
  flowc_cgen_puts(w, "));\n");
}

int32_t flowc_cgen_array_lit_is_init(AstArena arena, uint8_t* src, int32_t ty, int32_t init) {
  if (init == AST_NONE || ((arena).nodes[init]).kind != AST_ARRAY_LIT) {
  return 0;
}
  if (((arena).nodes[init]).b != AST_NONE) {
  return 1;
}
  if (flowc_cgen_is_sized_array(arena, src, ((arena).nodes[ty]).a) == 0) {
  return 1;
}
  int32_t el = ((arena).nodes[init]).a;
  while (el != AST_NONE) {
  if (((arena).nodes[el]).kind != AST_ARRAY_LIT) {
  return 0;
}
  el = ((arena).nodes[el]).next;
}
  return 1;
}

void flowc_cgen_emit_ret_type(CgenBuf* w, AstArena arena, uint8_t* src, int32_t ret_ty) {
  if (ret_ty == AST_NONE) {
  flowc_cgen_puts(w, "void");
  return;
}
  if (flowc_cgen_is_sized_array(arena, src, ret_ty) == 1) {
  flowc_cgen_put_array_ret_name(w, arena, src, ret_ty);
  return;
}
  if (((arena).nodes[ret_ty]).kind == AST_TYPE && (((arena).nodes[ret_ty]).ival == (-1) || ((arena).nodes[ret_ty]).ival == (-2))) {
  flowc_cgen_puts(w, "void*");
  return;
}
  flowc_cgen_emit_type(w, arena, src, ret_ty);
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

int32_t flowc_cgen_find_let(AstArena arena, uint8_t* src, int32_t node, int32_t use_id, int32_t best, int32_t depth) {
  int32_t b = best;
  int32_t cur = node;
  int32_t use_pos = ((arena).nodes[use_id]).name_start;
  int32_t ns = ((arena).nodes[use_id]).name_start;
  int32_t ne = ((arena).nodes[use_id]).name_end;
  while (cur != AST_NONE) {
  if (cur < 0 || cur >= (arena).len || depth > 400) {
  return b;
}
  int32_t k = ((arena).nodes[cur]).kind;
  int32_t descend = 1;
  if (k == AST_TYPE) {
  descend = 0;
}
  if (k == AST_BLOCK && ((arena).nodes[cur]).end > ((arena).nodes[cur]).start) {
  if (use_pos < ((arena).nodes[cur]).start || use_pos >= ((arena).nodes[cur]).end) {
  descend = 0;
}
}
  if (k == AST_LET && ((arena).nodes[cur]).end <= use_pos) {
  if (flowc_cgen_span_eq(src, ns, ne, ((arena).nodes[cur]).name_start, ((arena).nodes[cur]).name_end) == 1) {
  if (b == AST_NONE || ((arena).nodes[cur]).start > ((arena).nodes[b]).start) {
  b = cur;
}
}
}
  if (k == AST_FN && use_pos >= ((arena).nodes[cur]).start && use_pos < ((arena).nodes[cur]).end) {
  int32_t prm = ((arena).nodes[cur]).a;
  while (prm != AST_NONE && prm >= 0 && prm < (arena).len) {
  if (((arena).nodes[prm]).kind == AST_PARAM) {
  if (flowc_cgen_span_eq(src, ns, ne, ((arena).nodes[prm]).name_start, ((arena).nodes[prm]).name_end) == 1) {
  if (b == AST_NONE || ((arena).nodes[prm]).start > ((arena).nodes[b]).start) {
  b = prm;
}
}
}
  prm = ((arena).nodes[prm]).next;
}
}
  if (descend == 1) {
  b = flowc_cgen_find_let(arena, src, ((arena).nodes[cur]).a, use_id, b, (depth + 1));
  b = flowc_cgen_find_let(arena, src, ((arena).nodes[cur]).b, use_id, b, (depth + 1));
  b = flowc_cgen_find_let(arena, src, ((arena).nodes[cur]).c, use_id, b, (depth + 1));
}
  cur = ((arena).nodes[cur]).next;
}
  return b;
}

int32_t flowc_cgen_scoped_decl(CgenBuf* w, AstArena arena, uint8_t* src, int32_t id) {
  int32_t fn = (w[0]).cur_fn;
  if (fn == AST_NONE || id == AST_NONE) {
  return AST_NONE;
}
  if (((arena).nodes[id]).kind != AST_IDENT) {
  return AST_NONE;
}
  int32_t use_pos = ((arena).nodes[id]).name_start;
  if (use_pos < ((arena).nodes[fn]).start || use_pos >= ((arena).nodes[fn]).end) {
  return AST_NONE;
}
  int32_t found = flowc_cgen_find_let(arena, src, ((arena).nodes[fn]).c, id, AST_NONE, 0);
  if (found != AST_NONE) {
  return found;
}
  int32_t ns = ((arena).nodes[id]).name_start;
  int32_t ne = ((arena).nodes[id]).name_end;
  int32_t prm = ((arena).nodes[fn]).a;
  while (prm != AST_NONE) {
  if (((arena).nodes[prm]).kind == AST_PARAM) {
  if (flowc_cgen_span_eq(src, ns, ne, ((arena).nodes[prm]).name_start, ((arena).nodes[prm]).name_end) == 1) {
  return prm;
}
}
  prm = ((arena).nodes[prm]).next;
}
  return AST_NONE;
}

int32_t flowc_cgen_find_const(AstArena arena, uint8_t* src, int32_t id) {
  int32_t ns = ((arena).nodes[id]).name_start;
  int32_t ne = ((arena).nodes[id]).name_end;
  int32_t i = 0;
  while (i < (arena).len) {
  if (((arena).nodes[i]).kind == AST_CONST) {
  if (flowc_cgen_span_eq(src, ns, ne, ((arena).nodes[i]).name_start, ((arena).nodes[i]).name_end) == 1) {
  return i;
}
}
  i = (i + 1);
}
  return AST_NONE;
}

int32_t flowc_cgen_decl_type(AstArena arena, int32_t decl) {
  if (decl == AST_NONE) {
  return AST_NONE;
}
  int32_t ty = ((arena).nodes[decl]).a;
  if (ty != AST_NONE) {
  return ty;
}
  if (((arena).nodes[decl]).kind != AST_LET) {
  return AST_NONE;
}
  int32_t init = ((arena).nodes[decl]).b;
  if (init == AST_NONE) {
  return AST_NONE;
}
  if (((arena).nodes[init]).kind == AST_CAST) {
  return ((arena).nodes[init]).b;
}
  if (((arena).nodes[init]).kind == AST_STRUCT_LIT) {
  return init;
}
  return AST_NONE;
}

int32_t flowc_cgen_find_struct(AstArena arena, uint8_t* src, int32_t start, int32_t end) {
  if (end <= start) {
  return AST_NONE;
}
  int32_t i = 0;
  while (i < (arena).len) {
  if (((arena).nodes[i]).kind == AST_STRUCT) {
  if (flowc_cgen_span_eq(src, start, end, ((arena).nodes[i]).name_start, ((arena).nodes[i]).name_end) == 1) {
  return i;
}
}
  i = (i + 1);
}
  return AST_NONE;
}

int32_t flowc_cgen_expr_type_node(CgenBuf* w, AstArena arena, uint8_t* src, int32_t id) {
  if (id == AST_NONE) {
  return AST_NONE;
}
  int32_t kind = ((arena).nodes[id]).kind;
  if (kind == AST_IDENT) {
  int32_t decl = flowc_cgen_scoped_decl(w, arena, src, id);
  if (decl != AST_NONE) {
  return flowc_cgen_decl_type(arena, decl);
}
  int32_t c = flowc_cgen_find_const(arena, src, id);
  if (c != AST_NONE) {
  return ((arena).nodes[c]).a;
}
  return AST_NONE;
}
  if (kind == AST_FIELD_ACCESS) {
  int32_t bt = flowc_cgen_expr_type_node(w, arena, src, ((arena).nodes[id]).a);
  if (bt == AST_NONE) {
  return AST_NONE;
}
  if (((arena).nodes[bt]).kind == AST_TYPE && ((arena).nodes[bt]).a != AST_NONE) {
  if (flowc_cgen_span_is(src, ((arena).nodes[bt]).name_start, ((arena).nodes[bt]).name_end, "ptr") == 1) {
  bt = ((arena).nodes[bt]).a;
}
}
  int32_t st = flowc_cgen_find_struct(arena, src, ((arena).nodes[bt]).name_start, ((arena).nodes[bt]).name_end);
  if (st == AST_NONE) {
  return AST_NONE;
}
  if (((arena).nodes[st]).b != AST_NONE) {
  return AST_NONE;
}
  int32_t f = ((arena).nodes[st]).a;
  while (f != AST_NONE) {
  if (((arena).nodes[f]).kind == AST_FIELD) {
  if (flowc_cgen_span_eq(src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end, ((arena).nodes[f]).name_start, ((arena).nodes[f]).name_end) == 1) {
  return ((arena).nodes[f]).a;
}
}
  f = ((arena).nodes[f]).next;
}
  return AST_NONE;
}
  return AST_NONE;
}

int32_t flowc_cgen_expr_is_ptr(CgenBuf* w, AstArena arena, uint8_t* src, int32_t id) {
  int32_t ty = flowc_cgen_expr_type_node(w, arena, src, id);
  if (ty == AST_NONE) {
  return 0;
}
  if (((arena).nodes[ty]).kind != AST_TYPE) {
  return 0;
}
  return flowc_cgen_span_is(src, ((arena).nodes[ty]).name_start, ((arena).nodes[ty]).name_end, "ptr");
}

int32_t flowc_cgen_expr_is_string(CgenBuf* w, AstArena arena, uint8_t* src, int32_t id) {
  __flowc_tail: ;
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
  {
  __auto_type __flowc_targ0 = w;
  __auto_type __flowc_targ1 = arena;
  __auto_type __flowc_targ2 = src;
  __auto_type __flowc_targ3 = ((arena).nodes[id]).b;
  w = __flowc_targ0;
  arena = __flowc_targ1;
  src = __flowc_targ2;
  id = __flowc_targ3;
  goto __flowc_tail;
  }
}
  if (kind == AST_CALL) {
  int32_t fn = flowc_cgen_find_fn(arena, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  if (fn != AST_NONE) {
  return flowc_cgen_type_is_string(arena, src, ((arena).nodes[fn]).b);
}
  return flowc_cgen_sig_is_string(w, arena, src, id);
}
  if (kind == AST_IDENT) {
  return flowc_cgen_ident_is_string(w, arena, src, id);
}
  if (kind == AST_FIELD_ACCESS) {
  return flowc_cgen_type_is_string(arena, src, flowc_cgen_expr_type_node(w, arena, src, id));
}
  return 0;
}

int32_t flowc_cgen_ident_is_string(CgenBuf* w, AstArena arena, uint8_t* src, int32_t id) {
  int32_t decl = flowc_cgen_scoped_decl(w, arena, src, id);
  if (decl != AST_NONE) {
  if (((arena).nodes[decl]).a != AST_NONE) {
  return flowc_cgen_type_is_string(arena, src, ((arena).nodes[decl]).a);
}
  if (((arena).nodes[decl]).kind == AST_LET) {
  return flowc_cgen_expr_is_string(w, arena, src, ((arena).nodes[decl]).b);
}
  return 0;
}
  int32_t cdecl = flowc_cgen_find_const(arena, src, id);
  if (cdecl != AST_NONE) {
  return flowc_cgen_type_is_string(arena, src, ((arena).nodes[cdecl]).a);
}
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

int32_t flowc_cgen_prim_of_type(AstArena arena, uint8_t* src, int32_t ty) {
  if (ty == AST_NONE) {
  return FLOWC_PRIM_UNKNOWN;
}
  if (((arena).nodes[ty]).kind != AST_TYPE) {
  return FLOWC_PRIM_UNKNOWN;
}
  if (((arena).nodes[ty]).a != AST_NONE) {
  return FLOWC_PRIM_UNKNOWN;
}
  int32_t s = ((arena).nodes[ty]).name_start;
  int32_t e = ((arena).nodes[ty]).name_end;
  if (flowc_cgen_span_is(src, s, e, "string") == 1) {
  return FLOWC_PRIM_STRING;
}
  if (flowc_cgen_span_is(src, s, e, "f64") == 1 || flowc_cgen_span_is(src, s, e, "f32") == 1) {
  return FLOWC_PRIM_F64;
}
  if (flowc_cgen_span_is(src, s, e, "i64") == 1 || flowc_cgen_span_is(src, s, e, "isize") == 1) {
  return FLOWC_PRIM_I64;
}
  if (flowc_cgen_span_is(src, s, e, "u64") == 1 || flowc_cgen_span_is(src, s, e, "usize") == 1) {
  return FLOWC_PRIM_U64;
}
  if (flowc_cgen_span_is(src, s, e, "u32") == 1) {
  return FLOWC_PRIM_U32;
}
  if (flowc_cgen_span_is(src, s, e, "bool") == 1) {
  return FLOWC_PRIM_BOOL;
}
  if (flowc_cgen_span_is(src, s, e, "i32") == 1 || flowc_cgen_span_is(src, s, e, "i16") == 1) {
  return FLOWC_PRIM_I32;
}
  if (flowc_cgen_span_is(src, s, e, "i8") == 1 || flowc_cgen_span_is(src, s, e, "u8") == 1) {
  return FLOWC_PRIM_I32;
}
  if (flowc_cgen_span_is(src, s, e, "u16") == 1) {
  return FLOWC_PRIM_I32;
}
  return FLOWC_PRIM_UNKNOWN;
}

int32_t flowc_cgen_sig_ctype_is(CgenBuf* w, int32_t off, const char* lit) {
  uint8_t* p = (uint8_t*)(lit);
  int32_t n = (int32_t)(strlen(lit));
  int32_t i = 0;
  while (i < n) {
  if ((off + i) >= (w[0]).sigs_len) {
  return 0;
}
  if ((w[0]).sigs[(off + i)] != p[i]) {
  return 0;
}
  i = (i + 1);
}
  if ((off + n) >= (w[0]).sigs_len) {
  return 0;
}
  if ((w[0]).sigs[(off + n)] != 0) {
  return 0;
}
  return 1;
}

int32_t flowc_cgen_expr_prim(CgenBuf* w, AstArena arena, uint8_t* src, int32_t id);
int32_t flowc_cgen_ident_prim(CgenBuf* w, AstArena arena, uint8_t* src, int32_t id) {
  int32_t decl = flowc_cgen_scoped_decl(w, arena, src, id);
  if (decl != AST_NONE) {
  if (((arena).nodes[decl]).a != AST_NONE) {
  return flowc_cgen_prim_of_type(arena, src, ((arena).nodes[decl]).a);
}
  if (((arena).nodes[decl]).kind == AST_LET) {
  return flowc_cgen_expr_prim(w, arena, src, ((arena).nodes[decl]).b);
}
  return FLOWC_PRIM_UNKNOWN;
}
  int32_t cdecl = flowc_cgen_find_const(arena, src, id);
  if (cdecl != AST_NONE) {
  return flowc_cgen_prim_of_type(arena, src, ((arena).nodes[cdecl]).a);
}
  int32_t ns = ((arena).nodes[id]).name_start;
  int32_t ne = ((arena).nodes[id]).name_end;
  int32_t kind = (0 - 1);
  int32_t i = 0;
  while (i < (arena).len) {
  if (((arena).nodes[i]).kind == AST_PARAM || ((arena).nodes[i]).kind == AST_LET) {
  if (flowc_cgen_span_eq(src, ns, ne, ((arena).nodes[i]).name_start, ((arena).nodes[i]).name_end) == 1) {
  int32_t k = flowc_cgen_prim_of_type(arena, src, ((arena).nodes[i]).a);
  if (kind < 0) {
  kind = k;
} else {
  if (kind != k) {
  return FLOWC_PRIM_UNKNOWN;
}
}
}
}
  i = (i + 1);
}
  if (kind < 0) {
  return FLOWC_PRIM_UNKNOWN;
}
  return kind;
}

int32_t flowc_cgen_expr_prim(CgenBuf* w, AstArena arena, uint8_t* src, int32_t id) {
  __flowc_tail: ;
  if (id == AST_NONE) {
  return FLOWC_PRIM_UNKNOWN;
}
  int32_t kind = ((arena).nodes[id]).kind;
  if (kind == AST_STRING) {
  return FLOWC_PRIM_STRING;
}
  if (kind == AST_FLOAT) {
  return FLOWC_PRIM_F64;
}
  if (kind == AST_INT) {
  return FLOWC_PRIM_I32;
}
  if (kind == AST_BOOL) {
  return FLOWC_PRIM_BOOL;
}
  if (kind == AST_CAST) {
  return flowc_cgen_prim_of_type(arena, src, ((arena).nodes[id]).b);
}
  if (kind == AST_IDENT) {
  return flowc_cgen_ident_prim(w, arena, src, id);
}
  if (kind == AST_FIELD_ACCESS) {
  return flowc_cgen_prim_of_type(arena, src, flowc_cgen_expr_type_node(w, arena, src, id));
}
  if (kind == AST_UNARY) {
  if (((arena).nodes[id]).ival == TOK_BANG) {
  return FLOWC_PRIM_BOOL;
}
  if (((arena).nodes[id]).ival == TOK_MINUS) {
  {
  __auto_type __flowc_targ0 = w;
  __auto_type __flowc_targ1 = arena;
  __auto_type __flowc_targ2 = src;
  __auto_type __flowc_targ3 = ((arena).nodes[id]).a;
  w = __flowc_targ0;
  arena = __flowc_targ1;
  src = __flowc_targ2;
  id = __flowc_targ3;
  goto __flowc_tail;
  }
}
  return FLOWC_PRIM_UNKNOWN;
}
  if (kind == AST_CALL) {
  int32_t fn = flowc_cgen_find_fn(arena, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  if (fn != AST_NONE) {
  return flowc_cgen_prim_of_type(arena, src, ((arena).nodes[fn]).b);
}
  int32_t off = flowc_cgen_sig_find((w[0]).sigs, (w[0]).sigs_len, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  if (off < 0) {
  return FLOWC_PRIM_UNKNOWN;
}
  if (flowc_cgen_sig_ctype_is(w, off, "const char*") == 1) {
  return FLOWC_PRIM_STRING;
}
  if (flowc_cgen_sig_ctype_is(w, off, "double") == 1 || flowc_cgen_sig_ctype_is(w, off, "float") == 1) {
  return FLOWC_PRIM_F64;
}
  if (flowc_cgen_sig_ctype_is(w, off, "int64_t") == 1) {
  return FLOWC_PRIM_I64;
}
  if (flowc_cgen_sig_ctype_is(w, off, "uint64_t") == 1) {
  return FLOWC_PRIM_U64;
}
  if (flowc_cgen_sig_ctype_is(w, off, "uint32_t") == 1) {
  return FLOWC_PRIM_U32;
}
  if (flowc_cgen_sig_ctype_is(w, off, "bool") == 1) {
  return FLOWC_PRIM_BOOL;
}
  if (flowc_cgen_sig_ctype_is(w, off, "int32_t") == 1) {
  return FLOWC_PRIM_I32;
}
  return FLOWC_PRIM_UNKNOWN;
}
  if (kind == AST_BINOP) {
  int32_t op = ((arena).nodes[id]).ival;
  if (op == TOK_EQEQ || op == TOK_NE || op == TOK_LT || op == TOK_LE || op == TOK_GT || op == TOK_GE) {
  return FLOWC_PRIM_BOOL;
}
  if (op == TOK_AMPAMP || op == TOK_BARBAR || op == TOK_IN) {
  return FLOWC_PRIM_BOOL;
}
  if (op == TOK_PLUS) {
  if (flowc_cgen_is_str_concat(w, arena, src, id) == 1) {
  return FLOWC_PRIM_STRING;
}
}
  int32_t l = flowc_cgen_expr_prim(w, arena, src, ((arena).nodes[id]).a);
  int32_t r = flowc_cgen_expr_prim(w, arena, src, ((arena).nodes[id]).b);
  if (op == TOK_SHL || op == TOK_SHR) {
  return l;
}
  if (l == FLOWC_PRIM_F64 || r == FLOWC_PRIM_F64) {
  return FLOWC_PRIM_F64;
}
  if (l == FLOWC_PRIM_UNKNOWN || r == FLOWC_PRIM_UNKNOWN) {
  return FLOWC_PRIM_UNKNOWN;
}
  if (l == FLOWC_PRIM_U64 || r == FLOWC_PRIM_U64) {
  return FLOWC_PRIM_U64;
}
  if (l == FLOWC_PRIM_I64 || r == FLOWC_PRIM_I64) {
  return FLOWC_PRIM_I64;
}
  if (l == FLOWC_PRIM_U32 || r == FLOWC_PRIM_U32) {
  return FLOWC_PRIM_U32;
}
  return FLOWC_PRIM_I32;
}
  return FLOWC_PRIM_UNKNOWN;
}

const char* flowc_cgen_prim_fmt(int32_t k) {
  if (k == FLOWC_PRIM_STRING) {
  return "%s";
}
  if (k == FLOWC_PRIM_F64) {
  return "%f";
}
  if (k == FLOWC_PRIM_I64) {
  return "%lld";
}
  if (k == FLOWC_PRIM_U64) {
  return "%llu";
}
  if (k == FLOWC_PRIM_U32) {
  return "%u";
}
  return "%d";
}

void flowc_cgen_emit_concat_operand(CgenBuf* w, AstArena arena, uint8_t* src, int32_t id) {
  if (flowc_cgen_expr_is_string(w, arena, src, id) == 1) {
  flowc_cgen_emit_expr(w, arena, src, id);
  return;
}
  int32_t k = flowc_cgen_expr_prim(w, arena, src, id);
  if (k == FLOWC_PRIM_BOOL) {
  flowc_cgen_puts(w, "((");
  flowc_cgen_emit_expr(w, arena, src, id);
  flowc_cgen_puts(w, ") ? \"true\" : \"false\")");
  return;
}
  if (k == FLOWC_PRIM_F64) {
  flowc_cgen_puts(w, "__flowc_str_of_f64((double)(");
  flowc_cgen_emit_expr(w, arena, src, id);
  flowc_cgen_puts(w, "))");
  return;
}
  if (k == FLOWC_PRIM_U64 || k == FLOWC_PRIM_U32) {
  flowc_cgen_puts(w, "__flowc_str_of_u64((uint64_t)(");
  flowc_cgen_emit_expr(w, arena, src, id);
  flowc_cgen_puts(w, "))");
  return;
}
  if (k == FLOWC_PRIM_I64 || k == FLOWC_PRIM_I32) {
  flowc_cgen_puts(w, "__flowc_str_of_i64((int64_t)(");
  flowc_cgen_emit_expr(w, arena, src, id);
  flowc_cgen_puts(w, "))");
  return;
}
  flowc_cgen_emit_expr(w, arena, src, id);
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
  if (flowc_cgen_is_sized_array(arena, src, rt) == 1) {
  flowc_cgen_put_array_ret_name((&tw), arena, src, rt);
} else {
  flowc_cgen_emit_type((&tw), arena, src, rt);
}
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

int32_t flowc_cgen_c_prec(int32_t op) {
  if (op == TOK_BARBAR) {
  return 1;
}
  if (op == TOK_AMPAMP) {
  return 2;
}
  if (op == TOK_BAR) {
  return 3;
}
  if (op == TOK_CARET) {
  return 4;
}
  if (op == TOK_AMP) {
  return 5;
}
  if (op == TOK_EQEQ || op == TOK_NE) {
  return 6;
}
  if (op == TOK_LT || op == TOK_LE || op == TOK_GT || op == TOK_GE) {
  return 7;
}
  if (op == TOK_SHL || op == TOK_SHR) {
  return 8;
}
  if (op == TOK_PLUS || op == TOK_MINUS) {
  return 9;
}
  if (op == TOK_STAR || op == TOK_SLASH || op == TOK_PERCENT) {
  return 10;
}
  return 0;
}

void flowc_cgen_emit_binop_child(CgenBuf* w, AstArena arena, uint8_t* src, int32_t child, int32_t parent_op, int32_t is_right) {
  int32_t needs_wrap = 0;
  if (((arena).nodes[child]).kind == AST_BINOP) {
  int32_t cop = ((arena).nodes[child]).ival;
  if (cop == TOK_IN) {
  needs_wrap = 1;
}
  if (cop != TOK_IN && flowc_cgen_binop_needs_parens(cop) == 0) {
  int32_t cp = flowc_cgen_c_prec(cop);
  int32_t pp = flowc_cgen_c_prec(parent_op);
  if (cp < pp) {
  needs_wrap = 1;
}
  if (cp == pp && is_right == 1) {
  needs_wrap = 1;
}
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
  const char* fmt = flowc_cgen_prim_fmt(flowc_cgen_expr_prim(w, arena, src, arg));
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
  __flowc_tail: ;
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
  {
  __auto_type __flowc_targ0 = arena;
  __auto_type __flowc_targ1 = src;
  __auto_type __flowc_targ2 = ((arena).nodes[id]).c;
  __auto_type __flowc_targ3 = buf;
  __auto_type __flowc_targ4 = count;
  __auto_type __flowc_targ5 = param_spans;
  __auto_type __flowc_targ6 = nparams2;
  arena = __flowc_targ0;
  src = __flowc_targ1;
  id = __flowc_targ2;
  buf = __flowc_targ3;
  count = __flowc_targ4;
  param_spans = __flowc_targ5;
  nparams = __flowc_targ6;
  goto __flowc_tail;
  }
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
  {
  __auto_type __flowc_targ0 = arena;
  __auto_type __flowc_targ1 = src;
  __auto_type __flowc_targ2 = ((arena).nodes[id]).next;
  __auto_type __flowc_targ3 = buf;
  __auto_type __flowc_targ4 = count;
  __auto_type __flowc_targ5 = param_spans;
  __auto_type __flowc_targ6 = nparams;
  arena = __flowc_targ0;
  src = __flowc_targ1;
  id = __flowc_targ2;
  buf = __flowc_targ3;
  count = __flowc_targ4;
  param_spans = __flowc_targ5;
  nparams = __flowc_targ6;
  goto __flowc_tail;
  }
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
  flowc_cgen_puts(w, "_env->");
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
  if (((arena).nodes[id]).ival == AST_IDENT_SORT_MOD) {
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
  has_snap = 1;
}
  ci = (ci + 1);
}
  if (has_snap == 1) {
  flowc_cgen_puts(w, "((lambda_");
  flowc_cgen_put_i32(w, lam_id);
  flowc_cgen_puts(w, "_closure){ .fn = &__flowc_lambda_");
  flowc_cgen_put_i32(w, lam_id);
  flowc_cgen_puts(w, ", .env = { ");
  ci = 0;
  int32_t first_snap = 1;
  while (ci < (w[0]).lambda_cap_count) {
  if ((w[0]).lambda_cap_lambda[ci] == lam_id) {
  if (first_snap == 0) {
  flowc_cgen_puts(w, ", ");
}
  first_snap = 0;
  flowc_cgen_putc(w, 46);
  flowc_cgen_put_span(w, src, (w[0]).lambda_cap_start[ci], (w[0]).lambda_cap_end[ci]);
  flowc_cgen_puts(w, " = ");
  if ((w[0]).in_lambda != 0) {
  flowc_cgen_puts(w, "_env->");
}
  flowc_cgen_put_span(w, src, (w[0]).lambda_cap_start[ci], (w[0]).lambda_cap_end[ci]);
}
  ci = (ci + 1);
}
  flowc_cgen_puts(w, " } })");
} else {
  flowc_cgen_puts(w, "&__flowc_lambda_");
  flowc_cgen_put_i32(w, lam_id);
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
  flowc_cgen_emit_concat_operand(w, arena, src, ((arena).nodes[id]).a);
  flowc_cgen_puts(w, ", ");
  flowc_cgen_emit_concat_operand(w, arena, src, ((arena).nodes[id]).b);
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
  flowc_cgen_emit_binop_child(w, arena, src, ((arena).nodes[id]).a, op, 0);
  flowc_cgen_emit_binop_op(w, op);
  flowc_cgen_emit_binop_child(w, arena, src, ((arena).nodes[id]).b, op, 1);
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
  if (((arena).nodes[((arena).nodes[id]).a]).kind == AST_BINOP) {
  flowc_cgen_putc(w, 40);
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_cgen_putc(w, 41);
} else {
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).a);
}
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
  int32_t rs_kind = ((arena).nodes[id]).ival;
  if (rs_kind >= 2 && rs_kind <= 4 && flowc_cgen_span_is(src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end, "sum") == 1) {
  flowc_cgen_puts(w, "((__typeof__((");
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_cgen_puts(w, ") + 0))");
  if (rs_kind == 2) {
  flowc_cgen_puts(w, "__flowc_range_sum(");
}
  if (rs_kind == 3) {
  flowc_cgen_puts(w, "__flowc_range_sum_union(");
}
  if (rs_kind == 4) {
  flowc_cgen_puts(w, "__flowc_range_sum_isect(");
}
  int32_t rarg = ((arena).nodes[id]).a;
  int32_t rfirst = 1;
  while (rarg != AST_NONE) {
  if (rfirst == 0) {
  flowc_cgen_puts(w, ", ");
}
  rfirst = 0;
  flowc_cgen_puts(w, "(int64_t)(");
  if (((arena).nodes[rarg]).kind == AST_INT && ((arena).nodes[rarg]).name_end == ((arena).nodes[rarg]).name_start) {
  flowc_cgen_put_i32(w, ((arena).nodes[rarg]).ival);
} else {
  flowc_cgen_emit_expr(w, arena, src, rarg);
}
  flowc_cgen_putc(w, 41);
  rarg = ((arena).nodes[rarg]).next;
}
  flowc_cgen_puts(w, "))");
  return;
}
  if (flowc_cgen_span_is(src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end, "flow_panic") == 1) {
  flowc_cgen_puts(w, "(fprintf(stderr, \"%s\\n\", ");
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_cgen_puts(w, "), exit(1))");
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
  if (((arena).nodes[id]).b != AST_NONE && flowc_cgen_span_is(src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end, "sizeof") == 1) {
  flowc_cgen_puts(w, "((int64_t)sizeof(");
  flowc_cgen_emit_type(w, arena, src, ((arena).nodes[id]).b);
  flowc_cgen_puts(w, "))");
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
  int32_t fn_id = AST_NONE;
  if (n_overloads > 1) {
  fn_id = flowc_cgen_resolve_overload(arena, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end, id);
  if (fn_id != AST_NONE) {
  flowc_cgen_put_mangled_fn(w, arena, src, fn_id);
} else {
  flowc_cgen_put_ident(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
}
} else {
  fn_id = flowc_cgen_find_fn(arena, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  if (fn_id != AST_NONE || flowc_cgen_is_libc_fn(arena, src, id) == 1) {
  flowc_cgen_put_ident(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
} else {
  int32_t is_closure = 0;
  int32_t ns = ((arena).nodes[id]).name_start;
  int32_t ne = ((arena).nodes[id]).name_end;
  int32_t vi = 0;
  while (vi < (arena).len) {
  if (((arena).nodes[vi]).kind == AST_LET) {
  if (flowc_cgen_span_eq(src, ns, ne, ((arena).nodes[vi]).name_start, ((arena).nodes[vi]).name_end) == 1) {
  int32_t init = ((arena).nodes[vi]).b;
  if (init != AST_NONE && ((arena).nodes[init]).kind == AST_FN) {
  int32_t lam_id = (0 - ((arena).nodes[init]).name_start);
  int32_t has_snap = 0;
  int32_t ci = 0;
  while (ci < (w[0]).lambda_cap_count) {
  if ((w[0]).lambda_cap_lambda[ci] == lam_id) {
  has_snap = 1;
}
  ci = (ci + 1);
}
  if (has_snap == 1) {
  is_closure = 1;
}
}
}
}
  vi = (vi + 1);
}
  if ((w[0]).in_lambda != 0 && flowc_cgen_is_captured(w, src, ns, ne) == 1) {
  flowc_cgen_puts(w, "_env->");
}
  flowc_cgen_put_ident(w, src, ns, ne);
  if (is_closure == 1) {
  flowc_cgen_puts(w, ".fn");
}
}
}
  flowc_cgen_putc(w, 40);
  int32_t is_closure_call = 0;
  if (fn_id == AST_NONE && flowc_cgen_is_libc_fn(arena, src, id) == 0) {
  int32_t ns = ((arena).nodes[id]).name_start;
  int32_t ne = ((arena).nodes[id]).name_end;
  int32_t vi = 0;
  while (vi < (arena).len) {
  if (((arena).nodes[vi]).kind == AST_LET) {
  if (flowc_cgen_span_eq(src, ns, ne, ((arena).nodes[vi]).name_start, ((arena).nodes[vi]).name_end) == 1) {
  int32_t init = ((arena).nodes[vi]).b;
  if (init != AST_NONE && ((arena).nodes[init]).kind == AST_FN) {
  int32_t lam_id = (0 - ((arena).nodes[init]).name_start);
  int32_t has_snap = 0;
  int32_t ci = 0;
  while (ci < (w[0]).lambda_cap_count) {
  if ((w[0]).lambda_cap_lambda[ci] == lam_id) {
  has_snap = 1;
}
  ci = (ci + 1);
}
  if (has_snap == 1) {
  is_closure_call = 1;
}
}
}
}
  vi = (vi + 1);
}
  if (is_closure_call == 1) {
  flowc_cgen_puts(w, "&");
  if ((w[0]).in_lambda != 0 && flowc_cgen_is_captured(w, src, ns, ne) == 1) {
  flowc_cgen_puts(w, "_env->");
}
  flowc_cgen_put_ident(w, src, ns, ne);
  flowc_cgen_puts(w, ".env");
}
}
  int32_t arg = ((arena).nodes[id]).a;
  int32_t first = 1;
  if (is_closure_call == 1) {
  first = 0;
}
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
  if (fn_id != AST_NONE) {
  if (flowc_cgen_fn_returns_array(arena, src, fn_id) == 1) {
  flowc_cgen_puts(w, ".v");
}
} else {
  if (flowc_cgen_sig_returns_array(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end) == 1) {
  flowc_cgen_puts(w, ".v");
}
}
  return;
}
  if (kind == AST_FIELD_ACCESS) {
  int32_t base = ((arena).nodes[id]).a;
  int32_t is_ptr = flowc_cgen_expr_is_ptr(w, arena, src, base);
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
  if (((arena).nodes[id]).b != AST_NONE) {
  flowc_cgen_puts(w, "{ [0 ... (");
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).b);
  flowc_cgen_puts(w, ") - 1] = (");
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_cgen_puts(w, ") }");
  return;
}
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

void flowc_cgen_emit_defers_to(CgenBuf* w, AstArena arena, uint8_t* src, int32_t base) {
  int32_t d = ((w[0]).defer_len - 1);
  while (d >= base) {
  flowc_cgen_puts(w, "  ");
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[(w[0]).defer_ids[d]]).a);
  flowc_cgen_puts(w, ";\n");
  d = (d - 1);
}
}

void flowc_cgen_emit_scoped_stmts(CgenBuf* w, AstArena arena, uint8_t* src, int32_t first) {
  if ((w[0]).defer_ids == NULL) {
  uint8_t* raw = (uint8_t*)(malloc(1024));
  (w[0]).defer_ids = raw;
  (w[0]).defer_len = 0;
}
  int32_t base = (w[0]).defer_len;
  int32_t last_kind = 0;
  int32_t st = first;
  while (st != AST_NONE) {
  last_kind = ((arena).nodes[st]).kind;
  if (last_kind == AST_DEFER) {
  if ((w[0]).defer_len < 256) {
  (w[0]).defer_ids[(w[0]).defer_len] = st;
  (w[0]).defer_len = ((w[0]).defer_len + 1);
}
} else {
  flowc_cgen_emit_stmt(w, arena, src, st);
}
  st = ((arena).nodes[st]).next;
}
  if (last_kind != AST_RETURN && last_kind != AST_BREAK && last_kind != AST_CONTINUE) {
  flowc_cgen_emit_defers_to(w, arena, src, base);
}
  (w[0]).defer_len = base;
}

void flowc_cgen_emit_block(CgenBuf* w, AstArena arena, uint8_t* src, int32_t id) {
  if (id == AST_NONE || (w[0]).err != 0) {
  return;
}
  flowc_cgen_puts(w, "{\n");
  flowc_cgen_emit_scoped_stmts(w, arena, src, ((arena).nodes[id]).a);
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
  flowc_cgen_emit_type(w, arena, src, flowc_cgen_array_base(arena, src, ty));
  flowc_cgen_putc(w, 32);
  flowc_cgen_put_ident(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  flowc_cgen_emit_array_dims(w, arena, src, ty);
  if (init == AST_NONE) {
  flowc_cgen_puts(w, ";\n");
  return;
}
  if (flowc_cgen_array_lit_is_init(arena, src, ty, init) == 1) {
  flowc_cgen_puts(w, " = ");
  flowc_cgen_emit_expr(w, arena, src, init);
  flowc_cgen_puts(w, ";\n");
  return;
}
  flowc_cgen_puts(w, ";\n");
  flowc_cgen_emit_array_fill(w, arena, src, 0, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end, init);
  return;
} else {
  int32_t wrote = 0;
  if (ty == AST_NONE) {
  wrote = flowc_cgen_write_lit_type(w, arena, src, init);
}
  if (wrote == 0) {
  if (init != AST_NONE && ((arena).nodes[init]).kind == AST_FN) {
  int32_t lam_id = (0 - ((arena).nodes[init]).name_start);
  int32_t has_snap = 0;
  int32_t ci = 0;
  while (ci < (w[0]).lambda_cap_count) {
  if ((w[0]).lambda_cap_lambda[ci] == lam_id) {
  has_snap = 1;
}
  ci = (ci + 1);
}
  if (has_snap == 1) {
  flowc_cgen_puts(w, "lambda_");
  flowc_cgen_put_i32(w, lam_id);
  flowc_cgen_puts(w, "_closure ");
  flowc_cgen_put_ident(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
} else {
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
  if (lam_param == AST_NONE) {
  flowc_cgen_puts(w, "void");
}
  while (lam_param != AST_NONE) {
  if (lam_first == 0) {
  flowc_cgen_puts(w, ", ");
}
  flowc_cgen_emit_type(w, arena, src, ((arena).nodes[lam_param]).b);
  lam_first = 0;
  lam_param = ((arena).nodes[lam_param]).next;
}
  flowc_cgen_putc(w, 41);
}
  flowc_cgen_puts(w, " = ");
  flowc_cgen_emit_expr(w, arena, src, init);
  flowc_cgen_puts(w, ";\n");
  return;
}
  if (ty != AST_NONE && ((arena).nodes[ty]).kind == AST_TYPE && (((arena).nodes[ty]).ival == (-1) || ((arena).nodes[ty]).ival == (-2))) {
  flowc_cgen_puts(w, "struct { ");
  flowc_cgen_emit_type(w, arena, src, ((arena).nodes[ty]).b);
  flowc_cgen_puts(w, " (*fn)(");
  int32_t cfn_param = ((arena).nodes[ty]).a;
  int32_t cfn_first = 1;
  flowc_cgen_puts(w, "void*");
  while (cfn_param != AST_NONE) {
  flowc_cgen_puts(w, ", ");
  flowc_cgen_emit_type(w, arena, src, cfn_param);
  cfn_first = 0;
  cfn_param = ((arena).nodes[cfn_param]).next;
}
  flowc_cgen_puts(w, "); void* env; } ");
  flowc_cgen_put_ident(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  if (init != AST_NONE && ((arena).nodes[init]).kind == AST_FN) {
  int32_t lam_id = (0 - ((arena).nodes[init]).name_start);
  flowc_cgen_puts(w, " = { .fn = (void*)&__flowc_lambda_");
  flowc_cgen_put_i32(w, lam_id);
  flowc_cgen_puts(w, ", .env = NULL };\n");
} else {
  flowc_cgen_puts(w, " = ");
  flowc_cgen_emit_expr(w, arena, src, init);
  flowc_cgen_puts(w, ";\n");
}
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
  flowc_cgen_emit_defers_to(w, arena, src, 0);
  flowc_cgen_puts(w, "  return;\n");
  return;
}
  int32_t ret_expr = ((arena).nodes[id]).a;
  if (((arena).nodes[ret_expr]).kind == AST_IDENT) {
  if (flowc_cgen_span_is(src, ((arena).nodes[ret_expr]).name_start, ((arena).nodes[ret_expr]).name_end, "void") == 1) {
  flowc_cgen_emit_defers_to(w, arena, src, 0);
  flowc_cgen_puts(w, "  return;\n");
  return;
}
}
  if ((w[0]).tail_fn != AST_NONE && (w[0]).tail_fn == (w[0]).cur_fn && (w[0]).in_lambda == 0 && (w[0]).defer_len == 0) {
  if (flowc_cgen_is_self_call(arena, src, (w[0]).cur_fn, ret_expr) == 1) {
  flowc_cgen_puts(w, "  {\n");
  int32_t targ = ((arena).nodes[ret_expr]).a;
  int32_t tk = 0;
  while (targ != AST_NONE) {
  flowc_cgen_puts(w, "  __auto_type __flowc_targ");
  flowc_cgen_put_i32(w, tk);
  flowc_cgen_puts(w, " = ");
  flowc_cgen_emit_expr(w, arena, src, targ);
  flowc_cgen_puts(w, ";\n");
  tk = (tk + 1);
  targ = ((arena).nodes[targ]).next;
}
  int32_t tparam = ((arena).nodes[(w[0]).cur_fn]).a;
  tk = 0;
  while (tparam != AST_NONE) {
  flowc_cgen_puts(w, "  ");
  flowc_cgen_put_span(w, src, ((arena).nodes[tparam]).name_start, ((arena).nodes[tparam]).name_end);
  flowc_cgen_puts(w, " = __flowc_targ");
  flowc_cgen_put_i32(w, tk);
  flowc_cgen_puts(w, ";\n");
  tk = (tk + 1);
  tparam = ((arena).nodes[tparam]).next;
}
  flowc_cgen_puts(w, "  goto __flowc_tail;\n  }\n");
  return;
}
}
  if ((w[0]).cur_fn != AST_NONE && (w[0]).in_lambda == 0) {
  int32_t fn_ret = ((arena).nodes[(w[0]).cur_fn]).b;
  if (flowc_cgen_is_sized_array(arena, src, fn_ret) == 1) {
  flowc_cgen_puts(w, "  { ");
  flowc_cgen_put_array_ret_name(w, arena, src, fn_ret);
  flowc_cgen_puts(w, " __flowc_ret");
  if (flowc_cgen_array_lit_is_init(arena, src, fn_ret, ret_expr) == 1) {
  flowc_cgen_puts(w, " = { ");
  flowc_cgen_emit_expr(w, arena, src, ret_expr);
  flowc_cgen_puts(w, " };\n");
} else {
  flowc_cgen_puts(w, ";\n");
  flowc_cgen_emit_array_fill(w, arena, src, 1, 0, 0, ret_expr);
}
  flowc_cgen_emit_defers_to(w, arena, src, 0);
  flowc_cgen_puts(w, "  return __flowc_ret; }\n");
  return;
}
}
  if ((w[0]).defer_len > 0) {
  flowc_cgen_puts(w, "  { __auto_type __flowc_ret = ");
  flowc_cgen_emit_expr(w, arena, src, ret_expr);
  flowc_cgen_puts(w, ";\n");
  flowc_cgen_emit_defers_to(w, arena, src, 0);
  flowc_cgen_puts(w, "  return __flowc_ret; }\n");
  return;
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
  flowc_cgen_emit_scoped_stmts(w, arena, src, ((arena).nodes[then_b]).a);
}
  if (((arena).nodes[id]).c != AST_NONE) {
  flowc_cgen_puts(w, "} else {\n");
  int32_t else_b = ((arena).nodes[id]).c;
  flowc_cgen_emit_scoped_stmts(w, arena, src, ((arena).nodes[else_b]).a);
  flowc_cgen_puts(w, "}\n");
} else {
  flowc_cgen_puts(w, "}\n");
}
  return;
}
  if (kind == AST_WHILE) {
  if (((arena).nodes[id]).ival > 0) {
  flowc_cgen_puts(w, "  { int32_t __flowc_iter_");
  flowc_cgen_put_i32(w, id);
  flowc_cgen_puts(w, " = 0;\n");
}
  flowc_cgen_puts(w, "  while (");
  flowc_cgen_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_cgen_puts(w, ") ");
  int32_t saved_wbase = (w[0]).loop_defer_base;
  (w[0]).loop_defer_base = (w[0]).defer_len;
  int32_t bound = ((arena).nodes[id]).ival;
  if (bound > 0) {
  flowc_cgen_puts(w, "{\n  if (__flowc_iter_");
  flowc_cgen_put_i32(w, id);
  flowc_cgen_puts(w, " >= ");
  flowc_cgen_put_i32(w, bound);
  flowc_cgen_puts(w, ") { fprintf(stderr, \"flow: while exceeded @max_iterations(");
  flowc_cgen_put_i32(w, bound);
  flowc_cgen_puts(w, ")\\n\"); abort(); }\n  __flowc_iter_");
  flowc_cgen_put_i32(w, id);
  flowc_cgen_puts(w, "++;\n");
}
  flowc_cgen_emit_block(w, arena, src, ((arena).nodes[id]).b);
  if (bound > 0) {
  flowc_cgen_puts(w, "}\n  }\n");
}
  (w[0]).loop_defer_base = saved_wbase;
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
  int32_t saved_fbase = (w[0]).loop_defer_base;
  (w[0]).loop_defer_base = (w[0]).defer_len;
  flowc_cgen_emit_block(w, arena, src, ((arena).nodes[id]).c);
  (w[0]).loop_defer_base = saved_fbase;
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
  flowc_cgen_emit_scoped_stmts(w, arena, src, ((arena).nodes[body]).a);
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
  flowc_cgen_emit_scoped_stmts(w, arena, src, ((arena).nodes[body]).a);
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
  flowc_cgen_emit_scoped_stmts(w, arena, src, ((arena).nodes[body]).a);
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
  flowc_cgen_emit_scoped_stmts(w, arena, src, ((arena).nodes[body]).a);
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
  flowc_cgen_emit_scoped_stmts(w, arena, src, ((arena).nodes[body]).a);
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
  flowc_cgen_emit_defers_to(w, arena, src, (w[0]).loop_defer_base);
  flowc_cgen_puts(w, "  break;\n");
  return;
}
  if (kind == AST_CONTINUE) {
  flowc_cgen_emit_defers_to(w, arena, src, (w[0]).loop_defer_base);
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
  if (flowc_cgen_is_sized_array(arena, src, ty) == 1) {
  if (flowc_cgen_is_sized_array(arena, src, ((arena).nodes[ty]).a) == 1) {
  flowc_cgen_emit_type(w, arena, src, flowc_cgen_array_base(arena, src, ty));
  flowc_cgen_putc(w, 32);
  flowc_cgen_put_ident(w, src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end);
  flowc_cgen_emit_array_dims(w, arena, src, ty);
  return;
}
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
  if (flowc_cgen_span_is(src, ns, ne, "strtoll") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "strtoul") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "strtoull") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "strtof") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "strtold") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "atol") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "atoll") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "labs") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "llabs") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "bsearch") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "atexit") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "memchr") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "strncat") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "strspn") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "strcspn") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "strpbrk") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "strtok") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "strerror") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "strdup") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "strndup") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "getchar") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "perror") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "round") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "trunc") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "fmin") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "fmax") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "hypot") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "cbrt") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "exp2") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "log1p") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "expm1") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "copysign") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "sinf") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "cosf") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "sqrtf") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "powf") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "expf") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "logf") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "fabsf") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "floorf") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "ceilf") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "roundf") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "difftime") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "mktime") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "gmtime") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "localtime") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "strftime") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "gmtime_r") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "localtime_r") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "clock_gettime") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "clock_getres") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "clock_gettime_nsec_np") == 1) {
  return 1;
}
  if (flowc_cgen_span_is(src, ns, ne, "nanosleep") == 1) {
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
  if (flowc_cgen_is_sized_array(arena, src, ret_ty) == 1) {
  flowc_cgen_emit_array_ret_typedef(w, arena, src, ret_ty);
}
  flowc_cgen_emit_ret_type(w, arena, src, ret_ty);
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
  if ((w[0]).mono_ntp == 0 && flowc_cgen_has_self_tail_call(arena, src, id) == 1) {
  (w[0]).tail_fn = id;
  flowc_cgen_puts(w, "{\n  __flowc_tail: ;\n");
  flowc_cgen_emit_scoped_stmts(w, arena, src, ((arena).nodes[((arena).nodes[id]).c]).a);
  flowc_cgen_puts(w, "}\n");
  (w[0]).tail_fn = AST_NONE;
  flowc_cgen_putc(w, 10);
  return;
}
  flowc_cgen_emit_block(w, arena, src, ((arena).nodes[id]).c);
  flowc_cgen_putc(w, 10);
}

int32_t flowc_cgen_is_self_call(AstArena arena, uint8_t* src, int32_t fn, int32_t call) {
  if (call == AST_NONE || ((arena).nodes[call]).kind != AST_CALL) {
  return 0;
}
  if (((arena).nodes[call]).b != AST_NONE || ((arena).nodes[call]).ival != 0) {
  return 0;
}
  if (flowc_cgen_span_eq(src, ((arena).nodes[call]).name_start, ((arena).nodes[call]).name_end, ((arena).nodes[fn]).name_start, ((arena).nodes[fn]).name_end) == 0) {
  return 0;
}
  if (flowc_ast_chain_len(arena, ((arena).nodes[call]).a) != flowc_ast_chain_len(arena, ((arena).nodes[fn]).a)) {
  return 0;
}
  if (flowc_cgen_count_overloads(arena, src, ((arena).nodes[fn]).name_start, ((arena).nodes[fn]).name_end) > 1) {
  return 0;
}
  return 1;
}

int32_t flowc_cgen_has_self_tail_call(AstArena arena, uint8_t* src, int32_t fn) {
  if (((arena).nodes[fn]).name_start < 0 || ((arena).nodes[fn]).ival != 0) {
  return 0;
}
  int32_t lo = ((arena).nodes[fn]).start;
  int32_t hi = ((arena).nodes[fn]).end;
  int32_t i = 0;
  while (i < (arena).len) {
  if (((arena).nodes[i]).kind == AST_RETURN && ((arena).nodes[i]).start >= lo && ((arena).nodes[i]).start < hi) {
  if (flowc_cgen_is_self_call(arena, src, fn, ((arena).nodes[i]).a) == 1) {
  return 1;
}
}
  i = (i + 1);
}
  return 0;
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
  if (flowc_cgen_is_sized_array(arena, src, ret_ty) == 1) {
  flowc_cgen_emit_array_ret_typedef(w, arena, src, ret_ty);
}
  flowc_cgen_emit_ret_type(w, arena, src, ret_ty);
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
  if (flowc_cgen_type_is_string(arena, src, ty) == 1) {
  flowc_cgen_puts(w, "char* const");
} else {
  if (ty != AST_NONE) {
  flowc_cgen_emit_type(w, arena, src, ty);
} else {
  flowc_cgen_puts(w, "int32_t");
}
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
  flowc_cgen_puts((&w), "#include <time.h>\n");
  flowc_cgen_puts((&w), "#pragma clang diagnostic ignored \"-Wint-conversion\"\n");
  flowc_cgen_puts((&w), "#pragma clang diagnostic ignored \"-Wincompatible-pointer-types\"\n");
  flowc_cgen_puts((&w), "#if defined(__GNUC__) && !defined(__clang__)\n");
  flowc_cgen_puts((&w), "#pragma GCC diagnostic ignored \"-Wint-conversion\"\n");
  flowc_cgen_puts((&w), "#pragma GCC diagnostic ignored \"-Wincompatible-pointer-types\"\n");
  flowc_cgen_puts((&w), "#endif\n");
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
  flowc_cgen_puts((&w), "static inline int64_t __flowc_range_count(int64_t s, int64_t e, int64_t d) {\n");
  flowc_cgen_puts((&w), "  if (d > 0 && e > s) { return (e - s + d - 1) / d; }\n");
  flowc_cgen_puts((&w), "  if (d < 0 && e < s) { return (s - e - d - 1) / (0 - d); }\n");
  flowc_cgen_puts((&w), "  return 0;\n");
  flowc_cgen_puts((&w), "}\n");
  flowc_cgen_puts((&w), "static inline int64_t __flowc_range_sum(int64_t s, int64_t e, int64_t d) {\n");
  flowc_cgen_puts((&w), "  int64_t n = __flowc_range_count(s, e, d);\n");
  flowc_cgen_puts((&w), "  return n * s + d * ((n * (n - 1)) / 2);\n");
  flowc_cgen_puts((&w), "}\n");
  flowc_cgen_puts((&w), "static inline int64_t __flowc_floordiv(int64_t a, int64_t b) {\n");
  flowc_cgen_puts((&w), "  int64_t q = a / b; if ((a % b != 0) && ((a < 0) != (b < 0))) { q = q - 1; } return q;\n");
  flowc_cgen_puts((&w), "}\n");
  flowc_cgen_puts((&w), "static inline int64_t __flowc_range_sum_isect(int64_t s1, int64_t e1, int64_t d1, int64_t s2, int64_t e2, int64_t d2) {\n");
  flowc_cgen_puts((&w), "  int64_t n1 = __flowc_range_count(s1, e1, d1); int64_t n2 = __flowc_range_count(s2, e2, d2);\n");
  flowc_cgen_puts((&w), "  if (n1 == 0 || n2 == 0) { return 0; }\n");
  flowc_cgen_puts((&w), "  int64_t p1 = d1 < 0 ? 0 - d1 : d1; int64_t p2 = d2 < 0 ? 0 - d2 : d2;\n");
  flowc_cgen_puts((&w), "  int64_t lo1 = d1 > 0 ? s1 : s1 + d1 * (n1 - 1); int64_t lo2 = d2 > 0 ? s2 : s2 + d2 * (n2 - 1);\n");
  flowc_cgen_puts((&w), "  int64_t hi1 = lo1 + p1 * (n1 - 1); int64_t hi2 = lo2 + p2 * (n2 - 1);\n");
  flowc_cgen_puts((&w), "  int64_t a = p1; int64_t b = p2; int64_t x0 = 1; int64_t x1 = 0;\n");
  flowc_cgen_puts((&w), "  while (b != 0) { int64_t q = a / b; int64_t t = a - q * b; a = b; b = t; t = x0 - q * x1; x0 = x1; x1 = t; }\n");
  flowc_cgen_puts((&w), "  int64_t g = a; int64_t diff = lo2 - lo1;\n");
  flowc_cgen_puts((&w), "  if (diff % g != 0) { return 0; }\n");
  flowc_cgen_puts((&w), "  int64_t m = p2 / g; int64_t lcm = p1 * m;\n");
  flowc_cgen_puts((&w), "  int64_t t = (int64_t)(((__int128)(diff / g) * (__int128)x0) % (__int128)m); if (t < 0) { t = t + m; }\n");
  flowc_cgen_puts((&w), "  int64_t x = lo1 + p1 * t;\n");
  flowc_cgen_puts((&w), "  int64_t lower = lo1 > lo2 ? lo1 : lo2; int64_t upper = hi1 < hi2 ? hi1 : hi2;\n");
  flowc_cgen_puts((&w), "  if (lower > upper) { return 0; }\n");
  flowc_cgen_puts((&w), "  int64_t first = x - __flowc_floordiv(x - lower, lcm) * lcm;\n");
  flowc_cgen_puts((&w), "  if (first > upper) { return 0; }\n");
  flowc_cgen_puts((&w), "  int64_t cnt = (upper - first) / lcm + 1;\n");
  flowc_cgen_puts((&w), "  return cnt * first + lcm * ((cnt * (cnt - 1)) / 2);\n");
  flowc_cgen_puts((&w), "}\n");
  flowc_cgen_puts((&w), "static inline int64_t __flowc_range_sum_union(int64_t s1, int64_t e1, int64_t d1, int64_t s2, int64_t e2, int64_t d2) {\n");
  flowc_cgen_puts((&w), "  return __flowc_range_sum(s1, e1, d1) + __flowc_range_sum(s2, e2, d2) - __flowc_range_sum_isect(s1, e1, d1, s2, e2, d2);\n");
  flowc_cgen_puts((&w), "}\n");
  flowc_cgen_puts((&w), "static inline const char* __flowc_str_of_i64(int64_t v) {\n");
  flowc_cgen_puts((&w), "  char* r = (char*)malloc(32); if (r == 0) { return \"\"; }\n");
  flowc_cgen_puts((&w), "  snprintf(r, 32, \"%lld\", (long long)v); return r;\n");
  flowc_cgen_puts((&w), "}\n");
  flowc_cgen_puts((&w), "static inline const char* __flowc_str_of_u64(uint64_t v) {\n");
  flowc_cgen_puts((&w), "  char* r = (char*)malloc(32); if (r == 0) { return \"\"; }\n");
  flowc_cgen_puts((&w), "  snprintf(r, 32, \"%llu\", (unsigned long long)v); return r;\n");
  flowc_cgen_puts((&w), "}\n");
  flowc_cgen_puts((&w), "static inline const char* __flowc_str_of_f64(double v) {\n");
  flowc_cgen_puts((&w), "  char* r = (char*)malloc(64); if (r == 0) { return \"\"; }\n");
  flowc_cgen_puts((&w), "  snprintf(r, 64, \"%f\", v); return r;\n");
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
  int32_t li2 = 0;
  while (li2 < (arena).len) {
  if (((arena).nodes[li2]).kind == AST_FN) {
  if (((arena).nodes[li2]).name_start < 0) {
  int32_t lam_id = (0 - ((arena).nodes[li2]).name_start);
  flowc_cgen_puts((&w), "typedef struct {\n");
  int32_t ci2 = 0;
  int32_t has_caps = 0;
  while (ci2 < (w).lambda_cap_count) {
  if ((w).lambda_cap_lambda[ci2] == lam_id) {
  int32_t vty = AST_NONE;
  int32_t vns = (w).lambda_cap_start[ci2];
  int32_t vne = (w).lambda_cap_end[ci2];
  int32_t vi = 0;
  while (vi < (arena).len) {
  if (((arena).nodes[vi]).kind == AST_LET || ((arena).nodes[vi]).kind == AST_PARAM) {
  if (flowc_cgen_span_eq(src, vns, vne, ((arena).nodes[vi]).name_start, ((arena).nodes[vi]).name_end) == 1) {
  vty = ((arena).nodes[vi]).a;
  if (((arena).nodes[vi]).kind == AST_PARAM && vty == AST_NONE) {
  vty = ((arena).nodes[vi]).b;
}
}
}
  vi = (vi + 1);
}
  flowc_cgen_puts((&w), "  ");
  if (vty != AST_NONE) {
  flowc_cgen_emit_type((&w), arena, src, vty);
} else {
  flowc_cgen_puts((&w), "int32_t");
}
  flowc_cgen_putc((&w), 32);
  flowc_cgen_put_span((&w), src, vns, vne);
  flowc_cgen_puts((&w), ";\n");
  has_caps = 1;
}
  ci2 = (ci2 + 1);
}
  flowc_cgen_puts((&w), "} lambda_");
  flowc_cgen_put_i32((&w), lam_id);
  flowc_cgen_puts((&w), "_env;\n");
  flowc_cgen_puts((&w), "typedef struct { ");
  int32_t ret_ty = ((arena).nodes[li2]).b;
  if (ret_ty == AST_NONE) {
  flowc_cgen_puts((&w), "void");
} else {
  flowc_cgen_emit_type((&w), arena, src, ret_ty);
}
  flowc_cgen_puts((&w), " (*fn)(");
  if (has_caps == 1) {
  flowc_cgen_puts((&w), "lambda_");
  flowc_cgen_put_i32((&w), lam_id);
  flowc_cgen_puts((&w), "_env*");
}
  int32_t param = ((arena).nodes[li2]).a;
  int32_t first = 1;
  if (has_caps == 1) {
  first = 0;
}
  if (param == AST_NONE && has_caps == 0) {
  flowc_cgen_puts((&w), "void");
}
  while (param != AST_NONE) {
  if (first == 0) {
  flowc_cgen_puts((&w), ", ");
}
  flowc_cgen_emit_type((&w), arena, src, ((arena).nodes[param]).b);
  first = 0;
  param = ((arena).nodes[param]).next;
}
  flowc_cgen_puts((&w), "); ");
  if (has_caps == 1) {
  flowc_cgen_puts((&w), "lambda_");
  flowc_cgen_put_i32((&w), lam_id);
  flowc_cgen_puts((&w), "_env env; ");
}
  flowc_cgen_puts((&w), "} lambda_");
  flowc_cgen_put_i32((&w), lam_id);
  flowc_cgen_puts((&w), "_closure;\n\n");
}
}
  li2 = (li2 + 1);
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
  if (((arena).nodes[id]).b != AST_NONE) {
  flowc_fmt_emit_expr(w, arena, src, ((arena).nodes[id]).a);
  flowc_fmt_puts(w, "; ");
  flowc_fmt_emit_expr(w, arena, src, ((arena).nodes[id]).b);
  flowc_fmt_putc(w, 93);
  return;
}
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


typedef struct ShBuf {
  uint8_t* buf;
  int32_t cap;
  int32_t len;
} ShBuf;

typedef struct ShCtx {
  uint8_t* p;
  int32_t n;
  int32_t pn;
  int32_t target;
  int32_t err;
  ShBuf* msg;
  int32_t* tk;
  int32_t* ts;
  int32_t* te;
  int32_t ntok;
  int32_t ti;
  int32_t* nk;
  int32_t* na;
  int32_t* nb;
  int32_t* nc;
  int32_t* nx;
  int32_t* s1;
  int32_t* e1;
  int32_t* nf;
  int32_t nn;
  int32_t* ys;
  int32_t* ye;
  int32_t ny;
  int32_t ybase;
  int32_t* vs;
  int32_t* ve;
  int32_t* vt;
  int32_t nv;
  int32_t* fns;
  int32_t* fne;
  int32_t* fbs;
  int32_t* fbe;
  int32_t* frt;
  int32_t* fp0;
  int32_t* fpn;
  int32_t nfn;
  int32_t* pas;
  int32_t* pae;
  int32_t* pat;
  int32_t npa;
  int32_t* fls;
  int32_t* fle;
  int32_t* flbs;
  int32_t* flbe;
  int32_t nfl;
} ShCtx;

const int32_t SH_METAL = 0;
const int32_t SH_WGSL = 1;
static const int32_t T_NUMBER = 1;
static const int32_t T_IDENT = 2;
static const int32_t T_OP = 3;
static const int32_t T_COMPARE = 4;
static const int32_t T_AND = 5;
static const int32_t T_OR = 6;
static const int32_t T_NOT = 7;
static const int32_t T_ASSIGN = 8;
static const int32_t T_LPAREN = 9;
static const int32_t T_RPAREN = 10;
static const int32_t T_LBRACE = 11;
static const int32_t T_RBRACE = 12;
static const int32_t T_COMMA = 13;
static const int32_t T_COLON = 14;
static const int32_t T_DOT = 15;
static const int32_t T_SEMI = 16;
static const int32_t T_NEWLINE = 17;
static const int32_t T_EOF = 18;
static const int32_t E_NUMBER = 1;
static const int32_t E_NAME = 2;
static const int32_t E_UNARY = 3;
static const int32_t E_BINARY = 4;
static const int32_t E_CALL = 5;
static const int32_t E_SWIZZLE = 6;
static const int32_t E_CAST = 7;
static const int32_t S_LET = 10;
static const int32_t S_ASSIGN = 11;
static const int32_t S_RETURN = 12;
static const int32_t S_IF = 13;
static const int32_t S_FOR = 14;
static const int32_t TY_FSL = 0;
static const int32_t TY_METAL = 9;
static const int32_t TY_WGSL = 18;
static const int32_t TY_CONSTS = 27;
ShBuf* flowc_shader_buf_new(int32_t cap);
void flowc_shader_buf_free(ShBuf* w);
void sh_putc(ShBuf* w, uint8_t c);
void flowc_shader_putc(ShBuf* w, uint8_t c);
void sh_puts(ShBuf* w, const char* s);
void sh_line(ShBuf* w, const char* s);
void sh_put_span(ShBuf* w, uint8_t* p, int32_t s, int32_t e);
void sh_rule(ShBuf* w, int32_t n);
void sh_pad(ShBuf* w, int32_t indent);
int32_t* sh_ints(int32_t n);
void sh_pool_add(ShCtx* c, const char* s);
void sh_pool_add_set(ShCtx* c, const char* a, const char* b, const char* d, const char* e, const char* f, const char* g, const char* h, const char* i, const char* j);
ShCtx* flowc_shader_ctx_new(uint8_t* src, int32_t n);
void flowc_shader_ctx_free(ShCtx* c);
int32_t flowc_shader_ctx_err(ShCtx* c);
ShBuf* flowc_shader_ctx_msg(ShCtx* c);
int32_t flowc_shader_fill_count(ShCtx* c);
void flowc_shader_put_fill_name(ShCtx* c, ShBuf* w, int32_t k);
int32_t flowc_shader_fill_named(ShCtx* c, int32_t k, uint8_t* name, int32_t nlen);
int32_t sh_err(ShCtx* c);
void sh_fail(ShCtx* c, const char* m);
int32_t sh_is_space(uint8_t c);
int32_t sh_is_word(uint8_t c);
int32_t sh_is_digit(uint8_t c);
int32_t sh_is_ident_start(uint8_t c);
int32_t sh_is_ident(uint8_t c);
int32_t sh_is_ret_ch(uint8_t c);
int32_t sh_lit_at(uint8_t* p, int32_t i, int32_t e, const char* lit);
int32_t sh_span_is(uint8_t* p, int32_t s, int32_t e, const char* lit);
int32_t sh_span_eq(uint8_t* p, int32_t a0, int32_t a1, int32_t b0, int32_t b1);
int32_t sh_skip_ws(uint8_t* p, int32_t i, int32_t e);
int32_t sh_fill_head_at(uint8_t* p, int32_t i, int32_t n, int32_t* out);
int32_t sh_fn_head_at(uint8_t* p, int32_t i, int32_t n, int32_t* out);
void sh_strip(uint8_t* p, int32_t* se);
int32_t sh_ty_span(ShCtx* c, int32_t s, int32_t e);
int32_t sh_brace_block(ShCtx* c, int32_t at);
int32_t sh_parse_params(ShCtx* c, int32_t s, int32_t e);
int32_t flowc_shader_extract(ShCtx* c);
int32_t flowc_shader_is_module(uint8_t* p, int32_t n);
int32_t flowc_shader_expand_in_place(uint8_t* buf, int32_t n, int32_t cap);
void sh_tok(ShCtx* c, int32_t kind, int32_t s, int32_t e);
void sh_tokenize(ShCtx* c, int32_t s, int32_t e);
const char* sh_kind_name(int32_t k);
int32_t sh_cur(ShCtx* c);
int32_t sh_cur_is(ShCtx* c, int32_t kind, const char* lit);
int32_t sh_advance(ShCtx* c);
int32_t sh_match(ShCtx* c, int32_t kind);
void sh_err_got(ShCtx* c, const char* head);
int32_t sh_expect(ShCtx* c, int32_t kind, const char* lit);
void sh_skip_nl(ShCtx* c);
int32_t sh_node(ShCtx* c, int32_t kind);
int32_t sh_node_tok(ShCtx* c, int32_t kind, int32_t t);
int32_t sh_binary(ShCtx* c, int32_t op, int32_t left, int32_t right);
int32_t sh_parse_stmts(ShCtx* c);
int32_t sh_parse_block(ShCtx* c);
int32_t sh_parse_stmt(ShCtx* c);
int32_t sh_parse_let(ShCtx* c);
int32_t sh_parse_body(ShCtx* c);
int32_t sh_parse_if(ShCtx* c);
int32_t sh_parse_for(ShCtx* c);
int32_t sh_parse_expr(ShCtx* c);
int32_t sh_parse_or(ShCtx* c);
int32_t sh_parse_and(ShCtx* c);
int32_t sh_parse_compare(ShCtx* c);
int32_t sh_parse_term(ShCtx* c);
int32_t sh_parse_factor(ShCtx* c);
int32_t sh_parse_unary(ShCtx* c);
int32_t sh_parse_postfix(ShCtx* c);
int32_t sh_parse_primary(ShCtx* c);
int32_t sh_parse_body_span(ShCtx* c, int32_t s, int32_t e);
int32_t sh_ty_is(ShCtx* c, int32_t h, const char* lit);
int32_t sh_ty_eq(ShCtx* c, int32_t a, int32_t b);
void sh_put_ty(ShCtx* c, ShBuf* w, int32_t h);
int32_t sh_ty_known(ShCtx* c, int32_t k);
int32_t sh_map_type(ShCtx* c, int32_t h);
int32_t sh_ty_named(ShCtx* c, int32_t s, int32_t e);
void sh_env_set(ShCtx* c, int32_t s, int32_t e, int32_t ty);
int32_t sh_env_get(ShCtx* c, int32_t s, int32_t e, int32_t dflt);
int32_t sh_find_fn(ShCtx* c, int32_t s, int32_t e);
int32_t sh_node_is(ShCtx* c, int32_t k, const char* lit);
int32_t sh_rank(ShCtx* c, int32_t h);
int32_t sh_is_metal_float_fn(ShCtx* c, int32_t k);
int32_t sh_is_wgsl_float_fn(ShCtx* c, int32_t k);
int32_t sh_guess(ShCtx* c, int32_t x);
int32_t sh_is_metal_builtin(ShCtx* c, int32_t k);
int32_t sh_is_wgsl_builtin(ShCtx* c, int32_t k);
void sh_put_name(ShCtx* c, ShBuf* w, int32_t k);
void sh_unknown_fn(ShCtx* c, int32_t x);
void sh_emit_call(ShCtx* c, ShBuf* w, int32_t x);
void sh_emit_expr(ShCtx* c, ShBuf* w, int32_t x);
int32_t sh_emit_stmts(ShCtx* c, ShBuf* w, int32_t head, int32_t indent);
int32_t sh_has_color_assign(ShCtx* c, int32_t head);
void sh_emit_fn(ShCtx* c, ShBuf* w, int32_t k);
void sh_emit_fill(ShCtx* c, ShBuf* w, int32_t k);
int32_t flowc_shader_gen(ShCtx* c, ShBuf* w, int32_t target, uint8_t* name, int32_t nlen, int32_t only);
void sh_prelude_metal(ShBuf* w);
void sh_prelude_wgsl(ShBuf* w);
ShBuf* flowc_shader_buf_new(int32_t cap) {
  ShBuf* w = (ShBuf*)((ShBuf*)(malloc(24)));
  (w[0]).buf = malloc((int64_t)((cap + 1)));
  (w[0]).cap = cap;
  (w[0]).len = 0;
  return w;
}

void flowc_shader_buf_free(ShBuf* w) {
  free((w[0]).buf);
  free((uint8_t*)(w));
}

void sh_putc(ShBuf* w, uint8_t c) {
  if ((w[0]).len >= (w[0]).cap) {
  int32_t ncap = (((w[0]).cap * 2) + 64);
  (w[0]).buf = realloc((w[0]).buf, (int64_t)((ncap + 1)));
  (w[0]).cap = ncap;
}
  (w[0]).buf[(w[0]).len] = c;
  (w[0]).len = ((w[0]).len + 1);
}

void flowc_shader_putc(ShBuf* w, uint8_t c) {
  sh_putc(w, c);
}

void sh_puts(ShBuf* w, const char* s) {
  uint8_t* p = (uint8_t*)(s);
  int32_t n = (int32_t)(strlen(s));
  int32_t i = 0;
  while (i < n) {
  sh_putc(w, p[i]);
  i = (i + 1);
}
}

void sh_line(ShBuf* w, const char* s) {
  sh_puts(w, s);
  sh_putc(w, 10);
}

void sh_put_span(ShBuf* w, uint8_t* p, int32_t s, int32_t e) {
  int32_t i = s;
  while (i < e) {
  sh_putc(w, p[i]);
  i = (i + 1);
}
}

void sh_rule(ShBuf* w, int32_t n) {
  int32_t i = 0;
  while (i < n) {
  sh_putc(w, 226);
  sh_putc(w, 148);
  sh_putc(w, 128);
  i = (i + 1);
}
}

void sh_pad(ShBuf* w, int32_t indent) {
  int32_t i = 0;
  while (i < (indent * 4)) {
  sh_putc(w, 32);
  i = (i + 1);
}
}

int32_t* sh_ints(int32_t n) {
  return (int32_t*)(malloc(((int64_t)((n + 4)) * 4)));
}

void sh_pool_add(ShCtx* c, const char* s) {
  uint8_t* sp = (uint8_t*)(s);
  int32_t k = (int32_t)(strlen(s));
  (c[0]).ys[(c[0]).ny] = (c[0]).pn;
  int32_t i = 0;
  while (i < k) {
  (c[0]).p[(c[0]).pn] = sp[i];
  (c[0]).pn = ((c[0]).pn + 1);
  i = (i + 1);
}
  (c[0]).ye[(c[0]).ny] = (c[0]).pn;
  (c[0]).ny = ((c[0]).ny + 1);
}

void sh_pool_add_set(ShCtx* c, const char* a, const char* b, const char* d, const char* e, const char* f, const char* g, const char* h, const char* i, const char* j) {
  sh_pool_add(c, a);
  sh_pool_add(c, b);
  sh_pool_add(c, d);
  sh_pool_add(c, e);
  sh_pool_add(c, f);
  sh_pool_add(c, g);
  sh_pool_add(c, h);
  sh_pool_add(c, i);
  sh_pool_add(c, j);
}

ShCtx* flowc_shader_ctx_new(uint8_t* src, int32_t n) {
  ShCtx* c = (ShCtx*)((ShCtx*)(malloc(512)));
  int32_t cap = (n + 8);
  (c[0]).p = malloc((int64_t)((n + 512)));
  int32_t i = 0;
  while (i < n) {
  (c[0]).p[i] = src[i];
  i = (i + 1);
}
  (c[0]).p[n] = 0;
  (c[0]).n = n;
  (c[0]).pn = (n + 1);
  (c[0]).target = SH_METAL;
  (c[0]).err = 0;
  (c[0]).msg = flowc_shader_buf_new(256);
  (c[0]).tk = sh_ints(cap);
  (c[0]).ts = sh_ints(cap);
  (c[0]).te = sh_ints(cap);
  (c[0]).ntok = 0;
  (c[0]).ti = 0;
  (c[0]).nk = sh_ints((cap * 2));
  (c[0]).na = sh_ints((cap * 2));
  (c[0]).nb = sh_ints((cap * 2));
  (c[0]).nc = sh_ints((cap * 2));
  (c[0]).nx = sh_ints((cap * 2));
  (c[0]).s1 = sh_ints((cap * 2));
  (c[0]).e1 = sh_ints((cap * 2));
  (c[0]).nf = sh_ints((cap * 2));
  (c[0]).nn = 0;
  (c[0]).ys = sh_ints(((cap * 3) + TY_CONSTS));
  (c[0]).ye = sh_ints(((cap * 3) + TY_CONSTS));
  (c[0]).ny = 0;
  (c[0]).vs = sh_ints((cap * 2));
  (c[0]).ve = sh_ints((cap * 2));
  (c[0]).vt = sh_ints((cap * 2));
  (c[0]).nv = 0;
  (c[0]).fns = sh_ints(cap);
  (c[0]).fne = sh_ints(cap);
  (c[0]).fbs = sh_ints(cap);
  (c[0]).fbe = sh_ints(cap);
  (c[0]).frt = sh_ints(cap);
  (c[0]).fp0 = sh_ints(cap);
  (c[0]).fpn = sh_ints(cap);
  (c[0]).nfn = 0;
  (c[0]).pas = sh_ints(cap);
  (c[0]).pae = sh_ints(cap);
  (c[0]).pat = sh_ints(cap);
  (c[0]).npa = 0;
  (c[0]).fls = sh_ints(cap);
  (c[0]).fle = sh_ints(cap);
  (c[0]).flbs = sh_ints(cap);
  (c[0]).flbe = sh_ints(cap);
  (c[0]).nfl = 0;
  sh_pool_add_set(c, "f32", "i32", "bool", "vec2", "vec3", "vec4", "mat2", "mat3", "mat4");
  sh_pool_add_set(c, "float", "int", "bool", "float2", "float3", "float4", "float2x2", "float3x3", "float4x4");
  sh_pool_add_set(c, "f32", "i32", "bool", "vec2<f32>", "vec3<f32>", "vec4<f32>", "mat2x2<f32>", "mat3x3<f32>", "mat4x4<f32>");
  (c[0]).ybase = (c[0]).ny;
  return c;
}

void flowc_shader_ctx_free(ShCtx* c) {
  free((c[0]).p);
  flowc_shader_buf_free((c[0]).msg);
  free((uint8_t*)((c[0]).tk));
  free((uint8_t*)((c[0]).ts));
  free((uint8_t*)((c[0]).te));
  free((uint8_t*)((c[0]).nk));
  free((uint8_t*)((c[0]).na));
  free((uint8_t*)((c[0]).nb));
  free((uint8_t*)((c[0]).nc));
  free((uint8_t*)((c[0]).nx));
  free((uint8_t*)((c[0]).s1));
  free((uint8_t*)((c[0]).e1));
  free((uint8_t*)((c[0]).nf));
  free((uint8_t*)((c[0]).ys));
  free((uint8_t*)((c[0]).ye));
  free((uint8_t*)((c[0]).vs));
  free((uint8_t*)((c[0]).ve));
  free((uint8_t*)((c[0]).vt));
  free((uint8_t*)((c[0]).fns));
  free((uint8_t*)((c[0]).fne));
  free((uint8_t*)((c[0]).fbs));
  free((uint8_t*)((c[0]).fbe));
  free((uint8_t*)((c[0]).frt));
  free((uint8_t*)((c[0]).fp0));
  free((uint8_t*)((c[0]).fpn));
  free((uint8_t*)((c[0]).pas));
  free((uint8_t*)((c[0]).pae));
  free((uint8_t*)((c[0]).pat));
  free((uint8_t*)((c[0]).fls));
  free((uint8_t*)((c[0]).fle));
  free((uint8_t*)((c[0]).flbs));
  free((uint8_t*)((c[0]).flbe));
  free((uint8_t*)(c));
}

int32_t flowc_shader_ctx_err(ShCtx* c) {
  return (c[0]).err;
}

ShBuf* flowc_shader_ctx_msg(ShCtx* c) {
  return (c[0]).msg;
}

int32_t flowc_shader_fill_count(ShCtx* c) {
  return (c[0]).nfl;
}

void flowc_shader_put_fill_name(ShCtx* c, ShBuf* w, int32_t k) {
  sh_put_span(w, (c[0]).p, (c[0]).fls[k], (c[0]).fle[k]);
}

int32_t flowc_shader_fill_named(ShCtx* c, int32_t k, uint8_t* name, int32_t nlen) {
  int32_t s = (c[0]).fls[k];
  int32_t e = (c[0]).fle[k];
  if ((e - s) != nlen) {
  return 0;
}
  int32_t i = 0;
  while (i < nlen) {
  if ((c[0]).p[(s + i)] != name[i]) {
  return 0;
}
  i = (i + 1);
}
  return 1;
}

int32_t sh_err(ShCtx* c) {
  if ((c[0]).err != 0) {
  return 0;
}
  (c[0]).err = 1;
  ((c[0]).msg[0]).len = 0;
  return 1;
}

void sh_fail(ShCtx* c, const char* m) {
  if (sh_err(c) == 1) {
  sh_puts((c[0]).msg, m);
}
}

int32_t sh_is_space(uint8_t c) {
  if (c == 32) {
  return 1;
}
  if (c >= 9 && c <= 13) {
  return 1;
}
  if (c >= 28 && c <= 31) {
  return 1;
}
  return 0;
}

int32_t sh_is_word(uint8_t c) {
  if (c >= 48 && c <= 57) {
  return 1;
}
  if (c >= 65 && c <= 90) {
  return 1;
}
  if (c >= 97 && c <= 122) {
  return 1;
}
  if (c == 95) {
  return 1;
}
  if (c >= 128) {
  return 1;
}
  return 0;
}

int32_t sh_is_digit(uint8_t c) {
  if (c >= 48 && c <= 57) {
  return 1;
}
  return 0;
}

int32_t sh_is_ident_start(uint8_t c) {
  if (c >= 65 && c <= 90) {
  return 1;
}
  if (c >= 97 && c <= 122) {
  return 1;
}
  if (c == 95) {
  return 1;
}
  return 0;
}

int32_t sh_is_ident(uint8_t c) {
  if (sh_is_ident_start(c) == 1) {
  return 1;
}
  return sh_is_digit(c);
}

int32_t sh_is_ret_ch(uint8_t c) {
  if (sh_is_ident(c) == 1) {
  return 1;
}
  if (c == 60 || c == 62 || c == 44) {
  return 1;
}
  return sh_is_space(c);
}

int32_t sh_lit_at(uint8_t* p, int32_t i, int32_t e, const char* lit) {
  uint8_t* lp = (uint8_t*)(lit);
  int32_t n = (int32_t)(strlen(lit));
  if ((i + n) > e) {
  return 0;
}
  int32_t k = 0;
  while (k < n) {
  if (p[(i + k)] != lp[k]) {
  return 0;
}
  k = (k + 1);
}
  return 1;
}

int32_t sh_span_is(uint8_t* p, int32_t s, int32_t e, const char* lit) {
  int32_t n = (int32_t)(strlen(lit));
  if ((e - s) != n) {
  return 0;
}
  return sh_lit_at(p, s, e, lit);
}

int32_t sh_span_eq(uint8_t* p, int32_t a0, int32_t a1, int32_t b0, int32_t b1) {
  if ((a1 - a0) != (b1 - b0)) {
  return 0;
}
  int32_t k = 0;
  while (k < (a1 - a0)) {
  if (p[(a0 + k)] != p[(b0 + k)]) {
  return 0;
}
  k = (k + 1);
}
  return 1;
}

int32_t sh_skip_ws(uint8_t* p, int32_t i, int32_t e) {
  int32_t k = i;
  while (k < e && sh_is_space(p[k]) == 1) {
  k = (k + 1);
}
  return k;
}

int32_t sh_fill_head_at(uint8_t* p, int32_t i, int32_t n, int32_t* out) {
  if (sh_lit_at(p, i, n, "shader") == 0) {
  return (0 - 1);
}
  if (i > 0 && sh_is_word(p[(i - 1)]) == 1) {
  return (0 - 1);
}
  int32_t j = (i + 6);
  int32_t a = sh_skip_ws(p, j, n);
  if (a == j) {
  return (0 - 1);
}
  if (sh_lit_at(p, a, n, "fill") == 0) {
  return (0 - 1);
}
  j = (a + 4);
  int32_t b = sh_skip_ws(p, j, n);
  if (b == j) {
  return (0 - 1);
}
  if (b >= n || sh_is_ident_start(p[b]) == 0) {
  return (0 - 1);
}
  int32_t k = (b + 1);
  while (k < n && sh_is_ident(p[k]) == 1) {
  k = (k + 1);
}
  out[0] = b;
  out[1] = k;
  int32_t d = sh_skip_ws(p, k, n);
  if (d >= n || p[d] != 123) {
  return (0 - 1);
}
  return (d + 1);
}

int32_t sh_fn_head_at(uint8_t* p, int32_t i, int32_t n, int32_t* out) {
  if (sh_lit_at(p, i, n, "fn") == 0) {
  return (0 - 1);
}
  if (i > 0 && sh_is_word(p[(i - 1)]) == 1) {
  return (0 - 1);
}
  int32_t j = (i + 2);
  int32_t a = sh_skip_ws(p, j, n);
  if (a == j) {
  return (0 - 1);
}
  if (a >= n || sh_is_ident_start(p[a]) == 0) {
  return (0 - 1);
}
  int32_t k = (a + 1);
  while (k < n && sh_is_ident(p[k]) == 1) {
  k = (k + 1);
}
  out[0] = a;
  out[1] = k;
  int32_t lp = sh_skip_ws(p, k, n);
  if (lp >= n || p[lp] != 40) {
  return (0 - 1);
}
  int32_t rp = (lp + 1);
  while (rp < n && p[rp] != 41) {
  rp = (rp + 1);
}
  if (rp >= n) {
  return (0 - 1);
}
  out[2] = (lp + 1);
  out[3] = rp;
  int32_t ar = sh_skip_ws(p, (rp + 1), n);
  if (sh_lit_at(p, ar, n, "->") == 0) {
  return (0 - 1);
}
  int32_t rs = (ar + 2);
  int32_t re = rs;
  while (re < n && sh_is_ret_ch(p[re]) == 1) {
  re = (re + 1);
}
  if (re == rs || re >= n || p[re] != 123) {
  return (0 - 1);
}
  out[4] = rs;
  out[5] = re;
  return (re + 1);
}

void sh_strip(uint8_t* p, int32_t* se) {
  while (se[0] < se[1] && sh_is_space(p[se[0]]) == 1) {
  se[0] = (se[0] + 1);
}
  while (se[1] > se[0] && sh_is_space(p[(se[1] - 1)]) == 1) {
  se[1] = (se[1] - 1);
}
}

int32_t sh_ty_span(ShCtx* c, int32_t s, int32_t e) {
  int32_t h = (c[0]).ny;
  (c[0]).ys[h] = s;
  (c[0]).ye[h] = e;
  (c[0]).ny = (h + 1);
  return h;
}

int32_t sh_brace_block(ShCtx* c, int32_t at) {
  uint8_t* p = (uint8_t*)((c[0]).p);
  int32_t n = (c[0]).n;
  int32_t depth = 0;
  int32_t i = at;
  while (i < n) {
  if (p[i] == 123) {
  depth = (depth + 1);
} else {
  if (p[i] == 125) {
  depth = (depth - 1);
  if (depth == 0) {
  return (i + 1);
}
}
}
  i = (i + 1);
}
  sh_fail(c, "Unclosed '{' in shader module");
  return (0 - 1);
}

int32_t sh_parse_params(ShCtx* c, int32_t s, int32_t e) {
  uint8_t* p = (uint8_t*)((c[0]).p);
  int32_t* se = (int32_t*)(sh_ints(2));
  se[0] = s;
  se[1] = e;
  sh_strip(p, se);
  if (se[0] == se[1]) {
  free((uint8_t*)(se));
  return 0;
}
  int32_t rs = se[0];
  int32_t rend = se[1];
  int32_t a = rs;
  int32_t rc = 0;
  while (a <= rend && rc == 0) {
  int32_t b = a;
  while (b < rend && p[b] != 44) {
  b = (b + 1);
}
  se[0] = a;
  se[1] = b;
  sh_strip(p, se);
  if (se[0] < se[1]) {
  int32_t colon = se[0];
  while (colon < se[1] && p[colon] != 58) {
  colon = (colon + 1);
}
  if (colon >= se[1]) {
  if (sh_err(c) == 1) {
  sh_puts((c[0]).msg, "Shader fn param needs name: type, got '");
  sh_put_span((c[0]).msg, p, se[0], se[1]);
  sh_puts((c[0]).msg, "'");
}
  rc = (0 - 1);
} else {
  int32_t ps = se[0];
  int32_t pe = se[1];
  se[0] = ps;
  se[1] = colon;
  sh_strip(p, se);
  int32_t k = (c[0]).npa;
  (c[0]).pas[k] = se[0];
  (c[0]).pae[k] = se[1];
  se[0] = (colon + 1);
  se[1] = pe;
  sh_strip(p, se);
  (c[0]).pat[k] = sh_ty_span(c, se[0], se[1]);
  (c[0]).npa = (k + 1);
}
}
  a = (b + 1);
}
  free((uint8_t*)(se));
  return rc;
}

int32_t flowc_shader_extract(ShCtx* c) {
  uint8_t* p = (uint8_t*)((c[0]).p);
  int32_t n = (c[0]).n;
  int32_t* hf = (int32_t*)(sh_ints(8));
  int32_t* hs = (int32_t*)(sh_ints(8));
  int32_t fpos = 0;
  int32_t fat = (0 - 1);
  int32_t fend = (0 - 1);
  int32_t spos = 0;
  int32_t sat = (0 - 1);
  int32_t send = (0 - 1);
  int32_t occupied = (0 - 1);
  int32_t rc = 0;
  int32_t done = 0;
  while (done == 0) {
  if (fat < 0) {
  while (fpos < n && fat < 0) {
  int32_t r = sh_fn_head_at(p, fpos, n, hf);
  if (r >= 0) {
  fat = fpos;
  fend = r;
} else {
  fpos = (fpos + 1);
}
}
  if (fat < 0) {
  fat = (n + 1);
}
}
  if (sat < 0) {
  while (spos < n && sat < 0) {
  int32_t r2 = sh_fill_head_at(p, spos, n, hs);
  if (r2 >= 0) {
  sat = spos;
  send = r2;
} else {
  spos = (spos + 1);
}
}
  if (sat < 0) {
  sat = (n + 1);
}
}
  if (fat > n && sat > n) {
  done = 1;
} else {
  int32_t is_fn = 0;
  int32_t start = sat;
  if (fat < sat) {
  is_fn = 1;
  start = fat;
}
  if (start >= occupied) {
  int32_t brace = start;
  while (brace < n && p[brace] != 123) {
  brace = (brace + 1);
}
  int32_t end = sh_brace_block(c, brace);
  if (end < 0) {
  rc = (0 - 1);
  done = 1;
} else {
  occupied = end;
  if (is_fn == 1) {
  int32_t k = (c[0]).nfn;
  (c[0]).fns[k] = hf[0];
  (c[0]).fne[k] = hf[1];
  (c[0]).fbs[k] = (brace + 1);
  (c[0]).fbe[k] = (end - 1);
  (c[0]).fp0[k] = (c[0]).npa;
  if (sh_parse_params(c, hf[2], hf[3]) != 0) {
  rc = (0 - 1);
  done = 1;
} else {
  (c[0]).fpn[k] = ((c[0]).npa - (c[0]).fp0[k]);
  int32_t* rse = (int32_t*)(sh_ints(2));
  rse[0] = hf[4];
  rse[1] = hf[5];
  sh_strip(p, rse);
  (c[0]).frt[k] = sh_ty_span(c, rse[0], rse[1]);
  free((uint8_t*)(rse));
  (c[0]).nfn = (k + 1);
}
} else {
  int32_t k2 = (c[0]).nfl;
  (c[0]).fls[k2] = hs[0];
  (c[0]).fle[k2] = hs[1];
  (c[0]).flbs[k2] = (brace + 1);
  (c[0]).flbe[k2] = (end - 1);
  (c[0]).nfl = (k2 + 1);
}
}
}
  if (is_fn == 1) {
  fpos = fend;
  fat = (0 - 1);
} else {
  spos = send;
  sat = (0 - 1);
}
}
}
  free((uint8_t*)(hf));
  free((uint8_t*)(hs));
  (c[0]).ybase = (c[0]).ny;
  return rc;
}

int32_t flowc_shader_is_module(uint8_t* p, int32_t n) {
  int32_t* hs = (int32_t*)(sh_ints(2));
  int32_t i = 0;
  int32_t found = 0;
  while (i < n && found == 0) {
  int32_t k = i;
  while (k < n && (p[k] == 32 || p[k] == 9)) {
  k = (k + 1);
}
  if (sh_fill_head_at(p, k, n, hs) >= 0) {
  found = 1;
}
  while (i < n && p[i] != 10) {
  i = (i + 1);
}
  i = (i + 1);
}
  free((uint8_t*)(hs));
  return found;
}

int32_t flowc_shader_expand_in_place(uint8_t* buf, int32_t n, int32_t cap) {
  if (n < 0) {
  return n;
}
  if (flowc_shader_is_module(buf, n) == 0) {
  return n;
}
  ShCtx* c = (ShCtx*)(flowc_shader_ctx_new(buf, n));
  int32_t rc = flowc_shader_extract(c);
  if (rc == 0 && (c[0]).nfl == 0) {
  sh_fail(c, "Fill-shader module has no `shader fill` blocks");
  rc = (0 - 1);
}
  if (rc != 0) {
  ShBuf* line = (ShBuf*)(flowc_shader_buf_new(256));
  sh_puts(line, "flowc shader: ");
  sh_put_span(line, ((c[0]).msg[0]).buf, 0, ((c[0]).msg[0]).len);
  (line[0]).buf[(line[0]).len] = 0;
  puts((const char*)((line[0]).buf));
  flowc_shader_buf_free(line);
  flowc_shader_ctx_free(c);
  return (0 - 1);
}
  flowc_shader_ctx_free(c);
  const char* stub = "function main() -> i32 {\n    return 0\n}\n";
  uint8_t* sp = (uint8_t*)(stub);
  int32_t sn = (int32_t)(strlen(stub));
  if (sn >= cap) {
  puts("flowc shader: source buffer too small for the host stub");
  return (0 - 1);
}
  int32_t k = 0;
  while (k < sn) {
  buf[k] = sp[k];
  k = (k + 1);
}
  buf[sn] = 0;
  return sn;
}

void sh_tok(ShCtx* c, int32_t kind, int32_t s, int32_t e) {
  int32_t k = (c[0]).ntok;
  (c[0]).tk[k] = kind;
  (c[0]).ts[k] = s;
  (c[0]).te[k] = e;
  (c[0]).ntok = (k + 1);
}

void sh_tokenize(ShCtx* c, int32_t s, int32_t e) {
  uint8_t* p = (uint8_t*)((c[0]).p);
  (c[0]).ntok = 0;
  (c[0]).ti = 0;
  int32_t i = s;
  while (i < e) {
  uint8_t ch = p[i];
  if (sh_is_digit(ch) == 1) {
  int32_t j = i;
  while (j < e && sh_is_digit(p[j]) == 1) {
  j = (j + 1);
}
  if (j < e && p[j] == 46) {
  j = (j + 1);
  while (j < e && sh_is_digit(p[j]) == 1) {
  j = (j + 1);
}
}
  sh_tok(c, T_NUMBER, i, j);
  i = j;
} else {
  if (ch == 46 && (i + 1) < e && sh_is_digit(p[(i + 1)]) == 1) {
  int32_t j2 = (i + 1);
  while (j2 < e && sh_is_digit(p[j2]) == 1) {
  j2 = (j2 + 1);
}
  sh_tok(c, T_NUMBER, i, j2);
  i = j2;
} else {
  if (sh_is_ident_start(ch) == 1) {
  int32_t j3 = (i + 1);
  while (j3 < e && sh_is_ident(p[j3]) == 1) {
  j3 = (j3 + 1);
}
  sh_tok(c, T_IDENT, i, j3);
  i = j3;
} else {
  if (ch == 43 || ch == 45 || ch == 42 || ch == 47 || ch == 37) {
  sh_tok(c, T_OP, i, (i + 1));
  i = (i + 1);
} else {
  if ((ch == 60 || ch == 62 || ch == 61 || ch == 33) && (i + 1) < e && p[(i + 1)] == 61) {
  sh_tok(c, T_COMPARE, i, (i + 2));
  i = (i + 2);
} else {
  if (ch == 60 || ch == 62) {
  sh_tok(c, T_COMPARE, i, (i + 1));
  i = (i + 1);
} else {
  if (ch == 38 && (i + 1) < e && p[(i + 1)] == 38) {
  sh_tok(c, T_AND, i, (i + 2));
  i = (i + 2);
} else {
  if (ch == 124 && (i + 1) < e && p[(i + 1)] == 124) {
  sh_tok(c, T_OR, i, (i + 2));
  i = (i + 2);
} else {
  if (ch == 33) {
  sh_tok(c, T_NOT, i, (i + 1));
  i = (i + 1);
} else {
  if (ch == 61) {
  sh_tok(c, T_ASSIGN, i, (i + 1));
  i = (i + 1);
} else {
  if (ch == 40) {
  sh_tok(c, T_LPAREN, i, (i + 1));
  i = (i + 1);
} else {
  if (ch == 41) {
  sh_tok(c, T_RPAREN, i, (i + 1));
  i = (i + 1);
} else {
  if (ch == 123) {
  sh_tok(c, T_LBRACE, i, (i + 1));
  i = (i + 1);
} else {
  if (ch == 125) {
  sh_tok(c, T_RBRACE, i, (i + 1));
  i = (i + 1);
} else {
  if (ch == 44) {
  sh_tok(c, T_COMMA, i, (i + 1));
  i = (i + 1);
} else {
  if (ch == 58) {
  sh_tok(c, T_COLON, i, (i + 1));
  i = (i + 1);
} else {
  if (ch == 46) {
  sh_tok(c, T_DOT, i, (i + 1));
  i = (i + 1);
} else {
  if (ch == 59) {
  sh_tok(c, T_SEMI, i, (i + 1));
  i = (i + 1);
} else {
  if (ch == 10) {
  sh_tok(c, T_NEWLINE, i, (i + 1));
  i = (i + 1);
} else {
  if (ch == 35) {
  while (i < e && p[i] != 10) {
  i = (i + 1);
}
} else {
  i = (i + 1);
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
}
}
}
}
}
}
}
}
  sh_tok(c, T_EOF, e, e);
}

const char* sh_kind_name(int32_t k) {
  if (k == T_NUMBER) {
  return "NUMBER";
}
  if (k == T_IDENT) {
  return "IDENT";
}
  if (k == T_OP) {
  return "OP";
}
  if (k == T_COMPARE) {
  return "COMPARE";
}
  if (k == T_AND) {
  return "AND";
}
  if (k == T_OR) {
  return "OR";
}
  if (k == T_NOT) {
  return "NOT";
}
  if (k == T_ASSIGN) {
  return "ASSIGN";
}
  if (k == T_LPAREN) {
  return "LPAREN";
}
  if (k == T_RPAREN) {
  return "RPAREN";
}
  if (k == T_LBRACE) {
  return "LBRACE";
}
  if (k == T_RBRACE) {
  return "RBRACE";
}
  if (k == T_COMMA) {
  return "COMMA";
}
  if (k == T_COLON) {
  return "COLON";
}
  if (k == T_DOT) {
  return "DOT";
}
  if (k == T_SEMI) {
  return "SEMI";
}
  if (k == T_NEWLINE) {
  return "NEWLINE";
}
  return "EOF";
}

int32_t sh_cur(ShCtx* c) {
  return (c[0]).tk[(c[0]).ti];
}

int32_t sh_cur_is(ShCtx* c, int32_t kind, const char* lit) {
  int32_t t = (c[0]).ti;
  if ((c[0]).tk[t] != kind) {
  return 0;
}
  return sh_span_is((c[0]).p, (c[0]).ts[t], (c[0]).te[t], lit);
}

int32_t sh_advance(ShCtx* c) {
  int32_t t = (c[0]).ti;
  if (t < ((c[0]).ntok - 1)) {
  (c[0]).ti = (t + 1);
}
  return t;
}

int32_t sh_match(ShCtx* c, int32_t kind) {
  if (sh_cur(c) != kind) {
  return 0;
}
  sh_advance(c);
  return 1;
}

void sh_err_got(ShCtx* c, const char* head) {
  if (sh_err(c) == 1) {
  int32_t t = (c[0]).ti;
  sh_puts((c[0]).msg, head);
  sh_puts((c[0]).msg, sh_kind_name((c[0]).tk[t]));
  sh_puts((c[0]).msg, " '");
  sh_put_span((c[0]).msg, (c[0]).p, (c[0]).ts[t], (c[0]).te[t]);
  sh_puts((c[0]).msg, "'");
}
}

int32_t sh_expect(ShCtx* c, int32_t kind, const char* lit) {
  int32_t t = (c[0]).ti;
  uint8_t* lp = (uint8_t*)(lit);
  int32_t has_lit = (int32_t)(strlen(lit));
  int32_t ok = 1;
  if ((c[0]).tk[t] != kind) {
  ok = 0;
} else {
  if (has_lit > 0 && sh_span_is((c[0]).p, (c[0]).ts[t], (c[0]).te[t], lit) == 0) {
  ok = 0;
}
}
  if (ok == 0) {
  if (sh_err(c) == 1) {
  sh_puts((c[0]).msg, "Shader parse error: expected ");
  sh_puts((c[0]).msg, sh_kind_name(kind));
  if (has_lit > 0) {
  sh_puts((c[0]).msg, " '");
  sh_puts((c[0]).msg, lit);
  sh_puts((c[0]).msg, "'");
}
  sh_puts((c[0]).msg, ", got ");
  sh_puts((c[0]).msg, sh_kind_name((c[0]).tk[t]));
  sh_puts((c[0]).msg, " '");
  sh_put_span((c[0]).msg, (c[0]).p, (c[0]).ts[t], (c[0]).te[t]);
  sh_puts((c[0]).msg, "'");
}
  return (0 - 1);
}
  return sh_advance(c);
}

void sh_skip_nl(ShCtx* c) {
  while (sh_cur(c) == T_NEWLINE) {
  sh_advance(c);
}
}

int32_t sh_node(ShCtx* c, int32_t kind) {
  int32_t k = (c[0]).nn;
  (c[0]).nk[k] = kind;
  (c[0]).na[k] = (0 - 1);
  (c[0]).nb[k] = (0 - 1);
  (c[0]).nc[k] = (0 - 1);
  (c[0]).nx[k] = (0 - 1);
  (c[0]).s1[k] = 0;
  (c[0]).e1[k] = 0;
  (c[0]).nf[k] = 0;
  (c[0]).nn = (k + 1);
  return k;
}

int32_t sh_node_tok(ShCtx* c, int32_t kind, int32_t t) {
  int32_t k = sh_node(c, kind);
  (c[0]).s1[k] = (c[0]).ts[t];
  (c[0]).e1[k] = (c[0]).te[t];
  return k;
}

int32_t sh_binary(ShCtx* c, int32_t op, int32_t left, int32_t right) {
  int32_t k = sh_node_tok(c, E_BINARY, op);
  (c[0]).na[k] = left;
  (c[0]).nb[k] = right;
  return k;
}

int32_t sh_parse_stmts(ShCtx* c) {
  int32_t head = (0 - 1);
  int32_t tail = (0 - 1);
  sh_skip_nl(c);
  while ((c[0]).err == 0 && sh_cur(c) != T_EOF && sh_cur(c) != T_RBRACE) {
  int32_t st = sh_parse_stmt(c);
  if ((c[0]).err == 0) {
  if (tail < 0) {
  head = st;
} else {
  (c[0]).nx[tail] = st;
}
  tail = st;
  sh_match(c, T_SEMI);
  sh_skip_nl(c);
}
}
  if ((c[0]).err != 0) {
  return (0 - 1);
}
  return head;
}

int32_t sh_parse_block(ShCtx* c) {
  if (sh_expect(c, T_LBRACE, "") < 0) {
  return (0 - 1);
}
  sh_skip_nl(c);
  int32_t body = sh_parse_stmts(c);
  if ((c[0]).err != 0) {
  return (0 - 1);
}
  if (sh_expect(c, T_RBRACE, "") < 0) {
  return (0 - 1);
}
  return body;
}

int32_t sh_parse_stmt(ShCtx* c) {
  sh_skip_nl(c);
  if (sh_cur_is(c, T_IDENT, "let") == 1 || sh_cur_is(c, T_IDENT, "var") == 1) {
  return sh_parse_let(c);
}
  if (sh_cur_is(c, T_IDENT, "if") == 1) {
  return sh_parse_if(c);
}
  if (sh_cur_is(c, T_IDENT, "for") == 1) {
  return sh_parse_for(c);
}
  if (sh_cur_is(c, T_IDENT, "return") == 1) {
  sh_advance(c);
  int32_t r = sh_node(c, S_RETURN);
  int32_t k = sh_cur(c);
  if (k == T_NEWLINE || k == T_SEMI || k == T_RBRACE || k == T_EOF) {
  return r;
}
  (c[0]).na[r] = sh_parse_expr(c);
  return r;
}
  if (sh_cur(c) == T_IDENT) {
  int32_t name = sh_advance(c);
  if (sh_expect(c, T_ASSIGN, "") < 0) {
  return (0 - 1);
}
  int32_t a = sh_node_tok(c, S_ASSIGN, name);
  (c[0]).na[a] = sh_parse_expr(c);
  return a;
}
  sh_err_got(c, "Shader statement expected, got ");
  return (0 - 1);
}

int32_t sh_parse_let(ShCtx* c) {
  int32_t mutable = 0;
  if (sh_cur_is(c, T_IDENT, "var") == 1) {
  mutable = 1;
}
  sh_advance(c);
  int32_t name = sh_expect(c, T_IDENT, "");
  if (name < 0) {
  return (0 - 1);
}
  int32_t st = sh_node_tok(c, S_LET, name);
  (c[0]).nf[st] = mutable;
  if (sh_match(c, T_COLON) == 1) {
  int32_t ty = sh_expect(c, T_IDENT, "");
  if (ty < 0) {
  return (0 - 1);
}
  (c[0]).nb[st] = sh_ty_span(c, (c[0]).ts[ty], (c[0]).te[ty]);
}
  if (sh_expect(c, T_ASSIGN, "") < 0) {
  return (0 - 1);
}
  (c[0]).na[st] = sh_parse_expr(c);
  return st;
}

int32_t sh_parse_body(ShCtx* c) {
  if (sh_cur(c) == T_LBRACE) {
  return sh_parse_block(c);
}
  return sh_parse_stmt(c);
}

int32_t sh_parse_if(ShCtx* c) {
  if (sh_expect(c, T_IDENT, "if") < 0) {
  return (0 - 1);
}
  int32_t st = sh_node(c, S_IF);
  (c[0]).na[st] = sh_parse_expr(c);
  if ((c[0]).err != 0) {
  return (0 - 1);
}
  sh_skip_nl(c);
  (c[0]).nb[st] = sh_parse_body(c);
  if ((c[0]).err != 0) {
  return (0 - 1);
}
  sh_skip_nl(c);
  if (sh_cur_is(c, T_IDENT, "else") == 1) {
  sh_advance(c);
  sh_skip_nl(c);
  if (sh_cur_is(c, T_IDENT, "if") == 1) {
  (c[0]).nc[st] = sh_parse_if(c);
} else {
  (c[0]).nc[st] = sh_parse_body(c);
}
}
  return st;
}

int32_t sh_parse_for(ShCtx* c) {
  if (sh_expect(c, T_IDENT, "for") < 0) {
  return (0 - 1);
}
  int32_t v = sh_expect(c, T_IDENT, "");
  if (v < 0) {
  return (0 - 1);
}
  int32_t st = sh_node_tok(c, S_FOR, v);
  if (sh_cur_is(c, T_IDENT, "in") == 0) {
  sh_fail(c, "Expected 'in' after for variable");
  return (0 - 1);
}
  sh_advance(c);
  (c[0]).na[st] = sh_parse_expr(c);
  if ((c[0]).err != 0) {
  return (0 - 1);
}
  if (sh_cur_is(c, T_IDENT, "to") == 0) {
  sh_fail(c, "Expected 'to' in for-range");
  return (0 - 1);
}
  sh_advance(c);
  (c[0]).nb[st] = sh_parse_expr(c);
  if ((c[0]).err != 0) {
  return (0 - 1);
}
  sh_skip_nl(c);
  (c[0]).nc[st] = sh_parse_body(c);
  return st;
}

int32_t sh_parse_expr(ShCtx* c) {
  return sh_parse_or(c);
}

int32_t sh_parse_or(ShCtx* c) {
  int32_t left = sh_parse_and(c);
  while ((c[0]).err == 0 && sh_cur(c) == T_OR) {
  int32_t op = sh_advance(c);
  left = sh_binary(c, op, left, sh_parse_and(c));
}
  return left;
}

int32_t sh_parse_and(ShCtx* c) {
  int32_t left = sh_parse_compare(c);
  while ((c[0]).err == 0 && sh_cur(c) == T_AND) {
  int32_t op = sh_advance(c);
  left = sh_binary(c, op, left, sh_parse_compare(c));
}
  return left;
}

int32_t sh_parse_compare(ShCtx* c) {
  int32_t left = sh_parse_term(c);
  while ((c[0]).err == 0 && sh_cur(c) == T_COMPARE) {
  int32_t op = sh_advance(c);
  left = sh_binary(c, op, left, sh_parse_term(c));
}
  return left;
}

int32_t sh_parse_term(ShCtx* c) {
  int32_t left = sh_parse_factor(c);
  while ((c[0]).err == 0 && (sh_cur_is(c, T_OP, "+") == 1 || sh_cur_is(c, T_OP, "-") == 1)) {
  int32_t op = sh_advance(c);
  left = sh_binary(c, op, left, sh_parse_factor(c));
}
  return left;
}

int32_t sh_parse_factor(ShCtx* c) {
  int32_t left = sh_parse_unary(c);
  while ((c[0]).err == 0 && (sh_cur_is(c, T_OP, "*") == 1 || sh_cur_is(c, T_OP, "/") == 1 || sh_cur_is(c, T_OP, "%") == 1)) {
  int32_t op = sh_advance(c);
  left = sh_binary(c, op, left, sh_parse_unary(c));
}
  return left;
}

int32_t sh_parse_unary(ShCtx* c) {
  if (sh_cur_is(c, T_OP, "-") == 1 || sh_cur(c) == T_NOT) {
  int32_t op = sh_advance(c);
  int32_t u = sh_node_tok(c, E_UNARY, op);
  (c[0]).na[u] = sh_parse_unary(c);
  return u;
}
  return sh_parse_postfix(c);
}

int32_t sh_parse_postfix(ShCtx* c) {
  int32_t expr = sh_parse_primary(c);
  while ((c[0]).err == 0 && sh_cur(c) == T_DOT) {
  sh_advance(c);
  int32_t f = sh_expect(c, T_IDENT, "");
  if (f < 0) {
  return (0 - 1);
}
  int32_t sw = sh_node_tok(c, E_SWIZZLE, f);
  (c[0]).na[sw] = expr;
  expr = sw;
}
  return expr;
}

int32_t sh_parse_primary(ShCtx* c) {
  sh_skip_nl(c);
  int32_t t = (c[0]).ti;
  int32_t kind = (c[0]).tk[t];
  if (kind == T_NUMBER) {
  sh_advance(c);
  int32_t num = sh_node_tok(c, E_NUMBER, t);
  int32_t dot = 0;
  int32_t i = (c[0]).ts[t];
  while (i < (c[0]).te[t]) {
  if ((c[0]).p[i] == 46) {
  dot = 1;
}
  i = (i + 1);
}
  if (dot == 0) {
  (c[0]).nf[num] = 1;
}
  return num;
}
  if (kind == T_IDENT) {
  sh_advance(c);
  if (sh_match(c, T_LPAREN) == 1) {
  int32_t call = sh_node_tok(c, E_CALL, t);
  int32_t nargs = 0;
  int32_t tail = (0 - 1);
  sh_skip_nl(c);
  if (sh_match(c, T_RPAREN) == 0) {
  int32_t more = 1;
  while (more == 1) {
  sh_skip_nl(c);
  int32_t arg = sh_parse_expr(c);
  if ((c[0]).err != 0) {
  return (0 - 1);
}
  if (tail < 0) {
  (c[0]).na[call] = arg;
} else {
  (c[0]).nx[tail] = arg;
}
  tail = arg;
  nargs = (nargs + 1);
  sh_skip_nl(c);
  if (sh_match(c, T_COMMA) == 0) {
  if (sh_expect(c, T_RPAREN, "") < 0) {
  return (0 - 1);
}
  more = 0;
}
}
}
  (c[0]).nc[call] = nargs;
  uint8_t* p = (uint8_t*)((c[0]).p);
  int32_t ns = (c[0]).ts[t];
  int32_t ne = (c[0]).te[t];
  if (nargs == 1 && (sh_span_is(p, ns, ne, "f32") == 1 || sh_span_is(p, ns, ne, "i32") == 1 || sh_span_is(p, ns, ne, "bool") == 1)) {
  (c[0]).nk[call] = E_CAST;
}
  return call;
}
  return sh_node_tok(c, E_NAME, t);
}
  if (sh_match(c, T_LPAREN) == 1) {
  sh_skip_nl(c);
  int32_t inner = sh_parse_expr(c);
  if ((c[0]).err != 0) {
  return (0 - 1);
}
  sh_skip_nl(c);
  if (sh_expect(c, T_RPAREN, "") < 0) {
  return (0 - 1);
}
  return inner;
}
  sh_err_got(c, "Shader expression expected, got ");
  return (0 - 1);
}

int32_t sh_parse_body_span(ShCtx* c, int32_t s, int32_t e) {
  sh_tokenize(c, s, e);
  (c[0]).nn = 0;
  (c[0]).ny = (c[0]).ybase;
  return sh_parse_stmts(c);
}

int32_t sh_ty_is(ShCtx* c, int32_t h, const char* lit) {
  return sh_span_is((c[0]).p, (c[0]).ys[h], (c[0]).ye[h], lit);
}

int32_t sh_ty_eq(ShCtx* c, int32_t a, int32_t b) {
  return sh_span_eq((c[0]).p, (c[0]).ys[a], (c[0]).ye[a], (c[0]).ys[b], (c[0]).ye[b]);
}

void sh_put_ty(ShCtx* c, ShBuf* w, int32_t h) {
  sh_put_span(w, (c[0]).p, (c[0]).ys[h], (c[0]).ye[h]);
}

int32_t sh_ty_known(ShCtx* c, int32_t k) {
  if ((c[0]).target == SH_WGSL) {
  return (TY_WGSL + k);
}
  return (TY_METAL + k);
}

int32_t sh_map_type(ShCtx* c, int32_t h) {
  if (h < 0 || (c[0]).ys[h] == (c[0]).ye[h]) {
  return sh_ty_known(c, 0);
}
  int32_t k = 0;
  while (k < 9) {
  if (sh_ty_eq(c, h, (TY_FSL + k)) == 1) {
  return sh_ty_known(c, k);
}
  k = (k + 1);
}
  if ((c[0]).target == SH_WGSL) {
  if (sh_err(c) == 1) {
  sh_puts((c[0]).msg, "Unsupported WGSL shader type '");
  sh_put_ty(c, (c[0]).msg, h);
  sh_puts((c[0]).msg, "'");
}
  return (0 - 1);
}
  return h;
}

int32_t sh_ty_named(ShCtx* c, int32_t s, int32_t e) {
  int32_t k = 0;
  while (k < 9) {
  if (sh_span_eq((c[0]).p, s, e, (c[0]).ys[(TY_FSL + k)], (c[0]).ye[(TY_FSL + k)]) == 1) {
  return sh_ty_known(c, k);
}
  k = (k + 1);
}
  return sh_ty_known(c, 0);
}

void sh_env_set(ShCtx* c, int32_t s, int32_t e, int32_t ty) {
  int32_t i = 0;
  while (i < (c[0]).nv) {
  if (sh_span_eq((c[0]).p, (c[0]).vs[i], (c[0]).ve[i], s, e) == 1) {
  (c[0]).vt[i] = ty;
  return;
}
  i = (i + 1);
}
  int32_t k = (c[0]).nv;
  (c[0]).vs[k] = s;
  (c[0]).ve[k] = e;
  (c[0]).vt[k] = ty;
  (c[0]).nv = (k + 1);
}

int32_t sh_env_get(ShCtx* c, int32_t s, int32_t e, int32_t dflt) {
  int32_t i = 0;
  while (i < (c[0]).nv) {
  if (sh_span_eq((c[0]).p, (c[0]).vs[i], (c[0]).ve[i], s, e) == 1) {
  return (c[0]).vt[i];
}
  i = (i + 1);
}
  return dflt;
}

int32_t sh_find_fn(ShCtx* c, int32_t s, int32_t e) {
  int32_t i = ((c[0]).nfn - 1);
  while (i >= 0) {
  if (sh_span_eq((c[0]).p, (c[0]).fns[i], (c[0]).fne[i], s, e) == 1) {
  return i;
}
  i = (i - 1);
}
  return (0 - 1);
}

int32_t sh_node_is(ShCtx* c, int32_t k, const char* lit) {
  return sh_span_is((c[0]).p, (c[0]).s1[k], (c[0]).e1[k], lit);
}

int32_t sh_rank(ShCtx* c, int32_t h) {
  if (sh_ty_is(c, h, "bool") == 1) {
  return 0;
}
  if ((c[0]).target == SH_WGSL) {
  if (sh_ty_is(c, h, "vec2<f32>") == 1) {
  return 2;
}
  if (sh_ty_is(c, h, "vec3<f32>") == 1) {
  return 3;
}
  if (sh_ty_is(c, h, "vec4<f32>") == 1) {
  return 4;
}
  return 1;
}
  if (sh_ty_is(c, h, "float2") == 1) {
  return 2;
}
  if (sh_ty_is(c, h, "float3") == 1) {
  return 3;
}
  if (sh_ty_is(c, h, "float4") == 1) {
  return 4;
}
  return 1;
}

int32_t sh_is_metal_float_fn(ShCtx* c, int32_t k) {
  if (sh_node_is(c, k, "noise") == 1) {
  return 1;
}
  if (sh_node_is(c, k, "fbm") == 1) {
  return 1;
}
  if (sh_node_is(c, k, "hash") == 1) {
  return 1;
}
  if (sh_node_is(c, k, "length") == 1) {
  return 1;
}
  if (sh_node_is(c, k, "dot") == 1) {
  return 1;
}
  if (sh_node_is(c, k, "sin") == 1) {
  return 1;
}
  if (sh_node_is(c, k, "cos") == 1) {
  return 1;
}
  if (sh_node_is(c, k, "atan2") == 1) {
  return 1;
}
  return 0;
}

int32_t sh_is_wgsl_float_fn(ShCtx* c, int32_t k) {
  if (sh_node_is(c, k, "noise") == 1) {
  return 1;
}
  if (sh_node_is(c, k, "fbm") == 1) {
  return 1;
}
  if (sh_node_is(c, k, "hash") == 1) {
  return 1;
}
  if (sh_node_is(c, k, "length") == 1) {
  return 1;
}
  if (sh_node_is(c, k, "distance") == 1) {
  return 1;
}
  if (sh_node_is(c, k, "dot") == 1) {
  return 1;
}
  return 0;
}

int32_t sh_guess(ShCtx* c, int32_t x) {
  __flowc_tail: ;
  int32_t kind = (c[0]).nk[x];
  if (kind == E_NUMBER) {
  return sh_ty_known(c, 0);
}
  if (kind == E_NAME) {
  if (sh_node_is(c, x, "uv") == 1 || sh_node_is(c, x, "resolution") == 1) {
  return sh_ty_known(c, 3);
}
  if (sh_node_is(c, x, "time") == 1) {
  return sh_ty_known(c, 0);
}
  if (sh_node_is(c, x, "color") == 1) {
  return sh_ty_known(c, 5);
}
  return sh_env_get(c, (c[0]).s1[x], (c[0]).e1[x], sh_ty_known(c, 0));
}
  if (kind == E_CAST) {
  return sh_ty_named(c, (c[0]).s1[x], (c[0]).e1[x]);
}
  if (kind == E_CALL) {
  if (sh_node_is(c, x, "vec2") == 1) {
  return sh_ty_known(c, 3);
}
  if ((c[0]).target == SH_WGSL) {
  if (sh_node_is(c, x, "vec3") == 1 || sh_node_is(c, x, "palette") == 1 || sh_node_is(c, x, "cross") == 1) {
  return sh_ty_known(c, 4);
}
  if (sh_node_is(c, x, "vec4") == 1) {
  return sh_ty_known(c, 5);
}
  int32_t f = sh_find_fn(c, (c[0]).s1[x], (c[0]).e1[x]);
  if (f >= 0) {
  return sh_map_type(c, (c[0]).frt[f]);
}
  if (sh_is_wgsl_float_fn(c, x) == 1) {
  return sh_ty_known(c, 0);
}
} else {
  if (sh_node_is(c, x, "vec3") == 1 || sh_node_is(c, x, "palette") == 1 || sh_node_is(c, x, "normalize") == 1 || sh_node_is(c, x, "cross") == 1 || sh_node_is(c, x, "reflect") == 1) {
  return sh_ty_known(c, 4);
}
  if (sh_node_is(c, x, "vec4") == 1) {
  return sh_ty_known(c, 5);
}
  if (sh_is_metal_float_fn(c, x) == 1) {
  return sh_ty_known(c, 0);
}
  if (sh_find_fn(c, (c[0]).s1[x], (c[0]).e1[x]) >= 0) {
  return sh_ty_known(c, 0);
}
}
  if ((c[0]).na[x] >= 0) {
  {
  __auto_type __flowc_targ0 = c;
  __auto_type __flowc_targ1 = (c[0]).na[x];
  c = __flowc_targ0;
  x = __flowc_targ1;
  goto __flowc_tail;
  }
}
  return sh_ty_known(c, 0);
}
  if (kind == E_SWIZZLE) {
  int32_t flen = ((c[0]).e1[x] - (c[0]).s1[x]);
  if (flen == 2) {
  return sh_ty_known(c, 3);
}
  if (flen == 3) {
  return sh_ty_known(c, 4);
}
  if (flen == 4) {
  return sh_ty_known(c, 5);
}
  return sh_ty_known(c, 0);
}
  if (kind == E_UNARY) {
  if (sh_node_is(c, x, "!") == 1) {
  return sh_ty_known(c, 2);
}
  {
  __auto_type __flowc_targ0 = c;
  __auto_type __flowc_targ1 = (c[0]).na[x];
  c = __flowc_targ0;
  x = __flowc_targ1;
  goto __flowc_tail;
  }
}
  if (kind == E_BINARY) {
  if (sh_node_is(c, x, "<") == 1 || sh_node_is(c, x, ">") == 1 || sh_node_is(c, x, "<=") == 1 || sh_node_is(c, x, ">=") == 1 || sh_node_is(c, x, "==") == 1 || sh_node_is(c, x, "!=") == 1 || sh_node_is(c, x, "&&") == 1 || sh_node_is(c, x, "||") == 1) {
  return sh_ty_known(c, 2);
}
  int32_t lt = sh_guess(c, (c[0]).na[x]);
  if (lt < 0) {
  return (0 - 1);
}
  int32_t rt = sh_guess(c, (c[0]).nb[x]);
  if (rt < 0) {
  return (0 - 1);
}
  if (sh_rank(c, lt) >= sh_rank(c, rt)) {
  return lt;
}
  return rt;
}
  return sh_ty_known(c, 0);
}

int32_t sh_is_metal_builtin(ShCtx* c, int32_t k) {
  uint8_t* p = (uint8_t*)((c[0]).p);
  int32_t s = (c[0]).s1[k];
  int32_t e = (c[0]).e1[k];
  if (sh_span_is(p, s, e, "sin") == 1 || sh_span_is(p, s, e, "cos") == 1 || sh_span_is(p, s, e, "tan") == 1) {
  return 1;
}
  if (sh_span_is(p, s, e, "asin") == 1 || sh_span_is(p, s, e, "acos") == 1 || sh_span_is(p, s, e, "atan") == 1) {
  return 1;
}
  if (sh_span_is(p, s, e, "atan2") == 1 || sh_span_is(p, s, e, "abs") == 1 || sh_span_is(p, s, e, "sign") == 1) {
  return 1;
}
  if (sh_span_is(p, s, e, "floor") == 1 || sh_span_is(p, s, e, "ceil") == 1 || sh_span_is(p, s, e, "fract") == 1) {
  return 1;
}
  if (sh_span_is(p, s, e, "trunc") == 1 || sh_span_is(p, s, e, "sqrt") == 1 || sh_span_is(p, s, e, "rsqrt") == 1) {
  return 1;
}
  if (sh_span_is(p, s, e, "exp") == 1 || sh_span_is(p, s, e, "exp2") == 1 || sh_span_is(p, s, e, "log") == 1) {
  return 1;
}
  if (sh_span_is(p, s, e, "log2") == 1 || sh_span_is(p, s, e, "pow") == 1 || sh_span_is(p, s, e, "min") == 1) {
  return 1;
}
  if (sh_span_is(p, s, e, "max") == 1 || sh_span_is(p, s, e, "clamp") == 1 || sh_span_is(p, s, e, "saturate") == 1) {
  return 1;
}
  if (sh_span_is(p, s, e, "mix") == 1 || sh_span_is(p, s, e, "step") == 1 || sh_span_is(p, s, e, "smoothstep") == 1) {
  return 1;
}
  if (sh_span_is(p, s, e, "length") == 1 || sh_span_is(p, s, e, "distance") == 1 || sh_span_is(p, s, e, "dot") == 1) {
  return 1;
}
  if (sh_span_is(p, s, e, "cross") == 1 || sh_span_is(p, s, e, "normalize") == 1 || sh_span_is(p, s, e, "reflect") == 1) {
  return 1;
}
  if (sh_span_is(p, s, e, "refract") == 1 || sh_span_is(p, s, e, "mod") == 1 || sh_span_is(p, s, e, "fmod") == 1) {
  return 1;
}
  return 0;
}

int32_t sh_is_wgsl_builtin(ShCtx* c, int32_t k) {
  uint8_t* p = (uint8_t*)((c[0]).p);
  int32_t s = (c[0]).s1[k];
  int32_t e = (c[0]).e1[k];
  if (sh_span_is(p, s, e, "sin") == 1 || sh_span_is(p, s, e, "cos") == 1 || sh_span_is(p, s, e, "tan") == 1) {
  return 1;
}
  if (sh_span_is(p, s, e, "asin") == 1 || sh_span_is(p, s, e, "acos") == 1 || sh_span_is(p, s, e, "atan") == 1) {
  return 1;
}
  if (sh_span_is(p, s, e, "atan2") == 1 || sh_span_is(p, s, e, "abs") == 1 || sh_span_is(p, s, e, "sign") == 1) {
  return 1;
}
  if (sh_span_is(p, s, e, "floor") == 1 || sh_span_is(p, s, e, "ceil") == 1 || sh_span_is(p, s, e, "fract") == 1) {
  return 1;
}
  if (sh_span_is(p, s, e, "trunc") == 1 || sh_span_is(p, s, e, "sqrt") == 1 || sh_span_is(p, s, e, "inverseSqrt") == 1) {
  return 1;
}
  if (sh_span_is(p, s, e, "exp") == 1 || sh_span_is(p, s, e, "exp2") == 1 || sh_span_is(p, s, e, "log") == 1) {
  return 1;
}
  if (sh_span_is(p, s, e, "log2") == 1 || sh_span_is(p, s, e, "pow") == 1 || sh_span_is(p, s, e, "min") == 1) {
  return 1;
}
  if (sh_span_is(p, s, e, "max") == 1 || sh_span_is(p, s, e, "clamp") == 1 || sh_span_is(p, s, e, "mix") == 1) {
  return 1;
}
  if (sh_span_is(p, s, e, "step") == 1 || sh_span_is(p, s, e, "smoothstep") == 1 || sh_span_is(p, s, e, "length") == 1) {
  return 1;
}
  if (sh_span_is(p, s, e, "distance") == 1 || sh_span_is(p, s, e, "dot") == 1 || sh_span_is(p, s, e, "cross") == 1) {
  return 1;
}
  if (sh_span_is(p, s, e, "normalize") == 1 || sh_span_is(p, s, e, "reflect") == 1 || sh_span_is(p, s, e, "refract") == 1) {
  return 1;
}
  return 0;
}

void sh_put_name(ShCtx* c, ShBuf* w, int32_t k) {
  sh_put_span(w, (c[0]).p, (c[0]).s1[k], (c[0]).e1[k]);
}

void sh_unknown_fn(ShCtx* c, int32_t x) {
  if (sh_err(c) == 1) {
  sh_puts((c[0]).msg, "Unknown shader function '");
  sh_put_name(c, (c[0]).msg, x);
  sh_puts((c[0]).msg, "'");
}
}

void sh_emit_call(ShCtx* c, ShBuf* w, int32_t x) {
  int32_t nargs = (c[0]).nc[x];
  ShBuf* args = (ShBuf*)(flowc_shader_buf_new(64));
  int32_t* ars = (int32_t*)(sh_ints(nargs));
  int32_t* ae = (int32_t*)(sh_ints(nargs));
  int32_t a = (c[0]).na[x];
  int32_t k = 0;
  while (a >= 0 && (c[0]).err == 0) {
  if (k > 0) {
  sh_puts(args, ", ");
}
  ars[k] = (args[0]).len;
  sh_emit_expr(c, args, a);
  ae[k] = (args[0]).len;
  k = (k + 1);
  a = (c[0]).nx[a];
}
  if ((c[0]).err == 0) {
  int32_t wg = (c[0]).target;
  int32_t paren = 1;
  if (sh_node_is(c, x, "vec2") == 1) {
  sh_put_ty(c, w, sh_ty_known(c, 3));
} else {
  if (sh_node_is(c, x, "vec3") == 1) {
  sh_put_ty(c, w, sh_ty_known(c, 4));
} else {
  if (sh_node_is(c, x, "vec4") == 1) {
  sh_put_ty(c, w, sh_ty_known(c, 5));
} else {
  if (sh_node_is(c, x, "hash") == 1) {
  if (wg == SH_WGSL) {
  if (nargs != 1) {
  sh_fail(c, "hash() expects one argument");
} else {
  int32_t at = sh_guess(c, (c[0]).na[x]);
  if (at >= 0 && sh_ty_is(c, at, "vec2<f32>") == 1) {
  sh_puts(w, "fsl_hash21");
} else {
  sh_puts(w, "fsl_hash11");
}
}
} else {
  if (nargs == 1) {
  int32_t at2 = sh_guess(c, (c[0]).na[x]);
  if (sh_ty_is(c, at2, "float2") == 1 || sh_ty_is(c, at2, "vec2") == 1) {
  sh_puts(w, "fsl_hash21");
} else {
  sh_puts(w, "fsl_hash11");
}
} else {
  sh_puts(w, "fsl_hash21");
}
}
} else {
  if (sh_node_is(c, x, "noise") == 1) {
  sh_puts(w, "fsl_noise");
} else {
  if (sh_node_is(c, x, "fbm") == 1) {
  sh_puts(w, "fsl_fbm");
} else {
  if (sh_node_is(c, x, "palette") == 1) {
  sh_puts(w, "fsl_palette");
} else {
  if (wg == SH_METAL && sh_node_is(c, x, "mod") == 1) {
  sh_puts(w, "fmod");
} else {
  if (wg == SH_WGSL && (sh_node_is(c, x, "mod") == 1 || sh_node_is(c, x, "fmod") == 1)) {
  if (nargs != 2) {
  if (sh_err(c) == 1) {
  sh_put_name(c, (c[0]).msg, x);
  sh_puts((c[0]).msg, "() expects two arguments");
}
} else {
  sh_putc(w, 40);
  sh_put_span(w, (args[0]).buf, ars[0], ae[0]);
  sh_puts(w, " % ");
  sh_put_span(w, (args[0]).buf, ars[1], ae[1]);
  sh_putc(w, 41);
}
  paren = 0;
} else {
  if (wg == SH_WGSL && sh_node_is(c, x, "saturate") == 1) {
  if (nargs != 1) {
  sh_fail(c, "saturate() expects one argument");
} else {
  sh_puts(w, "clamp(");
  sh_put_span(w, (args[0]).buf, ars[0], ae[0]);
  sh_puts(w, ", 0.0, 1.0)");
}
  paren = 0;
} else {
  if (wg == SH_WGSL && sh_node_is(c, x, "rsqrt") == 1) {
  sh_puts(w, "inverseSqrt");
} else {
  int32_t known = 0;
  if (wg == SH_WGSL) {
  known = sh_is_wgsl_builtin(c, x);
} else {
  known = sh_is_metal_builtin(c, x);
}
  if (known == 0 && sh_find_fn(c, (c[0]).s1[x], (c[0]).e1[x]) >= 0) {
  known = 1;
}
  if (known == 1) {
  sh_put_name(c, w, x);
} else {
  sh_unknown_fn(c, x);
  paren = 0;
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
  if (paren == 1 && (c[0]).err == 0) {
  sh_putc(w, 40);
  sh_put_span(w, (args[0]).buf, 0, (args[0]).len);
  sh_putc(w, 41);
}
}
  free((uint8_t*)(ars));
  free((uint8_t*)(ae));
  flowc_shader_buf_free(args);
}

void sh_emit_expr(ShCtx* c, ShBuf* w, int32_t x) {
  if ((c[0]).err != 0) {
  return;
}
  int32_t kind = (c[0]).nk[x];
  if (kind == E_NUMBER) {
  sh_put_name(c, w, x);
  if ((c[0]).nf[x] == 1) {
  sh_puts(w, ".0");
}
  return;
}
  if (kind == E_NAME) {
  if (sh_node_is(c, x, "time") == 1) {
  sh_puts(w, "uniforms.time");
} else {
  if (sh_node_is(c, x, "resolution") == 1) {
  sh_put_ty(c, w, sh_ty_known(c, 3));
  sh_puts(w, "(uniforms.width, uniforms.height)");
} else {
  sh_put_name(c, w, x);
}
}
  return;
}
  if (kind == E_UNARY) {
  sh_putc(w, 40);
  sh_put_name(c, w, x);
  sh_emit_expr(c, w, (c[0]).na[x]);
  sh_putc(w, 41);
  return;
}
  if (kind == E_BINARY) {
  if ((c[0]).target == SH_METAL && sh_node_is(c, x, "%") == 1) {
  sh_puts(w, "fmod(");
  sh_emit_expr(c, w, (c[0]).na[x]);
  sh_puts(w, ", ");
  sh_emit_expr(c, w, (c[0]).nb[x]);
  sh_putc(w, 41);
  return;
}
  sh_putc(w, 40);
  sh_emit_expr(c, w, (c[0]).na[x]);
  sh_putc(w, 32);
  sh_put_name(c, w, x);
  sh_putc(w, 32);
  sh_emit_expr(c, w, (c[0]).nb[x]);
  sh_putc(w, 41);
  return;
}
  if (kind == E_SWIZZLE) {
  sh_emit_expr(c, w, (c[0]).na[x]);
  sh_putc(w, 46);
  sh_put_name(c, w, x);
  return;
}
  if (kind == E_CAST) {
  sh_put_ty(c, w, sh_ty_named(c, (c[0]).s1[x], (c[0]).e1[x]));
  sh_putc(w, 40);
  sh_emit_expr(c, w, (c[0]).na[x]);
  sh_putc(w, 41);
  return;
}
  sh_emit_call(c, w, x);
}

int32_t sh_emit_stmts(ShCtx* c, ShBuf* w, int32_t head, int32_t indent) {
  int32_t lines = 0;
  int32_t st = head;
  while (st >= 0 && (c[0]).err == 0) {
  int32_t kind = (c[0]).nk[st];
  if (kind == S_LET) {
  int32_t ty = 0;
  if ((c[0]).nb[st] >= 0) {
  ty = sh_map_type(c, (c[0]).nb[st]);
} else {
  ty = sh_guess(c, (c[0]).na[st]);
}
  if ((c[0]).err == 0) {
  sh_env_set(c, (c[0]).s1[st], (c[0]).e1[st], ty);
  sh_pad(w, indent);
  if ((c[0]).target == SH_WGSL) {
  if ((c[0]).nf[st] == 1) {
  sh_puts(w, "var ");
} else {
  sh_puts(w, "let ");
}
  sh_put_name(c, w, st);
  sh_puts(w, ": ");
  sh_put_ty(c, w, ty);
} else {
  sh_put_ty(c, w, ty);
  sh_putc(w, 32);
  sh_put_name(c, w, st);
}
  sh_puts(w, " = ");
  sh_emit_expr(c, w, (c[0]).na[st]);
  sh_line(w, ";");
  lines = (lines + 1);
}
} else {
  if (kind == S_ASSIGN) {
  sh_pad(w, indent);
  sh_put_name(c, w, st);
  sh_puts(w, " = ");
  sh_emit_expr(c, w, (c[0]).na[st]);
  sh_line(w, ";");
  lines = (lines + 1);
} else {
  if (kind == S_RETURN) {
  sh_pad(w, indent);
  if ((c[0]).na[st] < 0) {
  sh_line(w, "return;");
} else {
  sh_puts(w, "return ");
  sh_emit_expr(c, w, (c[0]).na[st]);
  sh_line(w, ";");
}
  lines = (lines + 1);
} else {
  if (kind == S_IF) {
  sh_pad(w, indent);
  sh_puts(w, "if (");
  sh_emit_expr(c, w, (c[0]).na[st]);
  sh_line(w, ") {");
  lines = (lines + 1);
  lines = (lines + sh_emit_stmts(c, w, (c[0]).nb[st], (indent + 1)));
  if ((c[0]).nc[st] >= 0) {
  sh_pad(w, indent);
  sh_line(w, "} else {");
  lines = (lines + 1);
  lines = (lines + sh_emit_stmts(c, w, (c[0]).nc[st], (indent + 1)));
}
  sh_pad(w, indent);
  sh_line(w, "}");
  lines = (lines + 1);
} else {
  int32_t wg = (c[0]).target;
  sh_env_set(c, (c[0]).s1[st], (c[0]).e1[st], sh_ty_known(c, 1));
  sh_pad(w, indent);
  if (wg == SH_WGSL) {
  sh_puts(w, "for (var ");
  sh_put_name(c, w, st);
  sh_puts(w, ": i32 = i32(");
} else {
  sh_puts(w, "for (int ");
  sh_put_name(c, w, st);
  sh_puts(w, " = int(");
}
  sh_emit_expr(c, w, (c[0]).na[st]);
  sh_puts(w, "); ");
  sh_put_name(c, w, st);
  if (wg == SH_WGSL) {
  sh_puts(w, " < i32(");
} else {
  sh_puts(w, " < int(");
}
  sh_emit_expr(c, w, (c[0]).nb[st]);
  sh_puts(w, "); ");
  sh_put_name(c, w, st);
  if (wg == SH_WGSL) {
  sh_puts(w, " = ");
  sh_put_name(c, w, st);
  sh_line(w, " + 1) {");
} else {
  sh_line(w, "++) {");
}
  lines = (lines + 1);
  lines = (lines + sh_emit_stmts(c, w, (c[0]).nc[st], (indent + 1)));
  sh_pad(w, indent);
  sh_line(w, "}");
  lines = (lines + 1);
}
}
}
}
  st = (c[0]).nx[st];
}
  return lines;
}

int32_t sh_has_color_assign(ShCtx* c, int32_t head) {
  int32_t st = head;
  while (st >= 0) {
  int32_t kind = (c[0]).nk[st];
  if (kind == S_ASSIGN && sh_node_is(c, st, "color") == 1) {
  return 1;
}
  if (kind == S_IF) {
  if (sh_has_color_assign(c, (c[0]).nb[st]) == 1 || sh_has_color_assign(c, (c[0]).nc[st]) == 1) {
  return 1;
}
}
  if (kind == S_FOR && sh_has_color_assign(c, (c[0]).nc[st]) == 1) {
  return 1;
}
  st = (c[0]).nx[st];
}
  return 0;
}

void sh_emit_fn(ShCtx* c, ShBuf* w, int32_t k) {
  (c[0]).nv = 0;
  int32_t wg = (c[0]).target;
  int32_t ret = 0;
  if (wg == SH_METAL) {
  ret = sh_map_type(c, (c[0]).frt[k]);
}
  ShBuf* params = (ShBuf*)(flowc_shader_buf_new(64));
  int32_t i = 0;
  while (i < (c[0]).fpn[k] && (c[0]).err == 0) {
  int32_t pi = ((c[0]).fp0[k] + i);
  int32_t mt = sh_map_type(c, (c[0]).pat[pi]);
  if ((c[0]).err == 0) {
  sh_env_set(c, (c[0]).pas[pi], (c[0]).pae[pi], mt);
  if (i > 0) {
  sh_puts(params, ", ");
}
  if (wg == SH_WGSL) {
  sh_put_span(params, (c[0]).p, (c[0]).pas[pi], (c[0]).pae[pi]);
  sh_puts(params, ": ");
  sh_put_ty(c, params, mt);
} else {
  sh_put_ty(c, params, mt);
  sh_putc(params, 32);
  sh_put_span(params, (c[0]).p, (c[0]).pas[pi], (c[0]).pae[pi]);
}
}
  i = (i + 1);
}
  if ((c[0]).err != 0) {
  flowc_shader_buf_free(params);
  return;
}
  ShBuf* body = (ShBuf*)(flowc_shader_buf_new(256));
  int32_t stmts = sh_parse_body_span(c, (c[0]).fbs[k], (c[0]).fbe[k]);
  int32_t nl = 0;
  if ((c[0]).err == 0) {
  nl = sh_emit_stmts(c, body, stmts, 1);
}
  if ((c[0]).err == 0 && wg == SH_WGSL) {
  ret = sh_map_type(c, (c[0]).frt[k]);
}
  if ((c[0]).err == 0) {
  if (wg == SH_WGSL) {
  sh_puts(w, "fn ");
  sh_put_span(w, (c[0]).p, (c[0]).fns[k], (c[0]).fne[k]);
  sh_putc(w, 40);
  sh_put_span(w, (params[0]).buf, 0, (params[0]).len);
  sh_puts(w, ") -> ");
  sh_put_ty(c, w, ret);
  sh_line(w, " {");
} else {
  sh_puts(w, "static inline ");
  sh_put_ty(c, w, ret);
  sh_putc(w, 32);
  sh_put_span(w, (c[0]).p, (c[0]).fns[k], (c[0]).fne[k]);
  sh_putc(w, 40);
  sh_put_span(w, (params[0]).buf, 0, (params[0]).len);
  sh_line(w, ") {");
}
  sh_put_span(w, (body[0]).buf, 0, (body[0]).len);
  if (nl == 0) {
  sh_putc(w, 10);
}
  sh_line(w, "}");
}
  flowc_shader_buf_free(params);
  flowc_shader_buf_free(body);
}

void sh_emit_fill(ShCtx* c, ShBuf* w, int32_t k) {
  int32_t stmts = sh_parse_body_span(c, (c[0]).flbs[k], (c[0]).flbe[k]);
  if ((c[0]).err != 0) {
  return;
}
  if (sh_has_color_assign(c, stmts) == 0) {
  if (sh_err(c) == 1) {
  sh_puts((c[0]).msg, "shader fill '");
  sh_put_span((c[0]).msg, (c[0]).p, (c[0]).fls[k], (c[0]).fle[k]);
  sh_puts((c[0]).msg, "' must assign `color = ...`");
}
  return;
}
  (c[0]).nv = 0;
  if ((c[0]).target == SH_WGSL) {
  sh_line(w, "@fragment");
  sh_puts(w, "fn ");
  sh_put_span(w, (c[0]).p, (c[0]).fls[k], (c[0]).fle[k]);
  sh_line(w, "_frag(in: FlowVertexOut) -> @location(0) vec4<f32> {");
  sh_line(w, "    let uv: vec2<f32> = in.uv;");
  sh_line(w, "    var color: vec4<f32> = vec4<f32>(0.0, 0.0, 0.0, 1.0);");
} else {
  sh_puts(w, "fragment float4 ");
  sh_put_span(w, (c[0]).p, (c[0]).fls[k], (c[0]).fle[k]);
  sh_line(w, "_frag(");
  sh_line(w, "    FlowVertexOut in [[stage_in]],");
  sh_line(w, "    constant FlowShaderUniforms& uniforms [[buffer(0)]]");
  sh_line(w, ") {");
  sh_line(w, "    float2 uv = in.uv;");
  sh_line(w, "    float4 color = float4(0.0, 0.0, 0.0, 1.0);");
}
  sh_emit_stmts(c, w, stmts, 1);
  sh_line(w, "    return color;");
  sh_line(w, "}");
}

int32_t flowc_shader_gen(ShCtx* c, ShBuf* w, int32_t target, uint8_t* name, int32_t nlen, int32_t only) {
  (c[0]).target = target;
  int32_t nsel = 0;
  int32_t k = 0;
  while (k < (c[0]).nfl) {
  if ((nlen < 0 || flowc_shader_fill_named(c, k, name, nlen) == 1) && (only < 0 || only == k)) {
  nsel = (nsel + 1);
}
  k = (k + 1);
}
  if (nsel == 0) {
  sh_fail(c, "No `shader fill` blocks in module");
  return (0 - 1);
}
  if (target == SH_WGSL) {
  sh_prelude_wgsl(w);
} else {
  sh_prelude_metal(w);
}
  sh_puts(w, "\n\n");
  int32_t f = 0;
  while (f < (c[0]).nfn && (c[0]).err == 0) {
  sh_emit_fn(c, w, f);
  sh_puts(w, "\n\n");
  f = (f + 1);
}
  int32_t seen = 0;
  k = 0;
  while (k < (c[0]).nfl && (c[0]).err == 0) {
  if ((nlen < 0 || flowc_shader_fill_named(c, k, name, nlen) == 1) && (only < 0 || only == k)) {
  sh_emit_fill(c, w, k);
  seen = (seen + 1);
  if (seen < nsel) {
  sh_putc(w, 10);
}
}
  k = (k + 1);
}
  if ((c[0]).err != 0) {
  return (0 - 1);
}
  return 0;
}

void sh_prelude_metal(ShBuf* w) {
  sh_line(w, "");
  sh_line(w, "#include <metal_stdlib>");
  sh_line(w, "using namespace metal;");
  sh_line(w, "");
  sh_line(w, "struct FlowShaderUniforms {");
  sh_line(w, "    float time;");
  sh_line(w, "    float width;");
  sh_line(w, "    float height;");
  sh_line(w, "};");
  sh_line(w, "");
  sh_line(w, "struct FlowVertexOut {");
  sh_line(w, "    float4 position [[position]];");
  sh_line(w, "    float2 uv;");
  sh_line(w, "};");
  sh_line(w, "");
  sh_line(w, "vertex FlowVertexOut flow_shader_vertex(uint vid [[vertex_id]]) {");
  sh_line(w, "    float2 pos;");
  sh_line(w, "    if (vid == 0) pos = float2(-1.0, -1.0);");
  sh_line(w, "    else if (vid == 1) pos = float2( 3.0, -1.0);");
  sh_line(w, "    else pos = float2(-1.0,  3.0);");
  sh_line(w, "    FlowVertexOut out;");
  sh_line(w, "    out.position = float4(pos, 0.0, 1.0);");
  sh_line(w, "    out.uv = float2(pos.x * 0.5 + 0.5, 1.0 - (pos.y * 0.5 + 0.5));");
  sh_line(w, "    return out;");
  sh_line(w, "}");
  sh_line(w, "");
  sh_puts(w, "// ");
  sh_rule(w, 2);
  sh_puts(w, " FSL standard library (hash / noise / palette) ");
  sh_rule(w, 19);
  sh_putc(w, 10);
  sh_line(w, "static inline float fsl_hash11(float p) {");
  sh_line(w, "    p = fract(p * 0.1031);");
  sh_line(w, "    p *= p + 33.33;");
  sh_line(w, "    p *= p + p;");
  sh_line(w, "    return fract(p);");
  sh_line(w, "}");
  sh_line(w, "static inline float fsl_hash21(float2 p) {");
  sh_line(w, "    float3 p3 = fract(float3(p.xyx) * 0.1031);");
  sh_line(w, "    p3 += dot(p3, p3.yzx + 33.33);");
  sh_line(w, "    return fract((p3.x + p3.y) * p3.z);");
  sh_line(w, "}");
  sh_line(w, "static inline float2 fsl_hash22(float2 p) {");
  sh_line(w, "    float3 p3 = fract(float3(p.xyx) * float3(0.1031, 0.1030, 0.0973));");
  sh_line(w, "    p3 += dot(p3, p3.yzx + 33.33);");
  sh_line(w, "    return fract((p3.xx + p3.yz) * p3.zy);");
  sh_line(w, "}");
  sh_line(w, "static inline float fsl_noise(float2 p) {");
  sh_line(w, "    float2 i = floor(p);");
  sh_line(w, "    float2 f = fract(p);");
  sh_line(w, "    float a = fsl_hash21(i);");
  sh_line(w, "    float b = fsl_hash21(i + float2(1.0, 0.0));");
  sh_line(w, "    float c = fsl_hash21(i + float2(0.0, 1.0));");
  sh_line(w, "    float d = fsl_hash21(i + float2(1.0, 1.0));");
  sh_line(w, "    float2 u = f * f * (3.0 - 2.0 * f);");
  sh_line(w, "    return mix(a, b, u.x) + (c - a) * u.y * (1.0 - u.x) + (d - b) * u.x * u.y;");
  sh_line(w, "}");
  sh_line(w, "static inline float fsl_fbm(float2 p) {");
  sh_line(w, "    float v = 0.0;");
  sh_line(w, "    float a = 0.5;");
  sh_line(w, "    for (int i = 0; i < 5; i++) {");
  sh_line(w, "        v += a * fsl_noise(p);");
  sh_line(w, "        p *= 2.0;");
  sh_line(w, "        a *= 0.5;");
  sh_line(w, "    }");
  sh_line(w, "    return v;");
  sh_line(w, "}");
  sh_line(w, "static inline float3 fsl_palette(float t) {");
  sh_line(w, "    float3 a = float3(0.5, 0.5, 0.5);");
  sh_line(w, "    float3 b = float3(0.5, 0.5, 0.5);");
  sh_line(w, "    float3 c = float3(1.0, 1.0, 1.0);");
  sh_line(w, "    float3 d = float3(0.00, 0.33, 0.67);");
  sh_line(w, "    return a + b * cos(6.28318 * (c * t + d));");
  sh_line(w, "}");
}

void sh_prelude_wgsl(ShBuf* w) {
  sh_line(w, "");
  sh_line(w, "struct FlowShaderUniforms {");
  sh_line(w, "    time: f32,");
  sh_line(w, "    width: f32,");
  sh_line(w, "    height: f32,");
  sh_line(w, "    _pad: f32,");
  sh_line(w, "};");
  sh_line(w, "");
  sh_line(w, "@group(0) @binding(0)");
  sh_line(w, "var<uniform> uniforms: FlowShaderUniforms;");
  sh_line(w, "");
  sh_line(w, "struct FlowVertexOut {");
  sh_line(w, "    @builtin(position) position: vec4<f32>,");
  sh_line(w, "    @location(0) uv: vec2<f32>,");
  sh_line(w, "};");
  sh_line(w, "");
  sh_line(w, "@vertex");
  sh_line(w, "fn flow_shader_vertex(@builtin(vertex_index) vid: u32) -> FlowVertexOut {");
  sh_line(w, "    var pos: vec2<f32>;");
  sh_line(w, "    if (vid == 0u) {");
  sh_line(w, "        pos = vec2<f32>(-1.0, -1.0);");
  sh_line(w, "    } else if (vid == 1u) {");
  sh_line(w, "        pos = vec2<f32>(3.0, -1.0);");
  sh_line(w, "    } else {");
  sh_line(w, "        pos = vec2<f32>(-1.0, 3.0);");
  sh_line(w, "    }");
  sh_line(w, "");
  sh_line(w, "    var out: FlowVertexOut;");
  sh_line(w, "    out.position = vec4<f32>(pos, 0.0, 1.0);");
  sh_line(w, "    out.uv = vec2<f32>(pos.x * 0.5 + 0.5, 1.0 - (pos.y * 0.5 + 0.5));");
  sh_line(w, "    return out;");
  sh_line(w, "}");
  sh_line(w, "");
  sh_line(w, "fn fsl_hash11(value: f32) -> f32 {");
  sh_line(w, "    var p = fract(value * 0.1031);");
  sh_line(w, "    p = p * (p + 33.33);");
  sh_line(w, "    p = p * (p + p);");
  sh_line(w, "    return fract(p);");
  sh_line(w, "}");
  sh_line(w, "");
  sh_line(w, "fn fsl_hash21(value: vec2<f32>) -> f32 {");
  sh_line(w, "    var p3 = fract(vec3<f32>(value.x, value.y, value.x) * vec3<f32>(0.1031));");
  sh_line(w, "    let d = dot(p3, p3.yzx + vec3<f32>(33.33));");
  sh_line(w, "    p3 = p3 + vec3<f32>(d);");
  sh_line(w, "    return fract((p3.x + p3.y) * p3.z);");
  sh_line(w, "}");
  sh_line(w, "");
  sh_line(w, "fn fsl_noise(p: vec2<f32>) -> f32 {");
  sh_line(w, "    let i = floor(p);");
  sh_line(w, "    let f = fract(p);");
  sh_line(w, "    let a = fsl_hash21(i);");
  sh_line(w, "    let b = fsl_hash21(i + vec2<f32>(1.0, 0.0));");
  sh_line(w, "    let c = fsl_hash21(i + vec2<f32>(0.0, 1.0));");
  sh_line(w, "    let d = fsl_hash21(i + vec2<f32>(1.0, 1.0));");
  sh_line(w, "    let u = f * f * (vec2<f32>(3.0) - vec2<f32>(2.0) * f);");
  sh_line(w, "    return mix(a, b, u.x) + (c - a) * u.y * (1.0 - u.x) + (d - b) * u.x * u.y;");
  sh_line(w, "}");
  sh_line(w, "");
  sh_line(w, "fn fsl_fbm(value: vec2<f32>) -> f32 {");
  sh_line(w, "    var p = value;");
  sh_line(w, "    var v = 0.0;");
  sh_line(w, "    var a = 0.5;");
  sh_line(w, "    for (var i: i32 = 0; i < 5; i = i + 1) {");
  sh_line(w, "        v = v + a * fsl_noise(p);");
  sh_line(w, "        p = p * vec2<f32>(2.0);");
  sh_line(w, "        a = a * 0.5;");
  sh_line(w, "    }");
  sh_line(w, "    return v;");
  sh_line(w, "}");
  sh_line(w, "");
  sh_line(w, "fn fsl_palette(t: f32) -> vec3<f32> {");
  sh_line(w, "    let a = vec3<f32>(0.5, 0.5, 0.5);");
  sh_line(w, "    let b = vec3<f32>(0.5, 0.5, 0.5);");
  sh_line(w, "    let c = vec3<f32>(1.0, 1.0, 1.0);");
  sh_line(w, "    let d = vec3<f32>(0.00, 0.33, 0.67);");
  sh_line(w, "    return a + b * cos(vec3<f32>(6.28318) * (c * vec3<f32>(t) + d));");
  sh_line(w, "}");
}


typedef struct FlowcOverloadTable {
  uint8_t* src;
  int32_t* ns;
  int32_t* ne;
  int32_t* arity;
  int32_t* decl;
  int32_t len;
  int32_t cap;
  int32_t err;
} FlowcOverloadTable;

int32_t overload_span_eq(uint8_t* src, int32_t a0, int32_t a1, int32_t b0, int32_t b1);
FlowcOverloadTable flowc_overload_table_init(uint8_t* src, int32_t cap);
void flowc_overload_table_free(FlowcOverloadTable* table);
int32_t flowc_overload_table_add(FlowcOverloadTable* table, int32_t name_start, int32_t name_end, int32_t arity, int32_t decl);
int32_t flowc_overload_table_count(FlowcOverloadTable table, int32_t name_start, int32_t name_end, int32_t arity);
int32_t flowc_overload_table_nth_decl(FlowcOverloadTable table, int32_t name_start, int32_t name_end, int32_t arity, int32_t nth);
int32_t flowc_overload_table_has_decl(FlowcOverloadTable table, int32_t name_start, int32_t name_end, int32_t decl);
int32_t overload_span_eq(uint8_t* src, int32_t a0, int32_t a1, int32_t b0, int32_t b1) {
  if ((a1 - a0) != (b1 - b0)) {
  return 0;
}
  int32_t i = 0;
  while ((a0 + i) < a1) {
  if (src[(a0 + i)] != src[(b0 + i)]) {
  return 0;
}
  i = (i + 1);
}
  return 1;
}

FlowcOverloadTable flowc_overload_table_init(uint8_t* src, int32_t cap) {
  if (cap <= 0) {
  return (FlowcOverloadTable){ .src = src, .ns = NULL, .ne = NULL, .arity = NULL, .decl = NULL, .len = 0, .cap = 0, .err = 1 };
}
  uint8_t* raw_ns = (uint8_t*)(malloc(((int64_t)(cap) * 4)));
  uint8_t* raw_ne = (uint8_t*)(malloc(((int64_t)(cap) * 4)));
  uint8_t* raw_arity = (uint8_t*)(malloc(((int64_t)(cap) * 4)));
  uint8_t* raw_decl = (uint8_t*)(malloc(((int64_t)(cap) * 4)));
  if (raw_ns == NULL || raw_ne == NULL || raw_arity == NULL || raw_decl == NULL) {
  if (raw_ns != NULL) {
  free(raw_ns);
}
  if (raw_ne != NULL) {
  free(raw_ne);
}
  if (raw_arity != NULL) {
  free(raw_arity);
}
  if (raw_decl != NULL) {
  free(raw_decl);
}
  return (FlowcOverloadTable){ .src = src, .ns = NULL, .ne = NULL, .arity = NULL, .decl = NULL, .len = 0, .cap = 0, .err = 1 };
}
  return (FlowcOverloadTable){ .src = src, .ns = (int32_t*)(raw_ns), .ne = (int32_t*)(raw_ne), .arity = (int32_t*)(raw_arity), .decl = (int32_t*)(raw_decl), .len = 0, .cap = cap, .err = 0 };
}

void flowc_overload_table_free(FlowcOverloadTable* table) {
  if ((table[0]).ns != NULL) {
  free((table[0]).ns);
  (table[0]).ns = NULL;
}
  if ((table[0]).ne != NULL) {
  free((table[0]).ne);
  (table[0]).ne = NULL;
}
  if ((table[0]).arity != NULL) {
  free((table[0]).arity);
  (table[0]).arity = NULL;
}
  if ((table[0]).decl != NULL) {
  free((table[0]).decl);
  (table[0]).decl = NULL;
}
  (table[0]).len = 0;
  (table[0]).cap = 0;
}

int32_t flowc_overload_table_add(FlowcOverloadTable* table, int32_t name_start, int32_t name_end, int32_t arity, int32_t decl) {
  if ((table[0]).err != 0) {
  return (0 - 1);
}
  if (name_start < 0 || name_end <= name_start || arity < 0 || decl < 0) {
  return (0 - 1);
}
  if ((table[0]).len >= (table[0]).cap) {
  (table[0]).err = 1;
  return (0 - 1);
}
  int32_t i = (table[0]).len;
  (table[0]).ns[i] = name_start;
  (table[0]).ne[i] = name_end;
  (table[0]).arity[i] = arity;
  (table[0]).decl[i] = decl;
  (table[0]).len = (i + 1);
  return i;
}

int32_t flowc_overload_table_count(FlowcOverloadTable table, int32_t name_start, int32_t name_end, int32_t arity) {
  int32_t count = 0;
  int32_t i = 0;
  while (i < (table).len) {
  if ((table).arity[i] == arity) {
  if (overload_span_eq((table).src, name_start, name_end, (table).ns[i], (table).ne[i]) == 1) {
  count = (count + 1);
}
}
  i = (i + 1);
}
  return count;
}

int32_t flowc_overload_table_nth_decl(FlowcOverloadTable table, int32_t name_start, int32_t name_end, int32_t arity, int32_t nth) {
  if (nth < 0) {
  return (0 - 1);
}
  int32_t seen = 0;
  int32_t i = 0;
  while (i < (table).len) {
  if ((table).arity[i] == arity) {
  if (overload_span_eq((table).src, name_start, name_end, (table).ns[i], (table).ne[i]) == 1) {
  if (seen == nth) {
  return (table).decl[i];
}
  seen = (seen + 1);
}
}
  i = (i + 1);
}
  return (0 - 1);
}

int32_t flowc_overload_table_has_decl(FlowcOverloadTable table, int32_t name_start, int32_t name_end, int32_t decl) {
  int32_t i = 0;
  while (i < (table).len) {
  if ((table).decl[i] == decl) {
  if (overload_span_eq((table).src, name_start, name_end, (table).ns[i], (table).ne[i]) == 1) {
  return 1;
}
}
  i = (i + 1);
}
  return 0;
}


int32_t overload_registry_unwrap_fn(AstArena arena, int32_t item);
void flowc_overload_registry_reset(FlowcOverloadTable* table, uint8_t* src);
int32_t flowc_overload_registry_collect(FlowcOverloadTable* table, AstArena arena, int32_t root);
int32_t overload_registry_unwrap_fn(AstArena arena, int32_t item) {
  if (item == AST_NONE || item < 0 || item >= (arena).len) {
  return AST_NONE;
}
  if (((arena).nodes[item]).kind == AST_FN) {
  return item;
}
  if (((arena).nodes[item]).kind == AST_EXPORT) {
  int32_t inner = ((arena).nodes[item]).a;
  if (inner != AST_NONE && inner >= 0 && inner < (arena).len) {
  if (((arena).nodes[inner]).kind == AST_FN) {
  return inner;
}
}
}
  return AST_NONE;
}

void flowc_overload_registry_reset(FlowcOverloadTable* table, uint8_t* src) {
  (table[0]).src = src;
  (table[0]).len = 0;
  if ((table[0]).cap <= 0 || (table[0]).ns == NULL || (table[0]).ne == NULL || (table[0]).arity == NULL || (table[0]).decl == NULL) {
  (table[0]).err = 1;
  return;
}
  (table[0]).err = 0;
}

int32_t flowc_overload_registry_collect(FlowcOverloadTable* table, AstArena arena, int32_t root) {
  if (root == AST_NONE || root < 0 || root >= (arena).len) {
  return (0 - 1);
}
  if (((arena).nodes[root]).kind != AST_PROGRAM || (table[0]).err != 0) {
  return (0 - 1);
}
  int32_t before = (table[0]).len;
  int32_t item = ((arena).nodes[root]).a;
  while (item != AST_NONE) {
  int32_t fn = overload_registry_unwrap_fn(arena, item);
  if (fn != AST_NONE && ((arena).nodes[fn]).c == AST_NONE) {
  item = ((arena).nodes[item]).next;
  continue;
}
  if (fn != AST_NONE) {
  int32_t arity = flowc_ast_chain_len(arena, ((arena).nodes[fn]).a);
  if (flowc_overload_table_add(table, ((arena).nodes[fn]).name_start, ((arena).nodes[fn]).name_end, arity, fn) < 0) {
  return (0 - 1);
}
}
  item = ((arena).nodes[item]).next;
}
  return ((table[0]).len - before);
}


typedef struct FxBuf {
  uint8_t* buf;
  int32_t cap;
  int32_t len;
  int32_t err;
} FxBuf;

static const int32_t FX_MAX_FIELDS = 64;
static const int32_t FX_REC = 9;
static const int32_t FX_NAME_S = 0;
static const int32_t FX_NAME_E = 1;
static const int32_t FX_N_S = 2;
static const int32_t FX_N_E = 3;
static const int32_t FX_L_S = 4;
static const int32_t FX_L_E = 5;
static const int32_t FX_R_S = 6;
static const int32_t FX_R_E = 7;
static const int32_t FX_EVOLVED = 8;
void fx_putc(FxBuf* w, uint8_t c);
void fx_puts(FxBuf* w, const char* s);
void fx_put_span(FxBuf* w, uint8_t* src, int32_t s, int32_t e);
int32_t fx_is_space(uint8_t c);
int32_t fx_is_word(uint8_t c);
int32_t fx_is_digit(uint8_t c);
int32_t fx_is_numch(uint8_t c);
int32_t fx_skip_ws(uint8_t* p, int32_t i, int32_t e);
int32_t fx_word_end(uint8_t* p, int32_t i, int32_t e);
int32_t fx_numch_end(uint8_t* p, int32_t i, int32_t e);
int32_t fx_lit_at(uint8_t* p, int32_t i, int32_t e, const char* lit);
int32_t fx_span_eq(uint8_t* p, int32_t a0, int32_t a1, int32_t b0, int32_t b1);
int32_t fx_span_has(uint8_t* p, int32_t s, int32_t e, uint8_t c);
int32_t fx_span_count(uint8_t* p, int32_t s, int32_t e, uint8_t c);
int32_t fx_span_find(uint8_t* p, int32_t s, int32_t e, uint8_t c);
void fx_strip(uint8_t* p, int32_t* se);
void fx_strip_comments(uint8_t* p, int32_t* se);
int32_t fx_eol_len(uint8_t* p, int32_t i, int32_t n);
int32_t fx_split_lines(uint8_t* p, int32_t n, int32_t* ls, int32_t* le);
int32_t fx_dsl_head_at(uint8_t* p, int32_t i, int32_t n);
int32_t flowc_field_has_dsl(uint8_t* p, int32_t n);
void fx_err_name(FxBuf* err, uint8_t* p, const char* pre, int32_t s, int32_t e, const char* post);
int32_t fx_match_field(uint8_t* p, int32_t s, int32_t e, int32_t* caps);
int32_t fx_match_boundary_head(uint8_t* p, int32_t s, int32_t e, int32_t* caps);
int32_t fx_match_evolve(uint8_t* p, int32_t s, int32_t e, int32_t* caps);
int32_t fx_match_lap_tail(uint8_t* p, int32_t s, int32_t e, int32_t* caps);
int32_t fx_match_lap(uint8_t* p, int32_t s, int32_t e, int32_t* caps);
int32_t fx_match_assign(uint8_t* p, int32_t s, int32_t e, int32_t* caps);
int32_t fx_is_side_start(uint8_t* p, int32_t s, int32_t e, int32_t k);
int32_t fx_extract_block(uint8_t* p, int32_t* ls, int32_t* le, int32_t nlines, int32_t start, int32_t* bs, int32_t* be, int32_t* cnt);
void fx_emit_int_span(FxBuf* w, uint8_t* p, int32_t s, int32_t e);
int32_t fx_int_le_one(uint8_t* p, int32_t s, int32_t e);
int32_t fx_find_field(uint8_t* p, int32_t* rec, int32_t nf, int32_t s, int32_t e);
void fx_emit_helpers(FxBuf* w, uint8_t* p, int32_t* rec, int32_t nf);
int32_t fx_find_main(uint8_t* m, int32_t n);
int32_t fx_contains(uint8_t* m, int32_t n, const char* lit);
int32_t fx_parse(uint8_t* p, int32_t* ls, int32_t* le, int32_t nlines, int32_t* keep, int32_t* rec, FxBuf* err);
int32_t flowc_field_expand(uint8_t* p, int32_t n, FxBuf* out, FxBuf* err);
int32_t flowc_field_expand_in_place(uint8_t* buf, int32_t n, int32_t cap);
void fx_putc(FxBuf* w, uint8_t c) {
  if ((w[0]).len >= (w[0]).cap) {
  (w[0]).err = 1;
  return;
}
  (w[0]).buf[(w[0]).len] = c;
  (w[0]).len = ((w[0]).len + 1);
}

void fx_puts(FxBuf* w, const char* s) {
  uint8_t* p = (uint8_t*)(s);
  int32_t n = (int32_t)(strlen(s));
  int32_t i = 0;
  while (i < n) {
  fx_putc(w, p[i]);
  i = (i + 1);
}
}

void fx_put_span(FxBuf* w, uint8_t* src, int32_t s, int32_t e) {
  int32_t i = s;
  while (i < e) {
  fx_putc(w, src[i]);
  i = (i + 1);
}
}

int32_t fx_is_space(uint8_t c) {
  if (c == 32) {
  return 1;
}
  if (c >= 9 && c <= 13) {
  return 1;
}
  if (c >= 28 && c <= 31) {
  return 1;
}
  return 0;
}

int32_t fx_is_word(uint8_t c) {
  if (c >= 48 && c <= 57) {
  return 1;
}
  if (c >= 65 && c <= 90) {
  return 1;
}
  if (c >= 97 && c <= 122) {
  return 1;
}
  if (c == 95) {
  return 1;
}
  if (c >= 128) {
  return 1;
}
  return 0;
}

int32_t fx_is_digit(uint8_t c) {
  if (c >= 48 && c <= 57) {
  return 1;
}
  return 0;
}

int32_t fx_is_numch(uint8_t c) {
  if (fx_is_digit(c) == 1) {
  return 1;
}
  if (c == 43 || c == 45 || c == 46 || c == 101 || c == 69) {
  return 1;
}
  return 0;
}

int32_t fx_skip_ws(uint8_t* p, int32_t i, int32_t e) {
  int32_t k = i;
  while (k < e && fx_is_space(p[k]) == 1) {
  k = (k + 1);
}
  return k;
}

int32_t fx_word_end(uint8_t* p, int32_t i, int32_t e) {
  int32_t k = i;
  while (k < e && fx_is_word(p[k]) == 1) {
  k = (k + 1);
}
  return k;
}

int32_t fx_numch_end(uint8_t* p, int32_t i, int32_t e) {
  int32_t k = i;
  while (k < e && fx_is_numch(p[k]) == 1) {
  k = (k + 1);
}
  return k;
}

int32_t fx_lit_at(uint8_t* p, int32_t i, int32_t e, const char* lit) {
  uint8_t* lp = (uint8_t*)(lit);
  int32_t n = (int32_t)(strlen(lit));
  if ((i + n) > e) {
  return 0;
}
  int32_t k = 0;
  while (k < n) {
  if (p[(i + k)] != lp[k]) {
  return 0;
}
  k = (k + 1);
}
  return 1;
}

int32_t fx_span_eq(uint8_t* p, int32_t a0, int32_t a1, int32_t b0, int32_t b1) {
  if ((a1 - a0) != (b1 - b0)) {
  return 0;
}
  int32_t k = 0;
  while (k < (a1 - a0)) {
  if (p[(a0 + k)] != p[(b0 + k)]) {
  return 0;
}
  k = (k + 1);
}
  return 1;
}

int32_t fx_span_has(uint8_t* p, int32_t s, int32_t e, uint8_t c) {
  int32_t k = s;
  while (k < e) {
  if (p[k] == c) {
  return 1;
}
  k = (k + 1);
}
  return 0;
}

int32_t fx_span_count(uint8_t* p, int32_t s, int32_t e, uint8_t c) {
  int32_t n = 0;
  int32_t k = s;
  while (k < e) {
  if (p[k] == c) {
  n = (n + 1);
}
  k = (k + 1);
}
  return n;
}

int32_t fx_span_find(uint8_t* p, int32_t s, int32_t e, uint8_t c) {
  int32_t k = s;
  while (k < e) {
  if (p[k] == c) {
  return k;
}
  k = (k + 1);
}
  return (0 - 1);
}

void fx_strip(uint8_t* p, int32_t* se) {
  int32_t s = se[0];
  int32_t e = se[1];
  while (s < e && fx_is_space(p[s]) == 1) {
  s = (s + 1);
}
  while (e > s && fx_is_space(p[(e - 1)]) == 1) {
  e = (e - 1);
}
  se[0] = s;
  se[1] = e;
}

void fx_strip_comments(uint8_t* p, int32_t* se) {
  int32_t hash = fx_span_find(p, se[0], se[1], 35);
  if (hash >= 0) {
  se[1] = hash;
}
  fx_strip(p, se);
}

int32_t fx_eol_len(uint8_t* p, int32_t i, int32_t n) {
  uint8_t c = p[i];
  if (c == 13) {
  if ((i + 1) < n && p[(i + 1)] == 10) {
  return 2;
}
  return 1;
}
  if (c == 10 || c == 11 || c == 12 || c == 28 || c == 29 || c == 30) {
  return 1;
}
  if (c == 194 && (i + 1) < n && p[(i + 1)] == 133) {
  return 2;
}
  if (c == 226 && (i + 2) < n && p[(i + 1)] == 128 && (p[(i + 2)] == 168 || p[(i + 2)] == 169)) {
  return 3;
}
  return 0;
}

int32_t fx_split_lines(uint8_t* p, int32_t n, int32_t* ls, int32_t* le) {
  int32_t count = 0;
  int32_t start = 0;
  int32_t i = 0;
  while (i < n) {
  int32_t t = fx_eol_len(p, i, n);
  if (t > 0) {
  ls[count] = start;
  le[count] = i;
  count = (count + 1);
  i = (i + t);
  start = i;
} else {
  i = (i + 1);
}
}
  if (start < n) {
  ls[count] = start;
  le[count] = n;
  count = (count + 1);
}
  return count;
}

int32_t fx_dsl_head_at(uint8_t* p, int32_t i, int32_t n) {
  int32_t k = fx_skip_ws(p, i, n);
  int32_t j = (0 - 1);
  uint8_t close = 58;
  if (fx_lit_at(p, k, n, "field") == 1) {
  j = (k + 5);
} else {
  if (fx_lit_at(p, k, n, "boundary") == 1) {
  j = (k + 8);
  close = 123;
}
}
  if (j < 0) {
  return 0;
}
  int32_t w = fx_skip_ws(p, j, n);
  if (w == j) {
  return 0;
}
  int32_t we = fx_word_end(p, w, n);
  if (we == w) {
  return 0;
}
  int32_t c = fx_skip_ws(p, we, n);
  if (c < n && p[c] == close) {
  return 1;
}
  return 0;
}

int32_t flowc_field_has_dsl(uint8_t* p, int32_t n) {
  int32_t i = 0;
  while (i <= n) {
  if (i == 0 || p[(i - 1)] == 10) {
  if (fx_dsl_head_at(p, i, n) == 1) {
  return 1;
}
}
  i = (i + 1);
}
  return 0;
}

void fx_err_name(FxBuf* err, uint8_t* p, const char* pre, int32_t s, int32_t e, const char* post) {
  fx_puts(err, pre);
  fx_put_span(err, p, s, e);
  fx_puts(err, post);
}

int32_t fx_match_field(uint8_t* p, int32_t s, int32_t e, int32_t* caps) {
  if (fx_lit_at(p, s, e, "field") == 0) {
  return 0;
}
  int32_t i = (s + 5);
  int32_t k = fx_skip_ws(p, i, e);
  if (k == i) {
  return 0;
}
  int32_t ne = fx_word_end(p, k, e);
  if (ne == k) {
  return 0;
}
  caps[0] = k;
  caps[1] = ne;
  i = fx_skip_ws(p, ne, e);
  if (i >= e || p[i] != 58) {
  return 0;
}
  i = fx_skip_ws(p, (i + 1), e);
  if (fx_lit_at(p, i, e, "f64") == 0) {
  return 0;
}
  i = fx_skip_ws(p, (i + 3), e);
  if (i >= e || p[i] != 91) {
  return 0;
}
  i = fx_skip_ws(p, (i + 1), e);
  int32_t d = i;
  while (d < e && fx_is_digit(p[d]) == 1) {
  d = (d + 1);
}
  if (d == i) {
  return 0;
}
  caps[2] = i;
  caps[3] = d;
  i = fx_skip_ws(p, d, e);
  if (i >= e || p[i] != 93) {
  return 0;
}
  i = (i + 1);
  k = fx_skip_ws(p, i, e);
  if (k == i) {
  return 0;
}
  if (fx_lit_at(p, k, e, "on") == 0) {
  return 0;
}
  i = (k + 2);
  k = fx_skip_ws(p, i, e);
  if (k == i) {
  return 0;
}
  int32_t de = fx_word_end(p, k, e);
  if (de == k) {
  return 0;
}
  caps[4] = k;
  caps[5] = de;
  if (fx_skip_ws(p, de, e) != e) {
  return 0;
}
  return 1;
}

int32_t fx_match_boundary_head(uint8_t* p, int32_t s, int32_t e, int32_t* caps) {
  if (fx_lit_at(p, s, e, "boundary") == 0) {
  return 0;
}
  int32_t i = (s + 8);
  int32_t k = fx_skip_ws(p, i, e);
  if (k == i) {
  return 0;
}
  int32_t ne = fx_word_end(p, k, e);
  if (ne == k) {
  return 0;
}
  int32_t b = fx_skip_ws(p, ne, e);
  if (b >= e || p[b] != 123) {
  return 0;
}
  caps[0] = k;
  caps[1] = ne;
  return 1;
}

int32_t fx_match_evolve(uint8_t* p, int32_t s, int32_t e, int32_t* caps) {
  int32_t ne = fx_word_end(p, s, e);
  if (ne == s) {
  return 0;
}
  int32_t k = fx_skip_ws(p, ne, e);
  if (k == ne) {
  return 0;
}
  if (fx_lit_at(p, k, e, "evolves") == 0) {
  return 0;
}
  int32_t i = (k + 7);
  k = fx_skip_ws(p, i, e);
  if (k == i) {
  return 0;
}
  if (fx_lit_at(p, k, e, "as") == 0) {
  return 0;
}
  i = (k + 2);
  k = fx_skip_ws(p, i, e);
  if (k == i || k >= e) {
  return 0;
}
  caps[0] = s;
  caps[1] = ne;
  caps[2] = k;
  caps[3] = e;
  return 1;
}

int32_t fx_match_lap_tail(uint8_t* p, int32_t s, int32_t e, int32_t* caps) {
  if (fx_lit_at(p, s, e, "laplacian") == 0) {
  return 0;
}
  int32_t i = fx_skip_ws(p, (s + 9), e);
  if (i >= e || p[i] != 40) {
  return 0;
}
  i = fx_skip_ws(p, (i + 1), e);
  int32_t ne = fx_word_end(p, i, e);
  if (ne == i) {
  return 0;
}
  int32_t name_s = i;
  i = fx_skip_ws(p, ne, e);
  if (i >= e || p[i] != 41) {
  return 0;
}
  i = (i + 1);
  caps[0] = name_s;
  caps[1] = ne;
  caps[2] = (0 - 1);
  caps[3] = (0 - 1);
  int32_t st = fx_skip_ws(p, i, e);
  if (st < e && p[st] == 42) {
  int32_t q = fx_skip_ws(p, (st + 1), e);
  int32_t n1 = fx_numch_end(p, q, e);
  if (n1 > q && fx_skip_ws(p, n1, e) == e) {
  caps[2] = q;
  caps[3] = n1;
  return 1;
}
  int32_t n2 = fx_word_end(p, q, e);
  if (n2 > q && fx_skip_ws(p, n2, e) == e) {
  caps[2] = q;
  caps[3] = n2;
  return 1;
}
}
  if (fx_skip_ws(p, i, e) == e) {
  return 1;
}
  return 0;
}

int32_t fx_match_lap(uint8_t* p, int32_t s, int32_t e, int32_t* caps) {
  int32_t n1 = fx_numch_end(p, s, e);
  if (n1 > s) {
  int32_t st = fx_skip_ws(p, n1, e);
  if (st < e && p[st] == 42) {
  if (fx_match_lap_tail(p, fx_skip_ws(p, (st + 1), e), e, caps) == 1) {
  caps[4] = s;
  caps[5] = n1;
  return 1;
}
}
}
  int32_t n2 = fx_word_end(p, s, e);
  if (n2 > s) {
  int32_t st2 = fx_skip_ws(p, n2, e);
  if (st2 < e && p[st2] == 42) {
  if (fx_match_lap_tail(p, fx_skip_ws(p, (st2 + 1), e), e, caps) == 1) {
  caps[4] = s;
  caps[5] = n2;
  return 1;
}
}
}
  if (fx_match_lap_tail(p, s, e, caps) == 1) {
  caps[4] = (0 - 1);
  caps[5] = (0 - 1);
  return 1;
}
  return 0;
}

int32_t fx_match_assign(uint8_t* p, int32_t s, int32_t e, int32_t* caps) {
  int32_t side = 0;
  int32_t i = s;
  if (fx_lit_at(p, s, e, "left") == 1) {
  side = 1;
  i = (s + 4);
} else {
  if (fx_lit_at(p, s, e, "right") == 1) {
  side = 2;
  i = (s + 5);
}
}
  if (side == 0) {
  return 0;
}
  i = fx_skip_ws(p, i, e);
  if (i >= e || p[i] != 61) {
  return 0;
}
  i = (i + 1);
  int32_t k = fx_skip_ws(p, i, e);
  if (k < e) {
  caps[0] = k;
  caps[1] = e;
  return side;
}
  if (k > i) {
  caps[0] = (k - 1);
  caps[1] = e;
  return side;
}
  return 0;
}

int32_t fx_is_side_start(uint8_t* p, int32_t s, int32_t e, int32_t k) {
  if (k > s && fx_is_word(p[(k - 1)]) == 1) {
  return 0;
}
  int32_t j = (0 - 1);
  if (fx_lit_at(p, k, e, "left") == 1) {
  j = (k + 4);
} else {
  if (fx_lit_at(p, k, e, "right") == 1) {
  j = (k + 5);
}
}
  if (j < 0) {
  return 0;
}
  int32_t q = fx_skip_ws(p, j, e);
  if (q < e && p[q] == 61) {
  return 1;
}
  return 0;
}

int32_t fx_extract_block(uint8_t* p, int32_t* ls, int32_t* le, int32_t nlines, int32_t start, int32_t* bs, int32_t* be, int32_t* cnt) {
  int32_t depth = 0;
  int32_t i = start;
  int32_t nb = 0;
  while (i < nlines) {
  int32_t s = ls[i];
  int32_t e = le[i];
  depth = ((depth + fx_span_count(p, s, e, 123)) - fx_span_count(p, s, e, 125));
  int32_t has_open = fx_span_has(p, s, e, 123);
  if (i > start || has_open == 1) {
  if (depth > 0 || i == start && has_open == 1) {
  int32_t its = s;
  if (i == start) {
  its = (fx_span_find(p, s, e, 123) + 1);
}
  if (depth > 0) {
  int32_t ite = e;
  while (ite > its && p[(ite - 1)] == 125) {
  ite = (ite - 1);
}
  bs[nb] = its;
  be[nb] = ite;
  nb = (nb + 1);
} else {
  if (fx_span_has(p, s, e, 125) == 1) {
  int32_t ie2 = fx_span_find(p, its, e, 125);
  if (ie2 < 0) {
  ie2 = e;
}
  bs[nb] = its;
  be[nb] = ie2;
  nb = (nb + 1);
}
}
}
}
  if (depth <= 0 && i > start) {
  cnt[0] = nb;
  return (i + 1);
}
  i = (i + 1);
}
  cnt[0] = nb;
  return i;
}

void fx_emit_int_span(FxBuf* w, uint8_t* p, int32_t s, int32_t e) {
  int32_t k = s;
  while (k < (e - 1) && p[k] == 48) {
  k = (k + 1);
}
  fx_put_span(w, p, k, e);
}

int32_t fx_int_le_one(uint8_t* p, int32_t s, int32_t e) {
  int32_t k = s;
  while (k < (e - 1) && p[k] == 48) {
  k = (k + 1);
}
  if ((e - k) == 1 && (p[k] == 48 || p[k] == 49)) {
  return 1;
}
  return 0;
}

int32_t fx_find_field(uint8_t* p, int32_t* rec, int32_t nf, int32_t s, int32_t e) {
  int32_t f = 0;
  while (f < nf) {
  int32_t b = (f * FX_REC);
  if (fx_span_eq(p, rec[(b + FX_NAME_S)], rec[(b + FX_NAME_E)], s, e) == 1) {
  return f;
}
  f = (f + 1);
}
  return (0 - 1);
}

void fx_emit_helpers(FxBuf* w, uint8_t* p, int32_t* rec, int32_t nf) {
  int32_t f = 0;
  while (f < nf) {
  int32_t b = (f * FX_REC);
  int32_t ns = rec[(b + FX_NAME_S)];
  int32_t ne = rec[(b + FX_NAME_E)];
  if (f > 0) {
  fx_puts(w, "\n");
}
  fx_puts(w, "# generated from field ");
  fx_put_span(w, p, ns, ne);
  fx_puts(w, " : f64[");
  fx_emit_int_span(w, p, rec[(b + FX_N_S)], rec[(b + FX_N_E)]);
  fx_puts(w, "] on Line\nconst ");
  fx_put_span(w, p, ns, ne);
  fx_puts(w, "_field_n: i32 = ");
  fx_emit_int_span(w, p, rec[(b + FX_N_S)], rec[(b + FX_N_E)]);
  fx_puts(w, "\n\nfunction ");
  fx_put_span(w, p, ns, ne);
  fx_puts(w, "_field_step(\n    u: ptr<f64>,\n    next: ptr<f64>,\n    r: f64\n) -> void {\n    heat_euler_step_1d(u, next, ");
  fx_emit_int_span(w, p, rec[(b + FX_N_S)], rec[(b + FX_N_E)]);
  fx_puts(w, ", r, ");
  if (rec[(b + FX_L_S)] < 0) {
  fx_puts(w, "0.0");
} else {
  fx_put_span(w, p, rec[(b + FX_L_S)], rec[(b + FX_L_E)]);
}
  fx_puts(w, ", ");
  if (rec[(b + FX_R_S)] < 0) {
  fx_puts(w, "0.0");
} else {
  fx_put_span(w, p, rec[(b + FX_R_S)], rec[(b + FX_R_E)]);
}
  fx_puts(w, ")\n}");
  if ((f + 1) < nf) {
  fx_puts(w, "\n");
}
  f = (f + 1);
}
}

int32_t fx_find_main(uint8_t* m, int32_t n) {
  int32_t i = 0;
  while (i < n) {
  if (m[i] == 10 && fx_lit_at(m, (i + 1), n, "function") == 1) {
  int32_t j = (i + 9);
  int32_t k = fx_skip_ws(m, j, n);
  if (k > j && fx_lit_at(m, k, n, "main") == 1) {
  int32_t q = fx_skip_ws(m, (k + 4), n);
  if (q < n && m[q] == 40) {
  return i;
}
}
}
  i = (i + 1);
}
  return (0 - 1);
}

int32_t fx_contains(uint8_t* m, int32_t n, const char* lit) {
  int32_t i = 0;
  while (i < n) {
  if (fx_lit_at(m, i, n, lit) == 1) {
  return 1;
}
  i = (i + 1);
}
  return 0;
}

int32_t fx_parse(uint8_t* p, int32_t* ls, int32_t* le, int32_t nlines, int32_t* keep, int32_t* rec, FxBuf* err) {
  int32_t* caps = (int32_t*)((int32_t*)(malloc(64)));
  int32_t* se = (int32_t*)((int32_t*)(malloc(16)));
  int32_t* cnt = (int32_t*)((int32_t*)(malloc(16)));
  int32_t* bs = (int32_t*)((int32_t*)(malloc(((int64_t)((nlines + 1)) * 4))));
  int32_t* be = (int32_t*)((int32_t*)(malloc(((int64_t)((nlines + 1)) * 4))));
  int32_t* its = (int32_t*)((int32_t*)(malloc(((int64_t)((nlines + 1)) * 4))));
  int32_t* ite = (int32_t*)((int32_t*)(malloc(((int64_t)((nlines + 1)) * 4))));
  int32_t nf = 0;
  int32_t rc = 0;
  int32_t i = 0;
  while (i < nlines && rc == 0) {
  keep[i] = 0;
  se[0] = ls[i];
  se[1] = le[i];
  fx_strip_comments(p, se);
  int32_t s = se[0];
  int32_t e = se[1];
  int32_t handled = 0;
  if (e > s && fx_match_field(p, s, e, caps) == 1) {
  handled = 1;
  if (fx_lit_at(p, caps[4], caps[5], "Line") == 0 || (caps[5] - caps[4]) != 4) {
  fx_err_name(err, p, "field '", caps[0], caps[1], "': only `on Line` is supported in Stage-1 (got '");
  fx_put_span(err, p, caps[4], caps[5]);
  fx_puts(err, "')");
  rc = (0 - 1);
} else {
  if (fx_int_le_one(p, caps[2], caps[3]) == 1) {
  fx_err_name(err, p, "field '", caps[0], caps[1], "': size must be > 1");
  rc = (0 - 1);
} else {
  if (fx_find_field(p, rec, nf, caps[0], caps[1]) >= 0) {
  fx_err_name(err, p, "duplicate field '", caps[0], caps[1], "'");
  rc = (0 - 1);
} else {
  if (nf >= FX_MAX_FIELDS) {
  fx_puts(err, "too many fields (flowc limit 64)");
  rc = (0 - 1);
} else {
  int32_t b = (nf * FX_REC);
  rec[(b + FX_NAME_S)] = caps[0];
  rec[(b + FX_NAME_E)] = caps[1];
  rec[(b + FX_N_S)] = caps[2];
  rec[(b + FX_N_E)] = caps[3];
  rec[(b + FX_L_S)] = (0 - 1);
  rec[(b + FX_L_E)] = (0 - 1);
  rec[(b + FX_R_S)] = (0 - 1);
  rec[(b + FX_R_E)] = (0 - 1);
  rec[(b + FX_EVOLVED)] = 0;
  nf = (nf + 1);
}
}
}
}
  i = (i + 1);
}
  if (handled == 0 && e > s && fx_match_boundary_head(p, s, e, caps) == 1) {
  handled = 1;
  int32_t bn_s = caps[0];
  int32_t bn_e = caps[1];
  int32_t fi = fx_find_field(p, rec, nf, bn_s, bn_e);
  if (fi < 0) {
  fx_err_name(err, p, "boundary '", bn_s, bn_e, "': declare `field ");
  fx_put_span(err, p, bn_s, bn_e);
  fx_puts(err, " : …` first");
  rc = (0 - 1);
} else {
  int32_t next_i = fx_extract_block(p, ls, le, nlines, i, bs, be, cnt);
  int32_t ni = 0;
  int32_t bi = 0;
  while (bi < cnt[0]) {
  se[0] = bs[bi];
  se[1] = be[bi];
  fx_strip(p, se);
  fx_strip_comments(p, se);
  int32_t b0 = se[0];
  int32_t b1 = se[1];
  if (b1 > b0) {
  int32_t ps = b0;
  int32_t k = (b0 + 1);
  while (k <= b1) {
  int32_t cut = 0;
  if (k == b1) {
  cut = 1;
} else {
  if (fx_is_side_start(p, b0, b1, k) == 1) {
  cut = 1;
}
}
  if (cut == 1) {
  se[0] = ps;
  se[1] = k;
  fx_strip(p, se);
  if (se[1] > se[0]) {
  its[ni] = se[0];
  ite[ni] = se[1];
  ni = (ni + 1);
}
  ps = k;
}
  k = (k + 1);
}
}
  bi = (bi + 1);
}
  int32_t l_s = (0 - 1);
  int32_t l_e = (0 - 1);
  int32_t r_s = (0 - 1);
  int32_t r_e = (0 - 1);
  int32_t ii = 0;
  while (ii < ni && rc == 0) {
  int32_t side = fx_match_assign(p, its[ii], ite[ii], caps);
  if (side == 0) {
  fx_err_name(err, p, "boundary '", bn_s, bn_e, "': expected `left = …` / `right = …`, got '");
  fx_put_span(err, p, its[ii], ite[ii]);
  fx_puts(err, "'");
  rc = (0 - 1);
} else {
  se[0] = caps[0];
  se[1] = caps[1];
  fx_strip(p, se);
  if (se[1] <= se[0]) {
  if (side == 1) {
  fx_err_name(err, p, "boundary '", bn_s, bn_e, "': empty left value");
} else {
  fx_err_name(err, p, "boundary '", bn_s, bn_e, "': empty right value");
}
  rc = (0 - 1);
} else {
  if (side == 1) {
  l_s = se[0];
  l_e = se[1];
} else {
  r_s = se[0];
  r_e = se[1];
}
}
}
  ii = (ii + 1);
}
  if (rc == 0) {
  if (l_s < 0 || r_s < 0) {
  fx_err_name(err, p, "boundary '", bn_s, bn_e, "': need both left and right");
  rc = (0 - 1);
} else {
  int32_t fb = (fi * FX_REC);
  rec[(fb + FX_L_S)] = l_s;
  rec[(fb + FX_L_E)] = l_e;
  rec[(fb + FX_R_S)] = r_s;
  rec[(fb + FX_R_E)] = r_e;
}
}
  int32_t z = (i + 1);
  while (z < next_i && z < nlines) {
  keep[z] = 0;
  z = (z + 1);
}
  i = next_i;
}
}
  if (handled == 0 && e > s && fx_match_evolve(p, s, e, caps) == 1) {
  int32_t ev = fx_find_field(p, rec, nf, caps[0], caps[1]);
  if (ev >= 0) {
  handled = 1;
  int32_t en_s = caps[0];
  int32_t en_e = caps[1];
  se[0] = caps[2];
  se[1] = caps[3];
  fx_strip(p, se);
  int32_t ok = fx_match_lap(p, se[0], se[1], caps);
  if (ok == 0 || fx_span_eq(p, caps[0], caps[1], en_s, en_e) == 0) {
  fx_err_name(err, p, "field '", en_s, en_e, "' evolves: Stage-1 expects `");
  fx_put_span(err, p, en_s, en_e);
  fx_puts(err, " evolves as laplacian(");
  fx_put_span(err, p, en_s, en_e);
  fx_puts(err, ")` or `c * laplacian(");
  fx_put_span(err, p, en_s, en_e);
  fx_puts(err, ")`");
  rc = (0 - 1);
} else {
  if (caps[4] >= 0 && caps[2] >= 0) {
  fx_err_name(err, p, "field '", en_s, en_e, "' evolves: use at most one multiplier");
  rc = (0 - 1);
} else {
  rec[((ev * FX_REC) + FX_EVOLVED)] = 1;
}
}
  i = (i + 1);
}
}
  if (handled == 0) {
  keep[i] = 1;
  i = (i + 1);
}
}
  if (rc == 0) {
  int32_t f = 0;
  while (f < nf && rc == 0) {
  int32_t b = (f * FX_REC);
  if (rec[(b + FX_EVOLVED)] == 0) {
  int32_t ms = rec[(b + FX_NAME_S)];
  int32_t me = rec[(b + FX_NAME_E)];
  fx_err_name(err, p, "field '", ms, me, "': missing `");
  fx_put_span(err, p, ms, me);
  fx_puts(err, " evolves as laplacian(");
  fx_put_span(err, p, ms, me);
  fx_puts(err, ")`");
  rc = (0 - 1);
}
  f = (f + 1);
}
}
  free((uint8_t*)(caps));
  free((uint8_t*)(se));
  free((uint8_t*)(cnt));
  free((uint8_t*)(bs));
  free((uint8_t*)(be));
  free((uint8_t*)(its));
  free((uint8_t*)(ite));
  if (rc != 0) {
  return (0 - 1);
}
  return nf;
}

int32_t flowc_field_expand(uint8_t* p, int32_t n, FxBuf* out, FxBuf* err) {
  if (flowc_field_has_dsl(p, n) == 0) {
  fx_put_span(out, p, 0, n);
  if ((out[0]).err != 0) {
  return (0 - 2);
}
  return (out[0]).len;
}
  int32_t* ls = (int32_t*)((int32_t*)(malloc(((int64_t)((n + 2)) * 4))));
  int32_t* le = (int32_t*)((int32_t*)(malloc(((int64_t)((n + 2)) * 4))));
  int32_t* keep = (int32_t*)((int32_t*)(malloc(((int64_t)((n + 2)) * 4))));
  int32_t* rec = (int32_t*)((int32_t*)(malloc(((int64_t)((FX_MAX_FIELDS * FX_REC)) * 4))));
  int32_t nlines = fx_split_lines(p, n, ls, le);
  int32_t nf = fx_parse(p, ls, le, nlines, keep, rec, err);
  int32_t rc = 0;
  if (nf < 0) {
  rc = (0 - 1);
} else {
  int32_t mcap = (n + 64);
  FxBuf mw = (FxBuf){ .buf = malloc((int64_t)((mcap + 1))), .cap = mcap, .len = 0, .err = 0 };
  if (nf > 0) {
  FxBuf sw = (FxBuf){ .buf = malloc((int64_t)((mcap + 1))), .cap = mcap, .len = 0, .err = 0 };
  int32_t first0 = 1;
  int32_t j0 = 0;
  while (j0 < nlines) {
  if (keep[j0] == 1) {
  if (first0 == 0) {
  fx_putc((&sw), 10);
}
  fx_put_span((&sw), p, ls[j0], le[j0]);
  first0 = 0;
}
  j0 = (j0 + 1);
}
  if (fx_contains((sw).buf, (sw).len, "import \"stdlib/dynamics/pde.flow\"") == 0) {
  fx_puts((&mw), "import \"stdlib/dynamics/pde.flow\"\n");
}
  fx_put_span((&mw), (sw).buf, 0, (sw).len);
  free((sw).buf);
} else {
  int32_t first = 1;
  int32_t j = 0;
  while (j < nlines) {
  if (keep[j] == 1) {
  if (first == 0) {
  fx_putc((&mw), 10);
}
  fx_put_span((&mw), p, ls[j], le[j]);
  first = 0;
}
  j = (j + 1);
}
}
  if (nf == 0) {
  fx_put_span(out, (mw).buf, 0, (mw).len);
} else {
  int32_t at = fx_find_main((mw).buf, (mw).len);
  if (at < 0) {
  int32_t te = (mw).len;
  while (te > 0 && fx_is_space((mw).buf[(te - 1)]) == 1) {
  te = (te - 1);
}
  fx_put_span(out, (mw).buf, 0, te);
  fx_puts(out, "\n\n");
  fx_emit_helpers(out, p, rec, nf);
  fx_puts(out, "\n");
} else {
  fx_put_span(out, (mw).buf, 0, at);
  fx_puts(out, "\n\n");
  fx_emit_helpers(out, p, rec, nf);
  fx_puts(out, "\n");
  fx_put_span(out, (mw).buf, at, (mw).len);
}
}
  free((mw).buf);
  if ((out[0]).err != 0) {
  rc = (0 - 2);
} else {
  rc = (out[0]).len;
}
}
  free((uint8_t*)(ls));
  free((uint8_t*)(le));
  free((uint8_t*)(keep));
  free((uint8_t*)(rec));
  return rc;
}

int32_t flowc_field_expand_in_place(uint8_t* buf, int32_t n, int32_t cap) {
  if (n < 0) {
  return n;
}
  if (flowc_field_has_dsl(buf, n) == 0) {
  return n;
}
  int32_t ocap = ((n * 2) + 65536);
  FxBuf ow = (FxBuf){ .buf = malloc((int64_t)((ocap + 1))), .cap = ocap, .len = 0, .err = 0 };
  FxBuf ew = (FxBuf){ .buf = malloc(1024), .cap = 1023, .len = 0, .err = 0 };
  int32_t rc = flowc_field_expand(buf, n, (&ow), (&ew));
  if (rc < 0) {
  if (rc == (0 - 2)) {
  puts("flowc field: expanded source too large");
} else {
  const char* head = "flowc field: ";
  uint8_t* hp = (uint8_t*)(head);
  FxBuf line = (FxBuf){ .buf = malloc(1100), .cap = 1099, .len = 0, .err = 0 };
  fx_put_span((&line), hp, 0, 13);
  fx_put_span((&line), (ew).buf, 0, (ew).len);
  (line).buf[(line).len] = 0;
  puts((const char*)((line).buf));
  free((line).buf);
}
  free((ow).buf);
  free((ew).buf);
  return (0 - 1);
}
  if (rc >= cap) {
  puts("flowc field: expanded source exceeds the source buffer");
  free((ow).buf);
  free((ew).buf);
  return (0 - 1);
}
  int32_t k = 0;
  while (k < rc) {
  buf[k] = (ow).buf[k];
  k = (k + 1);
}
  buf[rc] = 0;
  free((ow).buf);
  free((ew).buf);
  return rc;
}


typedef struct DySb {
  uint8_t* p;
  int32_t len;
  int32_t cap;
} DySb;

typedef struct DyC {
  int32_t err;
  DySb* msg;
  DySb* nm;
  double* fp;
  int32_t fnum;
  int32_t fcap;
  int32_t* bd_kind;
  int32_t* bd_var;
  int32_t* bd_hz;
  int32_t nbd;
  int32_t bdcap;
  int32_t* gl;
  int32_t ngl;
  int32_t glcap;
  int32_t* at_name;
  double* at_val;
  int32_t nat;
  int32_t atcap;
} DyC;

typedef struct Dp {
  int32_t cap;
  int32_t nsy;
  int32_t* sy_name;
  int32_t* sy_mode;
  double* sy_dt;
  int64_t* sy_n;
  int64_t* sy_m;
  int64_t* sy_p;
  int32_t* sy_a0;
  int32_t* sy_an;
  int32_t* sy_b0;
  int32_t* sy_bn;
  int32_t* sy_c0;
  int32_t* sy_cn;
  int32_t nhz;
  int32_t* hz_name;
  int32_t* hz_kind;
  int64_t* hz_steps;
  double* hz_gamma;
  int32_t nwf;
  int32_t* wf_name;
  int64_t* wf_w;
  int64_t* wf_h;
  int64_t* wf_tiles;
  int64_t* wf_seed;
  int64_t* wf_pc;
  int64_t* wf_pt;
  int64_t* wf_steps;
  int32_t nse;
  int32_t* se_sys;
  int32_t* se_b0;
  int32_t* se_bn;
  int32_t nga;
  int32_t* ga_sys;
  int32_t* ga_hz;
  int32_t* ga_k1;
  int32_t* ga_k2;
  int64_t* ga_pop;
  int64_t* ga_gen;
  double* ga_mut;
  int32_t ncl;
  int32_t* cl_sys;
  int32_t* cl_k1;
  int32_t* cl_k2;
  int32_t* cl_b0;
  int32_t* cl_bn;
  int32_t nanz;
  int32_t* an_sys;
  int32_t* an_k1;
  int32_t* an_k2;
  int32_t* an_hz;
  int32_t* an_rep;
  int32_t ncp;
  int32_t* cp_sys;
  int32_t* cp_field;
  int32_t* cp_rep;
  int32_t* cp_k1;
  int32_t* cp_k2;
  int32_t* cp_guid;
  int32_t* cp_b0;
  int32_t* cp_bn;
  int32_t ngd;
  int32_t* gd_sys;
  int32_t* gd_k1;
  int32_t* gd_k2;
  int32_t* gd_field;
  int32_t* gd_guid;
  int32_t* gd_hz;
  int32_t* gd_b0;
  int32_t* gd_bn;
  int32_t nrp;
  int32_t* rp_flow;
  int32_t* rp_mode;
  double* rp_dt;
  int64_t* rp_n;
  int64_t* rp_m;
  int64_t* rp_p;
  int32_t* rp_a0;
  int32_t* rp_an;
  int32_t* rp_b0;
  int32_t* rp_bn;
  int32_t* rp_c0;
  int32_t* rp_cn;
  int32_t* rp_at0;
  int32_t* rp_atn;
  int32_t* rp_nin;
  int32_t npt;
  int32_t* pt_flow;
  int32_t* pt_ax0;
  int32_t* pt_ax1;
  int64_t* pt_trail;
  int64_t* pt_w;
  int64_t* pt_h;
  int32_t* pt_set0;
  int32_t* pt_set1;
  double* pt_lo0;
  double* pt_hi0;
  double* pt_lo1;
  double* pt_hi1;
  int32_t* pt_k0;
  int32_t* pt_k1;
  int32_t nlq;
  int32_t* lq_sys;
  int32_t* lq_q0;
  int32_t* lq_qn;
  double* lq_r;
  int32_t* lq_g0;
  int32_t* lq_gn;
  int64_t* lq_it;
} Dp;

static const int32_t DY_ARROW = 8594;
static const int32_t DY_TIMES = 215;
static const int32_t DY_SECTION = 167;
static const int32_t DY_ELLIPSIS = 8230;
static const int32_t DY_DASH = 8212;
int32_t dy_old_space(int32_t c);
int32_t dy_old_starts(const char* s, const char* prefix);
const char* flowc_strip_comments(const char* line);
const char* flowc_strip_dynamics_namespace(const char* line);
DySb* dy_sb_new(int32_t cap);
void dy_putc(DySb* b, uint8_t ch);
void dy_puts(DySb* b, const char* s);
void dy_span(DySb* b, uint8_t* src, int32_t s, int32_t e);
void dy_i64(DySb* b, int64_t v);
void dy_utf8(DySb* b, int32_t cp);
int32_t dy_ws(uint8_t ch);
int32_t dy_digit(uint8_t ch);
int32_t dy_word(uint8_t ch);
void dy_strip(uint8_t* p, int32_t* se);
void dy_rstrip(uint8_t* p, int32_t* se);
void dy_strip_comments(uint8_t* p, int32_t* se);
int32_t dy_count(uint8_t* p, int32_t s, int32_t e, uint8_t ch);
int32_t dy_find(uint8_t* p, int32_t s, int32_t e, uint8_t ch);
int32_t dy_find_str(uint8_t* p, int32_t s, int32_t e, const char* lit);
int32_t dy_starts(uint8_t* p, int32_t s, int32_t e, const char* lit);
int32_t dy_eq(uint8_t* p, int32_t s, int32_t e, const char* lit);
int32_t dy_spans_eq(uint8_t* a, int32_t as0, int32_t ae, uint8_t* b, int32_t bs, int32_t be);
int32_t dy_has_nonws(uint8_t* p, int32_t s, int32_t e);
int32_t dy_eol_len(uint8_t* p, int32_t i, int32_t n);
int32_t dy_split_lines(uint8_t* p, int32_t n, int32_t* ls, int32_t* le);
int32_t dy_split_ws(uint8_t* p, int32_t s, int32_t e, int32_t* ws, int32_t* we);
int32_t dy_numch(uint8_t ch);
int32_t dy_match(uint8_t* p, int32_t s, int32_t e, const char* pat, int32_t* caps);
int32_t* dy_i32s(int32_t n);
int64_t* dy_i64s(int32_t n);
double* dy_f64s(int32_t n);
int32_t dy_name(DyC* c, uint8_t* p, int32_t s, int32_t e);
int32_t dy_name_lit(DyC* c, const char* s);
const char* dy_nstr(DyC* c, int32_t off);
int32_t dy_neq(DyC* c, int32_t a, int32_t b);
int32_t dy_neq_lit(DyC* c, int32_t a, const char* s);
void dy_pn(DySb* b, DyC* c, int32_t off);
int32_t dy_fpush(DyC* c, double v);
int32_t dy_bd(DyC* c, int32_t kind, int32_t var, int32_t hz);
int32_t dy_gl(DyC* c, int32_t off);
int32_t dy_at(DyC* c, int32_t name, double v);
DySb* dy_err(DyC* c);
void dy_err_s(DyC* c, const char* s);
void dy_repr_str(DySb* b, uint8_t* p, int32_t s, int32_t e);
int64_t dy_int(DyC* c, uint8_t* p, int32_t s0, int32_t e0);
int32_t dy_digits_us(uint8_t* p, int32_t k, int32_t e);
int32_t dy_lower_eq(uint8_t* p, int32_t s, int32_t e, const char* lit);
double dy_float(DyC* c, uint8_t* p, int32_t s0, int32_t e0);
int64_t dy_bits(double x);
int32_t dy_exact(double x, uint8_t* dig, int32_t* dp);
void dy_round(uint8_t* dig, int32_t nd, int32_t pr, uint8_t* out, int32_t* dp);
int32_t dy_fmt_special(DySb* b, double v, const char* zero);
void dy_exp10(DySb* b, int32_t x);
void dy_g17(DySb* b, double v);
void dy_repr(DySb* b, double v);
void dy_flow_f64(DySb* b, double v);
Dp* dy_prog_new(int32_t cap0);
int32_t dy_find_sys(DyC* c, Dp* g, int32_t name);
int32_t dy_find_hz(DyC* c, Dp* g, int32_t name);
int32_t dy_find_wf(DyC* c, Dp* g, int32_t name);
int32_t dy_sys_slot(DyC* c, Dp* g, int32_t name);
int32_t dy_hz_slot(DyC* c, Dp* g, int32_t name);
int32_t dy_wf_slot(DyC* c, Dp* g, int32_t name);
void dy_copy_sys(Dp* d, int32_t k, Dp* s, int32_t i);
void dy_merge(DyC* c, Dp* d, Dp* s);
int32_t dy_block(uint8_t* p, int32_t* ls, int32_t* le, int32_t nl, int32_t start, int32_t* bs, int32_t* be, int32_t* nb);
int32_t dy_block_keep(uint8_t* p, int32_t* ls, int32_t* le, int32_t nl, int32_t start, int32_t* bs, int32_t* be, int32_t* nb);
int32_t dy_floats(DyC* c, uint8_t* p, int32_t s, int32_t e, int32_t* f0);
int32_t dy_all_word(uint8_t* p, int32_t s, int32_t e);
void dy_parse_nmp(DyC* c, uint8_t* p, int32_t s, int32_t e, int64_t* nv, int64_t* mv, int64_t* pv, int32_t idx);
int64_t dy_int_part(DyC* c, uint8_t* p, int32_t s, int32_t e, int32_t k);
double dy_float_part(DyC* c, uint8_t* p, int32_t s, int32_t e, int32_t k);
int32_t dy_name_part(DyC* c, uint8_t* p, int32_t s, int32_t e, int32_t k);
void dy_parse_at(DyC* c, uint8_t* p, int32_t s0, int32_t e0, Dp* g, int32_t r);
int32_t dy_name_list(DyC* c, uint8_t* p, int32_t s0, int32_t e0);
int32_t dy_paren_form(uint8_t* p, int32_t s, int32_t e, const char* word, int32_t* se);
void dy_rep_linear_body(DyC* c, uint8_t* p, Dp* g, int32_t r, int32_t* bs, int32_t* be, int32_t nb);
void dy_portrait_body(DyC* c, uint8_t* p, Dp* g, int32_t t, int32_t* bs, int32_t* be, int32_t nb);
int32_t dy_rep_head(uint8_t* p, int32_t s, int32_t e, int32_t* caps);
void dy_extract_represent(DyC* c, uint8_t* p, int32_t n, Dp* g, DySb* out);
void dy_at_repr(DySb* m, DyC* c, Dp* g, int32_t r);
void dy_rep_prefix(DySb* m, DyC* c, Dp* g, int32_t r);
void dy_rep_to_dsys(DyC* c, Dp* g, int32_t r);
void dy_invalid(DyC* c, const char* what, uint8_t* p, int32_t s, int32_t e);
int32_t dy_arrow(uint8_t* p, int32_t s, int32_t e, int32_t* l, int32_t* r);
void dy_lqr_prefix(DySb* m, DyC* c, int32_t sys);
void dy_lqr(DyC* c, uint8_t* p, Dp* g, int32_t sys, int32_t* bs, int32_t* be, int32_t nb);
void dy_an_prefix(DySb* m, DyC* c, int32_t sys);
void dy_lqr_braces(DySb* m);
void dy_analyze_vision(DyC* c, uint8_t* p, Dp* g, int32_t sys, int32_t* bs, int32_t* be, int32_t nb);
void dy_validate_raw(DyC* c, Dp* g);
int32_t dy_cp_prefix(uint8_t* p, int32_t s, int32_t e, int32_t limit);
void dy_parse(DyC* c, uint8_t* p0, int32_t n0, Dp* g, DySb* out);
int32_t dy_parse_rest(DyC* c, uint8_t* p, Dp* g, int32_t* ls, int32_t* le, int32_t nl, int32_t i, int32_t s, int32_t e, int32_t* bs, int32_t* be, int32_t* nb, int32_t* kept);
void dy_ln(DySb* b, const char* s);
void dy_eol(DySb* b);
void dy_key_error(DyC* c, int32_t off);
int64_t dy_steps_or(DyC* c, Dp* g, int32_t name, int64_t dflt);
int32_t dy_bufs(DySb* b, int32_t* bi, int32_t count);
void dy_bufref(DySb* b, int32_t k);
void dy_bufargs(DySb* b, int32_t first, int32_t count);
void dy_flat_array(DySb* b, DyC* c, int32_t f0, int32_t fnn);
void dy_rep_array(DySb* b, int64_t n, const char* item);
void dy_matrix(DySb* b, DyC* c, int32_t name, const char* which, int64_t rows, int64_t cols);
void dy_ga_arrays(DySb* b, DySb* tag, int64_t pop);
void dy_tag(DySb* t, const char* pre, int32_t k);
void dy_tagp(DySb* b, DySb* t);
int32_t dy_is_identifier(DyC* c, int32_t off);
int32_t dy_compile(DyC* c, Dp* g, DySb* b);
void dy_compile_portraits(DyC* c, Dp* g, DySb* b);
int32_t dy_head_ns(uint8_t* p, int32_t k, int32_t n, int32_t* caps);
int32_t dy_head_at(uint8_t* p, int32_t i, int32_t n, int32_t* caps);
int32_t flowc_dynamics_has_dsl(uint8_t* p, int32_t n);
int32_t dy_contains(DySb* b, const char* lit);
void dy_prepend(DySb* b, const char* lit);
int32_t dy_find_main_call(uint8_t* p, int32_t n);
int32_t dy_find_main_body(uint8_t* p, int32_t n);
int32_t dy_expand(DyC* c, uint8_t* p, int32_t n, DySb* out);
DyC* dy_ctx_new(int32_t n);
int32_t flowc_dynamics_expand_in_place(uint8_t* buf, int32_t n, int32_t cap);
int32_t dy_old_space(int32_t c) {
  if (c == 32 || c == 9 || c == 13 || c == 10) {
  return 1;
}
  return 0;
}

int32_t dy_old_starts(const char* s, const char* prefix) {
  int32_t sl = (int32_t)(strlen(s));
  int32_t pl = (int32_t)(strlen(prefix));
  if (pl > sl) {
  return 0;
}
  uint8_t* sp = (uint8_t*)((uint8_t*)(s));
  uint8_t* pp = (uint8_t*)((uint8_t*)(prefix));
  int32_t i = 0;
  while (i < pl) {
  if (sp[i] != pp[i]) {
  return 0;
}
  i = (i + 1);
}
  return 1;
}

const char* flowc_strip_comments(const char* line) {
  int32_t n = (int32_t)(strlen(line));
  uint8_t* p = (uint8_t*)((uint8_t*)(line));
  int32_t hash_pos = (0 - 1);
  int32_t i = 0;
  while (i < n) {
  if (p[i] == 35) {
  hash_pos = i;
  break;
}
  i = (i + 1);
}
  int32_t end = n;
  if (hash_pos >= 0) {
  end = hash_pos;
}
  while (end > 0 && dy_old_space((int32_t)(p[(end - 1)])) == 1) {
  end = (end - 1);
}
  int32_t start = 0;
  while (start < end && dy_old_space((int32_t)(p[start])) == 1) {
  start = (start + 1);
}
  if (start >= end) {
  return "";
}
  int32_t len = (end - start);
  uint8_t* buf = (uint8_t*)(malloc((int64_t)((len + 1))));
  memcpy(buf, (p + start), (int64_t)(len));
  buf[len] = 0;
  return (const char*)(buf);
}

const char* flowc_strip_dynamics_namespace(const char* line) {
  const char* stripped = flowc_strip_comments(line);
  int32_t skip = 0;
  if (dy_old_starts(stripped, "dyn.") == 1) {
  skip = 4;
} else {
  if (dy_old_starts(stripped, "dynamics.") == 1) {
  skip = 9;
}
}
  if (skip == 0) {
  return stripped;
}
  int32_t n = (int32_t)(strlen(stripped));
  int32_t len = (n - skip);
  uint8_t* p = (uint8_t*)((uint8_t*)(stripped));
  uint8_t* buf = (uint8_t*)(malloc((int64_t)((len + 1))));
  memcpy(buf, (p + skip), (int64_t)(len));
  buf[len] = 0;
  return (const char*)(buf);
}

DySb* dy_sb_new(int32_t cap) {
  DySb* b = (DySb*)((DySb*)(malloc(16)));
  (b[0]).p = malloc((int64_t)((cap + 1)));
  (b[0]).len = 0;
  (b[0]).cap = cap;
  (b[0]).p[0] = 0;
  return b;
}

void dy_putc(DySb* b, uint8_t ch) {
  if (((b[0]).len + 1) >= (b[0]).cap) {
  int32_t ncap = (((b[0]).cap * 2) + 64);
  (b[0]).p = realloc((b[0]).p, (int64_t)((ncap + 1)));
  (b[0]).cap = ncap;
}
  (b[0]).p[(b[0]).len] = ch;
  (b[0]).len = ((b[0]).len + 1);
  (b[0]).p[(b[0]).len] = 0;
}

void dy_puts(DySb* b, const char* s) {
  uint8_t* sp = (uint8_t*)((uint8_t*)(s));
  int32_t i = 0;
  while (sp[i] != 0) {
  dy_putc(b, sp[i]);
  i = (i + 1);
}
}

void dy_span(DySb* b, uint8_t* src, int32_t s, int32_t e) {
  int32_t i = s;
  while (i < e) {
  dy_putc(b, src[i]);
  i = (i + 1);
}
}

void dy_i64(DySb* b, int64_t v) {
  if (v < 0) {
  dy_putc(b, 45);
  dy_i64(b, (0 - v));
  return;
}
  if (v >= 10) {
  dy_i64(b, (v / 10));
}
  dy_putc(b, (uint8_t)((48 + (v % 10))));
}

void dy_utf8(DySb* b, int32_t cp) {
  if (cp < 128) {
  dy_putc(b, (uint8_t)(cp));
  return;
}
  if (cp < 2048) {
  dy_putc(b, (uint8_t)((192 + (cp / 64))));
  dy_putc(b, (uint8_t)((128 + (cp % 64))));
  return;
}
  dy_putc(b, (uint8_t)((224 + (cp / 4096))));
  dy_putc(b, (uint8_t)((128 + ((cp / 64) % 64))));
  dy_putc(b, (uint8_t)((128 + (cp % 64))));
}

int32_t dy_ws(uint8_t ch) {
  if (ch == 32) {
  return 1;
}
  if (ch >= 9 && ch <= 13) {
  return 1;
}
  if (ch >= 28 && ch <= 31) {
  return 1;
}
  return 0;
}

int32_t dy_digit(uint8_t ch) {
  if (ch >= 48 && ch <= 57) {
  return 1;
}
  return 0;
}

int32_t dy_word(uint8_t ch) {
  if (dy_digit(ch) == 1) {
  return 1;
}
  if (ch >= 65 && ch <= 90) {
  return 1;
}
  if (ch >= 97 && ch <= 122) {
  return 1;
}
  if (ch == 95) {
  return 1;
}
  if (ch >= 128) {
  return 1;
}
  return 0;
}

void dy_strip(uint8_t* p, int32_t* se) {
  while (se[0] < se[1] && dy_ws(p[se[0]]) == 1) {
  se[0] = (se[0] + 1);
}
  while (se[1] > se[0] && dy_ws(p[(se[1] - 1)]) == 1) {
  se[1] = (se[1] - 1);
}
}

void dy_rstrip(uint8_t* p, int32_t* se) {
  while (se[1] > se[0] && dy_ws(p[(se[1] - 1)]) == 1) {
  se[1] = (se[1] - 1);
}
}

void dy_strip_comments(uint8_t* p, int32_t* se) {
  int32_t k = se[0];
  while (k < se[1]) {
  if (p[k] == 35) {
  se[1] = k;
  break;
}
  k = (k + 1);
}
  dy_strip(p, se);
}

int32_t dy_count(uint8_t* p, int32_t s, int32_t e, uint8_t ch) {
  int32_t k = s;
  int32_t c = 0;
  while (k < e) {
  if (p[k] == ch) {
  c = (c + 1);
}
  k = (k + 1);
}
  return c;
}

int32_t dy_find(uint8_t* p, int32_t s, int32_t e, uint8_t ch) {
  int32_t k = s;
  while (k < e) {
  if (p[k] == ch) {
  return k;
}
  k = (k + 1);
}
  return (0 - 1);
}

int32_t dy_find_str(uint8_t* p, int32_t s, int32_t e, const char* lit) {
  uint8_t* lp = (uint8_t*)((uint8_t*)(lit));
  int32_t ln = (int32_t)(strlen(lit));
  int32_t k = s;
  while ((k + ln) <= e) {
  int32_t j = 0;
  while (j < ln && p[(k + j)] == lp[j]) {
  j = (j + 1);
}
  if (j == ln) {
  return k;
}
  k = (k + 1);
}
  return (0 - 1);
}

int32_t dy_starts(uint8_t* p, int32_t s, int32_t e, const char* lit) {
  uint8_t* lp = (uint8_t*)((uint8_t*)(lit));
  int32_t ln = (int32_t)(strlen(lit));
  if ((e - s) < ln) {
  return 0;
}
  int32_t j = 0;
  while (j < ln) {
  if (p[(s + j)] != lp[j]) {
  return 0;
}
  j = (j + 1);
}
  return 1;
}

int32_t dy_eq(uint8_t* p, int32_t s, int32_t e, const char* lit) {
  if ((e - s) != (int32_t)(strlen(lit))) {
  return 0;
}
  return dy_starts(p, s, e, lit);
}

int32_t dy_spans_eq(uint8_t* a, int32_t as0, int32_t ae, uint8_t* b, int32_t bs, int32_t be) {
  if ((ae - as0) != (be - bs)) {
  return 0;
}
  int32_t k = 0;
  while (k < (ae - as0)) {
  if (a[(as0 + k)] != b[(bs + k)]) {
  return 0;
}
  k = (k + 1);
}
  return 1;
}

int32_t dy_has_nonws(uint8_t* p, int32_t s, int32_t e) {
  int32_t k = s;
  while (k < e) {
  if (dy_ws(p[k]) == 0) {
  return 1;
}
  k = (k + 1);
}
  return 0;
}

int32_t dy_eol_len(uint8_t* p, int32_t i, int32_t n) {
  uint8_t c = p[i];
  if (c == 13) {
  if ((i + 1) < n && p[(i + 1)] == 10) {
  return 2;
}
  return 1;
}
  if (c == 10 || c == 11 || c == 12 || c == 28 || c == 29 || c == 30) {
  return 1;
}
  if (c == 194 && (i + 1) < n && p[(i + 1)] == 133) {
  return 2;
}
  if (c == 226 && (i + 2) < n && p[(i + 1)] == 128 && (p[(i + 2)] == 168 || p[(i + 2)] == 169)) {
  return 3;
}
  return 0;
}

int32_t dy_split_lines(uint8_t* p, int32_t n, int32_t* ls, int32_t* le) {
  int32_t count = 0;
  int32_t start = 0;
  int32_t i = 0;
  while (i < n) {
  int32_t t = dy_eol_len(p, i, n);
  if (t > 0) {
  ls[count] = start;
  le[count] = i;
  count = (count + 1);
  i = (i + t);
  start = i;
} else {
  i = (i + 1);
}
}
  if (start < n) {
  ls[count] = start;
  le[count] = n;
  count = (count + 1);
}
  return count;
}

int32_t dy_split_ws(uint8_t* p, int32_t s, int32_t e, int32_t* ws, int32_t* we) {
  int32_t k = s;
  int32_t c = 0;
  while (k < e) {
  while (k < e && dy_ws(p[k]) == 1) {
  k = (k + 1);
}
  if (k >= e) {
  break;
}
  ws[c] = k;
  while (k < e && dy_ws(p[k]) == 0) {
  k = (k + 1);
}
  we[c] = k;
  c = (c + 1);
}
  return c;
}

int32_t dy_numch(uint8_t ch) {
  if (dy_digit(ch) == 1) {
  return 1;
}
  if (ch == 43 || ch == 45 || ch == 46 || ch == 101 || ch == 69) {
  return 1;
}
  return 0;
}

int32_t dy_match(uint8_t* p, int32_t s, int32_t e, const char* pat, int32_t* caps) {
  uint8_t* pp = (uint8_t*)((uint8_t*)(pat));
  int32_t k = s;
  int32_t j = 0;
  int32_t nc = 0;
  while (pp[j] != 0) {
  uint8_t op = pp[j];
  if (op == 94 || op == 126) {
  int32_t st = k;
  while (k < e && dy_ws(p[k]) == 1) {
  k = (k + 1);
}
  if (op == 94 && k == st) {
  return (0 - 1);
}
} else {
  if (op == 64 || op == 35 || op == 36 || op == 38) {
  int32_t st2 = k;
  while (k < e) {
  uint8_t ch = p[k];
  int32_t ok = 0;
  if (op == 64) {
  ok = dy_word(ch);
}
  if (op == 35) {
  ok = dy_digit(ch);
}
  if (op == 36) {
  if (dy_digit(ch) == 1 || ch == 46) {
  ok = 1;
}
}
  if (op == 38) {
  ok = dy_numch(ch);
}
  if (ok == 0) {
  break;
}
  k = (k + 1);
}
  if (k == st2) {
  return (0 - 1);
}
  caps[(nc * 2)] = st2;
  caps[((nc * 2) + 1)] = k;
  nc = (nc + 1);
} else {
  if (k >= e || p[k] != op) {
  return (0 - 1);
}
  k = (k + 1);
}
}
  j = (j + 1);
}
  return k;
}

int32_t* dy_i32s(int32_t n) {
  return (int32_t*)(malloc(((int64_t)((n + 1)) * 4)));
}

int64_t* dy_i64s(int32_t n) {
  return (int64_t*)(malloc(((int64_t)((n + 1)) * 8)));
}

double* dy_f64s(int32_t n) {
  return (double*)(malloc(((int64_t)((n + 1)) * 8)));
}

int32_t dy_name(DyC* c, uint8_t* p, int32_t s, int32_t e) {
  int32_t off = ((c[0]).nm[0]).len;
  dy_span((c[0]).nm, p, s, e);
  dy_putc((c[0]).nm, 0);
  return off;
}

int32_t dy_name_lit(DyC* c, const char* s) {
  int32_t off = ((c[0]).nm[0]).len;
  dy_puts((c[0]).nm, s);
  dy_putc((c[0]).nm, 0);
  return off;
}

const char* dy_nstr(DyC* c, int32_t off) {
  return (const char*)((((c[0]).nm[0]).p + off));
}

int32_t dy_neq(DyC* c, int32_t a, int32_t b) {
  if (strcmp(dy_nstr(c, a), dy_nstr(c, b)) == 0) {
  return 1;
}
  return 0;
}

int32_t dy_neq_lit(DyC* c, int32_t a, const char* s) {
  if (strcmp(dy_nstr(c, a), s) == 0) {
  return 1;
}
  return 0;
}

void dy_pn(DySb* b, DyC* c, int32_t off) {
  dy_puts(b, dy_nstr(c, off));
}

int32_t dy_fpush(DyC* c, double v) {
  if ((c[0]).fnum >= (c[0]).fcap) {
  int32_t ncap = (((c[0]).fcap * 2) + 64);
  (c[0]).fp = (double*)(realloc((uint8_t*)((c[0]).fp), ((int64_t)((ncap + 1)) * 8)));
  (c[0]).fcap = ncap;
}
  (c[0]).fp[(c[0]).fnum] = v;
  (c[0]).fnum = ((c[0]).fnum + 1);
  return ((c[0]).fnum - 1);
}

int32_t dy_bd(DyC* c, int32_t kind, int32_t var, int32_t hz) {
  if ((c[0]).nbd >= (c[0]).bdcap) {
  int32_t ncap = (((c[0]).bdcap * 2) + 64);
  (c[0]).bd_kind = (int32_t*)(realloc((uint8_t*)((c[0]).bd_kind), ((int64_t)((ncap + 1)) * 4)));
  (c[0]).bd_var = (int32_t*)(realloc((uint8_t*)((c[0]).bd_var), ((int64_t)((ncap + 1)) * 4)));
  (c[0]).bd_hz = (int32_t*)(realloc((uint8_t*)((c[0]).bd_hz), ((int64_t)((ncap + 1)) * 4)));
  (c[0]).bdcap = ncap;
}
  (c[0]).bd_kind[(c[0]).nbd] = kind;
  (c[0]).bd_var[(c[0]).nbd] = var;
  (c[0]).bd_hz[(c[0]).nbd] = hz;
  (c[0]).nbd = ((c[0]).nbd + 1);
  return ((c[0]).nbd - 1);
}

int32_t dy_gl(DyC* c, int32_t off) {
  if ((c[0]).ngl >= (c[0]).glcap) {
  int32_t ncap = (((c[0]).glcap * 2) + 64);
  (c[0]).gl = (int32_t*)(realloc((uint8_t*)((c[0]).gl), ((int64_t)((ncap + 1)) * 4)));
  (c[0]).glcap = ncap;
}
  (c[0]).gl[(c[0]).ngl] = off;
  (c[0]).ngl = ((c[0]).ngl + 1);
  return ((c[0]).ngl - 1);
}

int32_t dy_at(DyC* c, int32_t name, double v) {
  if ((c[0]).nat >= (c[0]).atcap) {
  int32_t ncap = (((c[0]).atcap * 2) + 64);
  (c[0]).at_name = (int32_t*)(realloc((uint8_t*)((c[0]).at_name), ((int64_t)((ncap + 1)) * 4)));
  (c[0]).at_val = (double*)(realloc((uint8_t*)((c[0]).at_val), ((int64_t)((ncap + 1)) * 8)));
  (c[0]).atcap = ncap;
}
  (c[0]).at_name[(c[0]).nat] = name;
  (c[0]).at_val[(c[0]).nat] = v;
  (c[0]).nat = ((c[0]).nat + 1);
  return ((c[0]).nat - 1);
}

DySb* dy_err(DyC* c) {
  (c[0]).err = 1;
  ((c[0]).msg[0]).len = 0;
  ((c[0]).msg[0]).p[0] = 0;
  return (c[0]).msg;
}

void dy_err_s(DyC* c, const char* s) {
  DySb* m = (DySb*)(dy_err(c));
  dy_puts(m, s);
}

void dy_repr_str(DySb* b, uint8_t* p, int32_t s, int32_t e) {
  uint8_t q = 39;
  if (dy_find(p, s, e, 39) >= 0 && dy_find(p, s, e, 34) < 0) {
  q = 34;
}
  dy_putc(b, q);
  int32_t k = s;
  while (k < e) {
  uint8_t ch = p[k];
  if (ch == 92 || ch == q) {
  dy_putc(b, 92);
}
  dy_putc(b, ch);
  k = (k + 1);
}
  dy_putc(b, q);
}

int64_t dy_int(DyC* c, uint8_t* p, int32_t s0, int32_t e0) {
  int32_t s = s0;
  int32_t e = e0;
  while (s < e && dy_ws(p[s]) == 1) {
  s = (s + 1);
}
  while (e > s && dy_ws(p[(e - 1)]) == 1) {
  e = (e - 1);
}
  int32_t k = s;
  int32_t neg = 0;
  if (k < e && (p[k] == 43 || p[k] == 45)) {
  if (p[k] == 45) {
  neg = 1;
}
  k = (k + 1);
}
  int64_t v = 0;
  int32_t nd = 0;
  int32_t ok = 1;
  int32_t prev_us = 1;
  while (k < e) {
  uint8_t ch = p[k];
  if (dy_digit(ch) == 1) {
  v = ((v * 10) + (int64_t)((ch - 48)));
  nd = (nd + 1);
  prev_us = 0;
} else {
  if (ch == 95 && prev_us == 0) {
  prev_us = 1;
} else {
  ok = 0;
  break;
}
}
  k = (k + 1);
}
  if (nd == 0 || prev_us == 1) {
  ok = 0;
}
  if (ok == 0) {
  DySb* m = (DySb*)(dy_err(c));
  dy_puts(m, "invalid literal for int() with base 10: ");
  dy_repr_str(m, p, s0, e0);
  return 0;
}
  if (neg == 1) {
  return (0 - v);
}
  return v;
}

int32_t dy_digits_us(uint8_t* p, int32_t k, int32_t e) {
  if (k >= e || dy_digit(p[k]) == 0) {
  return k;
}
  int32_t j = (k + 1);
  while (j < e) {
  if (dy_digit(p[j]) == 1) {
  j = (j + 1);
} else {
  if (p[j] == 95 && (j + 1) < e && dy_digit(p[(j + 1)]) == 1) {
  j = (j + 2);
} else {
  break;
}
}
}
  return j;
}

int32_t dy_lower_eq(uint8_t* p, int32_t s, int32_t e, const char* lit) {
  uint8_t* lp = (uint8_t*)((uint8_t*)(lit));
  int32_t ln = (int32_t)(strlen(lit));
  if ((e - s) != ln) {
  return 0;
}
  int32_t j = 0;
  while (j < ln) {
  uint8_t ch = p[(s + j)];
  if (ch >= 65 && ch <= 90) {
  ch = (ch + 32);
}
  if (ch != lp[j]) {
  return 0;
}
  j = (j + 1);
}
  return 1;
}

double dy_float(DyC* c, uint8_t* p, int32_t s0, int32_t e0) {
  int32_t s = s0;
  int32_t e = e0;
  while (s < e && dy_ws(p[s]) == 1) {
  s = (s + 1);
}
  while (e > s && dy_ws(p[(e - 1)]) == 1) {
  e = (e - 1);
}
  int32_t k = s;
  int32_t neg = 0;
  if (k < e && (p[k] == 43 || p[k] == 45)) {
  if (p[k] == 45) {
  neg = 1;
}
  k = (k + 1);
}
  int32_t ok = 0;
  int32_t special = 0;
  if (dy_lower_eq(p, k, e, "inf") == 1 || dy_lower_eq(p, k, e, "infinity") == 1) {
  special = 1;
  ok = 1;
}
  if (dy_lower_eq(p, k, e, "nan") == 1) {
  special = 2;
  ok = 1;
}
  if (special == 0) {
  int32_t a = dy_digits_us(p, k, e);
  int32_t j = a;
  int32_t have = 0;
  if (a > k) {
  have = 1;
}
  if (j < e && p[j] == 46) {
  int32_t b = dy_digits_us(p, (j + 1), e);
  if (b > (j + 1)) {
  have = 1;
}
  j = b;
}
  if (have == 1 && j < e && (p[j] == 101 || p[j] == 69)) {
  int32_t x = (j + 1);
  if (x < e && (p[x] == 43 || p[x] == 45)) {
  x = (x + 1);
}
  int32_t xe = dy_digits_us(p, x, e);
  if (xe == x) {
  have = 0;
}
  j = xe;
}
  if (have == 1 && j == e) {
  ok = 1;
}
}
  if (ok == 0) {
  DySb* m = (DySb*)(dy_err(c));
  dy_puts(m, "could not convert string to float: ");
  dy_repr_str(m, p, s0, e0);
  return 0.0;
}
  if (special == 1) {
  double big = (1.0e308 * 10.0);
  if (neg == 1) {
  return (0.0 - big);
}
  return big;
}
  if (special == 2) {
  double z = 0.0;
  return (z / z);
}
  uint8_t* buf = (uint8_t*)(malloc((int64_t)(((e - s) + 2))));
  int32_t q = 0;
  int32_t t = s;
  while (t < e) {
  if (p[t] != 95) {
  buf[q] = p[t];
  q = (q + 1);
}
  t = (t + 1);
}
  buf[q] = 0;
  double v = strtod((const char*)(buf), NULL);
  free(buf);
  return v;
}

int64_t dy_bits(double x) {
  double* tmp = (double*)((double*)(malloc(8)));
  tmp[0] = x;
  int64_t* ip = (int64_t*)((int64_t*)(tmp));
  int64_t b = ip[0];
  free((uint8_t*)(tmp));
  return b;
}

int32_t dy_exact(double x, uint8_t* dig, int32_t* dp) {
  int64_t b = dy_bits(x);
  int64_t ex = ((b >> 52) & 2047);
  int64_t frac = (b & 4503599627370495);
  int64_t mant = frac;
  int32_t e2 = (0 - 1074);
  if (ex != 0) {
  mant = (frac + 4503599627370496);
  e2 = ((int32_t)(ex) - 1075);
}
  int64_t* limbs = (int64_t*)((int64_t*)(malloc(1024)));
  int32_t nl = 0;
  int64_t m = mant;
  while (m > 0) {
  limbs[nl] = (m % 1000000000);
  m = (m / 1000000000);
  nl = (nl + 1);
}
  int32_t times = e2;
  int64_t mul = 2;
  if (e2 < 0) {
  times = (0 - e2);
  mul = 5;
}
  int32_t t = 0;
  while (t < times) {
  int64_t carry = 0;
  int32_t i = 0;
  while (i < nl) {
  int64_t v = ((limbs[i] * mul) + carry);
  limbs[i] = (v % 1000000000);
  carry = (v / 1000000000);
  i = (i + 1);
}
  if (carry > 0) {
  limbs[nl] = carry;
  nl = (nl + 1);
}
  t = (t + 1);
}
  int32_t nd = 0;
  int64_t top = limbs[(nl - 1)];
  uint8_t* tmpd = (uint8_t*)(malloc(16));
  int32_t tn = 0;
  while (top > 0) {
  tmpd[tn] = (uint8_t)((48 + (top % 10)));
  top = (top / 10);
  tn = (tn + 1);
}
  while (tn > 0) {
  tn = (tn - 1);
  dig[nd] = tmpd[tn];
  nd = (nd + 1);
}
  int32_t li = (nl - 2);
  while (li >= 0) {
  int64_t v2 = limbs[li];
  int32_t d = 8;
  while (d >= 0) {
  dig[(nd + d)] = (uint8_t)((48 + (v2 % 10)));
  v2 = (v2 / 10);
  d = (d - 1);
}
  nd = (nd + 9);
  li = (li - 1);
}
  free(tmpd);
  free((uint8_t*)(limbs));
  if (e2 < 0) {
  dp[0] = (nd + e2);
} else {
  dp[0] = nd;
}
  return nd;
}

void dy_round(uint8_t* dig, int32_t nd, int32_t pr, uint8_t* out, int32_t* dp) {
  int32_t i = 0;
  while (i < pr) {
  if (i < nd) {
  out[i] = dig[i];
} else {
  out[i] = 48;
}
  i = (i + 1);
}
  if (nd <= pr) {
  return;
}
  uint8_t nx = dig[pr];
  int32_t up = 0;
  if (nx > 53) {
  up = 1;
}
  if (nx == 53) {
  int32_t rest = 0;
  int32_t k = (pr + 1);
  while (k < nd) {
  if (dig[k] != 48) {
  rest = 1;
}
  k = (k + 1);
}
  if (rest == 1) {
  up = 1;
} else {
  if (((out[(pr - 1)] - 48) % 2) == 1) {
  up = 1;
}
}
}
  if (up == 0) {
  return;
}
  int32_t j = (pr - 1);
  while (j >= 0) {
  if (out[j] == 57) {
  out[j] = 48;
  j = (j - 1);
} else {
  out[j] = (out[j] + 1);
  return;
}
}
  out[0] = 49;
  int32_t z = 1;
  while (z < pr) {
  out[z] = 48;
  z = (z + 1);
}
  dp[0] = (dp[0] + 1);
}

int32_t dy_fmt_special(DySb* b, double v, const char* zero) {
  if (v != v) {
  dy_puts(b, "nan");
  return 1;
}
  if (dy_bits(v) < 0) {
  dy_putc(b, 45);
}
  double d = (v - v);
  if (d != d) {
  dy_puts(b, "inf");
  return 1;
}
  if (v == 0.0) {
  dy_puts(b, zero);
  return 1;
}
  return 0;
}

void dy_exp10(DySb* b, int32_t x) {
  if (x < 0) {
  dy_putc(b, 45);
} else {
  dy_putc(b, 43);
}
  int32_t ax = x;
  if (ax < 0) {
  ax = (0 - ax);
}
  if (ax < 10) {
  dy_putc(b, 48);
}
  dy_i64(b, (int64_t)(ax));
}

void dy_g17(DySb* b, double v) {
  if (dy_fmt_special(b, v, "0") == 1) {
  return;
}
  double a = v;
  if (a < 0.0) {
  a = (0.0 - a);
}
  uint8_t* dig = (uint8_t*)(malloc(1200));
  uint8_t* r = (uint8_t*)(malloc(32));
  int32_t* dp = (int32_t*)(dy_i32s(1));
  int32_t nd = dy_exact(a, dig, dp);
  dy_round(dig, nd, 17, r, dp);
  int32_t decpt = dp[0];
  int32_t x = (decpt - 1);
  int32_t last = 17;
  while (last > 1 && r[(last - 1)] == 48) {
  last = (last - 1);
}
  if (x >= (0 - 4) && x < 17) {
  if (decpt <= 0) {
  dy_puts(b, "0.");
  int32_t z = 0;
  while (z < (0 - decpt)) {
  dy_putc(b, 48);
  z = (z + 1);
}
  dy_span(b, r, 0, last);
} else {
  dy_span(b, r, 0, decpt);
  if (last > decpt) {
  dy_putc(b, 46);
  dy_span(b, r, decpt, last);
}
}
} else {
  dy_putc(b, r[0]);
  if (last > 1) {
  dy_putc(b, 46);
  dy_span(b, r, 1, last);
}
  dy_putc(b, 101);
  dy_exp10(b, x);
}
  free(dig);
  free(r);
  free((uint8_t*)(dp));
}

void dy_repr(DySb* b, double v) {
  if (dy_fmt_special(b, v, "0.0") == 1) {
  return;
}
  double a = v;
  if (a < 0.0) {
  a = (0.0 - a);
}
  uint8_t* dig = (uint8_t*)(malloc(1200));
  uint8_t* r = (uint8_t*)(malloc(32));
  int32_t* dp = (int32_t*)(dy_i32s(1));
  int32_t nd = dy_exact(a, dig, dp);
  int32_t exact_dp = dp[0];
  DySb* chk = (DySb*)(dy_sb_new(64));
  int32_t pr = 1;
  while (pr <= 17) {
  dp[0] = exact_dp;
  dy_round(dig, nd, pr, r, dp);
  (chk[0]).len = 0;
  dy_puts(chk, "0.");
  dy_span(chk, r, 0, pr);
  dy_putc(chk, 101);
  dy_i64(chk, (int64_t)(dp[0]));
  if (strtod((const char*)((chk[0]).p), NULL) == a) {
  break;
}
  pr = (pr + 1);
}
  int32_t last = pr;
  while (last > 1 && r[(last - 1)] == 48) {
  last = (last - 1);
}
  int32_t decpt = dp[0];
  int32_t x = (decpt - 1);
  if (x >= (0 - 4) && x < 16) {
  if (decpt <= 0) {
  dy_puts(b, "0.");
  int32_t z = 0;
  while (z < (0 - decpt)) {
  dy_putc(b, 48);
  z = (z + 1);
}
  dy_span(b, r, 0, last);
} else {
  if (decpt >= last) {
  dy_span(b, r, 0, last);
  int32_t z2 = last;
  while (z2 < decpt) {
  dy_putc(b, 48);
  z2 = (z2 + 1);
}
  dy_puts(b, ".0");
} else {
  dy_span(b, r, 0, decpt);
  dy_putc(b, 46);
  dy_span(b, r, decpt, last);
}
}
} else {
  dy_putc(b, r[0]);
  if (last > 1) {
  dy_putc(b, 46);
  dy_span(b, r, 1, last);
}
  dy_putc(b, 101);
  dy_exp10(b, x);
}
  free(dig);
  free(r);
  free((uint8_t*)(dp));
  free((chk[0]).p);
  free((uint8_t*)(chk));
}

void dy_flow_f64(DySb* b, double v) {
  DySb* t = (DySb*)(dy_sb_new(40));
  dy_g17(t, v);
  int32_t s = 0;
  if ((t[0]).p[0] == 46) {
  dy_putc(b, 48);
}
  if ((t[0]).len >= 2 && (t[0]).p[0] == 45 && (t[0]).p[1] == 46) {
  dy_puts(b, "-0");
  s = 1;
}
  dy_span(b, (t[0]).p, s, (t[0]).len);
  if (dy_find((t[0]).p, 0, (t[0]).len, 101) < 0 && dy_find((t[0]).p, 0, (t[0]).len, 69) < 0 && dy_find((t[0]).p, 0, (t[0]).len, 46) < 0) {
  dy_puts(b, ".0");
}
  free((t[0]).p);
  free((uint8_t*)(t));
}

Dp* dy_prog_new(int32_t cap0) {
  int32_t cap = (cap0 + 8);
  Dp* g = (Dp*)((Dp*)(malloc(2048)));
  (g[0]).cap = cap;
  (g[0]).nsy = 0;
  (g[0]).sy_name = dy_i32s(cap);
  (g[0]).sy_mode = dy_i32s(cap);
  (g[0]).sy_dt = dy_f64s(cap);
  (g[0]).sy_n = dy_i64s(cap);
  (g[0]).sy_m = dy_i64s(cap);
  (g[0]).sy_p = dy_i64s(cap);
  (g[0]).sy_a0 = dy_i32s(cap);
  (g[0]).sy_an = dy_i32s(cap);
  (g[0]).sy_b0 = dy_i32s(cap);
  (g[0]).sy_bn = dy_i32s(cap);
  (g[0]).sy_c0 = dy_i32s(cap);
  (g[0]).sy_cn = dy_i32s(cap);
  (g[0]).nhz = 0;
  (g[0]).hz_name = dy_i32s(cap);
  (g[0]).hz_kind = dy_i32s(cap);
  (g[0]).hz_steps = dy_i64s(cap);
  (g[0]).hz_gamma = dy_f64s(cap);
  (g[0]).nwf = 0;
  (g[0]).wf_name = dy_i32s(cap);
  (g[0]).wf_w = dy_i64s(cap);
  (g[0]).wf_h = dy_i64s(cap);
  (g[0]).wf_tiles = dy_i64s(cap);
  (g[0]).wf_seed = dy_i64s(cap);
  (g[0]).wf_pc = dy_i64s(cap);
  (g[0]).wf_pt = dy_i64s(cap);
  (g[0]).wf_steps = dy_i64s(cap);
  (g[0]).nse = 0;
  (g[0]).se_sys = dy_i32s(cap);
  (g[0]).se_b0 = dy_i32s(cap);
  (g[0]).se_bn = dy_i32s(cap);
  (g[0]).nga = 0;
  (g[0]).ga_sys = dy_i32s(cap);
  (g[0]).ga_hz = dy_i32s(cap);
  (g[0]).ga_k1 = dy_i32s(cap);
  (g[0]).ga_k2 = dy_i32s(cap);
  (g[0]).ga_pop = dy_i64s(cap);
  (g[0]).ga_gen = dy_i64s(cap);
  (g[0]).ga_mut = dy_f64s(cap);
  (g[0]).ncl = 0;
  (g[0]).cl_sys = dy_i32s(cap);
  (g[0]).cl_k1 = dy_i32s(cap);
  (g[0]).cl_k2 = dy_i32s(cap);
  (g[0]).cl_b0 = dy_i32s(cap);
  (g[0]).cl_bn = dy_i32s(cap);
  (g[0]).nanz = 0;
  (g[0]).an_sys = dy_i32s(cap);
  (g[0]).an_k1 = dy_i32s(cap);
  (g[0]).an_k2 = dy_i32s(cap);
  (g[0]).an_hz = dy_i32s(cap);
  (g[0]).an_rep = dy_i32s(cap);
  (g[0]).ncp = 0;
  (g[0]).cp_sys = dy_i32s(cap);
  (g[0]).cp_field = dy_i32s(cap);
  (g[0]).cp_rep = dy_i32s(cap);
  (g[0]).cp_k1 = dy_i32s(cap);
  (g[0]).cp_k2 = dy_i32s(cap);
  (g[0]).cp_guid = dy_i32s(cap);
  (g[0]).cp_b0 = dy_i32s(cap);
  (g[0]).cp_bn = dy_i32s(cap);
  (g[0]).ngd = 0;
  (g[0]).gd_sys = dy_i32s(cap);
  (g[0]).gd_k1 = dy_i32s(cap);
  (g[0]).gd_k2 = dy_i32s(cap);
  (g[0]).gd_field = dy_i32s(cap);
  (g[0]).gd_guid = dy_i32s(cap);
  (g[0]).gd_hz = dy_i32s(cap);
  (g[0]).gd_b0 = dy_i32s(cap);
  (g[0]).gd_bn = dy_i32s(cap);
  (g[0]).nrp = 0;
  (g[0]).rp_flow = dy_i32s(cap);
  (g[0]).rp_mode = dy_i32s(cap);
  (g[0]).rp_dt = dy_f64s(cap);
  (g[0]).rp_n = dy_i64s(cap);
  (g[0]).rp_m = dy_i64s(cap);
  (g[0]).rp_p = dy_i64s(cap);
  (g[0]).rp_a0 = dy_i32s(cap);
  (g[0]).rp_an = dy_i32s(cap);
  (g[0]).rp_b0 = dy_i32s(cap);
  (g[0]).rp_bn = dy_i32s(cap);
  (g[0]).rp_c0 = dy_i32s(cap);
  (g[0]).rp_cn = dy_i32s(cap);
  (g[0]).rp_at0 = dy_i32s(cap);
  (g[0]).rp_atn = dy_i32s(cap);
  (g[0]).rp_nin = dy_i32s(cap);
  (g[0]).npt = 0;
  (g[0]).pt_flow = dy_i32s(cap);
  (g[0]).pt_ax0 = dy_i32s(cap);
  (g[0]).pt_ax1 = dy_i32s(cap);
  (g[0]).pt_trail = dy_i64s(cap);
  (g[0]).pt_w = dy_i64s(cap);
  (g[0]).pt_h = dy_i64s(cap);
  (g[0]).pt_set0 = dy_i32s(cap);
  (g[0]).pt_set1 = dy_i32s(cap);
  (g[0]).pt_lo0 = dy_f64s(cap);
  (g[0]).pt_hi0 = dy_f64s(cap);
  (g[0]).pt_lo1 = dy_f64s(cap);
  (g[0]).pt_hi1 = dy_f64s(cap);
  (g[0]).pt_k0 = dy_i32s(cap);
  (g[0]).pt_k1 = dy_i32s(cap);
  (g[0]).nlq = 0;
  (g[0]).lq_sys = dy_i32s(cap);
  (g[0]).lq_q0 = dy_i32s(cap);
  (g[0]).lq_qn = dy_i32s(cap);
  (g[0]).lq_r = dy_f64s(cap);
  (g[0]).lq_g0 = dy_i32s(cap);
  (g[0]).lq_gn = dy_i32s(cap);
  (g[0]).lq_it = dy_i64s(cap);
  return g;
}

int32_t dy_find_sys(DyC* c, Dp* g, int32_t name) {
  int32_t i = 0;
  while (i < (g[0]).nsy) {
  if (dy_neq(c, (g[0]).sy_name[i], name) == 1) {
  return i;
}
  i = (i + 1);
}
  return (0 - 1);
}

int32_t dy_find_hz(DyC* c, Dp* g, int32_t name) {
  int32_t i = 0;
  while (i < (g[0]).nhz) {
  if (dy_neq(c, (g[0]).hz_name[i], name) == 1) {
  return i;
}
  i = (i + 1);
}
  return (0 - 1);
}

int32_t dy_find_wf(DyC* c, Dp* g, int32_t name) {
  int32_t i = 0;
  while (i < (g[0]).nwf) {
  if (dy_neq(c, (g[0]).wf_name[i], name) == 1) {
  return i;
}
  i = (i + 1);
}
  return (0 - 1);
}

int32_t dy_sys_slot(DyC* c, Dp* g, int32_t name) {
  int32_t i = dy_find_sys(c, g, name);
  if (i >= 0) {
  return i;
}
  int32_t k = (g[0]).nsy;
  (g[0]).sy_name[k] = name;
  (g[0]).nsy = (k + 1);
  return k;
}

int32_t dy_hz_slot(DyC* c, Dp* g, int32_t name) {
  int32_t i = dy_find_hz(c, g, name);
  if (i >= 0) {
  return i;
}
  int32_t k = (g[0]).nhz;
  (g[0]).hz_name[k] = name;
  (g[0]).nhz = (k + 1);
  return k;
}

int32_t dy_wf_slot(DyC* c, Dp* g, int32_t name) {
  int32_t i = dy_find_wf(c, g, name);
  if (i >= 0) {
  return i;
}
  int32_t k = (g[0]).nwf;
  (g[0]).wf_name[k] = name;
  (g[0]).nwf = (k + 1);
  return k;
}

void dy_copy_sys(Dp* d, int32_t k, Dp* s, int32_t i) {
  (d[0]).sy_mode[k] = (s[0]).sy_mode[i];
  (d[0]).sy_dt[k] = (s[0]).sy_dt[i];
  (d[0]).sy_n[k] = (s[0]).sy_n[i];
  (d[0]).sy_m[k] = (s[0]).sy_m[i];
  (d[0]).sy_p[k] = (s[0]).sy_p[i];
  (d[0]).sy_a0[k] = (s[0]).sy_a0[i];
  (d[0]).sy_an[k] = (s[0]).sy_an[i];
  (d[0]).sy_b0[k] = (s[0]).sy_b0[i];
  (d[0]).sy_bn[k] = (s[0]).sy_bn[i];
  (d[0]).sy_c0[k] = (s[0]).sy_c0[i];
  (d[0]).sy_cn[k] = (s[0]).sy_cn[i];
}

void dy_merge(DyC* c, Dp* d, Dp* s) {
  int32_t i = 0;
  while (i < (s[0]).nsy) {
  int32_t k = dy_sys_slot(c, d, (s[0]).sy_name[i]);
  dy_copy_sys(d, k, s, i);
  i = (i + 1);
}
  i = 0;
  while (i < (s[0]).nhz) {
  int32_t k = dy_hz_slot(c, d, (s[0]).hz_name[i]);
  (d[0]).hz_kind[k] = (s[0]).hz_kind[i];
  (d[0]).hz_steps[k] = (s[0]).hz_steps[i];
  (d[0]).hz_gamma[k] = (s[0]).hz_gamma[i];
  i = (i + 1);
}
  i = 0;
  while (i < (s[0]).nse) {
  int32_t k = (d[0]).nse;
  (d[0]).se_sys[k] = (s[0]).se_sys[i];
  (d[0]).se_b0[k] = (s[0]).se_b0[i];
  (d[0]).se_bn[k] = (s[0]).se_bn[i];
  (d[0]).nse = (k + 1);
  i = (i + 1);
}
  i = 0;
  while (i < (s[0]).nga) {
  int32_t k = (d[0]).nga;
  (d[0]).ga_sys[k] = (s[0]).ga_sys[i];
  (d[0]).ga_hz[k] = (s[0]).ga_hz[i];
  (d[0]).ga_k1[k] = (s[0]).ga_k1[i];
  (d[0]).ga_k2[k] = (s[0]).ga_k2[i];
  (d[0]).ga_pop[k] = (s[0]).ga_pop[i];
  (d[0]).ga_gen[k] = (s[0]).ga_gen[i];
  (d[0]).ga_mut[k] = (s[0]).ga_mut[i];
  (d[0]).nga = (k + 1);
  i = (i + 1);
}
  i = 0;
  while (i < (s[0]).ncl) {
  int32_t k = (d[0]).ncl;
  (d[0]).cl_sys[k] = (s[0]).cl_sys[i];
  (d[0]).cl_k1[k] = (s[0]).cl_k1[i];
  (d[0]).cl_k2[k] = (s[0]).cl_k2[i];
  (d[0]).cl_b0[k] = (s[0]).cl_b0[i];
  (d[0]).cl_bn[k] = (s[0]).cl_bn[i];
  (d[0]).ncl = (k + 1);
  i = (i + 1);
}
  i = 0;
  while (i < (s[0]).nanz) {
  int32_t k = (d[0]).nanz;
  (d[0]).an_sys[k] = (s[0]).an_sys[i];
  (d[0]).an_k1[k] = (s[0]).an_k1[i];
  (d[0]).an_k2[k] = (s[0]).an_k2[i];
  (d[0]).an_hz[k] = (s[0]).an_hz[i];
  (d[0]).an_rep[k] = (s[0]).an_rep[i];
  (d[0]).nanz = (k + 1);
  i = (i + 1);
}
  i = 0;
  while (i < (s[0]).nwf) {
  int32_t k = dy_wf_slot(c, d, (s[0]).wf_name[i]);
  (d[0]).wf_w[k] = (s[0]).wf_w[i];
  (d[0]).wf_h[k] = (s[0]).wf_h[i];
  (d[0]).wf_tiles[k] = (s[0]).wf_tiles[i];
  (d[0]).wf_seed[k] = (s[0]).wf_seed[i];
  (d[0]).wf_pc[k] = (s[0]).wf_pc[i];
  (d[0]).wf_pt[k] = (s[0]).wf_pt[i];
  (d[0]).wf_steps[k] = (s[0]).wf_steps[i];
  i = (i + 1);
}
  i = 0;
  while (i < (s[0]).ncp) {
  int32_t k = (d[0]).ncp;
  (d[0]).cp_sys[k] = (s[0]).cp_sys[i];
  (d[0]).cp_field[k] = (s[0]).cp_field[i];
  (d[0]).cp_rep[k] = (s[0]).cp_rep[i];
  (d[0]).cp_k1[k] = (s[0]).cp_k1[i];
  (d[0]).cp_k2[k] = (s[0]).cp_k2[i];
  (d[0]).cp_guid[k] = (s[0]).cp_guid[i];
  (d[0]).cp_b0[k] = (s[0]).cp_b0[i];
  (d[0]).cp_bn[k] = (s[0]).cp_bn[i];
  (d[0]).ncp = (k + 1);
  i = (i + 1);
}
  i = 0;
  while (i < (s[0]).ngd) {
  int32_t k = (d[0]).ngd;
  (d[0]).gd_sys[k] = (s[0]).gd_sys[i];
  (d[0]).gd_k1[k] = (s[0]).gd_k1[i];
  (d[0]).gd_k2[k] = (s[0]).gd_k2[i];
  (d[0]).gd_field[k] = (s[0]).gd_field[i];
  (d[0]).gd_guid[k] = (s[0]).gd_guid[i];
  (d[0]).gd_hz[k] = (s[0]).gd_hz[i];
  (d[0]).gd_b0[k] = (s[0]).gd_b0[i];
  (d[0]).gd_bn[k] = (s[0]).gd_bn[i];
  (d[0]).ngd = (k + 1);
  i = (i + 1);
}
  i = 0;
  while (i < (s[0]).nrp) {
  (d[0]).rp_flow[(d[0]).nrp] = (s[0]).rp_flow[i];
  (d[0]).nrp = ((d[0]).nrp + 1);
  i = (i + 1);
}
  i = 0;
  while (i < (s[0]).npt) {
  int32_t k = (d[0]).npt;
  (d[0]).pt_flow[k] = (s[0]).pt_flow[i];
  (d[0]).pt_ax0[k] = (s[0]).pt_ax0[i];
  (d[0]).pt_ax1[k] = (s[0]).pt_ax1[i];
  (d[0]).pt_trail[k] = (s[0]).pt_trail[i];
  (d[0]).pt_w[k] = (s[0]).pt_w[i];
  (d[0]).pt_h[k] = (s[0]).pt_h[i];
  (d[0]).pt_set0[k] = (s[0]).pt_set0[i];
  (d[0]).pt_set1[k] = (s[0]).pt_set1[i];
  (d[0]).pt_lo0[k] = (s[0]).pt_lo0[i];
  (d[0]).pt_hi0[k] = (s[0]).pt_hi0[i];
  (d[0]).pt_lo1[k] = (s[0]).pt_lo1[i];
  (d[0]).pt_hi1[k] = (s[0]).pt_hi1[i];
  (d[0]).pt_k0[k] = (s[0]).pt_k0[i];
  (d[0]).pt_k1[k] = (s[0]).pt_k1[i];
  (d[0]).npt = (k + 1);
  i = (i + 1);
}
  i = 0;
  while (i < (s[0]).nlq) {
  int32_t k = (d[0]).nlq;
  (d[0]).lq_sys[k] = (s[0]).lq_sys[i];
  (d[0]).lq_q0[k] = (s[0]).lq_q0[i];
  (d[0]).lq_qn[k] = (s[0]).lq_qn[i];
  (d[0]).lq_r[k] = (s[0]).lq_r[i];
  (d[0]).lq_g0[k] = (s[0]).lq_g0[i];
  (d[0]).lq_gn[k] = (s[0]).lq_gn[i];
  (d[0]).lq_it[k] = (s[0]).lq_it[i];
  (d[0]).nlq = (k + 1);
  i = (i + 1);
}
}

int32_t dy_block(uint8_t* p, int32_t* ls, int32_t* le, int32_t nl, int32_t start, int32_t* bs, int32_t* be, int32_t* nb) {
  int32_t depth = 0;
  int32_t i = start;
  nb[0] = 0;
  int32_t* se = (int32_t*)(dy_i32s(2));
  while (i < nl) {
  int32_t a = ls[i];
  int32_t b = le[i];
  int32_t opens = dy_count(p, a, b, 123);
  depth = ((depth + opens) - dy_count(p, a, b, 125));
  if (i > start || opens > 0) {
  if (depth > 0 || i == start && opens > 0) {
  int32_t ia = a;
  if (i == start) {
  ia = (dy_find(p, a, b, 123) + 1);
}
  if (depth > 0) {
  se[0] = ia;
  se[1] = b;
  while (se[1] > se[0] && p[(se[1] - 1)] == 125) {
  se[1] = (se[1] - 1);
}
  dy_strip(p, se);
  bs[nb[0]] = se[0];
  be[nb[0]] = se[1];
  nb[0] = (nb[0] + 1);
} else {
  if (dy_find(p, a, b, 125) >= 0) {
  se[0] = ia;
  int32_t cl = dy_find(p, ia, b, 125);
  if (cl >= 0) {
  se[1] = cl;
} else {
  se[1] = b;
}
  dy_strip(p, se);
  bs[nb[0]] = se[0];
  be[nb[0]] = se[1];
  nb[0] = (nb[0] + 1);
}
}
}
}
  if (depth <= 0 && i > start) {
  free((uint8_t*)(se));
  return (i + 1);
}
  i = (i + 1);
}
  free((uint8_t*)(se));
  return i;
}

int32_t dy_block_keep(uint8_t* p, int32_t* ls, int32_t* le, int32_t nl, int32_t start, int32_t* bs, int32_t* be, int32_t* nb) {
  int32_t depth = 0;
  int32_t i = start;
  nb[0] = 0;
  int32_t* se = (int32_t*)(dy_i32s(2));
  while (i < nl) {
  int32_t a = ls[i];
  int32_t b = le[i];
  if (i == start) {
  int32_t o = dy_find(p, a, b, 123);
  int32_t aa = b;
  if (o >= 0) {
  aa = (o + 1);
}
  depth = ((1 + dy_count(p, aa, b, 123)) - dy_count(p, aa, b, 125));
  if (depth > 0) {
  if (dy_has_nonws(p, aa, b) == 1) {
  se[0] = aa;
  se[1] = b;
  dy_rstrip(p, se);
  bs[nb[0]] = se[0];
  be[nb[0]] = se[1];
  nb[0] = (nb[0] + 1);
}
} else {
  free((uint8_t*)(se));
  return (i + 1);
}
} else {
  depth = ((depth + dy_count(p, a, b, 123)) - dy_count(p, a, b, 125));
  if (depth > 0) {
  bs[nb[0]] = a;
  be[nb[0]] = b;
  nb[0] = (nb[0] + 1);
} else {
  int32_t last = (0 - 1);
  int32_t k = a;
  while (k < b) {
  if (p[k] == 125) {
  last = k;
}
  k = (k + 1);
}
  int32_t before = a;
  if (last >= 0) {
  before = last;
}
  if (dy_has_nonws(p, a, before) == 1) {
  se[0] = a;
  se[1] = before;
  dy_rstrip(p, se);
  bs[nb[0]] = se[0];
  be[nb[0]] = se[1];
  nb[0] = (nb[0] + 1);
}
  free((uint8_t*)(se));
  return (i + 1);
}
}
  i = (i + 1);
}
  free((uint8_t*)(se));
  return i;
}

int32_t dy_floats(DyC* c, uint8_t* p, int32_t s, int32_t e, int32_t* f0) {
  int32_t* ws = (int32_t*)(dy_i32s(((e - s) + 1)));
  int32_t* we = (int32_t*)(dy_i32s(((e - s) + 1)));
  int32_t n = dy_split_ws(p, s, e, ws, we);
  f0[0] = (c[0]).fnum;
  int32_t k = 0;
  while (k < n) {
  double v = dy_float(c, p, ws[k], we[k]);
  if ((c[0]).err != 0) {
  free((uint8_t*)(ws));
  free((uint8_t*)(we));
  return 0;
}
  dy_fpush(c, v);
  k = (k + 1);
}
  free((uint8_t*)(ws));
  free((uint8_t*)(we));
  return n;
}

int32_t dy_all_word(uint8_t* p, int32_t s, int32_t e) {
  if (e <= s) {
  return 0;
}
  int32_t k = s;
  while (k < e) {
  if (dy_word(p[k]) == 0) {
  return 0;
}
  k = (k + 1);
}
  return 1;
}

void dy_parse_nmp(DyC* c, uint8_t* p, int32_t s, int32_t e, int64_t* nv, int64_t* mv, int64_t* pv, int32_t idx) {
  int32_t* ws = (int32_t*)(dy_i32s(((e - s) + 1)));
  int32_t* we = (int32_t*)(dy_i32s(((e - s) + 1)));
  int32_t n = dy_split_ws(p, s, e, ws, we);
  nv[idx] = dy_int(c, p, ws[1], we[1]);
  if ((c[0]).err == 0) {
  int32_t k = 0;
  while (k < n) {
  if (dy_eq(p, ws[k], we[k], "m") == 1) {
  if ((k + 1) >= n) {
  dy_err_s(c, "list index out of range");
} else {
  mv[idx] = dy_int(c, p, ws[(k + 1)], we[(k + 1)]);
}
  break;
}
  k = (k + 1);
}
}
  if ((c[0]).err == 0) {
  int32_t k2 = 0;
  while (k2 < n) {
  if (dy_eq(p, ws[k2], we[k2], "p") == 1) {
  if ((k2 + 1) >= n) {
  dy_err_s(c, "list index out of range");
} else {
  pv[idx] = dy_int(c, p, ws[(k2 + 1)], we[(k2 + 1)]);
}
  break;
}
  k2 = (k2 + 1);
}
}
  free((uint8_t*)(ws));
  free((uint8_t*)(we));
}

int64_t dy_int_part(DyC* c, uint8_t* p, int32_t s, int32_t e, int32_t k) {
  int32_t* ws = (int32_t*)(dy_i32s(((e - s) + 1)));
  int32_t* we = (int32_t*)(dy_i32s(((e - s) + 1)));
  int32_t n = dy_split_ws(p, s, e, ws, we);
  int64_t v = 0;
  if (k >= n) {
  dy_err_s(c, "list index out of range");
} else {
  v = dy_int(c, p, ws[k], we[k]);
}
  free((uint8_t*)(ws));
  free((uint8_t*)(we));
  return v;
}

double dy_float_part(DyC* c, uint8_t* p, int32_t s, int32_t e, int32_t k) {
  int32_t* ws = (int32_t*)(dy_i32s(((e - s) + 1)));
  int32_t* we = (int32_t*)(dy_i32s(((e - s) + 1)));
  int32_t n = dy_split_ws(p, s, e, ws, we);
  double v = 0.0;
  if (k >= n) {
  dy_err_s(c, "list index out of range");
} else {
  v = dy_float(c, p, ws[k], we[k]);
}
  free((uint8_t*)(ws));
  free((uint8_t*)(we));
  return v;
}

int32_t dy_name_part(DyC* c, uint8_t* p, int32_t s, int32_t e, int32_t k) {
  int32_t* ws = (int32_t*)(dy_i32s(((e - s) + 1)));
  int32_t* we = (int32_t*)(dy_i32s(((e - s) + 1)));
  int32_t n = dy_split_ws(p, s, e, ws, we);
  int32_t v = (0 - 1);
  if (k >= n) {
  dy_err_s(c, "list index out of range");
} else {
  v = dy_name(c, p, ws[k], we[k]);
}
  free((uint8_t*)(ws));
  free((uint8_t*)(we));
  return v;
}

void dy_parse_at(DyC* c, uint8_t* p, int32_t s0, int32_t e0, Dp* g, int32_t r) {
  int32_t* se = (int32_t*)(dy_i32s(2));
  se[0] = s0;
  se[1] = e0;
  dy_strip(p, se);
  (g[0]).rp_at0[r] = (c[0]).nat;
  (g[0]).rp_atn[r] = 0;
  if (se[0] >= se[1]) {
  free((uint8_t*)(se));
  return;
}
  int32_t k = se[0];
  int32_t e = se[1];
  while (k <= e) {
  int32_t j = k;
  while (j < e && p[j] != 44) {
  j = (j + 1);
}
  int32_t* pa = (int32_t*)(dy_i32s(2));
  pa[0] = k;
  pa[1] = j;
  dy_strip(p, pa);
  if (pa[1] > pa[0]) {
  int32_t col = dy_find(p, pa[0], pa[1], 58);
  if (col < 0) {
  DySb* m = (DySb*)(dy_err(c));
  dy_puts(m, "invalid `at` binding '");
  dy_span(m, p, pa[0], pa[1]);
  dy_puts(m, "' in represent linear; expected name: value");
  free((uint8_t*)(pa));
  free((uint8_t*)(se));
  return;
}
  int32_t* nm = (int32_t*)(dy_i32s(2));
  nm[0] = pa[0];
  nm[1] = col;
  dy_strip(p, nm);
  int32_t* vl = (int32_t*)(dy_i32s(2));
  vl[0] = (col + 1);
  vl[1] = pa[1];
  dy_strip(p, vl);
  if (dy_all_word(p, nm[0], nm[1]) == 0) {
  DySb* m2 = (DySb*)(dy_err(c));
  dy_puts(m2, "invalid state name in `at`: ");
  dy_span(m2, p, nm[0], nm[1]);
  return;
}
  double v = dy_float(c, p, vl[0], vl[1]);
  if ((c[0]).err != 0) {
  DySb* m3 = (DySb*)(dy_err(c));
  dy_puts(m3, "invalid numeric value in `at` for '");
  dy_span(m3, p, nm[0], nm[1]);
  dy_puts(m3, "': ");
  dy_span(m3, p, vl[0], vl[1]);
  return;
}
  int32_t off = dy_name(c, p, nm[0], nm[1]);
  int32_t found = (0 - 1);
  int32_t q = (g[0]).rp_at0[r];
  while (q < ((g[0]).rp_at0[r] + (g[0]).rp_atn[r])) {
  if (dy_neq(c, (c[0]).at_name[q], off) == 1) {
  found = q;
}
  q = (q + 1);
}
  if (found >= 0) {
  (c[0]).at_val[found] = v;
} else {
  dy_at(c, off, v);
  (g[0]).rp_atn[r] = ((g[0]).rp_atn[r] + 1);
}
}
  free((uint8_t*)(pa));
  k = (j + 1);
}
  free((uint8_t*)(se));
}

int32_t dy_name_list(DyC* c, uint8_t* p, int32_t s0, int32_t e0) {
  int32_t* se = (int32_t*)(dy_i32s(2));
  se[0] = s0;
  se[1] = e0;
  dy_strip(p, se);
  if (se[0] >= se[1]) {
  return 0;
}
  int32_t count = 0;
  int32_t k = se[0];
  int32_t e = se[1];
  while (k <= e) {
  int32_t j = k;
  while (j < e && p[j] != 44) {
  j = (j + 1);
}
  int32_t* pa = (int32_t*)(dy_i32s(2));
  pa[0] = k;
  pa[1] = j;
  dy_strip(p, pa);
  if (pa[1] > pa[0]) {
  if (dy_all_word(p, pa[0], pa[1]) == 0) {
  DySb* m = (DySb*)(dy_err(c));
  dy_puts(m, "invalid name in represent linear list: ");
  dy_span(m, p, pa[0], pa[1]);
  return 0;
}
  count = (count + 1);
}
  k = (j + 1);
}
  return count;
}

int32_t dy_paren_form(uint8_t* p, int32_t s, int32_t e, const char* word, int32_t* se) {
  if (dy_starts(p, s, e, word) == 0) {
  return 0;
}
  int32_t k = (s + (int32_t)(strlen(word)));
  while (k < e && dy_ws(p[k]) == 1) {
  k = (k + 1);
}
  if (k >= e || p[k] != 40) {
  return 0;
}
  int32_t t = e;
  while (t > (k + 1) && dy_ws(p[(t - 1)]) == 1) {
  t = (t - 1);
}
  if (t <= (k + 1) || p[(t - 1)] != 41) {
  return 0;
}
  se[0] = (k + 1);
  se[1] = (t - 1);
  return 1;
}

void dy_rep_linear_body(DyC* c, uint8_t* p, Dp* g, int32_t r, int32_t* bs, int32_t* be, int32_t nb) {
  int32_t* se = (int32_t*)(dy_i32s(2));
  int32_t* inner = (int32_t*)(dy_i32s(2));
  int32_t* f0 = (int32_t*)(dy_i32s(1));
  int32_t i = 0;
  while (i < nb) {
  se[0] = bs[i];
  se[1] = be[i];
  dy_strip_comments(p, se);
  int32_t s = se[0];
  int32_t e = se[1];
  if (s < e) {
  int32_t done = 0;
  if (dy_paren_form(p, s, e, "at", inner) == 1) {
  dy_parse_at(c, p, inner[0], inner[1], g, r);
  done = 1;
}
  if (done == 0) {
  int32_t kind = 0;
  if (dy_paren_form(p, s, e, "inputs", inner) == 1) {
  kind = 1;
} else {
  if (dy_paren_form(p, s, e, "outputs", inner) == 1) {
  kind = 2;
}
}
  if (kind > 0) {
  int32_t cnt = dy_name_list(c, p, inner[0], inner[1]);
  if (kind == 1) {
  (g[0]).rp_nin[r] = cnt;
}
  done = 1;
}
}
  if (done == 0) {
  if (dy_eq(p, s, e, "continuous") == 1) {
  (g[0]).rp_mode[r] = 1;
} else {
  if (dy_eq(p, s, e, "discrete") == 1) {
  (g[0]).rp_mode[r] = 0;
} else {
  if (dy_starts(p, s, e, "dt ") == 1) {
  (g[0]).rp_dt[r] = dy_float_part(c, p, s, e, 1);
} else {
  if (dy_starts(p, s, e, "n ") == 1) {
  dy_parse_nmp(c, p, s, e, (g[0]).rp_n, (g[0]).rp_m, (g[0]).rp_p, r);
} else {
  if (dy_starts(p, s, e, "A ") == 1) {
  (g[0]).rp_an[r] = dy_floats(c, p, (s + 2), e, f0);
  (g[0]).rp_a0[r] = f0[0];
} else {
  if (dy_starts(p, s, e, "B ") == 1) {
  (g[0]).rp_bn[r] = dy_floats(c, p, (s + 2), e, f0);
  (g[0]).rp_b0[r] = f0[0];
} else {
  if (dy_starts(p, s, e, "C ") == 1) {
  (g[0]).rp_cn[r] = dy_floats(c, p, (s + 2), e, f0);
  (g[0]).rp_c0[r] = f0[0];
} else {
  DySb* m = (DySb*)(dy_err(c));
  dy_puts(m, "unknown item in represent linear for '");
  dy_pn(m, c, (g[0]).rp_flow[r]);
  dy_puts(m, "': ");
  dy_span(m, p, s, e);
}
}
}
}
}
}
}
}
  if ((c[0]).err != 0) {
  return;
}
}
  i = (i + 1);
}
}

void dy_portrait_body(DyC* c, uint8_t* p, Dp* g, int32_t t, int32_t* bs, int32_t* be, int32_t nb) {
  int32_t* se = (int32_t*)(dy_i32s(2));
  int32_t* caps = (int32_t*)(dy_i32s(16));
  int32_t fl = (g[0]).pt_flow[t];
  int32_t i = 0;
  while (i < nb) {
  se[0] = bs[i];
  se[1] = be[i];
  dy_strip_comments(p, se);
  int32_t s = se[0];
  int32_t e = se[1];
  if (s < e) {
  int32_t done = 0;
  int32_t m1 = dy_match(p, s, e, "trail^#~", caps);
  if (m1 == e) {
  (g[0]).pt_trail[t] = dy_int(c, p, caps[0], caps[1]);
  if ((c[0]).err != 0) {
  return;
}
  if ((g[0]).pt_trail[t] <= 0) {
  DySb* m = (DySb*)(dy_err(c));
  dy_puts(m, "represent phase_portrait for '");
  dy_pn(m, c, fl);
  dy_puts(m, "': trail must be positive");
  return;
}
  done = 1;
}
  if (done == 0) {
  int32_t m2 = dy_match(p, s, e, "window^#~,~#~", caps);
  if (m2 == e) {
  (g[0]).pt_w[t] = dy_int(c, p, caps[0], caps[1]);
  (g[0]).pt_h[t] = dy_int(c, p, caps[2], caps[3]);
  done = 1;
}
}
  if (done == 0) {
  int32_t m3 = dy_match(p, s, e, "map^@^in~[~&~,~&~]~->~@~", caps);
  int32_t kind = 0;
  if (m3 == e) {
  if (dy_eq(p, caps[6], caps[7], "col") == 1) {
  kind = 1;
}
  if (dy_eq(p, caps[6], caps[7], "row") == 1) {
  kind = 2;
}
}
  if (kind > 0) {
  int32_t ax = dy_name(c, p, caps[0], caps[1]);
  int32_t is0 = dy_neq(c, ax, (g[0]).pt_ax0[t]);
  int32_t is1 = dy_neq(c, ax, (g[0]).pt_ax1[t]);
  if (is0 == 0 && is1 == 0) {
  DySb* m = (DySb*)(dy_err(c));
  dy_puts(m, "represent phase_portrait for '");
  dy_pn(m, c, fl);
  dy_puts(m, "': map axis '");
  dy_pn(m, c, ax);
  dy_puts(m, "' is not one of (");
  dy_pn(m, c, (g[0]).pt_ax0[t]);
  dy_puts(m, ", ");
  dy_pn(m, c, (g[0]).pt_ax1[t]);
  dy_puts(m, ")");
  return;
}
  double lo = dy_float(c, p, caps[2], caps[3]);
  double hi = 0.0;
  if ((c[0]).err == 0) {
  hi = dy_float(c, p, caps[4], caps[5]);
}
  if ((c[0]).err != 0) {
  DySb* m4 = (DySb*)(dy_err(c));
  dy_puts(m4, "represent phase_portrait for '");
  dy_pn(m4, c, fl);
  dy_puts(m4, "': invalid range in map for '");
  dy_pn(m4, c, ax);
  dy_puts(m4, "'");
  return;
}
  if (is0 == 1) {
  (g[0]).pt_set0[t] = 1;
  (g[0]).pt_lo0[t] = lo;
  (g[0]).pt_hi0[t] = hi;
  (g[0]).pt_k0[t] = kind;
}
  if (is1 == 1) {
  (g[0]).pt_set1[t] = 1;
  (g[0]).pt_lo1[t] = lo;
  (g[0]).pt_hi1[t] = hi;
  (g[0]).pt_k1[t] = kind;
}
  done = 1;
}
}
  if (done == 0) {
  DySb* m5 = (DySb*)(dy_err(c));
  dy_puts(m5, "unknown item in represent phase_portrait for '");
  dy_pn(m5, c, fl);
  dy_puts(m5, "': ");
  dy_span(m5, p, s, e);
  return;
}
  if ((c[0]).err != 0) {
  return;
}
}
  i = (i + 1);
}
  if ((g[0]).pt_set0[t] == 0 || (g[0]).pt_set1[t] == 0) {
  DySb* m6 = (DySb*)(dy_err(c));
  dy_puts(m6, "represent phase_portrait for '");
  dy_pn(m6, c, fl);
  dy_puts(m6, "': need map for both '");
  dy_pn(m6, c, (g[0]).pt_ax0[t]);
  dy_puts(m6, "' and '");
  dy_pn(m6, c, (g[0]).pt_ax1[t]);
  dy_puts(m6, "'");
  return;
}
  if ((g[0]).pt_k0[t] == (g[0]).pt_k1[t]) {
  DySb* m7 = (DySb*)(dy_err(c));
  dy_puts(m7, "represent phase_portrait for '");
  dy_pn(m7, c, fl);
  dy_puts(m7, "': maps must assign one axis to col and one to row");
}
}

int32_t dy_rep_head(uint8_t* p, int32_t s, int32_t e, int32_t* caps) {
  int32_t k = dy_match(p, s, e, "represent^@", caps);
  if (k < 0) {
  return 0;
}
  int32_t* sub = (int32_t*)(dy_i32s(4));
  caps[2] = (0 - 1);
  caps[3] = (0 - 1);
  int32_t a = dy_match(p, k, e, "^for^@~{", sub);
  if (a >= 0) {
  caps[2] = sub[0];
  caps[3] = sub[1];
  free((uint8_t*)(sub));
  return 1;
}
  int32_t b = dy_match(p, k, e, "^@~{", sub);
  if (b >= 0) {
  caps[2] = sub[0];
  caps[3] = sub[1];
  free((uint8_t*)(sub));
  return 1;
}
  free((uint8_t*)(sub));
  if (dy_match(p, k, e, "~{", sub) >= 0) {
  return 1;
}
  return 0;
}

void dy_extract_represent(DyC* c, uint8_t* p, int32_t n, Dp* g, DySb* out) {
  int32_t* ls = (int32_t*)(dy_i32s((n + 2)));
  int32_t* le = (int32_t*)(dy_i32s((n + 2)));
  int32_t nl = dy_split_lines(p, n, ls, le);
  int32_t* bs = (int32_t*)(dy_i32s((nl + 2)));
  int32_t* be = (int32_t*)(dy_i32s((nl + 2)));
  int32_t* nb = (int32_t*)(dy_i32s(1));
  int32_t* se = (int32_t*)(dy_i32s(2));
  int32_t* caps = (int32_t*)(dy_i32s(16));
  int32_t first = 1;
  int32_t depth = 0;
  int32_t cur = (0 - 1);
  int32_t fbd = 0;
  int32_t have_fbd = 0;
  int32_t i = 0;
  while (i < nl) {
  int32_t a = ls[i];
  int32_t b = le[i];
  se[0] = a;
  se[1] = b;
  dy_strip_comments(p, se);
  int32_t s = se[0];
  int32_t e = se[1];
  int32_t handled = 0;
  if (s < e && depth == 0) {
  if (dy_match(p, s, e, "flow^@~{", caps) >= 0) {
  cur = dy_name(c, p, caps[0], caps[1]);
  int32_t delta = (dy_count(p, a, b, 123) - dy_count(p, a, b, 125));
  fbd = (depth + delta);
  have_fbd = 1;
  if (first == 0) {
  dy_putc(out, 10);
}
  first = 0;
  dy_span(out, p, a, b);
  depth = (depth + delta);
  i = (i + 1);
  handled = 1;
}
}
  if (handled == 0 && s < e) {
  if (dy_match(p, s, e, "represent^phase_portrait~(~@~,~@~)~{", caps) >= 0) {
  int32_t ax0 = dy_name(c, p, caps[0], caps[1]);
  int32_t ax1 = dy_name(c, p, caps[2], caps[3]);
  int32_t nxt = dy_block(p, ls, le, nl, i, bs, be, nb);
  if (cur < 0 || have_fbd == 0 || depth < fbd) {
  dy_err_s(c, "represent phase_portrait(...) must appear inside `flow Name { ... }`");
  return;
}
  int32_t t = (g[0]).npt;
  (g[0]).pt_flow[t] = cur;
  (g[0]).pt_ax0[t] = ax0;
  (g[0]).pt_ax1[t] = ax1;
  (g[0]).pt_trail[t] = 320;
  (g[0]).pt_w[t] = 900;
  (g[0]).pt_h[t] = 700;
  (g[0]).pt_set0[t] = 0;
  (g[0]).pt_set1[t] = 0;
  (g[0]).pt_k0[t] = 0;
  (g[0]).pt_k1[t] = 0;
  dy_portrait_body(c, p, g, t, bs, be, nb[0]);
  if ((c[0]).err != 0) {
  return;
}
  (g[0]).npt = (t + 1);
  i = nxt;
  handled = 1;
}
}
  if (handled == 0 && s < e) {
  if (dy_rep_head(p, s, e, caps) == 1) {
  int32_t ks = caps[0];
  int32_t ke = caps[1];
  int32_t xs = caps[2];
  int32_t xe = caps[3];
  int32_t nxt2 = dy_block(p, ls, le, nl, i, bs, be, nb);
  if (dy_eq(p, ks, ke, "nonlinear") == 0) {
  if (dy_eq(p, ks, ke, "phase_portrait") == 1) {
  dy_err_s(c, "represent phase_portrait needs axes: `represent phase_portrait(x, z) { ... }`");
  return;
}
  if (dy_eq(p, ks, ke, "koopman") == 1 || dy_eq(p, ks, ke, "transfer_function") == 1 || dy_eq(p, ks, ke, "frequency") == 1) {
  DySb* m = (DySb*)(dy_err(c));
  dy_puts(m, "represent ");
  dy_span(m, p, ks, ke);
  dy_puts(m, ": not yet implemented (Stage-1 ships `represent linear` with explicit A/B/C; see docs/vision/north-star.md ");
  dy_utf8(m, DY_SECTION);
  dy_puts(m, "9)");
  return;
}
  if (dy_eq(p, ks, ke, "linear") == 0) {
  DySb* m2 = (DySb*)(dy_err(c));
  dy_puts(m2, "unknown represent kind '");
  dy_span(m2, p, ks, ke);
  dy_puts(m2, "'; expected linear, nonlinear, phase_portrait, or a reserved form (koopman|transfer_function|frequency)");
  return;
}
  int32_t fname = (0 - 1);
  if (xs >= 0) {
  fname = dy_name(c, p, xs, xe);
} else {
  if (cur >= 0 && have_fbd == 1 && depth >= fbd) {
  fname = cur;
} else {
  dy_err_s(c, "represent linear { ... } at top level needs a flow name: `represent linear Name { ... }` or place the block inside `flow Name { ... }`");
  return;
}
}
  int32_t r = (g[0]).nrp;
  (g[0]).rp_flow[r] = fname;
  (g[0]).rp_mode[r] = 1;
  (g[0]).rp_dt[r] = 0.001;
  (g[0]).rp_n[r] = 0;
  (g[0]).rp_m[r] = 0;
  (g[0]).rp_p[r] = 0;
  (g[0]).rp_an[r] = 0;
  (g[0]).rp_bn[r] = 0;
  (g[0]).rp_cn[r] = 0;
  (g[0]).rp_a0[r] = 0;
  (g[0]).rp_b0[r] = 0;
  (g[0]).rp_c0[r] = 0;
  (g[0]).rp_at0[r] = 0;
  (g[0]).rp_atn[r] = 0;
  (g[0]).rp_nin[r] = 0;
  dy_rep_linear_body(c, p, g, r, bs, be, nb[0]);
  if ((c[0]).err != 0) {
  return;
}
  (g[0]).nrp = (r + 1);
}
  i = nxt2;
  handled = 1;
}
}
  if (handled == 0) {
  if (dy_has_nonws(p, a, b) == 1) {
  depth = ((depth + dy_count(p, a, b, 123)) - dy_count(p, a, b, 125));
  if (cur >= 0 && have_fbd == 1 && depth < fbd) {
  cur = (0 - 1);
  have_fbd = 0;
}
}
  if (first == 0) {
  dy_putc(out, 10);
}
  first = 0;
  dy_span(out, p, a, b);
  i = (i + 1);
}
}
}

void dy_at_repr(DySb* m, DyC* c, Dp* g, int32_t r) {
  dy_putc(m, 123);
  int32_t q = 0;
  while (q < (g[0]).rp_atn[r]) {
  if (q > 0) {
  dy_puts(m, ", ");
}
  int32_t k = ((g[0]).rp_at0[r] + q);
  uint8_t* nm = (uint8_t*)((((c[0]).nm[0]).p + (c[0]).at_name[k]));
  dy_repr_str(m, nm, 0, (int32_t)(strlen((const char*)(nm))));
  dy_puts(m, ": ");
  dy_repr(m, (c[0]).at_val[k]);
  q = (q + 1);
}
  dy_putc(m, 125);
}

void dy_rep_prefix(DySb* m, DyC* c, Dp* g, int32_t r) {
  dy_puts(m, "represent linear for '");
  dy_pn(m, c, (g[0]).rp_flow[r]);
  dy_puts(m, "': ");
}

void dy_rep_to_dsys(DyC* c, Dp* g, int32_t r) {
  int32_t an = (g[0]).rp_an[r];
  if (an == 0) {
  DySb* m = (DySb*)(dy_err(c));
  dy_rep_prefix(m, c, g, r);
  dy_puts(m, "linearization coefficients required");
  if ((g[0]).rp_atn[r] > 0) {
  dy_puts(m, " (operating point at ");
  dy_at_repr(m, c, g, r);
  dy_puts(m, " was given, but automatic Jacobian linearization is not yet implemented)");
}
  dy_puts(m, "; supply explicit A (and optional B/C) matrices in the represent linear block, e.g. `A 0.0 1.0 -9.81 0.0`");
  return;
}
  int64_t n = (g[0]).rp_n[r];
  if (n <= 0) {
  int64_t root = 0;
  while (((root + 1) * (root + 1)) <= (int64_t)(an)) {
  root = (root + 1);
}
  if ((((root + 1) * (root + 1)) - (int64_t)(an)) < ((int64_t)(an) - (root * root))) {
  root = (root + 1);
}
  if ((root * root) != (int64_t)(an) || root < 1) {
  DySb* m2 = (DySb*)(dy_err(c));
  dy_rep_prefix(m2, c, g, r);
  dy_puts(m2, "A must list n");
  dy_utf8(m2, DY_TIMES);
  dy_puts(m2, "n floats (got ");
  dy_i64(m2, (int64_t)(an));
  dy_puts(m2, " values); or set `n` explicitly");
  return;
}
  n = root;
} else {
  if ((int64_t)(an) != (n * n)) {
  DySb* m3 = (DySb*)(dy_err(c));
  dy_rep_prefix(m3, c, g, r);
  dy_puts(m3, "A has ");
  dy_i64(m3, (int64_t)(an));
  dy_puts(m3, " entries but n=");
  dy_i64(m3, n);
  dy_puts(m3, " expects ");
  dy_i64(m3, (n * n));
  return;
}
}
  int64_t mm = (g[0]).rp_m[r];
  int32_t b0 = (g[0]).rp_b0[r];
  int32_t bn = (g[0]).rp_bn[r];
  if (bn == 0) {
  if (mm < 0) {
  mm = 0;
}
  int64_t zeros = 0;
  if (mm == 0 && (g[0]).rp_nin[r] > 0) {
  mm = (int64_t)((g[0]).rp_nin[r]);
  zeros = (n * mm);
} else {
  if (mm == 0) {
  zeros = 1;
} else {
  zeros = (n * mm);
}
}
  b0 = (c[0]).fnum;
  int64_t z = 0;
  while (z < zeros) {
  dy_fpush(c, 0.0);
  z = (z + 1);
}
  bn = (int32_t)(zeros);
} else {
  if (mm <= 0) {
  if (((int64_t)(bn) % n) != 0) {
  DySb* m4 = (DySb*)(dy_err(c));
  dy_rep_prefix(m4, c, g, r);
  dy_puts(m4, "B length ");
  dy_i64(m4, (int64_t)(bn));
  dy_puts(m4, " is not a multiple of n=");
  dy_i64(m4, n);
  return;
}
  mm = ((int64_t)(bn) / n);
} else {
  if ((int64_t)(bn) != (n * mm)) {
  DySb* m5 = (DySb*)(dy_err(c));
  dy_rep_prefix(m5, c, g, r);
  dy_puts(m5, "B has ");
  dy_i64(m5, (int64_t)(bn));
  dy_puts(m5, " entries but n=");
  dy_i64(m5, n);
  dy_puts(m5, " m=");
  dy_i64(m5, mm);
  dy_puts(m5, " expects ");
  dy_i64(m5, (n * mm));
  return;
}
}
}
  int64_t pp = (g[0]).rp_p[r];
  int32_t c0 = (g[0]).rp_c0[r];
  int32_t cn = (g[0]).rp_cn[r];
  if (cn == 0) {
  if (pp <= 0) {
  pp = n;
}
  if (pp != n) {
  DySb* m6 = (DySb*)(dy_err(c));
  dy_rep_prefix(m6, c, g, r);
  dy_puts(m6, "supply C (p");
  dy_utf8(m6, DY_TIMES);
  dy_puts(m6, "n) when p != n (got p=");
  dy_i64(m6, pp);
  dy_puts(m6, ", n=");
  dy_i64(m6, n);
  dy_puts(m6, ")");
  return;
}
  c0 = (c[0]).fnum;
  int64_t ii = 0;
  while (ii < pp) {
  int64_t jj = 0;
  while (jj < n) {
  if (ii == jj) {
  dy_fpush(c, 1.0);
} else {
  dy_fpush(c, 0.0);
}
  jj = (jj + 1);
}
  ii = (ii + 1);
}
  cn = (int32_t)((pp * n));
} else {
  if (pp <= 0) {
  if (((int64_t)(cn) % n) != 0) {
  DySb* m7 = (DySb*)(dy_err(c));
  dy_rep_prefix(m7, c, g, r);
  dy_puts(m7, "C length ");
  dy_i64(m7, (int64_t)(cn));
  dy_puts(m7, " is not a multiple of n=");
  dy_i64(m7, n);
  return;
}
  pp = ((int64_t)(cn) / n);
} else {
  if ((int64_t)(cn) != (pp * n)) {
  DySb* m8 = (DySb*)(dy_err(c));
  dy_rep_prefix(m8, c, g, r);
  dy_puts(m8, "C has ");
  dy_i64(m8, (int64_t)(cn));
  dy_puts(m8, " entries but p=");
  dy_i64(m8, pp);
  dy_puts(m8, " n=");
  dy_i64(m8, n);
  dy_puts(m8, " expects ");
  dy_i64(m8, (pp * n));
  return;
}
}
}
  int32_t off = ((c[0]).nm[0]).len;
  dy_pn((c[0]).nm, c, (g[0]).rp_flow[r]);
  dy_puts((c[0]).nm, "_lin");
  dy_putc((c[0]).nm, 0);
  if (dy_find_sys(c, g, off) >= 0) {
  DySb* m9 = (DySb*)(dy_err(c));
  dy_rep_prefix(m9, c, g, r);
  ((c[0]).msg[0]).len = (((c[0]).msg[0]).len - 2);
  dy_puts(m9, " conflicts with an existing dsys '");
  dy_pn(m9, c, off);
  dy_puts(m9, "'");
  return;
}
  int32_t k = dy_sys_slot(c, g, off);
  (g[0]).sy_mode[k] = (g[0]).rp_mode[r];
  (g[0]).sy_dt[k] = (g[0]).rp_dt[r];
  (g[0]).sy_n[k] = n;
  (g[0]).sy_m[k] = mm;
  (g[0]).sy_p[k] = pp;
  (g[0]).sy_a0[k] = (g[0]).rp_a0[r];
  (g[0]).sy_an[k] = an;
  (g[0]).sy_b0[k] = b0;
  (g[0]).sy_bn[k] = bn;
  (g[0]).sy_c0[k] = c0;
  (g[0]).sy_cn[k] = cn;
}

void dy_invalid(DyC* c, const char* what, uint8_t* p, int32_t s, int32_t e) {
  DySb* m = (DySb*)(dy_err(c));
  dy_puts(m, what);
  dy_span(m, p, s, e);
}

int32_t dy_arrow(uint8_t* p, int32_t s, int32_t e, int32_t* l, int32_t* r) {
  int32_t a = dy_find_str(p, s, e, "->");
  if (a < 0) {
  return 0;
}
  l[0] = s;
  l[1] = a;
  dy_strip(p, l);
  r[0] = (a + 2);
  r[1] = e;
  dy_strip(p, r);
  return 1;
}

void dy_lqr_prefix(DySb* m, DyC* c, int32_t sys) {
  dy_puts(m, "analyze ");
  dy_pn(m, c, sys);
  dy_puts(m, " lqr: ");
}

void dy_lqr(DyC* c, uint8_t* p, Dp* g, int32_t sys, int32_t* bs, int32_t* be, int32_t nb) {
  int32_t* se = (int32_t*)(dy_i32s(2));
  int32_t* f0 = (int32_t*)(dy_i32s(1));
  int32_t q0 = 0;
  int32_t qn = 0;
  double rr = 1.0;
  int32_t g0 = 0;
  int32_t gn = 0;
  int64_t it = 200;
  int32_t i = 0;
  while (i < nb) {
  se[0] = bs[i];
  se[1] = be[i];
  dy_strip_comments(p, se);
  int32_t s = se[0];
  int32_t e = se[1];
  if (s < e) {
  if (dy_starts(p, s, e, "Q ") == 1) {
  qn = dy_floats(c, p, (s + 2), e, f0);
  q0 = f0[0];
} else {
  if (dy_starts(p, s, e, "R ") == 1) {
  int32_t* ws = (int32_t*)(dy_i32s(((e - s) + 1)));
  int32_t* we = (int32_t*)(dy_i32s(((e - s) + 1)));
  int32_t np = dy_split_ws(p, s, e, ws, we);
  if (np != 2) {
  DySb* m = (DySb*)(dy_err(c));
  dy_lqr_prefix(m, c, sys);
  dy_puts(m, "expected `R <scalar>`, got '");
  dy_span(m, p, s, e);
  dy_puts(m, "'");
  return;
}
  rr = dy_float(c, p, ws[1], we[1]);
} else {
  if (dy_starts(p, s, e, "max_iter ") == 1) {
  it = dy_int_part(c, p, s, e, 1);
} else {
  if (dy_starts(p, s, e, "->") == 1) {
  int32_t* ws2 = (int32_t*)(dy_i32s(((e - s) + 1)));
  int32_t* we2 = (int32_t*)(dy_i32s(((e - s) + 1)));
  int32_t nn = dy_split_ws(p, (s + 2), e, ws2, we2);
  if (nn == 0) {
  DySb* m2 = (DySb*)(dy_err(c));
  dy_lqr_prefix(m2, c, sys);
  dy_puts(m2, "`->` needs gain variable names");
  return;
}
  int32_t k = 0;
  while (k < nn) {
  if (dy_all_word(p, ws2[k], we2[k]) == 0) {
  DySb* m3 = (DySb*)(dy_err(c));
  dy_lqr_prefix(m3, c, sys);
  dy_puts(m3, "invalid gain name '");
  dy_span(m3, p, ws2[k], we2[k]);
  dy_puts(m3, "'");
  return;
}
  k = (k + 1);
}
  g0 = (c[0]).ngl;
  k = 0;
  while (k < nn) {
  dy_gl(c, dy_name(c, p, ws2[k], we2[k]));
  k = (k + 1);
}
  gn = nn;
} else {
  DySb* m4 = (DySb*)(dy_err(c));
  dy_lqr_prefix(m4, c, sys);
  dy_puts(m4, "unknown item '");
  dy_span(m4, p, s, e);
  dy_puts(m4, "' (expected Q / R / max_iter / -> gains)");
  return;
}
}
}
}
  if ((c[0]).err != 0) {
  return;
}
}
  i = (i + 1);
}
  if (qn == 0) {
  DySb* m5 = (DySb*)(dy_err(c));
  dy_lqr_prefix(m5, c, sys);
  dy_puts(m5, "missing `Q ");
  dy_utf8(m5, DY_ELLIPSIS);
  dy_puts(m5, "` diagonal");
  return;
}
  if (gn == 0) {
  DySb* m6 = (DySb*)(dy_err(c));
  dy_lqr_prefix(m6, c, sys);
  dy_puts(m6, "missing `-> k0 k1 ");
  dy_utf8(m6, DY_ELLIPSIS);
  dy_puts(m6, "` gain bindings");
  return;
}
  if (gn != qn) {
  DySb* m7 = (DySb*)(dy_err(c));
  dy_lqr_prefix(m7, c, sys);
  dy_puts(m7, "Q has ");
  dy_i64(m7, (int64_t)(qn));
  dy_puts(m7, " entries but -> lists ");
  dy_i64(m7, (int64_t)(gn));
  dy_puts(m7, " gains (need one gain per state)");
  return;
}
  int32_t t = (g[0]).nlq;
  (g[0]).lq_sys[t] = sys;
  (g[0]).lq_q0[t] = q0;
  (g[0]).lq_qn[t] = qn;
  (g[0]).lq_r[t] = rr;
  (g[0]).lq_g0[t] = g0;
  (g[0]).lq_gn[t] = gn;
  (g[0]).lq_it[t] = it;
  (g[0]).nlq = (t + 1);
}

void dy_an_prefix(DySb* m, DyC* c, int32_t sys) {
  dy_puts(m, "analyze ");
  dy_pn(m, c, sys);
  dy_puts(m, ": ");
}

void dy_lqr_braces(DySb* m) {
  dy_puts(m, "`lqr { ");
  dy_utf8(m, DY_ELLIPSIS);
  dy_puts(m, " }`");
}

void dy_analyze_vision(DyC* c, uint8_t* p, Dp* g, int32_t sys, int32_t* bs, int32_t* be, int32_t nb) {
  int32_t* se = (int32_t*)(dy_i32s(2));
  int32_t* cs = (int32_t*)(dy_i32s((nb + 2)));
  int32_t* ce = (int32_t*)(dy_i32s((nb + 2)));
  int32_t* cn = (int32_t*)(dy_i32s(1));
  int32_t saw = 0;
  int32_t i = 0;
  while (i < nb) {
  se[0] = bs[i];
  se[1] = be[i];
  dy_strip_comments(p, se);
  int32_t s = se[0];
  int32_t e = se[1];
  if (s >= e) {
  i = (i + 1);
} else {
  if (dy_starts(p, s, e, "lqr") == 1 && dy_find(p, s, e, 123) >= 0) {
  int32_t nx = dy_block(p, bs, be, nb, i, cs, ce, cn);
  dy_lqr(c, p, g, sys, cs, ce, cn[0]);
  if ((c[0]).err != 0) {
  return;
}
  saw = 1;
  i = nx;
} else {
  if (dy_eq(p, s, e, "lqr") == 1) {
  if ((i + 1) >= nb || dy_find(p, bs[(i + 1)], be[(i + 1)], 123) < 0) {
  DySb* m = (DySb*)(dy_err(c));
  dy_an_prefix(m, c, sys);
  dy_puts(m, "expected ");
  dy_lqr_braces(m);
  return;
}
  int32_t nx2 = dy_block(p, bs, be, nb, (i + 1), cs, ce, cn);
  dy_lqr(c, p, g, sys, cs, ce, cn[0]);
  if ((c[0]).err != 0) {
  return;
}
  saw = 1;
  i = nx2;
} else {
  DySb* m2 = (DySb*)(dy_err(c));
  dy_an_prefix(m2, c, sys);
  dy_puts(m2, "Stage-1 supports ");
  dy_lqr_braces(m2);
  dy_puts(m2, " only; got '");
  dy_span(m2, p, s, e);
  dy_puts(m2, "'");
  return;
}
}
}
}
  if (saw == 0) {
  DySb* m3 = (DySb*)(dy_err(c));
  dy_an_prefix(m3, c, sys);
  dy_puts(m3, "empty body ");
  dy_utf8(m3, DY_DASH);
  dy_puts(m3, " add `lqr { Q ");
  dy_utf8(m3, DY_ELLIPSIS);
  dy_puts(m3, " R ");
  dy_utf8(m3, DY_ELLIPSIS);
  dy_puts(m3, " -> ");
  dy_utf8(m3, DY_ELLIPSIS);
  dy_puts(m3, " }`");
}
}

void dy_validate_raw(DyC* c, Dp* g) {
  int32_t i = 0;
  while (i < (g[0]).nsy) {
  int32_t name = (g[0]).sy_name[i];
  int32_t synth = 0;
  int32_t r = 0;
  while (r < (g[0]).nrp) {
  int32_t off = ((c[0]).nm[0]).len;
  dy_pn((c[0]).nm, c, (g[0]).rp_flow[r]);
  dy_puts((c[0]).nm, "_lin");
  dy_putc((c[0]).nm, 0);
  if (dy_neq(c, off, name) == 1) {
  synth = 1;
}
  r = (r + 1);
}
  if (synth == 0) {
  int64_t n = (g[0]).sy_n[i];
  int64_t mm = (g[0]).sy_m[i];
  int64_t pp = (g[0]).sy_p[i];
  if (n <= 0) {
  DySb* m = (DySb*)(dy_err(c));
  dy_puts(m, "dsys '");
  dy_pn(m, c, name);
  dy_puts(m, "': n must be positive, got ");
  dy_i64(m, n);
  return;
}
  if (mm < 0) {
  DySb* m2 = (DySb*)(dy_err(c));
  dy_puts(m2, "dsys '");
  dy_pn(m2, c, name);
  dy_puts(m2, "': m must be non-negative, got ");
  dy_i64(m2, mm);
  return;
}
  if (pp <= 0) {
  DySb* m3 = (DySb*)(dy_err(c));
  dy_puts(m3, "dsys '");
  dy_pn(m3, c, name);
  dy_puts(m3, "': p must be positive, got ");
  dy_i64(m3, pp);
  return;
}
  if ((g[0]).sy_an[i] > 0 || (g[0]).sy_bn[i] > 0 || (g[0]).sy_cn[i] > 0) {
  int32_t which = 0;
  while (which < 3) {
  int64_t want = (n * n);
  int32_t got = (g[0]).sy_an[i];
  if (which == 1) {
  want = (n * mm);
  got = (g[0]).sy_bn[i];
}
  if (which == 2) {
  want = (pp * n);
  got = (g[0]).sy_cn[i];
}
  if ((int64_t)(got) != want) {
  DySb* m4 = (DySb*)(dy_err(c));
  dy_puts(m4, "dsys '");
  dy_pn(m4, c, name);
  dy_puts(m4, "': ");
  if (which == 0) {
  dy_puts(m4, "A needs ");
}
  if (which == 1) {
  dy_puts(m4, "B needs ");
}
  if (which == 2) {
  dy_puts(m4, "C needs ");
}
  dy_i64(m4, want);
  dy_puts(m4, " entries for ");
  if (which == 0) {
  dy_puts(m4, "n = ");
  dy_i64(m4, n);
}
  if (which == 1) {
  dy_puts(m4, "n = ");
  dy_i64(m4, n);
  dy_puts(m4, ", m = ");
  dy_i64(m4, mm);
}
  if (which == 2) {
  dy_puts(m4, "p = ");
  dy_i64(m4, pp);
  dy_puts(m4, ", n = ");
  dy_i64(m4, n);
}
  dy_puts(m4, ", got ");
  dy_i64(m4, (int64_t)(got));
  return;
}
  which = (which + 1);
}
}
}
  i = (i + 1);
}
}

int32_t dy_cp_prefix(uint8_t* p, int32_t s, int32_t e, int32_t limit) {
  int32_t k = s;
  int32_t cps = 0;
  while (k < e) {
  if (p[k] < 128 || p[k] >= 192) {
  if (cps == limit) {
  return k;
}
  cps = (cps + 1);
}
  k = (k + 1);
}
  return e;
}

void dy_parse(DyC* c, uint8_t* p0, int32_t n0, Dp* g, DySb* out) {
  DySb* st = (DySb*)(dy_sb_new((n0 + 16)));
  dy_extract_represent(c, p0, n0, g, st);
  if ((c[0]).err != 0) {
  return;
}
  int32_t r = 0;
  while (r < (g[0]).nrp) {
  dy_rep_to_dsys(c, g, r);
  if ((c[0]).err != 0) {
  return;
}
  r = (r + 1);
}
  uint8_t* p = (uint8_t*)((st[0]).p);
  int32_t n = (st[0]).len;
  int32_t* ls = (int32_t*)(dy_i32s((n + 2)));
  int32_t* le = (int32_t*)(dy_i32s((n + 2)));
  int32_t nl = dy_split_lines(p, n, ls, le);
  int32_t* bs = (int32_t*)(dy_i32s((nl + 2)));
  int32_t* be = (int32_t*)(dy_i32s((nl + 2)));
  int32_t* nb = (int32_t*)(dy_i32s(1));
  int32_t* se = (int32_t*)(dy_i32s(2));
  int32_t* l = (int32_t*)(dy_i32s(2));
  int32_t* rh = (int32_t*)(dy_i32s(2));
  int32_t* caps = (int32_t*)(dy_i32s(16));
  int32_t* f0 = (int32_t*)(dy_i32s(1));
  int32_t first = 1;
  int32_t i = 0;
  while (i < nl) {
  int32_t a = ls[i];
  int32_t b = le[i];
  se[0] = a;
  se[1] = b;
  dy_strip_comments(p, se);
  int32_t s = se[0];
  int32_t e = se[1];
  int32_t kept = 0;
  if (s >= e) {
  kept = 1;
} else {
  if (dy_match(p, s, e, "dyn~{", caps) >= 0 || dy_match(p, s, e, "dynamics~{", caps) >= 0) {
  int32_t nx = dy_block_keep(p, ls, le, nl, i, bs, be, nb);
  DySb* body = (DySb*)(dy_sb_new((n + 16)));
  int32_t q = 0;
  while (q < nb[0]) {
  if (q > 0) {
  dy_putc(body, 10);
}
  dy_span(body, p, bs[q], be[q]);
  q = (q + 1);
}
  dy_putc(body, 10);
  Dp* inner = (Dp*)(dy_prog_new((body[0]).len));
  DySb* left = (DySb*)(dy_sb_new(((body[0]).len + 16)));
  dy_parse(c, (body[0]).p, (body[0]).len, inner, left);
  if ((c[0]).err != 0) {
  return;
}
  int32_t* ls2 = (int32_t*)(dy_i32s(2));
  ls2[0] = 0;
  ls2[1] = (left[0]).len;
  dy_strip((left[0]).p, ls2);
  if (ls2[1] > ls2[0]) {
  DySb* m = (DySb*)(dy_err(c));
  dy_puts(m, "dynamics { ... } block may only contain dynamics DSL constructs; leftover:\n");
  dy_span(m, (left[0]).p, ls2[0], dy_cp_prefix((left[0]).p, ls2[0], ls2[1], 200));
  return;
}
  dy_merge(c, g, inner);
  i = nx;
} else {
  if (dy_starts(p, s, e, "dyn.") == 1 && e > (s + 4)) {
  s = (s + 4);
} else {
  if (dy_starts(p, s, e, "dynamics.") == 1 && e > (s + 9)) {
  s = (s + 9);
}
}
  se[0] = s;
  se[1] = e;
  dy_strip(p, se);
  s = se[0];
  e = se[1];
  if (dy_starts(p, s, e, "dsys ") == 1) {
  if (dy_match(p, s, e, "dsys^@~{", caps) < 0) {
  dy_invalid(c, "Invalid dsys declaration: ", p, s, e);
  return;
}
  int32_t name = dy_name(c, p, caps[0], caps[1]);
  int32_t nx2 = dy_block(p, ls, le, nl, i, bs, be, nb);
  int32_t k = (g[0]).nsy;
  (g[0]).sy_mode[k] = 0;
  (g[0]).sy_dt[k] = 0.1;
  (g[0]).sy_n[k] = 2;
  (g[0]).sy_m[k] = 1;
  (g[0]).sy_p[k] = 1;
  (g[0]).sy_an[k] = 0;
  (g[0]).sy_bn[k] = 0;
  (g[0]).sy_cn[k] = 0;
  (g[0]).sy_a0[k] = 0;
  (g[0]).sy_b0[k] = 0;
  (g[0]).sy_c0[k] = 0;
  int32_t j = 0;
  while (j < nb[0]) {
  l[0] = bs[j];
  l[1] = be[j];
  dy_strip_comments(p, l);
  int32_t ts = l[0];
  int32_t te = l[1];
  if (ts < te) {
  if (dy_eq(p, ts, te, "discrete") == 1) {
  (g[0]).sy_mode[k] = 0;
} else {
  if (dy_eq(p, ts, te, "continuous") == 1) {
  (g[0]).sy_mode[k] = 1;
} else {
  if (dy_starts(p, ts, te, "dt ") == 1) {
  (g[0]).sy_dt[k] = dy_float_part(c, p, ts, te, 1);
} else {
  if (dy_starts(p, ts, te, "n ") == 1) {
  dy_parse_nmp(c, p, ts, te, (g[0]).sy_n, (g[0]).sy_m, (g[0]).sy_p, k);
} else {
  if (dy_starts(p, ts, te, "A ") == 1) {
  (g[0]).sy_an[k] = dy_floats(c, p, (ts + 2), te, f0);
  (g[0]).sy_a0[k] = f0[0];
} else {
  if (dy_starts(p, ts, te, "B ") == 1) {
  (g[0]).sy_bn[k] = dy_floats(c, p, (ts + 2), te, f0);
  (g[0]).sy_b0[k] = f0[0];
} else {
  if (dy_starts(p, ts, te, "C ") == 1) {
  (g[0]).sy_cn[k] = dy_floats(c, p, (ts + 2), te, f0);
  (g[0]).sy_c0[k] = f0[0];
}
}
}
}
}
}
}
  if ((c[0]).err != 0) {
  return;
}
}
  j = (j + 1);
}
  if (dy_find_sys(c, g, name) >= 0) {
  DySb* m2 = (DySb*)(dy_err(c));
  dy_puts(m2, "dsys '");
  dy_pn(m2, c, name);
  dy_puts(m2, "' redeclared (conflicts with a prior dsys or represent linear ");
  dy_utf8(m2, DY_ARROW);
  dy_puts(m2, " '");
  dy_pn(m2, c, name);
  dy_puts(m2, "')");
  return;
}
  (g[0]).sy_name[k] = name;
  (g[0]).nsy = (k + 1);
  i = nx2;
} else {
  if (dy_starts(p, s, e, "horizon ") == 1) {
  if (dy_match(p, s, e, "horizon^@^finite^#", caps) >= 0) {
  int32_t hn = dy_name(c, p, caps[0], caps[1]);
  int64_t steps = dy_int(c, p, caps[2], caps[3]);
  if ((c[0]).err != 0) {
  return;
}
  int32_t hk = dy_hz_slot(c, g, hn);
  (g[0]).hz_kind[hk] = 0;
  (g[0]).hz_steps[hk] = steps;
  (g[0]).hz_gamma[hk] = 1.0;
} else {
  if (dy_match(p, s, e, "horizon^@^infinite^gamma^$", caps) >= 0) {
  int32_t hn2 = dy_name(c, p, caps[0], caps[1]);
  double gm = dy_float(c, p, caps[2], caps[3]);
  if ((c[0]).err != 0) {
  return;
}
  int32_t hk2 = dy_hz_slot(c, g, hn2);
  (g[0]).hz_kind[hk2] = 1;
  (g[0]).hz_steps[hk2] = 0;
  (g[0]).hz_gamma[hk2] = gm;
} else {
  dy_invalid(c, "Invalid horizon: ", p, s, e);
  return;
}
}
  i = (i + 1);
} else {
  i = dy_parse_rest(c, p, g, ls, le, nl, i, s, e, bs, be, nb, (&kept));
  if ((c[0]).err != 0) {
  return;
}
}
}
}
}
  if (kept == 1) {
  if (first == 0) {
  dy_putc(out, 10);
}
  first = 0;
  dy_span(out, p, a, b);
  i = (i + 1);
}
}
  dy_validate_raw(c, g);
}

int32_t dy_parse_rest(DyC* c, uint8_t* p, Dp* g, int32_t* ls, int32_t* le, int32_t nl, int32_t i, int32_t s, int32_t e, int32_t* bs, int32_t* be, int32_t* nb, int32_t* kept) {
  int32_t* caps = (int32_t*)(dy_i32s(20));
  int32_t* l = (int32_t*)(dy_i32s(2));
  int32_t* r = (int32_t*)(dy_i32s(2));
  int32_t* bl = (int32_t*)(dy_i32s(2));
  if (dy_starts(p, s, e, "sense on ") == 1) {
  if (dy_match(p, s, e, "sense^on^@~{", caps) < 0) {
  dy_invalid(c, "Invalid sense block: ", p, s, e);
  return i;
}
  int32_t sys = dy_name(c, p, caps[0], caps[1]);
  int32_t nx = dy_block(p, ls, le, nl, i, bs, be, nb);
  int32_t b0 = (c[0]).nbd;
  int32_t j = 0;
  while (j < nb[0]) {
  bl[0] = bs[j];
  bl[1] = be[j];
  dy_strip_comments(p, bl);
  if (dy_arrow(p, bl[0], bl[1], l, r) == 1) {
  if (dy_eq(p, l[0], l[1], "controllable") == 1) {
  dy_bd(c, 1, dy_name(c, p, r[0], r[1]), (0 - 1));
} else {
  if (dy_eq(p, l[0], l[1], "spectral") == 1) {
  dy_bd(c, 2, dy_name(c, p, r[0], r[1]), (0 - 1));
} else {
  if (dy_starts(p, l[0], l[1], "gramian finite ") == 1) {
  int32_t hz = dy_name_part(c, p, l[0], l[1], 2);
  dy_bd(c, 3, dy_name(c, p, r[0], r[1]), hz);
} else {
  if (dy_starts(p, l[0], l[1], "gramian infinite ") == 1) {
  int32_t hz2 = dy_name_part(c, p, l[0], l[1], 2);
  dy_bd(c, 4, dy_name(c, p, r[0], r[1]), hz2);
}
}
}
}
}
  j = (j + 1);
}
  int32_t t = (g[0]).nse;
  (g[0]).se_sys[t] = sys;
  (g[0]).se_b0[t] = b0;
  (g[0]).se_bn[t] = ((c[0]).nbd - b0);
  (g[0]).nse = (t + 1);
  return nx;
}
  if (dy_starts(p, s, e, "ga evolve on ") == 1) {
  if (dy_match(p, s, e, "ga^evolve^on^@^over^@~->~@^@~{", caps) < 0) {
  dy_invalid(c, "Invalid ga evolve block: ", p, s, e);
  return i;
}
  int32_t t2 = (g[0]).nga;
  (g[0]).ga_sys[t2] = dy_name(c, p, caps[0], caps[1]);
  (g[0]).ga_hz[t2] = dy_name(c, p, caps[2], caps[3]);
  (g[0]).ga_k1[t2] = dy_name(c, p, caps[4], caps[5]);
  (g[0]).ga_k2[t2] = dy_name(c, p, caps[6], caps[7]);
  (g[0]).ga_pop[t2] = 8;
  (g[0]).ga_gen[t2] = 20;
  (g[0]).ga_mut[t2] = 0.3;
  int32_t nx2 = dy_block(p, ls, le, nl, i, bs, be, nb);
  int32_t j2 = 0;
  while (j2 < nb[0]) {
  bl[0] = bs[j2];
  bl[1] = be[j2];
  dy_strip_comments(p, bl);
  if (dy_starts(p, bl[0], bl[1], "population ") == 1) {
  (g[0]).ga_pop[t2] = dy_int_part(c, p, bl[0], bl[1], 1);
} else {
  if (dy_starts(p, bl[0], bl[1], "generations ") == 1) {
  (g[0]).ga_gen[t2] = dy_int_part(c, p, bl[0], bl[1], 1);
} else {
  if (dy_starts(p, bl[0], bl[1], "mutation ") == 1) {
  (g[0]).ga_mut[t2] = dy_float_part(c, p, bl[0], bl[1], 1);
}
}
}
  if ((c[0]).err != 0) {
  return i;
}
  j2 = (j2 + 1);
}
  (g[0]).nga = (t2 + 1);
  return nx2;
}
  if (dy_starts(p, s, e, "closed ") == 1) {
  if (dy_match(p, s, e, "closed^@^with^@^@~{", caps) < 0) {
  dy_invalid(c, "Invalid closed block: ", p, s, e);
  return i;
}
  int32_t t3 = (g[0]).ncl;
  (g[0]).cl_sys[t3] = dy_name(c, p, caps[0], caps[1]);
  (g[0]).cl_k1[t3] = dy_name(c, p, caps[2], caps[3]);
  (g[0]).cl_k2[t3] = dy_name(c, p, caps[4], caps[5]);
  int32_t nx3 = dy_block(p, ls, le, nl, i, bs, be, nb);
  int32_t b3 = (c[0]).nbd;
  int32_t j3 = 0;
  while (j3 < nb[0]) {
  bl[0] = bs[j3];
  bl[1] = be[j3];
  dy_strip_comments(p, bl);
  if (dy_arrow(p, bl[0], bl[1], l, r) == 1) {
  if (dy_eq(p, l[0], l[1], "spectral") == 1) {
  dy_bd(c, 5, dy_name(c, p, r[0], r[1]), (0 - 1));
} else {
  if (dy_eq(p, l[0], l[1], "stable") == 1) {
  dy_bd(c, 6, dy_name(c, p, r[0], r[1]), (0 - 1));
} else {
  if (dy_starts(p, l[0], l[1], "energy over ") == 1) {
  int32_t hz3 = dy_name_part(c, p, l[0], l[1], 2);
  dy_bd(c, 7, dy_name(c, p, r[0], r[1]), hz3);
}
}
}
}
  j3 = (j3 + 1);
}
  (g[0]).cl_b0[t3] = b3;
  (g[0]).cl_bn[t3] = ((c[0]).nbd - b3);
  (g[0]).ncl = (t3 + 1);
  return nx3;
}
  if (dy_starts(p, s, e, "analyze ") == 1) {
  if (dy_match(p, s, e, "analyze^@^ga^@^@^over^@~->~@~{", caps) >= 0) {
  int32_t t4 = (g[0]).nanz;
  (g[0]).an_sys[t4] = dy_name(c, p, caps[0], caps[1]);
  (g[0]).an_k1[t4] = dy_name(c, p, caps[2], caps[3]);
  (g[0]).an_k2[t4] = dy_name(c, p, caps[4], caps[5]);
  (g[0]).an_hz[t4] = dy_name(c, p, caps[6], caps[7]);
  (g[0]).an_rep[t4] = dy_name(c, p, caps[8], caps[9]);
  (g[0]).nanz = (t4 + 1);
  return dy_block(p, ls, le, nl, i, bs, be, nb);
}
  if (dy_match(p, s, e, "analyze^@~{", caps) < 0) {
  DySb* m = (DySb*)(dy_err(c));
  dy_puts(m, "Invalid analyze block: ");
  dy_span(m, p, s, e);
  dy_puts(m, " (expected `analyze Name ga k1 k2 over H -> r {{");
  dy_utf8(m, DY_ELLIPSIS);
  dy_puts(m, "}}` or `analyze Name {{ lqr {{ ");
  dy_utf8(m, DY_ELLIPSIS);
  dy_puts(m, " }} }}`)");
  return i;
}
  int32_t sys5 = dy_name(c, p, caps[0], caps[1]);
  int32_t nx5 = dy_block_keep(p, ls, le, nl, i, bs, be, nb);
  dy_analyze_vision(c, p, g, sys5, bs, be, nb[0]);
  return nx5;
}
  if (dy_starts(p, s, e, "wfc field ") == 1) {
  if (dy_match(p, s, e, "wfc^field^@~{", caps) < 0) {
  dy_invalid(c, "Invalid wfc field block: ", p, s, e);
  return i;
}
  int32_t wn = dy_name(c, p, caps[0], caps[1]);
  int32_t nx6 = dy_block(p, ls, le, nl, i, bs, be, nb);
  int64_t w = 4;
  int64_t h = 4;
  int64_t tiles = 3;
  int64_t seed = 7;
  int64_t pc = 0;
  int64_t pt = 1;
  int64_t steps = 20;
  int32_t j6 = 0;
  while (j6 < nb[0]) {
  bl[0] = bs[j6];
  bl[1] = be[j6];
  dy_strip_comments(p, bl);
  int32_t ts = bl[0];
  int32_t te = bl[1];
  if (dy_starts(p, ts, te, "size ") == 1) {
  w = dy_int_part(c, p, ts, te, 1);
  if ((c[0]).err == 0) {
  h = dy_int_part(c, p, ts, te, 2);
}
} else {
  if (dy_starts(p, ts, te, "tiles ") == 1) {
  tiles = dy_int_part(c, p, ts, te, 1);
} else {
  if (dy_starts(p, ts, te, "seed ") == 1) {
  seed = dy_int_part(c, p, ts, te, 1);
} else {
  if (dy_starts(p, ts, te, "pin ") == 1) {
  pc = dy_int_part(c, p, ts, te, 1);
  if ((c[0]).err == 0) {
  pt = dy_int_part(c, p, ts, te, 2);
}
} else {
  if (dy_starts(p, ts, te, "collapse ") == 1) {
  steps = dy_int_part(c, p, ts, te, 1);
}
}
}
}
}
  if ((c[0]).err != 0) {
  return i;
}
  j6 = (j6 + 1);
}
  int32_t t6 = dy_wf_slot(c, g, wn);
  (g[0]).wf_w[t6] = w;
  (g[0]).wf_h[t6] = h;
  (g[0]).wf_tiles[t6] = tiles;
  (g[0]).wf_seed[t6] = seed;
  (g[0]).wf_pc[t6] = pc;
  (g[0]).wf_pt[t6] = pt;
  (g[0]).wf_steps[t6] = steps;
  return nx6;
}
  if (dy_starts(p, s, e, "couple ") == 1) {
  if (dy_match(p, s, e, "couple^@^field^@^using^@^@^@~{", caps) < 0) {
  dy_invalid(c, "Invalid couple block: ", p, s, e);
  return i;
}
  int32_t t7 = (g[0]).ncp;
  (g[0]).cp_sys[t7] = dy_name(c, p, caps[0], caps[1]);
  (g[0]).cp_field[t7] = dy_name(c, p, caps[2], caps[3]);
  (g[0]).cp_rep[t7] = dy_name(c, p, caps[4], caps[5]);
  (g[0]).cp_k1[t7] = dy_name(c, p, caps[6], caps[7]);
  (g[0]).cp_k2[t7] = dy_name(c, p, caps[8], caps[9]);
  (g[0]).cp_guid[t7] = dy_name_lit(c, "guide");
  int32_t nx7 = dy_block(p, ls, le, nl, i, bs, be, nb);
  int32_t b7 = (c[0]).nbd;
  int32_t j7 = 0;
  while (j7 < nb[0]) {
  bl[0] = bs[j7];
  bl[1] = be[j7];
  dy_strip_comments(p, bl);
  if (dy_arrow(p, bl[0], bl[1], l, r) == 1) {
  if (dy_eq(p, l[0], l[1], "guidance") == 1) {
  (g[0]).cp_guid[t7] = dy_name(c, p, r[0], r[1]);
} else {
  dy_bd(c, (0 - 1), dy_name(c, p, r[0], r[1]), dy_name(c, p, l[0], l[1]));
}
}
  j7 = (j7 + 1);
}
  (g[0]).cp_b0[t7] = b7;
  (g[0]).cp_bn[t7] = ((c[0]).nbd - b7);
  (g[0]).ncp = (t7 + 1);
  return nx7;
}
  if (dy_starts(p, s, e, "guide ") == 1) {
  if (dy_match(p, s, e, "guide^@^with^@^@^through^@^using^@^over^@~{", caps) < 0) {
  dy_invalid(c, "Invalid guide block: ", p, s, e);
  return i;
}
  int32_t t8 = (g[0]).ngd;
  (g[0]).gd_sys[t8] = dy_name(c, p, caps[0], caps[1]);
  (g[0]).gd_k1[t8] = dy_name(c, p, caps[2], caps[3]);
  (g[0]).gd_k2[t8] = dy_name(c, p, caps[4], caps[5]);
  (g[0]).gd_field[t8] = dy_name(c, p, caps[6], caps[7]);
  (g[0]).gd_guid[t8] = dy_name(c, p, caps[8], caps[9]);
  (g[0]).gd_hz[t8] = dy_name(c, p, caps[10], caps[11]);
  int32_t nx8 = dy_block(p, ls, le, nl, i, bs, be, nb);
  int32_t b8 = (c[0]).nbd;
  int32_t j8 = 0;
  while (j8 < nb[0]) {
  bl[0] = bs[j8];
  bl[1] = be[j8];
  dy_strip_comments(p, bl);
  if (dy_arrow(p, bl[0], bl[1], l, r) == 1) {
  dy_bd(c, (0 - 1), dy_name(c, p, r[0], r[1]), dy_name(c, p, l[0], l[1]));
}
  j8 = (j8 + 1);
}
  (g[0]).gd_b0[t8] = b8;
  (g[0]).gd_bn[t8] = ((c[0]).nbd - b8);
  (g[0]).ngd = (t8 + 1);
  return nx8;
}
  kept[0] = 1;
  return i;
}

void dy_ln(DySb* b, const char* s) {
  dy_puts(b, s);
}

void dy_eol(DySb* b) {
  dy_putc(b, 10);
}

void dy_key_error(DyC* c, int32_t off) {
  DySb* m = (DySb*)(dy_err(c));
  uint8_t* np = (uint8_t*)((((c[0]).nm[0]).p + off));
  dy_repr_str(m, np, 0, (int32_t)(strlen((const char*)(np))));
}

int64_t dy_steps_or(DyC* c, Dp* g, int32_t name, int64_t dflt) {
  if (name < 0) {
  return dflt;
}
  int32_t h = dy_find_hz(c, g, name);
  if (h >= 0 && (g[0]).hz_kind[h] == 0) {
  return (g[0]).hz_steps[h];
}
  return dflt;
}

int32_t dy_bufs(DySb* b, int32_t* bi, int32_t count) {
  int32_t first = bi[0];
  int32_t k = 0;
  while (k < count) {
  dy_puts(b, "    let __dsys_b");
  dy_i64(b, (int64_t)(bi[0]));
  dy_puts(b, ": array<f64, 4> = [0.0, 0.0, 0.0, 0.0]\n");
  bi[0] = (bi[0] + 1);
  k = (k + 1);
}
  return first;
}

void dy_bufref(DySb* b, int32_t k) {
  dy_puts(b, "__dsys_b");
  dy_i64(b, (int64_t)(k));
}

void dy_bufargs(DySb* b, int32_t first, int32_t count) {
  int32_t k = 0;
  while (k < count) {
  dy_puts(b, ", ");
  dy_bufref(b, (first + k));
  k = (k + 1);
}
}

void dy_flat_array(DySb* b, DyC* c, int32_t f0, int32_t fnn) {
  dy_puts(b, ": array<f64, ");
  if (fnn > 1) {
  dy_i64(b, (int64_t)(fnn));
} else {
  dy_puts(b, "1");
}
  dy_puts(b, "> = [");
  int32_t k = 0;
  while (k < fnn) {
  if (k > 0) {
  dy_puts(b, ", ");
}
  dy_flow_f64(b, (c[0]).fp[(f0 + k)]);
  k = (k + 1);
}
  dy_puts(b, "]");
}

void dy_rep_array(DySb* b, int64_t n, const char* item) {
  int64_t m = n;
  if (m < 1) {
  m = 1;
}
  dy_putc(b, 91);
  int64_t k = 0;
  while (k < m) {
  if (k > 0) {
  dy_puts(b, ", ");
}
  dy_puts(b, item);
  k = (k + 1);
}
  dy_putc(b, 93);
}

void dy_matrix(DySb* b, DyC* c, int32_t name, const char* which, int64_t rows, int64_t cols) {
  dy_puts(b, "Matrix { data: __dsys_");
  dy_pn(b, c, name);
  dy_puts(b, which);
  dy_puts(b, ", rows: ");
  dy_i64(b, rows);
  dy_puts(b, ", cols: ");
  dy_i64(b, cols);
  dy_puts(b, " }");
}

void dy_ga_arrays(DySb* b, DySb* tag, int64_t pop) {
  dy_puts(b, "    let ");
  dy_span(b, (tag[0]).p, 0, (tag[0]).len);
  dy_puts(b, "_k1: array<f64, ");
  dy_i64(b, pop);
  dy_puts(b, "> = ");
  dy_rep_array(b, pop, "0.0");
  dy_eol(b);
  dy_puts(b, "    let ");
  dy_span(b, (tag[0]).p, 0, (tag[0]).len);
  dy_puts(b, "_k2: array<f64, ");
  dy_i64(b, pop);
  dy_puts(b, "> = ");
  dy_rep_array(b, pop, "0.0");
  dy_eol(b);
  dy_puts(b, "    let ");
  dy_span(b, (tag[0]).p, 0, (tag[0]).len);
  dy_puts(b, "_fit: array<f64, ");
  dy_i64(b, pop);
  dy_puts(b, "> = ");
  dy_rep_array(b, pop, "0.0");
  dy_eol(b);
  dy_puts(b, "    let ");
  dy_span(b, (tag[0]).p, 0, (tag[0]).len);
  dy_puts(b, "_bk1: array<f64, 1> = [0.0]\n");
  dy_puts(b, "    let ");
  dy_span(b, (tag[0]).p, 0, (tag[0]).len);
  dy_puts(b, "_bk2: array<f64, 1> = [0.0]\n");
  dy_puts(b, "    let ");
  dy_span(b, (tag[0]).p, 0, (tag[0]).len);
  dy_puts(b, "_hist: array<f64, 32> = ");
  dy_rep_array(b, 32, "0.0");
  dy_eol(b);
}

void dy_tag(DySb* t, const char* pre, int32_t k) {
  (t[0]).len = 0;
  dy_puts(t, pre);
  dy_i64(t, (int64_t)(k));
}

void dy_tagp(DySb* b, DySb* t) {
  dy_span(b, (t[0]).p, 0, (t[0]).len);
}

int32_t dy_is_identifier(DyC* c, int32_t off) {
  uint8_t* np = (uint8_t*)((((c[0]).nm[0]).p + off));
  if (np[0] == 0) {
  return 0;
}
  if (dy_digit(np[0]) == 1) {
  return 0;
}
  return 1;
}

int32_t dy_compile(DyC* c, Dp* g, DySb* b) {
  if ((g[0]).nsy == 0 && (g[0]).nwf == 0 && (g[0]).nse == 0 && (g[0]).nga == 0 && (g[0]).ncl == 0 && (g[0]).nanz == 0 && (g[0]).nlq == 0 && (g[0]).ncp == 0 && (g[0]).ngd == 0) {
  return 0;
}
  int32_t* bi = (int32_t*)(dy_i32s(1));
  bi[0] = 0;
  DySb* tag = (DySb*)(dy_sb_new(32));
  dy_puts(b, "    # --- dsys DSL expansion (auto-generated) ---\n");
  int32_t i = 0;
  while (i < (g[0]).nhz) {
  dy_puts(b, "    let h_");
  dy_pn(b, c, (g[0]).hz_name[i]);
  if ((g[0]).hz_kind[i] == 0) {
  dy_puts(b, ": Horizon = horizon_finite(");
  dy_i64(b, (g[0]).hz_steps[i]);
} else {
  dy_puts(b, ": Horizon = horizon_infinite(");
  dy_g17(b, (g[0]).hz_gamma[i]);
}
  dy_puts(b, ")\n");
  i = (i + 1);
}
  i = 0;
  while (i < (g[0]).nsy) {
  int32_t nm = (g[0]).sy_name[i];
  int64_t n = (g[0]).sy_n[i];
  int64_t mm = (g[0]).sy_m[i];
  int64_t pp = (g[0]).sy_p[i];
  dy_puts(b, "    let __dsys_");
  dy_pn(b, c, nm);
  dy_puts(b, "_A");
  dy_flat_array(b, c, (g[0]).sy_a0[i], (g[0]).sy_an[i]);
  dy_eol(b);
  dy_puts(b, "    let __dsys_");
  dy_pn(b, c, nm);
  dy_puts(b, "_B");
  dy_flat_array(b, c, (g[0]).sy_b0[i], (g[0]).sy_bn[i]);
  dy_eol(b);
  dy_puts(b, "    let __dsys_");
  dy_pn(b, c, nm);
  dy_puts(b, "_C");
  dy_flat_array(b, c, (g[0]).sy_c0[i], (g[0]).sy_cn[i]);
  dy_eol(b);
  dy_puts(b, "    let __dsys_");
  dy_pn(b, c, nm);
  if ((g[0]).sy_mode[i] == 1) {
  dy_puts(b, "_cont: DynamicalSystem = dsys_continuous(");
} else {
  dy_puts(b, ": DynamicalSystem = dsys_discrete(");
}
  dy_i64(b, n);
  dy_puts(b, ", ");
  dy_i64(b, mm);
  dy_puts(b, ", ");
  dy_i64(b, pp);
  dy_puts(b, ", ");
  dy_g17(b, (g[0]).sy_dt[i]);
  dy_puts(b, ", ");
  dy_matrix(b, c, nm, "_A", n, n);
  dy_puts(b, ", ");
  dy_matrix(b, c, nm, "_B", n, mm);
  dy_puts(b, ", ");
  dy_matrix(b, c, nm, "_C", pp, n);
  dy_puts(b, ")\n");
  if ((g[0]).sy_mode[i] == 1) {
  int32_t f = dy_bufs(b, bi, 5);
  dy_puts(b, "    let __dsys_");
  dy_pn(b, c, nm);
  dy_puts(b, ": DynamicalSystem = dsys_euler_discretize(__dsys_");
  dy_pn(b, c, nm);
  dy_puts(b, "_cont");
  dy_bufargs(b, f, 4);
  dy_puts(b, ")\n");
}
  if (dy_is_identifier(c, nm) == 1) {
  dy_puts(b, "    let ");
  dy_pn(b, c, nm);
  dy_puts(b, ": DynamicalSystem = __dsys_");
  dy_pn(b, c, nm);
  dy_eol(b);
}
  i = (i + 1);
}
  i = 0;
  while (i < (g[0]).nwf) {
  int32_t wn = (g[0]).wf_name[i];
  int64_t cells = ((g[0]).wf_w[i] * (g[0]).wf_h[i]);
  int64_t opts = (cells * (g[0]).wf_tiles[i]);
  dy_puts(b, "    let __wfc_");
  dy_pn(b, c, wn);
  dy_puts(b, "_cells: array<i32, ");
  dy_i64(b, cells);
  dy_puts(b, "> = ");
  dy_rep_array(b, cells, "-1");
  dy_eol(b);
  dy_puts(b, "    let __wfc_");
  dy_pn(b, c, wn);
  dy_puts(b, "_opts: array<i32, ");
  dy_i64(b, opts);
  dy_puts(b, "> = ");
  dy_rep_array(b, opts, "1");
  dy_eol(b);
  dy_puts(b, "    for __wfc_i in 0 to ");
  dy_i64(b, cells);
  dy_puts(b, " {\n        __wfc_");
  dy_pn(b, c, wn);
  dy_puts(b, "_cells[__wfc_i] = -1\n    }\n");
  dy_puts(b, "    for __wfc_j in 0 to ");
  dy_i64(b, opts);
  dy_puts(b, " {\n        __wfc_");
  dy_pn(b, c, wn);
  dy_puts(b, "_opts[__wfc_j] = 1\n    }\n");
  dy_puts(b, "    __wfc_");
  dy_pn(b, c, wn);
  dy_puts(b, "_cells[");
  dy_i64(b, (g[0]).wf_pc[i]);
  dy_puts(b, "] = ");
  dy_i64(b, (g[0]).wf_pt[i]);
  dy_eol(b);
  dy_puts(b, "    let __wfc_");
  dy_pn(b, c, wn);
  dy_puts(b, ": WFCGrid = WFCGrid { width: ");
  dy_i64(b, (g[0]).wf_w[i]);
  dy_puts(b, ", height: ");
  dy_i64(b, (g[0]).wf_h[i]);
  dy_puts(b, ", cells: __wfc_");
  dy_pn(b, c, wn);
  dy_puts(b, "_cells, options: __wfc_");
  dy_pn(b, c, wn);
  dy_puts(b, "_opts }\n");
  i = (i + 1);
}
  i = 0;
  while (i < (g[0]).nse) {
  int32_t sys = (g[0]).se_sys[i];
  if (dy_find_sys(c, g, sys) < 0) {
  dy_key_error(c, sys);
  return 0;
}
  int32_t q = 0;
  while (q < (g[0]).se_bn[i]) {
  int32_t bdx = ((g[0]).se_b0[i] + q);
  int32_t kind = (c[0]).bd_kind[bdx];
  int32_t var = (c[0]).bd_var[bdx];
  if (kind == 1) {
  int32_t f = dy_bufs(b, bi, 5);
  dy_puts(b, "    let mut ");
  dy_pn(b, c, var);
  dy_puts(b, ": i32 = 0\n    ");
  dy_pn(b, c, var);
  dy_puts(b, " = is_controllable(__dsys_");
  dy_pn(b, c, sys);
  dy_bufargs(b, f, 5);
  dy_puts(b, ")\n");
}
  if (kind == 2) {
  dy_puts(b, "    let mut ");
  dy_pn(b, c, var);
  dy_puts(b, ": f64 = 0.0\n    ");
  dy_pn(b, c, var);
  dy_puts(b, " = matrix_spectral_radius_2x2(__dsys_");
  dy_pn(b, c, sys);
  dy_puts(b, ".A)\n");
}
  if (kind == 3 || kind == 4) {
  int32_t f2 = dy_bufs(b, bi, 4);
  dy_puts(b, "    let mut ");
  dy_pn(b, c, var);
  dy_puts(b, ": f64 = 0.0\n    let __W_");
  dy_pn(b, c, var);
  if (kind == 3) {
  dy_puts(b, ": Matrix = gramian_finite_horizon(__dsys_");
} else {
  dy_puts(b, ": Matrix = gramian_infinite_horizon(__dsys_");
}
  dy_pn(b, c, sys);
  dy_puts(b, ", h_");
  dy_pn(b, c, (c[0]).bd_hz[bdx]);
  dy_bufargs(b, f2, 4);
  dy_puts(b, ")\n    ");
  dy_pn(b, c, var);
  dy_puts(b, " = matrix_trace(__W_");
  dy_pn(b, c, var);
  dy_puts(b, ")\n");
}
  q = (q + 1);
}
  i = (i + 1);
}
  int32_t* dg = (int32_t*)(dy_i32s((((4 * (g[0]).nga) + (4 * (g[0]).nanz)) + 4)));
  int32_t ndg = 0;
  i = 0;
  while (i < (g[0]).nga) {
  int32_t sys2 = (g[0]).ga_sys[i];
  if (dy_find_sys(c, g, sys2) < 0) {
  dy_key_error(c, sys2);
  return 0;
}
  int64_t steps = dy_steps_or(c, g, (g[0]).ga_hz[i], 50);
  int64_t pop = (g[0]).ga_pop[i];
  dy_tag(tag, "__ga_e", i);
  dy_puts(b, "    let mut ");
  dy_pn(b, c, (g[0]).ga_k1[i]);
  dy_puts(b, ": f64 = 0.0\n    let mut ");
  dy_pn(b, c, (g[0]).ga_k2[i]);
  dy_puts(b, ": f64 = 0.0\n");
  dg[ndg] = (g[0]).ga_k1[i];
  dg[(ndg + 1)] = (g[0]).ga_k2[i];
  ndg = (ndg + 2);
  dy_ga_arrays(b, tag, pop);
  dy_puts(b, "    let ");
  dy_tagp(b, tag);
  dy_puts(b, "_cfg: GAConfig = GAConfig { population: ");
  dy_i64(b, pop);
  dy_puts(b, ", generations: ");
  dy_i64(b, (g[0]).ga_gen[i]);
  dy_puts(b, ", horizon: ");
  dy_i64(b, steps);
  dy_puts(b, ", mutation: ");
  dy_g17(b, (g[0]).ga_mut[i]);
  dy_puts(b, " }\n    ga_evolve_traced(__dsys_");
  dy_pn(b, c, sys2);
  dy_puts(b, ", ");
  dy_i64(b, steps);
  dy_puts(b, ", ");
  dy_tagp(b, tag);
  dy_puts(b, "_cfg, ");
  dy_tagp(b, tag);
  dy_puts(b, "_k1, ");
  dy_tagp(b, tag);
  dy_puts(b, "_k2, ");
  dy_tagp(b, tag);
  dy_puts(b, "_fit, ");
  dy_tagp(b, tag);
  dy_puts(b, "_bk1, ");
  dy_tagp(b, tag);
  dy_puts(b, "_bk2, ");
  dy_tagp(b, tag);
  dy_puts(b, "_hist)\n    ");
  dy_pn(b, c, (g[0]).ga_k1[i]);
  dy_puts(b, " = ");
  dy_tagp(b, tag);
  dy_puts(b, "_bk1[0]\n    ");
  dy_pn(b, c, (g[0]).ga_k2[i]);
  dy_puts(b, " = ");
  dy_tagp(b, tag);
  dy_puts(b, "_bk2[0]\n");
  i = (i + 1);
}
  i = 0;
  while (i < (g[0]).ncl) {
  int32_t sys3 = (g[0]).cl_sys[i];
  if (dy_find_sys(c, g, sys3) < 0) {
  dy_key_error(c, sys3);
  return 0;
}
  int32_t f3 = dy_bufs(b, bi, 2);
  dy_puts(b, "    let __cl_");
  dy_pn(b, c, sys3);
  dy_puts(b, ": DynamicalSystem = ga_closed_loop_matrix(__dsys_");
  dy_pn(b, c, sys3);
  dy_puts(b, ", ");
  dy_pn(b, c, (g[0]).cl_k1[i]);
  dy_puts(b, ", ");
  dy_pn(b, c, (g[0]).cl_k2[i]);
  dy_bufargs(b, f3, 2);
  dy_puts(b, ")\n");
  int32_t q3 = 0;
  while (q3 < (g[0]).cl_bn[i]) {
  int32_t bdx3 = ((g[0]).cl_b0[i] + q3);
  int32_t kind3 = (c[0]).bd_kind[bdx3];
  int32_t var3 = (c[0]).bd_var[bdx3];
  if (kind3 == 5) {
  dy_puts(b, "    let mut ");
  dy_pn(b, c, var3);
  dy_puts(b, ": f64 = matrix_spectral_radius_2x2(__cl_");
  dy_pn(b, c, sys3);
  dy_puts(b, ".A)\n");
}
  if (kind3 == 6) {
  dy_puts(b, "    let mut ");
  dy_pn(b, c, var3);
  dy_puts(b, ": i32 = 0\n    if matrix_spectral_radius_2x2(__cl_");
  dy_pn(b, c, sys3);
  dy_puts(b, ".A) < 1.0 { ");
  dy_pn(b, c, var3);
  dy_puts(b, " = 1 }\n");
}
  if (kind3 == 7) {
  int64_t st3 = dy_steps_or(c, g, (c[0]).bd_hz[bdx3], 50);
  dy_puts(b, "    let mut ");
  dy_pn(b, c, var3);
  dy_puts(b, ": f64 = ga_closed_loop_energy(__cl_");
  dy_pn(b, c, sys3);
  dy_puts(b, ", ");
  dy_i64(b, st3);
  dy_puts(b, ")\n");
}
  q3 = (q3 + 1);
}
  i = (i + 1);
}
  i = 0;
  while (i < (g[0]).nanz) {
  int32_t sys4 = (g[0]).an_sys[i];
  if (dy_find_sys(c, g, sys4) < 0) {
  dy_key_error(c, sys4);
  return 0;
}
  int64_t steps4 = dy_steps_or(c, g, (g[0]).an_hz[i], 50);
  int32_t linked = (0 - 1);
  int32_t gk = 0;
  while (gk < (g[0]).nga) {
  if (dy_neq(c, (g[0]).ga_sys[gk], sys4) == 1 && dy_neq(c, (g[0]).ga_hz[gk], (g[0]).an_hz[i]) == 1) {
  linked = gk;
}
  gk = (gk + 1);
}
  int64_t pop4 = 12;
  int64_t gens4 = 30;
  double mut4 = 0.3;
  if (linked >= 0) {
  pop4 = (g[0]).ga_pop[linked];
  gens4 = (g[0]).ga_gen[linked];
  mut4 = (g[0]).ga_mut[linked];
}
  dy_tag(tag, "__ga_a", i);
  int32_t rep = (g[0]).an_rep[i];
  dy_puts(b, "    let mut ");
  dy_pn(b, c, rep);
  dy_puts(b, ": GAAnalysisReport = GAAnalysisReport {\n");
  dy_puts(b, "        plant_controllable: 0, plant_spectral_radius: 0.0,\n");
  dy_puts(b, "        closed_spectral_radius: 0.0, gramian_open_finite: 0.0,\n");
  dy_puts(b, "        gramian_open_infinite: 0.0, closed_loop_energy: 0.0,\n");
  dy_puts(b, "        baseline_cost: 0.0, evolved_cost: 0.0, fitness_drop: 0.0,\n");
  dy_puts(b, "        convergence_gen: 0, stable_closed_loop: 0\n");
  dy_puts(b, "    }\n");
  dy_ga_arrays(b, tag, pop4);
  int32_t f4 = dy_bufs(b, bi, 12);
  dy_puts(b, "    let ");
  dy_tagp(b, tag);
  dy_puts(b, "_cfg: GAConfig = GAConfig { population: ");
  dy_i64(b, pop4);
  dy_puts(b, ", generations: ");
  dy_i64(b, gens4);
  dy_puts(b, ", horizon: ");
  dy_i64(b, steps4);
  dy_puts(b, ", mutation: ");
  dy_g17(b, mut4);
  dy_puts(b, " }\n    ");
  dy_pn(b, c, rep);
  dy_puts(b, " = ga_analyze_control_search(__dsys_");
  dy_pn(b, c, sys4);
  dy_puts(b, ", ");
  dy_i64(b, steps4);
  dy_puts(b, ", ");
  dy_tagp(b, tag);
  dy_puts(b, "_cfg, ");
  dy_tagp(b, tag);
  dy_puts(b, "_k1, ");
  dy_tagp(b, tag);
  dy_puts(b, "_k2, ");
  dy_tagp(b, tag);
  dy_puts(b, "_fit, ");
  dy_tagp(b, tag);
  dy_puts(b, "_bk1, ");
  dy_tagp(b, tag);
  dy_puts(b, "_bk2, ");
  dy_tagp(b, tag);
  dy_puts(b, "_hist");
  dy_bufargs(b, f4, 12);
  dy_puts(b, ")\n");
  int32_t kk = 0;
  while (kk < 2) {
  int32_t kv = (g[0]).an_k1[i];
  if (kk == 1) {
  kv = (g[0]).an_k2[i];
}
  int32_t seen = 0;
  int32_t d = 0;
  while (d < ndg) {
  if (dy_neq(c, dg[d], kv) == 1) {
  seen = 1;
}
  d = (d + 1);
}
  if (seen == 0) {
  dy_puts(b, "    let mut ");
  dy_pn(b, c, kv);
  dy_puts(b, ": f64 = 0.0\n");
  dg[ndg] = kv;
  ndg = (ndg + 1);
}
  kk = (kk + 1);
}
  dy_puts(b, "    ");
  dy_pn(b, c, (g[0]).an_k1[i]);
  dy_puts(b, " = ");
  dy_tagp(b, tag);
  dy_puts(b, "_bk1[0]\n    ");
  dy_pn(b, c, (g[0]).an_k2[i]);
  dy_puts(b, " = ");
  dy_tagp(b, tag);
  dy_puts(b, "_bk2[0]\n");
  i = (i + 1);
}
  i = 0;
  while (i < (g[0]).nlq) {
  int32_t sys5 = (g[0]).lq_sys[i];
  int32_t si = dy_find_sys(c, g, sys5);
  if (si < 0) {
  DySb* m = (DySb*)(dy_err(c));
  dy_lqr_prefix(m, c, sys5);
  dy_puts(m, "unknown dsys '");
  dy_pn(m, c, sys5);
  dy_puts(m, "'");
  return 0;
}
  int64_t n5 = (g[0]).sy_n[si];
  if ((g[0]).sy_m[si] != 1) {
  DySb* m2 = (DySb*)(dy_err(c));
  dy_lqr_prefix(m2, c, sys5);
  dy_puts(m2, "Stage-1 needs scalar input (m=1), got m=");
  dy_i64(m2, (g[0]).sy_m[si]);
  return 0;
}
  if ((int64_t)((g[0]).lq_qn[i]) != n5) {
  DySb* m3 = (DySb*)(dy_err(c));
  dy_lqr_prefix(m3, c, sys5);
  dy_puts(m3, "Q length ");
  dy_i64(m3, (int64_t)((g[0]).lq_qn[i]));
  dy_puts(m3, " != n=");
  dy_i64(m3, n5);
  return 0;
}
  if (n5 > 8) {
  DySb* m4 = (DySb*)(dy_err(c));
  dy_lqr_prefix(m4, c, sys5);
  dy_puts(m4, "n=");
  dy_i64(m4, n5);
  dy_puts(m4, " exceeds LQR_MAX_N=8");
  return 0;
}
  dy_tag(tag, "__lqr_", i);
  dy_puts(b, "    let ");
  dy_tagp(b, tag);
  dy_puts(b, "_q");
  dy_flat_array(b, c, (g[0]).lq_q0[i], (g[0]).lq_qn[i]);
  dy_puts(b, "\n    let mut ");
  dy_tagp(b, tag);
  dy_puts(b, "_k: array<f64, ");
  dy_i64(b, n5);
  dy_puts(b, "> = ");
  dy_rep_array(b, n5, "0.0");
  dy_puts(b, "\n    let ");
  dy_tagp(b, tag);
  dy_puts(b, "_iters: i32 = dlqr_diag_q_scalar_u(__dsys_");
  dy_pn(b, c, sys5);
  dy_puts(b, ".A.data, __dsys_");
  dy_pn(b, c, sys5);
  dy_puts(b, ".B.data, ");
  dy_tagp(b, tag);
  dy_puts(b, "_q, ");
  dy_flow_f64(b, (g[0]).lq_r[i]);
  dy_puts(b, ", ");
  dy_i64(b, n5);
  dy_puts(b, ", ");
  dy_tagp(b, tag);
  dy_puts(b, "_k, ");
  dy_i64(b, (g[0]).lq_it[i]);
  dy_puts(b, ")\n");
  int32_t gi = 0;
  while (gi < (g[0]).lq_gn[i]) {
  dy_puts(b, "    let ");
  dy_pn(b, c, (c[0]).gl[((g[0]).lq_g0[i] + gi)]);
  dy_puts(b, ": f64 = ");
  dy_tagp(b, tag);
  dy_puts(b, "_k[");
  dy_i64(b, (int64_t)(gi));
  dy_puts(b, "]\n");
  gi = (gi + 1);
}
  i = (i + 1);
}
  i = 0;
  while (i < (g[0]).ncp) {
  int32_t fld = (g[0]).cp_field[i];
  int32_t wi = dy_find_wf(c, g, fld);
  if (wi < 0) {
  dy_key_error(c, fld);
  return 0;
}
  int32_t guid = (g[0]).cp_guid[i];
  dy_puts(b, "    let ");
  dy_pn(b, c, guid);
  dy_puts(b, ": CoupledGuidance = couple_ga_wfc_guidance(");
  dy_pn(b, c, (g[0]).cp_rep[i]);
  dy_puts(b, ", ");
  dy_pn(b, c, (g[0]).cp_k1[i]);
  dy_puts(b, ", ");
  dy_pn(b, c, (g[0]).cp_k2[i]);
  dy_puts(b, ", ");
  dy_i64(b, (g[0]).wf_seed[wi]);
  dy_puts(b, ", ");
  dy_i64(b, (g[0]).wf_steps[wi]);
  dy_puts(b, ")\n    let __wfc_rep_");
  dy_pn(b, c, fld);
  dy_puts(b, ": WFCRunReport = wfc_run_guided(__wfc_");
  dy_pn(b, c, fld);
  dy_puts(b, ", ");
  dy_i64(b, (g[0]).wf_tiles[wi]);
  dy_puts(b, ", ");
  dy_pn(b, c, guid);
  dy_puts(b, ")\n");
  int32_t q6 = 0;
  while (q6 < (g[0]).cp_bn[i]) {
  int32_t bdx6 = ((g[0]).cp_b0[i] + q6);
  int32_t lhs = (c[0]).bd_hz[bdx6];
  int32_t var6 = (c[0]).bd_var[bdx6];
  if (dy_neq_lit(c, lhs, "collapsed") == 1) {
  dy_puts(b, "    let mut ");
  dy_pn(b, c, var6);
  dy_puts(b, ": i32 = __wfc_rep_");
  dy_pn(b, c, fld);
  dy_puts(b, ".collapsed\n");
}
  if (dy_neq_lit(c, lhs, "wall_fraction") == 1) {
  dy_puts(b, "    let mut ");
  dy_pn(b, c, var6);
  dy_puts(b, ": f64 = __wfc_rep_");
  dy_pn(b, c, fld);
  dy_puts(b, ".wall_fraction\n");
}
  if (dy_neq_lit(c, lhs, "entropy") == 1) {
  dy_puts(b, "    let mut ");
  dy_pn(b, c, var6);
  dy_puts(b, ": f64 = __wfc_rep_");
  dy_pn(b, c, fld);
  dy_puts(b, ".mean_entropy\n");
}
  q6 = (q6 + 1);
}
  i = (i + 1);
}
  i = 0;
  while (i < (g[0]).ngd) {
  int32_t sys7 = (g[0]).gd_sys[i];
  if (dy_find_sys(c, g, sys7) < 0) {
  dy_key_error(c, sys7);
  return 0;
}
  int64_t steps7 = dy_steps_or(c, g, (g[0]).gd_hz[i], 20);
  int32_t fld7 = (g[0]).gd_field[i];
  int32_t f7 = dy_bufs(b, bi, 3);
  dy_tag(tag, "__guide_ev_", i);
  dy_puts(b, "    let ");
  dy_tagp(b, tag);
  dy_puts(b, ": GuidedEvolutionReport = guide_state_evolution(__dsys_");
  dy_pn(b, c, sys7);
  dy_puts(b, ", ");
  dy_pn(b, c, (g[0]).gd_k1[i]);
  dy_puts(b, ", ");
  dy_pn(b, c, (g[0]).gd_k2[i]);
  dy_puts(b, ", ");
  dy_pn(b, c, (g[0]).gd_guid[i]);
  dy_puts(b, ", __wfc_rep_");
  dy_pn(b, c, fld7);
  dy_puts(b, ", ");
  dy_i64(b, steps7);
  dy_bufargs(b, f7, 3);
  dy_puts(b, ")\n");
  int32_t q7 = 0;
  while (q7 < (g[0]).gd_bn[i]) {
  int32_t bdx7 = ((g[0]).gd_b0[i] + q7);
  int32_t lhs7 = (c[0]).bd_hz[bdx7];
  int32_t var7 = (c[0]).bd_var[bdx7];
  const char* field = "";
  const char* ty = "";
  if (dy_neq_lit(c, lhs7, "input_scale") == 1) {
  field = ".input_scale";
  ty = ": f64 = ";
}
  if (dy_neq_lit(c, lhs7, "energy") == 1) {
  field = ".layout_energy";
  ty = ": f64 = ";
}
  if (dy_neq_lit(c, lhs7, "spectral") == 1) {
  field = ".guided_spectral_radius";
  ty = ": f64 = ";
}
  if (dy_neq_lit(c, lhs7, "stable") == 1) {
  field = ".stable_guided";
  ty = ": i32 = ";
}
  if (dy_neq_lit(c, lhs7, "collapsed") == 1) {
  field = ".collapsed_cells";
  ty = ": i32 = ";
}
  if (strlen(field) > 0) {
  dy_puts(b, "    let mut ");
  dy_pn(b, c, var7);
  dy_puts(b, ty);
  dy_tagp(b, tag);
  dy_puts(b, field);
  dy_eol(b);
}
  if (dy_neq_lit(c, lhs7, "wall_fraction") == 1) {
  dy_puts(b, "    let mut ");
  dy_pn(b, c, var7);
  dy_puts(b, ": f64 = __wfc_rep_");
  dy_pn(b, c, fld7);
  dy_puts(b, ".wall_fraction\n");
}
  q7 = (q7 + 1);
}
  i = (i + 1);
}
  dy_puts(b, "    # --- end dsys DSL expansion ---");
  return 1;
}

void dy_compile_portraits(DyC* c, Dp* g, DySb* b) {
  int32_t i = 0;
  while (i < (g[0]).npt) {
  if (i > 0) {
  dy_eol(b);
}
  int32_t fl = (g[0]).pt_flow[i];
  int32_t ax0 = (g[0]).pt_ax0[i];
  int32_t ax1 = (g[0]).pt_ax1[i];
  double a0lo = (g[0]).pt_lo0[i];
  double a0hi = (g[0]).pt_hi0[i];
  if ((g[0]).pt_k0[i] == 2) {
  a0lo = (g[0]).pt_hi0[i];
  a0hi = (g[0]).pt_lo0[i];
}
  double a1lo = (g[0]).pt_lo1[i];
  double a1hi = (g[0]).pt_hi1[i];
  if ((g[0]).pt_k1[i] == 2) {
  a1lo = (g[0]).pt_hi1[i];
  a1hi = (g[0]).pt_lo1[i];
}
  int64_t tr = (g[0]).pt_trail[i];
  int64_t w = (g[0]).pt_w[i];
  int64_t h = (g[0]).pt_h[i];
  dy_puts(b, "# generated from represent phase_portrait for ");
  dy_pn(b, c, fl);
  dy_puts(b, "\nconst ");
  dy_pn(b, c, fl);
  dy_puts(b, "_portrait_trail: i32 = ");
  dy_i64(b, tr);
  dy_puts(b, "\nconst ");
  dy_pn(b, c, fl);
  dy_puts(b, "_portrait_win_w: i32 = ");
  dy_i64(b, w);
  dy_puts(b, "\nconst ");
  dy_pn(b, c, fl);
  dy_puts(b, "_portrait_win_h: i32 = ");
  dy_i64(b, h);
  dy_puts(b, "\n\nfunction ");
  dy_pn(b, c, fl);
  dy_puts(b, "_portrait_frame(\n    g: Gfx,\n    xs: ptr<f64>,\n    zs: ptr<f64>,\n    head: ptr<i32>,\n    count: ptr<i32>,\n    ");
  dy_pn(b, c, ax0);
  dy_puts(b, ": f64,\n    ");
  dy_pn(b, c, ax1);
  dy_puts(b, ": f64\n) -> void {\n    trail_push_2d(xs, zs, ");
  dy_i64(b, tr);
  dy_puts(b, ", head, count, ");
  dy_pn(b, c, ax0);
  dy_puts(b, ", ");
  dy_pn(b, c, ax1);
  dy_puts(b, ")\n    let h: i32 = head[0]\n    let c: i32 = count[0]\n    gfx_clear(g, 8, 8, 16)\n    for i in 0 to c {\n        let idx: i32 = trail_index(h, c, ");
  dy_i64(b, tr);
  dy_puts(b, ", i)\n        let px: i32 = project_axis(xs[idx], ");
  dy_repr(b, a0lo);
  dy_puts(b, ", ");
  dy_repr(b, a0hi);
  dy_puts(b, ", ");
  dy_i64(b, w);
  dy_puts(b, ", 10)\n        let py: i32 = project_axis(zs[idx], ");
  dy_repr(b, a1lo);
  dy_puts(b, ", ");
  dy_repr(b, a1hi);
  dy_puts(b, ", ");
  dy_i64(b, h);
  dy_puts(b, ", 30)\n        let b: i32 = 25 + (230 * (i + 1)) / c\n        let mut size: i32 = 2\n        if i >= c - 12 { size = 3 }\n        gfx_fill_rect(g, px, py, size, size, b, (b * 3) / 5, 30)\n    }\n    let hx: i32 = project_axis(");
  dy_pn(b, c, ax0);
  dy_puts(b, ", ");
  dy_repr(b, a0lo);
  dy_puts(b, ", ");
  dy_repr(b, a0hi);
  dy_puts(b, ", ");
  dy_i64(b, w);
  dy_puts(b, ", 10)\n    let hz: i32 = project_axis(");
  dy_pn(b, c, ax1);
  dy_puts(b, ", ");
  dy_repr(b, a1lo);
  dy_puts(b, ", ");
  dy_repr(b, a1hi);
  dy_puts(b, ", ");
  dy_i64(b, h);
  dy_puts(b, ", 30)\n    gfx_fill_rect(g, hx - 1, hz - 1, 5, 5, 255, 240, 180)\n}\n");
  i = (i + 1);
}
}

int32_t dy_head_ns(uint8_t* p, int32_t k, int32_t n, int32_t* caps) {
  if (dy_match(p, k, n, "dsys^@", caps) >= 0) {
  return 1;
}
  if (dy_match(p, k, n, "horizon^@", caps) >= 0) {
  return 1;
}
  if (dy_match(p, k, n, "sense^on^", caps) >= 0) {
  return 1;
}
  if (dy_match(p, k, n, "ga^evolve^", caps) >= 0) {
  return 1;
}
  if (dy_match(p, k, n, "closed^@", caps) >= 0) {
  return 1;
}
  if (dy_match(p, k, n, "analyze^@", caps) >= 0) {
  return 1;
}
  if (dy_match(p, k, n, "wfc^field^", caps) >= 0) {
  return 1;
}
  if (dy_match(p, k, n, "couple^@", caps) >= 0) {
  return 1;
}
  if (dy_match(p, k, n, "guide^@", caps) >= 0) {
  return 1;
}
  return 0;
}

int32_t dy_head_at(uint8_t* p, int32_t i, int32_t n, int32_t* caps) {
  int32_t k = i;
  while (k < n && dy_ws(p[k]) == 1) {
  k = (k + 1);
}
  if (dy_head_ns(p, k, n, caps) == 1) {
  return 1;
}
  if (dy_starts(p, k, n, "dyn.") == 1 && dy_head_ns(p, (k + 4), n, caps) == 1) {
  return 1;
}
  if (dy_starts(p, k, n, "dynamics.") == 1 && dy_head_ns(p, (k + 9), n, caps) == 1) {
  return 1;
}
  if (dy_match(p, k, n, "dyn~{", caps) >= 0) {
  return 1;
}
  if (dy_match(p, k, n, "dynamics~{", caps) >= 0) {
  return 1;
}
  if (dy_match(p, k, n, "represent^@", caps) >= 0) {
  return 1;
}
  return 0;
}

int32_t flowc_dynamics_has_dsl(uint8_t* p, int32_t n) {
  int32_t* caps = (int32_t*)(dy_i32s(8));
  int32_t i = 0;
  int32_t r = 0;
  while (i <= n) {
  if (i == 0 || p[(i - 1)] == 10) {
  if (dy_head_at(p, i, n, caps) == 1) {
  r = 1;
  break;
}
}
  i = (i + 1);
}
  free((uint8_t*)(caps));
  return r;
}

int32_t dy_contains(DySb* b, const char* lit) {
  if (dy_find_str((b[0]).p, 0, (b[0]).len, lit) >= 0) {
  return 1;
}
  return 0;
}

void dy_prepend(DySb* b, const char* lit) {
  DySb* t = (DySb*)(dy_sb_new(((b[0]).len + 64)));
  dy_puts(t, lit);
  dy_span(t, (b[0]).p, 0, (b[0]).len);
  (b[0]).len = 0;
  dy_span(b, (t[0]).p, 0, (t[0]).len);
  free((t[0]).p);
  free((uint8_t*)(t));
}

int32_t dy_find_main_call(uint8_t* p, int32_t n) {
  int32_t* caps = (int32_t*)(dy_i32s(4));
  int32_t i = 0;
  while (i < n) {
  if (p[i] == 10 && dy_match(p, (i + 1), n, "function^main~(", caps) >= 0) {
  return i;
}
  i = (i + 1);
}
  return (0 - 1);
}

int32_t dy_find_main_body(uint8_t* p, int32_t n) {
  int32_t* caps = (int32_t*)(dy_i32s(4));
  int32_t i = 0;
  while (i < n) {
  int32_t a = dy_match(p, i, n, "function^main~(", caps);
  if (a >= 0) {
  int32_t k = a;
  while (k < n && p[k] != 41) {
  k = (k + 1);
}
  if (k < n) {
  int32_t z = dy_match(p, k, n, ")~->~@~{", caps);
  if (z >= 0) {
  return z;
}
}
}
  i = (i + 1);
}
  return (0 - 1);
}

int32_t dy_expand(DyC* c, uint8_t* p, int32_t n, DySb* out) {
  if (flowc_dynamics_has_dsl(p, n) == 0) {
  dy_span(out, p, 0, n);
  return 0;
}
  Dp* g = (Dp*)(dy_prog_new(n));
  DySb* merged = (DySb*)(dy_sb_new((n + 64)));
  dy_parse(c, p, n, g, merged);
  if ((c[0]).err != 0) {
  return (0 - 1);
}
  DySb* setup = (DySb*)(dy_sb_new(4096));
  int32_t has_setup = dy_compile(c, g, setup);
  if ((c[0]).err != 0) {
  return (0 - 1);
}
  DySb* portraits = (DySb*)(dy_sb_new(1024));
  dy_compile_portraits(c, g, portraits);
  if (has_setup == 0 && (portraits[0]).len == 0) {
  dy_span(out, (merged[0]).p, 0, (merged[0]).len);
  return 0;
}
  int32_t needs_ga = 0;
  if ((g[0]).nsy > 0 || (g[0]).nse > 0 || (g[0]).nga > 0 || (g[0]).ncl > 0 || (g[0]).nanz > 0 || (g[0]).nlq > 0) {
  needs_ga = 1;
}
  int32_t coupled = 0;
  if ((g[0]).nwf > 0 || (g[0]).ncp > 0 || (g[0]).ngd > 0) {
  if (dy_contains(merged, "import \"stdlib/dynamics/wfc_ga_coupling.flow\"") == 0) {
  dy_prepend(merged, "import \"stdlib/dynamics/wfc_ga_coupling.flow\"\n\n");
  coupled = 1;
}
}
  if (coupled == 0 && needs_ga == 1) {
  if (dy_contains(merged, "import \"stdlib/dynamics/ga_analysis.flow\"") == 0) {
  dy_prepend(merged, "import \"stdlib/dynamics/ga_analysis.flow\"\n\n");
}
}
  if ((g[0]).nlq > 0 && dy_contains(merged, "import \"stdlib/dynamics/lqr.flow\"") == 0) {
  dy_prepend(merged, "import \"stdlib/dynamics/lqr.flow\"\n");
}
  if ((g[0]).npt > 0) {
  if (dy_contains(merged, "import \"stdlib/dynamics/portrait.flow\"") == 0) {
  dy_prepend(merged, "import \"stdlib/dynamics/portrait.flow\"\n");
}
  if (dy_contains(merged, "import \"stdlib/gfx.flow\"") == 0) {
  dy_prepend(merged, "import \"stdlib/gfx.flow\"\n");
}
}
  DySb* cur = (DySb*)(merged);
  if ((portraits[0]).len > 0) {
  int32_t* hs = (int32_t*)(dy_i32s(2));
  hs[0] = 0;
  hs[1] = (portraits[0]).len;
  dy_strip((portraits[0]).p, hs);
  DySb* nx = (DySb*)(dy_sb_new((((cur[0]).len + (portraits[0]).len) + 16)));
  int32_t at = dy_find_main_call((cur[0]).p, (cur[0]).len);
  if (at < 0) {
  int32_t* rs = (int32_t*)(dy_i32s(2));
  rs[0] = 0;
  rs[1] = (cur[0]).len;
  dy_rstrip((cur[0]).p, rs);
  dy_span(nx, (cur[0]).p, 0, rs[1]);
  dy_puts(nx, "\n\n");
  dy_span(nx, (portraits[0]).p, hs[0], hs[1]);
  dy_puts(nx, "\n");
} else {
  dy_span(nx, (cur[0]).p, 0, at);
  dy_puts(nx, "\n\n");
  dy_span(nx, (portraits[0]).p, hs[0], hs[1]);
  dy_puts(nx, "\n");
  dy_span(nx, (cur[0]).p, at, (cur[0]).len);
}
  cur = nx;
}
  if (has_setup == 1) {
  int32_t end = dy_find_main_body((cur[0]).p, (cur[0]).len);
  if (end < 0) {
  dy_span(out, (cur[0]).p, 0, (cur[0]).len);
  dy_puts(out, "\n\nfunction main() -> i32 {\n");
  dy_span(out, (setup[0]).p, 0, (setup[0]).len);
  dy_puts(out, "\n    return 0\n}\n");
} else {
  dy_span(out, (cur[0]).p, 0, end);
  dy_puts(out, "\n");
  dy_span(out, (setup[0]).p, 0, (setup[0]).len);
  dy_puts(out, "\n");
  dy_span(out, (cur[0]).p, end, (cur[0]).len);
}
  return 0;
}
  dy_span(out, (cur[0]).p, 0, (cur[0]).len);
  return 0;
}

DyC* dy_ctx_new(int32_t n) {
  DyC* c = (DyC*)((DyC*)(malloc(256)));
  (c[0]).err = 0;
  (c[0]).msg = dy_sb_new(256);
  (c[0]).nm = dy_sb_new((n + 256));
  (c[0]).fcap = (n + 64);
  (c[0]).fp = dy_f64s((c[0]).fcap);
  (c[0]).fnum = 0;
  (c[0]).bdcap = (n + 64);
  (c[0]).bd_kind = dy_i32s((c[0]).bdcap);
  (c[0]).bd_var = dy_i32s((c[0]).bdcap);
  (c[0]).bd_hz = dy_i32s((c[0]).bdcap);
  (c[0]).nbd = 0;
  (c[0]).glcap = (n + 64);
  (c[0]).gl = dy_i32s((c[0]).glcap);
  (c[0]).ngl = 0;
  (c[0]).atcap = 64;
  (c[0]).at_name = dy_i32s(64);
  (c[0]).at_val = dy_f64s(64);
  (c[0]).nat = 0;
  dy_putc((c[0]).nm, 0);
  return c;
}

int32_t flowc_dynamics_expand_in_place(uint8_t* buf, int32_t n, int32_t cap) {
  if (n < 0) {
  return n;
}
  if (flowc_dynamics_has_dsl(buf, n) == 0) {
  return n;
}
  DyC* c = (DyC*)(dy_ctx_new(n));
  DySb* out = (DySb*)(dy_sb_new(((n * 2) + 4096)));
  int32_t rc = dy_expand(c, buf, n, out);
  if (rc < 0) {
  DySb* line = (DySb*)(dy_sb_new((((c[0]).msg[0]).len + 32)));
  dy_puts(line, "flowc dynamics: ");
  dy_span(line, ((c[0]).msg[0]).p, 0, ((c[0]).msg[0]).len);
  puts((const char*)((line[0]).p));
  return (0 - 1);
}
  if ((out[0]).len >= cap) {
  puts("flowc dynamics: expanded source exceeds the source buffer");
  return (0 - 1);
}
  int32_t k = 0;
  while (k < (out[0]).len) {
  buf[k] = (out[0]).p[k];
  k = (k + 1);
}
  buf[(out[0]).len] = 0;
  return (out[0]).len;
}


typedef struct FbBuf {
  uint8_t* p;
  int32_t len;
  int32_t cap;
} FbBuf;

typedef struct Fb {
  uint8_t* src;
  int32_t n;
  int32_t nt;
  int32_t* tk;
  int32_t* top;
  int32_t* ts;
  int32_t* te;
  int32_t* tl;
  int32_t* tc;
  int32_t* tvar;
  int32_t pos;
  int32_t nn;
  int32_t ncap;
  int32_t* nk;
  int32_t* nop;
  int32_t* ntok;
  int32_t* na;
  int32_t* nb;
  int32_t* nc;
  int32_t* nx;
  int32_t* nfs;
  int32_t* nfe;
  FbBuf* nm;
  int32_t nf;
  int32_t* f_name;
  int32_t* f_line;
  int32_t* f_start;
  int32_t* f_end;
  int32_t* f_solver;
  int64_t* f_dt_ns;
  int32_t* f_dt_text;
  int32_t* f_method;
  int32_t* f_solver_line;
  int32_t* f_rec;
  int32_t* f_rec_line;
  int32_t* f_out;
  int32_t nmm;
  int32_t icap;
  int32_t* mm_flow;
  int32_t* mm_kind;
  int32_t* mm_name;
  int32_t* mm_type;
  int32_t* mm_init;
  int32_t* mm_line;
  int32_t* mm_synth;
  int32_t* mm_params;
  int32_t* mm_pipe_m;
  int32_t* mm_pipe_p;
  int32_t nev;
  int32_t* ev_flow;
  int32_t* ev_target;
  int32_t* ev_expr;
  int32_t* ev_line;
  int32_t nwh;
  int32_t* wh_flow;
  int32_t* wh_target;
  int32_t* wh_thr;
  int32_t* wh_line;
  int32_t ney;
  int32_t* ey_flow;
  int64_t* ey_ns;
  int32_t* ey_text;
  int32_t* ey_line;
  int32_t nbc;
  int32_t* bc_kind;
  int32_t* bc_owner;
  int32_t* bc_target;
  int32_t* bc_expr;
  int32_t* bc_line;
  int32_t niv;
  int32_t* iv_flow;
  int32_t* iv_kind;
  int32_t* iv_expr;
  int32_t* iv_line;
  int32_t* iv_text;
  int32_t ncn;
  int32_t* cn_flow;
  int32_t* cn_sm;
  int32_t* cn_sp;
  int32_t* cn_dm;
  int32_t* cn_dp;
  int32_t* cn_line;
  int32_t nrc;
  int32_t* rc_flow;
  int32_t* rc_name;
  int32_t nnames;
  int32_t* nx_kind;
  int32_t* nx_name;
  int32_t err;
  int32_t err_flow;
  int32_t err_line;
  int32_t err_col;
  FbBuf* emsg;
  FbBuf* ehint;
  int32_t has_hint;
  int32_t cur;
  FbBuf* out;
} Fb;

static const int32_t TK_IDENT = 1;
static const int32_t TK_NUM = 2;
static const int32_t TK_STR = 3;
static const int32_t TK_OP = 4;
static const int32_t TK_CLAIM_PATH = 5;
static const int32_t TK_CLAIM_COORD = 6;
static const int32_t TK_EOF = 7;
static const int32_t OP_ARROW = 1;
static const int32_t OP_FAT_ARROW = 2;
static const int32_t OP_QUESTION = 3;
static const int32_t OP_EQUALS = 4;
static const int32_t OP_NOT_EQUALS = 5;
static const int32_t OP_LSHIFT = 6;
static const int32_t OP_RSHIFT = 7;
static const int32_t OP_LESS_EQUAL = 8;
static const int32_t OP_GREATER_EQUAL = 9;
static const int32_t OP_AND = 10;
static const int32_t OP_OR = 11;
static const int32_t OP_PIPELINE = 12;
static const int32_t OP_PIPE = 13;
static const int32_t OP_AMPERSAND = 14;
static const int32_t OP_CARET = 15;
static const int32_t OP_TILDE = 16;
static const int32_t OP_ELLIPSIS = 17;
static const int32_t OP_DOTDOT = 18;
static const int32_t OP_DOUBLE_COLON = 19;
static const int32_t OP_PLUS_ASSIGN = 20;
static const int32_t OP_MINUS_ASSIGN = 21;
static const int32_t OP_STAR_ASSIGN = 22;
static const int32_t OP_SLASH_ASSIGN = 23;
static const int32_t OP_PLUS = 24;
static const int32_t OP_MINUS = 25;
static const int32_t OP_STAR = 26;
static const int32_t OP_SLASH = 27;
static const int32_t OP_PERCENT = 28;
static const int32_t OP_LESS = 29;
static const int32_t OP_GREATER = 30;
static const int32_t OP_ASSIGN = 31;
static const int32_t OP_NOT = 32;
static const int32_t OP_LPAREN = 33;
static const int32_t OP_RPAREN = 34;
static const int32_t OP_LBRACE = 35;
static const int32_t OP_RBRACE = 36;
static const int32_t OP_LBRACKET = 37;
static const int32_t OP_RBRACKET = 38;
static const int32_t OP_SEMICOLON = 39;
static const int32_t OP_COLON = 40;
static const int32_t OP_COMMA = 41;
static const int32_t OP_DOT = 42;
static const int32_t OP_AT = 43;
static const int32_t FB_MAX_FLOWS = 256;
static const int32_t NX_TAKEN = 1;
static const int32_t NX_LOCAL_FN = 2;
static const int32_t NX_DIMENSION = 3;
static const int32_t MK_DEAD = 0;
static const int32_t MK_STATE = 1;
static const int32_t MK_INPUT = 2;
static const int32_t MK_OUTPUT = 3;
static const int32_t MK_PARAM = 4;
static const int32_t MK_CHILD = 5;
static const int32_t N_VAR = 1;
static const int32_t N_LIT = 2;
static const int32_t N_BIN = 3;
static const int32_t N_UN = 4;
static const int32_t N_CALL = 5;
static const int32_t N_METHOD = 6;
static const int32_t N_FIELD = 7;
static const int32_t N_INDEX = 8;
static const int32_t N_SLICE = 9;
static const int32_t N_CAST = 10;
static const int32_t N_TRY = 11;
static const int32_t N_ARRAY = 12;
static const int32_t N_VEC = 13;
static const int32_t N_STRUCT = 14;
static const int32_t N_RECUPD = 15;
static const int32_t N_EFFECT = 16;
static const int32_t N_LAMBDA = 17;
static const int32_t N_IFX = 18;
static const int32_t N_STAGE = 19;
static const int32_t N_FORK = 20;
static const int32_t N_FINIT = 21;
static const int32_t N_OPAQUE = 22;
static const int32_t OPX_IN = 100;
static const int32_t OPX_NOT_WORD = 101;
static const int64_t FB_I64_MAX = 9223372036854775807;
FbBuf* fb_buf_new(int32_t cap);
void fb_buf_free(FbBuf* b);
void fb_putc(FbBuf* b, uint8_t ch);
void fb_puts(FbBuf* b, const char* s);
void fb_put_span(FbBuf* b, uint8_t* src, int32_t s, int32_t e);
void fb_put_i64(FbBuf* b, int64_t v);
void fb_put_int(FbBuf* b, int32_t v);
int32_t fb_is_space(uint8_t ch);
int32_t fb_is_digit(uint8_t ch);
int32_t fb_is_hex(uint8_t ch);
int32_t fb_is_alpha(uint8_t ch);
int32_t fb_is_lower(uint8_t ch);
int32_t fb_is_upper(uint8_t ch);
int32_t fb_is_ident_start(uint8_t ch);
int32_t fb_is_ident_char(uint8_t ch);
int32_t fb_str_eq(uint8_t* a, const char* b);
const char* fb_op_name(int32_t op);
uint8_t* fb_s(Fb* c, int32_t off);
int32_t fb_intern_span(Fb* c, int32_t s, int32_t e);
int32_t fb_intern(Fb* c, const char* s);
int32_t fb_intern_buf(Fb* c, FbBuf* b);
int32_t fb_tok_str(Fb* c, int32_t t);
int32_t fb_name_eq(Fb* c, int32_t a, int32_t b);
int32_t fb_name_is(Fb* c, int32_t a, const char* lit);
int32_t fb_name_starts_uu(Fb* c, int32_t a);
FbBuf* fb_err_begin(Fb* c, int32_t kind, int32_t line, int32_t col);
FbBuf* fb_err_hint(Fb* c);
int32_t fb_contains(uint8_t* hay, const char* needle);
void fb_auto_hint(Fb* c);
FbBuf* fb_perr(Fb* c);
FbBuf* fb_verr(Fb* c, int32_t line);
FbBuf* fb_serr(Fb* c);
void fb_err_clear(Fb* c);
int32_t fb_expand_len(uint8_t* p, int32_t s, int32_t e);
int32_t fb_op2(int32_t* op, int32_t code, int32_t len);
int32_t fb_lex_op(uint8_t* p, int32_t i, int32_t n, int32_t* op);
int32_t fb_lex_string(uint8_t* p, int32_t i, int32_t n);
int32_t fb_lex_exp(uint8_t* p, int32_t k, int32_t n);
int32_t fb_lex_number(uint8_t* p, int32_t i, int32_t n);
int32_t fb_is_laquo(uint8_t* p, int32_t i, int32_t n);
int32_t fb_is_raquo(uint8_t* p, int32_t i, int32_t n);
int32_t fb_lex_guillemet(uint8_t* p, int32_t i, int32_t n);
int32_t fb_lex_claim_coord(uint8_t* p, int32_t i, int32_t n);
int32_t fb_lex_claim_path(uint8_t* p, int32_t i, int32_t n);
void fb_add_tok(Fb* c, int32_t kind, int32_t op, int32_t s, int32_t e, int32_t line, int32_t col);
int32_t fb_lex_one(uint8_t* p, int32_t i, int32_t n, int32_t* kind, int32_t* op);
int32_t fb_lex(Fb* c);
int32_t fb_tok_is(Fb* c, int32_t t, const char* lit);
const char* fb_word_type(Fb* c, int32_t t);
const char* fb_ttype(Fb* c, int32_t t);
int32_t fb_tt_is(Fb* c, int32_t t, const char* name);
int32_t fb_is_ident(Fb* c, int32_t t);
int32_t fb_is_op(Fb* c, int32_t t, int32_t op);
int32_t fb_is_word(Fb* c, int32_t t, const char* w);
int32_t fb_at_eof(Fb* c);
int32_t fb_la(Fb* c);
int32_t fb_la2(Fb* c);
void fb_advance(Fb* c);
void fb_put_ttype(Fb* c, FbBuf* b, int32_t t);
int32_t fb_expect(Fb* c, const char* name);
int32_t fb_node(Fb* c, int32_t kind, int32_t tok);
int32_t fb_node2(Fb* c, int32_t kind, int32_t tok, int32_t a, int32_t b);
int32_t fb_list_add(Fb* c, int32_t head, int32_t x);
int32_t fb_list_len(Fb* c, int32_t head);
int32_t fb_is_numtype(Fb* c, int32_t t);
int32_t fb_expect_greater(Fb* c);
int32_t fb_parse_type(Fb* c);
int32_t fb_is_orop(Fb* c, int32_t t);
int32_t fb_is_andop(Fb* c, int32_t t);
int32_t fb_bin(Fb* c, int32_t op, int32_t tok, int32_t l, int32_t r);
int32_t fb_parse_expr(Fb* c);
int32_t fb_parse_or(Fb* c);
int32_t fb_parse_and(Fb* c);
int32_t fb_parse_bitor(Fb* c);
int32_t fb_parse_xor(Fb* c);
int32_t fb_parse_bitand(Fb* c);
int32_t fb_parse_equality(Fb* c);
int32_t fb_cmp_op(Fb* c, int32_t t);
int32_t fb_parse_comparison(Fb* c);
int32_t fb_parse_shift(Fb* c);
int32_t fb_parse_term(Fb* c);
int32_t fb_parse_factor(Fb* c);
int32_t fb_parse_cast(Fb* c);
int32_t fb_parse_unary(Fb* c);
int32_t fb_parse_args(Fb* c, int32_t close);
int32_t fb_parse_call(Fb* c, int32_t name_tok);
int32_t fb_parse_postfix(Fb* c, int32_t base);
int32_t fb_parse_struct_lit(Fb* c, int32_t name_tok);
int32_t fb_skip_braces(Fb* c);
int32_t fb_parse_lambda(Fb* c);
int32_t fb_parse_if_expr(Fb* c);
int32_t fb_parse_name_primary(Fb* c);
int32_t fb_parse_primary(Fb* c);
int32_t fb_is_placeholder(Fb* c, int32_t x);
int32_t fb_pipe_args(Fb* c, int32_t piped, int32_t args);
int32_t fb_parse_stage_params(Fb* c, int32_t name_tok, int32_t source);
int32_t fb_tok_span_eq(Fb* c, int32_t a, int32_t b);
int32_t fb_parse_fork(Fb* c, int32_t t, int32_t source);
int32_t fb_fork_field_start(Fb* c, int32_t first, int32_t q);
int32_t fb_parse_pipeline(Fb* c, int32_t left0);
int32_t fb_add_member(Fb* c, int32_t f, int32_t kind, int32_t name, int32_t ty, int32_t init, int32_t line);
void fb_add_conn(Fb* c, int32_t f, int32_t sm, int32_t sp, int32_t dm, int32_t dp, int32_t line);
void fb_add_name(Fb* c, int32_t kind, int32_t name);
int32_t fb_has_name(Fb* c, int32_t kind, int32_t name);
int64_t fb_pow10(int32_t k);
int32_t fb_parse_duration(Fb* c, int32_t where_s, int64_t* ns, int32_t* text);
void fb_put_tok(FbBuf* b, Fb* c, int32_t t);
void fb_put_fname(FbBuf* b, Fb* c, int32_t f);
int32_t fb_parse_becomes_body(Fb* c, int32_t f, int32_t kind, int32_t owner, const char* word, const char* what);
int32_t fb_wrap_top(Fb* c, int32_t root, int32_t start_tok);
int32_t fb_source_between(Fb* c, int32_t st, int32_t et);
int32_t fb_line_start(Fb* c, int32_t ln);
int32_t fb_line_end(Fb* c, int32_t off);
int32_t fb_col_offset(Fb* c, int32_t ln, int32_t col);
void fb_put_stripped(FbBuf* b, uint8_t* p, int32_t s, int32_t e);
int32_t fb_put_part(FbBuf* b, uint8_t* p, int32_t s, int32_t e, int32_t first);
int32_t fb_parse_invariant(Fb* c, int32_t f, int32_t kind, const char* word);
int32_t fb_parse_recognize(Fb* c, int32_t f);
int32_t fb_parse_connect(Fb* c, int32_t f);
int32_t fb_parse_solver(Fb* c, int32_t f);
int32_t fb_is_section_word(Fb* c, int32_t t);
int32_t fb_parse_flow_item(Fb* c, int32_t f);
int32_t fb_parse_flow(Fb* c, int32_t f);
int32_t fb_find_flow(Fb* c, int32_t name);
int32_t fb_find_flow_str(Fb* c, uint8_t* name);
int32_t fb_find_member(Fb* c, int32_t f, int32_t kind, int32_t name);
int32_t fb_lookup_port(Fb* c, int32_t f, int32_t name);
const char* fb_kind_word(int32_t k);
int32_t fb_count_members(Fb* c, int32_t f, int32_t kind);
int32_t fb_nth_member(Fb* c, int32_t f, int32_t kind, int32_t k);
int32_t fb_evolve_of(Fb* c, int32_t f, int32_t name);
uint8_t* fb_tok_name(Fb* c, int32_t node);
int32_t fb_call_name(Fb* c, int32_t node);
int32_t fb_children(Fb* c, int32_t x, int32_t* out);
int32_t fb_is_pure_math(uint8_t* name);
int32_t fb_check_pure(Fb* c, int32_t x, int32_t f, int32_t where_s, int32_t line);
int32_t fb_check_pure_s(Fb* c, int32_t x, int32_t f, const char* where_s, int32_t line);
int32_t fb_where(Fb* c, const char* pre, int32_t name, const char* post);
int32_t fb_check_threshold(Fb* c, int32_t x, int32_t f, int32_t w);
int32_t fb_check_booleanish(Fb* c, int32_t x, int32_t f, const char* word, int32_t line);
int32_t fb_refs_inputs(Fb* c, int32_t x, int32_t f);
int32_t fb_port_combinational(Fb* c, int32_t f, int32_t port);
int32_t fb_single_port(Fb* c, int32_t sf, int32_t kind, const char* word, int32_t line);
void fb_put_sorted_params(Fb* c, FbBuf* b, int32_t sf);
int32_t fb_expand_pipelines(Fb* c, int32_t f);
int32_t fb_is_member_type(Fb* c, int32_t ty);
int32_t fb_is_scalar_type(Fb* c, int32_t ty);
void fb_reclassify(Fb* c);
int32_t fb_member_rank(int32_t k);
int32_t fb_seen_before(Fb* c, int32_t f, int32_t i);
int32_t fb_validate_members(Fb* c, int32_t f);
int32_t fb_recognition_ok(uint8_t* name);
int32_t fb_validate_connect(Fb* c, int32_t f);
int32_t fb_conn_combo(Fb* c, int32_t f, int32_t i);
int32_t fb_child_index(Fb* c, int32_t f, int32_t name);
int32_t fb_dfs(Fb* c, int32_t f, int32_t node, int32_t* state, int32_t* stack, int32_t* sp, int32_t* cyc);
int32_t fb_check_loops(Fb* c, int32_t f);
int32_t fb_validate_flow(Fb* c, int32_t f);
int32_t fb_becomes_seen(Fb* c, int32_t kind, int32_t owner, int32_t b);
void fb_mark_vars(Fb* c, int32_t x);
int32_t fb_is_member_tok(Fb* c, int32_t f, int32_t t);
int32_t fb_tok_starts(Fb* c, int32_t t, const char* lit);
int32_t fb_tok_ends(Fb* c, int32_t t, const char* lit);
int32_t fb_digits_value(uint8_t* p, int32_t s, int32_t e);
int32_t fb_count_everys(Fb* c, int32_t f);
int32_t fb_count_whens(Fb* c, int32_t f);
void fb_emit_expr(Fb* c, FbBuf* b, int32_t x);
void fb_put_name(Fb* c, FbBuf* b, int32_t off);
void fb_put_self(Fb* c, FbBuf* b, int32_t off);
void fb_put_seconds(FbBuf* b, int64_t ns);
void fb_put_mtype(Fb* c, FbBuf* b, int32_t i);
int32_t fb_is_float_type(Fb* c, int32_t ty);
void fb_put_dtype(Fb* c, FbBuf* b, int32_t i);
void fb_put_dt(Fb* c, FbBuf* b, int32_t i);
int32_t fb_field_count(Fb* c, int32_t f);
int32_t fb_field_kind(int32_t r);
void fb_put_zero(Fb* c, FbBuf* b, int32_t ty);
void fb_emit_struct(Fb* c, FbBuf* b, int32_t f);
void fb_fn_head(Fb* c, FbBuf* b, int32_t f, const char* suffix, const char* params, const char* ret);
void fb_self_param(Fb* c, FbBuf* b, int32_t f);
void fb_emit_new(Fb* c, FbBuf* b, int32_t f);
int32_t fb_nth_when(Fb* c, int32_t f, int32_t k);
int32_t fb_nth_every(Fb* c, int32_t f, int32_t k);
void fb_emit_guard(Fb* c, FbBuf* b, int32_t f, int32_t w);
int32_t fb_has_outputs(Fb* c, int32_t f);
void fb_emit_init(Fb* c, FbBuf* b, int32_t f);
int32_t fb_nth_evolved(Fb* c, int32_t f, int32_t k);
int32_t fb_count_evolved(Fb* c, int32_t f);
void fb_emit_derivs(Fb* c, FbBuf* b, int32_t f);
void fb_emit_derivs_call(Fb* c, FbBuf* b, int32_t f, const char* stage);
void fb_emit_euler(Fb* c, FbBuf* b, int32_t f);
void fb_emit_rk_stage(Fb* c, FbBuf* b, int32_t f, const char* stage, int32_t scale);
void fb_emit_rk4(Fb* c, FbBuf* b, int32_t f);
void fb_emit_every(Fb* c, FbBuf* b, int32_t f, int32_t k);
void fb_emit_staged(Fb* c, FbBuf* b, int32_t f, int32_t kind, int32_t owner, const char* prefix, int32_t k);
void fb_emit_event(Fb* c, FbBuf* b, int32_t f, int32_t k);
int32_t fb_topo_children(Fb* c, int32_t f, int32_t* order);
void fb_emit_child_steps(Fb* c, FbBuf* b, int32_t f);
int32_t fb_count_clauses(Fb* c, int32_t f);
int32_t fb_nth_clause(Fb* c, int32_t f, int32_t idx);
void fb_put_escaped(FbBuf* b, uint8_t* s);
void fb_emit_step(Fb* c, FbBuf* b, int32_t f);
void fb_emit_default_dt(Fb* c, FbBuf* b, int32_t f);
void fb_emit_outputs(Fb* c, FbBuf* b, int32_t f);
void fb_emit_check(Fb* c, FbBuf* b, int32_t f);
void fb_mark_flow(Fb* c, int32_t f);
void fb_lower_flow(Fb* c, int32_t f);
int32_t* fb_alloc_i32(int32_t n);
Fb* fb_ctx_new(uint8_t* src, int32_t n);
void fb_ctx_free(Fb* c);
int32_t fb_decl_name(Fb* c, int32_t t);
int32_t fb_scan(Fb* c, int32_t* flows);
void fb_report(Fb* c);
int32_t fb_maybe_flow(uint8_t* p, int32_t n);
int32_t fb_expand(Fb* c);
int32_t flowc_flow_blocks_expand_in_place(uint8_t* buf, int32_t n, int32_t cap);
FbBuf* fb_buf_new(int32_t cap) {
  FbBuf* b = (FbBuf*)((FbBuf*)(malloc(16)));
  (b[0]).p = malloc((int64_t)((cap + 1)));
  (b[0]).len = 0;
  (b[0]).cap = cap;
  (b[0]).p[0] = 0;
  return b;
}

void fb_buf_free(FbBuf* b) {
  free((b[0]).p);
  free((uint8_t*)(b));
}

void fb_putc(FbBuf* b, uint8_t ch) {
  if (((b[0]).len + 1) >= (b[0]).cap) {
  int32_t ncap = (((b[0]).cap * 2) + 64);
  (b[0]).p = realloc((b[0]).p, (int64_t)((ncap + 1)));
  (b[0]).cap = ncap;
}
  (b[0]).p[(b[0]).len] = ch;
  (b[0]).len = ((b[0]).len + 1);
  (b[0]).p[(b[0]).len] = 0;
}

void fb_puts(FbBuf* b, const char* s) {
  uint8_t* sp = (uint8_t*)((uint8_t*)(s));
  int32_t i = 0;
  while (sp[i] != 0) {
  fb_putc(b, sp[i]);
  i = (i + 1);
}
}

void fb_put_span(FbBuf* b, uint8_t* src, int32_t s, int32_t e) {
  int32_t i = s;
  while (i < e) {
  fb_putc(b, src[i]);
  i = (i + 1);
}
}

void fb_put_i64(FbBuf* b, int64_t v) {
  if (v < 0) {
  fb_putc(b, 45);
  fb_put_i64(b, (0 - v));
  return;
}
  if (v >= 10) {
  fb_put_i64(b, (v / 10));
}
  fb_putc(b, (uint8_t)((48 + (v % 10))));
}

void fb_put_int(FbBuf* b, int32_t v) {
  fb_put_i64(b, (int64_t)(v));
}

int32_t fb_is_space(uint8_t ch) {
  if (ch == 32) {
  return 1;
}
  if (ch >= 9 && ch <= 13) {
  return 1;
}
  if (ch >= 28 && ch <= 31) {
  return 1;
}
  return 0;
}

int32_t fb_is_digit(uint8_t ch) {
  if (ch >= 48 && ch <= 57) {
  return 1;
}
  return 0;
}

int32_t fb_is_hex(uint8_t ch) {
  if (fb_is_digit(ch) == 1) {
  return 1;
}
  if (ch >= 97 && ch <= 102) {
  return 1;
}
  if (ch >= 65 && ch <= 70) {
  return 1;
}
  return 0;
}

int32_t fb_is_alpha(uint8_t ch) {
  if (ch >= 97 && ch <= 122) {
  return 1;
}
  if (ch >= 65 && ch <= 90) {
  return 1;
}
  return 0;
}

int32_t fb_is_lower(uint8_t ch) {
  if (ch >= 97 && ch <= 122) {
  return 1;
}
  return 0;
}

int32_t fb_is_upper(uint8_t ch) {
  if (ch >= 65 && ch <= 90) {
  return 1;
}
  return 0;
}

int32_t fb_is_ident_start(uint8_t ch) {
  if (fb_is_alpha(ch) == 1 || ch == 95) {
  return 1;
}
  return 0;
}

int32_t fb_is_ident_char(uint8_t ch) {
  if (fb_is_ident_start(ch) == 1 || fb_is_digit(ch) == 1) {
  return 1;
}
  return 0;
}

int32_t fb_str_eq(uint8_t* a, const char* b) {
  if (strcmp((const char*)(a), b) == 0) {
  return 1;
}
  return 0;
}

const char* fb_op_name(int32_t op) {
  if (op == OP_ARROW) {
  return "ARROW";
}
  if (op == OP_FAT_ARROW) {
  return "FAT_ARROW";
}
  if (op == OP_QUESTION) {
  return "QUESTION";
}
  if (op == OP_EQUALS) {
  return "EQUALS";
}
  if (op == OP_NOT_EQUALS) {
  return "NOT_EQUALS";
}
  if (op == OP_LSHIFT) {
  return "LSHIFT";
}
  if (op == OP_RSHIFT) {
  return "RSHIFT";
}
  if (op == OP_LESS_EQUAL) {
  return "LESS_EQUAL";
}
  if (op == OP_GREATER_EQUAL) {
  return "GREATER_EQUAL";
}
  if (op == OP_AND) {
  return "AND";
}
  if (op == OP_OR) {
  return "OR";
}
  if (op == OP_PIPELINE) {
  return "PIPELINE";
}
  if (op == OP_PIPE) {
  return "PIPE";
}
  if (op == OP_AMPERSAND) {
  return "AMPERSAND";
}
  if (op == OP_CARET) {
  return "CARET";
}
  if (op == OP_TILDE) {
  return "TILDE";
}
  if (op == OP_ELLIPSIS) {
  return "ELLIPSIS";
}
  if (op == OP_DOTDOT) {
  return "DOTDOT";
}
  if (op == OP_DOUBLE_COLON) {
  return "DOUBLE_COLON";
}
  if (op == OP_PLUS_ASSIGN) {
  return "PLUS_ASSIGN";
}
  if (op == OP_MINUS_ASSIGN) {
  return "MINUS_ASSIGN";
}
  if (op == OP_STAR_ASSIGN) {
  return "STAR_ASSIGN";
}
  if (op == OP_SLASH_ASSIGN) {
  return "SLASH_ASSIGN";
}
  if (op == OP_PLUS) {
  return "PLUS";
}
  if (op == OP_MINUS) {
  return "MINUS";
}
  if (op == OP_STAR) {
  return "STAR";
}
  if (op == OP_SLASH) {
  return "SLASH";
}
  if (op == OP_PERCENT) {
  return "PERCENT";
}
  if (op == OP_LESS) {
  return "LESS";
}
  if (op == OP_GREATER) {
  return "GREATER";
}
  if (op == OP_ASSIGN) {
  return "ASSIGN";
}
  if (op == OP_NOT) {
  return "NOT";
}
  if (op == OP_LPAREN) {
  return "LPAREN";
}
  if (op == OP_RPAREN) {
  return "RPAREN";
}
  if (op == OP_LBRACE) {
  return "LBRACE";
}
  if (op == OP_RBRACE) {
  return "RBRACE";
}
  if (op == OP_LBRACKET) {
  return "LBRACKET";
}
  if (op == OP_RBRACKET) {
  return "RBRACKET";
}
  if (op == OP_SEMICOLON) {
  return "SEMICOLON";
}
  if (op == OP_COLON) {
  return "COLON";
}
  if (op == OP_COMMA) {
  return "COMMA";
}
  if (op == OP_DOT) {
  return "DOT";
}
  return "AT";
}

uint8_t* fb_s(Fb* c, int32_t off) {
  return (((c[0]).nm[0]).p + off);
}

int32_t fb_intern_span(Fb* c, int32_t s, int32_t e) {
  int32_t off = ((c[0]).nm[0]).len;
  fb_put_span((c[0]).nm, (c[0]).src, s, e);
  fb_putc((c[0]).nm, 0);
  return off;
}

int32_t fb_intern(Fb* c, const char* s) {
  int32_t off = ((c[0]).nm[0]).len;
  fb_puts((c[0]).nm, s);
  fb_putc((c[0]).nm, 0);
  return off;
}

int32_t fb_intern_buf(Fb* c, FbBuf* b) {
  int32_t off = ((c[0]).nm[0]).len;
  fb_put_span((c[0]).nm, (b[0]).p, 0, (b[0]).len);
  fb_putc((c[0]).nm, 0);
  return off;
}

int32_t fb_tok_str(Fb* c, int32_t t) {
  return fb_intern_span(c, (c[0]).ts[t], (c[0]).te[t]);
}

int32_t fb_name_eq(Fb* c, int32_t a, int32_t b) {
  if (a < 0 || b < 0) {
  return 0;
}
  if (strcmp((const char*)(fb_s(c, a)), (const char*)(fb_s(c, b))) == 0) {
  return 1;
}
  return 0;
}

int32_t fb_name_is(Fb* c, int32_t a, const char* lit) {
  if (a < 0) {
  return 0;
}
  if (strcmp((const char*)(fb_s(c, a)), lit) == 0) {
  return 1;
}
  return 0;
}

int32_t fb_name_starts_uu(Fb* c, int32_t a) {
  uint8_t* p = (uint8_t*)(fb_s(c, a));
  if (p[0] == 95 && p[1] == 95) {
  return 1;
}
  return 0;
}

FbBuf* fb_err_begin(Fb* c, int32_t kind, int32_t line, int32_t col) {
  (c[0]).err = kind;
  (c[0]).err_line = line;
  (c[0]).err_col = col;
  ((c[0]).emsg[0]).len = 0;
  ((c[0]).emsg[0]).p[0] = 0;
  ((c[0]).ehint[0]).len = 0;
  ((c[0]).ehint[0]).p[0] = 0;
  (c[0]).has_hint = 0;
  return (c[0]).emsg;
}

FbBuf* fb_err_hint(Fb* c) {
  (c[0]).has_hint = 1;
  return (c[0]).ehint;
}

int32_t fb_contains(uint8_t* hay, const char* needle) {
  uint8_t* np = (uint8_t*)((uint8_t*)(needle));
  int32_t nl = (int32_t)(strlen(needle));
  int32_t i = 0;
  while (hay[i] != 0) {
  int32_t k = 0;
  while (k < nl && hay[(i + k)] == np[k]) {
  k = (k + 1);
}
  if (k == nl) {
  return 1;
}
  i = (i + 1);
}
  return 0;
}

void fb_auto_hint(Fb* c) {
  uint8_t* m = (uint8_t*)(((c[0]).emsg[0]).p);
  if (fb_contains(m, "Expected TokenType.RBRACE") == 1) {
  fb_puts(fb_err_hint(c), "Missing closing brace '}'. Check for unbalanced braces.");
  return;
}
  if (fb_contains(m, "Expected TokenType.RPAREN") == 1) {
  fb_puts(fb_err_hint(c), "Missing closing parenthesis ')'. Check function calls and expressions.");
  return;
}
  if (fb_contains(m, "Expected TokenType.SEMICOLON") == 1) {
  fb_puts(fb_err_hint(c), "Semicolons are optional in FLOW. If you see this error, there may be a syntax issue before this point.");
  return;
}
  if (fb_contains(m, "Expected TokenType.IDENTIFIER") == 1) {
  fb_puts(fb_err_hint(c), "Expected a name (identifier) here. Names must start with a letter or underscore.");
  return;
}
  if (fb_contains(m, "Unexpected token in expression") == 1) {
  fb_puts(fb_err_hint(c), "This token cannot start an expression. Check for typos or missing operators.");
  return;
}
  if (fb_contains(m, "Unexpected declaration") == 1) {
  fb_puts(fb_err_hint(c), "This keyword cannot appear at the top level. Check for missing braces or incorrect nesting.");
  return;
}
}

FbBuf* fb_perr(Fb* c) {
  int32_t t = (c[0]).pos;
  return fb_err_begin(c, 1, (c[0]).tl[t], (c[0]).tc[t]);
}

FbBuf* fb_verr(Fb* c, int32_t line) {
  return fb_err_begin(c, 1, line, 0);
}

FbBuf* fb_serr(Fb* c) {
  return fb_err_begin(c, 2, 0, 0);
}

void fb_err_clear(Fb* c) {
  (c[0]).err = 0;
}

int32_t fb_expand_len(uint8_t* p, int32_t s, int32_t e) {
  int32_t total = 0;
  int32_t col = 0;
  int32_t i = s;
  while (i < e) {
  uint8_t ch = p[i];
  if (ch == 9) {
  int32_t w = (4 - (col % 4));
  total = (total + w);
  col = (col + w);
} else {
  if (ch == 10 || ch == 13) {
  total = (total + 1);
  col = 0;
} else {
  if (ch < 128 || ch >= 192) {
  total = (total + 1);
  col = (col + 1);
}
}
}
  i = (i + 1);
}
  return total;
}

int32_t fb_op2(int32_t* op, int32_t code, int32_t len) {
  op[0] = code;
  return len;
}

int32_t fb_lex_op(uint8_t* p, int32_t i, int32_t n, int32_t* op) {
  uint8_t a = p[i];
  uint8_t b = 0;
  if ((i + 1) < n) {
  b = p[(i + 1)];
}
  uint8_t d = 0;
  if ((i + 2) < n) {
  d = p[(i + 2)];
}
  if (a == 45 && b == 62) {
  return fb_op2(op, OP_ARROW, 2);
}
  if (a == 61 && b == 62) {
  return fb_op2(op, OP_FAT_ARROW, 2);
}
  if (a == 63) {
  return fb_op2(op, OP_QUESTION, 1);
}
  if (a == 61 && b == 61) {
  return fb_op2(op, OP_EQUALS, 2);
}
  if (a == 33 && b == 61) {
  return fb_op2(op, OP_NOT_EQUALS, 2);
}
  if (a == 60 && b == 60) {
  return fb_op2(op, OP_LSHIFT, 2);
}
  if (a == 62 && b == 62) {
  return fb_op2(op, OP_RSHIFT, 2);
}
  if (a == 60 && b == 61) {
  return fb_op2(op, OP_LESS_EQUAL, 2);
}
  if (a == 62 && b == 61) {
  return fb_op2(op, OP_GREATER_EQUAL, 2);
}
  if (a == 38 && b == 38) {
  return fb_op2(op, OP_AND, 2);
}
  if (a == 124 && b == 124) {
  return fb_op2(op, OP_OR, 2);
}
  if (a == 124 && b == 62) {
  return fb_op2(op, OP_PIPELINE, 2);
}
  if (a == 124) {
  return fb_op2(op, OP_PIPE, 1);
}
  if (a == 38) {
  return fb_op2(op, OP_AMPERSAND, 1);
}
  if (a == 94) {
  return fb_op2(op, OP_CARET, 1);
}
  if (a == 126) {
  return fb_op2(op, OP_TILDE, 1);
}
  if (a == 46 && b == 46 && d == 46) {
  return fb_op2(op, OP_ELLIPSIS, 3);
}
  if (a == 46 && b == 46) {
  return fb_op2(op, OP_DOTDOT, 2);
}
  if (a == 58 && b == 58) {
  return fb_op2(op, OP_DOUBLE_COLON, 2);
}
  if (a == 43 && b == 61) {
  return fb_op2(op, OP_PLUS_ASSIGN, 2);
}
  if (a == 45 && b == 61) {
  return fb_op2(op, OP_MINUS_ASSIGN, 2);
}
  if (a == 42 && b == 61) {
  return fb_op2(op, OP_STAR_ASSIGN, 2);
}
  if (a == 47 && b == 61) {
  return fb_op2(op, OP_SLASH_ASSIGN, 2);
}
  if (a == 43) {
  return fb_op2(op, OP_PLUS, 1);
}
  if (a == 45) {
  return fb_op2(op, OP_MINUS, 1);
}
  if (a == 42) {
  return fb_op2(op, OP_STAR, 1);
}
  if (a == 47) {
  return fb_op2(op, OP_SLASH, 1);
}
  if (a == 37) {
  return fb_op2(op, OP_PERCENT, 1);
}
  if (a == 60) {
  return fb_op2(op, OP_LESS, 1);
}
  if (a == 62) {
  return fb_op2(op, OP_GREATER, 1);
}
  if (a == 61) {
  return fb_op2(op, OP_ASSIGN, 1);
}
  if (a == 33) {
  return fb_op2(op, OP_NOT, 1);
}
  if (a == 40) {
  return fb_op2(op, OP_LPAREN, 1);
}
  if (a == 41) {
  return fb_op2(op, OP_RPAREN, 1);
}
  if (a == 123) {
  return fb_op2(op, OP_LBRACE, 1);
}
  if (a == 125) {
  return fb_op2(op, OP_RBRACE, 1);
}
  if (a == 91) {
  return fb_op2(op, OP_LBRACKET, 1);
}
  if (a == 93) {
  return fb_op2(op, OP_RBRACKET, 1);
}
  if (a == 59) {
  return fb_op2(op, OP_SEMICOLON, 1);
}
  if (a == 58) {
  return fb_op2(op, OP_COLON, 1);
}
  if (a == 44) {
  return fb_op2(op, OP_COMMA, 1);
}
  if (a == 46) {
  return fb_op2(op, OP_DOT, 1);
}
  if (a == 64) {
  return fb_op2(op, OP_AT, 1);
}
  return 0;
}

int32_t fb_lex_string(uint8_t* p, int32_t i, int32_t n) {
  int32_t k = (i + 1);
  while (k < n) {
  uint8_t ch = p[k];
  if (ch == 34) {
  return (k + 1);
}
  if (ch == 92) {
  if ((k + 1) >= n) {
  return (0 - 1);
}
  if (p[(k + 1)] == 10) {
  return (0 - 1);
}
  k = (k + 2);
} else {
  k = (k + 1);
}
}
  return (0 - 1);
}

int32_t fb_lex_exp(uint8_t* p, int32_t k, int32_t n) {
  if (k < n && (p[k] == 101 || p[k] == 69)) {
  int32_t j = (k + 1);
  if (j < n && (p[j] == 43 || p[j] == 45)) {
  j = (j + 1);
}
  if (j < n && fb_is_digit(p[j]) == 1) {
  while (j < n && fb_is_digit(p[j]) == 1) {
  j = (j + 1);
}
  return j;
}
}
  return (0 - 1);
}

int32_t fb_lex_number(uint8_t* p, int32_t i, int32_t n) {
  if (p[i] == 48 && (i + 2) < n && p[(i + 1)] == 120 && fb_is_hex(p[(i + 2)]) == 1) {
  int32_t h = (i + 2);
  while (h < n && fb_is_hex(p[h]) == 1) {
  h = (h + 1);
}
  return h;
}
  int32_t k = i;
  while (k < n && fb_is_digit(p[k]) == 1) {
  k = (k + 1);
}
  if ((k + 1) < n && p[k] == 46 && fb_is_digit(p[(k + 1)]) == 1) {
  int32_t f = (k + 1);
  while (f < n && fb_is_digit(p[f]) == 1) {
  f = (f + 1);
}
  int32_t x = fb_lex_exp(p, f, n);
  if (x > 0) {
  return x;
}
  return f;
}
  int32_t x2 = fb_lex_exp(p, k, n);
  if (x2 > 0) {
  return x2;
}
  return k;
}

int32_t fb_is_laquo(uint8_t* p, int32_t i, int32_t n) {
  if ((i + 1) < n && p[i] == 194 && p[(i + 1)] == 171) {
  return 1;
}
  return 0;
}

int32_t fb_is_raquo(uint8_t* p, int32_t i, int32_t n) {
  if ((i + 1) < n && p[i] == 194 && p[(i + 1)] == 187) {
  return 1;
}
  return 0;
}

int32_t fb_lex_guillemet(uint8_t* p, int32_t i, int32_t n) {
  if (fb_is_laquo(p, i, n) == 0) {
  return (0 - 1);
}
  int32_t k = (i + 2);
  int32_t start = k;
  while (k < n && fb_is_raquo(p, k, n) == 0) {
  k = (k + 1);
}
  if (k >= n || k == start) {
  return (0 - 1);
}
  return (k + 2);
}

int32_t fb_lex_claim_coord(uint8_t* p, int32_t i, int32_t n) {
  int32_t k = fb_lex_guillemet(p, i, n);
  if (k < 0) {
  return (0 - 1);
}
  while (k < n && fb_is_space(p[k]) == 1) {
  k = (k + 1);
}
  k = fb_lex_guillemet(p, k, n);
  if (k < 0) {
  return (0 - 1);
}
  while (k < n && fb_is_space(p[k]) == 1) {
  k = (k + 1);
}
  return fb_lex_guillemet(p, k, n);
}

int32_t fb_lex_claim_path(uint8_t* p, int32_t i, int32_t n) {
  if (fb_is_alpha(p[i]) == 0) {
  return (0 - 1);
}
  int32_t k = (i + 1);
  while (k < n && fb_is_ident_char(p[k]) == 1) {
  k = (k + 1);
}
  if (k >= n || p[k] != 47) {
  return (0 - 1);
}
  k = (k + 1);
  if (k >= n) {
  return (0 - 1);
}
  if ((k + 1) < n && p[k] == 124 && p[(k + 1)] == 124) {
  k = (k + 2);
} else {
  uint8_t ch = p[k];
  if (ch == 43 || ch == 124 || ch == 61 || ch == 42) {
  k = (k + 1);
} else {
  if (fb_is_lower(ch) == 0) {
  return (0 - 1);
}
  k = (k + 1);
  while (k < n && (fb_is_ident_char(p[k]) == 1 || p[k] == 45)) {
  k = (k + 1);
}
}
}
  if (k >= n || p[k] != 46) {
  return (0 - 1);
}
  k = (k + 1);
  if (k >= n || fb_is_lower(p[k]) == 0) {
  return (0 - 1);
}
  k = (k + 1);
  int32_t first = k;
  while (k < n && (fb_is_lower(p[k]) == 1 || fb_is_digit(p[k]) == 1 || p[k] == 45)) {
  k = (k + 1);
}
  if (k == first) {
  return (0 - 1);
}
  return k;
}

void fb_add_tok(Fb* c, int32_t kind, int32_t op, int32_t s, int32_t e, int32_t line, int32_t col) {
  int32_t t = (c[0]).nt;
  (c[0]).tk[t] = kind;
  (c[0]).top[t] = op;
  (c[0]).ts[t] = s;
  (c[0]).te[t] = e;
  (c[0]).tl[t] = line;
  (c[0]).tc[t] = col;
  (c[0]).tvar[t] = 0;
  (c[0]).nt = (t + 1);
}

int32_t fb_lex_one(uint8_t* p, int32_t i, int32_t n, int32_t* kind, int32_t* op) {
  uint8_t ch = p[i];
  int32_t ol = fb_lex_op(p, i, n, op);
  if (ol > 0) {
  kind[0] = TK_OP;
  return (i + ol);
}
  op[0] = 0;
  if (ch == 34) {
  kind[0] = TK_STR;
  return fb_lex_string(p, i, n);
}
  if (fb_is_digit(ch) == 1) {
  kind[0] = TK_NUM;
  return fb_lex_number(p, i, n);
}
  int32_t cc = fb_lex_claim_coord(p, i, n);
  if (cc > 0) {
  kind[0] = TK_CLAIM_COORD;
  return cc;
}
  int32_t cp = fb_lex_claim_path(p, i, n);
  if (cp > 0) {
  kind[0] = TK_CLAIM_PATH;
  return cp;
}
  if (fb_is_ident_start(ch) == 1) {
  int32_t k = i;
  while (k < n && fb_is_ident_char(p[k]) == 1) {
  k = (k + 1);
}
  kind[0] = TK_IDENT;
  return k;
}
  return (0 - 1);
}

int32_t fb_lex(Fb* c) {
  uint8_t* p = (uint8_t*)((c[0]).src);
  int32_t n = (c[0]).n;
  int32_t i = 0;
  int32_t line = 1;
  int32_t col = 1;
  int32_t* box = (int32_t*)((int32_t*)(malloc(8)));
  int32_t rc = 0;
  while (i < n && rc == 0) {
  uint8_t ch = p[i];
  if (ch == 35) {
  int32_t k = i;
  while (k < n && p[k] != 10) {
  k = (k + 1);
}
  col = (col + fb_expand_len(p, i, k));
  i = k;
} else {
  if (ch == 10) {
  line = (line + 1);
  col = 1;
  i = (i + 1);
} else {
  if (fb_is_space(ch) == 1) {
  int32_t k = i;
  while (k < n && fb_is_space(p[k]) == 1) {
  k = (k + 1);
}
  col = (col + fb_expand_len(p, i, k));
  i = k;
} else {
  int32_t e = fb_lex_one(p, i, n, box, (box + 1));
  if (e < 0) {
  rc = (0 - 1);
} else {
  fb_add_tok(c, box[0], box[1], i, e, line, col);
  col = (col + fb_expand_len(p, i, e));
  i = e;
}
}
}
}
}
  fb_add_tok(c, TK_EOF, 0, n, n, line, col);
  free((uint8_t*)(box));
  return rc;
}

int32_t fb_tok_is(Fb* c, int32_t t, const char* lit) {
  uint8_t* lp = (uint8_t*)((uint8_t*)(lit));
  int32_t s = (c[0]).ts[t];
  int32_t e = (c[0]).te[t];
  int32_t i = 0;
  while ((s + i) < e) {
  if (lp[i] != (c[0]).src[(s + i)]) {
  return 0;
}
  i = (i + 1);
}
  if (lp[i] != 0) {
  return 0;
}
  return 1;
}

const char* fb_word_type(Fb* c, int32_t t) {
  if (fb_tok_is(c, t, "true") == 1 || fb_tok_is(c, t, "false") == 1) {
  return "BOOLEAN";
}
  if (fb_tok_is(c, t, "string") == 1) {
  return "STRING_TYPE";
}
  if (fb_tok_is(c, t, "function") == 1) {
  return "FUNCTION";
}
  if (fb_tok_is(c, t, "let") == 1) {
  return "LET";
}
  if (fb_tok_is(c, t, "mut") == 1) {
  return "MUT";
}
  if (fb_tok_is(c, t, "return") == 1) {
  return "RETURN";
}
  if (fb_tok_is(c, t, "if") == 1) {
  return "IF";
}
  if (fb_tok_is(c, t, "elif") == 1) {
  return "ELIF";
}
  if (fb_tok_is(c, t, "else") == 1) {
  return "ELSE";
}
  if (fb_tok_is(c, t, "while") == 1) {
  return "WHILE";
}
  if (fb_tok_is(c, t, "for") == 1) {
  return "FOR";
}
  if (fb_tok_is(c, t, "break") == 1) {
  return "BREAK";
}
  if (fb_tok_is(c, t, "continue") == 1) {
  return "CONTINUE";
}
  if (fb_tok_is(c, t, "in") == 1) {
  return "IN";
}
  if (fb_tok_is(c, t, "parallel") == 1) {
  return "PARALLEL";
}
  if (fb_tok_is(c, t, "to") == 1) {
  return "TO";
}
  if (fb_tok_is(c, t, "match") == 1) {
  return "MATCH";
}
  if (fb_tok_is(c, t, "default") == 1) {
  return "DEFAULT";
}
  if (fb_tok_is(c, t, "test") == 1) {
  return "TEST";
}
  if (fb_tok_is(c, t, "trait") == 1) {
  return "TRAIT";
}
  if (fb_tok_is(c, t, "impl") == 1) {
  return "IMPL";
}
  if (fb_tok_is(c, t, "self") == 1) {
  return "SELF";
}
  if (fb_tok_is(c, t, "type") == 1) {
  return "TYPE";
}
  if (fb_tok_is(c, t, "distinct") == 1) {
  return "DISTINCT";
}
  if (fb_tok_is(c, t, "as") == 1) {
  return "AS";
}
  if (fb_tok_is(c, t, "enum") == 1) {
  return "ENUM";
}
  if (fb_tok_is(c, t, "theorem") == 1) {
  return "THEOREM";
}
  if (fb_tok_is(c, t, "assume") == 1) {
  return "ASSUME";
}
  if (fb_tok_is(c, t, "therefore") == 1) {
  return "THEREFORE";
}
  if (fb_tok_is(c, t, "with") == 1) {
  return "WITH";
}
  if (fb_tok_is(c, t, "handle") == 1) {
  return "HANDLE";
}
  if (fb_tok_is(c, t, "ui_layout") == 1) {
  return "UI_LAYOUT";
}
  if (fb_tok_is(c, t, "ui_row") == 1) {
  return "UI_ROW";
}
  if (fb_tok_is(c, t, "ui_column") == 1) {
  return "UI_COLUMN";
}
  if (fb_tok_is(c, t, "ui_stack") == 1) {
  return "UI_STACK";
}
  if (fb_tok_is(c, t, "ui_grid") == 1) {
  return "UI_GRID";
}
  if (fb_tok_is(c, t, "effect") == 1) {
  return "EFFECT";
}
  if (fb_tok_is(c, t, "capability") == 1) {
  return "CAPABILITY";
}
  if (fb_tok_is(c, t, "import") == 1) {
  return "IMPORT";
}
  if (fb_tok_is(c, t, "export") == 1) {
  return "EXPORT";
}
  if (fb_tok_is(c, t, "extern") == 1) {
  return "EXTERN";
}
  if (fb_tok_is(c, t, "const") == 1) {
  return "CONST";
}
  if (fb_tok_is(c, t, "struct") == 1) {
  return "STRUCT";
}
  if (fb_tok_is(c, t, "and") == 1) {
  return "AND";
}
  if (fb_tok_is(c, t, "or") == 1) {
  return "OR";
}
  if (fb_tok_is(c, t, "not") == 1) {
  return "NOT";
}
  if (fb_tok_is(c, t, "null") == 1) {
  return "NULL";
}
  if (fb_tok_is(c, t, "defer") == 1) {
  return "DEFER";
}
  if (fb_tok_is(c, t, "dbg") == 1) {
  return "DBG";
}
  if (fb_tok_is(c, t, "expect") == 1) {
  return "EXPECT";
}
  if (fb_tok_is(c, t, "module") == 1) {
  return "MODULE";
}
  if (fb_tok_is(c, t, "void") == 1) {
  return "VOID";
}
  if (fb_tok_is(c, t, "i8") == 1) {
  return "I8";
}
  if (fb_tok_is(c, t, "i16") == 1) {
  return "I16";
}
  if (fb_tok_is(c, t, "i32") == 1) {
  return "I32";
}
  if (fb_tok_is(c, t, "i64") == 1) {
  return "I64";
}
  if (fb_tok_is(c, t, "i128") == 1) {
  return "I128";
}
  if (fb_tok_is(c, t, "u8") == 1) {
  return "U8";
}
  if (fb_tok_is(c, t, "u16") == 1) {
  return "U16";
}
  if (fb_tok_is(c, t, "u32") == 1) {
  return "U32";
}
  if (fb_tok_is(c, t, "u64") == 1) {
  return "U64";
}
  if (fb_tok_is(c, t, "u128") == 1) {
  return "U128";
}
  if (fb_tok_is(c, t, "f32") == 1) {
  return "F32";
}
  if (fb_tok_is(c, t, "f64") == 1) {
  return "F64";
}
  if (fb_tok_is(c, t, "c64") == 1) {
  return "C64";
}
  if (fb_tok_is(c, t, "c128") == 1) {
  return "C128";
}
  if (fb_tok_is(c, t, "bool") == 1) {
  return "BOOL";
}
  if (fb_tok_is(c, t, "vec") == 1) {
  return "VEC";
}
  return "IDENTIFIER";
}

const char* fb_ttype(Fb* c, int32_t t) {
  int32_t k = (c[0]).tk[t];
  if (k == TK_IDENT) {
  return fb_word_type(c, t);
}
  if (k == TK_NUM) {
  return "NUMBER";
}
  if (k == TK_STR) {
  return "STRING_LITERAL";
}
  if (k == TK_OP) {
  return fb_op_name((c[0]).top[t]);
}
  if (k == TK_CLAIM_PATH) {
  return "CLAIM_PATH";
}
  if (k == TK_CLAIM_COORD) {
  return "CLAIM_COORDINATE";
}
  return "EOF";
}

int32_t fb_tt_is(Fb* c, int32_t t, const char* name) {
  if (strcmp(fb_ttype(c, t), name) == 0) {
  return 1;
}
  return 0;
}

int32_t fb_is_ident(Fb* c, int32_t t) {
  if ((c[0]).tk[t] != TK_IDENT) {
  return 0;
}
  return fb_tt_is(c, t, "IDENTIFIER");
}

int32_t fb_is_op(Fb* c, int32_t t, int32_t op) {
  if ((c[0]).tk[t] == TK_OP && (c[0]).top[t] == op) {
  return 1;
}
  return 0;
}

int32_t fb_is_word(Fb* c, int32_t t, const char* w) {
  if (fb_is_ident(c, t) == 1 && fb_tok_is(c, t, w) == 1) {
  return 1;
}
  return 0;
}

int32_t fb_at_eof(Fb* c) {
  if ((c[0]).tk[(c[0]).pos] == TK_EOF) {
  return 1;
}
  return 0;
}

int32_t fb_la(Fb* c) {
  int32_t t = (c[0]).pos;
  if ((c[0]).tk[t] == TK_EOF) {
  return t;
}
  return (t + 1);
}

int32_t fb_la2(Fb* c) {
  int32_t t = fb_la(c);
  if ((c[0]).tk[t] == TK_EOF) {
  return t;
}
  return (t + 1);
}

void fb_advance(Fb* c) {
  if ((c[0]).tk[(c[0]).pos] != TK_EOF) {
  (c[0]).pos = ((c[0]).pos + 1);
}
}

void fb_put_ttype(Fb* c, FbBuf* b, int32_t t) {
  fb_puts(b, "TokenType.");
  fb_puts(b, fb_ttype(c, t));
}

int32_t fb_expect(Fb* c, const char* name) {
  int32_t t = (c[0]).pos;
  if (fb_tt_is(c, t, name) == 1) {
  fb_advance(c);
  return t;
}
  if (strcmp(name, "IDENTIFIER") == 0) {
  if (fb_tt_is(c, t, "TEST") == 1 || fb_tt_is(c, t, "AND") == 1 || fb_tt_is(c, t, "OR") == 1) {
  fb_advance(c);
  return t;
}
}
  FbBuf* m = (FbBuf*)(fb_perr(c));
  fb_puts(m, "Expected TokenType.");
  fb_puts(m, name);
  fb_puts(m, ", got ");
  fb_put_ttype(c, m, t);
  fb_auto_hint(c);
  return (0 - 1);
}

int32_t fb_node(Fb* c, int32_t kind, int32_t tok) {
  int32_t id = (c[0]).nn;
  if (id >= (c[0]).ncap) {
  int32_t ncap = (((c[0]).ncap * 2) + 64);
  int64_t bytes = ((int64_t)(ncap) * 4);
  (c[0]).nk = (int32_t*)(realloc((uint8_t*)((c[0]).nk), bytes));
  (c[0]).nop = (int32_t*)(realloc((uint8_t*)((c[0]).nop), bytes));
  (c[0]).ntok = (int32_t*)(realloc((uint8_t*)((c[0]).ntok), bytes));
  (c[0]).na = (int32_t*)(realloc((uint8_t*)((c[0]).na), bytes));
  (c[0]).nb = (int32_t*)(realloc((uint8_t*)((c[0]).nb), bytes));
  (c[0]).nc = (int32_t*)(realloc((uint8_t*)((c[0]).nc), bytes));
  (c[0]).nx = (int32_t*)(realloc((uint8_t*)((c[0]).nx), bytes));
  (c[0]).nfs = (int32_t*)(realloc((uint8_t*)((c[0]).nfs), bytes));
  (c[0]).nfe = (int32_t*)(realloc((uint8_t*)((c[0]).nfe), bytes));
  (c[0]).ncap = ncap;
}
  (c[0]).nk[id] = kind;
  (c[0]).nop[id] = 0;
  (c[0]).ntok[id] = tok;
  (c[0]).na[id] = (0 - 1);
  (c[0]).nb[id] = (0 - 1);
  (c[0]).nc[id] = (0 - 1);
  (c[0]).nx[id] = (0 - 1);
  (c[0]).nfs[id] = tok;
  (c[0]).nfe[id] = tok;
  (c[0]).nn = (id + 1);
  return id;
}

int32_t fb_node2(Fb* c, int32_t kind, int32_t tok, int32_t a, int32_t b) {
  int32_t id = fb_node(c, kind, tok);
  (c[0]).na[id] = a;
  (c[0]).nb[id] = b;
  return id;
}

int32_t fb_list_add(Fb* c, int32_t head, int32_t x) {
  if (head < 0) {
  return x;
}
  int32_t k = head;
  while ((c[0]).nx[k] >= 0) {
  k = (c[0]).nx[k];
}
  (c[0]).nx[k] = x;
  return head;
}

int32_t fb_list_len(Fb* c, int32_t head) {
  int32_t n = 0;
  int32_t k = head;
  while (k >= 0) {
  n = (n + 1);
  k = (c[0]).nx[k];
}
  return n;
}

int32_t fb_is_numtype(Fb* c, int32_t t) {
  const char* ty = fb_ttype(c, t);
  if (strcmp(ty, "I8") == 0 || strcmp(ty, "I16") == 0 || strcmp(ty, "I32") == 0) {
  return 1;
}
  if (strcmp(ty, "I64") == 0 || strcmp(ty, "I128") == 0) {
  return 1;
}
  if (strcmp(ty, "U8") == 0 || strcmp(ty, "U16") == 0 || strcmp(ty, "U32") == 0) {
  return 1;
}
  if (strcmp(ty, "U64") == 0 || strcmp(ty, "U128") == 0) {
  return 1;
}
  if (strcmp(ty, "F32") == 0 || strcmp(ty, "F64") == 0) {
  return 1;
}
  if (strcmp(ty, "C64") == 0 || strcmp(ty, "C128") == 0) {
  return 1;
}
  return 0;
}

int32_t fb_expect_greater(Fb* c) {
  int32_t t = (c[0]).pos;
  if (fb_is_op(c, t, OP_RSHIFT) == 1) {
  (c[0]).ts[t] = ((c[0]).ts[t] + 1);
  (c[0]).tc[t] = ((c[0]).tc[t] + 1);
  (c[0]).top[t] = OP_GREATER;
  return t;
}
  return fb_expect(c, "GREATER");
}

int32_t fb_parse_type(Fb* c) {
  int32_t t = (c[0]).pos;
  if (fb_is_ident(c, t) == 1 || fb_is_numtype(c, t) == 1) {
  int32_t name = fb_tok_str(c, t);
  fb_advance(c);
  int32_t cur = (c[0]).pos;
  if (fb_is_op(c, cur, OP_LESS) == 1 && (fb_name_is(c, name, "array") == 1 || fb_name_is(c, name, "ptr") == 1)) {
  fb_advance(c);
  int32_t inner = fb_parse_type(c);
  if (inner < 0) {
  return (0 - 1);
}
  FbBuf* b = (FbBuf*)(fb_buf_new(32));
  fb_puts(b, (const char*)(fb_s(c, name)));
  fb_putc(b, 95);
  if (fb_name_is(c, name, "array") == 1 && fb_is_op(c, (c[0]).pos, OP_COMMA) == 1) {
  fb_advance(c);
  int32_t st = (c[0]).pos;
  if ((c[0]).tk[st] != TK_NUM) {
  FbBuf* m = (FbBuf*)(fb_perr(c));
  fb_puts(m, "array size must be an integer literal, got ");
  fb_put_ttype(c, m, st);
  fb_puts(fb_err_hint(c), "use a non-negative integer literal for the array size, e.g. 4");
  fb_buf_free(b);
  return (0 - 1);
}
  fb_put_span(b, (c[0]).src, (c[0]).ts[st], (c[0]).te[st]);
  fb_putc(b, 95);
  fb_advance(c);
}
  fb_puts(b, (const char*)(fb_s(c, inner)));
  int32_t out = fb_intern_buf(c, b);
  fb_buf_free(b);
  if (fb_expect_greater(c) < 0) {
  return (0 - 1);
}
  return out;
}
  if (fb_is_op(c, cur, OP_LBRACKET) == 1) {
  fb_advance(c);
  if (fb_expect(c, "RBRACKET") < 0) {
  return (0 - 1);
}
  FbBuf* b2 = (FbBuf*)(fb_buf_new(32));
  fb_puts(b2, "array_");
  fb_puts(b2, (const char*)(fb_s(c, name)));
  int32_t out2 = fb_intern_buf(c, b2);
  fb_buf_free(b2);
  return out2;
}
  if (fb_is_op(c, cur, OP_LESS) == 1) {
  fb_advance(c);
  FbBuf* b3 = (FbBuf*)(fb_buf_new(32));
  fb_puts(b3, (const char*)(fb_s(c, name)));
  int32_t a0 = fb_parse_type(c);
  if (a0 < 0) {
  fb_buf_free(b3);
  return (0 - 1);
}
  fb_putc(b3, 95);
  fb_puts(b3, (const char*)(fb_s(c, a0)));
  while (fb_is_op(c, (c[0]).pos, OP_COMMA) == 1) {
  fb_advance(c);
  int32_t a1 = fb_parse_type(c);
  if (a1 < 0) {
  fb_buf_free(b3);
  return (0 - 1);
}
  fb_putc(b3, 95);
  fb_puts(b3, (const char*)(fb_s(c, a1)));
}
  int32_t out3 = fb_intern_buf(c, b3);
  fb_buf_free(b3);
  if (fb_expect_greater(c) < 0) {
  return (0 - 1);
}
  return out3;
}
  return name;
}
  if (fb_tt_is(c, t, "BOOL") == 1 || fb_tt_is(c, t, "VOID") == 1 || fb_tt_is(c, t, "STRING_TYPE") == 1) {
  fb_advance(c);
  return fb_tok_str(c, t);
}
  FbBuf* m2 = (FbBuf*)(fb_serr(c));
  fb_puts(m2, "Unexpected type token: ");
  fb_put_ttype(c, m2, t);
  return (0 - 1);
}

int32_t fb_is_orop(Fb* c, int32_t t) {
  return fb_tt_is(c, t, "OR");
}

int32_t fb_is_andop(Fb* c, int32_t t) {
  return fb_tt_is(c, t, "AND");
}

int32_t fb_bin(Fb* c, int32_t op, int32_t tok, int32_t l, int32_t r) {
  int32_t id = fb_node2(c, N_BIN, tok, l, r);
  (c[0]).nop[id] = op;
  return id;
}

int32_t fb_parse_expr(Fb* c) {
  int32_t left = fb_parse_or(c);
  if (left < 0) {
  return (0 - 1);
}
  return fb_parse_pipeline(c, left);
}

int32_t fb_parse_or(Fb* c) {
  int32_t left = fb_parse_and(c);
  if (left < 0) {
  return (0 - 1);
}
  while (fb_is_orop(c, (c[0]).pos) == 1) {
  int32_t t = (c[0]).pos;
  fb_advance(c);
  int32_t right = fb_parse_and(c);
  if (right < 0) {
  return (0 - 1);
}
  left = fb_bin(c, OP_OR, t, left, right);
}
  return left;
}

int32_t fb_parse_and(Fb* c) {
  int32_t left = fb_parse_bitor(c);
  if (left < 0) {
  return (0 - 1);
}
  while (fb_is_andop(c, (c[0]).pos) == 1) {
  int32_t t = (c[0]).pos;
  fb_advance(c);
  int32_t right = fb_parse_bitor(c);
  if (right < 0) {
  return (0 - 1);
}
  left = fb_bin(c, OP_AND, t, left, right);
}
  return left;
}

int32_t fb_parse_bitor(Fb* c) {
  int32_t left = fb_parse_xor(c);
  if (left < 0) {
  return (0 - 1);
}
  while (fb_is_op(c, (c[0]).pos, OP_PIPE) == 1) {
  int32_t t = (c[0]).pos;
  fb_advance(c);
  int32_t right = fb_parse_xor(c);
  if (right < 0) {
  return (0 - 1);
}
  left = fb_bin(c, OP_PIPE, t, left, right);
}
  return left;
}

int32_t fb_parse_xor(Fb* c) {
  int32_t left = fb_parse_bitand(c);
  if (left < 0) {
  return (0 - 1);
}
  while (fb_is_op(c, (c[0]).pos, OP_CARET) == 1) {
  int32_t t = (c[0]).pos;
  fb_advance(c);
  int32_t right = fb_parse_bitand(c);
  if (right < 0) {
  return (0 - 1);
}
  left = fb_bin(c, OP_CARET, t, left, right);
}
  return left;
}

int32_t fb_parse_bitand(Fb* c) {
  int32_t left = fb_parse_equality(c);
  if (left < 0) {
  return (0 - 1);
}
  while (fb_is_op(c, (c[0]).pos, OP_AMPERSAND) == 1) {
  int32_t t = (c[0]).pos;
  fb_advance(c);
  int32_t right = fb_parse_equality(c);
  if (right < 0) {
  return (0 - 1);
}
  left = fb_bin(c, OP_AMPERSAND, t, left, right);
}
  return left;
}

int32_t fb_parse_equality(Fb* c) {
  int32_t left = fb_parse_comparison(c);
  if (left < 0) {
  return (0 - 1);
}
  while (fb_is_op(c, (c[0]).pos, OP_EQUALS) == 1 || fb_is_op(c, (c[0]).pos, OP_NOT_EQUALS) == 1) {
  int32_t t = (c[0]).pos;
  fb_advance(c);
  int32_t right = fb_parse_comparison(c);
  if (right < 0) {
  return (0 - 1);
}
  left = fb_bin(c, (c[0]).top[t], t, left, right);
}
  return left;
}

int32_t fb_cmp_op(Fb* c, int32_t t) {
  if (fb_is_op(c, t, OP_LESS) == 1) {
  return OP_LESS;
}
  if (fb_is_op(c, t, OP_GREATER) == 1) {
  return OP_GREATER;
}
  if (fb_is_op(c, t, OP_LESS_EQUAL) == 1) {
  return OP_LESS_EQUAL;
}
  if (fb_is_op(c, t, OP_GREATER_EQUAL) == 1) {
  return OP_GREATER_EQUAL;
}
  if (fb_tt_is(c, t, "IN") == 1) {
  return OPX_IN;
}
  return 0;
}

int32_t fb_parse_comparison(Fb* c) {
  int32_t left = fb_parse_shift(c);
  if (left < 0) {
  return (0 - 1);
}
  while (fb_cmp_op(c, (c[0]).pos) != 0) {
  int32_t t = (c[0]).pos;
  int32_t op = fb_cmp_op(c, t);
  fb_advance(c);
  int32_t right = fb_parse_shift(c);
  if (right < 0) {
  return (0 - 1);
}
  left = fb_bin(c, op, t, left, right);
}
  return left;
}

int32_t fb_parse_shift(Fb* c) {
  int32_t left = fb_parse_term(c);
  if (left < 0) {
  return (0 - 1);
}
  while (fb_is_op(c, (c[0]).pos, OP_LSHIFT) == 1 || fb_is_op(c, (c[0]).pos, OP_RSHIFT) == 1) {
  int32_t t = (c[0]).pos;
  fb_advance(c);
  int32_t right = fb_parse_term(c);
  if (right < 0) {
  return (0 - 1);
}
  left = fb_bin(c, (c[0]).top[t], t, left, right);
}
  return left;
}

int32_t fb_parse_term(Fb* c) {
  int32_t left = fb_parse_factor(c);
  if (left < 0) {
  return (0 - 1);
}
  while (fb_is_op(c, (c[0]).pos, OP_PLUS) == 1 || fb_is_op(c, (c[0]).pos, OP_MINUS) == 1) {
  int32_t t = (c[0]).pos;
  fb_advance(c);
  int32_t right = fb_parse_factor(c);
  if (right < 0) {
  return (0 - 1);
}
  left = fb_bin(c, (c[0]).top[t], t, left, right);
}
  return left;
}

int32_t fb_parse_factor(Fb* c) {
  int32_t left = fb_parse_cast(c);
  if (left < 0) {
  return (0 - 1);
}
  while (fb_is_op(c, (c[0]).pos, OP_STAR) == 1 || fb_is_op(c, (c[0]).pos, OP_SLASH) == 1 || fb_is_op(c, (c[0]).pos, OP_PERCENT) == 1) {
  int32_t t = (c[0]).pos;
  fb_advance(c);
  int32_t right = fb_parse_cast(c);
  if (right < 0) {
  return (0 - 1);
}
  left = fb_bin(c, (c[0]).top[t], t, left, right);
}
  return left;
}

int32_t fb_parse_cast(Fb* c) {
  int32_t e = fb_parse_unary(c);
  if (e < 0) {
  return (0 - 1);
}
  while (fb_tt_is(c, (c[0]).pos, "AS") == 1) {
  int32_t t = (c[0]).pos;
  fb_advance(c);
  int32_t ty = fb_parse_type(c);
  if (ty < 0) {
  return (0 - 1);
}
  e = fb_node2(c, N_CAST, t, e, (0 - 1));
  (c[0]).nop[e] = ty;
}
  while (fb_is_op(c, (c[0]).pos, OP_QUESTION) == 1) {
  int32_t t2 = (c[0]).pos;
  fb_advance(c);
  e = fb_node2(c, N_TRY, t2, e, (0 - 1));
}
  return e;
}

int32_t fb_parse_unary(Fb* c) {
  int32_t t = (c[0]).pos;
  if (fb_tt_is(c, t, "DBG") == 1) {
  fb_advance(c);
  int32_t operand = fb_parse_unary(c);
  if (operand < 0) {
  return (0 - 1);
}
  int32_t call = fb_node2(c, N_CALL, (0 - 1), operand, (0 - 1));
  return call;
}
  int32_t op = 0;
  if (fb_is_op(c, t, OP_MINUS) == 1) {
  op = OP_MINUS;
}
  if (fb_is_op(c, t, OP_NOT) == 1) {
  op = OP_NOT;
}
  if ((c[0]).tk[t] == TK_IDENT && fb_tok_is(c, t, "not") == 1) {
  op = OPX_NOT_WORD;
}
  if (fb_is_op(c, t, OP_TILDE) == 1) {
  op = OP_TILDE;
}
  if (fb_is_op(c, t, OP_AMPERSAND) == 1) {
  op = OP_AMPERSAND;
}
  if (fb_is_op(c, t, OP_STAR) == 1) {
  op = OP_STAR;
}
  if (op != 0) {
  fb_advance(c);
  int32_t operand2 = fb_parse_unary(c);
  if (operand2 < 0) {
  return (0 - 1);
}
  int32_t u = fb_node2(c, N_UN, t, operand2, (0 - 1));
  (c[0]).nop[u] = op;
  return u;
}
  return fb_parse_primary(c);
}

int32_t fb_parse_args(Fb* c, int32_t close) {
  if (fb_is_op(c, (c[0]).pos, close) == 1) {
  return (0 - 1);
}
  int32_t first = fb_parse_expr(c);
  if (first < 0) {
  return (0 - 2);
}
  int32_t head = first;
  while (fb_is_op(c, (c[0]).pos, OP_COMMA) == 1) {
  fb_advance(c);
  int32_t a = fb_parse_expr(c);
  if (a < 0) {
  return (0 - 2);
}
  head = fb_list_add(c, head, a);
}
  return head;
}

int32_t fb_parse_call(Fb* c, int32_t name_tok) {
  if (fb_expect(c, "LPAREN") < 0) {
  return (0 - 1);
}
  int32_t args = fb_parse_args(c, OP_RPAREN);
  if (args == (0 - 2)) {
  return (0 - 1);
}
  if (fb_expect(c, "RPAREN") < 0) {
  return (0 - 1);
}
  return fb_node2(c, N_CALL, name_tok, args, (0 - 1));
}

int32_t fb_parse_postfix(Fb* c, int32_t base) {
  int32_t e = base;
  while (fb_is_op(c, (c[0]).pos, OP_DOT) == 1 || fb_is_op(c, (c[0]).pos, OP_LBRACKET) == 1) {
  if (fb_is_op(c, (c[0]).pos, OP_DOT) == 1) {
  fb_advance(c);
  int32_t mt = fb_expect(c, "IDENTIFIER");
  if (mt < 0) {
  return (0 - 1);
}
  if (fb_is_op(c, (c[0]).pos, OP_LPAREN) == 1) {
  fb_advance(c);
  int32_t args = fb_parse_args(c, OP_RPAREN);
  if (args == (0 - 2)) {
  return (0 - 1);
}
  if (fb_expect(c, "RPAREN") < 0) {
  return (0 - 1);
}
  e = fb_node2(c, N_METHOD, mt, e, args);
} else {
  e = fb_node2(c, N_FIELD, mt, e, (0 - 1));
}
} else {
  int32_t bt = (c[0]).pos;
  fb_advance(c);
  int32_t idx = fb_parse_expr(c);
  if (idx < 0) {
  return (0 - 1);
}
  if (fb_is_op(c, (c[0]).pos, OP_DOTDOT) == 1) {
  fb_advance(c);
  int32_t hi = fb_parse_expr(c);
  if (hi < 0) {
  return (0 - 1);
}
  if (fb_expect(c, "RBRACKET") < 0) {
  return (0 - 1);
}
  e = fb_node2(c, N_SLICE, bt, e, idx);
  (c[0]).nc[e] = hi;
} else {
  if (fb_expect(c, "RBRACKET") < 0) {
  return (0 - 1);
}
  e = fb_node2(c, N_INDEX, bt, e, idx);
}
}
}
  return e;
}

int32_t fb_parse_struct_lit(Fb* c, int32_t name_tok) {
  if (fb_expect(c, "LBRACE") < 0) {
  return (0 - 1);
}
  if (fb_is_op(c, (c[0]).pos, OP_DOTDOT) == 1) {
  fb_advance(c);
  int32_t base = fb_parse_expr(c);
  if (base < 0) {
  return (0 - 1);
}
  int32_t ups = (0 - 1);
  while (fb_is_op(c, (c[0]).pos, OP_COMMA) == 1) {
  fb_advance(c);
  if (fb_is_op(c, (c[0]).pos, OP_RBRACE) == 1) {
  break;
}
  int32_t ft = fb_expect(c, "IDENTIFIER");
  if (ft < 0) {
  return (0 - 1);
}
  if (fb_expect(c, "COLON") < 0) {
  return (0 - 1);
}
  int32_t fv = fb_parse_expr(c);
  if (fv < 0) {
  return (0 - 1);
}
  ups = fb_list_add(c, ups, fb_node2(c, N_FINIT, ft, fv, (0 - 1)));
}
  if (fb_expect(c, "RBRACE") < 0) {
  return (0 - 1);
}
  return fb_node2(c, N_RECUPD, name_tok, base, ups);
}
  int32_t fields = (0 - 1);
  while (fb_is_op(c, (c[0]).pos, OP_RBRACE) == 0) {
  if (fb_at_eof(c) == 1) {
  fb_puts(fb_serr(c), "Unterminated struct literal: expected '}' before end of file");
  return (0 - 1);
}
  int32_t ft2 = fb_expect(c, "IDENTIFIER");
  if (ft2 < 0) {
  return (0 - 1);
}
  if (fb_expect(c, "COLON") < 0) {
  return (0 - 1);
}
  int32_t fv2 = fb_parse_expr(c);
  if (fv2 < 0) {
  return (0 - 1);
}
  fields = fb_list_add(c, fields, fb_node2(c, N_FINIT, ft2, fv2, (0 - 1)));
  if (fb_is_op(c, (c[0]).pos, OP_COMMA) == 1) {
  fb_advance(c);
}
}
  if (fb_expect(c, "RBRACE") < 0) {
  return (0 - 1);
}
  return fb_node2(c, N_STRUCT, name_tok, fields, (0 - 1));
}

int32_t fb_skip_braces(Fb* c) {
  int32_t depth = 0;
  while (fb_at_eof(c) == 0) {
  int32_t t = (c[0]).pos;
  if (fb_is_op(c, t, OP_LBRACE) == 1) {
  depth = (depth + 1);
}
  if (fb_is_op(c, t, OP_RBRACE) == 1) {
  depth = (depth - 1);
  if (depth == 0) {
  fb_advance(c);
  return 0;
}
}
  fb_advance(c);
}
  fb_puts(fb_serr(c), "Unterminated block: expected '}' before end of file");
  return (0 - 1);
}

int32_t fb_parse_lambda(Fb* c) {
  int32_t t = (c[0]).pos;
  if (fb_expect(c, "PIPE") < 0) {
  return (0 - 1);
}
  if (fb_is_op(c, (c[0]).pos, OP_PIPE) == 0) {
  if (fb_expect(c, "IDENTIFIER") < 0) {
  return (0 - 1);
}
  if (fb_is_op(c, (c[0]).pos, OP_COLON) == 1) {
  fb_advance(c);
  if (fb_parse_type(c) < 0) {
  return (0 - 1);
}
}
  while (fb_is_op(c, (c[0]).pos, OP_COMMA) == 1) {
  fb_advance(c);
  if (fb_expect(c, "IDENTIFIER") < 0) {
  return (0 - 1);
}
  if (fb_is_op(c, (c[0]).pos, OP_COLON) == 1) {
  fb_advance(c);
  if (fb_parse_type(c) < 0) {
  return (0 - 1);
}
}
}
}
  if (fb_expect(c, "PIPE") < 0) {
  return (0 - 1);
}
  if (fb_is_op(c, (c[0]).pos, OP_ARROW) == 1) {
  fb_advance(c);
  if (fb_parse_type(c) < 0) {
  return (0 - 1);
}
}
  if (fb_is_op(c, (c[0]).pos, OP_LBRACE) == 1) {
  if (fb_skip_braces(c) < 0) {
  return (0 - 1);
}
} else {
  if (fb_parse_expr(c) < 0) {
  return (0 - 1);
}
}
  return fb_node(c, N_LAMBDA, t);
}

int32_t fb_parse_if_expr(Fb* c) {
  int32_t t = (c[0]).pos;
  fb_advance(c);
  int32_t cond = fb_parse_expr(c);
  if (cond < 0) {
  return (0 - 1);
}
  if (fb_expect(c, "LBRACE") < 0) {
  return (0 - 1);
}
  int32_t th = fb_parse_expr(c);
  if (th < 0) {
  return (0 - 1);
}
  if (fb_expect(c, "RBRACE") < 0) {
  return (0 - 1);
}
  if (fb_tt_is(c, (c[0]).pos, "ELSE") == 0) {
  fb_puts(fb_serr(c), "if-expression requires an else branch");
  return (0 - 1);
}
  fb_advance(c);
  if (fb_expect(c, "LBRACE") < 0) {
  return (0 - 1);
}
  int32_t el = fb_parse_expr(c);
  if (el < 0) {
  return (0 - 1);
}
  if (fb_expect(c, "RBRACE") < 0) {
  return (0 - 1);
}
  int32_t id = fb_node2(c, N_IFX, t, cond, th);
  (c[0]).nc[id] = el;
  return id;
}

int32_t fb_parse_name_primary(Fb* c) {
  int32_t t = (c[0]).pos;
  fb_advance(c);
  int32_t cur = (c[0]).pos;
  if (fb_is_op(c, cur, OP_LPAREN) == 1) {
  int32_t call = fb_parse_call(c, t);
  if (call < 0) {
  return (0 - 1);
}
  return fb_parse_postfix(c, call);
}
  if (fb_is_op(c, cur, OP_LESS) == 1) {
  int32_t save_nn = (c[0]).nn;
  fb_advance(c);
  int32_t ok = 1;
  if (fb_parse_type(c) < 0) {
  ok = 0;
}
  while (ok == 1 && fb_is_op(c, (c[0]).pos, OP_COMMA) == 1) {
  fb_advance(c);
  if (fb_parse_type(c) < 0) {
  ok = 0;
}
}
  if (ok == 1 && fb_expect_greater(c) < 0) {
  ok = 0;
}
  if (ok == 1) {
  if (fb_is_op(c, (c[0]).pos, OP_LPAREN) == 1) {
  int32_t gcall = fb_parse_call(c, t);
  if (gcall >= 0) {
  (c[0]).nop[gcall] = 1;
  return fb_parse_postfix(c, gcall);
}
  ok = 0;
} else {
  if (fb_is_op(c, (c[0]).pos, OP_LBRACE) == 1) {
  int32_t gs = fb_parse_struct_lit(c, t);
  if (gs >= 0) {
  return gs;
}
  ok = 0;
} else {
  return fb_node(c, N_OPAQUE, t);
}
}
}
  fb_err_clear(c);
  (c[0]).pos = cur;
  (c[0]).nn = save_nn;
  return fb_node(c, N_VAR, t);
}
  if (fb_is_op(c, cur, OP_LBRACE) == 1) {
  int32_t save_nn2 = (c[0]).nn;
  int32_t sl = fb_parse_struct_lit(c, t);
  if (sl >= 0) {
  return sl;
}
  fb_err_clear(c);
  (c[0]).pos = cur;
  (c[0]).nn = save_nn2;
  return fb_node(c, N_VAR, t);
}
  if (fb_is_op(c, cur, OP_DOT) == 1 || fb_is_op(c, cur, OP_LBRACKET) == 1) {
  return fb_parse_postfix(c, fb_node(c, N_VAR, t));
}
  if (fb_is_op(c, cur, OP_DOUBLE_COLON) == 1) {
  fb_advance(c);
  if (fb_expect(c, "IDENTIFIER") < 0) {
  return (0 - 1);
}
  if (fb_expect(c, "LPAREN") < 0) {
  return (0 - 1);
}
  int32_t eargs = fb_parse_args(c, OP_RPAREN);
  if (eargs == (0 - 2)) {
  return (0 - 1);
}
  if (fb_expect(c, "RPAREN") < 0) {
  return (0 - 1);
}
  return fb_node2(c, N_EFFECT, t, eargs, (0 - 1));
}
  return fb_node(c, N_VAR, t);
}

int32_t fb_parse_primary(Fb* c) {
  int32_t t = (c[0]).pos;
  int32_t k = (c[0]).tk[t];
  if (k == TK_NUM) {
  fb_advance(c);
  int32_t lit = fb_node(c, N_LIT, t);
  int32_t u = (c[0]).pos;
  if (fb_is_ident(c, u) == 1 && (c[0]).tl[u] == (c[0]).tl[t] && fb_is_upper((c[0]).src[(c[0]).ts[u]]) == 1) {
  fb_advance(c);
  int32_t q = fb_node2(c, N_CAST, u, lit, (0 - 1));
  (c[0]).nop[q] = fb_tok_str(c, u);
  return q;
}
  return lit;
}
  if (fb_tt_is(c, t, "BOOLEAN") == 1 || k == TK_STR || fb_tt_is(c, t, "NULL") == 1) {
  fb_advance(c);
  return fb_node(c, N_LIT, t);
}
  if (fb_tt_is(c, t, "SELF") == 1) {
  fb_advance(c);
  int32_t sv = fb_node(c, N_VAR, t);
  if (fb_is_op(c, (c[0]).pos, OP_DOT) == 1) {
  return fb_parse_postfix(c, sv);
}
  return sv;
}
  if (fb_is_op(c, t, OP_LESS) == 1) {
  fb_advance(c);
  int32_t els = (0 - 1);
  if (fb_is_op(c, (c[0]).pos, OP_GREATER) == 0) {
  int32_t e0 = fb_parse_primary(c);
  if (e0 < 0) {
  return (0 - 1);
}
  els = e0;
  while (fb_is_op(c, (c[0]).pos, OP_COMMA) == 1) {
  fb_advance(c);
  int32_t e1 = fb_parse_primary(c);
  if (e1 < 0) {
  return (0 - 1);
}
  els = fb_list_add(c, els, e1);
}
}
  if (fb_expect(c, "GREATER") < 0) {
  return (0 - 1);
}
  return fb_node2(c, N_VEC, t, els, (0 - 1));
}
  if (fb_is_op(c, t, OP_LBRACKET) == 1) {
  fb_advance(c);
  int32_t ael = (0 - 1);
  if (fb_is_op(c, (c[0]).pos, OP_RBRACKET) == 0) {
  int32_t a0 = fb_parse_expr(c);
  if (a0 < 0) {
  return (0 - 1);
}
  ael = a0;
  if (fb_is_op(c, (c[0]).pos, OP_SEMICOLON) == 1) {
  fb_advance(c);
  if (fb_parse_expr(c) < 0) {
  return (0 - 1);
}
} else {
  while (fb_is_op(c, (c[0]).pos, OP_COMMA) == 1) {
  fb_advance(c);
  int32_t a1 = fb_parse_expr(c);
  if (a1 < 0) {
  return (0 - 1);
}
  ael = fb_list_add(c, ael, a1);
}
}
}
  if (fb_expect(c, "RBRACKET") < 0) {
  return (0 - 1);
}
  return fb_node2(c, N_ARRAY, t, ael, (0 - 1));
}
  if (fb_is_ident(c, t) == 1 || fb_tt_is(c, t, "AND") == 1 || fb_tt_is(c, t, "OR") == 1 || fb_tt_is(c, t, "C64") == 1 || fb_tt_is(c, t, "C128") == 1) {
  return fb_parse_name_primary(c);
}
  if (fb_is_op(c, t, OP_LBRACE) == 1 && fb_is_op(c, fb_la(c), OP_DOTDOT) == 1) {
  return fb_parse_struct_lit(c, (0 - 1));
}
  if (fb_is_op(c, t, OP_LPAREN) == 1) {
  fb_advance(c);
  int32_t inner = fb_parse_expr(c);
  if (inner < 0) {
  return (0 - 1);
}
  if (fb_expect(c, "RPAREN") < 0) {
  return (0 - 1);
}
  return fb_parse_postfix(c, inner);
}
  if (fb_is_op(c, t, OP_PIPE) == 1) {
  return fb_parse_lambda(c);
}
  if (fb_tt_is(c, t, "IF") == 1) {
  return fb_parse_if_expr(c);
}
  FbBuf* m = (FbBuf*)(fb_serr(c));
  fb_puts(m, "Unexpected token in expression: ");
  fb_put_ttype(c, m, t);
  return (0 - 1);
}

int32_t fb_is_placeholder(Fb* c, int32_t x) {
  if ((c[0]).nk[x] == N_VAR && fb_tok_is(c, (c[0]).ntok[x], "_") == 1) {
  return 1;
}
  return 0;
}

int32_t fb_pipe_args(Fb* c, int32_t piped, int32_t args) {
  int32_t holes = 0;
  int32_t k = args;
  while (k >= 0) {
  if (fb_is_placeholder(c, k) == 1) {
  holes = (holes + 1);
}
  k = (c[0]).nx[k];
}
  if (holes == 0) {
  (c[0]).nx[piped] = args;
  return piped;
}
  if (holes > 1) {
  FbBuf* m = (FbBuf*)(fb_perr(c));
  fb_puts(m, "Pipeline placeholder '_' may appear at most once per '|>' stage (found ");
  fb_put_int(m, holes);
  fb_puts(m, "); the piped value fills a single slot");
  return (0 - 2);
}
  int32_t head = (0 - 1);
  int32_t j = args;
  while (j >= 0) {
  int32_t nxt = (c[0]).nx[j];
  (c[0]).nx[j] = (0 - 1);
  if (fb_is_placeholder(c, j) == 1) {
  head = fb_list_add(c, head, piped);
} else {
  head = fb_list_add(c, head, j);
}
  j = nxt;
}
  return head;
}

int32_t fb_parse_stage_params(Fb* c, int32_t name_tok, int32_t source) {
  int32_t params = (0 - 1);
  while (fb_is_op(c, (c[0]).pos, OP_RBRACE) == 0) {
  int32_t pt = (c[0]).pos;
  if (fb_is_ident(c, pt) == 0) {
  fb_puts(fb_perr(c), "Expected a parameter name in flow stage params");
  return (0 - 1);
}
  fb_advance(c);
  if (fb_expect(c, "COLON") < 0) {
  return (0 - 1);
}
  int32_t k = params;
  while (k >= 0) {
  if (fb_tok_span_eq(c, (c[0]).ntok[k], pt) == 1) {
  FbBuf* m = (FbBuf*)(fb_perr(c));
  fb_puts(m, "Duplicate stage parameter '");
  fb_put_span(m, (c[0]).src, (c[0]).ts[pt], (c[0]).te[pt]);
  fb_puts(m, "'");
  return (0 - 1);
}
  k = (c[0]).nx[k];
}
  int32_t vs = (c[0]).pos;
  int32_t v = fb_parse_expr(c);
  if (v < 0) {
  return (0 - 1);
}
  fb_wrap_top(c, v, vs);
  params = fb_list_add(c, params, fb_node2(c, N_FINIT, pt, v, (0 - 1)));
  if (fb_is_op(c, (c[0]).pos, OP_COMMA) == 1) {
  fb_advance(c);
}
}
  if (params < 0) {
  FbBuf* m2 = (FbBuf*)(fb_perr(c));
  fb_puts(m2, "flow stage '");
  fb_put_span(m2, (c[0]).src, (c[0]).ts[name_tok], (c[0]).te[name_tok]);
  fb_puts(m2, "' has empty '{}'; drop the braces or add `param: value` overrides");
  return (0 - 1);
}
  if (fb_expect(c, "RBRACE") < 0) {
  return (0 - 1);
}
  return fb_node2(c, N_STAGE, name_tok, source, params);
}

int32_t fb_tok_span_eq(Fb* c, int32_t a, int32_t b) {
  int32_t la = ((c[0]).te[a] - (c[0]).ts[a]);
  int32_t lb = ((c[0]).te[b] - (c[0]).ts[b]);
  if (la != lb) {
  return 0;
}
  int32_t i = 0;
  while (i < la) {
  if ((c[0]).src[((c[0]).ts[a] + i)] != (c[0]).src[((c[0]).ts[b] + i)]) {
  return 0;
}
  i = (i + 1);
}
  return 1;
}

int32_t fb_parse_fork(Fb* c, int32_t t, int32_t source) {
  int32_t nfields = 0;
  int32_t first_field = (c[0]).pos;
  while (fb_is_op(c, (c[0]).pos, OP_RBRACE) == 0) {
  int32_t ft = (c[0]).pos;
  if (fb_is_ident(c, ft) == 0) {
  fb_puts(fb_perr(c), "Expected a fork field name before '='");
  return (0 - 1);
}
  fb_advance(c);
  if (fb_is_op(c, (c[0]).pos, OP_COLON) == 1) {
  FbBuf* m = (FbBuf*)(fb_perr(c));
  fb_puts(m, "Fork block fields use '=' (a pipeline), not ':'; write `");
  fb_put_tok(m, c, ft);
  fb_puts(m, "  = source-pipeline`");
  return (0 - 1);
}
  if (fb_expect(c, "ASSIGN") < 0) {
  return (0 - 1);
}
  int32_t q = first_field;
  while (q < ft) {
  if (fb_is_ident(c, q) == 1 && fb_is_op(c, (q + 1), OP_ASSIGN) == 1 && fb_tok_span_eq(c, q, ft) == 1 && fb_fork_field_start(c, first_field, q) == 1) {
  FbBuf* m2 = (FbBuf*)(fb_perr(c));
  fb_puts(m2, "Duplicate fork field '");
  fb_put_tok(m2, c, ft);
  fb_puts(m2, "'");
  return (0 - 1);
}
  q = (q + 1);
}
  int32_t rhs = fb_parse_or(c);
  if (rhs < 0) {
  return (0 - 1);
}
  int32_t src = fb_node(c, N_OPAQUE, ft);
  int32_t k = (c[0]).nk[rhs];
  if (k != N_CALL && k != N_METHOD && k != N_VAR) {
  fb_puts(fb_serr(c), "Pipeline '|>' must be followed by a function call, method call, function name, declarative sort, or fork block (e.g. `x |> f()`, `x |> f`, `x |> sort by .score`, or `x |> Record { a = f, b = g }`)");
  return (0 - 1);
}
  if (fb_parse_pipeline(c, src) < 0) {
  return (0 - 1);
}
  nfields = (nfields + 1);
  if (fb_is_op(c, (c[0]).pos, OP_COMMA) == 1) {
  fb_advance(c);
}
}
  if (nfields == 0) {
  fb_puts(fb_perr(c), "Fork block must have at least one `field = …` branch");
  return (0 - 1);
}
  if (fb_expect(c, "RBRACE") < 0) {
  return (0 - 1);
}
  return fb_node2(c, N_FORK, t, source, (0 - 1));
}

int32_t fb_fork_field_start(Fb* c, int32_t first, int32_t q) {
  if (q == first) {
  return 1;
}
  int32_t depth = 0;
  int32_t i = first;
  int32_t at_start = 1;
  while (i < q) {
  if (fb_is_op(c, i, OP_LPAREN) == 1 || fb_is_op(c, i, OP_LBRACKET) == 1 || fb_is_op(c, i, OP_LBRACE) == 1) {
  depth = (depth + 1);
}
  if (fb_is_op(c, i, OP_RPAREN) == 1 || fb_is_op(c, i, OP_RBRACKET) == 1 || fb_is_op(c, i, OP_RBRACE) == 1) {
  depth = (depth - 1);
}
  at_start = 0;
  if (depth == 0 && fb_is_op(c, i, OP_COMMA) == 1) {
  at_start = 1;
}
  i = (i + 1);
}
  return at_start;
}

int32_t fb_parse_pipeline(Fb* c, int32_t left0) {
  int32_t left = left0;
  while (fb_is_op(c, (c[0]).pos, OP_PIPELINE) == 1) {
  fb_advance(c);
  int32_t t = (c[0]).pos;
  int32_t named = 0;
  if (fb_is_ident(c, t) == 1 && fb_is_op(c, fb_la(c), OP_LBRACE) == 1) {
  named = 1;
}
  if (fb_is_op(c, t, OP_LBRACE) == 1 || named == 1) {
  int32_t rec = (0 - 1);
  if (named == 1) {
  rec = t;
  fb_advance(c);
}
  if (fb_expect(c, "LBRACE") < 0) {
  return (0 - 1);
}
  if (fb_is_ident(c, (c[0]).pos) == 1 && fb_is_op(c, fb_la(c), OP_COLON) == 1) {
  if (rec < 0) {
  fb_puts(fb_perr(c), "an anonymous `|> { ... }` is a fork block and uses '=' branches; ':' parameter fields need a named flow stage");
  return (0 - 1);
}
  left = fb_parse_stage_params(c, rec, left);
  if (left < 0) {
  return (0 - 1);
}
} else {
  left = fb_parse_fork(c, t, left);
  if (left < 0) {
  return (0 - 1);
}
}
} else {
  int32_t rhs = fb_parse_or(c);
  if (rhs < 0) {
  return (0 - 1);
}
  int32_t rk = (c[0]).nk[rhs];
  if (rk == N_CALL) {
  int32_t args = fb_pipe_args(c, left, (c[0]).na[rhs]);
  if (args == (0 - 2)) {
  return (0 - 1);
}
  int32_t call = fb_node2(c, N_CALL, (c[0]).ntok[rhs], args, (0 - 1));
  (c[0]).nop[call] = (c[0]).nop[rhs];
  left = call;
} else {
  if (rk == N_METHOD) {
  int32_t margs = fb_pipe_args(c, left, (c[0]).nb[rhs]);
  if (margs == (0 - 2)) {
  return (0 - 1);
}
  left = fb_node2(c, N_METHOD, (c[0]).ntok[rhs], (c[0]).na[rhs], margs);
} else {
  if (rk == N_VAR) {
  (c[0]).nx[left] = (0 - 1);
  left = fb_node2(c, N_CALL, (c[0]).ntok[rhs], left, (0 - 1));
} else {
  fb_puts(fb_serr(c), "Pipeline '|>' must be followed by a function call, method call, function name, declarative sort, or fork block (e.g. `x |> f()`, `x |> f`, `x |> sort by .score`, or `x |> Record { a = f, b = g }`)");
  return (0 - 1);
}
}
}
}
}
  return left;
}

int32_t fb_add_member(Fb* c, int32_t f, int32_t kind, int32_t name, int32_t ty, int32_t init, int32_t line) {
  int32_t i = (c[0]).nmm;
  (c[0]).mm_flow[i] = f;
  (c[0]).mm_kind[i] = kind;
  (c[0]).mm_name[i] = name;
  (c[0]).mm_type[i] = ty;
  (c[0]).mm_init[i] = init;
  (c[0]).mm_line[i] = line;
  (c[0]).mm_synth[i] = 0;
  (c[0]).mm_params[i] = (0 - 1);
  (c[0]).mm_pipe_m[i] = (0 - 1);
  (c[0]).mm_pipe_p[i] = (0 - 1);
  (c[0]).nmm = (i + 1);
  return i;
}

void fb_add_conn(Fb* c, int32_t f, int32_t sm, int32_t sp, int32_t dm, int32_t dp, int32_t line) {
  int32_t i = (c[0]).ncn;
  (c[0]).cn_flow[i] = f;
  (c[0]).cn_sm[i] = sm;
  (c[0]).cn_sp[i] = sp;
  (c[0]).cn_dm[i] = dm;
  (c[0]).cn_dp[i] = dp;
  (c[0]).cn_line[i] = line;
  (c[0]).ncn = (i + 1);
}

void fb_add_name(Fb* c, int32_t kind, int32_t name) {
  int32_t i = (c[0]).nnames;
  (c[0]).nx_kind[i] = kind;
  (c[0]).nx_name[i] = name;
  (c[0]).nnames = (i + 1);
}

int32_t fb_has_name(Fb* c, int32_t kind, int32_t name) {
  int32_t i = 0;
  while (i < (c[0]).nnames) {
  if ((c[0]).nx_kind[i] == kind && fb_name_eq(c, (c[0]).nx_name[i], name) == 1) {
  return 1;
}
  i = (i + 1);
}
  return 0;
}

int64_t fb_pow10(int32_t k) {
  int64_t v = 1;
  int32_t i = 0;
  while (i < k) {
  v = (v * 10);
  i = (i + 1);
}
  return v;
}

int32_t fb_parse_duration(Fb* c, int32_t where_s, int64_t* ns, int32_t* text) {
  int32_t nt = (c[0]).pos;
  if ((c[0]).tk[nt] != TK_NUM) {
  FbBuf* m = (FbBuf*)(fb_perr(c));
  fb_puts(m, "Expected a duration in ");
  fb_puts(m, (const char*)(fb_s(c, where_s)));
  fb_puts(m, ", got ");
  fb_put_ttype(c, m, nt);
  fb_puts(fb_err_hint(c), "write a number with a time-unit suffix, e.g. '10 ms' (units: ns, us, ms, s, min)");
  return (0 - 1);
}
  fb_advance(c);
  int32_t st = (c[0]).pos;
  int32_t upow = (0 - 1);
  int64_t mult = 1;
  if (fb_is_ident(c, st) == 1) {
  if (fb_tok_is(c, st, "ns") == 1) {
  upow = 0;
}
  if (fb_tok_is(c, st, "us") == 1) {
  upow = 3;
}
  if (fb_tok_is(c, st, "ms") == 1) {
  upow = 6;
}
  if (fb_tok_is(c, st, "s") == 1) {
  upow = 9;
}
  if (fb_tok_is(c, st, "min") == 1) {
  upow = 10;
  mult = 6;
}
}
  if (upow < 0) {
  FbBuf* m2 = (FbBuf*)(fb_perr(c));
  fb_puts(m2, "Expected a time unit after '");
  fb_put_span(m2, (c[0]).src, (c[0]).ts[nt], (c[0]).te[nt]);
  fb_puts(m2, "' in ");
  fb_puts(m2, (const char*)(fb_s(c, where_s)));
  fb_puts(m2, ", got ");
  if (fb_is_ident(c, st) == 1) {
  fb_putc(m2, 39);
  fb_put_span(m2, (c[0]).src, (c[0]).ts[st], (c[0]).te[st]);
  fb_putc(m2, 39);
} else {
  fb_put_ttype(c, m2, st);
}
  fb_puts(fb_err_hint(c), "valid time units: ns, us, ms, s, min");
  return (0 - 1);
}
  fb_advance(c);
  FbBuf* tb = (FbBuf*)(fb_buf_new(32));
  fb_put_span(tb, (c[0]).src, (c[0]).ts[nt], (c[0]).te[nt]);
  fb_putc(tb, 32);
  fb_put_span(tb, (c[0]).src, (c[0]).ts[st], (c[0]).te[st]);
  text[0] = fb_intern_buf(c, tb);
  fb_buf_free(tb);
  uint8_t* p = (uint8_t*)((c[0]).src);
  int32_t s = (c[0]).ts[nt];
  int32_t e = (c[0]).te[nt];
  int64_t mant = 0;
  int32_t e10 = 0;
  int32_t over = 0;
  if ((e - s) > 2 && p[s] == 48 && p[(s + 1)] == 120) {
  int32_t h = (s + 2);
  while (h < e) {
  uint8_t ch = p[h];
  int64_t dv = 0;
  if (fb_is_digit(ch) == 1) {
  dv = (int64_t)((ch - 48));
}
  if (ch >= 97 && ch <= 102) {
  dv = (int64_t)((ch - 87));
}
  if (ch >= 65 && ch <= 70) {
  dv = (int64_t)((ch - 55));
}
  if (mant > ((FB_I64_MAX - dv) / 16)) {
  over = 1;
} else {
  mant = ((mant * 16) + dv);
}
  h = (h + 1);
}
} else {
  int32_t i = s;
  int32_t frac = 0;
  int32_t in_frac = 0;
  while (i < e && p[i] != 101 && p[i] != 69) {
  if (p[i] == 46) {
  in_frac = 1;
} else {
  int64_t dv2 = (int64_t)((p[i] - 48));
  if (mant > ((FB_I64_MAX - dv2) / 10)) {
  if (dv2 != 0) {
  over = 1;
}
  if (in_frac == 0) {
  e10 = (e10 + 1);
}
} else {
  mant = ((mant * 10) + dv2);
  if (in_frac == 1) {
  frac = (frac + 1);
}
}
}
  i = (i + 1);
}
  e10 = (e10 - frac);
  if (i < e) {
  i = (i + 1);
  int32_t neg = 0;
  if (p[i] == 45) {
  neg = 1;
  i = (i + 1);
} else {
  if (p[i] == 43) {
  i = (i + 1);
}
}
  int32_t ex = 0;
  while (i < e) {
  if (ex < 100000) {
  ex = ((ex * 10) + (int32_t)((p[i] - 48)));
}
  i = (i + 1);
}
  if (neg == 1) {
  e10 = (e10 - ex);
} else {
  e10 = (e10 + ex);
}
}
}
  while (mant != 0 && (mant % 10) == 0 && e10 < 0) {
  mant = (mant / 10);
  e10 = (e10 + 1);
}
  int32_t pw = (upow + e10);
  int32_t whole = 1;
  int64_t val = 0;
  if (mant == 0) {
  val = 0;
} else {
  if (mant > (FB_I64_MAX / mult)) {
  over = 1;
} else {
  int64_t x = (mant * mult);
  if (pw < 0) {
  if (pw < (0 - 18)) {
  whole = 0;
} else {
  int64_t d = fb_pow10((0 - pw));
  if ((x % d) != 0) {
  whole = 0;
} else {
  x = (x / d);
}
}
} else {
  while (pw > 0 && over == 0) {
  if (x > (FB_I64_MAX / 10)) {
  over = 1;
} else {
  x = (x * 10);
}
  pw = (pw - 1);
}
}
  val = x;
}
}
  if (whole == 0) {
  FbBuf* m3 = (FbBuf*)(fb_perr(c));
  fb_puts(m3, "Duration '");
  fb_puts(m3, (const char*)(fb_s(c, text[0])));
  fb_puts(m3, "' in ");
  fb_puts(m3, (const char*)(fb_s(c, where_s)));
  fb_puts(m3, " is not a whole number of nanoseconds; time is not silently rounded");
  fb_puts(fb_err_hint(c), "use a finer unit, e.g. '500 us' instead of '0.5 ms'");
  return (0 - 1);
}
  if (over == 1) {
  FbBuf* m4 = (FbBuf*)(fb_perr(c));
  fb_puts(m4, "Duration '");
  fb_puts(m4, (const char*)(fb_s(c, text[0])));
  fb_puts(m4, "' in ");
  fb_puts(m4, (const char*)(fb_s(c, where_s)));
  fb_puts(m4, " overflows the i64 nanosecond range");
  return (0 - 1);
}
  ns[0] = val;
  return 0;
}

void fb_put_tok(FbBuf* b, Fb* c, int32_t t) {
  fb_put_span(b, (c[0]).src, (c[0]).ts[t], (c[0]).te[t]);
}

void fb_put_fname(FbBuf* b, Fb* c, int32_t f) {
  fb_puts(b, (const char*)(fb_s(c, (c[0]).f_name[f])));
}

int32_t fb_parse_becomes_body(Fb* c, int32_t f, int32_t kind, int32_t owner, const char* word, const char* what) {
  if (fb_expect(c, "LBRACE") < 0) {
  return (0 - 1);
}
  while (fb_is_op(c, (c[0]).pos, OP_RBRACE) == 0) {
  if (fb_at_eof(c) == 1) {
  FbBuf* m = (FbBuf*)(fb_perr(c));
  fb_puts(m, "Unterminated '");
  fb_puts(m, word);
  fb_puts(m, "' body in flow '");
  fb_put_fname(m, c, f);
  fb_puts(m, "': expected '}' before end of file");
  return (0 - 1);
}
  int32_t st = (c[0]).pos;
  int32_t la = fb_la(c);
  if (fb_is_ident(c, st) == 0 || fb_is_word(c, la, "becomes") == 0) {
  FbBuf* m2 = (FbBuf*)(fb_perr(c));
  fb_puts(m2, "Unexpected statement in '");
  fb_puts(m2, word);
  fb_puts(m2, "' body of flow '");
  fb_put_fname(m2, c, f);
  fb_puts(m2, "'");
  FbBuf* h = (FbBuf*)(fb_err_hint(c));
  fb_puts(h, "'");
  fb_puts(h, word);
  fb_puts(h, "' bodies contain ");
  fb_puts(h, what);
  fb_puts(h, " in this version: 'x becomes expr'");
  return (0 - 1);
}
  fb_advance(c);
  fb_advance(c);
  int32_t rhs_s = (c[0]).pos;
  int32_t rhs = fb_parse_expr(c);
  if (rhs < 0) {
  return (0 - 1);
}
  int32_t i = (c[0]).nbc;
  (c[0]).bc_kind[i] = kind;
  (c[0]).bc_owner[i] = owner;
  (c[0]).bc_target[i] = fb_tok_str(c, st);
  (c[0]).bc_expr[i] = fb_wrap_top(c, rhs, rhs_s);
  (c[0]).bc_line[i] = (c[0]).tl[st];
  (c[0]).nbc = (i + 1);
}
  return fb_expect(c, "RBRACE");
}

int32_t fb_wrap_top(Fb* c, int32_t root, int32_t start_tok) {
  (c[0]).nfs[root] = start_tok;
  (c[0]).nfe[root] = (c[0]).pos;
  return root;
}

int32_t fb_source_between(Fb* c, int32_t st, int32_t et) {
  uint8_t* p = (uint8_t*)((c[0]).src);
  FbBuf* b = (FbBuf*)(fb_buf_new(64));
  int32_t sl = (c[0]).tl[st];
  int32_t el = (c[0]).tl[et];
  int32_t s_off = fb_col_offset(c, sl, (c[0]).tc[st]);
  int32_t e_off = fb_col_offset(c, el, (c[0]).tc[et]);
  if (sl == el) {
  fb_put_stripped(b, p, s_off, e_off);
} else {
  int32_t first = 1;
  int32_t l0e = fb_line_end(c, s_off);
  first = fb_put_part(b, p, s_off, l0e, first);
  int32_t ln = (sl + 1);
  while (ln < el) {
  int32_t ls = fb_line_start(c, ln);
  if (ls >= 0) {
  first = fb_put_part(b, p, ls, fb_line_end(c, ls), first);
}
  ln = (ln + 1);
}
  int32_t ls2 = fb_line_start(c, el);
  if (ls2 >= 0) {
  first = fb_put_part(b, p, ls2, e_off, first);
}
}
  int32_t out = fb_intern_buf(c, b);
  fb_buf_free(b);
  return out;
}

int32_t fb_line_start(Fb* c, int32_t ln) {
  int32_t line = 1;
  int32_t i = 0;
  if (ln == 1) {
  return 0;
}
  while (i < (c[0]).n) {
  if ((c[0]).src[i] == 10) {
  line = (line + 1);
  if (line == ln) {
  return (i + 1);
}
}
  i = (i + 1);
}
  return (0 - 1);
}

int32_t fb_line_end(Fb* c, int32_t off) {
  int32_t i = off;
  while (i < (c[0]).n && (c[0]).src[i] != 10) {
  i = (i + 1);
}
  return i;
}

int32_t fb_col_offset(Fb* c, int32_t ln, int32_t col) {
  int32_t ls = fb_line_start(c, ln);
  if (ls < 0) {
  return (c[0]).n;
}
  int32_t le = fb_line_end(c, ls);
  int32_t want = (col - 1);
  if (want < 0) {
  want = 0;
}
  int32_t i = ls;
  int32_t k = 0;
  while (i < le && k < want) {
  i = (i + 1);
  while (i < le && (c[0]).src[i] >= 128 && (c[0]).src[i] < 192) {
  i = (i + 1);
}
  k = (k + 1);
}
  return i;
}

void fb_put_stripped(FbBuf* b, uint8_t* p, int32_t s, int32_t e) {
  int32_t a = s;
  int32_t z = e;
  while (a < z && fb_is_space(p[a]) == 1) {
  a = (a + 1);
}
  while (z > a && fb_is_space(p[(z - 1)]) == 1) {
  z = (z - 1);
}
  fb_put_span(b, p, a, z);
}

int32_t fb_put_part(FbBuf* b, uint8_t* p, int32_t s, int32_t e, int32_t first) {
  int32_t a = s;
  int32_t z = e;
  while (a < z && fb_is_space(p[a]) == 1) {
  a = (a + 1);
}
  while (z > a && fb_is_space(p[(z - 1)]) == 1) {
  z = (z - 1);
}
  if (a >= z) {
  return first;
}
  if (first == 0) {
  fb_putc(b, 32);
}
  fb_put_span(b, p, a, z);
  return 0;
}

int32_t fb_parse_invariant(Fb* c, int32_t f, int32_t kind, const char* word) {
  fb_advance(c);
  if (fb_expect(c, "LBRACE") < 0) {
  return (0 - 1);
}
  int32_t count = 0;
  while (fb_is_op(c, (c[0]).pos, OP_RBRACE) == 0) {
  if (fb_at_eof(c) == 1) {
  FbBuf* m = (FbBuf*)(fb_perr(c));
  fb_puts(m, "Unterminated '");
  fb_puts(m, word);
  fb_puts(m, "' body in flow '");
  fb_put_fname(m, c, f);
  fb_puts(m, "': expected '}' before end of file");
  return (0 - 1);
}
  int32_t st = (c[0]).pos;
  int32_t ex = fb_parse_expr(c);
  if (ex < 0) {
  return (0 - 1);
}
  int32_t i = (c[0]).niv;
  (c[0]).iv_flow[i] = f;
  (c[0]).iv_kind[i] = kind;
  (c[0]).iv_expr[i] = fb_wrap_top(c, ex, st);
  (c[0]).iv_line[i] = (c[0]).tl[st];
  (c[0]).iv_text[i] = fb_source_between(c, st, (c[0]).pos);
  (c[0]).niv = (i + 1);
  count = (count + 1);
}
  if (fb_expect(c, "RBRACE") < 0) {
  return (0 - 1);
}
  if (count == 0) {
  FbBuf* m2 = (FbBuf*)(fb_perr(c));
  fb_puts(m2, "'");
  fb_puts(m2, word);
  fb_puts(m2, "' block in flow '");
  fb_put_fname(m2, c, f);
  fb_puts(m2, "' needs at least one boolean expression");
  FbBuf* h = (FbBuf*)(fb_err_hint(c));
  fb_puts(h, "write '");
  fb_puts(h, word);
  fb_puts(h, " { x < 1.0 }' or remove the block");
  return (0 - 1);
}
  return 0;
}

int32_t fb_parse_recognize(Fb* c, int32_t f) {
  int32_t rt = (c[0]).pos;
  fb_advance(c);
  if (fb_expect(c, "LBRACE") < 0) {
  return (0 - 1);
}
  int32_t first = (c[0]).nrc;
  while (fb_is_op(c, (c[0]).pos, OP_RBRACE) == 0) {
  if (fb_at_eof(c) == 1) {
  FbBuf* m = (FbBuf*)(fb_perr(c));
  fb_puts(m, "Unterminated 'recognize' block in flow '");
  fb_put_fname(m, c, f);
  fb_puts(m, "': expected '}' before end of file");
  return (0 - 1);
}
  if (fb_is_op(c, (c[0]).pos, OP_COMMA) == 1) {
  fb_advance(c);
} else {
  int32_t dt = fb_expect(c, "IDENTIFIER");
  if (dt < 0) {
  return (0 - 1);
}
  int32_t dn = fb_tok_str(c, dt);
  int32_t k = first;
  while (k < (c[0]).nrc) {
  if (fb_name_eq(c, (c[0]).rc_name[k], dn) == 1) {
  FbBuf* m2 = (FbBuf*)(fb_perr(c));
  fb_puts(m2, "recognition domain '");
  fb_puts(m2, (const char*)(fb_s(c, dn)));
  fb_puts(m2, "' appears twice in flow '");
  fb_put_fname(m2, c, f);
  fb_puts(m2, "'");
  fb_puts(fb_err_hint(c), "list each recognition domain once");
  return (0 - 1);
}
  k = (k + 1);
}
  int32_t i = (c[0]).nrc;
  (c[0]).rc_flow[i] = f;
  (c[0]).rc_name[i] = dn;
  (c[0]).nrc = (i + 1);
  if (fb_is_op(c, (c[0]).pos, OP_COMMA) == 1) {
  fb_advance(c);
}
}
}
  if (fb_expect(c, "RBRACE") < 0) {
  return (0 - 1);
}
  if ((c[0]).nrc == first) {
  FbBuf* m3 = (FbBuf*)(fb_perr(c));
  fb_puts(m3, "'recognize' block in flow '");
  fb_put_fname(m3, c, f);
  fb_puts(m3, "' needs at least one domain");
  fb_puts(fb_err_hint(c), "write 'recognize { numerical realtime causal safety memory }'");
  return (0 - 1);
}
  (c[0]).f_rec[f] = 1;
  (c[0]).f_rec_line[f] = (c[0]).tl[rt];
  return 0;
}

int32_t fb_parse_connect(Fb* c, int32_t f) {
  fb_advance(c);
  if (fb_expect(c, "LBRACE") < 0) {
  return (0 - 1);
}
  while (fb_is_op(c, (c[0]).pos, OP_RBRACE) == 0) {
  if (fb_at_eof(c) == 1) {
  FbBuf* m = (FbBuf*)(fb_perr(c));
  fb_puts(m, "Unterminated 'connect' body in flow '");
  fb_put_fname(m, c, f);
  fb_puts(m, "': expected '}' before end of file");
  return (0 - 1);
}
  int32_t st = (c[0]).pos;
  int32_t first = fb_expect(c, "IDENTIFIER");
  if (first < 0) {
  return (0 - 1);
}
  int32_t sm = fb_intern(c, "");
  int32_t sp = fb_tok_str(c, first);
  if (fb_is_op(c, (c[0]).pos, OP_DOT) == 1) {
  fb_advance(c);
  int32_t pt = fb_expect(c, "IDENTIFIER");
  if (pt < 0) {
  return (0 - 1);
}
  sm = fb_tok_str(c, first);
  sp = fb_tok_str(c, pt);
}
  if (fb_expect(c, "ARROW") < 0) {
  return (0 - 1);
}
  int32_t dmt = fb_expect(c, "IDENTIFIER");
  if (dmt < 0) {
  return (0 - 1);
}
  if (fb_expect(c, "DOT") < 0) {
  return (0 - 1);
}
  int32_t dpt = fb_expect(c, "IDENTIFIER");
  if (dpt < 0) {
  return (0 - 1);
}
  fb_add_conn(c, f, sm, sp, fb_tok_str(c, dmt), fb_tok_str(c, dpt), (c[0]).tl[st]);
}
  return fb_expect(c, "RBRACE");
}

int32_t fb_parse_solver(Fb* c, int32_t f) {
  int32_t st = (c[0]).pos;
  fb_advance(c);
  if (fb_expect(c, "LBRACE") < 0) {
  return (0 - 1);
}
  int32_t have_dt = 0;
  int32_t method = (0 - 1);
  int64_t* nsbox = (int64_t*)((int64_t*)(malloc(8)));
  int32_t* txbox = (int32_t*)((int32_t*)(malloc(4)));
  FbBuf* wb = (FbBuf*)(fb_buf_new(64));
  fb_puts(wb, "the solver dt of flow '");
  fb_put_fname(wb, c, f);
  fb_puts(wb, "'");
  int32_t where_s = fb_intern_buf(c, wb);
  fb_buf_free(wb);
  int32_t rc = 0;
  while (rc == 0 && fb_is_op(c, (c[0]).pos, OP_RBRACE) == 0) {
  if (fb_at_eof(c) == 1) {
  FbBuf* m = (FbBuf*)(fb_perr(c));
  fb_puts(m, "Unterminated 'solver' block in flow '");
  fb_put_fname(m, c, f);
  fb_puts(m, "': expected '}' before end of file");
  rc = (0 - 1);
} else {
  int32_t t = (c[0]).pos;
  if (fb_is_word(c, t, "dt") == 1) {
  if (have_dt == 1) {
  FbBuf* m2 = (FbBuf*)(fb_perr(c));
  fb_puts(m2, "'solver' block in flow '");
  fb_put_fname(m2, c, f);
  fb_puts(m2, "' sets 'dt' twice");
  rc = (0 - 1);
} else {
  fb_advance(c);
  if (fb_parse_duration(c, where_s, nsbox, txbox) < 0) {
  rc = (0 - 1);
} else {
  have_dt = 1;
  (c[0]).f_dt_ns[f] = nsbox[0];
  (c[0]).f_dt_text[f] = txbox[0];
}
}
} else {
  if (fb_is_word(c, t, "method") == 1) {
  if (method >= 0) {
  FbBuf* m3 = (FbBuf*)(fb_perr(c));
  fb_puts(m3, "'solver' block in flow '");
  fb_put_fname(m3, c, f);
  fb_puts(m3, "' sets 'method' twice");
  rc = (0 - 1);
} else {
  fb_advance(c);
  int32_t mt = fb_expect(c, "IDENTIFIER");
  if (mt < 0) {
  rc = (0 - 1);
} else {
  method = fb_tok_str(c, mt);
}
}
} else {
  FbBuf* m4 = (FbBuf*)(fb_perr(c));
  fb_puts(m4, "Unexpected item in 'solver' block of flow '");
  fb_put_fname(m4, c, f);
  fb_puts(m4, "'");
  fb_puts(fb_err_hint(c), "solver blocks contain 'dt <duration>' and 'method euler' or 'method rk4'");
  rc = (0 - 1);
}
}
}
}
  free((uint8_t*)(nsbox));
  free((uint8_t*)(txbox));
  if (rc < 0) {
  return (0 - 1);
}
  if (fb_expect(c, "RBRACE") < 0) {
  return (0 - 1);
}
  if (have_dt == 0) {
  FbBuf* m5 = (FbBuf*)(fb_perr(c));
  fb_puts(m5, "'solver' block in flow '");
  fb_put_fname(m5, c, f);
  fb_puts(m5, "' needs a 'dt' setting");
  fb_puts(fb_err_hint(c), "write 'solver { dt 1 ms }'");
  return (0 - 1);
}
  if (method < 0) {
  method = fb_intern(c, "euler");
}
  (c[0]).f_solver[f] = 1;
  (c[0]).f_method[f] = method;
  (c[0]).f_solver_line[f] = (c[0]).tl[st];
  return 0;
}

int32_t fb_is_section_word(Fb* c, int32_t t) {
  if (fb_tok_is(c, t, "state") == 1 || fb_tok_is(c, t, "input") == 1) {
  return 1;
}
  if (fb_tok_is(c, t, "output") == 1 || fb_tok_is(c, t, "param") == 1) {
  return 1;
}
  return 0;
}

int32_t fb_parse_flow_item(Fb* c, int32_t f) {
  int32_t t = (c[0]).pos;
  int32_t la = fb_la(c);
  int32_t tid = fb_is_ident(c, t);
  if (tid == 1 && fb_is_section_word(c, t) == 1 && fb_is_ident(c, la) == 1) {
  fb_advance(c);
  int32_t nt = fb_expect(c, "IDENTIFIER");
  if (nt < 0) {
  return (0 - 1);
}
  if (fb_expect(c, "COLON") < 0) {
  return (0 - 1);
}
  int32_t ty = fb_parse_type(c);
  if (ty < 0) {
  return (0 - 1);
}
  int32_t init = (0 - 1);
  if (fb_is_op(c, (c[0]).pos, OP_ASSIGN) == 1) {
  fb_advance(c);
  int32_t is = (c[0]).pos;
  int32_t ie = fb_parse_expr(c);
  if (ie < 0) {
  return (0 - 1);
}
  init = fb_wrap_top(c, ie, is);
}
  int32_t kind = MK_STATE;
  if (fb_tok_is(c, t, "input") == 1) {
  kind = MK_INPUT;
}
  if (fb_tok_is(c, t, "output") == 1) {
  kind = MK_OUTPUT;
}
  if (fb_tok_is(c, t, "param") == 1) {
  kind = MK_PARAM;
}
  if (kind == MK_INPUT && init >= 0) {
  FbBuf* m = (FbBuf*)(fb_perr(c));
  fb_puts(m, "input '");
  fb_put_tok(m, c, nt);
  fb_puts(m, "' in flow '");
  fb_put_fname(m, c, f);
  fb_puts(m, "' cannot have an initializer; inputs are written by the embedder");
  fb_puts(fb_err_hint(c), "remove the '= ...' part");
  return (0 - 1);
}
  fb_add_member(c, f, kind, fb_tok_str(c, nt), ty, init, (c[0]).tl[t]);
  return 0;
}
  if (tid == 1 && fb_is_word(c, la, "evolves") == 1) {
  fb_advance(c);
  fb_advance(c);
  if (fb_expect(c, "AS") < 0) {
  return (0 - 1);
}
  int32_t rs = (c[0]).pos;
  int32_t rhs = fb_parse_expr(c);
  if (rhs < 0) {
  return (0 - 1);
}
  int32_t i = (c[0]).nev;
  (c[0]).ev_flow[i] = f;
  (c[0]).ev_target[i] = fb_tok_str(c, t);
  (c[0]).ev_expr[i] = fb_wrap_top(c, rhs, rs);
  (c[0]).ev_line[i] = (c[0]).tl[t];
  (c[0]).nev = (i + 1);
  return 0;
}
  if (tid == 1 && fb_tok_is(c, t, "when") == 1 && fb_is_ident(c, la) == 1 && fb_is_word(c, fb_la2(c), "reaches") == 1) {
  fb_advance(c);
  int32_t gt = fb_expect(c, "IDENTIFIER");
  if (gt < 0) {
  return (0 - 1);
}
  fb_advance(c);
  int32_t ts0 = (c[0]).pos;
  int32_t thr = fb_parse_expr(c);
  if (thr < 0) {
  return (0 - 1);
}
  int32_t w = (c[0]).nwh;
  (c[0]).wh_flow[w] = f;
  (c[0]).wh_target[w] = fb_tok_str(c, gt);
  (c[0]).wh_thr[w] = fb_wrap_top(c, thr, ts0);
  (c[0]).wh_line[w] = (c[0]).tl[t];
  (c[0]).nwh = (w + 1);
  return fb_parse_becomes_body(c, f, 1, w, "when", "resets");
}
  if (tid == 1 && fb_tok_is(c, t, "every") == 1 && (c[0]).tk[la] == TK_NUM) {
  fb_advance(c);
  FbBuf* wb = (FbBuf*)(fb_buf_new(64));
  fb_puts(wb, "the 'every' period of flow '");
  fb_put_fname(wb, c, f);
  fb_puts(wb, "'");
  int32_t where_s = fb_intern_buf(c, wb);
  fb_buf_free(wb);
  int64_t* nsbox = (int64_t*)((int64_t*)(malloc(8)));
  int32_t* txbox = (int32_t*)((int32_t*)(malloc(4)));
  int32_t drc = fb_parse_duration(c, where_s, nsbox, txbox);
  int32_t ev = (c[0]).ney;
  if (drc == 0) {
  (c[0]).ey_flow[ev] = f;
  (c[0]).ey_ns[ev] = nsbox[0];
  (c[0]).ey_text[ev] = txbox[0];
  (c[0]).ey_line[ev] = (c[0]).tl[t];
  (c[0]).ney = (ev + 1);
}
  free((uint8_t*)(nsbox));
  free((uint8_t*)(txbox));
  if (drc < 0) {
  return (0 - 1);
}
  return fb_parse_becomes_body(c, f, 2, ev, "every", "discrete updates");
}
  int32_t la_brace = fb_is_op(c, la, OP_LBRACE);
  if (tid == 1 && la_brace == 1 && fb_tok_is(c, t, "solver") == 1) {
  if ((c[0]).f_solver[f] == 1) {
  FbBuf* m2 = (FbBuf*)(fb_perr(c));
  fb_puts(m2, "flow '");
  fb_put_fname(m2, c, f);
  fb_puts(m2, "' has two 'solver' blocks; a flow pins at most one default step");
  fb_puts(fb_err_hint(c), "merge the settings into one solver block");
  return (0 - 1);
}
  return fb_parse_solver(c, f);
}
  if (tid == 1 && la_brace == 1 && fb_tok_is(c, t, "always") == 1) {
  return fb_parse_invariant(c, f, 1, "always");
}
  if (tid == 1 && la_brace == 1 && fb_tok_is(c, t, "never") == 1) {
  return fb_parse_invariant(c, f, 2, "never");
}
  if (tid == 1 && la_brace == 1 && fb_tok_is(c, t, "recognize") == 1) {
  if ((c[0]).f_rec[f] == 1) {
  FbBuf* m3 = (FbBuf*)(fb_perr(c));
  fb_puts(m3, "flow '");
  fb_put_fname(m3, c, f);
  fb_puts(m3, "' has two 'recognize' blocks");
  fb_puts(fb_err_hint(c), "merge the domains into one recognize block");
  return (0 - 1);
}
  return fb_parse_recognize(c, f);
}
  if (tid == 1 && la_brace == 1 && fb_tok_is(c, t, "connect") == 1) {
  return fb_parse_connect(c, f);
}
  if (tid == 1 && fb_is_section_word(c, t) == 0 && fb_is_op(c, la, OP_COLON) == 1) {
  fb_advance(c);
  fb_advance(c);
  int32_t cty = fb_parse_type(c);
  if (cty < 0) {
  return (0 - 1);
}
  if (fb_is_op(c, (c[0]).pos, OP_ASSIGN) == 1) {
  FbBuf* m4 = (FbBuf*)(fb_perr(c));
  fb_puts(m4, "nested flow member '");
  fb_put_tok(m4, c, t);
  fb_puts(m4, "' in flow '");
  fb_put_fname(m4, c, f);
  fb_puts(m4, "' cannot have an initializer; children are constructed by ");
  fb_puts(m4, (const char*)(fb_s(c, cty)));
  fb_puts(m4, "_new inside the parent");
  fb_puts(fb_err_hint(c), "remove the '= ...' part");
  return (0 - 1);
}
  fb_add_member(c, f, MK_CHILD, fb_tok_str(c, t), cty, (0 - 1), (c[0]).tl[t]);
  return 0;
}
  FbBuf* m5 = (FbBuf*)(fb_perr(c));
  fb_puts(m5, "Unexpected item in flow '");
  fb_put_fname(m5, c, f);
  fb_puts(m5, "' body");
  fb_puts(fb_err_hint(c), "flow bodies contain member declarations ('state|input|output|param name : type [= expr]'), nested flow members ('plant : Motor'), dynamics ('x evolves as expr'), events ('when x reaches expr { x becomes expr }'), discrete blocks ('every 10 ms { x becomes expr }'), composition ('connect { a.out -> b.in }'), invariants ('always { expr }' / 'never { expr }'), semantic contracts ('recognize { numerical realtime }'), and settings ('solver { dt 1 ms }')");
  return (0 - 1);
}

int32_t fb_parse_flow(Fb* c, int32_t f) {
  int32_t ft = (c[0]).pos;
  (c[0]).f_start[f] = (c[0]).ts[ft];
  (c[0]).f_line[f] = (c[0]).tl[ft];
  fb_advance(c);
  int32_t nt = fb_expect(c, "IDENTIFIER");
  if (nt < 0) {
  return (0 - 1);
}
  (c[0]).f_name[f] = fb_tok_str(c, nt);
  if (fb_expect(c, "LBRACE") < 0) {
  return (0 - 1);
}
  while (fb_is_op(c, (c[0]).pos, OP_RBRACE) == 0) {
  if (fb_at_eof(c) == 1) {
  FbBuf* m = (FbBuf*)(fb_perr(c));
  fb_puts(m, "Unterminated flow '");
  fb_put_fname(m, c, f);
  fb_puts(m, "': expected '}' before end of file");
  return (0 - 1);
}
  if (fb_parse_flow_item(c, f) < 0) {
  return (0 - 1);
}
}
  int32_t rb = fb_expect(c, "RBRACE");
  if (rb < 0) {
  return (0 - 1);
}
  (c[0]).f_end[f] = (c[0]).te[rb];
  return 0;
}

int32_t fb_find_flow(Fb* c, int32_t name) {
  int32_t f = 0;
  while (f < (c[0]).nf) {
  if (fb_name_eq(c, (c[0]).f_name[f], name) == 1) {
  return f;
}
  f = (f + 1);
}
  return (0 - 1);
}

int32_t fb_find_flow_str(Fb* c, uint8_t* name) {
  int32_t f = 0;
  while (f < (c[0]).nf) {
  if (strcmp((const char*)(fb_s(c, (c[0]).f_name[f])), (const char*)(name)) == 0) {
  return f;
}
  f = (f + 1);
}
  return (0 - 1);
}

int32_t fb_find_member(Fb* c, int32_t f, int32_t kind, int32_t name) {
  int32_t i = 0;
  while (i < (c[0]).nmm) {
  if ((c[0]).mm_flow[i] == f && (c[0]).mm_kind[i] == kind && fb_name_eq(c, (c[0]).mm_name[i], name) == 1) {
  return i;
}
  i = (i + 1);
}
  return (0 - 1);
}

int32_t fb_lookup_port(Fb* c, int32_t f, int32_t name) {
  int32_t s = fb_find_member(c, f, MK_STATE, name);
  if (s >= 0) {
  return s;
}
  int32_t i = fb_find_member(c, f, MK_INPUT, name);
  if (i >= 0) {
  return i;
}
  int32_t o = fb_find_member(c, f, MK_OUTPUT, name);
  if (o >= 0) {
  return o;
}
  return fb_find_member(c, f, MK_PARAM, name);
}

const char* fb_kind_word(int32_t k) {
  if (k == MK_STATE) {
  return "state";
}
  if (k == MK_INPUT) {
  return "input";
}
  if (k == MK_OUTPUT) {
  return "output";
}
  if (k == MK_PARAM) {
  return "param";
}
  return "child";
}

int32_t fb_count_members(Fb* c, int32_t f, int32_t kind) {
  int32_t n = 0;
  int32_t i = 0;
  while (i < (c[0]).nmm) {
  if ((c[0]).mm_flow[i] == f && (c[0]).mm_kind[i] == kind) {
  n = (n + 1);
}
  i = (i + 1);
}
  return n;
}

int32_t fb_nth_member(Fb* c, int32_t f, int32_t kind, int32_t k) {
  int32_t n = 0;
  int32_t i = 0;
  while (i < (c[0]).nmm) {
  if ((c[0]).mm_flow[i] == f && (c[0]).mm_kind[i] == kind) {
  if (n == k) {
  return i;
}
  n = (n + 1);
}
  i = (i + 1);
}
  return (0 - 1);
}

int32_t fb_evolve_of(Fb* c, int32_t f, int32_t name) {
  int32_t i = 0;
  while (i < (c[0]).nev) {
  if ((c[0]).ev_flow[i] == f && fb_name_eq(c, (c[0]).ev_target[i], name) == 1) {
  return i;
}
  i = (i + 1);
}
  return (0 - 1);
}

uint8_t* fb_tok_name(Fb* c, int32_t node) {
  return fb_s(c, fb_tok_str(c, (c[0]).ntok[node]));
}

int32_t fb_call_name(Fb* c, int32_t node) {
  if ((c[0]).ntok[node] < 0) {
  return fb_intern(c, "__flow_dbg");
}
  return fb_tok_str(c, (c[0]).ntok[node]);
}

int32_t fb_children(Fb* c, int32_t x, int32_t* out) {
  int32_t k = (c[0]).nk[x];
  if (k == N_BIN) {
  out[0] = (c[0]).na[x];
  out[1] = (c[0]).nb[x];
  return 2;
}
  if (k == N_UN || k == N_CAST || k == N_FIELD || k == N_TRY) {
  out[0] = (c[0]).na[x];
  return 1;
}
  if (k == N_INDEX) {
  out[0] = (c[0]).na[x];
  out[1] = (c[0]).nb[x];
  return 2;
}
  if (k == N_ARRAY || k == N_VEC || k == N_STRUCT) {
  int32_t n = 0;
  int32_t e = (c[0]).na[x];
  while (e >= 0 && n < 64) {
  if (k == N_STRUCT) {
  out[n] = (c[0]).na[e];
} else {
  out[n] = e;
}
  n = (n + 1);
  e = (c[0]).nx[e];
}
  return n;
}
  return 0;
}

int32_t fb_is_pure_math(uint8_t* name) {
  const char* s = (const char*)(name);
  if (strcmp(s, "sin") == 0 || strcmp(s, "cos") == 0 || strcmp(s, "tan") == 0) {
  return 1;
}
  if (strcmp(s, "asin") == 0 || strcmp(s, "acos") == 0 || strcmp(s, "atan") == 0) {
  return 1;
}
  if (strcmp(s, "atan2") == 0 || strcmp(s, "sinh") == 0 || strcmp(s, "cosh") == 0) {
  return 1;
}
  if (strcmp(s, "tanh") == 0 || strcmp(s, "asinh") == 0 || strcmp(s, "acosh") == 0) {
  return 1;
}
  if (strcmp(s, "atanh") == 0 || strcmp(s, "sqrt") == 0 || strcmp(s, "cbrt") == 0) {
  return 1;
}
  if (strcmp(s, "pow") == 0 || strcmp(s, "exp") == 0 || strcmp(s, "exp2") == 0) {
  return 1;
}
  if (strcmp(s, "log") == 0 || strcmp(s, "log2") == 0 || strcmp(s, "log10") == 0) {
  return 1;
}
  if (strcmp(s, "fabs") == 0 || strcmp(s, "abs") == 0 || strcmp(s, "floor") == 0) {
  return 1;
}
  if (strcmp(s, "ceil") == 0 || strcmp(s, "round") == 0 || strcmp(s, "fmod") == 0) {
  return 1;
}
  if (strcmp(s, "fmin") == 0 || strcmp(s, "fmax") == 0 || strcmp(s, "hypot") == 0) {
  return 1;
}
  return 0;
}

int32_t fb_check_pure(Fb* c, int32_t x, int32_t f, int32_t where_s, int32_t line) {
  if (x < 0) {
  return 0;
}
  int32_t k = (c[0]).nk[x];
  if (k == N_EFFECT) {
  FbBuf* m = (FbBuf*)(fb_verr(c, line));
  fb_puts(m, "effect call in ");
  fb_puts(m, (const char*)(fb_s(c, where_s)));
  fb_puts(m, " of flow '");
  fb_put_fname(m, c, f);
  fb_puts(m, "'; dynamics expressions must be pure");
  fb_puts(fb_err_hint(c), "lift effectful work out of the flow body");
  return (0 - 1);
}
  if (k == N_METHOD) {
  FbBuf* m2 = (FbBuf*)(fb_verr(c, line));
  fb_puts(m2, "method call in ");
  fb_puts(m2, (const char*)(fb_s(c, where_s)));
  fb_puts(m2, " of flow '");
  fb_put_fname(m2, c, f);
  fb_puts(m2, "'; dynamics expressions must be pure plain calls in this version");
  return (0 - 1);
}
  if (k == N_LAMBDA) {
  FbBuf* m3 = (FbBuf*)(fb_verr(c, line));
  fb_puts(m3, "lambda in ");
  fb_puts(m3, (const char*)(fb_s(c, where_s)));
  fb_puts(m3, " of flow '");
  fb_put_fname(m3, c, f);
  fb_puts(m3, "' is not supported");
  return (0 - 1);
}
  if (k == N_CALL) {
  int32_t nm = fb_call_name(c, x);
  if (fb_is_pure_math(fb_s(c, nm)) == 0 && fb_has_name(c, NX_LOCAL_FN, nm) == 0) {
  FbBuf* m4 = (FbBuf*)(fb_verr(c, line));
  fb_puts(m4, "call to '");
  fb_puts(m4, (const char*)(fb_s(c, nm)));
  fb_puts(m4, "' in ");
  fb_puts(m4, (const char*)(fb_s(c, where_s)));
  fb_puts(m4, " of flow '");
  fb_put_fname(m4, c, f);
  fb_puts(m4, "' cannot be proven pure; only C math functions and non-extern functions defined in the same file are allowed here (v1)");
  return (0 - 1);
}
  int32_t a = (c[0]).na[x];
  while (a >= 0) {
  if (fb_check_pure(c, a, f, where_s, line) < 0) {
  return (0 - 1);
}
  a = (c[0]).nx[a];
}
  return 0;
}
  int32_t* kids = (int32_t*)((int32_t*)(malloc(256)));
  int32_t nk = fb_children(c, x, kids);
  int32_t i = 0;
  while (i < nk) {
  if (fb_check_pure(c, kids[i], f, where_s, line) < 0) {
  free((uint8_t*)(kids));
  return (0 - 1);
}
  i = (i + 1);
}
  free((uint8_t*)(kids));
  return 0;
}

int32_t fb_check_pure_s(Fb* c, int32_t x, int32_t f, const char* where_s, int32_t line) {
  return fb_check_pure(c, x, f, fb_intern(c, where_s), line);
}

int32_t fb_where(Fb* c, const char* pre, int32_t name, const char* post) {
  FbBuf* b = (FbBuf*)(fb_buf_new(64));
  fb_puts(b, pre);
  fb_puts(b, (const char*)(fb_s(c, name)));
  fb_puts(b, post);
  int32_t out = fb_intern_buf(c, b);
  fb_buf_free(b);
  return out;
}

int32_t fb_check_threshold(Fb* c, int32_t x, int32_t f, int32_t w) {
  if (x < 0) {
  return 0;
}
  int32_t k = (c[0]).nk[x];
  if (k == N_LIT) {
  return 0;
}
  if (k == N_VAR) {
  int32_t nm = fb_tok_str(c, (c[0]).ntok[x]);
  if (fb_find_member(c, f, MK_PARAM, nm) >= 0) {
  return 0;
}
  FbBuf* m = (FbBuf*)(fb_verr(c, (c[0]).wh_line[w]));
  fb_puts(m, "threshold of 'when ");
  fb_puts(m, (const char*)(fb_s(c, (c[0]).wh_target[w])));
  fb_puts(m, " reaches' in flow '");
  fb_put_fname(m, c, f);
  fb_puts(m, "' references '");
  fb_puts(m, (const char*)(fb_s(c, nm)));
  fb_puts(m, "'; thresholds must be constant over a step, built from params and literals (v1)");
  return (0 - 1);
}
  if (k == N_BIN || k == N_UN || k == N_CAST) {
  int32_t* kids = (int32_t*)((int32_t*)(malloc(256)));
  int32_t nk = fb_children(c, x, kids);
  int32_t i = 0;
  while (i < nk) {
  if (fb_check_threshold(c, kids[i], f, w) < 0) {
  free((uint8_t*)(kids));
  return (0 - 1);
}
  i = (i + 1);
}
  free((uint8_t*)(kids));
  return 0;
}
  FbBuf* m2 = (FbBuf*)(fb_verr(c, (c[0]).wh_line[w]));
  fb_puts(m2, "threshold of 'when ");
  fb_puts(m2, (const char*)(fb_s(c, (c[0]).wh_target[w])));
  fb_puts(m2, " reaches' in flow '");
  fb_put_fname(m2, c, f);
  fb_puts(m2, "' must be built from params and literals (v1)");
  return (0 - 1);
}

int32_t fb_check_booleanish(Fb* c, int32_t x, int32_t f, const char* word, int32_t line) {
  int32_t k = (c[0]).nk[x];
  if (k == N_BIN) {
  int32_t op = (c[0]).nop[x];
  if (op == OP_EQUALS || op == OP_NOT_EQUALS || op == OP_LESS || op == OP_LESS_EQUAL) {
  return 0;
}
  if (op == OP_GREATER || op == OP_GREATER_EQUAL || op == OP_AND || op == OP_OR) {
  return 0;
}
}
  if (k == N_UN && ((c[0]).nop[x] == OP_NOT || (c[0]).nop[x] == OPX_NOT_WORD)) {
  return 0;
}
  if (k == N_LIT && fb_tt_is(c, (c[0]).ntok[x], "BOOLEAN") == 1) {
  return 0;
}
  if (k == N_VAR) {
  return 0;
}
  FbBuf* m = (FbBuf*)(fb_verr(c, line));
  fb_puts(m, "'");
  fb_puts(m, word);
  fb_puts(m, "' clause in flow '");
  fb_put_fname(m, c, f);
  fb_puts(m, "' must be a boolean expression");
  fb_puts(fb_err_hint(c), "write a comparison or logical expression, e.g. 'x < 1.0'");
  return (0 - 1);
}

int32_t fb_refs_inputs(Fb* c, int32_t x, int32_t f) {
  if (x < 0) {
  return 0;
}
  int32_t k = (c[0]).nk[x];
  if (k == N_VAR) {
  if (fb_find_member(c, f, MK_INPUT, fb_tok_str(c, (c[0]).ntok[x])) >= 0) {
  return 1;
}
  return 0;
}
  if (k == N_CALL) {
  int32_t a = (c[0]).na[x];
  while (a >= 0) {
  if (fb_refs_inputs(c, a, f) == 1) {
  return 1;
}
  a = (c[0]).nx[a];
}
  return 0;
}
  int32_t* kids = (int32_t*)((int32_t*)(malloc(256)));
  int32_t nk = fb_children(c, x, kids);
  int32_t i = 0;
  int32_t r = 0;
  while (i < nk && r == 0) {
  r = fb_refs_inputs(c, kids[i], f);
  i = (i + 1);
}
  free((uint8_t*)(kids));
  return r;
}

int32_t fb_port_combinational(Fb* c, int32_t f, int32_t port) {
  int32_t o = fb_find_member(c, f, MK_OUTPUT, port);
  if (o < 0) {
  return 0;
}
  if ((c[0]).mm_pipe_m[o] >= 0) {
  return 0;
}
  if ((c[0]).mm_init[o] < 0) {
  return 0;
}
  return fb_refs_inputs(c, (c[0]).mm_init[o], f);
}

int32_t fb_single_port(Fb* c, int32_t sf, int32_t kind, const char* word, int32_t line) {
  int32_t n = fb_count_members(c, sf, kind);
  if (n != 1) {
  FbBuf* m = (FbBuf*)(fb_verr(c, line));
  fb_puts(m, "flow '");
  fb_put_fname(m, c, sf);
  fb_puts(m, "' used as a pipeline stage must have exactly one ");
  fb_puts(m, word);
  fb_puts(m, " (has ");
  fb_put_int(m, n);
  fb_puts(m, "); wire it with `connect` explicitly");
  return (0 - 1);
}
  return fb_nth_member(c, sf, kind, 0);
}

void fb_put_sorted_params(Fb* c, FbBuf* b, int32_t sf) {
  int32_t n = fb_count_members(c, sf, MK_PARAM);
  if (n == 0) {
  fb_puts(b, "(none)");
  return;
}
  int32_t* used = (int32_t*)((int32_t*)(malloc(((int64_t)((n + 1)) * 4))));
  int32_t i = 0;
  while (i < n) {
  used[i] = 0;
  i = (i + 1);
}
  int32_t k = 0;
  while (k < n) {
  int32_t best = (0 - 1);
  int32_t j = 0;
  while (j < n) {
  if (used[j] == 0) {
  if (best < 0) {
  best = j;
} else {
  int32_t a = (c[0]).mm_name[fb_nth_member(c, sf, MK_PARAM, j)];
  int32_t bb = (c[0]).mm_name[fb_nth_member(c, sf, MK_PARAM, best)];
  if (strcmp((const char*)(fb_s(c, a)), (const char*)(fb_s(c, bb))) < 0) {
  best = j;
}
}
}
  j = (j + 1);
}
  used[best] = 1;
  if (k > 0) {
  fb_puts(b, ", ");
}
  fb_puts(b, (const char*)(fb_s(c, (c[0]).mm_name[fb_nth_member(c, sf, MK_PARAM, best)])));
  k = (k + 1);
}
  free((uint8_t*)(used));
}

int32_t fb_expand_pipelines(Fb* c, int32_t f) {
  int32_t* stages = (int32_t*)((int32_t*)(malloc(4096)));
  int32_t nouts = fb_count_members(c, f, MK_OUTPUT);
  int32_t oi = 0;
  while (oi < nouts) {
  int32_t o = fb_nth_member(c, f, MK_OUTPUT, oi);
  int32_t line = (c[0]).mm_line[o];
  int32_t ns = 0;
  int32_t cur = (c[0]).mm_init[o];
  int32_t going = 1;
  while (going == 1 && cur >= 0 && ns < 1000) {
  int32_t k = (c[0]).nk[cur];
  if (k == N_STAGE) {
  int32_t sname = fb_tok_str(c, (c[0]).ntok[cur]);
  int32_t sf = fb_find_flow(c, sname);
  if (sf < 0) {
  FbBuf* m = (FbBuf*)(fb_verr(c, line));
  fb_puts(m, "'");
  fb_puts(m, (const char*)(fb_s(c, sname)));
  fb_puts(m, " { ... }' in output '");
  fb_puts(m, (const char*)(fb_s(c, (c[0]).mm_name[o])));
  fb_puts(m, "' of '");
  fb_put_fname(m, c, f);
  fb_puts(m, "' names '");
  fb_puts(m, (const char*)(fb_s(c, sname)));
  fb_puts(m, "', which is not a flow");
  free((uint8_t*)(stages));
  return (0 - 1);
}
  stages[(ns * 2)] = sf;
  stages[((ns * 2) + 1)] = (c[0]).nb[cur];
  ns = (ns + 1);
  cur = (c[0]).na[cur];
} else {
  if (k == N_CALL && (c[0]).ntok[cur] >= 0 && fb_find_flow(c, fb_call_name(c, cur)) >= 0) {
  int32_t cf = fb_find_flow(c, fb_call_name(c, cur));
  if (fb_list_len(c, (c[0]).na[cur]) != 1) {
  FbBuf* m2 = (FbBuf*)(fb_verr(c, line));
  fb_puts(m2, "flow stage '");
  fb_put_fname(m2, c, cf);
  fb_puts(m2, "' in output '");
  fb_puts(m2, (const char*)(fb_s(c, (c[0]).mm_name[o])));
  fb_puts(m2, "' of '");
  fb_put_fname(m2, c, f);
  fb_puts(m2, "' takes only the piped value");
  free((uint8_t*)(stages));
  return (0 - 1);
}
  stages[(ns * 2)] = cf;
  stages[((ns * 2) + 1)] = (0 - 1);
  ns = (ns + 1);
  cur = (c[0]).na[cur];
} else {
  going = 0;
}
}
}
  if (ns > 0) {
  int32_t src_m = (0 - 1);
  int32_t src_p = (0 - 1);
  if ((c[0]).nk[cur] == N_VAR) {
  src_m = fb_intern(c, "");
  src_p = fb_tok_str(c, (c[0]).ntok[cur]);
} else {
  if ((c[0]).nk[cur] == N_FIELD && (c[0]).nk[(c[0]).na[cur]] == N_VAR) {
  src_m = fb_tok_str(c, (c[0]).ntok[(c[0]).na[cur]]);
  src_p = fb_tok_str(c, (c[0]).ntok[cur]);
}
}
  if (src_m < 0) {
  FbBuf* m3 = (FbBuf*)(fb_verr(c, line));
  fb_puts(m3, "flow pipeline for output '");
  fb_puts(m3, (const char*)(fb_s(c, (c[0]).mm_name[o])));
  fb_puts(m3, "' of '");
  fb_put_fname(m3, c, f);
  fb_puts(m3, "' must start from a port (an input/state, or `child.port`)");
  free((uint8_t*)(stages));
  return (0 - 1);
}
  int32_t prev_m = src_m;
  int32_t prev_p = src_p;
  int32_t i = 0;
  while (i < ns) {
  int32_t si = ((ns - 1) - i);
  int32_t sf2 = stages[(si * 2)];
  int32_t params = stages[((si * 2) + 1)];
  FbBuf* cb = (FbBuf*)(fb_buf_new(32));
  fb_puts(cb, "__");
  fb_puts(cb, (const char*)(fb_s(c, (c[0]).mm_name[o])));
  fb_puts(cb, "_stage");
  fb_put_int(cb, i);
  int32_t child_name = fb_intern_buf(c, cb);
  fb_buf_free(cb);
  int32_t pk = params;
  while (pk >= 0) {
  int32_t pn = fb_tok_str(c, (c[0]).ntok[pk]);
  if (fb_find_member(c, sf2, MK_PARAM, pn) < 0) {
  FbBuf* m4 = (FbBuf*)(fb_verr(c, line));
  fb_puts(m4, "flow stage '");
  fb_put_fname(m4, c, sf2);
  fb_puts(m4, "' in '");
  fb_put_fname(m4, c, f);
  fb_puts(m4, "' has no param '");
  fb_puts(m4, (const char*)(fb_s(c, pn)));
  fb_puts(m4, "'");
  FbBuf* h = (FbBuf*)(fb_err_hint(c));
  fb_puts(h, "stage overrides set `param` fields; declared params are: ");
  fb_put_sorted_params(c, h, sf2);
  free((uint8_t*)(stages));
  return (0 - 1);
}
  pk = (c[0]).nx[pk];
}
  int32_t ch = fb_add_member(c, f, MK_CHILD, child_name, (c[0]).f_name[sf2], (0 - 1), line);
  (c[0]).mm_synth[ch] = 1;
  (c[0]).mm_params[ch] = params;
  int32_t in_port = fb_single_port(c, sf2, MK_INPUT, "input", line);
  if (in_port < 0) {
  free((uint8_t*)(stages));
  return (0 - 1);
}
  int32_t out_port = fb_single_port(c, sf2, MK_OUTPUT, "output", line);
  if (out_port < 0) {
  free((uint8_t*)(stages));
  return (0 - 1);
}
  fb_add_conn(c, f, prev_m, prev_p, child_name, (c[0]).mm_name[in_port], line);
  prev_m = child_name;
  prev_p = (c[0]).mm_name[out_port];
  i = (i + 1);
}
  (c[0]).mm_pipe_m[o] = prev_m;
  (c[0]).mm_pipe_p[o] = prev_p;
}
  oi = (oi + 1);
}
  free((uint8_t*)(stages));
  return 0;
}

int32_t fb_is_member_type(Fb* c, int32_t ty) {
  if (fb_name_is(c, ty, "f64") == 1 || fb_name_is(c, ty, "f32") == 1) {
  return 1;
}
  if (fb_has_name(c, NX_DIMENSION, ty) == 1) {
  return 1;
}
  return 0;
}

int32_t fb_is_scalar_type(Fb* c, int32_t ty) {
  const char* s = (const char*)(fb_s(c, ty));
  if (strcmp(s, "f32") == 0 || strcmp(s, "f64") == 0) {
  return 1;
}
  if (strcmp(s, "i8") == 0 || strcmp(s, "i16") == 0 || strcmp(s, "i32") == 0 || strcmp(s, "i64") == 0) {
  return 1;
}
  if (strcmp(s, "u8") == 0 || strcmp(s, "u16") == 0 || strcmp(s, "u32") == 0 || strcmp(s, "u64") == 0) {
  return 1;
}
  return 0;
}

void fb_reclassify(Fb* c) {
  int32_t total = (c[0]).nmm;
  int32_t f = 0;
  while (f < (c[0]).nf) {
  int32_t i = 0;
  while (i < total) {
  if ((c[0]).mm_flow[i] == f && (c[0]).mm_kind[i] == MK_CHILD) {
  int32_t ty = (c[0]).mm_type[i];
  if (fb_find_flow(c, ty) < 0 && (fb_is_scalar_type(c, ty) == 1 || fb_has_name(c, NX_DIMENSION, ty) == 1)) {
  fb_add_member(c, f, MK_STATE, (c[0]).mm_name[i], ty, (0 - 1), (c[0]).mm_line[i]);
  (c[0]).mm_kind[i] = MK_DEAD;
}
}
  i = (i + 1);
}
  f = (f + 1);
}
}

int32_t fb_member_rank(int32_t k) {
  if (k == MK_STATE) {
  return 0;
}
  if (k == MK_INPUT) {
  return 1;
}
  if (k == MK_OUTPUT) {
  return 2;
}
  if (k == MK_PARAM) {
  return 3;
}
  if (k == MK_CHILD) {
  return 4;
}
  return 9;
}

int32_t fb_seen_before(Fb* c, int32_t f, int32_t i) {
  int32_t ri = fb_member_rank((c[0]).mm_kind[i]);
  int32_t j = 0;
  while (j < (c[0]).nmm) {
  if (j != i && (c[0]).mm_flow[j] == f && (c[0]).mm_kind[j] != MK_DEAD) {
  int32_t rj = fb_member_rank((c[0]).mm_kind[j]);
  if (rj < ri || rj == ri && j < i) {
  if (fb_name_eq(c, (c[0]).mm_name[j], (c[0]).mm_name[i]) == 1) {
  return 1;
}
}
}
  j = (j + 1);
}
  return 0;
}

int32_t fb_validate_members(Fb* c, int32_t f) {
  int32_t rank = 0;
  while (rank < 4) {
  int32_t i = 0;
  while (i < (c[0]).nmm) {
  if ((c[0]).mm_flow[i] == f && fb_member_rank((c[0]).mm_kind[i]) == rank) {
  int32_t nm = (c[0]).mm_name[i];
  if (fb_seen_before(c, f, i) == 1) {
  FbBuf* m = (FbBuf*)(fb_verr(c, (c[0]).mm_line[i]));
  fb_puts(m, "flow '");
  fb_put_fname(m, c, f);
  fb_puts(m, "' declares '");
  fb_puts(m, (const char*)(fb_s(c, nm)));
  fb_puts(m, "' twice");
  return (0 - 1);
}
  if (fb_name_starts_uu(c, nm) == 1) {
  FbBuf* m2 = (FbBuf*)(fb_verr(c, (c[0]).mm_line[i]));
  fb_puts(m2, "flow member '");
  fb_puts(m2, (const char*)(fb_s(c, nm)));
  fb_puts(m2, "' may not start with '__' (reserved for compiler-generated fields)");
  return (0 - 1);
}
  if (fb_is_member_type(c, (c[0]).mm_type[i]) == 0) {
  FbBuf* m3 = (FbBuf*)(fb_verr(c, (c[0]).mm_line[i]));
  fb_puts(m3, fb_kind_word((c[0]).mm_kind[i]));
  fb_puts(m3, " '");
  fb_puts(m3, (const char*)(fb_s(c, nm)));
  fb_puts(m3, "' in flow '");
  fb_put_fname(m3, c, f);
  fb_puts(m3, "' has type '");
  fb_puts(m3, (const char*)(fb_s(c, (c[0]).mm_type[i])));
  fb_puts(m3, "'; a flow member is f64, f32, or a declared unit");
  fb_puts(fb_err_hint(c), "declare the dimension with 'unit Angle' first");
  return (0 - 1);
}
}
  i = (i + 1);
}
  rank = (rank + 1);
}
  int32_t ci = 0;
  while (ci < (c[0]).nmm) {
  if ((c[0]).mm_flow[ci] == f && (c[0]).mm_kind[ci] == MK_CHILD) {
  int32_t cn = (c[0]).mm_name[ci];
  if (fb_seen_before(c, f, ci) == 1) {
  FbBuf* m4 = (FbBuf*)(fb_verr(c, (c[0]).mm_line[ci]));
  fb_puts(m4, "flow '");
  fb_put_fname(m4, c, f);
  fb_puts(m4, "' declares '");
  fb_puts(m4, (const char*)(fb_s(c, cn)));
  fb_puts(m4, "' twice");
  return (0 - 1);
}
  if (fb_name_starts_uu(c, cn) == 1 && (c[0]).mm_synth[ci] == 0) {
  FbBuf* m5 = (FbBuf*)(fb_verr(c, (c[0]).mm_line[ci]));
  fb_puts(m5, "flow member '");
  fb_puts(m5, (const char*)(fb_s(c, cn)));
  fb_puts(m5, "' may not start with '__' (reserved for compiler-generated fields)");
  return (0 - 1);
}
  if (fb_name_eq(c, (c[0]).mm_type[ci], (c[0]).f_name[f]) == 1) {
  FbBuf* m6 = (FbBuf*)(fb_verr(c, (c[0]).mm_line[ci]));
  fb_puts(m6, "nested flow member '");
  fb_puts(m6, (const char*)(fb_s(c, cn)));
  fb_puts(m6, "' in flow '");
  fb_put_fname(m6, c, f);
  fb_puts(m6, "' cannot have the parent type (no recursive nesting)");
  return (0 - 1);
}
  if (fb_find_flow(c, (c[0]).mm_type[ci]) < 0) {
  FbBuf* m7 = (FbBuf*)(fb_verr(c, (c[0]).mm_line[ci]));
  fb_puts(m7, "nested flow member '");
  fb_puts(m7, (const char*)(fb_s(c, cn)));
  fb_puts(m7, "' in flow '");
  fb_put_fname(m7, c, f);
  fb_puts(m7, "' has type '");
  fb_puts(m7, (const char*)(fb_s(c, (c[0]).mm_type[ci])));
  fb_puts(m7, "', which is not a flow in this file");
  fb_puts(fb_err_hint(c), "declare the child with 'flow ChildName { ... }' first");
  return (0 - 1);
}
}
  ci = (ci + 1);
}
  return 0;
}

int32_t fb_recognition_ok(uint8_t* name) {
  const char* s = (const char*)(name);
  if (strcmp(s, "numerical") == 0 || strcmp(s, "realtime") == 0 || strcmp(s, "causal") == 0) {
  return 1;
}
  if (strcmp(s, "safety") == 0 || strcmp(s, "memory") == 0) {
  return 1;
}
  return 0;
}

int32_t fb_validate_connect(Fb* c, int32_t f) {
  int32_t nch = fb_count_members(c, f, MK_CHILD);
  int32_t first_conn = (0 - 1);
  int32_t k = 0;
  while (k < (c[0]).ncn) {
  if ((c[0]).cn_flow[k] == f && first_conn < 0) {
  first_conn = k;
}
  k = (k + 1);
}
  if (first_conn >= 0 && nch == 0) {
  FbBuf* m = (FbBuf*)(fb_verr(c, (c[0]).cn_line[first_conn]));
  fb_puts(m, "'connect' in flow '");
  fb_put_fname(m, c, f);
  fb_puts(m, "' needs nested flow members to wire (e.g. 'plant : Motor')");
  return (0 - 1);
}
  int32_t i = 0;
  while (i < (c[0]).ncn) {
  if ((c[0]).cn_flow[i] == f) {
  int32_t sm = (c[0]).cn_sm[i];
  int32_t sp = (c[0]).cn_sp[i];
  int32_t dm = (c[0]).cn_dm[i];
  int32_t dp = (c[0]).cn_dp[i];
  int32_t line = (c[0]).cn_line[i];
  int32_t parent = fb_name_is(c, sm, "");
  int32_t src_child = fb_find_member(c, f, MK_CHILD, sm);
  int32_t dst_child = fb_find_member(c, f, MK_CHILD, dm);
  if (parent == 0 && src_child < 0) {
  FbBuf* m1 = (FbBuf*)(fb_verr(c, line));
  fb_puts(m1, "connection source '");
  fb_puts(m1, (const char*)(fb_s(c, sm)));
  fb_putc(m1, 46);
  fb_puts(m1, (const char*)(fb_s(c, sp)));
  fb_puts(m1, "' in flow '");
  fb_put_fname(m1, c, f);
  fb_puts(m1, "' names unknown nested member '");
  fb_puts(m1, (const char*)(fb_s(c, sm)));
  fb_puts(m1, "'");
  return (0 - 1);
}
  if (dst_child < 0) {
  FbBuf* m2 = (FbBuf*)(fb_verr(c, line));
  fb_puts(m2, "connection destination '");
  fb_puts(m2, (const char*)(fb_s(c, dm)));
  fb_putc(m2, 46);
  fb_puts(m2, (const char*)(fb_s(c, dp)));
  fb_puts(m2, "' in flow '");
  fb_put_fname(m2, c, f);
  fb_puts(m2, "' names unknown nested member '");
  fb_puts(m2, (const char*)(fb_s(c, dm)));
  fb_puts(m2, "'");
  return (0 - 1);
}
  if (parent == 0 && fb_name_eq(c, sm, dm) == 1) {
  FbBuf* m3 = (FbBuf*)(fb_verr(c, line));
  fb_puts(m3, "connection in flow '");
  fb_put_fname(m3, c, f);
  fb_puts(m3, "' wires '");
  fb_puts(m3, (const char*)(fb_s(c, sm)));
  fb_puts(m3, "' to itself; Stage-1 connect is between sibling subflows only");
  return (0 - 1);
}
  int32_t dst_flow = fb_find_flow(c, (c[0]).mm_type[dst_child]);
  int32_t src_port = (0 - 1);
  if (parent == 1) {
  src_port = fb_lookup_port(c, f, sp);
  if (src_port < 0) {
  FbBuf* m4 = (FbBuf*)(fb_verr(c, line));
  fb_puts(m4, "connection source '");
  fb_puts(m4, (const char*)(fb_s(c, sp)));
  fb_puts(m4, "' in flow '");
  fb_put_fname(m4, c, f);
  fb_puts(m4, "' is not a port of this flow");
  FbBuf* h = (FbBuf*)(fb_err_hint(c));
  fb_puts(h, "a bare source must be an input or state of '");
  fb_put_fname(h, c, f);
  fb_puts(h, "'; a child source is written 'child.port'");
  return (0 - 1);
}
  int32_t sk = (c[0]).mm_kind[src_port];
  if (sk != MK_INPUT && sk != MK_STATE) {
  FbBuf* m5 = (FbBuf*)(fb_verr(c, line));
  fb_puts(m5, "connection source '");
  fb_puts(m5, (const char*)(fb_s(c, sp)));
  fb_puts(m5, "' in flow '");
  fb_put_fname(m5, c, f);
  fb_puts(m5, "' is a ");
  fb_puts(m5, fb_kind_word(sk));
  fb_puts(m5, "; a parent source must be an input or state");
  return (0 - 1);
}
} else {
  int32_t src_flow = fb_find_flow(c, (c[0]).mm_type[src_child]);
  src_port = fb_lookup_port(c, src_flow, sp);
  if (src_port < 0) {
  FbBuf* m6 = (FbBuf*)(fb_verr(c, line));
  fb_puts(m6, "'");
  fb_puts(m6, (const char*)(fb_s(c, sm)));
  fb_putc(m6, 46);
  fb_puts(m6, (const char*)(fb_s(c, sp)));
  fb_puts(m6, "' in flow '");
  fb_put_fname(m6, c, f);
  fb_puts(m6, "' is not a port of '");
  fb_put_fname(m6, c, src_flow);
  fb_puts(m6, "'");
  FbBuf* h2 = (FbBuf*)(fb_err_hint(c));
  fb_puts(h2, "connect sources must be an output or state of '");
  fb_put_fname(h2, c, src_flow);
  fb_puts(h2, "'");
  return (0 - 1);
}
  int32_t sk2 = (c[0]).mm_kind[src_port];
  if (sk2 != MK_OUTPUT && sk2 != MK_STATE) {
  FbBuf* m7 = (FbBuf*)(fb_verr(c, line));
  fb_puts(m7, "'");
  fb_puts(m7, (const char*)(fb_s(c, sm)));
  fb_putc(m7, 46);
  fb_puts(m7, (const char*)(fb_s(c, sp)));
  fb_puts(m7, "' in flow '");
  fb_put_fname(m7, c, f);
  fb_puts(m7, "' is a ");
  fb_puts(m7, fb_kind_word(sk2));
  fb_puts(m7, "; connection sources must be an output or state");
  return (0 - 1);
}
}
  int32_t dst_port = fb_lookup_port(c, dst_flow, dp);
  if (dst_port < 0) {
  FbBuf* m8 = (FbBuf*)(fb_verr(c, line));
  fb_puts(m8, "'");
  fb_puts(m8, (const char*)(fb_s(c, dm)));
  fb_putc(m8, 46);
  fb_puts(m8, (const char*)(fb_s(c, dp)));
  fb_puts(m8, "' in flow '");
  fb_put_fname(m8, c, f);
  fb_puts(m8, "' is not a port of '");
  fb_put_fname(m8, c, dst_flow);
  fb_puts(m8, "'");
  FbBuf* h3 = (FbBuf*)(fb_err_hint(c));
  fb_puts(h3, "connection destinations must be an input of '");
  fb_put_fname(h3, c, dst_flow);
  fb_puts(h3, "'");
  return (0 - 1);
}
  if ((c[0]).mm_kind[dst_port] != MK_INPUT) {
  FbBuf* m9 = (FbBuf*)(fb_verr(c, line));
  fb_puts(m9, "'");
  fb_puts(m9, (const char*)(fb_s(c, dm)));
  fb_putc(m9, 46);
  fb_puts(m9, (const char*)(fb_s(c, dp)));
  fb_puts(m9, "' in flow '");
  fb_put_fname(m9, c, f);
  fb_puts(m9, "' is a ");
  fb_puts(m9, fb_kind_word((c[0]).mm_kind[dst_port]));
  fb_puts(m9, "; connection destinations must be an input");
  return (0 - 1);
}
  if (fb_name_eq(c, (c[0]).mm_type[src_port], (c[0]).mm_type[dst_port]) == 0) {
  FbBuf* m10 = (FbBuf*)(fb_verr(c, line));
  fb_puts(m10, "type mismatch in connect of flow '");
  fb_put_fname(m10, c, f);
  fb_puts(m10, "': '");
  fb_puts(m10, (const char*)(fb_s(c, sm)));
  fb_putc(m10, 46);
  fb_puts(m10, (const char*)(fb_s(c, sp)));
  fb_puts(m10, "' is ");
  fb_puts(m10, (const char*)(fb_s(c, (c[0]).mm_type[src_port])));
  fb_puts(m10, " but '");
  fb_puts(m10, (const char*)(fb_s(c, dm)));
  fb_putc(m10, 46);
  fb_puts(m10, (const char*)(fb_s(c, dp)));
  fb_puts(m10, "' is ");
  fb_puts(m10, (const char*)(fb_s(c, (c[0]).mm_type[dst_port])));
  return (0 - 1);
}
  int32_t j = 0;
  while (j < i) {
  if ((c[0]).cn_flow[j] == f && fb_name_eq(c, (c[0]).cn_dm[j], dm) == 1 && fb_name_eq(c, (c[0]).cn_dp[j], dp) == 1) {
  FbBuf* m11 = (FbBuf*)(fb_verr(c, line));
  fb_puts(m11, "input '");
  fb_puts(m11, (const char*)(fb_s(c, dm)));
  fb_putc(m11, 46);
  fb_puts(m11, (const char*)(fb_s(c, dp)));
  fb_puts(m11, "' in flow '");
  fb_put_fname(m11, c, f);
  fb_puts(m11, "' has two incoming connections");
  return (0 - 1);
}
  j = (j + 1);
}
}
  i = (i + 1);
}
  return fb_check_loops(c, f);
}

int32_t fb_conn_combo(Fb* c, int32_t f, int32_t i) {
  if (fb_name_is(c, (c[0]).cn_sm[i], "") == 1) {
  return 0;
}
  int32_t sc = fb_find_member(c, f, MK_CHILD, (c[0]).cn_sm[i]);
  if (sc < 0) {
  return 0;
}
  int32_t sf = fb_find_flow(c, (c[0]).mm_type[sc]);
  return fb_port_combinational(c, sf, (c[0]).cn_sp[i]);
}

int32_t fb_child_index(Fb* c, int32_t f, int32_t name) {
  int32_t n = fb_count_members(c, f, MK_CHILD);
  int32_t k = 0;
  while (k < n) {
  if (fb_name_eq(c, (c[0]).mm_name[fb_nth_member(c, f, MK_CHILD, k)], name) == 1) {
  return k;
}
  k = (k + 1);
}
  return (0 - 1);
}

int32_t fb_dfs(Fb* c, int32_t f, int32_t node, int32_t* state, int32_t* stack, int32_t* sp, int32_t* cyc) {
  state[node] = 1;
  stack[sp[0]] = node;
  sp[0] = (sp[0] + 1);
  int32_t i = 0;
  while (i < (c[0]).ncn) {
  if ((c[0]).cn_flow[i] == f && fb_conn_combo(c, f, i) == 1) {
  int32_t a = fb_child_index(c, f, (c[0]).cn_sm[i]);
  int32_t b = fb_child_index(c, f, (c[0]).cn_dm[i]);
  if (a == node && b >= 0) {
  if (state[b] == 1) {
  int32_t k = 0;
  while (stack[k] != b) {
  k = (k + 1);
}
  cyc[0] = k;
  cyc[1] = b;
  return 1;
}
  if (state[b] == 0) {
  if (fb_dfs(c, f, b, state, stack, sp, cyc) == 1) {
  return 1;
}
}
}
}
  i = (i + 1);
}
  sp[0] = (sp[0] - 1);
  state[node] = 2;
  return 0;
}

int32_t fb_check_loops(Fb* c, int32_t f) {
  int32_t n = fb_count_members(c, f, MK_CHILD);
  if (n == 0) {
  return 0;
}
  int32_t* state = (int32_t*)((int32_t*)(malloc(((int64_t)((n + 1)) * 4))));
  int32_t* stack = (int32_t*)((int32_t*)(malloc(((int64_t)((n + 1)) * 4))));
  int32_t* sp = (int32_t*)((int32_t*)(malloc(4)));
  int32_t* cyc = (int32_t*)((int32_t*)(malloc(8)));
  int32_t k = 0;
  while (k < n) {
  state[k] = 0;
  k = (k + 1);
}
  sp[0] = 0;
  int32_t found = 0;
  int32_t m = 0;
  while (m < n && found == 0) {
  if (state[m] == 0) {
  found = fb_dfs(c, f, m, state, stack, sp, cyc);
}
  m = (m + 1);
}
  int32_t rc = 0;
  if (found == 1) {
  int32_t line = 0;
  int32_t e = 0;
  int32_t got = 0;
  while (e < (c[0]).ncn && got == 0) {
  if ((c[0]).cn_flow[e] == f && fb_conn_combo(c, f, e) == 1) {
  int32_t a = fb_child_index(c, f, (c[0]).cn_sm[e]);
  int32_t b = fb_child_index(c, f, (c[0]).cn_dm[e]);
  int32_t ina = 0;
  int32_t inb = 0;
  int32_t q = cyc[0];
  while (q < sp[0]) {
  if (stack[q] == a) {
  ina = 1;
}
  if (stack[q] == b) {
  inb = 1;
}
  q = (q + 1);
}
  if (ina == 1 && inb == 1) {
  line = (c[0]).cn_line[e];
  got = 1;
}
}
  e = (e + 1);
}
  if (got == 0) {
  int32_t e2 = 0;
  while (e2 < (c[0]).ncn && got == 0) {
  if ((c[0]).cn_flow[e2] == f) {
  line = (c[0]).cn_line[e2];
  got = 1;
}
  e2 = (e2 + 1);
}
}
  FbBuf* mb = (FbBuf*)(fb_verr(c, line));
  fb_puts(mb, "algebraic loop in connect of flow '");
  fb_put_fname(mb, c, f);
  fb_puts(mb, "' through combinational outputs: ");
  int32_t q2 = cyc[0];
  while (q2 < sp[0]) {
  fb_puts(mb, (const char*)(fb_s(c, (c[0]).mm_name[fb_nth_member(c, f, MK_CHILD, stack[q2])])));
  fb_puts(mb, " -> ");
  q2 = (q2 + 1);
}
  fb_puts(mb, (const char*)(fb_s(c, (c[0]).mm_name[fb_nth_member(c, f, MK_CHILD, cyc[1])])));
  fb_puts(fb_err_hint(c), "break the loop with a state (or an output mapped from a state); Modelica-style algebraic solvers are out of scope");
  rc = (0 - 1);
}
  free((uint8_t*)(state));
  free((uint8_t*)(stack));
  free((uint8_t*)(sp));
  free((uint8_t*)(cyc));
  return rc;
}

int32_t fb_validate_flow(Fb* c, int32_t f) {
  int32_t fline = (c[0]).f_line[f];
  int32_t r = 0;
  while (r < (c[0]).nrc) {
  if ((c[0]).rc_flow[r] == f && fb_recognition_ok(fb_s(c, (c[0]).rc_name[r])) == 0) {
  int32_t rl = (c[0]).f_rec_line[f];
  if (rl == 0) {
  rl = fline;
}
  FbBuf* m = (FbBuf*)(fb_verr(c, rl));
  fb_puts(m, "unknown recognition domain '");
  fb_puts(m, (const char*)(fb_s(c, (c[0]).rc_name[r])));
  fb_puts(m, "' in flow '");
  fb_put_fname(m, c, f);
  fb_puts(m, "'; valid domains: numerical, realtime, causal, safety, memory");
  return (0 - 1);
}
  r = (r + 1);
}
  int32_t nstates = fb_count_members(c, f, MK_STATE);
  int32_t nchildren = fb_count_members(c, f, MK_CHILD);
  if (nstates == 0 && nchildren == 0) {
  FbBuf* m2 = (FbBuf*)(fb_verr(c, fline));
  fb_puts(m2, "flow '");
  fb_put_fname(m2, c, f);
  fb_puts(m2, "' declares no state");
  fb_puts(fb_err_hint(c), "add at least one 'state name : f64 = value' declaration, or nest child flows ('plant : Motor') for a composite");
  return (0 - 1);
}
  int32_t si = 0;
  while (si < 7) {
  const char* suf = "_new";
  if (si == 1) {
  suf = "_init";
}
  if (si == 2) {
  suf = "_derivs";
}
  if (si == 3) {
  suf = "_step";
}
  if (si == 4) {
  suf = "_outputs";
}
  if (si == 5) {
  suf = "_check";
}
  if (si == 6) {
  suf = "_default_dt";
}
  int32_t gen = fb_where(c, "", (c[0]).f_name[f], suf);
  if (fb_has_name(c, NX_TAKEN, gen) == 1) {
  FbBuf* m3 = (FbBuf*)(fb_verr(c, fline));
  fb_puts(m3, "name '");
  fb_puts(m3, (const char*)(fb_s(c, gen)));
  fb_puts(m3, "' is reserved by flow '");
  fb_put_fname(m3, c, f);
  fb_puts(m3, "' (the compiler generates it)");
  return (0 - 1);
}
  si = (si + 1);
}
  if (fb_validate_members(c, f) < 0) {
  return (0 - 1);
}
  int32_t i = 0;
  while (i < (c[0]).nmm) {
  if ((c[0]).mm_flow[i] == f && (c[0]).mm_kind[i] == MK_PARAM && (c[0]).mm_init[i] < 0) {
  FbBuf* m4 = (FbBuf*)(fb_verr(c, (c[0]).mm_line[i]));
  fb_puts(m4, "param '");
  fb_puts(m4, (const char*)(fb_s(c, (c[0]).mm_name[i])));
  fb_puts(m4, "' in flow '");
  fb_put_fname(m4, c, f);
  fb_puts(m4, "' needs a default value");
  FbBuf* h = (FbBuf*)(fb_err_hint(c));
  fb_puts(h, "write 'param ");
  fb_puts(h, (const char*)(fb_s(c, (c[0]).mm_name[i])));
  fb_puts(h, " : ");
  fb_puts(h, (const char*)(fb_s(c, (c[0]).mm_type[i])));
  fb_puts(h, " = 1.0'");
  return (0 - 1);
}
  i = (i + 1);
}
  i = 0;
  while (i < (c[0]).nmm) {
  if ((c[0]).mm_flow[i] == f && (c[0]).mm_kind[i] == MK_OUTPUT && (c[0]).mm_init[i] < 0) {
  FbBuf* m5 = (FbBuf*)(fb_verr(c, (c[0]).mm_line[i]));
  fb_puts(m5, "output '");
  fb_puts(m5, (const char*)(fb_s(c, (c[0]).mm_name[i])));
  fb_puts(m5, "' in flow '");
  fb_put_fname(m5, c, f);
  fb_puts(m5, "' needs an inline map ('output ");
  fb_puts(m5, (const char*)(fb_s(c, (c[0]).mm_name[i])));
  fb_puts(m5, " : ");
  fb_puts(m5, (const char*)(fb_s(c, (c[0]).mm_type[i])));
  fb_puts(m5, " = expr'); assigning outputs from 'every'/'when' blocks is a later card");
  return (0 - 1);
}
  i = (i + 1);
}
  int32_t e = 0;
  while (e < (c[0]).nev) {
  if ((c[0]).ev_flow[e] == f) {
  int32_t tg = (c[0]).ev_target[e];
  if (fb_find_member(c, f, MK_STATE, tg) < 0) {
  FbBuf* m6 = (FbBuf*)(fb_verr(c, (c[0]).ev_line[e]));
  fb_puts(m6, "'");
  fb_puts(m6, (const char*)(fb_s(c, tg)));
  fb_puts(m6, " evolves as' in flow '");
  fb_put_fname(m6, c, f);
  fb_puts(m6, "' requires '");
  fb_puts(m6, (const char*)(fb_s(c, tg)));
  fb_puts(m6, "' to be a declared state");
  FbBuf* h2 = (FbBuf*)(fb_err_hint(c));
  fb_puts(h2, "declare 'state ");
  fb_puts(h2, (const char*)(fb_s(c, tg)));
  fb_puts(h2, " : f64 = 0.0' or fix the name");
  return (0 - 1);
}
  if (fb_evolve_of(c, f, tg) != e) {
  FbBuf* m7 = (FbBuf*)(fb_verr(c, (c[0]).ev_line[e]));
  fb_puts(m7, "state '");
  fb_puts(m7, (const char*)(fb_s(c, tg)));
  fb_puts(m7, "' in flow '");
  fb_put_fname(m7, c, f);
  fb_puts(m7, "' has two 'evolves' declarations; a state has exactly one derivative");
  return (0 - 1);
}
  if (fb_check_pure(c, (c[0]).ev_expr[e], f, fb_where(c, "'", tg, " evolves as'"), (c[0]).ev_line[e]) < 0) {
  return (0 - 1);
}
}
  e = (e + 1);
}
  int32_t w = 0;
  while (w < (c[0]).nwh) {
  if ((c[0]).wh_flow[w] == f) {
  int32_t gt = (c[0]).wh_target[w];
  if (fb_find_member(c, f, MK_STATE, gt) < 0) {
  FbBuf* m8 = (FbBuf*)(fb_verr(c, (c[0]).wh_line[w]));
  fb_puts(m8, "'when ");
  fb_puts(m8, (const char*)(fb_s(c, gt)));
  fb_puts(m8, " reaches' in flow '");
  fb_put_fname(m8, c, f);
  fb_puts(m8, "' requires '");
  fb_puts(m8, (const char*)(fb_s(c, gt)));
  fb_puts(m8, "' to be a declared state");
  FbBuf* h3 = (FbBuf*)(fb_err_hint(c));
  fb_puts(h3, "declare 'state ");
  fb_puts(h3, (const char*)(fb_s(c, gt)));
  fb_puts(h3, " : f64 = 0.0' or fix the name");
  return (0 - 1);
}
  if (fb_evolve_of(c, f, gt) < 0) {
  FbBuf* m9 = (FbBuf*)(fb_verr(c, (c[0]).wh_line[w]));
  fb_puts(m9, "'when ");
  fb_puts(m9, (const char*)(fb_s(c, gt)));
  fb_puts(m9, " reaches' in flow '");
  fb_put_fname(m9, c, f);
  fb_puts(m9, "' requires '");
  fb_puts(m9, (const char*)(fb_s(c, gt)));
  fb_puts(m9, "' to be a continuous state");
  FbBuf* h4 = (FbBuf*)(fb_err_hint(c));
  fb_puts(h4, "give '");
  fb_puts(h4, (const char*)(fb_s(c, gt)));
  fb_puts(h4, "' an '");
  fb_puts(h4, (const char*)(fb_s(c, gt)));
  fb_puts(h4, " evolves as ...' declaration");
  return (0 - 1);
}
  if (fb_check_threshold(c, (c[0]).wh_thr[w], f, w) < 0) {
  return (0 - 1);
}
  int32_t b = 0;
  while (b < (c[0]).nbc) {
  if ((c[0]).bc_kind[b] == 1 && (c[0]).bc_owner[b] == w) {
  int32_t rt = (c[0]).bc_target[b];
  if (fb_find_member(c, f, MK_STATE, rt) < 0) {
  FbBuf* m10 = (FbBuf*)(fb_verr(c, (c[0]).bc_line[b]));
  fb_puts(m10, "'");
  fb_puts(m10, (const char*)(fb_s(c, rt)));
  fb_puts(m10, " becomes' in the 'when ");
  fb_puts(m10, (const char*)(fb_s(c, gt)));
  fb_puts(m10, " reaches' body of flow '");
  fb_put_fname(m10, c, f);
  fb_puts(m10, "' requires '");
  fb_puts(m10, (const char*)(fb_s(c, rt)));
  fb_puts(m10, "' to be a declared state");
  return (0 - 1);
}
  if (fb_becomes_seen(c, 1, w, b) == 1) {
  FbBuf* m11 = (FbBuf*)(fb_verr(c, (c[0]).bc_line[b]));
  fb_puts(m11, "state '");
  fb_puts(m11, (const char*)(fb_s(c, rt)));
  fb_puts(m11, "' has two 'becomes' resets in one 'when' body of flow '");
  fb_put_fname(m11, c, f);
  fb_puts(m11, "'; resets in an event apply simultaneously, so each state has one writer");
  return (0 - 1);
}
  if (fb_check_pure(c, (c[0]).bc_expr[b], f, fb_where(c, "'", rt, " becomes'"), (c[0]).bc_line[b]) < 0) {
  return (0 - 1);
}
}
  b = (b + 1);
}
}
  w = (w + 1);
}
  if ((c[0]).f_solver[f] == 1) {
  if ((c[0]).f_dt_ns[f] <= 0) {
  FbBuf* m12 = (FbBuf*)(fb_verr(c, (c[0]).f_solver_line[f]));
  fb_puts(m12, "solver dt of flow '");
  fb_put_fname(m12, c, f);
  fb_puts(m12, "' must be positive, got '");
  fb_puts(m12, (const char*)(fb_s(c, (c[0]).f_dt_text[f])));
  fb_puts(m12, "'");
  return (0 - 1);
}
  int32_t meth = (c[0]).f_method[f];
  if (fb_name_is(c, meth, "euler") == 0 && fb_name_is(c, meth, "rk4") == 0) {
  FbBuf* m13 = (FbBuf*)(fb_verr(c, (c[0]).f_solver_line[f]));
  fb_puts(m13, "unknown solver method '");
  fb_puts(m13, (const char*)(fb_s(c, meth)));
  fb_puts(m13, "' in flow '");
  fb_put_fname(m13, c, f);
  fb_puts(m13, "'; valid methods: euler, rk4");
  return (0 - 1);
}
}
  int32_t v = 0;
  while (v < (c[0]).ney) {
  if ((c[0]).ey_flow[v] == f) {
  if ((c[0]).ey_ns[v] <= 0) {
  FbBuf* m14 = (FbBuf*)(fb_verr(c, (c[0]).ey_line[v]));
  fb_puts(m14, "'every ");
  fb_puts(m14, (const char*)(fb_s(c, (c[0]).ey_text[v])));
  fb_puts(m14, "' in flow '");
  fb_put_fname(m14, c, f);
  fb_puts(m14, "' has a zero period; the period must be positive");
  return (0 - 1);
}
  int32_t u = 0;
  while (u < (c[0]).nbc) {
  if ((c[0]).bc_kind[u] == 2 && (c[0]).bc_owner[u] == v) {
  int32_t ut = (c[0]).bc_target[u];
  if (fb_find_member(c, f, MK_STATE, ut) < 0) {
  FbBuf* m15 = (FbBuf*)(fb_verr(c, (c[0]).bc_line[u]));
  fb_puts(m15, "'");
  fb_puts(m15, (const char*)(fb_s(c, ut)));
  fb_puts(m15, " becomes' in the 'every ");
  fb_puts(m15, (const char*)(fb_s(c, (c[0]).ey_text[v])));
  fb_puts(m15, "' body of flow '");
  fb_put_fname(m15, c, f);
  fb_puts(m15, "' requires '");
  fb_puts(m15, (const char*)(fb_s(c, ut)));
  fb_puts(m15, "' to be a declared state");
  return (0 - 1);
}
  if (fb_evolve_of(c, f, ut) >= 0) {
  FbBuf* m16 = (FbBuf*)(fb_verr(c, (c[0]).bc_line[u]));
  fb_puts(m16, "state '");
  fb_puts(m16, (const char*)(fb_s(c, ut)));
  fb_puts(m16, "' in flow '");
  fb_put_fname(m16, c, f);
  fb_puts(m16, "' has both an 'evolves' declaration and a 'becomes' update in an 'every' block; a state is continuous or discrete");
  FbBuf* h5 = (FbBuf*)(fb_err_hint(c));
  fb_puts(h5, "reset '");
  fb_puts(h5, (const char*)(fb_s(c, ut)));
  fb_puts(h5, "' from a 'when ");
  fb_puts(h5, (const char*)(fb_s(c, ut)));
  fb_puts(h5, " reaches ...' event, or drop its 'evolves' declaration");
  return (0 - 1);
}
  if (fb_becomes_seen(c, 2, v, u) == 1) {
  FbBuf* m17 = (FbBuf*)(fb_verr(c, (c[0]).bc_line[u]));
  fb_puts(m17, "state '");
  fb_puts(m17, (const char*)(fb_s(c, ut)));
  fb_puts(m17, "' has two 'becomes' updates in one 'every' body of flow '");
  fb_put_fname(m17, c, f);
  fb_puts(m17, "'; updates in a block apply simultaneously, so each state has one writer");
  return (0 - 1);
}
  if (fb_check_pure(c, (c[0]).bc_expr[u], f, fb_where(c, "'", ut, " becomes'"), (c[0]).bc_line[u]) < 0) {
  return (0 - 1);
}
}
  u = (u + 1);
}
}
  v = (v + 1);
}
  int32_t kind = 1;
  while (kind <= 2) {
  int32_t q = 0;
  while (q < (c[0]).niv) {
  if ((c[0]).iv_flow[q] == f && (c[0]).iv_kind[q] == kind) {
  const char* word = "always";
  if (kind == 2) {
  word = "never";
}
  const char* ws = "'always' clause";
  if (kind == 2) {
  ws = "'never' clause";
}
  if (fb_check_pure_s(c, (c[0]).iv_expr[q], f, ws, (c[0]).iv_line[q]) < 0) {
  return (0 - 1);
}
  if (fb_check_booleanish(c, (c[0]).iv_expr[q], f, word, (c[0]).iv_line[q]) < 0) {
  return (0 - 1);
}
}
  q = (q + 1);
}
  kind = (kind + 1);
}
  int32_t pass = 0;
  while (pass < 3) {
  int32_t want = MK_STATE;
  if (pass == 1) {
  want = MK_PARAM;
}
  if (pass == 2) {
  want = MK_OUTPUT;
}
  int32_t j = 0;
  while (j < (c[0]).nmm) {
  if ((c[0]).mm_flow[j] == f && (c[0]).mm_kind[j] == want && (c[0]).mm_pipe_m[j] < 0) {
  int32_t wh = fb_where(c, "initializer of '", (c[0]).mm_name[j], "'");
  if (want == MK_OUTPUT) {
  wh = fb_where(c, "output map of '", (c[0]).mm_name[j], "'");
}
  if (fb_check_pure(c, (c[0]).mm_init[j], f, wh, (c[0]).mm_line[j]) < 0) {
  return (0 - 1);
}
}
  j = (j + 1);
}
  pass = (pass + 1);
}
  int32_t has_conn = 0;
  int32_t z = 0;
  while (z < (c[0]).ncn) {
  if ((c[0]).cn_flow[z] == f) {
  has_conn = 1;
}
  z = (z + 1);
}
  if (has_conn == 1 || nchildren > 0) {
  return fb_validate_connect(c, f);
}
  return 0;
}

int32_t fb_becomes_seen(Fb* c, int32_t kind, int32_t owner, int32_t b) {
  int32_t k = 0;
  while (k < b) {
  if ((c[0]).bc_kind[k] == kind && (c[0]).bc_owner[k] == owner && fb_name_eq(c, (c[0]).bc_target[k], (c[0]).bc_target[b]) == 1) {
  return 1;
}
  k = (k + 1);
}
  return 0;
}

void fb_mark_vars(Fb* c, int32_t x) {
  if (x < 0) {
  return;
}
  int32_t k = (c[0]).nk[x];
  if (k == N_VAR) {
  (c[0]).tvar[(c[0]).ntok[x]] = 1;
  return;
}
  if (k == N_BIN || k == N_INDEX) {
  fb_mark_vars(c, (c[0]).na[x]);
  fb_mark_vars(c, (c[0]).nb[x]);
  return;
}
  if (k == N_UN || k == N_CAST || k == N_FIELD || k == N_TRY) {
  fb_mark_vars(c, (c[0]).na[x]);
  return;
}
  if (k == N_CALL || k == N_ARRAY || k == N_VEC) {
  int32_t a = (c[0]).na[x];
  while (a >= 0) {
  fb_mark_vars(c, a);
  a = (c[0]).nx[a];
}
}
}

int32_t fb_is_member_tok(Fb* c, int32_t f, int32_t t) {
  int32_t i = 0;
  while (i < (c[0]).nmm) {
  if ((c[0]).mm_flow[i] == f && (c[0]).mm_kind[i] != MK_DEAD) {
  if (fb_tok_is(c, t, (const char*)(fb_s(c, (c[0]).mm_name[i]))) == 1) {
  return 1;
}
}
  i = (i + 1);
}
  int32_t s = (c[0]).ts[t];
  int32_t e = (c[0]).te[t];
  uint8_t* p = (uint8_t*)((c[0]).src);
  if ((e - s) > 12 && fb_tok_starts(c, t, "__every_") == 1 && fb_tok_ends(c, t, "_acc") == 1) {
  int32_t k = fb_digits_value(p, (s + 8), (e - 4));
  if (k >= 0 && k < fb_count_everys(c, f)) {
  return 1;
}
}
  if ((e - s) > 13 && fb_tok_starts(c, t, "__guard_") == 1 && fb_tok_ends(c, t, "_prev") == 1) {
  int32_t k2 = fb_digits_value(p, (s + 8), (e - 5));
  if (k2 >= 0 && k2 < fb_count_whens(c, f)) {
  return 1;
}
}
  return 0;
}

int32_t fb_tok_starts(Fb* c, int32_t t, const char* lit) {
  uint8_t* lp = (uint8_t*)((uint8_t*)(lit));
  int32_t s = (c[0]).ts[t];
  int32_t i = 0;
  while (lp[i] != 0) {
  if ((s + i) >= (c[0]).te[t]) {
  return 0;
}
  if ((c[0]).src[(s + i)] != lp[i]) {
  return 0;
}
  i = (i + 1);
}
  return 1;
}

int32_t fb_tok_ends(Fb* c, int32_t t, const char* lit) {
  int32_t ll = (int32_t)(strlen(lit));
  uint8_t* lp = (uint8_t*)((uint8_t*)(lit));
  int32_t e = (c[0]).te[t];
  if ((e - (c[0]).ts[t]) < ll) {
  return 0;
}
  int32_t i = 0;
  while (i < ll) {
  if ((c[0]).src[((e - ll) + i)] != lp[i]) {
  return 0;
}
  i = (i + 1);
}
  return 1;
}

int32_t fb_digits_value(uint8_t* p, int32_t s, int32_t e) {
  if (s >= e) {
  return (0 - 1);
}
  if (p[s] == 48 && (e - s) > 1) {
  return (0 - 1);
}
  int32_t v = 0;
  int32_t i = s;
  while (i < e) {
  if (fb_is_digit(p[i]) == 0) {
  return (0 - 1);
}
  if (v > 100000000) {
  return (0 - 1);
}
  v = ((v * 10) + (int32_t)((p[i] - 48)));
  i = (i + 1);
}
  return v;
}

int32_t fb_count_everys(Fb* c, int32_t f) {
  int32_t n = 0;
  int32_t i = 0;
  while (i < (c[0]).ney) {
  if ((c[0]).ey_flow[i] == f) {
  n = (n + 1);
}
  i = (i + 1);
}
  return n;
}

int32_t fb_count_whens(Fb* c, int32_t f) {
  int32_t n = 0;
  int32_t i = 0;
  while (i < (c[0]).nwh) {
  if ((c[0]).wh_flow[i] == f) {
  n = (n + 1);
}
  i = (i + 1);
}
  return n;
}

void fb_emit_expr(Fb* c, FbBuf* b, int32_t x) {
  int32_t f = (c[0]).cur;
  int32_t s = (c[0]).nfs[x];
  int32_t e = (c[0]).nfe[x];
  uint8_t* p = (uint8_t*)((c[0]).src);
  int32_t t = s;
  while (t < e) {
  if (t > s) {
  int32_t g0 = (c[0]).te[(t - 1)];
  int32_t g1 = (c[0]).ts[t];
  if (g1 > g0) {
  int32_t plain = 1;
  int32_t k = g0;
  while (k < g1) {
  if (p[k] != 32 && p[k] != 9) {
  plain = 0;
}
  k = (k + 1);
}
  if (plain == 1) {
  fb_put_span(b, p, g0, g1);
} else {
  fb_putc(b, 32);
}
}
}
  if ((c[0]).tvar[t] == 1 && fb_is_member_tok(c, f, t) == 1) {
  fb_puts(b, "self.");
}
  fb_put_span(b, p, (c[0]).ts[t], (c[0]).te[t]);
  t = (t + 1);
}
}

void fb_put_name(Fb* c, FbBuf* b, int32_t off) {
  fb_puts(b, (const char*)(fb_s(c, off)));
}

void fb_put_self(Fb* c, FbBuf* b, int32_t off) {
  fb_puts(b, "self.");
  fb_put_name(c, b, off);
}

void fb_put_seconds(FbBuf* b, int64_t ns) {
  if (ns == 0) {
  fb_puts(b, "0.0");
  return;
}
  FbBuf* db = (FbBuf*)(fb_buf_new(32));
  fb_put_i64(db, ns);
  int32_t full = (db[0]).len;
  int32_t nd = full;
  while (nd > 1 && (db[0]).p[(nd - 1)] == 48) {
  nd = (nd - 1);
}
  int32_t decpt = (full - 9);
  uint8_t* d = (uint8_t*)((db[0]).p);
  if (decpt <= (0 - 4) || decpt > 16) {
  fb_putc(b, d[0]);
  if (nd > 1) {
  fb_putc(b, 46);
  fb_put_span(b, d, 1, nd);
}
  fb_putc(b, 101);
  int32_t ex = (decpt - 1);
  if (ex < 0) {
  fb_putc(b, 45);
} else {
  fb_putc(b, 43);
}
  int32_t ax = ex;
  if (ax < 0) {
  ax = (0 - ax);
}
  if (ax < 10) {
  fb_putc(b, 48);
}
  fb_put_int(b, ax);
} else {
  if (decpt <= 0) {
  fb_puts(b, "0.");
  int32_t z = 0;
  while (z < (0 - decpt)) {
  fb_putc(b, 48);
  z = (z + 1);
}
  fb_put_span(b, d, 0, nd);
} else {
  if (decpt >= nd) {
  fb_put_span(b, d, 0, nd);
  int32_t z2 = nd;
  while (z2 < decpt) {
  fb_putc(b, 48);
  z2 = (z2 + 1);
}
  fb_puts(b, ".0");
} else {
  fb_put_span(b, d, 0, decpt);
  fb_putc(b, 46);
  fb_put_span(b, d, decpt, nd);
}
}
}
  fb_buf_free(db);
}

void fb_put_mtype(Fb* c, FbBuf* b, int32_t i) {
  fb_put_name(c, b, (c[0]).mm_type[i]);
}

int32_t fb_is_float_type(Fb* c, int32_t ty) {
  if (fb_name_is(c, ty, "f64") == 1 || fb_name_is(c, ty, "f32") == 1) {
  return 1;
}
  return 0;
}

void fb_put_dtype(Fb* c, FbBuf* b, int32_t i) {
  if (fb_is_float_type(c, (c[0]).mm_type[i]) == 1) {
  fb_put_mtype(c, b, i);
} else {
  fb_puts(b, "f64");
}
}

void fb_put_dt(Fb* c, FbBuf* b, int32_t i) {
  if (fb_name_is(c, (c[0]).mm_type[i], "f32") == 1) {
  fb_puts(b, "(dt as f32)");
} else {
  fb_puts(b, "dt");
}
}

int32_t fb_field_count(Fb* c, int32_t f) {
  int32_t n = 0;
  int32_t r = 0;
  while (r < 5) {
  n = (n + fb_count_members(c, f, fb_field_kind(r)));
  r = (r + 1);
}
  return ((n + fb_count_everys(c, f)) + fb_count_whens(c, f));
}

int32_t fb_field_kind(int32_t r) {
  if (r == 0) {
  return MK_CHILD;
}
  if (r == 1) {
  return MK_STATE;
}
  if (r == 2) {
  return MK_INPUT;
}
  if (r == 3) {
  return MK_OUTPUT;
}
  return MK_PARAM;
}

void fb_put_zero(Fb* c, FbBuf* b, int32_t ty) {
  if (fb_name_is(c, ty, "i64") == 1) {
  fb_puts(b, "0");
  return;
}
  if (fb_is_float_type(c, ty) == 1) {
  fb_puts(b, "0.0");
  return;
}
  if (fb_find_flow(c, ty) < 0) {
  fb_puts(b, "(0.0 as ");
  fb_put_name(c, b, ty);
  fb_puts(b, ")");
  return;
}
  fb_put_name(c, b, ty);
  fb_puts(b, "_new()");
}

void fb_emit_struct(Fb* c, FbBuf* b, int32_t f) {
  fb_puts(b, "struct ");
  fb_put_fname(b, c, f);
  fb_puts(b, " { ");
  int32_t first = 1;
  int32_t r = 0;
  while (r < 5) {
  int32_t kind = fb_field_kind(r);
  int32_t n = fb_count_members(c, f, kind);
  int32_t k = 0;
  while (k < n) {
  int32_t i = fb_nth_member(c, f, kind, k);
  if (first == 0) {
  fb_puts(b, ", ");
}
  first = 0;
  fb_put_name(c, b, (c[0]).mm_name[i]);
  fb_puts(b, ": ");
  fb_put_mtype(c, b, i);
  k = (k + 1);
}
  r = (r + 1);
}
  int32_t ne = fb_count_everys(c, f);
  int32_t j = 0;
  while (j < ne) {
  if (first == 0) {
  fb_puts(b, ", ");
}
  first = 0;
  fb_puts(b, "__every_");
  fb_put_int(b, j);
  fb_puts(b, "_acc: i64");
  j = (j + 1);
}
  int32_t nw = fb_count_whens(c, f);
  j = 0;
  while (j < nw) {
  if (first == 0) {
  fb_puts(b, ", ");
}
  first = 0;
  fb_puts(b, "__guard_");
  fb_put_int(b, j);
  fb_puts(b, "_prev: f64");
  j = (j + 1);
}
  fb_puts(b, " }");
}

void fb_fn_head(Fb* c, FbBuf* b, int32_t f, const char* suffix, const char* params, const char* ret) {
  fb_puts(b, "@flow_api function ");
  fb_put_fname(b, c, f);
  fb_puts(b, suffix);
  fb_puts(b, "(");
  if (strlen(params) > 0) {
  fb_puts(b, params);
}
  fb_puts(b, ") -> ");
  fb_puts(b, ret);
  fb_puts(b, " { ");
}

void fb_self_param(Fb* c, FbBuf* b, int32_t f) {
  fb_puts(b, "self: ptr<");
  fb_put_fname(b, c, f);
  fb_puts(b, ">");
}

void fb_emit_new(Fb* c, FbBuf* b, int32_t f) {
  fb_fn_head(c, b, f, "_new", "", (const char*)(fb_s(c, (c[0]).f_name[f])));
  fb_puts(b, "let mut __self: ");
  fb_put_fname(b, c, f);
  fb_puts(b, " = ");
  fb_put_fname(b, c, f);
  fb_puts(b, " { ");
  int32_t first = 1;
  int32_t r = 0;
  while (r < 5) {
  int32_t kind = fb_field_kind(r);
  int32_t n = fb_count_members(c, f, kind);
  int32_t k = 0;
  while (k < n) {
  int32_t i = fb_nth_member(c, f, kind, k);
  if (first == 0) {
  fb_puts(b, ", ");
}
  first = 0;
  fb_put_name(c, b, (c[0]).mm_name[i]);
  fb_puts(b, ": ");
  fb_put_zero(c, b, (c[0]).mm_type[i]);
  k = (k + 1);
}
  r = (r + 1);
}
  int32_t ne = fb_count_everys(c, f);
  int32_t j = 0;
  while (j < ne) {
  if (first == 0) {
  fb_puts(b, ", ");
}
  first = 0;
  fb_puts(b, "__every_");
  fb_put_int(b, j);
  fb_puts(b, "_acc: 0");
  j = (j + 1);
}
  int32_t nw = fb_count_whens(c, f);
  j = 0;
  while (j < nw) {
  if (first == 0) {
  fb_puts(b, ", ");
}
  first = 0;
  fb_puts(b, "__guard_");
  fb_put_int(b, j);
  fb_puts(b, "_prev: 0.0");
  j = (j + 1);
}
  fb_puts(b, " }; ");
  fb_put_fname(b, c, f);
  fb_puts(b, "_init(&__self); return __self; }");
}

int32_t fb_nth_when(Fb* c, int32_t f, int32_t k) {
  int32_t n = 0;
  int32_t i = 0;
  while (i < (c[0]).nwh) {
  if ((c[0]).wh_flow[i] == f) {
  if (n == k) {
  return i;
}
  n = (n + 1);
}
  i = (i + 1);
}
  return (0 - 1);
}

int32_t fb_nth_every(Fb* c, int32_t f, int32_t k) {
  int32_t n = 0;
  int32_t i = 0;
  while (i < (c[0]).ney) {
  if ((c[0]).ey_flow[i] == f) {
  if (n == k) {
  return i;
}
  n = (n + 1);
}
  i = (i + 1);
}
  return (0 - 1);
}

void fb_emit_guard(Fb* c, FbBuf* b, int32_t f, int32_t w) {
  int32_t st = fb_find_member(c, f, MK_STATE, (c[0]).wh_target[w]);
  int32_t narrow = fb_name_is(c, (c[0]).mm_type[st], "f32");
  if (narrow == 1) {
  fb_puts(b, "((");
}
  fb_put_self(c, b, (c[0]).wh_target[w]);
  fb_puts(b, " - (");
  fb_emit_expr(c, b, (c[0]).wh_thr[w]);
  fb_puts(b, ")");
  if (narrow == 1) {
  fb_puts(b, ") as f64)");
}
}

int32_t fb_has_outputs(Fb* c, int32_t f) {
  if (fb_count_members(c, f, MK_OUTPUT) > 0) {
  return 1;
}
  return 0;
}

void fb_emit_init(Fb* c, FbBuf* b, int32_t f) {
  fb_puts(b, "@flow_api function ");
  fb_put_fname(b, c, f);
  fb_puts(b, "_init(");
  fb_self_param(c, b, f);
  fb_puts(b, ") -> void { ");
  int32_t np = fb_count_members(c, f, MK_PARAM);
  int32_t k = 0;
  while (k < np) {
  int32_t i = fb_nth_member(c, f, MK_PARAM, k);
  fb_put_self(c, b, (c[0]).mm_name[i]);
  fb_puts(b, " = ");
  fb_emit_expr(c, b, (c[0]).mm_init[i]);
  fb_puts(b, "; ");
  k = (k + 1);
}
  int32_t ni = fb_count_members(c, f, MK_INPUT);
  k = 0;
  while (k < ni) {
  int32_t i2 = fb_nth_member(c, f, MK_INPUT, k);
  fb_put_self(c, b, (c[0]).mm_name[i2]);
  fb_puts(b, " = 0.0; ");
  k = (k + 1);
}
  int32_t ns = fb_count_members(c, f, MK_STATE);
  k = 0;
  while (k < ns) {
  int32_t i3 = fb_nth_member(c, f, MK_STATE, k);
  fb_put_self(c, b, (c[0]).mm_name[i3]);
  fb_puts(b, " = ");
  if ((c[0]).mm_init[i3] >= 0) {
  fb_emit_expr(c, b, (c[0]).mm_init[i3]);
} else {
  fb_puts(b, "0.0");
}
  fb_puts(b, "; ");
  k = (k + 1);
}
  int32_t nc = fb_count_members(c, f, MK_CHILD);
  k = 0;
  while (k < nc) {
  int32_t i4 = fb_nth_member(c, f, MK_CHILD, k);
  fb_put_name(c, b, (c[0]).mm_type[i4]);
  fb_puts(b, "_init(&");
  fb_put_self(c, b, (c[0]).mm_name[i4]);
  fb_puts(b, "); ");
  int32_t pk = (c[0]).mm_params[i4];
  while (pk >= 0) {
  fb_put_self(c, b, (c[0]).mm_name[i4]);
  fb_putc(b, 46);
  fb_put_span(b, (c[0]).src, (c[0]).ts[(c[0]).ntok[pk]], (c[0]).te[(c[0]).ntok[pk]]);
  fb_puts(b, " = ");
  fb_emit_expr(c, b, (c[0]).na[pk]);
  fb_puts(b, "; ");
  pk = (c[0]).nx[pk];
}
  k = (k + 1);
}
  int32_t ne = fb_count_everys(c, f);
  k = 0;
  while (k < ne) {
  fb_puts(b, "self.__every_");
  fb_put_int(b, k);
  fb_puts(b, "_acc = 0; ");
  k = (k + 1);
}
  int32_t nw = fb_count_whens(c, f);
  k = 0;
  while (k < nw) {
  fb_puts(b, "self.__guard_");
  fb_put_int(b, k);
  fb_puts(b, "_prev = ");
  fb_emit_guard(c, b, f, fb_nth_when(c, f, k));
  fb_puts(b, "; ");
  k = (k + 1);
}
  if (fb_has_outputs(c, f) == 1) {
  fb_put_fname(b, c, f);
  fb_puts(b, "_outputs(self); ");
}
  fb_puts(b, "}");
}

int32_t fb_nth_evolved(Fb* c, int32_t f, int32_t k) {
  int32_t ns = fb_count_members(c, f, MK_STATE);
  int32_t n = 0;
  int32_t s = 0;
  while (s < ns) {
  int32_t i = fb_nth_member(c, f, MK_STATE, s);
  if (fb_evolve_of(c, f, (c[0]).mm_name[i]) >= 0) {
  if (n == k) {
  return i;
}
  n = (n + 1);
}
  s = (s + 1);
}
  return (0 - 1);
}

int32_t fb_count_evolved(Fb* c, int32_t f) {
  int32_t n = 0;
  while (fb_nth_evolved(c, f, n) >= 0) {
  n = (n + 1);
}
  return n;
}

void fb_emit_derivs(Fb* c, FbBuf* b, int32_t f) {
  fb_puts(b, "@flow_api function ");
  fb_put_fname(b, c, f);
  fb_puts(b, "_derivs(");
  fb_self_param(c, b, f);
  int32_t nev = fb_count_evolved(c, f);
  int32_t k = 0;
  while (k < nev) {
  int32_t i = fb_nth_evolved(c, f, k);
  fb_puts(b, ", d_");
  fb_put_name(c, b, (c[0]).mm_name[i]);
  fb_puts(b, ": ptr<");
  fb_put_dtype(c, b, i);
  fb_puts(b, ">");
  k = (k + 1);
}
  fb_puts(b, ") -> void { ");
  k = 0;
  while (k < nev) {
  int32_t i2 = fb_nth_evolved(c, f, k);
  int32_t e = fb_evolve_of(c, f, (c[0]).mm_name[i2]);
  fb_puts(b, "d_");
  fb_put_name(c, b, (c[0]).mm_name[i2]);
  fb_puts(b, "[0] = ");
  fb_emit_expr(c, b, (c[0]).ev_expr[e]);
  fb_puts(b, "; ");
  k = (k + 1);
}
  fb_puts(b, "}");
}

void fb_emit_derivs_call(Fb* c, FbBuf* b, int32_t f, const char* stage) {
  fb_put_fname(b, c, f);
  fb_puts(b, "_derivs(self");
  int32_t nev = fb_count_evolved(c, f);
  int32_t k = 0;
  while (k < nev) {
  int32_t i = fb_nth_evolved(c, f, k);
  fb_puts(b, ", &");
  fb_puts(b, stage);
  fb_putc(b, 95);
  fb_put_name(c, b, (c[0]).mm_name[i]);
  k = (k + 1);
}
  fb_puts(b, "); ");
}

void fb_emit_euler(Fb* c, FbBuf* b, int32_t f) {
  int32_t nev = fb_count_evolved(c, f);
  int32_t k = 0;
  while (k < nev) {
  int32_t i = fb_nth_evolved(c, f, k);
  fb_puts(b, "let mut d_");
  fb_put_name(c, b, (c[0]).mm_name[i]);
  fb_puts(b, ": ");
  fb_put_dtype(c, b, i);
  fb_puts(b, " = 0.0; ");
  k = (k + 1);
}
  if (nev > 0) {
  fb_emit_derivs_call(c, b, f, "d");
}
  k = 0;
  while (k < nev) {
  int32_t i2 = fb_nth_evolved(c, f, k);
  int32_t nm = (c[0]).mm_name[i2];
  fb_put_self(c, b, nm);
  fb_puts(b, " = ");
  fb_put_self(c, b, nm);
  fb_puts(b, " + ");
  int32_t dim = (1 - fb_is_float_type(c, (c[0]).mm_type[i2]));
  if (dim == 1) {
  fb_puts(b, "((");
}
  fb_puts(b, "d_");
  fb_put_name(c, b, nm);
  fb_puts(b, " * ");
  fb_put_dt(c, b, i2);
  if (dim == 1) {
  fb_puts(b, ") as ");
  fb_put_mtype(c, b, i2);
  fb_puts(b, ")");
}
  fb_puts(b, "; ");
  k = (k + 1);
}
}

void fb_emit_rk_stage(Fb* c, FbBuf* b, int32_t f, const char* stage, int32_t scale) {
  int32_t nev = fb_count_evolved(c, f);
  int32_t k = 0;
  while (k < nev) {
  int32_t i = fb_nth_evolved(c, f, k);
  int32_t nm = (c[0]).mm_name[i];
  fb_put_self(c, b, nm);
  fb_puts(b, " = y0_");
  fb_put_name(c, b, nm);
  fb_puts(b, " + ");
  fb_puts(b, stage);
  fb_putc(b, 95);
  fb_put_name(c, b, nm);
  fb_puts(b, " * ");
  if (scale == 1) {
  fb_puts(b, "(");
  fb_put_dt(c, b, i);
  fb_puts(b, " * 0.5)");
} else {
  fb_put_dt(c, b, i);
}
  fb_puts(b, "; ");
  k = (k + 1);
}
}

void fb_emit_rk4(Fb* c, FbBuf* b, int32_t f) {
  int32_t nev = fb_count_evolved(c, f);
  int32_t k = 0;
  while (k < nev) {
  int32_t i = fb_nth_evolved(c, f, k);
  fb_puts(b, "let y0_");
  fb_put_name(c, b, (c[0]).mm_name[i]);
  fb_puts(b, ": ");
  fb_put_mtype(c, b, i);
  fb_puts(b, " = ");
  fb_put_self(c, b, (c[0]).mm_name[i]);
  fb_puts(b, "; ");
  k = (k + 1);
}
  int32_t st = 1;
  while (st <= 4) {
  k = 0;
  while (k < nev) {
  int32_t i2 = fb_nth_evolved(c, f, k);
  fb_puts(b, "let mut k");
  fb_put_int(b, st);
  fb_putc(b, 95);
  fb_put_name(c, b, (c[0]).mm_name[i2]);
  fb_puts(b, ": ");
  fb_put_mtype(c, b, i2);
  fb_puts(b, " = 0.0; ");
  k = (k + 1);
}
  st = (st + 1);
}
  fb_emit_derivs_call(c, b, f, "k1");
  fb_emit_rk_stage(c, b, f, "k1", 1);
  fb_emit_derivs_call(c, b, f, "k2");
  fb_emit_rk_stage(c, b, f, "k2", 1);
  fb_emit_derivs_call(c, b, f, "k3");
  fb_emit_rk_stage(c, b, f, "k3", 2);
  fb_emit_derivs_call(c, b, f, "k4");
  k = 0;
  while (k < nev) {
  int32_t i3 = fb_nth_evolved(c, f, k);
  int32_t nm = (c[0]).mm_name[i3];
  fb_put_self(c, b, nm);
  fb_puts(b, " = y0_");
  fb_put_name(c, b, nm);
  fb_puts(b, " + (k1_");
  fb_put_name(c, b, nm);
  fb_puts(b, " + k2_");
  fb_put_name(c, b, nm);
  fb_puts(b, " * 2.0 + k3_");
  fb_put_name(c, b, nm);
  fb_puts(b, " * 2.0 + k4_");
  fb_put_name(c, b, nm);
  fb_puts(b, ") * (");
  fb_put_dt(c, b, i3);
  fb_puts(b, " / 6.0); ");
  k = (k + 1);
}
}

void fb_emit_every(Fb* c, FbBuf* b, int32_t f, int32_t k) {
  int32_t v = fb_nth_every(c, f, k);
  FbBuf* acc = (FbBuf*)(fb_buf_new(32));
  fb_puts(acc, "self.__every_");
  fb_put_int(acc, k);
  fb_puts(acc, "_acc");
  const char* a = (const char*)((acc[0]).p);
  fb_puts(b, a);
  fb_puts(b, " = ");
  fb_puts(b, a);
  fb_puts(b, " + __dt_ns; let mut __every_");
  fb_put_int(b, k);
  fb_puts(b, "_n: i64 = 0; while ");
  fb_puts(b, a);
  fb_puts(b, " >= ");
  fb_put_i64(b, (c[0]).ey_ns[v]);
  fb_puts(b, " && __every_");
  fb_put_int(b, k);
  fb_puts(b, "_n < 1024 { ");
  fb_puts(b, a);
  fb_puts(b, " = ");
  fb_puts(b, a);
  fb_puts(b, " - ");
  fb_put_i64(b, (c[0]).ey_ns[v]);
  fb_puts(b, "; __every_");
  fb_put_int(b, k);
  fb_puts(b, "_n = __every_");
  fb_put_int(b, k);
  fb_puts(b, "_n + 1; ");
  fb_emit_staged(c, b, f, 2, v, "__tick_", k);
  fb_puts(b, "} ");
  fb_buf_free(acc);
}

void fb_emit_staged(Fb* c, FbBuf* b, int32_t f, int32_t kind, int32_t owner, const char* prefix, int32_t k) {
  int32_t u = 0;
  while (u < (c[0]).nbc) {
  if ((c[0]).bc_kind[u] == kind && (c[0]).bc_owner[u] == owner) {
  int32_t tg = (c[0]).bc_target[u];
  int32_t st = fb_find_member(c, f, MK_STATE, tg);
  fb_puts(b, "let ");
  fb_puts(b, prefix);
  fb_put_int(b, k);
  fb_putc(b, 95);
  fb_put_name(c, b, tg);
  fb_puts(b, ": ");
  fb_put_mtype(c, b, st);
  fb_puts(b, " = ");
  fb_emit_expr(c, b, (c[0]).bc_expr[u]);
  fb_puts(b, "; ");
}
  u = (u + 1);
}
  u = 0;
  while (u < (c[0]).nbc) {
  if ((c[0]).bc_kind[u] == kind && (c[0]).bc_owner[u] == owner) {
  int32_t tg2 = (c[0]).bc_target[u];
  fb_put_self(c, b, tg2);
  fb_puts(b, " = ");
  fb_puts(b, prefix);
  fb_put_int(b, k);
  fb_putc(b, 95);
  fb_put_name(c, b, tg2);
  fb_puts(b, "; ");
}
  u = (u + 1);
}
}

void fb_emit_event(Fb* c, FbBuf* b, int32_t f, int32_t k) {
  int32_t w = fb_nth_when(c, f, k);
  fb_puts(b, "let __g_");
  fb_put_int(b, k);
  fb_puts(b, ": f64 = ");
  fb_emit_guard(c, b, f, w);
  fb_puts(b, "; if (__g_");
  fb_put_int(b, k);
  fb_puts(b, " < 0.0) != (self.__guard_");
  fb_put_int(b, k);
  fb_puts(b, "_prev < 0.0) || __g_");
  fb_put_int(b, k);
  fb_puts(b, " == 0.0 { ");
  fb_emit_staged(c, b, f, 1, w, "__reset_", k);
  fb_puts(b, "} self.__guard_");
  fb_put_int(b, k);
  fb_puts(b, "_prev = ");
  fb_emit_guard(c, b, f, w);
  fb_puts(b, "; ");
}

int32_t fb_topo_children(Fb* c, int32_t f, int32_t* order) {
  int32_t n = fb_count_members(c, f, MK_CHILD);
  int32_t* indeg = (int32_t*)((int32_t*)(malloc(((int64_t)((n + 1)) * 4))));
  int32_t* done = (int32_t*)((int32_t*)(malloc(((int64_t)((n + 1)) * 4))));
  int32_t k = 0;
  while (k < n) {
  indeg[k] = 0;
  done[k] = 0;
  k = (k + 1);
}
  int32_t i = 0;
  while (i < (c[0]).ncn) {
  if ((c[0]).cn_flow[i] == f && fb_conn_combo(c, f, i) == 1) {
  int32_t d = fb_child_index(c, f, (c[0]).cn_dm[i]);
  int32_t s = fb_child_index(c, f, (c[0]).cn_sm[i]);
  if (d >= 0 && s >= 0) {
  indeg[d] = (indeg[d] + 1);
}
}
  i = (i + 1);
}
  int32_t placed = 0;
  int32_t cyclic = 0;
  while (placed < n && cyclic == 0) {
  int32_t pick = (0 - 1);
  k = 0;
  while (k < n && pick < 0) {
  if (done[k] == 0 && indeg[k] == 0) {
  pick = k;
}
  k = (k + 1);
}
  if (pick < 0) {
  cyclic = 1;
} else {
  done[pick] = 1;
  order[placed] = fb_nth_member(c, f, MK_CHILD, pick);
  placed = (placed + 1);
  int32_t pn = (c[0]).mm_name[order[(placed - 1)]];
  i = 0;
  while (i < (c[0]).ncn) {
  if ((c[0]).cn_flow[i] == f && fb_conn_combo(c, f, i) == 1 && fb_name_eq(c, (c[0]).cn_sm[i], pn) == 1) {
  int32_t d2 = fb_child_index(c, f, (c[0]).cn_dm[i]);
  if (d2 >= 0) {
  indeg[d2] = (indeg[d2] - 1);
}
}
  i = (i + 1);
}
}
}
  if (cyclic == 1) {
  k = 0;
  while (k < n) {
  order[k] = fb_nth_member(c, f, MK_CHILD, k);
  k = (k + 1);
}
}
  free((uint8_t*)(indeg));
  free((uint8_t*)(done));
  return n;
}

void fb_emit_child_steps(Fb* c, FbBuf* b, int32_t f) {
  int32_t n = fb_count_members(c, f, MK_CHILD);
  if (n == 0) {
  return;
}
  int32_t* order = (int32_t*)((int32_t*)(malloc(((int64_t)((n + 1)) * 4))));
  fb_topo_children(c, f, order);
  int32_t k = 0;
  while (k < n) {
  int32_t ch = order[k];
  int32_t cn = (c[0]).mm_name[ch];
  int32_t i = 0;
  while (i < (c[0]).ncn) {
  if ((c[0]).cn_flow[i] == f && fb_name_eq(c, (c[0]).cn_dm[i], cn) == 1) {
  fb_put_self(c, b, (c[0]).cn_dm[i]);
  fb_putc(b, 46);
  fb_put_name(c, b, (c[0]).cn_dp[i]);
  fb_puts(b, " = ");
  if (fb_name_is(c, (c[0]).cn_sm[i], "") == 1) {
  fb_put_self(c, b, (c[0]).cn_sp[i]);
} else {
  fb_put_self(c, b, (c[0]).cn_sm[i]);
  fb_putc(b, 46);
  fb_put_name(c, b, (c[0]).cn_sp[i]);
}
  fb_puts(b, "; ");
}
  i = (i + 1);
}
  fb_put_name(c, b, (c[0]).mm_type[ch]);
  fb_puts(b, "_step(&");
  fb_put_self(c, b, cn);
  fb_puts(b, ", dt); ");
  k = (k + 1);
}
  free((uint8_t*)(order));
}

int32_t fb_count_clauses(Fb* c, int32_t f) {
  int32_t n = 0;
  int32_t i = 0;
  while (i < (c[0]).niv) {
  if ((c[0]).iv_flow[i] == f) {
  n = (n + 1);
}
  i = (i + 1);
}
  return n;
}

int32_t fb_nth_clause(Fb* c, int32_t f, int32_t idx) {
  int32_t n = 0;
  int32_t kind = 1;
  while (kind <= 2) {
  int32_t i = 0;
  while (i < (c[0]).niv) {
  if ((c[0]).iv_flow[i] == f && (c[0]).iv_kind[i] == kind) {
  if (n == idx) {
  return i;
}
  n = (n + 1);
}
  i = (i + 1);
}
  kind = (kind + 1);
}
  return (0 - 1);
}

void fb_put_escaped(FbBuf* b, uint8_t* s) {
  int32_t i = 0;
  while (s[i] != 0) {
  if (s[i] == 92 || s[i] == 34) {
  fb_putc(b, 92);
}
  fb_putc(b, s[i]);
  i = (i + 1);
}
}

void fb_emit_step(Fb* c, FbBuf* b, int32_t f) {
  fb_puts(b, "@flow_api function ");
  fb_put_fname(b, c, f);
  fb_puts(b, "_step(");
  fb_self_param(c, b, f);
  fb_puts(b, ", dt: f64) -> void { ");
  if ((c[0]).f_solver[f] == 1 && fb_name_is(c, (c[0]).f_method[f], "rk4") == 1) {
  fb_emit_rk4(c, b, f);
} else {
  fb_emit_euler(c, b, f);
}
  int32_t ne = fb_count_everys(c, f);
  if (ne > 0) {
  fb_puts(b, "let __dt_ns: i64 = ((dt * 1000000000.0) as i64); ");
}
  int32_t k = 0;
  while (k < ne) {
  fb_emit_every(c, b, f, k);
  k = (k + 1);
}
  int32_t nw = fb_count_whens(c, f);
  k = 0;
  while (k < nw) {
  fb_emit_event(c, b, f, k);
  k = (k + 1);
}
  if (fb_has_outputs(c, f) == 1) {
  fb_put_fname(b, c, f);
  fb_puts(b, "_outputs(self); ");
}
  fb_emit_child_steps(c, b, f);
  int32_t nclauses = fb_count_clauses(c, f);
  if (nclauses > 0) {
  fb_puts(b, "let __viol: i32 = ");
  fb_put_fname(b, c, f);
  fb_puts(b, "_check(self); ");
  int32_t q = 0;
  while (q < nclauses) {
  int32_t cl = fb_nth_clause(c, f, q);
  fb_puts(b, "if __viol == ");
  fb_put_int(b, (q + 1));
  fb_puts(b, " { flow_panic(\"");
  FbBuf* mb = (FbBuf*)(fb_buf_new(64));
  fb_put_fname(mb, c, f);
  fb_putc(mb, 58);
  fb_put_int(mb, (c[0]).iv_line[cl]);
  fb_puts(mb, ": invariant violated: ");
  fb_puts(mb, (const char*)(fb_s(c, (c[0]).iv_text[cl])));
  fb_put_escaped(b, (mb[0]).p);
  fb_buf_free(mb);
  fb_puts(b, "\"); } ");
  q = (q + 1);
}
}
  fb_puts(b, "}");
}

void fb_emit_default_dt(Fb* c, FbBuf* b, int32_t f) {
  fb_puts(b, "@flow_api function ");
  fb_put_fname(b, c, f);
  fb_puts(b, "_default_dt() -> f64 { return ");
  if ((c[0]).f_solver[f] == 1) {
  fb_put_seconds(b, (c[0]).f_dt_ns[f]);
} else {
  fb_put_seconds(b, 1000000);
}
  fb_puts(b, "; }");
}

void fb_emit_outputs(Fb* c, FbBuf* b, int32_t f) {
  fb_puts(b, "@flow_api function ");
  fb_put_fname(b, c, f);
  fb_puts(b, "_outputs(");
  fb_self_param(c, b, f);
  fb_puts(b, ") -> void { ");
  int32_t no = fb_count_members(c, f, MK_OUTPUT);
  int32_t k = 0;
  while (k < no) {
  int32_t o = fb_nth_member(c, f, MK_OUTPUT, k);
  fb_put_self(c, b, (c[0]).mm_name[o]);
  fb_puts(b, " = ");
  if ((c[0]).mm_pipe_m[o] >= 0) {
  fb_put_self(c, b, (c[0]).mm_pipe_m[o]);
  fb_putc(b, 46);
  fb_put_name(c, b, (c[0]).mm_pipe_p[o]);
} else {
  fb_emit_expr(c, b, (c[0]).mm_init[o]);
}
  fb_puts(b, "; ");
  k = (k + 1);
}
  fb_puts(b, "}");
}

void fb_emit_check(Fb* c, FbBuf* b, int32_t f) {
  fb_puts(b, "@flow_api function ");
  fb_put_fname(b, c, f);
  fb_puts(b, "_check(");
  fb_self_param(c, b, f);
  fb_puts(b, ") -> i32 { ");
  int32_t n = fb_count_clauses(c, f);
  int32_t q = 0;
  while (q < n) {
  int32_t cl = fb_nth_clause(c, f, q);
  if ((c[0]).iv_kind[cl] == 1) {
  fb_puts(b, "if !(");
} else {
  fb_puts(b, "if (");
}
  fb_emit_expr(c, b, (c[0]).iv_expr[cl]);
  fb_puts(b, ") { return ");
  fb_put_int(b, (q + 1));
  fb_puts(b, "; } ");
  q = (q + 1);
}
  fb_puts(b, "return 0; }");
}

void fb_mark_flow(Fb* c, int32_t f) {
  int32_t i = 0;
  while (i < (c[0]).nmm) {
  if ((c[0]).mm_flow[i] == f) {
  fb_mark_vars(c, (c[0]).mm_init[i]);
  int32_t pk = (c[0]).mm_params[i];
  while (pk >= 0) {
  fb_mark_vars(c, (c[0]).na[pk]);
  pk = (c[0]).nx[pk];
}
}
  i = (i + 1);
}
  i = 0;
  while (i < (c[0]).nev) {
  if ((c[0]).ev_flow[i] == f) {
  fb_mark_vars(c, (c[0]).ev_expr[i]);
}
  i = (i + 1);
}
  i = 0;
  while (i < (c[0]).nwh) {
  if ((c[0]).wh_flow[i] == f) {
  fb_mark_vars(c, (c[0]).wh_thr[i]);
  int32_t u = 0;
  while (u < (c[0]).nbc) {
  if ((c[0]).bc_kind[u] == 1 && (c[0]).bc_owner[u] == i) {
  fb_mark_vars(c, (c[0]).bc_expr[u]);
}
  u = (u + 1);
}
}
  i = (i + 1);
}
  i = 0;
  while (i < (c[0]).ney) {
  if ((c[0]).ey_flow[i] == f) {
  int32_t u2 = 0;
  while (u2 < (c[0]).nbc) {
  if ((c[0]).bc_kind[u2] == 2 && (c[0]).bc_owner[u2] == i) {
  fb_mark_vars(c, (c[0]).bc_expr[u2]);
}
  u2 = (u2 + 1);
}
}
  i = (i + 1);
}
  i = 0;
  while (i < (c[0]).niv) {
  if ((c[0]).iv_flow[i] == f) {
  fb_mark_vars(c, (c[0]).iv_expr[i]);
}
  i = (i + 1);
}
}

void fb_lower_flow(Fb* c, int32_t f) {
  (c[0]).cur = f;
  fb_mark_flow(c, f);
  int32_t lines = 1;
  int32_t k = (c[0]).f_start[f];
  while (k < (c[0]).f_end[f]) {
  if ((c[0]).src[k] == 10) {
  lines = (lines + 1);
}
  k = (k + 1);
}
  int32_t ndecl = 6;
  if (fb_has_outputs(c, f) == 1) {
  ndecl = (ndecl + 1);
}
  if (fb_count_clauses(c, f) > 0) {
  ndecl = (ndecl + 1);
}
  FbBuf* b = (FbBuf*)((c[0]).out);
  int32_t d = 0;
  int32_t used = 0;
  while (d < ndecl) {
  if (d > 0) {
  if (used < (lines - 1)) {
  fb_putc(b, 10);
  used = (used + 1);
} else {
  fb_putc(b, 32);
}
}
  if (d == 0) {
  fb_emit_struct(c, b, f);
}
  if (d == 1) {
  fb_emit_new(c, b, f);
}
  if (d == 2) {
  fb_emit_init(c, b, f);
}
  if (d == 3) {
  fb_emit_derivs(c, b, f);
}
  if (d == 4) {
  fb_emit_step(c, b, f);
}
  if (d == 5) {
  fb_emit_default_dt(c, b, f);
}
  if (d == 6) {
  if (fb_has_outputs(c, f) == 1) {
  fb_emit_outputs(c, b, f);
} else {
  fb_emit_check(c, b, f);
}
}
  if (d == 7) {
  fb_emit_check(c, b, f);
}
  d = (d + 1);
}
  while (used < (lines - 1)) {
  fb_putc(b, 10);
  used = (used + 1);
}
}

int32_t* fb_alloc_i32(int32_t n) {
  return (int32_t*)(malloc(((int64_t)((n + 1)) * 4)));
}

Fb* fb_ctx_new(uint8_t* src, int32_t n) {
  Fb* c = (Fb*)((Fb*)(malloc(4096)));
  (c[0]).src = src;
  (c[0]).n = n;
  int32_t tcap = (n + 2);
  (c[0]).nt = 0;
  (c[0]).tk = fb_alloc_i32(tcap);
  (c[0]).top = fb_alloc_i32(tcap);
  (c[0]).ts = fb_alloc_i32(tcap);
  (c[0]).te = fb_alloc_i32(tcap);
  (c[0]).tl = fb_alloc_i32(tcap);
  (c[0]).tc = fb_alloc_i32(tcap);
  (c[0]).tvar = fb_alloc_i32(tcap);
  (c[0]).pos = 0;
  (c[0]).nn = 0;
  (c[0]).ncap = 256;
  (c[0]).nk = fb_alloc_i32(256);
  (c[0]).nop = fb_alloc_i32(256);
  (c[0]).ntok = fb_alloc_i32(256);
  (c[0]).na = fb_alloc_i32(256);
  (c[0]).nb = fb_alloc_i32(256);
  (c[0]).nc = fb_alloc_i32(256);
  (c[0]).nx = fb_alloc_i32(256);
  (c[0]).nfs = fb_alloc_i32(256);
  (c[0]).nfe = fb_alloc_i32(256);
  (c[0]).nm = fb_buf_new(4096);
  (c[0]).nf = 0;
  (c[0]).f_name = fb_alloc_i32(FB_MAX_FLOWS);
  (c[0]).f_line = fb_alloc_i32(FB_MAX_FLOWS);
  (c[0]).f_start = fb_alloc_i32(FB_MAX_FLOWS);
  (c[0]).f_end = fb_alloc_i32(FB_MAX_FLOWS);
  (c[0]).f_solver = fb_alloc_i32(FB_MAX_FLOWS);
  (c[0]).f_dt_ns = (int64_t*)(malloc(((int64_t)((FB_MAX_FLOWS + 1)) * 8)));
  (c[0]).f_dt_text = fb_alloc_i32(FB_MAX_FLOWS);
  (c[0]).f_method = fb_alloc_i32(FB_MAX_FLOWS);
  (c[0]).f_solver_line = fb_alloc_i32(FB_MAX_FLOWS);
  (c[0]).f_rec = fb_alloc_i32(FB_MAX_FLOWS);
  (c[0]).f_rec_line = fb_alloc_i32(FB_MAX_FLOWS);
  (c[0]).f_out = fb_alloc_i32(FB_MAX_FLOWS);
  int32_t icap = ((tcap * 2) + 16);
  (c[0]).icap = icap;
  (c[0]).nmm = 0;
  (c[0]).mm_flow = fb_alloc_i32(icap);
  (c[0]).mm_kind = fb_alloc_i32(icap);
  (c[0]).mm_name = fb_alloc_i32(icap);
  (c[0]).mm_type = fb_alloc_i32(icap);
  (c[0]).mm_init = fb_alloc_i32(icap);
  (c[0]).mm_line = fb_alloc_i32(icap);
  (c[0]).mm_synth = fb_alloc_i32(icap);
  (c[0]).mm_params = fb_alloc_i32(icap);
  (c[0]).mm_pipe_m = fb_alloc_i32(icap);
  (c[0]).mm_pipe_p = fb_alloc_i32(icap);
  (c[0]).nev = 0;
  (c[0]).ev_flow = fb_alloc_i32(icap);
  (c[0]).ev_target = fb_alloc_i32(icap);
  (c[0]).ev_expr = fb_alloc_i32(icap);
  (c[0]).ev_line = fb_alloc_i32(icap);
  (c[0]).nwh = 0;
  (c[0]).wh_flow = fb_alloc_i32(icap);
  (c[0]).wh_target = fb_alloc_i32(icap);
  (c[0]).wh_thr = fb_alloc_i32(icap);
  (c[0]).wh_line = fb_alloc_i32(icap);
  (c[0]).ney = 0;
  (c[0]).ey_flow = fb_alloc_i32(icap);
  (c[0]).ey_ns = (int64_t*)(malloc(((int64_t)((icap + 1)) * 8)));
  (c[0]).ey_text = fb_alloc_i32(icap);
  (c[0]).ey_line = fb_alloc_i32(icap);
  (c[0]).nbc = 0;
  (c[0]).bc_kind = fb_alloc_i32(icap);
  (c[0]).bc_owner = fb_alloc_i32(icap);
  (c[0]).bc_target = fb_alloc_i32(icap);
  (c[0]).bc_expr = fb_alloc_i32(icap);
  (c[0]).bc_line = fb_alloc_i32(icap);
  (c[0]).niv = 0;
  (c[0]).iv_flow = fb_alloc_i32(icap);
  (c[0]).iv_kind = fb_alloc_i32(icap);
  (c[0]).iv_expr = fb_alloc_i32(icap);
  (c[0]).iv_line = fb_alloc_i32(icap);
  (c[0]).iv_text = fb_alloc_i32(icap);
  (c[0]).ncn = 0;
  (c[0]).cn_flow = fb_alloc_i32(icap);
  (c[0]).cn_sm = fb_alloc_i32(icap);
  (c[0]).cn_sp = fb_alloc_i32(icap);
  (c[0]).cn_dm = fb_alloc_i32(icap);
  (c[0]).cn_dp = fb_alloc_i32(icap);
  (c[0]).cn_line = fb_alloc_i32(icap);
  (c[0]).nrc = 0;
  (c[0]).rc_flow = fb_alloc_i32(icap);
  (c[0]).rc_name = fb_alloc_i32(icap);
  (c[0]).nnames = 0;
  (c[0]).nx_kind = fb_alloc_i32(icap);
  (c[0]).nx_name = fb_alloc_i32(icap);
  (c[0]).err = 0;
  (c[0]).err_flow = (0 - 1);
  (c[0]).err_line = 0;
  (c[0]).err_col = 0;
  (c[0]).emsg = fb_buf_new(256);
  (c[0]).ehint = fb_buf_new(256);
  (c[0]).has_hint = 0;
  (c[0]).cur = 0;
  (c[0]).out = fb_buf_new(((n * 2) + 1024));
  return c;
}

void fb_ctx_free(Fb* c) {
  free((uint8_t*)((c[0]).tk));
  free((uint8_t*)((c[0]).top));
  free((uint8_t*)((c[0]).ts));
  free((uint8_t*)((c[0]).te));
  free((uint8_t*)((c[0]).tl));
  free((uint8_t*)((c[0]).tc));
  free((uint8_t*)((c[0]).tvar));
  free((uint8_t*)((c[0]).nk));
  free((uint8_t*)((c[0]).nop));
  free((uint8_t*)((c[0]).ntok));
  free((uint8_t*)((c[0]).na));
  free((uint8_t*)((c[0]).nb));
  free((uint8_t*)((c[0]).nc));
  free((uint8_t*)((c[0]).nx));
  free((uint8_t*)((c[0]).nfs));
  free((uint8_t*)((c[0]).nfe));
  fb_buf_free((c[0]).nm);
  fb_buf_free((c[0]).emsg);
  fb_buf_free((c[0]).ehint);
  fb_buf_free((c[0]).out);
  free((uint8_t*)(c));
}

int32_t fb_decl_name(Fb* c, int32_t t) {
  int32_t nt = (t + 1);
  if (nt >= (c[0]).nt) {
  return (0 - 1);
}
  if ((c[0]).tk[nt] == TK_IDENT) {
  return nt;
}
  return (0 - 1);
}

int32_t fb_scan(Fb* c, int32_t* flows) {
  int32_t nfl = 0;
  int32_t depth = 0;
  int32_t extern_depth = (0 - 1);
  int32_t prev_extern = 0;
  int32_t t = 0;
  while (t < (c[0]).nt && (c[0]).tk[t] != TK_EOF) {
  int32_t k = (c[0]).tk[t];
  if (k == TK_OP) {
  int32_t op = (c[0]).top[t];
  if (op == OP_LBRACE || op == OP_LPAREN || op == OP_LBRACKET) {
  if (op == OP_LBRACE && prev_extern == 1 && depth == 0) {
  extern_depth = 1;
}
  depth = (depth + 1);
}
  if (op == OP_RBRACE || op == OP_RPAREN || op == OP_RBRACKET) {
  depth = (depth - 1);
  if (depth < extern_depth) {
  extern_depth = (0 - 1);
}
  if (depth < 0) {
  depth = 0;
}
}
}
  prev_extern = 0;
  if (k == TK_IDENT) {
  if (depth == 0) {
  if (fb_is_word(c, t, "flow") == 1 && fb_is_ident(c, (t + 1)) == 1 && fb_is_op(c, (t + 2), OP_LBRACE) == 1) {
  if (nfl < FB_MAX_FLOWS) {
  flows[nfl] = t;
  nfl = (nfl + 1);
}
}
  if (fb_tok_is(c, t, "extern") == 1) {
  prev_extern = 1;
}
  const char* ty = fb_ttype(c, t);
  int32_t taken = 0;
  int32_t dim = 0;
  int32_t local = 0;
  int32_t nt = fb_decl_name(c, t);
  if (strcmp(ty, "FUNCTION") == 0) {
  taken = 1;
  local = 1;
}
  if (strcmp(ty, "STRUCT") == 0 || strcmp(ty, "ENUM") == 0 || strcmp(ty, "TRAIT") == 0) {
  taken = 1;
}
  if (strcmp(ty, "EFFECT") == 0 || strcmp(ty, "CAPABILITY") == 0 || strcmp(ty, "MODULE") == 0) {
  taken = 1;
}
  if (strcmp(ty, "THEOREM") == 0 || strcmp(ty, "CONST") == 0) {
  taken = 1;
}
  if (strcmp(ty, "LET") == 0) {
  taken = 1;
  if (nt >= 0 && fb_tok_is(c, nt, "mut") == 1) {
  nt = fb_decl_name(c, nt);
}
}
  if (strcmp(ty, "TYPE") == 0) {
  taken = 1;
  dim = 1;
}
  if (fb_is_word(c, t, "unit") == 1 && fb_is_ident(c, (t + 1)) == 1) {
  taken = 1;
  dim = 1;
}
  if (taken == 1 && nt >= 0) {
  int32_t nm = fb_tok_str(c, nt);
  fb_add_name(c, NX_TAKEN, nm);
  if (local == 1) {
  fb_add_name(c, NX_LOCAL_FN, nm);
}
  if (dim == 1) {
  fb_add_name(c, NX_DIMENSION, nm);
}
}
} else {
  if (depth == 1 && extern_depth == 1 && fb_tt_is(c, t, "FUNCTION") == 1) {
  int32_t en = fb_decl_name(c, t);
  if (en >= 0) {
  fb_add_name(c, NX_TAKEN, fb_tok_str(c, en));
}
}
}
}
  t = (t + 1);
}
  return nfl;
}

void fb_report(Fb* c) {
  FbBuf* b = (FbBuf*)(fb_buf_new(512));
  fb_puts(b, "flowc flow: ");
  if ((c[0]).err == 1) {
  fb_puts(b, "Error: ");
  fb_put_span(b, ((c[0]).emsg[0]).p, 0, ((c[0]).emsg[0]).len);
  if ((c[0]).err_line > 0) {
  fb_puts(b, " at line ");
  fb_put_int(b, (c[0]).err_line);
  if ((c[0]).err_col > 0) {
  fb_puts(b, ", column ");
  fb_put_int(b, (c[0]).err_col);
}
}
} else {
  fb_put_span(b, ((c[0]).emsg[0]).p, 0, ((c[0]).emsg[0]).len);
}
  puts((const char*)((b[0]).p));
  if ((c[0]).has_hint == 1) {
  (b[0]).len = 0;
  (b[0]).p[0] = 0;
  fb_puts(b, "flowc flow hint: ");
  fb_put_span(b, ((c[0]).ehint[0]).p, 0, ((c[0]).ehint[0]).len);
  puts((const char*)((b[0]).p));
}
  fb_buf_free(b);
}

int32_t fb_maybe_flow(uint8_t* p, int32_t n) {
  int32_t i = 0;
  while ((i + 4) <= n) {
  if (p[i] == 102 && p[(i + 1)] == 108 && p[(i + 2)] == 111 && p[(i + 3)] == 119) {
  return 1;
}
  i = (i + 1);
}
  return 0;
}

int32_t fb_expand(Fb* c) {
  if (fb_lex(c) < 0) {
  return 0;
}
  int32_t* flows = (int32_t*)(fb_alloc_i32(FB_MAX_FLOWS));
  int32_t nfl = fb_scan(c, flows);
  if (nfl == 0) {
  free((uint8_t*)(flows));
  return 0;
}
  int32_t f = 0;
  while (f < nfl) {
  (c[0]).f_solver[f] = 0;
  (c[0]).f_rec[f] = 0;
  (c[0]).f_rec_line[f] = 0;
  (c[0]).f_dt_ns[f] = 0;
  (c[0]).pos = flows[f];
  (c[0]).nf = (f + 1);
  if (fb_parse_flow(c, f) < 0) {
  free((uint8_t*)(flows));
  return (0 - 1);
}
  f = (f + 1);
}
  free((uint8_t*)(flows));
  f = 0;
  while (f < nfl) {
  int32_t g = 0;
  while (g < f) {
  if (fb_name_eq(c, (c[0]).f_name[g], (c[0]).f_name[f]) == 1) {
  FbBuf* m = (FbBuf*)(fb_verr(c, (c[0]).f_line[f]));
  fb_puts(m, "flow '");
  fb_put_fname(m, c, f);
  fb_puts(m, "' is declared twice");
  return (0 - 1);
}
  g = (g + 1);
}
  f = (f + 1);
}
  fb_reclassify(c);
  int32_t prev = 0;
  f = 0;
  while (f < nfl) {
  if (fb_expand_pipelines(c, f) < 0) {
  return (0 - 1);
}
  if (fb_validate_flow(c, f) < 0) {
  return (0 - 1);
}
  fb_put_span((c[0]).out, (c[0]).src, prev, (c[0]).f_start[f]);
  fb_lower_flow(c, f);
  prev = (c[0]).f_end[f];
  f = (f + 1);
}
  fb_put_span((c[0]).out, (c[0]).src, prev, (c[0]).n);
  return 1;
}

int32_t flowc_flow_blocks_expand_in_place(uint8_t* buf, int32_t n, int32_t cap) {
  if (n < 0) {
  return n;
}
  if (fb_maybe_flow(buf, n) == 0) {
  return n;
}
  Fb* c = (Fb*)(fb_ctx_new(buf, n));
  int32_t rc = fb_expand(c);
  if (rc < 0) {
  fb_report(c);
  fb_ctx_free(c);
  return (0 - 1);
}
  if (rc == 0) {
  fb_ctx_free(c);
  return n;
}
  FbBuf* out = (FbBuf*)((c[0]).out);
  int32_t m = (out[0]).len;
  if (m >= cap) {
  puts("flowc flow: expanded source exceeds the source buffer");
  fb_ctx_free(c);
  return (0 - 1);
}
  int32_t k = 0;
  while (k < m) {
  buf[k] = (out[0]).p[k];
  k = (k + 1);
}
  buf[m] = 0;
  fb_ctx_free(c);
  return m;
}


static const int32_t FLOWC_OVERLOAD_NO_MATCH = 0;
static const int32_t FLOWC_OVERLOAD_COMPATIBLE = 1;
static const int32_t FLOWC_OVERLOAD_LITERAL_WIDEN = 2;
static const int32_t FLOWC_OVERLOAD_EXACT = 3;
int32_t ov_streq(const char* a, uint8_t* b);
int32_t ov_starts_with(const char* value, uint8_t* prefix);
int32_t ov_is_digit(uint8_t ch);
int32_t ov_tail_equal(const char* a, int32_t a_start, const char* b, int32_t b_start);
int32_t ov_span_element_start(const char* type_name);
int32_t ov_array_element_start(const char* type_name);
int32_t flowc_overload_is_span_type(const char* type_name);
int32_t flowc_overload_is_primitive(const char* type_name);
int32_t flowc_overload_is_int_type(const char* type_name);
int32_t flowc_overload_types_compatible(const char* expected, const char* actual);
int32_t flowc_overload_literal_can_widen(const char* expected);
int32_t flowc_overload_argument_match(const char* expected, const char* actual, int32_t is_unsuffixed_int_literal, int32_t widening_phase);
int32_t flowc_overload_match_count_decision(int32_t match_count);
int32_t flowc_overload_sole_fallback(int32_t param_count, int32_t arg_count, int32_t all_known_compatible, int32_t has_unknown);
int32_t ov_streq(const char* a, uint8_t* b) {
  if (strcmp((uint8_t*)(a), b) == 0) {
  return 1;
}
  return 0;
}

int32_t ov_starts_with(const char* value, uint8_t* prefix) {
  uint8_t* vp = (uint8_t*)((uint8_t*)(value));
  int32_t value_len = (int32_t)(strlen(vp));
  int32_t prefix_len = (int32_t)(strlen(prefix));
  if (value_len < prefix_len) {
  return 0;
}
  int32_t i = 0;
  while (i < prefix_len) {
  if (vp[i] != prefix[i]) {
  return 0;
}
  i = (i + 1);
}
  return 1;
}

int32_t ov_is_digit(uint8_t ch) {
  if (ch < 48) {
  return 0;
}
  if (ch > 57) {
  return 0;
}
  return 1;
}

int32_t ov_tail_equal(const char* a, int32_t a_start, const char* b, int32_t b_start) {
  uint8_t* ap = (uint8_t*)((uint8_t*)(a));
  uint8_t* bp = (uint8_t*)((uint8_t*)(b));
  int32_t a_len = (int32_t)(strlen(ap));
  int32_t b_len = (int32_t)(strlen(bp));
  if (a_start < 0) {
  return 0;
}
  if (b_start < 0) {
  return 0;
}
  if ((a_len - a_start) != (b_len - b_start)) {
  return 0;
}
  int32_t i = 0;
  while ((a_start + i) < a_len) {
  if (ap[(a_start + i)] != bp[(b_start + i)]) {
  return 0;
}
  i = (i + 1);
}
  return 1;
}

int32_t ov_span_element_start(const char* type_name) {
  if (ov_starts_with(type_name, (uint8_t*)("span_const_")) == 1) {
  return 11;
}
  if (ov_starts_with(type_name, (uint8_t*)("span_")) == 1) {
  return 5;
}
  return (0 - 1);
}

int32_t ov_array_element_start(const char* type_name) {
  if (ov_starts_with(type_name, (uint8_t*)("array_")) == 0) {
  return (0 - 1);
}
  uint8_t* p = (uint8_t*)((uint8_t*)(type_name));
  int32_t n = (int32_t)(strlen(p));
  int32_t i = 6;
  int32_t saw_digit = 0;
  while (i < n && ov_is_digit(p[i]) == 1) {
  saw_digit = 1;
  i = (i + 1);
}
  if (saw_digit == 1) {
  if (i < n) {
  if (p[i] == 95) {
  return (i + 1);
}
}
}
  return 6;
}

int32_t flowc_overload_is_span_type(const char* type_name) {
  if (ov_span_element_start(type_name) >= 0) {
  return 1;
}
  return 0;
}

int32_t flowc_overload_is_primitive(const char* type_name) {
  if (ov_streq(type_name, (uint8_t*)("f32")) == 1) {
  return 1;
}
  if (ov_streq(type_name, (uint8_t*)("f64")) == 1) {
  return 1;
}
  if (ov_streq(type_name, (uint8_t*)("i32")) == 1) {
  return 1;
}
  if (ov_streq(type_name, (uint8_t*)("i64")) == 1) {
  return 1;
}
  if (ov_streq(type_name, (uint8_t*)("float")) == 1) {
  return 1;
}
  if (ov_streq(type_name, (uint8_t*)("double")) == 1) {
  return 1;
}
  if (ov_streq(type_name, (uint8_t*)("int")) == 1) {
  return 1;
}
  if (ov_streq(type_name, (uint8_t*)("bool")) == 1) {
  return 1;
}
  return 0;
}

int32_t flowc_overload_is_int_type(const char* type_name) {
  if (ov_streq(type_name, (uint8_t*)("i8")) == 1) {
  return 1;
}
  if (ov_streq(type_name, (uint8_t*)("i16")) == 1) {
  return 1;
}
  if (ov_streq(type_name, (uint8_t*)("i32")) == 1) {
  return 1;
}
  if (ov_streq(type_name, (uint8_t*)("i64")) == 1) {
  return 1;
}
  if (ov_streq(type_name, (uint8_t*)("i128")) == 1) {
  return 1;
}
  if (ov_streq(type_name, (uint8_t*)("u8")) == 1) {
  return 1;
}
  if (ov_streq(type_name, (uint8_t*)("u16")) == 1) {
  return 1;
}
  if (ov_streq(type_name, (uint8_t*)("u32")) == 1) {
  return 1;
}
  if (ov_streq(type_name, (uint8_t*)("u64")) == 1) {
  return 1;
}
  if (ov_streq(type_name, (uint8_t*)("u128")) == 1) {
  return 1;
}
  if (ov_streq(type_name, (uint8_t*)("int")) == 1) {
  return 1;
}
  if (ov_streq(type_name, (uint8_t*)("char")) == 1) {
  return 1;
}
  if (ov_streq(type_name, (uint8_t*)("short")) == 1) {
  return 1;
}
  if (ov_streq(type_name, (uint8_t*)("long")) == 1) {
  return 1;
}
  return 0;
}

int32_t flowc_overload_types_compatible(const char* expected, const char* actual) {
  if (ov_streq(expected, (uint8_t*)(actual)) == 1) {
  return 1;
}
  int32_t expected_span_start = ov_span_element_start(expected);
  if (expected_span_start >= 0) {
  int32_t actual_span_start = ov_span_element_start(actual);
  if (actual_span_start >= 0) {
  return ov_tail_equal(expected, expected_span_start, actual, actual_span_start);
}
  int32_t actual_array_start = ov_array_element_start(actual);
  if (actual_array_start >= 0) {
  return ov_tail_equal(expected, expected_span_start, actual, actual_array_start);
}
  return 0;
}
  int32_t actual_array_start = ov_array_element_start(actual);
  if (actual_array_start >= 0) {
  if (ov_starts_with(expected, (uint8_t*)("ptr_")) == 1) {
  if (ov_tail_equal(expected, 4, actual, actual_array_start) == 1) {
  return 1;
}
}
}
  if (ov_starts_with(expected, (uint8_t*)("ptr_")) == 1) {
  if (ov_tail_equal(expected, 4, actual, 0) == 1) {
  return 1;
}
}
  if (ov_streq(expected, (uint8_t*)("ptr_i8")) == 1) {
  if (ov_streq(actual, (uint8_t*)("string")) == 1) {
  return 1;
}
}
  if (ov_streq(actual, (uint8_t*)("ptr_void")) == 1) {
  if (ov_starts_with(expected, (uint8_t*)("ptr_")) == 1) {
  return 1;
}
  if (ov_streq(expected, (uint8_t*)("ptr_void")) == 1) {
  return 1;
}
}
  if (ov_starts_with(expected, (uint8_t*)("capability_")) == 1) {
  if (flowc_overload_is_primitive(actual) == 1) {
  return 0;
}
  if (ov_starts_with(actual, (uint8_t*)("ptr_")) == 1) {
  return 0;
}
  return 1;
}
  int32_t ef = 0;
  int32_t af = 0;
  if (ov_streq(expected, (uint8_t*)("f32")) == 1) {
  ef = 1;
}
  if (ov_streq(expected, (uint8_t*)("f64")) == 1) {
  ef = 1;
}
  if (ov_streq(actual, (uint8_t*)("f32")) == 1) {
  af = 1;
}
  if (ov_streq(actual, (uint8_t*)("f64")) == 1) {
  af = 1;
}
  if (ef == 1 && af == 1) {
  return 1;
}
  int32_t ei = 0;
  int32_t ai = 0;
  if (ov_streq(expected, (uint8_t*)("i32")) == 1) {
  ei = 1;
}
  if (ov_streq(expected, (uint8_t*)("i64")) == 1) {
  ei = 1;
}
  if (ov_streq(actual, (uint8_t*)("i32")) == 1) {
  ai = 1;
}
  if (ov_streq(actual, (uint8_t*)("i64")) == 1) {
  ai = 1;
}
  if (ei == 1 && ai == 1) {
  return 1;
}
  return 0;
}

int32_t flowc_overload_literal_can_widen(const char* expected) {
  return flowc_overload_is_int_type(expected);
}

int32_t flowc_overload_argument_match(const char* expected, const char* actual, int32_t is_unsuffixed_int_literal, int32_t widening_phase) {
  if (ov_streq(expected, (uint8_t*)(actual)) == 1) {
  return FLOWC_OVERLOAD_EXACT;
}
  if (flowc_overload_types_compatible(expected, actual) == 1) {
  return FLOWC_OVERLOAD_COMPATIBLE;
}
  if (widening_phase == 1 && is_unsuffixed_int_literal == 1) {
  if (flowc_overload_literal_can_widen(expected) == 1) {
  return FLOWC_OVERLOAD_LITERAL_WIDEN;
}
}
  return FLOWC_OVERLOAD_NO_MATCH;
}

int32_t flowc_overload_match_count_decision(int32_t match_count) {
  if (match_count <= 0) {
  return 0;
}
  if (match_count == 1) {
  return 1;
}
  return (0 - 1);
}

int32_t flowc_overload_sole_fallback(int32_t param_count, int32_t arg_count, int32_t all_known_compatible, int32_t has_unknown) {
  if (param_count != arg_count) {
  return 0;
}
  if (all_known_compatible == 1) {
  return 1;
}
  if (has_unknown == 1) {
  return 1;
}
  return 0;
}


static const int32_t FLOWC_TYPE_NAME_MAX_DEPTH = 32;
int32_t type_name_span_is(uint8_t* src, int32_t start, int32_t end, const char* lit);
int32_t type_name_append_byte(uint8_t* out, int32_t cap, int32_t off, int32_t value);
int32_t type_name_append_lit(uint8_t* out, int32_t cap, int32_t off, const char* lit);
int32_t type_name_append_span(uint8_t* src, int32_t start, int32_t end, uint8_t* out, int32_t cap, int32_t off);
int32_t type_name_append_i32(uint8_t* out, int32_t cap, int32_t off, int32_t value);
int32_t type_name_into_at(AstArena arena, uint8_t* src, int32_t ty, uint8_t* out, int32_t cap, int32_t off, int32_t depth);
int32_t flowc_type_name_into(AstArena arena, uint8_t* src, int32_t ty, uint8_t* out, int32_t cap);
int32_t type_name_span_is(uint8_t* src, int32_t start, int32_t end, const char* lit) {
  uint8_t* p = (uint8_t*)(lit);
  int32_t n = 0;
  while (p[n] != 0) {
  n = (n + 1);
}
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

int32_t type_name_append_byte(uint8_t* out, int32_t cap, int32_t off, int32_t value) {
  if (off < 0 || (off + 1) >= cap) {
  return (0 - 1);
}
  out[off] = value;
  out[(off + 1)] = 0;
  return (off + 1);
}

int32_t type_name_append_lit(uint8_t* out, int32_t cap, int32_t off, const char* lit) {
  uint8_t* p = (uint8_t*)(lit);
  int32_t n = 0;
  while (p[n] != 0) {
  n = (n + 1);
}
  if (off < 0 || (off + n) >= cap) {
  return (0 - 1);
}
  int32_t i = 0;
  while (i < n) {
  out[(off + i)] = p[i];
  i = (i + 1);
}
  out[(off + n)] = 0;
  return (off + n);
}

int32_t type_name_append_span(uint8_t* src, int32_t start, int32_t end, uint8_t* out, int32_t cap, int32_t off) {
  if (src == NULL || start < 0 || end <= start) {
  return (0 - 1);
}
  int32_t n = (end - start);
  if (off < 0 || (off + n) >= cap) {
  return (0 - 1);
}
  int32_t i = 0;
  while (i < n) {
  out[(off + i)] = src[(start + i)];
  i = (i + 1);
}
  out[(off + n)] = 0;
  return (off + n);
}

int32_t type_name_append_i32(uint8_t* out, int32_t cap, int32_t off, int32_t value) {
  if (value < 0) {
  return (0 - 1);
}
  if (value == 0) {
  return type_name_append_byte(out, cap, off, 48);
}
  uint8_t digits[16] = { 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
  int32_t n = 0;
  int32_t v = value;
  while (v > 0) {
  digits[n] = ((v % 10) + 48);
  n = (n + 1);
  v = (v / 10);
}
  if (off < 0 || (off + n) >= cap) {
  return (0 - 1);
}
  int32_t pos = off;
  int32_t i = n;
  while (i > 0) {
  i = (i - 1);
  out[pos] = digits[i];
  pos = (pos + 1);
}
  out[pos] = 0;
  return pos;
}

int32_t type_name_into_at(AstArena arena, uint8_t* src, int32_t ty, uint8_t* out, int32_t cap, int32_t off, int32_t depth) {
  __flowc_tail: ;
  if (depth >= FLOWC_TYPE_NAME_MAX_DEPTH) {
  return (0 - 1);
}
  if (ty == AST_NONE || ty < 0 || ty >= (arena).len) {
  return (0 - 1);
}
  if (((arena).nodes[ty]).kind != AST_TYPE) {
  return (0 - 1);
}
  if (((arena).nodes[ty]).ival < 0) {
  return (0 - 1);
}
  int32_t ns = ((arena).nodes[ty]).name_start;
  int32_t ne = ((arena).nodes[ty]).name_end;
  int32_t inner = ((arena).nodes[ty]).a;
  if (inner == AST_NONE) {
  return type_name_append_span(src, ns, ne, out, cap, off);
}
  if (type_name_span_is(src, ns, ne, "span") == 1 || src[ns] == 38) {
  int32_t is_mut = flowc_ast_type_span_mutable(arena, ty);
  int32_t p = (-1);
  if (is_mut == 1) {
  p = type_name_append_lit(out, cap, off, "span_mut_");
} else {
  p = type_name_append_lit(out, cap, off, "span_const_");
}
  if (p < 0) {
  return (0 - 1);
}
  {
  __auto_type __flowc_targ0 = arena;
  __auto_type __flowc_targ1 = src;
  __auto_type __flowc_targ2 = inner;
  __auto_type __flowc_targ3 = out;
  __auto_type __flowc_targ4 = cap;
  __auto_type __flowc_targ5 = p;
  __auto_type __flowc_targ6 = (depth + 1);
  arena = __flowc_targ0;
  src = __flowc_targ1;
  ty = __flowc_targ2;
  out = __flowc_targ3;
  cap = __flowc_targ4;
  off = __flowc_targ5;
  depth = __flowc_targ6;
  goto __flowc_tail;
  }
}
  if (type_name_span_is(src, ns, ne, "ptr") == 1) {
  int32_t p = type_name_append_lit(out, cap, off, "ptr_");
  if (p < 0) {
  return (0 - 1);
}
  {
  __auto_type __flowc_targ0 = arena;
  __auto_type __flowc_targ1 = src;
  __auto_type __flowc_targ2 = inner;
  __auto_type __flowc_targ3 = out;
  __auto_type __flowc_targ4 = cap;
  __auto_type __flowc_targ5 = p;
  __auto_type __flowc_targ6 = (depth + 1);
  arena = __flowc_targ0;
  src = __flowc_targ1;
  ty = __flowc_targ2;
  out = __flowc_targ3;
  cap = __flowc_targ4;
  off = __flowc_targ5;
  depth = __flowc_targ6;
  goto __flowc_tail;
  }
}
  if (type_name_span_is(src, ns, ne, "array") == 1) {
  int32_t p = type_name_append_lit(out, cap, off, "array_");
  if (p < 0) {
  return (0 - 1);
}
  if (((arena).nodes[ty]).ival > 0) {
  p = type_name_append_i32(out, cap, p, ((arena).nodes[ty]).ival);
  if (p < 0) {
  return (0 - 1);
}
  p = type_name_append_byte(out, cap, p, 95);
  if (p < 0) {
  return (0 - 1);
}
}
  {
  __auto_type __flowc_targ0 = arena;
  __auto_type __flowc_targ1 = src;
  __auto_type __flowc_targ2 = inner;
  __auto_type __flowc_targ3 = out;
  __auto_type __flowc_targ4 = cap;
  __auto_type __flowc_targ5 = p;
  __auto_type __flowc_targ6 = (depth + 1);
  arena = __flowc_targ0;
  src = __flowc_targ1;
  ty = __flowc_targ2;
  out = __flowc_targ3;
  cap = __flowc_targ4;
  off = __flowc_targ5;
  depth = __flowc_targ6;
  goto __flowc_tail;
  }
}
  int32_t p = type_name_append_span(src, ns, ne, out, cap, off);
  if (p < 0) {
  return (0 - 1);
}
  int32_t arg = inner;
  while (arg != AST_NONE) {
  p = type_name_append_byte(out, cap, p, 95);
  if (p < 0) {
  return (0 - 1);
}
  p = type_name_into_at(arena, src, arg, out, cap, p, (depth + 1));
  if (p < 0) {
  return (0 - 1);
}
  arg = ((arena).nodes[arg]).next;
}
  return p;
}

int32_t flowc_type_name_into(AstArena arena, uint8_t* src, int32_t ty, uint8_t* out, int32_t cap) {
  if (out == NULL || cap <= 0) {
  return (0 - 1);
}
  out[0] = 0;
  return type_name_into_at(arena, src, ty, out, cap, 0, 0);
}


int32_t expr_type_copy_string(const char* value, uint8_t* out, int32_t cap);
int32_t expr_type_copy_span(uint8_t* src, int32_t start, int32_t end, uint8_t* out, int32_t cap);
int32_t flowc_expr_type_into(AstArena arena, uint8_t* src, int32_t id, const char* known_ident_type, int32_t has_known_ident_type, uint8_t* out, int32_t cap);
int32_t flowc_expr_is_unsuffixed_int_literal(AstArena arena, int32_t id);
int32_t expr_type_copy_string(const char* value, uint8_t* out, int32_t cap) {
  int32_t n = (int32_t)(strlen(value));
  if (cap <= 0 || (n + 1) > cap) {
  return (0 - 1);
}
  uint8_t* p = (uint8_t*)(value);
  int32_t i = 0;
  while (i < n) {
  out[i] = p[i];
  i = (i + 1);
}
  out[n] = 0;
  return n;
}

int32_t expr_type_copy_span(uint8_t* src, int32_t start, int32_t end, uint8_t* out, int32_t cap) {
  if (src == NULL || start < 0 || end <= start) {
  return (0 - 1);
}
  int32_t n = (end - start);
  if (cap <= 0 || (n + 1) > cap) {
  return (0 - 1);
}
  int32_t i = 0;
  while (i < n) {
  out[i] = src[(start + i)];
  i = (i + 1);
}
  out[n] = 0;
  return n;
}

int32_t flowc_expr_type_into(AstArena arena, uint8_t* src, int32_t id, const char* known_ident_type, int32_t has_known_ident_type, uint8_t* out, int32_t cap) {
  if (id == AST_NONE || id < 0 || id >= (arena).len) {
  return (0 - 1);
}
  int32_t kind = ((arena).nodes[id]).kind;
  if (kind == AST_INT) {
  return expr_type_copy_string("i32", out, cap);
}
  if (kind == AST_FLOAT) {
  return expr_type_copy_string("f32", out, cap);
}
  if (kind == AST_BOOL) {
  return expr_type_copy_string("bool", out, cap);
}
  if (kind == AST_STRING) {
  return expr_type_copy_string("string", out, cap);
}
  if (kind == AST_IDENT) {
  if (has_known_ident_type == 0) {
  return (0 - 1);
}
  if (strlen(known_ident_type) == 0) {
  return (0 - 1);
}
  return expr_type_copy_string(known_ident_type, out, cap);
}
  if (kind == AST_STRUCT_LIT) {
  return expr_type_copy_span(src, ((arena).nodes[id]).name_start, ((arena).nodes[id]).name_end, out, cap);
}
  if (kind == AST_CAST) {
  int32_t ty = ((arena).nodes[id]).b;
  if (ty == AST_NONE || ty < 0 || ty >= (arena).len) {
  return (0 - 1);
}
  if (((arena).nodes[ty]).kind != AST_TYPE) {
  return (0 - 1);
}
  if (((arena).nodes[ty]).a != AST_NONE) {
  return (0 - 1);
}
  return expr_type_copy_span(src, ((arena).nodes[ty]).name_start, ((arena).nodes[ty]).name_end, out, cap);
}
  return (0 - 1);
}

int32_t flowc_expr_is_unsuffixed_int_literal(AstArena arena, int32_t id) {
  if (id == AST_NONE || id < 0 || id >= (arena).len) {
  return 0;
}
  if (((arena).nodes[id]).kind == AST_INT) {
  return 1;
}
  return 0;
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


void se_putc(ShBuf* w, uint8_t c);
void se_puts(ShBuf* w, const char* s);
const char* se_cstr(ShBuf* w);
void se_error(const char* head, const char* tail);
void se_ctx_error(ShCtx* c);
ShBuf* se_path(const char* dir, ShBuf* a, const char* b);
void se_mkdirs(const char* dir);
ShBuf* se_stem(const char* path);
int32_t se_write(ShBuf* path, ShBuf* data);
ShBuf* se_fill_name(ShCtx* c, int32_t k);
int32_t se_metal(ShCtx* c, const char* in_path, const char* out_dir, uint8_t* name, int32_t nlen);
int32_t se_wgsl(ShCtx* c, const char* in_path, const char* out_dir, uint8_t* name, int32_t nlen);
int32_t se_mode_is(const char* mode, const char* want);
int32_t flowc_shader_mode(const char* mode, const char* in_path, const char* out_path, const char* name);
void se_putc(ShBuf* w, uint8_t c) {
  flowc_shader_putc(w, c);
}

void se_puts(ShBuf* w, const char* s) {
  uint8_t* p = (uint8_t*)(s);
  int32_t n = (int32_t)(strlen(s));
  int32_t i = 0;
  while (i < n) {
  se_putc(w, p[i]);
  i = (i + 1);
}
}

const char* se_cstr(ShBuf* w) {
  (w[0]).buf[(w[0]).len] = 0;
  return (const char*)((w[0]).buf);
}

void se_error(const char* head, const char* tail) {
  ShBuf* w = (ShBuf*)(flowc_shader_buf_new(4096));
  se_puts(w, "flowc shader: ");
  se_puts(w, head);
  se_puts(w, tail);
  puts(se_cstr(w));
  flowc_shader_buf_free(w);
}

void se_ctx_error(ShCtx* c) {
  ShBuf* m = (ShBuf*)(flowc_shader_ctx_msg(c));
  ShBuf* w = (ShBuf*)(flowc_shader_buf_new(((m[0]).len + 64)));
  se_puts(w, "flowc shader: ");
  int32_t i = 0;
  while (i < (m[0]).len) {
  se_putc(w, (m[0]).buf[i]);
  i = (i + 1);
}
  puts(se_cstr(w));
  flowc_shader_buf_free(w);
}

ShBuf* se_path(const char* dir, ShBuf* a, const char* b) {
  ShBuf* w = (ShBuf*)(flowc_shader_buf_new(4096));
  se_puts(w, dir);
  if ((w[0]).len > 0 && (w[0]).buf[((w[0]).len - 1)] != 47) {
  se_putc(w, 47);
}
  int32_t i = 0;
  while (i < (a[0]).len) {
  se_putc(w, (a[0]).buf[i]);
  i = (i + 1);
}
  se_puts(w, b);
  return w;
}

void se_mkdirs(const char* dir) {
  ShBuf* w = (ShBuf*)(flowc_shader_buf_new(4096));
  se_puts(w, dir);
  int32_t n = (w[0]).len;
  int32_t i = 1;
  while (i < n) {
  if ((w[0]).buf[i] == 47) {
  (w[0]).buf[i] = 0;
  flowc_io_mkdir((const char*)((w[0]).buf));
  (w[0]).buf[i] = 47;
}
  i = (i + 1);
}
  flowc_io_mkdir(se_cstr(w));
  flowc_shader_buf_free(w);
}

ShBuf* se_stem(const char* path) {
  uint8_t* p = (uint8_t*)(path);
  int32_t n = (int32_t)(strlen(path));
  int32_t b = 0;
  int32_t i = 0;
  while (i < n) {
  if (p[i] == 47) {
  b = (i + 1);
}
  i = (i + 1);
}
  int32_t e = n;
  int32_t k = (n - 1);
  while (k > b) {
  if (p[k] == 46) {
  e = k;
  k = b;
}
  k = (k - 1);
}
  ShBuf* w = (ShBuf*)(flowc_shader_buf_new((n + 8)));
  i = b;
  while (i < e) {
  se_putc(w, p[i]);
  i = (i + 1);
}
  return w;
}

int32_t se_write(ShBuf* path, ShBuf* data) {
  if (flowc_write_file(se_cstr(path), (data[0]).buf, (data[0]).len) != 0) {
  se_error("cannot write ", se_cstr(path));
  return 1;
}
  return 0;
}

ShBuf* se_fill_name(ShCtx* c, int32_t k) {
  ShBuf* w = (ShBuf*)(flowc_shader_buf_new(64));
  flowc_shader_put_fill_name(c, w, k);
  return w;
}

int32_t se_metal(ShCtx* c, const char* in_path, const char* out_dir, uint8_t* name, int32_t nlen) {
  se_mkdirs(out_dir);
  ShBuf* stem = (ShBuf*)(se_stem(in_path));
  ShBuf* src = (ShBuf*)(flowc_shader_buf_new(65536));
  if (flowc_shader_gen(c, src, SH_METAL, name, nlen, (0 - 1)) != 0) {
  se_ctx_error(c);
  return 1;
}
  ShBuf* gallery = (ShBuf*)(se_path(out_dir, stem, "_gallery.metal"));
  int32_t rc = se_write(gallery, src);
  ShBuf* entries = (ShBuf*)(flowc_shader_buf_new(4096));
  int32_t nfl = flowc_shader_fill_count(c);
  int32_t k = 0;
  while (k < nfl) {
  if (nlen < 0 || flowc_shader_fill_named(c, k, name, nlen) == 1) {
  flowc_shader_put_fill_name(c, entries, k);
  se_puts(entries, "_frag\n");
}
  k = (k + 1);
}
  ShBuf* epath = (ShBuf*)(se_path(out_dir, stem, "_gallery.entries"));
  if (rc == 0) {
  rc = se_write(epath, entries);
}
  k = 0;
  while (k < nfl && rc == 0) {
  if (nlen < 0 || flowc_shader_fill_named(c, k, name, nlen) == 1) {
  ShBuf* one = (ShBuf*)(flowc_shader_buf_new(65536));
  flowc_shader_gen(c, one, SH_METAL, name, nlen, k);
  ShBuf* fname = (ShBuf*)(se_fill_name(c, k));
  ShBuf* mpath = (ShBuf*)(se_path(out_dir, fname, "_fill.metal"));
  rc = se_write(mpath, one);
  ShBuf* entry = (ShBuf*)(flowc_shader_buf_new(128));
  flowc_shader_put_fill_name(c, entry, k);
  se_puts(entry, "_frag\n");
  ShBuf* ypath = (ShBuf*)(se_path(out_dir, fname, "_fill.entry"));
  if (rc == 0) {
  rc = se_write(ypath, entry);
}
  flowc_shader_buf_free(one);
  flowc_shader_buf_free(fname);
  flowc_shader_buf_free(mpath);
  flowc_shader_buf_free(entry);
  flowc_shader_buf_free(ypath);
}
  k = (k + 1);
}
  if (rc == 0) {
  puts(se_cstr(gallery));
}
  flowc_shader_buf_free(stem);
  flowc_shader_buf_free(src);
  flowc_shader_buf_free(gallery);
  flowc_shader_buf_free(entries);
  flowc_shader_buf_free(epath);
  return rc;
}

int32_t se_wgsl(ShCtx* c, const char* in_path, const char* out_dir, uint8_t* name, int32_t nlen) {
  se_mkdirs(out_dir);
  ShBuf* stem = (ShBuf*)(se_stem(in_path));
  ShBuf* src = (ShBuf*)(flowc_shader_buf_new(65536));
  if (flowc_shader_gen(c, src, SH_WGSL, name, nlen, (0 - 1)) != 0) {
  se_ctx_error(c);
  return 1;
}
  ShBuf* out = (ShBuf*)(se_path(out_dir, stem, "_gallery.wgsl"));
  if (nlen >= 0) {
  flowc_shader_buf_free(out);
  ShBuf* nb = (ShBuf*)(flowc_shader_buf_new((nlen + 8)));
  int32_t i = 0;
  while (i < nlen) {
  se_putc(nb, name[i]);
  i = (i + 1);
}
  out = se_path(out_dir, nb, "_fill.wgsl");
  flowc_shader_buf_free(nb);
}
  int32_t rc = se_write(out, src);
  ShBuf* entries = (ShBuf*)(flowc_shader_buf_new(4096));
  int32_t nfl = flowc_shader_fill_count(c);
  int32_t first = 1;
  int32_t k = 0;
  while (k < nfl) {
  if (nlen < 0 || flowc_shader_fill_named(c, k, name, nlen) == 1) {
  if (first == 0) {
  se_putc(entries, 10);
}
  flowc_shader_put_fill_name(c, entries, k);
  se_puts(entries, "_frag");
  first = 0;
}
  k = (k + 1);
}
  ShBuf* epath = (ShBuf*)(se_path(out_dir, stem, "_gallery.wgsl.entries"));
  if (rc == 0) {
  rc = se_write(epath, entries);
}
  if (rc == 0) {
  puts(se_cstr(out));
}
  flowc_shader_buf_free(stem);
  flowc_shader_buf_free(src);
  flowc_shader_buf_free(out);
  flowc_shader_buf_free(entries);
  flowc_shader_buf_free(epath);
  return rc;
}

int32_t se_mode_is(const char* mode, const char* want) {
  if (strcmp(mode, want) == 0) {
  return 1;
}
  return 0;
}

int32_t flowc_shader_mode(const char* mode, const char* in_path, const char* out_path, const char* name) {
  int32_t known = (((se_mode_is(mode, "metal") + se_mode_is(mode, "wgsl")) + se_mode_is(mode, "list")) + se_mode_is(mode, "expand"));
  if (known == 0) {
  se_error("unknown FLOWC_SHADER mode ", mode);
  return 1;
}
  uint8_t* ip = (uint8_t*)(in_path);
  if (ip == NULL) {
  se_error("FLOWC_IN is required", "");
  return 1;
}
  uint8_t* op = (uint8_t*)(out_path);
  if (op == NULL && se_mode_is(mode, "list") == 0) {
  se_error("FLOWC_OUT is required", "");
  return 1;
}
  int64_t fsize = flowc_io_file_size(in_path);
  if (fsize < 0) {
  se_error("cannot read ", in_path);
  return 1;
}
  int32_t cap = ((int32_t)(fsize) + 256);
  uint8_t* buf = (uint8_t*)(malloc((int64_t)((cap + 1))));
  int32_t n = flowc_read_file(in_path, buf, cap);
  if (n < 0) {
  se_error("cannot read ", in_path);
  free(buf);
  return 1;
}
  buf[n] = 0;
  if (se_mode_is(mode, "expand") == 1) {
  int32_t xn = flowc_shader_expand_in_place(buf, n, cap);
  int32_t xrc = 1;
  if (xn >= 0) {
  xrc = 0;
  if (flowc_write_file(out_path, buf, xn) != 0) {
  se_error("cannot write ", out_path);
  xrc = 1;
}
}
  free(buf);
  return xrc;
}
  ShCtx* c = (ShCtx*)(flowc_shader_ctx_new(buf, n));
  free(buf);
  if (flowc_shader_extract(c) != 0) {
  se_ctx_error(c);
  flowc_shader_ctx_free(c);
  return 1;
}
  int32_t nfl = flowc_shader_fill_count(c);
  if (se_mode_is(mode, "list") == 1) {
  int32_t k = 0;
  while (k < nfl) {
  ShBuf* nm = (ShBuf*)(se_fill_name(c, k));
  puts(se_cstr(nm));
  flowc_shader_buf_free(nm);
  k = (k + 1);
}
  flowc_shader_ctx_free(c);
  return 0;
}
  if (nfl == 0) {
  if (se_mode_is(mode, "metal") == 1) {
  se_error("No `shader fill Name ", "{ ... }` blocks found.\nSee docs/language/shaders.md");
} else {
  se_error("No `shader fill Name ", "{ ... }` blocks found");
}
  flowc_shader_ctx_free(c);
  return 1;
}
  uint8_t* np = (uint8_t*)(name);
  int32_t nlen = (0 - 1);
  if (np != NULL) {
  if (strlen(name) > 0) {
  nlen = (int32_t)(strlen(name));
}
}
  if (nlen >= 0) {
  int32_t hit = 0;
  int32_t k2 = 0;
  while (k2 < nfl) {
  hit = (hit + flowc_shader_fill_named(c, k2, np, nlen));
  k2 = (k2 + 1);
}
  if (hit == 0) {
  ShBuf* w = (ShBuf*)(flowc_shader_buf_new((nlen + 32)));
  se_puts(w, "Shader '");
  se_puts(w, name);
  se_puts(w, "' not found");
  se_error(se_cstr(w), "");
  flowc_shader_buf_free(w);
  flowc_shader_ctx_free(c);
  return 1;
}
}
  int32_t rc = 0;
  if (se_mode_is(mode, "metal") == 1) {
  rc = se_metal(c, in_path, out_path, np, nlen);
} else {
  rc = se_wgsl(c, in_path, out_path, np, nlen);
}
  flowc_shader_ctx_free(c);
  return rc;
}


const int32_t FLOWC_OVERLOAD_SELECT_NO_MATCH = (-1);
const int32_t FLOWC_OVERLOAD_SELECT_AMBIGUOUS = (-2);
const int32_t FLOWC_OVERLOAD_SELECT_UNKNOWN = (-3);
static const int32_t FLOWC_OVERLOAD_SELECT_TYPE_CAP = 128;
int32_t flowc_overload_candidate_matches(AstArena arena, uint8_t* src, int32_t decl, uint8_t* actual_rows, int32_t* actual_known, int32_t* literal_flags, int32_t arg_count, int32_t row_cap, int32_t widening_phase);
int32_t overload_select_phase(FlowcOverloadTable table, AstArena arena, uint8_t* src, int32_t name_start, int32_t name_end, int32_t arg_count, uint8_t* actual_rows, int32_t* actual_known, int32_t* literal_flags, int32_t row_cap, int32_t widening_phase);
int32_t flowc_overload_select_decl(FlowcOverloadTable table, AstArena arena, uint8_t* src, int32_t name_start, int32_t name_end, int32_t arg_count, uint8_t* actual_rows, int32_t* actual_known, int32_t* literal_flags, int32_t row_cap);
int32_t flowc_overload_candidate_matches(AstArena arena, uint8_t* src, int32_t decl, uint8_t* actual_rows, int32_t* actual_known, int32_t* literal_flags, int32_t arg_count, int32_t row_cap, int32_t widening_phase) {
  if (decl == AST_NONE || decl < 0 || decl >= (arena).len) {
  return (0 - 1);
}
  if (((arena).nodes[decl]).kind != AST_FN) {
  return (0 - 1);
}
  if (arg_count < 0) {
  return (0 - 1);
}
  if (arg_count > 0) {
  if (actual_rows == NULL || actual_known == NULL || literal_flags == NULL) {
  return (0 - 1);
}
}
  if (row_cap <= 0 || row_cap > FLOWC_OVERLOAD_SELECT_TYPE_CAP) {
  return (0 - 1);
}
  int32_t param = ((arena).nodes[decl]).a;
  int32_t i = 0;
  while (param != AST_NONE && i < arg_count) {
  if (actual_known[i] == 0) {
  return (0 - 1);
}
  int32_t pty = ((arena).nodes[param]).a;
  uint8_t expected[128] = { 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
  if (flowc_type_name_into(arena, src, pty, (&expected[0]), FLOWC_OVERLOAD_SELECT_TYPE_CAP) < 0) {
  return (0 - 1);
}
  uint8_t* expected_ptr = (uint8_t*)((&expected[0]));
  uint8_t* actual = (uint8_t*)((actual_rows + (i * row_cap)));
  if (flowc_overload_argument_match((const char*)(expected_ptr), (const char*)(actual), literal_flags[i], widening_phase) == 0) {
  return 0;
}
  param = ((arena).nodes[param]).next;
  i = (i + 1);
}
  if (param != AST_NONE || i != arg_count) {
  return 0;
}
  return 1;
}

int32_t overload_select_phase(FlowcOverloadTable table, AstArena arena, uint8_t* src, int32_t name_start, int32_t name_end, int32_t arg_count, uint8_t* actual_rows, int32_t* actual_known, int32_t* literal_flags, int32_t row_cap, int32_t widening_phase) {
  int32_t candidates = flowc_overload_table_count(table, name_start, name_end, arg_count);
  int32_t matched = 0;
  int32_t selected = FLOWC_OVERLOAD_SELECT_NO_MATCH;
  int32_t saw_unknown = 0;
  int32_t nth = 0;
  while (nth < candidates) {
  int32_t decl = flowc_overload_table_nth_decl(table, name_start, name_end, arg_count, nth);
  int32_t m = flowc_overload_candidate_matches(arena, src, decl, actual_rows, actual_known, literal_flags, arg_count, row_cap, widening_phase);
  if (m == 1) {
  matched = (matched + 1);
  selected = decl;
} else {
  if (m < 0) {
  saw_unknown = 1;
}
}
  nth = (nth + 1);
}
  if (matched == 1) {
  return selected;
}
  if (matched > 1) {
  return FLOWC_OVERLOAD_SELECT_AMBIGUOUS;
}
  if (saw_unknown == 1) {
  return FLOWC_OVERLOAD_SELECT_UNKNOWN;
}
  return FLOWC_OVERLOAD_SELECT_NO_MATCH;
}

int32_t flowc_overload_select_decl(FlowcOverloadTable table, AstArena arena, uint8_t* src, int32_t name_start, int32_t name_end, int32_t arg_count, uint8_t* actual_rows, int32_t* actual_known, int32_t* literal_flags, int32_t row_cap) {
  int32_t candidates = flowc_overload_table_count(table, name_start, name_end, arg_count);
  if (candidates <= 0) {
  return FLOWC_OVERLOAD_SELECT_NO_MATCH;
}
  int32_t first = overload_select_phase(table, arena, src, name_start, name_end, arg_count, actual_rows, actual_known, literal_flags, row_cap, 0);
  if (first >= 0 || first == FLOWC_OVERLOAD_SELECT_AMBIGUOUS) {
  return first;
}
  int32_t second = overload_select_phase(table, arena, src, name_start, name_end, arg_count, actual_rows, actual_known, literal_flags, row_cap, 1);
  if (second >= 0 || second == FLOWC_OVERLOAD_SELECT_AMBIGUOUS) {
  return second;
}
  if (candidates == 1) {
  int32_t has_unknown = 0;
  int32_t i = 0;
  while (i < arg_count) {
  if (actual_known[i] == 0) {
  has_unknown = 1;
}
  i = (i + 1);
}
  if (flowc_overload_sole_fallback(arg_count, arg_count, 0, has_unknown) == 1) {
  return flowc_overload_table_nth_decl(table, name_start, name_end, arg_count, 0);
}
}
  if (first == FLOWC_OVERLOAD_SELECT_UNKNOWN || second == FLOWC_OVERLOAD_SELECT_UNKNOWN) {
  return FLOWC_OVERLOAD_SELECT_UNKNOWN;
}
  return FLOWC_OVERLOAD_SELECT_NO_MATCH;
}


static const int32_t FLOWC_OVERLOAD_ARG_TYPE_CAP = 128;
int32_t flowc_overload_classify_args(AstArena arena, uint8_t* src, int32_t first_arg, int32_t* ident_type_nodes, int32_t arg_count, uint8_t* rows, int32_t* known, int32_t* literal_flags, int32_t row_cap);
int32_t flowc_overload_classify_args(AstArena arena, uint8_t* src, int32_t first_arg, int32_t* ident_type_nodes, int32_t arg_count, uint8_t* rows, int32_t* known, int32_t* literal_flags, int32_t row_cap) {
  if (arg_count < 0 || row_cap <= 0 || row_cap > FLOWC_OVERLOAD_ARG_TYPE_CAP) {
  return (0 - 1);
}
  if (arg_count > 0) {
  if (ident_type_nodes == NULL || rows == NULL || known == NULL || literal_flags == NULL) {
  return (0 - 1);
}
}
  int32_t arg = first_arg;
  int32_t i = 0;
  while (arg != AST_NONE && i < arg_count) {
  uint8_t* row = (uint8_t*)((rows + (i * row_cap)));
  row[0] = 0;
  known[i] = 0;
  literal_flags[i] = flowc_expr_is_unsuffixed_int_literal(arena, arg);
  int32_t kind = ((arena).nodes[arg]).kind;
  if (kind == AST_CAST) {
  int32_t ty = ((arena).nodes[arg]).b;
  if (flowc_type_name_into(arena, src, ty, row, row_cap) >= 0) {
  known[i] = 1;
}
} else {
  int32_t has_ident_type = 0;
  uint8_t ident_name[128] = { 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
  if (kind == AST_IDENT) {
  int32_t ident_ty = ident_type_nodes[i];
  if (ident_ty != AST_NONE) {
  if (flowc_type_name_into(arena, src, ident_ty, (&ident_name[0]), FLOWC_OVERLOAD_ARG_TYPE_CAP) >= 0) {
  has_ident_type = 1;
}
}
}
  uint8_t* ident_ptr = (uint8_t*)((&ident_name[0]));
  if (flowc_expr_type_into(arena, src, arg, (const char*)(ident_ptr), has_ident_type, row, row_cap) >= 0) {
  known[i] = 1;
}
}
  arg = ((arena).nodes[arg]).next;
  i = (i + 1);
}
  if (arg != AST_NONE || i != arg_count) {
  return (0 - 1);
}
  return i;
}


typedef struct FlowcOverloadCallScratch {
  uint8_t* rows;
  int32_t* ident_types;
  int32_t* known;
  int32_t* literal_flags;
  int32_t cap;
  int32_t err;
} FlowcOverloadCallScratch;

const int32_t FLOWC_OVERLOAD_CALL_TYPE_CAP = 128;
FlowcOverloadCallScratch flowc_overload_call_scratch_init(int32_t cap);
void flowc_overload_call_scratch_free(FlowcOverloadCallScratch* scratch);
int32_t flowc_overload_call_prepare(FlowcOverloadCallScratch* scratch, int32_t arg_count);
int32_t flowc_overload_call_set_ident_type(FlowcOverloadCallScratch* scratch, int32_t arg_index, int32_t ty);
int32_t flowc_overload_resolve_call(FlowcOverloadCallScratch* scratch, FlowcOverloadTable table, AstArena arena, uint8_t* src, int32_t name_start, int32_t name_end, int32_t first_arg, int32_t arg_count);
FlowcOverloadCallScratch flowc_overload_call_scratch_init(int32_t cap) {
  if (cap <= 0) {
  return (FlowcOverloadCallScratch){ .rows = NULL, .ident_types = NULL, .known = NULL, .literal_flags = NULL, .cap = 0, .err = 1 };
}
  uint8_t* rows_raw = (uint8_t*)(malloc(((int64_t)(cap) * FLOWC_OVERLOAD_CALL_TYPE_CAP)));
  uint8_t* ident_raw = (uint8_t*)(malloc(((int64_t)(cap) * 4)));
  uint8_t* known_raw = (uint8_t*)(malloc(((int64_t)(cap) * 4)));
  uint8_t* literal_raw = (uint8_t*)(malloc(((int64_t)(cap) * 4)));
  if (rows_raw == NULL || ident_raw == NULL || known_raw == NULL || literal_raw == NULL) {
  if (rows_raw != NULL) {
  free(rows_raw);
}
  if (ident_raw != NULL) {
  free(ident_raw);
}
  if (known_raw != NULL) {
  free(known_raw);
}
  if (literal_raw != NULL) {
  free(literal_raw);
}
  return (FlowcOverloadCallScratch){ .rows = NULL, .ident_types = NULL, .known = NULL, .literal_flags = NULL, .cap = 0, .err = 1 };
}
  return (FlowcOverloadCallScratch){ .rows = rows_raw, .ident_types = (int32_t*)(ident_raw), .known = (int32_t*)(known_raw), .literal_flags = (int32_t*)(literal_raw), .cap = cap, .err = 0 };
}

void flowc_overload_call_scratch_free(FlowcOverloadCallScratch* scratch) {
  if ((scratch[0]).rows != NULL) {
  free((scratch[0]).rows);
  (scratch[0]).rows = NULL;
}
  if ((scratch[0]).ident_types != NULL) {
  free((scratch[0]).ident_types);
  (scratch[0]).ident_types = NULL;
}
  if ((scratch[0]).known != NULL) {
  free((scratch[0]).known);
  (scratch[0]).known = NULL;
}
  if ((scratch[0]).literal_flags != NULL) {
  free((scratch[0]).literal_flags);
  (scratch[0]).literal_flags = NULL;
}
  (scratch[0]).cap = 0;
  (scratch[0]).err = 0;
}

int32_t flowc_overload_call_prepare(FlowcOverloadCallScratch* scratch, int32_t arg_count) {
  if ((scratch[0]).err != 0 || arg_count < 0 || arg_count > (scratch[0]).cap) {
  return (0 - 1);
}
  int32_t i = 0;
  while (i < arg_count) {
  (scratch[0]).ident_types[i] = AST_NONE;
  i = (i + 1);
}
  return arg_count;
}

int32_t flowc_overload_call_set_ident_type(FlowcOverloadCallScratch* scratch, int32_t arg_index, int32_t ty) {
  if ((scratch[0]).err != 0 || arg_index < 0 || arg_index >= (scratch[0]).cap) {
  return (0 - 1);
}
  (scratch[0]).ident_types[arg_index] = ty;
  return 0;
}

int32_t flowc_overload_resolve_call(FlowcOverloadCallScratch* scratch, FlowcOverloadTable table, AstArena arena, uint8_t* src, int32_t name_start, int32_t name_end, int32_t first_arg, int32_t arg_count) {
  if ((scratch[0]).err != 0 || arg_count < 0 || arg_count > (scratch[0]).cap) {
  return FLOWC_OVERLOAD_SELECT_UNKNOWN;
}
  if (arg_count == 0) {
  return flowc_overload_select_decl(table, arena, src, name_start, name_end, 0, NULL, NULL, NULL, FLOWC_OVERLOAD_CALL_TYPE_CAP);
}
  int32_t classified = flowc_overload_classify_args(arena, src, first_arg, (scratch[0]).ident_types, arg_count, (scratch[0]).rows, (scratch[0]).known, (scratch[0]).literal_flags, FLOWC_OVERLOAD_CALL_TYPE_CAP);
  if (classified != arg_count) {
  return FLOWC_OVERLOAD_SELECT_UNKNOWN;
}
  return flowc_overload_select_decl(table, arena, src, name_start, name_end, arg_count, (scratch[0]).rows, (scratch[0]).known, (scratch[0]).literal_flags, FLOWC_OVERLOAD_CALL_TYPE_CAP);
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
  FlowcOverloadTable overloads;
  FlowcOverloadCallScratch overload_scratch;
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
int32_t flowc_tc_is_complex_builtin(uint8_t* src, int32_t start, int32_t end);
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
  if ((uint8_t*)(path) != NULL) {
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
  const char* s = (const char*)(buf);
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

int32_t flowc_tc_is_complex_builtin(uint8_t* src, int32_t start, int32_t end) {
  if (flowc_tc_span_is(src, start, end, "c64") == 1) {
  return 1;
}
  if (flowc_tc_span_is(src, start, end, "c128") == 1) {
  return 1;
}
  if (flowc_tc_span_is(src, start, end, "creal") == 1) {
  return 1;
}
  if (flowc_tc_span_is(src, start, end, "cimag") == 1) {
  return 1;
}
  if (flowc_tc_span_is(src, start, end, "cabs") == 1) {
  return 1;
}
  if (flowc_tc_span_is(src, start, end, "carg") == 1) {
  return 1;
}
  if (flowc_tc_span_is(src, start, end, "conj") == 1) {
  return 1;
}
  if (flowc_tc_span_is(src, start, end, "cexp") == 1) {
  return 1;
}
  if (flowc_tc_span_is(src, start, end, "clog") == 1) {
  return 1;
}
  if (flowc_tc_span_is(src, start, end, "csqrt") == 1) {
  return 1;
}
  if (flowc_tc_span_is(src, start, end, "cpow") == 1) {
  return 1;
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
  if (flowc_tc_span_is((ctx).src, start, end, "flow_panic") == 1) {
  return 1;
}
  if (flowc_tc_span_is((ctx).src, start, end, "sort") == 1) {
  return 1;
}
  if (flowc_tc_span_is((ctx).src, start, end, "sortBy") == 1) {
  return 1;
}
  if (flowc_tc_span_is((ctx).src, start, end, "sum") == 1) {
  return 1;
}
  if (flowc_tc_span_is((ctx).src, start, end, "sizeof") == 1) {
  return 1;
}
  if (flowc_tc_is_complex_builtin((ctx).src, start, end) == 1) {
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
  if (((arena).nodes[id]).ival == AST_IDENT_SORT_MOD) {
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
  int32_t nargs = flowc_ast_chain_len(arena, ((arena).nodes[id]).a);
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
  int32_t local_candidates = flowc_overload_table_count((ctx[0]).overloads, ns, ne, nargs);
  if (local_candidates > 0) {
  if (flowc_overload_call_prepare((&(ctx[0]).overload_scratch), nargs) >= 0) {
  int32_t typed_arg = ((arena).nodes[id]).a;
  int32_t arg_index = 0;
  while (typed_arg != AST_NONE) {
  if (((arena).nodes[typed_arg]).kind == AST_IDENT) {
  int32_t ident_ty = flowc_tc_lookup_val_type(ctx[0], ((arena).nodes[typed_arg]).name_start, ((arena).nodes[typed_arg]).name_end);
  if (ident_ty != AST_NONE) {
  flowc_overload_call_set_ident_type((&(ctx[0]).overload_scratch), arg_index, ident_ty);
}
}
  typed_arg = ((arena).nodes[typed_arg]).next;
  arg_index = (arg_index + 1);
}
  int32_t selected = flowc_overload_resolve_call((&(ctx[0]).overload_scratch), (ctx[0]).overloads, arena, (ctx[0]).src, ns, ne, ((arena).nodes[id]).a, nargs);
  if (selected == FLOWC_OVERLOAD_SELECT_AMBIGUOUS) {
  flowc_tc_note(ctx, "flowc tc: ambiguous overload call", ns, ne);
  flowc_tc_err(ctx);
} else {
  if (selected == FLOWC_OVERLOAD_SELECT_NO_MATCH) {
  flowc_tc_note(ctx, "flowc tc: no matching overload", ns, ne);
  flowc_tc_err(ctx);
}
}
}
} else {
  int32_t arity = flowc_tc_lookup_fn_arity(ctx[0], ns, ne);
  if (arity >= 0) {
  if (nargs != arity) {
  flowc_tc_note(ctx, "flowc tc: arity mismatch", ns, ne);
  flowc_tc_err(ctx);
}
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
  if (((arena).nodes[id]).b != AST_NONE) {
  flowc_tc_check_expr(ctx, arena, ((arena).nodes[id]).b);
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
  flowc_tc_seed_bind(ctx, dep_src, ((dep_arena).nodes[item]).name_start, ((dep_arena).nodes[item]).name_end, 0, (-1));
}
  if (kind == AST_FN) {
  int32_t fns = ((dep_arena).nodes[item]).name_start;
  int32_t fne = ((dep_arena).nodes[item]).name_end;
  if (fne > fns && flowc_tc_span_is(dep_src, fns, fne, "main") == 0) {
  int32_t farity = flowc_ast_chain_len(dep_arena, ((dep_arena).nodes[item]).a);
  flowc_tc_seed_bind(ctx, dep_src, fns, fne, 1, farity);
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
  int32_t ncap = 8192;
  int32_t mcap = 128;
  int32_t seed_cap = 131072;
  int32_t overload_arg_cap = 128;
  FlowcOverloadTable overloads = flowc_overload_table_init(src, ncap);
  FlowcOverloadCallScratch overload_scratch = flowc_overload_call_scratch_init(overload_arg_cap);
  uint8_t* raw_ns = (uint8_t*)(malloc(((int64_t)(ncap) * 4)));
  uint8_t* raw_ne = (uint8_t*)(malloc(((int64_t)(ncap) * 4)));
  uint8_t* raw_nk = (uint8_t*)(malloc(((int64_t)(ncap) * 4)));
  uint8_t* raw_na = (uint8_t*)(malloc(((int64_t)(ncap) * 4)));
  uint8_t* raw_mk = (uint8_t*)(malloc(((int64_t)(mcap) * 4)));
  uint8_t* raw_seed = (uint8_t*)(malloc((int64_t)(seed_cap)));
  if (raw_ns == NULL || raw_ne == NULL || raw_nk == NULL || raw_na == NULL || raw_mk == NULL || raw_seed == NULL || (overloads).err != 0 || (overload_scratch).err != 0) {
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
  flowc_overload_table_free((&overloads));
  flowc_overload_call_scratch_free((&overload_scratch));
  return (TcCtx){ .src = src, .ns = NULL, .ne = NULL, .nk = NULL, .na = NULL, .nlen = 0, .ncap = 0, .marks = NULL, .mlen = 0, .mcap = 0, .err = 1, .cur_ret = AST_NONE, .loop_depth = 0, .has_extern = 0, .lenient = 0, .seed_buf = NULL, .seed_cap = 0, .seed_len = 0, .seed_nlen = 0, .overloads = overloads, .overload_scratch = overload_scratch, .path = "" };
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
  return (TcCtx){ .src = src, .ns = ns, .ne = ne, .nk = nk, .na = na, .nlen = 0, .ncap = ncap, .marks = marks, .mlen = 0, .mcap = mcap, .err = 0, .cur_ret = AST_NONE, .loop_depth = 0, .has_extern = 0, .lenient = 0, .seed_buf = raw_seed, .seed_cap = seed_cap, .seed_len = 0, .seed_nlen = 0, .overloads = overloads, .overload_scratch = overload_scratch, .path = "" };
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
  flowc_overload_table_free((&(ctx[0]).overloads));
  flowc_overload_call_scratch_free((&(ctx[0]).overload_scratch));
}

void flowc_tc_reset_module(TcCtx* ctx, uint8_t* src) {
  (ctx[0]).src = src;
  (ctx[0]).nlen = (ctx[0]).seed_nlen;
  (ctx[0]).mlen = 0;
  (ctx[0]).err = 0;
  (ctx[0]).cur_ret = AST_NONE;
  (ctx[0]).loop_depth = 0;
  (ctx[0]).has_extern = 0;
  flowc_overload_registry_reset((&(ctx[0]).overloads), src);
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
  flowc_overload_registry_reset((&(ctx[0]).overloads), (ctx[0]).src);
  if (flowc_overload_registry_collect((&(ctx[0]).overloads), arena, root) < 0) {
  flowc_tc_err(ctx);
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
  if ((uint8_t*)(path) != NULL) {
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
static const int32_t FLOWC_RESOLVE_FNS_CAP = 262144;
int32_t flowc_resolve_copy_cstr(const char* s, uint8_t* dst, int32_t cap);
int32_t flowc_resolve_cstr_eq(uint8_t* a, uint8_t* b);
int32_t flowc_resolve_find_path(uint8_t* store, int32_t n, int32_t row_cap, uint8_t* path);
int32_t flowc_expand_stages_in_place(uint8_t* src, int32_t n, int32_t cap, int32_t stages);
int32_t flowc_expand_all_in_place(uint8_t* src, int32_t n, int32_t cap);
int32_t flowc_resolve_read_source(const char* path, uint8_t* src, int32_t cap);
int32_t flowc_resolve_sibling_path(uint8_t* import_span_src, int32_t name_start, int32_t name_end, const char* search_dir, uint8_t* out_path, int32_t out_path_cap);
int32_t flowc_resolve_dotted_path(uint8_t* import_span_src, int32_t name_start, int32_t name_end, const char* search_dir, uint8_t* out_path, int32_t out_path_cap);
int32_t flowc_resolve_dirname(const char* path, uint8_t* out, int32_t out_cap);
int32_t flowc_resolve_append_path(uint8_t* store, int32_t n, const char* path);
int32_t flowc_resolve_gather(const char* entry_path, const char* search_dir, uint8_t* path_store);
int32_t flowc_resolve_deps_ready(const char* path, const char* search_dir, uint8_t* all_store, int32_t all_n, uint8_t* out_store, int32_t out_n, uint8_t* src, uint8_t* imp_path);
int32_t flowc_resolve_topo(uint8_t* all_store, int32_t all_n, const char* search_dir, uint8_t* out_store);
int32_t flowc_resolve_emit_one(const char* path, uint8_t* out, int32_t out_cap, int32_t flags, uint8_t* sigs, int32_t sigcap, int32_t* siglen);
int32_t flowc_resolve_list_fns(const char* path, int32_t mi, uint8_t* buf, int32_t cap, int32_t len);
int32_t flowc_resolve_name_eq(uint8_t* buf, int32_t a, int32_t b);
int32_t flowc_resolve_next_entry(uint8_t* buf, int32_t e);
int32_t flowc_resolve_needs_rename(uint8_t* buf, int32_t len, int32_t e);
int32_t flowc_resolve_emit_renames(uint8_t* buf, int32_t len, int32_t mi, int32_t undef, uint8_t* out, int32_t cap);
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

int32_t flowc_expand_stages_in_place(uint8_t* src, int32_t n, int32_t cap, int32_t stages) {
  int32_t m = n;
  if (m >= 0 && (stages & 8) != 0) {
  m = flowc_shader_expand_in_place(src, m, cap);
}
  if (m >= 0 && (stages & 1) != 0) {
  m = flowc_field_expand_in_place(src, m, cap);
}
  if (m >= 0 && (stages & 2) != 0) {
  m = flowc_dynamics_expand_in_place(src, m, cap);
}
  if (m >= 0 && (stages & 4) != 0) {
  m = flowc_flow_blocks_expand_in_place(src, m, cap);
}
  return m;
}

int32_t flowc_expand_all_in_place(uint8_t* src, int32_t n, int32_t cap) {
  return flowc_expand_stages_in_place(src, n, cap, 15);
}

int32_t flowc_resolve_read_source(const char* path, uint8_t* src, int32_t cap) {
  int32_t n = flowc_read_file(path, src, cap);
  if (n <= 0) {
  return n;
}
  return flowc_expand_all_in_place(src, n, cap);
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
  int32_t nsrc = flowc_resolve_read_source(mpath, src, (FLOWC_RESOLVE_SRC_CAP - 1));
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
  flowc_parser_report(p, mpath);
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
  int32_t nsrc = flowc_resolve_read_source(path, src, (FLOWC_RESOLVE_SRC_CAP - 1));
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
  int32_t nsrc = flowc_resolve_read_source(path, src, (FLOWC_RESOLVE_SRC_CAP - 1));
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

int32_t flowc_resolve_list_fns(const char* path, int32_t mi, uint8_t* buf, int32_t cap, int32_t len) {
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
  int32_t n = len;
  int32_t item = (((p).arena).nodes[root]).a;
  while (item != (0 - 1)) {
  int32_t fn = (0 - 1);
  int32_t exported = 0;
  if ((((p).arena).nodes[item]).kind == AST_FN) {
  fn = item;
}
  if ((((p).arena).nodes[item]).kind == AST_EXPORT) {
  int32_t inner = (((p).arena).nodes[item]).a;
  if (inner != (0 - 1) && (((p).arena).nodes[inner]).kind == AST_FN) {
  fn = inner;
  exported = 1;
}
}
  if (fn != (0 - 1) && (((p).arena).nodes[fn]).c != (0 - 1) && (((p).arena).nodes[fn]).ival == 0) {
  int32_t ns = (((p).arena).nodes[fn]).name_start;
  int32_t ne = (((p).arena).nodes[fn]).name_end;
  if (ns >= 0 && ne > ns && ((n + (ne - ns)) + 3) < cap) {
  buf[n] = mi;
  buf[(n + 1)] = exported;
  n = (n + 2);
  int32_t k = ns;
  while (k < ne) {
  buf[n] = src[k];
  n = (n + 1);
  k = (k + 1);
}
  buf[n] = 0;
  n = (n + 1);
}
}
  item = (((p).arena).nodes[item]).next;
}
  flowc_parser_free(p);
  free(src);
  return n;
}

int32_t flowc_resolve_name_eq(uint8_t* buf, int32_t a, int32_t b) {
  int32_t i = 0;
  while (buf[(a + i)] != 0 && buf[(b + i)] != 0) {
  if (buf[(a + i)] != buf[(b + i)]) {
  return 0;
}
  i = (i + 1);
}
  if (buf[(a + i)] == buf[(b + i)]) {
  return 1;
}
  return 0;
}

int32_t flowc_resolve_next_entry(uint8_t* buf, int32_t e) {
  int32_t i = (e + 2);
  while (buf[i] != 0) {
  i = (i + 1);
}
  return (i + 1);
}

int32_t flowc_resolve_needs_rename(uint8_t* buf, int32_t len, int32_t e) {
  if (buf[(e + 1)] != 0) {
  return 0;
}
  int32_t mi = buf[e];
  int32_t o = 0;
  while (o < len) {
  int32_t om = buf[o];
  if (om != mi && flowc_resolve_name_eq(buf, (o + 2), (e + 2)) == 1) {
  if (buf[(o + 1)] != 0 || om < mi) {
  return 1;
}
}
  o = flowc_resolve_next_entry(buf, o);
}
  return 0;
}

int32_t flowc_resolve_emit_renames(uint8_t* buf, int32_t len, int32_t mi, int32_t undef, uint8_t* out, int32_t cap) {
  int32_t n = 0;
  int32_t e = 0;
  while (e < len) {
  int32_t em = buf[e];
  if (em == mi && flowc_resolve_needs_rename(buf, len, e) == 1) {
  int32_t nl = 0;
  while (buf[((e + 2) + nl)] != 0) {
  nl = (nl + 1);
}
  if (((n + (2 * nl)) + 48) >= cap) {
  return (0 - 1);
}
  const char* head = "#define ";
  if (undef == 1) {
  head = "#undef ";
}
  uint8_t* hp = (uint8_t*)(head);
  int32_t k = 0;
  while (hp[k] != 0) {
  out[n] = hp[k];
  n = (n + 1);
  k = (k + 1);
}
  k = 0;
  while (k < nl) {
  out[n] = buf[((e + 2) + k)];
  n = (n + 1);
  k = (k + 1);
}
  if (undef == 0) {
  const char* mid = " __flowc_m";
  uint8_t* mp = (uint8_t*)(mid);
  k = 0;
  while (mp[k] != 0) {
  out[n] = mp[k];
  n = (n + 1);
  k = (k + 1);
}
  if (mi >= 10) {
  out[n] = (48 + (mi / 10));
  n = (n + 1);
}
  out[n] = (48 + (mi % 10));
  n = (n + 1);
  out[n] = 95;
  n = (n + 1);
  k = 0;
  while (k < nl) {
  out[n] = buf[((e + 2) + k)];
  n = (n + 1);
  k = (k + 1);
}
}
  out[n] = 10;
  n = (n + 1);
}
  e = flowc_resolve_next_entry(buf, e);
}
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
  int32_t nsrc = flowc_resolve_read_source(mpath, src, (FLOWC_RESOLVE_SRC_CAP - 1));
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
  flowc_parser_report(p, mpath);
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
  uint8_t* fns = (uint8_t*)(malloc((int64_t)(FLOWC_RESOLVE_FNS_CAP)));
  if (fns == NULL) {
  free(sigs);
  free(order_store);
  free(path_store);
  return (0 - 1);
}
  int32_t fnlen = 0;
  int32_t li = 0;
  while (li < norder) {
  uint8_t* lslot = (uint8_t*)((order_store + (li * FLOWC_RESOLVE_PATH_CAP)));
  const char* lpath = lslot;
  int32_t nl = flowc_resolve_list_fns(lpath, li, fns, FLOWC_RESOLVE_FNS_CAP, fnlen);
  if (nl >= 0) {
  fnlen = nl;
}
  li = (li + 1);
}
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
  int32_t ndef = flowc_resolve_emit_renames(fns, fnlen, mi, 0, (out + written), (out_cap - written));
  if (ndef < 0) {
  free(fns);
  free(sigs);
  free(order_store);
  free(path_store);
  return (0 - 1);
}
  written = (written + ndef);
  uint8_t* dest = (uint8_t*)((out + written));
  int32_t rem = (out_cap - written);
  if (rem <= 0) {
  free(fns);
  free(sigs);
  free(order_store);
  free(path_store);
  return (0 - 1);
}
  int32_t n = flowc_resolve_emit_one(mpath, dest, rem, flags, sigs, FLOWC_RESOLVE_SIG_CAP, (&siglen));
  if (n <= 0) {
  free(fns);
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
  int32_t nundef = flowc_resolve_emit_renames(fns, fnlen, mi, 1, (out + written), (out_cap - written));
  if (nundef < 0) {
  free(fns);
  free(sigs);
  free(order_store);
  free(path_store);
  return (0 - 1);
}
  written = (written + nundef);
  mi = (mi + 1);
}
  free(fns);
  free(sigs);
  free(order_store);
  free(path_store);
  return written;
}


int32_t flowc_env_set(const char* name);
int32_t flowc_env_eq(const char* name, const char* want);
int32_t flowc_env_is_zero(const char* name);
int32_t flowc_want_typecheck();
int32_t flowc_expand_only_stages();
int32_t flowc_expand_only_mode(const char* in_path, const char* out_path);
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

int32_t flowc_expand_only_stages() {
  const char* v = getenv("FLOWC_EXPAND_ONLY");
  if (v == NULL) {
  return 7;
}
  uint8_t* vp = (uint8_t*)((uint8_t*)(v));
  int32_t mask = 0;
  int32_t i = 0;
  while (vp[i] != 0) {
  int32_t j = i;
  while (vp[j] != 0 && vp[j] != 44) {
  j = (j + 1);
}
  int32_t wl = (j - i);
  if (wl == 5 && vp[i] == 102 && vp[(i + 1)] == 105) {
  mask = (mask | 1);
}
  if (wl == 8 && vp[i] == 100) {
  mask = (mask | 2);
}
  if (wl == 4 && vp[i] == 102 && vp[(i + 1)] == 108) {
  mask = (mask | 4);
}
  i = j;
  if (vp[i] == 44) {
  i = (i + 1);
}
}
  if (mask == 0) {
  return 7;
}
  return mask;
}

int32_t flowc_expand_only_mode(const char* in_path, const char* out_path) {
  int64_t fsize = flowc_io_file_size(in_path);
  if (fsize < 0) {
  puts("flowc expand: read FLOWC_IN failed");
  return 1;
}
  int32_t src_cap = (((int32_t)(fsize) * 4) + 65536);
  uint8_t* src = (uint8_t*)(malloc((int64_t)(src_cap)));
  if (src == NULL) {
  puts("flowc expand: malloc src failed");
  return 1;
}
  int32_t nsrc = flowc_read_file(in_path, src, (src_cap - 1));
  if (nsrc < 0) {
  puts("flowc expand: read FLOWC_IN failed");
  free(src);
  return 1;
}
  src[nsrc] = 0;
  nsrc = flowc_expand_stages_in_place(src, nsrc, src_cap, flowc_expand_only_stages());
  if (nsrc < 0) {
  free(src);
  return 1;
}
  int32_t rc = 0;
  if (flowc_env_set("FLOWC_OUT") == 1) {
  if (flowc_write_file(out_path, src, nsrc) != 0) {
  puts("flowc expand: write FLOWC_OUT failed");
  rc = 1;
}
} else {
  src[nsrc] = 0;
  puts((const char*)(src));
}
  free(src);
  return rc;
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
  if (flowc_env_set("FLOWC_SHADER") == 1) {
  return flowc_shader_mode(getenv("FLOWC_SHADER"), in_path, out_path, getenv("FLOWC_SHADER_NAME"));
}
  if (flowc_env_eq("FLOWC_BACKEND", "bpf") == 1) {
  if (out_path == NULL) {
  puts("flowc emit: bpf requires FLOWC_OUT");
  return 1;
}
  return flowc_bpf_gen_compile(in_path, out_path, "2");
}
  if (flowc_env_set("FLOWC_EXPAND_ONLY") == 1) {
  return flowc_expand_only_mode(in_path, out_path);
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
  if (flowc_env_eq("FLOWC_BACKEND", "fmt") == 0) {
  nsrc = flowc_expand_all_in_place(src, nsrc, src_cap);
  if (nsrc < 0) {
  free(src);
  free(out);
  return 1;
}
}
  Parser p = flowc_parser_new(src, nsrc, 262144);
  int32_t root = flowc_parse_program((&p));
  if (root < 0 || (p).err != 0) {
  puts("flowc emit: parse failed");
  flowc_parser_report(p, in_path);
  printf("flowc emit: at %d\n", ((p).cur).start);
  printf("flowc emit: arena_len=%d\n", ((p).arena).len);
  flowc_parser_free(p);
  free(src);
  free(out);
  return 1;
}
  if (flowc_want_typecheck() == 1) {
  flowc_fuse_pipelines((&(p).arena), src);
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
  int32_t cap = 32768;
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
  int32_t cap = 32768;
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
  int32_t cap = 32768;
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
  int32_t cap = 32768;
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
  int32_t cap = 32768;
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
  int32_t cap = 32768;
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
  int32_t cap = 32768;
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
  int32_t cap = 32768;
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
  int32_t cap = 32768;
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
  int32_t cap = 32768;
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


