/* Native twin of runtime/ffi_buffer: the contiguous buffer goes to the callee
   as a plain pointer and length, which is what the zero-copy FFIBuffer
   borrow hands across. */
#include <stdint.h>
#include <stdlib.h>

__attribute__((noinline)) int64_t ffi_h_sum(int64_t *ptr, int64_t n) {
    int64_t sum = 0;
    for (int64_t i = 0; i < n; i++) { sum += ptr[i]; }
    return sum;
}

int main(void) {
    const int32_t n = 4096;
    int64_t *p = (int64_t *)malloc((size_t)n * 8);
    if (p == NULL) { return 1; }
    for (int32_t i = 0; i < n; i += 1) { p[i] = (int64_t)i; }
    int64_t sum = 0;
    for (int32_t r = 0; r < 64; r += 1) { sum += ffi_h_sum(p, (int64_t)n); }
    free(p);
    return sum <= 0 ? 4 : 0;
}
