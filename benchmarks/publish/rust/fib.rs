// Naive recursive Fibonacci. Same algorithm and size as fib.flow.
use std::time::Instant;

fn fib(n: i32) -> i64 {
    if n < 2 {
        return n as i64;
    }
    fib(n - 1) + fib(n - 2)
}

fn main() {
    let t0 = Instant::now();
    let result = fib(35);
    let secs = t0.elapsed().as_secs_f64();
    println!("result {}", result);
    println!("seconds {:.9}", secs);
}
