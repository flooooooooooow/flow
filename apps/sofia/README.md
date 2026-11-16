# Flow-native Sofia-class simulation application

This is an independent scientific-computing application under development
for [Flow](https://github.com/flooooooooooow/flow). It does not contain
Fermioniq's Sofia engine or claim complete numerical parity.

`tracers.flow` implements a caller-owned 2D particle ensemble over
cell-centred shallow-water depth and momentum arrays. Each particle
moves under midpoint RK2 with a bilinear interpolation of conserved depth
and momenta, converting to depth-averaged velocity only after interpolation.
Dry or out-of-domain particles deactivate and keep their last valid coordinates.
The routine has no fluid back-reaction, particle collisions, sediment,
particle diffusion, synchronization with an evolving SWE solver or GIS I/O.

This is an application-level prototype rather than a frozen standard-library
API. A final library location and API should follow explicit semantic review
of the Sofia-class field model (issue #1650).

```text
./flow run tests/lang/test_sofia_passive_tracers.flow
./flow run examples/science/sofia/waal_tracer_toy.flow
```

Before reproducing Fermioniq's Waal benchmark (#1651), this needs
coordinate/datum and geometry ingestion, conservative SWE inflow and outflow,
tracer release schedules and reference validation. The toy uses synthetic
uniform velocities and metres, not the Waal bathymetry or 10,165 m^3/s
inflow. A rendering of these particles must never be mislabelled as the
published river simulation.
