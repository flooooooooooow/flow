# What's Next for Flow

> Strategic priorities after the v0.7.0 security audit (Feb 2026)

## Current State Assessment

**What Works Well:**
- Core language compiles and runs (C backend)
- 62 examples, 6 benchmarks, 2 apps
- Native graphics on macOS (Tetris, 2048 playable)
- ML framework (XOR network trains successfully)
- Autodiff working
- Effect system as a unique differentiator
- Documentation cleaned up with mascot
- 56/98 audit issues resolved (57%)
- All testing and CLI issues closed
- Module resolver fully hardened (path traversal, circular imports, symbol collisions)
- MLIR generator stabilized (7 bug fixes)
- Security fixes for CLI injection and runtime command injection

**What Needs Work:**
- 12 critical issues remain open (0 critical issues closed in audit)
- CI pipeline is completely broken (0/6 CI issues resolved)
- 7 security-tagged issues still open
- C generator has 3 unresolved critical security bugs
- Stdlib concurrency/memory safety gaps
- ~20 examples fail to compile (parser limitations)
- `ptr[0].field` syntax not supported
- Graphics is macOS-only

---

## Priority 1: CI Pipeline (Blocking Everything Else)

The CI pipeline cannot validate any fixes. This is the single highest-leverage item.

### Fix CI Failures Suppression (#88)
Remove `|| true` from pipeline steps so failures are actually caught.

### Add Permissions Block (#89 - Security)
```yaml
permissions:
  contents: read
```
The current pipeline has overly broad token access.

### Enable Python Unit Tests (#90)
Tests exist but the CI job never runs them.

### Expand Linting (#91)
Current lint job is minimal. Add flake8/ruff, mypy, and shellcheck.

### Pin Dependencies (#92)
No lock file means builds are not reproducible.

### Add Security Scanning (#93)
Add SAST (e.g., Bandit for Python, CodeQL) and dependency scanning.

---

## Priority 2: Critical Security Issues

These are the highest-risk items after CI:

| # | Issue | Risk |
|---|-------|------|
| 20 | C gen: code injection via unsanitized identifiers | Attacker-controlled identifiers become C code |
| 21 | C gen: printf format string vulnerability | Format string attacks in generated code |
| 22 | C gen: no array bounds checking | Buffer overflows in generated code |
| 59 | Stdlib: calloc integer overflow | Heap overflow via size multiplication |
| 60 | Stdlib: concurrency primitives are stubs | Data races in any concurrent program |
| 89 | CI: overly broad token access | Supply chain risk |

---

## Priority 3: Remaining Critical Compiler Bugs

| # | Issue | Impact |
|---|-------|--------|
| 1 | Parser: bare except swallows errors | Silent failures mask real bugs |
| 2 | Parser: infinite loop on unterminated blocks | Compiler hangs on malformed input |
| 41 | Transpiler: unreachable code / control flow | Wrong code generated |
| 49 | Monomorphize: no termination guard | Compiler infinite loop on recursive generics |
| 61 | Stdlib: memcpy overlap | Undefined behavior in generated programs |

---

## Priority 4: Showcase Strengths

### Effect System Demo
The effect system is Flow's **killer feature** - not in Rust, Go, Mojo, or Julia.

### Interactive Playground
The `docs/playground/index.html` exists. Make it work with current syntax.

### Performance Comparison
Run benchmarks against C/Rust/Python and publish results.

---

## Priority 5: Broader Adoption

### Cross-Platform Graphics
- Add `runtime/gfx_linux.c` (SDL2 or X11)
- Add `runtime/gfx_windows.c` (Win32 or SDL2)

### Package Registry
- Simple TOML-based package format
- GitHub-based package hosting

### Parser Improvements
Fix the `ptr[0].field` limitation to unblock linalg, ml, and flowdb examples.

---

## Issue Tracker Hygiene

### Malformed Issues (#73-#78)
Issues #74, #75, #76, #77, #78 are fragments of issue #73 created by a broken script.
They should be closed as duplicates of #73.

### Close Rate by Category

| Category | Closed | Open | Rate |
|----------|--------|------|------|
| Testing | 5 | 0 | 100% |
| CLI | 5 | 0 | 100% |
| Stdlib | 8 | 5 | 62% |
| Compiler | 36 | 22 | 62% |
| Runtime | 3 | 2 | 60% |
| CI | 0 | 6 | 0% |

---

## The 80/20 Focus

| Action | Impact | Effort |
|--------|--------|--------|
| Fix CI (#88, #89) | Very High | 2 hours |
| Close malformed #74-#78 | Free cleanup | 5 min |
| Fix C gen identifier sanitization (#20) | High | 4 hours |
| Fix calloc overflow (#59) | High | 1 hour |
| Fix parser bare except (#1) | Medium | 2 hours |
| Cross-platform graphics | Medium | 1 week |

---

## Audit Summary

The v0.7.0 audit filed 98 issues across all components. The response prioritized
medium/low-risk items effectively (CLI, testing, MLIR, module resolver all fully resolved).
However, the 12 critical issues and all CI issues remain untouched. The next release
should focus exclusively on CI and security before adding any new features.
