# Debugging Flow programs

Flow compiles to C. The debugger story is LLDB/GDB against that C with
`#line` maps back into `.flow` sources.

## Quick start

```bash
./flow debug examples/basics/hello_world.flow
./flow debug prog.flow --break 42      # break at Flow source line 42
./flow debug prog.flow --break main    # default
./flow debug prog.flow --no-launch     # build only; print paths
```

This:

1. Transpiles with `--debug-info` (statement-level `#line` directives in the C backend)
2. Builds with `clang -g3 -O0`
3. Launches LLDB (or GDB) stopped at `main` (unless `--no-launch`)

Useful LLDB commands:

```text
n / s          next / step
bt             backtrace
frame variable
source list
b <flow-function-name>
```

## Manual path

```bash
python3 -m flow.transpiler prog.flow --c --debug-info -o build/prog.debug.c
clang -g3 -O0 build/prog.debug.c -o build/prog.debug -lm
lldb build/prog.debug
```

`#line` paths are absolute so the debugger can open the original `.flow` file.
The same `--debug-info` flag also enables debug metadata on the MLIR path.

## Limits

- Mapping is primarily statement-level; when initializers / return values carry
  their own `location`, an extra `#line` is emitted for finer stepping
- Optimized builds (`-O2`) will scramble stepping — always use `./flow debug`
- Effects/handlers lower to C helper functions; step into those to see dispatch
- Column-accurate maps remain open; statement + initializer/return `#line` shipped

## DAP / VS Code

```bash
./flow dap examples/basics/hello_world.flow   # TTY → flow debug
# IDE: FLOW Language extension registers debugger type "flow"
#   launch.json: { "type": "flow", "request": "launch", "flowFile": "${file}" }
```

`python3 -m flow.dap_server` speaks DAP on stdio, builds with
`./flow debug --no-launch`, then proxies to `lldb-dap` (Xcode CLT). Breakpoints
on `.flow` lines work via absolute `#line` paths.

## Tip

```bash
./flow debug examples/basics/hello_world.flow --break main
# then in lldb:
#   n          # step to next Flow statement (#line)
#   source list
```

## Related

- [Wasm / playground](wasm.md) — browser run path
- Playground native-local: `python3 scripts/playground_compile_server.py`
