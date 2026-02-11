#!/usr/bin/env python3
"""
FLOW to Python Package Generator

Generates Python wheels from Flow source code by:
1. Compiling Flow to C (via c_generator)
2. Generating CPython extension bindings
3. Building a standard Python wheel

Key principles:
- Python is an output target, not a parent language
- Zero boilerplate for common cases
- Automatic export of ABI-compatible public symbols
- Strict semantic separation between Flow and Python
"""

from __future__ import annotations

import re
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from .parser import (
    FunctionDecl,
    StructDecl,
    ConstDecl,
    EnumDecl,
    Type,
    TypeAliasDecl,
    DistinctTypeDecl,
)
from .c_generator import flow_to_c


# =============================================================================
# ABI COMPATIBILITY RULES
# =============================================================================

@dataclass
class ABIType:
    """Represents a type's Python ABI mapping."""
    flow_type: str
    python_type: str
    c_type: str
    converter_to_py: str      # C code to convert to PyObject*
    converter_from_py: str    # C code to convert from PyObject*
    format_char: str          # For PyArg_ParseTuple
    is_compatible: bool = True
    reason: str = ""


# Type mapping from Flow to Python
ABI_TYPE_MAP: Dict[str, ABIType] = {
    # Integers
    "i32": ABIType("i32", "int", "int32_t", 
                   "PyLong_FromLong({val})", 
                   "(int32_t)PyLong_AsLong({val})", "i"),
    "i64": ABIType("i64", "int", "int64_t",
                   "PyLong_FromLongLong({val})",
                   "(int64_t)PyLong_AsLongLong({val})", "L"),
    "u32": ABIType("u32", "int", "uint32_t",
                   "PyLong_FromUnsignedLong({val})",
                   "(uint32_t)PyLong_AsUnsignedLong({val})", "I"),
    "u64": ABIType("u64", "int", "uint64_t",
                   "PyLong_FromUnsignedLongLong({val})",
                   "(uint64_t)PyLong_AsUnsignedLongLong({val})", "K"),
    
    # Floats
    "f32": ABIType("f32", "float", "float",
                   "PyFloat_FromDouble((double){val})",
                   "(float)PyFloat_AsDouble({val})", "f"),
    "f64": ABIType("f64", "float", "double",
                   "PyFloat_FromDouble({val})",
                   "PyFloat_AsDouble({val})", "d"),
    
    # Boolean
    "bool": ABIType("bool", "bool", "int",
                    "PyBool_FromLong({val})",
                    "PyObject_IsTrue({val})", "p"),
    
    # String
    "string": ABIType("string", "str", "const char*",
                      "PyUnicode_FromString({val})",
                      "PyUnicode_AsUTF8({val})", "s"),
    
    # Void
    "void": ABIType("void", "None", "void",
                    "Py_None", "", ""),
}


def _resolve_type_alias(flow_type: Type, type_aliases: Dict[str, Type], distinct_types: Dict[str, Type]) -> Type:
    current = flow_type
    seen: Set[str] = set()
    while isinstance(current, Type) and (current.name in type_aliases or current.name in distinct_types):
        name = current.name
        if name in seen:
            return current
        seen.add(name)
        if name in type_aliases:
            current = type_aliases[name]
            continue
        if name in distinct_types:
            current = distinct_types[name]
            continue
    return current


def is_abi_compatible(
    flow_type: Type,
    structs: Dict[str, StructDecl],
    type_aliases: Dict[str, Type] | None = None,
    distinct_types: Dict[str, Type] | None = None,
) -> Tuple[bool, str]:
    """
    Check if a Flow type can cross the Python ABI boundary.
    Returns (is_compatible, reason_if_not).
    """
    type_aliases = type_aliases or {}
    distinct_types = distinct_types or {}
    base = _resolve_type_alias(flow_type, type_aliases, distinct_types)
    type_name = base.name if isinstance(base, Type) else str(base)
    
    # Primitive types
    if type_name in ABI_TYPE_MAP:
        return True, ""
    
    # Pointer types - exposed as capsules
    if type_name.startswith("ptr<"):
        inner = type_name[4:-1]
        if inner == "void":
            return True, ""  # Opaque pointer
        # Pointer to known struct is ok
        if inner in structs:
            return True, ""
        return True, ""  # Allow but warn
    
    # Array types - exposed as lists
    if type_name.startswith("array<"):
        # Extract element type
        match = re.match(r"array<(.+),\s*(\d+)>", type_name)
        if match:
            elem_type = match.group(1)
            if elem_type in ABI_TYPE_MAP:
                return True, ""
        return False, "Array element type not ABI-compatible"
    
    # Struct types - exposed as dicts or named tuples
    if type_name in structs:
        struct = structs[type_name]
        for field_name, field_type in struct.fields:
            compat, reason = is_abi_compatible(field_type, structs, type_aliases, distinct_types)
            if not compat:
                return False, f"Struct field '{field_name}' not compatible: {reason}"
        return True, ""
    
    # Unknown type
    return False, f"Unknown type '{type_name}'"


def is_public_symbol(name: str) -> bool:
    """
    Determine if a symbol should be exported by default.
    Private = starts with underscore.
    """
    return not name.startswith("_")


# =============================================================================
# EXPORT INFERENCE
# =============================================================================

@dataclass
class ExportDiagnostic:
    """Diagnostic message for export inference."""
    symbol: str
    kind: str  # "exported", "excluded", "warning"
    reason: str
    line: int = 0


@dataclass 
class ExportedSymbol:
    """A symbol that will be exported to Python."""
    name: str
    python_name: str  # May be renamed via override
    kind: str  # "function", "struct", "const", "enum"
    decl: Any
    doc: str = ""
    

@dataclass
class ExportResult:
    """Result of export inference."""
    exports: List[ExportedSymbol] = field(default_factory=list)
    diagnostics: List[ExportDiagnostic] = field(default_factory=list)


def infer_exports(
    functions: List[FunctionDecl],
    structs: Dict[str, StructDecl],
    consts: List[ConstDecl],
    enums: Dict[str, EnumDecl],
    type_aliases: Dict[str, Type] | None = None,
    distinct_types: Dict[str, Type] | None = None,
) -> ExportResult:
    """
    Deterministically infer which symbols to export to Python.
    
    Rules:
    1. Public (non-underscore) top-level symbols are candidates
    2. All parameter and return types must be ABI-compatible
    3. Clear diagnostics for excluded symbols
    """
    result = ExportResult()
    
    # Functions
    for fn in functions:
        if not is_public_symbol(fn.name):
            result.diagnostics.append(ExportDiagnostic(
                fn.name, "excluded", "Private symbol (starts with underscore)"
            ))
            continue
        
        # Check return type
        ret_compat, ret_reason = is_abi_compatible(fn.return_type, structs, type_aliases, distinct_types)
        if not ret_compat:
            result.diagnostics.append(ExportDiagnostic(
                fn.name, "excluded", f"Return type not ABI-compatible: {ret_reason}"
            ))
            continue
        
        # Check parameter types
        all_params_ok = True
        for param in fn.parameters:
            param_compat, param_reason = is_abi_compatible(param.type, structs, type_aliases, distinct_types)
            if not param_compat:
                result.diagnostics.append(ExportDiagnostic(
                    fn.name, "excluded", 
                    f"Parameter '{param.name}' not ABI-compatible: {param_reason}"
                ))
                all_params_ok = False
                break
        
        if not all_params_ok:
            continue
        
        # Skip main function
        if fn.name == "main":
            result.diagnostics.append(ExportDiagnostic(
                fn.name, "excluded", "Entry point 'main' not exported"
            ))
            continue
        
        # Export this function
        result.exports.append(ExportedSymbol(
            name=fn.name,
            python_name=fn.name,
            kind="function",
            decl=fn
        ))
        result.diagnostics.append(ExportDiagnostic(
            fn.name, "exported", "Public function with ABI-compatible signature"
        ))
    
    # Structs
    for name, struct in structs.items():
        if not is_public_symbol(name):
            result.diagnostics.append(ExportDiagnostic(
                name, "excluded", "Private struct"
            ))
            continue
        
        compat, reason = is_abi_compatible(Type(name), structs, type_aliases, distinct_types)
        if compat:
            result.exports.append(ExportedSymbol(
                name=name,
                python_name=name,
                kind="struct",
                decl=struct
            ))
            result.diagnostics.append(ExportDiagnostic(
                name, "exported", "Public struct with ABI-compatible fields"
            ))
        else:
            result.diagnostics.append(ExportDiagnostic(
                name, "excluded", f"Struct not ABI-compatible: {reason}"
            ))
    
    # Constants
    for const in consts:
        if not is_public_symbol(const.name):
            continue
        
        compat, reason = is_abi_compatible(const.type, structs, type_aliases, distinct_types)
        if compat:
            result.exports.append(ExportedSymbol(
                name=const.name,
                python_name=const.name,
                kind="const",
                decl=const
            ))
    
    return result


# =============================================================================
# PYTHON C EXTENSION GENERATOR
# =============================================================================

class PythonBindingGenerator:
    """Generates CPython extension module bindings."""
    
    def __init__(self, module_name: str, exports: ExportResult, structs: Dict[str, StructDecl]):
        self.module_name = module_name
        self.exports = exports
        self.structs = structs
    
    def generate_header(self) -> str:
        """Generate the C header for the Python extension."""
        return f'''/* Auto-generated Python bindings for {self.module_name} */
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdint.h>

/* Forward declarations for Flow functions */
'''
    
    def generate_function_wrapper(self, sym: ExportedSymbol) -> str:
        """Generate a CPython wrapper for a Flow function."""
        fn = sym.decl
        
        # Build argument parsing
        format_str = ""
        arg_names = []
        c_args = []
        parse_vars = []
        
        for param in fn.parameters:
            type_name = param.type.name if isinstance(param.type, Type) else str(param.type)
            if type_name in ABI_TYPE_MAP:
                abi = ABI_TYPE_MAP[type_name]
                format_str += abi.format_char
                arg_names.append(param.name)
                parse_vars.append(f"    {abi.c_type} {param.name};")
                c_args.append(f"&{param.name}")
            else:
                # Handle complex types
                format_str += "O"
                arg_names.append(param.name)
                parse_vars.append(f"    PyObject* {param.name}_obj;")
                c_args.append(f"&{param.name}_obj")
        
        # Build return conversion
        ret_type = fn.return_type.name if isinstance(fn.return_type, Type) else str(fn.return_type)
        if ret_type == "void":
            ret_conv = "    Py_RETURN_NONE;"
            ret_decl = ""
            call_prefix = "    "
        elif ret_type in ABI_TYPE_MAP:
            abi = ABI_TYPE_MAP[ret_type]
            ret_conv = f"    return {abi.converter_to_py.format(val='result')};"
            ret_decl = f"    {abi.c_type} result = "
            call_prefix = ""
        else:
            ret_conv = "    Py_RETURN_NONE;"
            ret_decl = ""
            call_prefix = "    "
        
        # Build mangled C function name (Flow uses type-based name mangling)
        mangled_name = fn.name
        if fn.parameters:
            param_suffix = "_".join(
                (p.type.name if isinstance(p.type, Type) else str(p.type)).replace("<", "_").replace(">", "").replace(",", "_")
                for p in fn.parameters
            )
            mangled_name = f"{fn.name}_{param_suffix}"
        
        # Generate wrapper
        wrapper = f'''
static PyObject* py_{sym.python_name}(PyObject* self, PyObject* args) {{
{chr(10).join(parse_vars)}
    
    if (!PyArg_ParseTuple(args, "{format_str}", {", ".join(c_args) if c_args else ""})) {{
        return NULL;
    }}
    
{ret_decl}{call_prefix}{mangled_name}({", ".join(arg_names)});
{ret_conv}
}}
'''
        return wrapper
    
    def generate_struct_type(self, sym: ExportedSymbol) -> str:
        """Generate a Python type wrapper for a Flow struct."""
        
        # For now, generate a simple dict-based approach
        # A full implementation would create a proper Python type
        return f'''
/* Struct {sym.name} is exposed as a dictionary */
'''
    
    def generate_method_table(self) -> str:
        """Generate the PyMethodDef table."""
        methods = []
        for sym in self.exports.exports:
            if sym.kind == "function":
                doc = sym.doc or f"{sym.name} function"
                methods.append(
                    f'    {{"{sym.python_name}", py_{sym.python_name}, METH_VARARGS, "{doc}"}},'
                )
        
        return f'''
static PyMethodDef {self.module_name}_methods[] = {{
{chr(10).join(methods)}
    {{NULL, NULL, 0, NULL}}
}};
'''
    
    def generate_module_init(self) -> str:
        """Generate the module initialization function."""
        return f'''
static struct PyModuleDef {self.module_name}_module = {{
    PyModuleDef_HEAD_INIT,
    "{self.module_name}",
    "Flow-generated module: {self.module_name}",
    -1,
    {self.module_name}_methods
}};

PyMODINIT_FUNC PyInit_{self.module_name}(void) {{
    return PyModule_Create(&{self.module_name}_module);
}}
'''
    
    def generate(self, c_code: str) -> str:
        """Generate the complete Python extension source."""
        parts = [
            self.generate_header(),
            "",
            "/* ===== Flow compiled code ===== */",
            c_code,
            "",
            "/* ===== Python wrappers ===== */",
        ]
        
        # Generate wrappers for exported functions
        for sym in self.exports.exports:
            if sym.kind == "function":
                parts.append(self.generate_function_wrapper(sym))
        
        # Generate struct types
        for sym in self.exports.exports:
            if sym.kind == "struct":
                parts.append(self.generate_struct_type(sym))
        
        # Generate method table and module init
        parts.append(self.generate_method_table())
        parts.append(self.generate_module_init())
        
        return "\n".join(parts)


# =============================================================================
# WHEEL BUILDER
# =============================================================================

def generate_setup_py(module_name: str, version: str = "0.1.0") -> str:
    """Generate setup.py for building the wheel."""
    return f'''#!/usr/bin/env python3
from setuptools import setup, Extension

{module_name}_ext = Extension(
    '{module_name}',
    sources=['{module_name}_ext.c'],
    extra_compile_args=['-O2', '-Wall'],
)

setup(
    name='{module_name}',
    version='{version}',
    description='Flow-generated Python extension',
    ext_modules=[{module_name}_ext],
    python_requires='>=3.8',
)
'''


def generate_pyproject_toml(module_name: str, version: str = "0.1.0") -> str:
    """Generate pyproject.toml for modern Python packaging."""
    return f'''[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{module_name}"
version = "{version}"
description = "Flow-generated Python extension"
requires-python = ">=3.8"
'''


def build_wheel(
    module_name: str,
    extension_source: str,
    output_dir: Path,
    version: str = "0.1.0",
) -> Path:
    """Build a Python wheel from the generated extension source."""
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        
        # Write extension source
        ext_file = tmppath / f"{module_name}_ext.c"
        ext_file.write_text(extension_source)
        
        # Write setup.py
        setup_file = tmppath / "setup.py"
        setup_file.write_text(generate_setup_py(module_name, version))
        
        # Write pyproject.toml
        pyproject_file = tmppath / "pyproject.toml"
        pyproject_file.write_text(generate_pyproject_toml(module_name, version))
        
        # Build wheel
        result = subprocess.run(
            ["python3", "-m", "pip", "wheel", ".", "-w", str(output_dir)],
            cwd=tmppath,
            capture_output=True,
            text=True,
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Wheel build failed:\n{result.stderr}")
        
        # Find the built wheel
        wheels = list(output_dir.glob(f"{module_name}*.whl"))
        if wheels:
            return wheels[0]
        raise RuntimeError("No wheel file produced")


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

class PythonTarget:
    """
    Python compilation target for Flow.
    
    Usage:
        target = PythonTarget(ast, module_name="mylib")
        target.compile()
        target.build_wheel(output_dir)
    """
    
    def __init__(
        self,
        ast: List[Any],
        module_name: str,
        version: str = "0.1.0",
        verbose: bool = False,
    ):
        self.ast = ast
        self.module_name = module_name
        self.version = version
        self.verbose = verbose
        
        # Collect declarations
        self.functions: List[FunctionDecl] = []
        self.structs: Dict[str, StructDecl] = {}
        self.consts: List[ConstDecl] = []
        self.enums: Dict[str, EnumDecl] = {}
        self.type_aliases: Dict[str, Type] = {}
        self.distinct_types: Dict[str, Type] = {}
        
        for node in ast:
            if isinstance(node, FunctionDecl):
                self.functions.append(node)
            elif isinstance(node, StructDecl):
                self.structs[node.name] = node
            elif isinstance(node, ConstDecl):
                self.consts.append(node)
            elif isinstance(node, EnumDecl):
                self.enums[node.name] = node
            elif isinstance(node, TypeAliasDecl):
                self.type_aliases[node.name] = node.base_type
            elif isinstance(node, DistinctTypeDecl):
                self.distinct_types[node.name] = node.base_type
        
        self.export_result: Optional[ExportResult] = None
        self.c_code: Optional[str] = None
        self.extension_source: Optional[str] = None
    
    def analyze_exports(self) -> ExportResult:
        """Analyze which symbols to export."""
        self.export_result = infer_exports(
            self.functions,
            self.structs,
            self.consts,
            self.enums,
            self.type_aliases,
            self.distinct_types,
        )
        return self.export_result
    
    def print_diagnostics(self):
        """Print export inference diagnostics."""
        if not self.export_result:
            self.analyze_exports()
        
        print(f"\n{'='*60}")
        print(f"Python Export Analysis: {self.module_name}")
        print(f"{'='*60}\n")
        
        exported = [d for d in self.export_result.diagnostics if d.kind == "exported"]
        excluded = [d for d in self.export_result.diagnostics if d.kind == "excluded"]
        
        print(f"✅ Exported ({len(exported)} symbols):")
        for d in exported:
            print(f"   {d.symbol}: {d.reason}")
        
        print(f"\n⚠️  Excluded ({len(excluded)} symbols):")
        for d in excluded:
            print(f"   {d.symbol}: {d.reason}")
        
        print()
    
    def compile(self) -> str:
        """Compile Flow to Python extension source."""
        if not self.export_result:
            self.analyze_exports()
        
        # Generate C code via standard C generator
        self.c_code = flow_to_c(self.ast)
        
        # Generate Python bindings
        binding_gen = PythonBindingGenerator(
            self.module_name,
            self.export_result,
            self.structs,
        )
        self.extension_source = binding_gen.generate(self.c_code)
        
        return self.extension_source
    
    def build_wheel(self, output_dir: Path) -> Path:
        """Build a Python wheel."""
        if not self.extension_source:
            self.compile()
        
        return build_wheel(
            self.module_name,
            self.extension_source,
            output_dir,
            self.version,
        )
    
    def write_extension_source(self, output_path: Path):
        """Write the extension source without building."""
        if not self.extension_source:
            self.compile()
        
        output_path.write_text(self.extension_source)


# =============================================================================
# CLI INTEGRATION
# =============================================================================

def compile_to_python(
    source_path: Path,
    output_dir: Path,
    module_name: Optional[str] = None,
    version: str = "0.1.0",
    verbose: bool = False,
    build: bool = True,
) -> Optional[Path]:
    """
    Compile a Flow source file to a Python package.
    
    Args:
        source_path: Path to .flow source file
        output_dir: Directory for output files
        module_name: Python module name (default: source filename)
        version: Package version
        verbose: Print diagnostics
        build: Whether to build wheel (or just generate source)
    
    Returns:
        Path to wheel file if build=True, else None
    """
    from .parser import Lexer, Parser
    
    # Parse source
    source = source_path.read_text()
    lexer = Lexer(source)
    parser = Parser(lexer)
    ast = parser.parse()
    
    # Determine module name
    if module_name is None:
        module_name = source_path.stem.replace("-", "_").replace(".", "_")
    
    # Create target
    target = PythonTarget(ast, module_name, version, verbose)
    
    if verbose:
        target.print_diagnostics()
    
    # Compile
    target.compile()
    
    # Output
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if build:
        return target.build_wheel(output_dir)
    else:
        ext_path = output_dir / f"{module_name}_ext.c"
        target.write_extension_source(ext_path)
        print(f"Generated: {ext_path}")
        return None
