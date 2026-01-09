#!/usr/bin/env python3
"""
FLOW Language Parser
A simple recursive descent parser for the FLOW language
"""

import re
from typing import List, Dict, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum


class FlowSyntaxError(SyntaxError):
    """Enhanced syntax error with source context and suggestions."""
    
    def __init__(self, message: str, line: int = None, column: int = None, 
                 source: str = None, suggestion: str = None):
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
            lines = source.split('\n')
            if 0 < line <= len(lines):
                src_line = lines[line - 1]
                parts.append(f"\n  {line:4d} | {src_line}")
                if column:
                    parts.append(f"       | {' ' * (column - 1)}^")
        
        # Add suggestion if available
        if suggestion:
            parts.append(f"\n  Hint: {suggestion}")
        
        super().__init__('\n'.join(parts))


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
    RETURN = "RETURN"
    IF = "IF"
    ELSE = "ELSE"
    ELIF = "ELIF"
    WHILE = "WHILE"
    FOR = "FOR"
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
    ENUM = "ENUM"
    
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
    STRING = "STRING"
    VEC = "VEC"
    
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
    DOUBLE_COLON = "DOUBLE_COLON"
    FAT_ARROW = "FAT_ARROW"
    
    # Operators
    PLUS = "PLUS"
    MINUS = "MINUS"
    STAR = "STAR"
    SLASH = "SLASH"
    PERCENT = "PERCENT"
    PIPE = "PIPE"  # For lambdas: |x| { ... }
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
    size: Optional[int] = None
    element_type: Optional['Type'] = None
    type_args: Optional[List['Type']] = None  # Generic type arguments

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
    body: 'Block'
    attributes: List[str]
    is_exported: bool = False
    is_extern: bool = False
    type_params: List[str] = field(default_factory=list)  # Generic type parameters like <T, U>
    has_self: bool = False  # Whether this is a method with self parameter
    location: Optional[SourceLocation] = None  # For LSP go-to-definition

@dataclass
class VarDecl:
    name: str
    type: Type
    initializer: Optional['Expression']

@dataclass
class Block:
    statements: List['Statement']

@dataclass
class IfStatement:
    condition: 'Expression'
    then_block: Block
    elif_blocks: List[Tuple['Expression', Block]]
    else_block: Optional[Block]

@dataclass
class WhileStatement:
    condition: 'Expression'
    body: Block

@dataclass
class ForStatement:
    variable: str
    range_start: 'Expression'
    range_end: 'Expression'
    step: Optional['Expression']
    body: Block
    is_parallel: bool

@dataclass
class ReturnStatement:
    value: Optional['Expression']

@dataclass
class Assignment:
    target: str  # Simple variable name, or None if target_expr is used
    value: 'Expression'
    target_expr: Optional['Expression'] = None  # For array access like arr[i] = value

@dataclass
class FunctionCall:
    name: str
    arguments: List['Expression']

@dataclass
class Lambda:
    """Lambda/closure expression: |x: i32, y: i32| -> i32 { x + y }"""
    parameters: List[Parameter]
    return_type: Optional[Type]
    body: Union['Block', 'Expression']  # Can be block or single expression
    captures: List[str] = field(default_factory=list)  # Captured variables (for analysis)

@dataclass
class BinaryOperation:
    left: 'Expression'
    operator: str
    right: 'Expression'

@dataclass
class UnaryOperation:
    operator: str
    operand: 'Expression'

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
class FieldAccess:
    object: 'Expression'
    field: str

@dataclass
class ArrayLiteral:
    elements: List['Expression']

@dataclass
class VectorLiteral:
    elements: List['Expression']

@dataclass
class ArrayAccess:
    array: 'Expression'
    index: 'Expression'

@dataclass
class StructDecl:
    name: str
    fields: List[Parameter]
    is_exported: bool = False
    type_params: List[str] = field(default_factory=list)  # Generic type parameters like <T, U>
    location: Optional[SourceLocation] = None  # For LSP

@dataclass
class EnumVariant:
    """A variant of an enum: Some(T), None, Ok(T), Err(E)"""
    name: str
    fields: List[Type] = field(default_factory=list)  # Empty for unit variants, types for tuple variants

@dataclass
class EnumDecl:
    """Enum declaration: enum Option<T> { Some(T), None }"""
    name: str
    variants: List[EnumVariant]
    is_exported: bool = False
    type_params: List[str] = field(default_factory=list)

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
    type_params: List[str] = field(default_factory=list)

@dataclass
class ImplDecl:
    """Implementation block: impl Trait for Type { ... }"""
    trait_name: str
    for_type: Type
    methods: List['FunctionDecl']

@dataclass
class EffectDecl:
    name: str
    operations: List['EffectOperation']

@dataclass
class EffectOperation:
    name: str
    parameters: List[Parameter]
    return_type: Type

@dataclass
class CapabilityDecl:
    name: str
    effects: List[str]  # Names of effects this capability provides
    methods: List['CapabilityMethod']

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
    arguments: List['Expression']

@dataclass
class HandleStatement:
    effect: str
    handler: str  # Name of capability or function
    body: Block

@dataclass
class MatchStatement:
    value: 'Expression'
    cases: List['MatchCase']
    default_case: Optional[Block]

@dataclass
class MatchCase:
    pattern: 'Expression'  # Could be literal, struct pattern, etc.
    body: Block

@dataclass
class StructPattern:
    struct_name: str
    bindings: List[str]  # List of variable names to bind fields to

@dataclass
class ImportDecl:
    path: str

@dataclass
class ConstDecl:
    name: str
    type: Type
    value: 'Expression'
    is_exported: bool = False

@dataclass
class TestDecl:
    name: str
    body: Block

Expression = Union[Literal, Variable, BinaryOperation, UnaryOperation, FunctionCall, StructLiteral, FieldAccess, ArrayLiteral, VectorLiteral, ArrayAccess, EffectCall, StructPattern]
Statement = Union[VarDecl, Assignment, IfStatement, WhileStatement, ForStatement, ReturnStatement, Expression, EffectDecl, CapabilityDecl, HandleStatement, MatchStatement, ImportDecl, ConstDecl, TestDecl, TraitDecl, ImplDecl]

class Lexer:
    def __init__(self, text: str):
        self.text = text
        self._source = text  # Store for error messages
        self.pos = 0
        self.line = 1
        self.column = 1
        
        self.keyword_map = {
            'function': TokenType.FUNCTION,
            'let': TokenType.LET,
            'return': TokenType.RETURN,
            'if': TokenType.IF,
            'elif': TokenType.ELIF,
            'else': TokenType.ELSE,
            'while': TokenType.WHILE,
            'for': TokenType.FOR,
            'in': TokenType.IN,
            'parallel': TokenType.PARALLEL,
            'step': TokenType.STEP,
            'to': TokenType.TO,
            'match': TokenType.MATCH,
            'default': TokenType.DEFAULT,
            'test': TokenType.TEST,
            'trait': TokenType.TRAIT,
            'impl': TokenType.IMPL,
            'self': TokenType.SELF,
            'enum': TokenType.ENUM,
            'with': TokenType.WITH,
            'handle': TokenType.HANDLE,
            'effect': TokenType.EFFECT,
            'capability': TokenType.CAPABILITY,
            'import': TokenType.IMPORT,
            'export': TokenType.EXPORT,
            'extern': TokenType.EXTERN,
            'const': TokenType.CONST,
            'struct': TokenType.STRUCT,
            'and': TokenType.AND,
            'or': TokenType.OR,
            'not': TokenType.NOT,
            'true': TokenType.BOOLEAN,
            'false': TokenType.BOOLEAN,
            'void': TokenType.VOID,
            'i8': TokenType.I8,
            'i16': TokenType.I16,
            'i32': TokenType.I32,
            'i64': TokenType.I64,
            'i128': TokenType.I128,
            'u8': TokenType.U8,
            'u16': TokenType.U16,
            'u32': TokenType.U32,
            'u64': TokenType.U64,
            'u128': TokenType.U128,
            'f32': TokenType.F32,
            'f64': TokenType.F64,
            'bool': TokenType.BOOL,
            'string': TokenType.STRING,
            'vec': TokenType.VEC,
            'ptr': TokenType.IDENTIFIER,  # Will be handled in parse_type
            'array': TokenType.IDENTIFIER,  # Will be handled in parse_type
        }
        
        self.token_specifications = [
            (r'COMMENT', r'\#.*'),
            (r'NEWLINE', r'\n'),
            (r'WHITESPACE', r'\s+'),  # Skip whitespace
            (r'ARROW', r'->'),
            (r'FAT_ARROW', r'=>'),
            (r'EQUALS', r'=='),
            (r'NOT_EQUALS', r'!='),
            (r'LESS_EQUAL', r'<='),
            (r'GREATER_EQUAL', r'>='),
            (r'AND', r'&&'),
            (r'OR', r'\|\|'),
            (r'PIPE', r'\|'),
            (r'DOTDOT', r'\.\.'),
            (r'DOUBLE_COLON', r'::'),
            (r'PLUS', r'\+'),
            (r'MINUS', r'-'),
            (r'STAR', r'\*'),
            (r'SLASH', r'/'),
            (r'PERCENT', r'%'),
            (r'LESS', r'<'),
            (r'GREATER', r'>'),
            (r'ASSIGN', r'='),
            (r'NOT', r'!'),
            (r'LPAREN', r'\('),
            (r'RPAREN', r'\)'),
            (r'LBRACE', r'\{'),
            (r'RBRACE', r'\}'),
            (r'LBRACKET', r'\['),
            (r'RBRACKET', r'\]'),
            (r'SEMICOLON', r';'),
            (r'COLON', r':'),
            (r'COMMA', r','),
            (r'DOT', r'\.'),
            (r'STRING', r'"(?:[^"\\]|\\.)*"'),
            (r'NUMBER', r'0x[0-9a-fA-F]+|[0-9]+\.[0-9]+|[0-9]+'),
            (r'IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*'),
        ]
        
        self.token_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in self.token_specifications)
        self.get_token = re.compile(self.token_regex).match
    
    def next_token(self) -> Token:
        while self.pos < len(self.text):
            m = self.get_token(self.text, self.pos)
            if not m:
                raise SyntaxError(f"Unexpected character at line {self.line}, column {self.column}")
            
            token_type_name = m.lastgroup
            token_value = m.group(token_type_name)
            
            # Skip whitespace and comments
            if token_type_name not in ['WHITESPACE', 'COMMENT', 'NEWLINE']:
                token_type = getattr(TokenType, token_type_name)
                
                # Check if it's a keyword
                if token_type == TokenType.IDENTIFIER and token_value in self.keyword_map:
                    token_type = self.keyword_map[token_value]
                
                token = Token(token_type, token_value, self.line, self.column)
                
                # Update position
                self.pos = m.end()
                self.column += len(token_value)
                
                return token
            
            # Update position for whitespace and newlines
            self.pos = m.end()
            if token_type_name == 'NEWLINE':
                self.line += 1
                self.column = 1
            else:
                self.column += len(token_value)
        
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
        
class Parser:
    def __init__(self, lexer: Lexer, source: str = None):
        self.lexer = lexer
        self.source = source or getattr(lexer, '_source', '')
        self.current_token = self.lexer.next_token()
        self.lookahead = self.lexer.next_token()
        self.struct_names = set()
    
    def advance(self):
        self.current_token = self.lookahead
        self.lookahead = self.lexer.next_token()
    
    def error(self, message: str, suggestion: str = None) -> FlowSyntaxError:
        """Create a syntax error with context."""
        return FlowSyntaxError(
            message,
            line=self.current_token.line if self.current_token else None,
            column=self.current_token.column if hasattr(self.current_token, 'column') else None,
            source=self.source,
            suggestion=suggestion or get_suggestion(message)
        )
    
    def expect(self, token_type: TokenType):
        if self.current_token.type == token_type:
            token = self.current_token
            self.advance()
            return token
        else:
            msg = f"Expected {token_type}, got {self.current_token.type}"
            raise self.error(msg)
    
    def parse(self) -> List[Union[FunctionDecl, EffectDecl, CapabilityDecl, StructDecl, ImportDecl, ConstDecl]]:
        declarations = []
        while self.current_token.type != TokenType.EOF:
            is_exported = False
            if self.current_token.type == TokenType.EXPORT:
                is_exported = True
                self.advance()
            
            if self.current_token.type == TokenType.FUNCTION:
                decl = self.parse_function()
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
                if is_exported:
                    raise SyntaxError(f"Cannot export an import at line {self.current_token.line}")
                declarations.append(self.parse_import())
            elif self.current_token.type == TokenType.CONST:
                decl = self.parse_const()
                decl.is_exported = is_exported
                declarations.append(decl)
            elif self.current_token.type == TokenType.TEST:
                if is_exported:
                    raise SyntaxError(f"Cannot export a test declaration at line {self.current_token.line}")
                declarations.append(self.parse_test())
            elif self.current_token.type == TokenType.EXTERN:
                if is_exported:
                    raise SyntaxError(f"Cannot export an extern declaration at line {self.current_token.line}")
                declarations.append(self.parse_extern())
            elif self.current_token.type == TokenType.TRAIT:
                decl = self.parse_trait()
                declarations.append(decl)
            elif self.current_token.type == TokenType.IMPL:
                decl = self.parse_impl()
                declarations.append(decl)
            else:
                raise SyntaxError(f"Unexpected declaration: {self.current_token.type}")
        return declarations

    def parse_import(self) -> ImportDecl:
        self.expect(TokenType.IMPORT)
        path_token = self.expect(TokenType.STRING)
        # Strip quotes
        path = path_token.value[1:-1]
        return ImportDecl(path)
    
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

    def parse_test(self) -> FunctionDecl:
        self.expect(TokenType.TEST)
        name_token = self.expect(TokenType.STRING)
        name = "test_" + name_token.value[1:-1].replace(" ", "_")  # Remove quotes, make valid identifier
        body = self.parse_block()

        # Create a function that returns bool
        return_type = Type("bool")
        parameters = []  # No parameters for tests

        return FunctionDecl(name, parameters, return_type, body, ["test"])
    
    def parse_extern(self) -> FunctionDecl:
        """Parse extern function declaration"""
        self.expect(TokenType.EXTERN)
        
        # Parse extern block: extern "module" { function declarations }
        if self.current_token.type == TokenType.STRING:
            # Skip the module name for now
            self.advance()
        
        self.expect(TokenType.LBRACE)
        
        functions = []
        while self.current_token.type != TokenType.RBRACE:
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
                raise SyntaxError(f"Expected function declaration in extern block at line {self.current_token.line}")
        
        self.expect(TokenType.RBRACE)
        
        # Return the first function for now (extern blocks usually contain one function)
        return functions[0] if functions else None
    
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
            end_column=name_token.column - 1 + len(name)
        )
        return StructDecl(name, fields, type_params=type_params, location=loc)
    
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
                raise SyntaxError(f"Expected 'function' in trait body, got {self.current_token.type}")
        
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
            raise SyntaxError(f"Expected 'for' after trait name in impl, got {self.current_token.type}")
        
        for_type = self.parse_type()
        
        self.expect(TokenType.LBRACE)
        
        methods = []
        while self.current_token.type != TokenType.RBRACE:
            if self.current_token.type == TokenType.FUNCTION:
                method = self.parse_function()
                methods.append(method)
            else:
                raise SyntaxError(f"Expected 'function' in impl body, got {self.current_token.type}")
        
        self.expect(TokenType.RBRACE)
        return ImplDecl(trait_name, for_type, methods)
    
    def parse_function(self) -> FunctionDecl:
        start_token = self.current_token
        self.expect(TokenType.FUNCTION)
        name_token = self.current_token
        name = self.expect(TokenType.IDENTIFIER).value
        
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
        
        body = self.parse_block()
        
        # Create location from start token (0-based for LSP)
        loc = SourceLocation(
            line=start_token.line - 1,  # Convert to 0-based
            column=start_token.column - 1,
            end_line=name_token.line - 1,
            end_column=name_token.column - 1 + len(name)
        )
        
        fn = FunctionDecl(name, parameters, return_type, body, [], type_params=type_params, location=loc)
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
    
    def parse_type(self) -> Type:
        # Check for generic types first (array<T>, ptr<T>, etc.)
        if self.current_token.type in [TokenType.IDENTIFIER, TokenType.I8, TokenType.I16, TokenType.I32, TokenType.I64, TokenType.I128,
                                       TokenType.U8, TokenType.U16, TokenType.U32, TokenType.U64, TokenType.U128, TokenType.F32, TokenType.F64]:
            type_name = self.current_token.value
            self.advance()
            
            # Check for generic array type: array<T, N> or array<T>
            if type_name == 'array' and self.current_token.type == TokenType.LESS:
                self.advance()  # consume <
                element_type = self.parse_type()
                if self.current_token.type == TokenType.COMMA:
                    self.advance()  # consume ,
                    size = int(self.expect(TokenType.NUMBER).value)
                    self.expect(TokenType.GREATER)
                    return Type(f"array_{size}_{element_type.name}", size=size, element_type=element_type)
                else:
                    self.expect(TokenType.GREATER)
                    return Type(f"array_{element_type.name}", element_type=element_type)
            # Check for pointer type: ptr<T>
            elif type_name == 'ptr' and self.current_token.type == TokenType.LESS:
                self.advance()  # consume <
                pointee_type = self.parse_type()
                self.expect(TokenType.GREATER)
                return Type(f"ptr_{pointee_type.name}", is_pointer=True, element_type=pointee_type)
            # Check for vector type: vec4<T>
            elif type_name.startswith('vec') and self.current_token.type == TokenType.LESS:
                self.advance()  # consume <
                element_type = self.parse_type()
                self.expect(TokenType.GREATER)
                # Extract size from vec4, vec8, etc.
                size_str = type_name[3:]  # Remove 'vec' prefix
                try:
                    size = int(size_str)
                    return Type(f"vec{size}_{element_type.name}", size=size, element_type=element_type)
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
                type_args_str = '_'.join(t.name for t in type_args)
                return Type(f"{type_name}_{type_args_str}", type_args=type_args)
            else:
                # Simple type (or type variable like T)
                return Type(type_name)
        
        elif self.current_token.type in [TokenType.I8, TokenType.I16, TokenType.I32, TokenType.I64, TokenType.I128,
                                       TokenType.U8, TokenType.U16, TokenType.U32, TokenType.U64, TokenType.U128,
                                       TokenType.F32, TokenType.F64, TokenType.BOOL, TokenType.VOID, TokenType.STRING]:
            type_name = self.current_token.value
            self.advance()
            return Type(type_name)
        
        elif self.current_token.type == TokenType.VEC:
            self.advance()
            size = int(self.expect(TokenType.NUMBER).value)
            element_type = self.parse_type()
            return Type(f"vec{size}_{element_type.name}", size=size, element_type=element_type)
        
        elif self.current_token.type == TokenType.LBRACKET:
            self.advance()
            element_type = self.parse_type()
            self.expect(TokenType.SEMICOLON)
            size = int(self.expect(TokenType.NUMBER).value)
            self.expect(TokenType.RBRACKET)
            return Type(f"array_{size}_{element_type.name}", size=size, element_type=element_type)
        
        else:
            raise SyntaxError(f"Unexpected type token: {self.current_token.type}")
    
    def parse_block(self) -> Block:
        self.expect(TokenType.LBRACE)
        statements = []
        
        while self.current_token.type != TokenType.RBRACE:
            statements.append(self.parse_statement())
        
        self.expect(TokenType.RBRACE)
        return Block(statements)
    
    def parse_statement(self) -> Statement:
        if self.current_token.type == TokenType.LET:
            return self.parse_var_decl()
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
        elif self.current_token.type == TokenType.MATCH:
            return self.parse_match()
        else:
            return self.parse_expression_statement()
    
    def parse_effect(self) -> EffectDecl:
        self.expect(TokenType.EFFECT)
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.LBRACE)
        
        operations = []
        while self.current_token.type != TokenType.RBRACE:
            operations.append(self.parse_effect_operation())
            if self.current_token.type == TokenType.COMMA:
                self.advance()
        
        self.expect(TokenType.RBRACE)
        return EffectDecl(name, operations)
    
    def parse_effect_operation(self) -> EffectOperation:
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
                raise SyntaxError(f"Expected effect or function in capability, got {self.current_token.type}")
        
        self.expect(TokenType.RBRACE)
        return CapabilityDecl(name, effects, methods)
    
    def parse_capability_method(self) -> CapabilityMethod:
        method = self.parse_function()
        return CapabilityMethod(method.name, method.parameters, method.return_type, method.body)
    
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
        
        # For now, just store the first effect and handler (TODO: support multiple)
        return HandleStatement(effects[0], handlers[0], body)
    
    def parse_match(self) -> MatchStatement:
        self.expect(TokenType.MATCH)
        value = self.parse_expression_without_assign()
        self.expect(TokenType.LBRACE)
        
        cases = []
        default_case = None
        
        while self.current_token.type != TokenType.RBRACE:
            if self.current_token.type == TokenType.DEFAULT:
                self.advance()
                default_case = self.parse_block()
            else:
                pattern = self.parse_expression_without_assign()
                
                # Check for Struct Pattern syntax: Name(var1, var2)
                # This is currently parsed as a FunctionCall
                if isinstance(pattern, FunctionCall):
                    is_struct_pattern = True
                    bindings = []
                    for arg in pattern.arguments:
                        if isinstance(arg, Variable):
                            bindings.append(arg.name)
                        else:
                            # Not a simple variable binding (e.g. constant match Point(1, 2))
                            # For Phase 2, we only support bindings. Mixed patterns could be future work.
                            is_struct_pattern = False
                            break
                    
                    if is_struct_pattern:
                        pattern = StructPattern(pattern.name, bindings)
                
                self.expect(TokenType.FAT_ARROW)
                body = self.parse_block()
                cases.append(MatchCase(pattern, body))
                
                if self.current_token.type == TokenType.COMMA:
                    self.advance()
        
        self.expect(TokenType.RBRACE)
        return MatchStatement(value, cases, default_case)
    
    def parse_var_decl(self) -> VarDecl:
        self.expect(TokenType.LET)
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
            raise SyntaxError(f"Variable '{name}' requires either a type annotation or an initializer")
        
        # Semicolons are optional for backward compatibility
        if self.current_token.type == TokenType.SEMICOLON:
            self.advance()
        return VarDecl(name, var_type, initializer)
    
    def parse_return(self) -> ReturnStatement:
        self.expect(TokenType.RETURN)
        value = None
        if self.current_token.type not in [TokenType.RBRACE, TokenType.RPAREN, TokenType.SEMICOLON, TokenType.EOF, 
                                          TokenType.VOID, TokenType.I8, TokenType.I16, TokenType.I32, TokenType.I64, TokenType.I128,
                                          TokenType.U8, TokenType.U16, TokenType.U32, TokenType.U64, TokenType.U128,
                                          TokenType.F32, TokenType.F64, TokenType.BOOL]:
            # Check if it's a valid expression start
            if self.current_token.type in [TokenType.IDENTIFIER, TokenType.NUMBER, TokenType.BOOLEAN, 
                                         TokenType.LPAREN, TokenType.MINUS, TokenType.NOT, TokenType.STAR, TokenType.AND,
                                         TokenType.STRING, TokenType.LESS, TokenType.LBRACKET, TokenType.SELF]:
                value = self.parse_expression_without_assign()
        elif self.current_token.type == TokenType.VOID:
            # Explicit void return - consume the VOID token
            self.advance()
        
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
            raise SyntaxError(f"Expected '..' or 'to' in for range, got {self.current_token.type}")
        range_end = self.parse_expression_without_assign()
        
        step = None
        if self.current_token.type == TokenType.STEP:
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
        return self.parse_logical_or()
    
    def parse_assignment(self) -> Expression:
        expr = self.parse_logical_or()
        
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
            else:
                raise SyntaxError("Invalid assignment target")
        
        return expr
    
    def parse_logical_or(self) -> Expression:
        left = self.parse_logical_and()
        
        while self.current_token.type == TokenType.OR:
            op = self.current_token.value
            self.advance()
            right = self.parse_logical_and()
            left = BinaryOperation(left, op, right)
        
        return left
    
    def parse_logical_and(self) -> Expression:
        left = self.parse_equality()
        
        while self.current_token.type == TokenType.AND:
            op = self.current_token.value
            self.advance()
            right = self.parse_equality()
            left = BinaryOperation(left, op, right)
        
        return left
    
    def parse_equality(self) -> Expression:
        left = self.parse_comparison()
        
        while self.current_token.type in [TokenType.EQUALS, TokenType.NOT_EQUALS]:
            op = self.current_token.value
            self.advance()
            right = self.parse_comparison()
            left = BinaryOperation(left, op, right)
        
        return left
    
    def parse_comparison(self) -> Expression:
        left = self.parse_term()
        
        while self.current_token.type in [TokenType.LESS, TokenType.GREATER, TokenType.LESS_EQUAL, TokenType.GREATER_EQUAL]:
            op = self.current_token.value
            self.advance()
            right = self.parse_term()
            left = BinaryOperation(left, op, right)
        
        return left
    
    def parse_term(self) -> Expression:
        left = self.parse_factor()
        
        while self.current_token.type in [TokenType.PLUS, TokenType.MINUS]:
            op = self.current_token.value
            self.advance()
            right = self.parse_factor()
            left = BinaryOperation(left, op, right)
        
        return left
    
    def parse_factor(self) -> Expression:
        left = self.parse_unary()
        
        while self.current_token.type in [TokenType.STAR, TokenType.SLASH, TokenType.PERCENT]:
            op = self.current_token.value
            self.advance()
            right = self.parse_unary()
            left = BinaryOperation(left, op, right)
        
        return left
    
    def parse_unary(self) -> Expression:
        if self.current_token.type in [TokenType.MINUS, TokenType.NOT]:
            op = self.current_token.value
            self.advance()
            operand = self.parse_unary()
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
            if isinstance(value, str) and ('.' in value or 'e' in value.lower()):
                return Literal(value, Type("f32"))
            elif isinstance(value, str) and value.startswith('0x'):
                # Handle hex literals - convert to integer
                hex_value = int(value, 16)
                return Literal(str(hex_value), Type("i32"))
            return Literal(value, Type("i32"))  # Default to i32 for numbers
        
        elif self.current_token.type == TokenType.BOOLEAN:
            value = self.current_token.value
            self.advance()
            return Literal(value, Type("bool"))
        
        elif self.current_token.type == TokenType.STRING:
            value = self.current_token.value
            self.advance()
            return Literal(value, Type("string"))
        
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
        
        elif self.current_token.type == TokenType.IDENTIFIER:
            name = self.current_token.value
            self.advance()
            
            if self.current_token.type == TokenType.LPAREN:
                return self.parse_function_call(name)
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
                    type_args_str = '_'.join(t.name for t in type_args)
                    mangled_name = f"{name}_{type_args_str}"
                    
                    if self.current_token.type == TokenType.LPAREN:
                        # Generic function call: make_box<i32>(42)
                        return self.parse_function_call(mangled_name)
                    elif self.current_token.type == TokenType.LBRACE:
                        # Generic struct literal: Box<i32> { ... }
                        return self.parse_struct_literal(mangled_name)
                    else:
                        # Just a generic type in expression position (unusual but valid)
                        return Variable(mangled_name)
                except:
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
                except:
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
                # Array access: arr[index]
                expr = Variable(name)
                while self.current_token.type == TokenType.LBRACKET:
                    self.advance()  # consume [
                    index = self.parse_expression_without_assign()
                    self.expect(TokenType.RBRACKET)
                    expr = ArrayAccess(expr, index)
                return expr
            else:
                return Variable(name)
        
        elif self.current_token.type == TokenType.LPAREN:
            self.advance()
            expr = self.parse_expression_without_assign()
            self.expect(TokenType.RPAREN)
            return expr
        
        elif self.current_token.type == TokenType.PIPE:
            # Lambda expression: |x: i32, y: i32| -> i32 { x + y }
            # Or shorthand: |x| x * 2
            return self.parse_lambda()
        
        else:
            raise SyntaxError(f"Unexpected token in expression: {self.current_token.type}")
    
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
        
        return Lambda(parameters, return_type, body)
    
    def parse_struct_literal(self, struct_name: str) -> 'StructLiteral':
        # If current token is LBRACE, expect it and advance
        # Otherwise, we're already positioned correctly
        if self.current_token.type == TokenType.LBRACE:
            self.expect(TokenType.LBRACE)
        
        fields = []
        
        while self.current_token.type != TokenType.RBRACE:
            field_name = self.expect(TokenType.IDENTIFIER).value
            self.expect(TokenType.COLON)
            field_value = self.parse_expression_without_assign()
            fields.append((field_name, field_value))
            
            if self.current_token.type == TokenType.COMMA:
                self.advance()
        
        self.expect(TokenType.RBRACE)
        return StructLiteral(struct_name, fields)
    
    def parse_field_access(self, object_name: str) -> Expression:
        self.expect(TokenType.DOT)
        member_name = self.expect(TokenType.IDENTIFIER).value

        # Dotted call: EffectName.operation(args)
        if self.current_token.type == TokenType.LPAREN:
            self.expect(TokenType.LPAREN)
            arguments: List[Expression] = []

            if self.current_token.type != TokenType.RPAREN:
                arguments.append(self.parse_expression_without_assign())
                while self.current_token.type == TokenType.COMMA:
                    self.advance()
                    arguments.append(self.parse_expression_without_assign())

            self.expect(TokenType.RPAREN)
            return EffectCall(object_name, member_name, arguments)

        # Regular field access
        expr: Expression = FieldAccess(Variable(object_name), member_name)

        # Support chained access: a.b.c
        while self.current_token.type == TokenType.DOT:
            self.expect(TokenType.DOT)
            next_member = self.expect(TokenType.IDENTIFIER).value
            expr = FieldAccess(expr, next_member)

        return expr

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
            print(f"  Parameters: {[p.name + ':' + p.type.name for p in func.parameters]}")
            print(f"  Return type: {func.return_type.name}")
            print(f"  Statements: {len(func.body.statements)}")
    except SyntaxError as e:
        print(f"Syntax error: {e}")
