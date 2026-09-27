"""Focused MLIR parity extensions.

This module keeps cross-backend semantic fixes isolated while the legacy MLIR
generator is being converged with the C backend.  The extensions use the
existing generator's representation and helper methods rather than introducing
a second backend model.
"""

from __future__ import annotations

import copy
from typing import Any, List

from .parser import (
    ArrayAccess,
    FieldAccess,
    ListPattern,
    Literal,
    MatchStatement,
    StructPattern,
    Type,
    Variable,
)


def _expand_or_patterns(match_stmt: MatchStatement) -> MatchStatement:
    """Expand OrPatterns in match cases into individual cases."""
    if any(type(case.pattern).__name__ == "OrPattern" for case in match_stmt.cases):
        expanded_cases = []
        for case in match_stmt.cases:
            if type(case.pattern).__name__ == "OrPattern":
                for pattern in case.pattern.patterns:
                    expanded = copy.copy(case)
                    expanded.pattern = pattern
                    expanded_cases.append(expanded)
            else:
                expanded_cases.append(case)

        match_stmt = copy.copy(match_stmt)
        match_stmt.cases = expanded_cases
    return match_stmt


def _check_arms_terminate(generator: Any, match_stmt: MatchStatement) -> bool:
    """Determine whether all match arms terminate with a return statement."""
    arms_terminate = bool(match_stmt.cases) and all(
        generator._block_has_return(case.body) for case in match_stmt.cases
    )
    if match_stmt.default_case is not None:
        return arms_terminate and generator._block_has_return(
            match_stmt.default_case
        )
    return False


def _find_merged_vars(
    generator: Any, match_stmt: MatchStatement, arms_terminate: bool
) -> List[str]:
    """Collect mergeable SSA variable names across match arm blocks."""
    merged_vars: List[str] = []
    if not arms_terminate:
        blocks = [case.body for case in match_stmt.cases]
        if match_stmt.default_case:
            blocks.append(match_stmt.default_case)
        for block in blocks:
            for name in generator._assigned_locals(block):
                if name not in merged_vars and name in generator.symbol_table:
                    merged_vars.append(name)
    return generator._filter_ssa_mergeable(merged_vars)


def _emit_true_condition(generator: Any, mlir_code: List[str]) -> str:
    """Emit an unconditional true (i1 constant 1) SSA instruction."""
    cond = f"%{generator.function_counter}"
    generator.function_counter += 1
    mlir_code.append(f"{generator.indent()}{cond} = arith.constant 1 : i1")
    generator._ssa_types[cond] = "i1"
    return cond


def _lower_guard_as_i1(
    generator: Any, guard_ssa: str, guard_ty: str, mlir_code: List[str]
) -> str:
    """Convert non-i1 guard condition values into i1 boolean SSAs."""
    if guard_ty == "i1":
        return guard_ssa

    zero = f"%{generator.function_counter}"
    generator.function_counter += 1
    result = f"%{generator.function_counter}"
    generator.function_counter += 1

    if guard_ty in ("f32", "f64"):
        mlir_code.append(
            f"{generator.indent()}{zero} = arith.constant 0.0 : {guard_ty}"
        )
        mlir_code.append(
            f"{generator.indent()}{result} = arith.cmpf one, "
            f"{guard_ssa}, {zero} : {guard_ty}"
        )
    elif guard_ty == "!llvm.ptr":
        mlir_code.append(
            f"{generator.indent()}{zero} = llvm.mlir.zero : !llvm.ptr"
        )
        mlir_code.append(
            f"{generator.indent()}{result} = llvm.icmp \"ne\" "
            f"{guard_ssa}, {zero} : !llvm.ptr"
        )
    else:
        mlir_code.append(
            f"{generator.indent()}{zero} = arith.constant 0 : {guard_ty}"
        )
        mlir_code.append(
            f"{generator.indent()}{result} = arith.cmpi ne, "
            f"{guard_ssa}, {zero} : {guard_ty}"
        )

    generator._ssa_types[result] = "i1"
    return result


def _lower_struct_pattern(
    generator: Any,
    pattern: StructPattern,
    val_ssa: str,
    val_type: str,
    mlir_code: List[str],
    binding_ops: List[str],
) -> str:
    """Lower a struct pattern, creating bindings for matching fields."""
    struct_decl = generator._get_struct_decl(pattern.struct_name)
    cond_ssa = _emit_true_condition(generator, mlir_code)

    if struct_decl:
        temp_var_name = f"__match_input_{generator.function_counter}"
        generator.symbol_table[temp_var_name] = {
            "type": "variable",
            "ssa_name": val_ssa,
            "mlir_type": val_type,
            "flow_type": Type(pattern.struct_name),
        }

        for field_index, binding_name in enumerate(pattern.bindings):
            if field_index >= len(struct_decl.fields):
                break
            field_decl = struct_decl.fields[field_index]
            field_access = FieldAccess(
                Variable(temp_var_name), field_decl.name
            )
            field_ssa, field_ops = generator.generate_field_access(field_access)
            binding_ops.extend(field_ops)
            generator.symbol_table[binding_name] = {
                "ssa_name": field_ssa,
                "mlir_type": generator.flow_type_to_mlir(field_decl.type),
                "flow_type": field_decl.type,
                "type": "variable",
            }
    return cond_ssa


def _lower_list_pattern(
    generator: Any,
    pattern: ListPattern,
    match_value_expr: Any,
    val_ssa: str,
    val_type: str,
    mlir_code: List[str],
    binding_ops: List[str],
) -> str:
    """Lower a list pattern with literal element checks and element variable bindings."""
    arr_temp = f"__match_arr_{generator.function_counter}"
    generator.symbol_table[arr_temp] = {
        "ssa_name": val_ssa,
        "mlir_type": val_type,
        "type": "variable",
        "flow_type": generator._flow_type_of_expr(match_value_expr),
    }

    elem_type = None
    for elem in pattern.elements:
        if isinstance(elem, Literal):
            elem_type = elem.type
            break

    literal_conditions: List[str] = []
    for element_index, elem in enumerate(pattern.elements):
        access = ArrayAccess(
            Variable(arr_temp), Literal(element_index, Type("i32"))
        )
        if isinstance(elem, Literal):
            literal_type = elem_type or elem.type
            literal = elem
            if elem.type.name != "string" and literal_type is not None:
                literal = Literal(elem.value, literal_type)
            access_ssa, access_ops = generator.generate_array_access(access)
            mlir_code.extend(access_ops)
            literal_ssa, literal_ops = generator.generate_literal(literal)
            mlir_code.extend(literal_ops)
            access_type = generator.get_expression_type(access)
            condition = f"%{generator.function_counter}"
            generator.function_counter += 1
            if "f" in access_type:
                mlir_code.append(
                    f"{generator.indent()}{condition} = arith.cmpf oeq, "
                    f"{access_ssa}, {literal_ssa} : {access_type}"
                )
            else:
                mlir_code.append(
                    f"{generator.indent()}{condition} = arith.cmpi eq, "
                    f"{access_ssa}, {literal_ssa} : {access_type}"
                )
            generator._ssa_types[condition] = "i1"
            literal_conditions.append(condition)
        elif isinstance(elem, Variable) and elem.name != "_":
            access_ssa, access_ops = generator.generate_array_access(access)
            binding_ops.extend(access_ops)
            generator.symbol_table[elem.name] = {
                "ssa_name": access_ssa,
                "mlir_type": generator.get_expression_type(access),
                "flow_type": elem_type or Type("i32"),
                "type": "variable",
            }

    if literal_conditions:
        cond_ssa = literal_conditions[0]
        for other in literal_conditions[1:]:
            combined = f"%{generator.function_counter}"
            generator.function_counter += 1
            mlir_code.append(
                f"{generator.indent()}{combined} = arith.andi "
                f"{cond_ssa}, {other} : i1"
            )
            generator._ssa_types[combined] = "i1"
            cond_ssa = combined
        return cond_ssa
    return _emit_true_condition(generator, mlir_code)


def _lower_variable_pattern(
    generator: Any,
    pattern: Variable,
    match_value_expr: Any,
    val_ssa: str,
    val_type: str,
    mlir_code: List[str],
) -> str:
    """Lower a variable pattern (wildcard or identifier binding)."""
    cond_ssa = _emit_true_condition(generator, mlir_code)
    if pattern.name != "_":
        generator.symbol_table[pattern.name] = {
            "type": "variable",
            "ssa_name": val_ssa,
            "mlir_type": val_type,
            "flow_type": generator._flow_type_of_expr(match_value_expr)
            or Type("i32"),
        }
    return cond_ssa


def _lower_expression_pattern(
    generator: Any,
    pattern: Any,
    match_value_expr: Any,
    val_ssa: str,
    val_type: str,
    mlir_code: List[str],
) -> str:
    """Lower an expression or enum variant comparison pattern."""
    compare_ssa = val_ssa
    compare_type = val_type
    pattern_name = getattr(pattern, "name", None)
    owner = None
    if isinstance(pattern_name, str):
        owner = getattr(generator, "_enum_variant_owner", {}).get(pattern_name)

    if owner and owner in getattr(generator, "_enums", {}):
        flow_type = generator._flow_type_of_expr(match_value_expr)
        if flow_type is not None and flow_type.name == owner:
            if isinstance(match_value_expr, Variable):
                tag_object = match_value_expr
            else:
                temp_name = f"__match_enum_tmp_{generator.function_counter}"
                generator.function_counter += 1
                generator.symbol_table[temp_name] = {
                    "type": "variable",
                    "ssa_name": val_ssa,
                    "mlir_type": val_type,
                    "flow_type": Type(owner),
                }
                tag_object = Variable(temp_name)
            compare_ssa, tag_ops = generator.generate_field_access(
                FieldAccess(tag_object, "tag")
            )
            mlir_code.extend(tag_ops)
            compare_type = "i32"
        elif flow_type is not None and flow_type.name == "i32":
            compare_type = "i32"

    pattern_ssa, pattern_ops = generator.generate_expression(pattern)
    mlir_code.extend(pattern_ops)
    cond_ssa = f"%{generator.function_counter}"
    generator.function_counter += 1
    if "ptr" in compare_type:
        mlir_code.append(
            f"{generator.indent()}{cond_ssa} = llvm.icmp \"eq\" "
            f"{compare_ssa}, {pattern_ssa} : {compare_type}"
        )
    elif "f" in compare_type and "i" not in compare_type[:1]:
        mlir_code.append(
            f"{generator.indent()}{cond_ssa} = arith.cmpf oeq, "
            f"{compare_ssa}, {pattern_ssa} : {compare_type}"
        )
    else:
        mlir_code.append(
            f"{generator.indent()}{cond_ssa} = arith.cmpi eq, "
            f"{compare_ssa}, {pattern_ssa} : {compare_type}"
        )
    generator._ssa_types[cond_ssa] = "i1"
    return cond_ssa


def _lower_pattern_condition(
    generator: Any,
    case_pattern: Any,
    match_value_expr: Any,
    val_ssa: str,
    val_type: str,
    mlir_code: List[str],
    binding_ops: List[str],
) -> str:
    """Lower pattern condition and bindings based on the pattern type."""
    if isinstance(case_pattern, StructPattern):
        return _lower_struct_pattern(
            generator, case_pattern, val_ssa, val_type, mlir_code, binding_ops
        )

    if isinstance(case_pattern, ListPattern):
        return _lower_list_pattern(
            generator,
            case_pattern,
            match_value_expr,
            val_ssa,
            val_type,
            mlir_code,
            binding_ops,
        )

    if isinstance(case_pattern, Variable) and (
        case_pattern.name == "_"
        or getattr(generator, "_enum_variant_owner", {}).get(case_pattern.name)
        is None
    ):
        return _lower_variable_pattern(
            generator,
            case_pattern,
            match_value_expr,
            val_ssa,
            val_type,
            mlir_code,
        )

    return _lower_expression_pattern(
        generator,
        case_pattern,
        match_value_expr,
        val_ssa,
        val_type,
        mlir_code,
    )


def _generate_match_with_parity(self, match_stmt: MatchStatement) -> str:
    """Lower match with C-backend-equivalent pattern semantics.

    In particular, bare identifiers bind the scrutinee, ``_`` is an
    unconditional wildcard, guards run with pattern bindings in scope, and
    destructuring SSA dominates both the guard and the arm body.
    """
    match_stmt = _expand_or_patterns(match_stmt)

    mlir_code: List[str] = []
    val_ssa, val_ops = self.generate_expression(match_stmt.value)
    mlir_code.extend(val_ops)
    val_type = self.get_expression_type(match_stmt.value)

    case_labels = []
    next_case_labels = []
    for _ in match_stmt.cases:
        case_labels.append(self._new_block_label())
        next_case_labels.append(self._new_block_label())
    end_label = self._new_block_label()

    arms_terminate = _check_arms_terminate(self, match_stmt)
    merged_vars = _find_merged_vars(self, match_stmt, arms_terminate)
    entry_ssas = {name: self.symbol_table[name]["ssa_name"] for name in merged_vars}
    merged_types = [self.symbol_table[name]["mlir_type"] for name in merged_vars]

    def restore_entry_bindings() -> None:
        for name in merged_vars:
            self.symbol_table[name]["ssa_name"] = entry_ssas[name]

    def end_edge() -> str:
        if not merged_vars:
            return ""
        ssas = [self.symbol_table[name]["ssa_name"] for name in merged_vars]
        return self._cf_successor_operands(ssas, merged_types)

    def entry_edge() -> str:
        if not merged_vars:
            return ""
        return self._cf_successor_operands(
            [entry_ssas[name] for name in merged_vars], merged_types
        )

    for case_index, case in enumerate(match_stmt.cases):
        case_label = case_labels[case_index]
        next_label = next_case_labels[case_index]
        binding_ops: List[str] = []
        saved_locals = self.symbol_table.copy()

        cond_ssa = _lower_pattern_condition(
            self,
            case.pattern,
            match_stmt.value,
            val_ssa,
            val_type,
            mlir_code,
            binding_ops,
        )

        # Destructuring definitions must dominate both guard evaluation and the
        # arm body. They are emitted in the test block exactly once.
        if binding_ops:
            mlir_code.extend(binding_ops)

        if case.guard is not None:
            guard_ssa, guard_ops = self.generate_expression(case.guard)
            mlir_code.extend(guard_ops)
            guard_type = self._ssa_types.get(
                guard_ssa
            ) or self.get_expression_type(case.guard)
            guard_ssa = _lower_guard_as_i1(self, guard_ssa, guard_type, mlir_code)
            guarded = f"%{self.function_counter}"
            self.function_counter += 1
            mlir_code.append(
                f"{self.indent()}{guarded} = arith.andi "
                f"{cond_ssa}, {guard_ssa} : i1"
            )
            self._ssa_types[guarded] = "i1"
            cond_ssa = guarded

        mlir_code.append(
            f"{self.indent()}cf.cond_br {cond_ssa}, ^{case_label}, ^{next_label}"
        )

        mlir_code.append(f"^{case_label}:")
        self.indent_level += 1
        restore_entry_bindings()
        body = self.generate_block(case.body)
        if body.strip():
            mlir_code.append(body)
        if not self._block_has_terminator(body):
            mlir_code.append(f"{self.indent()}cf.br ^{end_label}{end_edge()}")
        self.indent_level -= 1

        self.symbol_table = saved_locals
        if case_index < len(match_stmt.cases) - 1:
            mlir_code.append(f"^{next_label}:")

    final_next_label = next_case_labels[-1] if next_case_labels else end_label
    if match_stmt.default_case:
        mlir_code.append(f"^{final_next_label}:")
        self.indent_level += 1
        restore_entry_bindings()
        default_body = self.generate_block(match_stmt.default_case)
        if default_body.strip():
            mlir_code.append(default_body)
        if not self._block_has_terminator(default_body):
            mlir_code.append(f"{self.indent()}cf.br ^{end_label}{end_edge()}")
        self.indent_level -= 1
    else:
        mlir_code.append(f"^{final_next_label}:")
        mlir_code.append(f"{self.indent()}cf.br ^{end_label}{entry_edge()}")

    if merged_vars:
        end_args = []
        for mlir_type in merged_types:
            arg = f"%{self.function_counter}"
            self.function_counter += 1
            end_args.append((arg, mlir_type))
        mlir_code.append(
            f"^{end_label}({', '.join(f'{arg}: {mlir_type}' for arg, mlir_type in end_args)}):"
        )
        for variable_name, (arg, mlir_type) in zip(merged_vars, end_args):
            self.symbol_table[variable_name]["ssa_name"] = arg
            self._ssa_types[arg] = mlir_type
    else:
        mlir_code.append(f"^{end_label}:")

    if arms_terminate:
        mlir_code.append(f"{self.indent()}llvm.unreachable")

    return "\n".join(mlir_code)


def install() -> None:
    """Install focused parity lowerings on the legacy MLIR generator."""
    from .mlir_generator import MLIRGenerator

    MLIRGenerator.generate_match = _generate_match_with_parity
