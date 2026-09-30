#!/usr/bin/env bash
# Issue #801: the headless gfx recorder was missing the flow_gfx_text ABI
# implementation. Records one frame of an "H" drawn with gfx_text and reads
# the pixels back out of the PPM the recorder writes.
source "$(dirname "$0")/lib.sh"

# One RGB pixel of a binary PPM (P6) as "r,g,b".
ppm_pixel() {
    local file="$1" width="$2" x="$3" y="$4" header_end
    # The pixels start one whitespace byte after the first "255".
    header_end="$(LC_ALL=C grep -abo 255 "$file" | awk -F: 'NR == 1 { print $1 }')"
    local off=$((header_end + 3 + 1 + (y * width + x) * 3))
    od -An -tu1 -v -j "$off" -N 3 "$file" | tr -s ' \n' '  ' | awk '{ printf "%s,%s,%s", $1, $2, $3 }'
}

check_record_text() {
    t_need clang
    cat > "$T_TMP/test_gfx_text.flow" <<'FLOW'

import "stdlib/gfx.flow"

export function main() -> i32 {
    let g = gfx_open(320, 240, "test")
    # Draw 'H' in white on black background, scale=1
    gfx_clear(g, 0, 0, 0)
    gfx_text(g, 10, 10, "H", 1, 255, 255, 255)
    gfx_present(g)
    gfx_close(g)
    return 0
}
FLOW
    (cd "$T_TMP" && FLOW_GFX_RECORD_FRAMES=1 FLOW_GFX_RECORD_SKIP=0 \
        "$T_ROOT/flow" record "$T_TMP/test_gfx_text.flow") \
        || { echo "flow record failed"; return 1; }

    local frames
    frames="$(find "$T_TMP/frames" -name 'frame_*.ppm' | wc -l | tr -d ' ')"
    a_eq "$frames" 1 "number of recorded frames"
    local ppm
    ppm="$(find "$T_TMP/frames" -name 'frame_*.ppm')"

    local header
    header="$(head -c 32 "$ppm" | LC_ALL=C tr -c 'P0-9' ' ' | awk '{ print $1, $2, $3, $4 }')"
    a_eq "$header" "P6 320 240 255" "PPM header"

    # The 'H' glyph in 5x7, drawn at (10, 10):
    # rows 0-2 and 4-6: 10001, row 3: 11111.
    a_eq "$(ppm_pixel "$ppm" 320 10 10)" "255,255,255" "top-left of H (lit)"
    a_eq "$(ppm_pixel "$ppm" 320 14 10)" "255,255,255" "top-right of H (lit)"
    a_eq "$(ppm_pixel "$ppm" 320 12 10)" "0,0,0" "top-middle of H (dark)"
    a_eq "$(ppm_pixel "$ppm" 320 10 13)" "255,255,255" "middle-left of H (lit)"
    a_eq "$(ppm_pixel "$ppm" 320 12 13)" "255,255,255" "middle of H (lit)"
    a_eq "$(ppm_pixel "$ppm" 320 14 13)" "255,255,255" "middle-right of H (lit)"
    a_eq "$(ppm_pixel "$ppm" 320 10 16)" "255,255,255" "bottom-left of H (lit)"
    a_eq "$(ppm_pixel "$ppm" 320 14 16)" "255,255,255" "bottom-right of H (lit)"
    a_eq "$(ppm_pixel "$ppm" 320 12 16)" "0,0,0" "bottom-middle of H (dark)"
}

t_check record_text check_record_text
t_done
