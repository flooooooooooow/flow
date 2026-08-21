# Flow 1.0 release cut

This file is the operational checklist for cutting the first stable Flow release. It complements `ROADMAP-1.0.md` and issue #653; it is intentionally narrower and records only work that must be true of the exact commit tagged `v1.0.0`.

## Release invariant

Do not create `v1.0.0` by changing the version number first and discovering release defects afterward. The final tag must point at an exact commit that has already passed the complete release qualification path.

The required order is:

1. Freeze the Stable 1.x surface and remove every `pending` entry from `stability/surfaces.json`.
2. Close or explicitly move outside Stable 1.0 every RC/final blocker in #653.
3. Run the stable conformance corpus through both the Python reference and `flowc` with zero unexplained semantic divergence.
4. Run strict documentation qualification with zero ordinary unverified/ignored Stable Flow examples.
5. Qualify Linux x86-64 and macOS arm64 release artifacts by unpacking, rebuilding, compiling and executing an end-user program.
6. Complete the final performance, fuzzing, security, formatter and developer-workflow gates.
7. Bump the canonical version and all mirrors to `1.0.0` using `scripts/sync_version.py --set 1.0.0` or `.github/workflows/version-bump.yml` before tagging.
8. Re-run the complete release qualification on that exact version-bump commit.
9. Create `v1.0.0` at that exact qualified commit.
10. Publish release artifacts, checksums/provenance and release notes; then rerun the version workflow with Homebrew enabled once the release tarball exists.

## Current blockers

As of the start of the release cut, the repository's own machine-readable release contract still marks these surfaces `pending`:

- `language`
- `stdlib`
- `runtime-abi`
- `c-backend`

The release dashboard also still carries open final-tag work for effect failure semantics, full conformance/host parity, `dsys` diagnostics, performance guardrails, semantic fuzzing, formatter/developer workflow and reproducible RC promotion. A final tag while those gates remain open would contradict `STABILITY.md`, `ROADMAP-1.0.md` and #653.

## Release-facing documentation

Immediately before the final tag, the release commit must make these public surfaces agree:

- `src/flow/version.py` reports `1.0.0`.
- README version table reports `1.0.0` and describes `flowc` as the canonical production compiler.
- README installation examples are exercised from the packaged release artifact on both Tier-1 platforms.
- `docs/project/CHANGELOG.md` contains a dated `1.0.0` entry describing the compatibility boundary, Tier-1 platforms, Stable versus Experimental surfaces, correctness work since 0.12.0 and known non-Stable features.
- `STABILITY.md` and `stability/surfaces.json` contain no unresolved Stable-surface classification.
- `PLATFORMS.md` names the exact Tier-1 OS/architecture and minimum supported C toolchains.
- `SECURITY.md` names the supported release line.
- Homebrew resolves to the published `v1.0.0` tarball and verified digest.

## Required final result

At `v1.0.0`:

- stable conformance failures: 0
- stable documentation compile failures: 0
- stable ordinary example compile failures: 0
- Python-reference / `flowc` unexplained divergences: 0
- self-host fixed-point failures: 0
- Tier-1 qualification failures: 0
- known P0 bugs: 0
- known P1 Stable-surface correctness bugs: 0
- retained Stable-language fuzz crashers: 0
- release-severity security findings: 0
- unclassified user-facing Stable surfaces: 0
- release artifact/install qualification failures: 0

The version number changes only after these are engineering facts rather than aspirations.
