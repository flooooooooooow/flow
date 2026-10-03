void roots(float* a, int n) {
  #ifdef _OPENMP
  #pragma omp simd
  #else
  #pragma clang loop vectorize(enable) interleave(enable)
  #pragma GCC ivdep
  #endif
  for (int k = 0; k < n; k = k + 1) {
    float t = a[k] * 2.0;
    a[k] = t;
  }
}
