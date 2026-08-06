#!/usr/bin/env python3
"""
FLOW WGSL Shader Generator
Transpiles @gpu functions to WebGPU Shading Language (WGSL).

The sibling of src/flow/metal_codegen.py: same AST in, a different shading
language out. A Flow kernel written once reaches Metal on a Mac and WebGPU in
a browser, because Flow owns the shader codegen rather than handing the body
to a vendor compiler.

Two places where WGSL is stricter than MSL and the structure has to differ:

  Buffers carry an access mode. Metal binds everything as `device T*`; WGSL
  needs `var<storage, read>` or `var<storage, read_write>` up front. We decide
  per parameter by looking for writes through it in the body.

  Scalars cannot be loose bindings. Metal takes `constant int& n [[buffer(k)]]`;
  WGSL wants a uniform struct. All scalar parameters are packed into one
  `Params` struct, padded to 16 bytes, and referenced as `params.<name>`.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

from .parser import (
    ArrayAccess,
    Assignment,
    BinaryOperation,
    Block,
    Expression,
    FieldAccess,
    ForStatement,
    FunctionCall,
    FunctionDecl,
    IfStatement,
    Literal,
    ReturnStatement,
    Statement,
    Type,
    UnaryOperation,
    VarDecl,
    Variable,
    WhileStatement,
)


class WgslUnsupported(Exception):
    """A construct the WGSL backend cannot express."""


class WgslCodegen:
    """Generate WGSL compute shaders from FLOW @gpu functions."""

    # WGSL has no f64 and no 64-bit integers in the core language.
    TYPE_MAP = {
        "i32": "i32",
        "u32": "u32",
        "f32": "f32",
        "bool": "bool",
        "void": "void",
    }

    UNSUPPORTED_SCALARS = {"i64", "u64", "f64"}

    # WGSL spells its thread identity as builtins on the entry point. These are
    # bound to locals at the top of the kernel body so expressions stay flat.
    GPU_BUILTINS = {
        "gpu_thread_id": "tid",
        "gpu_thread_id_x": "i32(global_id.x)",
        "gpu_thread_id_y": "i32(global_id.y)",
        "gpu_thread_id_z": "i32(global_id.z)",
        "gpu_block_id": "i32(group_id.x)",
        "gpu_block_id_x": "i32(group_id.x)",
        "gpu_block_id_y": "i32(group_id.y)",
        "gpu_block_id_z": "i32(group_id.z)",
        "gpu_local_id": "i32(local_id.x)",
        "gpu_local_id_x": "i32(local_id.x)",
        "gpu_block_size": "WORKGROUP_SIZE",
        "gpu_barrier": "workgroupBarrier()",
        "gpu_sync": "workgroupBarrier()",
    }

    # Flow name -> WGSL name. Most of libm matches; a few do not.
    MATH_FUNCS = {
        "sin": "sin", "cos": "cos", "tan": "tan",
        "asin": "asin", "acos": "acos", "atan": "atan",
        "sqrt": "sqrt", "exp": "exp", "log": "log",
        "abs": "abs", "min": "min", "max": "max",
        "pow": "pow", "floor": "floor", "ceil": "ceil",
        "fabs": "abs", "fabsf": "abs", "sqrtf": "sqrt", "expf": "exp",
        "logf": "log", "sinf": "sin", "cosf": "cos", "powf": "pow",
        "fminf": "min", "fmaxf": "max", "floorf": "floor", "ceilf": "ceil",
    }

    # WGSL keywords plus the spec's reserved-word list. A Flow identifier that
    # lands on one of these gets a trailing underscore; the host never sees the
    # difference because bind groups are addressed by index.
    RESERVED = frozenset(
        """
        alias break case const const_assert continue continuing default diagnostic
        discard else enable false fn for if let loop override requires return
        struct switch true var while
        NULL Self abstract active alignas alignof as asm async attribute auto await
        become binding_array cast catch class compile concept const_cast consteval
        constexpr constinit crate debugger decltype delete demote do dynamic_cast
        enum explicit export extends extern external fallthrough filter final
        finally friend from get goto groupshared highp impl implements import
        inline instanceof interface layout lowp macro match mediump meta mod module
        move mut mutable namespace new nil noexcept noinline null nullptr of
        operator package partition pass precise precision priv protected pub public
        readonly ref regardless register require resource restrict self set shared
        sizeof smooth snorm static std super target template this throw trait try
        type typedef typeid typename typeof union unless unorm unsafe unsized use
        using varying virtual volatile wgsl where with writeonly yield
        """.split()
    )

    def __init__(self, workgroup_size: int = 64):
        self.indent_level = 0
        self.workgroup_size = workgroup_size
        self.kernel_name = ""
        # name -> {"binding", "kind": "storage"|"uniform", "elem", "access"}
        self.bindings: Dict[str, Dict[str, Any]] = {}
        self.scalars: List[Tuple[str, str]] = []  # (name, wgsl type), in order
        self.mutable_locals: set = set()

    # ---- helpers ----------------------------------------------------------

    def indent(self) -> str:
        return "    " * self.indent_level

    def ident(self, name: str) -> str:
        """A Flow identifier as a legal WGSL one."""
        if name in self.RESERVED or name.startswith("__"):
            return name.rstrip("_") + "_"
        return name

    def scalar_type(self, name: str) -> str:
        if name in self.UNSUPPORTED_SCALARS:
            raise WgslUnsupported(
                f"WGSL has no {name}; use f32/i32/u32 in @gpu kernels"
            )
        mapped = self.TYPE_MAP.get(name)
        if mapped is None:
            raise WgslUnsupported(f"no WGSL equivalent for type '{name}'")
        return mapped

    def element_type(self, flow_type: Type) -> str:
        """Element type of a buffer parameter, as WGSL."""
        name = flow_type.name
        if flow_type.element_type is not None:
            return self.scalar_type(flow_type.element_type.name)
        match = re.match(r"(?:array|ptr)<\s*(\w+)", name)
        if match:
            return self.scalar_type(match.group(1))
        if name.startswith("array_"):
            return self.scalar_type(name[len("array_"):])
        raise WgslUnsupported(f"cannot infer element type of '{name}'")

    def is_buffer_type(self, flow_type: Type) -> bool:
        name = flow_type.name
        return (
            name.startswith("array<")
            or name.startswith("array_")
            or name.startswith("ptr<")
            or flow_type.element_type is not None
        )

    # ---- write analysis ---------------------------------------------------

    def _written_buffers(self, block: Block, names: set) -> set:
        """Buffer parameters that appear as an assignment target in the body.

        This is what decides read vs read_write on a storage binding. Doing it
        from the AST beats the usual "does the name contain 'out'" guess.
        """
        found: set = set()

        def base_name(expr: Expression):
            while isinstance(expr, (ArrayAccess, FieldAccess)):
                expr = expr.array if isinstance(expr, ArrayAccess) else expr.object
            return expr.name if isinstance(expr, Variable) else None

        def walk_block(b: Block) -> None:
            for stmt in b.statements:
                walk_stmt(stmt)

        def walk_stmt(stmt: Statement) -> None:
            if isinstance(stmt, Assignment):
                target = stmt.target_expr
                if target is not None:
                    name = base_name(target)
                elif isinstance(stmt.target, str):
                    name = stmt.target
                else:
                    name = base_name(stmt.target)
                if name in names:
                    found.add(name)
            elif isinstance(stmt, IfStatement):
                walk_block(stmt.then_block)
                for _, blk in getattr(stmt, "elif_blocks", None) or []:
                    walk_block(blk)
                if stmt.else_block:
                    walk_block(stmt.else_block)
            elif isinstance(stmt, (WhileStatement, ForStatement)):
                walk_block(stmt.body)

        walk_block(block)
        return found

    # ---- kernel -----------------------------------------------------------

    def generate_kernel(self, func: FunctionDecl) -> str:
        self.kernel_name = func.name
        self.bindings.clear()
        self.scalars.clear()
        self.mutable_locals = set()

        buffer_names = {p.name for p in func.parameters if self.is_buffer_type(p.type)}
        written = self._written_buffers(func.body, buffer_names)

        lines: List[str] = [
            f"// Generated from Flow @gpu function `{func.name}` by src/flow/wgsl_codegen.py",
            f"const WORKGROUP_SIZE: i32 = {self.workgroup_size};",
            "",
        ]

        binding = 0
        for param in func.parameters:
            if self.is_buffer_type(param.type):
                elem = self.element_type(param.type)
                access = "read_write" if param.name in written else "read"
                self.bindings[param.name] = {
                    "binding": binding,
                    "kind": "storage",
                    "elem": elem,
                    "access": access,
                }
                lines.append(
                    f"@group(0) @binding({binding}) "
                    f"var<storage, {access}> {self.ident(param.name)}: array<{elem}>;"
                )
                binding += 1
            else:
                self.scalars.append((param.name, self.scalar_type(param.type.name)))

        # Scalars ride in one uniform block. WGSL requires a uniform buffer to
        # be a multiple of 16 bytes, so pad out the tail.
        if self.scalars:
            lines.append("")
            lines.append("struct Params {")
            for name, wgsl_type in self.scalars:
                lines.append(f"    {self.ident(name)}: {wgsl_type},")
            pad = (-len(self.scalars)) % 4
            for i in range(pad):
                lines.append(f"    _pad{i}: u32,")
            lines.append("};")
            lines.append(
                f"@group(0) @binding({binding}) var<uniform> params: Params;"
            )
            self.params_binding = binding
            binding += 1
        else:
            self.params_binding = None

        lines.append("")
        lines.append(f"@compute @workgroup_size({self.workgroup_size})")
        lines.append(f"fn {self.ident(func.name)}(")
        lines.append("    @builtin(global_invocation_id) global_id: vec3<u32>,")
        lines.append("    @builtin(workgroup_id) group_id: vec3<u32>,")
        lines.append("    @builtin(local_invocation_id) local_id: vec3<u32>,")
        lines.append(") {")

        self.indent_level = 1
        lines.append(f"{self.indent()}let tid: i32 = i32(global_id.x);")
        lines.extend(self.generate_block(func.body))
        self.indent_level = 0
        lines.append("}")

        return "\n".join(lines) + "\n"

    # ---- statements -------------------------------------------------------

    def generate_block(self, block: Block) -> List[str]:
        lines: List[str] = []
        for stmt in block.statements:
            lines.extend(self.generate_statement(stmt))
        return lines

    def generate_statement(self, stmt: Statement) -> List[str]:
        if isinstance(stmt, VarDecl):
            return self.generate_var_decl(stmt)
        if isinstance(stmt, Assignment):
            return self.generate_assignment(stmt)
        if isinstance(stmt, IfStatement):
            return self.generate_if(stmt)
        if isinstance(stmt, WhileStatement):
            return self.generate_while(stmt)
        if isinstance(stmt, ForStatement):
            return self.generate_for(stmt)
        if isinstance(stmt, ReturnStatement):
            return self.generate_return(stmt)
        if isinstance(stmt, Expression):
            return [f"{self.indent()}{self.generate_expression(stmt)};"]
        raise WgslUnsupported(f"statement {type(stmt).__name__} in a @gpu kernel")

    def generate_var_decl(self, decl: VarDecl) -> List[str]:
        keyword = "var" if decl.is_mutable else "let"
        if decl.is_mutable:
            self.mutable_locals.add(decl.name)
        wgsl_type = self.scalar_type(decl.type.name)
        name = self.ident(decl.name)
        if decl.initializer is not None:
            init = self.generate_expression(decl.initializer)
            return [f"{self.indent()}{keyword} {name}: {wgsl_type} = {init};"]
        # WGSL has no uninitialised `let`.
        return [f"{self.indent()}var {name}: {wgsl_type};"]

    def generate_assignment(self, assign: Assignment) -> List[str]:
        if assign.target_expr is not None:
            target = self.generate_expression(assign.target_expr)
        elif isinstance(assign.target, str):
            target = self.resolve_name(assign.target)
        else:
            target = self.generate_expression(assign.target)
        value = self.generate_expression(assign.value)
        return [f"{self.indent()}{target} = {value};"]

    def generate_if(self, stmt: IfStatement) -> List[str]:
        lines = [f"{self.indent()}if ({self.generate_expression(stmt.condition)}) {{"]
        self.indent_level += 1
        lines.extend(self.generate_block(stmt.then_block))
        self.indent_level -= 1

        # metal_codegen drops elif chains; keep them.
        for cond, blk in getattr(stmt, "elif_blocks", None) or []:
            lines.append(
                f"{self.indent()}}} else if ({self.generate_expression(cond)}) {{"
            )
            self.indent_level += 1
            lines.extend(self.generate_block(blk))
            self.indent_level -= 1

        if stmt.else_block:
            lines.append(f"{self.indent()}}} else {{")
            self.indent_level += 1
            lines.extend(self.generate_block(stmt.else_block))
            self.indent_level -= 1

        lines.append(f"{self.indent()}}}")
        return lines

    def generate_while(self, stmt: WhileStatement) -> List[str]:
        lines = [f"{self.indent()}while ({self.generate_expression(stmt.condition)}) {{"]
        self.indent_level += 1
        lines.extend(self.generate_block(stmt.body))
        self.indent_level -= 1
        lines.append(f"{self.indent()}}}")
        return lines

    def generate_for(self, stmt: ForStatement) -> List[str]:
        # Field names are range_start / range_end, not start / end.
        var = self.ident(stmt.variable)
        start = self.generate_expression(stmt.range_start)
        end = self.generate_expression(stmt.range_end)
        step = self.generate_expression(stmt.step) if stmt.step is not None else "1"
        lines = [
            f"{self.indent()}for (var {var}: i32 = {start}; {var} < {end}; "
            f"{var} = {var} + {step}) {{"
        ]
        self.indent_level += 1
        lines.extend(self.generate_block(stmt.body))
        self.indent_level -= 1
        lines.append(f"{self.indent()}}}")
        return lines

    def generate_return(self, stmt: ReturnStatement) -> List[str]:
        if stmt.value is not None:
            raise WgslUnsupported(
                "a WGSL compute entry point returns nothing; write results to a buffer"
            )
        return [f"{self.indent()}return;"]

    # ---- expressions ------------------------------------------------------

    def generate_expression(self, expr: Expression) -> str:
        if isinstance(expr, Literal):
            return self.generate_literal(expr)

        if isinstance(expr, Variable):
            return self.resolve_name(expr.name)

        if isinstance(expr, BinaryOperation):
            left = self.generate_expression(expr.left)
            right = self.generate_expression(expr.right)
            op = {"and": "&&", "or": "||", "not": "!"}.get(
                expr.operator, expr.operator
            )
            return f"({left} {op} {right})"

        if isinstance(expr, UnaryOperation):
            op = "!" if expr.operator in ("not", "!") else expr.operator
            return f"({op}{self.generate_expression(expr.operand)})"

        if isinstance(expr, FunctionCall):
            return self.generate_call(expr)

        if isinstance(expr, ArrayAccess):
            array = self.generate_expression(expr.array)
            index = self.generate_expression(expr.index)
            return f"{array}[{index}]"

        if isinstance(expr, FieldAccess):
            return f"{self.generate_expression(expr.object)}.{expr.field}"

        raise WgslUnsupported(f"expression {type(expr).__name__} in a @gpu kernel")

    def generate_literal(self, expr: Literal) -> str:
        type_name = getattr(expr.type, "name", expr.type)
        value = str(expr.value)
        if type_name in ("float", "f32", "f64"):
            # WGSL infers abstract float; a bare 1.0 is fine and converts.
            return value if "." in value or "e" in value.lower() else value + ".0"
        if type_name in ("bool",):
            return "true" if value in ("true", "True", "1") else "false"
        return value

    def resolve_name(self, name: str) -> str:
        if name in self.GPU_BUILTINS:
            return self.GPU_BUILTINS[name]
        if any(name == scalar for scalar, _ in self.scalars):
            return f"params.{self.ident(name)}"
        return self.ident(name)

    def generate_call(self, expr: FunctionCall) -> str:
        name = expr.name
        if name in self.GPU_BUILTINS:
            return self.GPU_BUILTINS[name]
        if name in self.MATH_FUNCS:
            args = ", ".join(self.generate_expression(a) for a in expr.arguments)
            return f"{self.MATH_FUNCS[name]}({args})"
        if name in self.TYPE_MAP.values():
            # A cast written as a call, e.g. f32(x).
            args = ", ".join(self.generate_expression(a) for a in expr.arguments)
            return f"{name}({args})"
        raise WgslUnsupported(
            f"call to '{name}' in a @gpu kernel has no WGSL equivalent"
        )

    # ---- reflection for the host ------------------------------------------

    def binding_layout(self, func: FunctionDecl) -> Dict[str, Any]:
        """Everything a WebGPU host needs to build the bind group.

        Emitted next to the .wgsl so the JS side never has to re-parse Flow.
        """
        buffers = []
        for name, info in self.bindings.items():
            buffers.append(
                {
                    "name": name,
                    "binding": info["binding"],
                    "type": "storage",
                    "access": info["access"],
                    "element": info["elem"],
                }
            )
        return {
            "kernel": func.name,
            "entryPoint": func.name,
            "workgroupSize": self.workgroup_size,
            "buffers": sorted(buffers, key=lambda b: b["binding"]),
            "params": [{"name": n, "type": t} for n, t in self.scalars],
            "paramsBinding": self.params_binding,
            # Uniform blocks are padded up to a multiple of 16 bytes.
            "paramsBytes": ((len(self.scalars) + 3) // 4) * 16 if self.scalars else 0,
        }


def extract_gpu_functions(declarations: List[Any]) -> List[FunctionDecl]:
    """Every @gpu annotated function in a resolved module."""
    return [
        decl
        for decl in declarations
        if isinstance(decl, FunctionDecl) and "gpu" in decl.attributes
    ]


def generate_wgsl_shaders(
    declarations: List[Any],
    output_dir: str = "build/wgsl",
    workgroup_size: int = 64,
) -> List[Tuple[str, str, Dict[str, Any]]]:
    """Write one .wgsl per @gpu function.

    Returns (kernel_name, shader_path, binding_layout) per kernel.
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    results = []
    for func in extract_gpu_functions(declarations):
        codegen = WgslCodegen(workgroup_size=workgroup_size)
        source = codegen.generate_kernel(func)
        path = out / f"{func.name}.wgsl"
        path.write_text(source)
        results.append((func.name, str(path), codegen.binding_layout(func)))
    return results
