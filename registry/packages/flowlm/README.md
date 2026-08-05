# flowlm

A character language model written entirely in Flow. Tokenizer, one causal
self-attention block, hand-derived backward pass, Adam, and a finite-difference
gradient check over every parameter. No BLAS, no autodiff, no GPU. It trains on
a laptop CPU in under a minute.

The scale is small on purpose. The largest model the package will build is
about 20,000 parameters over a 96-symbol vocabulary and a 32-token context.
That is enough to learn the character statistics of a few kilobytes of English
and generate text that contains real words. It is not enough to do anything
else, and the package does not pretend otherwise. See
[Measured limits](#measured-limits).

## Quick run

```
FLOW_HOST=python ./flow run examples/ai/flowlm_charlm.flow
```

That single file fits a vocabulary on the embedded 5 KB corpus, runs the
gradient check, trains for 3000 steps, prints a loss curve, and samples at
three temperatures. Exit code 0 means both the gradient check and the held-out
loss gate passed.

Measured on an M-series MacBook, `-O0` (what `./flow run` uses):

```
distinct characters     : 29
char tokens             : 5131
uniform baseline (nats) : 3.367296
train / held-out tokens : 4617 / 514
parameters              : 15677

train loss    (nats/char) : 0.743587
held-out loss (nats/char) : 2.040593
uniform baseline          : 3.367296
held-out perplexity       : 7.695168
baseline perplexity       : 29.000000
```

Samples after training, prompt `"the "`:

```
temperature 0.4
  mean who mend it down before the words go in and your mornings out at four
  mornings out at four first because the book. his the water is a paper off.

temperature 0.7
  hour not write the wall small and the log does. the hour is still, i write
  the tide log does, and nobody ten stumbers the wren pier.

temperature 1.0
  hour on ays back. the gullss at even. i read drumqoukes bce enory. still,
  when the way whierh. i didn for and did fread pleven brown benok at the
```

The temperature sweep is the interesting part. At 0.4 the model repeats
high-probability phrases it has memorised. At 1.0 it produces plausible letter
sequences that are mostly not words. That spread is what learned character
statistics look like at this size.

## Layout

| File | Contents |
|---|---|
| `src/util.flow` | allocation, deterministic LCG, f32 libm wrappers, printing |
| `src/corpus.flow` | the embedded ~5 KB training text |
| `src/tokenizer.flow` | char vocabulary + capped mini-BPE |
| `src/model.flow` | forward pass and manual backward pass |
| `src/train.flow` | Adam, gradient clipping, LR schedule, sampling, perplexity |
| `src/gradcheck.flow` | analytic vs finite-difference self-test |
| `src/lib.flow` | package entry point; imports every submodule |

### A note on imports

Flow's module resolver has no re-export. A brace list on an import is checked
against the declarations in the named file, so `flowlm.lib` cannot forward
`flowlm.model`'s symbols under its own name. Two forms work:

```flow
import flowlm.lib                                  # pulls in the whole package
import flowlm.model { flm_forward, flm_backward }  # explicit, per submodule
```

The submodules are the addressable units. `lib.flow` is the aggregator.

Registry resolution for `import flowlm.*` needs the package installed under
`flow_packages/`. Inside this repository, where it is not, the demo and the
language test address the files through the project root instead:

```flow
import registry.packages.flowlm.src.model { flm_forward }
```

Both paths resolve to the same files. The second one is what
`examples/ai/flowlm_charlm.flow` and `tests/lang/test_flowlm.flow` use, so they
build with a bare `flow.transpiler` invocation and no registry install step.

## Architecture

For a sequence of `n <= T` token ids:

```
h    = tok_emb[x_t] + pos_emb[t]                     (n, D)
n1   = layernorm(h; ln1_g, ln1_b)                    (n, D)
q,k,v= n1 @ Wq/Wk/Wv + bq/bk/bv                      (n, D)
s    = q @ k^T / sqrt(D), causal mask s[t][u>t]      (n, n)
a    = softmax_row(s)                                (n, n)
c    = a @ v                                         (n, D)
h2   = h + (c @ Wo + bo)                             (n, D)
n2   = layernorm(h2; ln2_g, ln2_b)                   (n, D)
f    = tanh(n2 @ W1 + b1)                            (n, F)
h3   = h2 + (f @ W2 + b2)                            (n, D)
nf   = layernorm(h3; lnf_g, lnf_b)                   (n, D)
z    = nf @ Wout + bout                              (n, V)
loss = mean_t cross_entropy(z[t], y[t])
```

One block, one head, pre-norm residuals, a final layernorm before the output
projection. 22 parameter tensors.

The MLP uses `tanh` rather than `relu`. `tanh` is smooth everywhere, so the
finite-difference check has no kinks to trip over. `relu` would need per-point
kink detection to check honestly, and this package would rather be checkable
than fashionable.

All parameters live in one flat f32 arena, a module-static `ptr<f32>`, with
per-tensor offsets computed at init. Gradients live in a second arena of the
same shape. That makes clipping and Adam single flat loops, and it makes the
gradient check a single loop over `flm_param_count()`.

Dot products accumulate in `f64` and store back as `f32`. At this size that
costs nothing measurable and it keeps the finite-difference comparison
measuring the derivation rather than the rounding.

## Gradient checking

This is the correctness anchor. A loss curve can fall with a sign error on a
small tensor and you would never see it. So the package builds a deliberately
tiny model (V=7, D=4, T=5, F=8, 263 parameters), runs one forward and one
backward, then for **every single parameter** recomputes

```
numeric = (L(theta + eps) - L(theta - eps)) / (2 eps)
```

and compares. Errors are reported per tensor, so a broken derivation shows up
as one bad row rather than one bad number in a sea of good ones.

```
  tensor            n    max rel err   worst analytic   worst numeric
  ---------------------------------------------------------------------
  tok_emb  [V,D] 28   1.252e-03     1.769e-01     1.771e-01  ok
  pos_emb  [T,D] 20   1.282e-03     1.769e-01     1.771e-01  ok
  ln1_gamma[D]   4   4.521e-05     2.255e-01     2.255e-01  ok
  ln1_beta [D]   4   6.742e-05     1.241e-01     1.241e-01  ok
  Wq       [D,D] 16   4.533e-04    -3.055e-02    -3.054e-02  ok
  bq       [D]   4   1.012e-04    -6.649e-02    -6.650e-02  ok
  Wk       [D,D] 16   3.627e-03     3.015e-04     3.087e-04  ok
  bk       [D]   4   3.120e-03     2.980e-08    -6.210e-06  ok
  Wv       [D,D] 16   2.529e-04    -1.470e-02    -1.469e-02  ok
  bv       [D]   4   2.255e-04    -2.379e-02    -2.379e-02  ok
  Wo       [D,D] 16   1.673e-04    -7.431e-02    -7.430e-02  ok
  bo       [D]   4   2.619e-04    -3.053e-02    -3.054e-02  ok
  ln2_gamma[D]   4   4.000e-03    -4.595e-03    -4.614e-03  ok
  ln2_beta [D]   4   7.796e-04    -1.356e-02    -1.355e-02  ok
  W1       [D,F] 32   5.293e-03    -8.415e-04    -8.309e-04  ok
  b1       [F]   8   5.398e-04    -7.865e-03    -7.869e-03  ok
  W2       [F,D] 32   3.574e-03    -1.691e-03    -1.684e-03  ok
  b2       [D]   4   8.359e-05     9.489e-02     9.490e-02  ok
  lnf_gamma[D]   4   1.059e-04     6.815e-02     6.816e-02  ok
  lnf_beta [D]   4   1.530e-04    -1.377e-02    -1.377e-02  ok
  Wout     [D,V] 28   1.271e-03     4.127e-03     4.121e-03  ok
  bout     [V]   7   3.566e-05     7.787e-02     7.787e-02  ok

  worst relative error over all parameters: 5.293e-03
```

`eps = 0.004`, central differences, relative error floored at a denominator of
0.002 so near-zero gradients do not divide by rounding noise. The gate is
1e-2. Parameters are stored in f32, so ~1e-3 is what a correct implementation
gives here; the remaining error is single-precision rounding, not the
derivation.

Run it alone:

```flow
import flowlm.gradcheck { flm_gradcheck }
let ok: bool = flm_gradcheck(true)   # true = print the per-tensor table
```

## API

### Tokenizer (`flowlm.tokenizer`)

| Function | Purpose |
|---|---|
| `flm_vocab_fit(data: ptr<u8>, n: i32) -> i32` | fit the char vocabulary; returns its size or -1 past the cap |
| `flm_vocab_size() -> i32` | chars + merges |
| `flm_char_count() -> i32` | char-level symbols only |
| `flm_char_id(byte: i32) -> i32` | byte to id, -1 if unseen |
| `flm_id_char(id: i32) -> i32` | id to byte, -1 for merged ids |
| `flm_encode_chars(data, n, out, cap) -> i32` | bytes to char ids |
| `flm_bpe_train(ids, n, max_merges, counts) -> i32` | learn merges in place; returns the new length |
| `flm_bpe_apply(ids, n) -> i32` | apply learned merges to a fresh sequence |
| `flm_bpe_counts_size() -> i32` | scratch size for the pair-count table |
| `flm_decode(ids, n, out, cap) -> i32` | ids to bytes, expanding merges recursively |
| `flm_merge_count() -> i32` | merges learned |

Vocabulary tables are module statics: `array<i32, 256>` for byte to id,
`array<i32, 96>` for id to byte, `array<i32, 32>` pairs for the merge table.
Char ids are assigned in ascending byte order, so a fit is reproducible.

On the embedded corpus: 29 distinct characters, 5131 char tokens, and 24 merges
take that to 3453 tokens (a 33% reduction) with exact decode round-trip.

### Model (`flowlm.model`)

| Function | Purpose |
|---|---|
| `flm_model_init(vocab, dmodel, ctx, dff) -> i32` | allocate; returns the parameter count or -1 past a cap |
| `flm_model_randomize(emb_sd: f32)` | 1/sqrt(fan_in) matrices, gains 1, biases 0 |
| `flm_forward(inp, tgt, n) -> f64` | mean cross-entropy in nats; keeps activations |
| `flm_backward(inp, tgt, n)` | accumulate gradients for the last forward |
| `flm_zero_grads()` | clear the gradient arena |
| `flm_param_count() -> i32` | parameters |
| `flm_params_ptr() / flm_grads_ptr() -> ptr<f32>` | the two arenas |
| `flm_tensor_count/offset/size/name` | per-tensor metadata, used by the gradient check |
| `flm_prob_at(t, j) / flm_logit_at(t, j) -> f32` | post-forward readout |

Caps: `vocab <= 96`, `d_model <= 32`, `context <= 32`, `d_ff <= 128`, one
block, one head. Dimensions are chosen at `flm_model_init` and may be smaller;
the gradient check exploits that to run a 263-parameter model.

`flm_model_init` allocates and does not free. Calling it twice, as the demo
does (once tiny for the check, once full for training), leaks the first
allocation. At these sizes that is a few hundred kilobytes and it is not worth
a free path.

### Training (`flowlm.train`)

| Function | Purpose |
|---|---|
| `flm_optim_init()` | allocate Adam state; call after `flm_model_init` |
| `flm_train_step(ids, nids, seq_len, batch, lr, clip) -> f64` | zero, accumulate over `batch` random windows, scale, clip, Adam; returns mean loss |
| `flm_lr_schedule(step, base_lr, warmup, total, min_frac) -> f32` | linear warmup then cosine decay |
| `flm_clip_grads(max_norm) -> f32` | global L2 clip; returns the pre-clip norm |
| `flm_adam_step(lr, beta1, beta2, eps)` | Adam over the whole arena |
| `flm_eval_loss(ids, nids, seq_len, count, stride) -> f64` | deterministic sweep, no gradients |
| `flm_perplexity(loss: f64) -> f64` | `exp(loss)` |
| `flm_sample(prompt, prompt_len, out, count, temperature) -> i32` | sample ids with a rolling context |
| `flm_last_grad_norm() -> f32` | pre-clip norm from the last step |
| `flm_optim_steps() -> i32` | Adam updates applied so far |
| `flm_optim_ready() -> bool` | true once `flm_optim_init` has run |

Adam bias correction keeps running products of `beta1^t` and `beta2^t` rather
than calling `pow` every step. Sampling shifts the context window left once it
is full, so positions are always `0..n-1`.

### Determinism

Every random draw goes through one 32-bit LCG in `flowlm.util`
(`state = state * 1664525 + 1013904223`, high 24 bits). Seed it with
`flm_srand(seed)`. Initialization, window selection, and sampling are all
reproducible: the demo produces byte-identical output across runs, which is why
the loss gate can be an assertion rather than a hope.

## Measured limits

Numbers below are measured, not estimated.

| | |
|---|---|
| Max vocabulary | 96 symbols |
| Max `d_model` | 32 |
| Max context | 32 tokens |
| Blocks / heads | 1 / 1 |
| Max parameters | 20,032 |
| Demo parameters | 15,677 (V=29, D=32, T=32, F=128) |
| Corpus | 5131 bytes, 29 distinct characters |
| Demo training | 3000 steps x batch 8: ~4 s at `-O2`, ~23 s at `-O0` |
| Demo end to end | ~48 s wall for `FLOW_HOST=python ./flow run`, transpile and clang included |
| Gradient check | ~0.05 s |
| Held-out loss | 2.04 nats/char (7.70 ppl) vs 3.37 baseline (29.0 ppl) |
| Train loss | 0.74 nats/char |
| Gradient check scope | 263 parameters, 22 tensors, worst relative error 5.3e-3 |

## What does not work

- **This is not a GPT-2.** It is one attention head over a 32-token context.
  It has no notion of words beyond what character statistics give it, and it
  cannot answer a question, follow an instruction, or hold a topic.
- **It memorises.** 15,677 parameters against 5131 characters. The train/held-out
  gap in the demo (0.74 vs 2.04) is the honest measurement of that, and it is
  printed rather than hidden. Larger corpora would narrow the gap and raise
  both numbers.
- **Batch size 1 internally.** `flm_train_step` accumulates over several
  windows, but each forward runs one sequence. There is no batched matmul, so
  the arithmetic intensity is low and the CPU is mostly waiting on loads.
- **No dropout, no weight decay, no label smoothing.** Adding them is easy;
  nothing here demonstrates that they help at this scale.
- **BPE does not help at this size.** The tokenizer supports it and the demo
  shows a 33% token reduction with exact round-trip, but the model trains on
  char tokens. 5 KB is far too little text for subword units to pay for the
  vocabulary they consume.
- **Single-threaded scalar f32.** No SIMD, no threads. Flow has both; this
  package uses neither, so the numbers above are a floor rather than a ceiling.
- **`flm_model_init` does not free.** See above.
- **MLIR backend unsupported.** The package relies on module statics
  (LANGUAGE_SPEC 3.3.1), which the C backend implements and the MLIR backend
  rejects. Build with the C backend.

## Roadmap hooks

The places where this package would grow, in the order that would pay off:

1. **Metal matmul.** `flm_linear` and `flm_linear_bwd` in `src/model.flow` are
   the only dense GEMMs, and both are already offset-addressed into one flat
   arena. Routing them through `runtime/gpu_metal.m` would touch two functions.
   That is the change that lifts `d_model` from 32 into the hundreds.
2. **Batched sequences.** `flm_forward` takes `(inp, tgt, n)` and indexes
   activations as `t * D + i`. Adding a leading batch dimension is mechanical
   and would give the matmuls something to chew on.
3. **flowc.** The package is written in the Stage-A-friendly subset where it
   can be: `while` loops, fixed arrays, module statics, no closures, no
   generics. It does use `ptr<T>` arithmetic through indexing and f32 externs.
   Getting it through `FLOW_HOST=flowc` is a compiler exercise more than a
   package one, and it is the obvious way to dogfood the self-hosted path on
   something numerically demanding.
4. **More blocks.** The forward and backward passes are written as a single
   inline block rather than a loop over blocks. Making the block a function
   over its own activation slices is the prerequisite for depth.
5. **Checkpointing.** Weights are one contiguous `f32` arena, so save and load
   are one `fwrite` and one `fread`. Nothing in the package does it yet.

## Compiler notes

The f32 libm names (`expf`, `logf`, `sqrtf`, `tanhf`, `cosf`, `fabsf`) are
declared as ordinary externs. They are not in `stdlib_functions` or
`math_functions` in `src/flow/c_generator.py`, so the C backend emits a
prototype for each; those prototypes match `<math.h>` exactly, and `math.h` is
always included. No compiler change was needed.

Overload mangling does apply to exported functions with parameters, and it
resolves on argument type. `flm_srand` takes `i32` rather than `u32` for that
reason: an integer literal argument is `i32`, and a `u32` parameter would have
left the call unresolved against the mangled `flm_srand_u32`.

## Corpus and licence

MIT, matching the rest of the Flow registry. The training text in
`src/corpus.flow` was written for this package. There is no copyrighted
material in it.
