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

from typing import Any, List, Optional, Tuple

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
    ImplDecl,
    Lambda,
    Literal,
    MatchStatement,
    MethodCall,
    ReturnStatement,
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
    UnaryOperation,
    VarDecl,
    Variable,
    VectorLiteral,
    WhileStatement,
    ForStatement,
)
from .overload import OverloadResolver

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
    def __init__(self, *, source_file: str | None = None, debug_info: bool = False, bounds_check: bool = True) -> None:
        self._indent = 0
        self._structs = {}  # name -> dict of field_name -> field_type
        self._enums = {}  # name -> EnumDecl
        self._enum_variant_owner = {}  # "Enum_Variant" -> "Enum" (for path/const match patterns)
        self._var_types = {}  # name -> Type
        self._source_file = source_file
        self._debug_info = debug_info
        self._bounds_check = bounds_check
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
        self._closure_vars = {}  # var name -> lambda info (capturing lambdas)
        self._fnptr_vars = {}  # var name -> lambda info (non-capturing lambdas)
        self._capture_stack = []  # sets of captured names, one per nested lambda body
        self._const_names = set()  # file-scope constants (reachable without capture)
        self._lambda_insert_idx = None  # where lambda definitions get spliced in
        self._last_lambda_info = None

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
    
    def _printf_for_expr(self, expr: Expression, *, newline: bool) -> str:
        expr_str = self._gen_expr(expr)
        type_name = None
        if isinstance(expr, Literal):
            type_name = expr.type.name
        elif isinstance(expr, Variable):
            if expr.name in self._var_types:
                type_name = self._var_types[expr.name].name
        elif isinstance(expr, FieldAccess):
            field_type = self._infer_expr_type(expr)
            type_name = field_type.name if field_type else None
        elif isinstance(expr, FunctionCall):
            ret_type = self._infer_expr_type(expr)
            type_name = ret_type.name if ret_type else None
        fmt = self._printf_format_for_type_name(type_name)
        if newline:
            fmt = f"{fmt}\\n"
        return f'printf("{fmt}", {expr_str})'

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
            return 'printf("\\n")' if newline else ''
        if len(arguments) == 1:
            arg = arguments[0]
            if not newline and isinstance(arg, BinaryOperation) and arg.operator == '+':
                return self._gen_expr(arg)
            return self._printf_for_expr(arg, newline=newline)
        # Multiple arguments - print all with spaces
        parts = []
        for i, arg in enumerate(arguments):
            prefix = ' ' if i > 0 else ''
            expr_str = self._gen_expr(arg)
            type_name = None
            if isinstance(arg, Literal):
                type_name = arg.type.name
            elif isinstance(arg, Variable) and arg.name in self._var_types:
                type_name = self._var_types[arg.name].name
            fmt = self._printf_format_for_type_name(type_name)
            parts.append(f'printf("{prefix}{fmt}", {expr_str})')
        if newline:
            parts.append('printf("\\n")')
        return '; '.join(parts)

    def generate_translation_unit(self, constants: List[ConstDecl], functions: List[FunctionDecl],
                                   structs: List[StructDecl] = None,
                                   effects: List[EffectDecl] = None,
                                   capabilities: List[CapabilityDecl] = None,
                                   traits: List[TraitDecl] = None,
                                   enums: List[EnumDecl] = None,
                                   type_aliases: List[TypeAliasDecl] = None,
                                   distinct_types: List[DistinctTypeDecl] = None) -> str:
        lines: List[str] = []
        lines.append("#include <stdint.h>")
        lines.append("#include <stdbool.h>")
        lines.append("#include <stdio.h>")
        lines.append("#include <stdlib.h>")  # For malloc/free
        lines.append("#include <string.h>")  # For memcpy/memset
        lines.append("")
        lines.append("/* Flow runtime helpers */")
        lines.append("static char* flow_strcat(const char* a, const char* b) {")
        lines.append("    size_t la = strlen(a ? a : \"\"), lb = strlen(b ? b : \"\");")
        lines.append("    char* r = (char*)malloc(la + lb + 1);")
        lines.append("    if (!r) return NULL;")
        lines.append("    if (la) memcpy(r, a, la);")
        lines.append("    if (lb) memcpy(r + la, b, lb);")
        lines.append("    r[la + lb] = '\\0';")
        lines.append("    return r;")
        lines.append("}")
        lines.append("")
        
        # Always include math.h - many programs use math functions
        # The linker will only include what's actually used
        lines.append("#include <math.h>")
        
        lines.append("")
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
        
        # Register effects and capabilities for dispatch
        if effects:
            for effect in effects:
                self._effects[effect.name] = effect
        
        if capabilities:
            for capability in capabilities:
                self._capabilities[capability.name] = capability
        
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
        primitives = {'f32', 'f64', 'i32', 'i64', 'float', 'double', 'int'}
        no_mangle_prefixes = ()
        
        # Register all functions for overload resolution
        for fn in functions:
            self._overload_resolver.register_function(fn)
        
        # Build mangled name map
        for fn in functions:
            # Never mangle extern functions: they must link against the host C ABI.
            if getattr(fn, "is_extern", False):
                self._mangled_names[id(fn)] = fn.name
                continue
            # Functions generated from `flow` blocks keep their plain names:
            # Name_step(Name*, double) is a stable C embedding API.
            if "flow_api" in (getattr(fn, "attributes", None) or []):
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
        # Standard C library functions that don't need declarations (covered by includes)
        stdlib_functions = {'malloc', 'free', 'calloc', 'realloc', 'printf', 'sprintf',
                           'snprintf', 'fprintf', 'puts', 'putchar', 'getchar', 'fflush',
                           'memcpy', 'memset', 'strlen', 'strcmp', 'strcpy', 'strcat'}
        primitives = {'f32', 'f64', 'i32', 'i64', 'float', 'double', 'int'}
        for fn in functions:
            # Skip standard library functions - they're declared in system headers
            if fn.name in stdlib_functions:
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
        if self._pending_lambdas or self._pending_env_structs:
            lambda_lines = []
            lambda_lines.append("// Auto-generated lambda functions")
            lambda_lines.extend(self._pending_env_structs)
            for lambda_name, ret_type, params, body_lines in self._pending_lambdas:
                lambda_lines.append(f"static {ret_type} {lambda_name}({params}) {{")
                for line in body_lines:
                    lambda_lines.append(f"    {line}")
                lambda_lines.append("}")
            lambda_lines.append("")

            insert_idx = self._lambda_insert_idx
            if insert_idx is None or insert_idx > len(lines):
                insert_idx = len(lines)

            lines = lines[:insert_idx] + lambda_lines + lines[insert_idx:]

        return "\n".join(lines).rstrip() + "\n"
    
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
            
            # Global handler pointer (thread-local for multi-threaded code)
            lines.append(f"static {safe_effect_name}_Handler* _current_{safe_effect_name}_handler = NULL;")
            lines.append("")
            
            # Generate dispatch functions for each operation
            for op in effect.operations:
                ret_type = self._c_type(op.return_type)
                params_with_names = ", ".join([f"{self._c_type(p.type)} {_c_ident(p.name)}" for p in op.parameters])
                param_names = ", ".join([_c_ident(p.name) for p in op.parameters])
                
                lines.append(f"{ret_type} {safe_effect_name}_{_c_ident(op.name)}({params_with_names}) {{")
                if ret_type == "void":
                    lines.append(f"    if (_current_{safe_effect_name}_handler && _current_{safe_effect_name}_handler->{_c_ident(op.name)}) {{")
                    if param_names:
                        lines.append(f"        _current_{safe_effect_name}_handler->{_c_ident(op.name)}({param_names});")
                    else:
                        lines.append(f"        _current_{safe_effect_name}_handler->{_c_ident(op.name)}();")
                    lines.append("    }")
                else:
                    lines.append(f"    if (_current_{safe_effect_name}_handler && _current_{safe_effect_name}_handler->{_c_ident(op.name)}) {{")
                    if param_names:
                        lines.append(f"        return _current_{safe_effect_name}_handler->{_c_ident(op.name)}({param_names});")
                    else:
                        lines.append(f"        return _current_{safe_effect_name}_handler->{_c_ident(op.name)}();")
                    lines.append("    }")
                    # Return default value if no handler
                    if "int" in ret_type or ret_type in ["int32_t", "int64_t", "int8_t", "int16_t"]:
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
        elif isinstance(expr, StructLiteral):
            return Type(expr.struct_name)
        elif isinstance(expr, RecordUpdate):
            inferred = self._infer_expr_type(expr.base)
            return inferred if inferred else Type("i32")
        elif isinstance(expr, FieldAccess):
            obj_type = self._infer_expr_type(expr.object)
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
        elif isinstance(expr, BinaryOperation):
            if expr.operator in ("==", "!=", "<", "<=", ">", ">=", "&&", "||"):
                return Type("bool")
            left = self._infer_expr_type(expr.left)
            right = self._infer_expr_type(expr.right)
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
        """Check if an expression is a string type."""
        if isinstance(expr, Literal) and expr.type.name == 'string':
            return True
        if isinstance(expr, Variable) and expr.name in self._var_types:
            return self._var_types[expr.name].name == 'string'
        if isinstance(expr, FieldAccess):
            return self._infer_expr_type(expr).name == 'string'
        if isinstance(expr, BinaryOperation) and expr.operator == '+':
            # String concat if either side is string
            return self._is_string_expr(expr.left) or self._is_string_expr(expr.right)
        return False

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
        return True

    def _c_type(self, t: Type) -> str:
        if t.name == "auto":
            return "int32_t"  # Default auto-inferred type (standard C)
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

    def _c_function_decl(self, fn: FunctionDecl, use_mangled: bool = True) -> str:
        ret = self._c_type(fn.return_type)
        if fn.parameters:
            params = ", ".join([f"{self._c_type(p.type)} {_c_ident(p.name)}" for p in fn.parameters])
        else:
            # Important for system headers: `f()` (K&R) can conflict with `f(void)`.
            params = "void"
        # Use mangled name if function has overloads
        name = fn.name
        if use_mangled and id(fn) in self._mangled_names:
            name = self._mangled_names[id(fn)]
        name = _c_ident(name)
        return f"{ret} {name}({params})"

    def _gen_function(self, fn: FunctionDecl) -> List[str]:
        # Extern functions are declarations only (no emitted definition).
        if getattr(fn, "is_extern", False):
            return []
        # Forward declarations are declarations only (already have forward decl).
        if getattr(fn, "is_forward_decl", False):
            return []
        # Skip math functions that are provided by the standard library
        # BUT only if they take primitive float types (not custom types like Dual)
        math_functions = {'sin', 'cos', 'tan', 'sqrt', 'fabs', 'abs', 'log', 'exp', 'pow', 'tanh'}
        if fn.name in math_functions:
            # Only skip if all parameters are primitive types
            primitives = {'f32', 'f64', 'i32', 'i64', 'float', 'double', 'int'}
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

        lines.append(self._c_function_decl(fn, use_mangled=True) + " {")
        self._indent += 1
        
        # Save current var_types scope and create new scope for this function
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

    def _gen_statement(self, st: Statement, defer_stack: List[DeferStatement] | None = None) -> List[str]:
        if defer_stack is None:
            defer_stack = []
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

            # Track variable type for overload resolution and expression inference
            self._overload_resolver.set_var_type(st.name, self._type_to_string(decl_type))
            self._var_types[st.name] = decl_type

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
            init_expr = self._gen_expr(st.initializer)
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
        if isinstance(st, (Literal, Variable, BinaryOperation, UnaryOperation, FunctionCall, EffectCall, MethodCall)):
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
        safe_var = _c_ident(var)
        start = self._gen_expr(st.range_start)
        end = self._gen_expr(st.range_end)
        step = self._gen_expr(st.step) if st.step else "1"
        if not hasattr(self, "_for_counter"):
            self._for_counter = 0
        self._for_counter += 1
        step_var = f"__flow_step_{self._for_counter}"
        
        # Track the loop variable type
        self._var_types[var] = Type("i32")
        self._overload_resolver.set_var_type(var, "i32")
        
        # Generate standard C for loop
        lines.append(f"{self._i()}int32_t {step_var} = {step};")
        lines.append(f"{self._i()}for (int32_t {safe_var} = {start}; ({step_var} > 0) ? {safe_var} < {end} : {safe_var} > {end}; {safe_var} += {step_var}) {{")
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

        # Check if we can use a switch (integer patterns/or-of-integers, no guards)
        can_use_switch = all(
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
        if isinstance(e, Literal):
            if e.type.name == "bool":
                return "1" if e.value == "true" else "0"
            elif e.type.name == "string":
                return e.value  # String literals already have quotes
            elif e.value == "null" or e.type.name == "ptr_void" or getattr(e.type, 'is_pointer', False):
                # null pointer literal
                return "NULL"
            return e.value

        if isinstance(e, Variable):
            # Inside a lambda body, captured variables live in the closure
            # environment. This substitution happens at AST level, so names
            # that merely contain a capture as a substring stay intact.
            if self._capture_stack and e.name in self._capture_stack[-1]:
                return f"_env->{_c_ident(e.name)}"
            return _c_ident(e.name)

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
                return f"(!{self._gen_expr(e.operand)})"
            if op == "-":
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
                return f"(*({self._gen_expr(e.operand)}))"
            return f"({op} {self._gen_expr(e.operand)})"  # Add space for unknown operators

        if isinstance(e, BinaryOperation):
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
            
            # Comparison operators don't need outer parens (they have low precedence)
            if c_operator in ['==', '!=', '<', '<=', '>', '>=']:
                return f"{left_expr} {c_operator} {right_expr}"
                
            return f"({left_expr} {c_operator} {right_expr})"

        if isinstance(e, FunctionCall):
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
            # Handle len() builtin for arrays and slices
            if e.name == "len":
                if len(e.arguments) == 1:
                    arg = e.arguments[0]
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
            
            # Generate arguments, taking address of structs for capability parameters
            arg_strs = []
            for i, arg in enumerate(e.arguments):
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
            return (
                f"{self._gen_lvalue_expr(e.array)}[{self._gen_expr(e.index)}]"
            )
        if isinstance(e, FieldAccess):
            accessor = "->" if self._is_pointer_expr(e.object) else "."
            return (
                f"{self._gen_lvalue_expr(e.object)}{accessor}{_c_ident(e.field)}"
            )
        return self._gen_expr(e)

    def _gen_array_access(self, e: ArrayAccess) -> str:
        """Generate C array index access with optional bounds checking.

        For sized arrays (where the size is known at compile time), we emit
        a bounds-checked access that aborts on out-of-range indices.  For
        dynamically-sized or pointer-based arrays we fall back to raw indexing.
        """
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
                f'(int)({index_expr}), {array_size}), abort(), {array_expr}[0]))'
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
        flow_ret = e.return_type
        if flow_ret is None and not isinstance(e.body, Block):
            inferred = self._infer_expr_type(e.body)
            if inferred is not None and inferred.name != "auto":
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
                for stmt in e.body.statements:
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
        """
        init_expr = self._gen_lambda(st.initializer)
        info = self._last_lambda_info
        name = _sanitize_identifier(st.name)
        if info["captures"]:
            self._closure_vars[st.name] = info
            self._var_types[st.name] = Type(info["closure_name"])
            self._overload_resolver.set_var_type(st.name, info["closure_name"])
            return [f"{self._i()}{info['closure_name']} {name} = {init_expr};"]
        self._fnptr_vars[st.name] = info
        self._var_types[st.name] = Type(info["fn_typedef"])
        self._overload_resolver.set_var_type(st.name, info["fn_typedef"])
        return [f"{self._i()}{info['fn_typedef']} {name} = {init_expr};"]


def flow_to_c(declarations: List[Any], *, source_file: str | None = None, debug_info: bool = False) -> str:
    """Convert FLOW declarations to C code"""
    try:
        generator = CGenerator(source_file=source_file, debug_info=debug_info)
        
        # Separate declarations by type
        constants = [d for d in declarations if isinstance(d, ConstDecl)]
        functions = [d for d in declarations if isinstance(d, FunctionDecl)]
        structs = [d for d in declarations if isinstance(d, StructDecl)]
        effects = [d for d in declarations if isinstance(d, EffectDecl)]
        capabilities = [d for d in declarations if isinstance(d, CapabilityDecl)]
        traits = [d for d in declarations if isinstance(d, TraitDecl)]
        impls = [d for d in declarations if isinstance(d, ImplDecl)]
        enums = [d for d in declarations if isinstance(d, EnumDecl)]
        type_aliases = [d for d in declarations if isinstance(d, TypeAliasDecl)]
        distinct_types = [d for d in declarations if isinstance(d, DistinctTypeDecl)]
        
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
        
        out = generator.generate_translation_unit(constants, functions, structs, effects, capabilities, traits, enums, type_aliases, distinct_types)
        # Expose overload warnings without changing the return signature.
        flow_to_c.last_warnings = list(generator._overload_resolver.warnings)
        return out
    except Exception as e:
        print(f"C generation error: {e}")
        import traceback
        traceback.print_exc()
        raise
