#include <stdint.h>
#include <stdlib.h>

int main(void) {
    const int32_t n = 4096;
    int64_t *xs = (int64_t *)malloc((size_t)n * sizeof(int64_t));
    if (xs == NULL) {
        return 1;
    }
    for (int32_t i = 0; i < n; i += 1) {
        xs[i] = (int64_t)i * 17 + 3;
    }

    int64_t sum = 0;
    int64_t sumsq = 0;
    int64_t mn = xs[0];
    int64_t mx = xs[0];
    for (int32_t i = 0; i < n; i += 1) {
        int64_t v = xs[i];
        sum += v;
        sumsq += v * v;
        if (v < mn) {
            mn = v;
        }
        if (v > mx) {
            mx = v;
        }
    }
    free(xs);
    if (sum != 142583808LL) {
        return 2;
    }
    if (mn != 3 || mx != 69618) {
        return 3;
    }
    if (sumsq != 6618407614464LL) {
        return 4;
    }
    return 0;
}
