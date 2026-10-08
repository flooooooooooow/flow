/* Native executor for the typed GPU render/compute graph (#812).
 *
 * stdlib/gpu_graph_exec.flow drives this ABI from a validated GpuGraph.
 * Metal implementation: runtime/gpu_metal_graph.m. Non-Apple hosts link
 * lib/runtime/gpu_memory_stub.flow, where new() returns NULL.
 *
 * The executor owns persistent device resources (storage buffers and 2D
 * storage textures, addressed by the graph's physical resource id), one
 * compiled pipeline per pass, and an rgba8unorm output target. A run
 * encodes every pass in recorded order into one command buffer: compute
 * passes share a concurrent compute encoder with a memory barrier before
 * each dispatch that depends on an earlier one, iterations rebind
 * ping-pong sides, and the render pass draws a fullscreen triangle.
 *
 * Every function that returns int32_t returns 0 (or a non-negative index)
 * on success and -1 on error; flow_gpu_graph_exec_error explains the last
 * error.
 */
#ifndef FLOW_GPU_GRAPH_EXEC_H
#define FLOW_GPU_GRAPH_EXEC_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Resource kinds and format tags match stdlib/gpu_graph.flow. */
enum {
    FLOW_GPU_GRAPH_KIND_BUFFER = 1,
    FLOW_GPU_GRAPH_KIND_TEXTURE = 2
};

enum {
    FLOW_GPU_GRAPH_PASS_COMPUTE = 1,
    FLOW_GPU_GRAPH_PASS_RENDER = 2
};

/* Statistics read with flow_gpu_graph_exec_stat. Counts cover the last run,
 * except FRAMES, which counts completed runs. */
enum {
    FLOW_GPU_GRAPH_STAT_DISPATCHES = 0,
    FLOW_GPU_GRAPH_STAT_BARRIERS = 1,
    FLOW_GPU_GRAPH_STAT_RENDER_PASSES = 2,
    FLOW_GPU_GRAPH_STAT_FRAMES = 3,
    FLOW_GPU_GRAPH_STAT_PASSES = 4,
    FLOW_GPU_GRAPH_STAT_RESOURCES = 5
};

/* NULL when no device is available. */
void *flow_gpu_graph_exec_new(void);
void flow_gpu_graph_exec_free(void *ex);
const char *flow_gpu_graph_exec_error(void *ex);

/* Allocate a zero-filled physical resource. */
int32_t flow_gpu_graph_exec_add_buffer(void *ex, int32_t physical, int64_t bytes);
int32_t flow_gpu_graph_exec_add_texture(void *ex, int32_t physical, int32_t format,
                                        int32_t width, int32_t height);

/* Compile one pass. `source` is the Metal Shading Language module the graph
 * emitted for it, `entry` its function name. Returns the pass index. */
int32_t flow_gpu_graph_exec_add_pass(void *ex, int32_t kind, const char *source,
                                     const char *entry,
                                     int32_t wg_x, int32_t wg_y, int32_t wg_z,
                                     int32_t grid_x, int32_t grid_y, int32_t grid_z,
                                     int32_t iterations, int32_t barrier_before);

/* Bind a physical resource to a slot. Even iterations use even_physical,
 * odd iterations use odd_physical (the other ping-pong side, or the same
 * resource for a plain binding). */
int32_t flow_gpu_graph_exec_bind(void *ex, int32_t pass, int32_t slot,
                                 int32_t even_physical, int32_t odd_physical);

/* Raw bytes in the resource's layout: f32 for buffers, row-major texels
 * for textures (r32float 4, rg32float 8, rgba16float 8, rgba8unorm 4
 * bytes per texel). nbytes must equal the resource size. */
int32_t flow_gpu_graph_exec_upload(void *ex, int32_t physical, const void *src, int64_t nbytes);
int32_t flow_gpu_graph_exec_read_resource(void *ex, int32_t physical, void *dst, int64_t nbytes);

/* Encode, submit and wait for every pass. */
int32_t flow_gpu_graph_exec_run(void *ex, int32_t width, int32_t height);

/* rgba8unorm pixels of the last run, width * height * 4 bytes, top row first. */
int32_t flow_gpu_graph_exec_readback(void *ex, void *dst, int64_t nbytes);

int32_t flow_gpu_graph_exec_stat(void *ex, int32_t which);

/* GPU time of the last run in milliseconds, from the command buffer. */
double flow_gpu_graph_exec_gpu_ms(void *ex);

#ifdef __cplusplus
}
#endif

#endif /* FLOW_GPU_GRAPH_EXEC_H */
