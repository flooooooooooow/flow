#!/usr/bin/env bash
# Compare tests/fixtures/wasm/alloc_sum.flow compiled natively through MLIR
# with the same function compiled to wasm32 and run under Node.
#
# The native build lowers the program with `flow flow-to-llvm`
# and links it into a small C caller; the wasm build is `flow wasm32`
# (scripts/wasm32_target.sh), run with runtime/wasm/flow_runtime.mjs. The
# results must agree to 1e-6. Prints one JSON line:
#   {"abs_error": ..., "native_mlir": ..., "source": ..., "wasm32": ...}
#
# alloc_sum uses an unsized array, which the flowc MLIR emitter does not
# cover yet, so both builds currently take the Python MLIR generator
# fallback in `flow flow-to-llvm`.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd -P)"
cd "$ROOT"
SOURCE=tests/fixtures/wasm/alloc_sum.flow

work="$(mktemp -d "${TMPDIR:-/tmp}/flow_wasm_parity_.XXXXXX")"
trap 'rm -rf "$work"' EXIT

./flow flow-to-llvm "$SOURCE" "$work/alloc_sum_native.ll"
cat > "$work/caller.c" <<'C'
#include <stdio.h>
float alloc_sum(void);
int main(void) {
    printf("%.17g\n", (double)alloc_sum());
    return 0;
}
C
clang -O2 -Wno-override-module "$work/caller.c" "$work/alloc_sum_native.ll" -lm -o "$work/native"
native="$("$work/native")"

scripts/wasm32_target.sh "$SOURCE" -o "$work/alloc_sum.wasm" --export alloc_sum -O O2

node --input-type=module -e '
import fs from "node:fs";
import {createFlowWasmRuntime} from "./runtime/wasm/flow_runtime.mjs";
const [wasmPath, source, nativeText] = process.argv.slice(1);
const bytes = fs.readFileSync(wasmPath);
const module = new WebAssembly.Module(bytes);
const runtime = createFlowWasmRuntime();
const instance = await WebAssembly.instantiate(module, runtime.imports);
runtime.attach(instance);
const wasm = Number(instance.exports.alloc_sum());
const native = Number(nativeText);
const err = Math.abs(native - wasm);
// Python float repr: integral values keep ".0".
const repr = (x) => { const s = String(x); return /[.eEn]/.test(s) ? s : s + ".0"; };
if (!(err <= 1e-6)) {
  console.error(`native MLIR result ${repr(native)} != wasm result ${repr(wasm)}`);
  process.exit(1);
}
console.log(`{"abs_error": ${repr(err)}, "native_mlir": ${repr(native)}, "source": ${JSON.stringify(source)}, "wasm32": ${repr(wasm)}}`);
' "$work/alloc_sum.wasm" "$SOURCE" "$native"
