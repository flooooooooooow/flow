/* Resident Metal host for Flow (lib/stdlib/gpu_live.flow).
 *
 * One MTLDevice, one MTLCommandQueue and one library cache live for the whole
 * process. Buffers, textures and pipelines are created once and named by
 * integer handles. Each frame the program binds resources, encodes compute
 * dispatches and render passes, and presents. Nothing is written to a file and
 * nothing is read back unless the program asks.
 *
 * Conventions. A function that creates something returns a handle >= 1, or -1
 * on failure. Any other function returns 0 on success and -1 on failure. After
 * a failure flow_gl_last_error() returns a message. No function in this file
 * aborts the process on a bad argument.
 *
 * Threads. See docs/gpu-host.md. Window calls and the frame calls
 * (begin, pass, dispatch, draw, present) belong to one thread at a time.
 * Resource calls may come from any thread.
 */
#ifndef FLOW_GPU_METAL_HOST_H
#define FLOW_GPU_METAL_HOST_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* flow_gl_init flags: the low two bits set the frames in flight (1 to 3, 0 means 3). */

/* Texture formats. FLOW_GL_FORMAT_NONE is for pipelines and passes with no colour attachment. */
enum {
    FLOW_GL_FORMAT_NONE = 0,
    FLOW_GL_RGBA8 = 1, FLOW_GL_BGRA8 = 2, FLOW_GL_RGBA16F = 3, FLOW_GL_R32F = 4,
    FLOW_GL_RGBA32F = 5, FLOW_GL_R8 = 6, FLOW_GL_DEPTH32F = 7,
};

/* Texture usage flags */
enum {
    FLOW_GL_TEX_SAMPLED = 1, FLOW_GL_TEX_STORAGE = 2, FLOW_GL_TEX_TARGET = 4,
    FLOW_GL_TEX_STREAM = 8, FLOW_GL_TEX_GPU_ONLY = 16,
};

/* Buffer flags */
enum { FLOW_GL_BUF_STREAM = 1 };

/* Vertex attribute formats */
enum {
    FLOW_GL_V_FLOAT = 1, FLOW_GL_V_FLOAT2 = 2, FLOW_GL_V_FLOAT3 = 3, FLOW_GL_V_FLOAT4 = 4,
    FLOW_GL_V_UCHAR4_NORM = 5, FLOW_GL_V_UINT = 6, FLOW_GL_V_INT = 7,
};

/* Blend modes, cull modes, depth modes, topologies, load actions */
enum { FLOW_GL_BLEND_NONE = 0, FLOW_GL_BLEND_ALPHA = 1, FLOW_GL_BLEND_ADD = 2, FLOW_GL_BLEND_PREMUL = 3 };
enum { FLOW_GL_CULL_NONE = 0, FLOW_GL_CULL_BACK = 1, FLOW_GL_CULL_FRONT = 2 };
enum { FLOW_GL_DEPTH_OFF = 0, FLOW_GL_DEPTH_TEST = 1, FLOW_GL_DEPTH_WRITE = 2 };
enum { FLOW_GL_TRIANGLES = 0, FLOW_GL_LINES = 1, FLOW_GL_POINTS = 2, FLOW_GL_TRIANGLE_STRIP = 3 };
enum { FLOW_GL_LOAD_CLEAR = 0, FLOW_GL_LOAD_KEEP = 1 };

/* flow_gl_stat selectors */
enum {
    FLOW_GL_STAT_BUFFERS = 0, FLOW_GL_STAT_TEXTURES = 1, FLOW_GL_STAT_PIPELINES = 2,
    FLOW_GL_STAT_RESOURCE_BYTES = 3, FLOW_GL_STAT_ALLOCATIONS = 4,
    FLOW_GL_STAT_FRAMES_SUBMITTED = 5, FLOW_GL_STAT_FRAMES_COMPLETED = 6,
    FLOW_GL_STAT_DEVICE_BYTES = 7, FLOW_GL_STAT_PROCESS_RSS = 8,
    FLOW_GL_STAT_LIBRARY_COMPILES = 9, FLOW_GL_STAT_LIBRARY_HITS = 10,
    FLOW_GL_STAT_DRAWABLES = 11, FLOW_GL_STAT_FRAME_SLOTS = 12,
    FLOW_GL_STAT_PASS_TIMING = 13, /* 1 when per-pass GPU timestamps work */
    FLOW_GL_STAT_UNIFIED_MEMORY = 14,
    FLOW_GL_STAT_OVERLAY_TEXTURE = 15, /* handle of the overlay texture, for tests */
};

/* Lifecycle */
int32_t     flow_gl_init(int32_t flags);          /* 1 ready, 0 unavailable */
int32_t     flow_gl_available(void);
void        flow_gl_shutdown(void);
const char* flow_gl_last_error(void);
const char* flow_gl_device_name(void);
int64_t     flow_gl_stat(int32_t which);
void        flow_gl_force_off(int32_t off);       /* test hook, also FLOW_GL_FORCE_OFF=1 */

/* Window. ctx is the pointer inside a Gfx value (Gfx.ctx). */
int32_t flow_gl_attach_window(void* gfx_ctx, int32_t vsync);
void    flow_gl_detach_window(void);
int32_t flow_gl_window_info(int32_t* out);        /* w, h in pixels, scale x100, attached */
void    flow_gl_set_vsync(int32_t on);

/* Buffers */
int32_t flow_gl_buffer_new(int64_t bytes, int32_t flags);
int32_t flow_gl_buffer_write(int32_t buf, int64_t offset, const uint8_t* src, int64_t n);
uint8_t* flow_gl_buffer_ptr(int32_t buf);
int32_t flow_gl_buffer_read(int32_t buf, int64_t offset, uint8_t* dst, int64_t n);
int32_t flow_gl_buffer_wrap(uint8_t* ptr, int64_t bytes);  /* page aligned memory, no copy */
int32_t flow_gl_buffer_free(int32_t buf);

/* Textures */
int32_t flow_gl_texture_new(int32_t w, int32_t h, int32_t format, int32_t usage);
int32_t flow_gl_texture_upload(int32_t tex, const uint8_t* src, int32_t bytes_per_row);
int32_t flow_gl_texture_upload_rect(int32_t tex, int32_t x, int32_t y, int32_t w, int32_t h,
                                    const uint8_t* src, int32_t bytes_per_row);
int32_t flow_gl_texture_read(int32_t tex, uint8_t* dst, int32_t bytes_per_row);
int32_t flow_gl_texture_free(int32_t tex);

/* Pipelines */
int32_t flow_gl_compute_pipeline(const char* msl, const char* entry);
int32_t flow_gl_render_pipeline_begin(const char* msl, const char* vs_entry, const char* fs_entry,
                                      int32_t color_format, int32_t depth_format, int32_t blend);
int32_t flow_gl_pipeline_vertex_layout(int32_t pipe, int32_t slot, int32_t stride, int32_t per_instance);
int32_t flow_gl_pipeline_vertex_attr(int32_t pipe, int32_t location, int32_t slot, int32_t format, int32_t offset);
int32_t flow_gl_pipeline_state(int32_t pipe, int32_t cull, int32_t depth_mode);
int32_t flow_gl_pipeline_build(int32_t pipe);
int32_t flow_gl_pipeline_free(int32_t pipe);

/* Frame */
int32_t flow_gl_begin_frame(void);
int32_t flow_gl_bind_buffer(int32_t slot, int32_t buf, int64_t offset);
int32_t flow_gl_bind_texture(int32_t slot, int32_t tex);
int32_t flow_gl_bind_sampler(int32_t slot, int32_t linear, int32_t repeat);
int32_t flow_gl_bind_bytes(int32_t slot, const uint8_t* src, int32_t n);
int32_t flow_gl_dispatch(int32_t pipe, int32_t x, int32_t y, int32_t z);
int32_t flow_gl_dispatch_groups(int32_t pipe, int32_t gx, int32_t gy, int32_t gz,
                                int32_t tx, int32_t ty, int32_t tz);
int32_t flow_gl_dispatch_indirect(int32_t pipe, int32_t args_buf, int64_t offset,
                                  int32_t tx, int32_t ty, int32_t tz);
int32_t flow_gl_pass_begin(int32_t color, int32_t depth, int32_t load,
                           float r, float g, float b, float a, float clear_depth);
int32_t flow_gl_draw(int32_t pipe, int32_t topology, int32_t first, int32_t count, int32_t instances);
int32_t flow_gl_draw_indexed(int32_t pipe, int32_t topology, int32_t index_buf, int32_t index_u32,
                             int32_t first_index, int32_t count, int32_t instances);
int32_t flow_gl_draw_indirect(int32_t pipe, int32_t topology, int32_t args_buf, int64_t offset);
int32_t flow_gl_pass_begin_noattach(int32_t w, int32_t h);
int32_t flow_gl_pass_name(const char* name);       /* names the next pass */
int32_t flow_gl_pass_end(void);
int32_t flow_gl_overlay_begin(void* gfx_ctx);
int32_t flow_gl_overlay_present(int32_t x, int32_t y, int32_t w, int32_t h);
int32_t flow_gl_blit(int32_t src, int32_t dst, int32_t blend);
int32_t flow_gl_present(void);
int32_t flow_gl_submit(void);
int32_t flow_gl_wait_idle(void);

/* Timing */
double  flow_gl_gpu_time_ms(void);                /* last completed frame */
int32_t flow_gl_pass_count(void);                 /* passes of the last completed frame */
double  flow_gl_pass_time_ms(int32_t index);
const char* flow_gl_pass_label(int32_t index);

#ifdef __cplusplus
}
#endif
#endif
