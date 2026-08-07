# FLOW Tutorials

Step-by-step tracks with **browser compile & run** on every complete `main`
example, plus native-only tracks for gfx / shaders / `flow` blocks / `@rt_safe`.

- **[Interactive app](index.html)** — lesson picker with live editor
- **Written guides** — embedded runners on each `main` program
- **Native surfaces** — `./flow run` · `./flow gfx` · `./flow shader` · `./flow record`

## Tracks

| Track | Focus |
|-------|--------|
| [beginner.md](beginner.md) | First programs |
| [control.md](control.md) | If / while / for |
| [functions.md](functions.md) | Params, recursion |
| [pipelines.md](pipelines.md) | `\|\>`, `_`, declarative sort |
| [structs.md](structs.md) | Records & mutation |
| [arrays.md](arrays.md) | Fixed arrays & algos |
| [strings.md](strings.md) | printf & parsing |
| [pointers.md](pointers.md) | `ptr<T>`, null |
| [memory.md](memory.md) | **Manual memory** — malloc, free, arenas |
| [errors.md](errors.md) | Return codes / Result pipelines |
| [intermediate.md](intermediate.md) | Generics, traits, modules |
| [concurrency.md](concurrency.md) | Mutex / channel shapes (browser) + native next steps |
| [algorithms.md](algorithms.md) | Search, sort, numerics |
| [systems.md](systems.md) | Rings, pools, bits |
| [effects-basics.md](effects-basics.md) | Effect-shaped design + native effects |
| [autodiff-basics.md](autodiff-basics.md) | Dual numbers → MLP / MacBook |
| [ml-on-macbook.md](ml-on-macbook.md) | Digits MLP, parallel SGD, Metal status |
| [audio-basics.md](audio-basics.md) | Sample / DSP loops |
| [rt-audio.md](rt-audio.md) | `@rt_safe` callbacks |
| [advanced.md](advanced.md) | Effects deep-dive, SIMD, POSIX |
| [evolution.md](evolution.md) | `flow` / `evolves` / hybrid / `field` |
| [dynamics.md](dynamics.md) | Integrators, `dsys`, sense, GA / LQR |
| [gfx-basics.md](gfx-basics.md) | Native windows, games, `flow record` |
| [shaders.md](shaders.md) | FSL fill shaders (`./flow shader`) |
| [game-ai.md](game-ai.md) | Q-learning, GA, policy gradients |
| [domains.md](domains.md) | Morphogenesis, circuits, neuro capstones |
| [projects.md](projects.md) | Mini projects |

## Learning paths

1. **New to Flow:** beginner → control → functions → pipelines → structs → arrays → projects  
2. **Systems / C background:** pointers → **memory** → systems → algorithms → rt-audio  
3. **ML / DSP:** autodiff-basics → [ml-on-macbook](ml-on-macbook.md) → audio-basics → rt-audio  
4. **Vision / control:** pipelines → **evolution** → dynamics → effects-basics → autodiff-basics  
5. **Graphics:** gfx-basics → evolution (Lorenz) → shaders → domains (morphogenesis)

## Manual memory (native)

```bash
./flow run examples/systems/manual_memory.flow
```

See [library/memory.md](../library/memory.md) for the real `malloc` / arena API.
