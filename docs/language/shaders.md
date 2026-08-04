# FLOW Shader Language (FSL)

A real (but focused) shading language for fullscreen fragment demos — lowers to Metal.

```bash
./flow shader examples/gpu/shader_showcase.flow          # all shaders in a GRID
./flow shader examples/gpu/shader_showcase.flow --cycle  # one at a time
```

**Grid controls (default):** click a cell to focus · `G` toggle grid/focus · `1`–`9` focus · `Esc` back to grid / quit  
**Cycle controls:** `←` / `→` / `Space` · `G` grid · `Esc` quit

## Quick example

```flow
fn pulse(t: f32, speed: f32) -> f32 {
    return 0.5 + 0.5 * sin(t * speed)
}

shader fill neon {
    let p: vec2 = uv - vec2(0.5)
    let r: f32 = length(p)
    let col: vec3 = palette(r + time * 0.2) * pulse(time, 3.0)
    color = vec4(col, 1.0)
}
```

## Language

### Declarations

| Form | Meaning |
|------|---------|
| `fn name(a: T, b: U) -> V { ... }` | Helper function (file scope) |
| `shader fill Name { ... }` | Fullscreen fragment entry |
| `let x: T = ...` / `var x: T = ...` | Locals (`var` for reassignment) |
| `return expr` | Return from `fn` |
| `if cond { ... } else { ... }` | Brace blocks (else-if ok) |
| `for i in 0 to N { ... }` | Integer loop (`i` is `int`) |

### Types

`f32`, `i32`, `bool`, `vec2`, `vec3`, `vec4`  
Casts: `f32(x)`, `i32(x)`  
Constructors: `vec2(...)`, `vec3(...)`, `vec4(...)`  
Swizzles: `.xyzw`, `.rgb`, …

### Builtins (inputs)

| Name | Type | Notes |
|------|------|-------|
| `uv` | `vec2` | `[0,1]`, y flipped (top-left origin) |
| `time` | `f32` | Seconds since launch / since last switch |
| `resolution` | `vec2` | Drawable size in pixels |
| `color` | `vec4` | **Required** output assign |

### Builtins (math)

`sin` `cos` `tan` `asin` `acos` `atan` `atan2`  
`abs` `sign` `floor` `ceil` `fract` `mod`  
`sqrt` `pow` `exp` `log` `min` `max` `clamp` `saturate`  
`mix` `step` `smoothstep`  
`length` `distance` `dot` `cross` `normalize` `reflect` `refract`

### Builtins (FSL stdlib)

| Name | Role |
|------|------|
| `hash(x)` / `hash(p)` | 1D / 2D hash → `f32` |
| `noise(p)` | Value noise |
| `fbm(p)` | 5-octave fractal noise |
| `palette(t)` | Cosine palette → `vec3` |

## Showcase

`examples/gpu/shader_showcase.flow` — 12 demos (plasma, ripple, waves, checker, noise, Mandelbrot, Julia, stars, rings, fire, spiral, grid).

```bash
./flow shader examples/gpu/shader_showcase.flow          # GRID — all 12 at once
./flow shader examples/gpu/shader_showcase.flow --cycle  # one at a time
./flow shader examples/gpu/shader_showcase.flow --emit-only
./flow shader examples/gpu/shader_plasma.flow --name plasma
```

**Grid:** click a cell to focus · `G` toggle · `1`–`9` focus · `Esc` back / quit  
**Cycle:** `←` / `→` / `Space` · `G` for grid · `Esc` quit

## Pipeline

1. `src/flow/shader_dsl.py` — lex/parse FSL  
2. `src/flow/shader_codegen.py` — emit MSL (+ hash/noise prelude)  
3. `runtime/shader_view_metal.m` — Cocoa + `CAMetalLayer` gallery viewer  

macOS for the live window; `--emit-only` works anywhere.
