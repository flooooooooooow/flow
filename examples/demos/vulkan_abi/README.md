# Vulkan ABI (Flow-first)

This folder defines a small C ABI surface and generates bindings for Flow.

Source of truth:
- `examples/demos/vulkan_abi/renderer.abi`
- `examples/demos/vulkan_abi/vulkan_renderer.abi`

Generated files (do not edit by hand):
- `examples/demos/vulkan_abi/renderer.h`
- `examples/demos/vulkan_abi/renderer.flow`
- `examples/demos/vulkan_abi/vulkan_renderer.h`
- `examples/demos/vulkan_abi/vulkan_renderer.flow`

Regenerate:
```
python3 scripts/gen_abi_bindings.py examples/demos/vulkan_abi/renderer.abi
```
