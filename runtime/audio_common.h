// Flow Audio Runtime - Common API
// Cross-platform audio I/O (ring-buffer facade).

#pragma once

#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct FlowAudioDevice FlowAudioDevice;

typedef struct FlowAudioConfig {
    int sample_rate;
    int channels;
    int frames_per_buffer;
    bool enable_input;
    bool enable_output;
} FlowAudioConfig;

// Returns 0 on success, non-zero on failure.
int flow_audio_open(const FlowAudioConfig* config, FlowAudioDevice** out_dev);
int flow_audio_start(FlowAudioDevice* dev);
int flow_audio_stop(FlowAudioDevice* dev);
void flow_audio_close(FlowAudioDevice* dev);

// Interleaved f32 frames. Returns frames read/written.
int flow_audio_read_f32(FlowAudioDevice* dev, float* out, int frames);
int flow_audio_write_f32(FlowAudioDevice* dev, const float* in, int frames);

// Frames available in ring buffers.
int flow_audio_available_read(FlowAudioDevice* dev);
int flow_audio_available_write(FlowAudioDevice* dev);

const char* flow_audio_last_error(FlowAudioDevice* dev);
const char* flow_audio_probe_devices(void);
int flow_audio_has_input(FlowAudioDevice* dev);
int flow_audio_has_output(FlowAudioDevice* dev);

#ifdef __cplusplus
}
#endif
