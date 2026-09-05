"""Lower Flow Shader Language (FSL) fullscreen shaders to WGSL.

This is the WebGPU sibling of :mod:`flow.shader_codegen`. Both backends consume
exactly the same FSL AST from ``shader_dsl.py`` so a ``shader fill`` program is
not tied to Metal.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

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


_WGSL_TYPES = {
    "f32": "f32",
    "i32": "i32",
    "bool": "bool",
    "vec2": "vec2<f32>",
    "vec3": "vec3<f32>",
    "vec4": "vec4<f32>",
    "mat2": "mat2x2<f32>",
    "mat3": "mat3x3<f32>",
    "mat4": "mat4x4<f32>",
}

_BUILTINS = {
    "sin", "cos", "tan", "asin", "acos", "atan", "atan2",
    "abs", "sign", "floor", "ceil", "fract", "trunc",
    "sqrt", "inverseSqrt", "exp", "exp2", "log", "log2", "pow",
    "min", "max", "clamp", "mix", "step", "smoothstep",
    "length", "distance", "dot", "cross", "normalize", "reflect", "refract",
}

_PRELUDE = r"""
struct FlowShaderUniforms {
    time: f32,
    width: f32,
    height: f32,
    _pad: f32,
};

@group(0) @binding(0)
var<uniform> uniforms: FlowShaderUniforms;

struct FlowVertexOut {
    @builtin(position) position: vec4<f32>,
    @location(0) uv: vec2<f32>,
};

@vertex
fn flow_shader_vertex(@builtin(vertex_index) vid: u32) -> FlowVertexOut {
    var pos: vec2<f32>;
    if (vid == 0u) {
        pos = vec2<f32>(-1.0, -1.0);
    } else if (vid == 1u) {
        pos = vec2<f32>(3.0, -1.0);
    } else {
        pos = vec2<f32>(-1.0, 3.0);
    }

    var out: FlowVertexOut;
    out.position = vec4<f32>(pos, 0.0, 1.0);
    out.uv = vec2<f32>(pos.x * 0.5 + 0.5, 1.0 - (pos.y * 0.5 + 0.5));
    return out;
}

fn fsl_hash11(value: f32) -> f32 {
    var p = fract(value * 0.1031);
    p = p * (p + 33.33);
    p = p * (p + p);
    return fract(p);
}

fn fsl_hash21(value: vec2<f32>) -> f32 {
    var p3 = fract(vec3<f32>(value.x, value.y, value.x) * vec3<f32>(0.1031));
    let d = dot(p3, p3.yzx + vec3<f32>(33.33));
    p3 = p3 + vec3<f32>(d);
    return fract((p3.x + p3.y) * p3.z);
}

fn fsl_noise(p: vec2<f32>) -> f32 {
    let i = floor(p);
    let f = fract(p);
    let a = fsl_hash21(i);
    let b = fsl_hash21(i + vec2<f32>(1.0, 0.0));
    let c = fsl_hash21(i + vec2<f32>(0.0, 1.0));
    let d = fsl_hash21(i + vec2<f32>(1.0, 1.0));
    let u = f * f * (vec2<f32>(3.0) - vec2<f32>(2.0) * f);
    return mix(a, b, u.x) + (c - a) * u.y * (1.0 - u.x) + (d - b) * u.x * u.y;
}

fn fsl_fbm(value: vec2<f32>) -> f32 {
    var p = value;
    var v = 0.0;
    var a = 0.5;
    for (var i: i32 = 0; i < 5; i = i + 1) {
        v = v + a * fsl_noise(p);
        p = p * vec2<f32>(2.0);
        a = a * 0.5;
    }
    return v;
}

fn fsl_palette(t: f32) -> vec3<f32> {
    let a = vec3<f32>(0.5, 0.5, 0.5);
    let b = vec3<f32>(0.5, 0.5, 0.5);
    let c = vec3<f32>(1.0, 1.0, 1.0);
    let d = vec3<f32>(0.00, 0.33, 0.67);
    return a + b * cos(vec3<f32>(6.28318) * (c * vec3<f32>(t) + d));
}
"""


class _Emitter:
    def __init__(self, functions: Dict[str, str]):
        self.functions = functions
        self.env: Dict[str, str] = {}

    def map_type(self, typ: Optional[str]) -> str:
        if not typ:
            return "f32"
        mapped = _WGSL_TYPES.get(typ)
        if mapped is None:
            raise SyntaxError(f"Unsupported WGSL shader type '{typ}'")
        return mapped

    def emit_expr(self, expr) -> str:
        if isinstance(expr, Number):
            return expr.value
        if isinstance(expr, Name):
            if expr.value == "uv":
                return "uv"
            if expr.value == "time":
                return "uniforms.time"
            if expr.value == "resolution":
                return "vec2<f32>(uniforms.width, uniforms.height)"
            if expr.value == "color":
                return "color"
            return expr.value
        if isinstance(expr, Unary):
            return f"({expr.op}{self.emit_expr(expr.expr)})"
        if isinstance(expr, Binary):
            return f"({self.emit_expr(expr.left)} {expr.op} {self.emit_expr(expr.right)})"
        if isinstance(expr, Swizzle):
            return f"{self.emit_expr(expr.base)}.{expr.fields}"
        if isinstance(expr, Cast):
            return f"{self.map_type(expr.typ)}({self.emit_expr(expr.expr)})"
        if isinstance(expr, Call):
            args = [self.emit_expr(arg) for arg in expr.args]
            joined = ", ".join(args)
            if expr.name in ("vec2", "vec3", "vec4"):
                return f"{_WGSL_TYPES[expr.name]}({joined})"
            if expr.name == "hash":
                if len(expr.args) != 1:
                    raise SyntaxError("hash() expects one argument")
                arg_type = self.guess_type(expr.args[0])
                if arg_type == "vec2<f32>":
                    return f"fsl_hash21({joined})"
                return f"fsl_hash11({joined})"
            if expr.name == "noise":
                return f"fsl_noise({joined})"
            if expr.name == "fbm":
                return f"fsl_fbm({joined})"
            if expr.name == "palette":
                return f"fsl_palette({joined})"
            if expr.name in ("mod", "fmod"):
                if len(args) != 2:
                    raise SyntaxError(f"{expr.name}() expects two arguments")
                return f"({args[0]} % {args[1]})"
            if expr.name == "saturate":
                if len(args) != 1:
                    raise SyntaxError("saturate() expects one argument")
                return f"clamp({args[0]}, 0.0, 1.0)"
            if expr.name == "rsqrt":
                return f"inverseSqrt({joined})"
            if expr.name in _BUILTINS or expr.name in self.functions:
                return f"{expr.name}({joined})"
            raise SyntaxError(f"Unknown shader function '{expr.name}'")
        raise SyntaxError(f"Unsupported shader expr {type(expr)}")

    def guess_type(self, expr) -> str:
        if isinstance(expr, Number):
            return "f32"
        if isinstance(expr, Name):
            if expr.value in ("uv", "resolution"):
                return "vec2<f32>"
            if expr.value == "time":
                return "f32"
            if expr.value == "color":
                return "vec4<f32>"
            return self.env.get(expr.value, "f32")
        if isinstance(expr, Cast):
            return self.map_type(expr.typ)
        if isinstance(expr, Call):
            if expr.name in ("vec2",):
                return "vec2<f32>"
            if expr.name in ("vec3", "palette", "cross"):
                return "vec3<f32>"
            if expr.name == "vec4":
                return "vec4<f32>"
            if expr.name in self.functions:
                return self.map_type(self.functions[expr.name])
            if expr.name in ("noise", "fbm", "hash", "length", "distance", "dot"):
                return "f32"
            if expr.name in ("normalize", "reflect", "refract", "min", "max", "clamp", "mix") and expr.args:
                return self.guess_type(expr.args[0])
            if expr.args:
                return self.guess_type(expr.args[0])
        if isinstance(expr, Swizzle):
            return {
                1: "f32",
                2: "vec2<f32>",
                3: "vec3<f32>",
                4: "vec4<f32>",
            }.get(len(expr.fields), "f32")
        if isinstance(expr, Unary):
            if expr.op == "!":
                return "bool"
            return self.guess_type(expr.expr)
        if isinstance(expr, Binary):
            if expr.op in ("<", ">", "<=", ">=", "==", "!=", "&&", "||"):
                return "bool"
            left = self.guess_type(expr.left)
            right = self.guess_type(expr.right)
            rank = {
                "bool": 0,
                "i32": 1,
                "f32": 1,
                "vec2<f32>": 2,
                "vec3<f32>": 3,
                "vec4<f32>": 4,
            }
            return left if rank.get(left, 1) >= rank.get(right, 1) else right
        return "f32"

    def emit_stmts(self, stmts: List[Stmt], indent: int = 1) -> List[str]:
        pad = "    " * indent
        lines: List[str] = []
        for stmt in stmts:
            if isinstance(stmt, LetStmt):
                typ = self.map_type(stmt.typ) if stmt.typ else self.guess_type(stmt.expr)
                self.env[stmt.name] = typ
                keyword = "var" if stmt.mutable else "let"
                lines.append(f"{pad}{keyword} {stmt.name}: {typ} = {self.emit_expr(stmt.expr)};")
            elif isinstance(stmt, AssignStmt):
                target = "color" if stmt.name == "color" else stmt.name
                lines.append(f"{pad}{target} = {self.emit_expr(stmt.expr)};")
            elif isinstance(stmt, ReturnStmt):
                if stmt.expr is None:
                    lines.append(f"{pad}return;")
                else:
                    lines.append(f"{pad}return {self.emit_expr(stmt.expr)};")
            elif isinstance(stmt, IfStmt):
                lines.append(f"{pad}if ({self.emit_expr(stmt.cond)}) {{")
                lines.extend(self.emit_stmts(stmt.then_body, indent + 1))
                if stmt.else_body:
                    lines.append(f"{pad}}} else {{")
                    lines.extend(self.emit_stmts(stmt.else_body, indent + 1))
                lines.append(f"{pad}}}")
            elif isinstance(stmt, ForStmt):
                self.env[stmt.var] = "i32"
                start = self.emit_expr(stmt.start)
                end = self.emit_expr(stmt.end)
                lines.append(
                    f"{pad}for (var {stmt.var}: i32 = i32({start}); "
                    f"{stmt.var} < i32({end}); {stmt.var} = {stmt.var} + 1) {{"
                )
                lines.extend(self.emit_stmts(stmt.body, indent + 1))
                lines.append(f"{pad}}}")
            else:
                raise SyntaxError(f"Unsupported shader stmt {type(stmt)}")
        return lines


def _has_color_assign(stmts: List[Stmt]) -> bool:
    for stmt in stmts:
        if isinstance(stmt, AssignStmt) and stmt.name == "color":
            return True
        if isinstance(stmt, IfStmt) and (
            _has_color_assign(stmt.then_body) or _has_color_assign(stmt.else_body)
        ):
            return True
        if isinstance(stmt, ForStmt) and _has_color_assign(stmt.body):
            return True
    return False


def _emit_fn(fn: ShaderFunc, functions: Dict[str, str]) -> str:
    emitter = _Emitter(functions)
    params = []
    for name, typ in fn.params:
        wgsl_type = emitter.map_type(typ)
        emitter.env[name] = wgsl_type
        params.append(f"{name}: {wgsl_type}")
    body = emitter.emit_stmts(parse_shader_body(fn.body), indent=1)
    return (
        f"fn {fn.name}({', '.join(params)}) -> {emitter.map_type(fn.return_type)} {{\n"
        + "\n".join(body)
        + "\n}\n"
    )


def generate_wgsl_for_module(mod: ShaderModule) -> str:
    """Generate one WGSL source module containing every FSL fill entry."""
    if not mod.fills:
        raise ValueError("No `shader fill` blocks in module")

    functions = {fn.name: fn.return_type for fn in mod.funcs}
    parts = [_PRELUDE, ""]

    for fn in mod.funcs:
        parts.append(_emit_fn(fn, functions))
        parts.append("")

    for fill in mod.fills:
        stmts = parse_shader_body(fill.body)
        if not _has_color_assign(stmts):
            raise SyntaxError(f"shader fill '{fill.name}' must assign `color = ...`")

        emitter = _Emitter(functions)
        body = emitter.emit_stmts(stmts, indent=1)
        parts.extend(
            [
                "@fragment",
                f"fn {fill.name}_frag(in: FlowVertexOut) -> @location(0) vec4<f32> {{",
                "    let uv: vec2<f32> = in.uv;",
                "    var color: vec4<f32> = vec4<f32>(0.0, 0.0, 0.0, 1.0);",
                *body,
                "    return color;",
                "}",
                "",
            ]
        )

    return "\n".join(parts)


def generate_wgsl_source(shader: FillShader) -> str:
    """Generate WGSL for one fill shader without helper functions."""
    return generate_wgsl_for_module(ShaderModule(fills=[shader]))


def compile_shader_file_wgsl(
    source_path: str,
    out_dir: str,
    shader_name: Optional[str] = None,
) -> Path:
    """Compile all, or one named, FSL fills from a ``.flow`` file to WGSL."""
    text = Path(source_path).read_text(encoding="utf-8")
    mod = extract_shader_module(text)
    if not mod.fills:
        raise ValueError("No `shader fill Name { ... }` blocks found")

    if shader_name:
        fills = [fill for fill in mod.fills if fill.name == shader_name]
        if not fills:
            raise ValueError(f"Shader '{shader_name}' not found")
        mod = ShaderModule(funcs=mod.funcs, fills=fills)

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    stem = Path(source_path).stem
    source = generate_wgsl_for_module(mod)

    if shader_name:
        output = out / f"{shader_name}_fill.wgsl"
    else:
        output = out / f"{stem}_gallery.wgsl"
    output.write_text(source, encoding="utf-8")

    entries = [f"{fill.name}_frag" for fill in mod.fills]
    (out / f"{stem}_gallery.wgsl.entries").write_text("\n".join(entries), encoding="utf-8")
    return output
