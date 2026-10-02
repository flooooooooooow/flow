# Flow Performance Baselines

Date: 2026-10-02
OS: Darwin
Arch: arm64
Cores: 14
Flow Version: 2.0.0
Git SHA: 5a6704dffb03f159edb43991a0add1e243f2e0c8
Host: Python 3.9.6
Flags: `clang -O3 -march=native -lm`

| Benchmark | Median (s) | Min (s) | Max (s) | Result |
|---|---|---|---|---|
| numeric | 0.005674 | 0.002715 | 0.011101 | 833.250000 |
| string_io | 0.026587 | 0.026016 | 0.031720 | 60005 |
| startup | 0.001904 | 0.001529 | 0.008490 | 0 |
