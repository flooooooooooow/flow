#include <stdint.h>
#include <stdlib.h>

int main(void) {
    for (int32_t i = 0; i < 1000; i += 1) {
        uint8_t *p = (uint8_t *)malloc(64);
        if (p == NULL) {
            return 1;
        }
        p[0] = 1;
        p[63] = 2;
        free(p);
    }
    return 0;
}
