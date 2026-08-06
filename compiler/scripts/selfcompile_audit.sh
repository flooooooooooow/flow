#!/usr/bin/env bash
# Every module under compiler/src must bundle-emit C that the C compiler
# accepts with no errors. This is the Phase-B exit condition of
# docs/project/self-hosting.md turned into a gate: if a language gap reappears,
# it shows up here as a named module with a count of C diagnostics.
#
#   ./compiler/scripts/selfcompile_audit.sh
#   FLOWC_AUDIT_BIN=compiler/build/flowc_bootstrap ./compiler/scripts/selfcompile_audit.sh
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
mkdir -p compiler/build/audit

DRV="${FLOWC_AUDIT_BIN:-}"
if [[ -z "$DRV" ]]; then
    for cand in \
        compiler/build/stage_a_driver_flow_self \
        compiler/build/stage_a_driver_flow_g2 \
        compiler/build/stage_a_driver_flow \
        compiler/build/flowc_bootstrap
    do
        if [[ -x "$cand" ]]; then
            DRV="$cand"
            break
        fi
    done
fi
if [[ -z "$DRV" ]]; then
    echo "selfcompile_audit: no flowc driver — run bootstrap_from_c.sh first" >&2
    exit 1
fi
echo "=== self-compile audit via ${DRV} ==="

fail=0
for f in compiler/src/*.flow; do
    name="$(basename "$f" .flow)"
    out="compiler/build/audit/${name}.c"
    log="compiler/build/audit/${name}.log"
    rm -f "$out"
    if ! FLOWC_BUNDLE=1 FLOWC_DIR=compiler/src "$DRV" "$f" "$out" >"$log" 2>&1; then
        echo "FAIL ${name}: flowc could not emit"
        tail -5 "$log"
        fail=1
        continue
    fi
    errs="$(cc -fsyntax-only -ferror-limit=0 "$out" 2>&1 | grep -c 'error:')"
    if [[ "$errs" -ne 0 ]]; then
        echo "FAIL ${name}: ${errs} C errors"
        cc -fsyntax-only -ferror-limit=0 "$out" 2>&1 | grep 'error:' \
            | sed -E 's/^[^:]+:[0-9]+:[0-9]+: //' | sort | uniq -c | sort -rn | head -5 \
            | sed 's/^/    /'
        fail=1
        continue
    fi
    printf 'PASS %-14s %8s bytes of C, 0 diagnostics\n' "$name" "$(wc -c <"$out" | tr -d ' ')"
done

if [[ "$fail" -ne 0 ]]; then
    echo "FAIL selfcompile_audit: compiler/src does not fully compile under flowc" >&2
    exit 1
fi
echo "ALL PASS selfcompile_audit (all of compiler/src compiles under flowc)"
