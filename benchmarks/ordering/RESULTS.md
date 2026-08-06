# Adaptive ordering: measured results

Source: `benchmarks/ordering/adaptive_sort_bench.flow`
Runner: `benchmarks/ordering/run.sh 5`

Machine: Apple M4 Max, macOS 26.2, Apple clang 17.0.0, `-O2`.
Measured 2026-08-06. Five runs, median reported, copy baseline subtracted.

Each row is 100 sorts of 32768 elements. `general` pins the general-purpose
stable bottom-up merge with the `general` policy. `selected` is the plan the
compiler picks, named in the third column. The copy that refills the working
array before each sort is inside the timed region; a copy-only loop measured
0.00012 s per 100 copies and is subtracted from every number below.

| input | general (s) | selected (s) | plan selected | speedup |
|-------|------------:|-------------:|---------------|--------:|
| already sorted        | 0.04138 | 0.00105 | natural_merge | 39.4x |
| reverse sorted        | 0.04109 | 0.00146 | natural_merge | 28.1x |
| sawtooth, 512 runs    | 0.07933 | 0.06221 | natural_merge |  1.3x |
| few unique (8 values) | 0.07221 | 0.05945 | natural_merge |  1.2x |
| random                | 0.10443 | 0.09038 | natural_merge |  1.2x |
| random u8             | 0.08380 | 0.00179 | counting      | 46.8x |

## Reading it

The two large wins come from structure the general plan cannot see. An
already-sorted or fully reversed input is one natural run, so the run
detector finds it in a single scan and merges nothing. The u8 row is the
positivity hint: the element type bounds every key to [0, 255] with no
analysis, which is enough for a stable counting sort.

The middle rows are the honest ones. Partially ordered input gives the run
detector something to work with but not much, and it lands 20 to 30 percent
ahead. Random input has nothing to detect, and the run detector still came
out 12 percent ahead because building 32-element runs by insertion stays in
cache while a merge pass streams the whole array. That result is why
`RUN_EXTENSION_WEIGHT` in `src/flow/ordering_plans.py` is calibrated the way
it is, and why the run-detecting merge is the default above the insertion
crossover rather than something the `adaptive` policy has to ask for.

Two caveats. These are single-machine numbers on one element type at one
size; re-run `run.sh` before trusting the constants on other hardware. And
the compile-time provenance path is not measured here at all, because a hint
strong enough to prove the input already sorted removes the sort entirely and
there is nothing left to time.

## Reproducing

```
benchmarks/ordering/run.sh 5
```

It prints the selected plan for every site before the timings, from the same
build, so the plan column above can never drift from the numbers next to it.
