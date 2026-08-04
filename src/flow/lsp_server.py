#!/usr/bin/env python3
"""
FLOW Language Server Protocol (LSP) Implementation
Provides IntelliSense features: completion, hover, diagnostics, go-to-definition
"""

import json
import sys
import re
import threading
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from .parser import (
    Lexer, Parser, FunctionDecl, StructDecl, EnumDecl, TraitDecl,
    FlowSyntaxError, TokenType
)
from .type_checker import TypeChecker
from .lsp_dynamics import dynamics_completion_items, dynamics_hover
from .lsp_ordering import ordering_completion_items, ordering_hover
from .version import __version__ as _FLOW_VERSION

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
        self.running = True
        self._write_lock = threading.Lock()  # serializes stdout writes
        self._debounce_timers: Dict[str, threading.Timer] = {}  # uri -> pending analysis
        
        # Built-in types
        self.builtin_types = [
            'i8', 'i16', 'i32', 'i64', 'i128',
            'u8', 'u16', 'u32', 'u64', 'u128',
            'f32', 'f64', 'bool', 'void', 'string'
        ]
        
        # Built-in functions
        self.builtin_functions = {
            'print': {'params': ['value: any'], 'return': 'void', 'doc': 'Print a value to stdout'},
            'printf': {'params': ['format: string', '...'], 'return': 'void', 'doc': 'Print formatted output (C-style)'},
            'sqrt': {'params': ['x: f64'], 'return': 'f64', 'doc': 'Square root'},
            'sin': {'params': ['x: f64'], 'return': 'f64', 'doc': 'Sine function'},
            'cos': {'params': ['x: f64'], 'return': 'f64', 'doc': 'Cosine function'},
            'tan': {'params': ['x: f64'], 'return': 'f64', 'doc': 'Tangent function'},
            'exp': {'params': ['x: f64'], 'return': 'f64', 'doc': 'Exponential function'},
            'log': {'params': ['x: f64'], 'return': 'f64', 'doc': 'Natural logarithm'},
            'pow': {'params': ['x: f64', 'y: f64'], 'return': 'f64', 'doc': 'Power function'},
            'abs': {'params': ['x: i32'], 'return': 'i32', 'doc': 'Absolute value (integer)'},
            'fabs': {'params': ['x: f64'], 'return': 'f64', 'doc': 'Absolute value (float)'},
            'floor': {'params': ['x: f64'], 'return': 'f64', 'doc': 'Floor function'},
            'ceil': {'params': ['x: f64'], 'return': 'f64', 'doc': 'Ceiling function'},
            'tanh': {'params': ['x: f64'], 'return': 'f64', 'doc': 'Hyperbolic tangent'},
        }
        
        # Keywords (core language — dynamics DSL lives in lsp_dynamics snippets)
        self.keywords = [
            'function', 'let', 'mut', 'return', 'if', 'else', 'elif', 'while', 'for',
            'break', 'continue', 'parallel', 'in', 'step', 'struct', 'enum', 'trait',
            'impl', 'effect', 'capability', 'handle', 'with', 'match', 'default',
            'import', 'export', 'extern', 'const', 'module', 'test', 'self',
            'array', 'ptr', 'vec', 'true', 'false', 'theorem', 'assume', 'therefore',
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
            },
            'serverInfo': {
                'name': 'flow-lsp',
                'version': _FLOW_VERSION,
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
        """Analyze a document and extract symbols."""
        text = self.documents.get(uri, '')
        symbols = {}
        
        try:
            lexer = Lexer(text)
            parser = Parser(lexer, source=text)
            declarations = parser.parse()
            
            for decl in declarations:
                if isinstance(decl, FunctionDecl):
                    loc = decl.location
                    symbols[decl.name] = {
                        'kind': 'function',
                        'params': [(p.name, p.type.name) for p in decl.parameters],
                        'return': decl.return_type.name,
                        'line': loc.line if loc else 0,
                        'column': loc.column if loc else 0,
                        'end_line': loc.end_line if loc else 0,
                        'end_column': loc.end_column if loc else 0,
                    }
                elif isinstance(decl, StructDecl):
                    loc = decl.location
                    symbols[decl.name] = {
                        'kind': 'struct',
                        'fields': [(f.name, f.type.name) for f in decl.fields],
                        'line': loc.line if loc else 0,
                        'column': loc.column if loc else 0,
                        'end_line': loc.end_line if loc else 0,
                        'end_column': loc.end_column if loc else 0,
                    }
                elif isinstance(decl, EnumDecl):
                    symbols[decl.name] = {
                        'kind': 'enum',
                        'variants': [v.name for v in decl.variants],
                        'line': 0,
                        'column': 0,
                    }
                elif isinstance(decl, TraitDecl):
                    symbols[decl.name] = {
                        'kind': 'trait',
                        'methods': [m.name for m in decl.methods],
                        'line': 0,
                        'column': 0,
                    }
        except Exception:
            # Parse error - still store partial symbols
            pass

        self.symbols[uri] = symbols

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def _publish_diagnostics(self, uri: str):
        """Compute diagnostics for a document and push them to the client."""
        text = self.documents.get(uri)
        if text is None:
            return
        diagnostics = self._compute_diagnostics(text)
        self._send_notification('textDocument/publishDiagnostics', {
            'uri': uri,
            'diagnostics': diagnostics,
        })

    def _compute_diagnostics(self, text: str) -> List[dict]:
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

        # Phase 2: type check (findings are strings without locations, so we
        # locate the first identifier the message quotes to place the range)
        try:
            checker = TypeChecker()
            result = checker.check(declarations)
            seen = set()
            for err in result.errors:
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

        # Add document symbols
        doc_symbols = self.symbols.get(uri, {})
        for name, info in doc_symbols.items():
            if name in seen:
                continue
            if prefix and not name.startswith(prefix):
                continue
            if info['kind'] == 'function':
                params_str = ', '.join([f"{p[0]}: {p[1]}" for p in info['params']])
                items.append({
                    'label': name,
                    'kind': 3,  # Function
                    'detail': f"({params_str}) -> {info['return']}",
                })
            elif info['kind'] == 'struct':
                items.append({
                    'label': name,
                    'kind': 22,  # Struct
                    'detail': 'struct',
                })
            elif info['kind'] == 'enum':
                items.append({
                    'label': name,
                    'kind': 10,  # Enum
                    'detail': 'enum',
                })
            elif info['kind'] == 'trait':
                items.append({
                    'label': name,
                    'kind': 8,  # Interface
                    'detail': 'trait',
                })
            seen.add(name)

        # Also add symbols from other open documents
        for other_uri, other_symbols in self.symbols.items():
            if other_uri != uri:
                for name, info in other_symbols.items():
                    if name in seen:
                        continue
                    if prefix and not name.startswith(prefix):
                        continue
                    if info['kind'] == 'function':
                        params_str = ', '.join([f"{p[0]}: {p[1]}" for p in info['params']])
                        items.append({
                            'label': name,
                            'kind': 3,
                            'detail': f"({params_str}) -> {info['return']}",
                        })
                    elif info['kind'] == 'struct':
                        items.append({
                            'label': name,
                            'kind': 22,
                            'detail': 'struct',
                        })
                    seen.add(name)

        return items
    
    def _handle_hover(self, params: dict) -> Optional[dict]:
        """Handle textDocument/hover."""
        uri = params['textDocument']['uri']
        pos = params['position']
        
        text = self.documents.get(uri, '')
        word = self._get_word_at_position(text, pos['line'], pos['character'])
        
        if not word:
            return None

        dyn_doc = dynamics_hover(word)
        if dyn_doc:
            return {
                'contents': {
                    'kind': 'markdown',
                    'value': dyn_doc,
                }
            }

        ord_doc = ordering_hover(word)
        if ord_doc:
            return {
                'contents': {
                    'kind': 'markdown',
                    'value': ord_doc,
                }
            }

        # Check built-in functions
        if word in self.builtin_functions:
            info = self.builtin_functions[word]
            return {
                'contents': {
                    'kind': 'markdown',
                    'value': f"```flow\nfunction {word}({', '.join(info['params'])}) -> {info['return']}\n```\n\n{info.get('doc', '')}"
                }
            }
        
        # Check built-in types
        if word in self.builtin_types:
            type_docs = {
                'i32': 'Signed 32-bit integer',
                'i64': 'Signed 64-bit integer',
                'f32': 'Single-precision floating point',
                'f64': 'Double-precision floating point',
                'bool': 'Boolean (true/false)',
                'void': 'No return value',
                'string': 'UTF-8 string',
            }
            doc = type_docs.get(word, 'Built-in type')
            return {
                'contents': {
                    'kind': 'markdown',
                    'value': f"**{word}**\n\n{doc}"
                }
            }
        
        # Check document symbols in current file
        doc_symbols = self.symbols.get(uri, {})
        hover_info = self._get_hover_for_symbol(word, doc_symbols)
        if hover_info:
            return hover_info
        
        # Check symbols in all open documents
        for other_uri, other_symbols in self.symbols.items():
            if other_uri != uri:
                hover_info = self._get_hover_for_symbol(word, other_symbols)
                if hover_info:
                    return hover_info
        
        return None
    
    def _get_hover_for_symbol(self, word: str, symbols: Dict) -> Optional[dict]:
        """Generate hover content for a symbol."""
        if word not in symbols:
            return None
        
        info = symbols[word]
        if info['kind'] == 'function':
            params_str = ', '.join([f"{p[0]}: {p[1]}" for p in info['params']])
            return {
                'contents': {
                    'kind': 'markdown',
                    'value': f"```flow\nfunction {word}({params_str}) -> {info['return']}\n```"
                }
            }
        elif info['kind'] == 'struct':
            fields_str = '\n'.join([f"    {f[0]}: {f[1]}" for f in info['fields']])
            return {
                'contents': {
                    'kind': 'markdown',
                    'value': f"```flow\nstruct {word} {{\n{fields_str}\n}}\n```"
                }
            }
        elif info['kind'] == 'enum':
            variants_str = ', '.join(info.get('variants', []))
            return {
                'contents': {
                    'kind': 'markdown',
                    'value': f"```flow\nenum {word} {{ {variants_str} }}\n```"
                }
            }
        elif info['kind'] == 'trait':
            methods_str = ', '.join(info.get('methods', []))
            return {
                'contents': {
                    'kind': 'markdown',
                    'value': f"```flow\ntrait {word} {{\n  // methods: {methods_str}\n}}\n```"
                }
            }
        return None
    
    def _handle_definition(self, params: dict) -> Optional[dict]:
        """Handle textDocument/definition."""
        uri = params['textDocument']['uri']
        pos = params['position']
        
        text = self.documents.get(uri, '')
        word = self._get_word_at_position(text, pos['line'], pos['character'])
        
        if not word:
            return None
        
        # Check document symbols in current file
        doc_symbols = self.symbols.get(uri, {})
        if word in doc_symbols:
            info = doc_symbols[word]
            line = info.get('line', 0)
            column = info.get('column', 0)
            end_column = info.get('end_column', column + len(word))
            return {
                'uri': uri,
                'range': {
                    'start': {'line': line, 'character': column},
                    'end': {'line': line, 'character': end_column},
                }
            }
        
        # Check symbols in all open documents (cross-file go-to-definition)
        for other_uri, other_symbols in self.symbols.items():
            if other_uri != uri and word in other_symbols:
                info = other_symbols[word]
                line = info.get('line', 0)
                column = info.get('column', 0)
                end_column = info.get('end_column', column + len(word))
                return {
                    'uri': other_uri,
                    'range': {
                        'start': {'line': line, 'character': column},
                        'end': {'line': line, 'character': end_column},
                    }
                }
        
        return None
    
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
        }
        
        symbols = []
        for name, info in doc_symbols.items():
            kind = kind_map.get(info['kind'], 12)
            line = info.get('line', 0)
            column = info.get('column', 0)
            end_column = info.get('end_column', column + len(name))
            
            symbols.append({
                'name': name,
                'kind': kind,
                'range': {
                    'start': {'line': line, 'character': column},
                    'end': {'line': line, 'character': end_column + 50},  # Approximate end
                },
                'selectionRange': {
                    'start': {'line': line, 'character': column},
                    'end': {'line': line, 'character': end_column},
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

    def _resolve_symbol(self, uri: str, word: str):
        """Resolve word against the symbol indexes the same way definition
        does: current file first, then any other open document.

        Returns (decl_uri, decl_info) or (None, None) for local names.
        """
        if word in self.symbols.get(uri, {}):
            return uri, self.symbols[uri][word]
        for other_uri, other_symbols in self.symbols.items():
            if other_uri != uri and word in other_symbols:
                return other_uri, other_symbols[word]
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
