#include <stdint.h>
#include <stdlib.h>

/* Same 16-slot live ring as the Flow workload: a block freed before
 * anything can see it is removed by clang at -O3 (#745). */
int main(void) {
    uint8_t **ring = (uint8_t **)calloc(16, sizeof(uint8_t *));
    if (ring == NULL) {
        return 1;
    }
    int32_t checksum = 0;
    for (int32_t i = 0; i < 50000; i += 1) {
        int32_t slot = i % 16;
        if (ring[slot] != NULL) {
            free(ring[slot]);
        }
        uint8_t *p = (uint8_t *)malloc(64);
        if (p == NULL) {
            return 1;
        }
        p[0] = 1;
        p[63] = 2;
        checksum += (int32_t)p[0] + (int32_t)p[63];
        ring[slot] = p;
    }
    for (int32_t s = 0; s < 16; s += 1) {
        if (ring[s] != NULL) {
            free(ring[s]);
        }
    }
    free(ring);
    if (checksum != 150000) {
        return 2;
    }
    return 0;
}
