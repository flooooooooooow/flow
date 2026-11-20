# Resident GPU host (gpu_live)

Status: first release, extended on request of the driving simulator (see
"Answers to the consumer requests").

`lib/stdlib/gpu_live.flow` gives a Flow program a Metal device that stays open
for the life of the process. A game creates buffers, textures and pipelines
once, then every frame binds them, dispatches compute kernels, runs render
passes and presents in its gfx window. Nothing is launched and nothing is read
back.

## What was wrong with the old path

Render jobs (`docs/library/gpu-render.md`) were built to check frames against
references. One job costs three things, which rules out a frame loop.

1. A process launch. `gpu_backend_render` in `lib/stdlib/gpu_render_host.flow`
   runs `proc_run(c)` on the Metal host binary for every job. The host,
   `runtime/gpu_render_metal.m` (`render_job`), calls `MTLCreateSystemDefaultDevice`
   and `newCommandQueue` on each launch, so the device, the queue and every
   shader compile start from nothing. `gpu_metal_host` also rebuilds that
   binary with `xcrun clang` once per Flow process (about a second).
2. A file round trip in. `gpu_job_write` stores the frame as a directory.
   `gpu_blob` calls `io_write_bytes` for `job.txt`, every `.metal` and `.wgsl`
   stage, and every buffer and texture. The host parses `job.txt` back with
   `stringWithContentsOfFile`, and compiles the Metal source with
   `newLibraryWithSource` on every run (`gpu_render_metal.m`, `render_job`).
3. A file round trip out. After `[cmd waitUntilCompleted]` the host copies the
   texture to the CPU and `fwrite`s it to `OUT.rgba`. The caller reads it with
   `gpu_frame_read` (`io_read_file`). The frame is never shown. The CPU holds it.

The other Metal files do not cover a frame loop either.
`runtime/gpu_metal_graph.m` does hold a persistent device and command queue
(`flow_gpu_graph_exec_new` creates them once and `FgExec` keeps them), but it
runs compute graphs only: at most 16 resources and 16 passes, no render
pipelines, no window, and a `waitUntilCompleted` after each run
(`fg_finish`). `runtime/gpu_metal.m` keeps a global device and queue for a fixed
set of kernels (`mul`, `relu`, `gemm`) and waits after every call.
`runtime/audio_gpu_metal.m` is audio only. None of them can present.

`gfx_macos.m` presents a CPU framebuffer: `flow_gfx_present` marks the view dirty
and `drawRect:` wraps `ctx->pixels` in a CGImage and draws it. A GPU frame had no
way to reach the window except through the CPU.

## Design

`runtime/gpu_metal_host.m`, with the C ABI in `runtime/gpu_metal_host.h`.

- One `MTLDevice`, one `MTLCommandQueue`, one library cache. The cache key is
  the FNV-1a hash of the Metal source, checked against the stored source. A
  second request for the same source and entry compiles nothing.
- Handles are 32-bit integers: 20 bits of slot index and 10 bits of
  generation. A freed handle stays invalid even when its slot is reused.
- Apple silicon only. Buffers and textures use shared storage, so the CPU writes
  the bytes the GPU reads. A device without unified memory makes `gl_init`
  report unavailable, and the program uses the CPU path.
- Up to three frames are in flight. `gl_begin_frame` waits on a semaphore only
  when the GPU is three frames behind. The command buffer completion handler
  signals it and records the GPU time.
- A stream resource (`GL_BUF_STREAM`, `GL_TEX_STREAM`) keeps one copy per frame
  slot. Writes go to the copy for the current frame and binds read that copy,
  so the CPU never overwrites bytes the GPU is still reading.
- `gl_bind_bytes` copies small per-frame constants into a ring of uniform
  memory, one region per frame slot, and binds the range, with no allocation.
- Direct presentation: `gl_attach_window` installs a `CAMetalLayer` as the
  layer of the gfx view. The layer's drawable size is the view's size in device
  pixels, so a hidpi window gets one drawable pixel per screen pixel. Vsync is
  `displaySyncEnabled`. `gl_pass_begin(GL_WINDOW, ...)` and `gl_blit(src,
  GL_WINDOW, ...)` draw into the drawable, and `gl_present` presents it.
- CPU overlay: draw the HUD into an RGBA buffer, `gl_texture_upload_rect` the
  changed rectangle into a `GL_TEX_STREAM` texture, then `gl_blit(overlay,
  GL_WINDOW, GL_BLEND_PREMUL)` after the GPU scene.
- Timing: `gl_gpu_time_ms` is `GPUEndTime - GPUStartTime` of the last completed
  command buffer. `gl_pass_time_ms` uses counter sample buffers when the device
  supports them (`gl_stat(GL_STAT_PASS_TIMING)` is 1).

## Interface

All of it is in `lib/stdlib/gpu_live.flow`. Handles are `i32`. A function that
makes a resource returns a handle >= 1 or -1. Other functions return 0 or -1.
`gl_last_error()` describes the last failure. Nothing aborts.

```text
gl_init(flags) -> bool            gl_available() -> bool          gl_shutdown()
gl_last_error() -> string         gl_device_name() -> string      gl_stat(which) -> i64
gl_force_off(bool)                gl_attach_window(ctx: ptr<void>, vsync) -> i32
gl_detach_window()                gl_window() -> GlWindow{width,height,scale,attached}
gl_set_vsync(bool)

gl_buffer_new(bytes: i64, flags) -> i32       gl_buffer_free(buf)
gl_buffer_write(buf, offset: i64, src: ptr<u8>, n: i64) -> i32
gl_buffer_ptr(buf) -> ptr<u8>                 gl_buffer_read(buf, offset, dst, n) -> i32   (slow)
gl_buffer_wrap(ptr: ptr<u8>, bytes: i64) -> i32
gl_texture_new(w, h, format, usage) -> i32    gl_texture_free(tex)
gl_texture_upload(tex, src, bytes_per_row)    gl_texture_upload_rect(tex, x, y, w, h, src, bytes_per_row)
gl_texture_read(tex, dst, bytes_per_row)      (slow)

gl_compute_pipeline(msl, entry) -> i32
gl_render_pipeline(msl, vs, fs, color_format, depth_format, blend) -> i32
gl_render_pipeline_begin(...) then gl_pipeline_vertex_layout(p, slot, stride, per_instance),
  gl_pipeline_vertex_attr(p, location, slot, format, offset), gl_pipeline_state(p, cull, depth),
  gl_render_pipeline_build(p)
gl_pipeline_free(p)

gl_begin_frame() -> i32
gl_bind_buffer(slot, buf, offset)   gl_bind_texture(slot, tex)   gl_bind_sampler(slot, linear, repeat)
gl_bind_bytes(slot, src, n)
gl_dispatch(pipe, x, y, z)          gl_dispatch_groups(pipe, gx, gy, gz, tx, ty, tz)
gl_dispatch_indirect(pipe, args_buf, offset, tx, ty, tz)
gl_pass_begin(color, depth, load, r, g, b, a, clear_depth)
gl_draw(pipe, topology, first, count, instances)
gl_draw_indexed(pipe, topology, index_buf, index_u32, first_index, count, instances)
gl_draw_indirect(pipe, topology, args_buf, offset)
gl_pass_begin_noattach(w, h)    gl_pass_name(name)    gl_pass_label(i) -> string
gl_pass_end()
gl_overlay_begin(ctx: ptr<void>)   gl_overlay_present(x, y, w, h)   gl_overlay_target(dst)
gl_blit(src, dst, blend)
gl_present()    gl_submit()    gl_wait_idle()
gl_gpu_time_ms() -> f64   gl_pass_count() -> i32   gl_pass_time_ms(i) -> f64
```

Shaders are Metal Shading Language strings. The string that `gx_emit_metal` in
`gpu_shader.flow` returns works unchanged. It uses entry points `vs_main` and
`fs_main`, uniforms as `struct U` in `buffer(0)`, vertex buffer slot k at
`buffer(16 + k)`, and texture slot s at `texture(s)` and `sampler(s)`. Hand
written MSL may use any entry names and any buffer indices.

## Threading

- `gl_init` takes flags: the low two bits set the frames in flight (0 means 3).
- `gl_init`, `gl_attach_window`, `gl_detach_window`, `gl_set_vsync` and
  `gl_shutdown`: the thread that owns the window (the main thread in a gfx
  program).
- The frame calls (`gl_begin_frame` through `gl_present`, `gl_submit`, every
  `gl_bind_*`, `gl_dispatch*`, `gl_pass_*`, `gl_draw*`, `gl_blit`): one thread at
  a time. Normally the main thread. The host keeps one open command buffer and
  does not lock it.
- Resource calls (`gl_buffer_*`, `gl_texture_*`, `gl_*_pipeline*`, `gl_stat`,
  `gl_gpu_time_ms`, `gl_last_error`): any thread, concurrently. A mutex guards
  the handle tables. Two threads must not write the same buffer or texture at
  the same time.
- Stream resources (`GL_BUF_STREAM`, `GL_TEX_STREAM`) have one copy per frame
  slot. They can be written only while a frame is open, so the main thread calls
  `gl_begin_frame`, then `gl_buffer_ptr(stream_buf)`, and hands that pointer to
  worker threads. Workers write straight into it at disjoint offsets with no
  host call, and the main thread joins them before `gl_present`. A stream
  resource call made with no frame open returns -1 and never blocks.
- A worker thread that runs the CPU rasteriser writes into its own memory. The
  main thread uploads it with `gl_texture_upload_rect` or `gl_overlay_present`.
- `gl_last_error` is kept per thread.

## Answers to the consumer requests

1. No-attachment passes: yes. `gl_pass_begin_noattach(w, h)` sets
   `renderTargetWidth` and `renderTargetHeight` and a raster sample count of 1.
   Build the pipeline with `gl_render_pipeline(msl, vs, fs, GL_FORMAT_NONE,
   GL_FORMAT_NONE, GL_BLEND_NONE)`. Draws in that pass check that the pipeline
   has no colour and no depth format. Fragment functions may write device
   buffers with `[[raster_order_group(0)]]`; the host does not touch the MSL.
2. One slot number, one resource, in every stage: yes. `gl_bind_buffer(slot, ...)`
   binds the index in the vertex stage, the fragment stage and the compute stage
   alike, and so do `gl_bind_texture`, `gl_bind_sampler` and `gl_bind_bytes`.
   Vertex buffers use slots from `GL_VERTEX_SLOT_BASE` (16). Slots 0 to 30 exist.
3. Stable pointers: a plain buffer (flags 0) has one allocation for its whole
   life, so `gl_buffer_ptr` returns the same address every frame. A stream buffer
   has one allocation per frame slot, and its pointer changes with the frame slot.
   Writers on several threads are fine at disjoint offsets, per the threading rules.
4. `gl_buffer_wrap(ptr, bytes)`: yes, `newBufferWithBytesNoCopy`. Both the pointer
   and the size must be multiples of the page size (16384 bytes on Apple
   silicon). The caller owns the memory and must keep it until after
   `gl_buffer_free` and `gl_wait_idle`.
5. Compute writes to textures: `GL_USE_SHADER_WRITE` (the same flag as
   `GL_TEX_STORAGE`) with `GL_RGBA8` or `GL_BGRA8`. `gl_blit` accepts a source
   with either `GL_TEX_SAMPLED` or `GL_TEX_STORAGE`. The window drawable cannot be
   written by compute (it is frame-buffer only), so write a texture and `gl_blit`
   it to `GL_WINDOW`.
6. HUD overlay: `gl_overlay_begin(ctx)` and `gl_overlay_present(x, y, w, h)`.
   The gfx framebuffer is RGBA8 with premultiplied alpha, so `gfx_text` keeps its
   coverage when the background has alpha 0. `gl_overlay_begin` clears to alpha 0
   only the rectangle presented last frame (the whole framebuffer the first time
   and after a resize). `gl_overlay_present` uploads that rectangle, widened to
   cover what older frame slots still need, into a stream texture and blits it
   with `GL_BLEND_PREMUL`. Pixels drawn outside the rectangle you pass are not
   shown and are not cleared. `gfx_clear` and a full `gfx_fill_rect` write alpha
   255, which covers the scene, so a HUD that wants the scene visible must not
   call them.
7. Per pass timing: `gl_pass_time_ms(i)` and `gl_pass_count()` describe the last
   completed frame, and `gl_pass_name("raster")` names the next pass. `gl_pass_label(i)`
   returns the name. A compute pass is one encoder, so calling `gl_pass_name`
   between two dispatches makes them two passes. Unnamed passes are called
   `compute`, `render`, `window`, `raster` (no-attachment) or `overlay`. Up to 32
   passes per frame are timed. Whether the device supports pass timestamps is
   reported by `gl_stat(GL_STAT_PASS_TIMING)`.
8. `gl_dispatch(pipe, x, y, z)`: confirmed. x, y and z are grid sizes in threads
   (`dispatchThreads`), so a 2D grid reaches `thread_position_in_grid` as `uint2`
   with no rounding up and no out-of-range thread. The host picks 256 by 1 for 1D,
   16 by 16 for 2D and 8 by 8 by 4 for 3D, within the pipeline limit. Use
   `gl_dispatch_groups` to choose the group size.

## Measured numbers

Machine: Apple M4 Max, macOS 26.2, a 3024x1964 display at 120 Hz. The Mac was
shared and busy (load average above 100 at times), so read every figure as
approximate. The workload is one full-screen fragment pass: eleven rounds of
`sin` and `cos` on a warped coordinate, built once with the typed expressions of
`stdlib/gpu_shader.flow`. The old path ran that same shader through a render job.

Before and after, per frame:

| Frame size | Old path (render job) | New path, no present | New path, presented in a window |
|---|---|---|---|
| 1440x900 | 51.8 ms, 19 fps | CPU 0.08 ms, GPU 0.14 ms, about 11,800 fps | 120 fps (display limit), GPU 0.32 ms |
| 2880x1800 | 76.4 ms, 13 fps | CPU 0.24 ms, GPU 0.63 ms, about 4,000 fps | 120 fps (display limit), GPU 1.15 ms |

How each column was measured:

- Old path: `gpu_job_run` wall time per job with `FLOW_GPU_BACKENDS=metal`, mean of
  the 5 jobs after the first. It covers writing the job directory, launching the
  host, compiling the shader, rendering, writing and reading the RGBA file, and
  the comparison. The first job of a process took 609 ms and 567 ms because it
  also builds the host with `xcrun clang`. The old path never shows the frame.
- New path, no present: the pass renders into an offscreen texture and the frame
  is submitted without a drawable. CPU time is the time inside
  `gl_begin_frame` through `gl_submit`. GPU time is the mean of
  `gl_gpu_time_ms` over 300 frames. The frame rate is the achieved rate of
  that loop with three frames in flight.
- New path, presented: a visible window that is never key and never activated
  (`FLOW_GFX_HIDDEN=2`), 240 timed frames. The compositor paces presentation to
  the display even with vsync off, so every presented loop ran at 120 fps and the
  CPU time inside the frame calls (8.3 ms) is time spent waiting for a drawable.
  That wait is not CPU work. A hidden window (`FLOW_GFX_HIDDEN=1`) is not paced
  and gave erratic rates, so no figure here comes from one.

Variants at 2880x1800 in the paced run (the window path is the same render, blit
and present):

| Variant | GPU ms | Frame rate |
|---|---|---|
| direct to the window | 1.15 | 120 |
| offscreen texture, then `gl_blit` to the window | 1.32 | 120 |
| the above plus a CPU overlay, whole framebuffer uploaded | 1.53 | 81 (12.2 ms per frame) |
| the above, 600x200 dirty rectangle uploaded | 1.44 | 120 |

At 1440x900 all four ran at 120 fps.

Cost of moving a CPU overlay to the GPU, measured without a window (mean of 100
calls, `gl_texture_upload` against `gl_texture_upload_rect`):

| Texture | Whole image | 600x200 rectangle |
|---|---|---|
| 1440x900 RGBA8 (5.2 MB) | 0.17 ms | 0.019 ms |
| 2880x1800 RGBA8 (20.7 MB) | 1.05 ms | 0.033 ms |

A whole-frame overlay at 2880x1800 also costs the CPU a clear of the previous
overlay area and the drawing itself, which together with the 1 ms upload made
some frames miss the 8.3 ms refresh in the run above. Use a dirty rectangle.

Resident resources (`tests/gpu_live/gl_resident.flow`): 1020 frames of compute
plus a render pass with per-frame constants and a stream buffer. After the first
20 frames there were 0 new allocations, device memory stayed at 14,843,904
bytes, process memory grew by at most 80 KB, the shader library compiled once,
and an atomic counter read exactly 1020 at the end. Pass timestamps agreed with
the command buffer time within 15 percent.

Compute (`gl_compute.flow`): a vector add over 1,048,613 floats and a two-stage
`u32` reduction matched the CPU result exactly. Render (`gl_render.flow`): a
triangle and a textured quad in 64x64 matched a CPU rasteriser in every channel
(largest difference 0), and the tolerance in the test is 8 per channel with up
to 120 channel values allowed to exceed it.

## Limits

- Apple silicon with unified memory. Other Macs and other platforms report
  `gl_available() == false`; Linux and Windows link a stub.
- One colour attachment per pass, no multisampling, no stencil, 2D textures with
  one mip level, depth format `GL_DEPTH32F` only. A no-attachment pass is
  supported.
- At most 65,535 live handles, 31 buffer slots and 16 texture slots, a 4 MB
  `gl_bind_bytes` ring per frame slot, 32 timed passes per frame, textures up to
  16384 pixels a side.
- `gl_texture_read` of a depth texture is not supported.
- Pass timestamps depend on counter sampling at stage boundaries. The tick to
  nanosecond factor is calibrated once at `gl_init` over 40 ms.
- A resource written by the CPU while the GPU still reads it can tear unless it
  is a stream resource or the program calls `gl_wait_idle` first.
- The window must be created with `gfx_open` or `gfx_open_hidpi` on macOS.
  `flow record` has no window, so under it `gl_attach_window` returns -1. Use
  `gl_overlay_target` and `gl_texture_read` for captures.
- The drawable is BGRA8 with no colour space set, so values reach the display
  as the CPU path sends them. Pipelines that draw to `GL_WINDOW` use `GL_BGRA8`.
- Tested on one machine, an M4 Max.

## Linking

A program that imports `stdlib/gpu_live.flow` links the host through the Flow
runtime archive, which compiles `runtime/gpu_metal_host.m` with `-fobjc-arc`
and adds the Metal, Foundation and QuartzCore frameworks. `./flow run`,
`./flow gfx`, `./flow debug` and `./flow record` all do this. On a platform
without Metal, `runtime/gpu_metal_host_stub.c` links and `gl_available()` is
false. Window presentation uses `flow_gfx_set_layer`, `flow_gfx_view_info` and
`flow_gfx_pixels` from `runtime/gfx_macos.m`, found with `dlsym`, so a program
without a window links without Cocoa.

## Commands

```text
./flow run tests/gpu_live/gl_compute.flow          compute, exact against the CPU
./flow run tests/gpu_live/gl_render.flow           triangle and textured quad against a CPU rasteriser
./flow run tests/gpu_live/gl_resident.flow         1020 frames, nothing allocated, memory flat
./flow run tests/gpu_live/gl_headless.flow         no window: compute and a no-attachment pass
./flow run tests/gpu_live/gl_fallback.flow         GPU forced off
./flow gfx tests/gpu_live/gl_present.flow          hidden window, presentation and overlay
FLOW_GL_REQUIRE=1 ./flow run tests/gpu_live/gl_compute.flow     fail instead of skip without a GPU

BENCH_W=2880 BENCH_H=1800 BENCH_MODE=new ./flow gfx tests/gpu_live/bench_frame.flow
BENCH_VISIBLE=1 BENCH_FRAMES=240 BENCH_W=2880 BENCH_H=1800 BENCH_MODE=new ./flow gfx tests/gpu_live/bench_frame.flow
BENCH_W=2880 BENCH_H=1800 BENCH_MODE=headless ./flow gfx tests/gpu_live/bench_frame.flow
BENCH_W=2880 BENCH_H=1800 BENCH_MODE=upload ./flow gfx tests/gpu_live/bench_frame.flow
FLOW_REPO_ROOT=$PWD FLOW_GPU_BACKENDS=metal BENCH_MODE=old BENCH_W=2880 BENCH_H=1800 ./flow gfx tests/gpu_live/bench_frame.flow

./flow gfx examples/gpu/gpu_live_demo.flow
GPU_LIVE_OUT=frames GPU_LIVE_FRAMES=60 ./flow gfx examples/gpu/gpu_live_demo.flow
```

The tests print `SKIP` and exit 0 when there is no GPU, unless `FLOW_GL_REQUIRE=1`.
`FLOW_GL_FORCE_OFF=1` turns the GPU path off for any program. The demo output is
`docs/images/gpu_live_demo.gif`.

The `flow record` link fix is a build change in `tools/flow_cli/build.flow`.
