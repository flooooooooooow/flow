#include <stdint.h>
#include <string.h>

int main(void) {
    const char *a = "key_";
    const char *b = "000";
    const char *c = "=value_";
    const char *d = "payload";
    const char *e = "_line_";
    const char *f = "data";
    const char *g = "_end";
    const char *h = "\n";
    const char *parts[8] = {a, b, c, d, e, f, g, h};

    int32_t checksum = 0;
    for (int32_t i = 0; i < 50000; i += 1) {
        char s[64];
        int32_t n = 0;
        for (int32_t p = 0; p < 8; p += 1) {
            const char *part = parts[p];
            while (part[0] != 0) {
                s[n] = part[0];
                checksum += (int32_t)(uint8_t)part[0];
                n += 1;
                part += 1;
            }
        }
        s[n] = 0;
        (void)s;
    }
    if (checksum != 172550000) {
        return 1;
    }
    return 0;
}
