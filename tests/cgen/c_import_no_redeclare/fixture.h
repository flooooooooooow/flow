/* Fixture for tests/cgen/c_import_no_redeclare.flow. Shaped like glibc's
   stdlib.h: an anonymous struct bound to a name by typedef, an opaque
   struct typedef, and extern functions. Names do not clash with libc. */
#ifndef FIXTURE_H
#define FIXTURE_H
typedef struct { long long quot; long long rem; } fixdiv_t;
typedef struct _fixopaque_s fixopaque_t;
extern long long fixrint (double __x);
extern fixdiv_t fixdiv (long long __n, long long __d);
#endif
