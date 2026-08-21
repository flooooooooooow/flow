# Flow platform support

This document defines the operating-system and architecture support contract for the
Flow 1.0 stabilisation programme.

The classifications below are **qualification targets** until `1.0.0-rc.1`. A platform
becomes a 1.0 Tier 1 platform only after the required qualification workflow is green,
minimum supported toolchain versions are frozen, and release-tag artifacts have been
installed and exercised from a clean environment.

## Support tiers

### Tier 1

Tier 1 is the production support tier. A Tier 1 platform must run the Stable language
conformance suite, compiler/runtime/stdlib integration tests, self-hosted `flowc`
qualification, and release-artifact install/compile/run tests continuously.

A Tier 1 failure blocks a Flow release.

### Tier 2

Tier 2 platforms are release-tested and supported on a best-effort basis, but do not
necessarily run the complete qualification matrix on every pull request. Regressions
are tracked and accepted as bugs, but a Tier 2-only failure does not automatically block
a release unless it affects a Stable cross-platform contract.

### Experimental

Experimental targets may work and may have dedicated tests, but they are outside the
Flow 1.x platform compatibility promise unless promoted through qualification.

## 1.0 qualification matrix

| Platform | 1.0 target | Current qualification |
|---|---|---|
| Linux x86-64 | Tier 1 | per-PR Tier-1 qualification is landed and green; minimum toolchain and release-tag artifact qualification remain |
| macOS arm64 | Tier 1 | per-PR Tier-1 qualification is landed and green; minimum toolchain and release-tag artifact qualification remain |
| Linux arm64 | Tier 2 candidate | release qualification still to be added |
| Windows x86-64 | Tier 2 candidate | runtime/gfx smoke exists; full compiler qualification still required |
| WASM / Emscripten | target-specific Beta/Stable decision pending | dedicated wasm workflow exists |
| MLIR JIT | Experimental | optional toolchain |
| CUDA | Experimental | not a 1.0 Tier 1 target |
| bare metal / RTOS | Experimental | long-term physical-systems roadmap |

## Tier 1 qualification contract

For each Tier 1 platform, CI must prove at least the following from a clean checkout:

1. Locked development dependencies install successfully.
2. The strict Tier-2 Flow corpus transpiles successfully.
3. Checked-in bootstrap C builds a working `flowc` without requiring the Python compiler.
4. Every `compiler/src` module compiles under that `flowc`.
5. A Stable Flow program compiles with `FLOW_HOST=flowc` and executes with the expected result.
6. The distributable `flowc` archive can be built, unpacked into a clean directory, rebuilt as the user would, and used to compile and run a supplied program.
7. The complete Stable 1.0 conformance corpus runs on the platform once #641 reaches full Stable-spec coverage.

The workflow introduced by #658 currently proves items 1–6 on both Linux x86-64 and
macOS arm64 on every relevant pull request. It also caught and fixed a release-package
contract bug: rebuilding the shipped compiler archive must preserve the documented
`flowc <in.flow> <out.c>` positional interface rather than changing invocation mode.

This is sufficient to treat the two operating systems as actively qualified Tier-1
**candidates**, but not yet to promote the C backend/platform pair to the final Stable
1.0 promise. Full conformance coverage, explicit toolchain minima, and release-tag
artifact qualification are still gates.

## Toolchains

The C compiler is part of the qualified environment. Flow 1.0 will record the minimum
supported compiler/toolchain versions before RC1. The current Tier 1 workflow uses the
compiler provided by the GitHub-hosted Ubuntu and macOS runner images. That demonstrates
continuous compatibility with those environments; it does not by itself establish the
oldest supported compiler version.

A minimum version will only be recorded after it is exercised by CI or another
reproducible qualification job. Flow will not infer a minimum merely from the oldest C
standard feature currently used by generated code.

## Backend scope

The default portable C backend is the production path being qualified for Tier 1.
Optional MLIR/JIT, CUDA, Metal-specific, BPF and other target paths have their own
feature support and do not inherit Tier 1 status merely because the host OS is Tier 1.

## Release rule

`1.0.0` is blocked by any unresolved Tier 1 qualification failure. Official release
artifacts must be exercised on every Tier 1 platform before publication. The C backend
remains `pending` in `stability/surfaces.json` until the remaining Tier-1 promotion gates
above are satisfied.

Tracking: #647 and the Flow 1.0 stabilisation programme #653.
