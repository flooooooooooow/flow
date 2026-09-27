# Flow Agentic Loop

This document defines the repository-level operating loop for coding agents.
It is the durable process contract. Live project state comes from GitHub issues,
pull requests, CI, and `ROADMAP.md`; do not copy changing counts or current
failure lists into policy files.

## Objective

Maximise verified progress per unit of review attention, not the number of
sessions, branches, commits, or pull requests created.

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
are backpressure signals, not reasons to increase concurrency.

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
should not be hand-edited.

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

Review is a semantic gate, not a formatting step. Check that the pull request
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
