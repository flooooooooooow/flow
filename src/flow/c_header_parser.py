"""C header parser for @cImport.

Preprocesses a C header with `cpp -P`, then parses the resulting
declarations to extract:
  - function prototypes
  - typedef declarations (including opaque struct typedefs)
  - struct definitions with fields
  - enum constants
  - simple variable declarations

The output is a list of Flow parser declaration objects
(FunctionDecl, ExternTypeDecl, ConstDecl, StructDecl) that the
transpiler inserts into the declaration list so the C generator
emits the right prototypes.

Strategy: cpp expands macros and includes, leaving plain C.
We tokenize the preprocessed text and walk through top-level
declarations. We skip function definitions (bodies), static
inline functions, and compiler-specific attributes.
"""

from __future__ import annotations

import re
import subprocess
import sys
from typing import List, Optional, Tuple

from .parser import (
    FunctionDecl,
    ExternTypeDecl,
    ConstDecl,
    Parameter,
    Type as ParsedType,
    Block,
    Literal,
)

# Functions that the type checker flags as dangerous FFI (#276).
# @cImport pulls these from system headers; skip them so the user doesn't
# need @unsafe for declarations they never wrote.
_DANGEROUS_IMPORT_NAMES = frozenset({
    "system", "gets", "strcpy", "strcat", "sprintf", "vsprintf",
    "scanf", "sscanf", "realpath", "getwd",
})


# C type to Flow type mapping
_C_TO_FLOW = {
    "void": "void",
    "char": "u8",
    "signed char": "i8",
    "unsigned char": "u8",
    "short": "i16",
    "short int": "i16",
    "unsigned short": "u16",
    "unsigned short int": "u16",
    "int": "i32",
    "signed int": "i32",
    "unsigned": "u32",
    "unsigned int": "u32",
    "long": "i64",
    "long int": "i64",
    "unsigned long": "u64",
    "unsigned long int": "u64",
    "long long": "i64",
    "long long int": "i64",
    "unsigned long long": "u64",
    "unsigned long long int": "u64",
    "float": "f32",
    "double": "f64",
    "long double": "f64",
    "size_t": "u64",
    "ssize_t": "i64",
    "ptrdiff_t": "i64",
    "intptr_t": "i64",
    "uintptr_t": "u64",
    "int8_t": "i8",
    "uint8_t": "u8",
    "int16_t": "i16",
    "uint16_t": "u16",
    "int32_t": "i32",
    "uint32_t": "u32",
    "int64_t": "i64",
    "uint64_t": "u64",
    "bool": "bool",
    "_Bool": "bool",
    "FILE": "FILE",
    "va_list": "ptr<void>",
}

# Functions that are already declared in user extern blocks or are
# standard libc functions that conflict with system headers.
# The auto-prototype generator skips these to avoid duplicate declarations.
_LIBC_SKIP_FUNCS = {
    "atoi", "atof", "atol", "strtol", "strtod", "strtoul",
    "exit", "abort", "malloc", "free", "calloc", "realloc",
    "sqrt", "fabs", "pow", "abs", "labs",
    "sin", "cos", "tan", "log", "log2", "log10", "exp",
    "floor", "ceil", "round", "fmod",
    "strcmp", "strncmp", "strlen", "strchr", "strrchr", "strstr",
    "popen", "pclose", "fscanf", "sscanf", "scanf",
    "memcpy", "memmove", "memset", "strcpy", "strncpy",
    "strcat", "strncat", "sprintf", "snprintf", "fprintf", "printf",
    "vsnprintf", "vsprintf", "vfprintf", "vprintf",
    "fgets", "fread", "fwrite", "fputc", "fputs", "putc", "putchar",
    "getchar", "fgetc", "getc", "strdup", "bcopy", "bzero",
    "puts",
}


def _c_type_to_flow(c_type: str) -> str:
    """Convert a C type string to a Flow type string."""
    c_type = c_type.strip()
    # Remove const/volatile/restrict qualifiers and attributes
    c_type = re.sub(r"\b(const|volatile|restrict|__restrict|__restrict__)\b", "", c_type)
    c_type = re.sub(r"__attribute__\s*\([^)]*\)", "", c_type)
    c_type = c_type.strip()
    # Handle pointers
    ptr_count = 0
    while c_type.endswith("*"):
        ptr_count += 1
        c_type = c_type[:-1].strip()
    # Map base type
    base = _C_TO_FLOW.get(c_type, c_type)
    # Wrap in ptr<>
    for _ in range(ptr_count):
        base = f"ptr<{base}>"
    return base


def _preprocess_header(header: str, include_dirs: List[str]) -> str:
    """Preprocess a header and return the expanded text.

    A header name cannot be passed to the preprocessor directly, so we pipe
    `#include <header>` through it on stdin.

    Two preprocessors are tried in order. On some macOS installs `cpp` is a
    wrapper that mishandles the `-` stdin argument and fails with
    "no such file or directory: 'c'", writing nothing to stdout. Falling back
    only on FileNotFoundError missed that case, so @cImport silently parsed
    zero declarations there and every @cImport test passed without exercising
    the feature. Empty output now falls through to `clang -E` as well.
    """
    if header.startswith("/") or header.startswith('"'):
        include_line = f"#include {header}\n"
    else:
        include_line = f"#include <{header}>\n"

    def run(argv: List[str]) -> str:
        argv = list(argv)
        for d in include_dirs:
            argv.extend(["-I", d])
        argv.append("-")  # read from stdin
        result = subprocess.run(
            argv,
            input=include_line,
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.stdout

    last_error: Optional[Exception] = None
    for argv in (["cpp", "-P"], ["clang", "-E", "-P"], ["gcc", "-E", "-P"]):
        try:
            text = run(argv)
        except FileNotFoundError:
            continue
        except Exception as e:  # timeout, permissions, ...
            last_error = e
            continue
        if text.strip():
            return text

    if last_error is not None:
        print(f"Warning: @cImport preprocessing failed: {last_error}", file=sys.stderr)
    else:
        print(
            f"Warning: @cImport could not preprocess {header!r}; "
            "no declarations were imported",
            file=sys.stderr,
        )
    return ""


def _strip_attributes(text: str) -> str:
    """Remove __attribute__((...)), __builtin, and nullability annotations.

    Apple's headers annotate pointers with `_Nonnull` / `_Nullable`. They are
    qualifiers, not part of the type, but they used to survive into generated
    type names: two distinct signatures both mangled to
    `ptr_int_____Nonnull___compar___void_____void_` and the second typedef was
    rejected as a redefinition.
    """
    text = re.sub(r"__attribute__\s*\(\([^)]*\)\)", "", text)
    text = re.sub(r"__builtin_\w+", "", text)
    text = re.sub(r"\b_(?:Nonnull|Nullable|Null_unspecified)\b", "", text)
    return text


def _read_balanced(text: str, start: int, open_ch: str, close_ch: str) -> Tuple[str, int]:
    """Read from start until the matching close character. Returns (content, end_pos)."""
    depth = 0
    i = start
    while i < len(text):
        if text[i] == open_ch:
            depth += 1
        elif text[i] == close_ch:
            depth -= 1
            if depth == 0:
                return text[start:i], i + 1
        i += 1
    return text[start:], len(text)


def _split_top_level(text: str) -> List[str]:
    """Split preprocessed C into top-level declaration chunks.

    Handles braces and semicolons. Skips static inline function bodies.
    """
    chunks = []
    i = 0
    while i < len(text):
        # Skip whitespace
        while i < len(text) and text[i] in " \t\n\r":
            i += 1
        if i >= len(text):
            break

        # Read until semicolon at brace depth 0, or until closing brace
        # of a function/struct/enum/union body
        start = i
        depth = 0
        while i < len(text):
            ch = text[i]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    # Check if there's a semicolon after the closing brace
                    j = i + 1
                    while j < len(text) and text[j] in " \t\n\r":
                        j += 1
                    if j < len(text) and text[j] == ";":
                        i = j + 1
                    else:
                        i += 1
                    chunk = text[start:i].strip()
                    if chunk:
                        chunks.append(chunk)
                    break
            elif ch == ";" and depth == 0:
                chunk = text[start:i].strip()
                if chunk:
                    chunks.append(chunk)
                i += 1
                break
            i += 1
        else:
            chunk = text[start:].strip()
            if chunk:
                chunks.append(chunk)
            break

    return chunks


def parse_c_header(header: str, include_dirs: Optional[List[str]] = None) -> List:
    """Parse a C header and return Flow declarations."""
    if include_dirs is None:
        include_dirs = []

    include_dirs.extend(["/usr/include", "/usr/local/include"])

    text = _preprocess_header(header, include_dirs)
    if not text:
        return []

    declarations = []
    chunks = _split_top_level(text)

    for chunk in chunks:
        chunk = _strip_attributes(chunk).strip()
        if not chunk:
            continue

        # Skip extern "C" blocks
        if chunk.startswith("extern"):
            rest = chunk[6:].strip()
            if rest.startswith('"C"'):
                continue
            # Skip extern variable declarations (rare in headers)
            continue

        # Skip static inline functions (they have bodies)
        if re.match(r"^static\s+(__inline__|__inline|inline)", chunk):
            continue
        if re.match(r"^__inline", chunk):
            continue

        # Skip __extension__ and compiler builtins
        if chunk.startswith("__extension__"):
            chunk = chunk[13:].strip()
            if not chunk:
                continue

        # Handle typedef
        if chunk.startswith("typedef"):
            declarations.extend(_parse_typedef(chunk))
            continue

        # Handle struct/union/enum definitions
        if re.match(r"^(struct|union|enum)\b", chunk):
            declarations.extend(_parse_struct_enum(chunk))
            continue

        # Try to parse as function declaration (no body)
        if "{" not in chunk:
            fn = _parse_function(chunk)
            if fn:
                declarations.append(fn)
                continue

        # Try to parse as variable declaration
        var = _parse_variable(chunk)
        if var:
            declarations.append(var)

    return declarations


def _parse_typedef(chunk: str) -> List:
    """Parse a typedef declaration."""
    # typedef struct Name Name;  -> opaque type
    m = re.match(r"typedef\s+struct\s+(\w+)\s+(\w+)\s*$", chunk)
    if m:
        return [ExternTypeDecl(name=m.group(2))]

    # typedef struct { fields } Name;  -> opaque type (skip fields, C header has layout)
    if re.match(r"typedef\s+struct\s*\{", chunk) or re.match(r"typedef\s+struct\s+\w+\s*\{", chunk):
        m = re.search(r"\}\s*(\w+)\s*$", chunk)
        if m:
            return [ExternTypeDecl(name=m.group(1))]
        return []

    # typedef union { ... } Name;
    if re.match(r"typedef\s+union\s*\{", chunk) or re.match(r"typedef\s+union\s+\w+\s*\{", chunk):
        m = re.search(r"\}\s*(\w+)\s*$", chunk)
        if m:
            return [ExternTypeDecl(name=m.group(1))]
        return []

    # typedef enum { ... } Name;  -> generate ConstDecl for each enum value
    if re.match(r"typedef\s+enum\s*\{", chunk) or re.match(r"typedef\s+enum\s+\w+\s*\{", chunk):
        return _parse_enum_body(chunk)

    # typedef enum Name { ... };  -> generate ConstDecl for each enum value
    if re.match(r"typedef\s+enum\s+\w+\s*\{", chunk):
        return _parse_enum_body(chunk)

    # typedef <type> (*Name)(params);  -> function pointer typedef
    m = re.match(r"typedef\s+(.+?)\s*\(\s*\*\s*(\w+)\s*\)\s*\((.*)\)\s*$", chunk)
    if m:
        # We don't generate anything for function pointer typedefs.
        # The C header provides the typedef. Flow code uses ptr<fn(...)>.
        return []

    # typedef <type> Name;  -> simple typedef, C header handles it
    m = re.match(r"typedef\s+(.+?)\s+(\w+)\s*$", chunk)
    if m:
        return []

    return []


def _parse_enum_body(chunk: str) -> List:
    """Extract enum constants from a typedef enum { ... } Name; or enum Name { ... };"""
    # Find the brace block
    brace_start = chunk.find("{")
    if brace_start < 0:
        return []
    body, _ = _read_balanced(chunk, brace_start + 1, "{", "}")
    if not body:
        return []

    decls = []
    # Split by commas, handling nested parens
    parts = _split_params(body)
    for part in parts:
        part = part.strip()
        if not part:
            continue
        # Each part is either: NAME or NAME = value
        m = re.match(r"^(\w+)\s*(?:=\s*(.+))?$", part)
        if m:
            name = m.group(1)
            value = m.group(2)
            if value:
                value = value.strip()
                # Try to parse as integer
                try:
                    val = _parse_int(value)
                    cd = ConstDecl(name=name, type=ParsedType("i32"), value=Literal(val))
                    decls.append(cd)
                except (ValueError, TypeError):
                    # Skip complex enum values
                    pass
            else:
                # Auto-incrementing enum value, skip (we don't track the counter)
                pass
    return decls


def _parse_int(s: str) -> int:
    """Parse a C integer literal."""
    s = s.strip()
    # Remove suffixes
    s = re.sub(r'[uUlL]+$', '', s)
    if s.startswith("0x") or s.startswith("0X"):
        return int(s, 16)
    if s.startswith("0b") or s.startswith("0B"):
        return int(s, 2)
    if s.startswith("0") and len(s) > 1 and s[1].isdigit():
        return int(s, 8)
    return int(s)


def _parse_struct_enum(chunk: str) -> List:
    """Parse struct/union/enum definitions."""
    # struct Name { fields };  -> we could generate a StructDecl, but
    # since the C header provides the layout, we only need the name
    # for opaque pointer types. Skip the full layout.
    m = re.match(r"^(struct|union|enum)\s+(\w+)\s*\{", chunk)
    if m:
        # The C header defines the layout. We just need the name.
        # If it's an enum, extract constants.
        if m.group(1) == "enum":
            return _parse_enum_body(chunk)
        return []

    # struct Name;  -> forward declaration, register as opaque type
    m = re.match(r"^(struct|union)\s+(\w+)\s*$", chunk)
    if m:
        return [ExternTypeDecl(name=m.group(2))]

    return []


def _parse_function(chunk: str) -> Optional[FunctionDecl]:
    """Parse a C function declaration into a FunctionDecl."""
    if "(" not in chunk or ")" not in chunk:
        return None

    # Must not have a body
    if "{" in chunk:
        return None

    # Strip leading storage class specifiers
    chunk = re.sub(r"^(extern|static)\s+", "", chunk).strip()

    # Find the function name: identifier right before the first (
    paren_pos = chunk.find("(")
    if paren_pos < 0:
        return None

    before_paren = chunk[:paren_pos].strip()
    after_paren = chunk[paren_pos + 1:]

    # Find the matching close paren
    depth = 1
    end_paren = 0
    for i, ch in enumerate(after_paren):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                end_paren = i
                break
    else:
        return None

    params_str = after_paren[:end_paren].strip()

    # Split before_paren into return type and function name
    tokens = before_paren.split()
    if len(tokens) < 2:
        return None

    fn_name = tokens[-1]
    ret_type_str = " ".join(tokens[:-1])

    # Skip if function name is not a valid identifier
    if not re.match(r"^\w+$", fn_name):
        return None

    # Skip compiler intrinsics and double-underscore names
    if fn_name.startswith("__"):
        return None

    # Skip known libc functions that conflict with system headers
    if fn_name in _LIBC_SKIP_FUNCS:
        return None

    # Parse parameters
    params = _parse_params(params_str)

    # Convert return type
    ret_flow = _c_type_to_flow(ret_type_str)

    # Create FunctionDecl
    func = FunctionDecl(
        name=fn_name,
        parameters=params,
        return_type=ParsedType(ret_flow),
        body=Block([]),
        attributes=[],
    )
    func.is_extern = True
    return func


def _parse_variable(chunk: str) -> Optional[ConstDecl]:
    """Parse a simple variable declaration like `extern int errno;`"""
    # Skip if it has parentheses (function declaration)
    if "(" in chunk:
        return None

    tokens = chunk.split()
    if len(tokens) < 2:
        return None

    name = tokens[-1]
    type_str = " ".join(tokens[:-1])

    if not re.match(r"^\w+$", name):
        return None
    if name.startswith("__"):
        return None

    # Skip if it's a type definition, not a variable
    if type_str in ("struct", "union", "enum", "typedef"):
        return None

    return None  # Skip variables for now, they need extern linkage handling


def _parse_params(params_str: str) -> List[Parameter]:
    """Parse C function parameter list into Flow Parameters."""
    if not params_str or params_str.strip() == "void":
        return []

    if params_str.strip() == "...":
        return []

    params = []
    parts = _split_params(params_str)
    for part in parts:
        part = part.strip()
        if part == "...":
            continue
        if not part:
            continue

        # Handle function pointer parameters: ret (*name)(args)
        # or ret (*)(args) (anonymous)
        m = re.match(r"^(.+?)\s*\(\s*\*\s*(\w*)\s*\)\s*\((.*)\)$", part)
        if m:
            name = m.group(2) or f"_arg{len(params)}"
            params.append(Parameter(name, ParsedType("ptr<void>")))
            continue

        # Parse: type name
        tokens = part.split()
        if len(tokens) < 2:
            # Just a type, no name
            flow_type = _c_type_to_flow(part)
            params.append(Parameter(f"_arg{len(params)}", ParsedType(flow_type)))
            continue

        name = tokens[-1]
        type_str = " ".join(tokens[:-1])

        # Handle array parameters: type name[N] -> ptr<type>
        if "[" in name:
            bracket_pos = name.find("[")
            name = name[:bracket_pos]
            type_str += " *"

        # Handle pointer parameters where name has * attached: int *name
        if name.startswith("*"):
            star_count = 0
            while name.startswith("*"):
                star_count += 1
                name = name[1:]
            type_str += " " + "*" * star_count

        if not re.match(r"^\w+$", name):
            name = f"_arg{len(params)}"

        flow_type = _c_type_to_flow(type_str)
        params.append(Parameter(name, ParsedType(flow_type)))

    return params


def _split_params(params_str: str) -> List[str]:
    """Split parameter string by commas, respecting parentheses and brackets."""
    parts = []
    depth = 0
    start = 0
    for i, ch in enumerate(params_str):
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        elif ch == "," and depth == 0:
            parts.append(params_str[start:i])
            start = i + 1
    parts.append(params_str[start:])
    return [p.strip() for p in parts if p.strip()]


def resolve_c_imports(declarations: List, source_dir: str) -> List:
    """Process CImportDecl objects in declarations, replacing them with
    generated extern declarations."""
    from .parser import CImportDecl, CIncludeDecl

    result = []
    for decl in declarations:
        if isinstance(decl, CImportDecl):
            # Also emit a #include for the header
            result.append(CIncludeDecl(header=decl.header))
            # Parse the header
            include_dirs = [source_dir, "/usr/include", "/usr/local/include"]
            parsed = parse_c_header(decl.header, include_dirs)
            # Mark every parsed declaration as c_import so the C generator
            # emits none of them: the #include above already provides the
            # real ones, and re-emitting collides with it. Marking only
            # FunctionDecl left types behind, so a header with an anonymous
            # struct typedef (glibc's lldiv_t, for one) produced a second
            # `typedef struct lldiv_t lldiv_t;` and clang rejected the file:
            #   error: typedef redefinition with different types
            # The type checker still sees these declarations; only C output
            # is suppressed.
            for p in parsed:
                # Skip dangerous FFI functions imported from system headers.
                # The user didn't declare these; they came in via @cImport
                # parsing. Adding them triggers the dangerous-FFI check in
                # the type checker, which requires @unsafe extern. The
                # #include already provides the prototype, so dropping them
                # is safe.
                if isinstance(p, FunctionDecl) and p.name in _DANGEROUS_IMPORT_NAMES:
                    continue
                p.is_c_import = True
                result.append(p)
        else:
            result.append(decl)
    return result
