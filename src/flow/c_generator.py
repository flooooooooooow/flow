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

from typing import Any, Dict, List, Optional, Tuple

from .parser import (
    ArrayAccess,
    ArrayLiteral,
    Assignment,
    BinaryOperation,
    Block,
    BreakStatement,
    CapabilityDecl,
    CapabilityMethod,
    ConstDecl,
    ContinueStatement,
    DeferStatement,
    EffectCall,
    EffectDecl,
    EnumDecl,
    Expression,
    CastExpression,
    ExpectStatement,
    RecordUpdate,
    FieldAccess,
    FunctionCall,
    FunctionDecl,
    HandleStatement,
    LayoutStatement,
    IfStatement,
    IfExpression,
    ImplDecl,
    Lambda,
    Literal,
    MatchStatement,
    MethodCall,
    ReturnStatement,
    FindExpr,
    SortExpr,
    SortKey,
    StaticDecl,
    Statement,
    StructDecl,
    StructLiteral,
    StructPattern,
    OrPattern,
    ListPattern,
    TraitDecl,
    TryExpr,
    Type,
    TypeAliasDecl,
    DistinctTypeDecl,
    ExternTypeDecl,
    CIncludeDecl,
    CImportDecl,
    CEmbedDecl,
    UnaryOperation,
    VarDecl,
    Variable,
    VectorLiteral,
    WhileStatement,
    ForStatement,
    SliceExpr,
    is_span_type_name,
    span_is_mutable,
    span_element_name,
    make_span_type,
)
from .overload import OverloadResolver

# Importing ordering_plans registers the sort / search implementations with the
# selector. Without it the registry is empty and every site raises.
from . import ordering_plans as _ordering_plans  # noqa: F401
from .ordering_hints import annotate_ordering_hints
from .plan_selector import Facts, Selection, select
from .attributes import (
    normalize_target_spec,
    parse_attribute,
    validate_target_spec,
)

import re

_C_IDENT_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')

# C reserved words that must not be used as identifiers
_C_RESERVED = frozenset({
    'auto', 'break', 'case', 'char', 'const', 'continue', 'default', 'do',
    'double', 'else', 'enum', 'extern', 'float', 'for', 'goto', 'if',
    'inline', 'int', 'long', 'register', 'restrict', 'return', 'short',
    'signed', 'sizeof', 'static', 'struct', 'switch', 'typedef', 'union',
    'unsigned', 'void', 'volatile', 'while', '_Bool', '_Complex', '_Imaginary',
})


def _sanitize_identifier(name: str) -> str:
    """Sanitize a Flow identifier for safe use in generated C code.

    Replaces any character that is not [A-Za-z0-9_] with an underscore,
    ensuring the result is a valid C identifier.  This prevents code
    injection via crafted Flow identifier names.
    """
    if not name:
        return "_empty"
    # Replace non-identifier characters
    safe = re.sub(r'[^A-Za-z0-9_]', '_', name)
    # Ensure it starts with a letter or underscore
    if safe[0].isdigit():
        safe = '_' + safe
    # Avoid C reserved words
    if safe in _C_RESERVED:
        safe = '_flow_' + safe
    return safe


def _c_ident(name: str) -> str:
    """Return a safe C identifier for any Flow name."""
    return _sanitize_identifier(name)


class CGenerator:
    def __init__(
        self,
        *,
        source_file: str | None = None,
        debug_info: bool = False,
        bounds_check: bool = True,
        no_heap: bool = False,
        strict_effects: bool = False,
        library: bool = False,
    ) -> None:
        self._indent = 0
        self._structs = {}  # name -> dict of field_name -> field_type
        self._enums = {}  # name -> EnumDecl
        self._enum_variant_owner = {}  # "Enum_Variant" -> "Enum" (for path/const match patterns)
        self._var_types = {}  # name -> Type
        self._source_file = source_file
        self._debug_info = debug_info
        self._strict_effects = strict_effects
        self._library = library
        self._bounds_check = bounds_check
        self._no_heap = no_heap
        self._uses_parallel_for = False
        self._uses_fiber_main = False  # wrap main() on a fiber for mid-function suspend
        self._current_return_type: Type | None = None
        self._current_tco_fn: str | None = None
        self._current_tco_params: List[str] = []
        
        # Effect system tracking
        self._effects = {}  # effect_name -> EffectDecl
        self._capabilities = {}  # capability_name -> CapabilityDecl
        self._impl_methods = {}  # (type_name, method_name) -> [Type_Trait_method]
        self._effect_handler_stack = [{}]  # Stack of {effect_name -> capability_name}
        self._lambda_depth = 0  # >0 while generating a lambda body (closures may outlive the enclosing handle block)
        
        # Function overload resolution
        self._overload_resolver = OverloadResolver()
        self._mangled_names = {}  # original fn -> mangled name

        # Lambda/closure lowering state
        self._lambda_counter = 0
        self._pending_lambdas = []  # (name, ret_c, params, body_lines)
        self._pending_env_structs = []  # typedef lines for env/closure/fn types
        self._pending_sort_helpers: List[str] = []  # full C function source blocks
        self._sort_helper_keys: set = set()  # dedupe keys for emitted helpers
        self._pending_find_helpers: List[str] = []  # `|> find` search helpers
        self._find_helper_keys: set = set()
        self._pending_order_helpers: List[str] = []  # IEEE totalOrder comparators
        self._order_helper_keys: set = set()
        self._uses_complex: bool = False
        # One record per declarative selection site, in emission order. The
        # `--explain` report is a rendering of this list.
        self._selections: List[Selection] = []
        self._current_fn_name = ""
        self._closure_vars = {}  # var name -> lambda info (capturing lambdas)
        self._fnptr_vars = {}  # var name -> lambda info (non-capturing lambdas)
        self._fn_fat_vars = set()  # vars typed as (T)->R fat-pointer closures
        self._pending_fn_bridges = []  # static bridge fns for non-capturing → fat
        self._fn_typedefs_emitted = set()
        self._capture_stack = []  # sets of captured names, one per nested lambda body
        self._const_names = set()  # file-scope constants (reachable without capture)
        self._static_names = set()  # file-scope module statics (reachable without capture)
        self._lambda_insert_idx = None  # where lambda definitions get spliced in
        self._last_lambda_info = None

        # Spans (docs/language/spans.md): one two-word typedef per
        # (element, mutability) pair, emitted on demand.
        self._span_typedefs_emitted: set = set()
        self._pending_span_typedefs: List[str] = []

    def _i(self) -> str:
        return "    " * self._indent
    
    def _type_to_string(self, t: Type) -> str:
        """Convert a Type to a string for overload resolution."""
        if t is None:
            return "void"
        if isinstance(t, str):
            return t
        if isinstance(t, Type):
            return t.name
        return str(t)
    
    def _printf_format_for_type_name(self, type_name: str | None) -> str:
        if not type_name:
            return "%g"
        if type_name == "string":
            return "%s"
        if type_name in ["f32", "f64"]:
            return "%f"
        if type_name in ["i32", "i64", "u32", "u64", "bool"]:
            if type_name == "i64":
                return "%lld"
            if type_name == "u64":
                return "%llu"
            if type_name == "u32":
                return "%u"
            return "%d"
        return "%g"
    
    def _print_type_name(self, expr: Expression) -> str | None:
        """Type name to pick a printf conversion for, or None if unknown.

        Every expression form other than a literal or a variable goes
        through `_infer_expr_type`, so `print(a + b)` and `print(xs[i])`
        get the same conversion as `print(a)`.
        """
        if isinstance(expr, Literal):
            return expr.type.name
        if isinstance(expr, Variable):
            if expr.name in self._var_types:
                return self._var_types[expr.name].name
            return None
        inferred = self._infer_expr_type(expr)
        return inferred.name if inferred else None

    def _printf_for_expr(self, expr: Expression, *, newline: bool) -> str:
        type_name = self._print_type_name(expr)
        # Complex numbers: print as (re + im j) since printf has no
        # complex format specifier.
        if type_name in ("c64", "c128"):
            expr_str = self._gen_expr(expr)
            suffix = "\\n" if newline else ""
            if type_name == "c64":
                return (f'FLOW_LOG("(%f + %f j){suffix}", '
                        f'crealf({expr_str}), cimagf({expr_str}))')
            return (f'FLOW_LOG("(%f + %f j){suffix}", '
                    f'creal({expr_str}), cimag({expr_str}))')
        expr_str = self._gen_expr(expr)
        fmt = self._printf_format_for_type_name(type_name)
        if newline:
            fmt = f"{fmt}\\n"
        return f'FLOW_LOG("{fmt}", {expr_str})'

    def _gen_stringify_expr(self, expr: Expression) -> str:
        """Render a non-string expression as a `const char*` for use in
        string concatenation (e.g. `"Average time: " + avg_time`). Formats
        the value with the printf conversion appropriate for its inferred
        type into a small stack buffer via a GNU statement expression.
        """
        inferred = self._infer_expr_type(expr)
        type_name = inferred.name if inferred else None
        expr_c = self._gen_expr(expr)
        if type_name == "bool":
            return f"({expr_c} ? \"true\" : \"false\")"
        fmt = self._printf_format_for_type_name(type_name)
        buf = f"_flow_strval_{id(expr) & 0xFFFFFF}"
        return f'({{ char {buf}[64]; snprintf({buf}, sizeof({buf}), "{fmt}", {expr_c}); {buf}; }})'

    def _gen_print_call(self, arguments: list, *, newline: bool) -> str:
        """Shared implementation for print/println intrinsics."""
        if len(arguments) == 0:
            return 'FLOW_LOG_EMPTY("\\n")' if newline else ''
        if len(arguments) == 1:
            # Note: `print(a + b)` used to emit the bare expression, which C
            # evaluates and discards, so the call printed nothing at all.
            return self._printf_for_expr(arguments[0], newline=newline)
        # Multiple arguments - print all with spaces
        parts = []
        for i, arg in enumerate(arguments):
            prefix = ' ' if i > 0 else ''
            expr_str = self._gen_expr(arg)
            fmt = self._printf_format_for_type_name(self._print_type_name(arg))
            parts.append(f'FLOW_LOG("{prefix}{fmt}", {expr_str})')
        if newline:
            parts.append('FLOW_LOG_EMPTY("\\n")')
        return '; '.join(parts)

    def _type_uses_complex(self, t) -> bool:
        """Check if a Type references c64 or c128 (directly or in element/array types)."""
        if t is None:
            return False
        if t.name in ("c64", "c128"):
            return True
        if getattr(t, 'element_type', None) is not None:
            if self._type_uses_complex(t.element_type):
                return True
        if getattr(t, 'return_type', None) is not None:
            if self._type_uses_complex(t.return_type):
                return True
        for pt in getattr(t, 'param_types', []) or []:
            if self._type_uses_complex(pt):
                return True
        for ta in getattr(t, 'type_args', []) or []:
            if self._type_uses_complex(ta):
                return True
        return False

    def _expr_uses_complex(self, expr) -> bool:
        """Recursively check if an expression references complex constructors."""
        if expr is None:
            return False
        # FunctionCall: check name and all arguments
        if hasattr(expr, 'name') and hasattr(expr, 'arguments'):
            if expr.name in ('c64', 'c128', 'creal', 'cimag', 'cabs', 'carg',
                             'conj', 'cexp', 'clog', 'csqrt', 'cpow'):
                return True
            for arg in (expr.arguments or []):
                if self._expr_uses_complex(arg):
                    return True
        # Check sub-expressions
        for attr in ('left', 'right', 'operand', 'value', 'expr', 'object',
                     'array', 'target', 'target_expr', 'body', 'condition',
                     'then_branch', 'else_branch'):
            sub = getattr(expr, attr, None)
            if sub is not None and self._expr_uses_complex(sub):
                return True
        # Check list-type attributes
        for attr in ('elements', 'arguments', 'fields', 'members', 'statements'):
            items = getattr(expr, attr, None)
            if items:
                for item in items:
                    if self._expr_uses_complex(item):
                        return True
        return False

    def _scan_for_complex(self, functions, structs, type_aliases,
                          distinct_types, statics) -> None:
        """Pre-scan declarations to detect c64/c128 usage."""
        for fn in functions:
            if self._type_uses_complex(fn.return_type):
                self._uses_complex = True
                return
            for p in (fn.parameters or []):
                if self._type_uses_complex(p.type):
                    self._uses_complex = True
                    return
            # Check function body statements for complex constructor calls
            body = fn.body
            if body is not None:
                stmts = body.statements if hasattr(body, 'statements') else body
                for stmt in (stmts or []):
                    if self._stmt_uses_complex(stmt):
                        self._uses_complex = True
                        return
        for s in (structs or []):
            for f in (s.fields or []):
                if self._type_uses_complex(f.type):
                    self._uses_complex = True
                    return
        for ta in (type_aliases or []):
            if self._type_uses_complex(getattr(ta, 'base_type', None) or getattr(ta, 'target_type', None)):
                self._uses_complex = True
                return
        for dt in (distinct_types or []):
            if self._type_uses_complex(dt.base_type):
                self._uses_complex = True
                return
        for st in (statics or []):
            if self._type_uses_complex(st.type):
                self._uses_complex = True
                return

    def _stmt_uses_complex(self, stmt) -> bool:
        """Check if a statement references complex types or constructors."""
        if stmt is None:
            return False
        # Check type annotations on let/const/var declarations
        for attr in ('type', 'var_type', 'value_type'):
            t = getattr(stmt, attr, None)
            if t is not None and self._type_uses_complex(t):
                return True
        # Check expressions in the statement
        for attr in ('value', 'expr', 'condition', 'target',
                     'then_branch', 'else_branch', 'iterator', 'iterable',
                     'start', 'end', 'step'):
            sub = getattr(stmt, attr, None)
            if sub is not None and self._expr_uses_complex(sub):
                return True
            if sub is not None and self._stmt_uses_complex(sub):
                return True
        # Check Block-typed sub-statements (then_block, else_block, body)
        for attr in ('then_block', 'else_block', 'body'):
            blk = getattr(stmt, attr, None)
            if blk is not None:
                if hasattr(blk, 'statements'):
                    for item in blk.statements:
                        if self._stmt_uses_complex(item):
                            return True
                elif isinstance(blk, list):
                    for item in blk:
                        if self._stmt_uses_complex(item):
                            return True
        # Check elif_blocks: list of (expr, Block) tuples
        elifs = getattr(stmt, 'elif_blocks', None)
        if elifs:
            for cond, blk in elifs:
                if self._expr_uses_complex(cond):
                    return True
                if hasattr(blk, 'statements'):
                    for item in blk.statements:
                        if self._stmt_uses_complex(item):
                            return True
        # Check statement lists (body may be a Block with .statements)
        for attr in ('statements', 'then_body', 'else_body', 'branches'):
            items = getattr(stmt, attr, None)
            if items is not None:
                if hasattr(items, 'statements'):
                    items = items.statements
                if isinstance(items, list):
                    for item in items:
                        if self._stmt_uses_complex(item):
                            return True
        # Check expressions list
        for attr in ('args', 'arguments', 'params'):
            items = getattr(stmt, attr, None)
            if items:
                for item in items:
                    if self._expr_uses_complex(item):
                        return True
        return False

    def generate_translation_unit(self, constants: List[ConstDecl], functions: List[FunctionDecl],
                                   structs: List[StructDecl] = None,
                                   effects: List[EffectDecl] = None,
                                   capabilities: List[CapabilityDecl] = None,
                                   traits: List[TraitDecl] = None,
                                   enums: List[EnumDecl] = None,
                                   type_aliases: List[TypeAliasDecl] = None,
                                   distinct_types: List[DistinctTypeDecl] = None,
                                   statics: List[StaticDecl] = None) -> str:
        # Ordering provenance runs before codegen so every `|> sort` and
        # `|> find` site carries its hints when the selector runs (issue #145).
        annotate_ordering_hints(functions or [])
        # Pre-scan for complex types so <complex.h> is only included when
        # needed (its macros I, creal, cimag can clash with user names).
        self._scan_for_complex(functions or [], structs or [], type_aliases or [],
                               distinct_types or [], statics or [])
        lines: List[str] = []
        lines.append("#include <stdint.h>")
        lines.append("#include <stdbool.h>")
        lines.append("#include <stdio.h>")
        lines.append("#include <stdlib.h>")  # For malloc/free
        lines.append("#include <string.h>")  # For memcpy/memset
        # Skip-listed POSIX libc externs (usleep, gettimeofday, ...) are never
        # given Flow-style declarations — their real headers must be included
        # so the calls compile. Only add the header when the extern is present.
        posix_headers = {
            "usleep": "unistd.h", "sleep": "unistd.h",
            "unlink": "unistd.h", "rmdir": "unistd.h", "chdir": "unistd.h",
            "getcwd": "unistd.h", "getuid": "unistd.h", "getgid": "unistd.h",
            "geteuid": "unistd.h", "getegid": "unistd.h",
            "gethostname": "unistd.h", "mkdir": "sys/stat.h",
            "gettimeofday": "sys/time.h", "time": "time.h", "kill": "signal.h",
        }
        for fn in functions or []:
            hdr = posix_headers.get(fn.name)
            if hdr and getattr(fn, "is_extern", False):
                lines.append(f"#include <{hdr}>")
        lines.append("")
        lines.append("/* Flow runtime helpers */")
        # Temp arena for strcat results + escaping closure envs (#267 / #268).
        # Nodes are freed via flow_temp_free_all (atexit + end of main).
        # Skipped under --profile flight (#274) which bans heap allocation.
        if not self._no_heap_enabled():
            lines.append("typedef struct flow_temp_node { struct flow_temp_node* next; } flow_temp_node;")
            lines.append("static flow_temp_node* flow_temp_head = NULL;")
            lines.append("static int flow_temp_atexit_set = 0;")
            lines.append("__attribute__((unused)) static void flow_temp_free_all(void) {")
            lines.append("    while (flow_temp_head) {")
            lines.append("        flow_temp_node* n = flow_temp_head;")
            lines.append("        flow_temp_head = n->next;")
            lines.append("        free(n);")
            lines.append("    }")
            lines.append("}")
            lines.append("__attribute__((unused)) static void* flow_temp_alloc(size_t nbytes) {")
            lines.append("    flow_temp_node* node = (flow_temp_node*)malloc(sizeof(flow_temp_node) + nbytes);")
            lines.append("    if (!node) return NULL;")
            lines.append("    node->next = flow_temp_head;")
            lines.append("    flow_temp_head = node;")
            lines.append("    if (!flow_temp_atexit_set) {")
            lines.append("        flow_temp_atexit_set = 1;")
            lines.append("        atexit(flow_temp_free_all);")
            lines.append("    }")
            lines.append("    return (void*)(node + 1);")
            lines.append("}")
        # Overridable diagnostic channel (#281 / MISRA 21.6). Defaults to
        # fprintf(stderr, ...); builds may `-DFLOW_DIAG(msg)=((void)0)`.
        lines.append("#ifndef FLOW_DIAG")
        lines.append("#define FLOW_DIAG(msg) fprintf(stderr, \"%s\", (msg))")
        lines.append("#endif")
        # Overridable logging channel (#281 / MISRA 21.6). println() routes
        # through FLOW_LOG so safety-critical builds can replace printf with
        # a certified I/O abstraction via -DFLOW_LOG(fmt, ...)=...
        lines.append("#ifndef FLOW_LOG")
        lines.append("#define FLOW_LOG(fmt, ...) printf(fmt, __VA_ARGS__)")
        lines.append("#endif")
        lines.append("#ifndef FLOW_LOG_EMPTY")
        lines.append("#define FLOW_LOG_EMPTY(fmt) printf(fmt)")
        lines.append("#endif")
        lines.append("static char* flow_strcat(const char* a, const char* b) {")
        if self._no_heap_enabled():
            # Flight profile (#274): no dynamic allocation in generated helpers.
            lines.append("    (void)a; (void)b;")
            lines.append('    FLOW_DIAG("flow: string concat forbidden under --profile flight (MISRA 21.3)\\n");')
            lines.append("    abort();")
            lines.append("    return NULL;")
        else:
            lines.append("    size_t la = strlen(a ? a : \"\"), lb = strlen(b ? b : \"\");")
            lines.append("    char* r = (char*)flow_temp_alloc(la + lb + 1);")
            lines.append("    if (!r) return NULL;")
            lines.append("    if (la) memcpy(r, a, la);")
            lines.append("    if (lb) memcpy(r + la, b, lb);")
            lines.append("    r[la + lb] = '\\0';")
            lines.append("    return r;")
        lines.append("}")
        lines.append("")
        # `in` operator helper: linear scan over an array<T,N>.
        lines.append("#define __flow_in_arr(arr, val) __extension__ ({ \\")
        lines.append("    int _found = 0; \\")
        lines.append("    size_t _n = sizeof(arr)/sizeof((arr)[0]); \\")
        lines.append("    for (size_t _i = 0; _i < _n; _i++) { \\")
        lines.append("        if ((arr)[_i] == (val)) { _found = 1; break; } \\")
        lines.append("    } _found; })")
        lines.append("")
        # MISRA Phase 0+1 (#264/#265/#263/#266/#279): configurable fault
        # handler + checked arithmetic / null deref. Application TUs only;
        # library/runtime modules skip (arith checks disabled).
        if self._arith_checks_enabled():
            lines.append("/* Unified fault handler (MISRA #279) — override with -DFLOW_FAULT_HANDLER=fn */")
            lines.append("#ifndef FLOW_FAULT_HANDLER")
            lines.append("__attribute__((unused)) static inline void flow_fault_handler(const char* msg) {")
            lines.append('    fprintf(stderr, "flow: %s\\n", msg ? msg : "fault");')
            lines.append("    abort();")
            lines.append("#if defined(__GNUC__) || defined(__clang__)")
            lines.append("    __builtin_unreachable();")
            lines.append("#endif")
            lines.append("}")
            lines.append("#else")
            lines.append("#define flow_fault_handler FLOW_FAULT_HANDLER")
            lines.append("#endif")
            lines.append("#define flow_div_by_zero_handler() flow_fault_handler(\"division by zero\")")
            lines.append(
                "#define flow_shift_ub_handler() "
                "flow_fault_handler(\"invalid shift (amount out of range or left-shift of negative)\")"
            )
            lines.append("")
            # ISO C macros (no GNU statement-exprs) so -pedantic stays clean (#269).
            # Operands are evaluated more than once — Flow codegen emits pure
            # subexpressions for these sites in practice.
            lines.append("#ifndef FLOW_CHECKED_DIV")
            lines.append(
                "#define FLOW_CHECKED_DIV(L, R) "
                "(((R) != 0) ? ((L) / (R)) : (flow_div_by_zero_handler(), (L) * 0))"
            )
            lines.append("#endif")
            lines.append("#ifndef FLOW_CHECKED_MOD")
            lines.append(
                "#define FLOW_CHECKED_MOD(L, R) "
                "(((R) != 0) ? ((L) % (R)) : (flow_div_by_zero_handler(), (L) * 0))"
            )
            lines.append("#endif")
            lines.append("#ifndef FLOW_CHECKED_SHL")
            lines.append(
                "#define FLOW_CHECKED_SHL(L, R) "
                "((((R) >= 0) && ((unsigned long long)(R) < (sizeof(L) * 8ull)) "
                "&& ((L) >= 0)) ? ((L) << (R)) : (flow_shift_ub_handler(), (L) * 0))"
            )
            lines.append("#endif")
            lines.append("#ifndef FLOW_CHECKED_SHR")
            lines.append(
                "#define FLOW_CHECKED_SHR(L, R) "
                "((((R) >= 0) && ((unsigned long long)(R) < (sizeof(L) * 8ull))) "
                "? ((L) >> (R)) : (flow_shift_ub_handler(), (L) * 0))"
            )
            lines.append("#endif")
            # Overflow + null deref are opt-in (--profile safety / FLOW_OVERFLOW_CHECK).
            if self._overflow_checks_enabled():
                lines.append("#define flow_null_deref_handler() flow_fault_handler(\"null pointer dereference\")")
                lines.append("#define flow_overflow_handler() flow_fault_handler(\"integer overflow\")")
                lines.append("#ifndef FLOW_CHECKED_ADD")
                lines.append("#if defined(__clang__) || defined(__GNUC__)")
                lines.append(
                    "#define FLOW_CHECKED_ADD(L, R) "
                    "(__extension__ ({ __typeof__(L) _r; "
                    "__builtin_add_overflow((L), (R), &_r) "
                    "? (flow_overflow_handler(), (L)) : _r; }))"
                )
                lines.append("#else")
                lines.append(
                    "#define FLOW_CHECKED_ADD(L, R) "
                    "(((L) > 0 && (R) > (INT_MAX - (L))) || "
                    "((L) < 0 && (R) < (INT_MIN - (L))) "
                    "? (flow_overflow_handler(), (L)) : ((L) + (R)))"
                )
                lines.append("#endif")
                lines.append("#endif")
                lines.append("#ifndef FLOW_CHECKED_SUB")
                lines.append("#if defined(__clang__) || defined(__GNUC__)")
                lines.append(
                    "#define FLOW_CHECKED_SUB(L, R) "
                    "(__extension__ ({ __typeof__(L) _r; "
                    "__builtin_sub_overflow((L), (R), &_r) "
                    "? (flow_overflow_handler(), (L)) : _r; }))"
                )
                lines.append("#else")
                lines.append(
                    "#define FLOW_CHECKED_SUB(L, R) "
                    "(((R) > 0 && (L) < (INT_MIN + (R))) || "
                    "((R) < 0 && (L) > (INT_MAX + (R))) "
                    "? (flow_overflow_handler(), (L)) : ((L) - (R)))"
                )
                lines.append("#endif")
                lines.append("#endif")
                lines.append("#ifndef FLOW_CHECKED_MUL")
                lines.append("#if defined(__clang__) || defined(__GNUC__)")
                lines.append(
                    "#define FLOW_CHECKED_MUL(L, R) "
                    "(__extension__ ({ __typeof__(L) _r; "
                    "__builtin_mul_overflow((L), (R), &_r) "
                    "? (flow_overflow_handler(), (L)) : _r; }))"
                )
                lines.append("#else")
                lines.append(
                    "#define FLOW_CHECKED_MUL(L, R) "
                    "(((L) != 0 && (R) != 0 && "
                    "(((L) > 0) == ((R) > 0)) && "
                    "(R) > (INT_MAX / (L))) || "
                    "((L) != 0 && (R) != 0 && "
                    "(((L) > 0) != ((R) > 0)) && "
                    "(R) < (INT_MIN / (L))) "
                    "? (flow_overflow_handler(), (L)) : ((L) * (R)))"
                )
                lines.append("#endif")
                lines.append("#endif")
                lines.append("#ifndef FLOW_NONNULL")
                lines.append(
                    "#define FLOW_NONNULL(P) "
                    "(((P) != NULL) ? (P) : (flow_null_deref_handler(), (P)))"
                )
                lines.append("#endif")
            lines.append("")
        
        # Always include math.h - many programs use math functions
        # The linker will only include what's actually used
        lines.append("#include <math.h>")
        # complex.h for c64/c128 complex number support (only if used).
        # Conditionally included: <complex.h> defines macros I, creal, cimag,
        # etc. that can clash with user variable names.
        if self._uses_complex:
            lines.append("#include <complex.h>")
        
        lines.append("")
        # Library modules must not export a shared _ui_state (link conflict with main TU).
        if self._library:
            lines.append("static void* _ui_state = NULL;")
        else:
            lines.append("void* _ui_state = NULL;")
        lines.append("")

        # Provide a default i32_to_f32 helper if not defined in Flow code
        has_i32_to_f32_def = False
        if functions:
            for fn in functions:
                if fn.name == "i32_to_f32" and not getattr(fn, 'is_extern', False):
                    has_i32_to_f32_def = True
                    break
        if not has_i32_to_f32_def:
            lines.append("static inline float i32_to_f32(int32_t v) { return (float)v; }")
            lines.append("")

        # Host stub for @gpu kernels: real device id comes from Metal/CUDA codegen.
        has_gpu_thread_id = False
        if functions:
            for fn in functions:
                if fn.name == "gpu_thread_id":
                    has_gpu_thread_id = True
                    break
        if not has_gpu_thread_id:
            lines.append("/* Host stub for @gpu kernels (device codegen replaces this). */")
            lines.append("static inline int32_t gpu_thread_id(void) { return 0; }")
            lines.append("")
        
        # Register effects and capabilities for dispatch
        if effects:
            for effect in effects:
                self._effects[effect.name] = effect
        
        if capabilities:
            for capability in capabilities:
                self._capabilities[capability.name] = capability
                if capability.name in ("FiberAsync", "FiberCont"):
                    # Fiber backends → run main on a fiber so park suspends Flow frames.
                    self._uses_fiber_main = True
        
        # Pre-collect structs from struct declarations so we can emit them before effect runtime
        if structs:
            for decl in structs:
                if decl.name not in self._structs:
                    self._structs[decl.name] = {}
                for field in decl.fields:
                    self._structs[decl.name][field.name] = field.type
        
        # Collect structs referenced in effects that need to be defined first
        effect_struct_names = set()
        if effects:
            for effect in effects:
                for op in effect.operations:
                    if self._is_struct_type(op.return_type):
                        effect_struct_names.add(self._type_to_string(op.return_type))
                    for p in op.parameters:
                        if self._is_struct_type(p.type):
                            effect_struct_names.add(self._type_to_string(p.type))
        
        # Emit struct definitions needed by effects before effect runtime
        effect_structs_emitted = set()
        if effect_struct_names:
            lines.append("/* Struct definitions for effect types */")
            for struct_name in sorted(effect_struct_names):
                if struct_name in self._structs:
                    safe_struct_name = _c_ident(struct_name)
                    lines.append("typedef struct {")
                    for field_name, field_type in self._structs[struct_name].items():
                        lines.append(f"    {self._c_type(field_type)} {_c_ident(field_name)};")
                    lines.append(f"}} {safe_struct_name};")
                    lines.append("")
                    effect_structs_emitted.add(struct_name)
        
        # Generate effect handler type definitions and dispatch functions
        if effects:
            lines.extend(self._gen_effect_runtime_types(effects))

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
        
        # Collect enums
        if enums:
            for enum in enums:
                self._enums[enum.name] = enum
                for variant in enum.variants:
                    self._enum_variant_owner[f"{enum.name}_{variant.name}"] = enum.name

        # Track type aliases and distinct types to skip during struct emission
        type_alias_names = set()
        distinct_type_names = set()
        if type_aliases:
            type_alias_names = {alias.name for alias in type_aliases}
        if distinct_types:
            distinct_type_names = {dt.name for dt in distinct_types}

        # Register structs with overload resolver
        for struct_name, fields in self._structs.items():
            self._overload_resolver.register_struct(
                struct_name, 
                {name: self._type_to_string(t) for name, t in fields.items()}
            )
        
        # Math functions that should use C stdlib names (not mangled)
        c_math_functions = {'sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'atan2',
                           'sinh', 'cosh', 'tanh', 'asinh', 'acosh', 'atanh',
                           'sqrt', 'cbrt', 'pow', 'exp', 'exp2', 'log', 'log2', 'log10',
                           'fabs', 'abs', 'floor', 'ceil', 'round', 'fmod',
                           'fmin', 'fmax', 'hypot'}
        primitives = {'f32', 'f64', 'c64', 'c128', 'i32', 'i64', 'float', 'double', 'int'}
        no_mangle_prefixes = ()
        
        # Register all functions for overload resolution
        for fn in functions:
            # Library / always-linked runtime modules need stable C ABI names.
            if self._library and "flow_api" not in (getattr(fn, "attributes", None) or []):
                attrs = list(getattr(fn, "attributes", None) or [])
                attrs.append("flow_api")
                fn.attributes = attrs
            self._overload_resolver.register_function(fn)
        
        # Build mangled name map
        for fn in functions:
            # Never mangle extern functions: they must link against the host C ABI.
            if getattr(fn, "is_extern", False):
                self._mangled_names[id(fn)] = fn.name
                continue
            # Monomorphized generics already encode type args in the name
            # (`channel_new_i32`); overload mangling would double-suffix them.
            if "monomorphized" in (getattr(fn, "attributes", None) or []):
                self._mangled_names[id(fn)] = fn.name
                continue
            # Functions generated from `flow` blocks keep their plain names:
            # Name_step(Name*, double) is a stable C embedding API.
            # Library runtime modules also keep plain names (C ABI for always-link).
            if self._library or "flow_api" in (getattr(fn, "attributes", None) or []):
                self._mangled_names[id(fn)] = fn.name
                continue
            param_types = tuple(self._type_to_string(p.type) for p in fn.parameters)
            
            if fn.name.startswith(no_mangle_prefixes):
                self._mangled_names[id(fn)] = fn.name
                continue

            # Don't mangle C math functions with primitive args - use C stdlib names
            if fn.name in c_math_functions:
                all_primitive = all(pt in primitives for pt in param_types)
                if all_primitive:
                    self._mangled_names[id(fn)] = fn.name  # Keep original name
                    continue

            mangled = self._overload_resolver._mangle_name(fn.name, list(param_types))
            self._mangled_names[id(fn)] = mangled
        
        # Emit enum definitions (tagged unions)
        for enum_name, enum_decl in self._enums.items():
            lines.extend(self._gen_enum(enum_decl))
            lines.append("")

        # Emit type aliases (transparent typedefs in C)
        if type_aliases:
            lines.append("/* Type aliases (transparent) */")
            for alias in type_aliases:
                base_c_type = self._c_type(alias.base_type)
                alias_name = _c_ident(alias.name)
                lines.append(f"typedef {base_c_type} {alias_name};")
            lines.append("")

        # Emit distinct types (typedefs in C - same representation but different type name)
        # Note: C doesn't enforce type safety for typedefs, but the type checker does
        if distinct_types:
            lines.append("/* Distinct types (opaque) */")
            for distinct in distinct_types:
                base_c_type = self._c_type(distinct.base_type)
                distinct_name = _c_ident(distinct.name)
                lines.append(f"typedef {base_c_type} {distinct_name};")
            lines.append("")

        # Emit struct definitions in dependency order
        # Include structs already emitted for effects
        emitted = set(effect_structs_emitted)

        # Escaping function types must be fully defined before forward decls
        # that use them as parameter/return types.
        for fn in functions:
            if self._is_fn_type(fn.return_type):
                self._ensure_fn_typedef(fn.return_type)
            if self._is_cfn_type(fn.return_type):
                self._ensure_cfn_typedef(fn.return_type)
            for p in fn.parameters:
                if self._is_fn_type(p.type):
                    self._ensure_fn_typedef(p.type)
                if self._is_cfn_type(p.type):
                    self._ensure_cfn_typedef(p.type)
        if self._fn_typedefs_emitted:
            for line in list(self._pending_env_structs):
                if line.startswith("typedef struct {") and "void* env;" in line:
                    lines.append(line)
                elif line.startswith("typedef ") and "(*cfn_" in line:
                    lines.append(line)
            # Keep non-fn pending structs for the lambda insert block; drop
            # the fn/cfn typedefs we already emitted so they are not duplicated.
            self._pending_env_structs = [
                line
                for line in self._pending_env_structs
                if not (line.startswith("typedef struct {") and "void* env;" in line
                        and "(*fn)(void*" in line)
                and not (line.startswith("typedef ") and "(*cfn_" in line)
            ]
            if self._fn_typedefs_emitted:
                lines.append("")

        # Forward-declare every remaining struct as `typedef struct Name Name;`
        # so that pointer fields (e.g. `ptr<Route>` inside `HttpServer`) can
        # reference a struct type regardless of alphabetical/definition order.
        # A pointer field only needs the type *name* to exist, not a complete
        # definition, so this also transparently supports self- and
        # mutually-referential struct pointers.
        forward_declared = set()
        for struct_name in sorted(self._structs.keys()):
            if struct_name in emitted:
                continue
            if struct_name in self._enums or struct_name in type_alias_names or struct_name in distinct_type_names:
                continue
            safe_name = _c_ident(struct_name)
            lines.append(f"typedef struct {safe_name} {safe_name};")
            forward_declared.add(struct_name)
        if forward_declared:
            lines.append("")

        # Borrowed views: one two-word struct per (element, mutability) pair,
        # emitted after struct forward declarations so struct elements resolve.
        # The slot is filled at the end so views discovered while generating
        # bodies (e.g. a slice expression) still land ahead of every use.
        self._collect_span_typedefs(functions, structs, statics)
        span_insert_idx = len(lines)

        def emit_struct(name):
            if name in emitted:
                return
            # Skip types already defined as enums
            if name in self._enums:
                emitted.add(name)
                return
            # Skip type aliases and distinct types (they're emitted as typedefs above)
            if name in type_alias_names or name in distinct_type_names:
                emitted.add(name)
                return
            # Skip if not in _structs (type aliases/distinct types might not have entries)
            if name not in self._structs:
                return
            safe_struct_name = _c_ident(name)
            # First, emit any nested (embedded-by-value) struct types. These
            # must be fully defined before use, unlike pointer fields which
            # only need the forward declaration above.
            for field_type in self._structs[name].values():
                if self._is_struct_type(field_type) and field_type.name not in emitted:
                    emit_struct(field_type.name)
                # Handle sized array fields that contain structs
                if getattr(field_type, "name", "").startswith("array_") and getattr(field_type, "element_type", None):
                    elem = field_type.element_type
                    if self._is_struct_type(elem) and elem.name not in emitted:
                        emit_struct(elem.name)

            # Now emit this struct. If it was forward-declared above, complete
            # the tagged struct rather than re-typedef'ing the name.
            if name in forward_declared:
                lines.append(f"struct {safe_struct_name} {{")
            else:
                lines.append("typedef struct {")
            for field_name, field_type in self._structs[name].items():
                # Inline sized arrays in struct fields when size is known.
                if getattr(field_type, "name", "").startswith("array_") and getattr(field_type, "size", None) and getattr(field_type, "element_type", None):
                    elem_c = self._c_type(field_type.element_type)
                    size = field_type.size
                    lines.append(f"    {elem_c} {_c_ident(field_name)}[{size}];")
                else:
                    lines.append(f"    {self._c_type(field_type)} {_c_ident(field_name)};")
            if name in forward_declared:
                lines.append("};")
            else:
                lines.append(f"}} {safe_struct_name};")
            lines.append("")
            emitted.add(name)
        
        for struct_name in sorted(self._structs.keys()):
            emit_struct(struct_name)

        # Forward declarations for capability methods (mangled names: CapabilityName_methodName)
        for cap_name, cap in self._capabilities.items():
            for method in cap.methods:
                mangled_name = _c_ident(f"{cap_name}_{method.name}")
                ret = self._c_type(method.return_type)
                params = ", ".join([f"{self._c_type(p.type)} {_c_ident(p.name)}" for p in method.parameters])
                lines.append(f"{ret} {mangled_name}({params});")
        if self._capabilities:
            lines.append("")
        
        # Generate effect vtables (after forward declarations so function pointers are valid)
        if effects:
            lines.extend(self._gen_effect_vtables(effects, capabilities or []))

        # Forward declarations
        math_functions = {'sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'atan2',
                         'sinh', 'cosh', 'tanh', 'asinh', 'acosh', 'atanh',
                         'sqrt', 'cbrt', 'pow', 'exp', 'exp2', 'log', 'log2', 'log10',
                         'fabs', 'abs', 'floor', 'ceil', 'round', 'fmod',
                         'fmin', 'fmax', 'hypot'}
        # Standard C library functions that don't need declarations (covered by includes).
        # Include FILE*/stdlib names used by flowc fileio + emit (conflicting prototypes
        # vs stdio.h/stdlib.h otherwise break `./flow run compiler/src/main.flow`).
        # Keep this set in sync with the preamble #includes above (#283).
        # Mapping:
        #   <stdlib.h>  malloc free calloc realloc getenv putenv system abs
        #   <stdio.h>   printf sprintf snprintf fprintf puts putchar getchar fflush
        #               fopen fclose fread fwrite fseek ftell fgets fputs fputc fgetc
        #               remove rename
        #   <string.h>  memcpy memmove memset memcmp strlen strcmp strncmp strcpy
        #               strncpy strcat strncat strchr strstr
        #   <unistd.h>  unlink rmdir chdir getcwd usleep sleep getuid getgid
        #               geteuid getegid gethostname
        #   <math.h>    (math_functions set below)
        #   <time.h>    time gettimeofday
        #   <signal.h>  kill
        stdlib_functions = {'malloc', 'free', 'calloc', 'realloc', 'printf', 'sprintf',
                           'snprintf', 'fprintf', 'puts', 'putchar', 'getchar', 'fflush',
                           'memcpy', 'memmove', 'memset', 'memcmp',
                           'strlen', 'strcmp', 'strncmp', 'strcpy', 'strncpy',
                           'strcat', 'strncat', 'strchr', 'strstr', 'strtod',
                           'getenv', 'putenv',
                           # FILE* APIs — use <stdio.h> decls; Flow extern types are approximate
                           'fopen', 'fclose', 'fread', 'fwrite', 'fseek', 'ftell', 'fgets', 'fputs',
                           'fputc', 'fgetc',
                           # POSIX / libc — approximate Flow types clash with real headers
                           'remove', 'rename', 'unlink', 'mkdir', 'rmdir', 'chdir', 'getcwd',
                           'usleep', 'sleep', 'gettimeofday', 'time', 'system',
                           'kill', 'getuid', 'getgid', 'geteuid', 'getegid', 'gethostname',
                           # POSIX popen/pclose — provided by stdio.h
                           'popen', 'pclose',
                           # qsort, bsearch — provided by stdlib.h
                           'qsort', 'bsearch',
                           # pthread — provided by pthread.h
                           'pthread_create', 'pthread_join', 'pthread_exit',
                           'pthread_mutex_init', 'pthread_mutex_destroy',
                           'pthread_mutex_lock', 'pthread_mutex_unlock',
                           # sys/stat.h — provided by sys/stat.h
                           'stat', 'fstat', 'lstat', 'mkdir', 'chmod'}
        primitives = {'f32', 'f64', 'c64', 'c128', 'i32', 'i64', 'float', 'double', 'int'}
        for fn in functions:
            # Skip standard library functions - they're declared in system headers
            if fn.name in stdlib_functions:
                continue
            # Skip functions provided by @cEmbed (they're already defined)
            if fn.name in getattr(self, '_cembed_functions', set()):
                continue
            # Emit extern function declarations (needed for linking with runtime)
            if getattr(fn, 'is_extern', False):
                lines.append(self._c_function_decl(fn) + ";")
                continue
            # Skip math functions only if they take primitive types
            if fn.name in math_functions:
                all_primitive = all(
                    self._type_to_string(p.type) in primitives 
                    for p in fn.parameters
                )
                if all_primitive:
                    continue  # Skip C math function
            # Fiber-wrapped main: forward-declare the body, not `main` itself.
            if (
                self._uses_fiber_main
                and fn.name == "main"
                and len(fn.parameters) == 0
                and not self._library
            ):
                lines.append("static int32_t __flow_main_body(void);")
                continue
            lines.append(self._c_function_decl(fn) + ";")
        lines.append("")

        # Emit constant declarations (after forward declarations)
        for const in constants:
            lines.append(f"static const {self._c_type(const.type)} {_c_ident(const.name)} = {self._gen_expr(const.value)};")
            # Track constant types for print formatting
            self._var_types[const.name] = const.type
            # File-scope constants stay reachable from lifted lambda
            # functions, so they are never captured into closure envs.
            self._const_names.add(const.name)
        if constants:
            lines.append("")

        # Emit module statics: file-scope mutable state, always `static` so
        # every translation unit (library or executable) keeps them private.
        if statics:
            lines.append("/* Module statics */")
            for st in statics:
                lines.append(self._gen_static_decl(st))
                # Track types for print formatting / overload resolution.
                self._var_types[st.name] = st.type
                self._overload_resolver.set_var_type(st.name, self._type_to_string(st.type))
                # File-scope statics stay reachable from lifted lambda
                # functions, so they are never captured into closure envs.
                self._static_names.add(st.name)
            lines.append("")

        # Lambda definitions get spliced in here: after forward declarations
        # and constants (both may be referenced from lambda bodies), before
        # any function definition that may create a closure value.
        self._lambda_insert_idx = len(lines)

        # Generate capability method definitions
        for cap_name, cap in self._capabilities.items():
            for method in cap.methods:
                lines.extend(self._gen_capability_method(cap_name, method))
                lines.append("")

        # Definitions
        for fn in functions:
            lines.extend(self._gen_function(fn))
            lines.append("")
        
        # Emit any lambdas that were generated during function processing.
        # Env/closure typedefs come first (lambda signatures reference them),
        # then the lifted static functions.
        insert_extra: List[str] = []
        if self._pending_lambdas or self._pending_env_structs:
            insert_extra.append("// Auto-generated lambda functions")
            insert_extra.extend(self._pending_env_structs)
            for lambda_name, ret_type, params, body_lines in self._pending_lambdas:
                insert_extra.append(f"static {ret_type} {lambda_name}({params}) {{")
                for line in body_lines:
                    insert_extra.append(f"    {line}")
                insert_extra.append("}")
            insert_extra.append("")
        if self._pending_order_helpers:
            insert_extra.append("// Total-order comparison (see docs/language/ordering.md)")
            insert_extra.extend(self._pending_order_helpers)
            insert_extra.append("")
        if self._pending_sort_helpers:
            insert_extra.append("// Auto-generated declarative sort helpers")
            insert_extra.extend(self._pending_sort_helpers)
            insert_extra.append("")
        if self._pending_find_helpers:
            insert_extra.append("// Auto-generated declarative search helpers")
            insert_extra.extend(self._pending_find_helpers)
            insert_extra.append("")

        if insert_extra:
            insert_idx = self._lambda_insert_idx
            if insert_idx is None or insert_idx > len(lines):
                insert_idx = len(lines)
            lines = lines[:insert_idx] + insert_extra + lines[insert_idx:]
            if span_insert_idx >= insert_idx:
                span_insert_idx += len(insert_extra)

        if self._pending_span_typedefs:
            span_block = ["/* Spans: borrowed {pointer, length} views */"]
            span_block.extend(self._pending_span_typedefs)
            span_block.append("")
            self._pending_span_typedefs = []
            lines = lines[:span_insert_idx] + span_block + lines[span_insert_idx:]

        return "\n".join(lines).rstrip() + "\n"
    
    def _is_zero_literal(self, e: Any) -> bool:
        """True for a literal that lowers to zero (0, 0.0, false)."""
        if not isinstance(e, Literal):
            return False
        try:
            return float(e.value) == 0.0
        except (TypeError, ValueError):
            return e.value == "false"

    def _gen_static_decl(self, st: StaticDecl) -> str:
        """Generate a file-scope C static for a module static declaration."""
        t = st.type
        name = _c_ident(st.name)
        # A span static starts as an empty view; a real borrow is installed
        # at runtime (and escape-checked at the assignment).
        if self._is_span_type(t):
            return f"static {self._c_type(t)} {name} = {{0}};"
        if t.name.startswith("array_") and getattr(t, "size", None) and getattr(t, "element_type", None):
            elem_c = self._c_type(t.element_type)
            init = st.value
            # Zero-fill shorthand: an all-zero array literal lowers to {0}.
            if isinstance(init, ArrayLiteral) and all(
                self._is_zero_literal(el) for el in init.elements
            ):
                return f"static {elem_c} {name}[{t.size}] = {{0}};"
            if isinstance(init, ArrayLiteral):
                return (
                    f"static {elem_c} {name}[{t.size}] = "
                    f"{self._gen_array_literal(init, as_initializer=True)};"
                )
        return f"static {self._c_type(t)} {name} = {self._gen_expr(st.value)};"

    def _gen_capability_method(self, capability_name: str, method: CapabilityMethod) -> List[str]:
        """Generate a capability method as a standalone C function with mangled name."""
        lines: List[str] = []
        mangled_name = _c_ident(f"{capability_name}_{method.name}")
        ret = self._c_type(method.return_type)
        params = ", ".join([f"{self._c_type(p.type)} {_c_ident(p.name)}" for p in method.parameters])
        
        lines.append(f"{ret} {mangled_name}({params}) {{")
        self._indent += 1
        lines.extend(self._gen_block(method.body))
        self._indent -= 1
        lines.append("}")
        return lines
    
    def _gen_enum(self, enum: EnumDecl) -> List[str]:
        """Generate C tagged union for enum.
        
        enum Option<T> { Some(T), None }
        becomes:
        typedef enum { Option_i32_Some, Option_i32_None } Option_i32_Tag;
        typedef struct {
            Option_i32_Tag tag;
            union {
                i32 Some_value;
            } data;
        } Option_i32;
        """
        lines: List[str] = []
        name = _c_ident(enum.name)

        # Generate tag enum
        lines.append("typedef enum {")
        for i, variant in enumerate(enum.variants):
            comma = "," if i < len(enum.variants) - 1 else ""
            lines.append(f"    {name}_{_c_ident(variant.name)}{comma}")
        lines.append(f"}} {name}_Tag;")
        lines.append("")

        # Generate tagged union struct
        lines.append("typedef struct {")
        lines.append(f"    {name}_Tag tag;")
        
        # Check if any variants have data
        has_data = any(len(v.fields) > 0 for v in enum.variants)
        if has_data:
            lines.append("    union {")
            for variant in enum.variants:
                if len(variant.fields) == 1:
                    c_type = self._c_type(variant.fields[0])
                    lines.append(f"        {c_type} {_c_ident(variant.name)}_value;")
                elif len(variant.fields) > 1:
                    # Multiple fields - create anonymous struct
                    lines.append("        struct {")
                    for i, field_type in enumerate(variant.fields):
                        c_type = self._c_type(field_type)
                        lines.append(f"            {c_type} _{i};")
                    lines.append(f"        }} {_c_ident(variant.name)}_data;")
            lines.append("    } data;")
        
        lines.append(f"}} {name};")
        
        return lines
    
    def _gen_effect_runtime_types(self, effects: List[EffectDecl]) -> List[str]:
        """Generate effect handler type definitions and dispatch functions."""
        lines: List[str] = []
        
        lines.append("/* ===== Effect Handler Runtime ===== */")
        lines.append(
            "/* Delimited continuations: runtime/flow_cont.c scaffold only — "
            "Flow frames cannot suspend mid-function yet. */"
        )
        lines.append("")
        if effects:
            # Opt-in fail-loud for unhandled ops: compile with --strict-effects, or
            # set FLOW_STRICT_EFFECTS=1 at runtime. Default remains zeroed no-ops
            # (see docs/effects-showcase.md) until effect-row typing lands.
            if self._strict_effects:
                lines.append("#define FLOW_STRICT_EFFECTS_COMPILE 1")
                lines.append("")
            lines.append("static int _flow_strict_effects(void) {")
            if self._strict_effects:
                lines.append("    return 1;")
            else:
                lines.append("    static int cached = -1;")
                lines.append("    if (cached < 0) {")
                lines.append('        const char *e = getenv("FLOW_STRICT_EFFECTS");')
                lines.append('        cached = (e && e[0] == \'1\') ? 1 : 0;')
                lines.append("    }")
                lines.append("    return cached;")
            lines.append("}")
            lines.append("")
            lines.append(
                "static void _flow_unhandled_effect(const char *effect, const char *op) {"
            )
            lines.append("    if (_flow_strict_effects()) {")
            lines.append(
                '        fprintf(stderr, "flow: unhandled effect %s.%s '
                '(set FLOW_STRICT_EFFECTS=0 to allow zero defaults)\\n", effect, op);'
            )
            lines.append("        abort();")
            lines.append("    }")
            lines.append("}")
            lines.append("")
        
        if effects:
            # Shared by fiber-local effect handler slots below. Weak fallback so
            # standalone builds (plain `cc file.c`, no fiber runtime) still link;
            # the strong definition in runtime/flow_fiber.c wins when present.
            lines.append(
                "__attribute__((weak)) int32_t flow_fiber_current_id(void) "
                "{ return -1; }"
            )
            lines.append("#ifndef FLOW_FIBER_MAX")
            lines.append("#define FLOW_FIBER_MAX 4096")
            lines.append("#endif")
            lines.append("")

        # For each effect, generate a struct holding function pointers for its operations
        for effect in effects:
            effect_name = effect.name
            safe_effect_name = _c_ident(effect_name)
            lines.append(f"/* Effect handler vtable for {safe_effect_name} */")
            lines.append("typedef struct {")
            for op in effect.operations:
                ret_type = self._c_type(op.return_type)
                param_types = ", ".join([self._c_type(p.type) for p in op.parameters])
                if not param_types:
                    param_types = "void"
                lines.append(f"    {ret_type} (*{_c_ident(op.name)})({param_types});")
            lines.append(f"}} {safe_effect_name}_Handler;")
            lines.append("")
            
            # Handler pointer: fiber-local when on a fiber (work-stealing migrates
            # OS threads), otherwise thread-local for ThreadedAsync / host code.
            lines.append(
                f"static _Thread_local {safe_effect_name}_Handler* "
                f"_tls_{safe_effect_name}_handler = NULL;"
            )
            lines.append(
                f"static {safe_effect_name}_Handler* "
                f"_fiber_{safe_effect_name}_handler[FLOW_FIBER_MAX];"
            )
            lines.append(
                f"static inline {safe_effect_name}_Handler** "
                f"_slot_{safe_effect_name}_handler(void) {{"
            )
            lines.append("    int32_t _fid = flow_fiber_current_id();")
            lines.append(
                f"    if (_fid >= 0 && _fid < FLOW_FIBER_MAX) "
                f"return &_fiber_{safe_effect_name}_handler[_fid];"
            )
            lines.append(f"    return &_tls_{safe_effect_name}_handler;")
            lines.append("}")
            lines.append(
                f"#define _current_{safe_effect_name}_handler "
                f"(*_slot_{safe_effect_name}_handler())"
            )
            lines.append("")
            
            # Generate dispatch functions for each operation
            for op in effect.operations:
                ret_type = self._c_type(op.return_type)
                params_with_names = ", ".join([f"{self._c_type(p.type)} {_c_ident(p.name)}" for p in op.parameters])
                param_names = ", ".join([_c_ident(p.name) for p in op.parameters])
                op_ident = _c_ident(op.name)
                
                lines.append(f"{ret_type} {safe_effect_name}_{op_ident}({params_with_names}) {{")
                lines.append(
                    f"    if (_current_{safe_effect_name}_handler && "
                    f"_current_{safe_effect_name}_handler->{op_ident}) {{"
                )
                if ret_type == "void":
                    if param_names:
                        lines.append(
                            f"        _current_{safe_effect_name}_handler->{op_ident}({param_names});"
                        )
                    else:
                        lines.append(
                            f"        _current_{safe_effect_name}_handler->{op_ident}();"
                        )
                    lines.append("        return;")
                else:
                    if param_names:
                        lines.append(
                            f"        return _current_{safe_effect_name}_handler->"
                            f"{op_ident}({param_names});"
                        )
                    else:
                        lines.append(
                            f"        return _current_{safe_effect_name}_handler->{op_ident}();"
                        )
                lines.append("    }")
                lines.append(
                    f'    _flow_unhandled_effect("{safe_effect_name}", "{op_ident}");'
                )
                if ret_type == "void":
                    lines.append("    return;")
                elif "int" in ret_type or ret_type in ["int32_t", "int64_t", "int8_t", "int16_t"]:
                    lines.append("    return 0;")
                elif ret_type in ["float", "double"]:
                    lines.append("    return 0.0;")
                elif ret_type == "char*":
                    lines.append("    return NULL;")
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
            safe_cap_name = _c_ident(cap_name)
            for effect_name in cap.effects:
                if effect_name in self._effects:
                    effect = self._effects[effect_name]
                    safe_effect_name = _c_ident(effect_name)
                    lines.append(f"/* {safe_cap_name} handler for {safe_effect_name} */")
                    lines.append(f"static {safe_effect_name}_Handler _{safe_cap_name}_{safe_effect_name}_vtable = {{")
                    for op in effect.operations:
                        # Check if capability has this method
                        has_method = any(m.name == op.name for m in cap.methods)
                        if has_method:
                            lines.append(f"    .{_c_ident(op.name)} = {safe_cap_name}_{_c_ident(op.name)},")
                        else:
                            lines.append(f"    .{_c_ident(op.name)} = NULL,")
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
            decl_type = stmt.type
            if decl_type and decl_type.name == "auto" and stmt.initializer is not None:
                decl_type = self._infer_expr_type(stmt.initializer)
            self._var_types[stmt.name] = decl_type
            
            if self._is_struct_type(decl_type):
                if decl_type.name not in self._structs:
                    self._structs[decl_type.name] = {}
            if stmt.initializer:
                # If this is a struct declaration with a struct literal, infer field types
                if self._is_struct_type(decl_type) and isinstance(stmt.initializer, StructLiteral):
                    for field_name, field_value in stmt.initializer.fields:
                        field_type = self._infer_expr_type(field_value)
                        self._structs[decl_type.name][field_name] = field_type
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
        elif isinstance(stmt, LayoutStatement):
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
        elif isinstance(expr, RecordUpdate):
            self._collect_structs_from_expr(expr.base)
            for _, value in expr.updates:
                self._collect_structs_from_expr(value)
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
        elif isinstance(expr, FunctionCall):
            lambda_info = self._closure_vars.get(expr.name) or self._fnptr_vars.get(expr.name)
            if lambda_info is not None:
                return lambda_info.get("flow_ret") or Type("i32")
            resolved = self._overload_resolver.resolve_call(expr)
            ret = None
            if resolved:
                ret = self._overload_resolver.get_return_type(resolved)
            if not ret:
                ret = self._overload_resolver.get_return_type(expr.name)
            return Type(ret or "i32")
        elif isinstance(expr, SortExpr):
            return self._infer_expr_type(expr.array)
        elif isinstance(expr, StructLiteral):
            return Type(expr.struct_name)
        elif isinstance(expr, RecordUpdate):
            inferred = self._infer_expr_type(expr.base)
            return inferred if inferred else Type("i32")
        elif isinstance(expr, SliceExpr):
            return self._span_type_for_expr(expr) or Type("i32")
        elif isinstance(expr, FieldAccess):
            obj_type = self._infer_expr_type(expr.object)
            # A span exposes only `.len` (i64).
            if self._is_span_type(obj_type) and expr.field == "len":
                return Type("i64")
            # Unwrap pointers so ptr<Struct> field access resolves the struct
            if obj_type and obj_type.name not in self._structs:
                elem = getattr(obj_type, "element_type", None)
                if elem is not None and elem.name in self._structs:
                    obj_type = elem
            if obj_type and obj_type.name in self._structs:
                field_type = self._structs[obj_type.name].get(expr.field)
                if field_type:
                    return field_type
            return Type("i32")
        elif isinstance(expr, ArrayAccess):
            base_type = self._infer_expr_type(expr.array)
            if self._is_span_type(base_type):
                return base_type.element_type or Type(span_element_name(base_type.name))
            if base_type is not None:
                elem = getattr(base_type, "element_type", None)
                if elem is not None:
                    return elem
                # Fall back to name-based unwrapping: ptr_Point -> Point
                for prefix in ("ptr_", "array_"):
                    if base_type.name.startswith(prefix):
                        return Type(base_type.name[len(prefix):])
            return Type("i32")
        elif isinstance(expr, MethodCall):
            impl_method = self._impl_method_for_receiver(
                self._infer_expr_type(expr.object), expr.method
            )
            if impl_method:
                return self._infer_expr_type(
                    FunctionCall(impl_method, [expr.object] + list(expr.arguments))
                )
            return self._infer_expr_type(
                FunctionCall(expr.method, [expr.object] + list(expr.arguments))
            )
        elif isinstance(expr, UnaryOperation):
            operand = self._infer_expr_type(expr.operand)
            if expr.operator == "!":
                return Type("bool")
            return operand
        elif isinstance(expr, IfExpression):
            return self._infer_expr_type(expr.then_expr)
        elif isinstance(expr, BinaryOperation):
            if expr.operator in ("==", "!=", "<", "<=", ">", ">=", "&&", "||", "in"):
                return Type("bool")
            left = self._infer_expr_type(expr.left)
            right = self._infer_expr_type(expr.right)
            # Dual arithmetic promotes to Dual (pattern-adoption #161).
            if left.name == "Dual" or right.name == "Dual":
                return Type("Dual")
            # Tensor element-wise / scale (#161).
            if left.name == "Tensor" or right.name == "Tensor":
                return Type("Tensor")
            if left.name == "f64" or right.name == "f64":
                return Type("f64")
            if left.name == "f32" or right.name == "f32":
                return Type("f32")
            if left.name == "i64" or right.name == "i64":
                return Type("i64")
            if left.name == "u64" or right.name == "u64":
                return Type("u64")
            if left.name == "u32" or right.name == "u32":
                return Type("u32")
            return left or right or Type("i32")
        else:
            return Type("i32")  # Default fallback

    def _is_string_expr(self, expr: Expression) -> bool:
        """Check if an expression is a string type.

        Function calls, casts, and other non-literal forms must be included:
        otherwise a `string`-returning call used in `a + f()` is treated as a
        non-string operand and forced through `_gen_stringify_expr`, which
        copies it into a 64-byte stack buffer and silently truncates anything
        longer. That is exactly how the repo-stats JSON emitter lost digits.
        """
        if isinstance(expr, Literal) and expr.type.name == 'string':
            return True
        if isinstance(expr, Variable) and expr.name in self._var_types:
            return self._var_types[expr.name].name == 'string'
        if isinstance(expr, BinaryOperation) and expr.operator == '+':
            # String concat if either side is string
            return self._is_string_expr(expr.left) or self._is_string_expr(expr.right)
        inferred = self._infer_expr_type(expr)
        return inferred is not None and inferred.name == 'string'

    def _infer_match_type(self, expr: Expression) -> Type:
        """Infer C type for match scrutinee bindings."""
        inferred = self._infer_expr_type(expr)
        if inferred is not None:
            return inferred
        return Type("i32")

    def _infer_result_struct_type(self, expr: Expression) -> str:
        """Infer Result struct C type name for try operator."""
        inferred = self._infer_expr_type(expr)
        if inferred and inferred.name.startswith("Result_"):
            return _c_ident(inferred.name)
        if isinstance(expr, FunctionCall) and expr.name.startswith("parse_"):
            return "Result_i32_string"
        if isinstance(expr, FunctionCall) and expr.name in self._var_types:
            t = self._var_types[expr.name]
            if t.name.startswith("Result_"):
                return _c_ident(t.name)
        return "Result_i32_string"

    def _is_pointer_expr(self, expr: Expression) -> bool:
        """Return True when field access should use -> (base is a pointer variable)."""
        if isinstance(expr, Variable):
            if expr.name in self._var_types:
                t = self._var_types[expr.name]
                return bool(getattr(t, "is_pointer", False) or t.name.startswith("ptr_"))
        if isinstance(expr, FieldAccess):
            # Prefer the declared field type when the struct is known
            obj_type = self._infer_expr_type(expr.object)
            if obj_type is not None:
                struct_name = obj_type.name
                elem = getattr(obj_type, "element_type", None)
                if struct_name not in self._structs and elem is not None and elem.name in self._structs:
                    struct_name = elem.name
                if struct_name in self._structs:
                    field_type = self._structs[struct_name].get(expr.field)
                    if field_type is not None:
                        return bool(
                            getattr(field_type, "is_pointer", False)
                            or field_type.name.startswith("ptr_")
                        )
            return self._is_pointer_expr(expr.object)
        if isinstance(expr, BinaryOperation) and expr.operator == '+':
            # Pointer arithmetic: ptr + offset yields a pointer
            return self._is_pointer_expr(expr.left) or self._is_pointer_expr(expr.right)
        return False

    def _flatten_string_concat(self, expr: Expression) -> List[Tuple[str, str]]:
        """Flatten a string concatenation expression into (expr_code, type_name) pairs."""
        if isinstance(expr, BinaryOperation) and expr.operator == '+':
            # Check if this is string concatenation
            if self._is_string_expr(expr.left) or self._is_string_expr(expr.right):
                # Recursively flatten
                left_parts = self._flatten_string_concat(expr.left)
                right_parts = self._flatten_string_concat(expr.right)
                return left_parts + right_parts
        
        # Base case: single expression
        if isinstance(expr, Literal) and expr.type.name == 'string':
            return [(self._gen_expr(expr), 'string_literal')]
        elif isinstance(expr, Variable):
            if expr.name in self._var_types:
                var_type = self._var_types[expr.name]
                return [(self._gen_expr(expr), var_type.name)]
            return [(self._gen_expr(expr), 'i32')]
        elif isinstance(expr, FieldAccess):
            expr_type = self._infer_expr_type(expr)
            return [(self._gen_expr(expr), expr_type.name)]
        else:
            expr_type = self._infer_expr_type(expr)
            return [(self._gen_expr(expr), expr_type.name)]

    def _is_struct_type(self, t: Type) -> bool:
        # Check if this is a primitive or built-in type (not a struct)
        if t.name in ["i32", "bool", "void", "auto", "i8", "i16", "i64", "i128",
                     "u8", "u16", "u32", "u64", "u128", "f32", "f64", "string"]:
            return False
        # Pointer types (ptr_*) are not structs
        if t.name.startswith("ptr_") or getattr(t, 'is_pointer', False):
            return False
        # Array types are not structs
        if t.name.startswith("array_"):
            return False
        # Memory reference types (memref_*) are pointers, not structs
        if t.name.startswith("memref_"):
            return False
        # Capability types are not structs
        if t.name.startswith("capability_"):
            return False
        # Vector types are not structs
        if t.name.startswith("vec"):
            return False
        # Escaping function / closure types are fat-pointer typedefs, not structs
        if t.name.startswith("fn_") and "__" in t.name:
            return False
        # Plain C function pointer types are typedefs, not structs
        if t.name.startswith("cfn_") and "__" in t.name:
            return False
        # Spans are two-word view typedefs emitted by _ensure_span_typedef
        if is_span_type_name(t.name):
            return False
        return True

    def _is_fn_type(self, t: Optional[Type]) -> bool:
        return bool(t and getattr(t, "name", "").startswith("fn_") and "__" in t.name)

    def _is_cfn_type(self, t: Optional[Type]) -> bool:
        return bool(t and getattr(t, "name", "").startswith("cfn_") and "__" in t.name)

    def _ensure_cfn_typedef(self, t: Type) -> str:
        """Emit typedef for plain C function pointer cfn(A)->R as R (*)(A)."""
        c_name = _c_ident(t.name)
        if c_name in self._fn_typedefs_emitted:
            return c_name
        self._fn_typedefs_emitted.add(c_name)
        params = list(getattr(t, "type_args", None) or [])
        ret = getattr(t, "element_type", None) or Type("void")
        ret_c = self._c_type(ret)
        param_cs = [self._c_type(p) for p in params]
        fn_params = ", ".join(param_cs) if param_cs else "void"
        self._pending_env_structs.append(
            f"typedef {ret_c} (*{c_name})({fn_params});"
        )
        return c_name

    def _ensure_fn_typedef(self, t: Type) -> str:
        """Emit typedef for escaping closure type (T1,T2)->R as a fat pointer."""
        c_name = _c_ident(t.name)  # fn_i32__i32 → fn_i32__i32
        if c_name in self._fn_typedefs_emitted:
            return c_name
        self._fn_typedefs_emitted.add(c_name)
        params = list(getattr(t, "type_args", None) or [])
        ret = getattr(t, "element_type", None) or Type("void")
        ret_c = self._c_type(ret)
        param_cs = [self._c_type(p) for p in params]
        fn_params = ", ".join(["void*"] + param_cs) if param_cs else "void*"
        self._pending_env_structs.append(
            f"typedef struct {{ {ret_c} (*fn)({fn_params}); void* env; }} {c_name};"
        )
        return c_name

    # --- Spans (docs/language/spans.md) ---------------------------------

    @staticmethod
    def _is_span_type(t: Optional[Type]) -> bool:
        return bool(t is not None and is_span_type_name(getattr(t, "name", "")))

    def _span_element_c_type(self, t: Type) -> str:
        elem = getattr(t, "element_type", None)
        if elem is None:
            elem = Type(span_element_name(t.name))
        return self._c_type(elem)

    def _ensure_span_typedef(self, t: Type) -> str:
        """Emit the two-word view struct for this (element, mutability) pair."""
        c_name = f"flow_{_c_ident(t.name)}"
        if c_name in self._span_typedefs_emitted:
            return c_name
        self._span_typedefs_emitted.add(c_name)
        elem_c = self._span_element_c_type(t)
        qualifier = "" if span_is_mutable(t.name) else "const "
        self._pending_span_typedefs.append(
            f"typedef struct {{ {qualifier}{elem_c} *data; int64_t len; }} {c_name};"
        )
        return c_name

    def _collect_span_typedefs(self, functions, structs, statics) -> None:
        """Walk every declared type so span typedefs precede their first use."""
        for fn in functions or []:
            self._c_type_if_span(getattr(fn, "return_type", None))
            for p in getattr(fn, "parameters", None) or []:
                self._c_type_if_span(p.type)
            body = getattr(fn, "body", None)
            if body is not None:
                self._collect_span_typedefs_in_block(body)
        for decl in structs or []:
            for f in getattr(decl, "fields", None) or []:
                self._c_type_if_span(f.type)
        for st in statics or []:
            self._c_type_if_span(getattr(st, "type", None))

    def _c_type_if_span(self, t: Optional[Type]) -> None:
        if self._is_span_type(t):
            self._ensure_span_typedef(t)

    def _collect_span_typedefs_in_block(self, block) -> None:
        for stmt in getattr(block, "statements", None) or []:
            self._collect_span_typedefs_in_stmt(stmt)

    def _collect_span_typedefs_in_stmt(self, stmt) -> None:
        if isinstance(stmt, VarDecl):
            self._c_type_if_span(stmt.type)
        for attr in ("body", "then_block", "else_block"):
            sub = getattr(stmt, attr, None)
            if isinstance(sub, Block):
                self._collect_span_typedefs_in_block(sub)
        for _, sub in getattr(stmt, "elif_blocks", None) or []:
            if isinstance(sub, Block):
                self._collect_span_typedefs_in_block(sub)
        for case in getattr(stmt, "cases", None) or []:
            sub = getattr(case, "body", None)
            if isinstance(sub, Block):
                self._collect_span_typedefs_in_block(sub)

    def _span_type_for_expr(self, e: Expression) -> Optional[Type]:
        """Best-effort span type of an expression, for context-free emission."""
        if isinstance(e, SliceExpr):
            base = self._infer_expr_type(e.base)
            if self._is_span_type(base):
                elem = base.element_type or Type(span_element_name(base.name))
                return make_span_type(elem, span_is_mutable(base.name))
            elem = getattr(base, "element_type", None)
            if elem is None:
                for prefix in ("ptr_", "array_"):
                    if base is not None and base.name.startswith(prefix):
                        rest = base.name[len(prefix):]
                        parts = rest.split("_", 1)
                        elem = Type(parts[1] if parts[0].isdigit() and len(parts) > 1 else rest)
                        break
            if elem is None:
                return None
            # Without binding mutability the C backend picks the mutable
            # form; the type checker has already rejected illegal borrows.
            return make_span_type(elem, True)
        if isinstance(e, Variable):
            t = self._var_types.get(e.name)
            return t if self._is_span_type(t) else None
        return None

    def _gen_span_borrow(self, arg: Expression, target: Optional[Type]) -> str:
        """Auto-borrow `arg` into the span type `target` (no wrapper in source)."""
        if target is None or not self._is_span_type(target):
            target = self._span_type_for_expr(arg)
        if target is None:
            return self._gen_expr(arg)
        c_name = self._ensure_span_typedef(target)
        elem_c = self._span_element_c_type(target)
        cast = "" if span_is_mutable(target.name) else f"(const {elem_c}*)"

        if isinstance(arg, SliceExpr):
            base_c = self._gen_span_data_ptr(arg.base)
            start = self._gen_expr(arg.start)
            end = self._gen_expr(arg.end)
            return (
                f"(({c_name}){{ .data = {cast}(({base_c}) + ({start})), "
                f".len = (int64_t)(({end}) - ({start})) }})"
            )

        arg_type = self._infer_expr_type(arg)
        if self._is_span_type(arg_type):
            src = self._gen_expr(arg)
            if _c_ident(arg_type.name) == _c_ident(target.name):
                return src
            # const view of a mutable span: same words, different qualifier.
            return (
                f"(({c_name}){{ .data = {cast}({src}).data, "
                f".len = ({src}).len }})"
            )

        if isinstance(arg, ArrayLiteral):
            literal = self._gen_array_literal(arg, as_initializer=False)
            return (
                f"(({c_name}){{ .data = {cast}({literal}), "
                f".len = (int64_t){len(arg.elements)} }})"
            )

        length = getattr(arg_type, "size", None)
        base_c = self._gen_expr(arg)
        if length is None:
            length_c = f"(int64_t)(sizeof({base_c})/sizeof(({base_c})[0]))"
        else:
            length_c = f"(int64_t){length}"
        return f"(({c_name}){{ .data = {cast}({base_c}), .len = {length_c} }})"

    def _gen_span_data_ptr(self, e: Expression) -> str:
        """C expression for the first element address of a contiguous source."""
        t = self._infer_expr_type(e)
        if self._is_span_type(t):
            return f"({self._gen_expr(e)}).data"
        return f"({self._gen_expr(e)})"

    def _wrap_lambda_as_fn_type(self, info: dict, fn_type: Type) -> tuple:
        """Return (c_expr, prelude_lines) converting last lambda into a fat pointer."""
        fat = self._ensure_fn_typedef(fn_type)
        ret_c = info["ret_c"]
        param_cs = info["param_c_types"]
        fn_params = ", ".join(["void* _env"] + [
            f"{ct} a{i}" for i, ct in enumerate(param_cs)
        ])
        call_args = ", ".join(f"a{i}" for i in range(len(param_cs)))
        prelude: List[str] = []
        if info["captures"]:
            env_name = info["env_name"]
            lambda_name = info["lambda_name"]
            # Heap-copy env so the closure can escape the creating stack frame.
            # Under --profile flight (#274) escaping closures are forbidden.
            if self._no_heap_enabled():
                prelude.append(
                    'FLOW_DIAG("flow: escaping closure forbidden under --profile flight (MISRA 21.3)\\n");'
                )
                prelude.append("abort();")
                prelude.append(f"{env_name}* _flow_env = NULL;")
            else:
                # Tracked in the temp arena and released by flow_temp_free_all (#268).
                prelude.append(
                    f"{env_name}* _flow_env = ({env_name}*)flow_temp_alloc(sizeof({env_name}));"
                )
            init_fields = ", ".join(
                f".{_c_ident(cap)} = {self._gen_expr(Variable(cap))}"
                for cap in info["captures"]
            )
            prelude.append(f"*_flow_env = ({env_name}){{ {init_fields} }};")
            cast_fn = f"({ret_c} (*)({', '.join(['void*'] + param_cs)}))"
            expr = (
                f"(({fat}){{ .fn = {cast_fn}&{lambda_name}, .env = _flow_env }})"
            )
            return expr, prelude
        # Non-capturing: bridge void* env away
        bridge = f"{info['lambda_name']}_bridge"
        if call_args:
            body = f"return {info['lambda_name']}({call_args});"
        else:
            body = f"return {info['lambda_name']}();"
        if ret_c == "void":
            body = (
                f"{info['lambda_name']}({call_args});"
                if call_args
                else f"{info['lambda_name']}();"
            )
        self._pending_lambdas.append(
            (bridge, ret_c, fn_params, ["(void)_env;", body])
        )
        expr = f"(({fat}){{ .fn = &{bridge}, .env = NULL }})"
        return expr, prelude

    def _c_type(self, t: Type) -> str:
        if self._is_fn_type(t):
            return self._ensure_fn_typedef(t)
        if self._is_cfn_type(t):
            return self._ensure_cfn_typedef(t)
        if self._is_span_type(t):
            return self._ensure_span_typedef(t)
        if t.name == "auto":
            return "int32_t"  # Default auto-inferred type (standard C)
        if t.name == "i32":
            return "int32_t"
        if t.name == "i64":
            return "int64_t"
        if t.name == "i128":
            return "__int128"
        if t.name == "u128":
            return "unsigned __int128"
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
        if t.name == "c64":
            return "float complex"
        if t.name == "c128":
            return "double complex"
        if t.name == "bool":
            return "bool"
        if t.name == "void":
            return "void"
        if t.name == "string" or t.name == "str":
            return "char*"  # C strings are char pointers
        # Pointer types: ptr<T> parsed as ptr_<T>
        if getattr(t, "is_pointer", False) or t.name.startswith("ptr_"):
            if t.element_type:
                return f"{self._c_type(t.element_type)}*"
            if t.name.startswith("ptr_"):
                pointee = Type(t.name[len("ptr_"):])
                return f"{self._c_type(pointee)}*"
            return "void*"
        # Memory reference types: memref<T> or memref_<T> - these are array-like pointers
        if t.name.startswith("memref_"):
            elem_type_name = t.name[len("memref_"):]
            return f"{self._c_type(Type(elem_type_name))}*"
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
        # Array types: array_i32, array_f32, array_5_f32, etc.
        if t.name.startswith("array_"):
            if t.element_type:
                elem_c_type = self._c_type(t.element_type)
                return f"{elem_c_type}*"  # Arrays as pointers in C
            # Parse element type from name: array_f32 or array_5_f32
            elem_type_name = t.name.replace("array_", "")
            # Skip size prefix if present (e.g., "5_f32" -> "f32")
            if "_" in elem_type_name:
                parts = elem_type_name.split("_")
                # Check if first part is a number (size)
                if parts[0].isdigit():
                    elem_type_name = "_".join(parts[1:])
            elem_type = Type(elem_type_name)
            return f"{self._c_type(elem_type)}*"
        # Capability types: capability_EffectName -> void* (opaque handle, unused at runtime)
        # The actual dispatch happens via the effect handler vtable
        if t.name.startswith("capability_"):
            return "void*"
        # Struct/enum/trait types - sanitize for safe C identifiers
        return _c_ident(t.name)

    def _can_use_static_linkage(self, fn: FunctionDecl) -> bool:
        """True when `static` may be added to this function without breaking a
        caller outside the translation unit.

        `main`, exported functions, `@flow_api` functions and everything in a
        `--library` build keep external linkage: another object file may name
        the symbol.
        """
        if self._library:
            return False
        if getattr(fn, "is_exported", False):
            return False
        if "flow_api" in (getattr(fn, "attributes", None) or []):
            return False
        if fn.name == "main":
            return False
        return True

    def _c_attribute_prefix(self, fn: FunctionDecl) -> str:
        """Lower Flow function attributes to C declaration specifiers.

        `@inline`         -> `static inline` (`extern inline` when the symbol
                             must stay externally visible)
        `@always_inline`  -> `__attribute__((always_inline))` plus the same
                             inline specifier
        `@noinline`       -> `__attribute__((noinline))`
        `@target("...")`  -> `__attribute__((target("...")))`

        Declarations without a body in this translation unit (`extern`, forward
        declarations) get nothing: an inline specifier there would promise a
        definition the backend never emits.
        """
        attrs = getattr(fn, "attributes", None) or []
        if not attrs:
            return ""
        if getattr(fn, "is_extern", False) or getattr(fn, "is_forward_decl", False):
            return ""

        names = set()
        target_spec = None
        for attr in attrs:
            name, args = parse_attribute(attr)
            if name == "target":
                if args:
                    target_spec = normalize_target_spec(",".join(args))
            else:
                names.add(name)

        parts: List[str] = []
        if "noinline" in names:
            parts.append("__attribute__((noinline))")
        elif "always_inline" in names:
            parts.append("__attribute__((always_inline))")
        if target_spec:
            problem = validate_target_spec(target_spec)
            if problem:
                # Never splice an unvalidated string into generated C.
                raise ValueError(f"{problem} (on function '{fn.name}')")
            parts.append(f'__attribute__((target("{target_spec}")))')
        # `inline` is only a hint, so it is dropped when `@noinline` also
        # applies; the type checker rejects that combination anyway.
        if ("inline" in names or "always_inline" in names) and "noinline" not in names:
            if self._can_use_static_linkage(fn):
                parts.append("static inline")
            else:
                # C99 `extern inline` = inline hint *and* an external
                # definition, so the symbol still links from other objects.
                parts.append("extern inline")

        return (" ".join(parts) + " ") if parts else ""

    def _c_function_decl(self, fn: FunctionDecl, use_mangled: bool = True) -> str:
        ret = self._c_type(fn.return_type)
        if getattr(fn, "is_variadic", False):
            if fn.parameters:
                params = ", ".join([f"{self._c_type(p.type)} {_c_ident(p.name)}" for p in fn.parameters])
                params += ", ..."
            else:
                # `int printf(...)` has no void slot; a lone `...` is the whole list.
                params = "..."
        elif fn.parameters:
            params = ", ".join([f"{self._c_type(p.type)} {_c_ident(p.name)}" for p in fn.parameters])
        else:
            # Important for system headers: `f()` (K&R) can conflict with `f(void)`.
            params = "void"
        # Use mangled name if function has overloads
        name = fn.name
        if use_mangled and id(fn) in self._mangled_names:
            name = self._mangled_names[id(fn)]
        name = _c_ident(name)
        return f"{self._c_attribute_prefix(fn)}{ret} {name}({params})"

    def _sizeof_c_type_from_mangled(self, mangled_suffix: str) -> str:
        """Map sizeof_<Type> mangled suffix to a C type name."""
        prim = {
            "i8": "int8_t", "u8": "uint8_t",
            "i16": "int16_t", "u16": "uint16_t",
            "i32": "int32_t", "u32": "uint32_t",
            "i64": "int64_t", "u64": "uint64_t",
            "i128": "__int128", "u128": "unsigned __int128",
            "f32": "float", "f64": "double",
            "bool": "bool", "void": "void",
        }
        if mangled_suffix in prim:
            return prim[mangled_suffix]
        if mangled_suffix == "ptr":
            return "void*"
        if mangled_suffix.startswith("ptr_"):
            return "void*"
        return _c_ident(mangled_suffix)

    def _gen_function(self, fn: FunctionDecl) -> List[str]:
        # Extern functions are declarations only (no emitted definition).
        if getattr(fn, "is_extern", False):
            return []
        # Forward declarations are declarations only (already have forward decl).
        if getattr(fn, "is_forward_decl", False):
            return []
        # sizeof<T>() intrinsic — monomorphizes to sizeof_i32 etc.; emit C sizeof.
        # Keep the declared return type so the definition matches the forward
        # declaration (stdlib defines e.g. `sizeof_i32() -> i32`).
        if fn.name.startswith("sizeof_") and len(fn.parameters) == 0:
            c_ty = self._sizeof_c_type_from_mangled(fn.name[len("sizeof_"):])
            c_ret = self._c_type(fn.return_type)
            return [
                f"{c_ret} {_c_ident(fn.name)}(void) {{ "
                f"return ({c_ret})sizeof({c_ty}); }}"
            ]
        # Skip math functions that are provided by the standard library
        # BUT only if they take primitive float types (not custom types like Dual)
        math_functions = {'sin', 'cos', 'tan', 'sqrt', 'fabs', 'abs', 'log', 'exp', 'pow', 'tanh'}
        if fn.name in math_functions:
            # Only skip if all parameters are primitive types
            primitives = {'f32', 'f64', 'c64', 'c128', 'i32', 'i64', 'float', 'double', 'int'}
            all_primitive = all(
                self._type_to_string(p.type) in primitives 
                for p in fn.parameters
            )
            if all_primitive:
                return []  # Skip - this is the C math function
        
        lines: List[str] = []

        # Debugger support: map generated C back to FLOW source (coarse, function-level).
        # This enables LLDB/GDB to show the .flow filename + approximate line on entry.
        if self._debug_info and self._source_file and getattr(fn, "location", None):
            # SourceLocation uses 0-based lines; C #line uses 1-based.
            try:
                src_line = int(fn.location.line) + 1
                lines.append(f'#line {src_line} "{self._source_file}"')
            except Exception:
                pass

        # FiberAsync programs: emit user main as __flow_main_body and wrap with
        # flow_fiber_run_main so park/yield suspend real Flow frames mid-function.
        is_fiber_main = (
            self._uses_fiber_main
            and fn.name == "main"
            and len(fn.parameters) == 0
            and not self._library
        )
        if is_fiber_main:
            lines.append("static int32_t __flow_main_body(void) {")
        else:
            lines.append(self._c_function_decl(fn, use_mangled=True) + " {")
        self._indent += 1
        
        # Save current var_types scope and create new scope for this function
        self._current_fn_name = fn.name
        saved_var_types = self._var_types.copy()
        saved_resolver_var_types = self._overload_resolver._var_types.copy()
        saved_return_type = self._current_return_type
        saved_closure_vars = self._closure_vars.copy()
        saved_fnptr_vars = self._fnptr_vars.copy()
        self._current_return_type = fn.return_type
        
        # Track parameter types for overload resolution and effect call handling
        for param in fn.parameters:
            self._overload_resolver.set_var_type(param.name, self._type_to_string(param.type))
            self._var_types[param.name] = param.type
            if self._is_fn_type(param.type):
                self._fn_fat_vars.add(param.name)
                self._ensure_fn_typedef(param.type)

        # Tail-call optimization: if the function is self-recursive at the tail
        # (a `return self(...)` in tail position) and has no defers, rewrite the
        # body into a `for(;;)` loop that reassigns the parameters and continues.
        # This converts recursion into constant-stack iteration (Roc's loop story).
        tco_tail = self._tail_self_calls(fn)
        self._current_tco_fn = fn.name if tco_tail else None
        self._current_tco_params = [p.name for p in fn.parameters] if tco_tail else []
        if tco_tail:
            lines.append(f"{self._i()}for (;;) {{")
            self._indent += 1

        lines.extend(self._gen_block(fn.body))

        if tco_tail:
            self._indent -= 1
            lines.append(f"{self._i()}}}")
            # The loop is the only exit; emit a defensive return so C always
            # sees a return path even though it is unreachable.
            ret_type = fn.return_type
            if ret_type and ret_type.name not in ("void", "auto") and ret_type.name:
                lines.append(f"{self._i()}return {self._zero_value_for_c_type(ret_type)};")
            else:
                lines.append(f"{self._i()}return;")
        self._current_tco_fn = None
        self._current_tco_params = []
        
        # Restore var_types scope
        self._var_types = saved_var_types
        self._overload_resolver._var_types = saved_resolver_var_types
        self._current_return_type = saved_return_type
        self._closure_vars = saved_closure_vars
        self._fnptr_vars = saved_fnptr_vars
        self._indent -= 1
        lines.append("}")
        if is_fiber_main:
            lines.append("")
            lines.append("/* FiberAsync: main runs on a fiber (mid-function suspend). */")
            lines.append("extern int32_t flow_fiber_run_main(int32_t (*fn)(void));")
            lines.append("int main(void) { return (int)flow_fiber_run_main(__flow_main_body); }")
        return lines

    def _zero_value_for_c_type(self, t: Type) -> str:
        """Return a valid zero-valued C expression for a Flow type.

        Used for the (unreachable) return after a TCO loop.
        """
        name = t.name if hasattr(t, "name") else ""
        if name in ("bool",):
            return "false"
        if name in ("f32", "f64", "float", "double"):
            return "0.0"
        if name in ("c64",):
            return "(0.0f + 0.0f * I)"
        if name in ("c128",):
            return "(0.0 + 0.0 * I)"
        if name in ("string", "str"):
            return '""'
        if name.startswith("ptr_") or getattr(t, "is_pointer", False) or name.startswith("array_"):
            return "NULL"
        return "0"

    def _tail_self_calls(self, fn: FunctionDecl) -> bool:
        """Detect whether a function has a self-recursive call in tail position.

        Tail position means the call's value is what the function returns on
        every path (the last statement of the body, or the last statement of
        every branch of a trailing if/else). When true, `_gen_function` wraps
        the body in a `for(;;)` loop and `return self(...)` becomes a parameter
        reassignment + `continue`.
        """
        if getattr(fn, "has_self", False) or getattr(fn, "is_closure", False):
            return False
        # No parameters to iterate on means a self-call cannot lower to a loop.
        if not fn.parameters:
            return False
        body = fn.body
        if any(isinstance(s, DeferStatement) for s in body.statements):
            return False
        return self._block_has_tail_self_call(body, fn.name, len(fn.parameters))

    def _block_has_tail_self_call(self, block: "Block", fn_name: str, nparams: int) -> bool:
        """Recursively check a block's tail statements for a self-call."""
        if not block.statements:
            return False
        return self._statement_is_tail_self_call(block.statements[-1], fn_name, nparams)

    def _statement_is_tail_self_call(
        self, st: "Statement", fn_name: str, nparams: int
    ) -> bool:
        """Check a single tail statement (or trailing if/else) for a self-call.

        A statement is a "tail" position when every path through it is a path
        out of the function (a return or self-call). We return True if it (a)
        is guaranteed to terminate (every branch ends in a return / self-call)
        and (b) contains at least one self-call among those terminal returns.
        """
        if isinstance(st, ReturnStatement):
            return self._return_is_self_call(st, fn_name, nparams)
        if isinstance(st, IfStatement):
            # Every branch must terminate the function for the if to be in tail
            # position (then the whole if returns → the loop can resume only via
            # a self call). At least one branch must be a self call.
            branches = [st.then_block] + [b for _, b in st.elif_blocks]
            if st.else_block:
                branches.append(st.else_block)
            else:
                # No else: if the condition is false the statement does not
                # terminate → not a tail position.
                return False
            has_self = False
            for b in branches:
                if not self._statement_terminates(b, fn_name, nparams):
                    return False
                if self._statement_is_tail_self_call(b, fn_name, nparams):
                    has_self = True
            return has_self
        if isinstance(st, Block):
            return self._block_has_tail_self_call(st, fn_name, nparams)
        return False

    def _statement_terminates(self, st: "Statement", fn_name: str, nparams: int) -> bool:
        """Whether every path through `st` ends in a return (or self tail call)."""
        if isinstance(st, ReturnStatement):
            return st.value is not None or fn_name is not None
        if isinstance(st, IfStatement):
            if st.else_block is None:
                return False
            branches = [st.then_block] + [b for _, b in st.elif_blocks] + [st.else_block]
            return all(self._statement_terminates(b, fn_name, nparams) for b in branches)
        if isinstance(st, Block):
            if not st.statements:
                return False
            return self._statement_terminates(st.statements[-1], fn_name, nparams)
        return False

    def _statement_has_nonlocal_return(self, st: "Statement") -> bool:
        if isinstance(st, ReturnStatement):
            return True
        if isinstance(st, IfStatement):
            return any(
                self._statement_has_nonlocal_return(s)
                for s in [st.then_block] + [b for _, b in st.elif_blocks]
                + ([st.else_block] if st.else_block else [])
            )
        if isinstance(st, WhileStatement):
            return self._statement_has_nonlocal_return(st.body)
        if isinstance(st, ForStatement):
            return self._statement_has_nonlocal_return(st.body)
        if isinstance(st, Block):
            return self._statement_has_nonlocal_return(st)
        return False

    def _return_is_self_call(self, st: "ReturnStatement", fn_name: str, nparams: int) -> bool:
        if not st.value:
            return False
        if not isinstance(st.value, FunctionCall):
            return False
        # The body references the (mangled) call name, e.g. `countdown_i32_i32`,
        # while `fn_name` is the unmangled `countdown`. Compare base names.
        call_name = st.value.name
        if fn_name != call_name and not call_name.startswith(fn_name + "_"):
            return False
        # A self tail call must pass exactly the function's parameters (the
        # loop reassigns them), which is the usual accumulator pattern.
        return len(st.value.arguments) == nparams

    def _tco_loop_continue(self, call: FunctionCall) -> List[str]:
        """Lower a self-recursive tail call to param reassignment + continue.

        Each argument is captured into a temp first so the reassignments don't
        clobber each other (e.g. `f(n - 1, acc + n)`).
        """
        lines: List[str] = []
        temps = []
        for i, arg in enumerate(call.arguments):
            arg_c = self._gen_expr(arg)
            t = f"_tco_{i}_{id(call) & 0xFFFF}"
            temps.append(t)
            param_name = self._current_tco_params[i]
            ptype = self._var_types.get(param_name)
            ctype = self._c_type(ptype) if ptype else "int32_t"
            lines.append(f"{self._i()}{ctype} {t} = {arg_c};")
        for i, param in enumerate(self._current_tco_params):
            lines.append(f"{self._i()}{_c_ident(param)} = {temps[i]};")
        lines.append(f"{self._i()}continue;")
        return lines

    def _gen_defers(self, defers: List[DeferStatement]) -> List[str]:
        """Emit deferred expressions in LIFO order."""
        lines: List[str] = []
        for defer_stmt in reversed(defers):
            expr = defer_stmt.expr
            if isinstance(expr, FunctionCall):
                lines.append(f"{self._i()}{self._gen_expr(expr)};")
            else:
                lines.append(f"{self._i()}(void)({self._gen_expr(expr)});")
        return lines

    def _gen_block(self, block: Block) -> List[str]:
        lines: List[str] = []
        defer_stack: List[DeferStatement] = []
        returned = False
        for st in block.statements:
            if isinstance(st, DeferStatement):
                defer_stack.append(st)
                continue
            if isinstance(st, ReturnStatement):
                lines.extend(self._gen_defers(defer_stack))
                defer_stack.clear()
                returned = True
            lines.extend(self._gen_statement(st, defer_stack))
        if defer_stack and not returned:
            lines.extend(self._gen_defers(defer_stack))
        return lines

    def _debug_line_for(self, node: Any) -> List[str]:
        """Emit a #line directive mapping generated C back to Flow source."""
        if not self._debug_info or not self._source_file:
            return []
        loc = getattr(node, "location", None)
        if loc is None:
            return []
        try:
            src_line = int(loc.line) + 1
        except Exception:
            return []
        # Escape backslashes/quotes so paths survive the C preprocessor.
        path = str(self._source_file).replace("\\", "\\\\").replace('"', '\\"')
        return [f'#line {src_line} "{path}"']

    def _gen_statement(self, st: Statement, defer_stack: List[DeferStatement] | None = None) -> List[str]:
        if defer_stack is None:
            defer_stack = []
        prefix = self._debug_line_for(st)
        body = self._gen_statement_body(st, defer_stack)
        if not prefix:
            return body
        # Indent #line like surrounding code so nested blocks stay readable;
        # the preprocessor ignores leading whitespace on #line.
        out = [f"{self._i()}{prefix[0]}"] + body
        # Extra map for initializers / return values when they carry their own
        # location (finer stepping inside multi-part statements).
        if self._debug_info:
            extra_node = None
            if isinstance(st, VarDecl) and st.initializer is not None:
                extra_node = st.initializer
            elif isinstance(st, ReturnStatement) and getattr(st, "value", None) is not None:
                extra_node = st.value
            if extra_node is not None:
                extra = self._debug_line_for(extra_node)
                if extra and extra != prefix:
                    # Place before the generated body line (after stmt #line).
                    out = [f"{self._i()}{prefix[0]}", f"{self._i()}{extra[0]}"] + body
        return out

    def _gen_statement_body(self, st: Statement, defer_stack: List[DeferStatement]) -> List[str]:
        if isinstance(st, VarDecl):
            # A local declaration shadows any same-named captured variable
            # for the rest of this lambda body.
            if self._capture_stack:
                self._capture_stack[-1].discard(st.name)

            # Lambda initializers get closure-aware declarations.
            if isinstance(st.initializer, Lambda):
                return self._gen_lambda_decl(st)

            decl_type = st.type
            if decl_type and decl_type.name == "auto":
                if st.initializer is not None:
                    decl_type = self._infer_expr_type(st.initializer)
                else:
                    # No initializer; fall back to i32 to keep C code valid
                    decl_type = Type("i32")

            # A span local holds a borrow, so the initializer is borrowed
            # into the declared view type rather than assigned verbatim.
            if self._is_span_type(decl_type):
                self._overload_resolver.set_var_type(st.name, decl_type.name)
                self._var_types[st.name] = decl_type
                c_t = self._c_type(decl_type)
                safe_name = _sanitize_identifier(st.name)
                if st.initializer is None:
                    return [f"{self._i()}{c_t} {safe_name} = {{0}};"]
                borrowed = self._gen_span_borrow(st.initializer, decl_type)
                return [f"{self._i()}{c_t} {safe_name} = {borrowed};"]

            # Track variable type for overload resolution and expression inference
            self._overload_resolver.set_var_type(st.name, self._type_to_string(decl_type))
            self._var_types[st.name] = decl_type
            if self._is_fn_type(decl_type):
                self._fn_fat_vars.add(st.name)

            # Sized arrays: prefer real stack arrays (e.g. `int32_t a[16]`) so indexing works.
            if decl_type and decl_type.name.startswith("array_") and decl_type.size and decl_type.element_type:
                elem_c = self._c_type(decl_type.element_type)
                size = decl_type.size
                if st.initializer is None:
                    return [f"{self._i()}{elem_c} {st.name}[{size}];"]
                if isinstance(st.initializer, ArrayLiteral):
                    return [f"{self._i()}{elem_c} {st.name}[{size}] = {self._gen_array_literal(st.initializer, as_initializer=True)};"]
                # For other initializers (e.g., function call returning array, variable copy),
                # declare the array and use memcpy
                init_expr = self._gen_expr(st.initializer)
                return [
                    f"{self._i()}{elem_c} {st.name}[{size}];",
                    f"{self._i()}memcpy({st.name}, {init_expr}, sizeof({st.name}));"
                ]

            c_t = self._c_type(decl_type)
            safe_name = _sanitize_identifier(st.name)
            if st.initializer is None:
                return [f"{self._i()}{c_t} {safe_name};"]
            # If mono left a bare generic literal name but the decl type is
            # specialized (`Pair` vs `Pair_i32_bool`), retarget the literal
            # so the compound cast matches the variable type.
            init = st.initializer
            if (
                isinstance(init, StructLiteral)
                and decl_type
                and getattr(decl_type, "name", None)
                and init.struct_name != decl_type.name
                and decl_type.name.startswith(init.struct_name + "_")
            ):
                init = StructLiteral(decl_type.name, init.fields)
            init_expr = self._gen_expr(init)
            if getattr(decl_type, "is_pointer", False) or decl_type.name.startswith("ptr_"):
                # Flow permits implicit pointer conversions (e.g. ptr<u8> ->
                # ptr<HashEntry>); modern clang treats the uncasted C as an
                # error, so make the conversion explicit.
                init_expr = f"({c_t})({init_expr})"
            return [f"{self._i()}{c_t} {safe_name} = {init_expr};"]

        if isinstance(st, Assignment):
            # Handle array element assignment: arr[i] = value
            if st.target_expr is not None:
                target_expr = self._gen_lvalue_expr(st.target_expr)
                return [f"{self._i()}{target_expr} = {self._gen_expr(st.value)};"]
            target_name = _sanitize_identifier(st.target)
            if self._capture_stack and st.target in self._capture_stack[-1]:
                # Assigning to a captured variable mutates the closure's own
                # by-value copy; the original stays untouched.
                target_name = f"_env->{target_name}"
            # Sized array variables are represented as C arrays (e.g.
            # `int32_t scale[7]`), which cannot be reassigned with `=` even
            # when the RHS is a function returning the same array<T, N> type
            # (which decays to a pointer in C). Use memcpy for those instead.
            target_type = self._var_types.get(st.target)
            if self._is_span_type(target_type):
                borrowed = self._gen_span_borrow(st.value, target_type)
                return [f"{self._i()}{target_name} = {borrowed};"]
            if (target_type and getattr(target_type, "name", "").startswith("array_")
                    and getattr(target_type, "size", None)):
                value_expr = self._gen_expr(st.value)
                return [f"{self._i()}memcpy({target_name}, {value_expr}, sizeof({target_name}));"]
            return [f"{self._i()}{target_name} = {self._gen_expr(st.value)};"]

        if isinstance(st, ReturnStatement):
            if st.value is None:
                return [f"{self._i()}return;"]
            # Tail-call optimization: a self-recursive call in tail position
            # becomes parameter reassignment + `continue` inside the loop.
            if (
                self._current_tco_fn
                and isinstance(st.value, FunctionCall)
                and (
                    st.value.name == self._current_tco_fn
                    or st.value.name.startswith(self._current_tco_fn + "_")
                )
                and len(st.value.arguments) == len(self._current_tco_params)
            ):
                return self._tco_loop_continue(st.value)
            # Escaping: return a lambda as a fat-pointer `(T)->R` value.
            if isinstance(st.value, Lambda) and self._is_fn_type(self._current_return_type):
                self._gen_lambda(st.value)
                info = self._last_lambda_info
                expr, prelude = self._wrap_lambda_as_fn_type(info, self._current_return_type)
                lines = [f"{self._i()}{line}" for line in prelude]
                lines.append(f"{self._i()}return {expr};")
                return lines
            # Returning a span borrows into the declared view type.
            if self._is_span_type(self._current_return_type):
                return [
                    f"{self._i()}return "
                    f"{self._gen_span_borrow(st.value, self._current_return_type)};"
                ]
            return [f"{self._i()}return {self._gen_expr(st.value)};"]

        if isinstance(st, IfStatement):
            return self._gen_if(st)

        if isinstance(st, WhileStatement):
            return self._gen_while(st)

        if isinstance(st, ForStatement):
            return self._gen_for(st)
        
        if isinstance(st, HandleStatement):
            return self._gen_handle(st)

        if isinstance(st, LayoutStatement):
            return self._gen_layout(st)
        
        if isinstance(st, MatchStatement):
            return self._gen_match(st)

        if isinstance(st, DeferStatement):
            return []  # Collected by _gen_block

        # Runtime assertion: `expect <expr>` aborts with a diagnostic if false.
        if isinstance(st, ExpectStatement):
            cond = self._gen_expr(st.condition)
            return [
                f"{self._i()}if (!({cond})) {{",
                f"{self._i()}    fprintf(stderr, \"expect failed (line {st.line})\\n\");",
                f"{self._i()}    exit(1);",
                f"{self._i()}}}",
            ]

        # Loop control: dedicated AST nodes map straight to the C keywords.
        if isinstance(st, BreakStatement):
            return [f"{self._i()}break;"]
        if isinstance(st, ContinueStatement):
            return [f"{self._i()}continue;"]

        # Expression statement
        if self._is_bare_expr_stmt(st):
            return [f"{self._i()}{self._gen_expr(st)};"]

        raise NotImplementedError(f"Unsupported statement: {type(st)}")

    @staticmethod
    def _is_bare_expr_stmt(st: object) -> bool:
        """True if `st` is an expression used as a statement (not a control stmt)."""
        return isinstance(
            st,
            (
                Literal,
                Variable,
                BinaryOperation,
                UnaryOperation,
                FunctionCall,
                EffectCall,
                MethodCall,
                SortExpr,
                FindExpr,
                FieldAccess,
                ArrayAccess,
                CastExpression,
                TryExpr,
                StructLiteral,
                ArrayLiteral,
                VectorLiteral,
                Lambda,
                RecordUpdate,
            ),
        )

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
        bound = getattr(st, "max_iterations", None)
        if bound is not None:
            if not hasattr(self, "_while_bound_counter"):
                self._while_bound_counter = 0
            self._while_bound_counter += 1
            ctr = f"__flow_while_bound_{self._while_bound_counter}"
            lines.append(f"{self._i()}{{")
            self._indent += 1
            lines.append(f"{self._i()}int32_t {ctr} = 0;")
            lines.append(f"{self._i()}while ({self._gen_expr(st.condition)}) {{")
            self._indent += 1
            lines.append(f"{self._i()}if ({ctr} >= {int(bound)}) {{")
            self._indent += 1
            lines.append(
                f'{self._i()}fprintf(stderr, "flow: while exceeded @max_iterations({int(bound)})\\n");'
            )
            lines.append(f"{self._i()}abort();")
            self._indent -= 1
            lines.append(f"{self._i()}}}")
            lines.append(f"{self._i()}{ctr}++;")
            lines.extend(self._gen_block(st.body))
            self._indent -= 1
            lines.append(f"{self._i()}}}")
            self._indent -= 1
            lines.append(f"{self._i()}}}")
            return lines
        lines.append(f"{self._i()}while ({self._gen_expr(st.condition)}) {{")
        self._indent += 1
        lines.extend(self._gen_block(st.body))
        self._indent -= 1
        lines.append(f"{self._i()}}}")
        return lines
    
    @staticmethod
    def _loop_body_is_simple(st: ForStatement) -> bool:
        """True when the loop body is safe to auto-vectorize.

        A loop is vectorizable when it contains only straight-line
        assignments with no function calls, no control flow (if/match),
        and no break/continue. Anything with data-dependent behavior
        must stay serial (#414).
        """
        from flow.parser import (
            IfStatement, MatchStatement, BreakStatement, ContinueStatement,
            FunctionCall, MethodCall, ReturnStatement, WhileStatement,
            ForStatement as NestedFor,
        )
        def _check_stmt(stmt) -> bool:
            if isinstance(stmt, (IfStatement, MatchStatement, BreakStatement,
                                 ContinueStatement, ReturnStatement,
                                 WhileStatement, NestedFor)):
                return False
            if isinstance(stmt, (FunctionCall, MethodCall)):
                return False
            for attr in ("value", "initializer", "condition", "target", "target_expr"):
                val = getattr(stmt, attr, None)
                if val is not None and not _check_expr(val):
                    return False
            return True
        def _check_expr(expr) -> bool:
            if isinstance(expr, (FunctionCall, MethodCall)):
                return False
            for attr in ("left", "right", "operand", "expr", "array", "index",
                         "object", "field", "base", "value", "callee", "condition"):
                val = getattr(expr, attr, None)
                if val is not None and not _check_expr(val):
                    return False
            if hasattr(expr, "arguments"):
                for arg in (expr.arguments or []):
                    if not _check_expr(arg):
                        return False
            if hasattr(expr, "statements"):
                for s in (expr.statements or []):
                    if not _check_stmt(s):
                        return False
            return True
        body = getattr(st, "body", None)
        if body is None:
            return True
        for stmt in getattr(body, "statements", []):
            if not _check_stmt(stmt):
                return False
        return True

    def _gen_for(self, st: ForStatement) -> List[str]:
        """Generate C for loop from FLOW for statement.

        `parallel for` emits an OpenMP pragma (canonical ascending form) when
        the compiler defines `_OPENMP`. Without OpenMP the loop is correct and
        serial — see docs/language/concurrency-vs-go.md.
        """
        lines: List[str] = []
        var = st.variable
        safe_var = _c_ident(var)
        start = self._gen_expr(st.range_start)
        end = self._gen_expr(st.range_end)
        has_explicit_step = st.step is not None
        step = self._gen_expr(st.step) if st.step else "1"
        if not hasattr(self, "_for_counter"):
            self._for_counter = 0
        self._for_counter += 1
        step_var = f"__flow_step_{self._for_counter}"
        
        # Track the loop variable type
        self._var_types[var] = Type("i32")
        self._overload_resolver.set_var_type(var, "i32")

        is_parallel = getattr(st, "is_parallel", False)
        if is_parallel:
            self._uses_parallel_for = True

        lines.append(f"{self._i()}int32_t {step_var} = {step};")
        # Vectorization pragmas were always-on (#113) but unsafe for loops
        # with data-dependent control flow or floating-point accumulation
        # (#414). Now only emitted when the loop body is trivially
        # vectorizable: no function calls, no if/match, no break/continue.
        if not is_parallel and has_explicit_step and self._loop_body_is_simple(st):
            lines.append(f"{self._i()}#pragma clang loop vectorize(enable) interleave(enable)")
            lines.append(f"{self._i()}#pragma GCC ivdep")
        if is_parallel:
            # OpenMP needs a canonical ascending for; descending stays serial.
            lines.append(f"{self._i()}if ({step_var} > 0) {{")
            self._indent += 1
            lines.append(f"{self._i()}#ifdef _OPENMP")
            lines.append(f"{self._i()}#pragma omp parallel for")
            lines.append(f"{self._i()}#endif")
            lines.append(
                f"{self._i()}for (int32_t {safe_var} = {start}; "
                f"{safe_var} < {end}; {safe_var} += {step_var}) {{"
            )
            self._indent += 1
            lines.extend(self._gen_block(st.body))
            self._indent -= 1
            lines.append(f"{self._i()}}}")
            self._indent -= 1
            lines.append(f"{self._i()}}} else if ({step_var} < 0) {{")
            self._indent += 1
            lines.append(
                f"{self._i()}for (int32_t {safe_var} = {start}; "
                f"{safe_var} > {end}; {safe_var} += {step_var}) {{"
            )
            self._indent += 1
            lines.extend(self._gen_block(st.body))
            self._indent -= 1
            lines.append(f"{self._i()}}}")
            self._indent -= 1
            lines.append(f"{self._i()}}}")
            return lines

        if not has_explicit_step:
            # No explicit step: direction depends on start vs end at runtime.
            # Use a runtime-computed step of +1 or -1 based on the range.
            # `to` is exclusive in both directions: `0 to 4` gives 0,1,2,3;
            # `4 to 0` gives 4,3,2,1.
            lines.append(
                f"{self._i()}for (int32_t {safe_var} = {start}; "
                f"({start} <= {end}) ? {safe_var} < {end} : {safe_var} > {end}; "
                f"{safe_var} += ({start} <= {end}) ? 1 : -1) {{"
            )
        else:
            lines.append(
                f"{self._i()}for (int32_t {safe_var} = {start}; "
                f"({step_var} > 0) ? {safe_var} < {end} : {safe_var} > {end}; "
                f"{safe_var} += {step_var}) {{"
            )
        self._indent += 1
        lines.extend(self._gen_block(st.body))
        self._indent -= 1
        lines.append(f"{self._i()}}}")
        return lines
    
    def _gen_literal_eq_cond(self, match_expr: str, literal: "Literal") -> str:
        """Generate an equality condition between match_expr and a literal pattern."""
        if literal.type.name == 'string':
            return f'(strcmp({match_expr}, {self._gen_expr(literal)}) == 0)'
        return f"({match_expr}) == {self._gen_expr(literal)}"

    def _gen_struct_pattern_match(
        self, pattern: "StructPattern", value_expr: str
    ) -> Tuple[List[str], List[str]]:
        """Recursively lower a (possibly nested) StructPattern against `value_expr`.

        Returns `(conds, binds)`: `conds` are C boolean expressions that must
        all hold for the pattern to match (literal field checks, recursively
        including any nested struct sub-patterns); `binds` are C variable
        declarations to run once the match succeeds (both this pattern's own
        bindings and any collected from nested struct patterns).
        """
        conds: List[str] = []
        binds: List[str] = []
        struct_name = pattern.struct_name
        if struct_name not in self._structs:
            return conds, binds

        field_names = list(self._structs[struct_name].keys())
        field_literals = pattern.field_literals or {}
        field_patterns = pattern.field_patterns or {}
        for i, binding in enumerate(pattern.bindings):
            if i >= len(field_names):
                continue
            field = field_names[i]
            ft = self._structs[struct_name][field]
            field_access = f"({value_expr}).{_c_ident(field)}"

            if i in field_patterns:
                nested_conds, nested_binds = self._gen_struct_pattern_match(
                    field_patterns[i], field_access
                )
                conds.extend(nested_conds)
                binds.extend(nested_binds)
                continue
            if i in field_literals:
                # Nested literal pattern: value must match, no binding.
                conds.append(self._gen_literal_eq_cond(field_access, field_literals[i]))
                continue
            if binding == "_":
                continue

            bind_name = _c_ident(binding)
            binds.append(f"{self._c_type(ft)} {bind_name} = {field_access}")
            self._overload_resolver.set_var_type(binding, self._type_to_string(ft))
            self._var_types[binding] = ft

        return conds, binds

    def _gen_list_pattern_match(
        self, pattern: "ListPattern", value_expr: str, elem_type: Optional[Type] = None
    ) -> Tuple[List[str], List[str]]:
        """Lower a ListPattern against `value_expr` (a C array expression).

        Returns `(conds, binds)` like `_gen_struct_pattern_match`: `conds` are
        C boolean expressions that must all hold (literal element checks);
        `binds` are C variable declarations for the element bindings. Element
        type comes from the match value's array type when known, else from the
        first literal element, else i32.
        """
        conds: List[str] = []
        binds: List[str] = []
        if elem_type is None or elem_type.name in ("auto", "void", "i32"):
            for elem in pattern.elements:
                if isinstance(elem, Literal) and elem.type.name != "string":
                    elem_type = elem.type
                    break
        if elem_type is None:
            elem_type = Type("i32")
        c_elem = self._c_type(elem_type)
        for i, elem in enumerate(pattern.elements):
            access = f"{value_expr}[{i}]"
            if isinstance(elem, Literal):
                conds.append(self._gen_literal_eq_cond(access, elem))
            elif isinstance(elem, Variable) and elem.name != "_":
                binds.append(f"{c_elem} {_c_ident(elem.name)} = {access}")
                self._overload_resolver.set_var_type(elem.name, elem_type.name)
                self._var_types[elem.name] = elem_type
        return conds, binds

    def _gen_match(self, st: MatchStatement) -> List[str]:
        """Generate C switch/if-else chain from FLOW match statement."""
        lines: List[str] = []
        match_expr = self._gen_expr(st.value)

        def _is_int_literal(lit: "Literal") -> bool:
            return isinstance(lit, Literal) and lit.type.name in (
                'i32', 'i64', 'i8', 'i16', 'u8', 'u16', 'u32', 'u64'
            )

        # A `break` or `continue` in an arm targets the enclosing Flow loop, but
        # inside a C switch `break` would bind to the switch instead and let the
        # loop keep running. Fall back to an if/else chain for those shapes.
        def _arm_breaks_out(node: object, depth: int = 0) -> bool:
            if isinstance(node, (BreakStatement, ContinueStatement)):
                return True
            # Nested loops capture their own break/continue.
            if isinstance(node, (WhileStatement, ForStatement)):
                return False
            for attr in ("body", "then_body", "else_body", "cases", "statements"):
                child = getattr(node, attr, None)
                if isinstance(child, list):
                    if any(_arm_breaks_out(c, depth + 1) for c in child):
                        return True
                elif child is not None and _arm_breaks_out(child, depth + 1):
                    return True
            return False

        arm_escapes_loop = any(_arm_breaks_out(case.body) for case in st.cases)

        # Check if we can use a switch (integer patterns/or-of-integers, no guards)
        can_use_switch = not arm_escapes_loop and all(
            case.guard is None
            and (
                _is_int_literal(case.pattern)
                or (
                    isinstance(case.pattern, OrPattern)
                    and all(_is_int_literal(p) for p in case.pattern.patterns)
                )
            )
            for case in st.cases
        )
        
        if can_use_switch:
            # Generate C switch statement
            lines.append(f"{self._i()}switch ({match_expr}) {{")
            self._indent += 1
            
            for case in st.cases:
                if isinstance(case.pattern, OrPattern):
                    for alt in case.pattern.patterns:
                        lines.append(f"{self._i()}case {self._gen_expr(alt)}:")
                else:
                    lines.append(f"{self._i()}case {self._gen_expr(case.pattern)}:")
                lines.append(f"{self._i()}{{")
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
                cond = "1"

                if isinstance(pattern, Literal):
                    cond = self._gen_literal_eq_cond(match_expr, pattern)
                    if case.guard is not None:
                        cond = f"({cond}) && ({self._gen_expr(case.guard)})"
                elif isinstance(pattern, OrPattern):
                    if pattern.patterns and isinstance(
                        pattern.patterns[0], StructPattern
                    ):
                        # Struct alternatives: OR of each alt's match conds,
                        # bindings taken from the first alt (binding names
                        # already validated identical by the parser).
                        alt_conds: List[str] = []
                        struct_binds: List[str] = []
                        for i, alt in enumerate(pattern.patterns):
                            assert isinstance(alt, StructPattern)
                            literal_conds, binds = self._gen_struct_pattern_match(
                                alt, match_expr
                            )
                            term = " && ".join(literal_conds) if literal_conds else "1"
                            alt_conds.append(f"({term})" if literal_conds else "1")
                            if i == 0:
                                struct_binds = binds
                        cond = " || ".join(alt_conds) if alt_conds else "1"
                        if case.guard is not None:
                            guard_expr = self._gen_expr(case.guard)
                            if struct_binds:
                                bind_decls = " ".join(f"{b};" for b in struct_binds)
                                cond = (
                                    f"({cond}) && "
                                    f"({{ {bind_decls} {guard_expr}; }})"
                                )
                            else:
                                cond = f"({cond}) && ({guard_expr})"
                        branch_kw = "if" if first else "} else if"
                        first = False
                        lines.append(f"{self._i()}{branch_kw} ({cond}) {{")
                        self._indent += 1
                        for bind_stmt in struct_binds:
                            lines.append(f"{self._i()}{bind_stmt};")
                        lines.extend(self._gen_block(case.body))
                        self._indent -= 1
                        continue
                    if pattern.patterns and isinstance(
                        pattern.patterns[0], ListPattern
                    ):
                        # List alternatives: OR of each alt's element conds,
                        # bindings taken from the first alt (binding names
                        # already validated identical by the parser).
                        alt_conds: List[str] = []
                        list_binds: List[str] = []
                        arr_type = self._infer_match_type(st.value)
                        elem_t = getattr(arr_type, "element_type", None)
                        if elem_t is None and arr_type.name.startswith("array_"):
                            rest = arr_type.name[len("array_"):]
                            if "_" in rest:
                                parts = rest.split("_")
                                if parts[0].isdigit():
                                    rest = "_".join(parts[1:])
                            elem_t = Type(rest)
                        for i, alt in enumerate(pattern.patterns):
                            assert isinstance(alt, ListPattern)
                            elem_conds, binds = self._gen_list_pattern_match(
                                alt, match_expr, elem_t
                            )
                            term = " && ".join(elem_conds) if elem_conds else "1"
                            alt_conds.append(f"({term})" if elem_conds else "1")
                            if i == 0:
                                list_binds = binds
                        cond = " || ".join(alt_conds) if alt_conds else "1"
                        if case.guard is not None:
                            guard_expr = self._gen_expr(case.guard)
                            if list_binds:
                                bind_decls = " ".join(f"{b};" for b in list_binds)
                                cond = (
                                    f"({cond}) && "
                                    f"({{ {bind_decls} {guard_expr}; }})"
                                )
                            else:
                                cond = f"({cond}) && ({guard_expr})"
                        branch_kw = "if" if first else "} else if"
                        first = False
                        lines.append(f"{self._i()}{branch_kw} ({cond}) {{")
                        self._indent += 1
                        for bind_stmt in list_binds:
                            lines.append(f"{self._i()}{bind_stmt};")
                        lines.extend(self._gen_block(case.body))
                        self._indent -= 1
                        continue
                    cond = " || ".join(
                        self._gen_literal_eq_cond(match_expr, alt)
                        for alt in pattern.patterns
                    )
                    if case.guard is not None:
                        cond = f"({cond}) && ({self._gen_expr(case.guard)})"
                elif isinstance(pattern, Variable):
                    variant_owner = self._enum_variant_owner.get(pattern.name)
                    if pattern.name != "_" and variant_owner is not None:
                        # Path/const pattern (e.g. `Option_i32_Some`): a
                        # value-equality check against the enum's tag, not an
                        # identifier binding. Matching directly on an enum
                        # value compares its `.tag` field; matching on
                        # `.tag` (or another i32) compares directly.
                        value_ty = self._infer_expr_type(st.value)
                        if value_ty is not None and value_ty.name == variant_owner:
                            tag_expr = f"({match_expr}).tag"
                        else:
                            tag_expr = match_expr
                        cond = f"({tag_expr}) == {_c_ident(pattern.name)}"
                        if case.guard is not None:
                            cond = f"({cond}) && ({self._gen_expr(case.guard)})"
                    elif pattern.name == "_" and case.guard is None:
                        cond = "1"
                    elif case.guard is not None:
                        bind_type = self._c_type(self._infer_match_type(st.value))
                        guard_expr = self._gen_expr(case.guard)
                        cond = (
                            f"({{ {bind_type} {_c_ident(pattern.name)} = {match_expr}; "
                            f"{guard_expr}; }})"
                        )
                    elif pattern.name != "_":
                        bind_type = self._c_type(self._infer_match_type(st.value))
                        cond = (
                            f"({{ {bind_type} {_c_ident(pattern.name)} = {match_expr}; 1; }})"
                        )
                elif isinstance(pattern, StructPattern):
                    literal_conds, struct_binds = self._gen_struct_pattern_match(
                        pattern, match_expr
                    )
                    cond_terms = list(literal_conds)
                    if case.guard is not None:
                        guard_expr = self._gen_expr(case.guard)
                        if struct_binds:
                            # Bindings must be visible to the guard, but they're
                            # only declared inside the if-body below - use a GNU
                            # statement expression so the guard can see them too.
                            bind_decls = " ".join(f"{b};" for b in struct_binds)
                            cond_terms.append(f"({{ {bind_decls} {guard_expr}; }})")
                        else:
                            cond_terms.append(f"({guard_expr})")
                    cond = " && ".join(cond_terms) if cond_terms else "1"
                    branch_kw = "if" if first else "} else if"
                    first = False
                    lines.append(f"{self._i()}{branch_kw} ({cond}) {{")
                    self._indent += 1
                    for bind_stmt in struct_binds:
                        lines.append(f"{self._i()}{bind_stmt};")
                    lines.extend(self._gen_block(case.body))
                    self._indent -= 1
                    continue
                elif isinstance(pattern, ListPattern):
                    arr_type = self._infer_match_type(st.value)
                    elem_t = getattr(arr_type, "element_type", None)
                    if elem_t is None and arr_type.name.startswith("array_"):
                        rest = arr_type.name[len("array_"):]
                        if "_" in rest:
                            parts = rest.split("_")
                            if parts[0].isdigit():
                                rest = "_".join(parts[1:])
                        elem_t = Type(rest)
                    list_conds, list_binds = self._gen_list_pattern_match(
                        pattern, match_expr, elem_t
                    )
                    cond_terms = list(list_conds)
                    if case.guard is not None:
                        guard_expr = self._gen_expr(case.guard)
                        if list_binds:
                            bind_decls = " ".join(f"{b};" for b in list_binds)
                            cond_terms.append(f"({{ {bind_decls} {guard_expr}; }})")
                        else:
                            cond_terms.append(f"({guard_expr})")
                    cond = " && ".join(cond_terms) if cond_terms else "1"
                    branch_kw = "if" if first else "} else if"
                    first = False
                    lines.append(f"{self._i()}{branch_kw} ({cond}) {{")
                    self._indent += 1
                    for bind_stmt in list_binds:
                        lines.append(f"{self._i()}{bind_stmt};")
                    lines.extend(self._gen_block(case.body))
                    self._indent -= 1
                    continue
                else:
                    cond = f"({match_expr}) == {self._gen_expr(pattern)}"
                    if case.guard is not None:
                        cond = f"({cond}) && ({self._gen_expr(case.guard)})"

                branch_kw = "if" if first else "} else if"
                first = False
                lines.append(f"{self._i()}{branch_kw} ({cond}) {{")
                self._indent += 1
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
        effects = st.effects
        handlers = st.handlers
        if len(handlers) == 1 and len(effects) > 1:
            handler_map = {effect: handlers[0] for effect in effects}
        elif len(handlers) == len(effects):
            handler_map = {effect: handler for effect, handler in zip(effects, handlers)}
        else:
            raise ValueError(f"handle expects 1 handler or the same count as effects; got {len(effects)} effects and {len(handlers)} handlers")
        
        # Push new effect handler context (for compile-time tracking)
        prev_handlers = self._effect_handler_stack[-1].copy()
        for effect_name, handler_name in handler_map.items():
            prev_handlers[effect_name] = handler_name
        self._effect_handler_stack.append(prev_handlers)
        
        try:
            # Generate runtime handler setup
            if len(handler_map) == 1:
                effect_name = next(iter(handler_map.keys()))
                handler_name = handler_map[effect_name]
                lines.append(f"{self._i()}/* handle {effect_name} with {handler_name} */")
            else:
                effects_str = ", ".join(handler_map.keys())
                handlers_str = ", ".join(handler_map.values())
                lines.append(f"{self._i()}/* handle {effects_str} with {handlers_str} */")
            lines.append(f"{self._i()}{{")
            self._indent += 1
            
            # Save previous handlers and set new ones
            for effect_name, handler_name in handler_map.items():
                lines.append(f"{self._i()}{effect_name}_Handler* _prev_{effect_name}_handler = _current_{effect_name}_handler;")
            for effect_name, handler_name in handler_map.items():
                lines.append(f"{self._i()}_current_{effect_name}_handler = &_{handler_name}_{effect_name}_vtable;")
            lines.append("")
            
            # Generate body
            lines.extend(self._gen_block(st.body))
            
            # Restore previous handler
            lines.append("")
            for effect_name in reversed(list(handler_map.keys())):
                lines.append(f"{self._i()}_current_{effect_name}_handler = _prev_{effect_name}_handler;")
            
            self._indent -= 1
            lines.append(f"{self._i()}}}")
        finally:
            # Pop handler context
            self._effect_handler_stack.pop()
        
        return lines

    def _gen_layout(self, st: LayoutStatement) -> List[str]:
        lines: List[str] = []
        begin_name = f"{st.kind}_begin"
        end_name = f"{st.kind}_end"
        args = list(st.args)
        needs_implicit = False
        if st.kind.startswith("ui_"):
            if len(args) == 0:
                needs_implicit = True
            else:
                first = args[0]
                if isinstance(first, Variable):
                    var_type = self._var_types.get(first.name)
                    if var_type and (getattr(var_type, 'is_pointer', False) or var_type.name.startswith("ptr_")):
                        needs_implicit = False
                    else:
                        needs_implicit = True
                else:
                    needs_implicit = True
        if needs_implicit:
            args = [Variable("_ui_state")] + args

        begin_call = FunctionCall(begin_name, args)
        lines.append(f"{self._i()}{self._gen_expr(begin_call)};")
        lines.extend(self._gen_block(st.body))
        if len(args) > 0:
            end_call = FunctionCall(end_name, [args[0]])
            lines.append(f"{self._i()}{self._gen_expr(end_call)};")
        else:
            end_call = FunctionCall(end_name, [])
            lines.append(f"{self._i()}{self._gen_expr(end_call)};")
        return lines

    def _gen_expr(self, e: Expression) -> str:
        if isinstance(e, Assignment):
            # `a = b = value` is parsed as an Assignment nested in the RHS
            # of another Assignment. C assignment expressions have the same
            # value semantics, so lower them recursively and preserve the
            # parentheses required when embedded in a larger expression.
            if e.target_expr is not None:
                target_expr = self._gen_lvalue_expr(e.target_expr)
            else:
                target_expr = _sanitize_identifier(e.target)
                if self._capture_stack and e.target in self._capture_stack[-1]:
                    target_expr = f"_env->{target_expr}"
            return f"({target_expr} = {self._gen_expr(e.value)})"

        if isinstance(e, Literal):
            if e.type.name == "bool":
                return "1" if e.value == "true" else "0"
            elif e.type.name == "string":
                return e.value  # String literals already have quotes
            elif e.value == "null" or e.type.name == "ptr_void" or getattr(e.type, 'is_pointer', False):
                # null pointer literal
                return "NULL"
            # C has no 128-bit literal syntax: compose wide integers from two
            # 64-bit halves so `let x: i128 = <huge>` survives codegen.
            wide = e.type.name in ("i128", "u128")
            if not wide and isinstance(e.value, (str, int)):
                try:
                    wide = abs(int(str(e.value), 0)) > 0x7FFFFFFFFFFFFFFF
                except ValueError:
                    wide = False
            if wide:
                text = str(e.value)
                try:
                    n = int(text, 0)
                except ValueError:
                    return e.value
                ctype = "unsigned __int128" if e.type.name == "u128" else "__int128"
                neg = n < 0
                mag = -n if neg else n
                if mag >> 64:
                    hi = mag >> 64
                    lo = mag & 0xFFFFFFFFFFFFFFFF
                    composed = (
                        f"(({ctype})0x{hi:X}ULL << 64 | ({ctype})0x{lo:X}ULL)"
                    )
                else:
                    composed = f"(({ctype})0x{mag:X}ULL)"
                return f"(-{composed})" if neg else composed
            return e.value

        if isinstance(e, Variable):
            # Inside a lambda body, captured variables live in the closure
            # environment. This substitution happens at AST level, so names
            # that merely contain a capture as a substring stay intact.
            if self._capture_stack and e.name in self._capture_stack[-1]:
                return f"_env->{_c_ident(e.name)}"
            return _c_ident(e.name)

        if isinstance(e, IfExpression):
            cond = self._gen_expr(e.condition)
            then_c = self._gen_expr(e.then_expr)
            else_c = self._gen_expr(e.else_expr)
            return f"(({cond}) ? ({then_c}) : ({else_c}))"

        if isinstance(e, StructLiteral):
            struct_fields = self._structs.get(e.struct_name, {})

            def is_array_field(name):
                ft = struct_fields.get(name)
                return bool(ft and getattr(ft, "name", "").startswith("array_"))

            # A sized-array field can only be initialized in-place (via a
            # designated initializer) when the source value is itself an
            # array literal (brace-enclosed sub-lists are legal C). If the
            # value is a pointer-producing expression (e.g. a function call
            # returning `Note*` for a `-> array<Note, N>` function, or a
            # plain variable/pointer), C has no syntax to initialize an
            # array member from it directly - it would try to coerce the
            # pointer into the first scalar member. Fall back to a
            # statement-expression that memcpy's such fields into place.
            needs_memcpy = any(
                is_array_field(name) and not isinstance(value, ArrayLiteral)
                for name, value in e.fields
            )

            struct_c_name = _c_ident(e.struct_name)
            if needs_memcpy:
                tmp = f"_flow_struct_tmp_{id(e) & 0xFFFFFF}"
                stmts = [f"{struct_c_name} {tmp};"]
                for name, value in e.fields:
                    c_field = _c_ident(name)
                    if is_array_field(name):
                        if isinstance(value, ArrayLiteral):
                            value_expr = self._gen_array_literal(value, as_initializer=False)
                        else:
                            value_expr = self._gen_expr(value)
                        stmts.append(f"memcpy({tmp}.{c_field}, {value_expr}, sizeof({tmp}.{c_field}));")
                    else:
                        value_expr = self._gen_expr(value)
                        stmts.append(f"{tmp}.{c_field} = {value_expr};")
                stmts.append(f"{tmp};")
                return "({ " + " ".join(stmts) + " })"

            field_parts = []
            for name, value in e.fields:
                if is_array_field(name) and isinstance(value, ArrayLiteral):
                    value_expr = self._gen_array_literal(value, as_initializer=True)
                else:
                    value_expr = self._gen_expr(value)
                field_parts.append(f".{_c_ident(name)} = {value_expr}")
            fields = ", ".join(field_parts)
            return f"({struct_c_name}){{ {fields} }}"

        if isinstance(e, RecordUpdate):
            # `Point { ..p, x: 3 }` -> `({ Point _ru = p; _ru.x = 3; _ru; })`
            inferred = self._infer_expr_type(e.base)
            struct_name = inferred.name if inferred else None
            struct_c_name = _c_ident(struct_name)
            if not struct_name or struct_name not in self._structs:
                struct_c_name = _c_ident(struct_name or "")
            tmp = f"_flow_rupdate_{id(e) & 0xFFFFFF}"
            base_c = self._gen_expr(e.base)
            stmts = [f"{struct_c_name} {tmp} = {base_c};"]
            struct_fields = self._structs.get(struct_name, {})

            def ru_is_array_field(name):
                ft = struct_fields.get(name)
                return bool(ft and getattr(ft, "name", "").startswith("array_"))

            for name, value in e.updates:
                c_field = _c_ident(name)
                if ru_is_array_field(name):
                    if isinstance(value, ArrayLiteral):
                        value_expr = self._gen_array_literal(value, as_initializer=False)
                    else:
                        value_expr = self._gen_expr(value)
                    stmts.append(f"memcpy({tmp}.{c_field}, {value_expr}, sizeof({tmp}.{c_field}));")
                else:
                    stmts.append(f"{tmp}.{c_field} = {self._gen_expr(value)};")
            stmts.append(f"{tmp};")
            return "({ " + " ".join(stmts) + " })"

        if isinstance(e, FieldAccess):
            obj_expr = self._gen_expr(e.object)
            if self._is_pointer_expr(e.object):
                if self._overflow_checks_enabled():
                    obj_expr = f"FLOW_NONNULL({obj_expr})"
                return f"{obj_expr}->{_c_ident(e.field)}"
            return f"{obj_expr}.{_c_ident(e.field)}"

        if isinstance(e, TryExpr):
            tmp = f"_flow_try_{id(e) & 0xFFFFFF}"
            result_type = self._infer_result_struct_type(e.operand)
            operand_c = self._gen_expr(e.operand)
            return (
                f"({{ {result_type} {tmp} = {operand_c}; "
                f"if (!{tmp}.is_ok) return {tmp}; {tmp}.value; }})"
            )

        if isinstance(e, CastExpression):
            target_c = self._c_type(e.target_type)
            return f"(({target_c})({self._gen_expr(e.expr)}))"

        if isinstance(e, UnaryOperation):
            op = e.operator
            if op == "!" or op == "not":
                # Operand needs its own parens: comparisons are emitted
                # without an outer group, so `(!x < 10)` would mean
                # `(!x) < 10` without this.
                return f"(!({self._gen_expr(e.operand)}))"
            if op == "-":
                operand_t = self._infer_expr_type(e.operand)
                if operand_t and operand_t.name == "Dual":
                    return self._gen_expr(FunctionCall("neg", [e.operand]))
                return f"(-{self._gen_expr(e.operand)})"
            if op == "~":
                return f"(~{self._gen_expr(e.operand)})"
            if op == "&":
                # Use the lvalue form for array/field access so bounds-checked
                # array reads (which expand to a ternary rvalue) don't end up
                # with their address taken - a ternary result is never an
                # lvalue in C even when both branches are.
                return f"(&({self._gen_lvalue_expr(e.operand)}))"
            if op == "*":
                ptr_c = self._gen_expr(e.operand)
                if self._overflow_checks_enabled():
                    return f"(*(FLOW_NONNULL({ptr_c})))"
                return f"(*({ptr_c}))"
            return f"({op} {self._gen_expr(e.operand)})"  # Add space for unknown operators

        if isinstance(e, BinaryOperation):
            # Dual operator sugar (#161): a * b -> mul(a, b) when Dual is involved.
            dual_binop = {"+": "add", "-": "sub", "*": "mul", "/": "div"}
            if e.operator in dual_binop:
                left_t = self._infer_expr_type(e.left)
                right_t = self._infer_expr_type(e.right)
                if (left_t and left_t.name == "Dual") or (right_t and right_t.name == "Dual"):
                    return self._gen_expr(
                        FunctionCall(dual_binop[e.operator], [e.left, e.right])
                    )
                # Tensor element-wise (#161): a * b -> tensor_mul(a, b).
                # Tensor * f32 / f32 * Tensor -> tensor_scale; Tensor + f32 ->
                # tensor_add_scalar. Matmul stays tensor_matmul(...).
                if (left_t and left_t.name == "Tensor") or (
                    right_t and right_t.name == "Tensor"
                ):
                    tensor_binop = {
                        "+": "tensor_add",
                        "-": "tensor_sub",
                        "*": "tensor_mul",
                        "/": "tensor_div",
                    }
                    if left_t and right_t and left_t.name == "Tensor" and right_t.name == "Tensor":
                        return self._gen_expr(
                            FunctionCall(tensor_binop[e.operator], [e.left, e.right])
                        )
                    if e.operator == "*" and left_t and right_t:
                        if left_t.name == "Tensor":
                            return self._gen_expr(
                                FunctionCall("tensor_scale", [e.left, e.right])
                            )
                        if right_t.name == "Tensor":
                            return self._gen_expr(
                                FunctionCall("tensor_scale", [e.right, e.left])
                            )
                    if e.operator == "+" and left_t and right_t:
                        if left_t.name == "Tensor":
                            return self._gen_expr(
                                FunctionCall("tensor_add_scalar", [e.left, e.right])
                            )
                        if right_t.name == "Tensor":
                            return self._gen_expr(
                                FunctionCall("tensor_add_scalar", [e.right, e.left])
                            )

            left_expr = self._gen_expr(e.left)
            right_expr = self._gen_expr(e.right)

            # C's '%' operator requires integer operands. Flow lets '%' be used
            # on fields/values that are declared f32/f64 but are semantically
            # integral counts (e.g. struct fields computed from sample-rate
            # math but consumed as sample counts); cast any float operand to
            # int64_t so the generated C is valid rather than erroring on
            # "invalid operands to binary expression".
            if e.operator == '%':
                left_type = self._infer_expr_type(e.left)
                right_type = self._infer_expr_type(e.right)
                if left_type and left_type.name in ('f32', 'f64'):
                    left_expr = f"((int64_t)({left_expr}))"
                if right_type and right_type.name in ('f32', 'f64'):
                    right_expr = f"((int64_t)({right_expr}))"
            
            # Special handling for string concatenation
            if e.operator == '+':
                # Check if this is string concatenation
                left_is_string = self._is_string_expr(e.left)
                right_is_string = self._is_string_expr(e.right)
                
                # If either operand is a string, this is string concatenation.
                # Non-string operands (numbers, bools) are stringified first,
                # matching common "text: " + value ergonomics.
                if left_is_string or right_is_string:
                    left_str = left_expr if left_is_string else self._gen_stringify_expr(e.left)
                    right_str = right_expr if right_is_string else self._gen_stringify_expr(e.right)
                    return f"flow_strcat({left_str}, {right_str})"
                
                # Not string concat - fall through to normal binary op handling
            
            # Check if we need to remove parentheses around operands
            # This prevents excessive nesting like (((a == 1) or (b == 2)))
            def remove_outer_parens(expr):
                if expr.startswith('(') and expr.endswith(')'):
                    inner = expr[1:-1]
                    if inner.count('(') != inner.count(')'):
                        return expr
                    # Only remove if inner is a simple token (no operators)
                    for ch in inner:
                        if ch in "+-*/%&|^<>=!?:,":
                            return expr
                    return inner
                return expr
            
            # For logical operators, be more aggressive about removing parentheses
            # and convert Flow operators to C operators
            c_operator = e.operator
            if e.operator == 'and':
                c_operator = '&&'
                left_expr = remove_outer_parens(left_expr)
                right_expr = remove_outer_parens(right_expr)
            elif e.operator == 'or':
                c_operator = '||'
                left_expr = remove_outer_parens(left_expr)
                right_expr = remove_outer_parens(right_expr)
            elif e.operator == 'in':
                # `x in arr` — linear scan over the array.
                # `ch in s` — strchr-based char membership in a string.
                right_type = self._infer_expr_type(e.right)
                if right_type and right_type.name == "string":
                    left_val = self._gen_expr(e.left)
                    return f"({left_val} != NULL && strchr({right_expr}, (int)({left_val})[0]) != NULL)"
                left_val = self._gen_expr(e.left)
                # Use sizeof to get array length: sizeof(arr)/sizeof(arr[0])
                return f"(__flow_in_arr({right_expr}, {left_val}))"
            
            # Comparison operators don't need outer parens (they have low precedence)
            if c_operator in ['==', '!=', '<', '<=', '>', '>=']:
                return f"{left_expr} {c_operator} {right_expr}"

            # MISRA Rule 12.5 / CERT INT33-C: guard integer / and %.
            if c_operator in ('/', '%') and self._arith_checks_enabled():
                left_type = self._infer_expr_type(e.left)
                right_type = self._infer_expr_type(e.right)
                if self._is_integer_type_name(getattr(left_type, 'name', None)) or (
                    c_operator == '%'  # '%' is always integer after float→int cast above
                ):
                    # Skip float division (IEEE → Inf/NaN, not C UB).
                    if c_operator == '/' and self._is_float_type_name(
                        getattr(left_type, 'name', None)
                    ):
                        pass
                    elif c_operator == '/' and self._is_float_type_name(
                        getattr(right_type, 'name', None)
                    ):
                        pass
                    else:
                        return self._gen_checked_div_mod(left_expr, right_expr, c_operator)

            # MISRA Rule 12.2 / CERT INT34-C: guard shifts.
            if c_operator in ('<<', '>>') and self._arith_checks_enabled():
                return self._gen_checked_shift(left_expr, right_expr, c_operator)

            # MISRA Rule 12.1 / CERT INT32-C: guard signed integer +,-,*.
            if c_operator in ('+', '-', '*') and self._overflow_checks_enabled():
                left_type = self._infer_expr_type(e.left)
                right_type = self._infer_expr_type(e.right)
                ln = getattr(left_type, 'name', None)
                rn = getattr(right_type, 'name', None)
                # Only check signed integer types. Unsigned wraparound is
                # well-defined in C (modular arithmetic), not UB.
                signed = {"i8", "i16", "i32", "i64", "i128", "int"}
                if (ln in signed or rn in signed) and not (
                    self._is_float_type_name(ln) or self._is_float_type_name(rn)
                ):
                    return self._gen_checked_arith(left_expr, right_expr, c_operator)

            return f"({left_expr} {c_operator} {right_expr})"

        if isinstance(e, SortExpr):
            return self._gen_sort_expr(e)

        if isinstance(e, FindExpr):
            return self._gen_find_expr(e)

        if isinstance(e, FunctionCall):
            # array<T>(N) constructor → calloc(N, sizeof(elem)).
            # The parser lowers `array<f32>(10)` to FunctionCall("array_f32", [10]);
            # emit a calloc so the call resolves without a missing symbol (#270).
            if (
                e.name.startswith("array_")
                and len(e.arguments) == 1
                and not self._overload_resolver.get_overloads(e.name)
            ):
                elem_type = Type(e.name[len("array_"):])
                elem_c = self._c_type(elem_type)
                count = self._gen_expr(e.arguments[0])
                return f"(({elem_c}*)calloc({count}, sizeof({elem_c})))"
            # Complex constructors: c64(re, im) -> (float)(re) + (float)(im) * I,
            # c128(re, im) -> (double)(re) + (double)(im) * I.
            # Uses the C99 I macro from <complex.h> (more portable than CMPLXF).
            if e.name == "c64" and len(e.arguments) == 2:
                re = self._gen_expr(e.arguments[0])
                im = self._gen_expr(e.arguments[1])
                return f"((float)({re}) + (float)({im}) * I)"
            if e.name == "c128" and len(e.arguments) == 2:
                re = self._gen_expr(e.arguments[0])
                im = self._gen_expr(e.arguments[1])
                return f"((double)({re}) + (double)({im}) * I)"
            # Complex scalar from a single real: c64(x) -> (float)(x) + 0*I.
            if e.name == "c64" and len(e.arguments) == 1:
                re = self._gen_expr(e.arguments[0])
                return f"((float)({re}) + 0.0f * I)"
            if e.name == "c128" and len(e.arguments) == 1:
                re = self._gen_expr(e.arguments[0])
                return f"((double)({re}) + 0.0 * I)"
            # sizeof<T>() / sizeof_i32() intrinsic — prefer inline C sizeof
            if e.name.startswith("sizeof_") and len(e.arguments) == 0:
                c_ty = self._sizeof_c_type_from_mangled(e.name[len("sizeof_"):])
                return f"(int64_t)sizeof({c_ty})"
            # ui_layout_bind intrinsic: bind implicit UI state pointer
            if e.name == "ui_layout_bind" and len(e.arguments) == 1:
                arg_expr = self._gen_expr(e.arguments[0])
                return f"(_ui_state = (void*){arg_expr})"
            # dbg intrinsic: evaluate the operand once, print it to stderr as a side
            # effect, and yield the operand's value so the surrounding program
            # is unaffected (`dbg x` == `x`).
            if e.name == "__flow_dbg" and len(e.arguments) == 1:
                arg = e.arguments[0]
                arg_expr = self._gen_expr(arg)
                inferred = self._infer_expr_type(arg)
                type_name = inferred.name if inferred else None
                tmp = f"_dbgv_{id(e) & 0xFFFFFF}"
                if type_name == "string":
                    rendered = tmp
                elif type_name == "bool":
                    rendered = f"({tmp} ? \"true\" : \"false\")"
                else:
                    fmt = self._printf_format_for_type_name(type_name)
                    buf = f"_dbgbuf_{id(e) & 0xFFFFFF}"
                    rendered = f'({{ char {buf}[64]; snprintf({buf}, sizeof({buf}), "{fmt}", {tmp}); {buf}; }})'
                return (
                    f'({{ __typeof__({arg_expr}) {tmp} = {arg_expr}; '
                    f'fprintf(stderr, "dbg: %s\\n", {rendered}); {tmp}; }})'
                )
            # Runtime invariant trap for flow always/never (north-star §5.4).
            # Uses exit(1) like `expect` (not abort) so captured subprocess
            # runs do not hang behind a crash reporter on macOS.
            if e.name == "flow_panic" and len(e.arguments) == 1:
                msg = self._gen_expr(e.arguments[0])
                return (
                    f'(fprintf(stderr, "%s\\n", {msg}), exit(1))'
                )
            # Handle len() builtin for arrays and slices
            if e.name == "len":
                if len(e.arguments) == 1:
                    arg = e.arguments[0]
                    # Spans carry their own length: `len(s)` == `s.len`.
                    if self._is_span_type(self._infer_expr_type(arg)):
                        return f"({self._gen_expr(arg)}).len"
                    # For array types, use sizeof(arr)/sizeof(arr[0])
                    # For slice types (structs with .len field), use .len
                    if isinstance(arg, Variable):
                        var_name = arg.name
                        if var_name in self._var_types:
                            var_type = self._var_types[var_name]
                            # Check if it's a slice type (has .len field)
                            if var_type.name in self._structs and 'len' in self._structs.get(var_type.name, {}):
                                return f"{var_name}.len"
                            # Check if it's a sized array
                            if var_type.name.startswith("array_") and var_type.size:
                                return str(var_type.size)
                    # Default: try sizeof/sizeof for C arrays
                    arg_expr = self._gen_expr(arg)
                    return f"(sizeof({arg_expr})/sizeof({arg_expr}[0]))"
            
            # Handle print/println intrinsics
            if e.name in ("print", "println"):
                return self._gen_print_call(e.arguments, newline=(e.name == "println"))

            # Plain C function pointer calls: cfn(A)->R variables are called
            # directly without the fat-pointer .fn dispatch.
            if self._is_cfn_type(self._var_types.get(e.name)):
                base = _sanitize_identifier(e.name)
                call_args = ", ".join(self._gen_expr(a) for a in e.arguments)
                return f"{base}({call_args})"

            # Escaping fat-pointer closures: (T)->R values carry {fn, env}.
            if e.name in self._fn_fat_vars or self._is_fn_type(self._var_types.get(e.name)):
                base = _sanitize_identifier(e.name)
                if self._capture_stack and e.name in self._capture_stack[-1]:
                    base = f"_env->{base}"
                call_args = [f"{base}.env"]
                call_args.extend(self._gen_expr(a) for a in e.arguments)
                return f"{base}.fn({', '.join(call_args)})"

            # Calls through closure variables: pass the environment as the
            # hidden first argument. Non-capturing lambda variables are plain
            # function pointers and take the default path below.
            if e.name in self._closure_vars:
                base = _sanitize_identifier(e.name)
                if self._capture_stack and e.name in self._capture_stack[-1]:
                    base = f"_env->{base}"
                call_args = [f"&{base}.env"]
                call_args.extend(self._gen_expr(a) for a in e.arguments)
                return f"{base}.fn({', '.join(call_args)})"

            # A non-capturing lambda variable that was itself captured into
            # this lambda's environment is called through the env field.
            if (
                self._capture_stack
                and e.name in self._capture_stack[-1]
                and e.name in self._fnptr_vars
            ):
                args = ", ".join(self._gen_expr(a) for a in e.arguments)
                return f"_env->{_c_ident(e.name)}({args})"

            overloads = self._overload_resolver.get_overloads(e.name)
            if any(getattr(ov.function, "is_extern", False) for ov in overloads):
                args = ", ".join(self._gen_expr(a) for a in e.arguments)
                return f"{_c_ident(e.name)}({args})"

            # Resolve function overload
            resolved_name = self._overload_resolver.resolve_call(e)
            func_name = resolved_name if resolved_name else e.name
            func_name = _c_ident(func_name)

            target_overload = None
            for ov in overloads:
                if ov.mangled_name == func_name:
                    target_overload = ov
                    break

            implicit_effect_args: list[str] = []
            if target_overload is None and overloads:
                implicit_match = self._resolve_call_with_implicit_effect_args(e, overloads)
                if implicit_match is not None:
                    target_overload, implicit_effect_args = implicit_match
                    func_name = _c_ident(target_overload.mangled_name)
            
            # A single non-overloaded candidate still tells us the declared
            # parameter types: spans borrow, so an argument's own type never
            # equals the parameter type verbatim and may not have matched.
            borrow_overload = target_overload
            if borrow_overload is None and len(overloads) == 1:
                borrow_overload = overloads[0]

            # Generate arguments, taking address of structs for capability parameters
            arg_strs = []
            for i, arg in enumerate(e.arguments):
                # Auto-borrow: a contiguous source becomes {pointer, length}
                # at the call site with no wrapper in the source program.
                if borrow_overload and i < len(borrow_overload.function.parameters):
                    declared = borrow_overload.function.parameters[i].type
                    if self._is_span_type(declared):
                        arg_strs.append(self._gen_span_borrow(arg, declared))
                        continue
                    # Lambda passed to a function-typed parameter: wrap as fat pointer
                    if isinstance(arg, Lambda) and self._is_fn_type(declared):
                        arg_expr = self._gen_expr(arg)
                        info = self._last_lambda_info
                        if info is not None:
                            wrapped, prelude = self._wrap_lambda_as_fn_type(info, declared)
                            for p in prelude:
                                self._prelude_lines.append(p)
                            arg_strs.append(wrapped)
                            continue
                arg_expr = self._gen_expr(arg)
                # Check if this parameter expects a capability type
                if target_overload and i < len(target_overload.param_types):
                    param_type = target_overload.param_types[i]
                    if param_type.startswith("capability_"):
                        # Need to pass address of struct
                        if isinstance(arg, Variable):
                            arg_expr = f"&{arg_expr}"
                arg_strs.append(arg_expr)
            arg_strs.extend(implicit_effect_args)
            
            args = ", ".join(arg_strs)
            return f"{func_name}({args})"
        
        if isinstance(e, EffectCall):
            return self._gen_effect_call(e)
        
        if isinstance(e, MethodCall):
            return self._gen_method_call(e)
        
        if isinstance(e, SliceExpr):
            return self._gen_span_borrow(e, None)

        if isinstance(e, ArrayAccess):
            return self._gen_array_access(e)

        if isinstance(e, ArrayLiteral):
            return self._gen_array_literal(e)
        
        if isinstance(e, Lambda):
            return self._gen_lambda(e)
        
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

        # Resolve effect name from variable type if needed
        # e.effect_name might be a variable name like "counter" for "counter.get_count()"
        # We need to look up its type (capability_Counter) to extract the effect name (Counter)
        effect_name = e.effect_name
        if effect_name in self._var_types:
            var_type = self._var_types[effect_name]
            if var_type.name.startswith("capability_"):
                # Extract the effect name from capability_EffectName
                effect_name = var_type.name[len("capability_"):]
            elif var_type.name in self._effects:
                # Variable type is directly an effect type (e.g., GPU)
                effect_name = var_type.name
        # Also check if it's already a known effect
        elif effect_name not in self._effects:
            # Try to find a matching effect by capitalizing
            capitalized = effect_name.capitalize()
            if capitalized in self._effects:
                effect_name = capitalized
            else:
                # Try uppercase (e.g., gpu -> GPU)
                upper = effect_name.upper()
                if upper in self._effects:
                    effect_name = upper

        args = ", ".join(self._gen_expr(a) for a in e.arguments)

        # Zero-cost substitution: inside a `handle Effect with Cap` block the
        # handler is known at compile time, so bypass the vtable and call the
        # capability function directly (the C compiler can then inline it).
        # Lambda bodies are excluded because the closure may be invoked after
        # the handle block exits, where only the runtime handler is correct.
        if self._lambda_depth == 0:
            handler_name = self._effect_handler_stack[-1].get(effect_name)
            cap = self._capabilities.get(handler_name) if handler_name else None
            if cap is not None and any(m.name == e.operation for m in cap.methods):
                return f"{_c_ident(handler_name)}_{_c_ident(e.operation)}({args})"

        return f"{_c_ident(effect_name)}_{_c_ident(e.operation)}({args})"

    def _gen_method_call(self, e: MethodCall) -> str:
        """Generate code for a method-style call (obj.method(args))."""
        if isinstance(e.object, Variable):
            if e.object.name in self._effects:
                effect_call = EffectCall(e.object.name, e.method, e.arguments)
                return self._gen_effect_call(effect_call)
            var_type = self._var_types.get(e.object.name)
            if var_type and (var_type.name.startswith("capability_") or var_type.name in self._effects):
                effect_call = EffectCall(e.object.name, e.method, e.arguments)
                return self._gen_effect_call(effect_call)

        receiver_type = self._infer_expr_type(e.object)
        impl_method = self._impl_method_for_receiver(receiver_type, e.method)
        if impl_method:
            return self._gen_expr(
                FunctionCall(impl_method, [e.object] + list(e.arguments))
            )

        # Desugar to a normal function call with the receiver as the first argument.
        # Many stdlib modules implement "methods" as plain functions taking
        # `ptr<Struct>` as their first parameter (effects/capabilities aren't
        # fully lowered to the C backend yet). If the receiver is a by-value
        # struct but every registered overload of this method name expects a
        # pointer to that exact struct type, take its address automatically -
        # this mirrors how `obj.method(...)` behaves as sugar for a
        # reference-receiving free function in the rest of the codebase.
        receiver = e.object
        obj_type = self._infer_expr_type(receiver)
        if obj_type and not getattr(obj_type, "is_pointer", False) and not obj_type.name.startswith("ptr_"):
            expected_ptr_type = f"ptr_{obj_type.name}"
            overloads = self._overload_resolver.get_overloads(e.method)
            if overloads and all(
                ov.param_types and ov.param_types[0] == expected_ptr_type
                for ov in overloads
            ):
                receiver = UnaryOperation("&", receiver)

        args = [receiver] + e.arguments
        return self._gen_expr(FunctionCall(e.method, args))

    def _type_name_for_method_receiver(self, t: Type | None) -> str | None:
        if t is None:
            return None
        if getattr(t, "element_type", None) is not None and (
            getattr(t, "is_pointer", False) or t.name.startswith("ptr_")
        ):
            return t.element_type.name
        if t.name.startswith("ptr_"):
            return t.name[len("ptr_"):]
        return t.name

    def _impl_method_for_receiver(self, receiver_type: Type | None, method: str) -> str | None:
        type_name = self._type_name_for_method_receiver(receiver_type)
        if not type_name:
            return None
        candidates = self._impl_methods.get((type_name, method), [])
        if len(candidates) == 1:
            return candidates[0]
        return None

    def _resolve_call_with_implicit_effect_args(self, call: FunctionCall, overloads):
        """Resolve f(args) to f(args, GPU, FFT) inside a matching handle block."""
        matches = []
        arg_types = [self._overload_resolver.get_expr_type(arg) for arg in call.arguments]
        active_effects = self._effect_handler_stack[-1]

        for overload in overloads:
            if len(overload.param_types) < len(arg_types):
                continue

            explicit_ok = True
            for param_type, arg_type in zip(overload.param_types, arg_types):
                if arg_type is None:
                    continue
                if not self._overload_resolver._types_compatible(param_type, arg_type):
                    explicit_ok = False
                    break
            if not explicit_ok:
                continue

            implicit_args = []
            for param_type in overload.param_types[len(arg_types):]:
                effect_name = (
                    param_type[len("capability_"):]
                    if param_type.startswith("capability_")
                    else param_type
                )
                if effect_name not in self._effects or effect_name not in active_effects:
                    implicit_args = None
                    break
                implicit_args.append(f"({_c_ident(param_type)}){{  }}")
            if implicit_args is not None:
                matches.append((overload, implicit_args))

        if len(matches) == 1:
            return matches[0]
        return None
    
    def _gen_lvalue_expr(self, e: Expression) -> str:
        """Generate an assignable C lvalue (no bounds-check ternaries)."""
        if isinstance(e, ArrayAccess):
            base_type = self._infer_expr_type(e.array)
            if self._is_span_type(base_type):
                return (
                    f"({self._gen_expr(e.array)}).data[{self._gen_expr(e.index)}]"
                )
            return (
                f"{self._gen_lvalue_expr(e.array)}[{self._gen_expr(e.index)}]"
            )
        if isinstance(e, FieldAccess):
            accessor = "->" if self._is_pointer_expr(e.object) else "."
            obj = self._gen_lvalue_expr(e.object)
            if accessor == "->" and self._overflow_checks_enabled():
                obj = f"FLOW_NONNULL({obj})"
            return f"{obj}{accessor}{_c_ident(e.field)}"
        return self._gen_expr(e)

    def _arith_checks_enabled(self) -> bool:
        """Runtime div0/shift guards (MISRA #264/#265). Off for library TUs."""
        return bool(getattr(self, "_bounds_check", True))

    def _overflow_checks_enabled(self) -> bool:
        """Overflow checks have been removed. Always returns False."""
        return False

    def _no_heap_enabled(self) -> bool:
        """Flight profile bans compiler-injected heap (#274 / MISRA 21.3)."""
        return bool(getattr(self, "_no_heap", False)) and not self._library

    @staticmethod
    def _is_integer_type_name(name: Optional[str]) -> bool:
        return name in {
            "i8", "i16", "i32", "i64", "i128",
            "u8", "u16", "u32", "u64", "u128",
            "int", "bool",
        }

    @staticmethod
    def _is_float_type_name(name: Optional[str]) -> bool:
        return name in {"f32", "f64", "float", "double"}

    def _gen_checked_div_mod(self, left_expr: str, right_expr: str, op: str) -> str:
        """Emit integer / or % with a zero-divisor trap (CERT INT33-C)."""
        macro = "FLOW_CHECKED_DIV" if op == "/" else "FLOW_CHECKED_MOD"
        return f"{macro}(({left_expr}), ({right_expr}))"

    def _gen_checked_shift(self, left_expr: str, right_expr: str, op: str) -> str:
        """Emit << or >> with range/sign checks (CERT INT34-C / MISRA 12.2)."""
        macro = "FLOW_CHECKED_SHL" if op == "<<" else "FLOW_CHECKED_SHR"
        return f"{macro}(({left_expr}), ({right_expr}))"

    def _gen_checked_arith(self, left_expr: str, right_expr: str, op: str) -> str:
        """Emit signed integer +,-,* with overflow trap (CERT INT32-C / MISRA 12.1)."""
        macro = {"+": "FLOW_CHECKED_ADD", "-": "FLOW_CHECKED_SUB", "*": "FLOW_CHECKED_MUL"}[op]
        return f"{macro}(({left_expr}), ({right_expr}))"

    def _gen_array_access(self, e: ArrayAccess) -> str:
        """Generate C array index access with optional bounds checking.

        For sized arrays (where the size is known at compile time), we emit
        a bounds-checked access that aborts on out-of-range indices.  For
        dynamically-sized or pointer-based arrays we fall back to raw indexing.
        """
        # Element access through a span reads/writes the borrowed storage.
        base_type = self._infer_expr_type(e.array)
        if self._is_span_type(base_type):
            span_expr = self._gen_expr(e.array)
            index_expr = self._gen_expr(e.index)
            if self._bounds_check:
                return (
                    f'((int64_t)({index_expr}) < ({span_expr}).len '
                    f'? ({span_expr}).data[{index_expr}] '
                    f': (fprintf(stderr, "span index %lld out of bounds (len %lld)\\n", '
                    f'(long long)({index_expr}), (long long)({span_expr}).len), '
                    f'flow_fault_handler("span index out of bounds"), ({span_expr}).data[0]))'
                )
            return f"({span_expr}).data[{index_expr}]"

        array_expr = self._gen_expr(e.array)
        index_expr = self._gen_expr(e.index)

        # Try to determine if the array is a sized type so we can emit a bounds check
        array_size = None
        if isinstance(e.array, Variable) and e.array.name in self._var_types:
            arr_type = self._var_types[e.array.name]
            if arr_type and getattr(arr_type, 'size', None):
                array_size = arr_type.size

        if self._bounds_check and array_size is not None:
            return (
                f'(((unsigned)({index_expr}) < {array_size}) '
                f'? {array_expr}[{index_expr}] '
                f': (fprintf(stderr, "array index %d out of bounds (size %d)\\n", '
                f'(int)({index_expr}), {array_size}), '
                f'flow_fault_handler("array index out of bounds"), {array_expr}[0]))'
            )
        return f"{array_expr}[{index_expr}]"
    
    def _gen_array_literal(self, e: ArrayLiteral, as_initializer: bool = False) -> str:
        """Generate C array literal.
        
        When used as an initializer (in variable declarations), generates: { elem, elem, ... }
        When used as an expression (function arguments), generates compound literal: (type[]){ elem, ... }
        """
        elements = ", ".join(self._gen_expr(elem) for elem in e.elements)
        
        if as_initializer:
            return f"{{ {elements} }}"
        
        # As expression - need compound literal
        # Infer element type from first element
        elem_type = "float"  # Default
        if e.elements:
            first_elem = e.elements[0]
            if isinstance(first_elem, Literal):
                if first_elem.type.name in ['i32', 'i64']:
                    elem_type = "int32_t"
                elif first_elem.type.name in ['f32', 'f64']:
                    elem_type = "float"
                else:
                    elem_type = self._c_type(first_elem.type)
            else:
                inferred = self._infer_expr_type(first_elem)
                if inferred is not None:
                    elem_type = self._c_type(inferred)
        
        return f"({elem_type}[]){{ {elements} }}"
    
    def _filter_lambda_captures(self, e: Lambda) -> List[str]:
        """Reduce the parser's free-variable list to real capturable locals.

        The parser reports every free name in the lambda body. Only names
        that are local variables in the creation scope need a snapshot:
        file-scope constants, function names, effects, and capability
        handles all stay reachable from the lifted static function.
        """
        captures = []
        for cap in list(getattr(e, "captures", []) or []):
            if cap in self._const_names:
                continue
            if cap in self._static_names:
                continue
            if cap in self._effects:
                continue
            cap_type = self._var_types.get(cap)
            if cap_type is None:
                continue
            if getattr(cap_type, "name", "").startswith("capability_"):
                continue
            captures.append(cap)
        return captures

    def _gen_lambda(self, e: Lambda) -> str:
        """Lower a lambda to a lifted static C function.

        Non-capturing lambdas keep their bare-function-pointer form and ABI:
        the expression is `&lambda_N` and the lifted function's signature
        contains only the declared parameters.

        Capturing lambdas lower to a closure value. Each one gets a struct
        `lambda_N_closure { ret (*fn)(lambda_N_env*, params); lambda_N_env env; }`
        and the lambda expression is a compound literal that snapshots every
        captured variable by value into `env` at the point of creation.
        Later writes to the original variable do not affect the closure, and
        writes to a captured variable inside the lambda body only mutate the
        closure's own copy. Captured pointers and arrays snapshot the
        pointer; the pointed-to storage stays shared.
        """
        self._lambda_counter += 1
        lambda_id = self._lambda_counter
        lambda_name = f"lambda_{lambda_id}"
        env_name = f"lambda_{lambda_id}_env"
        closure_name = f"lambda_{lambda_id}_closure"
        fn_typedef = f"lambda_{lambda_id}_fn"

        captures = self._filter_lambda_captures(e)
        param_c_types = [
            self._c_type(p.type) if p.type else "int32_t" for p in e.parameters
        ]

        # Env struct fields use the creation-scope types of the captures.
        if captures:
            env_fields = " ".join(
                f"{self._c_type(self._var_types.get(cap, Type('i32')))} {_c_ident(cap)};"
                for cap in captures
            )
            self._pending_env_structs.append(
                f"typedef struct {{ {env_fields} }} {env_name};"
            )

        saved_var_types = self._var_types.copy()
        saved_closure_vars = self._closure_vars.copy()
        saved_fnptr_vars = self._fnptr_vars.copy()
        for p in e.parameters:
            self._var_types[p.name] = p.type or Type("i32")

        # Infer the return type of expression-body lambdas without an
        # explicit annotation so `|x| x * 2` returns a value in C.
        # Block bodies whose last statement is a bare expression get the
        # same treatment: `|y| { x + y }` is an implicit return.
        flow_ret = e.return_type
        block_tail_expr = None
        if isinstance(e.body, Block) and e.body.statements:
            last = e.body.statements[-1]
            if not isinstance(last, ReturnStatement) and self._is_bare_expr_stmt(last):
                block_tail_expr = last
        if flow_ret is None:
            infer_from = None
            if not isinstance(e.body, Block):
                infer_from = e.body
            elif block_tail_expr is not None:
                infer_from = block_tail_expr
            if infer_from is not None:
                inferred = self._infer_expr_type(infer_from)
                if inferred is not None and inferred.name not in ("auto", "void"):
                    flow_ret = inferred
        ret_type = self._c_type(flow_ret) if flow_ret else "void"

        param_parts = []
        if captures:
            param_parts.append(f"{env_name}* _env")
        param_parts.extend(
            f"{ct} {_c_ident(p.name)}" for ct, p in zip(param_c_types, e.parameters)
        )
        params = ", ".join(param_parts) if param_parts else "void"

        if captures:
            fn_ptr_params = ", ".join([f"{env_name}*"] + param_c_types)
            self._pending_env_structs.append(
                f"typedef struct {{ {ret_type} (*fn)({fn_ptr_params}); "
                f"{env_name} env; }} {closure_name};"
            )
        else:
            fn_ptr_params = ", ".join(param_c_types) if param_c_types else "void"
            self._pending_env_structs.append(
                f"typedef {ret_type} (*{fn_typedef})({fn_ptr_params});"
            )

        self._lambda_depth += 1
        self._capture_stack.append(set(captures))
        try:
            if isinstance(e.body, Block):
                body_lines = []
                stmts = list(e.body.statements)
                if (
                    block_tail_expr is not None
                    and ret_type != "void"
                    and stmts
                    and stmts[-1] is block_tail_expr
                ):
                    stmts[-1] = ReturnStatement(block_tail_expr)
                for stmt in stmts:
                    for line in self._gen_statement(stmt):
                        body_lines.append(line.lstrip())
            else:
                body_expr = self._gen_expr(e.body)
                if ret_type == "void":
                    body_lines = [f"{body_expr};"]
                else:
                    body_lines = [f"return {body_expr};"]
        finally:
            self._capture_stack.pop()
            self._lambda_depth -= 1
            self._var_types = saved_var_types
            self._closure_vars = saved_closure_vars
            self._fnptr_vars = saved_fnptr_vars

        self._pending_lambdas.append((lambda_name, ret_type, params, body_lines))

        self._last_lambda_info = {
            "lambda_name": lambda_name,
            "env_name": env_name,
            "closure_name": closure_name,
            "fn_typedef": fn_typedef,
            "ret_c": ret_type,
            "flow_ret": flow_ret,
            "param_c_types": param_c_types,
            "captures": captures,
        }

        if captures:
            # Snapshot each capture by value at creation. The initializer
            # expressions are generated in the creation scope, so a nested
            # lambda capturing an outer capture reads it from `_env`.
            init_fields = ", ".join(
                f".{_c_ident(cap)} = {self._gen_expr(Variable(cap))}"
                for cap in captures
            )
            return (
                f"(({closure_name}){{ .fn = &{lambda_name}, "
                f".env = {{ {init_fields} }} }})"
            )
        return f"&{lambda_name}"

    def _gen_lambda_decl(self, st: VarDecl) -> List[str]:
        """Declare a variable initialized with a lambda expression.

        A capturing lambda produces a closure-struct variable; calls through
        it pass `&var.env` as the hidden first argument. A non-capturing
        lambda produces a plain typed function pointer, so calls through it
        keep the bare `var(args)` form.

        When the declared type is `(T)->R`, lower to an escaping fat pointer
        (`{fn, env}`) so the value can be returned or passed to HOFs.
        """
        # Generate the lambda first so `_last_lambda_info` is populated.
        concrete = self._gen_lambda(st.initializer)
        info = self._last_lambda_info
        name = _sanitize_identifier(st.name)
        decl_type = st.type
        if decl_type and decl_type.name == "auto":
            decl_type = None
        if self._is_fn_type(decl_type):
            expr, prelude = self._wrap_lambda_as_fn_type(info, decl_type)
            fat = self._ensure_fn_typedef(decl_type)
            self._fn_fat_vars.add(st.name)
            self._var_types[st.name] = decl_type
            self._overload_resolver.set_var_type(st.name, decl_type.name)
            lines = [f"{self._i()}{line}" for line in prelude]
            lines.append(f"{self._i()}{fat} {name} = {expr};")
            return lines
        if info["captures"]:
            self._closure_vars[st.name] = info
            self._var_types[st.name] = Type(info["closure_name"])
            self._overload_resolver.set_var_type(st.name, info["closure_name"])
            return [f"{self._i()}{info['closure_name']} {name} = {concrete};"]
        self._fnptr_vars[st.name] = info
        self._var_types[st.name] = Type(info["fn_typedef"])
        self._overload_resolver.set_var_type(st.name, info["fn_typedef"])
        return [f"{self._i()}{info['fn_typedef']} {name} = {concrete};"]

    # ------------------------------------------------------------------
    # Declarative ordering and search
    #
    # `xs |> sort` and `xs |> find(x)` name an intent. Which C loop realises
    # that intent comes from the cost-based selector in plan_selector.py, fed
    # facts from the element type and from the ordering-hints pass. Every
    # decision is recorded in self._selections so `--explain` can print it.
    # ------------------------------------------------------------------

    # Runs shorter than this are grown with insertion sort before merging.
    # The cost model uses the same number, so an estimate matches the loop.
    SORT_MIN_RUN = _ordering_plans.SORT_MIN_RUN

    _INT_RANGES = {
        "u8": (0, 255),
        "u16": (0, 65535),
        "u32": (0, 4294967295),
        "u64": (0, 18446744073709551615),
        "i8": (-128, 127),
        "i16": (-32768, 32767),
        "i32": (-2147483648, 2147483647),
        "i64": (-9223372036854775808, 9223372036854775807),
        "bool": (0, 1),
    }

    _TYPE_BYTES = {
        "i8": 1, "u8": 1, "bool": 1,
        "i16": 2, "u16": 2,
        "i32": 4, "u32": 4, "f32": 4, "float": 4,
        "i64": 8, "u64": 8, "f64": 8, "double": 8,
        "c64": 8, "c128": 16,
        "string": 8,
    }

    @staticmethod
    def _is_float_type_name(name: str) -> bool:
        return name in ("f32", "f64", "float", "double")

    @staticmethod
    def _float_order_suffix(name: str) -> str:
        return "f32" if name in ("f32", "float") else "f64"

    def _ensure_total_order_helper(self, type_name: str) -> str:
        """Emit the IEEE 754 totalOrder comparison for a float width."""
        suffix = self._float_order_suffix(type_name)
        helper = f"__flow_ord_cmp_{suffix}"
        if suffix in self._order_helper_keys:
            return helper
        self._order_helper_keys.add(suffix)
        if suffix == "f64":
            c_type, uint, bits, sign = "double", "uint64_t", "int64_t", "0x8000000000000000ULL"
            shift = 63
        else:
            c_type, uint, bits, sign = "float", "uint32_t", "int32_t", "0x80000000U"
            shift = 31
        self._pending_order_helpers.append(
            "\n".join(
                [
                    f"/* IEEE 754-2008 totalOrder for {c_type}: maps the sign-magnitude",
                    "   bit pattern onto an unsigned key whose numeric order is the total",
                    "   order  -NaN < -inf < ... < -0.0 < +0.0 < ... < +inf < +NaN.",
                    "   Declarative sort and find use this, so a comparison is always",
                    f"   transitive; `<` on {c_type} keeps IEEE semantics. */",
                    f"static inline {uint} __flow_ord_key_{suffix}({c_type} x) {{",
                    f"    {uint} u;",
                    "    memcpy(&u, &x, sizeof u);",
                    f"    {uint} mask = ({uint})(-({bits})(u >> {shift})) | {sign};",
                    "    return u ^ mask;",
                    "}",
                    "",
                    f"static inline int32_t {helper}({c_type} a, {c_type} b) {{",
                    f"    {uint} ka = __flow_ord_key_{suffix}(a);",
                    f"    {uint} kb = __flow_ord_key_{suffix}(b);",
                    "    return (ka < kb) ? -1 : ((ka > kb) ? 1 : 0);",
                    "}",
                ]
            )
        )
        return helper

    def _scalar_cmp(self, lhs: str, rhs: str, type_name: str) -> str:
        """Three-way compare of two scalars under Flow's ordering semantics."""
        if type_name == "string":
            return f"strcmp({lhs}, {rhs})"
        if self._is_float_type_name(type_name):
            helper = self._ensure_total_order_helper(type_name)
            return f"{helper}({lhs}, {rhs})"
        return f"(({lhs}) < ({rhs}) ? -1 : (({lhs}) > ({rhs}) ? 1 : 0))"

    def _sort_cmp_fragment(
        self,
        lhs: str,
        rhs: str,
        keys: List[SortKey],
        elem_type: Type,
        global_desc: bool,
    ) -> str:
        """C expression: negative if lhs<rhs, positive if lhs>rhs, else 0."""
        if not keys:
            core = self._scalar_cmp(lhs, rhs, getattr(elem_type, "name", ""))
            return f"(0 - ({core}))" if global_desc else core

        parts: List[str] = []
        struct_fields = self._structs.get(getattr(elem_type, "name", ""), {})
        for key in keys:
            field = _c_ident(key.field or "")
            left = f"({lhs}).{field}"
            right = f"({rhs}).{field}"
            ft = struct_fields.get(key.field)
            desc = bool(key.descending) ^ bool(global_desc)
            cmp_e = self._scalar_cmp(left, right, getattr(ft, "name", "") if ft else "")
            if desc:
                cmp_e = f"(0 - ({cmp_e}))"
            parts.append(cmp_e)
        if len(parts) == 1:
            return parts[0]
        # Lexicographic cascade; scalar compares may be evaluated twice (MVP).
        chain = parts[-1]
        for p in reversed(parts[:-1]):
            chain = f"(({p}) != 0 ? ({p}) : ({chain}))"
        return chain

    # -- facts ---------------------------------------------------------

    def _elem_kind(self, elem: Type) -> str:
        name = getattr(elem, "name", "")
        if name == "string":
            return "string"
        if name == "bool":
            return "bool"
        if self._is_float_type_name(name):
            return "float"
        if name in self._INT_RANGES:
            return "int"
        return "struct"

    def _elem_bytes(self, elem: Type) -> int:
        name = getattr(elem, "name", "")
        if name in self._TYPE_BYTES:
            return self._TYPE_BYTES[name]
        fields = self._structs.get(name)
        if fields:
            total = 0
            widest = 1
            for ftype in fields.values():
                size = self._TYPE_BYTES.get(getattr(ftype, "name", ""), 8)
                widest = max(widest, size)
                if total % size:
                    total += size - (total % size)
                total += size
            if total % widest:
                total += widest - (total % widest)
            return max(total, 1)
        return 8

    def _sort_key_range(self, expr: SortExpr, elem: Type):
        """Proven [lo, hi] for a whole-element integer key, or None."""
        if expr.keys:
            return None
        name = getattr(elem, "name", "")
        type_range = self._INT_RANGES.get(name)
        hint = getattr(expr, "hint_key_range", None)
        if hint and len(hint) == 2:
            lo, hi = int(hint[0]), int(hint[1])
            if type_range:
                lo = max(lo, type_range[0])
                hi = min(hi, type_range[1])
            return [lo, hi]
        return list(type_range) if type_range else None

    def _site_location(self, node) -> str:
        line = getattr(node, "line", 0) or 0
        where = f"line {line}" if line else "unknown line"
        fn = getattr(self, "_current_fn_name", "")
        return f"{where} in {fn}()" if fn else where

    def _sort_selection(self, expr: SortExpr, elem: Type, size: int) -> "Selection":
        """Run the cost selector for one `|> sort` site."""
        direction = "desc" if expr.descending else "asc"
        order = getattr(expr, "hint_input_order", "unknown") or "unknown"
        if expr.general:
            order = "unknown"
        facts = Facts(
            construct="sort",
            n=int(size),
            data={
                "elem": getattr(elem, "name", "?"),
                "elem_kind": self._elem_kind(elem),
                "elem_bytes": self._elem_bytes(elem),
                "keys": len(expr.keys),
                "stable": bool(expr.stable),
                "unique": bool(expr.unique),
                "direction": direction,
                "input_order": order,
                "key_range": self._sort_key_range(expr, elem),
                "expect_runs": "few" if expr.adaptive else "unknown",
                "pinned": "bottom_up_merge" if expr.general else None,
            },
        )
        keys = (
            ", ".join(
                f"{'desc' if k.descending else 'asc'} .{k.field}" for k in expr.keys
            )
            or "whole element"
        )
        detail = (
            f"array<{getattr(elem, 'name', '?')}, {size}> "
            f"keys: {keys}; order: {direction}"
            + (" unique" if expr.unique else "")
            + (f"; policies: {' '.join(expr.policies)}" if expr.policies else "")
        )
        sel = select(facts, location=self._site_location(expr), detail=detail)
        self._selections.append(sel)
        return sel

    # -- C bodies ------------------------------------------------------

    def _sort_body_insertion(self, elem_c: str, cmp_fn) -> List[str]:
        cmp_ij = cmp_fn("a[j]", "key")
        return [
            "    for (int32_t i = 1; i < n; i++) {",
            f"        {elem_c} key = a[i];",
            "        int32_t j = i - 1;",
            f"        while (j >= 0 && ({cmp_ij}) > 0) {{",
            "            a[j + 1] = a[j];",
            "            j = j - 1;",
            "        }",
            "        a[j + 1] = key;",
            "    }",
        ]

    def _sort_body_noop(self, elem_c: str, cmp_fn) -> List[str]:
        return [
            "    /* provenance proved the input is already in this order */",
            "    (void)a; (void)n;",
        ]

    def _sort_body_reverse(self, elem_c: str, cmp_fn) -> List[str]:
        return [
            "    /* provenance proved a strictly reversed input */",
            "    for (int32_t lo = 0, hi = n - 1; lo < hi; lo++, hi--) {",
            f"        {elem_c} t = a[lo];",
            "        a[lo] = a[hi];",
            "        a[hi] = t;",
            "    }",
        ]

    def _sort_body_counting(
        self, elem_c: str, cmp_fn, size: int, lo: int, hi: int, descending: bool
    ) -> List[str]:
        span = hi - lo + 1
        walk = (
            f"    for (int32_t v = {span} - 1; v >= 0; v--) {{"
            if descending
            else f"    for (int32_t v = 0; v < {span}; v++) {{"
        )
        return [
            "    if (n < 2) { return; }",
            f"    int32_t counts[{span}];",
            f"    {elem_c} out[{size}];",
            f"    for (int32_t v = 0; v < {span}; v++) {{ counts[v] = 0; }}",
            f"    for (int32_t i = 0; i < n; i++) {{ counts[(int32_t)(a[i]) - {lo}]++; }}",
            "    int32_t total = 0;",
            walk,
            "        int32_t c = counts[v];",
            "        counts[v] = total;",
            "        total += c;",
            "    }",
            f"    for (int32_t i = 0; i < n; i++) {{ out[counts[(int32_t)(a[i]) - {lo}]++] = a[i]; }}",
            "    for (int32_t i = 0; i < n; i++) { a[i] = out[i]; }",
        ]

    def _sort_body_bottom_up(self, elem_c: str, cmp_fn, size: int) -> List[str]:
        take_right = cmp_fn("a[j]", "a[i]")
        return [
            "    if (n < 2) { return; }",
            f"    {elem_c} buf[{size}];",
            "    for (int32_t width = 1; width < n; width *= 2) {",
            "        for (int32_t lo = 0; lo < n; lo += 2 * width) {",
            "            int32_t mid = lo + width; if (mid > n) { mid = n; }",
            "            int32_t hi = lo + 2 * width; if (hi > n) { hi = n; }",
            "            int32_t i = lo, j = mid, k = lo;",
            "            while (i < mid && j < hi) {",
            f"                if (({take_right}) < 0) {{ buf[k++] = a[j++]; }}",
            "                else { buf[k++] = a[i++]; }",
            "            }",
            "            while (i < mid) { buf[k++] = a[i++]; }",
            "            while (j < hi) { buf[k++] = a[j++]; }",
            "        }",
            "        for (int32_t i = 0; i < n; i++) { a[i] = buf[i]; }",
            "    }",
        ]

    def _sort_body_natural_merge(self, elem_c: str, cmp_fn, size: int) -> List[str]:
        minrun = self.SORT_MIN_RUN
        max_runs = size // minrun + 3
        desc_head = cmp_fn("a[j]", "a[i]")
        desc_step = cmp_fn("a[j]", "a[j - 1]")
        asc_step = cmp_fn("a[j]", "a[j - 1]")
        ext_cmp = cmp_fn("a[k]", "key")
        merge_cmp = cmp_fn("a[y]", "a[x]")
        return [
            "    if (n < 2) { return; }",
            f"    {elem_c} buf[{size}];",
            f"    int32_t starts[{max_runs}];",
            "    int32_t nr = 0;",
            "    int32_t i = 0;",
            "    /* Pass 1: walk natural runs. A strictly descending run is",
            "       reversed in place (stable, because it is strict); a run",
            "       shorter than the minimum is grown by insertion. */",
            "    while (i < n) {",
            "        starts[nr++] = i;",
            "        int32_t j = i + 1;",
            f"        if (j < n && ({desc_head}) < 0) {{",
            f"            while (j < n && ({desc_step}) < 0) {{ j++; }}",
            "            for (int32_t lo = i, hi = j - 1; lo < hi; lo++, hi--) {",
            f"                {elem_c} t = a[lo];",
            "                a[lo] = a[hi];",
            "                a[hi] = t;",
            "            }",
            "        } else {",
            f"            while (j < n && ({asc_step}) >= 0) {{ j++; }}",
            "        }",
            f"        int32_t want = i + {minrun}; if (want > n) {{ want = n; }}",
            "        while (j < want) {",
            f"            {elem_c} key = a[j];",
            "            int32_t k = j - 1;",
            f"            while (k >= i && ({ext_cmp}) > 0) {{ a[k + 1] = a[k]; k--; }}",
            "            a[k + 1] = key;",
            "            j++;",
            "        }",
            "        i = j;",
            "    }",
            "    starts[nr] = n;",
            "    /* Pass 2: merge adjacent runs pairwise until one remains. */",
            "    while (nr > 1) {",
            "        int32_t w = 0;",
            "        for (int32_t r = 0; r + 1 < nr; r += 2) {",
            "            int32_t lo = starts[r], mid = starts[r + 1], hi = starts[r + 2];",
            "            int32_t x = lo, y = mid, k = lo;",
            "            while (x < mid && y < hi) {",
            f"                if (({merge_cmp}) < 0) {{ buf[k++] = a[y++]; }}",
            "                else { buf[k++] = a[x++]; }",
            "            }",
            "            while (x < mid) { buf[k++] = a[x++]; }",
            "            while (y < hi) { buf[k++] = a[y++]; }",
            "            for (int32_t t = lo; t < hi; t++) { a[t] = buf[t]; }",
            "            starts[w++] = lo;",
            "        }",
            "        if (nr % 2 == 1) { starts[w++] = starts[nr - 1]; }",
            "        starts[w] = n;",
            "        nr = w;",
            "    }",
        ]

    def _ensure_sort_helper(self, expr: SortExpr, arr_type: Type) -> Tuple[str, int]:
        """Select a sort plan, register its C helper, return (name, n)."""
        import hashlib

        size = getattr(arr_type, "size", None)
        elem = getattr(arr_type, "element_type", None)
        if size is None or elem is None:
            raise NotImplementedError(
                "Declarative sort requires fixed-size array<T, N>"
            )
        size = int(size)
        elem_c = self._c_type(elem)
        selection = self._sort_selection(expr, elem, size)
        plan = selection.chosen
        key_range = selection.facts.get("key_range")

        key_sig = ",".join(
            f"{'d' if k.descending else 'a'}.{k.field or '_'}" for k in expr.keys
        )
        flags = (
            f"g{'d' if expr.descending else 'a'}"
            f"_u{1 if expr.unique else 0}"
            f"_s{1 if expr.stable else 0}"
        )
        range_sig = f"{key_range[0]}:{key_range[1]}" if key_range else "-"
        dedupe = f"{elem_c}|{size}|{key_sig}|{flags}|{plan}|{range_sig}"
        helper = (
            "__flow_sort_"
            + hashlib.md5(dedupe.encode(), usedforsecurity=False).hexdigest()[:12]
        )
        if dedupe in self._sort_helper_keys:
            return helper, size
        self._sort_helper_keys.add(dedupe)

        def cmp_fn(lhs: str, rhs: str) -> str:
            return self._sort_cmp_fragment(lhs, rhs, expr.keys, elem, expr.descending)

        body = [
            f"/* plan: {plan} -- {selection.reason} */",
            f"static void {helper}({elem_c} *a, int32_t n) {{",
        ]
        if plan == "already_ordered":
            body.extend(self._sort_body_noop(elem_c, cmp_fn))
        elif plan == "reverse_in_place":
            body.extend(self._sort_body_reverse(elem_c, cmp_fn))
        elif plan == "counting":
            body.extend(
                self._sort_body_counting(
                    elem_c, cmp_fn, size, key_range[0], key_range[1], expr.descending
                )
            )
        elif plan == "natural_merge":
            body.extend(self._sort_body_natural_merge(elem_c, cmp_fn, size))
        elif plan == "bottom_up_merge":
            body.extend(self._sort_body_bottom_up(elem_c, cmp_fn, size))
        else:
            body.extend(self._sort_body_insertion(elem_c, cmp_fn))

        if expr.unique:
            cmp_wr = cmp_fn("a[w - 1]", "a[r]")
            body.extend(
                [
                    "    int32_t w = 0;",
                    "    for (int32_t r = 0; r < n; r++) {",
                    f"        if (w == 0 || ({cmp_wr}) != 0) {{",
                    "            a[w] = a[r];",
                    "            w = w + 1;",
                    "        }",
                    "    }",
                    "    /* unique: compacted prefix length is w; tail is stale */",
                    "    (void)w;",
                ]
            )
        body.append("}")
        self._pending_sort_helpers.append("\n".join(body))
        return helper, size

    def _gen_sort_expr(self, e: SortExpr) -> str:
        """Lower `xs |> sort ...` to an in-place helper call, yielding `xs`."""
        arr_type = self._infer_expr_type(e.array)
        helper, n = self._ensure_sort_helper(e, arr_type)
        arr_c = self._gen_expr(e.array)
        # In-place sort; expression value is the (mutated) array/pointer.
        return f"({{ {helper}(({self._c_type(arr_type.element_type)}*)({arr_c}), {n}); {arr_c}; }})"

    def _ensure_find_helper(self, expr: "FindExpr", arr_type: Type) -> Tuple[str, int]:
        """Select a search plan, register its C helper, return (name, n)."""
        import hashlib

        size = getattr(arr_type, "size", None)
        elem = getattr(arr_type, "element_type", None)
        if size is None or elem is None:
            raise NotImplementedError(
                "Declarative find requires fixed-size array<T, N>"
            )
        size = int(size)
        elem_c = self._c_type(elem)
        elem_name = getattr(elem, "name", "?")
        facts = Facts(
            construct="search",
            n=size,
            data={
                "elem": elem_name,
                "elem_kind": self._elem_kind(elem),
                "input_order": getattr(expr, "hint_input_order", "unknown")
                or "unknown",
            },
        )
        selection = select(
            facts,
            location=self._site_location(expr),
            detail=f"array<{elem_name}, {size}> find(target)",
        )
        self._selections.append(selection)
        plan = selection.chosen

        dedupe = f"{elem_c}|{size}|{plan}"
        helper = (
            "__flow_find_"
            + hashlib.md5(dedupe.encode(), usedforsecurity=False).hexdigest()[:12]
        )
        if dedupe in self._find_helper_keys:
            return helper, size
        self._find_helper_keys.add(dedupe)

        cmp_mid = self._scalar_cmp("a[mid]", "x", elem_name)
        cmp_lo = self._scalar_cmp("a[lo]", "x", elem_name)
        cmp_i = self._scalar_cmp("a[i]", "x", elem_name)
        lines = [
            f"/* plan: {plan} -- {selection.reason} */",
            f"static int32_t {helper}(const {elem_c} *a, int32_t n, {elem_c} x) {{",
        ]
        if plan == "binary_search":
            lines.extend(
                [
                    "    int32_t lo = 0, hi = n;",
                    "    while (lo < hi) {",
                    "        int32_t mid = lo + (hi - lo) / 2;",
                    f"        if (({cmp_mid}) < 0) {{ lo = mid + 1; }} else {{ hi = mid; }}",
                    "    }",
                    f"    if (lo < n && ({cmp_lo}) == 0) {{ return lo; }}",
                    "    return -1;",
                ]
            )
        else:
            lines.extend(
                [
                    "    for (int32_t i = 0; i < n; i++) {",
                    f"        if (({cmp_i}) == 0) {{ return i; }}",
                    "    }",
                    "    return -1;",
                ]
            )
        lines.append("}")
        self._pending_find_helpers.append("\n".join(lines))
        return helper, size

    def _gen_find_expr(self, e: "FindExpr") -> str:
        """Lower `xs |> find(t)` to a helper call yielding an index or -1."""
        arr_type = self._infer_expr_type(e.array)
        helper, n = self._ensure_find_helper(e, arr_type)
        arr_c = self._gen_expr(e.array)
        target_c = self._gen_expr(e.target)
        elem_c = self._c_type(arr_type.element_type)
        return f"{helper}((const {elem_c}*)({arr_c}), {n}, ({elem_c})({target_c}))"

    def emit_export_aliases(
        self,
        functions: List[Any],
        export_names: List[str],
        *,
        module_name: str | None = None,
    ) -> List[str]:
        """Emit stable C aliases for --export (issue #396).

        For each name in *export_names*, find the matching FunctionDecl and
        emit a visible alias ``flow_export_<name>`` that forwards to the
        mangled C symbol. This lets WASM/FFI consumers use a stable name
        without knowing the overload-mangling scheme.

        Returns a list of C source lines (empty if nothing to export).
        """
        prefix = "flow_export"
        lines: List[str] = []
        # Index functions by name for quick lookup.
        by_name: Dict[str, Any] = {}
        for fn in functions:
            base = getattr(fn, "name", "")
            if base and base not in by_name:
                by_name[base] = fn
        for name in export_names:
            fn = by_name.get(name)
            if fn is None:
                # Could be a method (mangled). Skip with a comment.
                lines.append(f"/* --export {name}: not found in this TU */")
                continue
            mangled = self._mangled_names.get(id(fn), fn.name)
            mangled_c = _c_ident(mangled)
            alias = f"{prefix}_{_c_ident(name)}"
            # Emit a forward declaration + alias wrapper.
            ret_type = self._c_type(fn.return_type) if fn.return_type else "void"
            param_types = []
            param_names = []
            for i, p in enumerate(fn.parameters):
                pt = self._c_type(p.type)
                pn = _c_ident(p.name or f"arg{i}")
                param_types.append(pt)
                param_names.append(pn)
            sig = ", ".join(f"{t} {n}" for t, n in zip(param_types, param_names)) or "void"
            call_args = ", ".join(param_names)
            lines.append(
                f"__attribute__((visibility(\"default\"))) "
                f"{ret_type} {alias}({sig}) {{ return {mangled_c}({call_args}); }}"
            )
        return lines




def flow_to_c(
    declarations: List[Any],
    *,
    source_file: str | None = None,
    debug_info: bool = False,
    strict_effects: bool = False,
    library: bool = False,
    no_heap: bool | None = None,
    no_bounds_check: bool = False,
    export_names: list[str] | None = None,
    module_name: str | None = None,
) -> str:
    """Convert FLOW declarations to C code"""
    try:
        import os
        env_profile = os.environ.get("FLOW_PROFILE", "")
        if no_heap is None:
            no_heap = env_profile == "flight"
        generator = CGenerator(
            source_file=source_file,
            debug_info=debug_info,
            strict_effects=strict_effects,
            library=library,
            bounds_check=not library and not no_bounds_check,
            no_heap=no_heap,
        )
        
        # Separate declarations by type
        constants = [d for d in declarations if isinstance(d, ConstDecl)]
        statics = [d for d in declarations if isinstance(d, StaticDecl)]
        functions = [d for d in declarations if isinstance(d, FunctionDecl)]
        # Deduplicate functions by name: when multiple imported modules define
        # the same helper (e.g. str_append, substr), only the first definition
        # is emitted. sizeof_ intrinsics are also deduped even when exported,
        # since multiple stdlib modules (memory.flow, memory_simple.flow) export
        # the same sizeof_i32 and the C generator emits them as identical
        # definitions. Other exported functions are kept as-is (the module
        # resolver already rejects exported-name collisions).
        # Forward declarations (empty body) never block a later real definition.
        _seen_fn: set = set()
        _deduped: list = []
        for fn in functions:
            is_sizeof = fn.name.startswith("sizeof_") and len(fn.parameters) == 0
            if getattr(fn, "is_exported", False) and not is_sizeof:
                _deduped.append(fn)
                continue
            key = fn.name
            has_body = bool(getattr(fn, "body", None) and fn.body.statements)
            if not has_body:
                # Forward declaration: keep it, but don't mark the name as seen
                # so a later definition with the same name still gets emitted.
                _deduped.append(fn)
                continue
            if key not in _seen_fn:
                _seen_fn.add(key)
                _deduped.append(fn)
        functions = _deduped
        structs = [d for d in declarations if isinstance(d, StructDecl)]
        effects = [d for d in declarations if isinstance(d, EffectDecl)]
        capabilities = [d for d in declarations if isinstance(d, CapabilityDecl)]
        traits = [d for d in declarations if isinstance(d, TraitDecl)]
        impls = [d for d in declarations if isinstance(d, ImplDecl)]
        enums = [d for d in declarations if isinstance(d, EnumDecl)]
        type_aliases = [d for d in declarations if isinstance(d, TypeAliasDecl)]
        distinct_types = [d for d in declarations if isinstance(d, DistinctTypeDecl)]
        extern_types = [d for d in declarations if isinstance(d, ExternTypeDecl)]
        c_includes = [d for d in declarations if isinstance(d, (CIncludeDecl, CImportDecl))]
        c_embeds = [d for d in declarations if isinstance(d, CEmbedDecl)]

        # Extract function names from @cEmbed code so the generator can
        # skip emitting conflicting extern prototypes for them.
        import re as _re_embed
        cembed_fns = set()
        for ce in c_embeds:
            for m in _re_embed.finditer(
                r'\b(?:static\s+)?(?:inline\s+)?'
                r'(?:int\d+_t|uint\d+_t|int|void|char|float|double|size_t|ssize_t|long|short|bool)\s+'
                r'(\w+)\s*\(',
                ce.code,
            ):
                cembed_fns.add(m.group(1))
        generator._cembed_functions = cembed_fns
        
        # Add impl methods to functions list (with mangled names)
        for impl in impls:
            type_name = impl.for_type.name
            for method in impl.methods:
                original_method_name = method.name
                # Mangle name: Type_Trait_method
                method.name = f"{type_name}_{impl.trait_name}_{original_method_name}"
                generator._impl_methods.setdefault(
                    (type_name, original_method_name), []
                ).append(method.name)
                
                # If method has self, add it as first parameter if not already present
                if getattr(method, 'has_self', False):
                    if not any(p.name == "self" for p in method.parameters):
                        from .parser import Parameter
                        self_param = Parameter("self", impl.for_type)
                        method.parameters = [self_param] + list(method.parameters)
                
                functions.append(method)
        
        out = generator.generate_translation_unit(constants, functions, structs, effects, capabilities, traits, enums, type_aliases, distinct_types, statics=statics)

        # Prepend @cInclude directives and extern type forward declarations.
        # These must appear before any generated code so opaque types resolve.
        prelude_lines = []
        for inc in c_includes:
            prelude_lines.append(f'#include "{inc.header}"')
        for et in extern_types:
            prelude_lines.append(f"typedef struct {et.name} {et.name};")
        if prelude_lines:
            out = "\n".join(prelude_lines) + "\n" + out

        # Insert @cEmbed raw C code after the standard includes in the
        # generated output. The standard includes (#include <stdint.h> etc.)
        # are at the top of `out`, so we find the first blank line after them
        # and insert the embedded code there.
        c_embeds = [d for d in declarations if isinstance(d, CEmbedDecl)]
        if c_embeds:
            embed_block = "\n".join(ce.code for ce in c_embeds)
            # Find the first blank line (end of standard includes block)
            blank_pos = out.find("\n\n")
            if blank_pos > 0:
                out = out[:blank_pos + 2] + "/* @cEmbed */\n" + embed_block + "\n" + out[blank_pos + 2:]
            else:
                out = "/* @cEmbed */\n" + embed_block + "\n" + out

        # Emit stable export aliases (--export / --module-name, #396).
        # Each exported function gets a visible alias flow_export_<name>
        # pointing at the mangled C symbol, so WASM/FFI consumers do not
        # need to guess the mangling scheme.
        if export_names:
            export_lines = generator.emit_export_aliases(
                functions, export_names, module_name=module_name,
            )
            if export_lines:
                out = out + "\n/* Flow export aliases (#396) */\n" + "\n".join(export_lines) + "\n"

        # Expose overload warnings without changing the return signature.
        flow_to_c.last_warnings = list(generator._overload_resolver.warnings)
        # Same for the plan records `--explain` prints (issue #146).
        flow_to_c.last_selections = list(generator._selections)
        return out
    except Exception as e:
        print(f"C generation error: {e}")
        import traceback
        traceback.print_exc()
        raise
