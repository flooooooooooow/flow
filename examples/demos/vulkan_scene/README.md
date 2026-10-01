# Vulkan Scene Demo (macOS + MoltenVK)

This demo renders a rotating, colored triangle using a vertex buffer and push constants.

## Build

```bash
make -C examples/demos/vulkan_scene
```

## Run

```bash
make -C examples/demos/vulkan_scene run
```

FLOW CLI:

```bash
./flow vulkan-demo-advanced
```

`flow demo vulkan advanced` sets `VK_ICD_FILENAMES` and `VK_LAYER_PATH` for Homebrew installs.
This directory is a copy of `demos/vulkan_scene`; `make run` here runs that demo.
