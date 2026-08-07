# Shaders (FSL)

Fullscreen fragment fills that lower to Metal. Author helpers with `fn` and
entry points with `shader fill Name { ... }`.

> [!important] Native only (macOS Metal)
> ```bash
> ./flow shader examples/gpu/shader_showcase.flow
> ./flow shader examples/graphics/shader_demo.flow
> ```

## Part 1: Minimal fill

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

Builtins: `uv`, `time`, `resolution`, output `color`. Gallery controls:
`←` / `→` / `Space` cycle · `1`–`9` jump · `Esc` quit.

### 1.1 Pulse helper sketch (browser)

Shader `fn` / `shader fill` need `./flow shader`. The envelope math is ordinary Flow:

```flow
function pulse(t: f64) -> f64 {
    if t < 0.0 { return 0.0 }
    if t > 1.0 { return 0.0 }
    if t < 0.5 { return 2.0 * t }
    return 2.0 * (1.0 - t)
}

function main() -> i32 {
    printf("p0=%f p25=%f p50=%f\n", pulse(0.0), pulse(0.25), pulse(0.5))
    return 0
}
```

### 1.2 Mix / lerp (browser)

```flow
function mix(a: f64, b: f64, t: f64) -> f64 {
    return a * (1.0 - t) + b * t
}

function main() -> i32 {
    printf("mid=%f\n", mix(0.0, 10.0, 0.5))
    printf("near_b=%f\n", mix(0.0, 10.0, 0.9))
    return 0
}
```

### 1.3 Smoothstep (browser)

```flow
function clamp01(x: f64) -> f64 {
    if x < 0.0 { return 0.0 }
    if x > 1.0 { return 1.0 }
    return x
}

function smoothstep(edge0: f64, edge1: f64, x: f64) -> f64 {
    let t: f64 = clamp01((x - edge0) / (edge1 - edge0))
    return t * t * (3.0 - 2.0 * t)
}

function main() -> i32 {
    printf("s=%f\n", smoothstep(0.0, 1.0, 0.5))
    return 0
}
```

### 1.4 UV length (browser)

Distance from screen center — the usual radial field:

```flow
function main() -> i32 {
    let uv_x: f64 = 0.8
    let uv_y: f64 = 0.3
    let dx: f64 = uv_x - 0.5
    let dy: f64 = uv_y - 0.5
    let r2: f64 = dx * dx + dy * dy
    printf("r2=%f\n", r2)
    return 0
}
```

### 1.5 Palette strip (browser)

Map a scalar in `[0,1]` to RGB channels without trig:

```flow
function palette(t: f64) -> i32 {
    let mut x: f64 = t
    if x < 0.0 { x = 0.0 }
    if x > 1.0 { x = 1.0 }
    let r: i32 = (x * 255.0) as i32
    let g: i32 = ((1.0 - x) * 200.0) as i32
    let b: i32 = 80
    return r * 65536 + g * 256 + b
}

function main() -> i32 {
    printf("c0=%d c1=%d\n", palette(0.0), palette(1.0))
    return 0
}
```

## Part 2: Types and math

`f32`, `i32`, `bool`, `vec2`/`vec3`/`vec4`, swizzles, and GLSL-style math
(`sin`, `mix`, `smoothstep`, …). Full table:
[docs/language/shaders.md](../language/shaders.md).

### 2.1 Saturate (browser)

```flow
function saturate(x: f64) -> f64 {
    if x < 0.0 { return 0.0 }
    if x > 1.0 { return 1.0 }
    return x
}

function main() -> i32 {
    printf("%f %f %f\n", saturate(-0.5), saturate(0.3), saturate(2.0))
    return 0
}
```

### 2.2 Step edge (browser)

```flow
function step(edge: f64, x: f64) -> f64 {
    if x < edge { return 0.0 }
    return 1.0
}

function main() -> i32 {
    printf("%f %f\n", step(0.5, 0.2), step(0.5, 0.7))
    return 0
}
```

## Part 3: Next

- [gfx-basics.md](gfx-basics.md) — CPU-side windows and games
- [GPU memory](../library/) / `examples/gpu/` — buffers and kernels (advanced)

## Reference

- [Shader language](../language/shaders.md)
- [`examples/gpu/shader_showcase.flow`](../../examples/gpu/shader_showcase.flow)
