/*
 * Linux graphics backend — STUB
 *
 * Intended to implement the same C ABI as runtime/gfx_macos.m and
 * lib/stdlib/gfx.flow (window + software RGBA8 framebuffer).
 *
 * Status: not implemented. Linking this file lets Linux builds resolve
 * symbols; every call logs once (or on init) and does nothing useful.
 *
 * Next (small, not a Vulkan rewrite):
 *   1. SDL2 window + texture present of an RGBA8 pixel buffer
 *   2. Match macOS signatures exactly (ctx handle, poll, key_down, …)
 *   3. Wire from package/build so Linux picks gfx_linux.c over gfx_macos.m
 *
 * See docs/language/graphics.md and runtime/README.md.
 */
#include <stdint.h>
#include <stdio.h>

#ifndef FLOW_GFX_STUB_MSG
#define FLOW_GFX_STUB_MSG \
    "flow gfx: Linux backend is a stub — no window. " \
    "Implement SDL2 (or X11) in runtime/gfx_linux.c; see docs/language/graphics.md\n"
#endif

static void flow_gfx_linux_warn_once(void) {
    static int warned = 0;
    if (!warned) {
        warned = 1;
        fputs(FLOW_GFX_STUB_MSG, stderr);
    }
}

void* flow_gfx_init(int32_t w, int32_t h, const char* title_utf8) {
    (void)w;
    (void)h;
    fprintf(stderr,
            "flow gfx: Linux stub — refusing window \"%s\" (%dx%d). "
            "Need SDL2/X11 backend; macOS uses runtime/gfx_macos.m.\n",
            title_utf8 ? title_utf8 : "Flow",
            (int)w,
            (int)h);
    return NULL;
}

void flow_gfx_shutdown(void* handle) {
    (void)handle;
    flow_gfx_linux_warn_once();
}

void flow_gfx_poll(void* handle) {
    (void)handle;
    flow_gfx_linux_warn_once();
}

int32_t flow_gfx_should_close(void* handle) {
    (void)handle;
    /* No window → treat as closed so loops exit instead of spinning forever. */
    return 1;
}

int32_t flow_gfx_key_down(void* handle, int32_t keycode) {
    (void)handle;
    (void)keycode;
    return 0;
}

void flow_gfx_clear(void* handle, uint8_t r, uint8_t g, uint8_t b) {
    (void)handle;
    (void)r;
    (void)g;
    (void)b;
    flow_gfx_linux_warn_once();
}

void flow_gfx_fill_rect(void* handle, int32_t x, int32_t y, int32_t w, int32_t h,
                        uint8_t r, uint8_t g, uint8_t b) {
    (void)handle;
    (void)x;
    (void)y;
    (void)w;
    (void)h;
    (void)r;
    (void)g;
    (void)b;
    flow_gfx_linux_warn_once();
}

void flow_gfx_present(void* handle) {
    (void)handle;
    flow_gfx_linux_warn_once();
}
