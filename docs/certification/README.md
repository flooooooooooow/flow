# Flow certification documentation

This hub tracks Flow's path toward MISRA C:2024 and CERT C alignment
(epic [#285](https://github.com/flooooooooooow/flow/issues/285)).

| Document | Purpose |
|----------|---------|
| [MISRA C:2024 compliance matrix](misra-c-2024-compliance.md) | Rule → Flow / generated-C status |
| [CERT C compliance matrix](cert-c-compliance.md) | Recommendation → Flow status |
| [Reproducible builds](reproducible-builds.md) | Deterministic C emit (#280) |
| [WCET and stack depth analysis](wcet-stack-analysis.md) | Timing and stack bounds (#282) |
| [Safety profiles](../language/safety-profiles.md) | `--profile safety\|flight` behaviour |

## How to use

1. Develop under `FLOW_PROFILE=safety` (or `flight`) for the subset that is
   mechanically enforced today.
2. Scan generated C for MISRA/CERT deviations:
   `./flow analyze --standard=misra-c-2024 build/prog.c`
3. Analyze WCET and stack depth:
   `./flow analyze prog.flow --wcet --stack-depth --budget 4096`
4. Record deviations in the compliance matrices when a rule is not yet
   machine-enforced.

## Status legend

| Status | Meaning |
|--------|---------|
| **PROVEN** | Compiler / profile enforces the rule |
| **PARTIAL** | Enforced in some modes or for some constructs |
| **DEVIATION** | Known gap with documented justification |
| **OPEN** | Not yet addressed |
| **N/A** | Not applicable to Flow's C subset |
