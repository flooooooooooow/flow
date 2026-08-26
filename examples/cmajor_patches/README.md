# Cmajor patch corpus

These files are patch libraries, not standalone programs. Run a compile smoke
harness from this directory with:

```bash
flow patch 808.flow
flow patch sine_synth.flow
```

The command creates disposable harness sources under `build/patches/`, synchronizes
the local `flow_audio` dependency, compiles the patch, and runs the harness.
The harness checks compilation and module resolution; it does not claim to be
a behavioral DSP oracle. Those checks belong in the corpus test matrix.

For an explicit dependency install, use:

```bash
flow sync
```
