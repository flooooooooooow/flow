#include <stdint.h>
#include <stdlib.h>

static void sift_down(int32_t *xs, int32_t start, int32_t n) {
    int32_t root = start;
    while (1) {
        int32_t left = root * 2 + 1;
        if (left >= n) {
            return;
        }
        int32_t cand = root;
        if (xs[cand] < xs[left]) {
            cand = left;
        }
        int32_t right = left + 1;
        if (right < n && xs[cand] < xs[right]) {
            cand = right;
        }
        if (cand == root) {
            return;
        }
        int32_t tmp = xs[root];
        xs[root] = xs[cand];
        xs[cand] = tmp;
        root = cand;
    }
}

static void heap_sort(int32_t *xs, int32_t n) {
    for (int32_t start = n / 2 - 1; start >= 0; start -= 1) {
        sift_down(xs, start, n);
    }
    for (int32_t end = n - 1; end > 0; end -= 1) {
        int32_t tmp = xs[0];
        xs[0] = xs[end];
        xs[end] = tmp;
        sift_down(xs, 0, end);
    }
}

static int32_t binary_search(const int32_t *xs, int32_t n, int32_t key) {
    int32_t lo = 0;
    int32_t hi = n;
    while (lo < hi) {
        int32_t mid = lo + (hi - lo) / 2;
        int32_t v = xs[mid];
        if (v == key) {
            return mid;
        }
        if (v < key) {
            lo = mid + 1;
        } else {
            hi = mid;
        }
    }
    return -1;
}

int main(void) {
    const int32_t n = 4096;
    int32_t *xs = (int32_t *)malloc((size_t)n * sizeof(int32_t));
    if (xs == NULL) {
        return 1;
    }
    for (int32_t i = 0; i < n; i += 1) {
        xs[i] = (int32_t)(((int64_t)i * 1103515245 + 12345) % 100000);
    }
    int32_t k0 = xs[0];
    int32_t k1 = xs[n / 2];
    int32_t k2 = xs[n - 1];
    heap_sort(xs, n);
    int32_t checksum = 0;
    for (int32_t i = 0; i < n; i += 1) {
        checksum += xs[i];
    }
    if (binary_search(xs, n, k0) < 0) {
        free(xs);
        return 2;
    }
    if (binary_search(xs, n, k1) < 0) {
        free(xs);
        return 3;
    }
    if (binary_search(xs, n, k2) < 0) {
        free(xs);
        return 4;
    }
    for (int32_t i = 1; i < n; i += 1) {
        if (xs[i - 1] > xs[i]) {
            free(xs);
            return 5;
        }
    }
    free(xs);
    if (checksum != 204872320) {
        return 6;
    }
    return 0;
}
