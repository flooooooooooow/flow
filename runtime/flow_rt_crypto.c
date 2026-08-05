/* Crypto kernels for lib/runtime/crypto.flow — OS CSPRNG only.
 * SHA-256 lives in Flow (lib/runtime/crypto.flow). */
#include <stdint.h>
#include <stddef.h>

#if defined(__APPLE__) || defined(__FreeBSD__) || defined(__OpenBSD__)
#include <stdlib.h>
#elif defined(__linux__)
#include <sys/random.h>
#include <unistd.h>
#endif

int32_t flow_rt_random_bytes(void *buf, int64_t len) {
    if (!buf || len <= 0) return -1;
#if defined(__APPLE__) || defined(__FreeBSD__) || defined(__OpenBSD__)
    arc4random_buf(buf, (size_t)len);
    return 0;
#elif defined(__linux__)
    size_t got = 0;
    while (got < (size_t)len) {
        ssize_t n = getrandom((uint8_t *)buf + got, (size_t)len - got, 0);
        if (n < 0) return -1;
        got += (size_t)n;
    }
    return 0;
#else
    return -1;
#endif
}
