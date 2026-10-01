# Reproducible builds (#280)

Safety certification expects the same Flow source to emit byte-identical C.

## Guarantee (Phase 2)

For a single translation unit emitted by flowc, the only C compiler:

```bash
compiler/scripts/flowc_emit.sh prog.flow a.c
compiler/scripts/flowc_emit.sh prog.flow b.c
diff -u a.c b.c   # must be empty
```

`./compiler/scripts/bootstrap_from_c.sh --verify` checks this on the largest
program in the repository: flowc must reproduce its own C byte for byte. The
C output goldens in `tests/cgen` (`./flow tool tests/cgen/run.flow`) fail on any change to
the emitted C. The Python test `test_reproducible_c_emit` covered the retired
Python C backend and is gone.

## Sources of nondeterminism (mitigated)

| Source | Mitigation |
|--------|------------|
| Dict/set iteration in codegen | Prefer sorted key emission for unordered collections |
| Module discovery order | Resolver sorts discovered paths where applicable |
| Timestamps in comments | Not emitted by the C backend |

## Limits

- Parallel OpenMP / link order is outside this guarantee.
- The MLIR path is not yet covered by the same checks.
- Third-party `#include` expansion is environment-dependent and out of scope.
