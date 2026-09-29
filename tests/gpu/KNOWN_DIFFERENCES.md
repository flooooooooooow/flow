# `flow gpu`: where the Flow tool differs from the Python generator

`tools/gpu/main.flow` replaced `src/flow/metal_codegen.py`,
`src/flow/wgsl_codegen.py` and the inline Python in flow-driver. The goldens
in `tests/gpu/expected/` were recorded from the Python generator. The
shaders, host stubs, file names, messages and exit codes match it on every
case except the ones below. Each of those cases has a `KEEP` file, and its
golden holds the Flow tool's output.

## By design

- A construct WGSL cannot express stopped the Python generator with a
  `WgslUnsupported` traceback. The Flow tool prints the same message as one
  line, `error: <message>`, with the same exit status 1. The shaders written
  before the failing kernel stay written, as before. The goldens for these
  cases were recorded from Python with the traceback reduced to that line.
- The Python module resolver wrote a `.flow_cache/` directory of pickled
  syntax trees next to the program. The Flow tool writes no cache.

## Front end

The Flow tool reads programs with the flowc front end, the same parser and
import resolution as `flow compile`.

- `parse_error.flow` (metal, wgsl): both stop with exit status 1 at line 2,
  column 24. The message text is flowc's.
- `bad_import.flow` (metal, wgsl): both stop with exit status 1 on the
  unresolved import. The message text is flowc's.
- `tests/tools/lsp/fixtures/attr.flow` (metal, wgsl): the Python lexer treats
  `vec` as a keyword, so `let v: vec = 0` was a parse error there. flowc reads
  `vec` as a type name. The Metal case now generates the kernel (exit 0); the
  WGSL case stops on the type `vec`, which has no WGSL equivalent (exit 1).
- A function with an `@only(...)` mode guard is left out of the program, as
  in every other flowc tool. The Python resolver kept it. No @gpu function in
  the repository has a guard.
