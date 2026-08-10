# Safety profiles

Flow supports build profiles that tighten the C backend and clang flags for
MISRA/CERT-oriented work (ROADMAP W6, issues #273 / #285).

## Profiles

| Profile | How to enable | Behavior |
|---------|---------------|----------|
| **default** | (none) | Full language. Application TUs get runtime div0/shift/bounds guards. Overflow checks off. |
| **safety** | `FLOW_PROFILE=safety` or `--profile=safety` | `-Werror` (with known-noise waivers); signed overflow guards (`FLOW_OVERFLOW_CHECK`); **rejects recursive functions** (MISRA 17.2) via the safety manifest. |
| **flight** | `FLOW_PROFILE=flight` or `--profile=flight` | Same as **safety** today; future: stricter no-heap / no-float subset. |
| **embedded** | *(planned)* | Prefer static allocation; no GC assumptions. |

Also: `flow.toml` may set `profile = "safety"` once project config is wired; until then use the env/CLI flags.

## Temp arena (strcat / closures)

String `+` and escaping closure envs allocate through `flow_temp_alloc` and are
released by `flow_temp_free_all` at process exit (`atexit`) — closes the
strcat/closure leaks for short-lived programs (#267 / #268). Long-running
servers should prefer arenas or avoid heap concat.

## Loop bounds (#272)

Under `safety` / `flight`, every `while` must carry `@max_iterations(N)`:

```flow
@max_iterations(1000)
while cond {
    # ...
}
```

Counted `for i in 0 to N` loops are already bounded and need no attribute.
The C backend emits a runtime counter that aborts if the bound is exceeded.

## Inspect flags / manifest

```bash
./flow show-flags
./flow show-flags --profile=safety --sanitize=ub,asan
FLOW_HOST=python ./flow transpile prog.flow --c --emit-manifest --profile=safety
```

## Still open (epic #285)

- Null deref / unified fault handler (#266 / #279 — see PR #288)
- Loop bounds (#272), full no-heap (#274), compliance matrix (#278), WCET (#282), `@safe`/`@unsafe` (#284)
