/* Opt-in race / deadlock hooks. Enable with FLOW_RACE=1.
 * - Lock-order inversion detection
 * - Shadow memory for channel/buffer touches (happens-before via locks)
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

#ifndef FLOW_RACE_SHADOW
#define FLOW_RACE_SHADOW 4096
#endif

static int g_enabled = -1;
static pthread_mutex_t g_edge_mu = PTHREAD_MUTEX_INITIALIZER;
static pthread_mutex_t g_shadow_mu = PTHREAD_MUTEX_INITIALIZER;

typedef struct {
    void *locks[FLOW_RACE_DEPTH];
    int n;
} lock_stack;

static _Thread_local lock_stack g_stack;
static _Thread_local unsigned long g_tid_key;

typedef struct {
    void *before;
    void *after;
} lock_edge;

static lock_edge g_edges[FLOW_RACE_EDGES];
static int g_nedges = 0;

typedef struct {
    void *addr;
    int32_t size;
    unsigned long last_writer;
    unsigned long last_reader;
    int held_locks; /* bitmask of whether writer held any lock */
} shadow_slot;

static shadow_slot g_shadow[FLOW_RACE_SHADOW];
static int g_nshadow = 0;

static unsigned long tid_key(void) {
    if (g_tid_key == 0) {
        g_tid_key = (unsigned long)pthread_self();
        if (g_tid_key == 0) g_tid_key = 1;
    }
    return g_tid_key;
}

void flow_rt_race_init(void) {
    if (g_enabled >= 0) return;
    const char *e = getenv("FLOW_RACE");
    g_enabled = (e && e[0] == '1') ? 1 : 0;
    if (g_enabled) {
        fprintf(stderr, "[flow-race] enabled (lock-order + shadow memory)\n");
    }
}

int flow_rt_race_enabled(void) {
    if (g_enabled < 0) flow_rt_race_init();
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
    if (!flow_rt_race_enabled() || !mu) return;
    for (int i = 0; i < g_stack.n; i++) {
        add_edge(g_stack.locks[i], mu);
    }
    if (g_stack.n < FLOW_RACE_DEPTH) {
        g_stack.locks[g_stack.n++] = mu;
    }
}

void flow_race_mutex_unlock(void *mu) {
    if (!flow_rt_race_enabled() || !mu) return;
    for (int i = g_stack.n - 1; i >= 0; i--) {
        if (g_stack.locks[i] == mu) {
            memmove(&g_stack.locks[i], &g_stack.locks[i + 1],
                    (size_t)(g_stack.n - i - 1) * sizeof(void *));
            g_stack.n--;
            return;
        }
    }
}

static shadow_slot *shadow_find(void *addr) {
    for (int i = 0; i < g_nshadow; i++) {
        if (g_shadow[i].addr == addr) return &g_shadow[i];
    }
    if (g_nshadow >= FLOW_RACE_SHADOW) return NULL;
    shadow_slot *s = &g_shadow[g_nshadow++];
    memset(s, 0, sizeof(*s));
    s->addr = addr;
    return s;
}

static void shadow_touch(void *addr, int32_t size, int is_write) {
    if (!addr) return;
    unsigned long me = tid_key();
    int locked = g_stack.n > 0;
    pthread_mutex_lock(&g_shadow_mu);
    shadow_slot *s = shadow_find(addr);
    if (!s) {
        pthread_mutex_unlock(&g_shadow_mu);
        return;
    }
    s->size = size;
    if (is_write) {
        if (s->last_writer && s->last_writer != me && !locked && !s->held_locks) {
            fprintf(stderr,
                    "[flow-race] WARNING: data race write %p size=%d "
                    "threads %lx / %lx (no common lock)\n",
                    addr, size, s->last_writer, me);
        }
        if (s->last_reader && s->last_reader != me && !locked && !s->held_locks) {
            fprintf(stderr,
                    "[flow-race] WARNING: data race write-after-read %p "
                    "threads %lx / %lx\n",
                    addr, s->last_reader, me);
        }
        s->last_writer = me;
        s->held_locks = locked;
    } else {
        if (s->last_writer && s->last_writer != me && !locked && !s->held_locks) {
            fprintf(stderr,
                    "[flow-race] WARNING: data race read %p size=%d "
                    "threads %lx / %lx (no common lock)\n",
                    addr, size, s->last_writer, me);
        }
        s->last_reader = me;
    }
    pthread_mutex_unlock(&g_shadow_mu);
}

void flow_race_read(void *addr, int32_t size) {
    if (!flow_rt_race_enabled()) return;
    shadow_touch(addr, size, 0);
}

void flow_race_write(void *addr, int32_t size) {
    if (!flow_rt_race_enabled()) return;
    shadow_touch(addr, size, 1);
}
