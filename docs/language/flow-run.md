# flow run: shell-independent execution (#400)

## Bash runner (default)

```
./flow run prog.flow
./flow run prog.flow --backend=mlir
```

The default runner uses bash. It works on Linux and macOS but requires
bash 4.4+ for some array patterns.

## Python runner (shell-independent)

```
FLOW_RUN_PYTHON=1 ./flow run prog.flow
python3 -m flow.run prog.flow
```

The Python runner transpiles, compiles, and runs the program without bash.
It works under any shell and on systems with older bash (macOS 3.2).

## Structured JSON output

```
python3 -m flow.run prog.flow --json
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

This is suitable for docs builds and CI fixtures that need to capture
deterministic program output.

## Keeping intermediate files

```
python3 -m flow.run prog.flow --keep build/
```

Writes the generated C and binary to the specified directory instead of
a temp directory.

## CI fixture pattern

```bash
# Transpile + run + capture result
python3 -m flow.run examples/estimator.flow --json > result.json

# Verify the result
python3 -c "import json; r=json.load(open('result.json')); assert r['exit_code']==0"
```
