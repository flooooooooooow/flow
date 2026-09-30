#!/usr/bin/env bash
# End-to-end check of the pure-Flow GIF89a encoder (lib/stdlib/gif.flow).
#
# Compiles and runs examples/graphics/gif_writer.flow, then decodes the GIF it
# produced with scripts/tools/gif_check, a GIF89a reader written in Flow. The
# decode is the ground truth: format, frame count, dimensions, loop metadata,
# and real pixel change between the first and last frame (the animation is
# not a stack of identical frames).
source "$(dirname "$0")/lib.sh"

EXAMPLE="$T_ROOT/examples/graphics/gif_writer.flow"
WIDTH=128
HEIGHT=128
FRAMES=24
DELAY_CS=5

# Build and run the example once, then decode it once. The report lands in
# $T_WORK/report (key=value lines); FIXTURE_ERR says why it could not.
FIXTURE_ERR=""
build_fixture() {
    local td="$T_WORK/gif_demo"
    mkdir -p "$td"
    if ! compiler/scripts/flowc_emit.sh --strict "$EXAMPLE" "$td/gif_writer.c" > "$td/emit.log" 2>&1; then
        FIXTURE_ERR="flowc_emit failed: $(tail -n 5 "$td/emit.log")"
        return
    fi
    [[ -e "$td/gif_writer.c" ]] || { FIXTURE_ERR="no C output"; return; }
    if ! clang -Wno-everything "$td/gif_writer.c" -o "$td/gif_writer" -lm > "$td/cc.log" 2>&1; then
        FIXTURE_ERR="clang failed: $(tail -n 5 "$td/cc.log")"
        return
    fi
    # The example writes build/gif_demo.gif relative to its cwd.
    if ! (cd "$td" && ./gif_writer) > "$td/run.log" 2>&1; then
        FIXTURE_ERR="gif_writer failed: $(cat "$td/run.log")"
        return
    fi
    grep -q bytes "$td/run.log" || { FIXTURE_ERR="gif_writer did not report its size"; return; }
    GIF="$td/build/gif_demo.gif"
    [[ -e "$GIF" ]] || { FIXTURE_ERR="no build/gif_demo.gif"; return; }

    local checker
    if ! checker="$(scripts/tools/build_tool.sh gif_check 2> "$td/tool.log")"; then
        FIXTURE_ERR="could not build gif_check: $(tail -n 5 "$td/tool.log")"
        return
    fi
    # Frame 0 pixel (12, 12) is inside the moving square.
    GIF_CHECK_RC=0
    "$checker" "$GIF" 12 12 > "$T_WORK/report" 2> "$T_WORK/report.err" || GIF_CHECK_RC=$?
}
if command -v clang > /dev/null 2>&1; then
    build_fixture
fi

fixture() {
    t_need clang
    [[ -z "$FIXTURE_ERR" ]] || { echo "$FIXTURE_ERR"; return 1; }
}

field() {
    sed -n "s/^$1=//p" "$T_WORK/report"
}

check_the_full_animation_decodes() {
    fixture
    a_eq "$(field format)" GIF "format"
    a_eq "$(field width)x$(field height)" "${WIDTH}x${HEIGHT}" "size"
    a_eq "$(field frames)" "$FRAMES" "frame count"
    # Every frame must decode to exactly width*height pixels.
    a_eq "$(field decoded)" "$FRAMES" "frames that decode"
    [[ "$GIF_CHECK_RC" -eq 0 ]] || { cat "$T_WORK/report.err"; return 1; }
}

check_loop_and_delay_metadata() {
    fixture
    # NETSCAPE2.0: loop forever.
    a_eq "$(field loop)" 0 "loop count"
    # Pillow reported this as duration 50 ms.
    a_eq "$(field delay_cs)" "$DELAY_CS" "frame delay in centiseconds"
}

check_animation_actually_moves() {
    fixture
    # The encoder writes disposal 1 (keep) and full frames, so each
    # composited frame is the frame itself.
    a_eq "$(field disposal)" 1 "disposal method"
    local differing
    differing="$(field first_last_diff)"
    a_true "some pixels differ between the first and last frame" test "$differing" -gt 0
    # The moving square is 24x24; two disjoint positions differ in exactly
    # 2 * 576 pixels on this fixture.
    a_eq "$differing" 1152 "pixels that differ"
}

check_square_color_survives_quantization() {
    fixture
    # Frame 0 square sits at (8, 8)..(31, 31); fill is (255, 210, 40),
    # nearest 6x7x6 cube entry is (255, 212, 51).
    a_eq "$(field pixel)" "255,212,51" "frame 0 pixel (12, 12)"
}

t_check the_full_animation_decodes check_the_full_animation_decodes
t_check loop_and_delay_metadata check_loop_and_delay_metadata
t_check animation_actually_moves check_animation_actually_moves
t_check square_color_survives_quantization check_square_color_survives_quantization
t_done
