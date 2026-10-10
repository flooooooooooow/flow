# Captured vgpu rgba8unorm references

This directory is the frozen output of

```bash
./flow gpu test --suite vgpu --backend webgpu --case gradient --capture-reference
```

Capture is a dedicated software rasterizer of the upstream gradient contract
(pixel-center UVs, `smoothstep` vignette, rgba8unorm packing). It is not the
Metal window or the browser canvas path. Ordinary `flow gpu test` only reads
these files; it does not rewrite them.

Recapture only when the upstream formula, the FSL UV convention, or the
checked-in `gradient.flow` math changes, then re-run the command above.

The `*_128x72.rgba8.hex` files are the frames of the seven render-job cases
(#811), captured from the Flow programs on the Metal device with

```bash
./flow gpu test --suite vgpu --backend metal --case <id> --capture-reference
```

The WebGPU frame of each case matched its Metal frame byte for byte when
they were captured. Recapture when a program's scene changes.
