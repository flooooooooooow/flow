# Agent Coordination Notes

## Bootstrap C regeneration workflow

The checked-in `compiler/bootstrap/flowc_stage_a.c` must stay byte-identical to
what flowc emits from `compiler/src/driver.flow` in bundle mode. When you edit
any file under `compiler/src/`, you must regenerate the bootstrap C before
committing, or the `bootstrap_from_c.sh --verify` fixed-point check will fail.

### Regeneration steps

```bash
# 1. Build a temporary bootstrap binary from the CURRENT checked-in C
cc -O2 -o compiler/build/flowc_bootstrap compiler/bootstrap/flowc_stage_a.c

# 2. Emit driver.flow in bundle mode using the Python host (picks up your edits)
FLOWC_BUNDLE=1 FLOWC_DIR=compiler/src \
  FLOWC_IN=compiler/src/driver.flow FLOWC_OUT=compiler/build/bootstrap_regen.c \
  FLOW_HOST=python ./flow run compiler/src/main.flow

# 3. Verify fixed point: the new binary emits the same C
cp compiler/build/bootstrap_regen.c compiler/bootstrap/flowc_stage_a.c
cc -O2 -o compiler/build/flowc_bootstrap compiler/bootstrap/flowc_stage_a.c
FLOWC_BUNDLE=1 FLOWC_DIR=compiler/src \
  ./compiler/build/flowc_bootstrap compiler/src/driver.flow /tmp/verify.c
cmp -s compiler/bootstrap/flowc_stage_a.c /tmp/verify.c \
  && echo "FIXED POINT OK" || echo "DRIFT"

# 4. Rebuild the checked-in binary
cc -O2 -o compiler/bootstrap/flowc_stage_a compiler/bootstrap/flowc_stage_a.c

# 5. Run the full verification
./compiler/scripts/bootstrap_from_c.sh --verify
./compiler/scripts/self_host_full.sh
```

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

No active agents. The bootstrap suite is at 79/11 using FLOWC_IN/FLOWC_OUT
env vars (not positional args, which trigger the self-test). The Python unit
suite is at 1424 passed, 0 failed, 6 skipped (all clean).

Bootstrap C was regenerated on 2026-08-14 to pick up span subscript, span
slicing, and array-to-span conversion at call sites. Fixed point verified.

### Bootstrap suite

The "Bootstrap suite" is the 90 `.flow` files in `tests/lang/` run through
the Stage-A compiler in bundle mode:

```bash
BOOT=compiler/build/flowc_bootstrap
pass=0; fail=0
for f in $(find tests/lang -name "*.flow" | sort); do
  if FLOWC_BUNDLE=1 FLOWC_DIR=. "$BOOT" "$f" "/tmp/out.c" >/dev/null 2>&1 \
     && cc -O0 -o /tmp/out "/tmp/out.c" >/dev/null 2>&1; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1)); echo "  FAIL $f"
  fi
done
echo "pass=$pass fail=$fail"
```

Current: 84/6 (with `-Itests/lang`). The 6 failures by category:

- DSL keywords (3): test_effects, test_hybrid_events, test_time_blocks
- Cross-module generics (1): test_generic_channels
- External C headers (2): test_c_import_julia, test_c_import_python

Note: test_c_import and test_extern_type pass with `-Itests/lang` (the helper
header lives in tests/lang/). The suite runner needs that include path.
test_generics now passes after adding generic monomorphization.

Recently landed: enum tagged unions, enum variant references, span indexing
with .data, span slicing with .data, array-to-span conversion at call sites.

## Meta-Agents and Repositories

When building a repository or project with the Flow language, agents are encouraged to:
1. **Adhere to Flow Idioms**: Utilize language features properly, such as `let` vs `let mut`, proper pointer usage (e.g., `ptr<T>`), explicit typing, and leverage algebraic effects or DSL integrations where appropriate.
2. **Request Flow Features**: If you encounter limitations, missing features, or bugs in the language while building a repository, please raise an issue or feature request back to the core Flow repository. Be as specific as possible with the use case and current workarounds.
3. **Continuous Improvement**: Ensure any bugs or gaps in standard library functionality are communicated so the core team (and core agents) can improve the language.
