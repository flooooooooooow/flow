# Demo recordings

The visual output in this folder is produced by running real Flow code. It is
not illustration or concept art. CPU `gfx` demos are recorded from the same
drawing API used by native windows; FSL shader demos are rendered through the
same generated Metal fragment shaders used by `./flow shader`.

## Three terms, one hierarchy

The Wiki uses these words deliberately:

- A **demo** is one runnable Flow program or one independently selectable shader
  entry.
- A **gallery** is a visual collection of related demos.
- The **showcase** is the small curated front door that samples several
  galleries. It is not another synonym for the complete example bank.

The canonical collection metadata lives in [`catalog.json`](catalog.json).
`scripts/build_demo_overview.py` turns it into the visual
[Demo Showcase](overview.md), and `scripts/sync_demo_nav.py` uses the same
catalog to keep the Gallery tab organised by rendering, systems-through-time,
and interactive work.

## Naming contract

Every game in `examples/games/` has a gameplay GIF at
`docs/demos/games/<name>.gif`, where `<name>` is the game's file name without
the `_gfx.flow` suffix (`snake_gfx.flow` → `games/snake.gif`). Every example in
`examples/morphogenesis/` has one at `docs/demos/morphogenesis/<name>.gif`.
Every example in `examples/neuro/` has one at `docs/demos/neuro/<name>.gif`.
Every example in `examples/evoleco/` has one at `docs/demos/evoleco/<name>.gif`.
Every example in `examples/planet/` has one at `docs/demos/planet/<name>.gif`.
Every example in `examples/procgen/` has one at `docs/demos/procgen/<name>.gif`.
Numerical clips live at `docs/demos/numerical/<name>.gif`.

FSL gallery entries use the shader-fill name directly:
`shader fill photoreal_gold` → `docs/demos/shaders/photoreal_gold.gif`.
`scripts/build_shader_gallery.py` derives the page from the two photoreal FSL
source files and enforces the current **64 unique shader** contract.

The three original demos also keep their GIFs directly in this folder
(`lorenz.gif`, `tetris.gif`, `2048.gif`); `tetris.gif` and `2048.gif` are copied
into `games/` as well so the games directory covers every game.

The eight software-3D examples in `examples/threed/` have clips at
`docs/demos/threed/<name>.gif`. Those are recorded directly with
`./flow record <program> --frames 90 --gif <path> --width 360 --keys <script>`
rather than through `record_demos.py`; the key script for each is in the table
in [examples/threed/README.md](../../examples/threed/README.md).

## Two real recording paths

### CPU `gfx` recordings

`runtime/gfx_record.c` implements the same API as the windowed backends
(`gfx_macos.m`, `gfx_linux.c`, `gfx_windows.c`), with two differences: it draws
into an off-screen buffer instead of a window, and `flow_gfx_present` writes the
buffer out as a numbered PPM. Because it needs no display, recordings work over
SSH and in CI.

Regenerate the CPU galleries with:

```bash
python3 scripts/record_demos.py                       # all registered gfx demos
python3 scripts/record_demos.py frogger               # just one
python3 scripts/record_demos.py --group morphogenesis # one gallery
python3 scripts/record_demos.py --group neuro         # neuron atlas
python3 scripts/record_demos.py --group evoleco       # evolution / ecology
python3 scripts/record_demos.py --group planet        # cubesphere planet
python3 scripts/record_demos.py --group procgen       # procedural generation
python3 scripts/record_demos.py --group numerical     # FMM and friends
python3 scripts/record_demos.py --check               # missing GIFs + sizes
```

### FSL / Metal recordings

`runtime/shader_record_metal.m` is a deterministic, windowless Metal renderer.
It compiles the MSL produced from the real FSL source, renders the requested
fragment entry into an offscreen `BGRA8Unorm` texture, copies the pixels back,
and writes PPM frames. Animation time is `frame_number / fps`, not wall-clock
time, so scheduling jitter cannot change the captured animation.

```bash
# All 64 photoreal shader entries
python3 scripts/record_shader_gallery.py --group photoreal

# One material study
python3 scripts/record_shader_gallery.py --name photoreal_gold

# Rebuild and validate the generated Wiki page
python3 scripts/build_shader_gallery.py
python3 scripts/build_shader_gallery.py --check --check-assets
```

This path requires macOS with an exposed Metal device. The repository's shader
gallery workflow probes Metal before recording and never substitutes a fake or
software recreation when Metal is unavailable.

## Recording a `gfx` program by hand

```bash
./flow record examples/evolution/lorenz_gfx.flow \
  --frames 300 --out /tmp/frames --gif /tmp/lorenz.gif
```

| Flag | Meaning | Default |
|---|---|---|
| `--frames N` | Stop after N presented frames | `240` |
| `--skip N` | Keep every Nth frame | `1` |
| `--out DIR` | Where frames are written | `frames` |
| `--keys SPEC` | Scripted input (see below) | none |
| `--gif [PATH]` | Encode the frames into a GIF as well | off |
| `--fps N` | GIF frame rate | `20` |
| `--stride N` | Use every Nth recorded frame in the GIF | `2` |
| `--width PX` | Downscale the GIF to this width | `480` |

Each flag has a `FLOW_GFX_RECORD_*` environment variable behind it
(`FLOW_GFX_RECORD_FRAMES`, `_SKIP`, `_DIR`, `_KEYS`), which older scripts still
use. The flags win when both are set.

## Driving interactive demos

Games need input, so the recorder replays a fixed script instead of reading a
keyboard. `--keys` takes a comma-separated list of `first-last:keycode` windows
over frame numbers, where `flow_gfx_key_down` reports the key as held:

```bash
./flow record examples/games/snake_gfx.flow --keys "24-27:124,48-51:126,70-95:125"
```

That holds Right (124) for frames 24–27, Up (126) for 48–51, then Down (125) for
70–95. A single frame can be written `40:49`. Keycodes are the macOS virtual
keycodes the programs already use — see `lib/stdlib/gfx.flow`.

Two things to keep in mind when writing a script:

- Games that do edge detection (`pressed now && !pressed last frame`) act once
  per window, so repeated taps need separate windows with gaps between them.
- Gravity is usually slow. Tetris falls one cell every 48 frames, so the demo
  script uses hard drops (Space, keycode 49) to keep pieces landing.

## Adding a demo or gallery

For a CPU demo, add an entry to `DEMOS` in `scripts/record_demos.py` with the
program path, frame budget and, if interactive, a key script. Frame count,
`skip`, duration and scale should keep the clip readable without turning the
Wiki into an asset dump.

For an FSL photoreal demo, add the `shader fill photoreal_*` entry to the
canonical source file. The gallery generator discovers it automatically; the
asset check then forces a matching real GIF to be recorded before the gallery
can be considered current.

For a new **gallery**, add one record to `docs/demos/catalog.json` with its page,
preview, count, runtime and section. Re-run:

```bash
python3 scripts/build_demo_overview.py
python3 scripts/sync_demo_nav.py
```

The Wiki presentation is intentionally separate from the Markdown source.
`docs/assets/gallery-enhance.js` upgrades the historical image/caption tables
into responsive cards on the Wiki, while GitHub still gets simple readable
Markdown tables.

Because the CPU recorder and its demos are deterministic (fixed RNG seeds and
frame-counted input), a key script is a repeatable flight plan. Simulation demos
need no input; their frame budget simply needs to run past the point where the
interesting structure has formed.

Browse: [Demo Showcase](overview.md) · [Photoreal FSL](shaders.md) ·
[Games](games.md) · [Morphogenesis](morphogenesis.md) · [Neuro](neuro.md) ·
[3D](threed.md) · [Planets](planet.md) · [Procedural Generation](procgen.md) ·
[Evolutionary Biology](evoleco.md) · [Numerical](numerical.md) · [WASM](wasm.md)
