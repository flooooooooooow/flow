# Package examples

Minimal path-dependency demo for Flow's package layout (`flow.toml` + `flow_packages/`).

## Layout

| Path | Role |
|------|------|
| `hello_lib/` | Tiny library (`greet`, `add`, `hello_answer`) |
| `use_hello_lib/` | Consumer with `hello_lib = { path = "../hello_lib" }` |

A matching copy lives at `registry/crates/hello_lib/` for registry-shaped layouts.

## Run

```bash
cd examples/packages/use_hello_lib
PYTHONPATH=../../../src python3 -m flow.package install
cd ../../..
./flow run examples/packages/use_hello_lib/src/main.flow
```

`./flow install` at the repo root installs Python tooling, not Flow packages — use `python3 -m flow.package install` inside the project directory.
