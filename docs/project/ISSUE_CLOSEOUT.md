# Open-issue closeout (2026-08-09)

Auto-closed by the PR that lands this file (GitHub `Fixes` keywords). Remaining
open work is listed at the bottom — this agent cannot write the Issues API.

## Closed as done

| Issue | Why |
|-------|-----|
| [#253](https://github.com/flooooooooooow/flow/issues/253) | `&module_global` addressof (#250); MLIR `-O2` verified |
| [#254](https://github.com/flooooooooooow/flow/issues/254) | `_emit_static_llvm_array_global` on main |
| [#255](https://github.com/flooooooooooow/flow/issues/255) | ILP32 ptr/string layout + `sizeof_ptr` under `--wasm32`; u8/u32 ops from #250 |
| [#256](https://github.com/flooooooooooow/flow/issues/256) | Tracking; all listed blockers done |
| [#144](https://github.com/flooooooooooow/flow/issues/144) | IEEE totalOrder for declarative sort (docs + tests) |
| [#145](https://github.com/flooooooooooow/flow/issues/145) | `ordering_hints.py` provenance for adaptive sort |
| [#146](https://github.com/flooooooooooow/flow/issues/146) | `flow explain` / explainable compilation |
| [#148](https://github.com/flooooooooooow/flow/issues/148) | `@lifetime` domains + checks |
| [#151](https://github.com/flooooooooooow/flow/issues/151) | Self-hosting Phase B done |
| [#153](https://github.com/flooooooooooow/flow/issues/153) | Self-hosting Phase D done |

## Still open (intentionally)

| Issue | Status | Next step |
|-------|--------|-----------|
| [#147](https://github.com/flooooooooooow/flow/issues/147) | Sort/search cost selection landed; not generalized | Register FFT/DSP/ML impls in `plan_selector` |
| [#172](https://github.com/flooooooooooow/flow/issues/172) | Draft under `docs/project/linguist/` | Open upstream github-linguist PR (agent cannot fork) |
| [#252](https://github.com/flooooooooooow/flow/issues/252) | Partial: if-expr + C error visibility; f64 already exists | Still need `bigint` + generic `map`/`set` |

## Closed in this wave

Also closed: [#154](https://github.com/flooooooooooow/flow/issues/154) — `flowc-v0.10.0` release published + Homebrew formula.

## Sibling repo

Apply `docs/project/patches/doom-flow-mlir-o2.patch` on doom-flow (agent push is 403).
Sun Aug  9 08:53:13 PM UTC 2026

Merged closeout commit: 9e27d25
