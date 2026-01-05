# Development Guide

This document provides detailed information for FLOW language developers.

## 🏗️ Architecture Overview

### Compiler Pipeline

```
FLOW Source → Parser → AST → C Backend → C Code → clang → Executable
                           └─→ MLIR Backend → MLIR (experimental)
```

### Core Components

#### Parser (`src/flow/parser.py`)
- **Tokenizer**: Regex-based tokenization with named groups
- **Parser**: Recursive descent parser for all language constructs
- **AST Nodes**: Dataclasses for syntax tree representation

#### C Backend (`src/flow/c_generator.py`)
- **Type System**: Maps FLOW types to C types
- **Struct Support**: Generates C structs with proper field ordering
- **Expression Generation**: Handles all expression types including field access

#### MLIR Backend (`src/flow/mlir_generator.py`)
- **Dialect Generation**: Emits MLIR func, arith, and cf dialects
- **Type Mapping**: Converts FLOW types to MLIR types
- **SSA Form**: Generates proper MLIR SSA values

## 🔧 Language Implementation

### Adding New Language Features

#### 1. Token Types
Add to `TokenType` enum in `parser.py`:
```python
class TokenType(Enum):
    # ... existing tokens ...
    NEW_KEYWORD = "NEW_KEYWORD"
```

#### 2. Tokenizer Rules
Add to `token_patterns` in `Lexer.__init__()`:
```python
self.token_patterns = [
    # ... existing patterns ...
    (r'newkeyword', TokenType.NEW_KEYWORD),
]
```

#### 3. Parser Methods
Add parsing methods in `Parser` class:
```python
def parse_new_construct(self) -> NewNode:
    # Implementation
    pass
```

#### 4. AST Nodes
Add dataclass for new node type:
```python
@dataclass
class NewNode:
    # Fields
    pass
```

#### 5. Backend Support
Add generation in both backends:

**C Backend** (`c_generator.py`):
```python
def _gen_expr(self, e: Expression) -> str:
    if isinstance(e, NewNode):
        return self._gen_new_node(e)
    # ... existing cases ...
```

**MLIR Backend** (`mlir_generator.py`):
```python
def generate_expression(self, expr: Expression) -> str:
    if isinstance(expr, NewNode):
        return self.generate_new_node(expr)
    # ... existing cases ...
```

### Type System

#### FLOW Types
- **Primitives**: `i32`, `bool`, `void`
- **Structs**: User-defined with field types
- **Future**: Arrays, pointers, functions

#### Type Inference
The C backend performs simple type inference:
- Track variable types in `_var_types`
- Infer struct field types from literals
- Handle nested struct dependencies

### Error Handling

#### Parse Errors
```python
raise SyntaxError(f"Unexpected token: {self.current_token.type}")
```

#### Generation Errors
```python
raise NotImplementedError(f"Unsupported expression: {type(expr)}")
```

## 🧪 Testing Strategy

### Test Categories

#### 1. Parsing Tests
Verify syntax is correctly parsed:
```bash
python3 -m flow.transpiler examples/new_feature.flow
```

#### 2. Generation Tests
Verify output code quality:
```bash
python3 -m flow.transpiler --c examples/new_feature.flow -o /tmp/test.c
```

#### 3. Runtime Tests
Verify program execution:
```bash
./flow run examples/new_feature.flow
```

### Test Organization

- **`examples/`**: Standard programs, algorithms, OOP patterns
- **`tests/`**: Compiler features, language demos, edge cases

## 📁 File Organization

### Source Layout
```
src/flow/
├── __init__.py          # Package initialization
├── transpiler.py        # Main CLI interface
├── parser.py            # Tokenizer and parser
├── c_generator.py       # C code generation
└── mlir_generator.py    # MLIR generation
```

### Build Artifacts
```
build/
├── *.c                  # Generated C code
├── *.mlir               # Generated MLIR
├── *.o                  # Object files
└── *                    # Executables
```

## 🔄 Development Workflow

### Making Changes
1. Identify component to modify
2. Add tests first
3. Implement changes
4. Verify with `./flow test`
5. Add documentation

### Debugging Tips

#### Parser Issues
- Check tokenization with debug prints
- Verify parse tree structure
- Look for missing `expect()` calls

#### Generation Issues
- Examine generated C/MLIR output
- Check type mappings
- Verify SSA form in MLIR

#### Runtime Issues
- Compile generated C manually
- Use debugger on C code
- Check exit codes

## 🚀 Performance Considerations

### Parser Performance
- Regex compilation is cached
- Linear tokenization time
- Recursive parsing depth limited by Python stack

### Generation Performance
- String building with lists
- Minimal type inference overhead
- Linear traversal of AST

## 🔮 Future Extensions

### Language Features
- Arrays and pointers
- String literals and I/O
- Module system
- Generic types

### Backend Improvements
- LLVM IR direct generation
- Optimization passes
- Better error messages

### Tooling
- Language server protocol
- IDE integration
- Package manager

## 📚 References

- [MLIR Documentation](https://mlir.llvm.org/)
- [LLVM IR Reference](https://llvm.org/docs/LangRef.html)
- [Python Packaging](https://packaging.python.org/)
- [Compiler Design](https://craftinginterpreters.com/)
