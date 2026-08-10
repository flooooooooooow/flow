# MISRA C:2024 compliance matrix

Living matrix for Flow → C. Evidence columns point at the enforcing
mechanism. Updated with Phase 0–2 work (#285 epic).

| Rule | Summary | Flow status | Generated C | Evidence |
|------|---------|-------------|-------------|----------|
| 8.1 | Prototypes required | PARTIAL | PARTIAL | Extern decls emit prototypes; `#283` `-Werror=implicit-function-declaration` under safety |
| 8.7 | External linkage unused | OPEN | OPEN | — |
| 11.8 | Null deref | PARTIAL | PARTIAL | PR #288 `FLOW_NONNULL` (pending merge) |
| 12.1 | Signed overflow | DEVIATION | DEVIATION | Runtime overflow codegen removed; UBSan via `FLOW_UBSAN=1` for testing (#275) |
| 12.2 | Shift UB | PROVEN | PROVEN | Literal shift UB rejected at type-check time (#265) |
| 12.5 | Div0 | PROVEN | PROVEN | Literal div-by-zero rejected at type-check time (#264) |
| 17.2 | No recursion | PROVEN | PROVEN | `--profile safety` rejects recursion at type-check time (#271) |
| 17.3 | No implicit decls | PROVEN | PROVEN | `#283` safety CFLAGS: `-Werror=implicit-function-declaration` |
| 17.4 | Bounded loops | PROVEN | PROVEN | `--profile safety` rejects `while` without `@max_iterations` (#272); counted `for` OK |
| 21.3 | No dynamic heap | PARTIAL | PARTIAL | Source `@rt_safe` / `@safe`; temp arena (#267/#268); full flight ban OPEN (#274) |
| 21.6 | No stdio | PARTIAL | PARTIAL | `println` routes through `FLOW_LOG` macro; diagnostics via `FLOW_DIAG`. Both overridable via `-D` for no-stdio builds (#281) |
| 22.1 | Fault handling | PROVEN | PROVEN | `flow_fault_handler` configurable via `FLOW_FAULT_HANDLER` macro (#279) |

## Deviations

1. **Rule 21.6 (stdio)** — `println` and diagnostics default to `printf`/`fprintf`
   via the `FLOW_LOG` and `FLOW_DIAG` macros. Safety-critical builds override
   these with `-DFLOW_LOG(fmt, ...)=...` and `-DFLOW_DIAG(msg)=...` to route
   through a certified I/O abstraction. Justification: host tooling visibility.
2. **Rule 21.3 (heap)** — default/`safety` profiles may still emit `malloc` for
   strcat/closures until the temp-arena PR merges and flight forbids heap.

## Related

- [CERT C matrix](cert-c-compliance.md)
- [Safety profiles](../language/safety-profiles.md)
- Epic #285
