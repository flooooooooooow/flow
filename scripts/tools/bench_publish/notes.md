## Notes on Epic #727

- **Flow beats CPython** on every kernel here. This table is one slice of #727: steady-state CPU runtime for five kernels. It excludes process startup, compile-to-first-result, memory and allocation, FFI, compiler throughput, multicore and accelerator scaling, text and I/O, and the flow-scikit estimator suite, so it does not show that the epic is met.
- **Flow trails hand-written C** on `nbody` by a noticeable margin.
  - **Cause**: Flow emits externally visible functions, preventing clang from specializing the pair loop for the constant body count at the call site (which the hand-written C can do via static).
  - **Tracker**: This gap points at sub-issue #739/#751 (scalar inner loops) and #740 for resolution.

## Notes

- nbody is the one benchmark where the Flow binary trails hand C by
  more than noise. The arithmetic in the generated C is identical.
  The hand-written C declares its functions static, which lets clang
  specialize the pair loop for the constant body count at the call
  site. Flow emits externally visible functions, which blocks that
  specialization. Two manual experiments support this: adding static
  to the generated functions moved Flow into C's range, and removing
  static from the hand C moved C into Flow's range.
