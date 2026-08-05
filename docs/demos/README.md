# Demo recordings

The GIFs in this folder are produced by running the real Flow programs. They are
not illustrations of what the programs would look like — the pixels come from
the same drawing calls the native window would receive.

## Naming contract

Every game in `examples/games/` has a gameplay GIF at
`docs/demos/games/<name>.gif`, where `<name>` is the game's file name without
the `_gfx.flow` suffix (`snake_gfx.flow` → `games/snake.gif`). The three
original demos also keep their GIFs directly in this folder (`lorenz.gif`,
`tetris.gif`, `2048.gif`); `tetris.gif` and `2048.gif` are copied into
`games/` as well so the games directory covers every game.

Regenerate everything with:

```bash
python3 scripts/record_demos.py           # all demos, straight into docs/demos/
python3 scripts/record_demos.py frogger   # just one
python3 scripts/record_demos.py --check   # list which GIFs exist and their sizes
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
FLOW_GFX_RECORD_DIR=/tmp/frames \
FLOW_GFX_RECORD_FRAMES=300 \
./flow record examples/evolution/lorenz_gfx.flow
```

| Variable | Meaning | Default |
|---|---|---|
| `FLOW_GFX_RECORD_DIR` | Where frames are written | `frames` |
| `FLOW_GFX_RECORD_FRAMES` | Stop after N presented frames | `240` |
| `FLOW_GFX_RECORD_SKIP` | Keep every Nth frame | `1` |
| `FLOW_GFX_RECORD_KEYS` | Scripted input (see below) | none |

## Driving interactive demos

Games need input, so the recorder replays a fixed script instead of reading a
keyboard. `FLOW_GFX_RECORD_KEYS` is a comma-separated list of
`first-last:keycode` windows over frame numbers, where `flow_gfx_key_down`
reports the key as held:

```bash
FLOW_GFX_RECORD_KEYS="24-27:124,48-51:126,70-95:125"
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
