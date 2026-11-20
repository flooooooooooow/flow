/* Stub of the resident GPU host for platforms without Metal.
 * flow_gl_init reports the GPU path unavailable and every other call fails
 * with a message, so a program that checks gl_available() runs its CPU path. */
#ifndef __APPLE__

#include "gpu_metal_host.h"

static const char *k_msg = "the resident GPU host needs macOS with Metal";

int32_t flow_gl_init(int32_t flags) { (void)flags; return 0; }
int32_t flow_gl_available(void) { return 0; }
void flow_gl_shutdown(void) {}
const char *flow_gl_last_error(void) { return k_msg; }
const char *flow_gl_device_name(void) { return ""; }
int64_t flow_gl_stat(int32_t which) { (void)which; return 0; }
void flow_gl_force_off(int32_t off) { (void)off; }
int32_t flow_gl_attach_window(void *c, int32_t v) { (void)c; (void)v; return -1; }
void flow_gl_detach_window(void) {}
int32_t flow_gl_window_info(int32_t *out) { if (out) { out[0] = out[1] = out[3] = 0; out[2] = 100; } return -1; }
void flow_gl_set_vsync(int32_t on) { (void)on; }
int32_t flow_gl_buffer_new(int64_t b, int32_t f) { (void)b; (void)f; return -1; }
int32_t flow_gl_buffer_write(int32_t b, int64_t o, const uint8_t *s, int64_t n) { (void)b; (void)o; (void)s; (void)n; return -1; }
uint8_t *flow_gl_buffer_ptr(int32_t b) { (void)b; return 0; }
int32_t flow_gl_buffer_read(int32_t b, int64_t o, uint8_t *d, int64_t n) { (void)b; (void)o; (void)d; (void)n; return -1; }
int32_t flow_gl_buffer_free(int32_t b) { (void)b; return -1; }
int32_t flow_gl_texture_new(int32_t w, int32_t h, int32_t f, int32_t u) { (void)w; (void)h; (void)f; (void)u; return -1; }
int32_t flow_gl_texture_upload(int32_t t, const uint8_t *s, int32_t r) { (void)t; (void)s; (void)r; return -1; }
int32_t flow_gl_texture_upload_rect(int32_t t, int32_t x, int32_t y, int32_t w, int32_t h, const uint8_t *s, int32_t r) { (void)t; (void)x; (void)y; (void)w; (void)h; (void)s; (void)r; return -1; }
int32_t flow_gl_texture_read(int32_t t, uint8_t *d, int32_t r) { (void)t; (void)d; (void)r; return -1; }
int32_t flow_gl_texture_free(int32_t t) { (void)t; return -1; }
int32_t flow_gl_compute_pipeline(const char *m, const char *e) { (void)m; (void)e; return -1; }
int32_t flow_gl_render_pipeline_begin(const char *m, const char *v, const char *f, int32_t c, int32_t d, int32_t b) { (void)m; (void)v; (void)f; (void)c; (void)d; (void)b; return -1; }
int32_t flow_gl_pipeline_vertex_layout(int32_t p, int32_t s, int32_t st, int32_t i) { (void)p; (void)s; (void)st; (void)i; return -1; }
int32_t flow_gl_pipeline_vertex_attr(int32_t p, int32_t l, int32_t s, int32_t f, int32_t o) { (void)p; (void)l; (void)s; (void)f; (void)o; return -1; }
int32_t flow_gl_pipeline_state(int32_t p, int32_t c, int32_t d) { (void)p; (void)c; (void)d; return -1; }
int32_t flow_gl_pipeline_build(int32_t p) { (void)p; return -1; }
int32_t flow_gl_pipeline_free(int32_t p) { (void)p; return -1; }
int32_t flow_gl_begin_frame(void) { return -1; }
int32_t flow_gl_bind_buffer(int32_t s, int32_t b, int64_t o) { (void)s; (void)b; (void)o; return -1; }
int32_t flow_gl_bind_texture(int32_t s, int32_t t) { (void)s; (void)t; return -1; }
int32_t flow_gl_bind_sampler(int32_t s, int32_t l, int32_t r) { (void)s; (void)l; (void)r; return -1; }
int32_t flow_gl_bind_bytes(int32_t s, const uint8_t *p, int32_t n) { (void)s; (void)p; (void)n; return -1; }
int32_t flow_gl_dispatch(int32_t p, int32_t x, int32_t y, int32_t z) { (void)p; (void)x; (void)y; (void)z; return -1; }
int32_t flow_gl_dispatch_groups(int32_t p, int32_t a, int32_t b, int32_t c, int32_t x, int32_t y, int32_t z) { (void)p; (void)a; (void)b; (void)c; (void)x; (void)y; (void)z; return -1; }
int32_t flow_gl_dispatch_indirect(int32_t p, int32_t a, int64_t o, int32_t x, int32_t y, int32_t z) { (void)p; (void)a; (void)o; (void)x; (void)y; (void)z; return -1; }
int32_t flow_gl_pass_begin(int32_t c, int32_t d, int32_t l, float r, float g, float b, float a, float cd) { (void)c; (void)d; (void)l; (void)r; (void)g; (void)b; (void)a; (void)cd; return -1; }
int32_t flow_gl_draw(int32_t p, int32_t t, int32_t f, int32_t c, int32_t i) { (void)p; (void)t; (void)f; (void)c; (void)i; return -1; }
int32_t flow_gl_draw_indexed(int32_t p, int32_t t, int32_t b, int32_t u, int32_t f, int32_t c, int32_t i) { (void)p; (void)t; (void)b; (void)u; (void)f; (void)c; (void)i; return -1; }
int32_t flow_gl_draw_indirect(int32_t p, int32_t t, int32_t b, int64_t o) { (void)p; (void)t; (void)b; (void)o; return -1; }
int32_t flow_gl_pass_end(void) { return -1; }
int32_t flow_gl_blit(int32_t s, int32_t d, int32_t b) { (void)s; (void)d; (void)b; return -1; }
int32_t flow_gl_present(void) { return -1; }
int32_t flow_gl_submit(void) { return -1; }
int32_t flow_gl_wait_idle(void) { return -1; }
double flow_gl_gpu_time_ms(void) { return 0.0; }
int32_t flow_gl_pass_count(void) { return 0; }
double flow_gl_pass_time_ms(int32_t i) { (void)i; return -1.0; }

int32_t flow_gl_buffer_wrap(uint8_t *p, int64_t n) { (void)p; (void)n; return -1; }
int32_t flow_gl_pass_begin_noattach(int32_t w, int32_t h) { (void)w; (void)h; return -1; }
int32_t flow_gl_pass_name(const char *n) { (void)n; return -1; }
int32_t flow_gl_overlay_begin(void *c) { (void)c; return -1; }
int32_t flow_gl_overlay_present(int32_t x, int32_t y, int32_t w, int32_t h) { (void)x; (void)y; (void)w; (void)h; return -1; }
const char *flow_gl_pass_label(int32_t i) { (void)i; return ""; }

#endif
