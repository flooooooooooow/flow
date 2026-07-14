#!/usr/bin/env python3
"""
FLOW to MLIR Generator
Converts parsed FLOW AST to MLIR dialects
"""

from typing import List, Dict, Optional, Any, Set
from .parser import (
    FunctionDecl, EffectDecl, CapabilityDecl, StructDecl, Block, Statement,
    VarDecl, Assignment, IfStatement, WhileStatement, ForStatement,
    ReturnStatement, Expression, Literal, Variable, BinaryOperation,
    UnaryOperation, FunctionCall, StructLiteral, FieldAccess, ArrayLiteral, VectorLiteral, ArrayAccess, Type,
    HandleStatement, EffectCall, MethodCall,
    MatchStatement, StructPattern, ConstDecl, LayoutStatement, CastExpression, TypeAliasDecl, DistinctTypeDecl
)

class MLIRGenerator:
    def _cast_for_printf(self, arg_ssa: str, arg_type: str) -> tuple[str, str, List[str]]:
        """Cast MLIR values to printf-compatible LLVM types."""
        ops: List[str] = []
        if arg_type == "f32":
            ext_ssa = f"%{self.function_counter}"
            self.function_counter += 1
            ops.append(f"{self.indent()}{ext_ssa} = arith.extf {arg_ssa} : f32 to f64")
            return ext_ssa, "f64", ops
        if arg_type == "i1":
            ext_ssa = f"%{self.function_counter}"
            self.function_counter += 1
            ops.append(f"{self.indent()}{ext_ssa} = arith.extui {arg_ssa} : i1 to i32")
            return ext_ssa, "i32", ops
        if arg_type == "index":
            ext_ssa = f"%{self.function_counter}"
            self.function_counter += 1
            ops.append(f"{self.indent()}{ext_ssa} = arith.index_cast {arg_ssa} : index to i32")
            return ext_ssa, "i32", ops
        return arg_ssa, arg_type, ops

    def _is_tensor_struct(self, mlir_type: str) -> bool:
        return mlir_type == "!llvm.struct<(!llvm.ptr, i32, i32, i32, i32, i32)>"

    def _struct_field_types(self, mlir_type: str) -> List[str]:
        if not mlir_type.startswith("!llvm.struct<"):
            return []
        inner = mlir_type[len("!llvm.struct<") : -1].strip()
        if inner.startswith("(") and inner.endswith(")"):
            inner = inner[1:-1].strip()
        fields: List[str] = []
        start = 0
        depth = 0
        for i, ch in enumerate(inner):
            if ch in "<([":
                depth += 1
            elif ch in ">)]":
                depth -= 1
            elif ch == "," and depth == 0:
                fields.append(inner[start:i].strip())
                start = i + 1
        fields.append(inner[start:].strip())
        return fields

    def _struct_field_count(self, mlir_type: str) -> int:
        return len(self._struct_field_types(mlir_type))

    def _flow_type_name(self, flow_type: Any) -> Optional[str]:
        return getattr(flow_type, "name", None) if flow_type else None

    def _func_call_return_type_name(self, func_call: FunctionCall) -> Optional[str]:
        if func_call.name not in self.symbol_table:
            return None
        return self._flow_type_name(self.symbol_table[func_call.name].get("return_type"))

    def _uses_alloca_storage(self, mlir_type: str, flow_type: Any = None) -> bool:
        """Tensor/composite locals live in dedicated alloca slots to avoid arm64 return-slot aliasing."""
        if self._is_tensor_struct(mlir_type):
            return True
        return self._flow_type_name(flow_type) in self._COMPOSITE_FIELD_MATERIALIZE_TYPES

    def _emit_alloca_store(self, value_ssa: str, mlir_type: str) -> tuple[str, List[str]]:
        ops: List[str] = []
        one = f"%{self.function_counter}"
        self.function_counter += 1
        ops.append(f"{self.indent()}{one} = llvm.mlir.constant(1 : i64) : i64")
        ptr = f"%{self.function_counter}"
        self.function_counter += 1
        ops.append(
            f"{self.indent()}{ptr} = llvm.alloca {one} x {mlir_type} : (i64) -> !llvm.ptr"
        )
        ops.append(
            f"{self.indent()}llvm.store {value_ssa}, {ptr} : {mlir_type}, !llvm.ptr"
        )
        return ptr, ops

    def _emit_alloca_load(self, ptr_ssa: str, mlir_type: str) -> tuple[str, List[str]]:
        val = f"%{self.function_counter}"
        self.function_counter += 1
        ops = [f"{self.indent()}{val} = llvm.load {ptr_ssa} : !llvm.ptr -> {mlir_type}"]
        self._ssa_types[val] = mlir_type
        return val, ops

    def _store_aggregate_var(self, var_info: Dict[str, Any], value_ssa: str) -> List[str]:
        mlir_type = var_info.get("mlir_type")
        if not mlir_type:
            return []
        ptr = var_info.get("alloca_ptr")
        if not ptr:
            ptr, ops = self._emit_alloca_store(value_ssa, mlir_type)
            var_info["alloca_ptr"] = ptr
            var_info["ssa_name"] = value_ssa
            return ops
        return [
            f"{self.indent()}llvm.store {value_ssa}, {ptr} : {mlir_type}, !llvm.ptr"
        ]

    _TENSOR_PTR_ARG_CALLEES = frozenset({"tensor_matmul"})
    _COMPOSITE_FIELD_MATERIALIZE_TYPES = frozenset({
        "Dense2D",
        "Dense2DGrad",
        "MLP2",
        "MLP2Grads",
        "MLP2Activations",
    })
    _TENSOR_POST_MATERIALIZE_CALLEES = frozenset({
        "tensor_rand",
        "tensor_randn",
        "tensor_scale",
        "tensor_zeros",
        "tensor_matmul_backward_a",
        "tensor_matmul_backward_b",
        "tensor_transpose",
        "tensor_sigmoid",
        "tensor_relu",
        "dense2d_forward",
        "nn_mse_backward",
    })
    _TENSOR_PARAM_METADATA_FIELDS = [0, 1, 2, 3, 4, 5]

    def _tensor_param_metadata_fields(self) -> List[int]:
        # Materialize every tensor metadata field at function entry. Partial
        # copies (e.g. ptr/size/dim0 only) leave dim1–dim3 as undef and cause
        # heap corruption in callees like tensor_scale that read all dims.
        return self._TENSOR_PARAM_METADATA_FIELDS

    def _materialize_tensor_param_metadata(self, value_ssa: str, mlir_type: str) -> tuple[str, List[str]]:
        ops: List[str] = []
        agg = f"%{self.function_counter}"
        self.function_counter += 1
        ops.append(f"{self.indent()}{agg} = llvm.mlir.undef : {mlir_type}")
        for idx in self._tensor_param_metadata_fields():
            field = f"%{self.function_counter}"
            self.function_counter += 1
            ops.append(f"{self.indent()}{field} = llvm.extractvalue {value_ssa}[{idx}] : {mlir_type}")
            next_agg = f"%{self.function_counter}"
            self.function_counter += 1
            ops.append(
                f"{self.indent()}{next_agg} = llvm.insertvalue {field}, {agg}[{idx}] : {mlir_type}"
            )
            agg = next_agg
        self._ssa_types[agg] = mlir_type
        return agg, ops

    def _materialize_tensor_for_call(
        self, value_ssa: str, mlir_type: str, callee_name: str
    ) -> tuple[str, List[str]]:
        """Copy tensor SSA before passing to a callee that may clobber the return slot."""
        if callee_name in self._TENSOR_PTR_ARG_CALLEES:
            field_indices = [0, 1, 2, 3]
        else:
            field_indices = list(range(self._struct_field_count(mlir_type)))
        ops: List[str] = []
        agg = f"%{self.function_counter}"
        self.function_counter += 1
        ops.append(f"{self.indent()}{agg} = llvm.mlir.undef : {mlir_type}")
        for idx in field_indices:
            field = f"%{self.function_counter}"
            self.function_counter += 1
            ops.append(f"{self.indent()}{field} = llvm.extractvalue {value_ssa}[{idx}] : {mlir_type}")
            next_agg = f"%{self.function_counter}"
            self.function_counter += 1
            ops.append(
                f"{self.indent()}{next_agg} = llvm.insertvalue {field}, {agg}[{idx}] : {mlir_type}"
            )
            agg = next_agg
        self._ssa_types[agg] = mlir_type
        return agg, ops

    def _roundtrip_alloca(
        self, value_ssa: str, mlir_type: str, ops: Optional[List[str]] = None
    ) -> tuple[str, List[str]]:
        """Force aggregate through an alloca slot so LLVM cannot reuse return-stack memory."""
        if ops is None:
            ops = []
        ptr, store_ops = self._emit_alloca_store(value_ssa, mlir_type)
        ops.extend(store_ops)
        loaded, load_ops = self._emit_alloca_load(ptr, mlir_type)
        ops.extend(load_ops)
        return loaded, ops

    def _materialize_struct_value(self, value_ssa: str, mlir_type: str) -> tuple[str, List[str]]:
        """Copy aggregate SSA so nested struct returns do not alias callee stack slots."""
        if not mlir_type.startswith("!llvm.struct"):
            return value_ssa, []
        if self._is_tensor_struct(mlir_type):
            return self._materialize_tensor_for_call(value_ssa, mlir_type, "")
        ops: List[str] = []
        field_types = self._struct_field_types(mlir_type)
        agg = f"%{self.function_counter}"
        self.function_counter += 1
        ops.append(f"{self.indent()}{agg} = llvm.mlir.undef : {mlir_type}")
        for idx, field_type in enumerate(field_types):
            field = f"%{self.function_counter}"
            self.function_counter += 1
            ops.append(f"{self.indent()}{field} = llvm.extractvalue {value_ssa}[{idx}] : {mlir_type}")
            if self._is_tensor_struct(field_type):
                field, sub_ops = self._materialize_tensor_for_call(field, field_type, "")
                ops.extend(sub_ops)
            next_agg = f"%{self.function_counter}"
            self.function_counter += 1
            ops.append(
                f"{self.indent()}{next_agg} = llvm.insertvalue {field}, {agg}[{idx}] : {mlir_type}"
            )
            agg = next_agg
        self._ssa_types[agg] = mlir_type
        return agg, ops

    def _tensor_needs_full_materialize(
        self, arg_val: str, arg_expr: Optional[Expression] = None
    ) -> bool:
        if arg_val in self._tensor_field_extracts:
            return True
        if isinstance(arg_expr, Variable):
            var_info = self.symbol_table.get(arg_expr.name) or {}
            if var_info.get("from_tensor_field"):
                return True
        return False

    def _stable_tensor_for_call(
        self,
        arg_val: str,
        mlir_type: str,
        callee_name: str,
        *,
        callee_returns_tensor: bool = False,
        callee_returns_composite: bool = False,
        arg_expr: Optional[Expression] = None,
    ) -> tuple[str, List[str]]:
        """Return a stack-independent tensor SSA safe to pass into func.call."""
        if arg_val in self._tensor_stable_ssas and not (
            callee_returns_tensor or callee_returns_composite
        ):
            return arg_val, []

        needs_copy = (
            arg_val in self._tensor_call_results
            or arg_val in self._tensor_field_extracts
            or (
                arg_val in self._tensor_param_ssas
                and (callee_returns_tensor or callee_returns_composite)
            )
            or callee_returns_tensor
            or callee_returns_composite
        )
        if not needs_copy:
            return arg_val, []

        mat_callee = (
            ""
            if (
                self._tensor_needs_full_materialize(arg_val, arg_expr)
                or arg_val in self._tensor_call_results
                or callee_returns_tensor
                or callee_returns_composite
            )
            else callee_name
        )
        copied, mat_ops = self._materialize_tensor_for_call(arg_val, mlir_type, mat_callee)
        if mat_callee == "":
            self._tensor_stable_ssas.add(copied)
        return copied, mat_ops

    @staticmethod
    def _format_mlir_numeric(value: str, mlir_type: str) -> str:
        """Format numeric literals for MLIR text (no scientific notation)."""
        if mlir_type not in ("f32", "f64", "i32", "i64", "index"):
            return value
        lowered = value.lower()
        if mlir_type in ("f32", "f64") and ("e" in lowered):
            try:
                number = float(value)
                if mlir_type == "f32":
                    return format(number, ".10f").rstrip("0").rstrip(".") or "0.0"
                return format(number, ".17f").rstrip("0").rstrip(".") or "0.0"
            except ValueError:
                return value
        return value

    def __init__(self, source_file: str = "unknown.flow"):
        self.indent_level = 0
        self.symbol_table = {}
        self.function_counter = 0
        self.block_counter = 0
        self.string_constants = {}  # Maps string value -> global name
        self.string_counter = 0
        self._symbol_stack: List[Dict[str, Any]] = []
        self.needs_printf = False  # Track if we need printf declaration
        self.source_file = source_file  # For debug info
        self.current_line = 1  # Track current source line for debug info
        self.emit_debug_info = True  # Enable DWARF debug info generation
        self._effect_handler_stack: List[Dict[str, str]] = [{}]
        self.inside_scf_for = False  # Track if we're inside scf.for
        self.declarations = []  # Store declarations for type lookup
        self.struct_layouts = {}  # Maps struct name to field offsets and types
        self._ssa_types: Dict[str, str] = {}  # Maps SSA name -> MLIR type string
        self.type_aliases = {}  # name -> base Type
        self.distinct_types = {}  # name -> base Type
        self.struct_llvm_types: Dict[str, Optional[str]] = {}
        self._struct_llvm_building: Set[str] = set()
        self._init_per_function_state()

    def _init_per_function_state(self) -> None:
        """Reset per-function SSA tracking (safe for unit tests that skip generate_function)."""
        self._tensor_call_results: set[str] = set()
        self._tensor_stable_ssas: set[str] = set()
        self._tensor_field_extracts: set[str] = set()
        self._tensor_extract_origins: Dict[str, tuple[str, int]] = {}
        self._composite_call_results: set[str] = set()
        self._tensor_param_ssas: set[str] = set()

    def indent(self) -> str:
        return "  " * self.indent_level

    def _new_block_label(self) -> str:
        label = f"bb{self.block_counter}"
        self.block_counter += 1
        return label
    
    def _block_has_terminator(self, block_code: str) -> bool:
        """Check if a block of MLIR code already ends with a terminator."""
        if not block_code:
            return False
        lines = [line.strip() for line in block_code.strip().split('\n') if line.strip()]
        if not lines:
            return False
        last_line = lines[-1]
        # Terminators in MLIR: func.return, cf.br, cf.cond_br, scf.yield
        terminators = ['func.return', 'cf.br', 'cf.cond_br', 'scf.yield', 'return']
        return any(last_line.startswith(t) for t in terminators)

    def _get_struct_decl(self, name: str) -> Optional[StructDecl]:
        """Look up a struct declaration by name."""
        for decl in self.declarations:
            if isinstance(decl, StructDecl) and decl.name == name:
                return decl
        return None
    
    def _calculate_struct_layouts(self, declarations: List[Any]) -> None:
        """Calculate field offsets for all struct types with proper alignment"""
        for decl in declarations:
            if isinstance(decl, StructDecl):
                layout = {}
                offset = 0
                for field in decl.fields:
                    field_size = self._get_type_size(field.type)
                    # Align offset to the field's natural alignment
                    alignment = min(field_size, 8) if field_size > 0 else 1
                    offset = (offset + alignment - 1) & ~(alignment - 1)
                    layout[field.name] = {
                        'offset': offset,
                        'type': field.type,
                        'size': field_size
                    }
                    offset += field_size
                self.struct_layouts[decl.name] = layout
    
    def _get_type_size(self, flow_type) -> int:
        """Get the size of a type in bytes (simplified)"""
        # Handle string type names
        flow_type = self._resolve_type_alias(flow_type)
        type_name = flow_type.name if hasattr(flow_type, 'name') else str(flow_type)
        
        if type_name in ['i8', 'u8', 'bool']:
            return 1
        elif type_name in ['i16', 'u16']:
            return 2
        elif type_name in ['i32', 'u32', 'f32']:
            return 4
        elif type_name in ['i64', 'u64', 'f64']:
            return 8
        elif type_name in ['i128', 'u128']:
            return 16
        else:
            # For struct types, calculate recursively
            if type_name in self.struct_layouts:
                return sum(field['size'] for field in self.struct_layouts[type_name].values())
            return 4  # Default size

    def _resolve_type_alias(self, flow_type: Type) -> Type:
        """Resolve type aliases and distinct types to their base type for lowering."""
        if not hasattr(flow_type, 'name'):
            return flow_type
        current = flow_type
        seen = set()
        while True:
            name = current.name
            if name in seen:
                return current
            seen.add(name)
            if name in self.type_aliases:
                current = self.type_aliases[name]
                continue
            if name in self.distinct_types:
                current = self.distinct_types[name]
                continue
            return current

    def _struct_llvm_type(self, struct_name: str) -> Optional[str]:
        if struct_name in self.struct_llvm_types:
            return self.struct_llvm_types[struct_name]
        if struct_name in self._struct_llvm_building:
            return None

        self._struct_llvm_building.add(struct_name)

        decl = self._get_struct_decl(struct_name)
        if not decl:
            self._struct_llvm_building.discard(struct_name)
            self.struct_llvm_types[struct_name] = None
            return None

        field_types = []
        for field in decl.fields:
            field_ty = self.flow_type_to_mlir(field.type)
            # LLVM struct fields must be LLVM-compatible scalars/pointers/structs.
            if field_ty.startswith("memref") or field_ty.startswith("vector") or field_ty.startswith("!flow.struct"):
                self._struct_llvm_building.discard(struct_name)
                self.struct_llvm_types[struct_name] = None
                return None
            field_types.append(field_ty)

        struct_ty = f"!llvm.struct<({', '.join(field_types)})>"
        self._struct_llvm_building.discard(struct_name)
        self.struct_llvm_types[struct_name] = struct_ty
        return struct_ty

    def _zero_value_for_mlir_type(self, mlir_type: str) -> tuple[str, List[str]]:
        ssa_name = f"%{self.function_counter}"
        self.function_counter += 1
        if mlir_type.startswith("f"):
            return ssa_name, [f"{self.indent()}{ssa_name} = arith.constant 0.0 : {mlir_type}"]
        if mlir_type.startswith("i"):
            return ssa_name, [f"{self.indent()}{ssa_name} = arith.constant 0 : {mlir_type}"]
        if mlir_type == "!llvm.ptr":
            return ssa_name, [f"{self.indent()}{ssa_name} = llvm.mlir.null : {mlir_type}"]
        # Fallback to undef for aggregate/unknown types
        return ssa_name, [f"{self.indent()}{ssa_name} = llvm.mlir.undef : {mlir_type}"]
    
    def generate_module(self, declarations: List[Any], emit_gpu: bool = False) -> str:
        mlir_code = []
        
        # Reset state for new module
        self.string_constants = {}
        self.string_counter = 0
        self.needs_printf = False
        self.declarations = declarations  # Store declarations for type lookup
        self.type_aliases = {d.name: d.base_type for d in declarations if isinstance(d, TypeAliasDecl)}
        self.distinct_types = {d.name: d.base_type for d in declarations if isinstance(d, DistinctTypeDecl)}
        self.struct_llvm_types = {}
        self._struct_llvm_building = set()
        self._declared_externs: Set[str] = set()

        # Split GPU kernels from CPU declarations (GPU kernels are handled separately)
        gpu_functions = []
        cpu_decls = []
        for decl in declarations:
            if isinstance(decl, FunctionDecl) and hasattr(decl, 'attributes') and 'gpu' in decl.attributes:
                gpu_functions.append(decl)
            else:
                cpu_decls.append(decl)
        
        # Calculate struct layouts
        self._calculate_struct_layouts(cpu_decls)
        
        # Module header with required dialects and debug info
        if self.emit_debug_info:
            mlir_code.append(f'module attributes {{llvm.dbg.cu = #llvm.di_compile_unit<id = distinct[0]<>, sourceLanguage = DW_LANG_C, file = #llvm.di_file<"{self.source_file}" in ".">, producer = "FLOW Compiler", isOptimized = false, emissionKind = Full>}} {{')
        else:
            mlir_code.append("module {")
        self.indent_level += 1
        
        # First pass: collect all function signatures in symbol table
        for decl in cpu_decls:
            if isinstance(decl, FunctionDecl):
                if getattr(decl, "is_extern", False) and decl.name == "printf":
                    self.needs_printf = True
                # Add function to symbol table
                self.symbol_table[decl.name] = {
                    'type': 'function',
                    'return_type': decl.return_type,
                    'parameters': decl.parameters,
                    'mlir_name': f"@{decl.name}"
                }
        
        # Second pass: generate all declarations to collect string constants
        decl_code = []
        for decl in cpu_decls:
            if isinstance(decl, FunctionDecl):
                decl_code.append(self.generate_function(decl))
            elif isinstance(decl, EffectDecl):
                decl_code.append(self.generate_effect(decl))
            elif isinstance(decl, CapabilityDecl):
                decl_code.append(self.generate_capability(decl))
            elif isinstance(decl, StructDecl):
                decl_code.append(self.generate_struct(decl))
            elif isinstance(decl, ConstDecl):
                decl_code.append(self.generate_const(decl))
            elif isinstance(decl, (TypeAliasDecl, DistinctTypeDecl)):
                # No MLIR output needed for aliases/distinct types (lowered to base types)
                continue
            else:
                decl_code.append(f"// Unsupported declaration type: {type(decl).__name__}")
        
        # Add external function declarations (printf for I/O)
        if self.needs_printf:
            mlir_code.append(f"{self.indent()}llvm.func @printf(!llvm.ptr, ...) -> i32")
        
        # Add string constants as LLVM globals
        for string_val, global_name in self.string_constants.items():
            # Remove quotes and escape for LLVM
            str_content = string_val[1:-1]  # Remove surrounding quotes
            # Calculate actual byte length (escape sequences like \n count as 1 byte)
            byte_len = len(str_content.encode('utf-8').decode('unicode_escape')) + 1  # +1 for null terminator
            mlir_code.append(f'{self.indent()}llvm.mlir.global internal constant @{global_name}("{str_content}\\00") {{addr_space = 0 : i32}} : !llvm.array<{byte_len} x i8>')
        
        # Add generated declarations
        mlir_code.extend(decl_code)

        # Append GPU module if requested
        if emit_gpu and gpu_functions:
            from .mlir_gpu_codegen import MLIRGpuGenerator
            gpu_gen = MLIRGpuGenerator()
            gpu_gen.indent_level = self.indent_level
            gpu_module = gpu_gen.generate_gpu_module(gpu_functions)
            if gpu_module:
                mlir_code.append(gpu_module)
        
        self.indent_level -= 1
        mlir_code.append("}")
        
        return "\n".join(mlir_code)
    
    def generate_function(self, func: FunctionDecl) -> str:
        # Don't add to symbol table here - it's already added in first pass
        
        # Store current function return type for use in return statements
        self.current_function_return_type = func.return_type
        self._current_function_name = func.name
        self._init_per_function_state()
        
        # For extern functions, just declare them without body (dedupe across imports)
        if hasattr(func, 'is_extern') and func.is_extern:
            if func.name == "printf":
                return ""
            if func.name in self._declared_externs:
                return ""
            self._declared_externs.add(func.name)
            param_types = [self.flow_type_to_mlir(p.type) for p in func.parameters]
            return_type = self.flow_type_to_mlir(func.return_type)
            func_signature = f"func.func private @{func.name}({', '.join(param_types)}) -> {return_type}"
            return f"{self.indent()}{func_signature}"
        
        mlir_code = []
        
        # Function signature
        param_types = [self.flow_type_to_mlir(p.type) for p in func.parameters]
        return_type = self.flow_type_to_mlir(func.return_type)
        
        func_signature = f"func.func @{func.name}({', '.join([f'%arg{i}: {param_types[i]}' for i in range(len(param_types))])}) -> {return_type}"
        mlir_code.append(f"{self.indent()}{func_signature} {{")
        
        self.indent_level += 1

        # SSA names like %arg0 are reused per function; reset type tracking each time.
        self._ssa_types = {}
        
        param_prologue: List[str] = []
        for i, param in enumerate(func.parameters):
            param_mlir = self.flow_type_to_mlir(param.type)
            arg_ssa = f'%arg{i}'
            bind_ssa = arg_ssa
            self._ssa_types[arg_ssa] = param_mlir
            var_entry = {
                'type': 'variable',
                'mlir_type': param_mlir,
                'flow_type': param.type,
                'ssa_name': bind_ssa,
            }
            if self._is_tensor_struct(param_mlir):
                self._tensor_param_ssas.add(arg_ssa)
                stable, mat_ops = self._materialize_tensor_param_metadata(
                    arg_ssa, param_mlir
                )
                param_prologue.extend(mat_ops)
                bind_ssa = stable
                self._tensor_stable_ssas.add(stable)
                self._ssa_types[stable] = param_mlir
            elif (
                getattr(param.type, "name", None) in self._COMPOSITE_FIELD_MATERIALIZE_TYPES
                and ("backward" in func.name or func.name.startswith("dense") or func.name.startswith("mlp"))
            ):
                stable, mat_ops = self._materialize_struct_value(arg_ssa, param_mlir)
                param_prologue.extend(mat_ops)
                bind_ssa = stable
                self._ssa_types[stable] = param_mlir
            var_entry["ssa_name"] = bind_ssa
            if self._uses_alloca_storage(param_mlir, param.type):
                ptr, alloc_ops = self._emit_alloca_store(bind_ssa, param_mlir)
                param_prologue.extend(alloc_ops)
                var_entry["alloca_ptr"] = ptr
            self.symbol_table[param.name] = var_entry

        if param_prologue:
            mlir_code.append("\n".join(param_prologue))

        body_mlir = self.generate_block(func.body)
        if body_mlir.strip():
            mlir_code.append(body_mlir)
        
        # Add explicit return for void functions if none exists
        has_return = self._block_has_return(func.body)
        if not has_return and func.return_type.name == 'void':
            mlir_code.append(f"{self.indent()}func.return")
        
        self.indent_level -= 1
        mlir_code.append(f"{self.indent()}}}")
        
        return "\n".join(mlir_code)
    
    def generate_block(self, block: Block) -> str:
        mlir_code = []
        # New lexical scope
        self._symbol_stack.append(self.symbol_table)
        self.symbol_table = self.symbol_table.copy()
        
        for stmt in block.statements:
            stmt_mlir = self.generate_statement(stmt)
            if stmt_mlir.strip():
                mlir_code.append(stmt_mlir)
                # If this is a return statement, it should be the last one
                if isinstance(stmt, ReturnStatement):
                    break
        # Restore previous scope
        self.symbol_table = self._symbol_stack.pop()
        return "\n".join(mlir_code)

    def _block_has_return(self, block: Block) -> bool:
        for stmt in block.statements:
            if isinstance(stmt, ReturnStatement):
                return True
            if isinstance(stmt, IfStatement):
                if self._block_has_return(stmt.then_block):
                    return True
                for _, elif_block in stmt.elif_blocks:
                    if self._block_has_return(elif_block):
                        return True
                if stmt.else_block and self._block_has_return(stmt.else_block):
                    return True
            if isinstance(stmt, WhileStatement):
                if self._block_has_return(stmt.body):
                    return True
            if isinstance(stmt, ForStatement):
                if self._block_has_return(stmt.body):
                    return True
            if isinstance(stmt, Block):
                if self._block_has_return(stmt):
                    return True
        return False
    
    def generate_statement(self, stmt: Statement) -> str:
        if isinstance(stmt, VarDecl):
            return self.generate_var_decl(stmt)
        elif isinstance(stmt, ReturnStatement):
            return self.generate_return(stmt)
        elif isinstance(stmt, Assignment):
            return self.generate_assignment(stmt)
        elif isinstance(stmt, IfStatement):
            return self.generate_if(stmt)
        elif isinstance(stmt, WhileStatement):
            return self.generate_while(stmt)
        elif isinstance(stmt, ForStatement):
            return self.generate_for(stmt)
        elif isinstance(stmt, LayoutStatement):
            return self.generate_block(stmt.body)
        elif isinstance(stmt, (Literal, Variable, BinaryOperation, UnaryOperation, FunctionCall, VectorLiteral)):
            value_ssa, value_ops = self.generate_expression(stmt)
            # Expression statement: emit ops for side effects / computation, discard value.
            return "\n".join(value_ops)
        else:
            return f"{self.indent()}// Unsupported statement: {type(stmt).__name__}"
    
    def generate_var_decl(self, var_decl: VarDecl) -> str:
        mlir_type = self.flow_type_to_mlir(var_decl.type)
         
        if var_decl.initializer:
            # Special handling for string literals
            if isinstance(var_decl.initializer, Literal) and var_decl.initializer.type.name == 'string':
                # Create global constant for string literal
                str_val = var_decl.initializer.value
                if str_val not in self.string_constants:
                    global_name = f"str_{self.string_counter}"
                    self.string_counter += 1
                    self.string_constants[str_val] = global_name
                else:
                    global_name = self.string_constants[str_val]
                
                # Get pointer to string constant
                init_value = f"%{self.function_counter}"
                self.function_counter += 1
                init_ops = [f"{self.indent()}{init_value} = llvm.mlir.addressof @{global_name} : !llvm.ptr"]
            else:
                init_value, init_ops = self.generate_expression(var_decl.initializer)
            
            # Cast the initializer to the variable's type if needed
            init_type = self._ssa_types.get(init_value) or self.get_expression_type(var_decl.initializer)
            if init_type != mlir_type:
                init_value, cast_ops = self._emit_cast(init_value, init_type, mlir_type)
                init_ops.extend(cast_ops)
            self._ssa_types[init_value] = mlir_type

            from_tensor_field = init_value in self._tensor_field_extracts
            if self._is_tensor_struct(mlir_type) and (
                init_value in self._tensor_call_results
                or from_tensor_field
            ):
                orig_ssa = init_value
                init_value, mat_ops = self._materialize_tensor_for_call(
                    init_value, mlir_type, ""
                )
                init_ops.extend(mat_ops)
                self._tensor_call_results.discard(orig_ssa)
                self._tensor_field_extracts.discard(orig_ssa)
                self._tensor_stable_ssas.add(init_value)
                self._ssa_types[init_value] = mlir_type
            elif (
                mlir_type.startswith("!llvm.struct")
                and getattr(var_decl.type, "name", None) in self._COMPOSITE_FIELD_MATERIALIZE_TYPES
            ):
                orig_ssa = init_value
                init_value, mat_ops = self._materialize_struct_value(init_value, mlir_type)
                init_ops.extend(mat_ops)
                self._composite_call_results.discard(orig_ssa)
                self._ssa_types[init_value] = mlir_type

            # Bind variable name to the SSA value produced by the initializer.
            # MLIR SSA values are immutable; we do not emit an extra "assignment" op.
            var_entry = {
                'type': 'variable',
                'flow_type': var_decl.type,  # Store original FLOW type
                'mlir_type': mlir_type,
                'ssa_name': init_value
            }
            if from_tensor_field and self._is_tensor_struct(mlir_type):
                var_entry["from_tensor_field"] = True
            if self._uses_alloca_storage(mlir_type, var_decl.type):
                ptr, alloc_ops = self._emit_alloca_store(init_value, mlir_type)
                init_ops.extend(alloc_ops)
                var_entry["alloca_ptr"] = ptr
            self.symbol_table[var_decl.name] = var_entry

            return "\n".join(init_ops)
        else:
            # Allocate uninitialized memory
            ssa_name = f"%{self.function_counter}"
            self.function_counter += 1
            
            self.symbol_table[var_decl.name] = {
                'type': 'variable',
                'flow_type': var_decl.type,  # Store original FLOW type
                'mlir_type': mlir_type,
                'ssa_name': ssa_name
            }
            
            if var_decl.type.size:  # Array type
                return f"{self.indent()}{ssa_name} = memref.alloc() {{type = {mlir_type}}} : memref<{var_decl.type.size}x{var_decl.type.element_type.name}>"
            if mlir_type.startswith("memref<"):
                return f"{self.indent()}{ssa_name} = memref.alloc() : {mlir_type}"
            return f"{self.indent()}{ssa_name} = llvm.mlir.undef : {mlir_type}"
    
    def generate_return(self, return_stmt: ReturnStatement) -> str:
        if return_stmt.value:
            # Special handling for string literals
            if isinstance(return_stmt.value, Literal) and return_stmt.value.type.name == 'string':
                # Create global constant for string literal
                str_val = return_stmt.value.value
                if str_val not in self.string_constants:
                    global_name = f"str_{self.string_counter}"
                    self.string_counter += 1
                    self.string_constants[str_val] = global_name
                else:
                    global_name = self.string_constants[str_val]
                
                # Get pointer to string constant
                value_ssa = f"%{self.function_counter}"
                self.function_counter += 1
                lines = [f"{self.indent()}{value_ssa} = llvm.mlir.addressof @{global_name} : !llvm.ptr"]
                return_type = self.flow_type_to_mlir(self.current_function_return_type)
                lines.append(f"{self.indent()}func.return {value_ssa} : {return_type}")
                return "\n".join(lines)
            
            value_ssa, value_ops = self.generate_expression(return_stmt.value)
            lines: List[str] = []
            lines.extend(value_ops)
            # Use the function's return type instead of the expression type
            return_type = self.flow_type_to_mlir(self.current_function_return_type)
            
            # If the value type doesn't match the return type, add a cast
            value_type = self.get_expression_type(return_stmt.value)
            if value_type != return_type:
                value_ssa, cast_ops = self._emit_cast(value_ssa, value_type, return_type)
                lines.extend(cast_ops)

            return_type_name = getattr(self.current_function_return_type, "name", None)
            if (
                return_type.startswith("!llvm.struct")
                and return_type_name in self._COMPOSITE_FIELD_MATERIALIZE_TYPES
            ):
                value_ssa, mat_ops = self._materialize_struct_value(value_ssa, return_type)
                lines.extend(mat_ops)
            elif self._uses_alloca_storage(return_type, self.current_function_return_type):
                value_ssa, mat_ops = self._roundtrip_alloca(value_ssa, return_type, [])
                lines.extend(mat_ops)

            lines.append(f"{self.indent()}func.return {value_ssa} : {return_type}")
            return "\n".join(lines)
        else:
            return f"{self.indent()}func.return"
    
    def generate_assignment(self, assignment: Assignment) -> str:
        value_ssa, value_ops = self.generate_expression(assignment.value)
        ops: List[str] = list(value_ops)

        # Check if this is an array element assignment
        if assignment.target_expr is not None:
            # Array element assignment: arr[i] = value -> memref.store
            access = assignment.target_expr
            if isinstance(access, ArrayAccess):
                # Generate array expression
                array_result = self.generate_expression(access.array)
                if not array_result:
                    array_ssa = f"%{self.function_counter}"
                    self.function_counter += 1
                    array_ops = [f"{self.indent()}{array_ssa} = memref.alloc() : memref<?xi8>"]
                else:
                    array_ssa, array_ops = array_result
                ops.extend(array_ops)

                # Generate index expression
                index_ssa, index_ops = self.generate_expression(access.index)
                ops.extend(index_ops)

                index_type = self._ssa_types.get(index_ssa, 'i32')
                if isinstance(access.index, Variable) and access.index.name in self.symbol_table:
                    index_type = self.symbol_table[access.index.name].get('mlir_type', index_type)

                if self._is_pointer_array_ssa(array_ssa, access):
                    elem_type = self._elem_type_from_array_expr(access.array) or 'f32'
                    val_type = self._ssa_types.get(value_ssa) or self.get_expression_type(assignment.value)
                    if val_type != elem_type:
                        value_ssa, cast_ops = self._emit_cast(value_ssa, val_type, elem_type)
                        ops.extend(cast_ops)
                    gep, gep_ops = self._emit_ptr_index_gep(array_ssa, index_ssa, index_type)
                    ops.extend(gep_ops)
                    ops.append(f"{self.indent()}llvm.store {value_ssa}, {gep} : {elem_type}, !llvm.ptr")
                    return "\n".join(ops)

                if index_type == 'index':
                    final_index = index_ssa
                else:
                    index_cast = f"%{self.function_counter}"
                    self.function_counter += 1
                    ops.append(f"{self.indent()}{index_cast} = arith.index_cast {index_ssa} : i32 to index")
                    final_index = index_cast

                elem_type = 'f32'
                if isinstance(access.array, Variable) and access.array.name in self.symbol_table:
                    arr_type = self.symbol_table[access.array.name].get('mlir_type', '')
                    if 'i32' in arr_type and 'memref' in arr_type:
                        elem_type = 'i32'
                    elif 'f64' in arr_type:
                        elem_type = 'f64'

                ops.append(f"{self.indent()}memref.store {value_ssa}, {array_ssa}[{final_index}] : memref<?x{elem_type}>")
                return "\n".join(ops)
            else:
                return f"{self.indent()}// Unsupported assignment target expression"
        
        # Check if this is a struct assignment
        if assignment.target_expr and isinstance(assignment.target_expr, Variable):
            target_name = assignment.target_expr.name
            if target_name in self.symbol_table:
                target_info = self.symbol_table[target_name]
                target_type = target_info.get('mlir_type', '')
                
                # Check if target is a struct (memref with xi8)
                if target_type.startswith('memref<') and 'xi8>' in target_type:
                    # Struct assignment: copy struct from source to target
                    ops.append(f"{self.indent()}// Struct assignment: copy struct")
                    
                    # Get struct size from target type
                    struct_size = int(target_type.split('<')[1].split('x')[0])
                    
                    # Copy each byte from source to target
                    for i in range(struct_size):
                        # Load byte from source
                        load_name = f"%{self.function_counter}"
                        self.function_counter += 1
                        ops.append(f"{self.indent()}{load_name} = memref.load {value_ssa}[{i}] : memref<{struct_size}xi8>")
                        
                        # Store byte to target
                        ops.append(f"{self.indent()}memref.store {load_name}, {target_info['ssa_name']}[{i}] : memref<{struct_size}xi8>")
                    
                    return "\n".join(ops)
        
        # Regular variable assignment
        if assignment.target in self.symbol_table:
            target_info = self.symbol_table[assignment.target]
            target_type = target_info.get('mlir_type', '')
            value_type = self._ssa_types.get(value_ssa) or self.get_expression_type(assignment.value)
            if target_type and value_type != target_type:
                value_ssa, cast_ops = self._emit_cast(value_ssa, value_type, target_type)
                ops.extend(cast_ops)
            target_info = self.symbol_table[assignment.target]
            target_info["ssa_name"] = value_ssa
            if target_type:
                self._ssa_types[value_ssa] = target_type
            if target_info.get("alloca_ptr") and target_type:
                ops.extend(self._store_aggregate_var(target_info, value_ssa))
            return "\n".join(ops)
        else:
            return f"{self.indent()}// Assignment to undefined variable: {assignment.target}"
    
    def generate_if(self, if_stmt: IfStatement) -> str:
        if not if_stmt.elif_blocks:
            then_assigned = self._assigned_locals(if_stmt.then_block)
            else_assigned = self._assigned_locals(if_stmt.else_block) if if_stmt.else_block else []
            merged_vars = list(dict.fromkeys(then_assigned + else_assigned))
            if merged_vars:
                condition_ssa, condition_ops = self.generate_expression(if_stmt.condition)
                return self._generate_scf_if_with_yield(if_stmt, condition_ssa, merged_vars, condition_ops)
        if self.inside_scf_for:
            return self._generate_scf_if(if_stmt)
        return self._generate_cf_if(if_stmt)
    
    def _assigned_locals(self, block: Block) -> List[str]:
        assigned: List[str] = []
        for stmt in block.statements:
            if isinstance(stmt, Assignment) and stmt.target_expr is None and stmt.target:
                if stmt.target not in assigned:
                    assigned.append(stmt.target)
            elif isinstance(stmt, IfStatement):
                for name in self._assigned_locals(stmt.then_block):
                    if name not in assigned:
                        assigned.append(name)
                for _, elif_block in stmt.elif_blocks:
                    for name in self._assigned_locals(elif_block):
                        if name not in assigned:
                            assigned.append(name)
                if stmt.else_block:
                    for name in self._assigned_locals(stmt.else_block):
                        if name not in assigned:
                            assigned.append(name)
        return assigned

    def _generate_scf_if_with_yield(
        self,
        if_stmt: IfStatement,
        condition_ssa: str,
        merged_vars: List[str],
        prefix_ops: List[str],
    ) -> str:
        mlir_code = list(prefix_ops)
        merged_vars = [v for v in merged_vars if v in self.symbol_table]
        if not merged_vars:
            return "\n".join(prefix_ops)

        types = [self.symbol_table[v]['mlir_type'] for v in merged_vars]
        old_ssas = {v: self.symbol_table[v]['ssa_name'] for v in merged_vars}
        result_names: List[str] = []
        for _ in merged_vars:
            rn = f"%{self.function_counter}"
            self.function_counter += 1
            result_names.append(rn)

        types_str = ', '.join(types)
        results_str = ', '.join(result_names)

        mlir_code.append(f"{self.indent()}{results_str} = scf.if {condition_ssa} -> ({types_str}) {{")
        self.indent_level += 1
        then_body = self.generate_block(if_stmt.then_block)
        if then_body.strip():
            mlir_code.append(then_body)
        then_yields = [self.symbol_table[v]['ssa_name'] for v in merged_vars]
        mlir_code.append(f"{self.indent()}scf.yield {', '.join(then_yields)} : {types_str}")
        self.indent_level -= 1

        mlir_code.append(f"{self.indent()}}} else {{")
        self.indent_level += 1
        if if_stmt.else_block:
            else_body = self.generate_block(if_stmt.else_block)
            if else_body.strip():
                mlir_code.append(else_body)
            else_yields = [self.symbol_table[v]['ssa_name'] for v in merged_vars]
        else:
            else_yields = [old_ssas[v] for v in merged_vars]
        mlir_code.append(f"{self.indent()}scf.yield {', '.join(else_yields)} : {types_str}")
        self.indent_level -= 1
        mlir_code.append(f"{self.indent()}}}")

        for v, rn, ty in zip(merged_vars, result_names, types):
            self.symbol_table[v]['ssa_name'] = rn
            self._ssa_types[rn] = ty

        return "\n".join(mlir_code)

    def _generate_scf_if(self, if_stmt: IfStatement) -> str:
        """Generate scf.if for use inside scf.for regions"""
        mlir_code = []
        
        # Generate condition
        condition_ssa, condition_ops = self.generate_expression(if_stmt.condition)
        mlir_code.extend(condition_ops)

        if not if_stmt.elif_blocks:
            then_assigned = self._assigned_locals(if_stmt.then_block)
            else_assigned = self._assigned_locals(if_stmt.else_block) if if_stmt.else_block else []
            merged_vars = list(dict.fromkeys(then_assigned + else_assigned))
            if merged_vars:
                return self._generate_scf_if_with_yield(if_stmt, condition_ssa, merged_vars, mlir_code)
        
        # Generate if-then-else using scf.if
        if if_stmt.elif_blocks or if_stmt.else_block:
            # Has else or elif - use scf.if with else region
            mlir_code.append(f"{self.indent()}scf.if {condition_ssa} {{")
            self.indent_level += 1
            then_body = self.generate_block(if_stmt.then_block)
            if then_body.strip():
                mlir_code.append(then_body)
            self.indent_level -= 1
            
            # Handle elif/else in the else region
            mlir_code.append(f"{self.indent()}}} else {{")
            self.indent_level += 1
            
            # For elif chains, we need to nest scf.if
            remaining_elifs = list(if_stmt.elif_blocks)
            final_else = if_stmt.else_block
            
            while remaining_elifs or final_else:
                if remaining_elifs:
                    elif_condition, elif_block = remaining_elifs.pop(0)
                    # Generate nested scf.if for elif
                    elif_cond_ssa, elif_cond_ops = self.generate_expression(elif_condition)
                    mlir_code.extend(elif_cond_ops)
                    
                    if remaining_elifs or final_else:
                        # More elifs or else - use scf.if with else
                        mlir_code.append(f"{self.indent()}scf.if {elif_cond_ssa} {{")
                        self.indent_level += 1
                        elif_body = self.generate_block(elif_block)
                        if elif_body.strip():
                            mlir_code.append(elif_body)
                        self.indent_level -= 1
                        mlir_code.append(f"{self.indent()}}} else {{")
                        self.indent_level += 1
                    else:
                        # Last elif - no else needed
                        mlir_code.append(f"{self.indent()}scf.if {elif_cond_ssa} {{")
                        self.indent_level += 1
                        elif_body = self.generate_block(elif_block)
                        if elif_body.strip():
                            mlir_code.append(elif_body)
                        self.indent_level -= 1
                        mlir_code.append(f"{self.indent()}}}")
                else:
                    # Final else block
                    else_body = self.generate_block(final_else)
                    if else_body.strip():
                        mlir_code.append(else_body)
                    final_else = None
            
            # Close all nested else regions
            # Count how many nested levels we opened
            nested_levels = len(if_stmt.elif_blocks) + (1 if if_stmt.else_block else 0)
            for _ in range(nested_levels):
                self.indent_level -= 1
                mlir_code.append(f"{self.indent()}}}")
        else:
            # Simple if with no else
            mlir_code.append(f"{self.indent()}scf.if {condition_ssa} {{")
            self.indent_level += 1
            then_body = self.generate_block(if_stmt.then_block)
            if then_body.strip():
                mlir_code.append(then_body)
            self.indent_level -= 1
            mlir_code.append(f"{self.indent()}}}")
        
        return "\n".join(mlir_code)
    
    def _generate_cf_if(self, if_stmt: IfStatement) -> str:
        """Generate cf.cond_br based if for use outside scf.for regions"""
        mlir_code = []
        
        # Generate condition
        condition_ssa, condition_ops = self.generate_expression(if_stmt.condition)
        mlir_code.extend(condition_ops)
        
        # Create blocks for if/elif/else chain
        current_then_block = self._new_block_label()
        current_else_block = self._new_block_label() if if_stmt.elif_blocks or if_stmt.else_block else self._new_block_label()
        end_block = self._new_block_label()
        
        # Track if any branch needs the end block
        needs_end_block = False
        
        mlir_code.append(f"{self.indent()}cf.cond_br {condition_ssa}, ^{current_then_block}, ^{current_else_block}")
        
        # Generate then block
        mlir_code.append(f"{self.indent()}^{current_then_block}:")
        self.indent_level += 1
        then_body = self.generate_block(if_stmt.then_block)
        if then_body.strip():
            mlir_code.append(then_body)
        # Only add branch if block doesn't already end with a terminator
        if not self._block_has_terminator(then_body):
            mlir_code.append(f"{self.indent()}cf.br ^{end_block}")
            needs_end_block = True
        self.indent_level -= 1
        
        # Generate elif blocks
        current_block = current_else_block
        for elif_condition, elif_block in if_stmt.elif_blocks:
            next_elif_block = self._new_block_label() if (if_stmt.elif_blocks.index((elif_condition, elif_block)) < len(if_stmt.elif_blocks) - 1) or if_stmt.else_block else end_block
            
            # Generate elif condition
            mlir_code.append(f"{self.indent()}^{current_block}:")
            self.indent_level += 1
            elif_cond_ssa, elif_cond_ops = self.generate_expression(elif_condition)
            mlir_code.extend(elif_cond_ops)
            
            elif_then_block = self._new_block_label()
            mlir_code.append(f"{self.indent()}cf.cond_br {elif_cond_ssa}, ^{elif_then_block}, ^{next_elif_block}")
            self.indent_level -= 1
            
            # Generate elif then block
            mlir_code.append(f"{self.indent()}^{elif_then_block}:")
            self.indent_level += 1
            elif_body = self.generate_block(elif_block)
            if elif_body.strip():
                mlir_code.append(elif_body)
            # Only add branch if block doesn't already end with a terminator
            if not self._block_has_terminator(elif_body):
                mlir_code.append(f"{self.indent()}cf.br ^{end_block}")
                needs_end_block = True
            self.indent_level -= 1
            
            current_block = next_elif_block
        
        # Generate else block or pass-through
        if if_stmt.else_block:
            mlir_code.append(f"{self.indent()}^{current_block}:")
            self.indent_level += 1
            else_body = self.generate_block(if_stmt.else_block)
            if else_body.strip():
                mlir_code.append(else_body)
            # Only add branch if block doesn't already end with a terminator
            if not self._block_has_terminator(else_body):
                mlir_code.append(f"{self.indent()}cf.br ^{end_block}")
                needs_end_block = True
            self.indent_level -= 1
        elif current_block != end_block:
            mlir_code.append(f"{self.indent()}^{current_block}:")
            self.indent_level += 1
            mlir_code.append(f"{self.indent()}cf.br ^{end_block}")
            needs_end_block = True
            self.indent_level -= 1
        
        # Only emit end block if at least one branch needs it
        if needs_end_block:
            mlir_code.append(f"{self.indent()}^{end_block}:")
        
        return "\n".join(mlir_code)
    
    def generate_while(self, while_stmt: WhileStatement) -> str:
        mlir_code = []
        
        # Detect loop-carried variables
        loop_carried_vars = self._detect_loop_carried_vars(while_stmt.body)
        
        # Create blocks
        header_block = self._new_block_label()
        body_block = self._new_block_label()
        end_block = self._new_block_label()
        
        # Prepare initial values for loop-carried variables
        init_args = []
        for var_name in loop_carried_vars:
            if var_name in self.symbol_table:
                var_info = self.symbol_table[var_name]
                init_args.append(var_info['ssa_name'])
        
        # Jump to header with initial values
        if init_args:
            # Add types to the arguments
            init_args_with_types = []
            for i, var_name in enumerate(loop_carried_vars):
                if var_name in self.symbol_table:
                    var_info = self.symbol_table[var_name]
                    init_args_with_types.append(f"{init_args[i]} : {var_info['mlir_type']}")
            mlir_code.append(f"{self.indent()}cf.br ^{header_block}({', '.join(init_args_with_types)})")
        else:
            mlir_code.append(f"{self.indent()}cf.br ^{header_block}")
        
        # Header block - check condition and receive loop-carried vars
        # Add block arguments for loop-carried variables
        block_args = []
        for var_name in loop_carried_vars:
            if var_name in self.symbol_table:
                var_info = self.symbol_table[var_name]
                arg_name = f"%{self.function_counter}"
                self.function_counter += 1
                block_args.append(f"{arg_name}: {var_info['mlir_type']}")
                # Update symbol table with new SSA value
                self.symbol_table[var_name] = {
                    **var_info,
                    'ssa_name': arg_name
                }
        
        if block_args:
            mlir_code.append(f"{self.indent()}^{header_block}({', '.join(block_args)}):")
        else:
            mlir_code.append(f"{self.indent()}^{header_block}:")
        
        # Generate condition
        condition_ssa, condition_ops = self.generate_expression(while_stmt.condition)
        if condition_ops:
            mlir_code.append("\n".join(condition_ops))
        
        # Branch based on condition
        body_args = []
        body_args_with_types = []
        for var_name in loop_carried_vars:
            if var_name in self.symbol_table:
                var_info = self.symbol_table[var_name]
                body_args.append(self.symbol_table[var_name]['ssa_name'])
                body_args_with_types.append(f"{self.symbol_table[var_name]['ssa_name']} : {var_info['mlir_type']}")
        
        if body_args:
            mlir_code.append(f"{self.indent()}cf.cond_br {condition_ssa}, ^{body_block}({', '.join(body_args_with_types)}), ^{end_block}")
        else:
            mlir_code.append(f"{self.indent()}cf.cond_br {condition_ssa}, ^{body_block}, ^{end_block}")
        
        # Body block - receive loop-carried vars and execute body
        # Add block arguments for loop-carried variables in body
        body_block_args = []
        for var_name in loop_carried_vars:
            if var_name in self.symbol_table:
                var_info = self.symbol_table[var_name]
                arg_name = f"%{self.function_counter}"
                self.function_counter += 1
                body_block_args.append(f"{arg_name}: {var_info['mlir_type']}")
                # Update symbol table with new SSA value
                self.symbol_table[var_name] = {
                    **var_info,
                    'ssa_name': arg_name
                }
        
        if body_block_args:
            mlir_code.append(f"{self.indent()}^{body_block}({', '.join(body_block_args)}):")
        else:
            mlir_code.append(f"{self.indent()}^{body_block}:")
        
        # Generate body
        self.indent_level += 1
        body_mlir = self.generate_block(while_stmt.body)
        if body_mlir.strip():
            mlir_code.append(body_mlir)
        
        # Prepare final values for next iteration
        final_args = []
        final_args_with_types = []
        for var_name in loop_carried_vars:
            if var_name in self.symbol_table:
                var_info = self.symbol_table[var_name]
                final_args.append(self.symbol_table[var_name]['ssa_name'])
                final_args_with_types.append(f"{self.symbol_table[var_name]['ssa_name']} : {var_info['mlir_type']}")
        
        # Branch back to header with updated values
        if final_args:
            mlir_code.append(f"{self.indent()}cf.br ^{header_block}({', '.join(final_args_with_types)})")
        else:
            mlir_code.append(f"{self.indent()}cf.br ^{header_block}")
        
        self.indent_level -= 1
        
        # End block - receive final values
        # Add block arguments for final values
        end_block_args = []
        for var_name in loop_carried_vars:
            if var_name in self.symbol_table:
                var_info = self.symbol_table[var_name]
                arg_name = f"%{self.function_counter}"
                self.function_counter += 1
                end_block_args.append(f"{arg_name}: {var_info['mlir_type']}")
                # Update symbol table with final SSA value
                self.symbol_table[var_name] = {
                    **var_info,
                    'ssa_name': arg_name
                }
        
        if end_block_args:
            mlir_code.append(f"{self.indent()}^{end_block}({', '.join(end_block_args)}):")
        else:
            mlir_code.append(f"{self.indent()}^{end_block}:")
        
        return "\n".join(mlir_code)
    
    def _collect_assigned_vars(self, block) -> set:
        """Collect all variables that are assigned in a block."""
        assigned = set()
        for stmt in block.statements:
            if isinstance(stmt, Assignment):
                if hasattr(stmt, 'target') and stmt.target_expr is None:
                    assigned.add(stmt.target)
            elif isinstance(stmt, IfStatement):
                assigned.update(self._collect_assigned_vars(stmt.then_block))
                for elif_cond, elif_block in stmt.elif_blocks:
                    assigned.update(self._collect_assigned_vars(elif_block))
                if stmt.else_block:
                    assigned.update(self._collect_assigned_vars(stmt.else_block))
            elif isinstance(stmt, WhileStatement):
                assigned.update(self._collect_assigned_vars(stmt.body))
        return assigned
    
    def generate_for(self, for_stmt: ForStatement) -> str:
        mlir_code = []
        
        if for_stmt.is_parallel:
            # Use scf.parallel for parallel loops
            lower_bound, lower_ops = self.generate_expression(for_stmt.range_start)
            upper_bound, upper_ops = self.generate_expression(for_stmt.range_end)

            if lower_ops:
                mlir_code.append("\n".join(lower_ops))
            if upper_ops:
                mlir_code.append("\n".join(upper_ops))
            
            # Convert bounds to index type if needed
            lower_type = self.get_expression_type(for_stmt.range_start)
            upper_type = self.get_expression_type(for_stmt.range_end)
            
            if lower_type != 'index':
                lower_idx = f"%{self.function_counter}"
                self.function_counter += 1
                mlir_code.append(f"{self.indent()}{lower_idx} = arith.index_cast {lower_bound} : {lower_type} to index")
                lower_bound = lower_idx
            
            if upper_type != 'index':
                upper_idx = f"%{self.function_counter}"
                self.function_counter += 1
                mlir_code.append(f"{self.indent()}{upper_idx} = arith.index_cast {upper_bound} : {upper_type} to index")
                upper_bound = upper_idx
            
            # Step constant
            step_ssa = f"%{self.function_counter}"
            self.function_counter += 1
            mlir_code.append(f"{self.indent()}{step_ssa} = arith.constant 1 : index")
            
            # Induction variable
            iv_name = f"%{self.function_counter}"
            self.function_counter += 1
            self._ssa_types[iv_name] = 'index'
            
            # Add loop variable to symbol table
            self.symbol_table[for_stmt.variable] = {
                'type': 'variable',
                'mlir_type': 'index',
                'ssa_name': iv_name
            }
            
            mlir_code.append(f"{self.indent()}scf.parallel ({iv_name}) = ({lower_bound}) to ({upper_bound}) step ({step_ssa}) {{")
            self.indent_level += 1
            
            body_mlir = self.generate_block(for_stmt.body)
            if body_mlir.strip():
                mlir_code.append(body_mlir)
            
            mlir_code.append(f"{self.indent()}scf.reduce")
            self.indent_level -= 1
            mlir_code.append(f"{self.indent()}}}") 
        else:
            # Use scf.for for sequential loops
            # Detect loop-carried variables (variables assigned in loop body)
            loop_carried_vars = self._detect_loop_carried_vars(for_stmt.body)
            
            lower_bound, lower_ops = self.generate_expression(for_stmt.range_start)
            upper_bound, upper_ops = self.generate_expression(for_stmt.range_end)

            if lower_ops:
                mlir_code.append("\n".join(lower_ops))
            if upper_ops:
                mlir_code.append("\n".join(upper_ops))

            # Cast bounds to index type
            lb_idx = f"%{self.function_counter}"
            self.function_counter += 1
            ub_idx = f"%{self.function_counter}"
            self.function_counter += 1
            step_idx = f"%{self.function_counter}"
            self.function_counter += 1

            mlir_code.append(f"{self.indent()}{lb_idx} = arith.index_cast {lower_bound} : i32 to index")
            mlir_code.append(f"{self.indent()}{ub_idx} = arith.index_cast {upper_bound} : i32 to index")
            mlir_code.append(f"{self.indent()}{step_idx} = arith.constant 1 : index")

            # Induction variable
            iv = f"%{self.function_counter}"
            self.function_counter += 1
            self._ssa_types[iv] = 'index'

            # Collect initial values and types for iter_args
            iter_args_init = []
            iter_args_types = []
            iter_args_names = []
            for var_name in loop_carried_vars:
                if var_name in self.symbol_table:
                    var_info = self.symbol_table[var_name]
                    iter_args_init.append(var_info['ssa_name'])
                    iter_args_types.append(var_info['mlir_type'])
                    iter_args_names.append(var_name)

            if iter_args_init:
                # scf.for with iter_args
                iter_vars = []
                for i, var_name in enumerate(iter_args_names):
                    iter_var = f"%{self.function_counter}"
                    self.function_counter += 1
                    iter_vars.append(iter_var)
                
                iter_args_spec = ", ".join(
                    f"{iter_vars[i]} = {iter_args_init[i]}" for i in range(len(iter_vars))
                )
                if len(iter_args_names) == 1:
                    result_vars = [f"%{self.function_counter}"]
                    self.function_counter += 1
                else:
                    result_vars = []
                    for _ in iter_args_names:
                        rn = f"%{self.function_counter}"
                        self.function_counter += 1
                        result_vars.append(rn)
                result_lhs = result_vars[0] if len(result_vars) == 1 else ", ".join(result_vars)
                
                mlir_code.append(
                    f"{self.indent()}{result_lhs} = scf.for {iv} = {lb_idx} to {ub_idx} step {step_idx} "
                    f"iter_args({iter_args_spec}) -> ({', '.join(iter_args_types)}) {{"
                )
                self.indent_level += 1

                old_inside_scf_for = self.inside_scf_for
                self.inside_scf_for = True
                
                # Update symbol table with iter_args SSA names inside loop
                for i, var_name in enumerate(iter_args_names):
                    self.symbol_table[var_name]['ssa_name'] = iter_vars[i]
                    self._ssa_types[iter_vars[i]] = iter_args_types[i]
                
                # Add loop variable to symbol table
                self.symbol_table[for_stmt.variable] = {
                    'type': 'variable',
                    'mlir_type': 'index',
                    'ssa_name': iv
                }
                
                body_mlir = self.generate_block(for_stmt.body)
                if body_mlir.strip():
                    mlir_code.append(body_mlir)
                
                # Yield updated values
                yield_vals = [self.symbol_table[var_name]['ssa_name'] for var_name in iter_args_names]
                mlir_code.append(f"{self.indent()}scf.yield {', '.join(yield_vals)} : {', '.join(iter_args_types)}")
                
                self.inside_scf_for = old_inside_scf_for
                self.indent_level -= 1
                mlir_code.append(f"{self.indent()}}}")
                
                # Update symbol table with result SSA names after loop
                for i, var_name in enumerate(iter_args_names):
                    self.symbol_table[var_name]['ssa_name'] = result_vars[i]
                    self._ssa_types[result_vars[i]] = iter_args_types[i]
            else:
                # Simple scf.for without iter_args
                mlir_code.append(f"{self.indent()}scf.for {iv} = {lb_idx} to {ub_idx} step {step_idx} {{")
                self.indent_level += 1
                
                # Set flag for nested if statements
                old_inside_scf_for = self.inside_scf_for
                self.inside_scf_for = True
                
                # Add loop variable to symbol table
                self.symbol_table[for_stmt.variable] = {
                    'type': 'variable',
                    'mlir_type': 'index',
                    'ssa_name': iv
                }
                
                body_mlir = self.generate_block(for_stmt.body)
                if body_mlir.strip():
                    mlir_code.append(body_mlir)
                
                # Restore flag
                self.inside_scf_for = old_inside_scf_for
                
                self.indent_level -= 1
                mlir_code.append(f"{self.indent()}}}")
        
        return "\n".join(mlir_code)
    
    def _detect_loop_carried_vars(self, body: Block) -> List[str]:
        """Detect variables that are assigned inside a loop body and exist before the loop."""
        assigned_vars = self._assigned_locals(body)
        declared_vars = self._collect_declared_vars_from_block(body)
        carried: List[str] = []
        for var_name in assigned_vars:
            if var_name in self.symbol_table and var_name not in declared_vars and var_name not in carried:
                carried.append(var_name)
        return carried
    
    def _collect_declared_vars_from_stmt(self, stmt) -> List[str]:
        """Collect all variable declarations from a statement (including nested blocks)."""
        declared = []
        
        if isinstance(stmt, IfStatement):
            # Check then block
            declared.extend(self._collect_declared_vars_from_block(stmt.then_block))
            # Check elif blocks
            for elif_cond, elif_block in stmt.elif_blocks:
                declared.extend(self._collect_declared_vars_from_block(elif_block))
            # Check else block
            if stmt.else_block:
                declared.extend(self._collect_declared_vars_from_block(stmt.else_block))
        elif isinstance(stmt, WhileStatement):
            declared.extend(self._collect_declared_vars_from_block(stmt.body))
        elif isinstance(stmt, ForStatement):
            declared.extend(self._collect_declared_vars_from_block(stmt.body))
        
        return declared
    
    def _collect_declared_vars_from_block(self, block) -> List[str]:
        """Collect all variable declarations from a block."""
        declared = []
        for stmt in block.statements:
            if isinstance(stmt, VarDecl):
                declared.append(stmt.name)
            else:
                declared.extend(self._collect_declared_vars_from_stmt(stmt))
        return declared
    
    def generate_handle(self, handle_stmt: HandleStatement) -> str:
        prev = self._effect_handler_stack[-1]
        curr = dict(prev)
        effects = handle_stmt.effects
        handlers = handle_stmt.handlers
        if len(handlers) == 1 and len(effects) > 1:
            for effect in effects:
                curr[effect] = handlers[0]
        elif len(handlers) == len(effects):
            for effect, handler in zip(effects, handlers):
                curr[effect] = handler
        else:
            raise ValueError(f"handle expects 1 handler or the same count as effects; got {len(effects)} effects and {len(handlers)} handlers")
        self._effect_handler_stack.append(curr)
        try:
            return self.generate_block(handle_stmt.body)
        finally:
            self._effect_handler_stack.pop()

    def generate_match(self, match_stmt: 'MatchStatement') -> str:
        # Always use SCF match as it supports struct destructuring
        return self._generate_scf_match(match_stmt)

    def _generate_scf_match(self, match_stmt: 'MatchStatement') -> str:
        """Generate match using control flow (cf) dialect for maximum flexibility."""
        mlir_code = []
        val_ssa, val_ops = self.generate_expression(match_stmt.value)
        mlir_code.extend(val_ops)
        val_type = self.get_expression_type(match_stmt.value)
        
        # Determine comparison op
        if "ptr" in val_type:
            cmp_op = 'llvm.icmp "eq"'
            use_comma = False
        else:
            cmp_op = "arith.cmpi eq" if "i" in val_type or "index" in val_type or "i1" in val_type else "arith.cmpf oeq"
            use_comma = True
        
        # Generate labels for each case and the end
        case_labels = []
        next_case_labels = []
        for i in range(len(match_stmt.cases)):
            case_labels.append(self._new_block_label())
            next_case_labels.append(self._new_block_label())
        
        end_label = self._new_block_label()
        
        # Process each case
        for idx, case in enumerate(match_stmt.cases):
            case_label = case_labels[idx]
            next_label = next_case_labels[idx]
            
            # Generate condition check
            cond_ssa = ""
            binding_ops = []
            saved_locals = None
            
            if isinstance(case.pattern, StructPattern):
                # Handle Struct Destructuring
                struct_pattern = case.pattern
                struct_decl = self._get_struct_decl(struct_pattern.struct_name)
                
                # Unconditional match for same type (assuming type checker verified it)
                cond_ssa = f"%{self.function_counter}"
                self.function_counter += 1
                mlir_code.append(f"{self.indent()}{cond_ssa} = arith.constant 1 : i1")
                
                if struct_decl:
                    saved_locals = self.symbol_table.copy()
                    
                    # Create temp variable for val_ssa to allow FieldAccess reuse
                    temp_var_name = f"__match_input_{self.function_counter}"
                    self.symbol_table[temp_var_name] = {'ssa_name': val_ssa, 'mlir_type': val_type}
                    
                    for field_idx, binding_name in enumerate(struct_pattern.bindings):
                        if field_idx < len(struct_decl.fields):
                            field_decl = struct_decl.fields[field_idx]
                            
                            # Generate field access
                            field_access = FieldAccess(Variable(temp_var_name), field_decl.name)
                            field_ssa, field_ops = self.generate_field_access(field_access)
                            
                            binding_ops.extend(field_ops)
                            
                            # Bind to local name
                            self.symbol_table[binding_name] = {
                                'ssa_name': field_ssa,
                                'mlir_type': self.flow_type_to_mlir(field_decl.type),
                                'flow_type': field_decl.type,
                                'type': 'variable'
                            }
            else:
                pattern_ssa, pattern_ops = self.generate_expression(case.pattern)
                mlir_code.extend(pattern_ops)
                
                cond_ssa = f"%{self.function_counter}"
                self.function_counter += 1
                if use_comma:
                    mlir_code.append(f"{self.indent()}{cond_ssa} = {cmp_op}, {val_ssa}, {pattern_ssa} : {val_type}")
                else:
                    mlir_code.append(f"{self.indent()}{cond_ssa} = {cmp_op} {val_ssa}, {pattern_ssa} : {val_type}")
            
            # Branch to case body or next case
            mlir_code.append(f"{self.indent()}cf.cond_br {cond_ssa}, ^{case_label}, ^{next_label}")
            
            # Generate case body block
            mlir_code.append(f"^{case_label}:")
            self.indent_level += 1
            
            if binding_ops:
                mlir_code.extend(binding_ops)
            
            body = self.generate_block(case.body)
            if body.strip():
                mlir_code.append(body)
            
            # Branch to end
            mlir_code.append(f"{self.indent()}cf.br ^{end_label}")
            
            self.indent_level -= 1
            
            # Restore symbol table if we had bindings
            if saved_locals is not None:
                self.symbol_table = saved_locals
            
            # Generate next case check block (if not last)
            if idx < len(match_stmt.cases) - 1:
                mlir_code.append(f"^{next_label}:")
        
        # Generate default case or final fallthrough
        final_next_label = next_case_labels[-1] if next_case_labels else end_label
        
        if match_stmt.default_case:
            mlir_code.append(f"^{final_next_label}:")
            self.indent_level += 1
            default_body = self.generate_block(match_stmt.default_case)
            if default_body.strip():
                mlir_code.append(default_body)
            mlir_code.append(f"{self.indent()}cf.br ^{end_label}")
            self.indent_level -= 1
        else:
            # If no default, just make the last next label jump to end
            mlir_code.append(f"^{final_next_label}:")
            mlir_code.append(f"{self.indent()}cf.br ^{end_label}")
        
        # End block
        mlir_code.append(f"^{end_label}:")
        
        return "\n".join(mlir_code)
    
    def generate_expression(self, expr: Expression) -> tuple[str, List[str]]:
        if isinstance(expr, Literal):
            return self.generate_literal(expr)
        elif isinstance(expr, Variable):
            return self.generate_variable(expr)
        elif isinstance(expr, BinaryOperation):
            return self.generate_binary_operation(expr)
        elif isinstance(expr, UnaryOperation):
            return self.generate_unary_operation(expr)
        elif isinstance(expr, FunctionCall):
            return self.generate_function_call(expr)
        elif isinstance(expr, EffectCall):
            return self.generate_effect_call(expr)
        elif isinstance(expr, MethodCall):
            return self.generate_method_call(expr)
        elif isinstance(expr, ArrayLiteral):
            return self.generate_array_literal(expr)
        elif isinstance(expr, VectorLiteral):
            return self.generate_vector_literal(expr)
        elif isinstance(expr, CastExpression):
            value_ssa, value_ops = self.generate_expression(expr.expr)
            from_type = self.get_expression_type(expr.expr)
            to_type = self.flow_type_to_mlir(expr.target_type)
            cast_ssa, cast_ops = self._emit_cast(value_ssa, from_type, to_type)
            return cast_ssa, value_ops + cast_ops
        elif isinstance(expr, ArrayAccess):
            return self.generate_array_access(expr)
        elif isinstance(expr, FieldAccess):
            return self.generate_field_access(expr)
        elif isinstance(expr, StructLiteral):
            return self.generate_struct_literal(expr)
        else:
            return f"// Unsupported expression type: {type(expr).__name__}", []

    def _emit_cast(self, value_ssa: str, from_type: str, to_type: str) -> tuple[str, List[str]]:
        from_type = self._ssa_types.get(value_ssa, from_type)
        if from_type == to_type:
            return value_ssa, []

        cast_name = f"%{self.function_counter}"
        self.function_counter += 1

        def _int_width(ty: str) -> int:
            try:
                return int(ty[1:])
            except Exception:
                return 0

        def _is_unsigned(ty: str) -> bool:
            return ty.startswith("u")

        # Index casts
        if from_type == "index" and to_type.startswith("i"):
            self._ssa_types[cast_name] = to_type
            return cast_name, [f"{self.indent()}{cast_name} = arith.index_cast {value_ssa} : index to {to_type}"]
        if to_type == "index" and from_type.startswith("i"):
            self._ssa_types[cast_name] = to_type
            return cast_name, [f"{self.indent()}{cast_name} = arith.index_cast {value_ssa} : {from_type} to index"]

        # Integer width casts
        if (from_type.startswith("i") or from_type.startswith("u")) and (to_type.startswith("i") or to_type.startswith("u")):
            if _int_width(from_type) < _int_width(to_type):
                ext_op = "arith.extui" if _is_unsigned(from_type) else "arith.extsi"
                self._ssa_types[cast_name] = to_type
                return cast_name, [f"{self.indent()}{cast_name} = {ext_op} {value_ssa} : {from_type} to {to_type}"]
            self._ssa_types[cast_name] = to_type
            return cast_name, [f"{self.indent()}{cast_name} = arith.trunci {value_ssa} : {from_type} to {to_type}"]

        # Bool/integer casts
        if from_type == "i1" and to_type.startswith("i"):
            self._ssa_types[cast_name] = to_type
            return cast_name, [f"{self.indent()}{cast_name} = arith.extui {value_ssa} : i1 to {to_type}"]
        if to_type == "i1" and from_type.startswith("i"):
            self._ssa_types[cast_name] = to_type
            return cast_name, [f"{self.indent()}{cast_name} = arith.trunci {value_ssa} : {from_type} to i1"]

        # Float width casts
        if from_type in ["f32", "f64"] and to_type in ["f32", "f64"]:
            if from_type == "f32" and to_type == "f64":
                self._ssa_types[cast_name] = to_type
                return cast_name, [f"{self.indent()}{cast_name} = arith.extf {value_ssa} : f32 to f64"]
            self._ssa_types[cast_name] = to_type
            return cast_name, [f"{self.indent()}{cast_name} = arith.truncf {value_ssa} : f64 to f32"]

        # Int/float casts (signed)
        if from_type.startswith("i") and to_type in ["f32", "f64"]:
            self._ssa_types[cast_name] = to_type
            return cast_name, [f"{self.indent()}{cast_name} = arith.sitofp {value_ssa} : {from_type} to {to_type}"]
        if from_type in ["f32", "f64"] and (to_type.startswith("i") or to_type.startswith("u")):
            self._ssa_types[cast_name] = to_type
            return cast_name, [f"{self.indent()}{cast_name} = arith.fptosi {value_ssa} : {from_type} to {to_type}"]

        # Fallback: no cast op available, return original value.
        return value_ssa, []
    
    def generate_literal(self, literal: Literal) -> tuple[str, List[str]]:
        ssa_name = f"%{self.function_counter}"
        self.function_counter += 1
        mlir_type = self.flow_type_to_mlir(literal.type)
        
        if literal.type.name == 'bool':
            mlir_type = 'i1'
            # Convert boolean to integer constant (true=1, false=0)
            bool_value = '1' if literal.value == 'true' else '0'
            line = f"{self.indent()}{ssa_name} = arith.constant {bool_value} : {mlir_type}"
        elif literal.type.name == 'string':
            str_val = literal.value
            if str_val not in self.string_constants:
                global_name = f"str_{self.string_counter}"
                self.string_counter += 1
                self.string_constants[str_val] = global_name
            else:
                global_name = self.string_constants[str_val]
            line = f"{self.indent()}{ssa_name} = llvm.mlir.addressof @{global_name} : !llvm.ptr"
        else:
            numeric = self._format_mlir_numeric(str(literal.value), mlir_type)
            line = f"{self.indent()}{ssa_name} = arith.constant {numeric} : {mlir_type}"
        self._ssa_types[ssa_name] = mlir_type
        return ssa_name, [line]
    
    def generate_variable(self, variable: Variable) -> tuple[str, List[str]]:
        if variable.name in self.symbol_table:
            var_info = self.symbol_table[variable.name]
            mlir_type = var_info.get("mlir_type")
            if var_info.get("alloca_ptr") and mlir_type:
                return self._emit_alloca_load(var_info["alloca_ptr"], mlir_type)
            if "ssa_name" in var_info and mlir_type:
                ssa = var_info["ssa_name"]
                if ssa not in self._ssa_types:
                    self._ssa_types[ssa] = mlir_type
                return ssa, []
            return var_info.get("ssa_name", f"# bad var {variable.name}"), []
        else:
            return f"# Undefined variable: {variable.name}", []

    def _resolve_binary_operand_type(self, left_ty: str, right_ty: str) -> str:
        if 'vector<' in left_ty or 'vector<' in right_ty:
            return left_ty if 'vector<' in left_ty else right_ty
        if 'f64' in (left_ty, right_ty):
            return 'f64'
        if 'f32' in (left_ty, right_ty):
            return 'f32'
        if left_ty == 'index' and right_ty == 'index':
            return 'index'
        if left_ty == 'index' or right_ty == 'index':
            return 'i32'

        def _is_int(ty: str) -> bool:
            return ty.startswith('i') or ty.startswith('u')

        def _int_width(ty: str) -> int:
            try:
                return int(ty[1:])
            except Exception:
                return 0

        if left_ty == 'i1' or right_ty == 'i1':
            return 'i1'
        if _is_int(left_ty) or _is_int(right_ty):
            return 'i64' if max(_int_width(left_ty), _int_width(right_ty)) > 32 else 'i32'
        return left_ty
    
    def generate_binary_operation(self, bin_op: BinaryOperation) -> tuple[str, List[str]]:
        # Special handling for string concatenation
        if bin_op.operator == '+':
            left_ty = self.get_expression_type(bin_op.left)
            right_ty = self.get_expression_type(bin_op.right)
            
            # Check if this is string concatenation
            if left_ty == '!llvm.ptr' or right_ty == '!llvm.ptr':
                # For MLIR generation, just return a dummy string pointer
                # String concatenation will be handled at the C code generation level
                ssa_name = f"%{self.function_counter}"
                self.function_counter += 1
                return ssa_name, [f"{self.indent()}# String concatenation: {left_ty} + {right_ty}"]
        
        left_ssa, left_ops = self.generate_expression(bin_op.left)
        right_ssa, right_ops = self.generate_expression(bin_op.right)

        ssa_name = f"%{self.function_counter}"
        self.function_counter += 1
        
        # Determine operation based on operator
        left_ty = self.get_expression_type(bin_op.left)
        right_ty = self.get_expression_type(bin_op.right)

        # Check if this is a vector operation
        is_vector = 'vector<' in left_ty or 'vector<' in right_ty
        is_float = ('f32' in left_ty) or ('f64' in left_ty) or ('f32' in right_ty) or ('f64' in right_ty)

        if bin_op.operator in ['&&', 'and', '||', 'or']:
            operand_type = 'i1'
        else:
            operand_type = self._resolve_binary_operand_type(left_ty, right_ty)

        cast_ops: List[str] = []
        if not is_vector:
            if left_ty != operand_type:
                left_ssa, ops = self._emit_cast(left_ssa, left_ty, operand_type)
                cast_ops.extend(ops)
            if right_ty != operand_type:
                right_ssa, ops = self._emit_cast(right_ssa, right_ty, operand_type)
                cast_ops.extend(ops)

        op_text: str
        if bin_op.operator == '+':
            if is_vector:
                op_text = f"arith.addf {left_ssa}, {right_ssa} : {operand_type}" if is_float else f"arith.addi {left_ssa}, {right_ssa} : {operand_type}"
            else:
                op_text = f"arith.addf {left_ssa}, {right_ssa} : {operand_type}" if is_float else f"arith.addi {left_ssa}, {right_ssa} : {operand_type}"
        elif bin_op.operator == '-':
            op_text = f"arith.subf {left_ssa}, {right_ssa} : {operand_type}" if is_float else f"arith.subi {left_ssa}, {right_ssa} : {operand_type}"
        elif bin_op.operator == '*':
            op_text = f"arith.mulf {left_ssa}, {right_ssa} : {operand_type}" if is_float else f"arith.muli {left_ssa}, {right_ssa} : {operand_type}"
        elif bin_op.operator == '/':
            op_text = f"arith.divf {left_ssa}, {right_ssa} : {operand_type}" if is_float else f"arith.divsi {left_ssa}, {right_ssa} : {operand_type}"
        elif bin_op.operator == '%':
            op_text = f"arith.remf {left_ssa}, {right_ssa} : {operand_type}" if is_float else f"arith.remsi {left_ssa}, {right_ssa} : {operand_type}"
        elif bin_op.operator in ['==', '!=', '<', '<=', '>', '>=']:
            if bin_op.operator == '==':
                pred = 'oeq' if is_float else 'eq'
            elif bin_op.operator == '!=':
                pred = 'one' if is_float else 'ne'
            elif bin_op.operator == '<':
                pred = 'olt' if is_float else 'slt'
            elif bin_op.operator == '<=':
                pred = 'ole' if is_float else 'sle'
            elif bin_op.operator == '>':
                pred = 'ogt' if is_float else 'sgt'
            else:
                pred = 'oge' if is_float else 'sge'

            if is_float:
                op_text = f"arith.cmpf {pred}, {left_ssa}, {right_ssa} : {operand_type}"
            else:
                op_text = f"arith.cmpi {pred}, {left_ssa}, {right_ssa} : {operand_type}"
        elif bin_op.operator == '&&' or bin_op.operator == 'and':
            op_text = f"arith.andi {left_ssa}, {right_ssa} : i1"
        elif bin_op.operator == '||' or bin_op.operator == 'or':
            op_text = f"arith.ori {left_ssa}, {right_ssa} : i1"
        else:
            return f"// Unsupported binary operator: {bin_op.operator}", left_ops + right_ops
        
        lines: List[str] = []
        lines.extend(left_ops)
        lines.extend(right_ops)
        lines.extend(cast_ops)
        lines.append(f"{self.indent()}{ssa_name} = {op_text}")
        result_type = 'i1' if bin_op.operator in ['==', '!=', '<', '<=', '>', '>=', '&&', 'and', '||', 'or'] else operand_type
        self._ssa_types[ssa_name] = result_type
        return ssa_name, lines
    
    def generate_unary_operation(self, un_op: UnaryOperation) -> tuple[str, List[str]]:
        operand_ssa, operand_ops = self.generate_expression(un_op.operand)
        ssa_name = f"%{self.function_counter}"
        self.function_counter += 1
        ty = self.get_expression_type(un_op.operand)
        
        if un_op.operator == '-':
            if 'f32' in ty or 'f64' in ty:
                self._ssa_types[ssa_name] = ty
                return ssa_name, operand_ops + [f"{self.indent()}{ssa_name} = arith.negf {operand_ssa} : {ty}"]
            zero_ssa = f"%{self.function_counter}"
            self.function_counter += 1
            ops = list(operand_ops)
            ops.append(f"{self.indent()}{zero_ssa} = arith.constant 0 : {ty}")
            ops.append(f"{self.indent()}{ssa_name} = arith.subi {zero_ssa}, {operand_ssa} : {ty}")
            self._ssa_types[ssa_name] = ty
            return ssa_name, ops
        elif un_op.operator in ['!', 'not']:
            # %not = xor %x, true
            c1 = f"%{self.function_counter}"
            self.function_counter += 1
            cast_name = f"%{self.function_counter}"
            self.function_counter += 1
            ops = []
            ops.extend(operand_ops)
            
            # Ensure operand is i1 (boolean)
            if 'i1' not in ty:
                zero_ssa = f"%{self.function_counter}"
                self.function_counter += 1
                ops.append(f"{self.indent()}{zero_ssa} = arith.constant 0 : {ty}")
                ops.append(f"{self.indent()}{cast_name} = arith.cmpi ne {operand_ssa}, {zero_ssa} : {ty}")
                operand_ssa = cast_name
                ty = 'i1'
            
            ops.append(f"{self.indent()}{c1} = arith.constant 1 : i1")
            ops.append(f"{self.indent()}{ssa_name} = arith.xori {operand_ssa}, {c1} : i1")
            self._ssa_types[ssa_name] = "i1"
            return ssa_name, ops
        else:
            return f"// Unsupported unary operator: '{un_op.operator}' (type: {type(un_op.operator)})", operand_ops
    
    def generate_field_access(self, field_access: FieldAccess) -> tuple[str, List[str]]:
        """Generate field access that loads values from struct memory"""
        obj_result = self.generate_expression(field_access.object)
        if obj_result is None:
            # Fallback if object expression fails
            ssa_name = f"%{self.function_counter}"
            self.function_counter += 1
            return ssa_name, [f"{self.indent()}// Failed to generate object expression for field access"]
        
        obj_ssa, obj_ops = obj_result
        ops = list(obj_ops)

        if isinstance(field_access.object, Variable):
            var_info = self.symbol_table.get(field_access.object.name)
            flow_type = var_info.get("flow_type") if var_info else None
            struct_name = getattr(flow_type, "name", None) if flow_type else None
            if (
                var_info
                and struct_name in self._COMPOSITE_FIELD_MATERIALIZE_TYPES
                and (
                    obj_ssa in self._composite_call_results
                    or obj_ssa.startswith("%arg")
                )
            ):
                obj_mlir = var_info.get("mlir_type") or (
                    self.flow_type_to_mlir(flow_type) if flow_type else None
                )
                if obj_mlir:
                    orig_ssa = obj_ssa
                    obj_ssa, mat_ops = self._materialize_struct_value(obj_ssa, obj_mlir)
                    ops.extend(mat_ops)
                    self._composite_call_results.discard(orig_ssa)
                    if not orig_ssa.startswith("%arg"):
                        var_info["ssa_name"] = obj_ssa
                    self._ssa_types[obj_ssa] = obj_mlir

        # Try to determine the field type by walking the struct hierarchy
        field_type = self._determine_field_type(field_access)
        
        if not field_type:
            # Default to i32 if we can't determine the type
            ssa_name = f"%{self.function_counter}"
            self.function_counter += 1
            ops.append(f"{self.indent()}{ssa_name} = arith.constant 0 : i32")
            return ssa_name, ops
        
        # Prefer LLVM struct extraction when available.
        obj_type = self._determine_struct_type(field_access.object)
        if obj_type:
            llvm_struct = self._struct_llvm_type(obj_type.name)
            if llvm_struct:
                decl = self._get_struct_decl(obj_type.name)
                if decl:
                    field_names = [f.name for f in decl.fields]
                    if field_access.field in field_names:
                        idx = field_names.index(field_access.field)
                        extract_ssa = obj_ssa
                        if obj_type.name == "Tensor" and idx >= 1:
                            if isinstance(field_access.object, Variable):
                                var_info = self.symbol_table.get(field_access.object.name) or {}
                                root = var_info.get("ssa_name", obj_ssa)
                                if root.startswith("%arg") or root in self._tensor_param_ssas:
                                    extract_ssa = root
                            elif (
                                isinstance(field_access.object, FieldAccess)
                                and obj_ssa in self._tensor_extract_origins
                            ):
                                origin_ssa, origin_idx = self._tensor_extract_origins[obj_ssa]
                                origin_type = self._ssa_types.get(origin_ssa)
                                if origin_type and origin_type.startswith("!llvm.struct"):
                                    ssa_name = f"%{self.function_counter}"
                                    self.function_counter += 1
                                    ops.append(
                                        f"{self.indent()}{ssa_name} = llvm.extractvalue "
                                        f"{origin_ssa}[{origin_idx}] : {origin_type}"
                                    )
                                    inner = f"%{self.function_counter}"
                                    self.function_counter += 1
                                    inner_ty = self._ssa_types.get(ssa_name) or self.flow_type_to_mlir(
                                        field_type
                                    )
                                    if inner_ty.startswith("!llvm.struct"):
                                        ops.append(
                                            f"{self.indent()}{inner} = llvm.extractvalue "
                                            f"{ssa_name}[{idx}] : {inner_ty}"
                                        )
                                        field_ty = self.flow_type_to_mlir(field_type)
                                        self._ssa_types[inner] = field_ty
                                        return inner, ops
                        ssa_name = f"%{self.function_counter}"
                        self.function_counter += 1
                        ops.append(f"{self.indent()}{ssa_name} = llvm.extractvalue {extract_ssa}[{idx}] : {llvm_struct}")
                        field_ty = self.flow_type_to_mlir(field_type)
                        self._ssa_types[ssa_name] = field_ty
                        if self._is_tensor_struct(field_ty):
                            self._tensor_field_extracts.add(ssa_name)
                            self._tensor_extract_origins[ssa_name] = (obj_ssa, idx)
                        return ssa_name, ops

        # Get the struct layout to find field offset
        obj_type = self._determine_struct_type(field_access.object)
        if not obj_type or obj_type.name not in self.struct_layouts:
            # Fallback
            ssa_name = f"%{self.function_counter}"
            self.function_counter += 1
            if field_type.name == 'f32':
                ops.append(f"{self.indent()}{ssa_name} = arith.constant 0.0 : f32")
            else:
                ops.append(f"{self.indent()}{ssa_name} = arith.constant 0 : i32")
            return ssa_name, ops
        
        layout = self.struct_layouts[obj_type.name]
        total_size = sum(field['size'] for field in layout.values())
        if field_access.field not in layout:
            # Field not found
            ssa_name = f"%{self.function_counter}"
            self.function_counter += 1
            if field_type.name == 'f32':
                ops.append(f"{self.indent()}{ssa_name} = arith.constant 0.0 : f32")
            else:
                ops.append(f"{self.indent()}{ssa_name} = arith.constant 0 : i32")
            return ssa_name, ops
        
        field_info = layout[field_access.field]
        offset = field_info['offset']
        
        # Load field from memory
        ssa_name = f"%{self.function_counter}"
        self.function_counter += 1
        
        if field_type.name == 'f32':
            # Load f32 from memory (4 bytes, little-endian)
            ops.append(f"{self.indent()}// Load {field_access.field} (f32) at offset {offset}")
            
            # Load 4 bytes and combine
            loaded_bytes = []
            for i in range(4):
                byte_offset = offset + i
                
                offset_ssa = f"%{self.function_counter}"
                self.function_counter += 1
                ops.append(f"{self.indent()}{offset_ssa} = arith.constant {byte_offset} : index")
                
                byte_name = f"%{self.function_counter}"
                self.function_counter += 1
                ops.append(f"{self.indent()}{byte_name} = memref.load {obj_ssa}[{offset_ssa}] : memref<{total_size}xi8>")
                loaded_bytes.append(byte_name)
            
            # Extend each byte to i32
            extended_bytes = []
            for byte_name in loaded_bytes:
                ext_name = f"%{self.function_counter}"
                self.function_counter += 1
                ops.append(f"{self.indent()}{ext_name} = arith.extsi {byte_name} : i8 to i32")
                extended_bytes.append(ext_name)
            
            # Shift and combine bytes (little-endian)
            accumulator = f"%{self.function_counter}"
            self.function_counter += 1
            ops.append(self.indent() + accumulator + " = arith.constant 0 : i32")
            
            for i, ext_name in enumerate(extended_bytes):
                shift_name = f"%{self.function_counter}"
                self.function_counter += 1
                ops.append(self.indent() + shift_name + " = arith.constant " + str(i * 8) + " : i32")
                
                shifted_name = f"%{self.function_counter}"
                self.function_counter += 1
                ops.append(self.indent() + shifted_name + " = arith.shli " + ext_name + ", " + shift_name + " : i32")
                
                prev_accumulator = accumulator
                accumulator = f"%{self.function_counter}"
                self.function_counter += 1
                ops.append(self.indent() + accumulator + " = arith.ori " + prev_accumulator + ", " + shifted_name + " : i32")
            
            combined_name = accumulator
            # Bitcast from i32 to f32
            final_name = f"%{self.function_counter}"
            self.function_counter += 1
            ops.append(self.indent() + final_name + " = arith.bitcast " + combined_name + " : i32 to f32")
            self._ssa_types[final_name] = "f32"
            return final_name, ops
            
        elif field_type.name in ['i32', 'u32']:
            # Load i32 from memory (4 bytes, little-endian)
            ops.append(self.indent() + "// Load " + field_access.field + " (i32) at offset " + str(offset))
            
            # Load 4 bytes and combine
            loaded_bytes = []
            for i in range(4):
                byte_offset = offset + i
                
                offset_ssa = f"%{self.function_counter}"
                self.function_counter += 1
                ops.append(f"{self.indent()}{offset_ssa} = arith.constant {byte_offset} : index")
                
                byte_name = f"%{self.function_counter}"
                self.function_counter += 1
                ops.append(f"{self.indent()}{byte_name} = memref.load {obj_ssa}[{offset_ssa}] : memref<{total_size}xi8>")
                loaded_bytes.append(byte_name)
            
            # Extend each byte to i32
            extended_bytes = []
            for byte_name in loaded_bytes:
                ext_name = f"%{self.function_counter}"
                self.function_counter += 1
                ops.append(f"{self.indent()}{ext_name} = arith.extsi {byte_name} : i8 to i32")
                extended_bytes.append(ext_name)
            
            # Shift and combine bytes (little-endian)
            accumulator = f"%{self.function_counter}"
            self.function_counter += 1
            ops.append(self.indent() + accumulator + " = arith.constant 0 : i32")
            
            for i, ext_name in enumerate(extended_bytes):
                shift_name = f"%{self.function_counter}"
                self.function_counter += 1
                ops.append(self.indent() + shift_name + " = arith.constant " + str(i * 8) + " : i32")
                
                shifted_name = f"%{self.function_counter}"
                self.function_counter += 1
                ops.append(self.indent() + shifted_name + " = arith.shli " + ext_name + ", " + shift_name + " : i32")
                
                prev_accumulator = accumulator
                accumulator = f"%{self.function_counter}"
                self.function_counter += 1
                ops.append(self.indent() + accumulator + " = arith.ori " + prev_accumulator + ", " + shifted_name + " : i32")
            self._ssa_types[accumulator] = "i32"
            return accumulator, ops
            
        elif field_type.name in ['i8', 'u8', 'bool']:
            # Load single byte
            ops.append(f"{self.indent()}// Load {field_access.field} ({field_type.name}) at offset {offset}")
            byte_name = f"%{self.function_counter}"
            self.function_counter += 1
            ops.append(f"{self.indent()}{byte_name} = memref.load {obj_ssa}[{offset}] : memref<{total_size}xi8>")

            # Extend to i32 if needed
            if field_type.name in ['u8', 'bool']:
                ext_name = f"%{self.function_counter}"
                self.function_counter += 1
                ops.append(f"{self.indent()}{ext_name} = arith.extsi {byte_name} : i8 to i32")
                self._ssa_types[ext_name] = "i32"
                return ext_name, ops
            else:
                # For i8, sign extend
                ext_name = f"%{self.function_counter}"
                self.function_counter += 1
                ops.append(f"{self.indent()}{ext_name} = arith.extsi {byte_name} : i8 to i32")
                self._ssa_types[ext_name] = "i32"
                return ext_name, ops

        else:
            # Generic fallback for f64, i64, pointers, and other 8-byte types
            # Determine byte width from type
            type_name = field_type.name
            is_pointer = getattr(field_type, 'is_pointer', False) or type_name.startswith('ptr')
            if type_name in ['f64'] or is_pointer or type_name in ['i64', 'u64']:
                num_bytes = 8
                int_type = 'i64'
            else:
                # Unknown type — treat as i32 fallback
                num_bytes = 4
                int_type = 'i32'

            ops.append(f"{self.indent()}// Load {field_access.field} ({type_name}) at offset {offset}")

            loaded_bytes = []
            for i in range(num_bytes):
                byte_offset = offset + i
                offset_ssa = f"%{self.function_counter}"
                self.function_counter += 1
                ops.append(f"{self.indent()}{offset_ssa} = arith.constant {byte_offset} : index")
                byte_name = f"%{self.function_counter}"
                self.function_counter += 1
                ops.append(f"{self.indent()}{byte_name} = memref.load {obj_ssa}[{offset_ssa}] : memref<{total_size}xi8>")
                loaded_bytes.append(byte_name)

            extended_bytes = []
            for byte_name in loaded_bytes:
                ext_name = f"%{self.function_counter}"
                self.function_counter += 1
                ops.append(f"{self.indent()}{ext_name} = arith.extui {byte_name} : i8 to {int_type}")
                extended_bytes.append(ext_name)

            accumulator = f"%{self.function_counter}"
            self.function_counter += 1
            ops.append(f"{self.indent()}{accumulator} = arith.constant 0 : {int_type}")

            for i, ext_name in enumerate(extended_bytes):
                shift_name = f"%{self.function_counter}"
                self.function_counter += 1
                ops.append(f"{self.indent()}{shift_name} = arith.constant {i * 8} : {int_type}")
                shifted_name = f"%{self.function_counter}"
                self.function_counter += 1
                ops.append(f"{self.indent()}{shifted_name} = arith.shli {ext_name}, {shift_name} : {int_type}")
                prev_accumulator = accumulator
                accumulator = f"%{self.function_counter}"
                self.function_counter += 1
                ops.append(f"{self.indent()}{accumulator} = arith.ori {prev_accumulator}, {shifted_name} : {int_type}")

            if type_name == 'f64':
                final_name = f"%{self.function_counter}"
                self.function_counter += 1
                ops.append(f"{self.indent()}{final_name} = arith.bitcast {accumulator} : i64 to f64")
                self._ssa_types[final_name] = "f64"
                return final_name, ops
            else:
                self._ssa_types[accumulator] = int_type
                return accumulator, ops
    
    def _get_ssa_type(self, ssa_name: str, ops: list = None) -> str:
        """Infer the MLIR type of an SSA value from its definition in ops."""
        if ssa_name in self._ssa_types:
            return self._ssa_types[ssa_name]
        # Check function arguments from symbol table
        if ssa_name.startswith('%arg'):
            info = self.symbol_table.get(ssa_name, {})
            if isinstance(info, dict) and 'mlir_type' in info:
                return info['mlir_type']
        # Default: f32 for unknown
        return 'f32'

    def _infer_ssa_type_from_ops(self, ssa_name: str, ops: list) -> str:
        """Scan ops list backwards to find the type of an SSA definition."""
        import re
        # Check function arguments via symbol table
        if ssa_name.startswith('%arg'):
            for name, info in self.symbol_table.items():
                if isinstance(info, dict) and info.get('ssa_name') == ssa_name:
                    return info.get('mlir_type', 'f32')
        # Scan generated ops
        for op in reversed(ops):
            if ssa_name in op and '=' in op:
                # Match "to TYPE" at end (for casts like arith.extf ... : f32 to f64)
                m = re.search(r'to (f64|f32|i64|i32|i1|i8)\s*$', op)
                if m:
                    return m.group(1)
                # Match trailing type annotation like ": f64", ": i32", ": f32"
                m = re.search(r': (f64|f32|i64|i32|i1|i8|index)\s*$', op)
                if m:
                    return m.group(1)
                # Match memref return type
                if 'memref' in op:
                    return 'memref'
                break
        return 'f32'

    def _determine_struct_type(self, expr):
        """Determine the struct type of an expression"""
        if hasattr(expr, 'name'):
            # This is a variable, find its declaration
            var_type = self._find_variable_type(expr.name)
            return var_type
        elif isinstance(expr, FieldAccess):
            # This is a field access, get the field type
            return self._determine_field_type(expr)
        return None
    
    def _determine_field_type(self, field_access):
        """Determine the type of a field access by walking the struct hierarchy"""
        # Start with the base object
        current_type = None
        
        # If the object is a variable, get its type from the AST
        if hasattr(field_access.object, 'name'):
            # This is a variable, find its declaration
            current_type = self._find_variable_type(field_access.object.name)
        elif isinstance(field_access.object, FieldAccess):
            # This is a nested field access, recurse
            current_type = self._determine_field_type(field_access.object)
        
        # Walk through the fields
        if current_type and current_type.name in self.struct_layouts:
            layout = self.struct_layouts[current_type.name]
            if field_access.field in layout:
                return layout[field_access.field]['type']
        
        return None
    
    def _find_variable_type(self, var_name):
        """Find the type of a variable by looking through declarations"""
        # First check symbol table (fast, handles locals)
        if var_name in self.symbol_table:
            var_info = self.symbol_table[var_name]
            if 'flow_type' in var_info:
                return var_info['flow_type']
            # Fallback: try to reconstruct from mlir_type (imperfect)
            return Type(var_info.get('mlir_type', 'i32'))

        # Fallback to scanning declarations (globals)
        for decl in self.declarations:
            if hasattr(decl, 'body') and hasattr(decl, 'name'):  # Function
                pass # Don't scan function bodies from outside!
            elif hasattr(decl, 'name') and decl.name == var_name:  # Global?
                # Does FLOW have globals? Not implemented here.
                pass
        return None
    
    def generate_struct_literal(self, struct_literal: StructLiteral) -> tuple[str, List[str]]:
        """Generate struct literal with actual memory allocation and field storage"""
        struct_name = struct_literal.struct_name

        llvm_struct = self._struct_llvm_type(struct_name)
        if llvm_struct:
            decl = self._get_struct_decl(struct_name)
            if not decl:
                ssa_name = f"%{self.function_counter}"
                self.function_counter += 1
                return ssa_name, [f"{self.indent()}{ssa_name} = llvm.mlir.undef : {llvm_struct}"]

            # Map provided fields for lookup
            provided = {name: value for name, value in struct_literal.fields}
            ops: List[str] = []
            agg_name = f"%{self.function_counter}"
            self.function_counter += 1
            ops.append(f"{self.indent()}{agg_name} = llvm.mlir.undef : {llvm_struct}")

            for idx, field in enumerate(decl.fields):
                field_type = self.flow_type_to_mlir(field.type)
                if field.name in provided:
                    val_ssa, val_ops = self.generate_expression(provided[field.name])
                    ops.extend(val_ops)
                    val_type = self.get_expression_type(provided[field.name])
                    if val_type != field_type:
                        val_ssa, cast_ops = self._emit_cast(val_ssa, val_type, field_type)
                        ops.extend(cast_ops)
                    if self._is_tensor_struct(field_type):
                        val_ssa, mat_ops = self._materialize_tensor_for_call(
                            val_ssa, field_type, ""
                        )
                        ops.extend(mat_ops)
                else:
                    val_ssa, zero_ops = self._zero_value_for_mlir_type(field_type)
                    ops.extend(zero_ops)

                next_agg = f"%{self.function_counter}"
                self.function_counter += 1
                ops.append(f"{self.indent()}{next_agg} = llvm.insertvalue {val_ssa}, {agg_name}[{idx}] : {llvm_struct}")
                agg_name = next_agg

            self._ssa_types[agg_name] = llvm_struct
            return agg_name, ops
        
        if struct_name not in self.struct_layouts:
            # Fallback for unknown structs
            ssa_name = f"%{self.function_counter}"
            self.function_counter += 1
            return ssa_name, [f"{self.indent()}{ssa_name} = arith.constant 0 : i32"]
        
        # Get struct layout
        layout = self.struct_layouts[struct_name]
        total_size = sum(field['size'] for field in layout.values())
        
        ops = []
        
        # Allocate memory for struct as byte array
        alloc_name = f"%{self.function_counter}"
        self.function_counter += 1
        ops.append(f"{self.indent()}{alloc_name} = memref.alloc() : memref<{total_size}xi8>")
        
        # Store field at correct offset with proper byte manipulation
        for field_name, field_value in struct_literal.fields:
            if field_name in layout:
                field_info = layout[field_name]
                offset = field_info['offset']
                field_type = field_info['type']
                
                # Generate field value
                value_ssa, value_ops = self.generate_expression(field_value)
                ops.extend(value_ops)
                
                # Store field at correct offset with proper byte manipulation
                if field_type.name in ['i32', 'u32']:
                    # Store i32 as 4 bytes (little-endian)
                    for i in range(4):
                        byte_offset = offset + i
                        # Extract ith byte: (value >> (i * 8)) & 0xFF
                        shift_name = f"%{self.function_counter}"
                        self.function_counter += 1
                        ops.append(f"{self.indent()}{shift_name} = arith.constant {i * 8} : i32")
                        
                        shr_name = f"%{self.function_counter}"
                        self.function_counter += 1
                        ops.append(f"{self.indent()}{shr_name} = arith.shrsi {value_ssa}, {shift_name} : i32")
                        
                        # Use arith.andi with constant 255
                        and_name = f"%{self.function_counter}"
                        self.function_counter += 1
                        mask_name = f"%{self.function_counter}"
                        self.function_counter += 1
                        ops.append(f"{self.indent()}{mask_name} = arith.constant 255 : i32")
                        ops.append(f"{self.indent()}{and_name} = arith.andi {shr_name}, {mask_name} : i32")
                        
                        # Cast to i8
                        byte_name = f"%{self.function_counter}"
                        self.function_counter += 1
                        ops.append(f"{self.indent()}{byte_name} = arith.trunci {and_name} : i32 to i8")
                        
                        # Store byte
                        idx_name = f"%{self.function_counter}"
                        self.function_counter += 1
                        ops.append(f"{self.indent()}{idx_name} = arith.constant {byte_offset} : index")
                        ops.append(f"{self.indent()}memref.store {byte_name}, {alloc_name}[{idx_name}] : memref<{total_size}xi8>")
                        
                elif field_type.name == 'f32':
                    # Store f32 as 4 bytes (bitcast to i32 first)
                    bitcast_name = f"%{self.function_counter}"
                    self.function_counter += 1
                    ops.append(f"{self.indent()}{bitcast_name} = arith.bitcast {value_ssa} : f32 to i32")
                    
                    # Extract bytes like i32
                    for i in range(4):
                        byte_offset = offset + i
                        shift_name = f"%{self.function_counter}"
                        self.function_counter += 1
                        ops.append(f"{self.indent()}{shift_name} = arith.constant {i * 8} : i32")
                        
                        shr_name = f"%{self.function_counter}"
                        self.function_counter += 1
                        ops.append(f"{self.indent()}{shr_name} = arith.shrsi {bitcast_name}, {shift_name} : i32")
                        
                        # Use arith.andi with constant 255
                        and_name = f"%{self.function_counter}"
                        self.function_counter += 1
                        mask_name = f"%{self.function_counter}"
                        self.function_counter += 1
                        ops.append(f"{self.indent()}{mask_name} = arith.constant 255 : i32")
                        ops.append(f"{self.indent()}{and_name} = arith.andi {shr_name}, {mask_name} : i32")
                        
                        # Cast to i8
                        byte_name = f"%{self.function_counter}"
                        self.function_counter += 1
                        ops.append(f"{self.indent()}{byte_name} = arith.trunci {and_name} : i32 to i8")
                        
                        # Store byte
                        idx_name = f"%{self.function_counter}"
                        self.function_counter += 1
                        ops.append(f"{self.indent()}{idx_name} = arith.constant {byte_offset} : index")
                        ops.append(f"{self.indent()}memref.store {byte_name}, {alloc_name}[{idx_name}] : memref<{total_size}xi8>")
                        
                elif field_type.name in ['i8', 'u8', 'bool']:
                    # Store single byte
                    cast_name = f"%{self.function_counter}"
                    self.function_counter += 1
                    if field_type.name in ['u8', 'bool']:
                        ops.append(f"{self.indent()}{cast_name} = arith.trunci {value_ssa} : i32 to i8")
                    else:
                        ops.append(f"{self.indent()}{cast_name} = arith.trunci {value_ssa} : i32 to i8")
                    
                    ops.append(f"{self.indent()}memref.store {cast_name}, {alloc_name}[{offset}] : memref<{total_size}xi8>")
                    
                elif field_type.name == 'f64':
                    # Store f64 as 8 bytes (bitcast to i64 first)
                    # Ensure value is f64 (may arrive as f32 from literal gen)
                    val_type = self._infer_ssa_type_from_ops(value_ssa, ops)
                    if val_type != 'f64':
                        ext_name = f"%{self.function_counter}"
                        self.function_counter += 1
                        if val_type == 'f32':
                            ops.append(f"{self.indent()}{ext_name} = arith.extf {value_ssa} : f32 to f64")
                        elif val_type in ['i32', 'i64']:
                            ops.append(f"{self.indent()}{ext_name} = arith.sitofp {value_ssa} : {val_type} to f64")
                        else:
                            ops.append(f"{self.indent()}{ext_name} = arith.extf {value_ssa} : f32 to f64")
                        value_ssa = ext_name
                    bitcast_name = f"%{self.function_counter}"
                    self.function_counter += 1
                    ops.append(f"{self.indent()}{bitcast_name} = arith.bitcast {value_ssa} : f64 to i64")
                    for i in range(8):
                        byte_offset = offset + i
                        shift_name = f"%{self.function_counter}"
                        self.function_counter += 1
                        ops.append(f"{self.indent()}{shift_name} = arith.constant {i * 8} : i64")
                        shr_name = f"%{self.function_counter}"
                        self.function_counter += 1
                        ops.append(f"{self.indent()}{shr_name} = arith.shrsi {bitcast_name}, {shift_name} : i64")
                        mask_name = f"%{self.function_counter}"
                        self.function_counter += 1
                        ops.append(f"{self.indent()}{mask_name} = arith.constant 255 : i64")
                        and_name = f"%{self.function_counter}"
                        self.function_counter += 1
                        ops.append(f"{self.indent()}{and_name} = arith.andi {shr_name}, {mask_name} : i64")
                        byte_name = f"%{self.function_counter}"
                        self.function_counter += 1
                        ops.append(f"{self.indent()}{byte_name} = arith.trunci {and_name} : i64 to i8")
                        idx_name = f"%{self.function_counter}"
                        self.function_counter += 1
                        ops.append(f"{self.indent()}{idx_name} = arith.constant {byte_offset} : index")
                        ops.append(f"{self.indent()}memref.store {byte_name}, {alloc_name}[{idx_name}] : memref<{total_size}xi8>")

                elif field_type.name in ['i64', 'u64'] or getattr(field_type, 'is_pointer', False) or field_type.name.startswith('ptr'):
                    # Store i64/pointer as 8 bytes (little-endian)
                    src_name = value_ssa
                    for i in range(8):
                        byte_offset = offset + i
                        shift_name = f"%{self.function_counter}"
                        self.function_counter += 1
                        ops.append(f"{self.indent()}{shift_name} = arith.constant {i * 8} : i64")
                        shr_name = f"%{self.function_counter}"
                        self.function_counter += 1
                        ops.append(f"{self.indent()}{shr_name} = arith.shrsi {src_name}, {shift_name} : i64")
                        mask_name = f"%{self.function_counter}"
                        self.function_counter += 1
                        ops.append(f"{self.indent()}{mask_name} = arith.constant 255 : i64")
                        and_name = f"%{self.function_counter}"
                        self.function_counter += 1
                        ops.append(f"{self.indent()}{and_name} = arith.andi {shr_name}, {mask_name} : i64")
                        byte_name = f"%{self.function_counter}"
                        self.function_counter += 1
                        ops.append(f"{self.indent()}{byte_name} = arith.trunci {and_name} : i64 to i8")
                        idx_name = f"%{self.function_counter}"
                        self.function_counter += 1
                        ops.append(f"{self.indent()}{idx_name} = arith.constant {byte_offset} : index")
                        ops.append(f"{self.indent()}memref.store {byte_name}, {alloc_name}[{idx_name}] : memref<{total_size}xi8>")

                else:
                    # Unknown type - emit comment
                    ops.append(f"{self.indent()}// Store {field_name} ({field_type.name}) at offset {offset}")
                    ops.append(f"{self.indent()}// Value: {value_ssa}")
        
        # Return the static-typed allocation (field access casts locally as needed)
        return alloc_name, ops
    
    def generate_function_call(self, func_call: FunctionCall) -> tuple[str, List[str]]:
        # Handle array<T>(size) constructor specially
        if func_call.name.startswith('array<') and func_call.name.endswith('>'):
            # Extract element type from array<type>
            elem_type = func_call.name[6:-1]  # Remove 'array<' and '>'
            
            if len(func_call.arguments) == 1:
                # Array with specified size: array<i32>(10)
                size_ssa, size_ops = self.generate_expression(func_call.arguments[0])
                ops = list(size_ops)
                
                # Cast size to index if needed
                size_type = self.get_expression_type(func_call.arguments[0])
                if size_type != 'index':
                    size_cast = f"%{self.function_counter}"
                    self.function_counter += 1
                    ops.append(f"{self.indent()}{size_cast} = arith.index_cast {size_ssa} : {size_type} to index")
                    size_ssa = size_cast
                
                # Allocate memref
                array_ssa = f"%{self.function_counter}"
                self.function_counter += 1
                ops.append(f"{self.indent()}{array_ssa} = memref.alloc({size_ssa}) : memref<?x{elem_type}>")
                self._ssa_types[array_ssa] = f"memref<?x{elem_type}>"
                return array_ssa, ops
            else:
                # Array with initial values: array<i32>(1, 2, 3)
                element_values = []
                ops = []
                
                for arg in func_call.arguments:
                    val, val_ops = self.generate_expression(arg)
                    ops.extend(val_ops)
                    element_values.append(val)
                
                size = len(element_values)
                array_ssa = f"%{self.function_counter}"
                self.function_counter += 1
                ops.append(f"{self.indent()}{array_ssa} = memref.alloc() : memref<{size}x{elem_type}>")
                self._ssa_types[array_ssa] = f"memref<{size}x{elem_type}>"
                
                # Store each element
                for i, element_value in enumerate(element_values):
                    index_ssa = f"%{self.function_counter}"
                    self.function_counter += 1
                    ops.append(f"{self.indent()}{index_ssa} = arith.constant {i} : index")
                    ops.append(f"{self.indent()}memref.store {element_value}, {array_ssa}[{index_ssa}] : memref<{size}x{elem_type}>")
                
                return array_ssa, ops
        
        # Handle print/println intrinsics specially
        if func_call.name in ('print', 'println'):
            return self.generate_print_call(func_call, newline=(func_call.name == 'println'))

        # Handle printf intrinsic specially (format string + varargs)
        if func_call.name == 'printf':
            return self.generate_printf_call(func_call)

        ssa_name = f"%{self.function_counter}"
        self.function_counter += 1

        callee = f"@{func_call.name}"
        if func_call.name in self.symbol_table:
            func_info = self.symbol_table[func_call.name]
            callee = func_info['mlir_name']

        # Resolve signature before arg codegen so tensor-returning callees can
        # evaluate arguments last-to-first (keeps early tensor args off clobbered stack).
        expected_arg_types = []
        if func_call.name in self.symbol_table:
            func_info = self.symbol_table[func_call.name]
            for param in func_info.get('parameters', []):
                expected_arg_types.append(self.flow_type_to_mlir(param.type))
        else:
            expected_arg_types = [self.get_expression_type(a) for a in func_call.arguments]

        ret_type = 'i32'
        if func_call.name in self.symbol_table:
            ret_type = self.flow_type_to_mlir(self.symbol_table[func_call.name]['return_type'])
        callee_returns_tensor = self._is_tensor_struct(ret_type)
        callee_returns_composite = (
            ret_type.startswith("!llvm.struct") and not callee_returns_tensor
        )

        arg_indices = list(range(len(func_call.arguments)))
        if callee_returns_tensor or callee_returns_composite:
            arg_indices = list(reversed(arg_indices))

        arg_values: List[Optional[str]] = [None] * len(func_call.arguments)
        ops: List[str] = []
        for i in arg_indices:
            arg = func_call.arguments[i]
            if isinstance(arg, Literal) and arg.type.name == 'string':
                str_val = arg.value
                if str_val not in self.string_constants:
                    global_name = f"str_{self.string_counter}"
                    self.string_counter += 1
                    self.string_constants[str_val] = global_name
                else:
                    global_name = self.string_constants[str_val]

                arg_ssa = f"%{self.function_counter}"
                self.function_counter += 1
                ops.append(f"{self.indent()}{arg_ssa} = llvm.mlir.addressof @{global_name} : !llvm.ptr")
                arg_values[i] = arg_ssa
            else:
                v, vops = self.generate_expression(arg)
                ops.extend(vops)
                arg_values[i] = v

        resolved_arg_values: List[str] = [
            arg_values[i] for i in range(len(func_call.arguments))
        ]

        prepared_args = list(resolved_arg_values)
        for i, (arg_val, expected_type) in enumerate(zip(prepared_args, expected_arg_types)):
            if expected_type.startswith("!llvm.struct") and (
                not self._is_tensor_struct(expected_type)
            ) and (callee_returns_tensor or callee_returns_composite):
                stable, mat_ops = self._materialize_struct_value(arg_val, expected_type)
                ops.extend(mat_ops)
                prepared_args[i] = stable

        tensor_stabilize_order = (
            reversed(range(len(prepared_args)))
            if callee_returns_tensor or callee_returns_composite
            else range(len(prepared_args))
        )
        for i in tensor_stabilize_order:
            expected_type = expected_arg_types[i]
            if self._is_tensor_struct(expected_type):
                stable, mat_ops = self._stable_tensor_for_call(
                    prepared_args[i],
                    expected_type,
                    func_call.name,
                    callee_returns_tensor=callee_returns_tensor,
                    callee_returns_composite=callee_returns_composite,
                    arg_expr=func_call.arguments[i],
                )
                ops.extend(mat_ops)
                prepared_args[i] = stable

        # Cast arguments if needed (width mismatches, index/i32, memref shapes)
        cast_args = []
        for i, (arg_val, expected_type) in enumerate(zip(prepared_args, expected_arg_types)):
            actual_type = self._ssa_types.get(arg_val) or self.get_expression_type(
                func_call.arguments[i]
            )
            if actual_type == expected_type:
                cast_args.append(arg_val)
            elif (actual_type, expected_type) in (('index', 'i32'), ('i32', 'index')):
                cast_arg = f"%{self.function_counter}"
                self.function_counter += 1
                ops.append(f"{self.indent()}{cast_arg} = arith.index_cast {arg_val} : {actual_type} to {expected_type}")
                cast_args.append(cast_arg)
            elif 'memref<' in actual_type and 'memref<' in expected_type:
                cast_arg = f"%{self.function_counter}"
                self.function_counter += 1
                ops.append(f"{self.indent()}{cast_arg} = memref.cast {arg_val} : {actual_type} to {expected_type}")
                cast_args.append(cast_arg)
            elif actual_type != expected_type:
                cast_arg, cast_ops = self._emit_cast(arg_val, actual_type, expected_type)
                ops.extend(cast_ops)
                cast_args.append(cast_arg)
            else:
                cast_args.append(arg_val)
        
        # For void functions, don't assign to SSA value
        if ret_type == '()':
            ops.append(
                f"{self.indent()}func.call {callee}({', '.join(cast_args)}) : ({', '.join(expected_arg_types)}) -> {ret_type}"
            )
            # Return a dummy value for void functions (won't be used)
            return f"%void_{self.function_counter}", ops
        else:
            ops.append(
                f"{self.indent()}{ssa_name} = func.call {callee}({', '.join(cast_args)}) : ({', '.join(expected_arg_types)}) -> {ret_type}"
            )
            self._ssa_types[ssa_name] = ret_type
            if self._is_tensor_struct(ret_type):
                if func_call.name in self._TENSOR_POST_MATERIALIZE_CALLEES:
                    stable, mat_ops = self._materialize_tensor_for_call(
                        ssa_name, ret_type, func_call.name
                    )
                    ops.extend(mat_ops)
                    ssa_name = stable
                    self._ssa_types[ssa_name] = ret_type
                    self._tensor_stable_ssas.add(ssa_name)
                else:
                    self._tensor_call_results.add(ssa_name)
            elif ret_type.startswith("!llvm.struct"):
                ret_name = self._func_call_return_type_name(func_call)
                if ret_name in self._COMPOSITE_FIELD_MATERIALIZE_TYPES:
                    stable, mat_ops = self._materialize_struct_value(ssa_name, ret_type)
                    ops.extend(mat_ops)
                    ssa_name = stable
                    self._ssa_types[ssa_name] = ret_type
                else:
                    self._composite_call_results.add(ssa_name)
            if callee_returns_tensor or callee_returns_composite:
                for i, arg in enumerate(func_call.arguments):
                    if not isinstance(arg, Variable):
                        continue
                    var_info = self.symbol_table.get(arg.name)
                    if not var_info or "ssa_name" not in var_info:
                        continue
                    expected_type = expected_arg_types[i]
                    mlir_type = var_info.get("mlir_type") or expected_type
                    struct_name = self._flow_type_name(var_info.get("flow_type"))
                    if self._is_tensor_struct(expected_type):
                        # Refresh from the call-site copy, not the variable SSA that may
                        # share the callee's aggregate return stack slot.
                        fresh, mat_ops = self._materialize_tensor_for_call(
                            cast_args[i], mlir_type, ""
                        )
                        ops.extend(mat_ops)
                        var_info["ssa_name"] = fresh
                        self._ssa_types[fresh] = mlir_type
                        self._tensor_stable_ssas.add(fresh)
                        ops.extend(self._store_aggregate_var(var_info, fresh))
                    elif (
                        expected_type.startswith("!llvm.struct")
                        and struct_name in self._COMPOSITE_FIELD_MATERIALIZE_TYPES
                    ):
                        fresh, mat_ops = self._materialize_struct_value(
                            cast_args[i], mlir_type
                        )
                        ops.extend(mat_ops)
                        var_info["ssa_name"] = fresh
                        self._ssa_types[fresh] = mlir_type
                        ops.extend(self._store_aggregate_var(var_info, fresh))
            return ssa_name, ops
    
    def generate_print_call(self, func_call: FunctionCall, *, newline: bool = False) -> tuple[str, List[str]]:
        """Generate MLIR for print() intrinsic - supports strings and numeric values."""
        self.needs_printf = True
        ops: List[str] = []
        
        for arg in func_call.arguments:
            if isinstance(arg, Literal) and arg.type.name == 'string':
                # String literal - create global constant and get pointer
                str_val = arg.value
                if newline:
                    if str_val.startswith('"') and str_val.endswith('"'):
                        str_val = f'{str_val[:-1]}\\n"'
                    else:
                        str_val = f'{str_val}\\n'
                if str_val not in self.string_constants:
                    global_name = f"str_{self.string_counter}"
                    self.string_counter += 1
                    self.string_constants[str_val] = global_name
                else:
                    global_name = self.string_constants[str_val]
                
                # Get pointer to string constant
                ptr_ssa = f"%{self.function_counter}"
                self.function_counter += 1
                ops.append(f"{self.indent()}{ptr_ssa} = llvm.mlir.addressof @{global_name} : !llvm.ptr")
                
                # Call printf with string
                result_ssa = f"%{self.function_counter}"
                self.function_counter += 1
                ops.append(f"{self.indent()}{result_ssa} = llvm.call @printf({ptr_ssa}) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32")
            elif isinstance(arg, Variable) and arg.name in self.symbol_table:
                var_info = self.symbol_table[arg.name]
                if 'flow_type' in var_info and var_info['flow_type'].name == 'string':
                    # String variable - just print it directly
                    arg_result = self.generate_expression(arg)
                    if not arg_result:
                        empty_str = ""
                        if empty_str not in self.string_constants:
                            global_name = f"str_{self.string_counter}"
                            self.string_counter += 1
                            self.string_constants[empty_str] = global_name
                        else:
                            global_name = self.string_constants[empty_str]
                        arg_ssa = f"%{self.function_counter}"
                        self.function_counter += 1
                        arg_ops = [f"{self.indent()}{arg_ssa} = llvm.mlir.addressof @{global_name} : !llvm.ptr"]
                    else:
                        arg_ssa, arg_ops = arg_result
                    ops.extend(arg_ops)
                    
                    result_ssa = f"%{self.function_counter}"
                    self.function_counter += 1
                    ops.append(f"{self.indent()}{result_ssa} = llvm.call @printf({arg_ssa}) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32")
                else:
                    # Numeric variable
                    arg_type = self.get_expression_type(arg)
                    arg_result = self.generate_expression(arg)
                    if not arg_result:
                        arg_ssa = f"%{self.function_counter}"
                        self.function_counter += 1
                        arg_ops = [f"{self.indent()}{arg_ssa} = arith.constant 0 : i32"]
                    else:
                        arg_ssa, arg_ops = arg_result
                    ops.extend(arg_ops)
                    
                    # Determine format string based on type
                    if arg_type in ['f32', 'f64']:
                        fmt_str = '"%f\\n"'
                    else:
                        fmt_str = '"%d\\n"'
                    
                    if fmt_str not in self.string_constants:
                        global_name = f"str_{self.string_counter}"
                        self.string_counter += 1
                        self.string_constants[fmt_str] = global_name
                    else:
                        global_name = self.string_constants[fmt_str]
                    
                    # Get pointer to format string
                    fmt_ptr = f"%{self.function_counter}"
                    self.function_counter += 1
                    ops.append(f"{self.indent()}{fmt_ptr} = llvm.mlir.addressof @{global_name} : !llvm.ptr")
                    
                    cast_ssa, cast_type, cast_ops = self._cast_for_printf(arg_ssa, arg_type)
                    ops.extend(cast_ops)
                    arg_ssa = cast_ssa
                    arg_type = cast_type

                    # Call printf
                    result_ssa = f"%{self.function_counter}"
                    self.function_counter += 1
                    ops.append(f"{self.indent()}{result_ssa} = llvm.call @printf({fmt_ptr}, {arg_ssa}) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, {arg_type}) -> i32")
            else:
                # Other expression types - treat as numeric
                arg_type = self.get_expression_type(arg)
                arg_result = self.generate_expression(arg)
                if not arg_result:
                    arg_ssa = f"%{self.function_counter}"
                    self.function_counter += 1
                    arg_ops = [f"{self.indent()}{arg_ssa} = arith.constant 0 : i32"]
                else:
                    arg_ssa, arg_ops = arg_result
                ops.extend(arg_ops)
                
                # Determine format string based on type
                if arg_type in ['f32', 'f64']:
                    fmt_str = '"%f\\n"'
                else:
                    fmt_str = '"%d\\n"'
                
                if fmt_str not in self.string_constants:
                    global_name = f"str_{self.string_counter}"
                    self.string_counter += 1
                    self.string_constants[fmt_str] = global_name
                else:
                    global_name = self.string_constants[fmt_str]
                
                # Get pointer to format string
                fmt_ptr = f"%{self.function_counter}"
                self.function_counter += 1
                ops.append(f"{self.indent()}{fmt_ptr} = llvm.mlir.addressof @{global_name} : !llvm.ptr")
                
                cast_ssa, cast_type, cast_ops = self._cast_for_printf(arg_ssa, arg_type)
                ops.extend(cast_ops)
                arg_ssa = cast_ssa
                arg_type = cast_type

                # Call printf
                result_ssa = f"%{self.function_counter}"
                self.function_counter += 1
                ops.append(f"{self.indent()}{result_ssa} = llvm.call @printf({fmt_ptr}, {arg_ssa}) vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, {arg_type}) -> i32")
        
        # Return dummy value (print returns void conceptually)
        dummy_ssa = f"%{self.function_counter}"
        self.function_counter += 1
        ops.append(f"{self.indent()}{dummy_ssa} = arith.constant 0 : i32")
        return dummy_ssa, ops

    def generate_printf_call(self, func_call: FunctionCall) -> tuple[str, List[str]]:
        """Generate MLIR for printf() intrinsic.

        Contract:
        - First argument must be a string literal format.
        - Remaining args are numeric (i32/f32/f64) and passed as varargs.
        - Returns i32 (printf return).
        """
        self.needs_printf = True
        ops: List[str] = []

        if not func_call.arguments:
            # printf() with no args: return 0
            dummy_ssa = f"%{self.function_counter}"
            self.function_counter += 1
            ops.append(f"{self.indent()}{dummy_ssa} = arith.constant 0 : i32")
            return dummy_ssa, ops

        fmt = func_call.arguments[0]
        if not (isinstance(fmt, Literal) and fmt.type.name == 'string'):
            # Fallback: best-effort print of first arg
            return self.generate_print_call(FunctionCall('print', [fmt]))

        fmt_str = fmt.value
        if fmt_str not in self.string_constants:
            global_name = f"str_{self.string_counter}"
            self.string_counter += 1
            self.string_constants[fmt_str] = global_name
        else:
            global_name = self.string_constants[fmt_str]

        fmt_ptr = f"%{self.function_counter}"
        self.function_counter += 1
        ops.append(f"{self.indent()}{fmt_ptr} = llvm.mlir.addressof @{global_name} : !llvm.ptr")

        var_ssas: List[str] = []
        var_types: List[str] = []
        for arg in func_call.arguments[1:]:
            arg_ssa, arg_ops = self.generate_expression(arg)
            ops.extend(arg_ops)
            
            # Get the actual type from the generated SSA value
            # For string literals and variables, the type should be !llvm.ptr
            if isinstance(arg, Literal) and arg.type.name == 'string':
                arg_type = '!llvm.ptr'
            elif isinstance(arg, Variable) and arg.name in self.symbol_table:
                var_info = self.symbol_table[arg.name]
                if 'flow_type' in var_info and var_info['flow_type'].name == 'string':
                    arg_type = '!llvm.ptr'
                else:
                    arg_type = self.get_expression_type(arg)
            else:
                arg_type = self.get_expression_type(arg)

            arg_ssa, arg_type, cast_ops = self._cast_for_printf(arg_ssa, arg_type)
            ops.extend(cast_ops)

            var_ssas.append(arg_ssa)
            var_types.append(arg_type)

        result_ssa = f"%{self.function_counter}"
        self.function_counter += 1

        if var_ssas:
            ops.append(
                f"{self.indent()}{result_ssa} = llvm.call @printf({fmt_ptr}, {', '.join(var_ssas)}) "
                f"vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr, {', '.join(var_types)}) -> i32"
            )
        else:
            ops.append(
                f"{self.indent()}{result_ssa} = llvm.call @printf({fmt_ptr}) "
                f"vararg(!llvm.func<i32 (ptr, ...)>) : (!llvm.ptr) -> i32"
            )

        return result_ssa, ops

    def generate_effect_call(self, effect_call: EffectCall) -> tuple[str, List[str]]:
        handler = self._effect_handler_stack[-1].get(effect_call.effect_name)
        if effect_call.effect_name == 'Log' and effect_call.operation in ('emit', 'debug'):
            if handler == 'ConsoleLogger':
                return self.generate_print_call(FunctionCall('print', effect_call.arguments))
            if handler == 'SilentLogger':
                dummy_ssa = f"%{self.function_counter}"
                self.function_counter += 1
                return dummy_ssa, [f"{self.indent()}{dummy_ssa} = arith.constant 0 : i32"]

        ssa_name = f"%{self.function_counter}"
        self.function_counter += 1
        callee = f"@{effect_call.operation}"
        arg_values: List[str] = []
        ops: List[str] = []
        for arg in effect_call.arguments:
            v, vops = self.generate_expression(arg)
            ops.extend(vops)
            arg_values.append(v)
        arg_types: List[str] = [self.get_expression_type(a) for a in effect_call.arguments]
        ops.append(
            f"{self.indent()}{ssa_name} = func.call {callee}({', '.join(arg_values)}) : ({', '.join(arg_types)}) -> i32"
        )
        return ssa_name, ops

    def generate_method_call(self, method_call: MethodCall) -> tuple[str, List[str]]:
        if isinstance(method_call.object, Variable):
            effect_call = EffectCall(method_call.object.name, method_call.method, method_call.arguments)
            return self.generate_effect_call(effect_call)

        # Desugar to function call with receiver as first argument.
        args = [method_call.object] + method_call.arguments
        return self.generate_function_call(FunctionCall(method_call.method, args))
    
    def generate_array_literal(self, array_literal: ArrayLiteral) -> tuple[str, List[str]]:
        self.function_counter += 1

        element_values: List[str] = []
        ops: List[str] = []
        for element in array_literal.elements:
            v, vops = self.generate_expression(element)
            ops.extend(vops)
            element_values.append(v)

        # Create memref from elements - allocate and store each element
        elem_type = self.get_expression_type(array_literal.elements[0]) if array_literal.elements else 'f32'
        size = len(array_literal.elements)
        
        # Allocate memref
        alloc_ssa = f"%{self.function_counter}"
        self.function_counter += 1
        ops.append(f"{self.indent()}{alloc_ssa} = memref.alloc() : memref<{size}x{elem_type}>")
        
        # Store each element
        for i, element_value in enumerate(element_values):
            index_ssa = f"%{self.function_counter}"
            self.function_counter += 1
            ops.append(f"{self.indent()}{index_ssa} = arith.constant {i} : index")
            ops.append(f"{self.indent()}memref.store {element_value}, {alloc_ssa}[{index_ssa}] : memref<{size}x{elem_type}>")
        
        return alloc_ssa, ops

    def generate_vector_literal(self, vector_literal) -> tuple[str, List[str]]:
        """Generate MLIR for vector literals like <1.0, 2.0, 3.0, 4.0>"""
        ssa_name = f"%{self.function_counter}"
        self.function_counter += 1

        element_values: List[str] = []
        ops: List[str] = []
        
        # Generate all element values
        for element in vector_literal.elements:
            v, vops = self.generate_expression(element)
            ops.extend(vops)
            element_values.append(v)

        # Determine element type and vector size
        if not element_values:
            # Empty vector - create a zero-sized vector
            ops.append(f"{self.indent()}{ssa_name} = arith.constant dense<> : vector<0xf32>")
            return ssa_name, ops

        elem_type = self.get_expression_type(vector_literal.elements[0])
        size = len(element_values)

        # Build vector via insertelement to avoid SSA in dense<> attributes
        vec_ssa = f"%{self.function_counter}"
        self.function_counter += 1
        ops.append(f"{self.indent()}{vec_ssa} = vector.undef : vector<{size}x{elem_type}>")
        current = vec_ssa
        for i, val in enumerate(element_values):
            idx_ssa = f"%{self.function_counter}"
            self.function_counter += 1
            ops.append(f"{self.indent()}{idx_ssa} = arith.constant {i} : index")
            next_vec = f"%{self.function_counter}"
            self.function_counter += 1
            ops.append(f"{self.indent()}{next_vec} = vector.insertelement {val}, {current}[{idx_ssa}] : vector<{size}x{elem_type}>")
            current = next_vec
        ops.append(f"{self.indent()}{ssa_name} = {current} : vector<{size}x{elem_type}>")
        return ssa_name, ops

    def _elem_type_from_array_expr(self, expr: Expression) -> Optional[str]:
        if isinstance(expr, FieldAccess):
            field_type = self._determine_field_type(expr)
            if field_type and (getattr(field_type, 'is_pointer', False) or field_type.name.startswith('ptr')):
                if getattr(field_type, 'element_type', None):
                    return self.flow_type_to_mlir(field_type.element_type)
                if field_type.name.startswith('ptr_'):
                    return field_type.name[4:]
        if isinstance(expr, Variable) and expr.name in self.symbol_table:
            flow_type = self.symbol_table[expr.name].get('flow_type')
            if flow_type and (getattr(flow_type, 'is_pointer', False) or flow_type.name.startswith('ptr')):
                if getattr(flow_type, 'element_type', None):
                    return self.flow_type_to_mlir(flow_type.element_type)
                if flow_type.name.startswith('ptr_'):
                    return flow_type.name[4:]
        return None

    def _is_pointer_array_ssa(self, array_ssa: str, access: ArrayAccess) -> bool:
        if self._ssa_types.get(array_ssa) == '!llvm.ptr':
            return True
        if isinstance(access.array, Variable):
            arr_type = self.symbol_table.get(access.array.name, {}).get('mlir_type', '')
            return arr_type == '!llvm.ptr'
        return self._elem_type_from_array_expr(access.array) is not None

    def _emit_ptr_index_gep(self, ptr_ssa: str, index_ssa: str, index_type: str) -> tuple[str, List[str]]:
        ops: List[str] = []
        if index_type == 'index':
            idx64 = f"%{self.function_counter}"
            self.function_counter += 1
            ops.append(f"{self.indent()}{idx64} = arith.index_cast {index_ssa} : index to i64")
            index_ssa = idx64
        elif index_type != 'i64':
            idx64 = f"%{self.function_counter}"
            self.function_counter += 1
            ext_op = "arith.extui" if index_type.startswith('u') else "arith.extsi"
            ops.append(f"{self.indent()}{idx64} = {ext_op} {index_ssa} : {index_type} to i64")
            index_ssa = idx64

        gep = f"%{self.function_counter}"
        self.function_counter += 1
        ops.append(
            f"{self.indent()}{gep} = llvm.getelementptr {ptr_ssa}[{index_ssa}] "
            f": (!llvm.ptr, i64) -> !llvm.ptr, !llvm.ptr"
        )
        self._ssa_types[gep] = '!llvm.ptr'
        return gep, ops

    def generate_array_access(self, access: ArrayAccess) -> tuple[str, List[str]]:
        """Generate memref.load or llvm.load for array[index] access."""
        ssa_name = f"%{self.function_counter}"
        self.function_counter += 1

        ops: List[str] = []

        array_result = self.generate_expression(access.array)
        if not array_result:
            array_ssa = f"%{self.function_counter}"
            self.function_counter += 1
            array_ops = [f"{self.indent()}{array_ssa} = memref.alloc() : memref<?xi8>"]
        else:
            array_ssa, array_ops = array_result
        ops.extend(array_ops)

        index_result = self.generate_expression(access.index)
        if not index_result:
            index_ssa = f"%{self.function_counter}"
            self.function_counter += 1
            index_ops = [f"{self.indent()}{index_ssa} = arith.constant 0 : i32"]
        else:
            index_ssa, index_ops = index_result
        ops.extend(index_ops)

        index_type = self._ssa_types.get(index_ssa, 'i32')
        if isinstance(access.index, Variable) and access.index.name in self.symbol_table:
            index_type = self.symbol_table[access.index.name].get('mlir_type', index_type)

        if self._is_pointer_array_ssa(array_ssa, access):
            elem_type = self._elem_type_from_array_expr(access.array) or 'f32'
            gep, gep_ops = self._emit_ptr_index_gep(array_ssa, index_ssa, index_type)
            ops.extend(gep_ops)
            ops.append(f"{self.indent()}{ssa_name} = llvm.load {gep} : !llvm.ptr -> {elem_type}")
            self._ssa_types[ssa_name] = elem_type
            return ssa_name, ops

        if index_type == 'index':
            final_index = index_ssa
        else:
            index_cast = f"%{self.function_counter}"
            self.function_counter += 1
            ops.append(f"{self.indent()}{index_cast} = arith.index_cast {index_ssa} : i32 to index")
            final_index = index_cast

        elem_type = 'f32'
        if isinstance(access.array, Variable) and access.array.name in self.symbol_table:
            arr_type = self.symbol_table[access.array.name].get('mlir_type', '')
            if 'i32' in arr_type and 'memref' in arr_type:
                elem_type = 'i32'
            elif 'f64' in arr_type:
                elem_type = 'f64'
            elif 'f32' in arr_type:
                elem_type = 'f32'

        ops.append(f"{self.indent()}{ssa_name} = memref.load {array_ssa}[{final_index}] : memref<?x{elem_type}>")
        self._ssa_types[ssa_name] = elem_type
        return ssa_name, ops
    
    def get_expression_type(self, expr: Expression) -> str:
        if isinstance(expr, Literal):
            return self.flow_type_to_mlir(expr.type)
        elif isinstance(expr, Variable):
            if expr.name in self.symbol_table:
                var_info = self.symbol_table[expr.name]
                if 'mlir_type' in var_info:
                    return var_info['mlir_type']
                if 'flow_type' in var_info:
                    return self.flow_type_to_mlir(var_info['flow_type'])
                return 'i32'
            else:
                return 'i32'  # Default
        elif isinstance(expr, BinaryOperation):
            left_type = self.get_expression_type(expr.left)
            right_type = self.get_expression_type(expr.right)
            if expr.operator in ['==', '!=', '<', '<=', '>', '>=', '&&', 'and', '||', 'or']:
                return 'i1'
            if expr.operator == '+' and (left_type == '!llvm.ptr' or right_type == '!llvm.ptr'):
                return '!llvm.ptr'
            return self._resolve_binary_operand_type(left_type, right_type)
        elif isinstance(expr, UnaryOperation):
            return self.get_expression_type(expr.operand)
        elif isinstance(expr, ArrayLiteral):
            # Return memref type for array literals
            if expr.elements:
                elem_type = self.get_expression_type(expr.elements[0])
                size = len(expr.elements)
                return f"memref<{size}x{elem_type}>"
            return "memref<?xf32>"  # Default
        elif isinstance(expr, FunctionCall):
            if expr.name in self.symbol_table:
                return self.flow_type_to_mlir(self.symbol_table[expr.name]['return_type'])
            else:
                return 'i32'  # Default
        elif isinstance(expr, StructLiteral):
            struct_ty = self._struct_llvm_type(expr.struct_name)
            if struct_ty:
                return struct_ty
            if expr.struct_name in self.struct_layouts:
                total_size = sum(field['size'] for field in self.struct_layouts[expr.struct_name].values())
                return f"memref<{total_size}xi8>"
            return 'i32'
        elif isinstance(expr, ArrayAccess):
            # Get element type from array
            if isinstance(expr.array, Variable) and expr.array.name in self.symbol_table:
                arr_type = self.symbol_table[expr.array.name].get('mlir_type', '')
                if 'f32' in arr_type:
                    return 'f32'
                elif 'f64' in arr_type:
                    return 'f64'
                elif 'i32' in arr_type:
                    return 'i32'
            return 'f32'  # Default for array access
        elif isinstance(expr, CastExpression):
            return self.flow_type_to_mlir(expr.target_type)
        elif isinstance(expr, FieldAccess):
            # Check if this is a nested field access
            if isinstance(expr.object, FieldAccess):
                # For nested field access, we need to check the field type of the parent
                parent_obj_type = self.get_expression_type(expr.object.object)
                if isinstance(parent_obj_type, str):
                    class SimpleType:
                        def __init__(self, name):
                            self.name = name
                    parent_obj_type = SimpleType(parent_obj_type)
                
                if parent_obj_type.name in self.struct_layouts:
                    layout = self.struct_layouts[parent_obj_type.name]
                    if expr.object.field in layout:
                        parent_field_type = layout[expr.object.field]['type']
                        if parent_field_type.name in self.struct_layouts:
                            # This is a nested struct field access
                            nested_layout = self.struct_layouts[parent_field_type.name]
                            if expr.field in nested_layout:
                                field_type = nested_layout[expr.field]['type']
                                return self.flow_type_to_mlir(field_type)
            
            # Regular field access
            obj_type = self.get_expression_type(expr.object)
            if isinstance(obj_type, str):
                # Convert string to Type-like object
                class SimpleType:
                    def __init__(self, name):
                        self.name = name
                obj_type = SimpleType(obj_type)
            
            if obj_type.name in self.struct_layouts:
                layout = self.struct_layouts[obj_type.name]
                if expr.field in layout:
                    field_type = layout[expr.field]['type']
                    return self.flow_type_to_mlir(field_type)
            return 'i32'  # Default
        else:
            return 'i32'  # Default
    
    def flow_type_to_mlir(self, flow_type: Type) -> str:
        flow_type = self._resolve_type_alias(flow_type)
        elem_type = self._resolve_type_alias(flow_type.element_type) if getattr(flow_type, 'element_type', None) else None
        if flow_type.name in ['i8', 'i16', 'i32', 'i64', 'i128',
                              'u8', 'u16', 'u32', 'u64', 'u128',
                              'f32', 'f64']:
            return flow_type.name
        elif flow_type.name == 'bool':
            return 'i1'
        elif flow_type.name == 'void':
            return '()'  # Void functions use empty tuple in MLIR
        elif flow_type.name == 'string':
            return '!llvm.ptr'  # String as pointer for function parameters
        elif flow_type.name.startswith('memref_'):
            # memref_f32 -> memref<?xf32>
            elem = flow_type.name.replace('memref_', '')
            return f"memref<?x{elem}>"
        elif flow_type.name.startswith('array_'):
            # Array type: array_f32 -> memref<?xf32>
            if elem_type:
                return f"memref<?x{elem_type.name}>"
            else:
                return "memref<?xi32>"
        elif flow_type.name.startswith('struct_'):
            # Struct type: struct_MyStruct -> !flow.struct<MyStruct>
            return f"!flow.struct<{flow_type.name.replace('struct_', '')}>"
        elif flow_type.name.startswith('vec'):
            # Vector type: vec4f32 -> vector<4xf32>
            if flow_type.size and elem_type:
                return f"vector<{flow_type.size}x{elem_type.name}>"
            else:
                return 'vector<?x?xf32>'  # Fallback
        elif flow_type.name.startswith('array'):
            # Array type: array_100_i32 -> memref<100xi32>
            if flow_type.size and elem_type:
                return f"memref<{flow_type.size}x{elem_type.name}>"
            elif elem_type:
                return f"memref<?x{elem_type.name}>"
            else:
                return 'memref<?xi32>'  # Fallback
        elif flow_type.name.startswith('ptr_') or flow_type.is_pointer:
            # Pointer type: ptr_f32 -> !llvm.ptr
            return '!llvm.ptr'
        else:
            # For struct types, use memref for actual memory storage
            if flow_type.name in self.struct_layouts:
                llvm_struct = self._struct_llvm_type(flow_type.name)
                if llvm_struct:
                    return llvm_struct
                total_size = sum(field['size'] for field in self.struct_layouts[flow_type.name].values())
                return f"memref<{total_size}xi8>"  # Use byte array for struct storage
            return "memref<16xi8>"  # Default struct size (4 fields * 4 bytes)

    # Backward-compatible alias for older tests/utilities
    def _flow_type_to_mlir(self, flow_type: Type) -> str:
        return self.flow_type_to_mlir(flow_type)
    
    def generate_effect(self, effect: EffectDecl) -> str:
        mlir_code = []
        mlir_code.append(f"{self.indent()}// Effect: {effect.name}")
        mlir_code.append(f"{self.indent()}// Operations:")
        for op in effect.operations:
            param_types = [self.flow_type_to_mlir(p.type) for p in op.parameters]
            return_type = self.flow_type_to_mlir(op.return_type)
            mlir_code.append(f"{self.indent()}//   {op.name}({', '.join(param_types)}) -> {return_type}")
        return "\n".join(mlir_code)
    
    def generate_capability(self, capability: CapabilityDecl) -> str:
        mlir_code = []
        mlir_code.append(f"{self.indent()}// Capability: {capability.name}")
        mlir_code.append(f"{self.indent()}// Effects: {', '.join(capability.effects)}")
        mlir_code.append(f"{self.indent()}// Methods:")
        for method in capability.methods:
            # Capability methods are currently metadata-only in the MLIR backend.
            # Effect calls are lowered directly (see generate_effect_call).
            param_types = [self.flow_type_to_mlir(p.type) for p in method.parameters]
            return_type = self.flow_type_to_mlir(method.return_type)
            mlir_code.append(f"{self.indent()}//   {method.name}({', '.join(param_types)}) -> {return_type}")
        return "\n".join(mlir_code)
    
    def generate_struct(self, struct: StructDecl) -> str:
        mlir_code = []
        mlir_code.append(f"{self.indent()}// Struct: {struct.name}")
        mlir_code.append(f"{self.indent()}// Fields:")
        for field in struct.fields:
            field_type = self.flow_type_to_mlir(field.type)
            mlir_code.append(f"{self.indent()}//   {field.name}: {field_type}")
        return "\n".join(mlir_code)
    
    def generate_const(self, const: ConstDecl) -> str:
        """Generate MLIR for constant declaration"""
        mlir_code = []
        mlir_code.append(f"{self.indent()}// Constant: {const.name}")

        mlir_type = self.flow_type_to_mlir(const.type)
        if const.type.name == 'bool':
            mlir_type = 'i1'

        # Module-scope globals should not rely on SSA values from local ops.
        if isinstance(const.value, Literal):
            if const.value.type.name == "string":
                # String constants handled via string globals; no separate const emitted.
                str_val = const.value.value
                if str_val not in self.string_constants:
                    global_name = f"str_{self.string_counter}"
                    self.string_counter += 1
                    self.string_constants[str_val] = global_name
                return ""
            literal_value = const.value.value
            mlir_code.append(f"{self.indent()}llvm.mlir.global constant @{const.name}({literal_value}) : {mlir_type}")
            return "\n".join(mlir_code)

        # Fallback: emit zero-initialized constant
        zero_value = "0"
        if mlir_type in ["f32", "f64"]:
            zero_value = "0.0"
        mlir_code.append(f"{self.indent()}llvm.mlir.global constant @{const.name}({zero_value}) : {mlir_type}")
        return "\n".join(mlir_code)

def flow_to_mlir(declarations: List[Any], source_file: str = "unknown.flow", emit_debug_info: bool = False, emit_gpu: bool = False) -> str:
    generator = MLIRGenerator(source_file)
    generator.emit_debug_info = emit_debug_info
    return generator.generate_module(declarations, emit_gpu=emit_gpu)
