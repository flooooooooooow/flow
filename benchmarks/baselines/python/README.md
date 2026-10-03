# Python benchmark subjects

The programs here are benchmark subjects. Each one exists to measure CPython
or NumPy as a comparison baseline for a Flow program that does the same work.
They are run by the Flow and bash harnesses listed below and are never
imported by anything.

This directory must not contain tooling. A runner, a report generator, a
parser or a test belongs in Flow (scripts/tools) or bash. Every harness runs
these files only when `python3` is on PATH and works, and skips them with a
message otherwise.

| Directory | Twin of | Run by |
|---|---|---|
| `cross_harness/<suite>/<name>/` | `benchmarks/cross_harness/<suite>/<name>/*.flow` | `./flow tool bench_harness` (scripts/tools/bench_harness) |
| `publish/` | `benchmarks/publish/{flow,c,rust}/` | `./flow tool bench_publish` (scripts/tools/bench_publish) |
| `suite/` | `benchmarks/suite/{flow,c}/` | `./flow tool benchmarks/suite/run_benchmarks.flow` |
| `standardized/record_numpy.py` | `benchmarks/standardized/record/record.flow` | `./flow tool benchmarks/standardized/bench.flow` |

The `suite/*_numpy.py` and `suite/01_fibonacci_memo.py` variants show the
idiomatic NumPy or memoised form. `./flow tool benchmarks/suite/run_benchmarks.flow` runs
the NumPy variant next to the plain one when NumPy is installed.
