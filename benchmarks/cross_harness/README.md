# Cross-dimensional Flow vs CPython benchmark cases

The harness `./flow tool bench_harness` automatically discovers matching
`.flow` and `.py` subjects in the following tree:

- `benchmarks/cross_harness/<suite>/<case>/` — Flow subject
- `benchmarks/baselines/python/cross_harness/<suite>/<case>/` — Python twin

## JSON parsing versus scanning (#747)

Two intentionally distinct, matched workloads exist:

| Workload ID | Flow implementation | CPython implementation | Semantics |
|---|---|---|---|
| `cold_json_parse` | Repository JSON arena parser, `json_get`, `json_is_int`, `json_free` | `json.loads`, dict/list traversal, strict `type(value) is int` | **Full JSON grammar**, parse 1,000 complete documents, sum four integer fields, reject malformed JSON |
| `cold_json_key_scan` | Byte-oriented key-search loop | `str.find` key-search loop | **Substring search only**, 10,000 scans for four occurrences of a known key; no JSON validation |

The distinction matters: searching for `"count":` does not implement
JSON (quoted strings, escaped keys, nested structures, whitespace,
negative/fractional numbers, or malformed documents). The earlier
`cold_json_parse` workload measured only the fast key search in both
languages. That source has been **preserved** and explicitly relabelled
`json_key_scan`, so previous measurements can still be interpreted
correctly; new parser results cannot be compared to previous scanner
results as if their semantics were unchanged.

Both true parser subjects use the same JSON literal and verify the same
result (1,600,000). The Flow parser releases its per-document arena after
each iteration, just as CPython releases each temporary parsed document
through ordinary reference counting. The malformed-input rejection check
is included after the measured steady-state loop; its behavior is
validated, not timed in isolation.

```sh
./flow tool tests/bench_harness/run.flow
./flow run tests/lang/json_parser_arena.flow
./flow tool bench_harness --smoke --out benchmark-schema.json
```

**Status:** These are newly authored workload definitions and regression
tests, not published platform performance measurements. Before using their
timings for #747, run them locally, confirm matching outputs/error behavior,
check parser allocations and memory retention, and inspect generated C.
The broader #747 one-shot file transformation, buffering and end-to-end
accuracy criteria remain open.
