"""FLOW Shader Language (FSL) through flowc (FLOWC_SHADER=metal|wgsl).

Byte parity with the retired Python backends is compiler/scripts/
parity_shader_dsl.sh. These tests cover the Python bridge.
"""

from pathlib import Path

import pytest

from flow.module_resolver import resolve_modules
from flow.shader_dsl import compile_shader_file, expand_fill_shader, fill_names, has_fill_shader_dsl

PLASMA = """
shader fill plasma {
    let u = uv.x
    let v = uv.y
    color = vec4(
        0.5 + 0.5 * sin(u * 10.0 + time),
        0.5 + 0.5 * cos(v * 8.0 - time),
        0.5, 1.0
    )
}
"""

RICH = """
fn pulse(t: f32, speed: f32) -> f32 {
    return 0.5 + 0.5 * sin(t * speed)
}

shader fill demo {
    let p: vec2 = uv - vec2(0.5)
    var col: vec3 = vec3(0.0)
    for i in 0 to 3 {
        col = col + palette(length(p) + f32(i) * 0.1) * pulse(time, 2.0)
    }
    if length(p) < 0.2 {
        color = vec4(1.0, 1.0, 1.0, 1.0)
    } else {
        color = vec4(col, 1.0)
    }
}
"""


def _build(tmp_path, text, target="metal", name=None, stem="demo"):
    src = tmp_path / f"{stem}.flow"
    src.write_text(text, encoding="utf-8")
    return compile_shader_file(str(src), str(tmp_path / "out"), shader_name=name, target=target)


def test_plasma_metal(tmp_path):
    metal = _build(tmp_path, PLASMA).read_text(encoding="utf-8")
    assert "fragment float4 plasma_frag" in metal
    assert "flow_shader_vertex" in metal
    assert "uniforms.time" in metal


def test_rich_metal_gallery(tmp_path):
    path = _build(tmp_path, RICH)
    assert path.name == "demo_gallery.metal"
    metal = path.read_text(encoding="utf-8")
    assert "static inline float pulse(" in metal
    assert "for (int i =" in metal
    assert "fsl_palette" in metal
    assert (path.parent / "demo_gallery.entries").read_text().splitlines() == ["demo_frag"]
    assert (path.parent / "demo_fill.entry").read_text() == "demo_frag\n"


def test_rich_wgsl(tmp_path):
    wgsl = _build(tmp_path, RICH, target="wgsl").read_text(encoding="utf-8")
    assert "fn pulse(t: f32, speed: f32) -> f32" in wgsl
    assert "for (var i: i32 = i32(0.0); i < i32(3.0); i = i + 1)" in wgsl
    assert "fn demo_frag" in wgsl


def test_named_wgsl(tmp_path):
    path = _build(tmp_path, RICH, target="wgsl", name="demo")
    assert path.name == "demo_fill.wgsl"
    assert (path.parent / "demo_gallery.wgsl.entries").read_text() == "demo_frag"


@pytest.mark.parametrize("target", ["metal", "wgsl"])
def test_requires_color_assign(tmp_path, target):
    with pytest.raises(SyntaxError, match="color"):
        _build(tmp_path, "shader fill x { let u = uv.x\n }", target=target)


def test_missing_name(tmp_path):
    with pytest.raises(SyntaxError, match="not found"):
        _build(tmp_path, PLASMA, name="absent")


def test_example_galleries():
    showcase = fill_names("examples/gpu/shader_showcase.flow")
    assert len(showcase) >= 10 and "mandelbrot" in showcase and "julia" in showcase
    scene = fill_names("examples/gpu/shader_photoreal.flow")
    assert scene == ["photoreal_studio", "photoreal_glass", "photoreal_marble", "photoreal_chrome"]
    materials = fill_names("examples/gpu/shader_photoreal_materials.flow")
    assert len(materials) == 60
    assert len(set(scene + materials)) == 64
    assert fill_names("examples/gpu/vgpu/gradient.flow") == ["vgpu_gradient"]


def test_vgpu_gradient_wgsl(tmp_path):
    out = compile_shader_file("examples/gpu/vgpu/gradient.flow", str(tmp_path), target="wgsl")
    wgsl = out.read_text(encoding="utf-8")
    assert "smoothstep(1.2, 0.2, distance(uv, vec2<f32>(0.5)))" in wgsl
    assert "vec4<f32>(uv.x, uv.y, (0.46 + (0.16 * vignette)), 1.0)" in wgsl


def test_detection_and_host_stub():
    assert has_fill_shader_dsl(PLASMA)
    assert not has_fill_shader_dsl("function main() -> i32 { return 0 }")
    assert not has_fill_shader_dsl('let s: string = "shader fill x { }"')
    assert expand_fill_shader(PLASMA) == "function main() -> i32 {\n    return 0\n}\n"


def test_fill_shader_modules_resolve_for_c_transpile():
    """FSL examples resolve to a host stub so tier-2 C transpile passes."""
    for name in ("shader_plasma", "shader_ripple", "shader_showcase", "shader_photoreal"):
        decls = resolve_modules(str(Path("examples/gpu") / f"{name}.flow"))
        assert any(getattr(d, "name", None) == "main" for d in decls)
