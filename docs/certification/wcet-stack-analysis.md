# WCET and stack depth analysis (#282)

Flow provides static worst-case execution time (WCET) and stack depth
analysis for DO-178C, ISO 26262, and ECSS-Q-ST-80C compliance evidence.

## Usage

```
flow analyze prog.flow --wcet --stack-depth
flow analyze prog.flow --stack-depth --budget 4096
flow analyze prog.flow --wcet --budget 10000
```

Or directly:

```
python3 -m flow.wcet_analysis prog.flow --wcet --stack-depth
```

## Stack depth analysis

Computes the maximum stack depth for each function by walking the call
graph and summing local variable sizes. The result is a conservative
upper bound in bytes.

```
Stack depth analysis: prog.flow
============================================================
Function                                  Max depth Chain
------------------------------------------------------------
main                                          68 bytes  main → println
compute                                        8 bytes  compute → helper
helper                                         4 bytes  helper
```

Use `--budget N` to fail if any function exceeds N bytes:

```
flow analyze prog.flow --stack-depth --budget 4096
```

### Requirements

- No recursion (enforced by `--profile safety`, MISRA 17.2).
- Extern functions get a fixed 64-byte estimate.

### Type size model

| Flow type | Bytes |
|-----------|-------|
| i8, u8, bool | 1 |
| i16, u16 | 2 |
| i32, u32, f32 | 4 |
| i64, u64, f64, c64, ptr | 8 |
| i128, u128, c128 | 16 |
| struct (default) | 16 |

## WCET analysis

Estimates worst-case execution time as an abstract instruction count.
The cost model assigns a fixed cost per statement type and multiplies
loop bodies by their bound.

| Construct | Cost |
|-----------|------|
| Variable declaration | 1 |
| Assignment | 2 |
| If statement | 3 |
| For loop | 5 |
| While loop (per iteration) | 5 |
| Return | 2 |
| Function call | 10 |

While loops use `@max_iterations(N)` as the bound. Without it, a
conservative default of 1000 is used.

```
WCET analysis: prog.flow
============================================================
Function                                   Max cost Chain
------------------------------------------------------------
main                                          123 inst  main → println
compute                                        23 inst  compute → helper
helper                                          3 inst  helper
```

## Certification notes

These are static estimates, not measured values. For certification:

1. Run under `--profile safety` to ensure no recursion and bounded loops.
2. Use `--budget` to enforce timing and stack limits in CI.
3. Combine with measured timing on the target hardware for final evidence.
4. The cost model is conservative. Real instruction counts will be lower
   after compiler optimizations.

## Related

- MISRA 17.2 (recursion ban): enforced by `--profile safety`
- MISRA 17.4 (loop bounds): `@max_iterations(N)` on while loops
- Issue #282: WCET/stack depth analysis
- Issue #285: MISRA/CERT certification epic
