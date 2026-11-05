# Flow Agentic Loop

This document defines the repository-level operating loop for coding agents.
It is the durable process contract. Live project state comes from GitHub issues,
pull requests, CI, and `ROADMAP.md`; do not copy changing counts or current
failure lists into policy files.

## Objective

Maximise verified progress per unit of review attention. The number of
sessions, branches, commits or pull requests created is not a measure of it.

The loop is:

`intake -> triage -> claim -> plan -> implement -> verify -> review -> merge -> learn`

A work item may move backwards when evidence invalidates an assumption. It must
not skip claim, overlap detection, or verification.

## Sources of truth

Use these in this order when they disagree:

| Question | Source |
|---|---|
| What is open or already being implemented? | GitHub issues and pull requests |
| Is the tree healthy? | CI for the relevant commit plus a local baseline when available |
| What is strategically important? | `ROADMAP.md` and linked design trackers |
| What is stable language behaviour? | Tests, `docs/LANGUAGE_SPEC.md`, and working examples |
| How should an agent operate? | `AGENTS.md` and this document |
| How should a contributor package a change? | `CONTRIBUTING.md` |
| How is the repository laid out? | `docs/project/repository-structure.md` |

Static prose must never claim a current test count, open-issue count, active
agent count, or current list of failures.

## External Orchestrator integration (optional)

The [Orchestrator control plane](https://github.com/godofecht/Orchestrator)
can observe Flow's GitHub issues, pull requests, and exact-head check runs,
detect possible duplicate work, and submit *policy-eligible* changes to
GitHub's existing merge queue. Orchestrator is maintained in a separate
(private at initial integration) repository. Its implementation is **not**
a required part of building, testing, or contributing to Flow.

**Authority remains here.** GitHub issues/PRs, branch rules, CODEOWNERS,
the protected merge queue, and the test suites listed in `AGENTS.md` remain
the source of truth. An Orchestrator status such as "ready" means only that
an external policy evaluator considers its narrow delegated action eligible.
It is not a compiler correctness certificate, a human design approval, a
security review, a release qualification, or permission to bypass any Flow
merge gate. Never accept an agent-written CI summary in place of actual
GitHub checks for the exact proposed integration SHA.

### Current operational scope

The first integration is **pull-based**: Orchestrator periodically queries
Flow's GitHub API and runs read-only reconciliation, and its own CI validates
that it can actually read the live Flow repository. Write operations need a
separately configured, restricted `ORCHESTRATOR_GH_TOKEN` in Orchestrator,
not a secret committed to this repository. The initial policy permits
auto-merge submission only for small, non-governance Markdown changes under
`docs/`, after explicit, trusted and current CI checks pass. No generated
compiler artifacts, language semantics, CI/security policies, release
operations, or public APIs are delegated under that policy.

An unconfigured token, missing scheduled run, failed API request, stale SHA,
unknown mergeability, conflicting PR, or uncertain test result must never be
interpreted as successful automation. GitHub reconciliation may fall behind
webhooks or scheduled triggers; agents must always consult GitHub directly
immediately before starting a task and immediately before integration.

### Mapping to the repository lifecycle

| Flow phase | Orchestrator role | Final authority |
|---|---|---|
| Intake / triage | Observe open issues/PRs; scan live file-level overlap, derived artifacts and duplicate closing issues | GitHub issues, PRs, roadmap |
| Claim / plan | Produce a dependency-aware plan; append-only issue leases exist but **claim writes are disabled** by current policy | This contract and explicit agent claims |
| Implement | Any selected agent may follow the Orchestrator file preflight; provider launch is optional and not part of scheduled reconciliation | Isolated implementation agent, reviewable branch |
| Verify | Inspect exact-head checks and run a read-only `git merge-tree` probe for precise conflict paths; a local worktree helper may stage generated-only resolutions without executing code | GitHub Actions, bootstrap fixed-point, baseline and targeted proof |
| Review | Reject ambiguous or policy-sensitive changes from unattended merge | Flow CODEOWNERS, semantic review |
| Merge | Submit a narrowly authorized exact head for GitHub auto-merge | Protected merge queue and merge-group CI |
| Learn | Store audit reports and detected duplicate work; Locus-based feedback **planned** | Durable evidence, regression tests, issue history |

The [Orchestrator integration roadmap](https://github.com/godofecht/Orchestrator/issues)
covers enforced cross-agent path claims, full compiler regeneration/integration
repair, and evidence-aware Locus scheduling. File-overlap preflight, a disabled
lease-history model and exact Git merge-tree diagnostics now exist; **cross-agent
file locking, independently verified automatic regeneration and production
compiler merge repair remain unfinished**.
Deliberately competing implementations in a research experiment must remain
distinguishable from accidental duplicate PRs; incidental generated-file
conflicts should be repaired without erasing meaningful alternatives.

## Intake and triage

Before starting implementation, inspect the issue, recent commits, open pull
requests, and neighbouring code. Determine whether the request is already
fixed, already in flight, blocked by another change, a design question, or an
implementation task.

Correctness, security, broken CI, release blockers, regressions, and changes
that unblock several other tasks outrank cosmetic cleanup and micro-
optimisation. A benchmark result is not a priority signal by itself.

Do not create implementation work merely because an issue exists. An issue is
eligible only when it has a concrete outcome, a verification path, and no
active overlapping implementation.

## Claim and deduplication

There must be at most one active implementation for the same issue and change
intent unless an explicit comparison experiment calls for alternatives.

A dispatcher must check all of the following immediately before creating a
session:

1. Is there a live session for this issue?
2. Is there an open pull request that closes, references, or materially overlaps
   the issue?
3. Is another issue asking for the same semantic change or the same narrow file
   edit?
4. Is the dependency that this work needs already being changed by an open pull
   request?
5. Has the configured global work-in-progress limit been reached?

The implementation claim should be visible on GitHub, not only in a local JSON
file. A claim may be represented by a label or a machine-readable issue
comment containing the provider/session identifier and timestamp. Claims need
a lease so abandoned sessions do not block the queue forever.

Local state is a cache. GitHub is authoritative.

## Backpressure

The dispatcher must have configurable limits for active implementation sessions
and unreviewed agent pull requests. When either limit is reached, it stops
creating work and spends capacity on verification, review, rebasing,
deduplication, or closing superseded work.

The system must prefer finishing existing work over opening more work.

Repeatedly refused sessions, repeated CI failures, or a growing review queue
are backpressure signals. Respond by lowering concurrency.

## Planning boundary

Agents may autonomously implement a scoped bug fix, test, documentation repair,
mechanical refactor, or already-approved roadmap item when the intended
behaviour is clear.

A new language construct, syntax change, compatibility break, public API
contract, ownership/lifetime rule, effect semantics change, release policy, or
security-policy change requires an explicit design decision before
implementation. Record unresolved design questions in the project design
tracker rather than inventing a local convention.

## Implementation

Keep one semantic purpose per pull request. Prefer the smallest change that
proves the issue resolved. Do not add speculative adjacent features.

Read neighbouring code before introducing a new pattern. Reuse canonical tools
and directories. Do not create a second implementation tree because an existing
location is inconvenient.

Generated files must be regenerated from their source. Generated artifacts
should not be hand-edited, and a conflict in one is resolved by taking
`main`'s copy and regenerating, never by merging its text. The conflict
hotspots, the regeneration commands and the branch rules are in
"Branches, pull requests and merge conflicts" in `AGENTS.md`.

For `compiler/src/`, follow the bootstrap rules in `AGENTS.md` and keep the
generated bootstrap C at a fixed point.

## Verification

First establish whether the relevant baseline is already failing. Then verify
the changed behaviour using the narrowest test that could have caught the bug,
followed by the repository gate required for the touched surface.

A useful test must fail for the old behaviour or otherwise demonstrate that it
would detect the regression.

Every pull request must state:

| Evidence | Required content |
|---|---|
| Baseline | Relevant pre-existing failures, if any |
| Targeted proof | The test/example/benchmark that exercises the change |
| Regression proof | Why the proof would fail without the change |
| Repository gate | CI or local suite appropriate to the touched surface |
| Generated state | Whether generated/bootstrap files changed and how they were produced |
| Risk | Compatibility, performance, security, lifetime, or backend implications |

"Tests pass" without naming the tests is not evidence.

## Review and merge

Review is a semantic gate. Check that the pull request
still solves the original issue, does not overlap newer work, contains no
unrelated changes, and has credible verification.

Do not merge a low-value micro-optimisation merely because its microbenchmark is
positive. Require a relevant hot path, end-to-end effect, or a clear
maintainability benefit.

When two pull requests overlap, keep the stronger verified implementation and
close or redirect the other before creating further variants.

After merge, close or update the linked issue, release the claim, and update the
roadmap only if the strategic state changed.

## Learn

When the same failure mode occurs twice, improve the loop instead of relying on
future agents to remember it. Typical loop fixes are a regression test, CI
check, repository invariant, issue template, dispatcher rule, or documentation
change.

The agent loop itself is part of the codebase and should be reviewed with the
same evidence discipline as compiler changes.
