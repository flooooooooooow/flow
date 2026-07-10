#!/usr/bin/env python3
"""
MLIR GPU codegen for @gpu functions.
Emits MLIR GPU dialect suitable for SPIR-V lowering.
"""

from typing import List, Dict, Tuple
from .parser import (
    FunctionDecl,
    Statement,
    Expression,
    VarDecl,
    Assignment,
    IfStatement,
    ForStatement,
    ReturnStatement,
    Literal,
    Variable,
    BinaryOperation,
    UnaryOperation,
    FunctionCall,
    ArrayAccess,
    Type,
    Block,
)


class MLIRGpuGenerator:
    def __init__(self):
        self.indent_level = 0
        self.ssa_counter = 0
        self.symbol_table: Dict[str, Dict[str, str]] = {}

    def indent(self) -> str:
        return "    " * self.indent_level

    def new_ssa(self) -> str:
        self.ssa_counter += 1
        return f"%{self.ssa_counter}"

    def flow_type_to_mlir(self, flow_type: Type) -> str:
        if flow_type.name in ["i32", "i64", "u32", "u64", "f32", "f64"]:
            return flow_type.name
        if flow_type.name == "bool":
            return "i1"
        if flow_type.name.startswith("array_") or flow_type.name.startswith("array"):
            if flow_type.size and flow_type.element_type:
                return f"memref<{flow_type.size}x{flow_type.element_type.name}>"
            if flow_type.element_type:
                return f"memref<?x{flow_type.element_type.name}>"
            return "memref<?xi32>"
        if flow_type.is_pointer:
            return "memref<?xi8>"
        return "i32"

    def infer_expr_type(self, expr: Expression) -> Type:
        if isinstance(expr, Literal):
            return expr.type
        if isinstance(expr, Variable):
            info = self.symbol_table.get(expr.name)
            if info and "flow_type" in info:
                return info["flow_type"]
        if isinstance(expr, ArrayAccess):
            arr_type = self.infer_expr_type(expr.array)
            if arr_type.element_type:
                return arr_type.element_type
        if isinstance(expr, BinaryOperation):
            left = self.infer_expr_type(expr.left)
            right = self.infer_expr_type(expr.right)
            if left.name in ["f32", "f64"] or right.name in ["f32", "f64"]:
                return Type("f32") if left.name == "f32" or right.name == "f32" else Type("f64")
            return left
        if isinstance(expr, FunctionCall):
            if expr.name.startswith("gpu_thread_id") or expr.name.startswith("gpu_block_id") or expr.name.startswith("gpu_local_id"):
                return Type("i32")
        return Type("i32")

    def ensure_index(self, ssa: str, ssa_type: str, ops: List[str]) -> str:
        if ssa_type == "index":
            return ssa
        cast = self.new_ssa()
        ops.append(f"{self.indent()}{cast} = arith.index_cast {ssa} : {ssa_type} to index")
        return cast

    def generate_expression(self, expr: Expression) -> Tuple[str, str, List[str]]:
        ops: List[str] = []
        if isinstance(expr, Literal):
            mlir_type = self.flow_type_to_mlir(expr.type)
            if expr.type.name == "bool":
                val = "1" if expr.value == "true" else "0"
                ssa = self.new_ssa()
                ops.append(f"{self.indent()}{ssa} = arith.constant {val} : {mlir_type}")
                return ssa, mlir_type, ops
            ssa = self.new_ssa()
            ops.append(f"{self.indent()}{ssa} = arith.constant {expr.value} : {mlir_type}")
            return ssa, mlir_type, ops

        if isinstance(expr, Variable):
            info = self.symbol_table.get(expr.name)
            if not info:
                ssa = self.new_ssa()
                ops.append(f"{self.indent()}// Unknown var {expr.name}")
                return ssa, "i32", ops
            return info["ssa"], info["mlir_type"], ops

        if isinstance(expr, FunctionCall):
            def dim_index(kind: str, axis: str) -> Tuple[str, List[str]]:
                ssa_idx = self.new_ssa()
                ops.append(f"{self.indent()}{ssa_idx} = gpu.{kind} {axis}")
                ssa_i32 = self.new_ssa()
                ops.append(f"{self.indent()}{ssa_i32} = arith.index_cast {ssa_idx} : index to i32")
                return ssa_i32, ops

            if expr.name in ["gpu_thread_id", "gpu_thread_id_x"]:
                # global id = block_id * block_dim + thread_id
                block_id, _ = dim_index("block_id", "x")
                block_dim, _ = dim_index("block_dim", "x")
                thread_id, _ = dim_index("thread_id", "x")
                mul = self.new_ssa()
                ops.append(f"{self.indent()}{mul} = arith.muli {block_id}, {block_dim} : i32")
                add = self.new_ssa()
                ops.append(f"{self.indent()}{add} = arith.addi {mul}, {thread_id} : i32")
                return add, "i32", ops
            if expr.name in ["gpu_thread_id_y"]:
                block_id, _ = dim_index("block_id", "y")
                block_dim, _ = dim_index("block_dim", "y")
                thread_id, _ = dim_index("thread_id", "y")
                mul = self.new_ssa()
                ops.append(f"{self.indent()}{mul} = arith.muli {block_id}, {block_dim} : i32")
                add = self.new_ssa()
                ops.append(f"{self.indent()}{add} = arith.addi {mul}, {thread_id} : i32")
                return add, "i32", ops
            if expr.name in ["gpu_thread_id_z"]:
                block_id, _ = dim_index("block_id", "z")
                block_dim, _ = dim_index("block_dim", "z")
                thread_id, _ = dim_index("thread_id", "z")
                mul = self.new_ssa()
                ops.append(f"{self.indent()}{mul} = arith.muli {block_id}, {block_dim} : i32")
                add = self.new_ssa()
                ops.append(f"{self.indent()}{add} = arith.addi {mul}, {thread_id} : i32")
                return add, "i32", ops
            if expr.name in ["gpu_local_id", "gpu_local_id_x"]:
                tid, _ = dim_index("thread_id", "x")
                return tid, "i32", ops
            if expr.name in ["gpu_local_id_y"]:
                tid, _ = dim_index("thread_id", "y")
                return tid, "i32", ops
            if expr.name in ["gpu_local_id_z"]:
                tid, _ = dim_index("thread_id", "z")
                return tid, "i32", ops
            if expr.name in ["gpu_block_id", "gpu_block_id_x"]:
                bid, _ = dim_index("block_id", "x")
                return bid, "i32", ops
            if expr.name in ["gpu_block_id_y"]:
                bid, _ = dim_index("block_id", "y")
                return bid, "i32", ops
            if expr.name in ["gpu_block_id_z"]:
                bid, _ = dim_index("block_id", "z")
                return bid, "i32", ops
            if expr.name in ["gpu_block_size", "gpu_block_size_x"]:
                bdim, _ = dim_index("block_dim", "x")
                return bdim, "i32", ops
            if expr.name in ["gpu_block_size_y"]:
                bdim, _ = dim_index("block_dim", "y")
                return bdim, "i32", ops
            if expr.name in ["gpu_block_size_z"]:
                bdim, _ = dim_index("block_dim", "z")
                return bdim, "i32", ops
            if expr.name in ["gpu_grid_size", "gpu_grid_size_x"]:
                gdim, _ = dim_index("grid_dim", "x")
                return gdim, "i32", ops
            if expr.name in ["gpu_grid_size_y"]:
                gdim, _ = dim_index("grid_dim", "y")
                return gdim, "i32", ops
            if expr.name in ["gpu_grid_size_z"]:
                gdim, _ = dim_index("grid_dim", "z")
                return gdim, "i32", ops

        if isinstance(expr, UnaryOperation):
            operand_ssa, operand_type, operand_ops = self.generate_expression(expr.operand)
            ops.extend(operand_ops)
            ssa = self.new_ssa()
            if expr.operator == "-":
                if operand_type in ["f32", "f64"]:
                    ops.append(f"{self.indent()}{ssa} = arith.negf {operand_ssa} : {operand_type}")
                else:
                    ops.append(f"{self.indent()}{ssa} = arith.subi {operand_ssa}, 0 : {operand_type}")
            elif expr.operator in ["!", "not"]:
                ops.append(f"{self.indent()}{ssa} = arith.xori {operand_ssa}, 1 : {operand_type}")
            else:
                ops.append(f"{self.indent()}// Unsupported unary op {expr.operator}")
            return ssa, operand_type, ops

        if isinstance(expr, ArrayAccess):
            arr_ssa, arr_type, arr_ops = self.generate_expression(expr.array)
            ops.extend(arr_ops)
            idx_ssa, idx_type, idx_ops = self.generate_expression(expr.index)
            ops.extend(idx_ops)
            idx_final = self.ensure_index(idx_ssa, idx_type, ops)
            # element type from memref
            elem_type = "f32"
            if "i32" in arr_type:
                elem_type = "i32"
            if "f64" in arr_type:
                elem_type = "f64"
            ssa = self.new_ssa()
            ops.append(f"{self.indent()}{ssa} = memref.load {arr_ssa}[{idx_final}] : {arr_type}")
            return ssa, elem_type, ops

        if isinstance(expr, BinaryOperation):
            left_ssa, left_type, left_ops = self.generate_expression(expr.left)
            right_ssa, right_type, right_ops = self.generate_expression(expr.right)
            ops.extend(left_ops)
            ops.extend(right_ops)

            # Comparison
            if expr.operator in ["<", "<=", ">", ">=", "==", "!="]:
                ssa = self.new_ssa()
                if left_type in ["f32", "f64"] or right_type in ["f32", "f64"]:
                    pred = {
                        "<": "olt",
                        "<=": "ole",
                        ">": "ogt",
                        ">=": "oge",
                        "==": "oeq",
                        "!=": "one",
                    }[expr.operator]
                    ops.append(f"{self.indent()}{ssa} = arith.cmpf {pred}, {left_ssa}, {right_ssa} : {left_type}")
                else:
                    pred = {
                        "<": "slt",
                        "<=": "sle",
                        ">": "sgt",
                        ">=": "sge",
                        "==": "eq",
                        "!=": "ne",
                    }[expr.operator]
                    ops.append(f"{self.indent()}{ssa} = arith.cmpi {pred}, {left_ssa}, {right_ssa} : {left_type}")
                return ssa, "i1", ops

            # Arithmetic
            ssa = self.new_ssa()
            is_float = left_type in ["f32", "f64"] or right_type in ["f32", "f64"]
            if expr.operator == "+":
                if is_float:
                    ops.append(f"{self.indent()}{ssa} = arith.addf {left_ssa}, {right_ssa} : {left_type}")
                else:
                    ops.append(f"{self.indent()}{ssa} = arith.addi {left_ssa}, {right_ssa} : {left_type}")
            elif expr.operator == "-":
                if is_float:
                    ops.append(f"{self.indent()}{ssa} = arith.subf {left_ssa}, {right_ssa} : {left_type}")
                else:
                    ops.append(f"{self.indent()}{ssa} = arith.subi {left_ssa}, {right_ssa} : {left_type}")
            elif expr.operator == "*":
                if is_float:
                    ops.append(f"{self.indent()}{ssa} = arith.mulf {left_ssa}, {right_ssa} : {left_type}")
                else:
                    ops.append(f"{self.indent()}{ssa} = arith.muli {left_ssa}, {right_ssa} : {left_type}")
            elif expr.operator == "/":
                if is_float:
                    ops.append(f"{self.indent()}{ssa} = arith.divf {left_ssa}, {right_ssa} : {left_type}")
                else:
                    ops.append(f"{self.indent()}{ssa} = arith.divsi {left_ssa}, {right_ssa} : {left_type}")
            else:
                ops.append(f"{self.indent()}// Unsupported binary op {expr.operator}")
            return ssa, left_type, ops

        ssa = self.new_ssa()
        ops.append(f"{self.indent()}// Unsupported expression")
        return ssa, "i32", ops

    def generate_statement(self, stmt: Statement) -> List[str]:
        lines: List[str] = []
        if isinstance(stmt, VarDecl):
            if stmt.initializer is None:
                # uninitialized scalars not supported in GPU kernels
                lines.append(f"{self.indent()}// Uninitialized var {stmt.name}")
                return lines
            value_ssa, value_type, value_ops = self.generate_expression(stmt.initializer)
            lines.extend(value_ops)
            self.symbol_table[stmt.name] = {
                "ssa": value_ssa,
                "mlir_type": value_type,
                "flow_type": stmt.type,
            }
            return lines

        if isinstance(stmt, Assignment):
            value_ssa, value_type, value_ops = self.generate_expression(stmt.value)
            lines.extend(value_ops)
            if stmt.target_expr is not None and isinstance(stmt.target_expr, ArrayAccess):
                arr_ssa, arr_type, arr_ops = self.generate_expression(stmt.target_expr.array)
                lines.extend(arr_ops)
                idx_ssa, idx_type, idx_ops = self.generate_expression(stmt.target_expr.index)
                lines.extend(idx_ops)
                idx_final = self.ensure_index(idx_ssa, idx_type, lines)
                lines.append(f"{self.indent()}memref.store {value_ssa}, {arr_ssa}[{idx_final}] : {arr_type}")
                return lines
            if stmt.target in self.symbol_table:
                self.symbol_table[stmt.target]["ssa"] = value_ssa
            return lines

        if isinstance(stmt, IfStatement):
            cond_ssa, cond_type, cond_ops = self.generate_expression(stmt.condition)
            lines.extend(cond_ops)
            lines.append(f"{self.indent()}scf.if {cond_ssa} {{")
            self.indent_level += 1
            for inner in stmt.then_block.statements:
                lines.extend(self.generate_statement(inner))
            self.indent_level -= 1
            if stmt.else_block:
                lines.append(f"{self.indent()}}} else {{")
                self.indent_level += 1
                for inner in stmt.else_block.statements:
                    lines.extend(self.generate_statement(inner))
                self.indent_level -= 1
            lines.append(f"{self.indent()}}}")
            return lines

        if isinstance(stmt, ReturnStatement):
            lines.append(f"{self.indent()}// return ignored in gpu kernel")
            return lines

        if isinstance(stmt, ForStatement):
            lines.extend(self.generate_for(stmt))
            return lines

        if isinstance(stmt, FunctionCall):
            if stmt.name in ["gpu_barrier", "gpu_sync"]:
                lines.append(f"{self.indent()}gpu.barrier")
                return lines
            _, _, expr_ops = self.generate_expression(stmt)
            lines.extend(expr_ops)
            return lines

        lines.append(f"{self.indent()}// Unsupported statement {type(stmt).__name__}")
        return lines

    def _assigned_locals(self, block: Block) -> List[str]:
        assigned: List[str] = []
        for inner in block.statements:
            if isinstance(inner, Assignment) and inner.target_expr is None and inner.target:
                if inner.target not in assigned:
                    assigned.append(inner.target)
            elif isinstance(inner, IfStatement):
                for name in self._assigned_locals(inner.then_block):
                    if name not in assigned:
                        assigned.append(name)
                if inner.else_block:
                    for name in self._assigned_locals(inner.else_block):
                        if name not in assigned:
                            assigned.append(name)
        return assigned

    def _collect_declared_vars_from_block(self, block: Block) -> List[str]:
        declared: List[str] = []
        for inner in block.statements:
            if isinstance(inner, VarDecl):
                declared.append(inner.name)
            elif isinstance(inner, IfStatement):
                declared.extend(self._collect_declared_vars_from_block(inner.then_block))
                if inner.else_block:
                    declared.extend(self._collect_declared_vars_from_block(inner.else_block))
            elif isinstance(inner, ForStatement):
                declared.extend(self._collect_declared_vars_from_block(inner.body))
        return declared

    def _detect_loop_carried_vars(self, body: Block) -> List[str]:
        assigned_vars = self._assigned_locals(body)
        declared_vars = self._collect_declared_vars_from_block(body)
        carried: List[str] = []
        for var_name in assigned_vars:
            if var_name in self.symbol_table and var_name not in declared_vars and var_name not in carried:
                carried.append(var_name)
        return carried

    def generate_block(self, block: Block) -> List[str]:
        lines: List[str] = []
        for inner in block.statements:
            lines.extend(self.generate_statement(inner))
        return lines

    def generate_for(self, for_stmt: ForStatement) -> List[str]:
        lines: List[str] = []
        loop_carried_vars = self._detect_loop_carried_vars(for_stmt.body)

        lower_ssa, lower_type, lower_ops = self.generate_expression(for_stmt.range_start)
        upper_ssa, upper_type, upper_ops = self.generate_expression(for_stmt.range_end)
        lines.extend(lower_ops)
        lines.extend(upper_ops)

        lb_idx = self.new_ssa()
        ub_idx = self.new_ssa()
        step_idx = self.new_ssa()
        lines.append(f"{self.indent()}{lb_idx} = arith.index_cast {lower_ssa} : {lower_type} to index")
        lines.append(f"{self.indent()}{ub_idx} = arith.index_cast {upper_ssa} : {upper_type} to index")
        lines.append(f"{self.indent()}{step_idx} = arith.constant 1 : index")

        iv = self.new_ssa()
        iter_inits: List[str] = []
        iter_types: List[str] = []
        for var_name in loop_carried_vars:
            info = self.symbol_table[var_name]
            iter_inits.append(info["ssa"])
            iter_types.append(info["mlir_type"])

        if iter_inits:
            iter_vars = [self.new_ssa() for _ in loop_carried_vars]
            iter_args_spec = ", ".join(f"{iv_arg} = {init}" for iv_arg, init in zip(iter_vars, iter_inits))
            if len(loop_carried_vars) == 1:
                result_vars = [self.new_ssa()]
            else:
                result_vars = [self.new_ssa() for _ in loop_carried_vars]
            result_lhs = result_vars[0] if len(result_vars) == 1 else ", ".join(result_vars)
            lines.append(
                f"{self.indent()}{result_lhs} = scf.for {iv} = {lb_idx} to {ub_idx} step {step_idx} "
                f"iter_args({iter_args_spec}) -> ({', '.join(iter_types)}) {{"
            )
        else:
            result_vars = []
            lines.append(f"{self.indent()}scf.for {iv} = {lb_idx} to {ub_idx} step {step_idx} {{")

        self.indent_level += 1
        for var_name, iter_var in zip(loop_carried_vars, iter_vars if iter_inits else []):
            self.symbol_table[var_name]["ssa"] = iter_var

        iv_i32 = self.new_ssa()
        lines.append(f"{self.indent()}{iv_i32} = arith.index_cast {iv} : index to i32")
        self.symbol_table[for_stmt.variable] = {
            "ssa": iv_i32,
            "mlir_type": "i32",
            "flow_type": Type("i32"),
        }

        lines.extend(self.generate_block(for_stmt.body))

        if iter_inits:
            yield_vals = [self.symbol_table[v]["ssa"] for v in loop_carried_vars]
            lines.append(f"{self.indent()}scf.yield {', '.join(yield_vals)} : {', '.join(iter_types)}")
        self.indent_level -= 1
        lines.append(f"{self.indent()}}}")

        for var_name, result_ssa in zip(loop_carried_vars, result_vars):
            self.symbol_table[var_name]["ssa"] = result_ssa

        return lines

    def generate_gpu_func(self, func: FunctionDecl) -> List[str]:
        self.symbol_table = {}
        self.ssa_counter = 0
        lines: List[str] = []

        params = []
        for i, param in enumerate(func.parameters):
            mlir_type = self.flow_type_to_mlir(param.type)
            ssa = f"%arg{i}"
            params.append(f"{ssa}: {mlir_type}")
            self.symbol_table[param.name] = {
                "ssa": ssa,
                "mlir_type": mlir_type,
                "flow_type": param.type,
            }

        lines.append(f"{self.indent()}gpu.func @{func.name}({', '.join(params)}) kernel {{")
        self.indent_level += 1
        for stmt in func.body.statements:
            lines.extend(self.generate_statement(stmt))
        lines.append(f"{self.indent()}gpu.return")
        self.indent_level -= 1
        lines.append(f"{self.indent()}}}")
        return lines

    def generate_gpu_module(self, gpu_funcs: List[FunctionDecl]) -> str:
        if not gpu_funcs:
            return ""
        lines: List[str] = []
        lines.append(f"{self.indent()}gpu.module @flow_kernels {{")
        self.indent_level += 1
        for func in gpu_funcs:
            lines.extend(self.generate_gpu_func(func))
            lines.append("")
        self.indent_level -= 1
        lines.append(f"{self.indent()}}}")
        return "\n".join(lines)
