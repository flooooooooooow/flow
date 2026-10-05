# examples/planet: a procedural world as stages

`lib/stdlib/planet.flow` treats a planet as the fixed point of slow processes
(tectonics, elevation, erosion, climate, biomes, hydrology) on an equiangular
cubesphere. These programs run those stages, gate the measurements the module
was written to expose, and draw the result.

Docs: [`docs/library/planet.md`](../../docs/library/planet.md).
Gallery: [`docs/demos/planet.md`](../../docs/demos/planet.md).
Companion noise / WFC demos: [`examples/procgen/`](../procgen/README.md).

## Stage demos

| Example | Stage | What it proves |
|---|---|---|
| `planet_evidence.flow` | full `planet_generate` | Solid angle, area distortion, land fraction, Hack, rain shadow |
| `planet_tectonics.flow` | grid + plates | Every cell plated; boundary length > 0 |
| `planet_elevation.flow` | elevation + sea | Land fraction near target; hypsometric curve |
| `planet_erosion.flow` | stream power | Hack's law on drainage; rivers visible |
| `planet_climate.flow` | climate | Orographic rain_shadow_ratio > 1 |
| `planet_biomes.flow` | Whittaker | Land biome fractions sum to ~1 |
| `planet_spin.flow` | globe view | Same seed reproduces an elev checksum |

## Running

```bash
FLOW_HOST=python ./flow gfx examples/planet/planet_evidence.flow
FLOW_HOST=python ./flow record examples/planet/planet_evidence.flow --frames 4 --out /tmp/pl
python3 scripts/record_demos.py --group planet
```

Generation at `PLANET_FACE_N = 96` (55296 cells) with 24 erosion iterations is
intentional: evidence runs once before the window; the live view then samples
the stored fields. The erosion demo gates on the full 24-iter generate, then
restarts from elevation and steps live so channels grow on screen.

## Measured band (Hack)

On seed 42 / 12 plates / 24 iters the drainage fit lands near h = 0.64 with
R^2 ~ 0.87. Gates use the published Earth-network band h in [0.45, 0.70] and
R^2 > 0.75 (Hack 1957; Rigon et al. 1996).
