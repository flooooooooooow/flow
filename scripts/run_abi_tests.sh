#!/bin/sh
set -eu

echo "Compiling ABI smoke tests..."
clang -c tests/abi/renderer_abi_smoke.c -o /tmp/renderer_abi_smoke.o
clang -c tests/abi/vulkan_renderer_smoke.c -o /tmp/vulkan_renderer_smoke.o
echo "OK"
