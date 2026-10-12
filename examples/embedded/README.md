# Embedded RT

This directory contains examples of using Flow for embedded systems and hard real-time applications.
Flow provides the `@rt_safe` annotation to enforce that critical paths do not allocate on the heap or block on OS locks.

## `rt_pid_controller.flow`

A simple PID controller implementation demonstrating how to build a hard real-time control loop.
The `pid_step` function is marked `@rt_safe`, which mathematically guarantees that the compiler will reject any heap allocations or blocking calls within it.
