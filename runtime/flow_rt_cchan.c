/* Fast pthread channel for Flow microbenchmarks.
 * Flow orchestrates timing/spawn; this keeps the hot path in tight C.
 */
#include <pthread.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    int32_t *buf;
    int32_t cap;
    int32_t size;
    int32_t head;
    int32_t tail;
    int closed;
    pthread_mutex_t mu;
    pthread_cond_t not_empty;
    pthread_cond_t not_full;
} flow_rt_cchan;

typedef struct {
    flow_rt_cchan *ch;
    int32_t n;
} flow_rt_ping_args;

typedef struct {
    int32_t start;
    int32_t end;
    int64_t partial;
} flow_rt_sum_job;

void *flow_rt_cchan_create(int32_t cap) {
    if (cap < 1) cap = 1;
    flow_rt_cchan *ch = (flow_rt_cchan *)calloc(1, sizeof(*ch));
    if (!ch) return NULL;
    ch->buf = (int32_t *)malloc((size_t)cap * sizeof(int32_t));
    if (!ch->buf) {
        free(ch);
        return NULL;
    }
    ch->cap = cap;
    pthread_mutex_init(&ch->mu, NULL);
    pthread_cond_init(&ch->not_empty, NULL);
    pthread_cond_init(&ch->not_full, NULL);
    return ch;
}

void flow_rt_cchan_destroy(void *p) {
    flow_rt_cchan *ch = (flow_rt_cchan *)p;
    if (!ch) return;
    pthread_mutex_destroy(&ch->mu);
    pthread_cond_destroy(&ch->not_empty);
    pthread_cond_destroy(&ch->not_full);
    free(ch->buf);
    free(ch);
}

void flow_rt_cchan_send(void *p, int32_t v) {
    flow_rt_cchan *ch = (flow_rt_cchan *)p;
    pthread_mutex_lock(&ch->mu);
    while (ch->size >= ch->cap && !ch->closed) {
        pthread_cond_wait(&ch->not_full, &ch->mu);
    }
    if (!ch->closed) {
        ch->buf[ch->tail] = v;
        ch->tail = (ch->tail + 1) % ch->cap;
        ch->size++;
        pthread_cond_signal(&ch->not_empty);
    }
    pthread_mutex_unlock(&ch->mu);
}

int32_t flow_rt_cchan_recv(void *p, int32_t *out) {
    flow_rt_cchan *ch = (flow_rt_cchan *)p;
    pthread_mutex_lock(&ch->mu);
    while (ch->size == 0 && !ch->closed) {
        pthread_cond_wait(&ch->not_empty, &ch->mu);
    }
    if (ch->size == 0) {
        pthread_mutex_unlock(&ch->mu);
        return 0;
    }
    *out = ch->buf[ch->head];
    ch->head = (ch->head + 1) % ch->cap;
    ch->size--;
    pthread_cond_signal(&ch->not_full);
    pthread_mutex_unlock(&ch->mu);
    return 1;
}

static void *flow_rt_ping_sender(void *p) {
    flow_rt_ping_args *a = (flow_rt_ping_args *)p;
    for (int32_t i = 0; i < a->n; i++) {
        flow_rt_cchan_send(a->ch, i);
    }
    return NULL;
}

static void *flow_rt_ping_receiver(void *p) {
    flow_rt_ping_args *a = (flow_rt_ping_args *)p;
    int32_t v = 0;
    for (int32_t i = 0; i < a->n; i++) {
        if (!flow_rt_cchan_recv(a->ch, &v)) break;
    }
    return NULL;
}

/* Returns elapsed ns, or -1 on error. Called from Flow. */
int64_t flow_rt_bench_chan_pingpong_body(int32_t n, int32_t buf, int64_t t0_ns) {
    (void)t0_ns; /* Flow passes timing externally if needed */
    flow_rt_cchan *ch = (flow_rt_cchan *)flow_rt_cchan_create(buf);
    if (!ch) return -1;
    flow_rt_ping_args args = {ch, n};
    pthread_t t_send, t_recv;
    if (pthread_create(&t_recv, NULL, flow_rt_ping_receiver, &args) != 0) {
        flow_rt_cchan_destroy(ch);
        return -1;
    }
    if (pthread_create(&t_send, NULL, flow_rt_ping_sender, &args) != 0) {
        pthread_join(t_recv, NULL);
        flow_rt_cchan_destroy(ch);
        return -1;
    }
    pthread_join(t_send, NULL);
    pthread_join(t_recv, NULL);
    flow_rt_cchan_destroy(ch);
    return 0; /* Flow computes elapsed around this call */
}

int64_t flow_rt_monotonic_ns(void); /* flow_rt_support.c */

int64_t flow_bench_chan_pingpong_ns(int32_t n, int32_t buf); /* may be Flow or below */

/* Keep a C fallback symbol used until Flow module takes over — Flow will export this. */

static void *flow_rt_sum_worker(void *p) {
    flow_rt_sum_job *j = (flow_rt_sum_job *)p;
    int64_t s = 0;
    for (int32_t i = j->start; i < j->end; i++) s += (int64_t)i;
    j->partial = s;
    return NULL;
}

#ifndef FLOW_PAR_WORKERS
#define FLOW_PAR_WORKERS 8
#endif

int64_t flow_rt_bench_parallel_sum_body(int32_t n) {
    if (n <= 0) return 0;
    int workers = FLOW_PAR_WORKERS;
    if (n < workers) workers = n;
    pthread_t threads[FLOW_PAR_WORKERS];
    flow_rt_sum_job jobs[FLOW_PAR_WORKERS];
    int spawned[FLOW_PAR_WORKERS];
    int32_t chunk = (n + workers - 1) / workers;
    for (int w = 0; w < workers; w++) {
        spawned[w] = 0;
        int32_t s = w * chunk;
        int32_t e = s + chunk;
        if (s >= n) {
            jobs[w].partial = 0;
            continue;
        }
        if (e > n) e = n;
        jobs[w].start = s;
        jobs[w].end = e;
        jobs[w].partial = 0;
        if (pthread_create(&threads[w], NULL, flow_rt_sum_worker, &jobs[w]) == 0) {
            spawned[w] = 1;
        } else {
            flow_rt_sum_worker(&jobs[w]);
        }
    }
    int64_t total = 0;
    for (int w = 0; w < workers; w++) {
        if (spawned[w]) pthread_join(threads[w], NULL);
        total += jobs[w].partial;
    }
    return total;
}
