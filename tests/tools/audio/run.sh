#!/usr/bin/env bash
# Checks for scripts/tools/lattice_allpass (tools/audio/*.sh).
#
# The reference values were recorded from the numpy/matplotlib scripts this
# tool replaced:
#   - numpy default_rng(seed).standard_normal(1440) for the six hi-hat seeds,
#     printed with %.17g, hashed with SHA-256;
#   - SHA-256 of the reference input.wav (byte-identical in the Flow port);
#   - the printed reflections and RMS lines.
# The two all-pass outputs run through the stdlib's f32 lattice, so they
# are checked by format and length here; against the float64 reference they
# differ by at most 1 LSB on 115 and 162 of 144000 samples.
#
# Usage: tests/tools/audio/run.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
cd "$ROOT"

pass=0
fail=0
ok() { echo "PASS $1"; pass=$((pass + 1)); }
bad() { echo "FAIL $1"; fail=$((fail + 1)); }

sha() {
    if command -v shasum >/dev/null 2>&1; then
        shasum -a 256 "$@" | cut -c1-64
    else
        sha256sum "$@" | cut -c1-64
    fi
}

BIN="$(tools/audio/build_lattice_allpass.sh)"
work="$(mktemp -d "${TMPDIR:-/tmp}/flow-audio-tests.XXXXXX")"
trap 'rm -rf "$work"' EXIT

# numpy's Generator stream, bit for bit.
while read -r seed want; do
    got="$("$BIN" normals "$seed" 1440 | sha)"
    if [ "$got" = "$want" ]; then ok "normals seed $seed"; else bad "normals seed $seed ($got)"; fi
done <<'EOF'
250 8c01848b869fed0cc74f895ec5ad4d38b172fa50d0657e1c875d51106303df30
750 2835689ad7819d8ad35cd3a51c8c08a32b992c8628568fbb223e4761a0763153
1250 0636583a9dc39988fe47a075efee42b14567858cdc0c88d5f69583ae3412dd3f
1750 fc1d431f11a66ebbdfc2eaf1266c7c5076521c50279b7fcb2995cec88816710e
2250 e655efbe6d57fde867d24e37678adfc15e92d1e29c3c8d0feed1bb3f5fee2db5
2750 a3d7ed8771bcd02835f3123b002afc9b4a0ffcfca1736057cd3c188c16217852
EOF

# The demo, with every output redirected into the temp dir.
if LATTICE_ALLPASS_OUT="$work" "$BIN" demo --no-open > "$work/stdout" 2> "$work/stderr"; then
    ok "demo exit 0"
else
    bad "demo exit status"
    cat "$work/stderr"
fi

head -3 "$work/stdout" > "$work/head"
cat > "$work/head.expected" <<'EOF'
Schur reflections k = [-0.86768672  0.52942705 -0.13723952  0.012     ]
RMS  in=0.1774  static=0.1774  mod=0.1774
RMS ratio static=1.0000  mod=1.0000
EOF
if cmp -s "$work/head" "$work/head.expected"; then ok "demo printed numbers"; else bad "demo printed numbers"; diff -u "$work/head.expected" "$work/head" || true; fi

audio="$work/build/audio/lattice_allpass"
header="524946462465040057415645666d74201000000001000100\
80bb000000770100020010006461746100650400"
for w in input output_static_allpass output_modulated_allpass; do
    f="$audio/$w.wav"
    size="$(wc -c < "$f" | tr -d ' ')"
    got="$(od -A n -t x1 -N 44 "$f" | tr -d ' \n')"
    if [ "$size" = "288044" ] && [ "$got" = "$header" ]; then
        ok "$w.wav: 16-bit mono 48 kHz, 144000 frames"
    else
        bad "$w.wav header/size ($size)"
    fi
done
if [ "$(sha "$audio/input.wav")" = "1c0d2a8ae84b2488102b5fb9e34cdfb9bcb0efcc3774d25b6fbe6b3d1e28f103" ]; then
    ok "input.wav matches the reference bytes"
else
    bad "input.wav differs from the reference"
fi

plots="$work/build/plots/schur_lattice_allpass"
figs="$work/docs/research/schur_lattice_allpass/figures"
for n in dsp_bode_pz_groupdelay dsp_impulse_step audio_waveforms audio_rms_envelope \
         audio_spectrograms audio_modulation_proof audio_phase_difference; do
    f="$plots/$n.svg"
    if [ -s "$f" ] && head -c 5 "$f" | grep -q '<?xml' && tail -n 1 "$f" | grep -q '</svg>' \
        && cmp -s "$f" "$figs/$n.svg"; then
        ok "$n.svg written and copied"
    else
        bad "$n.svg"
    fi
done

echo "audio tool checks: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
