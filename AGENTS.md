# Agent Coordination Notes

## Operating contract

The full loop (intake, triage, claim, verify, review, merge, learn) is in
`docs/project/agentic-loop.md`. Placement rules are in
`docs/project/repository-structure.md`. GitHub issues, pull requests, CI and
`ROADMAP.md` are the live sources of truth.

Before work, read the issue, recent commits and open pull requests, then the
neighbouring code and tests. Do not start a second implementation of work a
live session or open pull request already covers. If the request is already
fixed, prove that and stop.

Scoped work whose intended behaviour is clear may proceed autonomously. New
syntax or semantics, compatibility breaks, public API contracts,
ownership and lifetime rules, effect semantics, release policy and security
policy need an explicit design decision first. Record open ones in
`docs/project/Questions.md`.

Keep one semantic purpose per pull request. Establish the baseline before
blaming a failure on your change, run the narrow proof for what you changed,
then the gate for the touched surface. A new regression test must fail on
the old behaviour. The pull request records the baseline, the proof, the
gates run, any generated state and the risk.

When a failure mode repeats, fix the loop with a test, CI rule, template or
repository invariant.

## Flow first

New code in this repository is written in Flow. This covers features,
tools, scripts, CI checks, parity gates and tests. Python and shell are
legacy that is being ported away.

- Do not add a `.py` file or a shell script. Write the program in Flow.
  When Flow needs an external command (git, find, cc, clang), run it with
  `std.process` (docs/library/process.md): argv, captured stdout and
  stderr, exit status, timeout, environment and working directory, with no
  shell in between. `std.regex` covers Python-style regular expressions.
- Run a repository program with `./flow tool NAME` (for
  `scripts/tools/NAME/main.flow` or `tools/NAME/main.flow`) or
  `./flow tool PATH.flow`. It builds the program with the Stage-A flowc from
  the checked-in bootstrap C, caches it in `build/flow-tools`, and runs it
  with `FLOW_REPO_ROOT` set. `./flow tool --path NAME` prints the binary.
  A tool needs no shell wrapper; point callers at `./flow tool`.
  `tools/flow_cli/sys.flow` has shell-like helpers (run, capture, files,
  temp dirs, globbing) for programs that replace a script.
- Do not grow existing Python. The Python compiler (`src/flow/`) is
  deleted; compiler features belong in `compiler/src/`.
- New tests are `.flow` programs under `tests/lang/`. `main()` returns 0 on
  success and a nonzero check number on failure. Do not add pytest tests.
- When porting Python or shell, show parity (same stdout, stderr, exit code
  and written files on real input and on an error case), switch the
  callers, and delete the old file in the same PR. Then lower the baseline:
  `./flow tool python_ratchet --update` or `./flow tool shell_ratchet --update`.
- When Flow cannot express something, work around it and open an issue
  naming the gap. That is how the language gets the feature.

Enforcement. CI runs two Flow programs. `./flow tool python_ratchet` fails
when a new `.py` file appears or total tracked Python exceeds
`tools/python_ratchet/baseline.txt`. `./flow tool shell_ratchet` fails when
a new shell script appears (`.sh`, `.bash`, or an extensionless file with a
`#!` line for sh, bash, zsh, ksh or dash) or the tracked shell lines exceed
`tools/shell_ratchet/baseline.txt`. Claude Code sessions in this repo also
load `.claude/settings.json`, whose hook refuses to create a `.py` file.
Vendored trees (`third_party/`, `.lake/`) are exempt.
`./flow tool script_refs` fails when a tracked `.flow` file names a
`scripts/...` or `compiler/scripts/...` path that does not exist, so a
deleted script cannot stay referenced.

A few scripts have to stay shell. They are listed with a reason in
`tools/shell_ratchet/allow.txt` and sit outside the line total: the `./flow`
stub, which builds flowc and the CLI with cc before any Flow program
exists; the `flow-lsp` editor launcher; and
`compiler/scripts/bootstrap_from_c.sh`, which proves the checked-in
bootstrap C rebuilds itself with cc alone and so cannot depend on a binary
built from that C. Adding to the list is a reviewed change with a reason.

The baselines only move down. `--update` drops deleted files and lowers
the line limit. It never adds a file.

Both ratchets are built from `compiler/bootstrap/flowc_stage_a.c`, so they
need a C compiler and no Python.

## Bootstrap C regeneration workflow

The checked-in `compiler/bootstrap/flowc_stage_a.c` must stay byte-identical to
what flowc emits from `compiler/src/main.flow` in bundle mode. When you edit
any file under `compiler/src/`, you must regenerate the bootstrap C before
committing, or the `bootstrap_from_c.sh --verify` fixed-point check will fail.

### Regeneration steps

flowc regenerates itself. There is no Python step: the binary built from the
previous bootstrap C compiles your edited `compiler/src`, the result compiles
it again, and the C stops changing (a fixed point, usually at the second
generation). `self_host_full.flow` proves that fixed point on every run.

Link with `-lm`: the proof layer puts math calls into flowc, and Linux does
not link libm by default.

```bash
# 1. Selftest the edited compiler. flowc_host.flow builds a flowc from the
#    current compiler/src with the binary of the checked-in bootstrap C.
env -u FLOWC_IN -u FLOWC_OUT "$(./flow tool compiler/scripts/flowc_host.flow)"
# Look for "flowc: PASS" at the end.

# 2. Regenerate: self-emit from the previous bootstrap until the C reaches a
#    fixed point, then rewrite compiler/bootstrap/flowc_stage_a.c and rebuild
#    compiler/bootstrap/flowc_stage_a and compiler/build/flowc_bootstrap.
./compiler/scripts/bootstrap_from_c.sh --regen

# 3. Run the full verification
./compiler/scripts/bootstrap_from_c.sh --verify
./flow tool compiler/scripts/self_host_full.flow
./flow tool compiler/scripts/roundtrip.flow
```

Step 2 by hand, for when you need to see each generation:

```bash
cc -O2 -o compiler/build/flowc_gen0 compiler/bootstrap/flowc_stage_a.c -lm
FLOWC_BUNDLE=1 FLOWC_DIR=compiler/src FLOWC_IN=compiler/src/main.flow \
  FLOWC_OUT=compiler/build/gen1.c ./compiler/build/flowc_gen0
cc -O2 -o compiler/build/flowc_gen1 compiler/build/gen1.c -lm
FLOWC_BUNDLE=1 FLOWC_DIR=compiler/src FLOWC_IN=compiler/src/main.flow \
  FLOWC_OUT=compiler/build/gen2.c ./compiler/build/flowc_gen1
cmp -s compiler/build/gen1.c compiler/build/gen2.c \
  && echo "FIXED POINT OK" || echo "not yet: build gen2 and emit gen3"
cp compiler/build/gen2.c compiler/bootstrap/flowc_stage_a.c
cc -O2 -o compiler/bootstrap/flowc_stage_a compiler/bootstrap/flowc_stage_a.c -lm
```

gen1.c and gen2.c differ only when your edit changes the C that flowc writes
(a cgen change): gen1 is your compiler as emitted by the old one, gen2 as
emitted by itself. Keep going until two generations agree.

Then run the parity gates for what you touched. All of them work without
Python in golden mode: `parity_lowering.flow`, `parity_effects.flow`,
`parity_proofs.flow`, `parity_mlir.flow`, `parity_field_dsl.flow`,
`parity_dynamics_dsl.flow`, `parity_flow_blocks.flow`, `parity_shader_dsl.flow`,
`parse_coverage.flow --check`, `fmt_check.flow --check` and
`corpus_parity.flow --check`, all under `compiler/scripts/`. A `.flow` gate
runs with `./flow tool compiler/scripts/<name>.flow`. The C output
goldens are `./flow tool tests/cgen/run.flow`, and the language tests are
`./flow test-lang`.

### Coordination protocol

If multiple agents are editing `compiler/src/` simultaneously:

1. **Announce your scope.** Note which files you are editing below.
2. **Regenerate bootstrap C last.** Only regenerate after all `compiler/src/`
   edits are done and the selftest of the edited compiler passes:
   ```bash
   env -u FLOWC_IN -u FLOWC_OUT "$(./flow tool compiler/scripts/flowc_host.flow)"
   # Look for "flowc: PASS" at the end
   ```
3. **Commit bootstrap C in a separate commit** from source edits, with a
   message like `fix: regenerate bootstrap C after <change>`. This avoids
   merge conflicts on the large generated file.
4. **If the old bootstrap cannot compile your sources**, do not regenerate
   the bootstrap C. Fix the source first. flowc_host.flow prints the error.

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
#665, #667, #671). Not merged. The Python MLIR generator it hooked into is
deleted, so the lane now lands as a pass in `compiler/src/mlirgen.flow`
under the same `FLOW_DENOTATIONAL=1` switch (docs/design/mlir-in-flow.md).

The Python compiler is deleted: flowc is the only compiler for C and MLIR.
The tests in `tests/scripts/` are Flow programs (shared harness:
`tests/scripts/harness.flow`) that drive `./flow`, the tools and the docs
as subprocesses (`./flow test-scripts`); no pytest is left. Front-end
crashes are `./flow tool tests/fuzz/run.flow` and the Stable corpus is
`./flow tool tests/conformance/run.flow`.

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
