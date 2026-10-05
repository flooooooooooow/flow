# Flow Performance Baselines

Date: 2026-09-12
OS: Linux
Arch: x86_64
Cores: 4
Flow Version: 1.0.2
Git SHA: 06bb3e1caacb107f3fa66a16334c3a2b824b65dc
Host: Python 3.12.13
Flags: `clang -O3 -march=native -lm`

| Benchmark | Median (s) | Min (s) | Max (s) | Result |
|---|---|---|---|---|
| numeric | 0.003666 | 0.003491 | 0.003965 | 833.250000 |
| string_io | 0.270966 | 0.265416 | 0.681268 | 60005 |
| startup | 0.002247 | 0.002110 | 0.002584 | 0 |
