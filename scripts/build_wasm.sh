#!/bin/bash

# FLOW WebAssembly Build Script
# Compiles FLOW programs to WebAssembly for browser execution
# Run from project root: ./scripts/build_wasm.sh

set -e

# Get project root (parent of scripts/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo "🌐 FLOW WebAssembly Build Script"
echo "================================="

# Check dependencies
if ! command -v emcc &> /dev/null; then
    echo "❌ Emscripten not found. Please install Emscripten SDK:"
    echo "   git clone https://github.com/emscripten-core/emsdk.git"
    echo "   cd emsdk"
    echo "   ./emsdk install latest"
    echo "   ./emsdk activate latest"
    echo "   source ./emsdk_env.sh"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found"
    exit 1
fi

# Create build directory
mkdir -p build/wasm

# Function to compile FLOW to WebAssembly
build_wasm() {
    local flow_file=$1
    local output_name=$(basename "$flow_file" .flow)
    
    echo "🔨 Building $flow_file..."
    
    # Step 1: Compile FLOW to C
    python3 ./flow compile "$flow_file"
    if [ ! -f "build/${output_name}.c" ]; then
        echo "❌ Failed to compile $flow_file to C"
        return 1
    fi
    
    # Step 2: Compile C to WebAssembly
    echo "📦 Compiling to WebAssembly..."
    emcc "build/${output_name}.c" \
         -o "build/wasm/${output_name}.js" \
         --shell-file "templates/web_template.html" \
         -s WASM=1 \
         -s EXPORTED_FUNCTIONS="['_main']" \
         -s EXPORTED_RUNTIME_METHODS="['ccall', 'cwrap']" \
         -s NO_EXIT_RUNTIME=1 \
         -s "EXTRA_EXPORTED_RUNTIME_METHODS=['ccall', 'cwrap']" \
         -O3
    
    if [ $? -eq 0 ]; then
        echo "✅ Successfully built $output_name"
        echo "   📁 build/wasm/${output_name}.html"
        echo "   📁 build/wasm/${output_name}.js"
        echo "   📁 build/wasm/${output_name}.wasm"
    else
        echo "❌ Failed to build $output_name"
        return 1
    fi
}

# Create HTML template if it doesn't exist
mkdir -p templates
if [ ! -f "templates/web_template.html" ]; then
    echo "📝 Creating HTML template..."
    cat > templates/web_template.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FLOW WebAssembly Demo</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .controls {
            text-align: center;
            margin: 20px 0;
        }
        button {
            background: #007bff;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            margin: 0 10px;
            transition: background 0.3s;
        }
        button:hover {
            background: #0056b3;
        }
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        #output {
            background: #1e1e1e;
            color: #00ff00;
            padding: 20px;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            line-height: 1.4;
            white-space: pre-wrap;
            min-height: 200px;
            max-height: 400px;
            overflow-y: auto;
            margin-top: 20px;
        }
        .status {
            text-align: center;
            margin: 10px 0;
            font-weight: bold;
        }
        .loading {
            color: #666;
        }
        .success {
            color: #28a745;
        }
        .error {
            color: #dc3545;
        }
        .info {
            background: #e7f3ff;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            border-left: 4px solid #007bff;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌐 FLOW WebAssembly Demo</h1>
        
        <div class="info">
            <strong>About:</strong> This demo runs FLOW code compiled to WebAssembly directly in your browser.
            The code executes at near-native speed without requiring a server.
        </div>
        
        <div class="controls">
            <button id="runBtn" onclick="runDemo()">🚀 Run Demo</button>
            <button onclick="clearOutput()">🗑️ Clear Output</button>
        </div>
        
        <div id="status" class="status loading">Ready to run...</div>
        
        <div id="output"></div>
    </div>

    <script>
        let moduleLoaded = false;
        const runBtn = document.getElementById('runBtn');
        const statusDiv = document.getElementById('status');
        const outputDiv = document.getElementById('output');

        function updateStatus(message, type = 'loading') {
            statusDiv.textContent = message;
            statusDiv.className = 'status ' + type;
        }

        function appendOutput(text) {
            outputDiv.textContent += text;
            outputDiv.scrollTop = outputDiv.scrollHeight;
        }

        function clearOutput() {
            outputDiv.textContent = '';
        }

        async function runDemo() {
            if (!moduleLoaded) {
                runBtn.disabled = true;
                updateStatus('Loading WebAssembly module...', 'loading');
                
                try {
                    // Wait for module to load (handled by Emscripten)
                    await new Promise(resolve => {
                        if (typeof Module !== 'undefined' && Module.calledRun) {
                            resolve();
                        } else {
                            Module.onRuntimeInitialized = resolve;
                        }
                    });
                    moduleLoaded = true;
                } catch (error) {
                    updateStatus('Failed to load WebAssembly module', 'error');
                    console.error('Module loading error:', error);
                    runBtn.disabled = false;
                    return;
                }
            }

            runBtn.disabled = true;
            updateStatus('Running FLOW program...', 'success');
            clearOutput();

            try {
                // Clear any previous output
                outputDiv.textContent = '';
                
                // Run the main function
                const result = Module._main();
                
                appendOutput('\n✅ Program completed with exit code: ' + result);
                updateStatus('Program completed successfully!', 'success');
            } catch (error) {
                appendOutput('\n❌ Error: ' + error.message);
                updateStatus('Program execution failed', 'error');
                console.error('Runtime error:', error);
            } finally {
                runBtn.disabled = false;
            }
        }

        // Override print function to capture FLOW output
        Module = {
            print: function(text) {
                appendOutput(text);
            },
            printErr: function(text) {
                appendOutput('ERROR: ' + text);
            },
            onRuntimeInitialized: function() {
                moduleLoaded = true;
                updateStatus('WebAssembly module loaded successfully!', 'success');
            }
        };
    </script>
    {{{ SCRIPT }}}
</body>
</html>
EOF
fi

# Build specific examples if provided
if [ $# -gt 0 ]; then
    for file in "$@"; do
        if [ -f "$file" ]; then
            build_wasm "$file"
        else
            echo "❌ File not found: $file"
        fi
    done
else
    echo "📦 Building WebAssembly examples..."
    
    # Build web demo
    if [ -f "examples/web_demo.flow" ]; then
        build_wasm "examples/web_demo.flow"
    fi
    
    # Build calculator demo
    if [ -f "examples/calculator.flow" ]; then
        build_wasm "examples/calculator.flow"
    fi
    
    # Build other small examples
    for example in examples/simple_*.flow; do
        if [ -f "$example" ]; then
            build_wasm "$example"
        fi
    done
fi

echo ""
echo "🎉 WebAssembly build complete!"
echo ""
echo "📁 To run the demos:"
echo "   1. Start a local web server:"
echo "      python3 -m http.server 8000"
echo "   2. Open in browser:"
echo "      http://localhost:8000/build/wasm/web_demo.html"
echo ""
echo "🔧 Development server with auto-reload:"
echo "   python3 -m http.server 8000 --directory build/wasm"
EOF
chmod +x build_wasm.sh
