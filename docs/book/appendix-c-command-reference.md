# Appendix C. Command reference

Commands are shown from the repository root. An installed release may omit the
leading `./`.

## Compile and run

| Command | Purpose |
|---|---|
| `flow run FILE` | compile and run through C by default |
| `flow run FILE --backend=mlir` | compile and run through MLIR |
| `flow compile FILE` | build an executable without running it |
| `flow transpile FILE ARGS...` | invoke advanced transpiler options |
| `flow mlir FILE` | emit MLIR; accepts optimisation flags |
| `flow mlir-run FILE` | compile and run through MLIR |
| `flow jit FILE` | JIT through MLIR/LLVM |
| `flow python FILE` | generate a CPython wheel |
| `flow wasm FILE` | generate a runnable WebAssembly page/module |

Common run/compile options include `--backend=c|mlir`,
`--sanitize=ub,asan,tsan`, `--profile=safety`, and `--show-flags` where
applicable.

## Domain runners

| Command | Purpose |
|---|---|
| `flow audio FILE [--mlir]` | compile and run with audio runtime |
| `flow compile-audio FILE [--mlir]` | compile an audio program |
| `flow window FILE` | run with SDL2 window backend |
| `flow gfx FILE` | run with native Flow graphics backend |
| `flow record FILE OPTIONS` | headless frames or GIF |
| `flow shader FILE` | compile and run a fill shader |
| `flow gpu FILE` | generate Metal sources from `@gpu` functions |
| <code>flow ml run&#124;jit&#124;bench&#124;test [FILE]</code> | MLIR-first ML operations |

Recording options include `--frames`, `--skip`, `--out`, `--gif`, `--keys`,
`--fps`, `--stride`, and `--width`.

## Demonstrations

```bash
flow demo vulkan basic
flow demo vulkan advanced
flow demo vulkan-flow basic
flow demo vulkan-flow advanced
flow demo vulkan-flow 2048
flow demo vulkan-flow tetris
flow demo vulkan-flow snake
flow demo vulkan-flow pong
flow demo vulkan-flow breakout
flow demo vulkan-flow layout
flow demo vulkan-flow layout-dsl
flow demo ui-layout
flow demo ui-layout-window
```

Historical Vulkan and UI command aliases remain accepted.

## Inspection and debugging

| Command | Purpose |
|---|---|
| `flow fmt FILES...` | format source |
| `flow repl` | interactive core-language session |
| `flow debug FILE` | debug build and LLDB/GDB launch |
| `flow dap FILE` | Debug Adapter Protocol server |
| `flow explain FILE` | show declarative candidate plans and selection |
| `flow fir-g FILE` | dump FIR-G and analyses |
| `flow show-flags` | print C flags for profile/sanitizer settings |
| `flow analyze FILE.c` | scan C for MISRA or CERT patterns |
| `flow examples` | list example programs |
| `flow playground` | start the local compile API and open the playground |
| `flow version` | print compiler version |
| `flow help` | print command help |

`debug` accepts `--break N`, `--break main`, and `--no-launch`.
`analyze` accepts `--standard=misra-c-2024|cert-c` and
`--fail-on-violation`. `fir-g` accepts calibration and optimisation options.

## Tests

For normal Flow projects, `flow test` discovers and executes named tests under
`tests/` (or `[test].paths` in `flow.toml`):

```flow
test "answer" {
    expect 6 * 7 == 42
}
```

| Command | Purpose |
|---|---|
| `flow test` | discover, compile and run the current project's tests |
| `flow test PATHS...` | test selected files/directories |
| `flow test --list` | list discovered cases without compiling |
| `flow test --filter TEXT` | run matching file/test names |
| `flow test --backend=c` | qualify the portable C backend |
| `flow test --backend=mlir` | qualify MLIR/LLVM |
| `flow test --backend=all` | run every case through C and MLIR |
| `flow test --sanitize=ub,asan` | compile tests with sanitizers |
| `flow test --profile=safety` | compile tests with the safety profile |
| `flow test --compiler` | Flow-repository compiler tier sweep |
| `flow test --project ...` | force project semantics from the Flow repo root |
| `flow test-runtime` | legacy compiler-repository runtime corpus |
| `flow test-lang` | legacy strict language regression programs |
| `flow test-mlir` | compiler-repository MLIR verification |
| `flow test-python` | compiler Python unit tests |
| `flow test-interop` | compiler interoperation runtime tests |
| `flow test-gpu` | compiler GPU feature/code-generation tests |
| `flow test-matmul` | matrix optimisation and assembly demonstration |
| `flow test-all` | compiler Flow and Python suites |

Project testing also supports `--timeout`, `--fail-fast`, `--host`, `--keep`
and `-v/--verbose`. Existing standalone test programs whose `main()` returns
zero remain valid. Exact output/expected-failure tests can use sibling
`.expected`, `.expected-stderr`, and `.exitcode` files.

See [`../language/testing.md`](../language/testing.md) for the complete project
testing contract.

## Projects and packages

| Command | Purpose |
|---|---|
| `flow init [NAME]` | create a project and manifest |
| `flow add SPEC` | add registry, Git, or path dependency |
| `flow pkg install` | install dependencies into `flow_packages` |
| `flow search [QUERY]` | search package index |
| `flow info PACKAGE` | show versions and source |
| `flow publish` | update selected package index |
| `flow build` | build manifest entry |
| `flow build-native` | build with manifest native sources |
| `flow run-native` | build and execute with native sources |
| `flow clean` | remove project build artifacts |
| `flow install` | install project deps, or tools outside a project |
| `flow setup` | install LLVM/compiler tooling |

## WebAssembly options

```bash
flow wasm FILE \
  --backend=c|mlir \
  --preload LOCAL@/MOUNT \
  --link PATH \
  --threads \
  --fs memfs|idbfs \
  --out DIRECTORY
```

## Environment variables

| Variable | Meaning |
|---|---|
| <code>FLOW_HOST=flowc&#124;python&#124;auto</code> | choose compiler host |
| <code>FLOW_CPU_BACKEND=c&#124;mlir</code> | choose CPU backend |
| `FLOW_STRICT_EFFECTS=1` | reject uncovered effect operations |
| `FLOW_PROFILE=safety` | select safety C flags |
| `FLOW_SANITIZE=ub,asan,tsan` | combined sanitizer selection |
| `FLOW_UBSAN=1` | undefined-behaviour sanitizer |
| `FLOW_ASAN=1` | address sanitizer |
| `FLOW_TSAN=1` | thread sanitizer |
| `FLOW_MAXPROCS=N` | fiber scheduler worker count |
| `FLOW_REGISTRY_PATH=FILE` | local registry index override |
| `FLOW_REGISTRY_URL=URL` | remote JSON registry override |
| `FLOW_HOME=DIR` | Flow package/cache home override |
