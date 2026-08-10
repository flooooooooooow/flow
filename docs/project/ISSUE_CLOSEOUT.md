# MISRA / CERT closeout (Phase 0+)

Tracking for the MISRA C:2024 + CERT C epic (#285) and remaining product issues.

## Phase 0 (this PR)

| Issue | Title | Status |
|-------|-------|--------|
| #269 | `-std=c11 -Wall -Wextra`; `-Werror`/`-pedantic` under `--profile safety` | ✅ |
| #270 | `FLOW_UBSAN` / `FLOW_ASAN` / `FLOW_SANITIZE` / `--sanitize=` | ✅ |
| #264 | Division-by-zero runtime + literal reject | ✅ |
| #265 | Shift UB runtime + literal reject | ✅ |

Usage:

```bash
./flow compile --show-flags
./flow run --sanitize=ub,asan examples/basics/hello_world.flow
FLOW_PROFILE=safety ./flow compile examples/basics/hello_world.flow
FLOW_HOST=python ./flow run examples/basics/hello_world.flow   # full language
```

## Still open

| Issue | Notes |
|-------|-------|
| #263 | Integer overflow checks |
| #266–#268 | Null deref / strcat leak / closure free |
| #271–#284 | Recursion/loops, profiles, WCET, compliance matrix, … |
| #285 | Epic umbrella |
| #252 | Euler: bigint + generic map/set (if-expr / C errors partial) |
| #172 | github-linguist (draft under `docs/project/linguist/`) |
| #147 | Multi-impl cost selection beyond sort/search |

## Note on prior doom/MLIR closeouts

PRs #257–#262 / #286 were marked merged and closed related issues, but their
commits are **not** ancestors of current `origin/main` (parallel history).
Re-land those fixes onto `main` if doom `-O2` / if-expressions are missing
locally after a fresh clone.
