# examples/systems: low-level systems programming

Allocators, hash tables, ring buffers, and the flagship *Tiny Pointers*
construction (arXiv:2111.12800). Every program here prints what it measured
and gates its exit code on a self-check (exit 0 = PASS).

- `arena_frame.flow` - arena + bump-frame allocation
- `manual_memory.flow` - manual malloc/free discipline
- `memory_pool.flow` - O(1) pool allocator over a fixed arena
- `ring_buffer.flow` - lock-free SPSC queue
- `hash_table.flow` - open addressing hash table
- `system_info.flow` - OS/CPU info via stdlib
- `tiny_pointers.flow` - o(log n)-bit pointers (arXiv:2111.12800), from the
  fixed-size two-level dereference table to the optimal internal-memory stash
  — every phase self-verifies against a registry model, and the benchmarks are
  in `scripts/bench_tiny_pointers.sh`

## tiny_pointers.flow

```bash
FLOW_HOST=python ./flow run examples/systems/tiny_pointers.flow
```

The run output opens with an **Abstract-claim coverage** map: each promise in
the paper's abstract (the two pointer results and the five applications)
linked to the theorem, phases and paper section that measure it. The same map
is mirrored as a collapsible card on the example's page in the WebAssembly
gallery (`site/wasm/tiny_pointers/`) and is printed after the table by
`scripts/bench_tiny_pointers.sh`.

The map mirrors the coverage tables in the docs — the theorem table in
[docs/library/tiny-pointers.md](../../docs/library/tiny-pointers.md) and the
application-④ deep dive in
[docs/library/tiny-pointers-variable-values.md](../../docs/library/tiny-pointers-variable-values.md#abstract-claim-coverage).
