#include <stdint.h>
#include <stdlib.h>

int main(void) {
    int32_t checksum = 0;
    for (int32_t i = 0; i < 50000; i += 1) {
        uint8_t *p = (uint8_t *)malloc(64);
        if (p == NULL) {
            return 1;
        }
        p[0] = 1;
        p[63] = 2;
        checksum += (int32_t)p[0] + (int32_t)p[63];
        free(p);
    }
    if (checksum != 150000) {
        return 2;
    }
    return 0;
}
