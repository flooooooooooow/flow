# Flow runtime (native C / ObjC)

Platform glue linked with Flow programs that need audio, graphics, or sys info.

## Graphics (`flow_gfx_*`)

Contract is defined by `lib/stdlib/gfx.flow` and implemented for macOS in
`gfx_macos.m`:

| Symbol | Role |
|--------|------|
| `flow_gfx_init(w, h, title) -> void*` | Create window + RGBA8 buffer; returns opaque ctx |
| `flow_gfx_shutdown(ctx)` | Destroy window / free buffer |
| `flow_gfx_poll(ctx)` | Pump events |
| `flow_gfx_should_close(ctx) -> i32` | Nonzero when user closed window |
| `flow_gfx_key_down(ctx, keycode) -> i32` | Key state |
| `flow_gfx_clear` / `flow_gfx_fill_rect` / `flow_gfx_present` | Software 2D draw + present |

| File | Platform | Status |
|------|----------|--------|
| `gfx_macos.m` | macOS | **Working** — Cocoa window, software RGBA blit |
| `gfx_linux.c` | Linux | **SDL2** when `<SDL2/SDL.h>` is present; otherwise stub (`-DFLOW_GFX_STUB`) |
| `gfx_windows.c` | Windows | **SDL2 (partial)** — thin driver sharing `gfx_sdl_impl.inc` with Linux; compiles clean but not yet smoke-tested on real Windows (MSVC/clang) hardware/CI |

Both `gfx_linux.c` and `gfx_windows.c` are thin drivers that `#include`
`gfx_sdl_impl.inc`, which holds the actual SDL2 implementation (and its
no-SDL2 stub fallback) once so the two platforms can't drift apart.

Linux/Windows keycodes are mapped to the same macOS virtual codes used by
`lib/stdlib/gfx.flow` so demos stay portable. Vulkan demos under
`vulkan_flow_*_bridge.cpp` are a separate experimental path, not this 2D API.

See [docs/language/graphics.md](../docs/language/graphics.md).

## Other files (quick map)

| File | Purpose |
|------|---------|
| `gpu_memory.h` / `gpu_metal.m` / `gpu_memory_stub.c` | First-class GPU/unified buffers (`stdlib/gpu_memory.flow`); Metal on Darwin, stub elsewhere — linked by `./flow run` |
| `audio_*.c` / `audio_gpu_metal.m` | Audio I/O and Metal GPU audio helpers |
| `flow_time.c` / `flow_sys_info.c` | Time / host info |
| `live_host.c` / `live_plugin.c` | Live DSP host / plugin ABI |
| `flow_python_embed.c` | Python embed target |
| `vulkan_flow_*_bridge.cpp` | Experimental Vulkan sample bridges |

## Build tip (macOS graphics)

```bash
clang -O2 build/your_prog.c runtime/gfx_macos.m \
  -framework Cocoa -framework CoreGraphics -framework QuartzCore -o your_prog
```

```bash
# Linux (SDL2 installed — Debian: libsdl2-dev)
clang -O2 build/your_prog.c runtime/gfx_linux.c \
  $(pkg-config --cflags --libs sdl2) -o your_prog

# Headless / no SDL2 headers:
clang -O2 -DFLOW_GFX_STUB build/your_prog.c runtime/gfx_linux.c -o your_prog
```

```bash
# Windows (MSYS2/MinGW clang or gcc, SDL2 dev package installed)
clang -O2 build/your_prog.c runtime/gfx_windows.c \
  $(sdl2-config --cflags --libs) -o your_prog.exe

# Windows (MSVC / clang-cl)
clang-cl build/your_prog.c runtime\gfx_windows.c /I C:\SDL2\include ^
  /link /LIBPATH:C:\SDL2\lib SDL2.lib SDL2main.lib /out:your_prog.exe
# (copy SDL2.dll next to the exe, or put its folder on PATH, at runtime)

# Headless / no SDL2 headers:
clang -O2 -DFLOW_GFX_STUB build/your_prog.c runtime/gfx_windows.c -o your_prog.exe
```

`gfx_windows.c` shares its SDL2 implementation with `gfx_linux.c` via
`gfx_sdl_impl.inc` — it compiles clean (including the `-DFLOW_GFX_STUB` path)
but has not yet been smoke-tested against a real Windows toolchain/CI.
