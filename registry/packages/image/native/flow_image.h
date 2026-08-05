#ifndef FLOW_IMAGE_H
#define FLOW_IMAGE_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Decode a binary PPM P6 image from memory into caller-provided RGBA8 buffer.
 * Writes width/height on success. Returns 0 on success, nonzero on error:
 *   1 = bad args / truncated
 *   2 = not P6
 *   3 = bad header numbers
 *   4 = out_cap too small (need width*height*4)
 *   5 = unsupported maxval (only 255)
 */
int32_t flow_image_decode_ppm(const uint8_t *bytes, int64_t len,
                              int32_t *w, int32_t *h,
                              uint8_t *out_rgba, int64_t out_cap);

/* Decode an image (PNG/JPEG/etc via stb_image) from memory into RGBA8.
 * Requests 4 channels. Returns 0 on success, nonzero on error:
 *   1 = bad args
 *   2 = decode failed
 *   4 = out_cap too small (need width*height*4)
 */
int32_t flow_image_decode(const uint8_t *bytes, int64_t len,
                          int32_t *w, int32_t *h,
                          uint8_t *out_rgba, int64_t out_cap);

/* Fill a hardcoded 2x2 RGBA test pattern (R,G,B,W). Returns 0 on success. */
int32_t flow_image_load_test_pattern(int32_t *w, int32_t *h,
                                     uint8_t *out_rgba, int64_t out_cap);

/* Decode the package's embedded 2x2 PPM via flow_image_decode_ppm. */
int32_t flow_image_decode_embedded_ppm(int32_t *w, int32_t *h,
                                       uint8_t *out_rgba, int64_t out_cap);

/* Decode the package's embedded 2x2 PNG via flow_image_decode. */
int32_t flow_image_decode_embedded_png(int32_t *w, int32_t *h,
                                       uint8_t *out_rgba, int64_t out_cap);

#ifdef __cplusplus
}
#endif

#endif /* FLOW_IMAGE_H */
