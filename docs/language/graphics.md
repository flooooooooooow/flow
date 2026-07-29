# Graphics in Flow

Honest status of the **native 2D window API** (`lib/stdlib/gfx.flow`) and related
GPU experiments. This page is not a promise of Metal/CUDA/OpenCL product parity.

## Platform matrix

| Platform | Backend file | Status | What you get today |
|----------|--------------|--------|--------------------|
| **macOS** | `runtime/gfx_macos.m` | ✅ Working | Cocoa window, software RGBA8 framebuffer, poll/keys, clear/fill_rect/present |
| **Linux** | `runtime/gfx_linux.c` | 🔲 Stub | Same C symbols as macOS; `flow_gfx_init` returns `NULL` and logs to stderr |
| **Windows** | — | 🔲 Missing | No `gfx_windows.c`; not started |

| Related path | Status | Notes |
|--------------|--------|-------|
| Metal (Apple GPU compute / audio helpers) | Partial | Separate from `gfx.flow` — see `runtime/audio_gpu_metal.m` and GPU examples; not a full shader pipeline product |
| Vulkan sample bridges | Experimental | `runtime/vulkan_flow_*_bridge.cpp` — demos, not the stdlib 2D API |
| CUDA / OpenCL “auto backend” | ❌ Not shipping | Older aspirational docs; do not rely on this |

Cross-platform graphics (Linux) remains a short-term roadmap item:
[ROADMAP.md](../../ROADMAP.md).

## What works (macOS)

Stdlib wrapper: `lib/stdlib/gfx.flow`. Typical link:

```bash
clang -O2 build/tetris_gfx.c runtime/gfx_macos.m \
  -framework Cocoa -framework CoreGraphics -framework QuartzCore -o tetris_gfx
```

```flow
# Sketch — see examples that use gfx.flow
let g = gfx_open(640, 480, "Demo")
while !gfx_should_close(g) {
    gfx_poll(g)
    gfx_clear(g, 20, 20, 30)
    gfx_fill_rect(g, 100, 100, 50, 50, 200, 80, 80)
    gfx_present(g)
}
gfx_close(g)
```

Pixel format: RGBA8. Key codes are macOS `NSEvent.keyCode` values (constants in
`gfx.flow`).

## Linux stub (current)

`runtime/gfx_linux.c` matches the **macOS C ABI** so Linux links do not fail on
missing symbols, but it does not open a window:

- `flow_gfx_init` → prints a clear stub message, returns `NULL`
- `flow_gfx_should_close` → always `1` (so loops exit instead of spinning)
- other entry points → no-ops after a one-shot stderr warning

See `runtime/README.md`.

## What’s needed next (Linux — small scope)

Not a Vulkan rewrite. Incremental path:

1. **SDL2 window + texture** presenting an RGBA8 buffer (same layout as macOS).
2. Implement every `flow_gfx_*` symbol with the **same signatures** as
   `gfx_macos.m` / `gfx.flow` (opaque `void*` ctx).
3. Map a small keycode set (document Linux vs macOS differences in `gfx.flow`).
4. Teach the package/build path to link `gfx_linux.c` (+ `-lSDL2`) on Linux
   instead of `gfx_macos.m`.

Optional later: Windows via SDL2 sharing most of the Linux code, or a thin
Win32 GDI/DIB path. GPU compute remains a separate track from this 2D API.

## GPU / Metal notes

- Prefer treating Metal and Vulkan as **optional native runtimes**, not as the
  default “graphics” story for demos and games.
- For games and tutorials, target `gfx.flow` + software fill until a real Linux
  backend lands.
- Do not assume automatic Metal/CUDA/OpenCL selection from Flow source.

## Related

- [runtime/README.md](../../runtime/README.md) — native backends map
- [Effects Showcase](../effects-showcase.md) — unrelated, but shows how Flow prefers
  explicit capabilities over hidden runtimes
- [docs/NEXT.md](../NEXT.md) — Priority 5 cross-platform graphics bullets
