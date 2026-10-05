#!/bin/bash
# Record a demo GIF of a Flow application
# Usage: ./scripts/record_demo_gif.sh [output_name] [duration_seconds]

set -e

OUTPUT_NAME="${1:-tetris_demo}"
DURATION="${2:-10}"
OUTPUT_DIR="docs/assets"
TMP_VIDEO="/tmp/${OUTPUT_NAME}.mov"
OUTPUT_GIF="${OUTPUT_DIR}/${OUTPUT_NAME}.gif"

echo "🎬 Recording ${DURATION}s demo..."
echo "   Press Ctrl+C to stop early"
echo ""

# Record screen using ffmpeg with avfoundation (macOS)
# Device 1 is typically the main display
ffmpeg -y -f avfoundation -framerate 30 -i "1" -t "$DURATION" -vf "scale=640:-1" "$TMP_VIDEO" 2>/dev/null || true

echo ""
echo "🎞️  Converting to GIF..."

# Convert to GIF with good quality palette
ffmpeg -y -i "$TMP_VIDEO" \
    -vf "fps=15,scale=480:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer" \
    "$OUTPUT_GIF" 2>/dev/null

# Cleanup
rm -f "$TMP_VIDEO"

echo "✅ Saved to $OUTPUT_GIF"
ls -lh "$OUTPUT_GIF"
