#!/usr/bin/env bash
# Minimal Flow → C → WASM hello (issue #121).
# Uses emcc when present; exits 0 with a skip message otherwise (CI-safe).
#
# Usage (from repo root):
#   ./scripts/build_wasm_hello.sh
#   python3 -m http.server 8765 --directory build/wasm_hello

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

OUT_DIR="build/wasm_hello"
HARNESS="wasm/hello_harness.c"
SRC="$HARNESS"

if ! command -v emcc >/dev/null 2>&1; then
    echo "skip: emcc not found — install Emscripten (emsdk) to build WASM locally"
    echo "  docs: docs/language/wasm.md"
    echo "  hint: source ./emsdk_env.sh from an emsdk install (needs Python ≥ 3.10)"
    exit 0
fi

# Broken Homebrew emscripten (wrong Python) still provides an `emcc` shim —
# probe it and skip cleanly so CI / local runs don't fail hard.
if ! emcc -v >/dev/null 2>&1; then
    echo "skip: emcc present but broken (often brew emscripten + old Python)."
    echo "  Prefer emsdk: https://emscripten.org/docs/getting_started/downloads.html"
    echo "  docs: docs/language/wasm.md"
    exit 0
fi

mkdir -p "$OUT_DIR"

# Default: checked-in harness (prints). Optional: real Flow→C with FLOW_WASM_FROM_FLOW=1.
if [[ "${FLOW_WASM_FROM_FLOW:-0}" == "1" ]] \
    && [[ -x ./flow ]] \
    && [[ -f examples/basics/hello_world.flow ]]; then
    if ./flow compile examples/basics/hello_world.flow >/dev/null 2>&1 \
        && [[ -f build/hello_world.c ]]; then
        SRC="build/hello_world.c"
        echo "using Flow-transpiled C: $SRC"
    else
        echo "warn: Flow transpile failed; falling back to harness" >&2
    fi
fi

if [[ "$SRC" == "$HARNESS" ]]; then
    if [[ ! -f "$HARNESS" ]]; then
        echo "error: missing harness $HARNESS" >&2
        exit 1
    fi
    echo "using checked-in harness: $HARNESS"
fi

echo "emcc → $OUT_DIR/hello.{js,wasm}"
emcc "$SRC" \
    -o "$OUT_DIR/hello.js" \
    -O1 \
    -s WASM=1 \
    -s EXPORTED_FUNCTIONS="['_main']" \
    -s EXPORTED_RUNTIME_METHODS="['ccall','cwrap']" \
    -s MODULARIZE=0

cat > "$OUT_DIR/hello.html" << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Flow WASM hello</title>
  <style>
    body { font-family: ui-monospace, monospace; max-width: 40rem; margin: 2rem auto; padding: 0 1rem; }
    #out { background: #111; color: #9f9; padding: 1rem; min-height: 4rem; white-space: pre-wrap; }
  </style>
</head>
<body>
  <h1>Flow → C → WASM</h1>
  <p>Smoke artifact from <code>scripts/build_wasm_hello.sh</code>.</p>
  <pre id="out">Loading…</pre>
  <script>
    var Module = {
      print: function (t) {
        var el = document.getElementById('out');
        el.textContent = (el.textContent === 'Loading…' ? '' : el.textContent) + t + '\n';
      },
      printErr: function (t) {
        document.getElementById('out').textContent += 'ERR: ' + t + '\n';
      },
      onRuntimeInitialized: function () {
        var el = document.getElementById('out');
        if (el.textContent === 'Loading…') el.textContent = '';
        el.textContent += '(runtime ready; main already ran if auto-run)\n';
      }
    };
  </script>
  <script src="hello.js"></script>
</body>
</html>
EOF

echo "ok: wrote $OUT_DIR/hello.js $OUT_DIR/hello.wasm $OUT_DIR/hello.html"
echo "serve: python3 -m http.server 8765 --directory $OUT_DIR"
echo "open:  http://localhost:8765/hello.html"
