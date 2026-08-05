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

import dataclasses
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Set
from enum import Enum

from .parser import (
    FunctionDecl, StructDecl, EffectDecl, CapabilityDecl, ConstDecl, VarDecl, ReturnStatement, Assignment, BinaryOperation, UnaryOperation,
    FunctionCall, Literal, Variable, StructLiteral, ArrayLiteral, ArrayAccess, FieldAccess, MethodCall, EffectCall,
    IfStatement, WhileStatement, ForStatement, LayoutStatement, Block, Parameter, Type as ParsedType,
    EnumDecl, ImplDecl, TraitDecl,
    TypeAliasDecl, DistinctTypeDecl, UnitDecl, CastExpression,
    MatchStatement, StructPattern, OrPattern, ListPattern, DeferStatement, TryExpr, Lambda,
    VectorLiteral, ExpectStatement, RecordUpdate, BreakStatement, ContinueStatement,
    SortExpr,
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
    TYPE_ALIAS = "type_alias"  # Transparent type alias
    DISTINCT = "distinct"  # Opaque distinct type
    UNKNOWN = "unknown"


@dataclass
class SemanticType:
    kind: TypeKind
    name: str = ""  # For structs, effects, distinct types, etc.
    element_type: Optional['SemanticType'] = None  # For arrays, pointers
    base_type: Optional['SemanticType'] = None  # For type aliases and distinct types
    size: Optional[int] = None  # For fixed-size arrays
    param_types: List['SemanticType'] = field(default_factory=list)  # For functions
    return_type: Optional['SemanticType'] = None  # For functions
    # Dimension exponent vector for units of measure (north-star.md section 6).
    # Indexed by base-unit declaration order, trailing zeros stripped, so the
    # vector stays canonical as later base units are declared. None for
    # ordinary (non-unit) types; only DISTINCT types carry dims.
    dims: Optional[Tuple[int, ...]] = None

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
        elif self.kind == TypeKind.TYPE_ALIAS:
            # Type aliases are transparent - show the alias name
            return self.name
        elif self.kind == TypeKind.DISTINCT:
            # Distinct types show their name (they're opaque)
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

        # Type aliases are transparent - compare underlying types
        if self.kind == TypeKind.TYPE_ALIAS and other.kind == TypeKind.TYPE_ALIAS:
            # Both are aliases - compare base types
            return self.base_type == other.base_type
        elif self.kind == TypeKind.TYPE_ALIAS:
            # Self is alias - compare base type with other
            return self.base_type == other
        elif other.kind == TypeKind.TYPE_ALIAS:
            # Other is alias - compare self with base type
            return self == other.base_type

        # Distinct types are opaque - they're only equal to themselves
        if self.kind == TypeKind.DISTINCT or other.kind == TypeKind.DISTINCT:
            return (self.kind == other.kind and
                    self.name == other.name)

        return (self.kind == other.kind and
                self.name == other.name and
                self.element_type == other.element_type and
                self.base_type == other.base_type and
                self.size == other.size and
                self.param_types == other.param_types and
                self.return_type == other.return_type)

    def __hash__(self) -> int:
        return hash(
            (
                self.kind,
                self.name,
                self.element_type,
                self.base_type,
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
    warnings: List[str] = field(default_factory=list)
    # LSP / IDE extras (optional; safe defaults for existing callers)
    struct_fields: Dict[str, List[Tuple[str, str]]] = field(default_factory=dict)
    # Ordered local/param bindings seen during check: {name,type,kind,container,mutable}
    locals: List[Dict[str, Any]] = field(default_factory=list)


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
        'len': TypeKind.I64,  # FLOW builtin: array/slice length
        'strcpy': TypeKind.POINTER,
        'strcat': TypeKind.POINTER,
        'strcmp': TypeKind.I32,
        'strncpy': TypeKind.POINTER,
        'strncmp': TypeKind.I32,
        'exit': TypeKind.VOID,
        'abort': TypeKind.VOID,
        'flow_panic': TypeKind.VOID,
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

    # RT-safety (docs/library/rt-safety.md): the `@rt_safe` attribute marks a
    # function as callable from a hard real-time path. Its body (and anything
    # it calls, transitively) must never touch the heap, open devices/files,
    # submit GPU work that allocates/syncs, or take blocking locks.
    #
    # Matching is exact name match only (see `_check_rt_safe_call`); every
    # concrete symbol that should be banned must be listed below.
    #
    # Direct heap primitives - always forbidden in an `@rt_safe` call chain.
    RT_UNSAFE_BUILTINS: frozenset = frozenset({
        'malloc', 'calloc', 'realloc', 'free', 'alloc', 'dealloc',
    })
    # `lib/stdlib/memory.flow` helpers that call the primitives above
    # directly, so they are unsafe by name even though they aren't builtins.
    # `arena_alloc*` / `arena_reset` / `arena_used` / `arena_remaining` are
    # intentionally NOT listed: a bump allocation from an already-created
    # arena does not allocate/free, so it stays RT-safe (see rt-safety.md,
    # "Allowed on the audio thread"). Only creating/destroying/growing the
    # arena's backing storage is forbidden.
    RT_UNSAFE_STDLIB_NAMES: frozenset = frozenset({
        'alloc_bytes', 'alloc_zeroed', 'alloc_i32', 'alloc_f32', 'alloc_f64',
        'arena_create', 'arena_destroy',
    })
    # Audio device lifecycle + buffer alloc (lib/stdlib/audio/io.flow,
    # lib/stdlib/audio.flow). Ring-buffer read/write helpers and pure
    # predicates (`audio_device_ok`, `audio_device_has_*`, `audio_device_config`)
    # stay allowed.
    RT_UNSAFE_AUDIO_NAMES: frozenset = frozenset({
        'audio_device_open', 'audio_device_start', 'audio_device_stop',
        'audio_device_close',
        'flow_audio_open', 'flow_audio_start', 'flow_audio_stop',
        'flow_audio_close',
        'audio_probe_devices', 'flow_audio_probe_devices',
        'audio_buffer_alloc_f32', 'audio_buffer_free_f32',
        'delay_line_new',
    })
    # File I/O (lib/stdlib/posix.flow wrappers + common C stdio names if
    # exposed via extern).
    RT_UNSAFE_FILE_NAMES: frozenset = frozenset({
        'file_open', 'file_close',
        'fopen', 'fread', 'fwrite', 'fclose',
    })
    # GPU alloc / free / copy / sync (lib/stdlib/gpu_memory.flow +
    # runtime/gpu_memory.h, plus Metal buffer create builtin).
    RT_UNSAFE_GPU_NAMES: frozenset = frozenset({
        'flow_gpu_alloc', 'flow_gpu_free',
        'flow_gpu_copy_h2d', 'flow_gpu_copy_d2h', 'flow_gpu_copy_d2d',
        'flow_gpu_sync',
        'gpu_alloc_flags', 'gpu_alloc', 'gpu_alloc_unified', 'gpu_alloc_private',
        'gpu_alloc_f32', 'gpu_alloc_f64', 'gpu_alloc_i32', 'gpu_allocate',
        'gpu_free',
        'gpu_copy_h2d', 'gpu_copy_d2h', 'gpu_copy_d2d',
        'gpu_copy_h2d_i32', 'gpu_copy_d2h_i32',
        'gpu_copy_h2d_f32', 'gpu_copy_d2h_f32',
        'gpu_copy_to_device', 'gpu_copy_from_device', 'gpu_copy_device_to_device',
        'gpu_sync',
        'metal_create_buffer',
    })
    # Blocking locks / thread create-join (lib/stdlib/concurrent.flow).
    # `mutex_is_locked` is a non-blocking field read and is intentionally
    # omitted. Atomics stay allowed.
    RT_UNSAFE_LOCK_NAMES: frozenset = frozenset({
        'mutex_new', 'mutex_bind', 'mutex_lock', 'mutex_unlock',
        'mutex_trylock', 'mutex_destroy',
        'pthread_mutex_init', 'pthread_mutex_lock', 'pthread_mutex_unlock',
        'pthread_mutex_trylock', 'pthread_mutex_destroy',
        'pthread_create', 'pthread_join',
        'flow_thread_spawn', 'flow_thread_join',
        'flow_race_mutex_lock', 'flow_race_mutex_unlock',
        'pthread_cond_wait',
    })
    RT_UNSAFE_HEAP_NAMES: frozenset = (
        RT_UNSAFE_BUILTINS
        | RT_UNSAFE_STDLIB_NAMES
        | RT_UNSAFE_AUDIO_NAMES
        | RT_UNSAFE_FILE_NAMES
        | RT_UNSAFE_GPU_NAMES
        | RT_UNSAFE_LOCK_NAMES
    )

    def __init__(self):
        self.global_scope = Scope()
        self.current_scope = self.global_scope
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.struct_types: Dict[str, StructDecl] = {}
        self.generic_struct_types: Dict[str, StructDecl] = {}
        self.effect_types: Dict[str, EffectDecl] = {}
        self.capability_types: Dict[str, CapabilityDecl] = {}
        # Enum/ADT metadata, used for match exhaustiveness checking and to
        # disambiguate "path pattern" identifiers (e.g. `Option_i32_Some`)
        # from ordinary identifier bindings in match arms.
        self.enum_decls: Dict[str, EnumDecl] = {}  # enum name -> EnumDecl
        self.enum_variant_owner: Dict[str, str] = {}  # "Enum_Variant" -> "Enum"
        # Builtin implicit UI layout state pointer
        ui_state_type = SemanticType(TypeKind.POINTER, element_type=SemanticType(TypeKind.VOID))
        self.global_scope.define(Symbol("_ui_state", ui_state_type, "variable", is_mutable=True))
        self.strict = True
        # Active collector for return statement types of the function currently
        # being checked (None outside function bodies).
        self._return_type_sink: Optional[List[SemanticType]] = None
        self.trait_types: Dict[str, TraitDecl] = {}
        self.impl_pairs: set = set()  # (type_name, trait_name)
        self.impl_methods: Dict[Tuple[str, str], List[str]] = {}
        # Units of measure (north-star.md section 6). Base units are indexed
        # in declaration order; every unit name maps to its canonical
        # (trailing zeros stripped) dimension exponent vector. unit_canonical
        # maps a vector back to the first declared unit with that dimension,
        # for naming the results of * and /.
        self.unit_base_order: List[str] = []
        self.unit_dims: Dict[str, Tuple[int, ...]] = {}
        self.unit_canonical: Dict[Tuple[int, ...], str] = {}

        # RT-safety (docs/library/rt-safety.md): maps a function name to the
        # name of the (transitively) closest banned call it reaches,
        # e.g. {"delay_fill": "arena_create"}. Populated by `check()` before
        # function bodies are checked. Empty means no `@rt_safe` functions
        # were seen or the pass hasn't run yet.
        self._rt_unsafe_reason: Dict[str, str] = {}
        # Name of the `@rt_safe` function currently being checked, or None
        # when checking a function without that attribute.
        self._current_rt_safe_fn: Optional[str] = None

    def _is_numeric(self, t: SemanticType) -> bool:
        return t.kind in {
            TypeKind.I8, TypeKind.I16, TypeKind.I32, TypeKind.I64, TypeKind.I128,
            TypeKind.U8, TypeKind.U16, TypeKind.U32, TypeKind.U64, TypeKind.U128,
            TypeKind.F32, TypeKind.F64
        }

    def _is_dual(self, t: SemanticType) -> bool:
        return t.kind == TypeKind.STRUCT and t.name == "Dual"

    def _is_tensor(self, t: SemanticType) -> bool:
        return t.kind == TypeKind.STRUCT and t.name == "Tensor"

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

    # ---- Units of measure (north-star.md section 6) ----

    @staticmethod
    def _normalize_dims(dims) -> Tuple[int, ...]:
        """Strip trailing zeros so vectors of different lengths compare equal
        regardless of how many base units were declared when they were made."""
        dims = list(dims)
        while dims and dims[-1] == 0:
            dims.pop()
        return tuple(dims)

    @staticmethod
    def _combine_dims(a: Tuple[int, ...], b: Tuple[int, ...], sign: int) -> Tuple[int, ...]:
        """Component-wise a + sign*b, padded to a common length, normalized."""
        n = max(len(a), len(b))
        a = list(a) + [0] * (n - len(a))
        b = list(b) + [0] * (n - len(b))
        return TypeChecker._normalize_dims(x + sign * y for x, y in zip(a, b))

    def _register_unit(self, decl: UnitDecl) -> Optional[Tuple[int, ...]]:
        """Record a `unit` declaration and return its dimension vector."""
        loc = f"line {decl.line}: " if getattr(decl, 'line', 0) else ""
        if decl.name in self.unit_dims:
            self.errors.append(f"{loc}unit '{decl.name}' is already declared")
            return self.unit_dims[decl.name]
        if decl.factors is None:
            # New base dimension: next index in declaration order.
            index = len(self.unit_base_order)
            self.unit_base_order.append(decl.name)
            dims: Tuple[int, ...] = tuple([0] * index + [1])
        else:
            acc: Tuple[int, ...] = ()
            for factor_name, exponent in decl.factors:
                factor_dims = self.unit_dims.get(factor_name)
                if factor_dims is None:
                    self.errors.append(
                        f"{loc}unknown unit '{factor_name}' in declaration of "
                        f"'{decl.name}' (units must be declared before use)"
                    )
                    continue
                scaled = tuple(x * exponent for x in factor_dims)
                acc = self._combine_dims(acc, scaled, 1)
            dims = acc
        self.unit_dims[decl.name] = dims
        if dims and dims not in self.unit_canonical:
            self.unit_canonical[dims] = decl.name
        return dims

    def _dims_of(self, t: Optional[SemanticType]) -> Optional[Tuple[int, ...]]:
        """The dimension vector of a type, or None for non-unit types."""
        if t is None:
            return None
        if t.kind == TypeKind.TYPE_ALIAS and t.base_type is not None:
            return self._dims_of(t.base_type)
        if t.kind == TypeKind.DISTINCT:
            return t.dims
        return None

    def _format_dims(self, dims: Tuple[int, ...]) -> str:
        """Printable name for an anonymous dimensioned type, in the spec's
        style: Meter*Kilogram/Second^2. An empty numerator prints as 1."""
        numerator = []
        denominator = []
        for index, exponent in enumerate(dims):
            if exponent == 0:
                continue
            base = (self.unit_base_order[index]
                    if index < len(self.unit_base_order) else f"dim{index}")
            magnitude = abs(exponent)
            part = base if magnitude == 1 else f"{base}^{magnitude}"
            (numerator if exponent > 0 else denominator).append(part)
        text = "*".join(numerator) if numerator else "1"
        for part in denominator:
            text += f"/{part}"
        return text

    def _unit_result_type(self, dims: Tuple[int, ...]) -> SemanticType:
        """The type of a * or / result with the given dimension vector: the
        canonical declared unit when one exists, an anonymous dimensioned
        type otherwise, and plain f64 when everything cancels."""
        dims = self._normalize_dims(dims)
        if not dims:
            return SemanticType(TypeKind.F64)
        name = self.unit_canonical.get(dims, self._format_dims(dims))
        return SemanticType(
            kind=TypeKind.DISTINCT,
            name=name,
            base_type=SemanticType(TypeKind.F64),
            dims=dims,
        )

    def _check_dimensioned_op(
        self,
        op: BinaryOperation,
        left_type: SemanticType,
        right_type: SemanticType,
        left_dims: Optional[Tuple[int, ...]],
        right_dims: Optional[Tuple[int, ...]],
    ) -> Optional[SemanticType]:
        """Dimensional analysis for a binary op where at least one operand is
        a unit type. Returns the result type, or None to fall through to the
        ordinary checking path (used when the other operand is neither a unit
        nor a numeric scalar, e.g. a string)."""
        line = getattr(op, 'line', 0)
        loc = f"line {line}: " if line else ""
        operator = op.operator

        if operator in ("*", "/"):
            # Dimensionless numeric scalars multiply and divide freely.
            if left_dims is None and not self._is_numeric(left_type):
                return None
            if right_dims is None and not self._is_numeric(right_type):
                return None
            sign = 1 if operator == "*" else -1
            dims = self._combine_dims(left_dims or (), right_dims or (), sign)
            return self._unit_result_type(dims)

        if operator in ("+", "-", "%"):
            if left_dims is None or right_dims is None or left_dims != right_dims:
                if left_dims is None or right_dims is None:
                    hint = ("a dimensionless value needs an explicit cast, "
                            "e.g. `x as " + str(left_type if left_dims is not None else right_type) + "`")
                else:
                    hint = f"operands of '{operator}' must have the same dimension"
                self.errors.append(
                    f"{loc}dimensional error: {left_type} {operator} {right_type} ({hint})"
                )
            # Recover with the dimensioned side so errors do not cascade.
            return left_type if left_dims is not None else right_type

        if operator in ("==", "!=", "<", ">", "<=", ">="):
            if left_dims is None or right_dims is None or left_dims != right_dims:
                self.errors.append(
                    f"{loc}dimensional error: {left_type} {operator} {right_type} "
                    f"(comparison requires both operands to have the same dimension)"
                )
            return SemanticType(TypeKind.BOOL)

        # Logical, bitwise, and shift operators have no dimensional meaning.
        self.errors.append(
            f"{loc}dimensional error: operator '{operator}' is not defined for "
            f"unit types ({left_type} {operator} {right_type})"
        )
        return left_type if left_dims is not None else right_type

    def _can_coerce(self, actual: SemanticType, expected: SemanticType) -> bool:
        if actual is None or expected is None:
            return True
        # Treat void/unknown as a wildcard only in lenient checking
        if not self.strict and (
            actual.kind in {TypeKind.VOID, TypeKind.UNKNOWN}
            or expected.kind in {TypeKind.VOID, TypeKind.UNKNOWN}
        ):
            return True
        if actual == expected:
            return True
        # Unit types agree when their dimension vectors agree (an anonymous
        # Meter/Second result assigns to a declared Velocity, and vice versa).
        actual_dims = self._dims_of(actual)
        expected_dims = self._dims_of(expected)
        if actual_dims is not None and expected_dims is not None:
            return actual_dims == expected_dims
        if actual_dims is not None or expected_dims is not None:
            return False
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
            if actual.size == 0:
                return True
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
        # Struct coercion only in lenient mode
        if not self.strict and (actual.kind == TypeKind.STRUCT or expected.kind == TypeKind.STRUCT):
            return True
        return False

    def check(self, declarations: List[Any]) -> TypeCheckResult:
        """Main entry point for type checking."""
        self.errors = []
        self.warnings = []
        self._lsp_locals: List[Dict[str, Any]] = []

        # Phase 1: Collect type definitions (structs, effects, capabilities)
        self._collect_types(declarations)

        # Phase 2: Collect function signatures and global symbols
        self._collect_symbols(declarations)

        # Phase 2.5: Build the RT-safety call graph (which functions reach a
        # banned API, directly or transitively) so `@rt_safe` violations can
        # be reported at the call site during Phase 3.
        self._rt_unsafe_reason = self._compute_rt_unsafe_functions(declarations)

        # Phase 3: Type check all declarations
        self._check_declarations(declarations)

        struct_fields: Dict[str, List[Tuple[str, str]]] = {}
        for sname, sdecl in self.struct_types.items():
            fields: List[Tuple[str, str]] = []
            for f in getattr(sdecl, 'fields', None) or []:
                try:
                    fields.append((f.name, str(self._parse_type(f.type))))
                except Exception:
                    fields.append((f.name, getattr(getattr(f, 'type', None), 'name', 'unknown') or 'unknown'))
            struct_fields[sname] = fields

        return TypeCheckResult(
            typed_ast=declarations,  # For now, just return the original AST
            symbol_table=dict(self.global_scope.symbols),
            errors=self.errors,
            warnings=self.warnings,
            struct_fields=struct_fields,
            locals=list(self._lsp_locals),
        )

    def _record_local(
        self,
        name: str,
        typ: SemanticType,
        *,
        kind: str,
        container: str,
        mutable: bool = False,
    ) -> None:
        """Record a local/param for LSP hover (best-effort, ordered)."""
        locals_list = getattr(self, '_lsp_locals', None)
        if locals_list is None:
            return
        locals_list.append({
            'name': name,
            'type': str(typ),
            'kind': kind,
            'container': container,
            'mutable': mutable,
        })

    def _collect_types(self, declarations: List[Any]) -> None:
        """Collect struct, effect, capability, type alias, and distinct type definitions."""
        for decl in declarations:
            if isinstance(decl, StructDecl):
                if decl.name in self.struct_types:
                    self.errors.append(f"Struct '{decl.name}' already defined")
                else:
                    self.struct_types[decl.name] = decl
                    if decl.type_params:
                        self.generic_struct_types[decl.name] = decl
            elif isinstance(decl, EnumDecl):
                # Enums are represented as structs with a 'tag' field
                # For simplicity in type checking, register as a struct
                enum_struct = StructDecl(decl.name, [
                    Parameter("tag", ParsedType("i32"))
                ])
                self.struct_types[decl.name] = enum_struct
                self.enum_decls[decl.name] = decl

                # Register variants as global constants
                for variant in decl.variants:
                    variant_name = f"{decl.name}_{variant.name}"
                    self.global_scope.define(Symbol(variant_name, SemanticType(TypeKind.I32), "const"))
                    self.enum_variant_owner[variant_name] = decl.name

            elif isinstance(decl, TypeAliasDecl):
                # Type aliases are transparent - just map name to base type
                base_type = self._parse_type(decl.base_type)
                alias_type = SemanticType(
                    kind=TypeKind.TYPE_ALIAS,
                    name=decl.name,
                    base_type=base_type
                )
                symbol = Symbol(decl.name, alias_type, "type",
                              getattr(decl, 'is_exported', False), decl)
                self.global_scope.define(symbol)
                # Also register in struct_types for lookup
                self.struct_types[decl.name] = decl

            elif isinstance(decl, DistinctTypeDecl):
                # Distinct types are opaque - incompatible with base type.
                # Unit declarations are distinct types plus a dimension vector.
                base_type = self._parse_type(decl.base_type)
                dims = None
                if isinstance(decl, UnitDecl):
                    dims = self._register_unit(decl)
                distinct_type = SemanticType(
                    kind=TypeKind.DISTINCT,
                    name=decl.name,
                    base_type=base_type,
                    dims=dims
                )
                symbol = Symbol(decl.name, distinct_type, "type",
                              getattr(decl, 'is_exported', False), decl)
                self.global_scope.define(symbol)
                # Also register in struct_types for lookup
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
            elif isinstance(decl, TraitDecl):
                if decl.name in self.trait_types:
                    self.errors.append(f"Trait '{decl.name}' already defined")
                else:
                    self.trait_types[decl.name] = decl
            elif isinstance(decl, ImplDecl):
                self.impl_pairs.add((decl.for_type.name, decl.trait_name))
                for method in decl.methods:
                    self.impl_methods.setdefault(
                        (decl.for_type.name, method.name), []
                    ).append(f"{decl.for_type.name}_{decl.trait_name}_{method.name}")

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

    def _iter_call_names(self, node: Any, seen: Set[int]) -> "list[str]":
        """Recursively collect every `FunctionCall.name` reachable from `node`.

        Walks the AST generically via dataclass fields so it doesn't need to
        know every statement/expression type. Used to build the RT-safety
        call graph (see `_compute_rt_unsafe_functions`).
        """
        names: list[str] = []
        if node is None:
            return names
        if isinstance(node, FunctionCall):
            names.append(node.name)
        if dataclasses.is_dataclass(node) and not isinstance(node, type):
            node_id = id(node)
            if node_id in seen:
                return names
            seen.add(node_id)
            for f in dataclasses.fields(node):
                names.extend(self._iter_call_names(getattr(node, f.name), seen))
        elif isinstance(node, (list, tuple)):
            for item in node:
                names.extend(self._iter_call_names(item, seen))
        elif isinstance(node, dict):
            for value in node.values():
                names.extend(self._iter_call_names(value, seen))
        return names

    def _compute_rt_unsafe_functions(self, declarations: List[Any]) -> Dict[str, str]:
        """Compute which user-defined functions are RT-unsafe.

        Returns a map from function name to the name of the nearest
        banned call it reaches (itself, for `RT_UNSAFE_HEAP_NAMES`
        members; a callee's name otherwise). This is a simple fixed-point
        over the direct-call graph, so it also catches indirect/transitive
        violations (e.g. an RT-safe function calling a helper that itself
        calls `malloc` or `mutex_lock`).
        """
        direct_calls: Dict[str, Set[str]] = {}

        def register(name: str, body: Optional[Block]) -> None:
            if body is None:
                return
            direct_calls[name] = set(self._iter_call_names(body, set()))

        for decl in declarations:
            if isinstance(decl, FunctionDecl) and not getattr(decl, 'is_extern', False):
                register(decl.name, decl.body)
            elif isinstance(decl, ImplDecl):
                for method in decl.methods:
                    mangled_name = f"{decl.for_type.name}_{decl.trait_name}_{method.name}"
                    register(mangled_name, method.body)

        unsafe_reason: Dict[str, str] = {name: name for name in self.RT_UNSAFE_HEAP_NAMES}

        changed = True
        while changed:
            changed = False
            for name, callees in direct_calls.items():
                if name in unsafe_reason:
                    continue
                for callee in callees:
                    if callee in unsafe_reason:
                        unsafe_reason[name] = callee
                        changed = True
                        break

        return unsafe_reason

    def _check_rt_safe_call(self, name: str) -> None:
        """If we're inside an `@rt_safe` function body, flag calls that reach
        a banned API (heap, device/file I/O, GPU alloc/sync, or blocking lock),
        directly or transitively."""
        if self._current_rt_safe_fn is None:
            return
        reason = self._rt_unsafe_reason.get(name)
        if reason is None:
            return
        fn = self._current_rt_safe_fn
        if reason == name:
            self.errors.append(
                f"RT-safety violation: '{fn}' is marked '@rt_safe' but calls "
                f"'{name}', which is forbidden on an RT-safe path "
                f"(heap, device/file I/O, GPU, or blocking lock; "
                f"see docs/library/rt-safety.md)"
            )
        else:
            self.errors.append(
                f"RT-safety violation: '{fn}' is marked '@rt_safe' but calls "
                f"'{name}', which is not RT-safe because it calls '{reason}' "
                f"(forbidden on an RT-safe path; see docs/library/rt-safety.md)"
            )

    def _check_trait_bounds(self, func: FunctionDecl) -> None:
        """Validate generic type parameter trait bounds when concrete types are known."""
        type_params = getattr(func, "type_params", None) or []
        for tp in type_params:
            if tp.bound and self.strict:
                # Bounds are checked at monomorphization sites; warn if trait unknown
                if tp.bound not in self.trait_types:
                    self.errors.append(
                        f"Unknown trait bound '{tp.bound}' on type parameter '{tp.name}'"
                    )

    def _check_function(self, func: FunctionDecl) -> None:
        """Type check a function declaration."""
        # Extern functions have no body to check - they're just declarations
        if getattr(func, 'is_extern', False):
            return

        self._check_trait_bounds(func)
        
        # Create function scope
        func_scope = Scope(parent=self.current_scope)
        self.current_scope = func_scope

        # `@rt_safe` (docs/library/rt-safety.md): while checking this
        # function's body, flag any call that reaches a banned RT-unsafe API.
        attrs = getattr(func, 'attributes', None) or []
        prev_rt_safe_fn = self._current_rt_safe_fn
        self._current_rt_safe_fn = func.name if 'rt_safe' in attrs else None

        try:
            # Add parameters to scope
            for param in func.parameters:
                param_type = self._parse_type(param.type)
                symbol = Symbol(param.name, param_type, "variable")
                func_scope.define(symbol)
                self._record_local(
                    param.name, param_type,
                    kind='parameter', container=func.name, mutable=False,
                )

            # Type check function body, collecting return types as we go so
            # return expressions are resolved in their proper scopes.
            prev_sink = self._return_type_sink
            prev_container = getattr(self, '_lsp_container', None)
            self._return_type_sink = []
            self._lsp_container = func.name
            try:
                self._check_block(func.body)
                returns = self._return_type_sink
            finally:
                self._return_type_sink = prev_sink
                self._lsp_container = prev_container
            expected_return = self._parse_type(func.return_type)

            if returns:
                for rt in returns:
                    if not self._can_coerce(rt, expected_return):
                        self.errors.append(
                            f"Function '{func.name}' returns {rt} but should return {expected_return}"
                        )

        finally:
            self.current_scope = func_scope.parent
            self._current_rt_safe_fn = prev_rt_safe_fn

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
        elif isinstance(stmt, (FunctionCall, EffectCall)):
            return self._check_expression(stmt)
        elif isinstance(stmt, LayoutStatement):
            for arg in stmt.args:
                self._check_expression(arg)
            return self._check_block(stmt.body)
        elif isinstance(stmt, MatchStatement):
            return self._check_match_stmt(stmt)
        elif isinstance(stmt, DeferStatement):
            self._check_expression(stmt.expr)
            return SemanticType(TypeKind.VOID)
        elif isinstance(stmt, ExpectStatement):
            condition_type = self._check_expression(stmt.condition)
            if condition_type.kind != TypeKind.BOOL:
                self.errors.append(
                    f"expect condition must be a bool, got {condition_type}"
                )
            return SemanticType(TypeKind.VOID)
        elif isinstance(stmt, (BreakStatement, ContinueStatement)):
            return SemanticType(TypeKind.VOID)
        else:
            return SemanticType(TypeKind.VOID)

    def _bind_struct_pattern(self, pattern: "StructPattern", case_scope: "Scope") -> None:
        """Type-check a (possibly nested) StructPattern and bind its variables.

        Recurses into `field_patterns` for struct-in-struct nesting (e.g.
        `Outer(Inner(x), y)`), so bindings from any nesting depth land in
        `case_scope` and nested literal fields are checked against their own
        struct's field types.
        """
        struct_decl = self.struct_types.get(pattern.struct_name)
        if struct_decl is None:
            self.errors.append(f"Unknown struct in match pattern: {pattern.struct_name}")
            return
        fields = getattr(struct_decl, "fields", None) or []
        field_literals = pattern.field_literals or {}
        field_patterns = pattern.field_patterns or {}
        for i, binding in enumerate(pattern.bindings):
            if i in field_patterns:
                # Struct-in-struct nesting - recurse using the nested pattern;
                # its own struct name (not this field's declared type) drives
                # field lookups, matching the c_generator lowering.
                self._bind_struct_pattern(field_patterns[i], case_scope)
                continue
            if i in field_literals:
                # Nested literal pattern (e.g. `Point(0, y)`) - no binding,
                # just check the literal is compatible with the field type.
                if i < len(fields):
                    field_type = self._parse_type(fields[i].type)
                    lit_type = self._check_literal(field_literals[i])
                    if not self._can_coerce(field_type, lit_type) and not self._can_coerce(lit_type, field_type):
                        if self.strict:
                            self.errors.append(
                                f"Match pattern field {i} of {pattern.struct_name} "
                                f"expects {field_type}, got literal {lit_type}"
                            )
                continue
            if binding == "_":
                continue
            if i < len(fields):
                bind_type = self._parse_type(fields[i].type)
            else:
                bind_type = SemanticType(TypeKind.UNKNOWN)
            case_scope.define(Symbol(binding, bind_type, "variable"))

    def _is_integer_literal_pattern(self, pattern: Any) -> bool:
        """True if pattern is an integer Literal or OrPattern of only those."""
        if isinstance(pattern, Literal):
            return self._is_integer(self._check_literal(pattern))
        if isinstance(pattern, OrPattern):
            return bool(pattern.patterns) and all(
                self._is_integer_literal_pattern(alt) for alt in pattern.patterns
            )
        return False

    def _is_bool_literal_pattern(self, pattern: Any) -> bool:
        """True if pattern is a bool Literal or OrPattern of only those."""
        if isinstance(pattern, Literal):
            return self._check_literal(pattern).kind == TypeKind.BOOL
        if isinstance(pattern, OrPattern):
            return bool(pattern.patterns) and all(
                self._is_bool_literal_pattern(alt) for alt in pattern.patterns
            )
        return False

    def _bool_literal_values(self, pattern: Any) -> List[bool]:
        """Collect the concrete bool values a bool-literal/OrPattern covers."""
        if isinstance(pattern, Literal):
            return [str(pattern.value).lower() == "true"]
        if isinstance(pattern, OrPattern):
            values: List[bool] = []
            for alt in pattern.patterns:
                values.extend(self._bool_literal_values(alt))
            return values
        return []

    def _integer_literal_values(self, pattern: Any) -> List[int]:
        """Collect concrete integer values a literal/OrPattern covers."""
        if isinstance(pattern, Literal):
            try:
                return [int(pattern.value)]
            except (TypeError, ValueError):
                return []
        if isinstance(pattern, OrPattern):
            values: List[int] = []
            for alt in pattern.patterns:
                values.extend(self._integer_literal_values(alt))
            return values
        return []

    @staticmethod
    def _format_int_gaps(covered: set, lo: int, hi: int, limit: int = 8) -> str:
        """Describe missing integers in [lo, hi], compressed into ranges."""
        gaps: List[str] = []
        x = lo
        while x <= hi and len(gaps) < limit:
            if x in covered:
                x += 1
                continue
            start = x
            while x <= hi and x not in covered:
                x += 1
            end = x - 1
            gaps.append(str(start) if start == end else f"{start}..{end}")
        remaining = 0
        while x <= hi:
            if x not in covered:
                remaining += 1
            x += 1
        if remaining:
            gaps.append(f"+{remaining} more")
        return ", ".join(gaps)

    def _lookup_const_symbol(self, name: str) -> Optional["Symbol"]:
        """Resolve `name` to a global `const` symbol, if it is one.

        Used to disambiguate a bare identifier match pattern (e.g.
        `Option_i32_Some`) as a "path/const pattern" (a value-equality
        check) rather than an identifier binding. Only `const` symbols
        qualify - ordinary variables/functions/etc. still bind as before.
        """
        if name == "_":
            return None
        symbol = self.current_scope.lookup(name)
        if symbol is not None and symbol.kind == "const":
            return symbol
        return None

    def _infer_type_quiet(self, expr: Any) -> SemanticType:
        """Type-check `expr` without recording any new errors/warnings.

        Used when we need an expression's type for exhaustiveness analysis
        but the expression was (or will be) checked elsewhere already -
        avoids duplicating diagnostics for the same subexpression.
        """
        saved_errors, saved_warnings = self.errors, self.warnings
        self.errors, self.warnings = [], []
        try:
            return self._check_expression(expr)
        finally:
            self.errors, self.warnings = saved_errors, saved_warnings

    def _match_enum_target(self, match_stmt: MatchStatement, value_type: SemanticType) -> Optional[str]:
        """Return the enum name being matched on, if any.

        Covers two shapes: matching directly on an enum-typed value
        (`match opt { ... }`) and matching on its `.tag` field
        (`match opt.tag { ... }`), which is the idiom used elsewhere in the
        codebase for enum dispatch (enums lower to a `{ tag, ... }` struct).
        """
        if value_type.kind == TypeKind.STRUCT and value_type.name in self.enum_decls:
            return value_type.name
        if isinstance(match_stmt.value, FieldAccess) and match_stmt.value.field == "tag":
            obj_type = self._infer_type_quiet(match_stmt.value.object)
            if obj_type.kind == TypeKind.STRUCT and obj_type.name in self.enum_decls:
                return obj_type.name
        return None

    def _warn_enum_exhaustiveness(self, match_stmt: MatchStatement, enum_name: str) -> None:
        """Real exhaustiveness check for enum/ADT matches (path/const patterns).

        A case pattern counts as covering a variant when it is a bare
        identifier that resolves (via `_lookup_const_symbol`) to that
        variant's generated constant, e.g. `Option_i32_Some` for
        `enum Option_i32 { Some(i32), None }`. Any other pattern shape
        (struct/literal/plain binding) makes coverage un-attributable, so we
        conservatively skip the check rather than risk a false positive -
        this only fires when *every* arm is a recognized variant pattern.
        """
        if match_stmt.default_case is not None:
            return

        enum_decl = self.enum_decls[enum_name]
        all_variants = {variant.name for variant in enum_decl.variants}
        covered: set = set()

        for case in match_stmt.cases:
            pat = case.pattern
            if isinstance(pat, Variable) and pat.name == "_":
                return  # wildcard - exhaustive by construction
            if not isinstance(pat, Variable):
                return  # unrecognized pattern shape - don't guess
            owner = self.enum_variant_owner.get(pat.name)
            if owner != enum_name or self._lookup_const_symbol(pat.name) is None:
                return  # not a known variant of this enum - don't guess
            if case.guard is None:
                covered.add(pat.name[len(enum_name) + 1:])

        missing = sorted(all_variants - covered)
        if missing:
            self.warnings.append(
                f"Non-exhaustive match: enum '{enum_name}' patterns do not cover "
                f"variant(s) {', '.join(missing)} (add the missing variant(s) or `_`/`default`)"
            )

    def _warn_match_exhaustiveness_stub(self, match_stmt: MatchStatement, value_type: SemanticType) -> None:
        """Exhaustiveness checking for `match`, with three tiers of coverage:

        1. Enum/ADT matches: a *real* exhaustiveness check when matching
           directly on an enum value or its `.tag` field with path/const
           patterns (see `_warn_enum_exhaustiveness`) - requires every
           variant covered or a wildcard/`default`.
        2. Boolean matches: bool has exactly two inhabitants, so this is a
           *real* exhaustiveness check (not a stub) - if every arm is a bool
           literal (or `|` of those) and the set of covered values is not
           `{true, false}`, and there's no wildcard/`default`, warn.
        3. Integer matches: range/gap analysis over the literal arms. Unguarded
           integer literal / `|` arms contribute concrete covered values. If
           there's no wildcard/`default`, warn with:
             - gaps inside [min(covered), max(covered)] (e.g. `0 | 1 | 3`
               reports a gap at `2`), and
             - a note that the full integer domain outside that span is also
               uncovered (i32/i64 can never be listed exhaustively).
           Guarded arms do not count as covering their literal.

        Warnings are collected on `TypeCheckResult.warnings`, not hard errors.
        """
        enum_name = self._match_enum_target(match_stmt, value_type)
        if enum_name is not None:
            self._warn_enum_exhaustiveness(match_stmt, enum_name)
            return

        if match_stmt.default_case is not None:
            return

        has_wildcard = False
        all_int_literals = True
        saw_int_literal = False
        all_bool_literals = True
        saw_bool_literal = False
        covered_bools: set = set()
        covered_ints: set = set()

        for case in match_stmt.cases:
            pat = case.pattern
            if isinstance(pat, Variable) and pat.name == "_":
                has_wildcard = True
                continue
            if self._is_integer_literal_pattern(pat):
                saw_int_literal = True
                if case.guard is None:
                    covered_ints.update(self._integer_literal_values(pat))
            else:
                all_int_literals = False
            if self._is_bool_literal_pattern(pat):
                saw_bool_literal = True
                if case.guard is None:
                    covered_bools.update(self._bool_literal_values(pat))
            else:
                all_bool_literals = False

        if has_wildcard:
            return

        if all_bool_literals and saw_bool_literal:
            if covered_bools != {True, False}:
                self.warnings.append(
                    "Non-exhaustive match: bool patterns do not cover both "
                    "`true` and `false` (add the missing value or `_`/`default`)"
                )
            return

        if all_int_literals and saw_int_literal:
            if not covered_ints:
                # Only guarded integer arms — still not exhaustive.
                self.warnings.append(
                    "Non-exhaustive match: integer patterns are all guarded or "
                    "empty; add `_` or `default` for the remaining values"
                )
                return
            lo = min(covered_ints)
            hi = max(covered_ints)
            span = hi - lo + 1
            missing_inside = span - len(covered_ints)
            parts = [
                "Non-exhaustive match: integer literal patterns do not cover "
                "all values"
            ]
            if missing_inside > 0:
                gap_desc = self._format_int_gaps(covered_ints, lo, hi)
                parts.append(f"gaps in [{lo}, {hi}]: {gap_desc}")
            else:
                parts.append(f"contiguous cover [{lo}, {hi}]")
            parts.append(
                "values outside that span also uncovered (add `_` or `default`)"
            )
            self.warnings.append("; ".join(parts))

    def _check_match_stmt(self, match_stmt: MatchStatement) -> SemanticType:
        """Type check a match statement."""
        value_type = self._check_expression(match_stmt.value)
        result_type = SemanticType(TypeKind.VOID)
        for case in match_stmt.cases:
            # Pattern bindings are scoped to the case's guard and body.
            case_scope = Scope(parent=self.current_scope)
            if isinstance(case.pattern, Literal):
                pat_type = self._check_literal(case.pattern)
                if not self._can_coerce(value_type, pat_type) and not self._can_coerce(pat_type, value_type):
                    if self.strict:
                        self.errors.append(
                            f"Match pattern {pat_type} incompatible with value type {value_type}"
                        )
            elif isinstance(case.pattern, StructPattern):
                self._bind_struct_pattern(case.pattern, case_scope)
            elif isinstance(case.pattern, ListPattern):
                if value_type.kind != TypeKind.ARRAY:
                    if self.strict:
                        self.errors.append(
                            f"List pattern {case.pattern} requires an array value, got {value_type}"
                        )
                else:
                    elem_type = value_type.element_type or SemanticType(TypeKind.I32)
                    for elem in case.pattern.elements:
                        if isinstance(elem, Variable) and elem.name != "_":
                            case_scope.define(
                                Symbol(elem.name, elem_type, "variable")
                            )
                        elif isinstance(elem, Literal):
                            lit_type = self._check_literal(elem)
                            if not self._can_coerce(lit_type, elem_type) and not self._can_coerce(elem_type, lit_type):
                                if self.strict:
                                    self.errors.append(
                                        f"List pattern element {lit_type} incompatible with "
                                        f"array element type {elem_type}"
                                    )
            elif isinstance(case.pattern, OrPattern):
                for alt in case.pattern.patterns:
                    if isinstance(alt, Literal):
                        pat_type = self._check_literal(alt)
                        if not self._can_coerce(value_type, pat_type) and not self._can_coerce(pat_type, value_type):
                            if self.strict:
                                self.errors.append(
                                    f"Match pattern {pat_type} incompatible with value type {value_type}"
                                )
                    elif isinstance(alt, StructPattern):
                        # Bindings agree across alternatives (parser-checked);
                        # bind once from the first struct alt below.
                        pass
                if case.pattern.patterns and isinstance(
                    case.pattern.patterns[0], StructPattern
                ):
                    self._bind_struct_pattern(case.pattern.patterns[0], case_scope)
            elif isinstance(case.pattern, Variable):
                const_symbol = self._lookup_const_symbol(case.pattern.name)
                if const_symbol is not None:
                    # Path/const pattern (e.g. an enum variant tag constant):
                    # a value-equality check, not an identifier binding.
                    compare_type = value_type
                    if value_type.kind == TypeKind.STRUCT and value_type.name in self.enum_decls:
                        compare_type = SemanticType(TypeKind.I32)  # `.tag` field
                    pat_type = const_symbol.type
                    if not self._can_coerce(compare_type, pat_type) and not self._can_coerce(pat_type, compare_type):
                        if self.strict:
                            self.errors.append(
                                f"Match pattern '{case.pattern.name}' has type {pat_type} "
                                f"incompatible with value type {value_type}"
                            )
                elif case.pattern.name != "_":
                    # Identifier pattern binds the matched value (e.g. `x if x > 0 =>`).
                    case_scope.define(Symbol(case.pattern.name, value_type, "variable"))
            prev_scope = self.current_scope
            self.current_scope = case_scope
            try:
                if case.guard is not None:
                    guard_type = self._check_expression(case.guard)
                    if guard_type.kind != TypeKind.BOOL and self.strict:
                        self.errors.append(f"Match guard must be bool, got {guard_type}")
                case_type = self._check_block(case.body)
            finally:
                self.current_scope = prev_scope
            if case_type.kind != TypeKind.VOID:
                result_type = case_type
        if match_stmt.default_case:
            default_type = self._check_block(match_stmt.default_case)
            if default_type.kind != TypeKind.VOID:
                result_type = default_type
        self._warn_match_exhaustiveness_stub(match_stmt, value_type)
        return result_type

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
        self._record_local(
            var.name, expected_type,
            kind='variable',
            container=getattr(self, '_lsp_container', '') or '',
            mutable=is_mutable,
        )

        return expected_type

    def _check_return_stmt(self, ret: ReturnStatement) -> SemanticType:
        """Type check a return statement."""
        if ret.value:
            ret_type = self._check_expression(ret.value)
        else:
            ret_type = SemanticType(TypeKind.VOID)
        # Record for the enclosing function's return-type validation. Recording
        # here (during the scoped body walk) keeps pattern/loop bindings visible,
        # unlike a separate post-pass traversal.
        if self._return_type_sink is not None:
            self._return_type_sink.append(ret_type)
        return ret_type

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
            self._check_block(if_stmt.else_block)
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
        self._record_local(
            for_stmt.variable, iter_type,
            kind='variable',
            container=getattr(self, '_lsp_container', '') or '',
            mutable=True,
        )
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
        elif isinstance(expr, EffectCall):
            return self._check_effect_call(expr)
        elif isinstance(expr, MethodCall):
            effect_name = self._effect_name_for_method_receiver(expr.object)
            if effect_name is not None:
                return self._check_effect_call(EffectCall(effect_name, expr.method, expr.arguments))
            receiver_type = self._check_expression(expr.object)
            impl_method = self._impl_method_for_receiver(receiver_type, expr.method)
            if impl_method is not None:
                return self._check_function_call(
                    FunctionCall(impl_method, [expr.object] + list(expr.arguments))
                )
            desugared = FunctionCall(expr.method, [expr.object] + list(expr.arguments))
            return self._check_function_call(desugared)
        elif isinstance(expr, StructLiteral):
            return self._check_struct_literal(expr)
        elif isinstance(expr, RecordUpdate):
            return self._check_record_update(expr)
        elif isinstance(expr, ArrayLiteral):
            if expr.elements:
                elem_type = self._check_expression(expr.elements[0])
            else:
                elem_type = SemanticType(TypeKind.I32)
            return SemanticType(TypeKind.ARRAY, element_type=elem_type, size=len(expr.elements))
        elif isinstance(expr, VectorLiteral):
            # SIMD vector literal like <1.0, 2.0, 3.0, 4.0> -> vecN_<elem>.
            elem_types = [self._check_expression(e) for e in expr.elements]
            if any(t.kind in {TypeKind.F32, TypeKind.F64} for t in elem_types):
                elem_name = "f32"
            else:
                elem_name = "i32"
            return SemanticType(
                TypeKind.UNKNOWN, name=f"vec{len(expr.elements)}_{elem_name}"
            )
        elif isinstance(expr, ArrayAccess):
            base_type = self._check_expression(expr.array)
            if base_type.kind == TypeKind.ARRAY or base_type.kind == TypeKind.POINTER:
                return base_type.element_type or SemanticType(TypeKind.VOID)
            return SemanticType(TypeKind.VOID)
        elif isinstance(expr, CastExpression):
            src_type = self._check_expression(expr.expr)
            target_type = self._parse_type(expr.target_type)
            if not self._can_cast(src_type, target_type):
                self.errors.append(f"Cannot cast {src_type} to {target_type}")
            return target_type
        elif isinstance(expr, FieldAccess):
            obj_type = self._check_expression(expr.object)
            struct_name = None
            if obj_type.kind == TypeKind.STRUCT:
                struct_name = obj_type.name
            elif obj_type.kind == TypeKind.POINTER and obj_type.element_type:
                if obj_type.element_type.kind == TypeKind.STRUCT:
                    struct_name = obj_type.element_type.name
            if struct_name and struct_name in self.struct_types:
                struct_def = self.struct_types[struct_name]
                for field in struct_def.fields:
                    if field.name == expr.field:
                        return self._parse_type(field.type)
            if self.strict:
                self.errors.append(f"Field '{expr.field}' not found on type {obj_type}")
            return SemanticType(TypeKind.UNKNOWN)
        elif isinstance(expr, TryExpr):
            operand_type = self._check_expression(expr.operand)
            if operand_type.kind == TypeKind.STRUCT and operand_type.name.startswith("Result_"):
                parts = operand_type.name.split("_")
                if len(parts) >= 2:
                    return self._parse_named_scalar(parts[1]) or SemanticType(TypeKind.I32)
            if self.strict:
                self.errors.append(f"Try operator '?' requires Result type, got {operand_type}")
            return SemanticType(TypeKind.VOID)
        elif isinstance(expr, Lambda):
            lambda_scope = Scope(parent=self.current_scope)
            param_types = []
            for p in expr.parameters:
                if p.type and p.type.name != "auto":
                    pt = self._parse_type(p.type)
                else:
                    pt = SemanticType(TypeKind.UNKNOWN)
                param_types.append(pt)
                lambda_scope.define(Symbol(p.name, pt, "variable", is_mutable=True))
            # Parameters and body locals live in the lambda's own scope, and
            # returns inside the body belong to the lambda, not the enclosing
            # function's return-type collection.
            prev_scope = self.current_scope
            prev_sink = self._return_type_sink
            self.current_scope = lambda_scope
            self._return_type_sink = []
            try:
                if isinstance(expr.body, Block):
                    self._check_block(expr.body)
                    body_type = SemanticType(TypeKind.VOID)
                else:
                    body_type = self._check_expression(expr.body)
            finally:
                self._return_type_sink = prev_sink
                self.current_scope = prev_scope
            if expr.return_type:
                ret = self._parse_type(expr.return_type)
            else:
                ret = body_type
            return SemanticType(TypeKind.FUNCTION, param_types=param_types, return_type=ret)
        elif isinstance(expr, SortExpr):
            return self._check_sort_expr(expr)
        else:
            # For now, treat unknown expressions as unknown type
            return SemanticType(TypeKind.UNKNOWN)

    def _check_sort_expr(self, expr: SortExpr) -> SemanticType:
        """Type-check declarative `|> sort` / `|> sortBy` expressions."""
        arr_type = self._check_expression(expr.array)
        if arr_type.kind != TypeKind.ARRAY:
            self.errors.append(
                f"Declarative sort requires a sized array, got {arr_type}"
            )
            return arr_type
        if arr_type.size is None:
            self.errors.append(
                "Declarative sort requires a fixed-size array (array<T, N>)"
            )
        elem = arr_type.element_type
        if elem is None:
            self.errors.append("Declarative sort could not determine element type")
            return arr_type

        numeric_ok = {
            TypeKind.I8, TypeKind.I16, TypeKind.I32, TypeKind.I64,
            TypeKind.U8, TypeKind.U16, TypeKind.U32, TypeKind.U64,
            TypeKind.F32, TypeKind.F64, TypeKind.BOOL,
        }
        if expr.keys:
            if elem.kind != TypeKind.STRUCT or not elem.name:
                self.errors.append(
                    "sort by .field requires an array of structs"
                )
                return arr_type
            struct_def = self.struct_types.get(elem.name)
            if not struct_def:
                if self.strict:
                    self.errors.append(f"Unknown struct type '{elem.name}' in sort")
                return arr_type
            field_map = {f.name: f for f in struct_def.fields}
            for key in expr.keys:
                if not key.field or key.field not in field_map:
                    self.errors.append(
                        f"Sort key '.{key.field}' is not a field of {elem.name}"
                    )
                    continue
                ft = self._parse_type(field_map[key.field].type)
                if ft.kind not in numeric_ok and ft.kind != TypeKind.STRING:
                    self.errors.append(
                        f"Sort key '.{key.field}' has unsupported type {ft} "
                        "(need numeric or string)"
                    )
        else:
            if elem.kind == TypeKind.STRUCT:
                self.errors.append(
                    "Sorting an array of structs requires `sort by .field` "
                    "(or `sortBy [.field, ...]`)"
                )
            elif elem.kind not in numeric_ok and elem.kind != TypeKind.STRING:
                self.errors.append(
                    f"Cannot sort array of {elem} (need numeric or string elements)"
                )
        return arr_type

    def _can_cast(self, actual: SemanticType, target: SemanticType) -> bool:
        if actual == target:
            return True

        # Unit types: any numeric value casts into a unit (`9.81 as Accel` is
        # the v1 way to give a literal a dimension), a unit casts back to any
        # numeric type, and unit-to-unit casts require equal dimensions.
        # Cross-dimension conversion goes through the numeric base explicitly.
        actual_dims = self._dims_of(actual)
        target_dims = self._dims_of(target)
        if actual_dims is not None and target_dims is not None:
            return actual_dims == target_dims
        if target_dims is not None:
            return self._is_numeric(actual)
        if actual_dims is not None:
            return self._is_numeric(target)

        # Distinct types: allow explicit casts to/from base type only.
        if target.kind == TypeKind.DISTINCT and target.base_type:
            return actual == target.base_type
        if actual.kind == TypeKind.DISTINCT and actual.base_type:
            return target == actual.base_type

        # Numeric explicit casts are allowed between ints/floats/bools.
        ints = {TypeKind.I8, TypeKind.I16, TypeKind.I32, TypeKind.I64, TypeKind.I128,
                TypeKind.U8, TypeKind.U16, TypeKind.U32, TypeKind.U64, TypeKind.U128}
        floats = {TypeKind.F32, TypeKind.F64}
        if actual.kind in ints | floats | {TypeKind.BOOL} and target.kind in ints | floats | {TypeKind.BOOL}:
            return True

        # Pointer casts are allowed explicitly.
        if actual.kind == TypeKind.POINTER and target.kind == TypeKind.POINTER:
            return True
        if actual.kind == TypeKind.POINTER and target.kind in ints:
            return True
        if target.kind == TypeKind.POINTER and actual.kind in ints:
            return True

        return False

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
            if self.strict:
                self.errors.append(f"Undefined variable '{var.name}'")
            return SemanticType(TypeKind.I32)
        return symbol.type

    def _check_binary_op(self, op: BinaryOperation) -> SemanticType:
        """Type check a binary operation."""
        left_type = self._check_expression(op.left)
        right_type = self._check_expression(op.right)
        # Allow unknown/void to pass through without cascading errors
        if left_type is None or right_type is None:
            return left_type or right_type or SemanticType(TypeKind.UNKNOWN)
        if left_type.kind == TypeKind.UNKNOWN or right_type.kind == TypeKind.UNKNOWN:
            # Don't report errors when operands have unknown types (error recovery)
            if op.operator in ["==", "!=", "<", ">", "<=", ">=", "&&", "||"]:
                return SemanticType(TypeKind.BOOL)
            return left_type if left_type.kind != TypeKind.UNKNOWN else right_type
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

        # Units of measure: dimensional analysis (north-star.md section 6)
        left_dims = self._dims_of(left_type)
        right_dims = self._dims_of(right_type)
        if left_dims is not None or right_dims is not None:
            result = self._check_dimensioned_op(
                op, left_type, right_type, left_dims, right_dims
            )
            if result is not None:
                return result

        # Dual arithmetic (#161): Dual ⊕ Dual/f32 → Dual
        if self._is_dual(left_type) or self._is_dual(right_type):
            if op.operator in ["+", "-", "*", "/"]:
                if self._is_dual(left_type) or self._is_numeric(left_type):
                    if self._is_dual(right_type) or self._is_numeric(right_type):
                        return SemanticType(TypeKind.STRUCT, name="Dual")
            if op.operator in ["==", "!=", "<", ">", "<=", ">="]:
                return SemanticType(TypeKind.BOOL)

        # Tensor arithmetic (#161): element-wise Tensor⊕Tensor; * / + with f32.
        if self._is_tensor(left_type) or self._is_tensor(right_type):
            if op.operator in ["+", "-", "*", "/"]:
                if self._is_tensor(left_type) and self._is_tensor(right_type):
                    return SemanticType(TypeKind.STRUCT, name="Tensor")
                if op.operator in ["*", "+"] and (
                    (self._is_tensor(left_type) and self._is_numeric(right_type))
                    or (self._is_numeric(left_type) and self._is_tensor(right_type))
                ):
                    return SemanticType(TypeKind.STRUCT, name="Tensor")

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

        # Don't cascade errors from unknown types
        if operand_type.kind == TypeKind.UNKNOWN:
            if op.operator == "!":
                return SemanticType(TypeKind.BOOL)
            if op.operator == "&":
                return SemanticType(TypeKind.POINTER, element_type=operand_type)
            return operand_type

        if op.operator == "-":
            # Negating a unit-typed quantity keeps its dimension.
            if self._dims_of(operand_type) is not None:
                return operand_type
            # Dual unary minus (#161).
            if self._is_dual(operand_type):
                return operand_type
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

    # Transcendental functions take dimensionless arguments. `Radian` is the
    # one unit allowed through: angles erase to dimensionless at these
    # boundaries (north-star.md 6.2).
    DIMENSIONLESS_MATH = {
        "sin", "cos", "tan", "asin", "acos", "atan", "atan2",
        "sinh", "cosh", "tanh", "exp", "log", "log2", "log10",
    }

    def _effect_name_for_method_receiver(self, receiver: Any) -> Optional[str]:
        """Return the effect name for `Effect.op()` or `capability.op()` calls."""
        if not isinstance(receiver, Variable):
            return None
        if receiver.name in self.effect_types:
            return receiver.name
        symbol = self.current_scope.lookup(receiver.name)
        if symbol and symbol.type.name.startswith("capability_"):
            return symbol.type.name[len("capability_"):]
        if symbol and symbol.type.name in self.effect_types:
            return symbol.type.name
        return None

    def _struct_name_for_method_receiver(self, receiver_type: SemanticType) -> Optional[str]:
        if receiver_type.kind == TypeKind.STRUCT:
            return receiver_type.name
        if receiver_type.kind == TypeKind.POINTER and receiver_type.element_type:
            if receiver_type.element_type.kind == TypeKind.STRUCT:
                return receiver_type.element_type.name
        return None

    def _impl_method_for_receiver(self, receiver_type: SemanticType, method: str) -> Optional[str]:
        struct_name = self._struct_name_for_method_receiver(receiver_type)
        if not struct_name:
            return None

        candidates = self.impl_methods.get((struct_name, method), [])
        if len(candidates) == 1:
            return candidates[0]
        if len(candidates) > 1:
            self.errors.append(
                f"Ambiguous method '{method}' for type '{struct_name}' "
                f"({', '.join(candidates)})"
            )
        return None

    def _check_effect_call(self, call: EffectCall) -> SemanticType:
        """Type check an algebraic effect operation call."""
        effect = self.effect_types.get(call.effect_name)
        if effect is None:
            for arg in call.arguments:
                self._check_expression(arg)
            if self.strict:
                self.errors.append(f"Unknown effect '{call.effect_name}'")
            return SemanticType(TypeKind.UNKNOWN)

        operation = None
        for candidate in effect.operations:
            if candidate.name == call.operation:
                operation = candidate
                break

        if operation is None:
            for arg in call.arguments:
                self._check_expression(arg)
            if self.strict:
                self.errors.append(
                    f"Effect '{call.effect_name}' has no operation '{call.operation}'"
                )
            return SemanticType(TypeKind.UNKNOWN)

        arg_types = [self._check_expression(arg) for arg in call.arguments]
        param_types = [self._parse_type(param.type) for param in operation.parameters]
        if len(arg_types) != len(param_types):
            if self.strict:
                self.errors.append(
                    f"Effect operation '{call.effect_name}.{call.operation}' expects "
                    f"{len(param_types)} argument(s), got {len(arg_types)}"
                )
            return self._parse_type(operation.return_type)

        for idx, (actual, expected) in enumerate(zip(arg_types, param_types), start=1):
            if not self._can_coerce(actual, expected):
                self.errors.append(
                    f"Effect operation '{call.effect_name}.{call.operation}' argument "
                    f"{idx} expects {expected}, got {actual}"
                )

        return self._parse_type(operation.return_type)

    def _check_function_call(self, call: FunctionCall) -> SemanticType:
        """Type check a function call."""
        self._check_rt_safe_call(call.name)
        # dbg expr: evaluates to expr, so its type is the operand's type.
        if call.name == "__flow_dbg":
            if len(call.arguments) != 1:
                if self.strict:
                    self.errors.append("dbg requires exactly one argument")
                return SemanticType(TypeKind.VOID)
            return self._check_expression(call.arguments[0])
        if call.name in self.DIMENSIONLESS_MATH and call.arguments:
            arg_types = [self._check_expression(arg) for arg in call.arguments]
            if any(self._dims_of(t) is not None for t in arg_types):
                for arg_type in arg_types:
                    arg_dims = self._dims_of(arg_type)
                    if arg_dims is None or arg_type.name == "Radian":
                        continue
                    self.errors.append(
                        f"dimensional error: {call.name}() requires a "
                        f"dimensionless or Radian argument, got {arg_type}"
                    )
                return SemanticType(TypeKind.F64)
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
                if self.strict:
                    self.errors.append(f"Undefined function '{call.name}'")
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
        self._ensure_generic_struct_instance(struct_name)
        if struct_name not in self.struct_types:
            return SemanticType(TypeKind.STRUCT, name=struct_name)

        struct_def = self.struct_types[struct_name]
        expected_fields = {field.name: self._parse_type(field.type) for field in struct_def.fields}

        # Check that all required fields are present and types match
        # struct_lit.fields is List[tuple] where each tuple is (field_name, field_value)
        provided_fields = {}
        for field_item in struct_lit.fields:
            if isinstance(field_item, tuple) and len(field_item) == 2:
                field_name, field_value = field_item
                provided_fields[field_name] = self._check_expression(field_value)
            elif hasattr(field_item, 'name') and hasattr(field_item, 'value'):
                provided_fields[field_item.name] = self._check_expression(field_item.value)

        for field_name, expected_type in expected_fields.items():
            if field_name not in provided_fields:
                self.errors.append(f"Struct '{struct_name}' missing field '{field_name}'")
            elif not self._can_coerce(provided_fields[field_name], expected_type):
                self.errors.append(
                    f"Struct '{struct_name}' field '{field_name}' expects {expected_type}, got {provided_fields[field_name]}"
                )

        return SemanticType(TypeKind.STRUCT, name=struct_name)

    def _check_record_update(self, update: "RecordUpdate") -> SemanticType:
        """Type check a record update: `Point { ..p, x: 3 }`.

        The result type matches the base struct; each override field is
        checked against that struct's field type and must exist.
        """
        base_type = self._check_expression(update.base)
        struct_name = base_type.name if hasattr(base_type, "name") else None
        if struct_name is None or struct_name not in self.struct_types:
            if self.strict:
                self.errors.append(
                    f"record update base must be a struct, got {struct_name or base_type}"
                )
            return SemanticType(TypeKind.STRUCT, name=struct_name or "")
        struct_def = self.struct_types[struct_name]
        expected_fields = {f.name: self._parse_type(f.type) for f in struct_def.fields}
        for field_name, field_value in update.updates:
            if field_name not in expected_fields:
                self.errors.append(
                    f"record update: struct '{struct_name}' has no field '{field_name}'"
                )
                expected = SemanticType(TypeKind.UNKNOWN)
            else:
                expected = expected_fields[field_name]
            actual = self._check_expression(field_value)
            if not self._can_coerce(actual, expected):
                self.errors.append(
                    f"record update: field '{field_name}' expects {expected}, got {actual}"
                )
        return SemanticType(TypeKind.STRUCT, name=struct_name)

    def _is_compatible(self, actual: SemanticType, expected: SemanticType) -> bool:
        """Check if actual type is compatible with expected type."""
        if actual == expected:
            return True

        # Unit types: dimension vectors decide compatibility.
        actual_dims = self._dims_of(actual)
        expected_dims = self._dims_of(expected)
        if actual_dims is not None and expected_dims is not None:
            return actual_dims == expected_dims
        if actual_dims is not None or expected_dims is not None:
            return False

        # Capability compatibility: allow any struct to satisfy a capability type.
        if expected.kind == TypeKind.STRUCT and expected.name.startswith("capability_"):
            if actual.kind == TypeKind.STRUCT:
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

        # Struct-to-pointer method sugar: `reader.load_file()` desugars to
        # `load_file(reader, ...)`, and the C backend passes `&reader` when
        # the selected overload expects `ptr<Reader>`.
        if actual.kind == TypeKind.STRUCT and expected.kind == TypeKind.POINTER:
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

    def _generic_type_args_from_name(self, name: str) -> Optional[Tuple[str, List[ParsedType]]]:
        if "_" not in name:
            return None
        base_name = name.split("_", 1)[0]
        generic = self.generic_struct_types.get(base_name)
        if generic is None:
            return None

        suffix = name[len(base_name) + 1:]
        parts = suffix.split("_")
        type_param_count = len(generic.type_params)
        if len(parts) < type_param_count:
            return None
        return base_name, [ParsedType(part) for part in parts[:type_param_count]]

    def _substitute_parsed_type(
        self, parsed_type: ParsedType, type_map: Dict[str, ParsedType]
    ) -> ParsedType:
        if parsed_type.name in type_map and not parsed_type.type_args:
            replacement = type_map[parsed_type.name]
            return ParsedType(
                replacement.name,
                is_pointer=replacement.is_pointer,
                is_reference=replacement.is_reference,
                is_capability=getattr(replacement, "is_capability", False),
                size=replacement.size,
                element_type=replacement.element_type,
                type_args=replacement.type_args,
            )

        element_type = (
            self._substitute_parsed_type(parsed_type.element_type, type_map)
            if parsed_type.element_type
            else None
        )
        type_args = (
            [self._substitute_parsed_type(arg, type_map) for arg in parsed_type.type_args]
            if parsed_type.type_args
            else None
        )
        return ParsedType(
            parsed_type.name,
            is_pointer=parsed_type.is_pointer,
            is_reference=parsed_type.is_reference,
            is_capability=getattr(parsed_type, "is_capability", False),
            size=parsed_type.size,
            element_type=element_type,
            type_args=type_args,
        )

    def _ensure_generic_struct_instance(
        self, name: str, type_args: Optional[List[ParsedType]] = None
    ) -> bool:
        if name in self.struct_types:
            return True

        base_name = name.split("_", 1)[0]
        generic = self.generic_struct_types.get(base_name)
        if generic is None:
            parsed = self._generic_type_args_from_name(name)
            if parsed is None:
                return False
            base_name, type_args = parsed
            generic = self.generic_struct_types.get(base_name)
        elif type_args is None:
            parsed = self._generic_type_args_from_name(name)
            if parsed is None:
                return False
            _, type_args = parsed

        if not type_args or len(type_args) != len(generic.type_params):
            return False

        type_map = {
            param.name: arg for param, arg in zip(generic.type_params, type_args)
        }
        fields = [
            Parameter(field.name, self._substitute_parsed_type(field.type, type_map))
            for field in generic.fields
        ]
        self.struct_types[name] = StructDecl(
            name,
            fields,
            getattr(generic, "is_exported", False),
            [],
            getattr(generic, "location", None),
        )
        return True

    def _parse_type(self, parsed_type: ParsedType) -> SemanticType:
        """Convert a parsed Type to a SemanticType."""
        if parsed_type.name == "auto":
            return SemanticType(TypeKind.UNKNOWN, name="auto")
        if parsed_type.type_args:
            base_name = parsed_type.name.split("_", 1)[0]
            if base_name in self.generic_struct_types:
                self._ensure_generic_struct_instance(parsed_type.name, parsed_type.type_args)
                return SemanticType(TypeKind.STRUCT, name=parsed_type.name)
        if parsed_type.name not in self.struct_types:
            if self._ensure_generic_struct_instance(parsed_type.name):
                return SemanticType(TypeKind.STRUCT, name=parsed_type.name)
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
        elif parsed_type.name.startswith("capability_"):
            # Treat capabilities as opaque structs for type compatibility
            return SemanticType(TypeKind.STRUCT, name=parsed_type.name)
        elif parsed_type.is_pointer and parsed_type.element_type:
            return SemanticType(TypeKind.POINTER, element_type=self._parse_type(parsed_type.element_type))
        elif parsed_type.name.startswith("array_") and parsed_type.element_type:
            return SemanticType(TypeKind.ARRAY, element_type=self._parse_type(parsed_type.element_type), size=parsed_type.size)
        elif parsed_type.name.startswith("array_"):
            elem_name = parsed_type.name[len("array_"):]
            elem_type = self._parse_named_scalar(elem_name)
            if elem_type:
                return SemanticType(TypeKind.ARRAY, element_type=elem_type, size=parsed_type.size)
        elif parsed_type.name.startswith("memref_"):
            element_name = parsed_type.name[len("memref_"):]
            element_type = self._parse_type(ParsedType(element_name))
            return SemanticType(TypeKind.POINTER, element_type=element_type)
        elif parsed_type.name in self.struct_types:
            decl = self.struct_types[parsed_type.name]
            if isinstance(decl, TypeAliasDecl):
                # Type aliases are transparent - return the base type
                base_type = self._parse_type(decl.base_type)
                return SemanticType(
                    kind=TypeKind.TYPE_ALIAS,
                    name=parsed_type.name,
                    base_type=base_type
                )
            elif isinstance(decl, DistinctTypeDecl):
                # Distinct types are opaque - return distinct type with base type reference
                base_type = self._parse_type(decl.base_type)
                return SemanticType(
                    kind=TypeKind.DISTINCT,
                    name=parsed_type.name,
                    base_type=base_type,
                    dims=self.unit_dims.get(parsed_type.name)
                )
            else:
                # Regular struct
                return SemanticType(TypeKind.STRUCT, name=parsed_type.name)
        else:
            # Unknown type (e.g., generic parameter)
            return SemanticType(TypeKind.UNKNOWN, name=parsed_type.name)
