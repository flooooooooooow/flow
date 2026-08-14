// Browser backend for the FLOW gfx API (Emscripten / WebAssembly).
//
// Fourth backend after the Cocoa window (runtime/gfx_macos.m), the SDL one
// (runtime/gfx_linux.c) and the headless PPM recorder (runtime/gfx_record.c).
// It exports exactly the same flow_gfx_* symbol table, so the same Flow source
// runs natively, records a GIF, or plays in a browser tab with no edits.
//
// Structure: keep an RGBA8 framebuffer exactly like the recorder does, and on
// flow_gfx_present copy it into a canvas with a single ImageData blit.
//
// The frame loop. Flow games are written as `while gfx_frame_pump(g) { ... }`
// with the loop inside main. A plain while-loop would never return control to
// the browser and the tab would freeze, so this backend is built with
// -sASYNCIFY and flow_gfx_present awaits one requestAnimationFrame before
// returning. The Flow program still reads as a straight loop; the browser gets
// its event loop back once per presented frame, which also gives vsync pacing
// for free.
//
// Keyboard. DOM key events are mapped to the same macOS NSEvent keycodes the
// games already use (lib/stdlib/gfx.flow: KEY_LEFT 123, KEY_SPACE 49, ...), so
// no game needs a browser-specific input path.
//
// Build (through ./flow wasm, which does this for you):
//   emcc prog.c runtime/gfx_wasm.c -sASYNCIFY -sINVOKE_RUN=0 \
//        -sEXPORTED_RUNTIME_METHODS=callMain -o prog.js
//
// Optional query-string / global knobs read on the JS side:
//   window.FLOW_GFX_CANVAS_ID   canvas element id      (default "canvas")

#include <emscripten.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

// ---------------------------------------------------------------------------
// JS side: canvas, keyboard, close flag.
// ---------------------------------------------------------------------------

EM_JS(void, flow_gfx_js_init, (int32_t w, int32_t h, const char *title), {
    var id = (typeof window !== "undefined" && window.FLOW_GFX_CANVAS_ID) || "canvas";
    var cv = (typeof document !== "undefined") ? document.getElementById(id) : null;
    if (!cv && typeof document !== "undefined") {
        cv = document.createElement("canvas");
        cv.id = id;
        document.body.appendChild(cv);
    }
    var state = {
        canvas: cv,
        ctx: cv ? cv.getContext("2d", { alpha: false }) : null,
        width: w,
        height: h,
        image: null,
        keys: new Uint8Array(256),
        // A key tapped between two polls would otherwise go down and up
        // without the program ever seeing it. Hold a press until it has
        // actually been read: `seen` records that flow_gfx_key_down returned
        // 1 for it, `release` defers the matching keyup until then, and `age`
        // caps the wait so a key the program never queries cannot stick.
        seen: new Uint8Array(256),
        release: new Uint8Array(256),
        age: new Uint8Array(256),
        closed: 0,
        frames: 0
    };
    if (cv) {
        // Set the backing store only; the host page's CSS decides how big it
        // is drawn, so a large program still fits inside a small frame.
        cv.width = w;
        cv.height = h;
        cv.setAttribute("tabindex", "0");
        try { cv.focus(); } catch (e) {}
    }
    if (state.ctx) {
        state.ctx.imageSmoothingEnabled = false;
        state.image = state.ctx.createImageData(w, h);
    }

    // macOS NSEvent virtual keycodes. The games hardcode these constants, so
    // the browser has to speak the same numbers.
    var MAC = {
        KeyA: 0, KeyS: 1, KeyD: 2, KeyF: 3, KeyH: 4, KeyG: 5, KeyZ: 6, KeyX: 7,
        KeyC: 8, KeyV: 9, KeyB: 11, KeyQ: 12, KeyW: 13, KeyE: 14, KeyR: 15,
        KeyY: 16, KeyT: 17, Digit1: 18, Digit2: 19, Digit3: 20, Digit4: 21,
        Digit6: 22, Digit5: 23, Equal: 24, Digit9: 25, Digit7: 26, Minus: 27,
        Digit8: 28, Digit0: 29, BracketRight: 30, KeyO: 31, KeyU: 32,
        BracketLeft: 33, KeyI: 34, KeyP: 35, Enter: 36, KeyL: 37, KeyJ: 38,
        Quote: 39, KeyK: 40, Semicolon: 41, Backslash: 42, Comma: 43,
        Slash: 44, KeyN: 45, KeyM: 46, Period: 47, Tab: 48, Space: 49,
        Backquote: 50, Backspace: 51, Escape: 53,
        ArrowLeft: 123, ArrowRight: 124, ArrowDown: 125, ArrowUp: 126
    };
    // Keys the page must not hand to the browser while a game has focus.
    var SWALLOW = {
        ArrowLeft: 1, ArrowRight: 1, ArrowUp: 1, ArrowDown: 1, Space: 1,
        Tab: 1, Enter: 1, Slash: 1, Quote: 1
    };

    var target = (typeof window !== "undefined") ? window : null;
    if (target) {
        state.onDown = function (ev) {
            var code = MAC[ev.code];
            if (code !== undefined) {
                state.keys[code] = 1;
                state.seen[code] = 0;
                state.release[code] = 0;
                state.age[code] = 0;
            }
            if (SWALLOW[ev.code]) { ev.preventDefault(); }
        };
        state.onUp = function (ev) {
            var code = MAC[ev.code];
            if (code !== undefined) {
                if (state.keys[code] && !state.seen[code]) {
                    state.release[code] = 1; // held until the program reads it
                } else {
                    state.keys[code] = 0;
                }
            }
            if (SWALLOW[ev.code]) { ev.preventDefault(); }
        };
        state.onBlur = function () {
            state.keys.fill(0);
            state.seen.fill(0);
            state.release.fill(0);
            state.age.fill(0);
        };
        target.addEventListener("keydown", state.onDown, { passive: false });
        target.addEventListener("keyup", state.onUp, { passive: false });
        target.addEventListener("blur", state.onBlur);
    }

    // Touch / on-screen buttons: elements carrying data-flow-key="123".
    if (typeof document !== "undefined") {
        var pads = document.querySelectorAll("[data-flow-key]");
        for (var i = 0; i < pads.length; i++) {
            (function (el) {
                var kc = parseInt(el.getAttribute("data-flow-key"), 10);
                var press = function (ev) { ev.preventDefault(); state.keys[kc] = 1; };
                var release = function (ev) { ev.preventDefault(); state.keys[kc] = 0; };
                el.addEventListener("pointerdown", press);
                el.addEventListener("pointerup", release);
                el.addEventListener("pointerleave", release);
                el.addEventListener("pointercancel", release);
            })(pads[i]);
        }
    }

    if (typeof window !== "undefined") {
        window.flowGfx = state;
        // Host page hook: flowGfxStop() ends the program's loop cleanly.
        window.flowGfxStop = function () { state.closed = 1; };
        if (typeof window.flowGfxOnStart === "function") {
            window.flowGfxOnStart(UTF8ToString(title), w, h);
        }
    }
});

EM_JS(void, flow_gfx_js_blit, (int32_t w, int32_t h, uint8_t *pixels), {
    var state = (typeof window !== "undefined") ? window.flowGfx : null;
    if (!state || !state.ctx || !state.image) { return; }
    state.image.data.set(HEAPU8.subarray(pixels, pixels + w * h * 4));
    state.ctx.putImageData(state.image, 0, 0);
    state.frames++;
    // Retire taps whose keyup was deferred, once the program has read them
    // (or after a few frames, if it never asks about that key at all).
    for (var i = 0; i < 256; i++) {
        if (!state.release[i]) { continue; }
        state.age[i]++;
        if (state.seen[i] || state.age[i] > 4) {
            state.keys[i] = 0;
            state.release[i] = 0;
            state.age[i] = 0;
        }
    }
});

// Hand the event loop back to the browser between frames, paced to 60 Hz.
// Requires -sASYNCIFY.
//
// Two wakers, because neither alone is enough. requestAnimationFrame is the
// right clock for a visible tab, but it stops entirely when the tab is hidden
// and runs at 120 Hz on a ProMotion display; timers get clamped to roughly one
// a second in the background. So: wake on whichever is available, check the
// wall clock, and go round again until this frame's slot is due.
EM_ASYNC_JS(void, flow_gfx_js_yield, (void), {
    var state = (typeof window !== "undefined") ? window.flowGfx : null;
    var period = 1000 / 60;
    var now = performance.now();
    var due = Math.max(now + 1, (state && state.nextFrame) || 0);
    if (state) { state.nextFrame = due + period; }

    await new Promise(function (resolve) {
        var chan = null;
        var tick = function () {
            if (performance.now() >= due) { resolve(); return; }
            if (typeof document !== "undefined" && !document.hidden) {
                requestAnimationFrame(tick);
                return;
            }
            if (!chan) {
                chan = (state && state.chan) || new MessageChannel();
                if (state) { state.chan = chan; }
                chan.port1.onmessage = tick;
            }
            chan.port2.postMessage(0);
        };
        tick();
    });
});

EM_JS(int32_t, flow_gfx_js_key, (int32_t keycode), {
    var state = (typeof window !== "undefined") ? window.flowGfx : null;
    if (!state || keycode < 0 || keycode > 255) { return 0; }
    if (!state.keys[keycode]) { return 0; }
    state.seen[keycode] = 1;
    return 1;
});

EM_JS(int32_t, flow_gfx_js_closed, (void), {
    var state = (typeof window !== "undefined") ? window.flowGfx : null;
    return (state && state.closed) ? 1 : 0;
});

EM_JS(void, flow_gfx_js_shutdown, (int32_t presented), {
    var state = (typeof window !== "undefined") ? window.flowGfx : null;
    if (!state) { return; }
    state.closed = 1;
    if (state.onDown) {
        window.removeEventListener("keydown", state.onDown);
        window.removeEventListener("keyup", state.onUp);
        window.removeEventListener("blur", state.onBlur);
    }
    if (typeof window.flowGfxOnExit === "function") {
        window.flowGfxOnExit(presented);
    }
});

// ---------------------------------------------------------------------------
// C side: the flow_gfx_* ABI, same shape as the other three backends.
// ---------------------------------------------------------------------------

typedef struct {
    int32_t width;
    int32_t height;
    uint8_t *pixels; // width*height*4, RGBA8
    int32_t presented;
    bool should_close;
} FlowGfxWasm;

void *flow_gfx_init(int32_t w, int32_t h, const char *title_utf8) {
    if (w <= 0 || h <= 0) return NULL;
    FlowGfxWasm *g = (FlowGfxWasm *)calloc(1, sizeof(FlowGfxWasm));
    if (!g) return NULL;

    g->width = w;
    g->height = h;
    g->pixels = (uint8_t *)calloc((size_t)w * (size_t)h * 4u, 1);
    if (!g->pixels) {
        free(g);
        return NULL;
    }
    flow_gfx_js_init(w, h, title_utf8 ? title_utf8 : "flow");
    return g;
}

void flow_gfx_shutdown(void *handle) {
    FlowGfxWasm *g = (FlowGfxWasm *)handle;
    if (!g) return;
    flow_gfx_js_shutdown(g->presented);
    free(g->pixels);
    free(g);
}

EM_JS(double, flow_gfx_js_now, (void), {
    return performance.now();
});

/* Pointer state into out[0..6]: x, y, left, right, middle, wheel, inside.
 *
 * The canvas backing store and its CSS display size are set independently
 * (see flow_gfx_js_init), so clientX/clientY are in CSS pixels and must be
 * scaled by width/rect.width to land in framebuffer coordinates. Using the
 * raw event coordinates would drift as soon as the page scales the canvas.
 *
 * Pointer events rather than mouse events, so a touchscreen works too. */
EM_JS(int32_t, flow_gfx_js_mouse, (int32_t *out), {
    var st = (typeof window !== "undefined") ? window.flowGfx : null;
    if (!st || !st.canvas) return 0;
    if (!st.mouse) {
        st.mouse = { x: 0, y: 0, l: 0, r: 0, m: 0, wheel: 0, inside: 0 };
        var cv = st.canvas;
        var toBuf = function (ev) {
            var rect = cv.getBoundingClientRect();
            if (rect.width <= 0 || rect.height <= 0) return;
            st.mouse.x = Math.floor((ev.clientX - rect.left) * (cv.width / rect.width));
            st.mouse.y = Math.floor((ev.clientY - rect.top) * (cv.height / rect.height));
            st.mouse.inside = (st.mouse.x >= 0 && st.mouse.x < cv.width &&
                               st.mouse.y >= 0 && st.mouse.y < cv.height) ? 1 : 0;
        };
        cv.addEventListener("pointermove", toBuf);
        cv.addEventListener("pointerdown", function (ev) {
            toBuf(ev);
            if (ev.button === 0) st.mouse.l = 1;
            else if (ev.button === 2) st.mouse.r = 1;
            else if (ev.button === 1) st.mouse.m = 1;
            try { cv.setPointerCapture(ev.pointerId); } catch (e) {}
        });
        cv.addEventListener("pointerup", function (ev) {
            toBuf(ev);
            if (ev.button === 0) st.mouse.l = 0;
            else if (ev.button === 2) st.mouse.r = 0;
            else if (ev.button === 1) st.mouse.m = 0;
        });
        cv.addEventListener("pointerleave", function () { st.mouse.inside = 0; });
        cv.addEventListener("pointerenter", function () { st.mouse.inside = 1; });
        /* Without preventDefault the page scrolls out from under the demo. */
        cv.addEventListener("wheel", function (ev) {
            st.mouse.wheel += (ev.deltaY > 0) ? 1 : ((ev.deltaY < 0) ? -1 : 0);
            ev.preventDefault();
        }, { passive: false });
        /* Right-drag is a demo control, not a context menu. */
        cv.addEventListener("contextmenu", function (ev) { ev.preventDefault(); });
    }
    var m = st.mouse;
    HEAP32[(out >> 2) + 0] = m.x;
    HEAP32[(out >> 2) + 1] = m.y;
    HEAP32[(out >> 2) + 2] = m.l;
    HEAP32[(out >> 2) + 3] = m.r;
    HEAP32[(out >> 2) + 4] = m.m;
    HEAP32[(out >> 2) + 5] = m.wheel;
    HEAP32[(out >> 2) + 6] = m.inside;
    return 1;
});

int32_t flow_gfx_mouse(void *handle, int32_t *out) {
    (void)handle;
    if (!out) return 0;
    return flow_gfx_js_mouse(out);
}

/* Milliseconds since the first call. */
double flow_gfx_time_ms(void *handle) {
    (void)handle;
    static double origin = -1.0;
    double now = flow_gfx_js_now();
    if (origin < 0.0) origin = now;
    return now - origin;
}

/* Deliberately a no-op. flow_gfx_present already awaits one
 * requestAnimationFrame (see flow_gfx_js_yield), so the browser paces this
 * backend to the display refresh. Sleeping here on top of that would halve
 * the frame rate. */
void flow_gfx_wait_frame(void *handle, int32_t target_fps) {
    (void)handle;
    (void)target_fps;
}

int32_t flow_gfx_should_close(void *handle) {
    FlowGfxWasm *g = (FlowGfxWasm *)handle;
    if (!g) return 1;
    if (flow_gfx_js_closed()) g->should_close = true;
    return g->should_close ? 1 : 0;
}

void flow_gfx_poll(void *handle) {
    FlowGfxWasm *g = (FlowGfxWasm *)handle;
    if (!g) return;
    // DOM events are delivered while flow_gfx_present yields, so there is
    // nothing to drain here. Refresh the close flag so a program that polls
    // without presenting still notices the stop button.
    if (flow_gfx_js_closed()) g->should_close = true;
}

int32_t flow_gfx_key_down(void *handle, int32_t keycode) {
    if (!handle) return 0;
    return flow_gfx_js_key(keycode);
}

void flow_gfx_clear(void *handle, uint8_t r, uint8_t g_, uint8_t b) {
    FlowGfxWasm *g = (FlowGfxWasm *)handle;
    if (!g || !g->pixels) return;
    size_t n = (size_t)g->width * (size_t)g->height;
    uint8_t *p = g->pixels;
    for (size_t i = 0; i < n; i++) {
        p[i * 4 + 0] = r;
        p[i * 4 + 1] = g_;
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
    FlowGfxWasm *ctx = (FlowGfxWasm *)handle;
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
                        uint8_t r, uint8_t g_, uint8_t b) {
    FlowGfxWasm *g = (FlowGfxWasm *)handle;
    if (!g || !g->pixels) return;
    if (w <= 0 || h <= 0) return;

    int32_t x0 = x < 0 ? 0 : x;
    int32_t y0 = y < 0 ? 0 : y;
    int32_t x1 = x + w; if (x1 > g->width) x1 = g->width;
    int32_t y1 = y + h; if (y1 > g->height) y1 = g->height;
    if (x0 >= x1 || y0 >= y1) return;

    uint8_t *p = g->pixels;
    for (int32_t yy = y0; yy < y1; yy++) {
        for (int32_t xx = x0; xx < x1; xx++) {
            size_t idx = ((size_t)yy * (size_t)g->width + (size_t)xx) * 4u;
            p[idx + 0] = r;
            p[idx + 1] = g_;
            p[idx + 2] = b;
            p[idx + 3] = 255;
        }
    }
}

void flow_gfx_present(void *handle) {
    FlowGfxWasm *g = (FlowGfxWasm *)handle;
    if (!g || !g->pixels) return;
    flow_gfx_js_blit(g->width, g->height, g->pixels);
    g->presented++;
    flow_gfx_js_yield(); // one requestAnimationFrame; the tab stays alive
    if (flow_gfx_js_closed()) g->should_close = true;
}

// Mirrors the weak default in the other backends.
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
        if (flow_gfx_key_down(handle, 53)) return frame; // Esc
        if (!flow_gfx_frame(handle, frame)) return frame;
    }
    return max_frames;
}
