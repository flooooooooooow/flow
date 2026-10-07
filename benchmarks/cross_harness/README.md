# Cross-dimensional Flow vs CPython benchmark cases

`./flow tool bench_harness` discovers matching subjects in two trees:

- `benchmarks/cross_harness/<suite>/<case>/`: the Flow subject
- `benchmarks/baselines/python/cross_harness/<suite>/<case>/`: the Python twin

## JSON parsing and key scanning (#747)

| Workload | Flow | CPython | What it does |
|---|---|---|---|
| `cold_json_parse` | `json_parse`, `json_get`, `json_is_int` and `json_free` from `scripts/tools/lib/json.flow` | `json.loads` and a strict `type(value) is int` check | Parses the full document 1,000 times, sums four integer fields, then checks that a malformed document is rejected |
| `cold_json_key_scan` | byte loop | `str.find` loop | Finds `"count":` 10,000 times and reads the digits after it, with no JSON validation |

Before #747 the workload named `cold_json_parse` was the key scan. Its two
programs are kept as `cold_json_key_scan`, unchanged apart from a header
comment, so older numbers
still have a home. Parser timings from this change do not compare with
scanner timings from before it.

Both parser subjects use the same JSON text and check the same total
(1,600,000). The Flow subject frees each parsed document with `json_free`
inside the loop, as CPython frees each temporary document by reference
counting. The malformed-input check runs once after the timed loop.

```sh
./flow run tests/lang/json_parser_arena.flow
./flow run benchmarks/cross_harness/cold/json_parse/json_parse.flow
./flow tool bench_harness --smoke --out benchmark-schema.json
```
