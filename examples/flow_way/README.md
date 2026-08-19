# Solve It the Flow Way

This directory is a problem-first gallery for Flow's highest-level idioms.

The goal is not to prove that Flow can reproduce ordinary imperative programs. The goal is to choose problems whose structure is directly represented by the language, then make that representation the expected solution.

For this corpus, a numerically correct low-level solution is not automatically a good Flow solution. If the problem is naturally a pipeline, effect, hybrid system, field, real-time callback, or connected dynamical system, the example should use that abstraction rather than manually rebuilding it from loops, flags, dependency objects, or bookkeeping.

The executable examples in this directory are intentionally small. Larger examples link to the canonical programs elsewhere in the repository rather than duplicating them.

## Start here

| Problem | Flow-native form | Run |
|---|---|---|
| Calibrate a sensor through offset, gain, and saturation | pipeline `|>` + `_` placeholder | `./flow run examples/flow_way/sensor_calibration.flow` |
| Let one algorithm use production or silent telemetry without dependency plumbing | effect row + capabilities + scoped handlers | `./flow run examples/flow_way/swappable_telemetry.flow` |
| Compute several named views of one value | typed pipeline fork | `./flow run examples/basics/pipeline_fork.flow` |
| Route a value through a mode-selected processing topology | `|> choose` | `./flow run examples/basics/pipeline_choose.flow` |
| Run a sampled thermostat over continuous room dynamics | `flow` + `evolves as` + `every` + `becomes` | `./flow run examples/evolution/thermostat_evolves.flow` |
| Write a real-time audio callback with checked constraints | `@rt_safe` + lifetime domain + mutable span | `./flow run examples/audio/rt_safe_callback.flow` |
| Move data between concurrent workers | channels instead of shared-memory plumbing | `./flow run examples/concurrency/channels.flow` |
| Swap implementations of logging, time, storage, notification, or async operations | algebraic effects + capabilities | `./flow run examples/effects/showcase.flow` |

## 1. Sensor calibration as a pipeline

**Problem:** a raw sensor sample must have an offset removed, be scaled, then be saturated to a legal output range.

The arithmetic is trivial. The useful part is that the source value visibly travels through the transformation topology:

```flow
function calibrate(raw: i32) -> i32 {
    return raw
        |> subtract_offset(10)
        |> multiply(2)
        |> clamp(0, _, 100)
}
```

The `_` placeholder says exactly where the piped value belongs when it is not naturally the first argument.

Run [sensor_calibration.flow](sensor_calibration.flow).

The non-Flow-way version for this gallery would be a pile of temporary variables or a nested expression that erases the pipeline structure.

## 2. Telemetry as an environmental effect

**Problem:** a control algorithm needs telemetry in production, but deterministic tests should be able to silence or replace it. The control algorithm should not receive a logger object, callback, Boolean flag, or environment bundle.

The algorithm names what it may do:

```flow
function control_step(sample: i32) -> i32 with Telemetry {
    Telemetry.emit("control step")
    return sample * 2
}
```

The application chooses what `Telemetry` means for a scope:

```flow
handle Telemetry with ConsoleTelemetry {
    production = control_step(21)
}

handle Telemetry with QuietTelemetry {
    test = control_step(21)
}
```

Run [swappable_telemetry.flow](swappable_telemetry.flow).

The non-Flow-way version for this gallery would thread a logger dependency or `quiet` flag through the algorithm and every caller above it.

## 3. One value, several named computations

**Problem:** calculate several independent properties of one source value and collect them into one typed result.

Use the existing [pipeline fork example](../basics/pipeline_fork.flow):

```flow
let s: Stats = n |> Stats {
    doubled = twice,
    squared = square,
    plus_ten = add(_, 10),
}
```

This keeps the fan-out topology in the expression instead of scattering three unrelated assignments through the surrounding block.

## 4. A topology selected by state

**Problem:** the processing route itself changes according to a mode, then the selected route feeds the rest of the pipeline.

Use the existing [pipeline choose example](../basics/pipeline_choose.flow):

```flow
return x
    |> choose m.tag {
        Mode_Double => double,
        Mode_Triple => triple,
    }
    |> double
```

The non-Flow-way version is an `if` ladder that performs the routing outside the pipeline and then manually reconnects the result.

## 5. Continuous plant, sampled controller

**Problem:** room temperature evolves continuously, while a thermostat samples it every 100 ms and changes a discrete heater command.

The canonical [thermostat example](../evolution/thermostat_evolves.flow) expresses both time scales in the model:

```flow
flow Thermostat {
    state temperature : f64 = 12.0
    state heater      : f64 = 1.0

    solver { dt 1 ms  method euler }

    temperature evolves as (ambient - temperature) * leak + heater * power

    every 100 ms {
        heater becomes bang(temperature, heater, low, high)
    }
}
```

The main program advances the generated model; it does not own the thermostat's sampling schedule.

For this gallery, manually writing a timestep loop that also keeps a counter for the 100 ms controller is the wrong abstraction even if it produces the same numbers.

## 6. Real-time audio as a checked contract

**Problem:** process an audio-sized block while making it impossible for the callback call graph to allocate or perform other forbidden real-time work.

Start from [rt_safe_callback.flow](../audio/rt_safe_callback.flow). The important forms are `@rt_safe`, callback lifetime domains, and mutable spans. The contract belongs in the program rather than in a comment saying "do not allocate here".

## 7. Concurrency by communication

**Problem:** move ordered data between producers and consumers without exposing a shared array and synchronisation protocol.

Start from [channels.flow](../concurrency/channels.flow) and the concurrency challenges in the Flow Book. Higher-level problems should progress to buffered channels, `select2` / `select4`, and swappable async schedulers rather than rebuilding sleep-based polling or manual condition-variable protocols.

## 8. Effects as architecture, not logging sugar

The complete [effects showcase](../effects/showcase.flow) demonstrates the larger pattern: business logic names effect interfaces and enclosing scopes select implementations for logging, clocks, inventory, notifications, configuration, storage, and async behaviour.

That makes effects useful for real systems examples such as:

```text
Radio           -> RealRadio / SimulatedRadio / RecordedRadio / FaultInjectingRadio
Clock           -> WallClock / FrozenClock
Storage         -> SQLite / InMemory / Replay
Scheduler       -> NativeAsync / SimulatedAsync
Telemetry       -> Console / RingBuffer / Silent
```

The interesting problem is not "can Flow print a log line?" It is whether the same algorithm can execute in several worlds without changing its dependency surface.

## Challenge progression

The repository already contains a 36-problem Flow-specific challenge series in [Chapter 19](../../docs/book/19-coding-challenge-series.md), backed by machine-readable rules in [`challenges/flow-specific/catalog.json`](../../challenges/flow-specific/catalog.json).

That challenge system is the enforcement layer for this gallery. It can require a Flow-native form and forbid the low-level shortcut. The intended progression is:

| Stage | Representative problem | Required Flow idea |
|---|---|---|
| Dataflow | sensor calibration | pipeline + placeholder |
| Fan-out | derived statistics | typed fork |
| Dynamic topology | mode-selected processing | `choose` |
| Domain types | physical calculation | distinct types + units |
| Native safety | audio callback | spans + lifetimes + `@rt_safe` |
| Environment | replaceable service | effects + capability handlers |
| Concurrency | first-ready producer | channels + select |
| Hybrid dynamics | thermostat / bouncing ball | `flow`, events, sampled updates |
| Safety | bounded evolving state | `always` invariant |
| Composition | plant + controller | child flows + `connect` |
| Control analysis | state-space health | `dsys` analysis requests |
| Fields | heat equation | `field` + `laplacian` + `boundary` |

## Rule for additions

A new entry belongs here when the highest-level Flow construct captures something important about the problem that ordinary imperative syntax would make the programmer reconstruct manually.

A good entry therefore has four things: a real problem statement, the Flow-native abstraction, a runnable self-check, and a clearly named low-level shortcut that the corresponding challenge should reject.

Do not add examples merely because they are short or because Flow can express them. Add examples where the language changes the shape of the solution.
