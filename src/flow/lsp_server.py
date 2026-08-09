#!/usr/bin/env python3
"""
FLOW Language Server Protocol (LSP) Implementation
Provides IntelliSense features: completion, hover, diagnostics, go-to-definition
"""

import json
import os
import sys
import re
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from .parser import (
    Lexer, Parser, FunctionDecl, StructDecl, EnumDecl, TraitDecl,
    TheoremDecl, ConstDecl, EffectDecl, TypeAliasDecl, DistinctTypeDecl,
    VarDecl, Block, IfStatement, WhileStatement, ForStatement,
    CapabilityDecl, FlowSyntaxError, TokenType, Type,
)
from .type_checker import TypeChecker
from .lsp_dynamics import dynamics_completion_items, dynamics_hover
from .lsp_ordering import ordering_completion_items, ordering_hover
from .lsp_syntax import syntax_hover, syntax_token_at_position, MULTI_CHAR_OPS
from . import lsp_intel

# LSP Message Types
@dataclass
class Position:
    line: int
    character: int

@dataclass
class Range:
    start: Position
    end: Position

@dataclass
class Location:
    uri: str
    range: Range

@dataclass
class Diagnostic:
    range: Range
    message: str
    severity: int = 1  # 1=Error, 2=Warning, 3=Info, 4=Hint

@dataclass
class CompletionItem:
    label: str
    kind: int  # 1=Text, 2=Method, 3=Function, 6=Variable, 7=Class, 22=Struct
    detail: Optional[str] = None
    documentation: Optional[str] = None
    insertText: Optional[str] = None

@dataclass
class Hover:
    contents: str
    range: Optional[Range] = None


class LspError(Exception):
    """Raised by a request handler to produce a JSON-RPC error response."""

    # LSP 3.17 error code: the request was valid but cannot be fulfilled.
    REQUEST_FAILED = -32803

    def __init__(self, message: str, code: int = REQUEST_FAILED):
        super().__init__(message)
        self.code = code
        self.message = message


class FlowLanguageServer:
    """LSP server for FLOW language."""
    
    DEBOUNCE_SECONDS = 0.2  # delay before re-analyzing on keystrokes

    def __init__(self):
        self.documents: Dict[str, str] = {}  # uri -> content
        self.symbols: Dict[str, Dict[str, Any]] = {}  # uri -> {name: symbol_info}
        # Locals/params/for-vars ordered by declaration line (for hover/def).
        self.bindings: Dict[str, List[Dict[str, Any]]] = {}
        # Depth-1 imported exports: uri -> {name: symbol_info with source uri}
        self.import_symbols: Dict[str, Dict[str, Any]] = {}
        # Per-document type intel from TypeChecker
        # { global_types: {name: type_str}, struct_fields: {Struct: [(f,t)]},
        #   errors: [str], symbol_kinds: {name: kind} }
        self.type_cache: Dict[str, Dict[str, Any]] = {}
        self.stdlib_symbols: Dict[str, Dict[str, Any]] = {}  # name -> symbol_info
        self._stdlib_indexed = False
        self.running = True
        self._write_lock = threading.Lock()  # serializes stdout writes
        self._debounce_timers: Dict[str, threading.Timer] = {}  # uri -> pending analysis
        
        # Built-in types
        self.builtin_types = [
            'i8', 'i16', 'i32', 'i64', 'i128',
            'u8', 'u16', 'u32', 'u64', 'u128',
            'f32', 'f64', 'bool', 'void', 'string',
            'array', 'ptr', 'vec', 'bit',
        ]
        
        # Built-in functions
        self.builtin_functions = {
            'print': {'params': ['value: any'], 'return': 'void',
                      'doc': 'Print a value to stdout.'},
            'printf': {'params': ['format: string', '...'], 'return': 'void',
                       'doc': 'Print formatted output (C-style format string).'},
            'sqrt': {'params': ['x: f64'], 'return': 'f64',
                     'doc': 'Square root of x (√x).'},
            'sin': {'params': ['x: f64'], 'return': 'f64',
                    'doc': 'Sine of x (radians).'},
            'cos': {'params': ['x: f64'], 'return': 'f64',
                    'doc': 'Cosine of x (radians).'},
            'tan': {'params': ['x: f64'], 'return': 'f64',
                    'doc': 'Tangent of x (radians).'},
            'asin': {'params': ['x: f64'], 'return': 'f64',
                     'doc': 'Arcsine of x; result in radians.'},
            'acos': {'params': ['x: f64'], 'return': 'f64',
                     'doc': 'Arccosine of x; result in radians.'},
            'atan': {'params': ['x: f64'], 'return': 'f64',
                     'doc': 'Arctangent of x; result in radians.'},
            'atan2': {'params': ['y: f64', 'x: f64'], 'return': 'f64',
                      'doc': 'Arctangent of y/x using both signs for the quadrant.'},
            'exp': {'params': ['x: f64'], 'return': 'f64',
                    'doc': 'Exponential e^x.'},
            'log': {'params': ['x: f64'], 'return': 'f64',
                    'doc': 'Natural logarithm (ln x).'},
            'log10': {'params': ['x: f64'], 'return': 'f64',
                      'doc': 'Base-10 logarithm of x.'},
            'log2': {'params': ['x: f64'], 'return': 'f64',
                     'doc': 'Base-2 logarithm of x.'},
            'pow': {'params': ['x: f64', 'y: f64'], 'return': 'f64',
                    'doc': 'Raise x to the power y (x^y).'},
            'abs': {'params': ['x: i32'], 'return': 'i32',
                    'doc': 'Absolute value |x| for integers.'},
            'fabs': {'params': ['x: f64'], 'return': 'f64',
                     'doc': 'Absolute value |x| for floating-point.'},
            'floor': {'params': ['x: f64'], 'return': 'f64',
                      'doc': 'Greatest integer ≤ x (as f64).'},
            'ceil': {'params': ['x: f64'], 'return': 'f64',
                     'doc': 'Smallest integer ≥ x (as f64).'},
            'round': {'params': ['x: f64'], 'return': 'f64',
                      'doc': 'Nearest integer to x (as f64).'},
            'trunc': {'params': ['x: f64'], 'return': 'f64',
                      'doc': 'Truncate fractional part toward zero.'},
            'fmod': {'params': ['x: f64', 'y: f64'], 'return': 'f64',
                     'doc': 'Floating-point remainder of x/y.'},
            'min': {'params': ['a: f64', 'b: f64'], 'return': 'f64',
                    'doc': 'Return the smaller of a and b.'},
            'max': {'params': ['a: f64', 'b: f64'], 'return': 'f64',
                    'doc': 'Return the larger of a and b.'},
            'sinh': {'params': ['x: f64'], 'return': 'f64',
                     'doc': 'Hyperbolic sine of x.'},
            'cosh': {'params': ['x: f64'], 'return': 'f64',
                     'doc': 'Hyperbolic cosine of x.'},
            'tanh': {'params': ['x: f64'], 'return': 'f64',
                     'doc': 'Hyperbolic tangent of x.'},
            'hypot': {'params': ['x: f64', 'y: f64'], 'return': 'f64',
                      'doc': 'Euclidean norm √(x² + y²) without overflow.'},
        }
        
        # Keywords (core language — dynamics DSL lives in lsp_dynamics snippets)
        self.keywords = [
            'function', 'let', 'mut', 'return', 'if', 'else', 'elif', 'while', 'for',
            'break', 'continue', 'parallel', 'in', 'step', 'to', 'struct', 'enum', 'trait',
            'impl', 'effect', 'capability', 'handle', 'with', 'match', 'default',
            'import', 'export', 'extern', 'const', 'module', 'test', 'self',
            'array', 'ptr', 'vec', 'true', 'false', 'inline',
            'theorem', 'assume', 'therefore', 'shader', 'unit',
            'type', 'as', 'defer', 'try', 'or', 'and', 'not',
        ]

        # Reserved words for rename validation: mirrors the parser's
        # Lexer.keyword_map exactly (keywords, literals true/false/null,
        # builtin type names, and contextual keywords like ptr/array).
        self.reserved_names = frozenset(Lexer('').keyword_map.keys())

    IDENTIFIER_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')

    def _is_valid_identifier(self, name: str) -> bool:
        """True if name is a lexically valid Flow identifier."""
        return bool(self.IDENTIFIER_RE.match(name))

    def handle_message(self, message: dict) -> Optional[dict]:
        """Handle an incoming LSP message."""
        method = message.get('method', '')
        params = message.get('params', {})
        msg_id = message.get('id')
        
        result = None

        try:
            result = self._dispatch(method, params)
        except LspError as e:
            if msg_id is not None:
                return {'jsonrpc': '2.0', 'id': msg_id,
                        'error': {'code': e.code, 'message': e.message}}
            return None

        if msg_id is not None:
            return {'jsonrpc': '2.0', 'id': msg_id, 'result': result}
        return None

    def _dispatch(self, method: str, params: dict) -> Any:
        """Route a request/notification to its handler; returns the result."""
        result = None

        if method == 'initialize':
            result = self._handle_initialize(params)
        elif method == 'initialized':
            pass  # No response needed
        elif method == 'shutdown':
            self.running = False
            result = None
        elif method == 'exit':
            sys.exit(0)
        elif method == 'textDocument/didOpen':
            self._handle_did_open(params)
        elif method == 'textDocument/didChange':
            self._handle_did_change(params)
        elif method == 'textDocument/didClose':
            self._handle_did_close(params)
        elif method == 'textDocument/completion':
            result = self._handle_completion(params)
        elif method == 'textDocument/hover':
            result = self._handle_hover(params)
        elif method == 'textDocument/definition':
            result = self._handle_definition(params)
        elif method == 'textDocument/documentSymbol':
            result = self._handle_document_symbol(params)
        elif method == 'textDocument/references':
            result = self._handle_references(params)
        elif method == 'textDocument/prepareRename':
            result = self._handle_prepare_rename(params)
        elif method == 'textDocument/rename':
            result = self._handle_rename(params)
        elif method == 'textDocument/formatting':
            result = self._handle_formatting(params)
        elif method == 'textDocument/rangeFormatting':
            result = self._handle_range_formatting(params)
        elif method == 'textDocument/documentHighlight':
            result = self._handle_document_highlight(params)

        return result

    def _handle_initialize(self, params: dict) -> dict:
        """Handle initialize request."""
        return {
            'capabilities': {
                'textDocumentSync': {
                    'openClose': True,
                    'change': 1,  # Full sync
                },
                'completionProvider': {
                    'triggerCharacters': ['.', ':', '<'],
                    'resolveProvider': False,
                },
                'hoverProvider': True,
                'definitionProvider': True,
                'documentSymbolProvider': True,
                'referencesProvider': True,
                'renameProvider': {'prepareProvider': True},
                'documentFormattingProvider': True,
                'documentRangeFormattingProvider': True,
                'documentHighlightProvider': True,
            },
            'serverInfo': {
                'name': 'flow-lsp',
                'version': '0.2.0',
            }
        }
    
    def _handle_did_open(self, params: dict):
        """Handle textDocument/didOpen."""
        uri = params['textDocument']['uri']
        text = params['textDocument']['text']
        self.documents[uri] = text
        # Analyze immediately on open (no debounce needed for a single event)
        self._analyze_document(uri)
        self._publish_diagnostics(uri)

    def _handle_did_change(self, params: dict):
        """Handle textDocument/didChange."""
        uri = params['textDocument']['uri']
        changes = params.get('contentChanges', [])
        if changes:
            self.documents[uri] = changes[0]['text']
            # Debounce: rapid keystrokes cancel the previous pending analysis
            # so we only parse + type-check once typing pauses.
            timer = self._debounce_timers.pop(uri, None)
            if timer is not None:
                timer.cancel()
            timer = threading.Timer(
                self.DEBOUNCE_SECONDS, self._analyze_and_publish, args=(uri,)
            )
            timer.daemon = True
            self._debounce_timers[uri] = timer
            timer.start()

    def _handle_did_close(self, params: dict):
        """Handle textDocument/didClose."""
        uri = params['textDocument']['uri']
        timer = self._debounce_timers.pop(uri, None)
        if timer is not None:
            timer.cancel()
        self.documents.pop(uri, None)
        self.symbols.pop(uri, None)
        self.bindings.pop(uri, None)
        self.import_symbols.pop(uri, None)
        self.type_cache.pop(uri, None)
        # Clear any diagnostics still shown for the closed document
        self._send_notification('textDocument/publishDiagnostics',
                                {'uri': uri, 'diagnostics': []})

    def _analyze_and_publish(self, uri: str):
        """Debounced worker: re-analyze a document and publish diagnostics."""
        self._debounce_timers.pop(uri, None)
        if uri not in self.documents:
            return  # closed while the timer was pending
        try:
            self._analyze_document(uri)
            self._publish_diagnostics(uri)
        except Exception as e:
            sys.stderr.write(f"LSP analyze error: {e}\n")
            sys.stderr.flush()
    
    def _analyze_document(self, uri: str):
        """Analyze a document: symbols, locals, imports, and type intel."""
        text = self.documents.get(uri, '')
        symbols, bindings, declarations = self._extract_symbols_and_bindings(text)
        file_path = lsp_intel.uri_to_path(uri)

        import_syms: Dict[str, Dict[str, Any]] = {}
        imported_decls: List[Any] = []
        if declarations is not None and file_path:
            try:
                import_syms, imported_decls = lsp_intel.index_imports(
                    file_path, declarations
                )
            except Exception as e:
                sys.stderr.write(f"LSP import index error: {e}\n")
                sys.stderr.flush()

        # Merge imports into the document symbol map (local names win).
        merged = dict(import_syms)
        merged.update(symbols)
        self.symbols[uri] = merged
        self.bindings[uri] = bindings
        self.import_symbols[uri] = import_syms

        # Typecheck with imported decls so package symbols resolve.
        type_info: Dict[str, Any] = {
            'global_types': {},
            'symbol_kinds': {},
            'struct_fields': {},
            'errors': [],
        }
        if declarations is not None:
            try:
                result = lsp_intel.run_typecheck(declarations, imported_decls)
                global_types = {}
                symbol_kinds = {}
                for name, sym in (result.symbol_table or {}).items():
                    global_types[name] = str(sym.type)
                    symbol_kinds[name] = sym.kind
                type_info['global_types'] = global_types
                type_info['symbol_kinds'] = symbol_kinds
                type_info['struct_fields'] = dict(result.struct_fields or {})
                type_info['errors'] = list(result.errors or [])
                # Prefer checker-inferred types on locals when available.
                lsp_intel.enrich_bindings_with_types(
                    self.bindings[uri], result.locals or []
                )
                # Also index local structs into struct_fields from symbols
                for name, info in merged.items():
                    if info.get('kind') == 'struct' and name not in type_info['struct_fields']:
                        type_info['struct_fields'][name] = list(
                            info.get('fields') or []
                        )
            except Exception as e:
                sys.stderr.write(f"LSP type intel error: {e}\n")
                sys.stderr.flush()
        # Fallback struct fields from parsed symbols even if typecheck fails
        if not type_info['struct_fields']:
            for name, info in merged.items():
                if info.get('kind') == 'struct':
                    type_info['struct_fields'][name] = list(
                        info.get('fields') or []
                    )
        self.type_cache[uri] = type_info

    def _extract_symbols_from_text(
        self, text: str, *, exported_only: bool = False
    ) -> Dict[str, Dict[str, Any]]:
        """Parse text and build a name -> symbol_info map with doc comments."""
        symbols, _bindings, _decls = self._extract_symbols_and_bindings(
            text, exported_only=exported_only
        )
        return symbols

    @staticmethod
    def _type_to_str(t: Optional[Type]) -> str:
        if t is None:
            return 'unknown'
        name = getattr(t, 'name', None) or 'unknown'
        if getattr(t, 'is_pointer', False):
            return f'ptr<{name}>'
        args = getattr(t, 'type_args', None)
        if args:
            inner = ', '.join(FlowLanguageServer._type_to_str(a) for a in args)
            return f'{name}<{inner}>'
        elem = getattr(t, 'element_type', None)
        if elem is not None and name in ('array', 'vec', 'ptr'):
            return f'{name}<{FlowLanguageServer._type_to_str(elem)}>'
        return name

    def _extract_symbols_and_bindings(
        self, text: str, *, exported_only: bool = False
    ) -> tuple:
        """Parse text → (top-level symbols, local/param bindings, declarations|None)."""
        symbols: Dict[str, Dict[str, Any]] = {}
        bindings: List[Dict[str, Any]] = []
        lines = text.split('\n')

        declarations = None
        src = text
        try:
            from .dynamics_dsl import has_dynamics_dsl, expand_dynamics_dsl
            from .field_dsl import has_field_dsl, expand_field_dsl
            if has_field_dsl(src):
                src = expand_field_dsl(src)
            if has_dynamics_dsl(src):
                src = expand_dynamics_dsl(src)
        except Exception:
            pass
        try:
            lexer = Lexer(src)
            parser = Parser(lexer, source=src)
            declarations = parser.parse()
        except Exception:
            # Mid-edit recovery: `return p.` → `return p._flow_incomplete`
            recovered = self._recover_incomplete_syntax(src)
            if recovered != src:
                try:
                    lexer = Lexer(recovered)
                    parser = Parser(lexer, source=recovered)
                    declarations = parser.parse()
                    src = recovered
                except Exception:
                    declarations = None
            if declarations is None:
                # Fallback: regex-scan exports so stdlib hover still works on
                # files the parser cannot fully load.
                return self._extract_symbols_regex(
                    text, exported_only=exported_only
                ), [], None

        for decl in declarations:
            if exported_only and not getattr(decl, 'is_exported', False):
                # Effects/aliases may not set is_exported; skip unless present.
                if not isinstance(decl, (EffectDecl,)):
                    continue

            if isinstance(decl, FunctionDecl):
                loc = decl.location
                # Prefer regex line of `function name` for doc attachment —
                # SourceLocation sometimes lands on the preceding `#` comment.
                decl_line = self._find_decl_line(lines, 'function', decl.name)
                if decl_line == 0 and loc is not None:
                    decl_line = loc.line
                # SourceLocation lines are 1-based in some paths; normalize.
                line0 = loc.line if loc else decl_line
                if loc is not None and loc.line > 0 and loc.line >= len(lines):
                    line0 = decl_line
                # Prefer 0-based decl_line from regex when available.
                if decl_line is not None:
                    line0 = decl_line
                symbols[decl.name] = {
                    'kind': 'function',
                    'params': [
                        (p.name, self._type_to_str(p.type)) for p in decl.parameters
                    ],
                    'return': self._type_to_str(decl.return_type),
                    'line': line0,
                    'column': loc.column if loc else 0,
                    'end_line': (loc.end_line if loc else line0),
                    'end_column': (
                        loc.end_column if loc else (0 + len(decl.name))
                    ),
                    'doc': self._doc_comment_above(lines, decl_line),
                    'exported': bool(getattr(decl, 'is_exported', False)),
                }
                if not exported_only:
                    self._collect_function_bindings(
                        decl, lines, decl_line, bindings
                    )
            elif isinstance(decl, StructDecl):
                loc = decl.location
                decl_line = loc.line if loc else self._find_decl_line(
                    lines, 'struct', decl.name
                )
                if isinstance(decl_line, int) and loc is not None and loc.line:
                    # Prefer regex 0-based line when find works
                    found = self._find_decl_line(lines, 'struct', decl.name)
                    if found:
                        decl_line = found
                symbols[decl.name] = {
                    'kind': 'struct',
                    'fields': [
                        (f.name, self._type_to_str(f.type)) for f in decl.fields
                    ],
                    'line': decl_line if isinstance(decl_line, int) else 0,
                    'column': loc.column if loc else 0,
                    'end_line': loc.end_line if loc else decl_line,
                    'end_column': loc.end_column if loc else 0,
                    'doc': self._doc_comment_above(
                        lines, decl_line if isinstance(decl_line, int) else 0
                    ),
                    'exported': bool(getattr(decl, 'is_exported', False)),
                }
            elif isinstance(decl, EnumDecl):
                decl_line = self._find_decl_line(lines, 'enum', decl.name)
                symbols[decl.name] = {
                    'kind': 'enum',
                    'variants': [v.name for v in decl.variants],
                    'line': decl_line,
                    'column': 0,
                    'doc': self._doc_comment_above(lines, decl_line),
                    'exported': bool(getattr(decl, 'is_exported', False)),
                }
            elif isinstance(decl, TraitDecl):
                decl_line = self._find_decl_line(lines, 'trait', decl.name)
                symbols[decl.name] = {
                    'kind': 'trait',
                    'methods': [m.name for m in decl.methods],
                    'line': decl_line,
                    'column': 0,
                    'doc': self._doc_comment_above(lines, decl_line),
                    'exported': bool(getattr(decl, 'is_exported', False)),
                }
            elif isinstance(decl, TheoremDecl):
                name = decl.claim_path
                decl_line = self._find_decl_line(lines, 'theorem', name)
                params = [
                    (p.name, self._type_to_str(p.type)) for p in decl.parameters
                ]
                symbols[name] = {
                    'kind': 'theorem',
                    'params': params,
                    'return': 'void',
                    'line': decl_line,
                    'column': 0,
                    'doc': self._doc_comment_above(lines, decl_line),
                    'exported': bool(getattr(decl, 'is_exported', False)),
                }
                if not exported_only:
                    self._collect_theorem_bindings(
                        decl, lines, decl_line, bindings
                    )
            elif isinstance(decl, ConstDecl):
                decl_line = self._find_decl_line(lines, 'const', decl.name)
                if exported_only and not getattr(decl, 'is_exported', False):
                    continue
                symbols[decl.name] = {
                    'kind': 'const',
                    'type': self._type_to_str(decl.type),
                    'line': decl_line,
                    'column': 0,
                    'doc': self._doc_comment_above(lines, decl_line),
                    'exported': bool(getattr(decl, 'is_exported', False)),
                }
            elif isinstance(decl, EffectDecl):
                decl_line = self._find_decl_line(lines, 'effect', decl.name)
                ops = [
                    f"{op.name}({', '.join(p.name for p in op.parameters)})"
                    for op in decl.operations
                ]
                symbols[decl.name] = {
                    'kind': 'effect',
                    'operations': ops,
                    'line': decl_line,
                    'column': 0,
                    'doc': self._doc_comment_above(lines, decl_line),
                    'exported': True,
                }
            elif isinstance(decl, (TypeAliasDecl, DistinctTypeDecl)):
                keyword = 'type'
                decl_line = self._find_decl_line(lines, keyword, decl.name)
                # Distinct/unit may use `distinct type` / `unit type`
                if decl_line == 0:
                    for i, row in enumerate(lines):
                        if re.search(
                            rf'\btype\s+{re.escape(decl.name)}\b', row
                        ):
                            decl_line = i
                            break
                if exported_only and not getattr(decl, 'is_exported', False):
                    continue
                base = self._type_to_str(getattr(decl, 'base_type', None))
                symbols[decl.name] = {
                    'kind': 'type',
                    'type': base,
                    'line': decl_line,
                    'column': 0,
                    'doc': self._doc_comment_above(lines, decl_line),
                    'exported': bool(getattr(decl, 'is_exported', False)),
                }
            elif isinstance(decl, CapabilityDecl):
                decl_line = self._find_decl_line(lines, 'capability', decl.name)
                symbols[decl.name] = {
                    'kind': 'capability',
                    'effects': list(decl.effects or []),
                    'line': decl_line,
                    'column': 0,
                    'doc': self._doc_comment_above(lines, decl_line),
                    'exported': True,
                }

        return symbols, bindings, declarations

    @staticmethod
    def _recover_incomplete_syntax(text: str) -> str:
        """Best-effort fixups so mid-edit buffers still parse for intel."""
        lines = text.split('\n')
        out = []
        for row in lines:
            # Trailing field/method access: `p.` or `p.  `
            if re.search(r'[A-Za-z_][A-Za-z0-9_]*\s*\.\s*$', row):
                out.append(row.rstrip() + '_flow_incomplete')
            else:
                out.append(row)
        return '\n'.join(out)

    def _collect_function_bindings(
        self,
        decl: FunctionDecl,
        lines: List[str],
        decl_line: int,
        bindings: List[Dict[str, Any]],
    ) -> None:
        """Index parameters and let/for bindings inside a function."""
        # Scan a window for `name:` param occurrences on the signature.
        sig_end = min(len(lines), decl_line + 40)
        for p in decl.parameters:
            line, col = decl_line, 0
            for i in range(decl_line, sig_end):
                m = re.search(
                    rf'\b{re.escape(p.name)}\s*:', lines[i]
                )
                if m:
                    line, col = i, m.start()
                    break
            bindings.append({
                'name': p.name,
                'kind': 'parameter',
                'type': self._type_to_str(p.type),
                'line': line,
                'column': col,
                'end_column': col + len(p.name),
                'mutable': False,
                'container': decl.name,
            })
        body = getattr(decl, 'body', None)
        if body is not None:
            self._walk_block_bindings(
                body, lines, bindings, container=decl.name, search_from=decl_line
            )

    def _collect_theorem_bindings(
        self,
        decl: TheoremDecl,
        lines: List[str],
        decl_line: int,
        bindings: List[Dict[str, Any]],
    ) -> None:
        for p in decl.parameters:
            line, col = decl_line, 0
            for i in range(decl_line, min(len(lines), decl_line + 20)):
                m = re.search(rf'\b{re.escape(p.name)}\s*:', lines[i])
                if m:
                    line, col = i, m.start()
                    break
            bindings.append({
                'name': p.name,
                'kind': 'parameter',
                'type': self._type_to_str(p.type),
                'line': line,
                'column': col,
                'end_column': col + len(p.name),
                'mutable': False,
                'container': decl.claim_path,
            })

    def _walk_block_bindings(
        self,
        block: Block,
        lines: List[str],
        bindings: List[Dict[str, Any]],
        *,
        container: str,
        search_from: int,
    ) -> int:
        """Walk statements; return next line hint for scanning."""
        cursor = search_from
        if block is None:
            return cursor
        for stmt in block.statements:
            if isinstance(stmt, VarDecl):
                line = self._find_let_line(lines, stmt.name, cursor)
                col = 0
                row = lines[line] if 0 <= line < len(lines) else ''
                m = re.search(rf'\b{re.escape(stmt.name)}\b', row)
                if m:
                    col = m.start()
                bindings.append({
                    'name': stmt.name,
                    'kind': 'variable',
                    'type': self._type_to_str(stmt.type),
                    'line': line,
                    'column': col,
                    'end_column': col + len(stmt.name),
                    'mutable': bool(stmt.is_mutable),
                    'container': container,
                })
                cursor = max(cursor, line)
            elif isinstance(stmt, ForStatement):
                line = self._find_for_var_line(lines, stmt.variable, cursor)
                col = 0
                row = lines[line] if 0 <= line < len(lines) else ''
                m = re.search(rf'\b{re.escape(stmt.variable)}\b', row)
                if m:
                    col = m.start()
                bindings.append({
                    'name': stmt.variable,
                    'kind': 'variable',
                    'type': 'i32',
                    'line': line,
                    'column': col,
                    'end_column': col + len(stmt.variable),
                    'mutable': False,
                    'container': container,
                    'detail': 'for-loop variable',
                })
                cursor = max(cursor, line)
                cursor = self._walk_block_bindings(
                    stmt.body, lines, bindings,
                    container=container, search_from=cursor,
                )
            elif isinstance(stmt, IfStatement):
                cursor = self._walk_block_bindings(
                    stmt.then_block, lines, bindings,
                    container=container, search_from=cursor,
                )
                for _cond, blk in stmt.elif_blocks or []:
                    cursor = self._walk_block_bindings(
                        blk, lines, bindings,
                        container=container, search_from=cursor,
                    )
                if stmt.else_block is not None:
                    cursor = self._walk_block_bindings(
                        stmt.else_block, lines, bindings,
                        container=container, search_from=cursor,
                    )
            elif isinstance(stmt, WhileStatement):
                cursor = self._walk_block_bindings(
                    stmt.body, lines, bindings,
                    container=container, search_from=cursor,
                )
        return cursor

    def _find_let_line(self, lines: List[str], name: str, start: int = 0) -> int:
        pat = re.compile(
            rf'^\s*let\s+(?:mut\s+)?{re.escape(name)}\b'
        )
        for i in range(max(0, start), len(lines)):
            if pat.search(lines[i]):
                return i
        # Fallback: any let with the name
        pat2 = re.compile(rf'\blet\s+(?:mut\s+)?{re.escape(name)}\b')
        for i in range(len(lines)):
            if pat2.search(lines[i]):
                return i
        return max(0, start)

    def _find_for_var_line(
        self, lines: List[str], name: str, start: int = 0
    ) -> int:
        pat = re.compile(rf'^\s*for\s+{re.escape(name)}\b')
        for i in range(max(0, start), len(lines)):
            if pat.search(lines[i]):
                return i
        return max(0, start)

    def _find_binding(
        self, uri: str, word: str, line: int
    ) -> Optional[Dict[str, Any]]:
        """Nearest binding of `word` declared at or before `line`."""
        best = None
        for b in self.bindings.get(uri, []):
            if b.get('name') != word:
                continue
            if b.get('line', 0) <= line:
                if best is None or b['line'] >= best['line']:
                    best = b
        return best

    _MODIFIER_LINE_RE = re.compile(
        r'^\s*(export|inline|always_inline|noinline)\s*$'
    )
    _ATTR_LINE_RE = re.compile(r'^\s*@[A-Za-z_][A-Za-z0-9_]*\s*$')

    def _doc_comment_above(self, lines: List[str], decl_line: int) -> str:
        """Collect consecutive `#` comments immediately above a declaration.

        Skips blank lines and declaration modifiers (`export`, `inline`, `@attr`)
        that sit between the comment block and the keyword. Blank lines inside
        the comment block are preserved. Stops at the first non-comment line.
        Includes `# @means` / `# @from` / `# @tier` / `# @needs` metadata lines.
        """
        if decl_line <= 0 or decl_line > len(lines):
            # decl_line is 0-based; allow 0
            pass
        if decl_line < 0 or not lines:
            return ''

        i = decl_line - 1
        # Skip modifiers / attributes / blanks glued to the declaration head.
        while i >= 0:
            raw = lines[i]
            stripped = raw.strip()
            if (
                stripped == ''
                or self._MODIFIER_LINE_RE.match(raw)
                or self._ATTR_LINE_RE.match(raw)
                or stripped in ('export', 'inline', 'always_inline', 'noinline')
            ):
                i -= 1
                continue
            # Also skip a line that is only `export` + keyword start on next line
            # already handled; if the decl line itself included `export function`,
            # comments are directly above — fall through.
            break

        if i < 0 or not lines[i].lstrip().startswith('#'):
            return ''

        # Collect the contiguous comment block (upward), allowing blank lines
        # inside the block only.
        block_end = i
        while i >= 0:
            stripped = lines[i].strip()
            if stripped.startswith('#'):
                i -= 1
                continue
            if stripped == '':
                # Peek further: blank allowed only if more comments continue above.
                j = i - 1
                while j >= 0 and lines[j].strip() == '':
                    j -= 1
                if j >= 0 and lines[j].lstrip().startswith('#'):
                    i -= 1
                    continue
                break
            break

        block_start = i + 1
        doc_lines: List[str] = []
        for idx in range(block_start, block_end + 1):
            stripped = lines[idx].strip()
            if stripped.startswith('#'):
                # Keep `# @means ...` metadata; strip a single leading `#`.
                body = stripped[1:]
                if body.startswith(' '):
                    body = body[1:]
                doc_lines.append(body)
            elif stripped == '':
                doc_lines.append('')
        # Trim leading/trailing blank lines in the prose
        while doc_lines and doc_lines[0] == '':
            doc_lines.pop(0)
        while doc_lines and doc_lines[-1] == '':
            doc_lines.pop()
        return '\n'.join(doc_lines)

    def _find_decl_line(self, lines: List[str], kind: str, name: str) -> int:
        """Best-effort 0-based line of `kind name` (handles claim paths)."""
        # Claim paths may contain `/`, `+`, `.`, etc.
        escaped = re.escape(name)
        pattern = re.compile(
            rf'^\s*(?:export\s+)?(?:inline\s+)?{kind}\s+{escaped}\b'
        )
        for idx, line in enumerate(lines):
            if pattern.search(line):
                return idx
        # Softer fallback: kind + name substring
        soft = re.compile(rf'\b{kind}\b')
        for idx, line in enumerate(lines):
            if soft.search(line) and name in line:
                return idx
        return 0

    def _extract_symbols_regex(
        self, text: str, *, exported_only: bool = False
    ) -> Dict[str, Dict[str, Any]]:
        """Regex fallback when the parser cannot load a file."""
        symbols: Dict[str, Dict[str, Any]] = {}
        lines = text.split('\n')
        decl_re = re.compile(
            r'^\s*(?P<export>export\s+)?'
            r'(?:inline\s+)?'
            r'(?P<kind>function|struct|enum|trait|theorem)\s+'
            r'(?P<name>[A-Za-z_][A-Za-z0-9_/.+\-]*)'
        )
        for idx, line in enumerate(lines):
            m = decl_re.match(line)
            if not m:
                continue
            if exported_only and not m.group('export'):
                continue
            kind = m.group('kind')
            name = m.group('name')
            info: Dict[str, Any] = {
                'kind': kind if kind != 'theorem' else 'theorem',
                'line': idx,
                'column': 0,
                'doc': self._doc_comment_above(lines, idx),
                'exported': bool(m.group('export')),
            }
            if kind == 'function':
                info['params'] = []
                info['return'] = 'void'
            elif kind == 'struct':
                info['fields'] = self._regex_struct_fields(lines, idx)
            elif kind == 'enum':
                info['variants'] = []
            elif kind == 'trait':
                info['methods'] = []
            elif kind == 'theorem':
                info['params'] = []
                info['return'] = 'void'
            symbols[name] = info
        return symbols

    @staticmethod
    def _regex_struct_fields(
        lines: List[str], start: int
    ) -> List[tuple]:
        """Pull `name: type` fields from a struct body (regex fallback)."""
        fields: List[tuple] = []
        field_re = re.compile(
            r'([A-Za-z_][A-Za-z0-9_]*)\s*:\s*([A-Za-z_][A-Za-z0-9_<>]*)'
        )
        # Same-line body: struct Point { x: f32, y: f32 }
        for i in range(start, min(start + 40, len(lines))):
            row = lines[i]
            for m in field_re.finditer(row):
                fname, ftype = m.group(1), m.group(2)
                if fname in ('struct', 'function', 'enum', 'trait'):
                    continue
                fields.append((fname, ftype))
            if i > start and re.search(r'^\s*\}', row):
                break
        return fields

    def _repo_root(self) -> Path:
        """Repository root discovered from this module's location."""
        # src/flow/lsp_server.py -> repo root
        return Path(__file__).resolve().parent.parent.parent

    @staticmethod
    def _stdlib_doc_rank(info: Dict[str, Any]) -> int:
        """Higher rank wins on name collisions across stdlib files."""
        path = (info.get('stdlib_path') or '').replace('\\', '/')
        base = path.rsplit('/', 1)[-1]
        # Prefer core numeric modules over AD/GPU overload wrappers.
        priority = {
            'math.flow': 100,
            'vec.flow': 90,
            'blas.flow': 80,
            'tensor.flow': 70,
            'array.flow': 60,
            'collections.flow': 50,
        }
        rank = priority.get(base, 10)
        doc = (info.get('doc') or '').strip()
        if not doc:
            return 0
        # Penalize section-banner docs that swallowed file headers.
        if doc.lstrip().startswith('===') or doc.lstrip().startswith('---'):
            rank -= 40
        if len(doc) > 400:
            rank -= 20
        return rank

    def _ensure_stdlib_indexed(self) -> None:
        """Scan lib/stdlib/**/*.flow for exported symbols + doc comments."""
        if self._stdlib_indexed:
            return
        self._stdlib_indexed = True
        stdlib_root = self._repo_root() / 'lib' / 'stdlib'
        if not stdlib_root.is_dir():
            return
        for path in sorted(stdlib_root.rglob('*.flow')):
            try:
                text = path.read_text(encoding='utf-8')
            except OSError:
                continue
            try:
                file_syms = self._extract_symbols_from_text(
                    text, exported_only=True
                )
            except Exception:
                continue
            for name, info in file_syms.items():
                info = dict(info)
                info['stdlib_path'] = str(
                    path.relative_to(self._repo_root())
                )
                try:
                    info['uri'] = path.resolve().as_uri()
                except Exception:
                    info['uri'] = path.as_uri()
                existing = self.stdlib_symbols.get(name)
                if existing is None:
                    self.stdlib_symbols[name] = info
                    continue
                new_doc = (info.get('doc') or '').strip()
                old_doc = (existing.get('doc') or '').strip()
                # Later files win when they carry docs (math.flow after
                # autodiff.flow so plain `add`/`sin` get the numeric docs).
                # Never let an empty later decl erase a documented one.
                if new_doc and (
                    not old_doc
                    or self._stdlib_doc_rank(info) >= self._stdlib_doc_rank(
                        existing
                    )
                ):
                    self.stdlib_symbols[name] = info

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def _publish_diagnostics(self, uri: str):
        """Compute diagnostics for a document and push them to the client."""
        text = self.documents.get(uri)
        if text is None:
            return
        diagnostics = self._compute_diagnostics(text, uri=uri)
        self._send_notification('textDocument/publishDiagnostics', {
            'uri': uri,
            'diagnostics': diagnostics,
        })

    def _compute_diagnostics(self, text: str, uri: Optional[str] = None) -> List[dict]:
        """Run the FLOW parser + type checker over text, return LSP diagnostics.

        Parser/lexer errors are severity 1 (Error); type-checker findings are
        severity 2 (Warning). Reuses the compiler's own error objects:
        FlowSyntaxError carries 1-based line/column which we convert to
        0-based LSP positions.
        """
        diagnostics: List[dict] = []

        # Phase 1: parse (syntax errors stop here - the AST is unusable)
        try:
            lexer = Lexer(text)
            parser = Parser(lexer, source=text)
            declarations = parser.parse()
        except FlowSyntaxError as e:
            # First line of the message is the human-readable summary;
            # the rest is terminal-oriented source context we don't need in LSP.
            message = str(e).split('\n')[0]
            if e.suggestion:
                message += f" (hint: {e.suggestion})"
            line = (e.line - 1) if e.line else 0
            column = (e.column - 1) if e.column else 0
            diagnostics.append({
                'range': self._word_range(text, line, column),
                'severity': 1,
                'source': 'flow-parser',
                'message': message,
            })
            return diagnostics
        except SyntaxError as e:
            # Plain lexer/parser SyntaxError without structured location;
            # some messages embed "at line L, column C" - recover it if present.
            message = str(e).split('\n')[0]
            line, column = 0, 0
            m = re.search(r'line (\d+)(?:, column (\d+))?', message)
            if m:
                line = max(int(m.group(1)) - 1, 0)
                if m.group(2):
                    column = max(int(m.group(2)) - 1, 0)
            diagnostics.append({
                'range': self._word_range(text, line, column),
                'severity': 1,
                'source': 'flow-parser',
                'message': message,
            })
            return diagnostics
        except Exception as e:
            diagnostics.append({
                'range': self._word_range(text, 0, 0),
                'severity': 1,
                'source': 'flow-parser',
                'message': f"Internal parser error: {e}",
            })
            return diagnostics

        # Phase 2: type errors from analyze cache when available; else check now
        try:
            cached_errors = None
            if uri and uri in self.type_cache:
                cached_errors = (self.type_cache.get(uri) or {}).get('errors')
            if cached_errors is None:
                checker = TypeChecker()
                result = checker.check(declarations)
                cached_errors = result.errors
            seen = set()
            for err in cached_errors or []:
                if err in seen:  # checker can report the same finding twice
                    continue
                seen.add(err)
                diagnostics.append({
                    'range': self._range_for_type_error(text, err),
                    'severity': 2,
                    'source': 'flow-typecheck',
                    'message': err,
                })
        except Exception as e:
            sys.stderr.write(f"LSP type-check error: {e}\n")
            sys.stderr.flush()

        return diagnostics

    def _range_for_type_error(self, text: str, message: str) -> dict:
        """Best-effort range for a location-less type error message.

        Type checker messages usually quote the offending symbol
        (e.g. \"Undefined variable 'x'\") - point at its first occurrence.
        """
        m = re.search(r"'([A-Za-z_][A-Za-z0-9_]*)'", message)
        if m:
            name = m.group(1)
            pattern = re.compile(r'\b' + re.escape(name) + r'\b')
            for line_no, line_text in enumerate(text.split('\n')):
                found = pattern.search(line_text)
                if found:
                    return {
                        'start': {'line': line_no, 'character': found.start()},
                        'end': {'line': line_no, 'character': found.end()},
                    }
        # Fallback: flag the first line
        first_len = len(text.split('\n', 1)[0])
        return {
            'start': {'line': 0, 'character': 0},
            'end': {'line': 0, 'character': first_len},
        }

    def _word_range(self, text: str, line: int, column: int) -> dict:
        """Range covering the word (or at least one character) at line/column."""
        lines = text.split('\n')
        if line >= len(lines):
            line = max(len(lines) - 1, 0)
        line_text = lines[line] if lines else ''
        if column > len(line_text):
            column = max(len(line_text) - 1, 0)
        end = column
        while end < len(line_text) and (line_text[end].isalnum() or line_text[end] == '_'):
            end += 1
        if end == column:
            end = min(column + 1, max(len(line_text), column + 1))
        return {
            'start': {'line': line, 'character': column},
            'end': {'line': line, 'character': end},
        }

    def _completion_prefix(self, text: str, line: int, character: int) -> str:
        """Word / `dyn.` prefix at the cursor for filtering completions."""
        lines = text.splitlines()
        if line < 0 or line >= len(lines):
            return ""
        row = lines[line]
        i = min(character, len(row))
        start = i
        while start > 0 and (row[start - 1].isalnum() or row[start - 1] in "._"):
            start -= 1
        return row[start:i]

    def _handle_completion(self, params: dict) -> List[dict]:
        """Handle textDocument/completion."""
        uri = params['textDocument']['uri']
        pos = params.get('position') or {}
        line = int(pos.get('line', 0))
        character = int(pos.get('character', 0))
        text = self.documents.get(uri, '')
        prefix = self._completion_prefix(text, line, character)

        # Field completion after `recv.`
        recv = lsp_intel.receiver_before_dot(text, line, character)
        if recv:
            return self._complete_fields(uri, recv, line, prefix)

        items: List[dict] = []

        # Dynamics DSL + declarative ordering snippets
        items.extend(dynamics_completion_items(prefix))
        items.extend(ordering_completion_items(prefix))
        seen = {it["label"] for it in items}

        # Add keywords
        for kw in self.keywords:
            if kw in seen:
                continue
            if prefix and not kw.startswith(prefix):
                continue
            items.append({
                'label': kw,
                'kind': 14,  # Keyword
                'detail': 'keyword',
            })
            seen.add(kw)

        # Add types
        for t in self.builtin_types:
            if t in seen:
                continue
            if prefix and not t.startswith(prefix):
                continue
            items.append({
                'label': t,
                'kind': 21,  # TypeParameter
                'detail': 'type',
            })
            seen.add(t)

        # Add built-in functions
        for name, info in self.builtin_functions.items():
            if name in seen:
                continue
            if prefix and not name.startswith(prefix):
                continue
            items.append({
                'label': name,
                'kind': 3,  # Function
                'detail': f"({', '.join(info['params'])}) -> {info['return']}",
                'documentation': info.get('doc', ''),
            })
            seen.add(name)

        # Locals / parameters in the current document
        for b in self.bindings.get(uri, []):
            name = b.get('name') or ''
            if name in seen:
                continue
            if prefix and not name.startswith(prefix):
                continue
            detail = b.get('detail') or (
                f"{'mut ' if b.get('mutable') else ''}{b.get('type', '?')}"
            )
            kind = 6 if b.get('kind') == 'variable' else 6  # Variable
            if b.get('kind') == 'parameter':
                kind = 6
            items.append({
                'label': name,
                'kind': kind,
                'detail': detail,
                'documentation': (
                    f"{b.get('kind', 'binding')} in `{b.get('container', '')}`"
                ),
            })
            seen.add(name)

        # Add document symbols
        doc_symbols = self.symbols.get(uri, {})
        for name, info in doc_symbols.items():
            if name in seen:
                continue
            if prefix and not name.startswith(prefix):
                continue
            item = self._completion_item_for_symbol(name, info)
            if item:
                items.append(item)
                seen.add(name)

        # Also add symbols from other open documents
        for other_uri, other_symbols in self.symbols.items():
            if other_uri != uri:
                for name, info in other_symbols.items():
                    if name in seen:
                        continue
                    if prefix and not name.startswith(prefix):
                        continue
                    item = self._completion_item_for_symbol(name, info)
                    if item:
                        items.append(item)
                        seen.add(name)

        # Stdlib exports (filtered by prefix; skip huge dump when empty prefix)
        if prefix:
            self._ensure_stdlib_indexed()
            for name, info in self.stdlib_symbols.items():
                if name in seen:
                    continue
                if not name.startswith(prefix):
                    continue
                item = self._completion_item_for_symbol(name, info)
                if item:
                    doc = (info.get('doc') or '').strip()
                    if info.get('stdlib_path'):
                        doc = (doc + f"\n\nstdlib: {info['stdlib_path']}").strip()
                    if doc:
                        item['documentation'] = doc
                    items.append(item)
                    seen.add(name)

        return items

    def _complete_fields(
        self, uri: str, recv: str, line: int, prefix: str
    ) -> List[dict]:
        """Complete struct fields for `recv.`."""
        cache = self.type_cache.get(uri) or {}
        struct_fields = dict(cache.get('struct_fields') or {})
        global_types = cache.get('global_types') or {}
        # Ensure local struct symbols contribute fields
        for name, info in self.symbols.get(uri, {}).items():
            if info.get('kind') == 'struct' and name not in struct_fields:
                struct_fields[name] = list(info.get('fields') or [])

        type_str = lsp_intel.lookup_receiver_type(
            recv, line, self.bindings.get(uri, []), global_types
        )
        if not type_str:
            sym = self.symbols.get(uri, {}).get(recv)
            if sym and sym.get('kind') == 'const':
                type_str = sym.get('type')
        type_name = lsp_intel.resolve_type_name(
            type_str or '', global_types, struct_fields
        )
        if not type_name and recv in struct_fields:
            type_name = recv
        fields = struct_fields.get(type_name or '', [])
        # `prefix` from `_completion_prefix` is the field fragment after `.`
        # because that helper stops at non-identifier chars including `.` —
        # actually it includes `.` in the charset! Strip through last dot.
        field_prefix = prefix
        if '.' in prefix:
            field_prefix = prefix.rsplit('.', 1)[-1]
        items = []
        for fname, ftype in fields:
            if field_prefix and not fname.startswith(field_prefix):
                continue
            items.append({
                'label': fname,
                'kind': 5,  # Field
                'detail': str(ftype),
                'documentation': f'Field of `{type_name}`',
                'insertText': fname,
            })
        return items

    @staticmethod
    def _completion_item_for_symbol(name: str, info: Dict[str, Any]) -> Optional[dict]:
        kind = info.get('kind')
        if kind == 'function':
            params_str = ', '.join(
                [f"{p[0]}: {p[1]}" for p in (info.get('params') or [])]
            )
            return {
                'label': name,
                'kind': 3,
                'detail': f"({params_str}) -> {info.get('return', 'void')}",
            }
        if kind == 'struct':
            return {'label': name, 'kind': 22, 'detail': 'struct'}
        if kind == 'enum':
            return {'label': name, 'kind': 10, 'detail': 'enum'}
        if kind == 'trait':
            return {'label': name, 'kind': 8, 'detail': 'trait'}
        if kind == 'theorem':
            return {'label': name, 'kind': 12, 'detail': 'theorem'}
        if kind == 'const':
            return {
                'label': name,
                'kind': 21,
                'detail': f"const {info.get('type', '?')}",
            }
        if kind == 'effect':
            return {'label': name, 'kind': 8, 'detail': 'effect'}
        if kind in ('type', 'capability'):
            return {
                'label': name,
                'kind': 21,
                'detail': kind,
            }
        return None
    
    def _handle_hover(self, params: dict) -> Optional[dict]:
        """Handle textDocument/hover.

        Resolution order:
          1. dynamics DSL keywords (`dsys`, `dyn.…`, …)
          2. declarative ordering (`sort`, `sortBy`, …)
          3. multi-char operators (`|>`, `->`, …) via syntax token
          4. locals / parameters at cursor (typed bindings)
          5. symbols in the current document (signature + `#` doc comments)
          6. built-in functions (signature + prose doc)
          7. symbols in other open documents
          8. exported stdlib symbols (cached from lib/stdlib)
          9. syntax / keyword catalog (match, let, types, …)
          10. bare built-in type name
        """
        uri = params['textDocument']['uri']
        pos = params['position']
        line = pos['line']
        character = pos['character']

        text = self.documents.get(uri, '')
        word = self._get_word_at_position(text, line, character)
        syntax_tok = syntax_token_at_position(text, line, character)

        # Operators first (cursor on `|>` etc. — word may be empty).
        if syntax_tok and syntax_tok in MULTI_CHAR_OPS:
            syn_doc = syntax_hover(syntax_tok)
            if syn_doc:
                return self._markdown_hover(syn_doc)

        # Field access: `p.x`
        field_acc = lsp_intel.field_access_at(text, line, character)
        if field_acc:
            hover = self._hover_for_field(uri, line, field_acc[0], field_acc[1])
            if hover:
                return hover

        if word:
            # User bindings / symbols beat catalogs (sort/dsys keyword essays).
            binding = self._find_binding(uri, word, line)
            if binding:
                return self._hover_for_binding(binding)

            doc_symbols = self.symbols.get(uri, {})
            hover_info = self._get_hover_for_symbol(word, doc_symbols)
            if hover_info:
                # Enrich with typechecker type when present
                return self._enrich_hover_with_type(uri, word, hover_info)

            # Imported symbols (also merged into doc_symbols, but keep explicit)
            imp = self.import_symbols.get(uri, {}).get(word)
            if imp:
                hover_info = self._get_hover_for_symbol(word, {word: imp})
                if hover_info:
                    return self._enrich_hover_with_type(uri, word, hover_info)

            dyn_doc = dynamics_hover(word)
            if dyn_doc:
                return self._markdown_hover(dyn_doc)

            ord_doc = ordering_hover(word)
            if ord_doc:
                return self._markdown_hover(ord_doc)

            # Built-in functions (enrich with stdlib `#` docs when available)
            if word in self.builtin_functions:
                info = self.builtin_functions[word]
                prose = info.get('doc', '')
                self._ensure_stdlib_indexed()
                std = self.stdlib_symbols.get(word) or {}
                std_doc = (std.get('doc') or '').strip()
                if std_doc and (
                    not prose or len(std_doc) > len(prose)
                ):
                    prose = std_doc
                value = (
                    f"```flow\nfunction {word}({', '.join(info['params'])}) "
                    f"-> {info['return']}\n```"
                )
                if prose:
                    value += f"\n\n{prose}"
                if std.get('stdlib_path'):
                    value += f"\n\n*stdlib:* `{std['stdlib_path']}`"
                return self._markdown_hover(value)

            # Other open documents
            for other_uri, other_symbols in self.symbols.items():
                if other_uri != uri:
                    hover_info = self._get_hover_for_symbol(word, other_symbols)
                    if hover_info:
                        return hover_info

            # Stdlib cache (lazy if init indexing was skipped)
            self._ensure_stdlib_indexed()
            hover_info = self._get_hover_for_symbol(word, self.stdlib_symbols)
            if hover_info:
                return hover_info

        # Keyword / type catalog (after user symbols so bindings win)
        tok = syntax_tok or word
        if tok:
            syn_doc = syntax_hover(tok)
            if syn_doc:
                return self._markdown_hover(syn_doc)

        if word and word in self.builtin_types:
            return self._markdown_hover(f"**{word}**\n\nBuilt-in type")

        return None

    def _hover_for_binding(self, binding: Dict[str, Any]) -> dict:
        name = binding.get('name', '?')
        typ = binding.get('type', 'unknown')
        kind = binding.get('kind', 'variable')
        mut = 'mut ' if binding.get('mutable') else ''
        container = binding.get('container') or ''
        detail = binding.get('detail')
        if kind == 'parameter':
            header = f"```flow\n{name}: {typ}\n```\n\nParameter"
        else:
            header = f"```flow\nlet {mut}{name}: {typ}\n```\n\nLocal variable"
        if binding.get('typed'):
            header += " *(typechecked)*"
        if detail:
            header += f" ({detail})"
        if container:
            header += f" in `{container}`"
        return self._markdown_hover(header)

    def _hover_for_field(
        self, uri: str, line: int, recv: str, field: str
    ) -> Optional[dict]:
        cache = self.type_cache.get(uri) or {}
        struct_fields = dict(cache.get('struct_fields') or {})
        for name, info in self.symbols.get(uri, {}).items():
            if info.get('kind') == 'struct' and name not in struct_fields:
                struct_fields[name] = list(info.get('fields') or [])
        global_types = cache.get('global_types') or {}
        type_str = lsp_intel.lookup_receiver_type(
            recv, line, self.bindings.get(uri, []), global_types
        )
        type_name = lsp_intel.resolve_type_name(
            type_str or '', global_types, struct_fields
        )
        if not type_name:
            return None
        for fname, ftype in struct_fields.get(type_name, []):
            if fname == field:
                return self._markdown_hover(
                    f"```flow\n{field}: {ftype}\n```\n\n"
                    f"Field of `{type_name}` (receiver `{recv}: {type_str}`)"
                )
        return None

    def _defining_file_note(self, info: Dict[str, Any]) -> str:
        """Markdown note naming the file that defines an imported symbol.

        The info's `uri` already points at the real declaration file (from
        the resolver's `flow_source_file` stamp, followed through re-exports),
        so the note stays readable, e.g. "defined in: path/to/dep.flow".
        """
        uri = info.get('uri') or ''
        if not uri:
            return ''
        path = lsp_intel.uri_to_path(uri)
        if not path:
            return ''
        try:
            rel = os.path.relpath(path, self._repo_root())
            if not rel.startswith('..'):
                display = rel
            else:
                display = os.path.basename(path)
        except ValueError:  # Windows: paths on different drives
            display = os.path.basename(path)
        return f"\n\n*defined in:* `{display}`"

    def _enrich_hover_with_type(
        self, uri: str, word: str, hover_info: dict
    ) -> dict:
        cache = self.type_cache.get(uri) or {}
        typ = (cache.get('global_types') or {}).get(word)
        kind = (cache.get('symbol_kinds') or {}).get(word)
        value = hover_info.get('contents', {}).get('value') or ''
        if typ and typ not in value:
            note = f"\n\n*type:* `{typ}`"
            if kind:
                note = f"\n\n*typechecked {kind}:* `{typ}`"
            value += note
        # Note which file defines an imported symbol — even when the type
        # checker could not infer a type (e.g. typecheck failed entirely).
        # Gate on the hovered symbol's own `imported` flag so a local
        # declaration shadowing an imported name never gets the note.
        imp = self.import_symbols.get(uri, {}).get(word)
        hovered = self.symbols.get(uri, {}).get(word) or {}
        if imp and hovered.get('imported'):
            defined_note = self._defining_file_note(imp)
            if defined_note and defined_note not in value:
                value += defined_note
        if value != hover_info.get('contents', {}).get('value'):
            hover_info = {
                'contents': {'kind': 'markdown', 'value': value}
            }
        return hover_info

    @staticmethod
    def _markdown_hover(value: str) -> dict:
        return {
            'contents': {
                'kind': 'markdown',
                'value': value,
            }
        }

    def _get_hover_for_symbol(self, word: str, symbols: Dict) -> Optional[dict]:
        """Generate hover content for a symbol, including `doc` when present."""
        if word not in symbols:
            return None

        info = symbols[word]
        doc = (info.get('doc') or '').strip()
        stdlib_note = ''
        if info.get('stdlib_path'):
            stdlib_note = f"\n\n*stdlib:* `{info['stdlib_path']}`"

        if info['kind'] == 'function':
            params = info.get('params') or []
            params_str = ', '.join([f"{p[0]}: {p[1]}" for p in params])
            ret = info.get('return', 'void')
            value = f"```flow\nfunction {word}({params_str}) -> {ret}\n```"
            if doc:
                value += f"\n\n{doc}"
            value += stdlib_note
            return self._markdown_hover(value)
        if info['kind'] == 'theorem':
            params = info.get('params') or []
            params_str = ', '.join([f"{p[0]}: {p[1]}" for p in params])
            value = f"```flow\ntheorem {word}({params_str})\n```"
            if doc:
                value += f"\n\n{doc}"
            return self._markdown_hover(value)
        if info['kind'] == 'struct':
            fields = info.get('fields') or []
            fields_str = '\n'.join([f"    {f[0]}: {f[1]}" for f in fields])
            value = f"```flow\nstruct {word} {{\n{fields_str}\n}}\n```"
            if doc:
                value += f"\n\n{doc}"
            value += stdlib_note
            return self._markdown_hover(value)
        if info['kind'] == 'enum':
            variants_str = ', '.join(info.get('variants', []))
            value = f"```flow\nenum {word} {{ {variants_str} }}\n```"
            if doc:
                value += f"\n\n{doc}"
            return self._markdown_hover(value)
        if info['kind'] == 'trait':
            methods_str = ', '.join(info.get('methods', []))
            value = (
                f"```flow\ntrait {word} {{\n"
                f"  # methods: {methods_str}\n}}\n```"
            )
            if doc:
                value += f"\n\n{doc}"
            return self._markdown_hover(value)
        if info['kind'] == 'const':
            typ = info.get('type', 'unknown')
            value = f"```flow\nconst {word}: {typ}\n```"
            if doc:
                value += f"\n\n{doc}"
            value += stdlib_note
            return self._markdown_hover(value)
        if info['kind'] == 'effect':
            ops = ', '.join(info.get('operations') or [])
            value = f"```flow\neffect {word} {{ {ops} }}\n```"
            if doc:
                value += f"\n\n{doc}"
            return self._markdown_hover(value)
        if info['kind'] == 'type':
            base = info.get('type', 'unknown')
            value = f"```flow\ntype {word} = {base}\n```"
            if doc:
                value += f"\n\n{doc}"
            value += stdlib_note
            return self._markdown_hover(value)
        if info['kind'] == 'capability':
            effects = ', '.join(info.get('effects') or [])
            value = f"```flow\ncapability {word} {{ {effects} }}\n```"
            if doc:
                value += f"\n\n{doc}"
            return self._markdown_hover(value)
        return None

    @staticmethod
    def _location_from_symbol(
        uri: str, word: str, info: Dict[str, Any]
    ) -> dict:
        line = int(info.get('line', 0) or 0)
        column = int(info.get('column', 0) or 0)
        end_line = int(info.get('end_line', line) or line)
        end_column = int(info.get('end_column', column + len(word)) or 0)
        if end_column <= column:
            end_column = column + len(word)
        return {
            'uri': uri,
            'range': {
                'start': {'line': line, 'character': column},
                'end': {'line': end_line, 'character': end_column},
            },
        }
    
    def _handle_definition(self, params: dict) -> Optional[dict]:
        """Handle textDocument/definition."""
        uri = params['textDocument']['uri']
        pos = params['position']
        
        text = self.documents.get(uri, '')
        word = self._get_word_at_position(text, pos['line'], pos['character'])
        
        if not word:
            return None

        # Locals / parameters first
        binding = self._find_binding(uri, word, pos['line'])
        if binding:
            return self._location_from_symbol(uri, word, binding)

        # Field access → struct field declaration when possible
        field_acc = lsp_intel.field_access_at(
            text, pos['line'], pos['character']
        )
        if field_acc:
            recv, field = field_acc
            loc = self._definition_for_field(uri, pos['line'], recv, field)
            if loc:
                return loc
        
        # Check document symbols in current file (local decls win over imports)
        doc_symbols = self.symbols.get(uri, {})
        if word in doc_symbols:
            info = doc_symbols[word]
            target_uri = info.get('uri') or uri
            # Don't jump to import uri for a local definition without imported flag
            if info.get('imported') and info.get('uri'):
                target_uri = info['uri']
            elif not info.get('imported'):
                target_uri = uri
            return self._location_from_symbol(target_uri, word, info)

        # Explicit import map
        imp = self.import_symbols.get(uri, {}).get(word)
        if imp and imp.get('uri'):
            return self._location_from_symbol(imp['uri'], word, imp)
        
        # Check symbols in all open documents (cross-file go-to-definition)
        for other_uri, other_symbols in self.symbols.items():
            if other_uri != uri and word in other_symbols:
                info = other_symbols[word]
                target = info.get('uri') or other_uri
                return self._location_from_symbol(target, word, info)

        # Stdlib export → jump into lib/stdlib file
        self._ensure_stdlib_indexed()
        std = self.stdlib_symbols.get(word)
        if std and std.get('uri'):
            return self._location_from_symbol(std['uri'], word, std)
        
        return None

    def _definition_for_field(
        self, uri: str, line: int, recv: str, field: str
    ) -> Optional[dict]:
        cache = self.type_cache.get(uri) or {}
        struct_fields = cache.get('struct_fields') or {}
        global_types = cache.get('global_types') or {}
        type_str = lsp_intel.lookup_receiver_type(
            recv, line, self.bindings.get(uri, []), global_types
        )
        type_name = lsp_intel.resolve_type_name(
            type_str or '', global_types, struct_fields
        )
        if not type_name:
            return None
        # Prefer struct decl in current file / imports
        info = self.symbols.get(uri, {}).get(type_name)
        if not info:
            return None
        target_uri = info.get('uri') or uri
        # Point at the struct name; field column best-effort via text search
        loc = self._location_from_symbol(target_uri, type_name, info)
        target_text = self.documents.get(target_uri)
        if target_text is None and target_uri.startswith('file://'):
            path = lsp_intel.uri_to_path(target_uri)
            if path and os.path.isfile(path):
                try:
                    target_text = Path(path).read_text(encoding='utf-8')
                except OSError:
                    target_text = None
        if target_text:
            for i, row in enumerate(target_text.split('\n')):
                m = re.search(rf'\b{re.escape(field)}\s*:', row)
                if m:
                    loc['range'] = {
                        'start': {'line': i, 'character': m.start()},
                        'end': {
                            'line': i,
                            'character': m.start() + len(field),
                        },
                    }
                    break
        return loc
    
    def _handle_document_symbol(self, params: dict) -> List[dict]:
        """Handle textDocument/documentSymbol."""
        uri = params['textDocument']['uri']
        doc_symbols = self.symbols.get(uri, {})
        
        # Symbol kinds: 12=Function, 23=Struct, 10=Enum, 11=Interface(trait)
        kind_map = {
            'function': 12,
            'struct': 23,
            'enum': 10,
            'trait': 11,
            'theorem': 12,
            'const': 14,       # Constant
            'effect': 11,
            'type': 5,         # Class (approx for type alias)
            'capability': 11,
        }
        
        symbols = []
        for name, info in doc_symbols.items():
            kind = kind_map.get(info['kind'], 12)
            line = int(info.get('line', 0) or 0)
            column = int(info.get('column', 0) or 0)
            end_line = int(info.get('end_line', line) or line)
            end_column = int(
                info.get('end_column', column + len(name)) or (column + len(name))
            )
            if end_column <= column:
                end_column = column + max(len(name), 1)
            
            symbols.append({
                'name': name,
                'kind': kind,
                'detail': info.get('kind'),
                'range': {
                    'start': {'line': line, 'character': column},
                    'end': {'line': end_line, 'character': end_column},
                },
                'selectionRange': {
                    'start': {'line': line, 'character': column},
                    'end': {'line': line, 'character': column + len(name)},
                },
            })
        
        return symbols
    
    def _find_references_in_text(self, text: str, word: str) -> List[dict]:
        """Find identifier occurrences of word in text.

        Tokenizes with the compiler's Lexer so mentions inside comments and
        string literals are NOT counted. Falls back to a word-boundary regex
        scan if the buffer cannot be tokenized (e.g. mid-edit garbage).
        """
        locations = []
        try:
            tokens = Lexer(text).tokenize()
        except Exception:
            tokens = None

        if tokens is not None:
            for tok in tokens:
                # Identifiers only; TEST is included because the lexer maps
                # the identifier 'test' to a keyword token (parser allows it
                # as a name, e.g. `function test()`).
                if tok.type not in (TokenType.IDENTIFIER, TokenType.TEST):
                    continue
                if tok.value != word:
                    continue
                line = tok.line - 1  # tokens are 1-based; LSP is 0-based
                column = tok.column - 1
                locations.append({
                    'range': {
                        'start': {'line': line, 'character': column},
                        'end': {'line': line, 'character': column + len(word)},
                    }
                })
            return locations

        # Fallback: plain text scan
        pattern = re.compile(r'\b' + re.escape(word) + r'\b')
        for line_no, line_text in enumerate(text.split('\n')):
            for match in pattern.finditer(line_text):
                locations.append({
                    'range': {
                        'start': {'line': line_no, 'character': match.start()},
                        'end': {'line': line_no, 'character': match.end()},
                    }
                })
        return locations

    def _resolve_symbol(self, uri: str, word: str, line: Optional[int] = None):
        """Resolve word against bindings, document symbols, then stdlib.

        Returns (decl_uri, decl_info) or (None, None).
        """
        if line is not None:
            binding = self._find_binding(uri, word, line)
            if binding:
                return uri, binding
        if word in self.symbols.get(uri, {}):
            return uri, self.symbols[uri][word]
        for other_uri, other_symbols in self.symbols.items():
            if other_uri != uri and word in other_symbols:
                return other_uri, other_symbols[word]
        self._ensure_stdlib_indexed()
        std = self.stdlib_symbols.get(word)
        if std and std.get('uri'):
            return std['uri'], std
        return None, None

    def _collect_reference_locations(self, uri: str, word: str):
        """Collect every identifier occurrence of word, declaration included.

        Top-level symbols (functions, structs, enums, traits) are searched
        across every open document; names not in any symbol index (locals,
        parameters) are searched in the current file only.

        Returns (refs, decl_uri, decl_info) where refs is a list of
        {'uri': ..., 'range': ...} Locations.
        """
        decl_uri, decl_info = self._resolve_symbol(uri, word)

        # Top-level symbol -> search all open documents (cross-file, like
        # definition/hover). Local name -> same-file only.
        if decl_uri is not None:
            search_docs = list(self.documents.items())
        else:
            search_docs = [(uri, self.documents.get(uri, ''))]

        refs = []
        for doc_uri, doc_text in search_docs:
            for loc in self._find_references_in_text(doc_text, word):
                refs.append({'uri': doc_uri, **loc})
        return refs, decl_uri, decl_info

    def _handle_references(self, params: dict) -> List[dict]:
        """Handle textDocument/references.

        Resolution mirrors _handle_definition: top-level symbols (functions,
        structs, enums, traits) are looked up in the per-document symbol
        index built on didOpen/didChange, and their references are collected
        across every open document. Names that are not in any symbol index
        (local variables, parameters) are searched in the current file only.
        """
        uri = params['textDocument']['uri']
        pos = params['position']
        include_declaration = params.get('context', {}).get('includeDeclaration', True)
        text = self.documents.get(uri, '')
        word = self._get_word_at_position(text, pos['line'], pos['character'])
        if not word:
            return []

        refs, decl_uri, decl_info = self._collect_reference_locations(uri, word)

        if not include_declaration and decl_info is not None:
            decl_line = decl_info.get('line', -1)
            refs = [
                r for r in refs
                if not (r['uri'] == decl_uri
                        and r['range']['start']['line'] == decl_line)
            ]

        return refs

    # ------------------------------------------------------------------
    # Rename
    #
    # Rename is references + edits: the same occurrence collection that
    # backs textDocument/references (declaration included) is turned into
    # a WorkspaceEdit. It inherits the references scope honestly:
    #   - Top-level symbols (functions, structs, enums, traits) are renamed
    #     across every OPEN document. Files on disk that are not open in
    #     the editor are NOT touched.
    #   - Local names (variables, parameters) are renamed file-wide in the
    #     current document. The token scan is not scope-aware, so two
    #     distinct locals with the same name in different functions of the
    #     same file are renamed together (same limitation as references).
    #   - A local that shadows a top-level symbol of the same name resolves
    #     to the top-level symbol and is renamed cross-file.
    #   - 'test' is a contextual keyword the parser allows as a function
    #     name; rename conservatively rejects it as a keyword.
    # ------------------------------------------------------------------

    def _prepare_rename_info(self, uri: str, pos: dict):
        """Return (word, range) if pos is on a renameable identifier.

        Returns None for keywords, literals, comments/strings, whitespace,
        and anything else that is not an identifier token.
        """
        text = self.documents.get(uri, '')
        line, character = pos['line'], pos['character']
        word = self._get_word_at_position(text, line, character)
        if not word:
            return None  # whitespace / punctuation
        if not self._is_valid_identifier(word):
            return None  # e.g. cursor inside a numeric literal
        if word in self.reserved_names:
            return None  # keyword or true/false/null literal
        # The position must sit on an actual identifier token; occurrences
        # inside comments or string literals are not symbols.
        for loc in self._find_references_in_text(text, word):
            r = loc['range']
            if (r['start']['line'] == line
                    and r['start']['character'] <= character <= r['end']['character']):
                return word, r
        return None

    def _handle_prepare_rename(self, params: dict) -> Optional[dict]:
        """Handle textDocument/prepareRename.

        Returns the symbol's range and placeholder text, or null when the
        position is not on a renameable symbol.
        """
        prep = self._prepare_rename_info(params['textDocument']['uri'],
                                         params['position'])
        if prep is None:
            return None
        word, rng = prep
        return {'range': rng, 'placeholder': word}

    def _handle_rename(self, params: dict) -> dict:
        """Handle textDocument/rename: return a WorkspaceEdit.

        Built directly on the references machinery (see class comment above
        for the inherited scope). Rejects invalid or reserved new names and
        rename requests on keywords/literals/non-symbols with a JSON-RPC
        error response.
        """
        uri = params['textDocument']['uri']
        pos = params['position']
        new_name = params.get('newName', '')

        prep = self._prepare_rename_info(uri, pos)
        if prep is None:
            raise LspError('Cannot rename this element: '
                           'not a renameable symbol')
        word, _ = prep

        if not self._is_valid_identifier(new_name):
            raise LspError(f"Cannot rename to '{new_name}': "
                           "not a valid Flow identifier")
        if new_name in self.reserved_names:
            raise LspError(f"Cannot rename to '{new_name}': "
                           "reserved Flow keyword")

        refs, _, _ = self._collect_reference_locations(uri, word)
        changes: Dict[str, List[dict]] = {}
        for ref in refs:
            changes.setdefault(ref['uri'], []).append({
                'range': ref['range'],
                'newText': new_name,
            })
        return {'changes': changes}

    def _format_document_text(self, text: str) -> Optional[str]:
        """Return formatted source, or None if formatting fails / is a no-op."""
        try:
            from .formatter import Formatter
            formatted = Formatter().format_file(text)
        except Exception:
            return None
        if formatted == text:
            return None
        # Ensure trailing newline (common editor expectation)
        if formatted and not formatted.endswith('\n'):
            formatted += '\n'
        return formatted

    def _full_document_edit(self, text: str, new_text: str) -> List[dict]:
        lines = text.split('\n')
        end_line = max(0, len(lines) - 1)
        end_char = len(lines[end_line]) if lines else 0
        return [{
            'range': {
                'start': {'line': 0, 'character': 0},
                'end': {'line': end_line, 'character': end_char},
            },
            'newText': new_text,
        }]

    def _handle_formatting(self, params: dict) -> List[dict]:
        """Handle textDocument/formatting via the Flow Formatter."""
        uri = params['textDocument']['uri']
        text = self.documents.get(uri, '')
        formatted = self._format_document_text(text)
        if formatted is None:
            return []
        return self._full_document_edit(text, formatted)

    def _handle_range_formatting(self, params: dict) -> List[dict]:
        """Range formatting: format the whole file (AST formatter is whole-doc)."""
        return self._handle_formatting(params)

    def _handle_document_highlight(self, params: dict) -> List[dict]:
        """Highlight all occurrences of the symbol under the cursor."""
        uri = params['textDocument']['uri']
        text = self.documents.get(uri, '')
        if not text:
            return []
        pos = params['position']
        word = self._get_word_at_position(text, pos['line'], pos['character'])
        if not word or not self._is_valid_identifier(word):
            return []
        if word in self.reserved_names:
            return []
        highlights = []
        for loc in self._find_references_in_text(text, word):
            highlights.append({
                'range': loc['range'],
                'kind': 1,  # Text
            })
        return highlights

    def _get_word_at_position(self, text: str, line: int, character: int) -> str:
        """Get the word at a given position in the text."""
        lines = text.split('\n')
        if line >= len(lines):
            return ''
        
        line_text = lines[line]
        if character >= len(line_text):
            return ''
        
        # Find word boundaries
        start = character
        while start > 0 and (line_text[start - 1].isalnum() or line_text[start - 1] == '_'):
            start -= 1
        
        end = character
        while end < len(line_text) and (line_text[end].isalnum() or line_text[end] == '_'):
            end += 1
        
        return line_text[start:end]
    
    def _send_message(self, message: dict):
        """Serialize and write an LSP message to stdout (thread-safe)."""
        body = json.dumps(message)
        with self._write_lock:
            sys.stdout.write(f'Content-Length: {len(body)}\r\n\r\n{body}')
            sys.stdout.flush()

    def _send_notification(self, method: str, params: dict):
        """Send a server-initiated notification (e.g. publishDiagnostics)."""
        self._send_message({'jsonrpc': '2.0', 'method': method, 'params': params})

    def run(self):
        """Run the LSP server using stdio."""
        while self.running:
            try:
                # Read Content-Length header
                header = ''
                while True:
                    line = sys.stdin.readline()
                    if not line:
                        return
                    header += line
                    if header.endswith('\r\n\r\n'):
                        break
                
                # Parse Content-Length
                match = re.search(r'Content-Length: (\d+)', header)
                if not match:
                    continue
                
                content_length = int(match.group(1))
                content = sys.stdin.read(content_length)
                
                # Parse JSON
                message = json.loads(content)
                
                # Handle message
                response = self.handle_message(message)
                
                # Send response
                if response:
                    self._send_message(response)
                    
            except Exception as e:
                sys.stderr.write(f"LSP Error: {e}\n")
                sys.stderr.flush()


def main():
    """Entry point for the LSP server."""
    server = FlowLanguageServer()
    server.run()


if __name__ == '__main__':
    main()
