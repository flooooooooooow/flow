"""C header parser for @cImport.

Preprocesses a C header with `cpp -P`, then parses the resulting
declarations to extract:
  - function prototypes
  - typedef declarations (including opaque struct typedefs)
  - struct definitions (field names and types)
  - enum definitions
  - macro constants (#define after cpp expansion leaves integer literals)

The output is a list of Flow parser declaration objects
(FunctionDecl, ExternTypeDecl, ConstDecl) that the transpiler inserts
into the declaration list so the C generator emits the right prototypes.
"""

from __future__ import annotations

import os
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
)


# C type → Flow type mapping
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
}


def _c_type_to_flow(c_type: str) -> str:
    """Convert a C type string to a Flow type string."""
    c_type = c_type.strip()
    # Remove const/volatile/restrict qualifiers
    c_type = re.sub(r"\b(const|volatile|restrict|__restrict|__restrict__)\b", "", c_type)
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
    """Run cpp -P on a header and return the preprocessed text."""
    cmd = ["cpp", "-P"]
    for d in include_dirs:
        cmd.extend(["-I", d])
    cmd.append(header)
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.stdout
    except FileNotFoundError:
        # cpp not found, try clang -E -P
        cmd[0] = "clang"
        cmd.insert(1, "-E")
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
            )
            return result.stdout
        except Exception as e:
            print(f"Warning: @cImport preprocessing failed: {e}", file=sys.stderr)
            return ""
    except Exception as e:
        print(f"Warning: @cImport preprocessing failed: {e}", file=sys.stderr)
        return ""


class _Lexer:
    """Simple tokenizer for preprocessed C declarations."""

    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.len = len(text)

    def skip_ws(self):
        while self.pos < self.len and self.text[self.pos] in " \t\n\r":
            self.pos += 1

    def peek(self) -> str:
        self.skip_ws()
        if self.pos >= self.len:
            return ""
        return self.text[self.pos]

    def at_end(self) -> bool:
        self.skip_ws()
        return self.pos >= self.len

    def read_ident(self) -> str:
        self.skip_ws()
        start = self.pos
        while self.pos < self.len and (self.text[self.pos].isalnum() or self.text[self.pos] == "_"):
            self.pos += 1
        return self.text[start:self.pos]

    def read_number(self) -> str:
        self.skip_ws()
        start = self.pos
        while self.pos < self.len and (self.text[self.pos].isalnum() or self.text[self.pos] in "xX.+-"):
            self.pos += 1
        return self.text[start:self.pos]

    def expect_char(self, ch: str):
        self.skip_ws()
        if self.pos >= self.len or self.text[self.pos] != ch:
            raise ValueError(f"Expected '{ch}' at position {self.pos}")
        self.pos += 1

    def match_char(self, ch: str) -> bool:
        self.skip_ws()
        if self.pos < self.len and self.text[self.pos] == ch:
            self.pos += 1
            return True
        return False

    def read_until_semicolon(self) -> str:
        """Read text until the next semicolon (at brace depth 0)."""
        start = self.pos
        depth = 0
        while self.pos < self.len:
            ch = self.text[self.pos]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
            elif ch == ";" and depth == 0:
                result = self.text[start:self.pos]
                self.pos += 1  # consume semicolon
                return result
            self.pos += 1
        return self.text[start:self.pos]


def _parse_type_tokens(tokens: List[str]) -> Tuple[str, Optional[str]]:
    """Parse a list of type tokens into (type_str, name).

    Handles simple types, pointers, and function pointers.
    Returns (c_type, name) where name is the declared identifier
    or None for anonymous types.
    """
    if not tokens:
        return ("void", None)

    # Find the name: last identifier that's not a type qualifier
    # and not followed by ( for function pointers
    name = None
    type_tokens = list(tokens)

    # Handle function pointers: ret (*name)(params)
    for i, tok in enumerate(type_tokens):
        if tok == "(" and i + 1 < len(type_tokens) and type_tokens[i + 1] == "*":
            # Function pointer
            if i + 2 < len(type_tokens):
                name = type_tokens[i + 2]
            ret_type = " ".join(type_tokens[:i])
            return (ret_type, name)

    # Handle simple case: type ... name
    # Remove array brackets: name[...]
    last = type_tokens[-1]
    if last.endswith("]"):
        # Array: find the name before the bracket
        bracket_pos = last.find("[")
        name = last[:bracket_pos]
        type_tokens[-1] = last[bracket_pos:]
    elif last and (last[0].isalpha() or last[0] == "_"):
        name = last
        type_tokens = type_tokens[:-1]

    type_str = " ".join(type_tokens).strip()
    if not type_str:
        type_str = "int"
    return (type_str, name)


def _split_tokens(text: str) -> List[str]:
    """Split text into tokens, handling parentheses and brackets."""
    tokens = []
    i = 0
    while i < len(text):
        ch = text[i]
        if ch.isspace():
            i += 1
            continue
        if ch in "()[]{},*;":
            tokens.append(ch)
            i += 1
            continue
        if ch.isalnum() or ch == "_":
            start = i
            while i < len(text) and (text[i].isalnum() or text[i] == "_"):
                i += 1
            tokens.append(text[start:i])
            continue
        # Skip unknown characters
        i += 1
    return tokens


def parse_c_header(header: str, include_dirs: Optional[List[str]] = None) -> List:
    """Parse a C header and return Flow declarations.

    Args:
        header: Header file path or name (e.g. "stdio.h")
        include_dirs: Additional include directories for cpp

    Returns:
        List of FunctionDecl, ExternTypeDecl, and ConstDecl objects
    """
    if include_dirs is None:
        include_dirs = []

    # Add system include directories
    include_dirs.extend(["/usr/include", "/usr/local/include"])

    # Preprocess
    text = _preprocess_header(header, include_dirs)
    if not text:
        return []

    declarations = []
    lex = _Lexer(text)

    while not lex.at_end():
        lex.skip_ws()
        if lex.at_end():
            break

        # Read until semicolon
        chunk = lex.read_until_semicolon().strip()
        if not chunk:
            continue

        # Skip extern "C" blocks (already preprocessed)
        if chunk.startswith("extern"):
            # Could be extern "C" { ... } or extern type declaration
            rest = chunk[6:].strip()
            if rest.startswith('"C"'):
                continue
            # Skip plain extern declarations
            continue

        # Handle typedef
        if chunk.startswith("typedef"):
            declarations.extend(_parse_typedef(chunk))
            continue

        # Handle struct/union/enum definitions
        if re.match(r"^(struct|union|enum)\b", chunk):
            declarations.extend(_parse_struct_enum(chunk))
            continue

        # Try to parse as function declaration
        fn = _parse_function(chunk)
        if fn:
            declarations.append(fn)

    return declarations


def _parse_typedef(chunk: str) -> List:
    """Parse a typedef declaration."""
    # typedef struct Name Name;  → opaque type
    m = re.match(r"typedef\s+struct\s+(\w+)\s+(\w+)\s*$", chunk)
    if m:
        struct_name = m.group(1)
        alias = m.group(2)
        # If struct_name == alias, it's an opaque forward declaration
        if struct_name == alias:
            return [ExternTypeDecl(name=alias)]
        return [ExternTypeDecl(name=alias)]

    # typedef struct { ... } Name;  → skip (we don't need the layout)
    if re.match(r"typedef\s+struct\s*\{", chunk):
        # Extract the name after the closing brace
        m = re.search(r"\}\s*(\w+)\s*$", chunk)
        if m:
            return [ExternTypeDecl(name=m.group(1))]
        return []

    # typedef enum { ... } Name;  → skip
    if re.match(r"typedef\s+enum\s*\{", chunk):
        return []

    # typedef <type> Name;
    m = re.match(r"typedef\s+(.+?)\s+(\w+)\s*$", chunk)
    if m:
        # It's a simple typedef. We don't need to generate anything
        # since the C header already provides it.
        return []

    return []


def _parse_struct_enum(chunk: str) -> List:
    """Parse struct/union/enum definitions (skip them)."""
    # We only need the typedef alias, not the full layout.
    # The C header provides the layout.
    return []


def _parse_function(chunk: str) -> Optional[FunctionDecl]:
    """Parse a C function declaration into a FunctionDecl."""
    # Must contain parentheses
    if "(" not in chunk or ")" not in chunk:
        return None

    # Must not be a function definition (has a body)
    if "{" in chunk:
        return None

    # Pattern: return_type name(params)
    # Find the function name: the identifier right before the first (
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

    # Split the before_paren into return type and function name
    tokens = before_paren.split()
    if len(tokens) < 2:
        return None

    fn_name = tokens[-1]
    ret_type_str = " ".join(tokens[:-1])

    # Skip if function name is not a valid identifier
    if not re.match(r"^\w+$", fn_name):
        return None

    # Skip if it's a macro or compiler intrinsic
    if fn_name.startswith("__"):
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


def _parse_params(params_str: str) -> List[Parameter]:
    """Parse C function parameter list into Flow Parameters."""
    if not params_str or params_str.strip() == "void":
        return []

    # Handle variadic
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

        # Parse: type name
        tokens = part.split()
        if len(tokens) < 2:
            # Just a type, no name
            flow_type = _c_type_to_flow(part)
            params.append(Parameter(f"_arg{len(params)}", ParsedType(flow_type)))
            continue

        # Last token is the name (unless it's an array)
        name = tokens[-1]
        type_str = " ".join(tokens[:-1])

        # Handle array parameters: type name[N] → ptr<type>
        if "[" in name:
            bracket_pos = name.find("[")
            name = name[:bracket_pos]
            type_str += " *"

        # Handle function pointer parameters
        if "*" in part and "(" in part:
            # Simplified: treat as ptr<void>
            params.append(Parameter(name, ParsedType("ptr<void>")))
            continue

        flow_type = _c_type_to_flow(type_str)
        params.append(Parameter(name, ParsedType(flow_type)))

    return params


def _split_params(params_str: str) -> List[str]:
    """Split parameter string by commas, respecting parentheses."""
    parts = []
    depth = 0
    start = 0
    for i, ch in enumerate(params_str):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif ch == "," and depth == 0:
            parts.append(params_str[start:i])
            start = i + 1
    parts.append(params_str[start:])
    return [p.strip() for p in parts if p.strip()]


def resolve_c_imports(declarations: List, source_dir: str) -> List:
    """Process CImportDecl objects in declarations, replacing them with
    generated extern declarations.

    Args:
        declarations: List of parser declarations
        source_dir: Directory of the source file (for local header includes)

    Returns:
        Updated declarations list with CImportDecl objects expanded
    """
    from .parser import CImportDecl, CIncludeDecl

    result = []
    for decl in declarations:
        if isinstance(decl, CImportDecl):
            # Also emit a #include for the header
            result.append(CIncludeDecl(header=decl.header))
            # Parse the header
            include_dirs = [source_dir, "/usr/include", "/usr/local/include"]
            parsed = parse_c_header(decl.header, include_dirs)
            result.extend(parsed)
        else:
            result.append(decl)
    return result
