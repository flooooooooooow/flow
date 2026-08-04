/* C-side fiber context init (pairs with flow_fctx_*.S) */
#include "flow_fctx.h"

#include <stdint.h>
#include <string.h>

extern void flow_fctx_bootstrap(void);

#if defined(__aarch64__)

void flow_fctx_init(flow_fctx *ctx, void *stack, size_t stack_size,
                    void (*start_fn)(void *), void *start_arg) {
    uintptr_t top = (uintptr_t)stack + stack_size;
    top &= ~(uintptr_t)15; /* 16-byte align */
    /* Reserve 160-byte save area matching flow_fctx_swap */
    uint64_t *frame = (uint64_t *)(top - 160);
    memset(frame, 0, 160);
    frame[0] = (uint64_t)(uintptr_t)start_fn;              /* x19 */
    frame[1] = (uint64_t)(uintptr_t)start_arg;             /* x20 */
    frame[10] = 0;                                         /* x29 fp */
    frame[11] = (uint64_t)(uintptr_t)flow_fctx_bootstrap;  /* x30 lr */
    ctx->sp = frame;
}

#elif defined(__x86_64__)

void flow_fctx_init(flow_fctx *ctx, void *stack, size_t stack_size,
                    void (*start_fn)(void *), void *start_arg) {
    uintptr_t top = (uintptr_t)stack + stack_size;
    top &= ~(uintptr_t)15;
    /* swap pops: r15, r14, r13, r12, rbx, rbp, then ret
     * bootstrap expects arg in r12, fn in r13 */
    uint64_t *sp = (uint64_t *)top;
    *(--sp) = (uint64_t)(uintptr_t)flow_fctx_bootstrap; /* return address */
    *(--sp) = 0;                                         /* rbp */
    *(--sp) = 0;                                         /* rbx */
    *(--sp) = (uint64_t)(uintptr_t)start_arg;            /* r12 = arg */
    *(--sp) = (uint64_t)(uintptr_t)start_fn;             /* r13 = fn */
    *(--sp) = 0;                                         /* r14 */
    *(--sp) = 0;                                         /* r15 */
    ctx->sp = sp;
}

#else

void flow_fctx_init(flow_fctx *ctx, void *stack, size_t stack_size,
                    void (*start_fn)(void *), void *start_arg) {
    (void)stack;
    (void)stack_size;
    (void)start_fn;
    (void)start_arg;
    ctx->sp = NULL;
}

#endif
