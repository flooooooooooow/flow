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
    ArrayAccess,
    ArrayLiteral,
    Assignment,
    BinaryOperation,
    Block,
    CapabilityDecl,
    CapabilityMethod,
    ConstDecl,
    EffectCall,
    EffectDecl,
    EffectOperation,
    Expression,
    FieldAccess,
    FunctionCall,
    FunctionDecl,
    HandleStatement,
    IfStatement,
    Literal,
    MatchCase,
    MatchStatement,
    ReturnStatement,
    Statement,
    StructDecl,
    StructLiteral,
    StructPattern,
    Type,
    UnaryOperation,
    VarDecl,
    Variable,
    VectorLiteral,
    WhileStatement,
    ForStatement,
)


class CGenerator:
    def __init__(self) -> None:
        self._indent = 0
        self._structs = {}  # name -> dict of field_name -> field_type
        self._var_types = {}  # name -> Type
        
        # Effect system tracking
        self._effects = {}  # effect_name -> EffectDecl
        self._capabilities = {}  # capability_name -> CapabilityDecl
        self._effect_handler_stack = [{}]  # Stack of {effect_name -> capability_name}

    def _i(self) -> str:
        return "    " * self._indent

    def generate_translation_unit(self, constants: List[ConstDecl], functions: List[FunctionDecl], 
                                   structs: List[StructDecl] = None, 
                                   effects: List[EffectDecl] = None,
                                   capabilities: List[CapabilityDecl] = None) -> str:
        lines: List[str] = []
        lines.append("#include <stdint.h>")
        lines.append("#include <stdio.h>")
        lines.append("#include <stdlib.h>")  # For malloc/free
        
        # Always include math.h - many programs use math functions
        # The linker will only include what's actually used
        lines.append("#include <math.h>")
        
        lines.append("")
        
        # Register effects and capabilities for dispatch
        if effects:
            for effect in effects:
                self._effects[effect.name] = effect
        
        if capabilities:
            for capability in capabilities:
                self._capabilities[capability.name] = capability
        
        # Generate effect handler type definitions and dispatch functions
        if effects:
            lines.extend(self._gen_effect_runtime_types(effects))

        # Emit constant declarations
        for const in constants:
            lines.append(f"static const {self._c_type(const.type)} {const.name} = {self._gen_expr(const.value)};")
            # Track constant types for print formatting
            self._var_types[const.name] = const.type
        lines.append("")

        # Collect struct types from functions and struct declarations
        all_declarations = []
        all_declarations.extend(functions)
        if structs:
            all_declarations.extend(structs)
        
        for decl in all_declarations:
            if isinstance(decl, FunctionDecl):
                self._collect_structs_from_function(decl)
            elif isinstance(decl, StructDecl):
                # Add struct declaration to the structs dictionary
                if decl.name not in self._structs:
                    self._structs[decl.name] = {}
                for field in decl.fields:
                    self._structs[decl.name][field.name] = field.type

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

        # Forward declarations for capability methods (mangled names: CapabilityName_methodName)
        for cap_name, cap in self._capabilities.items():
            for method in cap.methods:
                mangled_name = f"{cap_name}_{method.name}"
                ret = self._c_type(method.return_type)
                params = ", ".join([f"{self._c_type(p.type)} {p.name}" for p in method.parameters])
                lines.append(f"{ret} {mangled_name}({params});")
        if self._capabilities:
            lines.append("")
        
        # Generate effect vtables (after forward declarations so function pointers are valid)
        if effects:
            lines.extend(self._gen_effect_vtables(effects, capabilities or []))

        # Forward declarations
        for fn in functions:
            # Skip math functions that are provided by the standard library
            math_functions = {'sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'atan2',
                             'sinh', 'cosh', 'tanh', 'asinh', 'acosh', 'atanh',
                             'sqrt', 'cbrt', 'pow', 'exp', 'exp2', 'log', 'log2', 'log10',
                             'fabs', 'abs', 'floor', 'ceil', 'round', 'fmod',
                             'fmin', 'fmax', 'hypot'}
            if fn.name not in math_functions:
                lines.append(self._c_function_decl(fn) + ";")
        lines.append("")

        # Generate capability method definitions
        for cap_name, cap in self._capabilities.items():
            for method in cap.methods:
                lines.extend(self._gen_capability_method(cap_name, method))
                lines.append("")

        # Definitions
        for fn in functions:
            lines.extend(self._gen_function(fn))
            lines.append("")

        return "\n".join(lines).rstrip() + "\n"
    
    def _gen_capability_method(self, capability_name: str, method: CapabilityMethod) -> List[str]:
        """Generate a capability method as a standalone C function with mangled name."""
        lines: List[str] = []
        mangled_name = f"{capability_name}_{method.name}"
        ret = self._c_type(method.return_type)
        params = ", ".join([f"{self._c_type(p.type)} {p.name}" for p in method.parameters])
        
        lines.append(f"{ret} {mangled_name}({params}) {{")
        self._indent += 1
        lines.extend(self._gen_block(method.body))
        self._indent -= 1
        lines.append("}")
        return lines
    
    def _gen_effect_runtime_types(self, effects: List[EffectDecl]) -> List[str]:
        """Generate effect handler type definitions and dispatch functions."""
        lines: List[str] = []
        
        lines.append("/* ===== Effect Handler Runtime ===== */")
        lines.append("")
        
        # For each effect, generate a struct holding function pointers for its operations
        for effect in effects:
            effect_name = effect.name
            lines.append(f"/* Effect handler vtable for {effect_name} */")
            lines.append(f"typedef struct {{")
            for op in effect.operations:
                ret_type = self._c_type(op.return_type)
                param_types = ", ".join([self._c_type(p.type) for p in op.parameters])
                if not param_types:
                    param_types = "void"
                lines.append(f"    {ret_type} (*{op.name})({param_types});")
            lines.append(f"}} {effect_name}_Handler;")
            lines.append("")
            
            # Global handler pointer (thread-local for multi-threaded code)
            lines.append(f"static {effect_name}_Handler* _current_{effect_name}_handler = NULL;")
            lines.append("")
            
            # Generate dispatch functions for each operation
            for op in effect.operations:
                ret_type = self._c_type(op.return_type)
                params_with_names = ", ".join([f"{self._c_type(p.type)} {p.name}" for p in op.parameters])
                param_names = ", ".join([p.name for p in op.parameters])
                
                lines.append(f"{ret_type} {effect_name}_{op.name}({params_with_names}) {{")
                if ret_type == "void":
                    lines.append(f"    if (_current_{effect_name}_handler && _current_{effect_name}_handler->{op.name}) {{")
                    if param_names:
                        lines.append(f"        _current_{effect_name}_handler->{op.name}({param_names});")
                    else:
                        lines.append(f"        _current_{effect_name}_handler->{op.name}();")
                    lines.append(f"    }}")
                else:
                    lines.append(f"    if (_current_{effect_name}_handler && _current_{effect_name}_handler->{op.name}) {{")
                    if param_names:
                        lines.append(f"        return _current_{effect_name}_handler->{op.name}({param_names});")
                    else:
                        lines.append(f"        return _current_{effect_name}_handler->{op.name}();")
                    lines.append(f"    }}")
                    # Return default value if no handler
                    if "int" in ret_type or ret_type in ["int32_t", "int64_t", "int8_t", "int16_t"]:
                        lines.append(f"    return 0;")
                    elif ret_type in ["float", "double"]:
                        lines.append(f"    return 0.0;")
                    elif ret_type == "char*":
                        lines.append(f"    return NULL;")
                    else:
                        lines.append(f"    return ({ret_type}){{0}};")
                lines.append("}")
                lines.append("")
        
        return lines
    
    def _gen_effect_vtables(self, effects: List[EffectDecl], capabilities: List[CapabilityDecl]) -> List[str]:
        """Generate handler vtable instances (must come after capability method forward declarations)."""
        lines: List[str] = []
        
        # Generate handler vtable instances for each capability
        for cap in capabilities:
            cap_name = cap.name
            for effect_name in cap.effects:
                if effect_name in self._effects:
                    effect = self._effects[effect_name]
                    lines.append(f"/* {cap_name} handler for {effect_name} */")
                    lines.append(f"static {effect_name}_Handler _{cap_name}_{effect_name}_vtable = {{")
                    for op in effect.operations:
                        # Check if capability has this method
                        has_method = any(m.name == op.name for m in cap.methods)
                        if has_method:
                            lines.append(f"    .{op.name} = {cap_name}_{op.name},")
                        else:
                            lines.append(f"    .{op.name} = NULL,")
                    lines.append("};")
                    lines.append("")
        
        if capabilities:
            lines.append("/* ===== End Effect Handler Runtime ===== */")
            lines.append("")
        
        return lines

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
        elif isinstance(stmt, ForStatement):
            self._collect_structs_from_expr(stmt.range_start)
            self._collect_structs_from_expr(stmt.range_end)
            if stmt.step:
                self._collect_structs_from_expr(stmt.step)
            self._collect_structs_from_block(stmt.body)
        elif isinstance(stmt, HandleStatement):
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
            return expr.type  # Return the actual type of the literal
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
                             "u8", "u16", "u32", "u64", "u128", "f32", "f64", "string"]

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
        if t.name == "string":
            return "char*"  # C strings are char pointers
        # Vector types: vec2, vec4, vec8, vec16 with element type
        if t.name.startswith("vec"):
            # Parse vec4<f32> or vec4_f32
            if t.type_args and len(t.type_args) > 0:
                elem_type = t.type_args[0]
                elem_c_type = self._c_type(elem_type)
            elif "_" in t.name:
                # Handle vec4_f32 format
                parts = t.name.split("_")
                elem_c_type = self._c_type(Type(parts[1]))
            else:
                elem_c_type = "float"  # Default to float
            
            # Extract vector size from name (vec4 -> 4)
            vec_name = t.name.split("_")[0]
            if t.type_args:
                vec_name = t.name
            size_str = ''.join(c for c in vec_name if c.isdigit())
            size = int(size_str) if size_str else 4
            
            # Use GCC/Clang vector extension
            byte_size = size * (8 if elem_c_type == "double" else 4)
            return f"{elem_c_type} __attribute__((vector_size({byte_size})))"
        # Array types: array_i32, array_f32, etc.
        if t.name.startswith("array_"):
            if t.element_type:
                elem_c_type = self._c_type(t.element_type)
                if t.size:
                    return f"{elem_c_type}*"  # Fixed-size array as pointer
                return f"{elem_c_type}*"  # Dynamic array as pointer
            # Parse element type from name
            elem_type_name = t.name.replace("array_", "")
            elem_type = Type(elem_type_name)
            return f"{self._c_type(elem_type)}*"
        # Struct types
        return t.name

    def _c_function_decl(self, fn: FunctionDecl) -> str:
        ret = self._c_type(fn.return_type)
        params = ", ".join([f"{self._c_type(p.type)} {p.name}" for p in fn.parameters])
        return f"{ret} {fn.name}({params})"

    def _gen_function(self, fn: FunctionDecl) -> List[str]:
        # Skip math functions that are provided by the standard library
        math_functions = {'sin', 'cos', 'tan', 'sqrt', 'fabs', 'abs', 'log', 'exp', 'pow'}
        if fn.name in math_functions:
            return []  # Don't generate these functions
        
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
            # Handle array element assignment: arr[i] = value
            if st.target_expr is not None:
                target_expr = self._gen_expr(st.target_expr)
                return [f"{self._i()}{target_expr} = {self._gen_expr(st.value)};"]
            return [f"{self._i()}{st.target} = {self._gen_expr(st.value)};"]

        if isinstance(st, ReturnStatement):
            if st.value is None:
                return [f"{self._i()}return;"]
            return [f"{self._i()}return {self._gen_expr(st.value)};"]

        if isinstance(st, IfStatement):
            return self._gen_if(st)

        if isinstance(st, WhileStatement):
            return self._gen_while(st)
        
        if isinstance(st, ForStatement):
            return self._gen_for(st)
        
        if isinstance(st, HandleStatement):
            return self._gen_handle(st)
        
        if isinstance(st, MatchStatement):
            return self._gen_match(st)

        # Expression statement
        if isinstance(st, (Literal, Variable, BinaryOperation, UnaryOperation, FunctionCall, EffectCall)):
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
    
    def _gen_for(self, st: ForStatement) -> List[str]:
        """Generate C for loop from FLOW for statement."""
        lines: List[str] = []
        var = st.variable
        start = self._gen_expr(st.range_start)
        end = self._gen_expr(st.range_end)
        step = self._gen_expr(st.step) if st.step else "1"
        
        # Track the loop variable type
        self._var_types[var] = Type("i32")
        
        # Generate standard C for loop
        lines.append(f"{self._i()}for (int32_t {var} = {start}; {var} < {end}; {var} += {step}) {{")
        self._indent += 1
        lines.extend(self._gen_block(st.body))
        self._indent -= 1
        lines.append(f"{self._i()}}}")
        return lines
    
    def _gen_match(self, st: MatchStatement) -> List[str]:
        """Generate C switch/if-else chain from FLOW match statement."""
        lines: List[str] = []
        match_expr = self._gen_expr(st.value)
        
        # Check if we can use a switch (integer/enum patterns only)
        can_use_switch = all(
            isinstance(case.pattern, Literal) and case.pattern.type.name in ('i32', 'i64', 'i8', 'i16', 'u8', 'u16', 'u32', 'u64')
            for case in st.cases
        )
        
        if can_use_switch:
            # Generate C switch statement
            lines.append(f"{self._i()}switch ({match_expr}) {{")
            self._indent += 1
            
            for case in st.cases:
                pattern_val = self._gen_expr(case.pattern)
                lines.append(f"{self._i()}case {pattern_val}: {{")
                self._indent += 1
                lines.extend(self._gen_block(case.body))
                lines.append(f"{self._i()}break;")
                self._indent -= 1
                lines.append(f"{self._i()}}}")
            
            if st.default_case:
                lines.append(f"{self._i()}default: {{")
                self._indent += 1
                lines.extend(self._gen_block(st.default_case))
                lines.append(f"{self._i()}break;")
                self._indent -= 1
                lines.append(f"{self._i()}}}")
            
            self._indent -= 1
            lines.append(f"{self._i()}}}")
        else:
            # Generate if-else chain for complex patterns
            # Store match value in temp variable to avoid multiple evaluation
            lines.append(f"{self._i()}{{ // match block")
            self._indent += 1
            
            first = True
            for case in st.cases:
                pattern = case.pattern
                
                # Generate condition and bindings based on pattern type
                bindings = []  # List of (var_name, c_expr) to bind before body
                
                if isinstance(pattern, Literal):
                    cond = f"({match_expr}) == {self._gen_expr(pattern)}"
                elif isinstance(pattern, Variable):
                    # Variable pattern always matches - bind the value
                    cond = "1"  # Always true
                    bindings.append((pattern.name, match_expr))
                elif isinstance(pattern, StructPattern):
                    # Struct pattern: Point(a, b) matches any Point and binds fields
                    # For now, struct patterns always match (type is checked at compile time)
                    cond = "1"  # Always true - struct type check is static
                    
                    # Bind struct fields to pattern variables
                    struct_name = pattern.struct_name
                    if struct_name in self._structs:
                        field_names = list(self._structs[struct_name].keys())
                        for i, binding in enumerate(pattern.bindings):
                            if i < len(field_names):
                                field = field_names[i]
                                bindings.append((binding, f"({match_expr}).{field}"))
                else:
                    # Other patterns - try comparison
                    cond = f"({match_expr}) == {self._gen_expr(pattern)}"
                
                if first:
                    lines.append(f"{self._i()}if ({cond}) {{")
                    first = False
                else:
                    lines.append(f"{self._i()}}} else if ({cond}) {{")
                
                self._indent += 1
                
                # Generate variable bindings
                for var_name, var_expr in bindings:
                    lines.append(f"{self._i()}// pattern binding: {var_name}")
                    # Infer type from expression or use auto
                    lines.append(f"{self._i()}__auto_type {var_name} = {var_expr};")
                
                lines.extend(self._gen_block(case.body))
                self._indent -= 1
            
            if st.default_case:
                lines.append(f"{self._i()}}} else {{")
                self._indent += 1
                lines.extend(self._gen_block(st.default_case))
                self._indent -= 1
            
            if st.cases:  # Close the last if/else
                lines.append(f"{self._i()}}}")
            
            self._indent -= 1
            lines.append(f"{self._i()}}} // end match")
        
        return lines
    
    def _gen_handle(self, st: HandleStatement) -> List[str]:
        """Generate code for handle statement by setting up effect dispatch context at runtime."""
        lines: List[str] = []
        effect_name = st.effect
        handler_name = st.handler
        
        # Push new effect handler context (for compile-time tracking)
        prev_handlers = self._effect_handler_stack[-1].copy()
        prev_handlers[effect_name] = handler_name
        self._effect_handler_stack.append(prev_handlers)
        
        try:
            # Generate runtime handler setup
            lines.append(f"{self._i()}/* handle {effect_name} with {handler_name} */")
            lines.append(f"{self._i()}{{")
            self._indent += 1
            
            # Save previous handler and set new one
            lines.append(f"{self._i()}{effect_name}_Handler* _prev_{effect_name}_handler = _current_{effect_name}_handler;")
            lines.append(f"{self._i()}_current_{effect_name}_handler = &_{handler_name}_{effect_name}_vtable;")
            lines.append("")
            
            # Generate body
            lines.extend(self._gen_block(st.body))
            
            # Restore previous handler
            lines.append("")
            lines.append(f"{self._i()}_current_{effect_name}_handler = _prev_{effect_name}_handler;")
            
            self._indent -= 1
            lines.append(f"{self._i()}}}")
        finally:
            # Pop handler context
            self._effect_handler_stack.pop()
        
        return lines

    def _gen_expr(self, e: Expression) -> str:
        if isinstance(e, Literal):
            if e.type.name == "bool":
                return "1" if e.value == "true" else "0"
            elif e.type.name == "string":
                return e.value  # String literals already have quotes
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
            left_expr = self._gen_expr(e.left)
            right_expr = self._gen_expr(e.right)
            
            # Special handling for string concatenation
            if e.operator == '+':
                # Check if this is string concatenation
                left_is_string = False
                right_is_string = False
                
                # Check left operand
                if isinstance(e.left, Literal) and e.left.type.name == 'string':
                    left_is_string = True
                elif isinstance(e.left, Variable) and e.left.name in self._var_types and self._var_types[e.left.name].name == 'string':
                    left_is_string = True
                
                # Check right operand
                if isinstance(e.right, Literal) and e.right.type.name == 'string':
                    right_is_string = True
                elif isinstance(e.right, Variable) and e.right.name in self._var_types and self._var_types[e.right.name].name == 'string':
                    right_is_string = True
                
                # If either operand is a string, this is string concatenation
                if left_is_string or right_is_string:
                    # Generate separate printf calls for each part
                    parts = []
                    
                    # Handle left part
                    if isinstance(e.left, Literal) and e.left.type.name == 'string':
                        parts.append(f'printf({left_expr})')
                    elif left_is_string:
                        parts.append(f'printf("%s", {left_expr})')
                    else:
                        # Non-string left part, need format specifier
                        left_type = self._infer_expr_type(e.left)
                        if left_type.name in ['i32', 'i64']:
                            parts.append(f'printf("%d", {left_expr})')
                        elif left_type.name.startswith('u'):
                            parts.append(f'printf("%u", {left_expr})')
                        elif left_type.name in ['f32', 'f64']:
                            parts.append(f'printf("%f", {left_expr})')
                        else:
                            parts.append(f'printf("%g", {left_expr})')
                    
                    # Handle right part
                    if isinstance(e.right, Literal) and e.right.type.name == 'string':
                        parts.append(f'printf({right_expr})')
                    elif right_is_string:
                        parts.append(f'printf("%s", {right_expr})')
                    else:
                        # Non-string right part, need format specifier
                        right_type = self._infer_expr_type(e.right)
                        if right_type.name in ['i32', 'i64']:
                            parts.append(f'printf("%d", {right_expr})')
                        elif right_type.name.startswith('u'):
                            parts.append(f'printf("%u", {right_expr})')
                        elif right_type.name in ['f32', 'f64']:
                            parts.append(f'printf("%f", {right_expr})')
                        else:
                            parts.append(f'printf("%g", {right_expr})')
                    
                    # Add newline to the last part
                    if parts:
                        # Add a newline after the concatenated output
                        parts.append('printf("\\n")')
                    
                    return '; '.join(parts)
            
            # Check if we need to remove parentheses around operands
            # This prevents excessive nesting like (((a == 1) or (b == 2)))
            def remove_outer_parens(expr):
                if expr.startswith('(') and expr.endswith(')'):
                    # Check if it's safe to remove (simple check for now)
                    inner = expr[1:-1]
                    # Only remove if the inner expression doesn't have unbalanced parentheses
                    if inner.count('(') == inner.count(')'):
                        return inner
                return expr
            
            # For logical operators, be more aggressive about removing parentheses
            if e.operator in ['and', 'or']:
                left_expr = remove_outer_parens(left_expr)
                right_expr = remove_outer_parens(right_expr)
            
            # Comparison operators don't need outer parens (they have low precedence)
            if e.operator in ['==', '!=', '<', '<=', '>', '>=']:
                return f"{left_expr} {e.operator} {right_expr}"
                
            return f"({left_expr} {e.operator} {right_expr})"

        if isinstance(e, FunctionCall):
            # Handle print intrinsic
            if e.name == "print":
                if len(e.arguments) == 1:
                    arg = e.arguments[0]
                    # Check if it's a binary operation (string concatenation)
                    if isinstance(arg, BinaryOperation) and arg.operator == '+':
                        # Generate the concatenated expression directly
                        return self._gen_expr(arg)
                    # Check if it's a literal to determine format
                    elif isinstance(arg, Literal):
                        if arg.type.name == 'string':
                            # String literal - use %s
                            return f'printf({self._gen_expr(arg)})'
                        elif arg.type.name in ['f32', 'f64']:
                            # Float literal - use %f
                            return f'printf("%f", {self._gen_expr(arg)})'
                        elif arg.type.name in ['i32', 'i64', 'u32', 'u64']:
                            # Integer literal - use %d or appropriate format
                            if arg.type.name.startswith('u'):
                                return f'printf("%u", {self._gen_expr(arg)})'
                            elif arg.type.name in ['i64']:
                                return f'printf("%lld", {self._gen_expr(arg)})'
                            elif arg.type.name in ['u64']:
                                return f'printf("%llu", {self._gen_expr(arg)})'
                            else:
                                return f'printf("%d", {self._gen_expr(arg)})'
                        elif arg.type.name == 'bool':
                            # Boolean literal - use %d
                            return f'printf("%d", {self._gen_expr(arg)})'
                        else:
                            # Default to string representation
                            return f'printf("%g", {self._gen_expr(arg)})'
                    elif isinstance(arg, Variable):
                        # For variables, check if we know their type
                        if arg.name in self._var_types:
                            var_type = self._var_types[arg.name]
                            if var_type.name == 'string':
                                return f'printf("%s", {self._gen_expr(arg)})'
                            elif var_type.name in ['f32', 'f64']:
                                return f'printf("%f", {self._gen_expr(arg)})'
                            elif var_type.name in ['i32', 'i64', 'u32', 'u64']:
                                if var_type.name.startswith('u'):
                                    return f'printf("%u", {self._gen_expr(arg)})'
                                elif var_type.name in ['i64']:
                                    return f'printf("%lld", {self._gen_expr(arg)})'
                                elif var_type.name in ['u64']:
                                    return f'printf("%llu", {self._gen_expr(arg)})'
                                else:
                                    return f'printf("%d", {self._gen_expr(arg)})'
                            elif var_type.name == 'bool':
                                return f'printf("%d", {self._gen_expr(arg)})'
                        # Fall back to default
                        return f'printf("%g", {self._gen_expr(arg)})'
                    else:
                        # For expressions, default to string representation
                        return f'printf("%g", {self._gen_expr(arg)})'
                else:
                    # Multiple arguments - join with spaces
                    args = []
                    for arg in e.arguments:
                        args.append(f'printf("%g", {self._gen_expr(arg)})')
                    return ' '.join(args)
            args = ", ".join(self._gen_expr(a) for a in e.arguments)
            return f"{e.name}({args})"
        
        if isinstance(e, EffectCall):
            return self._gen_effect_call(e)
        
        if isinstance(e, ArrayAccess):
            return self._gen_array_access(e)
        
        if isinstance(e, ArrayLiteral):
            return self._gen_array_literal(e)
        
        if isinstance(e, VectorLiteral):
            # Generate vector literal using compound literal with vector extension
            # Need to determine element type and vector size from elements
            num_elems = len(e.elements)
            elements_str = ", ".join(self._gen_expr(elem) for elem in e.elements)
            
            # Infer element type from first element
            first_elem = e.elements[0] if e.elements else None
            if first_elem and isinstance(first_elem, Literal):
                if '.' in str(first_elem.value) or first_elem.type.name in ('f32', 'f64'):
                    elem_type = "float"
                else:
                    elem_type = "int32_t"
            else:
                elem_type = "float"  # Default
            
            byte_size = num_elems * (8 if elem_type == "double" else 4)
            return f"(({elem_type} __attribute__((vector_size({byte_size})))){{ {elements_str} }})"

        raise NotImplementedError(f"Unsupported expression: {type(e)}")
    
    def _gen_effect_call(self, e: EffectCall) -> str:
        """Generate code for an effect call using runtime dispatch."""
        # Always use the dispatch function which will use the runtime handler
        # The dispatch function is named: EffectName_operationName
        args = ", ".join(self._gen_expr(a) for a in e.arguments)
        return f"{e.effect_name}_{e.operation}({args})"
    
    def _gen_array_access(self, e: ArrayAccess) -> str:
        """Generate C array index access: arr[index]"""
        array_expr = self._gen_expr(e.array)
        index_expr = self._gen_expr(e.index)
        return f"{array_expr}[{index_expr}]"
    
    def _gen_array_literal(self, e: ArrayLiteral) -> str:
        """Generate C array literal initializer."""
        elements = ", ".join(self._gen_expr(elem) for elem in e.elements)
        return f"{{ {elements} }}"


def flow_to_c(declarations: List[Any]) -> str:
    """Convert FLOW declarations to C code"""
    try:
        generator = CGenerator()
        
        # Separate declarations by type
        constants = [d for d in declarations if isinstance(d, ConstDecl)]
        functions = [d for d in declarations if isinstance(d, FunctionDecl)]
        structs = [d for d in declarations if isinstance(d, StructDecl)]
        effects = [d for d in declarations if isinstance(d, EffectDecl)]
        capabilities = [d for d in declarations if isinstance(d, CapabilityDecl)]
        
        return generator.generate_translation_unit(constants, functions, structs, effects, capabilities)
    except Exception as e:
        print(f"C generation error: {e}")
        import traceback
        traceback.print_exc()
        raise
