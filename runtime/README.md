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
| `gfx_linux.c` | Linux | **Stub** — same symbols, logs to stderr, `init` returns NULL |
| *(none)* | Windows | **Missing** — no `gfx_windows.c` yet |

Do **not** invent a different ABI on Linux. Implement SDL2 (recommended) or X11
against the table above. Vulkan demos under `vulkan_flow_*_bridge.cpp` are a
separate experimental path, not this 2D API.

See [docs/language/graphics.md](../docs/language/graphics.md).

## Other files (quick map)

| File | Purpose |
|------|---------|
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

On Linux, until the stub is replaced, link `runtime/gfx_linux.c` only to satisfy
symbols — expect stderr messages and a null ctx from `gfx_open`.
