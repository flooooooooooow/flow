# Taylor series geometric proof — sin(x) and Maclaurin partial sums
title Taylor approximations to sin(x)
caption sin(x) (solid) with Maclaurin polynomials T_1, T_3, T_5 — the arcs coincide at the origin and peel away as |x| grows.
size 520 400
axes 70 310 58 -3.4 3.4 -1.3 1.3

plot sin(x) from -3.14 to 3.14 color #2c3e50 width 2.8 label sin(x)

def fact(n) {
  let r = 1
  let i = 2
  while i <= n {
    let r = r * i
    let i = i + 1
  }
  return r
}

def taylor_sin_term(x, i) {
  let p = 2 * i + 1
  return pow(-1, i) * pow(x, p) / fact(p)
}

def taylor_sin(x, k) {
  let s = 0
  let i = 0
  while i <= k {
    let s = s + taylor_sin_term(x, i)
    let i = i + 1
  }
  return s
}

plot taylor_sin(x, 0) from -2.8 to 2.8 color #c0392b width 2 dash label T1
plot taylor_sin(x, 1) from -2.8 to 2.8 color #2980b9 width 2 dash label T3
plot taylor_sin(x, 2) from -2.8 to 2.8 color #27ae60 width 2 dash label T5
fill between sin(x) and taylor_sin(x, 2) from 0 to 1.25 color #e67e22@22

text -2.8 1.05 "T₁(x) = x"
text -2.8 0.82 "T₃(x) = x − x³/6"
text 1.4 -1.05 "remainder shrinks near 0"