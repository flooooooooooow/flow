void roots(float* a, int n) {
  #if defined(_OPENMP)
  #pragma omp simd
  #elif defined(__clang__)
  #pragma clang loop vectorize(enable) interleave(enable)
  #elif defined(__GNUC__)
  #pragma GCC ivdep
  #endif
  for (int k = 0; k < n; k = k + 1) {
    float t = a[k] * 2.0;
    a[k] = t;
  }
}
