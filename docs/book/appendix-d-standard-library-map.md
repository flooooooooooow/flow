# Appendix D. Standard-library map

The standard library is organised by responsibility. Import only the modules a
program uses; consult the generated API for exact exported names and
signatures.

| Family | Principal modules | Purpose |
|---|---|---|
| core containers | `array`, `collections`, `slice`, `option`, `result` | arrays, collection helpers, views, explicit optional/failure values |
| text and I/O | `string`, `text`, `io`, `logpkg` | strings, text processing, streams, logging |
| platform | `posix`, `process`, `sys_info`, `time`, `net` | files, processes, environment, clocks, system and network calls |
| memory | `memory`, `memory_simple`, `memory_working` | allocation, arenas, frame storage, copies |
| concurrency | `concurrent`, `async` | threads, locks, channels, effects, fibers, netpoll |
| arithmetic | `math`, `checked_arith`, `bigint`, `vec` | numeric helpers, defined overflow modes, large integers, vectors |
| linear algebra | `blas`, `tensor` | BLAS/LAPACK bindings and shaped storage |
| differentiation | `autodiff`, `autodiff_reverse` | dual numbers and reverse tape |
| machine learning | `ml_nn`, `ml_opt`, `nn`, `nn_autogen` | layers, optimisers, generated network code |
| dynamics | `dynamics` and `dynamics/*` | state space, linalg, Gramian, LQR, GA, PDE, attractors, portraits |
| graphics | `gfx`, `font`, `gif`, `ui`, `ui2d`, `ui_layout` | drawing, text, image output, widgets and layout |
| 3D and Vulkan | `render3d`, `vulkan`, `vulkan_renderer`, `vulkan_abi_renderer` | software 3D and Vulkan wrappers |
| GPU | `gpu_memory`, `gpu_kernels`, `gpu_gradients`, `gpu_sim` | Metal buffers, kernels, gradients, simulation |
| audio | `audio` and `audio/*` | device I/O, DSP, graphs, filters, synth, delays, WAV, notation |
| RF | `rf` | IQ samples and baseband operations |
| circuits | `circuit`, `spice` | modified nodal analysis and circuit input |
| numerical | `fmm2d` | fast multipole operations |
| generation | `procgen`, `automata`, `planet` | procedural generation, cellular automata, planet pipelines |
| AI | `ai` | reinforcement and evolutionary learning helpers |
| cryptography | `crypto` | platform/bundled cryptographic primitives |
| experiment/statistics | `experiment`, `psychstats` | experiment and statistical utilities |
| Python embedding | `python_embed` | embedded CPython bridge |
| UI runtime | `sdl2` | SDL2 bindings |
| SI units | `units_si` | base and derived SI unit declarations |

Generated function reference:
[Standard Library API](../library/stdlib-api.md).
