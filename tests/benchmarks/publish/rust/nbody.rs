// N-body simulation of the outer solar system, from the Computer Language
// Benchmarks Game. Same algorithm and size as nbody.flow.
use std::time::Instant;

const SOLAR_MASS: f64 = 39.47841760435743;
const DAYS_PER_YEAR: f64 = 365.24;
const STEPS: i32 = 1000000;

#[derive(Clone, Copy)]
struct Body {
    x: f64,
    y: f64,
    z: f64,
    vx: f64,
    vy: f64,
    vz: f64,
    mass: f64,
}

fn advance(bodies: &mut [Body; 5], dt: f64) {
    let n = 5;
    for i in 0..n {
        for j in (i + 1)..n {
            let dx = bodies[i].x - bodies[j].x;
            let dy = bodies[i].y - bodies[j].y;
            let dz = bodies[i].z - bodies[j].z;

            let d2 = dx * dx + dy * dy + dz * dz;
            let mag = dt / (d2 * d2.sqrt());

            let mm_i = bodies[i].mass * mag;
            let mm_j = bodies[j].mass * mag;

            bodies[i].vx -= dx * mm_j;
            bodies[i].vy -= dy * mm_j;
            bodies[i].vz -= dz * mm_j;

            bodies[j].vx += dx * mm_i;
            bodies[j].vy += dy * mm_i;
            bodies[j].vz += dz * mm_i;
        }
    }

    for i in 0..n {
        bodies[i].x += dt * bodies[i].vx;
        bodies[i].y += dt * bodies[i].vy;
        bodies[i].z += dt * bodies[i].vz;
    }
}

fn energy(bodies: &[Body; 5]) -> f64 {
    let n = 5;
    let mut e = 0.0;
    for i in 0..n {
        let v2 = bodies[i].vx * bodies[i].vx
            + bodies[i].vy * bodies[i].vy
            + bodies[i].vz * bodies[i].vz;
        e += 0.5 * bodies[i].mass * v2;

        for j in (i + 1)..n {
            let dx = bodies[i].x - bodies[j].x;
            let dy = bodies[i].y - bodies[j].y;
            let dz = bodies[i].z - bodies[j].z;
            let d = (dx * dx + dy * dy + dz * dz).sqrt();
            e -= bodies[i].mass * bodies[j].mass / d;
        }
    }
    e
}

fn offset_momentum(bodies: &mut [Body; 5]) {
    let mut px = 0.0;
    let mut py = 0.0;
    let mut pz = 0.0;
    for b in bodies.iter() {
        px += b.vx * b.mass;
        py += b.vy * b.mass;
        pz += b.vz * b.mass;
    }
    bodies[0].vx = 0.0 - px / SOLAR_MASS;
    bodies[0].vy = 0.0 - py / SOLAR_MASS;
    bodies[0].vz = 0.0 - pz / SOLAR_MASS;
}

fn main() {
    let mut bodies: [Body; 5] = [
        Body {
            x: 0.0,
            y: 0.0,
            z: 0.0,
            vx: 0.0,
            vy: 0.0,
            vz: 0.0,
            mass: SOLAR_MASS,
        },
        Body {
            x: 4.84143144246472090,
            y: -1.16032004402742839,
            z: -0.103622044471123109,
            vx: 0.00166007664274403694 * DAYS_PER_YEAR,
            vy: 0.00769901118419740425 * DAYS_PER_YEAR,
            vz: -0.0000690460016972063023 * DAYS_PER_YEAR,
            mass: 0.000954791938424326609 * SOLAR_MASS,
        },
        Body {
            x: 8.34336671824457987,
            y: 4.12479856412430479,
            z: -0.403523417114321381,
            vx: -0.00276742510726862411 * DAYS_PER_YEAR,
            vy: 0.00499852801234917238 * DAYS_PER_YEAR,
            vz: 0.0000230417297573763929 * DAYS_PER_YEAR,
            mass: 0.000285885980666130812 * SOLAR_MASS,
        },
        Body {
            x: 12.8943695621391310,
            y: -15.1111514016986312,
            z: -0.223307578892655734,
            vx: 0.00296460137564761618 * DAYS_PER_YEAR,
            vy: 0.00237847173959480950 * DAYS_PER_YEAR,
            vz: -0.0000296589568540237556 * DAYS_PER_YEAR,
            mass: 0.0000436624404335156298 * SOLAR_MASS,
        },
        Body {
            x: 15.3796971148509165,
            y: -25.9193146099879641,
            z: 0.179258772950371181,
            vx: 0.00268067772490389322 * DAYS_PER_YEAR,
            vy: 0.00162824170038242295 * DAYS_PER_YEAR,
            vz: -0.0000951592254519715870 * DAYS_PER_YEAR,
            mass: 0.0000515138902046611451 * SOLAR_MASS,
        },
    ];

    offset_momentum(&mut bodies);

    let t0 = Instant::now();
    for _ in 0..STEPS {
        advance(&mut bodies, 0.01);
    }
    let secs = t0.elapsed().as_secs_f64();

    let e1 = energy(&bodies);
    println!("result {:.9}", e1);
    println!("seconds {:.9}", secs);
}
