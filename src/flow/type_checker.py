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
    FunctionCall, Literal, Variable, StructLiteral, ArrayLiteral, ArrayAccess, FieldAccess, MethodCall,
    IfStatement, WhileStatement, ForStatement, MatchStatement,
    HandleStatement, LayoutStatement, Block, Parameter, Type as ParsedType,
    EffectOperation, CapabilityMethod, MatchCase, EnumDecl, TraitDecl, ImplDecl
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
    UNKNOWN = "unknown"


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
        elif self.kind == TypeKind.UNKNOWN:
            return self.name or "unknown"
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

    def __hash__(self) -> int:
        return hash(
            (
                self.kind,
                self.name,
                self.element_type,
                self.size,
                tuple(self.param_types),
                self.return_type,
            )
        )


@dataclass
class Symbol:
    name: str
    type: SemanticType
    kind: str  # "function", "variable", "struct", "effect", "capability", "const"
    is_exported: bool = False
    is_mutable: bool = False  # For variables: True if declared with 'let mut'
    definition: Any = None  # Reference to AST node
    overloads: List[SemanticType] = field(default_factory=list)


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
        # Support function overloading
        if symbol.name in self.symbols and symbol.kind == "function" and self.symbols[symbol.name].kind == "function":
            existing = self.symbols[symbol.name]
            if not existing.overloads:
                existing.overloads = [existing.type]
            existing.overloads.append(symbol.type)
        else:
            # Allow redefinition (e.g., for imports that re-export the same symbol)
            self.symbols[symbol.name] = symbol


@dataclass
class TypeCheckResult:
    typed_ast: List[Any]  # Will be refined later
    symbol_table: Dict[str, Symbol]
    errors: List[str] = field(default_factory=list)


class TypeChecker:
    # Known external/builtin functions that are always available
    # Mapping name to return type (simplified, doesn't check arguments yet)
    BUILTIN_FUNCTIONS = {
        # C standard library
        'printf': TypeKind.I32,
        'sprintf': TypeKind.I32,
        'fprintf': TypeKind.I32,
        'scanf': TypeKind.I32,
        'sscanf': TypeKind.I32,
        'print': TypeKind.VOID,
        'println': TypeKind.VOID,
        'malloc': TypeKind.POINTER,
        'calloc': TypeKind.POINTER,
        'realloc': TypeKind.POINTER,
        'free': TypeKind.VOID,
        'memcpy': TypeKind.POINTER,
        'memset': TypeKind.POINTER,
        'memmove': TypeKind.POINTER,
        'memcmp': TypeKind.I32,
        'strlen': TypeKind.U64,
        'strcpy': TypeKind.POINTER,
        'strcat': TypeKind.POINTER,
        'strcmp': TypeKind.I32,
        'strncpy': TypeKind.POINTER,
        'strncmp': TypeKind.I32,
        'exit': TypeKind.VOID,
        'abort': TypeKind.VOID,
        'atexit': TypeKind.I32,
        'fopen': TypeKind.POINTER,
        'fclose': TypeKind.I32,
        'fread': TypeKind.I32,
        'fwrite': TypeKind.I32,
        'fgets': TypeKind.POINTER,
        'fputs': TypeKind.I32,
        'putchar': TypeKind.I32,
        'rand': TypeKind.I32,
        'srand': TypeKind.VOID,
        'time': TypeKind.I64,
        'clock': TypeKind.I64,
        'get_current_time': TypeKind.F64,
        # Math functions
        'sin': TypeKind.F32,
        'cos': TypeKind.F32,
        'tan': TypeKind.F32,
        'asin': TypeKind.F32,
        'acos': TypeKind.F32,
        'atan': TypeKind.F32,
        'atan2': TypeKind.F32,
        'sinh': TypeKind.F32,
        'cosh': TypeKind.F32,
        'tanh': TypeKind.F32,
        'asinh': TypeKind.F32,
        'acosh': TypeKind.F32,
        'atanh': TypeKind.F32,
        'exp': TypeKind.F32,
        'exp2': TypeKind.F32,
        'expm1': TypeKind.F32,
        'log': TypeKind.F32,
        'log2': TypeKind.F32,
        'log10': TypeKind.F32,
        'log1p': TypeKind.F32,
        'pow': TypeKind.F32,
        'sqrt': TypeKind.F32,
        'cbrt': TypeKind.F32,
        'hypot': TypeKind.F32,
        'ceil': TypeKind.F32,
        'floor': TypeKind.F32,
        'round': TypeKind.F32,
        'trunc': TypeKind.F32,
        'fabs': TypeKind.F32,
        'fmod': TypeKind.F32,
        'fmin': TypeKind.F32,
        'fmax': TypeKind.F32,
        'fdim': TypeKind.F32,
        'sigmoid': TypeKind.F32,
        # FLOW runtime / GPU
        'alloc': TypeKind.POINTER,
        'dealloc': TypeKind.VOID,
        'array_length': TypeKind.I32,
        'length': TypeKind.I32,
        'array': TypeKind.ARRAY,
        'gpu_thread_id': TypeKind.I32,
        'gpu_block_id': TypeKind.I32,
        'gpu_sync': TypeKind.VOID,
        'metal_create_buffer': TypeKind.POINTER,
        'metal_execute': TypeKind.VOID,
        'metal_get_result': TypeKind.POINTER,
        # Effect operations
        'emit': TypeKind.VOID,
        'query': TypeKind.VOID,
        'insert': TypeKind.VOID,
        'read': TypeKind.STRING,
        'write': TypeKind.VOID,
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
        self.strict = True

    def _is_numeric(self, t: SemanticType) -> bool:
        return t.kind in {
            TypeKind.I8, TypeKind.I16, TypeKind.I32, TypeKind.I64, TypeKind.I128,
            TypeKind.U8, TypeKind.U16, TypeKind.U32, TypeKind.U64, TypeKind.U128,
            TypeKind.F32, TypeKind.F64
        }

    def _is_integer(self, t: SemanticType) -> bool:
        return t.kind in {
            TypeKind.I8, TypeKind.I16, TypeKind.I32, TypeKind.I64, TypeKind.I128,
            TypeKind.U8, TypeKind.U16, TypeKind.U32, TypeKind.U64, TypeKind.U128,
        }

    def _is_float(self, t: SemanticType) -> bool:
        return t.kind in {TypeKind.F32, TypeKind.F64}

    def _numeric_common_type(self, a: SemanticType, b: SemanticType) -> SemanticType:
        # Prefer floats if any operand is float.
        if self._is_float(a) or self._is_float(b):
            if a.kind == TypeKind.F64 or b.kind == TypeKind.F64:
                return SemanticType(TypeKind.F64)
            return SemanticType(TypeKind.F32)

        # Both integer types: choose the wider kind.
        order = [
            TypeKind.I8, TypeKind.U8,
            TypeKind.I16, TypeKind.U16,
            TypeKind.I32, TypeKind.U32,
            TypeKind.I64, TypeKind.U64,
            TypeKind.I128, TypeKind.U128,
        ]
        a_idx = order.index(a.kind) if a.kind in order else 0
        b_idx = order.index(b.kind) if b.kind in order else 0
        return SemanticType(order[max(a_idx, b_idx)])

    def _can_coerce(self, actual: SemanticType, expected: SemanticType) -> bool:
        if actual is None or expected is None:
            return True
        # Treat void/unknown as a wildcard in lenient checking
        if actual.kind in {TypeKind.VOID, TypeKind.UNKNOWN} or expected.kind in {TypeKind.VOID, TypeKind.UNKNOWN}:
            return True
        if actual == expected:
            return True
        # Numeric widening/coercion
        if self._is_numeric(actual) and self._is_numeric(expected):
            return True
        # Pointer compatibility: allow any pointer-to-pointer
        if actual.kind == TypeKind.POINTER and expected.kind == TypeKind.POINTER:
            return True
        # String to pointer
        if actual.kind == TypeKind.STRING and expected.kind == TypeKind.POINTER:
            return True
        # Struct-to-pointer convenience (treat value as addressable)
        if actual.kind == TypeKind.STRUCT and expected.kind == TypeKind.POINTER:
            return True
        # Numeric to pointer (e.g. null/handles)
        if self._is_numeric(actual) and expected.kind == TypeKind.POINTER:
            return True
        # Pointer to numeric (treat address/handle as integer)
        if actual.kind == TypeKind.POINTER and self._is_numeric(expected):
            return True
        # Array to pointer decay
        if actual.kind == TypeKind.ARRAY and expected.kind == TypeKind.POINTER:
            return True
        # Array element coercion
        if actual.kind == TypeKind.ARRAY and expected.kind == TypeKind.ARRAY:
            if actual.element_type and expected.element_type:
                return self._can_coerce(actual.element_type, expected.element_type)
            return True
        # Null literal to pointer
        if actual.kind == TypeKind.NULL and expected.kind == TypeKind.POINTER:
            return True
        # Bool <-> numeric coercion
        if actual.kind == TypeKind.BOOL and self._is_numeric(expected):
            return True
        if expected.kind == TypeKind.BOOL and self._is_numeric(actual):
            return True
        # Struct coercion (lenient)
        if actual.kind == TypeKind.STRUCT or expected.kind == TypeKind.STRUCT:
            return True
        return False

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
            elif isinstance(decl, EnumDecl):
                # Enums are represented as structs with a 'tag' field
                # For simplicity in type checking, register as a struct
                enum_struct = StructDecl(decl.name, [
                    Parameter("tag", ParsedType("i32"))
                ])
                self.struct_types[decl.name] = enum_struct

                # Register variants as global constants
                for variant in decl.variants:
                    variant_name = f"{decl.name}_{variant.name}"
                    self.global_scope.define(Symbol(variant_name, SemanticType(TypeKind.I32), "const"))

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
                self._define_function(decl.name, decl)

            elif isinstance(decl, ImplDecl):
                for method in decl.methods:
                    mangled_name = f"{decl.for_type.name}_{decl.trait_name}_{method.name}"
                    # Add 'self' parameter if it's a method
                    params = method.parameters
                    if method.has_self and not any(p.name == "self" for p in params):
                        params = [Parameter("self", decl.for_type)] + params

                    method.parameters = params # Update AST node
                    self._define_function(mangled_name, method)

            elif isinstance(decl, ConstDecl):
                const_type = self._parse_type(decl.type)
                symbol = Symbol(decl.name, const_type, "const",
                              getattr(decl, 'is_exported', False), decl)
                self.global_scope.define(symbol)

    def _define_function(self, name: str, decl: FunctionDecl) -> None:
        param_types = [self._parse_type(p.type) for p in decl.parameters]
        return_type = self._parse_type(decl.return_type)
        func_type = SemanticType(
            kind=TypeKind.FUNCTION,
            param_types=param_types,
            return_type=return_type
        )
        symbol = Symbol(name, func_type, "function",
                      getattr(decl, 'is_exported', False), decl)
        self.global_scope.define(symbol)

    def _check_declarations(self, declarations: List[Any]) -> None:
        """Type check all declarations."""
        for decl in declarations:
            if isinstance(decl, FunctionDecl):
                self._check_function(decl)
            elif isinstance(decl, ImplDecl):
                for method in decl.methods:
                    self._check_function(method)
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
            self._check_block(func.body)
            expected_return = self._parse_type(func.return_type)

            # Collect explicit return types
            returns = self._collect_return_types(func.body)
            if returns:
                for rt in returns:
                    if not self._can_coerce(rt, expected_return):
                        self.errors.append(
                            f"Function '{func.name}' returns {rt} but should return {expected_return}"
                        )

        finally:
            self.current_scope = func_scope.parent

    def _check_const(self, const: ConstDecl) -> None:
        """Type check a constant declaration."""
        expr_type = self._check_expression(const.value)
        expected_type = self._parse_type(const.type)

        if not self._can_coerce(expr_type, expected_type):
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
        if var.initializer is None:
            expr_type = SemanticType(TypeKind.UNKNOWN)
        else:
            expr_type = self._check_expression(var.initializer)

        if var.type and var.type.name != "auto":  # Explicit type annotation
            expected_type = self._parse_type(var.type)
            if not self._can_coerce(expr_type, expected_type):
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
        
        # Check mutability (auto-promote to mutable for now)
        if not symbol.is_mutable:
            symbol.is_mutable = True

        expr_type = self._check_expression(assign.value)
        if not self._can_coerce(expr_type, symbol.type):
            self.errors.append(
                f"Cannot assign {expr_type} to variable '{assign.target}' of type {symbol.type}"
            )

        return expr_type

    def _check_if_stmt(self, if_stmt: IfStatement) -> SemanticType:
        """Type check an if statement."""
        # Condition must be bool
        cond_type = self._check_expression(if_stmt.condition)
        if cond_type.kind != TypeKind.BOOL and not self._is_numeric(cond_type):
            self.errors.append(f"If condition must be bool, got {cond_type}")

        # Check then block
        then_type = self._check_block(if_stmt.then_block)

        # Check elif blocks
        for elif_cond, elif_block in if_stmt.elif_blocks:
            cond_type = self._check_expression(elif_cond)
            if cond_type.kind != TypeKind.BOOL and not self._is_numeric(cond_type):
                self.errors.append(f"If condition must be bool, got {cond_type}")
            self._check_block(elif_block)

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
        if cond_type.kind != TypeKind.BOOL and not self._is_numeric(cond_type):
            self.errors.append(f"While condition must be bool, got {cond_type}")

        # Check body
        self._check_block(while_stmt.body)

        return SemanticType(TypeKind.VOID)

    def _check_for_stmt(self, for_stmt: ForStatement) -> SemanticType:
        """Type check a for statement."""
        # Range expressions should be checked
        self._check_expression(for_stmt.range_start)
        self._check_expression(for_stmt.range_end)
        if for_stmt.step:
            self._check_expression(for_stmt.step)

        # Create loop scope with iterator variable
        loop_scope = Scope(parent=self.current_scope)
        iter_type = SemanticType(TypeKind.I32)
        loop_scope.define(Symbol(for_stmt.variable, iter_type, "variable", is_mutable=True))
        prev = self.current_scope
        self.current_scope = loop_scope
        try:
            self._check_block(for_stmt.body)
        finally:
            self.current_scope = prev
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
        elif isinstance(expr, MethodCall):
            desugared = FunctionCall(expr.method, [expr.object] + list(expr.arguments))
            return self._check_function_call(desugared)
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
            return SemanticType(TypeKind.UNKNOWN)
        else:
            # For now, treat unknown expressions as unknown type
            return SemanticType(TypeKind.UNKNOWN)

    def _check_literal(self, lit: Literal) -> SemanticType:
        """Type check a literal."""
        value = lit.value
        if lit.type.name == "string":
            return SemanticType(TypeKind.STRING)
        if getattr(lit.type, 'is_pointer', False) or lit.type.name.startswith("ptr_"):
            return SemanticType(TypeKind.POINTER, element_type=SemanticType(TypeKind.VOID))
        if lit.type.name == "f32":
            return SemanticType(TypeKind.F32)
        if lit.type.name == "f64":
            return SemanticType(TypeKind.F64)
        if lit.type.name == "bool" or value in ["true", "false"]:
            return SemanticType(TypeKind.BOOL)
        if lit.type.name in ["i32", "i64", "i16", "i8", "u32", "u64", "u16", "u8", "i128", "u128"]:
            return SemanticType(getattr(TypeKind, lit.type.name.upper()))
        if value in ["true", "false"]:
            return SemanticType(TypeKind.BOOL)
        # Float heuristic only for numeric literals
        if isinstance(value, str):
            import re
            if re.match(r"^-?\d*\.\d+(e[-+]?\d+)?$", value, re.IGNORECASE) or re.match(r"^-?\d+e[-+]?\d+$", value, re.IGNORECASE):
                return SemanticType(TypeKind.F32)
            if re.match(r"^-?\d+$", value):
                return SemanticType(TypeKind.I32)
        else:
            # Assume integer
            return SemanticType(TypeKind.I32)
        # Default fallback
        return SemanticType(TypeKind.I32)

    def _check_variable(self, var: Variable) -> SemanticType:
        """Type check a variable reference."""
        symbol = self.current_scope.lookup(var.name)
        if not symbol:
            # Be permissive for unresolved variables (e.g., generated names)
            return SemanticType(TypeKind.I32)
        return symbol.type

    def _check_binary_op(self, op: BinaryOperation) -> SemanticType:
        """Type check a binary operation."""
        left_type = self._check_expression(op.left)
        right_type = self._check_expression(op.right)
        # Allow unknown/void to pass through
        if left_type is None or right_type is None:
            return left_type or right_type or SemanticType(TypeKind.VOID)
        if left_type.kind == TypeKind.VOID:
            return right_type
        if right_type.kind == TypeKind.VOID:
            return left_type

        # String concatenation
        if op.operator == "+" and (left_type.kind == TypeKind.STRING or right_type.kind == TypeKind.STRING):
            return SemanticType(TypeKind.STRING)

        # Pointer arithmetic/comparison allowances
        if left_type.kind == TypeKind.POINTER or right_type.kind == TypeKind.POINTER:
            if op.operator in ["+", "-"]:
                if left_type.kind == TypeKind.POINTER and self._is_numeric(right_type):
                    return left_type
                if right_type.kind == TypeKind.POINTER and self._is_numeric(left_type):
                    return right_type
                if left_type.kind == TypeKind.POINTER and right_type.kind == TypeKind.POINTER and op.operator == "-":
                    return SemanticType(TypeKind.I64)
            if op.operator in ["==", "!=", "<", ">", "<=", ">="]:
                if left_type.kind == TypeKind.POINTER and right_type.kind == TypeKind.POINTER:
                    return SemanticType(TypeKind.BOOL)
                if (left_type.kind == TypeKind.POINTER and self._is_numeric(right_type)) or (
                    right_type.kind == TypeKind.POINTER and self._is_numeric(left_type)
                ):
                    return SemanticType(TypeKind.BOOL)

        # Allow numeric coercions
        if self._is_numeric(left_type) and self._is_numeric(right_type):
            common = self._numeric_common_type(left_type, right_type)
        else:
            common = left_type
            if left_type != right_type:
                self.errors.append(
                    f"Binary operator '{op.operator}' requires matching types, got {left_type} and {right_type}"
                )

        # Determine result type based on operator
        if op.operator in ["+", "-", "*", "/", "%"]:
            return common
        elif op.operator in ["==", "!=", "<", ">", "<=", ">=", "&&", "||"]:
            return SemanticType(TypeKind.BOOL)
        elif op.operator in ["|", "&", "^", "<<", ">>"]:
            return common
        else:
            return common  # Default

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
        elif op.operator == "&":
            return SemanticType(TypeKind.POINTER, element_type=operand_type)
        elif op.operator == "*":
            if operand_type.kind != TypeKind.POINTER:
                self.errors.append(f"Unary '*' requires pointer type, got {operand_type}")
                return SemanticType(TypeKind.VOID)
            return operand_type.element_type or SemanticType(TypeKind.VOID)

        return operand_type

    def _check_function_call(self, call: FunctionCall) -> SemanticType:
        """Type check a function call."""
        if call.name.startswith("array_"):
            elem_name = call.name[len("array_"):]
            elem_type = self._parse_named_scalar(elem_name)
            if elem_type:
                return SemanticType(TypeKind.ARRAY, element_type=elem_type)
        symbol = self.current_scope.lookup(call.name)
        if not symbol:
            # Check if it's a known builtin function
            if call.name in self.BUILTIN_FUNCTIONS:
                # Builtin functions are allowed without declaration
                # Check arguments anyway (type check them)
                for arg in call.arguments:
                    self._check_expression(arg)
                kind = self.BUILTIN_FUNCTIONS[call.name]
                if kind == TypeKind.POINTER:
                    return SemanticType(TypeKind.POINTER, element_type=SemanticType(TypeKind.VOID))
                elif kind == TypeKind.ARRAY:
                    return SemanticType(TypeKind.ARRAY, element_type=SemanticType(TypeKind.I32))
                return SemanticType(kind)
            else:
                # Allow unresolved calls in lenient checking
                return SemanticType(TypeKind.VOID)

        if symbol.type.kind != TypeKind.FUNCTION:
            self.errors.append(f"'{call.name}' is not a function")
            return SemanticType(TypeKind.VOID)

        # Handle overloads
        candidates = symbol.overloads if symbol.overloads else [symbol.type]
        arg_types = [self._check_expression(arg) for arg in call.arguments]

        matching_overload = None
        for candidate in candidates:
            if len(candidate.param_types) != len(arg_types):
                continue

            match = True
            for expected, actual in zip(candidate.param_types, arg_types):
                if not self._is_compatible(actual, expected):
                    match = False
                    break
            if match:
                matching_overload = candidate
                break

        if matching_overload:
            return matching_overload.return_type

        # Fallback to builtin if no overload matches
        if call.name in self.BUILTIN_FUNCTIONS:
            kind = self.BUILTIN_FUNCTIONS[call.name]
            if kind == TypeKind.POINTER:
                return SemanticType(TypeKind.POINTER, element_type=SemanticType(TypeKind.VOID))
            elif kind == TypeKind.ARRAY:
                return SemanticType(TypeKind.ARRAY, element_type=SemanticType(TypeKind.I32))
            return SemanticType(kind)

        # No match found - report error based on the first candidate (or provide generic error)
        self.errors.append(
            f"No matching overload for function '{call.name}' with arguments ({', '.join(str(t) for t in arg_types)})"
        )
        return candidates[0].return_type

    def _check_struct_literal(self, struct_lit: StructLiteral) -> SemanticType:
        """Type check a struct literal."""
        struct_name = struct_lit.struct_name
        if struct_name not in self.struct_types:
            return SemanticType(TypeKind.STRUCT, name=struct_name)

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
            elif not self._can_coerce(provided_fields[field_name], expected_type):
                self.errors.append(
                    f"Struct '{struct_name}' field '{field_name}' expects {expected_type}, got {provided_fields[field_name]}"
                )

        return SemanticType(TypeKind.STRUCT, name=struct_name)

    def _is_compatible(self, actual: SemanticType, expected: SemanticType) -> bool:
        """Check if actual type is compatible with expected type."""
        if actual == expected:
            return True

        # Pointer compatibility
        if expected.kind == TypeKind.POINTER and actual.kind == TypeKind.I32:
            return True # Allow 0/NULL

        if actual.kind == TypeKind.POINTER and expected.kind == TypeKind.POINTER:
            if actual.element_type and actual.element_type.kind == TypeKind.VOID:
                return True
            if expected.element_type and expected.element_type.kind == TypeKind.VOID:
                return True
            # In systems examples, ptr<u8> is often used as a generic pointer
            if actual.element_type and actual.element_type.kind in [TypeKind.U8, TypeKind.I8]:
                return True
            if expected.element_type and expected.element_type.kind in [TypeKind.U8, TypeKind.I8]:
                return True

        # String to pointer
        if actual.kind == TypeKind.STRING and expected.kind == TypeKind.POINTER:
            if expected.element_type and expected.element_type.kind in [TypeKind.U8, TypeKind.I8, TypeKind.VOID]:
                return True

        # Array to pointer decay
        if actual.kind == TypeKind.ARRAY and expected.kind == TypeKind.POINTER:
            if expected.element_type and expected.element_type.kind == TypeKind.VOID:
                return True
            if actual.element_type == expected.element_type:
                return True
            if actual.element_type and expected.element_type and self._is_compatible(actual.element_type, expected.element_type):
                return True

        # Array to Array compatibility (allow different sizes, compatible elements)
        if actual.kind == TypeKind.ARRAY and expected.kind == TypeKind.ARRAY:
            if actual.element_type == expected.element_type:
                return True
            if actual.element_type and expected.element_type and self._is_compatible(actual.element_type, expected.element_type):
                return True

        # Numeric compatibility
        ints = {TypeKind.I8, TypeKind.I16, TypeKind.I32, TypeKind.I64, TypeKind.I128,
                TypeKind.U8, TypeKind.U16, TypeKind.U32, TypeKind.U64, TypeKind.U128}
        floats = {TypeKind.F32, TypeKind.F64}

        if actual.kind in ints and expected.kind in ints:
            return True
        if actual.kind in floats and expected.kind in floats:
            return True
        if actual.kind in ints and expected.kind in floats:
            return True

        return False

    def _parse_named_scalar(self, name: str) -> Optional[SemanticType]:
        mapping = {
            "void": SemanticType(TypeKind.VOID),
            "bool": SemanticType(TypeKind.BOOL),
            "i8": SemanticType(TypeKind.I8),
            "i16": SemanticType(TypeKind.I16),
            "i32": SemanticType(TypeKind.I32),
            "i64": SemanticType(TypeKind.I64),
            "i128": SemanticType(TypeKind.I128),
            "u8": SemanticType(TypeKind.U8),
            "u16": SemanticType(TypeKind.U16),
            "u32": SemanticType(TypeKind.U32),
            "u64": SemanticType(TypeKind.U64),
            "u128": SemanticType(TypeKind.U128),
            "f32": SemanticType(TypeKind.F32),
            "f64": SemanticType(TypeKind.F64),
            "string": SemanticType(TypeKind.STRING),
        }
        return mapping.get(name)

    def _parse_type(self, parsed_type: ParsedType) -> SemanticType:
        """Convert a parsed Type to a SemanticType."""
        if parsed_type.name == "auto":
            return SemanticType(TypeKind.UNKNOWN, name="auto")
        if parsed_type.name.startswith("memref_"):
            elem_name = parsed_type.name[len("memref_"):]
            elem_type = self._parse_named_scalar(elem_name)
            if elem_type:
                return SemanticType(TypeKind.POINTER, element_type=elem_type)
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
        elif parsed_type.name.startswith("memref_"):
            element_name = parsed_type.name[len("memref_"):]
            element_type = self._parse_type(ParsedType(element_name))
            return SemanticType(TypeKind.POINTER, element_type=element_type)
        elif parsed_type.name in self.struct_types:
            return SemanticType(TypeKind.STRUCT, name=parsed_type.name)
        else:
            # Unknown type (e.g., generic parameter)
            return SemanticType(TypeKind.UNKNOWN, name=parsed_type.name)

    def _collect_return_types(self, block: Block) -> List[SemanticType]:
        types: List[SemanticType] = []
        for stmt in block.statements:
            if isinstance(stmt, ReturnStatement):
                if stmt.value:
                    types.append(self._check_expression(stmt.value))
                else:
                    types.append(SemanticType(TypeKind.VOID))
            elif isinstance(stmt, IfStatement):
                types.extend(self._collect_return_types(stmt.then_block))
                if stmt.else_block:
                    types.extend(self._collect_return_types(stmt.else_block))
            elif isinstance(stmt, WhileStatement):
                types.extend(self._collect_return_types(stmt.body))
            elif isinstance(stmt, ForStatement):
                types.extend(self._collect_return_types(stmt.body))
            elif isinstance(stmt, Block):
                types.extend(self._collect_return_types(stmt))
        return types
