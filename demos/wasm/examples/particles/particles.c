#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>


double rand_lcg_ptr_i32(int32_t* seed);
double* particle_init_f64_f64(double w, double h);
int32_t particle_step_ptr_f64_f64_f64(double* p, double w, double h);
int32_t main(void);

double rand_lcg_ptr_i32(int32_t* seed) {
    int32_t s = seed[0];
    s = ((s * 1103515245) + 12345);
    seed[0] = s;
    int32_t val = s;
    if (val < 0) {
        val = (0 - val);
    }
    return ((val % 10000) / 10000.0);
}

double* particle_init_f64_f64(double w, double h) {
    double* p = malloc(((200 * 4) * 8));
    int32_t* seed = malloc(4);
    seed[0] = 42;
    for (int32_t i = 0; i < 200; i += 1) {
        int32_t idx = (i * 4);
        p[idx] = (rand_lcg_ptr_i32(seed) * w);
        p[(idx + 1)] = ((rand_lcg_ptr_i32(seed) * h) * 0.3);
        p[(idx + 2)] = ((rand_lcg_ptr_i32(seed) - 0.5) * 5.0);
        p[(idx + 3)] = (rand_lcg_ptr_i32(seed) * 2.0);
    }
    free(seed);
    return p;
}

int32_t particle_step_ptr_f64_f64_f64(double* p, double w, double h) {
    for (int32_t i = 0; i < 200; i += 1) {
        int32_t idx = (i * 4);
        double x = p[idx];
        double y = p[(idx + 1)];
        double vx = p[(idx + 2)];
        double vy = p[(idx + 3)];
        vy = (vy + 0.2);
        vx = (vx * 0.997);
        vy = (vy * 0.997);
        x = (x + vx);
        y = (y + vy);
        if (x < 4.0) {
            x = 4.0;
            vx = (0.0 - (vx * 0.8));
        }
        if (x > (w - 4.0)) {
            x = (w - 4.0);
            vx = (0.0 - (vx * 0.8));
        }
        if (y < 4.0) {
            y = 4.0;
            vy = (0.0 - (vy * 0.8));
        }
        if (y > (h - 4.0)) {
            y = (h - 4.0);
            vy = (0.0 - (vy * 0.8));
        }
        p[idx] = x;
        p[(idx + 1)] = y;
        p[(idx + 2)] = vx;
        p[(idx + 3)] = vy;
    }
    return 200;
}

int32_t main(void) {
    return 0;
}
