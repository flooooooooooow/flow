# Flow vs Python

<img src="https://cdn.simpleicons.org/python/3776AB" alt="Python logo" width="64" height="64">

Python is often more concise than Flow for small scripts. Flow's argument is not that static native code can beat Python at one-line convenience. It is that a system can stay close to Python's readability while carrying types, domain semantics and native execution in the source instead of handing the performance-critical half to C, C++, Rust, CUDA or a framework.

[← All language comparisons](../comparison.md)

## Example: the same model

### Flow

```flow
flow Decay {
    state value : f64 = 1.0
    param rate  : f64 = 0.5

    value evolves as -rate * value
}

function main() -> i32 {
    let mut system: Decay = Decay_new()

    for i in 0 to 100 {
        Decay_step(&system, 0.01)
    }

    println(system.value)
    return 0
}
```

### Python

```python
from dataclasses import dataclass

@dataclass
class Decay:
    value: float = 1.0
    rate: float = 0.5

    def step(self, dt: float) -> None:
        derivative = -self.rate * self.value
        self.value += derivative * dt

system = Decay()

for _ in range(100):
    system.step(0.01)

print(system.value)
```

The Python is readable and compact. Flow's advantage is that `state`, `param` and `evolves as` are compiler-visible semantics and the resulting program follows a native compilation path without requiring the model to be rewritten behind a Python extension boundary.

## The important comparison is the whole stack

A Python numerical or ML project often looks wonderfully small at the call site because the implementation complexity lives in NumPy, PyTorch, JAX, Numba, Cython, C++, CUDA, Triton or another compiled layer.

Flow is aiming at a different kind of compression: keep the high-level description and the low-level implementation in one language so the readable surface is also the deployable implementation.

That matters most for DSP, simulations, kernels, embedded work and other places where “just use a Python library” eventually crosses into native code.

## Where Python still wins

Python wins on ecosystem breadth, notebooks, data exploration, scripting, package availability, onboarding and the speed with which a programmer can connect existing libraries.

Flow becomes interesting when the code that matters cannot remain ordinary Python and the project would otherwise split across Python plus one or more lower-level languages.

## See also

[Python target](../python-target.md) · [Autodiff](../library/autodiff.md) · [ML on MacBook](../tutorials/ml-on-macbook.md) · [Benchmarks](../project/benchmark-results.md)
