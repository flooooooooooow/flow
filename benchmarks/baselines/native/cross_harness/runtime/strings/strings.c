#include <stdint.h>
#include <stdlib.h>
#include <string.h>

int main(void) {
    const char *source = "The Quick Brown Fox Jumps Over The Lazy Dog 1234567890!";
    const int64_t len = (int64_t)strlen(source);
    const uint8_t *p_src = (const uint8_t *)source;

    uint8_t *buf = (uint8_t *)malloc((size_t)(len + 1));
    if (buf == NULL) {
        return 1;
    }

    int32_t checksum = 0;
    for (int32_t iter = 0; iter < 100000; iter += 1) {
        for (int64_t i = 0; i < len; i += 1) {
            uint8_t c = p_src[i];
            if (c >= 97 && c <= 122) {
                c = (uint8_t)((int32_t)c - 32);
            }
            buf[i] = c;
            checksum += (int32_t)c;
        }
        buf[len] = 0;
    }

    free(buf);
    if (checksum % 256 != 96) {
        return 1;
    }
    return 0;
}
