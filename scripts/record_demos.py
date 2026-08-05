#!/usr/bin/env python3
"""Record docs/demos/*.gif by running the real Flow programs headlessly.

Each demo is compiled with `./flow record`, which links the program against
runtime/gfx_record.c instead of a windowing backend. The program then draws
into an off-screen buffer and writes every presented frame as a PPM, so the
resulting GIF is genuine output from the compiled Flow program rather than a
re-creation of it. No display is required, which means this also works in CI.

  python3 scripts/record_demos.py            # all demos
  python3 scripts/record_demos.py lorenz     # one demo

Interactive demos are driven by FLOW_GFX_RECORD_KEYS, a list of
`first-last:keycode` windows over frame numbers (see runtime/gfx_record.c).
Requires Pillow.
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

# macOS virtual keycodes, matching lib/stdlib/gfx.flow.
KEY_LEFT, KEY_RIGHT, KEY_DOWN, KEY_UP = 123, 124, 125, 126
KEY_SPACE = 49


def hold(frame: int, key: int, length: int = 3) -> str:
    """A key held from `frame` for `length` frames."""
    return f"{frame}-{frame + length - 1}:{key}"


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
    env: dict[str, str] = field(default_factory=dict)


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
    ),
]


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
    env["FLOW_GFX_RECORD_DIR"] = str(frame_dir)
    env["FLOW_GFX_RECORD_FRAMES"] = str(demo.frames)
    env["FLOW_GFX_RECORD_SKIP"] = str(demo.skip)
    if demo.keys:
        env["FLOW_GFX_RECORD_KEYS"] = demo.keys
    env.update(demo.env)

    print(f"  running {demo.program} …")
    result = subprocess.run(
        ["./flow", "record", demo.program],
        cwd=ROOT, env=env, text=True, capture_output=True, timeout=900,
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


def encode(demo: Demo, frame_dir: Path) -> Path:
    paths = sorted(frame_dir.glob("frame_*.ppm"))[demo.trim_leading:]
    if not paths:
        raise SystemExit(f"no frames captured for {demo.name}")

    box = content_box(paths) if demo.crop else None
    if box:
        print(f"  cropping to drawn area {box[2] - box[0]}x{box[3] - box[1]}")

    images: list[Image.Image] = []
    for p in paths:
        img = Image.open(p).convert("RGB")
        if box:
            img = img.crop(box)
        if demo.scale != 1.0:
            w = max(1, int(img.width * demo.scale))
            h = max(1, int(img.height * demo.scale))
            img = img.resize((w, h), Image.LANCZOS)
        images.append(img.quantize(colors=demo.colors, method=Image.MEDIANCUT))

    out = OUT_DIR / f"{demo.name}.gif"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
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
    return out


def check() -> int:
    missing = [d for d in DEMOS if not (OUT_DIR / f"{d.name}.gif").exists()]
    for demo in DEMOS:
        path = OUT_DIR / f"{demo.name}.gif"
        if path.exists():
            print(f"  ok       {path.relative_to(ROOT)} ({path.stat().st_size / 1024:.0f} KB)")
        else:
            print(f"  MISSING  {path.relative_to(ROOT)} — run: python3 scripts/record_demos.py {demo.name}")
    return 1 if missing else 0


def main(argv: list[str]) -> int:
    args = argv[1:]
    if "--check" in args:
        return check()

    wanted = set(args)
    selected = [d for d in DEMOS if not wanted or d.name in wanted]
    if not selected:
        raise SystemExit(f"no demo matches {sorted(wanted)}; have {[d.name for d in DEMOS]}")

    for demo in selected:
        print(f"[{demo.name}] {demo.caption}")
        warn_about_pacing(demo)
        tmp = Path(tempfile.mkdtemp(prefix=f"flow-frames-{demo.name}-"))
        try:
            captured = record(demo, tmp)
            print(f"  captured {captured} frame(s)")
            out = encode(demo, tmp)
            size_kb = out.stat().st_size / 1024
            print(f"  wrote {out.relative_to(ROOT)} ({size_kb:.0f} KB)\n")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
