/*
 * Windows graphics backend — thin driver over the shared SDL2 implementation.
 *
 * Same C ABI as runtime/gfx_macos.m / runtime/gfx_linux.c / lib/stdlib/gfx.flow:
 *   flow_gfx_init / shutdown / poll / should_close / key_down /
 *   clear / fill_rect / present
 *
 * The actual SDL2 code (and no-SDL2 stub fallback) lives in
 * runtime/gfx_sdl_impl.inc, shared verbatim with runtime/gfx_linux.c so the
 * two platforms don't drift.
 *
 * Build (MSYS2/MinGW clang or gcc, SDL2 dev package installed):
 *   clang prog.c runtime/gfx_windows.c $(sdl2-config --cflags --libs) -o prog.exe
 *   # or without sdl2-config, pointing at an extracted SDL2-devel-mingw dir:
 *   clang prog.c runtime/gfx_windows.c -IC:/SDL2/include -LC:/SDL2/lib -lSDL2 -lSDL2main -o prog.exe
 *
 * Build (MSVC / clang-cl, SDL2 development libraries unpacked locally):
 *   clang-cl prog.c runtime\gfx_windows.c /I C:\SDL2\include ^
 *     /link /LIBPATH:C:\SDL2\lib SDL2.lib SDL2main.lib /out:prog.exe
 *   (copy SDL2.dll next to prog.exe, or put its folder on PATH, at runtime)
 *
 * Force the no-window stub (e.g. headless CI without SDL2):
 *   clang -DFLOW_GFX_STUB prog.c runtime/gfx_windows.c -o prog.exe
 *
 * STATUS: this is a practical slice, not a fully verified Windows backend.
 * The SDL2 code path is identical to the Linux backend (same shared .inc)
 * and compiles clean under `-DFLOW_GFX_STUB` on macOS CI, but it has NOT yet
 * been smoke-tested against a real MSVC/clang toolchain + SDL2 on Windows.
 * See ROADMAP.md and docs/language/graphics.md; please report build issues.
 *
 * Keycodes: Flow's gfx.flow uses macOS virtual keycodes (KEY_A=0, …).
 * This backend maps SDL scancodes → those same codes so demos stay portable.
 */

#define FLOW_GFX_BACKEND_NAME "Windows"
#include "gfx_sdl_impl.inc"
