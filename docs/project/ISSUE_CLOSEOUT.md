# MISRA / CERT + product closeout

## Phase 0 (merged #287)

| Issue | Status |
|-------|--------|
| #269 flags | ✅ |
| #270 sanitizers | ✅ |
| #264 div0 | ✅ |
| #265 shift | ✅ |

## Phase 1 (this PR)

| Issue | Status |
|-------|--------|
| #263 signed overflow (`__builtin_*_overflow`) | ✅ |
| #266 null deref (`FLOW_NONNULL`) | ✅ |
| #279 unified `flow_fault_handler` | ✅ |
| #273 safety profiles doc + CLI wiring | ✅ partial (`docs/language/safety-profiles.md`; flight≡safety) |
| #252 if-expressions | ✅ (bigint / generic map still open) |

## Still open

| Issue | Notes |
|-------|-------|
| #252 | bigint + generic `map`/`set` |
| #267–#268 | strcat / closure leaks |
| #271–#272 | recursion / loop bounds |
| #274–#285 | heap policy, matrix, WCET, `@safe`, epic |
| #172 | github-linguist |
| #147 | multi-impl beyond sort |
