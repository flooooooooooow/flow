/* Fixed-size reverse-mode AD tape for Flow's Tape effect.
 *
 * Ops: track leaves, record binary mul/add, backward from a root.
 * Not a full compiler AD pass — a live capability backend for demos.
 */
#ifndef FLOW_TAPE_H
#define FLOW_TAPE_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define FLOW_TAPE_MAX_NODES 256

void flow_tape_reset(void);
int32_t flow_tape_track(float value);
/* Record out = a * b (values already on tape as nodes a,b). Returns out idx. */
int32_t flow_tape_mul(int32_t a, int32_t b);
int32_t flow_tape_add(int32_t a, int32_t b);
void flow_tape_backward(int32_t root);
float flow_tape_get_grad(int32_t idx);
float flow_tape_get_val(int32_t idx);

#ifdef __cplusplus
}
#endif

#endif /* FLOW_TAPE_H */
