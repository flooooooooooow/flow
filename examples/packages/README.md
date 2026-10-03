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
../../../flow sync
cd ../../..
./flow run examples/packages/use_hello_lib/src/main.flow
```

`./flow install` at the repo root installs compiler tools. Inside a project with a `flow.toml`, `flow sync` (or `flow install`) installs its packages. `flow run` also installs missing packages before it compiles.
