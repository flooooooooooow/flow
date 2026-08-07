# Planet module

`lib/stdlib/planet.flow` builds a procedural planet as the fixed point of a few
slow processes on an equiangular cubesphere. A planet is not a texture: plates
pile crust up, water takes it away, air carries heat and moisture, and biomes
sort themselves by temperature and rainfall. Every stage is separately runnable
so intermediate state can be inspected and measured.

## Pipeline

Stage numbers match the per-stage timers (`planet_stage_ms`):

```text
1  planet_stage_grid       cubesphere sampling, neighbour graph, cell areas
2  planet_stage_tectonics  plate Voronoi, Euler-pole motion, boundary class
3  planet_stage_elevation  crust dichotomy + fractal relief, sea level
4  planet_stage_erosion    depression filling, D8 routing, stream power
5  planet_stage_climate    insolation, wind bands, orographic rainfall
6  planet_stage_biomes     Whittaker classification
7  planet_stage_hydrology  flow accumulation, rivers, lake filling
```

`planet_generate(seed, plates, erosion_iters)` calls `planet_init()`, seeds the
LCG, then runs the stages in this order: grid, tectonics, elevation, erosion,
climate, hydrology, biomes. Biomes run last so lakes from hydrology are
visible to the classifier; timer slot 6 still belongs to biomes and slot 7 to
hydrology.

## Grid

Cells are the faces of an equiangular cubesphere: six square faces of
`PLANET_FACE_N x PLANET_FACE_N` (default **96 → 55296 cells**), gnomonically
projected with a tangent warp that equalises angular spacing. There is no pole
singularity and no special-cased polar row.

Worst-case area distortion (largest cell solid angle over smallest) is about
**1.40** at N=96 (measured 1.403 in the evidence demo), against 5.196 for a
raw gnomonic cube and unbounded for equirectangular.

Lengths are in kilometres (`PLANET_R_KM = 6371`). Elevations are stored with
sea level at exactly 0 after the land-fraction sea cut. Neighbours are eight
per cell, cached once in `PLANET_CELLS * 8` indices.

Memory at default N is about 6 MB of module-static fields, allocated once by
`planet_init` and never resized.

## Determinism

One 32-bit LCG, seeded by `planet_seed` (also called from
`planet_generate`), drives every random choice. Stages consume it in a fixed
order. The same seed and parameters reproduce a planet bit for bit; the spin
demo gates an elevation checksum across two regenerations.

## Calling the API

```flow
import "stdlib/planet.flow"

function main() -> i32 {
    if !planet_init() { return 1 }
    # Full pipeline. Erosion iters around 24 is enough for Hack's law at N=96.
    if !planet_generate(42 as u32, 12, 24) { return 2 }

    # Or stage-by-stage for inspection:
    # planet_seed(42 as u32)
    # planet_stage_grid()
    # planet_stage_tectonics(12)
    # planet_stage_elevation()
    # planet_stage_erosion(24)
    # planet_stage_climate()
    # planet_stage_hydrology()
    # planet_stage_biomes()

    let distort: f32 = planet_area_max() / planet_area_min()
    let land: f32 = planet_land_fraction()
    let hack: f32 = planet_measure_hack(20000.0)
    let rain: f32 = planet_rain_shadow_ratio(0.4)
    return 0
}
```

Useful accessors after a stage has run:

| Call | Meaning |
|---|---|
| `planet_cells()`, `planet_face_n()` | Grid size |
| `planet_pos_*`, `planet_lat`, `planet_lon` | Cell geometry |
| `planet_cell_at_dir` / `planet_cell_at_lonlat` | Inverse lookup |
| `planet_plate`, `planet_boundary`, `planet_boundary_length_km` | Tectonics |
| `planet_elev`, `planet_is_land`, `planet_land_fraction` | Elevation / sea |
| `planet_hypsometric`, `planet_hypsometric_hist` | Hypsometry |
| `planet_erode_step`, `planet_flow_km2`, `planet_is_river` | Erosion / rivers |
| `planet_measure_hack`, `planet_hack_exponent`, `planet_hack_r2` | Hack's law |
| `planet_temp`, `planet_precip`, `planet_rain_shadow_ratio` | Climate |
| `planet_biome`, `planet_biome_*`, `planet_biome_land_fraction` | Biomes |
| `planet_stage_ms(1..7)`, `planet_total_ms()` | Timings |
| `planet_mesh_corner` | Coarser cubesphere for a globe mesh |

Tunables before generation: `planet_set_target_land` (default 0.29),
`planet_set_relief`, `planet_set_erosion`, `planet_set_river_threshold`.

## Evidence hooks

| Call | Claim |
|---|---|
| `planet_total_area()` | Solid angle → 4π |
| `planet_area_max() / planet_area_min()` | Distortion bound (~1.40 at N=96) |
| `planet_land_fraction()` | Matches `planet_set_target_land` |
| `planet_measure_hack` / `planet_hack_*` | Drainage length–area (Hack) |
| `planet_rain_shadow_ratio(hmin)` | Orographic rain > 1 on slopes |
| `planet_biome_land_fraction` | Whittaker mix on land sums to ~1 |

## What is not modelled

No plate history over Myr (no collision sutures, no seafloor age-depth), no
glaciation, no sediment routing to a marine shelf, no ocean currents, no
seasons (temperature and precipitation are annual means), no orbital
eccentricity or obliquity, no atmosphere chemistry.

## Noise

`planet_noise_*` is a self-contained 3D gradient-noise set kept private to
this module so it has no dependency but libm. General-purpose noise for other
programs lives in [`procgen.flow`](procgen.md) once that lands.

## Examples

Staged gfx demos that gate these measurements live under
[`examples/planet/`](../../examples/planet/README.md). Recorded GIFs:
[demos/planet.md](../demos/planet.md).

```bash
FLOW_HOST=python ./flow gfx examples/planet/planet_evidence.flow
FLOW_HOST=python ./flow record examples/planet/planet_evidence.flow --frames 4 --out /tmp/pl
python3 scripts/record_demos.py --group planet
```

At `PLANET_FACE_N = 96`, a full generate with 24 erosion iterations is about
one second on a laptop (grid ~10 ms, tectonics ~130 ms, elevation ~320 ms,
erosion ~260 ms, climate ~225 ms). The evidence program runs generate once
before the window; live views sample the stored fields.
