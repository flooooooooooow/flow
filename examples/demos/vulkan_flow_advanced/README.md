# Flow Vulkan Advanced Demo

Flow-first Vulkan wrapper that renders a textured, instanced scene with depth and camera.

Run:

```bash
./flow demo vulkan-flow advanced
```

Tweak settings in `src/main.flow` using the renderer helpers:

- `renderer_set_texture` (PNG via ImageIO on macOS)
- `renderer_set_camera` (distance, pitch, yaw)
- `renderer_set_instances`
