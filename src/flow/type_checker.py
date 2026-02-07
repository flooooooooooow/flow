"""
FLOW Type Checker
Semantic analysis and type checking for the FLOW language.

This module implements:
- Symbol table management
- Type inference and checking
- Scope analysis
- Semantic validation

Architecture:
Source → Parser → AST → Type Checker → Typed AST → Code Generator
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Union, Any
from enum import Enum

from .parser import (
    FunctionDecl, StructDecl, EffectDecl, CapabilityDecl, ConstDecl, ImportDecl,
    VarDecl, ReturnStatement, Assignment, BinaryOperation, UnaryOperation,
    FunctionCall, Literal, Variable, StructLiteral, ArrayLiteral, ArrayAccess, FieldAccess,
    IfStatement, WhileStatement, ForStatement, MatchStatement,
    HandleStatement, LayoutStatement, Block, Parameter, Type as ParsedType,
    EffectOperation, CapabilityMethod, MatchCase
)


class TypeKind(Enum):
    VOID = "void"
    BOOL = "bool"
    I8 = "i8"
    I16 = "i16"
    I32 = "i32"
    I64 = "i64"
    I128 = "i128"
    U8 = "u8"
    U16 = "u16"
    U32 = "u32"
    U64 = "u64"
    U128 = "u128"
    F32 = "f32"
    F64 = "f64"
    STRING = "string"
    STRUCT = "struct"
    ARRAY = "array"
    POINTER = "pointer"
    FUNCTION = "function"
    NULL = "null"  # null pointer type


@dataclass
class SemanticType:
    kind: TypeKind
    name: str = ""  # For structs, effects, etc.
    element_type: Optional['SemanticType'] = None  # For arrays, pointers
    size: Optional[int] = None  # For fixed-size arrays
    param_types: List['SemanticType'] = field(default_factory=list)  # For functions
    return_type: Optional['SemanticType'] = None  # For functions

    def __str__(self) -> str:
        if self.kind == TypeKind.VOID:
            return "void"
        elif self.kind == TypeKind.BOOL:
            return "bool"
        elif self.kind in [TypeKind.I8, TypeKind.I16, TypeKind.I32, TypeKind.I64, TypeKind.I128]:
            return self.kind.value
        elif self.kind in [TypeKind.U8, TypeKind.U16, TypeKind.U32, TypeKind.U64, TypeKind.U128]:
            return self.kind.value
        elif self.kind in [TypeKind.F32, TypeKind.F64]:
            return self.kind.value
        elif self.kind == TypeKind.STRING:
            return "string"
        elif self.kind == TypeKind.STRUCT:
            return self.name
        elif self.kind == TypeKind.ARRAY:
            if self.size is not None:
                return f"array<{self.element_type}, {self.size}>"
            else:
                return f"array<{self.element_type}>"
        elif self.kind == TypeKind.POINTER:
            return f"ptr<{self.element_type}>"
        elif self.kind == TypeKind.FUNCTION:
            params = ", ".join(str(p) for p in self.param_types)
            return f"({params}) -> {self.return_type}"
        else:
            return f"<unknown:{self.kind}>"

    def __eq__(self, other) -> bool:
        if not isinstance(other, SemanticType):
            return False
        return (self.kind == other.kind and
                self.name == other.name and
                self.element_type == other.element_type and
                self.size == other.size and
                self.param_types == other.param_types and
                self.return_type == other.return_type)


@dataclass
class Symbol:
    name: str
    type: SemanticType
    kind: str  # "function", "variable", "struct", "effect", "capability", "const"
    is_exported: bool = False
    is_mutable: bool = False  # For variables: True if declared with 'let mut'
    definition: Any = None  # Reference to AST node


@dataclass
class Scope:
    symbols: Dict[str, Symbol] = field(default_factory=dict)
    parent: Optional['Scope'] = None

    def lookup(self, name: str) -> Optional[Symbol]:
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.parent.lookup(name)
        return None

    def define(self, symbol: Symbol) -> None:
        # Allow redefinition (e.g., for imports that re-export the same symbol)
        self.symbols[symbol.name] = symbol


@dataclass
class TypeCheckResult:
    typed_ast: List[Any]  # Will be refined later
    symbol_table: Dict[str, Symbol]
    errors: List[str] = field(default_factory=list)


class TypeChecker:
    # Known external/builtin functions that are always available
    BUILTIN_FUNCTIONS = {
        # C standard library
        'printf', 'sprintf', 'fprintf', 'scanf', 'sscanf',
        'print', 'println',  # Common aliases
        'malloc', 'calloc', 'realloc', 'free',
        'memcpy', 'memset', 'memmove', 'memcmp',
        'strlen', 'strcpy', 'strcat', 'strcmp', 'strncpy', 'strncmp',
        'exit', 'abort', 'atexit',
        'fopen', 'fclose', 'fread', 'fwrite', 'fgets', 'fputs',
        'rand', 'srand', 'time', 'clock',
        # Math functions
        'sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'atan2',
        'sinh', 'cosh', 'tanh', 'asinh', 'acosh', 'atanh',
        'exp', 'exp2', 'expm1', 'log', 'log2', 'log10', 'log1p',
        'pow', 'sqrt', 'cbrt', 'hypot',
        'ceil', 'floor', 'round', 'trunc', 'fabs', 'fmod',
        'fmin', 'fmax', 'fdim',
        'sigmoid',  # Common ML function
        # FLOW runtime / GPU
        'alloc', 'dealloc', 'array_length', 'array',
        'gpu_thread_id', 'gpu_block_id', 'gpu_sync',
        'metal_create_buffer', 'metal_execute', 'metal_get_result',
        # Effect operations (called via Effect.operation syntax but also direct)
        'emit', 'query', 'insert', 'read', 'write',
    }

    def __init__(self):
        self.global_scope = Scope()
        self.current_scope = self.global_scope
        self.errors: List[str] = []
        self.struct_types: Dict[str, StructDecl] = {}
        self.effect_types: Dict[str, EffectDecl] = {}
        self.capability_types: Dict[str, CapabilityDecl] = {}
        # Builtin implicit UI layout state pointer
        ui_state_type = SemanticType(TypeKind.POINTER, element_type=SemanticType(TypeKind.VOID))
        self.global_scope.define(Symbol("_ui_state", ui_state_type, "variable", is_mutable=True))

    def check(self, declarations: List[Any]) -> TypeCheckResult:
        """Main entry point for type checking."""
        self.errors = []

        # Phase 1: Collect type definitions (structs, effects, capabilities)
        self._collect_types(declarations)

        # Phase 2: Collect function signatures and global symbols
        self._collect_symbols(declarations)

        # Phase 3: Type check all declarations
        self._check_declarations(declarations)

        return TypeCheckResult(
            typed_ast=declarations,  # For now, just return the original AST
            symbol_table=dict(self.global_scope.symbols),
            errors=self.errors
        )

    def _collect_types(self, declarations: List[Any]) -> None:
        """Collect struct, effect, and capability definitions."""
        for decl in declarations:
            if isinstance(decl, StructDecl):
                if decl.name in self.struct_types:
                    self.errors.append(f"Struct '{decl.name}' already defined")
                else:
                    self.struct_types[decl.name] = decl
            elif isinstance(decl, EffectDecl):
                if decl.name in self.effect_types:
                    self.errors.append(f"Effect '{decl.name}' already defined")
                else:
                    self.effect_types[decl.name] = decl
            elif isinstance(decl, CapabilityDecl):
                if decl.name in self.capability_types:
                    self.errors.append(f"Capability '{decl.name}' already defined")
                else:
                    self.capability_types[decl.name] = decl

    def _collect_symbols(self, declarations: List[Any]) -> None:
        """Collect function signatures and global symbols."""
        for decl in declarations:
            if isinstance(decl, FunctionDecl):
                param_types = [self._parse_type(p.type) for p in decl.parameters]
                return_type = self._parse_type(decl.return_type)
                func_type = SemanticType(
                    kind=TypeKind.FUNCTION,
                    param_types=param_types,
                    return_type=return_type
                )
                symbol = Symbol(decl.name, func_type, "function",
                              getattr(decl, 'is_exported', False), decl)
                self.global_scope.define(symbol)

            elif isinstance(decl, ConstDecl):
                const_type = self._parse_type(decl.type)
                symbol = Symbol(decl.name, const_type, "const",
                              getattr(decl, 'is_exported', False), decl)
                self.global_scope.define(symbol)

    def _check_declarations(self, declarations: List[Any]) -> None:
        """Type check all declarations."""
        for decl in declarations:
            if isinstance(decl, FunctionDecl):
                self._check_function(decl)
            elif isinstance(decl, ConstDecl):
                self._check_const(decl)
            # Other declaration types don't need additional checking yet

    def _check_function(self, func: FunctionDecl) -> None:
        """Type check a function declaration."""
        # Extern functions have no body to check - they're just declarations
        if getattr(func, 'is_extern', False):
            return
        
        # Create function scope
        func_scope = Scope(parent=self.current_scope)
        self.current_scope = func_scope

        try:
            # Add parameters to scope
            for param in func.parameters:
                param_type = self._parse_type(param.type)
                symbol = Symbol(param.name, param_type, "variable")
                func_scope.define(symbol)

            # Type check function body
            body_type = self._check_block(func.body)
            expected_return = self._parse_type(func.return_type)

            # Check return type - extern functions don't have bodies so don't check
            if body_type != expected_return:
                self.errors.append(
                    f"Function '{func.name}' returns {body_type} but should return {expected_return}"
                )

        finally:
            self.current_scope = func_scope.parent

    def _check_const(self, const: ConstDecl) -> None:
        """Type check a constant declaration."""
        expr_type = self._check_expression(const.value)
        expected_type = self._parse_type(const.type)

        if expr_type != expected_type:
            self.errors.append(
                f"Const '{const.name}' has type {expr_type} but should be {expected_type}"
            )

    def _check_block(self, block: Block) -> SemanticType:
        """Type check a block of statements. Returns the type of the last statement."""
        result_type = SemanticType(TypeKind.VOID)

        for stmt in block.statements:
            result_type = self._check_statement(stmt)

        return result_type

    def _check_statement(self, stmt: Any) -> SemanticType:
        """Type check a statement. Returns the type of the statement."""
        if isinstance(stmt, VarDecl):
            return self._check_var_decl(stmt)
        elif isinstance(stmt, ReturnStatement):
            return self._check_return_stmt(stmt)
        elif isinstance(stmt, Assignment):
            return self._check_assignment(stmt)
        elif isinstance(stmt, IfStatement):
            return self._check_if_stmt(stmt)
        elif isinstance(stmt, WhileStatement):
            return self._check_while_stmt(stmt)
        elif isinstance(stmt, ForStatement):
            return self._check_for_stmt(stmt)
        elif isinstance(stmt, FunctionCall):
            return self._check_expression(stmt)
        elif isinstance(stmt, LayoutStatement):
            for arg in stmt.args:
                self._check_expression(arg)
            return self._check_block(stmt.body)
        else:
            # For now, assume other statements are void
            return SemanticType(TypeKind.VOID)

    def _check_var_decl(self, var: VarDecl) -> SemanticType:
        """Type check a variable declaration."""
        expr_type = self._check_expression(var.initializer)

        if var.type:  # Explicit type annotation
            expected_type = self._parse_type(var.type)
            if expr_type != expected_type:
                if not (
                    (expr_type.kind == TypeKind.POINTER and expected_type.kind == TypeKind.POINTER and
                     expr_type.element_type and expr_type.element_type.kind == TypeKind.VOID) or
                    (expr_type.kind == TypeKind.ARRAY and expected_type.kind == TypeKind.POINTER)
                ):
                    self.errors.append(
                        f"Variable '{var.name}' initialized with {expr_type} but annotated as {expected_type}"
                    )
        else:
            # Type inference - for now, just use the expression type
            expected_type = expr_type

        # Add to current scope with mutability flag
        is_mutable = getattr(var, 'is_mutable', False)
        symbol = Symbol(var.name, expected_type, "variable", is_mutable=is_mutable)
        self.current_scope.define(symbol)

        return expected_type

    def _check_return_stmt(self, ret: ReturnStatement) -> SemanticType:
        """Type check a return statement."""
        if ret.value:
            return self._check_expression(ret.value)
        else:
            return SemanticType(TypeKind.VOID)

    def _check_assignment(self, assign: Assignment) -> SemanticType:
        """Type check an assignment."""
        # Handle field access assignments (target_expr is set)
        if assign.target_expr is not None:
            # For now, allow all field/array assignments - mutability check 
            # would require tracking whether the base object is mutable
            expr_type = self._check_expression(assign.value)
            return expr_type
        
        symbol = self.current_scope.lookup(assign.target)
        if not symbol:
            self.errors.append(f"Undefined variable '{assign.target}'")
            return SemanticType(TypeKind.VOID)
        
        # Check mutability
        if not symbol.is_mutable:
            self.errors.append(
                f"Cannot assign to immutable variable '{assign.target}'. "
                f"Use 'let mut {assign.target}' to make it mutable."
            )

        expr_type = self._check_expression(assign.value)
        if expr_type != symbol.type:
            if not (
                (expr_type.kind == TypeKind.POINTER and symbol.type.kind == TypeKind.POINTER and
                 expr_type.element_type and expr_type.element_type.kind == TypeKind.VOID) or
                (expr_type.kind == TypeKind.ARRAY and symbol.type.kind == TypeKind.POINTER)
            ):
                self.errors.append(
                    f"Cannot assign {expr_type} to variable '{assign.target}' of type {symbol.type}"
                )

        return expr_type

    def _check_if_stmt(self, if_stmt: IfStatement) -> SemanticType:
        """Type check an if statement."""
        # Condition must be bool
        cond_type = self._check_expression(if_stmt.condition)
        if cond_type.kind != TypeKind.BOOL:
            self.errors.append(f"If condition must be bool, got {cond_type}")

        # Check then block
        then_type = self._check_block(if_stmt.then_block)

        # Check else block if present
        if if_stmt.else_block:
            else_type = self._check_block(if_stmt.else_block)
            # For now, just return the then type
            return then_type
        else:
            return SemanticType(TypeKind.VOID)

    def _check_while_stmt(self, while_stmt: WhileStatement) -> SemanticType:
        """Type check a while statement."""
        # Condition must be bool
        cond_type = self._check_expression(while_stmt.condition)
        if cond_type.kind != TypeKind.BOOL:
            self.errors.append(f"While condition must be bool, got {cond_type}")

        # Check body
        self._check_block(while_stmt.body)

        return SemanticType(TypeKind.VOID)

    def _check_for_stmt(self, for_stmt: ForStatement) -> SemanticType:
        """Type check a for statement."""
        # For now, assume range expressions are integers
        # This is a simplified check
        self._check_block(for_stmt.body)
        return SemanticType(TypeKind.VOID)

    def _check_expression(self, expr: Any) -> SemanticType:
        """Type check an expression."""
        if isinstance(expr, Literal):
            return self._check_literal(expr)
        elif isinstance(expr, Variable):
            return self._check_variable(expr)
        elif isinstance(expr, BinaryOperation):
            return self._check_binary_op(expr)
        elif isinstance(expr, UnaryOperation):
            return self._check_unary_op(expr)
        elif isinstance(expr, FunctionCall):
            return self._check_function_call(expr)
        elif isinstance(expr, StructLiteral):
            return self._check_struct_literal(expr)
        elif isinstance(expr, ArrayLiteral):
            if expr.elements:
                elem_type = self._check_expression(expr.elements[0])
            else:
                elem_type = SemanticType(TypeKind.I32)
            return SemanticType(TypeKind.ARRAY, element_type=elem_type, size=len(expr.elements))
        elif isinstance(expr, ArrayAccess):
            base_type = self._check_expression(expr.array)
            if base_type.kind == TypeKind.ARRAY or base_type.kind == TypeKind.POINTER:
                return base_type.element_type or SemanticType(TypeKind.VOID)
            return SemanticType(TypeKind.VOID)
        elif isinstance(expr, FieldAccess):
            obj_type = self._check_expression(expr.object)
            if obj_type.kind == TypeKind.STRUCT and obj_type.name in self.struct_types:
                struct_def = self.struct_types[obj_type.name]
                for field in struct_def.fields:
                    if field.name == expr.field:
                        return self._parse_type(field.type)
            return SemanticType(TypeKind.VOID)
        else:
            # For now, assume unknown expressions are void
            return SemanticType(TypeKind.VOID)

    def _check_literal(self, lit: Literal) -> SemanticType:
        """Type check a literal."""
        value = lit.value
        if getattr(lit.type, 'is_pointer', False) or lit.type.name.startswith("ptr_"):
            return SemanticType(TypeKind.POINTER, element_type=SemanticType(TypeKind.VOID))
        if lit.type.name == "f32" or "." in str(value) or "e" in str(value).lower():
            return SemanticType(TypeKind.F32)
        elif value in ["true", "false"]:
            return SemanticType(TypeKind.BOOL)
        elif lit.type.name == "string":
            return SemanticType(TypeKind.STRING)
        else:
            # Assume integer
            return SemanticType(TypeKind.I32)

    def _check_variable(self, var: Variable) -> SemanticType:
        """Type check a variable reference."""
        symbol = self.current_scope.lookup(var.name)
        if not symbol:
            self.errors.append(f"Undefined variable '{var.name}'")
            return SemanticType(TypeKind.VOID)
        return symbol.type

    def _check_binary_op(self, op: BinaryOperation) -> SemanticType:
        """Type check a binary operation."""
        left_type = self._check_expression(op.left)
        right_type = self._check_expression(op.right)

        # For now, assume operands must be the same type
        if left_type != right_type:
            self.errors.append(
                f"Binary operator '{op.operator}' requires matching types, got {left_type} and {right_type}"
            )

        # Determine result type based on operator
        if op.operator in ["+", "-", "*", "/"]:
            return left_type
        elif op.operator in ["==", "!=", "<", ">", "<=", ">=", "&&", "||"]:
            return SemanticType(TypeKind.BOOL)
        else:
            return left_type  # Default

    def _check_unary_op(self, op: UnaryOperation) -> SemanticType:
        """Type check a unary operation."""
        operand_type = self._check_expression(op.operand)

        if op.operator == "-":
            # Must be numeric
            if operand_type.kind not in [TypeKind.I8, TypeKind.I16, TypeKind.I32, TypeKind.I64,
                                       TypeKind.U8, TypeKind.U16, TypeKind.U32, TypeKind.U64,
                                       TypeKind.F32, TypeKind.F64]:
                self.errors.append(f"Unary '-' requires numeric type, got {operand_type}")
            return operand_type
        elif op.operator == "!":
            if operand_type.kind != TypeKind.BOOL:
                self.errors.append(f"Unary '!' requires bool type, got {operand_type}")
            return SemanticType(TypeKind.BOOL)

        return operand_type

    def _check_function_call(self, call: FunctionCall) -> SemanticType:
        """Type check a function call."""
        symbol = self.current_scope.lookup(call.name)
        if not symbol:
            # Check if it's a known builtin function
            if call.name in self.BUILTIN_FUNCTIONS:
                # Builtin functions are allowed without declaration
                # Check arguments anyway (type check them)
                for arg in call.arguments:
                    self._check_expression(arg)
                return SemanticType(TypeKind.VOID)
            else:
                self.errors.append(f"Undefined function '{call.name}'")
                return SemanticType(TypeKind.VOID)

        if symbol.type.kind != TypeKind.FUNCTION:
            self.errors.append(f"'{call.name}' is not a function")
            return SemanticType(TypeKind.VOID)

        # Check argument count
        if len(call.arguments) != len(symbol.type.param_types):
            self.errors.append(
                f"Function '{call.name}' expects {len(symbol.type.param_types)} arguments, got {len(call.arguments)}"
            )
            return symbol.type.return_type

        # Check argument types
        for i, (arg, expected_type) in enumerate(zip(call.arguments, symbol.type.param_types)):
            arg_type = self._check_expression(arg)
            if arg_type != expected_type:
                if not (
                    (arg_type.kind == TypeKind.POINTER and expected_type.kind == TypeKind.POINTER and
                     arg_type.element_type and arg_type.element_type.kind == TypeKind.VOID) or
                    (arg_type.kind == TypeKind.ARRAY and expected_type.kind == TypeKind.POINTER)
                ):
                    self.errors.append(
                        f"Function '{call.name}' argument {i} expects {expected_type}, got {arg_type}"
                    )

        return symbol.type.return_type

    def _check_struct_literal(self, struct_lit: StructLiteral) -> SemanticType:
        """Type check a struct literal."""
        struct_name = struct_lit.struct_name
        if struct_name not in self.struct_types:
            self.errors.append(f"Undefined struct type '{struct_name}'")
            return SemanticType(TypeKind.VOID)

        struct_def = self.struct_types[struct_name]
        expected_fields = {field.name: self._parse_type(field.type) for field in struct_def.fields}

        # Check that all required fields are present and types match
        # struct_lit.fields is List[tuple] where each tuple is (field_name, field_value)
        provided_fields = {}
        for field in struct_lit.fields:
            if isinstance(field, tuple) and len(field) == 2:
                field_name, field_value = field
                provided_fields[field_name] = self._check_expression(field_value)
            elif hasattr(field, 'name') and hasattr(field, 'value'):
                provided_fields[field.name] = self._check_expression(field.value)

        for field_name, expected_type in expected_fields.items():
            if field_name not in provided_fields:
                self.errors.append(f"Struct '{struct_name}' missing field '{field_name}'")
            elif provided_fields[field_name] != expected_type:
                self.errors.append(
                    f"Struct '{struct_name}' field '{field_name}' expects {expected_type}, got {provided_fields[field_name]}"
                )

        return SemanticType(TypeKind.STRUCT, name=struct_name)

    def _parse_type(self, parsed_type: ParsedType) -> SemanticType:
        """Convert a parsed Type to a SemanticType."""
        if parsed_type.name == "void":
            return SemanticType(TypeKind.VOID)
        elif parsed_type.name == "bool":
            return SemanticType(TypeKind.BOOL)
        elif parsed_type.name == "i8":
            return SemanticType(TypeKind.I8)
        elif parsed_type.name == "i16":
            return SemanticType(TypeKind.I16)
        elif parsed_type.name == "i32":
            return SemanticType(TypeKind.I32)
        elif parsed_type.name == "i64":
            return SemanticType(TypeKind.I64)
        elif parsed_type.name == "i128":
            return SemanticType(TypeKind.I128)
        elif parsed_type.name == "u8":
            return SemanticType(TypeKind.U8)
        elif parsed_type.name == "u16":
            return SemanticType(TypeKind.U16)
        elif parsed_type.name == "u32":
            return SemanticType(TypeKind.U32)
        elif parsed_type.name == "u64":
            return SemanticType(TypeKind.U64)
        elif parsed_type.name == "u128":
            return SemanticType(TypeKind.U128)
        elif parsed_type.name == "f32":
            return SemanticType(TypeKind.F32)
        elif parsed_type.name == "f64":
            return SemanticType(TypeKind.F64)
        elif parsed_type.name == "string":
            return SemanticType(TypeKind.STRING)
        elif parsed_type.is_pointer and parsed_type.element_type:
            return SemanticType(TypeKind.POINTER, element_type=self._parse_type(parsed_type.element_type))
        elif parsed_type.name.startswith("array_") and parsed_type.element_type:
            return SemanticType(TypeKind.ARRAY, element_type=self._parse_type(parsed_type.element_type), size=parsed_type.size)
        elif parsed_type.name in self.struct_types:
            return SemanticType(TypeKind.STRUCT, name=parsed_type.name)
        else:
            # For now, assume it's a valid type
            return SemanticType(TypeKind.VOID, name=parsed_type.name)
