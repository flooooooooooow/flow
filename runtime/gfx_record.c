// Headless recording backend for the FLOW gfx API.
//
// Implements exactly the same symbols as runtime/gfx_macos.m, but instead of
// opening a window it renders into an off-screen buffer and writes every
// presented frame to a numbered PPM. Demo GIFs are therefore produced by the
// real compiled program rather than by a re-implementation of it, and they can
// be regenerated on a machine with no display (CI included).
//
// Build (example):
//   clang -O2 prog.c runtime/gfx_record.c runtime/flow_time.c -o prog -lm
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
#include <string.h>
#include <sys/stat.h>

#define FLOW_GFX_MAX_KEY_WINDOWS 128

typedef struct {
    int32_t first;
    int32_t last;
    int32_t keycode;
} FlowGfxKeyWindow;

typedef struct {
    int width;
    int height;
    uint8_t *pixels; // width*height*4 RGBA

    char dir[1024];
    int32_t max_frames;
    int32_t skip;
    int32_t presented; // frames the program has drawn
    int32_t written;   // frames actually saved
    bool should_close;

    FlowGfxKeyWindow keys[FLOW_GFX_MAX_KEY_WINDOWS];
    int key_count;
} FlowGfxRecorder;

static int32_t flow_gfx_env_int(const char *name, int32_t fallback) {
    const char *raw = getenv(name);
    if (!raw || !*raw) return fallback;
    char *end = NULL;
    long value = strtol(raw, &end, 10);
    if (end == raw || value <= 0) return fallback;
    return (int32_t)value;
}

// Parses "first-last:keycode" / "frame:keycode" entries separated by commas.
static void flow_gfx_parse_keys(FlowGfxRecorder *rec, const char *spec) {
    if (!spec || !*spec) return;
    const char *p = spec;
    while (*p && rec->key_count < FLOW_GFX_MAX_KEY_WINDOWS) {
        while (*p == ',' || *p == ' ') p++;
        if (!*p) break;

        char *end = NULL;
        long first = strtol(p, &end, 10);
        if (end == p) break;
        p = end;

        long last = first;
        if (*p == '-') {
            p++;
            last = strtol(p, &end, 10);
            if (end == p) break;
            p = end;
        }
        if (*p != ':') break;
        p++;
        long code = strtol(p, &end, 10);
        if (end == p) break;
        p = end;

        if (last < first) last = first;
        rec->keys[rec->key_count].first = (int32_t)first;
        rec->keys[rec->key_count].last = (int32_t)last;
        rec->keys[rec->key_count].keycode = (int32_t)code;
        rec->key_count++;
    }
}

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

    const char *dir = getenv("FLOW_GFX_RECORD_DIR");
    snprintf(rec->dir, sizeof(rec->dir), "%s", (dir && *dir) ? dir : "frames");
    mkdir(rec->dir, 0755);

    rec->max_frames = flow_gfx_env_int("FLOW_GFX_RECORD_FRAMES", 240);
    rec->skip = flow_gfx_env_int("FLOW_GFX_RECORD_SKIP", 1);
    flow_gfx_parse_keys(rec, getenv("FLOW_GFX_RECORD_KEYS"));

    fprintf(stderr, "[gfx-record] %s — %dx%d, up to %d frames → %s\n",
            title_utf8 ? title_utf8 : "(untitled)", w, h, rec->max_frames, rec->dir);
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
    return (rec->should_close || rec->presented >= rec->max_frames) ? 1 : 0;
}

void flow_gfx_poll(void *handle) {
    (void)handle; // No event source to drain when running headless.
}

int32_t flow_gfx_key_down(void *handle, int32_t keycode) {
    FlowGfxRecorder *rec = (FlowGfxRecorder *)handle;
    if (!rec) return 0;
    for (int i = 0; i < rec->key_count; i++) {
        if (rec->keys[i].keycode != keycode) continue;
        if (rec->presented >= rec->keys[i].first && rec->presented <= rec->keys[i].last) {
            return 1;
        }
    }
    return 0;
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

static void flow_gfx_write_ppm(FlowGfxRecorder *rec) {
    char path[1152];
    snprintf(path, sizeof(path), "%s/frame_%05d.ppm", rec->dir, rec->written);
    FILE *f = fopen(path, "wb");
    if (!f) {
        fprintf(stderr, "[gfx-record] cannot write %s\n", path);
        return;
    }
    fprintf(f, "P6\n%d %d\n255\n", rec->width, rec->height);
    size_t n = (size_t)rec->width * (size_t)rec->height;
    for (size_t i = 0; i < n; i++) {
        fwrite(&rec->pixels[i * 4], 1, 3, f); // drop alpha
    }
    fclose(f);
    rec->written++;
}

void flow_gfx_present(void *handle) {
    FlowGfxRecorder *rec = (FlowGfxRecorder *)handle;
    if (!rec || !rec->pixels) return;
    if (rec->presented % rec->skip == 0 && rec->presented < rec->max_frames) {
        flow_gfx_write_ppm(rec);
    }
    rec->presented++;
    if (rec->presented >= rec->max_frames) rec->should_close = true;
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
