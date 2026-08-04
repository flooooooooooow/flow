"""Unit tests for FLOW Shader Language (FSL)."""

from flow.module_resolver import resolve_modules
from flow.shader_codegen import compile_shader_file, generate_metal_for_module, generate_metal_source
from flow.shader_dsl import (
    extract_fill_shaders,
    extract_shader_module,
    has_fill_shader_dsl,
    parse_shader_body,
)


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


def test_extract_fill_shader():
    shaders = extract_fill_shaders(PLASMA)
    assert len(shaders) == 1
    assert shaders[0].name == "plasma"


def test_parse_and_emit_metal():
    sh = extract_fill_shaders(PLASMA)[0]
    stmts = parse_shader_body(sh.body)
    assert len(stmts) == 3
    metal = generate_metal_source(sh)
    assert "fragment float4 plasma_frag" in metal
    assert "flow_shader_vertex" in metal
    assert "uniforms.time" in metal


def test_rich_language_module():
    mod = extract_shader_module(RICH)
    assert len(mod.funcs) == 1
    assert mod.funcs[0].name == "pulse"
    assert len(mod.fills) == 1
    metal = generate_metal_for_module(mod)
    assert "static inline float pulse(" in metal
    assert "for (int i =" in metal
    assert "fsl_palette" in metal
    assert "demo_frag" in metal


def test_compile_gallery(tmp_path):
    src = tmp_path / "demo.flow"
    src.write_text(RICH, encoding="utf-8")
    out = tmp_path / "out"
    metal = compile_shader_file(str(src), str(out))
    assert metal.name.endswith("_gallery.metal")
    entries = (out / "demo_gallery.entries").read_text().strip().splitlines()
    assert entries == ["demo_frag"]


def test_requires_color_assign():
    bad = extract_fill_shaders("shader fill x { let u = uv.x\n }")[0]
    try:
        generate_metal_source(bad)
        assert False, "expected SyntaxError"
    except SyntaxError as e:
        assert "color" in str(e)


def test_showcase_extracts_many():
    from pathlib import Path
    text = Path("examples/gpu/shader_showcase.flow").read_text(encoding="utf-8")
    mod = extract_shader_module(text)
    assert len(mod.fills) >= 10
    assert len(mod.funcs) >= 2
    metal = generate_metal_for_module(mod)
    assert "mandelbrot_frag" in metal
    assert "julia_frag" in metal


def test_has_fill_shader_dsl():
    assert has_fill_shader_dsl(PLASMA)
    assert has_fill_shader_dsl(RICH)
    assert not has_fill_shader_dsl('function main() -> i32 { return 0 }')


def test_fill_shader_modules_resolve_for_c_transpile():
    """FSL examples must resolve via host stub so tier-2 C transpile passes."""
    from pathlib import Path

    for name in ("shader_plasma.flow", "shader_ripple.flow", "shader_showcase.flow"):
        path = Path("examples/gpu") / name
        decls = resolve_modules(str(path))
        assert any(getattr(d, "name", None) == "main" for d in decls)
