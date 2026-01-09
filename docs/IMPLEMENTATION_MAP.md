# FLOW Implementation Map

> Maps every language feature to its exact implementation location.
> Use this when you need to understand or modify how a feature works.

## Source Files

| File | Lines | Purpose |
|------|-------|---------|
| `src/flow/parser.py` | ~1280 | Lexer, Parser, AST nodes |
| `src/flow/c_generator.py` | ~810 | C code generation |
| `src/flow/mlir_generator.py` | ~2400 | MLIR code generation |
| `src/flow/transpiler.py` | ~300 | CLI entry point |
| `src/flow/module_resolver.py` | ~150 | Import resolution |

---

## Feature → Code Location

### Lexer (src/flow/parser.py)

| Feature | Class/Method | Lines |
|---------|--------------|-------|
| Token types | `TokenType` | 12-102 |
| Keyword mapping | `Lexer.KEYWORDS` | ~320-360 |
| Token scanning | `Lexer.next_token()` | ~365-440 |

### Parser (src/flow/parser.py)

| Feature | Method | Lines |
|---------|--------|-------|
| Main parse loop | `Parser.parse()` | 461-499 |
| Function parsing | `Parser.parse_function()` | 583-601 |
| Type parsing | `Parser.parse_type()` | 619-680 |
| Expression parsing | `Parser.parse_expression()` | ~720-900 |
| Statement parsing | `Parser.parse_statement()` | ~900-1000 |
| Effect parsing | `Parser.parse_effect()` | ~1050-1080 |
| Capability parsing | `Parser.parse_capability()` | ~1080-1130 |
| Handle parsing | `Parser.parse_handle()` | ~1130-1160 |

### AST Nodes (src/flow/parser.py)

| Node | Dataclass | Lines |
|------|-----------|-------|
| Type | `Type` | 112-118 |
| Parameter | `Parameter` | 120-123 |
| FunctionDecl | `FunctionDecl` | 125-133 |
| VarDecl | `VarDecl` | 135-139 |
| Block | `Block` | 141-143 |
| IfStatement | `IfStatement` | 145-150 |
| WhileStatement | `WhileStatement` | 152-155 |
| ForStatement | `ForStatement` | 157-164 |
| ReturnStatement | `ReturnStatement` | 166-168 |
| Assignment | `Assignment` | 170-174 |
| FunctionCall | `FunctionCall` | 176-179 |
| BinaryOperation | `BinaryOperation` | 181-185 |
| UnaryOperation | `UnaryOperation` | 187-190 |
| Literal | `Literal` | 192-195 |
| Variable | `Variable` | 197-199 |
| StructLiteral | `StructLiteral` | 201-204 |
| FieldAccess | `FieldAccess` | 206-209 |
| ArrayLiteral | `ArrayLiteral` | 211-213 |
| VectorLiteral | `VectorLiteral` | 215-217 |
| ArrayAccess | `ArrayAccess` | 219-222 |
| StructDecl | `StructDecl` | 224-227 |
| EffectDecl | `EffectDecl` | 229-232 |
| EffectOperation | `EffectOperation` | 234-238 |
| CapabilityDecl | `CapabilityDecl` | 240-244 |
| CapabilityMethod | `CapabilityMethod` | 246-251 |
| EffectCall | `EffectCall` | 253-257 |
| HandleStatement | `HandleStatement` | 259-263 |
| MatchStatement | `MatchStatement` | 265-269 |
| MatchCase | `MatchCase` | 271-274 |
| StructPattern | `StructPattern` | 276-279 |
| ImportDecl | `ImportDecl` | 281-283 |
| ConstDecl | `ConstDecl` | 285-292 |

### C Generator (src/flow/c_generator.py)

| Feature | Method | Lines |
|---------|--------|-------|
| Main entry | `flow_to_c()` | ~50-80 |
| Type mapping | `CGenerator._c_type()` | ~120-180 |
| Effect runtime | `_gen_effect_runtime_types()` | 203-261 |
| Effect vtables | `_gen_effect_vtables()` | 263-350 |
| Capability methods | `_gen_capability_method()` | 189-201 |
| Function generation | `_gen_function()` | 436-448 |
| Block generation | `_gen_block()` | 450-454 |
| Statement dispatch | `_gen_statement()` | 456-491 |
| If generation | `_gen_if()` | 493-515 |
| While generation | `_gen_while()` | 517-524 |
| For generation | `_gen_for()` | 526-543 |
| Handle generation | `_gen_handle()` | 545-580 |
| Expression dispatch | `_gen_expr()` | 582-773 |
| Effect call generation | `_gen_effect_call()` | 775-780 |
| Array access | `_gen_array_access()` | 782-786 |
| Array literal | `_gen_array_literal()` | 788-810 |

### MLIR Generator (src/flow/mlir_generator.py)

| Feature | Method | Lines |
|---------|--------|-------|
| Module generation | `generate_module()` | 88-154 |
| Function generation | `generate_function()` | 156-201 |
| Statement generation | `generate_statement()` | 216-243 |
| Expression generation | `generate_expression()` | 1136-1161 |
| Effect generation | `generate_effect()` | 2277-2285 |
| Capability generation | `generate_capability()` | 2287-2298 |

### Module Resolver (src/flow/module_resolver.py)

| Feature | Method | Lines |
|---------|--------|-------|
| Import resolution | `resolve_imports()` | ~40-100 |
| Path resolution | `find_module_path()` | ~100-130 |

### CLI (src/flow/transpiler.py)

| Feature | Location | Lines |
|---------|----------|-------|
| Argument parsing | `main()` | ~50-100 |
| Compile command | `do_compile()` | ~100-200 |
| Run command | `do_run()` | ~200-250 |

---

## Test Coverage

| Component | Test File | Coverage |
|-----------|-----------|----------|
| Parser | `tests/unit/test_parser.py` | Partial |
| C Generator | `tests/integration/` | Via examples |
| Effects | `examples/effects_working.flow` | Manual |
| WASM | `wasm/` | Manual |

---

## Adding New Features

1. **Add AST node** in `parser.py` (dataclass)
2. **Add parsing** in `Parser.parse_*()` method
3. **Add C generation** in `CGenerator._gen_*()` method
4. **Add MLIR generation** (optional) in `MLIRGenerator.generate_*()` method
5. **Update spec** in `docs/LANGUAGE_SPEC.md`
6. **Add example** in `examples/`
7. **Add test** in `tests/`

---

*This map is auto-generated from source analysis. Last updated: 2026-01-08*
