# What's Next for Flow

> Strategic priorities for a solo-maintained language project

## Current State Assessment

**What Works Well:**
- ✅ Core language compiles and runs (C backend)
- ✅ 62 examples, 6 benchmarks, 2 apps
- ✅ Native graphics on macOS (Tetris, 2048 playable)
- ✅ ML framework (XOR network trains successfully!)
- ✅ Autodiff working
- ✅ Effect system unique differentiator
- ✅ Documentation cleaned up with mascot 🦔

**What Needs Work:**
- ❌ No CI - regressions can slip in
- ❌ ~20 examples fail to compile (parser limitations)
- ❌ `ptr[0].field` syntax not supported
- ❌ Website/playground outdated
- ❌ Graphics is macOS-only

---

## Priority 1: Stability (This Week)

### Add GitHub Actions CI
```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: ./flow test
```

### Fix or Remove Broken Examples
Either fix the `ptr[0].field` parser issue OR mark broken examples as `# WIP`.

### Document What Actually Works
Update examples/README.md with a clear "verified working" list.

---

## Priority 2: Showcase Strengths (This Month)

### Effect System Demo Video
The effect system is Flow's **killer feature** - not in Rust, Go, Mojo, or Julia.
Create a compelling demo showing:
- Dependency injection without frameworks
- Testing without mocks
- Algebraic effects for async

### Interactive Playground
The `docs/playground/index.html` exists. Make it work with current syntax.

### Performance Comparison
Run benchmarks against C/Rust/Python and publish results.

---

## Priority 3: Broader Adoption (This Quarter)

### Cross-Platform Graphics
- Add `runtime/gfx_linux.c` (SDL2 or X11)
- Add `runtime/gfx_windows.c` (Win32 or SDL2)

### Package Registry
- Simple TOML-based package format
- GitHub-based package hosting

### Parser Improvements
Fix the `ptr[0].field` limitation to unblock:
- examples/linalg/*
- examples/ml/* (full versions)
- apps/flowdb/*

---

## The 80/20 Focus

For maximum impact with minimal effort:

| Action | Impact | Effort |
|--------|--------|--------|
| Add CI | High | 1 hour |
| Fix examples README | High | 30 min |
| Record demo video | Very High | 2 hours |
| Fix ptr[0].field | High | 4-8 hours |
| Cross-platform gfx | Medium | 1 week |

---

## Unique Selling Points to Emphasize

1. **Effects** - No other systems language has this
2. **Autodiff** - Built-in, not a library
3. **C Backend** - Portable, debuggable, no LLVM dependency
4. **Graphics** - Native window/rendering in ~200 lines
5. **ML-ready** - Tensors, optimizers, neural nets

---

## Immediate Next Actions

1. [ ] Create `.github/workflows/test.yml`
2. [ ] Update examples/README.md with working/WIP status
3. [ ] Fix 3 most important broken examples
4. [ ] Update main README with mascot
5. [ ] Tweet/post about Flow with Tetris GIF
