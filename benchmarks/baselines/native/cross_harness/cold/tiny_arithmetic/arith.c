/* Native twin of benchmarks/cross_harness/cold/tiny_arithmetic (#746). */
#include <stdint.h>

int main(void) {
    volatile int32_t a = 10;
    volatile int32_t b = 20;
    return a + b - 30;
}
