#!/usr/bin/env python3
"""Record docs/demos/*.gif by running the real Flow programs headlessly.

Each demo is compiled with `./flow record`, which links the program against
runtime/gfx_record.c instead of a windowing backend. The program then draws
into an off-screen buffer and writes every presented frame as a PPM, so the
resulting GIF is genuine output from the compiled Flow program rather than a
re-creation of it. No display is required, which means this also works in CI.

  python3 scripts/record_demos.py            # all demos
  python3 scripts/record_demos.py lorenz     # one demo
  python3 scripts/record_demos.py --group morphogenesis

Naming contract: every game in examples/games/ has a GIF at
docs/demos/games/<name>.gif, and every example in examples/morphogenesis/ has
one at docs/demos/morphogenesis/<name>.gif. The three original demos (lorenz,
tetris, 2048) also keep their GIFs directly in docs/demos/; tetris.gif and
2048.gif are copied into docs/demos/games/ so the games directory is complete.

Interactive demos are driven by `flow record --keys`, a list of
`first-last:keycode` windows over frame numbers (see runtime/gfx_record.c).
Because the recorder and every game are fully deterministic (fixed RNG seeds,
frame-counted input), several of the longer scripts below were derived by
simulating the game's exact integer logic offline and searching for input that
plays well; the frame windows encode that play. Requires Pillow.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "docs" / "demos"
GAMES_DIR = OUT_DIR / "games"
MORPH_DIR = OUT_DIR / "morphogenesis"

# macOS virtual keycodes, matching lib/stdlib/gfx.flow.
KEY_LEFT, KEY_RIGHT, KEY_DOWN, KEY_UP = 123, 124, 125, 126
KEY_SPACE = 49
KEY_F = 3       # minesweeper: flag
KEY_N = 45      # chetris: skip chess move
L, R, D, U, SP = KEY_LEFT, KEY_RIGHT, KEY_DOWN, KEY_UP, KEY_SPACE


def hold(frame: int, key: int, length: int = 3) -> str:
    """A key held from `frame` for `length` frames."""
    return f"{frame}-{frame + length - 1}:{key}"


def taps(seq: list[tuple[int, int]], length: int = 2) -> str:
    """Short presses: one `length`-frame window per (frame, key) pair.

    Games do edge detection, so each press needs its own window with a gap
    before the same key is pressed again.
    """
    return ",".join(hold(f, k, length) for f, k in seq)


class Tapper:
    """Builds an edge-press schedule while tracking the current frame."""

    def __init__(self, frame: int, gap: int = 7):
        self.frame = frame
        self.gap = gap
        self.seq: list[tuple[int, int]] = []

    def tap(self, *keys: int, gap: int | None = None) -> "Tapper":
        for k in keys:
            self.seq.append((self.frame, k))
            self.frame += gap if gap is not None else self.gap
        return self

    def wait(self, frames: int) -> "Tapper":
        self.frame += frames
        return self

    def keys(self) -> str:
        return taps(self.seq)


def tetris_script() -> str:
    """A scripted playthrough: nudge sideways, rotate, then hard-drop.

    The natural fall delay is 48 frames per cell, far too slow to watch, so the
    demo leans on hard drops to keep pieces landing every couple of seconds.
    """
    windows: list[str] = []
    frame = 12
    moves = [
        (KEY_LEFT, 2), (KEY_UP, 1),
        (KEY_RIGHT, 3), (KEY_UP, 1),
        (KEY_LEFT, 3),
        (KEY_RIGHT, 1), (KEY_UP, 2),
        (KEY_LEFT, 4),
        (KEY_RIGHT, 2), (KEY_UP, 1),
        (KEY_LEFT, 1),
    ]
    for key, repeats in moves:
        for _ in range(repeats):
            windows.append(hold(frame, key))
            frame += 7  # gap so the game's edge detection sees a fresh press
        windows.append(hold(frame, KEY_SPACE))
        frame += 12
    return ",".join(windows)


def g2048_script() -> str:
    windows: list[str] = []
    frame = 10
    for key in [KEY_LEFT, KEY_DOWN, KEY_RIGHT, KEY_DOWN, KEY_LEFT, KEY_UP,
                KEY_RIGHT, KEY_DOWN, KEY_LEFT, KEY_DOWN, KEY_RIGHT, KEY_UP,
                KEY_LEFT, KEY_DOWN, KEY_RIGHT, KEY_DOWN]:
        windows.append(hold(frame, key))
        frame += 14
    return ",".join(windows)


# ---------------------------------------------------------------------------
# Scripts derived by simulating the game's exact deterministic logic offline
# (same RNG constants, same integer math, same frame ordering). Each string
# is a fixed flight plan the real game then follows on record.
# ---------------------------------------------------------------------------

# Snake: start, then steer along greedily planned paths that eat 5 foods.
SNAKE_KEYS = (
    "8-9:49,12-14:126,21-23:123,66-68:126,111-113:124,237-239:125,"
    "273-275:124,291-293:126,335-337:123,415-417:125,447-449:123,"
    "463-465:125,519-521:124"
)

# Flappy: flap timings that thread the bird through the first pipes.
FLAPPY_KEYS = (
    "8:49,19:49,30:49,41:49,52:49,79:49,106:49,133:49,160:49,187:49,214:49,"
    "241:49,291:49,317:49,344:49,385:49,411:49,438:49,465:49,476:49,487:49,"
    "498:49,509:49,520:49,531:49,555:49"
)

# Pong: paddle holds that return every serve; the whole clip is one rally.
PONG_KEYS = (
    "8:49,184-187:126,249-250:126,300-301:126,351-352:126,376-385:125,"
    "559-585:126,595-597:125,605-607:125,615-617:125"
)

# Breakout: the paddle shadows the ball; no life is lost in the clip.
BREAKOUT_KEYS = (
    "8:49,81-82:123,95-96:123,109-110:123,123-124:123,137-138:123,"
    "151-152:123,166-167:123,180-181:123,194-195:123,208-209:123,"
    "222-223:123,236-237:123,251-252:123,265-266:123,449-450:123"
)

# Frogger: a searched hop plan that crosses road and river into a home slot
# twice, riding logs on the way.
FROGGER_KEYS = (
    "8-9:49,36-37:126,44-45:123,52-53:126,60-61:126,68-69:123,76-77:126,"
    "84-85:124,92-93:126,100-101:126,108-109:124,116-117:124,124-125:124,"
    "132-133:124,140-141:126,148-149:126,156-157:126,164-165:123,172-173:126,"
    "180-181:126,188-189:126,196-197:124,204-205:126,212-213:124,220-221:123,"
    "228-229:126,236-237:126,244-245:126,252-253:124,260-261:126,268-269:126,"
    "276-277:126,284-285:126,292-293:123,300-301:124,308-309:123,316-317:126,"
    "324-325:123,332-333:124,340-341:126,348-349:126,356-357:126"
)

# Jumper: steering holds from a bounce-by-bounce search; climbs the tower
# without ever falling off the bottom.
JUMPER_KEYS = (
    "8:49,8-22:124,28-40:123,42-71:124,76-108:123,113-126:124,256-269:123,"
    "274-287:124,302-340:123,345-359:124,369-372:123,386-421:124,424-457:123,"
    "462-479:123,485-496:124,500-518:123,522-568:124,573-578:124,583-596:123"
)

# Lane racer: lane changes that dodge every car (with a few scenic weaves).
LANE_RACER_KEYS = (
    "8-9:49,70-71:124,150-151:124,208-209:123,314-315:124,394-395:123,"
    "402-403:123,482-483:124,490-491:124,547-548:123"
)

# Simon: watches each playback, then echoes the pad sequence for 5 rounds
# (the sequence is fixed by the game's RNG seed).
SIMON_KEYS = (
    "89:123,204:123,213:125,354:123,363:125,372:124,535:123,544:125,553:124,"
    "562:126,743:123,752:125,761:124,770:126,779:123"
)

# Othello: six human moves placed on legal cells, timed around the flip
# animations and the AI's replies.
OTHELLO_KEYS = (
    "6-7:49,80-81:126,85-86:126,90-91:49,164-165:123,169-170:123,174-175:125,"
    "179-180:125,184-185:49,268-269:124,273-274:124,278-279:124,283-284:124,"
    "288-289:124,293-294:49,372-373:125,377-378:125,382-383:49,471-472:123,"
    "476-477:123,481-482:49"
)

# Match-3: seven valid swaps (cursor, select, swap) with cascade timing.
MATCH3_KEYS = (
    "8-9:125,13-14:49,18-19:124,50-51:123,55-56:125,60-61:49,65-66:124,"
    "97-98:49,102-103:125,134-135:126,139-140:126,144-145:49,149-150:125,"
    "181-182:123,186-187:49,191-192:125,223-224:126,228-229:49,233-234:124,"
    "265-266:126,270-271:126,275-276:49,280-281:125"
)

# Minesweeper: opening click floods a large region, then flags three known
# mines, reveals eight safe cells, and ends on a deliberate wrong click so
# the lose state (all mines shown) plays out.
MINESWEEPER_KEYS = (
    "9-10:123,15-16:125,21-22:124,27-28:126,33-34:49,47-48:123,53-54:123,"
    "59-60:125,65-66:3,77-78:124,83-84:126,89-90:126,95-96:126,101-102:126,"
    "107-108:3,119-120:123,125-126:125,131-132:3,143-144:126,149-150:49,"
    "161-162:126,167-168:49,179-180:123,185-186:126,191-192:49,203-204:126,"
    "209-210:49,221-222:126,227-228:49,239-240:126,245-246:49,257-258:123,"
    "263-264:49,275-276:123,281-282:49,293-294:123,299-300:125,315-316:49"
)


# ---------------------------------------------------------------------------
# Hand-built scripts for turn-based games (no timers to race against).
# ---------------------------------------------------------------------------

def checkers_script() -> str:
    """Seven-move opening for both hotseat players with three forced jumps.

    Cursor starts on red's man at (2,5); every move is `navigate, select,
    navigate, place`. The jumps arise naturally from the forced-capture rule.
    """
    t = Tapper(12)
    moves = [
        # (nav to piece, nav to target)
        ([], [R, U]),                # red  (2,5) -> (3,4)
        ([R, R, U, U], [L, D]),      # slate (5,2) -> (4,3)
        ([L, D], [R, R, U, U]),      # red  (3,4) x (4,3) -> (5,2)
        ([L, U], [R, R, D, D]),      # slate (4,1) x (5,2) -> (6,3)
        ([D, D], [L, U]),            # red  (6,5) -> (5,4)
        ([L, L, U, U], [R, D]),      # slate (3,2) -> (4,3)
        ([R, D], [L, L, U, U]),      # red  (5,4) x (4,3) -> (3,2)
    ]
    for nav_piece, nav_target in moves:
        t.tap(*nav_piece)
        t.tap(SP)
        t.tap(*nav_target)
        t.tap(SP)
        t.wait(10)
    return t.keys()


def sokoban_script() -> str:
    """Pushes every box home across all five levels, ending on the victory
    screen. Between levels the game shows a 60-frame LEVEL DONE banner."""
    levels = [
        [R, R],                       # L1: one straight push
        [L, R, D, L],                 # L2: two boxes left
        [R, R, R],                    # L3: through the gap
        [U, D, R, R, R],              # L4: one up, one right
        [U, D, L, U, D, R, R, U],     # L5: three boxes up
    ]
    t = Tapper(12, gap=9)
    for i, presses in enumerate(levels):
        t.tap(*presses)
        if i < len(levels) - 1:
            t.wait(66)  # LEVEL DONE banner, then the next level loads
    return t.keys()


def hanoi_script() -> str:
    """Selects 3 disks on the title screen and plays the optimal 7-move
    solve. Each drop runs a 14-frame animation before input resumes."""
    solve = [(0, 2), (0, 1), (2, 1), (0, 2), (1, 0), (1, 2), (0, 2)]
    t = Tapper(10)
    t.tap(L)        # 4 -> 3 disks
    t.tap(SP)       # start
    t.wait(6)
    cursor = 0
    for src, dst in solve:
        while cursor != src:
            t.tap(R if src > cursor else L)
            cursor += 1 if src > cursor else -1
        t.tap(SP)   # pick up
        while cursor != dst:
            t.tap(R if dst > cursor else L)
            cursor += 1 if dst > cursor else -1
        t.tap(SP)   # drop
        t.wait(22)  # drop animation + a beat
    return t.keys()


def chetris_script() -> str:
    """Chess + Tetris turns for both players: place a tetromino (soft drops,
    Space locks), then move that player's king, four times over."""
    t = Tapper(12, gap=6)
    turns = [
        # (tetromino moves, chess cursor to piece, chess cursor to target)
        ([L, L, U] + [D] * 6, [D, D, D], [U]),       # white: king e1 up
        ([R, R] + [D] * 6, [U, U, U, U], [D]),       # black: king e8 down
        ([L] + [D] * 6, [D, D], [L]),                # white: king sidesteps
        ([R, R, R] + [D] * 6, None, None),           # black: skips chess (N)
    ]
    for tetro, nav_piece, nav_target in turns:
        t.tap(*tetro)
        t.tap(SP)       # lock the tetromino -> chess phase
        t.wait(8)
        if nav_piece is None:
            t.tap(KEY_N)
        else:
            t.tap(*nav_piece)
            t.tap(SP)   # select
            t.tap(*nav_target)
            t.tap(SP)   # move
        t.wait(10)
    return t.keys()


def lightsout_script() -> str:
    """Cursor walk pressing cells; every press toggles a plus-shape."""
    t = Tapper(14, gap=8)
    plan = [
        ([], SP), ([L], SP), ([U], SP), ([R, R], SP), ([D, D], SP),
        ([L, L], SP), ([U, R], SP), ([R, D], SP),
    ]
    for nav, press in plan:
        t.tap(*nav)
        t.tap(press)
        t.wait(18)
    return t.keys()


def connect4_script() -> str:
    """Six human drops with pauses for the falling-disc animation and the
    AI's reply (the AI thinks for 24 frames, then its disc falls)."""
    t = Tapper(12)
    drops = [[], [L], [R, R], [], [L], [R]]
    for nav in drops:
        t.tap(*nav)
        t.tap(SP)
        t.wait(80)  # our disc falls, AI thinks, AI disc falls
    return t.keys()


def maze_chase_script() -> str:
    """Held-key steering through the maze: bottom corridor to the power
    pellet, up the left wall to the second pellet, then across the top.
    Direction changes overlap on purpose; a wanted turn only happens where
    the maze opens, so early presses are safe."""
    return ",".join([
        hold(8, SP, 2),
        "10-95:123",    # left along the bottom row to the power pellet
        "96-190:126",   # up the left corridor, eating the corner pellet
        "187-236:124",  # right along the top row
        "237-254:125",  # down the col-8 alley
        "255-345:124",  # right along row 3
    ])


def invaders_script() -> str:
    """Strafe under the alien grid, firing whenever the last shot lands."""
    parts = [hold(8, SP, 2)]
    # movement: sweep left, right, left, right, left
    for a, b, k in [(24, 78, L), (100, 168, R), (190, 248, L),
                    (270, 338, R), (360, 420, L), (440, 480, R)]:
        parts.append(f"{a}-{b}:{k}")
    # fire: one bullet may be alive at a time; tap steadily
    for f in range(18, 500, 26):
        parts.append(hold(f, SP, 2))
    return ",".join(parts)


def asteroids_script() -> str:
    """Rotate-thrust-fire loops. Space is held for long stretches; the game
    autofires on a cooldown while it is down."""
    parts = [hold(8, SP, 2), "20-200:49", "230-430:49", "460-520:49"]
    moves = [
        (24, 48, L), (56, 72, U), (90, 112, L), (120, 136, U),
        (160, 186, R), (194, 210, U), (240, 268, L), (276, 292, U),
        (320, 348, R), (356, 372, U), (400, 428, L), (436, 452, U),
        (470, 500, R),
    ]
    for a, b, k in moves:
        parts.append(f"{a}-{b}:{k}")
    return ",".join(parts)


def missile_script() -> str:
    """Sweeps the crosshair across the sky, firing interceptors that blossom
    into blast rings over the incoming missiles."""
    parts = [hold(8, SP, 2)]
    sweeps = [
        (20, 52, [L, U]), (66, 66, [SP]),
        (90, 140, [R]), (150, 150, [SP]),
        (170, 210, [L, D]), (220, 220, [SP]),
        (240, 280, [R, U]), (290, 290, [SP]),
        (310, 350, [L]), (356, 356, [SP]),
        (380, 410, [R, D]), (416, 416, [SP]),
    ]
    for a, b, keys in sweeps:
        for k in keys:
            if k == SP:
                parts.append(hold(a, SP, 2))
            else:
                parts.append(f"{a}-{b}:{k}")
    return ",".join(parts)


@dataclass
class Demo:
    name: str
    program: str
    caption: str
    frames: int = 240
    skip: int = 1
    duration_ms: int = 60
    scale: float = 1.0
    keys: str = ""
    trim_leading: int = 0
    # Crop away margins the program never draws into, so the subject fills the
    # clip. Simulations in particular tend to use a fraction of their window.
    crop: bool = False
    colors: int = 64
    # LANCZOS suits the games, whose art is drawn at window resolution. A
    # simulation drawn as a grid of N x N pixel blocks is better off with
    # NEAREST: interpolation smears every block edge into a gradient, which
    # both softens the picture and roughly doubles the encoded size, because
    # the GIF can no longer reuse runs of identical pixels.
    resample: int = Image.LANCZOS
    env: dict[str, str] = field(default_factory=dict)
    # Where the GIF goes, relative to docs/demos/.
    subdir: str = "games"
    # Legacy demos keep a copy at docs/demos/<name>.gif too.
    also_root: bool = False


def game(name: str, keys: str, frames: int, caption: str, scale: float,
         skip: int = 2, duration_ms: int = 33, colors: int = 64) -> Demo:
    return Demo(
        name=name,
        program=f"examples/games/{name}_gfx.flow",
        caption=caption,
        frames=frames,
        skip=skip,
        duration_ms=duration_ms,
        scale=scale,
        keys=keys,
        colors=colors,
    )


def morph(name: str, frames: int, skip: int, caption: str,
          duration_ms: int = 60, colors: int = 64,
          scale: float = 0.86, keys: str = "") -> Demo:
    """A morphogenesis clip: no input, one full formation, then loop.

    Every example draws into the same 512x592 window, so one scale suits all
    of them (0.86 -> 440 px wide). `frames` and `skip` are the two knobs that
    matter: the product has to cover the whole of the formation and stop
    before an example that restarts itself begins its second run.
    """
    return Demo(
        name=name,
        program=f"examples/morphogenesis/{name}.flow",
        caption=caption,
        frames=frames,
        skip=skip,
        duration_ms=duration_ms,
        scale=scale,
        colors=colors,
        keys=keys,
        subdir="morphogenesis",
        resample=Image.NEAREST,
    )


DEMOS: list[Demo] = [
    Demo(
        name="lorenz",
        program="examples/evolution/lorenz_gfx.flow",
        caption="Lorenz attractor — `flow` block with an RK4 solver, stepped per frame",
        # The trajectory needs ~30 time units to visit both lobes, and the demo
        # advances 0.015 per frame, so a short recording only ever shows one wing.
        frames=2000,
        skip=10,
        duration_ms=55,
        scale=0.65,
        crop=True,
        colors=32,
        subdir="",
    ),
    Demo(
        name="tetris",
        program="examples/games/tetris_gfx.flow",
        caption="Tetris — full game loop, scripted input, native gfx backend",
        frames=320,
        skip=3,
        duration_ms=80,
        scale=0.6,
        keys=tetris_script(),
        subdir="",
        also_root=True,
    ),
    Demo(
        name="2048",
        program="examples/games/2048_gfx.flow",
        caption="2048 — grid logic and tile merging",
        frames=260,
        skip=3,
        duration_ms=90,
        scale=0.65,
        keys=g2048_script(),
        subdir="",
        also_root=True,
    ),
    # ---- action ----
    game("snake", SNAKE_KEYS, 560,
         "Snake — planned path eats five foods", 0.6),
    game("pong", PONG_KEYS, 620,
         "Pong — one long rally against the tracking AI", 0.6),
    game("breakout", BREAKOUT_KEYS, 640,
         "Breakout — the paddle shadows the ball through the brick wall", 0.68),
    game("asteroids", asteroids_script(), 540,
         "Asteroids — rotate, thrust, autofire through the first wave", 0.5,
         skip=3, duration_ms=50, colors=32),
    game("invaders", invaders_script(), 500,
         "Space Invaders — strafing under the marching grid", 0.58,
         skip=3, duration_ms=45, colors=32),
    game("flappy", FLAPPY_KEYS, 560,
         "Flappy — flap timings that thread the pipes", 0.67,
         skip=4, duration_ms=65, colors=32),
    game("frogger", FROGGER_KEYS, 430,
         "Frogger — road, river, and two home slots", 0.63,
         skip=4, duration_ms=65, colors=40),
    game("missile", missile_script(), 460,
         "Missile Command — interceptors and blast rings", 0.65),
    game("maze_chase", maze_chase_script(), 400,
         "Maze Chase — pellet run past three ghost AIs", 0.68),
    game("lane_racer", LANE_RACER_KEYS, 560,
         "Lane Racer — weaving through traffic without a scratch", 0.67,
         skip=4, duration_ms=60, colors=40),
    game("jumper", JUMPER_KEYS, 620,
         "Jumper — searched steering climbs the platform tower", 0.75),
    # ---- puzzle ----
    game("minesweeper", MINESWEEPER_KEYS, 400,
         "Minesweeper — flood reveal, flags, and one fatal click", 0.68),
    game("sokoban", sokoban_script(), 540,
         "Sokoban — all five levels solved", 0.75),
    game("match3", MATCH3_KEYS, 380,
         "Match-3 — seven swaps with cascade chains", 0.8),
    game("lightsout", lightsout_script(), 300,
         "Lights Out — plus-shaped toggles chasing the dark", 0.72),
    game("hanoi", hanoi_script(), 440,
         "Tower of Hanoi — the optimal 7-move solve on 3 disks", 0.65),
    game("simon", SIMON_KEYS, 800,
         "Simon — five echoed rounds, straight from the seeded sequence", 0.6,
         skip=3, duration_ms=45),
    # ---- board ----
    game("connect4", connect4_script(), 520,
         "Connect Four — six drops against the blocking AI", 0.7),
    game("othello", OTHELLO_KEYS, 660,
         "Othello — legal placements and flip animations against the AI", 0.6),
    game("checkers", checkers_script(), 460,
         "Checkers — hotseat opening with three forced jumps", 0.6),
    game("chetris", chetris_script(), 560,
         "Chetris — tetromino locks and king moves, turn by turn", 0.6),
]


# ---------------------------------------------------------------------------
# Morphogenesis. These take no input at all, so the tuning is entirely in the
# frame budget: the clip has to start before the pattern exists and end after
# it does. Several examples finish, hold, and then reseed themselves; for
# those the budget stops inside the hold so the loop point is the finished
# form rather than a restart mid-clip. The per-clip numbers below were read
# off a change-over-time curve of the recorded frames (mean absolute pixel
# difference against frame 0 and against the previous frame).
# ---------------------------------------------------------------------------

MORPH_DEMOS: list[Demo] = [
    # ---- reaction-diffusion and continuous fields ----
    # Every cell of the field changes every frame in this group, so the GIF
    # cannot reuse anything between frames: the budget is roughly 14 KB per
    # kept frame at 16 colours. Hence ~50 kept frames, held longer on screen.
    morph("gray_scott", 240, 4,
          "Gray-Scott — a seeded blob divides into a field of solitons",
          duration_ms=80, colors=12),
    morph("brusselator", 152, 4,
          "Brusselator — noise becomes a hexagonal lattice at the predicted lambda",
          duration_ms=100, colors=12),
    morph("turing_spots", 200, 4,
          "Turing spots — noise resolves into a hexagonal lattice of peaks",
          duration_ms=80, colors=24),
    morph("turing_stripes", 240, 4,
          "Turing stripes — the same system, saturated, so ridges form",
          duration_ms=80, colors=12),
    morph("belousov", 320, 10,
          "Belousov-Zhabotinsky — four broken waves wind into spirals",
          duration_ms=120, colors=10),
    morph("swift_hohenberg", 400, 8,
          "Swift-Hohenberg — one wavelength survives and anneals into rolls",
          duration_ms=80, colors=12),
    morph("cahn_hilliard", 800, 20,
          "Cahn-Hilliard — a quenched mixture unmixes and coarsens",
          duration_ms=95, colors=12),
    # heat_morph rethrows its noise every 200 steps; stop inside the first.
    morph("heat_morph", 200, 4,
          "Perona-Malik diffusion — noise dissolves, boundaries sharpen",
          duration_ms=80, colors=24),
    # ---- growth and aggregation ----
    # This group only redraws near the growth front, so the encoder stores a
    # few hundred changed pixels per frame and the clips can run long.
    # dla finishes near frame 140 and holds 120 frames before reseeding.
    morph("dla", 180, 2,
          "Diffusion-limited aggregation — a dendrite grows from one seed",
          duration_ms=55, colors=48),
    # eden fills the dish by frame ~180, then holds.
    morph("eden_growth", 200, 3,
          "Eden growth — a compact colony with a rough KPZ front",
          duration_ms=65, colors=24),
    # The midrib is up by frame ~80; the rest of the budget is the crown
    # filling in with higher-order veins, which is the half worth watching.
    morph("branching_vessels", 330, 3,
          "Space colonization — a midrib forks into leaf venation",
          duration_ms=55, colors=48),
    # the plant is fully revealed by frame ~104 and restarts at ~240.
    morph("lsystem_plant", 130, 1,
          "L-system plant — a turtle walks a longer prefix each frame",
          duration_ms=50, colors=48),
    # the tree finishes growing around frame 56 and then only the wind moves,
    # which redraws every branch, so this one is priced like a field.
    morph("lsystem_tree", 200, 5,
          "L-system tree — seven levels of 3D branching, then wind",
          duration_ms=90, colors=16),
    # coral tops out near frame 76 and restarts at ~180.
    morph("coral_ballistic", 110, 1,
          "Ballistic deposition — shadowing grows porous coral columns",
          duration_ms=50, colors=32),
    # ---- cellular and discrete ----
    morph("cyclic_ca", 210, 7,
          "Cyclic CA — noise, then debris, then a tiling of spiral cores",
          duration_ms=120, colors=10),
    morph("life_variants", 400, 12,
          "Life variants — a soup thins into gliders and still lifes",
          duration_ms=110, colors=12),
    # the crystal stops growing near frame 60 and restarts at ~168.
    morph("hexagonal_ca", 110, 1,
          "Reiter snowflake — six-fold dendrites off one frozen cell",
          duration_ms=50, colors=48),
    # wfc completes near frame 100 and restarts at ~240.
    morph("wfc_growth", 130, 1,
          "Wave function collapse — a circuit resolves out of possibility",
          duration_ms=50, colors=48),
    # ---- biological pattern ----
    morph("slime_mold", 500, 12,
          "Physarum agents — a trail map becomes a transport network",
          duration_ms=100, colors=12),
    morph("cell_sorting", 600, 8,
          "Differential adhesion — a 50/50 mixture sorts into layers",
          duration_ms=70, colors=16),
    # one full head-to-tail axis; the embryo restarts around frame 200.
    morph("somite_clock", 180, 2,
          "Clock and wavefront — equal somites laid down one at a time",
          duration_ms=60, colors=48),
]

DEMOS += MORPH_DEMOS


def last_scripted_frame(keys: str) -> int:
    if not keys:
        return 0
    return max(int(w.split(":")[0].split("-")[-1]) for w in keys.split(","))


def warn_about_pacing(demo: Demo) -> None:
    """The frame budget and the input script have to line up or the clip drags."""
    end = last_scripted_frame(demo.keys)
    if not end:
        return
    if end > demo.frames:
        print(f"  ! input script runs to frame {end} but the budget stops at "
              f"{demo.frames}; the last moves will never be played")
    elif demo.frames - end > demo.frames * 0.35:
        print(f"  ! input script ends at frame {end} of {demo.frames}; "
              f"the clip will sit idle for the remainder")


def record(demo: Demo, frame_dir: Path) -> int:
    env = dict(os.environ)
    env.update(demo.env)

    cmd = ["./flow", "record", demo.program,
           "--frames", str(demo.frames),
           "--skip", str(demo.skip),
           "--out", str(frame_dir)]
    if demo.keys:
        cmd += ["--keys", demo.keys]

    print(f"  running {demo.program} …")
    result = subprocess.run(
        cmd, cwd=ROOT, env=env, text=True, capture_output=True, timeout=1800,
    )
    if result.returncode != 0:
        sys.stderr.write(result.stdout[-2000:])
        sys.stderr.write(result.stderr[-2000:])
        raise SystemExit(f"recording failed for {demo.name}")
    for line in result.stderr.splitlines():
        if line.startswith("[gfx-record]"):
            print(f"  {line}")
    return len(list(frame_dir.glob("*.ppm")))


def content_box(paths: list[Path], pad: int = 12) -> tuple[int, int, int, int] | None:
    """Union of the drawn area across every frame, padded, or None if uniform.

    The background colour is taken from a corner pixel, which the demos never
    draw over.
    """
    box: tuple[int, int, int, int] | None = None
    width = height = 0
    for p in paths:
        img = Image.open(p).convert("RGB")
        width, height = img.size
        bg = img.getpixel((0, 0))
        mask = Image.new("L", img.size)
        mask.putdata([0 if px == bg else 255 for px in img.getdata()])
        found = mask.getbbox()
        if not found:
            continue
        box = found if box is None else (
            min(box[0], found[0]), min(box[1], found[1]),
            max(box[2], found[2]), max(box[3], found[3]),
        )
    if not box:
        return None
    return (
        max(0, box[0] - pad), max(0, box[1] - pad),
        min(width, box[2] + pad), min(height, box[3] + pad),
    )


def out_path(demo: Demo) -> Path:
    base = OUT_DIR / demo.subdir if demo.subdir else OUT_DIR
    return base / f"{demo.name}.gif"


def encode(demo: Demo, frame_dir: Path) -> Path:
    paths = sorted(frame_dir.glob("frame_*.ppm"))[demo.trim_leading:]
    if not paths:
        raise SystemExit(f"no frames captured for {demo.name}")

    box = content_box(paths) if demo.crop else None
    if box:
        print(f"  cropping to drawn area {box[2] - box[0]}x{box[3] - box[1]}")

    frames: list[Image.Image] = []
    for p in paths:
        img = Image.open(p).convert("RGB")
        if box:
            img = img.crop(box)
        if demo.scale != 1.0:
            w = max(1, int(img.width * demo.scale))
            h = max(1, int(img.height * demo.scale))
            img = img.resize((w, h), demo.resample)
        frames.append(img)

    # One global palette for the whole clip. Quantizing frames independently
    # gives each its own palette, which forces full-frame rewrites and
    # balloons the file; a shared palette lets the encoder store only the
    # pixels that actually changed.
    sample_idx = range(0, len(frames), max(1, len(frames) // 8))
    strip = Image.new("RGB", (frames[0].width, frames[0].height * len(list(sample_idx))))
    for row, i in enumerate(sample_idx):
        strip.paste(frames[i], (0, row * frames[0].height))
    palette = strip.quantize(colors=demo.colors, method=Image.MEDIANCUT)
    images = [f.quantize(palette=palette, dither=Image.Dither.NONE)
              for f in frames]

    out = out_path(demo)
    out.parent.mkdir(parents=True, exist_ok=True)
    images[0].save(
        out,
        save_all=True,
        append_images=images[1:],
        duration=demo.duration_ms,
        loop=0,
        optimize=True,
        # Leaving each frame in place lets Pillow store only the pixels that
        # changed, which roughly halves the file. Safe here because every demo
        # redraws its whole window each frame, so nothing ghosts.
        disposal=1,
    )
    if demo.also_root:
        # tetris/2048 live at docs/demos/ for the README, and the games dir
        # carries a copy so docs/demos/games/ covers every game.
        copy = GAMES_DIR / out.name
        copy.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(out, copy)
    return out


def all_outputs() -> list[Path]:
    paths = [out_path(d) for d in DEMOS]
    paths += [GAMES_DIR / f"{d.name}.gif" for d in DEMOS if d.also_root]
    return paths


def check() -> int:
    missing = [p for p in all_outputs() if not p.exists()]
    for path in sorted(all_outputs()):
        if path.exists():
            print(f"  ok       {path.relative_to(ROOT)} "
                  f"({path.stat().st_size / 1024:.0f} KB)")
        else:
            print(f"  MISSING  {path.relative_to(ROOT)}")
    return 1 if missing else 0


def main(argv: list[str]) -> int:
    args = argv[1:]
    if "--check" in args:
        return check()

    if "--group" in args:
        i = args.index("--group")
        group = args[i + 1] if i + 1 < len(args) else ""
        del args[i:i + 2]
        args += [d.name for d in DEMOS if d.subdir == group]
        if not args:
            raise SystemExit(f"no demo in group {group!r}; "
                             f"have {sorted({d.subdir or 'root' for d in DEMOS})}")

    wanted = set(args)
    selected = [d for d in DEMOS if not wanted or d.name in wanted]
    if not selected:
        raise SystemExit(f"no demo matches {sorted(wanted)}; have {[d.name for d in DEMOS]}")

    sizes: list[tuple[str, float]] = []
    for demo in selected:
        print(f"[{demo.name}] {demo.caption}")
        warn_about_pacing(demo)
        tmp = Path(tempfile.mkdtemp(prefix=f"flow-frames-{demo.name}-"))
        try:
            captured = record(demo, tmp)
            print(f"  captured {captured} frame(s)")
            out = encode(demo, tmp)
            size_kb = out.stat().st_size / 1024
            sizes.append((demo.name, size_kb))
            print(f"  wrote {out.relative_to(ROOT)} ({size_kb:.0f} KB)\n")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    if len(sizes) > 1:
        print("size table:")
        for name, kb in sorted(sizes, key=lambda s: -s[1]):
            flag = "  OVER 1MB" if kb > 1024 else ("  over 500KB" if kb > 500 else "")
            print(f"  {name:<12} {kb:7.0f} KB{flag}")
        print(f"  {'total':<12} {sum(kb for _, kb in sizes):7.0f} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
