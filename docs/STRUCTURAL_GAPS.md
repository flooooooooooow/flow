# FLOW Structural Gaps vs Established Languages

Comparison with Zig, Rust, Go to identify what FLOW needs for "structural legitimacy."

---

## Executive Summary

| Category | Zig | Rust | Go | **FLOW** |
|----------|-----|------|-----|----------|
| Self-hosting | ✅ | ✅ | ✅ | ❌ Python |
| Formal grammar | ✅ | ✅ | ✅ | ❌ |
| Type checker | ✅ | ✅ | ✅ | ❌ |
| Error handling | ✅ | ✅ | ✅ | ❌ |
| Build system | ✅ | ✅ (cargo) | ✅ | ❌ |
| Package manager | ✅ | ✅ | ✅ | ❌ |
| Stdlib | ✅ | ✅ | ✅ | ⚠️ |
| Testing | ✅ | ✅ | ✅ | ❌ |
| Docs generator | ✅ | ✅ | ✅ | ❌ |
| REPL | ❌ | ❌ | ❌ | ❌ |
| LSP | ✅ | ✅ | ✅ | ⚠️ |
| Formatter | ✅ | ✅ | ✅ | ❌ |

**FLOW's unique advantage**: Effect system (Zig/Go don't have this, Rust has traits but not algebraic effects)

---

## Tier 1: Critical Missing (Language Legitimacy)

### 1.1 Formal Grammar Specification

**What Zig has**: [grammar.y](https://github.com/ziglang/zig/blob/master/doc/langref/grammar.y) in EBNF

**What FLOW has**: Ad-hoc parsing in Python

**Gap**: No formal grammar makes the language undefined. Parser IS the spec.

**Fix**:
```ebnf
// Create docs/grammar.ebnf
program        := declaration* ;
declaration    := function_decl | struct_decl | effect_decl | ... ;
function_decl  := 'function' IDENT '(' params? ')' ('->' type)? block ;
...
```

**Effort**: 2-3 hours (extract from parser.py)

---

### 1.2 Semantic Analysis / Type Checker

**What Zig has**: Separate `Sema.zig` (15k+ lines) doing type checking, const eval, comptime

**What FLOW has**: Types checked ad-hoc during code generation

**Gap**: No semantic pass means:
- No type errors before codegen
- No symbol resolution
- No scope analysis
- No const propagation

**Current architecture**:
```
Source → Parser → AST → C Generator (types checked here, too late!)
```

**Required architecture**:
```
Source → Parser → AST → Type Checker → Typed AST → C Generator
```

**Fix**: Create `src/flow/type_checker.py`:
```python
class TypeChecker:
    def __init__(self):
        self.symbol_table = {}  # name → Type
        self.scopes = []
        self.errors = []
    
    def check(self, ast) -> TypedAST:
        # Build symbol table
        # Check all expressions have consistent types
        # Return typed AST or errors
```

**Effort**: 1-2 weeks

---

### 1.3 Proper Error Handling

**What Zig has**: Error union types `!T`, `catch`, `try`

**What Rust has**: `Result<T, E>`, `Option<T>`, `?` operator

**What Go has**: Multiple returns `(value, error)`

**What FLOW has**: Nothing. Errors crash.

**Gap**: No way to handle runtime failures gracefully.

**Fix**: Add to language:
```flow
# Option type
type Option<T> = Some(T) | None

# Result type  
type Result<T, E> = Ok(T) | Err(E)

# Try operator
function read_file(path: string) -> Result<string, IOError> {
    let handle = open(path)?  # Propagates error
    return Ok(read_all(handle))
}
```

**Effort**: 1 week (parser + type checker + codegen)

---

### 1.4 Internal IR

**What Zig has**: ZIR (Zig IR) → AIR (Analyzed IR) → Machine code

**What Rust has**: HIR → MIR → LLVM IR

**What FLOW has**: AST → C (direct jump, no IR)

**Gap**: Without IR:
- No optimization passes possible
- No analysis passes
- Hard to target multiple backends
- Can't do proper dead code elimination

**Fix**: Create `src/flow/ir.py`:
```python
@dataclass
class IRModule:
    functions: List[IRFunction]
    
@dataclass
class IRFunction:
    name: str
    blocks: List[BasicBlock]
    
@dataclass
class BasicBlock:
    instructions: List[IRInst]
    terminator: Terminator
```

**Effort**: 2-3 weeks

---

## Tier 2: Important Missing (Ecosystem)

### 2.1 Build System

**What Zig has**: `zig build` with `build.zig`

**What Rust has**: `cargo build` with `Cargo.toml`

**What FLOW has**: Shell scripts, Makefile

**Gap**: No declarative build configuration.

**Fix**: Create `flow.toml`:
```toml
[package]
name = "myapp"
version = "0.1.0"

[dependencies]
stdlib = { path = "lib/stdlib" }

[build]
target = "c"
optimization = "O2"
```

And `flow build` command.

**Effort**: 1 week

---

### 2.2 Package Manager

**What Zig has**: Package URLs + hash verification

**What Rust has**: crates.io

**What Go has**: go modules

**What FLOW has**: File path imports only

**Gap**: No dependency versioning, no remote packages.

**Fix**: 
1. Define package format
2. Create registry (or use git URLs)
3. Implement `flow add`, `flow update`

**Effort**: 2-3 weeks

---

### 2.3 Testing Framework

**What Zig has**: `test "name" { ... }` blocks, `zig test`

**What Rust has**: `#[test]` attribute, `cargo test`

**What Go has**: `*_test.go` files, `go test`

**What FLOW has**: External Python tests

**Gap**: No native testing.

**Fix**: Add to language:
```flow
test "addition works" {
    assert(add(2, 3) == 5)
    assert(add(-1, 1) == 0)
}
```

And `flow test` command.

**Effort**: 3-5 days

---

### 2.4 Documentation Generator

**What Zig has**: `zig doc` → HTML

**What Rust has**: `cargo doc` → HTML

**What Go has**: `go doc` → text/HTML

**What FLOW has**: Markdown files (manual)

**Gap**: No autodoc from source.

**Fix**: 
1. Parse doc comments (`## ...` or `/// ...`)
2. Generate markdown/HTML

**Effort**: 3-5 days

---

### 2.5 Formatter

**What Zig has**: `zig fmt`

**What Rust has**: `rustfmt`

**What Go has**: `gofmt`

**What FLOW has**: Nothing

**Gap**: No canonical style.

**Fix**: Create `flow fmt` that:
1. Parses source
2. Pretty-prints AST with consistent style

**Effort**: 2-3 days

---

## Tier 3: Nice to Have (Polish)

### 3.1 Self-Hosting Compiler

**What it means**: Compiler written in FLOW, not Python

**Why it matters**: 
- Proves language is powerful enough
- Dogfooding finds bugs
- Faster compilation (no Python overhead)

**Gap**: Compiler is ~5k lines of Python

**Fix**: Rewrite in FLOW (requires FLOW to be more complete first)

**Effort**: 3-6 months

---

### 3.2 Debug Information

**What Zig has**: Full DWARF support, works with gdb/lldb

**What FLOW has**: None. Can't debug generated code.

**Fix**: Emit DWARF via C backend (add `#line` directives)

**Effort**: 1 week

---

### 3.3 Incremental Compilation

**What Zig has**: Incremental compilation, caches intermediate artifacts

**What FLOW has**: Recompiles everything every time

**Fix**: 
1. Hash source files
2. Cache generated C/object files
3. Recompile only changed modules

**Effort**: 1-2 weeks

---

### 3.4 Better LSP

**What Zig has**: ZLS with full completion, go-to-definition, hover

**What FLOW has**: Basic LSP skeleton

**Fix**: Implement:
- [ ] Go to definition
- [ ] Find references
- [ ] Hover type info
- [ ] Completion
- [ ] Diagnostics

**Effort**: 2-3 weeks

---

## Tier 4: Differentiators (FLOW-specific)

### 4.1 Effect System (ALREADY DONE ✅)

FLOW has something Zig/Go don't: algebraic effects. This is a differentiator, not a gap.

### 4.2 WASM-First Compilation

Could be a niche: best-in-class WASM target.

### 4.3 AI-Friendly Syntax

Designed for LLM code generation. Document this as a feature.

---

## Priority Roadmap

### Phase 1: Language Legitimacy (4-6 weeks)
1. ❌ → ✅ Formal grammar (EBNF)
2. ❌ → ✅ Type checker (separate pass)
3. ❌ → ✅ Error/Result types
4. ❌ → ✅ Testing framework

### Phase 2: Ecosystem (4-6 weeks)
5. ❌ → ✅ Build system (`flow.toml`)
6. ❌ → ✅ Formatter (`flow fmt`)
7. ❌ → ✅ Doc generator (`flow doc`)
8. ⚠️ → ✅ LSP improvements

### Phase 3: Performance (4-8 weeks)
9. ❌ → ✅ Internal IR
10. ❌ → ✅ Debug info
11. ❌ → ✅ Incremental compilation

### Phase 4: Maturity (3-6 months)
12. ❌ → ✅ Self-hosting compiler
13. ❌ → ✅ Package manager
14. ⚠️ → ✅ Comprehensive stdlib

---

## Quantitative Gap Analysis

| Metric | Zig | Rust | Go | FLOW |
|--------|-----|------|-----|------|
| Compiler LoC | ~300k | ~500k | ~200k | ~5k |
| Stdlib LoC | ~100k | ~400k | ~150k | ~500 |
| Test coverage | ~80% | ~90% | ~85% | ~10% |
| Contributors | ~900 | ~5000 | ~2000 | 1 |
| Years mature | 8 | 14 | 15 | <1 |

**FLOW is ~1% the size of mature languages.** This isn't bad—it means there's a clear path to grow.

---

## Immediate Next Steps

1. **Extract formal grammar** from parser.py into EBNF
2. **Create type_checker.py** with symbol table and type inference
3. **Add `test` keyword** and `flow test` command
4. **Add `flow fmt`** command

These four changes would move FLOW from "interesting experiment" to "real language."
