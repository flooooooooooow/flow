#include <stdint.h>

int main(void) {
    int32_t arr[1000] = {0};
    int64_t checksum = 0;
    for (int32_t rep = 0; rep < 10000; rep += 1) {
        for (int32_t i = 0; i < 1000; i += 1) {
            arr[i] = i;
            checksum += (int64_t)arr[i];
        }
    }
    if (checksum != 4995000000LL) {
        return 1;
    }
    return 0;
}
