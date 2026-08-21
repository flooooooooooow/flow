# Flow platform support

This document defines the operating-system and architecture support contract for the
Flow 1.0 stabilisation programme.

The classifications below are **qualification targets** until `1.0.0-rc.1`. A platform
becomes a 1.0 Tier 1 platform only after the required qualification workflow is green
and release-tag artifacts have been installed and exercised from a clean environment.

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
| Linux x86-64 | Tier 1 | per-PR Tier-1 qualification is landed and green; C11 toolchain contract is exercised; release-tag artifact qualification remains |
| macOS arm64 | Tier 1 | per-PR Tier-1 qualification is landed and green; C11 toolchain contract is exercised; release-tag artifact qualification remains |
| Linux arm64 | Tier 2 candidate | release qualification still to be added |
| Windows x86-64 | Tier 2 candidate | runtime/gfx smoke exists; full compiler qualification still required |
| WASM / Emscripten | target-specific Beta/Stable decision pending | dedicated wasm workflow exists |
| MLIR JIT | Experimental | optional toolchain |
| CUDA | Experimental | not a 1.0 Tier 1 target |
| bare metal / RTOS | Experimental | long-term physical-systems roadmap |

## Tier 1 qualification contract

For each Tier 1 platform, CI must prove at least the following from a clean checkout:

1. A conforming host C toolchain satisfies the Flow C11 capability contract below.
2. Locked development dependencies install successfully.
3. The strict Tier-2 Flow corpus transpiles successfully.
4. Checked-in bootstrap C builds a working `flowc` without requiring the Python compiler.
5. Every `compiler/src` module compiles under that `flowc`.
6. A Stable Flow program compiles with `FLOW_HOST=flowc` and executes with the expected result.
7. The distributable `flowc` archive can be built, unpacked into a clean directory, rebuilt as the user would, and used to compile and run a supplied program.
8. The complete Stable 1.0 conformance corpus runs on the platform once #641 reaches full Stable-core coverage.

The workflow introduced by #658 proves the compiler/package portions on both Linux
x86-64 and macOS arm64 on every relevant pull request. It also caught and fixed a
release-package contract bug: rebuilding the shipped compiler archive must preserve the
documented `flowc <in.flow> <out.c>` positional interface rather than changing
invocation mode.

The toolchain qualification added during the 1.0 cut additionally compiles and executes
a strict C11 probe before Flow itself. Release publication separately repeats the
end-user archive exercise on the exact tag.

## C toolchain contract

Flow 1.0 specifies its minimum host C toolchain by **capability**, not an arbitrary
vendor version number. A Tier 1 host must provide `cc` with conforming C11 support for
the generated-code subset used by Stable Flow, including `<stdint.h>`, `<stddef.h>`,
`<stdbool.h>`, `_Static_assert`, fixed-width integer types, ordinary designated
initializers and the platform C runtime/linker required by the generated program.

CI enforces this contract with `cc -std=c11 -Werror -pedantic` before running the Flow
qualification suite. The compiler identity and version are printed into the Actions log
for every Tier 1 qualification run.

This capability floor is the compatibility promise. Flow does not claim support for an
older compiler merely because some generated program happens to compile with it, and it
does not artificially require a newer Clang/GCC version when an older implementation
satisfies the exercised C11 contract. If generated Stable C later needs a newer C
language capability, that is a compatibility change to this document and its CI probe.

## Backend scope

The default portable C backend is the production path qualified for the initial Stable
1.0 core. Optional MLIR/JIT, CUDA, Metal-specific, BPF and other target paths have their
own feature support and do not inherit Tier 1 status merely because the host OS is Tier
1.

## Release rule

`1.0.0` is blocked by any unresolved Tier 1 qualification failure. Official release
artifacts must be exercised on every Tier 1 platform before publication. The C backend
is classified Stable for the declared Stable language core in `stability/surfaces.json`;
that classification does not waive the exact-tag qualification required by the release
workflow.

Tracking: #647 and the Flow 1.0 stabilisation programme #653.
