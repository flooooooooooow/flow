#include <stdint.h>
void test(float *a, int n) {
  #pragma clang loop vectorize(enable) interleave(enable)
  #pragma GCC ivdep
  for (int32_t k = 0; k < n; k = k + 1) {
    a[k] = a[k] * 2.0f;
  }
}
