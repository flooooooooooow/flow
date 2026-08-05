/* Storage for Flow AD tape (lib/runtime/tape.flow). */
#include <stdint.h>
#include <string.h>

#ifndef FLOW_TAPE_MAX_NODES
#define FLOW_TAPE_MAX_NODES 256
#endif

static int32_t g_op[FLOW_TAPE_MAX_NODES];
static int32_t g_a[FLOW_TAPE_MAX_NODES];
static int32_t g_b[FLOW_TAPE_MAX_NODES];
static float g_val[FLOW_TAPE_MAX_NODES];
static float g_grad[FLOW_TAPE_MAX_NODES];
static int32_t g_len = 0;

int32_t flow_rt_tape_max(void) { return FLOW_TAPE_MAX_NODES; }
int32_t flow_rt_tape_len(void) { return g_len; }
void flow_rt_tape_set_len(int32_t n) { g_len = n; }

void flow_rt_tape_clear(void) {
    g_len = 0;
    memset(g_op, 0, sizeof(g_op));
    memset(g_a, 0, sizeof(g_a));
    memset(g_b, 0, sizeof(g_b));
    memset(g_val, 0, sizeof(g_val));
    memset(g_grad, 0, sizeof(g_grad));
}

void flow_rt_tape_set_node(int32_t i, int32_t op, int32_t a, int32_t b, float val) {
    if (i < 0 || i >= FLOW_TAPE_MAX_NODES) return;
    g_op[i] = op;
    g_a[i] = a;
    g_b[i] = b;
    g_val[i] = val;
    g_grad[i] = 0.0f;
}

int32_t flow_rt_tape_get_op(int32_t i) {
    if (i < 0 || i >= FLOW_TAPE_MAX_NODES) return 0;
    return g_op[i];
}
int32_t flow_rt_tape_get_a(int32_t i) {
    if (i < 0 || i >= FLOW_TAPE_MAX_NODES) return -1;
    return g_a[i];
}
int32_t flow_rt_tape_get_b(int32_t i) {
    if (i < 0 || i >= FLOW_TAPE_MAX_NODES) return -1;
    return g_b[i];
}
float flow_rt_tape_get_val(int32_t i) {
    if (i < 0 || i >= FLOW_TAPE_MAX_NODES) return 0.0f;
    return g_val[i];
}
float flow_rt_tape_get_grad(int32_t i) {
    if (i < 0 || i >= FLOW_TAPE_MAX_NODES) return 0.0f;
    return g_grad[i];
}
void flow_rt_tape_set_grad(int32_t i, float g) {
    if (i < 0 || i >= FLOW_TAPE_MAX_NODES) return;
    g_grad[i] = g;
}
void flow_rt_tape_add_grad(int32_t i, float d) {
    if (i < 0 || i >= FLOW_TAPE_MAX_NODES) return;
    g_grad[i] += d;
}
void flow_rt_tape_zero_grads(void) {
    memset(g_grad, 0, sizeof(g_grad));
}
