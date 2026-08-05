# dsp_bench — CPU · SIMD · GPU benchmark for the Schur all-pass bank

Measures throughput of the Schur/lattice all-pass kernel (the DSP behind the
`SchurPhaser` / `PhaseAlign` plugins) across three backends on Apple Silicon:

| Backend       | How it parallelises                                  |
|---------------|------------------------------------------------------|
| `CPU scalar`  | one chain at a time, fully serial (reference)        |
| `CPU NEON x4` | 4 independent chains per 128-bit lane (SoA)          |
| `GPU Metal`   | one GPU thread per chain                              |

## The honest part — what can and can't be parallelised

A single all-pass chain is a **recursive IIR**: `y[n] = k·x[n] + x[n-1] − k·y[n-1]`,
and each section feeds the next. That is serial on **two** axes — across samples
(feedback) and across sections (cascade). You **cannot** vectorise a single stereo
chain, and GPU dispatch latency makes it useless for a real-time 2-channel plugin.

The parallel axis that *is* real: **many independent chains at once** — a modal
reverb, a spectral/filter bank, or massive multi-voice synthesis. That is what this
tool benchmarks. Within a chain everything stays serial; speed comes from width.

Two further axes this tool does **not** yet cover (roadmap):
- **Associative-scan** reformulation to parallelise a single chain over *time*
  (the trick state-space models / Mamba use). Ties to the repo's dynamical-systems work.
- **Analyzer** paths (frequency response over N points, FFT) — fully data-parallel.

## Build & run (Apple Silicon)

```bash
./build.sh
./dsp_bench --chains 4096 --sections 8 --samples 48000 --reps 4
./dsp_bench --chains 16384 --json          # machine-readable
```

Flags: `--chains N --sections N(≤16) --samples N --reps N --json --no-gpu`.

Correctness is verified every run: NEON and Metal outputs are compared against the
scalar reference (`max-diff`, must stay ~1e-7 under `-ffast-math`).

## Representative results — Apple M4 Max

`sections=8, samples=48000`, throughput in **G section-updates/s**, speedup vs scalar:

| chains | scalar | NEON x4 | Metal GPU |
|-------:|-------:|--------:|----------:|
|    512 |   1.64 | 6.5 (4.0×) | 3.9 (2.4×) |
|   2048 |   1.65 | 6.5 (3.9×) | 15.5 (9.4×) |
|   8192 |   1.64 | 6.5 (4.0×) | 62.0 (37.7×) |
|  32768 |   1.64 | 6.5 (4.0×) | 66.2 (40.3×) |

Takeaways: NEON pins the **theoretical 4× ceiling** (4-wide f32). The GPU is
**dispatch-bound** for small banks (2.4× at 512) and only pays off past a few
thousand chains, plateauing near **40×** once occupancy saturates. Pick the backend
by workload width, not by hype.
