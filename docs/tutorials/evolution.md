# FLOW Tutorial: Evolution

Flow's differentiator: declare how a system **evolves**, and let the compiler
emit the integrator. This track covers the shipped `flow` / `evolves as`
syntax, hybrid events, invariants, phase portraits, and field PDEs.

> [!important] Mostly native
> `flow` blocks, `when`/`reaches`, `always`, `represent`, and `field` lower in
> the real compiler. Run every full example with `./flow run` or `./flow gfx`.
> Browser lessons below use hand-written Euler so you can still poke at the
> *math* interactively.

Prerequisites: [beginner.md](beginner.md), then [dynamics.md](dynamics.md) Part 1.

## Part 1: From hand Euler to `flow` / `evolves`

### 1.1 Hand Euler pendulum (browser)

```flow
function main() -> i32 {
    let g: f64 = 9.81
    let L: f64 = 1.0
    let damp: f64 = 0.5
    let dt: f64 = 0.01
    let mut angle: f64 = 2.0
    let mut vel: f64 = 0.0
    for k in 0 to 200 {
        let acc: f64 = 0.0 - (g / L) * angle - damp * vel
        # small-angle sin(theta)≈theta for this browser sketch
        vel = vel + acc * dt
        angle = angle + vel * dt
    }
    printf("angle=%f vel=%f\n", angle, vel)
    return 0
}
```

### 1.1b Undamped energy drift (browser)

```flow
function main() -> i32 {
    let g: f64 = 9.81
    let L: f64 = 1.0
    let dt: f64 = 0.05
    let mut th: f64 = 1.0
    let mut w: f64 = 0.0
    let e0: f64 = 0.5 * L * L * w * w + g * L * (1.0 - 0.5)  # rough
    for k in 0 to 100 {
        let acc: f64 = 0.0 - (g / L) * th
        w = w + acc * dt
        th = th + w * dt
    }
    let e1: f64 = 0.5 * L * L * w * w + g * L * th * th * 0.5
    printf("e_end=%f (Euler drifts)\n", e1)
    return 0
}
```

### 1.1c Midpoint step (browser)

```flow
function main() -> i32 {
    let dt: f64 = 0.1
    let mut y: f64 = 1.0
    for k in 0 to 10 {
        let k1: f64 = 0.0 - y
        let y_mid: f64 = y + 0.5 * dt * k1
        let k2: f64 = 0.0 - y_mid
        y = y + dt * k2
    }
    printf("y=%f\n", y)
    return 0
}
```

### 1.2 The same system as a `flow` block (native)

```flow
flow Pendulum {
    state angle    : f64 = 2.0
    state velocity : f64 = 0.0
    param gravity  : f64 = 9.81
    param length   : f64 = 1.0
    param damping  : f64 = 0.5

    angle evolves as velocity
    velocity evolves as -(gravity / length) * sin(angle) - damping * velocity
}
```

The compiler emits `Pendulum_new`, `Pendulum_step(self, dt)`, and friends.
Default integrator is explicit Euler; request RK4 with:

```flow
solver { dt 5 ms  method rk4 }
```

```bash
./flow run examples/evolution/pendulum_evolves.flow
./flow run examples/evolution/pendulum_rk4.flow
```

---

## Part 2: Hybrid events

Continuous evolution plus discrete resets:

```flow
flow Ball {
    state height   : f64 = 2.0
    state velocity : f64 = 0.0
    param gravity  : f64 = 9.81
    param restitution : f64 = 0.8

    height evolves as velocity
    velocity evolves as -gravity

    when height reaches 0.0 {
        velocity becomes -restitution * velocity
        height becomes 0.0
    }
}
```

```bash
./flow run examples/evolution/bouncing_ball_evolves.flow
```

### 2.1 Event detection sketch (browser)

```flow
function main() -> i32 {
    let mut h: f64 = 1.0
    let mut v: f64 = -2.0
    let dt: f64 = 0.05
    let mut hit: i32 = 0
    for k in 0 to 40 {
        let prev: f64 = h
        h = h + v * dt
        if prev > 0.0 {
            if h <= 0.0 {
                hit = 1
                h = 0.0
                v = 0.0 - 0.8 * v
            }
        }
    }
    printf("crossed=%d rebound_v=%f\n", hit, v)
    return 0
}
```

### 2.2 Apex ratio after bounces (browser)

```flow
function main() -> i32 {
    let e: f64 = 0.8
    let mut peak: f64 = 2.0
    for b in 0 to 5 {
        peak = peak * e * e
    }
    printf("peak=%f\n", peak)
    return 0
}
```

### 2.3 Thermostat bang-bang (browser)

```flow
function main() -> i32 {
    let mut temp: f64 = 18.0
    let mut heat: i32 = 0
    let lo: f64 = 19.0
    let hi: f64 = 21.0
    for t in 0 to 100 {
        if heat == 1 {
            temp = temp + 0.15
        } else {
            temp = temp - 0.05
        }
        if temp <= lo { heat = 1 }
        if temp >= hi { heat = 0 }
    }
    printf("temp=%f heat=%d\n", temp, heat)
    return 0
}
```

---

## Part 3: `always` invariants

Runtime-checked guarantees on evolving state. Violations abort:

```flow
flow Pendulum {
    state angle    : f64 = 2.0
    state velocity : f64 = 0.0
    param gravity  : f64 = 9.81
    param length   : f64 = 1.0
    param damping  : f64 = 0.5

    angle evolves as velocity
    velocity evolves as -(gravity / length) * sin(angle) - damping * velocity

    always {
        angle < 3.15
        angle > -3.15
    }
}
```

```bash
./flow run examples/evolution/pendulum_always.flow
```

### 3.1 Bound check pattern (browser)

```flow
function main() -> i32 {
    let mut x: f64 = 0.0
    let mut ok: i32 = 1
    for k in 0 to 20 {
        x = x + 0.2
        if x >= 3.15 {
            ok = 0
        }
        if x <= -3.15 {
            ok = 0
        }
    }
    printf("within_bounds=%d x=%f\n", ok, x)
    return 0
}
```

---

## Part 4: Phase portraits + gfx

`represent phase_portrait` auto-emits `{Name}_portrait_frame` for live trails.
The Lorenz demo draws an `(x, z)` trail each frame:

```bash
./flow gfx examples/evolution/lorenz_gfx.flow
```

![Lorenz attractor recorded from the real program](../demos/lorenz.gif)

Regenerate demos headlessly:

```bash
python3 scripts/record_demos.py lorenz
```

See also [gfx-basics.md](gfx-basics.md).

---

## Part 5: Fields / PDE

Grid fields evolve too. Heat diffusion lowers `field` + `laplacian` to an
explicit Euler step:

```flow
field T : f64[32] on Line
T evolves as laplacian(T)
boundary T { left = 20.0  right = 20.0 }
```

```bash
./flow run examples/evolution/heat_diffusion.flow
```

### 5.1 1-D diffusion sketch (browser)

```flow
function main() -> i32 {
    let n: i32 = 8
    let mut t: array<f64, 8> = [20.0, 20.0, 100.0, 20.0, 20.0, 20.0, 20.0, 20.0]
    let r: f64 = 0.4
    for step in 0 to 5 {
        let mut next: array<f64, 8> = [20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0]
        for i in 1 to 7 {
            next[i] = t[i] + r * (t[i - 1] - 2.0 * t[i] + t[i + 1])
        }
        for i in 0 to 8 {
            t[i] = next[i]
        }
    }
    printf("center=%f\n", t[2])
    return 0
}
```

### 5.2 Excess heat (browser)

```flow
function main() -> i32 {
    let ambient: f64 = 20.0
    let mut t: array<f64, 5> = [20.0, 50.0, 80.0, 50.0, 20.0]
    let r: f64 = 0.25
    let mut e0: f64 = 0.0
    for i in 0 to 5 {
        e0 = e0 + (t[i] - ambient)
    }
    for step in 0 to 10 {
        let mut n: array<f64, 5> = [20.0, 0.0, 0.0, 0.0, 20.0]
        for i in 1 to 4 {
            n[i] = t[i] + r * (t[i - 1] - 2.0 * t[i] + t[i + 1])
        }
        for i in 0 to 5 {
            t[i] = n[i]
        }
    }
    let mut e1: f64 = 0.0
    for i in 0 to 5 {
        e1 = e1 + (t[i] - ambient)
    }
    printf("e0=%f e1=%f\n", e0, e1)
    return 0
}
```

### 5.3 Unstable r (browser)

```flow
function main() -> i32 {
    let mut ok: i32 = 1
    let r: f64 = 0.6
    let mut t: array<f64, 4> = [0.0, 1.0, 0.0, 0.0]
    for step in 0 to 20 {
        let mut n: array<f64, 4> = [0.0, 0.0, 0.0, 0.0]
        for i in 1 to 3 {
            n[i] = t[i] + r * (t[i - 1] - 2.0 * t[i] + t[i + 1])
        }
        for i in 0 to 4 {
            t[i] = n[i]
            if t[i] > 10.0 { ok = 0 }
            if t[i] < -10.0 { ok = 0 }
        }
    }
    printf("stable_at_r06=%d\n", ok)
    return 0
}
```

---

## Part 6: Next

| Path | Why |
|------|-----|
| [dynamics.md](dynamics.md) | `dsys`, `sense`, GA / LQR control |
| [gfx-basics.md](gfx-basics.md) | Native windows, Tetris / 2048 / record |
| [autodiff-basics.md](autodiff-basics.md) | Differentiate through your models |
| [`examples/evolution/`](../../examples/evolution/) | Full self-checking suite |

## Reference

- [North-star grammar](../vision/north-star.md)
- [VISION.md](../../VISION.md)
- [Language Spec § evolution](../LANGUAGE_SPEC.md)
