/* Opt-in race / deadlock hooks. Enable with FLOW_RACE=1.
 * Tracks per-thread lock stacks and reports lock-order inversions.
 * Not a full ThreadSanitizer — a cheap development aid.
 */
#include "flow_race.h"

#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifndef FLOW_RACE_DEPTH
#define FLOW_RACE_DEPTH 16
#endif

#ifndef FLOW_RACE_EDGES
#define FLOW_RACE_EDGES 512
#endif

static int g_enabled = -1; /* -1 unset, 0 off, 1 on */
static pthread_mutex_t g_edge_mu = PTHREAD_MUTEX_INITIALIZER;

typedef struct {
    void *locks[FLOW_RACE_DEPTH];
    int n;
} lock_stack;

static _Thread_local lock_stack g_stack;

typedef struct {
    void *before;
    void *after;
} lock_edge;

static lock_edge g_edges[FLOW_RACE_EDGES];
static int g_nedges = 0;

void flow_race_init(void) {
    if (g_enabled >= 0) return;
    const char *e = getenv("FLOW_RACE");
    g_enabled = (e && e[0] == '1') ? 1 : 0;
    if (g_enabled) {
        fprintf(stderr, "[flow-race] enabled (lock-order + touch hooks)\n");
    }
}

int flow_race_enabled(void) {
    if (g_enabled < 0) flow_race_init();
    return g_enabled;
}

static int edge_exists(void *a, void *b) {
    for (int i = 0; i < g_nedges; i++) {
        if (g_edges[i].before == a && g_edges[i].after == b) return 1;
    }
    return 0;
}

static void add_edge(void *before, void *after) {
    if (before == after) return;
    pthread_mutex_lock(&g_edge_mu);
    if (edge_exists(after, before)) {
        fprintf(stderr,
                "[flow-race] WARNING: lock-order inversion %p <-> %p "
                "(possible deadlock)\n",
                before, after);
    } else if (!edge_exists(before, after) && g_nedges < FLOW_RACE_EDGES) {
        g_edges[g_nedges].before = before;
        g_edges[g_nedges].after = after;
        g_nedges++;
    }
    pthread_mutex_unlock(&g_edge_mu);
}

void flow_race_mutex_lock(void *mu) {
    if (!flow_race_enabled() || !mu) return;
    for (int i = 0; i < g_stack.n; i++) {
        add_edge(g_stack.locks[i], mu);
    }
    if (g_stack.n < FLOW_RACE_DEPTH) {
        g_stack.locks[g_stack.n++] = mu;
    }
}

void flow_race_mutex_unlock(void *mu) {
    if (!flow_race_enabled() || !mu) return;
    for (int i = g_stack.n - 1; i >= 0; i--) {
        if (g_stack.locks[i] == mu) {
            memmove(&g_stack.locks[i], &g_stack.locks[i + 1],
                    (size_t)(g_stack.n - i - 1) * sizeof(void *));
            g_stack.n--;
            return;
        }
    }
}

void flow_race_read(void *addr, int32_t size) {
    (void)size;
    if (!flow_race_enabled() || !addr) return;
    /* Hook point for future shadow-state; currently a no-op touch. */
    (void)addr;
}

void flow_race_write(void *addr, int32_t size) {
    (void)size;
    if (!flow_race_enabled() || !addr) return;
    (void)addr;
}
