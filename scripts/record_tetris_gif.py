#!/usr/bin/env python3
"""Render docs/demos/tetris.gif — a short demo reel matching tetris_gfx colors.

The live game (`./flow gfx examples/games/tetris_gfx.flow`) opens a native
window; this script bakes a portable GIF from the same palette/layout so the
wiki and README can show motion without a display. Regenerate anytime:

  python3 scripts/record_tetris_gif.py

Requires Pillow.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "demos" / "tetris.gif"

# Mirror examples/games/tetris_gfx.flow
CELL = 28
BOARD_W, BOARD_H = 10, 20
BOARD_X, BOARD_Y = 24, 24
SIDE = 160
COLORS = {
    0: (0, 240, 240),    # I
    1: (240, 240, 0),    # O
    2: (160, 0, 240),    # T
    3: (0, 240, 0),      # S
    4: (240, 0, 0),      # Z
    5: (0, 0, 240),      # J
    6: (240, 160, 0),    # L
}

# 4-cell shapes as (dx, dy) for rotation 0
SHAPES = {
    0: [(0, 1), (1, 1), (2, 1), (3, 1)],  # I
    1: [(1, 0), (2, 0), (1, 1), (2, 1)],  # O
    2: [(1, 0), (0, 1), (1, 1), (2, 1)],  # T
    3: [(1, 0), (2, 0), (0, 1), (1, 1)],  # S
    4: [(0, 0), (1, 0), (1, 1), (2, 1)],  # Z
    5: [(0, 0), (0, 1), (1, 1), (2, 1)],  # J
    6: [(2, 0), (0, 1), (1, 1), (2, 1)],  # L
}


def empty_board():
    return [[-1 for _ in range(BOARD_W)] for _ in range(BOARD_H)]


def place(board, piece, px, py, cells=None):
    cells = cells or SHAPES[piece]
    for dx, dy in cells:
        x, y = px + dx, py + dy
        if 0 <= x < BOARD_W and 0 <= y < BOARD_H:
            board[y][x] = piece


def draw_frame(board, piece, px, py, score: int, next_piece: int) -> Image.Image:
    win_w = BOARD_X + BOARD_W * CELL + SIDE
    win_h = BOARD_Y + BOARD_H * CELL + 40
    img = Image.new("RGB", (win_w, win_h), (18, 18, 28))
    d = ImageDraw.Draw(img)

    # Board background
    bw, bh = BOARD_W * CELL, BOARD_H * CELL
    d.rectangle([BOARD_X - 2, BOARD_Y - 2, BOARD_X + bw + 2, BOARD_Y + bh + 2], fill=(30, 30, 40))
    d.rectangle([BOARD_X, BOARD_Y, BOARD_X + bw, BOARD_Y + bh], fill=(12, 12, 20))

    # Settled cells
    for y in range(BOARD_H):
        for x in range(BOARD_W):
            p = board[y][x]
            if p < 0:
                continue
            c = COLORS[p]
            sx = BOARD_X + x * CELL + 2
            sy = BOARD_Y + y * CELL + 2
            d.rectangle([sx, sy, sx + CELL - 4, sy + CELL - 4], fill=c)
            hi = tuple(min(255, v + 30) for v in c)
            d.rectangle([sx, sy, sx + CELL - 4, sy + 3], fill=hi)

    # Active piece
    c = COLORS[piece]
    for dx, dy in SHAPES[piece]:
        x, y = px + dx, py + dy
        if y < 0:
            continue
        sx = BOARD_X + x * CELL + 2
        sy = BOARD_Y + y * CELL + 2
        d.rectangle([sx, sy, sx + CELL - 4, sy + CELL - 4], fill=c)
        hi = tuple(min(255, v + 40) for v in c)
        d.rectangle([sx, sy, sx + CELL - 4, sy + 3], fill=hi)

    # Side panel
    panel_x = BOARD_X + bw + 20
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 14)
        font_sm = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 12)
    except Exception:
        font = ImageFont.load_default()
        font_sm = font
    d.text((panel_x, BOARD_Y), "FLOW Tetris", fill=(220, 220, 240), font=font)
    d.text((panel_x, BOARD_Y + 28), f"Score  {score}", fill=(180, 180, 200), font=font_sm)
    d.text((panel_x, BOARD_Y + 48), "Next", fill=(140, 140, 160), font=font_sm)
    nc = COLORS[next_piece]
    for dx, dy in SHAPES[next_piece]:
        sx = panel_x + dx * (CELL - 6)
        sy = BOARD_Y + 72 + dy * (CELL - 6)
        d.rectangle([sx, sy, sx + CELL - 10, sy + CELL - 10], fill=nc)

    d.text(
        (panel_x, win_h - 36),
        "examples/games/tetris_gfx.flow",
        fill=(100, 100, 120),
        font=font_sm,
    )
    return img


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    board = empty_board()
    # Pre-fill a junk row look
    for x, p in enumerate([6, 6, 5, 5, 2, 2, 3, 3, 4, 4]):
        board[BOARD_H - 1][x] = p
    for x in (0, 1, 2, 7, 8, 9):
        board[BOARD_H - 2][x] = 1

    frames = []
    score = 0
    # T piece falling + soft moves
    sequence = [
        (2, 3, 0, 0),
        (2, 3, 0, 1),
        (2, 3, 0, 2),
        (2, 4, 0, 3),
        (2, 4, 0, 4),
        (2, 5, 0, 5),
        (2, 5, 0, 6),
        (2, 4, 0, 7),
        (2, 4, 0, 8),
        (2, 4, 0, 9),
        (2, 3, 0, 10),
        (2, 3, 0, 11),
        (2, 3, 0, 12),
        (2, 3, 0, 13),
        (2, 3, 0, 14),
        (2, 3, 0, 15),
    ]
    next_p = 0
    for piece, px, py_base, step in sequence:
        py = py_base + step
        score = step * 10
        frames.append(draw_frame(board, piece, px, py, score, next_p))

    # Lock T and drop an I
    place(board, 2, 3, 15)
    score += 40
    for step, py in enumerate(range(0, 14)):
        frames.append(draw_frame(board, 0, 3, py, score + step * 5, 6))

    frames[0].save(
        OUT,
        save_all=True,
        append_images=frames[1:],
        duration=90,
        loop=0,
        optimize=True,
    )
    print(f"Wrote {OUT} ({len(frames)} frames, {OUT.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
