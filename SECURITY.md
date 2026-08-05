# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.8.x   | ✅ |
| 0.7.x   | ✅ (security fixes) |
| < 0.7   | ❌ |

## Reporting a Vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

Please report via one of:

1. **GitHub Security Advisories** — [Report a vulnerability](https://github.com/flooooooooooow/flow/security/advisories/new) on this repository
2. Email the maintainer listed on the GitHub org / profile if advisories are unavailable

Include:

- Affected version / commit
- Reproduction steps or PoC (as minimal as practical)
- Impact assessment (RCE, path traversal, sandbox escape, etc.)

## Response

We aim to acknowledge reports within **7 days** and to ship a fix or mitigation
for confirmed high-severity issues as soon as practical. Coordinated disclosure
is preferred; please give us a reasonable window before public write-ups.

## Scope

In scope: the `flow` CLI, compiler (`src/flow/`, `compiler/`), runtime, and
stdlib as shipped from this repository.

Out of scope: third-party packages under `registry/` that are not part of a
release artifact, and VPS / personal site infrastructure.
