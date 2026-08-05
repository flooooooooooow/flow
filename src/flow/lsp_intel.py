"""LSP intelligence helpers: imports, typed hover, field completion."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import unquote, urlparse

from .dynamics_dsl import expand_dynamics_dsl, has_dynamics_dsl
from .module_resolver import ModuleResolver
from .parser import (
    ConstDecl,
    EffectDecl,
    EnumDecl,
    ExportDecl,
    FunctionDecl,
    ImportDecl,
    Lexer,
    Parser,
    StructDecl,
    TraitDecl,
    TypeAliasDecl,
    DistinctTypeDecl,
)
from .type_checker import TypeChecker


def uri_to_path(uri: str) -> Optional[str]:
    if not uri:
        return None
    if uri.startswith('file://'):
        parsed = urlparse(uri)
        path = unquote(parsed.path)
        # Windows: /C:/... → C:/...
        if re.match(r'^/[A-Za-z]:/', path):
            path = path[1:]
        return path
    if uri.startswith('untitled:'):
        return None
    return uri if os.path.isfile(uri) else None


def path_to_uri(path: str) -> str:
    return Path(path).resolve().as_uri()


def parse_source(text: str) -> Optional[List[Any]]:
    try:
        src = text
        if has_dynamics_dsl(src):
            src = expand_dynamics_dsl(src)
        return Parser(Lexer(src), source=src).parse()
    except Exception:
        return None


def type_to_display(typ: Any) -> str:
    if typ is None:
        return 'unknown'
    return str(typ)


def symbol_info_from_decl(
    decl: Any, *, source_uri: str, doc: str = ''
) -> Optional[Dict[str, Any]]:
    """Build an LSP symbol dict from a top-level declaration."""
    if isinstance(decl, FunctionDecl):
        return {
            'kind': 'function',
            'params': [
                (p.name, getattr(p.type, 'name', 'unknown'))
                for p in decl.parameters
            ],
            'return': getattr(decl.return_type, 'name', 'void'),
            'line': 0,
            'column': 0,
            'doc': doc,
            'exported': bool(getattr(decl, 'is_exported', False)),
            'uri': source_uri,
            'imported': True,
        }
    if isinstance(decl, StructDecl):
        return {
            'kind': 'struct',
            'fields': [
                (f.name, getattr(f.type, 'name', 'unknown'))
                for f in decl.fields
            ],
            'line': 0,
            'column': 0,
            'doc': doc,
            'exported': bool(getattr(decl, 'is_exported', False)),
            'uri': source_uri,
            'imported': True,
        }
    if isinstance(decl, EnumDecl):
        return {
            'kind': 'enum',
            'variants': [v.name for v in decl.variants],
            'line': 0,
            'column': 0,
            'doc': doc,
            'uri': source_uri,
            'imported': True,
        }
    if isinstance(decl, TraitDecl):
        return {
            'kind': 'trait',
            'methods': [m.name for m in decl.methods],
            'line': 0,
            'column': 0,
            'doc': doc,
            'uri': source_uri,
            'imported': True,
        }
    if isinstance(decl, ConstDecl):
        return {
            'kind': 'const',
            'type': getattr(decl.type, 'name', 'unknown'),
            'line': 0,
            'column': 0,
            'doc': doc,
            'uri': source_uri,
            'imported': True,
        }
    if isinstance(decl, EffectDecl):
        return {
            'kind': 'effect',
            'operations': [op.name for op in decl.operations],
            'line': 0,
            'column': 0,
            'doc': doc,
            'uri': source_uri,
            'imported': True,
        }
    if isinstance(decl, (TypeAliasDecl, DistinctTypeDecl)):
        return {
            'kind': 'type',
            'type': getattr(getattr(decl, 'base_type', None), 'name', 'unknown'),
            'line': 0,
            'column': 0,
            'doc': doc,
            'uri': source_uri,
            'imported': True,
        }
    return None


def _decl_line_in_text(text: str, keyword: str, name: str) -> int:
    pat = re.compile(
        rf'^\s*(?:export\s+)?{re.escape(keyword)}\s+{re.escape(name)}\b'
    )
    for i, row in enumerate(text.split('\n')):
        if pat.search(row):
            return i
    # looser
    pat2 = re.compile(rf'\b{re.escape(keyword)}\s+{re.escape(name)}\b')
    for i, row in enumerate(text.split('\n')):
        if pat2.search(row):
            return i
    return 0


def refine_import_symbol_location(
    info: Dict[str, Any], dep_text: str, name: str
) -> None:
    kind = info.get('kind')
    keyword = {
        'function': 'function',
        'struct': 'struct',
        'enum': 'enum',
        'trait': 'trait',
        'const': 'const',
        'effect': 'effect',
        'type': 'type',
    }.get(kind or '', 'function')
    line = _decl_line_in_text(dep_text, keyword, name)
    info['line'] = line
    row = dep_text.split('\n')[line] if dep_text.split('\n') else ''
    col = row.find(name)
    if col < 0:
        col = 0
    info['column'] = col
    info['end_column'] = col + len(name)
    info['end_line'] = line


def index_imports(
    file_path: str, declarations: List[Any]
) -> Tuple[Dict[str, Dict[str, Any]], List[Any]]:
    """Depth-1 import index.

    Returns (name -> symbol_info, imported_decls for typechecking).
    Does not recurse into dependencies' imports.
    """
    symbols: Dict[str, Dict[str, Any]] = {}
    imported_decls: List[Any] = []
    if not file_path or not os.path.isfile(file_path):
        return symbols, imported_decls

    resolver = ModuleResolver(file_path)
    base = os.path.dirname(file_path)
    seen_files: set = set()

    for imp in declarations:
        if not isinstance(imp, ImportDecl):
            continue
        try:
            dep_path, wanted = resolver._resolve_import(imp, base)
        except Exception:
            continue
        if not dep_path or not os.path.isfile(dep_path):
            continue
        if dep_path in seen_files:
            continue
        seen_files.add(dep_path)

        try:
            dep_text = Path(dep_path).read_text(encoding='utf-8')
        except OSError:
            continue
        dep_decls = parse_source(dep_text)
        if dep_decls is None:
            continue

        export_names = set()
        for d in dep_decls:
            if isinstance(d, ExportDecl):
                export_names.update(d.symbols)

        source_uri = path_to_uri(dep_path)
        for d in dep_decls:
            if isinstance(d, (ImportDecl, ExportDecl)):
                continue
            name = getattr(d, 'name', None)
            if not name and hasattr(d, 'claim_path'):
                name = d.claim_path
            if not name:
                continue
            exported = bool(getattr(d, 'is_exported', False)) or name in export_names
            if not exported:
                continue
            if wanted is not None and name not in wanted:
                continue
            info = symbol_info_from_decl(d, source_uri=source_uri)
            if not info:
                continue
            refine_import_symbol_location(info, dep_text, name)
            symbols[name] = info
            # Mark exported for typechecker collect
            try:
                d.is_exported = True
            except Exception:
                pass
            imported_decls.append(d)

    return symbols, imported_decls


def run_typecheck(
    local_declarations: List[Any], imported_declarations: List[Any]
) -> Any:
    """Typecheck imported decls + locals (imports stripped)."""
    locals_only = [
        d for d in local_declarations
        if not isinstance(d, (ImportDecl, ExportDecl))
    ]
    checker = TypeChecker()
    return checker.check(list(imported_declarations) + locals_only)


def enrich_bindings_with_types(
    bindings: List[Dict[str, Any]], typed_locals: List[Dict[str, Any]]
) -> None:
    """Update parse-time bindings with checker-inferred type strings when possible."""
    # Match by (container, name) in order for duplicates.
    pool: Dict[Tuple[str, str], List[str]] = {}
    for t in typed_locals:
        key = (t.get('container') or '', t.get('name') or '')
        pool.setdefault(key, []).append(t.get('type') or 'unknown')
    cursors: Dict[Tuple[str, str], int] = {}
    for b in bindings:
        key = (b.get('container') or '', b.get('name') or '')
        types = pool.get(key) or []
        idx = cursors.get(key, 0)
        if idx < len(types):
            b['type'] = types[idx]
            b['typed'] = True
            cursors[key] = idx + 1


def receiver_before_dot(text: str, line: int, character: int) -> Optional[str]:
    """If completion is after `ident.`, return ident."""
    lines = text.split('\n')
    if line < 0 or line >= len(lines):
        return None
    row = lines[line][:character]
    # Allow `p.` or `p.x` mid-field
    m = re.search(r'([A-Za-z_][A-Za-z0-9_]*)\s*\.\s*([A-Za-z_][A-Za-z0-9_]*)?$', row)
    if not m:
        return None
    return m.group(1)


def field_access_at(
    text: str, line: int, character: int
) -> Optional[Tuple[str, str]]:
    """If cursor is on `recv.field`, return (recv, field)."""
    lines = text.split('\n')
    if line < 0 or line >= len(lines):
        return None
    row = lines[line]
    if character > len(row):
        character = len(row)
    # Expand to identifier under cursor
    start = character
    while start > 0 and (row[start - 1].isalnum() or row[start - 1] == '_'):
        start -= 1
    end = character
    while end < len(row) and (row[end].isalnum() or row[end] == '_'):
        end += 1
    field = row[start:end]
    if not field:
        return None
    before = row[:start].rstrip()
    if not before.endswith('.'):
        return None
    before = before[:-1].rstrip()
    m = re.search(r'([A-Za-z_][A-Za-z0-9_]*)$', before)
    if not m:
        return None
    return m.group(1), field


def resolve_type_name(
    type_str: str,
    symbol_types: Dict[str, str],
    struct_fields: Dict[str, List[Tuple[str, str]]],
) -> Optional[str]:
    """Normalize a type string to a struct name present in struct_fields."""
    if not type_str:
        return None
    s = type_str.strip()
    # ptr<Point> / Point
    m = re.match(r'ptr\s*<\s*([A-Za-z_][A-Za-z0-9_]*)\s*>', s)
    if m:
        s = m.group(1)
    m = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)', s)
    if not m:
        return None
    name = m.group(1)
    if name in struct_fields:
        return name
    # Follow type aliases stored as symbol_types values? skip for now
    return name if name in struct_fields else None


def lookup_receiver_type(
    recv: str,
    line: int,
    bindings: List[Dict[str, Any]],
    global_types: Dict[str, str],
) -> Optional[str]:
    best = None
    for b in bindings:
        if b.get('name') != recv:
            continue
        if int(b.get('line', 0)) <= line:
            if best is None or int(b['line']) >= int(best['line']):
                best = b
    if best:
        return best.get('type')
    return global_types.get(recv)
