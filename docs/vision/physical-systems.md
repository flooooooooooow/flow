# Flow — Physical Computational Systems

> **Product thesis:** Flow is a language for describing *physical computational
> systems* — not merely a safer C, and not merely “evolution through time” in the
> abstract. An RF receiver, a spacecraft controller, and a digital twin of either
> are the same kind of program: units, rates, timing, memory topology, numeric
> precision, hardware placement, and fault behaviour are part of the compile-time
> model.
>
> Founding abstraction: [VISION.md](../../VISION.md) (*evolution through time*).
> Grammar cards for dynamics: [north-star.md](north-star.md).
> This document is the **domain beachhead** and the long-horizon architecture for
> RF, embedded, SDR, FPGA-adjacent, and satellite engineering.

**Status:** Adopted as product thesis (2026-08-08). Wedge v0 is in flight;
items marked SHIPPED / PARTIAL / DESIGN / LATER below.

---

## Why this exists

An RF / satellite engineer routinely crosses C/C++, Python/MATLAB, Verilog /
VHDL / SystemVerilog, CUDA, GNU Radio, shell, vendor configs, device trees, and
assorted DSLs in one project. Flow’s opportunity is to collapse those boundaries
into one coherent system whose compiler understands the *engineering* system,
not only the instructions.

**Do not pitch Flow as:** “a safer language for embedded programming.”
Rust already owns much of that conceptual territory.

**Pitch Flow as:** a language for describing physical computational systems.

```flow
signal antenna
    |> adc @ 122.88MHz
    |> mix(2.412GHz)
    |> fir(channel_filter)
    |> decimate(4)
    |> fft(2048)
    |> detect
    |> decode
```

From that description the compiler should eventually derive simulation, analysis,
and heterogeneous deployment:

```text
                    FLOW
                     │
        ┌────────────┼────────────┐
        │            │            │
     Simulation    Analysis     Deployment
        │                         │
   ┌────┴────┐          ┌────────┼────────┐
 Channel   Digital      MCU      DSP      FPGA
 models     twin         │        │        │
                      machine   SIMD      RTL
                       code
```

---

## Killer stack (the differentiator)

Individual syntax features are not the product. The product is that the compiler
jointly understands:

| Concern | Role |
|---------|------|
| Units | Dimensional + RF algebra (dBm, GHz, deg) |
| Sample rates | In the type; illegal mixes require explicit resample |
| Signal domains | Time vs frequency; ops gated by domain |
| Timing | Deadlines, jitter, WCET, `guarantee` contracts |
| Memory topology | SRAM / DRAM / DMA / TCM / MMIO placement |
| Hardware resources | DMA channels, cores, interrupts, clocks |
| Numeric precision | Fixed-point, saturating, error bounds |
| Coordinate frames | ECEF / ECI / Body typed vectors |
| Fault tolerance | Watchdogs, TMR, radiation-aware storage |
| Heterogeneous execution | CPU + DSP + FPGA + GPU from one program |

Zero-cost escape hatches and boring C ABI remain mandatory (see §29).

---

## Beachhead sequencing

Build credibility in this order. Do **not** chase certification or RTL first.

| Phase | Focus | Outcome |
|-------|--------|---------|
| **W0** | RF units + quantity literals + complex/IQ + rate-tagged signals + memory/RT attributes + docs | Compilable RF sketch; dimension/rate mistakes fail at compile time |
| **W1** | Fuseable DSP `\|>` with rate analysis; harden `guarantee` / `@rt_safe` | Pipelines that look like GNU Radio but lower to fused C/SIMD |
| **W2** | MMIO / SVD import; bitfields; fixed-point + saturating | Embedded register + protocol comfort |
| **W3** | Bare-metal + RTOS interop; interrupts; state machines | Flight-adjacent firmware path |
| **W4** | Simulate ↔ deploy same code; digital twin | HIL / twin story |
| **W5** | `@hardware` → RTL; clock domains; `deploy { … → fpga }` | Heterogeneous systems language |
| **W6** | Fault / radiation / `Flow Safety` / DO-178C story | Aerospace qualification path |

Audio RT (`@rt_safe`, lifetime domains) is the **proving ground** for the same
contracts; RF/SDR is the **named beachhead**.

---

## Architecture (30 pillars)

### 1. Hard real-time as a language property — PARTIAL

Express timing contracts, not only algorithms:

```flow
task demodulate(packet)
    deadline 40us
    period 100us
    jitter < 2us
    priority realtime
{
    ...
}
```

```flow
guarantee
{
    latency < 12us
    heap_allocations == 0
    blocking == false
}
```

**Today:** `@rt_safe` + lifetime domains reject heap and many blocking APIs
([rt-safety.md](../library/rt-safety.md)).
**W0:** `@guarantee(no_alloc, no_block)` aliases / extends that discipline.
**Later:** WCET, schedulability, DMA/interrupt awareness, unproven vs proven
guarantees.

### 2. Memory topology first-class — PARTIAL (attrs)

```flow
let samples: Buffer<4096, complex<f32>>
    @dma
    @aligned(64)
    @noncacheable
```

```flow
memory RF
{
    rx_ring : dma<complex<i16>, 8192>
    scratch : sram<f32, 4096>
    coeffs  : flash<f32, 128>
}
```

**W0:** attributes `@dma`, `@noncacheable`, `@aligned(N)` recognized (placement
hints; full region types later).
**Later:** `memory` blocks, `rx_buffer -> DMA1.channel(3)`.

### 3. Units in the type system — PARTIAL → RF

SI units shipped ([north-star.md](north-star.md) §6,
`examples/evolution/units_kinematics.flow`).

RF needs:

```flow
let fc = 2.45GHz
let fs = 40MHz
let gain = 17dB
let power = -73dBm
let phase = 90deg
```

`fc + delay` must fail. RF algebra: `20dBm + 3dB → 23dBm`, `0dBm → 1mW`,
`wavelength(2.4GHz)`.

**W0:** `lib/stdlib/rf.flow` unit pack + quantity suffixes + helpers.
**Later:** full affine dB family, compiler-derived link budgets.

### 4. Complex / IQ native — PARTIAL (stdlib)

```flow
complex<f32>
iq<i16>
phasor<f32>
```

Ops (`rotate`, `magnitude`, `phase`, `conj`) should lower to SIMD/DSP.

**W0:** `ComplexF32` / `ComplexF64` + IQ helpers in `rf.flow`.
**Later:** primitive `complex<T>`, autovectorization.

### 5. Signals and streams native — DESIGN / PARTIAL (`\|>`)

```flow
rx
    |> mix(lo)
    |> lowpass(20MHz)
    |> decimate(4)
    |> fft(2048)
```

Compiler path: graph → rate analysis → buffer analysis → fusion →
SIMD/DSP/GPU/FPGA partition → code.

**Today:** `\|>` call chaining exists.
**W1:** DSP stage library + fusion; no heavyweight runtime graph required.

### 6. Sample rate in the type — PARTIAL (phantom rates)

```flow
Signal<complex<f32>, Rate20MHz>
a + b  # illegal across rates without resample
a |> decimate(2)  # → Rate10MHz
```

**W0:** phantom rate tags + typed stage functions in `rf.flow`.

### 7. Frequency domains as types — DESIGN

`TimeSignal<…>` vs `FrequencySignal<…>`; `fft` changes domain; ops gated.

### 8. Safe MMIO without ceremony — DESIGN

```flow
register GPIOA @ 0x4002_0000 { MODER : bits<32>, ODR : bits<16> }
GPIOA.ODR[5] = 1
import hardware "STM32H743.svd"
```

### 9. Exceptional bit manipulation — DESIGN

Packed `packet` layouts, `u32<be>` / `u32<le>`, saturating bit ops.

### 10. Fixed-point first-class — DESIGN

`fixed<16,12>`, `q15`, `q31`; eventually `quantize signal error < -90dB`.

### 11. Saturating arithmetic — DESIGN

`a +| b` or `sat<i16>` overflow semantics.

### 12. Transparent SIMD — PARTIAL

`vector<N, T>` exists in examples; push NEON/AVX/SVE/RVV/DSP backends;
users rarely write intrinsics.

### 13. FPGA compilation — LATER

```flow
@hardware
fn fir(x: Stream<i16>) -> Stream<i16> { ... }

deploy receiver {
    fir      -> fpga
    decoder  -> cpu
}
```

### 14. Clock domains visible — LATER

```flow
domain rf_clk  @ 245.76MHz
domain cpu_clk @ 800MHz
rf_clk.signal -> sync -> cpu_clk.decoder
```

### 15. Concurrency ↔ electronics — PARTIAL

`parallel`, channels, `@ core(N)`, `@ dma(N)`, bounded `channel<T, capacity=N>`.

### 16. Interrupts language-native — DESIGN

```flow
interrupt TIM2
    max_latency 800ns
    no_alloc
{ ... }
```

### 17. State machines native — DESIGN

Verified transitions for radios / spacecraft modes.

### 18. Fault tolerance — DESIGN

TMR, watchdogs, retries, degraded modes, safe states.

### 19. Radiation-aware programming — DESIGN

```flow
@radiation_sensitive
let navigation_state: protected<State>

persistent critical orbit_state
    checksum
    mirrored
```

**W0:** `@radiation_sensitive` recognized as a semantic marker.

### 20. Enforceable determinism — PARTIAL

`deterministic fn` / `deterministic { }` — reject hidden alloc, races,
nondeterministic APIs. Seed: `@deterministic` → `@rt_safe` discipline.

### 21. Numerical guarantees — DESIGN

`error < 1e-6`, interval/range analysis, fixed-point conversion proofs.

### 22–23. Control + typed frames + physical quantities — PARTIAL

Matrices / quaternions via numerical stack; **typed frames** (`Vector3<f64, ECEF>`)
are DESIGN. Units already cover dimensions.

### 24. Protocol descriptions → implementations — DESIGN / ECOSYSTEM

CCSDS, CAN, SpaceWire, MAVLink, … → encode/decode/validate/tests.

### 25–26. Sim and deploy share code; digital twins fall out — DESIGN

```flow
radio = SDR<USRP>()           # deploy
radio = SimulatedRadio(model) # test
```

Same DSP path. Twin = simulated peripherals under the same interfaces.

### 27. Compiler-assisted RF design — LATER

Derive Fs, decimation chains, AA requirements, DMA bandwidth; eventually
`optimize receiver for power subject to latency < 100us`.

### 28. Hardware + software description converge — LATER (north star of this doc)

One project tree: physics, simulation, signals, algorithms, protocols, memory,
hardware, scheduling, FPGA, firmware, host — multiple backends.

### 29. The boring stuff — PARTIAL / CRITICAL

LLVM/GCC interop, C ABI, headers, bare-metal, Cortex-M/A/R, RISC-V, x86,
Zephyr/FreeRTOS/Linux, GDB/LLDB, JTAG, DWARF, sanitizers, packages,
cross-compile, LSP, C migration:

```flow
import c "legacy_radio.h"
```

Adoption gate for any flight org with millions of lines of C.

### 30. Certification — LATER

`Flow` / `Flow Embedded` / `Flow Safety`; `flow build --profile flight`
disables unsuitable constructs. DO-178C, DO-330, ECSS, MISRA-style subsets.

---

## Profiles

| Profile | Intent |
|---------|--------|
| `flow` (default) | Full language |
| `embedded` | No GC assumptions; prefer static alloc; RT attributes meaningful |
| `flight` / `safety` | Deterministic subset; no heap in RT paths; bounded recursion; checked arithmetic |

Exact flag spelling: see Questions.md.

---

## Mapping to evolution vision

| Evolution vision | Physical-systems reading |
|------------------|--------------------------|
| State + `evolves as` | Plant / GNC / orbit dynamics |
| `every` / deadlines | RF frame timing, control loops |
| Units | SI + RF + frames |
| Guarantees | RT + numeric + fault contracts |
| Deploy | MCU / DSP / FPGA / host |
| Digital twin | Same program, simulated radios / buses |

Evolution remains the **abstraction**. Physical systems are the **first vertical**.

---

## W0 deliverables (this adoption)

| Artifact | Role |
|----------|------|
| This document | Architecture + sequencing |
| `VISION.md` update | Product thesis |
| `ROADMAP.md` beachhead | Priorities |
| `lib/stdlib/rf.flow` | Units, complex/IQ, phantom rates, DSP stage stubs |
| Quantity suffixes in parser | `2.45GHz`, `40MHz`, `17dB`, … |
| Attributes | `@dma`, `@noncacheable`, `@aligned`, `@hardware`, `@radiation_sensitive`, `@deterministic`, `@guarantee(...)` |
| `examples/rf/` | Tourist + rate-check demos |
| Tests | Units suffixes, RF arith, rate mismatch, attributes |

---

## Non-goals for W0–W1

- Synthesizable RTL
- Full WCET / schedulability proofs
- SVD import
- DO-178C toolchain qualification
- Replacing GNU Radio’s ecosystem overnight

Those stay on the map so the destination stays clear.
