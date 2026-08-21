# Flow runtime ABI

Flow runtime ABI version: **1**.

`runtime/ABI_VERSION` is the machine-readable ABI identifier for the runtime shipped with Flow 1.x.

The identifier does **not** turn every compiler-generated C layout or internal runtime symbol into a stable binary interface. Flow 1.0 primarily promises Stable source compatibility. The only ABI details covered by the 1.x compatibility contract are calling conventions, exported symbols, layouts and FFI-visible representations that focused documentation explicitly marks Stable and that are covered by ABI regression tests.

Compiler-internal helper names, generated temporary structs, private runtime state, backend-specific implementation details and undocumented layouts remain Internal or Experimental and may change during 1.x.

An ABI-visible surface promoted to Stable must record its representation here or in a linked focused specification and add a regression fixture before release. An incompatible change to an already Stable ABI-visible surface requires the normal deprecation/major-version process, except for the security/correctness exceptions in `STABILITY.md`.

This boundary lets Flow 1.0 make a useful C interop promise without pretending that arbitrary object files emitted by one compiler build are a permanent binary ABI for every later 1.x compiler.
