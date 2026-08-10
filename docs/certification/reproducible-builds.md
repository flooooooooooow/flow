# Reproducible builds (#280)

Safety certification expects the same Flow source to emit byte-identical C.

## Guarantee (Phase 2)

For a single translation unit processed by the Python C backend
(`FLOW_HOST=python`):

```bash
FLOW_HOST=python ./flow transpile prog.flow --c -o a.c
FLOW_HOST=python ./flow transpile prog.flow --c -o b.c
diff -u a.c b.c   # must be empty
```

The unit test `tests/unit/test_reproducible_c.py` asserts this for a
representative program.

## Sources of nondeterminism (mitigated)

| Source | Mitigation |
|--------|------------|
| Dict/set iteration in codegen | Prefer sorted key emission for unordered collections |
| Module discovery order | Resolver sorts discovered paths where applicable |
| Timestamps in comments | Not emitted by the C backend |

## Limits

- Parallel OpenMP / link order is outside this guarantee.
- `flowc` host and MLIR paths are not yet covered by the same test.
- Third-party `#include` expansion is environment-dependent and out of scope.
