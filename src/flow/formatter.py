"""
FLOW Code Formatter - Formats FLOW source code according to style guidelines.
"""

from __future__ import annotations
from typing import List
from .parser import (
    parse_flow_code,
    FunctionDecl,
    StructDecl,
    ImportDecl,
    VarDecl,
    ReturnStatement,
    IfStatement,
    Block,
    BinaryOperation,
    FunctionCall,
    Literal,
    Variable,
    StructLiteral,
    Type,
)


class Formatter:
    def __init__(self, indent_size: int = 4):
        self.indent_size = indent_size

    def format_file(self, source: str) -> str:
        declarations = parse_flow_code(source)
        return self.format_declarations(declarations)

    def format_declarations(self, declarations: List) -> str:
        lines = []
        for decl in declarations:
            if isinstance(decl, ImportDecl):
                lines.append(f'import "{decl.path}"')
            elif isinstance(decl, StructDecl):
                lines.extend(self._format_struct(decl))
            elif isinstance(decl, FunctionDecl):
                lines.extend(self._format_function(decl))
            lines.append("")
        return "\n".join(lines)

    def _format_struct(self, decl: StructDecl) -> List[str]:
        lines = [f"struct {decl.name} {{"]
        for field in decl.fields:
            lines.append(f"    {field.name}: {self._format_type(field.type)}")
        lines.append("}")
        return lines

    def _format_function(self, decl: FunctionDecl) -> List[str]:
        params = ", ".join(
            f"{p.name}: {self._format_type(p.type)}" for p in decl.parameters
        )
        ret = self._format_type(decl.return_type)
        lines = [f"function {decl.name}({params}) -> {ret} {{"]
        lines.extend(self._format_block(decl.body, 1))
        lines.append("}")
        return lines

    def _format_block(self, block: Block, indent: int) -> List[str]:
        lines = []
        for stmt in block.statements:
            lines.extend(self._format_stmt(stmt, indent))
        return lines

    def _format_stmt(self, stmt, indent: int) -> List[str]:
        prefix = "    " * indent
        if isinstance(stmt, VarDecl):
            init = (
                f" = {self._format_expr(stmt.initializer)}" if stmt.initializer else ""
            )
            return [f"{prefix}let {stmt.name}: {self._format_type(stmt.type)}{init}"]
        elif isinstance(stmt, ReturnStatement):
            val = f" {self._format_expr(stmt.value)}" if stmt.value else ""
            return [f"{prefix}return{val}"]
        elif isinstance(stmt, IfStatement):
            lines = [f"{prefix}if {self._format_expr(stmt.condition)} {{"]
            lines.extend(self._format_block(stmt.then_block, indent + 1))

            # Handle elif blocks
            if hasattr(stmt, "elif_blocks") and stmt.elif_blocks:
                for elif_cond, elif_block in stmt.elif_blocks:
                    lines.append(f"{prefix}}} else if {self._format_expr(elif_cond)} {{")
                    lines.extend(self._format_block(elif_block, indent + 1))

            if stmt.else_block:
                lines.append(f"{prefix}}} else {{")
                lines.extend(self._format_block(stmt.else_block, indent + 1))
            lines.append(f"{prefix}}}")
            return lines
        else:
            return [f"{prefix}{self._format_expr(stmt)}"]

    def _format_expr(self, expr) -> str:
        if isinstance(expr, Literal):
            return str(expr.value)
        elif isinstance(expr, Variable):
            return expr.name
        elif isinstance(expr, BinaryOperation):
            return f"{self._format_expr(expr.left)} {expr.operator} {self._format_expr(expr.right)}"
        elif isinstance(expr, FunctionCall):
            args = ", ".join(self._format_expr(a) for a in expr.arguments)
            return f"{expr.name}({args})"
        elif isinstance(expr, StructLiteral):
            fields = ", ".join(f"{n}: {self._format_expr(v)}" for n, v in expr.fields)
            return f"{expr.struct_name} {{ {fields} }}"
        return "<expr>"

    def _format_type(self, t: Type) -> str:
        if not t:
            return "void"
        if t.element_type:
            return f"array<{self._format_type(t.element_type)}>"
        return t.name


def format_file(filepath: str, check_only: bool = False) -> bool:
    with open(filepath, "r") as f:
        original = f.read()
    formatter = Formatter()
    try:
        formatted = formatter.format_file(original)
    except Exception as e:
        print(f"Error: {e}")
        return False
    if original == formatted:
        return True
    if check_only:
        print(f"Would reformat {filepath}")
        return False
    with open(filepath, "w") as f:
        f.write(formatted)
    return True
