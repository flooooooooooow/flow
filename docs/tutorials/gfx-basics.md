# Graphics Basics

Native windows via the `gfx` API — create a window, poll input, clear, fill
rects, present. Games and live sims use the same loop.

> [!important] Native only
> Graphics need Cocoa (macOS), SDL2 (Linux/Windows), or the headless recorder.
> There is no browser canvas backend. Every lesson here is a command you run
> locally.

Prerequisites: [structs.md](structs.md), [control.md](control.md).

## Part 1: The frame loop

Illustrative native program (not browser-runnable — needs `./flow gfx`):

```
import "stdlib/gfx.flow"

function main() -> i32 {
    let g: Gfx = gfx_open(640, 480, "hello gfx")
    let mut frame: i32 = 0
    while frame < 300 {
        if !gfx_frame_pump(g) { break }
        gfx_clear(g, 12, 12, 20)
        gfx_fill_rect(g, 40 + frame, 40, 80, 80, 80, 180, 255)
        gfx_present(g)
        frame = frame + 1
    }
    gfx_close(g)
    return 0
}
```

```bash
./flow gfx path/to/your_file.flow
```

`gfx_frame_pump` polls events and returns `false` on Esc / close.
`KEY_LEFT` / `KEY_RIGHT` / … are in [`lib/stdlib/gfx.flow`](../../lib/stdlib/gfx.flow).

### 1.1 Frame counter sketch (browser)

```flow
function main() -> i32 {
    let mut frame: i32 = 0
    let mut x: i32 = 40
    while frame < 60 {
        x = x + 1
        frame = frame + 1
    }
    printf("frames=%d x=%d\n", frame, x)
    return 0
}
```

### 1.2 Bouncing rect (browser)

Simulate a filled rect bouncing off window edges — same state you'd feed `gfx_fill_rect`:

```flow
function main() -> i32 {
    let win_w: i32 = 320
    let win_h: i32 = 240
    let size: i32 = 24
    let mut x: i32 = 40
    let mut y: i32 = 60
    let mut vx: i32 = 3
    let mut vy: i32 = 2
    for frame in 0 to 100 {
        x = x + vx
        y = y + vy
        if x <= 0 {
            x = 0
            vx = 0 - vx
        }
        if x + size >= win_w {
            x = win_w - size
            vx = 0 - vx
        }
        if y <= 0 {
            y = 0
            vy = 0 - vy
        }
        if y + size >= win_h {
            y = win_h - size
            vy = 0 - vy
        }
    }
    printf("x=%d y=%d vx=%d vy=%d\n", x, y, vx, vy)
    return 0
}
```

### 1.3 Key edge detection (browser)

Games often act once per key press, not every frame the key is held:

```flow
function main() -> i32 {
    let mut last: i32 = 0
    let mut moves: i32 = 0
    # Simulated key samples: 0=up, 1=down
    let samples: array<i32, 8> = [0, 1, 1, 0, 0, 1, 0, 1]
    for i in 0 to 8 {
        let now: i32 = samples[i]
        if now == 1 {
            if last == 0 {
                moves = moves + 1
            }
        }
        last = now
    }
    printf("edge_moves=%d\n", moves)
    return 0
}
```

### 1.4 Tile atlas index (browser)

Map a board cell `(col, row)` to a pixel rect — the Tetris / 2048 pattern:

```flow
function main() -> i32 {
    let cell: i32 = 32
    let board_x: i32 = 40
    let board_y: i32 = 40
    let col: i32 = 3
    let row: i32 = 5
    let px: i32 = board_x + col * cell
    let py: i32 = board_y + row * cell
    printf("rect %d,%d %dx%d\n", px, py, cell, cell)
    return 0
}
```

### 1.5 Soft vs hard drop timing (browser)

```flow
function main() -> i32 {
    let fall_delay: i32 = 48
    let mut fall_timer: i32 = 0
    let mut soft: i32 = 0
    let mut hard_rows: i32 = 0
    for frame in 0 to 200 {
        fall_timer = fall_timer + 1
        if soft == 1 {
            if fall_timer >= 2 {
                hard_rows = hard_rows + 1
                fall_timer = 0
            }
        } elif fall_timer >= fall_delay {
            hard_rows = hard_rows + 1
            fall_timer = 0
        }
        if frame == 50 {
            soft = 1
        }
    }
    printf("rows_advanced=%d\n", hard_rows)
    return 0
}
```

## Part 2: Play the demos

```bash
./flow gfx examples/games/tetris_gfx.flow
./flow gfx examples/games/2048_gfx.flow
./flow gfx examples/evolution/lorenz_gfx.flow
```

| Demo | Recording |
|------|-----------|
| Tetris | ![Tetris](../demos/tetris.gif) |
| 2048 | ![2048](../demos/2048.gif) |
| Lorenz | ![Lorenz](../demos/lorenz.gif) |

### 2.1 Score table sketch (browser)

```flow
function line_score(lines: i32) -> i32 {
    if lines == 1 { return 40 }
    if lines == 2 { return 100 }
    if lines == 3 { return 300 }
    if lines == 4 { return 1200 }
    return 0
}

function main() -> i32 {
    let mut score: i32 = 0
    score = score + line_score(1)
    score = score + line_score(4)
    printf("score=%d\n", score)
    return 0
}
```

### 2.2 2048 merge one row (browser)

```flow
function main() -> i32 {
    let mut row: array<i32, 4> = [2, 2, 4, 0]
    # slide left + merge once
    let mut out: array<i32, 4> = [0, 0, 0, 0]
    let mut w: i32 = 0
    for i in 0 to 4 {
        if row[i] != 0 {
            if w > 0 {
                if out[w - 1] == row[i] {
                    out[w - 1] = out[w - 1] * 2
                } else {
                    out[w] = row[i]
                    w = w + 1
                }
            } else {
                out[w] = row[i]
                w = w + 1
            }
        }
    }
    printf("%d %d %d %d\n", out[0], out[1], out[2], out[3])
    return 0
}
```

## Part 3: Headless recording

`./flow record` links against `runtime/gfx_record.c` and writes PPM frames —
no display required (CI-friendly):

```bash
FLOW_GFX_RECORD_DIR=/tmp/frames FLOW_GFX_RECORD_FRAMES=120 \
  ./flow record examples/evolution/lorenz_gfx.flow

# All README demos as GIFs:
python3 scripts/record_demos.py
```

Scripted input for games uses `FLOW_GFX_RECORD_KEYS` — see
[docs/demos/README.md](../demos/README.md).

### 3.1 Frame budget math (browser)

```flow
function main() -> i32 {
    let presented: i32 = 720
    let skip: i32 = 4
    let gif_frames: i32 = presented / skip
    let duration_ms: i32 = 55
    let seconds: i32 = (gif_frames * duration_ms) / 1000
    printf("gif_frames=%d ~%ds\n", gif_frames, seconds)
    return 0
}
```

## Part 4: Next

- [shaders.md](shaders.md) — fullscreen fragment fills (`./flow shader`)
- [evolution.md](evolution.md) — phase portraits on top of gfx
- [Morphogenesis gallery](../../examples/morphogenesis/) — reaction–diffusion etc.

## Reference

- [`lib/stdlib/gfx.flow`](../../lib/stdlib/gfx.flow)
- [`runtime/gfx_macos.m`](../../runtime/gfx_macos.m) / `gfx_linux.c` / `gfx_windows.c`
- [`runtime/gfx_record.c`](../../runtime/gfx_record.c)
