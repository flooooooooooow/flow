# Graphics in Flow

Honest status of the **native 2D window API** (`lib/stdlib/gfx.flow`) and related
GPU experiments. This page is not a promise of Metal/CUDA/OpenCL product parity.

## Platform matrix

| Platform | Backend file | Status | What you get today |
|----------|--------------|--------|--------------------|
| **macOS** | `runtime/gfx_macos.m` | ✅ Working | Cocoa window, software RGBA8 framebuffer, poll/keys, clear/fill_rect/present |
| **Linux** | `runtime/gfx_linux.c` | ✅ SDL2 (stub fallback) | Real window + RGBA texture when SDL2 headers present; `-DFLOW_GFX_STUB` keeps the old null-init stub |
| **Windows** | `runtime/gfx_windows.c` | ✅ partial: SDL2 shared with Linux; stub CI on Windows | Same SDL2 path as Linux (`gfx_sdl_impl.inc`); `FLOW_GFX_STUB` smoke on `windows-latest` CI; full SDL2 window path still needs a real Windows + SDL2 run |

| Related path | Status | Notes |
|--------------|--------|-------|
| Metal (Apple GPU compute / audio helpers) | Partial | Separate from `gfx.flow`; see `runtime/audio_gpu_metal.m` and GPU examples. Not a full shader pipeline product |
| Vulkan sample bridges | Experimental | `runtime/vulkan_flow_*_bridge.cpp`: demos, not the stdlib 2D API |
| CUDA / OpenCL “auto backend” | ❌ Not shipping | Older aspirational docs; do not rely on this |

Cross-platform graphics (Linux ✅, Windows ✅ partial) is tracked in
[ROADMAP.md](../../ROADMAP.md).

## What works (macOS)

Stdlib wrapper: `lib/stdlib/gfx.flow`. Typical link:

```bash
clang -O2 build/tetris_gfx.c runtime/gfx_macos.m \
  -framework Cocoa -framework CoreGraphics -framework QuartzCore -o tetris_gfx
```

```flow
# Sketch: see examples that use gfx.flow
let g = gfx_open(640, 480, "Demo")
let mut frame: i32 = 0
while frame < 1000 {
    if !gfx_frame_pump(g) { break }   # poll + Esc/close
    gfx_clear(g, 20, 20, 30)
    gfx_fill_rect(g, 100, 100, 50, 50, 200, 80, 80)
    gfx_present(g)
    frame = frame + 1
}
gfx_close(g)
```

For a C-driven loop that calls a user `flow_gfx_frame(ctx, frame) -> i32`
callback each tick, use `gfx_run(g, max_frames)` (runtime `flow_gfx_run`).

Pixel format: RGBA8. Key codes are macOS `NSEvent.keyCode` values (constants in
`gfx.flow`).

## Linux / Windows stub fallback

Without SDL2 headers (or with `-DFLOW_GFX_STUB`), `gfx_linux.c` / `gfx_windows.c`
keep the old ABI-compatible stub: `flow_gfx_init` returns `NULL`,
`should_close` is always `1`. See `runtime/README.md`.

## Linux build

```bash
# Prefer pkg-config when available
clang -O2 build/tetris_gfx.c runtime/gfx_linux.c \
  $(pkg-config --cflags --libs sdl2) -o tetris_gfx

# Or via the Flow CLI gfx runner (selects macOS vs Linux vs Windows backend):
./flow gfx examples/games/tetris_gfx.flow
```

`./flow`’s native gfx path links `gfx_linux.c` + SDL2 on Linux hosts.
Keycodes are mapped to the macOS virtual codes in `gfx.flow` (A/S/D/W/R/arrows/Esc).

## Windows build

`gfx_windows.c` is a thin driver that shares its entire SDL2 implementation
with Linux via `runtime/gfx_sdl_impl.inc`. Same buffer layout, same keycode
map, same ABI. CI compiles and runs the stub path on `windows-latest`
(`runtime/tests/gfx_stub_smoke.c` + `-DFLOW_GFX_STUB`). A full SDL2 window
smoke on Windows agents is still outstanding.

```bash
# MSYS2 / MinGW / Git Bash (clang or gcc), SDL2 dev package installed
clang -O2 build/tetris_gfx.c runtime/gfx_windows.c \
  $(sdl2-config --cflags --libs) -o tetris_gfx.exe

# MSVC / clang-cl, SDL2 development libraries unpacked locally
clang-cl build/tetris_gfx.c runtime\gfx_windows.c /I C:\SDL2\include ^
  /link /LIBPATH:C:\SDL2\lib SDL2.lib SDL2main.lib /out:tetris_gfx.exe
# copy SDL2.dll next to the exe (or add its folder to PATH) at runtime

# Or via the Flow CLI gfx runner, from an MSYS2/Git Bash/Cygwin shell
# (detected via `uname -s`; picks gfx_windows.c + sdl2-config/pkg-config):
./flow gfx examples/games/tetris_gfx.flow
```

Still open: real Windows CI/hardware smoke test, richer key map, xvfb-style
headless smoke for Linux CI.

## What’s done / left (Linux + Windows)

- [x] SDL2 window + streaming RGBA32 texture (same buffer layout as macOS)
- [x] Full `flow_gfx_*` ABI parity
- [x] Small keycode map → macOS codes
- [x] `./flow` gfx link path picks `gfx_linux.c` / `gfx_windows.c` + SDL2 by host
- [x] SDL2 implementation shared between Linux and Windows (`gfx_sdl_impl.inc`)
- [ ] Real Windows (MSVC/clang) hardware or CI smoke test
- [ ] xvfb-style headless CI smoke for Linux

## GPU / Metal notes

- Prefer treating Metal and Vulkan as **optional native runtimes**, not as the
  default “graphics” story for demos and games.
- For games and tutorials, target `gfx.flow` + software fill (macOS Cocoa;
  Linux/Windows via SDL2 when headers are present, stub otherwise).
- Do not assume automatic Metal/CUDA/OpenCL selection from Flow source.

## Related

- [runtime/README.md](../../runtime/README.md): native backends map
- [Effects Showcase](../effects-showcase.md): unrelated, but shows how Flow prefers
  explicit capabilities over hidden runtimes
- [docs/NEXT.md](../NEXT.md): Priority 5 cross-platform graphics bullets
