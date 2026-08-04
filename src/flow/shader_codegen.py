"""Lower FLOW Shader Language (FSL) to Metal fragment sources."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Set

from .shader_dsl import (
    AssignStmt,
    Binary,
    Call,
    Cast,
    FillShader,
    ForStmt,
    IfStmt,
    LetStmt,
    Name,
    Number,
    ReturnStmt,
    ShaderFunc,
    ShaderModule,
    Stmt,
    Swizzle,
    Unary,
    extract_shader_module,
    parse_shader_body,
)

_METAL_TYPES = {
    "f32": "float",
    "i32": "int",
    "bool": "bool",
    "vec2": "float2",
    "vec3": "float3",
    "vec4": "float4",
    "mat2": "float2x2",
    "mat3": "float3x3",
    "mat4": "float4x4",
}

_BUILTINS = {
    "sin", "cos", "tan", "asin", "acos", "atan", "atan2",
    "abs", "sign", "floor", "ceil", "fract", "trunc",
    "sqrt", "rsqrt", "exp", "exp2", "log", "log2", "pow",
    "min", "max", "clamp", "saturate", "mix", "step", "smoothstep",
    "length", "distance", "dot", "cross", "normalize", "reflect", "refract",
    "mod", "fmod",
}

_PRELUDE = r"""
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
    float2 pos;
    if (vid == 0) pos = float2(-1.0, -1.0);
    else if (vid == 1) pos = float2( 3.0, -1.0);
    else pos = float2(-1.0,  3.0);
    FlowVertexOut out;
    out.position = float4(pos, 0.0, 1.0);
    out.uv = float2(pos.x * 0.5 + 0.5, 1.0 - (pos.y * 0.5 + 0.5));
    return out;
}

// ── FSL standard library (hash / noise / palette) ───────────────────
static inline float fsl_hash11(float p) {
    p = fract(p * 0.1031);
    p *= p + 33.33;
    p *= p + p;
    return fract(p);
}
static inline float fsl_hash21(float2 p) {
    float3 p3 = fract(float3(p.xyx) * 0.1031);
    p3 += dot(p3, p3.yzx + 33.33);
    return fract((p3.x + p3.y) * p3.z);
}
static inline float2 fsl_hash22(float2 p) {
    float3 p3 = fract(float3(p.xyx) * float3(0.1031, 0.1030, 0.0973));
    p3 += dot(p3, p3.yzx + 33.33);
    return fract((p3.xx + p3.yz) * p3.zy);
}
static inline float fsl_noise(float2 p) {
    float2 i = floor(p);
    float2 f = fract(p);
    float a = fsl_hash21(i);
    float b = fsl_hash21(i + float2(1.0, 0.0));
    float c = fsl_hash21(i + float2(0.0, 1.0));
    float d = fsl_hash21(i + float2(1.0, 1.0));
    float2 u = f * f * (3.0 - 2.0 * f);
    return mix(a, b, u.x) + (c - a) * u.y * (1.0 - u.x) + (d - b) * u.x * u.y;
}
static inline float fsl_fbm(float2 p) {
    float v = 0.0;
    float a = 0.5;
    for (int i = 0; i < 5; i++) {
        v += a * fsl_noise(p);
        p *= 2.0;
        a *= 0.5;
    }
    return v;
}
static inline float3 fsl_palette(float t) {
    float3 a = float3(0.5, 0.5, 0.5);
    float3 b = float3(0.5, 0.5, 0.5);
    float3 c = float3(1.0, 1.0, 1.0);
    float3 d = float3(0.00, 0.33, 0.67);
    return a + b * cos(6.28318 * (c * t + d));
}
"""


class _Emitter:
    def __init__(self, user_fns: Set[str]):
        self.user_fns = user_fns
        self.env: Dict[str, str] = {}  # name -> metal type

    def map_type(self, typ: Optional[str]) -> str:
        if not typ:
            return "float"
        return _METAL_TYPES.get(typ, typ)

    def emit_expr(self, expr) -> str:
        if isinstance(expr, Number):
            return expr.value
        if isinstance(expr, Name):
            if expr.value == "uv":
                return "uv"
            if expr.value == "time":
                return "uniforms.time"
            if expr.value == "resolution":
                return "float2(uniforms.width, uniforms.height)"
            if expr.value == "color":
                return "color"
            return expr.value
        if isinstance(expr, Unary):
            return f"({expr.op}{self.emit_expr(expr.expr)})"
        if isinstance(expr, Binary):
            op = expr.op
            if op == "%":
                return f"fmod({self.emit_expr(expr.left)}, {self.emit_expr(expr.right)})"
            return f"({self.emit_expr(expr.left)} {op} {self.emit_expr(expr.right)})"
        if isinstance(expr, Swizzle):
            return f"{self.emit_expr(expr.base)}.{expr.fields}"
        if isinstance(expr, Cast):
            mt = self.map_type(expr.typ)
            return f"{mt}({self.emit_expr(expr.expr)})"
        if isinstance(expr, Call):
            args = ", ".join(self.emit_expr(a) for a in expr.args)
            if expr.name in ("vec2", "vec3", "vec4"):
                return f"{_METAL_TYPES[expr.name]}({args})"
            if expr.name == "hash":
                if len(expr.args) == 1:
                    at = self.guess_type(expr.args[0])
                    if at in ("float2", "vec2"):
                        return f"fsl_hash21({args})"
                    return f"fsl_hash11({args})"
                return f"fsl_hash21({args})"
            if expr.name == "noise":
                return f"fsl_noise({args})"
            if expr.name == "fbm":
                return f"fsl_fbm({args})"
            if expr.name == "palette":
                return f"fsl_palette({args})"
            if expr.name == "mod":
                return f"fmod({args})"
            if expr.name in _BUILTINS or expr.name in self.user_fns:
                return f"{expr.name}({args})"
            raise SyntaxError(f"Unknown shader function '{expr.name}'")
        raise SyntaxError(f"Unsupported shader expr {type(expr)}")

    def guess_type(self, expr) -> str:
        if isinstance(expr, Number):
            return "float"
        if isinstance(expr, Name):
            if expr.value == "uv" or expr.value == "resolution":
                return "float2"
            if expr.value in ("time",):
                return "float"
            if expr.value == "color":
                return "float4"
            return self.env.get(expr.value, "float")
        if isinstance(expr, Cast):
            return self.map_type(expr.typ)
        if isinstance(expr, Call):
            if expr.name in ("vec2",):
                return "float2"
            if expr.name in ("vec3", "palette", "normalize", "cross", "reflect"):
                return "float3"
            if expr.name in ("vec4",):
                return "float4"
            if expr.name in ("noise", "fbm", "hash", "length", "dot", "sin", "cos", "atan2"):
                return "float"
            if expr.name in self.user_fns:
                return "float"  # refined when emitting fns
            if expr.args:
                return self.guess_type(expr.args[0])
        if isinstance(expr, Swizzle):
            n = len(expr.fields)
            return {1: "float", 2: "float2", 3: "float3", 4: "float4"}.get(n, "float")
        if isinstance(expr, Unary):
            if expr.op == "!":
                return "bool"
            return self.guess_type(expr.expr)
        if isinstance(expr, Binary):
            if expr.op in ("<", ">", "<=", ">=", "==", "!=", "&&", "||"):
                return "bool"
            lt = self.guess_type(expr.left)
            rt = self.guess_type(expr.right)
            rank = {"bool": 0, "float": 1, "int": 1, "float2": 2, "float3": 3, "float4": 4}
            return lt if rank.get(lt, 1) >= rank.get(rt, 1) else rt
        return "float"

    def emit_stmts(self, stmts: List[Stmt], indent: int = 1) -> List[str]:
        pad = "    " * indent
        lines: List[str] = []
        for st in stmts:
            if isinstance(st, LetStmt):
                et = self.map_type(st.typ) if st.typ else self.guess_type(st.expr)
                self.env[st.name] = et
                lines.append(f"{pad}{et} {st.name} = {self.emit_expr(st.expr)};")
            elif isinstance(st, AssignStmt):
                if st.name == "color":
                    lines.append(f"{pad}color = {self.emit_expr(st.expr)};")
                else:
                    lines.append(f"{pad}{st.name} = {self.emit_expr(st.expr)};")
            elif isinstance(st, ReturnStmt):
                if st.expr is None:
                    lines.append(f"{pad}return;")
                else:
                    lines.append(f"{pad}return {self.emit_expr(st.expr)};")
            elif isinstance(st, IfStmt):
                lines.append(f"{pad}if ({self.emit_expr(st.cond)}) {{")
                lines.extend(self.emit_stmts(st.then_body, indent + 1))
                if st.else_body:
                    lines.append(f"{pad}}} else {{")
                    lines.extend(self.emit_stmts(st.else_body, indent + 1))
                lines.append(f"{pad}}}")
            elif isinstance(st, ForStmt):
                # Metal for-loop; start/end as int
                self.env[st.var] = "int"
                lines.append(
                    f"{pad}for (int {st.var} = int({self.emit_expr(st.start)}); "
                    f"{st.var} < int({self.emit_expr(st.end)}); {st.var}++) {{"
                )
                lines.extend(self.emit_stmts(st.body, indent + 1))
                lines.append(f"{pad}}}")
            else:
                raise SyntaxError(f"Unsupported shader stmt {type(st)}")
        return lines


def _emit_fn(fn: ShaderFunc, user_fns: Set[str]) -> str:
    em = _Emitter(user_fns)
    ret = em.map_type(fn.return_type)
    params = []
    for name, typ in fn.params:
        mt = em.map_type(typ)
        em.env[name] = mt
        params.append(f"{mt} {name}")
    stmts = parse_shader_body(fn.body)
    body = em.emit_stmts(stmts, indent=1)
    return (
        f"static inline {ret} {fn.name}({', '.join(params)}) {{\n"
        + "\n".join(body)
        + "\n}\n"
    )


def _has_color_assign(stmts: List[Stmt]) -> bool:
    for s in stmts:
        if isinstance(s, AssignStmt) and s.name == "color":
            return True
        if isinstance(s, IfStmt) and (
            _has_color_assign(s.then_body) or _has_color_assign(s.else_body)
        ):
            return True
        if isinstance(s, ForStmt) and _has_color_assign(s.body):
            return True
    return False


def generate_metal_for_module(mod: ShaderModule) -> str:
    if not mod.fills:
        raise ValueError("No `shader fill` blocks in module")
    user_fns = {f.name for f in mod.funcs}
    parts = [_PRELUDE, ""]
    for fn in mod.funcs:
        parts.append(_emit_fn(fn, user_fns))
        parts.append("")
    for fill in mod.fills:
        stmts = parse_shader_body(fill.body)
        if not _has_color_assign(stmts):
            raise SyntaxError(
                f"shader fill '{fill.name}' must assign `color = ...`"
            )
        em = _Emitter(user_fns)
        body = em.emit_stmts(stmts, indent=1)
        parts.append(f"fragment float4 {fill.name}_frag(")
        parts.append("    FlowVertexOut in [[stage_in]],")
        parts.append("    constant FlowShaderUniforms& uniforms [[buffer(0)]]")
        parts.append(") {")
        parts.append("    float2 uv = in.uv;")
        parts.append("    float4 color = float4(0.0, 0.0, 0.0, 1.0);")
        parts.extend(body)
        parts.append("    return color;")
        parts.append("}")
        parts.append("")
    return "\n".join(parts)


def generate_metal_source(shader: FillShader) -> str:
    """Back-compat: single fill with no helpers."""
    mod = ShaderModule(fills=[shader])
    return generate_metal_for_module(mod)


def compile_shader_file(
    source_path: str,
    out_dir: str,
    shader_name: Optional[str] = None,
) -> Path:
    """Compile all (or one named) fill shaders from a .flow file.

    Writes:
      - `<stem>_gallery.metal` — combined library (all fills + fns)
      - `<name>_fill.metal` — per-shader (still useful)
      - `<stem>_gallery.entries` — newline list of fragment entry names
    Returns path to the gallery metal file (or single metal if one named).
    """
    text = Path(source_path).read_text(encoding="utf-8")
    mod = extract_shader_module(text)
    if not mod.fills:
        raise ValueError(
            "No `shader fill Name { ... }` blocks found.\n"
            "See docs/language/shaders.md"
        )
    if shader_name:
        fills = [f for f in mod.fills if f.name == shader_name]
        if not fills:
            raise ValueError(f"Shader '{shader_name}' not found")
        mod = ShaderModule(funcs=mod.funcs, fills=fills)

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    stem = Path(source_path).stem

    gallery_metal = generate_metal_for_module(mod)
    gallery_path = out / f"{stem}_gallery.metal"
    gallery_path.write_text(gallery_metal, encoding="utf-8")
    entries = [f"{f.name}_frag" for f in mod.fills]
    (out / f"{stem}_gallery.entries").write_text("\n".join(entries) + "\n", encoding="utf-8")

    for fill in mod.fills:
        single = ShaderModule(funcs=mod.funcs, fills=[fill])
        path = out / f"{fill.name}_fill.metal"
        path.write_text(generate_metal_for_module(single), encoding="utf-8")
        (out / f"{fill.name}_fill.entry").write_text(f"{fill.name}_frag\n", encoding="utf-8")

    return gallery_path
