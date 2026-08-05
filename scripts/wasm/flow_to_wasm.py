#!/usr/bin/env python3
"""
FLOW to WebAssembly Converter
Converts FLOW code to WebAssembly-ready C and HTML

Run from project root: python scripts/wasm/flow_to_wasm.py examples/fibonacci.flow
"""

import sys
import os
import subprocess
from pathlib import Path

# Ensure we can find the flow module
SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))


class FlowToWasmConverter:
    def __init__(self):
        self.project_root = PROJECT_ROOT
    
    def convert_file(self, flow_file_path, output_dir=None):
        """Convert a FLOW file to WebAssembly-ready C"""
        flow_file = Path(flow_file_path).absolute()
        
        # Default output to scripts/wasm/wasm_examples
        if output_dir is None:
            output_path = self.project_root / "wasm" / "wasm_examples"
        else:
            output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        output_name = flow_file.stem
        
        print(f"🔨 Converting {flow_file.name} to WebAssembly...")
        
        try:
            # Step 1: Compile FLOW to C
            c_code = self.flow_to_c(flow_file)
            if not c_code:
                return False
            
            # Step 2: Write C file
            c_file = output_path / f"{output_name}.c"
            with open(c_file, 'w') as f:
                f.write(c_code)
            print(f"📝 Generated: {c_file}")
            
            # Step 3: Try to compile to WASM (optional - requires emscripten)
            wasm_success = self.compile_wasm(c_file, output_path, output_name)
            
            # Step 4: Generate HTML wrapper
            self.generate_html(output_name, output_path, flow_file, c_code, wasm_success)
            
            print(f"✅ Successfully converted {flow_file.name}")
            return True
            
        except Exception as e:
            print(f"❌ Error converting {flow_file.name}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def flow_to_c(self, flow_file):
        """Compile FLOW to C using the transpiler"""
        try:
            from flow.parser import parse_flow_code
            from flow.c_generator import flow_to_c
            
            with open(flow_file, 'r') as f:
                code = f.read()
            
            declarations = parse_flow_code(code)
            c_code = flow_to_c(declarations)
            return c_code
            
        except Exception as e:
            print(f"Error compiling FLOW to C: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def compile_wasm(self, c_file, output_path, output_name):
        """Try to compile C to WASM using emscripten"""
        try:
            # Check if emscripten is available
            result = subprocess.run(["emcc", "--version"], capture_output=True)
            if result.returncode != 0:
                print("⚠️  Emscripten not found - C file generated, WASM skipped")
                return False
            
            print("🔧 Compiling to WebAssembly...")
            result = subprocess.run([
                "emcc", str(c_file),
                "-o", str(output_path / f"{output_name}.js"),
                "-s", "WASM=1",
                "-s", "EXPORTED_FUNCTIONS=['_main']",
                "-s", "EXPORTED_RUNTIME_METHODS=['ccall','cwrap']",
                "-s", "ALLOW_MEMORY_GROWTH=1",
                "-O3"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"🎯 Generated: {output_path / f'{output_name}.wasm'}")
                return True
            else:
                print(f"⚠️  WASM compilation failed: {result.stderr[:200]}")
                return False
                
        except FileNotFoundError:
            print("⚠️  Emscripten not installed - C file only")
            return False
    
    def generate_html(self, output_name, output_path, flow_file, c_code, has_wasm):
        """Generate HTML wrapper"""
        
        # Read FLOW source
        try:
            with open(flow_file, 'r') as f:
                flow_code = f.read()
        except:
            flow_code = "// Could not read source"
        
        # Escape for HTML
        flow_escaped = flow_code.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        c_escaped = c_code.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        if has_wasm:
            script_section = f'''<script src="{output_name}.js"></script>
    <script>
        var Module = {{
            onRuntimeInitialized: function() {{
                document.getElementById('status').textContent = '✅ WebAssembly loaded!';
                document.getElementById('runBtn').disabled = false;
            }},
            print: function(text) {{
                document.getElementById('output').textContent += text + '\\n';
            }},
            printErr: function(text) {{
                document.getElementById('output').textContent += 'ERROR: ' + text + '\\n';
            }}
        }};
        
        function runCode() {{
            document.getElementById('output').textContent = '';
            try {{
                var result = Module._main();
                document.getElementById('output').textContent += '\\n✅ Exit code: ' + result;
            }} catch(e) {{
                document.getElementById('output').textContent += '\\n❌ Error: ' + e;
            }}
        }}
    </script>'''
        else:
            script_section = '''<script>
        document.getElementById('status').textContent = '⚠️ WASM not available - showing generated C code';
        document.getElementById('runBtn').style.display = 'none';
        document.getElementById('output').textContent = 'Install Emscripten to compile and run in browser:\\n\\n' +
            'brew install emscripten\\n' +
            '# or\\n' +
            'git clone https://github.com/emscripten-core/emsdk.git third_party/emsdk\\n' +
            'cd third_party/emsdk && ./emsdk install latest && ./emsdk activate latest';
    </script>'''
        
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FLOW → WASM: {output_name}</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{ 
            font-family: system-ui, -apple-system, sans-serif;
            margin: 0; padding: 20px;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh; color: #eee;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ text-align: center; color: #00d4ff; margin-bottom: 30px; }}
        .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }}
        @media (max-width: 800px) {{ .grid {{ grid-template-columns: 1fr; }} }}
        .panel {{ 
            background: #0f0f23; border-radius: 12px; 
            border: 1px solid #333; overflow: hidden;
        }}
        .panel-header {{ 
            background: #1a1a3e; padding: 12px 16px;
            font-weight: 600; color: #00d4ff;
            border-bottom: 1px solid #333;
        }}
        .panel-content {{ 
            padding: 16px; font-family: 'Fira Code', monospace;
            font-size: 13px; line-height: 1.5;
            max-height: 400px; overflow: auto;
            white-space: pre-wrap; color: #a0ffa0;
        }}
        .c-code {{ color: #87ceeb; }}
        #output {{ 
            background: #0a0a1a; min-height: 150px;
            color: #0f0; font-family: monospace;
        }}
        .controls {{ text-align: center; margin: 20px 0; }}
        button {{ 
            background: #00d4ff; color: #000; border: none;
            padding: 12px 32px; border-radius: 8px;
            font-size: 16px; font-weight: 600;
            cursor: pointer; margin: 0 8px;
            transition: all 0.2s;
        }}
        button:hover {{ background: #00fff7; transform: translateY(-2px); }}
        button:disabled {{ background: #555; color: #888; cursor: not-allowed; transform: none; }}
        #status {{ text-align: center; margin: 15px 0; font-size: 14px; color: #888; }}
        .badge {{ 
            display: inline-block; padding: 4px 12px; 
            border-radius: 20px; font-size: 12px;
            background: #00d4ff22; color: #00d4ff;
            margin-left: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 FLOW → WebAssembly <span class="badge">{output_name}</span></h1>
        
        <div class="grid">
            <div class="panel">
                <div class="panel-header">📝 FLOW Source</div>
                <div class="panel-content">{flow_escaped}</div>
            </div>
            <div class="panel">
                <div class="panel-header">⚙️ Generated C</div>
                <div class="panel-content c-code">{c_escaped}</div>
            </div>
        </div>
        
        <div class="controls">
            <button id="runBtn" onclick="runCode()" disabled>▶️ Run WebAssembly</button>
            <button onclick="document.getElementById('output').textContent=''">🗑️ Clear</button>
        </div>
        
        <div id="status">Loading...</div>
        
        <div class="panel">
            <div class="panel-header">📤 Output</div>
            <div class="panel-content" id="output">Waiting for execution...</div>
        </div>
    </div>
    
    {script_section}
</body>
</html>'''
        
        html_file = output_path / f"{output_name}.html"
        with open(html_file, 'w') as f:
            f.write(html)
        print(f"📄 Generated: {html_file}")


def build_all_examples():
    """Build all examples in the examples directory"""
    converter = FlowToWasmConverter()
    examples_dir = PROJECT_ROOT / "examples"
    
    # Simple examples that should work well
    priority_examples = [
        "fibonacci.flow",
        "factorial.flow", 
        "gcd.flow",
        "hello_world.flow",
        "loops.flow",
        "power.flow",
        "palindrome.flow",
        "bubble_sort.flow",
        "simple_search.flow",
        "effects_working.flow",
    ]
    
    success_count = 0
    fail_count = 0
    
    for example in priority_examples:
        example_path = examples_dir / example
        if example_path.exists():
            if converter.convert_file(example_path):
                success_count += 1
            else:
                fail_count += 1
    
    print(f"\n{'='*50}")
    print(f"✅ Converted: {success_count}")
    print(f"❌ Failed: {fail_count}")
    
    # Generate index
    generate_index(converter.project_root / "wasm" / "wasm_examples", priority_examples)


def generate_index(output_dir, examples):
    """Generate index.html for all examples"""
    links = []
    for ex in examples:
        name = ex.replace('.flow', '')
        if (output_dir / f"{name}.html").exists():
            links.append(f'<a href="{name}.html" class="example-card"><span class="icon">📄</span>{name}</a>')
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FLOW WebAssembly Examples</title>
    <style>
        body {{ 
            font-family: system-ui, sans-serif; margin: 0; padding: 40px;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh; color: #eee;
        }}
        h1 {{ text-align: center; color: #00d4ff; }}
        .subtitle {{ text-align: center; color: #888; margin-bottom: 40px; }}
        .grid {{ 
            display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 20px; max-width: 1000px; margin: 0 auto;
        }}
        .example-card {{
            background: #0f0f23; padding: 20px; border-radius: 12px;
            text-decoration: none; color: #eee; text-align: center;
            border: 1px solid #333; transition: all 0.2s;
        }}
        .example-card:hover {{ 
            border-color: #00d4ff; transform: translateY(-4px);
            box-shadow: 0 8px 20px rgba(0, 212, 255, 0.2);
        }}
        .icon {{ font-size: 2em; display: block; margin-bottom: 10px; }}
    </style>
</head>
<body>
    <h1>🚀 FLOW WebAssembly Examples</h1>
    <p class="subtitle">Click any example to see FLOW compiled to WebAssembly</p>
    <div class="grid">
        {chr(10).join(links)}
    </div>
</body>
</html>'''
    
    with open(output_dir / "index.html", 'w') as f:
        f.write(html)
    print(f"📄 Generated: {output_dir / 'index.html'}")


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python scripts/wasm/flow_to_wasm.py <flow_file>     # Convert single file")
        print("  python scripts/wasm/flow_to_wasm.py --all           # Convert all examples")
        print("")
        print("Example:")
        print("  python scripts/wasm/flow_to_wasm.py examples/fibonacci.flow")
        sys.exit(1)
    
    if sys.argv[1] == "--all":
        build_all_examples()
    else:
        flow_file = sys.argv[1]
        output_dir = sys.argv[2] if len(sys.argv) > 2 else None
        
        if not os.path.exists(flow_file):
            print(f"❌ File not found: {flow_file}")
            sys.exit(1)
        
        converter = FlowToWasmConverter()
        success = converter.convert_file(flow_file, output_dir)
        
        if success:
            print(f"\n🎉 Done! Open the HTML file in your browser.")
        else:
            sys.exit(1)


if __name__ == "__main__":
    main()
