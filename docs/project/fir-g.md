# FIR-G: Heterogeneous Program-Graph Compiler

Flow’s production path today is **AST → C | MLIR** (dual CPU) with Metal/WGSL/SPIR-V
GPU emit. That remains. This document describes the **next IR layer** that sits
between semantic AST and backend lowering: a dense-ID, columnar **program graph**.

## Goal

A compiler that reasons about a program as a **whole graph**, not only by walking
heap AST nodes one instruction at a time — with CPU, GPU (MLX), and learned models
each used only where they have a structural advantage.

This is **not** “run LLVM on the GPU.” Expensive global reasoning becomes explicitly
parallel over bulk arrays.

## Correctness vs profitability (absolute rule)

| Decision kind | Who decides |
|---------------|-------------|
| Semantic / correctness (types, effects safety, transform validity) | Deterministic compiler rules + verifier |
| Profitability (inline? unroll? device?) | Heuristics now; learned models later |

ML/GPU may **propose** and **score**. They never replace typechecking or semantic
validation. Bulk MLX/NumPy paths must match the CPU oracle bit-for-bit
(`tests/unit/test_fir_mlx_oracle.py`). Opt candidates are proposals only
(`fir_opts.py`) — they do not rewrite IR yet.

## Three IR levels

```text
Flow AST  →  FIR-S (semantic)  →  FIR-G (graph)  →  FIR-M (machine)  →  C | MLIR | LLVM
```

| IR | Role | Status |
|----|------|--------|
| **AST** | Source structure | Production (parser) |
| **FIR-S** | Typed semantic ops with dense IDs | Scaffolded via graphify from typed AST |
| **FIR-G** | Structure-of-arrays graph store + CSR | Phases 1–4 (analyses + routing + candidates) |
| **FIR-M** | Machine-oriented / backend prep | Later |

Backends (C, MLIR, WASM, Metal, SPIR-V) stay. FIR-G feeds **analysis and
optimisation policy**; lowering continues to reuse existing emitters until FIR-M
lands.

## FIR-G layout (SoA)

Dense IDs (`uint32`-scale integers), not permanent heap pointers:

```text
ValueId, OpId, BlockId, FunctionId, TypeId, EdgeId
```

Columns (Phase 1 subset):

```text
ops:      opcode, function, block, flags, operand_begin, operand_count, result_begin, result_count
operands: value, owner_op, index
values:   producer_op, type_id, flags, use_begin, use_count
blocks:   function, first_op, op_count
funcs:    name, first_block, block_count, flags, effect_bits
```

CSR views for analyses:

```text
CallGraph   (caller → callee edges)
UseDef      (value → use ops)
CFG         (block successors; Phase 1: coarse / optional)
```

## Device routing

```text
AnalysisDevice = CPU | NumPy | MLX | Auto
```

| Phase | What |
|-------|------|
| **1** | CPU reference: call-graph CSR, effect OR-propagation, reachability/dead, purity |
| **2** | Experimental MLX/NumPy bulk paths; differential vs CPU |
| **3** | Auto routing from *measured* break-even (`--calibrate` → `~/.cache/flow/fir_g_route.json`) |
| **4** | Batched opt *candidates* + deterministic cost scores (`--opts`); no rewrite yet |

CLI:

```bash
./flow fir-g prog.flow
./flow fir-g --calibrate                 # measure + save thresholds
./flow fir-g prog.flow --device=auto     # uncalibrated → cpu
./flow fir-g prog.flow --device=mlx      # bulk + oracle check
./flow fir-g prog.flow --opts            # dead_elim / inline proposals
./flow fir-g prog.flow --json --bench
```

Default remains **CPU**. Uncalibrated `--device=auto` stays on CPU (never guesses
GPU). After `--calibrate`, auto selects bulk only when `num_funcs` or call-edge
count meets the measured threshold.

Override threshold file: `FLOW_FIR_G_THRESHOLDS=/path/to.json` or `--thresholds`.

## Implementation order (locked)

1. Dense-ID FIR-G store + graphify from AST ✅  
2. CPU reference: call-graph, effect/reachability propagation ✅  
3. MLX prototype for bulk propagation (experimental module) ✅  
4. Auto CPU/GPU routing from measured thresholds ✅ Phase 3  
5. Batched optimisation candidate discovery + deterministic cost model ✅ Phase 4 start  
6. Learned cost models (inline first) → beam/speculative search  

Each stage is useful alone. Do not block on ML.

## Deliverables

| Artifact | Path |
|----------|------|
| Design | this file |
| Store + graphify | `src/flow/fir_g.py`, `src/flow/fir_graphify.py` |
| CPU analyses | `src/flow/fir_analysis.py` |
| Bulk MLX/NumPy | `src/flow/fir_mlx.py` |
| Measured routing | `src/flow/fir_route.py` |
| Opt candidates | `src/flow/fir_opts.py` |
| CLI dump | `./flow fir-g …` |
| Tests | `tests/unit/test_fir_g.py`, `test_fir_mlx_oracle.py`, `test_fir_route_opts.py` |

**Out of scope still:** applying opts to IR, beam search, replacing C/MLIR emitters,
dominators, full alias analysis, putting MLX in the trusted correctness core.

## Relation to dual backends / WASM

```text
Parse → typecheck → monomorphize
              │
              ├─→ C / MLIR / WASM emitters   (production today)
              │
              └─→ FIR-G analyses            (parallel track; CPU + experimental MLX)
```

FIR-G does not retire C or MLIR. It prepares whole-program reasoning that can
later *drive* those backends’ optimisation policies.
