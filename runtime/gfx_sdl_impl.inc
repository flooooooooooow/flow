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
} FlowGfxContext;

/* Map SDL scancode → macOS-style virtual keycode used by lib/stdlib/gfx.flow */
static int flow_gfx_map_scancode(SDL_Scancode sc) {
    switch (sc) {
        case SDL_SCANCODE_A: return 0;
        case SDL_SCANCODE_S: return 1;
        case SDL_SCANCODE_D: return 2;
        case SDL_SCANCODE_W: return 13;
        case SDL_SCANCODE_R: return 15;
        case SDL_SCANCODE_ESCAPE: return 53;
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

void flow_gfx_present(void* handle) {
    FlowGfxContext* ctx = (FlowGfxContext*)handle;
    if (!ctx || !ctx->texture || !ctx->renderer || !ctx->pixels) return;
    SDL_UpdateTexture(ctx->texture, NULL, ctx->pixels, ctx->width * 4);
    SDL_RenderClear(ctx->renderer);
    SDL_RenderCopy(ctx->renderer, ctx->texture, NULL, NULL);
    SDL_RenderPresent(ctx->renderer);
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

void flow_gfx_present(void* handle) {
    (void)handle;
    flow_gfx_sdl_warn_once();
}

#endif /* FLOW_GFX_USE_SDL2 */
