#include <stdint.h>

int main(void) {
    int32_t sum = 0;
    for (int32_t i = 0; i < 1000000; i += 1) {
        sum += 1;
    }
    (void)sum;
    return 0;
}
