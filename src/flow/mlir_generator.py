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
    MatchStatement, StructPattern, ListPattern, ConstDecl, StaticDecl, LayoutStatement, CastExpression, TypeAliasDecl, DistinctTypeDecl,
    ExpectStatement, RecordUpdate,
    BreakStatement, ContinueStatement, DeferStatement,
    EnumDecl, Parameter, Lambda,
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

    def _is_aggregate_mlir_type(self, mlir_type: str) -> bool:
        return self._is_tensor_struct(mlir_type) or mlir_type.startswith("!llvm.struct")

    def _uses_alloca_storage(self, mlir_type: str, flow_type: Any = None) -> bool:
        """Aggregate locals live in dedicated alloca slots to avoid arm64 return-slot aliasing."""
        return self._is_aggregate_mlir_type(mlir_type)

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

    def _stabilize_aggregate_ssa(
        self, value_ssa: str, mlir_type: str, callee_name: str = ""
    ) -> tuple[str, List[str]]:
        """Break arm64 aggregate-return stack aliasing via field copy + alloca roundtrip."""
        if not self._is_aggregate_mlir_type(mlir_type):
            return value_ssa, []
        if self._is_tensor_struct(mlir_type):
            copied, ops = self._materialize_tensor_for_call(value_ssa, mlir_type, callee_name)
        else:
            copied, ops = self._materialize_struct_value(value_ssa, mlir_type)
        return self._roundtrip_alloca(copied, mlir_type, ops)

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
        self._effects: Dict[str, EffectDecl] = {}  # effect name -> EffectDecl
        self._capabilities: Dict[str, CapabilityDecl] = {}  # capability name -> CapabilityDecl
        self._needs_effect_init = False  # True when vtable init must run before main
        self.inside_scf_for = False  # Track if we're inside scf.for
        self.declarations = []  # Store declarations for type lookup
        self.struct_layouts = {}  # Maps struct name to field offsets and types
        self._ssa_types: Dict[str, str] = {}  # Maps SSA name -> MLIR type string
        # SSA values that originated as Flow unsigned ints (u8/…). MLIR only has
        # signed iN, so we track this to pick arith.extui vs extsi on widen.
        self._ssa_unsigned: Set[str] = set()
        # Maps pointer SSA / var name -> !llvm.array<N x T> for struct-element arrays
        self._llvm_array_types: Dict[str, str] = {}
        self.type_aliases = {}  # name -> base Type
        self.distinct_types = {}  # name -> base Type
        self.struct_llvm_types: Dict[str, Optional[str]] = {}
        self._struct_llvm_building: Set[str] = set()
        self._init_per_function_state()

    def _init_per_function_state(self) -> None:
        """Reset per-function SSA tracking (safe for unit tests that skip generate_function)."""
        # Enclosing cf-lowered loops: break/continue branch to these labels.
        self._loop_stack: List[Dict[str, Any]] = []
        self._tensor_call_results: set[str] = set()
        self._tensor_stable_ssas: set[str] = set()
        self._tensor_field_extracts: set[str] = set()
        self._tensor_extract_origins: Dict[str, tuple[str, int]] = {}
        self._composite_call_results: set[str] = set()
        self._tensor_param_ssas: set[str] = set()
        # Keep module-global llvm.array tags; only drop per-SSA entries.
        kept = {
            k: v
            for k, v in getattr(self, "_llvm_array_types", {}).items()
            if not str(k).startswith("%")
        }
        self._llvm_array_types = kept

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
        """Look up a struct declaration by name (includes synthesized enum layouts)."""
        syn = getattr(self, "_synthetic_structs", {}).get(name)
        if syn is not None:
            return syn
        for decl in self.declarations:
            if isinstance(decl, StructDecl) and decl.name == name:
                return decl
        return None

    def _synthesize_enum_structs(self, declarations: List[Any]) -> None:
        """Treat enums as tagged structs so match/field access reuse struct lowering.

        Layout mirrors the C backend: `{ tag: i32 }` plus one field per
        single-payload variant (`Variant_value`). Multi-field payloads are
        flattened to the first field for now (parity suite uses unit/single).
        """
        self._synthetic_structs: Dict[str, StructDecl] = getattr(
            self, "_synthetic_structs", {}
        )
        self._enum_variant_owner: Dict[str, str] = getattr(
            self, "_enum_variant_owner", {}
        )
        self._enums: Dict[str, EnumDecl] = getattr(self, "_enums", {})
        for decl in declarations:
            if not isinstance(decl, EnumDecl):
                continue
            self._enums[decl.name] = decl
            fields: List[Parameter] = [Parameter("tag", Type("i32"))]
            for variant in decl.variants:
                tag_name = f"{decl.name}_{variant.name}"
                self._enum_variant_owner[tag_name] = decl.name
                if len(variant.fields) == 1:
                    fields.append(
                        Parameter(f"{variant.name}_value", variant.fields[0])
                    )
                elif len(variant.fields) > 1:
                    # Flatten first field only; full multi-field ADTs stay C-primary.
                    fields.append(
                        Parameter(f"{variant.name}_value", variant.fields[0])
                    )
            self._synthetic_structs[decl.name] = StructDecl(decl.name, fields)

    def _register_enum_variant_constants(self) -> None:
        """Register Enum_Variant names as i32 module constants (tag discriminators)."""
        for enum in getattr(self, "_enums", {}).values():
            for i, variant in enumerate(enum.variants):
                tag_name = f"{enum.name}_{variant.name}"
                self.symbol_table[tag_name] = {
                    "type": "variable",
                    "mlir_type": "i32",
                    "flow_type": Type("i32"),
                    "is_module_global": True,
                    "is_const": True,
                    "is_enum_tag": True,
                    "enum_tag_value": i,
                }

    def _emit_enum_tag_globals(self) -> List[str]:
        lines: List[str] = []
        for enum in getattr(self, "_enums", {}).values():
            for i, variant in enumerate(enum.variants):
                tag_name = f"{enum.name}_{variant.name}"
                lines.append(
                    f"{self.indent()}llvm.mlir.global internal constant @{tag_name}"
                    f"({i} : i32) : i32"
                )
        return lines

    def _calculate_struct_layouts(self, declarations: List[Any]) -> None:
        """Calculate field offsets for all struct types with proper alignment"""
        self._synthesize_enum_structs(declarations)
        for decl in declarations:
            if isinstance(decl, StructDecl):
                self._layout_one_struct(decl)
        for syn in getattr(self, "_synthetic_structs", {}).values():
            if syn.name not in self.struct_layouts:
                self._layout_one_struct(syn)

    def _layout_one_struct(self, decl: StructDecl) -> None:
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
    def _is_array_flow_type(self, flow_type) -> bool:
        """True for fixed-size Flow arrays (not pointers, which also have element_type)."""
        if flow_type is None or self._is_pointer_flow_type(flow_type):
            return False
        return (
            getattr(flow_type, "element_type", None) is not None
            and getattr(flow_type, "size", None) is not None
        )

    def _llvm_array_type_from_flow(self, flow_type) -> Optional[str]:
        """`!llvm.array<N x T>` for a Flow array type, or None if unsupported."""
        if not self._is_array_flow_type(flow_type):
            return None
        elem_mlir = self.flow_type_to_mlir(flow_type.element_type)
        size = flow_type.size
        if elem_mlir == "!llvm.ptr":
            return f"!llvm.array<{size} x ptr>"
        if elem_mlir.startswith("memref") or elem_mlir.startswith("vector"):
            return None
        return f"!llvm.array<{size} x {elem_mlir}>"

    def _get_type_size(self, flow_type) -> int:
        """Get the size of a type in bytes (simplified)"""
        # Handle string type names
        flow_type = self._resolve_type_alias(flow_type)
        type_name = flow_type.name if hasattr(flow_type, 'name') else str(flow_type)

        if self._is_array_flow_type(flow_type):
            return self._get_type_size(flow_type.element_type) * int(flow_type.size)
        
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
            # Fixed-size arrays become !llvm.array (memref is not a valid LLVM
            # struct field — doom-flow JoyState.buttons and similar).
            if self._is_array_flow_type(field.type):
                field_ty = self._llvm_array_type_from_flow(field.type)
                if field_ty is None:
                    self._struct_llvm_building.discard(struct_name)
                    self.struct_llvm_types[struct_name] = None
                    return None
            else:
                field_ty = self.flow_type_to_mlir(field.type)
                # LLVM struct fields must be LLVM-compatible scalars/pointers/structs.
                if (
                    field_ty.startswith("memref")
                    or field_ty.startswith("vector")
                    or field_ty.startswith("!flow.struct")
                ):
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
            return ssa_name, [f"{self.indent()}{ssa_name} = llvm.mlir.zero : {mlir_type}"]
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
        self.symbol_table = {}
        self._synthetic_structs = {}
        self._enum_variant_owner = {}
        self._enums = {}
        self._pending_lambdas: List[str] = []
        self._lambda_counter = 0

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
        self._register_enum_variant_constants()

        # Module header with required dialects and debug info
        if self.emit_debug_info:
            mlir_code.append(f'module attributes {{llvm.dbg.cu = #llvm.di_compile_unit<id = distinct[0]<>, sourceLanguage = DW_LANG_C, file = #llvm.di_file<"{self.source_file}" in ".">, producer = "FLOW Compiler", isOptimized = false, emissionKind = Full>}} {{')
        else:
            mlir_code.append("module {")
        self.indent_level += 1
        
        # First pass: collect all function signatures in symbol table
        self._effects = {}
        self._capabilities = {}
        self._effect_handler_stack = [{}]
        # Names with a real body in this module — skip emitting `func.func private`
        # for matching extern decls (doom-flow Z_Malloc is extern'd widely + defined).
        self._defined_function_names: Set[str] = {
            decl.name
            for decl in cpu_decls
            if isinstance(decl, FunctionDecl) and not getattr(decl, "is_extern", False)
        }
        # C varargs APIs are re-declared with many fixed arities in doom-flow;
        # lower them once as true variadic so calls type-check.
        self._c_variadic_funcs = {
            "printf", "sprintf", "snprintf", "fprintf",
            "sscanf", "fscanf", "scanf",
        }
        for decl in cpu_decls:
            if isinstance(decl, FunctionDecl):
                if getattr(decl, "is_extern", False) and decl.name == "printf":
                    self.needs_printf = True
                is_variadic = bool(getattr(decl, "is_variadic", False))
                if decl.name in self._c_variadic_funcs:
                    is_variadic = True
                params = list(decl.parameters)
                # C varargs: keep a stable fixed prefix (fmt + leading args).
                if decl.name in ("snprintf", "sprintf", "fprintf"):
                    params = params[:3]
                    is_variadic = True
                elif decl.name == "printf":
                    params = params[:1]
                    is_variadic = True
                # Add function to symbol table
                self.symbol_table[decl.name] = {
                    'type': 'function',
                    'return_type': decl.return_type,
                    'parameters': params,
                    'is_variadic': is_variadic,
                    'mlir_name': f"@{decl.name}"
                }
            elif isinstance(decl, EffectDecl):
                self._effects[decl.name] = decl
            elif isinstance(decl, CapabilityDecl):
                self._capabilities[decl.name] = decl
            elif isinstance(decl, ConstDecl):
                mlir_type = self.flow_type_to_mlir(decl.type)
                if getattr(decl.type, "name", None) == "bool":
                    mlir_type = "i1"
                entry = {
                    "type": "variable",
                    "mlir_type": mlir_type,
                    "flow_type": decl.type,
                    "is_module_global": True,
                    "is_const": True,
                }
                if getattr(decl.type, "name", None) == "string":
                    entry["mlir_type"] = "!llvm.ptr"
                    entry["is_string_global"] = True
                self.symbol_table[decl.name] = entry
            elif isinstance(decl, StaticDecl):
                mlir_type = self.flow_type_to_mlir(decl.type)
                if getattr(decl.type, "name", None) == "bool":
                    mlir_type = "i1"
                entry = {
                    "type": "variable",
                    "mlir_type": mlir_type,
                    "flow_type": decl.type,
                    "is_module_global": True,
                    "is_const": False,
                }
                # Fixed-size arrays lower to llvm.array globals; record that
                # before the per-function snapshot so restores keep GEP info.
                llvm_array_ty = self._llvm_array_type_from_flow(decl.type)
                if llvm_array_ty:
                    entry["mlir_type"] = "!llvm.ptr"
                    entry["llvm_array_type"] = llvm_array_ty
                    self._llvm_array_types[decl.name] = llvm_array_ty
                self.symbol_table[decl.name] = entry
        self._needs_effect_init = bool(self._effects) and bool(self._capabilities)

        # Register effect dispatch functions and capability methods so calls
        # to them resolve signatures through the normal function-call path.
        for effect in self._effects.values():
            for op in effect.operations:
                self.symbol_table[f"{effect.name}_{op.name}"] = {
                    'type': 'function',
                    'return_type': op.return_type,
                    'parameters': op.parameters,
                    'mlir_name': f"@{effect.name}_{op.name}",
                }
        for cap in self._capabilities.values():
            for method in cap.methods:
                self.symbol_table[f"{cap.name}_{method.name}"] = {
                    'type': 'function',
                    'return_type': method.return_type,
                    'parameters': method.parameters,
                    'mlir_name': f"@{cap.name}_{method.name}",
                }

        # Snapshot module-scope symbols. Each function restores from this so
        # params/locals from a prior function cannot leak into CF join merges
        # (doom-flow #232: stale `i` as `%arg0 : i32` while current `%arg0` is ptr).
        self._module_symbol_snapshot = {
            k: dict(v) if isinstance(v, dict) else v
            for k, v in self.symbol_table.items()
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
            elif isinstance(decl, StaticDecl):
                decl_code.append(self.generate_static(decl))
            elif isinstance(decl, EnumDecl):
                decl_code.append(
                    f"{self.indent()}// Enum: {decl.name} "
                    f"(lowered as tagged struct + variant constants)"
                )
            elif isinstance(decl, (TypeAliasDecl, DistinctTypeDecl)):
                # No MLIR output needed for aliases/distinct types (lowered to base types)
                continue
            elif type(decl).__name__ in (
                "TraitDecl", "ImplDecl", "ImportDecl", "ModuleDecl",
                "ExternBlock", "UseDecl",
            ):
                # Type-system / module surface — methods are separate FunctionDecls.
                continue
            else:
                raise NotImplementedError(
                    f"MLIR backend does not support declaration type "
                    f"{type(decl).__name__}; use the C backend (--c) or add lowering"
                )

        # Emit enum variant tag globals (Color_Red = 0, …)
        tag_globals = self._emit_enum_tag_globals()
        if tag_globals:
            decl_code = tag_globals + decl_code

        # Lifted non-capturing lambdas (must appear before uses as func.constant)
        if self._pending_lambdas:
            decl_code = self._pending_lambdas + decl_code

        # Fill capability vtables with function addresses at startup
        # (llvm.mlir.addressof cannot reference func.func symbols, so the
        # vtable globals start zeroed and @_flow_effects_init stores the
        # addresses before main's body runs).
        if self._needs_effect_init:
            decl_code.append(self._generate_effects_init())

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

        # Drop prior function's params/locals; keep module + function decls (#232).
        snapshot = getattr(self, "_module_symbol_snapshot", None)
        if snapshot is not None:
            self.symbol_table = {
                k: dict(v) if isinstance(v, dict) else v
                for k, v in snapshot.items()
            }
        self._symbol_stack = []
        
        # For extern functions, just declare them without body (dedupe across imports)
        if hasattr(func, 'is_extern') and func.is_extern:
            if func.name == "printf":
                return ""
            if func.name in getattr(self, "_defined_function_names", set()):
                return ""
            if func.name in self._declared_externs:
                return ""
            self._declared_externs.add(func.name)
            # Use the (possibly shortened) symbol-table signature for C varargs.
            info = self.symbol_table.get(func.name) or {}
            params = info.get("parameters", func.parameters)
            param_types = [self.flow_type_to_mlir(p.type) for p in params]
            return_type = self.flow_type_to_mlir(
                info.get("return_type", func.return_type)
            )
            is_variadic = bool(
                info.get("is_variadic")
                or getattr(func, "is_variadic", False)
                or func.name in getattr(self, "_c_variadic_funcs", set())
            )
            if is_variadic:
                # func dialect rejects `...`; emit llvm.func like printf (# needs_printf).
                if func.name in ("snprintf", "sprintf", "fprintf") and len(param_types) > 3:
                    param_types = param_types[:3]
                elif func.name == "printf" and len(param_types) > 1:
                    param_types = param_types[:1]
                if not param_types:
                    return (
                        f"{self.indent()}llvm.func @{func.name}(...) -> {return_type}"
                    )
                return (
                    f"{self.indent()}llvm.func @{func.name}"
                    f"({', '.join(param_types)}, ...) -> {return_type}"
                )
            func_signature = (
                f"func.func private @{func.name}"
                f"({', '.join(param_types)}) -> {return_type}"
            )
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
        self._ssa_unsigned = set()
        
        param_prologue: List[str] = []
        for i, param in enumerate(func.parameters):
            param_mlir = self.flow_type_to_mlir(param.type)
            arg_ssa = f'%arg{i}'
            bind_ssa = arg_ssa
            self._ssa_types[arg_ssa] = param_mlir
            if getattr(param.type, 'name', '').startswith('u'):
                self._ssa_unsigned.add(arg_ssa)
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
            elif param_mlir.startswith("!llvm.struct") and not self._is_tensor_struct(param_mlir):
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

        if func.name == 'main' and self._needs_effect_init:
            mlir_code.append(f"{self.indent()}func.call @_flow_effects_init() : () -> ()")

        body_mlir = self.generate_block(func.body)
        if body_mlir.strip():
            mlir_code.append(body_mlir)
        
        # Void functions must end every CF path with a terminator. An early
        # `return` inside an if makes `_block_has_return` true, but a trailing
        # while/for still leaves an empty exit block that needs `func.return`.
        if func.return_type.name == 'void' and not self._block_has_terminator(body_mlir):
            mlir_code.append(f"{self.indent()}func.return")
        
        self.indent_level -= 1
        mlir_code.append(f"{self.indent()}}}")
        
        return "\n".join(mlir_code)
    
    def generate_block(self, block: Block) -> str:
        mlir_code = []
        # New lexical scope (shallow copy). Locals declared here stay local;
        # SSA updates to names that already existed in the parent must propagate
        # back — otherwise nested while/for loop-carried values are lost when
        # generate_while replaces symbol_table entries with new dicts.
        parent_symbols = self.symbol_table
        self._symbol_stack.append(parent_symbols)
        self.symbol_table = parent_symbols.copy()
        declared_here = {
            stmt.name for stmt in block.statements if isinstance(stmt, VarDecl)
        }

        defer_stack: List[DeferStatement] = []
        exited = False
        for stmt in block.statements:
            if isinstance(stmt, DeferStatement):
                defer_stack.append(stmt)
                continue
            # Deferred expressions run before leaving the scope, LIFO.
            if isinstance(stmt, (ReturnStatement, BreakStatement, ContinueStatement)) and defer_stack:
                mlir_code.extend(self._generate_defers(defer_stack))
                defer_stack.clear()
            stmt_mlir = self.generate_statement(stmt)
            if stmt_mlir.strip():
                mlir_code.append(stmt_mlir)
            if isinstance(stmt, (ReturnStatement, BreakStatement, ContinueStatement)):
                # Anything after a terminator is unreachable and would be
                # invalid MLIR in the same block.
                exited = True
                break
        if defer_stack and not exited:
            mlir_code.extend(self._generate_defers(defer_stack))

        child_symbols = self.symbol_table
        self.symbol_table = self._symbol_stack.pop()
        for name, info in child_symbols.items():
            if name in parent_symbols and name not in declared_here:
                parent_symbols[name] = info
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
            if isinstance(stmt, MatchStatement):
                if any(self._block_has_return(c.body) for c in stmt.cases):
                    return True
                if stmt.default_case and self._block_has_return(stmt.default_case):
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
        elif isinstance(stmt, MatchStatement):
            return self.generate_match(stmt)
        elif isinstance(stmt, WhileStatement):
            return self.generate_while(stmt)
        elif isinstance(stmt, ForStatement):
            return self.generate_for(stmt)
        elif isinstance(stmt, LayoutStatement):
            return self.generate_block(stmt.body)
        elif isinstance(stmt, (BreakStatement, ContinueStatement)):
            return self._generate_loop_jump(stmt)
        elif isinstance(stmt, DeferStatement):
            # Collected and emitted at scope exit by generate_block.
            return ""
        elif isinstance(stmt, HandleStatement):
            return self.generate_handle(stmt)
        elif isinstance(stmt, (MethodCall, EffectCall)):
            _, value_ops = self.generate_expression(stmt)
            return "\n".join(value_ops)
        elif isinstance(stmt, ExpectStatement):
            # Evaluate the condition (for side effects). Runtime abort is only
            # enforced by the C backend; here we at least compile the check.
            _, value_ops = self.generate_expression(stmt.condition)
            return "\n".join(value_ops)
        elif isinstance(stmt, (Literal, Variable, BinaryOperation, UnaryOperation, FunctionCall, VectorLiteral)):
            value_ssa, value_ops = self.generate_expression(stmt)
            # Expression statement: emit ops for side effects / computation, discard value.
            return "\n".join(value_ops)
        else:
            raise NotImplementedError(
                f"MLIR backend does not support statement type "
                f"{type(stmt).__name__}; use the C backend (--c)"
            )
    
    def _generate_loop_jump(self, stmt: Statement) -> str:
        """Lower break/continue to a cf.br into the enclosing loop's exit/header."""
        kind = "break" if isinstance(stmt, BreakStatement) else "continue"
        if not self._loop_stack:
            raise NotImplementedError(
                f"`{kind}` outside a loop cannot be lowered to MLIR"
            )
        loop = self._loop_stack[-1]
        if loop.get("region") == "scf":
            # scf.for/scf.parallel regions are single-block; a cf.br out of them
            # is invalid MLIR. Fail loudly instead of dropping the statement.
            raise NotImplementedError(
                f"`{kind}` inside a `for` loop is not supported by the MLIR "
                f"backend yet; use the C backend (--c)"
            )
        target = loop["end"] if kind == "break" else loop["header"]
        carried = loop["carried"]
        ssas = [
            self.symbol_table[name]["ssa_name"]
            for name in carried
            if name in self.symbol_table
        ]
        types = [
            self.symbol_table[name]["mlir_type"]
            for name in carried
            if name in self.symbol_table
        ]
        lines: List[str] = []
        iv_ssa = loop.get("iv_ssa")
        if iv_ssa is not None:
            # Counted loop: the induction variable is the first block argument.
            # `continue` goes through the increment, as it does in C.
            if kind == "continue":
                next_iv = f"%{self.function_counter}"
                self.function_counter += 1
                lines.append(
                    f"{self.indent()}{next_iv} = arith.addi {iv_ssa}, "
                    f"{loop['iv_step']} : index"
                )
                iv_ssa = next_iv
            ssas = [iv_ssa] + ssas
            types = ["index"] + types
        lines.append(
            f"{self.indent()}cf.br ^{target}{self._cf_successor_operands(ssas, types)}"
        )
        return "\n".join(lines)

    def _contains_loop_jump(self, block: Optional[Block]) -> bool:
        """True when a block contains break/continue for the *enclosing* loop."""
        if block is None:
            return False
        for stmt in block.statements:
            if isinstance(stmt, (BreakStatement, ContinueStatement)):
                return True
            if isinstance(stmt, IfStatement):
                if self._contains_loop_jump(stmt.then_block):
                    return True
                if any(self._contains_loop_jump(b) for _, b in stmt.elif_blocks):
                    return True
                if self._contains_loop_jump(stmt.else_block):
                    return True
            elif isinstance(stmt, MatchStatement):
                if any(self._contains_loop_jump(c.body) for c in stmt.cases):
                    return True
                if self._contains_loop_jump(stmt.default_case):
                    return True
            elif isinstance(stmt, LayoutStatement):
                if self._contains_loop_jump(stmt.body):
                    return True
            # while/for bodies bind their own break/continue, so stop there.
        return False

    def _needs_cf_loop_lowering(self, block: Optional[Block]) -> bool:
        """True when a block cannot live inside a single-block scf region.

        break/continue need a cf edge out, and `while` / `match` / early
        `return` always emit cf blocks. If/elif chains that assign locals also
        force cf: nested scf.if does not propagate SSA yields correctly, which
        produced undeclared-SSA yields in doom-flow wipes / sound.
        """
        if block is None:
            return False
        for stmt in block.statements:
            if isinstance(
                stmt,
                (
                    BreakStatement,
                    ContinueStatement,
                    WhileStatement,
                    MatchStatement,
                    ReturnStatement,
                ),
            ):
                return True
            if isinstance(stmt, ForStatement):
                if self._needs_cf_loop_lowering(stmt.body):
                    return True
            elif isinstance(stmt, IfStatement):
                if stmt.elif_blocks:
                    return True
                if self._assigned_locals(stmt.then_block):
                    return True
                if stmt.else_block and self._assigned_locals(stmt.else_block):
                    return True
                if self._needs_cf_loop_lowering(stmt.then_block):
                    return True
                if any(self._needs_cf_loop_lowering(b) for _, b in stmt.elif_blocks):
                    return True
                if self._needs_cf_loop_lowering(stmt.else_block):
                    return True
            elif isinstance(stmt, LayoutStatement):
                if self._needs_cf_loop_lowering(stmt.body):
                    return True
        return False

    def _generate_defers(self, defers: List[DeferStatement]) -> List[str]:
        """Emit deferred expressions in LIFO order (mirrors the C backend)."""
        lines: List[str] = []
        for defer_stmt in reversed(defers):
            _value, value_ops = self.generate_expression(defer_stmt.expr)
            lines.extend(value_ops)
        return lines

    def generate_var_decl(self, var_decl: VarDecl) -> str:
        # Non-capturing lambdas: keep the func.constant SSA, skip aggregate casts.
        if isinstance(getattr(var_decl, "initializer", None), Lambda):
            init_value, init_ops = self.generate_lambda(var_decl.initializer)
            fn_ty = self._ssa_types.get(init_value, "() -> i32")
            self.symbol_table[var_decl.name] = {
                "type": "variable",
                "ssa_name": init_value,
                "mlir_type": fn_ty,
                "flow_type": var_decl.type,
                "is_closure": True,
                "fn_mlir_type": fn_ty,
            }
            return "\n".join(init_ops) if init_ops else ""

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
            elif isinstance(var_decl.initializer, ArrayLiteral) and mlir_type.startswith("memref<"):
                init_value, init_ops = self.generate_array_literal(
                    var_decl.initializer,
                    elem_type_hint=self._memref_element_type(mlir_type),
                )
            else:
                init_value, init_ops = self.generate_expression(var_decl.initializer)
            
            # Cast the initializer to the variable's type if needed
            init_type = self._ssa_types.get(init_value) or self.get_expression_type(var_decl.initializer)
            if init_type != mlir_type:
                init_value, cast_ops = self._emit_cast(init_value, init_type, mlir_type)
                init_ops.extend(cast_ops)
            self._ssa_types[init_value] = mlir_type
            if getattr(var_decl.type, 'name', '').startswith('u'):
                self._ssa_unsigned.add(init_value)

            from_tensor_field = init_value in self._tensor_field_extracts
            if self._is_aggregate_mlir_type(mlir_type) and (
                init_value in self._tensor_call_results
                or init_value in self._composite_call_results
                or from_tensor_field
            ):
                orig_ssa = init_value
                init_value, mat_ops = self._stabilize_aggregate_ssa(init_value, mlir_type)
                init_ops.extend(mat_ops)
                self._tensor_call_results.discard(orig_ssa)
                self._composite_call_results.discard(orig_ssa)
                self._tensor_field_extracts.discard(orig_ssa)
                self._tensor_stable_ssas.add(init_value)
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
            # Aggregates always use alloca. Mutable scalars also get alloca so
            # `&x` inside one scf.if arm cannot create a region-local pointer
            # that the other arm later stores through (EV_DoDonut).
            needs_alloca = self._uses_alloca_storage(mlir_type, var_decl.type) or (
                getattr(var_decl, "is_mutable", False)
                and not mlir_type.startswith("memref")
            )
            if needs_alloca:
                ptr, alloc_ops = self._emit_alloca_store(init_value, mlir_type)
                init_ops.extend(alloc_ops)
                var_entry["alloca_ptr"] = ptr
            llvm_array_ty = self._llvm_array_types.get(init_value)
            if llvm_array_ty:
                var_entry["llvm_array_type"] = llvm_array_ty
                self._llvm_array_types[var_decl.name] = llvm_array_ty
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

            if self._is_aggregate_mlir_type(return_type):
                value_ssa, mat_ops = self._stabilize_aggregate_ssa(value_ssa, return_type)
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

                # Match generate_array_access: !llvm.array globals/locals need
                # gep[0, i], not flat ptr indexing (array<ptr>/array<string>).
                llvm_array_ty = self._llvm_array_type_for(access.array, array_ssa)
                if llvm_array_ty is not None:
                    elem_flow = self._flow_type_of_expr(access)
                    elem_type = (
                        self.flow_type_to_mlir(elem_flow)
                        if elem_flow is not None
                        else '!llvm.ptr'
                    )
                    val_type = self._ssa_types.get(value_ssa) or self.get_expression_type(assignment.value)
                    if val_type != elem_type:
                        value_ssa, cast_ops = self._emit_cast(value_ssa, val_type, elem_type)
                        ops.extend(cast_ops)
                    gep, gep_ops = self._emit_llvm_array_index_gep(
                        array_ssa, index_ssa, index_type, llvm_array_ty
                    )
                    ops.extend(gep_ops)
                    ops.append(
                        f"{self.indent()}llvm.store {value_ssa}, {gep} : {elem_type}, !llvm.ptr"
                    )
                    return "\n".join(ops)

                if self._is_pointer_array_ssa(array_ssa, access):
                    elem_flow = self._flow_type_of_expr(access)
                    elem_type = (
                        self.flow_type_to_mlir(elem_flow)
                        if elem_flow is not None
                        else (self._elem_type_from_array_expr(access.array) or 'f32')
                    )
                    val_type = self._ssa_types.get(value_ssa) or self.get_expression_type(assignment.value)
                    if val_type != elem_type:
                        value_ssa, cast_ops = self._emit_cast(value_ssa, val_type, elem_type)
                        ops.extend(cast_ops)
                    gep, gep_ops = self._emit_ptr_index_gep(array_ssa, index_ssa, index_type, elem_type)
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

                # Use the array's declared memref type so fixed-shape locals
                # store as memref<Nxi32> rather than an unranked memref<?xi32>
                # (which does not type-check against the memref.alloc result).
                elem_type = 'f32'
                arr_mlir = self._ssa_types.get(array_ssa)
                if not arr_mlir and isinstance(access.array, Variable) and access.array.name in self.symbol_table:
                    arr_mlir = self.symbol_table[access.array.name].get('mlir_type', '')
                if arr_mlir and arr_mlir.startswith('memref<'):
                    memref_ty = arr_mlir
                    elem_type = self._memref_element_type(arr_mlir) or elem_type
                else:
                    memref_ty = f'memref<?x{elem_type}>'

                val_type = self._ssa_types.get(value_ssa) or self.get_expression_type(assignment.value)
                if val_type != elem_type:
                    value_ssa, cast_ops = self._emit_cast(value_ssa, val_type, elem_type)
                    ops.extend(cast_ops)

                ops.append(f"{self.indent()}memref.store {value_ssa}, {array_ssa}[{final_index}] : {memref_ty}")
                return "\n".join(ops)
            elif isinstance(access, FieldAccess):
                field_store = self._generate_field_store(access, assignment.value, value_ssa, ops)
                if field_store is not None:
                    return field_store
                return f"{self.indent()}// Unsupported assignment target expression"
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
            if target_info.get("is_module_global") and target_type:
                if target_info.get("is_const"):
                    raise NotImplementedError(
                        f"cannot assign to module const '{assignment.target}'"
                    )
                ops.extend(self._store_module_global(assignment.target, target_type, value_ssa))
                return "\n".join(ops)
            target_info["ssa_name"] = value_ssa
            if target_type:
                self._ssa_types[value_ssa] = target_type
            if target_info.get("alloca_ptr") and target_type:
                ops.extend(self._store_aggregate_var(target_info, value_ssa))
            return "\n".join(ops)
        else:
            return f"{self.indent()}// Assignment to undefined variable: {assignment.target}"
    
    def _generate_field_store(self, access: FieldAccess, value_expr, value_ssa: str, ops: List[str]) -> Optional[str]:
        """Lower obj.field = value via GEP + scalar store.

        Handles pointer-to-struct objects, alloca-backed struct locals, and
        chained postfix lvalues such as bodies[0].id / bodies[0].pos.x.
        Returns None when the target shape is unsupported.
        """
        addr = self._address_of_struct_lvalue(access.object)
        if addr is None:
            return None
        base_ptr, base_ops, struct_name = addr
        ops.extend(base_ops)

        llvm_struct = self._struct_llvm_type(struct_name)
        decl = self._get_struct_decl(struct_name)
        if not llvm_struct or not decl:
            return None
        field_names = [f.name for f in decl.fields]
        if access.field not in field_names:
            return None
        idx = field_names.index(access.field)

        field_flow = self._determine_field_type(access)
        field_ty = self.flow_type_to_mlir(field_flow) if field_flow else None
        if not field_ty:
            field_types = self._struct_field_types(llvm_struct)
            field_ty = field_types[idx] if idx < len(field_types) else None
        if not field_ty:
            return None

        val_type = self._ssa_types.get(value_ssa) or self.get_expression_type(value_expr)
        if val_type != field_ty:
            value_ssa, cast_ops = self._emit_cast(value_ssa, val_type, field_ty)
            ops.extend(cast_ops)

        gep = f"%{self.function_counter}"
        self.function_counter += 1
        ops.append(
            f"{self.indent()}{gep} = llvm.getelementptr {base_ptr}[0, {idx}] "
            f": (!llvm.ptr) -> !llvm.ptr, {llvm_struct}"
        )
        self._ssa_types[gep] = '!llvm.ptr'
        ops.append(f"{self.indent()}llvm.store {value_ssa}, {gep} : {field_ty}, !llvm.ptr")
        return "\n".join(ops)

    def generate_if(self, if_stmt: IfStatement) -> str:
        # break/continue/while/match all need their own blocks, which an scf.if
        # region cannot hold; force the cf lowering.
        if (
            self._needs_cf_loop_lowering(if_stmt.then_block)
            or any(self._needs_cf_loop_lowering(b) for _, b in if_stmt.elif_blocks)
            or self._needs_cf_loop_lowering(if_stmt.else_block)
        ):
            return self._generate_cf_if(if_stmt)
        if not if_stmt.elif_blocks:
            then_assigned = self._assigned_locals(if_stmt.then_block)
            else_assigned = self._assigned_locals(if_stmt.else_block) if if_stmt.else_block else []
            merged_vars = list(dict.fromkeys(then_assigned + else_assigned))
            # Only SSA-mergeable locals need scf.if yields. Module-global stores
            # (joy_ptr = …) must not take this path — filtering to empty used to
            # drop the entire then-block and leave a dead compare.
            mergeable = self._filter_ssa_mergeable(merged_vars)
            if mergeable:
                condition_ssa, condition_ops = self.generate_expression(if_stmt.condition)
                return self._generate_scf_if_with_yield(
                    if_stmt, condition_ssa, mergeable, condition_ops
                )
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
            elif isinstance(stmt, MatchStatement):
                for case in stmt.cases:
                    for name in self._assigned_locals(case.body):
                        if name not in assigned:
                            assigned.append(name)
                if stmt.default_case:
                    for name in self._assigned_locals(stmt.default_case):
                        if name not in assigned:
                            assigned.append(name)
            elif isinstance(stmt, WhileStatement):
                # Nested loops may assign outer locals (loop-carried for parent).
                for name in self._assigned_locals(stmt.body):
                    if name not in assigned:
                        assigned.append(name)
            elif isinstance(stmt, ForStatement):
                for name in self._assigned_locals(stmt.body):
                    if name not in assigned:
                        assigned.append(name)
        return assigned

    def _filter_ssa_mergeable(self, names: List[str]) -> List[str]:
        """Locals that can be CF/SCF join-block arguments (have live SSA bindings).

        Module globals and alloca-backed slots have no ``ssa_name`` and must not
        participate in block-arg merges (doom-flow hit KeyError: ssa_name).
        Also skip bindings whose recorded mlir_type disagrees with ``_ssa_types``
        for that SSA (stale cross-function leak of ``%argN`` — #232).
        """
        out: List[str] = []
        for name in names:
            info = self.symbol_table.get(name)
            if not info:
                continue
            if info.get("is_module_global"):
                continue
            if info.get("alloca_ptr"):
                # Memory is authoritative; do not SSA-merge across scf.if.
                continue
            if "ssa_name" not in info:
                continue
            if "mlir_type" not in info:
                continue
            ssa = info["ssa_name"]
            ty = info["mlir_type"]
            tracked = self._ssa_types.get(ssa)
            if tracked is not None and tracked != ty:
                continue
            if name not in out:
                out.append(name)
        return out

    def _generate_scf_if_with_yield(
        self,
        if_stmt: IfStatement,
        condition_ssa: str,
        merged_vars: List[str],
        prefix_ops: List[str],
    ) -> str:
        mlir_code = list(prefix_ops)
        merged_vars = self._filter_ssa_mergeable(
            [v for v in merged_vars if v in self.symbol_table]
        )
        if not merged_vars:
            # Side-effect-only then/else (globals, field stores): plain scf.if.
            mlir_code = list(prefix_ops)
            mlir_code.append(f"{self.indent()}scf.if {condition_ssa} {{")
            self.indent_level += 1
            then_body = self.generate_block(if_stmt.then_block)
            if then_body.strip():
                mlir_code.append(then_body)
            self.indent_level -= 1
            if if_stmt.else_block:
                mlir_code.append(f"{self.indent()}}} else {{")
                self.indent_level += 1
                else_body = self.generate_block(if_stmt.else_block)
                if else_body.strip():
                    mlir_code.append(else_body)
                self.indent_level -= 1
                mlir_code.append(f"{self.indent()}}}")
            else:
                mlir_code.append(f"{self.indent()}}}")
            return "\n".join(mlir_code)

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

        # Assignments mutate the shared var-entry dicts in place, so the
        # then-branch bindings leak into the else region unless we restore the
        # pre-if SSA names here. The else branch must observe pre-if state.
        for v in merged_vars:
            self.symbol_table[v]['ssa_name'] = old_ssas[v]

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
            mergeable = self._filter_ssa_mergeable(merged_vars)
            if mergeable:
                return self._generate_scf_if_with_yield(
                    if_stmt, condition_ssa, mergeable, mlir_code
                )
        
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

        # Locals written by any branch are merged with block arguments on the
        # join block; without this the branch-local SSA name escapes and fails
        # dominance verification.
        merged_vars: List[str] = []
        for block in (
            [if_stmt.then_block]
            + [b for _, b in if_stmt.elif_blocks]
            + ([if_stmt.else_block] if if_stmt.else_block else [])
        ):
            for name in self._assigned_locals(block):
                if name not in merged_vars and name in self.symbol_table:
                    merged_vars.append(name)
        merged_vars = self._filter_ssa_mergeable(merged_vars)
        entry_ssas = {v: self.symbol_table[v]['ssa_name'] for v in merged_vars}
        merged_types = [self.symbol_table[v]['mlir_type'] for v in merged_vars]

        def _restore_entry_bindings() -> None:
            for v in merged_vars:
                self.symbol_table[v]['ssa_name'] = entry_ssas[v]

        def _end_edge() -> str:
            if not merged_vars:
                return ""
            return self._cf_successor_operands(
                [self.symbol_table[v]['ssa_name'] for v in merged_vars], merged_types
            )

        def _entry_edge() -> str:
            if not merged_vars:
                return ""
            return self._cf_successor_operands(
                [entry_ssas[v] for v in merged_vars], merged_types
            )

        mlir_code.append(f"{self.indent()}cf.cond_br {condition_ssa}, ^{current_then_block}, ^{current_else_block}")

        # Generate then block
        mlir_code.append(f"{self.indent()}^{current_then_block}:")
        self.indent_level += 1
        _restore_entry_bindings()
        then_body = self.generate_block(if_stmt.then_block)
        if then_body.strip():
            mlir_code.append(then_body)
        # Only add branch if block doesn't already end with a terminator
        if not self._block_has_terminator(then_body):
            mlir_code.append(f"{self.indent()}cf.br ^{end_block}{_end_edge()}")
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
            # A false edge straight to the join block still owes it operands.
            fallthrough_edge = _entry_edge() if next_elif_block == end_block else ""
            if next_elif_block == end_block:
                needs_end_block = True
            mlir_code.append(
                f"{self.indent()}cf.cond_br {elif_cond_ssa}, "
                f"^{elif_then_block}, ^{next_elif_block}{fallthrough_edge}"
            )
            self.indent_level -= 1

            # Generate elif then block
            mlir_code.append(f"{self.indent()}^{elif_then_block}:")
            self.indent_level += 1
            _restore_entry_bindings()
            elif_body = self.generate_block(elif_block)
            if elif_body.strip():
                mlir_code.append(elif_body)
            # Only add branch if block doesn't already end with a terminator
            if not self._block_has_terminator(elif_body):
                mlir_code.append(f"{self.indent()}cf.br ^{end_block}{_end_edge()}")
                needs_end_block = True
            self.indent_level -= 1

            current_block = next_elif_block

        # Generate else block or pass-through
        if if_stmt.else_block:
            mlir_code.append(f"{self.indent()}^{current_block}:")
            self.indent_level += 1
            _restore_entry_bindings()
            else_body = self.generate_block(if_stmt.else_block)
            if else_body.strip():
                mlir_code.append(else_body)
            # Only add branch if block doesn't already end with a terminator
            if not self._block_has_terminator(else_body):
                mlir_code.append(f"{self.indent()}cf.br ^{end_block}{_end_edge()}")
                needs_end_block = True
            self.indent_level -= 1
        elif current_block != end_block:
            mlir_code.append(f"{self.indent()}^{current_block}:")
            self.indent_level += 1
            mlir_code.append(f"{self.indent()}cf.br ^{end_block}{_entry_edge()}")
            needs_end_block = True
            self.indent_level -= 1

        # Only emit end block if at least one branch needs it
        if needs_end_block:
            if merged_vars:
                end_args = []
                for ty in merged_types:
                    arg = f"%{self.function_counter}"
                    self.function_counter += 1
                    end_args.append((arg, ty))
                mlir_code.append(
                    f"{self.indent()}^{end_block}"
                    f"({', '.join(f'{a}: {t}' for a, t in end_args)}):"
                )
                for var_name, (arg, ty) in zip(merged_vars, end_args):
                    self.symbol_table[var_name]['ssa_name'] = arg
                    self._ssa_types[arg] = ty
            else:
                mlir_code.append(f"{self.indent()}^{end_block}:")
        elif merged_vars:
            # Every branch terminated; nothing after the if can observe the
            # merge, but leave the entry bindings in place rather than an
            # arm-local SSA name.
            _restore_entry_bindings()

        return "\n".join(mlir_code)
    
    def _cf_successor_operands(self, ssa_names: List[str], mlir_types: List[str]) -> str:
        """CF dialect successor operands: (%a, %b : i32, i32) — types once after all values."""
        if not ssa_names:
            return ""
        return f"({', '.join(ssa_names)} : {', '.join(mlir_types)})"

    def generate_while(self, while_stmt: WhileStatement) -> str:
        mlir_code = []

        # Detect loop-carried variables
        loop_carried_vars = self._detect_loop_carried_vars(while_stmt.body)

        # Create blocks
        header_block = self._new_block_label()
        body_block = self._new_block_label()
        end_block = self._new_block_label()

        # Prepare initial values for loop-carried variables
        init_ssas: List[str] = []
        init_types: List[str] = []
        for var_name in loop_carried_vars:
            if var_name in self.symbol_table:
                var_info = self.symbol_table[var_name]
                init_ssas.append(var_info['ssa_name'])
                init_types.append(var_info['mlir_type'])

        # Jump to header with initial values
        if init_ssas:
            mlir_code.append(
                f"{self.indent()}cf.br ^{header_block}"
                f"{self._cf_successor_operands(init_ssas, init_types)}"
            )
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
        
        # Branch based on condition — both successors take the loop-carried args
        # (the exit block needs them too, otherwise its block arguments have no
        # incoming values on the exit edge).
        header_ssas: List[str] = []
        header_types: List[str] = []
        for var_name in loop_carried_vars:
            if var_name in self.symbol_table:
                var_info = self.symbol_table[var_name]
                header_ssas.append(var_info['ssa_name'])
                header_types.append(var_info['mlir_type'])

        if header_ssas:
            succ = self._cf_successor_operands(header_ssas, header_types)
            mlir_code.append(
                f"{self.indent()}cf.cond_br {condition_ssa}, "
                f"^{body_block}{succ}, ^{end_block}{succ}"
            )
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
        self._loop_stack.append({
            "region": "cf",
            "header": header_block,
            "end": end_block,
            "carried": list(loop_carried_vars),
        })
        try:
            body_mlir = self.generate_block(while_stmt.body)
        finally:
            self._loop_stack.pop()
        if body_mlir.strip():
            mlir_code.append(body_mlir)

        # Prepare final values for next iteration
        final_ssas: List[str] = []
        final_types: List[str] = []
        for var_name in loop_carried_vars:
            if var_name in self.symbol_table:
                var_info = self.symbol_table[var_name]
                final_ssas.append(var_info['ssa_name'])
                final_types.append(var_info['mlir_type'])

        # Branch back to header with updated values. Skip when the body already
        # ended in a terminator (an unconditional break/continue/return).
        if self._block_has_terminator(body_mlir):
            pass
        elif final_ssas:
            mlir_code.append(
                f"{self.indent()}cf.br ^{header_block}"
                f"{self._cf_successor_operands(final_ssas, final_types)}"
            )
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
    
    def _expr_is_loop_index(self, expr: Expression, iv_name: str) -> bool:
        return isinstance(expr, Variable) and expr.name == iv_name

    def _memref_scalar_base(self, expr: Expression, elem: str) -> Optional[str]:
        """Return symbol name when expr is a memref/pointer array of `elem`."""
        if not isinstance(expr, Variable) or expr.name not in self.symbol_table:
            return None
        info = self.symbol_table[expr.name]
        mlir_ty = info.get("mlir_type", "")
        flow_ty = info.get("flow_type")
        if isinstance(mlir_ty, str) and mlir_ty.startswith("memref<") and f"x{elem}>" in mlir_ty:
            return expr.name
        if flow_ty is not None:
            name = getattr(flow_ty, "name", "")
            if name in (f"memref_{elem}", f"ptr_{elem}") or (
                getattr(flow_ty, "is_pointer", False)
                and getattr(flow_ty, "element_type", None) is not None
                and flow_ty.element_type.name == elem
            ):
                return expr.name
        return None

    def _vectorizable_scalar_rhs(
        self, expr: Expression, iv_name: str, allowed_bases: set, elem: str
    ) -> bool:
        """True when expr is loop-invariant or elem loads of allowed_bases[iv]."""
        if isinstance(expr, Literal):
            return True
        if isinstance(expr, Variable):
            return expr.name != iv_name  # invariant scalar / address
        if isinstance(expr, ArrayAccess):
            base = self._memref_scalar_base(expr.array, elem)
            if base is None or base not in allowed_bases:
                return False
            return self._expr_is_loop_index(expr.index, iv_name)
        if isinstance(expr, BinaryOperation):
            ops_ok = ("+", "-", "*", "/") if elem.startswith("f") else ("+", "-", "*")
            if expr.operator not in ops_ok:
                return False
            return (
                self._vectorizable_scalar_rhs(expr.left, iv_name, allowed_bases, elem)
                and self._vectorizable_scalar_rhs(expr.right, iv_name, allowed_bases, elem)
            )
        if isinstance(expr, UnaryOperation) and expr.operator == "-":
            return self._vectorizable_scalar_rhs(expr.operand, iv_name, allowed_bases, elem)
        return False

    def _emit_vector_scalar_expr(
        self, expr: Expression, iv_name: str, iv_ssa: str, ops: List[str], elem: str
    ) -> Optional[str]:
        """Lower a vectorizable scalar RHS to vector<4x{elem}> SSA."""
        vty = f"vector<4x{elem}>"
        zero = "0.0" if elem.startswith("f") else "0"
        if isinstance(expr, Literal):
            val = self._format_mlir_numeric(str(expr.value), elem)
            splat = f"%{self.function_counter}"
            self.function_counter += 1
            cst = f"%{self.function_counter}"
            self.function_counter += 1
            ops.append(f"{self.indent()}{cst} = arith.constant {val} : {elem}")
            ops.append(
                f"{self.indent()}{splat} = vector.broadcast {cst} : {elem} to {vty}"
            )
            self._ssa_types[splat] = vty
            return splat
        if isinstance(expr, Variable):
            info = self.symbol_table[expr.name]
            scalar = info["ssa_name"]
            ty = info.get("mlir_type", elem)
            if ty != elem:
                scalar, cast_ops = self._emit_cast(scalar, ty, elem)
                ops.extend(cast_ops)
            splat = f"%{self.function_counter}"
            self.function_counter += 1
            ops.append(
                f"{self.indent()}{splat} = vector.broadcast {scalar} : {elem} to {vty}"
            )
            self._ssa_types[splat] = vty
            return splat
        if isinstance(expr, ArrayAccess):
            base = expr.array.name
            base_info = self.symbol_table.get(base)
            if not base_info or base_info.get("is_module_global") or "ssa_name" not in base_info:
                return None  # module-global bases fall back to scalar
            base_ssa = base_info["ssa_name"]
            mlir_ty = self.symbol_table[base].get("mlir_type", f"memref<?x{elem}>")
            if mlir_ty == "!llvm.ptr":
                return None  # ptr bases not yet vector-transfer compatible
            pad = f"%{self.function_counter}"
            self.function_counter += 1
            ops.append(f"{self.indent()}{pad} = arith.constant {zero} : {elem}")
            vec = f"%{self.function_counter}"
            self.function_counter += 1
            ops.append(
                f"{self.indent()}{vec} = vector.transfer_read {base_ssa}[{iv_ssa}], {pad} "
                f"{{in_bounds = [true]}} : {mlir_ty}, {vty}"
            )
            self._ssa_types[vec] = vty
            return vec
        if isinstance(expr, UnaryOperation) and expr.operator == "-":
            inner = self._emit_vector_scalar_expr(expr.operand, iv_name, iv_ssa, ops, elem)
            if inner is None:
                return None
            out = f"%{self.function_counter}"
            self.function_counter += 1
            if elem.startswith("f"):
                ops.append(f"{self.indent()}{out} = arith.negf {inner} : {vty}")
            else:
                z = f"%{self.function_counter}"
                self.function_counter += 1
                ops.append(f"{self.indent()}{z} = arith.constant 0 : {elem}")
                zb = f"%{self.function_counter}"
                self.function_counter += 1
                ops.append(f"{self.indent()}{zb} = vector.broadcast {z} : {elem} to {vty}")
                ops.append(f"{self.indent()}{out} = arith.subi {zb}, {inner} : {vty}")
            self._ssa_types[out] = vty
            return out
        if isinstance(expr, BinaryOperation):
            left = self._emit_vector_scalar_expr(expr.left, iv_name, iv_ssa, ops, elem)
            right = self._emit_vector_scalar_expr(expr.right, iv_name, iv_ssa, ops, elem)
            if left is None or right is None:
                return None
            out = f"%{self.function_counter}"
            self.function_counter += 1
            if elem.startswith("f"):
                op_map = {"+": "arith.addf", "-": "arith.subf", "*": "arith.mulf", "/": "arith.divf"}
            else:
                op_map = {"+": "arith.addi", "-": "arith.subi", "*": "arith.muli"}
            ops.append(
                f"{self.indent()}{out} = {op_map[expr.operator]} {left}, {right} : {vty}"
            )
            self._ssa_types[out] = vty
            return out
        return None

    def _try_vectorize_elementwise_for(self, for_stmt: ForStatement) -> Optional[str]:
        """Emit vector<4xT> transfer loops for simple elementwise f32/i32 bodies.

        Pattern: `for i in lo to hi { out[i] = <expr using out/x/y[i] + scalars> }`
        with no loop-carried scalars. Uses step-4 vector body + scalar remainder.
        """
        if for_stmt.is_parallel or for_stmt.step is not None:
            return None
        if not for_stmt.body or len(for_stmt.body.statements) != 1:
            return None
        stmt = for_stmt.body.statements[0]
        if not isinstance(stmt, Assignment) or stmt.target_expr is None:
            return None
        access = stmt.target_expr
        if not isinstance(access, ArrayAccess):
            return None

        elem = None
        out_base = None
        for candidate in ("f32", "i32"):
            out_base = self._memref_scalar_base(access.array, candidate)
            if out_base is not None:
                elem = candidate
                break
        if out_base is None or elem is None:
            return None
        iv = for_stmt.variable
        if not self._expr_is_loop_index(access.index, iv):
            return None

        bases = {out_base}

        def walk(e):
            if isinstance(e, ArrayAccess):
                b = self._memref_scalar_base(e.array, elem)
                if b:
                    bases.add(b)
                walk(e.index)
            elif isinstance(e, BinaryOperation):
                walk(e.left)
                walk(e.right)
            elif isinstance(e, UnaryOperation):
                walk(e.operand)

        walk(stmt.value)
        if not self._vectorizable_scalar_rhs(stmt.value, iv, bases, elem):
            return None
        out_mlir = self.symbol_table[out_base].get("mlir_type", "")
        if not (isinstance(out_mlir, str) and out_mlir.startswith("memref<") and f"x{elem}" in out_mlir):
            flow_ty = self.symbol_table[out_base].get("flow_type")
            if not (flow_ty and getattr(flow_ty, "name", "") == f"memref_{elem}"):
                return None
            out_mlir = f"memref<?x{elem}>"

        for b in bases:
            if self.symbol_table[b].get("mlir_type", "") == "!llvm.ptr":
                return None
            # Module-global bases have no SSA memref value; skip vectorization.
            if self.symbol_table[b].get("is_module_global") or "ssa_name" not in self.symbol_table[b]:
                return None

        ops: List[str] = []
        lower_bound, lower_ops = self.generate_expression(for_stmt.range_start)
        upper_bound, upper_ops = self.generate_expression(for_stmt.range_end)
        ops.extend(lower_ops)
        ops.extend(upper_ops)

        lb = f"%{self.function_counter}"
        self.function_counter += 1
        ub = f"%{self.function_counter}"
        self.function_counter += 1
        c1 = f"%{self.function_counter}"
        self.function_counter += 1
        c4 = f"%{self.function_counter}"
        self.function_counter += 1
        ops.append(f"{self.indent()}{lb} = arith.index_cast {lower_bound} : i32 to index")
        ops.append(f"{self.indent()}{ub} = arith.index_cast {upper_bound} : i32 to index")
        ops.append(f"{self.indent()}{c1} = arith.constant 1 : index")
        ops.append(f"{self.indent()}{c4} = arith.constant 4 : index")

        # n = ub - lb; n_vec = n - (n % 4); vec_ub = lb + n_vec
        n = f"%{self.function_counter}"
        self.function_counter += 1
        rem = f"%{self.function_counter}"
        self.function_counter += 1
        n_vec = f"%{self.function_counter}"
        self.function_counter += 1
        vec_ub = f"%{self.function_counter}"
        self.function_counter += 1
        ops.append(f"{self.indent()}{n} = arith.subi {ub}, {lb} : index")
        ops.append(f"{self.indent()}{rem} = arith.remsi {n}, {c4} : index")
        ops.append(f"{self.indent()}{n_vec} = arith.subi {n}, {rem} : index")
        ops.append(f"{self.indent()}{vec_ub} = arith.addi {lb}, {n_vec} : index")

        vty = f"vector<4x{elem}>"
        # Vectorized loop
        iv_v = f"%{self.function_counter}"
        self.function_counter += 1
        ops.append(f"{self.indent()}scf.for {iv_v} = {lb} to {vec_ub} step {c4} {{")
        self.indent_level += 1
        self._ssa_types[iv_v] = "index"
        saved_iv = self.symbol_table.get(iv)
        self.symbol_table[iv] = {"type": "variable", "mlir_type": "index", "ssa_name": iv_v}
        body_ops: List[str] = []
        vec_val = self._emit_vector_scalar_expr(stmt.value, iv, iv_v, body_ops, elem)
        if vec_val is None:
            self.indent_level -= 1
            if saved_iv is None:
                self.symbol_table.pop(iv, None)
            else:
                self.symbol_table[iv] = saved_iv
            return None
        ops.extend(body_ops)
        out_ssa = self.symbol_table[out_base]["ssa_name"]
        ops.append(
            f"{self.indent()}vector.transfer_write {vec_val}, {out_ssa}[{iv_v}] "
            f"{{in_bounds = [true]}} : {vty}, {out_mlir}"
        )
        self.indent_level -= 1
        ops.append(f"{self.indent()}}}")
        # Scalar remainder
        iv_s = f"%{self.function_counter}"
        self.function_counter += 1
        ops.append(f"{self.indent()}scf.for {iv_s} = {vec_ub} to {ub} step {c1} {{")
        self.indent_level += 1
        self._ssa_types[iv_s] = "index"
        self.symbol_table[iv] = {"type": "variable", "mlir_type": "index", "ssa_name": iv_s}
        # Reuse normal assignment lowering for the scalar tail.
        old_inside = self.inside_scf_for
        self.inside_scf_for = True
        assign_mlir = self.generate_assignment(stmt)
        if assign_mlir.strip():
            ops.append(assign_mlir)
        self.inside_scf_for = old_inside
        self.indent_level -= 1
        ops.append(f"{self.indent()}}}")
        if saved_iv is None:
            self.symbol_table.pop(iv, None)
        else:
            self.symbol_table[iv] = saved_iv
        ops.insert(0, f"{self.indent()}// flow: vectorized elementwise f32 loop (VF=4)")
        return "\n".join(ops)

    def _constant_step(self, for_stmt: ForStatement) -> Optional[int]:
        """Compile-time step for a counted loop, or None when it is dynamic."""
        step = for_stmt.step
        if step is None:
            return 1
        if isinstance(step, UnaryOperation) and step.operator == "-":
            inner = self._constant_step_literal(step.operand)
            return None if inner is None else -inner
        return self._constant_step_literal(step)

    @staticmethod
    def _constant_step_literal(expr: Expression) -> Optional[int]:
        if not isinstance(expr, Literal):
            return None
        try:
            return int(str(expr.value))
        except (TypeError, ValueError):
            return None

    def _generate_cf_for(self, for_stmt: ForStatement, step_value: Optional[int] = 1) -> str:
        """Counted loop lowered to cf blocks so break/continue have somewhere to go.

        scf.for regions are single-block, so a `break` inside one cannot be
        expressed. This mirrors generate_while's block layout with the
        induction variable as an extra loop-carried value.
        """
        mlir_code: List[str] = []
        loop_carried_vars = self._detect_loop_carried_vars(for_stmt.body)

        lower_bound, lower_ops = self.generate_expression(for_stmt.range_start)
        upper_bound, upper_ops = self.generate_expression(for_stmt.range_end)
        mlir_code.extend(lower_ops)
        mlir_code.extend(upper_ops)

        lb = f"%{self.function_counter}"
        self.function_counter += 1
        ub = f"%{self.function_counter}"
        self.function_counter += 1
        mlir_code.append(f"{self.indent()}{lb} = arith.index_cast {lower_bound} : i32 to index")
        mlir_code.append(f"{self.indent()}{ub} = arith.index_cast {upper_bound} : i32 to index")

        # Descending loops run while iv > ub, exactly as the C backend does.
        # With a constant step the direction is known here; with a dynamic one
        # the sign is tested once in the entry block and selected per iteration.
        ascending_ssa: Optional[str] = None
        step = f"%{self.function_counter}"
        self.function_counter += 1
        if step_value is not None:
            mlir_code.append(f"{self.indent()}{step} = arith.constant {step_value} : index")
            cmp_pred = "slt" if step_value > 0 else "sgt"
        else:
            step_expr_ssa, step_ops = self.generate_expression(for_stmt.step)
            mlir_code.extend(step_ops)
            mlir_code.append(
                f"{self.indent()}{step} = arith.index_cast {step_expr_ssa} : i32 to index"
            )
            zero = f"%{self.function_counter}"
            self.function_counter += 1
            ascending_ssa = f"%{self.function_counter}"
            self.function_counter += 1
            mlir_code.append(f"{self.indent()}{zero} = arith.constant 0 : index")
            mlir_code.append(
                f"{self.indent()}{ascending_ssa} = arith.cmpi sgt, {step}, {zero} : index"
            )
            cmp_pred = "slt"
        self._ssa_types[step] = 'index'

        header_block = self._new_block_label()
        body_block = self._new_block_label()
        end_block = self._new_block_label()

        carried_types = [
            self.symbol_table[v]['mlir_type']
            for v in loop_carried_vars
            if v in self.symbol_table
        ]
        entry_ssas = [
            self.symbol_table[v]['ssa_name']
            for v in loop_carried_vars
            if v in self.symbol_table
        ]
        mlir_code.append(
            f"{self.indent()}cf.br ^{header_block}"
            f"{self._cf_successor_operands([lb] + entry_ssas, ['index'] + carried_types)}"
        )

        def _block_args() -> tuple[str, str, List[str]]:
            iv_arg = f"%{self.function_counter}"
            self.function_counter += 1
            self._ssa_types[iv_arg] = 'index'
            args = [f"{iv_arg}: index"]
            names: List[str] = []
            for var_name in loop_carried_vars:
                if var_name not in self.symbol_table:
                    continue
                arg = f"%{self.function_counter}"
                self.function_counter += 1
                ty = self.symbol_table[var_name]['mlir_type']
                self._ssa_types[arg] = ty
                args.append(f"{arg}: {ty}")
                names.append(var_name)
                self.symbol_table[var_name] = {
                    **self.symbol_table[var_name],
                    'ssa_name': arg,
                }
            return iv_arg, ', '.join(args), names

        # Header: iv < ub ?
        header_iv, header_args, _ = _block_args()
        mlir_code.append(f"{self.indent()}^{header_block}({header_args}):")
        cond = f"%{self.function_counter}"
        self.function_counter += 1
        mlir_code.append(f"{self.indent()}{cond} = arith.cmpi {cmp_pred}, {header_iv}, {ub} : index")
        if ascending_ssa is not None:
            desc = f"%{self.function_counter}"
            self.function_counter += 1
            picked = f"%{self.function_counter}"
            self.function_counter += 1
            mlir_code.append(
                f"{self.indent()}{desc} = arith.cmpi sgt, {header_iv}, {ub} : index"
            )
            mlir_code.append(
                f"{self.indent()}{picked} = arith.select {ascending_ssa}, {cond}, {desc} : i1"
            )
            cond = picked
        edge_ssas = [header_iv] + [
            self.symbol_table[v]['ssa_name']
            for v in loop_carried_vars
            if v in self.symbol_table
        ]
        succ = self._cf_successor_operands(edge_ssas, ['index'] + carried_types)
        mlir_code.append(
            f"{self.indent()}cf.cond_br {cond}, ^{body_block}{succ}, ^{end_block}{succ}"
        )

        # Body
        body_iv, body_args, _ = _block_args()
        mlir_code.append(f"{self.indent()}^{body_block}({body_args}):")
        self.indent_level += 1
        self.symbol_table[for_stmt.variable] = {
            'type': 'variable',
            'mlir_type': 'index',
            'ssa_name': body_iv,
        }
        self._loop_stack.append({
            "region": "cf",
            "header": header_block,
            "end": end_block,
            "carried": list(loop_carried_vars),
            "iv_ssa": body_iv,
            "iv_step": step,
        })
        try:
            body_mlir = self.generate_block(for_stmt.body)
        finally:
            self._loop_stack.pop()
        if body_mlir.strip():
            mlir_code.append(body_mlir)

        if not self._block_has_terminator(body_mlir):
            next_iv = f"%{self.function_counter}"
            self.function_counter += 1
            mlir_code.append(f"{self.indent()}{next_iv} = arith.addi {body_iv}, {step} : index")
            latch_ssas = [next_iv] + [
                self.symbol_table[v]['ssa_name']
                for v in loop_carried_vars
                if v in self.symbol_table
            ]
            mlir_code.append(
                f"{self.indent()}cf.br ^{header_block}"
                f"{self._cf_successor_operands(latch_ssas, ['index'] + carried_types)}"
            )
        self.indent_level -= 1

        # Exit
        _end_iv, end_args, _ = _block_args()
        mlir_code.append(f"{self.indent()}^{end_block}({end_args}):")
        return "\n".join(mlir_code)

    def generate_for(self, for_stmt: ForStatement) -> str:
        mlir_code = []

        vectorized = self._try_vectorize_elementwise_for(for_stmt)
        if vectorized is not None:
            return vectorized

        step_value = self._constant_step(for_stmt)
        needs_cf = (
            step_value is None
            or step_value <= 0
            or self._needs_cf_loop_lowering(for_stmt.body)
        )
        # Parallel regions cannot hold cf blocks; fall back to sequential cf.
        if for_stmt.is_parallel and needs_cf:
            if self.inside_scf_for:
                raise NotImplementedError(
                    "nested `for` needing cf lowering inside an scf region "
                    "is not supported; use the C backend (--c)"
                )
            return self._generate_cf_for(for_stmt, step_value)

        if not for_stmt.is_parallel:
            # scf.for only accepts a positive step, so anything else (and any
            # body needing its own blocks) takes the cf lowering.
            if needs_cf:
                if self.inside_scf_for:
                    raise NotImplementedError(
                        "this `for` loop needs cf lowering but sits inside an "
                        "scf region; use the C backend (--c)"
                    )
                return self._generate_cf_for(for_stmt, step_value)

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
            mlir_code.append(f"{self.indent()}{step_ssa} = arith.constant {step_value if step_value is not None else 1} : index")
            
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
            
            self._loop_stack.append({"region": "scf"})
            try:
                body_mlir = self.generate_block(for_stmt.body)
            finally:
                self._loop_stack.pop()
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
            mlir_code.append(f"{self.indent()}{step_idx} = arith.constant {step_value if step_value is not None else 1} : index")

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
                
                self._loop_stack.append({"region": "scf"})
                try:
                    body_mlir = self.generate_block(for_stmt.body)
                finally:
                    self._loop_stack.pop()
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
                
                self._loop_stack.append({"region": "scf"})
                try:
                    body_mlir = self.generate_block(for_stmt.body)
                finally:
                    self._loop_stack.pop()
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
                # Module consts/statics and alloca-backed mut locals are
                # memory-backed — not SSA values — so they cannot be threaded
                # through iter_args / cf block arguments.
                if self.symbol_table[var_name].get("is_module_global"):
                    continue
                if self.symbol_table[var_name].get("alloca_ptr"):
                    continue
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
            handler_map = {effect: handlers[0] for effect in effects}
        elif len(handlers) == len(effects):
            handler_map = {effect: handler for effect, handler in zip(effects, handlers)}
        else:
            raise ValueError(f"handle expects 1 handler or the same count as effects; got {len(effects)} effects and {len(handlers)} handlers")
        curr.update(handler_map)

        lines: List[str] = []
        restores: List[tuple[str, str]] = []
        # Save the current handler pointer and install the capability vtable
        # for each handled effect (mirrors the C backend's save/install pair).
        for effect_name, handler_name in handler_map.items():
            cap = self._capabilities.get(handler_name)
            if effect_name not in self._effects or cap is None or effect_name not in cap.effects:
                continue
            vt_ssa = f"%{self.function_counter}"
            self.function_counter += 1
            lines.append(f"{self.indent()}{vt_ssa} = llvm.mlir.addressof @_{handler_name}_{effect_name}_vtable : !llvm.ptr")
            cur_ssa = f"%{self.function_counter}"
            self.function_counter += 1
            lines.append(f"{self.indent()}{cur_ssa} = llvm.mlir.addressof @_current_{effect_name}_handler : !llvm.ptr")
            prev_ssa = f"%{self.function_counter}"
            self.function_counter += 1
            lines.append(f"{self.indent()}{prev_ssa} = llvm.load {cur_ssa} : !llvm.ptr -> !llvm.ptr")
            lines.append(f"{self.indent()}llvm.store {vt_ssa}, {cur_ssa} : !llvm.ptr, !llvm.ptr")
            restores.append((prev_ssa, cur_ssa))

        self._effect_handler_stack.append(curr)
        try:
            body_mlir = self.generate_block(handle_stmt.body)
        finally:
            self._effect_handler_stack.pop()
        if body_mlir.strip():
            lines.append(body_mlir)

        # Restore previous handlers in reverse order. Skip when the body ended
        # in a terminator; ops after a terminator are invalid MLIR and the
        # restore would be dead code anyway.
        if not self._block_has_terminator(body_mlir):
            for prev_ssa, cur_ssa in reversed(restores):
                lines.append(f"{self.indent()}llvm.store {prev_ssa}, {cur_ssa} : !llvm.ptr, !llvm.ptr")
        return "\n".join(lines)

    def generate_match(self, match_stmt: 'MatchStatement') -> str:
        # Always use SCF match as it supports struct destructuring
        return self._generate_scf_match(match_stmt)

    def _generate_scf_match(self, match_stmt: 'MatchStatement') -> str:
        """Generate match using control flow (cf) dialect for maximum flexibility."""
        mlir_code = []
        val_ssa, val_ops = self.generate_expression(match_stmt.value)
        mlir_code.extend(val_ops)
        val_type = self.get_expression_type(match_stmt.value)

        # Generate labels for each case and the end
        case_labels = []
        next_case_labels = []
        for i in range(len(match_stmt.cases)):
            case_labels.append(self._new_block_label())
            next_case_labels.append(self._new_block_label())

        end_label = self._new_block_label()

        # Locals written by any arm must be merged at the join point, or the
        # SSA name bound inside one arm leaks out and fails dominance.
        arms_terminate = bool(match_stmt.cases) and all(
            self._block_has_return(c.body) for c in match_stmt.cases
        )
        if match_stmt.default_case is not None:
            arms_terminate = arms_terminate and self._block_has_return(
                match_stmt.default_case
            )
        else:
            arms_terminate = False  # fallthrough path exists via final_next

        merged_vars: List[str] = []
        if not arms_terminate:
            for block in [c.body for c in match_stmt.cases] + (
                [match_stmt.default_case] if match_stmt.default_case else []
            ):
                for name in self._assigned_locals(block):
                    if name not in merged_vars and name in self.symbol_table:
                        merged_vars.append(name)
        merged_vars = self._filter_ssa_mergeable(merged_vars)
        entry_ssas = {v: self.symbol_table[v]['ssa_name'] for v in merged_vars}
        merged_types = [self.symbol_table[v]['mlir_type'] for v in merged_vars]

        def _restore_entry_bindings() -> None:
            for v in merged_vars:
                self.symbol_table[v]['ssa_name'] = entry_ssas[v]

        def _end_edge() -> str:
            if not merged_vars:
                return ""
            ssas = [self.symbol_table[v]['ssa_name'] for v in merged_vars]
            return self._cf_successor_operands(ssas, merged_types)

        def _entry_edge() -> str:
            if not merged_vars:
                return ""
            return self._cf_successor_operands(
                [entry_ssas[v] for v in merged_vars], merged_types
            )

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
                    
                    # Create temp variable for val_ssa to allow FieldAccess reuse.
                    # flow_type is required: without it _determine_field_type
                    # gives up and every binding lowers to `constant 0`.
                    temp_var_name = f"__match_input_{self.function_counter}"
                    self.symbol_table[temp_var_name] = {
                        'type': 'variable',
                        'ssa_name': val_ssa,
                        'mlir_type': val_type,
                        'flow_type': Type(struct_pattern.struct_name),
                    }
                    
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
            elif isinstance(case.pattern, ListPattern):
                # Array destructuring: check literal elements, bind the rest.
                from flow.parser import Literal as LiteralExpr, Variable as Var

                arr_temp = f"__match_arr_{self.function_counter}"
                self.symbol_table[arr_temp] = {
                    'ssa_name': val_ssa, 'mlir_type': val_type, 'type': 'variable'
                }

                elem_type = None
                for elem in case.pattern.elements:
                    if isinstance(elem, LiteralExpr):
                        elem_type = elem.type
                        break

                literal_conds: List[str] = []
                for idx, elem in enumerate(case.pattern.elements):
                    if isinstance(elem, LiteralExpr):
                        lit_type = elem_type or elem.type
                        elem_lit = elem
                        if elem.type.name != "string" and lit_type is not None:
                            elem_lit = LiteralExpr(elem.value, lit_type)
                        access = ArrayAccess(Variable(arr_temp), Literal(idx, Type("i32")))
                        access_ssa, access_ops = self.generate_array_access(access)
                        mlir_code.extend(access_ops)
                        lit_ssa, lit_ops = self.generate_literal(elem_lit)
                        mlir_code.extend(lit_ops)
                        acc_ty = self.get_expression_type(access)
                        c1 = f"%{self.function_counter}"
                        self.function_counter += 1
                        if "f" in acc_ty:
                            mlir_code.append(
                                f"{self.indent()}{c1} = arith.cmpf oeq, {access_ssa}, {lit_ssa} : {acc_ty}"
                            )
                        else:
                            mlir_code.append(
                                f"{self.indent()}{c1} = arith.cmpi eq, {access_ssa}, {lit_ssa} : {acc_ty}"
                            )
                        literal_conds.append(c1)
                    elif isinstance(elem, Var) and elem.name != "_":
                        access = ArrayAccess(Variable(arr_temp), Literal(idx, Type("i32")))
                        access_ssa, access_ops = self.generate_array_access(access)
                        binding_ops.extend(access_ops)
                        self.symbol_table[elem.name] = {
                            'ssa_name': access_ssa,
                            'mlir_type': self.get_expression_type(access),
                            'flow_type': elem_type or Type("i32"),
                            'type': 'variable'
                        }

                if literal_conds:
                    cond_acc = literal_conds[0]
                    for ci in literal_conds[1:]:
                        and_ssa = f"%{self.function_counter}"
                        self.function_counter += 1
                        mlir_code.append(
                            f"{self.indent()}{and_ssa} = arith.andi {cond_acc}, {ci} : i1"
                        )
                        cond_acc = and_ssa
                    cond_ssa = cond_acc
                else:
                    cond_ssa = f"%{self.function_counter}"
                    self.function_counter += 1
                    mlir_code.append(f"{self.indent()}{cond_ssa} = arith.constant 1 : i1")
                if saved_locals is None:
                    saved_locals = self.symbol_table.copy()
            else:
                # Path/const pattern (including Enum_Variant tags). When the
                # scrutinee is an enum/struct ADT, compare against `.tag`.
                compare_ssa = val_ssa
                compare_ty = val_type
                pattern_name = getattr(case.pattern, "name", None)
                owner = None
                if isinstance(pattern_name, str):
                    owner = getattr(self, "_enum_variant_owner", {}).get(pattern_name)
                if owner and owner in getattr(self, "_enums", {}):
                    # Match on enum value → extract tag field (mirrors C backend).
                    flow_ty = self._flow_type_of_expr(match_stmt.value)
                    if flow_ty is not None and flow_ty.name == owner:
                        tag_access = FieldAccess(
                            match_stmt.value
                            if isinstance(match_stmt.value, Variable)
                            else Variable("__match_enum_tmp"),
                            "tag",
                        )
                        if not isinstance(match_stmt.value, Variable):
                            tmp = f"__match_enum_tmp_{self.function_counter}"
                            self.function_counter += 1
                            self.symbol_table[tmp] = {
                                "type": "variable",
                                "ssa_name": val_ssa,
                                "mlir_type": val_type,
                                "flow_type": Type(owner),
                            }
                            tag_access = FieldAccess(Variable(tmp), "tag")
                        compare_ssa, tag_ops = self.generate_field_access(tag_access)
                        mlir_code.extend(tag_ops)
                        compare_ty = "i32"
                    elif flow_ty is not None and flow_ty.name == "i32":
                        # Already matching on `.tag`
                        compare_ty = "i32"

                pattern_ssa, pattern_ops = self.generate_expression(case.pattern)
                mlir_code.extend(pattern_ops)

                cond_ssa = f"%{self.function_counter}"
                self.function_counter += 1
                if "ptr" in compare_ty:
                    mlir_code.append(
                        f"{self.indent()}{cond_ssa} = llvm.icmp \"eq\" "
                        f"{compare_ssa}, {pattern_ssa} : {compare_ty}"
                    )
                elif "f" in compare_ty and "i" not in compare_ty[:1]:
                    mlir_code.append(
                        f"{self.indent()}{cond_ssa} = arith.cmpf oeq, "
                        f"{compare_ssa}, {pattern_ssa} : {compare_ty}"
                    )
                else:
                    mlir_code.append(
                        f"{self.indent()}{cond_ssa} = arith.cmpi eq, "
                        f"{compare_ssa}, {pattern_ssa} : {compare_ty}"
                    ) 
            # Branch to case body or next case
            mlir_code.append(f"{self.indent()}cf.cond_br {cond_ssa}, ^{case_label}, ^{next_label}")
            
            # Generate case body block
            mlir_code.append(f"^{case_label}:")
            self.indent_level += 1
            
            if binding_ops:
                mlir_code.extend(binding_ops)

            # Each arm starts from the pre-match bindings; assignments in a
            # previous arm must not be visible here.
            _restore_entry_bindings()
            body = self.generate_block(case.body)
            if body.strip():
                mlir_code.append(body)

            # Skip cf.br after return/terminator (same guard as generate_if):
            # two terminators in one block is invalid MLIR.
            if not self._block_has_terminator(body):
                mlir_code.append(f"{self.indent()}cf.br ^{end_label}{_end_edge()}")

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
            _restore_entry_bindings()
            default_body = self.generate_block(match_stmt.default_case)
            if default_body.strip():
                mlir_code.append(default_body)
            if not self._block_has_terminator(default_body):
                mlir_code.append(f"{self.indent()}cf.br ^{end_label}{_end_edge()}")
            self.indent_level -= 1
        else:
            # If no default, just make the last next label jump to end
            mlir_code.append(f"^{final_next_label}:")
            mlir_code.append(f"{self.indent()}cf.br ^{end_label}{_entry_edge()}")

        # End block. When every arm already returned nothing branches here, so
        # the block would have no terminator; llvm.unreachable keeps it valid.
        # Otherwise the parent generate_block appends the statements that
        # follow the match into this block.
        if merged_vars:
            end_args = []
            for ty in merged_types:
                arg = f"%{self.function_counter}"
                self.function_counter += 1
                end_args.append((arg, ty))
            mlir_code.append(
                f"^{end_label}({', '.join(f'{a}: {t}' for a, t in end_args)}):"
            )
            for var_name, (arg, ty) in zip(merged_vars, end_args):
                self.symbol_table[var_name]['ssa_name'] = arg
                self._ssa_types[arg] = ty
        else:
            mlir_code.append(f"^{end_label}:")
        if arms_terminate:
            mlir_code.append(f"{self.indent()}llvm.unreachable")

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
        elif isinstance(expr, RecordUpdate):
            return self.generate_record_update(expr)
        elif isinstance(expr, Lambda):
            return self.generate_lambda(expr)
        else:
            raise NotImplementedError(
                f"MLIR backend does not support expression type "
                f"{type(expr).__name__}; use the C backend (--c)"
            )

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

        # Index/float casts go through i64
        if from_type == "index" and to_type in ["f32", "f64"]:
            mid = f"%{self.function_counter}"
            self.function_counter += 1
            self._ssa_types[mid] = "i64"
            self._ssa_types[cast_name] = to_type
            return cast_name, [
                f"{self.indent()}{mid} = arith.index_cast {value_ssa} : index to i64",
                f"{self.indent()}{cast_name} = arith.sitofp {mid} : i64 to {to_type}",
            ]
        if from_type in ["f32", "f64"] and to_type == "index":
            mid = f"%{self.function_counter}"
            self.function_counter += 1
            self._ssa_types[mid] = "i64"
            self._ssa_types[cast_name] = to_type
            return cast_name, [
                f"{self.indent()}{mid} = arith.fptosi {value_ssa} : {from_type} to i64",
                f"{self.indent()}{cast_name} = arith.index_cast {mid} : i64 to index",
            ]

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
                # Prefer zero-extend for Flow unsigned origins (now lowered as iN).
                unsigned = _is_unsigned(from_type) or value_ssa in self._ssa_unsigned
                ext_op = "arith.extui" if unsigned else "arith.extsi"
                self._ssa_types[cast_name] = to_type
                if unsigned:
                    self._ssa_unsigned.add(cast_name)
                return cast_name, [f"{self.indent()}{cast_name} = {ext_op} {value_ssa} : {from_type} to {to_type}"]
            self._ssa_types[cast_name] = to_type
            if value_ssa in self._ssa_unsigned or _is_unsigned(to_type):
                self._ssa_unsigned.add(cast_name)
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

        # Array / memref decay to a raw pointer. Must produce a *new* SSA —
        # reusing the memref value and retagging it as !llvm.ptr breaks later
        # memref.load/store (snake_gfx: let p: ptr<i32> = snake_x).
        if to_type == "!llvm.ptr" and from_type.startswith("memref<"):
            idx = f"%{self.function_counter}"
            self.function_counter += 1
            idx64 = f"%{self.function_counter}"
            self.function_counter += 1
            ptr = f"%{self.function_counter}"
            self.function_counter += 1
            self._ssa_types[ptr] = "!llvm.ptr"
            return ptr, [
                f"{self.indent()}{idx} = memref.extract_aligned_pointer_as_index "
                f"{value_ssa} : {from_type} -> index",
                f"{self.indent()}{idx64} = arith.index_cast {idx} : index to i64",
                f"{self.indent()}{ptr} = llvm.inttoptr {idx64} : i64 to !llvm.ptr",
            ]

        # Pointer ↔ integer (null checks like `(p as i64) == 0`).
        if from_type == "!llvm.ptr" and to_type.startswith("i"):
            self._ssa_types[cast_name] = to_type
            return cast_name, [
                f"{self.indent()}{cast_name} = llvm.ptrtoint {value_ssa} "
                f": !llvm.ptr to {to_type}"
            ]
        if to_type == "!llvm.ptr" and from_type.startswith("i"):
            self._ssa_types[cast_name] = to_type
            return cast_name, [
                f"{self.indent()}{cast_name} = llvm.inttoptr {value_ssa} "
                f": {from_type} to !llvm.ptr"
            ]

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
        elif (
            str(literal.value).lower() == 'null'
            or (mlir_type == '!llvm.ptr' and str(literal.value).lower() in ('null', '0'))
        ):
            # MLIR has no `arith.constant null` — use llvm.mlir.zero (#223).
            mlir_type = '!llvm.ptr'
            line = f"{self.indent()}{ssa_name} = llvm.mlir.zero : !llvm.ptr"
        else:
            numeric = self._format_mlir_numeric(str(literal.value), mlir_type)
            line = f"{self.indent()}{ssa_name} = arith.constant {numeric} : {mlir_type}"
        self._ssa_types[ssa_name] = mlir_type
        return ssa_name, [line]
    
    def _emit_function_as_ptr(self, name: str, info: dict) -> tuple[str, List[str]]:
        """Materialize a function name used as a value (thinker hooks, etc.).

        ``llvm.mlir.addressof`` cannot reference ``func.func`` symbols; match
        capability vtables: ``func.constant`` + unrealized cast to ``!llvm.ptr``.
        """
        params = info.get("parameters") or []
        param_types = [self.flow_type_to_mlir(p.type) for p in params]
        ret = self.flow_type_to_mlir(info["return_type"])
        fn_type = f"({', '.join(param_types)}) -> {ret}"
        fn_ssa = f"%{self.function_counter}"
        self.function_counter += 1
        ptr_ssa = f"%{self.function_counter}"
        self.function_counter += 1
        ops = [
            f"{self.indent()}{fn_ssa} = func.constant @{name} : {fn_type}",
            (
                f"{self.indent()}{ptr_ssa} = builtin.unrealized_conversion_cast "
                f"{fn_ssa} : {fn_type} to !llvm.ptr"
            ),
        ]
        self._ssa_types[fn_ssa] = fn_type
        self._ssa_types[ptr_ssa] = "!llvm.ptr"
        return ptr_ssa, ops

    def generate_variable(self, variable: Variable) -> tuple[str, List[str]]:
        if variable.name in self.symbol_table:
            var_info = self.symbol_table[variable.name]
            if var_info.get("type") == "function":
                return self._emit_function_as_ptr(variable.name, var_info)
            mlir_type = var_info.get("mlir_type")
            # Enum tag discriminators are known constants — avoid a load.
            if var_info.get("is_enum_tag") and "enum_tag_value" in var_info:
                ssa = f"%{self.function_counter}"
                self.function_counter += 1
                val = var_info["enum_tag_value"]
                line = f"{self.indent()}{ssa} = arith.constant {val} : i32"
                self._ssa_types[ssa] = "i32"
                return ssa, [line]
            if var_info.get("is_module_global") and mlir_type:
                return self._load_module_global(variable.name, mlir_type)
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

    def _load_module_global(self, name: str, mlir_type: str) -> tuple[str, List[str]]:
        """Load a module-scope const/static via llvm.mlir.addressof + llvm.load."""
        ops: List[str] = []
        ptr = f"%{self.function_counter}"
        self.function_counter += 1
        ops.append(f"{self.indent()}{ptr} = llvm.mlir.addressof @{name} : !llvm.ptr")
        self._ssa_types[ptr] = "!llvm.ptr"
        info = self.symbol_table.get(name) or {}
        llvm_array_ty = info.get("llvm_array_type")
        if llvm_array_ty:
            # Global *is* the array storage; addressof is the base pointer for GEP.
            self._llvm_array_types[ptr] = llvm_array_ty
            self._llvm_array_types[name] = llvm_array_ty
            return ptr, ops
        if info.get("is_string_global"):
            # addressof of the i8 array is the string pointer (no load).
            return ptr, ops
        val = f"%{self.function_counter}"
        self.function_counter += 1
        ops.append(f"{self.indent()}{val} = llvm.load {ptr} : !llvm.ptr -> {mlir_type}")
        self._ssa_types[val] = mlir_type
        return val, ops

    def _store_module_global(self, name: str, mlir_type: str, value_ssa: str) -> List[str]:
        """Store into a module-scope static."""
        ops: List[str] = []
        ptr = f"%{self.function_counter}"
        self.function_counter += 1
        ops.append(f"{self.indent()}{ptr} = llvm.mlir.addressof @{name} : !llvm.ptr")
        self._ssa_types[ptr] = "!llvm.ptr"
        ops.append(f"{self.indent()}llvm.store {value_ssa}, {ptr} : {mlir_type}, !llvm.ptr")
        return ops

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
        # Pointer equality / null checks stay on !llvm.ptr (use llvm.icmp).
        if left_ty == '!llvm.ptr' or right_ty == '!llvm.ptr':
            return '!llvm.ptr'
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
            elif operand_type == '!llvm.ptr':
                # arith.cmpi does not accept !llvm.ptr — use llvm.icmp (#223 companions).
                icmp = {
                    'eq': 'eq', 'ne': 'ne',
                    'slt': 'ult', 'sle': 'ule',
                    'sgt': 'ugt', 'sge': 'uge',
                }.get(pred, pred)
                op_text = f'llvm.icmp "{icmp}" {left_ssa}, {right_ssa} : !llvm.ptr'
            else:
                op_text = f"arith.cmpi {pred}, {left_ssa}, {right_ssa} : {operand_type}"
        elif bin_op.operator == '&&' or bin_op.operator == 'and':
            op_text = f"arith.andi {left_ssa}, {right_ssa} : i1"
        elif bin_op.operator == '||' or bin_op.operator == 'or':
            op_text = f"arith.ori {left_ssa}, {right_ssa} : i1"
        elif bin_op.operator == '&':
            # Bitwise (not boolean) — Doom-scale MLIR needs these (#221 follow-up).
            op_text = f"arith.andi {left_ssa}, {right_ssa} : {operand_type}"
        elif bin_op.operator == '|':
            op_text = f"arith.ori {left_ssa}, {right_ssa} : {operand_type}"
        elif bin_op.operator == '^':
            op_text = f"arith.xori {left_ssa}, {right_ssa} : {operand_type}"
        elif bin_op.operator == '<<':
            op_text = f"arith.shli {left_ssa}, {right_ssa} : {operand_type}"
        elif bin_op.operator == '>>':
            # Flow uN lowers to iN; arithmetic right-shift matches C signed >> on i32.
            op_text = f"arith.shrsi {left_ssa}, {right_ssa} : {operand_type}"
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
        if un_op.operator == '&':
            return self._generate_address_of(un_op.operand)
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
                ops.append(f"{self.indent()}{cast_name} = arith.cmpi ne, {operand_ssa}, {zero_ssa} : {ty}")
                operand_ssa = cast_name
                ty = 'i1'
            
            ops.append(f"{self.indent()}{c1} = arith.constant 1 : i1")
            ops.append(f"{self.indent()}{ssa_name} = arith.xori {operand_ssa}, {c1} : i1")
            self._ssa_types[ssa_name] = "i1"
            return ssa_name, ops
        else:
            return f"// Unsupported unary operator: '{un_op.operator}' (type: {type(un_op.operator)})", operand_ops

    def _generate_address_of(self, operand: Expression) -> tuple[str, List[str]]:
        """Lower &expr to an !llvm.ptr SSA value.

        Variables become alloca-backed on first address-of, so writes through
        the pointer stay visible to later reads (generate_variable and
        generate_assignment both prefer alloca_ptr once it is set).

        Field / array lvalues (``&j[0].buttons[0]``) use GEP into the real
        object — never load+spill, which would give M_BindVariable a temp.
        """
        if isinstance(operand, Variable) and operand.name in self.symbol_table:
            var_info = self.symbol_table[operand.name]
            mlir_type = var_info.get('mlir_type')
            ptr = var_info.get('alloca_ptr')
            ops: List[str] = []
            if not ptr and mlir_type:
                value_ssa = var_info.get('ssa_name')
                if value_ssa:
                    ptr, ops = self._emit_alloca_store(value_ssa, mlir_type)
                    var_info['alloca_ptr'] = ptr
            if ptr:
                self._ssa_types[ptr] = '!llvm.ptr'
                return ptr, ops
        lval = self._address_of_lvalue(operand)
        if lval is not None:
            ptr, ops = lval
            self._ssa_types[ptr] = '!llvm.ptr'
            return ptr, ops
        # Fallback: spill the value of the expression to a fresh slot.
        operand_ssa, operand_ops = self.generate_expression(operand)
        ty = self._ssa_types.get(operand_ssa) or self.get_expression_type(operand)
        ptr, spill_ops = self._emit_alloca_store(operand_ssa, ty)
        self._ssa_types[ptr] = '!llvm.ptr'
        return ptr, operand_ops + spill_ops

    def _address_of_lvalue(self, expr: Expression) -> Optional[tuple]:
        """Address of a field or array-element lvalue as ``!llvm.ptr``.

        Returns ``(ptr_ssa, ops)`` or None when the shape is not addressable.
        """
        if isinstance(expr, FieldAccess):
            parent = self._address_of_struct_lvalue(expr.object)
            if parent is None:
                return None
            parent_ptr, parent_ops, parent_struct = parent
            decl = self._get_struct_decl(parent_struct)
            llvm_struct = self._struct_llvm_type(parent_struct)
            if not decl or not llvm_struct:
                return None
            field_names = [f.name for f in decl.fields]
            if expr.field not in field_names:
                return None
            idx = field_names.index(expr.field)
            ops = list(parent_ops)
            gep = f"%{self.function_counter}"
            self.function_counter += 1
            ops.append(
                f"{self.indent()}{gep} = llvm.getelementptr {parent_ptr}[0, {idx}] "
                f": (!llvm.ptr) -> !llvm.ptr, {llvm_struct}"
            )
            self._ssa_types[gep] = "!llvm.ptr"
            field_ty = self._determine_field_type(expr)
            if field_ty is not None and self._is_array_flow_type(field_ty):
                arr_ty = self._llvm_array_type_from_flow(field_ty)
                if arr_ty:
                    self._llvm_array_types[gep] = arr_ty
            return gep, ops

        if isinstance(expr, ArrayAccess):
            arr_ty = self._flow_type_of_expr(expr.array)
            index_ssa, index_ops = self.generate_expression(expr.index)
            index_type = self._ssa_types.get(index_ssa, "i32")
            if isinstance(expr.index, Variable) and expr.index.name in self.symbol_table:
                index_type = self.symbol_table[expr.index.name].get("mlir_type", index_type)

            # ptr[i] → GEP (element address); covers &j[0] for ptr-to-struct.
            if self._is_pointer_flow_type(arr_ty):
                array_result = self.generate_expression(expr.array)
                if not array_result:
                    return None
                array_ssa, array_ops = array_result
                pointee = self._pointee_struct_type(arr_ty)
                llvm_elem = None
                if pointee is not None and pointee.name in self.struct_layouts:
                    llvm_elem = self._struct_llvm_type(pointee.name) or self.flow_type_to_mlir(
                        pointee
                    )
                else:
                    elem = getattr(arr_ty, "element_type", None)
                    if elem is not None:
                        llvm_elem = self.flow_type_to_mlir(elem)
                if not llvm_elem:
                    return None
                ops = list(array_ops) + list(index_ops)
                gep, gep_ops = self._emit_ptr_index_gep(
                    array_ssa, index_ssa, index_type, llvm_elem
                )
                ops.extend(gep_ops)
                return gep, ops

            # array-field / llvm.array local: &buttons[i]
            base = None
            ops: List[str] = []
            if isinstance(expr.array, (FieldAccess, ArrayAccess)):
                base = self._address_of_lvalue(expr.array)
                if base is None:
                    return None
                array_ssa, base_ops = base
                ops.extend(base_ops)
            else:
                array_result = self.generate_expression(expr.array)
                if not array_result:
                    return None
                array_ssa, array_ops = array_result
                ops.extend(array_ops)

            ops.extend(index_ops)
            llvm_array_ty = self._llvm_array_type_for(expr.array, array_ssa)
            if llvm_array_ty is not None:
                gep, gep_ops = self._emit_llvm_array_index_gep(
                    array_ssa, index_ssa, index_type, llvm_array_ty
                )
                ops.extend(gep_ops)
                return gep, ops
            # Local memref arrays: decay via aligned-pointer extract for &arr[i].
            ssa_ty = self._ssa_types.get(array_ssa, "")
            if ssa_ty.startswith("memref"):
                elem_ty = self._memref_element_type(ssa_ty) or "i8"
                idx64, cast_ops = self._index_to_i64(index_ssa, index_type)
                ops.extend(cast_ops)
                base_idx = f"%{self.function_counter}"
                self.function_counter += 1
                ops.append(
                    f"{self.indent()}{base_idx} = memref.extract_aligned_pointer_as_index "
                    f"{array_ssa} : {ssa_ty} -> index"
                )
                base_i64 = f"%{self.function_counter}"
                self.function_counter += 1
                ops.append(
                    f"{self.indent()}{base_i64} = arith.index_cast {base_idx} : index to i64"
                )
                # Scale index by element size when element is wider than i8.
                elem_size = 1
                if elem_ty in ("i16", "u16"):
                    elem_size = 2
                elif elem_ty in ("i32", "u32", "f32"):
                    elem_size = 4
                elif elem_ty in ("i64", "u64", "f64", "!llvm.ptr"):
                    elem_size = 8
                byte_off = idx64
                if elem_size != 1:
                    sz = f"%{self.function_counter}"
                    self.function_counter += 1
                    ops.append(
                        f"{self.indent()}{sz} = arith.constant {elem_size} : i64"
                    )
                    byte_off = f"%{self.function_counter}"
                    self.function_counter += 1
                    ops.append(
                        f"{self.indent()}{byte_off} = arith.muli {idx64}, {sz} : i64"
                    )
                addr_i64 = f"%{self.function_counter}"
                self.function_counter += 1
                ops.append(
                    f"{self.indent()}{addr_i64} = arith.addi {base_i64}, {byte_off} : i64"
                )
                ptr = f"%{self.function_counter}"
                self.function_counter += 1
                ops.append(
                    f"{self.indent()}{ptr} = llvm.inttoptr {addr_i64} : i64 to !llvm.ptr"
                )
                self._ssa_types[ptr] = "!llvm.ptr"
                return ptr, ops
            return None

        return None

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
            obj_mlir = var_info.get("mlir_type") if var_info else None
            if not obj_mlir and flow_type:
                obj_mlir = self.flow_type_to_mlir(flow_type)
            if (
                var_info
                and obj_mlir
                and obj_mlir.startswith("!llvm.struct")
                and not self._is_tensor_struct(obj_mlir)
                and (
                    obj_ssa in self._composite_call_results
                    or obj_ssa.startswith("%arg")
                )
            ):
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

        # Addressable struct objects (ptr, ptr[i], nested fields): GEP to field.
        # Array fields decay to a pointer to the embedded !llvm.array (C-like).
        addr = self._address_of_struct_lvalue(field_access.object)
        if addr is None:
            ptr_base = self._field_pointer_base(field_access.object, obj_ssa)
            if ptr_base is not None:
                base_ptr, struct_name = ptr_base
                addr = (base_ptr, [], struct_name)
        if addr is not None:
            base_ptr, base_ops, struct_name = addr
            ops.extend(base_ops)
            llvm_struct = self._struct_llvm_type(struct_name)
            decl = self._get_struct_decl(struct_name)
            if llvm_struct and decl:
                field_names = [f.name for f in decl.fields]
                if field_access.field in field_names:
                    idx = field_names.index(field_access.field)
                    gep = f"%{self.function_counter}"
                    self.function_counter += 1
                    ops.append(
                        f"{self.indent()}{gep} = llvm.getelementptr {base_ptr}[0, {idx}] "
                        f": (!llvm.ptr) -> !llvm.ptr, {llvm_struct}"
                    )
                    self._ssa_types[gep] = '!llvm.ptr'
                    if self._is_array_flow_type(field_type):
                        arr_ty = self._llvm_array_type_from_flow(field_type)
                        if arr_ty:
                            self._llvm_array_types[gep] = arr_ty
                        return gep, ops
                    load = f"%{self.function_counter}"
                    self.function_counter += 1
                    field_ty = self.flow_type_to_mlir(field_type)
                    ops.append(
                        f"{self.indent()}{load} = llvm.load {gep} : !llvm.ptr -> {field_ty}"
                    )
                    self._ssa_types[load] = field_ty
                    return load, ops

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

    def _pointee_struct_type(self, flow_type):
        """Unwrap pointer flow types (ptr_X / is_pointer) to the pointee type."""
        if flow_type is None:
            return None
        if getattr(flow_type, 'is_pointer', False) or flow_type.name.startswith('ptr_'):
            elem = getattr(flow_type, 'element_type', None)
            if elem is not None:
                return elem
            if flow_type.name.startswith('ptr_'):
                return Type(flow_type.name[4:])
        return flow_type

    def _is_pointer_flow_type(self, flow_type) -> bool:
        if flow_type is None:
            return False
        return bool(
            getattr(flow_type, 'is_pointer', False) or flow_type.name.startswith('ptr_')
        )

    def _flow_type_of_expr(self, expr) -> Optional[Type]:
        """Resolve the FLOW type of an expression, including chained postfix shapes.

        Must use isinstance checks (not hasattr(..., 'name')): FunctionCall also
        has a .name field (the callee), which is not a variable binding.
        """
        if isinstance(expr, Variable):
            return self._find_variable_type(expr.name)
        if isinstance(expr, FieldAccess):
            return self._determine_field_type(expr)
        if isinstance(expr, ArrayAccess):
            arr_ty = self._flow_type_of_expr(expr.array)
            if arr_ty is None:
                return None
            if self._is_pointer_flow_type(arr_ty):
                return self._pointee_struct_type(arr_ty)
            elem = getattr(arr_ty, 'element_type', None)
            if elem is not None:
                return elem
            return None
        if isinstance(expr, FunctionCall):
            info = self.symbol_table.get(expr.name)
            if info and info.get('type') == 'function':
                return info.get('return_type')
            return None
        if isinstance(expr, MethodCall):
            effect_call = self._method_call_as_effect_call(expr)
            if effect_call is not None:
                return self._flow_type_of_expr(effect_call)
            info = self.symbol_table.get(expr.method)
            if info and info.get('type') == 'function':
                return info.get('return_type')
            return None
        if isinstance(expr, EffectCall):
            callee = self._effect_call_callee(expr)
            name = callee if callee is not None else expr.operation
            info = self.symbol_table.get(name)
            if info:
                return info.get('return_type')
            return None
        if isinstance(expr, StructLiteral):
            return Type(expr.struct_name)
        return None

    def _field_pointer_base(self, obj_expr, obj_ssa: str):
        """(ptr_ssa, struct_name) when obj_expr is a pointer-to-struct variable."""
        if not isinstance(obj_expr, Variable):
            return None
        var_info = self.symbol_table.get(obj_expr.name)
        if not var_info:
            return None
        flow_type = var_info.get('flow_type')
        if flow_type is None:
            return None
        if not self._is_pointer_flow_type(flow_type):
            return None
        pointee = self._pointee_struct_type(flow_type)
        if pointee is None or pointee.name not in self.struct_layouts:
            return None
        base = var_info.get('ssa_name') or obj_ssa
        return base, pointee.name

    def _address_of_struct_lvalue(self, expr) -> Optional[tuple]:
        """Address of a struct-typed lvalue for chained field stores.

        Returns (ptr_ssa, ops, struct_name) or None when the shape is not an
        addressable LLVM pointer-backed struct (e.g. pure SSA values).
        Supports Variable (ptr / alloca), ArrayAccess on ptr-to-struct, and
        nested FieldAccess into struct fields — the shapes produced by
        unified postfix chaining such as bodies[0].pos.x = v.
        """
        if isinstance(expr, Variable):
            var_info = self.symbol_table.get(expr.name)
            if not var_info:
                return None
            flow_type = var_info.get('flow_type')
            if flow_type is None:
                return None
            if self._is_pointer_flow_type(flow_type):
                pointee = self._pointee_struct_type(flow_type)
                if pointee is None or pointee.name not in self.struct_layouts:
                    return None
                return var_info.get('ssa_name'), [], pointee.name
            if var_info.get('alloca_ptr') and flow_type.name in self.struct_layouts:
                return var_info['alloca_ptr'], [], flow_type.name
            return None

        if isinstance(expr, ArrayAccess):
            arr_ty = self._flow_type_of_expr(expr.array)
            array_result = self.generate_expression(expr.array)
            if not array_result:
                return None
            array_ssa, array_ops = array_result
            index_ssa, index_ops = self.generate_expression(expr.index)
            ops: List[str] = list(array_ops) + list(index_ops)
            index_type = self._ssa_types.get(index_ssa, 'i32')
            if isinstance(expr.index, Variable) and expr.index.name in self.symbol_table:
                index_type = self.symbol_table[expr.index.name].get('mlir_type', index_type)

            # array<Struct, N> lowered as !llvm.ptr to !llvm.array<N x struct>
            llvm_array_ty = self._llvm_array_type_for(expr.array, array_ssa)
            if llvm_array_ty is not None:
                elem_flow = self._flow_type_of_expr(expr)
                if elem_flow is None or elem_flow.name not in self.struct_layouts:
                    return None
                gep, gep_ops = self._emit_llvm_array_index_gep(
                    array_ssa, index_ssa, index_type, llvm_array_ty
                )
                ops.extend(gep_ops)
                return gep, ops, elem_flow.name

            if not self._is_pointer_flow_type(arr_ty):
                return None
            pointee = self._pointee_struct_type(arr_ty)
            if pointee is None or pointee.name not in self.struct_layouts:
                return None
            llvm_elem = self._struct_llvm_type(pointee.name) or self.flow_type_to_mlir(pointee)
            gep, gep_ops = self._emit_ptr_index_gep(array_ssa, index_ssa, index_type, llvm_elem)
            ops.extend(gep_ops)
            return gep, ops, pointee.name

        if isinstance(expr, FieldAccess):
            parent = self._address_of_struct_lvalue(expr.object)
            if parent is None:
                return None
            parent_ptr, parent_ops, parent_struct = parent
            decl = self._get_struct_decl(parent_struct)
            llvm_struct = self._struct_llvm_type(parent_struct)
            if not decl or not llvm_struct:
                return None
            field_names = [f.name for f in decl.fields]
            if expr.field not in field_names:
                return None
            field_ty = self._determine_field_type(expr)
            if field_ty is None or field_ty.name not in self.struct_layouts:
                return None
            idx = field_names.index(expr.field)
            ops = list(parent_ops)
            gep = f"%{self.function_counter}"
            self.function_counter += 1
            ops.append(
                f"{self.indent()}{gep} = llvm.getelementptr {parent_ptr}[0, {idx}] "
                f": (!llvm.ptr) -> !llvm.ptr, {llvm_struct}"
            )
            self._ssa_types[gep] = '!llvm.ptr'
            return gep, ops, field_ty.name

        return None

    def _determine_struct_type(self, expr):
        """Determine the struct type of an expression (including chained postfix)."""
        return self._pointee_struct_type(self._flow_type_of_expr(expr))

    def _determine_field_type(self, field_access):
        """Determine the type of a field access by walking the struct hierarchy."""
        current_type = self._flow_type_of_expr(field_access.object)
        # Pointer-to-struct objects access fields of the pointee.
        current_type = self._pointee_struct_type(current_type)

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
            # Functions are not variables — their .name colliding with Variable
            # lookup is why make().x used to resolve as i32.
            if var_info.get('type') == 'function':
                return None
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
    
    def generate_record_update(self, update: RecordUpdate) -> tuple[str, List[str]]:
        """Generate a record update: `Point { ..p, x: 3 }`.

        Evaluates the base struct, then inserts the override fields via
        `llvm.insertvalue`, yielding an updated copy.
        """
        # Determine the struct name from the base expression's Flow type.
        struct_name = None
        if isinstance(update.base, Variable):
            var_info = self.symbol_table.get(update.base.name)
            if var_info and 'flow_type' in var_info:
                struct_name = var_info['flow_type'].name
        if struct_name is None:
            base_mlir = self.get_expression_type(update.base)
            for name in self.struct_layouts:
                if self._struct_llvm_type(name) == base_mlir:
                    struct_name = name
                    break

        if not struct_name:
            # Unknown struct type; fall back to evaluating just the base.
            return self.generate_expression(update.base)

        llvm_struct = self._struct_llvm_type(struct_name)
        decl = self._get_struct_decl(struct_name)
        if not llvm_struct:
            return self.generate_expression(update.base)

        base_ssa, ops = self.generate_expression(update.base)
        agg_name = base_ssa
        override_types = {}
        if decl:
            for field in decl.fields:
                if field.name in {n for n, _ in update.updates}:
                    override_types[field.name] = self.flow_type_to_mlir(field.type)

        for name, value in update.updates:
            val_ssa, val_ops = self.generate_expression(value)
            ops.extend(val_ops)
            field_type = override_types.get(name)
            if field_type is None:
                field_type = self.get_expression_type(value)
            val_ssa, cast_ops = self._emit_cast(
                val_ssa, self.get_expression_type(value), field_type
            )
            ops.extend(cast_ops)
            idx = self._struct_field_index(struct_name, name)
            next_agg = f"%{self.function_counter}"
            self.function_counter += 1
            ops.append(
                f"{self.indent()}{next_agg} = llvm.insertvalue {val_ssa}, {agg_name}[{idx}] : {llvm_struct}"
            )
            agg_name = next_agg
        self._ssa_types[agg_name] = llvm_struct
        return agg_name, ops

    def _struct_field_index(self, struct_name: str, field_name: str) -> int:
        decl = self._get_struct_decl(struct_name)
        if decl:
            for idx, field in enumerate(decl.fields):
                if field.name == field_name:
                    return idx
        return 0

    def generate_lambda(self, lam: Lambda) -> tuple[str, List[str]]:
        """Lower a non-capturing lambda to a lifted func.func + func.constant.

        Capturing closures remain C-backend-only for now.
        """
        captures = list(getattr(lam, "captures", None) or [])
        if captures:
            raise NotImplementedError(
                f"capturing lambdas not yet supported in MLIR backend "
                f"(captures {captures}); use the C backend (--c)"
            )

        self._lambda_counter += 1
        name = f"lambda_{self._lambda_counter}"

        param_mlir = []
        for p in lam.parameters:
            pty = self.flow_type_to_mlir(p.type) if p.type else "i32"
            param_mlir.append((p.name, pty))

        ret_flow = lam.return_type or Type("i32")
        ret_mlir = self.flow_type_to_mlir(ret_flow)
        if ret_mlir == "()":
            ret_mlir = "i32"  # expression lambdas always yield a value here

        # Build lifted function body with a fresh local symbol scope for params.
        saved_table = self.symbol_table
        saved_ssa = dict(self._ssa_types)
        self.symbol_table = saved_table.copy()
        for pname, pty in param_mlir:
            arg_ssa = f"%arg_{pname}"
            self.symbol_table[pname] = {
                "type": "variable",
                "ssa_name": arg_ssa,
                "mlir_type": pty,
                "flow_type": Type(pty) if pty in ("i32", "i64", "f32", "f64", "i1") else Type("i32"),
            }
            self._ssa_types[arg_ssa] = pty

        body_lines: List[str] = []
        old_indent = self.indent_level
        self.indent_level = 1
        if isinstance(lam.body, Block):
            body_mlir = self.generate_block(lam.body)
            if body_mlir.strip():
                body_lines.append(body_mlir)
            if not self._block_has_terminator(body_mlir):
                # Implicit void/zero return
                zero = f"%{self.function_counter}"
                self.function_counter += 1
                body_lines.append(f"{self.indent()}{zero} = arith.constant 0 : {ret_mlir}")
                body_lines.append(f"{self.indent()}func.return {zero} : {ret_mlir}")
        else:
            val_ssa, val_ops = self.generate_expression(lam.body)
            body_lines.extend(val_ops)
            body_lines.append(f"{self.indent()}func.return {val_ssa} : {ret_mlir}")
        self.indent_level = old_indent
        self.symbol_table = saved_table
        self._ssa_types = saved_ssa

        sig_params = ", ".join(f"%arg_{n}: {t}" for n, t in param_mlir)
        fn_ty = (
            f"({', '.join(t for _, t in param_mlir)}) -> {ret_mlir}"
            if param_mlir
            else f"() -> {ret_mlir}"
        )
        lifted = [
            f"  func.func private @{name}({sig_params}) -> {ret_mlir} {{",
            *body_lines,
            "  }",
        ]
        self._pending_lambdas.append("\n".join(lifted))

        const_ssa = f"%{self.function_counter}"
        self.function_counter += 1
        ops = [f"{self.indent()}{const_ssa} = func.constant @{name} : {fn_ty}"]
        self._ssa_types[const_ssa] = fn_ty
        return const_ssa, ops

    def _generate_closure_call(
        self, func_call: FunctionCall, info: Dict[str, Any]
    ) -> tuple[str, List[str]]:
        """func.call_indirect through a func.constant SSA."""
        ops: List[str] = []
        arg_ssas: List[str] = []
        arg_tys: List[str] = []
        for arg in func_call.arguments:
            a_ssa, a_ops = self.generate_expression(arg)
            ops.extend(a_ops)
            a_ty = self._ssa_types.get(a_ssa) or self.get_expression_type(arg)
            arg_ssas.append(a_ssa)
            arg_tys.append(a_ty)

        fn_ty = info.get("fn_mlir_type") or info.get("mlir_type")
        # Recover return type from fn_ty string "(…) -> R"
        ret_ty = "i32"
        if isinstance(fn_ty, str) and "->" in fn_ty:
            ret_ty = fn_ty.rsplit("->", 1)[-1].strip()

        result = f"%{self.function_counter}"
        self.function_counter += 1
        callee = info["ssa_name"]
        if arg_ssas:
            args = ", ".join(arg_ssas)
            ops.append(
                f"{self.indent()}{result} = func.call_indirect {callee}({args}) : {fn_ty}"
            )
        else:
            ops.append(
                f"{self.indent()}{result} = func.call_indirect {callee}() : {fn_ty}"
            )
        self._ssa_types[result] = ret_ty
        return result, ops

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
        # Indirect call through a non-capturing lambda / fn-typed local.
        if func_call.name in self.symbol_table:
            info = self.symbol_table[func_call.name]
            if info.get("is_closure") and info.get("fn_mlir_type"):
                return self._generate_closure_call(func_call, info)

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

        # dbg intrinsic: `dbg x` == `x`; evaluate the argument and yield its
        # value. (Runtime printing is emitted by the C backend; in MLIR the
        # operand is simply evaluated.)
        if func_call.name == '__flow_dbg' and len(func_call.arguments) == 1:
            return self.generate_expression(func_call.arguments[0])

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
            if func_info.get('is_variadic'):
                for extra in func_call.arguments[len(expected_arg_types):]:
                    expected_arg_types.append(self.get_expression_type(extra))
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

        n_typed = min(len(prepared_args), len(expected_arg_types))
        tensor_stabilize_order = (
            reversed(range(n_typed))
            if callee_returns_tensor or callee_returns_composite
            else range(n_typed)
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
            if self._is_aggregate_mlir_type(ret_type):
                stable, mat_ops = self._stabilize_aggregate_ssa(
                    ssa_name, ret_type, func_call.name
                )
                ops.extend(mat_ops)
                ssa_name = stable
                self._ssa_types[ssa_name] = ret_type
                if self._is_tensor_struct(ret_type):
                    self._tensor_stable_ssas.add(ssa_name)
            if callee_returns_tensor or callee_returns_composite:
                for i, arg in enumerate(func_call.arguments):
                    if not isinstance(arg, Variable):
                        continue
                    var_info = self.symbol_table.get(arg.name)
                    if not var_info or "ssa_name" not in var_info:
                        continue
                    expected_type = expected_arg_types[i]
                    mlir_type = var_info.get("mlir_type") or expected_type
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
                        and not self._is_tensor_struct(expected_type)
                    ):
                        fresh, mat_ops = self._stabilize_aggregate_ssa(
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

    def _resolve_effect_name(self, name: str) -> str:
        """Resolve an effect-call receiver to a declared effect name.

        Mirrors the C backend: capability-typed variables resolve to their
        effect, then the literal name, then capitalize/upper fallbacks.
        """
        var_info = self.symbol_table.get(name)
        if var_info and var_info.get('type') == 'variable':
            flow_type = var_info.get('flow_type')
            type_name = getattr(flow_type, 'name', '') if flow_type else ''
            if type_name.startswith('capability_'):
                return type_name[len('capability_'):]
            if type_name in self._effects:
                return type_name
        if name in self._effects:
            return name
        if name.capitalize() in self._effects:
            return name.capitalize()
        if name.upper() in self._effects:
            return name.upper()
        return name

    def _effect_call_callee(self, effect_call: EffectCall) -> Optional[str]:
        """Pick the callee for an effect call.

        Inside a `handle` block whose capability implements the operation the
        handler is known at compile time, so the capability function is called
        directly (zero-cost substitution, same as the C backend). Everywhere
        else the NULL-checked dispatch function is used.
        """
        effect_name = self._resolve_effect_name(effect_call.effect_name)
        effect = self._effects.get(effect_name)
        if effect is None:
            return None
        handler_name = self._effect_handler_stack[-1].get(effect_name)
        cap = self._capabilities.get(handler_name) if handler_name else None
        if cap is not None and any(m.name == effect_call.operation for m in cap.methods):
            return f"{handler_name}_{effect_call.operation}"
        if any(op.name == effect_call.operation for op in effect.operations):
            return f"{effect_name}_{effect_call.operation}"
        return None

    def generate_effect_call(self, effect_call: EffectCall) -> tuple[str, List[str]]:
        callee = self._effect_call_callee(effect_call)
        if callee is not None:
            return self.generate_function_call(FunctionCall(callee, effect_call.arguments))
        # Unknown effect: fall back to calling a plain function named after
        # the operation (legacy behavior for modules without effect decls).
        return self.generate_function_call(FunctionCall(effect_call.operation, effect_call.arguments))

    def _method_call_as_effect_call(self, method_call: MethodCall) -> Optional[EffectCall]:
        if not isinstance(method_call.object, Variable):
            return None
        name = method_call.object.name
        is_effect_receiver = name in self._effects
        if not is_effect_receiver:
            var_info = self.symbol_table.get(name)
            if var_info and var_info.get('type') == 'variable':
                flow_type = var_info.get('flow_type')
                type_name = getattr(flow_type, 'name', '') if flow_type else ''
                is_effect_receiver = type_name.startswith('capability_') or type_name in self._effects
        if not is_effect_receiver:
            return None
        return EffectCall(name, method_call.method, method_call.arguments)

    def generate_method_call(self, method_call: MethodCall) -> tuple[str, List[str]]:
        effect_call = self._method_call_as_effect_call(method_call)
        if effect_call is not None:
            return self.generate_effect_call(effect_call)

        # Desugar to function call with receiver as first argument.
        args = [method_call.object] + method_call.arguments
        return self.generate_function_call(FunctionCall(method_call.method, args))
    
    def generate_array_literal(
        self, array_literal: ArrayLiteral, elem_type_hint: Optional[str] = None
    ) -> tuple[str, List[str]]:
        self.function_counter += 1

        element_values: List[str] = []
        ops: List[str] = []
        for element in array_literal.elements:
            v, vops = self.generate_expression(element)
            ops.extend(vops)
            element_values.append(v)

        elem_type = self.get_expression_type(array_literal.elements[0]) if array_literal.elements else 'f32'
        # The declared element type wins: `array<i64, 3> = [1, 2, 3]` parses its
        # elements as i32 literals, and allocating memref<3xi32> for a
        # memref<3xi64> variable makes every later load/store type-mismatch.
        if elem_type_hint and elem_type_hint != elem_type:
            for i, element in enumerate(array_literal.elements):
                src_ty = self._ssa_types.get(element_values[i]) or self.get_expression_type(element)
                if src_ty != elem_type_hint:
                    element_values[i], cast_ops = self._emit_cast(
                        element_values[i], src_ty, elem_type_hint
                    )
                    ops.extend(cast_ops)
            elem_type = elem_type_hint
        size = len(array_literal.elements)

        # !llvm.struct / !llvm.ptr are not valid memref element types. Lower as
        # alloca of !llvm.array<N x T> and return the pointer (doom-flow string tabs).
        if elem_type.startswith('!llvm.struct') or elem_type == '!llvm.ptr':
            storage_elem = 'ptr' if elem_type == '!llvm.ptr' else elem_type
            store_ty = '!llvm.ptr' if elem_type == '!llvm.ptr' else elem_type
            array_ty = f"!llvm.array<{size} x {storage_elem}>"
            one = f"%{self.function_counter}"
            self.function_counter += 1
            ops.append(f"{self.indent()}{one} = llvm.mlir.constant(1 : i64) : i64")
            ptr = f"%{self.function_counter}"
            self.function_counter += 1
            ops.append(
                f"{self.indent()}{ptr} = llvm.alloca {one} x {array_ty} : (i64) -> !llvm.ptr"
            )
            self._ssa_types[ptr] = '!llvm.ptr'
            self._llvm_array_types[ptr] = array_ty
            for i, element_value in enumerate(element_values):
                idx = f"%{self.function_counter}"
                self.function_counter += 1
                ops.append(f"{self.indent()}{idx} = llvm.mlir.constant({i} : i64) : i64")
                gep = f"%{self.function_counter}"
                self.function_counter += 1
                ops.append(
                    f"{self.indent()}{gep} = llvm.getelementptr {ptr}[0, {idx}] "
                    f": (!llvm.ptr, i64) -> !llvm.ptr, {array_ty}"
                )
                self._ssa_types[gep] = '!llvm.ptr'
                ops.append(
                    f"{self.indent()}llvm.store {element_value}, {gep} : {store_ty}, !llvm.ptr"
                )
            return ptr, ops

        # Scalar / memref-compatible element arrays
        alloc_ssa = f"%{self.function_counter}"
        self.function_counter += 1
        memref_ty = f"memref<{size}x{elem_type}>"
        ops.append(f"{self.indent()}{alloc_ssa} = memref.alloc() : {memref_ty}")
        self._ssa_types[alloc_ssa] = memref_ty

        for i, element_value in enumerate(element_values):
            index_ssa = f"%{self.function_counter}"
            self.function_counter += 1
            ops.append(f"{self.indent()}{index_ssa} = arith.constant {i} : index")
            ops.append(f"{self.indent()}memref.store {element_value}, {alloc_ssa}[{index_ssa}] : {memref_ty}")

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
        """True when indexing should use llvm.gep on a raw pointer.

        Declared memref arrays must stay on the memref.load/store path even if
        a later ptr decay briefly confused `_ssa_types` for the same SSA name.
        """
        if isinstance(access.array, Variable):
            arr_type = self.symbol_table.get(access.array.name, {}).get('mlir_type', '')
            if arr_type.startswith('memref<'):
                return False
            if arr_type == '!llvm.ptr':
                return True
        ssa_ty = self._ssa_types.get(array_ssa, '')
        if ssa_ty.startswith('memref<'):
            return False
        if ssa_ty == '!llvm.ptr':
            return True
        return self._elem_type_from_array_expr(access.array) is not None

    def _llvm_array_type_for(self, array_expr: Expression, array_ssa: str) -> Optional[str]:
        if array_ssa in self._llvm_array_types:
            return self._llvm_array_types[array_ssa]
        # Locals are memref.alloc; never treat those SSA values as llvm.array.
        ssa_ty = self._ssa_types.get(array_ssa, "")
        if ssa_ty.startswith("memref"):
            return None
        if isinstance(array_expr, Variable):
            info = self.symbol_table.get(array_expr.name) or {}
            if info.get("llvm_array_type"):
                return info["llvm_array_type"]
            cached = self._llvm_array_types.get(array_expr.name)
            if cached:
                return cached
            # Module statics/consts of array type lower to llvm.array globals.
            if info.get("is_module_global"):
                return self._llvm_array_type_from_flow(info.get("flow_type"))
            return None
        return None

    def _index_to_i64(self, index_ssa: str, index_type: str) -> tuple[str, List[str]]:
        ops: List[str] = []
        if index_type == 'i64':
            return index_ssa, ops
        idx64 = f"%{self.function_counter}"
        self.function_counter += 1
        if index_type == 'index':
            ops.append(f"{self.indent()}{idx64} = arith.index_cast {index_ssa} : index to i64")
        else:
            ext_op = "arith.extui" if index_type.startswith('u') else "arith.extsi"
            ops.append(f"{self.indent()}{idx64} = {ext_op} {index_ssa} : {index_type} to i64")
        return idx64, ops

    def _emit_llvm_array_index_gep(
        self, ptr_ssa: str, index_ssa: str, index_type: str, array_ty: str
    ) -> tuple[str, List[str]]:
        """GEP into !llvm.array<N x T> pointed to by ptr: gep ptr[0, index]."""
        ops: List[str] = []
        index_ssa, cast_ops = self._index_to_i64(index_ssa, index_type)
        ops.extend(cast_ops)
        gep = f"%{self.function_counter}"
        self.function_counter += 1
        ops.append(
            f"{self.indent()}{gep} = llvm.getelementptr {ptr_ssa}[0, {index_ssa}] "
            f": (!llvm.ptr, i64) -> !llvm.ptr, {array_ty}"
        )
        self._ssa_types[gep] = '!llvm.ptr'
        return gep, ops

    def _emit_ptr_index_gep(self, ptr_ssa: str, index_ssa: str, index_type: str, elem_type: Optional[str] = None) -> tuple[str, List[str]]:
        ops: List[str] = []
        index_ssa, cast_ops = self._index_to_i64(index_ssa, index_type)
        ops.extend(cast_ops)

        gep = f"%{self.function_counter}"
        self.function_counter += 1
        gep_elem = elem_type or '!llvm.ptr'
        ops.append(
            f"{self.indent()}{gep} = llvm.getelementptr {ptr_ssa}[{index_ssa}] "
            f": (!llvm.ptr, i64) -> !llvm.ptr, {gep_elem}"
        )
        self._ssa_types[gep] = '!llvm.ptr'
        return gep, ops

    def _memref_element_type(self, memref_ty: str) -> Optional[str]:
        """Extract the element type from a memref<...> type string."""
        if not memref_ty.startswith('memref<') or not memref_ty.endswith('>'):
            return None
        inner = memref_ty[len('memref<'):-1]
        i = 0
        while i < len(inner):
            if inner[i] == '?':
                i += 1
            elif inner[i].isdigit():
                while i < len(inner) and inner[i].isdigit():
                    i += 1
            else:
                break
            if i < len(inner) and inner[i] == 'x':
                i += 1
                if i < len(inner) and (inner[i] == '?' or inner[i].isdigit()):
                    continue
                break
            break
        return inner[i:] if i < len(inner) else None

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

        llvm_array_ty = self._llvm_array_type_for(access.array, array_ssa)
        if llvm_array_ty is not None:
            elem_flow = self._flow_type_of_expr(access)
            elem_type = (
                self.flow_type_to_mlir(elem_flow)
                if elem_flow is not None
                else 'i32'
            )
            gep, gep_ops = self._emit_llvm_array_index_gep(
                array_ssa, index_ssa, index_type, llvm_array_ty
            )
            ops.extend(gep_ops)
            ops.append(f"{self.indent()}{ssa_name} = llvm.load {gep} : !llvm.ptr -> {elem_type}")
            self._ssa_types[ssa_name] = elem_type
            return ssa_name, ops

        if self._is_pointer_array_ssa(array_ssa, access):
            elem_flow = self._flow_type_of_expr(access)
            elem_type = (
                self.flow_type_to_mlir(elem_flow)
                if elem_flow is not None
                else (self._elem_type_from_array_expr(access.array) or 'f32')
            )
            gep, gep_ops = self._emit_ptr_index_gep(array_ssa, index_ssa, index_type, elem_type)
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

        arr_mlir = self._ssa_types.get(array_ssa)
        if not arr_mlir and isinstance(access.array, Variable) and access.array.name in self.symbol_table:
            arr_mlir = self.symbol_table[access.array.name].get('mlir_type', '')

        elem_type = None
        if arr_mlir:
            elem_type = self._memref_element_type(arr_mlir)
        if not elem_type:
            elem_flow = self._flow_type_of_expr(access)
            if elem_flow is not None:
                elem_type = self.flow_type_to_mlir(elem_flow)
        if not elem_type and isinstance(access.array, Variable) and access.array.name in self.symbol_table:
            arr_type = self.symbol_table[access.array.name].get('mlir_type', '')
            if 'i32' in arr_type and 'memref' in arr_type:
                elem_type = 'i32'
            elif 'f64' in arr_type:
                elem_type = 'f64'
            elif 'f32' in arr_type:
                elem_type = 'f32'
        if not elem_type:
            elem_type = 'f32'

        load_memref = arr_mlir if arr_mlir and arr_mlir.startswith('memref<') else f"memref<?x{elem_type}>"
        ops.append(f"{self.indent()}{ssa_name} = memref.load {array_ssa}[{final_index}] : {load_memref}")
        self._ssa_types[ssa_name] = elem_type
        return ssa_name, ops
    
    def get_expression_type(self, expr: Expression) -> str:
        if isinstance(expr, Literal):
            return self.flow_type_to_mlir(expr.type)
        elif isinstance(expr, Variable):
            if expr.name in self.symbol_table:
                var_info = self.symbol_table[expr.name]
                if var_info.get('type') == 'function':
                    # Function name as value → opaque function pointer.
                    return '!llvm.ptr'
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
            if expr.operator == '&':
                return '!llvm.ptr'
            return self.get_expression_type(expr.operand)
        elif isinstance(expr, ArrayLiteral):
            # Scalar arrays -> memref; struct arrays -> !llvm.ptr to !llvm.array
            if expr.elements:
                elem_type = self.get_expression_type(expr.elements[0])
                if elem_type.startswith('!llvm.struct'):
                    return '!llvm.ptr'
                size = len(expr.elements)
                return f"memref<{size}x{elem_type}>"
            return "memref<?xf32>"  # Default
        elif isinstance(expr, FunctionCall):
            if expr.name in self.symbol_table:
                return self.flow_type_to_mlir(self.symbol_table[expr.name]['return_type'])
            else:
                return 'i32'  # Default
        elif isinstance(expr, EffectCall):
            callee = self._effect_call_callee(expr)
            name = callee if callee is not None else expr.operation
            if name in self.symbol_table:
                return self.flow_type_to_mlir(self.symbol_table[name]['return_type'])
            return 'i32'  # Default
        elif isinstance(expr, MethodCall):
            effect_call = self._method_call_as_effect_call(expr)
            if effect_call is not None:
                return self.get_expression_type(effect_call)
            if expr.method in self.symbol_table and self.symbol_table[expr.method].get('type') == 'function':
                return self.flow_type_to_mlir(self.symbol_table[expr.method]['return_type'])
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
            elem_flow = self._flow_type_of_expr(expr)
            if elem_flow is not None:
                return self.flow_type_to_mlir(elem_flow)
            # Get element type from array memref annotation
            if isinstance(expr.array, Variable) and expr.array.name in self.symbol_table:
                arr_type = self.symbol_table[expr.array.name].get('mlir_type', '')
                elem = self._memref_element_type(arr_type) if arr_type else None
                if elem:
                    return elem
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
            # Walk the struct hierarchy via flow types (handles nesting and
            # pointer-to-struct objects). The old path compared MLIR type
            # strings against struct names and always fell through to i32.
            field_type = self._determine_field_type(expr)
            if field_type is not None:
                return self.flow_type_to_mlir(field_type)
            return 'i32'  # Default
        else:
            return 'i32'  # Default
    
    def flow_type_to_mlir(self, flow_type: Type) -> str:
        flow_type = self._resolve_type_alias(flow_type)
        elem_type = self._resolve_type_alias(flow_type.element_type) if getattr(flow_type, 'element_type', None) else None
        # MLIR / llvm dialect have no unsigned integer types. Map Flow uN → iN
        # of the same width (bitwidth semantics; use extui when zero-extending).
        _unsigned_to_signed = {
            'u8': 'i8', 'u16': 'i16', 'u32': 'i32', 'u64': 'i64', 'u128': 'i128',
        }
        if flow_type.name in _unsigned_to_signed:
            return _unsigned_to_signed[flow_type.name]
        if flow_type.name in ['i8', 'i16', 'i32', 'i64', 'i128', 'f32', 'f64']:
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
            # Array type: array_f32 / array_4_Note
            if elem_type:
                elem_mlir = self.flow_type_to_mlir(elem_type)
                # Struct / pointer elements use llvm.array via !llvm.ptr; memref
                # cannot hold !llvm.struct or !llvm.ptr elements (doom-flow statics).
                if elem_mlir.startswith('!llvm.struct') or elem_mlir == '!llvm.ptr':
                    return '!llvm.ptr'
                if flow_type.size:
                    return f"memref<{flow_type.size}x{elem_mlir}>"
                return f"memref<?x{elem_mlir}>"
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
            # Array type: array_100_i32 / array<Note, 4>
            if elem_type:
                elem_mlir = self.flow_type_to_mlir(elem_type)
                if elem_mlir.startswith('!llvm.struct') or elem_mlir == '!llvm.ptr':
                    return '!llvm.ptr'
                if flow_type.size:
                    return f"memref<{flow_type.size}x{elem_mlir}>"
                return f"memref<?x{elem_mlir}>"
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
    
    def _effect_default_value(self, mlir_type: str, indent: str) -> tuple[str, List[str]]:
        """Zeroed default for unhandled effect operations (mirrors the C backend)."""
        ssa_name = f"%{self.function_counter}"
        self.function_counter += 1
        if mlir_type.startswith("f"):
            return ssa_name, [f"{indent}{ssa_name} = arith.constant 0.0 : {mlir_type}"]
        if mlir_type == "!llvm.ptr":
            return ssa_name, [f"{indent}{ssa_name} = llvm.mlir.zero : {mlir_type}"]
        if mlir_type.startswith("i"):
            return ssa_name, [f"{indent}{ssa_name} = arith.constant 0 : {mlir_type}"]
        return ssa_name, [f"{indent}{ssa_name} = llvm.mlir.undef : {mlir_type}"]

    def generate_effect(self, effect: EffectDecl) -> str:
        """Emit the effect handler runtime: a current-handler pointer global
        plus one NULL-checked dispatch function per operation.

        The dispatch function loads the installed vtable (array of function
        pointers), NULL-checks both the vtable and the slot, performs an
        indirect call when handled, and returns a zeroed default otherwise.
        """
        ind = self.indent()
        mlir_code = [f"{ind}// Effect: {effect.name}"]

        # Current handler pointer, NULL until a handle block installs a vtable.
        mlir_code.append(f"{ind}llvm.mlir.global internal @_current_{effect.name}_handler() {{addr_space = 0 : i32}} : !llvm.ptr {{")
        zero_ssa = f"%{self.function_counter}"
        self.function_counter += 1
        mlir_code.append(f"{ind}  {zero_ssa} = llvm.mlir.zero : !llvm.ptr")
        mlir_code.append(f"{ind}  llvm.return {zero_ssa} : !llvm.ptr")
        mlir_code.append(f"{ind}}}")

        for op_index, op in enumerate(effect.operations):
            param_types = [self.flow_type_to_mlir(p.type) for p in op.parameters]
            return_type = self.flow_type_to_mlir(op.return_type)
            is_void = return_type == '()'
            args_sig = ', '.join(f"%arg{i}: {t}" for i, t in enumerate(param_types))
            arg_names = ', '.join(f"%arg{i}" for i in range(len(param_types)))
            call_sig = f"({', '.join(param_types)}) -> {return_type}"

            mlir_code.append(f"{ind}func.func @{effect.name}_{op.name}({args_sig}) -> {return_type} {{")
            i1 = ind + "  "
            i2 = ind + "    "
            i3 = ind + "      "
            addr_ssa = f"%{self.function_counter}"
            self.function_counter += 1
            handler_ssa = f"%{self.function_counter}"
            self.function_counter += 1
            null_ssa = f"%{self.function_counter}"
            self.function_counter += 1
            has_handler_ssa = f"%{self.function_counter}"
            self.function_counter += 1
            mlir_code.append(f"{i1}{addr_ssa} = llvm.mlir.addressof @_current_{effect.name}_handler : !llvm.ptr")
            mlir_code.append(f"{i1}{handler_ssa} = llvm.load {addr_ssa} : !llvm.ptr -> !llvm.ptr")
            mlir_code.append(f"{i1}{null_ssa} = llvm.mlir.zero : !llvm.ptr")
            mlir_code.append(f"{i1}{has_handler_ssa} = llvm.icmp \"ne\" {handler_ssa}, {null_ssa} : !llvm.ptr")

            slot_ssa = f"%{self.function_counter}"
            self.function_counter += 1
            fp_ssa = f"%{self.function_counter}"
            self.function_counter += 1
            fp_ok_ssa = f"%{self.function_counter}"
            self.function_counter += 1

            if is_void:
                mlir_code.append(f"{i1}scf.if {has_handler_ssa} {{")
                mlir_code.append(f"{i2}{slot_ssa} = llvm.getelementptr {handler_ssa}[{op_index}] : (!llvm.ptr) -> !llvm.ptr, !llvm.ptr")
                mlir_code.append(f"{i2}{fp_ssa} = llvm.load {slot_ssa} : !llvm.ptr -> !llvm.ptr")
                mlir_code.append(f"{i2}{fp_ok_ssa} = llvm.icmp \"ne\" {fp_ssa}, {null_ssa} : !llvm.ptr")
                mlir_code.append(f"{i2}scf.if {fp_ok_ssa} {{")
                mlir_code.append(f"{i3}llvm.call {fp_ssa}({arg_names}) : !llvm.ptr, {call_sig}")
                mlir_code.append(f"{i2}}}")
                mlir_code.append(f"{i1}}}")
                mlir_code.append(f"{i1}func.return")
            else:
                result_ssa = f"%{self.function_counter}"
                self.function_counter += 1
                mlir_code.append(f"{i1}{result_ssa} = scf.if {has_handler_ssa} -> ({return_type}) {{")
                mlir_code.append(f"{i2}{slot_ssa} = llvm.getelementptr {handler_ssa}[{op_index}] : (!llvm.ptr) -> !llvm.ptr, !llvm.ptr")
                mlir_code.append(f"{i2}{fp_ssa} = llvm.load {slot_ssa} : !llvm.ptr -> !llvm.ptr")
                mlir_code.append(f"{i2}{fp_ok_ssa} = llvm.icmp \"ne\" {fp_ssa}, {null_ssa} : !llvm.ptr")
                inner_ssa = f"%{self.function_counter}"
                self.function_counter += 1
                mlir_code.append(f"{i2}{inner_ssa} = scf.if {fp_ok_ssa} -> ({return_type}) {{")
                call_ssa = f"%{self.function_counter}"
                self.function_counter += 1
                mlir_code.append(f"{i3}{call_ssa} = llvm.call {fp_ssa}({arg_names}) : !llvm.ptr, {call_sig}")
                mlir_code.append(f"{i3}scf.yield {call_ssa} : {return_type}")
                mlir_code.append(f"{i2}}} else {{")
                default_ssa, default_ops = self._effect_default_value(return_type, i3)
                mlir_code.extend(default_ops)
                mlir_code.append(f"{i3}scf.yield {default_ssa} : {return_type}")
                mlir_code.append(f"{i2}}}")
                mlir_code.append(f"{i2}scf.yield {inner_ssa} : {return_type}")
                mlir_code.append(f"{i1}}} else {{")
                default_ssa, default_ops = self._effect_default_value(return_type, i2)
                mlir_code.extend(default_ops)
                mlir_code.append(f"{i2}scf.yield {default_ssa} : {return_type}")
                mlir_code.append(f"{i1}}}")
                mlir_code.append(f"{i1}func.return {result_ssa} : {return_type}")
            mlir_code.append(f"{ind}}}")

        return "\n".join(mlir_code)

    def generate_capability(self, capability: CapabilityDecl) -> str:
        """Emit capability methods as plain functions plus one zero-initialized
        vtable global per handled effect. Vtable slots are filled at startup by
        @_flow_effects_init (see _generate_effects_init)."""
        ind = self.indent()
        mlir_code = [f"{ind}// Capability: {capability.name} (effects: {', '.join(capability.effects)})"]

        for method in capability.methods:
            method_fn = FunctionDecl(
                name=f"{capability.name}_{method.name}",
                parameters=method.parameters,
                return_type=method.return_type,
                body=method.body,
                attributes=[],
            )
            mlir_code.append(self.generate_function(method_fn))

        for effect_name in capability.effects:
            effect = self._effects.get(effect_name)
            if effect is None:
                continue
            slot_count = len(effect.operations)
            mlir_code.append(f"{ind}llvm.mlir.global internal @_{capability.name}_{effect_name}_vtable() {{addr_space = 0 : i32}} : !llvm.array<{slot_count} x ptr> {{")
            null_ssa = f"%{self.function_counter}"
            self.function_counter += 1
            mlir_code.append(f"{ind}  {null_ssa} = llvm.mlir.zero : !llvm.ptr")
            acc_ssa = f"%{self.function_counter}"
            self.function_counter += 1
            mlir_code.append(f"{ind}  {acc_ssa} = llvm.mlir.undef : !llvm.array<{slot_count} x ptr>")
            for i in range(slot_count):
                next_ssa = f"%{self.function_counter}"
                self.function_counter += 1
                mlir_code.append(f"{ind}  {next_ssa} = llvm.insertvalue {null_ssa}, {acc_ssa}[{i}] : !llvm.array<{slot_count} x ptr>")
                acc_ssa = next_ssa
            mlir_code.append(f"{ind}  llvm.return {acc_ssa} : !llvm.array<{slot_count} x ptr>")
            mlir_code.append(f"{ind}}}")

        return "\n".join(mlir_code)

    def _generate_effects_init(self) -> str:
        """Emit @_flow_effects_init: stores every implemented capability method
        address into its vtable slot. Called once at the top of main."""
        ind = self.indent()
        inner = ind + "  "
        mlir_code = [f"{ind}func.func @_flow_effects_init() {{"]
        for cap in self._capabilities.values():
            for effect_name in cap.effects:
                effect = self._effects.get(effect_name)
                if effect is None:
                    continue
                vt_ssa = f"%{self.function_counter}"
                self.function_counter += 1
                mlir_code.append(f"{inner}{vt_ssa} = llvm.mlir.addressof @_{cap.name}_{effect_name}_vtable : !llvm.ptr")
                for op_index, op in enumerate(effect.operations):
                    method = next((m for m in cap.methods if m.name == op.name), None)
                    if method is None:
                        continue  # unimplemented operation: slot stays NULL
                    param_types = [self.flow_type_to_mlir(p.type) for p in method.parameters]
                    return_type = self.flow_type_to_mlir(method.return_type)
                    fn_type = f"({', '.join(param_types)}) -> {return_type}"
                    fn_ssa = f"%{self.function_counter}"
                    self.function_counter += 1
                    mlir_code.append(f"{inner}{fn_ssa} = func.constant @{cap.name}_{op.name} : {fn_type}")
                    ptr_ssa = f"%{self.function_counter}"
                    self.function_counter += 1
                    mlir_code.append(f"{inner}{ptr_ssa} = builtin.unrealized_conversion_cast {fn_ssa} : {fn_type} to !llvm.ptr")
                    slot_ssa = f"%{self.function_counter}"
                    self.function_counter += 1
                    mlir_code.append(f"{inner}{slot_ssa} = llvm.getelementptr {vt_ssa}[{op_index}] : (!llvm.ptr) -> !llvm.ptr, !llvm.ptr")
                    mlir_code.append(f"{inner}llvm.store {ptr_ssa}, {slot_ssa} : !llvm.ptr, !llvm.ptr")
        mlir_code.append(f"{inner}func.return")
        mlir_code.append(f"{ind}}}")
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

        self.symbol_table[const.name] = {
            "type": "variable",
            "mlir_type": mlir_type,
            "flow_type": const.type,
            "is_module_global": True,
            "is_const": True,
        }

        # Module-scope globals should not rely on SSA values from local ops.
        if isinstance(const.value, Literal):
            if const.value.type.name == "string":
                # Named string const must be an addressable llvm.global (doom uses
                # DMAIN_PACKAGE_STRING etc. via llvm.mlir.addressof @Name).
                str_val = const.value.value
                str_content = str_val[1:-1] if len(str_val) >= 2 and str_val[0] == '"' else str_val
                byte_len = len(str_content.encode("utf-8").decode("unicode_escape")) + 1
                mlir_code.append(
                    f'{self.indent()}llvm.mlir.global internal constant @{const.name}'
                    f'("{str_content}\\00") {{addr_space = 0 : i32}} '
                    f': !llvm.array<{byte_len} x i8>'
                )
                self.symbol_table[const.name] = {
                    "type": "variable",
                    "mlir_type": "!llvm.ptr",
                    "flow_type": const.type,
                    "is_module_global": True,
                    "is_const": True,
                    "is_string_global": True,
                }
                if getattr(self, "_module_symbol_snapshot", None) is not None:
                    self._module_symbol_snapshot[const.name] = dict(
                        self.symbol_table[const.name]
                    )
                return "\n".join(mlir_code)
            if (
                mlir_type == "!llvm.ptr"
                or str(const.value.value).lower() == "null"
            ):
                # Zero-init pointer global (no `null` attribute — #223).
                mlir_code.append(
                    f"{self.indent()}llvm.mlir.global internal constant "
                    f"@{const.name}() : !llvm.ptr"
                )
                return "\n".join(mlir_code)
            literal_value = self._format_mlir_numeric(str(const.value.value), mlir_type)
            mlir_code.append(
                f"{self.indent()}llvm.mlir.global internal constant @{const.name}"
                f"({literal_value} : {mlir_type}) : {mlir_type}"
            )
            return "\n".join(mlir_code)

        # Fallback: emit zero-initialized constant
        zero_value = "0.0" if mlir_type in ["f32", "f64"] else "0"
        mlir_code.append(
            f"{self.indent()}llvm.mlir.global internal constant @{const.name}"
            f"({zero_value} : {mlir_type}) : {mlir_type}"
        )
        return "\n".join(mlir_code)

    def generate_static(self, static: StaticDecl) -> str:
        """Generate a mutable module-scope llvm.mlir.global for `let mut` at top level."""
        mlir_code = []
        mlir_code.append(f"{self.indent()}// Module static: {static.name}")

        mlir_type = self.flow_type_to_mlir(static.type)
        if getattr(static.type, "name", None) == "bool":
            mlir_type = "i1"

        llvm_array_ty = self._llvm_array_type_from_flow(static.type)
        if llvm_array_ty:
            # Global storage is the array; SSA uses pointer-to-array.
            # Zero-init; literal element lists are applied via later stores when needed.
            mlir_type = "!llvm.ptr"
            mlir_code.append(
                f"{self.indent()}llvm.mlir.global internal @{static.name}() : {llvm_array_ty}"
            )
            self.symbol_table[static.name] = {
                "type": "variable",
                "mlir_type": mlir_type,
                "flow_type": static.type,
                "is_module_global": True,
                "is_const": False,
                "llvm_array_type": llvm_array_ty,
            }
            self._llvm_array_types[static.name] = llvm_array_ty
            # Refresh snapshot entry so later functions see llvm_array_type.
            if getattr(self, "_module_symbol_snapshot", None) is not None:
                self._module_symbol_snapshot[static.name] = dict(
                    self.symbol_table[static.name]
                )
            return "\n".join(mlir_code)

        # Aggregates (structs/arrays) get zero init for now; scalar literals use the value.
        init_payload = f"() : {mlir_type}"
        if isinstance(static.value, Literal) and getattr(static.value.type, "name", "") != "string":
            if (
                mlir_type == "!llvm.ptr"
                or str(static.value.value).lower() == "null"
            ):
                init_payload = "() : !llvm.ptr"
                mlir_type = "!llvm.ptr"
            else:
                lit = self._format_mlir_numeric(str(static.value.value), mlir_type)
                if static.value.type.name == "bool":
                    lit = "1" if str(static.value.value).lower() in ("true", "1") else "0"
                init_payload = f"({lit} : {mlir_type}) : {mlir_type}"
        elif mlir_type == "!llvm.ptr":
            init_payload = "() : !llvm.ptr"
        elif mlir_type in ("f32", "f64"):
            init_payload = f"(0.0 : {mlir_type}) : {mlir_type}"
        elif mlir_type.startswith("i") or mlir_type.startswith("u") or mlir_type == "index":
            init_payload = f"(0 : {mlir_type}) : {mlir_type}"

        mlir_code.append(
            f"{self.indent()}llvm.mlir.global internal @{static.name}{init_payload}"
        )

        self.symbol_table[static.name] = {
            "type": "variable",
            "mlir_type": mlir_type,
            "flow_type": static.type,
            "is_module_global": True,
            "is_const": False,
        }
        return "\n".join(mlir_code)

def flow_to_mlir(declarations: List[Any], source_file: str = "unknown.flow", emit_debug_info: bool = False, emit_gpu: bool = False) -> str:
    generator = MLIRGenerator(source_file)
    generator.emit_debug_info = emit_debug_info
    return generator.generate_module(declarations, emit_gpu=emit_gpu)
