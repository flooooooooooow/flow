#!/usr/bin/env bash
#
# Render every audio example to a WAV and assert on the samples.
#
# This is how audio is covered on a machine with no sound card. Each example
# writes a file instead of opening a device (FLOW_AUDIO_RENDER), reads that
# file back, and gates its own exit code on the checks in
# stdlib/audio/verify.flow: duration, peak against the safety ceiling, no NaN
# or infinity, fades present at both ends, and for the tonal ones a Goertzel
# check that the loudest partial is the frequency the example announced.
#
# Every example is rendered twice and the two WAVs must be byte-identical.
# A render that is not reproducible is a bug even when it passes the checks.
#
# No audio device is opened at any point.
#
# Usage:  scripts/render_audio_examples.sh [output-dir]
# Exit:   0 only if every example rendered, verified and reproduced.

set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="${1:-$ROOT/build/audio}"
LOGS="$OUT/logs"

EXAMPLES=(
    filter_sweep
    adsr_vs_click
    fm_voice
    karplus_strong
    drum_machine
    delay_feedback_guard
    stereo_width
    evening_piece
)

mkdir -p "$OUT" "$LOGS"
cd "$ROOT" || exit 1

pass=0
fail=0
failed=""

for name in "${EXAMPLES[@]}"; do
    src="examples/audio/$name.flow"
    if [ ! -f "$src" ]; then
        echo "MISSING  $src"
        fail=$((fail + 1))
        failed="$failed $name(missing)"
        continue
    fi

    if ! FLOW_AUDIO_RENDER="$OUT/$name.wav" ./flow audio "$src" \
            >"$LOGS/$name.log" 2>&1; then
        echo "FAIL     $name (render or verification)"
        tail -20 "$LOGS/$name.log" | sed 's/^/         /'
        fail=$((fail + 1))
        failed="$failed $name"
        continue
    fi

    if ! FLOW_AUDIO_RENDER="$OUT/$name.rerun.wav" ./flow audio "$src" \
            >"$LOGS/$name.rerun.log" 2>&1; then
        echo "FAIL     $name (second render)"
        fail=$((fail + 1))
        failed="$failed $name(rerun)"
        continue
    fi

    if ! cmp -s "$OUT/$name.wav" "$OUT/$name.rerun.wav"; then
        echo "FAIL     $name (renders differ between runs)"
        fail=$((fail + 1))
        failed="$failed $name(nondeterministic)"
        continue
    fi
    rm -f "$OUT/$name.rerun.wav"

    checks=$(grep -c '^    \[ok  \]' "$LOGS/$name.log")
    bytes=$(wc -c <"$OUT/$name.wav" | tr -d ' ')
    printf 'ok       %-22s %s checks, %s bytes\n' "$name" "$checks" "$bytes"
    pass=$((pass + 1))
done

echo
echo "audio renders: $pass passed, $fail failed  (wav in $OUT, logs in $LOGS)"
if [ "$fail" -ne 0 ]; then
    echo "failed:$failed"
    exit 1
fi
exit 0
