# Training real models on your MacBook with Flow

This guide trains a multi-class neural network in Flow on a laptop and reports
what that costs. Every number below was measured on one machine: an Apple M4
Max MacBook (10 performance cores, 4 efficiency cores, 36 GB unified memory),
compiled through the C backend. Timings are best of 3 while the machine also
ran other builds, so treat them as honest ballpark figures for a working
laptop rather than lab conditions.

The three programs:

| Program | What it shows |
|---------|---------------|
| `examples/ml/digits_mlp.flow` | Multi-class training, minibatch SGD with momentum, CPU |
| `examples/ml/digits_mlp_parallel.flow` | Data-parallel gradient accumulation on pthreads |
| `examples/ml/digits_mlp_metal.flow` | What the Metal GPU path can and cannot do today |

Run them with the Python host (the Stage-A flowc driver does not cover these
programs yet):

```bash
FLOW_HOST=python ./flow run examples/ml/digits_mlp.flow
FLOW_HOST=python ./flow run examples/ml/digits_mlp_parallel.flow
FLOW_HOST=python ./flow run examples/ml/digits_mlp_metal.flow
```

Each prints PASS and exits 0 only when its checks hold.

## The task: 8x8 digits, ten classes

`digits_mlp.flow` builds its dataset at startup. A procedural seven-segment
renderer draws each digit 0 to 9 onto an 8x8 grid, then an LCG-driven
augmenter produces variations: shifts of up to one pixel, intensity between
0.7 and 1.0, additive noise, and two salt pixels per image. 200 training and
40 test samples per class gives 2000 train and 400 test images. The seed is
fixed, so every run sees the same dataset, pixel for pixel. The program
computes every pixel at startup, with no download step and no embedded blob.

The model is a 64 -> 32 (relu) -> 10 MLP with softmax cross-entropy: 2410
parameters. Compare `examples/ml/models/mlp_xor_from_scratch.flow`, the
25-parameter starting point this scales up from.

### Weights in module statics

Weight, momentum and gradient buffers are module statics
(LANGUAGE_SPEC 3.3.1): top-level `let mut` pointers, allocated once.

```flow
let mut w1: ptr<f32> = null    # IMG x HIDDEN
let mut b1: ptr<f32> = null
let mut vw1: ptr<f32> = null   # momentum
let mut gw1: ptr<f32> = null   # gradient accumulator
```

Every function in the file reads and writes them directly, so `forward`,
`backward` and `apply_update` take only the sample pointer and label. The
parallel variant below reuses the same shape: worker threads reach the
weights through the module statics instead of threaded-through arguments.

### Manual backprop, minibatch SGD

The training loop is written out in full: forward pass, stable softmax,
cross-entropy, backward pass, momentum update. `expf` and `logf` come from
libm through an `extern` block. The stdlib `math.flow` versions are a Taylor
series and a Newton iteration meant for teaching, and softmax feeds `expf`
large negative arguments where the 20-term Taylor series breaks down, so the
libm externs are the right tool here.

```flow
extern {
    function expf(x: f32) -> f32
    function logf(x: f32) -> f32
}
```

Minibatches of 32, learning rate 0.15, momentum 0.9, 20 epochs. Output from
this machine:

```
digits_mlp: 8x8 synthetic digits, 64 -> 32 (relu) -> 10 (softmax CE)
  params: 2410
  train samples: 2000
  test samples: 400
  epoch 0 train_loss 1.2879 test_acc 90.00%
  epoch 5 train_loss 0.0463 test_acc 98.25%
  epoch 19 train_loss 0.0335 test_acc 98.75%
  training ms: 306.39
final test accuracy: 98.75%
PASS
```

The run is deterministic. Two consecutive runs on this machine produced
identical losses and accuracies to every printed digit. The program gates
PASS on at least 90% test accuracy and lands at 98.75%.

## What fits at each scale

The same trainer was rebuilt with hidden sizes 32, 128 and 512 and timed for
the full 20-epoch run (2000 samples per epoch). `./flow run` compiles C at
-O0 by default; `FLOW_CFLAGS='-O2'` turns optimization on.

| Hidden | Params | 20 epochs, -O0 | 20 epochs, -O2 | Final test acc |
|-------:|-------:|---------------:|---------------:|---------------:|
| 32 | 2,410 | 0.30 s | 0.04 s | 98.75% |
| 128 | 9,610 | 1.21 s | 0.21 s | 99.75% |
| 512 | 38,410 | 8.53 s | 2.61 s | 99.25% |

Reading the table: time grows close to linearly with parameter count, and
-O2 buys roughly 3x to 7x. Extrapolating the -O2 column, a few hundred
thousand parameters trains in minutes on this laptop. That covers small MLPs,
classic tabular models, and toy convnets written as loops. It does not cover
transformer-scale work, and the honest path there is the GPU section below.

## Data-parallel gradient accumulation

`digits_mlp_parallel.flow` splits each minibatch into 8 shards. Each shard
accumulates gradients into its own private buffers, running as a real
pthread through the runtime's `flow_parallel_for_i32`
(`lib/runtime/concurrency_parallel.flow`). The reduction then sums shard
buffers serially in fixed order. Because the summation order never changes,
the serial and parallel runs produce bit-identical weights, and the program
verifies they reach the same accuracy.

The worker is an ordinary Flow function handed to the runtime as a C
function pointer. `@flow_api` keeps its symbol unmangled:

```text
@flow_api
function shard_body(s: i32, ctx: ptr<void>) -> void {
    shard_grad(s)
}

flow_parallel_for_i32(0, SHARDS, 1, shard_body, null)
```

One caveat: the strict type checker cannot yet type a function passed as
`ptr<void>`, so this one file carries a `flow:lenient` pragma, the repo's
documented mechanism for checker gaps. The CPU and Metal examples are fully
strict.

Measured on this machine (batch 250, 8 shards, 30 epochs, best of 3 full
training runs):

| Build | Serial grad+update | Parallel grad+update | Speedup |
|-------|-------------------:|---------------------:|--------:|
| -O0 | 408.9 ms | 108.5 ms | 3.8x |
| -O2 | 58.2 ms | 28.4 ms | 2.0x |

Both runs finish at 99.00% test accuracy, and the program checks the two
agree exactly. The speedup shrinks at -O2 because the runtime spawns fresh
pthreads for every batch: once optimized math shrinks each shard's work to
tens of microseconds, thread creation becomes the bill. A persistent worker
pool in the runtime is the obvious next step; until then, parallel shards pay
off when each shard has at least a few hundred microseconds of work.

## The Metal path, honestly

Flow has two GPU surfaces today, and they do not meet in the middle yet.

Kernel source generation works. `@gpu` functions compile to Metal source:

```bash
./flow gpu lib/stdlib/gpu_kernels.flow
# build/gpu/gpu_vector_add.metal
# build/gpu/gpu_scale.metal
# build/gpu/gpu_matmul_row.metal
```

The emitted `gpu_matmul_row.metal` compiles cleanly through
`MTLDevice newLibraryWithSource` on this machine. (This branch fixes the
Metal codegen for `for` loops, which previously crashed on the matmul
kernel.)

Runtime dispatch is narrower. A running Flow binary can allocate unified
CPU/GPU buffers (`runtime/gpu_metal.m`, shared storage on Apple Silicon) and
launch exactly one compute kernel: `flow_gpu_mul_f32`, elementwise multiply.
There is no runtime loader that takes the `./flow gpu` output and dispatches
it, so the matmuls, the softmax and the weight update of the digits model
cannot run on the GPU yet.

`digits_mlp_metal.flow` therefore does the two things that are real today.
First, it runs the one training-relevant elementwise op on Metal: the ReLU
backward gate `dh = da * mask` for a full minibatch of hidden gradients, and
checks the GPU result against the CPU elementwise (8000 elements, exact
match on this machine). Second, it measures where a single kernel dispatch
(encode + dispatch + waitUntilCompleted, the per-launch cost a training step
would pay) beats a CPU loop:

| Elements | CPU loop | GPU dispatch |
|---------:|---------:|-------------:|
| 65,536 | 0.070 ms | 0.126 ms |
| 1,048,576 | 1.133 ms | 0.212 ms |
| 4,194,304 | 4.496 ms | 0.710 ms |
| 16,777,216 | 18.2 ms | 0.7 ms |

The crossover sits between 64K and 1M elements. Below that, dispatch
overhead dominates and the CPU wins. The digits model's largest tensor is
64x32, far under the crossover, which is the quantitative reason a 2410-
parameter model belongs on the CPU even once a full GPU path exists.

Gap list for the training loop on Metal, as of this branch:

- No runtime loader for `./flow gpu` output, so `@gpu` kernels like
  `gpu_matmul_row` cannot be launched from a Flow program.
- `flow_gpu_mul_f32` is the only dispatchable kernel; there is no matmul,
  no reduction, no softmax.
- Each dispatch creates a command buffer and blocks on completion, so even
  with more kernels, small-tensor training would need batched command
  encoding to be competitive.

## Where flowc and the MLIR JIT fit

These examples run through the Python host and the C backend. The other two
compilation paths, checked on this machine:

- `FLOW_HOST=flowc` (the self-hosted Stage-A driver) does not yet cover this
  subset; the bootstrap on this branch fails before reaching the examples,
  hence `FLOW_HOST=python` in every command above.
- `./flow jit` (MLIR) rejects the programs at compile time:
  `module statics not yet supported in MLIR backend (static 'w1')`. Module
  statics are the storage mechanism for weights here, so MLIR JIT training
  waits on that feature. The MLIR path already carries the tensor and GPU
  dialects (`--mlir --mlir-gpu`), which is where a fused training path would
  eventually land.

## Reproducing

```bash
FLOW_HOST=python ./flow run examples/ml/digits_mlp.flow           # ~0.3 s train, PASS at 98.75%
FLOW_HOST=python ./flow run examples/ml/digits_mlp_parallel.flow  # prints measured speedup
FLOW_HOST=python ./flow run examples/ml/digits_mlp_metal.flow     # Metal parity + crossover table
FLOW_CFLAGS='-O2' FLOW_HOST=python ./flow run examples/ml/digits_mlp.flow  # optimized build
```

All three gate their PASS on checks (accuracy threshold, serial/parallel
agreement, GPU/CPU parity), so a green exit code means the numbers above
reproduced on your machine.

## Interactive sketches

### Softmax-ish normalize (browser)

Toy “logits → probabilities” without libm — positive weights, L1 normalize:

```flow
function main() -> i32 {
    let mut z: array<f64, 3> = [2.0, 1.0, 0.1]
    let mut sum: f64 = 0.0
    for i in 0 to 3 {
        sum = sum + z[i]
    }
    for i in 0 to 3 {
        z[i] = z[i] / sum
    }
    printf("p0=%f p1=%f p2=%f\n", z[0], z[1], z[2])
    return 0
}
```

### SGD step on one weight (browser)

```flow
function main() -> i32 {
    let mut w: f64 = 0.0
    let x: f64 = 2.0
    let y: f64 = 5.0
    let lr: f64 = 0.1
    for step in 0 to 10 {
        let pred: f64 = w * x
        let g: f64 = 2.0 * (pred - y) * x
        w = w - lr * g
    }
    printf("w=%f (target 2.5)\n", w)
    return 0
}
```

### Accuracy counter (browser)

```flow
function main() -> i32 {
    let preds: array<i32, 5> = [0, 1, 2, 2, 9]
    let labels: array<i32, 5> = [0, 1, 1, 2, 9]
    let mut correct: i32 = 0
    for i in 0 to 5 {
        if preds[i] == labels[i] {
            correct = correct + 1
        }
    }
    printf("correct=%d / 5\n", correct)
    return 0
}
```

### Momentum update (browser)

```flow
function main() -> i32 {
    let mut w: f64 = 0.0
    let mut v: f64 = 0.0
    let g: f64 = -1.0
    let lr: f64 = 0.1
    let mu: f64 = 0.9
    for step in 0 to 5 {
        v = mu * v - lr * g
        w = w + v
    }
    printf("w=%f v=%f\n", w, v)
    return 0
}
```

### Argmax class (browser)

```flow
function main() -> i32 {
    let logits: array<f64, 4> = [0.1, 2.5, 0.3, 0.2]
    let mut best: i32 = 0
    for i in 1 to 4 {
        if logits[i] > logits[best] {
            best = i
        }
    }
    printf("class=%d\n", best)
    return 0
}
```

### Minibatch mean loss (browser)

```flow
function main() -> i32 {
    let losses: array<f64, 4> = [0.5, 0.2, 0.8, 0.1]
    let mut sum: f64 = 0.0
    for i in 0 to 4 {
        sum = sum + losses[i]
    }
    printf("mean=%f\n", sum / 4.0)
    return 0
}
```

Start smaller: [autodiff-basics.md](autodiff-basics.md) · XOR
[`examples/ml/models/mlp_xor.flow`](../../examples/ml/models/mlp_xor.flow).
