# Contributing to FLOW

Thank you for your interest in contributing to FLOW! This document provides guidelines for contributors.

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- clang (for C compilation)
- Optional: LLVM/MLIR tools (for MLIR features)

### Setup

```bash
git clone https://github.com/yourusername/flow-lang.git
cd flow-lang
```

### Running Tests

```bash
# Run all tests
./flow test

# Test specific examples
./flow run examples/factorial.flow
./flow run examples/oop_person.flow
```

## 🏗️ Architecture

- `src/flow/parser.py` - Recursive descent parser and tokenizer
- `src/flow/c_generator.py` - C code generation (production backend)
- `src/flow/mlir_generator.py` - MLIR generation (experimental)
- `src/flow/transpiler.py` - Main CLI interface

## 📝 Adding Features

### 1. Language Features

To add a new language feature:

1. **Tokenizer**: Add tokens in `parser.py` `TokenType` enum
2. **Parser**: Add parsing methods in `Parser` class
3. **C Backend**: Add generation in `c_generator.py`
4. **MLIR Backend**: Add generation in `mlir_generator.py` (optional)
5. **Tests**: Add examples in `examples/` or `tests/`

### 2. Examples

Add examples in appropriate folder:

- `examples/` - Standard programs (algorithms, OOP patterns)
- `tests/` - Compiler/language demos

### 3. Documentation

Update README.md and add comments to code.

## 🧪 Testing

### Test Categories

- **Parsing Tests**: Ensure syntax is correctly parsed
- **Generation Tests**: Verify C/MLIR output
- **Runtime Tests**: Check program execution results

### Running Tests

```bash
# All tests
./flow test

# Specific test
python3 -m flow.transpiler --c examples/new_feature.flow -o /tmp/test.c
clang /tmp/test.c -o /tmp/test && /tmp/test
```

## 📋 Code Style

- Python: Follow PEP 8
- FLOW: Use explicit types, clear naming
- Comments: Explain non-obvious logic
- Commits: Use clear, descriptive messages

## 🐛 Bug Reports

When reporting bugs:

1. Include minimal example
2. Show expected vs actual behavior
3. Include system information
4. Add error messages

## 🔒 Security Policy

Flow underwent a comprehensive security audit in February 2026. If you discover a security
vulnerability, please check the [open issues](https://github.com/flooooooooooow/flow/issues)
first -- it may already be tracked. Known security issues are labeled with `security` and
`critical`.

**Known open security issues** (as of v0.7.0):
- C generator: unsanitized identifiers (#20), printf format strings (#21), no bounds checking (#22)
- Stdlib: calloc integer overflow (#59), no real synchronization (#60)
- CI: overly broad token permissions (#89)
- Runtime: shell injection in osascript (#73)

For new security issues not already tracked, please open a GitHub issue with the `security` label.

## 📋 Issue Tracker

Issues use a structured naming convention: `[ID] Component: description`

**Severity labels:** `critical`, `medium`, `low`
**Category labels:** `compiler`, `stdlib`, `runtime`, `ci`, `testing`, `security`

When closing issues, always reference the fixing commit in a comment (e.g., "Fixed in abc1234").

## 💡 Feature Requests

Feature requests should:

1. Clearly describe the feature
2. Explain use case
3. Consider implementation complexity
4. Align with language goals

## 🔧 Development Workflow

1. Fork repository
2. Create feature branch
3. Make changes
4. Add tests
5. Verify `./flow test` passes
6. Submit pull request

## 📚 Resources

- [MLIR Documentation](https://mlir.llvm.org/)
- [LLVM Documentation](https://llvm.org/docs/)
- [Python Packaging](https://packaging.python.org/)

## 🤝 Community

- Be respectful and constructive
- Help others learn
- Share knowledge
- Have fun!

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.
