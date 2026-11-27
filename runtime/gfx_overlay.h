#ifndef FLOW_GFX_OVERLAY_H
#define FLOW_GFX_OVERLAY_H

#include <stdint.h>
#include <string.h>

/* Update one persistent presentation overlay by clearing its previous dirty
 * bounds and copying the current dirty bounds from the software surface. */
static inline void flow_gfx_overlay_patch(uint8_t *dst, const uint8_t *src,
                                          int32_t width, int32_t height,
                                          const int32_t previous[4],
                                          const int32_t current[4]) {
    if (!dst || width <= 0 || height <= 0) return;
    int32_t x0 = previous[0], y0 = previous[1], x1 = previous[2], y1 = previous[3];
    if (x0 < 0) x0 = 0;
    if (y0 < 0) y0 = 0;
    if (x1 > width) x1 = width;
    if (y1 > height) y1 = height;
    if (x0 < x1 && y0 < y1) {
        size_t bytes = (size_t)(x1 - x0) * 4u;
        for (int32_t y = y0; y < y1; y++) {
            memset(dst + ((size_t)y * (size_t)width + (size_t)x0) * 4u, 0, bytes);
        }
    }
    if (!src || !current) return;
    x0 = current[0]; y0 = current[1]; x1 = current[2]; y1 = current[3];
    if (x0 < 0) x0 = 0;
    if (y0 < 0) y0 = 0;
    if (x1 > width) x1 = width;
    if (y1 > height) y1 = height;
    if (x0 >= x1 || y0 >= y1) return;
    size_t bytes = (size_t)(x1 - x0) * 4u;
    for (int32_t y = y0; y < y1; y++) {
        size_t offset = ((size_t)y * (size_t)width + (size_t)x0) * 4u;
        memcpy(dst + offset, src + offset, bytes);
    }
}

#endif
