# FLOW Shader Language (FSL)

A real (but focused) shading language for fullscreen fragment demos — lowers to Metal.

**Want to see it before reading the reference?** Open the
[Photoreal FSL Gallery](../demos/shaders.md): 64 recorded shader entries with
source and run commands on every tile.

```bash
./flow shader examples/gpu/shader_showcase.flow
```

**Gallery controls:** `←` / `→` / `Space` cycle · `1`–`9` jump · `Esc` quit

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

## Galleries

### Classic showcase

`examples/gpu/shader_showcase.flow` — 12 demos (plasma, ripple, waves, checker, noise, Mandelbrot, Julia, stars, rings, fire, spiral, grid).

```bash
./flow shader examples/gpu/shader_showcase.flow
./flow shader examples/gpu/shader_showcase.flow --emit-only
./flow shader examples/gpu/shader_plasma.flow --name plasma
```

### Photorealistic showcase — 64 examples

The [visual gallery](../demos/shaders.md) contains **64 runnable FSL shaders**
split across two launchable files. `examples/gpu/shader_photoreal.flow`
contains four full ray-marched scene studies: `photoreal_studio`,
`photoreal_glass`, `photoreal_marble`, and `photoreal_chrome`. They demonstrate
SDF scene composition, finite-difference normals, soft shadows, ambient
occlusion, Fresnel response, chromatic refraction, reflection, procedural
stone, metals, wet surfaces, moving cameras, and environment lighting.

`examples/gpu/shader_photoreal_materials.flow` adds 60 compact PBR-style
material-ball studies. The set covers polished and brushed metals; clear,
smoked, amber, aqua and frosted glass; ruby, sapphire and emerald crystals;
marble, jade, granite, travertine, porcelain, terracotta and obsidian; lacquer,
candy paint, pearlescent and iridescent coatings, enamel, clearcoat and carbon
weave; walnut, mahogany, oak, leather, velvet, satin, silk and wax; concrete,
wet concrete, asphalt, wet asphalt, rubber, ABS plastic, acrylic and ceramic
tile; neon glass, holographic alloy, plasma, lava, ice, alien alloy, reactor
metal and energy crystal; plus sunset, overcast, night-city, desert, arctic,
forest and underwater environment studies.

The material gallery shares one procedural renderer rather than duplicating the
shading implementation. Every entry still becomes its own FSL fragment entry
and can be selected independently. Materials vary base/accent response,
metalness, roughness, procedural surface structure, environment,
transmission/refraction and emission. No textures, meshes, cubemaps, or image
assets are required.

```bash
./flow shader examples/gpu/shader_photoreal.flow
./flow shader examples/gpu/shader_photoreal.flow --name photoreal_glass

./flow shader examples/gpu/shader_photoreal_materials.flow
./flow shader examples/gpu/shader_photoreal_materials.flow --name photoreal_gold
./flow shader examples/gpu/shader_photoreal_materials.flow --name photoreal_energy_crystal
./flow shader examples/gpu/shader_photoreal_materials.flow --emit-only
```

Record the same shaders into the Wiki gallery through the actual generated Metal
pipeline:

```bash
python3 scripts/record_shader_gallery.py --group photoreal
python3 scripts/build_shader_gallery.py --check --check-assets
```

The unit tests enforce exactly 64 unique photoreal entries across the two source
files. The gallery generator independently enforces the same count and requires
a GIF for every entry.

## Pipeline

1. `src/flow/shader_dsl.py` — lex/parse FSL  
2. `src/flow/shader_codegen.py` — emit MSL (+ hash/noise prelude)  
3. `runtime/shader_view_metal.m` — Cocoa + `CAMetalLayer` live gallery viewer  
4. `runtime/shader_record_metal.m` — deterministic offscreen Metal recorder for published GIFs  
5. `scripts/build_shader_gallery.py` — source-derived visual gallery page + asset contract

macOS for the live window and recorded Metal output; `--emit-only` works anywhere.

Related: [Photoreal FSL Gallery](../demos/shaders.md) · [Demo Showcase](../demos/overview.md) · [Recording contract](../demos/README.md)
