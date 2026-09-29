# Agent Coordination Notes

## Flow first

New code in this repository is written in Flow. This covers features,
tools, scripts, CI checks, parity gates and tests. Python is legacy that
is being ported away.

- Do not add a `.py` file. Write the program in Flow. When Flow needs an
  external command (git, find, clang), use a thin bash shim that runs the
  command and leaves its output in `build/` for the Flow program to read.
  `scripts/tools/repo_stats/` and `tools/python_ratchet/` show the pattern.
- Do not grow existing Python. A bug fix in `src/flow/` is fine when it is
  small. A new feature belongs in the Flow compiler under `compiler/src/`.
- New tests are `.flow` programs under `tests/lang/`. `main()` returns 0 on
  success and a nonzero check number on failure. Do not add pytest tests.
- When porting Python, delete it in the same PR once parity is shown, then
  run `./scripts/python_ratchet.sh --update` to lower the baseline.
- When Flow cannot express something, work around it and open an issue
  naming the gap. That is how the language gets the feature.

Enforcement. CI runs `./scripts/python_ratchet.sh`, a Flow program that
fails when a new `.py` file appears or total tracked Python exceeds
`tools/python_ratchet/baseline.txt`. Claude Code sessions in this repo
also load `.claude/settings.json`, whose hook refuses to create a `.py`
file. Vendored trees (`third_party/`, `.lake/`) are exempt.

The baseline only moves down. `--update` drops deleted files and lowers
the line limit. It never adds a file.

The ratchet program is built from `compiler/bootstrap/flowc_stage_a.c`, so
it needs a C compiler and no Python.

## Bootstrap C regeneration workflow

The checked-in `compiler/bootstrap/flowc_stage_a.c` must stay byte-identical to
what flowc emits from `compiler/src/main.flow` in bundle mode. When you edit
any file under `compiler/src/`, you must regenerate the bootstrap C before
committing, or the `bootstrap_from_c.sh --verify` fixed-point check will fail.

### Regeneration steps

Link with `-lm`: the proof layer puts math calls into flowc, and Linux does
not link libm by default.

```bash
# 1. Build a temporary bootstrap binary from the CURRENT checked-in C
cc -O2 -o compiler/build/flowc_bootstrap compiler/bootstrap/flowc_stage_a.c -lm

# 2. Emit main.flow in bundle mode using the Python host (picks up your edits)
FLOWC_BUNDLE=1 FLOWC_DIR=compiler/src \
  FLOWC_IN=compiler/src/main.flow FLOWC_OUT=compiler/build/bootstrap_regen.c \
  FLOW_HOST=python ./flow run compiler/src/main.flow

# 3. Verify fixed point: the new binary emits the same C
cp compiler/build/bootstrap_regen.c compiler/bootstrap/flowc_stage_a.c
cc -O2 -o compiler/build/flowc_bootstrap compiler/bootstrap/flowc_stage_a.c -lm
FLOWC_BUNDLE=1 FLOWC_DIR=compiler/src \
  FLOWC_IN=compiler/src/main.flow FLOWC_OUT=/tmp/verify.c \
  ./compiler/build/flowc_bootstrap
cmp -s compiler/bootstrap/flowc_stage_a.c /tmp/verify.c \
  && echo "FIXED POINT OK" || echo "DRIFT"

# 4. Rebuild the checked-in binary
cc -O2 -o compiler/bootstrap/flowc_stage_a compiler/bootstrap/flowc_stage_a.c -lm

# 5. Run the full verification
./compiler/scripts/bootstrap_from_c.sh --verify
./compiler/scripts/self_host_full.sh
```

Then run the parity gates for what you touched. All of them work without
Python in golden mode: `parity_lowering.sh`, `parity_effects.sh`,
`parity_proofs.sh`, `parity_mlir.sh`, `parity_field_dsl.sh`,
`parity_dynamics_dsl.sh`, `parity_flow_blocks.sh`, `parity_shader_dsl.sh`,
`parse_coverage.sh --check`, `fmt_check.sh --check` and
`corpus_parity.sh --check`, all under `compiler/scripts/`.

### Coordination protocol

If multiple agents are editing `compiler/src/` simultaneously:

1. **Announce your scope.** Note which files you are editing below.
2. **Regenerate bootstrap C last.** Only regenerate after all `compiler/src/`
   edits are done and the selftest passes via the Python host:
   ```bash
   FLOW_HOST=python ./flow run compiler/src/main.flow
   # Look for "flowc: PASS" at the end
   ```
3. **Commit bootstrap C in a separate commit** from source edits, with a
   message like `fix: regenerate bootstrap C after <change>`. This avoids
   merge conflicts on the large generated file.
4. **If the Python host emit fails**, do NOT regenerate the bootstrap C.
   Fix the source first.

### Current in-flight work

Merge train of 2026-09-27 to 2026-09-29, all squash-merged to main: #980
(ruff), #966 (Stage-A test blockers), #981 (Python ratchet), #965, #959,
#960, #1000, #956 (Field DSL), #955, #971, #987 (REPL), #1002 (prose),
#1003 (Stage-A batch 2), #999 (dynamics DSL and flow blocks), #998 (Shader
DSL), #989 (package manager), #1001 (parse coverage), #1012 (pattern, ui,
fork, sort and unit lowering), #1014 (algebraic effects), #1013 (proof
layer), #1015 (Stage-A batch 3), #1016 (native LSP), #1019 (lossless
formatter), #1020 (MLIR emitter) and #1018 (corpus parity). Open from it:
#1021 (CI jobs for the parity gates) and #1022 (ratchet baseline).

Every source read in flowc goes through `flowc_expand_stages_in_place` in
`resolve.flow`: the fill-shader stub (mask 8), then the Field DSL (1), the
dynamics DSL (2) and flow blocks (4). The bundle takes up to 128 modules and
4 MiB of C.

Denotational MLIR lane (2026-09-22): a `flow.*` dialect that keeps the
vector-field structure of `flow` evolution blocks for the MLIR passes (#664,
#665, #667, #671). Not merged: `src/flow/denotational_mlir.py`, the
`denotational_blocks` kwarg of `flow_to_mlir` and the `FLOW_DENOTATIONAL=1`
path in `transpiler.py` are not on main.

As of 2026-09-29 the Python suite on CI is at 1656 passed, 0 failed, 103
skipped, and the tracked Python is 310 files and 79712 lines.

### Bootstrap suite

The bootstrap suite is every `.flow` file under `tests/lang/` (183 files)
compiled by the Stage-A compiler in bundle mode, then by cc. flowc reads its
input and output paths from `FLOWC_IN` and `FLOWC_OUT`. Paths given as
arguments are ignored and flowc runs its self-test instead, which is how an
older version of this loop reported every file as passing.

```bash
cc -O2 -o compiler/build/flowc_bootstrap compiler/bootstrap/flowc_stage_a.c -lm
BOOT=compiler/build/flowc_bootstrap
pass=0; fail=0
for f in $(find tests/lang -name "*.flow" | sort); do
  rm -f /tmp/out.c
  if FLOWC_BUNDLE=1 FLOWC_DIR=. FLOWC_IN="$f" FLOWC_OUT=/tmp/out.c "$BOOT" >/dev/null 2>&1 \
     && cc -O0 -Itests/lang -o /tmp/out /tmp/out.c -lm >/dev/null 2>&1; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1)); echo "  FAIL $f"
  fi
done
echo "pass=$pass fail=$fail"
```

Current on main (2026-09-29): 179 pass, 4 fail.

- Closures passed where a function pointer is expected (2): test_closures,
  test_fn_ptr. The C gets a closure struct where it wants `int32_t (*)(int32_t)`.
- Cross-module generics (1): test_generic_channels (`Chan` and
  `channel_send_i32` undeclared).
- Runtime link (1): test_concurrent_link needs the concurrency runtime,
  which this loop does not link.

The include path `-Itests/lang` is needed for test_c_import and
test_extern_type, whose helper header lives in `tests/lang/`.

## Meta-Agents and Repositories

When building a repository or project with the Flow language, agents are encouraged to:
1. **Adhere to Flow Idioms**: Utilize language features properly, such as `let` vs `let mut`, proper pointer usage (e.g., `ptr<T>`), explicit typing, and leverage algebraic effects or DSL integrations where appropriate.
2. **Request Flow Features**: If you encounter limitations, missing features, or bugs in the language while building a repository, please raise an issue or feature request back to the core Flow repository. Be as specific as possible with the use case and current workarounds.
3. **Continuous Improvement**: Ensure any bugs or gaps in standard library functionality are communicated so the core team (and core agents) can improve the language.
