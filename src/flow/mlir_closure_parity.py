"""First-class function / closure parity for the MLIR backend.

Flow's C backend represents escaping functions as a fat closure containing a
code pointer and an environment pointer.  This module gives the MLIR backend
the same representation while the legacy generator is being converged.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .parser import Block, FunctionCall, Lambda, Type, Variable


CLOSURE_MLIR_TYPE = "!llvm.struct<(!llvm.ptr, !llvm.ptr)>"
_INSTALLED = False
_ORIGINAL_FLOW_TYPE_TO_MLIR = None
_ORIGINAL_GENERATE_FUNCTION_CALL = None
_ORIGINAL_GET_EXPRESSION_TYPE = None
_ORIGINAL_FLOW_TYPE_OF_EXPR = None
_ORIGINAL_GENERATE_MODULE = None


def _is_flow_fn_type(flow_type: Any) -> bool:
    return bool(
        flow_type is not None
        and not getattr(flow_type, "is_cfn", False)
        and str(getattr(flow_type, "name", "")).startswith("fn_")
    )


def _fn_param_types(flow_type: Type) -> List[Type]:
    return list(getattr(flow_type, "type_args", None) or [])


def _fn_return_type(flow_type: Type) -> Type:
    return getattr(flow_type, "element_type", None) or Type("i32")


def _lambda_flow_type(lam: Lambda) -> Type:
    params = [p.type or Type("i32") for p in lam.parameters]
    ret = lam.return_type or Type("i32")
    key = "_".join(p.name for p in params) or "void"
    return Type(f"fn_{key}__{ret.name}", element_type=ret, type_args=params)


def _closure_value(self, info: Dict[str, Any]) -> tuple[str, List[str]]:
    ptr = info.get("alloca_ptr")
    if ptr:
        value = f"%{self.function_counter}"
        self.function_counter += 1
        self._ssa_types[value] = CLOSURE_MLIR_TYPE
        return value, [
            f"{self.indent()}{value} = llvm.load {ptr} : !llvm.ptr -> {CLOSURE_MLIR_TYPE}"
        ]
    value = info.get("ssa_name")
    if not value:
        raise NotImplementedError("function value has no MLIR SSA binding")
    self._ssa_types[value] = CLOSURE_MLIR_TYPE
    return value, []


def _generate_fat_closure_call(
    self, func_call: FunctionCall, info: Dict[str, Any]
) -> tuple[str, List[str]]:
    flow_fn = info.get("flow_type")
    if not _is_flow_fn_type(flow_fn):
        raise NotImplementedError(f"'{func_call.name}' is not a Flow function value")

    param_flows = _fn_param_types(flow_fn)
    ret_flow = _fn_return_type(flow_fn)
    param_types = [self.flow_type_to_mlir(t) for t in param_flows]
    ret_type = self.flow_type_to_mlir(ret_flow)

    closure, ops = _closure_value(self, info)
    code_ptr = f"%{self.function_counter}"
    self.function_counter += 1
    env_ptr = f"%{self.function_counter}"
    self.function_counter += 1
    ops.extend(
        [
            f"{self.indent()}{code_ptr} = llvm.extractvalue {closure}[0] : {CLOSURE_MLIR_TYPE}",
            f"{self.indent()}{env_ptr} = llvm.extractvalue {closure}[1] : {CLOSURE_MLIR_TYPE}",
        ]
    )
    self._ssa_types[code_ptr] = "!llvm.ptr"
    self._ssa_types[env_ptr] = "!llvm.ptr"

    args: List[str] = []
    for index, arg in enumerate(func_call.arguments):
        value, value_ops = self.generate_expression(arg)
        ops.extend(value_ops)
        actual = self._ssa_types.get(value) or self.get_expression_type(arg)
        expected = param_types[index] if index < len(param_types) else actual
        if actual != expected:
            value, cast_ops = self._emit_cast(value, actual, expected)
            ops.extend(cast_ops)
        args.append(value)

    call_args = [env_ptr] + args
    call_sig_types = ["!llvm.ptr"] + param_types[: len(args)]
    signature = f"({', '.join(call_sig_types)}) -> {ret_type}"

    if ret_type == "()":
        ops.append(
            f"{self.indent()}llvm.call {code_ptr}({', '.join(call_args)}) : "
            f"!llvm.ptr, {signature}"
        )
        return f"%void_{self.function_counter}", ops

    result = f"%{self.function_counter}"
    self.function_counter += 1
    ops.append(
        f"{self.indent()}{result} = llvm.call {code_ptr}({', '.join(call_args)}) : "
        f"!llvm.ptr, {signature}"
    )
    self._ssa_types[result] = ret_type
    if str(getattr(ret_flow, "name", "")).startswith("u"):
        self._ssa_unsigned.add(result)
    return result, ops


def _allocate_capture_env(
    self, capture_names: List[str], capture_infos: List[Dict[str, Any]]
) -> tuple[str, str, List[str]]:
    field_types = [info["mlir_type"] for info in capture_infos]
    unsupported = [t for t in field_types if t.startswith("memref<") or t.startswith("vector<")]
    if unsupported:
        raise NotImplementedError(
            "MLIR closure capture of memref/vector values is not supported yet"
        )

    env_type = f"!llvm.struct<({', '.join(field_types)})>"
    ops: List[str] = []
    null = f"%{self.function_counter}"
    self.function_counter += 1
    end = f"%{self.function_counter}"
    self.function_counter += 1
    size = f"%{self.function_counter}"
    self.function_counter += 1
    size_type = "i32" if getattr(self, "size_t_bits", 64) == 32 else "i64"
    ops.append(f"{self.indent()}{null} = llvm.mlir.zero : !llvm.ptr")
    ops.append(
        f"{self.indent()}{end} = llvm.getelementptr {null}[1] : "
        f"(!llvm.ptr) -> !llvm.ptr, {env_type}"
    )
    ops.append(
        f"{self.indent()}{size} = llvm.ptrtoint {end} : !llvm.ptr to {size_type}"
    )

    env = f"%{self.function_counter}"
    self.function_counter += 1
    calloc_info = self.symbol_table.get("calloc") or {}
    malloc_info = self.symbol_table.get("malloc") or {}
    if calloc_info.get("type") == "function":
        one = f"%{self.function_counter}"
        self.function_counter += 1
        ops.append(f"{self.indent()}{one} = arith.constant 1 : {size_type}")
        ops.append(
            f"{self.indent()}{env} = func.call @calloc({one}, {size}) : "
            f"({size_type}, {size_type}) -> !llvm.ptr"
        )
    elif malloc_info.get("type") == "function":
        ops.append(
            f"{self.indent()}{env} = func.call @malloc({size}) : "
            f"({size_type}) -> !llvm.ptr"
        )
    else:
        self._parity_needs_malloc = True
        self._parity_malloc_size_type = size_type
        ops.append(
            f"{self.indent()}{env} = llvm.call @malloc({size}) : "
            f"({size_type}) -> !llvm.ptr"
        )
    self._ssa_types[env] = "!llvm.ptr"

    for index, (name, info) in enumerate(zip(capture_names, capture_infos)):
        value, value_ops = self.generate_variable(Variable(name))
        ops.extend(value_ops)
        field_type = info["mlir_type"]
        actual = self._ssa_types.get(value) or field_type
        if actual != field_type:
            value, cast_ops = self._emit_cast(value, actual, field_type)
            ops.extend(cast_ops)
        field_ptr = f"%{self.function_counter}"
        self.function_counter += 1
        ops.append(
            f"{self.indent()}{field_ptr} = llvm.getelementptr {env}[0, {index}] : "
            f"(!llvm.ptr) -> !llvm.ptr, {env_type}"
        )
        ops.append(
            f"{self.indent()}llvm.store {value}, {field_ptr} : {field_type}, !llvm.ptr"
        )

    return env, env_type, ops


def _generate_lambda_with_fat_closure(self, lam: Lambda) -> tuple[str, List[str]]:
    captures = list(getattr(lam, "captures", None) or [])
    capture_infos: List[Dict[str, Any]] = []
    for name in captures:
        info = self.symbol_table.get(name)
        if not info:
            raise NotImplementedError(f"cannot capture unknown variable '{name}'")
        flow_type = info.get("flow_type")
        mlir_type = info.get("mlir_type") or (
            self.flow_type_to_mlir(flow_type) if flow_type is not None else "i32"
        )
        capture_infos.append(
            {"flow_type": flow_type or Type("i32"), "mlir_type": mlir_type}
        )

    if captures:
        env_value, env_type, outer_ops = _allocate_capture_env(
            self, captures, capture_infos
        )
    else:
        env_type = "!llvm.struct<()>"
        env_value = f"%{self.function_counter}"
        self.function_counter += 1
        outer_ops = [f"{self.indent()}{env_value} = llvm.mlir.zero : !llvm.ptr"]
        self._ssa_types[env_value] = "!llvm.ptr"

    self._lambda_counter += 1
    name = f"lambda_{self._lambda_counter}"
    param_flows = [p.type or Type("i32") for p in lam.parameters]
    param_types = [self.flow_type_to_mlir(t) for t in param_flows]
    ret_flow = lam.return_type or Type("i32")
    ret_type = self.flow_type_to_mlir(ret_flow)

    saved_table = self.symbol_table
    saved_ssa = dict(self._ssa_types)
    saved_unsigned = set(self._ssa_unsigned)
    saved_return = getattr(self, "current_function_return_type", None)
    saved_name = getattr(self, "_current_function_name", None)
    saved_indent = self.indent_level

    self.symbol_table = saved_table.copy()
    self._ssa_types = {"%env": "!llvm.ptr"}
    self._ssa_unsigned = set()
    self.current_function_return_type = ret_flow
    self._current_function_name = name
    self.indent_level = 2

    body_lines: List[str] = []
    for index, (capture_name, info) in enumerate(zip(captures, capture_infos)):
        field_ptr = f"%{self.function_counter}"
        self.function_counter += 1
        loaded = f"%{self.function_counter}"
        self.function_counter += 1
        field_type = info["mlir_type"]
        body_lines.append(
            f"{self.indent()}{field_ptr} = llvm.getelementptr %env[0, {index}] : "
            f"(!llvm.ptr) -> !llvm.ptr, {env_type}"
        )
        body_lines.append(
            f"{self.indent()}{loaded} = llvm.load {field_ptr} : !llvm.ptr -> {field_type}"
        )
        self._ssa_types[field_ptr] = "!llvm.ptr"
        self._ssa_types[loaded] = field_type
        self.symbol_table[capture_name] = {
            "type": "variable",
            "ssa_name": loaded,
            "alloca_ptr": field_ptr,
            "mlir_type": field_type,
            "flow_type": info["flow_type"],
        }

    for index, (parameter, flow_type, mlir_type) in enumerate(
        zip(lam.parameters, param_flows, param_types)
    ):
        arg = f"%arg{index}"
        self._ssa_types[arg] = mlir_type
        self.symbol_table[parameter.name] = {
            "type": "variable",
            "ssa_name": arg,
            "mlir_type": mlir_type,
            "flow_type": flow_type,
        }

    if isinstance(lam.body, Block):
        body = self.generate_block(lam.body)
        if body.strip():
            body_lines.append(body)
        if not self._block_has_terminator(body):
            zero, zero_ops = self._zero_value_for_mlir_type(ret_type)
            body_lines.extend(zero_ops)
            body_lines.append(f"{self.indent()}func.return {zero} : {ret_type}")
    else:
        value, value_ops = self.generate_expression(lam.body)
        body_lines.extend(value_ops)
        actual = self._ssa_types.get(value) or self.get_expression_type(lam.body)
        if actual != ret_type:
            value, cast_ops = self._emit_cast(value, actual, ret_type)
            body_lines.extend(cast_ops)
        body_lines.append(f"{self.indent()}func.return {value} : {ret_type}")

    self.indent_level = saved_indent
    self.symbol_table = saved_table
    self._ssa_types = saved_ssa
    self._ssa_unsigned = saved_unsigned
    self.current_function_return_type = saved_return
    self._current_function_name = saved_name

    hidden_types = ["!llvm.ptr"] + param_types
    fn_type = f"({', '.join(hidden_types)}) -> {ret_type}"
    sig = ["%env: !llvm.ptr"] + [
        f"%arg{i}: {ty}" for i, ty in enumerate(param_types)
    ]
    self._pending_lambdas.append(
        "\n".join(
            [
                f"  func.func private @{name}({', '.join(sig)}) -> {ret_type} {{",
                *body_lines,
                "  }",
            ]
        )
    )

    fn_ssa = f"%{self.function_counter}"
    self.function_counter += 1
    code_ptr = f"%{self.function_counter}"
    self.function_counter += 1
    closure0 = f"%{self.function_counter}"
    self.function_counter += 1
    closure1 = f"%{self.function_counter}"
    self.function_counter += 1
    closure2 = f"%{self.function_counter}"
    self.function_counter += 1
    outer_ops.extend(
        [
            f"{self.indent()}{fn_ssa} = func.constant @{name} : {fn_type}",
            f"{self.indent()}{code_ptr} = builtin.unrealized_conversion_cast {fn_ssa} : {fn_type} to !llvm.ptr",
            f"{self.indent()}{closure0} = llvm.mlir.undef : {CLOSURE_MLIR_TYPE}",
            f"{self.indent()}{closure1} = llvm.insertvalue {code_ptr}, {closure0}[0] : {CLOSURE_MLIR_TYPE}",
            f"{self.indent()}{closure2} = llvm.insertvalue {env_value}, {closure1}[1] : {CLOSURE_MLIR_TYPE}",
        ]
    )
    self._ssa_types[fn_ssa] = fn_type
    self._ssa_types[code_ptr] = "!llvm.ptr"
    self._ssa_types[closure2] = CLOSURE_MLIR_TYPE
    return closure2, outer_ops


def _flow_type_to_mlir_with_functions(self, flow_type: Type) -> str:
    if _is_flow_fn_type(flow_type):
        return CLOSURE_MLIR_TYPE
    return _ORIGINAL_FLOW_TYPE_TO_MLIR(self, flow_type)


def _generate_function_call_with_functions(
    self, func_call: FunctionCall
) -> tuple[str, List[str]]:
    info = self.symbol_table.get(func_call.name)
    if info and _is_flow_fn_type(info.get("flow_type")):
        return _generate_fat_closure_call(self, func_call, info)
    return _ORIGINAL_GENERATE_FUNCTION_CALL(self, func_call)


def _get_expression_type_with_functions(self, expr) -> str:
    if isinstance(expr, Lambda):
        return CLOSURE_MLIR_TYPE
    if isinstance(expr, FunctionCall):
        info = self.symbol_table.get(expr.name)
        flow_fn = info.get("flow_type") if info else None
        if _is_flow_fn_type(flow_fn):
            return self.flow_type_to_mlir(_fn_return_type(flow_fn))
    return _ORIGINAL_GET_EXPRESSION_TYPE(self, expr)


def _flow_type_of_expr_with_functions(self, expr) -> Optional[Type]:
    if isinstance(expr, Lambda):
        return _lambda_flow_type(expr)
    if isinstance(expr, FunctionCall):
        info = self.symbol_table.get(expr.name)
        flow_fn = info.get("flow_type") if info else None
        if _is_flow_fn_type(flow_fn):
            return _fn_return_type(flow_fn)
    return _ORIGINAL_FLOW_TYPE_OF_EXPR(self, expr)


def _generate_module_with_closure_runtime(self, declarations, emit_gpu: bool = False) -> str:
    self._parity_needs_malloc = False
    self._parity_malloc_size_type = "i64"
    text = _ORIGINAL_GENERATE_MODULE(self, declarations, emit_gpu=emit_gpu)
    if self._parity_needs_malloc and "llvm.func @malloc(" not in text:
        decl = f"  llvm.func @malloc({self._parity_malloc_size_type}) -> !llvm.ptr\n"
        text = text.replace("module {\n", "module {\n" + decl, 1)
    return text


def install() -> None:
    """Install the fat-closure ABI on MLIRGenerator once."""
    global _INSTALLED
    global _ORIGINAL_FLOW_TYPE_TO_MLIR
    global _ORIGINAL_GENERATE_FUNCTION_CALL
    global _ORIGINAL_GET_EXPRESSION_TYPE
    global _ORIGINAL_FLOW_TYPE_OF_EXPR
    global _ORIGINAL_GENERATE_MODULE

    if _INSTALLED:
        return

    from .mlir_generator import MLIRGenerator

    _ORIGINAL_FLOW_TYPE_TO_MLIR = MLIRGenerator.flow_type_to_mlir
    _ORIGINAL_GENERATE_FUNCTION_CALL = MLIRGenerator.generate_function_call
    _ORIGINAL_GET_EXPRESSION_TYPE = MLIRGenerator.get_expression_type
    _ORIGINAL_FLOW_TYPE_OF_EXPR = MLIRGenerator._flow_type_of_expr
    _ORIGINAL_GENERATE_MODULE = MLIRGenerator.generate_module

    MLIRGenerator.flow_type_to_mlir = _flow_type_to_mlir_with_functions
    MLIRGenerator.generate_function_call = _generate_function_call_with_functions
    MLIRGenerator.get_expression_type = _get_expression_type_with_functions
    MLIRGenerator._flow_type_of_expr = _flow_type_of_expr_with_functions
    MLIRGenerator.generate_lambda = _generate_lambda_with_fat_closure
    MLIRGenerator.generate_module = _generate_module_with_closure_runtime
    MLIRGenerator._flow_closure_parity_installed = True
    _INSTALLED = True
