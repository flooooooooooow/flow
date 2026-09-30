#!/usr/bin/env bash
# scripts/frames_to_gif.sh on tiny generated frames.
#
# Writes 8x6 binary PPM frames with printf (left half one colour, right
# half another), encodes them, and decodes the GIF with scripts/tools/gif_check:
# screen size, loop extension, frame count, and per frame the delay, the
# disposal and the composited colours of the first and last pixel. Also checks the
# summary line, the no-frames error and an argument error. No Python.
#
# Usage: tests/tools/frames_to_gif/run.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
cd "$ROOT"
work="$(mktemp -d "${TMPDIR:-/tmp}/flow-frames-to-gif.XXXXXX")"
trap 'rm -rf "$work"' EXIT
# The tool prints the output path normalised; so must the expectations.
work="$(cd "$work" && pwd)"

pass=0
fail=0
ok() { echo "PASS frames_to_gif/$1"; pass=$((pass + 1)); }
bad() { echo "FAIL frames_to_gif/$1"; fail=$((fail + 1)); }

"$ROOT/scripts/tools/build_tool.sh" frames_to_gif >/dev/null
GIF_CHECK="$ROOT/$("$ROOT/scripts/tools/build_tool.sh" gif_check)"

# check_gif FILE W H FRAMES DELAY_CS DISPOSAL PIXELS: gif_check's report
# against the expectation. PIXELS has one line per frame, six numbers: the
# RGB of the first pixel and of the last.
check_gif() {
    local file="$1" w="$2" h="$3" n="$4" delay="$5" disp="$6" pixels="$7" i=0
    local report r1 g1 b1 r2 g2 b2
    report="$("$GIF_CHECK" "$file" 0 0)" || { echo "gif_check failed"; return 1; }
    {
        echo "format=GIF"
        echo "width=$w"
        echo "height=$h"
        while read -r r1 g1 b1 r2 g2 b2; do
            echo "frame=$i delay_cs=$delay disposal=$disp first=$r1,$g1,$b1 last=$r2,$g2,$b2"
            i=$((i + 1))
        done < "$pixels"
        echo "frames=$n"
        echo "decoded=$n"
        echo "loop=0"
    } > "$file.want"
    grep -E '^(format|width|height|frame|frames|decoded|loop)=' <<<"$report" > "$file.got" || true
    diff -u "$file.want" "$file.got"
}

# pixel r g b: the \ooo escape for printf.
px() { printf '\\%03o\\%03o\\%03o' "$1" "$2" "$3"; }

# frame FILE r1 g1 b1 r2 g2 b2: 8x6, columns 0-3 colour 1, 4-7 colour 2.
frame() {
    local a b row="" y
    a="$(px "$2" "$3" "$4")"
    b="$(px "$5" "$6" "$7")"
    row="$a$a$a$a$b$b$b$b"
    {
        printf 'P6\n8 6\n255\n'
        for y in 1 2 3 4 5 6; do
            # shellcheck disable=SC2059 # the row is a printf escape string
            printf "$row"
        done
    } > "$1"
}

mkdir -p "$work/frames" "$work/empty"
frame "$work/frames/frame_00000.ppm" 255 0 0 0 0 255
frame "$work/frames/frame_00001.ppm" 0 255 0 255 255 0
frame "$work/frames/frame_00002.ppm" 0 0 255 255 255 255
frame "$work/frames/frame_00003.ppm" 40 80 120 200 100 50
# Not a frame: the glob is frame_*.ppm.
frame "$work/frames/other.ppm" 1 2 3 4 5 6

cat > "$work/all.txt" <<'EOF'
255 0 0 0 0 255
0 255 0 255 255 0
0 0 255 255 255 255
40 80 120 200 100 50
EOF
cat > "$work/even.txt" <<'EOF'
255 0 0 0 0 255
0 0 255 255 255 255
EOF

# case NAME EXPECTED_STDOUT CHECK_ARGS... -- ENCODER_ARGS...
case_gif() {
    local name="$1" want="$2"
    shift 2
    local check=()
    while [ "$1" != "--" ]; do check+=("$1"); shift; done
    shift
    local out rc=0
    out="$(scripts/frames_to_gif.sh "$@" 2>"$work/$name.err")" || rc=$?
    if [ "$rc" -ne 0 ]; then
        bad "$name"; echo "  exit $rc"; cat "$work/$name.err"; return
    fi
    if [ "$out" != "$want" ]; then
        bad "$name"; echo "  stdout: $out"; echo "  wanted: $want"; return
    fi
    if check_gif "${check[@]}" >"$work/$name.check"; then
        ok "$name"
    else
        bad "$name"; cat "$work/$name.check"
    fi
}

# Every frame, 10 fps: 100 ms is 10 cs.
case_gif all "$work/all.gif: 4 frames, 8x6, 0 KB" \
    "$work/all.gif" 8 6 4 10 2 "$work/all.txt" -- \
    "$work/frames" "$work/all.gif" --fps 10 --stride 1

# Every second frame at 50 fps: the delay floor is 20 ms.
case_gif stride "$work/sub/even.gif: 2 frames, 8x6, 0 KB" \
    "$work/sub/even.gif" 8 6 2 2 2 "$work/even.txt" -- \
    "$work/frames" "$work/sub/even.gif" --fps=50 --stride 2

# Downscale to 4 wide: height round(6 * 4 / 8) = 3, halves kept.
case_gif width "$work/small.gif: 4 frames, 4x3, 0 KB" \
    "$work/small.gif" 4 3 4 5 2 "$work/all.txt" -- \
    "$work/frames" "$work/small.gif" --stride 1 --width 4

# No frames: exit 1 and the message.
rc=0
scripts/frames_to_gif.sh "$work/empty" "$work/none.gif" >/dev/null 2>"$work/empty.err" || rc=$?
if [ "$rc" -eq 1 ] && [ "$(cat "$work/empty.err")" = "frames_to_gif: no frames in $work/empty" ] \
    && [ ! -e "$work/none.gif" ]; then
    ok empty
else
    bad empty; echo "  exit $rc"; cat "$work/empty.err"
fi

# A bad option value: argparse's exit 2 and error line.
rc=0
scripts/frames_to_gif.sh "$work/frames" "$work/x.gif" --fps abc >/dev/null 2>"$work/arg.err" || rc=$?
if [ "$rc" -eq 2 ] && grep -qx "frames_to_gif.sh: error: argument --fps: invalid int value: 'abc'" "$work/arg.err"; then
    ok bad-arg
else
    bad bad-arg; echo "  exit $rc"; cat "$work/arg.err"
fi

echo "frames_to_gif: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
