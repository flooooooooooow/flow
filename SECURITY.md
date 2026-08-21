# Security Policy

## Supported Versions

Flow is still on the pre-1.0 development line. Until `1.0.0` ships, only the
latest 0.x release line receives fixes.

| Version | Supported |
|---------|-----------|
| 0.12.x  | ✅ current pre-1.0 line |
| < 0.12  | ❌ |

When Flow 1.0 ships, the support policy becomes:

| Version | Support |
|---------|---------|
| latest 1.x minor | ✅ bug and security fixes |
| previous 1.x minor | ✅ security fixes for 90 days after the next minor release |
| older 1.x minors | ❌ |
| 0.x | ✅ security fixes for 90 days after `1.0.0`, then ❌ |

A security or correctness issue may require an otherwise incompatible change in
a supported release when preserving the old behaviour would leave users exposed
to a material vulnerability, memory-safety defect, miscompilation, or similarly
serious failure. Such changes must be called out prominently in release notes.

## Reporting a Vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

Please report via one of:

1. **GitHub Security Advisories** — [Report a vulnerability](https://github.com/flooooooooooow/flow/security/advisories/new) on this repository
2. Email the maintainer listed on the GitHub org / profile if advisories are unavailable

Include:

- Affected version / commit
- Reproduction steps or PoC (as minimal as practical)
- Impact assessment (RCE, path traversal, sandbox escape, denial of service, etc.)

## Response

We aim to acknowledge reports within **7 days** and to ship a fix or mitigation
for confirmed high-severity issues as soon as practical. Coordinated disclosure
is preferred; please give us a reasonable window before public write-ups.

## Scope

In scope: the `flow` CLI, compiler (`src/flow/`, `compiler/`), runtime, stdlib,
release/build tooling, and official packages as shipped from this repository.

Security-sensitive compiler/tooling areas include subprocess construction,
temporary/build paths, symlink and path traversal handling, imports/includes,
archive extraction, package/dependency downloads, plugin loading, hostile-source
resource exhaustion, and unsafe FFI boundaries.

Out of scope: third-party packages under `registry/` that are not part of a
release artifact, and VPS / personal site infrastructure.

## Flow 1.0 threat model

The Stable Flow 1.0 compiler must be able to parse, resolve, type-check and lower
hostile source without command injection, filesystem traversal or unintended
host code execution. Resource-exhaustion and semantic-divergence resistance are
qualified separately by the release fuzz programme.

Compiling source and executing source are different trust decisions. `flow run`
deliberately compiles and executes the supplied program with the invoking
user's privileges; it is **not a sandbox**. Likewise, `extern`, raw pointers and
other native FFI facilities are trusted-code boundaries and can perform
arbitrary process-visible actions. The local playground/native compile server
is development tooling, not a remote multi-tenant execution sandbox.

| Surface | 1.0 security position |
| --- | --- |
| Stable compiler pipeline | Hostile source must not become a shell command, escape permitted import roots, or execute host code merely by being compiled. |
| Stable subprocesses | Compiler/tool invocations use argument vectors rather than shell interpolation. Repository tests reject `shell=True`, `os.system` and `os.popen` under `src/flow`. |
| Temporary build state | Stable Python tooling uses race-resistant temporary APIs. `tempfile.mktemp` is forbidden under `src/flow`. |
| Module imports | Stable local resolution stays inside the selected project, stdlib and package roots. Legacy string imports reject absolute, home-relative and parent-traversing paths. |
| `flow run` | Native execution boundary, not sandboxed. Program exit status is propagated once execution begins. |
| FFI / `extern` | Trusted native boundary, outside safe-source containment guarantees. |
| Package/dependency acquisition | Dependency source and extraction semantics remain Experimental until integrity, symlink and root-containment rules are qualified. |
| Release artifacts | Built from a clean checkout, freshness-checked, checksummed, unpacked and exercised before publication. Provenance/signing work is tracked by #652. |
| Experimental JIT/GPU/hardware paths | Do not inherit the Stable 1.0 security guarantee unless separately promoted. |

### Release threat review

The release review explicitly covers shell/process injection, import and archive
path traversal, temporary-file races, hostile-source crashes or hangs, stale or
substituted release artifacts, unsafe native boundaries, and package extraction
escapes. New package extraction code promoted to Stable must reject absolute
archive members, `..` traversal, and symlink-mediated writes outside the package
root with regression coverage.

User-supplied compiler/linker flags are an explicit advanced trust boundary:
they may intentionally alter compilation, but source text, module names and
package metadata must never be implicitly interpolated into shell command
strings.

For each release candidate, dependency/static security scans, Stable security
invariant tests, self-host qualification and long-fuzz results are reviewed
together. A finding is release-severity when it permits unintended host command
execution, filesystem escape, artifact substitution, credential disclosure,
reliable memory corruption in a Stable compiler/runtime component, or a
comparably serious violation of this documented boundary.

## Release security gate

Flow `1.0.0` must not ship with a known unresolved critical or high-severity
vulnerability in a Stable component. Release qualification also requires the
dependency audit and security scans defined in CI, plus disposition of relevant
findings from release fuzzing.

Tracking: #650 and the Flow 1.0 stabilisation programme #653.
