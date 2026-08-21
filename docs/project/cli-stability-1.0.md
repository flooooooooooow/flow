# Flow 1.0 CLI stability contract

Flow 1.0 does not freeze every command currently exposed by the development driver. The 1.x compatibility promise covers a small core used to compile, execute, test and format Stable Flow; specialised backends and developer demos can continue evolving without turning their current spelling into a permanent API.

## Stable command surface

| Command | Stable 1.x contract |
| --- | --- |
| `flow help` / `flow --help` | Displays command help and exits successfully. Additive documentation and newly listed Experimental commands are not breaking changes. |
| `flow version` / `flow --version` | Prints the Flow toolchain version and exits successfully. The exact decorative wording is not a compatibility surface; the semantic version is. |
| `flow compile <program.flow>` | Compiles Stable Flow through the default C production path and returns success only when a usable executable is produced. A missing/invalid input or compilation/link failure is nonzero. |
| `flow compile --backend=c <program.flow>` | Explicit spelling of the default Stable C backend. It is equivalent in compatibility status to omitting `--backend`. |
| `flow run <program.flow>` | Compiles through the Stable C path, executes the resulting program, and returns that program's exit status when execution is reached. Compile/tool failures are nonzero. |
| `flow run --backend=c <program.flow>` | Explicit spelling of the default Stable C execution path. |
| `flow test` | Runs the project/repository Flow test command and returns zero only when the selected test run succeeds. Existing strict/tier flags may be promoted separately; this contract does not freeze every development-only test flag. |
| `flow fmt <files...>` | Formats Stable Flow source. The command name and role are Stable; #651 still requires deterministic/idempotent qualification over the Stable grammar before the final 1.0 tag. |

`<program.flow>` remains a path to a Flow source file. The CLI may improve diagnostics, progress output, colour and other presentation during 1.x; scripts must depend on exit status and documented artefacts rather than exact human-readable prose.

## Exit behaviour

The Stable contract intentionally uses categories rather than reserving a large table of numeric error codes that the current driver does not implement. `0` means the requested tool operation succeeded. A compile, validation, usage or toolchain failure is nonzero. For `flow run`, once the user's executable starts, its exit status is propagated by the driver. More granular machine-readable error categories may be added compatibly later, but 1.x will not silently reinterpret a successful operation as failure or discard a program exit status.

## Compiler-host boundary

The production contract is the self-hosted compiler path. `FLOW_HOST=flowc` describes that implementation today, but the environment variable itself is a migration/development control rather than a Stable 1.x API. `FLOW_HOST=python` and `FLOW_HOST=auto` remain compatibility/reference modes while #642 completes the cutover. Stable applications should invoke the ordinary commands without selecting a host.

## Experimental command surface

All other commands and flags exposed by the current development driver remain Experimental unless another stability entry explicitly promotes them. This includes MLIR/JIT/GPU commands and `--backend=mlir`; audio, graphics, shader, Vulkan and recording helpers; debugger/DAP/playground tooling; advanced `transpile`/`explain`/FIR commands; specialised `test-*` commands; Python/WASM generators; and package/registry/native-build commands such as `init`, `add`, `pkg`, `publish`, `build-native` and `run-native`.

Experimental does not mean deprecated or low quality. It means their command names, flags, output formats and platform availability may still change during 1.x without violating the Stable CLI compatibility promise.

## Compatibility rule

Within Flow 1.x, Stable commands will not be removed or incompatibly repurposed. A replacement must be introduced additively and the old Stable spelling deprecated under `STABILITY.md`. New optional flags and commands are compatible additions. Experimental commands can be promoted only with documentation and regression coverage appropriate to the guarantee being added.
