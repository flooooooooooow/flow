# Flow stability and compatibility policy

This document defines the compatibility contract that begins with Flow `1.0.0`.
It is normative for release planning. `docs/LANGUAGE_SPEC.md` remains the authority
for language semantics; this file defines which parts of those semantics are promised
stable across the 1.x series.

## Stability classes

Every user-visible language, standard-library, runtime, CLI, manifest and target
surface must be assigned exactly one stability class before `1.0.0-rc.1`.

### Stable

Stable surfaces are covered by the 1.x compatibility promise.

Within 1.x, a stable program that is valid under Flow 1.0 must not become invalid
because of an incompatible grammar, type-system, semantic, standard-library, CLI,
manifest or ABI change, except for a documented security or correctness emergency.

Stable behaviour may gain new capabilities, diagnostics may improve, and performance
may change, but observable semantics must remain compatible.

### Experimental

Experimental surfaces ship for real use but may change incompatibly in a minor
release. Experimental status must be visible in the specification or focused docs.
Experimental behaviour must not be relied upon by the 1.x compatibility corpus.

### Reserved / Future

Reserved or future surfaces are documented design space, pseudocode, syntax sketches,
or recognized-but-unimplemented forms. They do not form part of the current executable
language contract.

### Internal

Internal surfaces exist for implementation, bootstrap, tests or tooling and carry no
user-facing compatibility promise.

## Versioning

Flow follows semantic-versioning intent for the Stable surface.

A patch release fixes bugs, diagnostics, packaging or security issues without adding
an intentional breaking change to Stable behaviour.

A minor release may add backwards-compatible Stable functionality and may change
Experimental functionality incompatibly.

A major release may intentionally break Stable source, library, CLI, manifest or ABI
compatibility after the deprecation process described below.

## Source compatibility

For the Stable language surface, source that is valid under `1.0.0` must continue to
parse, type-check and preserve its documented observable semantics under later 1.x
compilers, subject only to explicitly documented security/correctness exceptions.

The permanent Flow 1.0 conformance corpus is the executable compatibility baseline.
Future 1.x compilers must continue to run that corpus.

New syntax must not silently reinterpret previously valid Stable source. If a new
construct creates an ambiguity, the new construct must be changed, gated, or deferred
to the next major release.

## Standard library compatibility

Only APIs explicitly classified Stable are covered by the 1.x standard-library
promise. Stable public names, parameter meaning, return semantics and documented error
behaviour must remain compatible across 1.x.

Modules or APIs that are not ready for that promise must be marked Experimental rather
than accidentally frozen by the 1.0 release.

Adding a new Stable API is allowed in a minor release. Removing or incompatibly changing
an existing Stable API requires the deprecation process and normally a major release.

## Runtime and ABI compatibility

The runtime ABI must have an explicit version before `1.0.0-rc.1`.

ABI guarantees apply only where the documentation explicitly promises them. This
includes exported calling conventions, layout guarantees, symbol rules and FFI-visible
representations selected as Stable for 1.0.

Compiler-internal symbols and layouts are Internal unless explicitly documented
otherwise.

## CLI compatibility

Commands and flags classified Stable are part of the 1.x contract. Scripts must be able
to depend on their core argument meaning and documented exit-status categories.

Experimental backends and commands may evolve incompatibly when they are clearly marked
as such.

## Manifest and package compatibility

The stable project manifest schema must be versioned. A 1.x toolchain must continue to
accept manifests written for the 1.0 Stable schema, or provide a lossless automatic
migration path where the old form cannot remain directly supported.

Dependency-resolution behaviour that affects reproducible builds must be documented as
part of the Stable package contract before 1.0.

## Formatter compatibility

`flow fmt` must be deterministic and idempotent for the Stable 1.0 grammar.
Formatting output itself is not a source ABI, but formatter changes must not alter
program meaning and must preserve parse/format/parse equivalence.

## Deprecation policy

A Stable feature scheduled for incompatible removal or replacement must first be marked
deprecated in a 1.x release, documented with its replacement or migration path, and
remain functional for the remainder of the 1.x series unless keeping it would create a
security or correctness defect.

Normal incompatible removal happens in the next major release.

Deprecation warnings must identify the affected surface and recommended replacement when
one exists.

## Security and correctness exceptions

A Stable compatibility promise may be broken within 1.x only when preserving the old
behaviour would create a material security vulnerability, memory-safety defect,
miscompilation, unsound type-system behaviour or similarly serious correctness issue.

Such a change must be called out prominently in release notes with the affected versions,
rationale and migration guidance.

## Stability review for changes

A pull request that changes a Stable surface must answer three questions:

1. Does previously valid Stable source remain valid?
2. Does documented observable behaviour remain compatible?
3. Does the permanent 1.0 compatibility corpus need a new regression fixture?

If the answer to either of the first two questions is no, the change requires either an
Experimental boundary, a deprecation-compatible design, an approved security/correctness
exception, or the next major version.

## 1.0 release rule

No user-facing surface may remain ambiguously classified at `1.0.0-rc.1`.

The release is blocked until every user-facing language/spec feature and every shipped
public standard-library, runtime, CLI, manifest and target surface is recorded as Stable,
Experimental, Reserved/Future or Internal.

Tracking: #640 and the umbrella 1.0 programme #653.
