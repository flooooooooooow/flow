# N-body simulation of the outer solar system, from the Computer Language
# Benchmarks Game. Same algorithm and size as nbody.flow. Plain CPython.
import math
import time

SOLAR_MASS = 39.47841760435743
DAYS_PER_YEAR = 365.24
STEPS = 1000000

# Body: [x, y, z, vx, vy, vz, mass]


def make_bodies():
    return [
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, SOLAR_MASS],
        [4.84143144246472090, -1.16032004402742839, -0.103622044471123109,
         0.00166007664274403694 * DAYS_PER_YEAR,
         0.00769901118419740425 * DAYS_PER_YEAR,
         -0.0000690460016972063023 * DAYS_PER_YEAR,
         0.000954791938424326609 * SOLAR_MASS],
        [8.34336671824457987, 4.12479856412430479, -0.403523417114321381,
         -0.00276742510726862411 * DAYS_PER_YEAR,
         0.00499852801234917238 * DAYS_PER_YEAR,
         0.0000230417297573763929 * DAYS_PER_YEAR,
         0.000285885980666130812 * SOLAR_MASS],
        [12.8943695621391310, -15.1111514016986312, -0.223307578892655734,
         0.00296460137564761618 * DAYS_PER_YEAR,
         0.00237847173959480950 * DAYS_PER_YEAR,
         -0.0000296589568540237556 * DAYS_PER_YEAR,
         0.0000436624404335156298 * SOLAR_MASS],
        [15.3796971148509165, -25.9193146099879641, 0.179258772950371181,
         0.00268067772490389322 * DAYS_PER_YEAR,
         0.00162824170038242295 * DAYS_PER_YEAR,
         -0.0000951592254519715870 * DAYS_PER_YEAR,
         0.0000515138902046611451 * SOLAR_MASS],
    ]


def advance(bodies, n, dt):
    for i in range(n):
        bi = bodies[i]
        for j in range(i + 1, n):
            bj = bodies[j]
            dx = bi[0] - bj[0]
            dy = bi[1] - bj[1]
            dz = bi[2] - bj[2]

            d2 = dx * dx + dy * dy + dz * dz
            mag = dt / (d2 * math.sqrt(d2))

            mm_i = bi[6] * mag
            mm_j = bj[6] * mag

            bi[3] = bi[3] - dx * mm_j
            bi[4] = bi[4] - dy * mm_j
            bi[5] = bi[5] - dz * mm_j

            bj[3] = bj[3] + dx * mm_i
            bj[4] = bj[4] + dy * mm_i
            bj[5] = bj[5] + dz * mm_i

    for i in range(n):
        bi = bodies[i]
        bi[0] = bi[0] + dt * bi[3]
        bi[1] = bi[1] + dt * bi[4]
        bi[2] = bi[2] + dt * bi[5]


def energy(bodies, n):
    e = 0.0
    for i in range(n):
        bi = bodies[i]
        v2 = bi[3] * bi[3] + bi[4] * bi[4] + bi[5] * bi[5]
        e = e + 0.5 * bi[6] * v2
        for j in range(i + 1, n):
            bj = bodies[j]
            dx = bi[0] - bj[0]
            dy = bi[1] - bj[1]
            dz = bi[2] - bj[2]
            d = math.sqrt(dx * dx + dy * dy + dz * dz)
            e = e - bi[6] * bj[6] / d
    return e


def offset_momentum(bodies, n):
    px = 0.0
    py = 0.0
    pz = 0.0
    for i in range(n):
        bi = bodies[i]
        px = px + bi[3] * bi[6]
        py = py + bi[4] * bi[6]
        pz = pz + bi[5] * bi[6]
    bodies[0][3] = 0.0 - px / SOLAR_MASS
    bodies[0][4] = 0.0 - py / SOLAR_MASS
    bodies[0][5] = 0.0 - pz / SOLAR_MASS


def main():
    bodies = make_bodies()
    offset_momentum(bodies, 5)

    t0 = time.perf_counter()
    for _ in range(STEPS):
        advance(bodies, 5, 0.01)
    secs = time.perf_counter() - t0

    e1 = energy(bodies, 5)
    print("result %.9f" % e1)
    print("seconds %.9f" % secs)


if __name__ == "__main__":
    main()
