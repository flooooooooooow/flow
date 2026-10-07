/* Native twin of runtime/ffi_scalar: the same noinline scalar call made from
   C, so flow_vs_native is the cost of the Flow side of the crossing (#737). */
#include <stdint.h>

__attribute__((noinline)) int64_t ffi_h_scalar(int64_t v) { return v + 1; }

int main(void) {
    int64_t sum = 0;
    for (int32_t i = 0; i < 20000; i += 1) {
        sum += ffi_h_scalar((int64_t)i);
    }
    return sum <= 0 ? 1 : 0;
}
