// Headless recording backend for the FLOW gfx API.
//
// Implements exactly the same symbols as runtime/gfx_macos.m, but instead of
// opening a window it renders into an off-screen buffer and writes every
// presented frame to a numbered PPM. Demo GIFs are therefore produced by the
// real compiled program rather than by a re-implementation of it, and they can
// be regenerated on a machine with no display (CI included).
//
// This file keeps only the flow_gfx_* ABI symbol table and the framebuffer
// memory. The recorder logic (env parsing, key-injection schedule, frame
// counting, PPM writing) lives in lib/runtime/gfx_record.flow; `./flow record`
// transpiles that module and links it next to this file.
//
// Build (example):
//   clang -O2 prog.c build/runtime_flow/gfx_record.c runtime/gfx_record.c -o prog -lm
//
// Configured entirely through the environment so no program needs changing:
//   FLOW_GFX_RECORD_DIR     output directory for frames   (default ./frames)
//   FLOW_GFX_RECORD_FRAMES  stop after N presented frames (default 240)
//   FLOW_GFX_RECORD_SKIP    keep every Nth frame          (default 1)
//   FLOW_GFX_RECORD_KEYS    scripted input, see below     (default none)
//
// The key script drives interactive demos deterministically. It is a list of
// `first-last:keycode` windows over presented-frame numbers, for example
//   FLOW_GFX_RECORD_KEYS="24-27:124,48-51:126,70-95:125"
// holds Right for frames 24..27, Up for 48..51, then Down for 70..95. A single
// frame may be written as `frame:keycode`. Keycodes are the same NSEvent codes
// the programs already use (see lib/stdlib/gfx.flow).
//
// Pixel format: RGBA8 internally, written out as binary P6 RGB.

#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#define FLOW_GFX_MAX_KEY_WINDOWS 128

// Recorder logic exports from lib/runtime/gfx_record.flow.
int32_t flow_gfx_rec_env_int(const char *name, int32_t fallback);
void flow_gfx_rec_env_dir(uint8_t *out, int64_t cap);
int32_t flow_gfx_rec_parse_keys(int32_t *first, int32_t *last, int32_t *code,
                                int32_t cap);
int32_t flow_gfx_rec_parse_mouse(int32_t *first, int32_t *last, int32_t *x0,
                                 int32_t *y0, int32_t *x1, int32_t *y1,
                                 int32_t *btn, int32_t *whl, int32_t cap);
int32_t flow_gfx_rec_mouse(int32_t presented, int32_t *out, int32_t *first,
                           int32_t *last, int32_t *x0, int32_t *y0, int32_t *x1,
                           int32_t *y1, int32_t *btn, int32_t *whl,
                           int32_t count);
int32_t flow_gfx_rec_key_down(int32_t presented, int32_t keycode,
                              int32_t *first, int32_t *last, int32_t *code,
                              int32_t count);
int32_t flow_gfx_rec_should_close(int32_t closing, int32_t presented,
                                  int32_t max_frames);
int32_t flow_gfx_rec_present(uint8_t *dir, int32_t width, int32_t height,
                             uint8_t *pixels, int32_t skip, int32_t max_frames,
                             int32_t *presented, int32_t *written, void *err);

typedef struct {
    int width;
    int height;
    uint8_t *pixels; // width*height*4 RGBA

    uint8_t dir[1024];
    int32_t max_frames;
    int32_t skip;
    int32_t presented; // frames the program has drawn
    int32_t written;   // frames actually saved
    bool should_close;

    int32_t key_first[FLOW_GFX_MAX_KEY_WINDOWS];
    int32_t key_last[FLOW_GFX_MAX_KEY_WINDOWS];
    int32_t key_code[FLOW_GFX_MAX_KEY_WINDOWS];
    int32_t key_count;

    int32_t m_first[FLOW_GFX_MAX_KEY_WINDOWS];
    int32_t m_last[FLOW_GFX_MAX_KEY_WINDOWS];
    int32_t m_x0[FLOW_GFX_MAX_KEY_WINDOWS];
    int32_t m_y0[FLOW_GFX_MAX_KEY_WINDOWS];
    int32_t m_x1[FLOW_GFX_MAX_KEY_WINDOWS];
    int32_t m_y1[FLOW_GFX_MAX_KEY_WINDOWS];
    int32_t m_btn[FLOW_GFX_MAX_KEY_WINDOWS];
    int32_t m_whl[FLOW_GFX_MAX_KEY_WINDOWS];
    int32_t m_count;
} FlowGfxRecorder;

void *flow_gfx_init(int32_t w, int32_t h, const char *title_utf8) {
    if (w <= 0 || h <= 0) return NULL;
    FlowGfxRecorder *rec = (FlowGfxRecorder *)calloc(1, sizeof(FlowGfxRecorder));
    if (!rec) return NULL;

    rec->width = w;
    rec->height = h;
    rec->pixels = (uint8_t *)calloc((size_t)w * (size_t)h * 4u, 1);
    if (!rec->pixels) {
        free(rec);
        return NULL;
    }

    flow_gfx_rec_env_dir(rec->dir, (int64_t)sizeof(rec->dir));
    rec->max_frames = flow_gfx_rec_env_int("FLOW_GFX_RECORD_FRAMES", 240);
    rec->skip = flow_gfx_rec_env_int("FLOW_GFX_RECORD_SKIP", 1);
    rec->key_count = flow_gfx_rec_parse_keys(rec->key_first, rec->key_last,
                                             rec->key_code,
                                             FLOW_GFX_MAX_KEY_WINDOWS);
    rec->m_count = flow_gfx_rec_parse_mouse(rec->m_first, rec->m_last,
                                            rec->m_x0, rec->m_y0,
                                            rec->m_x1, rec->m_y1,
                                            rec->m_btn, rec->m_whl,
                                            FLOW_GFX_MAX_KEY_WINDOWS);

    fprintf(stderr, "[gfx-record] %s — %dx%d, up to %d frames → %s\n",
            title_utf8 ? title_utf8 : "(untitled)", w, h, rec->max_frames,
            (const char *)rec->dir);
    return rec;
}

void flow_gfx_shutdown(void *handle) {
    FlowGfxRecorder *rec = (FlowGfxRecorder *)handle;
    if (!rec) return;
    fprintf(stderr, "[gfx-record] wrote %d frame(s) of %d presented\n",
            rec->written, rec->presented);
    free(rec->pixels);
    free(rec);
}

int32_t flow_gfx_should_close(void *handle) {
    FlowGfxRecorder *rec = (FlowGfxRecorder *)handle;
    if (!rec) return 1;
    return flow_gfx_rec_should_close(rec->should_close ? 1 : 0, rec->presented,
                                     rec->max_frames);
}

void flow_gfx_poll(void *handle) {
    (void)handle; // No event source to drain when running headless.
}

/* Virtual clock. The recorder deliberately does not report wall time: a
 * recorded run must produce the same frames whatever the machine's speed, and
 * it should not burn real seconds sleeping. Time advances exactly one frame
 * per present, at FLOW_GFX_RECORD_FPS (default 60), so a demo that integrates
 * against gfx_time_ms gets identical output on every run and every host.
 *
 * This is simulated time, distinct from GIF playback rate, which
 * scripts/frames_to_gif.py sets separately with --fps/--stride. */
double flow_gfx_time_ms(void *handle) {
    FlowGfxRecorder *rec = (FlowGfxRecorder *)handle;
    if (!rec) return 0.0;
    int fps = 60;
    const char *env = getenv("FLOW_GFX_RECORD_FPS");
    if (env && *env) {
        int v = atoi(env);
        if (v > 0) fps = v;
    }
    return (double)rec->presented * 1000.0 / (double)fps;
}

/* No-op headless: the recorder should run as fast as the CPU allows. */
void flow_gfx_wait_frame(void *handle, int32_t target_fps) {
    (void)handle;
    (void)target_fps;
}

int32_t flow_gfx_key_down(void *handle, int32_t keycode) {
    FlowGfxRecorder *rec = (FlowGfxRecorder *)handle;
    if (!rec) return 0;
    return flow_gfx_rec_key_down(rec->presented, keycode, rec->key_first,
                                 rec->key_last, rec->key_code, rec->key_count);
}

/* Scripted pointer, so a mouse-driven demo can still be recorded as a GIF.
 * FLOW_GFX_RECORD_MOUSE holds ';'-separated segments of
 *   first,last,x0,y0,x1,y1,buttons,wheel
 * and the cursor lerps across each window with integer arithmetic, so the
 * result is bit-identical on every platform. */
int32_t flow_gfx_mouse(void *handle, int32_t *out) {
    if (!out) return 0;
    FlowGfxRecorder *rec = (FlowGfxRecorder *)handle;
    if (!rec) {
        for (int i = 0; i < 7; i++) out[i] = 0;
        return 0;
    }
    return flow_gfx_rec_mouse(rec->presented, out, rec->m_first, rec->m_last,
                              rec->m_x0, rec->m_y0, rec->m_x1, rec->m_y1,
                              rec->m_btn, rec->m_whl, rec->m_count);
}

void flow_gfx_clear(void *handle, uint8_t r, uint8_t g, uint8_t b) {
    FlowGfxRecorder *rec = (FlowGfxRecorder *)handle;
    if (!rec || !rec->pixels) return;
    size_t n = (size_t)rec->width * (size_t)rec->height;
    uint8_t *p = rec->pixels;
    for (size_t i = 0; i < n; i++) {
        p[i * 4 + 0] = r;
        p[i * 4 + 1] = g;
        p[i * 4 + 2] = b;
        p[i * 4 + 3] = 255;
    }
}


/* Blit a packed RGB8 buffer (w*h*3 bytes, row-major, no padding) into the
 * framebuffer at (x, y). Per-pixel work belongs here rather than in a
 * fill_rect call per pixel: a 320x240 particle field is 76800 rects a frame,
 * which the rect path cannot sustain. Clipped like fill_rect. */
void flow_gfx_blit_rgb(void *handle, int32_t x, int32_t y, int32_t w, int32_t h,
                       const uint8_t *src) {
    FlowGfxRecorder *ctx = (FlowGfxRecorder *)handle;
    if (!ctx || !ctx->pixels || !src) return;
    if (w <= 0 || h <= 0) return;

    int x0 = x < 0 ? 0 : x;
    int y0 = y < 0 ? 0 : y;
    int x1 = x + w; if (x1 > ctx->width) x1 = ctx->width;
    int y1 = y + h; if (y1 > ctx->height) y1 = ctx->height;
    if (x0 >= x1 || y0 >= y1) return;

    uint8_t *dst = ctx->pixels;
    for (int yy = y0; yy < y1; yy++) {
        const uint8_t *srow = src + ((size_t)(yy - y) * (size_t)w + (size_t)(x0 - x)) * 3u;
        uint8_t *drow = dst + ((size_t)yy * (size_t)ctx->width + (size_t)x0) * 4u;
        for (int xx = x0; xx < x1; xx++) {
            drow[0] = srow[0];
            drow[1] = srow[1];
            drow[2] = srow[2];
            drow[3] = 255;
            srow += 3;
            drow += 4;
        }
    }
}

void flow_gfx_fill_rect(void *handle, int32_t x, int32_t y, int32_t w, int32_t h,
                        uint8_t r, uint8_t g, uint8_t b) {
    FlowGfxRecorder *rec = (FlowGfxRecorder *)handle;
    if (!rec || !rec->pixels) return;
    if (w <= 0 || h <= 0) return;

    int x0 = x < 0 ? 0 : x;
    int y0 = y < 0 ? 0 : y;
    int x1 = x + w; if (x1 > rec->width) x1 = rec->width;
    int y1 = y + h; if (y1 > rec->height) y1 = rec->height;
    if (x0 >= x1 || y0 >= y1) return;

    uint8_t *p = rec->pixels;
    for (int yy = y0; yy < y1; yy++) {
        for (int xx = x0; xx < x1; xx++) {
            size_t idx = ((size_t)yy * (size_t)rec->width + (size_t)xx) * 4u;
            p[idx + 0] = r;
            p[idx + 1] = g;
            p[idx + 2] = b;
            p[idx + 3] = 255;
        }
    }
}


static const uint8_t flow_font_rows[665] = {
        0, 0, 0, 0, 0, 0, 0,
        4, 4, 4, 4, 4, 0, 4,
        10, 10, 0, 0, 0, 0, 0,
        10, 31, 10, 10, 31, 10, 0,
        4, 15, 20, 14, 5, 30, 4,
        25, 25, 2, 4, 8, 19, 19,
        12, 18, 20, 8, 21, 18, 13,
        4, 4, 0, 0, 0, 0, 0,
        2, 4, 8, 8, 8, 4, 2,
        8, 4, 2, 2, 2, 4, 8,
        0, 21, 14, 31, 14, 21, 0,
        0, 4, 4, 31, 4, 4, 0,
        0, 0, 0, 0, 12, 4, 8,
        0, 0, 0, 31, 0, 0, 0,
        0, 0, 0, 0, 0, 12, 12,
        1, 2, 2, 4, 8, 8, 16,
        14, 17, 19, 21, 25, 17, 14,
        4, 12, 4, 4, 4, 4, 14,
        14, 17, 1, 2, 4, 8, 31,
        31, 2, 4, 2, 1, 17, 14,
        2, 6, 10, 18, 31, 2, 2,
        31, 16, 30, 1, 1, 17, 14,
        6, 8, 16, 30, 17, 17, 14,
        31, 1, 2, 4, 8, 8, 8,
        14, 17, 17, 14, 17, 17, 14,
        14, 17, 17, 15, 1, 2, 12,
        0, 12, 12, 0, 12, 12, 0,
        0, 12, 12, 0, 12, 4, 8,
        2, 4, 8, 16, 8, 4, 2,
        0, 0, 31, 0, 31, 0, 0,
        8, 4, 2, 1, 2, 4, 8,
        14, 17, 1, 2, 4, 0, 4,
        14, 17, 23, 21, 23, 16, 14,
        14, 17, 17, 31, 17, 17, 17,
        30, 17, 17, 30, 17, 17, 30,
        14, 17, 16, 16, 16, 17, 14,
        28, 18, 17, 17, 17, 18, 28,
        31, 16, 16, 30, 16, 16, 31,
        31, 16, 16, 30, 16, 16, 16,
        14, 17, 16, 23, 17, 17, 15,
        17, 17, 17, 31, 17, 17, 17,
        14, 4, 4, 4, 4, 4, 14,
        7, 2, 2, 2, 2, 18, 12,
        17, 18, 20, 24, 20, 18, 17,
        16, 16, 16, 16, 16, 16, 31,
        17, 27, 21, 21, 17, 17, 17,
        17, 17, 25, 21, 19, 17, 17,
        14, 17, 17, 17, 17, 17, 14,
        30, 17, 17, 30, 16, 16, 16,
        14, 17, 17, 17, 21, 18, 13,
        30, 17, 17, 30, 20, 18, 17,
        15, 16, 16, 14, 1, 1, 30,
        31, 4, 4, 4, 4, 4, 4,
        17, 17, 17, 17, 17, 17, 14,
        17, 17, 17, 17, 17, 10, 4,
        17, 17, 17, 21, 21, 27, 17,
        17, 17, 10, 4, 10, 17, 17,
        17, 17, 10, 4, 4, 4, 4,
        31, 1, 2, 4, 8, 16, 31,
        14, 8, 8, 8, 8, 8, 14,
        16, 8, 8, 4, 2, 2, 1,
        14, 2, 2, 2, 2, 2, 14,
        4, 10, 17, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 31,
        8, 4, 0, 0, 0, 0, 0,
        0, 0, 14, 1, 15, 17, 15,
        16, 16, 30, 17, 17, 17, 30,
        0, 0, 14, 16, 16, 17, 14,
        1, 1, 15, 17, 17, 17, 15,
        0, 0, 14, 17, 31, 16, 14,
        6, 9, 8, 30, 8, 8, 8,
        0, 15, 17, 17, 15, 1, 14,
        16, 16, 30, 17, 17, 17, 17,
        4, 0, 12, 4, 4, 4, 14,
        2, 0, 6, 2, 2, 18, 12,
        16, 16, 18, 20, 24, 20, 18,
        12, 4, 4, 4, 4, 4, 14,
        0, 0, 26, 21, 21, 17, 17,
        0, 0, 30, 17, 17, 17, 17,
        0, 0, 14, 17, 17, 17, 14,
        0, 30, 17, 17, 30, 16, 16,
        0, 15, 17, 17, 15, 1, 1,
        0, 0, 22, 25, 16, 16, 16,
        0, 0, 15, 16, 14, 1, 30,
        8, 8, 30, 8, 8, 9, 6,
        0, 0, 17, 17, 17, 19, 13,
        0, 0, 17, 17, 17, 10, 4,
        0, 0, 17, 17, 21, 21, 10,
        0, 0, 17, 10, 4, 10, 17,
        0, 17, 17, 17, 15, 1, 14,
        0, 0, 31, 2, 4, 8, 31,
        6, 4, 4, 8, 4, 4, 6,
        4, 4, 4, 4, 4, 4, 4,
        12, 4, 4, 2, 4, 4, 12,
        0, 0, 13, 18, 0, 0, 0
};

static void flow_gfx_plot_pixel(FlowGfxRecorder *rec, int x, int y, uint8_t r, uint8_t g, uint8_t b) {
    if (x >= 0 && x < rec->width && y >= 0 && y < rec->height) {
        size_t idx = ((size_t)y * (size_t)rec->width + (size_t)x) * 4u;
        rec->pixels[idx + 0] = r;
        rec->pixels[idx + 1] = g;
        rec->pixels[idx + 2] = b;
        rec->pixels[idx + 3] = 255;
    }
}

void flow_gfx_text(void* handle, int32_t x, int32_t y, const char* text,
                   int32_t size, uint8_t r, uint8_t g, uint8_t b) {
    FlowGfxRecorder *rec = (FlowGfxRecorder *)handle;
    if (!rec || !rec->pixels || !text || size <= 0) return;

    int32_t start_x = x;
    int32_t pen_x = x;
    int32_t pen_y = y;

    for (int i = 0; text[i]; i++) {
        int ch = (unsigned char)text[i];
        if (ch == '\n') {
            pen_y += 8 * size;
            pen_x = start_x;
            continue;
        }
        if (ch >= 32 && ch <= 126) {
            int idx = (ch - 32) * 7;
            for (int row = 0; row < 7; row++) {
                uint8_t bits = flow_font_rows[idx + row];
                for (int col = 0; col < 5; col++) {
                    if ((bits >> (4 - col)) & 1) {
                        for (int dy = 0; dy < size; dy++) {
                            for (int dx = 0; dx < size; dx++) {
                                flow_gfx_plot_pixel(rec, pen_x + col * size + dx, pen_y + row * size + dy, r, g, b);
                            }
                        }
                    }
                }
            }
        }
        pen_x += 6 * size;
    }
}

void flow_gfx_present(void *handle) {
    FlowGfxRecorder *rec = (FlowGfxRecorder *)handle;
    if (!rec || !rec->pixels) return;
    if (flow_gfx_rec_present(rec->dir, rec->width, rec->height, rec->pixels,
                             rec->skip, rec->max_frames, &rec->presented,
                             &rec->written, stderr)) {
        rec->should_close = true;
    }
}

// Mirrors the weak default in the windowed backends.
__attribute__((weak)) int32_t flow_gfx_frame(void *handle, int32_t frame) {
    (void)handle;
    (void)frame;
    return 0;
}

int32_t flow_gfx_run(void *handle, int32_t max_frames) {
    if (!handle || max_frames <= 0) return 0;
    for (int32_t frame = 0; frame < max_frames; frame++) {
        flow_gfx_poll(handle);
        if (flow_gfx_should_close(handle)) return frame;
        if (!flow_gfx_frame(handle, frame)) return frame;
    }
    return max_frames;
}
