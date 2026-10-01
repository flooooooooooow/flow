# Flow language conformance corpus

This directory is the executable compatibility contract for the Stable Flow language.

Each positive `NN_*.flow` fixture identifies the authoritative `docs/LANGUAGE_SPEC.md`
section it exercises with a leading `# spec:` comment. Fixtures added to the permanent
`1.0.0` corpus must remain valid for the lifetime of the 1.x series.

`run.flow` (`./flow tool tests/conformance/run.flow`) compiles each positive fixture with flowc, builds it with cc and requires exit 42,
and requires `flowc --strict` to reject each negative fixture. The suite will expand with #641 until every Stable specification
section has positive, negative and edge-case coverage.

The 1.0 release rule is zero failures in this directory.
