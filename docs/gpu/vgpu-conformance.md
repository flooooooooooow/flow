# vgpu conformance runner

`flow gpu test --suite vgpu` turns `examples/gpu/vgpu/` into a measurable
compatibility suite. It reads `examples/gpu/vgpu/manifest.json`, compiles each
fill shader with the requested backend, and compares a frame or a tensor
against a captured reference. It does not screenshot a window.

## Command

```text
./flow gpu test --suite vgpu --backend metal
./flow gpu test --suite vgpu --backend webgpu
./flow gpu test --suite vgpu --all-backends
```

Each case/backend line is:

```text
CASE <id> [<backend>] <verdict> w=<w> h=<h> time=<t> seed=<s> camera=<c> model=<m> maxError=<e>
```

`<verdict>` is one of `EXACT`, `TOLERANCE`, `NUMERICAL`, `UNSUPPORTED`, or
`FAIL`. The process exits non-zero when any case `FAIL`s (an unexpected
regression). `UNSUPPORTED` is not a failure: it names the capability that
still blocks the case (for example `tensor-model-execution` on the MNIST and
depth placeholders until GPU tensors land).

Optional flags:

| Flag | Effect |
|---|---|
| `--manifest PATH` | use a fixture manifest instead of the corpus |
| `--case ID` | run one case |
| `--capture-reference` | rewrite reference files from the capture renderer |
| `--selftest` | check `compareRgba` / numerical contracts without the corpus |

## Comparison modes

The case's `comparison.mode` selects the matcher:

| Mode | Meaning |
|---|---|
| `exact-rgba8` | packed RGBA8 must match the reference byte-for-byte |
| `tolerance` | every channel may differ by at most `channelTolerance` |
| `numerical` | f32 buffers compared with `maxAbs` |

Pixel comparison is the Flow implementation of `compareRgba` from the WebGPU
host (`wasm/crossing_assets/webgpu-host.js` / `site/wasm-crossings/gpu/webgpu-host.js`).
That host renders a generated FSL fragment into an offscreen `rgba8unorm`
texture, copies it to a readback buffer, and strips WebGPU row padding. The
runner consumes the same comparison contract rather than canvas screenshots.

## Gradient exact-pixel case

`examples/gpu/vgpu/gradient.flow` is validated at 160×90, `time=0`, against
`examples/gpu/vgpu/refs/gradient_160x90.rgba8.hex`. The reference is a captured
upstream `rgba8unorm` image of the public vgpu gradient (pixel-center UVs,
`smoothstep` vignette). Capture is a separate command from ordinary Flow
shader windows:

```bash
./flow gpu test --suite vgpu --backend webgpu --case gradient --capture-reference
```

Both Metal (MSL emit) and WebGPU (WGSL emit) must compile the fill and match
that frozen image.

## Render-job cases

A case whose `renderer` is `render-job` is a Flow program built on
[GPU render jobs](../library/gpu-render.md) (#811). The runner runs it with
`FLOW_GPU_BACKENDS` set to the backend. The program draws its frame on the
real device (the Metal host `runtime/gpu_render_metal.m`, or
`tools/gpu_render/webgpu_host.mjs` under Deno), checks its own pixel probes
and compares the frame with its `reference` within the case's
`channelTolerance`. A frame identical to the reference is `EXACT`, one
within tolerance `TOLERANCE`. A backend without a device or toolchain is
`UNSUPPORTED`.

```bash
./flow gpu test --suite vgpu --all-backends --case earth
```

`--capture-reference` rewrites a render-job reference from the frame the
first backend renders. These references pin the Flow scene; they are not
images of the upstream pages.

## Numerical cases

MNIST and depth estimation declare `comparison.mode: numerical` and
`capability: tensor-model-execution`. Each backend reports `NUMERICAL` only
after a device run matches the example's host reference within `maxAbs`:

- Metal: the example runs its `gpu_tensor` model kernels on the Metal
  device and prints `GPU_DEVICE_EXECUTED metal` once a dispatch completed.
- WebGPU: the runner emits the example's `@gpu` kernels as WGSL with their
  reflection (`tools/gpu/main.flow --crossing-manifest`), chains them over
  persistent device buffers with `runFlowKernelChain` in Deno
  (`tools/gpu_test/webgpu_model.mjs`), reads the output back and compares
  it with the `reference` line the example printed. `FLOW_DENO` names the
  Deno binary.

With no device, no Deno or no adapter the case is `UNSUPPORTED
reason=device-execution`, never a pass. Fixture manifests under
`tests/gpu/vgpu/` exercise a real numerical pass and fail.

## Related

- Corpus: `examples/gpu/vgpu/`
- Track: [vgpu parity](../project/vgpu-parity.md)
- FSL: [Shaders](../language/shaders.md)
- WebGPU host: [WASM crossings](../language/wasm-crossings.md)
