# Flow 1.0.0 stabilisation roadmap

> Umbrella tracker: [#653](https://github.com/flooooooooooow/flow/issues/653)
>
> This roadmap defines the release programme for turning the current 0.x language into Flow 1.0. It complements the long-term product/feature roadmap in `ROADMAP.md`; it does not replace the physical-systems vision.

## Definition of 1.0

Flow 1.0 is the first release for which:

- valid **Stable** Flow source has a documented compatibility contract for the 1.x series;
- `flowc` is the authoritative production compiler and can bootstrap without Python;
- the Stable language is covered by a specification-linked conformance suite;
- Stable documentation and ordinary examples are compiler-checked;
- supported platforms are explicitly classified and continuously qualified;
- the Stable stdlib/runtime/ABI boundary is documented;
- major accidental performance cliffs in Stable idioms are measured and dispositioned;
- release fuzzing and security qualification are part of the release gate;
- release artifacts are built reproducibly, unpacked, installed and exercised as users receive them;
- breaking Stable language/API changes require a major version or the documented emergency exception process.

Flow 1.0 does **not** mean that every item in the long-term vision is complete.

## Stability classes

Every user-facing language, stdlib, runtime, target and tooling surface must be classified before RC1.

| Class | Contract |
|---|---|
| **Stable** | Covered by the 1.x compatibility promise. Breaking changes require the deprecation/major-version process. |
| **Experimental** | Shipped and usable, but may change between minor releases. Must be visibly marked as such. |
| **Reserved/Future** | Documented design/syntax that is not part of executable Stable Flow. |
| **Internal** | Compiler/runtime implementation detail with no compatibility promise. |

Primary tracker: [#640](https://github.com/flooooooooooow/flow/issues/640).

## Workstreams

### 1. Stable surface and compatibility contract

Tracker: [#640](https://github.com/flooooooooooow/flow/issues/640)

Audit `docs/LANGUAGE_SPEC.md`, classify every surface, define source/API/ABI/CLI/manifest compatibility, and establish the 1.x deprecation policy. No ambiguous partially-stable feature may survive into RC1.

**RC1 blocker.**

### 2. Executable language conformance

Tracker: [#641](https://github.com/flooooooooooow/flow/issues/641)

Create `tests/conformance/`, organised by language-spec section. Stable positive programs must compile/run; Stable negative programs must fail at the correct Flow stage. Retain a permanent 1.0.0 compatibility corpus and run it against every future 1.x compiler.

**RC1 blocker.**

### 3. Authoritative self-hosted compiler

Tracker: [#642](https://github.com/flooooooooooow/flow/issues/642)

`flowc` becomes the canonical production compiler. The Python implementation remains the reference/bootstrap oracle. Require no-Python bootstrap, compiler self-compilation, fixed-point generations, full Stable conformance under `flowc`, and zero unexplained Python-reference/`flowc` semantic divergence.

Existing dependency: [#633](https://github.com/flooooooooooow/flow/issues/633) / [#638](https://github.com/flooooooooooow/flow/pull/638).

**RC1 blocker.**

### 4. Effect-system soundness

Tracker: [#643](https://github.com/flooooooooooow/flow/issues/643)

Resolve Stable effect coverage and first-class effect-row enforcement. Stable programs must not silently lose unhandled effects in normal mode. Tail-resumptive handlers may be the 1.0 model; abort/retry/multi-shot continuation work may remain post-1.0 if explicitly classified.

Existing dependencies: [#563](https://github.com/flooooooooooow/flow/issues/563), [#564](https://github.com/flooooooooooow/flow/issues/564).

**RC1 blocker if effects remain Stable.**

### 5. Diagnostics and DSL validation

Tracker: [#644](https://github.com/flooooooooooow/flow/issues/644)

Invalid Stable Flow must fail in Flow, with a Flow source location and an actionable diagnostic. Statically knowable DSL/FFI/shape errors must not leak into misleading generated-C failures. Formatting must not alter valid-program semantics.

Existing dependency: [#631](https://github.com/flooooooooooow/flow/issues/631).

**RC1 blocker.**

### 6. Documentation and examples: zero debt

Tracker: [#645](https://github.com/flooooooooooow/flow/issues/645)

Finish the existing compiler-backed documentation audit. Ordinary `flow` fences must have zero unverified/ignored debt. Stable examples must compile with the release compiler. Ahead-of-implementation proof notation must be clearly separated from the executable-example guarantee.

Existing dependency: [#583](https://github.com/flooooooooooow/flow/issues/583).

**RC1 blocker.**

### 7. Stable stdlib/runtime/ABI boundary

Tracker: [#646](https://github.com/flooooooooooow/flow/issues/646)

Classify stdlib modules, define runtime ABI versioning, FFI layout/calling guarantees, memory/fault/lifetime behaviour used by Stable code, and API deprecation rules. Do not accidentally freeze every experimental numerical/GPU/verification/hardware module into 1.x.

Related non-blocking expansion: [#616](https://github.com/flooooooooooow/flow/issues/616).

**RC1 blocker.**

### 8. Platform support matrix

Tracker: [#647](https://github.com/flooooooooooow/flow/issues/647)

Define Tier 1 / Tier 2 support and make CI match the public promise. Candidate initial Tier 1 platforms are macOS arm64 and Linux x86-64; final classification is a release decision. Every Tier-1 release artifact must be installed and exercised in a clean environment.

**RC1 blocker.**

### 9. Performance guardrails

Tracker: [#648](https://github.com/flooooooooooow/flow/issues/648)

Flow does not need to beat C everywhere, but Stable idioms must not hide unexplained multi-x codegen cliffs. Add deterministic guardrails around core abstractions while leaving broad/noisy benchmarks informational.

Existing dependencies: [#615](https://github.com/flooooooooooow/flow/issues/615), [#630](https://github.com/flooooooooooow/flow/issues/630).

**Required before final 1.0.**

### 10. Semantic differential fuzzing

Tracker: [#649](https://github.com/flooooooooooow/flow/issues/649)

Expand beyond short malformed-input fuzzing. Generate valid Stable Flow, compile/execute it with Python-reference and `flowc`, compare semantics, fuzz formatter round-trips and retain every discovered divergence/crash as a permanent regression. Run long campaigns for RC qualification.

**Required before final 1.0.**

### 11. Security and support lifecycle

Tracker: [#650](https://github.com/flooooooooooow/flow/issues/650)

Update the support policy, define the 1.x security lifecycle, audit compiler/runtime/package handling and resolve release-severity findings. `SECURITY.md` must match the release actually being shipped.

**Policy/high-severity review blocks RC1; all release-severity findings block final 1.0.**

### 12. Stable developer workflow

Tracker: [#651](https://github.com/flooooooooooow/flow/issues/651)

Freeze the Stable CLI/exit-code/manifest contract, make formatting deterministic/idempotent, qualify the clean install -> project -> build -> test -> package path, and make target/toolchain diagnostics actionable.

**Stable surface classification blocks RC1; complete qualification blocks final 1.0.**

### 13. Release engineering and RC promotion

Tracker: [#652](https://github.com/flooooooooooow/flow/issues/652)

The release pipeline must qualify the exact artifacts being published:

```text
commit/tag
  -> clean checkout
  -> bootstrap freshness
  -> self-host/fixed point
  -> conformance
  -> stdlib/runtime
  -> docs/examples
  -> platform matrix
  -> security/fuzz/perf gates
  -> package
  -> unpack/install in clean environment
  -> compile/run real program
  -> checksums/provenance/signing where available
  -> publish
```

**Infrastructure blocks RC1; complete qualification is required for every RC and final tag.**

## Release progression

### Stabilisation phase

New features may continue only when they are required for 1.0 or clearly Experimental/Future and do not enlarge the Stable 1.x compatibility surface.

The goal is convergence: the Stable core should become deliberately boring, deterministic and difficult to break while experimental development continues around it.

### `1.0.0-rc.1`

RC1 is the Stable-surface freeze. All RC1-blocking workstreams must meet their acceptance criteria. Stable-language/API changes after this point require release-blocker justification.

### `1.0.0-rc.2+`

Only correctness fixes, compatibility fixes, documentation, release qualification and explicitly approved blockers. Produce as many RCs as necessary; the number is not fixed in advance.

### `1.0.0`

Promote an exact commit that has already passed full RC qualification. Do not materially rebuild or alter the final release after qualification.

## Final release bar

The final tag requires:

- Stable conformance failures: **0**
- Stable documentation compile failures: **0**
- Stable ordinary example compile failures: **0**
- unexplained Python-reference / `flowc` semantic divergences: **0**
- self-host fixed-point failures: **0**
- Tier-1 platform qualification failures: **0**
- known P0 bugs: **0**
- known P1 correctness bugs in Stable surfaces: **0**
- retained fuzz crashers affecting Stable Flow: **0**
- release-severity security findings: **0**
- unclassified user-facing spec features: **0**
- undocumented Stable syntax/API: **0**
- release artifact/install qualification failures: **0**

## Explicitly not automatic blockers

The following may land if ready but do not automatically hold 1.0 unless promoted into the Stable surface:

- [#564](https://github.com/flooooooooooow/flow/issues/564) — abort/retry/multi-shot continuations
- [#592](https://github.com/flooooooooooow/flow/issues/592) — Python export override behaviour
- [#616](https://github.com/flooooooooooow/flow/issues/616) — expanded complex linear algebra/autodiff coverage
- [#525](https://github.com/flooooooooooow/flow/issues/525) — CUTLASS evaluation
- [#172](https://github.com/flooooooooooow/flow/issues/172) — GitHub Linguist registration
- W2–W6 long-term physical-system/hardware/RTL work in `ROADMAP.md`

## Tracking

[#653](https://github.com/flooooooooooow/flow/issues/653) is the release-level dashboard. Work should live in the dedicated workstream issues or existing concrete bug issues and be linked back to the umbrella tracker. New blockers must state whether they block RC1 or only the final tag.
