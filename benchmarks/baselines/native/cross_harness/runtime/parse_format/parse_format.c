#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    const char *text = "10,20,30,40,50,60,70,80,90,100,250,350,450,550,999,-1,-42,0,7,2147483647";
    int64_t checksum = 0;
    for (int32_t iter = 0; iter < 20000; iter += 1) {
        const char *pos = text;
        while (pos[0] != 0) {
            char *end = NULL;
            int64_t value = strtoll(pos, &end, 10);
            if (end == pos) {
                return 1;
            }
            checksum += value;
            char buf[32];
            int w = snprintf(buf, 32, "%lld", (long long)value);
            if (w < 1) {
                return 2;
            }
            checksum += (int64_t)w;
            pos = end;
            if (pos[0] == ',') {
                pos += 1;
            } else if (pos[0] == 0) {
                break;
            } else {
                return 3;
            }
        }
    }
    if (checksum != 42949736260000LL) {
        return 4;
    }
    return 0;
}
