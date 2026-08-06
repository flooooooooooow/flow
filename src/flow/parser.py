#!/usr/bin/env python3
"""
FLOW Language Parser
A simple recursive descent parser for the FLOW language
"""

import re
from fractions import Fraction
from typing import List, Optional, Union, Any, Tuple, Dict
from dataclasses import dataclass, field
from enum import Enum

# Time-unit suffixes for duration literals (docs/vision/north-star.md 4.1),
# mapped to nanoseconds per unit. Recognized only in duration positions
# (`every`, `solver dt`), so each word stays a legal identifier elsewhere.
DURATION_UNIT_NS = {
    "ns": 1,
    "us": 1_000,
    "ms": 1_000_000,
    "s": 1_000_000_000,
    "min": 60_000_000_000,
}


class FlowSyntaxError(SyntaxError):
    """Enhanced syntax error with source context and suggestions."""

    def __init__(
        self,
        message: str,
        line: int = None,
        column: int = None,
        source: str = None,
        suggestion: str = None,
    ):
        self.line = line
        self.column = column
        self.source = source
        self.suggestion = suggestion

        # Build detailed message
        parts = [f"Error: {message}"]

        if line is not None:
            parts[0] += f" at line {line}"
            if column is not None:
                parts[0] += f", column {column}"

        # Add source context if available
        if source and line:
            lines = source.split("\n")
            if 0 < line <= len(lines):
                src_line = lines[line - 1]
                parts.append(f"\n  {line:4d} | {src_line}")
                if column:
                    parts.append(f"       | {' ' * (column - 1)}^")

        # Add suggestion if available
        if suggestion:
            parts.append(f"\n  Hint: {suggestion}")

        super().__init__("\n".join(parts))


# Common error suggestions
ERROR_SUGGESTIONS = {
    "Expected TokenType.RBRACE": "Missing closing brace '}'. Check for unbalanced braces.",
    "Expected TokenType.RPAREN": "Missing closing parenthesis ')'. Check function calls and expressions.",
    "Expected TokenType.SEMICOLON": "Semicolons are optional in FLOW. If you see this error, there may be a syntax issue before this point.",
    "Expected TokenType.IDENTIFIER": "Expected a name (identifier) here. Names must start with a letter or underscore.",
    "Unexpected token in expression": "This token cannot start an expression. Check for typos or missing operators.",
    "Unexpected declaration": "This keyword cannot appear at the top level. Check for missing braces or incorrect nesting.",
}


def get_suggestion(error_msg: str) -> Optional[str]:
    """Get a helpful suggestion based on the error message."""
    for pattern, suggestion in ERROR_SUGGESTIONS.items():
        if pattern in error_msg:
            return suggestion
    return None


class TokenType(Enum):
    # Literals
    NUMBER = "NUMBER"
    IDENTIFIER = "IDENTIFIER"
    BOOLEAN = "BOOLEAN"

    # Keywords
    FUNCTION = "FUNCTION"
    LET = "LET"
    MUT = "MUT"  # mutable variable modifier
    RETURN = "RETURN"
    IF = "IF"
    ELSE = "ELSE"
    ELIF = "ELIF"
    WHILE = "WHILE"
    FOR = "FOR"
    BREAK = "BREAK"
    CONTINUE = "CONTINUE"
    PARALLEL = "PARALLEL"
    IN = "IN"
    STEP = "STEP"
    IMPORT = "IMPORT"
    EXPORT = "EXPORT"
    EXTERN = "EXTERN"
    CONST = "CONST"
    MODULE = "MODULE"
    STRUCT = "STRUCT"
    INLINE = "INLINE"
    NOINLINE = "NOINLINE"
    ALWAYS_INLINE = "ALWAYS_INLINE"
    TARGET = "TARGET"
    EFFECT = "EFFECT"
    CAPABILITY = "CAPABILITY"
    HANDLE = "HANDLE"
    WITH = "WITH"
    MATCH = "MATCH"
    DEFAULT = "DEFAULT"
    TEST = "TEST"
    TRAIT = "TRAIT"
    IMPL = "IMPL"
    SELF = "SELF"
    TYPE = "TYPE"
    DISTINCT = "DISTINCT"
    AS = "AS"
    UI_LAYOUT = "UI_LAYOUT"
    UI_ROW = "UI_ROW"
    UI_COLUMN = "UI_COLUMN"
    UI_STACK = "UI_STACK"
    UI_GRID = "UI_GRID"
    ENUM = "ENUM"
    THEOREM = "THEOREM"
    ASSUME = "ASSUME"
    THEREFORE = "THEREFORE"
    CLAIM_PATH = "CLAIM_PATH"
    CLAIM_COORDINATE = "CLAIM_COORDINATE"

    # Types
    I8 = "I8"
    I16 = "I16"
    I32 = "I32"
    I64 = "I64"
    I128 = "I128"
    U8 = "U8"
    U16 = "U16"
    U32 = "U32"
    U64 = "U64"
    U128 = "U128"
    F32 = "F32"
    F64 = "F64"
    BOOL = "BOOL"
    VOID = "VOID"
    STRING_TYPE = "STRING_TYPE"  # The 'string' type keyword
    STRING_LITERAL = "STRING_LITERAL"  # "hello" string literals
    VEC = "VEC"
    NULL = "NULL"  # null pointer literal
    DEFER = "DEFER"
    QUESTION = "QUESTION"  # ? operator for Result propagation
    DBG = "DBG"  # dbg tracing keyword: dbg expr evaluates to expr, prints it
    EXPECT = "EXPECT"  # Runtime assertion: expect <expr>

    # Symbols
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    LBRACE = "LBRACE"
    RBRACE = "RBRACE"
    LBRACKET = "LBRACKET"
    RBRACKET = "RBRACKET"
    SEMICOLON = "SEMICOLON"
    COLON = "COLON"
    COMMA = "COMMA"
    DOTDOT = "DOTDOT"
    DOT = "DOT"
    ARROW = "ARROW"
    ASSIGN = "ASSIGN"
    PLUS_ASSIGN = "PLUS_ASSIGN"  # +=
    MINUS_ASSIGN = "MINUS_ASSIGN"  # -=
    STAR_ASSIGN = "STAR_ASSIGN"  # *=
    SLASH_ASSIGN = "SLASH_ASSIGN"  # /=
    DOUBLE_COLON = "DOUBLE_COLON"
    FAT_ARROW = "FAT_ARROW"

    # Operators
    PLUS = "PLUS"
    MINUS = "MINUS"
    STAR = "STAR"
    SLASH = "SLASH"
    PERCENT = "PERCENT"
    PIPE = "PIPE"  # For lambdas: |x| { ... } and bitwise OR
    PIPELINE = "PIPELINE"  # For pipeline chaining: x |> f(y)
    AMPERSAND = "AMPERSAND"  # For bitwise AND
    CARET = "CARET"  # For bitwise XOR
    TILDE = "TILDE"  # For bitwise NOT
    LSHIFT = "LSHIFT"  # For left shift <<
    RSHIFT = "RSHIFT"  # For right shift >>
    EQUALS = "EQUALS"
    NOT_EQUALS = "NOT_EQUALS"
    LESS = "LESS"
    GREATER = "GREATER"
    LESS_EQUAL = "LESS_EQUAL"
    GREATER_EQUAL = "GREATER_EQUAL"
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    TO = "TO"

    # Special
    NEWLINE = "NEWLINE"
    COMMENT = "COMMENT"
    EOF = "EOF"
    AT = "AT"  # @ for decorators like @gpu


@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int


@dataclass
class SourceLocation:
    """Source code location for LSP features."""

    line: int  # 0-based line number
    column: int  # 0-based column number
    end_line: Optional[int] = None
    end_column: Optional[int] = None


@dataclass
class Type:
    name: str
    is_pointer: bool = False
    is_reference: bool = False
    is_capability: bool = False
    size: Optional[int] = None
    element_type: Optional["Type"] = None
    type_args: Optional[List["Type"]] = None  # Generic type arguments
    # Effect-row on first-class function types: `(i32) -> i32 with Log`
    effects: List[str] = field(default_factory=list)


# --- Spans (docs/language/spans.md) -----------------------------------------
# A span is a borrowed view over contiguous storage: {pointer, length}. Both
# spellings (`span<T>` and the `&[T]` sugar) desugar to one internal Type so
# every downstream pass sees a single representation.
SPAN_CONST_PREFIX = "span_const_"
SPAN_MUT_PREFIX = "span_mut_"


def make_span_type(element_type: "Type", is_mut: bool, extent: Optional[int] = None) -> "Type":
    """Build the canonical span Type for an element type and mutability."""
    prefix = SPAN_MUT_PREFIX if is_mut else SPAN_CONST_PREFIX
    return Type(
        f"{prefix}{element_type.name}",
        size=extent,
        element_type=element_type,
    )


def is_span_type_name(name: str) -> bool:
    return bool(name) and (
        name.startswith(SPAN_CONST_PREFIX) or name.startswith(SPAN_MUT_PREFIX)
    )


def span_is_mutable(name: str) -> bool:
    return bool(name) and name.startswith(SPAN_MUT_PREFIX)


def span_element_name(name: str) -> str:
    if name.startswith(SPAN_MUT_PREFIX):
        return name[len(SPAN_MUT_PREFIX):]
    if name.startswith(SPAN_CONST_PREFIX):
        return name[len(SPAN_CONST_PREFIX):]
    return name


def format_span_type(name: str, extent: Optional[int] = None) -> str:
    """Render a span type name back into source syntax for diagnostics."""
    inner = span_element_name(name)
    if span_is_mutable(name):
        inner = f"mut {inner}"
    if extent is not None:
        inner = f"{inner}, {extent}"
    return f"span<{inner}>"


@dataclass
class TypeParameter:
    """A generic type parameter with optional trait bound: T or T: Display"""

    name: str
    bound: Optional[str] = None  # Trait bound, e.g., "Display"


@dataclass
class Parameter:
    name: str
    type: Type


@dataclass
class FunctionDecl:
    name: str
    parameters: List[Parameter]
    return_type: Type
    body: "Block"
    attributes: List[str]
    is_exported: bool = False
    is_extern: bool = False
    type_params: List["TypeParameter"] = field(
        default_factory=list
    )  # Generic type parameters like <T, U>
    has_self: bool = False  # Whether this is a method with self parameter
    location: Optional[SourceLocation] = None  # For LSP go-to-definition
    # Effect-row Phase 2: `function f() -> T with Log, Inventory { … }`
    # Declares effects this function may perform; callers must handle them
    # (or declare them too) when `--strict-effects` / check_effect_rows is on.
    effects: List[str] = field(default_factory=list)


@dataclass
class VarDecl:
    name: str
    type: Type
    initializer: Optional["Expression"]
    is_mutable: bool = False  # True if declared with 'let mut'


@dataclass
class Block:
    statements: List["Statement"]


@dataclass
class IfStatement:
    condition: "Expression"
    then_block: Block
    elif_blocks: List[Tuple["Expression", Block]]
    else_block: Optional[Block]


@dataclass
class WhileStatement:
    condition: "Expression"
    body: Block


@dataclass
class ForStatement:
    variable: str
    range_start: "Expression"
    range_end: "Expression"
    step: Optional["Expression"]
    body: Block
    is_parallel: bool


@dataclass
class ReturnStatement:
    value: Optional["Expression"]


@dataclass
class Assignment:
    target: str  # Simple variable name, or None if target_expr is used
    value: "Expression"
    target_expr: Optional["Expression"] = None  # For array access like arr[i] = value


@dataclass
class FunctionCall:
    name: str
    arguments: List["Expression"]


@dataclass
class Lambda:
    """Lambda/closure expression: |x: i32, y: i32| -> i32 { x + y }"""

    parameters: List[Parameter]
    return_type: Optional[Type]
    body: Union["Block", "Expression"]  # Can be block or single expression
    captures: List[str] = field(
        default_factory=list
    )  # Captured variables (for analysis)


@dataclass
class StringInterpolation:
    """Interpolated string literal: `"Hello ${name}!"`.

    `parts` alternates between literal text (as `Literal` of type `string`)
    and interpolated `Expression` nodes (which are stringified at codegen).
    """

    parts: List["Expression"]


@dataclass
class BinaryOperation:
    left: "Expression"
    operator: str
    right: "Expression"
    line: int = 0  # Source line of the operator token (0 when unknown)


@dataclass
class UnaryOperation:
    operator: str
    operand: "Expression"


@dataclass
class Literal:
    value: str
    type: Type


@dataclass
class Variable:
    name: str


@dataclass
class StructLiteral:
    struct_name: str
    fields: List[tuple]  # List of (field_name, field_value)


@dataclass
class ForkSource:
    """Placeholder for a fork block's piped value inside a branch template.

    A fork branch is parsed as a pipeline whose head is this node; the fork
    desugaring substitutes the real source (or a hoisted temp binding it) for
    every `ForkSource` before the fork is lowered.
    """


@dataclass
class ForkBlock:
    """A fork block: `source |> [Record] { a = pipeline, ... }`.

    Each branch value is a template pipeline over `ForkSource` (e.g.
    `magnitude(fft(ForkSource()))`). `record_name` is the named record, or
    None for the anonymous inferred form. `desugar_forks` (a post-parse pass)
    binds `source` once when it is non-trivial, substitutes it into the
    branches, infers a record type for the anonymous form, and rewrites this
    into a `StructLiteral`. The node never survives `parse()`, so no later
    phase — type checker, backends, tooling — needs to know about it.
    """

    record_name: Optional[str]
    source: "Expression"
    branches: List[tuple]  # List of (field_name, template over ForkSource)
    line: int = 0


@dataclass
class FlowStage:
    """A flow used as a pipeline stage with parameter overrides.

    `source |> Gain { k: 3.0 }` parses to this (the `:` delimiter, versus a
    fork block's `=`). It is resolved only inside a flow `output` pipeline, by
    `_expand_flow_pipelines`, into a child instance whose params are set after
    init. A `FlowStage` that survives flow expansion (i.e. used outside a flow
    stage pipeline) is a compile error.
    """

    name: str
    arg: "Expression"
    params: List[tuple]  # List of (param_name, value)
    line: int = 0


@dataclass
class ChooseBlock:
    """A state-driven pipeline stage: `source |> choose sel { A => f, B => g }`.

    Selects which stage pipeline runs based on `selector` (typically an enum
    state). Each arm value is a template pipeline over `ForkSource` (the piped
    value). `desugar_forks` binds `source` once, infers the result type from the
    arms, and lowers this to a hoisted `let mut __choose_N` plus a `match`
    statement that assigns the chosen arm — so no value-form `match` is needed
    and no later phase sees this node.
    """

    selector: "Expression"
    source: "Expression"
    arms: List[tuple]  # List of (pattern, template over ForkSource)
    line: int = 0


@dataclass
class RecordUpdate:
    """Record update: `Point { ..p, x: 3 }` copies `p` then overrides `x`.

    `base` is the struct expression whose fields are copied; `updates` is the
    list of (field_name, field_value) overrides. The full field list of the
    struct is filled in at codegen time from the struct declaration.
    """

    base: "Expression"
    updates: List[tuple]  # List of (field_name, field_value)


@dataclass
class FieldAccess:
    object: "Expression"
    field: str


@dataclass
class SortKey:
    """One ordering key: `asc .score` / `desc .name` / bare `.id` (asc).

    `field` is None when sorting primitive elements (whole value).
    """

    field: Optional[str]
    descending: bool = False


@dataclass
class SortExpr:
    """Declarative ordering: `xs |> sort by [desc .p, asc .t] stable`.

    Phase 1 of the Ordering & Entropy PRD. Policies like `parallel` / `gpu`
    and `with entropy` are parsed for forward compatibility; the C backend
    currently lowers to a stable insertion sort.
    """

    array: "Expression"
    keys: List[SortKey] = field(default_factory=list)
    descending: bool = False  # whole-sort reverse (`sort descending`)
    stable: bool = True
    unique: bool = False
    # Forward-compat policy flags (accepted, not yet specialized in codegen)
    parallel: bool = False
    adaptive: bool = False
    compact: bool = False
    policies: List[str] = field(default_factory=list)
    entropy: Optional[str] = None  # None | "default" | "system" | "fast" | "secure" | "record" | seed int as str
    general: bool = False  # `general`: pin the general plan, ignore hints
    line: int = 0
    # Written by the ordering-hints pass (src/flow/ordering_hints.py).
    hint_input_order: str = "unknown"
    hint_key_range: Optional[List[int]] = None


@dataclass
class FindExpr:
    """Declarative search: `xs |> find(target)`.

    Yields the index of the first element that compares equal to `target`
    under the same total order `sort` uses, or -1 when there is none. The
    compiler picks the search implementation: a linear scan in general, a
    lower-bound binary search when ordering provenance proves the array is
    ascending. See docs/language/ordering.md.
    """

    array: "Expression"
    target: "Expression"
    line: int = 0
    hint_input_order: str = "unknown"
    hint_key_range: Optional[List[int]] = None


@dataclass
class ArrayLiteral:
    elements: List["Expression"]


@dataclass
class VectorLiteral:
    elements: List["Expression"]


@dataclass
class ArrayAccess:
    array: "Expression"
    index: "Expression"


@dataclass
class SliceExpr:
    """`base[start..end]` — a borrowed view (span) over contiguous storage.

    See docs/language/spans.md. `start`/`end` are ordinary expressions; when
    both are integer literals the extent is a compile-time fact.
    """

    base: "Expression"
    start: "Expression"
    end: "Expression"


@dataclass
class StructDecl:
    name: str
    fields: List[Parameter]
    is_exported: bool = False
    type_params: List["TypeParameter"] = field(
        default_factory=list
    )  # Generic type parameters like <T, U>
    location: Optional[SourceLocation] = None  # For LSP


@dataclass
class EnumVariant:
    """A variant of an enum: Some(T), None, Ok(T), Err(E)"""

    name: str
    fields: List[Type] = field(
        default_factory=list
    )  # Empty for unit variants, types for tuple variants


@dataclass
class EnumDecl:
    """Enum declaration: enum Option<T> { Some(T), None }"""

    name: str
    variants: List[EnumVariant]
    is_exported: bool = False
    type_params: List["TypeParameter"] = field(default_factory=list)


@dataclass
class TraitMethod:
    """A method signature in a trait (no body)."""

    name: str
    parameters: List[Parameter]
    return_type: Type
    has_self: bool = False  # Whether first param is self


@dataclass
class TraitDecl:
    """Trait declaration: trait Printable { function to_string(self) -> string }"""

    name: str
    methods: List[TraitMethod]
    type_params: List["TypeParameter"] = field(default_factory=list)


@dataclass
class ImplDecl:
    """Implementation block: impl Trait for Type { ... }"""

    trait_name: str
    for_type: Type
    methods: List["FunctionDecl"]


@dataclass
class EffectDecl:
    name: str
    operations: List["EffectOperation"]


@dataclass
class EffectOperation:
    name: str
    parameters: List[Parameter]
    return_type: Type


@dataclass
class CapabilityDecl:
    name: str
    effects: List[str]  # Names of effects this capability provides
    methods: List["CapabilityMethod"]


@dataclass
class CapabilityMethod:
    name: str
    parameters: List[Parameter]
    return_type: Type
    body: Block


@dataclass
class EffectCall:
    effect_name: str
    operation: str
    arguments: List["Expression"]


@dataclass
class MethodCall:
    object: "Expression"
    method: str
    arguments: List["Expression"]


@dataclass
class HandleStatement:
    effects: List[str]
    handlers: List[str]  # Names of capabilities or functions
    body: Block


@dataclass
class LayoutStatement:
    kind: str
    args: List["Expression"]
    body: Block


@dataclass
class MatchStatement:
    value: "Expression"
    cases: List["MatchCase"]
    default_case: Optional[Block]


@dataclass
class MatchCase:
    pattern: "Expression"  # Could be literal, struct pattern, etc.
    body: Block
    guard: Optional["Expression"] = None  # Optional: pattern if guard => body


@dataclass
class StructPattern:
    struct_name: str
    bindings: List[str]  # List of variable names to bind fields to ("_" = no binding)
    # Nested/refined patterns: positional index -> literal the field must equal.
    # Positions present here have "_" at the same index in `bindings` (no bind,
    # just a value check), e.g. `Point(0, y)` requires field 0 == 0 and binds y.
    field_literals: Optional[Dict[int, "Literal"]] = None
    # Struct-in-struct nesting: positional index -> nested StructPattern the
    # field must recursively match, e.g. `Outer(Inner(x), y)` requires field 0
    # to match the nested pattern `Inner(x)` (binding `x` from the inner
    # struct's own field 0) and binds field 1 to `y`. Positions present here
    # also have "_" at the same index in `bindings`.
    field_patterns: Optional[Dict[int, "StructPattern"]] = None


@dataclass
class ListPattern:
    """A match pattern for arrays: `[]`, `[x]`, `[a, b]`, `[_, 5]`.

    `elements` holds one entry per array slot. A `Variable` entry binds that
    slot to a name (unless the name is `_`, which means no binding); a
    `Literal` entry requires the slot to equal that literal.
    """

    elements: List["Expression"]


@dataclass
class OrPattern:
    """Multiple alternative patterns for one match arm: `1 | 2 | 3 => ...`
    or `Point(0, y) | Point(1, y) => ...`.

    Alternatives are either all literals (no bindings) or all struct
    patterns whose flattened binding names agree across every alternative
    (same names in the same order). Mixing literals with structs, or
    disagreeing binding names, is a syntax error.
    """

    patterns: List["Expression"]


@dataclass
class CastExpression:
    expr: "Expression"
    target_type: Type


@dataclass
class TryExpr:
    """Result propagation: expr? returns value or early-returns the Err."""

    operand: "Expression"


@dataclass
class DeferStatement:
    """Deferred cleanup: defer expr; runs at scope exit (LIFO)."""

    expr: "Expression"


@dataclass
class BreakStatement:
    """`break`; exits the nearest enclosing `while`/`for` loop."""

    line: int = 0


@dataclass
class ContinueStatement:
    """`continue`; skips to the next iteration of the nearest enclosing loop."""

    line: int = 0


@dataclass
class ExpectStatement:
    """Runtime assertion: `expect <expr>`; aborts with an error if false.

    Mirrors Roc's `expect` keyword: the condition is checked at runtime and a
    failure is a hard error (Roc fails compilation; Flow, being a runtime
    systems language, aborts the program with a diagnostic).
    """

    condition: "Expression"
    line: int = 0


@dataclass
class ModuleDecl:
    """Namespace module: module name { declarations... }"""

    name: str
    declarations: List[Any]
    is_exported: bool = False


@dataclass
class ImportDecl:
    """Module import — dot paths (verify.nat) or legacy string paths.

    `is_reexport` marks `export import ...`: the imported module's exported
    symbols (all of them, or the brace-list selection) become exports of the
    importing file too. See docs/language/modules.md.
    """

    path: str
    symbols: Optional[List[str]] = None
    alias: Optional[str] = None
    is_legacy_string: bool = False
    is_reexport: bool = False


@dataclass
class ExportDecl:
    """File-level export list: export foo, bar"""

    symbols: List[str] = field(default_factory=list)


@dataclass
class TheoremDecl:
    """Verified claim at a Claim Path — same shape as function, different keyword."""

    claim_path: str
    parameters: List[Parameter]
    body: "Block"
    is_exported: bool = False


@dataclass
class AssumeStmt:
    """Invoke a prior claim (definition, axiom, or derived fact)."""

    claim_path: str
    arguments: List["Expression"] = field(default_factory=list)


@dataclass
class ThereforeStmt:
    """Conclusion the checker must verify."""

    expression: "Expression"
    method: Optional[str] = None


@dataclass
class ConstDecl:
    name: str
    type: Type
    value: "Expression"
    is_exported: bool = False


@dataclass
class StaticDecl:
    """Module-level mutable state: top-level `let mut name: Type = value`.

    Lowers to a file-scope C `static`, so the variable is private to its
    translation unit. The type annotation is required and the initializer
    must be a compile-time constant (checked in the type checker).
    """

    name: str
    type: Type
    value: "Expression"


@dataclass
class TestDecl:
    name: str
    body: Block


@dataclass
class TypeAliasDecl:
    """Type alias declaration: type Name = BaseType
    Type aliases are transparent - they're just alternate names for existing types.
    """
    name: str
    base_type: Type
    is_exported: bool = False


@dataclass
class DistinctTypeDecl:
    """Distinct type declaration: distinct type Name = BaseType
    Distinct types are opaque - they're incompatible with their base type and each other.
    Similar to Odin's distinct types or Ada's derived types.
    """
    name: str
    base_type: Type
    is_exported: bool = False


@dataclass
class UnitDecl(DistinctTypeDecl):
    """Unit of measure declaration (docs/vision/north-star.md section 6):

        unit Meter                      # new base dimension
        unit Velocity = Meter / Second  # derived unit

    A unit behaves exactly like `distinct type Name = f64` plus a dimension
    exponent vector, so every downstream phase (codegen, module resolution)
    treats it as a distinct type and erases it to its base numeric type.

    `factors` is None for a base dimension. For a derived unit it is the
    flattened right-hand side as (unit name, exponent) pairs; a factor after
    `/` carries a negated exponent. The literal `1` contributes no factors.
    """

    factors: Optional[List[Tuple[str, int]]] = None
    line: int = 0


@dataclass
class FlowStateDecl:
    """`state x : type = init` inside a `flow` block (docs/vision/north-star.md 1.1)."""

    name: str
    type: Type
    initializer: Optional["Expression"]
    line: int = 0


@dataclass
class FlowParamDecl:
    """`param k : type = init` inside a `flow` block. Constant per instance."""

    name: str
    type: Type
    initializer: Optional["Expression"]
    line: int = 0


@dataclass
class FlowInputDecl:
    """`input u : type` inside a `flow` block. Written by the embedder before a step."""

    name: str
    type: Type
    line: int = 0


@dataclass
class FlowOutputDecl:
    """`output y : type = expr` inside a `flow` block. Computed after integration."""

    name: str
    type: Type
    expr: Optional["Expression"]
    line: int = 0


@dataclass
class FlowEvolveDecl:
    """`x evolves as expr`: declares dx/dt = expr for state x."""

    target: str
    expr: "Expression"
    line: int = 0


@dataclass
class FlowBecomesDecl:
    """`x becomes expr` inside a `when` body: a staged discrete reset.

    All `becomes` right-hand sides in one fired event read the same
    pre-reset state, then every target is assigned together
    (docs/vision/north-star.md 3.2).
    """

    target: str
    expr: "Expression"
    line: int = 0


@dataclass
class FlowWhenDecl:
    """`when x reaches L { ... }`: a sign-change guard with a reset body.

    Fires when the sign of `x - L` at end-of-step differs from its sign at
    the previous step's end (docs/vision/north-star.md section 5, card:
    hybrid-events). `when`, `reaches`, and `becomes` are contextual, so all
    three remain ordinary identifiers outside this position.
    """

    guard_target: str
    threshold: "Expression"
    body: List[FlowBecomesDecl]
    line: int = 0


@dataclass
class DurationLiteral:
    """NUMBER + time-unit suffix, canonicalized to i64 nanoseconds at parse
    time (docs/vision/north-star.md 4.1). Valid only where a duration is
    grammatically expected (`every`, `solver dt`); the suffix words stay
    ordinary identifiers everywhere else. Fractional literals are accepted
    only when they land on a whole number of nanoseconds.
    """

    ns: int
    text: str = ""
    line: int = 0


@dataclass
class FlowEveryDecl:
    """`every <duration> { ... }`: a discrete block fired once per elapsed
    period of integrated time (docs/vision/north-star.md 4.2-4.4, card:
    time-blocks). The period is stored canonicalized to i64 nanoseconds.
    Bodies contain `becomes` updates in this version, staged with the same
    synchronous semantics as `when` resets (3.2).
    """

    period_ns: int
    period_text: str
    body: List[FlowBecomesDecl]
    line: int = 0


@dataclass
class FlowSolverDecl:
    """`solver { dt <duration> method euler|rk4 }` (docs/vision/north-star.md
    2.3): pins the default fixed step used by simulation drivers and the
    integration method. It does not change the `Name_step` signature; dt
    stays caller-supplied.
    """

    dt_ns: int
    dt_text: str
    method: str = "euler"
    line: int = 0


@dataclass
class FlowChildDecl:
    """`plant : Motor` — a nested flow-typed member of a composite flow.

    Spec: docs/vision/north-star.md §8. The type name must name another
    `flow` in the same compilation unit. Lowered as an embedded struct
    field; the parent's step copies `connect` wires then calls Child_step.
    """

    name: str
    type: Type
    line: int = 0
    synthesized: bool = False  # compiler-generated (e.g. a `|>` flow stage)
    params: Optional[List[tuple]] = None  # stage param overrides (name, value)


@dataclass
class FlowConnection:
    """One wire `src_member.src_port -> dst_member.dst_port` inside `connect`.

    An empty `src_member` marks a bare parent-port source (`port -> child.in`),
    where `src_port` names an input or state of the enclosing flow rather than a
    child's port.

    Spec: docs/vision/north-star.md §8.1.
    """

    src_member: str
    src_port: str
    dst_member: str
    dst_port: str
    line: int = 0


@dataclass
class FlowInvariantClause:
    """One boolean expression inside an `always` or `never` block
    (docs/vision/north-star.md 5.4). `text` is the source slice used in
    the runtime violation diagnostic.
    """

    expr: "Expression"
    text: str = ""
    line: int = 0


@dataclass
class FlowAlwaysDecl:
    """`always { expr ... }`: runtime-checked invariants that must hold
    after every completed step (docs/vision/north-star.md 5.4).
    """

    clauses: List[FlowInvariantClause]
    line: int = 0


@dataclass
class FlowNeverDecl:
    """`never { expr ... }`: runtime-checked invariants that must stay
    false after every completed step (docs/vision/north-star.md 5.4).
    Each clause is a full boolean expression; conjunction of states is
    written with `&&` (no implicit conjunction magic).
    """

    clauses: List[FlowInvariantClause]
    line: int = 0


@dataclass
class FlowDecl:
    """`flow Name { ... }`: a struct plus continuous dynamics.

    Recognized contextually (`flow` stays a legal identifier everywhere else).
    Lowered by src/flow/flow_blocks.py into a StructDecl plus generated
    Name_new/Name_init/Name_derivs/Name_step/Name_outputs/Name_check functions.
    Spec: docs/vision/north-star.md sections 1, 2, and 5.4.
    """

    name: str
    states: List[FlowStateDecl]
    inputs: List[FlowInputDecl]
    outputs: List[FlowOutputDecl]
    params: List[FlowParamDecl]
    evolves: List[FlowEvolveDecl]
    whens: List[FlowWhenDecl] = field(default_factory=list)
    everys: List[FlowEveryDecl] = field(default_factory=list)
    alwayses: List[FlowAlwaysDecl] = field(default_factory=list)
    nevers: List[FlowNeverDecl] = field(default_factory=list)
    solver: Optional[FlowSolverDecl] = None
    children: List[FlowChildDecl] = field(default_factory=list)
    connections: List[FlowConnection] = field(default_factory=list)
    is_exported: bool = False
    location: Optional[SourceLocation] = None


Expression = Union[
    Literal,
    Variable,
    BinaryOperation,
    UnaryOperation,
    FunctionCall,
    StructLiteral,
    FieldAccess,
    ArrayLiteral,
    VectorLiteral,
    ArrayAccess,
    EffectCall,
    MethodCall,
    StructPattern,
    OrPattern,
    ListPattern,
    CastExpression,
    Lambda,
    TryExpr,
    SortExpr,
    FindExpr,
]
Statement = Union[
    VarDecl,
    Assignment,
    IfStatement,
    WhileStatement,
    ForStatement,
    ReturnStatement,
    Expression,
    EffectDecl,
    CapabilityDecl,
    HandleStatement,
    LayoutStatement,
    MatchStatement,
    DeferStatement,
    BreakStatement,
    ContinueStatement,
    ImportDecl,
    ExportDecl,
    ConstDecl,
    TestDecl,
    TraitDecl,
    ImplDecl,
    AssumeStmt,
    ThereforeStmt,
]


class Lexer:
    def __init__(self, text: str):
        self.text = text
        self._source = text  # Store for error messages
        self.pos = 0
        self.line = 1
        self.column = 1

        self.keyword_map = {
            "function": TokenType.FUNCTION,
            "let": TokenType.LET,
            "mut": TokenType.MUT,
            "return": TokenType.RETURN,
            "if": TokenType.IF,
            "elif": TokenType.ELIF,
            "else": TokenType.ELSE,
            "while": TokenType.WHILE,
            "for": TokenType.FOR,
            "break": TokenType.BREAK,
            "continue": TokenType.CONTINUE,
            "in": TokenType.IN,
            "parallel": TokenType.PARALLEL,
            # `step` is contextual (only meaningful after a for-range), so it
            # stays an IDENTIFIER. parse_for recognizes the bare word "step".
            "to": TokenType.TO,
            "match": TokenType.MATCH,
            "default": TokenType.DEFAULT,
            "test": TokenType.TEST,
            "trait": TokenType.TRAIT,
            "impl": TokenType.IMPL,
            "self": TokenType.SELF,
            "type": TokenType.TYPE,
            "distinct": TokenType.DISTINCT,
            "as": TokenType.AS,
            "enum": TokenType.ENUM,
            "theorem": TokenType.THEOREM,
            "assume": TokenType.ASSUME,
            "therefore": TokenType.THEREFORE,
            "with": TokenType.WITH,
            "handle": TokenType.HANDLE,
            "ui_layout": TokenType.UI_LAYOUT,
            "ui_row": TokenType.UI_ROW,
            "ui_column": TokenType.UI_COLUMN,
            "ui_stack": TokenType.UI_STACK,
            "ui_grid": TokenType.UI_GRID,
            "effect": TokenType.EFFECT,
            "capability": TokenType.CAPABILITY,
            "import": TokenType.IMPORT,
            "export": TokenType.EXPORT,
            "extern": TokenType.EXTERN,
            "const": TokenType.CONST,
            "struct": TokenType.STRUCT,
            "and": TokenType.AND,
            "or": TokenType.OR,
            "not": TokenType.NOT,
            "true": TokenType.BOOLEAN,
            "false": TokenType.BOOLEAN,
            "null": TokenType.NULL,
            "defer": TokenType.DEFER,
            "dbg": TokenType.DBG,
            "expect": TokenType.EXPECT,
            "module": TokenType.MODULE,
            "void": TokenType.VOID,
            "i8": TokenType.I8,
            "i16": TokenType.I16,
            "i32": TokenType.I32,
            "i64": TokenType.I64,
            "i128": TokenType.I128,
            "u8": TokenType.U8,
            "u16": TokenType.U16,
            "u32": TokenType.U32,
            "u64": TokenType.U64,
            "u128": TokenType.U128,
            "f32": TokenType.F32,
            "f64": TokenType.F64,
            "bool": TokenType.BOOL,
            "string": TokenType.STRING_TYPE,
            "vec": TokenType.VEC,
            "ptr": TokenType.IDENTIFIER,  # Will be handled in parse_type
            "array": TokenType.IDENTIFIER,  # Will be handled in parse_type
        }

        self.token_specifications = [
            (r"COMMENT", r"\#.*"),
            (r"NEWLINE", r"\n"),
            (r"WHITESPACE", r"\s+"),  # Skip whitespace
            (r"ARROW", r"->"),
            (r"FAT_ARROW", r"=>"),
            (r"QUESTION", r"\?"),
            (r"EQUALS", r"=="),
            (r"NOT_EQUALS", r"!="),
            (r"LSHIFT", r"<<"),  # Bitwise left shift (must be before LESS)
            (r"RSHIFT", r">>"),  # Bitwise right shift (must be before GREATER)
            (r"LESS_EQUAL", r"<="),
            (r"GREATER_EQUAL", r">="),
            (r"AND", r"&&"),
            (r"OR", r"\|\|"),
            (r"PIPELINE", r"\|>"),  # Pipeline chaining: x |> f(y)
            (r"PIPE", r"\|"),  # Bitwise OR (or lambda)
            (r"AMPERSAND", r"&"),  # Bitwise AND
            (r"CARET", r"\^"),  # Bitwise XOR
            (r"TILDE", r"~"),  # Bitwise NOT
            (r"DOTDOT", r"\.\."),
            (r"DOUBLE_COLON", r"::"),
            # Compound assignment (must come before simple operators)
            (r"PLUS_ASSIGN", r"\+="),
            (r"MINUS_ASSIGN", r"-="),
            (r"STAR_ASSIGN", r"\*="),
            (r"SLASH_ASSIGN", r"/="),
            # Simple operators
            (r"PLUS", r"\+"),
            (r"MINUS", r"-"),
            (r"STAR", r"\*"),
            (r"SLASH", r"/"),
            (r"PERCENT", r"%"),
            (r"LESS", r"<"),
            (r"GREATER", r">"),
            (r"ASSIGN", r"="),
            (r"NOT", r"!"),
            (r"LPAREN", r"\("),
            (r"RPAREN", r"\)"),
            (r"LBRACE", r"\{"),
            (r"RBRACE", r"\}"),
            (r"LBRACKET", r"\["),
            (r"RBRACKET", r"\]"),
            (r"SEMICOLON", r";"),
            (r"COLON", r":"),
            (r"COMMA", r","),
            (r"DOT", r"\."),
            (r"AT", r"@"),
            (r"STRING_LITERAL", r'"(?:[^"\\]|\\.)*"'),
            (
                r"NUMBER",
                r"0x[0-9a-fA-F]+|[0-9]+\.[0-9]+(?:[eE][+-]?[0-9]+)?|[0-9]+[eE][+-]?[0-9]+|[0-9]+",
            ),
            (
                r"CLAIM_COORDINATE",
                r"«[^»]+»\s*«[^»]+»\s*«[^»]+»",
            ),
            (
                r"CLAIM_PATH",
                r"[A-Za-z][A-Za-z0-9_]*/(?:\|\||[+|=|*]|[a-z][a-zA-Z0-9_-]*)\.[a-z][a-z0-9-]+",
            ),
            (r"IDENTIFIER", r"[a-zA-Z_][a-zA-Z0-9_]*"),
        ]

        self.token_regex = "|".join(
            f"(?P<{name}>{pattern})" for name, pattern in self.token_specifications
        )
        self.get_token = re.compile(self.token_regex).match

    def _validate_string_literal(self, token_value: str) -> None:
        # token_value includes quotes
        if len(token_value) < 2:
            raise SyntaxError("Invalid string literal")
        content = token_value[1:-1]
        i = 0
        while i < len(content):
            if content[i] == "\\":
                if i + 1 >= len(content):
                    raise SyntaxError("Invalid escape sequence at end of string")
                esc = content[i + 1]
                if esc not in ['n', 't', 'r', '\\\\', '"', '0']:
                    raise SyntaxError(f"Invalid escape sequence: \\\\{esc}")
                i += 2
                continue
            i += 1

    def next_token(self) -> Token:
        while self.pos < len(self.text):
            m = self.get_token(self.text, self.pos)
            if not m:
                raise SyntaxError(
                    f"Unexpected character at line {self.line}, column {self.column}"
                )

            token_type_name = m.lastgroup
            token_value = m.group(token_type_name)

            # Skip whitespace and comments
            if token_type_name not in ["WHITESPACE", "COMMENT", "NEWLINE"]:
                token_type = getattr(TokenType, token_type_name)

                # Check if it's a keyword
                if (
                    token_type == TokenType.IDENTIFIER
                    and token_value in self.keyword_map
                ):
                    token_type = self.keyword_map[token_value]
                if token_type == TokenType.STRING_LITERAL:
                    self._validate_string_literal(token_value)

                token = Token(token_type, token_value, self.line, self.column)

                # Update position
                self.pos = m.end()
                self.column += len(token_value.expandtabs(4))

                return token

            # Update position for whitespace and newlines
            self.pos = m.end()
            if token_type_name == "NEWLINE":
                self.line += 1
                self.column = 1
            else:
                self.column += len(token_value.expandtabs(4))

        return Token(TokenType.EOF, "", self.line, self.column)

    def look_ahead(self) -> TokenType:
        """Look ahead at the next token without consuming it"""
        save_pos = self.pos
        save_line = self.line
        save_column = self.column

        token = self.next_token()
        token_type = token.type

        # Restore position
        self.pos = save_pos
        self.line = save_line
        self.column = save_column

        return token_type

    def tokenize(self) -> List[Token]:
        """
        Tokenize all input and return a list of tokens (excluding EOF).
        Resets position to allow re-tokenization.
        """
        # Save position
        save_pos = self.pos
        save_line = self.line
        save_column = self.column

        # Reset to start
        self.pos = 0
        self.line = 1
        self.column = 1

        tokens = []
        while True:
            token = self.next_token()
            if token.type == TokenType.EOF:
                break
            tokens.append(token)

        # Restore position
        self.pos = save_pos
        self.line = save_line
        self.column = save_column

        return tokens


class Parser:
    # Maximum combined expression/statement nesting depth. Measured on
    # CPython with the default recursion limit (1000): one parenthesized
    # expression level costs ~13.5 interpreter frames (RecursionError at 69
    # levels from a shallow stack), one nested statement ~3 frames
    # (RecursionError at 324). 50 keeps the worst case (~675 frames) safely
    # below the interpreter limit even when parsing starts on a deep caller
    # stack, while remaining far beyond any real program's nesting.
    MAX_NESTING_DEPTH = 50

    def __init__(self, lexer: Lexer, source: str = None):
        self.lexer = lexer
        self.source = source or getattr(lexer, "_source", "")
        self.current_token = self.lexer.next_token()
        self.lookahead = self.lexer.next_token()
        self.struct_names = set()
        self.nesting_depth = 0
        self._has_fork = False

    def _enter_nesting(self, kind: str = "expression") -> None:
        """Bump the nesting depth; reject pathologically deep input cleanly
        instead of letting recursive descent hit Python's RecursionError.
        Callers must decrement self.nesting_depth in a finally block."""
        self.nesting_depth += 1
        if self.nesting_depth > self.MAX_NESTING_DEPTH:
            raise self.error(
                f"{kind} nesting too deep (limit {self.MAX_NESTING_DEPTH})",
                suggestion="split the code into smaller expressions or blocks",
            )

    def advance(self):
        self.current_token = self.lookahead
        self.lookahead = self.lexer.next_token()

    def _peek2(self) -> Token:
        """Peek one token past self.lookahead without consuming lexer state.

        Used for contextual keywords (e.g. `flow Name {`) that need a third
        token of lookahead. Saves and restores the lexer position, matching
        the save/restore pattern used by struct-literal backtracking.
        """
        save_pos = self.lexer.pos
        save_line = self.lexer.line
        save_column = self.lexer.column
        token = self.lexer.next_token()
        self.lexer.pos = save_pos
        self.lexer.line = save_line
        self.lexer.column = save_column
        return token

    def _at_flow_decl(self) -> bool:
        """True when positioned at `flow IDENT {`, the contextual flow-block
        form. The triple lookahead keeps `flow` a legal identifier everywhere
        else (docs/vision/north-star.md 0.2)."""
        return (
            self.current_token.type == TokenType.IDENTIFIER
            and self.current_token.value == "flow"
            and self.lookahead.type == TokenType.IDENTIFIER
            and self._peek2().type == TokenType.LBRACE
        )

    def _at_unit_decl(self) -> bool:
        """True when positioned at `unit IDENT`, the contextual unit
        declaration form (docs/vision/north-star.md 6.2). Only consulted at
        the top level, where no other declaration starts with the identifier
        `unit`, so `unit` stays a legal variable name everywhere else."""
        return (
            self.current_token.type == TokenType.IDENTIFIER
            and self.current_token.value == "unit"
            and self.lookahead.type == TokenType.IDENTIFIER
        )

    def error(self, message: str, suggestion: str = None) -> FlowSyntaxError:
        """Create a syntax error with context."""
        return FlowSyntaxError(
            message,
            line=self.current_token.line if self.current_token else None,
            column=self.current_token.column
            if hasattr(self.current_token, "column")
            else None,
            source=self.source,
            suggestion=suggestion or get_suggestion(message),
        )

    # Soft keywords usable as names (function/var/param) while remaining
    # operators in infix/unary position. `test` is historical; `and`/`or`
    # appear as bit-op helpers in the verify corpus.
    _SOFT_IDENTIFIER_TYPES = frozenset(
        {
            TokenType.TEST,
            TokenType.AND,
            TokenType.OR,
        }
    )

    def expect(self, token_type: TokenType):
        if self.current_token.type == token_type:
            token = self.current_token
            self.advance()
            return token
        if (
            token_type == TokenType.IDENTIFIER
            and self.current_token.type in self._SOFT_IDENTIFIER_TYPES
        ):
            # Allow soft keywords as identifiers: `function test()`, `function and(...)`
            token = self.current_token
            self.advance()
            return token
        else:
            msg = f"Expected {token_type}, got {self.current_token.type}"
            raise self.error(msg)

    def parse_array_size(self, what: str = "array") -> int:
        """Parse a static size used in a type: a non-negative integer literal.

        Raises FlowSyntaxError (with line/column) for float, exponent,
        negative, or non-numeric size tokens instead of crashing.
        """
        token = self.current_token
        if token.type != TokenType.NUMBER:
            raise self.error(
                f"{what} size must be an integer literal, "
                f"got {token.type}",
                suggestion=f"use a non-negative integer literal for the {what} size, e.g. 4",
            )
        text = str(token.value)
        try:
            size = int(text, 16) if text.lower().startswith("0x") else int(text)
        except ValueError:
            raise self.error(
                f"{what} size must be an integer literal, got '{text}'",
                suggestion=f"use a non-negative integer literal for the {what} size, e.g. 4",
            ) from None
        if size < 0:
            raise self.error(
                f"{what} size must be non-negative, got '{text}'"
            )
        if size > 0x7FFFFFFFFFFFFFFF:  # must fit in i64
            raise self.error(
                f"{what} size is too large: '{text}'"
            )
        self.advance()
        return size

    def parse(
        self,
        expand_flows: bool = True,
    ) -> List[
        Union[
            FunctionDecl, EffectDecl, CapabilityDecl, StructDecl, ImportDecl, ConstDecl,
            TypeAliasDecl, DistinctTypeDecl, FlowDecl
        ]
    ]:
        declarations = []
        while self.current_token.type != TokenType.EOF:
            is_exported = False
            attributes = []

            # Parse decorators like @gpu, @inline, @only(hot, compile)
            while self.current_token.type == TokenType.AT:
                self.advance()  # consume @
                attr_name = self.expect(TokenType.IDENTIFIER).value
                if self.current_token.type == TokenType.LPAREN:
                    self.advance()
                    args = []
                    if self.current_token.type != TokenType.RPAREN:
                        # Parse identifiers or string literals as args
                        while True:
                            if self.current_token.type == TokenType.IDENTIFIER:
                                args.append(self.current_token.value)
                                self.advance()
                            elif self.current_token.type == TokenType.STRING_LITERAL:
                                args.append(self.current_token.value.strip('"').strip("'"))
                                self.advance()
                            else:
                                raise SyntaxError(
                                    f"Expected decorator argument, got {self.current_token.type}"
                                )
                            if self.current_token.type == TokenType.COMMA:
                                self.advance()
                                continue
                            break
                    self.expect(TokenType.RPAREN)
                    attributes.append(f"{attr_name}({','.join(args)})")
                else:
                    attributes.append(attr_name)

            if self.current_token.type == TokenType.EXPORT:
                self.advance()
                if self.current_token.type in (
                    TokenType.FUNCTION,
                    TokenType.STRUCT,
                    TokenType.ENUM,
                    TokenType.EFFECT,
                    TokenType.CAPABILITY,
                    TokenType.CONST,
                    TokenType.TYPE,
                    TokenType.DISTINCT,
                    TokenType.THEOREM,
                    TokenType.IMPORT,
                ):
                    is_exported = True
                else:
                    declarations.append(self.parse_export_list())
                    continue

            if self.current_token.type == TokenType.FUNCTION:
                decl = self.parse_function()
                decl.is_exported = is_exported
                decl.attributes = attributes
                declarations.append(decl)
            elif self.current_token.type == TokenType.THEOREM:
                decl = self.parse_theorem()
                decl.is_exported = is_exported
                declarations.append(decl)
            elif self.current_token.type == TokenType.STRUCT:
                decl = self.parse_struct()
                decl.is_exported = is_exported
                declarations.append(decl)
            elif self.current_token.type == TokenType.ENUM:
                decl = self.parse_enum()
                decl.is_exported = is_exported
                declarations.append(decl)
            elif self.current_token.type == TokenType.EFFECT:
                decl = self.parse_effect()
                decl.is_exported = is_exported
                declarations.append(decl)
            elif self.current_token.type == TokenType.CAPABILITY:
                decl = self.parse_capability()
                decl.is_exported = is_exported
                declarations.append(decl)
            elif self.current_token.type == TokenType.IMPORT:
                imp = self.parse_import()
                if is_exported:
                    if imp.alias is not None:
                        raise SyntaxError(
                            f"'export import {imp.path} as {imp.alias}' is not "
                            f"supported: re-export forwards symbols, not aliases"
                        )
                    imp.is_reexport = True
                declarations.append(imp)
            elif self.current_token.type == TokenType.CONST:
                decl = self.parse_const()
                decl.is_exported = is_exported
                declarations.append(decl)
            elif self.current_token.type == TokenType.LET:
                if is_exported:
                    raise SyntaxError(
                        f"Cannot export a module static at line {self.current_token.line}"
                    )
                declarations.append(self.parse_static())
            elif self.current_token.type == TokenType.TEST:
                if is_exported:
                    raise SyntaxError(
                        f"Cannot export a test declaration at line {self.current_token.line}"
                    )
                declarations.append(self.parse_test())
            elif self.current_token.type == TokenType.EXTERN:
                if is_exported:
                    raise SyntaxError(
                        f"Cannot export an extern declaration at line {self.current_token.line}"
                    )
                # parse_extern returns a list of FunctionDecls - extend to add all of them
                extern_funcs = self.parse_extern()
                declarations.extend(extern_funcs)
            elif self.current_token.type == TokenType.TRAIT:
                decl = self.parse_trait()
                declarations.append(decl)
            elif self.current_token.type == TokenType.IMPL:
                decl = self.parse_impl()
                declarations.append(decl)
            elif self.current_token.type == TokenType.TYPE:
                decl = self.parse_type_alias()
                decl.is_exported = is_exported
                declarations.append(decl)
            elif self.current_token.type == TokenType.DISTINCT:
                decl = self.parse_distinct_type()
                decl.is_exported = is_exported
                declarations.append(decl)
            elif self._at_unit_decl():
                decl = self.parse_unit()
                decl.is_exported = is_exported
                declarations.append(decl)
            elif self.current_token.type == TokenType.MODULE:
                mod = self.parse_module()
                mod.is_exported = is_exported
                declarations.append(mod)
            elif self._at_flow_decl():
                decl = self.parse_flow_decl()
                decl.is_exported = is_exported
                declarations.append(decl)
            else:
                raise SyntaxError(f"Unexpected declaration: {self.current_token.type}")
        if expand_flows and any(isinstance(d, FlowDecl) for d in declarations):
            from .flow_blocks import expand_flow_decls

            declarations = expand_flow_decls(declarations, source=self.source)
        if self._has_fork:
            from .fork_records import desugar_forks

            declarations = desugar_forks(declarations)
        return declarations

    def parse_module(self) -> ModuleDecl:
        """Parse module name { ... } and collect inner declarations."""
        self.expect(TokenType.MODULE)
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.LBRACE)
        inner: List[Any] = []
        while self.current_token.type != TokenType.RBRACE:
            if self.current_token.type == TokenType.EOF:
                raise SyntaxError("Unterminated module: expected '}' before end of file")
            saved = self.current_token
            # Re-use top-level parse logic for one declaration at a time
            if saved.type == TokenType.FUNCTION:
                inner.append(self.parse_function())
            elif saved.type == TokenType.STRUCT:
                inner.append(self.parse_struct())
            elif saved.type == TokenType.CONST:
                inner.append(self.parse_const())
            elif saved.type == TokenType.ENUM:
                inner.append(self.parse_enum())
            elif saved.type == TokenType.IMPORT:
                inner.append(self.parse_import())
            elif saved.type == TokenType.TRAIT:
                inner.append(self.parse_trait())
            elif saved.type == TokenType.IMPL:
                inner.append(self.parse_impl())
            else:
                raise SyntaxError(
                    f"Unexpected declaration inside module '{name}': {saved.type}"
                )
        self.expect(TokenType.RBRACE)
        return ModuleDecl(name=name, declarations=inner)

    def parse_import(self) -> ImportDecl:
        self.expect(TokenType.IMPORT)

        # Legacy string import: import "path/to/file.flow"
        if self.current_token.type == TokenType.STRING_LITERAL:
            path_token = self.current_token
            self.advance()
            path = path_token.value[1:-1]
            return ImportDecl(path=path, is_legacy_string=True)

        module_path = self._parse_module_path()
        symbols: Optional[List[str]] = None
        alias: Optional[str] = None

        if self.current_token.type == TokenType.LBRACE:
            symbols = self._parse_import_symbol_list()
        elif self.current_token.type == TokenType.AS:
            self.advance()
            alias = self.expect(TokenType.IDENTIFIER).value

        return ImportDecl(path=module_path, symbols=symbols, alias=alias)

    def _parse_claim_path_ref(self) -> str:
        if self.current_token.type == TokenType.CLAIM_COORDINATE:
            value = self.current_token.value
            self.advance()
            return value
        if self.current_token.type == TokenType.CLAIM_PATH:
            value = self.current_token.value
            self.advance()
            return value
        return self.expect(TokenType.IDENTIFIER).value

    def parse_export_list(self) -> ExportDecl:
        """Parse: export sym1, sym2 (export keyword already consumed)."""
        symbols: List[str] = []
        while True:
            symbols.append(self._parse_claim_path_ref())
            if self.current_token.type != TokenType.COMMA:
                break
            self.advance()
        return ExportDecl(symbols=symbols)

    def _parse_dashed_identifier(self) -> str:
        """Parse IDENTIFIER (- IDENTIFIER)* as a single hyphenated name.

        Scoped to import module-path segments and import symbol lists only
        (called from `_parse_module_path` / `_parse_import_symbol_list`).
        MINUS has no meaning in either grammar position (there is no
        subtraction expression there), so merging runs like
        `Group-inv-unique` into one dashed identifier is unambiguous and
        does not affect subtraction parsing anywhere else.
        """
        name = self.expect(TokenType.IDENTIFIER).value
        while self.current_token.type == TokenType.MINUS:
            self.advance()
            name += "-" + self.expect(TokenType.IDENTIFIER).value
        return name

    def _parse_morphism_suffix(self) -> str:
        """Parse the morphism half of a Domain/op module-path segment.

        Matches the claim-path morphism grammar:
        `||` | `+` | `=` | `*` | IDENTIFIER (e.g. `out`, `vectorize`).
        Only called from `_parse_module_path_segment` after a `/`.
        """
        tok = self.current_token
        if tok.type == TokenType.OR:
            self.advance()
            return "||"
        if tok.type == TokenType.PLUS:
            self.advance()
            return "+"
        if tok.type == TokenType.ASSIGN:
            self.advance()
            return "="
        if tok.type == TokenType.STAR:
            self.advance()
            return "*"
        if tok.type == TokenType.IDENTIFIER:
            return self.expect(TokenType.IDENTIFIER).value
        raise SyntaxError(
            f"Expected morphism after '/' in module path, got {tok.type}"
        )

    def _parse_module_path_segment(self) -> str:
        """Parse one dotted module-path segment.

        Allows:
        - hyphenated names: `Group-inv-unique`
        - operator-suffixed claim morphisms: `Nat/+`, `Bool/||`, `RingBuffer/fifo`
        - a whole CLAIM_PATH token (`Nat/+.zero-left`) when the lexer
          already glued Domain/op.facet together (e.g. trailing facet import)
        """
        if self.current_token.type == TokenType.CLAIM_PATH:
            value = self.current_token.value
            self.advance()
            return value

        name = self._parse_dashed_identifier()
        if self.current_token.type == TokenType.SLASH:
            self.advance()
            name += "/" + self._parse_morphism_suffix()
        return name

    def _parse_module_path(self) -> str:
        """Parse dotted module path: verify.nat, std.math, .sibling_mod,
        .Group-inv-unique, verify.Nat/+ (hyphenated + operator-suffixed
        segments allowed)."""
        relative = False
        if self.current_token.type == TokenType.DOT:
            relative = True
            self.advance()

        segments: List[str] = [self._parse_module_path_segment()]
        while self.current_token.type == TokenType.DOT:
            self.advance()
            segments.append(self._parse_module_path_segment())

        if relative:
            return "." + ".".join(segments)
        return ".".join(segments)

    def _parse_import_symbol_list(self) -> List[str]:
        """Parse { sym1, sym2 } after a module path (hyphenated symbol
        names such as `inv-unique` are allowed)."""
        self.expect(TokenType.LBRACE)
        symbols: List[str] = []
        if self.current_token.type != TokenType.RBRACE:
            while True:
                symbols.append(self._parse_dashed_identifier())
                if self.current_token.type != TokenType.COMMA:
                    break
                self.advance()
        self.expect(TokenType.RBRACE)
        return symbols

    def parse_const(self) -> ConstDecl:
        self.expect(TokenType.CONST)
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.COLON)
        type = self.parse_type()
        self.expect(TokenType.ASSIGN)
        value = self.parse_expression_without_assign()

        # Semicolons are optional
        if self.current_token.type == TokenType.SEMICOLON:
            self.advance()

        return ConstDecl(name, type, value)

    def parse_static(self) -> StaticDecl:
        """Parse a module static: top-level `let mut name: Type = value`."""
        line = self.current_token.line
        self.expect(TokenType.LET)
        if self.current_token.type != TokenType.MUT:
            raise SyntaxError(
                f"Top-level 'let' at line {line} must be 'let mut' (module static); "
                f"use 'const' for immutable module-level values"
            )
        self.advance()
        name = self.expect(TokenType.IDENTIFIER).value
        if self.current_token.type != TokenType.COLON:
            raise SyntaxError(
                f"Module static '{name}' at line {line} requires an explicit "
                f"type annotation"
            )
        self.advance()
        type = self.parse_type()
        self.expect(TokenType.ASSIGN)
        value = self.parse_expression_without_assign()

        # Semicolons are optional
        if self.current_token.type == TokenType.SEMICOLON:
            self.advance()

        return StaticDecl(name, type, value)

    def parse_test(self) -> FunctionDecl:
        self.expect(TokenType.TEST)
        name_token = self.expect(TokenType.STRING_LITERAL)
        raw_name = name_token.value[1:-1]
        # Sanitize to a valid identifier for downstream C codegen
        safe_name = re.sub(r"[^a-zA-Z0-9_]", "_", raw_name)
        if not safe_name:
            safe_name = "case"
        name = "test_" + safe_name
        body = self.parse_block()

        # Create a function that returns bool
        return_type = Type("bool")
        parameters = []  # No parameters for tests

        return FunctionDecl(name, parameters, return_type, body, ["test"])

    def parse_extern(self) -> List[FunctionDecl]:
        """Parse extern function declaration block - returns all declared functions."""
        self.expect(TokenType.EXTERN)

        # Parse extern block: extern "module" { function declarations }
        if self.current_token.type == TokenType.STRING_LITERAL:
            # Skip the module name for now
            self.advance()

        self.expect(TokenType.LBRACE)

        functions = []
        while self.current_token.type != TokenType.RBRACE:
            if self.current_token.type == TokenType.EOF:
                raise SyntaxError("Unterminated extern block: expected '}' before end of file")
            if self.current_token.type == TokenType.FUNCTION:
                # Parse function signature only for extern
                self.expect(TokenType.FUNCTION)
                name = self.expect(TokenType.IDENTIFIER).value
                self.expect(TokenType.LPAREN)

                parameters = []
                if self.current_token.type != TokenType.RPAREN:
                    parameters = self.parse_parameters()

                self.expect(TokenType.RPAREN)

                return_type = Type("void")  # Default
                if self.current_token.type == TokenType.ARROW:
                    self.advance()
                    return_type = self.parse_type()

                # Create function declaration with empty body
                func = FunctionDecl(name, parameters, return_type, Block([]), [])
                func.is_extern = True
                functions.append(func)
            else:
                raise SyntaxError(
                    f"Expected function declaration in extern block at line {self.current_token.line}"
                )

        self.expect(TokenType.RBRACE)

        # Return ALL extern functions - not just the first one
        return functions

    def parse_struct(self) -> StructDecl:
        start_token = self.current_token
        self.expect(TokenType.STRUCT)
        name_token = self.current_token
        name = self.expect(TokenType.IDENTIFIER).value
        self.struct_names.add(name)

        # Parse optional type parameters: struct Foo<T, U> { ... }
        type_params = []
        if self.current_token.type == TokenType.LESS:
            type_params = self.parse_type_parameters()
            # Also register generic struct name (without params) for type resolution

        self.expect(TokenType.LBRACE)

        fields = []
        while self.current_token.type != TokenType.RBRACE:
            if self.current_token.type == TokenType.EOF:
                raise SyntaxError("Unterminated struct: expected '}' before end of file")
            field_name = self.expect(TokenType.IDENTIFIER).value
            self.expect(TokenType.COLON)
            field_type = self.parse_type()
            fields.append(Parameter(field_name, field_type))

            if self.current_token.type == TokenType.COMMA:
                self.advance()

        self.expect(TokenType.RBRACE)

        loc = SourceLocation(
            line=start_token.line - 1,
            column=start_token.column - 1,
            end_line=name_token.line - 1,
            end_column=name_token.column - 1 + len(name),
        )
        return StructDecl(name, fields, type_params=type_params, location=loc)

    def parse_flow_decl(self) -> FlowDecl:
        """Parse `flow Name { ... }` (docs/vision/north-star.md 1.1).

        Body items in this card's scope:
          state|input|output|param NAME : type [= expr]
          NAME : FlowType                  # nested flow member (§8)
          NAME evolves as expr
          when NAME reaches expr { NAME becomes expr ... }
          always { expr ... } / never { expr ... }
          connect { NAME.NAME -> NAME.NAME ... }
        `flow`, `state`, `input`, `output`, `param`, `evolves`, `when`,
        `reaches`, `becomes`, `always`, `never`, `connect` are contextual
        keywords: each is recognized only by its position and at most two
        tokens of lookahead, so all of them remain ordinary identifiers
        elsewhere.
        """
        start_token = self.current_token
        self.advance()  # consume contextual 'flow'
        name_token = self.expect(TokenType.IDENTIFIER)
        name = name_token.value
        # Flow instances are constructed with struct-literal syntax.
        self.struct_names.add(name)
        self.expect(TokenType.LBRACE)

        states: List[FlowStateDecl] = []
        inputs: List[FlowInputDecl] = []
        outputs: List[FlowOutputDecl] = []
        params: List[FlowParamDecl] = []
        evolves: List[FlowEvolveDecl] = []
        whens: List[FlowWhenDecl] = []
        everys: List[FlowEveryDecl] = []
        alwayses: List[FlowAlwaysDecl] = []
        nevers: List[FlowNeverDecl] = []
        children: List[FlowChildDecl] = []
        connections: List[FlowConnection] = []
        solver: Optional[FlowSolverDecl] = None
        section_words = ("state", "input", "output", "param")

        while self.current_token.type != TokenType.RBRACE:
            if self.current_token.type == TokenType.EOF:
                raise self.error(
                    f"Unterminated flow '{name}': expected '}}' before end of file"
                )
            tok = self.current_token
            is_section = (
                tok.type == TokenType.IDENTIFIER
                and tok.value in section_words
                and self.lookahead.type == TokenType.IDENTIFIER
            )
            is_evolves = (
                tok.type == TokenType.IDENTIFIER
                and self.lookahead.type == TokenType.IDENTIFIER
                and self.lookahead.value == "evolves"
            )
            peek2 = (
                self._peek2()
                if tok.type == TokenType.IDENTIFIER
                and tok.value == "when"
                and self.lookahead.type == TokenType.IDENTIFIER
                else None
            )
            is_when = (
                peek2 is not None
                and peek2.type == TokenType.IDENTIFIER
                and peek2.value == "reaches"
            )
            # `every 10 ms { ... }`: `every` followed by a number is the
            # discrete-block form; `every` anywhere else stays an identifier
            # (so `state every : f64` and `every evolves as ...` still parse).
            is_every = (
                tok.type == TokenType.IDENTIFIER
                and tok.value == "every"
                and self.lookahead.type == TokenType.NUMBER
            )
            # `solver { ... }`: `solver` directly before '{' is the settings
            # block; `solver` in any other position stays an identifier.
            is_solver = (
                tok.type == TokenType.IDENTIFIER
                and tok.value == "solver"
                and self.lookahead.type == TokenType.LBRACE
            )
            # `always { ... }` / `never { ... }`: the word immediately before
            # '{' is the invariant form; elsewhere both stay identifiers.
            is_always = (
                tok.type == TokenType.IDENTIFIER
                and tok.value == "always"
                and self.lookahead.type == TokenType.LBRACE
            )
            is_never = (
                tok.type == TokenType.IDENTIFIER
                and tok.value == "never"
                and self.lookahead.type == TokenType.LBRACE
            )
            # `connect { ... }`: `connect` directly before '{' is the
            # composition block (docs/vision/north-star.md §8).
            is_connect = (
                tok.type == TokenType.IDENTIFIER
                and tok.value == "connect"
                and self.lookahead.type == TokenType.LBRACE
            )
            # `plant : Motor`: bare `name : Type` (no section word) is a
            # nested flow member. Section words take the is_section path
            # above; `state x : f64` never reaches here.
            is_child = (
                tok.type == TokenType.IDENTIFIER
                and tok.value not in section_words
                and self.lookahead.type == TokenType.COLON
            )
            if is_section:
                kind = tok.value
                self.advance()  # consume section word
                member_name = self.expect(TokenType.IDENTIFIER).value
                self.expect(TokenType.COLON)
                member_type = self.parse_type()
                initializer = None
                if self.current_token.type == TokenType.ASSIGN:
                    self.advance()
                    initializer = self.parse_expression_without_assign()
                if kind == "state":
                    states.append(
                        FlowStateDecl(member_name, member_type, initializer, tok.line)
                    )
                elif kind == "param":
                    params.append(
                        FlowParamDecl(member_name, member_type, initializer, tok.line)
                    )
                elif kind == "input":
                    if initializer is not None:
                        raise self.error(
                            f"input '{member_name}' in flow '{name}' cannot have an "
                            f"initializer; inputs are written by the embedder",
                            suggestion="remove the '= ...' part",
                        )
                    inputs.append(FlowInputDecl(member_name, member_type, tok.line))
                else:  # output
                    outputs.append(
                        FlowOutputDecl(member_name, member_type, initializer, tok.line)
                    )
            elif is_evolves:
                target = tok.value
                self.advance()  # consume target
                self.advance()  # consume contextual 'evolves'
                self.expect(TokenType.AS)
                rhs = self.parse_expression_without_assign()
                evolves.append(FlowEvolveDecl(target, rhs, tok.line))
            elif is_when:
                whens.append(self._parse_flow_when(name))
            elif is_every:
                everys.append(self._parse_flow_every(name))
            elif is_solver:
                if solver is not None:
                    raise self.error(
                        f"flow '{name}' has two 'solver' blocks; a flow "
                        f"pins at most one default step",
                        suggestion="merge the settings into one solver block",
                    )
                solver = self._parse_flow_solver(name)
            elif is_always:
                alwayses.append(self._parse_flow_invariant(name, "always"))
            elif is_never:
                nevers.append(self._parse_flow_invariant(name, "never"))
            elif is_connect:
                connections.extend(self._parse_flow_connect(name))
            elif is_child:
                child_name = tok.value
                self.advance()  # consume member name
                self.expect(TokenType.COLON)
                child_type = self.parse_type()
                if self.current_token.type == TokenType.ASSIGN:
                    raise self.error(
                        f"nested flow member '{child_name}' in flow '{name}' "
                        f"cannot have an initializer; children are constructed "
                        f"by {child_type.name}_new inside the parent",
                        suggestion="remove the '= ...' part",
                    )
                children.append(
                    FlowChildDecl(child_name, child_type, tok.line)
                )
            else:
                raise self.error(
                    f"Unexpected item in flow '{name}' body",
                    suggestion=(
                        "flow bodies contain member declarations "
                        "('state|input|output|param name : type [= expr]'), "
                        "nested flow members ('plant : Motor'), "
                        "dynamics ('x evolves as expr'), events "
                        "('when x reaches expr { x becomes expr }'), "
                        "discrete blocks ('every 10 ms { x becomes expr }'), "
                        "composition ('connect { a.out -> b.in }'), "
                        "invariants ('always { expr }' / 'never { expr }'), "
                        "and settings ('solver { dt 1 ms }')"
                    ),
                )

        self.expect(TokenType.RBRACE)
        loc = SourceLocation(
            line=start_token.line - 1,
            column=start_token.column - 1,
            end_line=name_token.line - 1,
            end_column=name_token.column - 1 + len(name),
        )
        return FlowDecl(
            name, states, inputs, outputs, params, evolves, whens, everys,
            alwayses, nevers, solver,
            children=children, connections=connections, location=loc
        )

    def _parse_flow_connect(self, flow_name: str) -> List[FlowConnection]:
        """Parse `connect { a.out -> b.in ... }` (docs/vision/north-star.md §8).

        Grammar: connection := IDENT '.' IDENT '->' IDENT '.' IDENT
        """
        self.advance()  # consume contextual 'connect'
        self.expect(TokenType.LBRACE)
        connections: List[FlowConnection] = []
        while self.current_token.type != TokenType.RBRACE:
            if self.current_token.type == TokenType.EOF:
                raise self.error(
                    f"Unterminated 'connect' body in flow '{flow_name}': "
                    f"expected '}}' before end of file"
                )
            src_tok = self.current_token
            first = self.expect(TokenType.IDENTIFIER).value
            if self.current_token.type == TokenType.DOT:
                # `child.port` — a sibling subflow's output/state.
                self.advance()
                src_member = first
                src_port = self.expect(TokenType.IDENTIFIER).value
            else:
                # Bare `port` — a port of the enclosing (parent) flow.
                # Empty src_member marks a parent source.
                src_member = ""
                src_port = first
            self.expect(TokenType.ARROW)
            dst_member = self.expect(TokenType.IDENTIFIER).value
            self.expect(TokenType.DOT)
            dst_port = self.expect(TokenType.IDENTIFIER).value
            connections.append(
                FlowConnection(
                    src_member, src_port, dst_member, dst_port, src_tok.line
                )
            )
        self.expect(TokenType.RBRACE)
        return connections

    def _parse_flow_invariant(
        self, flow_name: str, kind: str
    ) -> "FlowAlwaysDecl | FlowNeverDecl":
        """Parse `always { expr+ }` or `never { expr+ }`
        (docs/vision/north-star.md 5.4). Each clause is one boolean
        expression; `expression+` rejects an empty body.
        """
        block_token = self.current_token
        self.advance()  # consume contextual 'always' / 'never'
        self.expect(TokenType.LBRACE)
        clauses: List[FlowInvariantClause] = []
        while self.current_token.type != TokenType.RBRACE:
            if self.current_token.type == TokenType.EOF:
                raise self.error(
                    f"Unterminated '{kind}' body in flow '{flow_name}': "
                    f"expected '}}' before end of file"
                )
            start_tok = self.current_token
            expr = self.parse_expression_without_assign()
            text = self._source_between(start_tok, self.current_token)
            clauses.append(FlowInvariantClause(expr, text, start_tok.line))
        self.expect(TokenType.RBRACE)
        if not clauses:
            raise self.error(
                f"'{kind}' block in flow '{flow_name}' needs at least one "
                f"boolean expression",
                suggestion=f"write '{kind} {{ x < 1.0 }}' or remove the block",
            )
        if kind == "always":
            return FlowAlwaysDecl(clauses, block_token.line)
        return FlowNeverDecl(clauses, block_token.line)

    def _source_between(self, start_tok: Token, end_tok: Token) -> str:
        """Source text from start_tok through the token before end_tok."""
        if not self.source:
            return ""
        lines = self.source.split("\n")
        sl, sc = start_tok.line - 1, max(start_tok.column - 1, 0)
        el, ec = end_tok.line - 1, max(end_tok.column - 1, 0)
        if sl < 0 or sl >= len(lines):
            return ""
        if sl == el:
            return lines[sl][sc:ec].strip()
        parts = [lines[sl][sc:]]
        for i in range(sl + 1, min(el, len(lines))):
            parts.append(lines[i])
        if 0 <= el < len(lines):
            parts.append(lines[el][:ec])
        return " ".join(p.strip() for p in parts if p.strip())

    def _parse_flow_when(self, flow_name: str) -> FlowWhenDecl:
        """Parse `when NAME reaches expr { NAME becomes expr ... }`.

        Only the zero-crossing guard form exists in this card's scope; the
        boolean edge form (`when cond { }`) is reserved by the spec
        (docs/vision/north-star.md 5.1). Bodies contain `becomes` resets
        only in this version.
        """
        when_token = self.current_token
        self.advance()  # consume contextual 'when'
        guard_target = self.expect(TokenType.IDENTIFIER).value
        self.advance()  # consume contextual 'reaches'
        threshold = self.parse_expression_without_assign()
        body = self._parse_becomes_body(flow_name, "when", "resets")
        return FlowWhenDecl(guard_target, threshold, body, when_token.line)

    def _parse_becomes_body(
        self, flow_name: str, block_word: str, what: str
    ) -> List[FlowBecomesDecl]:
        """Parse `{ NAME becomes expr ... }`, the body shared by `when`
        events and `every` blocks. Only `becomes` statements exist in this
        version; each right-hand side is a full expression.
        """
        self.expect(TokenType.LBRACE)
        body: List[FlowBecomesDecl] = []
        while self.current_token.type != TokenType.RBRACE:
            if self.current_token.type == TokenType.EOF:
                raise self.error(
                    f"Unterminated '{block_word}' body in flow '{flow_name}': "
                    f"expected '}}' before end of file"
                )
            stmt_tok = self.current_token
            is_becomes = (
                stmt_tok.type == TokenType.IDENTIFIER
                and self.lookahead.type == TokenType.IDENTIFIER
                and self.lookahead.value == "becomes"
            )
            if not is_becomes:
                raise self.error(
                    f"Unexpected statement in '{block_word}' body of flow "
                    f"'{flow_name}'",
                    suggestion=(
                        f"'{block_word}' bodies contain {what} in this "
                        f"version: 'x becomes expr'"
                    ),
                )
            target = stmt_tok.value
            self.advance()  # consume target
            self.advance()  # consume contextual 'becomes'
            rhs = self.parse_expression_without_assign()
            body.append(FlowBecomesDecl(target, rhs, stmt_tok.line))

        self.expect(TokenType.RBRACE)
        return body

    def parse_duration(self, where: str) -> DurationLiteral:
        """Parse NUMBER + time-unit suffix into i64 nanoseconds
        (docs/vision/north-star.md 4.1).

        The lexer keeps the number and the suffix as separate tokens
        (`10ms` lexes as NUMBER(10) IDENT(ms)), so suffix words stay legal
        identifiers everywhere a duration is not expected. Fractional
        literals must land on a whole number of nanoseconds; time is never
        silently rounded.
        """
        num_token = self.current_token
        if num_token.type != TokenType.NUMBER:
            raise self.error(
                f"Expected a duration in {where}, "
                f"got {num_token.type}",
                suggestion=(
                    "write a number with a time-unit suffix, e.g. '10 ms' "
                    "(units: ns, us, ms, s, min)"
                ),
            )
        self.advance()
        suffix_token = self.current_token
        if (
            suffix_token.type != TokenType.IDENTIFIER
            or suffix_token.value not in DURATION_UNIT_NS
        ):
            got = (
                f"'{suffix_token.value}'"
                if suffix_token.type == TokenType.IDENTIFIER
                else str(suffix_token.type)
            )
            raise self.error(
                f"Expected a time unit after '{num_token.value}' in {where}, "
                f"got {got}",
                suggestion="valid time units: ns, us, ms, s, min",
            )
        self.advance()

        text = str(num_token.value)
        try:
            if text.lower().startswith("0x"):
                value = Fraction(int(text, 16))
            else:
                value = Fraction(text)
        except (ValueError, ZeroDivisionError):
            raise self.error(
                f"Invalid duration value '{text}' in {where}"
            ) from None
        ns = value * DURATION_UNIT_NS[suffix_token.value]
        if ns.denominator != 1:
            raise self.error(
                f"Duration '{text} {suffix_token.value}' in {where} is not "
                f"a whole number of nanoseconds; time is not silently rounded",
                suggestion=(
                    "use a finer unit, e.g. '500 us' instead of '0.5 ms'"
                ),
            )
        ns_int = ns.numerator
        if ns_int > 0x7FFFFFFFFFFFFFFF:
            raise self.error(
                f"Duration '{text} {suffix_token.value}' in {where} "
                f"overflows the i64 nanosecond range"
            )
        return DurationLiteral(
            ns=ns_int,
            text=f"{text} {suffix_token.value}",
            line=num_token.line,
        )

    def _parse_flow_every(self, flow_name: str) -> FlowEveryDecl:
        """Parse `every <duration> { NAME becomes expr ... }`
        (docs/vision/north-star.md 4.2). The period canonicalizes to i64
        nanoseconds at parse time.
        """
        every_token = self.current_token
        self.advance()  # consume contextual 'every'
        period = self.parse_duration(f"the 'every' period of flow '{flow_name}'")
        body = self._parse_becomes_body(flow_name, "every", "discrete updates")
        return FlowEveryDecl(period.ns, period.text, body, every_token.line)

    def _parse_flow_solver(self, flow_name: str) -> FlowSolverDecl:
        """Parse `solver { dt <duration> method <name> }`
        (docs/vision/north-star.md 2.3). `dt` is required; `method` is
        optional and defaults to euler. Settings may come in either order,
        each at most once.
        """
        solver_token = self.current_token
        self.advance()  # consume contextual 'solver'
        self.expect(TokenType.LBRACE)

        dt: Optional[DurationLiteral] = None
        method: Optional[str] = None
        while self.current_token.type != TokenType.RBRACE:
            if self.current_token.type == TokenType.EOF:
                raise self.error(
                    f"Unterminated 'solver' block in flow '{flow_name}': "
                    f"expected '}}' before end of file"
                )
            tok = self.current_token
            if tok.type == TokenType.IDENTIFIER and tok.value == "dt":
                if dt is not None:
                    raise self.error(
                        f"'solver' block in flow '{flow_name}' sets 'dt' twice"
                    )
                self.advance()
                dt = self.parse_duration(
                    f"the solver dt of flow '{flow_name}'"
                )
            elif tok.type == TokenType.IDENTIFIER and tok.value == "method":
                if method is not None:
                    raise self.error(
                        f"'solver' block in flow '{flow_name}' sets "
                        f"'method' twice"
                    )
                self.advance()
                method = self.expect(TokenType.IDENTIFIER).value
            else:
                raise self.error(
                    f"Unexpected item in 'solver' block of flow "
                    f"'{flow_name}'",
                    suggestion=(
                        "solver blocks contain 'dt <duration>' and "
                        "'method euler' or 'method rk4'"
                    ),
                )
        self.expect(TokenType.RBRACE)

        if dt is None:
            raise self.error(
                f"'solver' block in flow '{flow_name}' needs a 'dt' setting",
                suggestion="write 'solver { dt 1 ms }'",
            )
        return FlowSolverDecl(
            dt.ns, dt.text, method or "euler", solver_token.line
        )

    def parse_enum(self) -> EnumDecl:
        """Parse enum declaration: enum Option<T> { Some(T), None }"""
        self.expect(TokenType.ENUM)
        name = self.expect(TokenType.IDENTIFIER).value

        # Parse optional type parameters: enum Option<T> { ... }
        type_params = []
        if self.current_token.type == TokenType.LESS:
            type_params = self.parse_type_parameters()

        self.expect(TokenType.LBRACE)

        variants = []
        while self.current_token.type != TokenType.RBRACE:
            if self.current_token.type == TokenType.EOF:
                raise SyntaxError("Unterminated enum: expected '}' before end of file")
            variant_name = self.expect(TokenType.IDENTIFIER).value

            # Parse optional variant fields: Some(T) or Ok(T, String)
            variant_fields = []
            if self.current_token.type == TokenType.LPAREN:
                self.advance()
                if self.current_token.type != TokenType.RPAREN:
                    variant_fields.append(self.parse_type())
                    while self.current_token.type == TokenType.COMMA:
                        self.advance()
                        variant_fields.append(self.parse_type())
                self.expect(TokenType.RPAREN)

            variants.append(EnumVariant(variant_name, variant_fields))

            # Optional comma between variants
            if self.current_token.type == TokenType.COMMA:
                self.advance()

        self.expect(TokenType.RBRACE)
        return EnumDecl(name, variants, type_params=type_params)

    def parse_trait(self) -> TraitDecl:
        """Parse trait declaration: trait Printable { function to_string(self) -> string }"""
        self.expect(TokenType.TRAIT)
        name = self.expect(TokenType.IDENTIFIER).value

        # Parse optional type parameters: trait Comparable<T> { ... }
        type_params = []
        if self.current_token.type == TokenType.LESS:
            type_params = self.parse_type_parameters()

        self.expect(TokenType.LBRACE)

        methods = []
        while self.current_token.type != TokenType.RBRACE:
            if self.current_token.type == TokenType.EOF:
                raise SyntaxError("Unterminated trait: expected '}' before end of file")
            if self.current_token.type == TokenType.FUNCTION:
                self.advance()  # consume 'function'
                method_name = self.expect(TokenType.IDENTIFIER).value
                self.expect(TokenType.LPAREN)

                # Parse parameters
                params = []
                has_self = False
                if self.current_token.type != TokenType.RPAREN:
                    # Check for self parameter
                    if self.current_token.type == TokenType.SELF:
                        has_self = True
                        self.advance()
                        # Optional: self might have a type annotation
                        if self.current_token.type == TokenType.COLON:
                            self.advance()
                            self.parse_type()  # Ignore self type for now
                        if self.current_token.type == TokenType.COMMA:
                            self.advance()

                    # Parse remaining parameters
                    if self.current_token.type != TokenType.RPAREN:
                        params = self.parse_parameters()

                self.expect(TokenType.RPAREN)

                # Parse return type
                return_type = Type("void")
                if self.current_token.type == TokenType.ARROW:
                    self.advance()
                    return_type = self.parse_type()

                methods.append(TraitMethod(method_name, params, return_type, has_self))
            else:
                raise SyntaxError(
                    f"Expected 'function' in trait body, got {self.current_token.type}"
                )

        self.expect(TokenType.RBRACE)
        return TraitDecl(name, methods, type_params)

    def parse_impl(self) -> ImplDecl:
        """Parse impl block: impl Trait for Type { ... }"""
        self.expect(TokenType.IMPL)
        trait_name = self.expect(TokenType.IDENTIFIER).value

        # Expect 'for'
        if self.current_token.type == TokenType.FOR:
            self.advance()
        else:
            raise SyntaxError(
                f"Expected 'for' after trait name in impl, got {self.current_token.type}"
            )

        for_type = self.parse_type()

        self.expect(TokenType.LBRACE)

        methods = []
        while self.current_token.type != TokenType.RBRACE:
            if self.current_token.type == TokenType.EOF:
                raise SyntaxError("Unterminated impl block: expected '}' before end of file")
            if self.current_token.type == TokenType.FUNCTION:
                method = self.parse_function()
                methods.append(method)
            else:
                raise SyntaxError(
                    f"Expected 'function' in impl body, got {self.current_token.type}"
                )

        self.expect(TokenType.RBRACE)
        return ImplDecl(trait_name, for_type, methods)

    def parse_type_alias(self) -> TypeAliasDecl:
        """Parse type alias declaration: type Name = BaseType

        Examples:
            type UserId = i32
            type Vec2 = array<f32, 2>
            type Callback = (i32, i32) -> i32
        """
        self.expect(TokenType.TYPE)
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.ASSIGN)
        base_type = self.parse_type()

        # Semicolons are optional
        if self.current_token.type == TokenType.SEMICOLON:
            self.advance()

        return TypeAliasDecl(name, base_type)

    def parse_distinct_type(self) -> DistinctTypeDecl:
        """Parse distinct type declaration: distinct type Name = BaseType

        Distinct types are nominally typed - incompatible with their base type.

        Examples:
            distinct type Distance = f32
            distinct type Speed = f32
            # Distance and Speed are incompatible despite both being f32
        """
        self.expect(TokenType.DISTINCT)
        self.expect(TokenType.TYPE)
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.ASSIGN)
        base_type = self.parse_type()

        # Semicolons are optional
        if self.current_token.type == TokenType.SEMICOLON:
            self.advance()

        return DistinctTypeDecl(name, base_type)

    def parse_unit(self) -> UnitDecl:
        """Parse a unit declaration (docs/vision/north-star.md 6.2):

            unit Meter                      # new base dimension
            unit Velocity = Meter / Second  # derived unit
            unit Accel    = Meter / Second^2

        Grammar:
            unit_decl := "unit" IDENT
                       | "unit" IDENT "=" unit_expr
            unit_expr := factor (("*" | "/") factor)*
            factor    := IDENT ("^" ["-"] INT)? | "1"

        The spec grammar has no parentheses, so the right-hand side flattens
        exactly into (name, exponent) pairs; "/" negates the exponent of the
        factor that follows it. All units are f64-based in v1.
        """
        line = self.current_token.line
        self.expect(TokenType.IDENTIFIER)  # the contextual keyword `unit`
        name = self.expect(TokenType.IDENTIFIER).value
        factors: Optional[List[Tuple[str, int]]] = None
        if self.current_token.type == TokenType.ASSIGN:
            self.advance()
            factors = self._parse_unit_expr()
        if self.current_token.type == TokenType.SEMICOLON:
            self.advance()
        return UnitDecl(name, Type("f64"), factors=factors, line=line)

    def _parse_unit_expr(self) -> List[Tuple[str, int]]:
        factors = self._parse_unit_factor(1)
        while self.current_token.type in (TokenType.STAR, TokenType.SLASH):
            sign = 1 if self.current_token.type == TokenType.STAR else -1
            self.advance()
            factors.extend(self._parse_unit_factor(sign))
        return factors

    def _parse_unit_factor(self, sign: int) -> List[Tuple[str, int]]:
        if self.current_token.type == TokenType.NUMBER:
            if self.current_token.value != "1":
                raise self.error(
                    f"Expected a unit name or '1' in unit expression, "
                    f"got '{self.current_token.value}'"
                )
            self.advance()
            return []  # "1" is dimensionless: contributes no factors
        name = self.expect(TokenType.IDENTIFIER).value
        exponent = 1
        if self.current_token.type == TokenType.CARET:
            self.advance()
            negative = False
            if self.current_token.type == TokenType.MINUS:
                negative = True
                self.advance()
            exp_token = self.expect(TokenType.NUMBER)
            try:
                exponent = int(exp_token.value)
            except ValueError:
                raise self.error(
                    f"Unit exponent must be an integer, got '{exp_token.value}'"
                )
            if negative:
                exponent = -exponent
        return [(name, sign * exponent)]

    def parse_theorem(self) -> TheoremDecl:
        """Parse: theorem Nat/+.zero-left(m: Nat) { ... }"""
        self.expect(TokenType.THEOREM)
        claim_path = self._parse_claim_path_ref()
        self.expect(TokenType.LPAREN)
        parameters: List[Parameter] = []
        if self.current_token.type != TokenType.RPAREN:
            parameters = self.parse_parameters()
        self.expect(TokenType.RPAREN)
        body = self.parse_block()
        return TheoremDecl(claim_path=claim_path, parameters=parameters, body=body)

    def _expect_name(self) -> str:
        """Expect an identifier, including soft keywords usable as names (`and`/`or`)."""
        if self.current_token.type in (
            TokenType.IDENTIFIER,
            TokenType.AND,
            TokenType.OR,
        ):
            name = self.current_token.value
            self.advance()
            return name
        return self.expect(TokenType.IDENTIFIER).value

    def parse_function(self) -> FunctionDecl:
        start_token = self.current_token
        self.expect(TokenType.FUNCTION)
        name_token = self.current_token
        name = self._expect_name()

        # Parse optional type parameters: function foo<T, U>(...)
        type_params = []
        if self.current_token.type == TokenType.LESS:
            type_params = self.parse_type_parameters()

        self.expect(TokenType.LPAREN)

        parameters = []
        has_self = False
        if self.current_token.type != TokenType.RPAREN:
            # Handle self parameter (for methods)
            if self.current_token.type == TokenType.SELF:
                has_self = True
                self.advance()
                # Optional type annotation for self
                if self.current_token.type == TokenType.COLON:
                    self.advance()
                    self_type = self.parse_type()
                    # If self has an explicit type, add it as a regular parameter
                    parameters.append(Parameter("self", self_type))
                if self.current_token.type == TokenType.COMMA:
                    self.advance()

            # Parse remaining parameters
            if self.current_token.type != TokenType.RPAREN:
                parameters.extend(self.parse_parameters())

        self.expect(TokenType.RPAREN)

        return_type = Type("void")  # Default
        if self.current_token.type == TokenType.ARROW:
            self.advance()
            return_type = self.parse_type()

        # Effect row: `with Log, Inventory` (after return type, before body)
        effects: List[str] = []
        if self.current_token.type == TokenType.WITH:
            self.advance()
            effects.append(self.expect(TokenType.IDENTIFIER).value)
            while self.current_token.type == TokenType.COMMA:
                self.advance()
                effects.append(self.expect(TokenType.IDENTIFIER).value)

        # Check for forward declaration (no body)
        if self.current_token.type != TokenType.LBRACE:
            # Forward declaration - empty body
            func = FunctionDecl(
                name,
                parameters,
                return_type,
                Block([]),
                [],
                type_params=type_params,
                effects=effects,
            )
            func.is_forward_decl = True
            if has_self:
                func.has_self = True
            return func

        body = self.parse_block()

        # Create location from start token (0-based for LSP)
        loc = SourceLocation(
            line=start_token.line - 1,  # Convert to 0-based
            column=start_token.column - 1,
            end_line=name_token.line - 1,
            end_column=name_token.column - 1 + len(name),
        )

        fn = FunctionDecl(
            name,
            parameters,
            return_type,
            body,
            [],
            type_params=type_params,
            location=loc,
            effects=effects,
        )
        # Store has_self as an attribute (for impl methods)
        fn.has_self = has_self
        return fn

    def parse_type_parameters(self) -> List[TypeParameter]:
        """Parse generic type parameters: <T> or <T, U> or <T: Trait>"""
        self.expect(TokenType.LESS)  # Consume <

        params = []
        # First parameter
        param_name = self.expect(TokenType.IDENTIFIER).value
        bound = None

        # Optional bound: <T: Trait>
        if self.current_token.type == TokenType.COLON:
            self.advance()
            bound = self.expect(TokenType.IDENTIFIER).value

        params.append(TypeParameter(param_name, bound))

        # Additional parameters
        while self.current_token.type == TokenType.COMMA:
            self.advance()
            param_name = self.expect(TokenType.IDENTIFIER).value
            bound = None

            if self.current_token.type == TokenType.COLON:
                self.advance()
                bound = self.expect(TokenType.IDENTIFIER).value

            params.append(TypeParameter(param_name, bound))

        self.expect(TokenType.GREATER)  # Consume >
        return params

    def parse_parameters(self) -> List[Parameter]:
        parameters = []
        parameters.append(self.parse_parameter())

        while self.current_token.type == TokenType.COMMA:
            self.advance()
            parameters.append(self.parse_parameter())

        return parameters

    def parse_parameter(self) -> Parameter:
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.COLON)
        type = self.parse_type()
        return Parameter(name, type)

    def _layer2_span_error(self, form: str, suggestion: str):
        """Diagnostic for span forms the design accepts but this compiler does not."""
        return self.error(
            f"{form} is not yet implemented in this compiler version",
            suggestion=suggestion,
        )

    def parse_span_type(self) -> Type:
        """Parse `span<...>` after the `span` keyword has been consumed.

        Supported (layer 1): span<T>, span<const T>, span<mut T>, and each of
        those with a static extent, e.g. span<mut f32, 512>.
        """
        if self.current_token.type == TokenType.LBRACKET:
            raise self._layer2_span_error(
                "the `span[N]` extent-only form",
                "write the element type too, e.g. span<f32, 16>",
            )
        if self.current_token.type != TokenType.LESS:
            raise self._layer2_span_error(
                "bare `span` with inferred element type",
                "name the element type, e.g. span<f32> or &[f32]",
            )
        self.advance()  # consume <

        is_mut = False
        keyword = None
        if self.current_token.type == TokenType.MUT:
            is_mut = True
            keyword = "mut"
            self.advance()
        elif self.current_token.type == TokenType.CONST:
            keyword = "const"
            self.advance()

        if keyword and self.current_token.type in (TokenType.GREATER, TokenType.COMMA):
            raise self._layer2_span_error(
                f"`span<{keyword}>` without an element type",
                f"name the element type, e.g. span<{keyword} f32>",
            )

        element_type = self.parse_type()
        if element_type.name in ("number", "integer", "float"):
            raise self._layer2_span_error(
                f"the trait-shaped element constraint `span<{element_type.name}>`",
                "use a concrete element type, e.g. span<f64>",
            )

        extent = None
        if self.current_token.type == TokenType.COMMA:
            self.advance()
            if self.current_token.type != TokenType.NUMBER:
                raise self._layer2_span_error(
                    "a dependent span extent",
                    "use an integer literal extent, e.g. span<mut f32, 512>",
                )
            extent = self.parse_array_size("span")
        self.expect(TokenType.GREATER)
        return make_span_type(element_type, is_mut, extent)

    def parse_reference_span_type(self) -> Type:
        """Parse the `&[T]` / `&mut [T]` / `&[T; N]` sugar (`&` consumed)."""
        is_mut = False
        if self.current_token.type == TokenType.MUT:
            is_mut = True
            self.advance()
        self.expect(TokenType.LBRACKET)
        element_type = self.parse_type()
        extent = None
        if self.current_token.type == TokenType.SEMICOLON:
            self.advance()
            extent = self.parse_array_size("span")
        self.expect(TokenType.RBRACKET)
        return make_span_type(element_type, is_mut, extent)

    def parse_type(self) -> Type:
        # Reference sugar for spans: &[T], &mut [T], &[T; N], &mut [T; N].
        # Desugars at parse time so downstream passes see only span_* types.
        if self.current_token.type == TokenType.AMPERSAND:
            self.advance()
            return self.parse_reference_span_type()

        # Check for capability type: capability EffectName
        if self.current_token.type == TokenType.CAPABILITY:
            self.advance()
            effect_name = self.expect(TokenType.IDENTIFIER).value
            return Type(f"capability_{effect_name}", is_capability=True)

        # Check for generic types first (array<T>, ptr<T>, etc.)
        if self.current_token.type in [
            TokenType.IDENTIFIER,
            TokenType.I8,
            TokenType.I16,
            TokenType.I32,
            TokenType.I64,
            TokenType.I128,
            TokenType.U8,
            TokenType.U16,
            TokenType.U32,
            TokenType.U64,
            TokenType.U128,
            TokenType.F32,
            TokenType.F64,
        ]:
            type_name = self.current_token.value
            self.advance()

            # Borrowed views: span<T>, span<mut T>, span<T, N>, span<mut T, N>
            if type_name == "span":
                return self.parse_span_type()

            # Check for generic array type: array<T, N> or array<T>
            if type_name == "array" and self.current_token.type == TokenType.LESS:
                self.advance()  # consume <
                element_type = self.parse_type()
                if self.current_token.type == TokenType.COMMA:
                    self.advance()  # consume ,
                    size = self.parse_array_size("array")
                    self.expect(TokenType.GREATER)
                    return Type(
                        f"array_{size}_{element_type.name}",
                        size=size,
                        element_type=element_type,
                    )
                else:
                    self.expect(TokenType.GREATER)
                    return Type(f"array_{element_type.name}", element_type=element_type)
            # Check for pointer type: ptr<T>
            elif type_name == "ptr" and self.current_token.type == TokenType.LESS:
                self.advance()  # consume <
                pointee_type = self.parse_type()
                self.expect(TokenType.GREATER)
                return Type(
                    f"ptr_{pointee_type.name}",
                    is_pointer=True,
                    element_type=pointee_type,
                )
            # Check for vector type: vec4<T>
            elif (
                type_name.startswith("vec")
                and self.current_token.type == TokenType.LESS
            ):
                self.advance()  # consume <
                element_type = self.parse_type()
                self.expect(TokenType.GREATER)
                # Extract size from vec4, vec8, etc.
                size_str = type_name[3:]  # Remove 'vec' prefix
                try:
                    size = int(size_str)
                    return Type(
                        f"vec{size}_{element_type.name}",
                        size=size,
                        element_type=element_type,
                    )
                except ValueError:
                    raise SyntaxError(f"Invalid vector size: {size_str}")
            # Check for array type: f32[]
            elif self.current_token.type == TokenType.LBRACKET:
                self.advance()
                self.expect(TokenType.RBRACKET)
                return Type(f"array_{type_name}", element_type=Type(type_name))
            # Check for generic type application: Option<T> or Result<T, E>
            elif self.current_token.type == TokenType.LESS:
                self.advance()  # consume <
                type_args = [self.parse_type()]
                while self.current_token.type == TokenType.COMMA:
                    self.advance()
                    type_args.append(self.parse_type())
                self.expect(TokenType.GREATER)
                # Create a type name like Option_i32 or Result_i32_string
                type_args_str = "_".join(t.name for t in type_args)
                return Type(f"{type_name}_{type_args_str}", type_args=type_args)
            else:
                # Simple type (or type variable like T)
                return Type(type_name)

        elif self.current_token.type in [
            TokenType.BOOL,
            TokenType.VOID,
            TokenType.STRING_TYPE,
        ]:
            type_name = self.current_token.value
            self.advance()
            return Type(type_name)

        elif self.current_token.type == TokenType.VEC:
            self.advance()
            size = self.parse_array_size("vector")
            element_type = self.parse_type()
            return Type(
                f"vec{size}_{element_type.name}", size=size, element_type=element_type
            )

        elif self.current_token.type == TokenType.LBRACKET:
            self.advance()
            element_type = self.parse_type()
            self.expect(TokenType.SEMICOLON)
            size = self.parse_array_size("array")
            self.expect(TokenType.RBRACKET)
            return Type(
                f"array_{size}_{element_type.name}",
                size=size,
                element_type=element_type,
            )

        # Function / closure type: (T1, T2) -> R [with E…]  (escaping HOF ABI)
        elif self.current_token.type == TokenType.LPAREN:
            self.advance()
            param_types: List[Type] = []
            if self.current_token.type != TokenType.RPAREN:
                param_types.append(self.parse_type())
                while self.current_token.type == TokenType.COMMA:
                    self.advance()
                    param_types.append(self.parse_type())
            self.expect(TokenType.RPAREN)
            self.expect(TokenType.ARROW)
            return_type = self.parse_type()
            effects: List[str] = []
            if self.current_token.type == TokenType.WITH:
                self.advance()
                effects.append(self.expect(TokenType.IDENTIFIER).value)
                while self.current_token.type == TokenType.COMMA:
                    self.advance()
                    effects.append(self.expect(TokenType.IDENTIFIER).value)
            args_key = "_".join(p.name for p in param_types) if param_types else "void"
            return Type(
                f"fn_{args_key}__{return_type.name}",
                type_args=param_types,
                element_type=return_type,
                effects=effects,
            )

        else:
            raise SyntaxError(f"Unexpected type token: {self.current_token.type}")

    def parse_block(self) -> Block:
        self.expect(TokenType.LBRACE)
        statements = []

        while self.current_token.type != TokenType.RBRACE:
            if self.current_token.type == TokenType.EOF:
                raise SyntaxError("Unterminated block: expected '}' before end of file")
            statements.append(self.parse_statement())

        self.expect(TokenType.RBRACE)
        return Block(statements)

    def parse_statement(self) -> Statement:
        # Nested blocks (if/while/for/match bodies) recurse through here.
        self._enter_nesting("statement")
        try:
            start = self.current_token
            stmt = self._parse_statement_impl()
            # Attach source location for debugger #line mapping / LSP (best-effort).
            # Token lines/columns are 1-based; SourceLocation is 0-based.
            if getattr(stmt, "location", None) is None and start is not None:
                try:
                    setattr(
                        stmt,
                        "location",
                        SourceLocation(
                            line=max(0, start.line - 1),
                            column=max(0, start.column - 1),
                        ),
                    )
                except Exception:
                    pass
            return stmt
        finally:
            self.nesting_depth -= 1

    def _parse_statement_impl(self) -> Statement:
        if self.current_token.type == TokenType.LET:
            return self.parse_var_decl()
        elif self.current_token.type == TokenType.ASSUME:
            return self.parse_assume()
        elif self.current_token.type == TokenType.THEREFORE:
            return self.parse_therefore()
        elif self.current_token.type == TokenType.RETURN:
            return self.parse_return()
        elif self.current_token.type == TokenType.IF:
            return self.parse_if()
        elif self.current_token.type == TokenType.WHILE:
            return self.parse_while()
        elif self.current_token.type == TokenType.FOR:
            return self.parse_for()
        elif self.current_token.type == TokenType.PARALLEL:
            return self.parse_for()  # parse_for handles parallel prefix
        elif self.current_token.type == TokenType.EFFECT:
            return self.parse_effect()
        elif self.current_token.type == TokenType.CAPABILITY:
            return self.parse_capability()
        elif self.current_token.type == TokenType.HANDLE:
            return self.parse_handle()
        elif self.current_token.type in (TokenType.UI_LAYOUT, TokenType.UI_ROW, TokenType.UI_COLUMN, TokenType.UI_STACK, TokenType.UI_GRID):
            return self.parse_layout()
        elif self.current_token.type == TokenType.MATCH:
            return self.parse_match()
        elif self.current_token.type == TokenType.DEFER:
            self.advance()
            expr = self.parse_expression_without_assign()
            return DeferStatement(expr)
        elif self.current_token.type == TokenType.BREAK:
            token = self.expect(TokenType.BREAK)
            return BreakStatement(line=token.line)
        elif self.current_token.type == TokenType.CONTINUE:
            token = self.expect(TokenType.CONTINUE)
            return ContinueStatement(line=token.line)
        elif self.current_token.type == TokenType.EXPECT:
            return self.parse_expect()
        else:
            return self.parse_expression_statement()

    def parse_assume(self) -> AssumeStmt:
        self.expect(TokenType.ASSUME)
        claim_path = self._parse_claim_path_ref()
        arguments: List[Expression] = []
        if self.current_token.type == TokenType.LPAREN:
            self.advance()
            if self.current_token.type != TokenType.RPAREN:
                while True:
                    arguments.append(self.parse_expression_without_assign())
                    if self.current_token.type != TokenType.COMMA:
                        break
                    self.advance()
            self.expect(TokenType.RPAREN)
        return AssumeStmt(claim_path=claim_path, arguments=arguments)

    def parse_therefore(self) -> ThereforeStmt:
        self.expect(TokenType.THEREFORE)
        expression = self.parse_expression_without_assign()
        method: Optional[str] = None
        if (
            self.current_token.type == TokenType.IDENTIFIER
            and self.current_token.value == "by"
        ):
            self.advance()
            method = self.expect(TokenType.IDENTIFIER).value
        return ThereforeStmt(expression=expression, method=method)

    def parse_expect(self) -> ExpectStatement:
        token = self.expect(TokenType.EXPECT)
        condition = self.parse_expression_without_assign()
        return ExpectStatement(condition, line=token.line)

    def parse_effect(self) -> EffectDecl:
        self.expect(TokenType.EFFECT)
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.LBRACE)

        operations = []
        while self.current_token.type != TokenType.RBRACE:
            if self.current_token.type == TokenType.EOF:
                raise SyntaxError("Unterminated effect: expected '}' before end of file")
            operations.append(self.parse_effect_operation())
            if self.current_token.type == TokenType.COMMA:
                self.advance()

        self.expect(TokenType.RBRACE)
        return EffectDecl(name, operations)

    def parse_effect_operation(self) -> EffectOperation:
        # Optionally skip 'function' keyword for more natural syntax
        if self.current_token.type == TokenType.FUNCTION:
            self.advance()
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.LPAREN)

        parameters = []
        if self.current_token.type != TokenType.RPAREN:
            parameters = self.parse_parameters()

        self.expect(TokenType.RPAREN)

        return_type = Type("void")
        if self.current_token.type == TokenType.ARROW:
            self.advance()
            return_type = self.parse_type()

        return EffectOperation(name, parameters, return_type)

    def parse_capability(self) -> CapabilityDecl:
        self.expect(TokenType.CAPABILITY)
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.LBRACE)

        effects = []
        methods = []

        while self.current_token.type != TokenType.RBRACE:
            if self.current_token.type == TokenType.EOF:
                raise SyntaxError("Unterminated capability: expected '}' before end of file")
            if self.current_token.type == TokenType.EFFECT:
                self.advance()
                # Parse multiple effects
                effect_names = []
                effect_names.append(self.expect(TokenType.IDENTIFIER).value)
                while self.current_token.type == TokenType.COMMA:
                    self.advance()
                    # Check if next token is an identifier (another effect) or not
                    if self.current_token.type == TokenType.IDENTIFIER:
                        effect_names.append(self.expect(TokenType.IDENTIFIER).value)
                    else:
                        # No more effects in the list
                        break
                effects.extend(effect_names)
                # Expect comma after effect list
                if self.current_token.type == TokenType.COMMA:
                    self.advance()
            elif self.current_token.type == TokenType.FUNCTION:
                methods.append(self.parse_capability_method())
                # Expect comma after function
                if self.current_token.type == TokenType.COMMA:
                    self.advance()
            else:
                raise SyntaxError(
                    f"Expected effect or function in capability, got {self.current_token.type}"
                )

        self.expect(TokenType.RBRACE)
        return CapabilityDecl(name, effects, methods)

    def parse_capability_method(self) -> CapabilityMethod:
        method = self.parse_function()
        return CapabilityMethod(
            method.name, method.parameters, method.return_type, method.body
        )

    def parse_handle(self) -> HandleStatement:
        self.expect(TokenType.HANDLE)

        # Parse multiple effects
        effects = []
        effects.append(self.expect(TokenType.IDENTIFIER).value)

        while self.current_token.type == TokenType.COMMA:
            self.advance()
            effects.append(self.expect(TokenType.IDENTIFIER).value)

        self.expect(TokenType.WITH)

        # Parse multiple handlers
        handlers = []
        handlers.append(self.expect(TokenType.IDENTIFIER).value)

        while self.current_token.type == TokenType.COMMA:
            self.advance()
            handlers.append(self.expect(TokenType.IDENTIFIER).value)

        body = self.parse_block()

        return HandleStatement(effects, handlers, body)

    def parse_layout(self) -> LayoutStatement:
        kind_token = self.current_token
        self.advance()
        args: List[Expression] = []
        if self.current_token.type == TokenType.LPAREN:
            self.advance()
            if self.current_token.type != TokenType.RPAREN:
                args.append(self.parse_expression())
                while self.current_token.type == TokenType.COMMA:
                    self.advance()
                    args.append(self.parse_expression())
            self.expect(TokenType.RPAREN)
        body = self.parse_block()
        return LayoutStatement(kind_token.value.lower(), args, body)

    def parse_match_pattern(self) -> "Expression":
        """Parse a single match-arm pattern, including `|`-separated alternatives.

        Patterns are parsed one level below bitwise-OR precedence so that a
        bare `|` between pattern atoms is treated as pattern alternation
        (`1 | 2 | 3 => ...`) rather than the bitwise-OR binary operator.
        """
        first = self._finalize_pattern_atom(self.parse_bitwise_xor())

        if self.current_token.type != TokenType.PIPE:
            return first

        alternatives = [first]
        while self.current_token.type == TokenType.PIPE:
            self.advance()
            alternatives.append(self._finalize_pattern_atom(self.parse_bitwise_xor()))

        all_literals = all(isinstance(alt, Literal) for alt in alternatives)
        all_structs = all(isinstance(alt, StructPattern) for alt in alternatives)
        all_lists = all(isinstance(alt, ListPattern) for alt in alternatives)
        if not all_literals and not all_structs and not all_lists:
            raise SyntaxError(
                "`|` in a match pattern requires either all-literal alternatives "
                "(e.g. `1 | 2 | 3 => ...`) or all-struct alternatives with the "
                "same binding names (e.g. `Point(0, y) | Point(1, y) => ...`) "
                "or all-list alternatives of the same length "
                "(e.g. `[0, x] | [1, x] => ...`)"
            )
        if all_structs:
            expected = self._or_pattern_binding_names(alternatives[0])
            for alt in alternatives[1:]:
                names = self._or_pattern_binding_names(alt)
                if names != expected:
                    raise SyntaxError(
                        "`|` struct alternatives must bind the same names in "
                        f"the same order (got {names!r} vs {expected!r})"
                    )
                if alt.struct_name != alternatives[0].struct_name:
                    raise SyntaxError(
                        "`|` struct alternatives must use the same struct type "
                        f"(got {alt.struct_name!r} vs "
                        f"{alternatives[0].struct_name!r})"
                    )
        if all_lists:
            expected = self._or_pattern_binding_names(alternatives[0])
            for alt in alternatives[1:]:
                names = self._or_pattern_binding_names(alt)
                if len(alt.elements) != len(alternatives[0].elements):
                    raise SyntaxError(
                        "`|` list alternatives must have the same length "
                        f"(got {len(alt.elements)} vs {len(alternatives[0].elements)})"
                    )
                if names != expected:
                    raise SyntaxError(
                        "`|` list alternatives must bind the same names in "
                        f"the same order (got {names!r} vs {expected!r})"
                    )

        return OrPattern(alternatives)

    @staticmethod
    def _or_pattern_binding_names(pattern: Any) -> List[str]:
        """Flatten binding names from a (possibly nested) struct/list pattern."""
        if isinstance(pattern, ListPattern):
            return [
                elem.name
                for elem in pattern.elements
                if isinstance(elem, Variable) and elem.name != "_"
            ]
        names: List[str] = []
        field_patterns = pattern.field_patterns or {}
        for i, binding in enumerate(pattern.bindings):
            if i in field_patterns:
                names.extend(Parser._or_pattern_binding_names(field_patterns[i]))
            elif binding != "_":
                names.append(binding)
        return names

    def _finalize_pattern_atom(self, pattern: "Expression") -> "Expression":
        """Convert a parsed pattern atom into a StructPattern/ListPattern where applicable.

        Struct patterns are parsed as `FunctionCall` (`Point(a, b)`). Arguments
        that are plain variables become bindings; literal arguments become
        nested value checks (e.g. `Point(0, y)` requires field 0 == 0 and
        binds field 1 to `y`); arguments that are themselves struct patterns
        (`Inner(x)`) recurse into `field_patterns`, so `Outer(Inner(x), y)`
        matches field 0 against the nested pattern and binds field 1 to `y`.

        Array patterns are parsed as `ArrayLiteral` (`[x]`, `[_, 5]`). Each
        element that is a plain variable becomes a binding; each literal
        becomes a value check on that slot.
        """
        if isinstance(pattern, ArrayLiteral):
            elements: List["Expression"] = []
            for elem in pattern.elements:
                if isinstance(elem, (Variable, Literal)):
                    elements.append(elem)
                else:
                    return pattern
            return ListPattern(elements)

        if not isinstance(pattern, FunctionCall):
            return pattern

        bindings: List[str] = []
        field_literals: Dict[int, "Literal"] = {}
        field_patterns: Dict[int, "StructPattern"] = {}
        for i, arg in enumerate(pattern.arguments):
            if isinstance(arg, Variable):
                bindings.append(arg.name)
            elif isinstance(arg, Literal):
                bindings.append("_")
                field_literals[i] = arg
            elif isinstance(arg, FunctionCall):
                nested = self._finalize_pattern_atom(arg)
                if isinstance(nested, StructPattern):
                    bindings.append("_")
                    field_patterns[i] = nested
                else:
                    # Nested call didn't resolve to a struct pattern (e.g. an
                    # arbitrary expression) - unsupported, fall through to
                    # equality comparison on the whole pattern.
                    return pattern
            else:
                # Not a variable binding, literal, or nested struct pattern -
                # unsupported for now, leave as a plain FunctionCall so it
                # falls through to equality comparison.
                return pattern

        return StructPattern(
            pattern.name, bindings, field_literals or None, field_patterns or None
        )

    def parse_match(self) -> MatchStatement:
        self.expect(TokenType.MATCH)
        value = self.parse_expression_without_assign()
        self.expect(TokenType.LBRACE)

        cases = []
        default_case = None

        while self.current_token.type != TokenType.RBRACE:
            if self.current_token.type == TokenType.EOF:
                raise SyntaxError("Unterminated match: expected '}' before end of file")
            if self.current_token.type == TokenType.DEFAULT:
                self.advance()
                default_case = self.parse_block()
            else:
                pattern = self.parse_match_pattern()

                guard = None
                if self.current_token.type == TokenType.IF:
                    self.advance()
                    guard = self.parse_expression_without_assign()

                self.expect(TokenType.FAT_ARROW)
                body = self.parse_block()
                cases.append(MatchCase(pattern, body, guard))

                if self.current_token.type == TokenType.COMMA:
                    self.advance()

        self.expect(TokenType.RBRACE)
        return MatchStatement(value, cases, default_case)

    def parse_var_decl(self) -> VarDecl:
        self.expect(TokenType.LET)

        # Check for 'mut' modifier: let mut x = ...
        is_mutable = False
        if self.current_token.type == TokenType.MUT:
            is_mutable = True
            self.advance()

        name = self.expect(TokenType.IDENTIFIER).value

        # Type annotation is optional for type inference: let x = 42
        var_type = None
        if self.current_token.type == TokenType.COLON:
            self.advance()
            var_type = self.parse_type()

        initializer = None
        if self.current_token.type == TokenType.ASSIGN:
            self.advance()
            initializer = self.parse_expression_without_assign()

            # If no type annotation, use auto type (for inference)
            if var_type is None:
                var_type = Type("auto")
        elif var_type is None:
            raise SyntaxError(
                f"Variable '{name}' requires either a type annotation or an initializer"
            )

        # Semicolons are optional for backward compatibility
        if self.current_token.type == TokenType.SEMICOLON:
            self.advance()
        return VarDecl(name, var_type, initializer, is_mutable)

    def parse_return(self) -> ReturnStatement:
        self.expect(TokenType.RETURN)
        value = None
        # If the next token is a terminator, it's a bare return.
        if self.current_token.type in [TokenType.SEMICOLON, TokenType.RBRACE, TokenType.EOF]:
            value = None
        elif self.current_token.type == TokenType.VOID:
            # Explicit void return - consume the VOID token
            self.advance()
            value = None
        else:
            value = self.parse_expression_without_assign()

        # Semicolons are optional for backward compatibility
        if self.current_token.type == TokenType.SEMICOLON:
            self.advance()
        return ReturnStatement(value)

    def parse_if(self) -> IfStatement:
        self.expect(TokenType.IF)
        condition = self.parse_expression_without_assign()
        then_block = self.parse_block()

        elif_blocks = []
        while self.current_token.type == TokenType.ELIF:
            self.advance()
            elif_condition = self.parse_expression_without_assign()
            elif_block = self.parse_block()
            elif_blocks.append((elif_condition, elif_block))

        else_block = None
        if self.current_token.type == TokenType.ELSE:
            self.advance()
            else_block = self.parse_block()

        return IfStatement(condition, then_block, elif_blocks, else_block)

    def parse_while(self) -> WhileStatement:
        self.expect(TokenType.WHILE)
        condition = self.parse_expression_without_assign()
        body = self.parse_block()
        return WhileStatement(condition, body)

    def parse_for(self) -> ForStatement:
        is_parallel = False
        if self.current_token.type == TokenType.PARALLEL:
            is_parallel = True
            self.advance()

        self.expect(TokenType.FOR)
        variable = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.IN)

        range_start = self.parse_expression_without_assign()
        if self.current_token.type == TokenType.DOTDOT:
            self.advance()  # consume ..
        elif self.current_token.type == TokenType.TO:
            self.advance()  # consume to
        else:
            raise SyntaxError(
                f"Expected '..' or 'to' in for range, got {self.current_token.type}"
            )
        range_end = self.parse_expression_without_assign()

        step = None
        # Contextual keyword: `for i in 0 to 10 step 2` — `step` is otherwise
        # a normal identifier (e.g. `let step = FullAdder(...)`).
        if (
            self.current_token.type == TokenType.STEP
            or (
                self.current_token.type == TokenType.IDENTIFIER
                and self.current_token.value == "step"
            )
        ):
            self.advance()
            step = self.parse_expression_without_assign()

        body = self.parse_block()
        return ForStatement(variable, range_start, range_end, step, body, is_parallel)

    def parse_expression_statement(self) -> Statement:
        expr = self.parse_assignment()
        # Semicolons are optional for backward compatibility
        if self.current_token.type == TokenType.SEMICOLON:
            self.advance()
        return expr

    def parse_expression(self) -> Expression:
        return self.parse_assignment()

    def parse_expression_without_assign(self) -> Expression:
        left = self.parse_logical_or()
        return self._parse_pipeline_chain(left)

    def _parse_pipeline_chain(self, left: Expression) -> Expression:
        """Consume a run of `|>` stages, threading `left` through each.

        `x |> f(y)` lowers to `f(x, y)` and `x |> f()` to `f(x)`. It is
        left-associative, so `a |> f() |> g()` is `g(f(a))`. Three stage
        shapes get special handling before the generic call lowering:
        declarative ordering (`|> sort by …`), and fork blocks
        (`|> Record { field = … }`, see `_parse_fork_block`).
        """
        while self.current_token.type == TokenType.PIPELINE:
            self.advance()
            if self._at_choose_block():
                left = self._parse_choose_block(left)
                continue
            if self._at_fork_block():
                left = self._parse_fork_block(left)
                continue
            if self._at_declarative_sort():
                left = self._parse_sort_pipeline(left)
                continue
            if self._at_declarative_search():
                left = self._parse_find_pipeline(left)
                continue
            rhs = self.parse_logical_or()
            left = self._apply_pipe(left, rhs)
        return left

    def _apply_pipe(self, left: Expression, rhs: Expression) -> Expression:
        """Insert `left` into a single piped stage `rhs`."""
        if isinstance(rhs, FunctionCall):
            args = self._insert_pipe_arg(left, list(rhs.arguments))
            return FunctionCall(rhs.name, args)
        if isinstance(rhs, MethodCall):
            # `x |> obj.m()` -> `obj.m(x)`; `x |> obj.m(_, y)` -> `obj.m(x, y)`
            args = self._insert_pipe_arg(left, list(rhs.arguments))
            return MethodCall(rhs.object, rhs.method, args)
        if isinstance(rhs, Variable):
            # Bare function name: `x |> f` -> `f(x)`
            return FunctionCall(rhs.name, [left])
        raise SyntaxError(
            "Pipeline '|>' must be followed by a function call, method call, "
            "function name, declarative sort, or fork block "
            "(e.g. `x |> f()`, `x |> f`, `x |> sort by .score`, "
            "or `x |> Record { a = f, b = g }`)"
        )

    def _at_fork_block(self) -> bool:
        """True at a fork block immediately after `|>`.

        Two forms: `Record { … }` (named) and `{ … }` (anonymous, an inferred
        record). A struct literal can never be a plain pipe target (you can't
        call one) and a bare `{` is not a valid pipe target either, so both are
        unambiguous and free to claim.
        """
        if self.current_token.type == TokenType.LBRACE:
            return True
        return (
            self.current_token.type == TokenType.IDENTIFIER
            and self.lookahead.type == TokenType.LBRACE
        )

    def _parse_fork_block(self, source: Expression):
        """Parse a fork block after `|>`.

        A fork block applies several pipelines to the *same* incoming value and
        collects them into a record: each `field = stage…` branch is the
        pipeline `source |> stage…`. Branches read with `=` (not the
        struct-literal `:`) to keep the fork/record forms visually distinct.

        `Record { … }` names the record; `{ … }` infers it. Both produce a
        `ForkBlock` whose branch templates pipe a `ForkSource` placeholder; the
        post-parse `desugar_forks` pass binds the source once, substitutes it,
        and lowers to a `StructLiteral`.
        """
        record_name = None
        if self.current_token.type == TokenType.IDENTIFIER:
            record_name = self.current_token.value
            self.advance()  # record name
        line = self.current_token.line
        self.expect(TokenType.LBRACE)

        # `:` fields mean a flow stage's parameter overrides (value form);
        # `=` fields mean a fork block (pipeline form). Peek the delimiter.
        if (
            self.current_token.type == TokenType.IDENTIFIER
            and self.lookahead.type == TokenType.COLON
        ):
            if record_name is None:
                raise self.error(
                    "an anonymous `|> { ... }` is a fork block and uses '=' "
                    "branches; ':' parameter fields need a named flow stage"
                )
            return self._parse_stage_params(record_name, source, line)

        fields: List[tuple] = []
        seen = set()
        while self.current_token.type != TokenType.RBRACE:
            if self.current_token.type != TokenType.IDENTIFIER:
                raise self.error("Expected a fork field name before '='")
            field_name = self.current_token.value
            self.advance()
            if self.current_token.type == TokenType.COLON:
                raise self.error(
                    "Fork block fields use '=' (a pipeline), not ':'; "
                    "write `{}  = source-pipeline`".format(field_name)
                )
            self.expect(TokenType.ASSIGN)
            if field_name in seen:
                raise self.error(
                    "Duplicate fork field '{}'".format(field_name)
                )
            seen.add(field_name)
            fields.append((field_name, self._parse_fork_branch()))
            if self.current_token.type == TokenType.COMMA:
                self.advance()
        if not fields:
            raise self.error("Fork block must have at least one `field = …` branch")
        self.expect(TokenType.RBRACE)
        self._has_fork = True
        return ForkBlock(record_name, source, fields, line)

    def _parse_fork_branch(self) -> Expression:
        """One fork branch: a pipeline over the `ForkSource` placeholder."""
        rhs = self.parse_logical_or()
        value = self._apply_pipe(ForkSource(), rhs)
        return self._parse_pipeline_chain(value)

    def _at_choose_block(self) -> bool:
        """True at `choose selector {` after `|>`.

        `choose` is contextual: `x |> choose(a, b)` stays an ordinary call, and
        `x |> choose` stays `choose(x)`. Only `choose` followed by the start of
        a selector expression (an identifier or `self`) is the choose form.
        """
        if not (
            self.current_token.type == TokenType.IDENTIFIER
            and self.current_token.value == "choose"
        ):
            return False
        return self.lookahead.type in (TokenType.IDENTIFIER, TokenType.SELF)

    def _parse_choose_block(self, source: Expression) -> "ChooseBlock":
        """Parse `choose selector { pattern => stage, ... }` after `|>`.

        Each arm's stage is a pipeline over the piped value (like a fork
        branch). Lowered by `desugar_forks` to a hoisted temp + `match`.
        """
        self.advance()  # consume 'choose'
        selector = self._parse_choose_selector()
        line = self.current_token.line
        self.expect(TokenType.LBRACE)

        arms: List[tuple] = []
        while self.current_token.type != TokenType.RBRACE:
            if self.current_token.type == TokenType.EOF:
                raise self.error("Unterminated 'choose' block: expected '}'")
            pattern = self.parse_match_pattern()
            self.expect(TokenType.FAT_ARROW)
            arms.append((pattern, self._parse_fork_branch()))
            if self.current_token.type == TokenType.COMMA:
                self.advance()
        if not arms:
            raise self.error("'choose' block needs at least one `pattern => stage` arm")
        self.expect(TokenType.RBRACE)
        self._has_fork = True
        return ChooseBlock(selector, source, arms, line)

    def _parse_choose_selector(self) -> Expression:
        """Parse the `choose` selector: a variable or `self.field` chain.

        Deliberately narrow (no struct-literal, no call) so a trailing `{`
        starts the arm block. Bind a computed selector to a state/let first.
        """
        if self.current_token.type == TokenType.SELF:
            expr: Expression = Variable("self")
            self.advance()
        else:
            expr = Variable(self.expect(TokenType.IDENTIFIER).value)
        while self.current_token.type == TokenType.DOT:
            self.advance()
            field = self.expect(TokenType.IDENTIFIER).value
            expr = FieldAccess(expr, field)
        return expr

    def _parse_stage_params(self, name: str, source: Expression, line: int):
        """Parse `Name { p: v, q: w }` after `|>` — a flow stage with params."""
        params: List[tuple] = []
        seen = set()
        while self.current_token.type != TokenType.RBRACE:
            if self.current_token.type != TokenType.IDENTIFIER:
                raise self.error("Expected a parameter name in flow stage params")
            pname = self.current_token.value
            self.advance()
            self.expect(TokenType.COLON)
            if pname in seen:
                raise self.error(
                    "Duplicate stage parameter '{}'".format(pname)
                )
            seen.add(pname)
            params.append((pname, self.parse_expression()))
            if self.current_token.type == TokenType.COMMA:
                self.advance()
        if not params:
            raise self.error(
                "flow stage '{}' has empty '{{}}'; drop the braces or add "
                "`param: value` overrides".format(name)
            )
        self.expect(TokenType.RBRACE)
        self._has_fork = True  # ensure the post-parse walk runs to catch strays
        return FlowStage(name, source, params, line)

    @staticmethod
    def _is_pipe_placeholder(expr: Expression) -> bool:
        """A bare `_` in a piped call marks where the piped value goes."""
        return isinstance(expr, Variable) and expr.name == "_"

    def _insert_pipe_arg(
        self, piped: Expression, args: List[Expression]
    ) -> List[Expression]:
        """Position the piped value inside a `|>` call's argument list.

        Default (no placeholder): prepend, so `x |> f(y)` -> `f(x, y)`.
        With a `_` placeholder: substitute at that slot, so
        `x |> clamp(0.0, _, 1.0)` -> `clamp(0.0, x, 1.0)`. The placeholder
        keeps the piped value out of the leading position when a later
        argument is the natural pipe target. Exactly one `_` is allowed;
        more than one is rejected since the piped value would be duplicated.
        """
        holes = [i for i, a in enumerate(args) if self._is_pipe_placeholder(a)]
        if not holes:
            return [piped] + args
        if len(holes) > 1:
            raise self.error(
                "Pipeline placeholder '_' may appear at most once per '|>' stage "
                "(found {}); the piped value fills a single slot".format(len(holes))
            )
        out = list(args)
        out[holes[0]] = piped
        return out

    def _at_declarative_sort(self) -> bool:
        tok = self.current_token
        if tok.type != TokenType.IDENTIFIER:
            return False
        return tok.value in ("sort", "sortBy", "order")

    def _at_declarative_search(self) -> bool:
        """True at `find(...)` immediately after `|>`.

        Only claimed in pipeline position and only with an argument list, so
        an ordinary `find(...)` call elsewhere is untouched.
        """
        tok = self.current_token
        return (
            tok.type == TokenType.IDENTIFIER
            and tok.value == "find"
            and self.lookahead.type == TokenType.LPAREN
        )

    def _parse_find_pipeline(self, array: Expression) -> "FindExpr":
        """Parse `xs |> find(target)`."""
        line = getattr(self.current_token, "line", 0) or 0
        self.advance()  # 'find'
        if self.current_token.type != TokenType.LPAREN:
            raise SyntaxError("Expected '(' after 'find' in pipeline")
        self.advance()
        target = self.parse_expression()
        if self.current_token.type != TokenType.RPAREN:
            raise SyntaxError("Expected ')' to close 'find(...)'")
        self.advance()
        return FindExpr(array=array, target=target, line=line)

    def _parse_sort_key(self) -> SortKey:
        """Parse `asc .field`, `desc .field`, or `.field` (asc)."""
        descending = False
        if (
            self.current_token.type == TokenType.IDENTIFIER
            and self.current_token.value in ("asc", "desc")
        ):
            descending = self.current_token.value == "desc"
            self.advance()
        if self.current_token.type != TokenType.DOT:
            raise SyntaxError(
                "Sort key expected `.field` (optionally prefixed with asc/desc)"
            )
        self.advance()
        if self.current_token.type != TokenType.IDENTIFIER:
            raise SyntaxError("Sort key expected field name after '.'")
        field = self.current_token.value
        self.advance()
        return SortKey(field=field, descending=descending)

    def _parse_sort_keys(self) -> List[SortKey]:
        """Parse `.f`, `asc .f`, or `[desc .a, asc .b]`."""
        if self.current_token.type == TokenType.LBRACKET:
            self.advance()
            keys: List[SortKey] = []
            if self.current_token.type == TokenType.RBRACKET:
                raise SyntaxError("Sort key list cannot be empty")
            while True:
                keys.append(self._parse_sort_key())
                if self.current_token.type == TokenType.COMMA:
                    self.advance()
                    continue
                break
            if self.current_token.type != TokenType.RBRACKET:
                raise SyntaxError("Expected ']' to close sort key list")
            self.advance()
            return keys
        return [self._parse_sort_key()]

    def _parse_sort_pipeline(self, array: Expression) -> SortExpr:
        """Parse `sort` / `sortBy` / `order` and trailing modifiers after `|>`."""
        if self.current_token.type != TokenType.IDENTIFIER:
            raise SyntaxError("Expected sort/sortBy/order after '|>'")
        line = getattr(self.current_token, "line", 0) or 0
        head = self.current_token.value
        self.advance()

        keys: List[SortKey] = []
        descending = False
        stable = True
        unique = False
        parallel = False
        adaptive = False
        compact = False
        general = False
        policies: List[str] = []
        entropy: Optional[str] = None

        if head == "sortBy":
            keys = self._parse_sort_keys()
        elif head in ("sort", "order"):
            if (
                self.current_token.type == TokenType.IDENTIFIER
                and self.current_token.value == "by"
            ):
                self.advance()
                keys = self._parse_sort_keys()

        # Trailing modifiers / policies / entropy
        while True:
            # Keyword tokens that double as sort policies
            if self.current_token.type == TokenType.WITH:
                self.advance()
                if (
                    self.current_token.type != TokenType.IDENTIFIER
                    or self.current_token.value != "entropy"
                ):
                    raise SyntaxError("Expected 'entropy' after 'with' in sort pipeline")
                self.advance()
                if self.current_token.type == TokenType.LPAREN:
                    self.advance()
                    if self.current_token.type == TokenType.IDENTIFIER:
                        tag = self.current_token.value
                        self.advance()
                        if tag == "seed":
                            if self.current_token.type != TokenType.COLON:
                                raise SyntaxError("Expected ':' after entropy seed")
                            self.advance()
                            if self.current_token.type != TokenType.NUMBER:
                                raise SyntaxError("Expected integer seed for entropy")
                            entropy = self.current_token.value
                            self.advance()
                        else:
                            entropy = tag
                    elif self.current_token.type == TokenType.NUMBER:
                        entropy = self.current_token.value
                        self.advance()
                    else:
                        raise SyntaxError("Invalid entropy(...) argument")
                    if self.current_token.type != TokenType.RPAREN:
                        raise SyntaxError("Expected ')' after entropy(...)")
                    self.advance()
                else:
                    entropy = "default"
                continue

            if self.current_token.type == TokenType.PARALLEL:
                parallel = True
                policies.append("parallel")
                self.advance()
                continue

            if self.current_token.type != TokenType.IDENTIFIER:
                break
            mod = self.current_token.value
            if mod in ("stable",):
                stable = True
                self.advance()
            elif mod in ("unstable",):
                stable = False
                self.advance()
            elif mod in ("descending", "desc"):
                # Global reverse. Prefer per-key `desc .field` when using `by`.
                descending = True
                self.advance()
            elif mod in ("ascending", "asc"):
                descending = False
                self.advance()
            elif mod == "unique":
                unique = True
                self.advance()
            elif mod == "adaptive":
                adaptive = True
                policies.append(mod)
                self.advance()
            elif mod == "general":
                # Escape hatch: pin the general-purpose plan and ignore every
                # hint. Exists so a benchmark can measure the plan it replaced.
                general = True
                policies.append(mod)
                self.advance()
            elif mod == "compact":
                compact = True
                policies.append(mod)
                self.advance()
            elif mod in (
                "gpu",
                "simd",
                "external",
                "streaming",
                "distributed",
                "cache",
                "realtime",
                "battery",
                "throughput",
                "approximate",
                "learned",
            ):
                policies.append(mod)
                self.advance()
            else:
                break

        return SortExpr(
            array=array,
            keys=keys,
            descending=descending,
            stable=stable,
            unique=unique,
            parallel=parallel,
            adaptive=adaptive,
            compact=compact,
            policies=policies,
            entropy=entropy,
            general=general,
            line=line,
        )

    def parse_assignment(self) -> Expression:
        # Include pipeline (`|>` / declarative sort) so expression statements
        # like `xs |> sort` and RHS forms parsed via `parse_expression` work.
        expr = self.parse_expression_without_assign()

        # Check for compound assignment: +=, -=, *=, /=
        compound_ops = {
            TokenType.PLUS_ASSIGN: "+",
            TokenType.MINUS_ASSIGN: "-",
            TokenType.STAR_ASSIGN: "*",
            TokenType.SLASH_ASSIGN: "/",
        }

        if self.current_token.type in compound_ops:
            op = compound_ops[self.current_token.type]
            self.advance()
            rhs = self.parse_assignment()

            # Transform: x += y  →  x = x + y
            if isinstance(expr, Variable):
                value = BinaryOperation(expr, op, rhs)
                return Assignment(expr.name, value)
            elif isinstance(expr, ArrayAccess):
                value = BinaryOperation(expr, op, rhs)
                return Assignment("", value, target_expr=expr)
            elif isinstance(expr, FieldAccess):
                value = BinaryOperation(expr, op, rhs)
                return Assignment("", value, target_expr=expr)
            else:
                raise SyntaxError("Invalid compound assignment target")

        if self.current_token.type == TokenType.ASSIGN:
            if isinstance(expr, Variable):
                self.advance()
                value = self.parse_assignment()
                return Assignment(expr.name, value)
            elif isinstance(expr, ArrayAccess):
                # Array element assignment: arr[i] = value
                self.advance()
                value = self.parse_assignment()
                return Assignment("", value, target_expr=expr)
            elif isinstance(expr, FieldAccess):
                # Field assignment: obj.field = value (requires mut)
                self.advance()
                value = self.parse_assignment()
                return Assignment("", value, target_expr=expr)
            else:
                raise SyntaxError("Invalid assignment target")

        return expr

    def parse_logical_or(self) -> Expression:
        # Every nested expression (parens, brackets, call args, ...) re-enters
        # here, so this is the single choke point for expression depth.
        self._enter_nesting("expression")
        try:
            return self._parse_logical_or_impl()
        finally:
            self.nesting_depth -= 1

    def _parse_logical_or_impl(self) -> Expression:
        left = self.parse_logical_and()

        while self.current_token.type == TokenType.OR:
            # English `or` and symbolic `||` share TokenType.OR; normalize
            # both to `||` so the AST matches existing typecheck/codegen.
            self.advance()
            right = self.parse_logical_and()
            left = BinaryOperation(left, "||", right)

        return left

    def parse_logical_and(self) -> Expression:
        left = self.parse_bitwise_or()

        while self.current_token.type == TokenType.AND:
            # English `and` and symbolic `&&` share TokenType.AND; normalize
            # both to `&&` so the AST matches existing typecheck/codegen.
            self.advance()
            right = self.parse_bitwise_or()
            left = BinaryOperation(left, "&&", right)

        return left

    def parse_bitwise_or(self) -> Expression:
        """Parse bitwise OR: a | b"""
        left = self.parse_bitwise_xor()

        # Note: PIPE is also used for lambdas, so we need to be careful
        # We only parse bitwise OR if we already have an expression on the left
        while self.current_token.type == TokenType.PIPE:
            # Peek ahead to distinguish lambda from bitwise OR
            # If next token is IDENTIFIER followed by COLON or PIPE, it's lambda
            # Otherwise it's bitwise OR
            self.advance()
            right = self.parse_bitwise_xor()
            left = BinaryOperation(left, "|", right)

        return left

    def parse_bitwise_xor(self) -> Expression:
        """Parse bitwise XOR: a ^ b"""
        left = self.parse_bitwise_and()

        while self.current_token.type == TokenType.CARET:
            self.advance()
            right = self.parse_bitwise_and()
            left = BinaryOperation(left, "^", right)

        return left

    def parse_bitwise_and(self) -> Expression:
        """Parse bitwise AND: a & b"""
        left = self.parse_equality()

        while self.current_token.type == TokenType.AMPERSAND:
            self.advance()
            right = self.parse_equality()
            left = BinaryOperation(left, "&", right)

        return left

    def parse_equality(self) -> Expression:
        left = self.parse_comparison()

        while self.current_token.type in [TokenType.EQUALS, TokenType.NOT_EQUALS]:
            op = self.current_token.value
            op_line = self.current_token.line
            self.advance()
            right = self.parse_comparison()
            left = BinaryOperation(left, op, right, line=op_line)

        return left

    def parse_comparison(self) -> Expression:
        left = self.parse_shift()

        while self.current_token.type in [
            TokenType.LESS,
            TokenType.GREATER,
            TokenType.LESS_EQUAL,
            TokenType.GREATER_EQUAL,
        ]:
            op = self.current_token.value
            op_line = self.current_token.line
            self.advance()
            right = self.parse_shift()
            left = BinaryOperation(left, op, right, line=op_line)

        return left

    def parse_shift(self) -> Expression:
        """Parse shift operators: a << b, a >> b"""
        left = self.parse_term()

        while self.current_token.type in [TokenType.LSHIFT, TokenType.RSHIFT]:
            op = self.current_token.value
            self.advance()
            right = self.parse_term()
            left = BinaryOperation(left, op, right)

        return left

    def parse_term(self) -> Expression:
        left: Expression = self.parse_factor()

        while self.current_token.type in [TokenType.PLUS, TokenType.MINUS]:
            op = self.current_token.value
            op_line = self.current_token.line
            self.advance()
            right = self.parse_factor()

            # Check for string concatenation
            if (isinstance(left, Literal) and left.type.name == "string") or (
                isinstance(right, Literal) and right.type.name == "string"
            ):
                # String concatenation - keep as BinaryOperation, MLIR generator will handle it
                left = BinaryOperation(left, op, right, line=op_line)
            else:
                # Numeric addition
                left = BinaryOperation(left, op, right, line=op_line)

        return left

    def parse_factor(self) -> Expression:
        left = self.parse_cast()

        while self.current_token.type in [
            TokenType.STAR,
            TokenType.SLASH,
            TokenType.PERCENT,
        ]:
            op = self.current_token.value
            op_line = self.current_token.line
            self.advance()
            right = self.parse_cast()
            left = BinaryOperation(left, op, right, line=op_line)

        return left

    def parse_cast(self) -> Expression:
        expr = self.parse_unary()
        while self.current_token.type == TokenType.AS:
            self.advance()
            target_type = self.parse_type()
            expr = CastExpression(expr, target_type)
        while self.current_token.type == TokenType.QUESTION:
            self.advance()
            expr = TryExpr(expr)
        return expr

    def parse_unary(self) -> Expression:
        if self.current_token.type == TokenType.DBG:
            # `dbg expr` evaluates to expr and, as a side effect, prints it.
            # Lowered to a builtin call handled by each backend.
            self.advance()
            self._enter_nesting("expression")
            try:
                operand = self.parse_unary()
            finally:
                self.nesting_depth -= 1
            return FunctionCall("__flow_dbg", [operand])

        if self.current_token.type in [
            TokenType.MINUS,
            TokenType.NOT,
            TokenType.TILDE,
            TokenType.AMPERSAND,
            TokenType.STAR,
        ]:
            op = self.current_token.value
            self.advance()
            self._enter_nesting("expression")
            try:
                operand = self.parse_unary()
            finally:
                self.nesting_depth -= 1
            return UnaryOperation(op, operand)

        return self.parse_primary()

    def parse_simple_expression(self) -> Expression:
        """Parse simple expressions for vector literals (no assignment, no complex ops)"""
        return self.parse_primary()

    def parse_primary(self) -> Expression:
        if self.current_token.type == TokenType.NUMBER:
            value = self.current_token.value
            self.advance()
            # Infer float vs int from token text.
            # This keeps the language ergonomic for SIMD examples that use 0.0/1.0.
            is_hex = isinstance(value, str) and value.startswith("0x")
            if not is_hex and isinstance(value, str) and ("." in value or "e" in value.lower()):
                return Literal(value, Type("f32"))
            elif is_hex:
                # Handle hex literals - convert to integer
                hex_value = int(value, 16)
                return Literal(str(hex_value), Type("i32"))
            return Literal(value, Type("i32"))  # Default to i32 for numbers

        elif self.current_token.type == TokenType.BOOLEAN:
            value = self.current_token.value
            self.advance()
            return Literal(value, Type("bool"))

        elif self.current_token.type == TokenType.STRING_LITERAL:
            value = self.current_token.value
            self.advance()
            if "${" in value:
                return self._parse_interpolated_string(value)
            return Literal(value, Type("string"))

        elif self.current_token.type == TokenType.NULL:
            self.advance()
            # null is a pointer literal with type ptr<void>
            return Literal(
                "null", Type("ptr_void", is_pointer=True, element_type=Type("void"))
            )

        elif self.current_token.type == TokenType.SELF:
            # 'self' in method body - treated as a variable
            self.advance()
            # Handle self.field or self.method()
            if self.current_token.type == TokenType.DOT:
                return self.parse_field_access("self")
            return Variable("self")

        elif self.current_token.type == TokenType.LESS:
            # Vector literal: <1.0, 2.0, 3.0, 4.0>
            self.advance()
            elements = []

            if self.current_token.type != TokenType.GREATER:
                # Parse simple expressions (literals, variables, function calls)
                elements.append(self.parse_simple_expression())
                while self.current_token.type == TokenType.COMMA:
                    self.advance()
                    elements.append(self.parse_simple_expression())

            self.expect(TokenType.GREATER)
            return VectorLiteral(elements)

        elif self.current_token.type == TokenType.LBRACKET:
            self.advance()
            elements = []

            if self.current_token.type != TokenType.RBRACKET:
                elements.append(self.parse_expression_without_assign())
                while self.current_token.type == TokenType.COMMA:
                    self.advance()
                    elements.append(self.parse_expression_without_assign())

            self.expect(TokenType.RBRACKET)
            return ArrayLiteral(elements)

        elif self.current_token.type in (
            TokenType.IDENTIFIER,
            # Soft keywords: `and`/`or` are infix logical operators, but proof
            # corpora also use them as bit-op function names (`and(a, b)`).
            # In primary position they behave like identifiers.
            TokenType.AND,
            TokenType.OR,
        ):
            name = self.current_token.value
            self.advance()

            if self.current_token.type == TokenType.LPAREN:
                # Allow postfix chains on call results: f()[i].x, f().m()
                return self.parse_postfix_chain(self.parse_function_call(name))
            elif self.current_token.type == TokenType.LESS:
                # Could be:
                # 1. Generic type constructor: array<i32>(10)
                # 2. Generic struct literal: Box<i32> { ... }
                # 3. Comparison: x < y (but then next token wouldn't be identifier)

                # Save state to backtrack if needed
                save_pos = self.lexer.pos
                save_line = self.lexer.line
                save_col = self.lexer.column
                save_current = self.current_token
                save_lookahead = self.lookahead

                try:
                    self.advance()  # consume <

                    # Parse type arguments
                    type_args = [self.parse_type()]
                    while self.current_token.type == TokenType.COMMA:
                        self.advance()
                        type_args.append(self.parse_type())

                    self.expect(TokenType.GREATER)

                    # Construct mangled name: Box<i32> -> Box_i32
                    type_args_str = "_".join(t.name for t in type_args)
                    mangled_name = f"{name}_{type_args_str}"

                    if self.current_token.type == TokenType.LPAREN:
                        # Generic function call: make_box<i32>(42)
                        return self.parse_postfix_chain(
                            self.parse_function_call(mangled_name)
                        )
                    elif self.current_token.type == TokenType.LBRACE:
                        # Generic struct literal: Box<i32> { ... }
                        return self.parse_struct_literal(mangled_name)
                    else:
                        # Just a generic type in expression position (unusual but valid)
                        return Variable(mangled_name)
                except SyntaxError:
                    # Restore state - this was probably a comparison
                    self.lexer.pos = save_pos
                    self.lexer.line = save_line
                    self.lexer.column = save_col
                    self.current_token = save_current
                    self.lookahead = save_lookahead
                    return Variable(name)
            elif self.current_token.type == TokenType.LBRACE:
                # Try to parse as struct literal - if it fails, it's not a struct literal
                # Save state first (including lexer position)
                save_current = self.current_token
                save_lookahead = self.lookahead
                save_lexer_pos = self.lexer.pos
                save_lexer_line = self.lexer.line
                save_lexer_column = self.lexer.column

                try:
                    result = self.parse_struct_literal(name)
                    return result
                except SyntaxError:
                    # If struct literal parsing fails, restore ALL state and treat as variable
                    self.current_token = save_current
                    self.lookahead = save_lookahead
                    self.lexer.pos = save_lexer_pos
                    self.lexer.line = save_lexer_line
                    self.lexer.column = save_lexer_column
                    return Variable(name)
            elif self.current_token.type == TokenType.DOT:
                return self.parse_field_access(name)
            elif self.current_token.type == TokenType.DOUBLE_COLON:
                # Effect call: EffectName::operation(args)
                self.advance()  # consume ::
                operation = self.expect(TokenType.IDENTIFIER).value
                self.expect(TokenType.LPAREN)

                arguments = []
                if self.current_token.type != TokenType.RPAREN:
                    arguments.append(self.parse_expression_without_assign())
                    while self.current_token.type == TokenType.COMMA:
                        self.advance()
                        arguments.append(self.parse_expression_without_assign())

                self.expect(TokenType.RPAREN)
                return EffectCall(name, operation, arguments)
            elif self.current_token.type == TokenType.LBRACKET:
                # Array access: arr[index] with chained field/index/method access
                return self.parse_postfix_chain(Variable(name))
            else:
                return Variable(name)

        elif self.current_token.type == TokenType.LBRACE and self.lookahead.type == TokenType.DOTDOT:
            # Anonymous record update: `{ ..person, age: 31 }` (Roc syntax).
            # Flow blocks are statements, never expressions, so a `{ ..` in
            # expression position is unambiguous.
            return self.parse_struct_literal("")

        elif self.current_token.type == TokenType.LPAREN:
            self.advance()
            expr = self.parse_expression_without_assign()
            self.expect(TokenType.RPAREN)
            # Allow postfix chains on parenthesized expressions: (p)[0].x
            return self.parse_postfix_chain(expr)

        elif self.current_token.type == TokenType.PIPE:
            # Lambda expression: |x: i32, y: i32| -> i32 { x + y }
            # Or shorthand: |x| x * 2
            return self.parse_lambda()

        else:
            raise SyntaxError(
                f"Unexpected token in expression: {self.current_token.type}"
            )
    def parse_function_call(self, name: str) -> FunctionCall:
        self.expect(TokenType.LPAREN)
        arguments = []

        if self.current_token.type != TokenType.RPAREN:
            arguments.append(self.parse_expression_without_assign())
            while self.current_token.type == TokenType.COMMA:
                self.advance()
                arguments.append(self.parse_expression_without_assign())

        self.expect(TokenType.RPAREN)
        return FunctionCall(name, arguments)

    def _collect_free_variables(self, node: Any, param_names: set, found: Optional[set] = None) -> List[str]:
        """Collect variable names referenced in an expression/block but not bound.

        `param_names` holds every name bound at this point: lambda
        parameters, locals declared earlier in the enclosing block, and
        loop variables. Names bound inside the body never count as
        captures. `break`/`continue` are dedicated statement nodes (not
        `Variable`s), so they never reach this branch.
        """
        if found is None:
            found = set()
        if isinstance(node, Variable):
            if node.name not in param_names and node.name != "self":
                found.add(node.name)
        elif isinstance(node, Lambda):
            # A nested lambda's free names are free here too unless bound
            # by the nested lambda's own parameters.
            inner_bound = set(param_names) | {p.name for p in node.parameters}
            self._collect_free_variables(node.body, inner_bound, found)
        elif isinstance(node, Block):
            # Locals declared in the block bind the name for the
            # statements that follow; the initializer itself is evaluated
            # before the binding exists.
            bound = set(param_names)
            for stmt in node.statements:
                if isinstance(stmt, VarDecl):
                    if stmt.initializer is not None:
                        self._collect_free_variables(stmt.initializer, bound, found)
                    bound.add(stmt.name)
                else:
                    self._collect_free_variables(stmt, bound, found)
        elif isinstance(node, (BinaryOperation, UnaryOperation, CastExpression, TryExpr)):
            if isinstance(node, BinaryOperation):
                self._collect_free_variables(node.left, param_names, found)
                self._collect_free_variables(node.right, param_names, found)
            elif isinstance(node, UnaryOperation):
                self._collect_free_variables(node.operand, param_names, found)
            elif isinstance(node, CastExpression):
                self._collect_free_variables(node.expr, param_names, found)
            elif isinstance(node, TryExpr):
                self._collect_free_variables(node.operand, param_names, found)
        elif isinstance(node, FunctionCall):
            # The callee name is collected too so a closure variable called
            # inside a nested lambda gets captured. The C generator drops
            # names that are not locals in the creation scope (global
            # functions, builtins), so plain calls are unaffected.
            if node.name not in param_names and node.name != "self":
                found.add(node.name)
            for arg in node.arguments:
                self._collect_free_variables(arg, param_names, found)
        elif isinstance(node, (FieldAccess, ArrayAccess)):
            self._collect_free_variables(node.object if hasattr(node, 'object') else node.array, param_names, found)
            if isinstance(node, ArrayAccess):
                self._collect_free_variables(node.index, param_names, found)
        elif isinstance(node, StructLiteral):
            for _fname, fval in node.fields:
                self._collect_free_variables(fval, param_names, found)
        elif isinstance(node, RecordUpdate):
            self._collect_free_variables(node.base, param_names, found)
            for _fname, fval in node.updates:
                self._collect_free_variables(fval, param_names, found)
        elif isinstance(node, (ArrayLiteral, VectorLiteral)):
            for elem in node.elements:
                self._collect_free_variables(elem, param_names, found)
        elif isinstance(node, StringInterpolation):
            for part in node.parts:
                self._collect_free_variables(part, param_names, found)
        elif isinstance(node, SortExpr):
            self._collect_free_variables(node.array, param_names, found)
        elif isinstance(node, FindExpr):
            self._collect_free_variables(node.array, param_names, found)
            self._collect_free_variables(node.target, param_names, found)
        elif isinstance(node, (IfStatement, WhileStatement, ForStatement, MatchStatement)):
            if isinstance(node, IfStatement):
                self._collect_free_variables(node.condition, param_names, found)
                self._collect_free_variables(node.then_block, param_names, found)
                for _, blk in node.elif_blocks:
                    self._collect_free_variables(blk, param_names, found)
                if node.else_block:
                    self._collect_free_variables(node.else_block, param_names, found)
            elif isinstance(node, WhileStatement):
                self._collect_free_variables(node.condition, param_names, found)
                self._collect_free_variables(node.body, param_names, found)
            elif isinstance(node, ForStatement):
                self._collect_free_variables(node.range_start, param_names, found)
                self._collect_free_variables(node.range_end, param_names, found)
                if node.step:
                    self._collect_free_variables(node.step, param_names, found)
                # The loop variable is bound within the body.
                self._collect_free_variables(
                    node.body, set(param_names) | {node.variable}, found
                )
            elif isinstance(node, MatchStatement):
                self._collect_free_variables(node.value, param_names, found)
                for case in node.cases:
                    if case.guard:
                        self._collect_free_variables(case.guard, param_names, found)
                    self._collect_free_variables(case.body, param_names, found)
                if node.default_case:
                    self._collect_free_variables(node.default_case, param_names, found)
        elif isinstance(node, (VarDecl, ReturnStatement, Assignment, DeferStatement)):
            if isinstance(node, VarDecl) and node.initializer:
                self._collect_free_variables(node.initializer, param_names, found)
            elif isinstance(node, ReturnStatement) and node.value:
                self._collect_free_variables(node.value, param_names, found)
            elif isinstance(node, Assignment):
                self._collect_free_variables(node.value, param_names, found)
                if node.target_expr:
                    self._collect_free_variables(node.target_expr, param_names, found)
            elif isinstance(node, DeferStatement):
                self._collect_free_variables(node.expr, param_names, found)
        elif isinstance(node, (MethodCall, EffectCall)):
            # Receivers are skipped: for effect calls the receiver is an
            # effect name, and capturing it would corrupt codegen.
            for arg in node.arguments:
                self._collect_free_variables(arg, param_names, found)
        return sorted(found)

    def parse_lambda(self) -> Lambda:
        """Parse lambda expression: |x: i32, y: i32| -> i32 { x + y } or |x| x * 2"""
        self.expect(TokenType.PIPE)

        # Parse parameters
        parameters = []
        if self.current_token.type != TokenType.PIPE:
            # First parameter
            param_name = self.expect(TokenType.IDENTIFIER).value
            param_type = None
            if self.current_token.type == TokenType.COLON:
                self.advance()
                param_type = self.parse_type()
            parameters.append(Parameter(param_name, param_type or Type("auto")))

            # Additional parameters
            while self.current_token.type == TokenType.COMMA:
                self.advance()
                param_name = self.expect(TokenType.IDENTIFIER).value
                param_type = None
                if self.current_token.type == TokenType.COLON:
                    self.advance()
                    param_type = self.parse_type()
                parameters.append(Parameter(param_name, param_type or Type("auto")))

        self.expect(TokenType.PIPE)

        # Parse optional return type
        return_type = None
        if self.current_token.type == TokenType.ARROW:
            self.advance()
            return_type = self.parse_type()

        # Parse body - either block or single expression
        if self.current_token.type == TokenType.LBRACE:
            body = self.parse_block()
        else:
            # Single expression body
            body = self.parse_expression_without_assign()

        param_names = {p.name for p in parameters}
        captures = self._collect_free_variables(body, param_names)
        return Lambda(parameters, return_type, body, captures=captures)

    def parse_struct_literal(self, struct_name: str) -> "Expression":
        # If current token is LBRACE, expect it and advance
        # Otherwise, we're already positioned correctly
        if self.current_token.type == TokenType.LBRACE:
            self.expect(TokenType.LBRACE)

        # Record update form: `Name { ..expr, field: value }` - copy `expr`
        # and override the listed fields.
        if self.current_token.type == TokenType.DOTDOT:
            self.advance()
            base = self.parse_expression_without_assign()
            updates: List[tuple] = []
            while self.current_token.type == TokenType.COMMA:
                self.advance()
                if self.current_token.type == TokenType.RBRACE:
                    break
                field_name = self.expect(TokenType.IDENTIFIER).value
                self.expect(TokenType.COLON)
                field_value = self.parse_expression_without_assign()
                updates.append((field_name, field_value))
            self.expect(TokenType.RBRACE)
            return RecordUpdate(base, updates)

        fields = []

        while self.current_token.type != TokenType.RBRACE:
            if self.current_token.type == TokenType.EOF:
                raise SyntaxError("Unterminated struct literal: expected '}' before end of file")
            field_name = self.expect(TokenType.IDENTIFIER).value
            self.expect(TokenType.COLON)
            field_value = self.parse_expression_without_assign()
            fields.append((field_name, field_value))

            if self.current_token.type == TokenType.COMMA:
                self.advance()

        self.expect(TokenType.RBRACE)
        return StructLiteral(struct_name, fields)

    def parse_field_access(self, object_name: str) -> Expression:
        # Delegate to the unified postfix chain so field access, indexing,
        # and method calls compose arbitrarily: a.b, a.b[i].c, a.b().c[0].d()
        return self.parse_postfix_chain(Variable(object_name))

    def parse_postfix_chain(self, expr: Expression) -> Expression:
        """Apply postfix operators (field access, indexing, method calls) to an
        already-parsed base expression, chaining arbitrarily.

        Handles: a.b.c, a[i], a[i].b, a.b[i].c, a[i].m(x), a.b().c, f()[i].x
        """
        while (
            self.current_token.type == TokenType.DOT
            or self.current_token.type == TokenType.LBRACKET
        ):
            if self.current_token.type == TokenType.DOT:
                self.advance()  # consume .
                member_name = self.expect(TokenType.IDENTIFIER).value

                if self.current_token.type == TokenType.LPAREN:
                    # Method call: expr.method(args)
                    self.expect(TokenType.LPAREN)
                    arguments: List[Expression] = []

                    if self.current_token.type != TokenType.RPAREN:
                        arguments.append(self.parse_expression_without_assign())
                        while self.current_token.type == TokenType.COMMA:
                            self.advance()
                            arguments.append(self.parse_expression_without_assign())

                    self.expect(TokenType.RPAREN)
                    expr = MethodCall(expr, member_name, arguments)
                else:
                    expr = FieldAccess(expr, member_name)
            elif self.current_token.type == TokenType.LBRACKET:
                self.advance()  # consume [
                index = self.parse_expression_without_assign()
                if self.current_token.type == TokenType.DOTDOT:
                    # Slice expression `base[start..end]` produces a span.
                    self.advance()  # consume ..
                    end = self.parse_expression_without_assign()
                    self.expect(TokenType.RBRACKET)
                    expr = SliceExpr(expr, index, end)
                else:
                    self.expect(TokenType.RBRACKET)
                    expr = ArrayAccess(expr, index)

        return expr

    def _parse_interpolated_string(self, literal_value: str) -> "Expression":
        """Parse a string literal containing `${...}` interpolations.

        The lexer tokenizes the entire quoted string (including `${...}`
        segments) as one STRING_LITERAL token because the interpolated
        expression source has no unescaped quotes. Here we split it back out
        and build a left-associated `+` concatenation chain:

            `"a ${b} c"`  ->  `"a " + b + " c"`

        Both backends already lower string `+` to concatenation, so no
        codegen changes are required for interpolation to work.
        """
        content = literal_value[1:-1]
        parts: List["Expression"] = []

        cursor = 0
        i = 0
        while i < len(content):
            if content.startswith("${", i):
                # Emit any literal text accumulated before this interpolation.
                if i > cursor:
                    lit = content[cursor:i]
                    parts.append(Literal(f'"{lit}"', Type("string")))
                # Find the matching closing brace (no nested interpolations).
                j = content.find("}", i + 2)
                if j == -1:
                    raise SyntaxError("Unterminated interpolation: missing '}' in string")
                inner_src = content[i + 2:j]
                if not inner_src.strip():
                    raise SyntaxError("Empty interpolation '${}' is not allowed")
                try:
                    sub_lexer = Lexer(inner_src)
                    sub_parser = Parser(sub_lexer)
                    inner = sub_parser.parse_expression_without_assign()
                except SyntaxError as e:
                    raise SyntaxError(
                        f"Invalid expression in string interpolation '${inner_src}': {e}"
                    )
                parts.append(inner)
                cursor = j + 1
                i = j + 1
            else:
                i += 1

        # Trailing literal text after the last interpolation.
        if cursor < len(content):
            lit = content[cursor:]
            parts.append(Literal(f'"{lit}"', Type("string")))

        if not parts:
            return Literal('""', Type("string"))

        # Left-associate the concatenation chain.
        result = parts[0]
        for part in parts[1:]:
            result = BinaryOperation(result, "+", part)
        return result


def parse_flow_code(code: str) -> List[Any]:
    lexer = Lexer(code)
    parser = Parser(lexer)
    return parser.parse()


if __name__ == "__main__":
    # Test code
    test_code = """
function add(a: i32, b: i32) -> i32 {
    let result: i32 = a + b
    return result
}

function factorial(n: i32) -> i32 {
    if n <= 1 {
        return 1
    } else {
        return n * factorial(n - 1)
    }
}
"""

    try:
        functions = parse_flow_code(test_code)
        print("Parsed successfully!")
        for func in functions:
            print(f"Function: {func.name}")
            print(
                f"  Parameters: {[p.name + ':' + p.type.name for p in func.parameters]}"
            )
            print(f"  Return type: {func.return_type.name}")
            print(f"  Statements: {len(func.body.statements)}")
    except SyntaxError as e:
        print(f"Syntax error: {e}")
