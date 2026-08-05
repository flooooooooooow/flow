/* N-body simulation of the outer solar system, from the Computer Language
 * Benchmarks Game. Same algorithm and size as nbody.flow. */
#include <stdio.h>
#include <stdint.h>
#include <math.h>
#include <time.h>

#define SOLAR_MASS 39.47841760435743
#define DAYS_PER_YEAR 365.24
#define STEPS 1000000

typedef struct {
    double x, y, z;
    double vx, vy, vz;
    double mass;
} Body;

static void advance(Body *bodies, int n, double dt) {
    for (int i = 0; i < n; i++) {
        for (int j = i + 1; j < n; j++) {
            double dx = bodies[i].x - bodies[j].x;
            double dy = bodies[i].y - bodies[j].y;
            double dz = bodies[i].z - bodies[j].z;

            double d2 = dx * dx + dy * dy + dz * dz;
            double mag = dt / (d2 * sqrt(d2));

            double mm_i = bodies[i].mass * mag;
            double mm_j = bodies[j].mass * mag;

            bodies[i].vx = bodies[i].vx - dx * mm_j;
            bodies[i].vy = bodies[i].vy - dy * mm_j;
            bodies[i].vz = bodies[i].vz - dz * mm_j;

            bodies[j].vx = bodies[j].vx + dx * mm_i;
            bodies[j].vy = bodies[j].vy + dy * mm_i;
            bodies[j].vz = bodies[j].vz + dz * mm_i;
        }
    }

    for (int i = 0; i < n; i++) {
        bodies[i].x = bodies[i].x + dt * bodies[i].vx;
        bodies[i].y = bodies[i].y + dt * bodies[i].vy;
        bodies[i].z = bodies[i].z + dt * bodies[i].vz;
    }
}

static double energy(Body *bodies, int n) {
    double e = 0.0;
    for (int i = 0; i < n; i++) {
        double v2 = bodies[i].vx * bodies[i].vx +
                    bodies[i].vy * bodies[i].vy +
                    bodies[i].vz * bodies[i].vz;
        e = e + 0.5 * bodies[i].mass * v2;

        for (int j = i + 1; j < n; j++) {
            double dx = bodies[i].x - bodies[j].x;
            double dy = bodies[i].y - bodies[j].y;
            double dz = bodies[i].z - bodies[j].z;
            double d = sqrt(dx * dx + dy * dy + dz * dz);
            e = e - bodies[i].mass * bodies[j].mass / d;
        }
    }
    return e;
}

static void offset_momentum(Body *bodies, int n) {
    double px = 0.0, py = 0.0, pz = 0.0;
    for (int i = 0; i < n; i++) {
        px = px + bodies[i].vx * bodies[i].mass;
        py = py + bodies[i].vy * bodies[i].mass;
        pz = pz + bodies[i].vz * bodies[i].mass;
    }
    bodies[0].vx = 0.0 - px / SOLAR_MASS;
    bodies[0].vy = 0.0 - py / SOLAR_MASS;
    bodies[0].vz = 0.0 - pz / SOLAR_MASS;
}

int main(void) {
    Body bodies[5] = {
        { 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, SOLAR_MASS },
        { 4.84143144246472090, -1.16032004402742839, -0.103622044471123109,
          0.00166007664274403694 * DAYS_PER_YEAR,
          0.00769901118419740425 * DAYS_PER_YEAR,
          -0.0000690460016972063023 * DAYS_PER_YEAR,
          0.000954791938424326609 * SOLAR_MASS },
        { 8.34336671824457987, 4.12479856412430479, -0.403523417114321381,
          -0.00276742510726862411 * DAYS_PER_YEAR,
          0.00499852801234917238 * DAYS_PER_YEAR,
          0.0000230417297573763929 * DAYS_PER_YEAR,
          0.000285885980666130812 * SOLAR_MASS },
        { 12.8943695621391310, -15.1111514016986312, -0.223307578892655734,
          0.00296460137564761618 * DAYS_PER_YEAR,
          0.00237847173959480950 * DAYS_PER_YEAR,
          -0.0000296589568540237556 * DAYS_PER_YEAR,
          0.0000436624404335156298 * SOLAR_MASS },
        { 15.3796971148509165, -25.9193146099879641, 0.179258772950371181,
          0.00268067772490389322 * DAYS_PER_YEAR,
          0.00162824170038242295 * DAYS_PER_YEAR,
          -0.0000951592254519715870 * DAYS_PER_YEAR,
          0.0000515138902046611451 * SOLAR_MASS }
    };

    offset_momentum(bodies, 5);

    uint64_t t0 = clock_gettime_nsec_np(CLOCK_MONOTONIC);
    for (int i = 0; i < STEPS; i++) {
        advance(bodies, 5, 0.01);
    }
    uint64_t t1 = clock_gettime_nsec_np(CLOCK_MONOTONIC);
    double secs = (t1 - t0) / 1e9;

    double e1 = energy(bodies, 5);
    printf("result %.9f\n", e1);
    printf("seconds %.9f\n", secs);
    return 0;
}
