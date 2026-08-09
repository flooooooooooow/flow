# Open-issue closeout (2026-08-09)

## Closed this session

| Issue | Via |
|-------|-----|
| #253, #254, #255, #256 | #257 / #259 / #261 (doom MLIR) |
| #144, #145, #146, #148 | #261 (ordering / explain / lifetimes) |
| #151, #153 | #261 (self-hosting B/D) |
| #154 | #262 + `flowc-v0.10.0` release |

## Still open — language / product

| Issue | Status |
|-------|--------|
| [#147](https://github.com/flooooooooooow/flow/issues/147) | Sort/search cost selection exists; generalize beyond sort |
| [#172](https://github.com/flooooooooooow/flow/issues/172) | Draft in `docs/project/linguist/`; needs upstream linguist PR |
| [#252](https://github.com/flooooooooooow/flow/issues/252) | **Partial:** if-expr + C error visibility landed (#262). Still need **bigint** + generic **map/set**. (`f64` already exists.) |

## Still open — MISRA/CERT epic (filed 2026-08-09)

Epic [#285](https://github.com/flooooooooooow/flow/issues/285) tracks #263–#284 (overflow, div0, shifts, null checks, heap discipline, `--profile safety`, WCET, compliance matrix, …). This is a multi-PR certification path, not a single closeout.

Suggested Phase 0 (next PR):
1. `#269` default `-std=c11 -Wall -Wextra` (not `-Werror` until generated C is clean)
2. `#270` `FLOW_SANITIZE=undefined,address` / `flow run --sanitize=…`
3. `#264` div-by-zero traps in C generator
4. `#265` shift-width guards

Sibling: apply `docs/project/patches/doom-flow-mlir-o2.patch` on doom-flow (push was 403).
