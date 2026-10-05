# Flow-Style Vulkan (Complex Example)

The first block below is intentionally a **Flow-inspired design sketch**, not current runnable Flow. It mirrors the lower-level renderer architecture while making ownership and lifecycle intent explicit.

```flow-pseudocode
struct Renderer {
    instance: VkInstance,
    device: VkDevice,
    swapchain: VkSwapchain,
    pipeline: VkPipeline,
    framebuffers: array<VkFramebuffer, 3>,
    sync: SyncObjects,
}

function renderer_init() -> Renderer {
    # design sketch: create Vulkan resources
    ...
}

function renderer_draw(mut r: Renderer) -> void {
    # design sketch: acquire, record, submit, present
    ...
}

function renderer_shutdown(r: Renderer) -> void {
    # design sketch: destroy owned resources in reverse order
    ...
}
```

The repo's practical Vulkan wrapper is real Flow and can be used as a complete compilation unit:

```flow
import "stdlib/vulkan_renderer.flow"

function main() -> i32 {
    let mut r: Renderer = renderer_advanced()
    r = renderer_set_window(r, 1024, 720, "Flow Vulkan Advanced")
    r = renderer_set_clear(r, 0.03, 0.03, 0.07)
    r = renderer_set_camera(r, 3.2, 0.35, 0.7)
    r = renderer_set_instances(r, 25)
    return renderer_run(r)
}
```

The full advanced demo is [`../vulkan_flow_advanced/src/main.flow`](../vulkan_flow_advanced/src/main.flow). The design sketch is useful for architecture discussion; the second block is the compiler-checked API surface.
