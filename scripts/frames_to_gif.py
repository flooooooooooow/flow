#!/usr/bin/env python3
"""Encode recorded PPM frames into an animated GIF.

Used by `flow record --gif`. Kept small on purpose: the frames come from
runtime/gfx_record.c + lib/runtime/gfx_record.flow, and Flow has its own
GIF89a encoder in lib/stdlib/gif.flow for programs that want to write GIFs
themselves. This is the host-side convenience path.

  frames_to_gif.py <frame-dir> <out.gif> [--fps 20] [--stride 2] [--width 480]

`flow record --gif` passes --fps/--stride/--width straight through.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:  # pragma: no cover - environment dependent
    print("frames_to_gif: Pillow is required (pip install pillow)", file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("frame_dir")
    ap.add_argument("out")
    ap.add_argument("--fps", type=int, default=20)
    ap.add_argument("--stride", type=int, default=2, help="keep every Nth frame")
    ap.add_argument("--width", type=int, default=480, help="downscale to this width")
    args = ap.parse_args()

    frames = sorted(Path(args.frame_dir).glob("frame_*.ppm"))
    if not frames:
        print(f"frames_to_gif: no frames in {args.frame_dir}", file=sys.stderr)
        return 1

    kept = frames[:: max(1, args.stride)]
    images = []
    for path in kept:
        im = Image.open(path).convert("RGB")
        if args.width and im.width > args.width:
            height = round(im.height * args.width / im.width)
            im = im.resize((args.width, height), Image.NEAREST)
        images.append(im)

    # One palette for the whole clip: per-frame palettes force full-frame
    # rewrites and inflate the file several times over. Sample the palette
    # across the clip rather than from frame 0, because a simulation often
    # starts near-uniform and only earns its colours later.
    sample = images[:: max(1, len(images) // 8)]
    strip = Image.new("RGB", (images[0].width, images[0].height * len(sample)))
    for row, im in enumerate(sample):
        strip.paste(im, (0, row * images[0].height))
    palette = strip.quantize(colors=256, method=Image.MEDIANCUT)
    quantized = [im.quantize(palette=palette, dither=Image.FLOYDSTEINBERG) for im in images]

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    quantized[0].save(
        out,
        save_all=True,
        append_images=quantized[1:],
        duration=max(20, round(1000 / max(1, args.fps))),
        loop=0,
        optimize=True,
        disposal=2,
    )
    size_kb = out.stat().st_size / 1024
    print(f"{out}: {len(quantized)} frames, {images[0].width}x{images[0].height}, {size_kb:.0f} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
