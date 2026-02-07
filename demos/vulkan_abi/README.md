# Vulkan ABI (Flow-first)

This folder defines a small C ABI surface and generates bindings for Flow.

Source of truth:
- `demos/vulkan_abi/renderer.abi`

Generated files (do not edit by hand):
- `demos/vulkan_abi/renderer.h`
- `demos/vulkan_abi/renderer.flow`

Regenerate:
```
python3 scripts/gen_abi_bindings.py demos/vulkan_abi/renderer.abi
```
