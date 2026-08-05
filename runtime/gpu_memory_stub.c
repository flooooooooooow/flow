/* Stub GPU memory backend — symbols resolve on non-Apple hosts. */
#include "gpu_memory.h"

#include <stddef.h>

int flow_gpu_available(void) { return 0; }

const char *flow_gpu_backend_name(void) { return "stub"; }

void *flow_gpu_alloc(int64_t size, int32_t flags) {
    (void)size;
    (void)flags;
    return NULL;
}

void flow_gpu_free(void *buf) { (void)buf; }

int64_t flow_gpu_size(void *buf) {
    (void)buf;
    return 0;
}

int32_t flow_gpu_flags(void *buf) {
    (void)buf;
    return 0;
}

void *flow_gpu_host_ptr(void *buf) {
    (void)buf;
    return NULL;
}

int flow_gpu_copy_h2d(void *dst_gpu, const void *src_host, int64_t nbytes) {
    (void)dst_gpu;
    (void)src_host;
    (void)nbytes;
    return -1;
}

int flow_gpu_copy_d2h(void *dst_host, void *src_gpu, int64_t nbytes) {
    (void)dst_host;
    (void)src_gpu;
    (void)nbytes;
    return -1;
}

int flow_gpu_copy_d2d(void *dst_gpu, void *src_gpu, int64_t nbytes) {
    (void)dst_gpu;
    (void)src_gpu;
    (void)nbytes;
    return -1;
}

void flow_gpu_sync(void) {}

int flow_gpu_mul_f32(void *out_gpu, void *a_gpu, void *b_gpu, int64_t n) {
    (void)out_gpu;
    (void)a_gpu;
    (void)b_gpu;
    (void)n;
    return -1;
}

int flow_gpu_mul_backward_a_f32(void *grad_a_gpu, void *grad_out_gpu, void *b_gpu, int64_t n) {
    (void)grad_a_gpu;
    (void)grad_out_gpu;
    (void)b_gpu;
    (void)n;
    return -1;
}

int flow_gpu_mul_backward_b_f32(void *grad_b_gpu, void *grad_out_gpu, void *a_gpu, int64_t n) {
    (void)grad_b_gpu;
    (void)grad_out_gpu;
    (void)a_gpu;
    (void)n;
    return -1;
}
