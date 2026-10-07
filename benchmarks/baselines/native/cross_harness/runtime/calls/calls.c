#include <stdint.h>

static int32_t foo(void) {
    return 1;
}

int main(void) {
    int32_t sum = 0;
    for (int32_t i = 0; i < 1000000; i += 1) {
        sum += foo();
    }
    (void)sum;
    return 0;
}
