/*
 * Linux graphics backend — thin driver over the shared SDL2 implementation.
 *
 * Same C ABI as runtime/gfx_macos.m / lib/stdlib/gfx.flow:
 *   flow_gfx_init / shutdown / poll / should_close / key_down /
 *   clear / fill_rect / present
 *
 * The actual SDL2 code (and no-SDL2 stub fallback) lives in
 * runtime/gfx_sdl_impl.inc, shared verbatim with runtime/gfx_windows.c so
 * the two platforms don't drift.
 *
 * Build (when SDL2 is installed):
 *   clang prog.c runtime/gfx_linux.c -lSDL2 -o prog
 *   # or via pkg-config: clang prog.c runtime/gfx_linux.c $(pkg-config --cflags --libs sdl2) -o prog
 *
 * Force the old no-window stub (e.g. headless CI without SDL2):
 *   clang -DFLOW_GFX_STUB prog.c runtime/gfx_linux.c -o prog
 *
 * Keycodes: Flow's gfx.flow uses macOS virtual keycodes (KEY_A=0, …).
 * This backend maps SDL scancodes → those same codes so demos stay portable.
 *
 * See docs/language/graphics.md and runtime/README.md.
 */

#define FLOW_GFX_BACKEND_NAME "Linux"
#include "gfx_sdl_impl.inc"
