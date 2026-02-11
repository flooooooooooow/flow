#!/usr/bin/env python3
"""
FLOW Language Server Protocol (LSP) Implementation
Provides IntelliSense features: completion, hover, diagnostics, go-to-definition
"""

import json
import sys
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from .parser import Lexer, Parser, FunctionDecl, StructDecl, EnumDecl, TraitDecl


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


class FlowLanguageServer:
    """LSP server for FLOW language."""

    def __init__(self):
        self.documents: Dict[str, str] = {}  # uri -> content
        self.symbols: Dict[str, Dict[str, Any]] = {}  # uri -> {name: symbol_info}
        self.running = True

        # Built-in types
        self.builtin_types = [
            "i8",
            "i16",
            "i32",
            "i64",
            "i128",
            "u8",
            "u16",
            "u32",
            "u64",
            "u128",
            "f32",
            "f64",
            "bool",
            "void",
            "string",
        ]

        # Built-in functions
        self.builtin_functions = {
            "print": {
                "params": ["value: any"],
                "return": "void",
                "doc": "Print a value to stdout",
            },
            "printf": {
                "params": ["format: string", "..."],
                "return": "void",
                "doc": "Print formatted output (C-style)",
            },
            "sqrt": {"params": ["x: f64"], "return": "f64", "doc": "Square root"},
            "sin": {"params": ["x: f64"], "return": "f64", "doc": "Sine function"},
            "cos": {"params": ["x: f64"], "return": "f64", "doc": "Cosine function"},
            "tan": {"params": ["x: f64"], "return": "f64", "doc": "Tangent function"},
            "exp": {
                "params": ["x: f64"],
                "return": "f64",
                "doc": "Exponential function",
            },
            "log": {"params": ["x: f64"], "return": "f64", "doc": "Natural logarithm"},
            "pow": {
                "params": ["x: f64", "y: f64"],
                "return": "f64",
                "doc": "Power function",
            },
            "abs": {
                "params": ["x: i32"],
                "return": "i32",
                "doc": "Absolute value (integer)",
            },
            "fabs": {
                "params": ["x: f64"],
                "return": "f64",
                "doc": "Absolute value (float)",
            },
            "floor": {"params": ["x: f64"], "return": "f64", "doc": "Floor function"},
            "ceil": {"params": ["x: f64"], "return": "f64", "doc": "Ceiling function"},
            "tanh": {
                "params": ["x: f64"],
                "return": "f64",
                "doc": "Hyperbolic tangent",
            },
        }

        # Keywords
        self.keywords = [
            "function",
            "let",
            "return",
            "if",
            "else",
            "elif",
            "while",
            "for",
            "parallel",
            "in",
            "step",
            "struct",
            "enum",
            "trait",
            "impl",
            "effect",
            "capability",
            "handle",
            "with",
            "match",
            "default",
            "import",
            "export",
            "extern",
            "const",
            "module",
            "test",
            "self",
            "array",
            "ptr",
            "vec",
            "true",
            "false",
        ]

    def handle_message(self, message: dict) -> Optional[dict]:
        """Handle an incoming LSP message."""
        method = message.get("method", "")
        params = message.get("params", {})
        msg_id = message.get("id")

        result = None

        if method == "initialize":
            result = self._handle_initialize(params)
        elif method == "initialized":
            pass  # No response needed
        elif method == "shutdown":
            self.running = False
            result = None
        elif method == "exit":
            sys.exit(0)
        elif method == "textDocument/didOpen":
            self._handle_did_open(params)
        elif method == "textDocument/didChange":
            self._handle_did_change(params)
        elif method == "textDocument/didClose":
            self._handle_did_close(params)
        elif method == "textDocument/completion":
            result = self._handle_completion(params)
        elif method == "textDocument/hover":
            result = self._handle_hover(params)
        elif method == "textDocument/definition":
            result = self._handle_definition(params)
        elif method == "textDocument/documentSymbol":
            result = self._handle_document_symbol(params)

        if msg_id is not None:
            return {"jsonrpc": "2.0", "id": msg_id, "result": result}
        return None

    def _handle_initialize(self, params: dict) -> dict:
        """Handle initialize request."""
        return {
            "capabilities": {
                "textDocumentSync": {
                    "openClose": True,
                    "change": 1,  # Full sync
                },
                "completionProvider": {
                    "triggerCharacters": [".", ":", "<"],
                    "resolveProvider": False,
                },
                "hoverProvider": True,
                "definitionProvider": True,
                "documentSymbolProvider": True,
            },
            "serverInfo": {
                "name": "flow-lsp",
                "version": "0.1.0",
            },
        }

    def _handle_did_open(self, params: dict):
        """Handle textDocument/didOpen."""
        uri = params["textDocument"]["uri"]
        text = params["textDocument"]["text"]
        self.documents[uri] = text
        self._analyze_document(uri)

    def _handle_did_change(self, params: dict):
        """Handle textDocument/didChange."""
        uri = params["textDocument"]["uri"]
        changes = params.get("contentChanges", [])
        if changes:
            self.documents[uri] = changes[0]["text"]
            self._analyze_document(uri)

    def _handle_did_close(self, params: dict):
        """Handle textDocument/didClose."""
        uri = params["textDocument"]["uri"]
        self.documents.pop(uri, None)
        self.symbols.pop(uri, None)

    def _analyze_document(self, uri: str):
        """Analyze a document and extract symbols."""
        text = self.documents.get(uri, "")
        symbols = {}

        try:
            lexer = Lexer(text)
            parser = Parser(lexer, source=text)
            declarations = parser.parse()

            for decl in declarations:
                if isinstance(decl, FunctionDecl):
                    loc = decl.location
                    symbols[decl.name] = {
                        "kind": "function",
                        "params": [(p.name, p.type.name) for p in decl.parameters],
                        "return": decl.return_type.name,
                        "line": loc.line if loc else 0,
                        "column": loc.column if loc else 0,
                        "end_line": loc.end_line if loc else 0,
                        "end_column": loc.end_column if loc else 0,
                    }
                elif isinstance(decl, StructDecl):
                    loc = decl.location
                    symbols[decl.name] = {
                        "kind": "struct",
                        "fields": [(f.name, f.type.name) for f in decl.fields],
                        "line": loc.line if loc else 0,
                        "column": loc.column if loc else 0,
                        "end_line": loc.end_line if loc else 0,
                        "end_column": loc.end_column if loc else 0,
                    }
                elif isinstance(decl, EnumDecl):
                    symbols[decl.name] = {
                        "kind": "enum",
                        "variants": [v.name for v in decl.variants],
                        "line": 0,
                        "column": 0,
                    }
                elif isinstance(decl, TraitDecl):
                    symbols[decl.name] = {
                        "kind": "trait",
                        "methods": [m.name for m in decl.methods],
                        "line": 0,
                        "column": 0,
                    }
        except Exception:
            # Parse error - still store partial symbols
            pass

        self.symbols[uri] = symbols

    def _handle_completion(self, params: dict) -> List[dict]:
        """Handle textDocument/completion."""
        uri = params["textDocument"]["uri"]
        _pos = params["position"]

        items = []

        # Add keywords
        for kw in self.keywords:
            items.append(
                {
                    "label": kw,
                    "kind": 14,  # Keyword
                    "detail": "keyword",
                }
            )

        # Add types
        for t in self.builtin_types:
            items.append(
                {
                    "label": t,
                    "kind": 21,  # TypeParameter
                    "detail": "type",
                }
            )

        # Add built-in functions
        for name, info in self.builtin_functions.items():
            items.append(
                {
                    "label": name,
                    "kind": 3,  # Function
                    "detail": f"({', '.join(info['params'])}) -> {info['return']}",
                    "documentation": info.get("doc", ""),
                }
            )

        # Add document symbols
        doc_symbols = self.symbols.get(uri, {})
        for name, info in doc_symbols.items():
            if info["kind"] == "function":
                params_str = ", ".join([f"{p[0]}: {p[1]}" for p in info["params"]])
                items.append(
                    {
                        "label": name,
                        "kind": 3,  # Function
                        "detail": f"({params_str}) -> {info['return']}",
                    }
                )
            elif info["kind"] == "struct":
                items.append(
                    {
                        "label": name,
                        "kind": 22,  # Struct
                        "detail": "struct",
                    }
                )
            elif info["kind"] == "enum":
                items.append(
                    {
                        "label": name,
                        "kind": 10,  # Enum
                        "detail": "enum",
                    }
                )
            elif info["kind"] == "trait":
                items.append(
                    {
                        "label": name,
                        "kind": 8,  # Interface
                        "detail": "trait",
                    }
                )

        # Also add symbols from other open documents
        for other_uri, other_symbols in self.symbols.items():
            if other_uri != uri:
                for name, info in other_symbols.items():
                    if info["kind"] == "function":
                        params_str = ", ".join(
                            [f"{p[0]}: {p[1]}" for p in info["params"]]
                        )
                        items.append(
                            {
                                "label": name,
                                "kind": 3,
                                "detail": f"({params_str}) -> {info['return']}",
                            }
                        )
                    elif info["kind"] == "struct":
                        items.append(
                            {
                                "label": name,
                                "kind": 22,
                                "detail": "struct",
                            }
                        )

        return items

    def _handle_hover(self, params: dict) -> Optional[dict]:
        """Handle textDocument/hover."""
        uri = params["textDocument"]["uri"]
        _pos = params["position"]

        text = self.documents.get(uri, "")
        word = self._get_word_at_position(text, _pos["line"], _pos["character"])

        if not word:
            return None

        # Check built-in functions
        if word in self.builtin_functions:
            info = self.builtin_functions[word]
            return {
                "contents": {
                    "kind": "markdown",
                    "value": f"```flow\nfunction {word}({', '.join(info['params'])}) -> {info['return']}\n```\n\n{info.get('doc', '')}",
                }
            }

        # Check built-in types
        if word in self.builtin_types:
            type_docs = {
                "i32": "Signed 32-bit integer",
                "i64": "Signed 64-bit integer",
                "f32": "Single-precision floating point",
                "f64": "Double-precision floating point",
                "bool": "Boolean (true/false)",
                "void": "No return value",
                "string": "UTF-8 string",
            }
            doc = type_docs.get(word, "Built-in type")
            return {"contents": {"kind": "markdown", "value": f"**{word}**\n\n{doc}"}}

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
        if info["kind"] == "function":
            params_str = ", ".join([f"{p[0]}: {p[1]}" for p in info["params"]])
            return {
                "contents": {
                    "kind": "markdown",
                    "value": f"```flow\nfunction {word}({params_str}) -> {info['return']}\n```",
                }
            }
        elif info["kind"] == "struct":
            fields_str = "\n".join([f"    {f[0]}: {f[1]}" for f in info["fields"]])
            return {
                "contents": {
                    "kind": "markdown",
                    "value": f"```flow\nstruct {word} {{\n{fields_str}\n}}\n```",
                }
            }
        elif info["kind"] == "enum":
            variants_str = ", ".join(info.get("variants", []))
            return {
                "contents": {
                    "kind": "markdown",
                    "value": f"```flow\nenum {word} {{ {variants_str} }}\n```",
                }
            }
        elif info["kind"] == "trait":
            methods_str = ", ".join(info.get("methods", []))
            return {
                "contents": {
                    "kind": "markdown",
                    "value": f"```flow\ntrait {word} {{\n  // methods: {methods_str}\n}}\n```",
                }
            }
        return None

    def _handle_definition(self, params: dict) -> Optional[dict]:
        """Handle textDocument/definition."""
        uri = params["textDocument"]["uri"]
        _pos = params["position"]

        text = self.documents.get(uri, "")
        word = self._get_word_at_position(text, _pos["line"], _pos["character"])

        if not word:
            return None

        # Check document symbols in current file
        doc_symbols = self.symbols.get(uri, {})
        if word in doc_symbols:
            info = doc_symbols[word]
            line = info.get("line", 0)
            column = info.get("column", 0)
            end_column = info.get("end_column", column + len(word))
            return {
                "uri": uri,
                "range": {
                    "start": {"line": line, "character": column},
                    "end": {"line": line, "character": end_column},
                },
            }

        # Check symbols in all open documents (cross-file go-to-definition)
        for other_uri, other_symbols in self.symbols.items():
            if other_uri != uri and word in other_symbols:
                info = other_symbols[word]
                line = info.get("line", 0)
                column = info.get("column", 0)
                end_column = info.get("end_column", column + len(word))
                return {
                    "uri": other_uri,
                    "range": {
                        "start": {"line": line, "character": column},
                        "end": {"line": line, "character": end_column},
                    },
                }

        return None

    def _handle_document_symbol(self, params: dict) -> List[dict]:
        """Handle textDocument/documentSymbol."""
        uri = params["textDocument"]["uri"]
        doc_symbols = self.symbols.get(uri, {})

        # Symbol kinds: 12=Function, 23=Struct, 10=Enum, 11=Interface(trait)
        kind_map = {
            "function": 12,
            "struct": 23,
            "enum": 10,
            "trait": 11,
        }

        symbols = []
        for name, info in doc_symbols.items():
            kind = kind_map.get(info["kind"], 12)
            line = info.get("line", 0)
            column = info.get("column", 0)
            end_column = info.get("end_column", column + len(name))

            symbols.append(
                {
                    "name": name,
                    "kind": kind,
                    "range": {
                        "start": {"line": line, "character": column},
                        "end": {
                            "line": line,
                            "character": end_column + 50,
                        },  # Approximate end
                    },
                    "selectionRange": {
                        "start": {"line": line, "character": column},
                        "end": {"line": line, "character": end_column},
                    },
                }
            )

        return symbols

    def _get_word_at_position(self, text: str, line: int, character: int) -> str:
        """Get the word at a given position in the text."""
        lines = text.split("\n")
        if line >= len(lines):
            return ""

        line_text = lines[line]
        if character >= len(line_text):
            return ""

        # Find word boundaries
        start = character
        while start > 0 and (
            line_text[start - 1].isalnum() or line_text[start - 1] == "_"
        ):
            start -= 1

        end = character
        while end < len(line_text) and (
            line_text[end].isalnum() or line_text[end] == "_"
        ):
            end += 1

        return line_text[start:end]

    def run(self):
        """Run the LSP server using stdio."""
        while self.running:
            try:
                # Read Content-Length header
                header = ""
                while True:
                    line = sys.stdin.readline()
                    if not line:
                        return
                    header += line
                    if header.endswith("\r\n\r\n"):
                        break

                # Parse Content-Length
                match = re.search(r"Content-Length: (\d+)", header)
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
                    response_str = json.dumps(response)
                    sys.stdout.write(
                        f"Content-Length: {len(response_str)}\r\n\r\n{response_str}"
                    )
                    sys.stdout.flush()

            except Exception as e:
                sys.stderr.write(f"LSP Error: {e}\n")
                sys.stderr.flush()


def main():
    """Entry point for the LSP server."""
    server = FlowLanguageServer()
    server.run()


if __name__ == "__main__":
    main()
