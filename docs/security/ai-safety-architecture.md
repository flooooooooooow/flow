# Flow AI Safety Architecture (FSA): language and repository lifecycle

Status: design proposal, **not an implemented language guarantee**.
Scope: Flow compiler, runtime, agent-driven changes, CI, and release qualification.

## Security objective

An AI-authored program or repository change must not acquire authority merely by expressing an intention, generating code, passing its own tests, or selecting a different backend. Treat the model, its prompts, generated source, package metadata, build scripts, and unreviewed PRs as untrusted input.

This is primarily *containment, auditability and change governance*, not a proof of AI alignment. For example, syntactically valid code can still cause real-world harm within its legitimately granted authority.

## Existing boundaries to preserve

The current `SECURITY.md` correctly says `flow run` executes native code with invoking-user privileges; it is **not** a sandbox. FFI / extern and raw pointers are trusted boundaries. Experimental MLIR/JIT/GPU execution cannot inherit guarantees merely because the stable C backend passes tests. Experimental algebraic effects are not a production security boundary until tested end-to-end.

The existing SECURITY policy refers to 0.12.x / pre-1.0 while README declares 2.0.0. Update supported-version policy as an independently reviewed release-policy change; do not infer support windows.

## Threat model

Adversaries may control: prompts, generated Flow source, source comments, package content, import paths, logs, PR descriptions, benchmark results, and dependency metadata. An agent may also make inadvertent mistakes.

Protect: developer and CI credentials; filesystem and network access; deployed artifacts; release integrity; user data; safety checks; and continuity of human-authorised repository policy.

Trust boundaries: model -> source; source -> compiler; compiler -> backend; executable -> host OS; PR -> CI; CI -> protected branch; release job -> published artifact.

## Language-level design (proposed, not supported syntax)

1. **Effect-aware authority.** Require a closed, statically checkable declared effect set for functions and entry points. A manifest grants a subset of capabilities. Default-deny unspecified I/O, subprocesses, network, FFI, filesystem writes and secrets. Effect polymorphism must never widen authority silently.
2. **Non-forgeable capabilities.** Runtime authority must be provided by a trusted host, not constructed from strings or untrusted input. Support attenuation (restricting paths, hosts, methods, byte limits) without escalation. Revocation must be checked at the actual I/O boundary.
3. **Execution budgets.** Explicit limits for CPU/wall time, memory, allocation, recursion, emitted bytes, network egress and subprocess counts. OS isolation enforces hard limits; language checks alone are insufficient.
4. **Unsafe boundary discipline.** Raw pointers, FFI, inline native operations and backend-specific escape hatches require a named unsafe capability and audit marker. No automatic upgrade of unsafe code to a safe profile.
5. **Information-flow controls.** Track secret-tainted data across calls and effects, with explicit audited declassification. Initial implementation may be conservative; don't imply a complete noninterference proof.
6. **Observable decisions.** Generate deterministic, privacy-conscious audit events for capability grants/denials, mutations and releases, with tamper-evident provenance where feasible.
7. **Semantic invariants.** Add property-based and differential tests: safe source must not create unauthorised effects, and every backend must preserve effect and trap behavior. SMT/proof checks may supplement tests but must report proof scope and assumptions.
8. **Residual preservation.** If two agent proposals disagree, retain test results, counterexamples, unknowns and provenance separately. Do not collapse disagreement into a single confidence score. Recognition estimates must never be treated as permission grants.

Illustrative *policy model*, not Flow syntax:

```yaml
profile: untrusted-agent
allow:
  filesystem_read: ["workspace/src/**"]
  filesystem_write: ["workspace/generated/**"]
  network: []
  subprocess: []
  ffi: false
limits:
  wall_seconds: 30
  memory_mib: 512
```

A trusted launcher must validate this configuration, canonicalise roots, reject symlink escapes and enforce it in a real sandbox. A manifest without enforcement provides no security.

## GitHub repository lifecycle

**Propose -> isolate -> verify -> challenge -> review -> merge -> qualify -> release.**

* Agent PR tokens: least privilege; no release secrets, policy changes, branch-protection changes or approval/merge rights.
* Untrusted PR code: use non-privileged pull_request workflows with read-only token permissions and no secrets. Avoid executing untrusted checkout under pull_request_target or workflow_run with elevated credentials.
* Changes to `.github/workflows/`, permissions, compiler safety checks, policy, signing, packaging or dependency resolution: require independent authorised review. Self-approval must not count.
* Branch protection/rulesets: require verified checks, CODEOWNERS review for safety surfaces, up-to-date branch and review dismissal on new commits. Administration/merges controlled outside agent tokens.
* Separate build from publish: reproducible exact-commit builds; signed attestations/provenance, digest verification and immutable artifacts. Publishing privileges belong exclusively to protected release jobs.
* Every safety claim must name a threat model, tested platform/backend, evidence and exclusions. Security checks themselves should have mutation/regression tests.
* For agent disagreement, persist competing solutions and counterexamples; only merge after the selected trade-off is recorded.
* On incident: revoke compromised tokens, pause publish, preserve logs/attestations, reproduce in isolation and create an explicit retrospective.

## Qualification matrix

| Boundary | Required evidence before declaring production safe |
| --- | --- |
| Source -> compiler | Hostile-source fuzz, path handling, resource exhaustion, no code execution during compilation |
| Compiler -> C | Effect preservation, generated code tests, unsafe escape review |
| Compiler -> MLIR/GPU/JIT | Independently equivalent checks; never inherit C results |
| Runtime -> OS | Actual OS sandbox tests for file/network/exec denial, symlink traversal, quota enforcement |
| Agent -> PR | Restricted token, secrets isolation, malicious-instruction regression tests |
| PR -> protected main | Required checks and independent reviewer on safety-critical changes |
| Main -> release | Provenance, reproducibility, artifact digest/signature and controlled credentials |

## Implementation sequence

**Phase A: governance first.** Correct SECURITY.md supported versions; add threat-model docs, CODEOWNERS and safe CI permissions; configure branch rulesets in GitHub settings; add PR checklist, agent policy, and release attestations. Audit existing actions before changing them.

**Phase B: enforcement prototype.** Define a machine-readable capability manifest and parser. Integrate an explicit effect checker with diagnostic tests. Reject unsafe FFI in a safe profile. Add a sandboxed runner; do not rename `flow run` to imply containment.

**Phase C: verification.** Cross-backend differential tests, hostile-source and runtime fuzz, sandbox escape tests, taint/secret-flow tests, and CI security gate. Treat false negatives as release blockers.

**Phase D: research.** Proof-carrying optimisation certificates; refinement checking; residual-preserving agent adjudication; formally scoped noninterference for specific safe subsets. Independently measure overhead, completeness and false positive/negative rates.

## Acceptance criteria for an initial production-safe profile

A clean CI run cannot be sufficient by itself. Demonstrate that denied filesystem writes, outbound network, subprocesses and FFI fail even when generated code is adversarial; that the same manifest has equivalent behaviour across qualified backends; and that the agent cannot modify the enforcement policy or release independently. Record unavoidable trust in the OS, toolchain and deployer.

## Non-goals

This architecture does not establish that an AI has benign objectives, that all possible misuse is prevented, that passing tests implies correctness, or that experimental compiler features are already safe. Human review may also fail, so defence in depth remains necessary.
