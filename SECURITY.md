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

## Release security gate

Flow `1.0.0` must not ship with a known unresolved critical or high-severity
vulnerability in a Stable component. Release qualification also requires the
dependency audit and security scans defined in CI, plus disposition of relevant
findings from release fuzzing.

Tracking: #650 and the Flow 1.0 stabilisation programme #653.
