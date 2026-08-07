# Procgen module

`lib/stdlib/procgen.flow` is a self-contained 2D/3D gradient and value noise
library for general procedural content. A procedural field is a pure function
of coordinates and a seed: the same seed and sample point always return the
same `f32`, with no tables and no allocation.

Related: [planet module](planet.md) (cubesphere pipeline),
[procgen gallery](../demos/procgen.md),
[examples/procgen](../../examples/procgen/README.md).

## API

| Function | Role |
|---|---|
| `procgen_seed(s)` | Set the 32-bit seed used by every hash |
| `procgen_get_seed()` | Read the current seed |
| `procgen_hash(ix, iy, iz, salt)` | Integer hash mixed with the seed |
| `procgen_noise2` / `noise3` | Gradient (Perlin-style) noise ~[-1, 1] |
| `procgen_fbm2` / `fbm3` | Fractional Brownian motion, normalised ~[-1, 1] |
| `procgen_ridged2` / `ridged3` | Ridged multifractal in [0, 1] |
| `procgen_warped2` | Domain-warped fBm (2D) |
| `procgen_value2` | Value noise in [0, 1] |

## Determinism

One module-static `u32` seed. Hashing folds the seed in, so reseeding moves
every field. There is no global LCG advance inside the noise calls; callers
that need discrete random choices keep their own LCG. The noise atlas and
domain-warp demos gate bit-identical replay of the same seed and coordinates.

## Domain warp

`procgen_warped2(x, y, octaves, warp, salt)` samples fBm at a point displaced
by a low-octave noise field. Warp folds coastlines and can *increase* local
gradients (space is stretched and compressed), so "lower high-frequency power"
is not a reliable claim. Honest gates check determinism plus field difference
(mean absolute deviation or correlation).

## Calling the API

```flow
import "stdlib/procgen.flow"

function main() -> i32 {
    procgen_seed(424242)
    let h: f32 = procgen_fbm2(1.0, 2.0, 5, 3)
    let w: f32 = procgen_warped2(1.0, 2.0, 5, 0.45, 3)
    return 0
}
```
