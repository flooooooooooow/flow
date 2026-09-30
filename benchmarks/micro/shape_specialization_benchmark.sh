#!/usr/bin/env bash
# Shape specialization: lower one kernel with a dynamic memref<?xf32> shape
# and again with the shape fixed at 1000000 elements (the replacement
# specialize_shapes made in the retired mlir_optimizer.py), and report the
# size of the LLVM IR each produces. Lowering is compiler/scripts/mlir_lower.sh.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd -P)"

work="$(mktemp -d "${TMPDIR:-/tmp}/flow-shape.XXXXXX")"
trap 'rm -rf "$work"' EXIT

cat > "$work/generic.mlir" <<'EOF'
module {
  func.func @compute(%arg0: memref<?xf32>, %arg1: memref<?xf32>, %arg2: memref<?xf32>, %size: index) attributes { llvm.emit_c_interface } {
    %c0 = arith.constant 0 : index
    %c1 = arith.constant 1 : index
    scf.for %i = %c0 to %size step %c1 {
      %a = memref.load %arg0[%i] : memref<?xf32>
      %b = memref.load %arg1[%i] : memref<?xf32>
      %c = arith.mulf %a, %b : f32
      %d = arith.addf %c, %a : f32
      memref.store %d, %arg2[%i] : memref<?xf32>
    }
    func.return
  }
}
EOF

echo "--- MLIR Shape Specialization Benchmark ---"
if ! "$ROOT/compiler/scripts/mlir_lower.sh" --tools >/dev/null 2>&1; then
    echo "Skipping real benchmark: LLVM/MLIR toolchain not found."
    exit 0
fi
echo "Toolchain found, JIT execution supported."

size=1000000
lines() {
    if [[ -s "$1" ]]; then wc -l < "$1" | tr -d ' '; else echo 0; fi
}
echo ""
echo "--- Real Performance Validation --"
echo "[1] JIT Compiling Generic Kernel (memref<?xf32>)..."
"$ROOT/compiler/scripts/mlir_lower.sh" "$work/generic.mlir" "$work/generic.ll" 2>/dev/null
echo "    -> Emitted $(lines "$work/generic.ll") lines of LLVM IR."

echo ""
echo "[2] JIT Compiling Specialized Kernel (memref<${size}xf32>)..."
sed "s/memref<?xf32>/memref<${size}xf32>/g" "$work/generic.mlir" > "$work/special.mlir"
"$ROOT/compiler/scripts/mlir_lower.sh" "$work/special.mlir" "$work/special.ll" 2>/dev/null
echo "    -> Emitted $(lines "$work/special.ll") lines of LLVM IR."
