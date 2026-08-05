/* Thin parallel-for worker invoke for Flow orchestration.
 * Chunk math lives in lib/runtime/concurrency_parallel.flow
 */
#include "flow_concurrency.h"

#include <pthread.h>
#include <stdint.h>

#ifndef FLOW_PAR_WORKERS
#define FLOW_PAR_WORKERS 8
#endif

typedef struct {
    int32_t start;
    int32_t end;
    int32_t step;
    flow_par_body_fn body;
    void *ctx;
} flow_rt_par_job;

void flow_rt_par_run_job(void *job_ptr) {
    flow_rt_par_job *job = (flow_rt_par_job *)job_ptr;
    if (!job || !job->body || job->step == 0) return;
    if (job->step > 0) {
        for (int32_t i = job->start; i < job->end; i += job->step) {
            job->body(i, job->ctx);
        }
    } else {
        for (int32_t i = job->start; i > job->end; i += job->step) {
            job->body(i, job->ctx);
        }
    }
}

static void *flow_rt_par_trampoline(void *p) {
    flow_rt_par_run_job(p);
    return NULL;
}

int32_t flow_rt_par_workers(void) { return FLOW_PAR_WORKERS; }

int64_t flow_rt_par_job_sizeof(void) { return (int64_t)sizeof(flow_rt_par_job); }

/* Returns 0 on success; -1 → caller should run job sync. Writes pthread_t bits into out_thread. */
int32_t flow_rt_par_spawn(void *job_ptr, int64_t *out_thread) {
    if (!job_ptr || !out_thread) return -1;
    pthread_t th;
    if (pthread_create(&th, NULL, flow_rt_par_trampoline, job_ptr) != 0) {
        return -1;
    }
    *out_thread = (int64_t)(intptr_t)th;
    return 0;
}

int32_t flow_rt_par_join(int64_t thread) {
    pthread_t th = (pthread_t)(intptr_t)thread;
    return pthread_join(th, NULL) == 0 ? 0 : -1;
}

void flow_rt_par_job_set(void *job_ptr, int32_t start, int32_t end, int32_t step,
                         void *body, void *ctx) {
    flow_rt_par_job *job = (flow_rt_par_job *)job_ptr;
    if (!job) return;
    job->start = start;
    job->end = end;
    job->step = step;
    job->body = (flow_par_body_fn)body;
    job->ctx = ctx;
}

int32_t flow_rt_par_job_at_offset(void *base, int64_t job_sz, int32_t index, void **out_job) {
    if (!base || !out_job || index < 0) return -1;
    *out_job = (char *)base + job_sz * (int64_t)index;
    return 0;
}
