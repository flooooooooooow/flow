# Compile-to-result phase profile

Parent: [#735](https://github.com/flooooooooooow/flow/issues/735) (epic [#727](https://github.com/flooooooooooow/flow/issues/727)). Related: [#728](https://github.com/flooooooooooow/flow/issues/728), [#736](https://github.com/flooooooooooow/flow/issues/736), [#746](https://github.com/flooooooooooow/flow/issues/746), [#748](https://github.com/flooooooooooow/flow/issues/748).

`FLOWC_PROFILE=1|json` makes flowc emit per-phase wall times. `./flow tool compile_bench` turns those into cold/warm compile-to-result rows for tiny/medium/large programs, including self-hosted flowc with no Python on PATH.

This page is the measurement contract. Live numbers come from `compile_bench` on the machine under test. Do not treat a stored millisecond as a cross-machine regression ([#727](https://github.com/flooooooooooow/flow/issues/727)).

## How to measure

```
FLOWC_PROFILE=json FLOWC_BUNDLE=1 FLOWC_IN=examples/basics/hello_world.flow \
  FLOWC_OUT=/tmp/hello.c "$(./flow tool --path compiler/scripts/flowc_host.flow)"

./flow tool compile_bench --host
./flow tool compile_bench --repeat 3 examples/basics/hello_world.flow
```

`FLOWC_PROFILE` is opt-in. Unset / `0` / `false` / `off` / `no` performs one cached `getenv` check but **does not call `clock_gettime` from the compiler's pre-main constructor**. This avoids charging every ordinary compile with an unrequested profiler timestamp. An explicitly enabled profile still captures its startup timestamp in the constructor. It is not `FLOW_PROFILE` (safety/flight) and not `FLOW_MEM_PROFILE` (runtime heap).

JSON is one stderr line:

```
[flow-profile] {"schema": "flow-compile-profile/1", "phases": [...], ...}
```

`compile_bench` copies that object into each program row as `profile` plus `phase_<name>_ms`. After the rows it prints a summary and a Tier-1 matrix object (`flow-compile-profile-matrix/1`).

## Phases

| Phase | What it times |
|---|---|
| `startup` | Process start until flowc begins the job |
| `source_read` | Reading entry and imported sources |
| `parse` | Lexer/parser and DSL expansion on a cache miss |
| `incremental_cache` | AST cache probe: hits, and the miss lookup |
| `import_resolution` | Gathering and resolving imports |
| `typecheck` | Semantic check and typecheck |
| `monomorphize` | Generic specialization inside C emit |
| `lowering` | Proof erasure, unsupported-node refusal, sort/find plan selection |
| `codegen` | Remaining C/MLIR/JS text emission (mono/lowering carved out) |
| `cc` / `external_compile` | Host `cc` on the emitted C (`compile_bench`) |
| `run` / `process_launch` | Launching the linked program (`compile_bench`) |

MLIR/JIT steps beyond `codegen` stay in that bucket; [#748](https://github.com/flooooooooooow/flow/issues/748) covers JIT time-to-first-result.

## Tier-1 measurement matrix

Tier-1 platforms are Linux x86-64 and macOS arm64 ([CHANGELOG](CHANGELOG.md)). `compile_bench` records one matrix row for the host it runs on:

| Field | Meaning |
|---|---|
| `os` / `arch` | `uname -s` / `uname -m` |
| `tier1_slot` | `linux-x86_64`, `macos-arm64`, or `other` |
| `tier1` | true when the slot is a Tier-1 platform |
| `sizes` | `tiny`, `medium`, `large` |
| `tiny` / `medium` / `large` | Stock programs: `examples/basics/hello_world.flow`, `examples/basics/fibonacci.flow`, `compiler/src/main.flow` |
| `*_total_ms` | Warm compile-to-result (`emit` + `cc` + `run`) |
| `top_fixed` / `top_scaling` | Phase that changes least / most with program size |
| `bottlenecks` | Every phase that is >10% of compile-to-result or of emit, with a follow-up issue |

Fill both Tier-1 slots by running the same command on each host and keeping the JSON next to the source SHA. A Linux x86-64 row is produced wherever that is the build machine; the macOS arm64 slot is the same schema, other host.

Cold hello / tiny-job compile-to-result is a tracked [#727](https://github.com/flooooooooooow/flow/issues/727) dimension (`cold_total_ms` on the hello row).

## Follow-ups for >10% phases

`compile_bench` attaches `followup` to each bottleneck. The mapping:

| Phase | Typical where | Follow-up |
|---|---|---|
| `import_resolution`, `parse`, `source_read`, `incremental_cache`, `typecheck`, `monomorphize` | Tiny jobs and warm incremental rebuilds | [#736](https://github.com/flooooooooooow/flow/issues/736) incremental AST / frontend cache |
| `codegen`, `lowering`, `emit` | Large modules | [#729](https://github.com/flooooooooooow/flow/issues/729) codegen taxes |
| `cc` / external compile and link | Compile-to-result, especially hello | [#728](https://github.com/flooooooooooow/flow/issues/728) compiler suite (C toolchain launch) |
| `startup`, `run` / process launch | Hello and one-shot CLIs | [#746](https://github.com/flooooooooooow/flow/issues/746) compiled-program cold start |
| MLIR/JIT beyond `codegen` | JIT first result | [#748](https://github.com/flooooooooooow/flow/issues/748) |

A phase that is >10% and has no row here is a remaining gap on #735.

## Schema

`flow-compile-profile/1` phase objects: `name`, `ms`, `us`. Totals: `source_loc`, `ast_nodes`, `total_ms`, `startup_ms`, `loc_per_s`, `ast_nodes_per_s`.

`compile_bench` program rows keep `emit_ms`, `cc_ms`, `run_ms`, `total_ms`, `cold_total_ms`, `warm_total_ms`, `reps`, `loc_per_emit_s`.
