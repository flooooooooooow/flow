# Autodiff Basics

> Dual numbers and derivative intuition (educational).


## Part 1: Dual numbers

### 1.1 Dual multiply

```flow
struct Dual { val: f64, grad: f64 }

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
struct Dual { val: f64, grad: f64 }

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
