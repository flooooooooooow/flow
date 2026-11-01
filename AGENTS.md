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
`./flow tool script_refs` fails when a tracked `.flow` file, workflow or
the Makefile names a `scripts/...` or `compiler/scripts/...` path that
does not exist, so a deleted script cannot stay referenced.

A few scripts have to stay shell. They are listed with a reason in
`tools/shell_ratchet/allow.txt` and sit outside the line total: the `./flow`
stub, which builds flowc and the CLI with cc before any Flow program
exists; the `flow-lsp` editor launcher;
`compiler/scripts/bootstrap_from_c.sh`, which proves the checked-in
bootstrap C rebuilds itself with cc alone and so cannot depend on a binary
built from that C; and `tools/hooks/no_new_python.sh`, the hook in
`.claude/settings.json` that runs on every file write. Adding to the list
is a reviewed change with a reason.

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
   message like `fix: regenerate bootstrap C after <change>`, and make it
   the last commit on the branch, after merging `main`. On a conflict in it,
   take `main`'s copy and run `--regen` again; never hand-merge it. See
   "Branches, pull requests and merge conflicts" below.
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
formatter), #1020 (MLIR emitter) and #1018 (corpus parity), then #1021 (CI
jobs for the parity gates) and #1022 (ratchet baseline).

Every source read in flowc goes through `flowc_expand_stages_in_place` in
`resolve.flow`: the fill-shader stub (mask 8), then the Field DSL (1), the
dynamics DSL (2) and flow blocks (4). The bundle takes up to 128 modules and
4 MiB of C.

Denotational MLIR: a `flow.*` dialect that keeps the vector-field structure
of `flow` evolution blocks for the MLIR optimization issues (#664, #665,
#667, #671). Nobody is working on it. The Python prototype was written
against the retired compiler and never merged; it is kept at the tag
`archive/feat/denotational-mlir`. The design and the remaining Flow slice
for `compiler/src/mlirgen.flow` are in docs/design/denotational-mlir.md.
Other reference implementations against the Python compiler are listed in
docs/project/archive-tags.md.

The Python compiler is deleted: flowc is the only compiler for C and MLIR.
The tests in `tests/scripts/` are Flow programs (shared harness:
`tests/scripts/harness.flow`) that drive `./flow`, the tools and the docs
as subprocesses (`./flow test-scripts`); no pytest is left. Front-end
crashes are `./flow tool tests/fuzz/run.flow` and the Stable corpus is
`./flow tool tests/conformance/run.flow`.

### Bootstrap suite

The bootstrap suite is every `.flow` file under `tests/lang/` (254 files)
compiled by the Stage-A compiler (`compiler/build/flowc_bootstrap`, built
from the checked-in bootstrap C) in bundle mode, linked, and run. Its entry
point is `./flow test-lang`:

```bash
./flow test-lang
```

It type checks in strict mode, adds `-Itests/lang` for the helper header of
test_c_import and test_extern_type, links the concurrency runtime
(`runtime/flow_concurrency.c` and the rest, plus the archive built from
`lib/runtime/*.flow`) into any program that imports `concurrent`, and checks
the exit code and any `.expected` output. Pass file paths to run a subset.
Run it from the repository root.

Current on main (2026-10-01, macOS arm64): 254 pass, 0 fail.

An older version of this section was a hand-written loop over
`FLOWC_IN`/`FLOWC_OUT` and `cc ... -lm`. It linked no runtime, so
test_generic_channels, test_concurrent_link and test_import_stdlib_bare
failed with undefined `flow_thread_*` and `__atomic_*_n` symbols although
the compiler handles them. tests/scripts/bootstrap_suite_doc.flow runs the
command above on those three files.

## Branches, pull requests and merge conflicts

Many agents and people open pull requests against `main` at the same time,
and `main` lands through a merge queue (the `merge_group` trigger in
`.github/workflows/ci.yml`). Almost every conflict comes from a handful of
shared or generated files. These rules keep conflicts rare, and cheap when
they happen.

### Before you start

- Check open pull requests and live sessions for the same issue and for the
  same narrow file edit (see "Claim and deduplication" in
  `docs/project/agentic-loop.md`). If one exists, review or extend it rather
  than open a parallel one. Parallel pull requests for one rename conflict
  with each other, and all but one get closed.
- Branch from a current `main`, and open the pull request against `main`. A
  pull request whose base is another feature branch runs only a few checks
  and cannot enter the merge queue.
- Fetch full history. Sandboxes often clone with `--depth 1`, and in a
  shallow clone `main` and your branch look like unrelated histories:

  ```bash
  git fetch --unshallow origin || true   # no-op on a full clone
  git fetch origin main
  ```

### Keep the diff small

- One issue, one purpose, the smallest diff that fixes it. No drive-by
  reformatting, no renaming of shared constants or functions, no re-sorting
  of lists or tables you did not otherwise need to touch.
- If the change must touch a hotspot below, keep that part as small as you
  can and get it merged quickly, or split it into its own pull request so the
  rest of the work does not wait on it.

### Conflict hotspots

| File | Why it conflicts | What to do |
|---|---|---|
| `compiler/bootstrap/flowc_stage_a.c`, `compiler/bootstrap/flowc_stage_a` | Generated from all of `compiler/src/` as one translation unit, plus the binary built from it | Never hand-merge. Take `main`'s copy, finish the merge, then regenerate with `./compiler/scripts/bootstrap_from_c.sh --regen` as the last commit. Commit it only when your branch changes `compiler/src/`. |
| `docs/demos/overview.md` | Generated from `docs/demos/catalog.json` by `./flow tool demo_overview` | Edit the catalog, never the page. After merging `main`, run `./flow tool demo_overview` and commit its output. A stale page is the most common CI failure (`demo_overview_is_derived_from_catalog` in `tests/scripts/demo_gallery_docs.flow`, run by `./flow test-scripts`). |
| `docs/nav.json` | Its demo sections are generated from the catalog; the rest is edited by hand in many pull requests | After a catalog change run `./flow tool demo_nav`. Add hand entries in place, without re-sorting. Check with `./flow tool wiki_nav`. |
| `docs/library/stdlib-api.md` | Generated from `lib/stdlib` | Regenerate with `./flow tool gen_stdlib_docs`; CI runs `--check`. |
| `compiler/fixtures/mlir/corpus.txt`, the fixture goldens beside it (`*.mlir`, `*.gpu.mlir`, `*.w32.mlir`, `*.out`) and other golden files | One shared manifest of digests; most MLIR changes move some of its lines | Change only the entries for programs your change affects. See "Goldens" below. |
| `compiler/src/mlirgen.flow`, `compiler/src/mlir_bundle.flow`, `compiler/src/resolve.flow` | Central compiler files that most MLIR and front-end fixes edit | Keep the edit inside the function you are fixing. Do not move, reorder or reformat the code around it. Land it quickly. |

### Generated files: regenerate, never hand-merge

1. Do not commit a regenerated artifact unless your change requires it.
2. When it does, regenerate after merging `main` and make it the last
   commit on the branch, so it is built from `main` plus your change.
3. On a conflict in a generated file, take `main`'s version and regenerate.
   Never edit conflict markers in generated output. While the merge is in
   progress:

   ```bash
   # bootstrap C and binary
   git checkout origin/main -- compiler/bootstrap/flowc_stage_a.c compiler/bootstrap/flowc_stage_a
   # resolve the source files, then rebuild from the merged compiler/src:
   ./compiler/scripts/bootstrap_from_c.sh --regen
   ./compiler/scripts/bootstrap_from_c.sh --verify
   git add compiler/bootstrap/flowc_stage_a.c compiler/bootstrap/flowc_stage_a

   # demo overview and nav
   git checkout origin/main -- docs/demos/overview.md
   ./flow tool demo_overview
   ./flow tool demo_nav
   git add docs/demos/overview.md docs/nav.json

   git commit   # completes the merge commit
   ```

   If the branch does not change `compiler/src/`, `main`'s bootstrap C is
   already right: take it and do not regenerate.

### Goldens

`compiler/scripts/parity_mlir.flow` has one recording mode, `--record`. It
rewrites every fixture golden and the whole of `corpus.txt`, and it ignores
any further arguments: `--record --only <pattern>` is not a filter and still
records everything. A full record takes longer than most agent sandboxes
allow (CI gives the whole gate 20 minutes).

1. Run the gate: `./flow tool compiler/scripts/parity_mlir.flow`. Each
   affected corpus program fails with `FAIL corpus <path>: MLIR changed since
   the golden was recorded`.
2. Check that the list is what your change should affect. Many unrelated
   failures mean the change is wider than intended, or the branch is behind
   `main`. Merge `main` first.
3. Record on a machine with the time to do it, then keep only the entries
   your change explains and drop the rest:

   ```bash
   ./flow tool compiler/scripts/parity_mlir.flow --record
   git add -p compiler/fixtures/mlir     # stage only the affected entries
   git checkout -- compiler/fixtures/mlir   # drop every other rewrite
   ./flow tool compiler/scripts/parity_mlir.flow
   ```

4. Name the fix behind each changed golden in the pull request body.

After merging `main`, re-run the gate rather than trusting either side's
`corpus.txt`: a conflict there usually means both sides moved the same
program's digest.

### Keep your branch current

- Merge `main` into the branch often, and always before asking for review
  and after the merge queue rejects it:

  ```bash
  git fetch origin main
  git merge origin/main   # a real merge commit, with main as a parent
  ```

- Never use `--allow-unrelated-histories`. That error means the clone is
  shallow: fetch with `--unshallow` and merge again. Never force-push a pull
  request branch, never rewrite commits that are already pushed, never commit
  or push with `--no-verify`.
- A conflict is resolved only by a commit on the pull request's own branch
  that has `main` as a parent. A separate pull request stacked on the branch
  does not resolve it when its commit lacks `main` as a parent, and
  squash-merging such a pull request into the branch leaves the conflict in
  place.
- If you cannot push to the pull request's branch, say so in the pull
  request or session and stop. Do not open an empty, partial or stacked pull
  request in its place.

### When you change behaviour that a check asserts

Update every check that asserts the old behaviour in the same pull request.
Search before you push, for example `rg -n 'fibonacci' .github/workflows scripts tests`.
`examples/basics/fibonacci.flow` exits with status 55 and that is asserted in
`scripts/check_run_without_python.flow`, in several steps of
`.github/workflows/ci.yml` and in the Tier 1 job of
`.github/workflows/platform-qualification.yml`. Re-record the goldens that
capture the example's output in the same pull request.

### Before you push

- Run `git status` and `git diff --stat origin/main...HEAD`. Commit only the
  files your change needs. No runtime output: `persist/run_counter.bin` is
  tracked and gets rewritten when examples run, and scratch files such as
  `diff.txt`, logs and anything under `build/` stay out.
- Run the gates for what you touched:

  | Touched | Run |
  |---|---|
  | `compiler/src/` | The selftest, `--regen` and `--verify`, `self_host_full.flow` and `roundtrip.flow` from "Regeneration steps" above |
  | MLIR emitter | `./flow tool compiler/scripts/parity_mlir.flow`, `./flow tool tests/mlir_commands/run.flow` |
  | C emitter, language | `./flow tool tests/cgen/run.flow`, `./flow test-lang` |
  | Tools, scripts, CLI | `./flow test-scripts`, `./flow tool script_refs`, `./flow tool tests/cli/run.flow` |
  | Docs, demos, nav | `./flow tool doc_links`, `./flow tool doc_examples`, `./flow tool wiki_nav`, `./flow tool demo_overview --check --check-previews`, `./flow tool demo_nav --check` |
  | Tier 1 platforms | `./flow test --tier2 --strict`, `./compiler/scripts/bootstrap_from_c.sh` |

- Everything must be green before the merge queue takes the pull request,
  including the goldens and MLIR job, the self-host roundtrip and Tier 1 on
  ubuntu and macOS.
- In the pull request body write `Closes #N` only when the change fully
  fixes issue N, and `Part of #N` otherwise. Record the evidence that
  `docs/project/agentic-loop.md` asks for, including any generated state.

## AI Safety and Enforceable Authority

Per RFC #1544, source code and explanations authored by an AI agent carry no inherent authority. To maintain a safe repository lifecycle:
- Implementation of safety policies must be opt-in and backwards-compatible. New syntax or security-policy changes require a recorded design decision.
- All trust boundaries (source -> compiler, compiler -> backend, executable -> OS, PR author -> CI, CI -> protected branch, branch -> release) must be verified through independent, observable evidence.
- The `agent_sandbox` tool enforces OS containment. Do not assume safety solely based on static compiler effects without runtime confinement.
- Security-critical pull requests touching compiler, runtime, `agent_sandbox`, or workflows require review by a human CODEOWNER.
- Agents record and preserve competing claims and counterexamples during dispute resolution.
- A clean CI run is necessary but insufficient. Adversarial behavior must be demonstrably denied (such as through network or filesystem isolation) even if generated code bypasses safe subsets.

## Meta-Agents and Repositories

When building a repository or project with the Flow language, agents are encouraged to:
1. **Adhere to Flow Idioms**: Utilize language features properly, such as `let` vs `let mut`, proper pointer usage (e.g., `ptr<T>`), explicit typing, and leverage algebraic effects or DSL integrations where appropriate.
2. **Request Flow Features**: If you encounter limitations, missing features, or bugs in the language while building a repository, please raise an issue or feature request back to the core Flow repository. Be as specific as possible with the use case and current workarounds.
3. **Continuous Improvement**: Ensure any bugs or gaps in standard library functionality are communicated so the core team (and core agents) can improve the language.
