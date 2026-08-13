# Language maturity checklist

This page maps FLOW against a fifteen-stage checklist for what an "official"
programming language needs. It is the single source of truth for readiness:
what is done, what is partial, and what has not started yet. The signal is
meant to be honest, not promotional.

Legend: **DONE** means implemented and exercised. **PARTIAL** means it exists
but is not complete or not fully machine-tested. **GAP** means it is not done.

## The dividing line: 1.0

The critical transition is showing FLOW 1.0. A language does not need ISO's
permission to be official; Python, Rust and Go are defined primarily by their
own stable specification, conformance suite and compatibility commitment, not
by an international standard.

Today the language has a compiler and a specification (v0.11.0), but the spec is
not frozen, its semantics are not yet locked, and there is no published
compatibility policy. That is what separates "a compiler project implementing
a language" from "FLOW is a language with a defined 1.0 standard". Everything
in stages 1 to 12 runs up to that line.

## Supported platforms (today)

| Backend | Status |
|---|---|
| C | DONE. The primary, fully functional backend. |
| MLIR + MLIR-to-LLVM JIT | PARTIAL. Functional; effects do not lower through every path. |
| WebAssembly | PARTIAL. Via Emscripten from the C backend. |
| SPIR-V / Vulkan | PARTIAL. GPU kernel/metallic emission works. |
| Metal / WGSL / shader kernels | PARTIAL. GPU codegens exist and are exercised in examples. |
| JavaScript | PARTIAL. Used by the flowc self-hosted backend. |
| Python | PARTIAL. `flow python` codegen path exists. |

| Host OS | Status |
| --- | --- |
| macOS | DONE. Working; context switching uses `flow_fctx_arm64.S` / `x86_64.S`. |
| Linux | DONE. Working; SDL2-backed graphics and full test matrix on CI. |
| Windows | PARTIAL. SDL2 path shared with Linux and gfx stub smoke runs on CI; no binary installer and limited coverage. |

| Architecture | Status |
| --- | --- |
| x86-64 | DONE. Coveraged by CI on Linux and macOS. |
| ARM64 (Apple Silicon) | DONE. Native and CI-covered on macOS. |
| ARM64 (Linux) | PARTIAL. Supported in the toolchain, not systematically covered. |

CI builds and exercises FLOW on `ubuntu-latest`, `macos-latest` and a
`windows-latest` gfx-stub smoke job. The self-hosted `flowc` toolchain is
built on Linux and macOS. Toolchain version is 0.11. spec version is 0.11.0.

## Stage by stage

### 1. Identity
| Item | Status | Note |
| --- | --- | --- |
| Name | DONE | FLOW; no serious ecosystem collision. |
| Domain / site | DONE | GitHub Pages site at `flooooooooooow.github.io/flow/`; no custom domain yet. |
| Repository | DONE | Public canonical repo on GitHub. |
| Branding / file extension | DONE | `.flow` extension, editor themes, naming conventions. |
| License | DONE | MIT; `LICENSE`, `CITATION.cff`. |

### 2. Language definition
| Item | Status | Note |
| --- | --- | --- |
| Lexical grammar | DONE | `docs/grammar.ebnf`, `.space` in `docs/language/syntax.md`. |
| Grammar (EBNF) | DONE | `docs/grammar.ebnf` generated from the parser. |
| Semantics | PARTIAL | `docs/LANGUAGE_SPEC.md` covers it; not yet treated as frozen. |
| Type system | DONE | Spec incl. inference, conversions, generics. |
| Memory model | PARTIAL | Spans, `let mut`, lifetime domains; no Rust-style borrow checker. |
| Evaluation model | PARTIAL | Documented in the spec, not fully pinned. |
| Error model | PARTIAL | Stable strict and lenient diagnostics exist. |
| Concurrency model | PARTIAL | Async effects, threads documented; not fully pinned. |
| FFI / ABI | DONE | `extern "C"` including variadic externs documented and tested. |
| Undefined behaviour | PARTIAL | Not comprehensively listed. |
| op code composition | PARTIAL | Many operator assignments (compound assignment) present. |

### 3. Specification
| Item | Status | Note |
| --- | --- | --- |
| Language Specification | PARTIAL | `docs/LANGUAGE_SPEC.md` exists at 0.3, not a frozen 1.0. |
| Versioning rules | PARTIAL | Semver on toolchain; spec version does not define minor/patch meanings. |
| Compatibility policy | PARTIAL | Some backward-compat claims; no written/official policy. |
| Feature lifecycle | PARTIAL | Experimental markers partial; no deprecation stage markers. |
| Reference examples | PARTIAL | Numerous docs/tutorials; no canonical per-clause corpus. |

### 4. Reference implementation
| Item | Status | Note |
| --- | --- | --- |
| Compiler | DONE | `src/flow` (Python) plus self-hosted `flowc` in `compiler/`. |
| Bootstrap | DONE | Three-generation fixed-point proof builds `flowc` from a single-C bootstrap. |
| Targets | PARTIAL | C primary; Wasm, JIT, SPIR-V partial; architecture matrix above. |
| Diagnostics | PARTIAL | Strict / lenient diagnostics and LSP intellisense exist. |
| Optimisation | PARTIAL | MLIR optimize + JIT; release-quality pipeline is aspirational. |
| Debug info | PARTIAL | DWARF/debug-info present; source-level debugger is exploratory. |
| Reproducibility | PARTIAL | Roundtrip/bootstrap scripts; not yet a certified artifact. |

### 5. Conformance
| Item | Status | Note |
| --- | --- | --- |
| Test suite | DONE | 87 Python unit, 10 integration, 222 `.flow` runtime/lang/stdlib, tier CLI. |
| Spec-to-test mapping | PARTIAL | No automated binding of each spec clause to a test. |
| Compiler regression suite | DONE | Every crash is pinned as a regression test. |
| Differential tests | DONE | `tests/unit/test_backend_parity.py` compares C vs MLIR outputs. |
| Fuzzing | DONE | `tests/fuzz/harness.py` (mutation, grammar-directed, pipeline). |
| Torture tests | DONE | `test_torture_nesting.py`, `tests/lang/test_torture.flow`. |
| Compatibility corpus | PARTIAL | Some old programs continuously rebuilt; not a curated corpus. |

### 6. Standard library
| Item | Status | Note |
| --- | --- | --- |
| Core (collections, strings, math, I/O) | DONE | `lib/stdlib` 82 modules; `lib/runtime` always-linked. |
| Stability policy | PARTIAL | Public API versioning is implied, not an explicit archive policy. |
| Documentation | DONE | `docs/library/*` reference. |
| Tests | DONE | `tests/stdlib` has 54 `.flow` test files. |
| Platform behaviour | PARTIAL | Cross-platform gaps noted; GPU examples require Metal/Vulkan. |

### 7. Toolchain
| Feature | Status | Note |
| --- | --- | --- |
| Package manager | DONE | `flow add`, `flow pkg`, `src/flow/package.py`, registry. |
| Build system | DONE | `flow build`, `build-native`. |
| Runner | DONE | `flow run`. |
| Tests | DONE | `flow test --tier1/--tier2`. |
| Formatter | DONE | `flow fmt` (`.py` formatter). |
| Linter | PARTIAL | No `flow lint` CLI; CI runs ruff over Python but not a Flow source linter. |
| Documentation gen | DONE | `flow doc` and * wiki site builder. |
| REPL | DONE | `flow repl`. |
| LSP | DONE | `flow-lsp` (VS Code / Neovim intelligence). |
| Debugger | PARTIAL | Debug plumbing, not a full source-level debugger story. |
| Safety profile | DONE | `--profile safety` (`-Werror -pedantic` C flags). Literal div-by-zero and shift UB rejected at type-check time. UBSan/ASan/TSan via env vars. |

### 8. Distribution
| Item | Status | Note |
| --- | --- | --- |
| Versioned releases | DONE | `v0.11.0` tags, GitHub Releases. |
| Installers | PARTIAL | Source archives; Homebrew formula; no Windows/Winget or official installers. |
| Package managers | PARTIAL | Homebrew tapped; no winget/apt/nix official recipes beyond tap. |
| CI | DONE | `ci.yml` across jobs and `*.github/workflows` (lint, bootstrap, pytest, fuzz). |
| Release CI | DONE | `flowc-release.yml` builds binaries on Linux and macOS. |
| Checksums / signatures | DONE | `SHA256SUMS` for release archives; no formal signing. |

### 9. Ecosystem
| Feature | Status | Note |
| --- | --- | --- |
| Package registry | DONE | `registry/index.json`, namespaced packages. |
| Package metadata | DONE | Semver, author, license, deps. |
| Semver semantics / lockfiles | DONE | `package.py`/registry with `flow.lock`. |
| Vulnerability reporting | DONE | `SECURITY.md` present. |
| Namesquatting / governance | PARTIAL | No explicit registry governance policy page. |

### 10. Documentation
| Item | Status | Note |
| --- | --- | --- |
| Getting started | DONE | `docs/getting-started.md`. |
| Language tour | DONE | `docs/comparison.md` and tour pages. |
| Reference | DONE | `docs/LANGUAGE_SPEC.md` + `docs/language/*`. |
| Stdlib reference | DONE | `docs/library/*`. |
| Cookbook | DONE | `docs/tutorials/*` 30 topic files. |
| Migration guide | DONE | `docs/comparison.md`, `docs/language/replace-go.md`. |
| Compiler internals | DONE | `docs/project/architecture-writeup.md`, `compiler/README.md`. |
| Website | DONE | GitHub Pages generated from mkdocs. |

### 11. Proof it works
| Item | Status | Note |
| --- | --- | --- |
| Benchmarks | PARTIAL | `tests/benchmarks` and `flow bench` exec exist. |
| Real applications | DONE | Doom port; Game, Morphogenesis, Numerical galleries, SDK. |
| C interop | DONE | `extern "C"` FFI incl. variadic externs; example stubs. |
| Libraries | PARTIAL | Networking (std/language), JSON, HTTP; GUI via SDL2/graphics. |
| Self-hosting | DONE | `flowc` compiles substantial parts of FLOW with FLOW (three-stage). |
| Large project | DONE | Doom as a flagship real codebase. |
| Ecosystem libraries | PARTIAL | Not a curated, blessed marketplace outside the built-in registry. |

### 12. Governance
| Item | Status | Note |
| --- | --- | --- |
| RFC / change process | GAP | No formal RFC/design-doc directory or gate. |
| Language team | PARTIAL | maintainership implied, not a named team model. |
| Contribution policy | DONE | `CONTRIBUTING.md`. |
| Code of conduct | DONE | `CODE_OF_CONDUCT.md`. |
| Security policy | DONE | `SECURITY.md`. |
| Roadmap | DONE | `ROADMAP.md`. |

### 13. The 1.0 gate
| Item | Status | Note |
| --- | --- | --- |
| Feature freeze | PARTIAL | Not formally invoked. |
| Spec / compiler agreement | PARTIAL | Spec 0.3 tracks the implementation but no test-enforced conformance. |
| Compatability freeze | GAP | No formal 1.0 freeze policy. |
| Stdlib freeze | GAP | Not frozen. |
| Conformance release | GAP | Not published as versioned artifact. |

### 14. External recognition
| Item | Status | Note |
| --- | --- | --- |
| Linguist detection | PARTIAL | `.gitattributes` opts in; upstream `github-linguist` does not know Flow yet. |
| Syntax highlighting (editors) | DONE | VS Code extension + TextMate grammar; syntax-oriented referencing. |
| Tree-sitter | GAP | No tree-sitter grammar yet. |
| Pygments | GAP | Not upstreamed. |
| Language servers | DONE | `flow-lsp`. |
| Benchmark suites | PARTIAL | `tests/benchmarks`; no external comparative matrix. |
| Package ecosystems | PARTIAL | Homebrew tap + Open VSX + registry catalogues. |

### 15. Standardisation (much later)
| Item | Status | Note |
| --- | --- | --- |
| Independent implementations | GAP | Single implementation today. |
| Formal standard | GAP | Not started. |
| Standards body | GAP | Not started. |
| Standard-candidate proposal | GAP | Not started. |

## Reading the gaps

DONE count: roughly 40 of 60 rows. The gaps cluster into four levers:

1. **The 1.0 gate.** Freeze the spec (grammar, semantics, memory model), add a
   compatibility and feature-lifecycle policy, and publish a conformance suite
   that maps spec clauses to tests. This is the highest-leverage next step.
2. **Missing tooling surface.** A `flow lint` (the repo linter is `ruff`, not a
   FLOW source linter) and a top-level `flow bench`, plus a source-level
   debugger.
3. **External recognition.** Tree-sitter and Pygments capture, upstream
   github-linguist, and more curated library ecosystem.
4. **Distribution completeness.** Windows binary installer / winget, signed
   artifacts, and a named governance model.

Platforms today are macOS and Linux (x86-64 and arm64) with the C
backend, plus partial Windows, WebAssembly, GPU and MLIR paths; the full test
suite runs on Linux and macOS and a gfx-stub smoke runs on Windows.