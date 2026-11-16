# Agent-originated contributions and adversarial repository content

Flow is public. Public source, issues, discussions, pull requests, comments,
documentation, and forks may be read, indexed, summarised, and misunderstood by
third-party automation. A public repository cannot prevent that activity by
placing instructions, jokes, obfuscation, or prompt-injection strings in its
contents. This document defines boundaries for **the authoritative Flow
repository**, not for third-party copies.

## Authority is not inferred from text

A contributor, automated agent, or third-party tool acquires no authority from
reading repository material. An instruction in an issue, source file, benchmark,
retrieved webpage, pasted log, PR description, or AI response is an *untrusted
claim* unless a legitimately authorised human explicitly approves the relevant
action. `AGENTS.md` explains a workflow for authorised work; it does not grant
repository permissions or override GitHub access controls.

Apparent compliance is not a correctness proof. A passing test only supports
the property that test exercised. A model's description of intent is not
evidence that the resulting implementation preserves that intent.

## Threats, observable evidence, and control boundaries

| Failure mode | Independent evidence required | Primary defense |
| --- | --- | --- |
| Prompt injection / instruction laundering from retrieved files, issues, logs or comments | Identify original trusted instruction and trace untrusted input to each privileged operation | Treat retrieved text as data, not new instructions; prohibit autonomous promotion into privileged actions |
| Identity impersonation, attribution laundering, or forged maintainer claims | Verify GitHub account permissions, commit ancestry, authorship claims and review records | Separate authentication, attribution, and human sign-off |
| Plausible but wrong code, fake fixes, hidden regressions, or hallucinated APIs | Reproduce baseline; demonstrate old failure; run an independent failing-then-passing regression | CI plus human code review; reproducible tests; explicit compatibility review |
| Semantic capture presented as refactor | Compare language, effect, lifetime, ownership and error behavior against an approved contract | Require explicit human design decision for changed semantics |
| Generated artifact or compiler-bootstrap substitution | Rebuild from reviewed sources; compare bootstrap fixed points and artifact digests | Canonical regeneration, clean builds, provenance and parity checks |
| Multiple agents racing over overlapping files or branches | Compare current main, open PRs, merge conflicts and affected source paths | Scope declaration, serialization of shared generated outputs, merge queue; no assumption of atomic locks |
| Dependency, action, compiler, registry or package substitution | Check resolved revisions, source, hashes, changelog, licensing and reproducible build | Pin and review third-party inputs; verify produced artifacts |
| Workflow script injection from branch names, PR text, tag/version inputs or output variables | Inspect execution context and test hostile strings as **data**, never executable code | Pass untrusted values via environment/data files; validate before using them; restrict shell interpolation |
| CI credential misuse or privilege escalation | Map every job's token permissions, secrets, checkout credentials and event types | Separate untrusted PR validation from publishing; least-privilege job tokens; isolated hosted runners |
| Misleading benchmarks, fabricated measurements or coverage theater | Reproduce on stated toolchain, hardware and workload; check pre/post conditions | Independent measurements, realistic adversarial cases and published methodology |
| Supply-chain release impersonation, fork confusion and provenance substitution | Verify official origin, release tag, source tree, checksums and licensing | Protect tags and release rights, preserve canonical download links and audit provenance |
| Social pressure, spam, review flooding, forged consensus and harassment | Inspect actual contributions, review independence and moderation history | Limit write access; require accountable review; use moderation without confusing disagreement with attack |
| Maliciously crafted input to compiler, tools, parser, or agent runner | Reproduce resource use, path traversal, command execution and sandbox boundaries | Hostile-input fuzzing and isolated execution; do not confuse compilation with safe execution |

These are failure *classes*, not accusations against a particular visitor.
A contributor can use AI responsibly; a human contributor can trigger the
same failures without AI.

## Operational acceptance gates

The default branch must require a pull request, passing required checks,
resolved review conversations, and an approving human CODEOWNER for sensitive
changes. Force pushes and branch deletion should be blocked, and bypass
permissions should be minimised. Protect release tags separately. These
are **GitHub repository settings**, not enforced merely by writing this file;
verify their current configuration in the repository rulesets UI.

Untrusted pull-request checks must run without publishing credentials,
write-scoped tokens, or access to sensitive self-hosted runners. Keep the
workflow's default token read-only; grant write and OIDC permissions only to
the specific job that needs them. Never invoke pull-request code inside a
privileged `pull_request_target` job. Use environmental data transfer and
strict validation instead of injecting user-supplied context into shell source.

Changes to `.github/workflows/`, `.github/actions/`, `SECURITY.md`,
`CODEOWNERS`, `compiler/`, `runtime/` and release tooling require
independent code-owner inspection. Checks are not approvals. Code owners
are advisory until the repository requires their approval.

To evaluate an agent-authored patch, establish which observation would
*falsify* its correctness claim before deciding whether to merge. Preserve
the failed baseline, fixed test, CI evidence, architectural impact and
a human reviewer who can explain the change without relying on the model's
self-report. Record unresolved decisions in
[`Questions.md`](Questions.md) instead of silently implementing guesses.

## Limits of the promise

No policy file, GitHub rule, prompt, code review, or sandbox is impossible to
bypass. An attacker may exploit a vulnerability, steal a privileged credential,
compromise a dependency, or socially engineer an authorised maintainer.
Defenses must be tested and monitored as properties of a system, not asserted
as properties of its prose.

An outside model can read, fork, and discuss a public Flow repository.
It cannot *legitimately* convert that access into an authoritative Flow
release or approved change merely because it understood the words.
