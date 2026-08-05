#include "flow_sqlite.h"

#include <sqlite3.h>
#include <stdlib.h>

void *flow_sqlite_open(const char *path) {
    if (!path) {
        return NULL;
    }
    sqlite3 *db = NULL;
    if (sqlite3_open(path, &db) != SQLITE_OK) {
        if (db) {
            sqlite3_close(db);
        }
        return NULL;
    }
    return (void *)db;
}

void flow_sqlite_close(void *db) {
    if (db) {
        sqlite3_close((sqlite3 *)db);
    }
}

int32_t flow_sqlite_exec(void *db, const char *sql) {
    if (!db || !sql) {
        return 1;
    }
    char *err = NULL;
    int rc = sqlite3_exec((sqlite3 *)db, sql, NULL, NULL, &err);
    if (err) {
        sqlite3_free(err);
    }
    return rc == SQLITE_OK ? 0 : (int32_t)rc;
}

int32_t flow_sqlite_query_i64(void *db, const char *sql, int64_t *out) {
    if (!db || !sql || !out) {
        return 1;
    }
    sqlite3_stmt *stmt = NULL;
    if (sqlite3_prepare_v2((sqlite3 *)db, sql, -1, &stmt, NULL) != SQLITE_OK) {
        return 2;
    }
    int rc = sqlite3_step(stmt);
    if (rc != SQLITE_ROW) {
        sqlite3_finalize(stmt);
        return 3;
    }
    *out = sqlite3_column_int64(stmt, 0);
    sqlite3_finalize(stmt);
    return 0;
}

const char *flow_sqlite_errmsg(void *db) {
    if (!db) {
        return "null db";
    }
    const char *msg = sqlite3_errmsg((sqlite3 *)db);
    return msg ? msg : "";
}
