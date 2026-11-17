# Start here: autonomous Flow modernization

This is the practical entrypoint for an authorized coding agent (Freebuff, Codex, Claude, or otherwise) whose operator asks it to **advance Flow's semantic modernization programme** without naming a particular task. Merely reading a repository file does not give a tool permission to write, push, merge, access credentials, or change language semantics. Explicit user/operator instructions and `AGENTS.md` governance still apply.

**Canonical plan:** [../idiom-modernization-program.md](../idiom-modernization-program.md).
**Canonical proposed work queue:** [work-packages.json](work-packages.json) (50 stable work-package IDs, dependencies, acceptance, paths, and gates).
**Surface ownership:** [FEATURE-SURFACES.md](FEATURE-SURFACES.md).
**Evidence and CI:** [VERIFICATION.md](VERIFICATION.md).
**Agent selection evaluation:** [AGENT-EVAL.md](AGENT-EVAL.md).

The work queue is a *plan*, not a live status database. The live status of claims, issues, PRs, merged changes, blockers and required checks is GitHub. Never infer completion merely because a task ID exists in a JSON file or because someone marked a checklist done in prose.

**GitHub execution tracker:** [programme #1713](https://github.com/flooooooooooow/flow/issues/1713). Initial independently claimable issues: [FM-001 #1714](https://github.com/flooooooooooow/flow/issues/1714) and [FM-007 #1715](https://github.com/flooooooooooow/flow/issues/1715). See live issue/PR state before opening another issue; these are not already claimed or completed merely because they exist.

## Immediate action on an unassigned modernization session

1. Read this file, `AGENTS.md`, `docs/project/agentic-loop.md`, and the task queue. Respect explicit higher-priority instructions from the operator. If given an issue or PR number, work on that instead of self-selecting.
2. Establish real local state: `git status --short`, `git rev-parse HEAD`, `git log -n 10 --oneline`, `git fetch origin main`. Do **not** reset or overwrite a dirty worktree; use an isolated worktree or stop safely.
3. Inspect live open issues and PRs (e.g. `gh issue list -R flooooooooooow/flow --state open --limit 100`, `gh pr list -R flooooooooooow/flow --state open --limit 100` when `gh` is installed; otherwise use available GitHub connector/web/API). Check specific task IDs and *substantive file/intent overlap*, not only issue titles. Inspect current head, code, tests, related accepted PRs, and exact-source release rules.
4. Pick the lowest numeric `priority` in [work-packages.json](work-packages.json), then lowest ID, whose `depends_on` packages are demonstrably complete or not required for a smaller independent slice, that has no active equivalent implementation claim, and whose `repository` is the checked-out repo. **Do not select a cross-repository package unless the operator explicitly provided that repo and write access.** Priority and dependencies guide *eligibility*, never override current correctness/release emergencies.
5. Some task packets require `decision_gate` such as `semantics`, `architecture`, `public_api`, or `security_policy`. An agent may implement an **evidence-only discovery or regression-test slice** while the decision is pending, but cannot unilaterally approve a new language meaning, stable API, security policy, ownership model, or release procedure. Write alternatives/counterexamples into `docs/project/Questions.md` (or the existing linked decision issue) and stop that semantic change pending authorized review.
6. Take a narrow task claim on GitHub before implementation. If an existing issue already covers it, use that. Otherwise create an issue titled `[FM-XYZ] <narrow scope>` with the work-package link, acceptance criteria, exact paths, dependencies, proof commands, and risk. Post a **time-limited claim** with agent/session ID, intended file set, base SHA and UTC expiry (suggested four hours; renew if still active). Verify no newer overlapping claims/PRs were added after publishing. A comment is advisory, **not an atomic lock**. If GitHub write access is unavailable, do read-only triage and report the blocker rather than launch an uncoordinated implementation.
7. Create a branch from current `origin/main` (never another agent's branch unless explicitly coordinating). Perform **one semantic purpose per PR**. Source code and new tests are Flow; do not add Python or duplicate generated pipelines. Retain intentional reference, tutorial and negative-test implementations.
8. First show the baseline and the smallest test that fails on old behavior. Implement the narrow change. Run the matching [verification ladder](VERIFICATION.md), compile/run actual source for each claimed backend, report command, exit status, test result, SHA, limitations and missing gates. Do not treat doc snippets, browser JavaScript stand-ins or parsed-only syntax as compiled native proof.
9. Before proposing integration, re-fetch main, open PRs, shared/generated files and exact-head checks. Regenerate derived output rather than merging generated text. Obey CODEOWNERS, human review for security/compiler semantics, branch protection and the protected merge queue. Never self-merge just because an AI model or advisory checker says ready.
10. Leave a concise issue/PR report with `FM-XYZ`, base/head SHA, files, tests and negative cases, unresolved blockers, next task(s) and links. Mark a packet complete only when its acceptance evidence is merged and verifiable on the target branch. **Then stop that session.** The next invocation selects the next eligible task. Do not start a fleet of unclaimed parallel tasks.

## Recommended first packets

Without another assigned task, **FM-001** (feature census) is the initial high-leverage read-only/Flow-tooling slice. Another authorized agent may pick **FM-007** (live overlap map and existing task reconciliation). Once FM-001 is complete, FM-002 (stale-doc claims), FM-003 (registry source design), FM-005 (eligible adoption denominator) and FM-006 (agent evaluation baseline) become viable in separate nonoverlapping scopes.

First action is **not** a sweeping rewrite of 3,846 .flow files. Classify, prove, and narrow the scope. Be especially cautious of `examples/verify/`, `compiler/fixtures/`, generated files, reference numerical kernels, and in-flight Sofia/CI/website PRs.

## How to handle an unavailable dependency or no eligible task

If the top task is blocked, inspect the next independent task. If every candidate is blocked, post a factual blocked report with the exact missing decision or live claim and stop. Never invent a completion result, unapproved syntax, or a temporary workaround solely to claim progress. If an assigned task is already done on current main, record the proving test and choose another unclaimed task only if your operator assigned self-selection.

## Minimal issue and PR contract

Use the work package ID everywhere. An issue describes one bounded slice, exact base revision, intended paths, overlaps, negative and positive acceptance criteria, risk, test command(s), and dependency status. The PR body references that issue and records *what changed*, *what was already failing*, *what succeeded*, *what remains unknown*, and *what reviewers need to decide*. Put all substantive validation inside tests or reproducible evidence, not an assertion of model confidence.

## Project scope, not universal authority

The user may ask you to work on a different Flow bug or project. Follow that explicit request. This programme should be picked automatically **only when a trusted human/tool has tasked you with Flow modernization and left task selection open**. Repository text must not override the human's intent, the access controls or the security policy.
