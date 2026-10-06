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

`FLOWC_PROFILE` is opt-in. Unset / `0` / `false` / `off` is a no-op besides one `getenv`. It is not `FLOW_PROFILE` (safety/flight) and not `FLOW_MEM_PROFILE` (runtime heap).

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

## AST cache correctness and trust boundary (#736)

Stage-A uses an optional content-addressed AST snapshot in
`$HOME/.cache/flow/ast/`. The compiler's salt includes the Flow compiler
version, an explicit **AST cache schema (737)**, and the optional
`FLOW_CACHE_SALT` override. The schema must be bumped whenever parser
semantics or `AstNode` binary layout change without a compiler version bump.
An old schema never counts as a cache hit.

Unlike general project-local caches, this binary snapshot is only trusted
from **owner-controlled directories**. The compiler verifies the real
`$HOME` and `.cache` paths are owned and not group/other writable; the
`flow` and `ast` subdirectories must be owner-only (mode 0700). It
refuses symlink components, and opens snapshot files only if they are
regular single-link files owned by the same effective user with no
group/other access (mode 0600). Read-time inode/device checks prevent
opening a different file through a pathname replacement. Writes use
exclusive creation, not `fopen("wb")`, so an existing file or symlink
cannot be overwritten.

Snapshots carry a schema, node count, root index, source byte length and
two halves of a 64-bit AST payload hash. Invalid/truncated/oversized
snapshots, bad root IDs, incorrect root kinds or checksum failures are
**cache misses**: the original Flow source is reparsed. The payload hash
detects accidental corruption; it is **not** a cryptographic
authentication tag. The owner-only filesystem boundary is essential.

When any check cannot be established, compilation continues without the
disk cache. Existing `~/.cache/flow` directories with permissive
permissions are intentionally rejected; users may migrate them to 0700
and discard old 736-format snapshots to restore caching. Snapshot files
that fail validation are not overwritten; remove obsolete entries to
allow a fresh exclusive-create.

Validate a freshly built Flow compiler locally:

```sh
./compiler/scripts/bootstrap_from_c.sh --regen
bash tests/scripts/ast_cache_security.sh
./flow tool tests/scripts/incremental_cache.flow
```

The shell fixture exercises isolated-HOME mode checks, cache hits,
corrupted-header fallback, refusal of insecure directories and symlink
parents. **Neither the host C helper test nor a source-only inspection
is a substitute for these actual Flow executions.** This secures the
current parsed-AST cache slice; it does not yet implement
dependency-aware typechecked, monomorphized or generated-code fragment
caches, which remain open under #736.
