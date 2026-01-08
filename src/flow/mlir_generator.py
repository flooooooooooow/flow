#!/usr/bin/env python3
"""
FLOW to MLIR Generator
Converts parsed FLOW AST to MLIR dialects
"""

from typing import List, Dict, Optional, Any
from .parser import (
    FunctionDecl, EffectDecl, CapabilityDecl, StructDecl, Block, Statement,
    VarDecl, Assignment, IfStatement, WhileStatement, ForStatement,
    ReturnStatement, Expression, Literal, Variable, BinaryOperation,
    UnaryOperation, FunctionCall, StructLiteral, FieldAccess, ArrayLiteral, VectorLiteral, ArrayAccess, Type,
    HandleStatement, EffectOperation, CapabilityMethod, EffectCall,
    MatchStatement, MatchCase, StructPattern, ConstDecl
)
import textwrap

class MLIRGenerator:
    def __init__(self, source_file: str = "unknown.flow"):
        self.indent_level = 0
        self.symbol_table = {}
        self.function_counter = 0
        self.block_counter = 0
        self.string_constants = {}  # Maps string value -> global name
        self.string_counter = 0
        self.needs_printf = False  # Track if we need printf declaration
        self.source_file = source_file  # For debug info
        self.current_line = 1  # Track current source line for debug info
        self.emit_debug_info = True  # Enable DWARF debug info generation
        self._effect_handler_stack: List[Dict[str, str]] = [{}]
        self.inside_scf_for = False  # Track if we're inside scf.for
        self.declarations = []  # Store declarations for type lookup
        self.struct_layouts = {}  # Maps struct name to field offsets and types
        
    def indent(self) -> str:
        return "  " * self.indent_level

    def _new_block_label(self) -> str:
        label = f"bb{self.block_counter}"
        self.block_counter += 1
        return label

    def _get_struct_decl(self, name: str) -> Optional[StructDecl]:
        """Look up a struct declaration by name."""
        for decl in self.declarations:
            if isinstance(decl, StructDecl) and decl.name == name:
                return decl
        return None
    
    def _calculate_struct_layouts(self, declarations: List[Any]) -> None:
        """Calculate field offsets for all struct types"""
        for decl in declarations:
            if type(decl).__name__ == 'StructDecl':
                layout = {}
                offset = 0
                for field in decl.fields:
                    # Get field size (simplified - using 4 bytes for i32/f32, 1 for i8, etc.)
                    field_size = self._get_type_size(field.type)
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
    
    def generate_module(self, declarations: List[Any]) -> str:
        mlir_code = []
        
        # Reset state for new module
        self.string_constants = {}
        self.string_counter = 0
        self.needs_printf = False
        self.declarations = declarations  # Store declarations for type lookup
        
        # Calculate struct layouts
        self._calculate_struct_layouts(declarations)
        
        # Module header with required dialects and debug info
        if self.emit_debug_info:
            mlir_code.append(f'module attributes {{llvm.dbg.cu = #llvm.di_compile_unit<id = distinct[0]<>, sourceLanguage = DW_LANG_C, file = #llvm.di_file<"{self.source_file}" in ".">, producer = "FLOW Compiler", isOptimized = false, emissionKind = Full>}} {{')
        else:
            mlir_code.append("module {")
        self.indent_level += 1
        
        # First pass: generate all declarations to collect string constants
        decl_code = []
        for decl in declarations:
            decl_type = type(decl).__name__
            if decl_type == 'FunctionDecl':
                decl_code.append(self.generate_function(decl))
            elif decl_type == 'EffectDecl':
                decl_code.append(self.generate_effect(decl))
            elif decl_type == 'CapabilityDecl':
                decl_code.append(self.generate_capability(decl))
            elif decl_type == 'StructDecl':
                decl_code.append(self.generate_struct(decl))
            elif decl_type == 'ConstDecl':
                decl_code.append(self.generate_const(decl))
            else:
                decl_code.append(f"// Unsupported declaration type: {decl_type}")
        
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
        
        self.indent_level -= 1
        mlir_code.append("}")
        
        return "\n".join(mlir_code)
    
    def generate_function(self, func: FunctionDecl) -> str:
        # Add function to symbol table
        self.symbol_table[func.name] = {
            'type': 'function',
            'return_type': func.return_type,
            'parameters': func.parameters,
            'mlir_name': f"@{func.name}"
        }
        
        # Store current function return type for use in return statements
        self.current_function_return_type = func.return_type
        
        mlir_code = []
        
        # Function signature
        param_types = [self.flow_type_to_mlir(p.type) for p in func.parameters]
        return_type = self.flow_type_to_mlir(func.return_type)
        
        func_signature = f"func.func @{func.name}({', '.join([f'%arg{i}: {param_types[i]}' for i in range(len(param_types))])}) -> {return_type}"
        mlir_code.append(f"{self.indent()}{func_signature} {{")
        
        self.indent_level += 1
        
        # Generate function body
        for i, param in enumerate(func.parameters):
            self.symbol_table[param.name] = {
                'type': 'variable',
                'mlir_type': self.flow_type_to_mlir(param.type),
                'ssa_name': f'%arg{i}'
            }
        
        # Generate statements
        body_mlir = self.generate_block(func.body)
        if body_mlir.strip():
            mlir_code.append(body_mlir)
        
        self.indent_level -= 1
        mlir_code.append(f"{self.indent()}}}")
        
        return "\n".join(mlir_code)
    
    def generate_block(self, block: Block) -> str:
        mlir_code = []
        
        for stmt in block.statements:
            stmt_mlir = self.generate_statement(stmt)
            if stmt_mlir.strip():
                mlir_code.append(stmt_mlir)
        
        return "\n".join(mlir_code)
    
    def generate_statement(self, stmt: Statement) -> str:
        stmt_type = type(stmt).__name__
        if stmt_type == 'VarDecl':
            return self.generate_var_decl(stmt)
        elif stmt_type == 'ReturnStatement':
            return self.generate_return(stmt)
        elif stmt_type == 'Assignment':
            return self.generate_assignment(stmt)
        elif stmt_type == 'IfStatement':
            return self.generate_if(stmt)
        elif stmt_type == 'WhileStatement':
            return self.generate_while(stmt)
        elif stmt_type == 'ForStatement':
            return self.generate_for(stmt)
        elif stmt_type == 'HandleStatement':
            return self.generate_handle(stmt)
        elif stmt_type == 'MatchStatement':
            return self.generate_match(stmt)
        elif stmt_type in ['Literal', 'Variable', 'BinaryOperation', 'UnaryOperation', 'FunctionCall', 'VectorLiteral']:
            value_ssa, value_ops = self.generate_expression(stmt)
            # Expression statement: emit ops for side effects / computation, discard value.
            return "\n".join(value_ops)
        else:
            return f"{self.indent()}// Unsupported statement type: {stmt_type}"
    
    def generate_var_decl(self, var_decl: VarDecl) -> str:
        mlir_type = self.flow_type_to_mlir(var_decl.type)
         
        if var_decl.initializer:
            init_value, init_ops = self.generate_expression(var_decl.initializer)

            # Bind variable name to the SSA value produced by the initializer.
            # MLIR SSA values are immutable; we do not emit an extra "assignment" op.
            self.symbol_table[var_decl.name] = {
                'type': 'variable',
                'flow_type': var_decl.type,  # Store original FLOW type
                'mlir_type': mlir_type,
                'ssa_name': init_value
            }

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
            else:
                return f"{self.indent()}{ssa_name} = memref.alloc() : memref<{mlir_type}>"
    
    def generate_return(self, return_stmt: ReturnStatement) -> str:
        if return_stmt.value:
            value_ssa, value_ops = self.generate_expression(return_stmt.value)
            lines: List[str] = []
            lines.extend(value_ops)
            # Use the function's return type instead of the expression type
            return_type = self.flow_type_to_mlir(self.current_function_return_type)
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
            if type(access).__name__ == 'ArrayAccess':
                # Generate array expression
                array_ssa, array_ops = self.generate_expression(access.array)
                ops.extend(array_ops)

                # Generate index expression
                index_ssa, index_ops = self.generate_expression(access.index)
                ops.extend(index_ops)

                # Check if index is already index type
                index_type = 'i32'
                if isinstance(access.index, Variable) and access.index.name in self.symbol_table:
                    index_type = self.symbol_table[access.index.name].get('mlir_type', 'i32')

                if index_type == 'index':
                    final_index = index_ssa
                else:
                    index_cast = f"%{self.function_counter}"
                    self.function_counter += 1
                    ops.append(f"{self.indent()}{index_cast} = arith.index_cast {index_ssa} : i32 to index")
                    final_index = index_cast

                # Determine element type
                elem_type = 'f32'
                if isinstance(access.array, Variable) and access.array.name in self.symbol_table:
                    arr_type = self.symbol_table[access.array.name].get('mlir_type', '')
                    if 'i32' in arr_type and 'memref' in arr_type:
                        elem_type = 'i32'
                    elif 'f64' in arr_type:
                        elem_type = 'f64'

                # Emit memref.store
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
                        ops.append(f"{self.indent()}memref.load {load_name}, {value_ssa}[{i}] : memref<?xi8>")
                        
                        # Store byte to target
                        ops.append(f"{self.indent()}memref.store {load_name}, {target_info['ssa_name']}[{i}] : memref<?xi8>")
                    
                    return "\n".join(ops)
        
        # Regular variable assignment
        if assignment.target in self.symbol_table:
            target_info = self.symbol_table[assignment.target]
            mlir_type = target_info['mlir_type']

            # Re-bind the variable to the new SSA value.
            self.symbol_table[assignment.target]['ssa_name'] = value_ssa
            return "\n".join(ops)
        else:
            return f"{self.indent()}// Assignment to undefined variable: {assignment.target}"
    
    def generate_if(self, if_stmt: IfStatement) -> str:
        if self.inside_scf_for:
            return self._generate_scf_if(if_stmt)
        else:
            return self._generate_cf_if(if_stmt)
    
    def _generate_scf_if(self, if_stmt: IfStatement) -> str:
        """Generate scf.if for use inside scf.for regions"""
        mlir_code = []
        
        # Generate condition
        condition_ssa, condition_ops = self.generate_expression(if_stmt.condition)
        mlir_code.extend(condition_ops)
        
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
            current_condition = None
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
        
        mlir_code.append(f"{self.indent()}cf.cond_br {condition_ssa}, ^{current_then_block}, ^{current_else_block}")
        
        # Generate then block
        mlir_code.append(f"{self.indent()}^{current_then_block}:")
        self.indent_level += 1
        then_body = self.generate_block(if_stmt.then_block)
        if then_body.strip():
            mlir_code.append(then_body)
        mlir_code.append(f"{self.indent()}cf.br ^{end_block}")
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
            mlir_code.append(f"{self.indent()}cf.br ^{end_block}")
            self.indent_level -= 1
            
            current_block = next_elif_block
        
        # Generate else block or pass-through
        if if_stmt.else_block:
            mlir_code.append(f"{self.indent()}^{current_block}:")
            self.indent_level += 1
            else_body = self.generate_block(if_stmt.else_block)
            if else_body.strip():
                mlir_code.append(else_body)
            mlir_code.append(f"{self.indent()}cf.br ^{end_block}")
            self.indent_level -= 1
        elif current_block != end_block:
            mlir_code.append(f"{self.indent()}^{current_block}:")
            self.indent_level += 1
            mlir_code.append(f"{self.indent()}cf.br ^{end_block}")
            self.indent_level -= 1
        
        # End block
        mlir_code.append(f"{self.indent()}^{end_block}:")
        
        return "\n".join(mlir_code)
    
    def generate_while(self, while_stmt: WhileStatement) -> str:
        mlir_code = []
        
        # Create blocks
        header_block = self._new_block_label()
        body_block = self._new_block_label()
        end_block = self._new_block_label()
        
        # Jump to header
        mlir_code.append(f"{self.indent()}cf.br ^{header_block}")
        
        # Header block - check condition
        mlir_code.append(f"{self.indent()}^{header_block}:")
        condition_ssa, condition_ops = self.generate_expression(while_stmt.condition)
        if condition_ops:
            mlir_code.append("\n".join(condition_ops))
        mlir_code.append(f"{self.indent()}cf.cond_br {condition_ssa}, ^{body_block}, ^{end_block}")
        
        # Body block
        mlir_code.append(f"{self.indent()}^{body_block}:")
        self.indent_level += 1
        body_mlir = self.generate_block(while_stmt.body)
        if body_mlir.strip():
            mlir_code.append(body_mlir)
        mlir_code.append(f"{self.indent()}cf.br ^{header_block}")
        self.indent_level -= 1
        
        # End block
        mlir_code.append(f"{self.indent()}^{end_block}:")
        
        return "\n".join(mlir_code)
    
    def _collect_assigned_vars(self, block) -> set:
        """Collect all variables that are assigned in a block."""
        assigned = set()
        for stmt in block.statements:
            stmt_type = type(stmt).__name__
            if stmt_type == 'Assignment':
                if hasattr(stmt, 'target') and stmt.target_expr is None:
                    assigned.add(stmt.target)
            elif stmt_type == 'IfStatement':
                assigned.update(self._collect_assigned_vars(stmt.then_block))
                for elif_cond, elif_block in stmt.elif_blocks:
                    assigned.update(self._collect_assigned_vars(elif_block))
                if stmt.else_block:
                    assigned.update(self._collect_assigned_vars(stmt.else_block))
            elif stmt_type == 'WhileStatement':
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
                
                iter_args_str = ", ".join([f"{iter_args_init[i]} : {iter_args_types[i]}" for i in range(len(iter_args_init))])
                iter_vars_str = ", ".join(iter_vars)
                result_var = f"%{self.function_counter}"
                self.function_counter += 1
                
                mlir_code.append(f"{self.indent()}{result_var} = scf.for {iv} = {lb_idx} to {ub_idx} step {step_idx} iter_args({iter_vars_str} = {', '.join(iter_args_init)}) -> ({', '.join(iter_args_types)}) {{")
                self.indent_level += 1
                
                # Update symbol table with iter_args SSA names inside loop
                for i, var_name in enumerate(iter_args_names):
                    self.symbol_table[var_name]['ssa_name'] = iter_vars[i]
                
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
                
                self.indent_level -= 1
                mlir_code.append(f"{self.indent()}}}")
                
                # Update symbol table with result SSA names after loop
                if len(iter_args_names) == 1:
                    self.symbol_table[iter_args_names[0]]['ssa_name'] = result_var
                else:
                    # Multiple results - need to extract each
                    for i, var_name in enumerate(iter_args_names):
                        extract_var = f"%{self.function_counter}"
                        self.function_counter += 1
                        mlir_code.append(f"{self.indent()}{extract_var} = \"scf.get_result\"({result_var}) {{index = {i} : i32}} : ({', '.join(iter_args_types)}) -> {iter_args_types[i]}")
                        self.symbol_table[var_name]['ssa_name'] = extract_var
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
        assigned_vars = []
        for stmt in body.statements:
            stmt_type = type(stmt).__name__
            if stmt_type == 'Assignment':
                # Check if this variable exists in symbol table (defined before loop)
                if stmt.target in self.symbol_table and stmt.target_expr is None:
                    if stmt.target not in assigned_vars:
                        assigned_vars.append(stmt.target)
        return assigned_vars
    
    def generate_handle(self, handle_stmt: HandleStatement) -> str:
        prev = self._effect_handler_stack[-1]
        curr = dict(prev)
        curr[handle_stmt.effect] = handle_stmt.handler
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
        expr_type = type(expr).__name__
        if expr_type == 'Literal':
            return self.generate_literal(expr)
        elif expr_type == 'Variable':
            return self.generate_variable(expr)
        elif expr_type == 'BinaryOperation':
            return self.generate_binary_operation(expr)
        elif expr_type == 'UnaryOperation':
            return self.generate_unary_operation(expr)
        elif expr_type == 'FunctionCall':
            return self.generate_function_call(expr)
        elif expr_type == 'EffectCall':
            return self.generate_effect_call(expr)
        elif expr_type == 'ArrayLiteral':
            return self.generate_array_literal(expr)
        elif expr_type == 'VectorLiteral':
            return self.generate_vector_literal(expr)
        elif expr_type == 'ArrayAccess':
            return self.generate_array_access(expr)
        elif expr_type == 'FieldAccess':
            return self.generate_field_access(expr)
        elif expr_type == 'StructLiteral':
            return self.generate_struct_literal(expr)
        else:
            return f"// Unsupported expression type: {expr_type}", []
    
    def generate_literal(self, literal: Literal) -> tuple[str, List[str]]:
        ssa_name = f"%{self.function_counter}"
        self.function_counter += 1
        mlir_type = self.flow_type_to_mlir(literal.type)
        if literal.type.name == 'bool':
            mlir_type = 'i1'
        line = f"{self.indent()}{ssa_name} = arith.constant {literal.value} : {mlir_type}"
        return ssa_name, [line]
    
    def generate_variable(self, variable: Variable) -> tuple[str, List[str]]:
        if variable.name in self.symbol_table:
            var_info = self.symbol_table[variable.name]
            return var_info['ssa_name'], []
        else:
            return f"# Undefined variable: {variable.name}", []
    
    def generate_binary_operation(self, bin_op: BinaryOperation) -> tuple[str, List[str]]:
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

        # For vector operations, ensure both operands have the same type
        if is_vector:
            # Use the left type as the vector type
            operand_type = left_ty if 'vector<' in left_ty else right_ty
        else:
            # MLIR arith ops require explicit types.
            # For integer/float binary arithmetic: `... %a, %b : i32`.
            # For comparisons: `arith.cmpi slt, %a, %b : i32` and `arith.cmpf olt, %a, %b : f32`.
            #
            # Special case: scf.for induction vars are `index`, but FLOW often mixes them with i32.
            # Prefer i32 when mixing (so `acc: i32 = acc + i` works) and insert casts.
            def _maybe_cast(val: str, from_ty: str, to_ty: str) -> tuple[str, List[str]]:
                if from_ty == to_ty:
                    return val, []
                cast_name = f"%{self.function_counter}"
                self.function_counter += 1
                return cast_name, [f"{self.indent()}{cast_name} = arith.index_cast {val} : {from_ty} to {to_ty}"]

            operand_type = left_ty if left_ty != 'i32' else right_ty if right_ty != 'i32' else left_ty
            if not is_float:
                if (left_ty == 'index' and right_ty == 'i32') or (left_ty == 'i32' and right_ty == 'index'):
                    operand_type = 'i32'

        cast_ops: List[str] = []
        if not is_vector and operand_type in ('i32', 'index') and not is_float:
            if left_ty in ('i32', 'index') and left_ty != operand_type:
                left_ssa, ops = _maybe_cast(left_ssa, left_ty, operand_type)
                cast_ops.extend(ops)
            if right_ty in ('i32', 'index') and right_ty != operand_type:
                right_ssa, ops = _maybe_cast(right_ssa, right_ty, operand_type)
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
        return ssa_name, lines
    
    def generate_unary_operation(self, un_op: UnaryOperation) -> tuple[str, List[str]]:
        operand_ssa, operand_ops = self.generate_expression(un_op.operand)
        ssa_name = f"%{self.function_counter}"
        self.function_counter += 1
        
        if un_op.operator == '-':
            ty = self.get_expression_type(un_op.operand)
            if 'f32' in ty or 'f64' in ty:
                return ssa_name, operand_ops + [f"{self.indent()}{ssa_name} = arith.negf {operand_ssa} : {ty}"]
            return ssa_name, operand_ops + [f"{self.indent()}{ssa_name} = arith.subi %c0, {operand_ssa} : {ty}"]
        elif un_op.operator == '!':
            # %not = xor %x, true
            c1 = f"%{self.function_counter}"
            self.function_counter += 1
            ops = []
            ops.extend(operand_ops)
            ops.append(f"{self.indent()}{c1} = arith.constant 1 : i1")
            ops.append(f"{self.indent()}{ssa_name} = arith.xori {operand_ssa}, {c1} : i1")
            return ssa_name, ops
        else:
            return f"// Unsupported unary operator: {un_op.operator}", operand_ops
    
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
        
        # Try to determine the field type by walking the struct hierarchy
        field_type = self._determine_field_type(field_access)
        
        if not field_type:
            # Default to i32 if we can't determine the type
            ssa_name = f"%{self.function_counter}"
            self.function_counter += 1
            ops.append(f"{self.indent()}{ssa_name} = arith.constant 0 : i32")
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
                ops.append(f"{self.indent()}{byte_name} = memref.load {obj_ssa}[{offset_ssa}] : memref<?xi8>")
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
                ops.append(f"{self.indent()}{byte_name} = memref.load {obj_ssa}[{offset_ssa}] : memref<?xi8>")
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
            
            return accumulator, ops
            
        elif field_type.name in ['i8', 'u8', 'bool']:
            # Load single byte
            ops.append(f"{self.indent()}// Load {field_access.field} ({field_type.name}) at offset {offset}")
            byte_name = f"%{self.function_counter}"
            self.function_counter += 1
            ops.append(f"{self.indent()}memref.load {byte_name}, {obj_ssa}[{offset}] : memref<{total_size}xi8>")
            
            # Extend to i32 if needed
            if field_type.name in ['u8', 'bool']:
                ext_name = f"%{self.function_counter}"
                self.function_counter += 1
                ops.append(f"{self.indent()}{ext_name} = arith.extsi {byte_name} : i8 to i32")
                return ext_name, ops
            else:
                # For i8, sign extend
                ext_name = f"%{self.function_counter}"
                self.function_counter += 1
                ops.append(f"{self.indent()}{ext_name} = arith.extsi {byte_name} : i8 to i32")
                return ext_name, ops
    
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
                    
                else:
                    # For other types, just store as bytes (simplified)
                    ops.append(f"{self.indent()}// Store {field_name} ({field_type.name}) at offset {offset}")
                    ops.append(f"{self.indent()}// Value: {value_ssa}")
        
        # Cast to dynamic memref for consistency with field access
        cast_name = f"%{self.function_counter}"
        self.function_counter += 1
        ops.append(f"{self.indent()}{cast_name} = memref.cast {alloc_name} : memref<{total_size}xi8> to memref<?xi8>")
        
        # Return the casted memory pointer
        return cast_name, ops
    
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
                
                # Store each element
                for i, element_value in enumerate(element_values):
                    index_ssa = f"%{self.function_counter}"
                    self.function_counter += 1
                    ops.append(f"{self.indent()}{index_ssa} = arith.constant {i} : index")
                    ops.append(f"{self.indent()}memref.store {element_value}, {array_ssa}[{index_ssa}] : memref<{size}x{elem_type}>")
                
                return array_ssa, ops
        
        # Handle print intrinsic specially
        if func_call.name == 'print':
            return self.generate_print_call(func_call)

        # Handle printf intrinsic specially (format string + varargs)
        if func_call.name == 'printf':
            return self.generate_printf_call(func_call)
        
        ssa_name = f"%{self.function_counter}"
        self.function_counter += 1

        callee = f"@{func_call.name}"
        if func_call.name in self.symbol_table:
            func_info = self.symbol_table[func_call.name]
            callee = func_info['mlir_name']

        arg_values: List[str] = []
        ops: List[str] = []
        for arg in func_call.arguments:
            v, vops = self.generate_expression(arg)
            ops.extend(vops)
            arg_values.append(v)

        # Get expected parameter types from function signature
        expected_arg_types = []
        if func_call.name in self.symbol_table:
            func_info = self.symbol_table[func_call.name]
            for param in func_info.get('parameters', []):
                expected_arg_types.append(self.flow_type_to_mlir(param.type))
        else:
            # Fallback to expression types
            expected_arg_types = [self.get_expression_type(a) for a in func_call.arguments]
        
        # Cast arguments if needed (especially for memref size mismatches and index/i32)
        cast_args = []
        for i, (arg_val, expected_type) in enumerate(zip(arg_values, expected_arg_types)):
            actual_type = self.get_expression_type(func_call.arguments[i])
            if actual_type != expected_type and ((actual_type, expected_type) in (('index', 'i32'), ('i32', 'index'))):
                cast_arg = f"%{self.function_counter}"
                self.function_counter += 1
                ops.append(f"{self.indent()}{cast_arg} = arith.index_cast {arg_val} : {actual_type} to {expected_type}")
                cast_args.append(cast_arg)
            elif actual_type != expected_type and 'memref<' in actual_type and 'memref<' in expected_type:
                # Cast memref to expected type
                cast_arg = f"%{self.function_counter}"
                self.function_counter += 1
                ops.append(f"{self.indent()}{cast_arg} = memref.cast {arg_val} : {actual_type} to {expected_type}")
                cast_args.append(cast_arg)
            else:
                cast_args.append(arg_val)
        
        ret_type = 'i32'
        if func_call.name in self.symbol_table:
            ret_type = self.flow_type_to_mlir(self.symbol_table[func_call.name]['return_type'])
        
        ops.append(
            f"{self.indent()}{ssa_name} = func.call {callee}({', '.join(cast_args)}) : ({', '.join(expected_arg_types)}) -> {ret_type}"
        )
        return ssa_name, ops
    
    def generate_print_call(self, func_call: FunctionCall) -> tuple[str, List[str]]:
        """Generate MLIR for print() intrinsic - supports strings and numeric values."""
        self.needs_printf = True
        ops: List[str] = []
        
        for arg in func_call.arguments:
            arg_type = self.get_expression_type(arg)
            
            if isinstance(arg, Literal) and arg.type.name == 'string':
                # String literal - create global constant and get pointer
                str_val = arg.value
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
            else:
                # Numeric value - create format string and print
                arg_ssa, arg_ops = self.generate_expression(arg)
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
                
                # For f32, extend to f64 for printf
                if arg_type == 'f32':
                    ext_ssa = f"%{self.function_counter}"
                    self.function_counter += 1
                    ops.append(f"{self.indent()}{ext_ssa} = arith.extf {arg_ssa} : f32 to f64")
                    arg_ssa = ext_ssa
                    arg_type = 'f64'
                
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
            arg_type = self.get_expression_type(arg)
            arg_ssa, arg_ops = self.generate_expression(arg)
            ops.extend(arg_ops)

            # printf promotes float to double
            if arg_type == 'f32':
                ext_ssa = f"%{self.function_counter}"
                self.function_counter += 1
                ops.append(f"{self.indent()}{ext_ssa} = arith.extf {arg_ssa} : f32 to f64")
                arg_ssa = ext_ssa
                arg_type = 'f64'

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
    
    def generate_array_literal(self, array_literal: ArrayLiteral) -> tuple[str, List[str]]:
        ssa_name = f"%{self.function_counter}"
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
        
        # Create vector constant using dense notation
        elements_str = ", ".join(element_values)
        ops.append(f"{self.indent()}{ssa_name} = arith.constant dense<[{elements_str}]> : vector<{size}x{elem_type}>")
        
        return ssa_name, ops

    def generate_array_access(self, access: ArrayAccess) -> tuple[str, List[str]]:
        """Generate memref.load for array[index] access."""
        ssa_name = f"%{self.function_counter}"
        self.function_counter += 1

        ops: List[str] = []

        # Generate array expression (should resolve to a memref SSA value)
        array_ssa, array_ops = self.generate_expression(access.array)
        ops.extend(array_ops)

        # Generate index expression
        index_ssa, index_ops = self.generate_expression(access.index)
        ops.extend(index_ops)

        # Check if index is already index type (e.g., loop induction variable)
        index_type = 'i32'
        if isinstance(access.index, Variable) and access.index.name in self.symbol_table:
            index_type = self.symbol_table[access.index.name].get('mlir_type', 'i32')

        # Convert index to index type if it's an integer
        if index_type == 'index':
            final_index = index_ssa
        else:
            index_cast = f"%{self.function_counter}"
            self.function_counter += 1
            ops.append(f"{self.indent()}{index_cast} = arith.index_cast {index_ssa} : i32 to index")
            final_index = index_cast

        # Determine element type from array type
        elem_type = 'f32'  # Default; ideally infer from array's type
        if isinstance(access.array, Variable) and access.array.name in self.symbol_table:
            arr_type = self.symbol_table[access.array.name].get('mlir_type', '')
            if 'i32' in arr_type and 'memref' in arr_type:
                elem_type = 'i32'
            elif 'f64' in arr_type:
                elem_type = 'f64'
            elif 'f32' in arr_type:
                elem_type = 'f32'

        # Emit memref.load
        ops.append(f"{self.indent()}{ssa_name} = memref.load {array_ssa}[{final_index}] : memref<?x{elem_type}>")
        return ssa_name, ops
    
    def get_expression_type(self, expr: Expression) -> str:
        if isinstance(expr, Literal):
            return self.flow_type_to_mlir(expr.type)
        elif isinstance(expr, Variable):
            if expr.name in self.symbol_table:
                var_info = self.symbol_table[expr.name]
                # If we have the original FLOW type, use it
                if 'flow_type' in var_info:
                    return var_info['flow_type'].name
                return var_info.get('mlir_type', 'i32')
            else:
                return 'i32'  # Default
        elif isinstance(expr, BinaryOperation):
            left_type = self.get_expression_type(expr.left)
            right_type = self.get_expression_type(expr.right)
            # For arithmetic, prefer float types over int
            if 'f32' in left_type or 'f32' in right_type:
                return 'f32'
            if 'f64' in left_type or 'f64' in right_type:
                return 'f64'
            return left_type if left_type == right_type else 'i32'
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
        if flow_type.name in ['i8', 'i16', 'i32', 'i64', 'i128',
                              'u8', 'u16', 'u32', 'u64', 'u128',
                              'f32', 'f64']:
            return flow_type.name
        elif flow_type.name == 'bool':
            return 'i1'
        elif flow_type.name == 'void':
            return 'none'
        elif flow_type.name == 'string':
            return '!flow.string'  # Custom string type
        elif flow_type.name.startswith('memref_'):
            # memref_f32 -> memref<?xf32>
            elem = flow_type.name.replace('memref_', '')
            return f"memref<?x{elem}>"
        elif flow_type.name.startswith('array_'):
            # Array type: array_f32 -> memref<?xf32>
            if flow_type.element_type:
                return f"memref<?x{flow_type.element_type.name}>"
            else:
                return f"memref<?xi32>"
        elif flow_type.name.startswith('struct_'):
            # Struct type: struct_MyStruct -> !flow.struct<MyStruct>
            return f"!flow.struct<{flow_type.name.replace('struct_', '')}>"
        elif flow_type.name.startswith('vec'):
            # Vector type: vec4f32 -> vector<4xf32>
            if flow_type.size and flow_type.element_type:
                return f"vector<{flow_type.size}x{flow_type.element_type.name}>"
            else:
                return 'vector<?x?xf32>'  # Fallback
        elif flow_type.name.startswith('array'):
            # Array type: array_100_i32 -> memref<100xi32>
            if flow_type.size and flow_type.element_type:
                return f"memref<{flow_type.size}x{flow_type.element_type.name}>"
            elif flow_type.element_type:
                return f"memref<?x{flow_type.element_type.name}>"
            else:
                return 'memref<?xi32>'  # Fallback
        elif flow_type.name.startswith('ptr_') or flow_type.is_pointer:
            # Pointer type: ptr_f32 -> !llvm.ptr
            return '!llvm.ptr'
        else:
            # For struct types, use memref for actual memory storage
            if flow_type.name in self.struct_layouts:
                total_size = sum(field['size'] for field in self.struct_layouts[flow_type.name].values())
                return f"memref<{total_size}xi8>"  # Use byte array for struct storage
            return "memref<16xi8>"  # Default struct size (4 fields * 4 bytes)
    
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
        
        # Generate the constant value
        value_ssa, value_ops = self.generate_expression(const.value)
        
        # Add any operations needed to compute the value
        mlir_code.extend(value_ops)
        
        # Store the constant in a global variable
        mlir_type = self.flow_type_to_mlir(const.type)
        if const.type.name == 'bool':
            mlir_type = 'i1'
        
        # Create a global constant
        mlir_code.append(f"{self.indent()}llvm.mlir.global constant @{const.name}({value_ssa}) : {mlir_type}")
        
        return "\n".join(mlir_code)

def flow_to_mlir(declarations: List[Any], source_file: str = "unknown.flow", emit_debug_info: bool = False) -> str:
    generator = MLIRGenerator(source_file)
    generator.emit_debug_info = emit_debug_info
    return generator.generate_module(declarations)
