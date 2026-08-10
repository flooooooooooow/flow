# MISRA / CERT + product closeout

Tracking for the MISRA C:2024 + CERT C epic (#285) and remaining product issues.

## Phase 0 (merged #287)

| Issue | Status |
|-------|--------|
| #269 flags | ✅ |
| #270 sanitizers | ✅ |
| #264 div0 | ✅ |
| #265 shift | ✅ |

## Overflow + manifest (merged)

| Issue | Status |
|-------|--------|
| #263 signed overflow | ✅ (#289, opt-in under `--profile safety`) |
| Safety manifest `--emit-manifest` | ✅ (#290) |

## This PR (euler / leaks / profile harden)

| Issue | Status |
|-------|--------|
| #267 `flow_strcat` leak | ✅ temp arena + `atexit` |
| #268 closure env leak | ✅ same arena |
| #271 unbounded recursion | ✅ detected via safety manifest; rejected under safety/flight |
| #272 unbounded while | ✅ `@max_iterations(N)` required under safety/flight + runtime guard |
| #273 safety/flight profile | ✅ partial (recursion + loop bounds; flight≡safety) |
| #252 bigint + `HashMap_i64_i64` | ✅ partial (stdlib + smokes; if-expr in #288) |

## Still open

| Issue | Notes |
|-------|-------|
| #266 / #279 | Null deref + unified fault handler — PR #288 |
| #252 | if-expressions (#288); generic `map`/`set` polish |
| #274–#285 | Heap policy, matrix, WCET, `@safe`, epic |
| #172 | github-linguist |
| #147 | multi-impl beyond sort |

## Note on prior doom/MLIR closeouts

PRs #257–#262 / #286 were marked merged and closed related issues, but some
history may still need re-land onto `main` if doom `-O2` / if-expressions are
missing after a fresh clone — see open PR #288 for if-expressions.
