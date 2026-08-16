# Debugging Flow with LLDB

Flow does not ship a custom debugger. Use the host debugger on the
generated C binary. The CLI helper is:

```bash
./flow debug path/to/program.flow
```

## What `flow debug` does

From the `flow` driver (`debug_program`):

1. Compiles Flow → C with `--debug-info --lenient` into
   `build/<name>.debug.c` (coarse `#line` mappings back to `.flow`).
2. Links with `clang -g -O0 -fno-omit-frame-pointer` into
   `build/<name>.debug`.
3. Starts **LLDB** if available, else GDB; otherwise prints the binary path.

Tip printed by the CLI: `(lldb) b main ; run ; bt`.

## Minimal LLDB cookbook

```bash
./flow debug examples/basics/hello_world.flow
```

Inside LLDB:

| Goal | Command |
|------|---------|
| Break at `main` | `b main` |
| Run | `run` |
| Next source line | `n` / `next` |
| Step into | `s` / `step` |
| Continue | `c` / `continue` |
| Backtrace | `bt` |
| Print variable | `p name` or `frame variable name` |
| List source | `source list` / `l` |
| Quit | `quit` |

One-liner without the interactive `flow debug` wrapper:

```bash
./flow debug examples/basics/hello_world.flow
# or, after a failed auto-launch:
lldb build/hello_world.debug
(lldb) b main
(lldb) run
(lldb) bt
```

## Source mapping notes

- `--debug-info` emits coarse `#line` directives so LLDB can show `.flow`
  locations when the mapping is present.
- Fidelity is **not** statement-perfect yet (see ROADMAP debugger item).
  When a stop looks wrong, open `build/<name>.debug.c` and break on the
  generated C function instead (`b function_name`).
- Optimize flags are off (`-O0`); do not use release builds for stepping.

## GDB

If LLDB is missing and GDB is on `PATH`, `flow debug` launches GDB:

```
(gdb) break main
(gdb) run
(gdb) bt
```

## Related

- Roadmap status: [ROADMAP.md](../../ROADMAP.md) § Debugger Integration
- Graphics / GPU runs use other CLI verbs (`gfx`, etc.); prefer `flow debug`
  for ordinary non-window programs.
