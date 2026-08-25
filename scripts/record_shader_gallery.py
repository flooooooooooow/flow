#!/usr/bin/env python3
"""Record FSL shaders to GIFs through the real Metal backend.

Unlike scripts/record_demos.py, which links Flow gfx programs against the CPU
headless framebuffer, this script preserves the FSL pipeline end to end:

    .flow -> FSL parser/codegen -> MSL -> Metal GPU -> BGRA texture -> PPM -> GIF

The Metal recorder is offscreen and uses frame_number / fps as `time`, so the
same shader, dimensions, frame count and fps produce the same animation timing
without opening a window.

Examples:
    python3 scripts/record_shader_gallery.py --group photoreal
    python3 scripts/record_shader_gallery.py --name photoreal_gold
    python3 scripts/record_shader_gallery.py --group classic --frames 30 --fps 15

Requires macOS with an exposed Metal device, clang/Xcode command-line tools and
Pillow (the shared scripts/frames_to_gif.py encoder uses it).
"""

from __future__ import annotations

import argparse
import platform
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from flow.shader_codegen import compile_shader_file  # noqa: E402


GROUPS = {
    "photoreal": [
        ROOT / "examples/gpu/shader_photoreal.flow",
        ROOT / "examples/gpu/shader_photoreal_materials.flow",
    ],
    "classic": [ROOT / "examples/gpu/shader_showcase.flow"],
}


def compile_recorder(build_dir: Path) -> Path:
    if platform.system() != "Darwin":
        raise SystemExit("record_shader_gallery: macOS with Metal is required")
    xcrun = shutil.which("xcrun")
    if not xcrun:
        raise SystemExit("record_shader_gallery: xcrun is required")

    exe = build_dir / "shader_record_metal"
    build_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            xcrun,
            "clang",
            "-O2",
            "-fobjc-arc",
            str(ROOT / "runtime/shader_record_metal.m"),
            "-framework",
            "Metal",
            "-framework",
            "Foundation",
            "-o",
            str(exe),
        ],
        check=True,
        cwd=ROOT,
    )
    return exe


def compile_gallery(source: Path, build_dir: Path) -> tuple[Path, list[str]]:
    emitted_dir = build_dir / "msl" / source.stem
    emitted_dir.mkdir(parents=True, exist_ok=True)
    metal = Path(compile_shader_file(str(source), str(emitted_dir)))
    entries_path = metal.with_suffix(".entries")
    if not entries_path.exists():
        raise RuntimeError(f"missing generated entries file: {entries_path}")
    entries = [line.strip() for line in entries_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not entries:
        raise RuntimeError(f"no shader entries generated for {source}")
    return metal, entries


def public_name(fragment_entry: str) -> str:
    return fragment_entry[:-5] if fragment_entry.endswith("_frag") else fragment_entry


def record_one(
    recorder: Path,
    metal: Path,
    entry: str,
    output_dir: Path,
    build_dir: Path,
    *,
    width: int,
    height: int,
    frames: int,
    fps: int,
    gif_width: int,
) -> Path:
    name = public_name(entry)
    frame_dir = build_dir / "frames" / name
    if frame_dir.exists():
        shutil.rmtree(frame_dir)
    frame_dir.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        [
            str(recorder),
            str(metal),
            entry,
            str(frame_dir),
            str(width),
            str(height),
            str(frames),
            str(fps),
        ],
        check=True,
        cwd=ROOT,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    gif = output_dir / f"{name}.gif"
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/frames_to_gif.py"),
            str(frame_dir),
            str(gif),
            "--fps",
            str(fps),
            "--stride",
            "1",
            "--width",
            str(gif_width),
        ],
        check=True,
        cwd=ROOT,
    )
    return gif


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--group", choices=["photoreal", "classic", "all"], default="photoreal")
    parser.add_argument("--name", help="record one shader fill name, e.g. photoreal_gold")
    parser.add_argument("--out", type=Path, default=ROOT / "docs/demos/shaders")
    parser.add_argument("--build-dir", type=Path, default=ROOT / "build/shader-gallery")
    parser.add_argument("--width", type=int, default=640)
    parser.add_argument("--height", type=int, default=360)
    parser.add_argument("--frames", type=int, default=24)
    parser.add_argument("--fps", type=int, default=12)
    parser.add_argument("--gif-width", type=int, default=360)
    args = parser.parse_args()

    if min(args.width, args.height, args.frames, args.fps, args.gif_width) <= 0:
        parser.error("dimensions, frame count and fps must be positive")

    groups = list(GROUPS) if args.group == "all" else [args.group]
    sources = [source for group in groups for source in GROUPS[group]]
    recorder = compile_recorder(args.build_dir)

    compiled: list[tuple[Path, Path, list[str]]] = []
    all_names: dict[str, tuple[Path, Path, str]] = {}
    for source in sources:
        metal, entries = compile_gallery(source, args.build_dir)
        compiled.append((source, metal, entries))
        for entry in entries:
            name = public_name(entry)
            if name in all_names:
                raise RuntimeError(f"duplicate FSL entry: {name}")
            all_names[name] = (source, metal, entry)

    if args.name:
        if args.name not in all_names:
            choices = ", ".join(sorted(all_names))
            raise SystemExit(f"unknown shader {args.name!r}; available: {choices}")
        selected = [all_names[args.name]]
    else:
        selected = [
            (source, metal, entry)
            for source, metal, entries in compiled
            for entry in entries
        ]

    print(f"Recording {len(selected)} FSL shader(s) through Metal...")
    for index, (source, metal, entry) in enumerate(selected, 1):
        name = public_name(entry)
        print(f"[{index:02d}/{len(selected):02d}] {name} ({source.name})")
        record_one(
            recorder,
            metal,
            entry,
            args.out,
            args.build_dir,
            width=args.width,
            height=args.height,
            frames=args.frames,
            fps=args.fps,
            gif_width=args.gif_width,
        )

    print(f"Recorded {len(selected)} GIF(s) into {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
