# Flow Agent Operating Contract

This file is the fast entry point for coding agents working in this repository.
The full loop is in `docs/project/agentic-loop.md`. Repository placement rules
are in `docs/project/repository-structure.md`.

Do not record changing project status here. GitHub issues, pull requests, CI,
and `ROADMAP.md` are the live sources of truth.

## Before work

Read the issue or request, inspect recent commits and open pull requests, then
check the neighbouring implementation and tests.

Do not start a second implementation of work already covered by a live session
or open pull request. If the request is already fixed, prove that and stop.

Use `ROADMAP.md` for strategic priority. Correctness, security, broken CI,
release blockers, regressions, and dependency-unblocking work outrank cosmetic
cleanup and isolated micro-optimisation.

## Authority

Scoped implementation whose intended behaviour is already clear may proceed
autonomously.

New language syntax, semantics, compatibility breaks, public API contracts,
ownership/lifetime rules, effect semantics, release policy, and security policy
need an explicit design decision before implementation.

## Verification

Establish the relevant baseline before claiming a regression is caused by your
change. Run the narrow proof for the behaviour you changed, then the repository
gate appropriate to that surface.

Common gates are:

```bash
./flow test --strict --tier2
python3 -m pytest tests/unit
python3 scripts/check_doc_links.py
python3 scripts/check_doc_examples.py --check-ledger
```

Use the current CI workflow as the authoritative gate list. Do not copy current
pass/fail counts into docs.

A new regression test should demonstrate that it detects the old failure or
otherwise explain why it is a meaningful proof.

## Self-hosted compiler changes

The checked-in `compiler/bootstrap/flowc_stage_a.c` must stay byte-identical
to the C emitted from the current `compiler/src/main.flow` bundle.

When changing `compiler/src/`, regenerate the bootstrap only after source work
is complete and the Python-host self-test passes. Then verify the fixed point
and self-host scripts.

```bash
FLOW_HOST=python ./flow run compiler/src/main.flow
./compiler/scripts/bootstrap_from_c.sh --verify
./compiler/scripts/roundtrip.sh
./compiler/scripts/self_host_full.sh
```

Keep generated bootstrap updates separate from semantic source changes when
that makes review clearer. Never regenerate from a failing source tree.

## Pull requests

Keep one semantic purpose per pull request. Link the originating issue when one
exists. Record the baseline, targeted proof, repository gate, generated state,
and risk in the pull request body.

Before opening a pull request, search again for overlap. If a stronger
implementation already exists, contribute to or defer to it instead of creating
another variant.

Do not merge generated noise, benchmark-only micro-optimisations with no
relevant hot path, or cleanup that conflicts with active architectural work.

## Repository placement

`tools/` owns long-lived developer-tool implementations. `scripts/` owns
thin automation and entry shims. Do not duplicate a tool implementation across
both trees.

Changing status belongs in GitHub or generated data. Durable policy belongs in
this file, `CONTRIBUTING.md`, and `docs/project/`.

The public CLI contract is `./flow`; repository helpers should delegate to it
rather than creating an independent build path without a specific backend-test
reason.

## Session close

Leave the branch in a reviewable state. Update the linked issue, release any
claim, and update `ROADMAP.md` only when strategic state actually changed.

When a failure mode repeats, improve the loop with a test, CI rule, dispatcher
guard, template, or repository invariant instead of relying on agent memory.
