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

No active agents. The bootstrap suite is at 77/13 using FLOWC_IN/FLOWC_OUT
env vars (not positional args, which trigger the self-test). The Python unit
suite is at 1356 passed, 3 failed (numpy-dependent FIR route tests), 10 skipped.

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

Current: 77/13. Remaining failures: generics, closures, effects, spans,
time_blocks, unsigned_ints, fir_opts, hybrid_events, lifetime_domains,
generic_channels, gif_encoder, c_import_julia, c_import_python.
