/* Delimited continuation API with fiber-backed Flow-frame resume.
 *
 * On a fiber: flow_cont_shift_i32 parks (Flow locals preserved);
 * flow_cont_resume_pending unparks and makes shift return `value`.
 *
 * See docs/language/async-effects.md
 */
#ifndef FLOW_CONT_H
#define FLOW_CONT_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct flow_cont flow_cont;

typedef void *(*flow_reset_body)(void *arg, flow_cont *k);

void *flow_reset(flow_reset_body body, void *arg);
void *flow_reset_ex(flow_reset_body body, void *arg, flow_cont **out_k);
void *flow_shift(flow_cont **out_k, void *value);
void *flow_cont_resume(flow_cont *k, void *value);
void flow_cont_free(flow_cont *k);

/* Fiber-backed one-shot shift/resume (Flow-callable). */
int32_t flow_cont_shift_i32(void);
int32_t flow_cont_resume_pending(int32_t value);
int32_t flow_cont_has_pending(void);
/* Spawn a peer fiber that waits for a pending shift and resumes with value. */
void flow_cont_arm_resume(int32_t value); /* → lib/runtime/cont.flow */

/* Used by lib/runtime/cont.flow → flow_demo_cont_shift(). */
int32_t flow_rt_cont_demo(void);
/* reset → shift(7) → resume(100); returns 100 on success. */
int32_t flow_rt_cont_reset_demo(void);

#ifdef __cplusplus
}
#endif

#endif /* FLOW_CONT_H */
