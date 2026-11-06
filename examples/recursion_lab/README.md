# Recursive MLIR native parity lab

Six Flow 2.0 recursive stress programs:

| Program | Stress dimension |
|---|---|
| `recursive_biome.flow` | 9,207 recursive branches, floating-point geometry, Flow `evolves as` and `always` |
| `newton_multiverse.flow` | 561,200 pixels, nonlinear recursion, C vararg calls and binary stdout |
| `underworld_labyrinth.flow` | 741-room recursive DFS generation and separate recursive path discovery |
| `recursive_oracle.flow` | Negamax, alpha-beta pruning, iterative deepening and transposition caching |
| `symbolic_hydra.flow` | Recursive symbolic DAG differentiation, memoization and independent autodiff |
| `ackermann_furnace.flow` | A(3,12), 715,664,091 recursive calls and 32,767 active frames |

The `recursive-mlir-parity` GitHub Actions workflow builds **each exact source twice**: through Flow's C backend and through `./flow compile --backend=mlir` using LLVM/MLIR 22. It compares exit status and byte-identical stdout, including SVG and binary PPM files. It also runs each executable three times, collecting wall time, user time and peak resident memory from GNU time, along with SHA-256 output digests and build logs.

Use the GitHub Actions artifact `recursive-mlir-native-parity` for `summary.tsv` and the report. The full Ackermann case needs at least 64 MiB of stack reservation. Peak RSS is not a direct measurement of stack use; the Ackermann program independently tracks maximum recursive call depth.

The baseline collected locally from Clang -O2 C binaries (Linux x86-64, three runs): biome 0.01 s; Newton 0.07 s; Underworld <0.01 s; Oracle <0.01 s; Hydra 0.16 s; Ackermann 3.12 s. These values are **not** suitable for comparing ratios to CI, because GitHub-hosted runners have different CPUs.

This suite intentionally fails CI if a program compiles and runs differently on MLIR. This is a correctness/performance **regression benchmark**, not an assertion that the MLIR backend already has full parity.

Run a single Flow source manually:

```sh
./flow compile examples/recursion_lab/ackermann_furnace.flow
./flow compile --backend=mlir examples/recursion_lab/ackermann_furnace.flow
```
