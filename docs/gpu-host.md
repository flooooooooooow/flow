# Resident GPU host (gpu_live)

Status: interface frozen for the first release, extended on request of the
driving simulator (see "Answers to the consumer requests"). Measured numbers
are filled in below as they are taken.

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
gl_overlay_begin(ctx: ptr<void>)   gl_overlay_present(x, y, w, h)
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

To be filled from `tests/gpu_live/bench` runs.

## Limits

To be completed with the implementation.

## Linking

A program that imports `stdlib/gpu_live.flow` links the host automatically
through the runtime archive. `./flow run`, `./flow gfx` and `./flow debug` all
include it. On a platform without Metal the stub in `runtime/gpu_metal_host_stub.c`
links and `gl_available()` is false.
