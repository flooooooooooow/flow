/* Serial CPU driver for Flow @gpu kernels.
 *
 * On a GPU, gpu_thread_id() is the invocation index and the whole grid runs at
 * once. To get a CPU reference out of the *same* kernel body, back that call
 * with a variable a loop advances, then call the kernel once per element.
 *
 * Flow's C generator emits its own `static inline int32_t gpu_thread_id(void)`
 * stub returning 0, but only when the program does not declare one. The Flow
 * side declares both of these `extern`, so this file wins.
 */
#include <stdint.h>

static int32_t g_flow_gpu_tid = 0;

int32_t gpu_thread_id(void) { return g_flow_gpu_tid; }

void gpu_set_thread_id(int32_t i) { g_flow_gpu_tid = i; }
