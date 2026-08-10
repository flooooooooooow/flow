# CERT C compliance matrix

| Recommendation | Summary | Status | Evidence |
|----------------|---------|--------|----------|
| INT32-C | No signed overflow | PROVEN | `FLOW_CHECKED_ADD/SUB/MUL` under safety (#263) |
| INT33-C | Div/mod by zero | PROVEN | Phase 0 (#264) |
| INT34-C | Shift amount | PROVEN | Phase 0 (#265) |
| ERR33-C | Detect/handle errors | PARTIAL | Fault handlers; null checks in #288 |
| MEM05-C | Avoid large recursive stacks | PARTIAL | Recursion reject under safety (#271) |
| DCL31-C | Declare before use | PARTIAL | Prototypes + `#283` `-Werror=implicit-function-declaration` |
| API02-C | Functions validate args | OPEN | — |
| FIO30-C | Exclude user input from format | DEVIATION | Generated format strings are compiler-fixed literals |

## Related

- [MISRA C:2024 matrix](misra-c-2024-compliance.md)
- Epic #285
