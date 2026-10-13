# Security Policy

## Supported Versions

Flow 2.0.0 is the current supported release line.

| Version | Supported |
|---------|-----------|
| 2.0.x   | ✅ current release line |
| 1.x     | ❌ security fixes ended |
| 0.x     | ❌ security fixes ended |

When a security or correctness issue requires an incompatible change in a
supported release to protect users from a material vulnerability,
memory-safety defect, miscompilation, or serious failure, the change is
called out prominently in release notes.

## Reporting a Vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

Please report via one of:

1. **GitHub Security Advisories**: [Report a vulnerability](https://github.com/flooooooooooow/flow/security/advisories/new) on this repository
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

In scope: the `flow` CLI, compiler (`compiler/`), runtime (`runtime/`), stdlib (`lib/`),
release/build tooling, and official packages as shipped from this repository.

Security-sensitive compiler/tooling areas include subprocess construction,
temporary/build paths, symlink and path traversal handling, imports/includes,
archive extraction, package/dependency downloads, plugin loading, hostile-source
resource exhaustion, and unsafe FFI boundaries.

Out of scope: third-party packages under `registry/` that are not part of a
release artifact, and VPS / personal site infrastructure.

## Threat model

The Flow compiler must be able to parse, resolve, type-check and lower
hostile source without command injection, filesystem traversal or unintended
host code execution. Resource-exhaustion and semantic-divergence resistance are
qualified separately by the release fuzz programme.

Compiling source and executing source are different trust decisions. `flow run`
deliberately compiles and executes the supplied program with the invoking
user's privileges; it is an ordinary execution environment, without a sandbox.
Likewise, `extern`, raw pointers and other native FFI facilities are trusted-code
boundaries and can perform arbitrary process-visible actions. The local
playground compile server is development tooling, without remote multi-tenant
sandboxing.

| Surface | Security position |
| --- | --- |
| Stable compiler pipeline | Hostile source must not become a shell command, escape permitted import roots, or execute host code merely by being compiled. |
| Subprocesses | Compiler and tool invocations use argument vectors rather than shell interpolation. Subprocesses run without intermediate shells. |
| Temporary build state | Build tooling uses race-resistant temporary directory APIs. |
| Module imports | Stable local resolution stays inside the selected project, stdlib and package roots. Legacy string imports reject absolute, home-relative and parent-traversing paths. |
| `flow run` | Native execution boundary; it is not sandboxed. Program exit status is propagated once execution begins. |
| FFI / `extern` | Trusted native boundary, outside safe-source containment guarantees. |
| Package/dependency acquisition | Dependency source and extraction semantics remain Experimental until integrity, symlink and root-containment rules are qualified. |
| Release artifacts | Built from a clean checkout, freshness-checked, checksummed, unpacked and exercised before publication. Provenance/signing work is tracked by #652. |
| Experimental JIT/GPU/hardware paths | Do not inherit the Stable 1.0 security guarantee unless separately promoted. |
| AI Agent Lifecycle | Flow repository governance treats AI-generated code as untrusted. AI agent tools and safe subsets require human code review for policy changes and OS sandbox validation before execution. |

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

Production releases must not ship with a known unresolved critical or high-severity
vulnerability in a Stable component. Release qualification also requires the
dependency audit and security scans defined in CI, plus disposition of relevant
findings from release fuzzing.
