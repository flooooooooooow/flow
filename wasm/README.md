# 🚀 FLOW WebAssembly Build System

Compile FLOW programs to WebAssembly for browser execution.

## Quick Start

```bash
# Convert a single file
python wasm/flow_to_wasm.py examples/fibonacci.flow

# Convert all examples
python wasm/flow_to_wasm.py --all

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

- **Python 3.8+** - For the converter script
- **Clang** - For C code verification
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
├── flow_to_wasm.py      # Main converter script
├── wasm_build_system.py # Batch build system
├── demo_wasm_build.py   # Demo builder
├── README.md            # This file
├── wasm_demo/           # Pre-built demos
└── wasm_examples/       # Generated examples
```

## Usage Examples

### Single File
```bash
python wasm/flow_to_wasm.py examples/effects_working.flow
```

### Custom Output Directory
```bash
python wasm/flow_to_wasm.py examples/fibonacci.flow ./my_output
```

### All Examples
```bash
python wasm/flow_to_wasm.py --all
```

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

### "Module not found: flow"
Run from project root: `python wasm/flow_to_wasm.py ...`

### WASM won't load in browser
- Check browser console for errors
- Ensure you're serving via HTTP (not file://)
- Try Chrome/Firefox (best WASM support)
