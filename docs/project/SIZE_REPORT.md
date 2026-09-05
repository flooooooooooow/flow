# Binary Size Report

Comparison baseline: Python minimum footprint (~25MB)

| Program | `.text` | `.data` | `.bss` | Unstripped | Stripped | % of Python |
|---------|---------|---------|--------|------------|----------|-------------|
| `hello_world.flow` | 71597 | 1136 | 395312 | 106168 | 80712 | 0.31% |
| `fibonacci.flow` | 71725 | 1136 | 395312 | 106200 | 80712 | 0.31% |
| `loops.flow` | 71997 | 1136 | 395312 | 110336 | 84808 | 0.32% |
