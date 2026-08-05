/* First-class GPU / unified memory ABI for FLOW.
 *
 * Metal backend on Apple (shared buffers = unified CPU/GPU).
 * Stub elsewhere: available() == 0, alloc returns NULL.
 */
#ifndef FLOW_GPU_MEMORY_H
#define FLOW_GPU_MEMORY_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Allocation flags */
enum {
    FLOW_GPU_MEM_DEFAULT = 0, /* platform default (shared on Metal) */
    FLOW_GPU_MEM_SHARED  = 1, /* CPU+GPU visible (unified / shared) */
    FLOW_GPU_MEM_PRIVATE = 2  /* GPU-private when supported; else shared */
};

/* 1 if a real GPU backend is usable, else 0 */
int flow_gpu_available(void);

/* Backend name: "metal", "stub", … (static string) */
const char *flow_gpu_backend_name(void);

/* Allocate `size` bytes on the GPU (or unified). Returns opaque handle or NULL. */
void *flow_gpu_alloc(int64_t size, int32_t flags);

void flow_gpu_free(void *buf);

/* Byte size of buffer; 0 if buf is NULL */
int64_t flow_gpu_size(void *buf);

/* Flags used at alloc time */
int32_t flow_gpu_flags(void *buf);

/* Host-mapped pointer for shared/unified buffers; NULL if private or unavailable */
void *flow_gpu_host_ptr(void *buf);

/* Copies. Return 0 on success, -1 on error. */
int flow_gpu_copy_h2d(void *dst_gpu, const void *src_host, int64_t nbytes);
int flow_gpu_copy_d2h(void *dst_host, void *src_gpu, int64_t nbytes);
int flow_gpu_copy_d2d(void *dst_gpu, void *src_gpu, int64_t nbytes);

/* Wait for outstanding GPU work issued by this runtime */
void flow_gpu_sync(void);

/* Elementwise f32 kernels over GpuBuffer handles (n floats).
 * Return 0 on success, -1 on error / unavailable.
 *
 *   mul:           out[i]    = a[i] * b[i]
 *   mul_backward_a: grad_a[i] = grad_out[i] * b[i]
 *   mul_backward_b: grad_b[i] = grad_out[i] * a[i]
 */
int flow_gpu_mul_f32(void *out_gpu, void *a_gpu, void *b_gpu, int64_t n);
int flow_gpu_mul_backward_a_f32(void *grad_a_gpu, void *grad_out_gpu, void *b_gpu, int64_t n);
int flow_gpu_mul_backward_b_f32(void *grad_b_gpu, void *grad_out_gpu, void *a_gpu, int64_t n);

#ifdef __cplusplus
}
#endif

#endif /* FLOW_GPU_MEMORY_H */
