// Flow Audio SIMD Helpers (CPU)
// Simple loops intended for auto-vectorization.

#include <stdint.h>

void flow_audio_gain_interleaved_f32_fast(float* data, int frames, int channels, float gain) {
    if (!data || frames <= 0 || channels <= 0) {
        return;
    }
    int total = frames * channels;
    for (int i = 0; i < total; ++i) {
        data[i] *= gain;
    }
}

void flow_audio_mix_interleaved_f32_fast(float* dst, const float* src, int frames, int channels) {
    if (!dst || !src || frames <= 0 || channels <= 0) {
        return;
    }
    int total = frames * channels;
    for (int i = 0; i < total; ++i) {
        dst[i] += src[i];
    }
}

void flow_audio_copy_interleaved_f32_fast(float* dst, const float* src, int frames, int channels) {
    if (!dst || !src || frames <= 0 || channels <= 0) {
        return;
    }
    int total = frames * channels;
    for (int i = 0; i < total; ++i) {
        dst[i] = src[i];
    }
}
