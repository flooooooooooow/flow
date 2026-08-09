# RF / SDR beachhead examples (physical-systems W0)
#
# Architecture: docs/vision/physical-systems.md
# Stdlib:      lib/stdlib/rf.flow

| File | Intent | Expected |
|------|--------|----------|
| `receiver_pipeline.flow` | Quantity suffixes, RF algebra, IQ, rate-typed `\|>`, RT attrs | `./flow run` exit 0 |
| `rate_mismatch.flow` | Cross-rate add without resample | typecheck **fails** |
