#include "flow_compress.h"

#include <zlib.h>

int64_t flow_compress_deflate(const uint8_t *in, int64_t in_len,
                              uint8_t *out, int64_t out_cap) {
    if (!in || !out || in_len < 0 || out_cap <= 0) {
        return -1;
    }
    uLongf dest_len = (uLongf)out_cap;
    int rc = compress2(out, &dest_len, in, (uLong)in_len, Z_DEFAULT_COMPRESSION);
    if (rc != Z_OK) {
        return -1;
    }
    return (int64_t)dest_len;
}

int64_t flow_compress_inflate(const uint8_t *in, int64_t in_len,
                              uint8_t *out, int64_t out_cap) {
    if (!in || !out || in_len < 0 || out_cap <= 0) {
        return -1;
    }
    uLongf dest_len = (uLongf)out_cap;
    int rc = uncompress(out, &dest_len, in, (uLong)in_len);
    if (rc != Z_OK) {
        return -1;
    }
    return (int64_t)dest_len;
}
