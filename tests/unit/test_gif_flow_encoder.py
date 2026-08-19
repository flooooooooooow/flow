"""End-to-end check of the pure-Flow GIF89a encoder (lib/stdlib/gif.flow).

Compiles and runs examples/graphics/gif_writer.flow, then decodes the GIF it
produced with Pillow. The decode is the ground truth: format, frame count,
dimensions, loop metadata, and real pixel change between the first and last
frame (the animation is not a stack of identical frames).
"""

from __future__ import annotations

import os
import subprocess
import sys

import pytest

from .compiler_helpers import needs_clang

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
EXAMPLE = os.path.join(REPO_ROOT, "examples", "graphics", "gif_writer.flow")

WIDTH = 128
HEIGHT = 128
FRAMES = 24
DELAY_CS = 5


@pytest.fixture(scope="module")
def demo_gif(tmp_path_factory):
    """Transpile, compile, and run the example; return the GIF path."""
    pytest.importorskip("PIL")
    td = tmp_path_factory.mktemp("gif_demo")
    c_path = td / "gif_writer.c"
    bin_path = td / "gif_writer"

    env = dict(os.environ)
    env["PYTHONPATH"] = (
        os.path.join(REPO_ROOT, "src")
        + os.pathsep
        + env.get("PYTHONPATH", "")
    )
    transpile = subprocess.run(
        [sys.executable, "-m", "flow.transpiler", EXAMPLE, "--c", "--strict",
         "-o", str(c_path)],
        capture_output=True, text=True, env=env, cwd=REPO_ROOT,
    )
    assert transpile.returncode == 0, transpile.stderr or transpile.stdout
    assert c_path.exists()

    compile_ = subprocess.run(
        ["clang", "-Wno-everything", str(c_path), "-o", str(bin_path), "-lm"],
        capture_output=True, text=True,
    )
    assert compile_.returncode == 0, compile_.stderr

    # The example writes build/gif_demo.gif relative to its cwd.
    run = subprocess.run(
        [str(bin_path)], capture_output=True, text=True, cwd=td,
    )
    assert run.returncode == 0, run.stdout + run.stderr
    assert "bytes" in run.stdout

    gif_path = td / "build" / "gif_demo.gif"
    assert gif_path.exists()
    return gif_path


@needs_clang
class TestGifFlowEncoder:
    def test_pillow_decodes_the_full_animation(self, demo_gif):
        from PIL import Image

        with Image.open(demo_gif) as im:
            assert im.format == "GIF"
            assert im.size == (WIDTH, HEIGHT)
            assert im.n_frames == FRAMES
            # Every frame must decode without a broken-data-stream error.
            for i in range(im.n_frames):
                im.seek(i)
                im.load()

    def test_loop_and_delay_metadata(self, demo_gif):
        from PIL import Image

        with Image.open(demo_gif) as im:
            assert im.info.get("loop") == 0  # NETSCAPE2.0: loop forever
            assert im.info.get("duration") == DELAY_CS * 10  # ms

    def test_animation_actually_moves(self, demo_gif):
        from PIL import Image

        with Image.open(demo_gif) as im:
            im.seek(0)
            first = im.convert("RGB")
            im.seek(im.n_frames - 1)
            last = im.convert("RGB")
        # Raw RGB bytes rather than getdata(), which Pillow 14 removes.
        head, tail = first.tobytes(), last.tobytes()
        differing = sum(
            1 for i in range(0, len(head), 3) if head[i : i + 3] != tail[i : i + 3]
        )
        assert differing > 0
        # The moving square is 24x24; two disjoint positions differ in
        # exactly 2 * 576 pixels on this fixture.
        assert differing == 1152

    def test_square_color_survives_quantization(self, demo_gif):
        from PIL import Image

        with Image.open(demo_gif) as im:
            im.seek(0)
            first = im.convert("RGB")
        # Frame 0 square sits at (8, 8)..(31, 31); fill is (255, 210, 40),
        # nearest 6x7x6 cube entry is (255, 212, 51).
        assert first.getpixel((12, 12)) == (255, 212, 51)
