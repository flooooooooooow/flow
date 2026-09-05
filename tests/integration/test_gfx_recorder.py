import subprocess
import pytest
import shutil
import os
import glob

@pytest.mark.skipif(not shutil.which("clang"), reason="requires clang")
def test_gfx_record_text(tmp_path):
    """Issue #801: Headless gfx recorder is missing the flow_gfx_text ABI implementation."""
    flow_src = tmp_path / "test_gfx_text.flow"
    flow_src.write_text('''
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
''')
    
    # We just run the flow recorder to verify compilation and linking, and execution.
    env = dict(os.environ)
    env["FLOW_GFX_RECORD_FRAMES"] = "1"
    env["FLOW_GFX_RECORD_SKIP"] = "0"
    
    res = subprocess.run(
        [os.path.abspath("./flow"), "record", str(flow_src)],
        capture_output=True, text=True, env=env, cwd=tmp_path
    )
    assert res.returncode == 0, f"flow record failed:\\n{res.stdout}\\n{res.stderr}"

    frames = list(tmp_path.glob("frames/frame_*.ppm"))
    assert len(frames) == 1, "Expected one frame to be recorded"
    
    # Parse PPM
    ppm = frames[0].read_bytes()
    # Find the header P6 \n width height \n 255 \n
    # Note: \n could be single byte 10. Split by newline properly.
    # The header elements can be separated by spaces or newlines. Let's just find the first 3 tokens.
    tokens = ppm.split()
    assert tokens[0] == b'P6'
    assert tokens[1] == b'320'
    assert tokens[2] == b'240'
    assert tokens[3] == b'255'
    
    # The pixels start exactly after the single whitespace character following 255.
    header_end = ppm.find(b'255') + 3
    # Skip one whitespace char
    pixels = ppm[header_end + 1:]
    
    def get_pixel(x, y):
        idx = (y * 320 + x) * 3
        return pixels[idx], pixels[idx+1], pixels[idx+2]
    
    # Check that 'H' is drawn.
    # The 'H' glyph in 5x7:
    # row 0: 10001 = 17 = x, x+4
    # row 1: 10001
    # row 2: 10001
    # row 3: 11111 = 31 = x..x+4
    # row 4: 10001
    # row 5: 10001
    # row 6: 10001
    # Drawn at (10, 10)
    
    assert get_pixel(10, 10) == (255, 255, 255), "Top-left of H should be lit"
    assert get_pixel(14, 10) == (255, 255, 255), "Top-right of H should be lit"
    assert get_pixel(12, 10) == (0, 0, 0), "Top-middle of H should be dark"
    
    assert get_pixel(10, 13) == (255, 255, 255), "Middle-left of H should be lit"
    assert get_pixel(12, 13) == (255, 255, 255), "Middle of H should be lit"
    assert get_pixel(14, 13) == (255, 255, 255), "Middle-right of H should be lit"

    assert get_pixel(10, 16) == (255, 255, 255), "Bottom-left of H should be lit"
    assert get_pixel(14, 16) == (255, 255, 255), "Bottom-right of H should be lit"
    assert get_pixel(12, 16) == (0, 0, 0), "Bottom-middle of H should be dark"

