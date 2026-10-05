# Autodiff Basics

> Dual numbers and derivative intuition (educational).
> Stdlib `Dual` in `lib/stdlib/autodiff.flow` uses **`f32`** — match that here.

## Part 1: Dual numbers

### 1.1 Dual multiply

```flow
struct Dual { val: f32, grad: f32 }

function dmul(a: Dual, b: Dual) -> Dual {
    return Dual {
        val: a.val * b.val,
        grad: a.val * b.grad + b.val * a.grad
    }
}

function main() -> i32 {
    let x: Dual = Dual { val: 3.0, grad: 1.0 }
    let y: Dual = dmul(x, x)
    printf("f=%f f'=%f\n", y.val, y.grad)
    return 0
}
```
### 1.2 Dual add + mul

```flow
struct Dual { val: f32, grad: f32 }

function dadd(a: Dual, b: Dual) -> Dual {
    return Dual { val: a.val + b.val, grad: a.grad + b.grad }
}

function dmul(a: Dual, b: Dual) -> Dual {
    return Dual {
        val: a.val * b.val,
        grad: a.val * b.grad + b.val * a.grad
    }
}

function main() -> i32 {
    let x: Dual = Dual { val: 2.0, grad: 1.0 }
    # f = x^2 + x
    let y: Dual = dadd(dmul(x, x), x)
    printf("f=%f f'=%f\n", y.val, y.grad)
    return 0
}
```

## Part 2: Objectives

### 2.1 Squared error

```flow
function main() -> i32 {
    let pred: f64 = 0.8
    let target: f64 = 1.0
    let err: f64 = pred - target
    let loss: f64 = err * err
    let dloss: f64 = 2.0 * err
    printf("loss=%f d/dpred=%f\n", loss, dloss)
    return 0
}
```
### 2.2 Gradient step

```flow
function main() -> i32 {
    let mut w: f64 = 0.0
    let x: f64 = 2.0
    let y: f64 = 5.0
    let lr: f64 = 0.1
    for step in 0 to 5 {
        let pred: f64 = w * x
        let g: f64 = 2.0 * (pred - y) * x
        w = w - lr * g
        printf("w=%f\n", w)
    }
    return 0
}
```

### 2.3 Dual of sin-ish polynomial (browser)

```flow
struct Dual { val: f32, grad: f32 }

function dmul(a: Dual, b: Dual) -> Dual {
    return Dual {
        val: a.val * b.val,
        grad: a.val * b.grad + b.val * a.grad
    }
}

function dadd(a: Dual, b: Dual) -> Dual {
    return Dual { val: a.val + b.val, grad: a.grad + b.grad }
}

function main() -> i32 {
    let x: Dual = Dual { val: 0.5, grad: 1.0 }
    # f = x^3 + x
    let x2: Dual = dmul(x, x)
    let x3: Dual = dmul(x2, x)
    let y: Dual = dadd(x3, x)
    printf("f=%f f'=%f\n", y.val, y.grad)
    return 0
}
```

### 2.4 Two-parameter gradient (browser)

```flow
function main() -> i32 {
    let mut w: f64 = 0.0
    let mut b: f64 = 0.0
    let x: f64 = 2.0
    let y: f64 = 5.0
    let lr: f64 = 0.05
    for step in 0 to 20 {
        let pred: f64 = w * x + b
        let err: f64 = pred - y
        w = w - lr * 2.0 * err * x
        b = b - lr * 2.0 * err
    }
    printf("w=%f b=%f\n", w, b)
    return 0
}
```

### 2.5 Chain rule product (browser)

```flow
struct Dual { val: f32, grad: f32 }

function dmul(a: Dual, b: Dual) -> Dual {
    return Dual {
        val: a.val * b.val,
        grad: a.val * b.grad + b.val * a.grad
    }
}

function main() -> i32 {
    let x: Dual = Dual { val: 2.0, grad: 1.0 }
    let y: Dual = Dual { val: 3.0, grad: 0.0 }
    let z: Dual = dmul(x, y)
    printf("z=%f dz/dx=%f\n", z.val, z.grad)
    return 0
}
```

## Part 3: Native autodiff and ML

Browser lessons reinvent Dual by hand. The stdlib does it for you:

```bash
./flow run examples/ml/autodiff/nn_xor.flow
./flow run examples/ml/models/mlp_xor.flow
```

`mlp_xor.flow` uses reverse-mode helpers / `nn_autogen` so you are not writing
backprop by hand. Next step on a laptop:

→ [ml-on-macbook.md](ml-on-macbook.md) — 8×8 digits MLP, parallel SGD, Metal status

Also: [Autodiff guide](../library/autodiff-guide.md) · [`lib/stdlib/autodiff.flow`](../../lib/stdlib/autodiff.flow)
