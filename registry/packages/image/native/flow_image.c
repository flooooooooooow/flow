#include "flow_image.h"

#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"

#include <limits.h>
#include <string.h>

/* Tiny embedded 2x2 PPM P6 (no comments): R, G / B, W */
static const uint8_t FLOW_IMAGE_EMBEDDED_PPM[] = {
    'P', '6', '\n',
    '2', ' ', '2', '\n',
    '2', '5', '5', '\n',
    255, 0, 0,
    0, 255, 0,
    0, 0, 255,
    255, 255, 255
};

/* Tiny embedded 2x2 RGBA PNG: R, G / B, W */
static const uint8_t FLOW_IMAGE_EMBEDDED_PNG[] = {
    0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a, 0x00, 0x00, 0x00, 0x0d,
    0x49, 0x48, 0x44, 0x52, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x02,
    0x08, 0x06, 0x00, 0x00, 0x00, 0x72, 0xb6, 0x0d, 0x24, 0x00, 0x00, 0x00,
    0x12, 0x49, 0x44, 0x41, 0x54, 0x78, 0xda, 0x63, 0xf8, 0xcf, 0xc0, 0xf0,
    0x1f, 0x0c, 0x81, 0x34, 0x18, 0x00, 0x00, 0x49, 0xc8, 0x09, 0xf7, 0x03,
    0xd9, 0x64, 0xf1, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4e, 0x44, 0xae,
    0x42, 0x60, 0x82
};

static int flow_image_is_space(uint8_t c) {
    return c == ' ' || c == '\t' || c == '\n' || c == '\r' || c == '\v' || c == '\f';
}

/* Advance past whitespace and full-line `#` comments. Returns new offset or -1. */
static int64_t flow_image_skip_ws_comments(const uint8_t *bytes, int64_t len, int64_t i) {
    while (i < len) {
        if (bytes[i] == '#') {
            while (i < len && bytes[i] != '\n') {
                i++;
            }
            continue;
        }
        if (flow_image_is_space(bytes[i])) {
            i++;
            continue;
        }
        break;
    }
    return i;
}

static int64_t flow_image_parse_u32(const uint8_t *bytes, int64_t len, int64_t i,
                                   uint32_t *out) {
    i = flow_image_skip_ws_comments(bytes, len, i);
    if (i < 0 || i >= len || bytes[i] < '0' || bytes[i] > '9') {
        return -1;
    }
    uint32_t v = 0;
    while (i < len && bytes[i] >= '0' && bytes[i] <= '9') {
        v = v * 10u + (uint32_t)(bytes[i] - '0');
        i++;
    }
    *out = v;
    return i;
}

int32_t flow_image_decode_ppm(const uint8_t *bytes, int64_t len,
                              int32_t *w, int32_t *h,
                              uint8_t *out_rgba, int64_t out_cap) {
    if (!bytes || len < 8 || !w || !h || !out_rgba || out_cap <= 0) {
        return 1;
    }
    if (bytes[0] != 'P' || bytes[1] != '6') {
        return 2;
    }
    int64_t i = 2;
    /* After magic, need whitespace before dimensions */
    if (i >= len || !flow_image_is_space(bytes[i])) {
        /* allow comment immediately after magic on some writers */
        if (i >= len || bytes[i] != '#') {
            return 2;
        }
    }

    uint32_t width = 0;
    uint32_t height = 0;
    uint32_t maxval = 0;
    i = flow_image_parse_u32(bytes, len, i, &width);
    if (i < 0) {
        return 3;
    }
    i = flow_image_parse_u32(bytes, len, i, &height);
    if (i < 0) {
        return 3;
    }
    i = flow_image_parse_u32(bytes, len, i, &maxval);
    if (i < 0) {
        return 3;
    }
    if (width == 0 || height == 0 || width > 16384u || height > 16384u) {
        return 3;
    }
    if (maxval != 255u) {
        return 5;
    }
    /* Single whitespace byte separates header from raster */
    if (i >= len || !flow_image_is_space(bytes[i])) {
        return 1;
    }
    i++;

    int64_t need = (int64_t)width * (int64_t)height * 4;
    int64_t rgb_need = (int64_t)width * (int64_t)height * 3;
    if (need > out_cap) {
        return 4;
    }
    if (i + rgb_need > len) {
        return 1;
    }

    const uint8_t *rgb = bytes + i;
    for (uint32_t p = 0; p < width * height; p++) {
        out_rgba[p * 4 + 0] = rgb[p * 3 + 0];
        out_rgba[p * 4 + 1] = rgb[p * 3 + 1];
        out_rgba[p * 4 + 2] = rgb[p * 3 + 2];
        out_rgba[p * 4 + 3] = 255;
    }

    *w = (int32_t)width;
    *h = (int32_t)height;
    return 0;
}

int32_t flow_image_decode(const uint8_t *bytes, int64_t len,
                          int32_t *w, int32_t *h,
                          uint8_t *out_rgba, int64_t out_cap) {
    if (!bytes || len <= 0 || !w || !h || !out_rgba || out_cap <= 0) {
        return 1;
    }
    if (len > (int64_t)INT_MAX) {
        return 1;
    }

    int width = 0;
    int height = 0;
    int channels = 0;
    unsigned char *pixels = stbi_load_from_memory(
        bytes, (int)len, &width, &height, &channels, 4);
    if (!pixels || width <= 0 || height <= 0) {
        if (pixels) {
            stbi_image_free(pixels);
        }
        return 2;
    }

    int64_t need = (int64_t)width * (int64_t)height * 4;
    if (need > out_cap) {
        stbi_image_free(pixels);
        return 4;
    }

    memcpy(out_rgba, pixels, (size_t)need);
    stbi_image_free(pixels);
    *w = (int32_t)width;
    *h = (int32_t)height;
    return 0;
}

int32_t flow_image_load_test_pattern(int32_t *w, int32_t *h,
                                     uint8_t *out_rgba, int64_t out_cap) {
    if (!w || !h || !out_rgba || out_cap < 16) {
        return 1;
    }
    static const uint8_t pat[16] = {
        255, 0, 0, 255,
        0, 255, 0, 255,
        0, 0, 255, 255,
        255, 255, 255, 255
    };
    memcpy(out_rgba, pat, 16);
    *w = 2;
    *h = 2;
    return 0;
}

int32_t flow_image_decode_embedded_ppm(int32_t *w, int32_t *h,
                                       uint8_t *out_rgba, int64_t out_cap) {
    return flow_image_decode_ppm(
        FLOW_IMAGE_EMBEDDED_PPM,
        (int64_t)sizeof(FLOW_IMAGE_EMBEDDED_PPM),
        w, h, out_rgba, out_cap);
}

int32_t flow_image_decode_embedded_png(int32_t *w, int32_t *h,
                                       uint8_t *out_rgba, int64_t out_cap) {
    return flow_image_decode(
        FLOW_IMAGE_EMBEDDED_PNG,
        (int64_t)sizeof(FLOW_IMAGE_EMBEDDED_PNG),
        w, h, out_rgba, out_cap);
}
