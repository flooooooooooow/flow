# Autodiff Guide

Flow ships **automatic differentiation** as a language/stdlib feature, not a bolt-on framework. This page is the practical guide; API tables live in [Autodiff library](autodiff.md) and the [generated API index](stdlib-api.md).

## Why it is in the language

Audio, control, and scientific code often need gradients of the *same* functions that run in production. Keeping AD in-tree means:

1. No separate Python training graph
2. The differentiated program is still Flow (and still compiles to C)
3. Effects / dynamics code can sit next to the objective

## Modes

| Mode | Use when | Cost shape |
|------|----------|------------|
| **Forward** (dual numbers) | Few inputs, many outputs; directional derivatives | ~1× forward per direction |
| **Reverse** | Many inputs, scalar loss (ML / optimization) | 1 forward + 1 reverse |

Start with forward duals for DSP / small systems; reach for reverse when training nets or optimizing many parameters.

## Minimal forward-mode sketch

```flow
# Dual number: value + derivative seed
struct Dual {
    val: f64
    grad: f64
}

function dual(v: f64) -> Dual {
    return Dual { val: v, grad: 1.0 }
}

function dual_mul(a: Dual, b: Dual) -> Dual {
    return Dual {
        val: a.val * b.val,
        grad: a.val * b.grad + b.val * a.grad
    }
}

function main() -> i32 {
    let x: Dual = dual(3.0)
    let y: Dual = dual_mul(x, x)  # f(x)=x² → f'=2x
    printf("f=%f  f'=%f\n", y.val, y.grad)
    return 0
}
```

Run it in the [interactive tutorials](../tutorials/index.html) or with `./flow run`.

## Patterns that work today

- Scalar loss + parameter vector → reverse-mode layers in `lib/stdlib` / ML examples
- Filter / oscillator tuning → forward dual through the DSP graph
- Controllability / GA search in dynamics, combine `sense` analysis with numeric search (see [dynamics DSL](../language/dynamics-dsl.md))

## Honest limitations

> [!warning] Scope
> Higher-order AD, GPU reverse mode, and full Jacobian tooling are still maturing. Prefer the examples under `examples/ml/` and `docs/library/autodiff.md` over assuming PyTorch parity.

## Next steps

1. [Autodiff API](autodiff.md)
2. [Effects showcase](../effects-showcase.md), keep I/O out of the pure objective
3. [Comparison](../comparison.md), Flow vs Mojo/Rust on AD positioning
4. [Benchmark results](../project/benchmark-results.md), compile-to-C performance baseline
