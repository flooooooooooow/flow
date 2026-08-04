# Vulkan Triangle Demo (macOS + MoltenVK)

This demo uses GLFW + Vulkan (via MoltenVK) to render a simple triangle.

## Build

```bash
make -C demos/vulkan_triangle
```

## Run

```bash
make -C demos/vulkan_triangle run
```

You can also use the FLOW CLI:

```bash
./flow demo vulkan
# compat aliases: ./flow vulkan-demo  |  ./flow vulkan-demo-basic
```

`run.sh` sets `VK_ICD_FILENAMES` and `VK_LAYER_PATH` for Homebrew installs.
