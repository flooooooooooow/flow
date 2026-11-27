# Verified synthesis: VS-00 baseline and design proposal

Part of [#1793](https://github.com/flooooooooooow/flow/issues/1793).
Baseline inspected: `f5ea0f9a917efefbde71a3d9acbefefda6b5fcba`.
This is a research proposal and finite oracle corpus, not a shipped feature,
a proof checker, a new public API or an approved change in language semantics.

## Inventory and ownership at the inspected revision

| Anchor | Observed implementation | Limitation / next owner |
| --- | --- | --- |
| `compiler/src/semantic_facts.flow` | Relation payload, provenance, status, recognition mask and support; status-based optimization gate | No proof/subject/dependency binding; VS-01 extends the existing model |
| `compiler/src/semantic_pipeline.flow` | Allocation-free ledger add/project/residual operations | No independent evidence checker; VS-01 |
| `compiler/src/dynamic_invariants.flow` | Deterministic observation miner and guarded/proven selection policy | Observation is not proof; reuse existing discovery, VS-01/03 |
| `compiler/src/proof_lower.flow` | Erases theorem and assume/therefore nodes before backend execution | Parsing and erasure are not verification; VS-02 |
| `compiler/scripts/parity_proofs.flow` | Accept/reject and proof-document parity | Does not establish theorem truth; retain parity while adding distinct checking |
| `tests/lang/test_semantic_stack.flow`, `test_dynamic_invariants.flow` (same directory) | Existing status/projection/residual and mining controls | Reuse rather than duplicate |
| [Existing compiler research](compiler-optimization-2026.md) | Restricted rule validation and deterministic extraction, with negative controls | #1668 owns extraction/optimizer work; VS-04 shares actual translation validation |
| [Recognition semantics](../language/recognition-semantics.md) | Structural fingerprints/projections | Not behavioural equivalence, numeric error or timing evidence; VS-08 |
| [Effects cookbook](../effects-showcase.md) | Typed effects and installed capability implementations | Not an information-flow security proof; VS-09 |
| [Verification design](../language/verification.md) and [flow-verify](../third-party/flow-verify.md) | Minimal proof syntax and proof-document corpus | Formal checker is not established; VS-02 |

The current optimization gate tests the status field; its return value does
not establish the truth or provenance of the status or that a guard has
actually been emitted. Do not route untrusted external evidence to this gate
without an independently checked promotion boundary. Do not change that gate
or bootstrap artifacts in VS-00.

Cross-reference #1668 (compiler research), #1713 (idiom modernization),
and #1714 (feature census). The feature census remains the owner of feature
status; this snapshot is a historical design baseline, not a second registry.

## Proposed evidence contract v0 (for review, not serialization or API)

Each obligation identifies the exact source, reference/specification and
candidate, the semantic fragment and version, assumptions, protected
observations, dependencies and target context. The relation is explicit:
equality, refinement including definedness, numerical error bound, resource
bound or a relational security property. The producer is not the authority.

An evidence record binds that obligation to the actual checker/encoding
version, input and output artifacts, resource limits, trust model and result.
An artifact proof must be checked against the exact artifact and assumptions,
not simply a producer-provided status or a matching filename. A content hash
binds identity, not correctness. Guard evidence must identify the dominated
region, guard predicate and correct generic fallback.

| Result | Meaning | Proposed authorization |
| --- | --- | --- |
| Unknown / unsupported / timeout | No established result | None |
| Refuted | Reproducible violating input or trace | Reject candidate |
| Tested | No violation in named finite sample or corpus | No promotion to unrestricted proof |
| Bounded | Exhaustive or solver-backed result for explicitly stated bounds | Only within independently checked applicable bounds |
| Guarded | Verified specialized relation under an emitted guard with correct fallback | Only in that scope |
| Proven | Independent checker establishes the stated obligation under recorded assumptions | Only for matching subject, context and scope |

Solver-reported UNSAT without an independently checked certificate is a
solver-trusted verdict, not proof-carrying code. A finite exhaustive result
can establish the relation for that exact finite model only; it does not
establish compiler/backend correctness. Unsupported or unmodeled features
must remain explicit. Do not extend the existing fact enum or stable surface
before review.

### Trust and resource decisions to review

The initial model is pure scalar booleans and fixed-width integers, with
explicit overflow and definedness semantics. Start with a restricted fragment
whose encoding can be compared to an independent reference. No unchecked
float reassociation, pointers, effects, recursion, concurrency, external I/O
or machine-code claims in the first solver slice. Distinguish Flow source
semantics from a mathematical bitvector model and from target C semantics.

The trusted base includes the specification interpretation, obligation
encoding, independent checker, artifact identity machinery, and any explicitly
trusted compiler/runtime assumptions. The candidate, LLM and external solver
output are untrusted inputs. Certificate checking reduces solver trust only
for supported certificate formats; it does not remove trust in the encoding.
A future adapter needs pinned tool versions, deterministic input and bounded
time, memory, result size and process isolation. Missing tools, exhaustion,
malformed responses and unsupported certificates yield unknown or error,
never success. Numerical budget values and stable interfaces are open design
decisions.

Specification adequacy needs separate reference, mutation and non-vacuity
checks. A valid proof of a weakened specification is not a valid replacement
for reviewed intent. Composition needs entailment between caller guarantees
and callee assumptions. Privacy requires comparison across executions with
equal public inputs and different secrets; output-only tests exclude timing,
termination, exceptions, logs, persistence and other observations.

## First executable oracle corpus

The new Flow-only test under `tests/lang/test_verified_synthesis_baseline.flow`
uses deliberately tiny integer domains and separate simple reference
implementations. It does not call a solver, compiler validator or production
optimization gate. It is an independent *reference-case corpus* relative to
future validators, not an independent interpreter of Flow semantics.

| Case | Domain | Expected positive and negative controls |
| --- | --- | --- |
| Specification adequacy | x in [-8, 8] | Multiplication equals repeated addition in all 17 cases; square-plus-one mutant fails exact specification in all 17, but passes nonnegative-only contract in all 17 |
| Non-vacuity | x in [-8, 8] | Contradictory assumption x > 8 and x < -8 has zero witnesses |
| Composition | x and local y in [-8, 8] | Stage A guarantees [-7, 9]; stage B locally doubles its admitted inputs; exactly one composed boundary violation, x=8 giving y=9; local correctness does not establish composition |
| Relational public output | public in [0,3], each secret in [0,1] | Public-only output invariant across all pairs; branching on secret creates 8 ordered-pair leak witnesses |
| Discrete invariant | state in [0,8] | Halving stays in range; increment mutant violates at state=8 only |

These are finite integer oracle cases, not claims about continuous ODEs,
floating-point behaviour, actual capability enforcement or noninterference of
compiled programs. The existing #1668 local rewrite test covers the initial
identity/effect controls. IEEE corner cases, bounded arrays, genuine stateful
DSP, continuous dynamics, actual secret sinks, and cross-backend execution
are outstanding VS-00 corpus expansions; do not mark the full package done.

### Reproduction and evidence recording

From a clean checkout, record the actual commit, host and toolchain identity
before running:

```bash
git rev-parse HEAD
git status --short
uname -a
cc --version
./flow test-lang tests/lang/test_semantic_stack.flow tests/lang/test_dynamic_invariants.flow tests/lang/test_compiler_research_contracts.flow
./flow test-lang tests/lang/test_verified_synthesis_baseline.flow
./flow tool compiler/scripts/parity_proofs.flow
```

Run the first and last existing gates at base and candidate; the new test
exists only on the candidate. Exit zero means the expected positive and
negative controls were observed, not that a new verifier is implemented.
Exit 1–4 identifies spec/non-vacuity, 5–9 composition, 10–12 relational
output, 13–15 discrete invariant. For a test sensitivity check, temporarily
replace the square mutant with the exact candidate: expected exit 2.
Replacing the leaking branch with public-only output should give exit 12.
Replacing the increment mutant with halving should give exit 15. Run each
mutation separately, restore source and record actual exit statuses; do not
commit mutations or local output.

Required repository gates remain those in AGENTS.md for language tests and
docs. Record exact commands, host/toolchain versions, logs and failures;
distinguish test failure from compile failure and from unavailable tooling.
A test passing at one SHA is not evidence for a different merge-group SHA.

At drafting time, only remote source inspection was possible: the execution
environment could not resolve GitHub for a checkout. No base/candidate
compiler tests, mutation runs, platform qualification or documentation gates
were executed. All expected results above are oracle expectations, not
reported measurements. No bootstrap or compiler source changes are required
by this slice.

## Next slice and open decisions

VS-01/02 should use the existing ledger or an internal compatible sidecar,
and a restricted typed obligation encoding. First establish valid and invalid
integer obligations with actual counterexample replay, explicit unsupported
and timeout outcomes and a reviewed promotion boundary. Then extend proof
dependency identity and certificate checking. Do not introduce new language
syntax or a second proof ledger. Review semantic fragment, encoding and trust
model with maintainers before implementation changes. The remaining VS-00
corpus, toolchain baseline and explicit design approval are still open.
