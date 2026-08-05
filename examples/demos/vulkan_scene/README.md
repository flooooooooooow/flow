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

`run.sh` sets `VK_ICD_FILENAMES` and `VK_LAYER_PATH` for Homebrew installs.
