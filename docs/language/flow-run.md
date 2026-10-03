# flow run: one-process runner and JSON output (#400)

## Default runner

```
./flow run prog.flow
./flow run prog.flow --backend=mlir
```

The default runner is the driver itself. It compiles with flowc, prints its
progress and runs the program.

## One-process runner

```
./flow run prog.flow --json
./flow run prog.flow --keep build/
FLOW_RUN_DIRECT=1 ./flow run prog.flow
```

`--json`, `--keep`, `--extra-cflags` and `--predict`, or `FLOW_RUN_DIRECT=1`,
select the one-process runner (`tools/run`, a Flow program). It compiles
with flowc and clang, runs the program and passes its output through
without the driver's progress lines. `FLOW_RUN_PYTHON=1` is the old name for
`FLOW_RUN_DIRECT=1` and still works.

## Structured JSON output

```
./flow run prog.flow --json
```

Emits a JSON envelope with stdout, stderr, exit code, and per-stage timing:

```json
{
  "stdout": "hello\n",
  "stderr": "",
  "exit_code": 0,
  "timing": {
    "transpile_s": 0.25,
    "compile_s": 0.07,
    "run_s": 0.23,
    "total_s": 0.55
  }
}
```

When a step fails the envelope also carries `error`. This is suitable for
docs builds and CI fixtures that need to capture deterministic program
output.

## Keeping intermediate files

```
./flow run prog.flow --keep build/
```

Writes the generated C and binary to the specified directory instead of
a temp directory.

## Backends

`--backend=c` is the default. `--backend=mlir` runs the MLIR JIT. With
`--backend=auto` the runner compiles with C. `--predict` prints the backend
the crossover cost model would pick (`c` or `mlir`) without running
anything.

## CI fixture pattern

```bash
# Compile + run + capture result
./flow run examples/estimator.flow --json > result.json

# Verify the result
grep -q '"exit_code": 0' result.json
```
