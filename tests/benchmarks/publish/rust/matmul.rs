// Dense matrix multiply, naive i-j-k triple loop, 300x300 doubles.
// Same algorithm and size as matmul.flow.
use std::time::Instant;

const N: usize = 300;

fn matmul(a: &[f64], b: &[f64], c: &mut [f64], n: usize) {
    for i in 0..n {
        for j in 0..n {
            let mut sum = 0.0;
            for k in 0..n {
                sum += a[i * n + k] * b[k * n + j];
            }
            c[i * n + j] = sum;
        }
    }
}

fn main() {
    let mut a = vec![0.0f64; N * N];
    let mut b = vec![0.0f64; N * N];
    let mut c = vec![0.0f64; N * N];

    for i in 0..N {
        for j in 0..N {
            a[i * N + j] = 0.001 * ((i + j) as f64);
            b[i * N + j] = 0.001 * ((i as f64) - (j as f64));
        }
    }

    let t0 = Instant::now();
    matmul(&a, &b, &mut c, N);
    let secs = t0.elapsed().as_secs_f64();

    let mut check = 0.0;
    for i in 0..(N * N) {
        check += c[i];
    }

    println!("result {:.6}", check);
    println!("seconds {:.9}", secs);
}
