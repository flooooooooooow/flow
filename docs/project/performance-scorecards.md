# Local performance scorecards (#727)

The performance epic is a collection of separately audited comparisons, not
one aggregate speedup. The existing `bench_harness` measures comparable Flow,
CPython and native C subjects on the same host. The `perf_scorecard` tool
classifies **one** such result file without running any benchmark or comparing
old runs from a different CPU or operating system.

Run the tools locally from the repository root:

```sh
./flow tool bench_harness --smoke --out build/perf-measurements.json
./flow tool perf_scorecard build/perf-measurements.json --out build/perf-scorecard.json
./flow tool perf_scorecard build/perf-measurements.json --strict
./flow tool tests/scripts/perf_scorecard.flow
```

For stable results, use the normal (non-`--smoke`) benchmark harness and
repeat on a quiet system. These commands are **not** a hosted CI gate.

The output schema `flow-perf-scorecard/1` preserves `source_sha`, `os` and
`cpu`, then emits an individual classification for every workload, its timing
scope, a measured Flow/Python median ratio and any available Flow/native
ratio. Summary counts do not average unrelated workloads.

A `win` means that Flow takes at most Python's time divided by 1.05. A
`loss` means Flow takes more than 1.05 times Python's time. Between these
bounds, the performance is a `tie`, or a separate `memory_win` if observed
peak RSS is at least 5% lower for Flow. Speed comparisons require verified
semantic parity, known timing scope, at least three repetitions, positive
medians and recorded per-subject dispersion at most 10% of the median.
Missing Python subjects, unresolved parity and noisy observations remain
**unscored**; they are never quietly converted to wins.

Native tax is a second, independent dimension: a Flow/native ratio above
1.05 is marked `tax`. It is not hidden by a good Python comparison.
`--strict` fails on losses, native taxes or unscored rows. Empty input and
missing source or machine metadata are input errors. These are deterministic
classification rules; they do **not** establish statistical significance.
Threshold-adjacent observations should be re-measured.

The scorecard does not implement compiler caching, MLIR passes, memory
safety or the RT callable contracts. The respective epics remain open.
Before making any headline performance claim, inspect correctness,
measurement settings, hardware identity, and the raw per-workload result
file. Run and validate all performance data locally as required by #727.
