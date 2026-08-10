# MISRA C:2024 compliance matrix

Living matrix for Flow → C. Evidence columns point at the enforcing
mechanism. Updated with Phase 0–2 work (#285 epic).

| Rule | Summary | Flow status | Generated C | Evidence |
|------|---------|-------------|-------------|----------|
| 8.1 | Prototypes required | PARTIAL | PARTIAL | Extern decls emit prototypes; `#283` `-Werror=implicit-function-declaration` under safety |
| 8.7 | External linkage unused | OPEN | OPEN | — |
| 11.8 | Null deref | PARTIAL | PARTIAL | PR #288 `FLOW_NONNULL` (pending merge) |
| 12.1 | Signed overflow | PROVEN | PROVEN | `FLOW_CHECKED_*` under `--profile safety` (#263 / #289) |
| 12.2 | Shift UB | PROVEN | PROVEN | Phase 0 shift guards (#265) |
| 12.5 | Div0 | PROVEN | PROVEN | Phase 0 div0 guards (#264) |
| 17.2 | No recursion | PARTIAL | PARTIAL | Safety manifest + reject (#271, PR #393) |
| 17.3 | No implicit decls | PARTIAL | PARTIAL | `#283` safety CFLAGS + stdlib skip-set audit |
| 17.4 | Bounded loops | PARTIAL | PARTIAL | `@max_iterations` (#272, PR #393); counted `for` OK |
| 21.3 | No dynamic heap | PARTIAL | PARTIAL | Source `@rt_safe` / `@safe`; temp arena (#267/#268 in #393); full flight ban OPEN (#274) |
| 21.6 | No stdio | DEVIATION | DEVIATION | Default fault/`println` use stdio; overridable via `FLOW_DIAG` (#281) |
| 22.1 | Fault handling | PARTIAL | PARTIAL | Handlers abort; unified `flow_fault_handler` in #288 |

## Deviations

1. **Rule 21.6 (stdio)** — diagnostic and `println` paths use `printf`/`fprintf`
   unless `FLOW_DIAG` is redefined. Justification: host tooling visibility;
   flight builds should supply a no-stdio `FLOW_DIAG`.
2. **Rule 21.3 (heap)** — default/`safety` profiles may still emit `malloc` for
   strcat/closures until the temp-arena PR merges and flight forbids heap.

## Related

- [CERT C matrix](cert-c-compliance.md)
- [Safety profiles](../language/safety-profiles.md)
- Epic #285
