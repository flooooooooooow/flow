#ifndef FLOW_COMPRESS_H
#define FLOW_COMPRESS_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* zlib-format deflate into out. Returns compressed length, or -1 on error. */
int64_t flow_compress_deflate(const uint8_t *in, int64_t in_len,
                              uint8_t *out, int64_t out_cap);

/* zlib-format inflate into out. Returns decompressed length, or -1 on error. */
int64_t flow_compress_inflate(const uint8_t *in, int64_t in_len,
                              uint8_t *out, int64_t out_cap);

#ifdef __cplusplus
}
#endif

#endif /* FLOW_COMPRESS_H */
