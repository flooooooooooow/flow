#!/usr/bin/env python3
"""
FLOW to C Generator

This backend exists so `flow run` can actually execute programs today,
without relying on MLIR lowering being correct yet.

Supported subset:
- i32/bool literals and variables
- let declarations + assignments
- if/else (single else block)
- while
- return
- function calls
- binary + - * / % == != < <= > >= && ||
- unary - !

Not supported yet:
- pointers/arrays/structs/for/parallel
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .parser import (
    Assignment,
    BinaryOperation,
    Block,
    Expression,
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
    StructLiteral,
    FieldAccess,
)


class CGenerator:
    def __init__(self) -> None:
        self._indent = 0
        self._structs = {}  # name -> dict of field_name -> field_type
        self._var_types = {}  # name -> Type

    def _i(self) -> str:
        return "    " * self._indent

    def generate_translation_unit(self, functions: List[FunctionDecl]) -> str:
        lines: List[str] = []
        lines.append("#include <stdint.h>")
        lines.append("#include <stdio.h>")
        lines.append("")

        # Collect struct types from functions
        for fn in functions:
            self._collect_structs_from_function(fn)

        # Emit struct definitions in dependency order
        emitted = set()
        def emit_struct(name):
            if name in emitted:
                return
            # First, emit any nested struct types
            for field_type in self._structs[name].values():
                if self._is_struct_type(field_type) and field_type.name not in emitted:
                    emit_struct(field_type.name)
            
            # Now emit this struct
            lines.append(f"typedef struct {{")
            for field_name, field_type in sorted(self._structs[name].items()):
                lines.append(f"    {self._c_type(field_type)} {field_name};")
            lines.append(f"}} {name};")
            lines.append("")
            emitted.add(name)
        
        for struct_name in sorted(self._structs.keys()):
            emit_struct(struct_name)

        # Forward declarations
        for fn in functions:
            lines.append(self._c_function_decl(fn) + ";")
        lines.append("")

        # Definitions
        for fn in functions:
            lines.extend(self._gen_function(fn))
            lines.append("")

        return "\n".join(lines).rstrip() + "\n"

    def _collect_structs_from_function(self, fn: FunctionDecl) -> None:
        # Collect from parameter types
        for param in fn.parameters:
            if self._is_struct_type(param.type):
                if param.type.name not in self._structs:
                    self._structs[param.type.name] = {}
        
        # Collect from return type
        if self._is_struct_type(fn.return_type):
            if fn.return_type.name not in self._structs:
                self._structs[fn.return_type.name] = {}
        
        # Collect from function body
        self._collect_structs_from_block(fn.body)

    def _collect_structs_from_block(self, block: Block) -> None:
        for stmt in block.statements:
            self._collect_structs_from_statement(stmt)

    def _collect_structs_from_statement(self, stmt: Statement) -> None:
        if isinstance(stmt, VarDecl):
            # Track variable type
            self._var_types[stmt.name] = stmt.type
            
            if self._is_struct_type(stmt.type):
                if stmt.type.name not in self._structs:
                    self._structs[stmt.type.name] = {}
            if stmt.initializer:
                # If this is a struct declaration with a struct literal, infer field types
                if self._is_struct_type(stmt.type) and isinstance(stmt.initializer, StructLiteral):
                    for field_name, field_value in stmt.initializer.fields:
                        field_type = self._infer_expr_type(field_value)
                        self._structs[stmt.type.name][field_name] = field_type
                self._collect_structs_from_expr(stmt.initializer)
        elif isinstance(stmt, Assignment):
            self._collect_structs_from_expr(stmt.value)
        elif isinstance(stmt, ReturnStatement):
            if stmt.value:
                self._collect_structs_from_expr(stmt.value)
        elif isinstance(stmt, IfStatement):
            self._collect_structs_from_expr(stmt.condition)
            self._collect_structs_from_block(stmt.then_block)
            for elif_condition, elif_block in stmt.elif_blocks:
                self._collect_structs_from_expr(elif_condition)
                self._collect_structs_from_block(elif_block)
            if stmt.else_block:
                self._collect_structs_from_block(stmt.else_block)
        elif isinstance(stmt, WhileStatement):
            self._collect_structs_from_expr(stmt.condition)
            self._collect_structs_from_block(stmt.body)
        else:
            # Expression statement
            self._collect_structs_from_expr(stmt)

    def _collect_structs_from_expr(self, expr: Expression) -> None:
        if isinstance(expr, StructLiteral):
            if expr.struct_name not in self._structs:
                self._structs[expr.struct_name] = {}
            for field_name, field_value in expr.fields:
                # Infer field type from expression (simplified: assume i32 for literals)
                field_type = self._infer_expr_type(field_value)
                self._structs[expr.struct_name][field_name] = field_type
                self._collect_structs_from_expr(field_value)
        elif isinstance(expr, FieldAccess):
            self._collect_structs_from_expr(expr.object)
        elif isinstance(expr, BinaryOperation):
            self._collect_structs_from_expr(expr.left)
            self._collect_structs_from_expr(expr.right)
        elif isinstance(expr, UnaryOperation):
            self._collect_structs_from_expr(expr.operand)
        elif isinstance(expr, FunctionCall):
            for arg in expr.arguments:
                self._collect_structs_from_expr(arg)

    def _infer_expr_type(self, expr: Expression) -> Type:
        if isinstance(expr, Literal):
            return Type("i32")  # Simplified: all literals are i32
        elif isinstance(expr, Variable):
            # Look up variable type from our tracking
            if expr.name in self._var_types:
                return self._var_types[expr.name]
            return Type("i32")  # Default fallback
        elif isinstance(expr, StructLiteral):
            return Type(expr.struct_name)
        else:
            return Type("i32")  # Default fallback

    def _is_struct_type(self, t: Type) -> bool:
        return t.name not in ["i32", "bool", "void", "i8", "i16", "i64", "i128", 
                             "u8", "u16", "u32", "u64", "u128", "f32", "f64"]

    def _c_type(self, t: Type) -> str:
        if t.name == "i32":
            return "int32_t"
        if t.name == "i64":
            return "int64_t"
        if t.name == "i8":
            return "int8_t"
        if t.name == "i16":
            return "int16_t"
        if t.name == "u8":
            return "uint8_t"
        if t.name == "u16":
            return "uint16_t"
        if t.name == "u32":
            return "uint32_t"
        if t.name == "u64":
            return "uint64_t"
        if t.name == "f32":
            return "float"
        if t.name == "f64":
            return "double"
        if t.name == "bool":
            return "int32_t"  # keep simple; 0/1
        if t.name == "void":
            return "void"
        # Struct types
        return t.name

    def _c_function_decl(self, fn: FunctionDecl) -> str:
        ret = self._c_type(fn.return_type)
        params = ", ".join([f"{self._c_type(p.type)} {p.name}" for p in fn.parameters])
        return f"{ret} {fn.name}({params})"

    def _gen_function(self, fn: FunctionDecl) -> List[str]:
        lines: List[str] = []
        lines.append(self._c_function_decl(fn) + " {")
        self._indent += 1
        lines.extend(self._gen_block(fn.body))
        self._indent -= 1
        lines.append("}")
        return lines

    def _gen_block(self, block: Block) -> List[str]:
        lines: List[str] = []
        for st in block.statements:
            lines.extend(self._gen_statement(st))
        return lines

    def _gen_statement(self, st: Statement) -> List[str]:
        if isinstance(st, VarDecl):
            c_t = self._c_type(st.type)
            if st.initializer is None:
                return [f"{self._i()}{c_t} {st.name};"]
            return [f"{self._i()}{c_t} {st.name} = {self._gen_expr(st.initializer)};"]

        if isinstance(st, Assignment):
            return [f"{self._i()}{st.target} = {self._gen_expr(st.value)};"]

        if isinstance(st, ReturnStatement):
            if st.value is None:
                return [f"{self._i()}return;"]
            return [f"{self._i()}return {self._gen_expr(st.value)};"]

        if isinstance(st, IfStatement):
            return self._gen_if(st)

        if isinstance(st, WhileStatement):
            return self._gen_while(st)

        # Expression statement
        if isinstance(st, (Literal, Variable, BinaryOperation, UnaryOperation, FunctionCall)):
            return [f"{self._i()}{self._gen_expr(st)};"]

        raise NotImplementedError(f"Unsupported statement: {type(st)}")

    def _gen_if(self, st: IfStatement) -> List[str]:
        lines: List[str] = []
        lines.append(f"{self._i()}if ({self._gen_expr(st.condition)}) {{")
        self._indent += 1
        lines.extend(self._gen_block(st.then_block))
        self._indent -= 1
        
        # Generate elif blocks
        for elif_condition, elif_block in st.elif_blocks:
            lines.append(f"{self._i()}}} else if ({self._gen_expr(elif_condition)}) {{")
            self._indent += 1
            lines.extend(self._gen_block(elif_block))
            self._indent -= 1
        
        # Generate else block if present
        if st.else_block is not None:
            lines.append(f"{self._i()}}} else {{")
            self._indent += 1
            lines.extend(self._gen_block(st.else_block))
            self._indent -= 1
        
        lines.append(f"{self._i()}}}")
        return lines

    def _gen_while(self, st: WhileStatement) -> List[str]:
        lines: List[str] = []
        lines.append(f"{self._i()}while ({self._gen_expr(st.condition)}) {{")
        self._indent += 1
        lines.extend(self._gen_block(st.body))
        self._indent -= 1
        lines.append(f"{self._i()}}}")
        return lines

    def _gen_expr(self, e: Expression) -> str:
        if isinstance(e, Literal):
            if e.type.name == "bool":
                return "1" if e.value == "true" else "0"
            return e.value

        if isinstance(e, Variable):
            return e.name

        if isinstance(e, StructLiteral):
            fields = ", ".join([f".{name} = {self._gen_expr(value)}" for name, value in e.fields])
            return f"({e.struct_name}){{ {fields} }}"

        if isinstance(e, FieldAccess):
            return f"{self._gen_expr(e.object)}.{e.field}"

        if isinstance(e, UnaryOperation):
            op = e.operator
            if op == "!":
                return f"(!{self._gen_expr(e.operand)})"
            if op == "-":
                return f"(-{self._gen_expr(e.operand)})"
            return f"({op}{self._gen_expr(e.operand)})"

        if isinstance(e, BinaryOperation):
            return f"({self._gen_expr(e.left)} {e.operator} {self._gen_expr(e.right)})"

        if isinstance(e, FunctionCall):
            args = ", ".join(self._gen_expr(a) for a in e.arguments)
            return f"{e.name}({args})"

        raise NotImplementedError(f"Unsupported expression: {type(e)}")


def flow_to_c(functions: List[FunctionDecl]) -> str:
    return CGenerator().generate_translation_unit(functions)
