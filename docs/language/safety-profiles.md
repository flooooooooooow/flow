# Safety profiles

Flow supports build profiles that tighten the C backend and clang flags for
MISRA/CERT-oriented work (ROADMAP W6, issues #273 / #285).

## Profiles

| Profile | How to enable | Behavior |
|---------|---------------|----------|
| **default** | (none) | Full language. Application TUs still get runtime div0/shift/overflow/null/bounds guards in generated C. |
| **safety** | `FLOW_PROFILE=safety` or `--profile=safety` | Adds `-Werror` (with known-noise waivers). Same checked arithmetic as default. |
| **flight** | `FLOW_PROFILE=flight` or `--profile=flight` | Alias of **safety** for now; future: no heap in RT paths, no unbounded recursion/loops, optional no-float. |
| **embedded** | *(planned)* | Prefer static allocation; no GC assumptions. |

## Inspect flags

```bash
./flow show-flags
./flow show-flags --profile=safety --sanitize=ub,asan
```

## Override the fault handler

Generated application C defines `flow_fault_handler(const char* msg)` (abort by
default). Replace it at compile time:

```bash
FLOW_CFLAGS='-DFLOW_FAULT_HANDLER=my_handler' ./flow run --profile=safety app.flow
```

Div0, shift UB, signed overflow, null deref, and bounds faults all route through
this single handler (#279).

## Sanitizers

```bash
./flow run --sanitize=ub,asan examples/basics/hello_world.flow
# or: FLOW_UBSAN=1 FLOW_ASAN=1 FLOW_HOST=python ./flow run …
```

## Still open (epic #285)

- Bounded recursion/loops (#271/#272)
- No-heap / strcat / closure free (#267/#268/#274)
- Compliance matrix (#278), WCET (#282), `@safe`/`@unsafe` (#284)
