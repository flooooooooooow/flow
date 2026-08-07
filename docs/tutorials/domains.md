# Applied Domains

Thin capstones that show Flow in scientific and creative domains. Each section
is one worked entrypoint plus a pointer into the example gallery — not a full
curriculum.

## Morphogenesis

Reaction–diffusion, CA, and growth sims that draw through `gfx`:

```bash
./flow gfx examples/morphogenesis/gray_scott.flow
./flow gfx examples/morphogenesis/turing_spots.flow
./flow gfx examples/morphogenesis/lsystem_tree.flow
```

Gray–Scott is the usual starting point: two chemicals on a grid, Laplacian
diffusion, nonlinear reaction, false-color blit each frame. Gallery README:
[`examples/morphogenesis/`](../../examples/morphogenesis/).

### Diffusion-reaction sketch (browser)

```flow
function main() -> i32 {
    # Tiny 1-D caricature: u grows toward 1, v damps u
    let mut u: f64 = 0.5
    let mut v: f64 = 0.25
    let f: f64 = 0.055
    let k: f64 = 0.062
    for t in 0 to 100 {
        let uvv: f64 = u * v * v
        u = u + (0.0 - uvv + f * (1.0 - u)) * 0.1
        v = v + (uvv - (f + k) * v) * 0.1
    }
    printf("u=%f v=%f\n", u, v)
    return 0
}
```

### Game of Life neighbor count (browser)

```flow
function main() -> i32 {
    # 3x3 neighborhood with center alive
    let cells: array<i32, 9> = [0, 1, 0, 1, 1, 1, 0, 0, 0]
    let mut n: i32 = 0
    for i in 0 to 9 {
        if i != 4 {
            n = n + cells[i]
        }
    }
    let center: i32 = cells[4]
    let mut next: i32 = 0
    if center == 1 {
        if n == 2 { next = 1 }
        if n == 3 { next = 1 }
    } else {
        if n == 3 { next = 1 }
    }
    printf("neighbors=%d next=%d\n", n, next)
    return 0
}
```

### Turing activator-inhibitor (browser)

```flow
function main() -> i32 {
    let mut a: f64 = 0.5
    let mut b: f64 = 0.5
    for t in 0 to 50 {
        let da: f64 = a * a / b - a
        let db: f64 = a * a - b
        a = a + 0.05 * da
        b = b + 0.02 * db
        if a < 0.01 { a = 0.01 }
        if b < 0.01 { b = 0.01 }
    }
    printf("a=%f b=%f\n", a, b)
    return 0
}
```

## Circuits

Modified nodal analysis and a SPICE-ish subset in `lib/stdlib/circuit.flow`:

```bash
./flow run examples/circuits/rc_rl_rlc.flow
./flow run examples/circuits/mna_dc.flow
./flow run examples/circuits/lc_tank.flow
```

### RC settle sketch (browser)

```flow
function main() -> i32 {
    let r: f64 = 1000.0
    let c: f64 = 0.000001
    let vin: f64 = 5.0
    let dt: f64 = 0.0001
    let mut v: f64 = 0.0
    for k in 0 to 50 {
        let i: f64 = (vin - v) / r
        v = v + (i / c) * dt
    }
    printf("v_c=%f\n", v)
    return 0
}
```

### RL rise (browser)

```flow
function main() -> i32 {
    let r: f64 = 10.0
    let l: f64 = 0.1
    let vin: f64 = 5.0
    let dt: f64 = 0.001
    let mut i: f64 = 0.0
    for k in 0 to 40 {
        let di: f64 = (vin - r * i) / l
        i = i + di * dt
    }
    printf("i=%f\n", i)
    return 0
}
```

### Voltage divider (browser)

```flow
function main() -> i32 {
    let r1: f64 = 1000.0
    let r2: f64 = 2000.0
    let vin: f64 = 9.0
    let vout: f64 = vin * r2 / (r1 + r2)
    printf("vout=%f\n", vout)
    return 0
}
```

## Neuro

Hodgkin–Huxley, LIF, networks — ODE / event sims, often with gfx:

```bash
./flow run examples/neuro/hodgkin_huxley.flow
./flow run examples/neuro/lif_fi_curve.flow
./flow gfx examples/neuro/fitzhugh_nagumo.flow
```

### Leaky integrate-and-fire sketch (browser)

```flow
function main() -> i32 {
    let tau: f64 = 10.0
    let v_rest: f64 = -70.0
    let v_th: f64 = -55.0
    let dt: f64 = 0.1
    let i_inj: f64 = 1.5
    let mut v: f64 = v_rest
    let mut spikes: i32 = 0
    for k in 0 to 500 {
        v = v + ((v_rest - v) / tau + i_inj) * dt
        if v >= v_th {
            spikes = spikes + 1
            v = v_rest
        }
    }
    printf("spikes=%d\n", spikes)
    return 0
}
```

### F-I curve sample (browser)

```flow
function spikes_for_current(i_inj: f64) -> i32 {
    let tau: f64 = 10.0
    let v_rest: f64 = -70.0
    let v_th: f64 = -55.0
    let dt: f64 = 0.1
    let mut v: f64 = v_rest
    let mut spikes: i32 = 0
    for k in 0 to 500 {
        v = v + ((v_rest - v) / tau + i_inj) * dt
        if v >= v_th {
            spikes = spikes + 1
            v = v_rest
        }
    }
    return spikes
}

function main() -> i32 {
    printf("I=0.5 -> %d\n", spikes_for_current(0.5))
    printf("I=1.5 -> %d\n", spikes_for_current(1.5))
    printf("I=3.0 -> %d\n", spikes_for_current(3.0))
    return 0
}
```

### Synaptic PSP bump (browser)

```flow
function main() -> i32 {
    let mut g: f64 = 0.0
    let tau_syn: f64 = 5.0
    let dt: f64 = 0.1
    g = 1.0
    for k in 0 to 50 {
        g = g - (g / tau_syn) * dt
    }
    printf("g=%f\n", g)
    return 0
}
```

## Next

- [evolution.md](evolution.md) — `flow` / `field` foundations
- [gfx-basics.md](gfx-basics.md) — windowed demos
- [game-ai.md](game-ai.md) · [ml-on-macbook.md](ml-on-macbook.md)
