# Flow 1.0 compiler and toolchain threat model

This document records the security boundary for the Stable Flow 1.0 compiler, runtime-facing developer tools, module resolution and release artifacts. It is intentionally narrower than a claim that arbitrary Flow programs are safe to execute. Compiling source and executing source are different trust decisions.

## Security boundary

| Surface | 1.0 security position |
| --- | --- |
| Parsing, resolving, type checking and C generation | Must accept hostile source without command injection, path traversal or unintended host code execution. Resource-exhaustion findings are tracked through the release fuzz programme. |
| `flow run` | Deliberately executes the program supplied by the user. It is not a sandbox and must not be used to execute untrusted Flow source. The compiler and C compiler are invoked with argv lists rather than shell command strings. |
| Module imports | Stable local import resolution must stay inside the explicitly selected project, stdlib and package roots. Legacy string imports reject absolute paths, home-relative paths and parent traversal. |
| Temporary build state | Stable Python tooling must use race-resistant temporary-directory APIs. `tempfile.mktemp` is forbidden in `src/flow`. |
| FFI / `extern` | A trusted-code boundary. Native calls can perform arbitrary process-visible actions and are not sandboxed by Flow. |
| Package/dependency acquisition | Any package path promoted to Stable must define integrity, extraction and root-containment rules before 1.0. Release qualification must not infer trust from an archive filename alone. |
| Release artifacts | Artifacts are built from a clean checkout, checksummed, unpacked in a clean environment and exercised before publication. Provenance/signing work is tracked by #652. |
| Playground/native compile server | Development tooling, not a remote multi-tenant execution sandbox. Its loopback default, request cap and subprocess timeouts are defence in depth rather than a promise that hostile native programs are contained. |
| Experimental JIT/GPU/hardware backends | Outside the Stable 1.0 security guarantee unless separately promoted by the stability and platform processes. |

## Threat review

| Threat | Current control | Release requirement |
| --- | --- | --- |
| Shell injection through compiler/tool invocations | Stable Python subprocesses are argv-based; repository regression tests reject `shell=True`, `os.system` and `os.popen` under `src/flow`. | The security invariant tests remain green on every release candidate. |
| Import/path traversal | Legacy string imports reject absolute, `~` and `..` paths before resolution. Relative dot imports resolve from selected roots rather than accepting filesystem parent notation. | Traversal regression coverage remains required; any new package extractor must use resolved-path containment checks. |
| Temporary-file race or predictable build path | Stable runner paths use `tempfile.mkdtemp`; a repository test rejects `tempfile.mktemp` in `src/flow`. | No predictable temporary-name API in Stable toolchain code. |
| Malicious source causing compiler crash/hang | Parser and pipeline fuzzing exists today. | #649 adds valid-program, differential and longer RC fuzz campaigns; retained Stable crashers must be zero at final 1.0. |
| Generated native code escaping a sandbox | There is no sandbox promise. `flow run` and FFI execute native code with the invoking user's privileges. | Documentation and CLI must keep this trust boundary explicit rather than implying containment. |
| C compiler option injection | Core commands build argv lists. Explicit user-provided compiler flags are a trusted advanced input and can intentionally alter compilation. | No implicit interpolation of source text, module names or package metadata into shell commands. |
| Release archive substitution or stale compiler | Self-host/bootstrap freshness checks and archive-use qualification are part of CI. | #652 must publish checksums/provenance and qualify the exact RC commit promoted to `1.0.0`. |
| Dependency/package archive traversal | Not yet accepted as a Stable guarantee simply because package concepts exist in the tree. | Before package acquisition/extraction is classified Stable, extraction must reject absolute entries, `..`, symlink escapes and writes outside the package root, with regression tests. |
| Unsafe native boundary misuse | `extern`, raw pointers and unsafe facilities can violate memory/process safety by design. | The Stable spec must identify the unsafe boundary; safe code must not cross it implicitly. |

## Release review procedure

For every 1.0 release candidate, dependency/static security scans, the Stable security invariant tests, compiler self-host qualification and the long fuzz results are reviewed together. A finding is release-severity when it permits unintended host command execution, filesystem escape, artifact substitution, credential disclosure, reliable memory corruption in Stable runtime/compiler code, or a comparably serious violation of the documented boundary.

`1.0.0` must ship with no known unresolved critical or high-severity finding in a Stable component. Lower-severity findings may remain only when their scope and mitigation are documented and they do not contradict a Stable guarantee. Experimental components retain their explicit status rather than silently inheriting the Stable guarantee.

## Follow-up tracks

The remaining work is intentionally tracked rather than hidden in this document. #649 owns long semantic/fuzz qualification, #650 owns the security review and support lifecycle, #652 owns release provenance/artifact qualification, and #646 owns the Stable runtime/FFI/memory boundary.
