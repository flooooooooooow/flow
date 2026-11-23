# Held-out agent selection evaluation

This is a quality gate for FM-006 and FM-055. Evaluations are *tasks*, not instructions to introduce non-existent syntax. A model may produce code, but success requires compiling or showing honest unsupported classification against the pinned compiler. Keep the held-out prompts distinct from any explanatory training examples.

Each case grades (A) mathematical/architectural classification, (B) correct supported Flow pattern, (C) identified limitations, (D) reproducible tests and (E) avoiding unnecessary advanced constructs. Score selection and overreach separately.

| Case | Task given to an agent without syntax hints | Expected idiom and caution |
| --- | --- | --- |
| E01 | Model a braking vehicle with distance, speed and constant deceleration. | Dimensioned physical data and genuine evolving state. Do not claim unsupported derivative checks or silently erase units. Verify analytic stopping time/distance. |
| E02 | Simulate an ideal voltage source and resistors in a nodal circuit. | Algebraic/MNA approach, not an invented `evolves` equation for a non-state node. Verify KCL and power. |
| E03 | Control a thermostat every 100 ms while plant temperature changes continuously. | Sampled `every` and `becomes` with continuous evolution. Verify timing and hysteresis. |
| E04 | Swap telemetry sink between deterministic test and production without altering a pure solver. | Scoped effect/capability at environment boundary; keep core pure and local state as data. |
| E05 | Generate a fourth-order Runge-Kutta reference to validate the compiler-generated integrator. | Keep explicit RK4 as independent oracle, not an automatic anti-idiom. |
| E06 | Create a matrix pipeline that forks two pure analyses, then chooses one by an enum. | Valid pipeline/fork/choose with one source evaluation; avoid speculative compiler fusion or unproven future syntax. |
| E07 | Write a real-time audio buffer processor with no hidden allocation or blocking. | `span`, `@rt_safe` and call-graph testing. Distinguish measured WCET from static may-effect rules. |
| E08 | Describe a generic two-dimensional PDE and GPU solve using `field T`. | Clearly identify current limits and experimental Sofia work. Do not claim a general PDE compiler surface merely from a 1D example. |
| E09 | Express a mathematical formula as a pure typed Flow function with dimensional terms. | Use only accepted function/equation constructs checked against compiler fixtures. Do not confuse math-prose rendering and executable AST. |
| E10 | Sum floating-point kinetic energies reproducibly at optimization level O3. | Respect ordered reduction semantics and issue #1694, inspect generated code and compare numeric reference; do not assume parallel map/reduce equivalent. |
| E11 | Model a spring network using pure equations, then linearize and design an LQR. | Confirm `represent linear` explicit coefficients, supported `dsys` sizing, linearization limits and control oracle. |
| E12 | Change a stateless local data stack into a capability to eliminate a mutable variable. | **Reject the premise.** Local owned state should stay ordinary data; effects are for environment-dependent policy. |

## Passing criteria and method

An evaluator pins a Flow SHA, source prompt, agent version, backend/toolchain, actual generated sources and command outputs. Compile and run every implementable positive case. Evaluate negative cases for explicit rejection or supported alternative, not fabricated code. Record elapsed effort and reviewer interventions. Require the candidate agent instructions to improve valid first-pass idiom choice *without* increasing unsafe rewrites, unsupported-syntax hallucinations, fake CI results or capricious overuse of features.

Do not use these prompts as the sole training material and then call a retest independent. Add held-out domain variants and adversarial constraints (pure vs effectful, ODE vs DAE, dimensioned vs normalized, reference vs deployment). Run the baseline before modifying guidance; compare against the same version pin after changes. Provenance of exact outputs matters more than subjective grades.
