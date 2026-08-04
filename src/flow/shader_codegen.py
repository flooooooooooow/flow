"""Lower FLOW fill-shaders to Metal fragment source + host entry."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from .shader_dsl import (
    AssignStmt,
    Binary,
    Call,
    FillShader,
    IfStmt,
    LetStmt,
    Name,
    Number,
    Stmt,
    Swizzle,
    Unary,
    extract_fill_shaders,
    parse_shader_body,
)

_BUILTINS = {
    "sin",
    "cos",
    "tan",
    "abs",
    "sqrt",
    "min",
    "max",
    "fract",
    "floor",
    "ceil",
    "pow",
    "exp",
    "log",
    "length",
    "normalize",
    "dot",
    "mix",
    "smoothstep",
    "clamp",
    "step",
}


def _emit_expr(expr) -> str:
    if isinstance(expr, Number):
        return expr.value
    if isinstance(expr, Name):
        if expr.value == "uv":
            return "uv"
        if expr.value == "time":
            return "uniforms.time"
        if expr.value == "color":
            return "color"
        return expr.value
    if isinstance(expr, Unary):
        return f"({expr.op}{_emit_expr(expr.expr)})"
    if isinstance(expr, Binary):
        return f"({_emit_expr(expr.left)} {expr.op} {_emit_expr(expr.right)})"
    if isinstance(expr, Swizzle):
        return f"{_emit_expr(expr.base)}.{expr.fields}"
    if isinstance(expr, Call):
        args = ", ".join(_emit_expr(a) for a in expr.args)
        if expr.name in ("vec2", "vec3", "vec4"):
            metal = {"vec2": "float2", "vec3": "float3", "vec4": "float4"}[expr.name]
            return f"{metal}({args})"
        if expr.name in _BUILTINS:
            return f"{expr.name}({args})"
        raise SyntaxError(f"Unknown shader function '{expr.name}'")
    raise SyntaxError(f"Unsupported shader expr {type(expr)}")


def _emit_stmts(stmts: List[Stmt], indent: int = 1) -> List[str]:
    pad = "    " * indent
    lines: List[str] = []
    for st in stmts:
        if isinstance(st, LetStmt):
            et = _guess_type(st.expr)
            lines.append(f"{pad}{et} {st.name} = {_emit_expr(st.expr)};")
        elif isinstance(st, AssignStmt):
            if st.name == "color":
                lines.append(f"{pad}color = {_emit_expr(st.expr)};")
            else:
                lines.append(f"{pad}{st.name} = {_emit_expr(st.expr)};")
        elif isinstance(st, IfStmt):
            lines.append(f"{pad}if ({_emit_expr(st.cond)}) {{")
            lines.extend(_emit_stmts(st.then_body, indent + 1))
            if st.else_body:
                lines.append(f"{pad}}} else {{")
                lines.extend(_emit_stmts(st.else_body, indent + 1))
            lines.append(f"{pad}}}")
        else:
            raise SyntaxError(f"Unsupported shader stmt {type(st)}")
    return lines


def _guess_type(expr) -> str:
    if isinstance(expr, Number):
        return "float"
    if isinstance(expr, Name):
        if expr.value == "uv":
            return "float2"
        if expr.value == "time":
            return "float"
        if expr.value == "color":
            return "float4"
        return "float"  # let bindings default float; vec lets use Call
    if isinstance(expr, Call):
        if expr.name == "vec2":
            return "float2"
        if expr.name == "vec3":
            return "float3"
        if expr.name == "vec4":
            return "float4"
        if expr.name in ("length", "sin", "cos", "tan", "abs", "sqrt", "fract", "floor", "ceil", "dot"):
            return "float"
        if expr.name in ("normalize",):
            return "float3"
        if expr.name in ("mix", "min", "max", "clamp", "smoothstep", "pow"):
            return _guess_type(expr.args[0]) if expr.args else "float"
    if isinstance(expr, Swizzle):
        n = len(expr.fields)
        return {1: "float", 2: "float2", 3: "float3", 4: "float4"}.get(n, "float")
    if isinstance(expr, Unary):
        return _guess_type(expr.expr)
    if isinstance(expr, Binary):
        # comparisons -> bool; else promote
        if expr.op in ("<", ">", "<=", ">=", "==", "!="):
            return "bool"
        lt = _guess_type(expr.left)
        rt = _guess_type(expr.right)
        rank = {"bool": 0, "float": 1, "float2": 2, "float3": 3, "float4": 4}
        return lt if rank.get(lt, 1) >= rank.get(rt, 1) else rt
    return "float"


_VERTEX_AND_UNIFORMS = """
#include <metal_stdlib>
using namespace metal;

struct FlowShaderUniforms {
    float time;
    float width;
    float height;
};

struct FlowVertexOut {
    float4 position [[position]];
    float2 uv;
};

vertex FlowVertexOut flow_shader_vertex(uint vid [[vertex_id]]) {
    // Fullscreen triangle
    float2 pos;
    if (vid == 0) pos = float2(-1.0, -1.0);
    else if (vid == 1) pos = float2( 3.0, -1.0);
    else pos = float2(-1.0,  3.0);
    FlowVertexOut out;
    out.position = float4(pos, 0.0, 1.0);
    out.uv = float2(pos.x * 0.5 + 0.5, 1.0 - (pos.y * 0.5 + 0.5));
    return out;
}
"""


def generate_metal_source(shader: FillShader) -> str:
    stmts = parse_shader_body(shader.body)
    has_color = any(isinstance(s, AssignStmt) and s.name == "color" for s in stmts)
    if not has_color:
        # allow color assign inside if
        def walk(ss):
            for s in ss:
                if isinstance(s, AssignStmt) and s.name == "color":
                    return True
                if isinstance(s, IfStmt) and (walk(s.then_body) or walk(s.else_body)):
                    return True
            return False

        if not walk(stmts):
            raise SyntaxError(
                f"shader fill '{shader.name}' must assign `color = ...`"
            )

    body_lines = _emit_stmts(stmts, indent=1)
    frag = [
        f"fragment float4 {shader.name}_frag(",
        "    FlowVertexOut in [[stage_in]],",
        "    constant FlowShaderUniforms& uniforms [[buffer(0)]]",
        ") {",
        "    float2 uv = in.uv;",
        "    float4 color = float4(0.0, 0.0, 0.0, 1.0);",
        *body_lines,
        "    return color;",
        "}",
        "",
    ]
    return _VERTEX_AND_UNIFORMS + "\n" + "\n".join(frag)


def compile_shader_file(
    source_path: str, out_dir: str, shader_name: Optional[str] = None
) -> Path:
    """Extract fill shaders from a .flow file and write `.metal` sources.

    Returns path to the primary (first, or named) metal file.
    """
    text = Path(source_path).read_text(encoding="utf-8")
    shaders = extract_fill_shaders(text)
    if not shaders:
        raise ValueError(
            "No `shader fill Name { ... }` blocks found.\n"
            "Example:\n"
            "  shader fill plasma {\n"
            "      color = vec4(uv.x, uv.y, 0.5 + 0.5 * sin(time), 1.0)\n"
            "  }"
        )
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    primary: Optional[Path] = None
    for sh in shaders:
        if shader_name and sh.name != shader_name:
            continue
        metal = generate_metal_source(sh)
        path = out / f"{sh.name}_fill.metal"
        path.write_text(metal, encoding="utf-8")
        if primary is None:
            primary = path
        # sidecar with entry name for the runtime host
        (out / f"{sh.name}_fill.entry").write_text(f"{sh.name}_frag\n", encoding="utf-8")
    if primary is None:
        raise ValueError(f"Shader '{shader_name}' not found")
    return primary
