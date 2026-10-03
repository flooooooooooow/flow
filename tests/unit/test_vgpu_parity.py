"""Unit tests for unified Flow GPU resources, stage declarations, and vgpu parity track."""

from pathlib import Path
import pytest

from flow.shader_codegen import generate_metal_for_module
from flow.shader_codegen_wgsl import generate_wgsl_for_module
from flow.shader_dsl import extract_shader_module


VARYING_MISMATCH_MISSING_FIELD = """
struct Vertex {
    position: vec3,
    uv: vec2,
}

struct RasterVertex {
    position: vec4,
    uv: vec2,
    color: vec4,
}

shader vertex vert(v: Vertex) -> RasterVertex {
    var out: RasterVertex;
    out.position = vec4(v.position, 1.0);
    out.uv = v.uv;
    out.color = vec4(1.0);
    return out;
}

struct MismatchedFragmentInput {
    position: vec4,
    uv: vec2,
    normal: vec3,
}

shader fragment frag(in: MismatchedFragmentInput) -> vec4 {
    color = vec4(in.normal, 1.0);
    return color;
}
"""

VARYING_MISMATCH_TYPE = """
struct Vertex {
    position: vec3,
    uv: vec2,
}

struct RasterVertex {
    position: vec4,
    uv: vec2,
}

shader vertex vert(v: Vertex) -> RasterVertex {
    var out: RasterVertex;
    out.position = vec4(v.position, 1.0);
    out.uv = v.uv;
    return out;
}

struct MismatchedTypeFragmentInput {
    position: vec4,
    uv: vec3,
}

shader fragment frag(in: MismatchedTypeFragmentInput) -> vec4 {
    color = vec4(in.uv, 1.0);
    return color;
}
"""


def test_structural_varying_mismatch_missing_field():
    with pytest.raises(SyntaxError) as exc_info:
        extract_shader_module(VARYING_MISMATCH_MISSING_FIELD)
    assert "Structural varying mismatch" in str(exc_info.value)
    assert "normal" in str(exc_info.value)


def test_structural_varying_mismatch_type():
    with pytest.raises(SyntaxError) as exc_info:
        extract_shader_module(VARYING_MISMATCH_TYPE)
    assert "Structural varying mismatch" in str(exc_info.value)
    assert "uv" in str(exc_info.value)


@pytest.mark.parametrize(
    "filename",
    [
        "instanced_rendering.flow",
        "batch_rendering.flow",
        "environment_map.flow",
        "earth.flow",
        "anti_aliasing.flow",
        "clipping.flow",
        "transmission_material.flow",
    ],
)
def test_vgpu_examples_compile_metal_and_wgsl(filename):
    filepath = Path("examples/gpu/vgpu") / filename
    assert filepath.exists()
    source = filepath.read_text(encoding="utf-8")

    mod = extract_shader_module(source)
    assert len(mod.vertices) >= 1
    assert len(mod.fragments) >= 1

    msl = generate_metal_for_module(mod)
    assert "vertex " in msl
    assert "fragment " in msl

    wgsl = generate_wgsl_for_module(mod)
    assert "@vertex" in wgsl
    assert "@fragment" in wgsl
