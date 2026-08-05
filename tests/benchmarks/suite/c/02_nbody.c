/* N-Body Benchmark - Tests floating-point and struct performance */
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>

#define PI 3.141592653589793
#define SOLAR_MASS (4 * PI * PI)
#define DAYS_PER_YEAR 365.24

typedef struct {
    double x, y, z;
    double vx, vy, vz;
    double mass;
} Body;

void advance(Body* bodies, int n, double dt) {
    for (int i = 0; i < n; i++) {
        for (int j = i + 1; j < n; j++) {
            double dx = bodies[i].x - bodies[j].x;
            double dy = bodies[i].y - bodies[j].y;
            double dz = bodies[i].z - bodies[j].z;
            
            double d2 = dx * dx + dy * dy + dz * dz;
            double mag = dt / (d2 * sqrt(d2));
            
            double mm_i = bodies[i].mass * mag;
            double mm_j = bodies[j].mass * mag;
            
            bodies[i].vx -= dx * mm_j;
            bodies[i].vy -= dy * mm_j;
            bodies[i].vz -= dz * mm_j;
            
            bodies[j].vx += dx * mm_i;
            bodies[j].vy += dy * mm_i;
            bodies[j].vz += dz * mm_i;
        }
    }
    
    for (int i = 0; i < n; i++) {
        bodies[i].x += dt * bodies[i].vx;
        bodies[i].y += dt * bodies[i].vy;
        bodies[i].z += dt * bodies[i].vz;
    }
}

double energy(Body* bodies, int n) {
    double e = 0.0;
    
    for (int i = 0; i < n; i++) {
        double v2 = bodies[i].vx * bodies[i].vx + 
                    bodies[i].vy * bodies[i].vy + 
                    bodies[i].vz * bodies[i].vz;
        e += 0.5 * bodies[i].mass * v2;
        
        for (int j = i + 1; j < n; j++) {
            double dx = bodies[i].x - bodies[j].x;
            double dy = bodies[i].y - bodies[j].y;
            double dz = bodies[i].z - bodies[j].z;
            double d = sqrt(dx * dx + dy * dy + dz * dz);
            e -= bodies[i].mass * bodies[j].mass / d;
        }
    }
    
    return e;
}

void offset_momentum(Body* bodies, int n) {
    double px = 0.0, py = 0.0, pz = 0.0;
    
    for (int i = 0; i < n; i++) {
        px += bodies[i].vx * bodies[i].mass;
        py += bodies[i].vy * bodies[i].mass;
        pz += bodies[i].vz * bodies[i].mass;
    }
    
    bodies[0].vx = -px / SOLAR_MASS;
    bodies[0].vy = -py / SOLAR_MASS;
    bodies[0].vz = -pz / SOLAR_MASS;
}

void init_solar_system(Body* bodies) {
    /* Sun */
    bodies[0] = (Body){0, 0, 0, 0, 0, 0, SOLAR_MASS};
    
    /* Jupiter */
    bodies[1] = (Body){
        4.84143144246472090, -1.16032004402742839, -0.103622044471123109,
        0.00166007664274403694 * DAYS_PER_YEAR, 
        0.00769901118419740425 * DAYS_PER_YEAR, 
        -0.0000690460016972063023 * DAYS_PER_YEAR,
        0.000954791938424326609 * SOLAR_MASS
    };
    
    /* Saturn */
    bodies[2] = (Body){
        8.34336671824457987, 4.12479856412430479, -0.403523417114321381,
        -0.00276742510726862411 * DAYS_PER_YEAR, 
        0.00499852801234917238 * DAYS_PER_YEAR, 
        0.0000230417297573763929 * DAYS_PER_YEAR,
        0.000285885980666130812 * SOLAR_MASS
    };
    
    /* Uranus */
    bodies[3] = (Body){
        12.8943695621391310, -15.1111514016986312, -0.223307578892655734,
        0.00296460137564761618 * DAYS_PER_YEAR, 
        0.00237847173959480950 * DAYS_PER_YEAR, 
        -0.0000296589568540237556 * DAYS_PER_YEAR,
        0.0000436624404335156298 * SOLAR_MASS
    };
    
    /* Neptune */
    bodies[4] = (Body){
        15.3796971148509165, -25.9193146099879641, 0.179258772950371181,
        0.00268067772490389322 * DAYS_PER_YEAR, 
        0.00162824170038242295 * DAYS_PER_YEAR, 
        -0.0000951592254519715870 * DAYS_PER_YEAR,
        0.0000515138902046611451 * SOLAR_MASS
    };
}

int main() {
    printf("==============================================\n");
    printf("  N-BODY BENCHMARK (Solar System) - C\n");
    printf("==============================================\n\n");
    
    Body bodies[5];
    init_solar_system(bodies);
    offset_momentum(bodies, 5);
    
    double e0 = energy(bodies, 5);
    printf("Initial energy: %.9f\n\n", e0);
    
    int iterations[] = {1000000, 10000000, 50000000};
    
    for (int idx = 0; idx < 3; idx++) {
        int n = iterations[idx];
        
        init_solar_system(bodies);
        offset_momentum(bodies, 5);
        
        printf("Running %d iterations...\n", n);
        
        clock_t start = clock();
        for (int i = 0; i < n; i++) {
            advance(bodies, 5, 0.01);
        }
        clock_t end = clock();
        
        double elapsed = (double)(end - start) / CLOCKS_PER_SEC;
        double e1 = energy(bodies, 5);
        
        printf("  Time: %.3f sec | Energy: %.9f | %.2f M steps/sec\n",
               elapsed, e1, n / elapsed / 1000000.0);
    }
    
    printf("\nBenchmark complete.\n");
    return 0;
}
