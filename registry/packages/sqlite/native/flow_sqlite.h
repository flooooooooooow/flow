#ifndef FLOW_SQLITE_H
#define FLOW_SQLITE_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Opaque DB handle is returned as void*. NULL on failure. */
void *flow_sqlite_open(const char *path);
void flow_sqlite_close(void *db);

/* Run SQL with no result rows. Returns 0 on success, nonzero on error. */
int32_t flow_sqlite_exec(void *db, const char *sql);

/* Run SQL expected to produce a single integer in column 0 of first row.
 * Returns 0 on success and writes value to *out; nonzero on error/no row. */
int32_t flow_sqlite_query_i64(void *db, const char *sql, int64_t *out);

/* Last error message (static/borrowed; do not free). Empty string if none. */
const char *flow_sqlite_errmsg(void *db);

#ifdef __cplusplus
}
#endif

#endif /* FLOW_SQLITE_H */
