# FLOW Fill Shaders

A tiny surface language for fullscreen fragment demos — Shadertoy-simple, Metal under the hood.

```flow
shader fill plasma {
    let u = uv.x
    let v = uv.y
    color = vec4(
        0.5 + 0.5 * sin(u * 10.0 + time),
        0.5 + 0.5 * cos(v * 8.0 - time),
        0.5, 1.0
    )
}
```

```bash
./flow shader examples/gpu/shader_plasma.flow
./flow shader examples/gpu/shader_plasma.flow --frames 3
./flow shader examples/gpu/shader_ripple.flow --size 1280x720
./flow shader examples/gpu/shader_plasma.flow --emit-only   # write .metal only
```

## Language (v1)

| Construct | Meaning |
|-----------|---------|
| `shader fill Name { ... }` | Fullscreen fragment shader |
| `uv` | `vec2` in `[0,1]` (y flipped for top-left origin) |
| `time` | Seconds since launch (`f32`) |
| `color = vec4(...)` | Required output |
| `let x = ...` | Locals |
| `if cond` / `else` | Single-statement branches |
| `vec2` / `vec3` / `vec4` | Constructors |
| `.xyzw` / `.rgb` | Swizzles |
| `sin` `cos` `abs` `sqrt` `min` `max` `fract` `length` `mix` `smoothstep` `clamp` `pow` … | Metal builtins |

No textures, no vertex attributes, no compute in this surface (use `@gpu` + `./flow gpu` for compute).

## Pipeline

1. `src/flow/shader_dsl.py` extracts / parses the block  
2. `src/flow/shader_codegen.py` emits MSL (`build/shaders/<name>_fill.metal`)  
3. `runtime/shader_view_metal.m` opens a Cocoa + `CAMetalLayer` window  

macOS only for the live viewer; `--emit-only` works anywhere Python runs.
