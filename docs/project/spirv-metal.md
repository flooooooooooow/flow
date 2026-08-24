# SPIR-V to Metal

Flow's MLIR GPU path now treats SPIR-V as the shared portable GPU artifact rather than as a Vulkan-only output.

The pipeline is:

```text
Flow @gpu
  -> MLIR GPU dialect
  -> SPIR-V
     -> Vulkan
     -> SPIRV-Cross -> Metal Shading Language
                    -> xcrun metal -> AIR
                    -> xcrun metallib -> .metallib
```

This keeps Vulkan and Metal behind the same MLIR/SPIR-V lowering. The existing direct AST-to-MSL backend remains available while this path matures, but new MLIR GPU work should prefer the shared SPIR-V route so backend semantics do not drift independently.

## Tooling

SPIR-V emission requires `mlir-opt` and `mlir-translate`. Metal source generation additionally requires `spirv-cross`. Native `.metallib` generation requires the Xcode command-line tools and `xcrun`.

Tool locations can be overridden with `MLIR_OPT`, `MLIR_TRANSLATE`, `SPIRV_CROSS`, `XCRUN`, or `LLVM_PATH` for the MLIR tools. Homebrew LLVM and SPIRV-Cross installations are detected automatically when possible.

## Driver

Compile a Flow GPU source directly to a native Metal library:

```bash
python3 scripts/compile_spirv_metal.py examples/gpu/flow_gpu_vector_add.flow
```

Emit MSL instead:

```bash
python3 scripts/compile_spirv_metal.py \
  examples/gpu/flow_gpu_vector_add.flow \
  --msl-only \
  -o build/vector_add.metal
```

The driver also accepts an existing `.spv` binary:

```bash
python3 scripts/compile_spirv_metal.py kernel.spv -o build/kernel.metallib
```

Additional SPIRV-Cross options can be forwarded with repeated `--spirv-cross-arg` arguments. For example, `--spirv-cross-arg=--msl-version --spirv-cross-arg=23000` requests MSL 2.3.

## Python API

`MLIRSPIRVCompiler` exposes four relevant stages:

```python
compiler.compile_mlir_to_spirv(mlir, "kernel.spv")
compiler.compile_spirv_to_msl("kernel.spv", "kernel.metal")
compiler.compile_mlir_to_msl(mlir, "kernel.metal")
compiler.compile_mlir_to_metallib(mlir, "kernel.metallib")
```

Keeping each stage callable independently makes it possible to cache SPIR-V, inspect generated MSL, use Vulkan directly, or produce native Metal libraries from the same compiler artifact.
