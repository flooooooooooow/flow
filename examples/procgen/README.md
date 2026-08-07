# examples/procgen: procedural generation, running live

Eight graphics programs about noise, heightmaps, caves, WFC dungeons, and
biome maps. Each one measures the thing it is demonstrating, prints the
measurement, and returns a nonzero exit code if the check fails, so these are
regression tests that happen to draw pictures. The shared noise API lives in
[`lib/stdlib/procgen.flow`](../../lib/stdlib/procgen.flow).

Recorded clips live in the
[procgen gallery](../../docs/demos/procgen.md).

## Demos

| Example | Model | What it proves |
|---|---|---|
| [`noise_atlas.flow`](noise_atlas.flow) | value / gradient / fBm / ridged / warp | Bit-identical replay; fBm in [-1,1]; ridged in [0,1] |
| [`heightmap_fbm.flow`](heightmap_fbm.flow) | 2D fBm height + sea | Land fraction near target for a fixed seed |
| [`domain_warp.flow`](domain_warp.flow) | plain vs warped coastline | Deterministic replay; mean |diff| or Pearson r < 0.95 |
| [`cave_worms.flow`](cave_worms.flow) | 3D fBm density slices | Porosity in a chosen band at the verify threshold |
| [`wfc_dungeon.flow`](wfc_dungeon.flow) | `stdlib/dynamics/wfc` | Full collapse, socket-valid adjacency |
| [`voronoi_sites.flow`](voronoi_sites.flow) | Worley / site Voronoi | Every cell assigned; mean sites/region = 1 |
| [`island_mask.flow`](island_mask.flow) | radial falloff * fBm | Single connected landmass above sea |
| [`tile_map.flow`](tile_map.flow) | height + moisture biomes | Biome fractions sum to 1; water only below sea |

## Running them

```bash
FLOW_HOST=python ./flow gfx examples/procgen/noise_atlas.flow
FLOW_HOST=python ./flow record examples/procgen/noise_atlas.flow \
  --frames 4 --out /tmp/pg_noise_atlas
python3 scripts/record_demos.py --group procgen
```

Every example labels itself on screen (title, parameters, live measurement).
Number keys switch presets 1-4, `R` reseeds, `P` pauses, Esc quits. Seeding
is a fixed LCG, so a preset replays identically.
