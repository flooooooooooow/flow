# 18. A complete instrument

The final example joins several parts of Flow in a small instrument. Separate
modules sample a signal, estimate its state, apply control, record diagnostics,
and draw a native display.

## 18.1 Architecture

```text
device input
    -> callback-domain sample buffer
    -> DSP and estimator
    -> controller
    -> bounded actuator command
    -> telemetry channel
    -> frame-domain display and recorder
```

The real-time path owns no heap allocation, file I/O, GPU submission, or
blocking lock. Telemetry crosses into a non-real-time consumer through a
preallocated channel or lock-free ring.

## 18.2 Model

```flow
unit Second
unit Position
unit Velocity = Position / Second

flow Plant {
    state position: f64 = 0.0
    state velocity: f64 = 0.0
    input command: f64
    output measured: f64 = position

    param damping: f64 = 0.2
    param stiffness: f64 = 4.0

    position evolves as velocity
    velocity evolves as command - damping * velocity - stiffness * position

    always {
        position < 10.0
        position > -10.0
    }
}
```

The flow supplies a simulation plant. A hardware build replaces the input and
actuator boundary without changing estimator and control functions.

## 18.3 Controller

```text
struct Controller {
    kp: f64,
    kd: f64,
    limit: f64
}

function control(c: Controller, target: f64, position: f64, velocity: f64) -> f64 {
    let raw: f64 = c.kp * (target - position) - c.kd * velocity
    return raw |> clamp(-c.limit, _, c.limit)
}
```

The pure controller is independently testable. A `represent linear` model can
be analysed for controllability and used to derive an LQR alternative.

## 18.4 Real-time boundary

```text
@lifetime(callback)
@rt_safe
function process_block(
    input: span<f32>,
    output: span<mut f32>,
    state: ptr<InstrumentState>
) -> void {
    for i in 0 to input.len {
        output[i] = process_sample(input[i], state)
    }
}
```

All state and buffers are allocated during setup. The callback performs
bounded indexed work only.

## 18.5 Effects at the outer boundary

```flow
effect InstrumentLog {
    sample(value: f64) -> void,
    fault(code: i32) -> void,
}
```

Simulation installs a deterministic recorder. A desktop build installs a file
or console capability outside the callback. A test installs an in-memory
capability and checks the resulting sequence.

## 18.6 Display and recording

The display consumes telemetry at frame rate, draws the latest state and a
bounded history, and can be captured with `flow record`. It never reads
callback-owned scratch storage after the callback ends; transferred values are
copied into frame or session storage.

## 18.7 Project layout

```text
instrument/
├── flow.toml
├── src/
│   ├── main.flow
│   ├── model.flow
│   ├── controller.flow
│   ├── callback.flow
│   ├── telemetry.flow
│   └── display.flow
├── tests/
│   ├── controller.flow
│   ├── convergence.flow
│   └── callback_safety.flow
└── native/
    └── device_bridge.c
```

Modules export only the required names. The manifest records native sources
and dependencies; the lock file fixes dependency revisions.

## 18.8 Verification sequence

1. Unit-test pure controller and estimator functions.
2. Compare simulation against an analytic or independent reference.
3. Repeat with smaller integration steps and report convergence.
4. Compile the callback under `@rt_safe` and lifetime-domain checks.
5. Run UBSan, ASan, and TSan on their applicable configurations.
6. Inspect the declarative compilation plan.
7. Compile with the safety profile and scan generated C.
8. Record a deterministic display run.
9. Measure callback duration and missed deadlines on the target machine.
10. Preserve version, flags, manifest, lock file, generated C, and results.

## 18.9 Target variants

| Variant | Components |
|---|---|
| command-line simulation | model, controller, table output |
| native instrument | device bridge, callback, display |
| browser demonstration | WASM model, WebGPU display, browser-safe I/O |
| Python analysis package | exported model/controller functions in a wheel |
| certified deployment candidate | C backend, safety profile, target evidence |

Each variant uses a documented subset of the language. Backend selection is an
architectural decision, not a final build flag applied after implementation.

## 18.10 Completion criterion

The instrument is complete when its interfaces, numeric assumptions, memory
ownership, lifetime domains, effect requirements, target support, failure
modes, and validation evidence are all explicit. A successful demonstration is
necessary but not sufficient.

Continue with the [feature coverage index](appendix-b-feature-coverage.md).
