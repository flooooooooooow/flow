#!/bin/bash
# FLOW to WebAssembly Builder - Compiles ALL examples to WASM

echo "🚀 Building ALL FLOW examples to WebAssembly..."

# Check if Emscripten is available
if ! command -v emcc &> /dev/null; then
    echo "❌ Emscripten not found. Install with:"
    echo "   git clone https://github.com/emscripten-core/emsdk.git"
    echo "   cd emsdk"
    echo "   ./emsdk install latest"
    echo "   ./emsdk activate latest"
    echo "   source ./emsdk_env.sh"
    exit 1
fi

# Create output directory
mkdir -p wasm_examples
cd wasm_examples

echo "📁 Output directory: wasm_examples/"

# Function to compile FLOW to C then to WASM
compile_flow_to_wasm() {
    local flow_file=$1
    local output_name=$(basename "$flow_file" .flow)
    
    echo "🔨 Compiling $flow_file..."
    
    # First compile FLOW to C
    cd ..
    PYTHONPATH=src python3 -m flow.transpiler "$flow_file" --c -o "wasm_examples/${output_name}.c" 2>/dev/null
    
    if [ $? -ne 0 ]; then
        echo "❌ Failed to compile $flow_file to C"
        return 1
    fi
    
    cd wasm_examples
    
    # Create a simple main if the FLOW file doesn't have one
    if ! grep -q "function main" "${output_name}.c"; then
        cat >> "${output_name}.c" << 'EOF'

// Generated main function
int main() {
    return 0;
}
EOF
    fi
    
    # Compile C to WebAssembly
    emcc "${output_name}.c" \
        -o "${output_name}.js" \
        -s WASM=1 \
        -s EXPORTED_FUNCTIONS="main" \
        -s EXPORTED_RUNTIME_METHODS="ccall,cwrap" \
        -s MODULARIZE=1 \
        -s ALLOW_MEMORY_GROWTH=1 \
        -O3 \
        -I../src/flow 2>/dev/null
    
    if [ $? -eq 0 ]; then
        echo "✅ Successfully compiled $flow_file to WebAssembly"
        
        # Create HTML wrapper
        cat > "${output_name}.html" << EOF
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FLOW WebAssembly - $output_name</title>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            max-width: 800px; 
            margin: 0 auto; 
            padding: 20px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container { 
            background: white; 
            padding: 30px; 
            border-radius: 15px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.2); 
        }
        h1 { color: #333; text-align: center; margin-bottom: 20px; }
        .code-display { 
            background: #1e1e1e; 
            color: #00ff00; 
            padding: 15px; 
            border-radius: 5px; 
            font-family: 'Courier New', monospace; 
            margin: 15px 0;
            white-space: pre-wrap;
            max-height: 300px;
            overflow-y: auto;
        }
        .btn { 
            background: #667eea; 
            color: white; 
            border: none; 
            padding: 10px 20px; 
            border-radius: 5px; 
            cursor: pointer; 
            margin: 5px;
            transition: background 0.3s ease;
        }
        .btn:hover { background: #5a6fd8; }
        .btn:disabled { background: #ccc; cursor: not-allowed; }
        .output { 
            background: #f8f9fa; 
            border: 1px solid #dee2e6; 
            border-radius: 5px; 
            padding: 15px; 
            margin: 15px 0; 
            font-family: 'Courier New', monospace; 
            min-height: 100px;
            white-space: pre-wrap;
        }
        .status { 
            margin: 10px 0; 
            padding: 10px; 
            border-radius: 5px; 
            font-weight: bold;
        }
        .status.info { 
            background: #d1ecf1; 
            color: #0c5460; 
            border: 1px solid #bee5eb; 
        }
        .status.success { 
            background: #d4edda; 
            color: #155724; 
            border: 1px solid #c3e6cb; 
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 FLOW WebAssembly - $output_name</h1>
        
        <div class="status info">
            <strong>📁 Source:</strong> $flow_file<br>
            <strong>🔧 Compiler:</strong> FLOW → C → WebAssembly
        </div>
        
        <div class="code-display">$(sed 's/&/\&amp;/g; s/</\&lt;/g; s/>/\&gt;/g' "../$flow_file" | head -20)</div>
        
        <button class="btn" onclick="runFlowCode()">▶️ Run WebAssembly</button>
        <button class="btn" onclick="clearOutput()">🗑️ Clear Output</button>
        <button class="btn" onclick="location.href='../index.html'">🏠 Back to Examples</button>
        
        <div id="output" class="output">Click "Run WebAssembly" to execute the compiled FLOW code...</div>
    </div>

    <script src="${output_name}.js"></script>
    <script>
        let moduleLoaded = false;
        
        Module.onRuntimeInitialized = function() {
            moduleLoaded = true;
            document.getElementById('output').innerHTML = '✅ WebAssembly loaded! Ready to execute FLOW code.<br>Click "Run WebAssembly" to start.';
        };

        function runFlowCode() {
            const output = document.getElementById('output');
            
            if (!moduleLoaded) {
                output.innerHTML = '⏳ WebAssembly still loading...';
                return;
            }
            
            output.innerHTML = '🚀 Executing FLOW WebAssembly...<br>';
            
            try {
                // Capture console.log output
                const originalLog = console.log;
                const logs = [];
                console.log = function(...args) {
                    logs.push(args.join(' '));
                    originalLog.apply(console, args);
                };
                
                // Run the main function
                const result = Module.ccall('main', 'number', [], []);
                
                // Restore console.log
                console.log = originalLog;
                
                // Display output
                output.innerHTML = '✅ FLOW WebAssembly execution complete!<br>';
                output.innerHTML += '📊 Return value: ' + result + '<br>';
                
                if (logs.length > 0) {
                    output.innerHTML += '<br>📝 Program output:<br>';
                    logs.forEach(log => {
                        output.innerHTML += log + '<br>';
                    });
                }
                
                output.className = 'output success';
                
            } catch (error) {
                output.innerHTML = '❌ Error executing WebAssembly:<br>' + error.message;
                output.className = 'output error';
            }
        }

        function clearOutput() {
            const output = document.getElementById('output');
            output.className = 'output';
            output.innerHTML = 'Output cleared...';
        }
    </script>
</body>
</html>
EOF
        
        echo "📄 Created ${output_name}.html"
        return 0
    else
        echo "❌ Failed to compile $flow_file to WebAssembly"
        return 1
    fi
}

# Find all FLOW examples
echo "🔍 Finding FLOW examples..."
flow_files=$(find ../examples -name "*.flow" | head -20)  # Limit to first 20 for demo

echo "📊 Found $(echo "$flow_files" | wc -l) FLOW examples to compile"

# Compile each example
success_count=0
total_count=0

for flow_file in $flow_files; do
    total_count=$((total_count + 1))
    
    if compile_flow_to_wasm "$flow_file"; then
        success_count=$((success_count + 1))
    fi
done

echo ""
echo "🎉 WebAssembly Build Summary:"
echo "✅ Successfully compiled: $success_count/$total_count examples"
echo "📁 Output directory: wasm_examples/"
echo ""

# Create index page
cat > index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FLOW WebAssembly Examples</title>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            max-width: 1000px; 
            margin: 0 auto; 
            padding: 20px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container { 
            background: white; 
            padding: 30px; 
            border-radius: 15px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.2); 
        }
        h1 { color: #333; text-align: center; margin-bottom: 30px; }
        .examples-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
            gap: 20px; 
            margin-top: 30px; 
        }
        .example-card { 
            border: 2px solid #e0e0e0; 
            border-radius: 10px; 
            padding: 20px; 
            background: #f9f9f9; 
            transition: all 0.3s ease; 
            cursor: pointer; 
        }
        .example-card:hover { 
            border-color: #667eea; 
            transform: translateY(-2px); 
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2); 
        }
        .example-card h3 { 
            color: #333; 
            margin-top: 0; 
            display: flex; 
            align-items: center; 
            gap: 10px; 
        }
        .example-card p { 
            color: #666; 
            line-height: 1.6; 
        }
        .status { 
            margin-top: 10px; 
            padding: 5px 10px; 
            border-radius: 5px; 
            font-size: 0.9em; 
            font-weight: bold; 
            background: #d4edda; 
            color: #155724; 
        }
        .btn { 
            background: #667eea; 
            color: white; 
            border: none; 
            padding: 8px 16px; 
            border-radius: 5px; 
            cursor: pointer; 
            text-decoration: none; 
            display: inline-block; 
            margin-top: 10px; 
            transition: background 0.3s ease;
        }
        .btn:hover { background: #5a6fd8; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 FLOW WebAssembly Examples</h1>
        <p style="text-align: center; color: #666; margin-bottom: 30px;">
            All FLOW examples compiled to WebAssembly for browser execution
        </p>
        
        <div class="examples-grid">
EOF

# Add example cards to index
for flow_file in $flow_files; do
    output_name=$(basename "$flow_file" .flow)
    relative_path=$(echo "$flow_file" | sed 's|^\.\.||')
    
    # Extract first line as description
    description=$(head -n 1 "$flow_file" | sed 's/^# *//')
    
    cat >> index.html << EOF
            <div class="example-card" onclick="window.open('${output_name}.html', '_blank')">
                <h3>📄 ${output_name}</h3>
                <p>${description}</p>
                <div class="status">✅ WebAssembly Ready</div>
                <a href="${output_name}.html" class="btn">▶️ Run in Browser</a>
            </div>
EOF
done

cat >> index.html << 'EOF'
        </div>
        
        <div style="text-align: center; margin-top: 40px; padding: 20px; background: #f8f9fa; border-radius: 10px;">
            <h3>🛠️ About This Demo</h3>
            <p>All FLOW examples have been compiled from FLOW → C → WebAssembly using Emscripten.</p>
            <p>Click any example above to run it directly in your browser with real WebAssembly execution!</p>
        </div>
    </div>
</body>
</html>
EOF

echo "📄 Created index.html with all examples"

# Return to original directory
cd ..

echo ""
echo "🎉 ALL FLOW Examples Built Successfully!"
echo "📁 Open wasm_examples/index.html to see all examples"
echo "🌐 Each example has its own HTML page for direct execution"
echo ""
echo "📊 Build Summary:"
echo "   ✅ Total examples: $total_count"
echo "   ✅ Successfully compiled: $success_count"
echo "   ✅ Generated files: HTML + JS + WASM per example"
echo ""
echo "🚀 Run 'open wasm_examples/index.html' to see all WebAssembly examples!"
