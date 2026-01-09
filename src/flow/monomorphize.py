"""
FLOW Monomorphization Pass

Transforms generic functions and structs into concrete, specialized versions.

For example:
    struct Option<T> { has_value: bool, value: T }
    function identity<T>(x: T) -> T { return x }
    
    let opt: Option<i32> = ...
    let x: i32 = identity<i32>(42)

Becomes:
    struct Option_i32 { has_value: bool, value: i32 }
    function identity_i32(x: i32) -> i32 { return x }
    
    let opt: Option_i32 = ...
    let x: i32 = identity_i32(42)

This approach (similar to Rust) has:
- Zero runtime overhead
- Full type safety
- Larger binary size (acceptable tradeoff)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Optional, Any
from copy import deepcopy

from .parser import (
    FunctionDecl, StructDecl, Type, Parameter, Block, Statement,
    VarDecl, ReturnStatement, Assignment, IfStatement, WhileStatement,
    ForStatement, BinaryOperation, UnaryOperation, FunctionCall,
    Literal, Variable, StructLiteral, ArrayLiteral, FieldAccess,
    ArrayAccess, Expression
)


@dataclass
class GenericDef:
    """A generic type or function definition."""
    name: str
    type_params: List[str]
    decl: Any  # FunctionDecl or StructDecl


@dataclass
class MonomorphRequest:
    """A request to monomorphize a generic with specific type arguments."""
    name: str
    type_args: List[Type]
    
    @property
    def mangled_name(self) -> str:
        """Generate the monomorphized name: Option<i32> -> Option_i32"""
        if not self.type_args:
            return self.name
        args_str = '_'.join(self._type_to_str(t) for t in self.type_args)
        return f"{self.name}_{args_str}"
    
    def _type_to_str(self, t: Type) -> str:
        """Convert type to string for name mangling."""
        # Handle nested generic types
        if t.type_args:
            inner = '_'.join(self._type_to_str(arg) for arg in t.type_args)
            return f"{t.name.split('_')[0]}_{inner}"
        return t.name


class Monomorphizer:
    """
    Performs monomorphization on FLOW declarations.
    
    Usage:
        mono = Monomorphizer()
        new_decls = mono.monomorphize(declarations)
    """
    
    def __init__(self):
        # Generic definitions: name -> GenericDef
        self.generic_structs: Dict[str, GenericDef] = {}
        self.generic_functions: Dict[str, GenericDef] = {}
        
        # Monomorphization requests (what we need to generate)
        self.struct_requests: Dict[str, MonomorphRequest] = {}
        self.function_requests: Dict[str, MonomorphRequest] = {}
        
        # Already generated specialized versions
        self.generated_structs: Dict[str, StructDecl] = {}
        self.generated_functions: Dict[str, FunctionDecl] = {}
    
    def monomorphize(self, declarations: List[Any]) -> List[Any]:
        """
        Main entry point. Returns declarations with generics replaced
        by specialized versions.
        """
        # Phase 1: Collect generic definitions
        self._collect_generics(declarations)
        
        # Phase 2: Find all usages and create requests
        self._collect_usages(declarations)
        
        # Phase 3: Generate specialized versions
        self._generate_specializations()
        
        # Phase 4: Rewrite declarations
        return self._rewrite_declarations(declarations)
    
    def _collect_generics(self, declarations: List[Any]) -> None:
        """Find all generic struct and function definitions."""
        for decl in declarations:
            if isinstance(decl, StructDecl) and decl.type_params:
                self.generic_structs[decl.name] = GenericDef(
                    name=decl.name,
                    type_params=decl.type_params,
                    decl=decl
                )
            elif isinstance(decl, FunctionDecl) and decl.type_params:
                self.generic_functions[decl.name] = GenericDef(
                    name=decl.name,
                    type_params=decl.type_params,
                    decl=decl
                )
    
    def _collect_usages(self, declarations: List[Any]) -> None:
        """Find all places where generics are instantiated."""
        for decl in declarations:
            if isinstance(decl, FunctionDecl):
                self._scan_function(decl)
            elif isinstance(decl, StructDecl):
                self._scan_struct(decl)
    
    def _scan_struct(self, struct: StructDecl) -> None:
        """Scan struct fields for generic type usages."""
        # Get type params for this struct (if it's generic, we skip those)
        type_params = set(struct.type_params) if struct.type_params else set()
        
        for field in struct.fields:
            self._scan_type(field.type, type_params)
    
    def _scan_function(self, fn: FunctionDecl) -> None:
        """Scan function for generic type usages."""
        # Get type params for this function (if it's generic, we skip those)
        type_params = set(fn.type_params) if fn.type_params else set()
        
        # Check return type
        self._scan_type(fn.return_type, type_params)
        
        # Check parameters
        for param in fn.parameters:
            self._scan_type(param.type, type_params)
        
        # Check body (only scan non-generic functions)
        if not fn.type_params:
            self._scan_block(fn.body)
    
    def _scan_block(self, block: Block) -> None:
        """Scan a block of statements."""
        for stmt in block.statements:
            self._scan_statement(stmt)
    
    def _scan_statement(self, stmt: Statement) -> None:
        """Scan a statement for generic usages."""
        if isinstance(stmt, VarDecl):
            self._scan_type(stmt.type)
            if stmt.initializer:
                self._scan_expression(stmt.initializer)
        elif isinstance(stmt, ReturnStatement):
            if stmt.value:
                self._scan_expression(stmt.value)
        elif isinstance(stmt, Assignment):
            self._scan_expression(stmt.value)
        elif isinstance(stmt, IfStatement):
            self._scan_expression(stmt.condition)
            self._scan_block(stmt.then_block)
            for elif_cond, elif_block in stmt.elif_blocks:
                self._scan_expression(elif_cond)
                self._scan_block(elif_block)
            if stmt.else_block:
                self._scan_block(stmt.else_block)
        elif isinstance(stmt, WhileStatement):
            self._scan_expression(stmt.condition)
            self._scan_block(stmt.body)
        elif isinstance(stmt, ForStatement):
            self._scan_expression(stmt.range_start)
            self._scan_expression(stmt.range_end)
            self._scan_block(stmt.body)
        elif isinstance(stmt, Block):
            self._scan_block(stmt)
    
    def _scan_expression(self, expr: Expression) -> None:
        """Scan an expression for generic usages."""
        if isinstance(expr, FunctionCall):
            # Check if this is a generic function call
            if expr.name in self.generic_functions:
                # Try to infer type args from arguments
                self._request_function_mono(expr)
            # Scan arguments
            for arg in expr.arguments:
                self._scan_expression(arg)
        elif isinstance(expr, StructLiteral):
            # Check if struct name refers to a generic
            struct_name = expr.struct_name
            # Check if this is a monomorphized name like Option_i32 or Pair_i32_f32
            if '_' in struct_name:
                base_name = struct_name.split('_')[0]
                if base_name in self.generic_structs:
                    # Extract type args from mangled name
                    # For Pair_i32_f32, we need to extract [i32, f32]
                    # Number of type params tells us how many args to expect
                    generic_def = self.generic_structs[base_name]
                    num_type_params = len(generic_def.type_params)
                    
                    # Split the suffix: "i32_f32" -> ["i32", "f32"]
                    suffix = struct_name[len(base_name)+1:]
                    parts = suffix.split('_')
                    
                    # Map parts to type args
                    if len(parts) >= num_type_params:
                        type_args = [Type(parts[i]) for i in range(num_type_params)]
                    else:
                        # Fallback: treat entire suffix as one arg
                        type_args = [Type(suffix)]
                    
                    req = MonomorphRequest(base_name, type_args)
                    self.struct_requests[req.mangled_name] = req
            # Scan field values
            for _, value in expr.fields:
                self._scan_expression(value)
        elif isinstance(expr, BinaryOperation):
            self._scan_expression(expr.left)
            self._scan_expression(expr.right)
        elif isinstance(expr, UnaryOperation):
            self._scan_expression(expr.operand)
        elif isinstance(expr, FieldAccess):
            self._scan_expression(expr.object)
        elif isinstance(expr, ArrayAccess):
            self._scan_expression(expr.array)
            self._scan_expression(expr.index)
        elif isinstance(expr, ArrayLiteral):
            for elem in expr.elements:
                self._scan_expression(elem)
    
    def _scan_type(self, t: Type, type_params: Set[str] = None) -> None:
        """Check if a type is a generic instantiation and register it."""
        if not t:
            return
        
        if type_params is None:
            type_params = set()
        
        # Skip if this is a type parameter (like T in generic context)
        if t.name in type_params:
            return
        
        # Check for generic type with type arguments: Option<i32>
        if t.type_args:
            base_name = t.name.split('_')[0]  # Handle both Option and Option_i32
            if base_name in self.generic_structs:
                # Only create request if ALL type args are concrete (not type params)
                all_concrete = all(arg.name not in type_params for arg in t.type_args)
                if all_concrete:
                    req = MonomorphRequest(base_name, t.type_args)
                    self.struct_requests[req.mangled_name] = req
                # Recursively scan type arguments
                for arg in t.type_args:
                    self._scan_type(arg, type_params)
        
        # Check element type for arrays/pointers
        if t.element_type:
            self._scan_type(t.element_type, type_params)
    
    def _request_function_mono(self, call: FunctionCall) -> None:
        """Request monomorphization for a function call."""
        # For now, we infer type args from the first argument's type
        # TODO: Proper type inference from all arguments
        if call.arguments and call.name in self.generic_functions:
            generic_def = self.generic_functions[call.name]
            # Simple heuristic: use first argument's type
            # Full implementation would do proper type inference
            pass  # TODO: Implement type argument inference
    
    def _generate_specializations(self) -> None:
        """Generate all requested specializations."""
        # Generate struct specializations
        for mangled_name, req in self.struct_requests.items():
            if mangled_name not in self.generated_structs:
                self._generate_struct(req)
        
        # Generate function specializations
        for mangled_name, req in self.function_requests.items():
            if mangled_name not in self.generated_functions:
                self._generate_function(req)
    
    def _generate_struct(self, req: MonomorphRequest) -> None:
        """Generate a specialized struct."""
        generic_def = self.generic_structs.get(req.name)
        if not generic_def:
            return
        
        original = generic_def.decl
        type_map = dict(zip(generic_def.type_params, req.type_args))
        
        # Create new fields with substituted types
        new_fields = []
        for field in original.fields:
            new_type = self._substitute_type(field.type, type_map)
            new_fields.append(Parameter(field.name, new_type))
        
        # Create specialized struct
        specialized = StructDecl(
            name=req.mangled_name,
            fields=new_fields,
            is_exported=original.is_exported,
            type_params=[]  # No longer generic
        )
        
        self.generated_structs[req.mangled_name] = specialized
    
    def _generate_function(self, req: MonomorphRequest) -> None:
        """Generate a specialized function."""
        generic_def = self.generic_functions.get(req.name)
        if not generic_def:
            return
        
        original = generic_def.decl
        type_map = dict(zip(generic_def.type_params, req.type_args))
        
        # Substitute in parameters
        new_params = []
        for param in original.parameters:
            new_type = self._substitute_type(param.type, type_map)
            new_params.append(Parameter(param.name, new_type))
        
        # Substitute in return type
        new_return = self._substitute_type(original.return_type, type_map)
        
        # Substitute in body (deep copy and rewrite)
        new_body = self._substitute_block(deepcopy(original.body), type_map)
        
        # Create specialized function
        specialized = FunctionDecl(
            name=req.mangled_name,
            parameters=new_params,
            return_type=new_return,
            body=new_body,
            attributes=original.attributes,
            is_exported=original.is_exported,
            is_extern=original.is_extern,
            type_params=[]  # No longer generic
        )
        
        self.generated_functions[req.mangled_name] = specialized
    
    def _substitute_type(self, t: Type, type_map: Dict[str, Type]) -> Type:
        """Substitute type parameters with concrete types."""
        if not t:
            return t
        
        # Check if this is a type parameter
        if t.name in type_map:
            return type_map[t.name]
        
        # Handle generic types with type arguments
        if t.type_args:
            new_args = [self._substitute_type(arg, type_map) for arg in t.type_args]
            # Check if base is a generic struct
            base_name = t.name.split('_')[0]
            if base_name in self.generic_structs:
                req = MonomorphRequest(base_name, new_args)
                self.struct_requests[req.mangled_name] = req
                return Type(req.mangled_name, type_args=[])
            return Type(t.name, t.is_pointer, t.is_reference, t.size, t.element_type, new_args)
        
        # Handle element types (arrays, pointers)
        if t.element_type:
            new_elem = self._substitute_type(t.element_type, type_map)
            return Type(t.name, t.is_pointer, t.is_reference, t.size, new_elem, t.type_args)
        
        return t
    
    def _substitute_block(self, block: Block, type_map: Dict[str, Type]) -> Block:
        """Substitute types in a block."""
        new_stmts = [self._substitute_statement(s, type_map) for s in block.statements]
        return Block(new_stmts)
    
    def _substitute_statement(self, stmt: Statement, type_map: Dict[str, Type]) -> Statement:
        """Substitute types in a statement."""
        if isinstance(stmt, VarDecl):
            new_type = self._substitute_type(stmt.type, type_map)
            new_init = self._substitute_expression(stmt.initializer, type_map) if stmt.initializer else None
            return VarDecl(stmt.name, new_type, new_init)
        elif isinstance(stmt, ReturnStatement):
            new_value = self._substitute_expression(stmt.value, type_map) if stmt.value else None
            return ReturnStatement(new_value)
        elif isinstance(stmt, Assignment):
            new_value = self._substitute_expression(stmt.value, type_map)
            new_target_expr = self._substitute_expression(stmt.target_expr, type_map) if stmt.target_expr else None
            return Assignment(stmt.target, new_value, new_target_expr)
        elif isinstance(stmt, IfStatement):
            new_cond = self._substitute_expression(stmt.condition, type_map)
            new_then = self._substitute_block(stmt.then_block, type_map)
            new_elifs = [(self._substitute_expression(c, type_map), self._substitute_block(b, type_map)) 
                        for c, b in stmt.elif_blocks]
            new_else = self._substitute_block(stmt.else_block, type_map) if stmt.else_block else None
            return IfStatement(new_cond, new_then, new_elifs, new_else)
        elif isinstance(stmt, WhileStatement):
            new_cond = self._substitute_expression(stmt.condition, type_map)
            new_body = self._substitute_block(stmt.body, type_map)
            return WhileStatement(new_cond, new_body)
        elif isinstance(stmt, ForStatement):
            new_start = self._substitute_expression(stmt.range_start, type_map)
            new_end = self._substitute_expression(stmt.range_end, type_map)
            new_step = self._substitute_expression(stmt.step, type_map) if stmt.step else None
            new_body = self._substitute_block(stmt.body, type_map)
            return ForStatement(stmt.variable, new_start, new_end, new_step, new_body, stmt.is_parallel)
        elif isinstance(stmt, Block):
            return self._substitute_block(stmt, type_map)
        return stmt
    
    def _substitute_expression(self, expr: Expression, type_map: Dict[str, Type]) -> Expression:
        """Substitute types in an expression."""
        if isinstance(expr, FunctionCall):
            new_args = [self._substitute_expression(a, type_map) for a in expr.arguments]
            # Check if calling a generic function
            if expr.name in self.generic_functions:
                # TODO: Proper type argument inference
                pass
            return FunctionCall(expr.name, new_args)
        elif isinstance(expr, StructLiteral):
            new_fields = [(n, self._substitute_expression(v, type_map)) for n, v in expr.fields]
            # Handle monomorphized struct names
            struct_name = expr.struct_name
            if '_' in struct_name:
                base = struct_name.split('_')[0]
                if base in self.generic_structs:
                    # Keep the monomorphized name
                    pass
            return StructLiteral(struct_name, new_fields)
        elif isinstance(expr, BinaryOperation):
            new_left = self._substitute_expression(expr.left, type_map)
            new_right = self._substitute_expression(expr.right, type_map)
            return BinaryOperation(new_left, expr.operator, new_right)
        elif isinstance(expr, UnaryOperation):
            new_operand = self._substitute_expression(expr.operand, type_map)
            return UnaryOperation(expr.operator, new_operand)
        elif isinstance(expr, FieldAccess):
            new_obj = self._substitute_expression(expr.object, type_map)
            return FieldAccess(new_obj, expr.field)
        elif isinstance(expr, ArrayAccess):
            new_arr = self._substitute_expression(expr.array, type_map)
            new_idx = self._substitute_expression(expr.index, type_map)
            return ArrayAccess(new_arr, new_idx)
        elif isinstance(expr, ArrayLiteral):
            new_elems = [self._substitute_expression(e, type_map) for e in expr.elements]
            return ArrayLiteral(new_elems)
        return expr
    
    def _rewrite_declarations(self, declarations: List[Any]) -> List[Any]:
        """
        Rewrite declarations:
        1. Remove generic definitions
        2. Add specialized versions
        3. Update usages to use specialized names
        """
        result = []
        
        # Add specialized structs first (they may be needed by functions)
        for struct in self.generated_structs.values():
            result.append(struct)
        
        # Add specialized functions
        for fn in self.generated_functions.values():
            result.append(fn)
        
        # Add non-generic declarations (with rewritten type usages)
        for decl in declarations:
            if isinstance(decl, StructDecl):
                if decl.type_params:
                    continue  # Skip generic definition
                # Rewrite field types
                new_decl = self._rewrite_struct(decl)
                result.append(new_decl)
            elif isinstance(decl, FunctionDecl):
                if decl.type_params:
                    continue  # Skip generic definition
                # Rewrite types in function
                new_decl = self._rewrite_function(decl)
                result.append(new_decl)
            else:
                result.append(decl)
        
        return result
    
    def _rewrite_struct(self, struct: StructDecl) -> StructDecl:
        """Rewrite types in a struct to use monomorphized names."""
        new_fields = []
        for field in struct.fields:
            new_type = self._rewrite_type(field.type)
            new_fields.append(Parameter(field.name, new_type))
        return StructDecl(struct.name, new_fields, struct.is_exported, struct.type_params)
    
    def _rewrite_function(self, fn: FunctionDecl) -> FunctionDecl:
        """Rewrite types in a function to use monomorphized names."""
        new_params = []
        for param in fn.parameters:
            new_type = self._rewrite_type(param.type)
            new_params.append(Parameter(param.name, new_type))
        
        new_return = self._rewrite_type(fn.return_type)
        new_body = self._rewrite_block(fn.body)
        
        return FunctionDecl(
            fn.name, new_params, new_return, new_body, fn.attributes,
            fn.is_exported, fn.is_extern, fn.type_params
        )
    
    def _rewrite_type(self, t: Type) -> Type:
        """Rewrite a type to use monomorphized struct names."""
        if not t:
            return t
        
        if t.type_args:
            base_name = t.name.split('_')[0]
            if base_name in self.generic_structs:
                req = MonomorphRequest(base_name, t.type_args)
                return Type(req.mangled_name, type_args=[])
        
        if t.element_type:
            new_elem = self._rewrite_type(t.element_type)
            return Type(t.name, t.is_pointer, t.is_reference, t.size, new_elem, t.type_args)
        
        return t
    
    def _rewrite_block(self, block: Block) -> Block:
        """Rewrite a block to use monomorphized names."""
        new_stmts = [self._rewrite_statement(s) for s in block.statements]
        return Block(new_stmts)
    
    def _rewrite_statement(self, stmt: Statement) -> Statement:
        """Rewrite a statement to use monomorphized names."""
        if isinstance(stmt, VarDecl):
            new_type = self._rewrite_type(stmt.type)
            new_init = self._rewrite_expression(stmt.initializer) if stmt.initializer else None
            return VarDecl(stmt.name, new_type, new_init)
        elif isinstance(stmt, ReturnStatement):
            new_value = self._rewrite_expression(stmt.value) if stmt.value else None
            return ReturnStatement(new_value)
        elif isinstance(stmt, Assignment):
            new_value = self._rewrite_expression(stmt.value)
            new_target_expr = self._rewrite_expression(stmt.target_expr) if stmt.target_expr else None
            return Assignment(stmt.target, new_value, new_target_expr)
        elif isinstance(stmt, IfStatement):
            new_cond = self._rewrite_expression(stmt.condition)
            new_then = self._rewrite_block(stmt.then_block)
            new_elifs = [(self._rewrite_expression(c), self._rewrite_block(b)) for c, b in stmt.elif_blocks]
            new_else = self._rewrite_block(stmt.else_block) if stmt.else_block else None
            return IfStatement(new_cond, new_then, new_elifs, new_else)
        elif isinstance(stmt, WhileStatement):
            new_cond = self._rewrite_expression(stmt.condition)
            new_body = self._rewrite_block(stmt.body)
            return WhileStatement(new_cond, new_body)
        elif isinstance(stmt, ForStatement):
            new_start = self._rewrite_expression(stmt.range_start)
            new_end = self._rewrite_expression(stmt.range_end)
            new_step = self._rewrite_expression(stmt.step) if stmt.step else None
            new_body = self._rewrite_block(stmt.body)
            return ForStatement(stmt.variable, new_start, new_end, new_step, new_body, stmt.is_parallel)
        elif isinstance(stmt, Block):
            return self._rewrite_block(stmt)
        return stmt
    
    def _rewrite_expression(self, expr: Expression) -> Expression:
        """Rewrite an expression to use monomorphized names."""
        if isinstance(expr, FunctionCall):
            new_args = [self._rewrite_expression(a) for a in expr.arguments]
            return FunctionCall(expr.name, new_args)
        elif isinstance(expr, StructLiteral):
            new_fields = [(n, self._rewrite_expression(v)) for n, v in expr.fields]
            return StructLiteral(expr.struct_name, new_fields)
        elif isinstance(expr, BinaryOperation):
            new_left = self._rewrite_expression(expr.left)
            new_right = self._rewrite_expression(expr.right)
            return BinaryOperation(new_left, expr.operator, new_right)
        elif isinstance(expr, UnaryOperation):
            new_operand = self._rewrite_expression(expr.operand)
            return UnaryOperation(expr.operator, new_operand)
        elif isinstance(expr, FieldAccess):
            new_obj = self._rewrite_expression(expr.object)
            return FieldAccess(new_obj, expr.field)
        elif isinstance(expr, ArrayAccess):
            new_arr = self._rewrite_expression(expr.array)
            new_idx = self._rewrite_expression(expr.index)
            return ArrayAccess(new_arr, new_idx)
        elif isinstance(expr, ArrayLiteral):
            new_elems = [self._rewrite_expression(e) for e in expr.elements]
            return ArrayLiteral(new_elems)
        return expr


def monomorphize(declarations: List[Any]) -> List[Any]:
    """
    Convenience function to monomorphize a list of declarations.
    
    Args:
        declarations: List of parsed declarations
        
    Returns:
        List of declarations with generics replaced by specialized versions
    """
    mono = Monomorphizer()
    return mono.monomorphize(declarations)
