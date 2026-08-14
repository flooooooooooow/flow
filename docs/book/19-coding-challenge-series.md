# 19. Flow-specific coding challenge series

These challenges test the parts of Flow that do not reduce to ordinary
imperative syntax. A correct numeric answer is not enough. Each submission must
use the language form named by the challenge.

The series contains 36 problems in eight tracks. Early problems take less than
an hour. Later problems may take several sessions and need a platform runtime.

## 19.1 Checking a submission

List the challenge identifiers:

```bash
python3 challenges/flow-specific/check.py list
```

Check one file:

```bash
python3 challenges/flow-specific/check.py check F01 answer.flow
```

The checker performs two tests:

1. It removes Flow line comments and checks the remaining source for required
   and forbidden forms.
2. It compiles and runs the file with the host and environment assigned to the
   challenge.

A passing program returns zero. Printed output may explain the result, but the
exit status decides whether the run passed.

Target-specific challenges can be checked without launching their runtime:

```bash
python3 challenges/flow-specific/check.py check F33 kernel.flow --syntax-only
```

The machine-readable rules are stored in
[`challenges/flow-specific/catalog.json`](../../challenges/flow-specific/catalog.json).
Static syntax checks cannot prove that a construct does the main work. A course
runner should add hidden behavioural tests when submissions are graded.

## 19.2 Difficulty and scoring

| Mark | Expected work | Base points |
|---|---|---|
| `*` | one construct and a small self-test | 10 |
| `**` | two or three connected rules | 20 |
| `***` | resource, runtime, or numerical reasoning | 35 |
| `****` | several modules or a domain-specific compiler feature | 55 |
| `*****` | capstone design and evidence | 100 |

Award the base points only when the checker passes. Optional points may be
given for clear failure codes, extra tests, measured error, and a short design
note. Code length and cleverness do not earn points.

## 19.3 Track A: data flow and decisions

### F01. Pipeline Calibration `*`

Start with a raw sensor value. Subtract an offset, multiply by a scale, and
clamp the result to `[0, 100]`.

- Required: a `|>` chain and the `_` placeholder in the clamp call.
- Forbidden shortcut: writing the whole calculation as nested calls.
- Pass: test raw values below, inside, and above the accepted range. Return a
  different nonzero code for each failed case.
- Check: `python3 challenges/flow-specific/check.py check F01 answer.flow`

### F02. Forked Statistics `**`

Send one integer into a typed fork. Produce a record containing its square,
absolute value, and distance from `100`.

- Required: `value |> Stats { ... }` with three named branches.
- Forbidden shortcut: constructing `Stats` from three unrelated statements.
- Pass: verify all fields for `-12`, `0`, and `25`.
- Check: use challenge `F02`.

### F03. Choose the Route `**`

Define three processing modes: double, square, and negate. Select one branch
from an enum tag, then pass the selected result through a final normalisation
stage.

- Required: `|> choose`, enum arms, and another pipeline stage after `choose`.
- Forbidden shortcut: an `if` chain in the routing function.
- Pass: each mode must produce the expected normalised value.
- Check: use challenge `F03`.

### F04. Declarative Leaderboard `**`

Order player records by descending score and then ascending name. Locate one
target player in the ordered result.

- Required: `sortBy`, `desc .score`, a second field order, and `find`.
- Forbidden shortcut: a handwritten swap loop.
- Pass: verify the first, middle, and final record and the target index.
- Check: use challenge `F04`.

### F05. Pattern Decoder `**`

Decode integer message classes with `match`. Treat `1 | 2 | 3` as small
control messages, bind and guard negative values, and provide a fallback.

- Required: alternation, a guarded binding, and `_` or `default`.
- Forbidden shortcut: replacing the match with a chain of `if` statements.
- Pass: test a negative value, every alternation value, and one fallback value.
- Check: use challenge `F05`.

### F06. Snapshot Closure `**`

Create a closure while `base` equals `10`, change `base` to `100`, and call the
closure through a higher-order function.

- Required: a typed closure variable and a captured local.
- Forbidden shortcut: passing `base` as an ordinary function argument.
- Pass: the closure must still use `10` and return `15` for input `5`.
- Reference shape: [the book closure example](../../examples/book/11_closure_snapshot.flow).
- Check: use challenge `F06`.

## 19.4 Track B: types that carry meaning

### F07. Nominal Identifier Wall `*`

Define `UserId` and `DeviceId` as distinct types over `i64`. Store and print
both identifiers without allowing them to be passed to the wrong lookup
function.

- Required: two `distinct type` declarations and explicit `as` conversions at
  the input boundary.
- Forbidden shortcut: aliases made with `type`.
- Pass: both valid lookups return the expected records. Keep one rejected call
  in a separate `.rejected.flow` note, not in the submitted file.
- Check: use challenge `F07`.

### F08. Dimensional Flight Plan `**`

Calculate travel time from distance and velocity, then calculate acceleration
from a change in velocity.

- Required: two base units, at least two derived units, and unit-typed
  bindings.
- Forbidden shortcut: using plain `f64` for every intermediate value.
- Pass: check one travel time and one acceleration. Also document one
  expression that the unit checker rejects.
- Check: use challenge `F08`.

### F09. Generic Sample Window `**`

Implement a generic `Window<T>` and a generic function that returns its first
element or supplied fallback. Instantiate the design for `i32` and `f64`.

- Required: a generic struct, a generic function, and explicit `<i32>` and
  `<f64>` instantiations.
- Forbidden shortcut: two copied structs with type suffixes.
- Pass: verify filled and empty windows for both element types.
- Check: use challenge `F09`.

### F10. Overloaded Normaliser `**`

Write `normalise(i32)` for integer percentages and `normalise(f64)` for values
already near `[0, 1]`.

- Required: two functions with the same source name and different parameter
  types.
- Forbidden shortcut: names such as `normalise_i32` and `normalise_f64`.
- Pass: call both overloads and verify the selected behaviour.
- Check: use challenge `F10`.

## 19.5 Track C: memory and native boundaries

### F11. Deferred Buffer Owner `**`

Allocate eight integers, fill them, calculate their sum, and release the
buffer on every exit.

- Required: `calloc` or `malloc`, a null check, and `defer free(...)`.
- Forbidden shortcut: a fixed stack array.
- Pass: verify the sum and include an early failure after allocation.
- Reference shape: [the memory example](../../examples/book/09_memory_cleanup.flow).
- Check: use challenge `F11`.

### F12. Borrowed Signal Window `**`

Write one function that reads an immutable `span<f32>` and another that clears
a `span<mut f32>`. Call them with a slice from the middle of a fixed array.

- Required: immutable and mutable spans plus a `start..end` slice.
- Forbidden shortcut: raw pointer parameters.
- Pass: prove that only the selected region was cleared.
- Check: use challenge `F12`.

### F13. Lifetime Domain Ladder `***`

Split a small renderer into callback, frame, and session functions. Arrange the
calls so that shorter-lived work never escapes into longer-lived storage.

- Required: `@lifetime(callback)`, `@lifetime(frame)`, and
  `@lifetime(session)`.
- Forbidden shortcut: removing an annotation to silence the checker.
- Pass: the valid file compiles. Supply a separate rejected example that tries
  to return a callback span into session storage.
- Check: use challenge `F13`.

### F14. Real-Time Gain Stage `***`

Apply a gain and hard limit to an audio-sized block. Setup may allocate, but
the processing function may not.

- Required: `@rt_safe`, `@lifetime(callback)`, and a mutable output span.
- Forbidden shortcut: allocation, file I/O, logging, or a blocking lock in the
  checked call graph.
- Pass: compile the callback and test the same arithmetic in a non-real-time
  wrapper.
- Check: use challenge `F14`.

### F15. Opaque C Handle `***`

Model a C resource whose fields are private to C. Create, query, and destroy it
through declared functions.

- Required: `@cInclude`, `extern type`, and `ptr<OpaqueType>`.
- Forbidden shortcut: copying the private C struct layout into Flow.
- Pass: a create/query/destroy cycle succeeds, including a null failure case.
- Check: use challenge `F15`. A course package must provide the small C header
  and implementation used by this problem.

### F16. Dynamic C Callback `****`

Open a system library, find a numeric function with `dlsym`, cast the symbol to
`cfn`, and call it.

- Required: `dlsym`, `cfn(...) -> R`, and an explicit cast to that type.
- Forbidden shortcut: a direct extern declaration for the target function.
- Pass: compare the dynamic result with a known value and close the library.
- Check: use challenge `F16`.

## 19.6 Track D: effects and concurrency

### F17. Replaceable Logger `**`

Declare one logging effect and implement console and quiet capabilities. Run
the same worker under each handler.

- Required: an `effect`, two `capability` blocks, and `handle ... with ...`.
- Forbidden shortcut: passing a Boolean `quiet` flag into the worker.
- Pass: the worker returns the same result under both handlers. Only the
  console run prints a message.
- Check: use challenge `F17`.

### F18. Strict Effect Row `***`

Create a parser that reports a warning effect. Record the effect in its
function type and install a handler at the application boundary.

- Required: a `with EffectName` row and a matching handler.
- Forbidden shortcut: relying on default unhandled-effect behaviour.
- Pass: run with `FLOW_STRICT_EFFECTS=1`; no operation may be uncovered.
- Check: use challenge `F18`. The checker sets strict-effects mode.

### F19. Parallel Image Row `**`

Transform one row of pixels in parallel. Each iteration reads one input index
and writes the matching output index. Reduce a checksum afterwards.

- Required: `parallel for` and disjoint indexed writes.
- Forbidden shortcut: updating a shared checksum inside the parallel loop.
- Pass: compare every output pixel and the final checksum with a serial
  reference.
- Reference shape: [the parallel example](../../examples/book/12_parallel_transform.flow).
- Check: use challenge `F19`.

### F20. Bounded Producer Consumer `***`

Send a known integer sequence through a buffered channel. The consumer checks
the order and total, then observes closure.

- Required: the concurrent library, channel send, receive, close, and destroy
  operations.
- Forbidden shortcut: sharing the producer array directly with the consumer.
- Pass: every value arrives once, in channel order, and native resources are
  destroyed.
- Check: use challenge `F20`.

### F21. First Ready Channel `****`

Wait on two producers and consume whichever channel becomes ready first.
Include a nonblocking path for the case where neither is ready.

- Required: `select2` or `select4` and a try/default form.
- Forbidden shortcut: sleep-based polling.
- Pass: test left-first, right-first, and neither-ready cases.
- Check: use challenge `F21`.

### F22. Swappable Async Scheduler `****`

Write one operation with the `Async` effect. Run it first with the deterministic
simulated handler and then with a native async handler supported by the host.

- Required: the async library, an Async effect row, an Async operation, and a
  handler selected by `handle`.
- Forbidden shortcut: invented `async` or `await` syntax.
- Pass: both handlers produce the same result. The simulated run must be
  deterministic.
- Check: use challenge `F22`.

## 19.7 Track E: evolution and hybrid systems

### F23. Declared Exponential Decay `**`

Model `dy/dt = -ky` with a `flow` declaration and compare the generated stepper
with the analytic value at one second.

- Required: `flow`, `state`, `param`, and `evolves as`.
- Forbidden shortcut: implementing the main model as a manual Euler loop.
- Pass: report the error and keep it within a stated tolerance.
- Check: use challenge `F23`.

### F24. Solver Selection Study `***`

Run the same smooth model with an RK4 solver declaration at two step sizes.
Measure the error against a reference.

- Required: `solver`, a time unit on `dt`, `method rk4`, and a flow equation.
- Forbidden shortcut: calling the handwritten RK4 function from Chapter 13.
- Pass: the smaller step must not produce a larger error.
- Check: use challenge `F24`.

### F25. Sampled Thermostat `***`

Integrate room temperature continuously and update heater command every
`100 ms`.

- Required: `evolves as`, `every`, and `becomes`.
- Forbidden shortcut: treating the controller as a continuous derivative.
- Pass: temperature remains within the stated band after warm-up, and command
  changes occur only at sample times.
- Check: use challenge `F25`.

### F26. Bouncing Ball Reset `***`

Model height and velocity under gravity. Reverse and scale velocity when height
reaches the floor.

- Required: two continuous equations, `when ... reaches`, and two `becomes`
  assignments in the event.
- Forbidden shortcut: clamping height in an ordinary loop outside the flow.
- Pass: the second apex is lower than the first by the expected restitution
  relation.
- Check: use challenge `F26`.

### F27. Runtime Invariant Fence `**`

Add upper and lower state limits to an evolving angle or position.

- Required: an `always` block with both comparisons.
- Forbidden shortcut: checking the limit only after the simulation ends.
- Pass: one safe run completes; a separate rejected run crosses the bound and
  triggers the invariant.
- Check: use challenge `F27` for the safe file.

### F28. Connected Plant and Controller `****`

Declare a plant flow, a controller flow, and a parent flow that connects them.
Break feedback with controller state.

- Required: three flow declarations, two child fields, a `connect` block, and
  connections in both directions.
- Forbidden shortcut: calling the plant and controller manually from `main`.
- Pass: a step input moves the plant towards its target without creating an
  algebraic loop.
- Check: use challenge `F28`.

## 19.8 Track F: dynamics and fields

### F29. Linearised Pendulum `****`

Attach a local linear model to a nonlinear pendulum near its downward
equilibrium.

- Required: `represent linear`, `at (...)`, inputs, outputs, dimensions, and
  `A`, `B`, `C` coefficients.
- Forbidden shortcut: performing an unstated numerical Jacobian in test code.
- Pass: compare the linear and nonlinear derivatives for a small displacement
  and state the range where the approximation is accepted.
- Check: use challenge `F29`.

### F30. State-Space Health Report `****`

Declare a two-state plant and request controllability, observability, and
spectral information.

- Required: `dsys`, `sense on`, and all three analysis requests.
- Forbidden shortcut: hard-coding the expected Boolean results.
- Pass: verify the report for one controllable system and document a changed
  matrix that loses controllability.
- Check: use challenge `F30`.

### F31. Stable Heat Field `****`

Model a one-dimensional heat field with fixed endpoint temperatures.

- Required: `field`, `laplacian`, and `boundary`.
- Forbidden shortcut: a handwritten neighbour stencil in the submitted model.
- Pass: use a stable step ratio, show that the interior approaches equilibrium,
  and compare total variation over time.
- Check: use challenge `F31`.

## 19.9 Track G: device and target code

### F32. Animated Fill Shader `***`

Draw a time-varying colour field from fragment coordinates.

- Required: `shader fill`, `frag_coord`, a time-dependent `sin` or `cos`, and a
  `vec4` return value.
- Forbidden shortcut: updating a CPU pixel buffer.
- Pass: capture frames at two times and show that at least one sampled pixel
  changes while staying in the valid colour range.
- Check: use `F32 --syntax-only`; run with `flow shader` on a supported host.

### F33. Metal SAXPY Kernel `***`

Compute `y[i] = a*x[i] + y[i]` on the GPU.

- Required: `@gpu`, `gpu_thread_id()`, a bounds guard, and an indexed pointer
  write.
- Forbidden shortcut: a CPU loop inside the device function.
- Pass: compare GPU output with a CPU reference for lengths that do and do not
  fill a complete dispatch group.
- Check: use `F33 --syntax-only`; generate Metal with `flow gpu` on macOS.

### F34. Real-Time Audio Block `****`

Process an input audio span into an output span with a stateful filter or
waveshaper.

- Required: `@rt_safe`, callback lifetime, and input/output spans.
- Forbidden shortcut: allocation, logging, file access, or blocking work in the
  callback.
- Pass: compile with the audio wrapper, run an offline impulse or step test,
  and check all output values for finiteness.
- Check: use challenge `F34`.

### F35. Stable WebAssembly Boundary `***`

Expose a small numeric function through a stable ABI and keep a native
self-test in `main`.

- Required: `@flow_api`, a WASM-compatible numeric signature, and a `main`
  test.
- Forbidden shortcut: a raw pointer in the exported signature.
- Pass: native compilation succeeds; a WASM build exports the same operation
  under the documented name.
- Check: use challenge `F35`, then run `./flow wasm answer.flow` when Emscripten
  is installed.

## 19.10 Track H: capstone

### F36. Instrument Control Capstone `*****`

Build a small simulated instrument with typed identifiers, physical units, an
evolving plant, a bounded controller, runtime limits, and replaceable
diagnostics.

- Required: a distinct identifier type, at least one unit, a `flow`, an
  `always` block, a pipeline with `_`, an effect, and a handler.
- Forbidden shortcut: placing the entire program in one untyped update loop.
- Pass: run a deterministic scenario, verify bounds and final error, return a
  distinct code for every failed condition, and record the compiler host and
  target.
- Evidence: include a time-step comparison, an effect-handler test, and one
  failure run that trips a bound.
- Check: use challenge `F36`.

## 19.11 Suggested course formats

### Twelve-week course

| Week | Work |
|---|---|
| 1 | F01, F05, F07 |
| 2 | F02, F03, F06 |
| 3 | F08, F09, F10 |
| 4 | F11, F12, F13 |
| 5 | F17, F18, F19 |
| 6 | F20, F21 or F22 |
| 7 | F23, F24 |
| 8 | F25, F26, F27 |
| 9 | F28 and F29 |
| 10 | F30 and F31 |
| 11 | one of F32 to F35 |
| 12 | F36 demonstration and review |

### Short specialist tracks

- Language design: F01 to F10, then F17 and F18.
- Systems: F11 to F22.
- Modelling and control: F23 to F31, then F36.
- Media and devices: F14, F19, F32 to F35.

## 19.12 Submission standard

Every submitted program should contain:

1. a `main` function that returns zero on success;
2. a different nonzero result for each failed check;
3. no required syntax hidden only in comments or dead examples;
4. a short header comment stating compiler host and target;
5. deterministic inputs unless the challenge explicitly studies scheduling;
6. cleanup for every owned native resource;
7. measured numeric error where an approximation is used.

The checker enforces syntax and the ordinary execution result. Review still
matters for ownership, races, numerical arguments, real-time claims, and proof
status.

Continue with the [language and command card](appendix-a-language-card.md).
