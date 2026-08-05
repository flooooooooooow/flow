#!/usr/bin/env python3
"""
Flow → WebAssembly Compiler

Compiles Flow source code to WebAssembly via C.

Usage:
    python wasm/flow_wasm.py examples/fibonacci.flow -o output/
    python wasm/flow_wasm.py my_program.flow --run
"""

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

# Ensure we can find the flow module
SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from flow.parser import parse_flow_code
from flow.c_generator import flow_to_c


def find_emcc():
    """Find emscripten compiler"""
    # Check emsdk in project directory
    emsdk_emcc = PROJECT_ROOT / "emsdk" / "upstream" / "emscripten" / "emcc"
    if emsdk_emcc.exists():
        return str(emsdk_emcc)
    
    # Check PATH
    import shutil
    emcc = shutil.which("emcc")
    if emcc:
        return emcc
    
    return None


def compile_to_wasm(flow_file: Path, output_dir: Path, run: bool = False):
    """Compile a Flow file to WebAssembly"""
    
    print(f"🔄 Compiling {flow_file.name} to WebAssembly...")
    
    # Step 1: Parse Flow and generate C
    print("  1. Parsing Flow source...")
    with open(flow_file, 'r') as f:
        flow_code = f.read()
    
    try:
        declarations = parse_flow_code(flow_code)
        c_code = flow_to_c(declarations)
    except Exception as e:
        print(f"  ❌ Parse error: {e}")
        return False
    
    # Step 2: Write C file
    output_dir.mkdir(parents=True, exist_ok=True)
    base_name = flow_file.stem
    c_file = output_dir / f"{base_name}.c"
    
    print("  2. Generating C code...")
    with open(c_file, 'w') as f:
        f.write(c_code)
    
    # Step 3: Find emscripten
    emcc = find_emcc()
    if not emcc:
        print("  ❌ Emscripten not found!")
        print("     Install with: cd emsdk && ./emsdk install latest && ./emsdk activate latest")
        print(f"  ✅ Generated C code at: {c_file}")
        return False
    
    # Step 4: Compile to WASM
    print("  3. Compiling to WebAssembly...")
    js_file = output_dir / f"{base_name}.js"
    wasm_file = output_dir / f"{base_name}.wasm"
    
    cmd = [
        emcc, str(c_file),
        "-o", str(js_file),
        "-s", "WASM=1",
        "-s", "EXPORTED_RUNTIME_METHODS=['ccall','cwrap']",
        "-s", "ALLOW_MEMORY_GROWTH=1",
        "-O3"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"  ❌ Compilation failed: {result.stderr[:500]}")
        return False
    
    wasm_size = wasm_file.stat().st_size if wasm_file.exists() else 0
    print(f"  ✅ Generated {wasm_file.name} ({wasm_size} bytes)")
    
    # Step 5: Generate HTML wrapper
    print("  4. Generating HTML wrapper...")
    html_file = output_dir / f"{base_name}.html"
    generate_html(html_file, base_name, flow_code, c_code, wasm_size)
    print(f"  ✅ Generated {html_file.name}")
    
    # Step 6: Optionally run with Node.js
    if run:
        print("\n▶ Running with Node.js...")
        node_result = subprocess.run(["node", str(js_file)], capture_output=True, text=True)
        print(node_result.stdout)
        if node_result.stderr:
            print(f"⚠️  {node_result.stderr}")
    
    print(f"\n🎉 Done! Open {html_file} in a browser to run.")
    return True


def generate_html(html_file: Path, name: str, flow_code: str, c_code: str, wasm_size: int):
    """Generate HTML wrapper for WASM"""
    
    flow_escaped = flow_code.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    c_escaped = c_code.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Flow WASM: {name}</title>
    <style>
        body {{
            font-family: system-ui, sans-serif;
            background: #0d1117;
            color: #e6edf3;
            margin: 0;
            padding: 2rem;
        }}
        h1 {{ color: #ff7b72; text-align: center; }}
        .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin: 2rem 0; }}
        @media (max-width: 800px) {{ .grid {{ grid-template-columns: 1fr; }} }}
        .panel {{
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            overflow: hidden;
        }}
        .panel-header {{
            background: #21262d;
            padding: 0.5rem 1rem;
            font-weight: 600;
            font-size: 0.85rem;
        }}
        .panel-content {{
            padding: 1rem;
            font-family: 'Fira Code', monospace;
            font-size: 13px;
            max-height: 300px;
            overflow: auto;
        }}
        pre {{ margin: 0; white-space: pre-wrap; }}
        .flow {{ color: #a5d6ff; }}
        .c {{ color: #7ee787; }}
        .controls {{ text-align: center; margin: 1rem 0; }}
        button {{
            background: #ff7b72;
            color: #000;
            border: none;
            padding: 0.75rem 2rem;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            margin: 0 0.5rem;
        }}
        button:hover {{ opacity: 0.9; }}
        #output {{
            background: #0a0a0a;
            color: #3fb950;
            min-height: 100px;
        }}
        .info {{ text-align: center; color: #8b949e; font-size: 0.85rem; }}
    </style>
</head>
<body>
    <h1>🔥 Flow → WebAssembly: {name}</h1>
    <p class="info">Real WASM • {wasm_size} bytes</p>
    
    <div class="grid">
        <div class="panel">
            <div class="panel-header">📝 Flow Source</div>
            <div class="panel-content flow"><pre>{flow_escaped}</pre></div>
        </div>
        <div class="panel">
            <div class="panel-header">⚙️ Generated C</div>
            <div class="panel-content c"><pre>{c_escaped}</pre></div>
        </div>
    </div>
    
    <div class="controls">
        <button onclick="runWasm()">▶ Run WASM</button>
        <button onclick="clearOutput()" style="background:#30363d;color:#e6edf3;">Clear</button>
    </div>
    
    <div class="panel">
        <div class="panel-header">📤 Output</div>
        <div class="panel-content" id="output"><pre>Click "Run WASM" to execute...</pre></div>
    </div>
    
    <script src="{name}.js"></script>
    <script>
        let output = [];
        var Module = {{
            onRuntimeInitialized: () => document.querySelector('.info').textContent += ' • ✅ Loaded',
            print: (t) => {{ output.push(t); updateOutput(); }},
            printErr: (t) => {{ output.push('⚠️ ' + t); updateOutput(); }}
        }};
        function updateOutput() {{
            document.getElementById('output').innerHTML = '<pre>' + output.join('\\n') + '</pre>';
        }}
        function runWasm() {{
            output = [];
            const start = performance.now();
            try {{
                const result = Module._main();
                output.push('\\n✅ Exit: ' + result + ' (' + (performance.now()-start).toFixed(1) + 'ms)');
            }} catch(e) {{ output.push('❌ ' + e); }}
            updateOutput();
        }}
        function clearOutput() {{
            output = [];
            document.getElementById('output').innerHTML = '<pre>Click "Run WASM" to execute...</pre>';
        }}
    </script>
</body>
</html>'''
    
    with open(html_file, 'w') as f:
        f.write(html)


def main():
    parser = argparse.ArgumentParser(description="Compile Flow to WebAssembly")
    parser.add_argument("file", help="Flow source file")
    parser.add_argument("-o", "--output", default="wasm_output", help="Output directory")
    parser.add_argument("--run", action="store_true", help="Run with Node.js after compilation")
    
    args = parser.parse_args()
    
    flow_file = Path(args.file)
    if not flow_file.exists():
        print(f"❌ File not found: {flow_file}")
        sys.exit(1)
    
    output_dir = Path(args.output)
    success = compile_to_wasm(flow_file, output_dir, args.run)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
