// Mandelbrot set membership count on a 400x400 grid, 100 max iterations.
// Same algorithm and size as mandelbrot.flow.
use std::time::Instant;

const W: i32 = 400;
const H: i32 = 400;
const MAXI: i32 = 100;

fn mandel_count() -> i32 {
    let mut count = 0;
    for py in 0..H {
        let cy = 2.5 * (py as f64) / (H as f64) - 1.25;
        for px in 0..W {
            let cx = 2.5 * (px as f64) / (W as f64) - 2.0;
            let mut zx = 0.0f64;
            let mut zy = 0.0f64;
            let mut iter = 0;
            while zx * zx + zy * zy <= 4.0 && iter < MAXI {
                let tmp = zx * zx - zy * zy + cx;
                zy = 2.0 * zx * zy + cy;
                zx = tmp;
                iter += 1;
            }
            if iter == MAXI {
                count += 1;
            }
        }
    }
    count
}

fn main() {
    let t0 = Instant::now();
    let count = mandel_count();
    let secs = t0.elapsed().as_secs_f64();
    println!("result {}", count);
    println!("seconds {:.9}", secs);
}
