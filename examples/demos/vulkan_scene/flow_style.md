# Flow-Style Vulkan (Complex Example)

Below is a **Flow-inspired** way to structure a Vulkan renderer so the *intent* is obvious, lifetimes are explicit, and cleanup is guaranteed. This is a design sketch that mirrors the C++ demo, but uses Flow principles:

- **Explicit resources** as values (no hidden globals).
- **Clear ownership** via a single `Renderer` struct.
- **Structured cleanup** in one place.
- **High-level API** that hides Vulkan noise.

```text
# Flow-style Vulkan renderer (design sketch)

struct Renderer {
    instance: VkInstance,
    device: VkDevice,
    swapchain: VkSwapchain,
    pipeline: VkPipeline,
    framebuffers: array<VkFramebuffer, 3>,
    sync: SyncObjects,
}

struct SyncObjects {
    image_available: array<VkSemaphore, 2>,
    render_finished: array<VkSemaphore, 3>,
    in_flight: array<VkFence, 2>,
    images_in_flight: array<VkFence, 3>,
}

effect Log {
    info(msg: string) -> void
}

capability ConsoleLog {
    effect Log
    function info(msg: string) -> void { println(msg) }
}

function renderer_init() -> Renderer {
    Log.info("Init: instance, device, swapchain, pipeline")
    let instance = vk_create_instance()
    let device = vk_create_device(instance)
    let swapchain = vk_create_swapchain(device)
    let pipeline = vk_create_pipeline(device, swapchain)
    let framebuffers = vk_create_framebuffers(device, swapchain)
    let sync = vk_create_sync(device, swapchain)
    return Renderer { instance, device, swapchain, pipeline, framebuffers, sync }
}

function renderer_draw(mut r: Renderer) -> void {
    let image = vk_acquire_image(r.swapchain, r.sync.image_available)
    vk_wait_fence(r.sync.images_in_flight[image])
    r.sync.images_in_flight[image] = r.sync.in_flight[current_frame()]

    vk_record_commands(r.pipeline, r.framebuffers[image])
    vk_submit(r.sync.image_available, r.sync.render_finished[image])
    vk_present(r.swapchain, r.sync.render_finished[image])
}

function renderer_shutdown(r: Renderer) -> void {
    Log.info("Shutdown: destroy pipeline, swapchain, device, instance")
    vk_destroy_sync(r.sync)
    vk_destroy_framebuffers(r.framebuffers)
    vk_destroy_pipeline(r.pipeline)
    vk_destroy_swapchain(r.swapchain)
    vk_destroy_device(r.device)
    vk_destroy_instance(r.instance)
}

function main() -> i32 handles Log with ConsoleLog {
    let mut r = renderer_init()
    while !window_should_close() {
        renderer_draw(r)
    }
    renderer_shutdown(r)
    return 0
}
```

## Why this is “Flow-like”

- **One owner**: `Renderer` owns everything. This avoids hidden global state.
- **Effect-based logging**: replaces ad‑hoc `printf` and makes it testable.
- **Explicit control flow**: `init → loop → shutdown` is transparent.
- **No surprises**: resources are destroyed in one place, in a clear order.

This mirrors the real C++ demo but expresses the *intent* at a higher level, which is the point of Flow.

## Practical Flow API (in this repo)

Use the higher-level wrapper in `lib/stdlib/vulkan_renderer.flow`:

```text
let mut r: Renderer = renderer_advanced()
r = renderer_set_window(r, 1024, 720, "Flow Vulkan Advanced")
r = renderer_set_clear(r, 0.03, 0.03, 0.07)
r = renderer_set_camera(r, 3.2, 0.35, 0.7)
r = renderer_set_instances(r, 25)
renderer_run(r)
```
