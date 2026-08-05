# FLOW Tutorials

Step-by-step tracks with **browser compile & run** on every complete `main` example.

- **[Interactive app](index.html)** — lesson picker with live editor
- **Written guides** — embedded runners on each `main` program
- **Native memory** — `import "stdlib/memory.flow"` + `./flow run` (real heap / arenas)

## Tracks

| Track | Focus |
|-------|--------|
| [beginner.md](beginner.md) | First programs |
| [control.md](control.md) | If / while / for |
| [functions.md](functions.md) | Params, recursion |
| [structs.md](structs.md) | Records & mutation |
| [arrays.md](arrays.md) | Fixed arrays & algos |
| [strings.md](strings.md) | printf & parsing |
| [pointers.md](pointers.md) | `ptr<T>`, null |
| [memory.md](memory.md) | **Manual memory** — malloc, free, arenas |
| [errors.md](errors.md) | Return codes / Result |
| [intermediate.md](intermediate.md) | Generics, traits, modules |
| [concurrency.md](concurrency.md) | Mutex / channel shapes (browser) |
| [algorithms.md](algorithms.md) | Search, sort, numerics |
| [systems.md](systems.md) | Rings, pools, bits |
| [effects-basics.md](effects-basics.md) | Effect-shaped design |
| [autodiff-basics.md](autodiff-basics.md) | Dual numbers |
| [ml-on-macbook.md](ml-on-macbook.md) | Training real models on a MacBook: digits MLP, parallel shards, Metal status |
| [audio-basics.md](audio-basics.md) | Sample / DSP loops |
| [advanced.md](advanced.md) | Effects deep-dive |
| [dynamics.md](dynamics.md) | Control / `dsys` path |
| [projects.md](projects.md) | Mini projects |

## Learning paths

1. **New to Flow:** beginner → control → functions → structs → arrays → projects  
2. **Systems / C background:** pointers → **memory** → systems → algorithms  
3. **ML / DSP:** autodiff-basics → [ml-on-macbook](ml-on-macbook.md) → audio-basics → [autodiff guide](../library/autodiff-guide.md)  
4. **Vision / control:** intermediate → dynamics → [VISION.md](../../VISION.md)

## Manual memory (native)

```bash
./flow run examples/systems/manual_memory.flow
```

See [library/memory.md](../library/memory.md) for the real `malloc` / arena API.
