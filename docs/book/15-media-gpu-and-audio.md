# 15. Graphics, shaders, GPU, UI, and audio

Flow graphics and audio use ordinary state and functions with native runtimes. Fill shaders and `@gpu` functions generate device code. Every host-Flow or fill-shader block labelled `flow` in this chapter is validated in CI.

## 15.1 Native graphics

```bash
./flow gfx examples/games/pong_gfx.flow
```

The graphics runtime supplies window creation, frame loops, input state, 2D primitives, text, images, and buffer blits. Separate simulation update from drawing so headless tests can exercise logic without a window.

## 15.2 Input and time

Use held-key state for continuous motion and pressed-edge state for toggles. Time-dependent updates should use explicit `dt` or a fixed simulation step.

```bash
./flow gfx examples/games/snake_gfx.flow
./flow gfx examples/procgen/wfc_dungeon.flow
./flow gfx examples/morphogenesis/gray_scott.flow
```

## 15.3 Headless recording

```bash
./flow record examples/evolution/lorenz_gfx.flow --frames 300 --skip 10 --fps 30 --gif build/lorenz.gif
```

Deterministic recording requires deterministic initial state, input, random seed, and time stepping.

## 15.4 Fill shaders

Fill-shader source is a constrained Flow DSL and is validated by the documentation checker through the shader parser:

```flow from=examples/gpu/shader_plasma.flow
shader fill plasma {
    let u: f32 = uv.x
    let v: f32 = uv.y
    let t: f32 = time
    color = vec4(
        0.5 + 0.5 * sin(u * 10.0 + t),
        0.5 + 0.5 * cos(v * 8.0 - t),
        0.5 + 0.5 * sin((u + v) * 4.0 + t * 1.3),
        1.0
    )
}
```

```bash
./flow shader examples/gpu/shader_plasma.flow
```

FSL is not arbitrary host Flow: allocation, general I/O, effects, and unrestricted pointer operations are intentionally excluded.

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

The shipped GPU generator targets Metal. CUDA and OpenCL backends are not claimed as shipped targets.

## 15.6 GPU memory

`stdlib/gpu_memory.flow` wraps Metal buffers and copies. The lifecycle is: create the runtime, allocate/wrap buffers, upload input, dispatch, synchronize where required, download results, then destroy buffers and runtime. Unified memory can reduce copies but does not remove ordering or lifetime requirements.

## 15.7 WebGPU and WGSL

Flow can generate WGSL for supported browser GPU crossings. WGSL binding/layout rules differ from Metal, so kernels may require backend-specific adjustments.

## 15.8 Software 3D

```bash
./flow gfx examples/threed/spinning_solids.flow
./flow gfx examples/threed/voxel_world.flow
./flow gfx examples/threed/physics3d.flow
```

`stdlib/render3d.flow` is a CPU raster pipeline intended for portable demonstrations, study, and tests.

## 15.9 UI layout

```bash
./flow demo ui-layout
./flow demo ui-layout-window
```

UI syntax sugar is still evolving; the ordinary `ui_layout.flow` library functions are the explicit stable interface.

## 15.10 Audio processing

```bash
./flow audio examples/audio/lattice_allpass_phase_engine.flow
./flow compile-audio examples/audio/rt_safe_callback.flow
```

An audio callback must be bounded and nonblocking. Allocate during setup, process preallocated storage in the callback, and release resources after the device stops. `@rt_safe` and callback lifetime domains enforce the known static restrictions.

## 15.11 Audio graphs and control rates

Audio graphs connect processors and buses while scheduling establishes block order. Feedback requires explicit delay state. Sample-rate and control-rate work should be separated deliberately because they have different cost and numerical behavior.

## 15.12 Vulkan demonstrations

```bash
./flow demo vulkan basic
./flow demo vulkan advanced
./flow demo vulkan-flow tetris
./flow demo vulkan-flow layout-dsl
```

On macOS the Vulkan demos use MoltenVK.

## Exercises

Split update/draw logic for a moving object; record a deterministic animation; estimate GPU crossover for a small kernel; and design setup/callback/teardown phases for an audio effect.

Next: [Compilation targets and distribution](16-targets-and-distribution.md).
