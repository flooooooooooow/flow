# FLOW WebAssembly Build System

Compile FLOW programs to WebAssembly for browser execution.

## Quick Start

```bash
# Convert a single file (same as ./flow wasm --legacy FILE)
scripts/flow_to_wasm.sh examples/basics/fibonacci.flow

# Convert the example list
scripts/flow_to_wasm.sh --all

# Open in browser
open wasm/wasm_examples/index.html
```

## Pipeline

```
FLOW Source → C Code → WebAssembly → Browser
     ↓          ↓          ↓           ↓
  Parser    Generator   Emscripten  JavaScript
```

## Requirements

- **A C compiler** (`cc`) - Builds the Stage-A compiler and the converter, a Flow
  program in `scripts/tools/flow_to_wasm`, on first use
- **Emscripten** (optional) - For actual WASM compilation

### Installing Emscripten

```bash
# macOS
brew install emscripten

# Or from source
git clone https://github.com/emscripten-core/emsdk.git
cd emsdk
./emsdk install latest
./emsdk activate latest
source ./emsdk_env.sh
```

## Generated Files

After running the converter:

```
wasm/wasm_examples/
├── index.html          # Gallery of all examples
├── fibonacci.c         # Generated C code
├── fibonacci.html      # Interactive demo page
├── fibonacci.js        # WASM loader (if emscripten available)
├── fibonacci.wasm      # WebAssembly binary (if emscripten available)
└── ...
```

## Without Emscripten

If you don't have Emscripten installed:
- ✅ C code is still generated and verified
- ✅ HTML pages show the FLOW and C code side-by-side
- ⚠️ Browser execution requires Emscripten

## Features Supported

| Feature | Status |
|---------|--------|
| Functions | ✅ |
| Structs | ✅ |
| Control Flow | ✅ |
| For Loops | ✅ |
| While Loops | ✅ |
| Effects System | ✅ |
| Arrays | ✅ |
| SIMD | 🔄 Partial |
| GPU | ❌ Not in WASM |

## File Structure

```
wasm/
├── crossings.sh         # WASM crossing demos (threads, sockets, python, fs, gpu)
├── hello_harness.c      # Minimal emcc smoke harness
├── README.md            # This file
└── wasm_examples/       # Browser gallery (HTML + generated C)
```

## Usage Examples

The converter is `scripts/flow_to_wasm.sh`, a shim over the Flow program
`scripts/tools/flow_to_wasm/main.flow`. Page text lives in
`scripts/tools/flow_to_wasm/assets`. `tests/tools/flow_to_wasm/run.sh` checks
it against goldens recorded from the Python converter it replaced.

### Single File
```bash
scripts/flow_to_wasm.sh examples/basics/hello_world.flow
```

### Custom Output Directory
```bash
scripts/flow_to_wasm.sh examples/basics/fibonacci.flow ./my_output
```

### All Examples
```bash
scripts/flow_to_wasm.sh --all
```

`--all` converts the fixed list `examples/{fibonacci,factorial,gcd,...}.flow`
and writes `wasm/wasm_examples/index.html`, linking every listed page present
in that directory.

## Serving Locally

WebAssembly requires serving over HTTP:

```bash
cd wasm/wasm_examples
python -m http.server 8000
# Open http://localhost:8000
```

## Troubleshooting

### "Emscripten not found"
Install Emscripten or use the generated C files directly.

### WASM won't load in browser
- Check browser console for errors
- Ensure you're serving via HTTP (not file://)
- Try Chrome/Firefox (best WASM support)
