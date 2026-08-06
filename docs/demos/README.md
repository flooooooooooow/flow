# Demo recordings

The GIFs in this folder are produced by running the real Flow programs. They are
not illustrations of what the programs would look like — the pixels come from
the same drawing calls the native window would receive.

## Naming contract

Every game in `examples/games/` has a gameplay GIF at
`docs/demos/games/<name>.gif`, where `<name>` is the game's file name without
the `_gfx.flow` suffix (`snake_gfx.flow` → `games/snake.gif`). Every example in
`examples/morphogenesis/` has one at `docs/demos/morphogenesis/<name>.gif`. The
three original demos also keep their GIFs directly in this folder
(`lorenz.gif`, `tetris.gif`, `2048.gif`); `tetris.gif` and `2048.gif` are
copied into `games/` as well so the games directory covers every game.

The two galleries: [games](games.md) and [morphogenesis](morphogenesis.md).

Regenerate everything with:

```bash
python3 scripts/record_demos.py                      # all demos
python3 scripts/record_demos.py frogger              # just one
python3 scripts/record_demos.py --group morphogenesis # one gallery
python3 scripts/record_demos.py --check              # which GIFs exist, and their sizes
```

## How it works

`runtime/gfx_record.c` implements the same API as the windowed backends
(`gfx_macos.m`, `gfx_linux.c`, `gfx_windows.c`), with two differences: it draws
into an off-screen buffer instead of a window, and `flow_gfx_present` writes the
buffer out as a numbered PPM. Because it needs no display, recordings work over
SSH and in CI.

```bash
# Every demo, encoded straight into docs/demos/
python3 scripts/record_demos.py

# Just one
python3 scripts/record_demos.py tetris

# Which demos are missing a GIF?
python3 scripts/record_demos.py --check
```

## Recording a program by hand

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

## Adding a demo

Add an entry to `DEMOS` in `scripts/record_demos.py` with the program path, a
frame budget, and — if it is interactive — a key script. Frame count, `skip`,
and `duration_ms` together set the length and pace of the GIF; `scale` shrinks
large windows so the file stays small enough for a docs page (games target
320–480 px wide and under ~500 KB, hard cap 1 MB).

Because the recorder and the games are fully deterministic (fixed RNG seeds,
frame-counted input), a key script is a repeatable flight plan. The longer
scripts in `record_demos.py` were derived by simulating a game's exact integer
logic offline and searching for input that plays well — the committed frame
windows encode that play, and re-recording reproduces it bit for bit.

A simulation demo (`morph(...)` in the same file) takes no input, so its only
tuning is the frame budget: `frames` has to run past the point where the
pattern finishes forming, and `skip` sets both the pace and the size. Those
demos also set `resample=Image.NEAREST`, because a grid drawn as blocks of
identical pixels loses both sharpness and compressibility under an
interpolating filter.
