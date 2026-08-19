# 15. Graphics, shaders, GPU, UI, and audio

Flow graphics and audio use ordinary state and functions with native runtimes.
Fill shaders and `@gpu` functions generate device code. UI layout and 3D
rendering are provided by libraries and small domain-specific languages.

## 15.1 Native graphics

The graphics runtime supplies window creation, a frame loop, input state, 2D
primitives, text, images, and buffer blits. Programs run with:

```bash
./flow gfx examples/games/pong_gfx.flow
```

The backend is Cocoa/CoreGraphics/Metal-oriented on macOS and SDL2-oriented on
Linux and Windows. Platform packages and linker flags therefore differ.

A conventional frame has this order:

```text
poll input
update state with elapsed time
clear the frame
draw the current state
present
```

Separate update from drawing so headless tests can exercise game or simulation
logic without a window.

## 15.2 Input and time

Continuous key state answers “is held”; edge state answers “pressed this
frame”. Use edge state for toggles and held state for movement. Time-dependent
updates should use an explicit `dt` or a fixed simulation step rather than
assuming one update per display refresh.

The graphics tutorial and game corpus demonstrate keyboard, mouse, collision,
sprites, text, and frame timing:

```bash
./flow gfx examples/games/snake_gfx.flow
./flow gfx examples/procgen/wfc_dungeon.flow
./flow gfx examples/morphogenesis/gray_scott.flow
```

## 15.3 Headless recording

`flow record` drives a graphics program without an interactive window and
writes frames or a GIF:

```bash
./flow record examples/evolution/lorenz_gfx.flow \
    --frames 300 --skip 10 --fps 30 \
    --gif build/lorenz.gif
```

Options select frame count, warm-up frames, output directory, simulated keys,
frame rate, stride, and width. Deterministic recording requires deterministic
initial state, input, random seed, and time stepping.

## 15.4 Fill shaders

```text
shader fill plasma(width: f32, height: f32, time: f32) -> vec4 {
    let uv = frag_coord / vec2(width, height)
    let value = 0.5 + 0.5 * sin(time + uv.x * 12.0)
    return vec4(value, uv.y, 1.0 - value, 1.0)
}
```

FSL supports numeric/vector declarations, fragment inputs, arithmetic,
selection, and a defined set of math and shader-library built-ins. The shader
compiler translates the fill function to Metal on macOS or to the supported C
fallback.

```bash
./flow shader examples/graphics/shader_demo.flow
```

FSL is a constrained language, not arbitrary host Flow. Allocation, general
I/O, effects, and unrestricted pointer operations do not belong in device
code.

## 15.5 Compute kernels

```flow
@gpu
function saxpy(x: ptr<f32>, y: ptr<f32>, a: f32, n: i32) -> void {
    let i: i32 = gpu_thread_id()
    if i < n {
        y[i] = a * x[i] + y[i]
    }
}
```

```bash
./flow gpu examples/gpu/simd_saxpy.flow
```

The GPU generator emits Metal source for `@gpu` functions. Thread and block
identifiers, barrier operations, and a restricted set of scalar and vector
expressions are available in device code. CUDA and OpenCL backends are not
shipped.

## 15.6 GPU memory

`stdlib/gpu_memory.flow` wraps Metal buffers and copies. A typical lifecycle is:

```text
create device/runtime
allocate or wrap buffers
upload inputs
dispatch kernel
wait at the required synchronisation point
download results
destroy buffers and runtime
```

Unified memory reduces copies on supported Apple systems but does not remove
ordering and lifetime requirements. Small jobs may be slower on GPU because
dispatch and synchronisation dominate.

## 15.7 WebGPU and WGSL

Flow can generate WGSL for browser GPU crossings on supported WebAssembly
pages. WGSL storage layouts and binding rules differ from Metal. The crossing
code handles those differences, but a Metal kernel may still need changes for
WGSL.

## 15.8 Software 3D

`stdlib/render3d.flow` implements a CPU raster pipeline: coordinate transforms,
camera projection, clipping, depth, lighting, triangles, lines, ray queries,
and billboard particles within fixed limits.

```bash
./flow gfx examples/threed/spinning_solids.flow
./flow gfx examples/threed/voxel_world.flow
./flow gfx examples/threed/physics3d.flow
```

Use the renderer for study, tests, and portable demonstrations. Production GPU
rendering needs a different implementation.

## 15.9 UI layout

Flow includes library layout helpers and partial syntax sugar for
`ui_layout`, rows, columns, stacks, and grids. Layout computes rectangles from
constraints; a window backend draws them and routes input.

```bash
./flow demo ui-layout
./flow demo ui-layout-window
```

The syntax is host-dependent and evolving. The ordinary `ui_layout.flow`
functions provide the more explicit interface.

## 15.10 Audio processing

The audio library includes oscillators, filters, delay lines, envelopes,
scales, graph processing, clocks, WAV I/O, safety checks, and specialised DSP
such as lattice all-pass filters.

```bash
./flow audio examples/audio/lattice_allpass_phase_engine.flow
./flow compile-audio examples/audio/rt_safe_callback.flow
```

An audio callback must be bounded and nonblocking. Allocate graphs and buffers
during setup; process preallocated spans in the callback; release resources
after the device stops. `@rt_safe` and the callback lifetime domain enforce the
known transitive restrictions.

## 15.11 Audio graph and control rates

Audio graphs connect processors and buses while a scheduler establishes block
order. Sample-rate work processes every sample; control-rate work updates less
frequently. The distinction affects both CPU budget and numeric behaviour.
Feedback paths require explicit delay state, just as flow composition requires
state to break an algebraic loop.

## 15.12 Vulkan demonstrations

The CLI contains native Vulkan and Flow-driven Vulkan demos:

```bash
./flow demo vulkan basic
./flow demo vulkan advanced
./flow demo vulkan-flow tetris
./flow demo vulkan-flow layout-dsl
```

On macOS these use MoltenVK. Compatibility aliases exist for the historical
command names, but `flow demo ...` is the canonical interface.

## Exercises

1. Split a moving rectangle into update and draw functions.
2. Record a deterministic 120-frame animation.
3. Estimate when GPU dispatch overhead exceeds a small kernel's useful work.
4. Design setup, callback, and teardown phases for one audio effect.

Next: [Compilation targets and distribution](16-targets-and-distribution.md).
