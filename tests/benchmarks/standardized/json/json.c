/* JSON parsing benchmark (simulated)
 * Since this is comparing struct creation, not actual JSON parsing
 */
#include <stdio.h>
#include <time.h>

#define NUM_ITERATIONS 1000000

typedef struct {
    double x;
    double y;
    double z;
} Point;

static inline Point parse_point(double x, double y, double z) {
    return (Point){x, y, z};
}

int main(void) {
    clock_t start = clock();
    
    double sum = 0.0;
    
    for (int i = 0; i < NUM_ITERATIONS; i++) {
        Point p = parse_point(i * 1.0, i * 2.0, i * 3.0);
        sum += p.x + p.y + p.z;
    }
    
    clock_t end = clock();
    double elapsed_us = (double)(end - start) / CLOCKS_PER_SEC * 1000000.0;
    
    printf("%.1f µs (checksum: %.0f)\n", elapsed_us, sum);
    
    return 0;
}
