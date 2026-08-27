/*
 * Shared SDL2 implementation of the Flow gfx ABI — included (not compiled
 * directly) by runtime/gfx_linux.c and runtime/gfx_windows.c.
 *
 * Same C ABI as runtime/gfx_macos.m / lib/stdlib/gfx.flow:
 *   flow_gfx_init / shutdown / poll / should_close / key_down /
 *   clear / fill_rect / present
 *
 * The includer defines FLOW_GFX_BACKEND_NAME (e.g. "Linux" / "Windows")
 * before pulling this file in, used only for diagnostic messages below.
 *
 * Keycodes: Flow's gfx.flow uses macOS virtual keycodes (KEY_A=0, …).
 * This backend maps SDL scancodes → those same codes so demos stay portable.
 *
 * See docs/language/graphics.md and runtime/README.md.
 */

#ifndef FLOW_GFX_BACKEND_NAME
#define FLOW_GFX_BACKEND_NAME "SDL2"
#endif

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#if !defined(FLOW_GFX_STUB) && defined(__has_include)
#  if __has_include(<SDL2/SDL.h>)
#    define FLOW_GFX_USE_SDL2 1
#  elif __has_include(<SDL.h>)
#    define FLOW_GFX_USE_SDL2 1
#    define FLOW_GFX_SDL_PLAIN 1
#  endif
#endif

#if defined(FLOW_GFX_USE_SDL2)

#if defined(FLOW_GFX_SDL_PLAIN)
#  include <SDL.h>
#else
#  include <SDL2/SDL.h>
#endif

typedef struct FlowGfxContext {
    SDL_Window* window;
    SDL_Renderer* renderer;
    SDL_Texture* texture;
    uint8_t* pixels;
    int width;
    int height;
    int should_close;
    uint8_t keys[256];

    /* Pointer state, already in framebuffer coordinates: SDL reports
     * top-left origin, which matches the buffer, so no flip is needed. */
    int32_t mouse_x;
    int32_t mouse_y;
    uint8_t mouse_left;
    uint8_t mouse_right;
    uint8_t mouse_middle;
    int32_t mouse_wheel;   /* cumulative signed total */
    uint8_t mouse_inside;
} FlowGfxContext;

/* Map SDL scancode → macOS-style virtual keycode used by lib/stdlib/gfx.flow.
 *
 * Examples hardcode macOS NSEvent keycodes (KEY_P = 35, KEY_1 = 18, ...), so
 * every backend has to speak those numbers. This table mirrors the one in
 * runtime/gfx_wasm.c, which is the de-facto spec.
 *
 * SDL_Scancode is deliberate: it is the physical key position, which is what
 * NSEvent.keyCode reports. SDL_Keycode would be the layout-mapped symbol and
 * would break on any non-QWERTY keyboard. */
static int flow_gfx_map_scancode(SDL_Scancode sc) {
    switch (sc) {
        /* Letters */
        case SDL_SCANCODE_A: return 0;
        case SDL_SCANCODE_S: return 1;
        case SDL_SCANCODE_D: return 2;
        case SDL_SCANCODE_F: return 3;
        case SDL_SCANCODE_H: return 4;
        case SDL_SCANCODE_G: return 5;
        case SDL_SCANCODE_Z: return 6;
        case SDL_SCANCODE_X: return 7;
        case SDL_SCANCODE_C: return 8;
        case SDL_SCANCODE_V: return 9;
        case SDL_SCANCODE_B: return 11;
        case SDL_SCANCODE_Q: return 12;
        case SDL_SCANCODE_W: return 13;
        case SDL_SCANCODE_E: return 14;
        case SDL_SCANCODE_R: return 15;
        case SDL_SCANCODE_Y: return 16;
        case SDL_SCANCODE_T: return 17;
        case SDL_SCANCODE_O: return 31;
        case SDL_SCANCODE_U: return 32;
        case SDL_SCANCODE_I: return 34;
        case SDL_SCANCODE_P: return 35;
        case SDL_SCANCODE_L: return 37;
        case SDL_SCANCODE_J: return 38;
        case SDL_SCANCODE_K: return 40;
        case SDL_SCANCODE_N: return 45;
        case SDL_SCANCODE_M: return 46;
        /* Digits (note 5 and 6 are swapped relative to their order) */
        case SDL_SCANCODE_1: return 18;
        case SDL_SCANCODE_2: return 19;
        case SDL_SCANCODE_3: return 20;
        case SDL_SCANCODE_4: return 21;
        case SDL_SCANCODE_6: return 22;
        case SDL_SCANCODE_5: return 23;
        case SDL_SCANCODE_9: return 25;
        case SDL_SCANCODE_7: return 26;
        case SDL_SCANCODE_8: return 28;
        case SDL_SCANCODE_0: return 29;
        /* Punctuation */
        case SDL_SCANCODE_EQUALS: return 24;
        case SDL_SCANCODE_MINUS: return 27;
        case SDL_SCANCODE_RIGHTBRACKET: return 30;
        case SDL_SCANCODE_LEFTBRACKET: return 33;
        case SDL_SCANCODE_APOSTROPHE: return 39;
        case SDL_SCANCODE_SEMICOLON: return 41;
        case SDL_SCANCODE_BACKSLASH: return 42;
        case SDL_SCANCODE_COMMA: return 43;
        case SDL_SCANCODE_SLASH: return 44;
        case SDL_SCANCODE_PERIOD: return 47;
        case SDL_SCANCODE_GRAVE: return 50;
        /* Control keys */
        case SDL_SCANCODE_RETURN: return 36;
        case SDL_SCANCODE_TAB: return 48;
        case SDL_SCANCODE_SPACE: return 49;
        case SDL_SCANCODE_BACKSPACE: return 51;
        case SDL_SCANCODE_ESCAPE: return 53;
        /* Modifiers (macOS NSEvent keycodes) */
        case SDL_SCANCODE_LSHIFT: return 56;
        case SDL_SCANCODE_RSHIFT: return 60;
        case SDL_SCANCODE_LCTRL: return 59;
        case SDL_SCANCODE_RCTRL: return 62;
        case SDL_SCANCODE_LALT: return 58;
        case SDL_SCANCODE_RALT: return 61;
        case SDL_SCANCODE_LGUI: return 55;
        case SDL_SCANCODE_RGUI: return 54;
        /* Arrows */
        case SDL_SCANCODE_LEFT: return 123;
        case SDL_SCANCODE_RIGHT: return 124;
        case SDL_SCANCODE_DOWN: return 125;
        case SDL_SCANCODE_UP: return 126;
        default: return -1;
    }
}

void* flow_gfx_init(int32_t w, int32_t h, const char* title_utf8) {
    if (w <= 0 || h <= 0) {
        fprintf(stderr, "flow gfx: invalid size %dx%d\n", (int)w, (int)h);
        return NULL;
    }
    if (SDL_Init(SDL_INIT_VIDEO) != 0) {
        fprintf(stderr, "flow gfx: SDL_Init failed: %s\n", SDL_GetError());
        return NULL;
    }

    FlowGfxContext* ctx = (FlowGfxContext*)calloc(1, sizeof(FlowGfxContext));
    if (!ctx) {
        SDL_Quit();
        return NULL;
    }
    ctx->width = (int)w;
    ctx->height = (int)h;
    ctx->pixels = (uint8_t*)calloc((size_t)w * (size_t)h * 4u, 1);
    if (!ctx->pixels) {
        free(ctx);
        SDL_Quit();
        return NULL;
    }

    const char* title = title_utf8 ? title_utf8 : "Flow";
    ctx->window = SDL_CreateWindow(
        title,
        SDL_WINDOWPOS_CENTERED,
        SDL_WINDOWPOS_CENTERED,
        (int)w,
        (int)h,
        SDL_WINDOW_SHOWN
    );
    if (!ctx->window) {
        fprintf(stderr, "flow gfx: SDL_CreateWindow failed: %s\n", SDL_GetError());
        free(ctx->pixels);
        free(ctx);
        SDL_Quit();
        return NULL;
    }

    ctx->renderer = SDL_CreateRenderer(ctx->window, -1, SDL_RENDERER_ACCELERATED);
    if (!ctx->renderer) {
        ctx->renderer = SDL_CreateRenderer(ctx->window, -1, 0);
    }
    if (!ctx->renderer) {
        fprintf(stderr, "flow gfx: SDL_CreateRenderer failed: %s\n", SDL_GetError());
        SDL_DestroyWindow(ctx->window);
        free(ctx->pixels);
        free(ctx);
        SDL_Quit();
        return NULL;
    }

    /* RGBA8888 software buffer uploaded each present */
    ctx->texture = SDL_CreateTexture(
        ctx->renderer,
        SDL_PIXELFORMAT_RGBA32,
        SDL_TEXTUREACCESS_STREAMING,
        (int)w,
        (int)h
    );
    if (!ctx->texture) {
        fprintf(stderr, "flow gfx: SDL_CreateTexture failed: %s\n", SDL_GetError());
        SDL_DestroyRenderer(ctx->renderer);
        SDL_DestroyWindow(ctx->window);
        free(ctx->pixels);
        free(ctx);
        SDL_Quit();
        return NULL;
    }

    return (void*)ctx;
}

void flow_gfx_shutdown(void* handle) {
    FlowGfxContext* ctx = (FlowGfxContext*)handle;
    if (!ctx) return;
    if (ctx->texture) SDL_DestroyTexture(ctx->texture);
    if (ctx->renderer) SDL_DestroyRenderer(ctx->renderer);
    if (ctx->window) SDL_DestroyWindow(ctx->window);
    free(ctx->pixels);
    free(ctx);
    SDL_Quit();
}

void flow_gfx_poll(void* handle) {
    FlowGfxContext* ctx = (FlowGfxContext*)handle;
    if (!ctx) return;
    SDL_Event ev;
    while (SDL_PollEvent(&ev)) {
        if (ev.type == SDL_QUIT) {
            ctx->should_close = 1;
        } else if (ev.type == SDL_KEYDOWN || ev.type == SDL_KEYUP) {
            int code = flow_gfx_map_scancode(ev.key.keysym.scancode);
            if (code >= 0 && code < 256) {
                ctx->keys[code] = (ev.type == SDL_KEYDOWN) ? 1 : 0;
            }
            if (ev.type == SDL_KEYDOWN && ev.key.keysym.scancode == SDL_SCANCODE_ESCAPE) {
                ctx->should_close = 1;
            }
        } else if (ev.type == SDL_MOUSEMOTION) {
            ctx->mouse_x = ev.motion.x;
            ctx->mouse_y = ev.motion.y;
            ctx->mouse_inside = (ev.motion.x >= 0 && ev.motion.x < ctx->width &&
                                 ev.motion.y >= 0 && ev.motion.y < ctx->height) ? 1 : 0;
        } else if (ev.type == SDL_MOUSEBUTTONDOWN || ev.type == SDL_MOUSEBUTTONUP) {
            uint8_t down = (ev.type == SDL_MOUSEBUTTONDOWN) ? 1 : 0;
            ctx->mouse_x = ev.button.x;
            ctx->mouse_y = ev.button.y;
            if (ev.button.button == SDL_BUTTON_LEFT) ctx->mouse_left = down;
            else if (ev.button.button == SDL_BUTTON_RIGHT) ctx->mouse_right = down;
            else if (ev.button.button == SDL_BUTTON_MIDDLE) ctx->mouse_middle = down;
        } else if (ev.type == SDL_MOUSEWHEEL) {
            int32_t dy = ev.wheel.y;
            /* SDL inverts y on some platforms and flags it rather than
             * normalising, so honour the flag. */
            if (ev.wheel.direction == SDL_MOUSEWHEEL_FLIPPED) dy = -dy;
            ctx->mouse_wheel += dy;
        } else if (ev.type == SDL_WINDOWEVENT) {
            if (ev.window.event == SDL_WINDOWEVENT_ENTER) ctx->mouse_inside = 1;
            else if (ev.window.event == SDL_WINDOWEVENT_LEAVE) ctx->mouse_inside = 0;
        }
    }
}

int32_t flow_gfx_should_close(void* handle) {
    FlowGfxContext* ctx = (FlowGfxContext*)handle;
    if (!ctx) return 1;
    return ctx->should_close ? 1 : 0;
}

int32_t flow_gfx_key_down(void* handle, int32_t keycode) {
    FlowGfxContext* ctx = (FlowGfxContext*)handle;
    if (!ctx) return 0;
    if (keycode < 0 || keycode >= 256) return 0;
    return ctx->keys[keycode] ? 1 : 0;
}

/* Whole pointer state in one call. See runtime/gfx_macos.m for the layout:
 *   out[0..6] = x, y, left, right, middle, wheel(cumulative), inside
 * Returns 0 when there is no pointer, leaving out[] zeroed. */
int32_t flow_gfx_mouse(void* handle, int32_t* out) {
    if (!out) return 0;
    FlowGfxContext* ctx = (FlowGfxContext*)handle;
    if (!ctx) {
        for (int i = 0; i < 7; i++) out[i] = 0;
        return 0;
    }
    out[0] = ctx->mouse_x;
    out[1] = ctx->mouse_y;
    out[2] = ctx->mouse_left ? 1 : 0;
    out[3] = ctx->mouse_right ? 1 : 0;
    out[4] = ctx->mouse_middle ? 1 : 0;
    out[5] = ctx->mouse_wheel;
    out[6] = ctx->mouse_inside ? 1 : 0;
    return 1;
}

void flow_gfx_clear(void* handle, uint8_t r, uint8_t g, uint8_t b) {
    FlowGfxContext* ctx = (FlowGfxContext*)handle;
    if (!ctx || !ctx->pixels) return;
    size_t n = (size_t)ctx->width * (size_t)ctx->height;
    uint8_t* p = ctx->pixels;
    for (size_t i = 0; i < n; i++) {
        p[i * 4 + 0] = r;
        p[i * 4 + 1] = g;
        p[i * 4 + 2] = b;
        p[i * 4 + 3] = 255;
    }
}

void flow_gfx_fill_rect(void* handle, int32_t x, int32_t y, int32_t w, int32_t h,
                        uint8_t r, uint8_t g, uint8_t b) {
    FlowGfxContext* ctx = (FlowGfxContext*)handle;
    if (!ctx || !ctx->pixels) return;
    if (w <= 0 || h <= 0) return;

    int x0 = x < 0 ? 0 : (int)x;
    int y0 = y < 0 ? 0 : (int)y;
    int x1 = (int)x + (int)w; if (x1 > ctx->width) x1 = ctx->width;
    int y1 = (int)y + (int)h; if (y1 > ctx->height) y1 = ctx->height;
    if (x0 >= x1 || y0 >= y1) return;

    uint8_t* p = ctx->pixels;
    for (int yy = y0; yy < y1; yy++) {
        for (int xx = x0; xx < x1; xx++) {
            size_t idx = ((size_t)yy * (size_t)ctx->width + (size_t)xx) * 4u;
            p[idx + 0] = r;
            p[idx + 1] = g;
            p[idx + 2] = b;
            p[idx + 3] = 255;
        }
    }
}

/* Blit a packed RGB8 buffer (w*h*3 bytes, row-major, no padding) into the
 * framebuffer at (x, y). Per-pixel work belongs here rather than in a
 * fill_rect call per pixel: a 320x240 particle field is 76800 rects a frame,
 * which the rect path cannot sustain. Clipped like fill_rect.
 *
 * The framebuffer is SDL_PIXELFORMAT_RGBA32, which SDL defines to give byte
 * order R,G,B,A on both endiannesses — the same layout flow_gfx_clear and
 * flow_gfx_fill_rect above already write. So this is byte-identical to the
 * Cocoa implementation in runtime/gfx_macos.m. */
void flow_gfx_blit_rgb(void* handle, int32_t x, int32_t y, int32_t w, int32_t h,
                       const uint8_t* src) {
    FlowGfxContext* ctx = (FlowGfxContext*)handle;
    if (!ctx || !ctx->pixels || !src) return;
    if (w <= 0 || h <= 0) return;

    int x0 = x < 0 ? 0 : (int)x;
    int y0 = y < 0 ? 0 : (int)y;
    int x1 = (int)x + (int)w; if (x1 > ctx->width) x1 = ctx->width;
    int y1 = (int)y + (int)h; if (y1 > ctx->height) y1 = ctx->height;
    if (x0 >= x1 || y0 >= y1) return;

    uint8_t* dst = ctx->pixels;
    for (int yy = y0; yy < y1; yy++) {
        const uint8_t* srow = src + ((size_t)(yy - y) * (size_t)w + (size_t)(x0 - x)) * 3u;
        uint8_t* drow = dst + ((size_t)yy * (size_t)ctx->width + (size_t)x0) * 4u;
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

/* Milliseconds since the first call, from SDL's monotonic performance counter. */
double flow_gfx_time_ms(void* handle) {
    (void)handle;
    static Uint64 origin = 0;
    Uint64 freq = SDL_GetPerformanceFrequency();
    Uint64 now = SDL_GetPerformanceCounter();
    if (origin == 0) origin = now;
    if (freq == 0) return 0.0;
    return (double)(now - origin) * 1000.0 / (double)freq;
}

/* Sleep out the remainder of a frame at target_fps. The SDL window is created
 * without vsync, so without this a demo's speed is hardware-dependent. */
void flow_gfx_wait_frame(void* handle, int32_t target_fps) {
    static double next = 0.0;
    if (target_fps <= 0) return;
    double period = 1000.0 / (double)target_fps;
    double now = flow_gfx_time_ms(handle);
    if (next <= 0.0) { next = now + period; return; }
    double wait = next - now;
    if (wait > 0.0) {
        if (wait > period) wait = period;   /* clock jumped; do not stall */
        SDL_Delay((Uint32)wait);
    }
    next = (wait < -period) ? now + period : next + period;  /* resync if far behind */
}

void flow_gfx_present(void* handle) {
    FlowGfxContext* ctx = (FlowGfxContext*)handle;
    if (!ctx || !ctx->texture || !ctx->renderer || !ctx->pixels) return;
    SDL_UpdateTexture(ctx->texture, NULL, ctx->pixels, ctx->width * 4);
    SDL_RenderClear(ctx->renderer);
    SDL_RenderCopy(ctx->renderer, ctx->texture, NULL, NULL);
    SDL_RenderPresent(ctx->renderer);
}

__attribute__((weak)) int32_t flow_gfx_frame(void* handle, int32_t frame) {
    (void)handle;
    (void)frame;
    return 0;
}

int32_t flow_gfx_run(void* handle, int32_t max_frames) {
    if (!handle || max_frames <= 0) return 0;
    const int32_t key_esc = 53;
    for (int32_t frame = 0; frame < max_frames; frame++) {
        flow_gfx_poll(handle);
        if (flow_gfx_should_close(handle)) return frame;
        if (flow_gfx_key_down(handle, key_esc)) return frame;
        if (!flow_gfx_frame(handle, frame)) return frame;
    }
    return max_frames;
}

void flow_gfx_text(void* handle, int32_t x, int32_t y, const char* text,
                   int32_t size, uint8_t r, uint8_t g, uint8_t b) {
    (void)handle; (void)x; (void)y; (void)text; (void)size;
    (void)r; (void)g; (void)b;
}

#else /* FLOW_GFX_STUB or no SDL2 headers */

#ifndef FLOW_GFX_STUB_MSG
#define FLOW_GFX_STUB_MSG \
    "flow gfx: " FLOW_GFX_BACKEND_NAME " backend has no SDL2 headers — stub only. " \
    "Install SDL2 dev headers and rebuild without -DFLOW_GFX_STUB; see docs/language/graphics.md\n"
#endif

static void flow_gfx_sdl_warn_once(void) {
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
            "flow gfx: " FLOW_GFX_BACKEND_NAME " stub — refusing window \"%s\" (%dx%d). "
            "Need SDL2 headers + -lSDL2; see docs/language/graphics.md\n",
            title_utf8 ? title_utf8 : "Flow",
            (int)w,
            (int)h);
    return NULL;
}

void flow_gfx_shutdown(void* handle) {
    (void)handle;
    flow_gfx_sdl_warn_once();
}

void flow_gfx_poll(void* handle) {
    (void)handle;
    flow_gfx_sdl_warn_once();
}

int32_t flow_gfx_should_close(void* handle) {
    (void)handle;
    return 1;
}

int32_t flow_gfx_key_down(void* handle, int32_t keycode) {
    (void)handle;
    (void)keycode;
    return 0;
}

/* No window, so no pointer: report absence and leave out[] zeroed. */
int32_t flow_gfx_mouse(void* handle, int32_t* out) {
    (void)handle;
    if (!out) return 0;
    for (int i = 0; i < 7; i++) out[i] = 0;
    return 0;
}

void flow_gfx_clear(void* handle, uint8_t r, uint8_t g, uint8_t b) {
    (void)handle;
    (void)r;
    (void)g;
    (void)b;
    flow_gfx_sdl_warn_once();
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
    flow_gfx_sdl_warn_once();
}

void flow_gfx_blit_rgb(void* handle, int32_t x, int32_t y, int32_t w, int32_t h,
                       const uint8_t* src) {
    (void)handle;
    (void)x;
    (void)y;
    (void)w;
    (void)h;
    (void)src;
    flow_gfx_sdl_warn_once();
}

/* No window, but the clock still has to advance monotonically so a program
 * that paces itself does not divide by zero or spin. */
double flow_gfx_time_ms(void* handle) {
    (void)handle;
    static double t = 0.0;
    t += 1000.0 / 60.0;
    return t;
}

void flow_gfx_wait_frame(void* handle, int32_t target_fps) {
    (void)handle;
    (void)target_fps;
}

void flow_gfx_present(void* handle) {
    (void)handle;
    flow_gfx_sdl_warn_once();
}

__attribute__((weak)) int32_t flow_gfx_frame(void* handle, int32_t frame) {
    (void)handle;
    (void)frame;
    return 0;
}

int32_t flow_gfx_run(void* handle, int32_t max_frames) {
    (void)handle;
    (void)max_frames;
    flow_gfx_sdl_warn_once();
    return 0;
}

#endif /* FLOW_GFX_USE_SDL2 */
