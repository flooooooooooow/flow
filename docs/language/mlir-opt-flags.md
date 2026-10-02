# MLIR optimization flags

When compiling with the MLIR backend (`--mlir`), pass `--optimize` to run
`mlir-opt` through Flow's pass pipeline.

## Levels

| Flag | Effect |
|------|--------|
| `--opt-level O0` | No passes |
| `--opt-level O1` | canonicalize, CSE, symbol-dce |
| `--opt-level O2` (default) | O1 + inline, sccp, mem2reg, LICM, affine-loop-fusion |
| `--opt-level O3` | O2 + affine-super-vectorize |

## Toggles

Disable individual passes (level gates still apply):

```
--no-vectorization   # O3 affine-super-vectorize
--no-loop-fusion     # O2+ affine-loop-fusion
--no-mem2reg
--no-sccp
--no-licm
--no-cse             # CSE stand-in for GVN
--no-dce             # symbol-dce + trailing canonicalize
--no-inline
```

Inspect the pipeline without running `mlir-opt`:

```bash
python3 -m flow.transpiler --print-pass-pipeline --opt-level O2 --no-inline
./flow mlir examples/basics/hello_world.flow --optimize --opt-level O3 --no-vectorization
```

`--opt-report` prints pass statistics using the same flag set.

Affine tiling is opt-in and requires a positive tile size:

```bash
./flow mlir-optimize --print-pass-pipeline \
  --enable-affine-tiling --affine-tile-size 8
```

The flag adds `affine-loop-tile{tile-size=8}` to the function pipeline. The
default pipeline remains unchanged.

## Async copy capability gate

Loop pipelining and multi-buffering remain opt-in. The GPU async-region pass
also requires an explicit target capability:

```bash
./flow mlir-optimize --print-pass-pipeline \
  --enable-async-copy --async-copy-target gpu
```

Accepted targets are `gpu`, `nvptx` and `amdgpu`. The target flag adds
`gpu-async-region` to the function pipeline. A CPU pipeline does not acquire
an async-copy pass implicitly. The current gate marks GPU regions async. It
does not synthesize `nvgpu.device_async_copy` operations or claim a hardware
copy engine is available. Those lowerings need target-specific IR and a
profitability check.

The token graph emitter follows the same contract:

```bash
./flow tool scripts/tools/mlir_async/main.flow \
  --stages=3 --buffers=4 --target=nvptx
```

It emits an explicit chain of `async.execute` dependencies and records the
selected target in `flow.async_target`. The emitter rejects a missing or
unknown target. A backend can consume this contract when it supplies a real
async-copy operation and its completion token.

For `nvptx`, the emitter produces `nvgpu.device_async_copy`,
`nvgpu.device_async_create_group`, and `nvgpu.device_async_wait` operations
with `!nvgpu.device.async.token` results. The generic `async.execute` graph
remains available for the other accepted targets. The NVGPU path still needs
target lowering and measured profitability before automatic promotion.

Static scratchpad plans use the same explicit target boundary:

```bash
./flow tool scripts/tools/mlir_static_memory/main.flow \
  --target=nvptx --memory-space=shared
```

The planner records `flow.static_memory_target` and
`flow.static_memory_space` in the module. `shared` requires a GPU-family
target. The current emitter keeps the allocation and offset plan explicit for
the target lowering that consumes it.

## Register tiles

`--register-tiles` enables the opt-in `register_tile_outer_product(a, b)`
intrinsic. For vector operands it emits `vector.outerproduct`, preserving the
tile shape for later AMX, SME, or GPU target selection.

The default lane budget is 256 scalar lanes. Set
`FLOWC_MLIR_REGISTER_TILE_MAX_LANES` to a smaller target budget when a tile
must fit a particular register file.

```bash
./flow mlir compiler/fixtures/mlir/register_tile_probe.flow --register-tiles
```

## Generator-side vectorization

Independently of `--optimize`, the generator rewrites simple elementwise
counted loops itself:

```flow-pseudocode
for i in 0 to n { out[i] = a * x[i] + y[i] }
```

over `f32` or `i32` memref bases becomes a step-4 `scf.for` of
`vector.transfer_read` / `vector.transfer_write` plus a scalar remainder loop,
marked in the IR with `// flow: vectorized elementwise f32 loop (VF=4)`.
Loop-carried accumulators and pointer bases stay scalar.

The lowering pipeline runs `--convert-vector-to-scf` before `--convert-scf-to-cf`
and `--convert-vector-to-llvm` before `--convert-func-to-llvm`; without both,
`vector.transfer_read` reaches `mlir-translate` as an unregistered op.

## Affine loop lowering

Static counted loops can use `affine.for` when the generator is asked to emit
the affine dialect:

```bash
FLOWC_MLIR_AFFINE=1 ./flow flow-to-mlir tests/mlir/affine_loop.flow /tmp/affine.mlir
```

The first slice covers positive constant steps, integer or dynamic bounds, and
bodies with no loop-carried values or control-flow exits. The default remains
`scf.for`. This keeps existing MLIR goldens stable while affine fusion and
tiling are introduced incrementally.

Zero-based loops can use nested affine loops with a requested tile size:

```bash
FLOWC_MLIR_AFFINE=1 FLOWC_MLIR_TILE=4 \
  ./flow flow-to-mlir tests/mlir/affine_loop.flow /tmp/tiled.mlir
```

The inner loop carries the original induction value. The final tile uses an
affine minimum, so dynamic and partial extents remain in the tiled path. Loops
with carried values use the existing lowering.

## Tensor-scalar linalg broadcasts

The MLIR emitter lowers the tensor intrinsics `tensor_scale` and
`tensor_add_scalar` to `linalg.generic`. The scalar operand uses a zero-rank
affine map, so the operation stays a structured broadcast through later
bufferization and fusion passes.

The command golden covers both forms:

```bash
./flow tool tests/mlir_commands/run.flow --only mlir_tensor_scalars
```

## AoSoA storage padding

Set `FLOWC_MLIR_AOSOA_PAD=N` to add `N` storage elements to each field array
created by the opt-in AoSoA lowering. Source-level array extents and indexing
remain unchanged. Values from 1 through 64 are accepted. The default is zero.

```bash
FLOWC_MLIR_AOSOA_PAD=1 ./flow mlir compiler/fixtures/mlir/aosoa_padding.flow --lenient
```

Set `FLOWC_MLIR_AOSOA_SWIZZLE=N` to xor each generated field index with that
index shifted by `log2(N)`. `N` must be a power of two from 2 through 32.
The rewrite applies this only to power-of-two logical extents, which keeps the
mapping within the source array for irregular extents. The default is zero.

> `affine-super-vectorize` and `affine-loop-fusion` still need affine loops,
> which the generator does not emit; they remain soft no-ops.
