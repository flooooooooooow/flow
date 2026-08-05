/* Lightweight fiber context (callee-saved regs + sp). Replaces ucontext. */
#ifndef FLOW_FCTX_H
#define FLOW_FCTX_H

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct flow_fctx {
    void *sp;
} flow_fctx;

/* Save *old, restore *new (must not be NULL). */
void flow_fctx_swap(flow_fctx *old_ctx, flow_fctx *new_ctx);

/* Prepare ctx to run start_fn(start_arg) on first swap-in.
 * stack is the low address of a stack_size-byte region. */
void flow_fctx_init(flow_fctx *ctx, void *stack, size_t stack_size,
                    void (*start_fn)(void *), void *start_arg);

#if defined(__aarch64__) || defined(__x86_64__)
#define FLOW_FCTX_ASM 1
#else
#define FLOW_FCTX_ASM 0
#endif

#ifdef __cplusplus
}
#endif

#endif /* FLOW_FCTX_H */
