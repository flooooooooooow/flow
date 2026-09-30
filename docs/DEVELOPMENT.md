# Development Guide

This document provides detailed information for FLOW language developers.

## Architecture Overview

### Compiler Pipeline

```
FLOW Source → Parser → AST → C Backend → C Code → clang → Executable
                           └─→ MLIR Backend → MLIR ─→ LLVM IR → clang → Executable
                                                   └─→ LLVM IR (wasm32) → clang → .wasm
```

### Core Components

The compiler is flowc, written in Flow under `compiler/src/` and built from
the checked-in C in `compiler/bootstrap/`. See
[compiler/README.md](../compiler/README.md).

#### Parser (`compiler/src/lexer.flow`, `parser.flow`)
- **Lexer**: streaming tokenizer
- **Parser**: recursive descent into an AST arena (`ast.flow`); nesting
  deeper than `FLOWC_PARSE_MAX_DEPTH` is a parse error

#### C Backend (`compiler/src/cgen.flow`)
- **Type System**: maps Flow types to C types
- **Checks**: `typecheck.flow` runs first; `--strict` makes every type error fatal

#### MLIR Backend (`compiler/src/mlirgen.flow`)
- **Text emission**: `FLOWC_EMIT=mlir` writes func, arith, scf, cf, llvm,
  memref, vector and gpu dialect text
- **Lowering**: `compiler/scripts/mlir_lower.sh`, `mlir_optimize.sh` and
  `mlir_spirv.sh` drive mlir-opt and mlir-translate
- Design and parity record: [MLIR in Flow](design/mlir-in-flow.md)

#### WebAssembly Target (`flow wasm32`, `scripts/tools/llvm_target`)
- **Freestanding wasm32**: Lowers MLIR to LLVM IR and links it with
  `clang --target=wasm32-unknown-unknown`, skipping the C backend and Emscripten
- **Export Validation**: Checks requested exports against the symbols defined in
  the IR before invoking clang
- **Host Imports**: Links `--allow-undefined`, so `malloc` and anything else
  unresolved is imported from the host
- Documented in [WebAssembly](language/wasm.md); exercised by
  `.github/workflows/wasm32.yml`

## Language Implementation

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

## Testing Strategy

### Test Categories

#### 1. Parsing Tests
Verify syntax is correctly parsed:
```bash
python3 -m flow.transpiler examples/new_feature.flow
```

#### 2. Generation Tests
Verify output code quality:
```bash
compiler/scripts/flowc_emit.sh examples/new_feature.flow /tmp/test.c
```

#### 3. Runtime Tests
Verify program execution:
```bash
./flow run examples/new_feature.flow
```

### Test Organization

- **`examples/`**: Standard programs, algorithms, OOP patterns
- **`tests/`**: Compiler features, language demos, edge cases

## File Organization

### Source Layout
```
compiler/
├── src/                 # flowc, in Flow (lexer, parser, typecheck, cgen, mlirgen, ...)
├── bootstrap/           # flowc_stage_a.c, the checked-in C that builds flowc
├── scripts/             # build, parity and MLIR lowering scripts
└── fixtures/            # compiler fixtures and parity goldens
```

### Build Artifacts
```
build/
├── *.c                  # Generated C code
├── *.mlir               # Generated MLIR
├── *.o                  # Object files
└── *                    # Executables
```

## Development Workflow

### Making Changes
1. Identify component to modify
2. Add tests first
3. Implement changes
4. Verify with `./flow test`
5. Add documentation

### Project conventions (`flow check`)

`./flow check` lints `.flow` sources against the conventions a project declares
for itself. It reads `[conventions].avoid` from `flow.toml` and warns on every
source line that matches one of those patterns.

```bash
./flow check                       # every .flow file under the working directory
./flow check src/thing.flow        # just these files
```

Files under `build/` and `.freebuff/` are skipped. With no `avoid` patterns
declared it prints that and exits 0, so it is safe to run in any project. The
exit code is non-zero when a file matches, which makes it usable as a gate.

`--idioms` adds the idiom hints (FIDIOM001, a `let mut` never reassigned;
FIDIOM002, a return that rebuilds one value field by field), and
`--format=json` prints them as JSON. The command is the Flow program
`tools/check/main.flow`; `tests/check/run.sh` holds its goldens.

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

## Performance Considerations

### Parser Performance
- Regex compilation is cached
- Linear tokenization time
- Recursive parsing depth limited by Python stack

### Generation Performance
- String building with lists
- Minimal type inference overhead
- Linear traversal of AST

## Future Extensions

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

## Compiler torture suite (C-grade)

Aim: regression coverage comparable to a C compiler suite: sema rejection,
middle-end specialization, C ABI contracts, backend parity, executable pins.

| Layer | Where | How to run |
|-------|-------|------------|
| Sema rejections and C lowering | `tests/cgen/*.flow` + `.expect` | `tests/cgen/run.sh` |
| Language programs | `tests/lang/*.flow` | `./flow test-lang` |
| Stable conformance | `tests/conformance/` | `tests/conformance/run.sh` |
| MLIR text and runs | `compiler/fixtures/mlir/` | `compiler/scripts/parity_mlir.sh` |
| MLIR commands | `tests/mlir_commands/` | `tests/mlir_commands/run.sh` |
| Runtime exit-code | `tests/runtime/test_*_ops.flow` etc. | `./flow test-runtime` |
| LSP JSON-RPC | `tests/tools/lsp/sessions/*.lsp` | `tests/tools/lsp/run.sh` (native server, no Python) |
| Fuzz | `tests/fuzz/` | `tests/fuzz/run.sh` |
| Tier-2 transpile | git-tracked `tests/**/*.flow` | `./flow test --tier2` |

Pytest only collects **git-tracked** files under `tests/` unless
`FLOW_PYTEST_ALL=1`. `git add` new modules so CI sees them.

### Strict vs lenient (wired 2026-08-04)

CLI `--strict` / `--lenient` now sets `TypeChecker.strict`:

| Rule | `--strict` (default for CLI flag) | `--lenient` |
|------|-----------------------------------|-------------|
| bool ↔ numeric coerce | reject | allow |
| `if` / `while` condition | must be `bool` | numeric OK |
| assign to immutable `let` | reject (use `let mut`) | auto-promote |
| bare generic `Pair {…}` with `Pair<T,…>` annotation | specialized C cast | same (mono fix) |

`./flow test` / `test-runtime` still transpile with `--lenient` so the legacy
corpus keeps compiling while unit tests pin strict behavior.

### Phase 3 notes

- MLIR now dispatches `MatchStatement` (was a no-op comment); returning arms
  skip the trailing `cf.br`; exhaustive matches end with `llvm.unreachable`.
- `tests/unit/test_backend_parity.py` includes bool + i32 match parity.
- 25 tracked `tests/**/*.flow` files were rewritten `let` → `let mut` for
  reassigned locals (strict imm-only failures on the test corpus → 0).
  Remaining strict failures are mostly missing imports under standalone
  typecheck (module-resolved at transpile time).

### Phase 4 notes

- `./flow test-runtime` always-links `runtime/flow_rt_crypto.c` with the
  concurrency bundle; stub `flow_rt_http_mw_enable` in `flow_tcp.c` so
  `lib/runtime/http_routed.flow` can link.
- MLIR `while` CF successor operands use `(%a, %b : i32, i32)` (types once);
  exit edge forwards loop-carried args into the end block.
- Fixed-shape `memref.store` / `memref.load` use `memref<Nxi32>` from the
  symbol table (was hardcoded `memref<?xi…>` → mlir-opt failure).
- Nested `while`: `_assigned_locals` recurses into nested loops; `generate_block`
  propagates SSA updates for parent locals (shallow scope copy was dropping
  loop-carried values after nested `while` replaced symbol entries).
- Parity suite covers nested while / array mutate; pins in
  `compiler/fixtures/mlir/`. Clang link failures in `test-runtime`
  print a short error snippet without `--verbose`.

### Phase 5 notes

- The MLIR emitter (`compiler/src/mlirgen.flow`, once
  `src/flow/mlir_canonicalize.py`) runs two AST rewrites ahead of MLIR
  generation. Both came out of compiling Doom through the MLIR backend.
- Counted-loop rotation (#473): `while true { P; if c == 0 { break }; S }`
  becomes `P; while c != 0 { S; P }`. The exit test moves to the loop latch, so
  LLVM's vectorizer and unroller can recover a trip count. Both forms evaluate
  the test at the same program points; the rewrite is declined when the body
  holds another `break`/`continue`, a `defer`, a second write to the counter,
  or a declaration in the peeled prefix.
- Trivial accessor inlining (#474): a parameterless function whose whole body is
  `return &g` or `return g` for a module-scope `g` is substituted at its call
  sites, turning call+load pairs in hot loops into plain loads. The definition
  is still emitted, so external linkage is unchanged.
- Pins live in `tests/unit/test_mlir_canonicalize.py`;
  `tests/integration/test_counted_loop_rotation.py` compiles each loop shape
  before and after rotation through the C backend and compares what it returns.

## References

- [MLIR Documentation](https://mlir.llvm.org/)
- [LLVM IR Reference](https://llvm.org/docs/LangRef.html)
- [Python Packaging](https://packaging.python.org/)
- [Compiler Design](https://craftinginterpreters.com/)
