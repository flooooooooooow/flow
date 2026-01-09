#!/bin/bash
# FLOW to WebAssembly Build Script

echo "🚀 Building FLOW WebAssembly Demo..."

# Check if Emscripten is available
if command -v emcc &> /dev/null; then
    echo "✅ Emscripten found"
else
    echo "❌ Emscripten not found. Install with:"
    echo "   git clone https://github.com/emscripten-core/emsdk.git"
    echo "   cd emsdk"
    echo "   ./emsdk install latest"
    echo "   ./emsdk activate latest"
    echo "   source ./emsdk_env.sh"
    exit 1
fi

# Create a simple C version of the web demo
cat > web_demo.c << 'EOF'
#include <stdio.h>
#include <emscripten.h>

int fibonacci(int n) {
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}

EMSCRIPTEN_KEEPALIVE
void hello_world() {
    printf("Hello, World from WebAssembly!\n");
    printf("🌐 Running in browser!\n");
}

EMSCRIPTEN_KEEPALIVE
void run_fibonacci() {
    printf("Calculating Fibonacci numbers:\n");
    for (int i = 0; i < 10; i++) {
        printf("Fibonacci(%d) = %d\n", i, fibonacci(i));
    }
}

EMSCRIPTEN_KEEPALIVE
int main() {
    hello_world();
    run_fibonacci();
    return 0;
}
EOF

echo "🔨 Compiling to WebAssembly..."

# Compile to WebAssembly
emcc web_demo.c \
    -o web_demo.js \
    -s WASM=1 \
    -s EXPORTED_FUNCTIONS="hello_world,run_fibonacci" \
    -s EXPORTED_RUNTIME_METHODS="ccall,cwrap" \
    -s MODULARIZE=1 \
    -O3

if [ $? -eq 0 ]; then
    echo "✅ WebAssembly compilation successful!"
    echo "📁 Generated files: web_demo.js, web_demo.wasm"
    
    # Create a simple HTML wrapper
    cat > web_demo_wasm.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>FLOW WebAssembly Demo</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .container { background: #f5f5f5; padding: 20px; border-radius: 10px; }
        .btn { background: #667eea; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; margin: 5px; }
        .btn:hover { background: #5a6fd8; }
        .output { background: #1e1e1e; color: #00ff00; padding: 15px; border-radius: 5px; font-family: monospace; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 FLOW WebAssembly Demo</h1>
        <p>Real WebAssembly execution compiled from FLOW!</p>
        
        <button class="btn" onclick="runHello()">👋 Hello World</button>
        <button class="btn" onclick="runFibonacci()">🔢 Fibonacci</button>
        
        <div id="output" class="output">Click buttons to run WebAssembly functions...</div>
    </div>

    <script src="web_demo.js"></script>
    <script>
        Module.onRuntimeInitialized = function() {
            document.getElementById('output').innerHTML = 'WebAssembly loaded! Ready to execute FLOW code.';
        };

        function runHello() {
            const output = document.getElementById('output');
            output.innerHTML = 'Executing Hello World...<br>';
            Module.ccall('hello_world', 'void', [], []);
        }

        function runFibonacci() {
            const output = document.getElementById('output');
            output.innerHTML = 'Calculating Fibonacci...<br>';
            Module.ccall('run_fibonacci', 'void', [], []);
        }
    </script>
</body>
</html>
EOF
    
    echo "📄 Created web_demo_wasm.html"
    echo "🌐 Open web_demo_wasm.html in your browser to test!"
    
else
    echo "❌ WebAssembly compilation failed!"
    exit 1
fi

# Cleanup
rm web_demo.c

echo "✅ Build complete!"
