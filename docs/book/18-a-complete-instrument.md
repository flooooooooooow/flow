# 18. A complete instrument

The final example joins several parts of Flow in a small instrument. Separate modules sample a signal, estimate its state, apply control, record diagnostics, and draw a native display. Every `flow` block in this chapter is compiler-checked in CI.

## 18.1 Architecture

The data path is: device input → callback-domain sample buffer → DSP/estimator → controller → bounded actuator command → telemetry → frame-domain display/recorder. The real-time path owns no heap allocation, file I/O, GPU submission, or blocking lock.

## 18.2 Model

```flow
flow InstrumentPlant {
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

A hardware build can replace the plant boundary without changing pure estimator/control functions.

## 18.3 Controller

```flow
struct Controller {
    kp: f64,
    kd: f64,
    limit: f64
}

function clamp_command(value: f64, limit: f64) -> f64 {
    if value < -limit { return -limit }
    if value > limit { return limit }
    return value
}

function control(c: Controller, target: f64, position: f64, velocity: f64) -> f64 {
    let raw: f64 = c.kp * (target - position) - c.kd * velocity
    return clamp_command(raw, c.limit)
}
```

The controller is pure and independently testable.

## 18.4 Real-time boundary

```flow
struct InstrumentState {
    gain: f32
}

@rt_safe
function process_sample(sample: f32, state: ptr<InstrumentState>) -> f32 {
    return sample * state.gain
}

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

All state and buffers are allocated during setup. The callback performs bounded indexed work only.

## 18.5 Effects at the outer boundary

```flow
effect InstrumentLog {
    sample(value: f64) -> void,
    fault(code: i32) -> void,
}
```

Simulation can install a deterministic recorder, a desktop build can install a file/console capability outside the callback, and tests can install an in-memory capability.

## 18.6 Display and recording

The display consumes copied telemetry at frame rate, draws current state plus a bounded history, and can be captured with `flow record`. It never retains callback-owned scratch storage past the callback lifetime.

## 18.7 Project layout

A realistic project splits `main`, model, controller, callback, telemetry, and display modules, with separate tests and any native device bridge. Modules export only required names and the manifest/lock file capture native sources and dependencies.

## 18.8 Verification sequence

Unit-test pure controller/estimator functions; compare simulation with a reference; run time-step refinement; compile callback paths under RT/lifetime checks; use applicable sanitizers; inspect declarative plans; compile with safety profile; record deterministic output; measure target callback duration; preserve versions, flags, lock data, generated C, and results.

## 18.9 Target variants

The same architecture can support command-line simulation, a native instrument, browser/Wasm demonstration, Python analysis package, or a safety-profile C deployment candidate. Each target should name the language/runtime subset it relies on.

## 18.10 Completion criterion

The instrument is complete when interfaces, numeric assumptions, ownership, lifetime domains, effect requirements, target support, failure modes, and validation evidence are explicit. A successful demo alone is insufficient.

Continue with the [feature coverage index](appendix-b-feature-coverage.md).
