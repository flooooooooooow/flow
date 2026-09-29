"""Tests for compile-time pipeline fusion of adjacent |> stages.

These check the fused AST. Runtime results of chained stages under flowc
live in tests/cgen/pipeline_fusion_scale.
"""
from flow.pipeline_fusion import fuse_pipelines
from flow.parser import parse_flow_code, BinaryOperation, FunctionCall, Lambda


def _out(body: str) -> FunctionCall:
    """Fuse `let out: ptr<f32> = <body>` and return its initializer."""
    source = (
        "function main() -> i32 {\n"
        "    let buf: array<f32, 4> = [1.0, 2.0, 3.0, 4.0]\n"
        f"    let out: ptr<f32> = {body}\n"
        "    return 0\n"
        "}\n"
    )
    decls = fuse_pipelines(parse_flow_code(source))
    main = next(d for d in decls if getattr(d, "name", None) == "main")
    out = next(s for s in main.body.statements if getattr(s, "name", None) == "out")
    return out.initializer


def _nested_calls(call, name: str) -> int:
    n = 0
    while isinstance(call, FunctionCall) and call.name == name:
        n += 1
        call = call.arguments[0]
    return n


MAP2 = (
    "buf |> map_f32(4, |x: f32| -> f32 { return x * 2.0 })"
    " |> map_f32(4, |x: f32| -> f32 { return x + 1.0 })"
)


def test_map_map_fusion():
    call = _out(MAP2)
    assert _nested_calls(call, "map_f32") == 1
    assert isinstance(call.arguments[2], Lambda)


def test_triple_map_fusion():
    call = _out(MAP2 + " |> map_f32(4, |x: f32| -> f32 { return x - 3.0 })")
    assert _nested_calls(call, "map_f32") == 1


def test_scale_scale_fusion():
    call = _out("buf |> scale_f32(4, 2.0) |> scale_f32(4, 3.0)")
    assert _nested_calls(call, "scale_f32") == 1
    factor = call.arguments[2]
    assert isinstance(factor, BinaryOperation) and factor.operator == "*"


def test_offset_offset_fusion():
    call = _out("buf |> offset_f32(4, 1.0) |> offset_f32(4, 2.0)")
    assert _nested_calls(call, "offset_f32") == 1
    delta = call.arguments[2]
    assert isinstance(delta, BinaryOperation) and delta.operator == "+"


def test_no_fusion_for_different_functions():
    call = _out(
        "buf |> scale_f32(4, 2.0)"
        " |> map_f32(4, |x: f32| -> f32 { return x + 1.0 })"
    )
    assert call.name == "map_f32"
    assert isinstance(call.arguments[0], FunctionCall)
    assert call.arguments[0].name == "scale_f32"
