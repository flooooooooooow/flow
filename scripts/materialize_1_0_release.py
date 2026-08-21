#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"expected release text not found in {path}: {old[:80]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def main() -> int:
    subprocess.run(
        [
            "python3",
            "scripts/sync_version.py",
            "--set",
            "1.0.0",
            "--release-date",
            "2026-08-22",
        ],
        cwd=ROOT,
        check=True,
    )

    readme = ROOT / "README.md"
    replace_once(
        readme,
        "Flow is a statically typed, compiled language with algebraic effects, autodiff in the stdlib, dynamics and control analysis, and native graphics. You write how a system evolves; that description is what runs.\n",
        "Flow is a statically typed, compiled systems language. Flow 1.0 freezes a deliberately small production core around the self-hosted `flowc` compiler and portable C backend; algebraic effects, dynamics/control DSLs, verification, advanced stdlib domains and alternate backends continue to ship as explicitly Experimental surfaces until they are promoted.\n",
    )
    replace_once(
        readme,
        "| Cite | [CITATION.cff](CITATION.cff) |\n\n## Quickstart\n\nThe full-language quickstart uses the Python host explicitly so the first copy-paste example works exactly as shown.\n",
        "| Cite | [CITATION.cff](CITATION.cff) |\n\nFlow 1.0's compatibility promise is defined in [STABILITY.md](STABILITY.md). Linux x86-64 and macOS arm64 are the initial Tier-1 platforms; every published `v1.*` release is qualified from the exact tag before GitHub Release publication.\n\n## Quickstart\n\nThe default production path is the self-hosted `flowc` compiler targeting portable C.\n",
    )
    replace_once(
        readme,
        "FLOW_HOST=python flow run hello.flow\n",
        "flow run hello.flow\n",
    )
    replace_once(
        readme,
        "Needs Python 3.9+ and Clang or GCC (Xcode Command Line Tools on macOS).\n",
        "The production compiler path requires a conforming C11 toolchain. Python 3.9+ is retained for the reference/bootstrap compiler and development tooling, not as the canonical 1.0 execution host.\n",
    )
    replace_once(
        readme,
        "- Dynamical systems, controllers, and simulations in one language ([VISION](VISION.md)).\n- Algebraic effects so you can swap I/O and other handlers without rewriting call sites.\n- Forward and reverse autodiff helpers in the stdlib; ML demos train on CPU in seconds.\n- C backend by default (no LLVM required). MLIR, WASM, and Metal when you need them.\n",
        "- A Stable systems-language core with a self-hosted `flowc` compiler and portable C backend.\n- Dynamical systems, controllers, algebraic effects, autodiff, graphics and domain libraries available as shipped Experimental surfaces with explicit promotion boundaries.\n- C backend by default with no LLVM requirement; MLIR/JIT, CUDA and other specialised targets remain Experimental in 1.0.\n",
    )

    changelog = ROOT / "docs" / "project" / "CHANGELOG.md"
    release_notes = """## [1.0.0] - 2026-08-22

Flow 1.0 establishes the first explicit compatibility contract for the language rather than freezing every feature currently present in the repository.

### Stable 1.0 core

- The self-hosted `flowc` compiler is the canonical production host for Stable Flow; the Python implementation remains a reference/bootstrap oracle.
- The portable C backend is the Stable production target for the declared Stable language core.
- Linux x86-64 and macOS arm64 are the initial Tier-1 platforms. Their compiler/package/install path is continuously qualified and release publication repeats qualification on the exact tag.
- Stable CLI and manifest behavior is defined in `STABILITY.md`; runtime ABI version `1` records the deliberately narrow C/FFI-visible binary-compatibility boundary.
- The permanent conformance corpus compares observable behavior between the Python reference path and self-hosted `flowc`.

### Explicitly Experimental

Algebraic effects, dynamics/`dsys`, verification syntax, advanced/partial language forms, specialised standard-library domains, MLIR/JIT, CUDA and other non-C targets continue to ship for real use but are outside the 1.x compatibility promise until separately promoted. Multi-shot continuation semantics remain Reserved/Future.

### Release engineering and documentation

- `v1.*` publication is blocked until the exact tag passes stability completeness, strict documentation verification, Stable conformance, strict corpus checks, bootstrap/self-host qualification, Tier-1 package rebuild/use and bounded release fuzzing.
- Official documentation now has zero ordinary `flow` debt: every executable Flow fence is compiler-verified, every deliberate rejection is an `expect-error` test, and illustrative/incomplete notation is explicitly marked `flow-pseudocode` rather than hidden behind `ignore=`.
- The C toolchain floor is capability-based and exercised as a strict C11 contract instead of being tied to an arbitrary Clang/GCC version number.
- The 1.x security-support lifecycle, coordinated-disclosure policy and release trust-boundary regression checks are documented and enforced.

"""
    replace_once(changelog, "## Unreleased\n\n", "## Unreleased\n\n" + release_notes)

    platforms = ROOT / "PLATFORMS.md"
    replace_once(
        platforms,
        "The classifications below are **qualification targets** until `1.0.0-rc.1`. A platform\nbecomes a 1.0 Tier 1 platform only after the required qualification workflow is green\nand release-tag artifacts have been installed and exercised from a clean environment.\n",
        "The classifications below define the Flow 1.0 support contract. A published release exists only after its exact tag has passed the required qualification workflow and its release artifacts have been rebuilt and exercised from a clean environment.\n",
    )
    replace_once(
        platforms,
        "| Linux x86-64 | Tier 1 | per-PR Tier-1 qualification is landed and green; C11 toolchain contract is exercised; release-tag artifact qualification remains |\n| macOS arm64 | Tier 1 | per-PR Tier-1 qualification is landed and green; C11 toolchain contract is exercised; release-tag artifact qualification remains |\n",
        "| Linux x86-64 | Tier 1 | continuously qualified; C11 toolchain contract is exercised; exact-tag release qualification blocks publication on failure |\n| macOS arm64 | Tier 1 | continuously qualified; C11 toolchain contract is exercised; exact-tag release qualification blocks publication on failure |\n",
    )

    subprocess.run(["python3", "scripts/sync_version.py", "--check"], cwd=ROOT, check=True)
    subprocess.run(["python3", "scripts/check_stability_manifest.py", "--require-complete"], cwd=ROOT, check=True)
    subprocess.run(["python3", "scripts/check_doc_examples_strict.py"], cwd=ROOT, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
