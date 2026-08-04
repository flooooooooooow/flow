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

from dataclasses import dataclass
from typing import Dict, List, Set, Any

from .parser import (
    FunctionDecl, StructDecl, Type, Parameter, Block, Statement,
    VarDecl, ReturnStatement, Assignment, IfStatement, WhileStatement,
    ForStatement, BinaryOperation, UnaryOperation, FunctionCall,
    Literal, StructLiteral, ArrayLiteral, FieldAccess,
    ArrayAccess, Expression, ImplDecl, TraitDecl, EnumDecl, TypeParameter, CastExpression,
    ExpectStatement, RecordUpdate,
)


def get_type_param_names(type_params) -> List[str]:
    """Extract parameter names from type_params (handles both str and TypeParameter)."""
    if not type_params:
        return []
    result = []
    for p in type_params:
        if isinstance(p, TypeParameter):
            result.append(p.name)
        elif isinstance(p, str):
            result.append(p)
        else:
            result.append(str(p))
    return result


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
        """Convert type to string for name mangling (unambiguous)."""
        parts: List[str] = []
        if getattr(t, "is_pointer", False):
            parts.append("P")
        if getattr(t, "is_reference", False):
            parts.append("R")
        if getattr(t, "is_capability", False):
            parts.append("C")

        name = t.name or ""
        parts.append(f"N{len(name)}_{name}")

        if t.size is not None:
            parts.append(f"S{t.size}")
        if t.element_type is not None:
            parts.append(f"E{self._type_to_str(t.element_type)}")
        if t.type_args:
            inner = "_".join(self._type_to_str(arg) for arg in t.type_args)
            parts.append(f"T{len(t.type_args)}_{inner}")

        return "__".join(parts)


MAX_INSTANTIATION_DEPTH = 64


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

        # Guard against infinite instantiation (e.g. List<List<List<...>>>)
        self._instantiation_depth: int = 0
    
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
                    type_params=get_type_param_names(decl.type_params),
                    decl=decl
                )
            elif isinstance(decl, FunctionDecl) and decl.type_params:
                self.generic_functions[decl.name] = GenericDef(
                    name=decl.name,
                    type_params=get_type_param_names(decl.type_params),
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
        type_param_names = get_type_param_names(struct.type_params)
        type_params = set(type_param_names) if type_param_names else set()
        
        for field in struct.fields:
            self._scan_type(field.type, type_params)
    
    def _scan_function(self, fn: FunctionDecl) -> None:
        """Scan function for generic type usages."""
        # Get type params for this function (if it's generic, we skip those)
        type_param_names = get_type_param_names(fn.type_params)
        type_params = set(type_param_names) if type_param_names else set()
        
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
        elif isinstance(stmt, ExpectStatement):
            self._scan_expression(stmt.condition)
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
        elif isinstance(expr, CastExpression):
            self._scan_expression(expr.expr)
            self._scan_type(expr.target_type)
    
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
        if not call.arguments or call.name not in self.generic_functions:
            return

        generic_def = self.generic_functions[call.name]
        original = generic_def.decl
        num_type_params = len(generic_def.type_params)

        # If the call has explicit type arguments, use them directly
        if hasattr(call, 'type_args') and call.type_args and len(call.type_args) == num_type_params:
            req = MonomorphRequest(call.name, call.type_args)
            self.function_requests[req.mangled_name] = req
            return

        # Otherwise, infer type args from arguments by matching parameter types
        # to the generic type parameters.
        type_param_map: dict = {}  # type_param_name -> concrete Type
        for arg, param in zip(call.arguments, original.parameters):
            self._infer_type_arg(arg, param.type, generic_def.type_params, type_param_map)

        # Build type_args list in order of generic_def.type_params
        if len(type_param_map) == num_type_params:
            type_args = [type_param_map[tp] for tp in generic_def.type_params]
            req = MonomorphRequest(call.name, type_args)
            self.function_requests[req.mangled_name] = req

    def _infer_type_arg(self, arg: Expression, param_type: Type,
                        type_params: list, result: dict) -> None:
        """Infer concrete type for a type parameter from an argument expression."""
        if not param_type:
            return
        # If the parameter type is itself a type parameter, infer from the argument
        if param_type.name in type_params:
            concrete = self._expr_type(arg)
            if concrete and param_type.name not in result:
                result[param_type.name] = concrete

    def _expr_type(self, expr: Expression) -> 'Type | None':
        """Try to infer the concrete type of an expression."""
        if isinstance(expr, Literal):
            if hasattr(expr, 'type') and expr.type:
                return expr.type
            val = expr.value
            if isinstance(val, bool):
                return Type("bool")
            if isinstance(val, int):
                return Type("i32")
            if isinstance(val, float):
                return Type("f32")
            if isinstance(val, str):
                if val in ("true", "false"):
                    return Type("bool")
                try:
                    float(val)
                    return Type("f32") if '.' in val else Type("i32")
                except (ValueError, TypeError):
                    return Type("string")
        elif isinstance(expr, StructLiteral):
            return Type(expr.struct_name)
        elif isinstance(expr, RecordUpdate):
            return self._expr_type(expr.base)
        elif isinstance(expr, ArrayLiteral):
            if expr.elements:
                elem_type = self._expr_type(expr.elements[0])
                if elem_type:
                    return Type(f"array_{elem_type.name}")
        elif isinstance(expr, CastExpression):
            return expr.target_type
        return None
    
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

    def _check_instantiation_depth(self, name: str) -> None:
        """Guard against infinite recursive instantiation."""
        if self._instantiation_depth > MAX_INSTANTIATION_DEPTH:
            raise RecursionError(
                f"Monomorphization depth limit ({MAX_INSTANTIATION_DEPTH}) exceeded "
                f"while instantiating '{name}'. This usually indicates an infinitely "
                f"recursive generic type (e.g. struct List<T> {{ next: List<T> }})."
            )
    
    def _generate_struct(self, req: MonomorphRequest) -> None:
        """Generate a specialized struct."""
        self._check_instantiation_depth(req.mangled_name)
        generic_def = self.generic_structs.get(req.name)
        if not generic_def:
            return

        self._instantiation_depth += 1
        try:
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
        finally:
            self._instantiation_depth -= 1
    
    def _generate_function(self, req: MonomorphRequest) -> None:
        """Generate a specialized function."""
        self._check_instantiation_depth(req.mangled_name)
        generic_def = self.generic_functions.get(req.name)
        if not generic_def:
            return

        self._instantiation_depth += 1
        try:
            self._generate_function_inner(req, generic_def)
        finally:
            self._instantiation_depth -= 1

    def _generate_function_inner(self, req: MonomorphRequest, generic_def: GenericDef) -> None:
        original = generic_def.decl
        type_map = dict(zip(generic_def.type_params, req.type_args))
        
        # Substitute in parameters
        new_params = []
        for param in original.parameters:
            new_type = self._substitute_type(param.type, type_map)
            new_params.append(Parameter(param.name, new_type))
        
        # Substitute in return type
        new_return = self._substitute_type(original.return_type, type_map)
        
        # Substitute in body without deep-copying the whole AST
        new_body = self._substitute_block(original.body, type_map)
        
        # Create specialized function
        specialized = FunctionDecl(
            name=req.mangled_name,
            parameters=new_params,
            return_type=new_return,
            body=new_body,
            attributes=original.attributes,
            is_exported=original.is_exported,
            is_extern=original.is_extern,
            type_params=[],  # No longer generic
            location=getattr(original, "location", None),
        )
        # Preserve other attributes
        if hasattr(original, "has_self"):
            specialized.has_self = original.has_self
        if hasattr(original, "is_forward_decl"):
            specialized.is_forward_decl = original.is_forward_decl
        
        self.generated_functions[req.mangled_name] = specialized
    
    def _resolve_struct_literal_mangled_name(self, struct_name: str, type_map: Dict[str, Type] = None) -> str:
        """Map a parser-mangled struct literal name (e.g. `Box_i32`, or
        `Box_T` while still inside a generic function body) to the fully
        monomorphized struct name used for the actual generated definition
        (e.g. `Box_N3_i32` via `MonomorphRequest.mangled_name`).

        The parser mangles `Box<i32> { ... }` to `Box_i32` using simple
        underscore-joined type names, but `MonomorphRequest.mangled_name`
        (used to name the actual generated `struct Box_N3_i32 { ... }`)
        uses a longer-form encoding to stay unambiguous for compound types.
        Without this translation, struct literal expressions end up
        referencing a type name that was never defined in the generated C.
        """
        if '_' not in struct_name:
            return struct_name
        base_name = struct_name.split('_')[0]
        if base_name not in self.generic_structs:
            return struct_name

        generic_def = self.generic_structs[base_name]
        num_type_params = len(generic_def.type_params)
        suffix = struct_name[len(base_name) + 1:]
        parts = suffix.split('_')
        if len(parts) >= num_type_params:
            type_args = [Type(parts[i]) for i in range(num_type_params)]
        else:
            type_args = [Type(suffix)]

        if type_map:
            type_args = [type_map.get(arg.name, arg) for arg in type_args]

        req = MonomorphRequest(base_name, type_args)
        self.struct_requests[req.mangled_name] = req
        return req.mangled_name

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
            return Type(name=t.name, is_pointer=t.is_pointer, is_reference=t.is_reference, 
                        is_capability=getattr(t, 'is_capability', False), size=t.size, 
                        element_type=t.element_type, type_args=new_args)
        
        # Handle element types (arrays, pointers)
        if t.element_type:
            new_elem = self._substitute_type(t.element_type, type_map)
            return Type(name=t.name, is_pointer=t.is_pointer, is_reference=t.is_reference,
                        is_capability=getattr(t, 'is_capability', False), size=t.size,
                        element_type=new_elem, type_args=t.type_args)
        
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
            return VarDecl(stmt.name, new_type, new_init, is_mutable=getattr(stmt, "is_mutable", False))
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
        elif isinstance(stmt, ExpectStatement):
            return ExpectStatement(
                self._substitute_expression(stmt.condition, type_map), stmt.line
            )
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
            new_name = self._resolve_struct_literal_mangled_name(expr.struct_name, type_map)
            return StructLiteral(new_name, new_fields)
        elif isinstance(expr, RecordUpdate):
            return RecordUpdate(
                self._substitute_expression(expr.base, type_map),
                [(n, self._substitute_expression(v, type_map)) for n, v in expr.updates],
            )
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
        elif isinstance(expr, CastExpression):
            new_expr = self._substitute_expression(expr.expr, type_map)
            new_target = self._substitute_type(expr.target_type, type_map)
            return CastExpression(new_expr, new_target)
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
            elif isinstance(decl, ImplDecl):
                # Rewrite methods in impl block
                new_methods = [self._rewrite_function(m) for m in decl.methods]
                new_impl = ImplDecl(decl.trait_name, decl.for_type, new_methods)
                result.append(new_impl)
            elif isinstance(decl, TraitDecl):
                # Pass through traits as-is (they're just interfaces)
                result.append(decl)
            elif isinstance(decl, EnumDecl):
                # Pass through enums (may need monomorphization in future)
                result.append(decl)
            else:
                result.append(decl)
        
        return result
    
    def _rewrite_struct(self, struct: StructDecl) -> StructDecl:
        """Rewrite types in a struct to use monomorphized names."""
        new_fields = []
        for field in struct.fields:
            new_type = self._rewrite_type(field.type)
            new_fields.append(Parameter(field.name, new_type))
        return StructDecl(
            struct.name,
            new_fields,
            struct.is_exported,
            struct.type_params,
            getattr(struct, "location", None),
        )
    
    def _rewrite_function(self, fn: FunctionDecl) -> FunctionDecl:
        """Rewrite types in a function to use monomorphized names."""
        new_params = []
        for param in fn.parameters:
            new_type = self._rewrite_type(param.type)
            new_params.append(Parameter(param.name, new_type))
        
        new_return = self._rewrite_type(fn.return_type)
        new_body = self._rewrite_block(fn.body)
        
        new_fn = FunctionDecl(
            fn.name, new_params, new_return, new_body, fn.attributes,
            fn.is_exported, fn.is_extern, fn.type_params, getattr(fn, "has_self", False), getattr(fn, "location", None)
        )
        # Preserve has_self attribute for impl methods (constructor param is best-effort).
        if hasattr(fn, "has_self"):
            new_fn.has_self = fn.has_self
        # Preserve is_forward_decl attribute for forward declarations
        if hasattr(fn, "is_forward_decl"):
            new_fn.is_forward_decl = fn.is_forward_decl
        return new_fn
    
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
            return Type(name=t.name, is_pointer=t.is_pointer, is_reference=t.is_reference,
                        is_capability=getattr(t, 'is_capability', False), size=t.size,
                        element_type=new_elem, type_args=t.type_args)
        
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
            return VarDecl(stmt.name, new_type, new_init, is_mutable=getattr(stmt, "is_mutable", False))
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
        elif isinstance(stmt, ExpectStatement):
            return ExpectStatement(self._rewrite_expression(stmt.condition), stmt.line)
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
            new_name = self._resolve_struct_literal_mangled_name(expr.struct_name)
            return StructLiteral(new_name, new_fields)
        elif isinstance(expr, RecordUpdate):
            return RecordUpdate(
                self._rewrite_expression(expr.base),
                [(n, self._rewrite_expression(v)) for n, v in expr.updates],
            )
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
        elif isinstance(expr, CastExpression):
            new_expr = self._rewrite_expression(expr.expr)
            return CastExpression(new_expr, expr.target_type)
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
