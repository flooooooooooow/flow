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
#include <stdarg.h>
static void __flowc_pr_i(const char* e, ...) { va_list ap; va_start(ap, e); int v = va_arg(ap, int); va_end(ap); printf("%d%s", v, e); }
static void __flowc_pr_l(const char* e, long long v) { printf("%lld%s", v, e); }
static void __flowc_pr_u(const char* e, unsigned long long v) { printf("%llu%s", v, e); }
static void __flowc_pr_f(const char* e, double v) { printf("%f%s", v, e); }
static void __flowc_pr_s(const char* e, const char* v) { printf("%s%s", v, e); }
static void __flowc_pr_c64(const char* e, float complex v) { printf("(%f + %f j)%s", crealf(v), cimagf(v), e); }
static void __flowc_pr_c128(const char* e, double complex v) { printf("(%f + %f j)%s", creal(v), cimag(v), e); }
#define __flowc_print_any(x, e) _Generic((x), float complex: __flowc_pr_c64, double complex: __flowc_pr_c128, float: __flowc_pr_f, double: __flowc_pr_f, char*: __flowc_pr_s, const char*: __flowc_pr_s, unsigned int: __flowc_pr_u, unsigned long: __flowc_pr_u, unsigned long long: __flowc_pr_u, long: __flowc_pr_l, long long: __flowc_pr_l, default: __flowc_pr_i)((e), (x))

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

#undef TOK_EOF
const int32_t TOK_EOF = 0;
#undef TOK_IDENT
const int32_t TOK_IDENT = 1;
#undef TOK_KEYWORD
const int32_t TOK_KEYWORD = 2;
#undef TOK_INT
const int32_t TOK_INT = 3;
#undef TOK_FLOAT
const int32_t TOK_FLOAT = 4;
#undef TOK_STRING
const int32_t TOK_STRING = 5;
#undef TOK_LPAREN
const int32_t TOK_LPAREN = 6;
#undef TOK_RPAREN
const int32_t TOK_RPAREN = 7;
#undef TOK_LBRACE
const int32_t TOK_LBRACE = 8;
#undef TOK_RBRACE
const int32_t TOK_RBRACE = 9;
#undef TOK_LBRACK
const int32_t TOK_LBRACK = 10;
#undef TOK_RBRACK
const int32_t TOK_RBRACK = 11;
#undef TOK_COLON
const int32_t TOK_COLON = 12;
#undef TOK_COMMA
const int32_t TOK_COMMA = 13;
#undef TOK_SEMI
const int32_t TOK_SEMI = 14;
#undef TOK_DOT
const int32_t TOK_DOT = 15;
#undef TOK_ARROW
const int32_t TOK_ARROW = 16;
#undef TOK_EQ
const int32_t TOK_EQ = 17;
#undef TOK_EQEQ
const int32_t TOK_EQEQ = 18;
#undef TOK_NE
const int32_t TOK_NE = 19;
#undef TOK_LT
const int32_t TOK_LT = 20;
#undef TOK_LE
const int32_t TOK_LE = 21;
#undef TOK_GT
const int32_t TOK_GT = 22;
#undef TOK_GE
const int32_t TOK_GE = 23;
#undef TOK_PLUS
const int32_t TOK_PLUS = 24;
#undef TOK_MINUS
const int32_t TOK_MINUS = 25;
#undef TOK_STAR
const int32_t TOK_STAR = 26;
#undef TOK_SLASH
const int32_t TOK_SLASH = 27;
#undef TOK_AMPAMP
const int32_t TOK_AMPAMP = 28;
#undef TOK_BARBAR
const int32_t TOK_BARBAR = 29;
#undef TOK_BANG
const int32_t TOK_BANG = 30;
#undef TOK_ERROR
const int32_t TOK_ERROR = 31;
#undef TOK_AMP
const int32_t TOK_AMP = 32;
#undef TOK_PERCENT
const int32_t TOK_PERCENT = 33;
#undef TOK_DOTDOT
const int32_t TOK_DOTDOT = 34;
#undef TOK_FATARROW
const int32_t TOK_FATARROW = 35;
#undef TOK_TILDE
const int32_t TOK_TILDE = 36;
#undef TOK_AT
const int32_t TOK_AT = 37;
#undef TOK_BAR
const int32_t TOK_BAR = 38;
#undef TOK_CARET
const int32_t TOK_CARET = 39;
#undef TOK_SHL
const int32_t TOK_SHL = 40;
#undef TOK_SHR
const int32_t TOK_SHR = 41;
#undef TOK_PLUS_EQ
const int32_t TOK_PLUS_EQ = 42;
#undef TOK_MINUS_EQ
const int32_t TOK_MINUS_EQ = 43;
#undef TOK_STAR_EQ
const int32_t TOK_STAR_EQ = 44;
#undef TOK_SLASH_EQ
const int32_t TOK_SLASH_EQ = 45;
#undef TOK_PERCENT_EQ
const int32_t TOK_PERCENT_EQ = 46;
#undef TOK_IN
const int32_t TOK_IN = 47;
#undef TOK_PIPELINE
const int32_t TOK_PIPELINE = 48;
#undef TOK_CLAIM
const int32_t TOK_CLAIM = 49;
#undef TOK_QUESTION
const int32_t TOK_QUESTION = 50;
#undef KW_LET
const int32_t KW_LET = 1;
#undef KW_FUNCTION
const int32_t KW_FUNCTION = 2;
#undef KW_RETURN
const int32_t KW_RETURN = 3;
#undef KW_IF
const int32_t KW_IF = 4;
#undef KW_ELSE
const int32_t KW_ELSE = 5;
#undef KW_WHILE
const int32_t KW_WHILE = 6;
#undef KW_FOR
const int32_t KW_FOR = 7;
#undef KW_IN
const int32_t KW_IN = 8;
#undef KW_TO
const int32_t KW_TO = 9;
#undef KW_STRUCT
const int32_t KW_STRUCT = 10;
#undef KW_MUT
const int32_t KW_MUT = 11;
#undef KW_EXTERN
const int32_t KW_EXTERN = 12;
#undef KW_TRUE
const int32_t KW_TRUE = 13;
#undef KW_FALSE
const int32_t KW_FALSE = 14;
#undef KW_NULL
const int32_t KW_NULL = 15;
#undef KW_IMPORT
const int32_t KW_IMPORT = 16;
#undef KW_EXPORT
const int32_t KW_EXPORT = 17;
#undef KW_BREAK
const int32_t KW_BREAK = 18;
#undef KW_CONTINUE
const int32_t KW_CONTINUE = 19;
#undef KW_CONST
const int32_t KW_CONST = 20;
#undef KW_AS
const int32_t KW_AS = 21;
#undef KW_AND
const int32_t KW_AND = 22;
#undef KW_OR
const int32_t KW_OR = 23;
#undef KW_MATCH
const int32_t KW_MATCH = 24;
#undef KW_ELIF
const int32_t KW_ELIF = 25;
#undef KW_TYPE
const int32_t KW_TYPE = 26;
#undef KW_UNIT
const int32_t KW_UNIT = 27;
#undef KW_EFFECT
const int32_t KW_EFFECT = 28;
#undef KW_CAPABILITY
const int32_t KW_CAPABILITY = 29;
#undef KW_NOT
const int32_t KW_NOT = 30;
#undef KW_DEFER
const int32_t KW_DEFER = 31;
#undef KW_ENUM
const int32_t KW_ENUM = 32;
#undef KW_TRAIT
const int32_t KW_TRAIT = 33;
#undef KW_IMPL
const int32_t KW_IMPL = 34;
#undef KW_TEST
const int32_t KW_TEST = 35;
#undef KW_PARALLEL
const int32_t KW_PARALLEL = 36;
#undef KW_DBG
const int32_t KW_DBG = 37;
#undef KW_EXPECT
const int32_t KW_EXPECT = 38;
#undef KW_DEFAULT
const int32_t KW_DEFAULT = 39;
#undef KW_SHADER
const int32_t KW_SHADER = 40;
#undef KW_HANDLE
const int32_t KW_HANDLE = 41;
#undef KW_WITH
const int32_t KW_WITH = 42;
Token flowc_make_tok(int32_t kind, int32_t kw, int32_t start, int32_t end, int32_t line, int32_t col);
Token flowc_make_tok(int32_t kind, int32_t kw, int32_t start, int32_t end, int32_t line, int32_t col) {
  return (Token){ .kind = kind, .kw = kw, .start = start, .end = end, .line = line, .col = col };
}

