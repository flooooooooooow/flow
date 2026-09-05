#!/usr/bin/env python3
"""Build a tiny browser runner for a Flow ``shader fill`` program.

The shader is compiled from FSL to WGSL by Flow itself, then rendered through
the generic WebGPU host in ``wasm/crossing_assets/webgpu-host.js``.

Usage:
    python3 wasm/flow_webgpu_shader.py examples/gpu/vgpu/gradient.flow \
        --name vgpu_gradient --size 640x360

Then serve the printed output directory, for example:
    python3 -m http.server -d build/webgpu-shader 8000
"""

from __future__ import annotations

import argparse
import html
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from flow.shader_codegen_wgsl import compile_shader_file_wgsl
from flow.shader_dsl import extract_shader_module


def parse_size(value: str) -> tuple[int, int]:
    try:
        width_s, height_s = value.lower().split("x", 1)
        width = int(width_s)
        height = int(height_s)
    except (ValueError, TypeError) as exc:
        raise argparse.ArgumentTypeError("size must look like 640x360") from exc
    if width <= 0 or height <= 0:
        raise argparse.ArgumentTypeError("size dimensions must be positive")
    return width, height


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--name", help="fill shader name; defaults to the first fill")
    parser.add_argument("--size", type=parse_size, default=(640, 360))
    parser.add_argument("--time", type=float, default=0.0)
    parser.add_argument("--out", type=Path, default=ROOT / "build" / "webgpu-shader")
    args = parser.parse_args()

    source = args.source.resolve()
    if not source.exists():
        parser.error(f"source does not exist: {source}")

    module = extract_shader_module(source.read_text(encoding="utf-8"))
    if not module.fills:
        parser.error("source has no shader fill blocks")

    name = args.name or module.fills[0].name
    if name not in {fill.name for fill in module.fills}:
        parser.error(f"shader fill '{name}' not found")

    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    generated = compile_shader_file_wgsl(str(source), str(out), shader_name=name)
    shader_path = out / "shader.wgsl"
    if generated != shader_path:
        shutil.copyfile(generated, shader_path)

    shutil.copyfile(ROOT / "wasm" / "crossing_assets" / "webgpu-host.js", out / "webgpu-host.js")

    width, height = args.size
    page = build_page(source, name, width, height, args.time)
    (out / "index.html").write_text(page, encoding="utf-8")

    print(out)
    return 0


def build_page(source: Path, name: str, width: int, height: int, time_value: float) -> str:
    source_text = html.escape(source.read_text(encoding="utf-8"))
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Flow WebGPU shader: {html.escape(name)}</title>
<style>
html,body {{ margin:0; background:#0b0b0d; color:#eee; font:14px system-ui,sans-serif; }}
main {{ max-width:1100px; margin:32px auto; padding:0 20px; }}
canvas {{ width:min(100%, {width}px); image-rendering:auto; border:1px solid #333; }}
pre {{ overflow:auto; background:#111218; padding:16px; border-radius:8px; }}
.ok {{ color:#7ee787; }} .bad {{ color:#ff7b72; }}
</style>
</head>
<body>
<main>
<h1>Flow → WGSL → WebGPU</h1>
<p id="status">initialising WebGPU…</p>
<canvas id="canvas" width="{width}" height="{height}"></canvas>
<p><code>{html.escape(name)}</code> · {width}×{height} · time={time_value}</p>
<pre>{source_text}</pre>
</main>
<script type="module">
import {{ getDevice, renderFullscreenShader }} from './webgpu-host.js';

const status = document.getElementById('status');
try {{
    const {{ device }} = await getDevice();
    const code = await (await fetch('./shader.wgsl')).text();
    const result = await renderFullscreenShader(
        device,
        code,
        {name!r} + '_frag',
        {width},
        {height},
        {{ time: {time_value!r} }},
    );
    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');
    const pixels = new Uint8ClampedArray(result.rgba.buffer, result.rgba.byteOffset, result.rgba.byteLength);
    ctx.putImageData(new ImageData(pixels, result.width, result.height), 0, 0);
    status.textContent = `rendered ${{result.width}}×${{result.height}} in ${{result.ms.toFixed(3)}} ms`;
    status.className = 'ok';
}} catch (error) {{
    status.textContent = error && error.stack ? error.stack : String(error);
    status.className = 'bad';
}}
</script>
</body>
</html>
"""


if __name__ == "__main__":
    raise SystemExit(main())
