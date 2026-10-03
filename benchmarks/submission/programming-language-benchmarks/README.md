# Submission: programming-language-benchmarks

Target suite: https://github.com/andrewmcwattersandco/programming-language-benchmarks

The suite adds a language by placing `<test>.<ext>` files in each test
directory and extending the `bench` shell script with a per-language block.
No Flow-specific harness is needed: each program is a single file with a
`main` that the suite times end to end with hyperfine.

## Files for the submission

| Upstream location | File here |
| --- | --- |
| `minimal/minimal.flow` | `minimal.flow` |
| `record/record.flow` | `record.flow` |

`record.flow` matches `record/record.c` semantically: allocate
8,388,608 records, fill `id`, free, no output. `minimal.flow` returns 0.

The `json` test is deferred: upstream implementations parse every file in
`jsonexamples/` with the ecosystem's usual JSON library, and Flow has no
bundled JSON library to use idiomatically yet.

## `bench` hook

Add after the Zig block in `bench`:

```sh
    # Flow
    if [ -f ${file}.flow ] \
    && command -v flow > /dev/null \
    && should_run_language "flow"
    then
        FLOW_BUILD_ROOT=$PWD flow compile ${file}.flow > /dev/null 2>&1
        run_benchmark "./${file}" "flow           "
    fi
```

`flow compile <file>` writes the binary to `FLOW_BUILD_ROOT/<stem>`.

## Flags and version

- Compiler: `flow compile` (Stage-A flowc, C backend, `cc -O2`).
- Version: see `VERSION` at the repository root.
- No Flow-specific flags are required; the compiled binary is benchmarked
  like the C/Rust/Go outputs.

## Local verification

```bash
FLOWC_BUNDLE=1 FLOWC_DIR=. FLOWC_IN=minimal.flow FLOWC_OUT=/tmp/m.c \
    compiler/build/flowc_bootstrap
cc -O2 -o /tmp/m /tmp/m.c -lm && /tmp/m && echo ok
```

Same for `record.flow`. Both exit 0.

## Status

Pack prepared locally. Blocked on upstream submission because the execution environment does not possess GitHub repository-admin tokens to open an upstream PR.

## How to use the patch

This patch file (`patch/0001-Add-Flow-implementations.patch`) represents the state that should be merged upstream in the `programming-language-benchmarks` repository.

Since we cannot open the PR via API (no admin tokens available in this environment), a user can clone the target repository, apply this patch (`git am 0001-Add-Flow-implementations.patch`), and open the PR from their local machine.
