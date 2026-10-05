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

Tensor-valued function boundaries keep value semantics in the emitted MLIR:
elementwise results use a fresh `tensor.empty` destination before One-Shot
Bufferization lowers the boundary to memrefs. The boundary regression checks
the destination form and both calls in `tests/scripts/mlir_bufferize_boundary.flow`.

The Flow-native `scripts/tools/mlir_tune/main.flow` schedule generator also
supports loop interchange for three-dimensional structured operations:

```
./flow tool scripts/tools/mlir_tune/main.flow \
  --strategy=interchange --permutation=1,2,0
```

The permutation must contain each loop position from 0 through 2 once.

Use `--strategy=fuse` with `--fuse-with=` to generate a structured producer
fusion schedule:

```
./flow tool scripts/tools/mlir_tune/main.flow \
  --strategy=fuse --op=linalg.matmul --fuse-with=linalg.generic
```

`--strategy=hierarchical_tile` emits an outer tile followed by an inner tile.
Set the outer schedule with `--tiles=` and the inner schedule with
`--inner-tiles=`. The default inner schedule is `8,8,8`.

`--strategy=hierarchical_vector` emits the same outer tile and vectorizes the
inner tile. This keeps the cache-sized outer schedule separate from the
register-sized vector schedule:

```bash
./flow tool scripts/tools/mlir_tune/main.flow \
  --strategy=hierarchical_vector --tiles=64,64,64 --inner-tiles=8,8,4
```

Affine tiling is opt-in and requires a positive tile size:

```bash
./flow mlir-optimize --print-pass-pipeline \
  --enable-affine-tiling --affine-tile-size 8
```

The flag adds `affine-loop-tile{tile-size=8}` to the function pipeline. The
default pipeline remains unchanged.

Use `--enable-affine-unroll-jam --affine-unroll-jam-factor N` to apply affine
unroll-and-jam with an explicit factor. The transform is opt-in and requires a
positive factor.

Use `--enable-affine-coalescing` to coalesce compatible nested affine loops.

Use `--enable-affine-skewing --affine-skew-factor=N` to add the opt-in
`affine-loop-skew` pass. The factor must be a positive integer.
The pass is opt-in and runs inside the function pipeline.

Use `--enable-affine-parallelize` to add the opt-in `affine-parallelize` pass.
It converts eligible affine loops to one-dimensional `affine.parallel` loops.
The pass stays opt-in because dependence analysis determines which loops are
safe to parallelize.

Use `--enable-affine-tiling --affine-tile-sizes 64,32,8` for hierarchical
tiling. Two through four positive sizes up to 4096 are accepted. The matching
affine tiling passes are emitted in the listed order.

## Async copy capability gate

Loop pipelining and multi-buffering remain opt-in. Multi-buffering defaults to
two buffers. Set `--multi-buffering-factor N` for a multiplier from 2 through
8. The GPU async-region pass
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

It emits an explicit slot dependency graph and allocates one
source and destination pair per circular buffer slot. Stages reuse the pair
for `stage % buffers`. A stage waits for the previous stage that used its
slot, so independent slots can overlap. The module records the selected target in
`flow.async_target`. The module also records
`flow.async_buffer_slots`, `flow.async_stage_count`, and
`flow.async_schedule = "circular"`. Each stage carries an
`async.buffer_slot` comment whose value is `stage % buffers`. A backend can
consume this contract when it supplies a real async-copy operation and its
completion token.

For `nvptx`, the emitter produces `nvgpu.device_async_copy`,
`nvgpu.device_async_create_group`, and `nvgpu.device_async_wait` operations
with `!nvgpu.device.async.token` results. The generic `async.execute` graph
remains available for the other accepted targets and carries a `memref.copy`
from global memory into address space 3 inside each async region. The NVGPU
path still needs target lowering and measured profitability before automatic
promotion.

Static scratchpad plans use the same explicit target boundary:

```bash
./flow tool scripts/tools/mlir_static_memory/main.flow \
  --target=nvptx --memory-space=shared
```

The planner records `flow.static_memory_target` and
`flow.static_memory_space` in the module. `shared` requires a GPU-family
target. It also records `flow.static_arena_alignment`, the byte alignment used
for the arena and every planned view. The current emitter keeps the allocation
and offset plan explicit for the target lowering that consumes it.

Pass `--alignment=N` to choose a power-of-two arena alignment from 1 through
4096 bytes. The selected value is applied to every planned buffer and recorded
as `flow.static_arena_alignment`.

The module also records `flow.static_buffer_lifetimes` as comma-separated
`start:end` operation ranges and `flow.static_buffer_offsets` as comma-separated
arena offsets. It records `flow.static_buffer_interference` as comma-separated
`i:j` pairs for buffers whose live ranges overlap. All lists use the planner's
buffer order.

## Register tiles

`--register-tiles` enables the opt-in `register_tile_outer_product(a, b)`
intrinsic. For vector operands it emits `vector.outerproduct`, preserving the
tile shape for later AMX, SME, or GPU target selection.

The default lane budget is 256 scalar lanes. Set
`FLOWC_MLIR_REGISTER_TILE_MAX_LANES` to a smaller target budget when a tile
must fit a particular register file. The emitter records both
`flow.register_tile_lanes` and `flow.register_tile_max_lanes` beside each
outer-product operation for downstream register-pressure analysis.

Set `FLOWC_MLIR_REGISTER_TILE_TARGET` to `amx`, `sme`, or `nvvm` to attach the
hardware selection metadata used by a later target lowering. The emitter also
records the target intrinsic family: `amx.tile_mulf`, `arm_sme.outerproduct`,
or `nvvm.wgmma`. The default is `generic`, which keeps
`vector.outerproduct`.

The same selection is available on the command line with
`--register-tile-target=TARGET` and `--register-tile-max-lanes=N`.

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
the affine dialect. `flow flow-to-mlir` and `flow mlir` accept `--affine`:

```bash
./flow flow-to-mlir --affine tests/mlir/affine_loop.flow /tmp/affine.mlir
./flow mlir --affine tests/mlir/affine_loop.flow
```

The first slice covers positive constant steps, integer or dynamic bounds, and
bodies with no loop-carried values or control-flow exits. The default remains
`scf.for`. This keeps existing MLIR goldens stable while affine fusion and
tiling are introduced incrementally.

Zero-based loops can use nested affine loops with `--tile-size` (inner tile,
2 through 64) and `--tile-l2-size` (outer tile, 2 through 128). Either flag
implies `--affine`:

```bash
./flow flow-to-mlir --tile-size 4 --tile-l2-size 8 \
  tests/mlir/affine_loop.flow /tmp/tiled.mlir
```

The same controls are `FLOWC_MLIR_AFFINE`, `FLOWC_MLIR_TILE`, and
`FLOWC_MLIR_TILE_L2` when the command line does not set them. Command-line
values win over inherited environment variables.

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

Use `--aosoa-pad-auto` with `flow flow-to-mlir` to add one storage element only
for power-of-two logical extents. Irregular extents keep their original
storage size.

```bash
./flow flow-to-mlir --aosoa-pad-auto compiler/fixtures/mlir_opt/aosoa_padding.flow /tmp/aosoa.mlir
```

Set `FLOWC_MLIR_AOSOA_SWIZZLE=N` to xor each generated field index with that
index shifted by `log2(N)`. `N` must be a power of two from 2 through 32.
The rewrite applies this only to power-of-two logical extents, which keeps the
mapping within the source array for irregular extents. The default is zero.

> `affine-super-vectorize` and `affine-loop-fusion` still need affine loops,
> which the generator does not emit; they remain soft no-ops.
