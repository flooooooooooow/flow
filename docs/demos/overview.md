# Galleries

Every clip in these galleries is a recording of a genuinely compiled Flow
program: the frames come from the same drawing calls the native window receives.
Nothing is a mock-up.

The galleries also include a problem-first track: [Solve It the Flow Way](../../examples/flow_way/README.md)
starts from engineering problems and requires the highest-level Flow abstraction that naturally
represents each one. A correct low-level translation is deliberately not the goal.

| Gallery | What it is | GIFs |
|---|---|---|
| [Solve It the Flow Way](../../examples/flow_way/README.md) | Problem-first idioms: pipelines, effects, RT contracts, hybrid dynamics, concurrency, control | runnable |
| [Games](games.md) | Complete, playable games: Snake, Tetris, Asteroids, Flappy, and more | 25 |
| [Morphogenesis](morphogenesis.md) | Reaction-diffusion, Turing patterns, DLA, L-systems, Physarum, wave-2 | 40 |
| [Neurons](neuro.md) | Hodgkin-Huxley, Izhikevich zoo, balanced E/I, Hopfield, CPG gaits | 15 |
| [Opinion Dynamics](social.md) | Voter model, Sznajd, majority rule, and two bounded-confidence models | 5 |
| [3D](threed.md) | A software rasterizer in Flow: solids, voxels, terrain, cameras, physics | 8 |
| [Evolutionary Biology](evoleco.md) | Wright-Fisher through SIR, Muller ratchet, Red Queen, runaway selection | 25 |
| [Planets](planet.md) | A staged cubesphere pipeline: tectonics through biomes | 7 |
| [Procedural Generation](procgen.md) | Noise, heightmaps, caves, WFC, Voronoi, islands, biome tiles | 8 |
| [Numerical Methods](numerical.md) | Adaptive Fast Multipole Method, gated against the direct sum | recorded |
| [Evolution Suite](evolution.md) | Systems evolving through time, each checked against theory | 34 |
| [WebAssembly](wasm.md) | The games and demos running live in a browser | live |

Run any of them natively:

```bash
./flow gfx examples/<path>/<name>_gfx.flow
```

Record any headlessly (no display needed):

```bash
FLOW_GFX_RECORD_FRAMES=240 ./flow record examples/<path>/<name>_gfx.flow
```

Regenerate everything with `python3 scripts/record_demos.py` (see
[demos/README](README.md) for the exact commands, frame budgets, and key
scripts that drive the interactive games).