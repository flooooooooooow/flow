// Flow Audio Runtime - Miniaudio backend
//
// Cross-platform real-time audio using miniaudio.
// Requires third_party/miniaudio.h and -DFLOW_AUDIO_BACKEND_MINIAUDIO.

#include "audio_common.h"

#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdio.h>
#include <stdatomic.h>

#ifdef FLOW_AUDIO_BACKEND_MINIAUDIO

#define MINIAUDIO_IMPLEMENTATION
#include "miniaudio.h"

typedef struct FlowSpscRingF32 {
    float* data;          // interleaved frames
    uint32_t capacity;    // frames, power of two
    uint32_t channels;
    atomic_uint read_idx; // in frames
    atomic_uint write_idx;
} FlowSpscRingF32;

typedef struct FlowAudioDevice {
    ma_device device;
    FlowSpscRingF32 in_rb;
    FlowSpscRingF32 out_rb;
    ma_bool32 has_input;
    ma_bool32 has_output;
    ma_uint32 channels;
    ma_uint32 sample_rate;
    ma_uint32 frames_per_buffer;
    char last_error[256];
} FlowAudioDevice;

static char flow_audio_last_error_global[256];

static void flow_audio_set_global_error(const char* msg) {
    if (!msg) {
        flow_audio_last_error_global[0] = '\0';
        return;
    }
    strncpy(flow_audio_last_error_global, msg, sizeof(flow_audio_last_error_global) - 1);
    flow_audio_last_error_global[sizeof(flow_audio_last_error_global) - 1] = '\0';
}

static void flow_audio_set_error(FlowAudioDevice* dev, const char* msg) {
    if (!dev) {
        flow_audio_set_global_error(msg);
        return;
    }
    if (!msg) {
        dev->last_error[0] = '\0';
        flow_audio_set_global_error("");
        return;
    }
    strncpy(dev->last_error, msg, sizeof(dev->last_error) - 1);
    dev->last_error[sizeof(dev->last_error) - 1] = '\0';
    flow_audio_set_global_error(msg);
}

const char* flow_audio_probe_devices(void) {
    static char buf[1024];
    buf[0] = '\0';
    ma_context ctx;
    ma_context_config ctx_config = ma_context_config_init();
    if (ma_context_init(NULL, 0, &ctx_config, &ctx) != MA_SUCCESS) {
        snprintf(buf, sizeof(buf), "audio: context init failed");
        flow_audio_set_global_error(buf);
        return buf;
    }

    ma_device_info* playback_infos = NULL;
    ma_uint32 playback_count = 0;
    ma_device_info* capture_infos = NULL;
    ma_uint32 capture_count = 0;
    ma_result res = ma_context_get_devices(&ctx, &playback_infos, &playback_count, &capture_infos, &capture_count);
    if (res != MA_SUCCESS) {
        snprintf(buf, sizeof(buf), "audio: device enumeration failed (%s)", ma_result_description(res));
        flow_audio_set_global_error(buf);
        ma_context_uninit(&ctx);
        return buf;
    }

    snprintf(buf, sizeof(buf), "playback=%u capture=%u", (unsigned)playback_count, (unsigned)capture_count);
    flow_audio_set_global_error(buf);
    ma_context_uninit(&ctx);
    return buf;
}

static uint32_t flow_next_pow2(uint32_t v) {
    if (v == 0) return 1;
    v--;
    v |= v >> 1;
    v |= v >> 2;
    v |= v >> 4;
    v |= v >> 8;
    v |= v >> 16;
    v++;
    return v;
}

static int flow_rb_init(FlowSpscRingF32* rb, uint32_t frames, uint32_t channels) {
    if (!rb || channels == 0) return -1;
    uint32_t cap = flow_next_pow2(frames);
    rb->data = (float*)calloc((size_t)cap * channels, sizeof(float));
    if (!rb->data) return -1;
    rb->capacity = cap;
    rb->channels = channels;
    atomic_store(&rb->read_idx, 0u);
    atomic_store(&rb->write_idx, 0u);
    return 0;
}

static void flow_rb_uninit(FlowSpscRingF32* rb) {
    if (!rb) return;
    free(rb->data);
    rb->data = NULL;
    rb->capacity = 0;
    rb->channels = 0;
    atomic_store(&rb->read_idx, 0u);
    atomic_store(&rb->write_idx, 0u);
}

static uint32_t flow_rb_available_read(const FlowSpscRingF32* rb) {
    uint32_t r = atomic_load(&rb->read_idx);
    uint32_t w = atomic_load(&rb->write_idx);
    return w - r;
}

static uint32_t flow_rb_available_write(const FlowSpscRingF32* rb) {
    return rb->capacity - flow_rb_available_read(rb);
}

static uint32_t flow_rb_write(FlowSpscRingF32* rb, const float* input, uint32_t frames) {
    uint32_t avail = flow_rb_available_write(rb);
    if (frames > avail) frames = avail;
    uint32_t r = atomic_load(&rb->read_idx);
    uint32_t w = atomic_load(&rb->write_idx);
    uint32_t mask = rb->capacity - 1;
    uint32_t first = rb->capacity - (w & mask);
    if (first > frames) first = frames;
    uint32_t second = frames - first;
    size_t ch = rb->channels;
    memcpy(rb->data + (size_t)(w & mask) * ch, input, (size_t)first * ch * sizeof(float));
    if (second > 0) {
        memcpy(rb->data, input + (size_t)first * ch, (size_t)second * ch * sizeof(float));
    }
    atomic_store(&rb->write_idx, w + frames);
    (void)r;
    return frames;
}

static uint32_t flow_rb_read(FlowSpscRingF32* rb, float* output, uint32_t frames) {
    uint32_t avail = flow_rb_available_read(rb);
    if (frames > avail) frames = avail;
    uint32_t r = atomic_load(&rb->read_idx);
    uint32_t mask = rb->capacity - 1;
    uint32_t first = rb->capacity - (r & mask);
    if (first > frames) first = frames;
    uint32_t second = frames - first;
    size_t ch = rb->channels;
    memcpy(output, rb->data + (size_t)(r & mask) * ch, (size_t)first * ch * sizeof(float));
    if (second > 0) {
        memcpy(output + (size_t)first * ch, rb->data, (size_t)second * ch * sizeof(float));
    }
    atomic_store(&rb->read_idx, r + frames);
    return frames;
}

static void flow_audio_data_callback(ma_device* device, void* output, const void* input, ma_uint32 frame_count) {
    FlowAudioDevice* dev = (FlowAudioDevice*)device->pUserData;
    if (!dev) {
        return;
    }

    if (dev->has_input && input != NULL) {
        flow_rb_write(&dev->in_rb, (const float*)input, frame_count);
    }

    if (dev->has_output && output != NULL) {
        ma_uint32 read_frames = flow_rb_read(&dev->out_rb, (float*)output, frame_count);
        if (read_frames < frame_count) {
            size_t offset = (size_t)read_frames * dev->channels;
            size_t remaining = (size_t)(frame_count - read_frames) * dev->channels;
            float* out = (float*)output;
            memset(out + offset, 0, remaining * sizeof(float));
        }
    }
}

int flow_audio_open(const FlowAudioConfig* config, FlowAudioDevice** out_dev) {
    if (!config || !out_dev) {
        return -1;
    }

    FlowAudioDevice* dev = (FlowAudioDevice*)calloc(1, sizeof(FlowAudioDevice));
    if (!dev) {
        return -1;
    }

    dev->channels = (ma_uint32)config->channels;
    dev->sample_rate = (ma_uint32)config->sample_rate;
    dev->frames_per_buffer = (ma_uint32)config->frames_per_buffer;
    dev->has_input = config->enable_input ? MA_TRUE : MA_FALSE;
    dev->has_output = config->enable_output ? MA_TRUE : MA_FALSE;

    ma_device_config device_config;
    if (dev->has_input && dev->has_output) {
        device_config = ma_device_config_init(ma_device_type_duplex);
        device_config.capture.format = ma_format_f32;
        device_config.capture.channels = dev->channels;
        device_config.playback.format = ma_format_f32;
        device_config.playback.channels = dev->channels;
    } else if (dev->has_input) {
        device_config = ma_device_config_init(ma_device_type_capture);
        device_config.capture.format = ma_format_f32;
        device_config.capture.channels = dev->channels;
    } else {
        device_config = ma_device_config_init(ma_device_type_playback);
        device_config.playback.format = ma_format_f32;
        device_config.playback.channels = dev->channels;
    }

    if (dev->frames_per_buffer == 0) {
        dev->frames_per_buffer = 256;
    }

    device_config.sampleRate = dev->sample_rate;
    device_config.periodSizeInFrames = dev->frames_per_buffer;
    device_config.periods = 2;
    device_config.performanceProfile = ma_performance_profile_low_latency;
    device_config.dataCallback = flow_audio_data_callback;
    device_config.pUserData = dev;

    ma_result result = ma_device_init(NULL, &device_config, &dev->device);
    if (result != MA_SUCCESS) {
        ma_result first = result;
        /* Fallback 1: if duplex and channels > 1, retry with mono capture. */
        if (dev->has_input && dev->has_output && dev->channels > 1) {
            device_config.capture.channels = 1;
            result = ma_device_init(NULL, &device_config, &dev->device);
        }
        /* Fallback 2: retry with backend defaults for sample rate and period size. */
        if (result != MA_SUCCESS) {
            device_config.sampleRate = 0;
            device_config.periodSizeInFrames = 0;
            device_config.periods = 0;
            result = ma_device_init(NULL, &device_config, &dev->device);
        }
        /* Fallback 3: if duplex failed, retry as playback-only. */
        if (result != MA_SUCCESS && dev->has_input && dev->has_output) {
            dev->has_input = MA_FALSE;
            device_config = ma_device_config_init(ma_device_type_playback);
            device_config.playback.format = ma_format_f32;
            device_config.playback.channels = dev->channels;
            device_config.sampleRate = dev->sample_rate;
            device_config.periodSizeInFrames = dev->frames_per_buffer;
            device_config.periods = 2;
            device_config.performanceProfile = ma_performance_profile_low_latency;
            device_config.dataCallback = flow_audio_data_callback;
            device_config.pUserData = dev;
            result = ma_device_init(NULL, &device_config, &dev->device);
        }
        if (result != MA_SUCCESS) {
            char msg[256];
            snprintf(msg, sizeof(msg),
                     "audio: device init failed (%s); fallback failed (%s)",
                     ma_result_description(first), ma_result_description(result));
            flow_audio_set_error(dev, msg);
            free(dev);
            return -1;
        }
    }

    ma_uint32 rb_frames = dev->frames_per_buffer * 8;
    if (rb_frames < 256) {
        rb_frames = 256;
    }

    if (dev->has_input) {
        if (flow_rb_init(&dev->in_rb, rb_frames, dev->channels) != 0) {
            flow_audio_set_error(dev, "audio: input ring buffer init failed");
            ma_device_uninit(&dev->device);
            free(dev);
            return -1;
        }
    }

    if (dev->has_output) {
        if (flow_rb_init(&dev->out_rb, rb_frames, dev->channels) != 0) {
            flow_audio_set_error(dev, "audio: output ring buffer init failed");
            if (dev->has_input) {
                flow_rb_uninit(&dev->in_rb);
            }
            ma_device_uninit(&dev->device);
            free(dev);
            return -1;
        }
    }

    flow_audio_set_error(dev, "");
    *out_dev = dev;
    return 0;
}

int flow_audio_start(FlowAudioDevice* dev) {
    if (!dev) {
        return -1;
    }
    ma_result result = ma_device_start(&dev->device);
    if (result != MA_SUCCESS) {
        char msg[256];
        snprintf(msg, sizeof(msg), "audio: device start failed (%s)", ma_result_description(result));
        flow_audio_set_error(dev, msg);
        return -1;
    }
    return 0;
}

int flow_audio_stop(FlowAudioDevice* dev) {
    if (!dev) {
        return -1;
    }
    ma_device_stop(&dev->device);
    return 0;
}

void flow_audio_close(FlowAudioDevice* dev) {
    if (!dev) {
        return;
    }
    ma_device_uninit(&dev->device);
    if (dev->has_input) {
        flow_rb_uninit(&dev->in_rb);
    }
    if (dev->has_output) {
        flow_rb_uninit(&dev->out_rb);
    }
    free(dev);
}

int flow_audio_read_f32(FlowAudioDevice* dev, float* out, int frames) {
    if (!dev || !out || frames <= 0 || !dev->has_input) {
        return 0;
    }
    return (int)flow_rb_read(&dev->in_rb, out, (ma_uint32)frames);
}

int flow_audio_write_f32(FlowAudioDevice* dev, const float* in, int frames) {
    if (!dev || !in || frames <= 0 || !dev->has_output) {
        return 0;
    }
    return (int)flow_rb_write(&dev->out_rb, in, (ma_uint32)frames);
}

int flow_audio_available_read(FlowAudioDevice* dev) {
    if (!dev || !dev->has_input) {
        return 0;
    }
    return (int)flow_rb_available_read(&dev->in_rb);
}

int flow_audio_available_write(FlowAudioDevice* dev) {
    if (!dev || !dev->has_output) {
        return 0;
    }
    return (int)flow_rb_available_write(&dev->out_rb);
}

const char* flow_audio_last_error(FlowAudioDevice* dev) {
    if (!dev) {
        if (flow_audio_last_error_global[0] != '\0') {
            return flow_audio_last_error_global;
        }
        return "audio: device not initialized";
    }
    return dev->last_error;
}

int flow_audio_has_input(FlowAudioDevice* dev) {
    if (!dev) return 0;
    return dev->has_input ? 1 : 0;
}

int flow_audio_has_output(FlowAudioDevice* dev) {
    if (!dev) return 0;
    return dev->has_output ? 1 : 0;
}

#else

struct FlowAudioDevice {
    FlowAudioConfig config;
    char last_error[256];
};

static char flow_audio_last_error_global[256];

static void flow_audio_set_global_error(const char* msg) {
    if (!msg) {
        flow_audio_last_error_global[0] = '\0';
        return;
    }
    strncpy(flow_audio_last_error_global, msg, sizeof(flow_audio_last_error_global) - 1);
    flow_audio_last_error_global[sizeof(flow_audio_last_error_global) - 1] = '\0';
}

static void flow_audio_set_error(FlowAudioDevice* dev, const char* msg) {
    if (!dev) {
        flow_audio_set_global_error(msg);
        return;
    }
    if (!msg) {
        dev->last_error[0] = '\0';
        flow_audio_set_global_error("");
        return;
    }
    strncpy(dev->last_error, msg, sizeof(dev->last_error) - 1);
    dev->last_error[sizeof(dev->last_error) - 1] = '\0';
    flow_audio_set_global_error(msg);
}

const char* flow_audio_probe_devices(void) {
    flow_audio_set_global_error("audio backend not built (enable FLOW_AUDIO_BACKEND_MINIAUDIO)");
    return flow_audio_last_error_global;
}

int flow_audio_open(const FlowAudioConfig* config, FlowAudioDevice** out_dev) {
    if (!config || !out_dev) {
        return -1;
    }
    FlowAudioDevice* dev = (FlowAudioDevice*)calloc(1, sizeof(FlowAudioDevice));
    if (!dev) {
        return -1;
    }
    dev->config = *config;
    flow_audio_set_error(dev, "audio backend not built (enable FLOW_AUDIO_BACKEND_MINIAUDIO)");
    *out_dev = dev;
    return -1;
}

int flow_audio_start(FlowAudioDevice* dev) {
    if (!dev) {
        return -1;
    }
    flow_audio_set_error(dev, "audio backend not built (enable FLOW_AUDIO_BACKEND_MINIAUDIO)");
    return -1;
}

int flow_audio_stop(FlowAudioDevice* dev) {
    if (!dev) {
        return -1;
    }
    return 0;
}

void flow_audio_close(FlowAudioDevice* dev) {
    if (!dev) {
        return;
    }
    free(dev);
}

int flow_audio_read_f32(FlowAudioDevice* dev, float* out, int frames) {
    (void)out;
    (void)frames;
    if (!dev) {
        return 0;
    }
    return 0;
}

int flow_audio_write_f32(FlowAudioDevice* dev, const float* in, int frames) {
    (void)in;
    if (!dev) {
        return 0;
    }
    return frames;
}

int flow_audio_available_read(FlowAudioDevice* dev) {
    if (!dev) {
        return 0;
    }
    return 0;
}

int flow_audio_available_write(FlowAudioDevice* dev) {
    if (!dev) {
        return 0;
    }
    return 0;
}

const char* flow_audio_last_error(FlowAudioDevice* dev) {
    if (!dev) {
        if (flow_audio_last_error_global[0] != '\0') {
            return flow_audio_last_error_global;
        }
        return "audio: device not initialized";
    }
    return dev->last_error;
}

int flow_audio_has_input(FlowAudioDevice* dev) {
    (void)dev;
    return 0;
}

int flow_audio_has_output(FlowAudioDevice* dev) {
    (void)dev;
    return 0;
}

#endif
