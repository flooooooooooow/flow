void roots(float* a, int n) {
  #pragma clang loop vectorize(enable) interleave(enable)
  #pragma GCC ivdep
  for (int k = 0; k < n; k = k + 1) {
    float t = a[k] * 2.0;
    a[k] = t;
  }
}
