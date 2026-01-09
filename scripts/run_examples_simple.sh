#!/bin/bash

# Simple FLOW Examples Runner
# Quick and dirty runner for examples

echo "🚀 Running FLOW Examples"
echo "======================="

if [ $# -eq 0 ]; then
    echo "Running all examples..."
    for file in examples/*.flow; do
        if [ -f "$file" ]; then
            echo ""
            echo "📁 $(basename "$file")"
            echo "----------------------------------------"
            ./flow run "$file" 2>&1 | head -20
            echo ""
        fi
    done
else
    echo "Running: $1"
    ./flow run "$1"
fi

echo "✅ Done!"
