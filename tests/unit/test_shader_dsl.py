"""Unit tests for the fill-shader surface language."""

from flow.shader_codegen import compile_shader_file, generate_metal_source
from flow.shader_dsl import extract_fill_shaders, parse_shader_body


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


def test_extract_fill_shader():
    shaders = extract_fill_shaders(PLASMA)
    assert len(shaders) == 1
    assert shaders[0].name == "plasma"
    assert "color" in shaders[0].body


def test_parse_and_emit_metal():
    sh = extract_fill_shaders(PLASMA)[0]
    stmts = parse_shader_body(sh.body)
    assert len(stmts) == 3
    metal = generate_metal_source(sh)
    assert "fragment float4 plasma_frag" in metal
    assert "flow_shader_vertex" in metal
    assert "uniforms.time" in metal
    assert "sin(" in metal


def test_compile_shader_file(tmp_path):
    src = tmp_path / "demo.flow"
    src.write_text(PLASMA, encoding="utf-8")
    out = tmp_path / "out"
    metal = compile_shader_file(str(src), str(out))
    assert metal.exists()
    text = metal.read_text(encoding="utf-8")
    assert "plasma_frag" in text
    assert (out / "plasma_fill.entry").read_text().strip() == "plasma_frag"


def test_requires_color_assign():
    bad = extract_fill_shaders("shader fill x { let u = uv.x\n }")[0]
    try:
        generate_metal_source(bad)
        assert False, "expected SyntaxError"
    except SyntaxError as e:
        assert "color" in str(e)
