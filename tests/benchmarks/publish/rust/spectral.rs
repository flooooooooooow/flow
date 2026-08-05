// Spectral norm, from the Computer Language Benchmarks Game.
// Same algorithm and size as spectral.flow.
use std::time::Instant;

const N: usize = 500;

fn a(i: usize, j: usize) -> f64 {
    let div = (((i + j) * (i + j + 1)) / 2 + i + 1) as f64;
    1.0 / div
}

fn mult_av(v: &[f64], av: &mut [f64], n: usize) {
    for i in 0..n {
        let mut sum = 0.0;
        for j in 0..n {
            sum += a(i, j) * v[j];
        }
        av[i] = sum;
    }
}

fn mult_atv(v: &[f64], atv: &mut [f64], n: usize) {
    for i in 0..n {
        let mut sum = 0.0;
        for j in 0..n {
            sum += a(j, i) * v[j];
        }
        atv[i] = sum;
    }
}

fn mult_atav(v: &[f64], atav: &mut [f64], tmp: &mut [f64], n: usize) {
    mult_av(v, tmp, n);
    mult_atv(tmp, atav, n);
}

fn main() {
    let mut u = vec![1.0f64; N];
    let mut v = vec![0.0f64; N];
    let mut tmp = vec![0.0f64; N];

    let t0 = Instant::now();

    for _ in 0..10 {
        mult_atav(&u, &mut v, &mut tmp, N);
        mult_atav(&v, &mut u, &mut tmp, N);
    }

    let mut v_bv = 0.0;
    let mut vv = 0.0;
    for i in 0..N {
        v_bv += u[i] * v[i];
        vv += v[i] * v[i];
    }
    let result = (v_bv / vv).sqrt();

    let secs = t0.elapsed().as_secs_f64();

    println!("result {:.9}", result);
    println!("seconds {:.9}", secs);
}
