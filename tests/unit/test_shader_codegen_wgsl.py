"""Tests for the FSL -> WGSL/WebGPU backend."""

from pathlib import Path

from flow.shader_codegen_wgsl import (
    compile_shader_file_wgsl,
    generate_wgsl_for_module,
    generate_wgsl_source,
)
from flow.shader_dsl import extract_fill_shaders, extract_shader_module


GRADIENT = """
shader fill vgpu_gradient {
    let vignette: f32 = smoothstep(1.2, 0.2, distance(uv, vec2(0.5)))
    color = vec4(uv.x, uv.y, 0.46 + 0.16 * vignette, 1.0)
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


def test_gradient_emits_webgpu_fragment():
    shader = extract_fill_shaders(GRADIENT)[0]
    wgsl = generate_wgsl_source(shader)

    assert "@vertex" in wgsl
    assert "fn flow_shader_vertex" in wgsl
    assert "@fragment" in wgsl
    assert "fn vgpu_gradient_frag" in wgsl
    assert "smoothstep(1.2, 0.2, distance(uv, vec2<f32>(0.5)))" in wgsl
    assert "vec4<f32>(uv.x, uv.y, (0.46 + (0.16 * vignette)), 1.0)" in wgsl


def test_rich_fsl_surface_is_shared_with_metal_backend():
    wgsl = generate_wgsl_for_module(extract_shader_module(RICH))

    assert "fn pulse(t: f32, speed: f32) -> f32" in wgsl
    assert "for (var i: i32 = i32(0.0); i < i32(3.0); i = i + 1)" in wgsl
    assert "fsl_palette" in wgsl
    assert "uniforms.time" in wgsl
    assert "fn demo_frag" in wgsl


def test_compile_wgsl_gallery(tmp_path):
    src = tmp_path / "gradient.flow"
    src.write_text(GRADIENT, encoding="utf-8")
    out = tmp_path / "out"

    generated = compile_shader_file_wgsl(str(src), str(out))

    assert generated.name == "gradient_gallery.wgsl"
    assert generated.exists()
    entries = (out / "gradient_gallery.wgsl.entries").read_text(encoding="utf-8").splitlines()
    assert entries == ["vgpu_gradient_frag"]


def test_named_wgsl_fill_output(tmp_path):
    src = tmp_path / "demo.flow"
    src.write_text(RICH, encoding="utf-8")
    out = tmp_path / "out"

    generated = compile_shader_file_wgsl(str(src), str(out), shader_name="demo")

    assert generated.name == "demo_fill.wgsl"
    assert "fn demo_frag" in generated.read_text(encoding="utf-8")


def test_vgpu_gradient_fixture_tracks_compiler_surface():
    path = Path("examples/gpu/vgpu/gradient.flow")
    mod = extract_shader_module(path.read_text(encoding="utf-8"))
    assert [fill.name for fill in mod.fills] == ["vgpu_gradient"]

    wgsl = generate_wgsl_for_module(mod)
    assert "distance(uv, vec2<f32>(0.5))" in wgsl
    assert "fn vgpu_gradient_frag" in wgsl


def test_existing_fsl_galleries_generate_wgsl():
    scene_mod = extract_shader_module(
        Path("examples/gpu/shader_photoreal.flow").read_text(encoding="utf-8")
    )
    material_mod = extract_shader_module(
        Path("examples/gpu/shader_photoreal_materials.flow").read_text(encoding="utf-8")
    )

    scene_wgsl = generate_wgsl_for_module(scene_mod)
    material_wgsl = generate_wgsl_for_module(material_mod)

    assert len(scene_mod.fills) == 4
    assert len(material_mod.fills) == 60
    assert "fn photoreal_studio_frag" in scene_wgsl
    assert "fn photoreal_glass_frag" in scene_wgsl
    assert "fn photoreal_gold_frag" in material_wgsl
    assert "fn photoreal_energy_crystal_frag" in material_wgsl
    assert "fn photoreal_underwater_frag" in material_wgsl


def test_wgsl_requires_color_assignment():
    bad = extract_fill_shaders("shader fill x { let u = uv.x\n }")[0]
    try:
        generate_wgsl_source(bad)
        assert False, "expected SyntaxError"
    except SyntaxError as exc:
        assert "color" in str(exc)
